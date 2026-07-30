---
title: "caffe-ffi Conda 包构建验证复盘"
version: "1.5"
date: 2026-07-30
type: task-retrospective
scope: milestone
source: "apps/caffe-ffi-jupyter/scripts/test-conda-build.sh + projects/xuanspace/libs/caffe-ffi/conda.recipe/"
tags: ["conda-build", "scikit-build-core", "cmake", "rpath", "patchelf", "python-packaging", "tvm-ffi", "caffe-ffi", "editable-cleanup", "symbol-verification", "pattern-extraction", "l4-verification", "macos-cross-platform", "conda-build-compat", "pyproject-toml"]
status: in-progress
---

# caffe-ffi Conda 包构建验证复盘

## 执行摘要

本次任务完成了 caffe-ffi（基于 tvm-ffi 的 Caffe 深度学习框架 FFI 绑定库）的 Conda 包构建、验证与 RPATH 依赖解析闭环。构建产物 `caffe-ffi-0.1.0-py314_7.conda`（build number 7）在 Docker 容器内的干净 conda 环境中通过全部验证：导入成功、Blob 功能正常、Python 单元测试通过、所有共享库依赖通过 ldd 解析无 not found、libtvm_ffi.so 正确链接且 TVMFFIGetCustomAllocator 符号验证通过。构建过程中修复了 6 个关键问题，修改 3 个核心文件，实现了 editable 残留三重保护策略，萃取 7 个洞察 + 2 个可复用模式（L3），生成了L4升级验证计划与Checklist表格，完成了macOS跨平台代码适配（待实机验证），完成conda-build 25.x/26.x兼容性调研（A-T6），并完成pyproject.toml三层分离实践（A-T7）——CMake参数按"项目默认值→平台条件→Conda运行时"三层配置，build.sh SKBUILD_CMAKE_ARGS从12个精简为5个。

### 本目录产出物

| 文件 | 说明 |
|------|------|
| [README.md](README.md) | 本复盘主报告（事实还原/过程分析/洞察萃取/改进行动项） |
| [insight-action-backlog.md](insight-action-backlog.md) | 洞察转化的行动项清单与状态跟踪 |
| [l4-verification-plan-and-checklist.md](l4-verification-plan-and-checklist.md) | L4升级验证计划（20个补充测试场景）+ Checklist表格（可直接复制到任务追踪系统） |

### 关键结果

| 指标 | 结果 |
|------|------|
| Conda 包产物 | `caffe-ffi-0.1.0-py314_7.conda`（build number 7） |
| 构建耗时 | ~1分35秒 |
| Docker 容器 | `caffe-ffi-jupyter`（基于 jupyter-ssh-base:1.1） |
| Conda 环境 | caffe-ffi（Python 3.14, Conda-Forge） |
| 修复问题 | 6 个（build backend缺失、路径双重嵌套、CRLF、conda-verify不兼容、editable残留、pip wheel符号缺失） |
| 修改文件 | 3 个核心文件（build.sh/meta.yaml/test-conda-build.sh） |
| Editable清理 | ✅ 三重保护策略（build.sh两次 + test脚本两次） |
| ldd 验证 | ✅ 所有依赖解析，无 not found |
| RPATH 验证 | ✅ Linux `$ORIGIN` 相对路径；macOS `@loader_path` 代码适配完成（待验证） |
| macOS 支持 | 🚧 代码适配完成（build.sh/meta.yaml/test脚本均添加跨平台分支），待实机验证 |
| 模式沉淀 | ✅ 2个L3模式入库，生成L4验证计划和Checklist表格 |
| 符号验证 | ✅ TVMFFIGetCustomAllocator (T) 通过 nm 检查 |
| 功能测试 | ✅ import/Blob.fill/Blob.from_numpy/单元测试 全部通过 |

---

## S1 事实还原

### 时间线与关键事件

| 阶段 | 关键事件 | 结果 |
|------|---------|------|
| 阶段1：脚本执行 | 在 Docker 容器内执行 test-conda-build.sh | 脚本路径错误：从 /SpecWeave 挂载路径执行而非预装路径 |
| 阶段2：CRLF修复 | NTFS 挂载导致 shell 脚本 CRLF 行尾问题 | 使用 `sed -i 's/\r$//'` 批量修复 .sh/.cmake/.py 文件（含tvm-ffi vendor目录） |
| 阶段3：conda镜像 | 清华 TUNA 镜像连接超时 | 重置 conda config 使用 conda-forge 官方源 |
| 阶段4：conda-verify | conda-verify 与 Python 3.14 不兼容 | 安装 conda-build 时跳过 conda-verify；脚本中跳过 conda-verify 步骤 |
| 阶段5：conda-build命令 | `conda build` 子命令不存在（conda>=24.x 已移除） | 修改为直接调用 `conda-build` 命令 |
| 阶段6：BackendUnavailable | `--no-build-isolation` 导致 scikit-build-core 找不到 | 将 scikit-build-core/cmake/ninja/patchelf 加入 meta.yaml host requirements |
| 阶段7：双重嵌套路径 | CMake install DESTINATION=caffe_ffi 与 wheel.install-dir 叠加 | Install.cmake DESTINATION 改为 "."，避免 caffe_ffi/caffe_ffi/ |
| 阶段8：editable残留 | pip editable install 的 .pth 文件导致 Python 加载源码而非 conda 包 | 实现三重保护策略：build.sh双重清理 + test脚本预清理+安装前清理，彻底删除所有editable残留 |
| 阶段9：pip wheel符号缺失 | PyPI apache-tvm-ffi wheel缺少TVMFFIGetCustomAllocator符号 | 优先本地源码编译tvm-ffi，构建前后nm验证符号，设置SETUPTOOLS_SCM_PRETEND_VERSION |
| 阶段10：RPATH跨包依赖 | libtvm_ffi.so安装在tvm_ffi/lib/而非caffe_ffi/ | RPATH新增`$ORIGIN/../tvm_ffi/lib`；libtvm_ffi.so独立设置RPATH（深一级上溯4级） |
| 阶段11：构建参数隔离 | conda CMAKE_ARGS干扰tvm-ffi独立构建 | 临时保存/清空/恢复CMAKE_ARGS和SKBUILD_CMAKE_ARGS |
| 阶段12：ldd验证 | 修复后 _caffe_ffi.so 和 libtvm_ffi.so ldd 无 not found | 所有依赖通过 RPATH 正确解析 |
| 阶段13：单元测试集成 | 验证脚本增加Python单元测试步骤 | 设置CAFFE_FFI_DISABLE_BACKTRACE=1，运行test_python_api.py全部通过 |

