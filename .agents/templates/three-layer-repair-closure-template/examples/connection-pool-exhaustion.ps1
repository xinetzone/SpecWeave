# ==============================================================================
# 连接池耗尽 · 三层修复闭环 具体示例脚本
# ==============================================================================
# 配套模板：../three-layer-repair-closure-template.ps1（通用骨架）
# 配套模式：docs/retrospective/patterns/methodology-patterns/three-layer-repair-closure.md
#
# 场景：数据库连接池周期性耗尽（如每两周连接数到顶），应用报
#       "too many connections" / "connection pool exhausted"，重启应用恢复。
# 三层落地（PostgreSQL/psql 实现，MySQL 等价命令见注释）：
#   第 1 层 · 止血：终止【空闲超时】连接（pg_terminate_backend）
#   第 2 层 · 断源：按 client_addr/application_name 分组统计连接来源，定位泄漏源
#   第 3 层 · 兜底：-Watch 守护，监视连接数阈值，超限自动清理
#
# 安全红线（本示例已内置，勿移除）：
#   R1 只终止 state='idle' 的连接，绝不终止 active 事务/查询
#   R2 单次止血有数量上限（$MaxIdleConnectionsToKill），防止误伤全量连接
#   R3 密码走环境变量 PGPASSWORD，禁止明文硬编码
#   R4 默认 DryRun 演练，确认无误后再实跑
# ==============================================================================

#Requires -Version 5.1

<#
.SYNOPSIS
    PostgreSQL 连接池耗尽 · 三层修复闭环示例
.DESCRIPTION
    针对数据库连接数周期性耗尽场景的具体修复脚本。默认执行 第1层止血 + 第2层断源探测；
    -Watch 进入第3层守护模式。
.PARAMETER DbHost / DbPort / DbName / DbUser
    PostgreSQL 连接信息
.PARAMETER DbPassword
    可选；推荐改用环境变量 PGPASSWORD（或使用 psql 交互），禁止明文硬编码
.PARAMETER ThresholdPercent
    连接数达到 max_connections 的百分比即判故障（默认 80）
.PARAMETER IdleTimeoutSeconds
    止血：清理空闲超过该秒数的连接（默认 300）
.PARAMETER MaxIdleConnectionsToKill
    单次止血最多终止的连接数上限（默认 50，安全红线 R2）
.PARAMETER DryRun
    演练：仅打印 SQL 与将终止的连接，不实际执行
.PARAMETER Watch
    第3层守护模式
.PARAMETER WatchIntervalSeconds
    守护检查间隔（默认 60）
.EXAMPLE
    pwsh -File connection-pool-exhaustion.ps1 -DryRun
    演练：查看将清理的连接与断源统计
.EXAMPLE
    pwsh -File connection-pool-exhaustion.ps1 -ThresholdPercent 85 -IdleTimeoutSeconds 600
    单次：终止空闲超 10 分钟的连接 + 断源统计
.EXAMPLE
    pwsh -File connection-pool-exhaustion.ps1 -Watch -WatchIntervalSeconds 120
    守护：每 2 分钟检查连接数，超阈值自动清理
.NOTES
    SpecWeave 三层修复闭环示例 v1.0 ｜ 参考实现基于 PostgreSQL 11+
    适配 MySQL：连接数 SELECT COUNT(*) FROM information_schema.PROCESSLIST；
               kill 用 KILL <id>；（注意 MySQL 无 state，按 Command='Sleep' 且 Time>N 判定空闲）
    适配 Oracle：SELECT COUNT(*) FROM v$session；ALTER SYSTEM KILL SESSION 'sid,serial#'
#>

[CmdletBinding()]
param(
    [string]$DbHost = "127.0.0.1",
    [int]$DbPort = 5432,
    [string]$DbName = "appdb",
    [string]$DbUser = "app",
    [string]$DbPassword = "",

    [int]$ThresholdPercent = 80,
    [int]$IdleTimeoutSeconds = 300,
    [int]$MaxIdleConnectionsToKill = 50,

    [switch]$DryRun,
    [switch]$Watch,
    [int]$WatchIntervalSeconds = 60
)

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

