# Black Hole Ingress Listener - Phase 4
# RegimeOS v4.1-Windows | STRATSEC Security Protocol

$externalIngressPath = "C:\RegimeOS\external\ingress\"
$coreInboxPath = "C:\RegimeOS\adams_sierpinski\inbox\"
$whiteHolePath = "C:\RegimeOS\core_geodisc\egress\waste\"
$logFile = "C:\RegimeOS\logs\system\history.md"

function Write-IngressLog {
    param($message)
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    $logEntry = "- [$timestamp] INGRESS: $message`n"
    [System.IO.File]::AppendAllText($logFile, $logEntry, [System.Text.UTF8Encoding]::new($false))
}
function Invoke-SecurityValidation {
    param($file)
    try {
        $content = Get-Content $file.FullName -Raw
        $json = $content | ConvertFrom-Json
        if ($json.PSObject.Properties.Name -contains "signature" -and $json.signature -eq "ARMADA_VALID") {
            return $true
        }
        else {
            return $false
        }
    }
    catch {
        return $false
    }
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " BLACK HOLE INGRESS - POWER SOURCE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Funnel Mouth: C:\RegimeOS\external\ingress\" -ForegroundColor Green
Write-Host " Security: Weaponized Trap Active" -ForegroundColor Green
Write-Host " Destination: Centrifugal Core (Inbox)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-IngressLog "BLACK HOLE INGRESS: Daemon Started"

while ($true) {
    $files = Get-ChildItem -Path $externalIngressPath -Filter "*.json" -ErrorAction SilentlyContinue
    
    foreach ($file in $files) {
        $hash = (Get-FileHash $file.FullName -Algorithm SHA256).Hash.Substring(0, 8)
        
        if (Invoke-SecurityValidation -file $file) {
            # Execute Input Preprocessor (ternary_encoder.ps1) to clamp and resolve domains
            powershell -ExecutionPolicy Bypass -File C:\RegimeOS\bin\ternary_encoder.ps1 -filePath $file.FullName
            
            Move-Item $file.FullName -Destination $coreInboxPath -Force
            Write-IngressLog "[$hash] AUTHORIZED - Fed to Core"
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] AUTHORIZED - Core Feed" -ForegroundColor Green
        }
        else {
            Write-IngressLog "[$hash] UNAUTHORIZED - White Hole Purge (Intruder)"
            Remove-Item $file.FullName -Force
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] INTRUDER - Purged" -ForegroundColor Red
        }
    }
    
    Start-Sleep -Seconds 5
}