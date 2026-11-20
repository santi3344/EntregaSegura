param(
    [Parameter(Mandatory = $true)]
    [string]$DatabaseBackup,
    [string]$DatabaseUrl = $env:RESTORE_DATABASE_URL
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $DatabaseBackup)) {
    throw "No existe el respaldo indicado: $DatabaseBackup"
}
if ([string]::IsNullOrWhiteSpace($DatabaseUrl)) {
    throw 'RESTORE_DATABASE_URL es obligatorio para restaurar.'
}

$pgRestore = Get-Command pg_restore -ErrorAction SilentlyContinue
if ($null -eq $pgRestore) {
    throw 'pg_restore no está instalado o no está disponible en PATH.'
}

& $pgRestore.Source '--clean' '--if-exists' '--no-owner' "--dbname=$DatabaseUrl" $DatabaseBackup
if ($LASTEXITCODE -ne 0) {
    throw "pg_restore terminó con código $LASTEXITCODE."
}

Write-Output "Restauración completada en la base de datos de prueba."
