# Harness业务运行底座七组件Wiki教程 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建wiki目录结构与总览页（00-overview.md）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建目录 `docs/knowledge/learning/02-agent-engineering-methodology/harness-seven-components-wiki/`
  - 编写 `00-overview.md`：包含文章背景介绍、核心论点（LLM解决智能问题/Harness解决交付问题）、学习目标、前置知识要求、文档导航表、术语表
  - 在00-overview中嵌入组件架构总览Mermaid图（展示七大组件及其关系）
  - 包含原文来源标注和作者信息
  - 添加与现有harness-engineering-wiki的关联说明
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录存在且00-overview.md文件创建成功
  - `programmatic` TR-1.2: YAML frontmatter包含id、title、date、category、tags、source字段
  - `human-judgement` TR-1.3: 学习目标清晰，文档导航表完整列出所有后续章节
  - `human-judgement` TR-1.4: Mermaid架构图正确展示七大组件关系，语法可渲染

## [x] Task 2: 编写核心概念章（01-core-concepts.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 编写Harness核心定义：从"智能vs交付"问题出发，用家庭聚餐类比解释Harness
  - 阐述七大组件的一句话定义、核心职责、在Harness中的角色
  - 绘制组件协作流程图Mermaid（任务输入→模型网关→工具/知识/记忆→策略约束→执行→观测→配置闭环）
  - 解释七大组件之间的依赖关系和协作机制
  - 区分"Prompt只是开始"与Harness的关系
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-7
- **Test Requirements**:
  - `programmatic` TR-2.1: 文件存在且YAML frontmatter规范
  - `human-judgement` TR-2.2: 七大组件定义准确，与原文一致
  - `human-judgement` TR-2.3: 家庭聚餐类比解释清晰，与组件映射正确
  - `human-judgement` TR-2.4: Mermaid协作流程图完整展示组件间数据流

## [x] Task 3: 编写模型网关章节（02-model-gateway.md）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 模型网关（Model Gateway）的定义与核心职责：大脑调度中心
  - 核心原则：该用好模型不省、该用便宜模型不浪费、能用规则别麻烦大模型
  - 生活场景类比：家庭聚餐中不同助理的分工
  - 文章Agent中的三类典型任务路由（选题判断→强模型、材料整理→长上下文模型、格式整理→便宜模型）
  - 设计原则与常见误区（不要什么都用最贵模型、规则比模型可靠）
  - 绘制模型网关路由决策图Mermaid
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件存在且frontmatter规范
  - `human-judgement` TR-3.2: 模型网关定义、核心原则与原文一致
  - `human-judgement` TR-3.3: 文章Agent三类任务举例准确
  - `human-judgement` TR-3.4: 路由决策图Mermaid语法正确

## [x] Task 4: 编写工具注册表章节（03-tool-registry.md）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 工具注册表（Tool Registry）的定义与核心职责：Agent的手脚管理
  - 三件事：有哪些工具能用、每个工具需要什么参数、调用失败怎么办
  - 生活场景类比：家庭聚餐中可用的日历/地图/预订系统
  - 文章Agent中的工具应用（读取选题池、检索历史文章、保存草稿）
  - 关键区分：工具注册表回答"有没有/怎么调用"，不回答"该不该调用"（策略引擎职责）
  - 设计原则与常见误区
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-4.1: 文件存在且frontmatter规范
  - `human-judgement` TR-4.2: 工具注册表三件事描述准确
  - `human-judgement` TR-4.3: 工具注册表vs策略引擎的职责边界区分清晰

## [x] Task 5: 编写知识库引擎章节（04-knowledge-base.md）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 知识库引擎（Knowledge Base Engine）的定义：Agent的业务资料来源/参考书
  - 超越RAG的产品视角：不只是向量检索，是私有业务知识体系
  - 生活场景类比：家庭聚餐历史记录、餐厅评价、偏好资料
  - 文章Agent知识库三类内容：历史文章、案例纪要、观点框架
  - 核心洞见："知识库是你的判断力缓存"
  - 设计原则：不是堆资料，是让Agent逐渐理解你的内容资产
  - 常见误区
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-5.1: 文件存在且frontmatter规范
  - `human-judgement` TR-5.2: 知识库vs RAG的区分论述清晰
  - `human-judgement` TR-5.3: "判断力缓存"核心洞见准确保留
  - `human-judgement` TR-5.4: 三类知识库内容举例准确

