# 两性关系经典著作 OKF v0.2 知识包——独立对抗性评审报告（V 阶段）

- 评审对象：`doc/bundles/think/relationships/`（分组导言 `index.md` + 6 个 bundle，共 96 个 Markdown 文件）
- 评审范围：6 束 × 16 文件 + 分组导言 + 上层索引（`think/index.md`、`bundles/index.md`）
- 评审方式：fresh-context 独立验收；规范基线为 `spec.md`（AC-1～AC-10）、`tasks.md`、`.agents/rules/frontmatter.md`、范式 bundle `think/laozi/boshu-reading/`
- 取证方式：全量静态扫描（PyYAML 解析 frontmatter、toctree/相对链接 BFS、事实编号/信源配对/因果词扫描、直引与盗版关键词扫描）+ 人工抽查（30 条事实、3 篇 concept 正文、争议专项）
- 约束遵守：未修改任何源码文件；AC-3/AC-4 仅做静态检查，未运行 sphinx/invoke

---

## 一、结论概览

**总体判定：通过验收（PASS）。** 10 项 AC 全部达标，其中 AC-1～AC-7、AC-10 为明确 PASS，AC-8/AC-9/AC-10 三项 rubric 评分均达到或超过阈值 4 分。发现 7 项问题，全部为「低」或「微」严重度，不构成 AC 阻断，建议作为打磨项处理。

### 验收标准（AC）逐项结论

| AC | 检查内容 | 结论 | 关键证据（摘要） |
|---|---|---|---|
| AC-1 | 目录/文件结构 | ✅ PASS | 6 束每束恰好 16 文件（根 4 + concepts 6 + examples 3 + references 3），共 96 个 md |
| AC-2 | frontmatter 合规 | ✅ PASS（1 处缺陷） | type/okf_version/sources 体系正确；唯 `five-love-languages/references/01、02` 缺 `sources` 字段 |
| AC-3 | toctree（静态） | ✅ PASS | 全部 toctree 条目无断链；96 文件均可由 `doc/index.md` 经 toctree BFS 可达 |
| AC-4 | 相对链接（静态） | ✅ PASS | 束内链接与 21 条跨束链接全部有效，0 断链 |
| AC-5 | 事实溯源（G1） | ✅ PASS | 266 条事实 F-001 起连续无重复；3 种信源体制全部配对；因果词扫描 6 束全通过 |
| AC-6 | 版权合规 | ✅ PASS | 无 >30 汉字原书直引；唯一长命中为原创虚构教学对白；无盗版链接 |
| AC-7 | 上层索引 | ✅ PASS | `think/index.md`、`bundles/index.md` 统计与导航均已正确更新（think 域 13 束·5 组） |
| AC-8 | 内容忠实度（rubric） | ⭐ **5/5** | 抽查 3 篇 concept 忠实准确；书中主张一律归因；营销说法被隔离弃用 |
| AC-9 | 解读深度/原创（rubric） | ⭐ **4/5** | 概念澄清、理论脉络、原创实践、学术边界齐备；扣分项为 G2 四元组标签不统一 |
| AC-10 | 跨书联结（rubric） | ⭐ **5/5** | 分组导言知识地图/对话表/阅读路径齐备；每束 insights 跨书链接 ≥3（要求 ≥2） |

### 争议公允性四项专项

| 专项 | 结论 |
|---|---|
| 《爱的五种语言》实证争议（Impett 等 2024） | ✅ 强呈现 |
| 《男人来自火星》性别争议（Hyde 2005 等） | ✅ 强呈现 |
| 戈特曼预测力争议（Heyman & Smith Slep 2001） | ✅ 强呈现 |
| 《依恋》通俗主张 vs 学界共识 | ✅ 强呈现（逐篇设「本书主张 vs 学界共识」节） |

### 问题统计

- fail（阻断项）：**0**
- 低严重度：4 项
- 微严重度：3 项
- 首要 3 项问题：
  1. 【低】`five-love-languages/references/01-editions.md`、`02-further-reading.md` 的 frontmatter 缺 `sources` 字段（范式 references 文件带 sources）。
  2. 【低】G2 洞察四元组标签不统一：`five-love-languages`/`attached`/`mars-venus` 用「核心判断/证据/迁移/边界」，`gottman` 用「陈述/证据/反常识/行动」，仅 `intimate-relationships`/`art-of-loving` 用 spec 规定的「陈述/证据/反常识点/行动启示」。
  3. 【低】`mars-venus/facts.md` 信源列用内联 URL（61 个）而非 id 登记制，其中 11 处引用非权威聚合站 `www.zazhi.com.cn`（杂志网）。

