# scikit-build-core 在线文档与教程资源研究摘要

> 研究对象：scikit-build-core 官方文档（readthedocs）+ daobook pygallery 中文教程 + Web 搜索补充资料
> 抓取时间：2026-07-04
> 当前官方版本：0.12.2（main 分支 dev 标记为 0.12.3.dev149+gf0895076f）

## 官方文档目录结构

官方文档位于 https://scikit-build-core.readthedocs.io/en/latest/ ，目录分为五大板块：

### Guide（指南，7 篇）
- Getting started — https://scikit-build-core.readthedocs.io/en/latest/guide/getting_started.html
- Authoring your CMakeLists — https://scikit-build-core.readthedocs.io/en/latest/guide/cmakelists.html
- Dynamic linking — https://scikit-build-core.readthedocs.io/en/latest/guide/dynamic_link.html
- Cross-compiling — https://scikit-build-core.readthedocs.io/en/latest/guide/crosscompile.html
- Migrating from scikit-build — https://scikit-build-core.readthedocs.io/en/latest/guide/migration_guide.html
- Build procedure — https://scikit-build-core.readthedocs.io/en/latest/guide/build.html
- FAQs — https://scikit-build-core.readthedocs.io/en/latest/guide/faqs.html

### Configuration（配置，5 篇）
- Configuration（总览） — https://scikit-build-core.readthedocs.io/en/latest/configuration/index.html
- Overrides — https://scikit-build-core.readthedocs.io/en/latest/configuration/overrides.html
- Dynamic metadata — https://scikit-build-core.readthedocs.io/en/latest/configuration/dynamic.html
- Formattable fields — https://scikit-build-core.readthedocs.io/en/latest/configuration/formatted.html
- Search paths — https://scikit-build-core.readthedocs.io/en/latest/configuration/search_paths.html
- （侧栏未列）Entry-point configuration — https://scikit-build-core.readthedocs.io/en/latest/configuration/entrypoint_config.html

### Plugins（插件，2 篇）
- Setuptools — https://scikit-build-core.readthedocs.io/en/latest/plugins/setuptools.html
- Hatchling — https://scikit-build-core.readthedocs.io/en/latest/plugins/hatchling.html

### About project（关于项目，2 篇）
- Projects（使用 scikit-build-core 的项目列表） — https://scikit-build-core.readthedocs.io/en/latest/about/projects.html
- Changelog — https://scikit-build-core.readthedocs.io/en/latest/about/changelog.html
- GitHub repository — https://github.com/scikit-build/scikit-build-core

### API docs（API 参考与配置参考，4 篇）
- scikit_build_core package — https://scikit-build-core.readthedocs.io/en/latest/api/scikit_build_core.html
- Schema — https://scikit-build-core.readthedocs.io/en/latest/schema.html
- Config Reference — https://scikit-build-core.readthedocs.io/en/latest/reference/configs.html
- CLI Reference — https://scikit-build-core.readthedocs.io/en/latest/reference/cli.html

### 首页其他重要小节
- Features（特性列表，对比 classic scikit-build 的优势）
- Example（最小可用 pyproject.toml + CMakeLists.txt 示例）
- Configuration（首页配置速览，列出全部主要字段及默认值）
- Other projects for building（同类二进制构建后端对比：py-build-cmake、cmeel、meson-python、maturin、enscons）

## 关键页面内容要点

### getting-started（快速入门）

