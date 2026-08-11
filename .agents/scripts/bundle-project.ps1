<#
.SYNOPSIS
    将 SpecWeave 项目（包括所有嵌套 submodule）打包为单个 bundle 目录
.DESCRIPTION
    递归打包主仓库和所有 submodule 到 .bundle 文件，生成一个可离线分发的目录
    支持解包还原（unbundle）
.EXAMPLE
    # 打包
    ./.agents/scripts/bundle-project.ps1 -Bundle
    # 解包
    ./.agents/scripts/bundle-project.ps1 -Unbundle -BundlePath ./SpecWeave-bundle-20260728 -TargetPath ./restored
#>

#Requires -Version 5.1

param(
    [Parameter(Mandatory=$false, ParameterSetName="bundle")]
    [switch]$Bundle,

    [Parameter(Mandatory=$false, ParameterSetName="unbundle")]
    [switch]$Unbundle,

    [Parameter(Mandatory=$false, ParameterSetName="bundle")]
    [string]$OutputDir = "./SpecWeave-bundle-$(Get-Date -Format 'yyyyMMdd')",

    [Parameter(Mandatory=$true, ParameterSetName="unbundle")]
    [string]$BundlePath,

    [Parameter(Mandatory=$true, ParameterSetName="unbundle")]
    [string]$TargetPath,

    [switch]$Force
)

# ==============================================================================
# 版本校验（自包含，不依赖外部 lib 文件）
# 兼容 Windows PowerShell 5.1 和 PowerShell 7.4+
# 注意：版本检测逻辑在 param() 之后立即执行
# ==============================================================================
function Test-Pwsh7Requirement {
    [CmdletBinding()]
    param(
        [switch]$PassThru
    )

    $isCore = $false
    $currentVersion = $null
    $edition = 'Desktop'
    $versionOk = $false

    if ($PSVersionTable.ContainsKey('PSEdition')) {
        $edition = $PSVersionTable.PSEdition
    }
    $isCore = ($edition -eq 'Core')

    if ($PSVersionTable.ContainsKey('PSVersion')) {
        $currentVersion = $PSVersionTable.PSVersion
    }

    if ($isCore -and $null -ne $currentVersion) {
        $majorOk = ($currentVersion.Major -gt 7)
        $minorOk = ($currentVersion.Major -eq 7 -and $currentVersion.Minor -ge 4)
        $versionOk = ($majorOk -or $minorOk)
    }

    $result = [PSCustomObject]@{
        IsCore      = $isCore
        PSEdition   = $edition
        PSVersion   = $currentVersion
        VersionOk   = $versionOk
        IsSupported = ($isCore -and $versionOk)
    }

    if ($PassThru) {
        return $result
    }

    return $result.IsSupported
}

function Show-Pwsh7RequirementError {
    [CmdletBinding()]
    param()

    $checkResult = Test-Pwsh7Requirement -PassThru

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  错误：PowerShell 版本不支持" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""

    Write-Host "  当前 PowerShell 信息：" -ForegroundColor Yellow
    Write-Host "    PSEdition : $($checkResult.PSEdition)"
    Write-Host "    PSVersion : $($checkResult.PSVersion)"
    Write-Host ""

    Write-Host "  问题说明：" -ForegroundColor Yellow
    Write-Host "    本脚本需要 PowerShell 7.4 或更高版本（pwsh7）。"
    Write-Host "    当前运行的是旧版本或不兼容版本。"
    Write-Host ""

    Write-Host "  安装命令：" -ForegroundColor Yellow
    Write-Host "    winget install Microsoft.PowerShell"
    Write-Host ""

    Write-Host "  文档提示：" -ForegroundColor Yellow
    Write-Host "    请参考项目 ONBOARDING.md 配置开发环境。"
    Write-Host ""

    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""

    exit 1
}

if ($MyInvocation.InvocationName -ne '.') {
    $supported = Test-Pwsh7Requirement
    if (-not $supported) {
        Show-Pwsh7RequirementError
    }
}

$ErrorActionPreference = "Stop"

