# [项目名称] C++ 依赖瘦身优化（[新库] 替换 [旧库]） - 产品需求文档

> **模板版本**: v1.0 | 基于 Caffe→tvm-ffi 瘦身实践萃取
> **使用说明**: 将 `[占位符]` 替换为实际项目信息，删除不需要的章节，填写具体内容。每个章节末尾的「填写指引」给出了填写要求。

---

## Step 0: 环境预检（MANDATORY PRE-CHECK）

> ⚠️ **本步骤必须在写任何代码之前完成**，否则会因为环境不匹配浪费30%以上时间。

### 0.1 原项目构建环境信息

| 项 | 值 | 验证方式 |
|----|---|---------|
| 原项目推荐构建平台 | [Linux/macOS/Windows/Cross-platform] | 阅读原项目 README/INSTALL 文档 |
| 原项目编译器要求 | [GCC X+/Clang Y+/MSVC Z+] | 检查 CMakeLists.txt 中 CXX_STANDARD |
| 原项目C++标准 | [C++11/C++14/C++17/C++20] | 检查 CMAKE_CXX_STANDARD |
| 我们的目标构建平台 | [推荐优先使用原项目原生平台；Linux-origin项目优先WSL] | 决策记录 |
| 目标编译器版本 | [具体版本号，如 GCC 9.4.0] | `g++ --version` / `clang++ --version` |
| 目标C++标准 | [由新依赖库决定，如 tvm-ffi 要求 C++17] | 检查新库 CMakeLists.txt |

**环境预检确认清单（全部打勾后才能继续）：**
- [ ] 已阅读原项目 README/INSTALL 文档，确认推荐构建平台
- [ ] 已在目标平台验证编译器可用性（编译一个 hello world 通过）
- [ ] 已确认新依赖库在目标平台可正确编译
- [ ] 已决策跨平台策略（单平台优先 / 跨平台兼容），跨平台风险已评估并记录
- [ ] 如是 Windows 环境下的 Linux 原生 C++ 项目，已优先切换到 WSL

### 0.2 跨平台风险评估

| 风险项 | 评估 | 缓解措施 |
|--------|------|---------|
| POSIX 函数（unistd.h, dlfcn.h 等）在 Windows 不可用 | [高/中/低] | [使用条件编译/替换为跨平台替代] |
| MSVC 与 GCC/Clang 语法差异（如 `__attribute__`、`typeof`） | [高/中/低] | [宏隔离/使用标准 C++ 语法] |
| 路径分隔符差异（/ vs \） | [高/中/低] | [使用 std::filesystem::path] |
| 第三方库在目标平台的可用性 | [高/中/低] | [包管理器安装/源码编译] |
| 其他：[具体风险] | [高/中/低] | [缓解措施] |

**填写指引**: 环境预检是为了避免"代码写完了发现 Windows 上根本编不过"的问题。必须用实际命令验证，不能凭记忆假设。

---

## Step 0.5: API 映射前置验证（MANDATORY PRE-CHECK）

> ⚠️ **本步骤必须在迁移业务代码之前完成**，"边猜边写"会导致5-6轮返工。

### 0.5.1 旧依赖 API 使用清单

对每个要替换的旧依赖库，使用 grep 扫描完整使用情况：

```bash
# 示例：扫描 boost 使用
grep -rn "#include <boost" [源码目录] --include="*.hpp" --include="*.cpp" --include="*.h" | sort
grep -rn "boost::" [源码目录] --include="*.hpp" --include="*.cpp" --include="*.h" | grep -v "//.*boost::" | sort
```

| 旧依赖库 | 使用的组件/API | 使用位置（文件数） |
|---------|---------------|-----------------|
| [旧库1，如 boost] | [组件1: shared_ptr/make_shared] | [文件数: 如 45个文件] |
| [旧库1] | [组件2: mutex/condition_variable/scoped_lock] | [文件数] |
| [旧库2，如 glog] | [组件1: LOG(INFO/WARNING/ERROR/FATAL)] | [文件数] |
| [旧库2] | [组件2: CHECK/CHECK_EQ/DCHECK 系列宏] | [文件数] |
| ... | ... | ... |

### 0.5.2 旧API→新API映射表

对每个旧API，给出对应的新API替代方案，并**编写最小验证程序（10-20行）确认用法正确**后，才能标记为"已验证"。

| 旧API | 新API替代 | 验证状态 | 验证代码片段 |
|-------|----------|---------|------------|
| `boost::shared_ptr<T>` | `std::shared_ptr<T>` | ☐ 未验证 / ☑ 已验证 | `auto p = std::make_shared<int>(42); CHECK(*p == 42);` |
| `boost::mutex` | `std::mutex` | ☐ / ☑ | ... |
| `glog::LOG(INFO)` | 自定义日志宏 + `std::cerr` | ☐ / ☑ | ... |
| `CHECK_EQ(a, b)` | `ICHECK_EQ(a, b)` (tvm-ffi) | ☐ / ☑ | ... |
| ... | ... | ... | ... |