1. **多种快速启动渠道**：`scikit-build init --backend pybind11`（1.0 新增脚手架命令）、`uv init --lib --build-backend=scikit`、`scientific-python/cookie` 模板、`buildgen new myext -r py/pybind11`。
2. **8 种语言/绑定后端示例**：pybind11、nanobind、SWIG、Cython、C、ABI3（Stable ABI）、ABI3t（free-threaded Stable ABI）、Fortran（f2py-cmake）。每种后端给出完整 `pyproject.toml`、`CMakeLists.txt`、源代码三件套。
3. **关键构建规则**：`build-system.requires` 中**不要**手动加 `cmake`、`ninja`、`setuptools`、`wheel`；scikit-build-core 会智能判断并按需自动注入 `cmake`/`ninja`（部分环境如 Android/FreeBSD/WebAssembly/ClearLinux 无法安装 PyPI 版本但可能已装系统版本）。
4. **CMakeLists.txt 模式**：`cmake_minimum_required(VERSION 3.15...4.3)` + `project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)` + `find_package(Python ... COMPONENTS Interpreter Development.Module REQUIRED)` + `python_add_library(... MODULE WITH_SOABI)` + `install(TARGETS ... DESTINATION ${SKBUILD_PROJECT_NAME})`。强调使用 `Development.Module` 而非 `Development`（manylinux 缺少 libpython）。
5. **示例参考**：pybind11 用 `pybind/scikit_build_example`，nanobind 用 `wjakob/nanobind_example`，综合示例库 `scikit-build/scikit-build-sample-projects`（含 free-threading）。

### configuration（配置项）

**统一配置三层来源**：每个选项都可用三种方式表达，优先级覆盖关系一致：
- `pyproject.toml` 的 `[tool.scikit-build]` 表（静态首选）
- PEP 517 config-settings（动态首选，可加 `skbuild.` 前缀，如 `-Cskbuild.logging.level=INFO`）
- 环境变量 `SKBUILD_*`（应急用，不推荐常规使用）

**配置项分类与关键字段**：
- **顶层**：`build-dir`（CMake 构建目录，默认临时目录，可设置实现缓存复用）、`env`（传给 CMake 子进程的环境变量表，`setdefault` 语义，`force=true` 强制覆盖）、`experimental`（启用预览特性）、`fail`（仅 override 用，立即失败）、`metadata`（动态元数据声明）、`minimum-version`（向后兼容门，建议设为 `"build-system.requires"` 自动读取）、`strict-config`、`null-variant`（PEP 817 实验性）
- **cmake.\***：`version`（PEP 440 specifier，可填 `"CMakeLists.txt"` 自动读取）、`args`、`define`（additive 表）、`build-type`（默认 Release）、`source-dir`（默认 .）、`python-hints`
- **ninja.\***：`version`（默认 >=1.5）、`make-fallback`（默认 true）
- **logging.\***：`level`（默认 WARNING）
- **sdist.\***：`include`/`exclude`（gitignore 语法）、`inclusion-mode`（0.12 新增，默认 `default`，可选 `classic`/`manual`）、`reproducible`（默认 true）、`cmake`（默认 false）、`force-include`、`resolve-symlinks`
- **wheel.\***：`packages`（list 或 table 形式，0.10 起支持 table）、`py-api`（cp38/py3/py2.py3/cp315t 等）、`expand-macos-universal-tags`、`install-dir`（可填 `${SKBUILD_*_DIR}` 前缀）、`license-files`、`cmake`（默认 true，关闭则纯 Python wheel）、`platlib`、`exclude`、`build-tag`、`force-include`、`reproducible`（默认 false，opt-in）
- **backport.\***：`find-python`（默认 3.26.1，旧 CMake 自动回移植 FindPython）
- **editable.\***：`mode`（redirect/inplace）、`verbose`、`rebuild`、`rebuild-dir`
- **build.\***：`tool-args`、`targets`、`verbose`、`requires`（0.11 新增，注入额外 build-system.requires）
- **install.\***：`components`、`targets`、`strip`（默认 true）
- **generate[]**：动态元数据生成文件，`path`/`template`/`template-path`/`location`（install/build/source）
- **messages.\***：`after-failure`/`after-success`
- **search.\***：`site-packages`（默认 true）
- **variant\***（实验性 PEP 817）：`variant`/`variant-name`/`variant-label`/`null-variant`

**Overrides 系统**：`[[tool.scikit-build.overrides]]` 数组，`if` 条件支持：
- 版本类（specifier set）：`scikit-build-version`、`python-version`、`implementation-version`、`system-cmake`
- 字符串类（regex）：`platform-system`、`platform-machine`、`platform-node`、`implementation-name`、`abi-flags`、`state`
- 布尔类：`from-sdist`、`cmake-wheel`、`failed`（失败重试一次，0.10+）、`env.*`
- `if.any` 满足任一即可；多条件 `if` 全部满足才生效；自上而下覆盖；未匹配的 override 不校验未知字段（便于跨版本兼容）