function Find-ProjectRoot {
    param([string]$StartDir)
    $dir = Resolve-Path $StartDir
    while ($dir -ne [System.IO.Path]::GetPathRoot($dir)) {
        if (Test-Path (Join-Path $dir ".git")) {
            return $dir
        }
        $dir = Split-Path $dir -Parent
    }
    return (Split-Path (Split-Path $StartDir -Parent) -Parent)
}

function Write-Step {
    param([string]$Message)
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "  ✓ $Message" -ForegroundColor Green
}

function Get-Submodules {
    param([string]$RepoPath)
    Push-Location $RepoPath
    try {
        $subs = @()
        $gitmodules = Join-Path $RepoPath ".gitmodules"
        if (Test-Path $gitmodules) {
            $output = git submodule status --recursive 2>$null
            foreach ($line in $output) {
                if ($line -match '^.\s*([0-9a-f]+)\s+([^\s]+)\s+') {
                    $subs += [PSCustomObject]@{
                        Hash = $Matches[1]
                        Path = $Matches[2]
                        FullPath = Join-Path $RepoPath $Matches[2]
                    }
                }
            }
        }
        return $subs
    } finally {
        Pop-Location
    }
}

function Invoke-BundleRepo {
    param(
        [string]$RepoPath,
        [string]$RelativePath,
        [string]$OutputRoot
    )

    $bundleName = if ($RelativePath -eq ".") { "SpecWeave.bundle" } else { "$RelativePath.bundle" }
    $bundleName = $bundleName -replace '/', '__' -replace '\\', '__'
    $bundleFile = Join-Path $OutputRoot $bundleName

    Write-Step "Bundling: $RelativePath"

    Push-Location $RepoPath
    try {
        # 检查是否有未提交的更改
        $status = git status --porcelain
        if ($status -and -not $Force) {
            Write-Warning "  ⚠  $RelativePath 有未提交的更改，使用 -Force 强制打包当前状态"
            $script:hasDirty = $true
        }

        # 创建 bundle（包含所有分支和标签）
        git bundle create $bundleFile --all 2>&1 | Out-Null
        
        # 验证 bundle
        $verifyResult = git bundle verify $bundleFile 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Bundle verification failed for $RelativePath : $verifyResult"
        }

        Write-Success "Created: $bundleName"
        return [PSCustomObject]@{
            RelativePath = $RelativePath
            BundleFile = $bundleName
            IsMain = ($RelativePath -eq ".")
        }
    } finally {
        Pop-Location
    }
}

function Invoke-BundleProject {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "  SpecWeave 项目打包工具" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""

    $root = Find-ProjectRoot -StartDir $PSScriptRoot
    $script:hasDirty = $false

    # 创建输出目录
    if (Test-Path $OutputDir) {
        if ($Force) {
            Remove-Item $OutputDir -Recurse -Force
        } else {
            throw "输出目录已存在: $OutputDir，使用 -Force 覆盖"
        }
    }
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

    Write-Step "项目根目录: $root"
    Write-Step "输出目录: $OutputDir"
    Write-Host ""

    $manifest = @()

    # 打包主仓库
    $mainEntry = Invoke-BundleRepo -RepoPath $root -RelativePath "." -OutputRoot $OutputDir
    $manifest += $mainEntry

    # 递归打包所有 submodule
    $allSubs = Get-Submodules -RepoPath $root
    foreach ($sub in $allSubs) {
        $entry = Invoke-BundleRepo -RepoPath $sub.FullPath -RelativePath $sub.Path -OutputRoot $OutputDir
        $manifest += $entry
    }

    # 生成 manifest.json
    Write-Step "生成 manifest.json"
    $manifestPath = Join-Path $OutputDir "manifest.json"
    $manifest | ConvertTo-Json -Depth 10 | Set-Content $manifestPath -Encoding UTF8
    Write-Success "Manifest created: manifest.json"

    # 生成 README
    $readmePath = Join-Path $OutputDir "README.txt"
    $readme = @"
SpecWeave 离线分发包
===================

打包时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
包含仓库数: $($manifest.Count)

解包方法:
  powershell -ExecutionPolicy Bypass -File ./bundle-project.ps1 -Unbundle `
    -BundlePath ./ -TargetPath ./SpecWeave-restored

仓库列表:
"@
    foreach ($m in $manifest) {
        $marker = if ($m.IsMain) { " [主仓库]" } else { "" }
        $readme += "`n  - $($m.RelativePath)$marker"
    }
    Set-Content $readmePath $readme -Encoding UTF8
    Write-Success "README created"

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  打包完成!" -ForegroundColor Green
    Write-Host "  输出: $OutputDir" -ForegroundColor Green
    Write-Host "  仓库数: $($manifest.Count)" -ForegroundColor Green
    if ($script:hasDirty) {
        Write-Warning "  ⚠  部分仓库有未提交的更改（已按当前状态打包）"
    }
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
}

