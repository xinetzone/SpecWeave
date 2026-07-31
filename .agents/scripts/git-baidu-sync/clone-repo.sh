#!/usr/bin/env bash
set -euo pipefail

REPO_NAME=''
SYNC_ROOT=''
TARGET_PATH=''
REMOTE_NAME='baidu'
RENAME_ORIGIN=0
FORCE=0

COLOR_SUCCESS='\033[0;32m'
COLOR_STEP='\033[0;36m'
COLOR_WARNING='\033[0;33m'
COLOR_ERROR='\033[0;31m'
COLOR_INFO='\033[0;37m'
COLOR_HEADER='\033[0;35m'
COLOR_EXISTS='\033[0;36m'
COLOR_RESET='\033[0m'

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

print_step() {
    local num="$1"
    local title="$2"
    echo ""
    print_msg "=== 步骤 ${num}: ${title} ===" "$COLOR_HEADER"
}

show_help() {
    echo "用法: $0 [选项] -RepoName <仓库名> -SyncRoot <网盘同步根路径>"
    echo ""
    echo "选项:"
    echo "  -RepoName <名称>      仓库名称（必需）"
    echo "  -SyncRoot <路径>      网盘同步根目录（必需）"
    echo "  -TargetPath <路径>    本地目标路径（默认当前目录/<repo-name>）"
    echo "  -RemoteName <名称>    Remote 名称（默认 baidu）"
    echo "  -RenameOriginToBaidu  将 origin 重命名为 baidu"
    echo "  -Force                强制覆盖已存在的目录"
    echo "  -h, --help            显示此帮助"
    echo ""
    echo "示例:"
    echo "  $0 -RepoName my-project -SyncRoot ~/BaiduSync/git-sync"
    echo "  $0 -RepoName my-project -SyncRoot ~/BaiduSync/git-sync -TargetPath ~/projects/myapp -RenameOriginToBaidu"
}

while [ $# -gt 0 ]; do
    case "$1" in
        -RepoName)
            if [ $# -lt 2 ]; then echo "错误: -RepoName 需要参数" >&2; exit 1; fi
            REPO_NAME="$2"; shift 2 ;;
        -RepoName=*)
            REPO_NAME="${1#-RepoName=}"; shift ;;
        -SyncRoot)
            if [ $# -lt 2 ]; then echo "错误: -SyncRoot 需要参数" >&2; exit 1; fi
            SYNC_ROOT="$2"; shift 2 ;;
        -SyncRoot=*)
            SYNC_ROOT="${1#-SyncRoot=}"; shift ;;
        -TargetPath)
            if [ $# -lt 2 ]; then echo "错误: -TargetPath 需要参数" >&2; exit 1; fi
            TARGET_PATH="$2"; shift 2 ;;
        -TargetPath=*)
            TARGET_PATH="${1#-TargetPath=}"; shift ;;
        -RemoteName)
            if [ $# -lt 2 ]; then echo "错误: -RemoteName 需要参数" >&2; exit 1; fi
            REMOTE_NAME="$2"; shift 2 ;;
        -RemoteName=*)
            REMOTE_NAME="${1#-RemoteName=}"; shift ;;
        -RenameOriginToBaidu|--rename-origin)
            RENAME_ORIGIN=1; shift ;;
        -Force|--force)
            FORCE=1; shift ;;
        -h|--help)
            show_help; exit 0 ;;
        *)
            echo "未知参数: $1" >&2; show_help; exit 1 ;;
    esac
done

if [ -z "$REPO_NAME" ] || [ -z "$SYNC_ROOT" ]; then
    echo "错误: 必须指定 -RepoName 和 -SyncRoot 参数" >&2
    show_help
    exit 1
fi

resolve_path() {
    local p="$1"
    if [ -d "$p" ]; then
        (cd "$p" && pwd)
    elif [ -d "$(dirname "$p")" ]; then
        echo "$(cd "$(dirname "$p")" && pwd)/$(basename "$p")"
    else
        echo "$p"
    fi
}

