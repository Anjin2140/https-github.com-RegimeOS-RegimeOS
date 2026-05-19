# Uninstall Script v4.0-Windows
Write-Host "[!] Uninstalling RegimeOS v4.0-Windows..." -ForegroundColor Yellow
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\RegimeOS" -Recurse -Force
Write-Host "[+] RegimeOS Removed. System restored to R0 baseline." -ForegroundColor Green
