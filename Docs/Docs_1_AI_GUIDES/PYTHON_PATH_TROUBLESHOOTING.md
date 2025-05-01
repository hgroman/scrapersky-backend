# Running the Server Locally: Python Path Troubleshooting

## Common Issue: "No module named 'src'"

When running the server locally (outside of Docker), you might encounter this error:

```
ModuleNotFoundError: No module named 'src'
```

This error occurs because Python can't find the 'src' module in its import path. This is a common issue when running applications that use relative imports.

### Specific Troubleshooting for Uvicorn

This error is especially common when using Uvicorn directly to run the server. You might see error logs like:

```
File ".../uvicorn/importer.py", line 19, in import_from_string
  module = importlib.import_module(module_str)
...
ModuleNotFoundError: No module named 'src'
```

When using Uvicorn's auto-reload feature, this error may appear repeatedly in the logs whenever a file changes.

## Solutions

### Solution 1: Run from Project Root (Recommended)

Always run the server from the project root directory:

```bash
# From the project root directory (where run_server.py is located)
python run_server.py
```

### Solution 2: Set PYTHONPATH Environment Variable

If you need to run the server from a different directory, set the PYTHONPATH environment variable:

```bash
# Linux/Mac
export PYTHONPATH=/path/to/scraper-sky-backend
python /path/to/scraper-sky-backend/run_server.py

# Windows
set PYTHONPATH=C:\path\to\scraper-sky-backend
python C:\path\to\scraper-sky-backend\run_server.py
```

### Solution 3: Install the Package in Development Mode

You can install the package in development mode, which adds it to your Python path:

```bash
# From the project root directory
pip install -e .
```

This requires a proper setup.py file in the project root.

## Uvicorn Command Line Usage

If you're using Uvicorn directly to run the server, make sure to set the PYTHONPATH and use the correct application path:

```bash
# Wrong (will cause ModuleNotFoundError)
uvicorn app:app --reload

# Correct (when running from project root)
PYTHONPATH=. uvicorn src.app:app --reload
```

You can also create an alias in your shell profile:

```bash
# Add to your .bashrc or .zshrc
alias run-scraper-sky="cd /path/to/scraper-sky-backend && PYTHONPATH=. python run_server.py"
```

## Docker vs. Local Development

- **Docker**: The Docker environment is already configured with the correct Python path
- **Local development**: Requires proper Python path configuration as described above

Always verify your working directory and Python path when running locally!

## Environment Variables

Local development may also require setting up environment variables that Docker automatically provides:

```bash
# Example environment variables needed for local development
export SUPABASE_POOLER_HOST=localhost
export SUPABASE_POOLER_PORT=5432
export SUPABASE_POOLER_USER=postgres
export SUPABASE_DB_PASSWORD=postgres
export SCRAPER_SKY_DEV_MODE=true
```

Consult the docker-compose.yml file for a complete list of environment variables used by the application.

## Quick Reference for Fixing "No module named 'src'" Error

1. **Check where you're running from**: Ensure you're in the project root directory
2. **Set PYTHONPATH**: `export PYTHONPATH=/path/to/scraper-sky-backend`
3. **Use the correct command**: `python run_server.py` (not `python src/app.py`)
4. **For Uvicorn**: Use `PYTHONPATH=. uvicorn src.app:app --reload`
5. **For test scripts**: Always run from project root or set PYTHONPATH
