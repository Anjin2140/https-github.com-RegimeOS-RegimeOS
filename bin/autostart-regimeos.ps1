# RegimeOS Auto-Start Script - Phase 5
# Runs both daemons on system boot

# Start Turbine Dynamics
Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File C:\RegimeOS\kernel\turbine_dynamics.ps1" -WindowStyle Normal

# Start Black Hole Ingress
Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File C:\RegimeOS\bin\black_hole_ingress.ps1" -WindowStyle Normal

# Start Web Portal Dashboard API
Start-Process "C:\Users\cadam\AppData\Local\Microsoft\WindowsApps\python3.12.exe" -ArgumentList "C:\RegimeOS\portal\app.py" -WindowStyle Hidden

# Log startup
$timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
$logEntry = "- [$timestamp] AUTOSTART: Core daemons and Web Portal dashboard launched`n"
[System.IO.File]::AppendAllText("C:\RegimeOS\logs\system\history.md", $logEntry, [System.Text.UTF8Encoding]::new($false))