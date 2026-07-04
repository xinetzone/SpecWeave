# MopMonk 安全 Agent 系统 Wiki 教程 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 验证目标目录并准备文件结构
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 检查 docs/knowledge/learning/ 目录是否存在，如不存在则创建
  - 确定最终文件名并验证命名规范（kebab-case、纯英文）
  - 准备TOML frontmatter模板，包含source字段指向原文章URL
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-1.1: 目标目录 docs/knowledge/learning/ 存在
  - `programmatic` TR-1.2: 文件名符合kebab-case规范，通过 `python .agents/scripts/check-filename-convention.py` 验证
  - `human-judgement` TR-1.3: TOML frontmatter包含正确的source字段，格式符合派生产物溯源要求

## [x] Task 2: 编写教程概述与学习目标章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 撰写教程引言，介绍MopMonk（扫地僧）的背景和CyberGym榜单成绩
  - 明确列出学习目标（读者学完后能理解什么）
  - 说明前置知识要求和适合的读者群体
  - 提供教程内容概览
- **Acceptance Criteria Addressed**: [AC-1, AC-3]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 学习目标明确具体，可衡量
  - `human-judgement` TR-2.2: 背景介绍准确反映原文关键信息（73.1%成功率、全球第七、中国第一）
  - `human-judgement` TR-2.3: 语言通俗易懂，适合目标读者

## [x] Task 3: 创建目录导航系统
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 设计完整的文档目录结构，包含所有必需章节
  - 使用Markdown锚点链接创建可点击的目录导航
  - 确保目录层级清晰，逻辑顺序合理（从入门到深入）
- **Acceptance Criteria Addressed**: [AC-1, FR-1]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 目录包含所有必需章节（概述、核心概念、步骤导读、FAQ、资源链接）
  - `human-judgement` TR-3.2: 目录链接指向正确的章节锚点
  - `human-judgement` TR-3.3: 章节顺序符合学习逻辑

## [x] Task 4: 编写核心概念解析章节
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 解析CyberGym基准：UC Berkeley打造、ICLR 2026论文、1507个漏洞实例、188个开源项目、"AI安全奥运会"地位
  - 解析Harness协调层：模型与工具/环境之间的协调层、手脚+神经系统比喻、工具编排/状态管理/反馈回收
  - 解析PoC（概念验证）：漏洞触发输入、"漏洞版触发、修复版不触发"的差分判定要求
  - 解析MiniMax M3基座：上海开源模型、三大能力（编程/1M上下文/多模态）、SWE-Bench Pro 59.0%等跑分数据
  - 解析MopMonk三大核心技术：
    1. 结构化漏洞记忆（七类记忆对象、下一步硬约束、证据收敛）
    2. 记忆驱动的漏洞挖掘（初始化记忆、假设测试、结果写回、降低上下文负担）
    3. 共享记忆多Agent并行探索（多方向推进、共享失败经验、提升有效试验密度）
  - 关键术语首次出现时提供解释
- **Acceptance Criteria Addressed**: [AC-2, AC-3, FR-3, FR-8]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 所有关键概念解释与原文一致，无编造内容
  - `human-judgement` TR-4.2: 关键数据准确无误（73.1%、1507、188、7.5倍、59.0%、66.0%、74.2%等）
  - `human-judgement` TR-4.3: 专业术语有清晰解释，非专业读者可理解
  - `human-judgement` TR-4.4: 三大核心技术的解析完整准确，逻辑清晰

## [x] Task 5: 编写步骤式学习导读指南
- **Priority**: medium
- **Depends On**: Task 4
- **Description**: 
  - 设计三层学习路径：
    - 入门层（Level 1）：理解MopMonk现象和行业意义（适合所有读者）
    - 进阶层（Level 2）：理解Harness价值和Agent架构（适合开发者）
    - 深入层（Level 3）：掌握三大核心技术细节（适合AI安全研究者）
  - 为每一层提供明确的学习步骤、阅读重点和思考题
  - 提供MopMonk技术架构的文字描述（可选Mermaid图）
- **Acceptance Criteria Addressed**: [AC-1, FR-4]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 三层学习路径清晰分层，难度递进合理
  - `human-judgement` TR-5.2: 每层有明确的学习目标和重点内容指引
  - `human-judgement` TR-5.3: （如使用Mermaid）图表符合安全编码六规则，可正确渲染

## [x] Task 6: 编写常见问题解答（FAQ）章节
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 设计至少5个常见问题，覆盖：
    1. MopMonk团队到底是谁？（身份猜测，保持开放不证实）
    2. MopMonk和传统漏洞挖掘工具/方法有什么区别？
    3. 为什么Harness比堆参数更重要？
    4. 普通人如何学习AI安全Agent开发？
    5. MopMonk的成绩对AI行业意味着什么？
    6. MiniMax M3基座在其中起到什么作用？
  - 每个问题提供基于原文的准确回答，不添加未经证实的推测
- **Acceptance Criteria Addressed**: [AC-6, FR-5]
- **Test Requirements**:
  - `human-judgement` TR-6.1: FAQ包含至少5个问题，覆盖身份、技术、行业等多个维度
  - `human-judgement` TR-6.2: 回答基于原文内容，不编造信息
  - `human-judgement` TR-6.3: 回答清晰有帮助，能真正解答读者疑问

## [x] Task 7: 整理相关资源链接章节
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 
  - 整理并列出所有相关资源链接：
    - 原微信公众号文章（标注来源）
    - CyberGym论文：https://arxiv.org/pdf/2506.02548
    - MopMonk GitHub仓库：https://github.com/MopMonkAI/MopMonkAgent
    - MiniMax M3相关资源（如原文提及）
    - 其他相关基准（NYU CTF、CVE-Bench、SWE-Bench等，简单说明）
  - 对每个链接提供简短说明，介绍资源内容
- **Acceptance Criteria Addressed**: [AC-4, FR-6]
- **Test Requirements**:
  - `programmatic` TR-7.1: 所有URL格式正确，无拼写错误
  - `human-judgement` TR-7.2: 每个链接有清晰的内容说明
  - `human-judgement` TR-7.3: 覆盖原文提及的所有重要资源

## [x] Task 8: 整体审校与格式规范验证
- **Priority**: high
- **Depends On**: Task 7
- **Description**: 
  - 通读全文，确保逻辑连贯、语言流畅
  - 检查所有技术数据与原文一致性
  - 验证Markdown格式正确性（标题层级、列表、链接等）
  - 检查TOML frontmatter完整性
  - 运行文件名规范检查脚本
  - （可选）运行链接检查工具验证内部锚点
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-5]
- **Test Requirements**:
  - `programmatic` TR-8.1: 文件名通过命名规范检查
  - `human-judgement` TR-8.2: 全文无技术错误和数据偏差
  - `human-judgement` TR-8.3: Markdown格式正确，渲染无问题
  - `human-judgement` TR-8.4: TOML frontmatter符合规范要求