---

## 二、逐 AC 证据判定

### AC-1 目录/文件结构 —— PASS

6 个 bundle slug：`intimate-relationships`、`art-of-loving`、`gottman-seven-principles`、`five-love-languages`、`attached`、`mars-venus`。

每束文件构成完全一致（各 16 个 md）：

- 根层 4 个：`index.md`、`log.md`、`facts.md`、`insights.md`
- `concepts/` 6 个：`index.md` + 5 篇概念文（00～04）
- `examples/` 3 个：`index.md` + 2 篇应用文（01、02）
- `references/` 3 个：`index.md` + 2 篇信源文（01、02）

合计 6 × 16 = 96 个 md，加分组导言 `relationships/index.md`。子目录 `concepts/examples/references/index.md` 无 frontmatter，与范式 `boshu-reading` 对应文件做法一致，不判违规。

### AC-2 frontmatter 合规 —— PASS（1 处缺陷）

- 内容文件均有非空 `type` 字段；6 个 bundle 根 `index.md` 均为 `type: OKF` + `okf_version: "0.2"` + 非空 `sources`，符合「okf_version 仅 bundle 根 index」约定。
- 分组导言 `relationships/index.md` 为 `type: group`，正确。
- 全部文件无 `file:///` 绝对路径；文件名全部 kebab-case 纯英文；`generated.by` 统一为 `reference_agent/trae-research-agent`。
- **缺陷（低）**：`five-love-languages/references/01-editions.md:1-9` 与 `five-love-languages/references/02-further-reading.md` 的 frontmatter 仅含 `type/title/description/tags/generated/status/stale_after`，**缺 `sources` 字段**；范式 `boshu-reading/references/core-manuscripts.md` 带 sources，其余 5 束 references 文件亦带 sources。

### AC-3 toctree 静态检查 —— PASS

- 镜像 `scripts/check-toctrees.py` 的 `resolve_target`/`check_reachable`/`check_consistency` 逻辑做静态验证：全部 `{toctree}` 条目均可解析为存在文件，无断链。
- 以 `doc/index.md` 为根做 toctree BFS，96 个 md 全部可达；各 `index.md` 目录清单与磁盘文件一致。
- 风格差异（微，不阻断）：`intimate-relationships/index.md:81-90` 的 toctree 条目带 `.md` 后缀（`concepts/index.md`）且无 `:hidden:`；其余 5 束用无后缀 docname（`concepts/index`）并带 `:hidden:`（如 `art-of-loving/index.md:104-111`）。两种写法 MyST 均可解析。

### AC-4 相对链接静态检查 —— PASS

- 束内 Markdown 相对链接全部解析有效。
- 6 束 `insights.md` 跨束相对链接经路径归一化后共 **21 条，0 断链**：intimate-relationships 4 条、art-of-loving 4 条、gottman 3 条、five-love-languages 3 条、attached 4 条、mars-venus 3 条（TR-8.2 要求每束 ≥2，达标）。

### AC-5 事实溯源与 G1 —— PASS

事实条数：intimate-relationships 43、art-of-loving 45、gottman 45、five-love-languages 45、attached 43、mars-venus 45，合计 **266 条**；各束均自 F-001 起连续编号、无重复、无跳号。

信源体制分三种，均能配对溯源：

1. **frontmatter sources id 制**：intimate-relationships（24 个 id）、art-of-loving（21 个）、gottman（29 个）——事实表信源列引用的 id 全部在 frontmatter 中定义。
2. **文末信源登记表制**：five-love-languages（frontmatter 仅 2 条内部 sources，真实信源 S1～S27 定义在 `facts.md` 文末）、attached（S1～S25 文末登记）——文末 S 编号全部可配对。
3. **内联 URL 制**：mars-venus（事实表信源列直接写 URL，45 行共 61 个 URL）——链接均可读，域名含 en.wikipedia.org 16、apa.org 5、handwiki 4、researchgate 4、douban 4 等，无可疑/盗版域名。

G1（事实无因果论断词）：扫描「因为/导致/使得/因此/所以/从而/因而」，6 束 facts **零命中**。

