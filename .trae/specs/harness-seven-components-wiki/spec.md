---
id: "harness-seven-components-wiki"
title: "Harness业务运行底座七组件Wiki教程"
theme: "knowledge-learning"
status: "planning"
created: "2026-07-13"
source: "https://mp.weixin.qq.com/s/IOBCNtztxpinWrYW_AtYew?from=industrynews&color_scheme=light#rd"
source_author: "王戴明"
category: "02-agent-engineering-methodology"
---

# Harness业务运行底座七组件Wiki教程 - Product Requirement Document

## Overview
- **Summary**: 基于王戴明发布的微信公众号文章《2026年Agent领域最重要的创新：Harness》，创建一份结构清晰、内容详实的wiki教程。文章提出Harness是AI Agent的业务运行底座，由模型网关、工具注册表、知识库引擎、记忆系统、策略引擎、可观测性、配置管理七大核心组件构成，通过"家庭聚餐"生活场景类比和"文章Agent"实战案例系统阐述。本教程将文章内容进行体系化重构，形成适合不同知识水平读者学习的完整wiki。
- **Purpose**: 帮助读者系统理解Harness七大组件的定义、相互关系、设计原则与实践方法，将一篇微信文章转化为可反复查阅、逐层深入的结构化学习资源，降低Harness概念的学习门槛，指导产品经理和开发者在真实业务中构建可控的Agent系统。
- **Target Users**: AI产品经理、AI应用开发者、技术管理者、对Agent工程化感兴趣的学习者（覆盖从入门到进阶不同水平）。

## Goals
- 系统阐述Harness七大组件的理论定义、核心职责与设计原则
- 通过"家庭聚餐"类比和"文章Agent"案例将抽象概念具象化
- 提供可操作的实践指南：组件选型要点、实施步骤、注意事项
- 深度剖析文章Agent案例，展示七大组件如何协同工作
- 预判学习过程中的常见疑问并给出清晰解答
- 建立与现有harness-engineering-wiki的知识关联，形成互补
- 遵循项目wiki原子化结构规范，输出层级化的多文件教程

## Non-Goals (Out of Scope)
- 不复刻或替代已有的harness-engineering-wiki（涅羽/阿里技术版，聚焦三代范式/四条铁律/六大模式）
- 不进行Harness相关开源框架（如LangGraph、CrewAI等）的代码级实现教程
- 不超出原文范围进行无依据的技术推演或框架对比
- 不生成可运行的代码原型或工程脚手架
- 不涉及特定云厂商或商业产品的评测推荐

## Background & Context
- **文章来源**：微信公众号，作者王戴明
- **发布时间**：2026年
- **核心论点**：大模型只能解决智能问题，Harness才能解决交付问题；LLM是聪明的大脑，Harness是让大脑能干活的工作系统
- **核心类比**：家庭聚餐安排（私人助理+工具+知识+记忆+规则+记录+配置）
- **贯穿案例**：文章Agent（帮作者稳定写出好文章的Agent系统）
- **现有资产**：项目中已有harness-engineering-wiki（基于阿里技术涅羽文章），聚焦三代工程范式演进、四条铁律、六大模式、悟空招聘案例，本教程与其形成互补——前者侧重工程范式与模式语言，本教程侧重业务运行底座的组件架构与产品视角
- **wiki目录位置**：docs/knowledge/learning/02-agent-engineering-methodology/ 下新建 harness-seven-components-wiki/
- **wiki结构规范**：遵循项目现有wiki原子化规范（00-overview.md、01-xx.md、...、README.md索引），使用YAML frontmatter，Mermaid图表，相对路径交叉引用

