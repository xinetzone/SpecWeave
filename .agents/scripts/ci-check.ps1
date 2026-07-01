# CI/CD pipeline check script
# Usage: .\ci-check.ps1

$ErrorActionPreference = "Stop"

# 编码安全设置：强制控制台输出使用UTF-8，兼容PowerShell 5和7
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSDefaultParameterValues['*:Encoding'] = 'utf8'
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$agentsDir = Split-Path -Parent $scriptDir
$root = Split-Path -Parent $agentsDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CI/CD Pipeline Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PowerShell version: $($PSVersionTable.PSVersion)" -ForegroundColor Gray
Write-Host "Console encoding: $([Console]::OutputEncoding.WebName)" -ForegroundColor Gray
Write-Host ""

# 1. Repo compliance checks (gitignore + vendor + mermaid + filename + roles)
Write-Host "[1/8] Repo compliance checks (gitignore+vendor+mermaid+filename+roles)..." -ForegroundColor Yellow
python "$root\.agents\scripts\repo-check.py" all
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: repo compliance check failed" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

# 2. Check links
Write-Host "[2/8] Check links..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-links.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: link check failed" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

# 3. Check spec consistency
Write-Host "[3/8] Check spec consistency..." -ForegroundColor Yellow
python "$root\.agents\scripts\spec-tool.py" check
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARN: spec consistency check has warnings" -ForegroundColor Yellow
}
Write-Host ""

# 4. Check pattern maturity (CI mode)
Write-Host "[4/8] Check pattern maturity..." -ForegroundColor Yellow
python "$root\.agents\scripts\pattern-maturity.py" check
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pattern maturity check failed" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

# 5. Generate docs (nav + dashboard + apps)
Write-Host "[5/8] Generate docs (nav+dashboard+apps)..." -ForegroundColor Yellow
python "$root\.agents\scripts\docgen.py" all
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: doc generation failed" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

# 6. Check script duplication
Write-Host "[6/9] Check PowerShell pipe safety..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-powershell-pipe-safety.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARN: PowerShell pipe safety check failed unexpectedly" -ForegroundColor Yellow
}
Write-Host ""

# 7. Check script duplication
Write-Host "[7/9] Check script duplication..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-duplication.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARN: cross-file duplication detected, consider extracting to lib/" -ForegroundColor Yellow
    Write-Host "  Ref: .agents/scripts/lib/README.md" -ForegroundColor Yellow
}
else {
    Write-Host "  PASS" -ForegroundColor Green
}
Write-Host ""

# 8. Stage guardrail log check (strict mode)
Write-Host "[8/9] Check stage guardrail logs..." -ForegroundColor Yellow
$sgLogFile = $env:STAGE_GUARDRAIL_LOG
if (-not $sgLogFile) {
    $logsDir = Join-Path $root ".agents\logs"
    if (Test-Path $logsDir) {
        $latestLog = Get-ChildItem -Path $logsDir -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($latestLog) {
            $sgLogFile = $latestLog.FullName
        }
    }
}
if ($sgLogFile -and (Test-Path $sgLogFile)) {
    python "$root\.agents\scripts\check-stage-guardrails.py" --log-file $sgLogFile --strict
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: stage guardrail log violations found (strict mode)" -ForegroundColor Red
        exit 1
    }
    Write-Host "  PASS" -ForegroundColor Green
}
else {
    Write-Host "  SKIP (no log file found, set STAGE_GUARDRAIL_LOG env var)" -ForegroundColor DarkGray
}
Write-Host ""

# 9. Generate SG dashboard
Write-Host "[9/9] Generate stage guardrail dashboard..." -ForegroundColor Yellow
$logsDir = Join-Path $root ".agents\logs"
if (Test-Path $logsDir) {
    $logFiles = Get-ChildItem -Path $logsDir -Filter "*.log" -ErrorAction SilentlyContinue
    if ($logFiles -and $logFiles.Count -gt 0) {
        python "$root\.agents\scripts\generate-sg-dashboard.py"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "WARN: SG dashboard generation failed (non-blocking)" -ForegroundColor Yellow
        }
        else {
            Write-Host "  PASS (dashboard: .agents/reports/sg-dashboard.html)" -ForegroundColor Green
        }
    }
    else {
        Write-Host "  SKIP (no log files in .agents/logs/)" -ForegroundColor DarkGray
    }
}
else {
    Write-Host "  SKIP (logs directory does not exist)" -ForegroundColor DarkGray
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All checks passed" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
