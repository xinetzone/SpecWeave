[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('--global', '--local', '--system')]
    [string]$Scope = '--global',

    [switch]$Attributes,

    [Parameter()]
    [string]$TargetDir = '.'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ColorSuccess = 'Green'
$ColorChanged = 'Yellow'
$ColorExists = 'Cyan'
$ColorWarning = 'DarkYellow'
$ColorError = 'Red'
$ColorInfo = 'Gray'
$ColorHeader = 'Magenta'

$MinGitVersion = [Version]'2.30.0'

$GitAttributesContent = @'
# 默认：所有文本文件自动检测换行符，入库时统一为 LF
* text=auto

# ===== 明确指定需要 LF 换行符的文件（跨平台脚本/源码）=====
*.sh text eol=lf
*.bash text eol=lf
*.zsh text eol=lf
*.fish text eol=lf
*.py text eol=lf
*.rb text eol=lf
*.pl text eol=lf
*.pm text eol=lf
*.php text eol=lf
*.c text eol=lf
*.h text eol=lf
*.cpp text eol=lf
*.hpp text eol=lf
*.cc text eol=lf
*.hh text eol=lf
*.java text eol=lf
*.go text eol=lf
*.rs text eol=lf
*.js text eol=lf
*.jsx text eol=lf
*.ts text eol=lf
*.tsx text eol=lf
*.mjs text eol=lf
*.cjs text eol=lf
*.css text eol=lf
*.scss text eol=lf
*.less text eol=lf
*.html text eol=lf
*.htm text eol=lf
*.xml text eol=lf
*.json text eol=lf
*.yaml text eol=lf
*.yml text eol=lf
*.toml text eol=lf
*.ini text eol=lf
*.cfg text eol=lf
*.conf text eol=lf
*.env text eol=lf
*.sql text eol=lf
*.md text eol=lf
*.markdown text eol=lf
*.rst text eol=lf
*.txt text eol=lf
*.textile text eol=lf
Makefile text eol=lf
makefile text eol=lf
*.mk text eol=lf
CMakeLists.txt text eol=lf
*.cmake text eol=lf
Dockerfile text eol=lf
docker-compose.yml text eol=lf
*.service text eol=lf
*.timer text eol=lf
.gitignore text eol=lf
.gitattributes text eol=lf
.gitmodules text eol=lf
.mailmap text eol=lf

# ===== 明确指定需要 CRLF 换行符的文件（Windows 专用）=====
*.bat text eol=crlf
*.cmd text eol=crlf
*.ps1 text eol=crlf
*.psm1 text eol=crlf
*.psd1 text eol=crlf
*.reg text eol=crlf
*.inf text eol=crlf
*.ahk text eol=crlf

# ===== 二进制文件（禁止换行符转换，禁止 diff）=====
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.bmp binary
*.ico binary
*.svg binary
*.webp binary
*.tiff binary
*.tif binary
*.ttf binary
*.otf binary
*.woff binary
*.woff2 binary
*.eot binary
*.pdf binary
*.doc binary
*.docx binary
*.xls binary
*.xlsx binary
*.ppt binary
*.pptx binary
*.odt binary
*.ods binary
*.odp binary
*.zip binary
*.tar binary
*.gz binary
*.bz2 binary
*.xz binary
*.7z binary
*.rar binary
*.zst binary
*.lz binary
*.lzma binary
*.tgz binary
*.tbz2 binary
*.pack binary
*.idx binary
*.bundle binary
*.exe binary
*.dll binary
*.so binary
*.dylib binary
*.a binary
*.lib binary
*.o binary
*.obj binary
*.bin binary
*.msi binary
*.mp3 binary
*.mp4 binary
*.wav binary
*.flac binary
*.ogg binary
*.avi binary
*.mkv binary
*.mov binary
*.webm binary
*.sqlite binary
*.db binary
*.swf binary
*.class binary
*.jar binary
*.war binary
*.pyc binary
*.pyo binary
*.pyd binary
*.egg binary
*.whl binary
'@

function Write-ColorMessage {
    param(
        [string]$Message,
        [string]$Color = 'White',
        [string]$Prefix = ''
    )
    if ($Prefix) {
        Write-Host "[$Prefix] " -NoNewline -ForegroundColor $Color
    }
    Write-Host $Message -ForegroundColor $Color
}

