# UTF-8 Encoding Verification Script
# Usage: .\verify-encoding.ps1 [-Quiet] [-Json]

param(
    [switch]$Quiet,
    [switch]$Json
)

$ErrorActionPreference = 'Continue'

$origChcp = chcp
$origChcpMatch = [regex]::Match($origChcp, ':\s*(\d+)')
if ($origChcpMatch.Success) {
    $origCodePage = $origChcpMatch.Groups[1].Value
} else {
    $origCodePage = [string](Get-Culture).TextInfo.ANSICodePage
}
$origInputEnc = [Console]::InputEncoding
$origOutputEnc = [Console]::OutputEncoding
$origPSOutputEnc = $OutputEncoding
$origPYIO = $env:PYTHONIOENCODING
$origPYUTF8 = $env:PYTHONUTF8

chcp 65001 > $null 2>&1
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSDefaultParameterValues['*:Encoding'] = 'utf8'
}

$script:results = @()
$script:passCount = 0
$script:failCount = 0

function Add-Result {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Detail = ''
    )
    $script:results += [PSCustomObject]@{
        name   = $Name
        passed = $Passed
        detail = $Detail
    }
    if ($Passed) {
        $script:passCount++
    } else {
        $script:failCount++
    }
}

function Write-Result {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Detail = ''
    )
    Add-Result -Name $Name -Passed $Passed -Detail $Detail
    if (-not $Quiet -and -not $Json) {
        if ($Passed) {
            Write-Host '[PASS] ' -NoNewline -ForegroundColor Green
        } else {
            Write-Host '[FAIL] ' -NoNewline -ForegroundColor Red
        }
        Write-Host $Name -NoNewline -ForegroundColor White
        if ($Detail) {
            Write-Host ' - ' -NoNewline -ForegroundColor Gray
            Write-Host $Detail -ForegroundColor $(if ($Passed) { 'Gray' } else { 'Yellow' })
        } else {
            Write-Host ''
        }
    }
}

if (-not $Quiet -and -not $Json) {
    Write-Host ''
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host '  UTF-8 Encoding Verification' -ForegroundColor Cyan
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host "PowerShell: $($PSVersionTable.PSVersion)" -ForegroundColor Gray
    Write-Host ''
}

# Test 1: PowerShell Write-Host Chinese
try {
    $null = Write-Host '测试中文：你好世界' 6>&1
    Write-Result -Name 'PowerShell Write-Host Chinese' -Passed $true -Detail '输出中文文本成功'
} catch {
    Write-Result -Name 'PowerShell Write-Host Chinese' -Passed $false -Detail $_.Exception.Message
}

# Test 2: PowerShell Write-Host emoji
try {
    $emoji = [string]([char]0x2705) + [string]([char]0x274C) + [string]([char]0x26A0) + [string]([char]0xFE0F)
    $null = Write-Host $emoji 6>&1
    Write-Result -Name 'PowerShell Write-Host Emoji' -Passed $true -Detail '输出emoji成功'
} catch {
    Write-Result -Name 'PowerShell Write-Host Emoji' -Passed $false -Detail $_.Exception.Message
}

# Test 3: chcp code page check
try {
    $chcpOutput = chcp
    $chcpMatch = [regex]::Match($chcpOutput, ':\s*(\d+)')
    if ($chcpMatch.Success) {
        $currentCP = $chcpMatch.Groups[1].Value
    } else {
        $currentCP = 'unknown'
    }
    $cpPassed = $currentCP -eq '65001'
    Write-Result -Name 'chcp Code Page' -Passed $cpPassed -Detail "当前=$currentCP (期望=65001)"
} catch {
    Write-Result -Name 'chcp Code Page' -Passed $false -Detail $_.Exception.Message
}

