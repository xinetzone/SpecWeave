#Requires -Version 7.4
<#
.SYNOPSIS
    wechat-mp-archiver 定时同步入口（供 Windows 任务计划程序调用）。

.DESCRIPTION
    默认执行增量同步：mp-archiver sync -a <账号>
      列表 catch-up 追平新文章 -> 归档正文/富媒体（--FetchMetrics 时含互动）。
    指定 -Full 时执行全量回溯+下架对账：
      mp-archiver run -a <账号> --full --include-failed

    特性：
      - 自动定位项目根目录（脚本位于 deploy/ 下，根为其父目录），可用 -ProjectRoot 覆盖；
      - 优先使用项目 .venv 中的 Python，缺失时回退 PATH 中的 python；
      - 全部输出追加到 logs/sync-yyyyMMdd.log（logs/ 已在 .gitignore 忽略）；
      - 透传 mp-archiver 退出码，便于任务计划程序监测：
          0 成功；1 存在失败文章/参数错误；2 登录态失效需重新扫码；
          3 账号未找到；4 采集服务不可达或环境异常。

.PARAMETER Account
    公众号账号别名（与 list/fetch 使用的昵称或微信号一致）。

.PARAMETER FetchMetrics
    同时采集评论与阅读/点赞等互动指标（需已配置互动凭证，见 deploy/README.md 第 8 节）。

.PARAMETER Full
    执行全量回溯与下架对账（日常调度不建议使用；建议每周至多一次）。

.PARAMETER ProjectRoot
    项目根目录（含 .env 与 .venv）。默认取脚本所在 deploy/ 目录的父目录。

.EXAMPLE
    pwsh -File .\deploy\sync-incremental.ps1 -Account "某公众号"
.EXAMPLE
    pwsh -File .\deploy\sync-incremental.ps1 -Account "某公众号" -Full
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Account,

    [switch]$FetchMetrics,

    [switch]$Full,

    [string]$ProjectRoot
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ProjectRoot) {
    $ProjectRoot = Split-Path -Parent $scriptDir
}
$ProjectRoot = (Resolve-Path $ProjectRoot).Path

$venvPython = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
if (Test-Path $venvPython) {
    $python = $venvPython
} else {
    $python = (Get-Command python -ErrorAction Stop).Source
}

$logDir = Join-Path $ProjectRoot 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logFile = Join-Path $logDir ("sync-{0:yyyyMMdd}.log" -f (Get-Date))

$cliArgs = @('-m', 'mp_archiver')
if ($Full) {
    $cliArgs += @('run', '-a', $Account, '--full', '--include-failed')
    $mode = 'full'
} else {
    $cliArgs += @('sync', '-a', $Account)
    $mode = 'incremental'
}
if ($FetchMetrics) {
    $cliArgs += '--fetch-metrics'
}

$startedAt = Get-Date
"===== $($startedAt.ToString('o')) mode=$mode account=$Account python=$python =====" |
    Out-File -FilePath $logFile -Append -Encoding utf8

Push-Location $ProjectRoot
$exitCode = 0
try {
    & $python @cliArgs 2>&1 | Tee-Object -FilePath $logFile -Append
    $exitCode = $LASTEXITCODE
} catch {
    "[fatal] 脚本执行异常：$_" | Tee-Object -FilePath $logFile -Append
    $exitCode = 4
} finally {
    Pop-Location
    $finishedAt = Get-Date
    "----- exit=$exitCode finished=$($finishedAt.ToString('o')) elapsed_sec=$([int]($finishedAt - $startedAt).TotalSeconds) -----" |
        Out-File -FilePath $logFile -Append -Encoding utf8
}

exit $exitCode
