Below is a **project-specific** Docker & Kubernetes Deployment Guide for your **ScraperSky** MVP. It references your actual filenames, environment variables, and run commands. You can store this as a markdown file (e.g., `DOCKER_K8S_GUIDE.md`) in your repo. The instructions are tailored to **your** folder structure, how you run your app (`run_server.py`), and your environment variable usage (`settings.py`). They also assume you want to deploy onto **Google Cloud Platform (GCP)** using Kubernetes.

---

# SCRAPERSKY DOCKER & KUBERNETES DEPLOYMENT GUIDE

This guide explains how to containerize **ScraperSky** for production and deploy it to GCP Kubernetes. Follow these steps in sequence, testing after each phase to ensure the AI agent (or any developer) retains context and validates success.

---

## 1. Create a `.dockerignore`

1. **What**  
   - Prevents unnecessary or sensitive files from ending up in the Docker image.

2. **Why**  
   - Smaller images, faster builds, better security.

3. **Steps**  
   1. In the root of your repo (same level as `Dockerfile`), create a file named **`.dockerignore`**.
   2. Add (at minimum) these lines:
      ```bash
      __pycache__/
      *.pyc
      *.pyo
      *.pyd
      .env
      .venv
      env/
      venv/
      .git/
      .github/
      .vscode/
      *.md
      *.log
      tests/
      pytest.ini
      ```
   3. **Verify** by running a Docker build (next steps) and ensuring the final image does not contain these folders/files.

---

## 2. Update `requirements.txt` (If Needed)

1. **Check** if any dev-only dependencies exist in your `requirements.txt`. If so, split them out into a separate `requirements-dev.txt`.  
2. **Keep** your production dependencies in `requirements.txt` for a leaner final image.

Example breakdown:

- `requirements.txt` (production):
  ```
  fastapi==0.115.8
  uvicorn==0.34.0
  psycopg2_binary==2.9.10
  pydantic==2.10.6
  pydantic_settings==2.7.1
  python-dotenv==1.0.1
  # ...
  ```

- `requirements-dev.txt` (development/test):
  ```
  pytest
  black
  flake8
  # ...
  ```

(*If you do not have dev-only dependencies, you can skip this.*)

---

## 3. Create or Optimize Your `Dockerfile`

### 3.1 Example Multi-Stage `Dockerfile`

> **Note**: This `Dockerfile` references your **`run_server.py`** script and expects environment variables loaded at runtime from a `.env` or from Kubernetes secrets. It also removes **`reload=True`** so we don’t use dev auto-reload in production.

Here’s a template you can adapt:

```dockerfile
# -----------------------------------------
# Stage 1: Builder - Install dependencies
# -----------------------------------------
FROM python:3.11-slim as builder

# System-level dependencies (e.g., for psycopg2 compile, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Create a non-root user (for security)
RUN adduser --disabled-password --gecos "" myuser
USER myuser

WORKDIR /app

# Copy only requirements to leverage Docker layer caching
COPY requirements.txt /app/
# If using a separate dev dependencies file:
# COPY requirements-dev.txt /app/

# Install dependencies into a local user path
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy entire project (excluding what’s in .dockerignore)
COPY . /app

# -----------------------------------------
# Stage 2: Final Image
# -----------------------------------------
FROM python:3.11-slim

# Copy the local user's installed packages from builder to final
COPY --from=builder /home/myuser/.local /home/myuser/.local

# Recreate the same user in final stage
RUN adduser --disabled-password --gecos "" myuser
USER myuser

ENV PATH=/home/myuser/.local/bin:$PATH
WORKDIR /app

# Copy project files
COPY --from=builder /app /app

# Expose port 8000 for FastAPI
EXPOSE 8000

# Using an environment variable to control reload for dev vs. prod
# (Below is just an example. In production, we typically do not use reload.)
ENV UVICORN_RELOAD false

# Final run command
CMD [ "python", "run_server.py" ]
```

#### 3.1.1 Why Multi-Stage?

- **Build stage** installs dependencies with `build-essential` (needed for `psycopg2_binary` or other compiled libs).  
- **Final stage** is slimmer, contains no dev toolchain, and uses `python:3.11-slim` for minimal overhead.

#### 3.1.2 Verify

1. **Build** the image:  
   ```bash
   docker build -t scraper-sky .
   ```
2. **List** images:  
   ```bash
   docker images
   ```
   - You should see `scraper-sky` with a size in the hundreds of MB (not >1GB).
3. **Run**:  
   ```bash
   docker run -d --name test-scraper -p 8000:8000 scraper-sky
   ```
4. **Test**:  
   - Open `http://localhost:8000/health` or `curl localhost:8000/health`.  
   - Expect `{"status":"operational"}` response.

---

## 4. Environment Variables & Secrets

### 4.1 Project’s `.env`

Your `src/config/settings.py` loads environment variables like `supabase_url`, `openai_api_key`, etc.

- **Important**: In production, you generally **do not** bake `.env` into the Docker image. Instead, you provide them at runtime (e.g., Docker Compose or Kubernetes Secrets).

### 4.2 Docker Compose Example

*(If you’re testing locally in production mode before deploying to K8s)*

```yaml
version: "3.9"

services:
  scraper:
    build:
      context: .
      dockerfile: Dockerfile
    image: scraper-sky
    container_name: scraper_container
    ports:
      - "8000:8000"
    env_file:
      - .env  # Only for local dev testing
    environment:
      UVICORN_RELOAD: "false"  # Ensures we run in production mode
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 5s
```

