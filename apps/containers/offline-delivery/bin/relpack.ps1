#!/usr/bin/env pwsh
#Requires -Version 7.0
# ==============================================================================
# relpack.ps1 — offline-delivery 厂商侧交付流水线 CLI（Windows 原生，pwsh 7.4+）
#
# 容器命令统一经 wsl.exe 桥接到 bash 版 bin/relpack（不做逻辑分叉）：
#   wsl.exe -d <发行版> -- bash <WSL 路径>/bin/relpack <参数...>
# 发行版优先级：OFFLINE_DELIVERY_WSL_DISTRO → XMNN_WSL_DISTRO → COMPOSE_WSL_DISTRO
#               → podman-machine-default（wsl.exe -l -v 查看）
# 本脚本只做：参数校验 + 桥接 + help；载荷暂存/依赖集/构建/打包/冒烟逻辑全在 bash 版。
# 参数: -Product <名>（默认 xmnn-runtime）/ -Version <版本> / -Wheel <PATH>
#       / -Torch cpu|cu130 / -BaseImage <REF> / -PipMirror official|tuna|aliyun
#       / -NoCache / -Deps（等价于 deps 子命令）/ -Write（deps 的 --write）
# 覆盖优先级: CLI 旗标 > 环境变量（BASE_IMAGE / PIP_MIRROR / TORCH_FLAVOR）> product.env
# 规范: .agents/rules/delivery-pipeline.md   快速开始: docs/01-quickstart.md
# ==============================================================================
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$BinDir = $PSScriptRoot
$Commands = @('version', 'stage', 'deps', 'build', 'pack', 'smoke')
$OptionKeys = @('p', 'product', 'version', 'wheel', 'torch', 'base-image', 'pip-mirror',
                'no-cache', 'deps', 'write')
$Flavors = @('cpu', 'cu130')
$Mirrors = @('official', 'tuna', 'aliyun')
$Allow = @{
    version = @(); stage = @('wheel'); deps = @('write'); pack = @('version'); smoke = @('version')
    build   = @('torch', 'base-image', 'pip-mirror', 'no-cache')
}

# 与 bash 版 `bin/relpack --help` 文案一致（同一头部注释块）
$UsageText = @'
# relpack — offline-delivery 厂商侧交付流水线 CLI（bash 4+；WSL / Linux / macOS）
#
# 用法: bin/relpack [-p|--product <产品名>] <命令> [选项]
#   -p, --product <名>  产品名（默认 xmnn-runtime；须存在 products/<名>/product.env）
#   -h, --help          显示本帮助
# 命令:
#   version                                        打印产品名/形态/底座镜像 ref 与 Id/载荷/归档名
#   stage   [--wheel PATH]                         暂存载荷 wheel 到 products/<产品>/release/payload/
#                                                  （随交付包发出，不进镜像构建上下文；只留一个）
#   deps    [--write]                              校验/重写 products/<产品>/deps.txt（载荷依赖集）
#   build   [--torch cpu|cu130] [--base-image REF] 构建底座镜像 <镜像名>:base-<形态>（不含载荷）
#           [--pip-mirror official|tuna|aliyun] [--no-cache]
#   pack    [--version V]                          导出 artifacts/<镜像名>-base-<形态>.tar.gz + release.json
#   smoke   [--version V]                          以交付骨架为唯一入口：load → up → smoke → down
# 覆盖优先级: CLI 旗标 > 环境变量（BASE_IMAGE / PIP_MIRROR / TORCH_FLAVOR）> product.env
# 规范: .agents/rules/delivery-pipeline.md  快速开始: docs/01-quickstart.md
# ==============================================================================
# Windows 原生参数名: -Product -Version -Wheel -Torch -BaseImage -PipMirror -NoCache -Deps -Write
'@

function Fail([string]$Message) { Write-Host "[ERR ] $Message" -ForegroundColor Red; exit 1 }

function Show-Usage { Write-Host $UsageText }

function Get-WslDistro {
    foreach ($key in @('OFFLINE_DELIVERY_WSL_DISTRO', 'XMNN_WSL_DISTRO', 'COMPOSE_WSL_DISTRO')) {
        $value = [Environment]::GetEnvironmentVariable($key)
        if (-not [string]::IsNullOrWhiteSpace($value)) { return $value }
    }
    return 'podman-machine-default'
}

