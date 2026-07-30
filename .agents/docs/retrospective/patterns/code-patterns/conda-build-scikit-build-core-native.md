---
id: "conda-build-scikit-build-core-native"
title: "conda-build + scikit-build-core 原生扩展打包模式"
type: code-pattern
date: 2026-07-30
maturity: L3 方法论（已完成闭环验证）
maturity_note: "双案例验证（caffe-ffi + tvm-ffi 跨包依赖），涵盖参数隔离、RPATH、符号验证、构建隔离等完整流程"
source: "retrospective-caffe-ffi-conda-build-20260730 复盘"
related_patterns:
  - "conda-custom-channels-mirror.md"
  - "shared-lib-symbol-dual-layer-control.md"
  - "cmake-four-layer-modular-architecture.md"
tags: ["conda", "conda-build", "scikit-build-core", "native-extension", "cmake", "rpath", "orign", "symbol-verification", "build-isolation", "pep-517"]
validation_count: 2
reuse_count: 0
---

# conda-build + scikit-build-core 原生扩展打包模式

## 触发场景

- 使用 conda-build 打包包含 C/C++ 原生扩展的 Python 包，构建系统为 scikit-build-core（PEP 517）
- 包内有 `.so`/`.pyd` 原生扩展，且依赖其他 conda 包中的原生库（跨包依赖）
- 开发环境存在 `pip install -e .` 残留，可能干扰 conda 包构建和验证
- 需要确保构建产物在不同 conda 环境中可移植，不依赖构建机绝对路径
- 嵌套构建：主包构建时需要本地编译依赖子项目（如从源码构建依赖库而非使用 PyPI wheel）

**不适用场景**：
- 纯 Python 包（无原生扩展）
- 使用 setuptools/distutils 而非 scikit-build-core 的构建
- Windows 平台（RPATH 机制不同，使用 PATH 环境变量）
- macOS 平台（使用 `@loader_path`/`@rpath` 而非 `$ORIGIN`，待验证）

## 问题背景

conda-build 与 scikit-build-core 集成时存在五个独立的陷阱层，任何一层处理不当都会导致构建失败或运行时错误：

```
┌─────────────────────────────────────────────────────────────────────┐
│           conda-build + scikit-build-core 五层陷阱                     │
├──────────────────┬──────────────────────────────────────────────────┤
│  层1：依赖分层    │  build/host/run 三段依赖划分错误，                  │
│                  │  Python构建后端必须在host段                        │
├──────────────────┼──────────────────────────────────────────────────┤
│  层2：构建隔离    │  --no-build-isolation 模式下环境变量污染，            │
│                  │  CMAKE_ARGS/SKBUILD_CMAKE_ARGS 泄漏到子项目构建       │
├──────────────────┼──────────────────────────────────────────────────┤
│  层3：RPATH配置  │  绝对路径触发Placeholder too short，                │
│                  │  相对路径深度计算错误导致依赖找不到                   │
├──────────────────┼──────────────────────────────────────────────────┤
│  层4：符号验证    │  预编译Wheel缺少关键符号，RPATH修改后符号不丢失       │
├──────────────────┼──────────────────────────────────────────────────┤
│  层5：Editable残留│  .pth/.py/__pycache__/direct_url.json 四件套残留    │
│                  │  导致import加载源码目录而非conda包                   │
└──────────────────┴──────────────────────────────────────────────────┘
```

### 依赖分层规则（conda-build 三段式）

| 段 | 安装阶段 | 用途 | scikit-build-core 特有要求 |
|----|---------|------|---------------------------|
| `build` | 构建开始前（构建环境） | 构建工具本身（编译器、cmake、ninja） | `setuptools-scm`、`hatchling` 等构建后端必须放在 `host`，**不要**放在 `build` |
| `host` | 构建开始前（主机环境） | 构建时需要链接/导入的库 | `python`、`scikit-build-core`、`pybind11`、`nanobind`、需要链接的 C/C++ 库 |
| `run` | 安装后（运行时环境） | 运行时依赖 | 与 `host` 中版本兼容的运行时库 |

