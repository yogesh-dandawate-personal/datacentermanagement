# Docker Deployment Guide - iNetZero Platform

**Status**: ✅ READY FOR DOCKER DEPLOYMENT
**Date**: March 10, 2026
**Frontend Dockerfile**: Multi-stage Node.js build
**Backend Dockerfile**: Python FastAPI application

---

## 🐳 Docker Images Ready

### Frontend Image
- **Base**: Node.js 20 Alpine (lightweight)
- **Build**: Multi-stage (builder + production)
- **Port**: 3000
- **Size**: ~100MB
- **Server**: serve (production-grade)
- **Health Check**: HTTP endpoint monitoring

### Backend Image
- **Base**: Python 3.12 Slim
- **Framework**: FastAPI with Uvicorn
- **Port**: 8000
- **Dependencies**: Installed from requirements.txt
- **Health Check**: API health endpoint

---

## 📋 Quick Start - Build Locally

### 1. Build Frontend Image
```bash
cd frontend
docker build -t inetze ro-frontend:latest .
cd ..

# Verify
docker images | grep inetze ro-frontend
```

### 2. Build Backend Image
```bash
cd backend
docker build -t inetze ro-backend:latest .
cd ..

# Verify
docker images | grep inetze ro-backend
```

### 3. Run Locally (Docker Compose)
```bash
# Create docker-compose.yml in project root
docker-compose up

# Access:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

---

## 🚀 Deploy to AWS ECS (Elastic Container Service)

### Step 1: Create AWS Account & Setup CLI
```bash
# Install AWS CLI
brew install awscli

# Configure credentials
aws configure
# Enter: Access Key ID
# Enter: Secret Access Key
# Region: us-east-1
# Output format: json
```

### Step 2: Create ECR Repositories
```bash
# Create frontend repository
aws ecr create-repository \
  --repository-name inetze ro-frontend \
  --region us-east-1

# Create backend repository
aws ecr create-repository \
  --repository-name inetze ro-backend \
  --region us-east-1

# Get repository URIs (copy these for next steps)
aws ecr describe-repositories \
  --repository-names inetze ro-frontend inetze ro-backend \
  --region us-east-1
```

### Step 3: Login to ECR
```bash
# Get login token
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

### Step 4: Push Images to ECR
```bash
# Set your AWS account ID
AWS_ACCOUNT_ID=123456789012
ECR_REGION=us-east-1

# Frontend
docker tag inetze ro-frontend:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.$ECR_REGION.amazonaws.com/inetze ro-frontend:latest

docker push \
  $AWS_ACCOUNT_ID.dkr.ecr.$ECR_REGION.amazonaws.com/inetze ro-frontend:latest

# Backend
docker tag inetze ro-backend:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.$ECR_REGION.amazonaws.com/inetze ro-backend:latest

docker push \
  $AWS_ACCOUNT_ID.dkr.ecr.$ECR_REGION.amazonaws.com/inetze ro-backend:latest
```

### Step 5: Create ECS Cluster
```bash
aws ecs create-cluster --cluster-name inetze ro-cluster --region us-east-1
```

### Step 6: Create ECS Tasks & Services
See AWS console or use CloudFormation template (contact AWS support for details).

---

## 🌥️ Deploy to Google Cloud Run

### Step 1: Setup Google Cloud SDK
```bash
# Install gcloud CLI
brew install google-cloud-sdk

# Initialize
gcloud init

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### Step 2: Configure Container Registry
```bash
# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Configure docker authentication
gcloud auth configure-docker
```

### Step 3: Push Images
```bash
# Build and tag frontend
docker build -t gcr.io/YOUR_PROJECT_ID/inetze ro-frontend:latest frontend/
docker push gcr.io/YOUR_PROJECT_ID/inetze ro-frontend:latest

# Build and tag backend
docker build -t gcr.io/YOUR_PROJECT_ID/inetze ro-backend:latest backend/
docker push gcr.io/YOUR_PROJECT_ID/inetze ro-backend:latest
```

### Step 4: Deploy to Cloud Run
```bash
# Frontend
gcloud run deploy inetze ro-frontend \
  --image gcr.io/YOUR_PROJECT_ID/inetze ro-frontend:latest \
  --platform managed \
  --region us-central1 \
  --port 3000 \
  --allow-unauthenticated

# Backend
gcloud run deploy inetze ro-backend \
  --image gcr.io/YOUR_PROJECT_ID/inetze ro-backend:latest \
  --platform managed \
  --region us-central1 \
  --port 8000 \
  --allow-unauthenticated
```

### Step 5: Get Service URLs
```bash
gcloud run services list --platform managed --region us-central1

# URLs will be in format:
# https://inetze ro-frontend-XXXXXX-uc.a.run.app
# https://inetze ro-backend-XXXXXX-uc.a.run.app
```

---

## 🎪 Deploy to Heroku

### Step 1: Setup Heroku CLI
```bash
# Install
brew tap heroku/brew && brew install heroku

