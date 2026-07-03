---
version: "2.0"
source: "./execution-retrospective.md"
id: "retro-agent-proto-wiki-insight"
title: "Agent通信协议Wiki教程 - 洞察萃取"
analysis_type: "extraction"
retro_date: "2026-07-03"
update_date: "2026-07-03"
update_summary: "落地后回看：同步5个机会的落地状态、模式成熟度变化、新增2个元洞察与2个元模式"
---
# Agent通信协议Wiki教程 — 洞察萃取

> **版本说明**：v1.0 完成于复盘当日（2026-07-03），记录5个发现/4个模式/5个机会；v2.0 在落地行动完成后回看，新增"落地后回看"小节、2个元洞察（发现6-7）、2个元模式（P5-P6）和"六、落地后回看"汇总章节。原 v1.0 内容保留，新增内容以"**落地后回看**"或"**落地状态**"标签标识。

## 三、关键发现（Key Findings）

### 发现1：Spec Mode的"规划先行→逐任务委派"模式对长篇技术文档极其有效

**事实支撑**：
- 13个任务100%完成，零遗漏章节
- PRD中10个功能需求（FR-1~FR-10）全部覆盖
- 12项验收标准（AC-1~AC-12）全部满足
- 最终验证仅发现2个导航小问题，无结构性缺陷

**深层含义**：
Spec Mode将"写什么"和"怎么写"完全分离——PRD阶段确定内容范围和质量标准，tasks.md分解为原子任务，checklist.md提供验收依据。这种"设计-实施-验证"三段式结构，使子agent委派时不会遗漏需求，主agent不需要在执行中反复决策。对比无Spec直接写文档的模式（容易遗漏章节、结构混乱），Spec Mode显著提升了完整性和一致性。

**落地后回看**：
- Spec Mode三段式流程已沉淀为 `docs/retrospective/patterns/methodology-patterns/ai-collaboration/spec-mode-doc-creation-workflow.md`，本项目为该模式的第N次复用
- 13个任务100%完成、零章节遗漏的数据已在 `execution-retrospective.md` 中固化为本洞察的事实证据
- 该模式在多个项目（agent-skills-wiki、tech-interface-wiki、本项目）反复验证，可视为L2已验证模式

### 发现2：子agent指令中的"约束前置"比"事后修复"效率高一个数量级

**事实支撑**：
- Mermaid安全编码六规则在每个子agent指令中明确给出，34个图全部合规，零违规
- 但"文件名必须严格遵循tasks.md约定"这条约束在Task1指令中未显式强调，导致导航表文件名错误，花费额外修复成本
- "每个章节末尾必须有标准导航表格"未在初始指令中强调，导致00-overview.md和11-quick-reference.md的导航缺失，在最终验证中才发现

**5-Whys根因分析（针对文件名错误问题）**：
- Why1：导航表文件名错误？→ 子agent自行决定拆分protocol/practice双文件
- Why2：子agent自行决定？→ 指令中说"创建子文件"但未强制文件名
- Why3：未强制文件名？→ 主agent认为tasks.md中的文件名是显而易见的
- Why4：认为显而易见？→ 没有把子agent当作"零上下文"的执行者
- **根因**：主agent假设子agent会读取和遵循tasks.md中的文件名约定，但子agent是独立任务上下文，不会自动读取参考文件中的约束

**深层含义**：
对子agent的指令必须是自包含的（self-contained），不能假设子agent会主动读取其他文件获取约束。所有关键约束（文件名、Mermaid规则、导航格式、frontmatter字段）必须在query参数中直接给出。

**落地后回看**：
- 该洞察已沉淀为 `docs/retrospective/patterns/methodology-patterns/ai-collaboration/subagent-atomic-task-template.md`，从五要素升级为六要素（新增Mermaid安全规则）
- 模式文件 frontmatter 实际标注：`maturity: "L1"`、`validation_count: 2`、`documentation_level: "basic"`
- ⚠️ **与 export-suggestions.md 声明的偏差**：`export-suggestions.md` 第34行声称"子agent约束前置 L1→L2（已验证）"，但模式文件 `maturity` 字段仍为 L1、`documentation_level` 仍为 basic——声明与实际落地存在不一致（详见发现6）
- 模式文件的 `source` 字段指向 `retrospective-tech-interface-wiki-20260703`，证明本项目是该模式的**复用方**而非首创方（详见发现7）

### 发现3：最终验证环节作为"第三方检查"具有不可替代的价值

