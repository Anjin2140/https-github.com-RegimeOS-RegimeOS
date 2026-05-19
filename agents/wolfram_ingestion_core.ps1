# Wolfram Ingestion Core - PowerShell Native
# RegimeOS v4.1-Windows | Phase 3

$timestamp = Get-Date -Format 'yyyyMMddHHmmss'
$impulseFile = "C:\RegimeOS\adams_sierpinski\inbox\impulse_wolfram_$timestamp.json"

$workloads = @("COMPUTED", "TRIGONOMETRIC", "CALCULUS", "MATRIX")
$workload = Get-Random -InputObject $workloads

@{
    source = "wolfram_ingestion"
    timestamp = $timestamp
    workload = $workload
    rpm_boost = 5
    tri_polar_state = 1
} | ConvertTo-Json | Out-File -FilePath $impulseFile -Encoding UTF8

Write-Host "[$timestamp] Wolfram Impulse ($workload) → $impulseFile" -ForegroundColor Green
