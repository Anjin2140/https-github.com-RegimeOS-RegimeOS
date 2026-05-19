# Backup/Snapshot Script v4.0-Windows
param()
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "C:\RegimeOS\backups\snapshots\snapshot_$timestamp"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

# Backup state files
Get-ChildItem -Path "C:\RegimeOS" -Recurse -Filter "*.md" -Include "*/state/*" | Copy-Item -Destination $backupDir -Force

# Create manifest
$manifest = @"
# Backup Manifest

- **Timestamp:** $timestamp
- **Version:** 4.0-Windows
- **Files Backed Up:** $((Get-ChildItem -Path $backupDir -Filter "*.md" | Measure-Object).Count)
"@
Set-Content -Path "$backupDir\manifest.md" -Value $manifest
Write-Host "Backup complete: $backupDir"
