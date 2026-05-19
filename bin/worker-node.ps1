# RegimeOS Worker Node - Phase 5 Mode 5
param($NodeID)

$centralInbox = "\\SERVER\RegimeOS\ClusterState\inbox\"
$localInbox = "C:\RegimeOS\adams_sierpinski\inbox\"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " WORKER NODE: $NodeID" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

while ($true) {
    # Pull work from central inbox
    $work = Get-ChildItem -Path $centralInbox -Filter "*.json" -ErrorAction SilentlyContinue
    foreach ($item in $work) {
        Copy-Item $item.FullName -Destination $localInbox -Force
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Work received: $($item.Name)" -ForegroundColor Green
    }
    Start-Sleep -Seconds 10
}