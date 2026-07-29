#Requires -Version 5.1
# ==============================================================================
# SpecWeave PowerShell Encoding Safety Library
# ==============================================================================
# UTF-8 No BOM safe write functions for PS5.1/7.x, following Write-First principle.
# Avoids PS5.1 default encoding pitfalls (GBK/UTF-16LE/UTF8-BOM).
#
# Version: 1.0.0
# 依赖：dot-source 共享版本校验库 pwsh7-version-check.ps1（同目录）
# 使用方法：. "$PSScriptRoot/../lib/encoding-safety.ps1"
# ==============================================================================

# 模块版本
$script:EncodingSafetyVersion = '1.0.0'

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
# PS1 语法分析调试日志系统
# ==============================================================================
# 环境变量 PS1_SYNTAX_DEBUG=1 启用详细调试日志（与Python端对应）

if (-not (Get-Variable -Name 'Ps1SyntaxDebugEnabled' -Scope Script -ErrorAction SilentlyContinue)) {
    $script:Ps1SyntaxDebugEnabled = ($null -ne $env:PS1_SYNTAX_DEBUG -and $env:PS1_SYNTAX_DEBUG -eq '1')
}

function Write-Ps1Trace {
    <#
    .SYNOPSIS
        输出 PS1 语法分析调试跟踪日志（仅在 PS1_SYNTAX_DEBUG=1 时生效）。
    #>
    [CmdletBinding()]
    param([Parameter(Mandatory=$true, Position=0)][string]$Message)
    if ($script:Ps1SyntaxDebugEnabled) {
        Write-Host "[PS1_SYNTAX] DEBUG  $Message" -ForegroundColor DarkGray
    }
}

function Write-Ps1TraceHs {
    <#
    .SYNOPSIS
        输出 here-string 专用事件日志（与Python端 _trace_hs 对齐）。
    .PARAMETER Pos
        当前位置。
    .PARAMETER Event
        事件类型（start/end/escape/eof_warn/skip/line_check）。
    .PARAMETER Quote
        引号类型（" 或 '）。
    .PARAMETER Context
        额外上下文信息（hashtable）。
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][int]$Pos,
        [Parameter(Mandatory=$true)][string]$Event,
        [char]$Quote = [char]0,
        [hashtable]$Context = @{}
    )
    if (-not $script:Ps1SyntaxDebugEnabled) { return }
    $q = if ($Quote -ne [char]0) { "quote=$Quote" } else { "" }
    $ctxParts = @()
    foreach ($k in $Context.Keys) {
        $ctxParts += "$k=$($Context[$k])"
    }
    $ctx = if ($ctxParts.Count -gt 0) { " " + ($ctxParts -join ' ') } else { "" }
    $eventUpper = $Event.ToUpper()
    Write-Host "[PS1_SYNTAX] DEBUG   [HS-$eventUpper] pos=$Pos $q$ctx" -ForegroundColor DarkGray
}

function Write-Ps1TraceNewline {
    <#
    .SYNOPSIS
        输出换行符检测日志（与Python端 _trace_newline 对齐）。
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][int]$Pos,
        [Parameter(Mandatory=$true)][string]$Type  # CRLF / LF / CR
    )
    if ($script:Ps1SyntaxDebugEnabled) {
        Write-Host "[PS1_SYNTAX] DEBUG   [NL]  pos=$Pos type=$Type" -ForegroundColor DarkGray
    }
}

function Write-Ps1TraceBom {
    <#
    .SYNOPSIS
        输出 BOM 检测结果（与Python端 _trace_bom 对齐）。
    #>
    [CmdletBinding()]
    param([Parameter(Mandatory=$true)][bool]$Detected)
    if (-not $script:Ps1SyntaxDebugEnabled) { return }
    if ($Detected) {
        Write-Host "[PS1_SYNTAX] DEBUG   [BOM] UTF-8 BOM detected at position 0, skipping" -ForegroundColor DarkGray
    } else {
        Write-Host "[PS1_SYNTAX] DEBUG   [BOM] No BOM detected" -ForegroundColor DarkGray
    }
}

function Write-Ps1TraceLineStart {
    <#
    .SYNOPSIS
        输出行首检测日志（与Python端 _trace_linestart 对齐）。
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][int]$Pos,
        [Parameter(Mandatory=$true)][string]$Reason
    )
    if ($script:Ps1SyntaxDebugEnabled) {
        Write-Host "[PS1_SYNTAX] DEBUG   [LINE] pos=$Pos at_line_start=True reason=$Reason" -ForegroundColor DarkGray
    }
}

