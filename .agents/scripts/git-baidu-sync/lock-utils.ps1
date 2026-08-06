# lock-utils.ps1 - Git 网盘同步锁机制 PowerShell 模块
# dot-source 使用，或作为模块导入
# 提供与 lock-utils.sh 等价的功能

$script:LockUtilsVersion = "1.0.0"
$script:LockDefaultTimeoutMinutes = 30
$script:LockUtilsDeviceId = ""
$script:LockUtilsSyncRoot = ""
$script:LockUtilsCacheLoaded = $false

function Lock-Err {
    param([string]$Message)
    Write-Error "[lock-utils ERROR] $Message"
}

function Lock-Warn {
    param([string]$Message)
    Write-Host "[lock-utils WARN] $Message" -ForegroundColor Yellow
}

function Lock-Info {
    param([string]$Message)
    Write-Host "[lock-utils] $Message" -ForegroundColor Gray
}

function Lock-DetectOS {
    if ($IsWindows) { return "win" }
    if ($IsMacOS) { return "macos" }
    if ($IsLinux) { return "linux" }
    if ($env:OS -eq "Windows_NT") { return "win" }
    return "unknown"
}

function Lock-GetHostname {
    $hn = $env:COMPUTERNAME
    if (-not $hn) { $hn = $env:HOSTNAME }
    if (-not $hn) {
        try { $hn = [System.Net.Dns]::GetHostName() } catch { $hn = "unknown-host" }
    }
    $hn = $hn -replace '[^a-zA-Z0-9_-]', ''
    if (-not $hn) { $hn = "unknown-host" }
    return $hn.ToLower()
}

function Lock-GetPid {
    return $PID
}

