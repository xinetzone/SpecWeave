---
id: retrospective-i-have-adhd-wiki-insights-20260728
title: i-have-adhd知识沉淀洞察与模式萃取（Wiki教程+二次验证）
source: "execution-retrospective.md I阶段洞察+E阶段模式萃取 + 二次验证审查4条新洞察+4个新L1模式"
analyzed_at: 2026-07-28
closed_loop_at: 2026-07-28
second_validated_at: 2026-07-28
type: insight-extraction
parent_report: ./README.md
status: archived-with-second-validation
methodology: seven-concepts-r-i-e-plus-closed-loop-plus-second-validation
total_insights: 8
total_patterns: 7
---

# 洞察提取与模式萃取

> 本文档包含i-have-adhd知识沉淀两轮执行（Wiki教程+文章分析）的8条核心洞察和7条可复用模式。所有洞察均已完成"改进建议→落地执行→验证"闭环，模式已合并/增强/独立入库到现有方法论模式库。**二次验证审查新增4条核心洞察和4个新L1执行模式**。

---

## 闭环状态总览

### Wiki教程轮洞察与模式（第一轮执行）

| 洞察 | 改进建议 | 落地状态 |
|------|---------|---------|
| 洞察1：主题簇合并委派 | 建立主题簇判定4标准 | ✅ 已增强现有模式 [medium-task-merged-delegation-strategy](../../../patterns/methodology-patterns/ai-collaboration/medium-task-merged-delegation-strategy.md)（validation_count 2→3，新增主题簇判定4标准） |
| 洞察2：文件名漂移契约缺口 | 两阶段索引维护+文件名硬约束 | ✅ 已升级现有模式 [navigation-hub-filename-contract](../../../patterns/methodology-patterns/ai-collaboration/navigation-hub-filename-contract.md)（L1→L2，validation_count 1→3，新增两阶段索引维护法）；Wiki链接已全部修正 |
| 洞察3：增值内容需显式标记 | 【SpecWeave补充】标识 | ✅ 已在Wiki 3处增值内容添加blockquote标记 |
| 洞察4：前次改进有效 | 复盘改进项追踪机制 | ✅ 验证归零，纳入委派模板标准实践 |

### 二次验证审查轮洞察与模式（第二轮验证，🆕）

| 洞察 | 改进建议 | 落地状态 |
|------|---------|---------|
| 洞察5：G4过程合规门缺失 | 引入G4过程合规门+验证任务checklist化+子代理自检清单 | ✅ 已萃取 [orchestration-execution-layering.md](../../../patterns/methodology-patterns/governance-strategy/orchestration-execution-layering.md) L1模式，含G4检查清单6项 |
| 洞察6：单案例L2模式确认偏误 | G3增加失败案例强制要求+V阶段固定攻击视角+二次验证SOP | ✅ 已萃取 [knowledge-crystallization-second-validation-sop.md](../../../patterns/methodology-patterns/governance-strategy/knowledge-crystallization-second-validation-sop.md) L1模式；2个L2模式已升级v2.0含失败案例 |
| 洞察7：执行模式半闭环缺口 | E阶段SOP增加执行模式独立入库要求 | ✅ 3条执行模式已全部独立入库governance-strategy目录 |
| 洞察8：模式成熟度与文档长度张力 | 核心层+扩展层分层架构推荐 | ✅ 4个新L1模式全部采用分层架构，速查表在文档开头1屏内 |

| 萃取模式 | 入库状态 |
|---------|---------|
| PM-TD-001 主题簇合并委派 | 🔄 合并增强 → medium-task-merged-delegation-strategy（L2，3次验证） |
| PM-LK-001 两阶段索引维护 | 🔄 合并增强 → navigation-hub-filename-contract（L2升级，新增两阶段法） |
| PM-WD-001 开源Wiki知识沉淀 | 🆕 互补模式 → 与现有 [external-tech-doc-wiki-structure](../../../patterns/methodology-patterns/document-architecture/external-tech-doc-wiki-structure.md)（web文档翻译型）形成互补，本模式为源码分析型Wiki |
| PM-OE-001 编排-执行分层法 | 🆕 独立入库L1 → [orchestration-execution-layering.md](../../../patterns/methodology-patterns/governance-strategy/orchestration-execution-layering.md) |
| PM-SA-001 风格锚定一致性法 | 🆕 独立入库L1 → [style-anchoring-consistency.md](../../../patterns/methodology-patterns/governance-strategy/style-anchoring-consistency.md) |
| PM-SC-001 强约束自检法 | 🆕 独立入库L1 → [strong-constraint-self-check.md](../../../patterns/methodology-patterns/governance-strategy/strong-constraint-self-check.md) |
| PM-SV-001 知识沉淀二次验证SOP | 🆕 独立入库L1 → [knowledge-crystallization-second-validation-sop.md](../../../patterns/methodology-patterns/governance-strategy/knowledge-crystallization-second-validation-sop.md) |

