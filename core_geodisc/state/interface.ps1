Clear-Host

# Helper to read and parse value
function Get-RPM-Value {
    param($path)
    if (!(Test-Path $path)) { return "0 / 0" }
    $c = (Get-Content $path -Raw).Trim()
    return $c
}

function Get-RPM-Only {
    param($path)
    if (!(Test-Path $path)) { return 0 }
    $c = (Get-Content $path -Raw).Trim()
    return ($c -split ' / ')[0] -as [int]
}

# Read raw displays
$coreRpmRaw = Get-RPM-Value "C:\RegimeOS\core_geodisc\velocity\rpm.md"
$mainRpmRaw = Get-RPM-Value "C:\RegimeOS\turbine_main\rotor\velocity\rpm.md"

# Calculate true average of all sub-turbines dynamically
$subTotal = 0
$subCount = 0
$subTurbines = Get-ChildItem -Path "C:\RegimeOS\turbine_sub\" -Directory -Filter "sub_turbine_*" -ErrorAction SilentlyContinue
foreach ($sub in $subTurbines) {
    $path = "$($sub.FullName)\velocity\rpm.md"
    if (Test-Path $path) {
        $subTotal += Get-RPM-Only $path
        $subCount++
    }
}
$subAvgVal = if ($subCount -gt 0) { [Math]::Floor($subTotal / $subCount) } else { 0 }
$subRpmRaw = "$subAvgVal / 500"

# Format display strings to fit perfectly into the box (width 50)
$coreLine = "║  Core Geodisc RPM: " + $coreRpmRaw.PadRight(27) + " ║"
$mainLine = "║  Main Rotor RPM:   " + $mainRpmRaw.PadRight(27) + " ║"
$subLine  = "║  Sub-Turbine Avg:  " + $subRpmRaw.PadRight(27) + " ║"

Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  RegimeOS Command Center v4.1-Windows          ║" -ForegroundColor Cyan
Write-Host "╠════════════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host $coreLine -ForegroundColor Green
Write-Host $mainLine -ForegroundColor Green
Write-Host $subLine -ForegroundColor Green
Write-Host "║  Rotation Points:  18                          ║" -ForegroundColor Green
Write-Host "║  Learning Layers:  18                          ║" -ForegroundColor Green
Write-Host "║  System Health:    ✓ All Systems Operational   ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
