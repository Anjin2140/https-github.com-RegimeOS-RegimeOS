# Turbine Dynamics Daemon - Phase 3.5 FINAL
$coreRpmPath = "C:\RegimeOS\core_geodisc\velocity\rpm.md"
$mainRpmPath = "C:\RegimeOS\turbine_main\rotor\velocity\rpm.md"
$inboxPath = "C:\RegimeOS\adams_sierpinski\inbox\"
$egressValidatedPath = "C:\RegimeOS\core_geodisc\egress\validated\"
$egressIdlePath = "C:\RegimeOS\core_geodisc\egress\idle\"

Write-Host "=== FILTRATION DAEMON STARTING ===" -ForegroundColor Cyan
Write-Host "Inbox Path: $inboxPath" -ForegroundColor Yellow

$cycleCount = 0
$processedCount = 0

function Get-RPM {
    param($path)
    if (!(Test-Path $path)) { return 0 }
    $c = Get-Content $path -Raw
    return ($c -split ' / ')[0] -as [int]
}

function Set-RPM {
    param($path, $value, $max)
    "$value / $max" | Out-File -FilePath $path -Encoding ASCII
}

while ($true) {
    $cycleCount++
    $processedCount = 0
    $impulses = Get-ChildItem -Path $inboxPath -Filter "*.json" -ErrorAction SilentlyContinue
    
    if ($impulses.Count -gt 0) {
        Write-Host "[$(Get-Date -Format HH:mm:ss)] Cycle $cycleCount - Processing $($impulses.Count) files" -ForegroundColor Green
    }
    
    foreach ($impulse in $impulses) {
        try {
            $content = Get-Content $impulse.FullName -Raw
            $json = $content | ConvertFrom-Json
            $state = $json.tri_polar_state
            
            # Option D: Workload Correlation
            if ($json.source -eq "wolfram_ingestion" -and $json.workload -and $json.rpm_boost) {
                $workload = $json.workload
                $boost = $json.rpm_boost
                $turbinesToBoost = @()
                
                if ($workload -eq "COMPUTED") { $turbinesToBoost = 1..8 }
                elseif ($workload -eq "TRIGONOMETRIC") { $turbinesToBoost = 9..16 }
                elseif ($workload -eq "CALCULUS") { $turbinesToBoost = 17..24 }
                elseif ($workload -eq "MATRIX") { $turbinesToBoost = 25..32 }
                
                foreach ($id in $turbinesToBoost) {
                    $subId = "{0:D2}" -f $id
                    $subPath = "C:\RegimeOS\turbine_sub\sub_turbine_$subId\velocity\rpm.md"
                    if (Test-Path $subPath) {
                        $subRpm = Get-RPM $subPath
                        $newSub = [Math]::Min(500, $subRpm + $boost)
                        Set-RPM $subPath $newSub 500
                    }
                }
                Write-Host "[$(Get-Date -Format HH:mm:ss)] Wolfram Correlation: Ingested $workload -> boosted sub_turbines $($turbinesToBoost[0]) to $($turbinesToBoost[-1])" -ForegroundColor Cyan
            }
            
            if ($state -eq 1) {
                Move-Item $impulse.FullName -Destination $egressValidatedPath -Force
                $processedCount++
            }
            elseif ($state -eq -1) {
                Remove-Item $impulse.FullName -Force
                $processedCount++
            }
            else {
                Move-Item $impulse.FullName -Destination $egressIdlePath -Force
                $processedCount++
            }
        }
        catch {
            Write-Host "ERROR: $($impulse.Name)" -ForegroundColor Red
        }
    }
    
    # RPM UPDATE - Data to Power Conversion
    $coreRpm = Get-RPM $coreRpmPath
    $mainRpm = Get-RPM $mainRpmPath
    
    $newCore = [Math]::Min(2000, $coreRpm + ([Math]::Floor($processedCount / 10)))
    $newMain = [Math]::Min(1000, $mainRpm + ([Math]::Floor($processedCount / 20)))
    
    Set-RPM $coreRpmPath $newCore 2000
    Set-RPM $mainRpmPath $newMain 1000
    
    # SUB-TURBINE UPDATE - Energy Redistribution
    $subBoost = [Math]::Floor($processedCount / 30)
    $subTurbines = Get-ChildItem -Path "C:\RegimeOS\turbine_sub\" -Directory -Filter "sub_turbine_*" -ErrorAction SilentlyContinue
    foreach ($sub in $subTurbines) {
        $subPath = "$($sub.FullName)\velocity\rpm.md"
        if (Test-Path $subPath) {
            $subRpm = Get-RPM $subPath
            $newSub = [Math]::Min(500, $subRpm + $subBoost)
            Set-RPM $subPath $newSub 500
        }
    }
    
    if ($cycleCount % 10 -eq 0) {
        Write-Host "[$(Get-Date -Format HH:mm:ss)] RPM: Core=$newCore, Main=$newMain, Sub-Boost=$subBoost" -ForegroundColor Cyan
    }
    
    Start-Sleep -Seconds 2
}