function Set-Ps1SyntaxDebug {
    <#
    .SYNOPSIS
        编程方式启用/禁用 PS1 语法调试日志（与Python端 set_debug 对齐）。
    #>
    [CmdletBinding()]
    param([Parameter(Mandatory=$true)][bool]$Enabled)
    $script:Ps1SyntaxDebugEnabled = $Enabled
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

# ==============================================================================
# PowerShell 语法分析 — 括号深度感知（PS5.1 兼容）
# ==============================================================================
# 提供字符串/注释感知的代码遍历和括号深度追踪，用于安全地在脚本中插入代码
# 而不会错误地嵌套到函数体、if块等内部。
#
# 设计原则：
#   - PS5.1 兼容（不使用 ??、?:、??= 等 pwsh7+ 运算符）
#   - 正确处理：行注释(#)、注释块(<# #>, 支持嵌套)、单引号字符串('')、
#     双引号字符串("")、反引号转义(`)、双引号 here-string(@"..."@)、
#     单引号 here-string(@'...'@)
#   - 与 Python 端 lib/ps1_syntax.py 逻辑保持一致
# ==============================================================================
function Skip-Ps1HereString {
    <#
    .SYNOPSIS
        检测当前位置是否为 PowerShell here-string 开头，若是则跳过整个 here-string。
    .DESCRIPTION
        PowerShell here-string 语法：
        - 双引号 here-string: @" <换行> ... <换行开头>"@
          支持反引号 (`) 转义，变量会被展开
        - 单引号 here-string: @' <换行> ... <换行开头>'@
          完全字面量，不处理转义，不展开变量

        检测规则：
        1. 当前字符必须是 '@'
        2. 下一个字符必须是 '"' 或 '''
        3. @<quote> 之后必须紧跟换行符（可带可选 CR）
        4. 结束标记 <quote>@ 必须在行首位置

        若当前位置不是 here-string 开头，直接返回原位置（不做任何修改）。
    .PARAMETER Content
        要分析的 PowerShell 代码字符串。
    .PARAMETER Position
        当前扫描位置（0-based）。调用方需确保 Position 在有效范围内。
    .OUTPUTS
        [int] 若当前位置是 here-string 开头，返回 here-string 结束标记之后的位置；
              否则返回原 Position（表示未跳过任何内容）。
    .EXAMPLE
        # 在逐字符遍历时安全跳过 here-string
        $i = Skip-Ps1HereString -Content $code -Position $i
        if ($i -ne $originalI) { continue }  # 跳过了 here-string
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, Position=0)][AllowEmptyString()][string]$Content,
        [Parameter(Mandatory=$true, Position=1)][int]$Position
    )
    $n = $Content.Length
    $i = $Position

    # 空字符串直接返回原位置
    if ($n -eq 0) { return $Position }

    # 检测 @' 或 @" 后跟换行符
    if ($i -lt $n -and $Content[$i] -eq '@' -and ($i + 1) -lt $n -and ($Content[$i + 1] -eq '"' -or $Content[$i + 1] -eq "'")) {
        $quoteChar = $Content[$i + 1]
        $j = $i + 2

        # 按原始逻辑检测换行符（当前仅支持 LF 和 CRLF）
        $nlType = $null
        $afterCr = $false
        if ($j -lt $n -and $Content[$j] -eq "`r") {
            $j++
            $afterCr = $true
        }
        if ($j -lt $n -and $Content[$j] -eq "`n") {
            $nlType = if ($afterCr) { "CRLF" } else { "LF" }
        }

        if ($null -ne $nlType) {
            # here-string 开始
            Write-Ps1TraceHs -Pos $i -Event "start" -Quote $quoteChar -Context @{newline=$nlType; content_len=$n}
            Write-Ps1TraceNewline -Pos $j -Type $nlType

            $i = $j + 1  # 跳过换行符（j 指向 `n）
            $endMarker0 = $quoteChar
            $endMarker1 = '@'
            $escapeCount = 0
            $closed = $false

            while ($i -lt $n) {
                # 行首检测：当前位置是文件开头，或前一个字符是 `n
                $atLineStart = ($i -eq 0) -or ($Content[$i - 1] -eq "`n")
                if ($atLineStart) {
                    $reason = if ($i -eq 0) { "pos=0" } else { "prev_char=LF" }
                    Write-Ps1TraceLineStart -Pos $i -Reason $reason
                }
                if ($atLineStart -and ($i + 1) -lt $n -and $Content[$i] -eq $endMarker0 -and $Content[$i + 1] -eq $endMarker1) {
                    Write-Ps1TraceHs -Pos $i -Event "end" -Quote $quoteChar -Context @{end_pos=($i+2); escapes=$escapeCount}
                    $i += 2  # 跳过结束标记 <quote>@
                    $closed = $true
                    break
                }
                # 双引号 here-string 支持反引号转义（如 `"、`n、`$ 等）
                if ($quoteChar -eq '"' -and $Content[$i] -eq '`' -and ($i + 1) -lt $n) {
                    $escapeCount++
                    Write-Ps1TraceHs -Pos $i -Event "escape" -Quote $quoteChar -Context @{escaped_char="'$($Content[$i+1])'"}
                    $i += 2  # 跳过反引号及其转义的字符
                    continue
                }
                # 换行符遍历日志
                if ($Content[$i] -eq "`r" -and ($i + 1) -lt $n -and $Content[$i + 1] -eq "`n") {
                    Write-Ps1TraceNewline -Pos $i -Type "CRLF"
                } elseif ($Content[$i] -eq "`r") {
                    Write-Ps1TraceNewline -Pos $i -Type "CR"
                } elseif ($Content[$i] -eq "`n" -and ($i -eq 0 -or $Content[$i - 1] -ne "`r")) {
                    Write-Ps1TraceNewline -Pos $i -Type "LF"
                }
                $i++
            }
            # while 循环正常结束（未 break）= EOF 未闭合
            if (-not $closed) {
                Write-Ps1TraceHs -Pos $i -Event "eof_warn" -Quote $quoteChar -Context @{escapes=$escapeCount; msg="here-string not closed before EOF"}
            }
            return $i
        } else {
            # @<quote> 后无换行符，不是 here-string
            $nextChars = if ($j -lt $n) { $Content.Substring($j, [Math]::Min(5, $n - $j)) } else { "<EOF>" }
            Write-Ps1TraceHs -Pos $i -Event "skip" -Quote $quoteChar -Context @{reason="no_newline_after_open"; next_chars=$nextChars}
        }
    }

    # 不是 here-string 开头，返回原位置
    return $Position
}

