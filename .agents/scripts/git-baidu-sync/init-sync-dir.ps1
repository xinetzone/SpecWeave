[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$SyncRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ColorSuccess = 'Green'
$ColorExists = 'Cyan'
$ColorWarning = 'Yellow'
$ColorInfo = 'Gray'
$ColorHeader = 'Magenta'

$Directories = @(
    'repos',
    'locks',
    'backups',
    'logs',
    'meta',
    'archive'
)

$ReadmeContent = @"
百度网盘 Git 同步空间 - 目录说明
================================

本目录是多设备 Git 仓库同步空间，目录结构如下：

repos/       - 中央裸仓库区，每个仓库一个 <project-name>.git 目录
locks/       - 锁文件区，防止多设备同时写入，<project-name>.lock.json
backups/     - Bundle 备份区，按项目和日期组织：<project-name>/<YYYYMMDD-HHMMSS>.bundle
logs/        - 操作日志区，按日期组织：sync-<YYYYMMDD>.log
meta/        - 设备注册元数据区，包含 README.txt 和 devices.json
archive/     - 废弃仓库归档区，不再活跃的仓库移至此目录

命名规则：
- 目录名只用小写字母、数字、连字符（-）
- 禁止空格、中文、下划线、特殊字符
- 确保跨平台兼容（Windows/macOS/Linux）

初始化脚本：init-sync-dir.ps1 / init-sync-dir.sh
详细文档：请参考 .agents/docs/knowledge/learning/08-systems-infrastructure/git-baidu-sync/
"@

$GitignoreContent = @"
# 忽略临时文件
*.tmp
*.temp
*.swp
*.swo
*~

# 忽略锁文件（保留 locks/ 目录结构）
locks/*.lock.json
!locks/.gitkeep

# 操作系统文件
.DS_Store
Thumbs.db
Desktop.ini

# 编辑器文件
.vscode/
.idea/
"@

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

function Ensure-Directory {
    param([string]$Path)

    if (Test-Path -Path $Path -PathType Container) {
        Write-ColorMessage "目录已存在: $Path" -Color $ColorExists -Prefix 'SKIP'
        return $false
    }
    else {
        New-Item -Path $Path -ItemType Directory -Force | Out-Null
        Write-ColorMessage "已创建目录: $Path" -Color $ColorSuccess -Prefix 'CREATE'
        return $true
    }
}

function Ensure-File {
    param(
        [string]$Path,
        [string]$Content
    )

    if (Test-Path -Path $Path -PathType Leaf) {
        Write-ColorMessage "文件已存在: $Path" -Color $ColorExists -Prefix 'SKIP'
        return $false
    }
    else {
        Set-Content -Path $Path -Value $Content -Encoding UTF8
        Write-ColorMessage "已创建文件: $Path" -Color $ColorSuccess -Prefix 'CREATE'
        return $true
    }
}

function Show-DirectoryTree {
    param([string]$RootPath)

    Write-Host ''
    Write-ColorMessage '=== 目录结构 ===' -Color $ColorHeader
    Write-Host (Split-Path -Path $RootPath -Leaf) '/' -ForegroundColor $ColorHeader

    $items = Get-ChildItem -Path $RootPath -Force | Sort-Object { $_.PSIsContainer -eq $false }, Name
    foreach ($item in $items) {
        $prefix = if ($item -eq $items[-1]) { '    └── ' } else { '    ├── ' }
        if ($item.PSIsContainer) {
            Write-Host ($prefix + $item.Name + '/') -ForegroundColor $ColorInfo
            $subItems = Get-ChildItem -Path $item.FullName -Force | Sort-Object Name
            foreach ($subItem in $subItems) {
                $subPrefix = if ($subItem -eq $subItems[-1]) { '    │   └── ' } else { '    │   ├── ' }
                if ($subItem -eq $subItems[-1] -and $item -ne $items[-1]) {
                    $subPrefix = '    │   └── '
                }
                $displayName = if ($subItem.PSIsContainer) { $subItem.Name + '/' } else { $subItem.Name }
                Write-Host ($subPrefix + $displayName) -ForegroundColor $ColorInfo
            }
        }
        else {
            Write-Host ($prefix + $item.Name) -ForegroundColor $ColorInfo
        }
    }
    Write-Host ''
}

# Main
Write-Host ''
Write-ColorMessage '=== 百度网盘 Git 同步空间初始化 ===' -Color $ColorHeader
Write-ColorMessage "目标路径: $SyncRoot" -Color $ColorInfo
Write-Host ''

$rootExists = Test-Path -Path $SyncRoot -PathType Container
if (-not $rootExists) {
    New-Item -Path $SyncRoot -ItemType Directory -Force | Out-Null
    Write-ColorMessage "已创建根目录: $SyncRoot" -Color $ColorSuccess -Prefix 'CREATE'
}
else {
    Write-ColorMessage "根目录已存在: $SyncRoot" -Color $ColorExists -Prefix 'SKIP'
}
Write-Host ''

Write-ColorMessage '--- 创建子目录 ---' -Color $ColorHeader
$createdCount = 0
$existedCount = 0
foreach ($dir in $Directories) {
    $fullPath = Join-Path -Path $SyncRoot -ChildPath $dir
    if (Ensure-Directory -Path $fullPath) {
        $createdCount++
    }
    else {
        $existedCount++
    }
}
Write-Host ''

$locksGitkeep = Join-Path -Path $SyncRoot -ChildPath 'locks\.gitkeep'
if (-not (Test-Path -Path $locksGitkeep)) {
    New-Item -Path $locksGitkeep -ItemType File -Force | Out-Null
    Write-ColorMessage "已创建文件: $locksGitkeep" -Color $ColorSuccess -Prefix 'CREATE'
}
else {
    Write-ColorMessage "文件已存在: $locksGitkeep" -Color $ColorExists -Prefix 'SKIP'
}
Write-Host ''

Write-ColorMessage '--- 创建说明文件 ---' -Color $ColorHeader
$readmePath = Join-Path -Path $SyncRoot -ChildPath 'meta\README.txt'
[void](Ensure-File -Path $readmePath -Content $ReadmeContent)
Write-Host ''

Write-ColorMessage '--- 创建 .gitignore ---' -Color $ColorHeader
$gitignorePath = Join-Path -Path $SyncRoot -ChildPath '.gitignore'
[void](Ensure-File -Path $gitignorePath -Content $GitignoreContent)
Write-Host ''

Write-ColorMessage '=== 初始化完成 ===' -Color $ColorHeader
Write-ColorMessage "新建目录: $createdCount 个" -Color $ColorSuccess
Write-ColorMessage "已存在: $existedCount 个" -Color $ColorExists

if ($rootExists -and ($createdCount -eq 0)) {
    Write-ColorMessage '提示: 所有目录均已存在，幂等执行成功' -Color $ColorWarning -Prefix 'INFO'
}

Show-DirectoryTree -RootPath $SyncRoot
