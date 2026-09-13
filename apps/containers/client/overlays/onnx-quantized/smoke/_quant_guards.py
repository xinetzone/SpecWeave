"""构建期守卫：五包版本打印 + cp314t free-threading + torch 系缺席负向验证。

提取为独立脚本（而非 Dockerfile 内联 python -c）的原因：
buildah 对 shell-form RUN 的 /bin/bash -lc '<body>' 做二次分词，
python -c 内层双重转义引号（\\"...\\"）在构建器内被切断（SyntaxError），
固化为脚本后构建 RUN 只需无嵌套引号的单一路径参数。

负向守卫集合与源 variants/onnx-dev/Dockerfile Stage 2 一致：
torch / torchvision（一等排除）+ onnxoptimizer（ft 不兼容，CPython #111506）。
"""
import importlib.util
import sys
import sysconfig

import onnx
import onnxconverter_common
import onnxruntime
import onnxscript
import onnxsim

print("  onnx", onnx.__version__)
print("  onnxruntime", onnxruntime.__version__)
print("  onnxscript", onnxscript.__version__)
print("  onnxconverter-common", onnxconverter_common.__version__)
print("  onnxsim(module)", onnxsim.__version__)

assert sysconfig.get_config_var("Py_GIL_DISABLED") == 1, "NOT a free-threading build"
assert sys._is_gil_enabled() is False, "GIL still enabled"

for absent_pkg in ("torch", "torchvision", "onnxoptimizer"):
    assert importlib.util.find_spec(absent_pkg) is None, f"{absent_pkg} must be absent"

print("[OK] guards: cp314t + GIL off + torch/torchvision/onnxoptimizer absent")
