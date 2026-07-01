---
id: "retrospective-specforge-insight-20260629-export"
source: "https://forum.trae.cn/t/topic/2000"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/competitive-analysis/retrospective-specforge-insight-20260629/export-suggestions.toml"
---
# 导出建议：改进项落地路径

## 高优先级行动项

### 行动1：实现阶段守卫机制

**目标**：为feature-development工作流增加阶段边界硬约束，防止AI跨阶段操作。

**落地步骤**：
1. 在[feature-development.md](../../../../../.agents/workflows/feature-development.md)中新增"阶段守卫"章节，定义标准阶段序列和每个阶段的允许/禁止操作
2. 在AGENTS.md的启动协议中增加阶段守卫检查规则
3. 为每个阶段定义明确的"进入条件"和"退出标准"

**验收标准**：AI在需求阶段被要求写代码时，能主动拦截并提示"当前为需求阶段，请先完成需求澄清"。

### 行动2：增加前置文档强制读取检查点

**目标**：确保每个角色开始工作前已读取必要的前置文档。

**落地步骤**：
1. 为feature-development.md的每个步骤增加"前置文档"检查项
2. 明确每个步骤开始前必须确认读取的文档清单
3. 将此规则纳入developer/architect/tester/reviewer的角色定义

**验收标准**：developer开始编码前，输出中包含"已读取：技术方案文档、任务分解清单、开发规范"的确认。

### 行动3：增加功能演进分支

**目标**：区分新功能、功能扩展、功能重构三类变更的处理流程。

**落地步骤**：
1. 在feature-development.md中新增"功能演进"章节
2. 定义三类变更的判定标准和对应流程
3. 明确功能扩展的轻量流程（影响分析→增量方案→增量实现→回归测试）
4. 明确功能重构的重量流程（方案重审→全量影响评估→全量回归）
5. 萃取为独立的方法论模式

**验收标准**：当用户说"给X加个Y功能"时，AI能自动判断变更类型并选择对应流程。

## 中优先级行动项

### 行动4：BUG修复回归测试闭环

**目标**：每个BUG修复后自动生成回归测试，防止复发。

**落地步骤**：
1. 在[workflows/testing.md](../../../../../.agents/workflows/testing.md)中增加"BUG修复回归测试"章节
2. 在[roles/developer.md](../../../../../.agents/roles/developer.md)中增加"修复后提交回归测试"的职责
3. 在[roles/tester.md](../../../../../.agents/roles/tester.md)中增加"验证回归测试覆盖"的检查项
4. 考虑新增一个check-bug-regression.py脚本（可选）

**验收标准**：每个BUG修复PR中包含针对该BUG的测试用例。

### 行动5：萃取苏格拉底引导提问模式

**目标**：将引导式提问方法论形式化为可复用模式。

**落地步骤**：
1. 在[patterns/methodology-patterns/ai-collaboration/](file:///d:/spaces/SpecWeave/docs/retrospective/patterns/methodology-patterns/ai-collaboration/)下新增socratic-questioning.md
2. 包含五项核心原则（选项优先、单维度聚焦、解释附带、推荐引导、迭代允许）
3. 提供正反例对比
4. 更新CATEGORIES.md索引

**验收标准**：AI在需求不清时，自动使用引导式提问而非开放式大问题。

## 低优先级行动项

### 行动6：编写贯穿式教学案例

**目标**：用一个完整案例串联所有角色/协议/工作流。

**落地步骤**：
1. 选择"用户登录功能"作为贯穿案例
2. 从需求提出到最终上线，按角色分工展示每个阶段的输入/输出/交互
3. 在docs/下新增guides/tutorials目录存放

**备注**：此为文档完善项，不影响核心机制，可在高/中优先级项完成后进行。

### 行动7：增强AGENTS.md显式指令入口

**目标**：让用户能通过关键词直接触发指令集。

**落地步骤**：
1. 在AGENTS.md上下文路由表中增加"常用指令快捷入口"区域
2. 列出retrospective/insight/export-report/atomization/atomic-commit五个指令集的触发关键词
3. 保持现有自动路由能力不变，显式入口是补充而非替代

**备注**：简单改动，可在其他工作完成后顺便做。

## 不建议行动的项

| 项目 | 原因 |
|------|------|
| 将AGENTS.md改为13步刚性Skill流水线 | 团队协作需要灵活性，刚性流水线适合个人场景 |
| 在需求阶段禁用技术术语 | 团队成员有技术背景，技术可行性讨论应尽早介入 |
| 所有问题都改为ABC选项 | 团队沟通效率高，选项式引导适合新手不适合专业协作 |
| 在报名帖/Demo帖中提及SpecForge | SpecWeave是独立自研体系，无需在参赛帖中引入对比 |

## 推荐执行顺序

```
1. 行动2（前置文档读取）→ 最小改动，立即见效
2. 行动1（阶段守卫）→ 核心机制增强
3. 行动3（功能演进分类）→ 流程补全
4. 行动4（BUG回归测试）→ 质量闭环
5. 行动5（引导提问模式）→ 交互优化
6. 行动7（显式指令入口）→ 小改动
7. 行动6（贯穿案例）→ 大文档，最后做
```

建议行动1-3可以在一个Spec中打包实现（均为feature-development工作流增强），行动4-5分别独立实现，行动6-7择机进行。
