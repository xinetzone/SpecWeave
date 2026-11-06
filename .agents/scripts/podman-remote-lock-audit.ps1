<#
.SYNOPSIS
    Podman 远端连接锁定审计（只读）。

.DESCRIPTION
    把「容器存储只落远端、本地不膨胀」这条策略固化为可执行断言。
    默认完全不改状态；仅当显式传入 -Fix 时，允许执行「把默认连接设回
    remote-ai」这一项修复，且执行前先打印完整命令。

    审计项（C1-C10）：
      C1  默认连接名是否等于 remote-ai
      C2  本地 podman machine 是否存在且状态为 stopped
      C3  零参数 podman 实际落点是否为远端主机
      C4  本地容器存储目录实际体积
      C5  本地遗留归档（.tar/.vhdx/podman save 产物）扫描
      C6  D:\WSL 残留体积
      C7  远端 graphroot 所在文件系统可用空间
      C8  CONTAINER_HOST / DOCKER_HOST / CONTAINER_CONNECTION 是否被设置
      C9  WSL 发行版的 ext4.vhdx 体积（N/A=发行版已被删除）
      C10 WSL 内共享盘挂载与可写性（候选 /media/pc/data/ai 或 /media/pc/data；
          N/A=发行版已被删除）

.PARAMETER Json
    以 JSON 输出机器可读结果（不输出人类可读表格）。

.PARAMETER Fix
    仅修复 C1 与 C9：
      C1 执行 podman system connection default remote-ai；
      C9 在 C9 判 FAIL 且 sparse 未开启时执行
         wsl --manage openkylin-test --set-sparse true。
    执行前打印完整命令；绝不启动 machine、不改其他状态。
    C10 不提供修复动作：挂载属于外部会话的职责，脚本不重放可能破坏挂载的操作。

.NOTES
    退出码语义：0=全部 PASS；1=存在 FAIL；2=无 FAIL 但存在 UNKNOWN
    （例如 podman 缺失、远端不可达）。单条检查失败不会中断后续检查。

    依据：podman system connection ls --format json / podman machine ls --format json /
    podman info --format json（Host.serviceIsRemote + Store.GraphRoot）/
    ssh + df -B1（远端 graphroot 真实所在文件系统）。
    不使用 podman system df —— 其 infra-container 统计不可靠。
#>
#Requires -Version 5.1
# PWSH7-EXEMPT: 只读审计脚本，必须在 Windows PowerShell 5.1 下直接运行（语法限于 5.1 子集），同时兼容 pwsh 7.x

[CmdletBinding()]
param(
    [switch]$Json,
    [switch]$Fix
)

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) { $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
$RepoRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# =============================================================================
# 配置区（阈值与路径集中在此，便于日后调整）
# =============================================================================
$Config = [ordered]@{
    # C1：策略锁定的默认连接名
    ExpectedDefaultConnection = 'remote-ai'

    # C4：本地容器存储目录合计上限（MB）
    MaxLocalStorageMB = 1024

    # C6：D:\WSL 残留上限（MB）。当前实测基线约 2763 MB（machine 基础镜像 +
    #     WSL 导入 tar），阈值留约 10% 余量；超过即视为本地膨胀。
    MaxWslResidualMB = 3072

    # C7：远端 graphroot 所在文件系统可用空间低水位（GiB）
    MinRemoteFreeGiB = 50

    # C9：WSL 发行版与其 ext4.vhdx 体积上限
    #     基线 1,354,760,192 B ≈ 1.262 GiB（2026-11 实测），阈值约 2 倍余量。
    WslDistroName = 'openkylin-test'
    WslVhdxPath = 'D:\WSL\openkylin-test\ext4.vhdx'
    WslVhdxBaselineBytes = 1354760192
    MaxWslVhdxGiB = 2.5

    # C10：WSL 内共享盘挂载候选（按列表顺序逐个探测，取首个可写者）
    #      过渡期 /media/pc/data/ai 与旧布局 /media/pc/data 同时接受，
    #      因此挂载点切换、回滚到旧布局都不会制造假告警。
    WslMountPoints = @(
        '/media/pc/data/ai',
        '/media/pc/data'
    )
    EnableWslMountAutodiscover = $true

    # C6：本地 WSL 残留根目录
    WslResidualRoot = 'D:\WSL'

    # C5/C6：由 C9 单独计量的资产——既不算遗留归档，也不计入 WSL 残留总量，
    #         避免 C6 的 3 GiB 预算与 C9 的 2.5 GiB 上限互相矛盾。
    WslOwnedByC9Paths = @(
        'D:\WSL\openkylin-test\ext4.vhdx'
    )

    # C6：已知 WSL 资产（发行版磁盘 + 导入用安装介质），不计入「podman machine 残留」总量
    WslResidualExcludePaths = @(
        'D:\WSL\openkylin-test\ext4.vhdx',
        'D:\WSL\import\openKylin-3.0-wsl-amd64.wsl'
    )

    # C4：本地容器存储候选根（不存在的自动跳过）
    LocalStorageRootCandidates = @(
        (Join-Path $env:LOCALAPPDATA 'containers'),
        (Join-Path $env:USERPROFILE '.local\share\containers'),
        (Join-Path $env:USERPROFILE '.config\containers')
    )

    # C5：遗留归档扫描根（仅本地磁盘；工作区位于 SMB 共享，不消耗本地存储）
    LeftoverScanRoots = @(
        @{ Path = (Join-Path $env:USERPROFILE 'Downloads'); MaxDepth = 3 },
        @{ Path = (Join-Path $env:USERPROFILE 'Desktop'); MaxDepth = 2 },
        @{ Path = 'D:\WSL'; MaxDepth = 3 }
    )
    LeftoverNamePatterns = @('*.tar', '*.tar.gz', '*.tar.zst', '*.tar.xz', '*.vhdx')

    # C5：已知的 podman machine 基础镜像产物（属正常缓存，不计为违规）
    KnownMachineArtifactPatterns = @(
        'D:\WSL\libs\podman-machine-default.tar',
        'D:\WSL\podman-machine-wsl\*'
    )

    # C5：扫描时跳过的目录名（避免进入 .git/依赖树，防止重复覆盖 .temp）
    SkipDirectoryNames = @('.git', 'node_modules', '.venv', 'vendor', '__pycache__', '.temp')

    # 外部命令超时（秒）
    CommandTimeoutSec = 60
    SshTimeoutSec = 20
}

# =============================================================================
# 通用工具函数
# =============================================================================
$script:Results = New-Object System.Collections.ArrayList
$script:PodmanPath = $null
$script:DefaultUri = $null
$script:DefaultIdentity = $null
$script:GraphRoot = $null
$script:RemoteSocket = $null
$script:SparseEnabled = $null
$script:WslDistroExists = $false

$podmanCmd = Get-Command podman -ErrorAction SilentlyContinue
if ($podmanCmd) {
    if ($podmanCmd.Source) { $script:PodmanPath = $podmanCmd.Source } else { $script:PodmanPath = $podmanCmd.Path }
}
$sshCmd = Get-Command ssh -ErrorAction SilentlyContinue
if ($sshCmd) {
    if ($sshCmd.Source) { $script:SshPath = $sshCmd.Source } else { $script:SshPath = $sshCmd.Path }
} else {
    $script:SshPath = $null
}
$wslCmd = Get-Command wsl -ErrorAction SilentlyContinue
if ($wslCmd) {
    if ($wslCmd.Source) { $script:WslPath = $wslCmd.Source } else { $script:WslPath = $wslCmd.Path }
} else {
    $script:WslPath = $null
}

function Add-Check {
    param(
        [string]$Id,
        [string]$Name,
        [ValidateSet('PASS', 'FAIL', 'UNKNOWN', 'N/A')][string]$Status,
        [string]$Measured,
        [string]$Threshold,
        [string]$Detail,
        [string[]]$Evidence = @()
    )
    $obj = [PSCustomObject]@{
        Id        = $Id
        Name      = $Name
        Status    = $Status
        Measured  = $Measured
        Threshold = $Threshold
        Detail    = $Detail
        Evidence  = @($Evidence)
    }
    [void]$script:Results.Add($obj)
    return $obj
}

function Format-Argument {
    param([string]$Value)
    if ($Value -match '^[^\s"]*$') { return $Value }
    return '"' + ($Value -replace '"', '\"') + '"'
}

function Invoke-Cmd {
    param(
        [string]$Exe,
        [string[]]$ArgList = @(),
        [int]$TimeoutSec = 60,
        [int]$CodePage = 65001
    )
    $obj = [PSCustomObject]@{
        ExitCode = $null
        StdOut   = ''
        StdErr   = ''
        TimedOut = $false
        Error    = $null
    }
    if (-not $Exe) {
        $obj.Error = '可执行文件未指定'
        return $obj
    }
    try {
        $argStr = @($ArgList | ForEach-Object { Format-Argument ([string]$_) }) -join ' '
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $Exe
        $psi.Arguments = $argStr
        $psi.UseShellExecute = $false
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $psi.CreateNoWindow = $true
        if ($CodePage -ne 65001) {
            $enc = [System.Text.Encoding]::GetEncoding($CodePage)
            $psi.StandardOutputEncoding = $enc
            $psi.StandardErrorEncoding = $enc
        } else {
            $psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
            $psi.StandardErrorEncoding = [System.Text.Encoding]::UTF8
        }

        $proc = [System.Diagnostics.Process]::Start($psi)
        $outTask = $proc.StandardOutput.ReadToEndAsync()
        $errTask = $proc.StandardError.ReadToEndAsync()
        if (-not $proc.WaitForExit($TimeoutSec * 1000)) {
            $obj.TimedOut = $true
            try { $proc.Kill() } catch { }
            try { [void]$proc.WaitForExit(5000) } catch { }
        }
        try { $obj.ExitCode = $proc.ExitCode } catch { }
        try { $obj.StdOut = $outTask.GetAwaiter().GetResult() } catch { $obj.StdOut = '' }
        try { $obj.StdErr = $errTask.GetAwaiter().GetResult() } catch { $obj.StdErr = '' }
    } catch {
        $obj.Error = $_.Exception.Message
    }
    return $obj
}

function Invoke-Podman {
    param([string[]]$ArgList = @(), [int]$TimeoutSec = 60)
    if (-not $script:PodmanPath) {
        throw 'podman 不在 PATH 中'
    }
    return Invoke-Cmd -Exe $script:PodmanPath -ArgList $ArgList -TimeoutSec $TimeoutSec
}

function Get-DirSizeMB {
    param([string]$Path)
    if (-not $Path) { return $null }
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) { return $null }
    try {
        $files = Get-ChildItem -LiteralPath $Path -Recurse -Force -File -ErrorAction SilentlyContinue
        if (-not $files) { return 0.0 }
        $sum = ($files | Measure-Object -Property Length -Sum).Sum
        if (-not $sum) { return 0.0 }
        return ([double]$sum / 1MB)
    } catch {
        return $null
    }
}

