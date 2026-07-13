param(
  [Parameter(Mandatory = $true)]
  [string]$BackupFile,
  [switch]$Force
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $BackupFile)) { throw "Backup não encontrado: $BackupFile" }
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

try {
  docker compose stop backend
  docker cp $BackupFile "${container}:/tmp/ferias-restore.dump"
  if ($LASTEXITCODE -ne 0) { throw "Falha ao copiar o backup para o container." }
  docker compose exec -T db pg_restore -U $dbUser -d $dbName --clean --if-exists --no-owner /tmp/ferias-restore.dump
  if ($LASTEXITCODE -ne 0) { throw "Falha ao restaurar o banco." }
  docker compose run --rm --entrypoint alembic backend upgrade head
  if ($LASTEXITCODE -ne 0) { throw "A restauração foi aplicada, mas as migrations falharam." }
  Write-Host "Restauração concluída e migrations aplicadas com sucesso."
} finally {
  docker compose exec -T db rm -f /tmp/ferias-restore.dump 2>$null
  if ($backendWasRunning) { docker compose up -d backend }
}
