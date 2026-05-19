param(
    [Parameter(Mandatory=$true)]
    [string]$Message,
    
    [Parameter(Mandatory=$false)]
    [string]$Level = "ERROR"
)

$configPath = "C:\RegimeOS\kernel\config.json"
if (-not (Test-Path $configPath)) {
    Write-Warning "Config file not found, skipping alert dispatch."
    return
}

$config = Get-Content $configPath -Raw | ConvertFrom-Json

# Discord Webhook Dispatch
if ($config.alert_discord_webhook) {
    try {
        $body = @{
            content = "🚨 **RegimeOS Alert ($Level)**: $Message"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri $config.alert_discord_webhook -Method Post -ContentType "application/json" -Body $body
        Write-Host "Discord alert dispatched successfully." -ForegroundColor Green
    } catch {
        Write-Error "Failed to dispatch Discord alert: $_"
    }
}

# Email Notification Dispatch
if ($config.alert_email_recipient -and $config.alert_email_smtp_server) {
    try {
        $smtpPort = if ($config.alert_email_smtp_port) { $config.alert_email_smtp_port } else { 587 }
        $subject = "🚨 RegimeOS Alert ($Level)"
        $bodyText = "RegimeOS Status Alert`n=================`nLevel: $Level`nTimestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`nMessage: $Message`n`n--`nRegimeOS Automatic Monitor System"
        
        Send-MailMessage -From "alerts@regimeos.local" -To $config.alert_email_recipient -Subject $subject -Body $bodyText -SmtpServer $config.alert_email_smtp_server -Port $smtpPort -ErrorAction Stop
        Write-Host "Email alert dispatched successfully." -ForegroundColor Green
    } catch {
        Write-Warning "Failed to dispatch Email alert: $_ (Make sure SMTP server is accessible)"
    }
}

# Always log alerts to local security/incident audit log
$incidentLogPath = "C:\RegimeOS\logs\system\incidents.md"
$timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
$incidentEntry = "- [$timestamp] ALERT [$Level]: $Message`n"
[System.IO.File]::AppendAllText($incidentLogPath, $incidentEntry, [System.Text.UTF8Encoding]::new($false))