## Functional Requirements
- **FR-1**: 理论概述——详细解释Harness的定义定位、七大组件各自的定义/核心职责/4个基础要素/层级归属，以及组件间的依赖关系与协作流程
- **FR-2**: 组件详解——对每个组件（模型网关、工具注册表、知识库引擎、记忆系统、策略引擎、可观测性、配置管理）进行独立章节深度讲解，包含：核心概念、生活场景类比、文章Agent中的具体应用、设计原则、常见误区
- **FR-3**: 实践指南——提供从0到1构建Harness的操作步骤，包含：组件选型决策、实施优先级排序、最小可行Harness构建路径、各组件落地注意事项
- **FR-4**: 案例分析——以"文章Agent"为主线案例进行深度剖析，展示七大组件如何在一个具体业务场景中协同工作；补充"家庭聚餐"类比与真实Agent的映射关系
- **FR-5**: 常见问题解答——预判并解答至少12个学习过程中的常见疑问，覆盖概念混淆、实施难点、边界判断、与现有知识的关系等
- **FR-6**: 图表说明——使用Mermaid绘制组件架构图、组件协作流程图、模型选择决策图、记忆分层图、策略边界图、配置层次图、可观测性闭环图等专业图表
- **FR-7**: 知识关联——建立与harness-engineering-wiki、four-engineering-concepts-wiki、agent-skills-wiki等现有wiki的交叉引用链接
- **FR-8**: 结构化输出——采用原子化多文件结构，包含总览页、理论章节、组件章节、实践章节、案例章节、FAQ、资源链接、速查手册及README索引
- **FR-9**: 层级化目录——生成清晰的章节目录导航，适配不同知识水平读者（入门路径/进阶路径/产品经理路径/开发者路径）

## Non-Functional Requirements
- **NFR-1**: 内容准确性：忠实于原文观点和案例，不篡改作者核心论点，区分原文观点与教程补充说明
- **NFR-2**: 可读性：使用通俗类比降低理解门槛，技术术语有清晰定义，适合产品经理和开发者共同阅读
- **NFR-3**: 结构清晰：严格遵循原子化文档规范，每个文件聚焦单一主题，文件间通过相对路径互引
- **NFR-4**: 图表质量：Mermaid图表遵循安全编码规则，配色专业，信息层次清晰
- **NFR-5**: 完整性：七大组件每个都必须有独立章节，不遗漏原文中的任何一个组件或核心观点
- **NFR-6**: 渐进式披露：从概述→组件→实践→案例→FAQ的递进顺序，支持不同深度的阅读需求
- **NFR-7**: YAML frontmatter：每个文件包含规范的id、title、date、category、tags、source等元数据字段
- **NFR-8**: 中文撰写：全文使用中文，术语首次出现附英文原文

## Constraints
- **Technical**:
  - 必须遵循项目wiki原子化结构规范（参考weasyprint-wiki和harness-engineering-wiki的结构模式）
  - 图表必须使用Mermaid格式，不得使用ASCII字符画或外部图片
  - Markdown文档使用MyST兼容语法
  - 交叉引用使用相对路径，禁止file:///绝对路径
  - 每个文件需包含YAML frontmatter
- **Business**:
  - 教程为公开学习内容，不包含私域信息
  - 输出位置固定为 docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/
- **Dependencies**:
  - 依赖已提取的微信文章内容（已通过defuddle获取）
  - 依赖现有harness-engineering-wiki的结构模式作为参考
  - 依赖项目的generate-readme.py脚本生成README索引

## Assumptions
- 用户期望的"七概念"即文章中提出的Harness七大组件（模型网关、工具注册表、知识库引擎、记忆系统、策略引擎、可观测性、配置管理），而非SpecWeave自身的R-I-E-C-A-F-V七概念方法论
- 文章内容已完整提取，包含所有核心观点、类比和案例
- 新wiki作为独立子目录存在，不修改现有harness-engineering-wiki的内容
- 教程主要服务于学习和知识沉淀目的，不追求工程实现细节

## Acceptance Criteria

### AC-1: 理论概述完整准确
- **Given**: 已提取的文章全文内容
- **When**: 编写理论概述章节
- **Then**: 准确定义Harness概念（"AI Agent的业务运行底座"），清晰阐述"LLM解决智能问题、Harness解决交付问题"的核心论点，完整列出七大组件名称及一句话定义，组件间关系描述准确
- **Verification**: `human-judgment`
- **Notes**: 需包含Harness定义原文引用，七大组件覆盖率100%

