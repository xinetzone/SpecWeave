# DevContainer Win11 - System PowerShell Profile
# Applied to all users (System32 PowerShell profile location)

# UTF-8 encoding
chcp 65001 | Out-Null

# Initialize conda if available
if (Test-Path "C:\conda\Scripts\conda.exe") {
    try {
        (& "C:\conda\Scripts\conda.exe" "shell.powershell" "hook") | Out-String | Invoke-Expression
        conda activate main 2>$null
    } catch {
        Write-Warning "Conda initialization failed: $_"
    }
}

# Ensure free-threading Python environment variable
$env:Py_GIL_DISABLED = "1"

# Set default location to workspace
if (Test-Path "C:\workspace") {
    Set-Location "C:\workspace"
}

# Welcome message
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  DevContainer Win11 - PowerShell Session" -ForegroundColor Cyan
Write-Host "  Python: Free-threading (cp314t) via Miniforge3" -ForegroundColor Cyan
Write-Host "  Workspace: C:\workspace" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