function ConvertTo-WslPath([string]$WindowsPath) {
    $full = [System.IO.Path]::GetFullPath($WindowsPath)
    if ($full -notmatch '^[A-Za-z]:') { return $full }
    $drive = $full.Substring(0, 1).ToLowerInvariant()
    return "/mnt/$drive" + $full.Substring(2).Replace('\', '/')
}

# —— 参数解析与宿主侧校验（语义与 bash 版一致） ——
$command = ''; $product = ''; $version = ''; $wheel = ''
$torch = ''; $baseImage = ''; $pipMirror = ''; $noCache = $false
$depsSwitch = $false; $write = $false
for ($i = 0; $i -lt $args.Count; $i++) {
    $raw = [string]$args[$i]
    if (-not $raw.StartsWith('-')) {
        $candidate = $raw.ToLowerInvariant()
        if ($candidate -notin $Commands) { Fail "未知命令：$raw（支持 $($Commands -join '/')；-h 查看用法）" }
        $command = $candidate
        continue
    }
    $key = $raw.TrimStart('-'); $val = ''
    if ($key.Contains('=')) { $parts = $key.Split('=', 2); $key = $parts[0]; $val = $parts[1] }
    $key = $key.ToLowerInvariant()
    if ($key -in @('h', 'help')) { Show-Usage; exit 0 }
    if ($key -notin $OptionKeys) { Fail "未知选项：$raw（-h 查看用法）" }
    # 无值开关：no-cache（build）/ deps（等价于 deps 子命令）/ write（deps --write）
    if ($key -eq 'no-cache') { $noCache = $true; continue }
    if ($key -eq 'deps') { $depsSwitch = $true; continue }
    if ($key -eq 'write') { $write = $true; continue }
    if ($val -eq '') {
        if ($i + 1 -ge $args.Count) { Fail "$raw 需要参数（-h 查看用法）" }
        $i++; $val = [string]$args[$i]
    }
    switch ($key) {
        'p' { $product = $val }
        'product' { $product = $val }
        'version' { $version = $val }
        'wheel' { $wheel = $val }
        'torch' { $torch = $val }
        'base-image' { $baseImage = $val }
        'pip-mirror' { $pipMirror = $val }
    }
}
# -Deps 是 deps 子命令的 Windows 原生写法：与位置命令并存时不得指向同一命令之外
if ($depsSwitch) {
    if ($command -ne '' -and $command -ne 'deps') { Fail "命令冲突：-Deps 与 $command 不能同时使用（-h 查看用法）" }
    $command = 'deps'
}
if ($command -eq '') { Show-Usage; exit 1 }
if ($torch -ne '' -and $torch -notin $Flavors) { Fail "非法形态：$torch（白名单 $($Flavors -join '|')）" }
if ($pipMirror -ne '' -and $pipMirror -notin $Mirrors) { Fail "非法 pip 镜像源：$pipMirror（白名单 $($Mirrors -join '|')）" }
$used = @{
    wheel        = ($wheel -ne ''); version = ($version -ne ''); torch = ($torch -ne '')
    'base-image' = ($baseImage -ne ''); 'pip-mirror' = ($pipMirror -ne '')
    'no-cache'   = $noCache; write = $write
}
foreach ($name in @($used.Keys)) {
    if ($used[$name] -and $name -notin $Allow[$command]) { Fail "--$name 不适用于 $command 命令（-h 查看用法）" }
}

# —— 桥接到 bash 版（所有动态值经 argv 传入，不做插值拼命令） ——
# wsl.exe 会吞掉参数中的单个反斜杠（D:\x → D:x），Windows 绝对路径先归一到 /mnt/<盘>/…
if ($wheel -ne '' -and $wheel -match '^[A-Za-z]:[\\/]') { $wheel = ConvertTo-WslPath $wheel }
$bridgeArgs = @()
if ($product -ne '') { $bridgeArgs += @('--product', $product) }
$bridgeArgs += $command
if ($wheel -ne '') { $bridgeArgs += @('--wheel', $wheel) }
if ($version -ne '') { $bridgeArgs += @('--version', $version) }
if ($torch -ne '') { $bridgeArgs += @('--torch', $torch) }
if ($baseImage -ne '') { $bridgeArgs += @('--base-image', $baseImage) }
if ($pipMirror -ne '') { $bridgeArgs += @('--pip-mirror', $pipMirror) }
if ($noCache) { $bridgeArgs += '--no-cache' }
if ($write) { $bridgeArgs += '--write' }

if ($null -eq (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    Fail "未找到 wsl.exe：容器命令须在 WSL 内执行——请安装 WSL2，或在 WSL 内直接运行 bash bin/relpack"
}
$distro = Get-WslDistro
$wslScript = ConvertTo-WslPath (Join-Path $BinDir 'relpack')
$wslArgs = @('-d', $distro, '--', 'bash', $wslScript) + $bridgeArgs
$display = ($wslArgs | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } }) -join ' '
& wsl.exe @wslArgs
if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host "[ERR ] relpack 失败（exit $LASTEXITCODE）" -ForegroundColor Red
    Write-Host "  发行版  : $distro"
    Write-Host "  复现命令: wsl.exe $display"
    exit $LASTEXITCODE
}