### usage / build（使用方法 / 构建流程）

1. **Quickstart 三件套**：`pipx run build`、`uv build`、`pip install build && python -m build`；默认先 SDist 后 Wheel，`--sdist --wheel` 可分别从源码直接构建。
2. **SDist 构建四步**：读 `pyproject.toml` → 隔离环境装 `build-system.requires` → 调 `get_requires_for_build_sdist`（动态依赖）→ 调 `build_sdist` 产出 tarball。`pip` 不能构建 SDist，只有 `build` 工具能。
3. **Wheel 构建四步**：同上，调 `get_requires_for_build_wheel` 与 `build_wheel`。无隔离时可直接 `python -c "from scikit_build_core.build import build_wheel; build_wheel('dist')"`。
4. **Wheel 文件结构**：包目录 + `<name>-<version>.dist-info/`（METADATA/WHEEL/RECORD）+ `.data/{scripts,headers,data}` 子目录（推荐用 `importlib.resources` 而非 `.data/data` 避免污染系统目录）。
5. **二进制 wheel 分发**：`linux_*` 标签不能上 PyPI，需 `auditwheel` 转 manylinux/musllinux；macOS 需 `delocate` + 交叉编译 Apple Silicon；Windows 需 `delvewheel`。推荐 `cibuildwheel` 一站式跨平台构建。
6. **Wheel 文件名五段**：`name-version-pythontag-abitag-platformtag`（如 `scikit_build_core-0.1.2-py3-none-any.whl`）。

### cmake-config（CMakeLists 配置）

1. **环境检测变量**：`${SKBUILD}`（值为 "2"，classic 为 "1"）、`${SKBUILD_CORE_VERSION}`（版本号），可据此写兼容性 CMakeLists。
2. **项目信息变量**：`${SKBUILD_PROJECT_NAME}`、`${SKBUILD_PROJECT_VERSION}`（1.0 起限制为四段 `major.minor.patch.tweak`，可直接喂 `project(VERSION ...)`）、`${SKBUILD_PROJECT_VERSION_FULL}`（含 dev/local 后缀）、`${SKBUILD_STATE}`（sdist/wheel/metadata_wheel/editable/metadata_editable）。
3. **FindPython 推荐写法**：`find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)`，**不要**用 `Development`（含 Embed，manylinux 缺 libpython）；Stable ABI 用 `Development.SABIModule`（CMake 3.26+），通过 `${SKBUILD_SABI_COMPONENT}` 与 `${SKBUILD_SABI_VERSION}` 条件注入。
4. **安装目录变量**：`${SKBUILD_PLATLIB_DIR}`（默认，→ site-packages）、`${SKBUILD_PURELIB_DIR}`、`${SKBUILD_DATA_DIR}`（→ 环境根，慎用）、`${SKBUILD_HEADERS_DIR}`（→ Python include）、`${SKBUILD_SCRIPTS_DIR}`（→ bin/Scripts）、`${SKBUILD_METADATA_DIR}`（dist-info，仅 wheel 阶段可用）、`${SKBUILD_NULL_DIR}`（丢弃）。
5. **SOABI 处理**：交叉编译时 FindPython 的 `Python_SOABI` 可能错误，应使用 `${SKBUILD_SOABI}`；可 `set(Python_SOABI ${SKBUILD_SOABI})` 覆盖（非官方支持但实际有效）。
6. **语言助手**：Cython 用 `cython-cmake`（`include(UseCython)` + `cython_transpile`），Fortran 用 `f2py-cmake`（`include(UseF2Py)`），均为独立 CMake 包，加入 `build.requires`。

### troubleshooting / faqs（故障排查）

