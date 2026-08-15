#Requires -Version 5.1
<#
.SYNOPSIS
    onnx-dev 容器一键启动脚本 (PowerShell)
.DESCRIPTION
    Windows PowerShell 包装器，通过 WSL 运行容器启动脚本
.EXAMPLE
    .\start-dev.ps1                    # Ephemeral Python REPL
    .\start-dev.ps1 test_simple.py     # 运行测试脚本
    .\start-dev.ps1 -Info              # 显示镜像信息
    .\start-dev.ps1 -Daemon            # Persistent 后台模式
#>

param(
    [switch]$Daemon,
    [switch]$Bash,
    [switch]$Info,
    [switch]$Stop,
    [switch]$Logs,
    [switch]$Help,
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Remaining
)

if ($Help) {
    Write-Host @"
onnx-dev 容器启动脚本 (PowerShell)

用法:
  .\start-dev.ps1                      Ephemeral Python REPL
  .\start-dev.ps1 <script.py> [args]   运行脚本
  .\start-dev.ps1 -Bash                进入 bash
  .\start-dev.ps1 -Info                显示镜像/容器信息
  .\start-dev.ps1 -Daemon              Persistent 后台模式
  .\start-dev.ps1 -Daemon -Stop        停止容器
  .\start-dev.ps1 -Daemon -Logs        查看日志
  .\start-dev.ps1 -Help                显示帮助

示例:
  .\start-dev.ps1 test_simple.py
  .\start-dev.ps1 -Info
"@
    exit 0
}

# 配置
$WslDistro = "Ubuntu-26.04"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WslDrive = $ScriptDir.Substring(0,1).ToLower()
$WslPath = "/mnt/$WslDrive/" + $ScriptDir.Substring(3) -replace '\\', '/'
$WslScript = "$WslPath/wsl-run.sh"

Write-Host "[INFO] WSL: $WslDistro" -ForegroundColor Cyan
Write-Host "[INFO] 脚本: $WslScript" -ForegroundColor Cyan
Write-Host ""

# 构建参数
$wslArgs = @("-d", $WslDistro, "--", "bash", $WslScript)
if ($Daemon) { $wslArgs += "-d" }
if ($Stop) { $wslArgs += "--stop" }
if ($Logs) { $wslArgs += "--logs" }
if ($Bash) { $wslArgs += "--bash" }
if ($Info) { $wslArgs += "--info" }
if ($Remaining) { $wslArgs += $Remaining }

& wsl.exe @wslArgs
exit $LASTEXITCODE