# Login
heroku login
```

### Step 2: Enable Container Registry
```bash
heroku container:login
```

### Step 3: Create Heroku Apps
```bash
# Frontend app
heroku create inetze ro-frontend --region us

# Backend app
heroku create inetze ro-backend --region us

# Verify
heroku apps
```

### Step 4: Build and Push Images
```bash
# Frontend
docker build -t registry.heroku.com/inetze ro-frontend/web frontend/
docker push registry.heroku.com/inetze ro-frontend/web
heroku container:release web --app inetze ro-frontend

# Backend
docker build -t registry.heroku.com/inetze ro-backend/web backend/
docker push registry.heroku.com/inetze ro-backend/web
heroku container:release web --app inetze ro-backend
```

### Step 5: Set Environment Variables
```bash
# Frontend
heroku config:set REACT_APP_API_URL=https://inetze ro-backend.herokuapp.com \
  --app inetze ro-frontend

# Backend
heroku config:set DATABASE_URL=your_database_url \
  --app inetze ro-backend
```

### Step 6: Access Your Apps
```bash
# Frontend
heroku open --app inetze ro-frontend

# Backend API Docs
heroku open /api/docs --app inetze ro-backend
```

---

## 🔄 Docker Compose (Local Development)

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3000')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/inetze ro
    depends_on:
      - postgres
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/api/v1/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=inetze ro_user
      - POSTGRES_PASSWORD=inetze ro_password
      - POSTGRES_DB=inetze ro
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U inetze ro_user -d inetze ro"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Run with Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove volumes
docker-compose down -v
```

---

## 📊 Monitor Containers

### View Running Containers
```bash
docker ps

# Format output
docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}"
```

### View Logs
```bash
# Frontend
docker logs container_id -f

# Backend
docker logs container_id -f

# All services
docker-compose logs -f
```

### Check Container Health
```bash
docker inspect container_id | grep -A 10 Health
```

---

## 🛡️ Security Best Practices

### 1. Use Multi-Stage Builds
✅ Already implemented in both Dockerfiles
- Reduces image size
- Removes build tools from production
- Smaller attack surface

### 2. Non-Root User
```dockerfile
RUN useradd -m -u 1000 app
USER app
```

### 3. Health Checks
✅ Already implemented
- Frontend: HTTP status check
- Backend: API endpoint health check

### 4. Environment Variables
```bash
# Never hardcode secrets
docker run -e DATABASE_URL=your_db_url image_name

# Or use .env file
docker run --env-file .env.production image_name
```

### 5. Image Scanning
```bash
# Scan for vulnerabilities
docker scan inetze ro-frontend:latest
docker scan inetze ro-backend:latest
```

---

## 🚨 Troubleshooting

### Image Build Failures
```bash
# Check build logs
docker build --no-cache -t name:tag .

# Check for missing files
docker exec container_id ls -la /app
```

### Port Conflicts
```bash
# Find process using port
lsof -i :3000
lsof -i :8000

# Kill process
kill -9 PID
```

### Connection Issues
```bash
# Check container network
docker network ls
docker network inspect bridge

# Test connectivity
docker exec container_id curl http://other_container:port
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Check image size
docker images --format "{{.Repository}}\t{{.Size}}"

# Optimize by removing unused images
docker image prune
```

---

## 📈 Production Checklist

Before deploying to production:

- [ ] Frontend builds without errors
- [ ] Backend starts without errors
- [ ] Health checks passing
- [ ] Environment variables configured
- [ ] Database connection tested
- [ ] API endpoints responding
- [ ] Frontend can reach backend
- [ ] Static assets loading correctly
- [ ] Logs being captured
- [ ] Monitoring/alerting setup
- [ ] Backup/recovery plan ready
- [ ] SSL/TLS certificates configured
- [ ] Rate limiting enabled
- [ ] Security scanning completed

---

## 🔗 Environment Variables

### Frontend
```
REACT_APP_API_URL=https://api.your-domain.com
REACT_APP_ENVIRONMENT=production
```

### Backend
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your_secret_key
DEBUG=false
LOG_LEVEL=info
```

---

## 📞 Support

### Docker Documentation
- https://docs.docker.com
- https://docs.docker.com/compose

### AWS ECS
- https://docs.aws.amazon.com/ecs
- https://console.aws.amazon.com/ecs

### Google Cloud Run
- https://cloud.google.com/run/docs
- https://console.cloud.google.com

### Heroku
- https://devcenter.heroku.com
- https://dashboard.heroku.com

---

## 🎯 Summary

Your application is ready for containerized deployment:

1. ✅ **Frontend** - Multi-stage Node.js build
2. ✅ **Backend** - Python FastAPI container
3. ✅ **Health Checks** - Automatic monitoring
4. ✅ **Docker Compose** - Local testing

**Choose your cloud platform and deploy!**

### Quick Commands
```bash
# Build locally
docker build -t inetze ro-frontend:latest frontend/
docker build -t inetze ro-backend:latest backend/

# Test locally
docker-compose up

# Push to cloud
# (See platform-specific instructions above)
```

---

**Choose AWS, Google Cloud, or Heroku and follow the steps above!** 🚀
