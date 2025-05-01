#!/bin/bash
set -e

echo "===== RUNTIME CODE USAGE ANALYSIS ====="

# Ensure the Docker container is running
docker-compose up -d --build scrapersky

# Run the exerciser from the host machine
python tools/exercise_endpoints.py --base-url http://localhost:8000

# Stop the container to trigger the FastAPI lifespan shutdown and log the collected modules
docker-compose stop scrapersky

# Fetch logs and pipe them into the analysis script running in a temporary container
docker-compose logs scrapersky | docker-compose run --rm scrapersky python tools/analyze_runtime_results.py

echo "===== ANALYSIS SCRIPT FINISHED (Manual Steps Required) ====="
# echo "Check reports/unused_files.json for the list of unused files"
