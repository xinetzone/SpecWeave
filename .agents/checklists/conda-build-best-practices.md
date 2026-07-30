---
title: "Conda 构建最佳实践检查清单"
date: 2026-07-30
source:
  - apps/caffe-ffi-jupyter/conda-build-verification-report.md
  - projects/xuanspace/libs/caffe-ffi/conda.recipe/
tags: [conda-build, checklist, best-practices, RPATH, OpenBLAS, scikit-build-core, editable]
status: "✅ 基于caffe-ffi build 5实践验证"
---

# Conda 构建最佳实践检查清单

> 基于 caffe-ffi Conda 包（build 5）构建修复经验总结。适用于使用 scikit-build-core + CMake + patchelf 的 Python C/C++ 扩展包构建。

---

## 📋 目录

- [1. meta.yaml 配置检查](#1-metayaml-配置检查)
- [2. build.sh 构建脚本检查](#2-buildsh-构建脚本检查)
- [3. RPATH 与共享库处理检查](#3-rpath-与共享库处理检查)
- [4. BLAS/数值库检测检查](#4-blas数值库检测检查)
- [5. pip install 集成检查](#5-pip-install-集成检查)
- [6. Editable 安装残留防护检查](#6-editable-安装残留防护检查)
- [7. Prefix Replacement 问题检查](#7-prefix-replacement-问题检查)
- [8. Conda-Build 测试检查](#8-conda-build-测试检查)
- [9. 多阶段环境清理检查](#9-多阶段环境清理检查)
- [10. 构建后验证检查清单](#10-构建后验证检查清单)

---

## 1. meta.yaml 配置检查

| # | 检查项 | 状态 | 说明与示例 |
|---|--------|------|-----------|
| 1.1 | **Build number 正确递增** | ☐ | 每次修改构建配置后必须递增 `build.number`，避免conda使用缓存的旧包 |
| 1.2 | **Python 版本约束正确** | ☐ | `skip: true  # [py<314]` 或对应版本限制 |
| 1.3 | **`detect_binary_files_with_prefix: false`** | ☐ | **关键**：当RPATH全部使用`$ORIGIN`相对路径时，必须设置此项禁用prefix路径扫描，避免"Placeholder too short"错误 |
| 1.4 | **`missing_dso_whitelist` 配置完整** | ☐ | 列出包内自带的共享库（如 `*/libtvm_ffi*.so*`, `*/libopenblas*.so*`），避免conda DSO检查误报 |
| 1.5 | **Host 依赖包含开发包** | ☐ | 数值库如OpenBLAS：host需同时包含运行时包(`libopenblas`)和开发包(`openblas`，提供头文件和`.so`符号链接)；run段仅需运行时包 |
| 1.6 | **Host 依赖包含构建工具** | ☐ | `cmake`, `ninja`, `patchelf`, `scikit-build-core`, `cython`, `setuptools-scm`, `typing-extensions` 等 |
| 1.7 | **Run 依赖完整性** | ☐ | 运行时需要的库（如`libopenblas`, `protobuf`, `numpy`）必须在run段列出 |
| 1.8 | **Test 段配置完整** | ☐ | 包含：①所有需要import的包（含内部依赖如tvm_ffi）；②功能测试commands；③requires必要测试依赖 |

**关键配置示例**：
```yaml
build:
  number: 5
  skip: true  # [py<314]
  detect_binary_files_with_prefix: false   # RPATHs are $ORIGIN-relative; no prefix replacement
  missing_dso_whitelist:
    - "*/libtvm_ffi*.so*"
    - "*/libopenblas*.so*"

requirements:
  host:
    - {{ compiler('cxx') }}
    - cmake>=3.26
    - ninja>=1.11
    - patchelf
    - scikit-build-core>=0.10.0
    - libopenblas      # 运行时库
    - openblas         # 开发包（头文件+libopenblas.so符号链接）
    - cython>=3.2.8
    - setuptools-scm
  run:
    - libopenblas      # 仅运行时库
```

---

## 2. build.sh 构建脚本检查

| # | 检查项 | 状态 | 说明与示例 |
|---|--------|------|-----------|
| 2.1 | **set -eux -o pipefail** | ☐ | 严格错误检查，避免静默失败 |
| 2.2 | **CRLF 修复处理** | ☐ | Windows/Docker挂载目录可能有CRLF换行符，需用`dos2unix`或`sed -i 's/\r$//'`修复 |
| 2.3 | **In-tree 构建残留清理** | ☐ | 构建前清理 `build/`, `_skbuild/`, `dist/`, `*.egg-info/` 目录 |
| 2.4 | **CMAKE_ARGS 隔离** | ☐ | pip install前临时清空conda的`CMAKE_ARGS`（包含`-DCMAKE_INSTALL_PREFIX=$PREFIX`等会干扰scikit-build-core wheel构建），安装后恢复 |
| 2.5 | **SKBUILD_CMAKE_ARGS 空格分隔** | ☐ | **注意**：CMake参数使用空格分隔，**不能用分号`;`**（会被CMake解析为列表分隔符导致参数错误） |
| 2.6 | **本地依赖优先安装** | ☐ | 对于vendor子模块依赖，先pip install本地源码确保版本一致，再构建主包 |
| 2.7 | **setuptools-scm 版本伪装** | ☐ | git submodule在Docker中可能无法正确describe版本，需设置`SETUPTOOLS_SCM_PRETEND_VERSION` |
| 2.8 | **CMake 选项关闭backtrace** | ☐ | 对于FFI库，设置`-DTVM_FFI_USE_LIBBACKTRACE=OFF -DTVM_FFI_BACKTRACE_ON_SEGFAULT=OFF`避免pytest环境下backtrace_symbols()崩溃 |
| 2.9 | **构建后patchelf RPATH修复** | ☐ | 见第3节 |
| 2.10 | **ldd 依赖验证** | ☐ | 构建后运行`ldd`检查是否有"not found"依赖 |
| 2.11 | **nm 符号验证** | ☐ | 对关键符号(如TVMFFIGetCustomAllocator)用`nm -D`验证为T类型（全局导出） |

---

## 3. RPATH 与共享库处理检查

| # | 检查项 | 状态 | 说明与示例 |
|---|--------|------|-----------|
| 3.1 | **优先使用 `$ORIGIN` 相对路径** | ☐ | **强制要求**：所有RPATH使用`$ORIGIN`相对路径，禁止绝对路径（避免prefix replacement问题） |
| 3.2 | **patchelf 可用检查** | ☐ | host依赖必须包含patchelf，build.sh中先`command -v patchelf`检查 |
| 3.3 | **主扩展SO的RPATH配置** | ☐ | 需包含：①`$ORIGIN`（同目录）；②`$ORIGIN/../<dep_pkg>/lib`（依赖包内库）；③`$ORIGIN/../../..`（上溯3级到PREFIX/lib） |
| 3.4 | **依赖SO的RPATH同步修复** | ☐ | **易错点**：不仅主SO需要修复，包内依赖SO（如tvm_ffi/lib/libtvm_ffi.so）也需要独立设置RPATH |
| 3.5 | **依赖SO的RPATH深度计算正确** | ☐ | 子目录的SO需要计算正确的上溯级数（如tvm_ffi/lib/下需要上溯4级：`$ORIGIN/../../../../`） |
| 3.6 | **patchelf前后打印RPATH** | ☐ | 修复前后都用`patchelf --print-rpath`打印，便于调试 |
| 3.7 | **RPATH解析验证** | ☐ | ldd检查关键依赖库是否通过RPATH正确解析到预期路径（如libtvm_ffi应解析到tvm_ffi/lib/而非PREFIX/lib） |

**RPATH 层级计算参考**（Python site-packages布局）：
```
site-packages/
├── caffe_ffi/
│   └── _caffe_ffi.so          ← 需要上溯3级到 PREFIX/lib
│       ├── $ORIGIN            → caffe_ffi/
│       ├── $ORIGIN/../tvm_ffi/lib → tvm_ffi/lib/
│       └── $ORIGIN/../../..   → lib/python3.14/site-packages/ → lib/python3.14/ → PREFIX/ → PREFIX/lib ✅
└── tvm_ffi/
    └── lib/
        └── libtvm_ffi.so      ← 需要上溯4级到 PREFIX/lib
            ├── $ORIGIN        → tvm_ffi/lib/
            ├── $ORIGIN/..     → tvm_ffi/
            └── $ORIGIN/../../../../ → lib/ → python3.14/ → PREFIX/ → PREFIX/lib ✅
```

**标准修复代码模板**：
```bash
# 主扩展SO
_caffe_so=$(find ... -name "_caffe_ffi*.so" | head -1)
NEW_RPATH="\$ORIGIN:\$ORIGIN/lib:\$ORIGIN/../tvm_ffi/lib:\$ORIGIN/../../.."
patchelf --set-rpath "$NEW_RPATH" "$_caffe_so"

# 依赖SO（在更深层级）
_dep_so="$SP_DIR/tvm_ffi/lib/libtvm_ffi.so"
_DEP_RPATH="\$ORIGIN:\$ORIGIN/..:\$ORIGIN/../../../../"
patchelf --set-rpath "$_DEP_RPATH" "$_dep_so"
```

---

## 4. BLAS/数值库检测检查

| # | 检查项 | 状态 | 说明与示例 |
|---|--------|------|-----------|
| 4.1 | **区分运行时包与开发包** | ☐ | conda-forge通常拆分为两个包：`libxxx`（仅版本化.so）和`xxx`（无lib前缀，提供头文件和libxxx.so符号链接）。host需同时安装两者 |
| 4.2 | **自定义Find模块命名** | ☐ | 自定义BLAS检测模块命名为`DetectBLAS.cmake`而非`FindBLAS.cmake`，避免与CMake内置模块递归冲突 |
| 4.3 | **两阶段搜索策略** | ☐ | Phase 1: 优先搜索conda路径（`HINTS` + `NO_DEFAULT_PATH`，收集CONDA_PREFIX/CMAKE_PREFIX_PATH/Python_SITEARCH父目录）；Phase 2: 失败回退系统默认路径（无NO_DEFAULT_PATH） |
| 4.4 | **库名包含变体** | ☐ | `NAMES openblas openblasp openblas.so.0`（pthreads变体、版本化soname） |
| 4.5 | **头文件搜索路径** | ☐ | `PATH_SUFFIXES include include/openblas`（cblas.h可能在openblas子目录） |
| 4.6 | **库路径包含lib64** | ☐ | `PATH_SUFFIXES lib lib64`（部分发行版使用lib64） |
| 4.7 | **失败诊断信息** | ☐ | 未找到时明确输出是缺头文件还是缺库文件，提示安装相应包 |
| 4.8 | **显式开关控制** | ☐ | 提供`-DCAFFE_USE_BLAS=ON/OFF`选项允许用户禁用BLAS（使用纯C++ fallback） |
| 4.9 | **构建日志验证** | ☐ | 构建日志中应看到`Found OpenBLAS: .../libopenblas.so`而非"not found"警告 |
| 4.10 | **ldd最终验证** | ☐ | 最终SO的ldd输出中应包含libopenblas（或对应BLAS库） |

**DetectBLAS.cmake 模板要点**：
```cmake
# 收集conda搜索路径
if(DEFINED ENV{CONDA_PREFIX})
  list(APPEND _blas_search_paths "$ENV{CONDA_PREFIX}")
endif()
list(APPEND _blas_search_paths ${CMAKE_PREFIX_PATH})

# Phase 1: conda定向搜索
find_path(OPENBLAS_INCLUDE_DIR
  NAMES cblas.h openblas_config.h
  HINTS ${_blas_search_paths}
  PATH_SUFFIXES include include/openblas
  NO_DEFAULT_PATH)
find_library(OPENBLAS_LIBRARY
  NAMES openblas openblasp openblas.so.0
  HINTS ${_blas_search_paths}
  PATH_SUFFIXES lib lib64
  NO_DEFAULT_PATH)

# Phase 2: 系统回退
if(NOT OPENBLAS_INCLUDE_DIR OR NOT OPENBLAS_LIBRARY)
  find_path(OPENBLAS_INCLUDE_DIR NAMES cblas.h PATH_SUFFIXES openblas)
  find_library(OPENBLAS_LIBRARY NAMES openblas openblasp blas)
endif()
```

---

## 5. pip install 集成检查

| # | 检查项 | 状态 | 说明与示例 |
|---|--------|------|-----------|
| 5.1 | **本地依赖优先pip install** | ☐ | 对于git submodule依赖，先`pip install <local_dir> --no-deps --no-build-isolation`确保编译和运行时版本一致 |
| 5.2 | **--no-build-isolation** | ☐ | 使用conda已安装的构建工具，避免pip重新下载创建隔离环境（版本不一致问题） |
| 5.3 | **--no-deps** | ☐ | 依赖由conda管理，避免pip重复安装 |
| 5.4 | **依赖安装前置CMAKE_ARGS清空** | ☐ | 安装本地依赖前清空`CMAKE_ARGS`，避免conda的CMAKE_INTERRUPT_ARGS干扰依赖的独立构建 |
| 5.5 | **Cython扩展编译开关** | ☐ | 依赖包含Cython扩展时，需通过`SKBUILD_CMAKE_ARGS=-DXXX_BUILD_PYTHON_MODULE=ON`确保扩展被编译 |
| 5.6 | **CMAKE_ARGS恢复** | ☐ | pip install后恢复原始CMAKE_ARGS（保存到_OLD_CMAKE_ARGS变量） |
| 5.7 | **安装后验证** | ☐ | pip install后立即验证`python -c "import dep_pkg; print(dep_pkg.__file__)"`确认从site-packages加载 |
| 5.8 | **find_package查找已安装依赖** | ☐ | 主包CMake优先通过`find_package(dep CONFIG REQUIRED)`查找pip安装的版本（而非add_subdirectory编译源码） |
| 5.9 | **Python cmakedir查找** | ☐ | 通过`python -m <dep_pkg>.config --cmakedir`获取CMake config路径，设置`<dep>_ROOT` |

**本地依赖pip安装模板**：
```bash
# 保存并清空CMAKE_ARGS
_OLD_CMAKE_ARGS="${CMAKE_ARGS:-}"
export CMAKE_ARGS="-DDEP_USE_LIBBACKTRACE=OFF -DDEP_BACKTRACE_ON_SEGFAULT=OFF"

# pip安装本地依赖
$PYTHON -m pip install "${LOCAL_DEP_DIR}" --no-deps -vv --no-build-isolation

# 清理editable文件（见第6节）

# 恢复CMAKE_ARGS
if [ -n "$_OLD_CMAKE_ARGS" ]; then
    export CMAKE_ARGS="$_OLD_CMAKE_ARGS"
else
    unset CMAKE_ARGS
fi
```

---

## 6. Editable 安装残留防护检查

| # | 检查项 | 状态 | 说明与示例 |
|---|--------|------|-----------|
| 6.1 | **认识问题** | ☐ | scikit-build-core在`--no-build-isolation`模式下，可能错误为非editable安装生成`_editable_skbc_*.pth`和`.py` finder文件，导致Python优先从源码目录加载 |
| 6.2 | **三重防护清理策略** | ☐ | 必须在三个时机都进行清理：pre-build（构建前）、build.sh内（每次pip install后）、post-install（conda install后） |
| 6.3 | **Pre-build 彻底清理** | ☐ | 构建前遍历所有site-packages，删除`_editable_*`、`__editable__*`，以及包含源码路径(xuanspace/SpecWeave)的.pth文件 |
| 6.4 | **build.sh 内每次pip install后清理** | ☐ | pip install tvm-ffi和pip install caffe-ffi后都要立即清理finder文件 |
| 6.5 | **Post-install 兜底清理** | ☐ | **易错点**：conda install后仍可能有钩子重新生成editable文件，必须在conda install后再次清理 |
| 6.6 | **使用find而非ls glob** | ☐ | set -e环境下ls glob无匹配会失败，使用`find ... -maxdepth 1 \( -name "_editable_*" -o -name "__editable__*" \) -type f -delete` |
| 6.7 | **覆盖所有site-packages** | ☐ | 使用`python -c "import site; print(' '.join(site.getsitepackages()))"`获取所有site-packages路径，包括SP_DIR |

**标准清理代码模板**：
```bash
# Editable文件清理函数
clean_editable() {
  for _sp in $($PYTHON -c "import site; print(' '.join(site.getsitepackages()))" 2>/dev/null) "${SP_DIR:-}"; do
    if [ -n "$_sp" ] && [ -d "$_sp" ]; then
      find "$_sp" -maxdepth 1 \( -name "_editable_*" -o -name "__editable__*" \) -type f -delete 2>/dev/null || true
      # 额外清理指向源码路径的.pth文件
      find "$_sp" -maxdepth 1 -name "*.pth" -type f 2>/dev/null | while read f; do
        if grep -q "xuanspace\|SpecWeave\|build\|_skbuild" "$f" 2>/dev/null; then
          rm -f "$f"
        fi
      done
    fi
  done
}
```

---

## 7. Prefix Replacement 问题检查

| # | 检查项 | 状态 | 说明与示例 |
|---|--------|------|-----------|
| 7.1 | **认识问题根因** | ☐ | conda-build默认扫描二进制文件中的构建路径，替换为占位符（默认80字符）。RPATH含绝对路径时，长路径会导致"Placeholder of length '80' too short" |
| 7.2 | **根本解决方案：全相对RPATH** | ☐ | **首选**：所有RPATH使用`$ORIGIN`相对路径（见第3节），无需路径替换 |
| 7.3 | **禁用prefix检测** | ☐ | meta.yaml设置`detect_binary_files_with_prefix: false`，明确告诉conda-build不需要路径替换 |
| 7.4 | **备选方案：增大prefix_length** | ☐ | 如必须用绝对路径，可增大`--prefix-length 128`或在meta.yaml设置`build/prefix_length: 128`，但不推荐 |
| 7.5 | **避免绝对路径** | ☐ | SKBUILD_CMAKE_ARGS中CMAKE_INSTALL_RPATH禁止使用`${PREFIX}/lib`绝对路径，改用`$ORIGIN/../../..`相对路径 |
| 7.6 | **多SO统一处理** | ☐ | 记住：包内所有SO都需要处理，不只是主扩展 |
| 7.7 | **构建验证无placeholder警告** | ☐ | 构建日志不应出现"Placeholder too short"或"binary files with prefix"相关警告 |

---

## 8. Conda-Build 测试检查

| # | 检查项 | 状态 | 说明与示例 |
|---|--------|------|-----------|
| 8.1 | **test/imports 包含所有依赖** | ☐ | 不仅测试主包，还要测试内部依赖包（如tvm_ffi） |
| 8.2 | **test/commands 功能测试** | ☐ | 包含：版本检查、native可用性检查、基础功能测试（如Blob创建） |
| 8.3 | **conda-build --test 指定channel** | ☐ | **易错点**：`conda-build --test`默认不继承构建时的channel，必须显式添加`-c conda-forge` |
| 8.4 | **conda-build --test 传入包文件路径** | ☐ | **易错点**：必须传入构建好的`.conda`/`.tar.bz2`文件路径，而非recipe目录（否则报"info/index.json not found"） |
| 8.5 | **测试命令退出码正确** | ☐ | 测试脚本失败时返回非零退出码，让conda-build正确标记测试失败 |
| 8.6 | **测试在/tmp目录运行** | ☐ | 手动验证时`cd /tmp`避免cwd源码目录shadowing site-packages包 |

**conda-build --test 正确用法**：
```bash
# 错误：传入recipe目录
# conda-build --test path/to/recipe  # ❌

# 正确：传入.conda包文件 + 指定channel
_PKG=$(find "$CONDA_PREFIX/conda-bld/linux-64" -name "pkg-*.conda" | sort -V | tail -1)
conda-build --test -c conda-forge "$_PKG"  # ✅
```

---

## 9. 多阶段环境清理检查

| # | 检查项 | 阶段 | 说明 |
|---|--------|------|------|
| 9.1 | 旧conda包卸载 | Pre-build | `conda remove -y pkgname` + `pip uninstall -y pkgname` |
| 9.2 | conda-bld目录清理 | Pre-build | `rm -rf $CONDA_PREFIX/conda-bld` |
| 9.3 | conda包缓存清理 | Pre-build | `conda clean -y --packages` + `rm -rf $CONDA_PREFIX/pkgs/pkgname-*` |
| 9.4 | site-packages残留目录 | Pre-build | 删除site-packages下的pkg目录和*.dist-info |
| 9.5 | PREFIX/lib残留SO | Pre-build | `rm -f $PREFIX/lib/libpkgname*`（手动复制的SO） |
| 9.6 | Editable finder文件 | Pre-build/build.sh/post-install | 见第6节三重防护 |
| 9.7 | In-tree构建残留 | Pre-build | 源码目录下的build/, _skbuild/, dist/, *.egg-info/ |
| 9.8 | CRLF换行符 | Pre-build | dos2unix或sed修复所有文本文件 |
| 9.9 | Post-install兜底清理 | Post-conda-install | conda install后再次清理editable文件 |

---

## 10. 构建后验证检查清单

构建完成后，**必须逐项验证**以下内容：

### 10.1 包加载路径验证
```bash
cd /tmp  # 关键：避免cwd源码目录干扰
python -c "
import pkgname
import dep_pkg
import os
pkg_file = pkgname.__file__
dep_file = dep_pkg.__file__
assert 'site-packages' in pkg_file, f'pkg from wrong path: {pkg_file}'
assert 'site-packages' in dep_file, f'dep from wrong path: {dep_file}'
print('✓ Packages loading from site-packages')
"
```

### 10.2 Native/Runtime可用性验证
```bash
python -c "
import pkgname
assert pkgname._ffi_api.is_available(), 'Native not available!'
print('✓ Native available: True')
"
```

### 10.3 核心功能测试
```bash
python -c "
from pkgname import CoreClass
import numpy as np
obj = CoreClass([100])
obj.fill(1.0)
assert obj.count() == 100
data = obj.to_numpy()
assert np.allclose(data, 1.0)
print('✓ Core functionality test passed')
"
```

### 10.4 RPATH验证
```bash
_SO=$(python -c "import pkgname, glob, os; print(glob.glob(os.path.join(os.path.dirname(pkgname.__file__), '_pkgname*.so'))[0])")
echo "RPATH: $(patchelf --print-rpath $_SO)"
# 验证：RPATH中无绝对路径，全部是$ORIGIN开头
patchelf --print-rpath $_SO | grep -q '\$ORIGIN' && echo "✓ RPATH uses \$ORIGIN relative paths"
! patchelf --print-rpath $_SO | grep -q '/opt/conda' && echo "✓ RPATH contains no absolute paths"
```

### 10.5 依赖解析验证（ldd）
```bash
echo "=== ldd output ==="
ldd $_SO
# 检查1：无"not found"
if ldd $_SO | grep -q 'not found'; then
  echo "✗ UNRESOLVED DEPENDENCIES!"
  ldd $_SO | grep 'not found'
  exit 1
fi
echo "✓ All shared library dependencies resolved"

# 检查2：关键依赖路径正确（如libtvm_ffi应解析到tvm_ffi/lib/）
if ldd $_SO | grep libtvm_ffi | grep -q 'tvm_ffi/lib'; then
  echo "✓ libtvm_ffi correctly resolved to tvm_ffi/lib/"
fi

# 检查3：BLAS库已链接（如适用）
if ldd $_SO | grep -qi openblas; then
  echo "✓ OpenBLAS linked - BLAS acceleration enabled"
else
  echo "⚠ No BLAS library linked (pure C++ fallback)"
fi
```

### 10.6 ABI符号验证
```bash
_DEP_SO=$(python -c "import dep_pkg, os; print(os.path.join(os.path.dirname(dep_pkg.__file__), 'lib', 'libdep.so'))")
if nm -D $_DEP_SO | grep -q " T RequiredSymbol"; then
  echo "✓ Required ABI symbol found (T type)"
else
  echo "✗ Required ABI symbol NOT found!"
  exit 1
fi
```

### 10.7 Conda包测试
```bash
conda-build --test -c conda-forge /path/to/package-*.conda
echo "✓ Conda package tests passed"
```

---

## 🔧 常见问题速查表

| 错误信息 | 根因 | 解决方案 |
|----------|------|----------|
| `Placeholder of length '80' too short` | RPATH含绝对构建路径 | 改用`$ORIGIN`相对RPATH + `detect_binary_files_with_prefix: false` |
| `undefined symbol: TVMFFIGetCustomAllocator` | 编译时和运行时tvm-ffi版本不一致 | pip install本地vendor源码，确保版本一致 |
| `ImportError: cannot import name 'core'` | Cython扩展未编译 | SKBUILD_CMAKE_ARGS添加`-DXXX_BUILD_PYTHON_MODULE=ON` |
| `package loading from source directory, not site-packages` | editable .pth文件残留 | 三重防护清理（pre/build/post） |
| `Could NOT find OpenBLAS` | 缺开发包或搜索路径不对 | host添加`openblas`包 + 两阶段DetectBLAS.cmake |
| `info/index.json not found` | conda-build --test传入了recipe目录 | 传入.conda包文件路径 |
| `Could not solve for environment` (conda test) | conda-build --test缺少channel | 添加`-c conda-forge`参数 |
| `Some shared libraries not found` (ldd) | RPATH设置错误或缺少依赖 | patchelf修复RPATH + meta.yaml run段补全依赖 |
| CMake arguments parsed incorrectly (list issue) | SKBUILD_CMAKE_ARGS用分号分隔 | 改用空格分隔CMake参数 |

---

## 📁 相关文件参考

本次实践的完整代码参考：
- 构建脚本：[build.sh](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/conda.recipe/build.sh)
- 元数据：[meta.yaml](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/conda.recipe/meta.yaml)
- BLAS检测：[DetectBLAS.cmake](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/cmake/DetectBLAS.cmake)
- 完整验证脚本：[full-clean-rebuild.sh](file:///d:/spaces/SpecWeave/apps/caffe-ffi-jupyter/scripts/full-clean-rebuild.sh)
- 验证报告：[conda-build-verification-report.md](file:///d:/spaces/SpecWeave/apps/caffe-ffi-jupyter/conda-build-verification-report.md)