# Test 4: Console OutputEncoding check
try {
    $oeWeb = [Console]::OutputEncoding.WebName
    $oeCP = [Console]::OutputEncoding.CodePage
    $oePassed = $oeCP -eq 65001
    Write-Result -Name 'Console OutputEncoding' -Passed $oePassed -Detail "$oeWeb (CodePage=$oeCP)"
} catch {
    Write-Result -Name 'Console OutputEncoding' -Passed $false -Detail $_.Exception.Message
}

# Test 5: $OutputEncoding check
try {
    $poeWeb = $OutputEncoding.WebName
    $poeCP = $OutputEncoding.CodePage
    $poePassed = ($poeCP -eq 65001) -or ($poeWeb -match 'utf-?8')
    Write-Result -Name 'PowerShell $OutputEncoding' -Passed $poePassed -Detail "$poeWeb (CP=$poeCP)"
} catch {
    Write-Result -Name 'PowerShell $OutputEncoding' -Passed $false -Detail $_.Exception.Message
}

# Test 6: Python stdout encoding
$pyAvail = $null -ne (Get-Command python -ErrorAction SilentlyContinue)
if (-not $pyAvail) {
    Write-Result -Name 'Python stdout Encoding' -Passed $false -Detail 'Python not found'
} else {
    try {
        $pyEnc = (python -c "import sys; print(sys.stdout.encoding or 'none')" 2>&1).Trim()
        $pyEncPassed = $pyEnc -match 'utf-?8'
        Write-Result -Name 'Python stdout Encoding' -Passed $pyEncPassed -Detail $pyEnc
    } catch {
        Write-Result -Name 'Python stdout Encoding' -Passed $false -Detail $_.Exception.Message
    }
}

# Test 7: Python print Chinese
if (-not $pyAvail) {
    Write-Result -Name 'Python Print Chinese' -Passed $false -Detail 'Python not found'
} else {
    try {
        $pyChOut = python -c "print('中文输出测试')" 2>&1 | Out-String
        $pyChErr = ($pyChOut | Select-String -Pattern 'UnicodeEncodeError|Traceback' -Quiet)
        $pyChPassed = (-not $pyChErr) -and ($pyChOut -match '中文输出测试')
        Write-Result -Name 'Python Print Chinese' -Passed $pyChPassed -Detail $(if ($pyChPassed) { 'print("中文输出测试")无异常' } else { $pyChOut.Trim() })
    } catch {
        Write-Result -Name 'Python Print Chinese' -Passed $false -Detail $_.Exception.Message
    }
}

# Test 8: Python print emoji
if (-not $pyAvail) {
    Write-Result -Name 'Python Print Emoji' -Passed $false -Detail 'Python not found'
} else {
    try {
        $pyEmojiStr = [string]([char]0x2705) + 'emoji测试'
        $pyEmojiCmd = "print('$pyEmojiStr')"
        $pyEmOut = python -c $pyEmojiCmd 2>&1 | Out-String
        $pyEmErr = ($pyEmOut | Select-String -Pattern 'UnicodeEncodeError|Traceback' -Quiet)
        $pyEmPassed = (-not $pyEmErr) -and ($pyEmOut -match 'emoji')
        Write-Result -Name 'Python Print Emoji' -Passed $pyEmPassed -Detail $(if ($pyEmPassed) { 'print emoji无UnicodeEncodeError' } else { $pyEmOut.Trim() })
    } catch {
        Write-Result -Name 'Python Print Emoji' -Passed $false -Detail $_.Exception.Message
    }
}

# Test 9: Python pipe output
if (-not $pyAvail) {
    Write-Result -Name 'Python Pipe Output' -Passed $false -Detail 'Python not found'
} else {
    try {
        $pipeOut = python -c "print('管道中文测试')" 2>&1 | Out-String
        $pipePassed = $pipeOut -match '管道中文测试'
        Write-Result -Name 'Python Pipe Output' -Passed $pipePassed -Detail $(if ($pipePassed) { '管道捕获中文成功' } else { '未检测到中文内容' })
    } catch {
        Write-Result -Name 'Python Pipe Output' -Passed $false -Detail $_.Exception.Message
    }
}

