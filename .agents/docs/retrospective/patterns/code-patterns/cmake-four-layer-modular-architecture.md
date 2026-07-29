---
id: "cmake-four-layer-modular-architecture"
source: "caffe-ffi CMakeLists.txt第二轮深度原子化复盘 (2026-07-29)"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/cmake-four-layer-modular-architecture.toml"
---
# CMake四层模块化架构模式

## 模式概述

将超过100行的 CMakeLists.txt 按"变量→依赖→函数→目标"四层职责拆分为独立模块，配合严格include顺序声明依赖关系，消除跨模块重复代码。物理拆分（Round 1）后必须进行逻辑抽象（Round 2）提取公共函数，避免"拆了文件但没消除重复"的假模块化。

## 触发场景

- 单文件 CMakeLists.txt 超过 100 行，包含选项定义、依赖查找、编译配置、目标构建等多种职责
- 多个构建目标（主库+测试+示例）存在重复的 `target_compile_*` 配置
- Windows/Linux/macOS 平台判断逻辑散落在多个位置
- 新增模块时不确定include顺序，函数"未定义"错误反复出现

## 核心步骤

### 第一步：按四层职责划分模块文件

| 层级 | 文件名 | 职责 | 依赖 |
|------|--------|------|------|
| **选项层** | `Options.cmake` | C++标准、构建选项（option()）、cmake_policy | 无依赖（最底层） |
| **依赖层** | `Dependencies.cmake` + `Detect<Name>.cmake` | 第三方库查找，每个复杂依赖独立为Detect模块 | Options |
| **函数层** | `<Xxx>Config.cmake` | 封装公共target_*配置为可复用function | 依赖层设置的变量 |
| **目标层** | `TargetBuild.cmake`/`Tests.cmake`/`Install.cmake` | add_library/add_executable定义具体目标 | 函数层 |
| **平台层** | `<Platform>DllCopy.cmake` | 平台特定逻辑（Windows DLL复制/macOS rpath等） | 目标层 |

⚠️ **命名强制规则**：自定义依赖检测模块**必须**使用 `Detect<Name>.cmake`，**禁止**使用 `Find<Name>.cmake`（会与CMake内置模块冲突导致无限递归）。

### 第二步：严格按依赖顺序编排入口文件

主 `CMakeLists.txt` 仅负责include，不包含业务逻辑，include顺序必须遵循依赖链：

```cmake
# CMakeLists.txt 入口（建议不超过15行）
cmake_minimum_required(VERSION 3.20)
project(my_project CXX)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
include(Options)          # 1. 选项（无依赖）
include(Dependencies)     # 2. 依赖查找（依赖Options）
include(CompilerConfig)   # 3. 公共函数（依赖Dependencies的变量）
include(ProtoCompile)     # 4. 代码生成（依赖Dependencies的Protobuf）
include(TargetBuild)      # 5. 主目标构建（使用CompilerConfig函数）
include(WindowsDllCopy)   # 6. 平台适配（配置主目标的DLL复制）
include(Tests)            # 7. 测试目标（使用CompilerConfig + WindowsDllCopy）
include(Install)          # 8. 安装规则
```

### 第三步：两轮重构策略

- **Round 1（物理拆分）**：将单文件按职责拆分为多个 .cmake 文件，保持功能等价
- **Round 2（逻辑抽象）**：审查拆分后的文件，提取跨模块重复代码为公共函数（关键！跳过这一步等于没做模块化）

### 第四步：编写 cmake/README.md 说明模块依赖

必须为模块目录编写README，明确说明：
- 每个模块的职责
- include顺序约束链
- 模块间依赖关系图

## 反模式

