param(
  [string]$OutputDirectory = "backups",
  [string]$UploadsDirectory = "uploads"
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
New-Item -ItemType Directory -Force $OutputDirectory | Out-Null
$staging = Join-Path $OutputDirectory ".backup-$timestamp"
$output = Join-Path $OutputDirectory "ferias-$timestamp.zip"
$databaseDump = Join-Path $staging "database.dump"
New-Item -ItemType Directory -Force $staging | Out-Null

try {
  docker compose exec -T db pg_dump -U $dbUser -d $dbName -Fc -f /tmp/ferias-backup.dump
  if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar backup no PostgreSQL." }

  docker cp "${container}:/tmp/ferias-backup.dump" $databaseDump
  if ($LASTEXITCODE -ne 0) { throw "Falha ao copiar backup do container." }

  $uploadsDestino = Join-Path $staging "uploads"
  if (Test-Path -LiteralPath $UploadsDirectory) {
    Copy-Item -LiteralPath $UploadsDirectory -Destination $uploadsDestino -Recurse
  } else {
    New-Item -ItemType Directory -Force $uploadsDestino | Out-Null
  }

  @{
    formato = 1
    criado_em_utc = (Get-Date).ToUniversalTime().ToString("o")
    banco = $dbName
    inclui_uploads = $true
  } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $staging "manifest.json") -Encoding UTF8

  Compress-Archive -Path (Join-Path $staging "*") -DestinationPath $output -CompressionLevel Optimal
  $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $output).Hash.ToLowerInvariant()
  Set-Content -LiteralPath "$output.sha256" -Value "$hash  $(Split-Path $output -Leaf)" -Encoding ASCII
  Write-Host "Backup criado em $output (banco, uploads e checksum SHA-256)."
} finally {
  docker compose exec -T db rm -f /tmp/ferias-backup.dump 2>$null
  if (Test-Path -LiteralPath $staging) {
    Remove-Item -LiteralPath $staging -Recurse -Force
  }
}
