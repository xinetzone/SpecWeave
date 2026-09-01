---
id: "scikit-build-core-pure-python-minimal"
title: "scikit-build-core 纯Python项目最小配置"
type: "code-pattern"
date: "2026-08-27"
maturity: "L1-draft"
source: "retrospective-jupyter-podman-rootless-seven-rounds 模式P2 + 洞察I3/I4"
related_patterns:
  - "conda-build-scikit-build-core-native"
  - "cmake-four-layer-modular-architecture"
  - "toml-table-declaration-consistency"
  - "container-devtool-seven-layer-stack"
tags: ["scikit-build-core", "cmake", "ninja", "pure-python", "pyproject.toml", "build-system", "setuptools-migration", "pep-517"]
validation_count: 1
reuse_count: 0
---

# scikit-build-core 纯Python项目最小配置

## 模式概述

将纯Python包从setuptools迁移到scikit-build-core + CMake + Ninja时，最常见的失败原因是六个配置陷阱：手动声明cmake/ninja依赖、使用废弃的配置键、TOML表重复声明、删除CMakeLists.txt、手写install规则、使用错误的verbose键。这些陷阱会导致构建失败、pip install挂起无输出、editable模式Permission denied等问题。

本模式提供纯Python项目迁移到scikit-build-core的**可直接复制**的最小配置模板，包含pyproject.toml和CMakeLists.txt两个文件的正确写法，以及6个必须避开的陷阱。

## 触发场景

- 将纯Python包从setuptools迁移到scikit-build-core构建后端时
- 纯Python项目希望使用现代化构建后端，为未来添加C扩展预留能力时
- 需要Ninja快速构建（editable wheel <1秒）时
- 适用于：纯Python CLI工具、纯Python库、任务管理工具（invoke等）、未来可能添加C扩展的Python项目
- 不适用于：已有C/C++扩展的项目（使用[conda-build-scikit-build-core-native](conda-build-scikit-build-core-native.md)）、仍需使用setuptools特性的项目（如setup.py自定义构建步骤）、完全不需要C扩展能力且对构建速度无要求的简单项目

## 核心配置（直接复制即可用）

### 文件1：pyproject.toml

```toml
[build-system]
requires = ["scikit-build-core>=0.9"]
build-backend = "scikit_build_core.build"

[project]
name = "<your-package-name>"
version = "0.1.0"
# ... 其他project元数据（dependencies, authors等）

[tool.scikit-build]
wheel.packages = ["<your_package_dir>"]  # 你的Python包目录名（如"tasks"）
build.verbose = false                    # ✅ scikit-build-core >=0.10
build-dir = "build/{wheel_tag}"
minimum-version = "0.9"

[tool.scikit-build.cmake]
build-type = "Release"
args = ["-G", "Ninja"]                   # ✅ 通过cmake.args设置Ninja生成器
```

### 文件2：CMakeLists.txt（必须存在，仅需9行）

```cmake
cmake_minimum_required(VERSION 3.15...3.31)
project(
  ${SKBUILD_PROJECT_NAME}
  VERSION ${SKBUILD_PROJECT_VERSION}
  LANGUAGES NONE                         # ✅ 纯Python项目必须是NONE
)

# scikit-build-core handles Python package installation via wheel.packages
# 不需要写任何 install() 规则！
```

### 可选：optional-dependencies分组（推荐）

```toml
[project.optional-dependencies]
# 按功能分组，与模式P1的三层后端架构配套
sdk = ["podman>=5.0.0"]
compose = ["podman-compose>=1.0.0"]
full = ["sdk", "compose"]
model = ["omlmd>=0.2.0", "olot[oras-py]>=0.2.0"]
dev = ["pytest>=8.0", "ruff>=0.5"]
```

## 六个必避陷阱

### ❌ 陷阱1：在build-system.requires中手动声明cmake/ninja

```toml
# ❌ 错误：scikit-build-core自动注入cmake和ninja，手动声明会导致版本冲突
[build-system]
requires = ["scikit-build-core>=0.9", "cmake>=3.15", "ninja>=1.10"]  # 多了cmake和ninja
```

**后果**：构建时可能出现版本冲突警告；在某些环境下会下载不必要的wheel包，拖慢构建速度。

