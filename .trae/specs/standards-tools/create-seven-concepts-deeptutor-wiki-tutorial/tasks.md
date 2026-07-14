---
version: 1.0
id: create-seven-concepts-deeptutor-wiki-tutorial-tasks
title: 七概念理论与DeepTutor实践案例Wiki教程 - 实施计划
---

# 七概念理论与DeepTutor实践案例Wiki教程 - The Implementation Plan

## [x] Task 1: S阶段锚定 - 建立术语表与原文事实库
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 从DeepTutor原文提取关键术语表（glossary），包含术语→精确定义→禁止替换的同义词
  - 从七概念现有文档提取方法论术语表
  - 对DeepTutor原文进行段落编号/章节标记，为CLN引文溯源做准备
  - 将原文内容与术语表保存为中间参考文件（不提交到docs公共区域）
- **Acceptance Criteria Addressed**: AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-1.1: 术语表包含≥20个DeepTutor关键术语（如Agent引擎、Partners、三层记忆、Mastery Path、活书编译器、GraphRAG等）
  - `programmatic` TR-1.2: 术语表包含七概念7个核心术语（R/I/E/C/A/F/V）的准确定义
  - `programmatic` TR-1.3: 每个术语有明确的"禁止替换同义词"列表
  - `human-judgment` TR-1.4: 术语定义与原文表述一致，无擅自释义
- **Notes**: 遵循SVA模式的Source锚定阶段，这是后续所有编写的唯一事实源

## [x] Task 2: 教程原子化结构设计与目录创建
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 设计原子化文档结构，确定文件拆分方案（遵循单一职责、单文件≤500行）
  - 确定最终存放目录（建议`docs/knowledge/seven-concepts-deeptutor-tutorial/`）
  - 创建目录结构与README.md骨架（含导航表、阅读路径）
  - 设计Mermaid可视化图表（如适用：七概念五层模型DeepTutor映射图、学习路径图、文档导航图）
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-2.1: 目录结构设计完成，每个文件有明确主题，无主题重叠
  - `programmatic` TR-2.2: 预估单文件行数均≤500行
  - `human-judgment` TR-2.3: 导航结构符合从入门到进阶的认知路径
  - `human-judgment` TR-2.4: 文件命名遵循kebab-case规范
- **Notes**: 遵循A原子化粒度寻优，使用U型曲线平衡认知负荷与导航成本

## [x] Task 3: 七概念核心理论章节编写
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 编写00-overview.md（教程简介、阅读指南、前置知识）
  - 编写01-seven-concepts-theory/目录下理论文件：
    - 01-r-retrospective.md（复盘R）
    - 02-i-insight.md（洞察I）
    - 03-e-extraction.md（萃取E）
    - 04-c-atomic-commit.md（原子提交C）
    - 05-a-atomization.md（原子化A）
    - 06-f-first-principles.md（第一性原理F）
    - 07-v-adversarial-review.md（对抗性审查V）
  - 每个理论文件包含：一句话公理、4个基础要素、层级归属、核心价值、常见误区
  - 引用现有七概念文档时使用相对路径链接
  - 遵循术语表，不擅自替换术语
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-3.1: 7个概念文件全部创建
  - `programmatic` TR-3.2: 每个概念包含公理、4要素、层级归属三要素
  - `programmatic` TR-3.3: 所有YAML frontmatter完整（id/title/source/version）
  - `human-judgment` TR-3.4: 理论表述与现有七概念文档一致，无概念曲解
  - `human-judgment` TR-3.5: 语言通俗易懂，适合作为入门教程
- **Notes**: 理论部分要"教学化"表达，不是照搬方法论文档，要降低理解门槛

## [x] Task 4: DeepTutor项目案例介绍章节编写
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 编写02-deeptutor-case/目录下案例文件：
    - 00-deeptutor-overview.md（项目简介、背景、核心价值）
    - 01-core-architecture.md（Agent循环底层设计、六种模式共享runtime）
    - 02-nine-modules/（9大功能模块，每个模块独立文件或按合理粒度拆分）
    - 03-quick-start.md（快速开始：PyPI、Docker、CLI三种方式）
    - 04-pros-and-cons.md（优缺点评价、适用场景）
  - 所有引用原文内容使用>块引用，标注章节位置（遵循CLN规则）
  - 功能描述必须与原文一致，不添加原文未提及的功能
  - 包含原文提到的安装命令、配置参数、端口号等精确信息
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-4.1: 9大功能模块（Chat/Partners/My Agents/Co-Writer/Book/Knowledge Center/Learning Space/Memory/Settings）全部覆盖
  - `programmatic` TR-4.2: 三种安装方式命令与原文完全一致
  - `programmatic` TR-4.3: 所有原文引文标注了来源位置（如"——功能详情第2节"）
  - `programmatic` TR-4.4: 无原文未提及的虚构功能/数据/数字
  - `human-judgment` TR-4.5: 功能描述准确还原原文，无意译导致的信息偏差
- **Notes**: 此阶段只做事实性描述，不做七概念解读；解读留到下一任务；严格遵循术语表

