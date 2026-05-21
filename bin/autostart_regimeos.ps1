# C:\RegimeOS\bin\autostart_regimeos.ps1
# Autostart script for all RegimeOS background daemons on Windows startup

$ErrorActionPreference = "Stop"
Write-Host "Booting all RegimeOS background daemons..." -ForegroundColor Cyan

# Define python executable path explicitly
$pythonPath = "C:\Users\cadam\AppData\Local\Microsoft\WindowsApps\python3.12.exe"

# Set environment variables for the daemons
$env:DAEMON_MODE = "true"
$env:POLL_INTERVAL = "30"
$env:REGIME_BASE_DIR = "C:\RegimeOS"

# Pre-Launch Integrity Check (Enforced Sovereign Chain of Custody)
Write-Host "[*] Executing pre-launch signature verification..." -ForegroundColor Yellow
$verifyOutput = & $pythonPath "C:\RegimeOS\language\anaconda\src\compiler\vault.py" --verify 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] SEC_VIOLATION: Signature check failed! Aborting startup." -ForegroundColor Red
    Write-Error "CRITICAL: Integrity check failed: $verifyOutput"
    Exit 99
}
Write-Host "[+] Integrity check passed: $verifyOutput" -ForegroundColor Green

# 1. Start the FastAPI Web Portal (HTTPS/HTTP)
Start-Process -FilePath $pythonPath -ArgumentList "C:\RegimeOS\portal\app.py" -WorkingDirectory "C:\RegimeOS\portal" -WindowStyle Hidden

# 2. Start the ANACONDA Secure Financial Ingester (continuous loop mode)
Start-Process -FilePath $pythonPath -ArgumentList "C:\RegimeOS\language\anaconda\bin\anaconda-runtime.py C:\RegimeOS\language\anaconda\src\examples\financial_ingester.air" -WorkingDirectory "C:\RegimeOS\language\anaconda" -WindowStyle Hidden

# 3. Start Core single-core math controller
Start-Process -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy Bypass -File C:\RegimeOS\kernel\single-core.ps1" -WorkingDirectory "C:\RegimeOS\kernel" -WindowStyle Hidden

# 4. Start Stability Monitor
Start-Process -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy Bypass -File C:\RegimeOS\bin\monitor-stability.ps1" -WorkingDirectory "C:\RegimeOS\bin" -WindowStyle Hidden

# 5. Start Black Hole Ingress
Start-Process -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy Bypass -File C:\RegimeOS\bin\black_hole_ingress_active.ps1" -WorkingDirectory "C:\RegimeOS\bin" -WindowStyle Hidden

# 6. Start Turbine Dynamics
Start-Process -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy Bypass -File C:\RegimeOS\kernel\turbine_dynamics_active.ps1" -WorkingDirectory "C:\RegimeOS\kernel" -WindowStyle Hidden

# 7. Start Wolfram Generator
Start-Process -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy Bypass -File C:\RegimeOS\bin\wolfram-generator.ps1" -WorkingDirectory "C:\RegimeOS\bin" -WindowStyle Hidden

Write-Host "All background daemons initialized successfully!" -ForegroundColor Green