# ==============================================================================
# 结构化日志
# ==============================================================================
function Write-Info { param([string]$m) Write-Host "[INFO] $m" -ForegroundColor Green }
function Write-Warn { param([string]$m) Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Write-Err  { param([string]$m) Write-Host "[ERROR] $m" -ForegroundColor Red }
function Write-Step { param([string]$m) Write-Host ""; Write-Host "===== $m =====" -ForegroundColor Cyan; Write-Host "" }

# ==============================================================================
# 连接与查询工具（E4 常量集中）
# ==============================================================================
function Get-PsqlQuery {
    param([string]$Sql, [int]$TimeoutSeconds = 15)
    $env:PGPASSWORD = $DbPassword
    $out = psql -h $DbHost -p $DbPort -U $DbUser -d $DbName -t -A -c $Sql `
            -v ON_ERROR_STOP=1 --no-align --field-separator='|' `
            2>$null
    return $out
}

# ==============================================================================
# 故障信号判定：连接数是否超过阈值（机器可判，返回布尔）
# ==============================================================================
function Test-FaultSignal {
    # 当前连接数 / max_connections 百分比
    $row = Get-PsqlQuery "SELECT round(count(*) * 100.0 / m.max_conn) FROM pg_stat_activity a, (SELECT setting::int AS max_conn FROM pg_settings WHERE name='max_connections') m;"
    if (-not $row) {
        Write-Warn "无法查询连接数（数据库不可达？），按非故障处理以避免误操作"
        return $false
    }
    $pct = [int]($row.Trim())
    Write-Info "当前连接使用率: $pct% (阈值 $ThresholdPercent%)"
    return ($pct -ge $ThresholdPercent)
}

# ==============================================================================
# 第 1 层 · 止血：终止空闲超时连接（只杀 idle，绝不杀 active）
# ==============================================================================
function Invoke-StopBleeding {
    param([bool]$AllowModify = $true)
    Write-Step "第 1 层 · 止血 (连接池 ${DbUser}@${DbHost}:${DbPort}/${DbName})"

    # 找出空闲超时连接（安全红线 R1：仅 state='idle'）
    $idleSql = "SELECT pid, application_name, coalesce(client_addr::text,'local') AS client, round(extract(epoch FROM (now()-state_change))) AS idle_s FROM pg_stat_activity WHERE state='idle' AND now()-state_change > interval '$IdleTimeoutSeconds seconds' ORDER BY idle_s DESC LIMIT $MaxIdleConnectionsToKill;"
    $idle = @(Get-PsqlQuery $idleSql)

    if ($idle.Count -eq 0 -or -not $idle[0]) {
        Write-Info "无空闲超时连接（> ${IdleTimeoutSeconds}s）需清理"
        return $true
    }

    Write-Warn "发现 $($idle.Count) 个空闲超时连接（上限 $MaxIdleConnectionsToKill）："
    $idle | ForEach-Object { Write-Warn "  $_" }

    if ($DryRun -or -not $AllowModify) {
        Write-Warn "[演练] 将执行：pg_terminate_backend 终止上述连接"
        return $true
    }

    # 终止（幂等：重复执行无副作用；数量受 LIMIT 保护）
    $killSql = "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state='idle' AND now()-state_change > interval '$IdleTimeoutSeconds seconds' LIMIT $MaxIdleConnectionsToKill;"
    $null = Get-PsqlQuery $killSql
    Start-Sleep -Seconds 1

    # E4 verify：验证连接使用率是否回落到阈值以下
    if (Test-FaultSignal) {
        Write-Err "[FAIL] 止血后连接使用率仍 ≥ $ThresholdPercent%，可能有活跃连接泄漏，请人工介入"
        return $false
    }
    Write-Info "[PASS] 连接使用率已回落至阈值以下"
    return $true
}

# ==============================================================================
# 第 2 层 · 断源：按来源分组统计，定位连接泄漏源头（只读）
# ==============================================================================
function Invoke-SourceProbe {
    Write-Step "第 2 层 · 断源探测 (按来源分组统计连接)"
    if ($DryRun) {
        Write-Warn "[演练] 将执行连接来源统计 SQL"
        return
    }
    $srcSql = "SELECT coalesce(client_addr::text,'local') AS client, coalesce(application_name,'(null)') AS app, state, count(*) AS n FROM pg_stat_activity GROUP BY 1,2,3 ORDER BY n DESC, client;"
    Write-Info "连接来源 Top（client | app | state | count）："
    Get-PsqlQuery $srcSql | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    Write-Warn "断源提示：若某 client_addr/application_name 长期保持 active 且计数居高不下，大概率是该调用方连接未释放（泄漏 SQL/池配置过小）"
    Write-Warn "根治动作：修代码释放连接 / 调整池上限 / 加连接回收，仅靠止血必然复发（反模式1）"
}

# ==============================================================================
# 第 3 层 · 兜底：守护循环
# ==============================================================================
function Invoke-WatchHeal {
    param([int]$IntervalSeconds)
    Write-Step "第 3 层 · 守护自愈 (每 $IntervalSeconds 秒检查)"
    Write-Info "按 Ctrl+C 停止。"
    while ($true) {
        $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        if (Test-FaultSignal) {
            Write-Warn "[$ts] 连接使用率超阈值，执行自动止血..."
            $ok = Invoke-StopBleeding -AllowModify $true
            if ($ok) { Write-Info "[$ts] 自愈成功" } else { Write-Err "[$ts] 自愈失败，请人工介入" }
        }
        else {
            Write-Info "[$ts] 连接使用率正常，继续监视..."
        }
        Start-Sleep -Seconds $IntervalSeconds
    }
}

# ==============================================================================
# 主流程
# ==============================================================================
Write-Step "三层修复闭环 · 连接池 ${DbUser}@${DbHost}:${DbPort}/${DbName}"
if ($DryRun) { Write-Warn "DryRun 模式：仅展示动作，不实际修改" }
if ([string]::IsNullOrEmpty($DbPassword)) {
    Write-Warn "DbPassword 为空：将使用环境变量 PGPASSWORD（推荐）或 psql 交互。若两者皆无请先设置。"
}

if ($Watch) {
    Invoke-WatchHeal -IntervalSeconds $WatchIntervalSeconds
    exit 0
}

$healed = Invoke-StopBleeding -AllowModify (-not $DryRun)
Invoke-SourceProbe

if ($healed) {
    Write-Step "完成"
    Write-Info "处置完成。建议用 -Watch 开启守护兜底；并跟进断源（泄漏代码修复）。"
    exit 0
}
else {
    Write-Err "止血未成功，请人工介入排查活跃连接泄漏。"
    exit 1
}
