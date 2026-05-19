# monitor-stability.ps1
# RegimeOS v4.1-Windows
$logPath = "C:\RegimeOS\logs\system\history.md"
$maxSizeKB = 10
$checkIntervalSeconds = 10 # Short interval for demonstration/testing

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " REGIMEOS STABILITY MONITOR & ROTATOR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Target Log: $logPath" -ForegroundColor Green
Write-Host " Max Size: $maxSizeKB KB" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

while ($true) {
    if (Test-Path $logPath) {
        $file = Get-Item $logPath
        $sizeKB = $file.Length / 1KB
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Checked log size: $($sizeKB.ToString('F2')) KB"
        
        if ($sizeKB -gt $maxSizeKB) {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $archivePath = "C:\RegimeOS\logs\system\history_$timestamp.md"
            
            # Perform rotation
            Move-Item $logPath $archivePath -Force
            
            $rotEntry = "- [$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')] SYSTEM: Log rotated. Archive: history_$timestamp.md`n"
            [System.IO.File]::WriteAllText($logPath, $rotEntry, [System.Text.UTF8Encoding]::new($false))
            
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] LOG ROTATED to history_$timestamp.md" -ForegroundColor Yellow
        }
    }
    
    # Run status check of the single-core engine / turbines
    # Let's count processes
    $pwshCount = (Get-Process powershell -ErrorAction SilentlyContinue).Count
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] System Health: PowerShell Tasks = $pwshCount"
    
    Start-Sleep -Seconds $checkIntervalSeconds
}
