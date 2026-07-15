---
title: "常见问题与最佳实践"
source: "spec:create-scikit-build-core-wiki-tutorial"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/scikit-build-core-wiki/05-faq-and-best-practices.toml"
date: 2026-07-04
tags: [scikit-build-core, faq, best-practices, troubleshooting, ci, conda]
category: "learning"
status: "stable"
author: "SpecWeave"
summary: "汇总 scikit-build-core 真实项目常见问题与故障排查流程，覆盖 CI、Conda、迁移场景最佳实践与调试技巧"
---
# 常见问题与最佳实践

本章汇总 scikit-build-core 在真实项目中最常遇到的问题、对应的故障排查流程，以及在 CI、Conda、迁移等场景下的最佳实践。建议结合 [04 - 入门到进阶指南](04-quickstart-to-advanced.md) 与 [03 - 核心 API 与配置](03-core-api-and-config.md) 一起查阅：前者提供可复制的最小示例，后者是配置项的权威参考。

> 本章所有源码锚点均相对 `external/tools/scikit-build-core/` 根目录，行号与 v0.12.2 同步。

## FAQ 主题清单

以下是 12 个高频问题速查表，每项链接到下文详细解答：

1. [如何启用多线程构建？](#faq-1-如何启用多线程构建)
2. [FindPython 报错怎么办？](#faq-2-findpython-报错怎么办)
3. [如何调试构建过程？](#faq-3-如何调试构建过程)
4. [如何迁移 setup.py 动态选项？](#faq-4-如何迁移-setuppy-动态选项)
5. [wheel 标签是 `linux` 不能上 PyPI 怎么办？](#faq-5-wheel-标签是-linux-不能上-pypi-怎么办)
6. [Conda 打包要注意什么？](#faq-6-conda-打包要注意什么)
7. [Free-threaded Windows 怎么处理？](#faq-7-free-threaded-windows-怎么处理)
8. [`prepare_metadata_*` 为什么被禁用？](#faq-8-prepare_metadata-为什么被禁用)
9. [`minimum-version` 该设什么值？](#faq-9-minimum-version-该设什么值)
10. [`build-system.requires` 要加 `cmake`/`ninja` 吗？](#faq-10-build-systemrequires-要加-cmakeninja-吗)
11. [如何实现"构建失败则回退纯 Python wheel"？](#faq-11-如何实现构建失败则回退纯-python-wheel)
12. [如何注入额外 `build-system.requires`？](#faq-12-如何注入额外-build-systemrequires)

## FAQ 详细解答

### FAQ 1: 如何启用多线程构建

scikit-build-core 默认在 Unix-like 平台使用 Ninja generator，Ninja 自动按机器核心数并行编译。如果需要显式控制并行度，有三种方式：

通过 CMake define 传递（推荐用于 `pip install` 命令行）：

```bash
pip install -Ccmake.define.CMAKE_BUILD_PARALLEL_LEVEL=8 .
```

通过环境变量传递（推荐用于 CI）：

```bash
CMAKE_BUILD_PARALLEL_LEVEL=8 pip install .
```

通过 `[tool.scikit-build.env]` 表转发已有环境变量（`setdefault` 语义，仅在未设置时填入）：

```toml
[tool.scikit-build.env]
CMAKE_BUILD_PARALLEL_LEVEL = { env = "MAX_JOBS", default = "8" }
```

> 配置语义详见 [03 - 核心 API 与配置 - 顶层配置项](03-core-api-and-config.md) 的 `env` 表说明。`setdefault` 表示仅当 CMake 子进程环境中未设置该变量时才注入默认值，已有值不会被覆盖；如需强制覆盖，使用 `force = true`。

### FAQ 2: FindPython 报错怎么办

典型错误信息：`Could NOT find Python` 或请求 `Development.Embed` 组件失败。

**根因**：manylinux 镜像为了体积与兼容性，**不附带 `libpython`**（嵌入库）。`Development` 组件等价于 `Development.Interpreter + Development.Module + Development.Embed`，请求 `Development.Embed` 必然失败。

**正确写法**（仅请求 `Development.Module`）：

```cmake
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
python_add_library(myext MODULE WITH_SOABI main.cpp)
```

**Stable ABI 写法**（CMake 3.26+，通过 `${SKBUILD_SABI_COMPONENT}` 条件注入 `Development.SABIModule`）：

```cmake
find_package(Python
    COMPONENTS Interpreter ${SKBUILD_SABI_COMPONENT} REQUIRED
)
```

`${SKBUILD_SABI_COMPONENT}` 由 `Builder.configure`（`src/scikit_build_core/builder/builder.py#L257`）在 `wheel.py-api` 设为 `cp38` 等 Stable ABI 目标时注入，对应 `${SKBUILD_SABI_VERSION}`（如 `3.8`）。详见 [03 - 核心 API 与配置 - CMakeLists.txt 集成示例](03-core-api-and-config.md)。

### FAQ 3: 如何调试构建过程

scikit-build-core 默认日志级别为 `WARNING`，且 `pip` 会吞掉大部分输出。调试三件套：

1. **`pip` 必须加 `-v`**（否则输出被静默）：

   ```bash
   pip install -ve .
   ```

2. **提高 scikit-build-core 日志级别**：

   ```bash
   pip install -v -Cskbuild.logging.level=INFO .
   # 或 DEBUG
   pip install -v -Cskbuild.logging.level=DEBUG .
   ```

3. **打印当前所有设置与 wheel 标签**（无需构建）：

   ```bash
   scikit-build builder            # 输出 Python/CMake/Ninja 版本与全部 settings
   scikit-build builder wheel-tag # 计算并输出 wheel 标签
   scikit-build builder sysconfig  # 输出 sysconfig 信息
   ```

   CLI 子命令注册于 `src/scikit_build_core/__main__.py#L37`。

4. **关闭 build isolation 以保留构建目录**（用于 gcov/GDB/IDE 调试）：

   ```bash
   pip install --no-build-isolation -Cbuild-dir=build -ve .
   ```

   `build-dir` 指定持久构建目录后，`compile_commands.json`、`.gcno`/`.gcda`、DWARF 调试信息都会保留在 `build/` 下，便于 `gcovr -r . build`、GDB、clangd 等工具使用。

### FAQ 4: 如何迁移 setup.py 动态选项

setuptools 已弃用 `setup.py` 中的自定义命令选项。迁移到 scikit-build-core 有两种典型路径：

**路径 A**：转为 CMake option，通过 `-Ccmake.define.<NAME>=<value>` 传递：

```toml
# pyproject.toml
[tool.scikit-build]
cmake.define = { MY_FEATURE = "ON" }
```

```bash
# 命令行覆盖
pip install -Ccmake.define.MY_FEATURE=OFF .
```

**路径 B**：使用 `[[tool.scikit-build.overrides]]` 按条件配置（平台、Python 版本、环境变量等）：

```toml
[[tool.scikit-build.overrides]]
if.platform-machine = "arm64"
cmake.define.MY_FEATURE = "ON"

[[tool.scikit-build.overrides]]
if.env.CI = "true"
cmake.build-type = "Debug"
```

`process_overrides`（`src/scikit_build_core/settings/skbuild_overrides.py#L38`）支持 12 种 `if` 选择器，详见 [03 - 核心 API 与配置 - Overrides 系统](03-core-api-and-config.md)。

> 如果上述两种方式无法满足需求，请到 <https://github.com/scikit-build/scikit-build-core/issues> 反馈用例。

### FAQ 5: wheel 标签是 `linux` 不能上 PyPI 怎么办

scikit-build-core 与大多数后端一样，默认产出 `linux_x86_64` 标签的 wheel，这种 wheel **不可上传到 PyPI**（PEP 513/571/599 不允许）。需通过 wheel 修复工具转为 `manylinux_*` 或 `musllinux_*` 标签：

| 平台 | 工具 | 产物 |
|---|---|---|
| Linux | `auditwheel` | `manylinux_*` / `musllinux_*` |
| macOS | `delocate` | 修复动态库依赖，可选 universal2 |
| Windows | `delvewheel` | 修复 DLL 依赖 |
| 跨平台统一 | `repairwheel` | 自动选择上述工具 |
| CI 一站式 | `cibuildwheel` | 自动构建 + 修复 + 矩阵 |

`cibuildwheel` 会自动调用对应平台的修复工具，详见 [CI 集成最佳实践 - cibuildwheel 集成](#cibuildwheel-集成)。

> 例外：ARMv6 等无 manylinux 规范的平台可上传 `linux_*` 标签 wheel，详见 [PEP 599 备注](https://peps.python.org/pep-0599/)。

### FAQ 6: Conda 打包要注意什么

scikit-build-core 已发布到 conda-forge，被数十个配方使用。关键要点：

- `host` 表重建 `build-system.requires` 的 conda 版本
- `build` 表显式加 `cmake` 和 `make`/`ninja`
- `scikit-build-core` 配方自身**不能**依赖 `cmake`/`make`/`ninja`，否则会进错表（`host` 而非 `build`）
- conda-build 在 UNIX 系统硬编码 `CMAKE_GENERATOR="Unix Makefiles"`，若想用 Ninja 需手动 `unset CMAKE_GENERATOR` 或显式 `export CMAKE_GENERATOR=Ninja`

完整 `meta.yaml` 示例见 [Conda 打包最佳实践](#conda-打包最佳实践)。

### FAQ 7: Free-threaded Windows 怎么处理

Windows 上自由线程（free-threaded，Python 3.13t+）构建需手动添加 C 定义 `Py_GIL_DISABLED`。原因：自由线程构建与普通构建共享同一份 Python 配置头文件，Python 无法在头文件层面区分两种构建，因此 `Py_GIL_DISABLED` 必须由项目方在 CMake 中显式定义。

`CMakeLists.txt` 写法：

```cmake
if(WIN32 AND SKBUILD_ABI_FLAGS MATCHES "t")
    add_compile_definitions(Py_GIL_DISABLED)
endif()
```

`${SKBUILD_ABI_FLAGS}` 由 `Builder.configure`（`src/scikit_build_core/builder/builder.py#L257`）注入，含 `t` 表示自由线程。Linux/macOS 不需要此处理，因为 Python 头文件已正确区分。

`pyproject.toml` 启用 abi3t（free-threaded Stable ABI）：

```toml
[tool.scikit-build]
wheel.py-api = "cp315.cp315t"
```

详见 [04 - 入门到进阶指南 - abi3t](04-quickstart-to-advanced.md)。

### FAQ 8: prepare_metadata_* 为什么被禁用

PEP 517 的 `prepare_metadata_for_build_wheel` 钩子用于在不构建 wheel 的情况下输出元数据，pip 在解析依赖时优先调用此钩子以加速安装。

scikit-build-core 在 `_has_safe_metadata()`（`src/scikit_build_core/build/__init__.py#L77-L90`）中扫描 `tool.scikit-build.overrides[].if.failed`：**若存在 `if.failed=true` override，则禁用 `prepare_metadata_*` 钩子**。

**原因**：`prepare_metadata_*` 在"快速元数据阶段"运行，不会真正触发 CMake 构建；而 `if.failed=true` 的语义是"构建失败后回退到纯 Python wheel"。如果允许 `prepare_metadata_*` 在元数据阶段提前"成功"，pip 会缓存该元数据，后续真实构建失败时无法触发回退逻辑。禁用后，pip 必须走完整的 `build_wheel` 路径，才能让 `if.failed` 重试机制生效。

启用 `if.failed` 后，日志中会出现 `prepare_metadata_for_build_wheel is disabled due to unsafe overrides` 提示，属正常行为。

### FAQ 9: minimum-version 该设什么值

`minimum-version` 是向后兼容门，推荐设为 `"build-system.requires"`：

```toml
[tool.scikit-build]
minimum-version = "build-system.requires"
```

**`"build-system.requires"` 的含义**：自动以 `build-system.requires` 中声明的 `scikit-build-core` 版本下限作为 `minimum-version`，无需手动同步两处版本号。例如 `requires = ["scikit-build-core >=0.10"]` 等价于 `minimum-version = "0.10"`。

**避免 upper cap**：不要写 `scikit-build-core <0.13` 这种上限约束。scikit-build-core 遵循语义化版本，minor 版本向后兼容，upper cap 会阻碍用户升级。如确实需要回避某个回归，用 `!=0.12.0` 等精确排除。

**版本行为差异**（关键变更）：

| 版本 | 重要变更 |
|---|---|
| 0.10 | `cmake.minimum-version`/`ninja.minimum-version` 重命名为 `cmake.version`/`ninja.version`（完整 specifier set）；`cmake.verbose`/`cmake.targets` 重命名为 `build.verbose`/`build.targets`；`wheel.packages` 支持 table 形式；新增 `from-sdist`/`system-cmake`/`cmake-wheel`/`failed` override 条件 |
| 0.11 | 新增 `build.requires` 动态注入；`metadata.template` provider；改进 fancy-pypi-readme 版本号支持 |
| 0.12 | 新增 `sdist.inclusion-mode`（默认 `default`，不再遍历被忽略目录，更快更可预测；`classic` 为旧行为，`manual` 不读 gitignore）；改进交叉编译支持；支持 fancy-pypi-readme 25.1 |

### FAQ 10: build-system.requires 要加 cmake/ninja 吗

**不要手动加 `cmake`/`ninja`/`setuptools`/`wheel`**。scikit-build-core 通过 `GetRequires` 类（`src/scikit_build_core/builder/get_requires.py#L56`）智能判断并按需注入：

- `GetRequires.cmake()`：根据 `cmake.version` specifier 决定是否注入 PyPI `cmake` 包
- `GetRequires.ninja()`：根据 `ninja.version` specifier 与 `ninja.make-fallback` 决定是否注入 PyPI `ninja` 包
- `setuptools`/`wheel` 仅 setuptools 兼容层需要，原生后端不需要

**例外**（系统已装版本优先，不注入 PyPI 版本）：Android、FreeBSD、WebAssembly、ClearLinux 等环境无法安装 PyPI `cmake`/`ninja` wheel，但通常已预装系统版本。scikit-build-core 通过 `system-cmake` override 条件检测系统 CMake 版本。

如需指定最低版本，用 `[tool.scikit-build]` 表的 `cmake.version` 与 `ninja.version`：

```toml
[tool.scikit-build]
cmake.version = ">=3.18"
ninja.version = ">=1.10"
```

`cmake.version` 还可填 `"CMakeLists.txt"`，自动从 `cmake_minimum_required(...)` 解析最低版本（`SettingsReader` 调用 `find_min_cmake_version` 实现）。

### FAQ 11: 如何实现构建失败则回退纯 Python wheel

0.10+ 支持 `if.failed=true` override，实现"构建失败则回退纯 Python wheel"策略。典型场景：纯 Python 实现作为 fallback，C 扩展作为加速可选。

```toml
[tool.scikit-build]
wheel.cmake = true  # 默认尝试 CMake 构建

# 失败回退：关闭 CMake，构建纯 Python wheel
[[tool.scikit-build.overrides]]
if.failed = true
wheel.cmake = false
```

工作流程：

1. pip 调用 `build_wheel`，scikit-build-core 尝试 CMake 构建
2. 若 CMake 构建失败，scikit-build-core 内部捕获异常，重新求值 `if.failed=true` override
3. 应用 `wheel.cmake = false`，重新执行构建（这次跳过 CMake，纯 Python 打包）
4. 输出纯 Python wheel

> 注意：`if.failed` 触发的重试仅一次。重试仍失败则抛出原始异常。同时启用 `if.failed` 会禁用 `prepare_metadata_*` 钩子（详见 [FAQ 8](#faq-8-prepare_metadata-为什么被禁用)）。

### FAQ 12: 如何注入额外 build-system.requires

0.11+ 新增 `build.requires` 配置项，可动态注入额外 `build-system.requires`。典型用途：源码构建用本地路径依赖，SDist 构建用 PyPI 版本（避免 SDist 包含本地路径引用）。

```toml
[tool.scikit-build]
# 默认（PyPI 构建）：从 PyPI 安装 pybind11
build.requires = ["pybind11 >=2.12"]

# SDist 构建时：用本地路径的 pybind11
[[tool.scikit-build.overrides]]
if.state = "sdist"
build.requires = ["pybind11 @ file:///tmp/pybind11"]
```

`build.requires` 与 `build-system.requires` 的区别：

| 字段 | 静态/动态 | 用途 |
|---|---|---|
| `build-system.requires` | 静态 | 在 `pyproject.toml` 顶层声明，pip 隔离环境安装 |
| `build.requires` | 动态 | 由 `GetRequires` 在 `get_requires_for_build_*` 钩子返回，可被 overrides 条件控制 |

`GetRequires` 类（`src/scikit_build_core/builder/get_requires.py#L56`）统一返回 `build-system.requires` + `build.requires` + 智能注入的 `cmake`/`ninja` + 动态元数据 provider 依赖。

## 跨平台编译故障排查

### 故障排查决策流程

遇到构建失败时，按以下决策流程定位错误类型并找到对应解决方案：

```mermaid
flowchart TD
    A["构建失败：从错误信息定位"] --> B{"错误类型？"}
    B -->|"Could NOT find Python"| C["FindPython 错误"]
    B -->|"Python_SOABI 不匹配"| D["SOABI 错误"]
    B -->|"Could NOT find Ninja / Make"| E["Generator 程序查找失败"]
    B -->|"linux 标签不可上 PyPI"| F["Wheel 标签问题"]
    B -->|"import 失败：.so/.dll 找不到"| G["动态库依赖问题"]
    B -->|"MSVC：build/Release/ 路径不存在"| H["多配置 Generator 路径问题"]
    C --> C1["仅请求 Development.Module"]
    C1 --> C2["manylinux 禁用 Development.Embed"]
    D --> D1["使用 ${SKBUILD_SOABI}"]
    D1 --> D2["或 set("Python_SOABI ${SKBUILD_SOABI}")"]
    E --> E1["检查 cmake.version / ninja.version"]
    E1 --> E2["查 scikit-build builder 输出"]
    F --> F1["auditwheel / delocate / delvewheel"]
    F1 --> F2["或 cibuildwheel 自动修复"]
    G --> G1["用 install(TARGETS) 而非按路径"]
    G1 --> G2["考虑静态链接 / wheel 修复工具"]
    H --> H1["用 $<TARGET_FILE:t> 生成器表达式"]
    H1 --> H2["或 set *_OUTPUT_DIRECTORY 加 $<0:>"]
```

### FindPython 常见错误

详见 [FAQ 2](#faq-2-findpython-报错怎么办)。核心规则：仅请求 `Development.Module`，manylinux 缺 `libpython` 不能请求 `Development.Embed`。

### SOABI 错误

交叉编译时 CMake 的 `Python_SOABI` 变量可能返回错误值（如目标平台扩展名后缀与构建平台不一致）。scikit-build-core 知道正确的 SOABI，并通过 `Builder.configure`（`src/scikit_build_core/builder/builder.py#L257`）注入 `${SKBUILD_SOABI}`。

推荐写法：

```cmake
# 覆盖 FindPython 的错误 SOABI
if(DEFINED SKBUILD_SOABI)
    set(Python_SOABI ${SKBUILD_SOABI})
endif()

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
python_add_library(myext MODULE WITH_SOABI main.cpp)
```

> `set(Python_SOABI ${SKBUILD_SOABI})` 在 `find_package(Python)` **之前**调用，可强制 FindPython 使用正确值。非官方支持但实际有效。

### macOS 跨编译

Apple Silicon（M1/M2/M3）跨编译的关键点：

- `ARCHFLAGS="-arch arm64"` 触发 `CMAKE_OSX_ARCHITECTURES`，由 `Builder.configure` 解析
- universal2 wheel：`ARCHFLAGS="-arch arm64 -arch x86_64"` + `wheel.expand-macos-universal-tags = true`
- macOS 版本字符串由 `normalize_macos_version`（`src/scikit_build_core/builder/macos.py`）归一化，处理 `12.0`、`macosx-12-arm64` 等格式
- `delocate` 修复 macOS wheel 的动态库依赖

```bash
# Apple Silicon 原生构建
ARCHFLAGS="-arch arm64" pip install .

# universal2 wheel（需在 Apple Silicon 上构建）
ARCHFLAGS="-arch arm64 -arch x86_64" python -m build --wheel
```

### Windows 特殊处理

- **Free-threaded**：手动 `Py_GIL_DISABLED` C 定义，详见 [FAQ 7](#faq-7-free-threaded-windows-怎么处理)
- **MSVC vs Ninja generator**：Visual Studio generator 是多配置 generator，产物路径含 `Release/` 子目录（详见下文"多配置 Generator 路径问题"）；可通过 `CMAKE_GENERATOR=Ninja` 切换为单配置 generator
- **DLL 依赖修复**：`delvewheel` 修复 Windows wheel 的 DLL 依赖

```bash
# 强制使用 Ninja generator（需在 Developer Command Prompt 中运行）
set CMAKE_GENERATOR=Ninja
pip install .
```

### 多配置 Generator 路径问题

Visual Studio、Xcode、Ninja Multi-Config 是多配置 generator，把每个 target 的构建产物放在按配置命名的子目录中（如 `build/Release/main.exe` 而非 `build/main.exe`）。这会导致按路径引用构建产物的 CMake 代码失败。

**两条可移植规则**：

1. **用 `install(...)` 而非按路径引用**：install 步骤会剥离 per-config 子目录，scikit-build-core 只把 install tree 复制进 wheel。需要引用 target 真实路径时用 `$<TARGET_FILE:main>` 生成器表达式。

   ```cmake
   add_executable(main main.cpp)
   install(TARGETS main DESTINATION ${SKBUILD_SCRIPTS_DIR})
   ```

2. **`*_OUTPUT_DIRECTORY` 加空生成器表达式 `$<0:>`**：避免多配置 generator 把配置子目录加回来。

   ```cmake
   set_target_properties(mymod PROPERTIES
       LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/mypkg$<0:>"
   )
   ```

## 依赖管理最佳实践

### build-system.requires 规则

**核心规则**：不要手动加 `cmake`/`ninja`/`setuptools`/`wheel`。详见 [FAQ 10](#faq-10-build-systemrequires-要加-cmakeninja-吗)。

最小 `build-system.requires` 示例（pybind11 项目）：

```toml
[build-system]
requires = ["scikit-build-core >=0.10", "pybind11 >=2.12"]
build-backend = "scikit_build_core.build"
```

### build.requires 动态注入（0.11+）

详见 [FAQ 12](#faq-12-如何注入额外-build-systemrequires)。`build.requires` 用于按条件注入额外构建依赖，与 overrides 配合可实现"源码构建用本地路径，SDist 构建用 PyPI"等模式。

### 动态元数据 provider 选择

scikit-build-core 内置 4 个动态元数据 provider，注册于 `pyproject.toml#L95-L98`：

| Provider | 适用字段 | 适用场景 |
|---|---|---|
| `scikit_build_core.metadata.setuptools_scm` | `version` | git 项目首选，从 git tag 或 `.git_archival.txt` 读版本 |
| `scikit_build_core.metadata.regex` | `version` | 非 git 项目或自定义版本文件（如从 `__init__.py` 抽 `__version__`），支持 `result`/`remove` 后处理（0.10+） |
| `scikit_build_core.metadata.fancy_pypi_readme` | `readme` | 复杂 README 渲染，包装 hatch-fancy-pypi-readme |
| `scikit_build_core.metadata.template` | 任意字段 | 跨字段模板填充（0.11.2+） |

`get_standard_metadata`（`src/scikit_build_core/build/metadata.py#L53`）处理流程：先处理 legacy `tool.scikit-build.metadata` 表，再处理新式 `[[tool.dynamic-metadata]]`，最后调用 vendored `pyproject_metadata` 解析 PEP 621 元数据。

**第三方 provider 注意事项**：需 `experimental = true`，接口可能在 minor 版本间变化。

### generate[] 文件生成

`[[tool.scikit-build.generate]]` 用 `string.Template` 把元数据写到文件，常用于生成 `_version.py`：

```toml
[[tool.scikit-build.generate]]
path = "src/myproject/_version.py"
template = '''
__version__ = "${version}"
'''
location = "source"  # source 会自动加入 sdist.include 并覆盖现有文件
```

`generate_file_contents`（`src/scikit_build_core/build/generate.py#L20`）实现模板渲染。`location` 取值：`install`（写入 wheel 安装目录）/`build`（写入构建目录）/`source`（写入源码目录，会进 sdist）。

## 可编辑安装故障排查

scikit-build-core 支持两种可编辑安装模式，由 `editable.mode` 配置项控制：

### redirect 模式（默认）

工作原理：`editable_redirect`（`src/scikit_build_core/build/_editable.py#L48`）读取 `resources/_editable_redirect.py` 模板，生成 `.pth` 文件 + `_editable_skbc_<pkg>.py` shim，使用 `sys.meta_path` 映射 import；若 `editable.rebuild = true`，import 时触发 CMake 重建。

**常见问题**：

- **redirect 失败**：检查 `.pth` 文件是否在 `site-packages/` 下，文件名形如 `_<pkg>_skbc_editable.pth`
- **rebuild 不触发**：检查 `editable.rebuild = true` 是否设置，且 `editable.rebuild-dir` 指向有效的 CMake 构建目录（默认 `build/{wheel_tag}`）
- **import 报错找不到模块**：检查 `wheel.packages` 是否正确声明，scikit-build-core 据此生成 import 映射

调试命令：

```bash
pip install -ve . -Cskbuild.editable.verbose=true
# 查看 .pth 与 shim 文件位置
python -c "import sys; print([p for p in sys.path if 'skbc' in p.lower()])"
```

### inplace 模式

简单 `.pth` 指向源码包目录，无 `sys.meta_path` 重定向。

**限制**：

- **不支持 CMake 重建**：`editable.rebuild = true` 在 inplace 模式下无效
- **要求源码目录布局与安装布局一致**：扩展模块 `.so`/`.pyd` 必须直接位于源码包目录下，由 CMake `install(...)` 或 `*_OUTPUT_DIRECTORY` 显式放置
- **多配置 generator 不兼容**：MSVC 等多配置 generator 会把产物放在 `Release/` 子目录，破坏 inplace 假设；需用 `set_target_properties(... LIBRARY_OUTPUT_DIRECTORY "src/mypkg$<0:>")` 强制扁平化

```toml
[tool.scikit-build.editable]
mode = "inplace"
```

### 可编辑安装通用排查步骤

1. 确认 `pip install -ve .` 输出中 `editable.mode` 与预期一致
2. 用 `scikit-build builder` 打印 settings，确认 `editable.rebuild` / `editable.rebuild-dir` 值
3. 检查 `site-packages/` 下 `.pth` 文件内容（应指向源码包目录或包含 `_editable_skbc_` shim 引用）
4. 修改源码后重新 `import`，观察是否触发 rebuild（`editable.verbose = true` 会输出 rebuild 日志）

## CI 集成最佳实践（GitHub Actions）

### 基本 workflow 示例

以下是一个完整可复制的 GitHub Actions workflow，覆盖 Python 3.9-3.13 与三大操作系统：

```yaml
name: build-wheels
on:
  push:
    branches: [main]
  pull_request:
  release:
    types: [published]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python: ["3.9", "3.10", "3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # setuptools-scm 需要 git history
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - name: Install build tooling
        run: python -m pip install -U pip build
      - name: Build wheel and sdist
        run: python -m build
      - uses: actions/upload-artifact@v4
        with:
          name: dist-${{ matrix.os }}-${{ matrix.python }}
          path: dist/*
```

**关键要点**：

- `fetch-depth: 0`：完整 git history，`setuptools_scm` 等 provider 需要
- `fail-fast: false`：单矩阵失败不取消其他矩阵
- `python -m build`：默认先 SDist 后 Wheel，符合 PyPI 上传规范

### cibuildwheel 集成

`cibuildwheel` 自动处理跨平台 wheel 构建、manylinux/musllinux 修复、Apple Silicon 交叉编译，是发布二进制 wheel 的标准工具：

```yaml
name: release-wheels
on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  build_wheels:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Build wheels
        uses: pypa/cibuildwheel@v2.21
        env:
          CIBW_BUILD: "cp39-* cp310-* cp311-* cp312-* cp313-*"
          CIBW_SKIP: "*-musllinux_* *i686*"
          CIBW_ARCHS_MACOS: "x86_64 arm64"
          CIBW_MANYLINUX_X86_64_IMAGE: manylinux2014
          CIBW_BUILD_VERBOSITY: 1
      - uses: actions/upload-artifact@v4
        with:
          name: cibw-wheels-${{ matrix.os }}
          path: wheelhouse/*.whl

  build_sdist:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - run: pipx run build --sdist
      - uses: actions/upload-artifact@v4
        with:
          name: sdist
          path: dist/*.tar.gz

  upload:
    needs: [build_wheels, build_sdist]
    runs-on: ubuntu-latest
    if: github.event_name == 'release'
    steps:
      - uses: actions/download-artifact@v4
        with:
          path: dist
          merge-multiple: true
      - uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

**关键配置说明**：

- `CIBW_BUILD`：限定构建的 wheel 标签（cp39-cp313）
- `CIBW_SKIP`：跳过 musllinux 与 i686（按需调整）
- `CIBW_ARCHS_MACOS`：macOS 同时构建 x86_64 与 arm64（universal2 由 `cibuildwheel` 内部处理或通过 `wheel.expand-macos-universal-tags` 配置）
- `CIBW_BUILD_VERBOSITY`：构建日志详细度

### 缓存策略

scikit-build-core 的 `build-dir` 配置可持久化 CMake 构建目录，配合 GitHub Actions `actions/cache` 可显著缩短二次构建时间：

```toml
# pyproject.toml
[tool.scikit-build]
build-dir = "build/{wheel_tag}"
```

```yaml
# .github/workflows/build.yml
- uses: actions/cache@v4
  with:
    path: build
    key: ${{ runner.os }}-${{ matrix.python }}-${{ hashFiles('CMakeLists.txt', 'pyproject.toml', 'src/**/*.cpp') }}
    restore-keys: |
      ${{ runner.os }}-${{ matrix.python }}-
```

**关键要点**：

- `build-dir = "build/{wheel_tag}"`：`{wheel_tag}` 占位符确保不同 wheel 标签使用独立构建目录，避免缓存污染
- `key` 含 CMakeLists.txt 与 pyproject.toml 的 hash，配置变更时自动失效
- `restore-keys` 提供 fallback：完全 key 未命中时按前缀恢复，部分命中优于全无
- scikit-build-core 通过 `.skbuild-info.json` 检测 stale cache，配置变更即使 key 命中也会重新 configure

### Free-threaded CI

Python 3.13t（free-threaded）CI 矩阵配置：

```yaml
matrix:
  include:
    - os: ubuntu-latest
      python: "3.13t"
      free-threaded: true
    - os: macos-latest
      python: "3.13t"
      free-threaded: true
    # Windows 需手动 Py_GIL_DISABLED
    - os: windows-latest
      python: "3.13t"
      free-threaded: true
      cmake-define: "Py_GIL_DISABLED=ON"
```

`pyproject.toml` 配置：

```toml
[tool.scikit-build]
wheel.py-api = "cp315.cp315t"  # 同时支持普通与自由线程

[[tool.scikit-build.overrides]]
if.platform-system = "Windows"
if.env.PY_GIL_DISABLED = "1"
cmake.define.Py_GIL_DISABLED = "ON"
```

> `actions/setup-python@v5` 已支持 `python-version: "3.13t"`，会自动安装自由线程版本。详见 [actions/setup-python 文档](https://github.com/actions/setup-python)。

## Conda 打包最佳实践

完整 `recipe/meta.yaml` 示例（基于官方 FAQs）：

```yaml
{% set name = "myproject" %}
{% set version = load_file_regex(load_file="pyproject.toml",
    regex_pattern='version = "([^"]+)"')[1] %}

package:
  name: {{ name|lower }}
  version: {{ version }}

source:
  path: ..

build:
  script:
    - {{ PYTHON }} -m pip install . -vv

requirements:
  build:
    - python                              # [build_platform != target_platform]
    - cross-python_{{ target_platform }}  # [build_platform != target_platform]
    - {{ compiler('c') }}
    - {{ stdlib('c') }}
    - {{ compiler('cxx') }}
    - cmake >=3.15
    - make                                 # [not win]
  host:
    - python
    - pip
    - scikit-build-core >=0.12
  run:
    - python

test:
  imports:
    - myproject
```

**关键要点**：

1. **`host` 表重建 `build-system.requires`**：用 conda 版本替换 PyPI 版本（`scikit-build-core >=0.12`、`pybind11` 等）
2. **`build` 表加 `cmake` 和 `make`/`ninja`**：scikit-build-core 在 conda 环境下不注入 PyPI `cmake`/`ninja`（因 `scikit-build-core` 配方不能依赖它们，会进错表），由 conda 配方显式声明
3. **conda-build 在 UNIX 硬编码 `CMAKE_GENERATOR="Unix Makefiles"`**：若想用 Ninja，需在 `build.script` 中 `unset CMAKE_GENERATOR` 或显式 `export CMAKE_GENERATOR=Ninja`：

   ```yaml
   build:
     script:
       - unset CMAKE_GENERATOR  # [unix]
       - {{ PYTHON }} -m pip install . -vv
   ```

4. **交叉编译**：`build_platform != target_platform` 条件保证交叉编译时 `build` 表包含 `python` 与 `cross-python_{{ target_platform }}`

## 从 classic scikit-build 迁移

### 配置变更

#### build-backend 与 requires

```toml
# 迁移前
[build-system]
requires = ["scikit-build", "cmake", "ninja"]
build-backend = "skbuild"

# 迁移后
[build-system]
requires = ["scikit-build-core >=0.10"]
build-backend = "scikit_build_core.build"
```

变更要点：

- `build-backend` 改为 `scikit_build_core.build`
- `requires` 中 `scikit-build` 改为 `scikit-build-core`
- **移除 `cmake` 与 `ninja`**：scikit-build-core 智能注入，详见 [FAQ 10](#faq-10-build-systemrequires-要加-cmakeninja-吗)
- 用 `[tool.scikit-build]` 表的 `cmake.version` 与 `ninja.version` 指定最低版本

#### setup.py / setup.cfg 迁移

把 setup.py / setup.cfg 配置迁移到 `pyproject.toml` 的 `[project]` 表（PEP 621）。

**迁移技巧**（来自官方文档）：临时把 `build-backend` 改为 `setuptools`，安装 `hatch`，运行 `hatch new --init` 自动迁移配置到 `pyproject.toml`，再把 `build-backend` 改回 `scikit_build_core.build`。

```bash
# 临时改 build-backend = "setuptools"
pip install hatch
hatch new --init  # 自动迁移 setup.py/cfg 到 pyproject.toml
# 改回 build-backend = "scikit_build_core.build"
```

#### MANIFEST.in 改用 sdist.include / sdist.exclude

scikit-build-core 默认包含所有未被 `.gitignore` 忽略的文件，因此 `MANIFEST.in` 通常可以删除。如需显式包含/排除：

```toml
[tool.scikit-build.sdist]
include = ["third_party/*.h"]
exclude = ["tests/*", "docs/*"]
```

`include` / `exclude` 使用 gitignore 语法。`sdist.inclusion-mode`（0.12+）控制包含模式：`default`（默认，不遍历被忽略目录）/ `classic`（旧行为）/ `manual`（不读 gitignore，完全手动）。

### CMake 变更

#### 移除 PythonExtensions 模块

classic scikit-build 的 `PythonExtensions` 模块在 scikit-build-core 中不存在，改用 CMake 内置的 `find_package(Python)` + `python_add_library`：

```cmake
# 迁移前（classic scikit-build）
find_package(PythonExtensions REQUIRED)
add_library(${LIBRARY} MODULE ${FILENAME})
python_extension_module(${LIBRARY})

# 迁移后（scikit-build-core）
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
python_add_library(${LIBRARY} MODULE WITH_SOABI ${FILENAME})
```

#### UseCython 模块

classic scikit-build 的 `UseCython` 模块由独立 CMake 包 [cython-cmake](https://github.com/scikit-build/cython-cmake) 替代。把 `cython-cmake` 加入 `build-system.requires`，CMakeLists.txt 中 `include(UseCython)` 并调用 `cython_transpile`。

Fortran 类似：用独立包 [f2py-cmake](https://github.com/scikit-build/f2py-cmake) 替代，`include(UseF2Py)`。

#### 环境变量重命名

| classic scikit-build | scikit-build-core | 说明 |
|---|---|---|
| `SKBUILD_CONFIGURE_OPTIONS` | `SKBUILD_CMAKE_ARGS` | 配置阶段 CMake 参数（setuptools 兼容层仍支持旧名） |
| `SKBUILD_BUILD_OPTIONS` | （不支持） | 用 `CMAKE_BUILD_PARALLEL_LEVEL` 控制并行，`SKBUILD_CMAKE_VERBOSE` 控制详细输出 |

```bash
# 迁移前
export SKBUILD_CONFIGURE_OPTIONS="-DBUILD_TESTS=ON"
export SKBUILD_BUILD_OPTIONS="-j8"

# 迁移后
export SKBUILD_CMAKE_ARGS="-DBUILD_TESTS=ON"
export CMAKE_BUILD_PARALLEL_LEVEL=8
```

## 调试方法

### 日志与设置打印

| 方法 | 命令 | 用途 |
|---|---|---|
| 提高 pip 详细度 | `pip install -ve .` | 显示 scikit-build-core 全部输出 |
| 提高日志级别 | `-Cskbuild.logging.level=DEBUG` | 显示 DEBUG 级别日志 |
| 构建详细输出 | `-Cbuild.verbose=true` | 显示 CMake --build 完整输出 |
| 打印当前 settings | `scikit-build builder` | 不构建，仅打印 Python/CMake/Ninja 版本与全部 settings |
| 查看 wheel 标签 | `scikit-build builder wheel-tag` | 计算并打印 wheel 标签 |
| 查看 sysconfig | `scikit-build builder sysconfig` | 打印 sysconfig 信息 |
| 查看 file-api 响应 | `scikit-build file-api query <build_dir>` 然后 `scikit-build file-api reply <reply_dir>` | 解析 CMake File API 响应 |

CLI 子命令注册于 `src/scikit_build_core/__main__.py#L37`，4 个顶层子命令：`build` / `builder` / `file-api` / `init`。

### 持久构建目录调试

默认构建目录是临时的，构建后删除。调试时需持久化：

```bash
pip install --no-build-isolation -Cbuild-dir=build -ve .
```

或在 `pyproject.toml` 中固定：

```toml
[tool.scikit-build]
build-dir = "build"
```

持久化后可用：

- `gcovr -r . build`：覆盖率分析
- `gdb`：DWARF 调试信息保留
- `clangd` 或 VSCode C/C++ extension：通过 `build/compile_commands.json` 提供 IntelliSense

导出 compile_commands.json：

```bash
pip install --no-build-isolation --check-build-dependencies -ve . \
  -Cbuild-dir=build \
  -Ccmake.define.CMAKE_EXPORT_COMPILE_COMMANDS=1
```

### Windows Debug 构建

`cmake.build-type=Debug` 构建的扩展链接 debug CPython（`pythonXY_d.dll`、`_d.pyd` 后缀），只能在 debug 解释器 `python_d.exe` 下加载。在普通 `python.exe` 下 import 会崩溃（`0x80000003`）。

**保留调试信息但能在普通 Python 下加载**：在 CPython 头文件周围临时 undef `_DEBUG`，避免自动链接 `pythonXY_d.lib`：

```c
#ifdef _DEBUG
#  define SKB_RESTORE_DEBUG
#  undef _DEBUG
#endif
#include <Python.h>
#ifdef SKB_RESTORE_DEBUG
#  define _DEBUG
#endif
```

## 最佳实践清单

1. **`build-system.requires` 只写 scikit-build-core 与语言绑定库**，不写 `cmake`/`ninja`/`setuptools`/`wheel`（[FAQ 10](#faq-10-build-systemrequires-要加-cmakeninja-吗)）
2. **`minimum-version` 设为 `"build-system.requires"`**，避免版本同步问题（[FAQ 9](#faq-9-minimum-version-该设什么值)）
3. **`build-dir = "build/{wheel_tag}"`**，启用 CI 缓存与本地增量构建（[CI 缓存策略](#缓存策略)）
4. **CMake 仅请求 `Development.Module`**，manylinux 兼容（[FAQ 2](#faq-2-findpython-报错怎么办)）
5. **交叉编译用 `${SKBUILD_SOABI}`**，避免 FindPython SOABI 错误（[SOABI 错误](#soabi-错误)）
6. **`install(TARGETS)` 而非按路径引用产物**，兼容多配置 generator（[多配置 Generator 路径问题](#多配置-generator-路径问题)）
7. **CI 必加 `fetch-depth: 0`**，setuptools-scm 等 provider 需要 git history（[基本 workflow 示例](#基本-workflow-示例)）
8. **发布二进制 wheel 用 `cibuildwheel`**，自动处理 manylinux 修复与跨平台（[cibuildwheel 集成](#cibuildwheel-集成)）
9. **Conda 配方在 `build` 表显式加 `cmake` 与 `make`/`ninja`**，`scikit-build-core` 配方自身不能依赖它们（[FAQ 6](#faq-6-conda-打包要注意什么)）
10. **Free-threaded Windows 手动加 `Py_GIL_DISABLED`**（[FAQ 7](#faq-7-free-threaded-windows-怎么处理)）
11. **从 classic scikit-build 迁移**：移除 `PythonExtensions`、改用 `python_add_library(... MODULE WITH_SOABI)`、`SKBUILD_CONFIGURE_OPTIONS` 改名 `SKBUILD_CMAKE_ARGS`（[从 classic scikit-build 迁移](#从-classic-scikit-build-迁移)）
12. **调试三件套**：`pip install -ve .` + `-Cskbuild.logging.level=DEBUG` + `scikit-build builder`（[FAQ 3](#faq-3-如何调试构建过程)）

---

← 上一章：[入门到进阶指南](04-quickstart-to-advanced.md) | [返回目录](00-overview.md) | 下一章：[参考资料](06-resources.md) →
