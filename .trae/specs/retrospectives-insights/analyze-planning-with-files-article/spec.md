# planning-with-files 文章深度洞察分析 Spec

## Why

用户希望对微信公众号文章《planning-with-files:像 Manus 一样工作》进行系统性学习、深度洞察与知识萃取。该文章介绍了 GitHub 开源项目 `OthmanAdi/planning-with-files`(24 小时内获得 23,000+ Star),该项目将 Manus(被 Meta 以 20 亿美元收购的 AI Agent 公司)的"上下文工程"方法论开源化,核心是通过"3-File Pattern"(task_plan.md / findings.md / progress.md)将文件系统作为 AI 的"外接硬盘",解决 Context Window 导致的失忆、目标漂移、重复犯错三大痛点。

此方法论与 SpecWeave 项目的核心使命高度相关:SpecWeave 自身通过 `.agents/` 规范体系、AGENTS.md 启动协议、上下文路由表、spec-driven 工作流解决类似的 AI 智能体协作问题。深入分析可为本项目的智能体记忆机制、Skill 体系设计、阶段守卫规则提供借鉴与反思视角,并识别两类"上下文工程"方案(文件系统外接 vs 规范路由)的差异化价值。

## What Changes

- 提取并整理微信文章全文内容,识别文章主体结构(开场引入/痛点剖析/方案呈现/Hooks 机制/安装方法/实测对比/适用场景/社区扩展/总结升华)
- 提炼文章核心观点:AI Agent 瓶颈在工程化方法而非模型能力,文件系统作为持久化外存可根治 Context Window 失忆症
- 分析论证逻辑:从"金鱼记忆"痛点到"3-File Pattern"方案再到"Hooks 自动化"升华的逻辑链条
- 评估信息结构:九章节的组织方式与内容层次
- 萃取关键知识点:3-File Pattern 职责划分、6 个 Hooks 自动动作、4 大核心规则、5 种 IDE 安装方式
- 评估信息来源可靠性(Manus 收购真实性、23k Star 数据、OthmanAdi 作者权威性)、内容时效性、专业性
- 与 SpecWeave 现有实践对照分析:planning-with-files 的 3-File Pattern ↔ SpecWeave 的 spec.md/tasks.md/checklist.md;Hooks 机制 ↔ 阶段守卫;2-Action 规则 ↔ 上下文路由表
- 形成系统性理解与批判性思考,输出结构化洞察分析报告
- **BREAKING**:无(纯分析任务,不涉及代码或现有文档修改)

## Impact

- Affected specs: 无直接修改;产出可作为 retrospectives-insights 主题的方法论参考材料,并为 docs/knowledge/ 增加一篇上下文工程最佳实践知识文档
- Affected code: 无代码改动;产出为 Markdown 分析报告
- 关联资产:可与 SpecWeave 的 `.agents/` 体系、AGENTS.md 启动协议、阶段守卫规则、Skill 命令体系形成双向对照分析

## ADDED Requirements

### Requirement: 文章全文内容提取与结构识别

系统 SHALL 完整提取微信文章正文内容,并识别其结构组成(标题、副标题、正文段落、图片说明、代码块、引用块、相关链接)。

#### Scenario: 内容提取完整

