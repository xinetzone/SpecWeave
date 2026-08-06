#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
    echo "用法: $0 <同步空间根路径>"
    echo "示例: $0 ~/BaiduSync/git-sync"
    exit 1
fi

SYNC_ROOT="$1"

COLOR_SUCCESS='\033[0;32m'
COLOR_EXISTS='\033[0;36m'
COLOR_WARNING='\033[0;33m'
COLOR_INFO='\033[0;37m'
COLOR_HEADER='\033[0;35m'
COLOR_RESET='\033[0m'

DIRECTORIES=(
    "repos"
    "locks"
    "backups"
    "logs"
    "meta"
    "archive"
)

README_CONTENT='百度网盘 Git 同步空间 - 目录说明
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
'

GITIGNORE_CONTENT='# 忽略临时文件
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
'

print_msg() {
    local msg="$1"
    local color="$2"
    local prefix="${3:-}"
    if [ -n "$prefix" ]; then
        echo -e "${color}[${prefix}] ${msg}${COLOR_RESET}"
    else
        echo -e "${color}${msg}${COLOR_RESET}"
    fi
}

ensure_dir() {
    local dir="$1"
    if [ -d "$dir" ]; then
        print_msg "目录已存在: $dir" "$COLOR_EXISTS" "SKIP"
        return 1
    else
        mkdir -p "$dir"
        print_msg "已创建目录: $dir" "$COLOR_SUCCESS" "CREATE"
        return 0
    fi
}

ensure_file() {
    local file="$1"
    local content="$2"
    if [ -f "$file" ]; then
        print_msg "文件已存在: $file" "$COLOR_EXISTS" "SKIP"
        return 1
    else
        printf '%s\n' "$content" > "$file"
        print_msg "已创建文件: $file" "$COLOR_SUCCESS" "CREATE"
        return 0
    fi
}

show_tree() {
    local root="$1"
    local root_name
    root_name=$(basename "$root")
    echo ""
    print_msg "=== 目录结构 ===" "$COLOR_HEADER"
    echo -e "${COLOR_HEADER}${root_name}/${COLOR_RESET}"

    local items=()
    while IFS= read -r -d '' item; do
        items+=("$item")
    done < <(find "$root" -maxdepth 1 -mindepth 1 -print0 2>/dev/null | sort -z)

    local total=${#items[@]}
    local idx=0
    for item in "${items[@]}"; do
        idx=$((idx + 1))
        local name
        name=$(basename "$item")
        local is_last=0
        if [ "$idx" -eq "$total" ]; then
            is_last=1
        fi

        local prefix="    ├── "
        [ "$is_last" -eq 1 ] && prefix="    └── "

        if [ -d "$item" ]; then
            echo -e "${COLOR_INFO}${prefix}${name}/${COLOR_RESET}"

            local subitems=()
            while IFS= read -r -d '' subitem; do
                subitems+=("$subitem")
            done < <(find "$item" -maxdepth 1 -mindepth 1 -print0 2>/dev/null | sort -z)

            local subtotal=${#subitems[@]}
            local subidx=0
            for subitem in "${subitems[@]}"; do
                subidx=$((subidx + 1))
                local subname
                subname=$(basename "$subitem")
                local subprefix="    │   ├── "
                if [ "$subidx" -eq "$subtotal" ]; then
                    if [ "$is_last" -eq 1 ]; then
                        subprefix="        └── "
                    else
                        subprefix="    │   └── "
                    fi
                fi
                local display_name="$subname"
                [ -d "$subitem" ] && display_name="${subname}/"
                echo -e "${COLOR_INFO}${subprefix}${display_name}${COLOR_RESET}"
            done
        else
            echo -e "${COLOR_INFO}${prefix}${name}${COLOR_RESET}"
        fi
    done
    echo ""
}

created_count=0
existed_count=0

echo ""
print_msg "=== 百度网盘 Git 同步空间初始化 ===" "$COLOR_HEADER"
print_msg "目标路径: $SYNC_ROOT" "$COLOR_INFO"
echo ""

root_existed=1
if [ ! -d "$SYNC_ROOT" ]; then
    mkdir -p "$SYNC_ROOT"
    print_msg "已创建根目录: $SYNC_ROOT" "$COLOR_SUCCESS" "CREATE"
    root_existed=0
else
    print_msg "根目录已存在: $SYNC_ROOT" "$COLOR_EXISTS" "SKIP"
fi
echo ""

print_msg "--- 创建子目录 ---" "$COLOR_HEADER"
for dir in "${DIRECTORIES[@]}"; do
    full_path="${SYNC_ROOT}/${dir}"
    if ensure_dir "$full_path"; then
        created_count=$((created_count + 1))
    else
        existed_count=$((existed_count + 1))
    fi
done
echo ""

locks_gitkeep="${SYNC_ROOT}/locks/.gitkeep"
if [ ! -f "$locks_gitkeep" ]; then
    touch "$locks_gitkeep"
    print_msg "已创建文件: $locks_gitkeep" "$COLOR_SUCCESS" "CREATE"
else
    print_msg "文件已存在: $locks_gitkeep" "$COLOR_EXISTS" "SKIP"
fi
echo ""

print_msg "--- 创建说明文件 ---" "$COLOR_HEADER"
readme_path="${SYNC_ROOT}/meta/README.txt"
ensure_file "$readme_path" "$README_CONTENT"
echo ""

print_msg "--- 创建 .gitignore ---" "$COLOR_HEADER"
gitignore_path="${SYNC_ROOT}/.gitignore"
ensure_file "$gitignore_path" "$GITIGNORE_CONTENT"
echo ""

print_msg "=== 初始化完成 ===" "$COLOR_HEADER"
print_msg "新建目录: ${created_count} 个" "$COLOR_SUCCESS"
print_msg "已存在: ${existed_count} 个" "$COLOR_EXISTS"

if [ "$root_existed" -eq 1 ] && [ "$created_count" -eq 0 ]; then
    print_msg "提示: 所有目录均已存在，幂等执行成功" "$COLOR_WARNING" "INFO"
fi

show_tree "$SYNC_ROOT"
