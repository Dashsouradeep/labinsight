# 🧪 LabInsight Testing Guide

## Quick Test (5 minutes)

This guide will help you verify that the LabInsight system is working correctly.

---

## Prerequisites

Before testing, make sure you have:
- ✅ MongoDB running (port 27017)
- ✅ Redis running (port 6379)
- ✅ Backend running (port 8000)
- ✅ Frontend running (port 3000)

### Start Services (if not already running)

**Terminal 1 - MongoDB & Redis (Docker):**
```bash
docker run -d -p 27017:27017 --name labinsight-mongo mongo:latest
docker run -d -p 6379:6379 --name labinsight-redis redis:latest
```

**Terminal 2 - Backend:**
```bash
cd backend
.venv\Scripts\activate
python -m uvicorn main:app --reload --port 8000
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## Test 1: Backend Health Check (30 seconds)

### Check if backend is running:

Open your browser or use curl:
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "environment": "development",
  "services": {
    "api": "operational",
    "database": "operational",
    "redis": "operational",
    "ollama": "pending"
  }
}
```

✅ **Pass:** All services show "operational" (ollama can be "pending")
❌ **Fail:** If you get connection errors, check that MongoDB and Redis are running

---

## Test 2: User Registration (1 minute)

### Open the application:
1. Go to: **http://localhost:3000**
2. You should see the login page
3. Click **"Sign Up"** or go to **http://localhost:3000/auth/signup**

### Create an account:
- **Email:** test@example.com
- **Password:** Test123456!
- **Age:** 30
- **Gender:** Male or Female
- Check the terms checkbox
- Click **"Sign Up"**

**Expected Result:**
- ✅ You should be redirected to the dashboard
- ✅ You should see "Welcome to LabInsight" or similar message
- ✅ No error messages

**Common Issues:**
- ❌ "Email already exists" → Use a different email
- ❌ "Connection error" → Check backend is running
- ❌ "Database error" → Check MongoDB is running

---

## Test 3: Login (30 seconds)

### Test login functionality:
1. Click **"Logout"** (if logged in)
2. Go to: **http://localhost:3000/auth/login**
3. Enter your credentials:
   - **Email:** test@example.com
   - **Password:** Test123456!
4. Click **"Login"**

**Expected Result:**
- ✅ You should be redirected to the dashboard
- ✅ You should see your email in the header
- ✅ No error messages

---

## Test 4: File Upload (2 minutes)

### Create a test lab report:

Create a text file named `test_lab_report.txt` with this content:

```
Lab Results - Patient Test Report

Date: January 15, 2024
Patient ID: TEST001

Complete Blood Count:
Hemoglobin: 14.2 g/dL
WBC: 7.5 k/μL
Platelets: 250 k/μL

Metabolic Panel:
Glucose: 95 mg/dL
Cholesterol: 185 mg/dL
LDL: 110 mg/dL
HDL: 55 mg/dL
Triglycerides: 140 mg/dL

Thyroid Function:
TSH: 2.5 μIU/mL

Liver Function:
ALT: 28 U/L
AST: 32 U/L

Kidney Function:
Creatinine: 0.9 mg/dL
```

Save this as an image (screenshot it) or convert to PDF.

### Upload the file:
1. Go to: **http://localhost:3000/upload**
2. Drag and drop your file OR click to browse
3. Select your test file
4. Click **"Upload Report"**

**Expected Result:**
- ✅ File uploads successfully
- ✅ You see "Processing..." status
- ✅ After 5-15 seconds, status changes to "Completed"
- ✅ You're redirected to the report detail page

**What's Happening:**
- OCR extracts text from your image/PDF
- AI detects medical parameters (hemoglobin, glucose, etc.)
- System classifies risk levels
- Explanations are generated

---

## Test 5: View Report Results (1 minute)

### Check the analysis:
1. You should be on the report detail page
2. Or go to **Dashboard** → Click on your report

**Expected to See:**
- ✅ Report file name and upload date
- ✅ List of detected parameters with values
- ✅ Color-coded risk levels:
  - 🟢 Green = Normal
  - 🟡 Yellow = Mild Abnormal
  - 🔴 Red = Critical
- ✅ Explanations for each parameter
- ✅ Medical disclaimers
- ✅ Normal range information

**Example Parameter Card:**
```
Hemoglobin
14.2 g/dL
Normal Range: 13.5 - 17.5 g/dL
Risk Level: Normal ✓

Explanation: Your hemoglobin level of 14.2 is within the normal range. 
This is a good sign for your health. This is not medical advice. 
Consult your doctor for interpretation.
```

---

## Test 6: Dashboard (30 seconds)

### Check the dashboard:
1. Go to: **http://localhost:3000/dashboard**

**Expected to See:**
- ✅ List of all your uploaded reports
- ✅ Processing status for each report
- ✅ Upload date
- ✅ File names
- ✅ "Upload New Report" button
- ✅ Quick stats (if available)

---

## Test 7: Upload Second Report (Optional - for trends)

### Test trend analysis:
1. Create another test report with slightly different values:

```
Lab Results - Follow-up Report

Date: February 15, 2024

Hemoglobin: 14.8 g/dL
Glucose: 92 mg/dL
Cholesterol: 180 mg/dL
```