**关键反模式**：将 `scikit-build-core` 放在 `build` 段，导致 `--no-build-isolation` 模式下找不到构建后端。

## 核心步骤（六步法）

### 步骤1：meta.yaml 依赖正确分层

```yaml
# ✅ meta.yaml 正确配置
package:
  name: caffe-ffi
  version: {{ version }}

source:
  path: ..

build:
  number: 6
  script: bash conda.recipe/build.sh  # 显式指定build.sh
  detect_binary_files_with_prefix: false  # RPATH使用$ORIGIN相对路径，禁用前缀检测
  missing_dso_whitelist:
    - "*/libtvm_ffi*.so*"  # 本地源码编译的依赖库，通过RPATH解析
    - "*/libopenblas*.so*"  # conda环境中的依赖库

requirements:
  build:
    - {{ compiler('cxx') }}
    - cmake >=3.18
    - ninja
    - git  # SETUPTOOLS_SCM_PRETEND_VERSION需要git
  host:
    - python
    - pip
    - scikit-build-core >=0.5  # ✅ 构建后端必须在host段
    - setuptools-scm >=8.0     # ✅ 版本管理工具在host段
    - pybind11 >=2.10
    - numpy >=1.21
    - openblas-devel  # 构建时需要链接的C库
  run:
    - python
    - numpy >=1.21
    - openblas  # 运行时依赖
    - __osx >={{ MACOSX_DEPLOYMENT_TARGET|default("10.13") }}  # [osx]
```

**关键配置说明**：
- `detect_binary_files_with_prefix: false`：使用 `$ORIGIN`/`@loader_path` 相对 RPATH 时必须设置，否则 conda-build 会尝试做前缀替换，在相对路径上失败
- `missing_dso_whitelist`：本地源码编译的依赖库（不通过 conda 依赖安装）需要加入白名单，否则 conda-build 的 DSO 检查会报错；conda-build ≥26.5 将重命名为 `missing_dso_allowlist`，建议同时保留两个key做前向兼容
- macOS平台条件依赖：`cctools # [osx]`（提供install_name_tool/otool）、`llvm-openmp # [osx]`（OpenMP运行时）、`macos-sdk # [osx]`（SDK头文件）

### 步骤1b：pyproject.toml 三层分离配置CMake参数

CMake参数应按"项目默认值→平台条件→Conda运行时"**三层分离**原则配置，避免在build.sh中堆积大量-D参数：

```toml
# pyproject.toml
[tool.scikit-build]
minimum-version = "0.10"
cmake.build-type = "Release"
ninja.make-fallback = false
build.verbose = true

# 第一层：项目默认值（适用于所有构建环境：pip/conda/editable）
[tool.scikit-build.cmake.define]
CMAKE_EXPORT_COMPILE_COMMANDS = "ON"
CAFFE_CPU_ONLY = "ON"
CAFFE_USE_BLAS = "ON"
CAFFE_FFI_BUILD_TESTS = "OFF"
CMAKE_INSTALL_RPATH_USE_LINK_PATH = "ON"
CMAKE_SKIP_BUILD_RPATH = "OFF"
CMAKE_BUILD_WITH_INSTALL_RPATH = "ON"
CMAKE_POSITION_INDEPENDENT_CODE = "ON"

# 第二层：平台条件（通过[[tool.scikit-build.overrides]]）
# Linux：$ORIGIN相对RPATH
[[tool.scikit-build.overrides]]
if.platform-system = "linux"
[tool.scikit-build.overrides.cmake.define]
CMAKE_BUILD_RPATH_USE_ORIGIN = "ON"

# macOS：@rpath/install_name
[[tool.scikit-build.overrides]]
if.platform-system = "^darwin"
[tool.scikit-build.overrides.cmake.define]
CMAKE_MACOSX_RPATH = "ON"
CMAKE_INSTALL_NAME_DIR = "@rpath"
```

**三层分离原则**：

