@echo off
echo 🤖 Starting MikroBot QA Monitoring...
echo This will run QA tests every 15 minutes
echo Press Ctrl+C to stop
echo.
start /B cmd /c run_qa_automation.bat
echo ✅ QA Monitoring started in background!
echo You can close this window.