# Test 10: Get-Content read Chinese Markdown
try {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $agentsDir = Split-Path -Parent $scriptDir
    $rootDir = Split-Path -Parent $agentsDir
    $testFile = Join-Path $rootDir 'AGENTS.md'
    if (-not (Test-Path $testFile)) {
        $testFile = Join-Path $rootDir 'README.md'
    }
    if (Test-Path $testFile) {
        $firstLine = Get-Content -Path $testFile -Encoding UTF8 -TotalCount 1 -ErrorAction Stop
        $hasGarbled = $firstLine -match [char]0xFFFD
        $gcPassed = (-not $hasGarbled) -and ($firstLine.Length -gt 0)
        $fileName = Split-Path $testFile -Leaf
        Write-Result -Name 'Get-Content Read Chinese MD' -Passed $gcPassed -Detail $(if ($gcPassed) { "读取${fileName}首行正常" } else { '检测到乱码' })
    } else {
        Write-Result -Name 'Get-Content Read Chinese MD' -Passed $false -Detail '未找到AGENTS.md或README.md'
    }
} catch {
    Write-Result -Name 'Get-Content Read Chinese MD' -Passed $false -Detail $_.Exception.Message
}

# Test 11: git log Chinese commit
$gitAvail = $null -ne (Get-Command git -ErrorAction SilentlyContinue)
if (-not $gitAvail) {
    Write-Result -Name 'Git Log Chinese' -Passed $false -Detail 'Git not found'
} else {
    try {
        $scriptDir2 = Split-Path -Parent $MyInvocation.MyCommand.Path
        $agentsDir2 = Split-Path -Parent $scriptDir2
        $rootDir2 = Split-Path -Parent $agentsDir2
        Push-Location $rootDir2
        $gitLog = git log -1 --oneline 2>&1 | Out-String
        Pop-Location
        $gitErr = ($gitLog | Select-String -Pattern 'fatal|not a git repository' -Quiet)
        if ($gitErr) {
            Write-Result -Name 'Git Log Chinese' -Passed $false -Detail '不是git仓库或git命令失败'
        } else {
            $hasGarbledGit = $gitLog -match [char]0xFFFD
            if ($hasGarbledGit) {
                Write-Result -Name 'Git Log Chinese' -Passed $false -Detail 'git log输出存在乱码'
            } else {
                Write-Result -Name 'Git Log Chinese' -Passed $true -Detail 'git log输出无乱码'
            }
        }
    } catch {
        Pop-Location -ErrorAction SilentlyContinue
        Write-Result -Name 'Git Log Chinese' -Passed $false -Detail $_.Exception.Message
    }
}

# Test 12: cmd echo Chinese
try {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = 'cmd.exe'
    $psi.Arguments = '/c echo 中文CMD测试'
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
    $psi.StandardErrorEncoding = [System.Text.Encoding]::UTF8
    $proc = [System.Diagnostics.Process]::Start($psi)
    $cmdStdout = $proc.StandardOutput.ReadToEnd()
    $cmdStderr = $proc.StandardError.ReadToEnd()
    $proc.WaitForExit()
    $cmdPassed = ($cmdStdout -match '中文CMD测试') -and (-not ($cmdStderr -match 'Error'))
    Write-Result -Name 'cmd echo Chinese' -Passed $cmdPassed -Detail $(if ($cmdPassed) { 'cmd /c echo中文正常' } else { '输出异常或乱码' })
} catch {
    Write-Result -Name 'cmd echo Chinese' -Passed $false -Detail $_.Exception.Message
}

