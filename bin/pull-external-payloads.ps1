# pull-external-payloads.ps1
# RegimeOS v4.1-Windows
$localClonePath = "C:\RegimeOS\external\local_clone"
$ingressPath = "C:\RegimeOS\external\ingress\"

if (!(Test-Path $localClonePath)) {
    Write-Error "Local clone path not found at $localClonePath"
    exit 1
}

# Run git pull
Write-Host "Pulling latest payloads from remote repository..." -ForegroundColor Cyan
Set-Location $localClonePath
$pullResult = git pull 2>&1
Write-Host $pullResult

# Scan for incoming json payloads
$payloads = Get-ChildItem -Path $localClonePath -Filter "*.json" -ErrorAction SilentlyContinue
if ($payloads.Count -gt 0) {
    Write-Host "Found $($payloads.Count) payloads. Validating signatures..." -ForegroundColor Yellow
}

foreach ($payload in $payloads) {
    try {
        $content = Get-Content $payload.FullName -Raw
        $json = $content | ConvertFrom-Json
        
        # Security Signature Check (ARMADA_VALID)
        if ($json.PSObject.Properties.Name -contains "signature" -and $json.signature -eq "ARMADA_VALID") {
            $dest = Join-Path $ingressPath $payload.Name
            Move-Item $payload.FullName -Destination $dest -Force
            Write-Host "AUTHORIZED: $($payload.Name) moved to ingress." -ForegroundColor Green
        }
        else {
            Remove-Item $payload.FullName -Force
            Write-Host "INTRUDER REJECTED: $($payload.Name) deleted." -ForegroundColor Red
        }
    }
    catch {
        Write-Host "ERROR parsing $($payload.Name)" -ForegroundColor Red
    }
}
