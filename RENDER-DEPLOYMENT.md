# Deploying ScraperSky to Render

This guide explains how to deploy ScraperSky to Render using Docker.

## Prerequisites

1. A Render account (https://render.com)
2. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Steps

1. **Connect Your Repository**
   - Log in to your Render dashboard
   - Click "New +" and select "Web Service"
   - Connect your Git repository

2. **Configure Your Service**
   - Choose the repository and branch to deploy
   - Select "Docker" as the environment
   - The service will automatically detect the `render.yaml` configuration

3. **Set Environment Variables**
   In your Render dashboard, set the following environment variables:
   - `OPENAI_API_KEY`
   - `SCRAPER_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_DB_PASSWORD`

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically:
     - Build your Docker image
     - Deploy your service
     - Set up HTTPS
     - Configure health checks
     - Enable auto-deploy for future commits

## Monitoring and Maintenance

1. **Health Checks**
   - Render automatically monitors the `/health` endpoint
   - View health status in your Render dashboard

2. **Logs**
   - Access logs from your service's dashboard
   - View build logs, deployment logs, and runtime logs

3. **Scaling**
   - Adjust `numInstances` in `render.yaml` for horizontal scaling
   - Upgrade your service plan for more resources

## Local Testing

Before deploying, test your Docker build locally:
```bash
docker build -t scrapersky .
docker run -p 8000:8000 --env-file .env scrapersky
```

Visit `http://localhost:8000/health` to verify the service is running.