detect_os() {
    case "$(uname -s)" in
        Darwin) echo 'macos' ;;
        Linux) echo 'linux' ;;
        MINGW*|MSYS*|CYGWIN*) echo 'windows' ;;
        *) echo 'unknown' ;;
    esac
}

get_device_id() {
    local os
    os=$(detect_os)
    local os_short
    case "$os" in
        macos) os_short='mac' ;;
        linux) os_short='linux' ;;
        windows) os_short='win' ;;
        *) os_short='unknown' ;;
    esac

    local hn
    hn=$(hostname 2>/dev/null || echo 'device')
    local hn_clean
    hn_clean=$(echo "$hn" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')
    echo "${os_short}-${hn_clean}"
}

SYNC_ROOT=$(resolve_path "$SYNC_ROOT")
BARE_REPO="${SYNC_ROOT}/repos/${REPO_NAME}.git"
DEVICES_JSON="${SYNC_ROOT}/meta/devices.json"

if [ -z "$TARGET_PATH" ]; then
    TARGET_PATH="$(pwd)/${REPO_NAME}"
fi
TARGET_PATH=$(resolve_path "$TARGET_PATH")

echo ""
print_msg '=========================================' "$COLOR_HEADER"
print_msg '  百度网盘 Git 仓库克隆工具（新设备）' "$COLOR_HEADER"
print_msg '=========================================' "$COLOR_HEADER"
echo ""
print_msg "仓库名称: $REPO_NAME" "$COLOR_INFO"
print_msg "网盘同步根目录: $SYNC_ROOT" "$COLOR_INFO"
print_msg "裸仓库路径: $BARE_REPO" "$COLOR_INFO"
print_msg "本地目标路径: $TARGET_PATH" "$COLOR_INFO"
echo ""

print_step 0 '前置检查'

if [ ! -d "${SYNC_ROOT}/repos" ]; then
    print_msg "同步目录不存在或未初始化: $SYNC_ROOT" "$COLOR_ERROR" 'ERR'
    print_msg '请先执行 init-sync-dir.sh 初始化同步目录，并等待网盘完成首次全量同步' "$COLOR_WARNING" 'HINT'
    exit 1
fi
print_msg '同步目录验证通过' "$COLOR_SUCCESS" 'OK'

if [ ! -d "$BARE_REPO" ]; then
    print_msg "裸仓库不存在: $BARE_REPO" "$COLOR_ERROR" 'ERR'
    print_msg '请确认：' "$COLOR_WARNING" 'HINT'
    print_msg '  1. 网盘已完成首次全量同步' "$COLOR_WARNING"
    print_msg '  2. RepoName 参数正确' "$COLOR_WARNING"
    print_msg "  3. repos/ 目录下能看到 $REPO_NAME.git 文件夹" "$COLOR_WARNING"
    exit 1
fi
print_msg '裸仓库目录存在' "$COLOR_SUCCESS" 'OK'

if ! git --version >/dev/null 2>&1; then
    print_msg '未检测到 Git，请先安装 Git' "$COLOR_ERROR" 'ERR'
    exit 1
fi
print_msg "Git 版本: $(git --version)" "$COLOR_INFO" 'OK'

if [ -d "$TARGET_PATH" ] && [ "$FORCE" -eq 0 ]; then
    if [ "$(ls -A "$TARGET_PATH" 2>/dev/null | wc -l)" -gt 0 ]; then
        print_msg "目标路径已存在且非空: $TARGET_PATH" "$COLOR_WARNING" 'WARN'
        read -r -p '是否继续？可能覆盖文件 (y/N) ' ans
        if [ "$ans" != 'y' ] && [ "$ans" != 'Y' ]; then
            print_msg '用户取消操作' "$COLOR_WARNING" 'ABORT'
            exit 0
        fi
    fi
fi

print_step 1 '检测临时文件（确认网盘同步完成）'

temp_files=()
while IFS= read -r -d '' f; do
    temp_files+=("$f")
done < <(find "$BARE_REPO" -type f \( -name '*.tmp' -o -name '*.lock' -o -name '*downloading*' -o -name '*.part' -o -name '*.temp' -o -name '*.crdownload' -o -name '*.!ut' \) -print0 2>/dev/null)

if [ "${#temp_files[@]}" -gt 0 ]; then
    print_msg "检测到 ${#temp_files[@]} 个临时文件（网盘可能还在同步）：" "$COLOR_WARNING" 'WARN'
    for f in "${temp_files[@]:0:10}"; do
        echo "  - $(basename "$f")"
    done
    echo ""
    print_msg '临时文件可能意味着网盘尚未完成同步，克隆可能导致仓库损坏！' "$COLOR_ERROR" 'DANGER'

    if [ "$FORCE" -eq 1 ]; then
        print_msg '-Force 已指定，继续执行（不推荐）' "$COLOR_WARNING" 'WARN'
    else
        read -r -p '是否继续？强烈建议等待同步完成 (y/N) ' ans
        if [ "$ans" != 'y' ] && [ "$ans" != 'Y' ]; then
            print_msg '用户取消操作，请等待网盘同步完成后重试' "$COLOR_WARNING" 'ABORT'
            exit 0
        fi
    fi
else
    print_msg '未检测到临时文件，同步可能已完成' "$COLOR_SUCCESS" 'OK'
fi

PACK_DIR="${BARE_REPO}/objects/pack"
if [ ! -d "$PACK_DIR" ]; then
    print_msg "pack 目录不存在: $PACK_DIR" "$COLOR_ERROR" 'ERR'
    print_msg '裸仓库可能不完整，请等待网盘同步完成' "$COLOR_WARNING" 'HINT'
    exit 1
fi

pack_count=$(find "$PACK_DIR" -maxdepth 1 -name '*.pack' -type f 2>/dev/null | wc -l)
if [ "$pack_count" -eq 0 ]; then
    print_msg '未找到 pack 文件，裸仓库可能不完整' "$COLOR_ERROR" 'ERR'
    exit 1
fi

while IFS= read -r pf; do
    if [ ! -s "$pf" ]; then
        print_msg "pack 文件大小为 0: $pf" "$COLOR_ERROR" 'ERR'
        exit 1
    fi
done < <(find "$PACK_DIR" -maxdepth 1 -name '*.pack' -type f 2>/dev/null)

print_msg "找到 $pack_count 个 pack 文件" "$COLOR_SUCCESS" 'OK'

print_step 2 '裸仓库健康检查 (git fsck --full)'

print_msg '执行 fsck，请稍候...' "$COLOR_INFO"
fsck_output=$(git -C "$BARE_REPO" fsck --full 2>&1) || {
    print_msg '裸仓库健康检查失败！可能是网盘同步未完成或仓库损坏。' "$COLOR_ERROR" 'ERR'
    echo "$fsck_output"
    print_msg '建议：等待网盘继续同步后重试，或检查首台设备是否正确注册。' "$COLOR_WARNING" 'HINT'
    exit 1
}

has_fsck_errors=0
while IFS= read -r line; do
    if echo "$line" | grep -qE '^error:|^fatal:|missing blob|missing tree|missing commit'; then
        has_fsck_errors=1
        echo -e "${COLOR_ERROR}${line}${COLOR_RESET}"
    fi
done <<< "$fsck_output"

if [ "$has_fsck_errors" -eq 1 ]; then
    print_msg '裸仓库健康检查发现错误，终止克隆' "$COLOR_ERROR" 'ERR'
    exit 1
fi
print_msg '裸仓库健康检查通过' "$COLOR_SUCCESS" 'OK'

print_step 3 '克隆仓库到本地'

if [ -d "$TARGET_PATH" ] && [ "$(ls -A "$TARGET_PATH" 2>/dev/null | wc -l)" -gt 0 ]; then
    if [ "$FORCE" -eq 1 ]; then
        print_msg "目标目录非空，-Force 已指定，删除后重新克隆: $TARGET_PATH" "$COLOR_WARNING" 'WARN'
        rm -rf "$TARGET_PATH"
    fi
