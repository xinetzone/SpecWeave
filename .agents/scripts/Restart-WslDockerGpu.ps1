#Requires -Version 5.1
# PWSH7-EXEMPT: WSL系统维护脚本，有意兼容 Windows PowerShell 5.1

<#
.SYNOPSIS
    重启WSL并验证Docker GPU自动启动状态。
.DESCRIPTION
    执行 wsl --shutdown 关闭WSL，等待WSL自动重启，然后通过三层验证模型
    （L1驱动层→L2工具层→L3运行时层→GPU容器端到端测试）确认Docker GPU支持正常。
.PARAMETER Distro
    WSL发行版名称，默认 "Ubuntu"。
.PARAMETER ShutdownWaitSeconds
    wsl --shutdown 后等待秒数，默认 8。
.PARAMETER BootWaitSeconds
    WSL启动后等待Docker boot命令完成的秒数，默认 20。
.PARAMETER NoContainerTest
    跳过GPU容器端到端测试。
.PARAMETER Diagnose
    诊断模式：不重启WSL，仅诊断。
#>

param(
    [string]$Distro = 'Ubuntu',
    [int]$ShutdownWaitSeconds = 8,
    [int]$BootWaitSeconds = 20,
    [switch]$NoContainerTest,
    [switch]$Diagnose
)

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