- 说明：art-of-loving `facts.md:116`（F-022）信源格 `s-wiki-en（版权页扫描件）`、`facts.md:119`（F-025）`s-wiki-en（参考文献）`——id `s-wiki-en` 存在且可配对，括号为人工注释，非断链。

### AC-6 版权合规 —— PASS

- 中文弯引号/直角引号扫描：**无任何 >30 汉字的原书直引**。
- 唯一 >30 字命中为 `mars-venus/examples/01-critical-application.md:10` 的 34 字对话（"这有什么难的，你明天直接找他说清楚啊……你就是太软弱。"），但该文件第 4 行明确声明"本文场景为**原创虚构**（教学用）"，属原创教学对白，非原书引文，不构成侵权。
- 块引用（`>`）超长项逐条核对，全部为本 bundle 原创声明/说明文字（性质声明、采集说明、版权声明），非原书正文。
- 15～30 字引号片段均为概念术语（如"爱箱"隐喻，22 字，已归因）或原创示例对话。
- 盗版关键词 17 处命中全部为**否定式声明**（"不提供盗版资源链接"等），无任何实际盗版/下载链接。
- 各束根 index 均有原创转述版权声明（如 `intimate-relationships/index.md:30`）。

### AC-7 上层索引 —— PASS

- `think/index.md`：分组表含 relationships 行（标注"6 束"），toctree 含 `relationships/index`，域描述已更新。
- `bundles/index.md`：frontmatter `total_bundles: 297 / groups: 37 / domains: 14`，正文"297 个知识包…14 域 37 组"；think 域标题"**13 束 · 5 组**"，域内束数 psi4 + laozi 1 + math 1 + suanxue 1 + relationships 6 = 13，与磁盘一致；生态 Mermaid 与推荐路径的 think 节点均含 relationships；toctree 保持域级不变。
- relationships 增量（+6 束、+1 组）已正确落地；总计 297/37 与磁盘启发式计数之差源于**既有域**的 group/直接 bundle 计数约定差异，与本次新增无关。

### AC-8 内容忠实度（rubric 1～5） —— 5/5

抽查 3 篇 concept 正文，忠实度高：

- `gottman-seven-principles/concepts/01-four-horsemen.md`：四骑士（批评/蔑视/辩护/筑墙）及解药、情绪淹没（flooding）、"筑墙者约 85% 为男性"、"前三分钟苛刻开场"、"暂停至少 20 分钟"等均与戈特曼体系一致；蔑视"最强单一预测因子"明确归为"戈特曼研究称"。
- `art-of-loving/concepts/02-theory-of-love.md`：爱作为对生存问题的回答、克服分离四途径、母爱/父爱类型学（明确标注"是类型分析，而非对具体父母的描述"）、五对象、四要素（care/responsibility/respect/knowledge，respect 词根"看见"）均准确；"爱是对人类生存问题的回答"明确标为**转述**。
- `attached/concepts/04-toward-secure.md`：依恋悖论、直接沟通要点、择偶建议与本书一致；三条学术边界与量表源流（Hazan & Shaver 1987、Bartholomew & Horowitz 1991、Brennan 等 1998 ECR、Fraley 等 2000 ECR-R）准确。

归因纪律：mars-venus 全书主张一律标"该书主张/该书称"（如 `facts.md` F-018、F-020、F-021）；争议性营销说法不单列为事实，而进入 `facts.md:101-105` 的"放弃清单" X-01～X-05（如 X-03"哈佛大学已将火星金星理论体系纳入课程体系——仅见于中文电商宣传文案，未找到哈佛大学方面任何信源"），`concepts/00-book-and-phenomenon.md:56` 亦声明"不予采信"。

### AC-9 解读深度 / 原创实践 / G1-G3（rubric 1～5） —— 4/5

- **概念澄清**：四骑士篇区分"抱怨 vs 批评"、"蔑视=厌恶+优越 vs 愤怒"、"筑墙=生理淹没而非态度恶劣"；爱的艺术篇区分"自爱 vs 自私"、"母爱/父爱的类型性质"——澄清到位。
- **理论脉络**：attached 篇给出成人依恋从 Bowlby/Ainsworth 到三类型/四类型/两维度的完整脉络；IR 篇 F-036 给出相互依赖理论 Thibaut & Kelley 1959/1978 源流。
- **原创实践（G3 可迁移）**：四骑士篇给出"承担争议中 5% 责任"脚本、"口头宣布暂停"脚本，并附跨文化提示（"沉默"在部分文化中可能是尊重）；attached 篇给出"把风格当观察工具、不把类型当命运判决、不把本书当临床依据"的可迁移使用姿势。
- **G1**：facts 无因果词（见 AC-5）。
- **G2（扣分点）**：6 束 insights 均含四元组且事实/洞察分层清晰，但标签不统一——`intimate-relationships`、`art-of-loving` 用 spec 规定的「陈述/证据/反常识点/行动启示」；`gottman/insights.md:38-68` 用「陈述/证据/反常识/行动」（语义一致，后两项为缩写）；`five-love-languages`、`attached`、`mars-venus` 用「核心判断/证据/迁移/边界」（如 `five-love-languages/insights.md:20`、`attached/insights.md:17`、`mars-venus/insights.md:21`）。后一种实质覆盖四要素（核心判断≈陈述、证据、迁移≈行动启示+G3、边界≈反常识/局限），且"边界"要素强化了学术公允，但标签与 spec FR-6/G2 不符，判为低严重度偏离，故本项扣 1 分。

### AC-10 跨书联结（rubric 1～5） —— 5/5

- 分组导言 `relationships/index.md`：含三层定位导言、6 束导航表（6 行）、Mermaid 知识地图（L1 学术/L2 哲学/L3 通俗三个 subgraph）、跨书概念对话表（4 行，链接有效）、三条阅读路径（问题驱动/体系/批判）。
- 跨束 insights 链接 21 条全部有效（见 AC-4），且链接为实质性概念互参（如 gottman `insights.md` 末条"爱可以通过练习经营"链接到 `art-of-loving/concepts/04-practice-of-loving.md`）。

---

## 三、30 条事实抽查表

每束抽 5 条，覆盖作者、原版年份、出版社、≥1 个核心理论名。判定列核对学术准确性与信源配对。