function Detect-OS {
    if ($IsWindows -or $env:OS -eq 'Windows_NT' -or (-not (Get-Variable -Name IsWindows -ErrorAction SilentlyContinue) -and [Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT)) {
        return 'windows'
    }
    if ($IsMacOS -or (Test-Path '/usr/bin/sw_vers')) {
        return 'macos'
    }
    if ($IsLinux -or (Test-Path '/etc/os-release')) {
        return 'linux'
    }
    return 'unknown'
}

function Get-GitVersion {
    try {
        $versionOutput = & git --version 2>$null
        if ($versionOutput -match 'git version (\d+\.\d+\.\d+)') {
            return [Version]$Matches[1]
        }
        return $null
    }
    catch {
        return $null
    }
}

function Get-GitConfig {
    param(
        [string]$Key,
        [string]$ConfigScope
    )
    try {
        $value = & git config $ConfigScope --get $Key 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $value
        }
        return $null
    }
    catch {
        return $null
    }
}

function Set-GitConfigValue {
    param(
        [string]$Key,
        [string]$Value,
        [string]$ConfigScope,
        [string]$Description
    )

    $oldValue = Get-GitConfig -Key $Key -ConfigScope $ConfigScope
    $effectiveScope = $ConfigScope

    if ($null -eq $oldValue) {
        $allScopes = @('--system', '--global', '--local')
        foreach ($s in $allScopes) {
            if ($s -ne $ConfigScope) {
                $v = Get-GitConfig -Key $Key -ConfigScope $s
                if ($null -ne $v) {
                    $oldValue = $v
                    break
                }
            }
        }
    }

    if ($null -ne $oldValue -and $oldValue -eq $Value) {
        Write-ColorMessage "${Key} = ${Value} (${Description})" -Color $ColorExists -Prefix 'OK'
        return @{ Changed = $false; Old = $oldValue; New = $Value }
    }

    & git config $ConfigScope $Key $Value 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-ColorMessage "${Key}: 设置失败" -Color $ColorError -Prefix 'ERR'
        return @{ Changed = $false; Old = $oldValue; New = $null; Error = $true }
    }

    if ($null -eq $oldValue) {
        Write-ColorMessage "${Key}: (未设置) → ${Value} (${Description})" -Color $ColorChanged -Prefix 'SET'
    }
    else {
        Write-ColorMessage "${Key}: ${oldValue} → ${Value} (${Description})" -Color $ColorChanged -Prefix 'CHG'
    }
    return @{ Changed = $true; Old = $oldValue; New = $Value }
}

function Write-ConfigSection {
    param([string]$Title)
    Write-Host ''
    Write-ColorMessage "--- ${Title} ---" -Color $ColorHeader
}

Write-Host ''
Write-ColorMessage '=== Git 跨平台配置工具 ===' -Color $ColorHeader
Write-Host ''

$os = Detect-OS
Write-ColorMessage "检测到操作系统: $os" -Color $ColorInfo
Write-ColorMessage "配置作用域: $Scope" -Color $ColorInfo
Write-Host ''

$gitVersion = Get-GitVersion
if ($null -eq $gitVersion) {
    Write-ColorMessage '未检测到 Git，请先安装 Git' -Color $ColorError -Prefix 'ERR'
    exit 1
}
Write-ColorMessage "Git 版本: $gitVersion" -Color $ColorInfo
if ($gitVersion -lt $MinGitVersion) {
    Write-ColorMessage "警告: Git 版本 $gitVersion 低于推荐版本 $MinGitVersion，部分配置可能不支持" -Color $ColorWarning -Prefix 'WARN'
}
Write-Host ''

$changes = @()

if ($Attributes) {
    Write-ConfigSection -Title '生成 .gitattributes 模板'
    $targetPath = Join-Path -Path $TargetDir -ChildPath '.gitattributes'
    if (Test-Path -Path $targetPath -PathType Leaf) {
        Write-ColorMessage ".gitattributes 已存在: $targetPath" -Color $ColorExists -Prefix 'SKIP'
    }
    else {
        Set-Content -Path $targetPath -Value $GitAttributesContent -Encoding UTF8
        Write-ColorMessage "已创建 .gitattributes: $targetPath" -Color $ColorSuccess -Prefix 'CREATE'
    }
    Write-Host ''
}

Write-ConfigSection -Title '通用性能与 GC 配置（所有平台）'
$changes += Set-GitConfigValue -Key 'core.preloadindex' -Value 'true' -ConfigScope $Scope -Description '并行预加载索引，加速 status/diff'
$changes += Set-GitConfigValue -Key 'gc.auto' -Value '6700' -ConfigScope $Scope -Description '松散对象超过此数自动 GC，减少小文件'
$changes += Set-GitConfigValue -Key 'gc.autopacklimit' -Value '1' -ConfigScope $Scope -Description '保持最少 pack 文件数，优化网盘同步'
$changes += Set-GitConfigValue -Key 'push.default' -Value 'simple' -ConfigScope $Scope -Description '安全的默认推送策略'
$changes += Set-GitConfigValue -Key 'core.quotepath' -Value 'false' -ConfigScope $Scope -Description '禁用路径转义，中文文件名正常显示'