| 层 | 位置 | 包含参数 | 原因 |
|---|---|---|---|
| 项目默认值 | `[tool.scikit-build.cmake.define]` | BUILD_TYPE、CPU_ONLY、USE_BLAS、SKIP_BUILD_RPATH、POSITION_INDEPENDENT_CODE等 | 适用于所有构建环境 |
| 平台条件 | `[[tool.scikit-build.overrides]]` | Linux: BUILD_RPATH_USE_ORIGIN；macOS: MACOSX_RPATH、INSTALL_NAME_DIR | 通过`if.platform-system`正则匹配 |
| Conda运行时 | `build.sh SKBUILD_CMAKE_ARGS` | CMAKE_PREFIX_PATH、INSTALL_RPATH、PREFER_SYSTEM_TVM_FFI等 | 依赖运行时变量`$PREFIX`或需post-build RPATH修复 |

**关键约束**：
- ❌ **禁止**在pyproject.toml中设置`CMAKE_INSTALL_RPATH`：conda环境下RPATH由patchelf/install_name_tool在构建后重新设置，pyproject.toml中设置的值会被覆盖
- ❌ **禁止**在pyproject.toml中设置`CMAKE_PREFIX_PATH`：该值依赖运行时`${PREFIX}`变量，不同conda环境路径不同
- ✅ **应**在pyproject.toml中设置项目通用的CMake选项，减少build.sh中SKBUILD_CMAKE_ARGS的参数数量
- ✅ **应**使用`if.platform-system`（值为`sys.platform`的正则匹配：`"linux"`/`"^darwin"`/`"win32"`）处理平台差异

### 步骤2：build.sh 构建前环境准备与Editable清理

```bash
#!/bin/bash
set -euxo pipefail

# ---- Editable残留三重保护清理（第一重：构建前清理） ----
clean_editable_files() {
    python - <<'PY'
import site, glob, os, shutil
for sp in site.getsitepackages():
    # 清理 _editable_*.pth 和对应的 finder .py
    for pth in glob.glob(os.path.join(sp, '_editable_*.pth')) + glob.glob(os.path.join(sp, '__editable__.*.pth')):
        base = os.path.splitext(pth)[0]
        for f in [pth, base + '.py']:
            if os.path.exists(f):
                os.remove(f)
        # 清理 __pycache__ 中的finder缓存
        pycache = os.path.join(sp, '__pycache__')
        if os.path.isdir(pycache):
            for cached in glob.glob(os.path.join(pycache, os.path.basename(base) + '.*.pyc')):
                os.remove(cached)
    # 清理 direct_url.json（pip editable安装标记）
    for dist_info in glob.glob(os.path.join(sp, 'caffe_ffi-*.dist-info')) + glob.glob(os.path.join(sp, 'caffe-ffi-*.dist-info')):
        duj = os.path.join(dist_info, 'direct_url.json')
        if os.path.exists(duj):
            os.remove(duj)
PY
}
clean_editable_files

# ---- 设置SETUPTOOLS_SCM_PRETEND_VERSION绕过git版本问题 ----
export SETUPTOOLS_SCM_PRETEND_VERSION="${PKG_VERSION}"
```

### 步骤3：嵌套构建参数隔离（关键！）

当主包需要本地编译依赖子项目时，**必须**隔离 conda-build 注入的 `CMAKE_ARGS` 和 `SKBUILD_CMAKE_ARGS`，否则子项目会继承主包的安装路径等参数，导致安装到错误位置：

```bash
# ---- 保存conda-build注入的原始环境变量 ----
_SAVED_CMAKE_ARGS="${CMAKE_ARGS:-}"
_SAVED_SKBUILD_CMAKE_ARGS="${SKBUILD_CMAKE_ARGS:-}"

# ---- 临时清除构建参数，编译依赖子项目 ----
unset CMAKE_ARGS
unset SKBUILD_CMAKE_ARGS

echo "[build.sh] Building tvm-ffi from source (isolated environment)..."
export TVM_FFI_HOME="${SRC_DIR}/../tvm-ffi"
export SETUPTOOLS_SCM_PRETEND_VERSION_TVM_FFI="0.2.0"

# 在隔离环境中pip安装依赖（不使用conda-build的CMAKE_ARGS）
pip install --no-build-isolation "${TVM_FFI_HOME}" --prefix="${PREFIX}" \
    --no-deps -vv --no-cache-dir

# ---- 恢复原始构建参数，构建主包 ----
export CMAKE_ARGS="${_SAVED_CMAKE_ARGS}"
export SKBUILD_CMAKE_ARGS="${_SAVED_SKBUILD_CMAKE_ARGS}"

echo "[build.sh] Building caffe-ffi..."
pip install --no-build-isolation "${SRC_DIR}" --prefix="${PREFIX}" \
    --no-deps -vv --no-cache-dir
```

