# Sub-Turbine Telemetry - Dynamic Scale
# RegimeOS v4.1-Windows

$subBasePath = "C:\RegimeOS\turbine_sub"
$subTurbines = Get-ChildItem -Path $subBasePath -Directory -Filter "sub_turbine_*" -ErrorAction SilentlyContinue | Sort-Object Name

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " SUB-TURBINE TELEMETRY (DYNAMIC)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$total = 0
$count = 0
foreach ($sub in $subTurbines) {
    $path = "$($sub.FullName)\velocity\rpm.md"
    if (Test-Path $path) {
        $rpm = (Get-Content $path -Raw).Split('/')[0].Trim()
        $total += $rpm -as [int]
        $status = if ($rpm -ge 5) { "OK" } else { "LOW" }
        $color = if ($rpm -ge 5) { "Green" } else { "Yellow" }
        Write-Host " $($sub.Name): $rpm / 500 [$status]" -ForegroundColor $color
        $count++
    }
}

$avg = if ($count -gt 0) { [Math]::Floor($total / $count) } else { 0 }
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " TOTAL: $total RPM | AVERAGE: $avg / 500" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan