# ==============================================================================
# common.sh — relpack 共享片段：应用根/产品目录解析、product.env 加载与必需键
#             校验、Windows→WSL 路径换算、podman 可用性检查。
#
# 由 bin/relpack source；依赖 lib/log.sh 的 die/warn，且约定 APP_ROOT 由入口
# 脚本按自身位置设定（未设定时按本文件位置回推：bin/lib/ → ../..）。
# 产品常量一律来自 products/<产品名>/product.env，本文件不内嵌任何产品值。
# ==============================================================================

# 应用根目录（bin/lib/common.sh → ../.. = offline-delivery/）
app_root() {
    if [ -n "${APP_ROOT:-}" ]; then printf '%s' "$APP_ROOT"; return 0; fi
    (cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
}

# 产品目录：<应用根>/products/<产品名>
product_dir() { printf '%s/products/%s' "$(app_root)" "$1"; }

# 相对应用根的路径 → 绝对路径（目录不存在时按字面拼接，不报错）
abs_under_root() {
    local p
    p="$(app_root)/$1"
    if [ -d "$p" ]; then (cd "$p" && pwd); else printf '%s' "$p"; fi
}

# 加载 product.env 并校验必需键齐备（值不加引号、不写空格）
load_product_env() {  # $1 = 产品名
    local name="$1" dir key
    dir="$(product_dir "$name")"
    if [ ! -f "$dir/product.env" ]; then
        die "未找到产品参数文件：$dir/product.env
  可用产品：$(ls "$(app_root)/products" 2>/dev/null | tr '\n' ' ')
  指定方式：bin/relpack -p <产品名> <命令>"
    fi
    # shellcheck disable=SC1090  # 路径来自产品名，非固定文件
    . "$dir/product.env"
    for key in PRODUCT IMAGE_NAME CONTAINERFILE WHEEL_GLOB WHEEL_PREFIX \
               WHEEL_DIST BASE_IMAGE_DEFAULT TORCH_DEFAULT RELEASE_DIR; do
        if [ -z "${!key:-}" ]; then
            die "product.env 缺少必需键 $key：$dir/product.env"
        fi
    done
    if [ "$PRODUCT" != "$name" ]; then
        die "product.env 的 PRODUCT=$PRODUCT 与目录名 $name 不一致：$dir/product.env"
    fi
}

# Windows 绝对路径 → WSL drvfs 路径：D:\x → /mnt/d/x（已是 POSIX 路径时原样返回）
win_to_wsl_path() {
    local p="$1" drive rest
    case "$p" in
        [A-Za-z]:[\\/]*)
            drive="$(printf '%s' "${p:0:1}" | tr '[:upper:]' '[:lower:]')"
            rest="$(printf '%s' "${p:2}" | tr '\\\\' '/')"
            printf '/mnt/%s%s' "$drive" "$rest" ;;
        *) printf '%s' "$p" ;;
    esac
}

# rootless podman 需要 XDG_RUNTIME_DIR（缺它会拒绝启动/打挂）；经 wsl.exe 以非登录
# shell 调用时该变量常未设，故仅在其未设或为空时按 id -u 兜底，绝不覆盖已有值。
ensure_xdg_runtime_dir() {
    [ -n "${XDG_RUNTIME_DIR:-}" ] && return 0
    local uid dir
    uid="$(id -u)"
    dir="/run/user/$uid"
    export XDG_RUNTIME_DIR="$dir"
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir" 2>/dev/null \
            || warn "无法创建 $XDG_RUNTIME_DIR（rootless podman 可能启动失败，请确认 /run/user 已挂载）"
    fi
}

# podman 可用性检查（容器命令只在 Linux / WSL 内执行）
require_podman() {
    command -v podman >/dev/null 2>&1 || die "未找到 podman：容器命令须在 Linux / WSL 发行版内执行
  1) 启动 Podman Machine：podman machine start（自检：podman info）
  2) Windows 原生请改用 pwsh bin/relpack.ps1（自动经 wsl.exe 桥接到本脚本）
  3) 指定 WSL 发行版：环境变量 OFFLINE_DELIVERY_WSL_DISTRO=<发行版>（wsl -l -v 查看）"
    ensure_xdg_runtime_dir
}