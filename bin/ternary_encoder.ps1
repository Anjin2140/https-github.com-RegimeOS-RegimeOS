# Input Preprocessor - Phase 5
# ternary_encoder.ps1 | RegimeOS Input Preprocessor
# Implements: ▼, -∞ -> -0, |0|, +0 -> +∞, ▲

param(
    [string]$filePath
)

if (!(Test-Path $filePath)) {
    Write-Error "File not found: $filePath"
    exit 1
}

try {
    $content = Get-Content $filePath -Raw
    $json = $content | ConvertFrom-Json
    
    # Extract raw input state/value for processing
    $rawValue = 0
    if ($json.PSObject.Properties.Name -contains "raw_value") {
        $rawValue = $json.raw_value -as [double]
    } elseif ($json.PSObject.Properties.Name -contains "tri_polar_state") {
        $rawValue = $json.tri_polar_state -as [double]
    } else {
        $rawValue = 0
    }
    
    # Constants for the Architect Anchor bounds (▼ = -13, ▲ = 13)
    $Nabla = -13.0
    $Delta = 13.0
    $Deadband = 0.0
    
    # 1. Bounds Clamping (▼ & ▲)
    $clampedValue = $rawValue
    if ($rawValue -lt $Nabla) {
        $clampedValue = $Nabla
    } elseif ($rawValue -gt $Delta) {
        $clampedValue = $Delta
    }
    
    # 2. Domain Polarity Resolution (▼, -∞ -> -0, |0|, +0 -> +∞, ▲)
    $triPolarState = 0
    if ($clampedValue -eq $Deadband) {
        $triPolarState = 0 # Absolute Deadband |0|
    } elseif ($clampedValue -lt $Deadband) {
        $triPolarState = -1 # Negative Domain (-∞ -> -0)
    } else {
        $triPolarState = 1 # Positive Domain (+0 -> +∞)
    }
    
    # 3. Update JSON fields
    # We add the clamped preprocessed_value and assign the resolved tri_polar_state
    if ($json.PSObject.Properties.Name -contains "preprocessed_value") {
        $json.preprocessed_value = $clampedValue
    } else {
        $json | Add-Member -MemberType NoteProperty -Name "preprocessed_value" -Value $clampedValue -Force
    }
    $json.tri_polar_state = $triPolarState
    
    # 4. Write back to file
    $json | ConvertTo-Json | Out-File -FilePath $filePath -Encoding UTF8
    
    # 5. Log transaction
    $hash = (Get-FileHash $filePath -Algorithm SHA256).Hash.Substring(0, 8)
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    $logEntry = "- [$timestamp] PREPROCESS: File: $(Split-Path $filePath -Leaf) | Hash: $hash | Raw: $rawValue -> Clamped: $clampedValue -> State: $triPolarState`n"
    [System.IO.File]::AppendAllText("C:\RegimeOS\logs\system\history.md", $logEntry, [System.Text.UTF8Encoding]::new($false))
    
    Write-Host "[PREPROCESS] Success: $rawValue -> Clamped: $clampedValue -> State: $triPolarState" -ForegroundColor Green
}
catch {
    Write-Error "Failed to preprocess file: $_"
    exit 1
}
