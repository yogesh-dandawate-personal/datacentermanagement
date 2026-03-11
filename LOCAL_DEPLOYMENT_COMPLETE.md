# iNetZero Platform - Local Deployment Guide

**Status**: ✅ **Ready for Local Deployment**
**Date**: 2026-03-11

---

## 🚀 Quick Start (5 Minutes)

### Terminal 1: Start Backend

```bash
cd /Users/yogesh/00_MyCode/01_PersonalProjects/datacentermanagement

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Start backend server (runs on http://localhost:8000)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Start Frontend

```bash
cd /Users/yogesh/00_MyCode/01_PersonalProjects/datacentermanagement/frontend

# Install frontend dependencies
npm install

# Start frontend dev server (runs on http://localhost:3000)
npm run dev
```

---

## 📋 Complete Setup Instructions

### **Step 1: Check Prerequisites**

```bash
# Check Node.js version (need >=18.0.0)
node --version

# Check Python version (need >=3.9)
python --version

# Check npm version (need >=9.0.0)
npm --version
```

If any are missing, install them first.

---

### **Step 2: Backend Setup**

```bash
cd /Users/yogesh/00_MyCode/01_PersonalProjects/datacentermanagement/backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file for local development
cat > .env << 'EOF'
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key-here-change-in-production
API_KEY=test-api-key-change-in-production
DEBUG=True
LOG_LEVEL=INFO
EOF

# Initialize database (if needed)
python -c "from app.main import app; print('Backend ready')"
```

**Start Backend**:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Backend runs at**: http://localhost:8000
✅ **API Docs**: http://localhost:8000/docs
✅ **ReDoc**: http://localhost:8000/redoc

---

### **Step 3: Frontend Setup**

```bash
cd /Users/yogesh/00_MyCode/01_PersonalProjects/datacentermanagement/frontend

# Install dependencies
npm install --legacy-peer-deps

# Create .env file
cat > .env.local << 'EOF'
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=iNetZero
VITE_LOG_LEVEL=info
EOF

# Verify build
npm run build
```

**Start Frontend (Development)**:
```bash
npm run dev
```

✅ **Frontend runs at**: http://localhost:3000

---

### **Step 4: Verify Deployment**

#### Backend Health Check
```bash
# Test backend is running
curl http://localhost:8000/api/v1/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}
```

#### Frontend Access
```bash
# Open in browser
open http://localhost:3000

# Or access directly via browser
# http://localhost:3000
```

#### API Documentation
```
# Interactive API docs
http://localhost:8000/docs

# Alternative API docs
http://localhost:8000/redoc
```

---

## 🗄️ Database Setup (Optional)

### Using SQLite (Default - No Setup Required)
```bash
# SQLite is used by default - no setup needed!
# Database file: backend/test.db (auto-created)
```

### Using PostgreSQL (Recommended for Production)

```bash
# 1. Install PostgreSQL
brew install postgresql  # macOS
# or download from https://www.postgresql.org/download/

# 2. Start PostgreSQL service
brew services start postgresql

# 3. Create database
psql postgres -c "CREATE DATABASE inetzero;"

# 4. Update .env file
cat > backend/.env << 'EOF'
DATABASE_URL=postgresql://postgres:password@localhost/inetzero
SECRET_KEY=your-secret-key-here
API_KEY=test-api-key
DEBUG=True
EOF

# 5. Run migrations (if applicable)
cd backend
python -m alembic upgrade head

# 6. Start backend with PostgreSQL
python -m uvicorn app.main:app --reload
```

---

## 📱 Access the Application

### **Frontend Application**
```
URL: http://localhost:3000
Features:
  • Dashboard with real-time metrics
  • Energy monitoring
  • Carbon accounting
  • Analytics and reporting
  • Trading marketplace
  • Settings and preferences
```

### **Backend API**
```
Base URL: http://localhost:8000/api/v1
Documentation: http://localhost:8000/docs
Test Endpoint: http://localhost:8000/api/v1/health
```

### **Default Credentials** (if available)
```
Username: admin@example.com
Password: password123
(Check backend documentation for actual credentials)
```

---

## 🔧 Development Workflow

### **Make Changes**
```bash
# Frontend changes are hot-reloaded
# - Edit files in frontend/src/
# - Changes appear instantly in browser

# Backend changes require restart
# - Edit files in backend/app/
# - Restart uvicorn to see changes
```

### **Run Tests**

**Backend Tests**:
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app  # With coverage
```

**Frontend Tests**:
```bash
cd frontend
npm test
npm run test:coverage
```

### **Build for Production**

**Frontend**:
```bash
cd frontend
npm run build
# Output: frontend/dist/
```

