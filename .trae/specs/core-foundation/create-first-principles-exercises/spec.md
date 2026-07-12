# 第一性原理思维训练题库 - Product Requirement Document

## Overview
- **Summary**: 基于[08-methodology-framework.md](../../../../docs/knowledge/learning/first-principles/08-methodology-framework.md)定义的六步操作流程，在`docs/knowledge/learning/first-principles/`目录下创建系统化的思维训练题库，包含分层级练习题、案例分析、参考答案与解析，帮助读者通过刻意练习掌握第一性原理思维方法。
- **Purpose**: 将理论框架转化为可实践的训练材料，解决"看懂了但不会用"的问题。通过循序渐进的练习设计，让读者能够从识别概念开始，逐步掌握拆解、质疑、重构、验证的完整思维流程。
- **Target Users**: 第一性原理学习者（包括技术背景、商业背景、方法论研究者等不同背景读者），已阅读过08-methodology-framework.md希望通过练习巩固的实践者。

## Goals
- 基于六步方法论框架设计分层级练习题（入门/进阶/挑战）
- 覆盖六步流程的每一步骤专项训练与综合案例分析
- 提供详细的参考答案与解析，包含常见误区提示
- 建立练习题与知识库现有文档的交叉引用
- 在README.md中新增训练题库导航入口
- 遵循现有文档格式规范（YAML frontmatter、可信度标注、偏差提示）

## Non-Goals (Out of Scope)
- 不创建交互式Web应用或在线答题系统（仅Markdown静态文档）
- 不开发自动化评分或AI判题功能
- 不新增第一性原理理论内容（仅基于现有08-methodology-framework.md框架出题）
- 不覆盖物理/DFT等专业领域的深度技术习题（保持跨领域通用性）
- 不翻译为英文（仅中文版本）

## Background & Context
- 现有第一性原理知识库已完成12个核心文件，包含完整的哲学起源、物理应用、商业案例、方法论框架
- [08-methodology-framework.md](../../../../docs/knowledge/learning/first-principles/08-methodology-framework.md)提供了六步操作流程、7个常见误区、实践检查清单，但缺乏配套练习材料
- 这是复盘项目ACT-012行动项（中优先级），目标是帮助读者刻意练习而非仅停留在概念理解
- 现有文档已建立可信度评级、偏差标注、对抗性审查等质量机制，练习题需延续这些规范
- 相关可参考模式：[00-adversarial-review-protocol.md](../../../../docs/knowledge/learning/first-principles/00-adversarial-review-protocol.md)的审查标准

## Functional Requirements
- **FR-1**: 创建12-exercises.md主文件，包含题库说明、难度分级说明、使用指南
- **FR-2**: 按六步流程设计专项练习题：
  - Step 1 问题定义：至少5道题（3入门+1进阶+1挑战）
  - Step 2 假设列举：至少5道题（3入门+1进阶+1挑战）
  - Step 3 拆解至基本要素：至少5道题（3入门+1进阶+1挑战）
  - Step 4 质疑与验证：至少5道题（3入门+1进阶+1挑战）
  - Step 5 重新构建：至少4道题（2入门+1进阶+1挑战）
  - Step 6 验证与迭代：至少4道题（2入门+1进阶+1挑战）
- **FR-3**: 设计3个综合案例分析，覆盖不同领域（1日常生活/1工程技术/1商业创新），要求完整应用六步流程
- **FR-4**: 每道题目包含：难度标记、场景描述、具体任务、预期产出格式、对应框架章节链接
- **FR-5**: 所有题目提供参考答案要点（非唯一标准答案），包含：
  - 常见错误/误区分析
  - 思考路径提示
  - 关键检查点
  - 可信度标注（如涉及事实判断）
- **FR-6**: 设计7个误区识别专项练习，对应08框架第4章的7个常见误区
- **FR-7**: 提供练习进度追踪表（可勾选的检查清单格式）
- **FR-8**: 所有文件遵循现有frontmatter规范（YAML格式，id/title/source/created_at等字段）
- **FR-9**: 在[README.md](../../../../docs/knowledge/learning/first-principles/)的文件导航表中新增练习题入口
- **FR-10**: 练习题中引用现有知识库内容时使用正确的file:///链接格式