- **Verify** by running:  
  ```bash
  docker-compose -f docker-compose.yml up --build
  ```
  and then test the endpoint.

---

## 5. Kubernetes Deployment (GCP)

### 5.1 Push Image to GCP Container Registry (or Artifact Registry)

1. **Tag** your image for GCP:
   ```bash
   # Example for GCR (Container Registry)
   docker tag scraper-sky gcr.io/YOUR_PROJECT_ID/scraper-sky:latest
   ```
2. **Authenticate** to GCP:
   ```bash
   gcloud auth configure-docker
   ```
3. **Push** your image:
   ```bash
   docker push gcr.io/YOUR_PROJECT_ID/scraper-sky:latest
   ```

### 5.2 Create Kubernetes Deployment & Service

Your **`k8s/deployment.yaml`** might look like this:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scraper-deployment
  labels:
    app: scraper-sky
spec:
  replicas: 2
  selector:
    matchLabels:
      app: scraper-sky
  template:
    metadata:
      labels:
        app: scraper-sky
    spec:
      containers:
        - name: scraper-container
          image: gcr.io/YOUR_PROJECT_ID/scraper-sky:latest
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
          env:
            - name: UVICORN_RELOAD
              value: "false"
            # EXAMPLE: pass secrets or config from K8S secrets
            # - name: SUPABASE_URL
            #   valueFrom:
            #     secretKeyRef:
            #       name: supabase-secret
            #       key: SUPABASE_URL
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 15
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: scraper-service
spec:
  selector:
    app: scraper-sky
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer  # GCP will provision an external LB
```

**Explanation**:

- **replicas**: 2 for basic high availability.  
- **port**: 8000 is where our FastAPI listens.  
- **LoadBalancer** on GCP automatically creates an external IP.

### 5.3 Apply Deployment

1. **Set** your GCP project and cluster context:
   ```bash
   gcloud container clusters get-credentials YOUR_CLUSTER --zone=YOUR_ZONE --project=YOUR_PROJECT_ID
   ```
2. **Apply**:
   ```bash
   kubectl apply -f k8s/deployment.yaml
   ```
3. **Check**:
   ```bash
   kubectl get pods
   kubectl get svc
   ```
4. Once the **LoadBalancer** is provisioned, you’ll see an external IP. Hit `EXTERNAL_IP/health` and confirm a `{"status":"operational"}` response.

---

## 6. Security Reminders

1. **Secrets**:  
   - Don’t store real secrets in `.env` inside your repo. Use Kubernetes Secrets or GCP Secret Manager.  
   - Example:  
     ```yaml
     kind: Secret
     apiVersion: v1
     metadata:
       name: supabase-secret
     type: Opaque
     data:
       SUPABASE_URL: <base64-encoded>
       SUPABASE_SERVICE_ROLE_KEY: <base64-encoded>
       # ...
     ```
   - Then reference in your deployment’s `env` section.

2. **Non-Root User**:  
   - Already done in the multi-stage `Dockerfile`: `adduser --disabled-password --gecos "" myuser` + `USER myuser`.

3. **SSL**:  
   - If you’re hooking up domain traffic, consider Ingress + Let’s Encrypt or GCP HTTPS LB.

4. **Resource Limits**:  
   - Already in `k8s/deployment.yaml`. Tweak to your usage.

---

## 7. Testing & Ongoing Validation

1. **Local Docker test**:  
   - `docker build -t scraper-sky . && docker run -p 8000:8000 scraper-sky`
   - Visit `localhost:8000/health`.
2. **Local Docker Compose**:  
   - `docker-compose -f docker-compose.yml up --build`
   - Confirm environment variable usage, logging, etc.
3. **Kubernetes**:  
   - `kubectl logs <pod-name>` to see your container logs.
   - `kubectl describe pod <pod-name>` for debugging.

---

## 8. Next Steps (Specific to ScraperSky)

1. **Sitemap and Email Scrapers**  
   - Finalize the logic in `src/routers/email_scanner.py` and `src/routers/sitemap_scraper.py`.
   - Validate concurrency, error handling, and data insertion into your DB (Supabase).
2. **BigQuery**  
   - If you plan to integrate BigQuery (from the README), ensure your GCP service account JSON is not baked into the image. Mount it or use Workload Identity in GKE.
3. **Monitoring & Logging**  
   - Setup Cloud Logging / Cloud Monitoring in GCP.  
   - Potentially use a dedicated logging library that outputs JSON (for better search in GCP logs).
4. **Continuous Integration (CI/CD)**  
   - Use GitHub Actions or Cloud Build to automate Docker builds and deployments.

---

## Summary

This guide is tailored to **your** ScraperSky project with **FastAPI** entry points (`run_server.py`, `src/main.py`), environment-managed secrets (`src/config/settings.py`), and a GCP-based K8s workflow. By following these steps:

1. You **ignore** sensitive/unnecessary files with `.dockerignore`.  
2. You create a **multi-stage** `Dockerfile` that references **your** run commands and environment variables.  
3. You test locally, then **push** to GCP Container Registry, and **deploy** to your GKE cluster via the provided `k8s/deployment.yaml`.  
4. You ensure security best practices (non-root user, no secrets in images) and readiness/liveness probes for better reliability.  
5. You maintain and scale via GCP’s auto-scaling and monitoring.

---

**End of Guide**  

This should equip you (and any AI agent working on your code) with a precise, **ScraperSky-specific** roadmap to containerizing and deploying your FastAPI application to Google Cloud Kubernetes. Happy deploying!