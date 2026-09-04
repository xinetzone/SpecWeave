# 《老子》传本源流谱系 OKF 知识包 - 产品需求文档（PRD）

## Overview
- **Summary**：在 `bundles/laozi-lineage/` 下构建一个符合 OKF v0.2 规范的开放知识包（Knowledge Bundle），系统调研《老子》从战国楚简到西汉帛书、汉简，再到传世注本的传本源流谱系。每个抄本/异文/方法均为独立概念文档，携带 YAML frontmatter（`type`/`title`/`sources`/`generated`/`verified`/`status`），正文每条事实性论断以脚注 `[^source-id]` 溯源至 frontmatter `sources` 条目，实现"可溯源、可审计、可机读"。
- **Purpose**：用户此前已表达对帛书版《道德经》发现史与版本源流的兴趣。本知识包将零散对话升级为结构化、可溯源的学术知识资产，使"哪个本子更早""避讳如何断代""德经为何在前"等问题有可核查的文献依据，而非凭记忆作答。
- **Target Users**：中国哲学/古典文献学研究者、简帛学爱好者、需要引用《老子》早期传本的 AI 智能体与知识图谱消费者。

## Goals
- 以 OKF v0.2 格式完整呈现《老子》传本源流谱系，覆盖至少 8 个关键传本节点（4 出土 + 4 传世）。
- 每条事实性论断可溯源到学术权威信源（专著、发掘报告、整理本、博物馆/高校机构页），`sources[].resource` 为可核查的具体文献（含 ISBN/DOI/机构 URL）。
- 运用七概念方法论知识沉淀链路（R→I→E→V）：R 采集客观事实、I 形成洞察、E 萃取可复用方法模式、V 对抗审查剔除过度断言。
- 产出 2 个可迁移的方法论概念：避讳断代法、传本源流重建法。
- Bundle 通过 OKF v0.2 一致性检查（§11）：每个 `.md` 含可解析 frontmatter 与非空 `type`，`index.md`/`log.md` 符合保留文件约定。

## Non-Goals (Out of Scope)
- 不做《老子》全文逐章校勘或白话译文（那是独立校注专著的体量）。
- 不覆盖所有传本（如唐宋数十种道藏本、敦煌残卷全目），只选谱系关键节点；次要传本在正文中提及但不单列概念。
- 不做思想史/哲学义理的深度阐发（除非异文本身直接影响断代或谱系判断）。
- 不构建运行时 Attested Computation（OKF §10）——本 bundle 属人文知识类型，无 SQL/代码计算需求。
- 不修改 `vendor/knowledge-catalog/`（third_party 只读子模块），仅遵循其 SPEC.md 格式规范。
- 不引入新的 Python/JS 依赖或工具链；纯 Markdown + YAML frontmatter。

## Background & Context
- **格式依据**：[vendor/knowledge-catalog/okf/SPEC.md](../../../../vendor/knowledge-catalog/okf/SPEC.md) 定义 OKF v0.2——目录树状 Markdown + YAML frontmatter，保留文件 `index.md`/`log.md`，`sources` 字段承载溯源，`generated`/`verified` 承载信任，`status`/`stale_after` 承载生命周期。
- **位置约束**：`vendor/knowledge-catalog/` 在 [vendor/AGENTS.md](../../../../vendor/AGENTS.md) 中登记为 `third_party` 子模块，明确"❌ 禁止本地修改"。OKF SPEC §3 允许 bundle 作为"larger repository 中的子目录"存在，故在主权区 `bundles/laozi-lineage/` 新建独立 bundle。
- **方法论依据**：七概念场景 4"知识沉淀/方法论"链路 R→I→E→V（见 [.agents/commands/seven-concepts.md](../../../../.agents/commands/seven-concepts.md) 流程 4）：R 采集案例事实 → I 本质发现 → E 模式萃取 → V 对抗验证 → 入库。
- **内容敏感度**：研究对象为公有领域古典文献与公开发表的学术成果，属 AGENTS.md 步骤 2.3 所定义的"公开内容（Public）"，走标准工作流。
- **学术背景**：《老子》传本在 20 世纪下半叶因三次重大出土发现（郭店楚简 1993、马王堆帛书 1973、北大汉简 2009 入藏）而根本改写了谱系认知；传世本以王弼注本（魏晋）为通行本之祖，河上公本系统为另一大支。避讳字（邦/国、恒/常）是断代关键硬证据。