| 束 | F 编号 | 事实摘录（节） | 信源 | 判定 |
|---|---|---|---|---|
| intimate-relationships | F-001 | 作者罗兰·S·米勒（Rowland S. Miller），萨姆休斯顿州立大学心理学教授 | mhe-9e；shsu-vita | ✅ 准确，配对 |
| intimate-relationships | F-010 | 英文原版 *Intimate Relationships*，McGraw-Hill（纽约），社会心理学系列 | utah-4e；mhe-9e | ✅ 准确，配对 |
| intimate-relationships | F-011 | 第 1 版 1985 年，唯一作者莎伦·布雷姆（Sharon S. Brehm）；第 4 版版权页版权年 2007/2002/1992/1985 | utah-4e | ✅ 准确（版权页著录口径） |
| intimate-relationships | F-036 | 第 6 章相互依赖以社会交换/相互依赖理论为框架，用 CL、CLalt；该理论 Thibaut & Kelley 1959 提出、1978 系统化 | vanlange-rusbult；spt-afirstlook | ✅ 准确（核心理论），配对 |
| intimate-relationships | F-005 | 米勒获 2008 年 IARR 教学奖 | mhe-9e；douban-6e | ✅ 准确（出版社简介口径） |
| art-of-loving | F-001 | 弗洛姆 1900-03-23 生于美因河畔法兰克福 | s-britannica；s-db；s-ifef | ✅ 准确，配对 |
| art-of-loving | F-019 | 《爱的艺术》英文原版 1956 年由纽约哈珀兄弟公司（Harper & Brothers）出版 | s-wiki-en；s-surf；s-scirp | ✅ 准确，配对 |
| art-of-loving | F-029 | 成熟的爱含四要素：关心 care、责任 responsibility、尊重 respect、认识 knowledge | s-wiki-en；s-wiki-es | ✅ 准确（核心理论），配对 |
| art-of-loving | F-033 | 掌握艺术需四条件：纪律、专注、耐心、最高关注 | s-sobrief；s-15min | ✅ 准确，配对 |
| art-of-loving | F-002 | 弗洛姆 1980-03-18 逝于瑞士提契诺州穆拉尔托 | s-britannica；s-db；s-ifef | ✅ 准确，配对 |
| gottman-seven-principles | F-001 | 约翰·戈特曼，华盛顿大学心理学荣誉教授 | s-johngottman；s-bookshop | ✅ 准确，配对 |
| gottman-seven-principles | F-010 | *The Seven Principles for Making Marriage Work* 1999 年精装初版，Gottman & Nan Silver，Crown 旗下 Harmony Books | s-utah-excerpt；s-prh | ✅ 准确，配对 |
| gottman-seven-principles | F-026 | 末日四骑士：批评/蔑视/辩护/筑墙（中译批评/鄙视/辩护/冷战） | s-psychology；s-douban-quotes | ✅ 准确（核心理论），配对 |
| gottman-seven-principles | F-027 | 蔑视为四者中最具腐蚀性，是离婚"最强单一预测因子" | s-gratitude；s-psychology | ✅ 准确（归为戈特曼研究主张），配对 |
| gottman-seven-principles | F-004 | 1986 年于华盛顿大学建成公寓式"爱情实验室"，系统观察始于 1970 年代 | s-gottman-research | ✅ 准确，配对 |
| five-love-languages | F-001 | Gary Demonte Chapman，1938 年生，婚姻辅导者/牧师/电台主持/作家【P0】 | S3、S4、S8 | ✅ 准确，文末 S 登记配对 |
| five-love-languages | F-010 | *The Five Love Languages* 1992 年由芝加哥 Northfield Publishing 首次出版【P0】 | S7、S8 | ✅ 准确，配对 |
| five-love-languages | F-017 | 五爱语英文原名 words of affirmation / quality time / receiving gifts / acts of service / physical touch【P0】 | S2、S4 | ✅ 准确（核心理论），配对 |
| five-love-languages | F-018 | 中译通行名：肯定的言词/精心的时刻/接受礼物/服务的行动/身体的接触【P0】 | S20、S22 | ✅ 准确，配对 |
| five-love-languages | F-009 | 因本书获美国福音派基督教出版协会（ECPA）白金图书奖 | S8 | ✅ 准确（行业奖口径），配对 |
| attached | F-001 | 全名 *Attached: The New Science of Adult Attachment…*，作者 Amir Levine 与 Rachel Heller（版权页 Rachel S. F. Heller）【P0】 | S2、S3 | ✅ 准确，配对 |
| attached | F-004 | 2010 年由企鹅集团 Tarcher 品牌首次出版，精装 304 页【P0】 | S2、S7 | ✅ 准确，配对 |
| attached | F-007 | 成人亲密关系分焦虑/回避/安全三风格（附出版社官方简介）【P0】 | S2、S19 | ✅ 准确（核心理论），配对 |
| attached | F-011 | 依恋理论由约翰·鲍尔比（John Bowlby，1907–1990）于 20 世纪中叶创立，借鉴习性学与演化论【P0】 | S24、S16 | ✅ 准确，配对 |
| attached | F-012 | 《依恋与失落》三部曲 1969/1973/1980，纽约 Basic Books；第一卷 1982 修订版【P0】 | S11、S23 | ✅ 准确，配对 |
| mars-venus | F-001 | 约翰·格雷，1951-12-28 生于得克萨斯州休斯敦 | 维基·作者；Handwiki | ✅ 准确，URL 可访问 |
| mars-venus | F-004 | 1982 年函授获哥伦比亚太平洋大学（CPU）博士；CPU 未获正规认证且已停办 | 维基·作者；Buzzard (2002) | ✅ 准确（学历争议如实标注） |
| mars-venus | F-009 | 英文首版 1992 年纽约 HarperCollins 精装，x+286 页，ISBN 0-06-016848-X，OCLC 25201010 | WorldCat；Open Library | ✅ 准确，URL 可访问 |
| mars-venus | F-018 | 该书主张：男人来自火星、女人来自金星，多数冲突源于误以为对方"按错的方式行事" | 维基·书页 | ✅ 准确（标"该书主张"） |
| mars-venus | F-021 | 该书称压力反应：男人退缩进"洞穴"独处，女人倾诉减压；中译第 3 章"男人躲进'洞穴'，女人滔滔不绝" | zazhi.com.cn（中译本目录）；维基·书页 | ✅ 内容准确（核心理论，标"该书称"）；但并列信源含非权威聚合站，见问题 3 |

**抽查结论：30/30 条事实准确、信源可配对。** 作者生卒/学历、原版年份与出版社、核心理论名均与权威资料一致；通俗书主张均做了归因或争议标注。

---

## 四、争议公允性四项专项结论

### 4.1 《爱的五种语言》—— Impett 等 2024 综述【强呈现】