**原理**：conda-build 会设置 `CMAKE_ARGS="-DCMAKE_INSTALL_PREFIX=${PREFIX} ..."` 等参数，这些参数是为主包准备的。如果子项目继承这些参数，会导致：
1. 子项目安装到错误的位置
2. 子项目使用主包的 RPATH 设置
3. 子项目链接到主包的依赖而非自身依赖

### 步骤4：$ORIGIN 相对 RPATH 配置与跨包依赖

**绝对禁止**使用 `${PREFIX}/lib` 绝对路径，这会触发 conda-build 的 "Placeholder too short" 错误（前缀替换时路径长度不足）。必须使用 `$ORIGIN` 相对路径，并根据库嵌套层级精确计算深度：

```bash
# ---- RPATH配置：$ORIGIN相对路径，精确计算深度 ----

# 主包原生扩展位置：${SP_DIR}/caffe_ffi/_caffe_ffi.so
# 深度：site-packages/caffe_ffi/ → ../../ 到达 site-packages/ → ../../../ 到达 PREFIX/
# 所以到PREFIX/lib是$ORIGIN/../../../lib/
# 到tvm_ffi/lib是$ORIGIN/../../../tvm_ffi/lib/

CAFFE_FFI_LIB="${SP_DIR}/caffe_ffi/_caffe_ffi.so"
TVM_FFI_LIB="${SP_DIR}/tvm_ffi/lib/libtvm_ffi.so"

# 为主包_caffe_ffi.so设置RPATH：自身所在目录 + conda lib目录 + 跨包tvm_ffi依赖
patchelf --set-rpath '$ORIGIN:$ORIGIN/../../../lib:$ORIGIN/../../../tvm_ffi/lib' "${CAFFE_FFI_LIB}"

# 为依赖的libtvm_ffi.so设置RPATH（它在更深一层：tvm_ffi/lib/，深度+1）
# 它需要找到同目录的其他tvm_ffi库 + conda lib目录
patchelf --set-rpath '$ORIGIN:$ORIGIN/../../../../lib' "${TVM_FFI_LIB}"
```

**RPATH深度计算公式**：
1. 从 `.so` 文件所在目录到 `${PREFIX}` 的 `..` 层数 = 深度
2. `${PREFIX}/lib` → `$ORIGIN/${depth_parents}lib`
3. 跨包依赖（如 `${PREFIX}/tvm_ffi/lib/`）→ `$ORIGIN/${depth_parents}tvm_ffi/lib`
4. **每个依赖库单独计算**：嵌套更深的库需要更多 `../`

### 步骤5：符号完整性双重验证

在 RPATH 修改前后都要验证关键符号存在，防止：
1. 预编译 wheel 缺少关键符号（如 PyPI 上的 apache-tvm-ffi wheel 缺少 `TVMFFIGetCustomAllocator`）
2. patchelf 操作意外破坏符号表