function Invoke-UnbundleProject {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "  SpecWeave 项目解包工具" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""

    $BundlePath = Resolve-Path $BundlePath

    if (-not (Test-Path (Join-Path $BundlePath "manifest.json"))) {
        throw "无效的 bundle 目录，缺少 manifest.json: $BundlePath"
    }

    Write-Step "Bundle 目录: $BundlePath"
    Write-Step "目标目录: $TargetPath"
    Write-Host ""

    $manifest = Get-Content (Join-Path $BundlePath "manifest.json") | ConvertFrom-Json

    if (Test-Path $TargetPath) {
        if ($Force) {
            Remove-Item $TargetPath -Recurse -Force
        } else {
            throw "目标目录已存在: $TargetPath，使用 -Force 覆盖"
        }
    }

    # 先解压主仓库
    $mainEntry = $manifest | Where-Object { $_.IsMain } | Select-Object -First 1
    $mainBundle = Join-Path $BundlePath $mainEntry.BundleFile
    Write-Step "克隆主仓库..."
    git clone $mainBundle $TargetPath 2>&1 | Out-Null
    Write-Success "主仓库已克隆"

    # 初始化 submodule
    Push-Location $TargetPath
    try {
        # 解压每个 submodule（按路径深度排序，确保父目录先存在）
        $subEntries = $manifest | Where-Object { -not $_.IsMain } | Sort-Object { $_.RelativePath.Count('/') }
        
        foreach ($entry in $subEntries) {
            Write-Step "Restoring submodule: $($entry.RelativePath)"
            
            $subPath = Join-Path $TargetPath $entry.RelativePath
            $subBundle = Join-Path $BundlePath $entry.BundleFile
            
            # 确保父目录存在
            $parentDir = Split-Path $subPath -Parent
            if (-not (Test-Path $parentDir)) {
                New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
            }

            # 从 bundle 克隆 submodule
            git clone $subBundle $subPath 2>&1 | Out-Null
            
            Write-Success "Restored: $($entry.RelativePath)"
        }

        # 修复 submodule 配置（将 remote URL 指向本地 bundle 位置 - 可选）
        Write-Step "Submodule 已全部还原"
    } finally {
        Pop-Location
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  解包完成!" -ForegroundColor Green
    Write-Host "  目标: $TargetPath" -ForegroundColor Green
    Write-Host "  仓库数: $($manifest.Count)" -ForegroundColor Green
    Write-Host ""
    Write-Host "  后续步骤:" -ForegroundColor Yellow
    Write-Host "  cd $TargetPath" -ForegroundColor Yellow
    Write-Host "  git submodule status --recursive" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
}

if ($Bundle) {
    Invoke-BundleProject
} elseif ($Unbundle) {
    Invoke-UnbundleProject
} else {
    Write-Host "SpecWeave Bundle 工具" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "用法:" -ForegroundColor White
    Write-Host "  打包:  ./.agents/scripts/bundle-project.ps1 -Bundle [-OutputDir <dir>] [-Force]"
    Write-Host "  解包:  ./.agents/scripts/bundle-project.ps1 -Unbundle -BundlePath <bundle-dir> -TargetPath <target> [-Force]"
    Write-Host ""
}
