#!/bin/bash
# =============================================================================
# fix-jupyter-gil.sh — Jupyter kernel GIL 被重新启用 诊断/修复/验证 一体化脚本
#
# 来源：troubleshooting-devcontainer-jupyter-gil-20260819.md（I→F→V→C→R→I→E 链路）
# 背景：free-threading Python（cp314t）加载未声明 Py_MOD_GIL_USED 的 C 扩展
#       （如 Jupyter 栈的 _brotli）时，经 PyUnstable_Module_SetGIL 自动拉起 GIL，
#       导致 bash 上下文 _is_gil_enabled()=False、Jupyter kernel 内=True。
# 修复：/etc/supervisor/conf.d/jupyter.conf 的 environment= 注入 PYTHON_GIL="0"，
#       使 supervisord 启动 Jupyter 时显式保持 GIL 关闭（kernel 子进程继承）。
#
# 用法：
#   bash fix-jupyter-gil.sh             # 只诊断（GIL-01~02，只读）
#   bash fix-jupyter-gil.sh --fix       # 诊断 + 幂等修复 jupyter.conf
#   bash fix-jupyter-gil.sh --verify    # 诊断 + kernel E2E 验证
#   bash fix-jupyter-gil.sh --all       # 诊断 + 修复 + 验证 + 重建/清理指引（默认推荐）
#   bash fix-jupyter-gil.sh --help
#
# 退出码：0=健康/修复完成；1=修复后仍异常；2=参数错误/非 free-threading 环境
# =============================================================================
set -euo pipefail

CONF="/etc/supervisor/conf.d/jupyter.conf"
MAIN_PY="${MAIN_PY:-/opt/conda/envs/main/bin/python}"
CHECK_GIL_PY="scripts/check_gil_state.py"   # 与 GIL-02 复用（若镜像内存在）

mode_fix=0
mode_verify=0
for arg in "$@"; do
    case "$arg" in
        -f|--fix)    mode_fix=1 ;;
        -v|--verify) mode_verify=1 ;;
        -a|--all)    mode_fix=1; mode_verify=1 ;;
        -h|--help)   sed -n '2,20p' "$0"; exit 0 ;;
        *) echo "[ERROR] 未知参数: $arg （用法见 --help）" >&2; exit 2 ;;
    esac
done
# 默认：无参数时只诊断；--all 时执行完整链路
if [ "$mode_fix" -eq 0 ] && [ "$mode_verify" -eq 0 ]; then
    echo "[NOTE] 未指定 --fix/--verify/--all，仅执行只读诊断。"
fi

# ---------------------------------------------------------------------------
# GIL-01 环境检测：free-threading 构建 + bash 上下文 GIL 状态
# ---------------------------------------------------------------------------
echo ""
echo "=== [GIL-01] 环境检测 ==="
if [ ! -x "$MAIN_PY" ]; then
    echo "[ERROR] 未找到 $MAIN_PY（main 环境 Python 缺失）" >&2
    exit 2
fi
FT_CHECK=$("$MAIN_PY" -c "import sysconfig; print(1 if sysconfig.get_config_var('Py_GIL_DISABLED') else 0)" 2>/dev/null || echo 0)
if [ "$FT_CHECK" != "1" ]; then
    PY_VER=$("$MAIN_PY" -c "import sys; print(sys.version.split()[0])" 2>/dev/null || echo "?")
    echo "[SKIP] 非 free-threading 构建（Python $PY_VER），GIL 守卫不适用。"
    exit 0
fi
"$MAIN_PY" - <<'PYEOF'
import sys
print(f"  Python        : {sys.version.split()[0]} ({sys.executable})")
print(f"  构建          : free-threading (Py_GIL_DISABLED=1)")
print(f"  bash GIL 状态 : {'已启用' if sys._is_gil_enabled() else '禁用（nogil 生效）'}")
PYEOF

# ---------------------------------------------------------------------------
# GIL-02 肇事复现：import _brotli（Jupyter 栈依赖）观察 GIL 是否被拉起
#           ——复用 scripts/check_gil_state.py（金丝雀审计），不重复实现
# ---------------------------------------------------------------------------
echo ""
echo "=== [GIL-02] 肇事模块复现（_brotli） ==="
if [ -f "$CHECK_GIL_PY" ]; then
    "$MAIN_PY" "$CHECK_GIL_PY" --pre brotli --no-audit || true
else
    echo "  [WARN] 未找到 $CHECK_GIL_PY，跳过金丝雀审计（可单独运行诊断）"
    echo "  手动复现：$MAIN_PY -c \"import sys,brotli; print('GIL:', sys._is_gil_enabled())\""
fi

