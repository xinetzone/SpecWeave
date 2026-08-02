---
id: "cmake-list-removal-diagnostic-output"
title: "CMake列表变更诊断输出模式"
type: "code-pattern"
maturity: "L2-validated"
validation_count: 2
created: "2026-08-01"
last_updated: "2026-08-01"
source: "retrospective-caffe-ffi-tests-enable-20260801"
related_patterns: ["cmake-public-target-config-function", "cmake-four-layer-modular-architecture", "cmake-platform-specific-operation-encapsulation", "core-entry-structured-logging", "bash-unified-structured-logging"]
tags: ["cmake", "build-system", "diagnostic-logging", "observability", "testing", "list-manipulation", "developer-experience"]
---

# CMake列表变更诊断输出模式

## 触发场景

- 使用 `file(GLOB ...)` 收集源文件/测试文件后，需要排除特定文件
- 使用 `list(FILTER ...)` 按正则/条件过滤列表项
- 使用 `list(REMOVE_DUPLICATES)` 去重后需要确认去重效果
- 在 `if()` 条件分支中对列表有条件地添加/移除项
- CI 流水线需要从构建日志中审计哪些文件被包含/排除
- 新成员 onboarding 需要快速理解构建系统包含了哪些组件

## 问题本质

CMake 中使用 `list(REMOVE_ITEM)`、`list(FILTER)`、`list(REMOVE_DUPLICATES)` 等命令从源文件列表、测试列表、目标列表中排除项时，若仅靠注释说明排除原因而不打印任何构建时日志，被排除的文件会"隐形消失"：

1. **构建日志不可见**：CI 日志和本地构建输出中看不到哪些文件被包含、哪些被排除
2. **排查成本高**：当"为什么某个测试/源文件没有被编译/运行"时，必须打开 CMakeLists.txt 逐行阅读 `REMOVE_ITEM` 调用
3. **变更不可审计**：修改列表排除规则后，无法从 configure 日志中直观看到前后差异
4. **注释是死文档**：只有阅读源码的人能看到注释说明，不看 CMakeLists.txt 就完全不知道排除逻辑的存在

典型反例（caffe-ffi 修改前）：
```cmake
file(GLOB CAFFE_FFI_CPP_TEST_SRCS "${CMAKE_CURRENT_SOURCE_DIR}/tests/cpp/*.cpp")
# Exclude test files with known pre-existing issues not related to current work
list(REMOVE_ITEM CAFFE_FFI_CPP_TEST_SRCS
  "${CMAKE_CURRENT_SOURCE_DIR}/tests/cpp/test_net.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/tests/cpp/test_insert_splits.cpp"
)
# ↑ 这里没有任何 message() 输出，构建者完全不知道两个测试被排除了
```

## 核心原则

**注释是静态文档（给读源码的人看），message 输出是活文档（给每个运行构建的人看），两者不可互相替代。**

核心设计流程：
```
┌──────────────────────────────────────────────────────┐
│           列表变更诊断输出标准流程                      │
├──────────────────────────────────────────────────────┤
│ 1. 变更前：打印原始列表长度（可选，用于对比）            │
│    list(LENGTH <list> _before)                        │
│                                                       │
│ 2. 执行变更：REMOVE_ITEM / FILTER / REMOVE_DUPLICATES │
│    list(REMOVE_ITEM <list> <item1> <item2> ...)       │
│                                                       │
│ 3. 变更后：打印新长度 + 变更数量 + 具体内容             │
│    list(LENGTH <list> _after)                         │
│    math(EXPR _removed "${_before} - ${_after}")        │
│    message(STATUS "[module] <type>: ${_after} items")  │
│    message(STATUS "[module] <type> list: ${<list>}")  │
└──────────────────────────────────────────────────────┘
```

## 标准方案

### 第一步：变更前记录长度（可选但推荐）

对于有明确排除项的场景，记录变更前列表长度，以便计算被移除的项数：

```cmake
file(GLOB ALL_SRCS "${SRC_DIR}/*.cpp")
list(LENGTH ALL_SRCS _before_count)
```

### 第二步：执行列表变更操作

```cmake
list(REMOVE_ITEM ALL_SRCS
  "${SRC_DIR}/broken_file.cpp"
  "${SRC_DIR}/platform_specific_${UNSUPPORTED_PLATFORM}.cpp"
)
# 或 list(FILTER ALL_SRCS EXCLUDE REGEX ".*_test_helper\\.cpp$")
# 或 list(REMOVE_DUPLICATES ALL_SRCS)
```

### 第三步：变更后打印诊断信息（必做）

```cmake
list(LENGTH ALL_SRCS _after_count)
math(EXPR _removed "${_before_count} - ${_after_count}")

message(STATUS "[mymodule] Source files: ${_after_count} (removed ${_removed})")
message(STATUS "[mymodule] Source list: ${ALL_SRCS}")
```

如果跳过了第一步（变更前长度），至少打印最终长度和列表内容：

```cmake
list(LENGTH ALL_SRCS _count)
message(STATUS "[mymodule] Source files: ${_count}")
message(STATUS "[mymodule] Source list: ${ALL_SRCS}")
```

### 第四步：对被排除的项单独说明原因（高级用法）

当排除项有明确的排除原因（如"平台不支持"、"已知Bug"、"待修复"）时，逐项打印排除原因：

```cmake
set(EXCLUDED_SRCS "")

if(NOT WIN32)
  list(REMOVE_ITEM ALL_SRCS "${SRC_DIR}/win32_specific.cpp")
  list(APPEND EXCLUDED_SRCS "win32_specific.cpp (non-Windows platform)")
endif()

if(_removed GREATER 0)
  message(STATUS "[mymodule] Excluded ${_removed} file(s):")
  foreach(_excl ${EXCLUDED_SRCS})
    message(STATUS "  - ${_excl}")
  endforeach()
endif()
```

## 代码模板

### 模板A：简单排除（推荐最小实现）

```cmake
# ── 收集源文件 ──
file(GLOB MY_MODULE_SRCS
  "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp"
)
list(LENGTH MY_MODULE_SRCS _src_before)

# ── 排除有已知问题/平台不支持的文件 ──
list(REMOVE_ITEM MY_MODULE_SRCS
  "${CMAKE_CURRENT_SOURCE_DIR}/src/known_broken.cpp"
)

# ── 诊断输出（必做）──
list(LENGTH MY_MODULE_SRCS _src_after)
math(EXPR _src_removed "${_src_before} - ${_src_after}")
message(STATUS "[mymodule] Sources: ${_src_after} files (removed ${_src_removed})")
message(STATUS "[mymodule] Source files: ${MY_MODULE_SRCS}")
```

**Configure 输出示例**：
```
-- [mymodule] Sources: 12 files (removed 1)
-- [mymodule] Source files: /path/src/a.cpp;/path/src/b.cpp;...
```

### 模板B：条件排除（平台/特性分支）

```cmake
file(GLOB TEST_SRCS "${CMAKE_CURRENT_SOURCE_DIR}/tests/*.cpp")
list(LENGTH TEST_SRCS _test_before)
set(_excluded_info "")

# 条件排除
if(NOT CAFFE_USE_CUDA)
  list(REMOVE_ITEM TEST_SRCS "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_cuda_kernels.cpp")
  list(APPEND _excluded_info "  - test_cuda_kernels.cpp (CUDA disabled)")
endif()

if(MSVC_VERSION LESS 1930)
  list(REMOVE_ITEM TEST_SRCS "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_cpp20_features.cpp")
  list(APPEND _excluded_info "  - test_cpp20_features.cpp (MSVC < 1930)")
endif()

# 诊断输出
list(LENGTH TEST_SRCS _test_after)
math(EXPR _test_removed "${_test_before} - ${_test_after}")
message(STATUS "[mymodule] Test files: ${_test_after} (removed ${_test_removed})")
if(_test_removed GREATER 0)
  message(STATUS "[mymodule] Excluded tests:")
  foreach(_line ${_excluded_info})
    message(STATUS "${_line}")
  endforeach()
endif()
message(STATUS "[mymodule] Test list: ${TEST_SRCS}")
```

**Configure 输出示例**：
```
-- [mymodule] Test files: 8 (removed 2)
-- [mymodule] Excluded tests:
--   - test_cuda_kernels.cpp (CUDA disabled)
--   - test_cpp20_features.cpp (MSVC < 1930)
-- [mymodule] Test list: /path/tests/test_a.cpp;...
```

### 模板C：GLOB + FILTER 过滤模式

