#Requires -Version 5.1
<#
.SYNOPSIS
    Caffe-FFI WSL 一键部署 PowerShell 包装器
.DESCRIPTION
    从 Windows PowerShell/CMD 直接调用，自动通过 wsl.exe 执行 WSL 内的部署脚本。
    无需手动进入 WSL 终端，支持所有 wsl-deploy.sh 参数。
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
.PARAMETER Distribution
    WSL 发行版名称（默认自动检测 Ubuntu）
.PARAMETER Help
    显示帮助
.EXAMPLE
    .\deploy.ps1 -CN
    # 国内用户一键部署
.EXAMPLE
    .\deploy.ps1 -CN -Cleanup
    # 国内用户部署+验证后自动清理
.EXAMPLE
    .\deploy.ps1 -Rebuild -NoCache
    # 强制无缓存重建
.EXAMPLE
    .\deploy.ps1 -LogFormat json
    # JSON 格式输出（供监控平台采集）
.NOTES
    前置条件：
    - WSL2 已安装（Ubuntu 24.04/26.04 推荐）
    - Docker 已在 WSL 中可用（Docker Desktop WSL集成 或 WSL原生docker.io）
    - 首次使用请先在 WSL 中完成 Docker 安装
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
    [string]$Distribution = "",
    [switch]$Help
)

if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Full
    exit 0
}

# ── 颜色输出 ──
function Write-Info { param([string]$Msg) Write-Host "[INFO]  $Msg" -ForegroundColor Green }
function Write-Warn { param([string]$Msg) Write-Host "[WARN]  $Msg" -ForegroundColor Yellow }
function Write-Err  { param([string]$Msg) Write-Host "[ERROR] $Msg" -ForegroundColor Red }
function Write-Ok   { param([string]$Msg) Write-Host "  OK   $Msg" -ForegroundColor Green }
function Write-Step { param([string]$Msg) Write-Host "`n=== $Msg ===" -ForegroundColor Cyan }

# ── 1. 检测 wsl.exe 是否可用 ──
Write-Step "WSL 环境检测"

$wslExe = Get-Command wsl.exe -ErrorAction SilentlyContinue
if (-not $wslExe) {
    Write-Err "wsl.exe 未找到！请先安装 WSL2："
    Write-Err "  以管理员身份运行 PowerShell，执行："
    Write-Err "  wsl --install -d Ubuntu-24.04"
    Write-Err "  安装后重启计算机。"
    exit 1
}
Write-Ok "wsl.exe 可用"

# ── 2. 检测 WSL 发行版 ──
$wslList = wsl.exe --list --verbose 2>&1
if ($LASTEXITCODE -ne 0 -or -not $wslList) {
    Write-Err "WSL 未正确安装或没有可用的发行版。"
    Write-Err "请执行: wsl --install -d Ubuntu-24.04"
    exit 1
}

if (-not $Distribution) {
    # 自动检测 Ubuntu 发行版（优先 24.04/26.04）
    $ubuntuDistros = $wslList | Where-Object { $_ -match 'Ubuntu' -and $_ -match '2\s' } | ForEach-Object {
        if ($_ -match '^\s*(\*?\s*)?(Ubuntu[\w.-]*)\s+') { $matches[2].Trim() }
    }
    if ($ubuntuDistros) {
        $Distribution = $ubuntuDistros[0]
        Write-Info "自动检测到 WSL 发行版: $Distribution"
    } else {
        # 尝试第一个正在运行的发行版
        $firstDistro = ($wslList | Select-String '^\s*\*?\s*(\S+)\s' | Select-Object -First 1)
        if ($firstDistro) {
            $Distribution = $firstDistro.Matches.Groups[1].Value.Trim('*').Trim()
            Write-Warn "未检测到 Ubuntu，使用发行版: $Distribution"
        } else {
            Write-Err "未找到可用的 WSL 发行版"
            exit 1
        }
    }
}
Write-Ok "使用 WSL 发行版: $Distribution"

# ── 3. 转换 Windows 路径到 WSL 路径 ──
Write-Step "路径转换"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$appDir = Split-Path -Parent $scriptDir
$projectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $appDir))

