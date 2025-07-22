@echo off
echo 📅 Setting up Windows Task Scheduler for QA Automation...

:: Luo scheduled task joka ajaa QA-testin 15 minuutin välein
schtasks /create /sc MINUTE /mo 15 /tn "MikroBot_QA_Automation" /tr "python \"C:\Users\HP\Desktop\Claude projects\mikrobot_django_dev\dashboard\qa_automation.py\"" /st %time:~0,5% /ru "HP" /f

if %errorlevel% equ 0 (
    echo ✅ QA Automation scheduled successfully!
    echo    Task runs every 15 minutes
    echo    Task name: MikroBot_QA_Automation
    echo.
    echo 📋 To manage the task:
    echo    View: schtasks /query /tn "MikroBot_QA_Automation"
    echo    Delete: schtasks /delete /tn "MikroBot_QA_Automation" /f
    echo    Run now: schtasks /run /tn "MikroBot_QA_Automation"
) else (
    echo ❌ Failed to create scheduled task
    echo Run as Administrator if needed
)

pause