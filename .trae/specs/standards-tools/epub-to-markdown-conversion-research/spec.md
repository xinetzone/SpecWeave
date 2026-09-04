---
status: "draft"
id: "epub-to-markdown-conversion-research"
title: "EPUB 转 Markdown 转换方案系统性调研"
source: "user request"
date: "2026-08-19"
type: "spec"
theme: "standards-tools"
change-id: "epub-to-markdown-conversion-research"
---

# EPUB 转 Markdown 转换方案调研 Spec

## Why
用户需要将 EPUB 格式电子书转换为 Markdown 以便于在 AI 智能体、文档工作流中复用，但当前缺乏对主流转换工具（pandoc、calibre 等）的系统性横向对比与场景化选型依据。存在调研空白，需形成一份详尽的对比分析报告，明确推荐方案、适用场景与具体操作步骤，避免盲目选型导致复杂元素（图片/表格/公式/代码块/目录/样式）丢失或性能/兼容性问题。

## What Changes
- 系统调研主流 EPUB→Markdown 转换工具的功能特性、转换质量、兼容性、使用方法与优缺点
- 对比各工具对 EPUB 复杂元素（图片、表格、公式、代码块、目录结构、样式格式）的处理能力
- 归纳转换过程中的常见问题与解决方案
- 评估各工具性能表现（转换速度、资源占用）
- 调研基于 Python 等语言的编程实现方案（自行开发转换脚本的可行性）
- 产出结构化对比分析报告，给出推荐方案与适用场景矩阵、具体操作步骤或实现思路

## Impact
- Affected specs: 无既有 spec 直接影响（属于新增调研任务）
- Affected code: 无生产代码变更；产出物为调研报告（Markdown），存放于 `docs/knowledge/` 下

## 内容敏感度
- 级别：**公开（Public）** —— 研究对象为开源工具/官方文档/公开文章，无访问控制
- 工作流：标准 Spec Mode，产出报告最终落位 `docs/` 对应目录

## 方法论编排（seven-concepts-cmd）
- 场景：场景4 知识沉淀（R→I→E→V→C），因涉及方案选型与创新结论，编排完整链路
- 链路：R（事实采集：各工具客观规格与实测数据）→ I（洞察：能力差异根因与选型关键因子）→ E（萃取：推荐方案与适用场景模式）→ V（对抗审查：多视角攻击推荐结论）→ C（原子交付：报告入库）
- 质量门：G1（事实无因果词）、G2（洞察四元组）、G3（模式可迁移）、V门（审查意见≥5条、采纳≥2条）

## ADDED Requirements

### Requirement: 主流工具功能特性调研
系统 SHALL 调研 pandoc、calibre（ebook-convert）、以及不少于 2 个其他主流工具（如 mupdf、wheezy.template 生态、pypandoc、ebooklib 等）的功能特性。

#### Scenario: 覆盖主要工具
- **WHEN** 调研完成
- **THEN** 报告中包含各工具的：核心功能、输入输出格式支持、配置灵活性、维护活跃度、跨平台（Windows/Linux/macOS）支持情况

### Requirement: 复杂元素处理能力对比
报告 SHALL 逐项对比各工具对 EPUB 复杂元素（图片、表格、公式、代码块、目录结构、样式格式）的保真处理能力，并给出可实测的样例验证结论。

#### Scenario: 复杂元素验收
- **WHEN** 使用代表性 EPUB 样例（含公式、表格、代码块、多级目录、图片、富样式）逐工具实测
- **THEN** 报告中展示每种元素在各工具下的保留/丢失情况，明确标注 DOCX/MathML/LaTeX、表格对齐、图片外链与本地化等处理细节

### Requirement: 常见问题与解决方案
报告 SHALL 归纳转换过程中的常见问题（乱码、样式丢失、链接失效、公式渲染失败、超大文件性能劣化、CJK 排版错乱等）及对应解决方案。

#### Scenario: 问题方案可用
- **WHEN** 报告评审
- **THEN** 每个问题至少给出 1 条可复现的解决方案，并说明触发条件与适用工具

### Requirement: 性能对比
报告 SHALL 对主要工具进行转换性能对比（转换耗时、峰值内存、文件体积增长），并提供测试方法与结果数据。

#### Scenario: 性能数据可溯
- **WHEN** 性能测试完成
- **THEN** 性能数据带测试环境、样本规模、命令与耗时/内存记录，可复现

### Requirement: 编程实现方案评估
报告 SHALL 评估基于 Python 自行开发转换脚本的可行性（如使用 ebooklib + 自定义 XHTML→Markdown 转换、pypandoc、BeautifulSoup/htmldom 方案），给出实现思路、代码骨架示意、优缺点与适用边界。

#### Scenario: 自研方案可行
- **WHEN** 评审自研方案章节
- **THEN** 包含实现思路、最小代码骨架、依赖清单、与成熟工具方案的成本/收益对比及选型建议

### Requirement: 推荐方案与适用场景矩阵
报告 SHALL 给出明确的推荐方案，并形成「工具 × 典型场景」适用矩阵，覆盖普通文本书、技术/代码书、含大量公式的学术书、图片密集型画册、批量处理等场景。

#### Scenario: 推荐与矩阵可用
- **WHEN** 报告评审
- **THEN** 每个典型场景明确推荐工具、理由、操作步骤（命令/代码）与注意事项

## MODIFIED Requirements
无（新增调研任务）

## REMOVED Requirements
无