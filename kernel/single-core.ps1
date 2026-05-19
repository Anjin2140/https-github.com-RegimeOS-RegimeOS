# === TRI-SIM SINGLE-CORE ENGINE (v3 - BLOAT FILTER) ===

# Create RunspacePool (16 Turbines in 1 Process)
$pool = [runspacefactory]::CreateRunspacePool(1, 32)
$pool.Open()

# Shared State with Thread-Safe Lock Object
$sharedState = @{
    CoreRPM = 2000
    MainRPM = 1000
    SubBoost = 0
    Cycle = 0
}
$syncLock = New-Object System.Object

# Turbine Script Block
$turbineScript = {
    param($inbox, $sharedState, $syncLock)  # ← FIXED: Contiguous param block
    
    # === BLOAT FILTER MATRIX ===
    $bloatPatterns = @(
        ".git", "node_modules", "__pycache__", ".venv",
        "bin", "obj", "*.log", "*.tmp", ".DS_Store", "Thumbs.db"
    )
    # ===========================
    
    while ($true) {
        try {
            $files = Get-ChildItem $inbox -File -ErrorAction SilentlyContinue
            $fileCount = 0
            
            foreach ($file in $files) {
                try {
                    # === BLOAT CHECK ===
                    $isBloat = $false
                    foreach ($pattern in $bloatPatterns) {
                        if ($file.FullName -like "*$pattern*") {
                            $isBloat = $true
                            break
                        }
                    }
                    
                    if ($isBloat) {
                        # Purge Bloat
                        Remove-Item $file.FullName -Force -ErrorAction SilentlyContinue
                        [System.Threading.Monitor]::Enter($syncLock)
                        try { $sharedState.Cycle++; $sharedState.SubBoost++ }
                        finally { [System.Threading.Monitor]::Exit($syncLock) }
                        continue # Skip to next file
                    }
                    # ===================

                    # Process Clean File
                    $hash = Get-FileHash $file.FullName -Algorithm SHA256 -ErrorAction SilentlyContinue

                    # Update shared state (thread-safe using Monitor)
                    [System.Threading.Monitor]::Enter($syncLock)
                    try {
                        $sharedState.SubBoost++
                        $sharedState.Cycle++
                        $fileCount++
                    }
                    finally {
                        [System.Threading.Monitor]::Exit($syncLock)
                    }
                    
                    # Move processed file
                    Move-Item $file.FullName "C:\RegimeOS\adams_sierpinski\processed\" -Force -ErrorAction SilentlyContinue
                }
                catch {
                    # Log error but continue processing
                    [System.Threading.Monitor]::Enter($syncLock)
                    try {
                        $sharedState.Cycle++
                    }
                    finally {
                        [System.Threading.Monitor]::Exit($syncLock)
                    }
                }
            }
            
            # If no files, still increment cycle for telemetry
            if ($fileCount -eq 0) {
                [System.Threading.Monitor]::Enter($syncLock)
                try { $sharedState.Cycle++ }
                finally { [System.Threading.Monitor]::Exit($syncLock) }
                Start-Sleep -Seconds 4
            }
        }
        catch {
            Start-Sleep -Seconds 2
        }
    }
}

# Launch 16 Turbines
$runspaces = @()
for ($i = 0; $i -lt 32; $i++) {
    $ps = [powershell]::Create()
    $ps.RunspacePool = $pool
    $ps.AddScript($turbineScript).AddArgument("C:\RegimeOS\adams_sierpinski\inbox").AddArgument($sharedState).AddArgument($syncLock)
    $runspaces += [PSCustomObject]@{ Pipe = $ps; Async = $ps.BeginInvoke() }
}

# Main Loop (Telemetry Display)
Write-Host "=== TRI-SIM SINGLE-CORE ENGINE ===" -ForegroundColor Cyan
Write-Host "32 Turbines Active | RunspacePool Ready" -ForegroundColor Green
Write-Host ""

while ($true) {
    # Thread-safe read of shared state
    [System.Threading.Monitor]::Enter($syncLock)
    try {
        $cycle = $sharedState.Cycle
        $boost = $sharedState.SubBoost
        $coreRPM = $sharedState.CoreRPM
        $mainRPM = $sharedState.MainRPM
    }
    finally {
        [System.Threading.Monitor]::Exit($syncLock)
    }
    
    # Display telemetry
    $timestamp = Get-Date -Format 'HH:mm:ss'
    Write-Host "[$timestamp] Cycle $cycle - Sub-Boost=$boost | RPM: Core=$coreRPM, Main=$mainRPM" -ForegroundColor Green
    
    Start-Sleep -Seconds 6
}

# Cleanup (Ctrl+C)
$pool.Close()
$pool.Dispose()
