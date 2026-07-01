# Encoding diagnostic script for Windows PowerShell
# Usage: .\check-encoding.ps1 [-Json]

param(
    [switch]$Json
)

$ErrorActionPreference = 'Continue'

# Save original encoding state BEFORE modifying anything
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

# Set UTF-8 for script's own output (diagnostics should render correctly)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSDefaultParameterValues['*:Encoding'] = 'utf8'
}

$script:results = @()
$script:passCount = 0
$script:warnCount = 0
$script:errorCount = 0

function Test-IsUtf8 {
    param([string]$EncodingName)
    if (-not $EncodingName) { return $false }
    $n = $EncodingName.ToLower().Replace('-', '').Replace('_', '')
    return $n -in @('utf8', 'utf8sig', 'cp65001', 'utf8nobom')
}

function Add-Result {
    param(
        [string]$Name,
        [string]$Value,
        [string]$Status,
        [string]$Message,
        [string[]]$Fixes = @()
    )
    $script:results += [PSCustomObject]@{
        name    = $Name
        value   = $Value
        status  = $Status
        message = $Message
        fixes   = $Fixes
    }
    switch ($Status) {
        'pass'  { $script:passCount++ }
        'warn'  { $script:warnCount++ }
        'error' { $script:errorCount++ }
    }
}

function Show-Item {
    param(
        [string]$Name,
        [string]$Value,
        [string]$Status,
        [string]$Message,
        [string[]]$Fixes = @()
    )
    $sym = switch ($Status) {
        'pass'  { '[PASS]' }
        'warn'  { '[WARN]' }
        'error' { '[FAIL]' }
        default { '[----]' }
    }
    $col = switch ($Status) {
        'pass'  { 'Green' }
        'warn'  { 'Yellow' }
        'error' { 'Red' }
        default { 'Gray' }
    }
    Write-Host "  $sym " -NoNewline -ForegroundColor $col
    Write-Host $Name -NoNewline -ForegroundColor White
    if ($Value) {
        Write-Host " = $Value" -ForegroundColor Gray
    } else {
        Write-Host ''
    }
    if ($Message) {
        Write-Host "         $Message" -ForegroundColor $col
    }
    foreach ($f in $Fixes) {
        Write-Host "   FIX>  $f" -ForegroundColor Cyan
    }
}

if (-not $Json) {
    Write-Host ''
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host '  Encoding Health Diagnostic' -ForegroundColor Cyan
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host "PowerShell: $($PSVersionTable.PSVersion)" -ForegroundColor Gray
    Write-Host ''
}

# ── 1. Active Code Page (chcp) ──
if (-not $Json) { Write-Host '[Console Code Page]' -ForegroundColor White }
if ($origCodePage -eq '65001') {
    Add-Result -Name 'Active Code Page (chcp)' -Value $origCodePage -Status 'pass' -Message 'UTF-8 CP65001 active'
} elseif ($origCodePage -eq '936') {
    Add-Result -Name 'Active Code Page (chcp)' -Value $origCodePage -Status 'error' -Message 'GBK CP936 - Chinese characters may corrupt in pipes' -Fixes @(
        'chcp 65001',
        '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8'
    )
} else {
    Add-Result -Name 'Active Code Page (chcp)' -Value $origCodePage -Status 'warn' -Message 'Non-UTF-8 code page' -Fixes @('chcp 65001')
}
if (-not $Json) {
    $r = $script:results[-1]
    Show-Item -Name $r.name -Value $r.value -Status $r.status -Message $r.message -Fixes $r.fixes
}

# ── 2-4. Console Encodings ──
if (-not $Json) { Write-Host ''; Write-Host '[Console Encoding]' -ForegroundColor White }

