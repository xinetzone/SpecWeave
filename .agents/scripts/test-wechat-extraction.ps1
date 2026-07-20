# test-wechat-extraction.ps1
# 微信公众号内容提取验证脚本
# 功能：验证 defuddle CLI 是否可用，并对测试 URL 进行提取验证

param(
    [string]$TestUrl = "https://mp.weixin.qq.com/s/5Hwn3et9k-XtEATC-SDR6A"
)

. (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "lib\encoding-safety.ps1")


Write-Host "=== 微信公众号内容提取验证 ===" -ForegroundColor Cyan

# 1. 检查 defuddle 是否可用
Write-Host "`n[1/3] 检查 defuddle CLI 可用性..." -ForegroundColor Yellow
try {
    $defuddleVersion = npx defuddle --version 2>&1
    Write-Host "  defuddle 可用: $defuddleVersion" -ForegroundColor Green
} catch {
    Write-Host "  defuddle 未安装或不可用，尝试安装..." -ForegroundColor Red
    try {
        npx --yes defuddle --version 2>&1 | Out-Null
        Write-Host "  defuddle 安装成功" -ForegroundColor Green
    } catch {
        Write-Host "  defuddle 安装失败: $_" -ForegroundColor Red
        exit 1
    }
}

# 2. 测试提取
Write-Host "`n[2/3] 测试提取微信公众号文章..." -ForegroundColor Yellow
$tempFile = [System.IO.Path]::GetTempPath() + "wechat-test-" + (Get-Date -Format "yyyyMMddHHmmss") + ".md"
try {
    $result = npx defuddle $TestUrl 2>&1 | Out-String
    if ($result.Length -gt 100) {
        [System.IO.File]::WriteAllText($tempFile, $result, $Utf8NoBomSingleton)
        Write-Host "  提取成功: $(($result | Select-String -Pattern '\S').Count) 行内容" -ForegroundColor Green
        Write-Host "  临时文件: $tempFile" -ForegroundColor Gray
    } else {
        Write-Host "  提取失败: 返回内容过短 ($($result.Length) 字符)" -ForegroundColor Red
        Write-Host "  原始输出: $result" -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Host "  提取异常: $_" -ForegroundColor Red
    exit 1
}

# 3. 质量检查
Write-Host "`n[3/3] 内容质量检查..." -ForegroundColor Yellow
$content = Get-Content $tempFile -Raw -Encoding UTF8
$checks = @{
    "包含标题" = ($content -match "^#\s+") -or ($content -match "^\S.*\n=+")
    "包含段落" = ($content.Length -gt 500)
    "包含链接" = ($content -match "https?://")
    "无错误信息" = ($content -notmatch "(?i)(error|failed|timeout|4\d{2}|5\d{2})")
}
$allPassed = $true
foreach ($check in $checks.GetEnumerator()) {
    $status = if ($check.Value) { "PASS" } else { "FAIL" }
    $color = if ($check.Value) { "Green" } else { "Red" }
    Write-Host "  [$status] $($check.Key)" -ForegroundColor $color
    if (-not $check.Value) { $allPassed = $false }
}

Write-Host "`n=== 验证结果 ===" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "所有检查通过，defuddle 正常可用" -ForegroundColor Green
    exit 0
} else {
    Write-Host "部分检查未通过，请检查输出" -ForegroundColor Red
    Write-Host "临时文件保留: $tempFile" -ForegroundColor Gray
    exit 1
}