- Impett, Park & Muise（2024，*Current Directions in Psychological Science*）综述结论见于 `five-love-languages/facts.md` F-040/F-041（"10 项研究无一支持三主张，独立量表下五种爱语评分都很高"）。
- 设专篇 `concepts/04-evaluation-and-boundaries.md` 讲证据边界，明言"成书时没有同行评审的实证研究作为支撑"。
- `references/02-further-reading.md` 与 `insights.md` 边界条均引用（"「匹配效应」无实证支持（F-040）"）。

### 4.2 《男人来自火星，女人来自金星》—— Hyde 2005 性别相似性假说【强呈现】

- Hyde（2005）《The Gender Similarities Hypothesis》（*American Psychologist* 60(6):581–592，46 项元分析、约 78% 效应量 d<0.35）作为反方核心证据；另引 Carothers & Reis 2013、Zell 2015（d=0.21）、Davies & Shackelford 2006。
- 设专篇 `concepts/03-scholarly-criticism.md`；`insights.md` 洞察 1 标题即"火星金星是'经验共鸣型隐喻'，不是'实证型理论'——主张层与证据层必须分离"。
- 书中主张一律标"该书主张/该书称"；销量数字做了多口径并陈（1500 万/3000 万/5000 万）并把"1.5 亿册、158 周、哈佛课程"等中文宣传说法列入放弃清单 X-01～X-03，不予采信。

### 4.3 戈特曼 —— Heyman & Smith Slep 2001 交叉验证批评【强呈现】

- Heyman & Smith Slep（2001）《The Hazards of Predicting Divorce Without Crossvalidation》见于 facts 信源、`concepts/00-gottman-love-lab.md`、`references/02-further-reading.md:76`（"91%–94% 准确率来自其自有样本与自有编码者；在独立前瞻样本上预测力明显下降"）。
- `insights.md:39` 进一步给出"二手再分析中阳性预测值可低至 21%"，并在"反常识"条澄清学界质疑的是"把相关性当预测公式、未做样本外验证"，而非沟通模式与婚姻质量相关这一方向。
- "91%" 说法双口径标注（facts F-021"此为戈特曼团队的自我报告口径"；insights 要求引用时主动标注该口径）。

### 4.4 《依恋》—— 通俗主张 vs 学界共识【强呈现，可作范本】

- 每篇概念文均设"本书主张 vs 学界共识"节（`concepts/00:67`、`01:81`、`02:75`、`03:70`，`04` 用三条编号学术边界 + 对照表）。
- 准确呈现学术脉络：Bowlby/Ainsworth、Hazan & Shaver 1987 三题迫选量表（定位为"首个自陈测量，设计目标是证明成人恋爱具依恋性质"）、Bartholomew & Horowitz 1991 四类型、Brennan/Clark/Shaver 1998 ECR 与 Fraley/Waller/Brennan 2000 ECR-R 两维度、taxometric 类别/维度之争。
- 明确把"风格可快速改变"标为"乐观化表述"（内部工作模型相对稳定、改变反复渐进），并补充跨文化适用性（西方个体主义背景）与"严重困扰求助专业"的边界。

---

## 五、问题清单（按严重度排序，含文件:行号与修复建议）

### 低严重度（4 项）

1. **references 文件缺 `sources` 字段**
   - 位置：`five-love-languages/references/01-editions.md:1-9`、`five-love-languages/references/02-further-reading.md`（frontmatter 在 `stale_after` 后即 `---` 结束）。
   - 问题：范式 `boshu-reading/references/core-manuscripts.md` 及其余 5 束 references 文件均带 `sources`，此两文件缺失。
   - 建议：补 `sources` 列表（可引用 facts.md 文末登记的 S7～S11、S18～S22、S26～S27 等）。

2. **G2 洞察四元组标签不统一**
   - 位置：`five-love-languages/insights.md:20`、`attached/insights.md:17`、`mars-venus/insights.md:21` 用「核心判断/证据/迁移/边界」；`gottman-seven-principles/insights.md:38-68` 用「陈述/证据/反常识/行动」；仅 `intimate-relationships`、`art-of-loving` 用 spec 规定的「陈述/证据/反常识点/行动启示」。
   - 问题：标签与 spec FR-6/G2 不符（内容实质覆盖四要素，"边界/迁移"反而增强了公允性与可迁移性）。
   - 建议：二选一——(a) 统一改回 spec 四标签；(b) 若认为"核心判断/证据/迁移/边界"更优，则在 spec/frontmatter 规范中将四元组标签修订为该口径并全量统一，避免一套产出两套 schema。

