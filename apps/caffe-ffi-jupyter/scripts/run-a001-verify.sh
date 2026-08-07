#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# A-001 修复运行级验证启动脚本（在 caffe-ffi-jupyter 容器内执行）
#
# 作用：
#   1. 激活 conda 环境 caffe-ffi（Python 3.14）
#   2. 按需重编译 native 扩展（editable-install.sh，含 tvm-ffi + caffe-ffi，
#      覆盖 A-001 修复的 net.cpp）—— 重编译是运行级验证的前提
#   3. 运行 a001_verify_fix.py，默认使用 hub/caffe/resnet50_caffe 测试网络
#
# 用法（容器内）：
#   bash run-a001-verify.sh                 # 重编译 + 验证（默认）
#   REBUILD=0 bash run-a001-verify.sh       # 跳过重编译，仅验证（.so 已含修复）
#   bash run-a001-verify.sh --layer-name conv1
#
# 说明：本脚本应放在容器挂载的 /SpecWeave 下，路径为
#   /SpecWeave/apps/caffe-ffi-jupyter/scripts/run-a001-verify.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

VERIFY_SCRIPT="/SpecWeave/.trae/specs/caffe-ffi-followup-fixes-analysis/a001_verify_fix.py"
MODEL_DIR="/SpecWeave/external/chaos/xmtools/models/hub/caffe/resnet50_caffe"

echo "=========================================================="
echo "[a001] A-001 修复运行级验证"
echo "=========================================================="

# ── 1. 激活 conda 环境 ──
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export KMP_DUPLICATE_LIB_OK=TRUE
echo "[a001] Python: $(python --version)"
echo "[a001] conda env: $CONDA_DEFAULT_ENV"

# ── 2. 前置校验：验证脚本与测试模型存在 ──
for f in "$VERIFY_SCRIPT" "$MODEL_DIR/ResNet-50-deploy.prototxt" "$MODEL_DIR/ResNet-50-model.caffemodel"; do
    if [ ! -f "$f" ]; then
        echo "[a001] FATAL: 文件不存在: $f" >&2
        exit 2
    fi
done

# ── 3. 按需重编译 native 扩展 ──
if [ "${REBUILD:-1}" = "1" ]; then
    echo "[a001] 重编译 native 扩展（editable-install.sh）..."
    if [ -x /usr/local/bin/editable-install.sh ]; then
        # editable-install.sh 末尾 exec "$@"，传 true 使其重编译后正常返回
        /usr/local/bin/editable-install.sh true
    else
        # 回退：直接对 caffe-ffi 源码做 editable 安装
        cd /SpecWeave/projects/xuanspace/libs/caffe-ffi
        pip install --no-build-isolation --no-cache-dir -e .
    fi
else
    echo "[a001] 跳过重编译（REBUILD=0，使用已安装的 native 扩展）"
fi

# ── 4. 运行验证脚本 ──
echo "[a001] 运行 a001_verify_fix.py ..."
python "$VERIFY_SCRIPT" --proto "$MODEL_DIR/ResNet-50-deploy.prototxt" \
    --caffemodel "$MODEL_DIR/ResNet-50-model.caffemodel" "$@"
rc=$?

echo "=========================================================="
if [ $rc -eq 0 ]; then
    echo "[a001] 验证通过（ALL PASS）"
else
    echo "[a001] 验证未通过（exit=$rc）"
fi
echo "=========================================================="
exit $rc