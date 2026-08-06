$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "common.ps1")

$parsed = Parse-Arguments -Arguments $args -Defaults @{
    format = "markdown"
    "verifier-non-llm" = $null
    "verifier-locked" = $null
    "verifier-deterministic" = $null
    "state-history" = $null
    "state-resume" = $null
    "state-no-repeat" = $null
    "stop-rounds" = $null
    "stop-threshold" = $null
    "stop-budget" = $null
    "stop-diminishing" = $null
}

$Format = Get-Format $parsed
$ConfigPath = Get-Config $parsed
$configData = Load-ConfigFile $ConfigPath

function Get-Param {
    param($Key1, $Key2 = $null)
    $k = $Key1 -replace "_", "-"
    if ($parsed.ContainsKey($k) -and $null -ne $parsed[$k]) { return $parsed[$k] }
    if ($Key2 -and $configData -and $null -ne $configData.$Key2) { return $configData.$Key2 }
    return $null
}

$VerifierNonLLM = Get-Param "verifier-non-llm" "verifier"
if ($VerifierNonLLM -is [PSCustomObject] -and $null -ne $VerifierNonLLM.nonLLM) { $VerifierNonLLM = $VerifierNonLLM.nonLLM }
$VerifierLocked = Get-Param "verifier-locked" "verifier"
if ($VerifierLocked -is [PSCustomObject] -and $null -ne $VerifierLocked.locked) { $VerifierLocked = $VerifierLocked.locked }
$VerifierDeterministic = Get-Param "verifier-deterministic" "verifier"
if ($VerifierDeterministic -is [PSCustomObject] -and $null -ne $VerifierDeterministic.deterministic) { $VerifierDeterministic = $VerifierDeterministic.deterministic }

$StateHistory = Get-Param "state-history" "state"
if ($StateHistory -is [PSCustomObject] -and $null -ne $StateHistory.history) { $StateHistory = $StateHistory.history }
$StateResume = Get-Param "state-resume" "state"
if ($StateResume -is [PSCustomObject] -and $null -ne $StateResume.resume) { $StateResume = $StateResume.resume }
$StateNoRepeat = Get-Param "state-no-repeat" "state"
if ($StateNoRepeat -is [PSCustomObject] -and $null -ne $StateNoRepeat.noRepeat) { $StateNoRepeat = $StateNoRepeat.noRepeat }

$StopRounds = Get-Param "stop-rounds" "stop"
if ($StopRounds -is [PSCustomObject] -and $null -ne $StopRounds.rounds) { $StopRounds = $StopRounds.rounds }
$StopThreshold = Get-Param "stop-threshold" "stop"
if ($StopThreshold -is [PSCustomObject] -and $null -ne $StopThreshold.threshold) { $StopThreshold = $StopThreshold.threshold }
$StopBudget = Get-Param "stop-budget" "stop"
if ($StopBudget -is [PSCustomObject] -and $null -ne $StopBudget.budget) { $StopBudget = $StopBudget.budget }
$StopDiminishing = Get-Param "stop-diminishing" "stop"
if ($StopDiminishing -is [PSCustomObject] -and $null -ne $StopDiminishing.diminishing) { $StopDiminishing = $StopDiminishing.diminishing }

$results = @()
$failures = @()

function Add-Check {
    param($Category, $Name, $Passed, $Recommendation)
    $script:results += @{
        category = $Category
        name = $Name
        passed = $Passed
        recommendation = $Recommendation
    }
    if (-not $Passed) {
        $script:failures += @{ category = $Category; name = $Name; recommendation = $Recommendation }
    }
}

Add-Check "验证器" "验证器是否非LLM实现" ($VerifierNonLLM -eq $true) "必须使用确定性代码（Python/Shell/单元测试）作为验证器，禁止使用LLM做判断。建议重写验证器为确定性脚本。"
Add-Check "验证器" "验证器是否锁定不可篡改" ($VerifierLocked -eq $true) "验证器必须提交到版本控制并设置只读权限，禁止Agent修改。建议将验证器文件设为只读或放在独立目录。"
Add-Check "验证器" "验证器是否确定性输出" ($VerifierDeterministic -eq $true) "验证器必须对相同输入产生相同输出，评分标准需明确可量化。建议使用精确的数值评分而非模糊判断。"

