# build-web-dist.ps1 — Windows 侧入口：经 WSL(openKylin-3.0) + podman 构建 doocs/md 前端
#
# 用法：
#   pwsh ./scripts/build-web-dist.ps1                 # 常规构建（保留工作副本，二次更快）
#   $env:MD_CLEAN='1'; pwsh ./scripts/build-web-dist.ps1   # 构建后清理 WSL 工作副本
#   $env:MD_SRC='/mnt/d/path/to/md'; pwsh ./scripts/build-web-dist.ps1
#
# 前提：openKylin-3.0 内 podman 已有 localhost/node:22-alpine 镜像
# （podman pull docker.m.daocloud.io/library/node:22-alpine）。
#Requires -Version 7.4
[CmdletBinding()]
param(
    [string]$Distro = 'openKylin-3.0'
)

$ErrorActionPreference = 'Stop'
$wsl = Join-Path $env:WINDIR 'System32\wsl.exe'
if (-not (Test-Path $wsl)) { throw "未找到 wsl.exe：$wsl" }

# 发行版存在性检查
# 注意：wsl.exe -l 始终输出 UTF-16LE（可能带 BOM、含 CRLF），不能直接用 & 捕获——
# PowerShell 会按 [Console]::OutputEncoding（中文系统常为 GBK）解码，产生 NUL、乱码与空条目。
# 这里通过 ProcessStartInfo.StandardOutputEncoding 显式指定 UTF-16LE 解码，避免代码页依赖。
function Get-WslDistros {
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = $wsl
    $psi.Arguments = '-l --quiet'
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.StandardOutputEncoding = [System.Text.Encoding]::Unicode
    $process = [System.Diagnostics.Process]::Start($psi)
    $stdout = $process.StandardOutput.ReadToEnd()
    $process.WaitForExit()
    # 兼容个别版本残留的 NUL 字符；Trim 后过滤空行
    $stdout -split "`r?`n" |
        ForEach-Object { $_.Trim([char]0).Trim() } |
        Where-Object { $_ }
}

$distros = @(Get-WslDistros)
if ($Distro -notin $distros) {
    throw "WSL 发行版 $Distro 不存在。可用：$($distros -join ', ')"
}

# 定位脚本（经 /mnt/d 映射传入 WSL）
$scriptWin = Join-Path $PSScriptRoot 'build-web-dist.sh'
if (-not (Test-Path $scriptWin)) { throw "缺少 $scriptWin" }

# CRLF -> LF（保证 bash 可执行；幂等）
$text = [System.IO.File]::ReadAllText($scriptWin) -replace "`r`n", "`n"
[System.IO.File]::WriteAllText($scriptWin, $text, (New-Object System.Text.UTF8Encoding($false)))

$scriptWsl = '/mnt/' + ($scriptWin -replace '^([A-Za-z]):[\\/]', { $_.Groups[1].Value.ToLower() + '/' }) -replace '\\', '/'

Write-Host "[ps1] 在 WSL($Distro) 执行 $scriptWsl" -ForegroundColor Cyan
& $wsl -d $Distro -e bash -lc "bash $(if ($env:MD_CLEAN) { 'MD_CLEAN=' + $env:MD_CLEAN + ' ' })'$scriptWsl'"
exit $LASTEXITCODE