function Get-OutputLines {
    param([string]$Text)
    if (-not $Text) { return @() }
    return @($Text -split "`r?`n" | Where-Object { $_.Trim().Length -gt 0 })
}

# =============================================================================
# C1：默认连接名
# =============================================================================
function Invoke-Check1 {
    $r = Invoke-Podman -ArgList @('system', 'connection', 'ls', '--format', 'json') -TimeoutSec $Config.CommandTimeoutSec
    if ($r.Error) {
        return Add-Check -Id 'C1' -Name '默认连接名' -Status 'UNKNOWN' -Measured 'n/a' -Threshold $Config.ExpectedDefaultConnection -Detail ("调用失败: " + $r.Error)
    }
    if ($r.TimedOut) {
        return Add-Check -Id 'C1' -Name '默认连接名' -Status 'UNKNOWN' -Measured 'n/a' -Threshold $Config.ExpectedDefaultConnection -Detail 'podman system connection ls 超时'
    }
    if ($r.ExitCode -ne 0) {
        return Add-Check -Id 'C1' -Name '默认连接名' -Status 'UNKNOWN' -Measured 'n/a' -Threshold $Config.ExpectedDefaultConnection -Detail ("podman 返回非零退出码 " + $r.ExitCode)
    }
    try {
        $parsed = $r.StdOut | ConvertFrom-Json
    } catch {
        return Add-Check -Id 'C1' -Name '默认连接名' -Status 'UNKNOWN' -Measured 'n/a' -Threshold $Config.ExpectedDefaultConnection -Detail ("JSON 解析失败: " + $_.Exception.Message)
    }
    # 注意：Windows PowerShell 5.1 的 ConvertFrom-Json 返回的是「整个数组对象」，
    # 必须显式逐元素展开，否则 @(...) 只会得到一个数组元素。
    $entries = @()
    foreach ($e in $parsed) { $entries += $e }

    $defaults = @($entries | Where-Object { $_.Default -eq $true })
    if ($defaults.Count -eq 1) {
        $script:DefaultUri = $defaults[0].URI
        if ($defaults[0].PSObject.Properties['Identity']) { $script:DefaultIdentity = $defaults[0].Identity }
    }
    $names = @($defaults | ForEach-Object { $_.Name })
    $measured = if ($names.Count -gt 0) { $names -join ', ' } else { '(无默认连接)' }
    $ok = ($defaults.Count -eq 1 -and $defaults[0].Name -eq $Config.ExpectedDefaultConnection)

    $status = if ($ok) { 'PASS' } else { 'FAIL' }
    $detail = if ($defaults.Count -eq 0) {
        '未设置默认连接，零参数 podman 行为不确定'
    } elseif ($defaults.Count -gt 1) {
        '存在多个默认连接，零参数 podman 落点不确定'
    } elseif (-not $ok) {
        "默认连接为 $($defaults[0].Name)，策略要求 $($Config.ExpectedDefaultConnection)"
    } else {
        '默认连接符合策略'
    }
    return Add-Check -Id 'C1' -Name '默认连接名' -Status $status -Measured $measured `
        -Threshold $Config.ExpectedDefaultConnection -Detail $detail -Evidence @("URI=$($script:DefaultUri)")
}

# =============================================================================
# C2：本地 machine 状态
# =============================================================================
function Invoke-Check2 {
    $r = Invoke-Podman -ArgList @('machine', 'ls', '--format', 'json') -TimeoutSec $Config.CommandTimeoutSec
    if ($r.Error -or $r.TimedOut -or $r.ExitCode -ne 0) {
        $why = if ($r.Error) { $r.Error } elseif ($r.TimedOut) { '超时' } else { "退出码 $($r.ExitCode)" }
        return Add-Check -Id 'C2' -Name '本地 machine 状态' -Status 'UNKNOWN' -Measured 'n/a' -Threshold '全部 stopped' -Detail ("podman machine ls 失败: " + $why)
    }
    try {
        $parsedMachines = $r.StdOut | ConvertFrom-Json
    } catch {
        return Add-Check -Id 'C2' -Name '本地 machine 状态' -Status 'UNKNOWN' -Measured 'n/a' -Threshold '全部 stopped' -Detail ("JSON 解析失败: " + $_.Exception.Message)
    }
    $machines = @()
    foreach ($e in $parsedMachines) { $machines += $e }

    $parts = @()
    $bad = 0
    foreach ($m in $machines) {
        $state = 'stopped'
        if ($m.Running -eq $true) { $state = 'running' }
        elseif ($m.Starting -eq $true) { $state = 'starting' }
        if ($state -ne 'stopped') { $bad = $bad + 1 }
        $parts += ("{0}={1}" -f $m.Name, $state)
    }

    if ($machines.Count -eq 0) {
        return Add-Check -Id 'C2' -Name '本地 machine 状态' -Status 'PASS' -Measured '(无本地 machine)' -Threshold '全部 stopped' -Detail '本地无 machine，天然不占用本地存储'
    }
    $status = if ($bad -eq 0) { 'PASS' } else { 'FAIL' }
    $detail = if ($bad -eq 0) { '全部 machine 处于 stopped（本审计不启动任何 machine）' } else { "$bad 个 machine 处于运行/启动中，会占用本地存储与本地 socket" }
    return Add-Check -Id 'C2' -Name '本地 machine 状态' -Status $status -Measured ($parts -join '; ') `
        -Threshold '全部 stopped' -Detail $detail
}