---

## 一、核心洞察（4条，均含G2四元组+闭环验证）

### 洞察1：主题簇合并委派平衡效率与上下文完整性

- **现象描述**：11个原子任务实际通过8次子代理调用完成，其中9/11（82%）的任务通过主题簇合并委派执行（Task3+4、Task5-8、Task9-10），所有合并委派均一次性通过验收无返工
- **证据引用**：执行日志显示，同主题章节合并委派时，子代理能在一个bounded context内保持术语统一、内容衔接自然；平均每次委派产出373行内容
- **根因分析**：Spec Mode"one subtask at a time"原则的初衷是质量控制，但强相关章节（如安装→配置→排障构成使用全链路）拆分过细会导致子代理丢失相邻章节上下文，产生术语不一致、内容重复、交叉引用断裂等问题。矛盾的本质是"原子性粒度"与"上下文完整性"之间的权衡，而非简单的"越细越好"
- **改进建议**：建立主题簇判定标准——满足以下任一条件即可合并委派：(a)共享同一源文件 (b)内容存在前后引用关系 (c)读者通常连续阅读 (d)术语体系需要统一；合并时必须在query中明确各章节边界和交叉引用要求
- **✅ 闭环落地**：主题簇判定4标准已写入 [medium-task-merged-delegation-strategy.md](../../../patterns/methodology-patterns/ai-collaboration/medium-task-merged-delegation-strategy.md) "主题簇判定标准"章节（含本次案例表格），validation_count从2更新为3，新增"主题簇"标签，并与navigation-hub-filename-contract建立双向关联。

---

### 洞察2：文件名漂移暴露规划-实现契约缺口

- **现象描述**：Task1创建README.md时预设的5个文件名与后续子代理实际创建的文件名不一致（如03-exception-scenarios.md→03-exceptions-and-checklist.md），在Task11最终质量验证阶段才发现并修正
- **证据引用**：5处文件名差异全部是子代理在创建文件时根据实际内容增加了描述性后缀（-and-checklist、always-on-、customization-and-troubleshooting、-extracted、-and-resources），这些变更使文件名更具描述性，但未通知主agent更新索引
- **根因分析**：tasks.md中只描述了章节主题，未将最终文件名作为硬约束；子代理根据内容自主调整文件名是合理的创作行为，但README索引在Task1中预先写死，缺少"文件名变更同步"机制。根因是规划阶段的"文件名约定"与实现阶段的"文件名自主"之间存在契约缺口
- **改进建议**：采用"两阶段索引维护"模式——(1)Task1的README只列章节标题和序号，不写死文件名；(2)每个章节子代理在创建文件的同一任务中同步更新README对应行；(3)最终运行link-check做全量验证；或tasks.md中明确标注每个章节的最终文件名作为子代理必须遵守的契约
- **✅ 闭环落地**：(1)5处文件名链接不一致已全部修正；(2) [navigation-hub-filename-contract.md](../../../patterns/methodology-patterns/ai-collaboration/navigation-hub-filename-contract.md) 从L1升级到L2，validation_count从1更新为3，新增案例3（本次文件名漂移事件），新增"两阶段索引维护法"实践增强章节，并与medium-task-merged-delegation-strategy建立双向关联。

---

### 洞察3：知识沉淀增值内容需显式标记区分