## [x] Task 6: 编写记忆系统章节（05-memory-system.md）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 记忆系统（Memory System）的定义：便签本和档案柜
  - 短期记忆vs长期记忆的区分
  - 生活场景类比：记住"刚刚否掉了火锅"、"上次说过别选太远"
  - 文章Agent记忆应用：短期（正在写什么、被否掉的方向）、长期（写作风格、文章结构、标题偏好、不喜欢的表达）
  - 核心难点：不是记得越多越好——记太少没连续性、记太多上下文污染/成本飙升/串台
  - 产品经理真正要设计的：记什么、记多久、什么时候压缩/忘掉
  - 绘制记忆分层图Mermaid（短期工作记忆/中期会话记忆/长期偏好记忆）
  - 知识库vs记忆系统的关键区别（资料库vs便签本+档案柜）
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-6.1: 文件存在且frontmatter规范
  - `human-judgement` TR-6.2: 短期/长期记忆区分清晰，与原文一致
  - `human-judgement` TR-6.3: 记忆系统设计难点论述充分（遗忘/压缩/边界）
  - `human-judgement` TR-6.4: 知识库vs记忆系统区别对比表清晰
  - `human-judgement` TR-6.5: 记忆分层图Mermaid语法正确

## [x] Task 7: 编写策略引擎章节（06-policy-engine.md）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 策略引擎（Policy Engine）的定义：把规则和红线变成强制约束
  - 为什么策略引擎最容易被低估
  - 生活场景类比：预算不超2000元、未经确认不付款、不乱发消息
  - 文章Agent三条关键策略：选题策略（与定位有关/真实案例/商业判断）、内容安全策略（不写AI鸡汤/不复述无判断案例/不泄露私聊客户信息）、质量策略（开头有判断/有核心矛盾/不像咨询报告/像作者的文章）
  - 策略引擎vs记忆系统的区别：记忆记录事实、策略把事实和规则变成行动边界
  - 核心作用：不是让Agent更会写，而是让Agent不乱写
  - 绘制策略引擎边界约束图Mermaid（能力圈/安全红线/质量标准三层边界）
  - 常见误区
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-7.1: 文件存在且frontmatter规范
  - `human-judgement` TR-7.2: 文章Agent三条策略完整准确
  - `human-judgement` TR-7.3: 策略引擎vs记忆系统区分清晰
  - `human-judgement` TR-7.4: 策略边界图Mermaid语法正确

## [x] Task 8: 编写可观测性章节（07-observability.md）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 可观测性（Observability）的定义：知道Agent到底干得怎么样
  - 没有可观测性就没有Agent运营
  - 生活场景类比：花了多少钱、哪些环节出问题、下次选不选这家餐厅
  - 文章Agent的数据追踪工作流：阅读数/点赞数/推荐数/转发数→点赞率/推荐率/转发率
  - 数据解读：阅读高但认可低（标题党）、阅读不高但推荐转发高（选题窄但有价值）
  - Badcase闭环：发现问题→归因问题→修改策略/知识/提示词/工具
  - 核心洞见：可观测性决定能不能从"能用"优化到"好用"
  - 绘制可观测性闭环图Mermaid（执行→数据采集→指标分析→Badcase归因→策略优化→再执行）
  - 常见误区（只看结果数据不看Badcase）
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-8.1: 文件存在且frontmatter规范
  - `human-judgement` TR-8.2: 文章发布数据指标和解读逻辑准确
  - `human-judgement` TR-8.3: Badcase闭环流程完整
  - `human-judgement` TR-8.4: 可观测性闭环图Mermaid语法正确

