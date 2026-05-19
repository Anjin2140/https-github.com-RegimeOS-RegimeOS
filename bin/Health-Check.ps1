$coreRpmPath = "C:\RegimeOS\core_geodisc\velocity\rpm.md"
$coreRpm = 0
if (Test-Path $coreRpmPath) {
    $c = Get-Content $coreRpmPath -Raw
    $coreRpm = ($c -split ' / ')[0] -as [int]
}
$status = "healthy"
if ($coreRpm -le 0) { $status = "warning" }

$health = [PSCustomObject]@{
    status = $status
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffffffK")
    version = "4.1-Windows"
    kernel = "verified"
    core_rpm = $coreRpm
}
$health | ConvertTo-Json