# =============================================================================
# C3：零参数 podman 的实际落点
# =============================================================================
function Invoke-Check3 {
    $r = Invoke-Podman -ArgList @('info', '--format', 'json') -TimeoutSec $Config.CommandTimeoutSec
    if ($r.Error -or $r.TimedOut -or $r.ExitCode -ne 0) {
        $why = if ($r.Error) { $r.Error } elseif ($r.TimedOut) { '超时（远端可能不可达）' } else { "退出码 $($r.ExitCode)" }
        return Add-Check -Id 'C3' -Name '零参数 podman 落点' -Status 'UNKNOWN' -Measured 'n/a' -Threshold '远端 Linux 服务 (serviceIsRemote=true)' -Detail ("podman info 失败: " + $why)
    }
    try {
        $info = $r.StdOut | ConvertFrom-Json
    } catch {
        return Add-Check -Id 'C3' -Name '零参数 podman 落点' -Status 'UNKNOWN' -Measured 'n/a' -Threshold '远端 Linux 服务 (serviceIsRemote=true)' -Detail ("JSON 解析失败: " + $_.Exception.Message)
    }

    $serviceIsRemote = $false
    if ($info.host.PSObject.Properties['serviceIsRemote']) { $serviceIsRemote = [bool]$info.host.serviceIsRemote }
    $script:GraphRoot = $info.store.graphRoot
    $hostname = $info.host.hostname
    $socketPath = ''
    if ($info.host.PSObject.Properties['remoteSocket'] -and $info.host.remoteSocket -and $info.host.remoteSocket.PSObject.Properties['path']) {
        $socketPath = [string]$info.host.remoteSocket.path
    }
    $script:RemoteSocket = $socketPath

    $localName = [System.Net.Dns]::GetHostName()
    $graphRootPosix = -not ($script:GraphRoot -match '^[A-Za-z]:')
    $hostnameDiffers = ($hostname -ne $localName)

    # 追加证据：默认连接 URI 与 info 报告的用户运行目录 uid 是否一致
    $uidFromConn = $null
    $uidFromInfo = $null
    if ($script:DefaultUri -and $script:DefaultUri -match '/run/user/(\d+)') { $uidFromConn = $Matches[1] }
    if ($socketPath -and $socketPath -match '/run/user/(\d+)') { $uidFromInfo = $Matches[1] }
    $uidConsistent = $true
    if ($uidFromConn -and $uidFromInfo) { $uidConsistent = ($uidFromConn -eq $uidFromInfo) }

    $ok = ($serviceIsRemote -and $graphRootPosix -and $hostnameDiffers -and $uidConsistent)
    $status = if ($ok) { 'PASS' } else { 'FAIL' }
    $detail = if ($ok) {
        'info 明确报告 serviceIsRemote=true，graphRoot 为远端 POSIX 路径，且主机名不等于本机'
    } else {
        $reasons = @()
        if (-not $serviceIsRemote) { $reasons += 'serviceIsRemote 不为 true' }
        if (-not $graphRootPosix) { $reasons += 'graphRoot 为 Windows 盘符路径' }
        if (-not $hostnameDiffers) { $reasons += 'hostname 与本机相同' }
        if (-not $uidConsistent) { $reasons += "默认连接 uid($uidFromConn) 与 info uid($uidFromInfo) 不一致" }
        '落点证据不足: ' + ($reasons -join '；')
    }

    $measured = "hostname=$hostname, serviceIsRemote=$serviceIsRemote, graphRoot=$($script:GraphRoot)"
    return Add-Check -Id 'C3' -Name '零参数 podman 落点' -Status $status -Measured $measured `
        -Threshold 'serviceIsRemote=true + 远端 POSIX graphRoot + hostname≠本机' -Detail $detail `
        -Evidence @("本机 hostname=$localName", "remoteSocket=$socketPath", "默认连接 uid=$uidFromConn / info uid=$uidFromInfo")
}

