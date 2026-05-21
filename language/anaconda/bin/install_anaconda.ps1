# install_anaconda.ps1
# ANACONDA Compiler & Environment Installer
# Classification: BLACK PROJECT // SOVEREIGN

$ErrorActionPreference = "Stop"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "     ANACONDA SOVEREIGN ENVIRONMENT INSTALLER" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# 1. Verify Python installation
Write-Host "[*] Checking Python environment..." -ForegroundColor Yellow
$pythonPath = "python"
if (Test-Path "C:\Users\cadam\AppData\Local\Microsoft\WindowsApps\python3.12.exe") {
    $pythonPath = "C:\Users\cadam\AppData\Local\Microsoft\WindowsApps\python3.12.exe"
}

try {
    $pythonVersion = & $pythonPath --version 2>&1
    Write-Host "[+] Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "Python is not installed or not in system PATH. ANACONDA compiler requires Python 3.12+."
    Exit 1
}

# 2. Verify Cryptography package in Python
Write-Host "[*] Verifying cryptography package..." -ForegroundColor Yellow
$hasCrypto = & $pythonPath -c "import cryptography" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python cryptography library is missing. Run 'pip install cryptography' first."
    Exit 1
}

# 3. Define the embedded public key PEM
$publicKeyPem = @"
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEA1Oydi99yKZdC+jEjJrU6bHtlesaIRB9q/CcmDHZTl0c=
-----END PUBLIC KEY-----
"@

# 4. Verify Manifest Signature using Python
Write-Host "[*] Verifying manifest signature with embedded public key..." -ForegroundColor Yellow

# Write the public key to a temporary file for verification
$tempPubKeyFile = [System.IO.Path]::GetTempFileName()
$publicKeyPem | Out-File -FilePath $tempPubKeyFile -Encoding ascii -NoNewline

$pyVerifyScript = @"
import sys
import json
import hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

try:
    # Load public key
    with open(r'$tempPubKeyFile', 'rb') as f:
        pub_key = serialization.load_pem_public_key(f.read())
        
    # Load manifest and signature
    with open('manifest.json', 'r', encoding='utf-8') as f:
        manifest_data = json.load(f)
    with open('manifest.sig', 'rb') as f:
        signature = f.read()
        
    # Reconstruct manifest hash
    files = manifest_data.get('files', {})
    h_all = hashlib.sha384()
    for rel_path in sorted(files.keys()):
        h_all.update(rel_path.encode('utf-8'))
        h_all.update(files[rel_path].encode('utf-8'))
    manifest_hash = h_all.hexdigest()
    
    # Verify signature
    pub_key.verify(signature, manifest_hash.encode('utf-8'))
    print('SIGNATURE_VERIFIED')
except Exception as e:
    print(f'SIGNATURE_FAILED: {e}')
    sys.exit(1)
"@

$verifyResult = & $pythonPath -c $pyVerifyScript 2>&1

# Clean up temp public key file
if (Test-Path $tempPubKeyFile) {
    Remove-Item $tempPubKeyFile -Force
}

if ($LASTEXITCODE -ne 0 -or $verifyResult -notmatch "SIGNATURE_VERIFIED") {
    Write-Host "[!] $verifyResult" -ForegroundColor Red
    Write-Error "CRITICAL: Manifest signature verification failed. Chain of custody is broken."
    Exit 99
}
Write-Host "[+] SUCCESS: Manifest Ed25519 signature is valid." -ForegroundColor Green

# 5. Verify individual file hashes using PowerShell
Write-Host "[*] Verifying file integrity list (SHA-384)..." -ForegroundColor Yellow

if (-not (Test-Path "manifest.json")) {
    Write-Error "manifest.json not found in the current directory."
    Exit 1
}

$manifest = Get-Content -Raw "manifest.json" | ConvertFrom-Json
$files = $manifest.files
$fileCount = 0

foreach ($relPath in $files.psobject.properties.name) {
    $expectedHash = $files.$relPath
    # Convert forward slashes in manifest path to backslashes for Windows
    $localPath = $relPath.Replace("/", "\")
    
    if (-not (Test-Path $localPath)) {
        Write-Host "[!] Missing file: $localPath" -ForegroundColor Red
        Write-Error "CRITICAL: Missing file in repository: $localPath"
        Exit 99
    }
    
    # Compute SHA-384 hash of the file
    $hashResult = Get-FileHash -Path $localPath -Algorithm SHA384
    $actualHash = $hashResult.Hash.ToLower()
    
    if ($actualHash -ne $expectedHash.ToLower()) {
        Write-Host "[!] Hash mismatch for file: $localPath" -ForegroundColor Red
        Write-Host "    Expected: $expectedHash" -ForegroundColor Red
        Write-Host "    Actual  : $actualHash" -ForegroundColor Red
        Write-Error "CRITICAL: File integrity check failed for $localPath"
        Exit 99
    }
    
    $fileCount++
}

Write-Host "[+] SUCCESS: Verified all $fileCount files successfully. Zero drift detected." -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
Write-Host " ANACONDA ENFORCED INSTALLATION COMPLETE (SECURE)" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
