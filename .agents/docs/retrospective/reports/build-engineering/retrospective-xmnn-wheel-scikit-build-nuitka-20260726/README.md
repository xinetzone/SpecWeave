---
id: "retrospective-xmnn-wheel-scikit-build-nuitka-20260726"
title: "XMNN Wheel 构建系统搭建复盘（scikit-build-core + Nuitka + CMake）"
type: "build-engineering"
date: "2026-07-26"
status: "completed"
maturity: "L2"
source: "xmtools wheel packaging project"
tags: ["nuitka", "scikit-build-core", "cmake", "wheel", "tvm", "python3.14", "native-packaging"]
---

# XMNN Wheel 构建系统搭建复盘（scikit-build-core + Nuitka + CMake）

## 执行摘要

为 XMNN（NPU推理工具包）搭建了基于 **scikit-build-core + CMake + Nuitka** 的现代化 Python wheel 构建系统，替代了传统的 setuptools/setup.py 方案。最终产出 169MB 的 `xmnn-0.1.0-cp314-cp314-linux_x86_64.whl`，在干净虚拟环境中6项验证全部通过。项目强制 Python >=3.14 运行时约束，并解决了 TVM 源码在 Python 3.12+ 上的 AST 兼容性问题。

**关键数据**：
- 最终 wheel 大小：169 MB
- Python 版本约束：>=3.14
- 构建工具链：scikit-build-core >=0.5 + cmake >=3.18 + ninja >=1.10 + Nuitka
- 编译依赖库：libtvm.so（76MB）+ 7个 LLVM/系统级依赖库
- 验证通过率：6/6 ✅
- 核心源文件数：7个配置/构建文件

---

## R·事实清单（G1质量门：无因果词）

### F01. 初始需求

- 任务目标：在 `external/chaos/xmtools/` 目录中创建 `external/chaos/npuusertools/xmnn/` 的 whl 包
- 指定工具链：Nuitka + cmake + ninja
- 打包对象1：`external/chaos/npu_tvm/python/tvm`（需包含 `relay/std/` 的 `.rly` 数据文件）
- 打包对象2：`external/chaos/npu_tvm/vta/python/vta`（需包含 `vta_hw/config/` 的配置文件）
- TVM原生库构建命令：`inv config -f` 后执行 `inv make`

### F02. 构建系统选择变更

- 初始方案：setuptools + setup.py + MANIFEST.in
- 用户明确要求：避免使用 setuptools 和 setup.py，改用 cmake 与 scikit-build-core
- 变更后方案：pyproject.toml 声明 `build-backend = "scikit_build_core.build"`，CMakeLists.txt 控制所有安装规则

### F03. Python 版本约束设定

