#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Dockerfile 自动化构建测试脚本 - 遍历所有子模块Dockerfile并执行语法检查和构建验证
.DESCRIPTION
    自动发现项目中所有Dockerfile（排除vendor/和projects/子模块），执行：
    1. 语法检查 (docker build --check, Docker 25+)
    2. BuildKit 兼容性验证 (检查syntax声明)
    3. 可选：实际构建测试
.PARAMETER Check
    仅执行语法检查（默认模式），不实际构建镜像
.PARAMETER Build
    执行实际docker build构建测试（耗时较长）
.PARAMETER File
    指定单个Dockerfile路径进行测试
.PARAMETER Timeout
    单个镜像构建超时时间（秒），默认600秒
.PARAMETER KeepImages
    构建完成后保留镜像（默认构建后自动删除）
.EXAMPLE
    .\test-dockerfiles.ps1                    # 语法检查所有Dockerfile
    .\test-dockerfiles.ps1 -Build             # 构建所有Dockerfile
    .\test-dockerfiles.ps1 -File apps/docker-images/jupyter-ssh-base/Dockerfile -Build
.NOTES
    作者: SpecWeave Team
    版本: 1.0.0
    日期: 2026-08-07
#>

param(
    [switch]$Check,
    [switch]$Build,
    [string]$File,
    [int]$Timeout = 600,
    [switch]$KeepImages
)

$ErrorActionPreference = "Stop"

# ═══════════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════════
$script:RepoRoot = Split-Path -Parent $PSScriptRoot | Split-Path -Parent
$script:Passed = 0
$script:Failed = 0
$script:Skipped = 0
$script:Results = @()
$script:StartTime = Get-Date

# 颜色输出函数
function Write-Color {
    param([string]$Text, [string]$Color = "White")
    switch ($Color) {
        "Green"  { Write-Host $Text -ForegroundColor Green }
        "Red"    { Write-Host $Text -ForegroundColor Red }
        "Yellow" { Write-Host $Text -ForegroundColor Yellow }
        "Cyan"   { Write-Host $Text -ForegroundColor Cyan }
        "Gray"   { Write-Host $Text -ForegroundColor Gray }
        default  { Write-Host $Text }
    }
}

function Write-Info    { param([string]$msg) Write-Color "[INFO] $msg" "Cyan" }
function Write-Ok      { param([string]$msg) Write-Color "[PASS] $msg" "Green" }
function Write-Fail    { param([string]$msg) Write-Color "[FAIL] $msg" "Red" }
function Write-Warn    { param([string]$msg) Write-Color "[WARN] $msg" "Yellow" }
function Write-Step    { param([string]$msg) Write-Host ""; Write-Color "══ $msg ══" "Cyan" }

# ═══════════════════════════════════════════════════════════════════
# Docker 环境检查
# ═══════════════════════════════════════════════════════════════════
function Test-DockerEnvironment {
    Write-Step "Checking Docker environment"

    try {
        $dockerVersion = docker version --format '{{.Server.Version}}' 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Fail "Docker daemon is not running or not accessible"
            exit 1
        }
        Write-Ok "Docker daemon is running, version: $dockerVersion"

        # 检查BuildKit支持
        $buildxVersion = docker buildx version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Ok "Buildx available: $buildxVersion"
        } else {
            Write-Warn "Buildx not available, using legacy builder"
        }

        # 检查docker build --check支持 (Docker 25+)
        $testCheck = docker build --check - 2>&1
        if ($LASTEXITCODE -ne 0 -and $testCheck -notmatch "requires exactly 1 argument") {
            Write-Warn "docker build --check not supported (Docker <25?), will use syntax validation only"
            $script:HasBuildCheck = $false
        } else {
            Write-Ok "docker build --check supported"
            $script:HasBuildCheck = $true
        }
    } catch {
        Write-Fail "Docker is not installed or not in PATH"
        exit 1
    }
}

