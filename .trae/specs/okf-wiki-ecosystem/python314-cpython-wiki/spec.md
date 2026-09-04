---
status: "draft"
id: python314-cpython-wiki-spec
title: "Python 3.14 + CPython 源码深度 Wiki 教程 — 产品需求文档"
date: "2026-08-19"
category: "learning"
source: "https://docs.python.org/zh-cn/3.14/, https://docs.python.org/3.14/whatsnew/3.14.html, https://github.com/python/cpython (tag: v3.14.0)"
tags: ["python314", "cpython", "free-threading", "jit", "t-strings", "wiki", "tutorial"]
---

# Python 3.14 + CPython 源码深度 Wiki 教程 — 产品需求文档

## Overview

- **Summary**: 基于 Python 3.14 官方文档（中文/英文）和 CPython 源码（GitHub tag v3.14.0），生成一套系统化的中文 Wiki 教程，覆盖 Python 3.14 全部核心新特性、CPython 源码架构深度解析，以及从应用开发者到 C 扩展作者的完整迁移路径。源码引用使用 CPython 源码树内相对路径（如 `Python/ceval.c`），并提供 GitHub 链接。
- **Purpose**: Python 3.14 是自 Python 3.0 以来最具变革性的版本——自由线程（无GIL）正式支持、Copy-and-Patch JIT、t-strings 模板字符串、延迟注解求值、多解释器、Zstandard 压缩等重磅特性同时落地。同时 CPython 内部架构经历了 Tier 2 优化器、QSBR 无锁回收、mimalloc 集成等深层重构。目前中文社区缺乏一份同时覆盖"用户级新特性"和"源码级实现原理"的系统教程，本 Wiki 填补这一空白。
- **Target Users**:
  - **应用开发者**: 了解 Python 3.14 新语法/新模块/性能改进，掌握迁移要点
  - **库作者/C 扩展开发者**: 理解 C API 变更、自由线程兼容性、Limited API 改动
  - **源码学习者/贡献者**: 理解 CPython 内部架构（解释器循环、JIT、GC、对象系统）
  - **技术决策者**: 评估升级成本与收益、了解自由线程/JIT 成熟度

## Goals

- G1: 完整覆盖 Python 3.14 所有 PEP 级新特性（PEP 649/749、703/779、734、750、758、765、768、741、776、784、761、744）
- G2: 每个语言/库特性配有可运行的代码示例和源码引用（CPython 源码树相对路径 + GitHub 链接，格式为 `[Python/ceval.c](https://github.com/python/cpython/blob/v3.14.0/Python/ceval.c)`）
- G3: CPython 源码架构章节覆盖核心运行时（解释器循环、编译器、GC、对象系统、内存管理）
- G4: 自由线程和 JIT 两大核心架构变更有深度原理解析（含 QSBR、BRC、mimalloc、copy-and-patch JIT、Tier 2 uop 优化器）
- G5: 提供完整的迁移指南（废弃/移除 API 对照、C API 变更迁移、自由线程兼容性检查清单）
- G6: Wiki 格式遵循项目现有 wiki 规范（frontmatter、章节编号、mermaid 图表、章节导航）

## Non-Goals

- NG1: 不覆盖 Python 基础语法教学（假设读者已有 Python 3.10+ 基础）
- NG2: 不逐行翻译官方文档（重点是系统化梳理、源码对照、迁移指导、中文语境下的补充说明）
- NG3: 不覆盖 3.15/3.16 开发中特性（仅在必要时标注"3.14 中可用的版本"）
- NG4: 不构建 CPython 编译指南（仅引用源码结构，不做构建教程）
- NG5: 不生成 PDF/DOCX 导出（纯 Markdown Wiki）

## Background & Context

- **源码参考**: CPython 官方仓库 https://github.com/python/cpython ，基于 v3.14.0 tag；本地工作区如有源码检出可交叉验证
- **官方文档**: https://docs.python.org/zh-cn/3.14/（中文版）和 https://docs.python.org/3.14/（英文版）
- **发布日期**: Python 3.14 于 2025 年 10 月 7 日正式发布
- **现有 Wiki 模板**: 项目已有多个成熟 Wiki（agency-agents-wiki、deepseek-harness-wiki、okf-kit-wiki 等），采用编号章节（00-overview.md 开始）+ frontmatter + mermaid 架构图 + 章节导航的格式
- **输出目录**: `docs/knowledge/learning/python314-cpython-wiki/`