## [x] Task 9: 编写配置管理章节（08-configuration.md）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 配置管理（Configuration Management）的定义：让Agent可以持续调教
  - 为什么产品经理必须理解配置管理（不能每次改规则都找开发发版）
  - 生活场景类比：本次预算1500还是3000、优先考虑老人还是小孩
  - 文章Agent配置项：目标读者（AI产品经理/软件公司老板）、核心交付物（深度长文/快速观点）、内容级别（公开发布/内部沉淀）
  - 配置vs长期记忆/策略红线的区别：配置是"这次任务怎么执行"，不是修改长期风格或触碰红线
  - 核心价值：不是每次重新教Agent怎么写，而是通过配置告诉它"这次我要什么"
  - 绘制配置管理层次图Mermaid（红线策略层/长期偏好层/任务配置层）
  - 常见误区
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-9.1: 文件存在且frontmatter规范
  - `human-judgement` TR-9.2: 配置管理与策略/记忆的边界区分清晰
  - `human-judgement` TR-9.3: 文章Agent配置项举例准确
  - `human-judgement` TR-9.4: 配置层次图Mermaid语法正确

## [x] Task 10: 编写实践指南章节（09-practice-guide.md）
- **Priority**: high
- **Depends On**: Task 3,4,5,6,7,8,9
- **Description**:
  - 分角色实践路径：产品经理视角 vs 开发者视角
  - 从零构建Harness的实施步骤（五步法）：
    1. 明确业务场景与交付标准（策略先行）
    2. 搭建最小工具集与模型路由
    3. 注入核心知识与记忆
    4. 建立观测与Badcase闭环
    5. 抽象配置实现持续调教
  - 实施优先级排序表（哪些组件必须先有、哪些可以后补）
  - 最小可行Harness（MVH）构建清单
  - 组件选型决策表（模型网关选型考量、知识库方案选择等）
  - 各组件落地注意事项与反模式
  - "大模型解决智能问题、Harness解决交付问题"实践印证
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-10.1: 文件存在且frontmatter规范
  - `human-judgement` TR-10.2: 实施步骤清晰可操作，五步法逻辑通顺
  - `human-judgement` TR-10.3: 实施优先级排序合理（策略/工具优先，配置/观测逐步完善）
  - `human-judgement` TR-10.4: 反模式提醒具体实用

## [x] Task 11: 编写案例分析章节（10-case-study.md）
- **Priority**: high
- **Depends On**: Task 3,4,5,6,7,8,9
- **Description**:
  - 案例一：家庭聚餐——七大组件生活化映射表（完整表格）
  - 案例二：文章Agent深度剖析
    - 业务场景与痛点（"改它比自己写还累"问题）
    - 七大组件逐一映射：每个组件在文章Agent中的具体配置
    - 组件协同工作流（从选题→写作→发布→复盘的全流程组件调用链）
    - 没有Harness的文章Agent vs 有Harness的文章Agent对比
  - 案例启示：有价值的Agent是能在具体业务里稳定交付结果的Agent
  - 传统PM交付功能 vs AI PM交付效果
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-11.1: 文件存在且frontmatter规范
  - `human-judgement` TR-11.2: 家庭聚餐→七大组件映射表完整准确
  - `human-judgement` TR-11.3: 文章Agent逐组件分析深入具体
  - `human-judgement` TR-11.4: 有无Harness对比表有说服力

## [x] Task 12: 编写FAQ章节（11-faq.md）
- **Priority**: medium
- **Depends On**: Task 10, 11
- **Description**:
  - 包含至少12个FAQ，覆盖以下类别：
    - 概念混淆类（4个）：知识库vs记忆有什么区别？工具注册表vs策略引擎如何划分？Harness和Prompt Engineering什么关系？配置管理vs长期记忆的边界在哪？
    - 实施难点类（4个）：最小可行Harness应该包含哪些组件？如何开始设计策略引擎？什么时候该升级模型vs优化Harness？知识库应该放哪些内容？
    - 边界判断类（2个）：什么样的Agent不需要完整Harness？Badcase闭环怎么落地？
    - 知识关联类（2个）：本教程和harness-engineering-wiki（驾驭工程）有什么区别和联系？Harness七大组件和四代工程范式（Prompt→Context→Harness→Loop）如何对应？
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-12.1: 文件存在且frontmatter规范
  - `programmatic` TR-12.2: FAQ数量≥12个，覆盖四个类别
  - `human-judgement` TR-12.3: 回答准确、清晰、有实操价值

