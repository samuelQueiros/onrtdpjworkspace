param(
  [string]$OutputDirectory = "backups"
)

$ErrorActionPreference = "Stop"
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
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$output = Join-Path $OutputDirectory "ferias-$timestamp.dump"
New-Item -ItemType Directory -Force $OutputDirectory | Out-Null

docker compose exec -T db pg_dump -U $dbUser -d $dbName -Fc -f /tmp/ferias-backup.dump
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar backup no PostgreSQL." }

docker cp "${container}:/tmp/ferias-backup.dump" $output
if ($LASTEXITCODE -ne 0) { throw "Falha ao copiar backup do container." }

docker compose exec -T db rm -f /tmp/ferias-backup.dump
Write-Host "Backup criado em $output"