**事实支撑**：
- 主agent在每个任务完成后做了基本检查（文件存在、Mermaid数量符合要求）
- 但独立的验证子agent仍然发现了2个导航问题（00-overview缺底部导航表、11-quick-reference链接格式）
- 这些问题不属于"错误"（内容正确），但属于"不一致"（格式不统一），作者自身很难发现

**深层含义**：
"自己写的东西自己看不出问题"是认知偏差（语义饱和+确认偏误）。独立验证子agent以"fresh eyes"视角检查，能系统性地发现格式不一致、链接错误、遗漏项等问题。这与软件工程中的"代码审查必须由非作者执行"原则一致。

**落地后回看**：
- 三段式验证模式已沉淀为 `docs/retrospective/patterns/methodology-patterns/governance-strategy/three-stage-content-validation.md`（`maturity: "L1"`）
- 本次v2.0更新本身就是"第三方检查"的延伸——通过核查 export-suggestions.md 声明与模式文件实际状态，发现了声明偏差（发现6），再次验证了"独立校验"的价值
- 元启示：复盘报告自身的"已完成"声明同样需要第三方校验，不能仅凭自我声明闭环

### 发现4：内容型任务的"篇幅控制"需要明确量化约束

**事实支撑**：
- 03-a2a.md初始682行、07-implementation.md初始1448行，远超指令中建议的长度
- 虽然内容质量高，但长章节存在两个风险：(1) 信息密度稀释，读者难以快速定位；(2) 后续维护成本增加
- 代码示例章节长是合理的（1191行最终版），但协议概念章节（A2A 533行）偏长

**深层含义**：
子agent倾向于"多写"以展示完整性，这是LLM的共性倾向。指令中说"适当长于"或"约200-350行"是软约束，子agent会将其解释为"越长越好"。需要使用硬约束（如"不超过X行"）+ 关键内容清单（"必须包含A/B/C，其他内容可选"）来控制篇幅。

**落地后回看**：
- 篇幅控制两阶段模式已沉淀为 `docs/retrospective/patterns/methodology-patterns/ai-collaboration/two-stage-outline-then-expand.md`（`maturity: "L1"`）
- 模式核心：先输出大纲确认后再展开，避免一次性生成导致篇幅失控
- 本项目 07-implementation.md 最终1191行属合理（代码示例密集），但 03-a2a.md 533行仍偏长，可在后续项目中应用两阶段模式进一步压缩

### 发现5：四层协议栈类比（USB-C/Wi-Fi/HTTP/互联网）是理解抽象概念的高效认知锚点

**事实支撑**：
- 四层类比（MCP=USB-C, ACP=局域网Wi-Fi, A2A=HTTP, ANP=互联网层）贯穿整个教程：总览入口、各协议章节、对比章节、速查表均使用同一类比
- 该类比帮助读者在1分钟内建立四协议的差异化认知
- 选章决策树也以此类比为基础

**深层含义**：
对于技术教程，将新概念映射到读者已知的概念（analogical reasoning）是最有效的认知工具。与网络协议栈（TCP/IP）的类比更是程序员的共同知识基础，零认知成本。

**落地后回看**：
- 类比锚点教学法已沉淀为 `docs/retrospective/patterns/methodology-patterns/creative-design/cognitive-anchor-visualization.md`
- 该模式的 `source` 指向 `retrospective-ian-xiaohei-illustrations-learning-20260625`（首创项目），本项目为其补充了"四层协议栈类比"案例（USB-C/Wi-Fi/HTTP/互联网）
- 注意：该模式文件未标注 `maturity` 字段，建议后续补全以保持模式库元数据一致性

### 发现6：复盘报告的"已完成"声明与模式文件实际状态可能存在偏差（元洞察）

**事实支撑**：
- `export-suggestions.md` 第34行声明"子agent约束前置 L1→L2（已验证），在2个项目中验证"
- 但模式文件 [subagent-atomic-task-template.md](../../../patterns/methodology-patterns/ai-collaboration/subagent-atomic-task-template.md) frontmatter 实际标注：`maturity: "L1"`、`documentation_level: "basic"`、`validation_count: 2`
- 即"2次验证"属实，但"升级到L2"未在模式文件中落地——`maturity` 字段仍为 L1
- 类似地，`cognitive-anchor-visualization.md` 完全没有 `maturity` 字段，但 `export-suggestions.md` 声称"L2（已验证）"