**API映射确认清单：**
- [ ] 已使用 grep 完整扫描所有旧依赖的使用点（含间接使用）
- [ ] 每个旧API都有对应的新API映射方案
- [ ] 每个映射都有最小验证程序（至少编译+运行通过）
- [ ] 对新库中不存在直接等价API的情况，已设计兼容层方案（见 Step 1）
- [ ] 对存在语义差异的API（如错误处理机制不同），已记录语义差异和适配方案

**填写指引**: "最小验证程序"是关键——不能只看文档觉得"应该可以"，必须写个小程序编译运行过，确认API名称、参数、返回值、include路径都正确。

---

## Step 1: 依赖闭包分析（MANDATORY PRE-CHECK）

> ⚠️ **禁止"我觉得需要哪些文件"的正向猜测**。必须使用工具获取真实的 include 闭包。

### 1.1 入口点识别

| 入口类型 | 文件路径 | 说明 |
|---------|---------|------|
| 主库入口头文件 | [如 include/caffe/caffe.hpp] | 所有外部使用者 include 的主头文件 |
| FFI/绑定入口 | [如 src/caffe/_caffe.cpp] | Python/其他语言绑定入口 |
| 其他入口 | [如 tools/caffe.cpp（如迁移）] | |

### 1.2 Include 闭包分析

使用编译器获取真实的头文件依赖树：

```bash
# 方法1（推荐）：使用 g++ -H 输出 include 树
g++ -H -I[include路径] -fsyntax-only [入口文件.cpp] 2>&1 | grep -E "^\." | sort

# 方法2：使用 CMake 生成的 compile_commands.json + clangd
# 配置 CMAKE_EXPORT_COMPILE_COMMANDS=ON，然后用 clangd 检查

# 方法3：使用 include-what-you-use (iwyu)
iwyu [源文件.cpp]
```

### 1.3 必需迁移文件清单

基于闭包分析结果，列出**所有**需要迁移的头文件和源文件，按模块分组：