function Write-Step { param([string]$msg) Write-Host "`n[*] $msg" -ForegroundColor Cyan }
function Write-Pass { param([string]$msg) Write-Host "[PASS] $msg" -ForegroundColor Green }
function Write-Fail { param([string]$msg) Write-Host "[FAIL] $msg" -ForegroundColor Red }
function Write-Warn { param([string]$msg) Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Info { param([string]$msg) Write-Host "       $msg" -ForegroundColor Gray }

function Test-WslCommand {
    param([string]$cmd)
    $suffix = ' 2>/dev/null; echo EXIT_CODE:$?'
    $fullCmd = $cmd + $suffix
    $output = wsl.exe -d $Distro -e bash -c $fullCmd 2>&1
    return ($output -match 'EXIT_CODE:0')
}

$TroubleshootGuide = @'

==================== 排查指南 ====================

【L1 驱动层失败】nvidia-smi不可用
  排查步骤：
  1. 在WSL中执行: ls /usr/lib/wsl/lib/libcuda* 确认驱动库存在
  2. 在Windows设备管理器中确认NVIDIA GPU正常
  3. 执行 wsl --shutdown 后重新打开WSL
  4. Windows侧更新NVIDIA驱动到最新版本
  5. 检查WSL版本: wsl --version（需要WSL2 2.0+）

【L2 工具层失败】nvidia-container-toolkit未安装或异常
  排查步骤：
  1. 在WSL中重新运行: sudo bash setup-wsl-docker-gpu.sh
  2. 手动检查: dpkg -l | grep nvidia-container-toolkit
  3. 检查apt源: cat /etc/apt/sources.list.d/nvidia-container-toolkit.list
  4. 手动安装: sudo apt update; sudo apt install -y nvidia-container-toolkit
  5. 检查源中$ARCH是否展开: 不应出现$ARCH字面量，应为amd64

【L3 运行时层失败】Docker nvidia runtime未注册或Docker未运行
  排查步骤：
  1. 检查Docker是否运行: ps aux | grep dockerd
  2. 检查daemon.json: cat /etc/docker/daemon.json
     （应包含 runtimes.nvidia 配置）
  3. 重新配置: sudo nvidia-ctk runtime configure --runtime=docker
  4. 检查wsl.conf [boot]命令:
     cat /etc/wsl.conf | grep -A2 boot
     （command应启动containerd和dockerd）
  5. 手动启动Docker（WSL无systemd环境）:
     sudo setsid containerd > /var/log/containerd.log 2>&1 < /dev/null &
     sleep 2; sudo setsid dockerd > /var/log/dockerd.log 2>&1 < /dev/null &
  6. 查看启动日志:
     cat /var/log/dockerd-boot.log 2>/dev/null
     cat /var/log/containerd-boot.log 2>/dev/null
     cat /var/log/dockerd.log 2>/dev/null | tail -30

【GPU容器测试失败】Docker runtime正常但容器内无法访问GPU
  排查步骤：
  1. 检查containerd是否启动: ps aux | grep containerd
  2. 检查nvidia-container-runtime路径: which nvidia-container-runtime
  3. 检查daemon.json中nvidia runtime的path配置
  4. 查看dockerd日志中GPU相关错误:
     cat /var/log/dockerd.log | grep -i nvidia | tail -10
  5. 重启Docker服务（手动kill后setsid启动）

如果以上步骤无法解决，在WSL中运行:
  sudo bash setup-wsl-docker-gpu.sh
（重新执行完整安装配置流程，幂等安全）

====================================================
'@

function Show-Troubleshooting {
    param([bool]$L1_pass, [bool]$L2_pass, [bool]$L3_pass, [bool]$Gpu_pass)

    Write-Host $TroubleshootGuide -ForegroundColor Magenta
}

# 主流程
if ($Diagnose) {
    Write-Host '============================================' -ForegroundColor White
    Write-Host ' WSL Docker GPU 诊断模式（不重启WSL）' -ForegroundColor White
    Write-Host '============================================' -ForegroundColor White
} else {
    Write-Host '============================================' -ForegroundColor White
    Write-Host ' WSL Docker GPU 重启验证工具' -ForegroundColor White
    Write-Host '============================================' -ForegroundColor White

    Write-Step '检查 wsl.exe 可用性'
    $wslAvailable = Get-Command wsl.exe -ErrorAction SilentlyContinue
    if (-not $wslAvailable) { Write-Fail 'wsl.exe 未找到，请确保WSL已安装'; exit 1 }
    Write-Pass 'wsl.exe 可用'

    Write-Step "检查WSL发行版: $Distro"
    $distros = wsl.exe -l -q 2>&1
    $distroExists = $false
    foreach ($d in $distros) {
        $cleanName = $d.Trim() -replace "`0", ''
        if ($cleanName -eq $Distro) { $distroExists = $true; break }
    }
    if (-not $distroExists) {
        Write-Fail "发行版 '$Distro' 不存在。可用发行版："
        wsl.exe -l -v
        exit 1
    }
    Write-Pass "发行版 $Distro 存在"

    Write-Step "执行 wsl --shutdown（等待 $ShutdownWaitSeconds 秒）"
    wsl.exe --shutdown
    Start-Sleep -Seconds $ShutdownWaitSeconds
    Write-Pass 'WSL已关闭'

    Write-Step "触发WSL启动，等待boot命令完成（等待 $BootWaitSeconds 秒）"
    wsl.exe -d $Distro -e bash -c 'echo WSL booting...' 2>&1 | Out-Null
    Write-Info 'WSL已唤醒，等待Docker boot命令完成...'
    Start-Sleep -Seconds $BootWaitSeconds
    Write-Pass '等待完成'
}

# 三层验证
$passCount = 0
$failCount = 0

Write-Step 'L1 驱动层验证: nvidia-smi'
$l1_suffix = ' 2>&1; echo EXIT_CODE:$?'
$l1Cmd = 'nvidia-smi' + $l1_suffix
$l1Output = wsl.exe -d $Distro -e bash -c $l1Cmd 2>&1
$L1_pass = ($l1Output -match 'EXIT_CODE:0') -and ($l1Output -match 'NVIDIA-SMI')
if ($L1_pass) {
    $driverVer = ($l1Output | Select-String 'Driver Version:\s*(\S+)').Matches.Groups[1].Value
    $gpuName = ($l1Output | Select-String '\|\s+0\s+(\S.+\S)\s+On').Matches.Groups[1].Value
    if (-not $gpuName) { $gpuName = 'NVIDIA GPU' }
    Write-Pass 'nvidia-smi 正常'
    Write-Info "GPU: $gpuName | 驱动: $driverVer"
    $passCount++
} else {
    Write-Fail 'nvidia-smi 不可用'
    $failCount++
}

Write-Step 'L2 工具层验证: nvidia-container-toolkit'
$l2Check1 = Test-WslCommand 'which nvidia-container-runtime'
$l2Check2 = Test-WslCommand 'dpkg -l nvidia-container-toolkit 2>/dev/null | grep -q ^ii'
$l2Check3 = Test-WslCommand 'which nvidia-ctk'
$L2_pass = $l2Check1 -and $l2Check2 -and $l2Check3
if ($L2_pass) {
    $ctkCmd = 'nvidia-ctk --version 2>/dev/null | head -1'
    $ctkVer = wsl.exe -d $Distro -e bash -c $ctkCmd 2>&1
    Write-Pass 'nvidia-container-toolkit 已安装'
    Write-Info $ctkVer
    $passCount++
} else {
    Write-Fail 'nvidia-container-toolkit 未完整安装'
    Write-Info "  which nvidia-container-runtime: $(if($l2Check1){'OK'}else{'MISSING'})"
    Write-Info "  dpkg nvidia-container-toolkit: $(if($l2Check2){'OK'}else{'NOT INSTALLED'})"
    Write-Info "  which nvidia-ctk: $(if($l2Check3){'OK'}else{'MISSING'})"
    $failCount++
}

Write-Step 'L3 运行时层验证: Docker nvidia runtime'
$l3Check1 = Test-WslCommand 'docker info >/dev/null 2>&1'
$l3Check2 = $false
$l3Runtime = ''
if ($l3Check1) {
    $l3Runtime = wsl.exe -d $Distro -e bash -c 'docker info 2>&1 | grep Runtimes' 2>&1
    $l3Check2 = $l3Runtime -match 'nvidia'
}
$L3_pass = $l3Check1 -and $l3Check2
if ($L3_pass) {
    Write-Pass 'Docker运行中且nvidia runtime已注册'
    Write-Info $l3Runtime.Trim()
    $passCount++
} else {
    if (-not $l3Check1) { Write-Fail 'Docker未运行' }
    else { Write-Fail 'Docker nvidia runtime未注册'; Write-Info $l3Runtime.Trim() }
    $failCount++
}

# GPU容器测试
$Gpu_pass = $false
if (-not $NoContainerTest -and $L3_pass) {
    Write-Step 'GPU容器端到端测试: docker run --gpus all'
    $gpuCheckCmd = 'bash -c ''if docker images ubuntu:22.04 --format "{{.Repository}}:{{.Tag}}" 2>/dev/null | grep -q ubuntu:22.04; then docker run --rm --gpus all ubuntu:22.04 nvidia-smi >/dev/null 2>&1 && echo GPU_OK || echo GPU_FAIL; else echo NEED_PULL; fi'''
    $gpuResult = wsl.exe -d $Distro -e $gpuCheckCmd 2>&1

    if ($gpuResult -match 'GPU_OK') {
        Write-Pass '容器内GPU访问正常'
        $Gpu_pass = $true; $passCount++
    } elseif ($gpuResult -match 'NEED_PULL') {
        Write-Info '本地无ubuntu:22.04镜像，执行拉取和测试...'
        $gpuPullCmd = 'docker run --rm --gpus all ubuntu:22.04 nvidia-smi 2>&1 && echo GPU_OK || echo GPU_FAIL'
        $gpuResult2 = wsl.exe -d $Distro -e bash -c $gpuPullCmd 2>&1
        if ($gpuResult2 -match 'GPU_OK') {
            Write-Pass '容器内GPU访问正常'
            $Gpu_pass = $true; $passCount++
        } else {
            Write-Fail '容器内GPU访问失败'
            Write-Info ($gpuResult2 -replace 'GPU_FAIL','' | Select-Object -Last 5 | Out-String).Trim()
            $failCount++
        }
    } else {
        Write-Fail '容器内GPU访问失败'
        Write-Info ($gpuResult -replace 'GPU_FAIL','' | Select-Object -Last 5 | Out-String).Trim()
        $failCount++
    }
} elseif ($NoContainerTest) {
    Write-Info '（已跳过容器端到端测试 -NoContainerTest）'
    $Gpu_pass = $true
} else {
    Write-Info '（L3失败，跳过容器测试）'
}

# 结果汇总
Write-Host "`n============================================" -ForegroundColor White
Write-Host ' 验证结果汇总' -ForegroundColor White
Write-Host '============================================' -ForegroundColor White
Write-Host "  L1 驱动层:     $(if($L1_pass){'PASS'}else{'FAIL'})" -ForegroundColor $(if($L1_pass){'Green'}else{'Red'})
Write-Host "  L2 工具层:     $(if($L2_pass){'PASS'}else{'FAIL'})" -ForegroundColor $(if($L2_pass){'Green'}else{'Red'})
Write-Host "  L3 运行时层:   $(if($L3_pass){'PASS'}else{'FAIL'})" -ForegroundColor $(if($L3_pass){'Green'}else{'Red'})
if (-not $NoContainerTest) {
    Write-Host "  GPU容器测试:   $(if($Gpu_pass){'PASS'}else{'FAIL'})" -ForegroundColor $(if($Gpu_pass){'Green'}else{'Red'})
}
Write-Host '============================================' -ForegroundColor White

if ($failCount -gt 0) {
    Write-Host $TroubleshootGuide
    exit 1
} else {
    Write-Host "`n所有检查通过！Docker GPU已就绪。" -ForegroundColor Green
    exit 0
}
