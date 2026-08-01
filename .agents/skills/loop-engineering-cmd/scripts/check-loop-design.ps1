$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "common.ps1")

$parsed = Parse-Arguments -Arguments $args -Defaults @{
    format = "markdown"
    "step1-explore" = $null
    "step2-score" = $null
    "step3-scope" = $null
    "step4-real" = $null
    "step5-evaluate" = $null
}

$Format = Get-Format $parsed
$ConfigPath = Get-Config $parsed
$configData = Load-ConfigFile $ConfigPath

function Get-Step {
    param($Key)
    if ($parsed.ContainsKey($Key) -and $null -ne $parsed[$Key]) { return $parsed[$Key] }
    if ($configData -and $configData.steps -and $null -ne $configData.steps.$Key) { return [bool]$configData.steps.$Key }
    return $null
}

$Step1 = Get-Step "step1"
if ($null -eq $Step1) { $Step1 = Get-Step "step1-explore" }
$Step2 = Get-Step "step2"
if ($null -eq $Step2) { $Step2 = Get-Step "step2-score" }
$Step3 = Get-Step "step3"
if ($null -eq $Step3) { $Step3 = Get-Step "step3-scope" }
$Step4 = Get-Step "step4"
if ($null -eq $Step4) { $Step4 = Get-Step "step4-real" }
$Step5 = Get-Step "step5"
if ($null -eq $Step5) { $Step5 = Get-Step "step5-evaluate" }

$steps = @(
    @{
        num = 1
        name = "探索"
        title = "清晰探索文档与边界约束"
        passed = ($Step1 -eq $true)
        recommendation = "必须编写清晰的探索文档，明确：目标是什么、哪些文件/目录可以修改、哪些绝对不能碰、评分标准是什么。没有边界约束的Loop会越改越乱。"
    },
    @{
        num = 2
        name = "评分"
        title = "评分脚本锁定，禁止Agent修改"
        passed = ($Step2 -eq $true)
        recommendation = "评分脚本（验证器）必须锁定：设置只读权限、提交到独立目录、禁止Agent写入。评分脚本是裁判，不能让运动员（Agent）改裁判。"
    },
    @{
        num = 3
        name = "变更"
        title = "变更范围限定（仅执行脚本）"
        passed = ($Step3 -eq $true)
        recommendation = "必须明确限定Agent可以修改的文件范围：只允许修改执行脚本/目标文件，禁止修改验证器、配置文件、其他无关代码。建议用目录白名单机制控制变更范围。"
    },
    @{
        num = 4
        name = "执行"
        title = "在真实环境中执行（非纸上谈兵）"
        passed = ($Step4 -eq $true)
        recommendation = "必须在真实运行环境中执行验证，不能只做静态分析或纸上谈兵。模拟环境中通过的方案在真实环境可能失败，必须实际运行代码验证。"
    },
    @{
        num = 5
        name = "评估"
        title = "评估自动化、优胜劣汰"
        passed = ($Step5 -eq $true)
        recommendation = "评估必须完全自动化：自动运行评分、自动比较结果、自动保留当前最优方案、自动淘汰较差方案。人工介入评估会破坏Loop的自动化循环。"
    }
)

$score = 0
$failures = @()
foreach ($step in $steps) {
    if ($step.passed) { $score++ } else { $failures += $step }
}

if ($score -eq 5) {
    $verdict = "五步法设计完整"
    $verdictColor = "Green"
    $exitCode = 0
} elseif ($score -ge 3) {
    $verdict = "设计基本完整，有缺失项需补充"
    $verdictColor = "Yellow"
    $exitCode = 2
} else {
    $verdict = "设计不完整，存在严重缺陷"
    $verdictColor = "Red"
    $exitCode = 1
}

if ($Format -eq "json") {
    $output = @{
        command = "check-loop-design"
        summary = @{
            score = $score
            max_score = 5
            verdict = $verdict
            exit_code = $exitCode
        }
        steps = $steps
        failures = $failures
    }
    $output | ConvertTo-Json -Depth 10
    exit $exitCode
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Loop Engineering - 循环设计检查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "五步完整性评分: $score / 5" -ForegroundColor $(if ($score -eq 5) { "Green" } elseif ($score -ge 3) { "Yellow" } else { "Red" })
Write-Host "结论: $verdict" -ForegroundColor $verdictColor
Write-Host ""

Write-Host "五步法检查:" -ForegroundColor Yellow
foreach ($step in $steps) {
    $icon = if ($step.passed) { "[OK]" } else { "[!!]" }
    $color = if ($step.passed) { "Green" } else { "Red" }
    Write-Host "  $icon 环节$($step.num) [$($step.name)]: $($step.title)" -ForegroundColor $color
    if (-not $step.passed) {
        Write-Host "       建议: $($step.recommendation)" -ForegroundColor DarkYellow
    }
}
Write-Host ""

if ($failures.Count -gt 0) {
    Write-Host "[!] 问题清单与修复建议:" -ForegroundColor $(if ($score -ge 3) { "Yellow" } else { "Red" })
    foreach ($step in $failures) {
        Write-Host "  环节$($step.num) [$($step.name)]:" -ForegroundColor $(if ($score -ge 3) { "DarkYellow" } else { "Red" })
        Write-Host "    $($step.recommendation)" -ForegroundColor Gray
    }
    Write-Host ""
} else {
    Write-Host "[OK] 五步法设计完整！" -ForegroundColor Green
    Write-Host "  探索→评分→变更→执行→评估各环节均已满足要求。" -ForegroundColor Green
    Write-Host ""
}

Write-Host "五步法流程说明:" -ForegroundColor Yellow
Write-Host "  1. [探索] 定义目标和边界 → 明确什么能改什么不能改" -ForegroundColor Gray
Write-Host "  2. [评分] 锁定验证器 → 裁判不能被运动员修改" -ForegroundColor Gray
Write-Host "  3. [变更] 限定修改范围 → Agent只能碰指定文件" -ForegroundColor Gray
Write-Host "  4. [执行] 真实环境运行 → 不纸上谈兵" -ForegroundColor Gray
Write-Host "  5. [评估] 自动化优胜劣汰 → 保留最优方案" -ForegroundColor Gray
Write-Host ""

exit $exitCode
