# wolfram-generator.ps1
# RegimeOS v4.1-Windows
Write-Host "=== WOLFRAM DATABASE INGESTION ACTIVE ===" -ForegroundColor Green
while ($true) {
    powershell -ExecutionPolicy Bypass -File C:\RegimeOS\agents\wolfram_ingestion_core.ps1
    Start-Sleep -Seconds 5
}