- **现象描述**：Wiki内容包含两类性质不同的内容：(a)原项目文档的中文整理翻译（忠实于源），(b)二次创作增值内容（Trae IDE适配、跨领域模式萃取、设计原理关联分析等原项目未涉及的内容）
- **证据引用**：08-patterns-extracted.md是完全的新增价值（方法论抽象），原项目SKILL.md只列规则未做模式提炼；04-installation-guide.md中5.11节Trae IDE适配基于Agent Skills标准推理补充，原项目INSTALL.md未提及Trae
- **根因分析**：七概念E阶段（萃取）天然要求超越原项目文档进行抽象，这是知识沉淀的核心价值——不是复制文档而是提炼可迁移方法论。但增值内容的正确性无法通过"与原项目对照"验证，需要独立的质量保障机制。当前Wiki未对两类内容做显式区分，读者无法判断哪些是原项目内容、哪些是二次创作
- **改进建议**：增值内容使用显式标记区分（如"> **【SpecWeave方法论补充】**"标识）；对非原文的推理补充内容，V阶段增加"正确性验证"视角；模式萃取等深度增值内容至少经过1次对抗审查
- **✅ 闭环落地**：Wiki 3处增值内容已添加blockquote标记：(1) [04-installation-guide.md 5.11节](../../../../knowledge/learning/03-agent-platforms-tools/i-have-adhd-wiki/04-installation-guide.md)（Trae IDE适配）、(2) [08-patterns-extracted.md章节头](../../../../knowledge/learning/03-agent-platforms-tools/i-have-adhd-wiki/08-patterns-extracted.md)（模式萃取全章）、(3) [09-faq-and-resources.md Q9](../../../../knowledge/learning/03-agent-platforms-tools/i-have-adhd-wiki/09-faq-and-resources.md)（设计原理关联）。

---

### 洞察4：前次复盘改进建议有效——质量问题归零

- **现象描述**：本次执行未出现前次复盘（文章分析任务）记录的4类质量问题：frontmatter缺失、HTML实体编码未解码、提取工具残留垃圾文字、错别字
- **证据引用**：Task11质量门验证中，frontmatter检查显示11个文件全部包含正确的YAML frontmatter（id/title/source三字段）；无HTML实体、垃圾文字、错别字问题；唯一发现的问题是文件名链接不一致
- **根因分析**：前次复盘的改进建议（子代理query中增加项目约定自检清单、内容提取任务强制包含清理步骤）在本次执行中得到了落实——每个子代理query都明确要求了YAML frontmatter、中文编写、无垃圾文字等规范。子代理按照明确指令执行，避免了前次的格式问题
- **改进建议**：建立"复盘改进项追踪"机制——每次复盘产生的改进建议应形成checklist项，在后续类似任务中验证执行效果；本次验证通过的改进项可升级为标准实践，纳入委派模板
- **✅ 闭环落地**：本次任务中前次复盘的4类质量问题（frontmatter缺失/HTML实体/垃圾文字/错别字）零复现，验证了"子代理query自检清单"的有效性。YAML frontmatter规范（id/title/source三字段）、中文编写要求、无垃圾文字清理步骤已纳入委派query标准模板。

---

## 二、可复用执行模式萃取（3条，均含G3四要素+📦入库状态）

### 模式PM-WD-001：开源项目Wiki知识沉淀流程

| 要素 | 内容 |
|------|------|
| **模式名称** | 开源项目Wiki知识沉淀（Open Source Project Wiki Documentation） |
| **触发场景** | 需要将external/libs/下的第三方开源库转化为系统性中文Wiki教程时 |
| **适用边界** | 项目已有一定文档基础（README/官方文档/源码注释），需要整理、翻译、补充、抽象为知识库 |
| **核心步骤** | 1. R阶段预读：通读核心文件（入口→配置→示例→测试）识别核心概念<br>2. PRD先行：生成spec.md+tasks.md+checklist三件套<br>3. 目录先行：Task1创建README索引和目录结构<br>4. 主题簇委派：按"理念→规则→使用→高级→FAQ"顺序，同主题章节合并委派<br>5. 质量门串联：G1(事实准确)→G2(分析完整)→G3(模式可迁移)<br>6. 索引同步：每个章节完成后更新README链接（或最终统一验证）<br>7. 模式萃取：E阶段提炼跨领域可复用模式<br>8. 最终验证：全量链接检查+frontmatter校验+checklist逐项核对 |
| **反模式** | ❌ 直接翻译所有文档不做增值抽象（变成文档翻译而非知识沉淀）<br>❌ 跳过PRD直接写内容（边想边写导致结构混乱）<br>❌ 子代理query不含源文件路径和质量标准（导致臆造内容）<br>❌ 所有章节单独委派无主题簇（割裂上下文，内容重复矛盾） |
| **迁移验证** | ✅ 第三方SDK接入文档中文化 ✅ 内部框架使用手册编写 ✅ 开源论文/规范解读知识库 ✅ 技术书籍章节编写 |
| **来源案例** | 本次i-have-adhd知识沉淀（11文件/2982行/72KB/43检查点全通过） |
| **📦 入库状态** | 🆕 互补候选模式。与现有 [external-tech-doc-wiki-structure](../../../patterns/methodology-patterns/document-architecture/external-tech-doc-wiki-structure.md)（web文档翻译型Wiki）形成互补——本模式面向**源码分析型Wiki**（核心信息来自SKILL.md源码+hooks实现+evals测试），流程中包含"预读源码识别核心概念"和"E阶段模式萃取"两个源码特有步骤。待后续第2次源码型Wiki任务验证后正式入库为独立模式。 |

