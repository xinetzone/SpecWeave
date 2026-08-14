#Requires -Version 7.0
<#
.SYNOPSIS
    Caffe-FFI WSL 一键部署 PowerShell 包装器
.DESCRIPTION
    从 Windows PowerShell/CMD 直接调用，自动通过 wsl.exe 执行 WSL 内的部署脚本。
    支持 text/json 双格式日志输出，与 bash 脚本统一的结构化日志契约。
.PARAMETER CN
    使用国内镜像源（apt: aliyun, pip: aliyun, conda: tuna）
.PARAMETER NoCache
    构建时禁用 Docker 缓存
.PARAMETER SkipBase
    跳过基础镜像(jupyter-ssh-base)检查/构建
.PARAMETER SkipRun
    仅构建，不启动容器和运行时验证
.PARAMETER Rebuild
    先清理旧容器和镜像再重建
.PARAMETER Cleanup
    验证完成后自动清理容器
.PARAMETER Tag
    镜像标签（默认: latest）
.PARAMETER SshPort
    SSH 端口映射（默认: 2222）
.PARAMETER JupyterPort
    Jupyter 端口映射（默认: 8888）
.PARAMETER Password
    SSH 密码（默认: deploy-test）
.PARAMETER Token
    Jupyter Token（默认: deploy-token）
.PARAMETER Verbose
    详细输出
.PARAMETER LogFormat
    日志格式: text (默认) | json
.PARAMETER LogLevel
    日志级别: DEBUG|INFO|WARN|ERROR
.PARAMETER LogJson
    JSON 同时输出到 stdout
.PARAMETER LogJsonOutput
    JSON 日志输出文件路径（默认: $env:TEMP\caffe-ffi-events.jsonl）
.PARAMETER Distribution
    WSL 发行版名称（默认自动检测 Ubuntu）
.PARAMETER Help
    显示帮助
.EXAMPLE
    .\deploy.ps1 -CN
    # 国内用户一键部署
.EXAMPLE
    .\deploy.ps1 -CN -LogFormat json -LogJson
    # JSON 格式输出（供监控平台采集）
#>

[CmdletBinding()]
param(
    [switch]$CN,
    [switch]$NoCache,
    [switch]$SkipBase,
    [switch]$SkipRun,
    [switch]$Rebuild,
    [switch]$Cleanup,
    [string]$Tag = "latest",
    [int]$SshPort = 2222,
    [int]$JupyterPort = 8888,
    [string]$Password = "deploy-test",
    [string]$Token = "deploy-token",
    [ValidateSet("text", "json")]
    [string]$LogFormat = "text",
    [ValidateSet("DEBUG", "INFO", "WARN", "ERROR")]
    [string]$LogLevel = "INFO",
    [switch]$LogJson,
    [string]$LogJsonOutput = "",
    [string]$Distribution = "",
    [switch]$Help
)

# ── 加载共享库（common.ps1 自动加载 pwsh7-version-check 和 logging） ──
. "$PSScriptRoot/lib/common.ps1"

# ── 版本校验 ──
if ($MyInvocation.InvocationName -ne '.') {
    if (-not (Test-Pwsh7Version)) { Show-Pwsh7VersionError }
}

if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Full
    exit 0
}

# ── 日志配置 ──
$LogService = "caffe-ffi-deploy-ps"
if (-not $LogJsonOutput) {
    $LogJsonOutput = Join-Path $env:TEMP "caffe-ffi-events.jsonl"
}
$LogJson = $LogJson.IsPresent
$LogFields = @{}

# ── 启动事件 ──
$deployStart = Get-Date
$LogFields["container"] = "caffe-ffi-jupyter"
$LogFields["image_tag"] = $Tag
$LogFields["ssh_port"] = "$SshPort"
$LogFields["jupyter_port"] = "$JupyterPort"
Log-Event -Event "ps_deploy_start" -Fields @{
    cn_mirrors = "$($CN.IsPresent)"
    no_cache = "$($NoCache.IsPresent)"
    log_format = $LogFormat
}

