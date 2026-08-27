---
id: "cpp-header-first-fact-collection"
title: "大型 C/C++ 项目的头文件优先事实采集策略"
source: "../../../../../../bundles/retrospective-okf-wiki-build.md#L157-L174"
maturity: "L2"
validation_count: 2
reuse_count: 0
documentation_level: "detailed"
related_patterns:
  - "vendor-high-level-doc-first-research"
  - "open-source-repo-four-layer-identification"
  - "source-pipeline-penetration-method"
  - "source-code-to-okf-wiki-workflow"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/patterns/methodology-patterns/research-knowledge/cpp-header-first-fact-collection.toml"
---
# 大型 C/C++ 项目的头文件优先事实采集策略

## 模式类型

方法论模式（源码事实采集 / 知识沉淀）

## 成熟度

L2 已验证（2 次独立案例验证：Apache TVM 编译器、TuyaOpen 嵌入式 IoT，均在本项目 OKF 知识包构建任务中执行）

## 模式概述

对源码规模 >1000 文件、含头文件与实现文件分离的 C/C++ 项目做**事实采集**（R 阶段）时，以 `include/` 头文件为 API 声明的权威来源，实现文件（`.c`/`.cc`）仅用于验证函数存在性和理解内部数据流，构建系统文件（Kconfig/CMakeLists.txt）作为模块依赖关系和架构裁剪的补充信息来源，V 阶段在头文件中 Grep 验证每个类名/宏名并检查命名空间前缀。

核心价值是**降低 AI 文档生成中的 API 虚构率**——C++ 项目的 API 虚构风险显著高于 Python 和 Markdown 项目，根因是"版本迁移期的统计惯性"（AI 把训练数据中的旧版 API 当作源码中真实存在的新版 API），而头文件权威性分层是消除这一风险的最有效手段。

## 问题现象

直接让 AI 从 C/C++ 源码采集事实并生成文档时，常见的失败模式：

1. **从实现文件提取 API 声明**：把 `.c`/`.cc` 中的静态函数、内部宏当成公共 API 写入文档，读者无法从外部使用。
2. **虚构旧版 API**：AI 基于训练数据的"统计惯性"编造旧版 API（如 TVM 案例中的 `PackedFunc`/`TVMArgs`/`TVM_FFI_REGISTER_GLOBAL` 8 类虚构 API，涉及 10 个文件），本质是"正确的知识用在错误的时间点"。
3. **头文件与实现文件对应关系断裂**：实现文件中存在但头文件中无声明的函数被当作公共接口。
4. **忽略模块依赖关系**：不读构建系统文件，错过可选组件、条件编译、模块裁剪信息。
5. **错误引用头文件版本**：对版本迁移期项目，依赖旧版头文件而非最新 `.h`。

## 触发场景

### 适用场景

- ✅ C/C++ 嵌入式或编译器项目，源码规模 >1000 文件
- ✅ 含头文件与实现文件分离（`.h`/`.hpp` 与 `.c`/`.cc`/`.cpp` 分目录）
- ✅ 需要从源码生成 API 文档 / Wiki / 教程 / 概念清单
- ✅ 项目处于版本迁移期（新旧 API 并存）
- ✅ 任何含头文件的 C++ 库（TuyaOpen、Apache TVM 已验证）

### 不适用场景（边界条件）

- ❌ 纯 Python/Markdown 项目（无头文件分层，Python 可直接以源码符号为权威）
- ❌ 单文件小工具/脚本（无声明与实现分离）
- ❌ 头文件自动生成的项目（如 protobuf 生成的 `.pb.h`，应以 `.proto` 源为权威）
- ❌ 闭源/无头文件访问的项目（无法执行头文件优先采集，改用文档分析）

## 核心做法

### 步骤1：R 阶段优先阅读头文件

优先阅读 `include/` 下的头文件，提取类声明、函数签名、枚举类型、宏定义。头文件是"公共 API 契约"，是事实采集的第一权威来源。

### 步骤2：实现文件仅用于验证

实现文件（`.c`/`.cc`）仅用于验证函数存在性和理解内部数据流，**不作为 API 声明的权威来源**。实现文件中可能存在静态函数、内部宏、未被头文件导出的符号。

### 步骤3：构建系统文件作为补充信息来源

构建系统文件（Kconfig/CMakeLists.txt）作为模块依赖关系和架构裁剪的补充信息来源——可识别可选组件、条件编译分支、模块之间的链接依赖，弥补头文件不表达的"编译期关系"。