**正确做法**：`requires` 中只放 `scikit-build-core>=0.9`，cmake和ninja由scikit-build-core自动管理。

---

### ❌ 陷阱2：使用已废弃的cmake.verbose而非build.verbose

```toml
# ❌ 错误：scikit-build-core >=0.10已废弃cmake.verbose
[tool.scikit-build]
cmake.verbose = false  # 废弃！会警告或报错
```

**后果**：构建时出现DeprecationWarning，未来版本会直接报错。

**正确做法**：使用 `build.verbose = false`（在 `[tool.scikit-build]` 表内）。

---

### ❌ 陷阱3：使用不存在的cmake.generator键

```toml
# ❌ 错误：cmake.generator不是有效配置键
[tool.scikit-build]
cmake.generator = "Ninja"  # 无效！
```

**后果**：scikit-build-core忽略该键，使用默认生成器（可能是Unix Makefiles而非Ninja），构建速度变慢。

**正确做法**：在 `[tool.scikit-build.cmake]` 表中通过 `args = ["-G", "Ninja"]` 设置。

---

### ❌ 陷阱4：TOML dotted key内联表与显式[table]冲突（最隐蔽！）

```toml
# ❌ 错误：cmake.version dotted key隐式创建了[tool.scikit-build.cmake]子表
[tool.scikit-build]
cmake.version = ">=3.15"  # 这行内联创建了[tool.scikit-build.cmake]！

# ... 后面又显式声明[tool.scikit-build.cmake]表
[tool.scikit-build.cmake]  # TOML解析错误：Cannot declare ('tool', 'scikit-build', 'cmake') twice
build-type = "Release"
args = ["-G", "Ninja"]
```

**后果**：TOML解析失败，`pip install` **挂起无输出**（scikit-build-core在import时解析TOML，异常未被pip捕获显示，看起来像卡住了）。这是最坑的陷阱——没有报错信息，只有进程挂起。

**正确做法**：
- 使用 `minimum-version = "0.9"` 放在 `[tool.scikit-build]` 级别，替代 `cmake.version`
- 只要需要写 `[tool.scikit-build.cmake]` 的子键（build-type/args等），就**不要**在父表中使用任何 `cmake.xxx` dotted key
- 统一使用显式 `[table]` 声明，避免dotted key隐式建表

---

### ❌ 陷阱5：删除CMakeLists.txt（纯Python也需要！）

```bash
# ❌ 错误：以为纯Python不需要CMakeLists.txt
rm CMakeLists.txt  # 构建报错：source directory does not appear to contain CMakeLists.txt
```

**后果**：CMake configure步骤失败，构建直接报错。

**根本原因**：scikit-build-core即使在纯Python模式（`wheel.packages`自动发现）下，构建流程也**始终经过CMake configure步骤**。`wheel.packages`只是替代了手写`install(DIRECTORY)`规则，但不替代CMakeLists.txt本身。

**正确做法**：保留开头的9行最小CMakeLists.txt，`LANGUAGES NONE`表示不需要任何语言编译器，CMake配置0.1秒完成，Ninja构建无工作项（纯Python，无需编译）。

---

### ❌ 陷阱6：手写install(DIRECTORY)规则（Windows下Permission denied）

```cmake
# ❌ 错误：纯Python项目不需要手写install规则
cmake_minimum_required(VERSION 3.15...3.31)
project(mypkg LANGUAGES NONE)

install(DIRECTORY tasks/ DESTINATION ${SKBUILD_PLATLIB_DIR}/tasks)  # 多此一举！
```

**后果**：
- Windows editable模式下可能出现Permission denied（文件被占用无法复制）
- 多余的安装规则可能导致文件重复安装
- 忘记配置PATTERN排除__pycache__等无关文件

**正确做法**：**完全删除**手写install规则，CMakeLists.txt中只保留project声明。`wheel.packages = ["tasks"]`自动处理Python包发现和安装。

## 关键配置项说明

