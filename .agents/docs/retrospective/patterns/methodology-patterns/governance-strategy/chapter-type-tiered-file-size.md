---
id: "chapter-type-tiered-file-size"
domain: "methodology"
layer: "governance"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "comprehensive"
source: "../../../reports/project-reports/retrospective-tvm-ffi-wiki-tutorial-20260705/insight-extraction.md#洞察1文件大小限制需要按章节类型分层"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/chapter-type-tiered-file-size.toml"
rules: []
references: []
skills: []
related_patterns:
  -   - "navigation-hub-filename-contract"
  -   - "atomization-three-criteria-test"
  -   - "cross-wiki-reference-directory-first"
---

# 章节类型分层文件大小策略

## 模式概述

在为 wiki 教程定义文件大小限制时，**必须按章节类型（概念型/API参考型/实战案例型/参考型）分层设置上限**，而非使用统一值。不同章节类型的信息密度表达式不同——概念型以文字为主（每行信息密度高），API 参考型以代码为主（每行信息密度低），统一的行数上限会导致 API 参考型章节超限或概念型章节内容不足。

## 问题背景

### 典型失败场景

在 TVM FFI Wiki 教程创建项目中，17 个文件中有 9 个（53%）超过 300 行上限，而之前的概念型教程（ffi-wiki、idl-wiki）的 300 行上限合规率接近 100%。同一规则在不同类型教程上产生了截然不同的合规结果。

### 数据对比

| 教程 | 类型 | 文件数 | >300行数量 | 合规率 |
|---|---|---|---|---|
| ffi-wiki | 概念型 | 8 | 0 | 100% |
| idl-wiki | 概念型 | 10 | 0 | 100% |
| tvm-ffi-wiki | API参考型 | 17 | 9 | 47% |

### 按章节类型的行数分布

| 章节类型 | 典型文件 | 自然行数范围 | 300 行上限 | 建议上限 |
|---|---|---|---|---|
| 概念型 | 概述、架构、对比分析 | 70-350 | 合理 | 300 |
| API参考型 | 核心 API、类型系统、容器 | 200-500 | 偏紧 | 500 |
| 实战案例型 | 完整示例、最佳实践 | 300-800 | 过紧 | 800 |
| 参考型 | FAQ、资源列表 | 200-600 | 偏紧 | 600 |

### 为什么统一上限不合理

1. **信息密度差异**：概念型章节每行是文字描述（高密度），API 参考型章节每行可能是单行代码声明（低密度）。300 行概念型文字可覆盖 5-8 个概念，300 行 API 参考型代码可能只覆盖 3-4 个 API
2. **代码块天然占行**：一个完整的 API 示例包括 C++ 声明（3-5 行）+ Python 调用（3-5 行）+ 注释（2-3 行），单个 API 平均 10-15 行。10 个 API 就是 100-150 行纯代码
3. **双语言负担**：vendor 教程要求 C++ 和 Python 双语言示例，代码行数翻倍

## 解决方案

### 分层大小限制表

| 章节类型 | 行数上限 | 识别特征 | 典型示例 |
|---|---|---|---|
| **概念型** | ≤ 300 行 | 以文字描述和 Mermaid 图为主，代码示例 ≤ 20% | 概述、架构设计、概念对比、发展趋势 |
| **API 参考型** | ≤ 500 行 | 以 API 声明和代码示例为主，代码示例 30-50% | 核心 API、类型系统、容器、序列化 |
| **实战案例型** | ≤ 800 行 | 以完整端到端示例为主，代码示例 ≥ 50% | 完整示例、最佳实践、项目集成 |
| **参考型** | ≤ 600 行 | 以条目列表和简短解答为主，代码示例 20-40% | FAQ、术语表、资源列表 |

### 操作步骤

```
步骤1：在 spec 中为每个章节标注章节类型（concept/api-reference/case-study/reference）
步骤2：在 checklist 中按章节类型分别检查文件大小
步骤3：超限时判断：是内容超限（需拆分）还是类型误判（需调整类型）
步骤4：内容超限时，优先考虑拆分为独立子章节，而非压缩内容
```

### Spec 模板字段

```yaml
## 章节规划
chapters:
  - file: "02-cpp-core-api.md"
    title: "C++ 核心 API"
    type: "api-reference"    # concept | api-reference | case-study | reference
    max_lines: 500
    description: "Any/Object/Function/Tensor 四大核心类型的 API 详解"
```

### 判断准则：何时拆分 vs 调整类型

| 场景 | 决策 | 理由 |
|---|---|---|
| 内容确实需要 500 行才能讲清楚，且无法拆分为独立子主题 | 调整类型（如 concept→api-reference） | 内容完整性优先 |
| 内容可拆分为 2 个独立子主题（如"Any 和 Object"+"Function 和 Tensor"） | 拆分为 2 个文件 | 原子化原则优先 |
| 内容混杂了概念说明和 API 参考 | 拆分为概念章 + API 参考章 | 单一职责原则 |

## 适用场景

- **触发条件**：创建包含 API 参考、实战案例或 FAQ 的 wiki 教程
- **不适用**：纯概念型教程（如 ffi-wiki、idl-wiki 的理论章节），300 行上限仍然合理

## 已知局限

1. **类型边界模糊**：部分章节可能同时包含概念说明和 API 参考（如"架构设计"章节中嵌入核心 API 介绍），此时按主体内容占比判断类型
2. **依赖章节类型标注的准确性**：如果 spec 中类型标注错误，分层限制也会失效
3. **不解决代码块质量**：行数限制不保证代码质量，仍需人工审查代码示例的正确性和完整性

## 成熟度评估

| 维度 | 评级 | 说明 |
|---|---|---|
| 验证次数 | 1 次（L1） | 仅在 TVM FFI Wiki 教程创建项目中通过事后验证确认了问题根因 |
| 复用次数 | 0 次（L1） | 尚未在其他 API 参考型教程中主动应用 |
| 文档完整度 | 综合级 | 包含问题背景、数据对比、分层表、操作步骤、判断准则、局限声明 |
| 升级路径 | 在后续 2 个 API 参考型教程中验证后升级至 L2 | 验证指标：各类型章节合规率 ≥ 90% |

## 模式溯源

- **来源复盘**：[retrospective-tvm-ffi-wiki-tutorial-20260705](../../../reports/project-reports/retrospective-tvm-ffi-wiki-tutorial-20260705/retrospective-report.md)
- **来源洞察**：[insight-extraction.md](../../../reports/project-reports/retrospective-tvm-ffi-wiki-tutorial-20260705/insight-extraction.md#洞察1文件大小限制需要按章节类型分层)
- **提取日期**：2026-07-05
- **提取者**：SpecWeave