| 模块 | 必需头文件 | 必需源文件 | 备注 |
|------|-----------|-----------|------|
| [核心抽象] | [文件列表] | [文件列表] | [Blob, Layer, Net 等] |
| [Util工具] | [文件列表] | [文件列表] | [math, io, logging 等] |
| [Layer实现] | [文件列表] | [文件列表] | [推理路径所需层] |
| [Proto] | [caffe.proto] | [生成的 .pb.cc] | |
| [FFI/绑定] | [文件列表] | [文件列表] | |
| [兼容层] | [compat/*.hpp] | (header-only) | 新建，见 Step 2 |
| **总计** | **XX个** | **YY个** | |

**不在范围内（明确不迁移）：**
- [ ] GPU/CUDA 相关文件（如仅目标 CPU）
- [ ] 训练相关 solver（如仅目标推理）
- [ ] 第三方数据库后端（LMDB/LevelDB/HDF5 等）
- [ ] 其他语言绑定（MATLAB/Java/R 等）
- [ ] 工具程序（tools/）
- [ ] 示例和文档
- [ ] 其他：[具体列出]

**闭包分析确认清单：**
- [ ] 使用 `-H` 或等效工具获取了完整 include 树
- [ ] 必需迁移文件清单一次性列出（不是迁移过程中临时补）
- [ ] 明确区分"必需迁移"和"不迁移"的文件，边界清晰
- [ ] 对每个"不迁移"的文件，确认没有其他必需文件依赖它

**填写指引**: 正向猜测"大概需要哪些文件"是头文件遗漏的主要原因。"打地鼠式补文件"（编译报错→补一个文件→再报错→再补）会浪费大量时间。用工具做闭包分析一次性列出清单。

---

## Overview

- **Summary**: 对 [原项目名称] 的 C++ 核心库进行依赖瘦身，使用 [新库名称]（C++[XX]标准）替换 [旧库1]、[旧库2] 等老旧依赖。瘦身完成的代码放置到 [目标目录]，通过 [FFI/绑定机制] 提供上层语言接口。最终形成一个不依赖 [旧库列表]、使用 C++[XX] 标准库 + [新库] 的轻量核心库。
- **Purpose**: 原始 [原项目] 依赖 [旧库及其组件数量]，编译配置复杂、跨平台问题频发（[列举具体痛点]）。通过替换为 [新库] + C++[XX] 标准库，大幅减少外部依赖，提高可维护性和构建效率，使得 [目标产物] 可以作为独立包分发使用。
- **Target Users**: [使用瘦身核心库的开发者画像]

## Goals

- 使用 [新库] 的 [错误/检查系统] 替换 [旧库] 的 [对应功能]
- 使用 C++[XX] 标准库替换 [旧库] 各组件（[具体组件映射]）
- 编写最小兼容层（compat/）替代 [旧库] 中 [新库+标准库] 未直接覆盖的API
- 移除 [需要移除的旧依赖] 依赖
- 将 [绑定/FFI文件] 从 [旧绑定机制] 重写为 [新绑定机制]
- 将瘦身完成的代码放置到 [目标目录]
- 适配现有上层代码使用新接口
- 提供统一的 CMake 构建系统
- 确保瘦身代码编译通过、核心功能完整、无内存泄漏

## Non-Goals (Out of Scope)

- 不修改 [原项目源码目录]（只读参考）
- 不保留 [明确不支持的功能，如 CUDA/训练等]
- [其他不在范围内的内容]

## Background & Context

- **[新库名称]** 位于 [路径]，要求 C++[XX]，提供：
  - [列出新库核心能力]
- **C++[XX] 标准库**已涵盖 [旧库] 绝大多数常用功能（[具体映射见 0.5.2]）
- **[原项目] 当前[旧库]使用分布**（需要替换）：
  - [详细见 0.5.1 API 使用清单]

## Functional Requirements

- **FR-1**: 提供最小兼容层头文件（`compat/`），将 [旧库] API 映射到 [新库] + C++[XX] std:: 实现
- **FR-2**: 核心抽象完成依赖替换，无 [旧库] 引用
- **FR-3**: 必要的 util 组件完成依赖替换
- **FR-4**: 核心功能模块完成依赖替换
- **FR-5**: 重写绑定/FFI 模块为新机制（移除旧绑定依赖）
- **FR-6**: 提供统一的 CMake 构建系统
- **FR-7**: 适配上层语言（Python/其他）使用新接口
- **FR-8**: 完全移除所有旧依赖的引用和链接

## Non-Functional Requirements

- **NFR-1（编译）**: 瘦身代码在 C++[XX] 编译器下编译无错误，不依赖 [旧库开发包]
- **NFR-2（功能等价）**: 替换后的核心逻辑与原始项目行为一致
- **NFR-3（性能）**: 性能不低于原始版本（[具体性能指标]）
- **NFR-4（内存安全）**: 无内存泄漏（RAII 自动管理）
- **NFR-5（代码规范）**: 遵循现有代码风格，不引入新的第三方依赖
- **NFR-6（最小依赖）**: 瘦身核心库外部依赖仅有：C++[XX]标准库、[新库]、[其他必需依赖如 protobuf/BLAS]
- **NFR-7（构建效率）**: 相比原项目完整构建，构建时间显著减少

## Constraints

- **Technical**: C++[XX] 标准；[功能限制如 CPU_ONLY]；不修改原文件；[新绑定机制的技术约束]
- **Business**: 代码放置到 [目标目录]；保持 License 声明
- **Dependencies**: [已有依赖列表]

## Assumptions

- [新库] 可作为 CMake 子项目引入
- [代码生成依赖如 protobuf] 处理方式
- [核心功能范围的假设]
- [绑定层实现方式的假设]
- [其他假设]

## Acceptance Criteria

### AC-1: 源码无旧依赖残留
- **Given**: 瘦身完成后目标目录下所有 C++ 源文件
- **When**: 执行 grep 搜索旧依赖引用
- **Then**: 除 compat/ 兼容层（如有必要的映射别名）外，所有源文件不包含旧依赖引用
- **Verification**: `programmatic`

### AC-2: CMake 配置不查找旧依赖
- **Given**: CMakeLists.txt 和 cmake 模块
- **When**: 检查 find_package 和 target_link_libraries
- **Then**: 仅查找/链接新依赖和必需的系统库，不包含旧依赖
- **Verification**: `programmatic`

### AC-3: C++[XX] 编译通过
- **Given**: 使用 CMake 配置并编译
- **When**: 执行 cmake + 编译
- **Then**: 编译成功无错误
- **Verification**: `programmatic`

### AC-4: 核心功能可用
- **Given**: [具体测试场景]
- **When**: [操作步骤]
- **Then**: [预期结果]
- **Verification**: `programmatic`

### AC-5: 兼容层 API 覆盖完整
- **Given**: 新的 compat/ 头文件
- **When**: 检查所有被替换的 API
- **Then**: 所有旧API均有可用替代
- **Verification**: `human-judgment`

### AC-6: CHECK/异常处理正确
- **Given**: 触发检查失败的测试用例
- **When**: 执行触发失败的代码
- **Then**: 抛出预期异常，消息包含文件/行号/条件
- **Verification**: `programmatic`

### AC-7: 目录结构符合规范
- **Given**: 目标目录结构
- **When**: 检查文件布局
- **Then**: [具体目录结构要求]
- **Verification**: `human-judgment`

### AC-8: 无内存泄漏
- **Given**: 多次创建销毁核心对象
- **When**: 使用 valgrind/ASan 运行测试
- **Then**: 无明确内存泄漏报告
- **Verification**: `programmatic`

### AC-9: 上层接口兼容
- **Given**: 适配后的上层代码和现有测试
- **When**: 运行测试
- **Then**: 测试通过
- **Verification**: `programmatic`

### AC-10: FFI/绑定模块可正确加载
- **Given**: 编译生成的绑定模块
- **When**: 在目标语言中加载
- **Then**: 加载成功，可以调用导出函数
- **Verification**: `programmatic`

## Open Questions

- [ ] [待确认问题1]
- [ ] [待确认问题2]