| 配置项 | 位置 | 推荐值 | 说明 |
|--------|------|--------|------|
| `build-system.requires` | `[build-system]` | `["scikit-build-core>=0.9"]` | 不要加cmake/ninja |
| `build-backend` | `[build-system]` | `"scikit_build_core.build"` | 注意是下划线不是连字符 |
| `wheel.packages` | `[tool.scikit-build]` | `["<pkg>"]` | Python包目录列表，纯Python必填 |
| `build.verbose` | `[tool.scikit-build]` | `false` | scikit-build-core >=0.10用这个 |
| `build-dir` | `[tool.scikit-build]` | `"build/{wheel_tag}"` | 构建产物隔离到build/ |
| `minimum-version` | `[tool.scikit-build]` | `"0.9"` | 替代cmake.version |
| `build-type` | `[tool.scikit-build.cmake]` | `"Release"` | CMake构建类型 |
| `cmake.args` | `[tool.scikit-build.cmake]` | `["-G", "Ninja"]` | Ninja生成器设置方式 |
| `LANGUAGES` | CMakeLists.txt | `NONE` | 纯Python必须是NONE，不要写CXX/C |

## 验证方法

配置完成后，按以下步骤验证：

```bash
# 1. 语法检查：TOML和CMake是否能正确解析
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))" && echo "TOML OK"
cmake -S . -B build/test -G Ninja  # 应0.1秒完成，无错误

# 2. 构建wheel（非editable）
pip wheel . -w dist/
# 应在1-2秒内完成，检查dist/下有.whl文件

# 3. 构建editable wheel（开发模式）
pip install -e .
# 应<1秒完成，无Permission denied

# 4. 验证安装可导入
python -c "import <your_package>; print(<your_package>.__file__)"
# 应输出正确的安装路径

# 5. 验证包内容（可选）
python -m pip show -f <your-package-name>
# 检查所有Python文件都正确安装
```

## 反模式（不要这么做）

### ❌ 反模式1：直接删除CMakeLists.txt
见陷阱5。

### ❌ 反模式2：在pyproject.toml中混用dotted key和显式表
见陷阱4——这是最隐蔽的错误，会导致pip install挂起无输出。

### ❌ 反模式3：先迁移构建系统再做功能
构建系统是基础设施，应在功能稳定后统一迁移升级。功能快速迭代期反复修改构建配置是浪费时间。（参考[capability-stack-progressive-building](../methodology-patterns/governance-strategy/capability-stack-progressive-building.md)）

### ❌ 反模式4：使用cmake.verbose而非build.verbose
scikit-build-core >=0.10已废弃cmake.verbose，必须用build.verbose。

### ❌ 反模式5：把Python包目录写成wheel.packages的路径而非目录名
```toml
# ❌ 错误
wheel.packages = ["src/tasks"]  # 如果包在src/下应该用wheel.package-dir或正确配置

# ✅ 正确（扁平布局，包在项目根目录）
wheel.packages = ["tasks"]
```

## 失败案例（真实踩坑记录）

### 案例1：TOML表冲突导致pip install挂起2小时无输出（源案例）

**背景**：在Jupyter Podman Rootless七轮优化的P2阶段，首次将tasks/包从setuptools迁移到scikit-build-core。

**操作**：参考scikit-build-core文档，在`[tool.scikit-build]`中写了`cmake.version = ">=3.15"`（dotted key），后面又加了`[tool.scikit-build.cmake]`表写build-type和args。

**现象**：
- `pip install -e .` 执行后无任何输出，进程挂起
- Ctrl+C中断后重试仍然挂起
- 检查进程列表发现pip进程在等待，无CPU占用
- 误以为是网络问题/镜像源问题，反复重试浪费约2小时
- 尝试降级pip版本、换conda环境、重启WSL均无效

**根因定位**：
- 手动用Python解析pyproject.toml：`python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"`
- 立即抛出 `TomlDecodeError: Cannot declare ('tool', 'scikit-build', 'cmake') twice`
- 原来是TOML v1.0规范禁止同一键路径混用dotted key隐式建表和显式[table]声明
- scikit-build-core在import时解析pyproject.toml，异常被pip的构建隔离机制吞掉，表现为静默挂起

**修复**：删除`cmake.version = ">=3.15"`，改用`minimum-version = "0.9"`放在`[tool.scikit-build]`级别。