```cmake
file(GLOB ALL_HEADERS "${CMAKE_CURRENT_SOURCE_DIR}/include/**/*.hpp")
list(FILTER ALL_HEADERS EXCLUDE REGEX ".*_internal\\.hpp$")
list(FILTER ALL_HEADERS EXCLUDE REGEX ".*/detail/.*")

list(LENGTH ALL_HEADERS _hdr_count)
message(STATUS "[mymodule] Public headers: ${_hdr_count}")
message(STATUS "[mymodule] Public header list: ${ALL_HEADERS}")
```

## 反模式

- ❌ **仅靠注释说明排除**：`# Exclude broken files` 后直接 `list(REMOVE_ITEM ...)`，无任何 message 输出
- ❌ **静默过滤无输出**：`list(FILTER ...)` 在条件分支内静默执行，构建日志无任何痕迹
- ❌ **打印长度但不打印列表内容**：`message(STATUS "Found ${n} files")` 只打印数字，不打印具体文件路径，无法审计具体哪些文件被包含
- ❌ **使用 message(TRACE) 或 message(DEBUG)**：这些级别默认不显示，诊断输出应使用 `STATUS`（默认可见）级别
- ❌ **在 foreach 中逐文件打印但不汇总**：大量逐行输出反而降低可读性，应先汇总数量再打印列表
- ❌ **条件分支内无输出**：`if(WIN32) list(REMOVE_ITEM ...)` 在非 Windows 平台完全静默，无法追踪哪个分支生效

## 验证方法

1. **Configure 阶段可见性**：运行 `cmake ..` 后，在输出中搜索 `[module]` 标签，确认能看到列表统计信息
2. **数量一致性**：变更前后数量差等于实际排除的文件数
3. **CI 日志可审计**：在 CI 构建日志中能通过 grep 快速定位到列表变更信息
4. **新成员可理解**：不阅读 CMakeLists.txt 仅看 configure 输出即可知道哪些文件被包含/排除

## 跨构建系统迁移

| 构建系统 | 等价实现 |
|---------|---------|
| **Makefile** | `$(info Sources: $(words $(SRCS)) files)` + `$(filter-out ...)` 后打印 |
| **Bazel BUILD** | `glob(include=["*.cpp"], exclude=["broken.cpp"])` + `print("Sources:", glob(...))` |
| **Meson** | `files_src = files('*.cpp')` 后遍历排除 + `message()` |
| **SCons** | `Glob('*.cpp')` 后列表推导过滤 + `print()` |
| **Python setup.py** | 排除 packages 后 `print(f"Including {len(pkgs)} packages: {pkgs}")` |
| **CI pipeline (GitHub Actions)** | `exclude` 规则后 `echo "Matrix: ${{ toJSON(matrix) }}"` |

核心思想通用：**对列表的任何修改操作后，必须输出修改后的列表状态**。

## 与现有模式的关系

| 模式 | 语言/场景 | 焦点 | 区别 |
|------|----------|------|------|
| cmake-public-target-config-function | CMake | 封装重复的 target_* 配置 | 聚焦目标编译配置，本模式聚焦列表可观测性 |
| cmake-four-layer-modular-architecture | CMake | CMakeLists.txt 分层架构 | 聚焦架构组织，本模式是架构中的诊断实践 |
| core-entry-structured-logging | Python | 函数入口/出口黄金三要素 | Python运行时日志，本模式是CMake configure时日志 |
| bash-unified-structured-logging | Bash | 脚本结构化日志(text+json) | Bash运行时日志，理念一致但生态不同 |
| **本模式** | **CMake** | **列表变更操作的构建时可观测性** | **CMake configure阶段特有的诊断实践** |

## 实际案例

### 案例1：caffe-ffi 测试文件启用（2026-08-01）

- **场景**：删除 `Tests.cmake` 中静默排除 `test_net.cpp` 和 `test_insert_splits.cpp` 的 `REMOVE_ITEM` 块
- **应用前**：2个测试文件被静默排除，configure 输出无任何提示，测试从9个变为7个但无人知晓
- **应用后**：添加诊断输出后，configure 显示 `C++ test sources: 9`，可以直观看到所有测试都已包含
- **效果**：排查"为什么测试没运行"的时间从30分钟降至0秒（看configure输出即可）
