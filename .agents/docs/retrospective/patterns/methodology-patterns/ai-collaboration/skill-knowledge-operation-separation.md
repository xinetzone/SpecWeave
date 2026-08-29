---
id: "skill-knowledge-operation-separation"
source: "../../../../../../docs/knowledge/learning/okf-bundles/chaos/ai-agent-skills/concepts/08-jira-skill-engineering.md#双技能拆分：操作与知识分离"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/skill-knowledge-operation-separation.toml"
maturity: "L2"
validation_count: 2
reuse_count: 0
documentation_level: "standard"
related_patterns:
  - "skill-three-part-structure"
  - "skill-five-elements-model"
  - "skill-intent-routing"
  - "progressive-context-disclosure"
---
> **提炼自**：jira-skill v3.28.0 双技能拆分实践（`jira-communication` 操作型 21 脚本 + `jira-syntax` 纯知识型）—— 单案例待验证

# 技能知识操作分离（Skill Knowledge-Operation Separation）

## 模式类型

方法论模式（AI协作/Skill架构设计）

## 成熟度

L2 已验证（jira-skill + mermaid-cmd 双案例；mermaid-cmd 静态测量 T1 下降 85.5%、T2=0；T3 动态质量回归待实测补充）

## 适用场景

当一个领域技能同时包含"操作面"（API/CLI 调用、脚本执行、状态变更）与"知识面"（语法参考、模板、验证规则、字段字典）时，将两者拆分为独立技能。

| 场景 | 是否适用 | 说明 |
|------|---------|------|
| 领域技能同时含操作与知识两面 | ✅ 核心场景 | Jira：操作（增删改查）+ 知识（Wiki 标记语法） |
| 纯知识型内容（语法表/模板/规范）被反复以只读方式使用 | ✅ 适用 | 知识面可独立成无工具技能 |
| 操作面脚本多、权限重（Bash/网络/写操作） | ✅ 适用 | 操作面技能声明 allowed-tools |
| 单职责轻量技能（仅操作或仅知识） | ❌ 不适用 | 拆分会过度碎片化 |
| 工具/脚本数量少（<5） | ⚠️ 部分适用 | 拆分的收益小于维护成本 |

## 问题背景

单体技能将操作面与知识面混装，会带来三重问题：

1. **上下文隔离失败**：纯写作任务（如编写 Jira Wiki 标记）加载整个技能时，会把操作型脚本、工具说明一并载入，浪费上下文窗口，甚至触发无关脚本加载
2. **权限膨胀**：知识型任务本不需要 Bash 执行权限或网络写权限，但单体技能会暴露全部 allowed-tools，扩大攻击面
3. **发版耦合**：语法表更新与 API 脚本更新被迫同步发版，低频知识变更被高频操作变更阻塞，或反向拖慢

jira-skill 的解法：拆分为 `jira-communication`（API 操作，allowed-tools: Bash(python:*) Bash(uv:*) Read Write，21 个脚本）与 `jira-syntax`（Wiki 标记语法/模板/验证，无 allowed-tools，纯知识）。

## 核心做法

1. **识别知识面与操作面**：盘点领域能力，区分"需要执行动作"的操作面与"只需查询参考"的知识面。jira-syntax 的语法表、模板、常见错误对照表即知识面；增删改查、状态转换、评论附件即操作面
2. **拆分为两类技能**：
   - 知识型技能：无 `allowed-tools`，只含参考内容（语法表、模板、验证清单），AI 在写作/查询任务中仅读不执行
   - 操作型技能：声明明确的 `allowed-tools`，含全部可执行脚本
3. **独立发版与版本管理**：两技能各自维护版本、各自发布（jira-skill 发布三个包族：完整版 + 两个独立技能版，用户可按需安装）
4. **操作型技能内部再分层**：脚本按职责分 core（高频核心）/workflow（流程）/utility（低频辅助），配合共享 lib 复用
5. **验证知识面正确性**：知识型技能配备独立验证（jira-syntax 的 `validate-jira-syntax.sh` 不与发布命令链式调用），保证参考内容本身准确

## 反例警示