function Find-NonWhitespace {
    <#
    .SYNOPSIS
        返回 start 之后第一个非空白字符的位置（与 Python 端 find_non_whitespace 对齐）。
    .DESCRIPTION
        空白字符包括：空格、制表符(\t)、回车符(\r)、换行符(\n)。
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, Position=0)][AllowEmptyString()][string]$Content,
        [Parameter(Position=1)][int]$Start = 0
    )
    $i = $Start
    $n = $Content.Length
    if ($n -eq 0) { return 0 }
    while ($i -lt $n -and ($Content[$i] -eq ' ' -or $Content[$i] -eq "`t" -or $Content[$i] -eq "`r" -or $Content[$i] -eq "`n")) {
        $i++
    }
    return $i
}

function Skip-Ps1LineComments {
    <#
    .SYNOPSIS
        跳过连续的行注释、空行和空白，返回下一个有意义代码的位置（与 Python 端 skip_line_comments 对齐）。
    .DESCRIPTION
        注意：不会跳过 #Requires 行（它是有意义的声明）。
        支持 here-string 感知，避免将 here-string 内的 # 误判为注释。
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, Position=0)][AllowEmptyString()][string]$Content,
        [Parameter(Mandatory=$true, Position=1)][int]$Start
    )
    $i = $Start
    $n = $Content.Length
    if ($n -eq 0) { return 0 }
    while ($i -lt $n) {
        $i = Find-NonWhitespace -Content $Content -Start $i
        if ($i -ge $n) { break }

        # ── Here-string 感知：如果当前位置是 here-string 开头，先跳过它 ──
        $prevI = $i
        $i = Skip-Ps1HereString -Content $Content -Position $i
        if ($i -ne $prevI) { continue }

        $ch = $Content[$i]
        # 空行（\r 已被 Find-NonWhitespace 跳过，这里只剩 \n）
        if ($ch -eq "`n") {
            $i++
            continue
        }
        # 行注释（但不是 #Requires、不是 <# 注释块开头）
        if ($ch -eq '#' -and (($i + 1) -ge $n -or $Content[$i + 1] -ne '<')) {
            $isRequires = $false
            if (($i + 8) -lt $n) {
                $hashTag = $Content.Substring($i, [Math]::Min(9, $n - $i))
                if ($hashTag -match '(?i)^#requires') { $isRequires = $true }
            }
            if ($isRequires) { break }
            while ($i -lt $n -and $Content[$i] -ne "`n") { $i++ }
            continue
        }
        # 注释块 <# ... #>（支持嵌套）
        if (($i + 1) -lt $n -and $ch -eq '<' -and $Content[$i + 1] -eq '#') {
            $depth = 1
            $i += 2
            while ($i -lt $n -and $depth -gt 0) {
                if (($i + 1) -lt $n -and $Content[$i] -eq '<' -and $Content[$i + 1] -eq '#') {
                    $depth++; $i += 2
                } elseif (($i + 1) -lt $n -and $Content[$i] -eq '#' -and $Content[$i + 1] -eq '>') {
                    $depth--; $i += 2
                } else { $i++ }
            }
            continue
        }
        break
    }
    return $i
}

