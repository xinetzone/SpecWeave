---
title: "caffe-ffi Conda 包构建验证复盘"
version: "1.0"
date: 2026-07-30
type: task-retrospective
scope: milestone
source: "apps/caffe-ffi-jupyter/scripts/test-conda-build.sh + projects/xuanspace/libs/caffe-ffi/conda.recipe/"
tags: ["conda-build", "scikit-build-core", "cmake", "rpath", "patchelf", "python-packaging", "tvm-ffi", "caffe-ffi"]
status: completed
---

# caffe-ffi Conda 包构建验证复盘

## 执行摘要

本次任务完成了 caffe-ffi（基于 tvm-ffi 的 Caffe 深度学习框架 FFI 绑定库）的 Conda 包构建、验证与 RPATH 依赖解析闭环。构建产物 `caffe-ffi-0.1.0-py314h2bc3f7f_0.conda`（1.09MB）在 Docker 容器内的干净 conda 环境中通过全部验证：导入成功、Blob 功能正常、所有共享库依赖通过 ldd 解析无 not found、libtvm_ffi.so 正确链接。构建过程中修复了 5 个关键问题，修改 4 个核心文件，萃取 2 个可复用模式。

### 关键结果

| 指标 | 结果 |
|------|------|
| Conda 包产物 | `caffe-ffi-0.1.0-py314_0.conda`（1.09MB） |
| 构建耗时 | ~1分35秒 |
| Docker 容器 | `caffe-ffi-jupyter`（基于 jupyter-ssh-base:1.1） |
| Conda 环境 | caffe-ffi（Python 3.14, Conda-Forge） |
| 修复问题 | 5 个（build backend缺失、路径双重嵌套、CRLF、conda-verify不兼容、editable残留） |
| 修改文件 | 4 个核心文件 |
| ldd 验证 | ✅ 所有依赖解析，无 not found |
| RPATH 验证 | ✅ `$ORIGIN:$ORIGIN/lib:$ORIGIN/../../..` 正确设置 |
| 功能测试 | ✅ import/Blob.fill/Blob.from_numpy 全部通过 |

---

## S1 事实还原

### 时间线与关键事件

| 阶段 | 关键事件 | 结果 |
|------|---------|------|
| 阶段1：脚本执行 | 在 Docker 容器内执行 test-conda-build.sh | 脚本路径错误：从 /SpecWeave 挂载路径执行而非预装路径 |
| 阶段2：CRLF修复 | NTFS 挂载导致 shell 脚本 CRLF 行尾问题 | 使用 `sed -i 's/\r$//'` 批量修复 .sh/.cmake/.py 文件 |
| 阶段3：conda镜像 | 清华 TUNA 镜像连接超时 | 重置 conda config 使用 conda-forge 官方源 |
| 阶段4：conda-verify | conda-verify 与 Python 3.14 不兼容 | 安装 conda-build 时跳过 conda-verify；脚本中跳过 conda-verify 步骤 |
| 阶段5：conda-build命令 | `conda build` 子命令不存在（conda>=24.x 已移除） | 修改为直接调用 `conda-build` 命令 |
| 阶段6：BackendUnavailable | `--no-build-isolation` 导致 scikit-build-core 找不到 | 将 scikit-build-core/cmake/ninja/patchelf 加入 meta.yaml host requirements |
| 阶段7：双重嵌套路径 | CMake install DESTINATION=caffe_ffi 与 wheel.install-dir 叠加 | Install.cmake DESTINATION 改为 "."，避免 caffe_ffi/caffe_ffi/ |
| 阶段8：editable残留 | pip editable install 的 .pth 文件导致 Python 加载源码而非 conda 包 | 删除 _editable_skbc_*.pth 文件 + conda install --force-reinstall |
| 阶段9：ldd验证 | 修复后 _caffe_ffi.so 和 libtvm_ffi.so ldd 无 not found | 所有依赖通过 RPATH 正确解析 |

### 修改文件清单