```bash
# ---- 符号验证：RPATH修改前检查 ----
echo "[build.sh] Verifying critical symbols BEFORE patchelf..."
if ! nm -D "${TVM_FFI_LIB}" | grep -q "T TVMFFIGetCustomAllocator"; then
    echo "[build.sh] ERROR: TVMFFIGetCustomAllocator symbol not found (T symbol expected)"
    echo "[build.sh] This usually means the PyPI wheel is stripped or misconfigured"
    echo "[build.sh] Checking available TVMFFI symbols:"
    nm -D "${TVM_FFI_LIB}" | grep TVMFFI | head -20
    exit 1
fi

# 执行RPATH修改...
patchelf --set-rpath ...

# ---- 符号验证：RPATH修改后复查 ----
echo "[build.sh] Verifying critical symbols AFTER patchelf..."
if ! nm -D "${TVM_FFI_LIB}" | grep -q "T TVMFFIGetCustomAllocator"; then
    echo "[build.sh] ERROR: Symbol lost during patchelf!"
    exit 1
fi

# ---- ldd依赖验证 ----
echo "[build.sh] Verifying library dependencies with ldd..."
ldd "${CAFFE_FFI_LIB}" | grep -E "not found|libtvm|libopenblas" || true
if ldd "${CAFFE_FFI_LIB}" | grep -q "not found"; then
    echo "[build.sh] ERROR: Unresolved dependencies found!"
    ldd "${CAFFE_FFI_LIB}"
    exit 1
fi
```

**符号判断标准**：
- `T` 大写：符号在 .text 段定义（公共函数，是我们需要的）
- `U`：符号未定义（依赖其他库，正常）
- `W`/`w`：弱符号（通常是 C++ 模板实例化，正常）
- 如果预期的 `T` 符号缺失，说明链接时符号被隐藏或库版本不对

### 步骤6：Editable残留三重保护（后清理+安装验证）

```bash
# ---- Editable残留清理（第二重：依赖安装后清理） ----
clean_editable_files

# 主包安装...
pip install ...

# ---- Editable残留清理（第三重：主包安装后清理） ----
clean_editable_files

# ---- 安装路径验证门禁 ----
echo "[build.sh] Verifying import path..."
python -c "
import caffe_ffi
import os
# 必须从site-packages导入，不能从源码目录
assert 'site-packages' in caffe_ffi.__file__, \
    f'Imported from source directory instead of site-packages: {caffe_ffi.__file__}'
print(f'[build.sh] caffe_ffi imported from: {caffe_ffi.__file__}')
"
```

## 反模式（不要这么做）

### ❌ 反模式1：将scikit-build-core放在build段而非host段

```yaml
# ❌ 错误：构建后端在build段，--no-build-isolation时找不到
requirements:
  build:
    - cmake
    - ninja
    - scikit-build-core  # 错误位置！
  host:
    - python
    - pip
```

- **后果**：`pip install --no-build-isolation` 时找不到 `scikit_build_core` 构建后端，构建失败
- **正确做法**：所有 Python 构建后端都放在 `host` 段

### ❌ 反模式2：嵌套构建时不隔离CMAKE_ARGS

```bash
# ❌ 错误：直接pip安装依赖，继承主包CMAKE_ARGS
pip install --no-build-isolation ../tvm-ffi --prefix="${PREFIX}"
```

- **后果**：tvm-ffi 的 cmake_install_prefix 被设置为主包的路径，可能安装到错误位置；RPATH 也继承主包设置导致依赖查找错误
- **正确做法**：步骤3 的保存→清除→构建→恢复流程

### ❌ 反模式3：RPATH使用绝对路径

```bash
# ❌ 错误：绝对RPATH触发Placeholder too short
patchelf --set-rpath "${PREFIX}/lib" "${CAFFE_FFI_LIB}"
```

- **后果**：conda-build 在进行前缀替换时，发现新路径长度超过二进制中的占位符长度，报错 "Placeholder too short"
- **正确做法**：始终使用 `$ORIGIN` 相对路径，按步骤4计算深度

### ❌ 反模式4：所有库使用统一RPATH深度

```bash
# ❌ 错误：所有.so使用相同深度
patchelf --set-rpath '$ORIGIN:$ORIGIN/../../../lib' "${CAFFE_FFI_LIB}"
patchelf --set-rpath '$ORIGIN:$ORIGIN/../../../lib' "${TVM_FFI_LIB}"  # 错误！它在更深一层
```

- **后果**：嵌套在子目录中的库（如 `tvm_ffi/lib/libtvm_ffi.so`）的相对路径深度错误，找不到依赖
- **正确做法**：每个库根据自身所在目录单独计算 `../` 层数

