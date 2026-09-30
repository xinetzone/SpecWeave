---
name: pattern-to-methodology-library
description: 把七概念知识包 E 阶段成型的模式独立沉淀入 docs/retrospective 方法论模式库——去重判定、模式文档加伴生 TOML、三处索引登记、回写上游知识包、入库 V 门与校验。当用户要求模式沉淀、模式入库、把知识包里的模式登记到模式库时使用；知识包尚未建成、纯问答或只是顺改一篇模式文档不要使用。
---

# pattern-to-methodology-library

把一个已在七概念知识包 E 阶段成型的可迁移模式，独立化为方法论模式库中的正式条目，完成双向链接与入库二次审查。本技能沉淀自三次同构交付：最小充分脚手架选型法（governance-strategy）、场景区间选型法（governance-strategy）、逆序文档学习法（research-knowledge）。

**分工边界**：

- **seven-concepts-cmd** 负责方法论编排（场景识别、概念链路、质量门顺序、CMD-LOG）；
- **knowledge-pack-builder** 负责知识包本身的产出规范（包内模式在包内成型，默认不入库）；
- **本技能只管一件事**——用户明确说"模式沉淀/模式入库"后，模式独立化的判定、文件、位置、登记、回写与校验。

## 0. 触发与边界

**使用**：用户明确要求"模式沉淀/模式入库/把这个模式登记到模式库"，且指定或上下文中可定位到一个已成型知识包。

**不使用**：① 知识包尚未建成、模式还在 R/I 阶段（先走 knowledge-pack-builder）；② 用户只要求顺改某篇既有模式文档（直接 Edit）；③ 随口问答与概念解释；④ 私域内容未判级就落盘（公开模式库不收私域条目，先做敏感度判级）。

## 1. 阶段 0：入库前判定（不通过不建文件）

### 1.1 定位上游模式

读用户指定知识包的 `index.md`，定位 E 阶段模式条目，提取：模式中英文名、一句话定义、步骤数、反模式数、成熟度自标、支撑事实编号与数量、V 审查记录。通读该包 concept 页时只取与模式直接相关的证据，不把案例细节搬进库。

### 1.2 去重四步（G3 前置硬门）

1. 读 [方法论模式库总索引](../../../docs/retrospective/patterns/methodology-patterns/index.md) 总表，按模式名与一句话定义初筛候选；
2. Grep 模式核心动作关键词（如"逆向""选型""重组"）于 `docs/retrospective/patterns/`，补捞名称不含关键词的近邻模式；
3. Read 全部候选模式全文，逐一对齐三个维度——**作用对象**（如代码仓库 vs 文档站）、**核心动作**、**所处层级**（遍历策略/产出流水线/产出结构）；
4. 出具裁定：重复则停止并报告应更新哪篇；**层级互补不算重复**，但必须在新模式的关系表中写清边界（如"产出流水线 vs 语料遍历策略"）。

### 1.3 选定子区域

按总索引的分区归属落位，既有七区：governance-strategy（治理）、research-knowledge（研究读法）、document-architecture（文档结构）、tools-automation（工具自动化）、retrospective-knowledge（复盘）、ai-collaboration（人机协作）、writing-expression（写作表达）。归类依据是模式核心动作而非案例主题。

### 1.4 冻结 session 与成熟度重裁

