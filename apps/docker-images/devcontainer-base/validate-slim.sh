#!/bin/bash
set -e

echo "=========================================="
echo "=== DevContainer Slim Images Validation ==="
echo "=========================================="
echo ""

echo "=== All images ==="
docker images | grep -E "REPOSITORY|devcontainer-base"
echo ""

echo "=========================================="
echo "=== Test 1: conda-llvm-slim ==="
echo "=========================================="
docker run --rm devcontainer-base:conda-llvm-slim bash -c '
echo "Python version:"
python --version
echo ""
echo "Python free-threading check:"
python -c "import sysconfig; print(\"GIL disabled:\", sysconfig.get_config_var(\"Py_GIL_DISABLED\") == 1)"
echo ""
echo "LLVM/Clang:"
clang --version | head -1
llvm-config --version
echo ""
echo "CMake:"
cmake --version | head -1
echo ""
echo "Ninja:"
ninja --version
echo ""
echo "ccache:"
ccache --version | head -1
echo ""
echo "Test compilation (C++17 with clang):"
echo "#include <iostream>
int main() { std::cout << \"Hello from clang++!\" << std::endl; return 0; }" > /tmp/test.cpp
clang++ -std=c++17 /tmp/test.cpp -o /tmp/test && /tmp/test
rm -f /tmp/test.cpp /tmp/test
echo ""
echo "[OK] conda-llvm-slim all checks passed!"
'

echo ""
echo "=========================================="
echo "=== Test 2: onnx-dev-slim ==="
echo "=========================================="
docker run --rm devcontainer-base:onnx-dev-slim bash -c '
echo "Python:"
python --version
echo ""
echo "ONNX:"
python -c "import onnx; print(\"onnx:\", onnx.__version__)"
echo ""
echo "ONNX Runtime:"
python -c "import onnxruntime; print(\"onnxruntime:\", onnxruntime.__version__)"
echo ""
echo "Simple ONNX inference test:"
python -c "
import onnx
from onnx import helper, TensorProto
import onnxruntime as ort
import numpy as np

# Create a simple model
X = helper.make_tensor_value_info(\"X\", TensorProto.FLOAT, [1, 3])
Y = helper.make_tensor_value_info(\"Y\", TensorProto.FLOAT, [1, 3])
node = helper.make_node(\"Relu\", [\"X\"], [\"Y\"])
graph = helper.make_graph([node], \"relu\", [X], [Y])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid(\"\", 13)])
onnx.checker.check_model(model)

# Run inference
session = ort.InferenceSession(model.SerializeToString())
result = session.run(None, {\"X\": np.array([[-1.0, 0.0, 1.0]], dtype=np.float32)})
print(\"Relu([-1,0,1]) =\", result[0])
assert np.allclose(result[0], [[0.0, 0.0, 1.0]]), \"Inference failed!\"
print(\"[OK] ONNX inference works!\")
"
echo ""
echo "[OK] onnx-dev-slim all checks passed!"
'

echo ""
echo "=========================================="
echo "=== Test 3: onnx-quantized-slim ==="
echo "=========================================="
docker run --rm devcontainer-base:onnx-quantized-slim bash -c '
echo "Quantization modules:"
python -c "from onnxruntime.quantization import quantize_dynamic; print(\"quantize_dynamic: OK\")"
python -c "import onnxconverter_common; print(\"onnxconverter-common:\", onnxconverter_common.__version__)"
python -c "import onnxsim; print(\"onnxsim: OK\")"
echo ""
echo "[OK] onnx-quantized-slim all checks passed!"
'

echo ""
echo "=========================================="
echo "=== VALIDATION COMPLETE ==="
echo "=========================================="
echo ""
echo "=== Final Image Sizes ==="
docker images | grep -E "REPOSITORY|devcontainer-base"
echo ""
echo "=== Size comparison (slim vs expected) ==="
echo "Root (base+conda+docker): ~1.4GB"
echo "conda-llvm (adds LLVM/Clang/CMake/Ninja/ccache): ~2.9GB"
echo "onnx-dev (adds ONNX/ONNXRuntime): ~3.1GB"
echo "onnx-quantized (adds quantization tools): ~3.3GB"
echo ""
echo "Expected savings vs non-slim: ~2.3GB (removed chown CoW layer + aggressive cleanup)"