2. Upload this second report
3. Go to: **http://localhost:3000/trends**

**Expected to See:**
- ✅ Trend charts for each parameter
- ✅ Trend indicators (↑ Improving, ↓ Worsening, → Stable)
- ✅ Change percentages
- ✅ Summary statistics
- ✅ Date range filters (All Time, 3 Months, 6 Months, 1 Year)

---

## Test 8: Run Automated Tests (Optional)

### Backend Tests:
```bash
cd backend
pytest tests/ -v
```

**Expected:** All tests pass ✅

### Frontend Tests:
```bash
cd frontend
npm test
```

**Expected:** All tests pass ✅

---

## Verification Checklist

Use this checklist to verify everything works:

### Backend
- [ ] Health endpoint returns "healthy"
- [ ] MongoDB connection is operational
- [ ] Redis connection is operational
- [ ] Can create user accounts
- [ ] Can login with credentials
- [ ] Can logout successfully

### File Upload
- [ ] Can upload PDF files
- [ ] Can upload image files (JPEG, PNG)
- [ ] Files under 10MB are accepted
- [ ] Files over 10MB are rejected
- [ ] Invalid file types are rejected

### AI Processing
- [ ] OCR extracts text from uploaded files
- [ ] Parameters are detected (hemoglobin, glucose, etc.)
- [ ] Risk levels are classified correctly
- [ ] Explanations are generated
- [ ] Processing completes within 30 seconds

### Frontend
- [ ] Login page works
- [ ] Signup page works
- [ ] Dashboard displays reports
- [ ] Upload page accepts files
- [ ] Report detail page shows analysis
- [ ] Trends page shows charts (with 2+ reports)
- [ ] All pages are responsive
- [ ] No console errors in browser (F12)

### Data Accuracy
- [ ] Normal values show as "Normal" (green)
- [ ] Slightly abnormal values show as "Mild Abnormal" (yellow)
- [ ] Very abnormal values show as "Critical" (red)
- [ ] Explanations include medical disclaimers
- [ ] Normal ranges are displayed correctly

---

## Troubleshooting

### Issue: "Cannot reach site"
**Solution:** 
- Check MongoDB is running: `docker ps | findstr mongo`
- Check Redis is running: `docker ps | findstr redis`
- Check backend is running: `curl http://localhost:8000/health`
- Check frontend is running: Open http://localhost:3000

### Issue: "No parameters detected"
**Solution:**
- Make sure the image is clear and readable
- Text should contain values like "Hemoglobin: 13.5 g/dL"
- Try the sample test data provided above
- Check backend logs for OCR errors

### Issue: "Processing failed"
**Solution:**
- Check backend terminal for error messages
- Verify PaddleOCR is installed: `pip list | findstr paddle`
- Check file is valid PDF or image
- Try a simpler test file

### Issue: "Authentication error"
**Solution:**
- Clear browser cookies
- Try incognito/private mode
- Check backend logs for JWT errors
- Verify Redis is running

### Issue: Frontend shows blank page
**Solution:**
- Check browser console (F12) for errors
- Verify frontend is running: `npm run dev`
- Check .env.local file exists with correct API URL
- Try refreshing the page (Ctrl+F5)

---

## Performance Benchmarks

Expected performance for a typical report:

| Operation | Expected Time |
|-----------|--------------|
| User signup | < 1 second |
| User login | < 1 second |
| File upload | < 2 seconds |
| OCR processing | 5-10 seconds |
| Parameter extraction | 1-2 seconds |
| Risk classification | < 1 second |
| Total pipeline | 10-15 seconds |
| Page load | < 2 seconds |

---

## Success Criteria

Your system is working correctly if:

✅ All 8 tests above pass
✅ You can create an account and login
✅ You can upload a lab report
✅ The report is processed successfully
✅ You can view the analysis results
✅ Parameters are detected and classified
✅ Explanations are generated
✅ No error messages appear
✅ All pages load without issues

---

## Next Steps After Testing

Once you've verified the system works:

1. **Try with real lab reports** (if you have any)
2. **Upload multiple reports** to test trend analysis
3. **Test with different file formats** (PDF, JPEG, PNG)
4. **Test error cases** (invalid files, large files)
5. **Check mobile responsiveness** (resize browser window)
6. **Review the generated explanations** for accuracy
7. **Test with multiple user accounts**

---

## Getting Help

If you encounter issues:

1. **Check the logs:**
   - Backend: Terminal where you ran `uvicorn`
   - Frontend: Browser console (F12)
   - MongoDB: `docker logs labinsight-mongo`
   - Redis: `docker logs labinsight-redis`

2. **Common log locations:**
   - Backend errors: Terminal output
   - Frontend errors: Browser DevTools Console
   - Network errors: Browser DevTools Network tab

3. **Verify configuration:**
   - `backend/.env` - MongoDB and Redis URLs
   - `frontend/.env.local` - API URL and NextAuth secret

---

## 🎉 Congratulations!

If all tests pass, you have a fully functional AI-powered lab analysis system!

You can now:
- Upload lab reports
- Get AI-powered analysis
- View risk classifications
- Read plain-language explanations
- Track trends over time
- Manage your health data

**Remember:** This is not medical advice. Always consult with your healthcare provider for interpretation of lab results.