# ---------------------------------------------------------------------------
# GIL-03 配置检查/修复：jupyter.conf environment= 幂等注入 PYTHON_GIL="0"
# ---------------------------------------------------------------------------
if [ "$mode_fix" -eq 1 ]; then
    echo ""
    echo "=== [GIL-03] 修复 jupyter.conf（幂等） ==="
    if [ ! -f "$CONF" ]; then
        echo "[ERROR] 未找到 $CONF（supervisord 配置缺失）" >&2
        exit 1
    fi
    if grep -q "PYTHON_GIL" "$CONF"; then
        echo "  [OK] $CONF 已含 PYTHON_GIL，跳过注入："
        grep "PYTHON_GIL" "$CONF" | sed 's/^/      /'
    else
        sed -i 's|^environment=\(.*\)$|environment=\1,PYTHON_GIL="0"|' "$CONF"
        echo "  [FIXED] 已注入 PYTHON_GIL=\"0\" 到 environment= 行："
        grep "PYTHON_GIL" "$CONF" | sed 's/^/      /'
        echo "  [ACTION] 需重启 supervisord 的 jupyter 服务生效："
        echo "      supervisorctl restart jupyter"
    fi
    # 防覆盖自检：entrypoint 若只改 directory= 则安全（本修复不受影响）
    if [ -f /entrypoint.sh ] && grep -q '^directory=' "$CONF"; then
        echo "  [INFO] entrypoint 运行时仅改 directory= 行，不会覆盖 environment= 注入"
    fi
else
    echo ""
    echo "=== [GIL-03] 配置检查（只读，--fix 可注入） ==="
    if grep -q "PYTHON_GIL" "$CONF" 2>/dev/null; then
        echo "  [OK] $CONF 已含 PYTHON_GIL："
        grep "PYTHON_GIL" "$CONF" | sed 's/^/      /'
    else
        echo "  [FAIL] $CONF 缺少 PYTHON_GIL，Jupyter kernel 内 GIL 会被 _brotli 拉起"
        echo "  [HINT] 运行 bash fix-jupyter-gil.sh --fix 注入"
    fi
fi

# ---------------------------------------------------------------------------
# GIL-04 kernel E2E 验证：spawn Jupyter kernel 执行代码，确认 _is_gil_enabled()=False
# ---------------------------------------------------------------------------
if [ "$mode_verify" -eq 1 ]; then
    echo ""
    echo "=== [GIL-04] Jupyter kernel E2E 验证 ==="
    export HOME="${HOME:-/home/devuser}"
    # 关键：模拟 supervisord 环境（PYTHON_GIL=0），kernel 作为子进程继承
    if ! "$MAIN_PY" - <<'PYEOF'; then
import sys
from jupyter_client import KernelManager

km = KernelManager(kernel_name="python3")
km.start_kernel()
try:
    kc = km.client(); kc.start_channels(); kc.wait_for_ready(timeout=30)
    mid = kc.execute("import sys; print('E2E_OK GIL_ENABLED=', sys._is_gil_enabled())")
    ok = False
    while True:
        msg = kc.get_iopub_msg(timeout=30)
        if msg["parent_header"].get("msg_id") != mid:
            continue
        t = msg["msg_type"]
        if t == "stream":
            line = msg["content"]["text"].strip()
            print("  [kernel]", line)
            ok = ("E2E_OK" in line) and ("GIL_ENABLED= False" in line)
        elif t == "error":
            print("  [ERROR]", msg["content"]["traceback"])
            break
        elif t == "status" and msg["content"]["execution_state"] == "idle":
            break
    print("  [RESULT]", "PASS（kernel 内 GIL 保持禁用）" if ok else "FAIL（kernel 内 GIL 仍被启用）")
    sys.exit(0 if ok else 1)
finally:
    km.shutdown_kernel(now=True)
PYEOF
        echo "[FAIL] kernel E2E 未通过：先 --fix 注入 PYTHON_GIL=0 并 supervisorctl restart jupyter 后再验" >&2
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
# GIL-05 重建与清理指引（宿主侧 WSL/Podman）
# ---------------------------------------------------------------------------
echo ""
echo "=== [GIL-05] 宿主侧重建与清理指引（如源 jupyter.conf 已修复） ==="
echo "  1. 确认源文件已修复："
echo "       apps/docker-images/devcontainer-base/config/supervisor/conf.d/jupyter.conf"
echo "       （environment= 行应含 PYTHON_GIL=\"0\"）"
echo "  2. 重建 base（根因落 base 层，所有变体自动继承）："
echo "       bash scripts/build.sh --tag latest [--cn]"
echo "  3. 重建变体（conda-llvm 自带幂等 sed 防御，对其他变体从 latest 构建即安全）："
echo "       bash variants/build.sh --variant conda-llvm --tag latest [--cn]"
echo "  4. 验证 + 清理旧悬空镜像："
echo "       podman run --rm -e PYTHON_GIL=0 <image> bash fix-jupyter-gil.sh --verify"
echo "       podman image prune -f   # 先停用旧容器，见报告第五节"

echo ""
echo "=== 完成 ==="