### 修改文件清单

| 文件 | 修改内容 | 行数变化 |
|------|---------|---------|
| [conda.recipe/meta.yaml](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/conda.recipe/meta.yaml) | build number=7；完善三段式依赖（host段增加setuptools-scm/protobuf/openblas/typing-extensions；osx增加cctools/llvm-openmp/macos-sdk）；增加missing_dso_whitelist（含.dylib条目）和注释；完善test段（imports/commands/requires/source_files）；完善about段description | +53/-5 |
| [conda.recipe/build.sh](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/conda.recipe/build.sh) | 增加 `clean_editable_files()` 三重保护清理；tvm-ffi安装前彻底清理构建残留；CMAKE_ARGS/SKBUILD_CMAKE_ARGS构建隔离；SETUPTOOLS_SCM_PRETEND_VERSION=0.1.13；nm符号验证(TVMFFIGetCustomAllocator)；macOS跨平台适配（IS_MACOS检测、@loader_path RPATH、install_name_tool、otool/nm -gU封装）；RPATH新增`$ORIGIN/../tvm_ffi/lib`；libtvm_ffi.so独立RPATH设置（深一级路径）；构建后双重editable清理；详细环境变量日志；**A-T7精简**：移除_EXTRA_CMAKE_ARGS平台分支和10个重复-D参数（迁移到pyproject.toml三层分离），SKBUILD_CMAKE_ARGS从12个精简为5个conda专属参数 | +200/-10 |
| [pyproject.toml](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/pyproject.toml) | **A-T7新增**：CMake参数三层分离——项目默认值（CAFFE_USE_BLAS/CAFFE_FFI_BUILD_TESTS/CMAKE_POSITION_INDEPENDENT_CODE）、Linux override（CMAKE_BUILD_RPATH_USE_ORIGIN从全局移到Linux-only）、macOS override（CMAKE_MACOSX_RPATH/CMAKE_INSTALL_NAME_DIR）；CMAKE_BUILD_RPATH_USE_ORIGIN从全局修正为Linux-only | +30/-5 |
| [cmake/Install.cmake](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/cmake/Install.cmake) | DESTINATION 从 "caffe_ffi" 改为 "."，添加详细注释说明双重嵌套原因；新增protobuf Python文件安装规则 | +10/-2 |
| [scripts/test-conda-build.sh](file:///d:/spaces/SpecWeave/apps/caffe-ffi-jupyter/scripts/test-conda-build.sh) | 跳过 conda-verify；conda build → conda-build；recipe 验证改为 YAML parse；实现完整 `clean_editable_residuals()` 函数（清理.pth+.py+__pycache__+direct_url.json）；Step 1b预清理 + Step 7a安装前彻底清理（双重保障）；安装前删除stale包目录；Step 8a0显式验证site-packages加载路径；Step 8c跨平台依赖检查（Linux ldd / macOS otool -L）；新增Step 8d Python单元测试集成；macOS跨平台适配（IS_MACOS检测、otool/nm -gU封装、@rpath验证、.dylib库查找、PLATFORM子目录自适应、Bootstrap Docker/本地miniconda/miniforge自适应）；apache-tvm-ffi pip卸载重装避免版本冲突 | +400/-50 |

### Bug 修复记录

| # | 问题现象 | 根因 | 修复方案 |
|---|---------|------|---------|
| 1 | `BackendUnavailable: Cannot import 'scikit_build_core.build'` | conda-build 使用 `--no-build-isolation` 时，pip 不创建隔离环境，build requirements 中的包不在安装环境中可用 | 将 scikit-build-core、cmake、ninja、patchelf 从 `build` 段移至 `host` 段（build段保留以双重保险） |
| 2 | 安装后 `_caffe_ffi.so` 位于 `caffe_ffi/caffe_ffi/_caffe_ffi.so`（双重嵌套） | scikit-build-core 的 `wheel.install-dir="caffe_ffi"` 设置 CMAKE_INSTALL_PREFIX 为 `caffe_ffi/`，而 CMake install DESTINATION 又指定了 `caffe_ffi`，导致路径叠加 | CMake install DESTINATION 改为 "."，相对于 install-dir 安装，添加详细注释 |
| 3 | conda-verify 与 Python 3.14 不兼容导致安装失败 | conda-verify 尚未适配 Python 3.14（2026-07 时点） | 安装 conda-build 时跳过 conda-verify 依赖（`--no-deps`）；脚本中跳过 conda-verify 步骤 |
| 4 | `conda: error: argument COMMAND: invalid choice: 'build'` | conda >= 24.x 将 `conda build` 子命令拆分为独立 `conda-build` 命令 | 脚本中 `conda build` → `conda-build` |
| 5 | Python `import caffe_ffi` 加载源码目录而非 conda 安装包 | 之前的 pip editable install 留下了 `_editable_skbc_*.pth/.py` 文件、__pycache__缓存、pip的direct_url.json，覆盖了site-packages中的conda包；pip uninstall无法彻底清理scikit-build-core生成的finder文件 | **三重保护策略**：(1)test脚本Step 1b预清理 + Step 7a安装前彻底清理；(2)build.sh中tvm-ffi安装后、caffe-ffi安装后双重清理；(3)清理函数同时处理_editable_*和__editable__*（.pth+.py+pyc）、指向源码路径的自定义.pth、direct_url.json；安装前强制删除stale包目录 |
| 6 | pip安装的apache-tvm-ffi 0.1.12 wheel运行时加载失败 | PyPI wheel缺少`TVMFFIGetCustomAllocator`符号，与本地编译的libtvm_ffi.so存在符号差异，导致运行时custom allocator功能失效 | 优先使用本地源码编译tvm-ffi（SpecWeave vendor目录）；构建前后用`nm -D`验证TVMFFIGetCustomAllocator为T符号（全局文本段）；设置SETUPTOOLS_SCM_PRETEND_VERSION=0.1.13绕过git describe问题；pip安装apache-tvm-ffi仅作为回退方案 |

### 构建产物结构

```
site-packages/
├── caffe_ffi/                          # caffe-ffi 包目录
│   ├── __init__.py                     # Python 包入口
│   ├── _core.py                        # 核心绑定
│   ├── _ffi_api.py                     # FFI API层
│   ├── _caffe_ffi.cpython-314-x86_64-linux-gnu.so  # C++ 编译扩展
│   │   └── RPATH: $ORIGIN:$ORIGIN/lib:$ORIGIN/../tvm_ffi/lib:$ORIGIN/../../..
│   ├── caffe_pb2.py                    # protobuf 生成代码（与预生成版本同步）
│   ├── blob.py, io.py, layer.py, net.py
│   ├── caffe/                          # Caffe 子模块
│   └── tools/                          # 工具模块
└── tvm_ffi/                            # tvm-ffi 包目录（本地源码编译）
    ├── __init__.py
    ├── _ffi_api.py
    ├── lib/
    │   └── libtvm_ffi.so              # tvm-ffi 运行库（本地编译）
    │       └── RPATH: $ORIGIN:$ORIGIN/..:$ORIGIN/../../../../
    └── ... (其他tvm-ffi模块)
```

**RPATH 层级说明**：
- `$ORIGIN`：当前 .so 所在目录（`caffe_ffi/` 或 `tvm_ffi/lib/`）
- `$ORIGIN/lib`：同目录下 lib/ 子目录（预留私有库）
- `$ORIGIN/../tvm_ffi/lib`：**跨包路径**，从 caffe_ffi/ 指向同级 tvm_ffi/lib/（_caffe_ffi.so 专用）
- `$ORIGIN/../../..`：上溯3级到达 PREFIX/lib（caffe_ffi/ → site-packages/ → python3.14/ → lib/）
- `$ORIGIN/../../../../`：上溯4级到达 PREFIX/lib（tvm_ffi/lib/ → tvm_ffi/ → site-packages/ → python3.14/ → lib/）

### ldd 验证结果

**`_caffe_ffi.so` 依赖解析**：
- libtvm_ffi.so → `$ORIGIN/../tvm_ffi/lib/libtvm_ffi.so`（跨包路径，通过 `$ORIGIN/../tvm_ffi/lib` RPATH）✅
- libprotobuf.so.35.1.0 → conda 环境 lib ✅
- libopenblas.so.0 → conda 环境 lib ✅
- libstdc++.so.6 / libm.so.6 / libgcc_s.so.1 / libc.so.6 / ld-linux-x86-64.so.2 → 系统/conda 基础库 ✅
- libabsl_*（abseil 系列库）→ conda 环境 lib ✅
- **not found 依赖：无** ✅
- **符号验证**：`nm -D libtvm_ffi.so | grep TVMFFIGetCustomAllocator` → `T TVMFFIGetCustomAllocator`（全局文本段符号，正常）✅

**`libtvm_ffi.so` 依赖解析**：
- 仅依赖基础系统库：libstdc++.so.6, libm.so.6, libgcc_s.so.1, libc.so.6, libdl.so.2
- **not found 依赖：无** ✅

---

## S2 过程分析

### 成功因素

1. **Docker 容器复用**：使用已运行的 `caffe-ffi-jupyter` 容器而非每次启动新容器，保持 conda 环境缓存，大幅加速迭代
2. **test-conda-build.sh 全流程自动化**：脚本涵盖环境检查→预清理editable→CRLF修复→依赖安装→recipe验证→构建→安装前彻底清理→安装→路径验证→功能测试→ldd检查→单元测试→包信息输出，一键完成
3. **Editable 残留三重保护策略**：(1) test脚本Step 1b预清理 + Step 7a安装前清理；(2) build.sh内tvm-ffi安装后、caffe-ffi安装后双重清理；(3) 清理函数覆盖所有editable变体（_editable_*/__editable__* .pth+.py+pyc、源码路径.pth、direct_url.json、stale目录）
4. **RPATH 四层跨包设计**：`$ORIGIN`（同目录）、`$ORIGIN/lib`（子目录）、`$ORIGIN/../tvm_ffi/lib`（跨包同级依赖）、`$ORIGIN/../../..`（conda环境lib）四层相对路径；libtvm_ffi.so独立设置深一级RPATH（上溯4级）；无需设置LD_LIBRARY_PATH
5. **本地源码优先的 tvm-ffi 构建策略**：优先使用SpecWeave vendor目录的本地源码编译tvm-ffi，避免PyPI wheel符号缺失问题；SETUPTOOLS_SCM_PRETEND_VERSION绕过git describe；构建前后nm验证TVMFFIGetCustomAllocator符号
6. **构建参数隔离机制**：嵌套构建tvm-ffi时临时保存/清空/恢复CMAKE_ARGS和SKBUILD_CMAKE_ARGS，避免conda-build的CMAKE_ARGS（含CMAKE_INSTALL_PREFIX等）干扰独立构建
7. **build.sh tvm-ffi 多路径自动检测**：CAFFE_FFI_TVM_FFI_DIR环境变量→SpecWeave挂载路径→SRC_DIR相对路径，多级自动检测确保本地tvm-ffi在各种布局下都能找到
8. **patchelf 后置修复 + ldd 硬性门禁**：构建完成后用patchelf设置RPATH并执行ldd验证，grep "not found"直接exit 1，确保不遗漏任何未解析依赖
9. **单元测试集成**：验证脚本Step 8d自动运行Python单元测试（设置CAFFE_FFI_DISABLE_BACKTRACE=1避免pytest环境下C++栈回溯崩溃）

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

**关键问题：editable install 残留系统性干扰 conda 包验证**

- Why 1? → conda install后Python加载源码目录而非site-packages包
  - Why 2? → `_editable_skbc_*.pth` 文件在sys.path中优先级高于site-packages
    - Why 3? → pip uninstall无法彻底删除scikit-build-core生成的finder模块（.pth+.py+__pycache__+direct_url.json）
      - Why 4? → conda和pip的包数据库不同步，pip不知道conda安装的包，也不清理非pip创建的文件
        - Why 5? → PEP 660 editable install的finder机制复杂（不仅是.pth路径注入，还包含namespace merging的finder模块），简单删除.pth不够

**根因**：scikit-build-core的PEP 660 editable install会创建一组配套文件（.pth路径注入 + .py finder模块 + __pycache__缓存 + pip的direct_url.json标记），pip uninstall在conda环境中无法彻底清理这些文件。必须实现专门的、多维度的清理策略（三重保护）才能保证conda包验证环境干净。

**关键问题：pip wheel与本地编译库符号不兼容**

- Why 1? → 本地编译的caffe-ffi运行时加载PyPI安装的libtvm_ffi.so时custom allocator功能失效
  - Why 2? → PyPI wheel中的libtvm_ffi.so缺少`TVMFFIGetCustomAllocator`符号
    - Why 3? → PyPI apache-tvm-ffi 0.1.12 wheel的编译选项与本地不同（可能关闭了custom allocator或使用了不同版本的源码）
      - Why 4? → pip默认从PyPI安装wheel，而非使用本地vendor目录的源码编译
        - Why 5? → 缺乏符号完整性验证，链接时不报错但运行时符号缺失

**根因**：预编译wheel与本地编译代码之间可能存在符号差异（编译选项、版本差异、strip操作等），特别是对于FFI这种需要紧密二进制兼容的库。必须优先使用本地源码编译依赖库，并在构建前后用`nm -D`验证关键符号存在。

### 瓶颈与约束

| 瓶颈/约束 | 影响 | 应对 |
|----------|------|------|
| Python 3.14 生态成熟度 | conda-verify 等包尚未适配，conda-forge 部分包可能缺失 | 跳过不兼容工具，使用 `--no-deps` 安装核心包 |
| NTFS 挂载 CRLF 问题 | Windows 宿主机上编辑的脚本在 Linux 容器内执行失败 | 构建脚本自动检测并修复 CRLF（含vendor目录） |
| conda-build build/host/run 三段式 | 容易混淆各段职责，特别是 --no-build-isolation 时 | host 段必须包含所有 Python 构建后端；build段保留双重保险 |
| editable install 残留复杂 | PEP 660生成多文件（.pth+.py+pyc+direct_url.json），pip/conda均无法彻底清理 | 三重保护策略：build.sh双重清理 + test脚本预清理+安装前清理；清理函数覆盖所有变体 |
| 嵌套构建参数污染 | conda CMAKE_ARGS含CMAKE_INSTALL_PREFIX等设置，干扰子项目独立构建 | 临时保存/清空/恢复CMAKE_ARGS和SKBUILD_CMAKE_ARGS |
| 跨包RPATH依赖 | 依赖库可能安装在同级其他包的lib/下（而非自身目录或系统lib） | RPATH必须包含`$ORIGIN/../<dep_pkg>/lib`跨包路径；根据库的嵌套深度精确计算上溯级数 |
| pip wheel二进制兼容性 | PyPI预编译wheel可能缺少关键符号或版本不匹配 | 优先本地源码编译；构建前后nm验证关键符号；pip wheel仅作为最后回退 |
| C++ backtrace在pytest崩溃 | `backtrace_symbols()`在pytest环境处理Python栈帧会崩溃 | 默认设置`CAFFE_FFI_DISABLE_BACKTRACE=1`，用户可显式启用 |

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

### 洞察 3：Editable Install 残留的三重保护清理策略

**现象陈述**：开发环境中 `pip install -e .`（editable install）创建的不仅是 `.pth` 文件，而是一整套配套文件（.pth路径注入 + .py finder模块 + __pycache__缓存 + pip direct_url.json标记），这些文件在pip uninstall和conda install后均可能残留，导致Python加载源码目录而非conda包。简单删除.pth文件不够。

**证据**：
- Bug #5：conda install caffe-ffi 后 `import caffe_ffi` 加载的是源码目录而非 site-packages/caffe_ffi/
- scikit-build-core PEP 660生成：`_editable_skbc_<pkg>.pth` + `_editable_skbc_<pkg>.py`（~30KB finder模块）+ `__pycache__/_editable_skbc_<pkg>.*.pyc`
- pip uninstall无法删除finder .py和__pycache__；conda install不清理非自身包的文件
- 修复：三重保护策略（build.sh内两次 + test脚本两次），清理函数覆盖所有变体

**反常识**：editable install的残留不是单个.pth文件问题，而是一组文件的系统性污染。.pth文件优先级高于正常site-packages包，finder模块还会做namespace merging，仅删除.pth可能因为finder模块缓存仍然失败。pip和conda都不会自动清理对方创建的editable残留。

**下次行动**：在conda包构建验证中必须实现三重保护editable清理：
1. **build.sh内置清理函数**：tvm-ffi安装后、caffe-ffi安装后各执行一次（双重保险），清理所有`_editable_*`和`__editable__*`（.pth+.py）、指向源码路径的.pth文件
2. **test脚本Step 1b预清理**：任何构建步骤之前清理一次，防止editable残留干扰构建过程
3. **test脚本Step 7a安装前彻底清理**：安装前再次清理，删除stale包目录、direct_url.json
4. **Step 8a0路径验证门禁**：必须验证`__file__`路径包含`site-packages/caffe_ffi`，否则fail

### 洞察 4：跨包 RPATH 依赖的层级计算模型

**现象陈述**：当依赖的共享库安装在同级其他Python包的lib/子目录下（而非自身目录或系统lib），RPATH必须精确计算跨包相对路径和目录嵌套深度的上溯级数。绝对路径`$PREFIX/lib`会导致conda-build prefix replacement时"Placeholder too short"错误。

**证据**：
- libtvm_ffi.so安装在`site-packages/tvm_ffi/lib/libtvm_ffi.so`（比_caffe_ffi.so深一级）
- 最初RPATH只有`$ORIGIN:$ORIGIN/lib:$ORIGIN/../../..`，无法找到tvm_ffi/lib/下的库
- 添加`$ORIGIN/../tvm_ffi/lib`跨包路径后_caffe_ffi.so能找到libtvm_ffi.so
- libtvm_ffi.so需要上溯4级（lib→tvm_ffi→site-packages→python3.14→lib），而非_caffe_ffi.so的3级
- 使用`${PREFIX}/lib`绝对路径触发conda-build的prefix replacement机制，因路径长度超过placeholder限制而失败

**反常识**：直觉上"conda环境lib目录就是PREFIX/lib"，但RPATH不能用绝对路径——conda-build会尝试将构建时的PREFIX替换为安装时的PREFIX，若RPATH包含绝对路径且长度超过placeholder（通常256字符）会构建失败。所有RPATH必须使用`$ORIGIN`相对路径，且必须精确计算每个库所在目录到PREFIX/lib的上溯级数。

**下次行动**：设置多层Python包共享库RPATH时：
1. 一律使用`$ORIGIN`相对路径，禁止绝对路径
2. 为每个.so单独计算RPATH，不要假设所有库深度相同
3. 包含跨包路径`$ORIGIN/../<dep_pkg>/lib`指向同级依赖包的lib目录
4. 上溯级数 = 从.so所在目录到PREFIX/lib的`..`个数
5. 构建后必须用`patchelf --print-rpath`验证，并执行ldd检查

### 洞察 5：嵌套构建时的 CMAKE_ARGS 隔离机制

**现象陈述**：conda-build设置的CMAKE_ARGS环境变量包含`-DCMAKE_INSTALL_PREFIX=$PREFIX`等设置，当build.sh中需要先pip install一个依赖的本地CMake项目（嵌套构建）时，这些参数会污染子项目的CMake配置，导致安装路径错误或构建失败。

**证据**：
- build.sh中先pip install本地tvm-ffi，再pip install caffe-ffi
- conda CMAKE_ARGS包含CMAKE_INSTALL_PREFIX、CMAKE_FIND_ROOT_PATH等设置
- 不隔离时tvm-ffi被安装到错误的前缀，或find_package找到错误的路径
- 修复：嵌套构建前保存OLD_CMAKE_ARGS/SKBUILD_CMAKE_ARGS，清空后执行子构建，完成后恢复
- SKBUILD_CMAKE_ARGS也需要同样处理，因为scikit-build-core会读取该变量

**反常识**：直觉上"环境变量设置应该被子进程继承"，但conda-build注入的CMAKE_ARGS是为了主包构建准备的，对于需要先构建的依赖包，这些参数是污染而非帮助。嵌套构建必须主动隔离这些变量，子项目应该使用自己的CMake配置。

**下次行动**：conda-build脚本中嵌套pip install本地CMake项目时：
1. 构建前保存`_OLD_CMAKE_ARGS="${CMAKE_ARGS:-}"`和`_OLD_SKBUILD_CMAKE_ARGS="${SKBUILD_CMAKE_ARGS:-}"`
2. `export CMAKE_ARGS=""`和`unset SKBUILD_CMAKE_ARGS`清空变量
3. 仅追加子项目需要的特定参数（如`-DTVM_FFI_USE_LIBBACKTRACE=OFF`）
4. 子构建完成后恢复原始值

### 洞察 6：预编译 Wheel 的符号完整性验证

**现象陈述**：PyPI上的预编译wheel可能与本地编译的代码存在符号差异（编译选项不同、版本差异、strip操作等），这些差异在链接时不报错但运行时会导致微妙的功能失效。对于需要紧密二进制兼容的FFI库，必须验证关键符号存在。

**证据**：
- Bug #6：pip install apache-tvm-ffi 0.1.12 wheel后，caffe-ffi运行时TVMFFIGetCustomAllocator功能失效
- `nm -D libtvm_ffi.so | grep TVMFFIGetCustomAllocator`显示wheel中缺少该T符号（全局文本段）
- 本地源码编译的libtvm_ffi.so正确包含该符号
- 链接阶段不报错（因为是动态链接，符号在运行时解析），直到调用custom allocator时才崩溃

**反常识**：直觉上"pip能安装成功、ldd不报错、import不报错就没问题"，但动态链接的符号是延迟解析的，关键功能符号缺失可能只在特定代码路径触发时才暴露。预编译wheel的编译选项可能与本地环境不兼容，特别是对于提供自定义分配器、回调函数等扩展点的库。

**下次行动**：对于提供FFI/扩展点的C++共享库：
1. 优先使用本地源码编译而非PyPI预编译wheel（特别是在conda构建环境中）
2. 构建前后用`nm -D <lib.so> | grep <CriticalSymbol>`验证关键符号为`T`（全局文本段）
3. SETUPTOOLS_SCM_PRETEND_VERSION绕过git submodule在Docker中Windows路径问题
4. pip wheel仅作为最后回退方案，并必须通过符号验证

### 洞察 7：C++ 栈回溯在 pytest 环境中的崩溃问题

**现象陈述**：C++层的`backtrace_symbols()`在pytest测试环境中处理Python栈帧时会导致段错误，使得正常的单元测试无法运行。

**证据**：
- 直接运行Python脚本时backtrace正常工作
- 通过pytest运行时，C++异常触发backtrace_symbols()会崩溃
- 原因：pytest的栈帧布局/信号处理与正常Python解释器不同，backtrace_symbols无法安全处理混合栈帧
- 修复：默认设置`CAFFE_FFI_DISABLE_BACKTRACE=1`环境变量禁用backtrace，用户可显式设为0重新启用

**反常识**：直觉上"backtrace是调试功能，应该默认开启帮助排查问题"，但在测试框架环境中它本身会成为崩溃源，导致测试无法进行。对于会被pytest导入的C++扩展库，backtrace功能应该默认关闭，仅在需要调试时显式启用。

**下次行动**：C++ Python扩展库的backtrace/stacktrace功能：
1. 提供环境变量开关（如`CAFFE_FFI_DISABLE_BACKTRACE=1`）
2. 在测试脚本/CI中默认禁用backtrace
3. 文档中说明如何在需要调试时启用

### 模式 1：conda-build + scikit-build-core 原生扩展打包模式（升级版）

> 📚 **正式模式文档**：[conda-build-scikit-build-core-native.md](../../patterns/code-patterns/conda-build-scikit-build-core-native.md)（L3 方法论，已沉淀至模式库）

**触发场景**：需要将 C++/CMake 构建的 Python 原生扩展打包为 Conda 包，依赖 scikit-build-core 构建系统，需要依赖另一个同架构本地编译的Python C++扩展（如tvm-ffi），且需要精确控制RPATH和符号兼容性。

**核心步骤**：
1. **meta.yaml 三段式依赖**：
   - build：`{{ compiler('cxx') }}`、patchelf、cmake、ninja、scikit-build-core（build段保留作双重保险）
   - host：python、pip、scikit-build-core、cmake、ninja、patchelf、C++依赖库（-dev包，如libprotobuf、libopenblas）、numpy、cython、setuptools-scm、typing-extensions
   - run：python、运行时依赖（不含构建工具）、pytest（如果tvm.testing间接需要）
   - build: number: N（递增），detect_binary_files_with_prefix: false（全相对RPATH不需要prefix替换）
2. **build.sh 关键配置**：
   - `set -eux -o pipefail`严格模式
   - CRLF预处理（dos2unix/sed），清理in-tree构建残留
   - **嵌套构建参数隔离**：保存/清空/恢复CMAKE_ARGS和SKBUILD_CMAKE_ARGS
   - **本地依赖优先策略**：多路径自动检测本地源码（环境变量→Docker挂载→相对路径），pip wheel仅作回退
   - `pip install . --no-deps --no-build-isolation`（必须--no-build-isolation）
   - SETUPTOOLS_SCM_PRETEND_VERSION处理git submodule版本问题
   - **三重保护editable清理**：clean_editable_files()函数，在依赖安装后和主包安装后各执行一次
3. **RPATH 四层跨包设计**（全`$ORIGIN`相对路径，禁止绝对路径）：
   - `$ORIGIN`：同目录
   - `$ORIGIN/lib`：子目录（预留）
   - `$ORIGIN/../<dep_pkg>/lib`：跨包同级依赖（如`tvm_ffi/lib`）
   - `$ORIGIN/../../..`：上溯N级到PREFIX/lib（精确计算深度）
   - 为每个依赖的.so单独设置RPATH（根据其目录深度）
4. **符号完整性验证**：`nm -D`验证关键符号为T类型
5. **ldd 硬性门禁**：构建后立即执行ldd检查，grep "not found"直接exit 1
6. **patchelf RPATH设置**：为主包和所有依赖的.so分别设置正确的相对RPATH

**反模式**：
- ❌ 将scikit-build-core/cmake/ninja仅放在build requirements（--no-build-isolation时找不到）
- ❌ CMake install DESTINATION重复包名目录（与wheel.install-dir叠加导致双重嵌套）
- ❌ 使用`${PREFIX}/lib`绝对路径（触发conda-build prefix replacement "Placeholder too short"错误）
- ❌ 所有.so使用相同RPATH（不考虑依赖库嵌套深度不同）
- ❌ 嵌套构建时不隔离CMAKE_ARGS（conda参数污染子项目构建）
- ❌ 直接pip install PyPI wheel作为FFI依赖（可能缺少关键符号）
- ❌ 仅依赖LD_LIBRARY_PATH而不设置RPATH（conda环境不应依赖全局LD_LIBRARY_PATH）
- ❌ 跳过nm符号验证（运行时才发现符号缺失）
- ❌ 假设pip uninstall能清理editable残留（实际需要专门的三重保护清理）

**成熟度**：L3（已在caffe-ffi项目端到端验证6次迭代，单元测试通过，ldd全部解析，符号验证通过）

### 模式 2：Conda 构建验证干净环境前置清理模式（升级版）

> 📚 **正式模式文档**：[conda-package-clean-verification.md](../../patterns/code-patterns/conda-package-clean-verification.md)（L3 方法论，已沉淀至模式库）

**触发场景**：在开发Docker容器中反复迭代验证conda包构建结果，容器内存在之前的editable install、pip install、stale目录等多种残留。

**核心步骤**：
1. **Step 1b 预清理**（任何构建/安装步骤之前）：
   - 调用`clean_editable_residuals(pkg_name)`清理editable残留
2. **彻底清理函数**必须处理：
   - scikit-build-core风格：`_editable_skbc_*.pth` + `_editable_skbc_*.py` finder模块 + `__pycache__/_editable_skbc_*.pyc`
   - PEP 660通用风格：`__editable__.*.pth`
   - pip标记：`<pkg>-*.dist-info/direct_url.json`
   - 指向源码路径（xuanspace/SpecWeave/_skbuild）的自定义.pth文件
   - stale包目录：`rm -rf site-packages/<pkg>/` 和 `<pkg>-*.dist-info/`
3. **Step 7a 安装前再清理**（双重保险）：
   - 再次调用clean_editable_residuals
   - 卸载可能冲突的pip包（如pip版apache-tvm-ffi）
   - 删除所有site-packages中的stale包目录
4. **强制重装**：`conda install -y --use-local --force-reinstall <package>`
5. **Step 8a0 加载路径验证门禁**（硬性fail条件）：
   - `python -c "import <pkg>; print(<pkg>.__file__)"`
   - grep必须匹配`site-packages/<pkg>/`，否则直接fail
6. **多维度验证**：
   - 8a: import测试 + 版本 + native available检查
   - 8b: 核心功能测试（Blob fill/from_numpy/shape/count等）
   - 8c: ldd完整检查（not found门禁 + 关键库链接验证如libtvm_ffi、BLAS、protobuf）
   - 8d: Python单元测试（设置`CAFFE_FFI_DISABLE_BACKTRACE=1`防止pytest崩溃）
7. **build.sh内置清理**（第三重保护）：build.sh内也调用clean_editable_files()

**反模式**：
- ❌ 直接`conda install`而不清理任何残留（.pth+.py+pyc+direct_url.json多重污染）
- ❌ 仅清理.pth文件而忽略finder .py和__pycache__（namespace merging仍可能干扰）
- ❌ 仅验证import成功而不验证`__file__`路径（可能加载了源码目录）
- ❌ 跳过ldd检查（运行时才发现缺失依赖）
- ❌ 不设置CAFFE_FFI_DISABLE_BACKTRACE=1就运行pytest（C++ backtrace在pytest中崩溃）
- ❌ 构建前不预清理（editable残留可能干扰构建过程本身）

**成熟度**：L3（已在caffe-ffi验证中验证6次迭代，有/无editable残留环境均能正确通过，单元测试通过）

---

## S4 改进行动项

| ID | 行动项 | 优先级 | 验收标准 | 类型 | 状态 |
|----|--------|--------|---------|------|------|
| ACT-001 | build.sh增加`_editable_*.pth`自动清理步骤，实现三重保护策略 | 高 | 验证脚本在有editable残留的环境中也能正确验证conda包；build.sh内置清理函数；test脚本预清理+安装前清理+路径验证门禁 | 质量门禁 | ✅ 已完成 |
| ACT-002 | 在meta.yaml中增加`missing_dso_whitelist`的详细注释，说明哪些库是vendored/bundled | 中 | 其他开发者阅读meta.yaml能理解DSO白名单的用途 | 文档 | ⏸️ 搁置 |
| ACT-003 | ~~将RPATH `$ORIGIN/../../..`改为`$PREFIX/lib`绝对路径~~ | 中 | **已取消**：绝对路径会导致conda-build prefix replacement "Placeholder too short"错误，必须使用全`$ORIGIN`相对路径 | 健壮性 | ❌ 已取消（方案不可行） |
| ACT-003b | 为每个依赖的.so单独计算并设置RPATH（考虑目录嵌套深度），添加`$ORIGIN/../tvm_ffi/lib`跨包路径 | 中 | _caffe_ffi.so（深度3）和libtvm_ffi.so（深度4）RPATH正确；ldd无not found；包含跨包路径 | 健壮性 | ✅ 已完成 |
| ACT-004 | 为caffe-ffi conda recipe增加macOS（`@rpath`/`@loader_path`）支持 | 低 | build.sh/meta.yaml/test-conda-build.sh均已添加macOS跨平台分支（install_name_tool/otool/nm -gU）；待macOS实机构建验证 | 跨平台 | 🚧 代码适配完成（待验证） |
| A-T7 | pyproject.toml CMake参数三层分离 | 低 | 项目默认值→平台条件→Conda运行时三层分离；SKBUILD_CMAKE_ARGS从12个精简为5个；CMAKE_BUILD_RPATH_USE_ORIGIN修正为Linux-only | 模式增强 | ✅ 代码完成（待实机构建验证） |
| ACT-005 | 将洞察和模式萃取为正式模式文档，存入patterns/ | 中 | 已沉淀2个L3模式：conda-build-scikit-build-core-native.md（打包六步法）、conda-package-clean-verification.md（五维验证法）；已更新模式索引 | 知识沉淀 | ✅ 已完成 |
| ACT-006 | build.sh中增加关键符号nm验证步骤 | 中 | 构建前后验证TVMFFIGetCustomAllocator等关键符号为T类型，防止pip wheel符号缺失 | 健壮性 | ✅ 已完成 |
| ACT-007 | 嵌套构建时CMAKE_ARGS/SKBUILD_CMAKE_ARGS参数隔离 | 中 | 本地源码编译tvm-ffi时隔离conda的CMAKE_ARGS，防止污染子项目构建 | 健壮性 | ✅ 已完成 |
| ACT-008 | 验证脚本集成Python单元测试步骤 | 中 | test-conda-build.sh Step 8d自动运行单元测试；设置CAFFE_FFI_DISABLE_BACKTRACE=1防止pytest崩溃 | 质量门禁 | ✅ 已完成 |

---

## 附录：验证命令速查

```bash
# 一键构建验证（在容器内执行，推荐）
bash /SpecWeave/apps/caffe-ffi-jupyter/scripts/test-conda-build.sh

# 手动验证步骤
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export CAFFE_FFI_DISABLE_BACKTRACE=1

# 1. 彻底清理editable残留（三重保护）
python -c "
import site, glob, os, shutil
for sp in site.getsitepackages():
    # Clean _editable_skbc_* files
    for pth in glob.glob(os.path.join(sp, '_editable_*.pth')) + glob.glob(os.path.join(sp, '__editable__.*.pth')):
        base = os.path.splitext(pth)[0]
        for f in [pth, base + '.py']:
            if os.path.exists(f): os.remove(f)
        pyc_dir = os.path.join(sp, '__pycache__')
        if os.path.isdir(pyc_dir):
            for pyc in glob.glob(os.path.join(pyc_dir, os.path.basename(base) + '.*.pyc')):
                os.remove(pyc)
    # Clean direct_url.json
    for di in glob.glob(os.path.join(sp, 'caffe_ffi-*.dist-info', 'direct_url.json')):
        os.remove(di)
    # Remove stale caffe_ffi directory
    pkg_dir = os.path.join(sp, 'caffe_ffi')
    if os.path.isdir(pkg_dir): shutil.rmtree(pkg_dir)
"

# 2. 构建
conda-build --no-anaconda-upload --no-test -c conda-forge \
  /SpecWeave/projects/xuanspace/libs/caffe-ffi/conda.recipe/

# 3. 安装
PKG=$(find "$CONDA_PREFIX/conda-bld" -name "caffe-ffi-*.conda" -type f | sort -V | tail -1)
conda install -y --use-local --force-reinstall "$PKG"

# 4. 验证加载路径（必须在site-packages下）
python -c "import caffe_ffi; p=caffe_ffi.__file__; print(p); assert 'site-packages/caffe_ffi' in p, f'Wrong path: {p}'; print('PASS: loading from conda site-packages')"

# 5. 验证RPATH和ldd
CAFFE_SO=$(python -c "import caffe_ffi, glob, os; print(glob.glob(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi*.so'))[0])")
echo "=== RPATH ==="
patchelf --print-rpath "$CAFFE_SO"
echo "=== ldd check ==="
ldd "$CAFFE_SO"
if ldd "$CAFFE_SO" | grep -q "not found"; then echo "FAIL: unresolved deps"; exit 1; else echo "PASS: all deps resolved"; fi
echo "=== Symbol check ==="
TVM_SO=$(python -c "import tvm_ffi, os; print(os.path.join(os.path.dirname(tvm_ffi.__file__), 'lib', 'libtvm_ffi.so'))")
nm -D "$TVM_SO" | grep TVMFFIGetCustomAllocator && echo "PASS: TVMFFIGetCustomAllocator symbol found" || echo "FAIL: symbol missing"

# 6. 功能测试
python -c "from caffe_ffi import Blob; import numpy as np; b=Blob([2,3,4,5]); b.fill(3.14); print('count:',b.count(),'data[0]:',np.array(b.data_tensor)[0,0,0,0]); assert abs(np.array(b.data_tensor)[0]-3.14)<1e-6; print('PASS: Blob test')"

# 7. 单元测试
export CAFFE_FFI_DISABLE_BACKTRACE=1
python /SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python/test_python_api.py
```

<!-- changelog -->
- 2026-07-30 | code+docs | v1.5更新：A-T7 pyproject.toml CMake参数三层分离实践——项目默认值（cmake.define）+平台条件（overrides）+Conda运行时（build.sh）三层分离；pyproject.toml新增CAFFE_USE_BLAS/CAFFE_FFI_BUILD_TESTS/CMAKE_POSITION_INDEPENDENT_CODE，CMAKE_BUILD_RPATH_USE_ORIGIN从全局修正为Linux-only override，新增macOS override；build.sh SKBUILD_CMAKE_ARGS从12个精简为5个conda专属参数；模式文档新增步骤1b三层分离指南；待实机构建验证
- 2026-07-30 | docs | v1.4更新：A-T6 conda-build 25.x/26.x兼容性调研完成——确认无scikit-build-core原生支持；发现6项关键版本变更（patchelf<0.18限制/pip选项自动管理/Python 3.9移除/macOS RPATH修复/Python 3.14兼容/whitelist→allowlist重命名）；meta.yaml添加allowlist迁移注释；模式文档新增conda-build版本兼容性矩阵
- 2026-07-30 | docs | v1.3更新：ACT-004 macOS跨平台代码适配完成，build.sh/meta.yaml/test-conda-build.sh三个核心文件均添加macOS分支（@loader_path RPATH、install_name_tool、otool -L、nm -gU、.dylib支持），build number升至7，模式文档标注待验证状态；待macOS实机构建验证
- 2026-07-30 | docs | v1.2更新：ACT-005完成——萃取2个L3模式存入patterns/（conda-build-scikit-build-core-native.md、conda-package-clean-verification.md），生成L4升级验证计划与Checklist表格
- 2026-07-30 | docs | v1.1更新：6次构建迭代完善，新增editable三重保护策略、跨包RPATH四层设计、嵌套构建参数隔离、符号完整性验证、单元测试集成；修复6个Bug，萃取7个洞察+2个L3成熟度模式，完成ACT-001/003b/006/007/008
- 2026-07-30 | docs | caffe-ffi Conda包构建验证里程碑复盘：1.09MB包构建成功，5个Bug修复，ldd/RPATH完全解析，2个可复用模式萃取