## [x] Task 13: 编写资源链接章节（12-resources.md）
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 原文来源链接
  - 相关wiki资源交叉引用：
    - harness-engineering-wiki（驾驭工程：三代范式/四条铁律/六大模式）
    - four-engineering-concepts-wiki.md（四代工程范式演进）
    - harness-loop-engineering-article-analysis.md（Loop Engineering深度分析）
    - longcat-agent-learning-wiki（Loop Engineering实践）
    - headroom-context-compression-wiki（上下文管理）
  - 延伸阅读建议
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-13.1: 文件存在且frontmatter规范
  - `programmatic` TR-13.2: 所有本地引用路径正确（相对路径，无file:///）
  - `human-judgement` TR-13.3: 资源分类清晰，相关wiki链接准确

## [x] Task 14: 编写速查手册（13-quick-reference.md）
- **Priority**: medium
- **Depends On**: Task 3,4,5,6,7,8,9
- **Description**:
  - 七组件公理速查卡表格（组件/一句话公理/核心职责/生活类比/文章Agent应用/设计原则）
  - 核心论点速记：LLM解决智能问题/Harness解决交付问题
  - MVH最小可行Harness检查清单
  - Badcase闭环速查
  - 与harness-engineering-wiki核心概念对照表
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-14.1: 文件存在且frontmatter规范
  - `human-judgement` TR-14.2: 速查表信息密度高、可快速查阅
  - `human-judgement` TR-14.3: 七组件公理卡准确完整

## [x] Task 15: 生成README.md索引并更新上级目录
- **Priority**: high
- **Depends On**: Task 1-14
- **Description**:
  - 编写harness-seven-components-wiki/README.md：包含主题概述、文档索引表（含标签）、多路径学习导航（产品经理快速入门/开发者完整路径/进阶关联学习）、相关资源链接
  - 使用README_INDEX_START/END标记包裹索引表区域（遵循项目自动生成规范）
  - 更新上级目录 `docs/knowledge/learning/02-agent-engineering-methodology/README.md`：
    - 在子Wiki索引表中新增harness-seven-components-wiki条目
    - 在根级文档索引中新增入口文件链接（如需要）
    - 在推荐学习路径中适当位置加入新wiki
    - 在快速导航按场景分组中加入新wiki链接
- **Acceptance Criteria Addressed**: AC-7, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-15.1: README.md存在且包含完整索引表
  - `programmatic` TR-15.2: README_INDEX_START/END标记正确
  - `human-judgement` TR-15.3: 至少3条学习路径设计合理（产品经理/开发者/进阶）
  - `programmatic` TR-15.4: 上级目录README已更新，新wiki条目信息准确
  - `programmatic` TR-15.5: 所有交叉引用路径正确（相对路径）

## [x] Task 16: 链接完整性验证与最终质量检查
- **Priority**: high
- **Depends On**: Task 15
- **Description**:
  - 运行链接检查脚本验证所有本地相对路径引用正确
  - 检查所有Mermaid图表语法（无语法错误、遵循安全编码规则）
  - 检查所有文件YAML frontmatter完整性和规范性
  - 检查是否有file:///绝对路径（必须为零）
  - 检查七大组件覆盖完整性（每个组件有独立章节）
  - 检查FAQ数量（≥12个）
  - 检查Mermaid图表数量（≥7张）
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `programmatic` TR-16.1: 链接检查通过，零断链
  - `programmatic` TR-16.2: 无file:///绝对路径
  - `programmatic` TR-16.3: Mermaid图表≥7张且语法正确
  - `programmatic` TR-16.4: FAQ≥12个
  - `programmatic` TR-16.5: 七大组件独立章节文件数=7个
  - `human-judgement` TR-16.6: 内容忠实于原文，核心观点无遗漏或歪曲
