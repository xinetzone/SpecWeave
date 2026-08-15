# ==============================================================================
# 三层修复闭环 · 通用自动化脚本模板
# ==============================================================================
# 配套模式：docs/retrospective/patterns/methodology-patterns/three-layer-repair-closure.md
# 参考实现：.agents/scripts/fix-screenshot-tool.ps1（-Watch 守护模式）
#
# 本模板将「三层修复闭环」方法论文档化，用于处置"反复复发型故障"：
#   第 1 层 · 止血（Stop Bleeding）：执行最小修复恢复当前症状
#   第 2 层 · 断源（Remove Source）：探测并提示周期性破坏源
#   第 3 层 · 兜底（Auto Heal）：-Watch 守护模式，监视故障信号自动止血
#
# 定制步骤（搜索 TODO 标记）：
#   1. $TargetName              → 目标应用/服务/包名
#   2. $FaultSignalThreshold    → 故障信号判定（事件日志/进程/文件缺失）
#   3. Invoke-StopBleeding 函数 → 你的止血修复命令（幂等、可验证）
#   4. Invoke-SourceProbe 函数  → 你的破坏源探测逻辑（只读）
#
# 遵循：自动化幂等四要素（bp-automation-idempotent-four-elements）：
#   E1 面向结果建模 | E2 幂等 | E3 备份可回滚 | E4 常量集中 + 可判定 verify
# ==============================================================================

#Requires -Version 5.1

<#
.SYNOPSIS
    三层修复闭环通用模板（治标 → 断源 → 兜底）
.DESCRIPTION
    针对反复复发型故障的通用修复脚本骨架。默认执行 第1层止血 + 第2层断源探测；
    -Watch 进入第3层守护模式，循环监视故障信号并自动止血。
.PARAMETER TargetName
    TODO: 目标应用/服务/包名（用于日志与判定）
.PARAMETER DryRun
    演练模式：只打印将执行的动作，不实际修改（用于首次验证模板）
.PARAMETER Watch
    第3层守护模式：每 WatchIntervalSeconds 秒检查故障信号，检测到即自动止血
.PARAMETER WatchIntervalSeconds
    守护模式检查间隔（默认 60 秒）
.PARAMETER SkipHeal
    跳过第1层止血（仅探测断源）
.PARAMETER SkipSource
    跳过第2层断源探测（仅止血）
.EXAMPLE
    pwsh -File three-layer-repair-closure-template.ps1 -TargetName "my-service"
    单次：止血 + 断源探测
.EXAMPLE
    pwsh -File three-layer-repair-closure-template.ps1 -TargetName "my-service" -Watch
    守护：每 60 秒检查故障信号并自动止血
.EXAMPLE
    pwsh -File three-layer-repair-closure-template.ps1 -TargetName "my-service" -DryRun
    演练：查看脚本将执行的动作而不实际修改
.NOTES
    SpecWeave 三层修复闭环模板 v1.0
    兼容 PowerShell 5.1+ / 7.4+（结构化日志使用 Write-Host，无 7.x 专属语法）
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$TargetName = "your-app",      # TODO: 目标应用/服务/包名

    [switch]$DryRun,
    [switch]$Watch,
    [int]$WatchIntervalSeconds = 60,
    [switch]$SkipHeal,
    [switch]$SkipSource,

    # 状态/日志文件（幂等与可审计）
    [string]$StateFile = "$env:TEMP\three-layer-repair-state.json"
)

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

# ==============================================================================
# 常量集中声明区（E4：单点修改，避免硬编码散落）
# ==============================================================================
# TODO: 故障信号判定阈值——返回 $true 表示"当前处于故障态"
# 示例（事件日志）：
#   Get-WinEvent -LogName 'Microsoft-Windows-AppModel-Runtime/Admin' -MaxEvents 200 -ErrorAction SilentlyContinue |
#       Where-Object { $_.Id -in 208,216 -and $_.Message -match 'ScreenSketch' }
function Test-FaultSignal {
    param()
    # TODO: 替换为你的故障信号判定逻辑
    # 返回 $true 表示检测到故障，$false 表示正常
    return $false
}

