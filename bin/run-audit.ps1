# Audit Runner - Phase 4
. C:\RegimeOS\kernel\shakespeare_audit.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " SHAKESPEARE-4096 AUDIT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$files = @(
    "C:\RegimeOS\core_geodisc\velocity\rpm.md",
    "C:\RegimeOS\adams_sierpinski\inbox\*.json",
    "C:\RegimeOS\core_geodisc\egress\validated\*.json"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        $hash = Get-ShakespeareHash $file
        Write-AuditLog "File: $file | Hash: $hash"
        Write-Host "[$(Split-Path $file -Leaf)] $hash.Substring(0,16)..." -ForegroundColor Gray
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Audit complete - See logs\system\audit.md" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan