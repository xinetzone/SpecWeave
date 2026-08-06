#Requires -Version 5.1
<#
.SYNOPSIS
    PS1 语法分析统一测试套件（PowerShell 端）。
.DESCRIPTION
    读取由 lib/ps1_test_cases.py 导出的 JSON 测试数据（ps1_syntax_cases.json），
    对 encoding-safety.ps1 中的以下函数执行跨语言对齐验证：
      - Find-Ps1TopLevelInsertPoint  （顶层插入点查找）
      - Get-Ps1BraceDepth            （括号深度计算）
      - Skip-Ps1HereString           （here-string 跳过原语）
      - Add-Ps1CodeAtTopLevel        （代码端到端插入）

    测试用例与 Python 端（test_ps1_syntax.py）完全共享同一数据源，
    确保双端语法分析逻辑一致性。

    运行方式：
      pwsh -File .agents/scripts/tests/test_ps1_syntax_unified.ps1
      powershell -ExecutionPolicy Bypass -File .agents/scripts/tests/test_ps1_syntax_unified.ps1
#>

$ErrorActionPreference = 'Stop'

# ── 路径定位 ──────────────────────────────────────────────────────────────
$Script:TestsDir = $PSScriptRoot
$Script:ScriptsDir = Split-Path $TestsDir -Parent
$Script:LibDir = Join-Path $ScriptsDir 'lib'
$Script:CasesJson = Join-Path $TestsDir 'ps1_syntax_cases.json'

# ── 版本校验（仅直接运行时）──────────────────────────────────────────────
if ($MyInvocation.InvocationName -ne '.') {
    . (Join-Path $LibDir 'pwsh7-version-check.ps1')
    if (-not (Test-Pwsh7Version)) {
        Show-Pwsh7VersionError
        exit 1
    }
}

# ── 引入被测模块 ─────────────────────────────────────────────────────────
. (Join-Path $LibDir 'encoding-safety.ps1')

# ── 加载共享测试用例 ─────────────────────────────────────────────────────
if (-not (Test-Path $CasesJson)) {
    Write-Host "ERROR: Test cases JSON not found at: $CasesJson" -ForegroundColor Red
    Write-Host "Please run: python -m lib.ps1_test_cases --export-json" -ForegroundColor Yellow
    exit 1
}

$Script:Cases = Get-Content $CasesJson -Raw -Encoding UTF8 | ConvertFrom-Json

# ── 版本检测测试用例 ──
$VersionDetectCases = @()
if ($Script:Cases.PSObject.Properties.Name -contains 'version_detect_cases') {
    $VersionDetectCases = $Script:Cases.version_detect_cases
}

# ── 测试统计 ─────────────────────────────────────────────────────────────
$Script:Passed = 0
$Script:Failed = 0
$Script:Failures = [System.Collections.ArrayList]::new()

function Write-TestCaseResult {
    param(
        [string]$Category,
        [string]$Id,
        [string]$Name,
        [bool]$Ok,
        [string]$Message
    )
    if ($Ok) {
        $Script:Passed++
        Write-Host "  PASS [$Category/$Id] $Name" -ForegroundColor Green
        if ($Message) { Write-Host "        $Message" -ForegroundColor DarkGray }
    } else {
        $Script:Failed++
        [void]$Script:Failures.Add(@{ Category = $Category; Id = $Id; Name = $Name; Message = $Message })
        Write-Host "  FAIL [$Category/$Id] $Name" -ForegroundColor Red
        Write-Host "        $Message" -ForegroundColor DarkGray
    }
}

# ── 辅助：安全 Substring ─────────────────────────────────────────────────
function Get-SafeSubstring {
    param([string]$Text, [int]$Start, [int]$Length = 60)
    if ($Start -ge $Text.Length) { return '' }
    $actualLen = [Math]::Min($Length, $Text.Length - $Start)
    return $Text.Substring($Start, $actualLen).Replace("`n", '\n').Replace("`r", '\r')
}

