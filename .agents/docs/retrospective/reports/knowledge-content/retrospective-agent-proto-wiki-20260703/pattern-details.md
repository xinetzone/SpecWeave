---
id: "agent-proto-wiki-pattern-details"
title: "Agent通信协议Wiki - 模式详情"
source: "insight-extraction.md"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/reports/knowledge-content/retrospective-agent-proto-wiki-20260703/pattern-details.toml"
---
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