| 错误做法 | 后果 |
|---------|------|
| 所有东西塞进一个"全功能"技能 | 纯写作任务加载操作脚本，上下文浪费、无关工具暴露 |
| 知识型技能也声明 allowed-tools | 权限膨胀，"只读参考"技能获得写执行能力 |
| 拆分过碎（每个语法表一个技能） | 技能数量失控，AI 发现与路由成本上升 |
| 知识面与操作面共用一份版本号强制同步 | 低频知识变更被高频操作变更阻塞 |
| 知识型技能没有独立验证 | 语法表/模板错误直接污染写作输出 |

## 检验标准

- [ ] 纯知识任务（只读参考）加载的技能不含 allowed-tools，不触发任何脚本加载
- [ ] 操作任务加载的技能仅包含完成任务所需的最小工具权限
- [ ] 知识面与操作面可独立发版、独立版本号
- [ ] 知识型技能参考内容有独立验证机制
- [ ] 同一领域任务能清晰判定"该走知识技能还是操作技能"

## 迁移验证

- **运维脚本库**（跨领域）：将"命令参考手册/配置模板"（知识）与"执行脚本"（操作）分离，文档查看不触发执行权限
- **数据分析技能**（跨领域）：数据字典、字段说明、统计口径（知识）与 ETL/清洗脚本（操作）分离，分析师查字典不加载执行工具
- **文档生成工具链**（跨领域）：Markdown/格式规范（知识）与渲染/发布脚本（操作）分离
- **极端场景**：工具数量极少（<5）或领域纯单一（只有知识或只有操作）时，分离收益为负，应保持单体——本模式失效的边界条件

> 单案例标注：目前仅有 jira-skill 一个完整案例。建议验证场景：将本模式应用到第 2 个含"操作+知识"双面的领域技能后升级为 L2。

### 验证场景建议（L1→L2 升级路径）

**升级标准**：① 第 2 个独立案例（非 jira-skill 变体）；② 领域同时有知识面与操作面，且知识面在纯只读任务中被独立使用；③ 拆分后收益可度量（上下文 Token/工具权限/独立发版，至少占一）；④ 边界条件被验证。

**候选评估**（2026-08-25 盘点 `.agents/skills/` 24 个 Skill）：
- **首选 `mermaid-cmd`**：知识面（安全编码六规则+模板+语法 Gotchas）与操作面（check-mermaid.py）结构同构 jira-skill，纯写作场景独立使用知识面 → 已实施逻辑拆分验证（见下）
- **次选 `source-code-to-okf-wiki`**：知识面为 prompt 模板而非语法/格式参考，拆分收益需论证
- **反向边界 `forum-posting`**：DOM 选择器知识仅在操作时使用，不满足前提②，印证「为拆而拆」反模式

**验证结果（2026-08-25）**：`mermaid-cmd` 已按逻辑分离实施——SKILL.md 新增 §4.5「知识面与操作面分离」加载分层，纯写作场景仅加载知识面（六规则+模板），检查修复场景才加载操作面（check-mermaid.py）。

**测量结果（2026-08-25 静态实测，脚本 `.chaos/notebook/2026-08-25-mermaid-token-baseline.py`）**：

| 指标 | 对照组（拆分前全量） | 实验组（知识面） | 判定 |
|------|------|------|------|
| T1 Token 消耗 | 3979 | 575（下降 85.5%） | PASS（阈值 ≥20%） |
| T2 工具暴露数 | 10 | 0 | PASS |

T3 动态质量回归（2026-08-25 独立会话实测）：对照组与实验组一次写对率均为 9/9（100%），差距 0 次，无回归 → T3 PASS。T1/T2/T3 三项全通过，L2 状态最终确认（validation_count 2）。

#### 测试方案：Token 消耗与工具暴露数对比

**目标**：量化拆分收益（升级 L2 前提③）。H1：拆分后纯写作任务 Token 下降 ≥20%，工具暴露数降为 0。

**分组**：
- 对照组（拆分前全量 SKILL.md）：`git show HEAD~1:.agents/skills/mermaid-cmd/SKILL.md`；若无快照，手动剔除操作面（§5 check-mermaid.py 调用步骤）构造
- 实验组（拆分后知识面）：§6 六规则 + §9 Gotchas + §10 模板引用（即 §4.5 定义的知识面切片）