| 文件 | 修改内容 | 行数变化 |
|------|---------|---------|
| [conda.recipe/meta.yaml](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/conda.recipe/meta.yaml) | 将 scikit-build-core/cmake/ninja/patchelf 从 build 移至 host requirements | +6/-0 |
| [conda.recipe/build.sh](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/conda.recipe/build.sh) | 增加 vendor tvm-ffi build 目录搜索；find\|grep 管道添加 `\|\| true` 防 pipefail | +6/-0 |
| [cmake/Install.cmake](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/cmake/Install.cmake) | DESTINATION 从 "caffe_ffi" 改为 "."，添加注释说明双重嵌套原因 | +4/-2 |
| [scripts/test-conda-build.sh](file:///d:/spaces/SpecWeave/apps/caffe-ffi-jupyter/scripts/test-conda-build.sh) | 跳过 conda-verify；conda build → conda-build；recipe 验证改为 YAML parse；typo修复(data_tenso→data_tensor) | +15/-8 |

### Bug 修复记录

| # | 问题现象 | 根因 | 修复方案 |
|---|---------|------|---------|
| 1 | `BackendUnavailable: Cannot import 'scikit_build_core.build'` | conda-build 使用 `--no-build-isolation` 时，pip 不创建隔离环境，build requirements 中的包不在安装环境中可用 | 将 scikit-build-core、cmake、ninja、patchelf 从 `build` 段移至 `host` 段 |
| 2 | 安装后 `_caffe_ffi.so` 位于 `caffe_ffi/caffe_ffi/_caffe_ffi.so`（双重嵌套） | scikit-build-core 的 `wheel.install-dir="caffe_ffi"` 设置 CMAKE_INSTALL_PREFIX 为 `caffe_ffi/`，而 CMake install DESTINATION 又指定了 `caffe_ffi`，导致路径叠加 | CMake install DESTINATION 改为 "."，相对于 install-dir 安装 |
| 3 | conda-verify 与 Python 3.14 不兼容导致安装失败 | conda-verify 尚未适配 Python 3.14（2026-07 时点） | 安装 conda-build 时跳过 conda-verify 依赖；脚本中跳过 conda-verify 步骤 |
| 4 | `conda: error: argument COMMAND: invalid choice: 'build'` | conda >= 24.x 将 `conda build` 子命令拆分为独立 `conda-build` 命令 | 脚本中 `conda build` → `conda-build` |
| 5 | Python `import caffe_ffi` 加载源码目录而非 conda 安装包 | 之前的 pip editable install 留下了 `_editable_skbc_caffe_ffi.pth` 文件，覆盖了 site-packages 中的 conda 包 | 删除 .pth 文件后 `conda install --force-reinstall` |

### 构建产物结构

```
site-packages/caffe_ffi/
├── __init__.py              # Python 包入口
├── _core.py                 # 核心绑定
├── _ffi_api.py              # FFI API层
├── _caffe_ffi.cpython-314-x86_64-linux-gnu.so  # C++ 编译扩展
│   └── RPATH: $ORIGIN:$ORIGIN/lib:$ORIGIN/../../..
├── libtvm_ffi.so            # tvm-ffi 运行库（bundled）
│   └── RPATH: $ORIGIN/../../..:$ORIGIN:$ORIGIN/lib
├── caffe_pb2.py             # protobuf 生成代码
├── blob.py, io.py, layer.py, net.py
├── caffe/                   # Caffe 子模块
└── tools/                   # 工具模块
```

### ldd 验证结果

**`_caffe_ffi.so` 依赖解析**：
- libtvm_ffi.so → `$ORIGIN/libtvm_ffi.so`（同目录，通过 `$ORIGIN` RPATH）✅
- libprotobuf.so.35.1.0 → conda 环境 lib ✅
- libopenblas.so.0 → conda 环境 lib ✅
- libstdc++.so.6 / libm.so.6 / libgcc_s.so.1 / libc.so.6 / ld-linux-x86-64.so.2 → 系统/conda 基础库 ✅
- libabsl_*（abseil 系列库）→ conda 环境 lib ✅
- **not found 依赖：无** ✅

**`libtvm_ffi.so` 依赖解析**：
- 仅依赖基础系统库：libstdc++.so.6, libm.so.6, libgcc_s.so.1, libc.so.6, libdl.so.2
- **not found 依赖：无** ✅

---

## S2 过程分析

### 成功因素

1. **Docker 容器复用**：使用已运行的 `caffe-ffi-jupyter` 容器而非每次启动新容器，保持 conda 环境缓存，大幅加速迭代
2. **test-conda-build.sh 全流程自动化**：脚本涵盖环境检查→CRLF修复→依赖安装→构建→安装→功能验证→ldd检查→包信息输出，一键完成
3. **RPATH 三层设计**：`$ORIGIN`（同目录找 libtvm_ffi.so）、`$ORIGIN/lib`（子目录）、`$ORIGIN/../../..`（conda 环境 lib）三层相对路径，无需设置 LD_LIBRARY_PATH
4. **build.sh tvm-ffi 多路径搜索**：SP_DIR→PREFIX→CMake build 目录→vendor tvm-ffi build 目录，5级搜索确保 libtvm_ffi.so 在各种构建模式下都能找到
5. **patchelf 后置修复**：构建完成后用 patchelf 设置 RPATH 并执行 ldd 验证，确保不遗漏任何 not found 依赖

### 问题根因分析（5-Whys）

**核心问题：conda-build 构建 scikit-build-core 项目时 BackendUnavailable**

- Why 1? → pip 找不到 `scikit_build_core.build` 模块
  - Why 2? → `--no-build-isolation` 禁用了 pip 的构建隔离环境
    - Why 3? → build requirements 中的 scikit-build-core 仅在 build 隔离环境中可用
      - Why 4? → conda-build 将 build requirements 安装到构建环境（build env），但 `--no-build-isolation` 使 pip 在 host 环境中查找构建后端
        - Why 5? → meta.yaml 中 build/host requirements 的职责区分不清：build 用于编译器工具链，host 用于 Python 构建后端和链接库

**根因**：conda-build 的三段式 requirements（build/host/run）语义与 pip 的 build isolation 存在交互。当使用 `--no-build-isolation`（scikit-build-core 必需）时，Python 构建后端（scikit-build-core、cmake、ninja）必须在 host requirements 中声明，而非仅在 build requirements 中。

**另一问题：CMake install 路径双重嵌套**

- Why 1? → 安装后 `_caffe_ffi.so` 在 `caffe_ffi/caffe_ffi/_caffe_ffi.so`
  - Why 2? → scikit-build-core 设置 `wheel.install-dir="caffe_ffi"` 使 CMAKE_INSTALL_PREFIX 指向 `caffe_ffi/`
    - Why 3? → Install.cmake 中 `DESTINATION caffe_ffi` 是相对于 CMAKE_INSTALL_PREFIX 的路径
      - Why 4? → 两个 "caffe_ffi" 叠加导致双重嵌套

**根因**：scikit-build-core 的 `wheel.install-dir` 会改变 CMAKE_INSTALL_PREFIX，CMake install 规则中的 DESTINATION 必须相对于 install-dir 而非 site-packages 根目录。这是 scikit-build-core 与裸 CMake 的关键区别。

### 瓶颈与约束

| 瓶颈/约束 | 影响 | 应对 |
|----------|------|------|
| Python 3.14 生态成熟度 | conda-verify 等包尚未适配，conda-forge 部分包可能缺失 | 跳过不兼容工具，使用 `--no-deps` 安装核心包 |
| NTFS 挂载 CRLF 问题 | Windows 宿主机上编辑的脚本在 Linux 容器内执行失败 | 构建脚本自动检测并修复 CRLF |
| conda-build build/host/run 三段式 | 容易混淆各段职责，特别是 --no-build-isolation 时 | host 段必须包含所有 Python 构建后端 |
| editable install 残留 | .pth 文件干扰干净环境验证 | 验证前显式清理 .pth 并 force-reinstall |

---

## S3 洞察与模式萃取

### 洞察 1：conda-build + scikit-build-core 三段式依赖管理模型

**现象陈述**：使用 conda-build 构建 scikit-build-core 项目时，若 build.sh 中使用 `pip install --no-build-isolation`，则 scikit-build-core、cmake、ninja 等构建后端必须放在 host requirements 而非仅放在 build requirements。

**证据（事实编号引用）**：
- Bug #1：最初 scikit-build-core 在 build requirements 中，导致 BackendUnavailable
- 修复：将 scikit-build-core/cmake/ninja/patchelf 移至 host requirements 后构建成功
- build.sh 使用 `pip install . --no-deps -vv --no-build-isolation`

**反常识**：直觉上"构建工具"应该放在 build requirements，但 conda-build 的 build 段仅用于编译器工具链（gcc、cmake 二进制本身），Python 构建后端在 `--no-build-isolation` 模式下必须通过 host 段提供到 host 环境中。

**下次行动**：编写 conda recipe 时遵循以下规则：
- `build`：C/C++ 编译器（`{{ compiler('cxx') }}`）、make 等系统构建工具
- `host`：Python、pip、Python 构建后端（scikit-build-core、setuptools）、链接库（libprotobuf、numpy headers）、CMake/Ninja 二进制
- `run`：运行时 Python 依赖（不包括构建工具）

### 洞察 2：scikit-build-core wheel.install-dir 与 CMake install DESTINATION 的叠加规则

**现象陈述**：scikit-build-core 的 `wheel.install-dir` 配置会设置 CMAKE_INSTALL_PREFIX，CMake install() 中的 DESTINATION 是相对于该前缀的，不能重复包名目录。

**证据**：
- Bug #2：`wheel.install-dir="caffe_ffi"` + `install(TARGETS _caffe_ffi LIBRARY DESTINATION caffe_ffi)` → `caffe_ffi/caffe_ffi/_caffe_ffi.so`
- 修复：DESTINATION 改为 "." → 正确安装到 `caffe_ffi/_caffe_ffi.so`

**反常识**：裸 CMake 项目中 DESTINATION 通常是相对于 CMAKE_INSTALL_PREFIX 的完整子路径（如 `lib/`、`bin/`），但 scikit-build-core 已经通过 wheel.install-dir 处理了包目录前缀，CMake install 规则应该相对于该前缀使用 "." 或子目录名。

**下次行动**：在 scikit-build-core 项目中，CMake install(TARGETS) 的 DESTINATION 使用 "." 时对应 wheel.install-dir 指定的包目录；若需要安装到子目录，使用 "lib/"、"bin/" 等相对于包目录的路径。

### 洞察 3：Editable Install 残留对 Conda 包验证的干扰

**现象陈述**：开发环境中 `pip install -e .`（editable install）创建的 `.pth` 文件会在 conda install 后仍然生效，导致 Python 加载源码目录而非 conda 包。

**证据**：
- Bug #5：conda install caffe-ffi 后 `import caffe_ffi` 加载的是源码目录而非 site-packages/caffe_ffi/
- 原因：`_editable_skbc_caffe_ffi.pth` 文件残留
- 修复：删除 .pth 文件 + `conda install --force-reinstall`

**反常识**：`pip uninstall caffe-ffi` 不会删除所有 .pth 文件（特别是 scikit-build-core 生成的 `_editable_skbc_*.pth`），conda install 也不会清理不属于自己包的 .pth 文件。这些残留文件优先级高于正常 site-packages 包。

**下次行动**：验证 conda 包前必须执行：
1. `pip uninstall -y <package>` 卸载 pip 安装版本
2. 手动查找并删除 `site-packages/_editable_*.pth` 文件
3. `conda install --force-reinstall <package>` 强制覆盖安装
4. 用 `python -c "import <package>; print(<package>.__file__)"` 确认加载路径

### 模式 1：conda-build + scikit-build-core 原生扩展打包模式

**触发场景**：需要将 C++/CMake 构建的 Python 原生扩展打包为 Conda 包，依赖 scikit-build-core 构建系统，且需要捆绑 vendored C++ 共享库（如 libtvm_ffi.so）。

**核心步骤**：
1. **meta.yaml 三段式依赖**：
   - build：`{{ compiler('cxx') }}`、patchelf
   - host：python、pip、scikit-build-core、cmake、ninja、patchelf、C++ 依赖库（-dev 包）、numpy、cython
   - run：python、运行时依赖（不含构建工具）
2. **build.sh 关键配置**：
   - `pip install . --no-deps --no-build-isolation`（必须 --no-build-isolation）
   - CMAKE_INSTALL_RPATH 使用 `$ORIGIN:$ORIGIN/lib` 相对路径
   - CMAKE_INSTALL_RPATH_USE_LINK_PATH=ON（自动添加链接库路径）
3. **vendored 库捆绑**：
   - 构建后多路径搜索 vendored .so（SP_DIR → PREFIX → CMake build → vendor build）
   - 复制到 `$SP_DIR/<package>/` 目录（供 `$ORIGIN` RPATH 查找）
   - 同时复制到 `$PREFIX/lib/`（conda 标准库路径）
4. **patchelf RPATH 设置**：`$ORIGIN:$ORIGIN/lib:$PREFIX/lib`
5. **ldd 验证**：构建后立即执行 ldd 检查 not found 依赖

**反模式**：
- ❌ 将 scikit-build-core/cmake/ninja 仅放在 build requirements（--no-build-isolation 时找不到）
- ❌ CMake install DESTINATION 重复包名目录（与 wheel.install-dir 叠加导致双重嵌套）
- ❌ 忘记将 vendored .so 复制到包目录（$ORIGIN 找不到）
- ❌ 仅依赖 LD_LIBRARY_PATH 而不设置 RPATH（conda 环境不应依赖全局 LD_LIBRARY_PATH）

**成熟度**：L2（已在 caffe-ffi 项目端到端验证，ldd 全部解析通过）

### 模式 2：Conda 构建验证干净环境前置清理模式

**触发场景**：在开发 Docker 容器中验证 conda 包构建结果，容器内可能存在之前的 editable install 或 pip install 残留。

**核心步骤**：
1. **清理 pip 版本**：`pip uninstall -y <package>`（可能需要多次）
2. **清理 .pth 残留**：
   ```bash
   find "$SP_DIR" -name "_editable_*.pth" -delete 2>/dev/null || true
   find "$SP_DIR" -name "__editable__.*.pth" -delete 2>/dev/null || true
   ```
3. **强制重装 conda 包**：`conda install -y --offline --use-local --force-reinstall <package>`
4. **验证加载路径**：`python -c "import <pkg>; print(<pkg>.__file__)"` 确认路径在 `site-packages/<pkg>/` 下
5. **ldd 检查**：定位 .so 文件后执行 `ldd` 并 grep "not found"
6. **功能测试**：import → 核心功能（Blob/Array等）→ 数据传输（numpy互操作）

**反模式**：
- ❌ 直接 `conda install` 而不清理 pip 版本（.pth 文件残留导致加载错误路径）
- ❌ 仅验证 import 成功而不验证 `__file__` 路径（可能加载了源码目录）
- ❌ 跳过 ldd 检查（运行时才发现缺失依赖）

**成熟度**：L2（已在 caffe-ffi 验证中验证，清理后 import 路径正确）

---

## S4 改进行动项

| ID | 行动项 | 优先级 | 验收标准 | 类型 |
|----|--------|--------|---------|------|
| ACT-001 | build.sh 增加 `_editable_*.pth` 自动清理步骤，在 conda install 前执行 | 高 | 验证脚本在有 editable 残留的环境中也能正确验证 conda 包 | 质量门禁 |
| ACT-002 | 在 meta.yaml 中增加 `missing_dso_whitelist` 的详细注释，说明哪些库是 vendored/bundled | 中 | 其他开发者阅读 meta.yaml 能理解 DSO 白名单的用途 | 文档 |
| ACT-003 | 考虑将 RPATH `$ORIGIN/../../..` 改为 conda-build 标准的 `$PREFIX/lib` 绝对路径（构建时替换） | 中 | 构建后 RPATH 不依赖 conda-build 的自动重定位也能正确工作 | 健壮性 |
| ACT-004 | 为 caffe-ffi conda recipe 增加 macOS（`@rpath`/`@loader_path`）支持 | 低 | macOS conda 包也能正确解析 libtvm_ffi 依赖 | 跨平台 |
| ACT-005 | 将洞察1（conda-build三段式依赖）和模式1（conda-build+scikit-build-core打包）萃取为正式模式文档，存入 patterns/ | 中 | 模式文档含触发条件、meta.yaml模板、build.sh模板、反模式清单 | 知识沉淀 |

---

## 附录：验证命令速查

```bash
# 一键构建验证（在容器内执行）
bash /SpecWeave/apps/caffe-ffi-jupyter/scripts/test-conda-build.sh

# 手动验证步骤
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi

# 1. 清理残留
pip uninstall -y caffe-ffi 2>/dev/null || true
find "$CONDA_PREFIX/lib/python3.14/site-packages" -name "_editable_*.pth" -delete 2>/dev/null || true

# 2. 构建
conda-build --no-anaconda-upload -c conda-forge \
  /SpecWeave/projects/xuanspace/libs/caffe-ffi/conda.recipe/

# 3. 安装
PKG=$(find "$CONDA_PREFIX/conda-bld" -name "caffe-ffi-*.conda" -type f | sort -V | tail -1)
conda install -y --offline --use-local --force-reinstall "$PKG"

# 4. 验证加载路径
python -c "import caffe_ffi; print(caffe_ffi.__file__)"

# 5. 验证 ldd/RPATH
CAFFE_SO=$(python -c "import caffe_ffi, glob, os; print(glob.glob(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi*.so'))[0])")
echo "RPATH: $(patchelf --print-rpath $CAFFE_SO)"
ldd $CAFFE_SO | grep "not found" && echo "FAIL: unresolved deps" || echo "PASS: all deps resolved"

# 6. 功能测试
python -c "from caffe_ffi import Blob; import numpy as np; b=Blob([2,3,4,5]); b.fill(3.14); print('count:',b.count(),'data[0]:',np.array(b.data_tensor)[0,0,0,0])"
```

<!-- changelog -->
- 2026-07-30 | docs | caffe-ffi Conda包构建验证里程碑复盘：1.09MB包构建成功，5个Bug修复，ldd/RPATH完全解析，2个可复用模式萃取
