---
id: "cmake-code-pattern-template"
title: "CMake代码模式文档模板"
type: template
date: 2026-07-29
version: "1.0.0"
source: "萃取自3个CMake模式的共性结构：cmake-four-layer-modular-architecture / cmake-public-target-config-function / cmake-platform-specific-operation-encapsulation"
related_patterns:
  - "../../docs/retrospective/patterns/code-patterns/cmake-four-layer-modular-architecture.md"
  - "../../docs/retrospective/patterns/code-patterns/cmake-public-target-config-function.md"
  - "../../docs/retrospective/patterns/code-patterns/cmake-platform-specific-operation-encapsulation.md"
tags: ["template", "cmake", "code-pattern", "build-system", "pattern-extraction"]
x-toml-ref: "../../../.meta/toml/.agents/templates/cmake-code-pattern-template.toml"
---

# CMake代码模式文档模板

> **使用说明**：本模板从3个已验证CMake模式（四层模块化架构、公共目标配置函数、平台特定操作封装）的共性结构萃取而成。当你从CMake构建系统实践中提炼出新的可复用代码模式时，复制本模板，将 `{占位符}` 替换为实际内容即可入库到 `.agents/docs/retrospective/patterns/code-patterns/`。
>
> **适用场景**：编写CMake构建系统相关的代码模式入库文档（code-patterns/）。
>
> **结构说明**：9章节固定结构——概述→触发场景→核心步骤→反模式→检验标准→迁移验证→适用条件，与development-standard-template相比更聚焦CMake构建领域，步骤更具体、反模式更典型。
>
> **配套文件**：TOML元数据模板 [cmake-code-pattern-template.toml](cmake-code-pattern-template.toml)，填写后放置于 `.meta/toml/.agents/docs/retrospective/patterns/code-patterns/{pattern-id}.toml`。

---

## 模板填写顺序

> **填写指引**：按以下顺序填写，避免跳跃导致结构不一致：
>
> 1. **frontmatter**：填写id/source/x-toml-ref
> 2. **模式标题+概述**：一句话说清"解决什么问题+核心机制+关键收益"
> 3. **触发场景**：列出可观察的信号（≥3条），帮助读者判断是否适用
> 4. **核心步骤**：分步骤描述"怎么做"，每步配CMake代码示例
> 5. **反模式**：列出典型错误写法+后果+正确做法（≥3个）
> 6. **检验标准**：可量化/可验证的验收标准（≥5条）
> 7. **迁移验证**：已验证的项目+通用场景适用性
> 8. **适用条件**：CMake版本要求+项目规模+不适用场景

---

<!-- 以下为模式文档正文模板，复制到code-patterns/目录后替换{占位符} -->

```yaml
---
id: "{pattern-id-kebab-case}"
source: "{来源复盘/项目名称与日期，如：caffe-ffi CMakeLists.txt第二轮深度原子化复盘 (2026-07-29)}"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/{pattern-id-kebab-case}.toml"
---
```

# {模式标题}（中文描述模式核心要点，如"CMake四层模块化架构模式"）

## 模式概述

{1-3句话概述：模式解决什么问题、核心机制是什么、关键收益是什么。例如：将超过100行的CMakeLists.txt按四层职责拆分为独立模块，配合严格include顺序声明依赖关系，消除跨模块重复代码。}

{可选第二段：补充两轮重构策略说明、与其他模式的关系、关键注意事项。}

## 触发场景

- {触发条件1：描述什么情况下应该使用此模式，需具体可观察的信号，如"单文件CMakeLists.txt超过100行"}
- {触发条件2：如"多个构建目标存在重复的target_*配置"}
- {触发条件3：如"平台判断逻辑散落在多个位置"}
- {至少3条触发场景，每条以可观察的信号描述而非抽象原则}

## 核心步骤

### 第一步：{步骤标题，如"创建公共配置文件，定义配置函数"}

{步骤说明文字，解释为什么要做、做什么}

```cmake
# 代码示例：展示正确的做法
{完整CMake代码块}
```

⚠️ **关键规则**：{必须遵守的强制规则，违反会导致严重问题。如"所有target_*命令必须使用${ARG_VISIBILITY}变量，禁止硬编码PRIVATE/PUBLIC"}

### 第二步：{步骤标题}

{步骤说明}

```cmake
{CMake代码块}
```

### 第三步：{步骤标题}

{步骤说明}

```cmake
{CMake代码块}
```

{根据模式复杂度增加步骤，CMake模式通常4-6步。参考示例：四层架构4步、公共配置函数4步、平台封装6步。}

## 反模式

> **填写指引**：每个反模式必须包含三部分——错误代码示例、具体后果（非抽象描述）、正确做法简述。CMake模式尤其要覆盖以下典型陷阱：命名冲突（Find<Name>.cmake）、硬编码（PRIVATE/VISIBILITY）、参数遗漏（无校验）、include顺序错误、平台判断散落、复制粘贴导致参数错误、option僵尸、macro()变量泄漏。

### ❌ 反模式1：{反模式名称，如"Find<Name>.cmake命名冲突（致命）"}
```cmake
# 错误示例：展示典型错误写法
{错误CMake代码}
```
结果：{描述错误写法导致的具体后果，如"cmake configure时无限循环，消息重复输出上百次后崩溃"。正确做法是{一句话说明正确做法，如"重命名为DetectBLAS.cmake"}。}

### ❌ 反模式2：{反模式名称}
```cmake
# 错误示例
{错误CMake代码}
```
结果：{具体后果}。正确做法是{正确做法简述}。

### ❌ 反模式3：{反模式名称}
```cmake
# 错误示例
{错误CMake代码}
```
结果：{具体后果}。正确做法是{正确做法简述}。

{至少3个反模式，推荐4-5个。每个都要有代码+后果+正确做法三件套。}

## 检验标准

做完后如何验证模式应用质量：

1. **{标准名称1，如"入口精简"}**：{可量化/可验证的标准描述，如"主CMakeLists.txt不超过20行，只做project() + include()"}
2. **{标准名称2，如"零重复"}**：{可量化标准，如"跨模块target_*配置代码重复为0"}
3. **{标准名称3，如"参数校验完整"}**：{可验证标准，如"传入不存在的target/缺失VISIBILITY时均有友好FATAL_ERROR提示"}
4. **{标准名称4，如"命名合规"}**：{可验证标准，如"自定义检测模块为Detect<Name>.cmake，无Find<Name>.cmake"}
5. **{标准名称5，如"实际构建"}**：{可验证标准，如"cmake configure + build + 测试全部通过"}
{至少5条检验标准，应包含：代码行数标准、零重复标准、参数校验标准、功能验证标准、实际构建验证标准}

## 迁移验证

- ✅ **{项目名称，如caffe-ffi项目}**：{具体验证数据：行数减少比例（如Tests.cmake从123行→21行（-83%））、修复Bug数量、测试通过情况等量化结果}
- ✅ **通用场景**：{描述哪些通用场景可以套用此模式，如"任何使用CMake构建、超过100行的C/C++项目均可套用"}

## 适用条件

- CMake版本 ≥ {最低版本要求，如3.15}（说明依赖的CMake特性，如"支持cmake_parse_arguments"）
- 项目规模：{描述适用的项目规模/复杂度阈值，如"单文件CMakeLists.txt超过100行，或有≥2个构建目标"}
- 特别适合：{最高收益场景，如"需要跨平台支持（Windows/Linux/macOS）时收益最大"}
- 不适用：{不适用场景描述，避免过度使用，如"简单单目标项目（<50行CMakeLists.txt），模块化反而增加文件数量开销"}
