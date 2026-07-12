---
version: "1.0"
theme: "retrospectives-insights"
created: "2026-07-10"
status: "draft"
source: "spec.md"
---
# 七核心概念方法论体系整合 - The Implementation Plan

## [x] Task 1: 项目全面系统性复盘（第一性原理分析）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 使用git log统计项目从初创到当前的提交历史数据（总提交数、按时间分布、提交类型分布）
  - 按六大发展阶段（基础奠基期/规范建设期/品牌文档期/知识沉淀期/体系完善期/迁移归档期）梳理关键事件、决策点、产出物
  - 提取七个核心概念在项目历史中的实际应用案例（成功/失败各≥5个）
  - 运用第一性原理分析七概念的本质，剥离经验类比，识别隐含假设
  - 产出《项目全面系统性复盘报告》，存储为原子化模式文件
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: git提交数据真实统计（使用git log --oneline | wc -l等命令），提交数误差≤5
  - `programmatic` TR-1.2: 六大阶段每个阶段关键事件≥3个，有明确commit hash或文件引用
  - `programmatic` TR-1.3: 七概念应用案例≥10个（成功≥5，失败/反模式≥5），每个案例有具体文件引用
  - `human-judgment` TR-1.4: 复盘报告遵循"事实→分析→洞察→建议"结构，第一性原理分析有明确的假设剥离和公理提炼过程
  - `programmatic` TR-1.5: 报告文件大小3000-8000字符，符合原子化单一职责原则
- **Notes**: 参考[retrospective.md](../../../../.agents/commands/retrospective.md)指令集执行，数据验证三查法必须执行

## [x] Task 2: 七概念本质定位与层级模型构建
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于Task 1的第一性原理分析结果，提炼每个概念的≤5个不可再分基础要素
  - 建立五层定位图谱（感知层/认知层/验证层/执行层/沉淀层），明确每个概念的层级归属
  - 定义概念间的依赖关系、前置条件、后置输出
  - 绘制七概念关系全景Mermaid图（flowchart）
  - 产出《七概念本质定位与层级模型》原子化模式文件
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `human-judgment` TR-2.1: 每个概念基础要素≤5个，要素间独立无重叠，真正"不可再分"
  - `human-judgment` TR-2.2: 五层定位图谱逻辑自洽，无循环依赖
  - `programmatic` TR-2.3: Mermaid图语法正确可渲染，包含所有7个概念节点
  - `human-judgment` TR-2.4: 概念依赖关系DAG无环，前置/后置定义清晰
  - `programmatic` TR-2.5: 文件YAML frontmatter正确，相对路径引用无断链
- **Notes**: 参考[first-principles.md](../../../../.agents/commands/first-principles.md)的公理提炼方法

## [x] Task 3: 组合触发条件与决策树设计
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 梳理≥15种项目管理典型场景（里程碑完成/故障发生/新功能开发/重构/文档整理/知识沉淀/架构决策/代码审查/版本发布等）
  - 为每种场景定义触发特征、应使用的概念组合、执行顺序
  - 设计触发决策树（Mermaid flowchart）：从问题特征判断启动哪些概念
  - 定义单一概念/双概念组合/多概念协同的场景边界
  - 定义成本收益阈值规则：何时不应使用某概念（避免过度方法论）
  - 产出《七概念组合触发决策树》原子化模式文件
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: 覆盖典型场景≥15种，每种场景明确概念组合和顺序
  - `human-judgment` TR-3.2: 决策树逻辑清晰，从根节点到叶子节点路径无歧义
  - `programmatic` TR-3.3: Mermaid决策树语法正确可渲染
  - `human-judgment` TR-3.4: 成本收益规则包含≥3种"不应使用"场景（如简单问题/紧急修复/PoC阶段）
  - `programmatic` TR-3.5: 文件大小符合原子化标准，链接检查通过
- **Notes**: 参考[adversarial-review.md](../../../../.agents/commands/adversarial-review.md)的场景速查矩阵设计模式

## [x] Task 4: 五种核心组合应用流程设计
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 设计5种核心组合流程：
    1. 里程碑闭环流程（复盘→洞察→萃取→原子提交）
    2. 问题解决流程（第一性原理→对抗性审查→原子提交）
    3. 重构优化流程（洞察→原子化→对抗性审查→原子提交）
    4. 知识沉淀流程（复盘→萃取→原子化→原子提交）
    5. 创新突破流程（第一性原理→对抗性审查→洞察→萃取）
  - 每个流程包含：触发条件、输入清单、输出清单、≤10个执行步骤、RACI角色分工、质量门禁检查点
  - 每个流程配Mermaid流程图
  - 定义流程间跳转与嵌套规则
  - 产出5个原子化流程模式文件 + 1个流程总览索引文件
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 5种流程文档齐全，每个流程步骤≤10步
  - `human-judgment` TR-4.2: 每个流程触发条件明确无歧义，输入输出可验证
  - `programmatic` TR-4.3: 每个流程配有Mermaid图，语法正确可渲染
  - `human-judgment` TR-4.4: 流程间跳转规则覆盖≥3种嵌套场景
  - `programmatic` TR-4.5: 6个文件（5流程+1索引）均通过链接检查，frontmatter正确
- **Notes**: 参考现有各指令集的执行步骤设计，保持风格一致

## [x] Task 5: 交互机制与接口规范制定
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 定义每个概念的标准输入格式（接收什么数据、结构要求）
  - 定义每个概念的标准输出格式（产出什么、如何传递给下一个概念）
  - 建立跨概念追溯机制：从最终产出如何回溯到每个环节的决策依据（如commit hash关联、文档引用链）
  - 定义异常处理流程：某环节不通过/数据缺失/角色冲突时的回退、重试、升级路径（≥3种场景）
  - 定义组合场景下RACI责任聚合规则（与单一概念RACI的关系）
  - 产出《七概念交互机制与接口规范》原子化模式文件
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `human-judgment` TR-5.1: 7个概念的输入输出格式定义清晰，与现有指令集不矛盾
  - `human-judgment` TR-5.2: 追溯机制可操作，有具体的追溯方法说明
  - `human-judgment` TR-5.3: 异常处理覆盖≥3种失败场景，每种有明确处理路径
  - `human-judgment` TR-5.4: RACI聚合规则说明清楚，不与现有单一概念RACI冲突
  - `programmatic` TR-5.5: 文件通过链接检查，大小符合原子化标准
- **Notes**: 接口规范参考各指令集现有的"输入规范"和"输出规范"章节

## [x] Task 6: 质量标准与检查清单开发
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 开发七概念组合应用综合检查清单（≥20项），可直接逐项打勾验证
  - 为5种组合流程分别定义通过/不通过判定标准
  - 提炼≥8种常见反模式（表演式复盘/过度原子化/形式化审查/确认偏差/权威崇拜/幸存者偏差/为创新而创新/角色混同等），每种含识别特征、危害、避免方法
  - 定义方法论成熟度L1-L4评估标准（参考CMMI和现有模式成熟度）
  - 产出《七概念组合应用质量门禁与检查清单》原子化模式文件 + Quick Reference速查表
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: 综合检查清单项≥20，每项有明确检查方法和通过标准
  - `programmatic` TR-6.2: 5种流程各有≥3个量化或可判定的通过标准
  - `programmatic` TR-6.3: 反模式清单≥8种，每种有识别特征和避免方法
  - `human-judgment` TR-6.4: L1-L4成熟度标准可操作，有明确的跃迁条件
  - `programmatic` TR-6.5: Quick Reference速查表≤1页（≤3000字符），核心内容一目了然
  - `programmatic` TR-6.6: 所有文件通过链接检查
- **Notes**: 检查清单格式参考现有脚本和规范中的checklist设计

## [x] Task 7: 方法论自举验证（对抗性审查）
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 使用对抗性审查知识研究场景（七模块协议）对完整方法论体系进行自举验证
  - 执行步骤0：跨领域概念扫描（防御语义漂移，7个核心概念+相关术语）
  - 执行步骤1：来源三级分类（项目内部来源/权威方法论/学术来源）
  - 执行步骤2：可信度四级评分（🟢A/🔵B/🟡C/🔴D）
  - 执行步骤3：五维验证（来源资质/交叉验证/时效性/逻辑一致性/偏差识别）
  - 执行步骤4：异常标记（⚠️待验证/❓存疑/⚖️争议/🔍利益冲突/📚歧义术语）
  - 执行步骤5：记录完整验证日志
  - 执行步骤6：可信度动态调整，修复发现的问题
  - 执行元审查（自检）：完整性/偏差/方法论合规/反模式检测
  - 产出《方法论自举验证报告》+ 验证日志
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: 七模块协议完整执行，每个步骤有记录
  - `programmatic` TR-7.2: 🟢A级结论占比≥60%，🔴D级结论=0
  - `programmatic` TR-7.3: 所有⚠️/❓/⚖️/🔍标记均有说明和处理方案
  - `human-judgment` TR-7.4: 验证日志完整可追溯，第三方可复现审查过程
  - `human-judgment` TR-7.5: 方法论自洽性验证通过，无内部矛盾、无循环论证
  - `programmatic` TR-7.6: 元审查4项检查全部通过（完整性/偏差/合规/反模式）
- **Notes**: 严格按照[adversarial-review.md](../../../../.agents/commands/adversarial-review.md)知识研究场景七模块协议执行，禁止跳过步骤

## [x] Task 8: 产出物原子化归档与索引同步
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 将所有产出物（复盘报告/定位模型/决策树/5个流程/接口规范/质量清单/速查表/验证报告）原子化存储到`docs/retrospective/patterns/methodology-patterns/governance-strategy/`目录
  - 为每个文件添加正确的YAML frontmatter（id/title/source/x-toml-ref）
  - 创建对应的TOML元数据文件在`.meta/toml/`对应目录
  - 更新相关索引：
    - governance-strategy/README.md（新增模式条目）
    - methodology-patterns/README.md（更新分类统计）
    - docs/retrospective/patterns/README.md（更新模式计数）
  - 运行收尾脚本：`python .agents/scripts/finalize-atomization.py`
  - 运行链接检查：`python .agents/scripts/check-links.py --path docs/retrospective/patterns/methodology-patterns/governance-strategy/`
  - 更新本spec的tasks.md和checklist.md为全部完成状态
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-8.1: 所有文件存储路径正确，每个文件有正确的YAML frontmatter
  - `programmatic` TR-8.2: 对应TOML元数据文件齐全，路径正确
  - `programmatic` TR-8.3: 相关README索引已更新，包含新模式条目
  - `programmatic` TR-8.4: finalize-atomization.py执行无错误
  - `programmatic` TR-8.5: check-links.py执行无断链，无file:///绝对路径
  - `programmatic` TR-8.6: 所有文件通过CI检查（重复代码检测、中文编码等）
- **Notes**: 参考[atomization.md](../../../../.agents/commands/atomization.md)和[atomization-finalize-cmd](file:///d:/spaces/SpecWeave/.agents/skills/atomization-finalize-cmd/)执行收尾
