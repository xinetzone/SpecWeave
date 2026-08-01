$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "common.ps1")

$parsed = Parse-Arguments -Arguments $args -Defaults @{
    format = "markdown"
    iterations = 20
    "code-understandable" = $null
    changelog = $null
    "human-involvement" = $null
    "verifier-quality" = $null
    "review-mechanism" = $null
}

$Format = Get-Format $parsed
$ConfigPath = Get-Config $parsed
$configData = Load-ConfigFile $ConfigPath

function Get-IntParam {
    param($Key, $Default = 20)
    if ($parsed.ContainsKey($Key) -and $null -ne $parsed[$Key]) { return [int]$parsed[$Key] }
    if ($configData -and $null -ne $configData.$Key) { return [int]$configData.$Key }
    return $Default
}

function Get-BoolParamDeep {
    param($Key, $SubKey)
    $k = $Key -replace "_", "-"
    if ($parsed.ContainsKey($k) -and $null -ne $parsed[$k]) { return $parsed[$k] }
    if ($configData -and $configData.$Key -and $null -ne $configData.$Key.$SubKey) { return [bool]$configData.$Key.$SubKey }
    return $null
}

$Iterations = 20
if ($parsed.ContainsKey("iterations") -and $null -ne $parsed["iterations"]) { $Iterations = [int]$parsed["iterations"] }
if ($configData -and $null -ne $configData.iterations) { $Iterations = [int]$configData.iterations }

$CodeUnderstandable = $null
$Changelog = $null
$HumanInvolvement = $null
$VerifierQuality = $null
$ReviewMechanism = $null

if ($parsed.ContainsKey("code-understandable") -and $null -ne $parsed["code-understandable"]) { $CodeUnderstandable = $parsed["code-understandable"] }
elseif ($configData -and $configData.comprehension -and $null -ne $configData.comprehension.codeUnderstandable) { $CodeUnderstandable = [bool]$configData.comprehension.codeUnderstandable }

if ($parsed.ContainsKey("changelog") -and $null -ne $parsed["changelog"]) { $Changelog = $parsed["changelog"] }
elseif ($configData -and $configData.comprehension -and $null -ne $configData.comprehension.changelog) { $Changelog = [bool]$configData.comprehension.changelog }

if ($parsed.ContainsKey("human-involvement") -and $null -ne $parsed["human-involvement"]) { $HumanInvolvement = $parsed["human-involvement"] }
elseif ($configData -and $configData.cognitive -and $null -ne $configData.cognitive.humanInvolvement) { $HumanInvolvement = [bool]$configData.cognitive.humanInvolvement }

if ($parsed.ContainsKey("verifier-quality") -and $null -ne $parsed["verifier-quality"]) { $VerifierQuality = $parsed["verifier-quality"] }
elseif ($configData -and $configData.cognitive -and $null -ne $configData.cognitive.verifierQuality) { $VerifierQuality = [bool]$configData.cognitive.verifierQuality }

if ($parsed.ContainsKey("review-mechanism") -and $null -ne $parsed["review-mechanism"]) { $ReviewMechanism = $parsed["review-mechanism"] }
elseif ($configData -and $configData.cognitive -and $null -ne $configData.cognitive.reviewMechanism) { $ReviewMechanism = [bool]$configData.cognitive.reviewMechanism }

$risks = @()
$comprehensionScore = 0
$cognitiveScore = 0

if ($Iterations -le 15) {
    $comprehensionScore++
    $risks += @{ category = "理解债"; name = "迭代次数评估"; level = "low"; passed = $true; detail = "迭代次数$($Iterations)轮，在安全范围内（≤15轮）"; recommendation = "" }
} elseif ($Iterations -le 25) {
    $comprehensionScore += 0.5
    $risks += @{ category = "理解债"; name = "迭代次数评估"; level = "medium"; passed = $true; detail = "迭代次数$($Iterations)轮，中等复杂度（16-25轮）"; recommendation = "建议增加变更日志要求，关键节点人工审查" }
} else {
    $risks += @{ category = "理解债"; name = "迭代次数评估"; level = "high"; passed = $false; detail = "迭代次数$($Iterations)轮，超过建议上限（>25轮）"; recommendation = "迭代次数过多会累积理解债，建议降低到25轮以内或分阶段执行" }
}

if ($CodeUnderstandable -eq $true) {
    $comprehensionScore++
    $risks += @{ category = "理解债"; name = "代码可理解性"; level = "low"; passed = $true; detail = "有保持代码可理解性的措施"; recommendation = "" }
} else {
    $risks += @{ category = "理解债"; name = "代码可理解性"; level = "high"; passed = $false; detail = "没有措施保持代码可理解性"; recommendation = "必须要求代码保持可读性，禁止过度优化导致的代码晦涩；建议添加代码规范检查" }
}

if ($Changelog -eq $true) {
    $comprehensionScore++
    $risks += @{ category = "理解债"; name = "变更日志完整性"; level = "low"; passed = $true; detail = "有完整的变更日志记录"; recommendation = "" }
} else {
    $risks += @{ category = "理解债"; name = "变更日志完整性"; level = "medium"; passed = $false; detail = "缺少变更日志"; recommendation = "必须记录每次迭代的变更原因和内容，便于人类理解演进过程" }
}