# ── 1. 检测 wsl.exe ──
Log-Step "WSL 环境检测"

$wslExe = Get-Command wsl.exe -ErrorAction SilentlyContinue
if (-not $wslExe) {
    Log-Error "wsl.exe 未找到！请先安装 WSL2：wsl --install -d Ubuntu-24.04"
    Log-Event -Event "ps_deploy_error" -Fields @{ phase="precheck"; error="wsl_not_found" }
    exit 1
}
Log-Ok "wsl.exe 可用"

# ── 2. 检测 WSL 发行版 ──
# wsl.exe 输出 UTF-16 LE，需清理 NUL 字符和空行
$wslListRaw = wsl.exe --list --verbose 2>&1
$wslList = @($wslListRaw | ForEach-Object { ($_ -replace "`0", "").Trim() } | Where-Object { $_ -and $_ -notmatch '^NAME\s+STATE' })
if ($LASTEXITCODE -ne 0 -or -not $wslList) {
    Log-Error "WSL 未正确安装或没有可用的发行版。请执行: wsl --install -d Ubuntu-24.04"
    Log-Event -Event "ps_deploy_error" -Fields @{ phase="precheck"; error="no_distro" }
    exit 1
}

if (-not $Distribution) {
    $ubuntuDistros = $wslList | Where-Object { $_ -match 'Ubuntu' } | ForEach-Object {
        $cleaned = $_ -replace '^\*?\s*', ''
        if ($cleaned -match '^([^\s]+)') { $matches[1] }
    }
    if ($ubuntuDistros.Count -gt 0) {
        $Distribution = $ubuntuDistros[0]
        Log-Info "自动检测到 WSL 发行版: $Distribution"
    } else {
        $firstLine = $wslList | Select-Object -First 1
        if ($firstLine) {
            $Distribution = ($firstLine -replace '^\*?\s*', '') -split '\s+' | Select-Object -First 1
            Log-Warn "未检测到 Ubuntu，使用发行版: $Distribution"
        } else {
            Log-Error "未找到可用的 WSL 发行版"
            Log-Event -Event "ps_deploy_error" -Fields @{ phase="precheck"; error="distro_not_found" }
            exit 1
        }
    }
}
$LogFields["distribution"] = $Distribution
Log-Ok "使用 WSL 发行版: $Distribution"

# ── 3. 路径转换 ──
Log-Step "路径转换"

$scriptDir = Get-ScriptDirectory
$appDir = Split-Path -Parent $scriptDir
$wslAppDir = Convert-WindowsPathToWsl $appDir
Log-Info "WSL 工作目录: $wslAppDir"

# ── 4. Docker 预检测 ──
Log-Step "Docker 环境预检测"

$dockerCheck = wsl.exe -d $Distribution bash -c "docker --version 2>/dev/null && echo 'DOCKER_OK' || echo 'DOCKER_MISSING'" 2>&1
if ($dockerCheck -match 'DOCKER_MISSING') {
    Log-Error "WSL ($Distribution) 中 Docker 不可用！请安装 Docker Desktop 或原生 Docker。"
    Log-Event -Event "ps_deploy_error" -Fields @{ phase="precheck"; error="docker_missing" }
    exit 1
}
$dockerVer = ($dockerCheck | Select-String 'Docker version [\d.]+').Matches.Value
Log-Ok "Docker 可用: $dockerVer"

$daemonCheck = wsl.exe -d $Distribution bash -c "docker info >/dev/null 2>&1 && echo 'DAEMON_OK' || echo 'DAEMON_DOWN'" 2>&1
if ($daemonCheck -match 'DAEMON_DOWN') {
    Log-Error "Docker daemon 未运行！请启动 Docker Desktop 或执行 sudo systemctl start docker"
    Log-Event -Event "ps_deploy_error" -Fields @{ phase="precheck"; error="docker_daemon_down" }
    exit 1
}
Log-Ok "Docker daemon 运行中"

