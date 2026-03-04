@echo off
echo ========================================
echo Checking Git Status for GitHub Upload
echo ========================================
echo.

echo Initializing git repository...
git init
echo.

echo Adding all files (respecting .gitignore)...
git add .
echo.

echo ========================================
echo FILES THAT WILL BE COMMITTED:
echo ========================================
git status --short
echo.

echo ========================================
echo FILES THAT ARE IGNORED:
echo ========================================
git status --ignored --short | findstr "!!"
echo.

echo ========================================
echo SUMMARY:
echo ========================================
git status
echo.

echo ========================================
echo To proceed with upload:
echo 1. Review the files above
echo 2. Update README.md with your name
echo 3. Update LICENSE with your name
echo 4. Run: git commit -m "Initial commit: LabInsight"
echo 5. Run: git remote add origin https://github.com/Dashsouradeep/labinsight.git
echo 6. Run: git push -u origin main
echo ========================================
pause
