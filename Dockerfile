# -----------------------------------------
# Stage 1: Builder - Install dependencies
# -----------------------------------------
FROM python:3.11-slim as builder

# System-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN adduser --disabled-password --gecos "" myuser
USER myuser

WORKDIR /app

# Copy only requirements to leverage Docker layer caching
COPY requirements.txt /app/

# Install dependencies into a local user path
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy entire project (excluding what's in .dockerignore)
COPY --chown=myuser:myuser . /app

# -----------------------------------------
# Stage 2: Final Image
# -----------------------------------------
FROM python:3.11-slim

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the local user's installed packages from builder
COPY --from=builder /home/myuser/.local /home/myuser/.local

# Recreate the same user in final stage
RUN adduser --disabled-password --gecos "" myuser
USER myuser

ENV PATH=/home/myuser/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV UVICORN_RELOAD=false

WORKDIR /app

# Copy project files
COPY --from=builder --chown=myuser:myuser /app /app

# Create crawl4ai directory with proper permissions
USER root
RUN mkdir -p /home/myuser/.crawl4ai && chown myuser:myuser /home/myuser/.crawl4ai
USER myuser

# Expose port 8000 for FastAPI
EXPOSE 8000

# Health check - using environment variable values or defaults
# Note: Docker Compose healthcheck will take precedence when defined there
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