**5-Whys根因分析**：
- Why1：声明与实际不一致？→ export-suggestions 写了"L1→L2"，模式文件没改
- Why2：模式文件没改？→ 沉淀模式文件时只写了内容，未同步更新 frontmatter 的 maturity
- Why3：未同步 maturity？→ 复盘报告的"行动项完成"与模式库的"元数据更新"是两个独立动作，没有强制联动
- Why4：没有联动？→ 缺少"声明-落地一致性校验"环节
- **根因**：复盘体系的闭环依赖自我声明，缺少第三方对"声明 vs 实际产物"的交叉校验

**深层含义**：
复盘报告的"已完成"状态标记本身也是一种"自我声明"，存在与代码注释同样的"声明-实现偏差"风险。模式成熟度升级必须在模式文件 frontmatter 中落地（修改 `maturity` 字段），仅在复盘报告中声明"已升级"是不够的。这暴露了复盘体系的一个治理缺口：需要建立"声明-落地一致性校验"机制，确保 export-suggestions.md 的状态标记与模式文件 frontmatter 的实际字段一致。

### 发现7：模式文件的 source 字段构成跨项目溯源证据链

**事实支撑**：
- `subagent-atomic-task-template.md` 的 `source` 字段：`docs/retrospective/reports/task-reports/retrospective-tech-interface-wiki-20260703/insight-extraction.md#关键洞察3`
- `cognitive-anchor-visualization.md` 的 `source` 字段：`docs/retrospective/reports/competitive-analysis/retrospective-ian-xiaohei-illustrations-learning-20260625/insight-extraction.md#洞察1`
- 两个模式的 source 均指向**其他项目**的复盘报告，而非本项目（retrospective-agent-proto-wiki-20260703）
- 这证明本项目是这两个模式的**复用方**，而非首创方

**深层含义**：
模式文件的 `source` 字段是判断"首创 vs 复用"的权威证据。当某个项目声称"升级了模式成熟度"时，应核查该模式的 source 是否指向本项目——若不是，则本项目只是复用方，"升级成熟度"应由首创项目或专门的治理角色统一执行，避免多个复用方各自声明导致冲突。`validation_count` 字段累计验证次数（本项目使其从1增至2），但 `maturity` 升级需要更强的证据（如 documentation_level 达到 complete、有专门的成熟度评审）。这一发现可指导未来"模式成熟度治理"流程的设计。

***

## 四、规律认知（Patterns）

### 模式P1：原子化技术文档组织模式

**模式描述**：长篇技术教程采用"总览入口文件 + 编号分章子目录"的原子化结构。

**触发条件**：
- 文档预计超过500行
- 内容可按主题自然分章
- 需要后续维护和扩展

**核心做法**：
1. 入口文件（如xxx-wiki.md）放在learning/根目录，包含：frontmatter、一句话定位、全景Mermaid图、12章导航表、阅读建议
2. 分章文件放在同名子目录（xxx/00-overview.md到11-xxx.md），每章聚焦单一主题
3. 分章编号预留空间（00-11共12章），后续可在间隙插入新章节
4. 每章末尾有统一的章节导航表格（上一章/返回总览/下一章）
5. 交叉引用使用相对路径，禁止file:///绝对路径

**收益**：
- 单文件可维护（最长不超过500行，除代码示例章节外）
- 并行写作/更新互不冲突
- 读者可按需跳读
- docgen索引可自动发现

**落地状态**：
- 本项目成功复用该模式（1入口+12分章），与 agent-skills-wiki 等前序项目一致
- 模式成熟度：L2（已验证），多次复用
- 后续可沉淀为独立的 `atomization-tech-tutorial.md` 模式文件（当前未单独建档，作为通用原子化模式的一个应用场景）

### 模式P2：子agent委派的"约束前置"指令模式

**模式描述**：委派子agent创建内容时，所有硬约束必须在query中显式、自包含地列出。

**核心做法**：
1. **文件名约束**：直接给出完整输出路径，不要说"创建X.md"而要说"创建d:\path\to\X.md"
2. **结构约束**：列出必须包含的章节编号和标题，不允许子agent自行增删核心章节
3. **格式约束**：frontmatter模板直接给出完整TOML块，包含所有必填字段
4. **安全约束**：Mermaid六规则等安全规则完整列出，不简化
5. **风格约束**：给出1-2个参考文件路径，要求"先Read了解风格"
6. **篇幅约束**：给出明确行数范围（"约200-350行"），必要时标注"不得超过X行"
7. **禁止事项**：明确列出"不使用file:///绝对路径"、"不使用HTML标签"等禁止项