## Functional Requirements
- **FR-1**：Bundle 根目录含 `index.md`（带 `okf_version: "0.2"` frontmatter）与 `log.md`，按 `manuscripts/`、`archaeology/`、`variants/`、`methodology/`、`references/` 五个子目录组织概念。
- **FR-2**：`manuscripts/` 下至少 8 个传本概念：郭店楚简本、帛书甲本、帛书乙本、北大汉简本、河上公注本、想尔注本、王弼注本、傅奕校定本。每个含年代、材质、字数/章数、避讳特征、篇序、完残程度、整理出版信息。
- **FR-3**：`archaeology/` 下含马王堆三号汉墓、郭店一号楚墓两个考古语境概念，含墓葬年代、墓主、出土位置、共存器物/文献。
- **FR-4**：`variants/` 下至少 4 个关键异文概念：邦/国避讳、恒/常避讳、德经/道经篇序、大器免成/晚成。每个呈现异文本身、各本对应字、断代/谱系意义、争议点。
- **FR-5**：`methodology/` 下含 2 个萃取模式概念：避讳断代法、传本源流重建法。每个含触发场景、核心步骤、反模式、迁移验证（G3 质量门）。
- **FR-6**：`references/` 下为每条学术信源建立概念文档，至少 10 条权威信源（高明、荆门市博物馆、国家文物局文献室、北大出土文献研究所、楼宇烈、饶宗颐、陈鼓应等），`resource` 字段含 ISBN/DOI 或机构 URL。
- **FR-7**：每个概念文档 frontmatter 含 `type`（必填）、`title`、`description`、`tags`、`generated: { by, at }`、`verified`、`status`、`sources`（正文引用时必含 `id`）。
- **FR-8**：正文每条事实性论断以 Markdown 脚注 `[^source-id]` 标注，脚注 label 与 `sources[].id` 一一对应；无来源支撑的推断必须显式标注为"学界推测"或"编者按"，不得伪装成事实。
- **FR-9**：概念间通过 bundle 相对路径 `/path/to/concept.md` 互相链接，形成谱系图可遍历的有向图；链接容忍断链（OKF §6.1），但关键父子/引用链接不应断。
- **FR-10**：`log.md` 按 ISO 8601 日期倒序记录 Creation/Update 条目。
- **FR-11**：V 阶段对抗审查结果显式记录——对有争议的断代（如河上公年代、想尔注作者、北大简出土地点缺失）在概念正文设"争议与不确定性"小节，`status` 视情况设为 `draft` 或在 `stable` 中标注争议，不得给出单一确定性断言。

## Non-Functional Requirements
- **NFR-1（可机读）**：所有 frontmatter 为合法 YAML，可被任意 YAML 解析器读取；`type` 值采用 PascalCase 描述性命名（`Manuscript`、`Archaeological Site`、`Textual Variant`、`Methodology Pattern`、`Reference`）。
- **NFR-2（可溯源）**：100% 的事实性论断有脚注引用；每个 `sources` 条目至少含 `resource` 与 `title`，学术专著优先含 `author` 与 ISBN。
- **NFR-3（一致性）**：通过 OKF §11 一致性三项检查（frontmatter 可解析、`type` 非空、保留文件合规）。
- **NFR-4（原子性）**：每个概念文件单一职责，不混合多个传本/异文；文件 < 500 行（遵循项目代码架构规则）。
- **NFR-5（语言）**：正文以中文为主，专有名词附英文/拼音（如 Wang Bi、Mawangdui）；脚注与信源标题保留原文。
- **NFR-6（可维护）**：`stale_after` 对时效性内容设为 2027-12-31（约一年半后复核），稳定文献可设更晚或不设。
- **NFR-7（无外部依赖）**：bundle 可被 `cat`/`git clone` 直接消费，无需 SDK 或构建步骤。

## Constraints
- **Technical**：纯 UTF-8 Markdown + YAML frontmatter；不允许 HTML/JS（除非为 OKF viewer 可选的 `viz.html`，本 bundle 不要求）；路径使用 POSIX 风格相对路径。
- **Business**：所有信源必须是公开可核查的学术文献，不得使用匿名博客、百度知道、未注明出处的网络帖；网络信源仅限博物馆/高校/出版社官方页。
- **Dependencies**：格式依赖 `vendor/knowledge-catalog/okf/SPEC.md`（只读引用，不修改）；方法论依赖 `.agents/commands/seven-concepts.md` 场景 4 链路。
- **Location**：`bundles/laozi-lineage/`（用户确认，主权区新建顶层目录）。
- **Vendor 边界**：严禁写入 `vendor/knowledge-catalog/` 任何文件。

## Assumptions
- 用户期望"全面"指谱系关键节点覆盖，而非穷尽所有传本（Non-Goals 已界定）。
- 学术权威信源的准确出版信息（ISBN、年份、页码）可通过网络检索核实；若无法核实，标注"待核"而非编造。
- 我（agent）作为 `generated.by`（遵循 OKF §7 actor 约定，形如 `reference_agent/trae-glm`），V 阶段对抗审查由我以 `process:seven-concepts-V` 身份执行，最终 `human:<user>` 审阅后升级为 human-reviewed。
- 出土简帛文献的释文以正式出版整理本为准，不直接引用未刊布材料。
- 避讳断代逻辑基于汉代避讳制度的既有学术共识（邦→国避高祖刘邦、恒→常避文帝刘恒、启→开避景帝刘启、彻→通避武帝刘彻）。