# =============================================================================
# C4：本地容器存储体积
# =============================================================================
function Invoke-Check4 {
    $roots = New-Object System.Collections.ArrayList
    foreach ($p in $Config.LocalStorageRootCandidates) {
        if ($p) { [void]$roots.Add([System.IO.Path]::GetFullPath($p)) }
    }
    if ($script:PodmanPath) {
        $r = Invoke-Podman -ArgList @('machine', 'inspect') -TimeoutSec $Config.CommandTimeoutSec
        if (-not $r.Error -and -not $r.TimedOut -and $r.ExitCode -eq 0) {
            try {
                $parsedInspect = $r.StdOut | ConvertFrom-Json
                foreach ($m in $parsedInspect) {
                    if ($m.ConfigDir -and $m.ConfigDir.Path) {
                        [void]$roots.Add([System.IO.Path]::GetFullPath([string]$m.ConfigDir.Path))
                    }
                }
            } catch { }
        }
    }

    # 去重：按长度升序，若当前路径已被更上层路径覆盖则跳过
    $unique = New-Object System.Collections.ArrayList
    $sorted = @($roots | Sort-Object -Property Length)
    foreach ($p in $sorted) {
        $covered = $false
        foreach ($u in $unique) {
            if ($p.ToLowerInvariant().StartsWith($u.ToLowerInvariant().TrimEnd('\') + '\')) { $covered = $true; break }
        }
        if (-not $covered) { [void]$unique.Add($p) }
    }

    $parts = @()
    $total = 0.0
    $missing = 0
    foreach ($p in $unique) {
        if (-not (Test-Path -LiteralPath $p -PathType Container)) { continue }
        $mb = Get-DirSizeMB -Path $p
        if ($null -eq $mb) { $missing = $missing + 1; continue }
        $total = $total + $mb
        $parts += ("{0}={1:N1}MB" -f $p, $mb)
    }
    $totalRounded = [math]::Round($total, 1)
    if ($parts.Count -eq 0) { $parts = @('(候选目录均不存在)') }

    $status = if ($total -gt $Config.MaxLocalStorageMB) { 'FAIL' } else { 'PASS' }
    $detail = if ($status -eq 'FAIL') {
        "本地容器存储合计 $totalRounded MB 超过上限 $($Config.MaxLocalStorageMB) MB，应清理本地镜像/容器/缓存"
    } else {
        "本地容器存储合计 $totalRounded MB，未超过上限 $($Config.MaxLocalStorageMB) MB"
    }
    if ($missing -gt 0) { $detail = $detail + "；$missing 个候选路径无法读取（未计入）" }

    return Add-Check -Id 'C4' -Name '本地容器存储体积' -Status $status -Measured ("总计 " + $totalRounded + ' MB') `
        -Threshold ("<= " + $Config.MaxLocalStorageMB + ' MB') -Detail $detail -Evidence $parts
}

# =============================================================================
# C5：本地遗留归档扫描
# =============================================================================
function Test-KnownMachineArtifact {
    param([string]$Path)
    foreach ($pat in $Config.KnownMachineArtifactPatterns) {
        if ($Path -like $pat) { return $true }
    }
    return $false
}

function Test-C9OwnedPath {
    param([string]$Path)
    foreach ($p in $Config.WslOwnedByC9Paths) {
        if ($Path -ieq $p) { return $true }
    }
    return $false
}

function Get-LeftoverFiles {
    param([string]$Root, [int]$MaxDepth)
    $found = New-Object System.Collections.ArrayList
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return $found }
    $queue = New-Object System.Collections.Queue
    $queue.Enqueue([PSCustomObject]@{ Path = $Root; Depth = 0 })
    while ($queue.Count -gt 0) {
        $node = $queue.Dequeue()
        $entries = @(Get-ChildItem -LiteralPath $node.Path -Force -ErrorAction SilentlyContinue)
        foreach ($e in $entries) {
            if ($e.PSIsContainer) {
                $skip = ($Config.SkipDirectoryNames -contains $e.Name)
                if (-not $skip -and $node.Depth -lt $MaxDepth) {
                    $queue.Enqueue([PSCustomObject]@{ Path = $e.FullName; Depth = ($node.Depth + 1) })
                }
                continue
            }
            foreach ($pat in $Config.LeftoverNamePatterns) {
                if ($e.Name -like $pat) {
                    [void]$found.Add([PSCustomObject]@{ Path = $e.FullName; SizeMB = [math]::Round($e.Length / 1MB, 1) })
                    break
                }
            }
        }
    }
    return $found
}

function Invoke-Check5 {
    $all = New-Object System.Collections.ArrayList
    foreach ($root in $Config.LeftoverScanRoots) {
        $items = Get-LeftoverFiles -Root $root.Path -MaxDepth $root.MaxDepth
        foreach ($i in $items) { [void]$all.Add($i) }
    }

    $unexpected = @($all | Where-Object { -not (Test-KnownMachineArtifact -Path $_.Path) -and -not (Test-C9OwnedPath -Path $_.Path) })
    $known = @($all | Where-Object { Test-KnownMachineArtifact -Path $_.Path })
    $c9Owned = @($all | Where-Object { Test-C9OwnedPath -Path $_.Path })
    $unexpectedMB = 0.0
    foreach ($u in $unexpected) { $unexpectedMB = $unexpectedMB + $u.SizeMB }
    $knownMB = 0.0
    foreach ($k in $known) { $knownMB = $knownMB + $k.SizeMB }

    $evidence = @()
    foreach ($u in $unexpected) { $evidence += ("{0} ({1} MB)" -f $u.Path, $u.SizeMB) }
    foreach ($k in $known) { $evidence += ("[machine 缓存] {0} ({1} MB)" -f $k.Path, $k.SizeMB) }
    foreach ($o in $c9Owned) { $evidence += ("[C9 管辖，单独计量] {0} ({1} MB)" -f $o.Path, $o.SizeMB) }

    $status = if ($unexpected.Count -gt 0) { 'FAIL' } else { 'PASS' }
    $detail = if ($status -eq 'FAIL') {
        "发现 $($unexpected.Count) 个疑似本地镜像归档（合计 $([math]::Round($unexpectedMB,1)) MB），应改为远端存储或删除"
    } else {
        "未发现残留归档；$($known.Count) 个已知 machine 基础镜像产物（合计 $([math]::Round($knownMB,1)) MB）不计为违规"
    }
    return Add-Check -Id 'C5' -Name '本地遗留归档扫描' -Status $status `
        -Measured ("unexpected=$($unexpected.Count), known=$($known.Count)") `
        -Threshold 'unexpected=0' -Detail $detail -Evidence $evidence
}

# =============================================================================
# C6：D:\WSL 残留体积
# =============================================================================
function Invoke-Check6 {
    $root = $Config.WslResidualRoot
    if (-not (Test-Path -LiteralPath $root -PathType Container)) {
        return Add-Check -Id 'C6' -Name 'D:\WSL 残留体积' -Status 'PASS' -Measured '(目录不存在)' -Threshold ("<= " + $Config.MaxWslResidualMB + ' MB') -Detail "$root 不存在，无本地 WSL 残留"
    }
    $totalMB = Get-DirSizeMB -Path $root
    if ($null -eq $totalMB) {
        return Add-Check -Id 'C6' -Name 'D:\WSL 残留体积' -Status 'UNKNOWN' -Measured 'n/a' -Threshold ("<= " + $Config.MaxWslResidualMB + ' MB') -Detail "$root 无法读取"
    }
    $excludedMB = 0.0
    foreach ($p in $Config.WslResidualExcludePaths) {
        if (Test-Path -LiteralPath $p -PathType Leaf) {
            $excludedMB = $excludedMB + ((Get-Item -LiteralPath $p -Force).Length / 1MB)
        }
    }
    $totalMB = $totalMB - $excludedMB
    $totalMB = [math]::Round($totalMB, 1)
    $evidence = @()
    foreach ($child in @(Get-ChildItem -LiteralPath $root -Force -Directory -ErrorAction SilentlyContinue)) {
        $mb = Get-DirSizeMB -Path $child.FullName
        if ($null -ne $mb) {
            $sub = 0.0
            foreach ($p in $Config.WslResidualExcludePaths) {
                if ($p.StartsWith($child.FullName.TrimEnd('\') + '\', [System.StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $p -PathType Leaf)) {
                    $sub = $sub + ((Get-Item -LiteralPath $p -Force).Length / 1MB)
                }
            }
            $evidence += ("{0}={1:N1}MB" -f $child.Name, ($mb - $sub))
        }
    }
    if ($excludedMB -gt 0) {
        $evidence += ("[已知 WSL 资产已排除] {0:N1} MB" -f $excludedMB)
    }
    $pct = if ($Config.MaxWslResidualMB -gt 0) { [math]::Round(($totalMB / $Config.MaxWslResidualMB) * 100) } else { 0 }
    $status = if ($totalMB -gt $Config.MaxWslResidualMB) { 'FAIL' } else { 'PASS' }
    $detail = if ($status -eq 'FAIL') {
        "$root 占用 $totalMB MB，超过上限 $($Config.MaxWslResidualMB) MB"
    } else {
        "$root 占用 $totalMB MB（占上限 $pct%），在阈值内"
    }
    return Add-Check -Id 'C6' -Name 'D:\WSL 残留体积' -Status $status -Measured "$totalMB MB" `
        -Threshold ("<= " + $Config.MaxWslResidualMB + ' MB') -Detail $detail -Evidence $evidence
}

# =============================================================================
# C7：远端 graphroot 可用空间
# =============================================================================
function Invoke-Check7 {
    if (-not $script:GraphRoot) {
        return Add-Check -Id 'C7' -Name '远端 graphroot 可用空间' -Status 'UNKNOWN' -Measured 'n/a' -Threshold (">= " + $Config.MinRemoteFreeGiB + ' GiB') -Detail '缺少 graphroot（C3 未成功取得 podman info）'
    }
    if (-not $script:DefaultUri) {
        return Add-Check -Id 'C7' -Name '远端 graphroot 可用空间' -Status 'UNKNOWN' -Measured 'n/a' -Threshold (">= " + $Config.MinRemoteFreeGiB + ' GiB') -Detail '缺少默认连接 URI（C1 未成功）'
    }
    $m = [regex]::Match($script:DefaultUri, '^ssh://(?<user>[^@/]+)@(?<host>[^:/]+)(?::(?<port>\d+))?')
    if (-not $m.Success) {
        return Add-Check -Id 'C7' -Name '远端 graphroot 可用空间' -Status 'UNKNOWN' -Measured 'n/a' -Threshold (">= " + $Config.MinRemoteFreeGiB + ' GiB') -Detail "默认连接不是 ssh:// 形式，无法远程 df：$($script:DefaultUri)"
    }
    if (-not $script:SshPath) {
        return Add-Check -Id 'C7' -Name '远端 graphroot 可用空间' -Status 'UNKNOWN' -Measured 'n/a' -Threshold (">= " + $Config.MinRemoteFreeGiB + ' GiB') -Detail 'ssh 不在 PATH 中，无法远程 df'
    }

    $user = $m.Groups['user'].Value
    $hostName = $m.Groups['host'].Value
    $port = $m.Groups['port'].Value
    $remoteCmd = "df -B1 --output=avail,target '$($script:GraphRoot)'"
    $sshArgs = @('-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8')
    if ($script:DefaultIdentity -and (Test-Path -LiteralPath $script:DefaultIdentity)) {
        $sshArgs += @('-i', $script:DefaultIdentity)
    }
    if ($port) { $sshArgs += @('-p', $port) }
    $sshArgs += @(("{0}@{1}" -f $user, $hostName), $remoteCmd)

    $r = Invoke-Cmd -Exe $script:SshPath -ArgList $sshArgs -TimeoutSec $Config.SshTimeoutSec
    if ($r.Error -or $r.TimedOut -or $r.ExitCode -ne 0) {
        $why = if ($r.Error) { $r.Error } elseif ($r.TimedOut) { '超时' } else { ("退出码 $($r.ExitCode): " + (($r.StdErr) -replace "`r?`n", ' ').Trim()) }
        return Add-Check -Id 'C7' -Name '远端 graphroot 可用空间' -Status 'UNKNOWN' -Measured 'n/a' -Threshold (">= " + $Config.MinRemoteFreeGiB + ' GiB') -Detail ("远程 df 失败: " + $why)
    }

    $lines = Get-OutputLines -Text $r.StdOut
    if ($lines.Count -eq 0) {
        return Add-Check -Id 'C7' -Name '远端 graphroot 可用空间' -Status 'UNKNOWN' -Measured 'n/a' -Threshold (">= " + $Config.MinRemoteFreeGiB + ' GiB') -Detail '远程 df 无输出'
    }
    $last = $lines[$lines.Count - 1]
    $fields = @($last -split '\s+')
    $availBytes = 0
    if (-not [int64]::TryParse($fields[0], [ref]$availBytes)) {
        return Add-Check -Id 'C7' -Name '远端 graphroot 可用空间' -Status 'UNKNOWN' -Measured $last -Threshold (">= " + $Config.MinRemoteFreeGiB + ' GiB') -Detail '远程 df 输出无法解析'
    }
    $target = ''
    if ($fields.Count -gt 1) { $target = ($fields[1..($fields.Count - 1)] -join ' ') }
    $freeGiB = [math]::Round(($availBytes / 1073741824), 1)

    $status = if ($freeGiB -lt $Config.MinRemoteFreeGiB) { 'FAIL' } else { 'PASS' }
    $detail = if ($status -eq 'FAIL') {
        "graphroot 所在文件系统仅剩 $freeGiB GiB，低于低水位 $($Config.MinRemoteFreeGiB) GiB"
    } else {
        "graphroot 所在文件系统可用 $freeGiB GiB，高于低水位 $($Config.MinRemoteFreeGiB) GiB"
    }
    return Add-Check -Id 'C7' -Name '远端 graphroot 可用空间' -Status $status -Measured "$freeGiB GiB 可用" `
        -Threshold (">= " + $Config.MinRemoteFreeGiB + ' GiB') -Detail $detail `
        -Evidence @("graphRoot=$($script:GraphRoot)", "df target=$target", "ssh=$user@$hostName")
}

# =============================================================================
# C8：连接覆盖类环境变量
# =============================================================================
function Invoke-Check8 {
    $names = @('CONTAINER_HOST', 'DOCKER_HOST', 'CONTAINER_CONNECTION')
    $set = @()
    $persisted = @()
    foreach ($n in $names) {
        $v = [Environment]::GetEnvironmentVariable($n, 'Process')
        if ($v) { $set += ("{0}={1}" -f $n, $v) }
        $uv = [Environment]::GetEnvironmentVariable($n, 'User')
        $mv = [Environment]::GetEnvironmentVariable($n, 'Machine')
        if ($uv) { $persisted += ("User:{0}={1}" -f $n, $uv) }
        if ($mv) { $persisted += ("Machine:{0}={1}" -f $n, $mv) }
    }

    $evidence = @()
    foreach ($s in $set) { $evidence += ("进程环境 " + $s) }
    foreach ($p in $persisted) { $evidence += ("持久化 " + $p) }
    if ($evidence.Count -eq 0) { $evidence = @('进程环境与持久化层均未设置') }

    $status = if ($set.Count -gt 0) { 'FAIL' } else { 'PASS' }
    $measured = if ($set.Count -gt 0) { $set -join '; ' } else { '全部未设置' }
    $detail = if ($status -eq 'FAIL') {
        '检测到会绕过连接锁定的环境变量，零参数 podman 可能落到非预期端点'
    } elseif ($persisted.Count -gt 0) {
        '当前进程未设置；但持久化层存在同名变量，新开会话会重新注入'
    } else {
        '连接覆盖类环境变量未设置'
    }
    return Add-Check -Id 'C8' -Name '连接覆盖类环境变量' -Status $status -Measured $measured `
        -Threshold 'CONTAINER_HOST/DOCKER_HOST/CONTAINER_CONNECTION 均未设置' -Detail $detail -Evidence $evidence
}

# =============================================================================
# C9：WSL VHDX 体积
# =============================================================================
function Get-WslDistroList {
    if (-not $script:WslPath) { return $null }
    $r = Invoke-Cmd -Exe $script:WslPath -ArgList @('--list', '--quiet') -TimeoutSec $Config.SshTimeoutSec
    if ($r.Error -or $r.TimedOut) { return $null }
    # wsl.exe 可能输出含 NUL 的 UTF-16 字节流，按 UTF-8 解码后去掉 NUL 即可还原 ASCII 名称
    $text = ($r.StdOut -replace "`0", '')
    $names = @($text -split "`r?`n" | ForEach-Object { $_.Trim() } | Where-Object { $_.Length -gt 0 })
    $errText = ((($r.StdErr -replace "`0", '') -replace "`r?`n", ' ').Trim())
    return [PSCustomObject]@{
        Names    = $names
        ExitCode = $r.ExitCode
        StdErr   = $errText
    }
}

function Invoke-Check9 {
    $name = $Config.WslDistroName
    $threshold = ("<= " + $Config.MaxWslVhdxGiB + ' GiB')
    $sampledAt = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')

    if (-not $script:WslPath) {
        return Add-Check -Id 'C9' -Name 'WSL VHDX 体积' -Status 'UNKNOWN' -Measured 'n/a' `
            -Threshold $threshold -Detail 'wsl.exe 不在 PATH 中，无法测量 VHDX'
    }

    $list = Get-WslDistroList
    if ($null -eq $list) {
        return Add-Check -Id 'C9' -Name 'WSL VHDX 体积' -Status 'UNKNOWN' -Measured 'n/a' `
            -Threshold $threshold -Detail 'wsl --list --quiet 执行失败或超时'
    }

    $script:WslDistroExists = ($list.Names -contains $name)
    if (-not $script:WslDistroExists) {
        $detail = ("发行版 $name 不存在（wsl --list 未列出），视为合法状态，不制造告警")
        if ($list.StdErr) { $detail = $detail + "；wsl 提示: $($list.StdErr)" }
        return Add-Check -Id 'C9' -Name 'WSL VHDX 体积' -Status 'N/A' -Measured '(发行版不存在)' `
            -Threshold $threshold -Detail $detail -Evidence @("采样时刻=$sampledAt")
    }

    $path = $Config.WslVhdxPath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        return Add-Check -Id 'C9' -Name 'WSL VHDX 体积' -Status 'UNKNOWN' -Measured '(VHDX 未找到)' `
            -Threshold $threshold -Detail ("发行版存在于列表，但 $path 不存在，无法测量") `
            -Evidence @("采样时刻=$sampledAt")
    }
    try {
        $bytes = [int64](Get-Item -LiteralPath $path -Force).Length
    } catch {
        return Add-Check -Id 'C9' -Name 'WSL VHDX 体积' -Status 'UNKNOWN' -Measured 'n/a' `
            -Threshold $threshold -Detail ("读取 VHDX 大小失败: " + $_.Exception.Message) `
            -Evidence @("采样时刻=$sampledAt")
    }

    $sizeGiB = [math]::Round(($bytes / 1073741824), 3)
    $deltaBytes = [int64]($bytes - $Config.WslVhdxBaselineBytes)
    $deltaGiB = [math]::Round(($deltaBytes / 1073741824), 3)
    $maxBytes = [int64]($Config.MaxWslVhdxGiB * 1073741824)

    # sparse 状态：优先 wsl --get-sparse；该子命令在部分 WSL 版本不可用时回退 fsutil
    $sparseRaw = ''
    $sparseSource = ''
    $sr = Invoke-Cmd -Exe $script:WslPath -ArgList @('--manage', $name, '--get-sparse') -TimeoutSec $Config.SshTimeoutSec
    if (-not $sr.Error -and -not $sr.TimedOut -and $sr.ExitCode -eq 0) {
        $sparseRaw = ((($sr.StdOut -replace "`0", '') -replace "`r?`n", ' ').Trim())
        $sparseSource = 'wsl --get-sparse'
        $low = $sparseRaw.ToLowerInvariant()
        if ($low -match 'disabled|not enabled|false|关闭|未启用|已禁用') {
            $script:SparseEnabled = $false
        } elseif ($low -match 'enabled|true|开启|已启用') {
            $script:SparseEnabled = $true
        }
    } else {
        $fsutilPath = Join-Path $env:SystemRoot 'System32\fsutil.exe'
        if (Test-Path -LiteralPath $fsutilPath -PathType Leaf) {
            $fr = Invoke-Cmd -Exe $fsutilPath -ArgList @('sparse', 'queryflag', $path) -TimeoutSec $Config.SshTimeoutSec -CodePage ([int](Get-Culture).TextInfo.ANSICodePage)
            if (-not $fr.Error -and -not $fr.TimedOut -and $fr.ExitCode -eq 0) {
                $sparseRaw = ((($fr.StdOut -replace "`0", '') -replace "`r?`n", ' ').Trim())
                $sparseSource = 'fsutil（wsl --get-sparse 不可用）'
                $low = $sparseRaw.ToLowerInvariant()
                if ($low -match 'not a sparse|非稀疏|不是稀疏') {
                    $script:SparseEnabled = $false
                } elseif ($low -match 'sparse|稀疏') {
                    $script:SparseEnabled = $true
                }
            }
        }
    }
    $sparseText = if ([string]::IsNullOrEmpty($sparseSource)) {
        'sparse=(查询失败)'
    } elseif ($null -eq $script:SparseEnabled) {
        "sparse=未知($sparseRaw)"
    } else {
        "sparse=$($script:SparseEnabled) [$sparseSource]"
    }

    $status = if ($bytes -gt $maxBytes) { 'FAIL' } else { 'PASS' }
    $deltaText = if ($deltaBytes -ge 0) { "+$deltaGiB GiB" } else { "$deltaGiB GiB" }
    $detail = if ($status -eq 'FAIL') {
        "VHDX 为 $sizeGiB GiB，超过上限 $($Config.MaxWslVhdxGiB) GiB（相对基线 $deltaText）"
    } else {
        "VHDX 为 $sizeGiB GiB，未超过上限 $($Config.MaxWslVhdxGiB) GiB（相对基线 $deltaText）"
    }
    $measured = "$sizeGiB GiB ($bytes B), 相对基线 $deltaText, $sparseText"
    return Add-Check -Id 'C9' -Name 'WSL VHDX 体积' -Status $status -Measured $measured `
        -Threshold ("$threshold（基线 " + ([math]::Round(($Config.WslVhdxBaselineBytes / 1073741824), 3)) + ' GiB）') `
        -Detail $detail -Evidence @("path=$path", "采样时刻=$sampledAt", "sparse 原始输出=$sparseRaw")
}

# =============================================================================
# C10：WSL 共享盘挂载
# =============================================================================
function Get-WslMountEntries {
    param([string]$Distro)
    $r = Invoke-Cmd -Exe $script:WslPath -ArgList @('-d', $Distro, '--', 'cat', '/proc/mounts') -TimeoutSec $Config.CommandTimeoutSec
    if ($r.Error -or $r.TimedOut -or $r.ExitCode -ne 0) {
        $why = if ($r.Error) { $r.Error } elseif ($r.TimedOut) { '超时' } else { "退出码 $($r.ExitCode)" }
        return [PSCustomObject]@{ Entries = @(); Error = $why }
    }
    $entries = @()
    foreach ($line in (Get-OutputLines -Text ($r.StdOut -replace "`0", ''))) {
        $f = @($line -split '\s+')
        if ($f.Count -lt 4) { continue }
        $src = ($f[0] -replace '\\040', ' ').Replace('\134', '\')
        $mp = ($f[1] -replace '\\040', ' ').Replace('\134', '\')
        $ft = $f[2]
        $opts = $f[3]
        $isShare = $false
        if ($ft -eq 'drvfs' -or $ft -eq 'cifs') {
            $isShare = $true
        } elseif ($ft -eq '9p' -and ($src -match 'drvfs' -or $opts -match 'drvfs')) {
            $isShare = $true
        }
        $entries += [PSCustomObject]@{
            Source     = $src
            MountPoint = $mp
            FsType     = $ft
            Options    = $opts
            IsShare    = $isShare
        }
    }
    return [PSCustomObject]@{ Entries = $entries; Error = $null }
}

function Test-WslMountWritable {
    param([string]$Distro, [string]$MountPoint)

    # 零字节可写性探测：touch 后立即 rm，不写大文件
    $probeName = '.podman-audit-probe-' + ([System.Guid]::NewGuid().ToString('N').Substring(0, 8))
    $probePath = $MountPoint.TrimEnd('/') + '/' + $probeName
    $tr = Invoke-Cmd -Exe $script:WslPath -ArgList @('-d', $Distro, '--', 'touch', $probePath) -TimeoutSec $Config.CommandTimeoutSec
    $rmExit = $null
    if (-not $tr.Error -and -not $tr.TimedOut -and $tr.ExitCode -eq 0) {
        $rr = Invoke-Cmd -Exe $script:WslPath -ArgList @('-d', $Distro, '--', 'rm', '-f', $probePath) -TimeoutSec $Config.CommandTimeoutSec
        if (-not $rr.Error -and -not $rr.TimedOut) { $rmExit = $rr.ExitCode }
    }

    $writeFailed = [bool]($tr.Error -or $tr.TimedOut -or $tr.ExitCode -ne 0)
    $why = ''
    if ($writeFailed) {
        $errText = ((($tr.StdErr -replace "`0", '') -replace "`r?`n", ' ').Trim())
        $why = if ($tr.Error) { $tr.Error } elseif ($tr.TimedOut) { '超时' } else { ("touch 退出码 $($tr.ExitCode): " + $errText) }
    } elseif ($null -eq $rmExit -or $rmExit -ne 0) {
        $why = ("探测文件已创建但清理失败（rm 退出码 $rmExit）")
    }

    return [PSCustomObject]@{
        Ok        = [bool](-not $writeFailed -and $rmExit -eq 0)
        ProbePath = $probePath
        Residue   = [bool](-not $writeFailed -and ($null -eq $rmExit -or $rmExit -ne 0))
        Why       = $why
    }
}

function Test-RootLevelMountPoint {
    param([string]$MountPoint)
    # 根目录级挂载：/mnt 本身或 /mnt/<单段>（如 /mnt/c、/mnt/d）。这类挂载点落在
    # Windows 盘根，写入通常需要管理员权限，纳入可写候选只会制造假告警。
    if ($MountPoint -match '^/mnt$') { return $true }
    if ($MountPoint -match '^/mnt/[^/]+$') { return $true }
    return $false
}

function Invoke-Check10 {
    $name = $Config.WslDistroName
    $threshold = ("候选挂载点（" + ($Config.WslMountPoints -join ' / ') + "）之一为 drvfs/cifs 且可写")
    $sampledAt = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')

    if (-not $script:WslPath) {
        return Add-Check -Id 'C10' -Name 'WSL 共享盘挂载' -Status 'UNKNOWN' -Measured 'n/a' `
            -Threshold $threshold -Detail 'wsl.exe 不在 PATH 中，无法检查发行版内挂载'
    }
    if (-not $script:WslDistroExists) {
        # 可能 C9 之前未能列出；此处再确认一次
        $list = Get-WslDistroList
        if ($null -eq $list) {
            return Add-Check -Id 'C10' -Name 'WSL 共享盘挂载' -Status 'UNKNOWN' -Measured 'n/a' `
                -Threshold $threshold -Detail 'wsl --list --quiet 执行失败或超时'
        }
        $script:WslDistroExists = ($list.Names -contains $name)
        if (-not $script:WslDistroExists) {
            return Add-Check -Id 'C10' -Name 'WSL 共享盘挂载' -Status 'N/A' -Measured '(发行版不存在)' `
                -Threshold $threshold -Detail ("发行版 $name 不存在，无法检查挂载，视为合法状态") `
                -Evidence @("采样时刻=$sampledAt")
        }
    }

    $mount = Get-WslMountEntries -Distro $name
    if ($mount.Error) {
        return Add-Check -Id 'C10' -Name 'WSL 共享盘挂载' -Status 'UNKNOWN' -Measured 'n/a' `
            -Threshold $threshold -Detail ("读取 /proc/mounts 失败: " + $mount.Error) `
            -Evidence @("采样时刻=$sampledAt")
    }

    $entries = @($mount.Entries)
    $shares = @($entries | Where-Object { $_.IsShare })
    $evidence = @()
    foreach ($s in $shares) { $evidence += ("share {0} <- {1} [{2}]" -f $s.MountPoint, $s.Source, $s.FsType) }
    if ($evidence.Count -eq 0) { $evidence = @('未发现 drvfs/cifs 挂载') }

    # 候选构造：配置常量按列表顺序优先（过渡期 /media/pc/data/ai 与旧布局
    # /media/pc/data 同时接受）；常量均未命中且允许自动发现时，追加其余 drvfs/cifs
    # 挂载，但排除根目录级挂载。所有候选逐个做可写探测，取首个可写者。
    $candidates = @()
    $pickSources = @()
    $notes = @()
    foreach ($mp in $Config.WslMountPoints) {
        $hit = @($entries | Where-Object { $_.MountPoint -eq $mp })
        if ($hit.Count -eq 0) {
            $notes += ("[常量未挂载] " + $mp)
        } elseif ($hit[0].IsShare) {
            $candidates += $hit[0]
            $pickSources += '常量'
        } else {
            $notes += ("[常量类型不符] {0} 为 {1}" -f $mp, $hit[0].FsType)
        }
    }
    if ($Config.EnableWslMountAutodiscover) {
        foreach ($s in $shares) {
            if (Test-RootLevelMountPoint -MountPoint $s.MountPoint) {
                $notes += ("[根目录级挂载，已排除] {0} <- {1} [{2}]" -f $s.MountPoint, $s.Source, $s.FsType)
                continue
            }
            $dup = $false
            foreach ($c in $candidates) { if ($c.MountPoint -eq $s.MountPoint) { $dup = $true } }
            if (-not $dup) {
                $candidates += $s
                $pickSources += '自动发现'
            }
        }
    } else {
        $notes += '[自动发现已禁用]'
    }

    if ($candidates.Count -eq 0) {
        $detail = ("常量候选（" + ($Config.WslMountPoints -join ' / ') + "）均未命中，且无可用自动发现候选")
        return Add-Check -Id 'C10' -Name 'WSL 共享盘挂载' -Status 'FAIL' -Measured '(不可用)' `
            -Threshold $threshold -Detail $detail -Evidence @((("采样时刻=" + $sampledAt)) + $notes + $evidence)
    }

    $target = $null
    $sourceOfPick = ''
    $probe = $null
    $skipped = @()
    for ($i = 0; $i -lt $candidates.Count; $i++) {
        $cand = $candidates[$i]
        $pr = Test-WslMountWritable -Distro $name -MountPoint $cand.MountPoint
        if ($pr.Residue) {
            $measured = ("mount={0} ({1}, {2}), 来源={3}, writable=True(清理失败)" -f $cand.MountPoint, $cand.FsType, $cand.Source, $pickSources[$i])
            $ev = @((("采样时刻=" + $sampledAt)), ("探测路径=" + $pr.ProbePath))
            return Add-Check -Id 'C10' -Name 'WSL 共享盘挂载' -Status 'UNKNOWN' -Measured $measured `
                -Threshold $threshold -Detail ("挂载可写但清理失败，无法确认无残留: " + $pr.Why) -Evidence @($ev + $notes + $evidence)
        }
        if ($pr.Ok) {
            $target = $cand
            $sourceOfPick = $pickSources[$i]
            $probe = $pr
            break
        }
        $skipped += ("[不可写] {0} ({1}) <- {2}: {3}" -f $cand.MountPoint, $cand.FsType, $cand.Source, $pr.Why)
    }

    $measured0 = ("mount={0} ({1}, {2}), 来源={3}, writable=False" -f $candidates[0].MountPoint, $candidates[0].FsType, $candidates[0].Source, $pickSources[0])
    if (-not $target) {
        $detail = ("候选挂载均不可写（共 {0} 个）: {1}" -f $candidates.Count, $skipped[0])
        return Add-Check -Id 'C10' -Name 'WSL 共享盘挂载' -Status 'FAIL' -Measured $measured0 `
            -Threshold $threshold -Detail $detail -Evidence @((("采样时刻=" + $sampledAt)) + $skipped + $notes + $evidence)
    }

    $measured = ("mount={0} ({1}, {2}), 来源={3}, writable=True" -f $target.MountPoint, $target.FsType, $target.Source, $sourceOfPick)
    $ev = @((("采样时刻=" + $sampledAt)), ("探测路径=" + $probe.ProbePath))
    $ev = @($ev + $skipped + $notes + $evidence)

    $detail = if ($sourceOfPick -eq '常量') {
        "$($target.MountPoint) 为 drvfs/cifs 挂载（常量候选命中），零字节写入与清理均成功"
    } else {
        "常量候选均未命中，自动发现可用共享挂载 $($target.MountPoint)，零字节写入与清理均成功"
    }
    return Add-Check -Id 'C10' -Name 'WSL 共享盘挂载' -Status 'PASS' -Measured $measured `
        -Threshold $threshold -Detail $detail -Evidence $ev
}

# =============================================================================
# 执行
# =============================================================================
function Invoke-CheckSafely {
    param([string]$Id, [string]$Name, [scriptblock]$Body)
    try {
        $result = & $Body
        if ($null -eq $result) {
            return Add-Check -Id $Id -Name $Name -Status 'UNKNOWN' -Measured 'n/a' -Threshold 'n/a' -Detail '检查未返回结果'
        }
        return $result
    } catch {
        return Add-Check -Id $Id -Name $Name -Status 'UNKNOWN' -Measured 'n/a' -Threshold 'n/a' -Detail ("检查执行异常: " + $_.Exception.Message)
    }
}

$c1 = Invoke-CheckSafely -Id 'C1' -Name '默认连接名' -Body { Invoke-Check1 }
[void](Invoke-CheckSafely -Id 'C2' -Name '本地 machine 状态' -Body { Invoke-Check2 })
[void](Invoke-CheckSafely -Id 'C3' -Name '零参数 podman 落点' -Body { Invoke-Check3 })
[void](Invoke-CheckSafely -Id 'C4' -Name '本地容器存储体积' -Body { Invoke-Check4 })
[void](Invoke-CheckSafely -Id 'C5' -Name '本地遗留归档扫描' -Body { Invoke-Check5 })
[void](Invoke-CheckSafely -Id 'C6' -Name 'D:\WSL 残留体积' -Body { Invoke-Check6 })
[void](Invoke-CheckSafely -Id 'C7' -Name '远端 graphroot 可用空间' -Body { Invoke-Check7 })
[void](Invoke-CheckSafely -Id 'C8' -Name '连接覆盖类环境变量' -Body { Invoke-Check8 })
[void](Invoke-CheckSafely -Id 'C9' -Name 'WSL VHDX 体积' -Body { Invoke-Check9 })
[void](Invoke-CheckSafely -Id 'C10' -Name 'WSL 共享盘挂载' -Body { Invoke-Check10 })

# -Fix：修复 C1（默认连接）与 C9（VHDX sparse），执行前打印完整命令
if ($Fix -and $c1.Status -ne 'PASS' -and $script:PodmanPath) {
    $fixCmd = 'podman system connection default ' + $Config.ExpectedDefaultConnection
    if ($Json) {
        [Console]::Error.WriteLine('[FIX] 计划执行（只改默认连接，不启动任何 machine）:')
        [Console]::Error.WriteLine('       ' + $fixCmd)
    } else {
        Write-Host ''
        Write-Host '[FIX] 计划执行（只改默认连接，不启动任何 machine）:' -ForegroundColor Yellow
        Write-Host ('       ' + $fixCmd) -ForegroundColor Yellow
    }
    $fixResult = Invoke-Cmd -Exe $script:PodmanPath `
        -ArgList @('system', 'connection', 'default', $Config.ExpectedDefaultConnection) -TimeoutSec 30
    if ($fixResult.Error -or $fixResult.TimedOut -or $fixResult.ExitCode -ne 0) {
        $why = if ($fixResult.Error) { $fixResult.Error } elseif ($fixResult.TimedOut) { '超时' } else { "退出码 $($fixResult.ExitCode)" }
        if ($Json) { [Console]::Error.WriteLine('[FIX] 执行失败: ' + $why) }
        else { Write-Host ('[FIX] 执行失败: ' + $why) -ForegroundColor Red }
    } else {
        if ($Json) { [Console]::Error.WriteLine('[FIX] 执行完成，重新核验 C1') }
        else { Write-Host '[FIX] 执行完成，重新核验 C1' -ForegroundColor Green }
        [void]$script:Results.Remove($c1)
        $c1 = Invoke-CheckSafely -Id 'C1' -Name '默认连接名' -Body { Invoke-Check1 }
    }
}

# -Fix：仅当 C9 判 FAIL 且 sparse 明确未开启时，才尝试把 VHDX 转为稀疏
$c9 = @($script:Results | Where-Object { $_.Id -eq 'C9' })[0]
if ($Fix -and $script:WslPath -and $script:WslDistroExists -and ($script:SparseEnabled -eq $false) -and $c9 -and ($c9.Status -eq 'FAIL')) {
    $fixCmd9 = 'wsl --manage ' + $Config.WslDistroName + ' --set-sparse true'
    if ($Json) {
        [Console]::Error.WriteLine('[FIX] 计划执行（仅把 VHDX 设为 sparse，不启动发行版）:')
        [Console]::Error.WriteLine('       ' + $fixCmd9)
    } else {
        Write-Host ''
        Write-Host '[FIX] 计划执行（仅把 VHDX 设为 sparse，不启动发行版）:' -ForegroundColor Yellow
        Write-Host ('       ' + $fixCmd9) -ForegroundColor Yellow
    }
    $fixResult9 = Invoke-Cmd -Exe $script:WslPath `
        -ArgList @('--manage', $Config.WslDistroName, '--set-sparse', 'true') -TimeoutSec $Config.CommandTimeoutSec
    if ($fixResult9.Error -or $fixResult9.TimedOut -or $fixResult9.ExitCode -ne 0) {
        $why9 = if ($fixResult9.Error) { $fixResult9.Error } elseif ($fixResult9.TimedOut) { '超时' } else { "退出码 $($fixResult9.ExitCode)" }
        if ($Json) { [Console]::Error.WriteLine('[FIX] C9 执行失败: ' + $why9) }
        else { Write-Host ('[FIX] C9 执行失败: ' + $why9) -ForegroundColor Red }
    } else {
        if ($Json) { [Console]::Error.WriteLine('[FIX] C9 执行完成，重新核验 C9') }
        else { Write-Host '[FIX] C9 执行完成，重新核验 C9' -ForegroundColor Green }
        [void]$script:Results.Remove($c9)
        $script:SparseEnabled = $null
        [void](Invoke-CheckSafely -Id 'C9' -Name 'WSL VHDX 体积' -Body { Invoke-Check9 })
    }
}

# =============================================================================
# 输出与退出码
# =============================================================================
$failCount = @($script:Results | Where-Object { $_.Status -eq 'FAIL' }).Count
$unknownCount = @($script:Results | Where-Object { $_.Status -eq 'UNKNOWN' }).Count
$passCount = @($script:Results | Where-Object { $_.Status -eq 'PASS' }).Count
$naCount = @($script:Results | Where-Object { $_.Status -eq 'N/A' }).Count

if ($failCount -gt 0) { $exitCode = 1 }
elseif ($unknownCount -gt 0) { $exitCode = 2 }
else { $exitCode = 0 }

if ($Json) {
    $payload = [ordered]@{
        script      = 'podman-remote-lock-audit.ps1'
        generated_at = (Get-Date).ToString('o')
        host        = [System.Net.Dns]::GetHostName()
        fix_requested = [bool]$Fix
        summary     = [ordered]@{
            total   = $script:Results.Count
            pass    = $passCount
            fail    = $failCount
            unknown = $unknownCount
            na      = $naCount
        }
        exit_code   = $exitCode
        checks      = @($script:Results)
    }
    $payload | ConvertTo-Json -Depth 8
} else {
    Write-Host ''
    Write-Host '============================================================' -ForegroundColor Cyan
    Write-Host ' Podman 远端连接锁定审计（只读）' -ForegroundColor Cyan
    Write-Host (" 本机: {0}   时间: {1}" -f [System.Net.Dns]::GetHostName(), (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) -ForegroundColor Gray
    Write-Host '============================================================' -ForegroundColor Cyan
    foreach ($r in $script:Results) {
        $color = switch ($r.Status) {
            'PASS' { 'Green' }
            'FAIL' { 'Red' }
            'N/A' { 'DarkGray' }
            default { 'Yellow' }
        }
        Write-Host ("[{0}] {1} {2}" -f $r.Status, $r.Id, $r.Name) -ForegroundColor $color
        Write-Host ("       实测: {0}" -f $r.Measured) -ForegroundColor Gray
        Write-Host ("       阈值: {0}" -f $r.Threshold) -ForegroundColor Gray
        if ($r.Detail) { Write-Host ("       说明: {0}" -f $r.Detail) -ForegroundColor Gray }
        foreach ($e in $r.Evidence) { Write-Host ("       证据: {0}" -f $e) -ForegroundColor DarkGray }
    }
    Write-Host '------------------------------------------------------------' -ForegroundColor Cyan
    Write-Host ("汇总: PASS={0}  FAIL={1}  UNKNOWN={2}  N/A={3}" -f $passCount, $failCount, $unknownCount, $naCount) -ForegroundColor White
    Write-Host ("退出码: {0}  (0=全部通过, 1=存在违规, 2=存在无法判定项)" -f $exitCode) -ForegroundColor White
    Write-Host ''
}

exit $exitCode
