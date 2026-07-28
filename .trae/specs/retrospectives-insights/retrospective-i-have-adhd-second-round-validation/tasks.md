---
version: 1.0
---
# i-have-adhd知识沉淀任务二次验证复盘 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 执行过程完整回溯与R阶段事实采集
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 收集第一次任务完整上下文：spec.md/tasks.md/checklist.md/7份产出文件/元复盘报告
  - 基于tasks.md状态记录还原任务时间线：跨会话节点、子代理委托时序、质量门检查点、修复记录
  - 梳理R阶段客观事实清单：任务规模数据（文件数/行数/子代理次数/质量门数量/修复问题数）、执行流程节点、关键决策点
  - 创建validation-report.md，完成第一章：任务概览与执行时间线
  - 严格遵循G1质量门：事实描述无因果推断词，纯客观可验证
- **Acceptance Criteria Addressed**: [AC-1, AC-10]
- **Test Requirements**:
  - `programmatic` TR-1.1: validation-report.md已创建，YAML frontmatter包含version/source/title/date/meta_type字段
  - `programmatic` TR-1.2: 任务时间线覆盖：会话1（Task1-5）→上下文压缩→会话2（Task6-10）→元复盘，关键节点完整
  - `programmatic` TR-1.3: 事实清单Grep检查无"因为/导致/所以/因此/由于"等因果推断词
  - `human-judgement` TR-1.4: 所有事实数据（文件数/行数/子代理次数）可通过对应文件验证，无主观臆断
- **Notes**: R（复盘）阶段核心任务，保持客观中立，只记录"发生了什么"，不分析"为什么"

## [x] Task 2: 三条执行模式逐条有效性审计（I阶段核心）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 对照"编排-执行分层法"5个核心步骤，逐条审计执行遵循度：
    ①主代理制定三件套 → ②逐任务委托子代理 → ③主代理验证+更新状态 → ④质量门通过后推进 → ⑤最终统一验证
  - 对照"风格锚定法"5个核心步骤，逐条审计执行遵循度：
    ①确定目标目录 → ②读取1-2个现有条目 → ③识别隐式约定 → ④按锚定风格撰写 → ⑤对比检查一致性
  - 对照"强约束自检启发式"4个核心步骤，执行Grep强约束审计：
    ①搜索"必须/禁止/绝不/一定" → ②逐条追问反例 → ③柔化有例外的规则 → ④V阶段攻击边界
  - 每个模式给出遵循度三级评分（遵循/部分遵循/未遵循）+具体证据（文件路径+行号/片段）
  - 识别每个模式的≥2个优势点和≥1个待改进点
  - 完成validation-report.md第二章：执行模式有效性审计结果
- **Acceptance Criteria Addressed**: [AC-2, AC-3, AC-4, AC-10]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 3条执行模式每条均有完整的5/5/4步审计，每步有评分+证据
  - `programmatic` TR-2.2: 强约束词Grep搜索覆盖所有7份产出文件+元复盘报告，列出所有命中位置
  - `human-judgement` TR-2.3: 每个模式≥2个具体优势点+≥1个具体待改进点，均有证据支撑
  - `programmatic` TR-2.4: 审计结果使用表格呈现，清晰易读
- **Notes**: I（洞察）阶段开始，此处发现的问题是后续根因分析的基础；遵循"证据优先"原则，每个评分都要有具体文件证据

## [x] Task 3: 两个L2模式第二轮对抗审查（V阶段）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 对"行动优先输出范式"进行第二轮V阶段审查，采用第一次未使用的新视角：
    - 非技术用户视角：对非编程/非工具使用场景是否适用？
    - 多轮长对话视角：超过10轮对话后进度重述是否反而增加认知负担？
    - 创意写作/头脑风暴视角：结论前置是否会抑制创意发散？
    - 高风险决策视角：快速行动是否可能导致忽略关键风险？
  - 对"逆向适配创新模式"进行第二轮V阶段审查，重点寻找失败案例：
    - 检索/思考"极端群体方法→主流产品"的失败案例
    - 识别该模式的必要前提条件，不满足时必然失败
    - 识别模式应用过程中的早期预警信号
  - 每个模式产出≥3条新的实质性审查意见（不重复第一次V阶段的9条意见）
  - 对采纳的意见，直接补充/更新到对应模式文档中，记录修改说明
  - 完成validation-report.md第三章：L2模式第二轮对抗审查结果
