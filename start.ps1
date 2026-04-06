# anthropic-proxy Execution Script for Windows
$ErrorActionPreference = "Stop"

if (-not (Test-Path .env)) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "Please run .\install.ps1 first." -ForegroundColor Yellow
    exit 1
}

Write-Host "🚀 Starting anthropic-proxy..." -ForegroundColor Green
uv run uvicorn server:app --host 0.0.0.0 --port 8082