1. **多线程构建**：`CMAKE_BUILD_PARALLEL_LEVEL=8 pip install .` 或 `-Ccmake.define.CMAKE_BUILD_PARALLEL_LEVEL=8`；Ninja 默认按核心数并行；可用 `[tool.scikit-build.env]` 转发 `MAX_JOBS` 到 `CMAKE_BUILD_PARALLEL_LEVEL`（`setdefault` 语义）。
2. **动态 setup.py 选项迁移**：转为 CMake option 用 `-Ccmake.define.<NAME>=<value>` 传递；或用 `[[tool.scikit-build.overrides]]` 按条件配置。
3. **FindPython 报错**：仅请求 `Development.Module`；manylinux 没有 libpython，请求 `Development.Embed` 会失败。
4. **调试方法**：`pip` 必须加 `-v` 否则吞输出；提高 `logging.level=INFO`/`build.verbose=true`；`scikit-build builder` 打印当前所有设置；`scikit-build builder wheel-tag` 查看 wheel 标签。
5. **Wheel 修复**：默认产出 `linux` wheel 不可上 PyPI，必须 `auditwheel`（Linux）/`delocate`（macOS）/`delvewheel`（Windows）转 manylinux/musllinux；`cibuildwheel` 自动处理；`repairwheel` 是统一工具。
6. **Conda recipe 要点**：在 `host` 表重建 `build-system.requires`（conda 版本），`build` 表加 `cmake` 和 `make`/`ninja`；conda-build 在 UNIX 硬编码 `CMAKE_GENERATOR="Unix Makefiles"`，需手动改用 Ninja；`scikit-build-core` 配方不能依赖 cmake/make/ninja（会进错表）。
7. **Free-threaded Windows**：需手动 `Py_GIL_DISABLED` C 定义（两套构建共享配置文件，Python 无法自动设置）。
8. **Wheel variants（实验性）**：PEP 817 早期预览，需 `experimental=true`，仅 config-settings 或 overrides 可设；`variant="cpu :: abi :: cp313"`、`variant-label=cpu`；自动注入 `variantlib` 依赖。

### migration_guide（迁移指南）

- **配置变更**：`build-backend` 改为 `scikit_build_core.build`；`requires` 中 `scikit-build` 改 `scikit-build-core`，移除 `cmake`/`ninja`；填 `[tool.scikit-build]` 表；setup.py/cfg 配置迁移到 pyproject.toml（可临时改 `build-backend=setuptools` + `hatch new --init` 自动迁移）；`MANIFEST.in` 改用 `sdist.include`/`sdist.exclude`。
- **CMake 变更**：移除 `PythonExtensions` 模块，改用 `find_package(Python ... COMPONENTS Interpreter Development.Module)` + `python_add_library(... MODULE WITH_SOABI)`；`UseCython` 模块暂不支持（参考 getting started）；`SKBUILD_CONFIGURE_OPTIONS` 环境变量改名为 `SKBUILD_CMAKE_ARGS`；`SKBUILD_BUILD_OPTIONS` 不再支持，用 `CMAKE_BUILD_PARALLEL_LEVEL`/`SKBUILD_CMAKE_VERBOSE` 替代。

### configuration/dynamic（动态元数据）

- **内置 4 个 provider**：
  - `scikit_build_core.metadata.setuptools_scm`（version）：从 git tag 或 `.git_archival.txt` 读版本
  - `scikit_build_core.metadata.regex`（version）：从文件 regex 抽取，支持 `result`/`remove` 后处理（0.10+）
  - `scikit_build_core.metadata.fancy_pypi_readme`（readme）：包装 hatch-fancy-pypi-readme
  - `scikit_build_core.metadata.template`（任意字段）：引用其他 metadata 字段做模板输出（0.11.2+）
- **build.requires**（0.11+）：注入额外 `build-system.requires`，常与 overrides 配合实现"源码构建用本地路径，SDist 构建用 PyPI"
- **文件生成 `[[tool.scikit-build.generate]]`**：用 `string.Template` 把 metadata 写到文件，`location` 可选 install/build/source（source 会自动加入 sdist.include 并覆盖现有文件）
- 第三方 provider 需 `experimental=true`（接口可能在 minor 版本间变化）

### configuration/overrides（覆盖系统）

详见上文 configuration 节"Overrides 系统"小节。重点：`if.failed=true` 可实现"构建失败则回退纯 Python wheel"（0.10+），但会禁用 `prepare_metadata_*` hooks。

### reference/cli（CLI 参考）