# ── 5. 构建参数 ──
$bashArgs = @()
if ($CN) { $bashArgs += "--cn" }
if ($NoCache) { $bashArgs += "--no-cache" }
if ($SkipBase) { $bashArgs += "--skip-base" }
if ($SkipRun) { $bashArgs += "--skip-run" }
if ($Rebuild) { $bashArgs += "--rebuild" }
if ($Cleanup) { $bashArgs += "--cleanup" }
if ($Tag -ne "latest") { $bashArgs += "--tag"; $bashArgs += $Tag }
if ($SshPort -ne 2222) { $bashArgs += "--ssh-port"; $bashArgs += "$SshPort" }
if ($JupyterPort -ne 8888) { $bashArgs += "--jupyter-port"; $bashArgs += "$JupyterPort" }
if ($Password -ne "deploy-test") { $bashArgs += "--password"; $bashArgs += $Password }
if ($Token -ne "deploy-token") { $bashArgs += "--token"; $bashArgs += $Token }
if ($VerbosePreference -eq 'Continue' -or $PSBoundParameters['Verbose']) { $bashArgs += "--verbose" }
if ($LogFormat -ne "text") { $bashArgs += "--log-format=$LogFormat" }
if ($LogLevel -ne "INFO") { $bashArgs += "--log-level=$LogLevel" }
if ($LogJson) { $bashArgs += "--log-json" }

# ── 6. 执行部署 ──
Log-Step "开始执行部署"
Log-Info "调用 WSL: bash scripts/wsl-deploy.sh $($bashArgs -join ' ')"
if ($LogFormat -eq "text" -or $LogJson) { Write-Host "" }

$startTime = Get-Date
wsl.exe -d $Distribution --cd "$wslAppDir" bash -c "bash scripts/wsl-deploy.sh $($bashArgs -join ' ')"
$exitCode = $LASTEXITCODE
$duration = [math]::Round(((Get-Date) - $startTime).TotalSeconds)

Log-Metric -Name "ps_deploy_duration_seconds" -Value $duration -Unit "seconds"

if ($LogFormat -eq "text" -or $LogJson) { Write-Host "" }

if ($exitCode -eq 0) {
    Log-Step "部署成功"
    Log-Ok "总耗时: $duration 秒"
    Log-Event -Event "ps_deploy_complete" -Fields @{ status="success"; duration="$duration"; exit_code=0 }
    Log-Metric -Name "ps_deploy_exit_code" -Value 0
    if ($LogFormat -eq "text" -or $LogJson) {
        Write-Host ""
        Write-Host "连接信息：" -ForegroundColor Cyan
        Write-Host "  SSH:     ssh -p $SshPort jupyteruser@localhost  (密码: $Password)"
        Write-Host "  Jupyter: http://localhost:${JupyterPort}/?token=$Token"
        Write-Host ""
        Write-Host "JSON 事件日志: $LogJsonOutput" -ForegroundColor Gray
    }
} else {
    Log-Step "部署失败"
    Log-Error "退出码: $exitCode"
    Log-Error "耗时: $duration 秒"
    Log-Event -Event "ps_deploy_complete" -Fields @{ status="failed"; duration="$duration"; exit_code=$exitCode }
    Log-Metric -Name "ps_deploy_exit_code" -Value $exitCode
    if ($LogFormat -eq "text" -or $LogJson) {
        Write-Host ""
        Write-Host "故障排查：" -ForegroundColor Yellow
        Write-Host "  1. 查看容器日志:  wsl -d $Distribution -- docker logs caffe-ffi-jupyter 2>&1 | tail -50"
        Write-Host "  2. 运行诊断脚本:  .\diagnose.ps1"
        Write-Host "  3. 进入容器调试:  wsl -d $Distribution -- docker exec -it caffe-ffi-jupyter bash"
        Write-Host "  4. 查看部署指南:  WSL-DEPLOY-GUIDE.md"
        Write-Host ""
        Write-Host "JSON 事件日志: $LogJsonOutput" -ForegroundColor Gray
    }
}

exit $exitCode