## Functional Requirements

- **FR-1**: 教程共 13 章（00-12），涵盖概述、语言新特性、执行模型变革、新模块、标准库改进、CPython源码架构、C API、构建系统、迁移指南、实战示例、FAQ、最佳实践、总结资源
- **FR-2**: 每个章节使用 YAML frontmatter（id、title、source、date、category、tags）
- **FR-3**: 代码示例必须可运行（标注 Python 版本要求，自由线程特性标注 `PYTHON_GIL=0` 或 `t` suffix 构建要求）
- **FR-4**: 涉及 CPython 源码的部分必须提供源码树相对路径引用，并附 GitHub v3.14.0 tag 链接（格式：`[目录/文件](https://github.com/python/cpython/blob/v3.14.0/目录/文件)`）
- **FR-5**: 架构/流程相关内容使用 mermaid 图表可视化
- **FR-6**: 每章末尾包含"上一章/下一章"导航链接
- **FR-7**: 00-overview 包含章节导航表、目标受众矩阵、核心特性对比表、版本信息表
- **FR-8**: 自由线程章节必须覆盖：启用方式、单线程开销数据、线程安全模型、关键区段、QSBR/BRC 原理、扩展兼容性、已知限制
- **FR-9**: JIT 章节必须覆盖：启用方式（PYTHON_JIT=1）、copy-and-patch 原理、Tier 1/Tier 2 架构、trace 记录、uop 优化器、stencil 生成、限制说明
- **FR-10**: t-strings 章节必须覆盖：语法、与 f-strings 对比、Template/Interpolation 对象模型、安全使用场景（SQL/HTML/Shell）、源码引用
- **FR-11**: 延迟注解章节必须覆盖：PEP 649/749 核心变化、annotationlib 模块三种 Format、from __future__ import annotations 弃用路径、迁移示例
- **FR-12**: 多解释器章节必须覆盖：concurrent.interpreters 模块、InterpreterPoolExecutor、CSP/Actor 模型、与 multiprocessing 对比、对象共享限制
- **FR-13**: 源码架构章节必须覆盖：顶层目录结构、三层头文件体系、解释器循环（ceval.c/ceval_gil.c）、字节码编译、对象系统、GC（GIL/FT 双模式）、内存分配（pymalloc/mimalloc）、PEG 解析器
- **FR-14**: 迁移指南必须包含：废弃 API 对照表、移除 API 替代方案、C API 变更清单、字节码变更摘要、平台支持变化、已知问题规避

## Non-Functional Requirements

- **NFR-1**: 内容准确性 — 所有特性描述必须可在官方文档或本地源码中验证，不编造 API 或行为
- **NFR-2**: 中文表达 — 全文使用中文，技术术语保留英文原文并附首次出现时的中文解释
- **NFR-3**: 原子化章节 — 每章 2000-5000 字，单一主题，避免跨章节强耦合
- **NFR-4**: 源码引用规范 — C 源码引用使用 CPython 源码树相对路径 + GitHub 链接，格式为 `[目录/文件](https://github.com/python/cpython/blob/v3.14.0/目录/文件#Lstart-Lend)`；不硬编码本地绝对路径
- **NFR-5**: 代码示例规范 — Python 代码使用 `python` 语言标记，C 代码使用 `c`，Shell 命令使用 `bash`
- **NFR-6**: 七概念方法论 — Wiki 生成过程遵循 R→I→E→V→C 知识沉淀链路，产出 seven-concepts-report.md

## Constraints

- **Technical**:
  - 输出格式为 Markdown（.md），不生成 HTML/PDF
  - 使用项目现有 Wiki 格式约定（编号 00-12、frontmatter、mermaid、章节导航）
  - 源码引用路径必须对应 CPython v3.14.0 源码树中的实际存在文件（相对路径）
  - mermaid 图表必须使用项目支持的语法（graph TB/TD/LR、flowchart、classDiagram 等）
- **Business**:
  - 中文内容面向中文 Python 开发者社区
  - 不包含版权受限内容（官方文档为 PSF 许可证，可引用并注明来源）