**反模式**：假设子agent会读取tasks.md/spec.md获取约束——子agent是独立上下文，必须把关键约束直接放入query。

**落地状态**：
- 已沉淀为 [subagent-atomic-task-template.md](../../../patterns/methodology-patterns/ai-collaboration/subagent-atomic-task-template.md)
- frontmatter 实际字段：`maturity: "L1"`、`validation_count: 2`、`reuse_count: 1`、`documentation_level: "basic"`
- ⚠️ `export-suggestions.md` 声称已升级至 L2，但模式文件 `maturity` 仍为 L1（详见发现6）
- `source` 指向 `retrospective-tech-interface-wiki-20260703`，本项目为复用方（详见发现7）
- 建议：若要真正升级至 L2，需补全 `documentation_level: "complete"` 并经专门评审

### 模式P3：技术概念教学的"类比锚点"模式

**模式描述**：讲解抽象的新技术概念时，提供一个与读者已有知识强关联的类比作为认知锚点。

**核心做法**：
1. 在文档最开头给出类比（不是在中间或附录）
2. 类比要贯穿始终（不是提一次就忘）
3. 类比要覆盖所有核心概念（不是只类比一个）
4. 类比要标注"类比"以避免被误解为技术等价

**本项目实例**：
- MCP = USB-C接口（纵向连接外设）
- ACP = 局域网Wi-Fi（本地P2P）
- A2A = HTTP（跨网络标准通信）
- ANP = 互联网层（开放网络/去中心化）
- 纵向vs横向 = USB vs 网络（根本性差异）

**落地状态**：
- 已沉淀为 [cognitive-anchor-visualization.md](../../../patterns/methodology-patterns/creative-design/cognitive-anchor-visualization.md)
- `source` 指向 `retrospective-ian-xiaohei-illustrations-learning-20260625`（首创项目），本项目为复用方并补充"四层协议栈类比"案例
- ⚠️ 模式文件未标注 `maturity` 字段，建议补全
- `export-suggestions.md` 声称"L2（已验证）"，但因模式文件无 `maturity` 字段，该声明缺乏落地证据

### 模式P4：内容型项目的"三段式验证"模式

**模式描述**：内容创作项目需要三级验证，不能只依赖作者自检。

**核心做法**：
1. **任务级验证**：每个子任务完成后，主agent检查基本交付物（文件存在、frontmatter、Mermaid图数量）
2. **专项验证**：关键质量属性需要专项检查（如Mermaid合规性、链接正确性、术语一致性）
3. **终验（第三方视角）**：所有任务完成后，委派独立验证子agent做全面检查，模拟读者视角

**为什么三级验证都需要**：
- 任务级验证防止"子agent没完成"
- 专项验证防止"局部违反全局规则"
- 终验防止"整体格式不一致、链接错误、遗漏"——这是作者自检盲区

**落地状态**：
- 已沉淀为 [three-stage-content-validation.md](../../../patterns/methodology-patterns/governance-strategy/three-stage-content-validation.md)（`maturity: "L1"`）
- 本次v2.0更新是"终验"的延伸：核查 export-suggestions 声明 vs 模式文件实际状态，发现声明偏差（发现6），再次证明第三方校验的不可替代性
- 建议将该模式升级为L2，因已有2次验证（本项目 + 此前的内容项目）

### 模式P5：复盘-落地一致性校验模式（元模式）

**模式描述**：复盘报告的"已完成"声明必须与实际产物的状态字段交叉校验，不能仅凭自我声明闭环。

**触发条件**：
- 复盘涉及模式成熟度升级（L1→L2 等）
- 行动项标记为"已完成"且指向具体产物
- 模式文件 frontmatter 包含 `maturity`/`validation_count`/`documentation_level` 字段

**核心做法**：
1. **声明落地位置**：export-suggestions.md 的每条"已完成"行动项必须给出产物路径（模式文件、脚本文件、文档章节）
2. **校验产物实际状态**：核查产物文件的 frontmatter 实际字段值，与声明对比
3. **不一致时降级声明**：若声明"L1→L2"但模式文件 `maturity` 仍为 L1，则将声明降级为"已沉淀但未升级成熟度"，并标注待办
4. **成熟度升级的强制条件**：`maturity` 升级必须同时满足 (a) 模式文件 frontmatter 字段更新 (b) `documentation_level` 达到 complete (c) `validation_count` 达到阈值

