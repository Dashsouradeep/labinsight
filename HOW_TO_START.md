# 🚀 How to Start LabInsight

## ✅ Prerequisites Verified
- MongoDB Atlas: Connected successfully
- Redis: Running on Docker (port 6379)
- Python dependencies: Core packages installed
- Frontend: Ready to start

## 📋 Quick Start (3 Steps)

### Step 1: Start Backend Server
Open a terminal and run:
```cmd
cd backend
python -m uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 2: Start Frontend Server
Open a NEW terminal and run:
```cmd
cd frontend
npm run dev
```

You should see:
```
- Local:        http://localhost:3000
- Ready in [time]
```

### Step 3: Open Your Browser
Go to: **http://localhost:3000**

---

## 🎯 What You Can Do Now

### 1. **Sign Up / Login**
- Create a new account at `/auth/signup`
- Login at `/auth/login`

### 2. **Upload Lab Reports**
- Go to `/upload`
- Upload a lab report image (JPEG/PNG) or PDF
- System will extract parameters automatically

### 3. **View Dashboard**
- See all your uploaded reports
- View processing status

### 4. **View Report Details**
- Click on any report to see extracted parameters
- View risk levels (Normal/Mild Abnormal/Critical)
- Read AI-generated explanations

### 5. **View Trends**
- Track parameter changes over time
- See visual charts of your health metrics

---

## 🔧 Current System Status

✅ **Working Features:**
- User authentication (signup/login/logout)
- File upload and validation
- MongoDB Atlas database
- Redis session storage
- Basic parameter extraction (regex-based)
- Risk classification
- Frontend UI with all pages

⚠️ **Temporary Limitations:**
- OCR uses mock data (PaddleOCR not installed yet)
- Upload a report and you'll see sample extracted parameters
- Real OCR will be added once dependencies finish installing

---

## 🐛 Troubleshooting

### Backend won't start?
```cmd
cd backend
pip install fastapi uvicorn python-multipart pymongo motor redis python-jose passlib bcrypt python-dotenv pydantic pydantic-settings email-validator
```

### Frontend won't start?
```cmd
cd frontend
npm install
```

### Can't connect to database?
Check `backend/.env` has:
```
MONGODB_URL=mongodb+srv://labinsight_user:labinsight_user%4073@labinsight.wzzhapp.mongodb.net/?appName=LabInsight
```

---

## 📝 Test the System

1. **Sign up** with email and password
2. **Login** with your credentials
3. **Upload** a lab report image
4. **View** the extracted parameters
5. **Check** the trends page

The system is now functional with basic AI analysis!
