# monitor-stability.ps1
# RegimeOS v4.1-Windows - Hardened Stability & Alert Monitor
$logPath = "C:\RegimeOS\logs\system\history.md"
$maxSizeKB = 10
$checkIntervalSeconds = 10

$perfLogPath = "C:\RegimeOS\logs\system\performance.log"
$lastLogPosition = 0
$perfLogCounter = 0

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " REGIMEOS STABILITY & ALERT MONITOR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Target Log: $logPath" -ForegroundColor Green
Write-Host " Max Size: $maxSizeKB KB" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# Helper to dispatch alert
function Send-RegimeAlert {
    param($message, $level="ERROR")
    Write-Host "[ALERT] Dispatching: $message" -ForegroundColor Red
    powershell -ExecutionPolicy Bypass -File C:\RegimeOS\bin\send-alert.ps1 -Message $message -Level $level
}

# Initialize log reader position to end of file to monitor only new entries
if (Test-Path $logPath) {
    $lastLogPosition = (Get-Item $logPath).Length
}

# State trackers to avoid alert spamming
$lastHealthStatus = "healthy"
$lastMathStatus = "PASS"

while ($true) {
    # 1. Log Rotation
    if (Test-Path $logPath) {
        $file = Get-Item $logPath
        $sizeKB = $file.Length / 1KB
        
        # Monitor new log entries for errors/anomalies
        if ($file.Length -gt $lastLogPosition) {
            $reader = New-Object System.IO.StreamReader($logPath)
            $reader.BaseStream.Seek($lastLogPosition, [System.IO.SeekOrigin]::Begin) | Out-Null
            while ($line = $reader.ReadLine()) {
                if ($line -like "*[!]*" -or $line -like "*ERROR*" -or $line -like "*ANOMALY*" -or $line -like "*crushed*") {
                    Send-RegimeAlert -Message "Anomaly detected in history log: $line" -Level "WARNING"
                }
            }
            $lastLogPosition = $reader.BaseStream.Position
            $reader.Close()
        }

        if ($sizeKB -gt $maxSizeKB) {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $archivePath = "C:\RegimeOS\logs\system\history_$timestamp.md"
            
            # Perform rotation
            Move-Item $logPath $archivePath -Force
            
            $rotEntry = "- [$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')] SYSTEM: Log rotated. Archive: history_$timestamp.md`n"
            [System.IO.File]::WriteAllText($logPath, $rotEntry, [System.Text.UTF8Encoding]::new($false))
            $lastLogPosition = (Get-Item $logPath).Length
            
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] LOG ROTATED to history_$timestamp.md" -ForegroundColor Yellow
        }
    }
    
    # 2. Performance Baseline Logging (Every 60 seconds = every 6 iterations)
    $perfLogCounter++
    if ($perfLogCounter -ge 6) {
        $perfLogCounter = 0
        try {
            # Get CPU load %
            $cpu = Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average | Select-Object -ExpandProperty Average
            # Get RAM stats
            $os = Get-CimInstance Win32_OperatingSystem
            $totalRamMB = $os.TotalVisibleMemorySize / 1KB
            $freeRamMB = $os.FreePhysicalMemory / 1KB
            $usedRamMB = $totalRamMB - $freeRamMB
            $ramPercent = ($usedRamMB / $totalRamMB) * 100
            
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $perfEntry = "$timestamp | CPU: $($cpu.ToString('F1'))% | RAM: $($usedRamMB.ToString('F0'))MB / $($totalRamMB.ToString('F0'))MB ($($ramPercent.ToString('F1'))%)`n"
            [System.IO.File]::AppendAllText($perfLogPath, $perfEntry, [System.Text.UTF8Encoding]::new($false))
            
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Logged performance: CPU $cpu%, RAM $ramPercent%" -ForegroundColor Gray
        } catch {
            Write-Warning "Failed to log performance metrics: $_"
        }
    }
    
    # 3. Active Process Health Check
    $pwshCount = (Get-Process powershell -ErrorAction SilentlyContinue).Count
    
    # 4. Engine Health Verification (Health-Check.ps1)
    if (Test-Path "C:\RegimeOS\bin\Health-Check.ps1") {
        try {
            $healthJson = powershell -ExecutionPolicy Bypass -File C:\RegimeOS\bin\Health-Check.ps1 | ConvertFrom-Json
            if ($healthJson.status -ne "healthy" -and $lastHealthStatus -eq "healthy") {
                Send-RegimeAlert -Message "System health degraded to status: $($healthJson.status). Core RPM is $($healthJson.core_rpm)." -Level "CRITICAL"
                $lastHealthStatus = $healthJson.status
            } elseif ($healthJson.status -eq "healthy" -and $lastHealthStatus -ne "healthy") {
                Send-RegimeAlert -Message "System health recovered to status: healthy." -Level "INFO"
                $lastHealthStatus = "healthy"
            }
        } catch {
            Write-Warning "Health-Check script execution failed: $_"
        }
    }
    
    # 5. Core Math Verification (verify_proofs.py)
    if (Test-Path "C:\RegimeOS\kernel\verify_proofs.py") {
        try {
            # Run test suite using verified python3.12 path
            $res = Start-Process "C:\Users\cadam\AppData\Local\Microsoft\WindowsApps\python3.12.exe" -ArgumentList "C:\RegimeOS\kernel\verify_proofs.py" -NoNewWindow -PassThru -Wait
            if ($res.ExitCode -ne 0 -and $lastMathStatus -eq "PASS") {
                Send-RegimeAlert -Message "Cryptographic and mathematical proofs verification FAILED!" -Level "CRITICAL"
                $lastMathStatus = "FAIL"
            } elseif ($res.ExitCode -eq 0 -and $lastMathStatus -ne "PASS") {
                Send-RegimeAlert -Message "Cryptographic and mathematical proofs verification RESTORED (PASS)." -Level "INFO"
                $lastMathStatus = "PASS"
            }
        } catch {
            Write-Warning "Math verification suite execution failed: $_"
        }
    }
    
    Start-Sleep -Seconds $checkIntervalSeconds
}
