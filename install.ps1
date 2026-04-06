# anthropic-proxy Installation Script for Windows
$ErrorActionPreference = "Stop"

Write-Host "🔍 Checking for uv..." -ForegroundColor Cyan
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "❌ uv not found. Installing uv..." -ForegroundColor Yellow
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    # Note: PATH might not be updated in the current session
    Write-Host "⚠️  uv has been installed. You may need to restart your terminal." -ForegroundColor DarkYellow
} else {
    Write-Host "✅ uv is already installed." -ForegroundColor Green
}

Write-Host "⚙️  Configuring environment..." -ForegroundColor Cyan
if (-not (Test-Path .env)) {
    if (Test-Path .env.example) {
        Copy-Item .env.example .env
        Write-Host "✅ Created .env from .env.example" -ForegroundColor Green
        Write-Host "⚠️  Please edit .env and add your API keys." -ForegroundColor Yellow
    } else {
        Write-Host "❌ .env.example not found. Please create .env manually." -ForegroundColor Red
    }
} else {
    Write-Host "ℹ️  .env already exists, skipping." -ForegroundColor Gray
}

Write-Host "🚀 Setup complete!" -ForegroundColor Green
Write-Host "--------------------------------------------------"
Write-Host "To start the server, run:" -ForegroundColor White
Write-Host "  .\start.ps1" -ForegroundColor White
Write-Host "--------------------------------------------------"
