---
title: "caffe-ffi Conda 构建：pip install 本地 tvm-ffi 集成方案 (AC-16)"
date: 2026-07-30
source:
  - projects/xuanspace/libs/caffe-ffi/conda.recipe/build.sh
  - projects/xuanspace/libs/caffe-ffi/conda.recipe/meta.yaml
  - projects/xuanspace/libs/caffe-ffi/cmake/Dependencies.cmake
  - projects/xuanspace/vendor/tvm-ffi/pyproject.toml
tags: [conda-build, caffe-ffi, tvm-ffi, ABI, pip-install, scikit-build-core]
status: "planning"
---

# caffe-ffi Conda 构建：pip install 本地 tvm-ffi 集成方案 - Product Requirement Document

## Overview

- **Summary**: 重构 caffe-ffi 的 Conda 构建流程，将 tvm-ffi 的获取方式从 "CMake add_subdirectory 编译 + 手动复制 .so" 改为 "pip install 本地 vendor 源码"，确保编译时和运行时使用同一份 libtvm_ffi.so，彻底解决 TVMFFIGetCustomAllocator 符号未定义的 ABI 兼容性问题。
- **Purpose**: 当前 Conda 构建中，CMake 通过 add_subdirectory 从本地 vendor 源码编译 tvm-ffi（包含最新 API 如 TVMFFIGetCustomAllocator），但运行时 Python 导入 tvm_ffi 时加载的是 pip 安装的 apache-tvm-ffi 0.1.12 wheel（缺少这些新符号），导致 _caffe_ffi.so 加载失败。问题的根本原因是编译时链接的 libtvm_ffi.so 与运行时加载的 libtvm_ffi.so 不是同一个文件。
- **Target Users**: caffe-ffi 开发者和 Conda 包用户（需要 native 功能可用的 Caffe FFI 绑定）。

## Goals

- **G1**: Conda 包中 caffe-ffi native 库能成功加载，无 undefined symbol 错误
- **G2**: 编译时和运行时使用同一份从本地 vendor 源码编译的 libtvm_ffi.so
- **G3**: 不再需要 build.sh 中复杂的 libtvm_ffi.so 搜索、复制、RPATH 修补逻辑
- **G4**: CMake 依赖查找使用标准 find_package(tvm_ffi CONFIG) 模式，而非 add_subdirectory
- **G5**: meta.yaml 的 test imports 能通过（包括 native 功能测试）
- **G6**: 保留非 Docker/非 SpecWeave 环境的回退能力（当本地 tvm-ffi 不存在时仍可通过 pip 安装）

## Non-Goals (Out of Scope)

- 不修改 tvm-ffi 本身的源码或构建系统（vendor 子模块只读）
- 不创建独立的 tvm-ffi Conda 包（保持 caffe-ffi 单包分发）
- 不解决 BLAS/OpenBLAS 未检测到的问题（属于独立问题）
- 不修改 Windows bld.bat 构建脚本（本次仅修复 Linux/macOS build.sh）
- 不更新 pip 发布的 apache-tvm-ffi 版本
- 不更改 caffe-ffi 的 Python API 或 C++ 代码

## Background & Context

### 当前构建流程与问题

当前 caffe-ffi Conda 构建流程：
1. meta.yaml 的 host/run 依赖不包含 tvm-ffi
2. build.sh 检测本地 vendor/tvm-ffi 源码路径
3. CMake Dependencies.cmake 通过 `add_subdirectory(vendor/tvm-ffi EXCLUDE_FROM_ALL)` 编译 tvm-ffi
4. caffe-ffi 链接到本地编译的 libtvm_ffi.so（含 TVMFFIGetCustomAllocator 等新符号）
5. `pip install . --no-deps` 构建 caffe-ffi wheel 并安装
6. build.sh 手动从 CMake build 目录搜索 libtvm_ffi.so 并复制到 $PREFIX/lib 和 _caffe_ffi.so 同级目录
7. build.sh 用 patchelf 修补 RPATH 为 $ORIGIN:$ORIGIN/lib:$PREFIX/lib

**问题**：步骤6虽然复制了正确的 libtvm_ffi.so 到正确位置，但运行时 Python 的加载顺序是：
1. `import tvm_ffi` → 加载 pip 安装的 apache-tvm-ffi 0.1.12 wheel 中的 libtvm_ffi.so（在 tvm_ffi/lib/ 下）
2. pip 版本的 libtvm_ffi.so 已加载到进程中，缺少 TVMFFIGetCustomAllocator
3. `tvm_ffi.load_module(_caffe_ffi.so)` → dlopen 发现 libtvm_ffi.so 已加载，直接复用 pip 版本
4. 符号解析失败 → undefined symbol

