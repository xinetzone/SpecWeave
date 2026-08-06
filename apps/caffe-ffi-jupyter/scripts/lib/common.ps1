# caffe-ffi-jupyter 公共工具库
# 提供 WSL 检测、路径转换、Docker 检查、Python 版本验证等通用功能
# 用法：. "$PSScriptRoot/common.ps1"

# 保存 lib/ 目录路径（加载时求值，后续函数调用不受作用域影响）
$script:CaffeLibDir = $PSScriptRoot

# ── WSL 环境检测 ──

function Test-WslAvailable {
    [CmdletBinding()]
    param()

    # 检查是否在 WSL 中运行
    if ($env:WSL_DISTRO_NAME -or (Test-Path '/proc/version' -ErrorAction SilentlyContinue)) {
        return $false  # 已在 WSL 内，不需要再调用 wsl.exe
    }

    # 检查 wsl.exe 是否可用
    try {
        $null = Get-Command wsl.exe -ErrorAction Stop
        # 检查默认发行版是否存在
        $distros = & wsl.exe -l -q 2>&1
        if ($LASTEXITCODE -eq 0 -and $distros) {
            # 过滤掉空行和标题（wsl.exe -l -q 第一行可能有BOM）
            $hasDistro = $false
            foreach ($d in $distros) {
                $line = $d.ToString().Trim()
                if ($line -and -not $line.StartsWith([char]0xFEFF)) {
                    $hasDistro = $true
                    break
                }
            }
            return $hasDistro
        }
        return $false
    } catch {
        return $false
    }
}

function Get-WslDefaultDistro {
    [CmdletBinding()]
    param()

    if (-not (Test-WslAvailable)) { return $null }

    $distros = & wsl.exe -l -q 2>&1
    if ($LASTEXITCODE -ne 0) { return $null }

    foreach ($d in $distros) {
        $line = $d.ToString().Trim()
        if ($line -and -not $line.StartsWith([char]0xFEFF) -and -not $line.Contains('(默认)') -and -not $line.Contains('(Default)')) {
            return $line
        }
    }
    return $null
}

# ── 路径转换 ──

function Convert-WindowsPathToWsl {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$WindowsPath
    )

    $fullPath = [System.IO.Path]::GetFullPath($WindowsPath)
    $drive = $fullPath.Substring(0, 1).ToLower()
    $rest = $fullPath.Substring(2).Replace('\', '/')
    return "/mnt/$drive$rest"
}

# ── Docker 检查 ──

function Test-DockerAvailable {
    [CmdletBinding()]
    param(
        [switch]$InWsl
    )

    try {
        if ($InWsl -and (Test-WslAvailable)) {
            $null = & wsl.exe bash -c "command -v docker" 2>&1
            if ($LASTEXITCODE -ne 0) { return $false }
            $null = & wsl.exe -- docker ps 2>&1
        } else {
            $null = Get-Command docker -ErrorAction Stop
            $null = docker ps 2>&1
        }
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Test-DockerContainerRunning {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$ContainerName,
        [switch]$InWsl
    )

    try {
        if ($InWsl -and (Test-WslAvailable)) {
            $status = & wsl.exe -- docker inspect -f '{{.State.Running}}' "$ContainerName" 2>&1
        } else {
            $status = docker inspect -f '{{.State.Running}}' "$ContainerName" 2>&1
        }
        return ($LASTEXITCODE -eq 0 -and $status.Trim() -eq 'true')
    } catch {
        return $false
    }
}

function Test-DockerImageExists {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$ImageName,
        [switch]$InWsl
    )

    try {
        if ($InWsl -and (Test-WslAvailable)) {
            $null = & wsl.exe -- docker image inspect "$ImageName" 2>&1
        } else {
            $null = docker image inspect "$ImageName" 2>&1
        }
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

# ── Python 版本检查 ──

function Test-PythonVersion {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$PythonPath,
        [Parameter(Mandatory=$true)][version]$MinVersion
    )

    try {
        $versionOutput = & $PythonPath -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>&1
        if ($LASTEXITCODE -ne 0) { return $false }
        $ver = [version]($versionOutput.Trim())
        return $ver -ge $MinVersion
    } catch {
        return $false
    }
}

function Get-PythonVersion {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$PythonPath
    )

    try {
        $versionOutput = & $PythonPath -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            return [version]($versionOutput.Trim())
        }
    } catch {}
    return $null
}

# ── 脚本目录解析 ──

function Get-ScriptDirectory {
    [CmdletBinding()]
    param()

    # 向上查找调用栈，返回第一个非 lib/ 目录的 PSScriptRoot（即调用方脚本目录）
    $scope = 1
    while ($scope -lt 10) {
        try {
            $root = Get-Variable -Name PSScriptRoot -Scope $scope -ValueOnly -ErrorAction Stop
            if ($root -and $root -ne $script:CaffeLibDir) { return $root }
        } catch {}
        $scope++
    }
    # fallback：返回 common.ps1 所在目录
    return $script:CaffeLibDir
}

function Get-ProjectRoot {
    [CmdletBinding()]
    param()

    $scriptDir = Get-ScriptDirectory
    # scripts/ 目录位于项目根目录下
    return (Resolve-Path (Join-Path $scriptDir '..')).Path
}

# ── 自动加载同级依赖库（顶层 dot-source，函数会定义到调用方作用域） ──
# pwsh7-version-check.ps1 和 logging.ps1 都有幂等守卫，重复 dot-source 安全
. "$script:CaffeLibDir/pwsh7-version-check.ps1"
. "$script:CaffeLibDir/logging.ps1"

# ── WSL 命令执行封装 ──

function Invoke-WslCommand {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$Command,
        [string]$Distro,
        [string]$WorkingDirectory,
        [switch]$PassThru
    )

    $wslArgs = @()
    if ($Distro) { $wslArgs += '-d', $Distro }
    if ($WorkingDirectory) {
        $wslPath = Convert-WindowsPathToWsl $WorkingDirectory
        $wslArgs += '--cd', $wslPath
    }
    $wslArgs += '--', 'bash', '-c', $Command

    # 将 wsl.exe 输出写到主机（不进入函数输出流），避免污染布尔/退出码返回值
    & wsl.exe $wslArgs 2>&1 | Out-Host
    $exitCode = $LASTEXITCODE

    if ($PassThru) { return $exitCode }
    return ($exitCode -eq 0)
}

# ── 文件哈希计算 ──

function Get-FileHashString {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [ValidateSet('MD5','SHA1','SHA256')][string]$Algorithm = 'SHA256'
    )

    try {
        $hash = Get-FileHash -Path $Path -Algorithm $Algorithm -ErrorAction Stop
        return $hash.Hash.ToLower()
    } catch {
        return $null
    }
}