## [x] Task 5: 七概念×DeepTutor融合分析章节编写
- **Priority**: high
- **Depends On**: Task 3, Task 4
- **Description**: 
  - 编写03-analysis/目录下分析文件：
    - 00-framework-mapping.md（七概念→DeepTutor映射总览表）
    - 01-r-in-deeptutor.md（DeepTutor如何体现复盘R：Memory三层记忆的反事实推理与因果转化）
    - 02-i-in-deeptutor.md（洞察I：Mastery Path的掌握度追踪与规律发现）
    - 03-e-in-deeptutor.md（萃取E：Knowledge Center的知识形式化与版本管理）
    - 04-c-in-deeptutor.md（原子提交C：六种模式独立切换但共享上下文的职责边界）
    - 05-a-in-deeptutor.md（原子化A：9大模块的粒度设计、单文件≤500行架构思想）
    - 06-f-in-deeptutor.md（第一性原理F：从"个性化终身辅导"公理出发的架构设计）
    - 07-v-in-deeptutor.md（对抗性审查V：Quiz模式的证伪测试、Mastery Path的达标 gate）
    - 08-combined-workflows.md（组合应用分析：R→I→E知识沉淀链路在Memory Graph中的体现、A→V→C原子化验证在模块设计中的体现等）
  - 每个分析必须：指出DeepTutor哪里体现该概念、为什么这么设计（机制M）、带来什么好处（结果B）
  - 避免"两张皮"：不是先讲理论再贴案例，而是融合分析
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: 7个单概念分析 + 1个组合工作流分析 = 8个分析文件全部创建
  - `human-judgment` TR-5.2: 每个分析有明确的"哪里体现→为什么→好处"三层结构
  - `human-judgment` TR-5.3: 分析有深度，不是简单贴标签（如不说"Memory就是R"，而是说"Memory的L1→L2→L3三层设计如何对应R的事实采集→反事实推演→因果转化"）
  - `human-judgment` TR-5.4: 组合工作流分析至少覆盖3种核心组合（R→I→E、A→V→C、F→V→I）
- **Notes**: 这是教程最有价值的部分，体现理论与实践的深度结合

## [/] Task 6: 学习路径与实践练习章节编写
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 编写04-learning-path/目录下学习文件：
    - 00-reading-guide.md（分阶段阅读路径：入门30分钟→进阶2小时→实战扩展）
    - 01-practice-exercises.md（实践练习：参考现有exercises格式，设计1-2个练习）
    - 02-self-checklist.md（自学质量检查清单：33项简化版）
    - 03-further-reading.md（延伸阅读：七概念完整文档索引、DeepTutor GitHub链接）
  - 练习设计要可操作：如"用七概念分析你熟悉的一个开源项目"
  - 提供练习评分标准（简化版rubric）
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: 阅读路径包含至少3个阶段（入门/进阶/实战）
  - `programmatic` TR-6.2: 至少1个可动手的实践练习
  - `human-judgment` TR-6.3: 练习有明确的目标、步骤、验收标准
  - `human-judgment` TR-6.4: 延伸阅读链接有效（相对路径+外部URL）
- **Notes**: 练习参考`governance-strategy/exercises/`下的现有材料

## [ ] Task 7: 导航README与索引组装
- **Priority**: medium
- **Depends On**: Task 3, Task 4, Task 5, Task 6
- **Description**: 
  - 完成教程主README.md（含教程简介、目标读者、目录导航表、阅读路径、Changelog）
  - 确保所有原子文件间的相对路径链接正确
  - 检查frontmatter完整性（id/title/source/version/date等）
  - 初步人工检查明显的断链和错误
- **Acceptance Criteria Addressed**: AC-4, AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-7.1: README.md包含完整目录导航表（按阅读顺序）
  - `programmatic` TR-7.2: 所有文件有完整YAML frontmatter
  - `programmatic` TR-7.3: 无`file:///`绝对路径
  - `human-judgment` TR-7.4: 导航逻辑清晰，新读者能找到入口
- **Notes**: README是读者第一接触点，必须清晰友好

## [ ] Task 8: V阶段 - 独立事实核查（委派新子代理）
- **Priority**: high
- **Depends On**: Task 7
- **Description**: 
  - 委派**未参与之前任何编写任务**的新子代理执行独立事实核查
  - 核查维度：
    (a) 引文真实性——所有>块引用中的每句话在原文中可定位
    (b) 术语一致性——关键术语与术语表一致，无近义词替换
    (c) 案例归属——DeepTutor的数据/功能/描述不张冠李戴
    (d) 章节标注——引用标注的章节位置准确
    (e) 虚构概念检测——教程中提到的DeepTutor功能/架构/数字在原文中存在
    (f) 理论准确性——七概念理论表述与现有方法论文档一致
  - 提供核查checklist，要求逐条验证并报告问题
  - 根据核查报告修复所有发现的问题
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-8.1: 核查子代理是全新的（无之前任务上下文）
  - `programmatic` TR-8.2: 核查覆盖6个维度（a-f）
  - `programmatic` TR-8.3: 所有发现的问题已修复
  - `human-judgment` TR-8.4: 核查报告有具体的问题定位（文件+行号），不是泛泛而谈
- **Notes**: **关键质量门**——防范"共享误解"和组装幻觉；核查子代理必须独立，不能复用之前的子代理

## [ ] Task 9: 质量门禁与最终收尾
- **Priority**: high
- **Depends On**: Task 8
- **Description**: 
  - 运行`python .agents/scripts/check-links.py --path <tutorial-dir>`检查链接有效性，修复断链
  - 检查所有文件单文件行数≤500行
  - 更新相关索引（如docs/knowledge/README.md，如需要）
  - 添加Changelog条目（用`<!-- changelog -->`标记）
  - 最终整体通读检查
- **Acceptance Criteria Addressed**: AC-4, AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-9.1: check-links.py通过，无断链
  - `programmatic` TR-9.2: 所有单文件≤500行
  - `programmatic` TR-9.3: 无`file:///`绝对路径
  - `human-judgment` TR-9.4: 整体阅读流畅，无明显逻辑断裂
- **Notes**: 使用ci-check-cmd中的链接检查能力；遵循docgen-cmd规范更新索引（如需）