# ══════════════════════════════════════════════════════════════════════════
#  测试类别 1: Find-Ps1TopLevelInsertPoint（顶层插入点）
# ══════════════════════════════════════════════════════════════════════════
function Test-InsertPointCases {
    Write-Host ""
    Write-Host "── Insert Point Tests ──" -ForegroundColor Cyan

    foreach ($case in $Script:Cases.insert_point_cases) {
        $content = $case.content
        $searchFrom = $case.search_from
        $expectedKeyword = $case.expected_keyword
        $expectedMinPos = $case.expected_min_pos

        # 调用被测函数
        try {
            $insertPos = Find-Ps1TopLevelInsertPoint -Content $content -SearchFrom $searchFrom
        } catch {
            Write-TestCaseResult -Category "InsertPoint" -Id $case.id -Name $case.name `
                -Ok $false -Message "EXCEPTION: $_"
            continue
        }

        $issues = [System.Collections.ArrayList]::new()

        # 1. 验证插入点位置范围
        if ($insertPos -lt $expectedMinPos) {
            [void]$issues.Add("insertPos=$insertPos < expectedMinPos=$expectedMinPos")
        }
        if ($insertPos -gt $content.Length) {
            [void]$issues.Add("insertPos=$insertPos > len=$($content.Length)")
        }

        # 2. 验证插入点附近包含期望关键词
        if ($expectedKeyword) {
            $windowStart = $insertPos
            $windowEnd = [Math]::Min($insertPos + 200, $content.Length)
            $window = $content.Substring($windowStart, $windowEnd - $windowStart)
            $foundInWindow = $window -like "*$expectedKeyword*"
            $foundInPre = $false
            if (-not $foundInWindow) {
                $preStart = [Math]::Max(0, $insertPos - 50)
                $preLen = $insertPos - $preStart
                if ($preLen -gt 0) {
                    $preWindow = $content.Substring($preStart, $preLen)
                    $foundInPre = $preWindow -like "*$expectedKeyword*"
                }
            }
            if (-not $foundInWindow -and -not $foundInPre) {
                [void]$issues.Add("keyword '$expectedKeyword' not found near insertPos=$insertPos")
            }
        }

        # 3. 验证插入点处括号深度为 0
        if ($insertPos -gt 0 -and $insertPos -lt $content.Length) {
            $preContent = $content.Substring(0, $insertPos)
            if ($preContent.Length -gt 0) {
                $depth = Get-Ps1BraceDepth -Content $preContent
                if ($depth -ne 0) {
                    [void]$issues.Add("braceDepth at insertPos=$insertPos is $depth, expected 0")
                }
            }
        }

        # 4. 验证整体括号平衡
        $fullDepth = Get-Ps1BraceDepth -Content $content
        if ($fullDepth -ne 0) {
            [void]$issues.Add("full braceDepth=$fullDepth, expected 0")
        }

        $snippet = Get-SafeSubstring -Text $content -Start $insertPos -Length 60
        if ($issues.Count -gt 0) {
            $msg = ($issues -join '; ') + " | next=`"$snippet...`""
            Write-TestCaseResult -Category "InsertPoint" -Id $case.id -Name $case.name -Ok $false -Message $msg
        } else {
            $msg = "insertPos=$insertPos, next=`"$snippet...`""
            Write-TestCaseResult -Category "InsertPoint" -Id $case.id -Name $case.name -Ok $true -Message $msg
        }
    }
}

# ══════════════════════════════════════════════════════════════════════════
#  测试类别 2: Get-Ps1BraceDepth（括号深度）
# ══════════════════════════════════════════════════════════════════════════
function Test-BraceDepthCases {
    Write-Host ""
    Write-Host "── Brace Depth Tests ──" -ForegroundColor Cyan

    foreach ($case in $Script:Cases.brace_depth_cases) {
        $content = $case.content
        $endPos = if ($case.end_pos -ge 0) { $case.end_pos } else { $content.Length }
        $expectedDepth = $case.expected_depth

        try {
            $depth = Get-Ps1BraceDepth -Content $content -EndPos $endPos
        } catch {
            Write-TestCaseResult -Category "BraceDepth" -Id $case.id -Name $case.name `
                -Ok $false -Message "EXCEPTION: $_"
            continue
        }

        if ($depth -ne $expectedDepth) {
            Write-TestCaseResult -Category "BraceDepth" -Id $case.id -Name $case.name `
                -Ok $false -Message "braceDepth=$depth, expected $expectedDepth"
        } else {
            Write-TestCaseResult -Category "BraceDepth" -Id $case.id -Name $case.name `
                -Ok $true -Message "braceDepth=$depth"
        }
    }
}

