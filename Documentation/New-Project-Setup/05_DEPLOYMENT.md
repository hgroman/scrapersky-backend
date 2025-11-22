# Deployment Guide (Render + Vercel)

**Document:** 05_DEPLOYMENT.md  
**Phase:** Production Deployment  
**Time Required:** 45-60 minutes  
**Prerequisites:** Working application from documents 01-04

---

## Overview

Deploy your FastAPI backend to Render and React frontend to Vercel.

---

## Render Backend Deployment

### Step 1: Prepare for Deployment

Create `render.yaml` in project root:

```yaml
services:
  - type: web
    name: your-app-api
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: ENVIRONMENT
        value: production
```

### Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your repository
5. Configure:
   - **Name:** your-app-api
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variables

In Render dashboard, add all variables from your `.env`:

```
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_DB_PASSWORD=...
SUPABASE_POOLER_HOST=...
SUPABASE_POOLER_PORT=6543
SUPABASE_POOLER_USER=...
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Step 4: Deploy

Click "Create Web Service" - Render will:
1. Clone your repository
2. Install dependencies
3. Start your application
4. Provide a URL: `https://your-app-api.onrender.com`

### Step 5: Verify Deployment

```bash
curl https://your-app-api.onrender.com/health
curl https://your-app-api.onrender.com/docs
```

---

## Docker Deployment (Alternative)

If using Docker on Render:

**Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**render.yaml:**
```yaml
services:
  - type: web
    name: your-app-api
    env: docker
    dockerfilePath: ./Dockerfile
```

---

## Vercel Frontend Deployment

### Step 1: Create React App

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

### Step 2: Configure API URL

Create `frontend/.env.production`:

```
VITE_API_URL=https://your-app-api.onrender.com
```

### Step 3: Deploy to Vercel

```bash
npm install -g vercel
vercel login
vercel --prod
```

Or connect via Vercel dashboard:
1. Go to https://vercel.com
2. Import your repository
3. Configure:
   - **Framework:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Add environment variable: `VITE_API_URL`

---

## Health Checks & Monitoring

### Health Check Endpoint

Ensure your API has:

```python
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow()}
```

### Render Health Check

Configure in Render dashboard:
- **Health Check Path:** `/health`
- **Expected Status:** 200

---

## CORS Configuration

Update `src/config/settings.py` for production:

```python
# In production .env
CORS_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com
```

---

## Verification Checklist

- [ ] Backend deployed to Render
- [ ] Environment variables configured
- [ ] Health check endpoint working
- [ ] API docs accessible at /docs
- [ ] Frontend deployed to Vercel
- [ ] Frontend can call backend API
- [ ] CORS configured correctly
- [ ] SSL/HTTPS working

---

## Next Steps

✅ **Completed:** Deployment

**Next:** [06_FRONTEND_INTEGRATION.md](./06_FRONTEND_INTEGRATION.md) - Frontend API integration

---

**Status:** ✅ Deployment complete