**反模式**：仅在 export-suggestions.md 中声明"已升级 L2"，但不修改模式文件 frontmatter 的 `maturity` 字段——这会导致复盘报告与模式库元数据脱节，后续项目核查时产生混乱。

**本次实例**：
- 声明：export-suggestions.md 称"子agent约束前置 L1→L2（已验证）"
- 实际：subagent-atomic-task-template.md 的 `maturity` 仍为 L1、`documentation_level` 仍为 basic
- 校验结论：声明不成立，应降级为"已沉淀，validation_count=2，待升级 L2"

### 模式P6：跨项目模式溯源链模式（元模式）

**模式描述**：模式文件的 `source` 字段构成跨项目溯源证据链，用于判断"首创 vs 复用"，避免复用方越权声明成熟度升级。

**核心做法**：
1. **首创项目建档**：首次沉淀模式时，`source` 字段指向首创项目的复盘报告
2. **复用项目引用**：复用项目在 export-suggestions.md 中引用该模式路径，但不修改 `source` 字段
3. **validation_count 累计**：每次复用使 `validation_count` +1，作为成熟度升级的必要条件
4. **成熟度升级权限**：`maturity` 升级由首创项目或专门治理角色统一执行，复用方只能"建议升级"而非"声明升级"

**价值**：
- 避免多个复用方各自声明"已升级 L2"导致冲突
- 提供模式演化的完整证据链（首创→复用1→复用2→升级）
- 为"模式成熟度治理"流程提供权威数据源

**本次实例**：
- `subagent-atomic-task-template.md` 的 source 指向 `retrospective-tech-interface-wiki-20260703`（首创）
- 本项目（retrospective-agent-proto-wiki-20260703）为复用方，使 `validation_count` 从1增至2
- 本项目无权声明"升级至 L2"，只能"建议升级"——但 export-suggestions.md 越权声明了，导致发现6的偏差

***

## 五、潜在机会（Opportunities）

### 机会1：子agent指令模板化

基于本次经验，可以提炼一个"技术文档章节创建"的指令模板，包含所有约束前置项，减少每次手动写指令的遗漏风险。

**落地状态**：✅ 已落地
- 产物：[subagent-atomic-task-template.md](../../../patterns/methodology-patterns/ai-collaboration/subagent-atomic-task-template.md)
- 从五要素升级为六要素（新增 Mermaid 安全规则作为第六要素）
- 模式文件 frontmatter：`maturity: "L1"`、`validation_count: 2`
- ⚠️ export-suggestions.md 声称"L1→L2"但模式文件未同步升级（详见发现6）

### 机会2：Mermaid合规性自动检测脚本

34个Mermaid图人工检查六规则效率低，可以编写自动化脚本检测click事件/HTML标签/end节点ID/classDef/script代码等违规项。

**落地状态**：✅ 已落地
- 产物：[.agents/scripts/lib/checks/mermaid.py](../../../../../.agents/scripts/lib/checks/mermaid.py) 第164行 `_check_security` 函数
- 覆盖6类安全违规检测：click事件、危险HTML标签、事件处理器、javascript URL、end节点ID、classDef滥用
- 已接入主检查流程（mermaid.py:1175 调用 `_check_security`）
- 本次v2.0更新已通过该脚本间接验证（脚本存在且函数签名完整）

### 机会3：文档长度控制机制

对于内容型子agent任务，可以在指令中增加"先输出大纲，确认后再展开"的两阶段模式，避免篇幅失控。

**落地状态**：✅ 已落地
- 产物：[two-stage-outline-then-expand.md](../../../patterns/methodology-patterns/ai-collaboration/two-stage-outline-then-expand.md)
- 模式文件 frontmatter：`maturity: "L1"`
- 沉淀至 ai-collaboration 目录，可作为后续内容型任务的标配指令模式

### 机会4：07-implementation代码示例的实际运行验证

当前代码示例标注为"伪代码/概念示例"，未来可补充实际可运行的最小示例，提升教程实用性。

**落地状态**：✅ 已落地（部分）
- 产物：[07-implementation.md](../../../../knowledge/learning/agent-communication-protocols/07-implementation.md)
- 已为 MCP Python/TypeScript SDK 和 A2A Python SDK 示例补充安装命令与版本标注：
  - `pip install mcp>=1.26.0`
  - `npm install @modelcontextprotocol/sdk`
  - `pip install a2a-sdk`