### ❌ 反模式5：只清理.pth文件，忽略其他editable残留

```bash
# ❌ 错误：只删除.pth，不清理finder模块和缓存
rm -f "${SP_DIR}/_editable_*.pth"
```

- **后果**：`__editable___caffe_ffi_finder.py` 仍然存在，`__pycache__` 中有旧的字节码缓存，`direct_url.json` 让 pip 认为这是 editable 安装
- **正确做法**：步骤2 的三重保护清理函数（.pth + .py + __pycache__ + direct_url.json）

### ❌ 反模式6：跳过符号验证，编译通过就认为没问题

```bash
# ❌ 错误：只编译不验证符号
pip install ...
patchelf --set-rpath ...
# 直接结束，不检查nm和ldd
```

- **后果**：
  - PyPI wheel 缺少关键符号直到运行时才发现
  - patchelf 操作可能意外破坏符号表
  - 依赖库缺失只在用户import时才报错
- **正确做法**：步骤5 的双重符号验证 + ldd 依赖检查

## 检验标准

做完之后怎么知道做对了？

- [ ] 标准1：meta.yaml 中 `scikit-build-core`、`setuptools-scm` 在 `host` 段而非 `build` 段
- [ ] 标准2：`detect_binary_files_with_prefix: false` 已设置
- [ ] 标准3：嵌套子项目构建前后保存/恢复了 `CMAKE_ARGS` 和 `SKBUILD_CMAKE_ARGS`
- [ ] 标准4：所有 RPATH 使用 `$ORIGIN` 相对路径，无 `${PREFIX}` 绝对路径
- [ ] 标准5：每个 `.so` 文件的 RPATH 深度根据自身位置单独计算
- [ ] 标准6：patchelf 前后都用 `nm -D` 验证关键符号为 `T` 类型
- [ ] 标准7：`ldd` 检查所有依赖库，无 "not found"
- [ ] 标准8：build.sh 中有三重 editable 残留清理（构建前、依赖后、主包后）
- [ ] 标准9：构建末尾验证 `import caffe_ffi` 的 `__file__` 包含 `site-packages`
- [ ] 标准10：conda-build 构建无 "Placeholder too short"、"missing DSO" 错误
- [ ] 标准11：在全新 conda 环境中 `conda install --offline` 后 import 成功
- [ ] 标准12：单元测试在全新环境中全部通过

## 完整 test-conda-build.sh 验证脚本模板

