---
id: "caffe-slim-tvm-ffi-troubleshooting"
title: "Caffe-Slim TVM FFI 环境调试与错误排查手册"
date: 2026-07-27
tags: [caffe-slim, tvm-ffi, troubleshooting, ffi, python-bindings, wsl, environment-debugging, dlpack]
source: "../../retrospective/reports/code-optimization/retrospective-caffe-slim-batch-inference-mnist-20260727/README.md"
---

# Caffe-Slim TVM FFI 环境调试与错误排查手册

> 本文档记录 Caffe-Slim（TVM FFI Python绑定）从环境配置到模型验证的完整错误链，包含**6个独立环境问题**的症状、根因、诊断命令和修复方案。可作为团队配置C++推理库Python FFI绑定时的参考排查手册。

---

## 一、环境与版本要求

| 组件 | 要求 | 实际环境 |
|------|------|---------|
| Python | ≥ 3.14（caffe-slim声明） | Windows: 3.13.9 ❌ / WSL Ubuntu: 3.12.3 ⚠️ |
| OS | Linux/macOS（Windows需WSL） | Windows 11 + WSL2 Ubuntu 22.04 |
| C++编译器 | CMake + GCC/Clang | GCC 11.4.0 |
| FFI绑定 | TVM FFI（内置），非boost::python | tvm-ffi (源码编译版) |
| numpy | ≥ 1.24（DLPack支持） | numpy 1.26.4 |

> **注意**：caffe-slim的pyproject.toml声明Python≥3.14，但实际在Python 3.12上也可运行（因为TVM FFI的Cython扩展可在3.12编译）。版本要求主要来自scikit-build-core。

---

## 二、环境问题排查全景图

```
import caffe 失败
├── E1: Python版本不满足（<3.14）
│   └── 解决：切换WSL/conda/pyenv
├── E2: ImportError: tvm_ffi is required
│   └── 解决：PYTHONPATH包含tvm-ffi/python
├── E3: cannot import name 'core' from partially initialized module 'tvm_ffi'
│   └── 解决：Cython扩展.so缺失 → 安装或编译
├── E4: undefined symbol: TVMFFIGetCustomAllocator
│   └── 解决：ABI不兼容 → 替换libtvm_ffi.so为构建配套版
├── E5: _caffe.so not found
│   └── 解决：LD_LIBRARY_PATH或symlink
└── E6: VENDOR_DIR路径差一级
    └── 解决：dirname层数从3改为2，加assert验证
```

---

## 三、逐个错误详解

### E1：Python版本不满足（<3.14）

**症状**：
```bash
$ pip install -e .
ERROR: Package 'caffe-slim' requires a different Python: 3.13.9 not in '>=3.14'
```

**根因**：caffe-slim使用scikit-build-core构建，pyproject.toml声明`requires-python = ">=3.14"`。

**诊断命令**：
```bash
python3 --version
which python3
```

**修复方案**：

方案A（推荐，本次使用）：WSL2 + Python 3.12
```bash
wsl --install -d Ubuntu
# 在WSL中
sudo apt update && sudo apt install python3 python3-pip
python3 --version  # Python 3.12.3
```

方案B：pyenv安装3.14（如果可用）
```bash
pyenv install 3.14.0
pyenv local 3.14.0
```

方案C：conda创建虚拟环境
```bash
conda create -n caffe python=3.12
conda activate caffe
```

> ⚠️ **注意**：即使声明≥3.14，在3.12上手动修改requires-python后也能编译和运行，但这是非官方支持的配置。

---

### E2：ImportError: tvm_ffi is required

**症状**：
```python
>>> import caffe
ImportError: tvm_ffi is required. Please install tvm_ffi first.
```

**根因**：`caffe/__init__.py`尝试`import tvm_ffi`，但tvm-ffi的Python包路径未在`sys.path`中。

**诊断命令**：
```python
import sys
print("\n".join(sys.path))
# 检查是否包含 tvm-ffi/python 路径

import importlib.util
print(importlib.util.find_spec("tvm_ffi"))  # 应为None
```

**目录结构背景**：
```
vendor/
├── caffe/caffe-slim/          # CAFFE_SLIM_DIR
│   ├── python/caffe/          # caffe包
│   └── build/                 # 构建输出
└── tvm-ffi/python/tvm_ffi/    # tvm_ffi包 ← 需要加入PYTHONPATH
```