### 步骤4：V 阶段在头文件中 Grep 验证

V 阶段对每个类名、宏名在 `include/` 中 Grep 验证，并检查命名空间前缀（如 `ffi::` vs 无命名空间）。对版本迁移期项目，以最新 `.h` 头文件为权威来源。

## 反模式（不要这么做）

### ❌ 反模式1：从实现文件提取 API 声明

从 `.c`/`.cc` 实现文件提取 API 声明。**后果**：提取到静态函数或内部宏，这些符号未在头文件中声明，读者无法从外部调用，文档即失效。

**正确做法**：API 声明只从头文件提取；实现文件仅用于"验证存在性"和"理解数据流"。

### ❌ 反模式2：不验证头文件与实现文件的对应关系

直接采信实现文件中的函数而不检查其是否在头文件中声明。**后果**：实现文件中存在但头文件中无声明的函数被当作公共接口，实际是内部实现细节。

**正确做法**：每个函数/类名必须能在头文件中 Grep 到对应声明，才算"公共 API"。

### ❌ 反模式3：忽视构建系统文件

不读 Kconfig/CMakeLists.txt。**后果**：错过模块依赖和可选组件信息，无法理解架构裁剪，文档中描述的功能可能在特定构建配置下不存在。

**正确做法**：将构建系统文件作为模块依赖关系和架构裁剪的补充信息来源，识别条件编译和可选组件。

### ❌ 反模式4：对版本迁移期项目依赖旧版头文件

使用旧版头文件作为权威来源。**后果**：文档描述的是已被废弃的 API，正是"版本迁移期统计惯性"虚构的温床。

**正确做法**：以最新 `.h` 头文件为权威，宏定义需区分已废弃宏与新 API。

## 检验标准

| 维度 | 检验点 |
|------|--------|
| 权威来源 | 文档中每个 API 声明都能在 `include/` 头文件中 Grep 到，且命名空间前缀正确 |
| 实现文件角色 | 实现文件仅用于验证存在性和理解数据流，未从中提取公共 API 声明 |
| 构建信息 | Kconfig/CMakeLists.txt 已作为模块依赖和架构裁剪的补充信息来源 |
| 版本正确性 | 版本迁移期项目引用的是最新头文件而非旧版 |
| 虚构率 | TVM 类项目虚构 API 率降至 0（Grep 验证零未命中） |

## 迁移示例

- **场景1（跨项目）**：学习另一个大型 C++ 库（如 Boost、Poco）时，R 阶段优先读 `include/`，V 阶段在头文件中 Grep 验证每个 API。
- **场景2（跨语言）**：C 项目（`.h` 声明 vs `.c` 定义）同样适用；Rust 项目可类比为"trait 定义与公开 API 面 vs 实现体"——公开 API 以 trait/公开函数签名为权威。
- **场景3（跨领域）**：非 C/C++ 但存在"契约/接口声明"与"内部实现"分离的场景（如 IDL/OpenAPI 规范 + 实现服务），声明文件优先采集、实现仅用于验证的思路同样成立。

## 与其他模式的关系

| 关系模式 | 关系类型 | 说明 |
|---------|---------|------|
| [vendor-high-level-doc-first-research.md](vendor-high-level-doc-first-research.md) | 前置互补 | 高层文档（AGENTS.md/README）建立全局框架；本模式提供"事实采集时以头文件为权威"的细则，两者可组合使用 |
| [open-source-repo-four-layer-identification.md](open-source-repo-four-layer-identification.md) | 前置互补 | 四层识别法回答"先读哪层"（规范层优先）；本模式回答"在实现层内部，头文件 vs 实现文件谁权威" |
| [source-pipeline-penetration-method.md](source-pipeline-penetration-method.md) | 互补 | 管线穿透法回答"顺着数据流学习"；本模式回答"API 声明的权威来源在哪" |
| [source-code-to-okf-wiki-workflow.md](../ai-collaboration/source-code-to-okf-wiki-workflow.md) | 宿主流程 | 本模式是 source-code-to-okf-wiki R 阶段在 C/C++ 项目上的专项细化 |
| [external-content-fact-verification.md](../ai-collaboration/external-content-fact-verification.md) | 方法论支撑 | V 阶段的头文件 Grep 验证是外部内容事实验证在源码场景的应用 |

---

*模式版本：v1.0 | 创建日期：2026-08-23 | maturity: L2（validation_count=2：Apache TVM + TuyaOpen，待更多 C/C++ 项目验证）*