### AC-2: 七大组件每个都有独立深度章节
- **Given**: 文章内容和wiki结构规范
- **When**: 编写组件详解章节
- **Then**: 每个组件至少包含：定义、核心职责、生活场景类比解释、文章Agent中的具体应用、设计原则、常见误区，共7个独立章节文件
- **Verification**: `programmatic`
- **Notes**: 7个组件文件数量和命名必须规范

### AC-3: Mermaid图表专业且信息完整
- **Given**: 组件间关系和流程描述
- **When**: 绘制Mermaid图表
- **Then**: 至少包含7张专业Mermaid图表：组件架构总览图、组件协作流程图、模型网关路由决策图、知识库vs记忆系统对比图、策略引擎边界约束图、可观测性闭环图、配置管理层次图
- **Verification**: `human-judgment`
- **Notes**: Mermaid语法正确，遵循安全编码规则，可正常渲染

### AC-4: 实践指南可操作
- **Given**: 组件理论和案例分析
- **When**: 编写实践指南章节
- **Then**: 提供清晰的实施步骤（从最小可行Harness到完整系统）、组件选型决策表、实施优先级排序、各组件落地注意事项和反模式提醒
- **Verification**: `human-judgment`
- **Notes**: 需区分产品经理视角和开发者视角的实践要点

### AC-5: 案例分析深度充分
- **Given**: 文章中的"家庭聚餐"类比和"文章Agent"案例
- **When**: 编写案例分析章节
- **Then**: 深度剖析文章Agent案例，逐组件映射其在文章写作场景中的具体职责、配置要点和协同关系；家庭聚餐类比与七大组件形成完整映射表
- **Verification**: `human-judgment`

### AC-6: FAQ覆盖核心疑问
- **Given**: 教程全部内容
- **When**: 编写FAQ章节
- **Then**: 包含至少12个常见问题解答，覆盖：概念混淆（知识库vs记忆、工具vs策略等）、实施难点（如何开始、优先级、最小集）、边界判断（哪些不需要Harness、何时升级模型vs优化Harness）、与现有知识的关系（与Harness Engineering的区别/互补）
- **Verification**: `programmatic`

### AC-7: 原子化文件结构规范
- **Given**: wiki教程全部内容
- **When**: 组织文件结构
- **Then**: 输出约12-15个原子化Markdown文件（00-overview、01-concept、02-08各组件、09-practice、10-case-study、11-faq、12-resources、13-quick-reference、README），每个文件有规范YAML frontmatter，文件间通过相对路径正确互引
- **Verification**: `programmatic`

### AC-8: 与现有wiki建立正确关联
- **Given**: 新wiki和现有wiki结构
- **When**: 添加交叉引用
- **Then**: 在00-overview和12-resources中正确链接到harness-engineering-wiki、four-engineering-concepts-wiki等相关资源；同时更新上级目录README.md（02-agent-engineering-methodology/README.md）将新wiki加入索引
- **Verification**: `programmatic`

### AC-9: 适配多水平读者的学习路径
- **Given**: 完整教程内容
- **When**: 设计导航和学习路径
- **Then**: README中提供至少3条学习路径（产品经理快速入门/开发者完整路径/进阶关联学习），支持不同背景读者按需阅读
- **Verification**: `human-judgment`

### AC-10: 链接完整性验证通过
- **Given**: 全部wiki文件
- **When**: 运行链接检查
- **Then**: 所有本地相对路径引用正确可访问，无断链，无file:///绝对路径
- **Verification**: `programmatic`

## Open Questions
- [ ] 新wiki目录名称建议为 `harness-seven-components-wiki/` 还是 `harness-business-runtime-wiki/`？（倾向后者更准确描述主题，但前者直接呼应"七组件"）
- [ ] 是否需要在教程中增加"与现有harness-engineering-wiki的对比/互补说明"章节？
- [ ] 速查手册（13-quick-reference）的详细程度——是单页速查卡还是完整的参考手册？
