---
id: "create-minit2i-wiki-tutorial"
title: "MiniT2I极简文生图模型Wiki教程生成"
theme: "retrospectives-insights"
status: "planning"
created: "2026-08-03"
source: "d:\\AI\\.trae\\specs\\retrospectives-insights\\analyze-minit2i-wechat-article\\"
---

# MiniT2I极简文生图模型Wiki教程生成 - Product Requirement Document

## Overview
- **Summary**: 将已完成的MiniT2I深度分析成果（13个中间分析文件+最终报告）重构整理为面向学习者的结构化Wiki教程。教程遵循项目现有Wiki标准格式（两位数字编号章节、TOML frontmatter、导航链接），输出到`docs/knowledge/learning/minit2i-minimalist-t2i-wiki/`目录，包含8个章节：概述与学习目标、核心设计哲学、技术路线三大减法、MM-JiT架构深度解析、实验结果与性能分析、局限性与开放问题、范式转移与方法论启示、总结FAQ与资源。
- **Purpose**: 将一次性的技术分析报告转化为可复用、可导航、适合系统学习的Wiki教程，帮助AI研究者和工程师理解MiniT2I的极简主义设计哲学、技术创新点，以及"减法哲学"对AI研究和工程实践的方法论启示。
- **Target Users**: AI研究者、计算机视觉从业者、生成式AI开发者、技术管理者、对AI模型架构创新和极简主义设计思想感兴趣的学习者。

## Goals
- 将分析工作区的13个中间文件重构为面向教学的8章Wiki结构
- 遵循项目现有Wiki的格式规范（编号、frontmatter、导航、Mermaid图表）
- 保持技术准确性：所有数据（FID、GFLOPs、参数量等）100%与原分析一致
- 设计适合学习的认知路径：从背景→哲学→技术→架构→数据→局限→洞察→总结
- 补充教学辅助元素：学习目标、前置知识、章节导航、Mermaid架构图、关键要点总结
- 生成可在docs站点中正常渲染的完整Wiki

## Non-Goals (Out of Scope)
- 不重新爬取或分析MiniT2I论文原文（基于已有分析成果）
- 不进行模型复现或补充实验
- 不更新原始分析工作区的文件（保留原analyze-minit2i-wechat-article目录不变）
- 不修改docs站点的全局配置或索引（仅生成Wiki内容）
- 不翻译为英文（保持中文）