---

### 模式PM-TD-001：主题簇合并委派

| 要素 | 内容 |
|------|------|
| **模式名称** | 主题簇合并委派（Topic Cluster Task Delegation） |
| **触发场景** | Spec Mode下存在多个内容强相关、共享上下文、存在前后引用的子任务时 |
| **主题簇判定标准** | 满足任一条件即可判定为同主题簇：(a)共享同一源文件 (b)内容存在前后引用关系 (c)读者通常连续阅读 (d)术语体系需要统一 |
| **核心步骤** | 1. 依赖分析：画出任务依赖图识别有向边<br>2. 主题簇识别：将强连通分量或线性链合并为一个主题簇<br>3. 委派打包：每个主题簇作为一个general_purpose_task调用，query中明确列出所有要创建的文件名和各自内容边界<br>4. 边界声明：声明"每个章节独立成文，交叉引用使用相对路径"<br>5. 批量验收：主题簇内所有章节一起验证术语一致性 |
| **反模式** | ❌ 机械地"一文件一任务"拆分（导致上下文丢失、术语不一致、内容重复）<br>❌ 过度合并（不相关主题塞给一个子代理，超出上下文窗口导致质量下降）<br>❌ 不声明章节边界（子代理把多章节合并成一个大文件） |
| **迁移验证** | ✅ API文档批量生成（同一资源多个端点） ✅ 教程系列编写（入门→进阶→高级） ✅ 多文件代码重构（同一模块多文件） ✅ 测试用例批量编写（同一功能正反案例） |
| **来源案例** | 本次Task5-8合并安装+持久化+评估+自定义（均源自INSTALL.md/hooks/evals且构成使用全链路），子代理返回质量一致无返工 |
| **📦 入库状态** | 🔄 合并增强到 [medium-task-merged-delegation-strategy.md](../../../patterns/methodology-patterns/ai-collaboration/medium-task-merged-delegation-strategy.md)：(1) validation_count 2→3（第3次验证案例）；(2) 新增"主题簇判定标准"章节（4条判定条件+本次案例表格）；(3) 新增"主题簇"标签；(4) 与navigation-hub-filename-contract建立双向关联。原PM-TD-001编号保留作为本次萃取的溯源标识。 |

---

### 模式PM-LK-001：两阶段索引维护防断链

| 要素 | 内容 |
|------|------|
| **模式名称** | 两阶段索引维护（Two-Phase Index Maintenance） |
| **触发场景** | 多文件文档项目中，索引文件（README/目录页/导航栏）需要预先创建，但具体文件名在实现阶段可能根据内容调整时 |
| **核心步骤** | 1. 阶段一（规划时）：README只列出章节标题和序号，不写死文件名；或使用占位文件名并标注"文件名以实际创建为准"<br>2. 阶段二（实现时）：每个章节子代理在创建md文件的同一任务中同步更新README对应行<br>3. 最终关卡（交付前）：运行link-check验证所有内部链接<br>4. 强制规则：子代理如创建的文件名与tasks.md规划不一致，必须在返回结果中明确报告 |
| **反模式** | ❌ Task1一次性写死所有文件名（导致文件名合理调整后索引断链）<br>❌ 所有链接留到最后统一检查修复（断链积累多，修复成本高且易遗漏）<br>❌ 子代理改文件名不报告（主agent无法同步更新索引） |
| **迁移验证** | ✅ 静态网站/博客目录页维护 ✅ 多章节书籍目录页 ✅ 组件库文档导航 ✅ Monorepo包索引维护 |
| **来源案例** | 本次Task1预设5个文件名与实际不一致，在Task11才发现修正，触发了本模式的萃取 |
| **📦 入库状态** | 🔄 升级增强到 [navigation-hub-filename-contract.md](../../../patterns/methodology-patterns/ai-collaboration/navigation-hub-filename-contract.md)：(1) 成熟度L1→**L2**；(2) validation_count 1→3（新增案例2/案例3）；(3) documentation_level basic→standard；(4) 新增"案例3：i-have-adhd Wiki教程"详细记录本次5处文件名漂移事件；(5) 新增"两阶段索引维护法"实践增强章节；(6) 与medium-task-merged-delegation-strategy建立双向关联。原PM-LK-001编号保留作为本次萃取的溯源标识。 |

---

## 二、二次验证审查核心洞察（4条🆕，均含G2四元组+闭环验证）

> 以下4条洞察来自第三轮二次验证审查，针对第一轮萃取的执行模式和L2方法论模式进行系统性审计后提炼。

### 洞察5：质量门体系"内容-centric"导致执行模式后半段系统性失效（G4过程合规门缺失）

- **现象描述**：3条执行模式（编排-执行/风格锚定/强约束自检）在审计中呈现共同特征——前半段（规划/准备/搜索）遵循度50-100%，后半段（验证/闭环/对比检查）遵循度0-50%。具体表现为：主代理信任子代理自报告跳过逐文件验证、风格锚定第⑤步对比检查完全缺失、强约束自检在模式入库后未执行第二次。
- **证据引用**：模式A遵循度55%（2/5步✅、3/5步⚠️）、模式B遵循度50%（2/5步✅、2/5步⚠️、1/5步❌）、模式C遵循度37.5%（0/4步✅、4/4步⚠️）；9项P0问题全部是验证环节遗漏导致。
- **根因分析**：七概念质量门（G1-G3+V门）全部聚焦产出物质量（事实准确性、洞察完整性、模式可迁移性、审查意见质量），没有定义过程合规标准。tasks.md中验证类任务仅写"验证"二字而无具体checklist，执行者缺乏明确的完成判定标准，倾向于快速扫过后标记完成。这是结构性缺口而非执行疏忽。
- **改进建议**：(1)引入G4过程合规门：任务完成前用checklist逐项确认执行模式被遵循；(2)验证类任务必须写checklist，禁止笼统写"验证结果"；(3)子代理返回须附自检清单，主代理逐项核实而非信任。
- **✅ 闭环落地**：已萃取 [orchestration-execution-layering.md](../../../patterns/methodology-patterns/governance-strategy/orchestration-execution-layering.md) L1模式，核心步骤第⑤步包含G4过程合规检查清单6项（YAML字段完整/x-toml-ref可解析/风格与锚点一致/无强约束残留/内容符合指令/无工具标签残留）。

---

### 洞察6：单案例萃取L2模式存在结构性"确认偏误闭环"，二次验证是必要纠偏机制

- **现象描述**：2个L2方法论模式在V1审查后仍存在显著盲区：行动优先范式遗漏非技术用户/创意写作/长对话/高风险决策4个边界场景；逆向适配模式遗漏3个必要前提（互惠性/跨多样性冲突/源社区验证）和AccessiBe等4个FTC罚款级别的重大失败案例。这些盲区在单轮V审查中未被发现，直到V2对抗审查才暴露。
- **证据引用**：V2审查行动优先范式产出5条新意见（全部采纳），逆向适配范式挖掘出4个真实失败案例+3个遗漏前提+7个早期预警信号；两个模式v1.0→v2.0新增内容约60-80行。
- **根因分析**：知识沉淀全链路（R→I→E→V）存在系统性确认偏误：R采集成功案例→I从成功提炼洞察→E从成功萃取模式→V检查内部逻辑一致性。整个链路无强制环节要求"寻找反例/失败案例"，G3仅要求"≥2个正向迁移案例"即通过，形成"成功→成功→成功"自我强化闭环。加上V1由同一执行代理在同一上下文完成，确认偏误进一步放大。
- **改进建议**：(1)G3质量门对创新类模式增加失败案例强制要求（≥1个真实失败案例）；(2)V阶段固定攻击视角"什么情况下会伤害用户/适得其反？"；(3)新L2模式入库后1-2周内按SOP安排二次验证。
- **✅ 闭环落地**：(1)已萃取 [knowledge-crystallization-second-validation-sop.md](../../../patterns/methodology-patterns/governance-strategy/knowledge-crystallization-second-validation-sop.md) L1模式，固化8个Task标准流程；(2)两个L2模式均已升级v2.0，行动优先补充4个边界场景+8个破规场景，逆向适配补充4个失败案例+3个前提+7个预警信号。

