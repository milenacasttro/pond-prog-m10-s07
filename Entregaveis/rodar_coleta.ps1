# Rode na raiz do projeto (PowerShell)
# Uso: .\Entregaveis\rodar_coleta.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not $env:GITHUB_TOKEN) {
    Write-Host "GITHUB_TOKEN nao definido." -ForegroundColor Yellow
    Write-Host "Defina antes de rodar:"
    Write-Host '  $env:GITHUB_TOKEN = "ghp_seuToken"' -ForegroundColor Cyan
    exit 1
}

Write-Host "Coletando metricas..." -ForegroundColor Green
python Entregaveis/coletar_metricas.py milenacasttro pond-prog-m10-s07 --all-runs --limit 30
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Gerando graficos..." -ForegroundColor Green
python Entregaveis/gerar_graficos.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Pronto!" -ForegroundColor Green
Write-Host "  Entregaveis/dados/metricas.csv"
Write-Host "  Entregaveis/graficos/*.png"