function Get-Ps1CodeChars {
    <#
    .SYNOPSIS
        迭代字符串中的代码字符，跳过字符串和注释内容（括号深度感知基础原语）。
    .DESCRIPTION
        逐字符遍历 PowerShell 代码字符串，跳过注释和字符串字面量内容，
        仅返回代码部分的字符及其位置。用于正确追踪括号深度。
        正确处理：行注释、注释块（支持嵌套）、单/双引号字符串、反引号转义、
        以及双/单引号 here-string (@"..."@ / @'...'@)。
    .PARAMETER Content
        要分析的 PowerShell 代码字符串。
    .PARAMETER Start
        起始位置（0-based），默认为 0。
    .OUTPUTS
        依次返回 [PSCustomObject]@{ Index = int; Char = char }
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, Position=0)][AllowEmptyString()][string]$Content,
        [Parameter(Position=1)][int]$Start = 0
    )
    $i = $Start
    $n = $Content.Length
    if ($n -eq 0) { return }
    while ($i -lt $n) {
        $ch = $Content[$i]

        # ── Here-string @'...'@ 或 @"..."@ ──
        $prevI = $i
        $i = Skip-Ps1HereString -Content $Content -Position $i
        if ($i -ne $prevI) { continue }

        # ── 注释块 <#...#>（支持嵌套）──
        if ($ch -eq '<' -and ($i + 1) -lt $n -and $Content[$i + 1] -eq '#') {
            $depth = 1
            $i += 2
            while ($i -lt $n -and $depth -gt 0) {
                if (($i + 1) -lt $n -and $Content[$i] -eq '<' -and $Content[$i + 1] -eq '#') {
                    $depth++
                    $i += 2
                } elseif (($i + 1) -lt $n -and $Content[$i] -eq '#' -and $Content[$i + 1] -eq '>') {
                    $depth--
                    $i += 2
                } else {
                    $i++
                }
            }
            continue
        }

        # ── 行注释 #... ──
        if ($ch -eq '#') {
            while ($i -lt $n -and $Content[$i] -ne "`n") {
                $i++
            }
            continue
        }

        # ── 单引号字符串 '...'（含 '' 转义）──
        if ($ch -eq "'") {
            $i++
            while ($i -lt $n) {
                if ($Content[$i] -eq "'") {
                    if (($i + 1) -lt $n -and $Content[$i + 1] -eq "'") {
                        $i += 2
                        continue
                    }
                    $i++
                    break
                }
                $i++
            }
            continue
        }

        # ── 双引号字符串 "..."（含反引号 ` 转义）──
        if ($ch -eq '"') {
            $i++
            while ($i -lt $n) {
                if ($Content[$i] -eq '`' -and ($i + 1) -lt $n) {
                    $i += 2
                    continue
                }
                if ($Content[$i] -eq '"') {
                    $i++
                    break
                }
                $i++
            }
            continue
        }

        [PSCustomObject]@{ Index = $i; Char = $ch }
        $i++
    }
}

