---
id: "skill-intent-routing"
source: "../../../../../../bundles/chaos/ai-agent-skills/concepts/08-jira-skill-engineering.md#意图映射 + ../../../../../../bundles/chaos/ai-agent-skills/libs/tests/agent-rules-skill/skills/agent-rules/SKILL.md#Scripts"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/skill-intent-routing.toml"
maturity: "L2"
validation_count: 2
reuse_count: 0
documentation_level: "standard"
related_patterns:
  - "skill-discovery-protocol"
  - "lazy-loading-pattern"
  - "skill-knowledge-operation-separation"
  - "skill-three-part-structure"
---
> **提炼自**：jira-skill SKILL.md 意图映射表（F-016）+ agent-rules-skill SKILL.md Scripts 表 —— 双案例验证

# 技能意图路由（Skill Intent Routing）

## 模式类型

方法论模式（AI协作/Skill内容组织）

## 成熟度

L2 已验证（jira-skill + agent-rules-skill 双案例）

## 适用场景

当一个技能包含多个脚本/命令（≥5），且 SKILL.md 需要引导 AI 在任务中快速选择正确脚本时，用"用户意图 → 脚本"映射表取代逐脚本讲解。

| 场景 | 是否适用 | 说明 |
|------|---------|------|
| 多脚本技能（≥5 脚本） | ✅ 核心场景 | jira-skill 21 脚本、agent-rules-skill 13 脚本 |
| 一个脚本覆盖多个意图 | ✅ 适用 | jira-issue.py 同时覆盖 work/qa/get |
| 脚本文件名与用户意图不直观对应 | ✅ 适用 | 意图用用户语言表达 |
| 单脚本/单命令技能 | ❌ 不适用 | 无路由必要 |
| 脚本少且文件名自明（<5） | ⚠️ 部分适用 | 简单清单即可，无需完整映射表 |

## 问题背景

多脚本技能若在 SKILL.md 中逐个讲解每个脚本，会出现：

1. **选择困难**：AI 面对 N 个脚本不知道用哪个，容易选错（如"记录工时"误用 `jira-issue.py get`）
2. **上下文膨胀**：21 个脚本逐一说明消耗大量 Token，挤占实际任务上下文
3. **意图-实现错位**：用户说"处理这个 ticket"，脚本叫 `jira-issue.py work`——文件名与用户意图不总是直观对应
4. **重复讲解**：脚本说明与 `references/` 明细重复，SKILL.md 变长

jira-skill 的解法：SKILL.md 提供"用户意图 | 脚本调用"映射表（分诊→`jira-issue.py work`、QA→`jira-issue.py qa`、状态变更→`jira-transition.py do`、记录工时→`jira-worklog.py`），AI 按意图路由而非浏览全部脚本。agent-rules-skill 同样在 SKILL.md 提供 "Scripts | Purpose" 表（13 脚本：`generate-agents.sh`→生成 AGENTS.md、`verify-commands.sh`→验证命令可执行等）。

## 核心做法

1. **按用户意图组织映射表**：列用"用户要做什么"（分诊/创建/搜索/记录工时），而非脚本文件名或实现术语
2. **一意图一行、意图互斥**：每个意图映射到明确的脚本调用；一个脚本覆盖多意图时拆成多行（jira-issue.py 拆 work/qa/get 三行）
3. **补充自动触发条件**：列出无需用户显式表达的触发信号（jira-skill：出现 Jira URL 或 `PROJ-123` 格式 issue key 即触发）
4. **脚本明细下沉 references/**：SKILL.md 只保留映射表，脚本完整参数/选项放 `references/` 按需读取
5. **配合脚本分层**：映射表指向 core/workflow/utility 分层的脚本，而非扁平清单
6. **为破坏性操作标注 dry-run/验证入口**：映射表中对状态变更等破坏性意图指向支持 `--dry-run` 的脚本

## 反例警示

| 错误做法 | 后果 |
|---------|------|
| 用"文件名清单"代替意图映射 | AI 靠文件名猜用途，意图-实现错位仍在 |
| 映射表过细（每个子命令一行） | 表太长失去路由意义，退化为脚本文档 |
| 只有映射表没有自动触发条件 | 用户不显式说意图时（如直接贴 URL）无法路由 |
| 映射表与脚本实现脱节 | 脚本改名/拆分子命令后映射表过期，AI 调错脚本 |
| 将脚本完整文档内联进映射表 | 上下文膨胀，违背路由目的 |

## 检验标准

- [ ] SKILL.md 中 AI 能在 1 次查表内从用户意图定位到目标脚本
- [ ] 映射表的"用户意图"列使用用户语言而非实现术语
- [ ] 所有高频意图（≥80% 使用）均有映射条目
- [ ] 脚本明细在 references/ 中，SKILL.md 未逐脚本展开
- [ ] 映射表与 scripts/ 目录结构同步，脚本变更时映射同步更新

## 迁移验证

- **运维脚本库**（跨领域）：将"重启服务/查看日志/扩容节点"等运维意图映射到对应脚本，而非让 AI 浏览全部运维脚本
- **数据分析技能**（跨领域）：把"做透视/查分布/跑回归"映射到数据分析脚本，分析任务按意图直达
- **文档生成工具链**（跨领域）：把"生成导航/刷新看板/校验链接"映射到 docgen 脚本族
- **极端场景**：用户意图模糊（只说"处理一下"）时，映射表应提供默认/兜底路由；工具数量少时映射表退化为简单清单即可

## 与现有模式的关系

| 相关模式 | 关系 | 说明 |
|---------|------|------|
| [skill-discovery-protocol.md](skill-discovery-protocol.md) | 层级互补 | 发现协议解决"项目有哪些技能"（跨技能路由），本模式解决"单个技能内选哪个脚本"（技能内路由） |
| [lazy-loading-pattern.md](lazy-loading-pattern.md) | 支撑 | 按需加载是意图路由的机制基础——AI 按意图查表后才加载目标脚本 |
| [skill-knowledge-operation-separation.md](skill-knowledge-operation-separation.md) | 协同 | 技能拆分后（操作/知识），操作技能内部仍需意图路由组织多脚本 |
| [skill-three-part-structure.md](../../code-patterns/skill-three-part-structure.md) | 配套 | SKILL.md 承载映射表、references/ 承载脚本明细，符合三段式结构 |