fi

print_msg "克隆 $BARE_REPO -> $TARGET_PATH" "$COLOR_INFO"
if clone_output=$(git clone "$BARE_REPO" "$TARGET_PATH" 2>&1); then
    echo "$clone_output" | while IFS= read -r line; do echo -e "${COLOR_INFO}${line}${COLOR_RESET}"; done
    print_msg '克隆完成' "$COLOR_SUCCESS" 'OK'
else
    print_msg '克隆失败：' "$COLOR_ERROR" 'ERR'
    echo "$clone_output"
    exit 1
fi

print_step 4 '验证克隆结果'

is_work_tree=$(git -C "$TARGET_PATH" rev-parse --is-inside-work-tree 2>/dev/null || echo 'false')
if [ "$is_work_tree" != 'true' ]; then
    print_msg '错误：克隆结果不是有效的工作仓库' "$COLOR_ERROR" 'ERR'
    exit 1
fi
print_msg '工作仓库验证通过' "$COLOR_SUCCESS" 'OK'

if [ "$RENAME_ORIGIN" -eq 1 ]; then
    if git -C "$TARGET_PATH" remote | grep -q '^origin$' 2>/dev/null; then
        if ! git -C "$TARGET_PATH" remote | grep -q "^${REMOTE_NAME}$" 2>/dev/null; then
            git -C "$TARGET_PATH" remote rename origin "$REMOTE_NAME" 2>/dev/null
            print_msg "已将 remote 'origin' 重命名为 '$REMOTE_NAME'" "$COLOR_SUCCESS" 'RENAME'
        fi
    fi
fi

echo ""
print_msg '=== 克隆摘要 ===' "$COLOR_HEADER"

print_msg '最新提交：' "$COLOR_INFO"
git -C "$TARGET_PATH" log --oneline -5 2>/dev/null | while IFS= read -r line; do
    echo "  $line"
done

branch_count=$(git -C "$TARGET_PATH" branch -a 2>/dev/null | wc -l)
print_msg "分支数量: $branch_count" "$COLOR_INFO"

tag_count=$(git -C "$TARGET_PATH" tag 2>/dev/null | wc -l)
print_msg "标签数量: $tag_count" "$COLOR_INFO"

echo ""
print_msg 'Remote 配置：' "$COLOR_INFO"
git -C "$TARGET_PATH" remote -v 2>/dev/null | while IFS= read -r line; do echo "  $line"; done

status_output=$(git -C "$TARGET_PATH" status --short 2>/dev/null)
if [ -n "$status_output" ]; then
    echo ""
    print_msg '注意：工作区有未提交变更（可能是换行符差异）：' "$COLOR_WARNING" 'WARN'
    echo "$status_output" | head -10 | while IFS= read -r line; do echo "  $line"; done
else
    print_msg '工作区状态：干净' "$COLOR_SUCCESS" 'OK'
fi

print_step 5 '配置本地跨平台设置'

os=$(detect_os)

if [ "$os" = 'windows' ]; then
    git -C "$TARGET_PATH" config --local core.autocrlf true 2>/dev/null || true
    git -C "$TARGET_PATH" config --local core.fscache true 2>/dev/null || true
    git -C "$TARGET_PATH" config --local core.longpaths true 2>/dev/null || true
else
    git -C "$TARGET_PATH" config --local core.autocrlf input 2>/dev/null || true
fi

git -C "$TARGET_PATH" config --local core.preloadindex true 2>/dev/null || true
git -C "$TARGET_PATH" config --local gc.auto 6700 2>/dev/null || true
git -C "$TARGET_PATH" config --local gc.autopacklimit 1 2>/dev/null || true

print_msg '本地跨平台配置已设置' "$COLOR_SUCCESS" 'OK'