**修复方案**：

在脚本开头添加路径，或设置环境变量：

```python
import os, sys
CAFFE_SLIM_DIR = "/path/to/vendor/caffe/caffe-slim"
VENDOR_DIR = os.path.dirname(os.path.dirname(CAFFE_SLIM_DIR))  # 两层dirname！
sys.path.insert(0, os.path.join(VENDOR_DIR, "tvm-ffi", "python"))
sys.path.insert(0, os.path.join(CAFFE_SLIM_DIR, "python"))
```

Shell启动脚本：
```bash
#!/bin/bash
export VENDOR_DIR="/path/to/vendor"
export PYTHONPATH="$VENDOR_DIR/tvm-ffi/python:$CAFFE_SLIM_DIR/python:$PYTHONPATH"
export LD_LIBRARY_PATH="$CAFFE_SLIM_DIR/build/lib:$LD_LIBRARY_PATH"
python3 batch_inference_demo.py
```

---

### E3：cannot import name 'core'（Cython扩展缺失）

**症状**：
```python
>>> import tvm_ffi
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File ".../tvm_ffi/__init__.py", line 15, in <module>
    from . import _api_internal
  File ".../tvm_ffi/_api_internal.py", line 1, in <module>
    from . import core
ImportError: cannot import name 'core' from partially initialized module 'tvm_ffi'
(most likely due to a circular import)
```

**根因**：`tvm_ffi.core`是Cython编译的C扩展（`core.cpython-312-x86_64-linux-gnu.so`），纯Python目录中不包含此文件。`pip install tvm_ffi`安装的纯Python包缺少编译的`.so`扩展。

**诊断命令**：
```bash
# 检查tvm_ffi目录下是否有编译的.so文件
find /path/to/tvm-ffi/python/tvm_ffi -name "*.so"
# 如果只有.py文件没有.so，说明C扩展未编译

# 检查Python是否能找到core子模块
python3 -c "import tvm_ffi.core; print(tvm_ffi.core.__file__)"
# ModuleNotFoundError 确认缺失
```

**错误信息误导性**：错误信息说"circular import"（循环导入），但实际是C扩展.so文件缺失。这是FFI类库最常见的误导性错误之一——import链断裂时Python的错误信息经常指向"circular import"。

**修复方案**：

方案A（推荐，本次使用）：使用PyPI版tvm_ffi的C扩展，再替换libtvm_ffi.so
```bash
pip install tvm-ffi  # 安装带C扩展的版本
# 注意：这会安装PyPI版的libtvm_ffi.so，后续E4需要替换
```

