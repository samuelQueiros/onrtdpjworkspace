param(
  [string]$OutputDirectory = "backups"
)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$output = Join-Path $OutputDirectory "ferias-$timestamp.dump"
New-Item -ItemType Directory -Force $OutputDirectory | Out-Null

docker compose exec -T db pg_dump -U ferias -d ferias -Fc -f /tmp/ferias-backup.dump
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar backup no PostgreSQL." }

docker cp "ferias-db:/tmp/ferias-backup.dump" $output
if ($LASTEXITCODE -ne 0) { throw "Falha ao copiar backup do container." }

docker compose exec -T db rm -f /tmp/ferias-backup.dump
Write-Host "Backup criado em $output"