- 配置位置：[pyproject.toml](file:///d:/spaces/SpecWeave/external/chaos/xmtools/pyproject.toml) 中 `requires-python = ">=3.14"`
- CMake 层版本检查：[CMakeLists.txt](file:///d:/spaces/SpecWeave/external/chaos/xmtools/CMakeLists.txt#L6-L10) 中 `Python3_VERSION VERSION_LESS "3.14"` 触发 FATAL_ERROR
- 验证脚本版本检查：[verify_wheel.py](file:///d:/spaces/SpecWeave/external/chaos/xmtools/scripts/verify_wheel.py#L361-L363) 中 `sys.version_info < (3, 14)` 退出码1
- Invoke 任务版本检查：[tasks.py](file:///d:/spaces/SpecWeave/external/chaos/xmtools/tasks.py#L195-L199) 中 check_deps 任务

### F04. Nuitka 编译配置

- TVM 编译命令参数：`--module --include-package=tvm --include-data-dir=...=relay/std --output-dir=...`
- VTA 编译命令参数：`--module --include-package=vta --nofollow-import-to=tvm --include-data-dir=...=vta_hw/config --output-dir=...`
- 不使用 `--follow-imports`（曾尝试后放弃，会编译标准库导致错误）
- 不使用 `--output-filename`（Nuitka 模块模式下文件名必须匹配模块名）
- 代码注入方式：`_inject_preamble()` 函数将引导代码写入 `__init__.py` 顶部，编译后 `_restore_file()` 恢复
- 备份文件后缀：`.bak_xmnn`

### F05. Python 3.14 AST 兼容性处理

- 被移除的 AST 类：`ast.NameConstant`、`ast.Num`、`ast.Str`、`ast.Bytes`（均合并到 `ast.Constant`）
- 被移除的 AST 类：`ast.Index`、`ast.ExtSlice`（Python 3.9 中废弃，3.12 中移除）
- 修复方式：Monkey-patch，在模块加载时检查 `hasattr(ast, "Xxx")`，缺失则定义兼容类
- 注入位置：[tasks.py](file:///d:/spaces/SpecWeave/external/chaos/xmtools/tasks.py#L22-L82) 中的 `_PREAMBLE_TVM` 和 `_PREAMBLE_VTA`
- 运行时注入：[_xmnn_bootstrap.py](file:///d:/spaces/SpecWeave/external/chaos/xmtools/_xmnn_bootstrap.py#L37-L71) 中同样包含 Monkey-patch（通过 .pth 文件在所有 import 前加载）

### F06. TVM 原生库构建

- 标准构建命令：`inv config -f` 生成配置，`inv make` 编译
- 发现问题：默认配置下 `USE_EXAMPLE_TARGET_HOOKS=OFF`，导致 `TIRToRuntime` 属性未注册，`tvm.build(llvm)` 失败
- 补丁操作：[tasks.py](file:///d:/spaces/SpecWeave/external/chaos/xmtools/tasks.py#L226-L240) 中 `build_tvm` 任务在 `inv config -f` 后、`inv make` 前，正则替换 `config.cmake` 将 `USE_EXAMPLE_TARGET_HOOKS` 设为 ON
- 最终产物：`libtvm.so`（76MB），不单独安装 `libtvm_runtime.so`

### F07. 原生库依赖管理

- 依赖库来源目录：`/opt/conda/envs/xmnn/lib`
- 安装目标目录：wheel 包内的 `_libs/` 子目录
- 被打包的依赖库：libLLVM.so.22.1、libz.so.1、libzstd.so.1、libxml2.so.16、libiconv.so.2、libicuuc.so.78、libicudata.so.78
- 符号链接处理：[install_real_lib()](file:///d:/spaces/SpecWeave/external/chaos/xmtools/CMakeLists.txt#L71-L89) 函数通过 `get_filename_component(... REALPATH)` 解析真实文件，安装真实文件后在 install-CODE 中重建符号链接
- RPATH 设置：[CMakeLists.txt](file:///d:/spaces/SpecWeave/external/chaos/xmtools/CMakeLists.txt#L134-L147) 使用 patchelf 将 `_libs/` 下所有 .so 的 RPATH 设置为 `$ORIGIN`

### F08. 引导加载机制

- 引导脚本：[_xmnn_bootstrap.py](file:///d:/spaces/SpecWeave/external/chaos/xmtools/_xmnn_bootstrap.py) 安装到 site-packages 根目录
- 激活方式：[xmnn_bootstrap.pth](file:///d:/spaces/SpecWeave/external/chaos/xmtools/xmnn_bootstrap.pth) 包含单行 `import _xmnn_bootstrap`，Python 启动时自动执行
- 引导脚本职责：设置 `TVM_LIBRARY_PATH`、设置 `LD_LIBRARY_PATH`、`RTLD_GLOBAL` 预加载 libtvm.so、应用 AST Monkey-patch
- `_libs/` 目录存在性检查：引导脚本优先查找 `_libs/` 目录，不存在则降级到包根目录

### F09. CMake 安装规则

- tvm Nuitka 产物：`build/nuitka/tvm.cpython-314-x86_64-linux-gnu.so` → 安装到包根目录
- vta Nuitka 产物：`build/nuitka/vta_out/vta.cpython-314-x86_64-linux-gnu.so` → 安装到包根目录
- TVM C++ 库：`libtvm.so` → 安装到 `_libs/`
- xmnn 源码：`npuusertools/xmnn/` → 安装到 `xmnn/`（.py/.ttf/.pyi 文件，排除 __pycache__/.pyc/tools_cpp/autolibs）
- relay/std 数据：`npu_tvm/python/tvm/relay/std/*.rly` → 安装到 `tvm/relay/std/`
- vta_hw/config 配置：`npu_tvm/vta/vta_hw/config/*.py|*.json` → 安装到 `vta_hw/config/`
- VTA 仿真库：`npu_tvm/build/vta/vta_hw/lib/libvta_fsim*.so` → 安装到 `_libs/`
- wheel.install-dir 设置为 "."（site-packages 根级别安装）

### F10. 构建自动化

- 自动化工具：Invoke（Python 任务自动化）
- 可用任务：init、clean、check_deps、build_tvm、nuitka_tvm、nuitka_vta、build_wheel、verify、build_all
- 一键构建：`build_all` 任务链 pre=[clean, build_tvm, nuitka_tvm, nuitka_vta, build_wheel]
- build_wheel 前置检查：检查 tvm.so、vta.so、libtvm.so 是否存在，缺失则报错提示

### F11. 验证体系

- 验证脚本：[scripts/verify_wheel.py](file:///d:/spaces/SpecWeave/external/chaos/xmtools/scripts/verify_wheel.py)（442行）
- 验证流程：创建临时 venv → 升级 pip → force-reinstall wheel → 执行检查项
- 日志系统：控制台 INFO 级别 + 文件 DEBUG 级别双输出，含时间戳/级别/模块名
- 6项核心检查：import tvm、import vta、import xmnn、tvm.relay 访问、libtvm ctypes 加载、relay/std .rly 文件可访问、vta_hw/config .json 文件可访问
- 计时器：StepTimer 上下文管理器记录每个阶段耗时
- 最终验证结果：6/6 检查通过，wheel 可用

### F12. 遇到并解决的错误列表

| # | 错误现象 | 发生阶段 |
|---|---------|---------|
| E1 | setuptools 残留，不符合用户要求 | 初始方案 |
| E2 | CMake 相对路径解析错误（pyproject.toml 定义的相对路径相对于 build 目录） | CMake 配置 |
| E3 | Nuitka --output-filename=__init__.so 导致模块名不匹配 | Nuitka 编译 |
| E4 | Nuitka --follow-imports 尝试编译标准库模块导致失败 | Nuitka 编译 |
| E5 | 同时加载 libtvm.so 和 libtvm_runtime.so 导致符号重复注册 | 运行时 |
| E6 | Python 3.14 上 ast.NameConstant/Num/Str/Bytes/Index/ExtSlice 不存在 | 导入时 |
| E7 | Windows 命令行长度限制导致长命令被截断 | 命令执行 |
| E8 | Nuitka 编译 .so 安装到 tvm/ 子目录导致 tvm.tvm 嵌套路径 | CMake 安装 |
| E9 | TIRToRuntime 属性未注册，tvm.build(llvm) 失败 | TVM 运行时 |
| E10 | libtvm.so 依赖的 libLLVM/libz 等库在目标环境路径不存在 | 运行时加载 |
| E11 | Nuitka 未嵌入 relay/std 数据文件 | Nuitka 数据包含 |
| E12 | scipy 依赖未声明，TVM 量化模块 ImportError | 依赖声明 |

### F13. 最终文件清单（核心文件）

| 文件 | 行数 | 用途 |
|------|------|------|
| pyproject.toml | 17行 | 构建后端声明、依赖、scikit-build 配置 |
| CMakeLists.txt | 149行 | CMake 构建规则、安装路径、patchelf RPATH |
| tasks.py | 456行 | Invoke 自动化任务（构建/编译/打包/验证） |
| _xmnn_bootstrap.py | 71行 | 运行时引导脚本（环境变量+AST兼容+预加载） |
| xmnn_bootstrap.pth | 1行 | .pth 文件激活引导脚本 |
| scripts/verify_wheel.py | 442行 | 端到端验证脚本 |

---

## I·洞察分析（G2质量门：四元组完整）

### 洞察 I1：Nuitka + .pth 引导优于 `__init__.py` 注入

**陈述**：对于 Nuitka 编译的 Python 包，通过 `.pth` 文件 + 独立 bootstrap 模块设置运行时环境，比向 `__init__.py` 注入代码更可靠、更易维护。

**证据（F04、F08）**：
- Nuitka 将整个 Python 包编译为单个 `.so` 文件，原始 `__init__.py` 内容被编译进二进制，注入的引导代码仅在编译时生效
- 运行时 `__init__.py` 不再被执行（.so 替代了整个包），注入的路径设置代码无法在运行时起作用
- `.pth` 文件在 Python 解释器启动时、任何包 import 之前被处理，确保引导代码最早执行
- xmnn_bootstrap.pth 仅1行（`import _xmnn_bootstrap`），维护成本极低

**反常识**：直觉上在 `__init__.py` 顶部注入代码是最自然的做法，但 Nuitka 编译后这个入口点消失了，必须使用 Python 解释器级别的钩子（.pth 文件）。

**下次行动**：所有 Nuitka 编译的 wheel 包，运行时环境设置（路径、环境变量、Monkey-patch）统一采用 `.pth + bootstrap模块` 模式。

---

### 洞察 I2：CMake 原生库依赖隔离是 wheel 可移植性的关键

**陈述**：将原生依赖库存放在 wheel 包内独立目录（`_libs/`）并设置 `$ORIGIN` RPATH，是解决 Linux wheel 二进制可移植性的可靠方案。

**证据（F07、F08、E10）**：
- libtvm.so 依赖 libLLVM-22、libz、libzstd、libxml2、libiconv、libicuuc、libicudata 共7个系统级共享库
- 目标机器上这些库的版本和路径不可控（conda vs 系统包管理器 vs 自定义路径）
- install_real_lib() 函数处理符号链接（如 libLLVM.so.22 → libLLVM.so.22.1），确保安装真实文件
- patchelf 将 RPATH 设为 `$ORIGIN`，使动态链接器在同目录查找依赖
- 引导脚本通过 `LD_LIBRARY_PATH` 兜底，双重保障

**反常识**：仅设置 `LD_LIBRARY_PATH` 环境变量不足以解决问题，因为 `ctypes.CDLL` 使用 `RTLD_GLOBAL` 加载时，动态链接器的 RPATH/RUNPATH 设置优先级高于环境变量；必须同时用 patchelf 设置 RPATH。

**下次行动**：打包含 C/C++ 原生依赖的 Python wheel 时，固定使用 `_libs/` 目录隔离 + patchelf RPATH + 引导脚本 LD_LIBRARY_PATH 三件套方案。

---

### 洞察 I3：Python 大版本升级的 AST 破坏需要运行时 Monkey-patch 而非源码修改

**陈述**：Python 3.12+ 移除了多个 AST 类（NameConstant/Num/Str/Bytes/Index/ExtSlice），对于无法直接修改源码的第三方库（如 TVM），运行时 Monkey-patch 是最小侵入、最可持续的兼容方案。

**证据（F05、F06、E6）**：
- TVM 源码在多处使用 `ast.NameConstant`、`ast.Num`、`ast.Str` 等类（Python 3.8 时代代码）
- 直接 patch TVM 源码不现实（代码量大、submodule 不可修改、上游合并周期长）
- Monkey-patch 在 import 前定义兼容类：`ast.NameConstant = type("NameConstant", (ast.Constant,), {})` 等
- 双重注入点：编译时注入 PREAMBLE（确保 Nuitka 编译过程不报错）+ 运行时 bootstrap（确保 wheel 安装后使用不报错）
- 6个类中，4个是 Constant 的别名（NameConstant/Num/Str/Bytes），2个需要手动定义 _fields（Index/ExtSlice）

**反常识**：通常认为 Monkey-patch 是反模式，但在"无法修改上游源码 + 必须跨大版本兼容"的约束下，Monkey-patch 反而比 vendor/fork 源码更干净——它是纯加法，不引入代码副本。

**下次行动**：Python 大版本升级遇到被移除的 stdlib API 时，优先评估 Monkey-patch 可行性（类未被删除、仅合并或重命名时可行），而非直接 fork 源码。

---

### 洞察 I4：scikit-build-core + CMake 相比 setuptools 提供了确定性的 wheel 内容控制

**陈述**：scikit-build-core 将 wheel 内容完全交给 CMake `install()` 规则控制，消除了 setuptools 的 `find_packages()`/`package_data` 启发式匹配带来的不确定性。

**证据（F02、F09、E1/E2）**：
- setuptools 的 MANIFEST.in 和 package_data 配置经常出现"本地能跑、wheel缺文件"的问题
- CMake 的 `install(FILES/DIRECTORY ... DESTINATION ...)` 规则是显式的——安装什么、安装到哪里，一目了然
- `FILES_MATCHING PATTERN` 精确控制文件类型（如只安装 .rly 到 tvm/relay/std/）
- CMake 可以在配置阶段做版本检查、路径检查（FATAL_ERROR 立即终止而非打包后才发现问题）
- cmake.define 传入的路径参数在 CMakeLists.txt 中通过 `IS_ABSOLUTE` 检查确保绝对路径解析正确

**反常识**：CMake 是 C/C++ 构建工具，但在 Python wheel 打包场景下，它作为"安装规则引擎"比 setuptools 更合适——因为二进制 wheel 的核心需求就是"精确控制哪些文件放到哪里"，这正是 CMake install 的强项。

**下次行动**：包含原生二进制产物（.so、数据文件、配置文件）的 Python 包，优先选择 scikit-build-core + CMake 而非 setuptools。

---

### 洞察 I5：TVM 的 TIRToRuntime 注册需要启用示例目标钩子

**陈述**：TVM 的 LLVM 代码生成路径依赖 `TIRToRuntime` 属性的注册，该注册通过 `USE_EXAMPLE_TARGET_HOOKS=ON` 启用，而 TVM 的默认 CMake 配置将其设为 OFF。

**证据（F06、E9）**：
- 标准构建流程 `inv config -f && inv make` 生成的 libtvm.so 不包含 TIRToRuntime 注册
- 运行 `tvm.build(llvm)` 时报 AttributeError: module 'tvm.target' has no attribute 'TIRToRuntime'
- TVM 源码中 `example_target_hooks` 是注册 TIRToRuntime 的唯一路径
- 需要在 `inv config -f` 之后、`inv make` 之前补丁 config.cmake
- 该钩子在 TVM 的 CMake 配置中名为 `USE_EXAMPLE_TARGET_HOOKS`，属于 "how-to" 示例性质但实际是 LLVM 后端的必需组件

**反常识**：名为 "example"（示例）的钩子在实际使用中是必需的，而不是可选的演示代码。TVM 的构建配置命名具有误导性。

**下次行动**：从源码构建 TVM 并需要 LLVM 代码生成时，必须显式设置 `USE_EXAMPLE_TARGET_HOOKS=ON`，并在构建文档中将其列为必需步骤。

---

## E·模式萃取（G3质量门：可迁移验证）

### 模式 P1：Nuitka + scikit-build-core 原生 Python Wheel 打包模式

**触发场景**：
- 需要将 Python 包编译为原生扩展（.so）以提升性能、隐藏源码、或消除 Python 源码依赖
- 需要精确控制 wheel 包内容（含二进制库、数据文件、配置文件）
- 不希望使用 setuptools 的隐式打包规则

**核心步骤**：
1. **pyproject.toml 配置**：声明 `build-backend = "scikit_build_core.build"`，通过 `[tool.scikit-build]` 配置 cmake/ninja 版本
2. **Nuitka 预编译**：使用 Invoke/Make 等任务工具在 CMake 配置前完成 Nuitka 编译（`--module --include-package=X --include-data-dir=src=dst`）
3. **CMakeLists.txt 安装规则**：用 `install(FILES/DIRECTORY ... DESTINATION ...)` 显式声明所有安装内容
4. **路径引导**：使用 `.pth` 文件 + bootstrap 模块设置运行时环境变量和 Monkey-patch（而非 `__init__.py` 注入）
5. **依赖库隔离**：将原生依赖放入 `_libs/` 子目录，用 patchelf 设置 `$ORIGIN` RPATH
6. **版本约束**：在 pyproject.toml、CMakeLists.txt、验证脚本三处强制版本检查
7. **验证脚本**：创建临时 venv 安装 wheel 并运行端到端功能测试

**反模式**：
- ❌ 在 Nuitka 编译时使用 `--follow-imports`（会编译标准库导致失败）
- ❌ 使用 `--output-filename` 覆盖模块输出名（Nuitka 模块模式文件名必须匹配模块名）
- ❌ 同时加载 libtvm.so 和 libtvm_runtime.so（符号冲突）
- ❌ 依赖 Nuitka 的 `--include-data-dir` 嵌入数据到 .so（数据路径在运行时不可预测，应通过 CMake 单独安装数据文件）
- ❌ 仅用 LD_LIBRARY_PATH 不设 RPATH（动态链接器不一定遵循环境变量）

**迁移验证**：该模式可迁移到以下场景：
- PyTorch/TensorFlow 自定义算子的 wheel 打包
- 任何 C/C++ 扩展 + Python 封装层的混合包
- 需要内置模型权重/配置文件的 AI 推理包

---

### 模式 P2：Python 大版本 AST 兼容性 Monkey-patch 模式

**触发场景**：
- 第三方库使用了新版本 Python 中已移除的 AST/stdlib API
- 无法或不愿 fork/修改上游源码
- 被移除的 API 可以通过继承新 API 类来兼容

**核心步骤**：
1. 识别被移除的 API：对比目标 Python 版本和源码编写版本的 changelog
2. 分类兼容策略：
   - 简单别名类（合并到父类）：`ast.Xxx = type("Xxx", (ast.ParentClass,), {})`
   - 需要 _fields 的类：手动定义 `_fields` 元组和 `__init__`
3. 双重注入点：编译时注入（确保 Nuitka/Cython 编译通过）+ 运行时注入（.pth 确保 import 前生效）
4. 使用 `hasattr()` 防御检查：`if not hasattr(ast, "NameConstant"):` 避免重复定义
5. 注入位置优先选 .pth 文件（最早执行）而非 `__init__.py`

**反模式**：
- ❌ 直接修改第三方库源码（submodule 不可持续、合并冲突）
- ❌ Vendor 整个第三方库副本（维护成本高、安全更新不同步）
- ❌ 不加 hasattr 检查直接覆盖（破坏已兼容的新版本）

**迁移验证**：该模式可迁移到：
- 任何 Python 大版本升级（3.12→3.13→3.14+）中移除的 AST/typing/collections 等模块 API
- 其他 stdlib 模块的破坏性变更（如 asyncio API 变更、pathlib 变更等）

---

### 模式 P3：Linux Wheel 原生依赖隔离模式

**触发场景**：
- Python wheel 包含需要在目标机器上加载的 .so 文件
- .so 文件依赖非标准的系统共享库（不在 manylinux 规范内）
- 需要 wheel 在不同 Linux 发行版上可移植

**核心步骤**：
1. 创建 `_libs/` 子目录存放所有私有共享库
2. 使用 `get_filename_component(... REALPATH)` 解析符号链接，安装真实文件
3. 在 install-CODE 阶段重建符号链接（如 libLLVM.so.22 → libLLVM.so.22.1）
4. 使用 patchelf 将所有 .so 的 RPATH 设置为 `$ORIGIN`
5. 引导脚本设置 `LD_LIBRARY_PATH` 包含 `_libs/` 作为兜底
6. 使用 `RTLD_GLOBAL` 预加载主库（如 libtvm.so）确保符号全局可见

**反模式**：
- ❌ 将依赖库安装到 site-packages 根目录（污染全局命名空间）
- ❌ 仅安装符号链接不安装真实文件（dpkg 包的符号链接在 wheel 中无效）
- ❌ 仅依赖 LD_LIBRARY_PATH 不设 RPATH（ctypes.CDLL 加载时可能不遵循）
- ❌ 同时安装同一库的两个版本（符号冲突）

**迁移验证**：该模式可迁移到：
- CUDA/cuDNN 等 GPU 运行时库的打包
- 自定义 C++ 扩展依赖的第三方 C++ 库（如 protobuf、grpc）
- 任何需要"batteries-included"的原生 Python 包

---

## 关键决策记录

| 决策 | 选项A | 选项B | 决策结果 | 决策依据 |
|------|-------|-------|---------|---------|
| 构建后端 | setuptools + setup.py | scikit-build-core + CMake | B | 用户明确要求避免 setuptools；CMake 提供确定性安装规则 |
| 引导注入点 | `__init__.py` 顶部注入 | `.pth` + bootstrap 模块 | B | Nuitka 编译后 __init__.py 不被执行；.pth 在解释器启动时最早执行 |
| 运行时库目录 | 包根目录 | `_libs/` 子目录 | B | 避免污染 site-packages 根目录；符号隔离更清晰 |
| AST 兼容方案 | Patch TVM 源码 | Monkey-patch ast 模块 | B | TVM 是 submodule 不可直接修改；Monkey-patch 零侵入 |
| 数据文件方案 | 依赖 Nuitka --include-data-dir | CMake install(DIRECTORY) | B | Nuitka 嵌入数据路径不可预测；CMake 安装路径确定性强 |
| libtvm_runtime.so | 一起安装 | 只安装 libtvm.so | B | libtvm.so 已包含 runtime 符号，两者同时加载导致重复注册 |

---

## 改进建议与原子行动项

### A1（高优先级）：添加构建环境 Dockerfile 固化
- **问题**：当前 LLVM_LIB_DIR 硬编码为 `/opt/conda/envs/xmnn/lib`，构建环境依赖特定 conda 环境
- **建议**：利用已有的 [docker/dev-llvm22/Dockerfile](file:///d:/spaces/SpecWeave/external/chaos/xmtools/docker/dev-llvm22/Dockerfile) 固化构建环境，CI 中直接使用 Docker 构建
- **验收标准**：`docker build` 后 `docker run` 内执行 `inv build-all` 可成功产出 wheel

### A2（中优先级）：添加 manylinux 合规性检查
- **问题**：当前 RPATH 方案可工作但未 auditwheel 验证，可能存在其他未发现的系统库依赖
- **建议**：在 verify_wheel.py 中添加 `auditwheel show` 检查，确认除了已打包的7个库外无其他外部依赖
- **验收标准**：`auditwheel show xmnn-*.whl` 输出仅依赖已打包在 `_libs/` 中的库

### A3（中优先级）：添加 tvm.build(llvm) 端到端计算验证
- **问题**：当前验证仅检查模块导入和库加载，未验证 tvm.build() 生成代码并执行的功能正确性
- **建议**：在 verify_wheel.py 中添加计算图构建+执行测试（如 A[i]*2 → 验证结果）
- **验收标准**：验证脚本输出包含 "tvm.build(llvm) compute test: PASS"

### A4（低优先级）：清理 tasks.py 中 PREAMBLE_TVM 和 PREAMBLE_VTA 的重复代码
- **问题**：两个 PREAMBLE 中 AST Monkey-patch 代码完全重复（60+行重复）
- **建议**：提取 `_AST_COMPAT_PATCH` 常量，两个 PREAMBLE 共用
- **验收标准**：tasks.py 中 AST patch 代码只定义一次

---

## 产物统计

```
Wheel 文件: xmnn-0.1.0-cp314-cp314-linux_x86_64.whl
Wheel 大小: ~169 MB
内容构成:
  - tvm.cpython-314-x86_64-linux-gnu.so  (~123 MB)  Nuitka 编译的 TVM
  - _libs/libtvm.so                      (~76 MB)   TVM C++ 运行时 (注: 压缩后实际占比不同)
  - vta.cpython-314-x86_64-linux-gnu.so  (~12 MB)   Nuitka 编译的 VTA
  - _libs/libLLVM-22.1.so                (~LLVM依赖)
  - _libs/libz.so.1, libzstd.so.1, ...   (~系统依赖)
  - xmnn/                                (~业务代码)
  - tvm/relay/std/*.rly                  (4个文件)   Relay 标准库 Prelude
  - vta_hw/config/                       (JSON+PY)   VTA 硬件配置
  - _xmnn_bootstrap.py                   (71行)      引导脚本
  - xmnn_bootstrap.pth                   (1行)       自动加载钩子
```

---

## 相关报告索引

- [retrospective-xmnn-wheel-packaging-data-dirs-20260722](../bug-fix/docker-build/retrospective-xmnn-wheel-packaging-data-dirs-20260722/README.md) — 早期数据目录问题修复
- [retrospective-xmnn-nuitka-docker-runtime-20260722](../bug-fix/docker-build/retrospective-xmnn-nuitka-docker-runtime-20260722/README.md) — Docker 运行时环境问题
- [retrospective-tvm-llvm-weak-symbol-leak-fix-20260721](../bugfix/retrospective-tvm-llvm-weak-symbol-leak-fix-20260721/README.md) — LLVM 弱符号泄漏修复