**Backend**:
```bash
cd backend
# No build needed - runs from source
# For deployment, use gunicorn or similar:
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

---

## 🐛 Troubleshooting

### Frontend Won't Start

**Error**: `npm: command not found`
```bash
# Install Node.js from https://nodejs.org/
node --version  # Verify installation
```

**Error**: `Port 3000 already in use`
```bash
# Kill process on port 3000
lsof -i :3000
kill -9 <PID>

# Or use different port
npm run dev -- --port 3001
```

**Error**: `Cannot find module`
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### Backend Won't Start

**Error**: `pip: command not found`
```bash
# Install Python from https://www.python.org/
python --version  # Verify installation
```

**Error**: `ModuleNotFoundError`
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Error**: `Port 8000 already in use`
```bash
# Kill process on port 8000
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### API Connection Issues

**Error**: `VITE_API_URL: Cannot connect`
```bash
# Check backend is running
curl http://localhost:8000/api/v1/health

# Update .env if using different port
# frontend/.env.local
VITE_API_URL=http://localhost:8001/api/v1
```

---

## 📊 System Architecture (Local)

```
┌─────────────────────────────────────┐
│     iNetZero Local Environment      │
├─────────────────────────────────────┤
│                                     │
│  Frontend (Vite)                    │
│  http://localhost:3000              │
│  ├─ React 18                        │
│  ├─ Real-time dashboards           │
│  └─ Dark mode support              │
│         ↓                           │
│     API Calls (http)                │
│         ↓                           │
│  Backend (FastAPI)                  │
│  http://localhost:8000              │
│  ├─ REST API endpoints             │
│  ├─ WebSocket support              │
│  └─ API Documentation              │
│         ↓                           │
│  Database (SQLite/PostgreSQL)       │
│  ├─ Users & authentication         │
│  ├─ Energy metrics                 │
│  ├─ Carbon calculations            │
│  └─ Analytics data                 │
│                                     │
└─────────────────────────────────────┘
```

---

## 🎯 Verification Checklist

- [ ] Node.js installed (>=18.0.0)
- [ ] Python installed (>=3.9)
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] `.env` files created
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can access http://localhost:3000
- [ ] API docs available at http://localhost:8000/docs
- [ ] API responds to http://localhost:8000/api/v1/health

---

## 📝 Environment Variables

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=iNetZero
VITE_LOG_LEVEL=info
VITE_SESSION_TIMEOUT=3600
```

### Backend (.env)
```
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=dev-secret-key-change-in-production
API_KEY=dev-api-key-change-in-production
DEBUG=True
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
```

---

## 🚀 Next Steps

### Local Development
1. ✅ Start backend and frontend
2. Make changes to code
3. Test features locally
4. Run tests
5. Commit changes to git

### Deploy to Production
1. Build frontend: `npm run build`
2. Deploy backend (Railway, Heroku, AWS)
3. Configure database (Cloud SQL, AWS RDS)
4. Deploy frontend to Vercel
5. Set up monitoring and alerts

---

## 💡 Tips & Tricks

### Hot Reload
```bash
# Frontend changes auto-reload (Vite)
npm run dev

# Backend requires manual restart
# Use Ctrl+C and re-run uvicorn
```

### Debug Mode
```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG

# Frontend with verbose output
npm run dev -- --debug

# Backend with logging
python -m uvicorn app.main:app --reload --log-level debug
```

### Test Data
```bash
# Seed database with test data
cd backend
python scripts/seed_db.py
```

### Performance Testing
```bash
# Load testing (requires locust)
pip install locust
locust -f tests/locustfile.py --host=http://localhost:8000
```

---

## 📞 Support

### Logs
```bash
# Backend logs (in uvicorn output)
# Frontend logs (in browser console)
# Check browser DevTools: F12 → Console

# Full logs with timestamps
# Backend: Add --log-level debug
# Frontend: Check browser console
```

### Common Issues
- **Ports in use**: Kill processes or use different ports
- **Dependencies**: Reinstall with `pip install -r requirements.txt`
- **CORS issues**: Backend CORS headers should be set
- **API 404**: Check `VITE_API_URL` environment variable

---

## ✅ Deployment Complete

Your iNetZero Platform is now running locally!

**Access your application**:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/v1
- **API Docs**: http://localhost:8000/docs

**Status**:
- ✅ Frontend: Running on port 3000
- ✅ Backend: Running on port 8000
- ✅ Database: SQLite (or PostgreSQL)
- ✅ All features: Available

---

**Happy development!** 🎉

For production deployment, see: `VERCEL_DEPLOYMENT_GUIDE.md`
