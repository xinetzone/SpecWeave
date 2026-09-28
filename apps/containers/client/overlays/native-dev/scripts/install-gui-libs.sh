#!/bin/bash
# ==============================================================================
# install-gui-libs.sh — base env 恢复 Tk/tcl 运行时 + X11 客户端库（构建期执行一次）
#
# 背景（2026-09-25 实证）：
#   - 基底 jupyter-podman-rootless 的深度清理**删除**了 base env 的 tk/tcl 文件
#     （libtk8.6.so / libtcl8.6.so / lib/tk8.6 / lib/tcl8.6 / bin/tclsh / bin/wish），
#     却**保留**了 _tkinter.cpython-314-*.so 与 conda-meta 的 tk-8.6.13 记录——
#     形成「记录说已装、文件已不在」的腐坏态：`import tkinter` 在 dlopen
#     libtk8.6.so 处报 ImportError，且常规 `mamba install tk` 被判「已安装」空转。
#   - 运行期 GUI 透传（`up --gui`，compose.passthrough.gui*.yaml）已提供
#     Wayland/X11 socket，但镜像内零 X11 客户端库，libtk8.6.so 的 NEEDED
#     libX11.so.6 无处解析——本脚本一并补齐（显示通道仍由运行期提供）。
#
# 关键决策（勿随意改，均有实测依据）：
#   ① 先 `rm conda-meta/tk-*.json` 丢弃腐坏记录，再**精确版本**安装：
#      conda-forge 现行 latest 是 tk 9.0.x（soname libtk9.0.so），与 base env 中
#      按 8.6 编译的 _tkinter 不兼容（实测会把 libtk8.6.so 换成 libtk9.0.so）；
#      而 `--force-reinstall` 因基底 `conda clean -a` 擦除 pkgs 缓存而失败
#      （实测 libmamba: Cannot find a valid extracted directory cache）。
#   ② 目标 env 仅 base（/opt/conda）：native-dev 内核与 SSH 会话的 python 都在
#      base env；main env 是 Jupyter 服务/LLVM 工具链 env，不引入以免扰动求解。
#   ③ libtk8.6.so 的 NEEDED 实测仅 libX11.so.6 + libm + libc（无 libXss/libXext），
#      故只显式装 xorg-libx11（libxcb/xau/xdmcp 由依赖自动带出）。
#   ④ 版本漂移防线：本脚本自检 import/Tcl patchlevel，完整断言见
#      smoke/_toolchain_guards.py §10（root 与 devuser 双身份复跑）。
#
# 调用：Containerfile.native-dev Layer 4.5（CONDA_MIRROR 经 RUN env 传入）。
# ==============================================================================
set -euo pipefail

CONDA_PREFIX_DIR=/opt/conda
PYTHON="${CONDA_PREFIX_DIR}/bin/python"
MAMBA="${CONDA_PREFIX_DIR}/bin/mamba"

case "${CONDA_MIRROR:-official}" in
    tuna)   CH="https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/" ;;
    aliyun) CH="https://mirrors.aliyun.com/anaconda/cloud/conda-forge/" ;;
    *)      CH="conda-forge" ;;
esac
echo "[gui] conda channel: ${CH}"

# ── ① 丢弃腐坏记录（基底 rm 文件但留记录的反向修复；依据见头注①）────────────
rm -f "${CONDA_PREFIX_DIR}/conda-meta/tk-"*.json
echo "[gui] dropped stale tk conda-meta record"

# ── ② 精确版本恢复：tk=8.6.13（tcl/tk 8.6 一体包）+ X11 客户端库 ──────────────
"${MAMBA}" install -y -n base --override-channels -c "${CH}" \
    "tk=8.6.13" xorg-libx11
"${MAMBA}" clean -afy

# ── ③ 构建期轻量自检（完整守卫在 _toolchain_guards.py §10）────────────────────
for rel in lib/libtk8.6.so lib/libtcl8.6.so lib/libX11.so.6 lib/tk8.6 lib/tcl8.6; do
    if [ ! -e "${CONDA_PREFIX_DIR}/${rel}" ]; then
        echo "[gui] ERROR: missing ${rel} after install" >&2
        exit 1
    fi
done
"${PYTHON}" - <<'PY'
import tkinter as tk

print(f"[gui] import tkinter OK, TkVersion={tk.TkVersion}")
print(f"[gui] Tcl patchlevel={tk.Tcl().eval('info patchlevel')}")
PY
echo "[gui] Tk 8.6 runtime + X11 client libs restored (display comes from 'up --gui')"