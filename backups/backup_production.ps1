param(
    [string]$BackupDir = $env:BACKUP_DIR,
    [int]$RetentionDays = 30
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($BackupDir)) {
    $BackupDir = Join-Path (Get-Location) 'backups'
}

$databaseUrl = $env:DATABASE_URL
if ([string]::IsNullOrWhiteSpace($databaseUrl)) {
    throw 'DATABASE_URL es obligatorio para respaldar PostgreSQL.'
}

$pgDump = Get-Command pg_dump -ErrorAction SilentlyContinue
if ($null -eq $pgDump) {
    throw 'pg_dump no está instalado o no está disponible en PATH.'
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$databaseBackup = Join-Path $BackupDir "postgres-$timestamp.dump"
$mediaBackup = Join-Path $BackupDir "media-$timestamp.zip"

New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
& $pgDump.Source '--format=custom' "--file=$databaseBackup" "--dbname=$databaseUrl"
if ($LASTEXITCODE -ne 0) {
    throw "pg_dump terminó con código $LASTEXITCODE."
}

if (Test-Path 'media') {
    Compress-Archive -Path 'media' -DestinationPath $mediaBackup -Force
}

$cutoff = (Get-Date).AddDays(-$RetentionDays)
Get-ChildItem -Path $BackupDir -File |
    Where-Object { $_.LastWriteTime -lt $cutoff } |
    Remove-Item -Force

Write-Output "Respaldo PostgreSQL creado: $databaseBackup"
if (Test-Path $mediaBackup) {
    Write-Output "Respaldo de archivos creado: $mediaBackup"
}