```bash
#!/bin/bash
set -euxo pipefail

# 测试环境名称
ENV_NAME="caffe-ffi-test"
BUILD_DIR="./conda-bld"

# ---- Step 0: 清理旧环境 ----
conda env remove -n "${ENV_NAME}" -y 2>/dev/null || true
rm -rf "${BUILD_DIR}"

# ---- Step 1: 清理当前环境的editable残留（测试脚本第一重） ----
python - <<'PY'
import site, glob, os
for sp in site.getsitepackages():
    for pth in glob.glob(os.path.join(sp, '_editable_*.pth')) + glob.glob(os.path.join(sp, '__editable__.*.pth')):
        base = os.path.splitext(pth)[0]
        for f in [pth, base + '.py']:
            if os.path.exists(f): os.remove(f)
        pycache = os.path.join(sp, '__pycache__')
        if os.path.isdir(pycache):
            for cached in glob.glob(os.path.join(pycache, os.path.basename(base) + '.*.pyc')):
                os.remove(cached)
    for dist_info in glob.glob(os.path.join(sp, 'caffe_ffi-*.dist-info')) + glob.glob(os.path.join(sp, 'caffe-ffi-*.dist-info')):
        duj = os.path.join(dist_info, 'direct_url.json')
        if os.path.exists(duj): os.remove(duj)
PY

# ---- Step 2: 构建conda包 ----
conda build conda.recipe/ -c conda-forge --output-folder "${BUILD_DIR}" --no-test

# ---- Step 3: 获取构建产物路径 ----
PKG_FILE=$(conda build conda.recipe/ --output --output-folder "${BUILD_DIR}")
echo "Built package: ${PKG_FILE}"

# ---- Step 4: 创建全新测试环境 ----
conda create -n "${ENV_NAME}" python=3.12 -c conda-forge -y

# ---- Step 5: 在新环境中安装前再次清理（防万一） ----
conda run -n "${ENV_NAME}" python - <<'PY'
import site, glob, os
for sp in site.getsitepackages():
    for pth in glob.glob(os.path.join(sp, '_editable_*.pth')):
        os.remove(pth)
PY

# ---- Step 6: 离线安装conda包 ----
conda install -n "${ENV_NAME}" --offline "${PKG_FILE}" -y

# ---- Step 7: 验证导入路径 ----
conda run -n "${ENV_NAME}" python -c "
import caffe_ffi
assert 'site-packages' in caffe_ffi.__file__, f'Wrong import path: {caffe_ffi.__file__}'
print(f'Successfully imported from: {caffe_ffi.__file__}')
"

# ---- Step 8: 验证ldd依赖 ----
conda run -n "${ENV_NAME}" python -c "
import caffe_ffi._caffe_ffi
import subprocess, glob, os
lib_path = os.path.dirname(caffe_ffi._caffe_ffi.__file__)
for so in glob.glob(os.path.join(lib_path, '*.so')):
    result = subprocess.run(['ldd', so], capture_output=True, text=True)
    assert 'not found' not in result.stdout, f'Unresolved deps in {so}'
print('All library dependencies resolved')
"

# ---- Step 9: 禁用C++栈回溯避免pytest崩溃 ----
export CAFFE_FFI_DISABLE_BACKTRACE=1

# ---- Step 10: 运行单元测试 ----
conda run -n "${ENV_NAME}" python -m pytest tests/ -v

echo "✅ All verification steps passed!"
```

## 迁移示例

这个模式还能用在什么场景？

### 场景1：caffe-ffi Conda包（本项目，源案例）

- **原生扩展**：`_caffe_ffi.so`（pybind11）
- **跨包依赖**：tvm-ffi（本地源码编译）、openblas（conda依赖）
- **嵌套深度**：`_caffe_ffi.so` 3层，`libtvm_ffi.so` 4层
- **验证结果**：6次迭代，build 6成功，全新环境import+测试通过

### 场景2：其他pybind11/nanobind项目

- **适用场景**：任何使用 scikit-build-core + pybind11/nanobind 的 Conda 包
- **应用方式**：直接复用六步法，根据实际库位置调整RPATH深度
- **关键差异**：无跨包本地依赖时，可以省略步骤3（参数隔离）和跨包RPATH

### 场景3：跨领域——Rust/Cargo cdylib + conda

- **场景**：使用 maturin 构建 Rust 原生扩展的 Conda 包
- **迁移要点**：
  - 依赖分层规则同样适用（maturin 在 host 段）
  - RPATH `$ORIGIN` 规则同样适用
  - 参数隔离：CARGO_BUILD_RUSTFLAGS 等可能需要类似隔离
  - 符号验证：`nm -D` 检查 extern "C" 函数符号
- **待验证**：maturin 与 conda-build 的具体集成细节

### 场景4：跨领域——npm native node-gyp 插件打包（概念迁移）

- **类比**：node-gyp 原生插件也有依赖查找问题，Linux 下使用 RPATH
- **洞察**："构建参数隔离"、"相对路径可移植性"、"符号验证"三层防御思想可迁移到任何原生模块打包场景
- **迁移价值**：降低从 Python/Conda 迁移到其他原生打包场景的认知成本

## 待验证问题（升级L4需确认）

> 📌 **2026-07-30 更新（v1.3.0）**：
> - (1) macOS平台代码适配完成（`@loader_path`/`install_name_tool`/`otool -L`/`nm -gU`），待实机验证（A-T1）
> - (4) **conda-build 25.x/26.x 调研完成**（A-T6）：无scikit-build-core原生支持，但有6项兼容性注意事项
> - (5) **pyproject.toml三层分离完成**（A-T7）：CMake参数三层分离原则已确立并实践，build.sh SKBUILD_CMAKE_ARGS从12个精简为5个；待实机构建验证