- **WHEN** 分析任务启动
- **THEN** 系统已通过 defuddle 提取文章全文 Markdown
- **AND** 识别出文章的九大章节(开场引入、Context Window 痛点、planning-with-files 介绍、3-File Pattern、Hooks 机制、安装方法、实测对比、适用场景、社区扩展、总结)
- **AND** 保留代码块(3-File Pattern 文件名、安装命令)、引用块(Manus 原话)、图片说明文字
- **AND** 提取相关链接(GitHub 仓库 https://github.com/OthmanAdi/planning-with-files、MIT 许可证、23k Star 数据)

### Requirement: 核心观点提炼

系统 SHALL 准确提炼文章的核心观点与主张,包括主论点和支撑论点。

#### Scenario: 核心观点识别

- **WHEN** 进行核心观点分析
- **THEN** 识别主论点:"AI Agent 的瓶颈不在模型能力,而在工程化方法;planning-with-files 将文件系统作为 AI 外接硬盘,解决 Context Window 失忆症"
- **AND** 识别痛点论点:Context Window 是 AI 的"金鱼记忆"——TodoWrite 会消失、50 次工具调用后目标漂移、失败不记录、上下文越塞越慢
- **AND** 识别方案论点:3-File Pattern(task_plan.md / findings.md / progress.md)将易失 RAM 映射为持久 Disk
- **AND** 识别升华论点:Manus 值 20 亿美元不是因独家模型,而是因解决了"让 AI 记得住、不跑偏、不重复犯错"这一基础关键问题

### Requirement: 论证逻辑分析

系统 SHALL 分析文章的论证结构,评估论据是否充分支撑论点。

#### Scenario: 论证链条梳理

- **WHEN** 进行论证逻辑分析
- **THEN** 梳理"痛点引入(金鱼记忆)→ 失败模式归纳(4 类)→ 方案呈现(3-File Pattern)→ 原理升华(Context=RAM, Filesystem=Disk)→ 自动化机制(Hooks 6 动作 + 4 规则)→ 安装落地(5 种 IDE)→ 实测验证(21 轮对话对比)→ 适用边界(用/不用场景)→ 社区生态(fork 扩展)→ 总结升华(工程化 > 模型能力)"的论证结构
- **AND** 评估痛点描述是否有具体场景支撑(AI 改项目改到一半问"你要做什么"、10 步任务忘第 1 步、API 报错 3 次相同重试)
- **AND** 评估方案是否回应了所有提出的痛点(3-File Pattern 对应记忆/进度/发现,Hooks 对应自动重读/记录错误)
- **AND** 识别论证中的潜在跳跃(20 亿美元估值归因单一方法论是否过度简化)

### Requirement: 关键知识点萃取

系统 SHALL 系统性萃取文章中的关键技术知识点与方法论要点。

#### Scenario: 知识点结构化输出

- **WHEN** 进行知识萃取
- **THEN** 输出 Context Window 痛点的 4 类表现(TodoWrite 消失、50 次后目标漂移、失败不记录、上下文塞满)
- **AND** 输出 3-File Pattern 的三文件职责(task_plan.md 跟踪阶段进度 / findings.md 存储研究发现 / progress.md 会话日志测试结果)
- **AND** 输出核心原理映射(Context Window = RAM 易失有限 / Filesystem = Disk 持久无限 / 重要东西写到磁盘)
- **AND** 输出 Hooks 机制的 6 个自动动作(创建计划、重读计划、更新进度、存储发现、记录错误、验证完成度)
- **AND** 输出 4 大核心规则(先建计划再开工、2-Action 规则、记录所有错误、绝不重复失败)
- **AND** 输出 5 种 IDE 安装方式(Claude Code 插件、手动 clone、Git 子模块、Legacy Skills、Cursor/其他 IDE)
- **AND** 输出社区扩展生态(devis、multi-manus-planning、plan-cascade、agentfund-skill、buzhangsan/skill-manager 双语 Skill 管理器)

### Requirement: 信息来源可靠性评估

系统 SHALL 评估文章信息来源的可靠性,包括项目真实性、数据可信度、归因合理性。

#### Scenario: 来源可靠性评估

- **WHEN** 进行可靠性评估
- **THEN** 评估项目真实性(GitHub 仓库 OthmanAdi/planning-with-files 是否存在、23k Star 是否合理、MIT 协议)
- **THEN** 评估 Manus 收购事件真实性(Meta 2025 年 12 月以 20 亿美元收购、8 个月营收破亿)
- **THEN** 评估归因合理性(20 亿美元估值归因"上下文工程"方法论是否过度简化,是否存在其他关键因素)
- **THEN** 评估数据可信度(24 小时爆火、23k Star、社区 fork 数量,标注无法独立验证项)
- **THEN** 评估作者权威性(OthmanAdi 在 AI Agent 社区的地位、与 Manus 团队的关系)

### Requirement: 与 SpecWeave 实践对照分析

系统 SHALL 将 planning-with-files 方法论与 SpecWeave 现有实践进行对照,识别异同与可借鉴点。

#### Scenario: 双向对照分析

- **WHEN** 进行对照分析
- **THEN** 对照 3-File Pattern ↔ SpecWeave spec.md/tasks.md/checklist.md(职责映射:task_plan↔tasks、findings↔spec、progress↔checklist)
- **AND** 对照 Hooks 机制 ↔ SpecWeave 阶段守卫(自动触发 vs 显式路由)
- **AND** 对照 2-Action 规则 ↔ SpecWeave 上下文路由表(强制写文件 vs 强制读规范)
- **AND** 对照"先建计划再开工"↔ SpecWeave Spec 模式协议(先 spec 后 implementation)
- **AND** 对照"记录所有错误"↔ SpecWeave 复盘体系与知识库
- **AND** 识别 SpecWeave 独有优势(AGENTS.md 启动协议、vendor 嵌套路由、能力注册中心 L0/L1/L2、角色定义体系)
- **AND** 识别 planning-with-files 独有优势(Hooks 自动化、IDE 无关适配、社区生态规模)
- **AND** 提炼双向借鉴建议(SpecWeave 可借鉴 Hooks 自动化思路,planning-with-files 可借鉴规范路由体系)

### Requirement: 批判性思考与改进建议

系统 SHALL 对文章内容进行批判性思考,识别优点、局限与改进方向。

#### Scenario: 批判性分析

- **WHEN** 进行批判性思考
- **THEN** 识别文章优点(痛点场景化描述生动、方案三文件结构清晰、原理映射 RAM/Disk 直观、安装方式覆盖主流 IDE、实测对比有量化数据)
- **AND** 识别文章局限性(20 亿估值归因单一方法论过度简化、无失败案例与适用边界反例、无与同类工具对比、实测数据样本单一、未深入 Hooks 技术实现细节)
- **AND** 提出改进建议(补充 Hooks 实现原理、增加多场景实测样本、对比同类上下文工程方案、补充长期维护成本、讨论文件系统膨胀的治理策略)
- **AND** 识别方法论潜在风险(文件过多导致信息过载、Hooks 误触发、跨任务文件污染、版本冲突)

## MODIFIED Requirements

无(本次为新增分析任务,不修改现有需求)

## REMOVED Requirements

无(本次不移除任何现有需求)
