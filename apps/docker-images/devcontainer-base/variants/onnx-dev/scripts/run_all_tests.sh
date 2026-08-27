#!/bin/bash
# onnx-dev 容器内测试脚本 - 一次性验证所有示例和工具
set -e

WORKSPACE_DIR="/workspace"
EXAMPLES_DIR="$WORKSPACE_DIR/examples"
TOOLS_DIR="$WORKSPACE_DIR/tools"
PYTHON="/opt/conda/envs/main/bin/python"

echo "============================================"
echo "Test 1: opset模式冒烟推理 (examples/inference_demo.py)"
echo "============================================"
$PYTHON $EXAMPLES_DIR/inference_demo.py

echo ""
echo "============================================"
echo "Test 2: 简单环境验证 (examples/simple_verify.py)"
echo "============================================"
$PYTHON $EXAMPLES_DIR/simple_verify.py

echo ""
echo "============================================"
echo "Test 3: free-threading包检查 (tools/ft_compat_check.py) - 人类可读"
echo "============================================"
$PYTHON $TOOLS_DIR/ft_compat_check.py

echo ""
echo "============================================"
echo "Test 4: free-threading包检查 (JSON输出)"
echo "============================================"
$PYTHON $TOOLS_DIR/ft_compat_check.py --json

echo ""
echo "============================================"
echo "Test 5: 验证已有ONNX模型推理（如果存在模型文件）"
echo "============================================"
if [ -d "$WORKSPACE_DIR/models" ] && ls $WORKSPACE_DIR/models/*.onnx 1>/dev/null 2>&1; then
    for model in $WORKSPACE_DIR/models/*.onnx; do
        echo "  测试模型: $model"
        $PYTHON -c "
import onnx
import onnxruntime as ort
import numpy as np
m = onnx.load('$model')
print(f'  模型ir_version={m.ir_version}, opset={[o.version for o in m.opset_import]}')
sess = ort.InferenceSession('$model', providers=['CPUExecutionProvider'])
for inp in sess.get_inputs():
    print(f'  输入: {inp.name}, shape={inp.shape}, type={inp.type}')
    fake_input = np.random.randn(*[1 if (d is None or (isinstance(d, str) and (d.isalpha() or 'batch' in d.lower()))) else d for d in inp.shape]).astype(np.float32)
    out = sess.run(None, {inp.name: fake_input})
    print(f'  输出数量: {len(out)}, 输出0形状: {out[0].shape}')
print('  ✅ 模型推理成功')
"
    done
else
    echo "  (未发现models目录或.onnx文件，跳过模型推理测试)"
    echo "  如需测试自己的模型，请创建 models/ 目录并放入.onnx文件，或使用 docker run -v 挂载模型路径"
fi

echo ""
echo "============================================"
echo "✅ All tests completed!"
echo "============================================"