# ══════════════════════════════════════════════════════════════════════════
#  测试类别 3: Skip-Ps1HereString（here-string 跳过原语）
# ══════════════════════════════════════════════════════════════════════════
function Test-HereStringCases {
    Write-Host ""
    Write-Host "── Here-string Primitive Tests ──" -ForegroundColor Cyan

    foreach ($case in $Script:Cases.here_string_cases) {
        $content = $case.content
        $position = $case.position
        $expectedNewPos = $case.expected_new_pos

        try {
            $targetVer = if ($case.PSObject.Properties.Name -contains 'target_version' -and $case.target_version) { $case.target_version } else { 'auto' }
            $newPos = Skip-Ps1HereString -Content $content -Position $position -TargetVersion $targetVer
        } catch {
            Write-TestCaseResult -Category "HereString" -Id $case.id -Name $case.name `
                -Ok $false -Message "EXCEPTION: $_"
            continue
        }

        if ($newPos -ne $expectedNewPos) {
            $snippet = Get-SafeSubstring -Text $content -Start $position -Length 30
            Write-TestCaseResult -Category "HereString" -Id $case.id -Name $case.name `
                -Ok $false -Message ("newPos={0}, expected {1} | at pos={2}: `"{3}...`"" -f $newPos,$expectedNewPos,$position,$snippet)
        } else {
            Write-TestCaseResult -Category "HereString" -Id $case.id -Name $case.name `
                -Ok $true -Message "newPos=$newPos"
        }
    }
}

# ══════════════════════════════════════════════════════════════════════════
#  测试类别 4: Add-Ps1CodeAtTopLevel（代码端到端插入）
# ══════════════════════════════════════════════════════════════════════════
function Test-InsertCodeCases {
    Write-Host ""
    Write-Host "── Code Insertion Tests ──" -ForegroundColor Cyan

    foreach ($case in $Script:Cases.insert_code_cases) {
        $content = $case.content
        $codeToInsert = $case.code_to_insert
        $searchFrom = $case.search_from
        $expectedStartsWith = $case.expected_starts_with
        $expectedContains = $case.expected_contains

        try {
            $result = Add-Ps1CodeAtTopLevel -Content $content -CodeToInsert $codeToInsert -SearchFrom $searchFrom
        } catch {
            Write-TestCaseResult -Category "InsertCode" -Id $case.id -Name $case.name `
                -Ok $false -Message "EXCEPTION: $_"
            continue
        }

        $issues = [System.Collections.ArrayList]::new()

        if ($expectedStartsWith) {
            if (-not $result.StartsWith($expectedStartsWith)) {
                [void]$issues.Add("result does not start with '$expectedStartsWith'")
            }
        }

        if ($expectedContains) {
            if ($result -notlike "*$expectedContains*") {
                [void]$issues.Add("result does not contain '$expectedContains'")
            }
        }

        # 验证插入后括号平衡
        $depth = Get-Ps1BraceDepth -Content $result
        if ($depth -ne 0) {
            [void]$issues.Add("braceDepth after insertion is $depth, expected 0")
        }

        $snippet = Get-SafeSubstring -Text $result -Start 0 -Length 100
        if ($issues.Count -gt 0) {
            Write-TestCaseResult -Category "InsertCode" -Id $case.id -Name $case.name `
                -Ok $false -Message (($issues -join '; ') + " | result: `"$snippet...`"")
        } else {
            Write-TestCaseResult -Category "InsertCode" -Id $case.id -Name $case.name `
                -Ok $true -Message "result: `"$snippet...`""
        }
    }
}

# ══════════════════════════════════════════════════════════════════════════
#  测试类别 5: Get-Ps1TargetVersion（版本自动检测）
# ══════════════════════════════════════════════════════════════════════════
function Test-VersionDetectCases {
    Write-Host "`n───────────────────────────────────────────────────────────────────────────────" -ForegroundColor Cyan
    Write-Host "  Version Detection Tests (跨平台版本自动检测)" -ForegroundColor Cyan
    Write-Host "───────────────────────────────────────────────────────────────────────────────" -ForegroundColor Cyan
    Write-Host ""

    $VersionDetectPassed = 0
    $VersionDetectFailed = 0
    foreach ($case in $VersionDetectCases) {
        $result = Get-Ps1TargetVersion -Content $case.content
        if ($result -eq $case.expected_version) {
            Write-Host "  PASS [VersionDetect/$($case.id)] $($case.name)" -ForegroundColor Green
            $Script:Passed++
            $VersionDetectPassed++
        } else {
            Write-Host "  FAIL [VersionDetect/$($case.id)] $($case.name): expected '$($case.expected_version)', got '$result'" -ForegroundColor Red
            $Script:Failed++
            $VersionDetectFailed++
            [void]$Script:Failures.Add(@{ Category = "VersionDetect"; Id = $case.id; Name = $case.name; Message = "expected '$($case.expected_version)', got '$result'" })
        }
    }
    Write-Host "  Version Detection 结果: $VersionDetectPassed passed, $VersionDetectFailed failed" -ForegroundColor $(if ($VersionDetectFailed -eq 0) { 'Green' } else { 'Red' })
}

# ══════════════════════════════════════════════════════════════════════════
#  测试类别 6: TargetVersion 模式验证（5.1/7.x 换行符差异）
# ══════════════════════════════════════════════════════════════════════════
function Test-TargetVersionMode {
    Write-Host "`n───────────────────────────────────────────────────────────────────────────────" -ForegroundColor Cyan
    Write-Host "  TargetVersion Mode Tests (5.1/7.x 换行符模式验证)" -ForegroundColor Cyan
    Write-Host "───────────────────────────────────────────────────────────────────────────────" -ForegroundColor Cyan
    Write-Host ""

    $TargetVersionPassed = 0
    $TargetVersionFailed = 0

    # Test 1: Resolve explicit 5.1 overrides content
    $result = Resolve-Ps1TargetVersion -Content '$x = $y ?? 1' -TargetVersion '5.1'
    if ($result -eq '5.1') {
        Write-Host "  PASS [TargetVer/explicit_51] 显式 5.1 覆盖内容检测" -ForegroundColor Green
        $Script:Passed++; $TargetVersionPassed++
    } else {
        Write-Host "  FAIL [TargetVer/explicit_51] 显式 5.1 应返回 5.1, got $result" -ForegroundColor Red
        $Script:Failed++; $TargetVersionFailed++
        [void]$Script:Failures.Add(@{ Category = "TargetVer"; Id = "explicit_51"; Name = "显式 5.1 覆盖内容检测"; Message = "expected '5.1', got '$result'" })
    }

    # Test 2: Resolve explicit 7.x overrides content
    $result = Resolve-Ps1TargetVersion -Content "#Requires -Version 5`nGet-Process" -TargetVersion '7.x'
    if ($result -eq '7.x') {
        Write-Host "  PASS [TargetVer/explicit_7x] 显式 7.x 覆盖内容检测" -ForegroundColor Green
        $Script:Passed++; $TargetVersionPassed++
    } else {
        Write-Host "  FAIL [TargetVer/explicit_7x] 显式 7.x 应返回 7.x, got $result" -ForegroundColor Red
        $Script:Failed++; $TargetVersionFailed++
        [void]$Script:Failures.Add(@{ Category = "TargetVer"; Id = "explicit_7x"; Name = "显式 7.x 覆盖内容检测"; Message = "expected '7.x', got '$result'" })
    }

    # Test 3: Auto-detect from #Requires -Version 5
    $result = Resolve-Ps1TargetVersion -Content "#Requires -Version 5`nGet-Process" -TargetVersion 'auto'
    if ($result -eq '5.1') {
        Write-Host "  PASS [TargetVer/auto_51] auto 模式检测 Requires -Version 5 → 5.1" -ForegroundColor Green
        $Script:Passed++; $TargetVersionPassed++
    } else {
        Write-Host "  FAIL [TargetVer/auto_51] auto 应检测为 5.1, got $result" -ForegroundColor Red
        $Script:Failed++; $TargetVersionFailed++
        [void]$Script:Failures.Add(@{ Category = "TargetVer"; Id = "auto_51"; Name = "auto 模式检测 Requires -Version 5"; Message = "expected '5.1', got '$result'" })
    }

    # Test 4: Auto-detect from ?? operator
    $result = Resolve-Ps1TargetVersion -Content '$x = $y ?? 1' -TargetVersion 'auto'
    if ($result -eq '7.x') {
        Write-Host "  PASS [TargetVer/auto_7x_op] auto 模式检测 ?? 运算符 → 7.x" -ForegroundColor Green
        $Script:Passed++; $TargetVersionPassed++
    } else {
        Write-Host "  FAIL [TargetVer/auto_7x_op] auto 应检测为 7.x, got $result" -ForegroundColor Red
        $Script:Failed++; $TargetVersionFailed++
        [void]$Script:Failures.Add(@{ Category = "TargetVer"; Id = "auto_7x_op"; Name = "auto 模式检测 ?? 运算符"; Message = "expected '7.x', got '$result'" })
    }

    # Build test here-strings using char codes to avoid literal CR issues
    $CR = [char]13
    $LF = [char]10
    $CRLF = "$CR$LF"
    $hsCr = '@"' + $CR + 'line' + $CR + '"@'
    $hsCrlf = '@"' + $CRLF + 'line' + $CRLF + '"@'

    # Test 5: 7.x mode recognizes CR-only here-string
    $pos = Skip-Ps1HereString -Content $hsCr -Position 0 -TargetVersion '7.x'
    if ($pos -eq $hsCr.Length) {
        Write-Host "  PASS [TargetVer/hs_cr_7x] 7.x 模式识别 CR-only here-string (pos=$pos)" -ForegroundColor Green
        $Script:Passed++; $TargetVersionPassed++
    } else {
        Write-Host "  FAIL [TargetVer/hs_cr_7x] 7.x 应跳过整个 CR here-string (pos=$pos vs len=$($hsCr.Length))" -ForegroundColor Red
        $Script:Failed++; $TargetVersionFailed++
        [void]$Script:Failures.Add(@{ Category = "TargetVer"; Id = "hs_cr_7x"; Name = "7.x 模式识别 CR-only here-string"; Message = "pos=$pos, expected $($hsCr.Length)" })
    }

    # Test 6: 5.1 mode rejects CR-only here-string
    $pos = Skip-Ps1HereString -Content $hsCr -Position 0 -TargetVersion '5.1'
    if ($pos -eq 0) {
        Write-Host "  PASS [TargetVer/hs_cr_51_reject] 5.1 模式拒绝 CR-only here-string (pos=0)" -ForegroundColor Green
        $Script:Passed++; $TargetVersionPassed++
    } else {
        Write-Host "  FAIL [TargetVer/hs_cr_51_reject] 5.1 不应跳过 CR here-string (pos=$pos, expected 0)" -ForegroundColor Red
        $Script:Failed++; $TargetVersionFailed++
        [void]$Script:Failures.Add(@{ Category = "TargetVer"; Id = "hs_cr_51_reject"; Name = "5.1 模式拒绝 CR-only here-string"; Message = "pos=$pos, expected 0" })
    }

    # Test 7: 5.1 mode recognizes CRLF here-string
    $pos = Skip-Ps1HereString -Content $hsCrlf -Position 0 -TargetVersion '5.1'
    if ($pos -eq $hsCrlf.Length) {
        Write-Host "  PASS [TargetVer/hs_crlf_51] 5.1 模式识别 CRLF here-string (pos=$pos)" -ForegroundColor Green
        $Script:Passed++; $TargetVersionPassed++
    } else {
        Write-Host "  FAIL [TargetVer/hs_crlf_51] 5.1 应跳过 CRLF here-string (pos=$pos vs len=$($hsCrlf.Length))" -ForegroundColor Red
        $Script:Failed++; $TargetVersionFailed++
        [void]$Script:Failures.Add(@{ Category = "TargetVer"; Id = "hs_crlf_51"; Name = "5.1 模式识别 CRLF here-string"; Message = "pos=$pos, expected $($hsCrlf.Length)" })
    }

    Write-Host "  TargetVersion Mode 结果: $TargetVersionPassed passed, $TargetVersionFailed failed" -ForegroundColor $(if ($TargetVersionFailed -eq 0) { 'Green' } else { 'Red' })
}

# ══════════════════════════════════════════════════════════════════════════
#  主入口
# ══════════════════════════════════════════════════════════════════════════
function Main {
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "PS1 Syntax Unified Test Suite (PowerShell)" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "Test cases source: $Script:CasesJson" -ForegroundColor DarkGray
    Write-Host ""

    Test-InsertPointCases
    Test-BraceDepthCases
    Test-HereStringCases
    Test-InsertCodeCases
    Test-VersionDetectCases
    Test-TargetVersionMode

    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    $totalColor = if ($Script:Failed -eq 0) { 'Green' } else { 'Red' }
    Write-Host "Results: $Script:Passed passed, $Script:Failed failed (total $($Script:Passed + $Script:Failed))" -ForegroundColor $totalColor
    Write-Host "============================================================" -ForegroundColor Cyan

    if ($Script:Failed -gt 0) {
        Write-Host ""
        Write-Host "Failed cases summary:" -ForegroundColor Red
        foreach ($f in $Script:Failures) {
            Write-Host "  [$($f.Category)/$($f.Id)] $($f.Name)" -ForegroundColor Red
            Write-Host "    $($f.Message)" -ForegroundColor DarkGray
        }
        return 1
    }
    return 0
}

if ($MyInvocation.InvocationName -ne '.') {
    exit (Main)
}
