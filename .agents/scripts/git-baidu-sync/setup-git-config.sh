#!/usr/bin/env bash
set -euo pipefail

SCOPE='--global'
ATTRIBUTES=0
TARGET_DIR='.'

COLOR_SUCCESS='\033[0;32m'
COLOR_CHANGED='\033[0;33m'
COLOR_EXISTS='\033[0;36m'
COLOR_WARNING='\033[0;33m'
COLOR_ERROR='\033[0;31m'
COLOR_INFO='\033[0;37m'
COLOR_HEADER='\033[0;35m'
COLOR_RESET='\033[0m'

MIN_GIT_VERSION='2.30.0'

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

print_section() {
    local title="$1"
    echo ""
    print_msg "--- ${title} ---" "$COLOR_HEADER"
}

detect_os() {
    local os='unknown'
    case "$(uname -s)" in
        Darwin)
            os='macos'
            ;;
        Linux)
            os='linux'
            ;;
        MINGW*|MSYS*|CYGWIN*)
            os='windows'
            ;;
    esac
    echo "$os"
}

version_compare() {
    local v1="$1"
    local v2="$2"
    if [ "$(printf '%s\n' "$v1" "$v2" | sort -V | head -n1)" = "$v2" ]; then
        return 0
    else
        return 1
    fi
}

get_git_version() {
    local version_output
    version_output=$(git --version 2>/dev/null) || true
    if echo "$version_output" | grep -q 'git version'; then
        echo "$version_output" | sed 's/git version //' | awk '{print $1}'
    else
        echo ""
    fi
}

get_git_config() {
    local key="$1"
    local config_scope="$2"
    git config "$config_scope" --get "$key" 2>/dev/null || echo ""
}

get_any_config() {
    local key="$1"
    local val
    for s in '--system' '--global' '--local'; do
        val=$(get_git_config "$key" "$s")
        if [ -n "$val" ]; then
            echo "$val"
            return
        fi
    done
    echo ""
}

set_git_config_value() {
    local key="$1"
    local value="$2"
    local config_scope="$3"
    local description="$4"

    local old_value
    old_value=$(get_git_config "$key" "$config_scope")
    if [ -z "$old_value" ]; then
        old_value=$(get_any_config "$key")
    fi

    if [ -n "$old_value" ] && [ "$old_value" = "$value" ]; then
        print_msg "${key} = ${value} (${description})" "$COLOR_EXISTS" 'OK'
        OK_COUNT=$((OK_COUNT + 1))
        return 0
    fi

    if git config "$config_scope" "$key" "$value" 2>/dev/null; then
        if [ -z "$old_value" ]; then
            print_msg "${key}: (未设置) → ${value} (${description})" "$COLOR_CHANGED" 'SET'
        else
            print_msg "${key}: ${old_value} → ${value} (${description})" "$COLOR_CHANGED" 'CHG'
        fi
        CHANGED_COUNT=$((CHANGED_COUNT + 1))
        return 0
    else
        print_msg "${key}: 设置失败" "$COLOR_ERROR" 'ERR'
        return 0
    fi
}

GITATTRIBUTES_CONTENT='# 默认：所有文本文件自动检测换行符，入库时统一为 LF
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
'

while [ $# -gt 0 ]; do
    case "$1" in
        --global|--local|--system)
            SCOPE="$1"
            shift
            ;;
        --attributes)
            ATTRIBUTES=1
            shift
            ;;
        --target-dir)
            if [ $# -lt 2 ]; then
                print_msg "--target-dir 需要参数" "$COLOR_ERROR" 'ERR'
                exit 1
            fi
            TARGET_DIR="$2"
            shift 2
            ;;
        --target-dir=*)
            TARGET_DIR="${1#--target-dir=}"
            shift
            ;;
        -h|--help)
            echo "用法: $0 [--global|--local|--system] [--attributes] [--target-dir <dir>]"
            echo ""
            echo "选项:"
            echo "  --global         设置全局配置（默认）"
            echo "  --local          设置当前仓库本地配置"
            echo "  --system         设置系统级配置"
            echo "  --attributes     生成 .gitattributes 模板"
            echo "  --target-dir DIR 指定 .gitattributes 生成目录（默认当前目录）"
            echo "  -h, --help       显示此帮助"
            exit 0
            ;;
        *)
            print_msg "未知参数: $1" "$COLOR_ERROR" 'ERR'
            exit 1
            ;;
    esac
done

echo ""
print_msg "=== Git 跨平台配置工具 ===" "$COLOR_HEADER"
echo ""

OS=$(detect_os)
print_msg "检测到操作系统: $OS" "$COLOR_INFO"
print_msg "配置作用域: $SCOPE" "$COLOR_INFO"
echo ""

GIT_VERSION=$(get_git_version)
if [ -z "$GIT_VERSION" ]; then
    print_msg '未检测到 Git，请先安装 Git' "$COLOR_ERROR" 'ERR'
    exit 1