- **Acceptance Criteria Addressed**: [AC-5, AC-9, AC-10]
- **Test Requirements**:
  - `programmatic` TR-3.1: 每个模式≥3条新审查意见，与第一次V阶段意见无重复
  - `human-judgement` TR-3.2: ≥2个新的边界场景/反例被识别，填补第一次审查盲区
  - `programmatic` TR-3.3: 采纳的意见已更新到对应模式文档，有Changelog记录
  - `human-judgement` TR-3.4: 审查意见具体有实质内容，非客套话或泛泛而谈
- **Notes**: V阶段核心，这次是对模式本身的审查而非对原始分析的审查，目标是找到模式边界而非否定模式价值

## [x] Task 4: 遗漏问题审计与根因分析
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**: 
  - 以"第三方审计者"视角通读所有7份产出文件+元复盘报告
  - 检查维度：错别字/语法错误、链接有效性（相对路径正确性）、逻辑自相矛盾、事实不准确、论证不充分、格式不规范、YAML frontmatter完整性
  - 对发现的问题进行分类：
    - P0（必须修复）：断链、事实错误、逻辑矛盾、影响理解的错别字
    - P1（建议修复）：表述不通顺、格式不美观、可补充完善的内容
    - P2（后续优化）：风格改进、结构优化、内容扩展建议
  - 对P0/P1问题进行根因分析（5 Why）：为什么第一次执行和第一次复盘都遗漏了这个问题？流程哪里有缺口？
  - 完成validation-report.md第四章：遗漏问题清单与根因分析
- **Acceptance Criteria Addressed**: [AC-6, AC-9, AC-10]
- **Test Requirements**:
  - `programmatic` TR-4.1: 问题清单使用标准表格（问题描述/文件位置/行号/严重程度/根因分析/修复建议/状态）
  - `human-judgement` TR-4.2: P0问题数量=0或全部在本次任务中修复
  - `human-judgement` TR-4.3: 根因分析追溯到流程层面，不是"粗心大意""没注意"等表面原因
  - `programmatic` TR-4.4: link-check验证所有内部链接有效性
- **Notes**: 不要回避问题，以"吹毛求疵"的标准进行审计；这一步是"修复即闭环"原则的体现

## [x] Task 5: 模式成熟度评估与I阶段洞察整合
- **Priority**: medium
- **Depends On**: Task 2, Task 3, Task 4
- **Description**: 
  - 对照SpecWeave模式成熟度L1-L4标准，评估5个模式（行动优先/逆向适配/编排-执行分层/风格锚定/强约束自检）的当前成熟度
  - 明确每个模式升级到L3（多案例验证）所需满足的具体条件，给出可执行的验证路径
  - 识别≥3个共性洞察：关于知识沉淀流程、七概念方法论执行、模式质量保证的更高层次结论
  - 每个洞察遵循G2质量门四元组：现象描述+根因分析+影响评估+改进建议
  - 完成validation-report.md第五章：模式成熟度评估与核心洞察
- **Acceptance Criteria Addressed**: [AC-7, AC-10]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 5个模式每个都有明确的当前成熟度等级+L3升级条件
  - `human-judgement` TR-5.2: ≥3条核心洞察，每条完整包含四元组（现象+根因+影响+建议），通过G2质量门
  - `human-judgement` TR-5.3: L3升级路径具体可执行，不是空泛的"需要更多案例"
- **Notes**: I（洞察）阶段收尾，从具体审计结果上升到方法论层面的洞察

