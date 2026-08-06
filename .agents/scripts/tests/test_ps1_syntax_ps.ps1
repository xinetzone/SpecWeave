#Requires -Version 5.1
<#
.SYNOPSIS
    测试 encoding-safety.ps1 中括号深度感知函数的正确性。
    对应 Python 端 test_ps1_syntax.py 的核心测试场景。
#>

$ErrorActionPreference = 'Stop'

# 直接运行时执行版本校验（dot-source 时由调用方负责）
if ($MyInvocation.InvocationName -ne '.') {
    . "$PSScriptRoot/../lib/pwsh7-version-check.ps1"
    if (-not (Test-Pwsh7Version)) {
        Show-Pwsh7VersionError
    }
}

# 引入 encoding-safety.ps1（包含括号深度感知函数）
. "$PSScriptRoot/../lib/encoding-safety.ps1"

$passed = 0
$failed = 0

function Test-Case {
    param(
        [string]$Name,
        [string]$Content,
        [int]$ExpectedPos,
        [string]$ExpectedPrefix = ""
    )
    $result = Find-Ps1TopLevelInsertPoint -Content $Content
    $ok = ($result -eq $ExpectedPos)
    $prefixOk = $true
    if ($ExpectedPrefix) {
        $actualPrefix = $Content.Substring($result, [Math]::Min($ExpectedPrefix.Length, $Content.Length - $result))
        $prefixOk = ($actualPrefix -eq $ExpectedPrefix)
        $ok = $ok -and $prefixOk
    }
    if ($ok) {
        Write-Host "  PASS $Name (pos=$result)" -ForegroundColor Green
        $script:passed++
    } else {
        Write-Host "  FAIL $Name (expected=$ExpectedPos, got=$result)" -ForegroundColor Red
        if ($ExpectedPrefix -and -not $prefixOk) {
            Write-Host "       expected prefix: $ExpectedPrefix" -ForegroundColor DarkGray
            $actualAt = $Content.Substring($result, [Math]::Min(60, $Content.Length - $result)).Replace("`n", '\n')
            Write-Host "       actual at pos=$result : $actualAt" -ForegroundColor DarkGray
        }
        $script:failed++
    }
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Testing Find-Ps1TopLevelInsertPoint (PowerShell)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: 脚本级 param() - 应在 param 块后插入
$content1 = @"
param(
    [string]`$Name = "World"
)
Write-Host "Hello `$Name"
"@
$p1 = Find-Ps1TopLevelInsertPoint -Content $content1
Test-Case -Name "1. 脚本级 param() - 在param块后插入" -Content $content1 -ExpectedPos $p1 -ExpectedPrefix "Write-Host"

# Test 2: 函数内 param() - 应在 function 前插入
$content2 = @"
function Get-Greeting {
    param(
        [string]`$Name
    )
    return "Hello `$Name"
}
Get-Greeting
"@
Test-Case -Name "2. 函数内 param() - 在function前插入" -Content $content2 -ExpectedPos 0 -ExpectedPrefix "function"

# Test 3: 头部注释块 + 脚本级 param()
$content3 = @"
<#
.SYNOPSIS
    测试脚本
#>
param(
    [string]`$Path
)
Get-ChildItem `$Path
"@
$p3 = Find-Ps1TopLevelInsertPoint -Content $content3
Test-Case -Name "3. 头部注释块 + 脚本级param()" -Content $content3 -ExpectedPos $p3 -ExpectedPrefix "Get-ChildItem"

# Test 4: 嵌套函数
$content4 = @"
function Outer {
    param([string]`$x)
    function Inner {
        param([string]`$y)
        return `$y
    }
    return Inner `$x
}
Outer "hello"
"@
Test-Case -Name "4. 嵌套函数 - 在第一个function前" -Content $content4 -ExpectedPos 0 -ExpectedPrefix "function"

# Test 5: 字符串中的假括号
$content5 = @"
`$msg = "This is { not a real brace } and # not a comment"
Write-Host `$msg
"@
Test-Case -Name "5. 字符串中的假括号" -Content $content5 -ExpectedPos 0 -ExpectedPrefix '$msg'

# Test 7: 行注释中的假括号
$content7 = @"
# This is a comment { fake braces }
# Another comment line
Write-Host "real code starts here"
"@
$p7 = Find-Ps1TopLevelInsertPoint -Content $content7
Test-Case -Name "7. 行注释中的假括号" -Content $content7 -ExpectedPos $p7 -ExpectedPrefix "Write-Host"

# Test 9: 脚本级 if/else
$content9 = @"
if (`$IsWindows) {
    Write-Host "Windows"
} else {
    Write-Host "Other"
}
"@
Test-Case -Name "9. 脚本级if/else" -Content $content9 -ExpectedPos 0 -ExpectedPrefix "if"

# Test 16: dot-source
$content16 = @"
. "`$PSScriptRoot/lib.ps1"
`$config = Get-Config
"@
Test-Case -Name "16. dot-source引用" -Content $content16 -ExpectedPos 0 -ExpectedPrefix "."

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Testing Get-Ps1BraceDepth" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Test brace depth at various points
$bd1 = Get-Ps1BraceDepth -Content "function f { param(`$x) `"hi`" }"
if ($bd1 -eq 0) { Write-Host "  PASS brace-depth: after complete function = 0" -ForegroundColor Green; $script:passed++ }
else { Write-Host "  FAIL brace-depth: after complete function expected 0 got $bd1" -ForegroundColor Red; $script:failed++ }

$bd2 = Get-Ps1BraceDepth -Content "function f { param(`$x)"
if ($bd2 -eq 1) { Write-Host "  PASS brace-depth: inside function = 1" -ForegroundColor Green; $script:passed++ }
else { Write-Host "  FAIL brace-depth: inside function expected 1 got $bd2" -ForegroundColor Red; $script:failed++ }

$bd3 = Get-Ps1BraceDepth -Content '`$s = "{ fake }" # comment { also fake }'
if ($bd3 -eq 0) { Write-Host "  PASS brace-depth: braces in strings/comments = 0" -ForegroundColor Green; $script:passed++ }
else { Write-Host "  FAIL brace-depth: strings/comments expected 0 got $bd3" -ForegroundColor Red; $script:failed++ }

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Testing Add-Ps1CodeAtTopLevel" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Test: insert code before function
$original = @"
function Test-Func {
    param([int]`$x)
    return `$x
}
"@
$toInsert = "# INSERTED CHECK`n"
$result = Add-Ps1CodeAtTopLevel -Content $original -CodeToInsert $toInsert
if ($result.StartsWith("# INSERTED CHECK")) {
    Write-Host "  PASS Add-Ps1CodeAtTopLevel: inserted before function" -ForegroundColor Green
    $script:passed++
} else {
    Write-Host "  FAIL Add-Ps1CodeAtTopLevel: expected INSERTED CHECK at start" -ForegroundColor Red
    $script:failed++
}

# Test: insert code after script-level param
$original2 = @"
param([string]`$Name)
Write-Host `$Name
"@
$result2 = Add-Ps1CodeAtTopLevel -Content $original2 -CodeToInsert "# VERSION CHECK`n"
if ($result2 -match '(?s)# VERSION CHECK.*Write-Host') {
    Write-Host "  PASS Add-Ps1CodeAtTopLevel: inserted after param block" -ForegroundColor Green
    $script:passed++
} else {
    Write-Host "  FAIL Add-Ps1CodeAtTopLevel: expected VERSION CHECK before Write-Host" -ForegroundColor Red
    Write-Host "       result: $($result2.Substring(0, [Math]::Min(100, $result2.Length)))" -ForegroundColor DarkGray
    $script:failed++
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Results: $passed passed, $failed failed" -ForegroundColor $(if ($failed -eq 0) { 'Green' } else { 'Red' })
Write-Host "============================================================" -ForegroundColor Cyan

if ($failed -gt 0) { exit 1 }