function Lock-GetIso8601 {
    return (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
}

function Lock-Iso8601ToEpoch {
    param([string]$IsoString)
    if ([string]::IsNullOrWhiteSpace($IsoString)) { return 0 }
    try {
        $dt = [DateTimeOffset]::Parse($IsoString)
        return [long]$dt.ToUnixTimeSeconds()
    }
    catch {
        try {
            $dt = Get-Date $IsoString
            return [long]([DateTimeOffset]$dt).ToUnixTimeSeconds()
        }
        catch {
            return 0
        }
    }
}

function Lock-GetNowEpoch {
    return [long][DateTimeOffset]::Now.ToUnixTimeSeconds()
}

function Lock-PidExists {
    param([int]$Pid)
    if ($Pid -le 0) { return $false }
    try {
        $process = Get-Process -Id $Pid -ErrorAction Stop
        return $null -ne $process
    }
    catch {
        return $false
    }
}

function Lock-GetDeviceCachePath {
    if ($script:LockUtilsSyncRoot -and (Test-Path (Join-Path $script:LockUtilsSyncRoot "meta"))) {
        return Join-Path $script:LockUtilsSyncRoot "meta\devices.json"
    }
    return Join-Path $HOME ".git-baidu-sync-device-id"
}

function Lock-ExtractDeviceIdFromCache {
    param(
        [string]$CacheFile,
        [string]$MyHostname,
        [string]$MyOS
    )
    if (-not (Test-Path $CacheFile)) { return $null }

    if ($CacheFile -like "*devices.json") {
        try {
            $json = Get-Content $CacheFile -Raw -Encoding UTF8 | ConvertFrom-Json -ErrorAction Stop
            $found = $json.devices | Where-Object { $_.hostname -eq $MyHostname -and $_.os -eq $MyOS } | Select-Object -First 1
            if ($found -and $found.id) { return $found.id }
        }
        catch { }
        return $null
    }

    try {
        $content = (Get-Content $CacheFile -Raw -Encoding UTF8).Trim()
        if ($content -match '^[a-z0-9-]+-(win|macos|linux|unknown)-[0-9]+$') {
            return $content
        }
    }
    catch { }
    return $null
}

function Lock-SaveDeviceId {
    param(
        [string]$DeviceId,
        [string]$CacheFile
    )
    $cacheDir = Split-Path $CacheFile -Parent
    if (-not (Test-Path $cacheDir)) {
        New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null
    }

    if ($CacheFile -like "*devices.json") {
        $json = $null
        if (Test-Path $CacheFile) {
            try {
                $json = Get-Content $CacheFile -Raw -Encoding UTF8 | ConvertFrom-Json -ErrorAction Stop
            }
            catch {
                $json = [PSCustomObject]@{ devices = @() }
            }
        }
        else {
            $json = [PSCustomObject]@{ devices = @() }
        }

        $myHostname = Lock-GetHostname
        $myOS = Lock-DetectOS
        $ts = Lock-GetIso8601
        $newDevice = [PSCustomObject]@{
            id            = $DeviceId
            hostname      = $myHostname
            os            = $myOS
            registered_at = $ts
            last_seen     = $ts
        }
        $json.devices += $newDevice
        $json | ConvertTo-Json -Depth 10 | Set-Content $CacheFile -Encoding UTF8
        return
    }

    Set-Content -Path $CacheFile -Value $DeviceId -Encoding UTF8 -NoNewline
}

function Lock-GenerateDeviceId {
    param(
        [string]$Hostname,
        [string]$OSType
    )
    $seq = 1
    $cacheFile = Lock-GetDeviceCachePath

    if (Test-Path $cacheFile -and ($cacheFile -notlike "*devices.json")) {
        try {
            $existing = (Get-Content $cacheFile -Raw -Encoding UTF8).Trim()
            if ($existing -match "^$([regex]::Escape($Hostname))-$([regex]::Escape($OSType))-(\d+)$") {
                $seq = [int]$Matches[1]
            }
        }
        catch { }
    }

    return "$Hostname-$OSType-$(($seq).ToString('00'))"
}

function Lock-EnsureDeviceId {
    if ($script:LockUtilsCacheLoaded -and $script:LockUtilsDeviceId) { return }

    $myHostname = Lock-GetHostname
    $myOS = Lock-DetectOS
    $cacheFile = Lock-GetDeviceCachePath

    $cachedId = Lock-ExtractDeviceIdFromCache -CacheFile $cacheFile -MyHostname $myHostname -MyOS $myOS
    if ($cachedId) {
        $script:LockUtilsDeviceId = $cachedId
        $script:LockUtilsCacheLoaded = $true
        return
    }

    $script:LockUtilsDeviceId = Lock-GenerateDeviceId -Hostname $myHostname -OSType $myOS
    try {
        Lock-SaveDeviceId -DeviceId $script:LockUtilsDeviceId -CacheFile $cacheFile
    }
    catch { }
    $script:LockUtilsCacheLoaded = $true
}

function Lock-GetTimeoutMinutes {
    $envTimeout = $env:GIT_SYNC_LOCK_TIMEOUT
    if ($envTimeout -and $envTimeout -match '^\d+$') {
        return [int]$envTimeout
    }
    return $script:LockDefaultTimeoutMinutes
}

function Lock-GetLockfilePath {
    param([string]$RepoName)
    if (-not $script:LockUtilsSyncRoot) {
        Lock-Err "SyncRoot 未初始化，请先调用 Lock-Init"
        return $null
    }
    return Join-Path $script:LockUtilsSyncRoot "locks\$RepoName.lock.json"
}

function Lock-ReadJsonField {
    param(
        [string]$FilePath,
        [string]$Field
    )
    try {
        $json = Get-Content $FilePath -Raw -Encoding UTF8 | ConvertFrom-Json -ErrorAction Stop
        return $json.$Field
    }
    catch {
        try {
            $content = Get-Content $FilePath -Raw -Encoding UTF8
            if ($content -match "`"$Field`"\s*:\s*`"?([^,}`"]+)`"?") {
                return $Matches[1].Trim()
            }
        }
        catch { }
        return $null
    }
}

function Lock-IsTimeoutLock {
    param([string]$Lockfile)
    $acquiredAt = Lock-ReadJsonField -FilePath $Lockfile -Field "acquired_at"
    if (-not $acquiredAt) { return $true }
    $lockEpoch = Lock-Iso8601ToEpoch -IsoString $acquiredAt
    $nowEpoch = Lock-GetNowEpoch
    $timeoutMins = Lock-GetTimeoutMinutes
    $diffMins = [math]::Floor(($nowEpoch - $lockEpoch) / 60)
    return $diffMins -ge $timeoutMins
}

function Lock-BuildLockJson {
    param(
        [string]$Operation,
        [string]$DeviceId,
        [int]$Pid,
        [string]$Hostname
    )
    $ts = Lock-GetIso8601
    $obj = [PSCustomObject]@{
        device_id      = $DeviceId
        pid            = $Pid
        acquired_at    = $ts
        operation      = $Operation
        hostname       = $Hostname
        script_version = $script:LockUtilsVersion
    }
    return $obj | ConvertTo-Json -Depth 5
}

function Lock-Init {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$SyncRoot
    )

    if (-not (Test-Path $SyncRoot -PathType Container)) {
        Lock-Err "同步根目录不存在: $SyncRoot"
        return $false
    }

    $script:LockUtilsSyncRoot = $SyncRoot
    $script:LockUtilsCacheLoaded = $false
    $script:LockUtilsDeviceId = ""
    Lock-EnsureDeviceId

    $locksDir = Join-Path $SyncRoot "locks"
    if (-not (Test-Path $locksDir)) {
        try {
            New-Item -ItemType Directory -Path $locksDir -Force | Out-Null
        }
        catch {
            Lock-Err "无法创建 locks 目录: $locksDir"
            return $false
        }
    }

    Lock-Info "锁系统初始化完成 (device_id=$($script:LockUtilsDeviceId), sync_root=$SyncRoot)"
    return $true
}

function Lock-Acquire {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$RepoName,
        [Parameter(Mandatory = $true, Position = 1)]
        [string]$Operation
    )

    Lock-EnsureDeviceId

    $lockfile = Lock-GetLockfilePath -RepoName $RepoName
    if (-not $lockfile) { return $false }

    $myDeviceId = $script:LockUtilsDeviceId
    $myPid = Lock-GetPid
    $myHostname = Lock-GetHostname

    for ($retry = 1; $retry -le 3; $retry++) {
        if (Test-Path $lockfile -PathType Leaf) {
            $holderDevice = Lock-ReadJsonField -FilePath $lockfile -Field "device_id"
            $holderPid = Lock-ReadJsonField -FilePath $lockfile -Field "pid"
            $holderOp = Lock-ReadJsonField -FilePath $lockfile -Field "operation"
            $holderTs = Lock-ReadJsonField -FilePath $lockfile -Field "acquired_at"
            $holderHost = Lock-ReadJsonField -FilePath $lockfile -Field "hostname"

            if ($holderDevice -eq $myDeviceId) {
                $holderPidInt = 0
                [int]::TryParse($holderPid, [ref]$holderPidInt) | Out-Null
                if ($holderPidInt -gt 0 -and (Lock-PidExists -Pid $holderPidInt)) {
                    if ($holderPidInt -eq $myPid) {
                        Lock-Info "锁已被当前进程持有，重入成功"
                        return $true
                    }
                    Lock-Err "仓库 $RepoName 已被本设备其他进程持有 (pid=$holderPidInt, op=$holderOp, since=$holderTs)"
                    return $false
                }
                Lock-Warn "发现本设备残留锁 (pid=$holderPid 已不存在)，自动清理"
                Remove-Item $lockfile -Force -ErrorAction SilentlyContinue
            }
            elseif (Lock-IsTimeoutLock -Lockfile $lockfile) {
                Lock-Warn "========================================"
                Lock-Warn "发现超时锁，自动清理："
                Lock-Warn "  仓库: $RepoName"
                Lock-Warn "  持有者 device_id: $holderDevice"
                Lock-Warn "  持有者 hostname: $holderHost"
                Lock-Warn "  持有者 pid: $holderPid"
                Lock-Warn "  操作: $holderOp"
                Lock-Warn "  获取时间: $holderTs"
                Lock-Warn "========================================"
                Remove-Item $lockfile -Force -ErrorAction SilentlyContinue
            }
            else {
                Lock-Err "仓库 $RepoName 已被其他设备持有锁"
                Lock-Err "  device_id: $holderDevice"
                Lock-Err "  hostname: $holderHost"
                Lock-Err "  pid: $holderPid"
                Lock-Err "  operation: $holderOp"
                Lock-Err "  acquired_at: $holderTs"
                Lock-Err "请等待持有者完成或确认超时后使用 Lock-ForceRelease 或 force-unlock 工具"
                return $false
            }
        }

        $lockJson = Lock-BuildLockJson -Operation $Operation -DeviceId $myDeviceId -Pid $myPid -Hostname $myHostname

        $created = $false
        try {
            New-Item -Path $lockfile -ItemType File -ErrorAction Stop | Out-Null
            Set-Content -Path $lockfile -Value $lockJson -Encoding UTF8 -NoNewline
            $created = $true
        }
        catch [System.IO.IOException] {
            $created = $false
        }
        catch {
            if ($_.Exception -is [System.Management.Automation.ItemExistsException] -or
                $_.CategoryInfo.Category -eq "ResourceExists") {
                $created = $false
            }
            else {
                Lock-Warn "创建锁文件遇到异常，重试 ($retry/3): $_"
                $created = $false
            }
        }

        if ($created -and (Test-Path $lockfile)) {
            Lock-Info "已获取锁: $RepoName (op=$Operation, pid=$myPid)"
            return $true
        }

        if ($retry -lt 3) {
            Lock-Info "获取锁时遇到竞态，重试 ($retry/3)..."
            Start-Sleep -Milliseconds 200
        }
    }

    Lock-Err "获取锁失败（多次重试后仍失败，可能存在并发竞争）"
    return $false
}

function Lock-Release {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$RepoName
    )

    Lock-EnsureDeviceId

    $lockfile = Lock-GetLockfilePath -RepoName $RepoName
    if (-not $lockfile) { return $false }

    if (-not (Test-Path $lockfile -PathType Leaf)) {
        Lock-Warn "释放锁时文件不存在: $lockfile（可能已被超时清理）"
        return $true
    }

    $holderDevice = Lock-ReadJsonField -FilePath $lockfile -Field "device_id"
    $holderPid = Lock-ReadJsonField -FilePath $lockfile -Field "pid"
    $myDeviceId = $script:LockUtilsDeviceId

    if ($holderDevice -ne $myDeviceId) {
        Lock-Err "拒绝释放他人的锁！"
        Lock-Err "  持有者: $holderDevice"
        Lock-Err "  本设备: $myDeviceId"
        Lock-Err "如需强制释放，请使用 Lock-ForceRelease 或 force-unlock 工具"
        return $false
    }

    $myPid = Lock-GetPid
    $holderPidInt = 0
    [int]::TryParse($holderPid, [ref]$holderPidInt) | Out-Null
    if ($holderPidInt -gt 0 -and $holderPidInt -ne $myPid -and (Lock-PidExists -Pid $holderPidInt)) {
        Lock-Warn "释放同设备不同进程的锁 (holder_pid=$holderPidInt, my_pid=$myPid)"
    }

    try {
        Remove-Item $lockfile -Force -ErrorAction Stop
    }
    catch {
        Lock-Err "删除锁文件失败: $lockfile"
        return $false
    }
    Lock-Info "已释放锁: $RepoName"
    return $true
}

function Lock-Check {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$RepoName
    )

    $lockfile = Lock-GetLockfilePath -RepoName $RepoName
    if (-not $lockfile) { return 99 }

    if (-not (Test-Path $lockfile -PathType Leaf)) {
        Write-Host "无锁（可用）"
        return 0
    }

    $holderDevice = Lock-ReadJsonField -FilePath $lockfile -Field "device_id"
    $holderPid = Lock-ReadJsonField -FilePath $lockfile -Field "pid"
    $holderOp = Lock-ReadJsonField -FilePath $lockfile -Field "operation"
    $holderTs = Lock-ReadJsonField -FilePath $lockfile -Field "acquired_at"
    $holderHost = Lock-ReadJsonField -FilePath $lockfile -Field "hostname"
    $holderVer = Lock-ReadJsonField -FilePath $lockfile -Field "script_version"

    Write-Host "=== 锁状态: $RepoName ==="
    Write-Host "  device_id:      $holderDevice"
    Write-Host "  hostname:       $holderHost"
    Write-Host "  pid:            $holderPid"
    Write-Host "  operation:      $holderOp"
    Write-Host "  acquired_at:    $holderTs"
    Write-Host "  script_version: $holderVer"

    try { Lock-EnsureDeviceId } catch {}
    $myDeviceId = $script:LockUtilsDeviceId
    $nowEpoch = Lock-GetNowEpoch
    $lockEpoch = Lock-Iso8601ToEpoch -IsoString $holderTs
    $diffMins = 0
    if ($lockEpoch -gt 0) {
        $diffMins = [math]::Floor(($nowEpoch - $lockEpoch) / 60)
        Write-Host "  已持有:        $diffMins 分钟"
    }

    $timeoutMins = Lock-GetTimeoutMinutes
    Write-Host "  超时阈值:      $timeoutMins 分钟"

    if (Lock-IsTimeoutLock -Lockfile $lockfile) {
        Write-Host "状态: 超时（可安全清理或重新获取）" -ForegroundColor Yellow
        return 3
    }

    if ($myDeviceId -and $holderDevice -eq $myDeviceId) {
        $holderPidInt = 0
        [int]::TryParse($holderPid, [ref]$holderPidInt) | Out-Null
        if ($holderPidInt -gt 0 -and (Lock-PidExists -Pid $holderPidInt)) {
            Write-Host "状态: 被本设备持有" -ForegroundColor Green
            return 1
        }
        else {
            Write-Host "状态: 本设备残留锁（进程已退出，视同超时）" -ForegroundColor Yellow
            return 3
        }
    }

    Write-Host "状态: 被其他设备持有" -ForegroundColor Red
    return 2
}

function Lock-GetHolderInfo {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$RepoName
    )

    $lockfile = Lock-GetLockfilePath -RepoName $RepoName
    if (-not $lockfile) { return "{}" }

    if (-not (Test-Path $lockfile -PathType Leaf)) {
        return "{}"
    }

    Get-Content $lockfile -Raw -Encoding UTF8
}

function Lock-ForceRelease {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$RepoName,
        [Parameter(Mandatory = $false)]
        [switch]$Force
    )

    $lockfile = Lock-GetLockfilePath -RepoName $RepoName
    if (-not $lockfile) { return $false }

    if (-not (Test-Path $lockfile -PathType Leaf)) {
        Lock-Info "锁不存在，无需强制释放: $RepoName"
        return $true
    }

    $holderDevice = Lock-ReadJsonField -FilePath $lockfile -Field "device_id"
    $holderPid = Lock-ReadJsonField -FilePath $lockfile -Field "pid"
    $holderOp = Lock-ReadJsonField -FilePath $lockfile -Field "operation"
    $holderTs = Lock-ReadJsonField -FilePath $lockfile -Field "acquired_at"
    $holderHost = Lock-ReadJsonField -FilePath $lockfile -Field "hostname"

    try { Lock-EnsureDeviceId } catch {}
    $myDeviceId = $script:LockUtilsDeviceId
    $nowEpoch = Lock-GetNowEpoch
    $lockEpoch = Lock-Iso8601ToEpoch -IsoString $holderTs
    $diffMins = 0
    if ($lockEpoch -gt 0) {
        $diffMins = [math]::Floor(($nowEpoch - $lockEpoch) / 60)
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  警告: 强制解锁（DANGER）" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  仓库:          $RepoName"
    Write-Host "  持有者device:  $holderDevice"
    Write-Host "  持有者host:    $holderHost"
    Write-Host "  持有者pid:     $holderPid"
    Write-Host "  操作类型:      $holderOp"
    Write-Host "  获取时间:      $holderTs"
    Write-Host "  已持有时长:    $diffMins 分钟"
    Write-Host ""

    if ($myDeviceId -and $holderDevice -eq $myDeviceId) {
        Write-Host "  提示: 这是本设备持有的锁" -ForegroundColor Cyan
    }
    else {
        Write-Host "  警告: 这是 OTHER DEVICE 持有的锁！" -ForegroundColor Red
        Write-Host "     强制释放可能导致并发 push 和仓库损坏！" -ForegroundColor Red
        Write-Host "     请确认持有者设备确实已离线/崩溃且不再操作！" -ForegroundColor Red
    }
    Write-Host ""

    if (-not $Force) {
        Write-Host "确认强制释放？(输入 YES 继续，其他输入取消): " -NoNewline -ForegroundColor Yellow
        $confirm = Read-Host
        if ($confirm -ne "YES") {
            Lock-Info "用户取消操作"
            return $false
        }
    }

    Lock-Warn "执行强制释放锁: $lockfile"
    try {
        Remove-Item $lockfile -Force -ErrorAction Stop
    }
    catch {
        Lock-Err "强制释放失败（无法删除锁文件）: $_"
        return $false
    }
    Lock-Warn "锁已强制释放。请等待网盘同步完成后再操作。"
    Write-Host ""
    Lock-Info "强制释放完成: $RepoName"
    return $true
}

$MyInvocationLine = $MyInvocation.Line
if ($MyInvocation.InvocationName -ne '.' -and
    $MyInvocation.InvocationName -ne '&' -and
    -not ($MyInvocationLine -match '\.\s+.*lock-utils\.ps1') -and
    $MyInvocation.MyCommand.Path -eq $PSCommandPath -and
    -not $PSBoundParameters.Count -eq 0 -eq $false) {
    if ($MyInvocation.MyCommand.Path -eq $PSCommandPath -and $MyInvocation.Line -notmatch '\.\s+') {
        Write-Host @"
lock-utils.ps1 - Git 网盘同步锁机制 PowerShell 模块

本文件是函数库，应被其他脚本 dot-source 使用，不直接执行。

用法（在其他脚本中）:
  . .\lock-utils.ps1

  Lock-Init <SyncRoot>                # 初始化锁系统（必须先调用）
  Lock-Acquire <RepoName> <Op>        # 原子获取锁（返回$true成功/$false失败）
  Lock-Release <RepoName>             # 释放锁
  Lock-Check <RepoName>               # 检查锁状态（返回0无锁/1自己持有/2他人持有/3超时）
  Lock-GetHolderInfo <RepoName>       # 输出锁持有者JSON
  Lock-ForceRelease <RepoName> [-Force]  # 强制释放锁（需交互确认）

环境变量:
  GIT_SYNC_LOCK_TIMEOUT    锁超时分钟数（默认30）
"@
    }
}