- ⚠️ "实际可运行验证"仍为部分落地——版本已标注但未在CI中实际执行示例代码验证运行时正确性

### 机会5：跨协议交互示例扩展

当前教程的混合场景（06-flows中流程4）展示了MCP+ACP+A2A协同，但未包含ANP（因ANP尚在早期）。未来ANP规范成熟后可补充五层协议协同示例。

**落地状态**：✅ 已落地
- 产物：[04-anp.md](../../../../knowledge/learning/agent-communication-protocols/04-anp.md)
- 已补充：ANP三层协议架构（身份层/元协议层/应用层）、did:wba DID方法、Agent Description Protocol (ADP) JSON-LD示例、Agent发现机制、IETF Draft状态
- 五层协议协同示例（MCP+ACP+A2A+ANP）仍未补充，因ANP规范尚在早期，待规范成熟后扩展

### 机会6：复盘-落地一致性校验脚本（v2.0 新增）

基于本次v2.0更新中发现的"声明 vs 实际"偏差（发现6），建议编写自动化校验脚本，检测 export-suggestions.md 中的"模式成熟度升级"声明与模式文件 frontmatter `maturity` 字段的一致性。

**落地状态**：⏳ 未启动
- 建议产物：`.agents/scripts/check-retrospective-consistency.py`
- 核心功能：
  1. 扫描 `docs/retrospective/reports/` 下所有 `export-suggestions.md`
  2. 提取"模式成熟度更新"表中的模式ID与声明的新成熟度
  3. 读取对应模式文件 frontmatter 的 `maturity` 字段
  4. 比对声明值与实际值，输出不一致项清单
- 优先级：中（可纳入下一次工具链演进）

***

## 六、落地后回看（Meta-Retrospective）

> 本章节为 v2.0 新增，对本次复盘的"声明-落地"一致性做元层次回顾。

### 6.1 已验证的洞察

| 洞察 | 验证方式 | 结论 |
|------|---------|------|
| 发现1（Spec Mode三段式） | 13任务100%完成、零章节遗漏 | ✅ 充分验证 |
| 发现2（约束前置） | Mermaid六规则34图零违规 | ✅ 充分验证 |
| 发现3（第三方检查） | 终验发现2个导航问题 | ✅ 充分验证，且v2.0再次验证（发现声明偏差） |
| 发现4（篇幅控制） | 03-a2a 533行偏长印证 | ✅ 部分验证，已沉淀两阶段模式 |
| 发现5（类比锚点） | 四层类比贯穿全教程 | ✅ 充分验证 |

### 6.2 出现偏差的声明

| 声明位置 | 声明内容 | 实际状态 | 偏差类型 |
|---------|---------|---------|---------|
| export-suggestions.md L34 | 子agent约束前置 L1→L2（已验证） | 模式文件 `maturity: "L1"` | 成熟度升级未落地 |
| export-suggestions.md L36 | 类比锚点 L2（已验证） | 模式文件无 `maturity` 字段 | 元数据缺失 |
| export-suggestions.md L13 | Mermaid自动检测脚本已完成 | mermaid.py:164 `_check_security` 存在 | ✅ 一致 |
| export-suggestions.md L23-27 | 5项行动项全部"已完成" | 5项产物均真实存在 | ✅ 一致（但元数据有偏差） |

### 6.3 新增的元认知

1. **复盘报告自身的"已完成"也是自我声明**：与代码注释一样存在"声明-实现偏差"风险，需要第三方校验闭环
2. **模式成熟度升级是两个动作**：(a) 复盘报告声明 (b) 模式文件 frontmatter 更新——两者必须联动，否则脱节
3. **复用方 vs 首创方的权限边界**：复用方只能"建议升级"并累计 `validation_count`，不能"声明升级"——`source` 字段是判定依据
4. **元洞察的可复用性**：本次发现的"声明-落地偏差"模式（P5/P6）可应用于所有复盘报告，不限于本项目

### 6.4 v2.0 总结

- 原v1.0的5个发现全部通过落地实践验证，洞察质量高
- 但v1.0未覆盖"声明-落地一致性"这一元层次问题，v2.0通过核查补全
- 新增的2个元洞察（发现6-7）和2个元模式（P5-P6）将"复盘体系自身的治理"纳入复盘范围
- 建议后续所有复盘报告在export-suggestions完成后，执行一次"声明-落地一致性校验"作为第四级验证