if ($HumanInvolvement -eq $true) {
    $cognitiveScore++
    $risks += @{ category = "认知让渡"; name = "人类参与度"; level = "low"; passed = $true; detail = "有人类参与关键节点"; recommendation = "" }
} else {
    $risks += @{ category = "认知让渡"; name = "人类参与度"; level = "high"; passed = $false; detail = "完全自动化无人类参与"; recommendation = "人类必须参与验证器设计和关键节点审查，不能完全交给Loop" }
}

if ($VerifierQuality -eq $true) {
    $cognitiveScore++
    $risks += @{ category = "认知让渡"; name = "验证器设计质量"; level = "low"; passed = $true; detail = "验证器由人类设计审核"; recommendation = "" }
} else {
    $risks += @{ category = "认知让渡"; name = "验证器设计质量"; level = "high"; passed = $false; detail = "验证器设计质量无保障"; recommendation = "验证器必须由人类设计并审核，不能让Agent自己设计裁判" }
}

if ($ReviewMechanism -eq $true) {
    $cognitiveScore++
    $risks += @{ category = "认知让渡"; name = "结果审查机制"; level = "low"; passed = $true; detail = "有结果审查机制"; recommendation = "" }
} else {
    $risks += @{ category = "认知让渡"; name = "结果审查机制"; level = "medium"; passed = $false; detail = "缺少结果审查机制"; recommendation = "最终结果必须经过人工验收，不能直接采用Loop输出" }
}

$highRisks = ($risks | Where-Object { $_.level -eq "high" }).Count
$mediumRisks = ($risks | Where-Object { $_.level -eq "medium" }).Count

if ($highRisks -eq 0 -and $mediumRisks -eq 0) {
    $riskLevel = "低"
    $riskColor = "Green"
    $exitCode = 0
} elseif ($highRisks -eq 0) {
    $riskLevel = "中"
    $riskColor = "Yellow"
    $exitCode = 2
} else {
    $riskLevel = "高"
    $riskColor = "Red"
    $exitCode = 1
}

if ($Format -eq "json") {
    $output = @{
        command = "assess-risks"
        summary = @{
            risk_level = $riskLevel
            high_risks = $highRisks
            medium_risks = $mediumRisks
            comprehension_score = $comprehensionScore
            cognitive_score = $cognitiveScore
            exit_code = $exitCode
        }
        risks = $risks
    }
    $output | ConvertTo-Json -Depth 10
    exit $exitCode
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Loop Engineering - 风险评估" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "综合风险等级: $riskLevel" -ForegroundColor $riskColor
Write-Host "  高风险项: $highRisks" -ForegroundColor $(if ($highRisks -gt 0) { "Red" } else { "Green" })
Write-Host "  中风险项: $mediumRisks" -ForegroundColor $(if ($mediumRisks -gt 0) { "Yellow" } else { "Green" })
Write-Host "  理解债得分: $comprehensionScore / 3" -ForegroundColor White
Write-Host "  认知让渡得分: $cognitiveScore / 3" -ForegroundColor White
Write-Host ""

$categories = $risks | Group-Object category
foreach ($cat in $categories) {
    Write-Host "[$($cat.Name)]" -ForegroundColor Yellow
    foreach ($risk in $cat.Group) {
        $levelColor = switch ($risk.level) {
            "low" { "Green" }
            "medium" { "Yellow" }
            "high" { "Red" }
        }
        $icon = switch ($risk.level) {
            "low" { "[OK]" }
            "medium" { "[!]" }
            "high" { "[!!]" }
        }
        Write-Host "  $icon [$($risk.level.ToUpper())] $($risk.name)" -ForegroundColor $levelColor
        Write-Host "       $($risk.detail)" -ForegroundColor Gray
        if ($risk.recommendation) {
            Write-Host "       建议: $($risk.recommendation)" -ForegroundColor DarkYellow
        }
    }
    Write-Host ""
}

if ($highRisks -gt 0) {
    Write-Host "[!!] 高风险防范建议:" -ForegroundColor Red
    Write-Host "  1. 理解债风险：限制迭代次数≤25轮，强制变更日志，关键节点人工审查" -ForegroundColor Red
    Write-Host "  2. 认知让渡风险：人类必须设计验证器，最终结果人工验收，保留终止开关" -ForegroundColor Red
    Write-Host ""
} elseif ($mediumRisks -gt 0) {
    Write-Host "[!] 中风险提示:" -ForegroundColor Yellow
    Write-Host "  建议按照上述推荐项补充防护措施后再运行Loop。" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "[OK] 风险控制良好！" -ForegroundColor Green
    Write-Host "  理解债和认知让渡风险均有有效防范措施。" -ForegroundColor Green
    Write-Host ""
}

Write-Host "核心风险说明:" -ForegroundColor Yellow
Write-Host "  理解债：迭代过多、代码变难理解，最终人类无法维护" -ForegroundColor Gray
Write-Host "  认知让渡：过度依赖Loop，人类失去对系统的理解和控制" -ForegroundColor Gray
Write-Host ""

exit $exitCode