---

### 洞察7：执行模式萃取后未独立入库形成"知识沉淀半闭环"，严重限制复用性

- **现象描述**：第一轮萃取的3条执行模式（编排-执行分层法/风格锚定法/强约束自检法）在第一次元复盘中已完整描述（触发场景+核心步骤+反模式+迁移验证四要素），但均未创建独立模式文档入库，仅停留在元复盘报告的表格中。二次验证审计时，这些模式的定义只能回到原始复盘报告中查找。
- **证据引用**：validation-report.md 5.2节成熟度评估显示3条执行模式均为"无独立文档"状态，无法通过模式目录/索引检索，无法被成熟度管理脚本追踪，reuse_count永远为0导致L3升级不可能。
- **根因分析**：SpecWeave方法论模式有明确入库路径（patterns/methodology-patterns/子目录+TOML元数据+README索引），但"执行模式"（过程性知识，与"领域方法论"相对）没有对等的入库SOP。第一次元复盘中2个领域方法论模式自然走了入库流程，但3条执行经验因无明确存放目录和流程被遗漏。
- **改进建议**：(1)E阶段SOP增加执行模式入库检查项——所有命名模式必须独立入库，不允许仅在复盘表格中描述；(2)执行模式统一存放governance-strategy目录；(3)为执行模式建立与方法论模式对等的TOML元数据。
- **✅ 闭环落地**：3条执行模式已全部独立入库到governance-strategy目录：[orchestration-execution-layering.md](../../../patterns/methodology-patterns/governance-strategy/orchestration-execution-layering.md)、[style-anchoring-consistency.md](../../../patterns/methodology-patterns/governance-strategy/style-anchoring-consistency.md)、[strong-constraint-self-check.md](../../../patterns/methodology-patterns/governance-strategy/strong-constraint-self-check.md)，每个模式均有独立TOML元数据，README索引已同步更新。

---

### 洞察8：模式成熟度与文档长度存在内在张力，需要"核心层+扩展层"分层文档架构

- **现象描述**：两个L2模式在V2审查后文档显著增长：action-first从164行增长到约250行（+52%），reverse-adaptation从约130行增长到约280行（+115%），增加的内容包括失败案例、预警信号、边界场景、根因分析等。文档越成熟（边界越清晰、反例越充分），篇幅越长，与"极简分发""新人快速上手"原则形成矛盾。
- **证据引用**：validation-report.md 5.4节洞察4详细记录了此张力：新人阅读成本增加，想快速了解核心规则需跳过大量失败案例和历史版本信息；但过度精简又丢失边界信息导致误用。
- **根因分析**：当前模式文档采用单文件架构——核心规则、边界条件、失败案例、预警信号、版本历史全部堆叠在一个Markdown文件中。这种架构在L1阶段简洁高效，但随成熟度提升（L2→L3），反例和边界信息累积导致文档冗长，核心规则被淹没。
- **改进建议**：(1)采用"核心层+扩展层"分层架构：核心层（文档开头1屏内）保留最精简核心规则+判断流程+默认行为，确保1分钟可读完；扩展层（后续章节）包含失败案例、预警信号、版本历史等详细信息；(2)文档开头提供"速查表"。
- **✅ 闭环落地**：4个新L1模式全部采用分层架构，文档开头均有"速查表"章节（7行表格概括一句话定义、触发条件、铁律、核心数字），扩展层包含问题现象、核心思想（Mermaid图）、核心步骤（含checklist）、适用场景、失败案例、反模式、迁移验证等详细章节。此架构标准已写入二次验证SOP作为推荐实践。

---

## 三、二次验证新萃取执行模式入库详情（4条🆕，均含G3四要素+📦入库状态）

### 模式PM-OE-001：编排-执行分层执行法