**指标**：
- T1 Token 消耗：tiktoken(cl100k) 静态测算，或动态会话 `usage.prompt_tokens`；tiktoken 不可用时以 `len(text)//2` 估算并标注
- T2 工具暴露数：文本中 `check-mermaid.py|python .agents/scripts|--fix|--path` 出现次数（动态实测 = AI 实际脚本调用次数），实验组应为 0
- T3 质量回归：同任务图表"一次写对率"，须无回归

**执行步骤**：
1. 静态测算：Python 脚本分别读对照组/实验组文本，输出 tokens 与工具暴露数（`count_tokens`/`count_tool_exposure` 两个函数，见本文件来源工程实践）
2. 动态实测（可选）：Trae 中用同一任务集（T-a 登录 flowchart / T-b 下单 sequenceDiagram / T-c 微服务架构图，均含中文节点与 `-->| "标签" |`、`<br/>`、`EN_ID ["中文"]`）各执行 2 次，记录 prompt tokens 与脚本调用次数
3. 工具暴露行为核对：实验组纯写作路径不得出现 check-mermaid.py 调用
4. 记录与判定（记录表：组/任务/T1/T2/T3）

**判定规则**：
- 通过：T1 下降 ≥20% 且 T2=0 且 T3 无回归 → 升级 L2（validation_count 1→2）
- 部分通过：T1 下降 <20% 但 T2=0 → 收益以权限收窄为主，升级但标注收益类型
- 不通过：T2>0 或 T3 回归 → 回修 §4.5 加载路由，不升级

**防混淆**：对照组/实验组用同一任务文本，仅加载内容不同；动态实测保持同模型同温度；静态测算以 tiktoken 为准。

#### T3 动态质量回归实测（一次写对率）

**目标**：验证知识/操作分离不降低纯写作任务图表质量。H1：实验组（知识面）一次写对率 ≥ 对照组（拆分前全量）。

**分组与执行**：对照组 = `git show HEAD:.agents/skills/mermaid-cmd/SKILL.md` 全文；实验组 = 知识面切片（§6+§9+§10 模板引用，切片脚本 `.chaos/notebook/2026-08-25-mermaid-context-slice.py`）。两组在不同 Trae 会话执行（防上下文污染）。任务集 T-a 登录 flowchart / T-b 下单 sequenceDiagram / T-c 微服务架构图（均含中文节点、`-->| "标签" |`、`<br/>`、`EN_ID ["中文"]`），每任务每组 3 次（共 18 份输出）。

**一次写对评分清单（9 项全过才算）**：
1. 代码块内无空行（§6 R1）
2. 含中文/空格/特殊字符（@#≥≤+）文本加双引号（§6 R2）
3. 文本不以列表标记开头（§6 R3）
4. 换行用 `<br/>` 而非 `\n`（§6 R4）
5. subgraph 用 `EN_ID ["中文标题"]`（§6 R5）
6. 边标签 `-->| "标签" |`（§6 R6）
7. 节点 ID 英文，大括号节点文本加引号（§9）
8. subgraph 嵌套 ≤3 层（§9）
9. 代码块围栏全小写 `mermaid`（§9）

**判定**：实验组一次写对率 ≥ 对照组且差距 ≤1 次 → 无回归（T3 PASS）；低 2 次及以上 → 知识面切片遗漏规则，回修 §4.5 重测。

## 与现有模式的关系

| 相关模式 | 关系 | 说明 |
|---------|------|------|
| [skill-three-part-structure.md](../../code-patterns/skill-three-part-structure.md) | 分层依据 | SKILL/references/scripts 信息分层是操作面内部组织的基础 |
| [skill-five-elements-model.md](skill-five-elements-model.md) | 互补 | 五要素定义单个技能文档质量，本模式定义"何时拆成两个技能" |
| [skill-intent-routing.md](skill-intent-routing.md) | 协同 | 拆分成多个技能/脚本后，用意图路由表引导 AI 选择 |
| [progressive-context-disclosure.md](progressive-context-disclosure.md) | 泛化→特化 | 上下文渐进式披露是通用原则，本模式是其"按技能粒度隔离"的具体实现 |
