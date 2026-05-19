# Cluster Monitor - Phase 5 Mode 5 (FIXED)
$winrmStatus = (Get-Service WinRM).Status
$nodeCount = (Get-ChildItem "C:\RegimeOS\cluster\nodes\" -ErrorAction SilentlyContinue).Count

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " MODE 5 CLUSTER STATUS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Local Node: ACTIVE" -ForegroundColor Green
Write-Host "WinRM Status: $winrmStatus" -ForegroundColor Green
Write-Host "Cluster State: C:\RegimeOS\cluster\state\" -ForegroundColor Cyan
Write-Host "Worker Nodes: $nodeCount registered" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan