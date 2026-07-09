# 指令集-知识库映射关系的第一性原理分析 - Product Requirement Document

## Overview

* **Summary**: 基于"指令集-知识库关联对应性前提"模式和"第一性原理"六步思维框架，对[export-suggestions.md](file:///d:/AI/docs/retrospective/reports/insight-extraction/external-learning/retrospective-first-principles-comprehensive-research-20260709/export-suggestions.md#L63-L63)中暴露的模式沉淀状态不一致问题进行系统性分析。通过第一性原理拆解指令集与知识库关联的根本逻辑，建立完整的映射关系框架，明确关联对应规则，并从公理层面推导和验证关联逻辑的合理性。

* **Purpose**:

  1. 解决export-suggestions.md第62行与第63行的重复/不一致条目问题（同一模式一个标记"已完成"，一个标记"待沉淀"）
  2. 从第一性原理出发，将"关联对应性前提"从经验性模式提升为公理化推导的规则体系
  3. 建立指令集与知识库之间完整、可验证、系统性的映射框架，而非仅停留在三标准检查清单
  4. 明确指令集（operational how-to）与知识库（theoretical why/reference）的本质分工与关联边界

* **Target Users**: AI智能体方法论维护者、模式库贡献者、知识系统架构设计者

## Goals

* 从根本问题出发（Step 1），识别指令集与知识库关联的本质目的

* 剥离现有模式中隐含的经验假设（Step 2），识别哪些是真正的公理、哪些是特定场景的经验规则

* 拆解关联关系至不可再分的基本要素（Step 3），建立关联关系的形式化模型

* 提炼自洽的关联公理体系（Step 4），确保公理之间独立且完备

* 自下而上推导出完整的关联规则集（Step 5），覆盖何时关联、关联什么、如何关联、如何验证

* 通过已有案例验证推导结果（Step 6），确认first-principles和mermaid两个已验证案例符合推导规则，并识别现有模式的不足

## Non-Goals (Out of Scope)

* 不修改现有代码或生产文件（分析产出物放置在spec目录和可能的报告目录）

* 不创建新的可执行模式文件（本次是分析任务，模式沉淀属于后续任务）

* 不自动修复export-suggestions.md中的不一致（分析结论给出修复建议，由后续行动项执行）

* 不扩展到spec引用验证（spec-reference-validation.md中Spec引用验证部分是另一个子模式，本次聚焦指令集↔知识库映射）

* 不进行跨项目的大规模实证验证（仅用已有2个验证案例进行回溯验证）

## Background & Context

* **现有模式状态**：[spec-reference-validation.md](file:///d:/AI/docs/retrospective/patterns/methodology-patterns/governance-strategy/spec-reference-validation.md)已将"Spec引用验证"与"关联对应性前提"合并为一个模式，成熟度L2（validation\_count=2）

* **不一致问题**：export-suggestions.md第62行标记"指令集↔知识库关联对应性前提"已完成，第63行标记"指令集-知识库关联对应性前提"待沉淀（暂记录于project\_memory），二者名称仅差一个符号（↔ vs -），存在重复条目

* **project\_memory记录**：project\_memory中详细记录了该模式的三标准验证（完整流程/检查清单/项目验证）和两个验证案例

* **第一性原理框架**：[08-methodology-framework.md](file:///d:/AI/docs/knowledge/learning/first-principles/08-methodology-framework.md)定义了六步操作流程，[first-principles.md](file:///d:/AI/.agents/commands/first-principles.md)指令集定义了RACI矩阵和质量验收标准

* **关联关系现状**：9个指令集中仅2个（file-creation.md、first-principles.md、mermaid.md后补）建立了知识库关联，其余7个因无对应系统性资料档案而未关联

## Functional Requirements

* **FR-1**: 问题定义与边界澄清

  * 明确"指令集↔知识库关联"要解决的根本问题（不是"建立链接"这个动作本身）

  * 区分症状（噪声化的关联资源章节、断链）与根因（缺乏系统化的关联判定逻辑）

  * 划定分析边界：指令集(.agents/commands/)与知识库(docs/knowledge/)之间的双向关联

* **FR-2**: 现有假设列举与剥离

  * 系统性列出当前关联实践中隐含的所有假设

  * 逐条质疑：哪些是物理/逻辑硬约束，哪些是惯例/经验可挑战

  * 识别"物理多文件=系统性"谬误的深层原因

* **FR-3**: 基本要素拆解

  * 将关联关系拆解为不可再分的基本要素（关联方、关联目的、关联质量、关联结构、关联验证）

  * 从多学科视角（信息论、认知科学、知识工程、软件架构）分析每个要素

  * 建立关联关系的形式化描述模型

* **FR-4**: 关联公理体系提炼

  * 从基本要素中提炼自洽的公理集（3-5条）

  * 验证公理的独立性（公理之间不可互推）和完备性（所有规则可从公理导出）

  * 对公理进行可信度分级

* **FR-5**: 关联规则自下而上推导

  * 基于公理推导出完整的判定规则集（何时关联/不关联）

  * 推导出关联内容选择规则（链接到README还是具体文件、标注什么信息）

  * 推导出关联结构规则（子章节划分、路径风格、双向链接要求）

  * 推导出验证规则（有效性检查、质量验收）

* **FR-6**: 回溯验证与现有模式对比

  * 用first-principles案例验证推导规则

  * 用mermaid案例验证推导规则（特别验证单文件系统性的判定）

  * 将推导结果与现有spec-reference-validation.md的三标准对比，识别现有模式的完备性和不足

  * 明确回答export-suggestions.md第63行"待沉淀"条目的状态：是否需要单独沉淀、或已被现有模式覆盖、或需要拆分模式

* **FR-7**: 产出物生成

  * 生成完整的第一性原理分析报告，包含六步分析全过程

  * 生成关联映射框架（含公理、规则、判定矩阵）

  * 生成对export-suggestions.md第63行问题的明确诊断和处理建议

## Non-Functional Requirements

* **NFR-1**: 逻辑严谨性

  * 从公理到规则的推导链必须完整，每一步可追溯

  * 不允许跳跃式推理，每条规则必须明确标注源自哪条公理

* **NFR-2**: 可验证性

  * 所有结论必须可通过已有案例证伪或证实

  * 判定规则必须可操作（不能停留在抽象层面）

* **NFR-3**: 系统性

  * 规则集必须覆盖关联建立的全生命周期（判定→内容选择→结构设计→建立→验证→维护）

  * 不能遗漏关键决策点

* **NFR-4**: 诚实面对局限

  * 明确标注哪些结论是高可信度公理（🟢）、哪些是中可信度经验规则（🔵）、哪些是待验证假设（🟡）

  * 不声称第一性原理推导能解决所有问题

* **NFR-5**: 符合第一性原理指令集质量验收标准

  * 基础要素不可再分，无经验性假设混入公理层

  * 公理之间自洽无矛盾

  * 推导方案覆盖原问题全部边界

  * 验证基于事实数据而非主观判断

## Constraints

* **Technical**:

  * 分析产出为Markdown文档

  * 必须使用项目现有文件作为证据，不得编造案例

  * 遵循项目Markdown/frontmatter规范

* **Business**:

  * 本次是分析任务，产出物为理论框架和诊断结论，不直接修改文件

  * 分析深度控制在fundamental级别（按first-principles指令集depth参数）

* **Dependencies**:

  * 依赖已读取的关键文件：spec-reference-validation.md、first-principles.md、08-methodology-framework.md、task-reports/链接复盘报告、export-suggestions.md、insight-extraction.md、project\_memory.md

## Assumptions

* 假设现有2个验证案例（first-principles和mermaid）的事实数据准确无误

* 假设"指令集"和"知识库"的目录边界在本次分析范围内保持不变（.agents/commands/ vs docs/knowledge/）

* 假设分析结论可用于后续模式更新或拆分决策，但分析本身不执行文件修改

* 假设第一性原理方法论适用于此问题（问题属于方法论/架构决策范畴，符合first-principles指令集触发条件）

## Acceptance Criteria

### AC-1: 问题定义清晰

* **Given**: 开始分析前

* **When**: 执行Step 1问题定义

* **Then**: 明确区分症状（重复条目、噪声关联）与根因（关联判定缺乏公理化基础），问题陈述以"现状/期望/障碍/价值"四要素呈现

* **Verification**: `human-judgment`

* **Notes**: 问题定义不应预设解决方案（如不预设"应该拆分模式"或"应该合并模式"）

### AC-2: 假设清单完整

* **Given**: Step 2假设剥离

* **When**: 列举所有隐含假设

* **Then**: 至少列出8条以上隐含假设，并按"物理硬约束/工程约束/惯例约束"分类，每条标注是否可挑战

* **Verification**: `human-judgment`

### AC-3: 基本要素不可再分

* **Given**: Step 3要素拆解

* **When**: 拆解至基本要素

* **Then**: 每个要素满足"原子停止标准"：该要素是可验证事实而非判断、继续拆解不改变关联规则结论、在当前问题尺度下可靠

* **Verification**: `human-judgment`

### AC-4: 公理体系自洽独立完备

* **Given**: Step 4公理提炼

* **When**: 产出公理列表

* **Then**: 公理数量3-5条，满足：(a)相互独立不可互推，(b)所有后续规则可从公理导出，(c)公理之间无逻辑矛盾，(d)每条公理标注可信度等级

* **Verification**: `human-judgment`

### AC-5: 规则集推导完整可操作

* **Given**: Step 5规则重构

* **When**: 从公理推导关联规则

* **Then**: 规则覆盖四类决策：①是否建立关联（判定规则+判定矩阵）、②关联什么内容（文件选择+标注要求）、③如何结构化关联（章节组织+路径风格）、④如何验证（链接检查+质量验收），每条规则标注公理来源

* **Verification**: `human-judgment`

### AC-6: 双案例回溯验证通过

* **Given**: Step 6验证

* **When**: 用first-principles和mermaid两个案例测试推导规则

* **Then**: (a)两个案例均满足规则集的正向判定（应该关联），(b)两个案例的实际关联方式（文件选择、路径风格等）与规则一致或可解释偏差原因，(c)7个未关联指令集的判定结果与规则一致

* **Verification**: `programmatic` + `human-judgment`

* **Notes**: programmatic部分指可通过Grep/LS验证7个指令集确实无对应系统性资料

### AC-7: 现有模式对比诊断明确

* **Given**: 验证完成后

* **When**: 对比推导规则与spec-reference-validation.md现有三标准

* **Then**: 明确指出现有三标准哪些是公理级、哪些是规则级、遗漏了哪些维度、是否需要模式拆分或升级，并明确回答export-suggestions.md第63行"待沉淀"条目的处理方案

* **Verification**: `human-judgment`

### AC-8: 报告格式符合要求

* **Given**: 分析完成

* **When**: 生成最终报告

* **Then**: 报告包含六步完整结构（问题定义→假设列举→要素拆解→公理提炼→规则推导→验证结论），使用可信度分级标注结论，frontmatter符合项目规范

* **Verification**: `programmatic` + `human-judgment`

### AC-9: 第一性原理质量验收通过

* **Given**: 报告完成

* **When**: 对照first-principles指令集质量验收标准检查

* **Then**: 满足6条质量标准：基础要素真正不可再分、公理自洽无矛盾、方案覆盖全部边界、验证基于事实、推导链完整每步可追溯、成本收益评估客观（承认分析局限）

* **Verification**: `human-judgment`

## Open Questions

* [ ] spec-reference-validation.md中"Spec引用验证"和"关联对应性前提"是否是同一抽象层级的模式，还是应该拆分为两个独立模式？（分析过程中推导确定）

* [ ] 第63行条目中的"指令集-知识库关联对应性前提"与第62行的"指令集↔知识库关联对应性前提"是同一模式的名称变体，还是存在实质差异？（分析过程中确定）

* [ ] 现有三标准（完整流程/检查清单/项目验证）是否构成完备的判定条件，还是存在第四条隐含标准（如"与指令集执行步骤的对应关系"）？（推导过程中确定）