$ieWeb = $origInputEnc.WebName
$ieCP = $origInputEnc.CodePage
$ieDisp = "$ieWeb ($ieCP)"
if (Test-IsUtf8 $ieWeb) {
    Add-Result -Name '[Console]::InputEncoding' -Value $ieDisp -Status 'pass' -Message 'UTF-8 input encoding'
} else {
    Add-Result -Name '[Console]::InputEncoding' -Value $ieDisp -Status 'error' -Message 'Non-UTF-8 input encoding' -Fixes @(
        '[Console]::InputEncoding = [System.Text.Encoding]::UTF8'
    )
}
if (-not $Json) {
    $r = $script:results[-1]
    Show-Item -Name $r.name -Value $r.value -Status $r.status -Message $r.message -Fixes $r.fixes
}

$oeWeb = $origOutputEnc.WebName
$oeCP = $origOutputEnc.CodePage
$oeDisp = "$oeWeb ($oeCP)"
if (Test-IsUtf8 $oeWeb) {
    Add-Result -Name '[Console]::OutputEncoding' -Value $oeDisp -Status 'pass' -Message 'UTF-8 output encoding'
} else {
    Add-Result -Name '[Console]::OutputEncoding' -Value $oeDisp -Status 'error' -Message 'Non-UTF-8 output - Chinese may corrupt' -Fixes @(
        '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8'
    )
}
if (-not $Json) {
    $r = $script:results[-1]
    Show-Item -Name $r.name -Value $r.value -Status $r.status -Message $r.message -Fixes $r.fixes
}

$poeWeb = $origPSOutputEnc.WebName
if (Test-IsUtf8 $poeWeb) {
    Add-Result -Name '$OutputEncoding' -Value $poeWeb -Status 'pass' -Message 'PowerShell OutputEncoding is UTF-8'
} else {
    Add-Result -Name '$OutputEncoding' -Value $poeWeb -Status 'warn' -Message 'PowerShell OutputEncoding not UTF-8, affects pipes' -Fixes @(
        '$OutputEncoding = [System.Text.Encoding]::UTF8'
    )
}
if (-not $Json) {
    $r = $script:results[-1]
    Show-Item -Name $r.name -Value $r.value -Status $r.status -Message $r.message -Fixes $r.fixes
}

# ── 5. PowerShell version default encoding ──
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $de = $PSDefaultParameterValues['*:Encoding']
    if ($de -and (Test-IsUtf8 $de)) {
        Add-Result -Name 'PS7+ Default Encoding' -Value $de -Status 'pass' -Message 'Default cmdlet encoding is UTF-8'
    } else {
        $deVal = 'not set'
        if ($de) { $deVal = $de }
        Add-Result -Name 'PS7+ Default Encoding' -Value $deVal -Status 'warn' -Message 'Recommend setting default encoding to utf8' -Fixes @(
            '$PSDefaultParameterValues[''*:Encoding''] = ''utf8'''
        )
    }
} else {
    Add-Result -Name 'PS5.x Encoding' -Value 'PowerShell 5.x' -Status 'warn' -Message 'PS 5.x has poor UTF-8 defaults; always use -Encoding utf8' -Fixes @(
        'Upgrade to PowerShell 7+ for better UTF-8 defaults'
    )
}
if (-not $Json) {
    $r = $script:results[-1]
    Show-Item -Name $r.name -Value $r.value -Status $r.status -Message $r.message -Fixes $r.fixes
}

# ── 6. Python stdout encoding ──
if (-not $Json) { Write-Host ''; Write-Host '[Python Environment]' -ForegroundColor White }
$pyAvail = $false
$pyEnc = $null
try {
    $pyCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pyCmd) {
        $pyAvail = $true
        # Temporarily restore original env to get REAL baseline encoding
        $env:PYTHONIOENCODING = $origPYIO
        $env:PYTHONUTF8 = $origPYUTF8
        $pyEnc = (python -c 'import sys; print(sys.stdout.encoding or "none")' 2>$null).Trim()
    }
} catch {
    $pyEnc = 'error'
}
# Restore UTF-8 for our output
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'