### ❌ 反模式1：Find<Name>.cmake 命名冲突（致命）
```cmake
# 错误：自定义模块命名为 FindBLAS.cmake
# cmake/FindBLAS.cmake
find_package(BLAS QUIET)  # CMake优先搜索CMAKE_MODULE_PATH，递归调用自己→无限循环
```
结果：cmake configure时无限循环，"Found BLAS"消息重复输出上百次后崩溃。必须重命名为 `DetectBLAS.cmake`。

### ❌ 反模式2：只做物理拆分不做逻辑抽象（假模块化）
```cmake
# 拆分后 Tests.cmake 和 TargetBuild.cmake 都有这段重复代码：
target_include_directories(test_target PRIVATE ${SOME_INCLUDES})
target_compile_definitions(test_target PRIVATE CPU_ONLY USE_OPENBLAS)
target_compile_options(test_target PRIVATE /W4 /MP)
target_link_libraries(test_target PRIVATE ${BLAS_LIBRARIES} protobuf::libprotobuf)
```
结果：Tests.cmake 从123行只减到100行（-19%），没有消除重复。正确做法是提取到 `CompilerConfig.cmake` 的公共函数中，Tests.cmake可精简83%（123→21行）。

### ❌ 反模式3：Dependencies.cmake 职责过重
```cmake
# Dependencies.cmake 中直接写70行BLAS检测逻辑
if(MSVC)
  find_library(BLAS_LIB NAMES openblas PATHS ${CONDA_PREFIX}/Library/lib ...)
  # ...70行后...
endif()
find_package(Protobuf REQUIRED)
find_package(TVM REQUIRED)
```
结果：Dependencies.cmake 膨胀到99行，BLAS逻辑无法独立复用。正确做法是拆分为 `DetectBLAS.cmake`，Dependencies.cmake中只做 `include(DetectBLAS)`。

### ❌ 反模式4：include顺序随意
```cmake
# 错误：Tests在CompilerConfig之前include
include(Tests)          # 使用caffe_ffi_configure_target()，但函数尚未定义
include(CompilerConfig) # 函数定义
```
结果：CMake报"Unknown CMake command"错误。include顺序本身就是依赖声明——被依赖的函数定义模块必须在使用方之前include。

### ❌ 反模式5：平台判断散落在多个文件
```cmake
# TargetBuild.cmake 中有 if(MSVC) 复制DLL
# Tests.cmake 中也有 if(MSVC) 复制DLL
# WindowsDllCopy.cmake 中也有 if(MSVC) 复制DLL
```
结果：DLL复制逻辑重复65行，修改时需要改3处。正确做法是统一封装到平台专用模块。

## 检验标准

做完后如何验证模块化质量：

1. **行数标准**：单个.cmake模块不超过100行（除了平台专用文件）
2. **重复率**：跨模块target_*配置代码重复为0
3. **入口精简**：主CMakeLists.txt不超过20行，只做project() + include()
4. **顺序正确**：按依赖链include，无"Unknown CMake command"错误
5. **命名合规**：所有自定义检测模块为Detect<Name>.cmake，无Find<Name>.cmake
6. **文档完整**：cmake/README.md说明了模块关系和include顺序
7. **实际构建**：cmake configure + build + 测试全部通过

## 迁移验证

- ✅ **caffe-ffi项目**：CMakeLists.txt从~480行单文件拆分为9个模块，Tests.cmake从123行→21行（-83%），Dependencies.cmake从99行→31行（-69%），修复3个Bug（含FindBLAS命名冲突致命Bug），py314+MSVC环境40个C++测试全部通过
- ✅ **通用场景**：任何使用CMake构建、超过100行的C/C++项目均可套用此模式，尤其适合多目标（库+测试+示例）项目

## 适用条件

- 构建系统：CMake 3.15+（支持cmake_parse_arguments）
- 项目规模：单文件CMakeLists.txt超过100行，或有≥2个构建目标
- 平台需求：需要跨平台支持（Windows/Linux/macOS）时收益最大
- 不适用：简单单目标项目（<50行CMakeLists.txt），模块化反而增加文件数量开销