| 要素 | 内容 |
|------|------|
| **模式名称** | 编排-执行分层执行法（Orchestration-Execution Layering） |
| **触发场景** | ≥5个子任务的复杂任务，涉及大量内容撰写+多阶段质量门+跨会话执行时 |
| **核心步骤** | ①主代理制定三件套（spec/tasks/checklist）→ ②逐任务委托子代理（明确bounded context）→ ③主代理验证结果+更新状态（含G4过程合规检查清单6项）→ ④通过质量门后推进下一任务 → ⑤最终统一验证收尾（含子代理自检清单逐项核实） |
| **反模式** | ❌ 主代理自己撰写所有长篇内容（对话膨胀）；❌ 一次性并行委托无依赖任务（状态混乱）；❌ 委托时不给出明确bounded context（结果不可预测）；❌ 信任子代理自报告不做独立验证（格式问题堆积） |
| **迁移验证** | ✅ 文档批量生成 ✅ 代码重构多模块修改 ✅ 数据分析报告撰写 ✅ 测试用例批量编写 |
| **来源案例** | i-have-adhd文章分析任务（5次子代理委托，首次应用遵循度55%暴露验证环节缺口，二次验证审计后补充G4检查清单） |
| **📦 入库状态** | 🆕 独立入库L1 → [orchestration-execution-layering.md](../../../patterns/methodology-patterns/governance-strategy/orchestration-execution-layering.md)，含G4过程合规检查清单6项、子代理bounded context模板、委托vs直接执行决策树、3个失败案例详细分析，validation_count=1 |

---

### 模式PM-SA-001：风格锚定一致性保证法

| 要素 | 内容 |
|------|------|
| **模式名称** | 风格锚定一致性保证法（Style Anchoring Consistency） |
| **触发场景** | 向已有知识库/代码库/文档库新增内容，需要与现有内容保持格式、风格、深度一致时 |
| **同目录锚定铁律** | 必须选择**同目录**现有条目作为锚点，禁止跨目录风格比较（P0-04误判教训：creative-design目录惯例用"核心概念"而非"问题背景"，跨目录比较导致误判） |
| **核心步骤** | ①确定目标目录 → ②读取1-2个同目录现有高质量条目作为风格锚 → ③识别隐式约定（5维度：章节标题命名/YAML字段/表格列格式/语言风格/深度粒度）→ ④按锚定风格撰写新内容 → ⑤对比检查一致性（5维checklist逐项打勾） |
| **反模式** | ❌ 只读抽象规范不看实际样例；❌ 凭记忆/印象直接写；❌ 跨目录选择锚点（导致风格误判）；❌ 写完不做对比检查（风格漂移无法自纠正） |
| **迁移验证** | ✅ 新增代码模块 ✅ API端点 ✅ 测试用例 ✅ 文档/博客等任何需一致性场景 |
| **来源案例** | i-have-adhd模式萃取（首次应用步骤⑤缺失导致风格漂移）+ 二次验证审计（发现跨目录比较误判P0-04，纠正后萃取同目录锚定铁律） |
| **📦 入库状态** | 🆕 独立入库L1 → [style-anchoring-consistency.md](../../../patterns/methodology-patterns/governance-strategy/style-anchoring-consistency.md)，含5维对比checklist、同目录锚定铁律、2个具体失败案例、锚点选择标准，validation_count=3 |

---

### 模式PM-SC-001：强约束语言自检启发式

| 要素 | 内容 |
|------|------|
| **模式名称** | 强约束语言自检启发式（Strong Constraint Self-Check） |
| **触发场景** | 撰写规则、规范、指南、checklist等包含约束性内容的文档时 |
| **3个强制检查点** | CP1：源文件V阶段修正后 → CP2：模式入库前（独立执行，不假设V阶段已覆盖）→ CP3：提示词/模板同步时 |
| **核心步骤** | ①搜索"必须/禁止/绝不/一定"等强约束词 → ②4个固定攻击视角追问反例（非目标用户/极端场景/与其他规则冲突/创意场景）→ ③如有反例，采用2类柔化模式（默认推荐+显式列举例外/条件触发表述）→ ④保留强约束的正当理由（元规则定义/安全关键场景/法律合规要求） |
| **反模式** | ❌ 用强约束语言表述有例外的规则（机械执行产生反效果）；❌ 约束语言模糊（"尽量""适当"无可执行标准）；❌ 只说规则不说例外；❌ V阶段修正源文件后不回溯更新下游萃取产物 |
| **迁移验证** | ✅ 编码规范 ✅ AI提示词规则 ✅ 团队流程规范 ✅ 安全规则 ✅ 操作手册 |
| **来源案例** | i-have-adhd V1阶段（修正analysis-report强约束但模式文档残留）+ 二次验证审计（发现V→E回环缺失，模式入库后强约束残留P0-08，补充3检查点机制） |
| **📦 入库状态** | 🆕 独立入库L1 → [strong-constraint-self-check.md](../../../patterns/methodology-patterns/governance-strategy/strong-constraint-self-check.md)，含3个强制检查点（CP1/CP2/CP3）、4个固定攻击视角表格、2类柔化模式、保留强约束正当理由4条、2个具体失败案例，validation_count=2 |

