# CI/CD pipeline check script
# Usage: .\ci-check.ps1

$ErrorActionPreference = "Stop"

# 编码安全设置：强制控制台输出使用UTF-8，兼容PowerShell 5和7
cmd /c chcp 65001 > $null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
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

$totalSteps = 16

# 1. Repo compliance checks (gitignore + vendor + mermaid + filename + roles)
Write-Host "[1/$totalSteps] Repo compliance checks (gitignore+vendor+mermaid+filename+roles)..." -ForegroundColor Yellow
python "$root\.agents\scripts\repo-check.py" all
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: repo compliance check failed" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

# 2. Check links
Write-Host "[2/$totalSteps] Check links..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-links.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: link check failed" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

# 3. Check RACI compliance (A唯一性/R≠A分离/角色列完整性)
Write-Host "[3/$totalSteps] Check RACI compliance in rules/commands..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-raci-compliance.py" --path "$root\.agents\rules"
$raciExit = $LASTEXITCODE
python "$root\.agents\scripts\check-raci-compliance.py" --path "$root\.agents\commands"
$raciExit2 = $LASTEXITCODE
if ($raciExit -ne 0 -or $raciExit2 -ne 0) {
    Write-Host "ERROR: RACI compliance check found errors (double-A, missing-A, or self-approval)" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

# 4. Check hardcode (8类硬编码AST检测)
Write-Host "[4/$totalSteps] Check hardcoded values in Python scripts..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-hardcode.py" --path "$root\.agents\scripts" --threshold 60
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: hardcode check found error-level issues (external URLs, absolute paths, etc.)" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

# 5. Check file size (module-size-bug-correlation 模式门禁，渐进式warn-only)
Write-Host "[5/$totalSteps] Check file size thresholds (module-size-bug-correlation)..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-file-size.py" --warn-only
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARN: file size check found new files exceeding ERROR threshold" -ForegroundColor Yellow
}
Write-Host ""

# 6. Check spec consistency
Write-Host "[6/$totalSteps] Check spec consistency..." -ForegroundColor Yellow
python "$root\.agents\scripts\spec-tool.py" check
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARN: spec consistency check has warnings" -ForegroundColor Yellow
}
Write-Host ""

# 7. Check spec output archive (产出物归档检查, warn-only until historical violations are cleaned)
Write-Host "[7/$totalSteps] Check spec output archive (process vs deliverable separation)..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-spec-output-archive.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARN: some completed specs still have output files not archived to docs/ (non-blocking, historical debt)" -ForegroundColor Yellow
}
Write-Host ""

# 8. Check pattern maturity (CI mode)
Write-Host "[8/$totalSteps] Check pattern maturity..." -ForegroundColor Yellow
python "$root\.agents\scripts\pattern-maturity.py" check
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pattern maturity check failed" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

# 9. Generate docs (nav + dashboard + apps)
Write-Host "[9/$totalSteps] Generate docs (nav+dashboard+apps)..." -ForegroundColor Yellow
python "$root\.agents\scripts\docgen.py" all
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: doc generation failed" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

# 10. Check directory README existence (P1#3 门禁检查, ERROR级)
Write-Host "[10/$totalSteps] Check directory README existence..." -ForegroundColor Yellow
python "$root\.agents\scripts\generate-readme.py" --check
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: missing directory READMEs found (run generate-readme.py --all to fix)" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

# 11. Check Skill quality (五要素模型 + Agent Skills开放标准合规性)
Write-Host "[11/$totalSteps] Check Skill quality (five-elements + open standards compliance)..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-skill-quality.py" --threshold 70
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Skill quality check failed (errors found or average score below threshold)" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

# 12. Check PowerShell pipe safety
Write-Host "[12/$totalSteps] Check PowerShell pipe safety..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-powershell-pipe-safety.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARN: PowerShell pipe safety check failed unexpectedly" -ForegroundColor Yellow
}
Write-Host ""

# 13. Check script duplication
Write-Host "[13/$totalSteps] Check script duplication..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-duplication.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARN: cross-file duplication detected, consider extracting to lib/" -ForegroundColor Yellow
    Write-Host "  Ref: .agents/scripts/lib/README.md" -ForegroundColor Yellow
}
else {
    Write-Host "  PASS" -ForegroundColor Green
}
Write-Host ""

# 14. Stage guardrail log check (strict mode)
Write-Host "[14/$totalSteps] Check stage guardrail logs..." -ForegroundColor Yellow
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

# 15. Generate SG dashboard
Write-Host "[15/$totalSteps] Generate stage guardrail dashboard..." -ForegroundColor Yellow
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

# 16. Version ripple check (模式更新后下游文档版本一致性, 含递归自举验证)
Write-Host "[16/$totalSteps] Check version ripple (bootstrap + doc consistency)..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-version-ripple.py" --root "$root\docs" --bootstrap
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: version ripple check failed (bootstrap or stale references)" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All checks passed" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
