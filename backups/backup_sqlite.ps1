param(
    [string]$BackupDir = $env:BACKUP_DIR
)

if ([string]::IsNullOrWhiteSpace($BackupDir)) {
    $BackupDir = Join-Path (Get-Location) 'backups'
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$destination = Join-Path $BackupDir "db-$timestamp.sqlite3"
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
Copy-Item 'db.sqlite3' $destination -Force
if (Test-Path 'media') {
    Compress-Archive -Path 'media' -DestinationPath (Join-Path $BackupDir "media-$timestamp.zip") -Force
}
Write-Output "Backup creado: $destination"