`scikit-build` 命令（或 `python -m scikit_build_core`）子命令：
- `scikit-build build requires [--mode {sdist,wheel,editable}]`：获取构建依赖（含动态）
- `scikit-build build project-table`：输出处理动态 metadata 后的完整 project 表
- `scikit-build builder`：系统信息（Python/CMake/Ninja 版本、SOABI、wheel 标签等）
- `scikit-build builder wheel-tag [--archs ...] [--abi ABI] [--purelib]`：计算 wheel 标签
- `scikit-build builder sysconfig`：sysconfig 信息
- `scikit-build file-api query <build_dir>` / `reply <reply_dir>`：CMake File API 工具

### changelog（变更日志要点）

- 最新稳定版 **0.12.2**：修复 Windows 文件包含模式、强制规范化 SDist 名（PyPI 不再接受非规范化名）、改进 inclusion 调试日志
- **0.12.0** 重要变更：新增 `sdist.inclusion-mode`（默认 `default`，不再遍历被忽略目录，更快更可预测；`classic` 为旧行为，`manual` 不读 gitignore）；改进交叉编译支持；支持 fancy-pypi-readme 25.1
- **0.11.x**：新增 `build.requires` 动态注入；`metadata.template` provider；改进 fancy-pypi-readme 版本号支持
- **0.10.x**：`cmake.minimum-version`/`ninja.minimum-version` 重命名为 `cmake.version`/`ninja.version`（完整 specifier set）；`cmake.verbose`/`cmake.targets` 重命名为 `build.verbose`/`build.targets`；`wheel.packages` 支持 table 形式；新增 `from-sdist`/`system-cmake`/`cmake-wheel`/`failed` override 条件；`minimum-version` 支持 `"build-system.requires"`

## 教程资源内容要点（daobook pygallery）

教程地址：https://daobook.github.io/pygallery/study/fields/scikit-build-core/index.html
作者：xinetzone