3. **mars-venus 信源用内联 URL 且含非权威聚合站**
   - 位置：`mars-venus/facts.md`（45 行信源列共 61 个内联 URL）；其中 11 处引用 `www.zazhi.com.cn`（杂志网，非权威聚合站），如 F-020、F-021（`facts.md:60-61`）。
   - 问题：与其余束的 id 登记制不一致；zazhi.com.cn 仅用于"中译本目录"这类书目细节且有维基并列，但信源质量存隐患。
   - 建议：改为 frontmatter/文末 id 登记制；中译本目录尽量替换为出版社/图书馆/WorldCat 等权威著录，zazhi 仅作旁证。

4. **five-love-languages / attached 信源主体放在文末登记表，frontmatter sources 近乎为空**
   - 位置：`five-love-languages/facts.md`（frontmatter 仅 2 条内部 sources，真实信源 S1～S27 在文末）、`attached/facts.md`（S1～S25 在文末）。
   - 问题：功能上可溯源（文末 S 编号全部配对），但与另 4 束体制不统一，且 frontmatter 层不可机读。
   - 建议：将文末 S 登记表迁移/镜像到 frontmatter `sources`，或在规范中明确"文末信源登记表"为认可体制。

### 微严重度（3 项）

5. **art-of-loving 事实信源格含中文括号注释**
   - 位置：`art-of-loving/facts.md:116`（F-022 `s-wiki-en（版权页扫描件）`）、`art-of-loving/facts.md:119`（F-025 `s-wiki-en（参考文献）`）。
   - 问题：id 可配对，但括号注释可能被自动化扫描误判为 id 的一部分。
   - 建议：将注释移至信源 title 或单独备注列，信源格只保留纯 id。

6. **intimate-relationships toctree 风格不一致**
   - 位置：`intimate-relationships/index.md:81-90`（条目带 `.md` 后缀、无 `:hidden:`）；对照 `art-of-loving/index.md:104-111`（无后缀 docname + `:hidden:`）。
   - 问题：两种写法 MyST 均可解析、不影响构建，仅风格不统一。
   - 建议：统一为无后缀 docname + `:hidden:`。

7. **art-of-loving 概念文脚注用维基镜像站**
   - 位置：`art-of-loving/concepts/02-theory-of-love.md` 脚注（`a.osmarks.net`、`elmirador.edu.co:8081` 等维基镜像 URL）。
   - 问题：镜像站可访问但非常规范威源，存在长期失效风险。
   - 建议：替换为 canonical `en.wikipedia.org` / `es.wikipedia.org` 对应条目，镜像仅作访问受限时的备用。

---

## 六、总评

本批 6 个"两性关系经典著作"知识包整体质量**优良，达到 OKF v0.2 验收标准**。

突出优点：

- **结构与工程合规**：96 文件结构整齐，toctree 与相对链接静态门禁全绿，frontmatter 体系规范，事实编号连续、信源全部可溯源，G1 因果词零命中。
- **版权处理干净**：全程原创转述，无超长直引、无盗版链接，唯一长对白为原创虚构且自我声明。
- **争议公允性是最大亮点**：4 本通俗自助书的实证短板均被主动、准确、有据地呈现——Impett 2024、Hyde 2005、Heyman & Smith Slep 2001 等关键反方文献到位，《依恋》逐篇设"本书主张 vs 学界共识"，《火星金星》将"哈佛课程"等营销说法列入放弃清单不予采信。这种"主张层/证据层分离"的处理显著高于一般科普转述，可作为后续通俗著作知识包的范本。
- **跨书联结实质有效**：知识地图、概念对话表、阅读路径与 21 条跨束链接构成了真正的主题网络，而非孤立书目。

主要不足集中在**一致性而非正确性**：references 缺 sources、G2 四元组标签两套 schema、信源登记三种体制并存，以及个别非权威信源与镜像站。这些均为低/微严重度的打磨项，不影响事实准确性与学术公允性，建议在后续一轮统一修整。

**验收结论：PASS（10/10 AC 达标；rubric AC-8=5、AC-9=4、AC-10=5；0 阻断项，4 低 + 3 微建议项）。**