方案B：从源码编译tvm-ffi
```bash
cd /path/to/tvm-ffi
pip install -e .  # 就地编译Cython扩展
# 或
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

方案C：将build目录的so文件复制到Python包目录
```bash
cp /path/to/tvm-ffi/build/lib.*/*.so /path/to/tvm-ffi/python/tvm_ffi/
```

**验证命令**：
```python
import tvm_ffi
# 检查是否包含C扩展函数
assert hasattr(tvm_ffi, '_LIB'), "C扩展未加载"
print("tvm_ffi C扩展加载成功")
print([x for x in dir(tvm_ffi) if not x.startswith('_')])
```

---

### E4：undefined symbol: TVMFFIGetCustomAllocator（ABI不兼容）

**症状**：
```python
>>> import caffe
ImportError: /path/to/_caffe.so: undefined symbol: TVMFFIGetCustomAllocator
```

**根因**：`_caffe.so`在编译时链接了源码构建版的`libtvm_ffi.so`，该版本导出了`TVMFFIGetCustomAllocator`符号（自定义内存分配器支持）。但PyPI安装的tvm_ffi包带的`libtvm_ffi.so`是旧版本，不包含此符号。

**诊断命令**：
```bash
# 检查_caffe.so需要哪些符号
nm -D /path/to/_caffe.so | grep TVMFFIGetCustomAllocator
# U TVMFFIGetCustomAllocator  ← 未定义（需要外部提供）

# 检查当前libtvm_ffi.so导出了哪些符号
nm -D /path/to/site-packages/tvm_ffi/libtvm_ffi.so | grep TVMFFIGetCustomAllocator
# （无输出，表示该版本不导出此符号）

# 检查构建目录的libtvm_ffi.so
nm -D /path/to/caffe-slim/build/lib/libtvm_ffi.so | grep TVMFFIGetCustomAllocator
# T TVMFFIGetCustomAllocator  ← 导出了！
```

**修复方案**：用构建配套版本替换PyPI版本：

```bash
# 找到PyPI安装的tvm_ffi位置
TVM_FFI_SITE=$(python3 -c "import tvm_ffi; print(tvm_ffi.__path__[0])")
echo "tvm_ffi location: $TVM_FFI_SITE"

# 备份PyPI版本的lib
mv "$TVM_FFI_SITE/libtvm_ffi.so" "$TVM_FFI_SITE/libtvm_ffi.so.pypi_backup"

# 用构建目录的版本替换（软链接或复制）
ln -sf /path/to/caffe-slim/build/lib/libtvm_ffi.so "$TVM_FFI_SITE/libtvm_ffi.so"

# 验证符号现在可用
nm -D "$TVM_FFI_SITE/libtvm_ffi.so" | grep TVMFFIGetCustomAllocator
# 应该看到 T TVMFFIGetCustomAllocator
```

**原理**：C++动态库的符号在运行时解析。`_caffe.so`在编译时记录了需要`TVMFFIGetCustomAllocator`，运行时动态链接器需要在某个已加载的.so中找到这个符号。ABI兼容性要求：**编译_caffe.so时使用的libtvm_ffi头文件版本必须与运行时加载的libtvm_ffi.so版本一致**。

---

### E5：_caffe.so 动态库未找到

**症状**：
```python
>>> import caffe
  File ".../caffe/_ffi.py", line 25, in <module>
    _LIB = _find_lib("_caffe")
  File ".../caffe/_ffi.py", line 20, in _find_lib
    raise RuntimeError(f"Cannot find library {lib_name}")
RuntimeError: Cannot find library _caffe
```

**根因**：`_find_lib()`函数在预定义的搜索路径中查找`_caffe.so`，但WSL构建输出目录（`build/python/caffe/`）不在搜索路径中。

**诊断命令**：
```bash
# 查找_caffe.so实际位置
find /path/to/caffe-slim -name "_caffe*.so" 2>/dev/null
# 典型输出: build/python/caffe/_caffe.cpython-312-x86_64-linux-gnu.so

# 查看_find_lib搜索哪些路径（需要读源码）
grep -A 20 "def _find_lib" python/caffe/_ffi.py
```

**`_find_lib()`搜索路径分析**（典型实现）：
1. `caffe/`包所在目录本身
2. 环境变量`CAFFE_LIB_DIR`指定的目录
3. 系统库路径（`/usr/lib`, `/usr/local/lib`）
4. build目录的几种常见布局

**修复方案**：

方案A（推荐，本次使用）：创建symlink
```bash
cd /path/to/caffe-slim/python/caffe/
ln -sf ../../build/python/caffe/_caffe.cpython-312-x86_64-linux-gnu.so _caffe.so
# 验证
ls -la _caffe.so
python3 -c "import caffe; print('caffe imported successfully')"
```

方案B：设置LD_LIBRARY_PATH
```bash
export LD_LIBRARY_PATH="/path/to/caffe-slim/build/python/caffe:$LD_LIBRARY_PATH"
```

方案C：设置CAFFE_LIB_DIR环境变量
```bash
export CAFFE_LIB_DIR="/path/to/caffe-slim/build/python/caffe"
```

方案D：编译时设置rpath（最可靠，需重编译）
```bash
cmake .. -DCMAKE_INSTALL_RPATH="$ORIGIN/../../build/lib" -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON
```

---

### E6：VENDOR_DIR路径计算差一级

**症状**：
```python
# 脚本中的路径计算
CAFFE_SLIM_DIR = os.path.dirname(os.path.abspath(__file__))
VENDOR_DIR = os.path.dirname(os.path.dirname(os.path.dirname(CAFFE_SLIM_DIR)))
# 结果指向 vendor/caffe/ 而非 vendor/
# 导致 tvm-ffi 路径错误：vendor/caffe/tvm-ffi/python（不存在）
```

**根因**：链式调用`os.path.dirname()`的层数错误。三层dirname从`vendor/caffe/caffe-slim/`上溯到`vendor/caffe/`，但tvm-ffi在`vendor/tvm-ffi/`，只需要两层dirname到`vendor/`。

**目录结构**：
```
vendor/                          ← VENDOR_DIR 应该到这里（2层dirname）
├── caffe/                       ← 3层dirname错误地到了这里
│   └── caffe-slim/              ← __file__所在目录
│       └── batch_inference_demo.py
└── tvm-ffi/
    └── python/tvm_ffi/
```

**诊断命令**：
```python
import os
CAFFE_SLIM_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"CAFFE_SLIM_DIR: {CAFFE_SLIM_DIR}")
print(f"3 dirnames: {os.path.dirname(os.path.dirname(os.path.dirname(CAFFE_SLIM_DIR)))}")
print(f"2 dirnames: {os.path.dirname(os.path.dirname(CAFFE_SLIM_DIR))}")

# 验证tvm-ffi路径是否存在
VENDOR_DIR = os.path.dirname(os.path.dirname(CAFFE_SLIM_DIR))
tvm_ffi_path = os.path.join(VENDOR_DIR, "tvm-ffi", "python")
print(f"tvm_ffi exists: {os.path.exists(tvm_ffi_path)}")
assert os.path.exists(tvm_ffi_path), f"tvm_ffi not found at {tvm_ffi_path}"
```

**修复方案**：
```python
# 修正为2层dirname，并加assert防御
CAFFE_SLIM_DIR = os.path.dirname(os.path.abspath(__file__))
VENDOR_DIR = os.path.dirname(os.path.dirname(CAFFE_SLIM_DIR))

# 路径锚点验证（防御性编程）
_known_file = os.path.join(CAFFE_SLIM_DIR, "python", "caffe", "__init__.py")
assert os.path.exists(_known_file), f"CAFFE_SLIM_DIR seems wrong: {CAFFE_SLIM_DIR}"

_tvm_ffi_init = os.path.join(VENDOR_DIR, "tvm-ffi", "python", "tvm_ffi", "__init__.py")
assert os.path.exists(_tvm_ffi_init), f"VENDOR_DIR seems wrong: {VENDOR_DIR}"
```

**参考模式**：[path-anchor-semantization.md](../../retrospective/patterns/code-patterns/path-anchor-semantization.md) — 每级parent赋予语义变量名，避免链式`.parent.parent`计算差一级。

---

## 四、快速验证检查清单

配置完成后，运行以下命令验证环境是否正确：

```bash
#!/bin/bash
echo "=== Caffe-Slim 环境验证 ==="

echo "[1/6] Python版本检查"
python3 --version

echo "[2/6] PYTHONPATH检查"
python3 -c "
import sys
tvm_found = any('tvm-ffi' in p for p in sys.path)
caffe_found = any('caffe-slim/python' in p or 'caffe-slim\\python' in p for p in sys.path)
print(f'  tvm-ffi in path: {tvm_found}')
print(f'  caffe-slim in path: {caffe_found}')
"

echo "[3/6] tvm_ffi C扩展检查"
python3 -c "
import tvm_ffi
assert hasattr(tvm_ffi, '_LIB'), 'C扩展未加载'
print('  tvm_ffi C扩展: OK')
"

echo "[4/6] libtvm_ffi.so ABI检查"
python3 -c "
import tvm_ffi
lib_path = tvm_ffi._LIB._name
import subprocess
result = subprocess.run(['nm', '-D', lib_path], capture_output=True, text=True)
has_alloc = 'TVMFFIGetCustomAllocator' in result.stdout
print(f'  TVMFFIGetCustomAllocator符号: {\"OK\" if has_alloc else \"MISSING\"} ')
"

echo "[5/6] caffe导入检查"
python3 -c "
import caffe
print(f'  caffe version: {getattr(caffe, \"__version__\", \"unknown\")}')
print(f'  caffe imported: OK')
"

echo "[6/6] _caffe.so加载检查"
python3 -c "
import caffe._caffe as _caffe
print(f'  _caffe.so loaded: OK')
"

echo "=== 验证完成 ==="
```

---

## 五、模型加载与推理验证

环境配置通过后，验证模型推理正确性：

### 阶段1：随机权重冒烟测试
```python
import caffe
import numpy as np

net = caffe.Net("lenet.prototxt", caffe.TEST)
data = np.random.randn(1, 1, 28, 28).astype(np.float32)
net.set_input_data("data", data)
net.forward()
out = np.array(net.blob_data("prob"), copy=True)
assert out.shape == (1, 10), f"Unexpected output shape: {out.shape}"
assert abs(out.sum() - 1.0) < 1e-5, "Probabilities don't sum to 1"
print("随机权重冒烟测试通过")
```

### 阶段2：预训练权重加载测试
```python
net = caffe.Net("lenet.prototxt", "lenet_iter_10000.caffemodel", caffe.TEST)
data = np.random.randn(64, 1, 28, 28).astype(np.float32) / 256.0
net.set_input_data("data", data)
net.forward()
out = np.array(net.blob_data("prob"), copy=True)
assert out.shape == (64, 10)
preds = np.argmax(out, axis=1)
print(f"预训练权重推理完成，预测分布: {np.bincount(preds, minlength=10)}")
```

### 阶段3：标准数据集准确率验证
```python
# 加载MNIST测试集
test_data = np.load("data/mnist/mnist_test.npz")
images = test_data["data"]   # (10000, 1, 28, 28), float32, scale=1/256
labels = test_data["labels"] # (10000,), int64

# 分批推理（参考zero-copy-batch-inference-defense模式）
result = forward_all(net, "data", "prob", images)
predictions = np.argmax(result["prob"], axis=1)
accuracy = (predictions == labels).mean()
print(f"MNIST测试集准确率: {accuracy*100:.2f}%")
assert accuracy > 0.985, f"准确率过低: {accuracy*100:.2f}% (期望>98.5%)"
```

**准确率判据**：
- 随机权重：~10%（均匀分布）
- 正常训练的LeNet：98.5%~99.2%
- 如果准确率在30-70%：通常是预处理参数错误（如scale用1/255而非1/256，或忘记除以256）
- 如果准确率在80-95%：可能是部分权重加载错误，或prototxt与caffemodel不完全匹配
- 如果准确率~10%：权重文件无效（截断/错误格式）或输入数据未预处理

---

## 六、常见错误快速定位表

| 错误信息 | 问题编号 | 快速修复 |
|---------|---------|---------|
| `requires a different Python: 3.x not in '>=3.14'` | E1 | 切换Python版本或WSL |
| `ImportError: tvm_ffi is required` | E2 | 设置PYTHONPATH包含tvm-ffi/python |
| `cannot import name 'core' from partially initialized module` | E3 | 安装tvm-ffi或编译Cython扩展 |
| `undefined symbol: TVMFFIGetCustomAllocator` | E4 | 替换libtvm_ffi.so为构建版 |
| `RuntimeError: Cannot find library _caffe` | E5 | 创建symlink或设置LD_LIBRARY_PATH |
| `FileNotFoundError: ...tvm_ffi/__init__.py` | E6 | 修正VENDOR_DIR的dirname层数 |
| 准确率~10% | 模型问题 | 检查模型文件大小+magic bytes+scale预处理 |
| 准确率~50-80% | 数据问题 | 检查输入shape和预处理（BGR↔RGB, mean, scale） |
| 输出每批都一样 | Zero-copy | `np.array(..., copy=True)` 拷贝输出 |
| 最后一批崩溃 | Padding | 创建zero-padded batch数组 |
| 单样本和批量结果不同 | Consistency | 检查padding和slice逻辑 |

---

## 七、环境配置一键脚本（WSL/Ubuntu）

```bash
#!/bin/bash
set -euo pipefail

CAFFE_SLIM_DIR="$(cd "$(dirname "$0")" && pwd)"
VENDOR_DIR="$(dirname "$(dirname "$CAFFE_SLIM_DIR")")"

echo "=== Caffe-Slim 环境配置 ==="
echo "CAFFE_SLIM_DIR: $CAFFE_SLIM_DIR"
echo "VENDOR_DIR: $VENDOR_DIR"

# 1. 安装系统依赖
echo "[1/4] 安装系统依赖..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-pip python3-numpy cmake g++

# 2. 安装Python依赖
echo "[2/4] 安装Python依赖..."
pip3 install --user numpy scikit-build-core cython

# 3. 编译caffe-slim（如果尚未编译）
if [ ! -f "$CAFFE_SLIM_DIR/build/python/caffe/_caffe.cpython-312-x86_64-linux-gnu.so" ]; then
    echo "[3/4] 编译caffe-slim..."
    cd "$CAFFE_SLIM_DIR"
    mkdir -p build && cd build
    cmake .. -DCMAKE_BUILD_TYPE=Release
    make -j"$(nproc)"
else
    echo "[3/4] caffe-slim已编译，跳过"
fi

# 4. 设置环境变量和symlink
echo "[4/4] 配置运行环境..."

# 创建_caffe.so symlink
cd "$CAFFE_SLIM_DIR/python/caffe"
_CAFFE_BUILT=$(ls "$CAFFE_SLIM_DIR/build/python/caffe/_caffe.cpython"*.so 2>/dev/null | head -1)
if [ -n "$_CAFFE_BUILT" ]; then
    ln -sf "$_CAFFE_BUILT" _caffe.so
    echo "  _caffe.so symlink created"
fi

# 替换libtvm_ffi.so
TVM_FFI_SITE=$(python3 -c "import tvm_ffi; print(tvm_ffi.__path__[0])" 2>/dev/null || echo "")
if [ -n "$TVM_FFI_SITE" ] && [ -f "$CAFFE_SLIM_DIR/build/lib/libtvm_ffi.so" ]; then
    if [ -f "$TVM_FFI_SITE/libtvm_ffi.so" ] && [ ! -f "$TVM_FFI_SITE/libtvm_ffi.so.build_backup" ]; then
        mv "$TVM_FFI_SITE/libtvm_ffi.so" "$TVM_FFI_SITE/libtvm_ffi.so.build_backup"
    fi
    ln -sf "$CAFFE_SLIM_DIR/build/lib/libtvm_ffi.so" "$TVM_FFI_SITE/libtvm_ffi.so"
    echo "  libtvm_ffi.so replaced with build version"
fi

# 设置PYTHONPATH和LD_LIBRARY_PATH
export PYTHONPATH="$VENDOR_DIR/tvm-ffi/python:$CAFFE_SLIM_DIR/python:${PYTHONPATH:-}"
export LD_LIBRARY_PATH="$CAFFE_SLIM_DIR/build/lib:${LD_LIBRARY_PATH:-}"

echo ""
echo "=== 配置完成 ==="
echo "请运行以下命令使环境变量生效："
echo "  export PYTHONPATH=\"$VENDOR_DIR/tvm-ffi/python:$CAFFE_SLIM_DIR/python:\$PYTHONPATH\""
echo "  export LD_LIBRARY_PATH=\"$CAFFE_SLIM_DIR/build/lib:\$LD_LIBRARY_PATH\""
echo ""
echo "然后运行：python3 $CAFFE_SLIM_DIR/batch_inference_demo.py"
```

使用方法：
```bash
chmod +x setup_env.sh
source setup_env.sh  # 用source执行才能在当前shell设置环境变量
```

---

## 八、相关参考

| 参考文档 | 路径 | 说明 |
|---------|------|------|
| 复盘报告 | [retrospective-caffe-slim-batch-inference-mnist-20260727](../../retrospective/reports/code-optimization/retrospective-caffe-slim-batch-inference-mnist-20260727/README.md) | 完整R-I-E复盘 |
| 零拷贝分批推理模式 | [zero-copy-batch-inference-defense.md](../../retrospective/patterns/code-patterns/zero-copy-batch-inference-defense.md) | 分批推理代码模式 |
| 模型下载验证模式 | [pretrained-model-download-validation.md](../../retrospective/patterns/code-patterns/pretrained-model-download-validation.md) | 模型下载验证代码模式 |
| 路径锚点语义化 | [path-anchor-semantization.md](../../retrospective/patterns/code-patterns/path-anchor-semantization.md) | 避免.dirname差一级 |
| 共享库符号双层控制 | [shared-lib-symbol-dual-layer-control.md](../../retrospective/patterns/code-patterns/shared-lib-symbol-dual-layer-control.md) | 动态库符号可见性 |
| Python原生扩展自包含wheel | [python-native-extension-self-contained-wheel.md](../../retrospective/patterns/code-patterns/python-native-extension-self-contained-wheel.md) | 自包含wheel打包 |
| FFI环境配置模式 | 见复盘报告E阶段模式1 | FFI绑定五步配置法 |

---

## Changelog

- 2026-07-27 | create | 初始版本，从caffe-slim MNIST验证复盘提取6个环境错误的完整诊断和修复方案，作为团队FFI环境调试参考文档
