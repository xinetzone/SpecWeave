# Agentrys AI多智能体芯片设计工作流 - 实施计划（tasks.md）

## [x] Task 1: R阶段 - 事实采集与结构化整理
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 从已获取的文章内容中提取客观事实，形成结构化事实清单
  - 事实需覆盖：文章背景信息、Agentrys公司与白皮书概述、四大核心架构属性（分层编排/受治理迭代/目标无关性/溯源知识库）、五子系统流程、AgentCore芯片规格与硬约束、PPA收敛数据、Sign-off结果、开源工具栈、核心主张
  - 严格遵循G1质量门：无因果推断词（"因为"/"所以"/"导致"/"错误"/"说明"/"证明"等），纯客观描述
  - 每条事实标注来源段落引用
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 事实数量≥20条
  - `programmatic` TR-1.2: 因果词黑名单扫描（因为/所以/导致/错误/失误/说明/证明），零命中
  - `programmatic` TR-1.3: 事实覆盖四大架构属性、五子系统流程、核心成果数据三个维度
  - `human-judgement` TR-1.4: 事实描述客观中立，不包含分析判断或推论
- **Notes**: 参考[retrospective指令集](file:///d:/spaces/SpecWeave/.agents/commands/retrospective.md)的事实采集规范
- **完成状态**: 产出36条事实，G1质量门通过，文件：facts.md

## [x] Task 2: I阶段 - 核心洞察提炼
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于事实清单，提炼≥3条核心洞察
  - 每条洞察必须包含四元组：(1)现象陈述 (2)证据（引用事实编号Fxx） (3)反常识/深层本质 (4)可迁移行动建议
  - 洞察聚焦于：为什么Agentrys的工作流能成功？其架构设计有哪些超越芯片设计领域的通用原则？
  - 需明确指出与现有"多智能体闭环执行"模式的关系和差异
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `programmatic` TR-2.1: 洞察数量≥3条
  - `programmatic` TR-2.2: 每条洞察包含四元组全部四个要素，证据引用事实编号
  - `human-judgement` TR-2.3: 反常识要点超越表面总结，揭示深层架构原则
  - `human-judgement` TR-2.4: 可迁移行动建议可直接应用于AI辅助软件工程领域
  - `human-judgement` TR-2.5: 与现有闭环执行模式的差异已明确说明
- **Notes**: 参考[insight指令集](../../../../.agents/commands/insight.md)
- **完成状态**: 产出4条洞察（有界迭代预算、跨阶段回溯反馈、溯源信任基础设施、目标-机制解耦），G2质量门通过，文件：insights.md

## [x] Task 3: E阶段 - 模式萃取与文档化
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 根据洞察结果，决定萃取1个还是2个模式（候选："受治理迭代预算"模式、"溯源驱动知识积累"模式）
  - 每个模式按标准模板编写：YAML frontmatter（id/title/type/date/maturity/source/related_patterns/tags）+ 触发场景 + 核心做法（3-7步）+ 反模式（≥3个）+ 检验标准 + 迁移示例（≥1个跨领域）
  - 选择正确的存储目录：架构类→architecture-patterns/，治理类→governance-strategy/
  - 成熟度初始标记为L1-draft（单案例待验证）
- **Acceptance Criteria Addressed**: AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-3.1: 模式数量1-2个，符合萃取决策
  - `programmatic` TR-3.2: 每个模式frontmatter字段完整（id唯一，title，type，date，maturity，source，related_patterns，tags）
  - `programmatic` TR-3.3: 核心做法3-7步，可直接执行
  - `programmatic` TR-3.4: 反模式≥3个，对等提炼
  - `programmatic` TR-3.5: 迁移示例≥1个非芯片/EDA领域（如AI软件工程、DevOps、内容生成等）
  - `human-judgement` TR-3.6: 抽象层级合适——不具体到芯片设计，也不空洞到"注意风险"
  - `human-judgement` TR-3.7: 与现有模式无实质重复，关系（互补/扩展/独立）清晰说明
- **Notes**: 参考[extraction指令集](../../../../.agents/commands/extraction.md)；需grep检查现有模式库防重复
- **完成状态**: 产出2个模式（bounded-iteration-budget治理策略模式、provenance-driven-trust架构模式），G3质量门通过

## [x] Task 4: V阶段 - 对抗性审查
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 对每个萃取模式进行多视角对抗审查，至少覆盖3个视角：
    - 魔鬼代言人视角：攻击模式的假设条件，找出可能失效的场景
    - 新人视角：模式描述是否清晰？是否有隐含前提未说明？
    - 约束极限视角：在极端条件下（零预算/极紧时间/无知识库积累）模式是否成立？
  - 输出具体审查意见（≥5条总计，≥2条被采纳修正）
  - 根据审查意见修正模式文档
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 审查意见总计≥5条，具体且有实质内容（非"写得很好"类客套话）
  - `programmatic` TR-4.2: 至少2条审查意见被采纳并修正了模式文档
  - `programmatic` TR-4.3: 覆盖≥3个审查视角
  - `human-judgement` TR-4.4: 审查意见确实暴露了模式的潜在盲区，修正后模式更健壮
- **Notes**: 参考[adversarial-review指令集](file:///d:/spaces/SpecWeave/.agents/commands/adversarial-review.md)
- **完成状态**: 产出7条审查意见，采纳4条修正模式文档，V门质量门通过，文件：adversarial-review.md

## [x] Task 5: C阶段 - 模式入库、索引更新与验证
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 将最终模式文件写入正确的patterns子目录
  - 更新对应目录的README.md索引，添加新模式条目
  - 添加related_patterns交叉引用
  - 运行link-check.py验证所有链接有效
  - 检查是否需要更新更高层级的索引文件
  - 生成本次知识沉淀的简要执行记录（R→I→E→V各阶段产出摘要+质量门通过记录）
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: 模式文件位于正确目录（architecture-patterns/ 或 governance-strategy/）
  - `programmatic` TR-5.2: 对应目录README.md已更新，包含新模式条目
  - `programmatic` TR-5.3: `python .agents/scripts/check-links.py` 链接验证通过，零断链
  - `programmatic` TR-5.4: 模式frontmatter中related_patterns字段已正确填写
  - `human-judgement` TR-5.5: 索引条目格式与现有条目一致，分类正确
- **Notes**: 参考[docgen-cmd](../../../../.agents/skills/docgen-cmd/SKILL.md)进行索引更新
- **完成状态**: 两个模式文件位于正确目录，两个README索引已更新，related_patterns交叉引用验证通过，链接检查零断链，执行摘要已生成，G4质量门通过
