@echo off
echo 🤖 MikroBot QA Automation Starting...
echo Timestamp: %date% %time%

cd /d "C:\Users\HP\Desktop\Claude projects\mikrobot_django_dev"

:loop
echo.
echo 📡 Checking Django server...
curl -s http://localhost:8000/dashboard/ > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Django server not running! Start with: python manage.py runserver
    echo Waiting 60 seconds and retrying...
    timeout /t 60 /nobreak > nul
    goto :loop
)

echo ✅ Django server is running
echo.
echo 🧪 Running QA automation...

python dashboard/qa_automation.py

echo.
echo ⏰ Next run in 15 minutes... (Press Ctrl+C to stop)
timeout /t 900 /nobreak > nul

goto :loop