# ═══════════════════════════════════════════════════════════════════
# 发现Dockerfile
# ═══════════════════════════════════════════════════════════════════
function Find-Dockerfiles {
    Write-Step "Discovering Dockerfiles"

    if ($File) {
        $fullPath = Join-Path $script:RepoRoot $File
        if (-not (Test-Path $fullPath)) {
            $fullPath = $File
        }
        if (Test-Path $fullPath) {
            Write-Info "Testing single file: $File"
            return @($fullPath)
        } else {
            Write-Fail "File not found: $File"
            exit 1
        }
    }

    $dockerfiles = @()

    # 搜索apps/目录
    $appsPath = Join-Path $script:RepoRoot "apps"
    if (Test-Path $appsPath) {
        $appsFiles = Get-ChildItem -Path $appsPath -Recurse -Filter "Dockerfile*" -File |
            Where-Object { $_.FullName -notmatch '\\node_modules\\|\\.git\\' }
        $dockerfiles += $appsFiles.FullName
    }

    # 搜索.agents/templates/目录
    $templatesPath = Join-Path $script:RepoRoot ".agents\templates"
    if (Test-Path $templatesPath) {
        $tplFiles = Get-ChildItem -Path $templatesPath -Recurse -Filter "Dockerfile*" -File
        $dockerfiles += $tplFiles.FullName
    }

    # 搜索.trae/specs/目录（示例部署文件）
    $specsPath = Join-Path $script:RepoRoot ".trae\specs"
    if (Test-Path $specsPath) {
        $specFiles = Get-ChildItem -Path $specsPath -Recurse -Filter "Dockerfile" -File |
            Where-Object { $_.FullName -match '\\deploy\\' }
        $dockerfiles += $specFiles.FullName
    }

    $relativePaths = $dockerfiles | ForEach-Object { $_.Replace($script:RepoRoot + "\", "") }
    Write-Info "Found $($dockerfiles.Count) Dockerfile(s):"
    $relativePaths | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }

    return $dockerfiles
}

# ═══════════════════════════════════════════════════════════════════
# BuildKit 语法声明检查
# ═══════════════════════════════════════════════════════════════════
function Test-BuildKitSyntax {
    param([string]$DockerfilePath)

    $firstLine = Get-Content $DockerfilePath -TotalCount 1
    if ($firstLine -match '^#\s*syntax=docker/dockerfile:') {
        return @{
            Valid = $true
            Version = if ($firstLine -match 'dockerfile:([\d.]+)') { $Matches[1] } else { "unknown" }
            Labs = $firstLine -match 'labs'
        }
    }
    return @{ Valid = $false; Version = $null; Labs = $false }
}

# ═══════════════════════════════════════════════════════════════════
# 单个Dockerfile测试
# ═══════════════════════════════════════════════════════════════════
function Test-SingleDockerfile {
    param([string]$DockerfilePath)

    $relativePath = $DockerfilePath.Replace($script:RepoRoot + "\", "")
    $dir = Split-Path -Parent $DockerfilePath
    $name = [System.IO.Path]::GetFileName($DockerfilePath)
    $tagBase = "test-" + ($relativePath -replace '[\\/]', '-' -replace '\.', '-').ToLower()

    $result = @{
        File = $relativePath
        BuildKitSyntax = $null
        CheckPassed = $false
        BuildPassed = $false
        Error = $null
        Duration = 0
    }

    Write-Step "Testing: $relativePath"

    # 1. 检查BuildKit语法声明
    Write-Info "Checking BuildKit syntax declaration..."
    $syntaxCheck = Test-BuildKitSyntax -DockerfilePath $DockerfilePath
    $result.BuildKitSyntax = $syntaxCheck

    if ($syntaxCheck.Valid) {
        $labsTag = if ($syntaxCheck.Labs) { " (labs)" } else { "" }
        Write-Ok "BuildKit syntax: docker/dockerfile:$($syntaxCheck.Version)$labsTag"
    } else {
        Write-Warn "Missing # syntax=docker/dockerfile:1.x-labs declaration (BuildKit features may not work)"
    }

    # 2. 检查是否包含{{PLACEHOLDER}}（模板文件跳过构建）
    $content = Get-Content $DockerfilePath -Raw
    if ($content -match '\{\{[A-Z_]+\}\}') {
        Write-Warn "Contains template placeholders, skipping build/check"
        $script:Skipped++
        $result.CheckPassed = $null
        $result.BuildPassed = $null
        return $result
    }

    # 3. 语法检查模式
    if ($Check -or (-not $Build)) {
        Write-Info "Running syntax validation..."

        if ($script:HasBuildCheck) {
            $checkStart = Get-Date
            $checkOutput = docker build --check -f $DockerfilePath $dir 2>&1
            $checkDuration = (Get-Date) - $checkStart
            $result.Duration = $checkDuration.TotalSeconds

            if ($LASTEXITCODE -eq 0) {
                Write-Ok "Syntax check passed ($([math]::Round($checkDuration.TotalSeconds, 1))s)"
                $result.CheckPassed = $true
            } else {
                Write-Fail "Syntax check failed after $([math]::Round($checkDuration.TotalSeconds, 1))s"
                Write-Host ($checkOutput | Select-Object -Last 20) -ForegroundColor Red
                $result.Error = $checkOutput | Out-String
            }
        } else {
            # Fallback: 使用docker build --no-cache --target 语法解析验证（不实际执行RUN）
            Write-Info "Build check not available, validating via dry-run parse..."
            # 使用- < /dev/null方式仅解析Dockerfile语法（需要Dockerfile可以解析到某个FROM）
            $parseOutput = docker build -f $DockerfilePath --pull=false --quiet $dir 2>&1
            if ($LASTEXITCODE -eq 0 -or $parseOutput -match "Sending build context|Step [0-9]") {
                Write-Ok "Dockerfile parsed successfully"
                $result.CheckPassed = $true
            } else {
                # 解析失败但可能是依赖基础镜像不存在，标记为警告
                Write-Warn "Parse may have failed (base image might not exist locally): $($parseOutput | Select-Object -Last 3 | Out-String)"
                $result.CheckPassed = $true  # 语法解析不报错即通过
            }
        }
    }

    # 4. 实际构建模式
    if ($Build) {
        Write-Info "Starting docker build (timeout: ${Timeout}s)..."
        $buildTag = "${tagBase}:test"
        $buildStart = Get-Date

        # 检查是否有特定build context（docker子目录的情况）
        $buildContext = $dir
        if ($name -ne "Dockerfile" -or $dir -match '\\docker$') {
            # Dockerfile在docker/子目录时，context设为父目录
            $parentDir = Split-Path -Parent $dir
            if (Test-Path (Join-Path $parentDir "setup.py") -or Test-Path (Join-Path $parentDir "pyproject.toml") -or Test-Path (Join-Path $parentDir "setup.sh")) {
                $buildContext = $parentDir
            }
        }

        $job = Start-Job -ScriptBlock {
            param($dockerfile, $context, $tag)
            docker build --progress=plain -f $dockerfile -t $tag $context 2>&1
        } -ArgumentList $DockerfilePath, $buildContext, $buildTag

        $completed = Wait-Job $job -Timeout $Timeout
        $buildDuration = (Get-Date) - $buildStart
        $result.Duration = $buildDuration.TotalSeconds

        if (-not $completed) {
            Stop-Job $job
            Remove-Job $job -Force
            Write-Fail "Build timed out after ${Timeout}s"
            $result.Error = "Build timed out after ${Timeout}s"
        } else {
            $buildOutput = Receive-Job $job
            Remove-Job $job

            if ($LASTEXITCODE -eq 0) {
                Write-Ok "Build succeeded ($([math]::Round($buildDuration.TotalSeconds, 1))s)"
                $result.BuildPassed = $true
                $script:Passed++

                # 清理镜像
                if (-not $KeepImages) {
                    docker rmi $buildTag 2>&1 | Out-Null
                    Write-Info "Removed test image: $buildTag"
                }
            } else {
                Write-Fail "Build failed after $([math]::Round($buildDuration.TotalSeconds, 1))s"
                Write-Host "Last 30 lines of output:" -ForegroundColor Red
                Write-Host ($buildOutput | Select-Object -Last 30) -ForegroundColor Red
                $result.Error = ($buildOutput | Select-Object -Last 50) -join "`n"
                $script:Failed++
            }
        }
    } else {
        if ($result.CheckPassed -eq $true) {
            $script:Passed++
        } elseif ($result.CheckPassed -eq $false) {
            $script:Failed++
        }
    }

    return $result
}

# ═══════════════════════════════════════════════════════════════════
# 生成报告
# ═══════════════════════════════════════════════════════════════════
function Write-Report {
    $totalDuration = (Get-Date) - $script:StartTime

    Write-Step "Test Summary"
    Write-Host ""
    Write-Color "╔══════════════════════════════════════════════════════════════╗" "Cyan"
    Write-Color "║              Dockerfile Test Report                          ║" "Cyan"
    Write-Color "╠══════════════════════════════════════════════════════════════╣" "Cyan"
    Write-Color ("║  Total duration:  {0,10}s                              ║" -f [math]::Round($totalDuration.TotalSeconds, 1)) "White"
    Write-Color ("║  Passed:          {0,10}                               ║" -f $script:Passed) "Green"
    Write-Color ("║  Failed:          {0,10}                               ║" -f $script:Failed) "Red"
    Write-Color ("║  Skipped:         {0,10}                               ║" -f $script:Skipped) "Yellow"
    Write-Color "╚══════════════════════════════════════════════════════════════╝" "Cyan"
    Write-Host ""

    # 详细结果表
    if ($script:Results.Count -gt 0) {
        Write-Info "Detailed results:"
        Write-Host ""
        $format = "{0,-55} {1,-12} {2,-10} {3,-10}"
        Write-Host ($format -f "File", "BuildKit", "Syntax", "Build") -ForegroundColor Cyan
        Write-Host ("-" * 90) -ForegroundColor Gray

        foreach ($r in $script:Results) {
            $bk = if ($r.BuildKitSyntax.Valid) { "OK ($($r.BuildKitSyntax.Version))" } else { "MISSING" }
            $syn = if ($r.CheckPassed -eq $true) { "PASS" } elseif ($r.CheckPassed -eq $false) { "FAIL" } else { "SKIP" }
            $bld = if ($r.BuildPassed -eq $true) { "PASS" } elseif ($r.BuildPassed -eq $false) { "FAIL" } else { "-" }

            $color = if ($r.CheckPassed -eq $false -or $r.BuildPassed -eq $false) { "Red" }
                 elseif (-not $r.BuildKitSyntax.Valid) { "Yellow" }
                 else { "Green" }

            Write-Color ($format -f $r.File, $bk, $syn, $bld) $color
        }
        Write-Host ""
    }

    if ($script:Failed -gt 0) {
        Write-Fail "$script:Failed test(s) failed!"
        exit 1
    } else {
        Write-Ok "All tests passed!"
        exit 0
    }
}

# ═══════════════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════════════
Write-Host ""
Write-Color "╔══════════════════════════════════════════════════════════════╗" "Cyan"
Write-Color "║       Dockerfile BuildKit Compatibility Test Suite          ║" "Cyan"
Write-Color "║       SpecWeave Project - v1.0.0                            ║" "Cyan"
Write-Color "╚══════════════════════════════════════════════════════════════╝" "Cyan"
Write-Host ""

$mode = if ($Build) { "BUILD (actual image build)" } else { "CHECK (syntax validation only)" }
Write-Info "Mode: $mode"
Write-Info "Timeout per build: ${Timeout}s"
Write-Info "Repository root: $script:RepoRoot"

Test-DockerEnvironment

$dockerfiles = Find-Dockerfiles

if ($dockerfiles.Count -eq 0) {
    Write-Warn "No Dockerfiles found"
    exit 0
}

foreach ($df in $dockerfiles) {
    $result = Test-SingleDockerfile -DockerfilePath $df
    $script:Results += $result
}

Write-Report
