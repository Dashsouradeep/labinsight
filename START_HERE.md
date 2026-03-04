# 🚀 Start LabInsight - Step by Step

## ⚠️ IMPORTANT: Prerequisites

Before starting, you MUST have these running:

### 1. MongoDB
- **Option A (Docker)**: `docker run -d -p 27017:27017 --name mongodb mongo:latest`
- **Option B (Local)**: Start MongoDB service on your system
- **Option C (Cloud)**: Use MongoDB Atlas and update `backend/.env` with your connection string

### 2. Redis
- **Option A (Docker)**: `docker run -d -p 6379:6379 --name redis redis:latest`
- **Option B (Local)**: Start Redis service on your system
- **Option C (Cloud)**: Use Redis Cloud and update `backend/.env` with your connection string

---

## 🎯 Quick Start (After Prerequisites)

### Step 1: Start Backend (Terminal 1)

```bash
cd backend

# Activate virtual environment
.venv\Scripts\activate

# Start the backend server
python -m uvicorn main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 2: Start Frontend (Terminal 2)

```bash
cd frontend

# Start the frontend server
npm run dev
```

**Expected output:**
```
- ready started server on 0.0.0.0:3000
- Local:        http://localhost:3000
```

### Step 3: Open Browser

Go to: **http://localhost:3000**

---

## 🔧 Troubleshooting

### "Cannot reach site" or "Connection refused"

**Check 1: Is MongoDB running?**
```bash
# Test MongoDB connection
curl http://localhost:27017
# Should return: "It looks like you are trying to access MongoDB over HTTP..."
```

**Check 2: Is Redis running?**
```bash
# Test Redis connection (if redis-cli installed)
redis-cli ping
# Should return: PONG
```

**Check 3: Is backend running?**
```bash
# Test backend health
curl http://localhost:8000/health
# Should return JSON with status
```

**Check 4: Is frontend running?**
- Open http://localhost:3000
- Check terminal for errors

### Backend won't start

**Error: "Failed to connect to MongoDB"**
- MongoDB is not running
- Start MongoDB first (see prerequisites above)

**Error: "Failed to connect to Redis"**
- Redis is not running
- Start Redis first (see prerequisites above)

**Error: "ModuleNotFoundError"**
```bash
cd backend
pip install -r requirements.txt
```

### Frontend won't start

**Error: "Cannot find module"**
```bash
cd frontend
npm install
```

**Error: "NEXTAUTH_SECRET is not set"**
- The .env.local file should already be created
- If missing, copy from .env.local.example

---

## 📦 First Time Setup (If not done yet)

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure .env (should already exist)
# Edit backend/.env if you need to change MongoDB/Redis URLs
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# .env.local should already be created
```

---

## ✅ Verification Checklist

Before opening the browser, verify:

- [ ] MongoDB is running (port 27017)
- [ ] Redis is running (port 6379)
- [ ] Backend is running (port 8000) - check terminal for "Application startup complete"
- [ ] Frontend is running (port 3000) - check terminal for "ready started server"
- [ ] No error messages in either terminal

---

## 🎉 Using the System

Once everything is running:

1. **Sign Up**: Create an account at http://localhost:3000
2. **Upload**: Upload a lab report (PDF or image)
3. **Wait**: Processing takes 5-15 seconds
4. **View**: See your results with AI analysis!

---

## 🐳 Easy Mode: Using Docker (Alternative)

If you have Docker installed, you can start MongoDB and Redis easily:

```bash
# Start MongoDB
docker run -d -p 27017:27017 --name labinsight-mongo mongo:latest

# Start Redis
docker run -d -p 6379:6379 --name labinsight-redis redis:latest

# Verify they're running
docker ps
```

Then follow the normal backend/frontend startup steps above.

---

## 📞 Still Having Issues?

Check the logs:
- **Backend logs**: Look at the terminal where you ran `uvicorn`
- **Frontend logs**: Look at the terminal where you ran `npm run dev`
- **Browser console**: Press F12 in your browser

Common issues:
- Port already in use: Change ports in .env files
- Permission denied: Run as administrator or use sudo
- Module not found: Reinstall dependencies
