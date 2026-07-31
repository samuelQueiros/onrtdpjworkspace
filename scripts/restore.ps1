param(
  [Parameter(Mandatory = $true)]
  [string]$BackupFile,
  [switch]$Force,
  [string]$UploadsDirectory = "uploads",
  [switch]$SkipSafetyBackup
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $BackupFile)) { throw "Backup não encontrado: $BackupFile" }
$BackupFile = (Resolve-Path -LiteralPath $BackupFile).Path
if (-not $Force) {
  $confirmation = Read-Host "A restauração substituirá os dados atuais. Digite RESTAURAR para continuar"
  if ($confirmation -ne "RESTAURAR") { throw "Restauração cancelada." }
}

$config = @{}
if (Test-Path ".env") {
  Get-Content ".env" | Where-Object { $_ -match '^\s*([^#][^=]*)=(.*)$' } | ForEach-Object {
    $config[$matches[1].Trim()] = $matches[2].Trim()
  }
}
$dbUser = if ($config.POSTGRES_USER) { $config.POSTGRES_USER } else { "ferias" }
$dbName = if ($config.POSTGRES_DB) { $config.POSTGRES_DB } else { "ferias" }
$container = docker compose ps -q db
if (-not $container) { throw "O container do PostgreSQL não está em execução." }
$backendWasRunning = [bool](docker compose ps --status running -q backend)
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$staging = Join-Path ([System.IO.Path]::GetTempPath()) "ferias-restore-$timestamp"
$databaseDump = $BackupFile
$uploadsBackup = $null

try {
  if (-not $SkipSafetyBackup) {
    & (Join-Path $PSScriptRoot "backup.ps1") -UploadsDirectory $UploadsDirectory
    if ($LASTEXITCODE -ne 0) { throw "Falha ao criar backup de segurança antes da restauração." }
  }

  if ($BackupFile.EndsWith(".zip", [StringComparison]::OrdinalIgnoreCase)) {
    $checksumFile = "$BackupFile.sha256"
    if (-not (Test-Path -LiteralPath $checksumFile)) {
      throw "Checksum ausente: $checksumFile"
    }
    $esperado = ((Get-Content -LiteralPath $checksumFile -Raw).Trim() -split '\s+')[0].ToLowerInvariant()
    $obtido = (Get-FileHash -Algorithm SHA256 -LiteralPath $BackupFile).Hash.ToLowerInvariant()
    if ($esperado -ne $obtido) { throw "Checksum SHA-256 do backup inválido." }

    New-Item -ItemType Directory -Force $staging | Out-Null
    Expand-Archive -LiteralPath $BackupFile -DestinationPath $staging
    $databaseDump = Join-Path $staging "database.dump"
    if (-not (Test-Path -LiteralPath $databaseDump)) {
      throw "O pacote não contém database.dump."
    }
  }

  docker compose stop backend
  docker cp $databaseDump "${container}:/tmp/ferias-restore.dump"
  if ($LASTEXITCODE -ne 0) { throw "Falha ao copiar o backup para o container." }
  docker compose exec -T db pg_restore -U $dbUser -d $dbName --clean --if-exists --no-owner /tmp/ferias-restore.dump
  if ($LASTEXITCODE -ne 0) { throw "Falha ao restaurar o banco." }
  docker compose run --rm migrate
  if ($LASTEXITCODE -ne 0) { throw "A restauração foi aplicada, mas as migrations falharam." }

  $uploadsRestaurados = Join-Path $staging "uploads"
  if (Test-Path -LiteralPath $uploadsRestaurados) {
    if (Test-Path -LiteralPath $UploadsDirectory) {
      $uploadsBackup = "$UploadsDirectory.pre-restore-$timestamp"
      Move-Item -LiteralPath $UploadsDirectory -Destination $uploadsBackup
    }
    Copy-Item -LiteralPath $uploadsRestaurados -Destination $UploadsDirectory -Recurse
  }
  Write-Host "Restauração concluída e migrations aplicadas com sucesso."
  if ($uploadsBackup) { Write-Host "Uploads anteriores preservados em $uploadsBackup" }
} finally {
  docker compose exec -T db rm -f /tmp/ferias-restore.dump 2>$null
  if (Test-Path -LiteralPath $staging) {
    Remove-Item -LiteralPath $staging -Recurse -Force
  }
  if ($backendWasRunning) { docker compose up -d backend }
}