# ==============================================================================
# 结构化日志
# ==============================================================================
function Write-Info { param([string]$m) Write-Host "[INFO] $m" -ForegroundColor Green }
function Write-Warn { param([string]$m) Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Write-Err  { param([string]$m) Write-Host "[ERROR] $m" -ForegroundColor Red }
function Write-Step { param([string]$m) Write-Host ""; Write-Host "===== $m =====" -ForegroundColor Cyan; Write-Host "" }

# ==============================================================================
# 第 1 层 · 止血：执行最小修复恢复症状（E1 面向结果 + E2 幂等 + E3 备份可回滚）
# ==============================================================================
function Invoke-StopBleeding {
    param([bool]$AllowModify = $true)
    Write-Step "第 1 层 · 止血 ($TargetName)"

    if ($DryRun -or -not $AllowModify) {
        Write-Warn "[演练] 将执行止血修复："
        Write-Warn "  -> TODO 你的止血命令（重注册/重启服务/恢复配置）"
        return $true
    }

    # E3：如需改写任何配置文件，先备份
    # $backup = "$configPath.bak-$(Get-Date -Format 'yyyyMMddHHmmss')"
    # Copy-Item $configPath $backup -Force

    # TODO: 你的止血修复命令（必须幂等：重复执行无副作用）
    # Add-AppxPackage -DisableDevelopmentMode -Register "$installPath\AppXManifest.xml"
    # Restart-Service -Name $TargetName -Force

    # E4 verify：修复后判定是否恢复（人读 PASS/FAIL + 退出码）
    if (Test-FaultSignal) {
        Write-Err "[FAIL] $TargetName 仍处于故障态"
        return $false
    }
    Write-Info "[PASS] $TargetName 已恢复"
    return $true
}

# ==============================================================================
# 第 2 层 · 断源：探测并提示周期性破坏源（只读）
# ==============================================================================
function Invoke-SourceProbe {
    Write-Step "第 2 层 · 断源探测 ($TargetName)"

    if ($DryRun) {
        Write-Warn "[演练] 将执行破坏源探测："
        Write-Warn "  -> TODO 你的破坏源探测逻辑（清理软件/杀毒/更新/计划任务）"
        return
    }

    # TODO: 探测可疑破坏源（只读，不修改任何东西）
    # 示例：检查可疑清理/优化进程
    # $suspects = Get-Process -ErrorAction SilentlyContinue |
    #     Where-Object { $_.ProcessName -match 'clean|optimize|master|youhua' }
    # if ($suspects) { Write-Warn "发现可疑进程: $($suspects.ProcessName -join ', ')" }

    Write-Info "断源探测完成：若存在周期性破坏源，请执行白名单/卸载/禁用隔离"
    Write-Info "（断源是唯一根治动作；只靠止血必然复发——见模式文档反模式1）"
}

# ==============================================================================
# 第 3 层 · 兜底：守护循环，监视故障信号自动止血
# ==============================================================================
function Invoke-WatchHeal {
    param([int]$IntervalSeconds)
    Write-Step "第 3 层 · 守护自愈 (每 $IntervalSeconds 秒检查)"
    Write-Info "按 Ctrl+C 停止。"
    while ($true) {
        $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        if (Test-FaultSignal) {
            Write-Warn "[$ts] 检测到 $TargetName 故障信号，执行自动止血..."
            $ok = Invoke-StopBleeding -AllowModify $true
            if ($ok) { Write-Info "[$ts] 自愈成功" }
            else     { Write-Err  "[$ts] 自愈失败，请人工介入" }
        }
        else {
            Write-Info "[$ts] $TargetName 正常，继续监视..."
        }
        Start-Sleep -Seconds $IntervalSeconds
    }
}

# ==============================================================================
# 主流程
# ==============================================================================
Write-Step "三层修复闭环 · $TargetName"

if ($DryRun) { Write-Warn "DryRun 模式：仅展示动作，不实际修改" }

if ($Watch) {
    Invoke-WatchHeal -IntervalSeconds $WatchIntervalSeconds
    exit 0
}

# 第 1 层：止血
$healed = $true
if (-not $SkipHeal) {
    $healed = Invoke-StopBleeding -AllowModify $true
}

# 第 2 层：断源探测（无论止血是否成功都执行，定位复发根因）
if (-not $SkipSource) {
    Invoke-SourceProbe
}

if ($healed) {
    Write-Step "完成"
    Write-Info "$TargetName 处置完成（止血 + 断源探测）。建议用 -Watch 开启守护兜底。"
    exit 0
}
else {
    Write-Err "止血未成功，请检查上述输出后重试，或人工介入。"
    exit 1
}
