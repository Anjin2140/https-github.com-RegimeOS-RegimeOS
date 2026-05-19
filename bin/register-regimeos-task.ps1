# register-regimeos-task.ps1
# RegimeOS v4.1-Windows
$taskName = "RegimeOS-Daemons-User"
$startupPath = [System.IO.Path]::Combine($env:APPDATA, 'Microsoft\Windows\Start Menu\Programs\Startup')
$batFile = Join-Path $startupPath "regimeos_startup.bat"

Write-Host "Attempting auto-boot registration..." -ForegroundColor Cyan

try {
    # Method 1: Task Scheduler (Try standard registration)
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    }
    
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File C:\RegimeOS\bin\autostart-regimeos.ps1"
    $trigger = New-ScheduledTaskTrigger -AtLogon
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    $registeredTask = Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force
    
    if ($registeredTask) {
        Write-Host "SUCCESS: Registered scheduled task via Task Scheduler!" -ForegroundColor Green
        # Cleanup startup folder if it existed
        if (Test-Path $batFile) { Remove-Item $batFile -Force }
        exit 0
    }
}
catch {
    Write-Host "Task Scheduler registration failed or denied (normal for standard user sandbox). Trying User Startup Folder..." -ForegroundColor Yellow
}

# Method 2: User Startup Folder (Reliable Standard User Fallback)
try {
    if (!(Test-Path $startupPath)) {
        New-Item -ItemType Directory -Path $startupPath -Force | Out-Null
    }
    
    $batContent = @"
@echo off
REM Auto-start RegimeOS Daemons
start /min powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\RegimeOS\bin\autostart-regimeos.ps1
"@
    $batContent | Out-File -FilePath $batFile -Encoding ASCII -Force
    
    if (Test-Path $batFile) {
        Write-Host "SUCCESS: Registered autostart bat file in User Startup folder:" -ForegroundColor Green
        Write-Host "Path: $batFile" -ForegroundColor Cyan
    } else {
        Write-Error "Failed to write bat file in User Startup folder."
    }
}
catch {
    Write-Error "Failed to register auto-boot shortcut: $_"
}
