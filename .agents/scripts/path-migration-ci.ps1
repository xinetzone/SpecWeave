<#
.SYNOPSIS
    路径迁移CI检查脚本 - 在CI环境中自动检测旧路径残留或执行路径迁移
.DESCRIPTION
    基于 path-migration-template.py 的四层日志模式，提供CI环境友好的封装。
    默认只扫描不修改（安全模式，PR门禁用）。
    发现旧路径残留时返回非0退出码阻断CI。
.PARAMETER OldPath
    要迁移的旧路径（必须指定）
.PARAMETER NewPath
    目标新路径（必须指定）
.PARAMETER MigrationName
    迁移名称，用于提交信息（默认自动生成）
.PARAMETER ScanOnly
    只扫描不修改（默认模式）
.PARAMETER DryRun
    试运行模式
.PARAMETER Execute
    实际执行迁移
.PARAMETER AutoCommit
    执行迁移后自动原子提交
.PARAMETER Threshold
    允许的残留引用数上限（默认0，仅ScanOnly模式有效）
.EXAMPLE
    .\path-migration-ci.ps1 -OldPath "old/path" -NewPath "new/path"
.EXAMPLE
    .\path-migration-ci.ps1 -OldPath "old/path" -NewPath "new/path" -Execute -AutoCommit
#>

# ==============================================================================
# Parameters (must be first executable statement after comment-based help)
# ==============================================================================
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$OldPath,

    [Parameter(Mandatory = $true, Position = 1)]
    [string]$NewPath,

    [string]$MigrationName,

    [switch]$ScanOnly,

    [switch]$DryRun,

    [switch]$Execute,

    [switch]$AutoCommit,

    [int]$Threshold = 0
)

$ErrorActionPreference = "Stop"

# ==============================================================================
# Encoding Safety
# ==============================================================================
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSDefaultParameterValues['*:Encoding'] = 'utf8'
}

# ==============================================================================
# Path Configuration
# ==============================================================================
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$agentsDir = Split-Path -Parent $scriptDir
$root = Split-Path -Parent $agentsDir
$templateScript = Join-Path $agentsDir "scripts\templates\path-migration-template.py"
$tempScript = Join-Path ([System.IO.Path]::GetTempPath()) "path-migration-ci-temp.py"

# ==============================================================================
# Color helpers
# ==============================================================================
function Write-Step { Write-Host $args[0] -ForegroundColor Yellow }
function Write-Pass { Write-Host $args[0] -ForegroundColor Green }
function Write-Fail { Write-Host $args[0] -ForegroundColor Red }
function Write-Info { Write-Host $args[0] -ForegroundColor Cyan }
function Write-Detail { Write-Host $args[0] -ForegroundColor Gray }
function Write-Warn { Write-Host $args[0] -ForegroundColor DarkYellow }

# ==============================================================================
# Default: ScanOnly if no other mode specified
# ==============================================================================
if (-not $DryRun -and -not $Execute) { $ScanOnly = $true }

# ==============================================================================
# Validate required params
# ==============================================================================
if (-not $OldPath) { Write-Fail "ERROR: -OldPath is required"; exit 2 }
if (-not $NewPath) { Write-Fail "ERROR: -NewPath is required"; exit 2 }

if (-not $MigrationName) {
    $MigrationName = "path-migration-" + (Get-Date -Format "yyyyMMddHHmmss")
}

# ==============================================================================
# Header
# ==============================================================================
$totalSteps = 5
Write-Info "========================================"
Write-Info "  Path Migration CI Check"
Write-Info "========================================"
Write-Detail "Old path:     $OldPath"
Write-Detail "New path:     $NewPath"
Write-Detail "Migration:    $MigrationName"
$modeDisplay = if ($ScanOnly) { "SCAN-ONLY (gate)" } elseif ($DryRun) { "DRY-RUN" } else { "EXECUTE" }
Write-Detail "Mode:         $modeDisplay"
Write-Detail "Threshold:    $Threshold"
Write-Detail "Project root: $root"
Write-Host ""

# ==============================================================================
# [1/5] Environment Check
# ==============================================================================
Write-Step "[1/$totalSteps] Environment check..."

$pythonCmd = $null
try {
    $v = python --version 2>&1
    if ($LASTEXITCODE -eq 0) { $pythonCmd = "python" }
}
catch {
    try {
        $v = python3 --version 2>&1
        if ($LASTEXITCODE -eq 0) { $pythonCmd = "python3" }
    }
    catch {}
}
if (-not $pythonCmd) { Write-Fail "  FAIL: Python not found"; exit 2 }
Write-Detail "  Python: $v"