function Get-Ps1BraceDepth {
    <#
    .SYNOPSIS
        计算 PowerShell 代码在指定位置的括号深度（{ 未闭合数量）。
    .DESCRIPTION
        使用 Get-Ps1CodeChars 跳过字符串和注释后，统计 { 和 } 的深度。
        返回 0 表示在顶层（可以安全插入代码）。
    .PARAMETER Content
        要分析的 PowerShell 代码字符串。
    .PARAMETER EndPos
        结束位置（0-based，不包含），默认为字符串末尾。
    .OUTPUTS
        [int] 括号深度。0 = 顶层，>0 = 在某个代码块内部。
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, Position=0)][AllowEmptyString()][string]$Content,
        [Parameter(Position=1)][int]$EndPos = -1
    )
    if ([string]::IsNullOrEmpty($Content)) { return 0 }
    if ($EndPos -lt 0) { $EndPos = $Content.Length }
    $depth = 0
    foreach ($item in Get-Ps1CodeChars -Content $Content -Start 0) {
        if ($item.Index -ge $EndPos) { break }
        if ($item.Char -eq '{') { $depth++ }
        elseif ($item.Char -eq '}') { $depth-- }
    }
    return $depth
}

function Find-Ps1TopLevelInsertPoint {
    <#
    .SYNOPSIS
        找到 PowerShell 脚本中的顶层安全插入点（括号深度 = 0 的位置）。
    .DESCRIPTION
        从指定位置开始扫描，找到第一个可以安全插入代码的顶层位置。
        正确识别：
        - 脚本级 param()：返回 param 块结束后的位置
        - 第一个函数定义：返回函数定义开始前的行首位置
        - 其他顶层语句：返回语句起始的行首位置
        完整支持 CRLF 换行符和 here-string 感知。
    .PARAMETER Content
        要分析的 PowerShell 代码字符串。
    .PARAMETER SearchFrom
        起始搜索位置（0-based），默认为 0。
    .OUTPUTS
        [int] 安全插入点的索引位置。
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, Position=0)][AllowEmptyString()][string]$Content,
        [Parameter(Position=1)][int]$SearchFrom = 0
    )
    if ([string]::IsNullOrEmpty($Content)) { return 0 }
    $n = $Content.Length

    # 使用统一的辅助函数跳过空白和注释（含 CRLF 和 here-string 感知）
    $pos = Skip-Ps1LineComments -Content $Content -Start (Find-NonWhitespace -Content $Content -Start $SearchFrom)

    # 检查是否以脚本级 param( 开头（且在顶层，深度=0）
    if ($pos -lt $n) {
        $substr = $Content.Substring($pos)
        $paramMatch = [regex]::Match($substr, '(?i)^\s*param\s*\(')
        if ($paramMatch.Success) {
            $preDepth = Get-Ps1BraceDepth -Content $Content -EndPos $pos
            if ($preDepth -eq 0) {
                # 找到 param 块结束位置
                $parenPos = $Content.IndexOf('(', $pos)
                if ($parenPos -ge 0) {
                    $pDepth = 0
                    $pi = $parenPos
                    while ($pi -lt $n) {
                        $pch = $Content[$pi]
                        # ── Here-string @'...'@ 或 @"..."@ ──
                        $prevPi = $pi
                        $pi = Skip-Ps1HereString -Content $Content -Position $pi
                        if ($pi -ne $prevPi) { continue }
                        # 跳过注释块 <#...#>（支持嵌套）
                        if ($pch -eq '<' -and ($pi + 1) -lt $n -and $Content[$pi + 1] -eq '#') {
                            $cDepth = 1; $pi += 2
                            while ($pi -lt $n -and $cDepth -gt 0) {
                                if (($pi + 1) -lt $n -and $Content[$pi] -eq '<' -and $Content[$pi + 1] -eq '#') {
                                    $cDepth++; $pi += 2
                                } elseif (($pi + 1) -lt $n -and $Content[$pi] -eq '#' -and $Content[$pi + 1] -eq '>') {
                                    $cDepth--; $pi += 2
                                } else { $pi++ }
                            }
                            continue
                        }
                        # 跳过行注释 #...
                        if ($pch -eq '#') {
                            while ($pi -lt $n -and $Content[$pi] -ne "`n") { $pi++ }
                            continue
                        }
                        # 跳过单引号字符串
                        if ($pch -eq "'") {
                            $pi++
                            while ($pi -lt $n) {
                                if ($Content[$pi] -eq "'") {
                                    if (($pi + 1) -lt $n -and $Content[$pi + 1] -eq "'") { $pi += 2; continue }
                                    $pi++; break
                                }
                                $pi++
                            }
                            continue
                        }
                        # 跳过双引号字符串
                        if ($pch -eq '"') {
                            $pi++
                            while ($pi -lt $n) {
                                if ($Content[$pi] -eq '`' -and ($pi + 1) -lt $n) { $pi += 2; continue }
                                if ($Content[$pi] -eq '"') { $pi++; break }
                                $pi++
                            }
                            continue
                        }
                        if ($pch -eq '(') { $pDepth++ }
                        elseif ($pch -eq ')') {
                            $pDepth--
                            if ($pDepth -eq 0) {
                                # 跳过闭括号后空白和换行（含 CRLF 支持）
                                $nextChar = $pi + 1
                                while ($nextChar -lt $n -and ($Content[$nextChar] -eq ' ' -or $Content[$nextChar] -eq "`t" -or $Content[$nextChar] -eq "`r")) {
                                    $nextChar++
                                }
                                if ($nextChar -lt $n -and $Content[$nextChar] -eq "`n") {
                                    $nextChar++
                                    $nextChar = Find-NonWhitespace -Content $Content -Start $nextChar
                                }
                                return $nextChar
                            }
                        }
                        $pi++
                    }
                }
            }
        }
    }

    # 扫描找到第一个顶层代码位置（括号深度 = 0）
    $braceDepth = if ($pos -gt 0) { Get-Ps1BraceDepth -Content $Content -EndPos $pos } else { 0 }
    $i = $pos
    while ($i -lt $n) {
        # 行首位置
        $lineStart = $i
        # 跳过行首空白（仅空格和制表符，不跳过换行符——与 Python 端一致）
        while ($i -lt $n -and ($Content[$i] -eq ' ' -or $Content[$i] -eq "`t")) { $i++ }

        # 空行（\r 由后续 Skip-Ps1LineComments/Find-NonWhitespace 处理）
        if ($i -lt $n -and $Content[$i] -eq "`n") {
            $i++
            continue
        }

        # 跳过连续的行注释和空行（含 here-string 感知和 CRLF 支持）
        $oldI = $i
        $i = Skip-Ps1LineComments -Content $Content -Start $i
        if ($i -ge $n) { break }

        # 在顶层 → 返回行首位置（安全插入点）
        if ($braceDepth -eq 0) {
            return $lineStart
        }

        # 扫描到行尾，追踪括号深度（Get-Ps1CodeChars 已具备完整的 here-string/字符串/注释感知）
        $lineDone = $false
        foreach ($item in Get-Ps1CodeChars -Content $Content -Start $i) {
            if ($item.Char -eq '{') { $braceDepth++ }
            elseif ($item.Char -eq '}') { $braceDepth-- }
            if ($item.Char -eq "`n") {
                $i = $item.Index + 1
                $lineDone = $true
                break
            }
        }
        if (-not $lineDone) { $i = $n }
    }

    return $n
}