gitattributes_path="${TARGET_PATH}/.gitattributes"
if [ ! -f "$gitattributes_path" ]; then
    print_msg '仓库中未找到 .gitattributes' "$COLOR_INFO" 'INFO'
    print_msg '建议运行 setup-git-config.sh --attributes 生成跨平台换行符配置' "$COLOR_WARNING" 'HINT'
else
    print_msg '.gitattributes 已存在' "$COLOR_SUCCESS" 'OK'
fi

print_step 6 '注册设备到 meta/devices.json'

device_id=$(get_device_id)
read -r -p "请输入设备可读名称（如：工作笔记本）: " device_name
if [ -z "$device_name" ]; then
    device_name="$device_id"
fi

device_os="$os"
hostname_val=$(hostname 2>/dev/null || echo 'unknown')

now=$(date +%Y-%m-%dT%H:%M:%S%z)
now="${now:0:22}:${now:22}"

devices_dir=$(dirname "$DEVICES_JSON")
mkdir -p "$devices_dir"

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    PYTHON=''
fi

if [ -n "$PYTHON" ]; then
    "$PYTHON" << PYEOF
import json
import os
import sys

devices_json = "$DEVICES_JSON"
device_id = "$device_id"
device_name = "$device_name"
device_os = "$device_os"
hostname = "$hostname_val"
now = "$now"
sync_root = "$SYNC_ROOT"

data = {"devices": []}
if os.path.exists(devices_json):
    try:
        with open(devices_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if 'devices' not in data or not isinstance(data['devices'], list):
            data['devices'] = []
    except Exception:
        data = {"devices": []}

found = False
for dev in data['devices']:
    if dev.get('id') == device_id:
        dev['last_seen'] = now
        dev['sync_root'] = sync_root
        found = True
        break

if not found:
    data['devices'].append({
        "id": device_id,
        "name": device_name,
        "os": device_os,
        "hostname": hostname,
        "registered_at": now,
        "last_seen": now,
        "sync_root": sync_root
    })

os.makedirs(os.path.dirname(devices_json), exist_ok=True)
with open(devices_json, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'OK: {device_id}')
PYEOF
    if [ $? -eq 0 ]; then
        print_msg "设备信息已写入: $DEVICES_JSON" "$COLOR_SUCCESS" 'OK'
    else
        print_msg 'JSON 写入失败，请手动编辑 devices.json' "$COLOR_ERROR" 'ERR'
    fi
else
    print_msg "未找到 Python，跳过自动注册，请手动添加设备信息到: $DEVICES_JSON" "$COLOR_WARNING" 'WARN'
    cat <<EOF
建议添加：
{
  "id": "$device_id",
  "name": "$device_name",
  "os": "$device_os",
  "hostname": "$hostname_val",
  "registered_at": "$now",
  "last_seen": "$now",
  "sync_root": "$SYNC_ROOT"
}
EOF
fi

if [ -f "$DEVICES_JSON" ]; then
    existing=$(grep "\"id\": \"$device_id\"" "$DEVICES_JSON" 2>/dev/null || true)
    if [ -n "$existing" ]; then
        print_msg "设备已注册/更新: $device_id" "$COLOR_SUCCESS" 'OK'
    fi
fi

echo ""
print_msg '=========================================' "$COLOR_SUCCESS"
print_msg '  仓库克隆完成！' "$COLOR_SUCCESS"
print_msg '=========================================' "$COLOR_SUCCESS"
echo ""
print_msg "仓库名: $REPO_NAME" "$COLOR_SUCCESS"
print_msg "本地路径: $TARGET_PATH" "$COLOR_SUCCESS"
print_msg "设备 ID: $device_id" "$COLOR_SUCCESS"
echo ""
print_msg '后续步骤：' "$COLOR_HEADER"
print_msg "1. cd $TARGET_PATH" "$COLOR_INFO"
print_msg "2. 检查 git status 是否干净" "$COLOR_INFO"
print_msg '3. 如有 .gitattributes 变更，执行 git add --renormalize .' "$COLOR_INFO"
print_msg "4. 日常推送: git push ${REMOTE_NAME}" "$COLOR_INFO"
echo ""