if ($os -eq 'windows') {
    Write-Host ''
    Write-ConfigSection -Title 'Windows 平台特定配置'
    $changes += Set-GitConfigValue -Key 'core.autocrlf' -Value 'true' -ConfigScope $Scope -Description '检出转 CRLF，提交转 LF'
    $changes += Set-GitConfigValue -Key 'core.fscache' -Value 'true' -ConfigScope $Scope -Description 'Windows 文件系统缓存，加速操作'
    $changes += Set-GitConfigValue -Key 'core.longpaths' -Value 'true' -ConfigScope $Scope -Description '解除 260 字符路径限制'
    if ($Scope -eq '--local') {
        $changes += Set-GitConfigValue -Key 'core.filemode' -Value 'false' -ConfigScope $Scope -Description '忽略 Unix 权限位'
        $changes += Set-GitConfigValue -Key 'core.symlinks' -Value 'false' -ConfigScope $Scope -Description '不创建符号链接，避免权限问题'
    }
}
elseif ($os -eq 'macos' -or $os -eq 'linux') {
    Write-Host ''
    Write-ConfigSection -Title "$os 平台特定配置"
    $changes += Set-GitConfigValue -Key 'core.autocrlf' -Value 'input' -ConfigScope $Scope -Description '提交转 LF，检出不转换'
    if ($Scope -eq '--local') {
        $bare = & git rev-parse --is-bare-repository 2>$null
        if ($bare -eq 'true') {
            Write-ColorMessage '检测到裸仓库，使用跨平台兼容设置' -Color $ColorInfo -Prefix 'INFO'
            $changes += Set-GitConfigValue -Key 'core.filemode' -Value 'false' -ConfigScope $Scope -Description '裸仓库跨平台兼容：忽略权限位'
            $changes += Set-GitConfigValue -Key 'core.symlinks' -Value 'false' -ConfigScope $Scope -Description '裸仓库跨平台兼容：不使用 symlink'
        }
        else {
            $changes += Set-GitConfigValue -Key 'core.filemode' -Value 'true' -ConfigScope $Scope -Description '跟踪 Unix 文件权限位'
            $changes += Set-GitConfigValue -Key 'core.symlinks' -Value 'true' -ConfigScope $Scope -Description '支持符号链接'
        }
    }
}
else {
    Write-ColorMessage '无法识别操作系统，跳过平台特定配置' -Color $ColorWarning -Prefix 'WARN'
}

if ($Scope -eq '--local') {
    Write-Host ''
    Write-ConfigSection -Title '非裸中央仓库可选配置'
    $bare = & git rev-parse --is-bare-repository 2>$null
    if ($bare -eq 'false') {
        $receiveValue = Get-GitConfig -Key 'receive.denyCurrentBranch' -ConfigScope $Scope
        if ($null -eq $receiveValue) {
            Write-ColorMessage '提示: 非裸仓库可设置 receive.denyCurrentBranch=updateInstead 允许直接推送' -Color $ColorInfo -Prefix 'TIP'
            Write-ColorMessage '执行: git config --local receive.denyCurrentBranch updateInstead' -Color $ColorInfo
        }
    }
}

$changedCount = ($changes | Where-Object { $_.Changed -eq $true }).Count
$okCount = ($changes | Where-Object { $_.Changed -eq $false -and -not $_.Error }).Count

Write-Host ''
Write-ConfigSection -Title '配置验证'
Write-ColorMessage "执行 git config ${Scope} --list ..." -Color $ColorInfo
Write-Host ''

& git config $Scope --list

Write-Host ''
Write-ColorMessage '=== 配置完成 ===' -Color $ColorHeader
Write-ColorMessage "变更项: $changedCount 个" -Color $ColorChanged
Write-ColorMessage "已存在: $okCount 个" -Color $ColorExists

if ($Scope -eq '--global') {
    Write-Host ''
    Write-ColorMessage '提示: 对网盘同步仓库，建议进入仓库目录后用 --local 再执行一次：' -Color $ColorWarning -Prefix 'TIP'
    Write-ColorMessage "  pwsh -File $($MyInvocation.MyCommand.Path) --local" -Color $ColorInfo
}