function Add-Ps1CodeAtTopLevel {
    <#
    .SYNOPSIS
        在 PowerShell 脚本的顶层安全位置插入代码块（括号深度感知）。
    .DESCRIPTION
        使用 Find-Ps1TopLevelInsertPoint 找到安全插入点，将代码插入到
        第一个顶层位置之前，避免嵌套到函数体、if 块等内部。
    .PARAMETER Content
        原始 PowerShell 代码字符串。
    .PARAMETER CodeToInsert
        要插入的代码字符串。
    .PARAMETER SearchFrom
        起始搜索位置，默认为 0。
    .OUTPUTS
        [string] 插入后的完整代码字符串。
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, Position=0)][AllowEmptyString()][string]$Content,
        [Parameter(Mandatory=$true, Position=1)][AllowEmptyString()][string]$CodeToInsert,
        [Parameter(Position=2)][int]$SearchFrom = 0
    )
    if ([string]::IsNullOrEmpty($Content)) { return $CodeToInsert }
    if (-not $CodeToInsert.EndsWith("`n")) { $CodeToInsert += "`n" }
    $insertPoint = Find-Ps1TopLevelInsertPoint -Content $Content -SearchFrom $SearchFrom
    return $Content.Substring(0, $insertPoint) + $CodeToInsert + $Content.Substring($insertPoint)
}

Initialize-EncodingSafety