- 沉淀 session 号 `sc-YYYYMMDD-<topic>-pattern`；
- **不照抄知识包内的成熟度自标**：对照[总索引中的成熟度等级说明](../../../docs/retrospective/patterns/methodology-patterns/index.md#成熟度等级说明)重新裁定。单案例首次入库一律 **L1-draft**，validation_count 按完整案例数计（半个案例不算）；升级条件（L1→L1.5→L2）写入 maturity_note。

## 2. 阶段 1：模式独立化（新建两份文件）

### 2.1 模式文档

路径：`docs/retrospective/patterns/methodology-patterns/<sub-area>/<kebab-id>.md`

照 `assets/pattern-template.md` 起步，九段结构一个不缺：frontmatter、模式概述、触发场景（适用/不适用）、核心做法（分步）、反模式、检验标准、迁移示例、与现有模式的关系、沉淀与校验记录。

frontmatter 关键字段：`type: Pattern`、`id`（=文件名）、`source`（含上游 session 与事实/洞察/V 数量）、`source_report`、`x-toml-ref`、`maturity`/`maturity_note`、`validation_count`、`reuse_count: 0`、`documentation_level: complete`、`abstract_level: domain-general`、`tags`、`related_patterns`。

### 2.2 伴生 TOML

路径：`.meta/toml/docs/retrospective/patterns/methodology-patterns/<sub-area>/<kebab-id>.toml`

照 `assets/pattern-toml-template.toml`，TOML 与 frontmatter 的 id/maturity/validation_count/source 必须一致，`[bindings] related_patterns` 与 frontmatter `related_patterns` 对齐。

### 2.3 相对路径层级（三次实测，禁止凭记忆）

从 `docs/retrospective/patterns/methodology-patterns/<sub-area>/` 出发：

| 目标 | 相对路径 |
|---|---|
| 上游知识包 index | `../../../../knowledge/<域>/<bundle-id>/index.md` |
| 伴生 TOML | `../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/<sub-area>/<kebab-id>.toml` |
| 同区兄弟模式 | `<sibling-id>.md` |
| 跨区模式（如 document-architecture） | `../document-architecture/<sibling-id>.md` |

### 2.4 抽象化纪律

- 模式正文只用通用动作表述步骤（如"取文件树""骨架扫描"），案例仅作证据出现并挂事实编号（F-xxx）；
- 案例的完整地图、完整问题域清单保留在上游知识包，**不复制入模式库**，避免案例与通用模式互相绑死；
- 步骤须给出主手段之外的替代手段（如无 API 时用 sitemap/llms.txt），保证脱离案例环境可执行。

## 3. 阶段 2：三处索引登记

| # | 文件 | 改法 |
|---|---|---|
| 1 | `<sub-area>/index.md` 的 toctree | 按文件名字母序插入一行 `<kebab-id>`，只追加不重排 |
| 2 | `<sub-area>/README.md` 模式清单表 | 插入一行：文件链接、一句话价值（含案例与验证次数）、成熟度简写 |
| 3 | `methodology-patterns/index.md` 总表 | 末尾插入一行：id、中文链接、成熟度、validation_count、reuse_count、一句话适用边界与升级条件 |

表格行列数变化时**整表替换**，不做局部拼接。

## 4. 阶段 3：回写上游知识包

1. E 节标题下加 blockquote 沉淀说明：入库日期、通用版相对链接（知识包 index 出发为 `../../../retrospective/patterns/methodology-patterns/<sub-area>/<kebab-id>.md`）、本节保留为案例版；
2. 成熟度表述与库等级表对齐（如包内"L1"改为"L1-draft"并注明重裁依据）；
3. 质量门表 G3 行补充入库记录（入库版反模式数如有扩充要写明）；
4. 知识包 CMD-LOG 代码块追加两条：沉淀 session 的 S0（CMD_START）与 S99（CHAIN_COMPLETED，含交付物路径）。

只回写与沉淀直接相关的位置，不顺手改知识包其他内容。

## 5. 阶段 4：入库 V 门（4 视角，意见 ≥5）

| 视角 | 必查攻击点 |
|---|---|
| 魔鬼代言人 | 去重裁定是否成立；成熟度是否虚高；步骤在限流/截断/无元信息时是否失效；是否有幸存者偏差 |
| 新人 | 脱离案例背景能否执行；有无非 API/无工具替代；规模阈值是否被误当硬门槛 |
| 老板 | 建图/执行成本是否过度工程；照做出错时责任边界；检验标准是否对准决策结果而非流程完整 |
| 未来 | 模式前提消失后退化为什么（如文档站普遍版本化）；技术更替后的复查触发器 |

每条意见给裁定（采纳/部分采纳/不采纳＋理由），采纳项当场回归确认（写明改了哪份文件的哪一处），全部关闭才过 V 门，并把四视角裁定摘要写入模式文档"沉淀与校验记录"。

## 6. 阶段 5：落盘后校验（按顺序执行）

```powershell
# 1. 文件名规范（务必 --directory 限定，避免全仓含 submodule 扫描）
python .agents/scripts/check-filename-convention.py --directory docs/retrospective/patterns/methodology-patterns/<sub-area>

# 2. 链接检查（含 frontmatter 路径字段；一次给齐三个变更目录）
python .agents/scripts/check-links.py --paths docs/retrospective/patterns/methodology-patterns/<sub-area> docs/retrospective/patterns/methodology-patterns docs/knowledge/<域>/<bundle-id> --check-frontmatter-paths
```

链接报告的处置纪律：**逐条区分新增断链与存量断链**——模式库目录存在历史断链，只有出现在本次新建文件与新增链接中的断链必须修复；存量问题列入报告、不在本任务扩散修改。

```powershell
# 3. TOML 可解析与字段一致性
python -c "import tomllib; d=tomllib.load(open('.meta/toml/docs/retrospective/patterns/methodology-patterns/<sub-area>/<kebab-id>.toml','rb')); print(d['id'], d['maturity'])"
```

另自检：三处索引均已登记、上游回写四处齐全、frontmatter 无 `file:///` 绝对路径。若 `python` 不在 PATH，改用全路径 `& "C:\Users\XMICUser\AppData\Local\Programs\Python\Python314\python.exe"`。

## 7. C 阶段收尾

- 默认**只给 Conventional Commits 提交提案，不执行 git commit/push**；
- 提交范围单一：模式文档＋TOML＋三处索引＋上游回写，不夹带目录内其他未提交变更（若上游包存在历史未提交改动，提示用户拆分提交）；
- 提案形如：`docs(patterns): 沉淀「<模式名>」入方法论模式库——<一句话价值>（L1-draft）`。

## 8. 反模式（三次实战真实教训）

1. **不做去重直接建文件**——与既有模式重复或只改了名字的模式入库后会造成双权威，去重四步不可省。
2. **照抄知识包成熟度**——包内自标与库等级表口径不同（如 L1 vs L1-draft），入库必须对照等级表重裁。
3. **全文搬运案例细节**——把完整分类地图、237 篇清单复制进模式文档，模式与案例绑死、无法独立迁移。
4. **只加 toctree 不登记总表**（或反之）——三处索引是一个整体，漏登一处读者就有盲区。
5. **回写上游只加链接不更新 G3 记录与日志**——知识包读者无法知道模式已独立化，会继续把案例版当最新版引用。
6. **看到链接报告的存量断链就顺手全修**——扩大提交范围、违反单一职责；只修本次引入的断链。
7. **V 门只写好评**——入库 V 的核心是攻击去重裁定与成熟度，意见少于 5 条或无一条触及模式失效条件，视为 V 门未执行。
8. **凭记忆数相对路径层级**——模式库五层深、上游包三层深，层级数错是断链首因，照第 2.3 节表格落路径并跑链接脚本实证。