## Acceptance Criteria

### AC-1: Bundle 结构合规
- **Given**：`bundles/laozi-lineage/` 目录已创建
- **When**：检查目录结构
- **Then**：存在 `index.md`、`log.md` 及 `manuscripts/`、`archaeology/`、`variants/`、`methodology/`、`references/` 五个子目录，每个子目录含 `index.md`
- **Verification**: `programmatic`（文件系统检查 + 人工审查目录列表）

### AC-2: OKF v0.2 一致性通过
- **Given**：bundle 下所有非保留 `.md` 文件
- **When**：逐个解析 YAML frontmatter
- **Then**：每个文件含可解析 frontmatter 块、非空 `type` 字段；`index.md`/`log.md` 无 frontmatter（根 `index.md` 例外，可含 `okf_version`）；无文件违反保留文件名
- **Verification**: `programmatic`（YAML 解析脚本/人工逐文件检查）

### AC-3: 传本覆盖度
- **Given**：`manuscripts/` 目录
- **When**：列出概念文件
- **Then**：至少包含郭店楚简本、帛书甲本、帛书乙本、北大汉简本、河上公注本、想尔注本、王弼注本、傅奕校定本共 8 个传本概念
- **Verification**: `programmatic`（文件存在性检查）

### AC-4: 每条事实性论断可溯源
- **Given**：任意概念正文
- **When**：扫描正文中的事实陈述与脚注
- **Then**：每条事实性论断带 `[^id]` 脚注，且 `id` 在 frontmatter `sources` 中存在对应条目；`sources[].resource` 为具体可核查文献（ISBN/DOI/机构 URL），非泛泛"某书"
- **Verification**: `human-judgment`（审查者抽查 ≥10 条论断，核对脚注与 sources 对应关系及信源可核查性）

### AC-5: 七概念链路质量门
- **Given**：R/I/E/V 各阶段产出
- **When**：按 G1-G3 质量门检查
- **Then**：G1（R 阶段事实无因果词，纯客观描述）通过；G2（I 阶段异文/谱系洞察含现象+根因+影响+建议四元组）通过；G3（E 阶段方法论模式含触发场景+核心步骤+反模式+迁移验证）通过
- **Verification**: `human-judgment`（按七概念质量标准逐门核对）

### AC-6: 对抗审查与不确定性显式化
- **Given**：有学术争议的概念（河上公年代、想尔注作者、北大简来源等）
- **When**：审查正文
- **Then**：每个争议点设"争议与不确定性"小节，列出至少两种学术观点及代表学者，不做单一确定性断言；`status` 或正文标注体现不确定性
- **Verification**: `human-judgment`

### AC-7: 信源权威度
- **Given**：`references/` 目录
- **When**：审查信源清单
- **Then**：至少 10 条信源，其中 ≥80% 为正式出版的学术专著、发掘报告、整理本或高校/博物馆机构页；无匿名博客/百科帖作为唯一来源
- **Verification**: `human-judgment`

### AC-8: 概念间交叉链接
- **Given**：bundle 概念图
- **When**：遍历链接
- **Then**：每个传本概念链接到其考古语境（如适用）、相关异文、所采信的 references；至少 80% 的概念有出链或入链，形成连通图而非孤立文件
- **Verification**: `programmatic`（链接计数 + 人工抽查）

### AC-9: 信任与生命周期元数据完整
- **Given**：每个概念 frontmatter
- **When**：检查 `generated`、`verified`、`status`
- **Then**：`generated.by` 非空且符合 actor 约定；`verified` 至少含一条（agent 自检或 process）；`status` 为 `draft`/`stable`/`deprecated` 之一
- **Verification**: `programmatic`

### AC-10: log.md 记录
- **Given**：`log.md`
- **When**：检查格式
- **Then**：按 `YYYY-MM-DD` 日期倒序，含 Creation 条目记录 bundle 建立，后续 Update 条目记录各阶段增量
- **Verification**: `programmatic` + `human-judgment`

## Open Questions
- [ ] 北大汉简《老子》的正式出版卷次与页码需网络核实（《北京大学藏西汉竹书（贰）》2012 上海古籍出版社，韩巍整理），若核实有误会在 references 中修正。
- [ ] 是否需要纳入敦煌唐写本（如 Pelliot 2584、2420 等）作为独立概念？当前方案在想尔注/傅奕本正文中提及，不单列；若用户要求更全面可追加。
- [ ] `verified` 最终是否由用户以 `human:<id>` 身份签署？当前假设 agent V 阶段后标记为 machine-confirmed，用户审阅后升级。
- [ ] 是否需要为 bundle 生成 `viz.html`（OKF viewer 可选可视化）？当前 Non-Goal，但若用户希望有谱系图可视化可追加。