# 转换为 WSL 路径: D:\xxx → /mnt/d/xxx
function Convert-ToWslPath {
    param([string]$WindowsPath)
    $fullPath = [System.IO.Path]::GetFullPath($WindowsPath)
    $drive = $fullPath.Substring(0, 1).ToLower()
    $rest = $fullPath.Substring(2).Replace('\', '/')
    return "/mnt/$drive$rest"
}

$wslScriptDir = Convert-ToWslPath $scriptDir
$wslAppDir = Convert-ToWslPath $appDir
$wslProjectRoot = Convert-ToWslPath $projectRoot

Write-Info "脚本目录(WSL): $wslScriptDir"
Write-Info "项目根目录(WSL): $wslProjectRoot"

# ── 4. 检查 WSL 中 Docker 是否可用 ──
Write-Step "Docker 环境预检测"

$dockerCheck = wsl.exe -d $Distribution bash -c "docker --version 2>/dev/null && echo 'DOCKER_OK' || echo 'DOCKER_MISSING'" 2>&1
if ($dockerCheck -match 'DOCKER_MISSING') {
    Write-Err "WSL ($Distribution) 中 Docker 不可用！"
    Write-Err "请选择以下方案之一安装 Docker："
    Write-Err ""
    Write-Err "方案A - Docker Desktop（推荐新手）："
    Write-Err "  1. 安装 Docker Desktop for Windows"
    Write-Err "  2. Settings > Resources > WSL Integration 启用 $Distribution"
    Write-Err ""
    Write-Err "方案B - WSL 原生 Docker（性能更好）："
    Write-Err "  wsl -d $Distribution"
    Write-Err "  sudo apt update && sudo apt install -y docker.io"
    Write-Err "  sudo systemctl enable docker && sudo systemctl start docker"
    Write-Err "  sudo usermod -aG docker `$USER"
    Write-Err "  # 退出 WSL 后重新运行本脚本"
    exit 1
}
$dockerVer = ($dockerCheck | Select-String 'Docker version [\d.]+').Matches.Value
Write-Ok "Docker 可用: $dockerVer"

# ── 5. 检查 WSL 内 Docker daemon 状态 ──
$daemonCheck = wsl.exe -d $Distribution bash -c "docker info >/dev/null 2>&1 && echo 'DAEMON_OK' || echo 'DAEMON_DOWN'" 2>&1
if ($daemonCheck -match 'DAEMON_DOWN') {
    Write-Err "Docker daemon 未运行！"
    Write-Err "如果使用 Docker Desktop，请启动 Docker Desktop 应用。"
    Write-Err "如果使用原生 Docker，在 WSL 中执行: sudo systemctl start docker"
    exit 1
}
Write-Ok "Docker daemon 运行中"

# ── 6. 构建参数 ──
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

# ── 7. 执行部署 ──
Write-Step "开始执行部署"

$wslBashScript = "$wslScriptDir/wsl-deploy.sh"
$wslCommand = "cd `"$wslAppDir`" && bash scripts/wsl-deploy.sh $($bashArgs -join ' ')"

Write-Info "执行命令: wsl.exe -d $Distribution bash -c `"$wslCommand`""
Write-Host ""

# 使用 wsl.exe 执行，保留实时输出
# 注意：不使用 -e 以确保登录 shell 加载正确的 PATH
$startTime = Get-Date
wsl.exe -d $Distribution --cd "$wslAppDir" bash -c "bash scripts/wsl-deploy.sh $($bashArgs -join ' ')"
$exitCode = $LASTEXITCODE
$endTime = Get-Date
$duration = [math]::Round(($endTime - $startTime).TotalSeconds)

Write-Host ""
if ($exitCode -eq 0) {
    Write-Step "部署成功"
    Write-Ok "总耗时: $duration 秒"
    Write-Host ""
    Write-Host "连接信息：" -ForegroundColor Cyan
    Write-Host "  SSH:     ssh -p $SshPort jupyteruser@localhost  (密码: $Password)"
    Write-Host "  Jupyter: http://localhost:${JupyterPort}/?token=$Token"
} else {
    Write-Step "部署失败"
    Write-Err "退出码: $exitCode"
    Write-Err "耗时: $duration 秒"
    Write-Host ""
    Write-Host "故障排查：" -ForegroundColor Yellow
    Write-Host "  1. 查看容器日志:  wsl -d $Distribution -- docker logs caffe-ffi-jupyter 2>&1 | tail -50"
    Write-Host "  2. 运行诊断脚本:  .\diagnose.ps1"
    Write-Host "  3. 进入容器调试:  wsl -d $Distribution -- docker exec -it caffe-ffi-jupyter bash"
    Write-Host "  4. 查看部署指南:  WSL-DEPLOY-GUIDE.md"
}

exit $exitCode