**目录结构（仅 2 个子页面）**：
1. [`scikit-build-core` 概述](https://daobook.github.io/pygallery/study/fields/scikit-build-core/intro.html)
   - 示例（最小 pyproject.toml + CMakeLists.txt）
   - 配置（全字段速览，含默认值）
   - 用于构建的其他项目（同类后端对比）
2. [入门指南](https://daobook.github.io/pygallery/study/fields/scikit-build-core/getting-started.html)

**内容特点**：
- **本质是官方首页的中文翻译**：`intro.html` 是 `index.html`（官方首页 Features/Example/Configuration/Other projects）的逐段中译，配置字段表与官方首页"Configuration"小节一致
- **翻译存在时滞**：`intro.html` 中 `minimum-version = "0.11"` 标注为 "current version"，而官方已到 0.12.2；提及"自由线程的 Python 3.13"而非"3.13+"；setuptools/hatchling 描述为"高度实验性"（官方已调整措辞为"可能未来独立成包"）
- **术语本地化**：`wheel` 译为"轮子"，`SDist` 保留原文，`Stable ABI` 译为"稳定 ABI"，`free-threaded` 译为"自由线程"
- **缺失内容**：未覆盖官方 Guide 的 7 篇深度文档（CMakeLists 作者指南、动态链接、交叉编译、迁移指南、构建流程、FAQ），未覆盖 Configuration 的 5 篇子文档（Overrides、Dynamic metadata、Formattable fields、Search paths、Entry-point config），未覆盖 Plugins、API docs、Config/CLI Reference
- **生态定位**：pygallery 是综合性 Python 工具教程集，scikit-build-core 与 cibuildwheel、Conan、pybind11、CMake、Ninja 同属"领域"分类，可作为这些工具的中文入门索引

**Web 搜索补充资料**：
- **SciPy 2024 论文**（https://doi.org/10.25080/FMKR8387）：Henry Schreiner 等人发表的《Scikit-build-core: A modern build-backend for CPython C/C++/Fortran/Cython extensions》，涵盖 Python 打包历史、scikit-build-core 设计与内部实现、采用案例。是深入了解设计动机与内部架构的权威资料。
- **pydevtools.com 实战教程**：使用 uv + scikit-build-core + pybind11 构建 C++ 扩展的端到端示例，含完整 `pyproject.toml` 与 `CMakeLists.txt`。
- **CSDN 博客（中文）**：基础介绍性文章，部分内容混淆了 classic scikit-build（setup.py 风格）与 scikit-build-core（pyproject.toml 风格），参考需谨慎。
- **pybind11 / nanobind 官方文档**：均推荐 scikit-build-core 作为构建后端，nanobind 文档给出推荐配置 `minimum-version="0.4"`、`build-dir="build/{wheel_tag}"`、`wheel.py-api="cp312"`。

## 三方内容差异与互补分析

### 官方文档侧重（规范 + 参考）
- **完整性与权威性最强**：覆盖 Guide/Configuration/Plugins/About/API 五大板块，是配置项、CLI、API 的唯一权威来源
- **配置参考最详尽**：`reference/configs.html` 逐项给出类型、默认值、配置键、环境变量、行为说明、版本变更历史
- **面向规范与正确性**：强调 PEP 标准、minimum-version 兼容性、Stable ABI、free-threaded、wheel 修复等规范流程
- **多语言绑定示例齐全**：8 种后端（pybind11/nanobind/SWIG/Cython/C/ABI3/ABI3t/Fortran）并列对照
- **不足**：无中文版；无完整端到端项目实战；无内部架构剖析（仅在 SciPy 论文中有）

### 教程资源侧重（daobook，中文入门索引）
- **中文本地化**：是少有的中文 scikit-build-core 资料，降低中文用户入门门槛
- **定位为概述级**：仅翻译首页，提供"是什么 + 最小示例 + 配置字段速览 + 同类对比"
- **生态关联性**：与 cibuildwheel、Conan、pybind11、CMake、Ninja 教程同站，形成工具链视角
- **不足**：内容时滞（落后 1-2 个版本）；覆盖面窄（仅首页内容）；无深度章节；无实战项目；翻译存在术语不一致（"轮子"等）

### Web 补充资料侧重
- **SciPy 2024 论文**：补足"为什么这样设计"的动机与内部架构（论文第 3-4 节）
- **pydevtools 实战**：补足"从零到可用"的端到端流程（含 uv 工作流）
- **pybind11/nanobind 文档**：补足"绑定库视角的集成建议"
- **CSDN 博客**：中文补充但质量参差，存在 classic/core 混淆

### 源码研究将补充什么（预判）
1. **模块职责与调用链**：`scikit_build_core.build` 模块如何实现 PEP 517 hooks（`build_sdist`/`build_wheel`/`prepare_metadata_for_build_wheel`/`build_editable` 等），`_shims`、`_compat`、`settings`、`cmake_run`、`builder`、`file_api` 等子模块的职责边界
2. **配置系统实现**：`settings` 模块如何用 pydantic 模型（或类似）定义配置 schema、三层来源合并逻辑、overrides 求值引擎、minimum-version 默认值回退机制
3. **CMake 调用细节**：`cmake_run` 如何编排 configure→build→install 三步、如何注入 `${SKBUILD_*}` 变量、FindPython 回移植机制、generator 选择策略
4. **wheel 打包实现**：`builder.wheel` 如何调用 CMake install、如何发现包文件、如何应用 force-include/exclude、如何生成 dist-info、如何处理 platlib/purelib
5. **动态元数据插件机制**：`metadata.*` provider 的注册与调用接口、`generate[]` 模板渲染流程
6. **测试用例即文档**：`tests/packages/` 下数十个示例项目是活的文档，覆盖官方文档未详述的边缘场景

### 三方互补关系
```
官方文档（What + How-to + Reference）
    │
    ├─ daobook（中文入门索引，降低门槛，但需注意版本时滞）
    ├─ SciPy 论文（Why + 内部架构）
    ├─ pydevtools/pybind11/nanobind（端到端实战 + 绑定库集成建议）
    └─ 源码研究（实现细节 + 模块职责 + 边缘场景）
```

Wiki 教程应以官方文档为骨架，用 daobook 做中文入门索引补充，用 SciPy 论文与源码研究填充"为什么"与"怎么实现"，用实战资料提供端到端示例。

## 建议 Wiki 章节应覆盖的主题清单

基于以上研究，建议 Wiki 教程覆盖以下主题（按由浅入深排序）：

### 入门层
1. **scikit-build-core 是什么**：定位（CMake + Python 打包的桥梁）、与 classic scikit-build 的关系、与同类后端（meson-python/maturin/py-build-cmake/cmeel/enscons）对比
2. **5 分钟快速开始**：`scikit-build init` / `uv init --lib --build-backend=scikit` / scientific-python/cookie 三种脚手架；最小 pyproject.toml + CMakeLists.txt 示例
3. **第一个 C 扩展**：从零编写 pyproject.toml、CMakeLists.txt、`_core.c`，构建并安装验证

### 语言绑定层
4. **多语言绑定实战**：pybind11、nanobind、SWIG、Cython、C、Fortran 六种后端的完整示例与差异对比
5. **Stable ABI（ABI3）与 free-threaded（ABI3t）**：`wheel.py-api` 配置、`${SKBUILD_SABI_COMPONENT}` 用法、PEP 703/793/803/817 等新规范支持

### 配置层
6. **配置系统总览**：三层来源（pyproject.toml/config-settings/环境变量）的优先级与转换规则
7. **配置项分类详解**：cmake.*/ninja.*/sdist.*/wheel.*/build.*/install.*/editable.*/logging.*/backport.*/generate[]/messages.*/search.*/env 等，每类配最小示例
8. **minimum-version 兼容机制**：如何用 `"build-system.requires"` 自动同步、各版本默认行为差异、避免 upper cap 的最佳实践
9. **Overrides 条件配置**：if 条件类型（版本/字符串/布尔）、`if.any`、`failed` 失败回退、跨版本兼容写法
10. **动态元数据**：4 个内置 provider（setuptools-scm/regex/fancy-pypi-readme/template）、`build.requires` 注入、`generate[]` 文件生成、第三方 provider 注意事项

### CMake 集成层
11. **CMakeLists.txt 编写指南**：`${SKBUILD_*}` 变量全集、FindPython 正确写法、安装目录变量、SOABI 处理、语言助手（cython-cmake/f2py-cmake）
12. **构建流程详解**：SDist 四步、Wheel 四步、wheel 文件结构、`.data/{scripts,headers,data}` 用法
13. **交叉编译**：Apple Silicon、Windows ARM、WebAssembly/Emscripten/Pyodide、`_PYTHON_HOST_PLATFORM`、`ARCHFLAGS`

### 分发层
14. **Wheel 修复与分发**：auditwheel/delocate/delvewheel/repairwheel、cibuildwheel 自动化、manylinux/musllinux 规范
15. **Conda 打包**：conda-forge 配方要点、host/build 表区分、CMAKE_GENERATOR 处理
16. **多线程构建与缓存**：`CMAKE_BUILD_PARALLEL_LEVEL`、`build-dir` 缓存复用、`[tool.scikit-build.env]` 转发

### 迁移与故障排查层
17. **从 classic scikit-build 迁移**：配置变更、CMake 变更、环境变量重命名、PythonExtensions/UseCython 替代方案
18. **故障排查指南**：调试方法（`-v`/`logging.level`/`scikit-build builder`）、FindPython 常见错误、wheel 标签问题、free-threaded Windows 特殊处理
19. **实验性特性**：wheel variants（PEP 817）、editable rebuild、inplace 模式

### 工具链与生态层
20. **CLI 工具参考**：`scikit-build build/builder/file-api` 子命令详解与使用场景
21. **插件后端**：setuptools 集成（过渡路径）、hatchling 插件、何时选择原生后端 vs 插件
22. **生态项目案例**：使用 scikit-build-core 的知名项目列表与借鉴方向

### 实现原理层（依赖源码研究）
23. **架构与模块职责**：`build`/`settings`/`cmake_run`/`builder`/`file_api`/`metadata`/`_shims`/`_compat` 模块职责与调用链
24. **PEP 517 hooks 实现**：`build_sdist`/`build_wheel`/`prepare_metadata_*`/`build_editable` 内部流程
25. **配置 schema 与合并引擎**：pydantic 模型、三层来源合并、overrides 求值、minimum-version 回退