if (-not $pyAvail) {
    Add-Result -Name 'Python' -Value 'not found' -Status 'warn' -Message 'Python not found in PATH, skipping Python checks'
} elseif (Test-IsUtf8 $pyEnc) {
    Add-Result -Name 'Python stdout encoding' -Value $pyEnc -Status 'pass' -Message 'Python stdout is UTF-8'
} else {
    Add-Result -Name 'Python stdout encoding' -Value $pyEnc -Status 'error' -Message 'Python stdout not UTF-8 - Chinese may corrupt' -Fixes @(
        '$env:PYTHONUTF8=1',
        'python -X utf8 script.py',
        '[Environment]::SetEnvironmentVariable(''PYTHONUTF8'',''1'',''User'')'
    )
}
if (-not $Json) {
    $r = $script:results[-1]
    Show-Item -Name $r.name -Value $r.value -Status $r.status -Message $r.message -Fixes $r.fixes
}

# ── 7. PYTHONIOENCODING ──
if (-not $origPYIO) {
    Add-Result -Name 'PYTHONIOENCODING' -Value '(not set)' -Status 'warn' -Message 'PYTHONIOENCODING not set' -Fixes @(
        '$env:PYTHONIOENCODING=''utf-8''',
        '[Environment]::SetEnvironmentVariable(''PYTHONIOENCODING'',''utf-8'',''User'')'
    )
} elseif (Test-IsUtf8 $origPYIO) {
    Add-Result -Name 'PYTHONIOENCODING' -Value $origPYIO -Status 'pass' -Message 'PYTHONIOENCODING is UTF-8'
} else {
    Add-Result -Name 'PYTHONIOENCODING' -Value $origPYIO -Status 'error' -Message 'PYTHONIOENCODING is not UTF-8' -Fixes @(
        '$env:PYTHONIOENCODING=''utf-8'''
    )
}
if (-not $Json) {
    $r = $script:results[-1]
    Show-Item -Name $r.name -Value $r.value -Status $r.status -Message $r.message -Fixes $r.fixes
}

# ── 8. PYTHONUTF8 ──
if ($origPYUTF8 -eq '1') {
    Add-Result -Name 'PYTHONUTF8' -Value $origPYUTF8 -Status 'pass' -Message 'Python UTF-8 mode enabled'
} else {
    $pyUtf8Val = '(not set)'
    if ($origPYUTF8) { $pyUtf8Val = $origPYUTF8 }
    Add-Result -Name 'PYTHONUTF8' -Value $pyUtf8Val -Status 'warn' -Message 'PYTHONUTF8 not set to 1' -Fixes @(
        '$env:PYTHONUTF8=1',
        '[Environment]::SetEnvironmentVariable(''PYTHONUTF8'',''1'',''User'')'
    )
}
if (-not $Json) {
    $r = $script:results[-1]
    Show-Item -Name $r.name -Value $r.value -Status $r.status -Message $r.message -Fixes $r.fixes
}

# ── 9. Git encoding config ──
if (-not $Json) { Write-Host ''; Write-Host '[Git Configuration]' -ForegroundColor White }
$gitAvail = $false
try {
    $gCmd = Get-Command git -ErrorAction SilentlyContinue
    if ($gCmd) { $gitAvail = $true }
} catch {}