---

### 模式PM-SV-001：知识沉淀二次验证SOP

| 要素 | 内容 |
|------|------|
| **模式名称** | 知识沉淀二次验证SOP（Knowledge Crystallization Second Validation SOP） |
| **触发场景** | 新萃取的L2模式入库后1-2周内，或当单案例萃取模式需要系统性验证边界时 |
| **核心流程（8个Task）** | Task1：R阶段事实采集（重建执行时间线、产出清单、修复记录）→ Task2：执行模式合规审计（逐条评估遵循度）→ Task3：V阶段第二轮对抗审查（新视角攻击边界、找失败案例）→ Task4：遗漏问题审计+5-Whys根因分析（P0/P1/P2分级）→ Task5：模式成熟度评估（L1/L2/L3判定+升级路径）→ Task6：E阶段新模式入库（执行模式独立文档+SOP萃取）→ Task7：提示词模板/下游产物同步更新 → Task8：最终验证闭环 |
| **6类必查视角** | 非目标用户视角、极端/边缘场景视角、失败案例/反例视角、跨领域迁移视角、与现有模式冲突视角、元视角（审计自身是否犯同样错误） |
| **截断规则（防无限递归）** | 二次验证本身不再进行三次验证；二次验证发现的P0问题修复后不再独立审计修复过程；SOP模式本身作为L1实验性模式入库，需在后续2次二次验证实践中验证后才考虑L2升级 |
| **反模式** | ❌ 重复V1已发现的问题（审查视角重叠）；❌ 二次验证变成"挑刺大会"否定模式价值（目标是找边界而非否定）；❌ 无限递归验证（三次/四次验证）；❌ 审计自身不做自检（引入新错误） |
| **迁移验证** | ✅ 所有单案例萃取的L2方法论模式 ✅ 跨领域迁移类创新模式 ✅ 规范类/规则类模式 ✅ 提示词模板验证 |
| **来源案例** | 本次i-have-adhd知识沉淀二次验证（首个完整应用案例，8个Task全部完成，9项P0修复，4个新模式入库） |
| **📦 入库状态** | 🆕 独立入库L1 → [knowledge-crystallization-second-validation-sop.md](../../../patterns/methodology-patterns/governance-strategy/knowledge-crystallization-second-validation-sop.md)，含8个Task标准流程、6类必查视角、4个质量门（G1/G2/G3/G-V）标准、问题分级P0/P1/P2、截断规则防无限递归，validation_count=1 |

---

## 四、变更日志

| 日期 | 变更内容 |
|------|---------|
| 2026-07-28 | 初始版本：4条洞察+3条模式萃取完成 |
| 2026-07-28 | 闭环归档：(1) frontmatter增加status:archived/closed_loop_at/methodology字段；(2) 新增闭环状态总览表；(3) 每条洞察增加✅闭环落地验证记录；(4) 每条模式增加📦入库状态；(5) PM-TD-001→合并增强medium-task-merged-delegation-strategy(L2,3次验证)；(6) PM-LK-001→升级navigation-hub-filename-contract(L1→L2,新增两阶段法)；(7) PM-WD-001标记为互补候选模式待二次验证 |
| 2026-07-28 | 二次验证更新：(1) frontmatter增加second_validated_at/total_insights:8/total_patterns:7字段，status更新为archived-with-second-validation；(2) 闭环状态总览表拆分为"Wiki教程轮"和"二次验证审查轮"两个子表；(3) 新增洞察5-8共4条二次验证核心洞察（G4过程合规门缺失/确认偏误闭环/执行模式半闭环/分层文档架构），每条含G2四元组+闭环验证；(4) 新增PM-OE-001/PM-SA-001/PM-SC-001/PM-SV-001共4个新L1执行模式独立入库详情，每个含G3四要素+📦入库状态；(5) 新增3条执行模式从"表格描述"升级为"独立文档入库"的状态更新 |