### 关键文件结构分析

- tvm-ffi pyproject.toml: `wheel.install-dir = "tvm_ffi"`，`wheel.packages = ["python/tvm_ffi"]`
- tvm-ffi CMakeLists.txt:
  - `install(TARGETS tvm_ffi_shared DESTINATION lib)` → 相对于 install-dir，即 `tvm_ffi/lib/libtvm_ffi.so`
  - `install(TARGETS tvm_ffi_cython DESTINATION .)` → `tvm_ffi/` 目录下
  - tvm_ffi_cython 的 RPATH 设置为 `$ORIGIN/lib`（正确指向自己的 lib/ 子目录）
- caffe-ffi 当前 Install.cmake: `install(TARGETS _caffe_ffi LIBRARY DESTINATION .)` → `caffe_ffi/_caffe_ffi.so`
- caffe-ffi pyproject.toml: `wheel.install-dir = "caffe_ffi"`

### 解决方案核心思路

在 build.sh 中**先**通过 pip 从本地 vendor 源码安装 tvm-ffi（非 editable），**再**构建 caffe-ffi。这使得：
1. tvm_ffi Python 包从本地源码安装（非 PyPI wheel），其 libtvm_ffi.so 包含所有需要的符号
2. CMake 通过 `python -m tvm_ffi.config --cmakedir` 找到已安装的 tvm-ffi CMake 配置
3. CMake 使用标准 find_package(tvm_ffi CONFIG) 链接，不需要 add_subdirectory
4. 运行时 import tvm_ffi 加载的就是正确版本的 libtvm_ffi.so
5. _caffe_ffi.so 的 RPATH 需要能找到 tvm_ffi/lib/ 目录下的 libtvm_ffi.so

## Functional Requirements

- **FR-1**: build.sh 在构建 caffe-ffi 之前，检测本地 tvm-ffi 源码并通过 pip install 安装到构建环境
- **FR-2**: 安装本地 tvm-ffi 时使用非 editable 模式（`pip install path/to/tvm-ffi --no-deps`），确保文件正确安装到 $PREFIX
- **FR-3**: Dependencies.cmake 在 tvm-ffi 已通过 pip 安装时，使用 find_package 模式而非 add_subdirectory 模式
- **FR-4**: build.sh 移除手动复制 libtvm_ffi.so 和复杂的多位置搜索逻辑
- **FR-5**: _caffe_ffi.so 的 RPATH 正确设置，能找到 tvm_ffi 包中的 libtvm_ffi.so（相对于 _caffe_ffi.so 的路径）
- **FR-6**: meta.yaml 更新，移除 run 依赖中对 pip 安装 apache-tvm-ffi 的隐式依赖，改为由 build.sh 在构建时安装本地 tvm-ffi 并打包
- **FR-7**: 当本地 tvm-ffi 源码不可用时（非 SpecWeave/Docker 环境），保留回退到 pip install apache-tvm-ffi 的能力
- **FR-8**: 构建完成后运行验证测试，确认 native 库加载成功且基本功能（Blob创建/填充）正常

## Non-Functional Requirements

- **NFR-1**: 构建时间不应显著增加（pip install tvm-ffi 从本地源码编译约增加 30-60 秒）
- **NFR-2**: Conda 包大小应保持合理（tvm-ffi Python 文件 + libtvm_ffi.so 约增加 3-4 MB）
- **NFR-3**: 构建脚本应保持健壮性，正确处理 pipefail 和错误退出
- **NFR-4**: RPATH 应使用相对路径（$ORIGIN），确保 Conda 包可在不同环境路径下重定位

## Constraints

- **Technical**: 
  - 不能修改 vendor/tvm-ffi 子模块（只读）
  - conda-build 环境中 $PREFIX 是安装目标前缀，$SP_DIR 是 site-packages
  - scikit-build-core 使用 wheel.install-dir 控制安装目录
  - Linux 动态链接器使用已加载库缓存，同名 .so 已加载后不会重新搜索
- **Business**: 需要保持向后兼容，非 SpecWeave 环境仍能构建
- **Dependencies**: scikit-build-core, cmake, ninja, patchelf, tvm-ffi (本地vendor源码)

