$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "common.ps1")

$parsed = Parse-Arguments -Arguments $args -Defaults @{
    format = "markdown"
    frequency = $null
    verifiable = $null
    budget = $null
    environment = $null
}

$Format = Get-Format $parsed
$ConfigPath = Get-Config $parsed
$configData = Load-ConfigFile $ConfigPath

function Get-BoolParam {
    param($Key)
    if ($parsed.ContainsKey($Key) -and $null -ne $parsed[$Key]) { return $parsed[$Key] }
    if ($configData -and $null -ne $configData.$Key) { return [bool]$configData.$Key }
    return $null
}

function Get-StrParam {
    param($Key)
    if ($parsed.ContainsKey($Key) -and $null -ne $parsed[$Key]) { return [string]$parsed[$Key] }
    if ($configData -and $null -ne $configData.$Key) { return [string]$configData.$Key }
    return $null
}

$Frequency = Get-StrParam "frequency"
$Verifiable = Get-BoolParam "verifiable"
$Budget = Get-BoolParam "budget"
$Environment = Get-BoolParam "environment"

$score = 0
$results = @()
$recommendations = @()

if ($Frequency -eq "yes") {
    $score++
    $results += @{ name = "任务频率"; passed = $true; score = 1; detail = "每周至少重复一次" }
} elseif ($Frequency -eq "uncertain") {
    $results += @{ name = "任务频率"; passed = $false; score = 0; detail = "频率不确定"; recommendation = "建议先观察一段时间确认任务频率，或先人工执行几次确认是否真的需要自动化。" }
    $recommendations += "频率不明确，建议先人工执行几次确认重复频率再决定是否建Loop。"
} else {
    $results += @{ name = "任务频率"; passed = $false; score = 0; detail = "每周少于一次"; recommendation = "任务频率不足，ROI不够。建议直接人工执行，不要建Loop。建造成本约相当于5-10次人工执行，低频任务无法回本。" }
    $recommendations += "[不要建Loop] 任务频率低于每周一次，建Loop的ROI不足。"
}

if ($Verifiable -eq $true) {
    $score++
    $results += @{ name = "验证自动化"; passed = $true; score = 1; detail = "可以写出确定性验证脚本" }
} else {
    $results += @{ name = "验证自动化"; passed = $false; score = 0; detail = "无法写出确定性验证脚本"; recommendation = "没有确定性验证器是Loop的致命缺陷——Agent无法判断方案好坏，会盲目迭代。无验证器不建Loop。" }
    $recommendations += "[不要建Loop] 无法写出确定性验证脚本，Loop无法自动判断方案好坏。"
}

if ($Budget -eq $true) {
    $score++
    $results += @{ name = "预算评估"; passed = $true; score = 1; detail = "有足够Token承受试错冗余" }
} else {
    $results += @{ name = "预算评估"; passed = $false; score = 0; detail = "Token预算不足"; recommendation = "Loop通常需要10-50次迭代，每轮消耗约为单次人工执行的2-5倍。建议先评估预算或从简单任务开始试水。" }
    $recommendations += "Token预算可能不足，建议先做预算评估或设置严格的预算上限。"
}

if ($Environment -eq $true) {
    $score++
    $results += @{ name = "环境访问"; passed = $true; score = 1; detail = "Agent能访问真实运行环境" }
} else {
    $results += @{ name = "环境访问"; passed = $false; score = 0; detail = "无法访问真实运行环境"; recommendation = "在沙箱/模拟环境中验证无法代表真实情况，Loop会优化出'应试'方案。必须能在真实环境执行代码才建Loop。" }
    $recommendations += "[不要建Loop] Agent无法访问真实运行环境，无法做真实验证。"
}

$passedCount = ($results | Where-Object { $_.passed }).Count
$failedCount = 4 - $passedCount

if ($score -eq 4) {
    $verdict = "强烈建议建Loop"
    $verdictColor = "Green"
    $exitCode = 0
} elseif ($score -eq 3) {
    $verdict = "可以考虑建Loop，但需先解决缺失项"
    $verdictColor = "Yellow"
    $exitCode = 2
} elseif ($score -eq 2) {
    $verdict = "谨慎评估，建议先解决问题再考虑"
    $verdictColor = "Yellow"
    $exitCode = 2
} else {
    $verdict = "不要建Loop"
    $verdictColor = "Red"
    $exitCode = 1
}

$hardNo = ($recommendations | Where-Object { $_ -like "*不要建Loop*" }).Count
if ($hardNo -gt 0 -and $score -lt 4) {
    $exitCode = 1
}

if ($Format -eq "json") {
    $output = @{
        command = "check-applicability"
        summary = @{
            score = $score
            max_score = 4
            passed = $passedCount
            failed = $failedCount
            verdict = $verdict
            exit_code = $exitCode
        }
        checks = $results
        recommendations = $recommendations
    }
    $output | ConvertTo-Json -Depth 10
    exit $exitCode
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Loop Engineering - 适用性判定" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "适用性评分: $score / 4" -ForegroundColor $(if ($score -eq 4) { "Green" } elseif ($score -ge 2) { "Yellow" } else { "Red" })
Write-Host "结论: $verdict" -ForegroundColor $verdictColor
Write-Host ""

Write-Host "四项标准检查:" -ForegroundColor Yellow
foreach ($check in $results) {
    $icon = if ($check.passed) { "[OK]" } else { "[!!]" }
    $color = if ($check.passed) { "Green" } else { "Red" }
    Write-Host "  $icon ($($check.score)/1) $($check.name)" -ForegroundColor $color
    Write-Host "       $($check.detail)" -ForegroundColor Gray
    if (-not $check.passed -and $check.recommendation) {
        Write-Host "       建议: $($check.recommendation)" -ForegroundColor DarkYellow
    }
}
Write-Host ""

if ($recommendations.Count -gt 0) {
    Write-Host "建议:" -ForegroundColor Yellow
    foreach ($rec in $recommendations) {
        $color = if ($rec -like "*不要建Loop*") { "Red" } else { "DarkYellow" }
        Write-Host "  - $rec" -ForegroundColor $color
    }
    Write-Host ""
}

if ($score -eq 4) {
    Write-Host "[OK] 四项标准全部满足，适合建Loop！" -ForegroundColor Green
    Write-Host "  建议先运行 verify-three-elements 验证三要素设计。" -ForegroundColor Green
} elseif ($hardNo -gt 0) {
    Write-Host "[!] 存在硬性不满足项，不建议建Loop。" -ForegroundColor Red
} else {
    Write-Host "[!] 部分标准未满足，请根据建议改进后重新评估。" -ForegroundColor Yellow
}
Write-Host ""

exit $exitCode