# Test 13: Project script Chinese output
try {
    $scriptDir3 = Split-Path -Parent $MyInvocation.MyCommand.Path
    $checkLinks = Join-Path $scriptDir3 'check-links.py'
    if (Test-Path $checkLinks) {
        $projOut = python $checkLinks --help 2>&1 | Out-String
        $projErr = ($projOut | Select-String -Pattern 'Error|Traceback|UnicodeEncodeError' -Quiet)
        $projPassed = (-not $projErr)
        $hasChinese = $projOut -match '[\u4e00-\u9fff]'
        Write-Result -Name 'Project Script Chinese' -Passed $projPassed -Detail $(if ($projPassed) { if ($hasChinese) { 'check-links.py --help中文输出正常' } else { '脚本运行正常（帮助信息无中文）' } } else { '脚本执行错误' })
    } else {
        Write-Result -Name 'Project Script Chinese' -Passed $false -Detail '未找到check-links.py'
    }
} catch {
    Write-Result -Name 'Project Script Chinese' -Passed $false -Detail $_.Exception.Message
}

# Test 14: Environment variables check (advisory, non-blocking)
try {
    $pyioVal = if ($env:PYTHONIOENCODING) { $env:PYTHONIOENCODING } else { '(not set)' }
    $pyutf8Val = if ($env:PYTHONUTF8) { $env:PYTHONUTF8 } else { '(not set)' }
    $pyioOk = $env:PYTHONIOENCODING -match 'utf-?8'
    $pyutf8Ok = $env:PYTHONUTF8 -eq '1'
    $envParts = @()
    $envParts += "PYTHONIOENCODING=$pyioVal"
    $envParts += "PYTHONUTF8=$pyutf8Val"
    $envDetail = $envParts -join ', '
    if (-not $pyioOk) { $envDetail += ' (建议设置PYTHONIOENCODING=utf-8)' }
    if (-not $pyutf8Ok) { $envDetail += ' (建议设置PYTHONUTF8=1)' }
    Write-Result -Name 'Environment Variables' -Passed $true -Detail $envDetail
} catch {
    Write-Result -Name 'Environment Variables' -Passed $true -Detail '检查完成'
}

# Summary
$total = $script:passCount + $script:failCount

if ($Json) {
    $out = [PSCustomObject]@{
        summary = [PSCustomObject]@{
            total      = $total
            passed     = $script:passCount
            failed     = $script:failCount
            all_passed = ($script:failCount -eq 0)
        }
        tests = $script:results
    }
    $out | ConvertTo-Json -Depth 5
} elseif (-not $Quiet) {
    Write-Host ''
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host '  Summary' -ForegroundColor Cyan
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host '  Passed: ' -NoNewline -ForegroundColor White
    Write-Host $script:passCount -ForegroundColor Green
    Write-Host '  Failed: ' -NoNewline -ForegroundColor White
    Write-Host $script:failCount -ForegroundColor Red
    Write-Host '  Total:  ' -NoNewline -ForegroundColor White
    Write-Host $total -ForegroundColor White
    Write-Host ''
    if ($script:failCount -eq 0) {
        Write-Host '  All tests PASSED!' -ForegroundColor Green
    } else {
        Write-Host '  Some tests FAILED.' -ForegroundColor Red
        foreach ($r in ($script:results | Where-Object { -not $_.passed })) {
            Write-Host "    - $($r.name): $($r.detail)" -ForegroundColor Yellow
        }
    }
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host ''
} else {
    Write-Host "$script:passCount/$total passed, $script:failCount failed"
    if ($script:failCount -gt 0) {
        foreach ($r in ($script:results | Where-Object { -not $_.passed })) {
            Write-Host "  FAIL: $($r.name)" -ForegroundColor Red
        }
    }
}

try {
    [Console]::InputEncoding = $origInputEnc
    [Console]::OutputEncoding = $origOutputEnc
    $OutputEncoding = $origPSOutputEnc
    $env:PYTHONIOENCODING = $origPYIO
    $env:PYTHONUTF8 = $origPYUTF8
} catch {}

if ($script:failCount -gt 0) {
    exit 1
}
exit 0