## [ ] Task 6: 元复盘SOP萃取与模式文档更新（E阶段）
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 基于本次二次验证执行过程，萃取"知识沉淀二次验证SOP"可复用模式：
    - 触发时机：什么时候需要做二次验证？
    - 验证维度清单：必查的5-8个维度是什么？
    - 标准检查步骤：按什么顺序做验证？
    - 质量标准：验证通过的判定条件
    - 输出模板：验证报告的标准结构
  - 补充第一次萃取的3条执行模式文档（如需要）：根据本次审计结果补充边界场景、反例、注意事项
  - 将"知识沉淀二次验证SOP"存放到docs/retrospective/patterns/methodology-patterns/governance-strategy/目录（风格锚定同目录现有模式）
  - 完成validation-report.md第六章：元复盘SOP萃取说明
- **Acceptance Criteria Addressed**: [AC-8, AC-9, AC-10]
- **Test Requirements**:
  - `programmatic` TR-6.1: SOP模式文档已创建，YAML frontmatter完整（id/title/source/maturity等）
  - `programmatic` TR-6.2: SOP包含触发场景、核心步骤、检查清单、反模式、迁移验证五要素，通过G3质量门
  - `human-judgement` TR-6.3: SOP可独立理解，不参考本次具体任务也能执行二次验证
  - `human-judgement` TR-6.4: 对原有模式文档的补充内容恰当，不破坏原有结构
- **Notes**: E（萃取）阶段核心目标——将本次元复盘实践本身沉淀为可复用模式，实现"做一次复盘，沉淀一个SOP"的闭环

## [ ] Task 7: 问题修复与报告整合
- **Priority**: high
- **Depends On**: Task 4, Task 6
- **Description**: 
  - 修复Task4识别的所有P0问题和可在本次任务中修复的P1问题
  - 整合所有章节，撰写validation-report.md执行摘要（300字以内）
  - 撰写改进建议章节：对知识沉淀流程、七概念方法论执行、质量保证机制的具体改进建议
  - 添加Changelog章节
  - 记录行动优先范式在本次任务交互中的应用体验和自我评估
  - 确保报告整体逻辑连贯、前后呼应
- **Acceptance Criteria Addressed**: [AC-9, AC-11]
- **Test Requirements**:
  - `programmatic` TR-7.1: 所有P0问题100%修复，P1问题≥50%修复或有明确修复计划
  - `human-judgement` TR-7.2: 执行摘要300字以内，概括验证核心结论
  - `human-judgement` TR-7.3: 改进建议≥5条，每条具体可执行，明确修改位置/内容/验证方法
  - `programmatic` TR-7.4: Changelog章节使用<!-- changelog -->标记包裹
  - `human-judgement` TR-7.5: 包含范式自体验章节，诚实记录行动优先范式在本次长任务中的优缺点
- **Notes**: 修复问题时遵循"修复→预防→闭环"三阶段，不仅修复当前问题，还要补上流程缺口防止再发

## [ ] Task 8: 索引更新与最终验证收尾
- **Priority**: high
- **Depends On**: Task 6, Task 7
- **Description**: 
  - 更新governance-strategy/README.md索引，添加"知识沉淀二次验证SOP"条目
  - 更新retrospectives-insights/README.md，登记本spec状态为in_progress
  - 运行link-check验证所有链接有效性（本spec目录+模式更新目录）
  - 检查所有Markdown文件YAML frontmatter完整性
  - 检查无file:///绝对路径引用
  - 通读检查错别字、语法错误
  - 更新checklist.md标记所有验证点状态
  - 导出最终元复盘报告到docs/retrospective/reports/对应目录
- **Acceptance Criteria Addressed**: [AC-11]
- **Test Requirements**:
  - `programmatic` TR-8.1: 两个README.md索引已更新，包含新条目正确链接
  - `programmatic` TR-8.2: link-check脚本验证无链接错误
  - `programmatic` TR-8.3: 所有.md文件YAML frontmatter包含必要字段
  - `programmatic` TR-8.4: Grep搜索无file:///绝对路径引用
  - `human-judgement` TR-8.5: 通读无明显错别字或语法错误
  - `programmatic` TR-8.6: checklist.md所有检查点已更新状态
- **Notes**: 应用本次验证的强约束自检和风格锚定，确保本spec自身符合规范，做到"范式自我验证"
