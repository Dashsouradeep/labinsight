# 🔍 Backend Connection Test

## Quick Checks

### 1. Is Backend Running?
Check your backend terminal - you should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 2. Test Backend Directly
Open a new terminal and run:
```cmd
curl http://localhost:8000/api/health
```

Or open in browser: http://localhost:8000/docs

### 3. Check Backend Logs
When you upload a file, the backend terminal should show:
```
INFO: POST /api/reports/upload
INFO: Report uploaded successfully
```

If you don't see these logs, the frontend isn't reaching the backend.

---

## Common Issues

### Issue 1: Backend Not Running
**Solution:** Restart backend:
```cmd
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Issue 2: Wrong Port
**Check:** Backend should be on port 8000, frontend on port 3000

### Issue 3: CORS Error
**Check browser console (F12)** for errors like:
```
Access to fetch at 'http://localhost:8000' has been blocked by CORS policy
```

### Issue 4: Authentication Token Missing
**Check browser console** for:
```
401 Unauthorized
```

---

## Debug Steps

1. **Open Browser Console** (F12 → Console tab)
2. **Try uploading again**
3. **Look for errors** - share what you see
4. **Check Network tab** (F12 → Network tab)
   - Look for the upload request
   - Check if it's reaching the backend
   - See the response status code

---

## What to Share

Please share:
1. **Backend terminal output** (last 20 lines)
2. **Browser console errors** (F12 → Console)
3. **Network tab** - status of /api/reports/upload request