fi
print_msg "Git 版本: $GIT_VERSION" "$COLOR_INFO"
if ! version_compare "$GIT_VERSION" "$MIN_GIT_VERSION"; then
    print_msg "警告: Git 版本 $GIT_VERSION 低于推荐版本 $MIN_GIT_VERSION，部分配置可能不支持" "$COLOR_WARNING" 'WARN'
fi
echo ""

CHANGED_COUNT=0
OK_COUNT=0

if [ "$ATTRIBUTES" -eq 1 ]; then
    print_section '生成 .gitattributes 模板'
    target_path="${TARGET_DIR}/.gitattributes"
    if [ -f "$target_path" ]; then
        print_msg ".gitattributes 已存在: $target_path" "$COLOR_EXISTS" 'SKIP'
    else
        printf '%s\n' "$GITATTRIBUTES_CONTENT" > "$target_path"
        print_msg "已创建 .gitattributes: $target_path" "$COLOR_SUCCESS" 'CREATE'
    fi
    echo ""
fi

print_section '通用性能与 GC 配置（所有平台）'
set_git_config_value 'core.preloadindex' 'true' "$SCOPE" '并行预加载索引，加速 status/diff'
set_git_config_value 'gc.auto' '6700' "$SCOPE" '松散对象超过此数自动 GC，减少小文件'
set_git_config_value 'gc.autopacklimit' '1' "$SCOPE" '保持最少 pack 文件数，优化网盘同步'
set_git_config_value 'push.default' 'simple' "$SCOPE" '安全的默认推送策略'
set_git_config_value 'core.quotepath' 'false' "$SCOPE" '禁用路径转义，中文文件名正常显示'

if [ "$OS" = 'windows' ]; then
    echo ""
    print_section 'Windows 平台特定配置'
    set_git_config_value 'core.autocrlf' 'true' "$SCOPE" '检出转 CRLF，提交转 LF'
    set_git_config_value 'core.fscache' 'true' "$SCOPE" 'Windows 文件系统缓存，加速操作'
    set_git_config_value 'core.longpaths' 'true' "$SCOPE" '解除 260 字符路径限制'
    if [ "$SCOPE" = '--local' ]; then
        set_git_config_value 'core.filemode' 'false' "$SCOPE" '忽略 Unix 权限位'
        set_git_config_value 'core.symlinks' 'false' "$SCOPE" '不创建符号链接，避免权限问题'
    fi
elif [ "$OS" = 'macos' ] || [ "$OS" = 'linux' ]; then
    echo ""
    print_section "$OS 平台特定配置"
    set_git_config_value 'core.autocrlf' 'input' "$SCOPE" '提交转 LF，检出不转换'
    if [ "$SCOPE" = '--local' ]; then
        bare=$(git rev-parse --is-bare-repository 2>/dev/null) || bare='false'
        if [ "$bare" = 'true' ]; then
            print_msg '检测到裸仓库，使用跨平台兼容设置' "$COLOR_INFO" 'INFO'
            set_git_config_value 'core.filemode' 'false' "$SCOPE" '裸仓库跨平台兼容：忽略权限位'
            set_git_config_value 'core.symlinks' 'false' "$SCOPE" '裸仓库跨平台兼容：不使用 symlink'
        else
            set_git_config_value 'core.filemode' 'true' "$SCOPE" '跟踪 Unix 文件权限位'
            set_git_config_value 'core.symlinks' 'true' "$SCOPE" '支持符号链接'
        fi
    fi
else
    print_msg '无法识别操作系统，跳过平台特定配置' "$COLOR_WARNING" 'WARN'
fi

if [ "$SCOPE" = '--local' ]; then
    echo ""
    print_section '非裸中央仓库可选配置'
    bare=$(git rev-parse --is-bare-repository 2>/dev/null) || bare='false'
    if [ "$bare" = 'false' ]; then
        receive_value=$(get_git_config 'receive.denyCurrentBranch' "$SCOPE")
        if [ -z "$receive_value" ]; then
            print_msg '提示: 非裸仓库可设置 receive.denyCurrentBranch=updateInstead 允许直接推送' "$COLOR_INFO" 'TIP'
            print_msg '执行: git config --local receive.denyCurrentBranch updateInstead' "$COLOR_INFO"
        fi
    fi
fi

echo ""
print_section '配置验证'
print_msg "执行 git config ${SCOPE} --list ..." "$COLOR_INFO"
echo ""

git config "$SCOPE" --list

echo ""
print_msg '=== 配置完成 ===' "$COLOR_HEADER"
print_msg "变更项: ${CHANGED_COUNT} 个" "$COLOR_CHANGED"
print_msg "已存在: ${OK_COUNT} 个" "$COLOR_EXISTS"

if [ "$SCOPE" = '--global' ]; then
    echo ""
    print_msg '提示: 对网盘同步仓库，建议进入仓库目录后用 --local 再执行一次：' "$COLOR_WARNING" 'TIP'
    print_msg "  bash $0 --local" "$COLOR_INFO"
fi