1. **macOS支持**（代码适配完成，待实机验证）：`@loader_path`/`@rpath` 替代 `$ORIGIN` 的具体语法和深度计算是否一致？`install_name_tool` 替代 `patchelf` 的用法；`otool -L` 替代 `ldd`；`nm -gU` 替代 `nm -D`
2. **Windows支持**：Windows 下无 RPATH，依赖 PATH 环境变量，如何在 conda 包中正确设置？
3. **多架构支持**：aarch64/ppc64le 等非x86架构下patchelf和RPATH行为是否一致？
4. ~~**pyproject.toml配置**：是否可以通过pyproject.toml的`[tool.scikit-build]`配置部分cmake参数，减少build.sh中的手动操作？~~ ✅ **已解决（A-T7 v1.3.0）**：三层分离原则——项目默认值放`[tool.scikit-build.cmake.define]`，平台条件放`[[tool.scikit-build.overrides]]`，conda运行时参数保留在build.sh
5. **pyproject.toml配置的非conda构建验证**：直接`pip install .`（非conda环境）是否使用正确的默认CMake参数？构建产物是否可正常导入？

### conda-build版本兼容性矩阵

| conda-build版本 | 当前模式兼容性 | 需要的适配 |
|---|---|---|
| ≤24.x（当前使用版本） | ✅ 完全兼容 | 无 |
| 25.3.x | ✅ 兼容 | patchelf自动约束为<0.18，无需手动pin |
| 25.4.x-25.10.x | ✅ 兼容 | pip install选项可简化（非必须） |
| 25.11.x-26.0.x | ✅ 兼容 | Python ≥3.10；CMake 4兼容（当前CMake≥3.26即可） |
| 26.1.x-26.4.x | ✅ 兼容 | macOS RPATH更可靠（先删后加） |
| 26.5.x+ | ⚠️ 兼容（有deprecation warning） | 添加`missing_dso_allowlist`别名消除警告 |
| 27.3+ | ❌ 需适配 | `missing_dso_whitelist`移除，必须使用`missing_dso_allowlist` |

## Changelog

- **2026-07-30** (v1.3.0): A-T7 pyproject.toml三层分离实践完成：新增步骤1b"pyproject.toml三层分离配置CMake参数"；CMake参数按"项目默认值→平台条件→Conda运行时"三层分离；CMAKE_BUILD_RPATH_USE_ORIGIN从全局设置修正为Linux-only override；新增macOS override（CMAKE_MACOSX_RPATH/CMAKE_INSTALL_NAME_DIR）；build.sh SKBUILD_CMAKE_ARGS从12个精简为5个；待实机构建验证
- **2026-07-30** (v1.2.0): A-T6 conda-build 25.x/26.x兼容性调研完成：确认无scikit-build-core原生支持，新增conda-build版本兼容性矩阵；meta.yaml添加missing_dso_allowlist迁移注释
- **2026-07-30** (v1.1.0): ACT-004 代码适配阶段：build.sh添加macOS平台检测与跨平台工具函数封装（get_rpath/set_rpath/check_symbol/check_deps/fix_dep_ref），meta.yaml添加macOS条件依赖（cctools/llvm-openmp/macos-sdk）和.dylib DSO白名单；实机构建验证待执行
- **2026-07-30** (v1.0.0): 初始版本，从 caffe-ffi conda-build 6次迭代复盘萃取，双案例验证（主包+依赖包），标记 L3 方法论

## 与相关模式的关系

- **[conda-custom-channels-mirror.md](conda-custom-channels-mirror.md)**：本模式步骤0前的环境准备可能需要镜像源配置，依赖该模式
- **[shared-lib-symbol-dual-layer-control.md](shared-lib-symbol-dual-layer-control.md)**：本模式的符号验证是该模式的下游应用——编译时控制符号可见性，打包时验证符号完整性
- **[cmake-four-layer-modular-architecture.md](cmake-four-layer-modular-architecture.md)**：scikit-build-core底层调用CMake，CMake模块化架构有助于构建参数隔离