if (-not (Test-Path $templateScript)) { Write-Fail "  FAIL: Template not found: $templateScript"; exit 2 }
if (-not (Test-Path (Join-Path $root "AGENTS.md"))) { Write-Fail "  FAIL: Project root invalid: $root"; exit 2 }
Write-Pass "  PASS"

# ==============================================================================
# [2/5] Prepare migration script (inject config)
# ==============================================================================
Write-Step "[2/$totalSteps] Prepare migration script..."

try {
    $templateContent = Get-Content $templateScript -Raw -Encoding UTF8
    $injected = $templateContent -replace '^OLD_PATH\s*=\s*".*?"', "OLD_PATH = ""$OldPath""" `
                                 -replace '^NEW_PATH\s*=\s*".*?"', "NEW_PATH = ""$NewPath""" `
                                 -replace '^MIGRATION_NAME\s*=\s*".*?"', "MIGRATION_NAME = ""$MigrationName"""
    [System.IO.File]::WriteAllText($tempScript, $injected, [System.Text.Encoding]::UTF8)
    Write-Detail "  Config injected into: $tempScript"
}
catch {
    Write-Fail "  FAIL: $($_.Exception.Message)"; exit 2
}
Write-Pass "  PASS"

# ==============================================================================
# [3/5] Execute scan / migration
# ==============================================================================
if ($ScanOnly) {
    Write-Step "[3/$totalSteps] Execute scan (scan-only)..."
    $scanArgs = "--scan-only"
}
elseif ($DryRun) {
    Write-Step "[3/$totalSteps] Execute scan (dry-run)..."
    $scanArgs = "--dry-run"
}
else {
    Write-Step "[3/$totalSteps] Execute migration..."
    $scanArgs = @()
    if (-not $AutoCommit) { $scanArgs += "--no-commit" }
}

$scanStart = Get-Date
$scanOutput = & $pythonCmd $tempScript $scanArgs 2>&1
$scanExitCode = $LASTEXITCODE
$scanDuration = [math]::Round(((Get-Date) - $scanStart).TotalSeconds, 2)

Write-Detail "  Duration: ${scanDuration}s"
Write-Detail "  Exit code: $scanExitCode"

# ==============================================================================
# [4/5] Parse results
# ==============================================================================
Write-Step "[4/$totalSteps] Parse results..."

$matchedFiles = 0; $matchedRefs = 0; $scanSuccess = $true

if ($scanOutput -match '去重后唯一文件:\s*(\d+)') { $matchedFiles = [int]$Matches[1] }
if ($scanOutput -match '匹配引用总数:\s*(\d+)') { $matchedRefs = [int]$Matches[1] }
if ($scanOutput -match '迁移完成|扫描完成') { $scanSuccess = $true }
elseif ($scanExitCode -ne 0) { $scanSuccess = $false }

Write-Info "  Matched files: $matchedFiles"
Write-Info "  Matched refs: $matchedRefs"

# ==============================================================================
# [5/5] Gate decision
# ==============================================================================
Write-Step "[5/$totalSteps] Gate decision..."

if ($ScanOnly) {
    if ($matchedFiles -gt $Threshold) {
        Write-Fail "  FAIL: $matchedFiles files with residual refs (threshold: $Threshold)"
        Write-Detail "  To preview: .\path-migration-ci.ps1 -OldPath '$OldPath' -NewPath '$NewPath' -DryRun"
        Write-Detail "  To execute: .\path-migration-ci.ps1 -OldPath '$OldPath' -NewPath '$NewPath' -Execute -AutoCommit"
        exit 1
    }
    else {
        Write-Pass "  PASS: No residual refs (threshold: $Threshold)"
    }
}
elseif ($DryRun) {
    if ($scanSuccess) { Write-Pass "  DRY-RUN: Would modify $matchedFiles files" }
    else { Write-Fail "  DRY-RUN failed (exit: $scanExitCode)" }
}
else {
    if ($scanSuccess) { Write-Pass "  Migration executed successfully" }
    else { Write-Fail "  Migration failed (exit: $scanExitCode)"; exit 1 }
}

# ==============================================================================
# Summary
# ==============================================================================
Write-Host ""
Write-Info "========================================"
Write-Info "  Summary"
Write-Info "========================================"
Write-Detail "Mode:              $modeDisplay"
Write-Detail "Matched files:     $matchedFiles"
Write-Detail "Matched refs:      $matchedRefs"
Write-Detail "Duration:          ${scanDuration}s"
Write-Detail "Result:            $(if ($scanSuccess) { 'PASS' } else { 'FAIL' })"

# Cleanup
try { Remove-Item $tempScript -Force -ErrorAction SilentlyContinue } catch {}
exit 0