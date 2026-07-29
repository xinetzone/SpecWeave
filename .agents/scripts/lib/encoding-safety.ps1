#Requires -Version 5.1
# ==============================================================================
# SpecWeave PowerShell Encoding Safety Library
# ==============================================================================
# UTF-8 No BOM safe write functions for PS5.1/7.x, following Write-First principle.
# Avoids PS5.1 default encoding pitfalls (GBK/UTF-16LE/UTF8-BOM).
#
# 依赖：dot-source 共享版本校验库 pwsh7-version-check.ps1（同目录）
# 使用方法：. "$PSScriptRoot/../lib/encoding-safety.ps1"
# ==============================================================================

# 引入共享版本校验库（幂等安全，多次 dot-source 不会重复定义）
. "$PSScriptRoot/pwsh7-version-check.ps1"

# 直接运行时执行版本校验（dot-source 时由调用方负责）
if ($MyInvocation.InvocationName -ne '.') {
    if (-not (Test-Pwsh7Version)) {
        Show-Pwsh7VersionError
    }
}

if (-not (Get-Variable -Name 'Utf8NoBomSingleton' -Scope Script -ErrorAction SilentlyContinue)) {
    $script:Utf8NoBomSingleton = [System.Text.UTF8Encoding]::new($false)
}

# ==============================================================================
# 编码安全初始化
# ==============================================================================
function Initialize-EncodingSafety {
    [CmdletBinding()]
    param()

    # 编码状态诊断日志（仅在 Verbose 模式下输出，方便排查编码问题）
    if ($VerbosePreference -ne 'SilentlyContinue' -or $env:SPECWEAVE_ENCODING_DEBUG) {
        $cpBefore = 0
        try { $cpBefore = [Console]::OutputEncoding.CodePage } catch {}
        Write-Host "[EncodingSafety] Before init:" -ForegroundColor DarkGray
        Write-Host "  Console.OutputEncoding = $([Console]::OutputEncoding.WebName) (CP $cpBefore)" -ForegroundColor DarkGray
        Write-Host "  Console.InputEncoding  = $([Console]::InputEncoding.WebName)" -ForegroundColor DarkGray
        Write-Host "  OutputEncoding         = $($global:OutputEncoding.WebName)" -ForegroundColor DarkGray
        Write-Host "  PYTHONIOENCODING       = $env:PYTHONIOENCODING" -ForegroundColor DarkGray
        Write-Host "  PSDefault Encoding     = $($PSDefaultParameterValues['*:Encoding'])" -ForegroundColor DarkGray
    }

    try { chcp 65001 > $null 2>&1 } catch {}
    [Console]::OutputEncoding = $script:Utf8NoBomSingleton
    [Console]::InputEncoding  = $script:Utf8NoBomSingleton
    $global:OutputEncoding    = $script:Utf8NoBomSingleton
    $env:PYTHONIOENCODING = 'utf-8'
    $env:PYTHONUTF8       = '1'
    if ($PSVersionTable.PSVersion.Major -ge 7) {
        $PSDefaultParameterValues['*:Encoding'] = 'utf8'
    }

    if ($VerbosePreference -ne 'SilentlyContinue' -or $env:SPECWEAVE_ENCODING_DEBUG) {
        $cpAfter = 0
        try { $cpAfter = [Console]::OutputEncoding.CodePage } catch {}
        Write-Host "[EncodingSafety] After init:" -ForegroundColor DarkGray
        Write-Host "  Console.OutputEncoding = $([Console]::OutputEncoding.WebName) (CP $cpAfter)" -ForegroundColor DarkGray
        Write-Host "  Console.InputEncoding  = $([Console]::InputEncoding.WebName)" -ForegroundColor DarkGray
        Write-Host "  OutputEncoding         = $($global:OutputEncoding.WebName)" -ForegroundColor DarkGray
        Write-Host "  PYTHONIOENCODING       = $env:PYTHONIOENCODING" -ForegroundColor DarkGray
        Write-Host "  PSDefault Encoding     = $($PSDefaultParameterValues['*:Encoding'])" -ForegroundColor DarkGray
    }
}

function Write-Utf8File {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, Position=0)][string]$Path,
        [Parameter(Mandatory=$true, Position=1, ValueFromPipeline=$true)][AllowEmptyString()][string]$Content,
        [switch]$Append,
        [switch]$NoNewline,
        [bool]$CreateDirectory = $true
    )
    begin { $sb = [System.Text.StringBuilder]::new() }
    process { if ($Content) { [void]$sb.Append($Content) } }
    end {
        $text = $sb.ToString()
        if (-not $NoNewline -and $text.Length -gt 0 -and -not $text.EndsWith("`n")) {
            $text += [Environment]::NewLine
        }
        $parent = Split-Path -Parent $Path
        if ($CreateDirectory -and $parent -and -not (Test-Path -LiteralPath $parent)) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
        if ($Append -and (Test-Path -LiteralPath $Path)) {
            $existing = [System.IO.File]::ReadAllText($Path, $script:Utf8NoBomSingleton)
            $text = $existing + $text
        }
        [System.IO.File]::WriteAllText($Path, $text, $script:Utf8NoBomSingleton)
    }
}

function Read-Utf8File {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, Position=0)][string]$Path,
        [switch]$Raw
    )
    if (-not (Test-Path -LiteralPath $Path)) { throw "File not found: $Path" }
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $hasBom = $bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF
    if ($hasBom) { $bytes = $bytes[3..($bytes.Length-1)] }
    $text = $script:Utf8NoBomSingleton.GetString($bytes)
    if ($Raw) { return $text }
    return $text -split '\r?\n'
}

function Test-Utf8File {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, Position=0)][string]$Path
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        return [PSCustomObject]@{ Path=$Path; Exists=$false; HasBom=$false; IsUtf8=$false; IsUtf8NoBom=$false; Encoding='not-found'; HasGarbled=$false }
    }
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $hasBom = $bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF
    $testBytes = if ($hasBom) { $bytes[3..($bytes.Length-1)] } else { $bytes }
    $isUtf8 = $true; $hasGarbled = $false
    try {
        $decoded = $script:Utf8NoBomSingleton.GetString($testBytes)
        $hasGarbled = $decoded -match [char]0xFFFD
    } catch { $isUtf8 = $false; $hasGarbled = $true }
    $enc = if ($hasBom) { 'utf-8-bom' } elseif ($isUtf8) { 'utf-8-nobom' } else { 'unknown' }
    return [PSCustomObject]@{ Path=$Path; Exists=$true; HasBom=$hasBom; IsUtf8=$isUtf8; IsUtf8NoBom=($isUtf8 -and -not $hasBom); Encoding=$enc; HasGarbled=$hasGarbled; ByteLength=$bytes.Length }
}

Initialize-EncodingSafety
