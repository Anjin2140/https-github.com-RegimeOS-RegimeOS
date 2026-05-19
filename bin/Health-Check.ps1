$coreRpmPath = "C:\RegimeOS\core_geodisc\velocity\rpm.md"
$coreRpm = 0
if (Test-Path $coreRpmPath) {
    $c = Get-Content $coreRpmPath -Raw
    $coreRpm = ($c -split ' / ')[0] -as [int]
}
$status = "healthy"
# Verify if the single-core engine process is running
$engineProc = Get-CimInstance Win32_Process -Filter "Name = 'powershell.exe' and CommandLine like '%single-core.ps1%'"
if (-not $engineProc) {
    $status = "critical"
}

$health = [PSCustomObject]@{
    status = $status
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffffffK")
    version = "4.1-Windows"
    kernel = "verified"
    core_rpm = $coreRpm
}
$health | ConvertTo-Json
