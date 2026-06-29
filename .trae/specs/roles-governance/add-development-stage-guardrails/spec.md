# 开发流程阶段守卫与功能演进治理规则 Spec

## Why

SpecWeave 的 `.agents/` 目录已建立完整的角色定义、协作协议与功能开发工作流，但在实际执行中存在三个治理缺口：

1. **阶段越界问题**：角色定义中的 Non-Goals 是描述性约束（"不应该做X"），但缺少执行时的机制性拦截。AI 在需求讨论阶段可能直接跳到代码实现方案，或在编码阶段擅自变更架构决策，导致"越做越偏"。
2. **前置文档未强读**：AGENTS.md 启动协议要求加载规范文件，但开发过程中每个新阶段开始前没有强制要求读取前置输出文档（如 developer 开始编码前未读完 architect 的技术方案），上下文缺失导致实现偏离设计。
3. **功能变更无分类**：现有的 feature-development 工作流只覆盖"新功能从0到1"场景，缺少对已有功能变更的分类处理——小改走大流程效率低，大改走轻量流程风险高。

以上问题在竹简悟道项目开发中已多次暴露（如修BUG后回归问题出现、功能扩展时已有代码被搅乱）。社区优秀实践 SpecForge（topic/2000）的 GUARDRAILS 机制、PROJECT-CONTEXT 协议和功能演进分类提供了可借鉴的设计思路。本 Spec 将这三个治理机制融入 SpecWeave 现有体系，补强流程硬约束。

## What Changes

在现有 `.agents/` 治理体系基础上，新增和修改以下内容：

1. **新增阶段守卫规则**：在 `.agents/rules/` 下新增 `stage-guardrails.md`，定义开发流程的标准阶段序列、每个阶段的允许/禁止操作、跨阶段拦截规则
2. **新增前置文档强制读取协议**：在 `.agents/protocols/` 下新增 `pre-document-reading.md`，定义各角色在开始工作前必须读取的前置文档清单与确认机制
3. **增强功能开发工作流**：修改 `.agents/workflows/feature-development.md`，增加：
   - 每个步骤的"阶段守卫"检查点
   - 每个步骤的"前置文档"强制读取确认
   - 功能演进分支（新功能/功能扩展/功能重构三类路径）
4. **更新角色定义**：在 developer、architect、tester、reviewer 角色文件中补充阶段守卫相关的 Non-Goals 与职责
5. **更新 AGENTS.md 路由表**：在上下文路由表中新增阶段守卫规则和前置文档读取协议的入口

## Impact

- Affected specs: 无（本 Spec 为新增治理规则，不修改已有 spec 的核心结论）
- Affected code: 无代码修改，仅修改 `.agents/` 下的规范文档
- Affected docs:
  - 新增 `.agents/rules/stage-guardrails.md`
  - 新增 `.agents/protocols/pre-document-reading.md`
  - 修改 `.agents/workflows/feature-development.md`（较大改动：增加守卫检查点+功能演进分支）
  - 修改 `.agents/roles/developer.md`、`architect.md`、`tester.md`、`reviewer.md`（小改动：补充Non-Goals）
  - 修改 `AGENTS.md`（路由表新增条目）
  - 修改 `.agents/rules/README.md`（新增stage-guardrails索引）
  - 修改 `.agents/protocols/README.md`（新增pre-document-reading索引）

## ADDED Requirements

### Requirement: 阶段守卫规则定义

系统 SHALL 提供明确的开发阶段守卫规则，定义标准阶段序列和每个阶段的操作边界，AI 尝试跨阶段操作时必须被拦截。

#### Scenario: 标准阶段序列定义
- **WHEN** 智能体开始功能开发任务
- **THEN** 必须遵循以下标准阶段序列：需求接收 → 方案设计 → 任务分配 → 代码实现 → 测试编写 → 代码审查 → 合并代码 → 完成确认
- **AND** 每个阶段有且仅有一个负责角色
- **AND** 每个阶段有明确的进入条件和退出标准

#### Scenario: 各阶段操作边界
- **WHEN** 智能体处于某个阶段
- **THEN** 必须遵守该阶段的操作边界：
  - 需求接收阶段：只允许需求分析、边界澄清、验收标准定义；禁止讨论技术实现方案、禁止编写代码
  - 方案设计阶段：只允许架构设计、技术选型、接口定义、风险评估；禁止编写业务代码
  - 任务分配阶段：只允许任务拆分、角色匹配、优先级排序；禁止修改技术方案核心内容
  - 代码实现阶段：只允许按方案编码；禁止擅自变更架构决策、禁止跳过单元测试
  - 测试编写阶段：只允许测试用例设计、测试代码编写、缺陷记录；禁止自行修复发现的缺陷（须反馈给developer）
  - 代码审查阶段：只允许质量审查、改进建议；禁止直接修改代码
- **AND** 每个阶段边界必须包含正例和反例

#### Scenario: 跨阶段拦截
- **WHEN** 智能体在某个阶段尝试执行其他阶段的操作
- **THEN** 必须显式拦截，输出格式为：
  ```
  ⚠️ 阶段守卫拦截：当前为【X阶段】，【Y操作】属于【Z阶段】的职责。
  请先完成当前阶段：[当前阶段的退出标准]
  ```
- **AND** 拦截后不得执行越界操作，必须等待当前阶段完成或经orchestrator批准阶段跳转

#### Scenario: 阶段跳转审批
- **WHEN** 因特殊原因需要跳过某个阶段或逆向回退
- **THEN** 必须由orchestrator明确批准
- **AND** 审批记录须在交接文档中注明原因
- **AND** 逆向回退（如从代码实现回到方案设计）必须经过reviewer确认回退范围

### Requirement: 前置文档强制读取协议

系统 SHALL 定义各角色开始工作前必须读取的前置文档清单，并建立"不读完不许动手"的强制确认机制。

#### Scenario: 前置文档清单
- **WHEN** 各角色准备开始执行任务
- **THEN** 必须先读取以下前置文档：

  | 角色 | 阶段 | 必须读取的前置文档 |
  |------|------|-------------------|
  | orchestrator | 需求接收 | 用户需求原始描述、项目README、相关历史spec |
  | architect | 方案设计 | 任务分解清单、项目技术栈文档、现有架构文档、开发规范 |
  | orchestrator | 任务分配 | 技术方案文档、角色能力矩阵 |
  | developer | 代码实现 | 技术方案文档、任务分解清单、开发规范、相关模块现有代码 |
  | tester | 测试编写 | 需求文档、技术方案文档、代码实现、测试规范 |
  | reviewer | 代码审查 | 需求文档、技术方案文档、代码实现、测试报告、审查checklist |
  | orchestrator | 合并代码 | 审查通过报告、CI检查结果 |
  | orchestrator | 完成确认 | 合并结果、测试报告、验收标准清单 |

- **AND** 清单中的每一项必须可定位到具体文档路径

#### Scenario: 读取确认机制
- **WHEN** 角色开始执行任务时
- **THEN** 必须在输出中显式确认已读取所有前置文档，格式为：
  ```
  📋 前置文档确认：已读取 [文档1]、[文档2]、[文档3]
  ```
- **AND** 如果缺少某项文档，必须先请求获取或标注"文档缺失，基于现有信息继续"并说明风险

#### Scenario: 新会话强制重载
- **WHEN** 智能体在新会话中继续之前的任务
- **THEN** 必须重新读取所有相关前置文档
- **AND** 不得依赖前一会话的记忆继续执行

### Requirement: 功能演进分类处理

系统 SHALL 区分新功能、功能扩展、功能重构三类变更，分别定义对应的处理流程。

#### Scenario: 变更类型判定
- **WHEN** 接收到一个开发需求
- **THEN** orchestrator 必须首先判定变更类型：
  - **新功能（New Feature）**：从零构建的全新能力，不涉及已有功能的修改
  - **功能扩展（Extension）**：在已有功能上新增能力，不破坏现有结构和接口，回归风险低
  - **功能重构（Refactoring）**：改动已有功能的核心结构、数据模型或接口契约，可能影响现有行为，回归风险高
- **AND** 判定依据必须记录在任务分解清单中

#### Scenario: 三类变更的流程路径
- **WHEN** 变更类型确定后
- **THEN** 按以下流程路径执行：
  - **新功能**：完整8步流程（需求→设计→分配→编码→测试→审查→合并→确认）
  - **功能扩展**：轻量流程（影响分析→增量方案→增量实现→回归测试→增量审查→合并）
  - **功能重构**：重量流程（影响全量评估→方案重审→全量任务重规划→实现→全量回归→双重审查→合并）
- **AND** 功能扩展和功能重构的具体步骤在workflow文档中明确定义

#### Scenario: 功能扩展轻量流程
- **WHEN** 判定为功能扩展
- **THEN** 执行以下轻量流程：
  1. 影响分析：developer分析新增能力对已有代码的影响范围，列出需修改/新增的文件清单
  2. 增量方案：architect确认影响分析，给出增量实现方案（不重新设计整体架构）
  3. 增量实现：developer按增量方案编码，保持已有代码不变
  4. 回归测试：tester执行新增功能测试+相关已有功能的回归测试
  5. 增量审查：reviewer审查增量代码和回归测试结果
  6. 合并：orchestrator确认后合并
- **AND** 整个流程跳过"任务分配"阶段，由orchestrator直接指派
- **AND** 回归测试范围由architect在增量方案中明确

#### Scenario: 功能重构重量流程
- **WHEN** 判定为功能重构
- **THEN** 执行以下重量流程：
  1. 影响全量评估：architect评估重构对所有相关模块、接口、数据的影响，输出影响分析报告
  2. 方案重审：architect重新设计方案，reviewer参与方案审查
  3. 全量任务重规划：orchestrator根据新方案重新拆分任务
  4. 实现：developer按新方案实现，确保向后兼容或提供迁移路径
  5. 全量回归：tester执行全量测试（不只是相关模块）
  6. 双重审查：reviewer审查代码 + architect审查架构一致性
  7. 合并：orchestrator确认双重审查通过后合并
- **AND** 重构方案必须包含回滚策略
- **AND** 如果重构涉及数据迁移，必须包含数据迁移脚本和验证步骤

### Requirement: 工作流文档增强

系统 SHALL 更新 feature-development.md，将阶段守卫和前置文档读取机制嵌入每个步骤。

#### Scenario: 步骤执行要点增强
- **WHEN** 查阅 feature-development.md 的任意步骤
- **THEN** 每个步骤的"执行要点"必须包含：
  1. 阶段守卫检查：本阶段允许/禁止的操作
  2. 前置文档确认：开始前必须读取的文档清单
  3. 完成标志更新：包含前置文档已读取的确认
- **AND** 功能扩展和功能重构的分支流程在workflow中有独立章节

#### Scenario: 流程图更新
- **WHEN** 查看 feature-development.md 的 Mermaid 流程图
- **THEN** 必须包含功能演进的分支判断节点
- **AND** 三类变更的路径用不同样式区分（新功能实线、功能扩展虚线、功能重构点线）

### Requirement: AGENTS.md 路由更新

系统 SHALL 将阶段守卫规则和前置文档读取协议纳入 AGENTS.md 上下文路由表。

#### Scenario: 路由表新增条目
- **WHEN** AGENTS.md 被智能体加载
- **THEN** 上下文路由表必须包含：
  - `.agents/rules/stage-guardrails.md` 的入口，适用场景为"阶段越界拦截、流程执行顺序、功能变更分类"
  - `.agents/protocols/pre-document-reading.md` 的入口，适用场景为"任务开始前文档读取、新会话上下文恢复"
- **AND** 规则体系索引表中包含 stage-guardrails.md

## MODIFIED Requirements

### Requirement: 角色Non-Goals增强

现有 developer、architect、tester、reviewer 角色定义中的 Non-Goals 需要补充阶段守卫相关约束。

#### Scenario: developer Non-Goals 补充
- **WHEN** 查阅 developer.md
- **THEN** Non-Goals 部分必须包含："不在代码实现阶段擅自变更架构决策；不在未读取技术方案文档的情况下开始编码"

#### Scenario: architect Non-Goals 补充
- **WHEN** 查阅 architect.md
- **THEN** Non-Goals 部分必须包含："不在方案设计阶段编写业务代码；不在需求未澄清时给出技术方案"

#### Scenario: tester Non-Goals 补充
- **WHEN** 查阅 tester.md
- **THEN** Non-Goals 部分必须包含："不在测试阶段自行修复缺陷（须反馈developer）；不在未读取需求和技术方案的情况下设计测试用例"

#### Scenario: reviewer Non-Goals 补充
- **WHEN** 查阅 reviewer.md
- **THEN** Non-Goals 部分必须包含："不在审查阶段直接修改业务代码；不在未读取前置文档的情况下给出审查结论"

## REMOVED Requirements

无。