**教训**：TOML语法错误不会产生友好的错误信息，在迁移构建系统时**第一步**就应该用`python -c "import tomllib; ..."`验证TOML语法，不要等到pip install挂起才排查。

---

## 不适用场景与反目标用户

### ❌ 反目标用户1：已有大量C/C++/Rust扩展的项目

**特征**：项目中已有pybind11/Cython/C extension模块，使用CMake编译原生代码。

**为什么不适用**：
- 本模式的`LANGUAGES NONE`和9行最小CMakeLists.txt假设没有编译目标
- 已有原生扩展的项目需要完整的CMake配置（find_package/pybind11_add_module/install(TARGETS)等）
- 应使用 [conda-build-scikit-build-core-native](conda-build-scikit-build-core-native.md) 模式

**判断信号**：CMakeLists.txt中出现`pybind11_add_module`、`add_library`、`add_executable`等编译指令。

---

### ❌ 反目标用户2：依赖setuptools高级特性的项目

**特征**：项目使用setup.py自定义构建步骤、setuptools.EntryPoints插件系统、build_py子命令重写、或依赖setuptools-scm等setuptools专属插件。

**为什么不适用**：
- scikit-build-core不兼容setup.py自定义构建逻辑
- 迁移需要重写所有自定义构建步骤为CMake逻辑或scikit-build-core钩子
- 如果setuptools工作正常且无性能/功能问题，迁移ROI为负

**判断信号**：项目中存在setup.py且包含`cmdclass`、`build_py`、`develop`等自定义类；pyproject.toml中有`[tool.setuptools]`的复杂配置。

---

### ❌ 反目标用户3：单文件脚本/超简单Python包

**特征**：只有单个.py文件的小工具、临时脚本、无包结构的简单项目（如只有一个`hello.py`）。

**为什么不适用**：
- 引入CMake + Ninja增加了不必要的构建依赖链
- 9行CMakeLists.txt虽然轻量，但对于单文件项目仍然是额外负担
- 使用setuptools的最简配置（甚至不需要pyproject.toml，直接setup.py）或hatchling/pdm-backend等纯Python后端更轻量

**判断信号**：项目没有`<package>/__init__.py`的包结构，只是松散的.py文件集合；无editable开发需求。

---

### ❌ 边界场景：src-layout（src/目录布局）项目需要额外配置

**特征**：项目使用`src/<package>/`而非扁平布局（包直接在项目根目录）。

**为什么需要注意**：
- 本模式的`wheel.packages = ["<pkg>"]`默认假设扁平布局
- src-layout需要额外配置`wheel.package-dir`或调整为`wheel.packages = ["src/<pkg>"]`配合sdist配置
- CMakeLists.txt中的路径处理也可能需要调整

**处理方式**：scikit-build-core支持src-layout，但需要参考官方文档的src-layout示例配置，不能直接复制本模式模板。本模式聚焦扁平布局的最小配置。

---

### 早期预警信号：以下情况出现时应暂停迁移

| 信号 | 含义 | 建议 |
|------|------|------|
| `pip install -e .` 挂起超过30秒无输出 | 大概率TOML语法错误（陷阱4） | 立即Ctrl+C，运行tomllib解析检查 |
| CMake configure报错但pyproject.toml看起来正确 | 检查是否dotted key冲突 | 搜索文件中所有`xxx.yyy =`模式 |
| editable安装后import失败 | wheel.packages配置错误或包目录名不匹配 | 检查wheel.packages值与实际目录名一致 |
| 构建出现DeprecationWarning | 使用了废弃配置键（陷阱2） | 对照本模式关键配置项表逐一检查 |
| 团队成员不熟悉CMake | 迁移有学习成本 | 确保至少一人掌握CMake基础语法后再推广 |

## 检验标准

做完之后怎么知道做对了？

