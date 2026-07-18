---
id: "retrospective-session-agents-md-violation-20260624-export"
title: "四、改进建议与行动计划"
source: "会话内用户纠错记录"
x-toml-ref: "../../../../../../../.meta/toml/.agents/docs/retrospective/reports/project-governance/process-and-compliance/retrospective-session-agents-md-violation-20260624/export-suggestions.toml"
---
# 四、改进建议与行动计划

## 4.1 改进建议

| 序号 | 问题 | 改进措施 | 优先级 | 预期效果 |
|------|------|---------|--------|---------|
| 1 | 系统级 Skill 提示与 AGENTS.md「必须首先读取」的隐式优先级冲突 | 在系统提示中或 AGENTS.md 顶部增加明确的分层规则——「若工作区存在 AGENTS.md，优先读取它，再根据其路由表确定需要加载哪些 Skill」 | 高 | 消除启动时的注意力竞争，确保 AGENTS.md 始终最先被读取 |
| 2 | 多 Skill 并行加载时「执行路径竞争」导致输出格式偏离 | 增加 Skill 加载前的语义去重检查——同一轮中不加载两个都声称「生成文档/报告/文件」的 Skill；或在 Skill 描述中增加互斥元数据 | 中 | 避免 consulting-analysis + docx 同时加载导致的格式冲突 |
| 3 | 纠错反馈后智能体只修症状不追溯根因 | 在纠错工作流中增加「根因诊断」步骤——收到纠错反馈后，先回答「为什么我犯了这些错误？缺少了哪些前置读取？」，再执行修正 | 高 | 避免「打地鼠」式修正循环，将纠错轮次从 N 次压缩为 1-2 次 |
| 4 | 短指令模式依赖上下文连续性，跨会话或上下文中断后失效 | 考虑在 AGENTS.md 中增加「短指令完整性检查」机制——收到短指令时，若上下文不完整，先主动确认当前项目状态再执行 | 低 | 降低跨会话短指令的误判风险 |

## 4.2 行动计划

| 优先级 | 改进项 | 具体措施 | 建议时间 | 状态 |
|--------|--------|---------|---------|------|
| 高 | AGENTS.md 启动协议强化 | 在 AGENTS.md 首行增加 `<!-- PRIORITY: READ FIRST - before any Skill or tool -->` 注释；在系统级规则中（如 user_rules）增加「收到任务后首先读取 AGENTS.md」的强制规则 | 立即 | 待规划 |
| 高 | 纠错反馈触发根因诊断 | 在 developer/reviewer 角色提示词中增加纠错工作流——收到纠错反馈 → 诊断知识缺口 → 读取缺失文档 → 执行全量修正 | 本轮会话内 | 待规划 |
| 中 | Skill 加载语义去重 | 在执行路径中增加检查：若已加载 consulting-analysis 或 report-generator 等报告类 Skill，则不加载 docx/pptx 等办公文档生成类 Skill | 下一迭代 | 待规划 |
| 低 | 短指令上下文完整性检查 | 当收到「复盘+洞察」「跟进行动项」等已注册短指令时，若未在启动时读取 AGENTS.md，先触发 AGENTS.md 读取再执行短指令 | 下一迭代 | 待规划 |

## 4.3 可复用模式登记

| 资产 | 描述 | 复用等级 | 说明 |
|------|------|---------|------|
| 根因诊断模式 | 纠错反馈触发后，先回答「为什么犯错、缺少什么知识」，再执行修正 | 直接复用 | 适用于所有智能体纠错场景，能显著压缩修正轮次 |
| Skill 语义互斥检查 | 在加载多个 Skill 前进行操作语义去重，避免竞争性 Skill 同时激活 | 按场景适配 | 适用于 consulting-analysis/docx、html-report/pptx 等语义重叠场景 |
| 启动协议分层优先级 | 明确 AGENTS.md（项目级）> Skill 工具（系统级）的启动读取顺序 | 直接复用 | 适用于所有包含 AGENTS.md 的项目 |

## 4.4 后续方向

```mermaid
flowchart LR
    NOW["当前：识别出 4 项错误根因<br/>制定了 4 项改进措施"] --> NEXT["短期<br/>AGENTS.md 启动协议强化<br/>纠错反馈触发根因诊断"]
    NEXT --> MID["中期<br/>Skill 语义互斥检查<br/>短指令上下文完整性检查"]
    MID --> FAR["长期<br/>形成智能体执行合规性<br/>自检与自愈机制"]
```

---

*数据来源：本轮会话实际执行记录*