## Background & Context
- **已有成果位置**：`d:\AI\.trae\specs\retrospectives-insights\analyze-minit2i-wechat-article\`
- **已有成果内容**：spec.md、tasks.md、checklist.md、raw-content.md、cleaned-content.md、structure-analysis.md、core-arguments.md、mm-jit-architecture.md、experiment-data.md、limitations.md、paradigm-insights.md、methodology-insights.md、wechat-article-analysis-minit2i-20260709.md（最终报告，515行）
- **Wiki标准位置**：`d:\AI\docs\knowledge\learning\`
- **参考Wiki示例**：
  - `ai-engineering-four-milestones-wiki/`（8章结构）
  - `github-cli-wiki/`（8章结构，含Mermaid架构图）
- **Wiki格式规范**：
  - 两位数字编号（00-overview.md, 01-xxx.md, ..., 07-xxx.md）
  - TOML frontmatter（id、title、source、date、category、tags）
  - 每章末尾有导航链接（←上一章 | 下一章→）
  - 00-overview包含章节导航表
  - 适当使用Mermaid流程图/架构图
  - 使用表格、引用块、要点列表增强可读性

## Functional Requirements
- **FR-1**: 创建Wiki目录 `docs/knowledge/learning/minit2i-minimalist-t2i-wiki/`
- **FR-2**: 生成00-overview.md：概述与学习目标，包含背景、核心主题、学习目标、前置知识、章节导航表、阅读路径建议
- **FR-3**: 生成01-design-philosophy.md：核心设计哲学，包含"每一步都做减法"的哲学、质疑默认前提、减法即加法、如无必要勿增实体、基线先于优化
- **FR-4**: 生成02-three-subtractions.md：技术路线三大减法，包含无VAE像素直出、无AdaLN朴素Transformer、无私有数据两阶段训练
- **FR-5**: 生成03-mm-jit-architecture.md：MM-JiT架构深度解析，包含MM-DiT vs MM-JiT对比、两层文本适配器、删除AdaLN的依据、关键洞察"噪声图像携带时间步信息"、架构简化量化收益
- **FR-6**: 生成04-experiments-performance.md：实验结果与性能分析，包含模型规格、计算量对比、GenEval/DPG-Bench/PRISM-Bench结果、训练成本、消融实验结论、与SD3综合对比
- **FR-7**: 生成05-limitations-open-problems.md：局限性与开放问题，包含patch伪影、CFG副作用、分辨率天花板、数据瓶颈、科学态度分析
- **FR-8**: 生成06-paradigm-shift-insights.md：范式转移与方法论启示，包含堆料→提纯、研究门槛降低（AlexNet时刻）、LLM范式迁移、减法哲学、何恺明团队研究风格、对研究者/工程师的建议
- **FR-9**: 生成07-summary-faq-resources.md：总结、FAQ与资源，包含10条关键要点、常见问题解答、参考资料链接、术语表
- **FR-10**: 每个章节包含TOML frontmatter、章节导航、适当的Mermaid图表（架构图、技术路线图、对比表）

## Non-Functional Requirements
- **NFR-1**: 技术准确性：所有数据指标（258M参数、570 GFLOPs、FID 13.7、GenEval 0.87、8张H100 3天等）必须与原分析报告完全一致
- **NFR-2**: 结构一致性：遵循项目现有Wiki的格式规范，包括编号、frontmatter字段、导航链接格式
- **NFR-3**: 学习友好：语言通俗易懂，避免过度学术化，前置知识明确，章节间逻辑递进
- **NFR-4**: 可读性：使用表格、列表、引用块、Mermaid图表增强视觉呈现，避免大段纯文字
- **NFR-5**: 完整性：覆盖原分析报告的所有核心内容（11个章节），无关键信息遗漏

## Constraints
- **Technical**: 基于已有的分析内容进行重构整理，不新增外部信息；Markdown格式，兼容MkDocs渲染
- **Business**: 输出为中文；教程为学习研究用途
- **Dependencies**: 依赖`analyze-minit2i-wechat-article`目录下已完成的分析成果

## Assumptions
- 原分析报告中的技术数据和观点是准确完整的
- Wiki目录结构和格式与参考示例（ai-engineering-four-milestones-wiki、github-cli-wiki）保持一致即可
- 不需要运行MkDocs本地预览，生成Markdown文件即可
- 不需要更新docs站点全局索引（后续可单独处理）

## Acceptance Criteria

### AC-1: Wiki目录和文件结构正确
- **Given**: 已有完整的MiniT2I分析成果
- **When**: 生成Wiki教程
- **Then**: 在`docs/knowledge/learning/minit2i-minimalist-t2i-wiki/`下生成8个Markdown文件（00-07），文件名遵循两位数字编号规范
- **Verification**: `programmatic`

### AC-2: 00-overview内容完整规范
- **Given**: Wiki目录已创建
- **When**: 查看00-overview.md
- **Then**: 包含背景介绍、核心主题、学习目标（5条）、前置知识、章节导航表（8章完整链接）、阅读路径建议，且有正确的TOML frontmatter
- **Verification**: `human-judgment`

### AC-3: 技术数据100%准确
- **Given**: 所有章节已生成
- **When**: 核对关键数据点
- **Then**: 以下数据与原报告完全一致：
  - MiniT2I-B/16去噪器258M参数，总参数~600M
  - 单步GFLOPs：1379→570（降低58.7%）
  - AdaLN移除后：层数12→17层，FID 18.7→13.7
  - GenEval 0.87，DPG-Bench 84.2
  - B/32在8张H100训练约3天
  - patch边界梯度高17-22%
  - L/16为912M参数，SD3-Medium约2B参数
- **Verification**: `programmatic`

### AC-4: 核心技术内容无遗漏
- **Given**: 所有章节已生成
- **When**: 对照原分析报告11个章节
- **Then**: 以下主题全部覆盖：三大减法设计、MM-JiT两个核心设计、噪声图像携带时间步信息、四个局限性、范式转移五个洞察、何恺明团队研究风格、七条方法论建议
- **Verification**: `human-judgment`

### AC-5: 格式规范符合项目标准
- **Given**: 所有章节已生成
- **When**: 检查格式规范
- **Then**: 
  - 每个文件有正确的TOML frontmatter（id、title、source、date、category、tags）
  - 每个章节末尾有导航链接（←上一章 | 下一章→）
  - 00-overview有完整章节导航表
  - 至少包含2个Mermaid图表（架构对比图、技术路线图）
  - 使用表格呈现对比数据
- **Verification**: `programmatic` + `human-judgment`

### AC-6: 学习路径逻辑清晰
- **Given**: 所有章节已生成
- **When**: 按顺序阅读8个章节
- **Then**: 认知路径为"背景→哲学→技术减法→架构→数据→局限→洞察→总结"，逻辑递进自然，前置知识明确
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要生成Wiki索引页（minit2i-minimalist-t2i-wiki.md）放在learning目录下？
- [ ] 是否需要补充更多Mermaid图表（如训练流程图、范式转移对比图）？