if (-not $gitAvail) {
    Add-Result -Name 'Git' -Value 'not found' -Status 'warn' -Message 'Git not found in PATH, skipping Git checks'
    if (-not $Json) {
        $r = $script:results[-1]
        Show-Item -Name $r.name -Value $r.value -Status $r.status -Message $r.message -Fixes $r.fixes
    }
} else {
    $gCommitEnc = git config --get i18n.commitencoding 2>$null
    $gLogEnc = git config --get i18n.logoutputencoding 2>$null
    $gQuotePath = git config --get core.quotepath 2>$null

    # i18n.commitencoding
    if (-not $gCommitEnc -or (Test-IsUtf8 $gCommitEnc)) {
        $cv = '(default: utf-8)'
        if ($gCommitEnc) { $cv = $gCommitEnc }
        Add-Result -Name 'git i18n.commitencoding' -Value $cv -Status 'pass' -Message 'Git commit encoding is UTF-8'
    } else {
        Add-Result -Name 'git i18n.commitencoding' -Value $gCommitEnc -Status 'error' -Message 'Git commit encoding not UTF-8' -Fixes @(
            'git config --global i18n.commitencoding utf-8'
        )
    }
    if (-not $Json) {
        $r = $script:results[-1]
        Show-Item -Name $r.name -Value $r.value -Status $r.status -Message $r.message -Fixes $r.fixes
    }

    # i18n.logoutputencoding
    if ((Test-IsUtf8 $gLogEnc) -or -not $gLogEnc) {
        $lv = '(not set)'
        if ($gLogEnc) { $lv = $gLogEnc }
        if ($gLogEnc) {
            Add-Result -Name 'git i18n.logoutputencoding' -Value $lv -Status 'pass' -Message 'Git log encoding is UTF-8'
        } else {
            Add-Result -Name 'git i18n.logoutputencoding' -Value $lv -Status 'warn' -Message 'Recommend setting for non-ASCII log output' -Fixes @(
                'git config --global i18n.logoutputencoding utf-8'
            )
        }
    } else {
        Add-Result -Name 'git i18n.logoutputencoding' -Value $gLogEnc -Status 'error' -Message 'Git log encoding not UTF-8' -Fixes @(
            'git config --global i18n.logoutputencoding utf-8'
        )
    }
    if (-not $Json) {
        $r = $script:results[-1]
        Show-Item -Name $r.name -Value $r.value -Status $r.status -Message $r.message -Fixes $r.fixes
    }

    # core.quotepath
    if ($gQuotePath -eq 'false') {
        Add-Result -Name 'git core.quotepath' -Value 'false' -Status 'pass' -Message 'Non-ASCII filenames display correctly'
    } else {
        $qv = '(default: true)'
        if ($gQuotePath) { $qv = $gQuotePath }
        Add-Result -Name 'git core.quotepath' -Value $qv -Status 'warn' -Message 'Escapes non-ASCII filenames in output' -Fixes @(
            'git config --global core.quotepath false'
        )
    }
    if (-not $Json) {
        $r = $script:results[-1]
        Show-Item -Name $r.name -Value $r.value -Status $r.status -Message $r.message -Fixes $r.fixes
    }
}

# ── Summary ──
$total = $script:passCount + $script:warnCount + $script:errorCount
if ($total -gt 0) {
    $score = [math]::Round(($script:passCount / $total) * 100)
} else {
    $score = 100
}

if ($Json) {
    $out = [PSCustomObject]@{
        summary = [PSCustomObject]@{
            total_checks = $total
            pass         = $script:passCount
            warnings     = $script:warnCount
            errors       = $script:errorCount
            health_score = $score
        }
        checks  = $script:results
    }
    $out | ConvertTo-Json -Depth 5
} else {
    Write-Host ''
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host '  Summary' -ForegroundColor Cyan
    Write-Host '========================================' -ForegroundColor Cyan
    $hc = if ($score -ge 90) { 'Green' } elseif ($score -ge 70) { 'Yellow' } else { 'Red' }
    Write-Host '  Health Score: ' -NoNewline -ForegroundColor White
    Write-Host "$score%" -ForegroundColor $hc
    Write-Host "  Pass:     $script:passCount" -ForegroundColor Green
    Write-Host "  Warnings: $script:warnCount" -ForegroundColor Yellow
    Write-Host "  Errors:   $script:errorCount" -ForegroundColor Red
    if ($script:errorCount -eq 0 -and $script:warnCount -eq 0) {
        Write-Host ''
        Write-Host '  All encoding settings are optimal!' -ForegroundColor Green
    } elseif ($script:errorCount -eq 0) {
        Write-Host ''
        Write-Host '  No critical issues, but some settings can be improved.' -ForegroundColor Yellow
    } else {
        Write-Host ''
        Write-Host '  Critical encoding issues detected! Run FIX> commands above.' -ForegroundColor Red
    }
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host ''
}

if ($script:errorCount -gt 0) {
    exit 1
}
exit 0
