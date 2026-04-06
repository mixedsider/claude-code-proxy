# anthropic-proxy Restart Script for Windows
$ErrorActionPreference = "Continue"

Write-Host "`n🔍 Finding and stopping existing anthropic-proxy processes on port 8082..." -ForegroundColor Cyan

# Find processes using port 8082
$connections = Get-NetTCPConnection -LocalPort 8082 -ErrorAction SilentlyContinue

if ($connections) {
    foreach ($conn in $connections) {
        $p = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
        if ($p) {
            Write-Host "🛑 Stopping process $($p.ProcessName) (PID: $($p.Id))..." -ForegroundColor Yellow
            Stop-Process -Id $p.Id -Force
        }
    }
    Write-Host "✅ Existing processes stopped." -ForegroundColor Green
} else {
    Write-Host "ℹ️ No existing process found on port 8082." -ForegroundColor Gray
}

# Start the server using start.ps1
.\start.ps1