Add-Check "状态文件" "状态文件是否记录历史" ($StateHistory -eq $true) "状态文件必须记录每次迭代的方案、参数和评分结果。建议在状态文件中保存完整的迭代日志。"
Add-Check "状态文件" "状态文件是否支持断点续传" ($StateResume -eq $true) "状态文件需支持中断后从上次状态继续执行。建议在状态文件中保存当前进度和最优方案。"
Add-Check "状态文件" "状态文件是否避免重复尝试" ($StateNoRepeat -eq $true) "状态文件需记录已尝试过的方案，避免重复尝试相同或相似参数。建议添加已尝试方案的去重机制。"

Add-Check "停止条件" "是否有轮次限制" ($StopRounds -eq $true) "必须设置最大迭代次数防止无限循环。建议设置硬上限（简单任务≤15轮，复杂任务≤40轮）。"
Add-Check "停止条件" "是否有阈值达标条件" ($StopThreshold -eq $true) "需设置明确的达标阈值（如测试通过率100%、延迟<50ms）。建议根据业务目标定义清晰的成功标准。"
Add-Check "停止条件" "是否有预算限制" ($StopBudget -eq $true) "必须设置Token/时间预算上限防止成本失控。建议设置每轮Token上限和总预算。"
Add-Check "停止条件" "是否有收益递减检测" ($StopDiminishing -eq $true) "需检测连续多轮提升低于阈值时自动停止。建议添加连续3轮提升<1%则停止的机制。"

$totalChecks = $results.Count
$passedChecks = ($results | Where-Object { $_.passed }).Count
$failedChecks = $failures.Count
$exitCode = if ($failedChecks -eq 0) { 0 } else { 1 }

if ($Format -eq "json") {
    $output = @{
        command = "verify-three-elements"
        summary = @{
            total = $totalChecks
            passed = $passedChecks
            failed = $failedChecks
            exit_code = $exitCode
        }
        checks = $results
        failures = $failures
    }
    $output | ConvertTo-Json -Depth 10
    exit $exitCode
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Loop Engineering - 三要素验证" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "验证结果汇总:" -ForegroundColor Yellow
Write-Host "  总检查项: $totalChecks" -ForegroundColor White
Write-Host "  通过: $passedChecks" -ForegroundColor Green
Write-Host "  失败: $failedChecks" -ForegroundColor $(if ($failedChecks -gt 0) { "Red" } else { "Green" })
Write-Host ""

$categories = $results | Group-Object category
foreach ($cat in $categories) {
    Write-Host "[$($cat.Name)]" -ForegroundColor Yellow
    foreach ($check in $cat.Group) {
        $status = if ($check.passed) { "PASS" } else { "FAIL" }
        $color = if ($check.passed) { "Green" } else { "Red" }
        $icon = if ($check.passed) { "[OK]" } else { "[!!]" }
        Write-Host "  $icon $status - $($check.name)" -ForegroundColor $color
        if (-not $check.passed) {
            Write-Host "       建议: $($check.recommendation)" -ForegroundColor DarkYellow
        }
    }
    Write-Host ""
}

if ($failedChecks -gt 0) {
    Write-Host "[!] 修复建议:" -ForegroundColor Red
    Write-Host "  三要素缺一不可，必须全部通过才能构建可靠的Loop。" -ForegroundColor Red
    Write-Host "  请根据上述失败项逐一修复后重新验证。" -ForegroundColor Red
    Write-Host ""
} else {
    Write-Host "[OK] 三要素验证全部通过！" -ForegroundColor Green
    Write-Host "  验证器、状态文件、停止条件均已满足要求，可以构建Loop。" -ForegroundColor Green
    Write-Host ""
}

exit $exitCode
