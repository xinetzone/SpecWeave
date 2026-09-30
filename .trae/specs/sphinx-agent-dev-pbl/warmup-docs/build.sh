#!/usr/bin/env bash
# ===================================================================
#  一键构建脚本（macOS / Linux / Git Bash）
#  用法：bash build.sh
#
#  设计说明：本脚本会自动寻找可用的 Python，并验证它能 import sphinx。
#  如果预置的 .venv 失效（跨机器复制时常见），会自动回退到系统 Python。
# ===================================================================

set -u

echo ""
echo "  正在把你的文档变成网页..."
echo ""

# --- 候选 Python 列表（按优先级） ---
CANDIDATES=()

# 1. 预置虚拟环境（教师准备时创建）
[ -x ".venv/bin/python" ] && CANDIDATES+=(".venv/bin/python")
[ -x ".venv/Scripts/python.exe" ] && CANDIDATES+=(".venv/Scripts/python.exe")

# 2. 系统 Python
CANDIDATES+=("python3" "python")

# --- 逐个验证：必须能 import sphinx 才算可用 ---
PY=""
for cand in "${CANDIDATES[@]}"; do
    if "$cand" -c "import sphinx" >/dev/null 2>&1; then
        PY="$cand"
        break
    fi
done

if [ -z "$PY" ]; then
    echo "  ✗ 找不到可用的 Python（或没装 sphinx）"
    echo ""
    echo "  请把这句话告诉老师："
    echo "    warmup-docs 环境的 sphinx 不可用，需要重新准备环境"
    echo ""
    echo "  临时替代方案（不需要 Python）："
    echo "    把你 index.md 的内容粘贴到任意在线 Markdown 预览器，"
    echo "    也能看到渲染效果。"
    echo ""
    exit 1
fi

echo "  [使用] $PY"
echo ""
"$PY" -m sphinx -b html docs docs/_build/html

if [ $? -ne 0 ]; then
    echo ""
    echo "  ============================================"
    echo "  ✗ 构建失败了。请把上面的报错拍照给老师。"
    echo "  ============================================"
    exit 1
fi

echo ""
echo "  ============================================"
echo "  ✓ 成功！现在打开这个文件看看效果："
echo ""
echo "    docs/_build/html/index.html"
echo "  ============================================"
echo ""
echo "  提示：可以直接复制下面这行命令自动打开（macOS）"
echo "    open docs/_build/html/index.html"
echo ""
