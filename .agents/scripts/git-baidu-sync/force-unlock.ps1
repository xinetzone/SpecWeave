[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$RepoName,

    [Parameter(Mandatory = $false)]
    [string]$SyncRoot,

    [Parameter(Mandatory = $false)]
    [switch]$Force,

    [Parameter(Mandatory = $false)]
    [switch]$Help
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LockUtils = Join-Path $ScriptDir "lock-utils.ps1"

if (-not (Test-Path $LockUtils)) {
    Write-Error "[ERROR] 找不到锁模块: $LockUtils"
    exit 2
}

. $LockUtils

if ($Help) {
    Write-Host @"
用法: force-unlock.ps1 -RepoName <repo> -SyncRoot <path> [-Force]

强制释放指定仓库的锁（危险操作）。

参数:
  -RepoName <repo>    仓库名称（必填）
  -SyncRoot <path>    同步空间根目录（必填，或设置 GIT_SYNC_ROOT 环境变量）
  -Force              跳过交互确认（危险）
  -Help               显示此帮助

环境变量:
  GIT_SYNC_LOCK_TIMEOUT    锁超时分钟数（默认30）

示例:
  .\force-unlock.ps1 -RepoName my-project -SyncRoot D:\BaiduSync\git-sync
  .\force-unlock.ps1 -RepoName my-project -SyncRoot D:\BaiduSync\git-sync -Force
"@
    exit 0
}

if (-not $RepoName) {
    Write-Error "[ERROR] 必须指定 -RepoName 参数"
    exit 2
}

if (-not $SyncRoot) {
    $envRoot = $env:GIT_SYNC_ROOT
    if ($envRoot) {
        $SyncRoot = $envRoot
        Write-Host "[INFO] 使用环境变量 GIT_SYNC_ROOT=$SyncRoot"
    }
    else {
        Write-Error "[ERROR] 必须指定 -SyncRoot 参数或设置 GIT_SYNC_ROOT 环境变量"
        exit 2
    }
}

if (-not (Lock-Init -SyncRoot $SyncRoot)) {
    Write-Error "[ERROR] 锁系统初始化失败"
    exit 2
}

Write-Host ""
Write-Host "=== 当前锁状态 ==="
[void](Lock-Check -RepoName $RepoName)
Write-Host ""

if (Lock-ForceRelease -RepoName $RepoName -Force:$Force) {
    Write-Host ""
    Write-Host "[SUCCESS] 强制解锁完成: $RepoName" -ForegroundColor Green
    exit 0
}
else {
    Write-Host ""
    Write-Host "[CANCELLED/FAILED] 强制解锁未执行或失败" -ForegroundColor Yellow
    exit 1
}