## Non-Functional Requirements
- **NFR-1**: 题目场景应贴近现实，避免过于抽象或学术化的假问题
- **NFR-2**: 入门级题目应明确指引使用框架中的具体工具（如"连续问5个为什么"、"列出至少10个假设"）
- **NFR-3**: 参考答案应诚实标注"参考答案要点，非唯一正确解"，鼓励独立思考
- **NFR-4**: 涉及商业案例时必须保持批判性视角，沿用现有偏差提示传统，避免事后归因
- **NFR-5**: 文档组织清晰，使用折叠区块（<details>）隐藏答案，方便读者先独立思考再查看
- **NFR-6**: 文件命名遵循kebab-case规范，纯英文文件名（12-exercises.md）
- **NFR-7**: 总题量控制在30-40题之间（含专项+综合+误区），避免过多导致学习门槛过高

## Constraints
- **Technical**: 仅使用Markdown格式，不依赖外部工具或脚本；使用<details>HTML标签实现答案折叠
- **Business**: 中优先级任务，预计工作量"中"
- **Dependencies**: 依赖现有08-methodology-framework.md的六步框架结构

## Assumptions
- 读者已阅读或正在阅读08-methodology-framework.md，了解六步流程基本概念
- Markdown渲染环境支持<details>标签（GitHub、VS Code预览、大多数现代Markdown编辑器均支持）
- 题目设计不需要专业领域知识即可理解和尝试（通用思维训练）
- 现有README.md的文件导航表结构保持稳定，按现有序号模式新增序号12

## Acceptance Criteria

### AC-1: 文件结构与格式合规
- **Given**: 任务完成
- **When**: 检查docs/knowledge/learning/first-principles/目录
- **Then**: 存在12-exercises.md文件，使用正确YAML frontmatter，文件名为纯英文kebab-case
- **Verification**: `programmatic`
- **Notes**: 运行文件名规范检查脚本验证

### AC-2: 六步专项练习覆盖完整
- **Given**: 12-exercises.md已创建
- **When**: 统计各步骤题目数量
- **Then**: Step1-4每步至少5题，Step5-6每步至少4题，总计至少28道专项练习题，每道题有难度标记
- **Verification**: `programmatic`

### AC-3: 综合案例与误区练习完整
- **Given**: 12-exercises.md已创建
- **When**: 检查综合案例和误区识别部分
- **Then**: 包含至少3个跨领域综合案例分析，包含7个误区识别专项练习
- **Verification**: `human-judgment`

### AC-4: 参考答案质量达标
- **Given**: 每道题目
- **When**: 查看答案部分
- **Then**: 所有题目有参考答案要点，包含常见误区分析，使用<details>标签折叠隐藏，明确标注"参考答案要点，非唯一正确解"
- **Verification**: `human-judgment`

### AC-5: README导航更新
- **Given**: 任务完成
- **When**: 查看README.md文件导航表
- **Then**: 文件导航表中包含序号12的12-exercises.md条目，链接正确，有难度等级和阅读顺序建议
- **Verification**: `programmatic`

### AC-6: 交叉引用与链接有效
- **Given**: 任务完成
- **When**: 运行链接检查脚本
- **Then**: 所有内部file:///链接有效，无断链
- **Verification**: `programmatic`

### AC-7: 延续现有质量规范
- **Given**: 12-exercises.md已创建
- **When**: 审查内容风格
- **Then**: 延续现有文档的批判性视角，涉及商业案例时有偏差提示，不做"第一性原理万能"的宣称，保持框架中关于适用边界的审慎态度
- **Verification**: `human-judgment`

### AC-8: 练习进度追踪功能
- **Given**: 12-exercises.md已创建
- **When**: 查看文档结构
- **Then**: 包含可勾选的练习进度追踪表，方便读者标记完成状态
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要为不同背景读者（技术/商业/哲学）设计分轨练习路径？（建议：v1版本不做分轨，综合题目标注适合领域即可）
- [ ] 答案是否需要提供不同难度层级的解析（基础版vs深度版）？（建议：v1版本提供统一的参考答案要点）