- **Dependencies**:
  - CPython v3.14.0 源码可通过 GitHub 访问（如有本地检出可交叉验证）
  - 官方 Python 3.14 文档可访问

## Assumptions

- 读者具备 Python 3.10+ 编程基础，了解基本的类型注解、asyncio、C 扩展概念
- CPython v3.14.0 tag 包含 Python 3.14 的所有稳定特性实现
- 输出目录 `docs/knowledge/learning/python314-cpython-wiki/` 不需要预先创建

## Acceptance Criteria

### AC-1: Wiki 结构完整性
- **Type**: `rule`
- **Given**: Wiki 教程已生成
- **When**: 检查输出目录
- **Then**: 包含 13 个编号章节文件（00-overview.md 至 12-summary-resources.md）+ seven-concepts-report.md
- **Pass Condition**: 所有 14 个文件存在且非空，每章有正确的 frontmatter
- **Evidence**: 文件列表 + 每章 frontmatter 检查

### AC-2: 内容覆盖完整性
- **Type**: `rule`
- **Given**: Wiki 教程已生成
- **When**: 逐章检查内容
- **Then**: 覆盖 FR-1 列出的所有主题（12+ PEP、源码架构、迁移指南、实战示例）
- **Pass Condition**: 每个 PEP 有独立章节或子章节；源码架构覆盖 FR-13 列出的所有子系统；迁移指南覆盖 FR-14 列出的所有变更类别
- **Evidence**: 章节内容审查 + PEP 覆盖清单

### AC-3: 源码引用有效性
- **Type**: `rule`
- **Given**: Wiki 中的源码引用
- **When**: 检查源码链接
- **Then**: 所有引用的源码文件路径对应 CPython v3.14.0 源码树中的真实文件（相对路径），GitHub 链接可访问
- **Pass Condition**: 无断链引用（GitHub 链接可达、相对路径与源码树结构一致）
- **Evidence**: GitHub 链接验证 + 源码树结构对照检查

### AC-4: 代码示例质量
- **Type**: `rubric`
- **Dimension**: 代码示例的可运行性、教育价值和与主题的相关性
- **Scale**: 1-5
- **Anchors**:
  - 1 = 代码示例缺失或与主题无关
  - 3 = 代码示例基本可运行但缺乏注释或输出说明
  - 5 = 每个代码示例有清晰注释、预期输出说明、版本要求标注，且示例循序渐进
- **Pass Threshold**: >= 4
- **Evidence**: 逐章代码示例审查

### AC-5: 架构可视化质量
- **Type**: `rubric`
- **Dimension**: mermaid 图表的清晰度、准确性和信息密度
- **Scale**: 1-5
- **Anchors**:
  - 1 = 无 mermaid 图表或图表错误无法渲染
  - 3 = 有基本架构图但不够完整或标注不清
  - 5 = 架构图准确反映 CPython 内部结构，有清晰的子图分组和颜色标注，文字精炼
- **Pass Threshold**: >= 4
- **Evidence**: mermaid 语法检查 + 视觉审查

### AC-6: 格式规范合规性
- **Type**: `rule`
- **Given**: 所有 Wiki 文件
- **When**: 检查格式
- **Then**: 符合项目 Wiki 格式规范（frontmatter、章节编号、导航链接、标题层级）
- **Pass Condition**: 每章有正确 frontmatter（id/title/source/date/category/tags）；章节编号连续（00-12）；每章有上下章导航；标题层级不跳级
- **Evidence**: 格式审查清单

### AC-7: 迁移指南实用性
- **Type**: `rubric`
- **Dimension**: 迁移指南对实际升级工作的指导价值
- **Scale**: 1-5
- **Anchors**:
  - 1 = 仅列出"有变更"无具体指导
  - 3 = 有 before/after 代码对比但不够全面
  - 5 = 包含完整 API 映射表、常见陷阱、C 扩展适配步骤、自由线程兼容性检查清单
- **Pass Threshold**: >= 4
- **Evidence**: 迁移章节内容审查

## Open Questions

- [ ] 是否需要包含 Python 3.14 安装/构建指南章节？（当前 NG4 排除）
- [ ] 自由线程实战示例是否需要多线程性能基准测试代码？
- [ ] 是否需要与 Python 3.13 的逐项对比（what's new 之外的迁移视角）？
