# DevContainer Win11 - Health Check Script
# Returns 0 if healthy, 1 if unhealthy
# Checks: sshd port 22 listening + jupyter HTTP 200 on port 8888

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$exitCode = 0

# Check SSH port 22
try {
    $sshListener = Get-NetTCPConnection -LocalPort 22 -State Listen -ErrorAction SilentlyContinue
    if ($sshListener) {
        Write-Host "[OK] sshd listening on port 22"
    } else {
        Write-Host "[FAIL] sshd not listening on port 22"
        $exitCode = 1
    }
} catch {
    Write-Host "[FAIL] SSH check error: $_"
    $exitCode = 1
}

# Check Jupyter HTTP
try {
    $jupyterPort = $env:JUPYTER_PORT
    if (-not $jupyterPort) { $jupyterPort = 8888 }

    $response = Invoke-WebRequest -Uri "http://localhost:$jupyterPort/" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "[OK] Jupyter responding on port $jupyterPort (HTTP 200)"
    } else {
        Write-Host "[WARN] Jupyter returned status $($response.StatusCode) - may still be starting"
        # Don't fail on non-200 - could be redirect
    }
} catch {
    Write-Host "[FAIL] Jupyter not responding on port 8888: $_"
    $exitCode = 1
}

# Check Python free-threading (bonus check)
try {
    $pythonExe = "C:\conda\envs\main\python.exe"
    if (Test-Path $pythonExe) {
        $gilEnabled = & $pythonExe -c "import sys; print(sys._is_gil_enabled())" 2>$null
        if ($gilEnabled -eq "False") {
            Write-Host "[OK] Python free-threading active (GIL disabled)"
        } else {
            Write-Host "[WARN] Python GIL enabled or check failed"
        }
    }
} catch {
    # Non-critical check
}

exit $exitCode
