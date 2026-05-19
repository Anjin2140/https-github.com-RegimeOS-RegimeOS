# Black Hole Data Generator - Phase 5 Live Operations
# RegimeOS v4.1-Windows | STRATSEC Approved

$ingressPath = "C:\RegimeOS\external\ingress\"
$logFile = "C:\RegimeOS\logs\system\ingestion.md"

function Write-IngestionLog {
    param($message)
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    $logEntry = "- [$timestamp] $message`n"
    [System.IO.File]::AppendAllText($logFile, $logEntry, [System.Text.UTF8Encoding]::new($false))
}

function New-AuthorizedData {
    param($id)
    @{
        signature = "ARMADA_VALID"
        type = "AUTHORIZED"
        id = "auth_$id"
        timestamp = Get-Date -Format 'yyyyMMddHHmmss'
        payload = "Valid data payload $id"
        tri_polar_state = 1
    } | ConvertTo-Json
}

function New-IntruderData {
    param($id)
    @{
        signature = "INVALID"
        type = "INTRUDER"
        id = "intruder_$id"
        timestamp = Get-Date -Format 'yyyyMMddHHmmss'
        payload = "Breach attempt $id"
        tri_polar_state = -1
    } | ConvertTo-Json
}

function New-IdleData {
    param($id)
    @{
        signature = "ARMADA_VALID"
        type = "PENDING"
        id = "idle_$id"
        timestamp = Get-Date -Format 'yyyyMMddHHmmss'
        payload = "Pending review $id"
        tri_polar_state = 0
    } | ConvertTo-Json
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " BLACK HOLE DATA GENERATOR - LIVE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Target: C:\RegimeOS\external\ingress\" -ForegroundColor Green
Write-Host " Mode: Continuous Stream" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-IngestionLog "GENERATOR: Black Hole Data Generator Started"

$counter = 0
$authorizedCount = 0
$intruderCount = 0
$idleCount = 0
while ($true) {
    $counter++
    
    # Generate mixed data stream (60% Auth, 25% Intruder, 15% Idle)
    $rand = Get-Random -Minimum 1 -Maximum 100
    
    if ($rand -le 60) {
        # Authorized Data (feeds core)
        $data = New-AuthorizedData -id $counter
        $filename = "auth_$counter.json"
        $authorizedCount++
        $color = "Green"
        $type = "AUTHORIZED"
    }
    elseif ($rand -le 85) {
        # Intruder Data (purged by trap)
        $data = New-IntruderData -id $counter
        $filename = "intruder_$counter.json"
        $intruderCount++
        $color = "Red"
        $type = "INTRUDER"
    }
    else {
        # Idle Data (holding queue)
        $data = New-IdleData -id $counter
        $filename = "idle_$counter.json"
        $idleCount++
        $color = "Yellow"
        $type = "IDLE"
    }
    
    # Drop into Black Hole Funnel
    $data | Out-File -FilePath "$ingressPath\$filename" -Encoding ASCII
    
    # Log every 10 items
    if ($counter % 10 -eq 0) {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Dropped: $counter | Auth: $authorizedCount | Intruder: $intruderCount | Idle: $idleCount" -ForegroundColor $color
        Write-IngestionLog "BATCH: $counter items dropped (Auth: $authorizedCount, Intruder: $intruderCount, Idle: $idleCount)"
    }
    
    # Rate limit: 1 item per second (sustainable load)
    Start-Sleep -Seconds 1
}