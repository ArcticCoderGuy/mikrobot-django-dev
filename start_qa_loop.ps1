# MikroBot QA Automation Loop
Write-Host "🤖 MikroBot QA Automation starting..." -ForegroundColor Green
Write-Host "Tests will run every 15 minutes" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor White

$projectPath = "C:\Users\HP\Desktop\Claude projects\mikrobot_django_dev"
Set-Location $projectPath

while ($true) {
    Write-Host "`n⏰ $(Get-Date -Format 'HH:mm:ss') - Running QA tests..." -ForegroundColor Cyan
    
    try {
        python "dashboard/qa_automation.py" 2>$null
        Write-Host "✅ QA tests completed" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ QA test failed: $_" -ForegroundColor Red
    }
    
    Write-Host "💤 Sleeping for 15 minutes..." -ForegroundColor Yellow
    Start-Sleep -Seconds 900  # 15 minutes
}