- [ ] `pyproject.toml` 的 `[build-system].requires` 只有 `scikit-build-core>=0.9`，无cmake/ninja
- [ ] 使用 `build.verbose` 而非 `cmake.verbose`
- [ ] Ninja生成器通过 `cmake.args = ["-G", "Ninja"]` 设置，无 `cmake.generator`
- [ ] `[tool.scikit-build]` 中无任何 `cmake.xxx` dotted key（如cmake.version），cmake相关配置全部在 `[tool.scikit-build.cmake]` 显式表中
- [ ] CMakeLists.txt存在，有 `LANGUAGES NONE`
- [ ] CMakeLists.txt中**无**任何 `install(DIRECTORY)` 或 `install(FILES)` 规则
- [ ] `pip install -e .` 成功完成，耗时<1秒，无Permission denied
- [ ] 全新虚拟环境中 `pip install .` 后import正常
- [ ] `cmake -S . -B build/test` 配置0.1秒内完成，无错误
- [ ] 构建过程无DeprecationWarning

## 迁移示例

### 示例1：invoke任务管理工具（本项目，源案例）

- **包目录**：`tasks/`（9个Python模块）
- **配置**：wheel.packages = ["tasks"], LANGUAGES NONE
- **结果**：scikit-build-core 1.0.3 + CMake 4.4.0 + Ninja 1.13.0，editable wheel构建<1秒
- **环境**：Windows + Python 3.13（cp313）

### 示例2：从setuptools迁移的通用纯Python CLI

```toml
# setuptools旧配置（迁移前）
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

# 迁移后按本模式配置即可，9行CMakeLists.txt
```

### 示例3：未来计划添加C扩展的纯Python项目（渐进式）

- **阶段1（当前）**：纯Python，使用本模式最小配置，LANGUAGES NONE，editable构建<1秒
- **阶段2（未来）**：添加C扩展时，将LANGUAGES改为CXX，在CMakeLists.txt中添加pybind11_add_module()和install(TARGETS ...)，其他配置无需改动
- **优势**：迁移到scikit-build-core后，未来添加C扩展不需要再次迁移构建系统，只需修改CMakeLists.txt

### 示例4：跨领域——概念迁移到其他构建后端

核心洞察"**构建系统需要一个最小入口文件，即使没有实际构建工作**"可迁移到：
- **meson-python**：纯Python项目也需要meson.build，即使没有编译目标
- **maturin**：混合Python/Rust项目需要Cargo.toml作为构建入口
- **Bazel**：纯Python目标也需要BUILD文件声明py_library

## 错误症状→原因速查表

| 症状 | 最可能的原因 | 修复方法 |
|------|-------------|---------|
| `pip install` 挂起无输出，进程不退出 | TOML中cmake.xxx dotted key与[tool.scikit-build.cmake]表冲突（陷阱4） | 删除cmake.xxx dotted key，用minimum-version替代cmake.version |
| `CMake Error: The source directory does not appear to contain CMakeLists.txt` | 删除了CMakeLists.txt（陷阱5） | 添加9行最小CMakeLists.txt，LANGUAGES NONE |
| `CMake Warning: Manually-specified variables were not used: ...` | 使用了不存在的cmake.generator（陷阱3） | 改用cmake.args = ["-G", "Ninja"] |
| `DeprecationWarning: cmake.verbose is deprecated` | 使用了cmake.verbose（陷阱2） | 改为build.verbose |
| Windows editable模式 `Permission denied` | 手写了install(DIRECTORY)规则（陷阱6） | 删除install规则，用wheel.packages自动处理 |
| 构建时警告cmake版本不对 | 在build-system.requires中手动放了cmake（陷阱1） | 移除cmake/ninja，由scikit-build-core自动管理 |

## 与其他模式的关系

| 模式 | 关系 |
|------|------|
| [conda-build-scikit-build-core-native](conda-build-scikit-build-core-native.md) | 互补：本模式是**纯Python+pip wheel**最小配置；那个模式是**C/C++原生扩展+conda-build**的完整配置 |
| [capability-stack-progressive-building](../methodology-patterns/governance-strategy/capability-stack-progressive-building.md) | 方法论基础：构建系统迁移在七层栈中位于L7，应在功能稳定后最后进行 |
| [container-devtool-seven-layer-stack](../architecture-patterns/container-devtool-seven-layer-stack.md) | 配套架构：L7构建系统层使用本模式的配置 |

## Changelog

<!-- changelog -->
- 2026-08-27 | feat | 从Jupyter Podman Rootless七轮优化复盘萃取，L1-draft单案例待验证