## Assumptions

- tvm-ffi 的 pip install 从本地源码可以正常工作（其 pyproject.toml 使用 scikit-build-core + Cython 构建）
- tvm-ffi 安装后，`python -m tvm_ffi.config --cmakedir` 能正确返回 CMake 配置目录
- Conda 包中同时包含 tvm_ffi 和 caffe_ffi 两个包是可接受的（不创建独立的 tvm-ffi Conda 包）
- 本地 vendor/tvm-ffi 源码版本与 caffe-ffi 兼容（这也是当前 add_subdirectory 模式的前提）

## Acceptance Criteria

### AC-1: Conda 构建成功
- **Given**: 在 caffe-ffi-jupyter Docker 容器中
- **When**: 运行 conda build conda.recipe/
- **Then**: 构建成功完成，生成 .conda 包文件，Post-build RPATH/ldd 检查无错误
- **Verification**: `programmatic`
- **Notes**: 使用 full-clean-rebuild.sh 或 test-conda-build.sh 验证

### AC-2: tvm-ffi 从本地源码安装
- **Given**: Conda 构建过程中存在本地 vendor/tvm-ffi
- **When**: build.sh 执行
- **Then**: tvm_ffi Python 包从本地源码安装（不是从 PyPI wheel），其 libtvm_ffi.so 包含 TVMFFIGetCustomAllocator 符号
- **Verification**: `programmatic`
- **Notes**: 通过 nm -D 检查 $SP_DIR/tvm_ffi/lib/libtvm_ffi.so 中的符号

### AC-3: Native 库加载成功
- **Given**: Conda 包安装到干净的 conda 环境中
- **When**: 执行 `python -c "import caffe_ffi; print(caffe_ffi.is_available())"`
- **Then**: 输出 True，无 undefined symbol 错误，无 "Falling back to Python-only mode" 警告
- **Verification**: `programmatic`

### AC-4: 基本功能测试通过
- **Given**: Conda 包已安装
- **When**: 执行 `python -c "from caffe_ffi import Blob; b = Blob([100]); b.fill(1.0); print(b.count())"`
- **Then**: 输出 100，无错误
- **Verification**: `programmatic`

### AC-5: meta.yaml test 段通过
- **Given**: Conda 包构建完成
- **When**: conda-build 执行 test 阶段
- **Then**: 所有 test.imports 和 test.commands 通过
- **Verification**: `programmatic`

### AC-6: ldd 依赖全部解析
- **Given**: Conda 包已安装
- **When**: 运行 `ldd $SP_DIR/caffe_ffi/_caffe_ffi.so`
- **Then**: 所有共享库依赖（包括 libtvm_ffi.so）均已解析，无 "not found"
- **Verification**: `programmatic`

### AC-7: 回退模式保留
- **Given**: 构建环境中没有本地 vendor/tvm-ffi 源码
- **When**: build.sh 执行
- **Then**: 回退到 pip install apache-tvm-ffi 模式（当前行为），构建可完成（但可能缺少新API符号）
- **Verification**: `programmatic`
- **Notes**: 通过设置 CAFFE_FFI_TVM_FFI_DIR="" 并移除 vendor 路径来测试

### AC-8: RPATH 使用相对路径
- **Given**: Conda 包已安装
- **When**: 运行 `patchelf --print-rpath $SP_DIR/caffe_ffi/_caffe_ffi.so`
- **Then**: RPATH 包含 $ORIGIN 相对路径指向 tvm_ffi/lib/，不依赖绝对路径
- **Verification**: `programmatic`

## Open Questions

- [ ] tvm-ffi 从本地 pip install 时，是否需要禁用 Cython 编译的可选依赖（如 libbacktrace）？当前 build.sh 设置了 TVM_FFI_USE_LIBBACKTRACE=OFF，但通过 pip install 时需要通过环境变量或 CMake args 传递这些选项
- [ ] _caffe_ffi.so 需要什么样的 RPATH 才能找到 tvm_ffi/lib/libtvm_ffi.so？caffe_ffi/ 和 tvm_ffi/ 是 site-packages 下的同级目录，所以 $ORIGIN/../tvm_ffi/lib 应该可以
- [ ] meta.yaml 中是否需要将 tvm-ffi 声明为依赖？还是完全由 build.sh 处理？
- [ ] 构建 test-conda-build.sh 和 full-clean-rebuild.sh 是否需要相应更新？
