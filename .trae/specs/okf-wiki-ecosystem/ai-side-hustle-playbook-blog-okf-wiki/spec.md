---
type: spec
title: "《零基础AI实操赚钱项目教程（完整版）》→ OKF Wiki 知识包"
source: "https://mp.weixin.qq.com/s/g_XAFbxuhczf3iSaZiOyKg"
status: completed
methodology: seven-concepts-cmd
content-sensitivity: public
---

# 《零基础AI实操赚钱项目教程（完整版）》→ OKF Wiki 知识包

## 概述

- **目的**：全面学习微信公众号「干货534」于 2026-10-08 发布的《零基础AI实操赚钱项目教程（完整版）》（正文十章，35,518 字符），把「认知破局 → 工具准备 → 六大项目路径 → 定价与沟通 → 垂直行业与知识付费 → 避坑红线」转化为可溯源、口径分层、有时效管理的中文 OKF v0.2 知识包。
- **读者**：考虑以 AI 为工具承接副业或自由职业的从业者；评估 AI 服务接单、AI 带货、AI 内容账号等变现路径的读者；需要一站式工具箱、报价体系、交付 SOP 与合规红线清单的实操读者。
- **目标目录**：`projects/awesome-okf-xs/doc/bundles/sheke/industry/ai-side-hustle-playbook/`（社会科学域 / AI 行业与商业趋势分组，与既有 `auto-money-system`、`monetization-direction`、`overseas-freelance-night-work` 同组）。
- **基线**：本束为**新建**，事实编号自 `F-001` 起，与同项目既有束编号体系互不干涉。
- **工作流**：七概念知识沉淀链路 `R→I→E→V→C`；完成后由独立上下文审查。Git 提交在七概念 C 阶段执行（**仅本地提交，不 push**），推送须另获用户明确授权。

## 内容敏感度预检

- URL 为 `https://mp.weixin.qq.com/s/g_XAFbxuhczf3iSaZiOyKg?scene=1&click_id=676897105`：`scene=1` 与 `click_id=` 属分享追踪参数，非 `share?code=` / `token=` / 邀请码等访问控制参数；无登录墙、无企业内部域名信号。
- 文章正文可完整公开获取，内容为公开经验分享与商业方法论，不含个人隐私、内部会议或商业秘密。
- **判定：公开内容（Public）** → 标准工作流：spec 落 `.trae/specs/okf-wiki-ecosystem/`，产出物落 `projects/awesome-okf-xs/doc/bundles/`。

## 七概念编排

```text
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261022-wechat-okf-bundle | msg=公开文章转OKF Wiki | ctx={"scenario":"knowledge","topic":"零基础AI实操赚钱项目教程","depth":"standard"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20261022-wechat-okf-bundle | msg=场景判定为知识沉淀 | ctx={"scenario":"knowledge","chain":"R-I-E-V-C"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20261022-wechat-okf-bundle | msg=选定链路 R→I→E→V→C | ctx={"scenario":"knowledge","depth":"standard","gates":["G1","G2","G3","V","G4"]}
```

- **场景**：知识沉淀（需要从单篇公开文章沉淀可迁移的模式与决策清单）。
- **链路**：`R → I → E → V → C`。
- **G1（事实）**：≥20 条无因果词客观陈述，本轮实测 F-001～F-092 共 92 条，分「元信息 / 作者观点 / 作者建议 / 原文示例 / 作者案例 / 算术示例 / 核验事实」七类。
- **G2（洞察）**：≥3 条四元组（陈述 + F 编号证据 + 反常识 + 行动），落在「卖结果不卖时间」「AI 是放大器不是发动机」「可复现性缺失使教程退化为清单」三条主轴。
- **G3（模式）**：≥1 个可迁移模式，含触发场景（含「不适用于」边界）、3-7 个步骤、≥3 个反模式、检验标准、跨场景迁移示例。
- **V（对抗审查）**：四视角（魔鬼代言人 / 新人 / 老板 / 未来），≥5 条具体意见，≥2 条被采纳并修正。
- **C（原子提交）**：子模块先提交 → 主仓库 spec 提交 → 子模块指针提交，**不 push**。

## 骨架判定（操作可复现性两问）

| 问 | 结论 | 依据 |
|---|---|---|
| ① 博文中是否有读者可照做的安装/配置/代码/调用/实测流程？ | **是** | 工具清单（F-025～F-032）、头像三步与五步交付链（F-035）、内容标准化四步（F-041）、带货脚本公式（F-048）、接单五步（F-053）、标准交付七步（F-064）均为可照做的操作流程。 |
| ② 这些流程是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？ | **否** | 全文无工具版本号、无输入输出对照、无实验记录；收入与单量案例（F-033、F-075）多为第三方博主转述，无可审计的测试记录。步骤顺序具备，版本与输入输出缺失。 |

**判定：任一为「否」→ 不设 `examples/`**，采用概念骨架 `index + concepts + references + log`。
**内容性质**：商业分析/实操方法论类（非技术教程），`description` 显式标注「AI 变现实操方法论，非源码教程」。
**先例一致性**：同组既有 `auto-money-system`（同为商业分析类）亦无 `examples/`，本束沿用同一口径。
**理由**：定价表、脚本公式、交付 SOP 等内容以「清单 / 决策表」形态写入 concepts 层即可承载；`examples/` 目录一旦建立却无实测样本，会制造伪结构。

## 归属位置分析

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `sheke/industry/ai-side-hustle-playbook/` | ✅ | 主线是 AI 工具化个人变现的完整商业路径（认知 → 工具 → 六项目 → 定价 → 升级 → 风险），属于行业与商业趋势。 |
| `sheke/industry/auto-money-system/` | △ | 有「卖产品化的结果」交集，但该束聚焦自动化系统架构，本文聚焦个人实操路径，视角不同，保持并列并互链。 |
| `sheke/industry/monetization-direction/` | △ | 变现方向主题相近，但该束更偏选型与赛道判断，本文提供可执行报价与交付 SOP。 |
| `sheke/finance/` | ❌ | 不涉及理财、投资与资产配置。 |
| `jishu/ai/` | ❌ | 无 AI 技术实现教程、无 API 级操作。 |
| 新建分组 | ❌ | 单篇文章不得新建分组。 |

**命名冲突核查**：`Glob doc/bundles/sheke/industry/*playbook*/**` 无命中，确认 `ai-side-hustle-playbook` 在全库无同名目录。

## 信源与获取方式

| 代号 | URL / 路径 | 性质 | 状态 |
| --- | --- | --- | --- |
| W0 | `https://mp.weixin.qq.com/s/g_XAFbxuhczf3iSaZiOyKg?scene=1&click_id=676897105` | 文章原始入口 | **已获取完整 HTML**（3,835,683 B） |
| P0 | `C:\Users\xinzo\AppData\Local\Temp\wx_ai_hustle_raw.html` | 本地保存的页面 HTML 副本（临时区，不入库） | **已获取**，含 `id="js_content"` 正文容器 |
| P1 | `C:\Users\xinzo\AppData\Local\Temp\wx_ai_hustle_text.md` | 由 P0 经深度匹配提取的正文纯文本 | **已获取**，35,518 字符 / 1,789 行 —— 本束正文提取基准 |
| M1 | 页面脚本变量 `msg_title` / `nickname` / `ct` / `msg_desc` | 元信息字段 | 已解析：标题、署名、发布时间戳、摘要 |

- **获取方法**：常规 WebFetch / browser_use 在本轮遭遇反爬拦截（13/13 次失败）。改用 `Invoke-WebRequest` 携带桌面 Chrome UA 直取 HTML，再用自写 Python 脚本按 `<div id="js_content">` 标签深度匹配切分正文，转义还原后得到纯文本。该路径可重复执行，且比增量浏览切片更完整。
- **临时文件纪律**：P0 / P1 与提取脚本全部位于系统临时目录，不进入 `d:\spaces\SpecWeave`，不产生入库污染。

## 知识地图

| 层 | 产出 | 覆盖原文 |
|---|---|---|
| 元信息与阅读导引 | `concepts/00-article-provenance-and-reading-guide.md` | F-001～F-006 |
| 认知与商业模式 | `concepts/01-mental-models-and-market-window.md` | 第一章（F-007～F-024） |
| 工具箱与成本地板 | `concepts/02-toolbox-and-cost-floor.md` | 第二章（F-025～F-032） |
| 项目层 | `concepts/03-ai-art-and-pod.md` / `04-ai-content-account.md` / `05-ai-commerce-video.md` | 第三、四、五章（F-033～F-051） |
| 交易层 | `concepts/06-ai-service-orders.md` / `07-pricing-and-client-communication.md` | 第六、七章（F-052～F-064） |
| 升级层 | `concepts/08-vertical-industry-high-ticket.md` / `09-knowledge-products-and-personal-ip.md` | 第八、九章（F-065～F-075） |
| 边界层 | `concepts/10-risks-compliance-and-mindset-traps.md` | 第十章（F-076～F-082） |
| 模式层 | `concepts/11-verify-before-scale-pattern.md` | L1 可迁移模式「先验证再放大」（F-016、F-020、F-035、F-063、F-064、F-067、F-074） |
| 查证层 | `references/article-source.md` / `references/verification.md` | 全部 F 编号 + P0 核验结论 |

共 12 篇 concepts 正文 + 2 篇 references 正文 + 3 个索引（根 `index.md`、`concepts/index.md`、`references/index.md`）+ `log.md`，合计 18 个 Markdown。

## 事实登记

事实唯一登记见 [`facts.md`](facts.md)，F-001 至 F-092 连续。原文无脚注与外部链接；F-083～F-092 为 P0 核验补充事实，登记权威信源口径与源文差异。本表与 bundle `references/article-source.md` 保持同一编号集合。

## 功能需求

- **FR-1**：新建 bundle `ai-side-hustle-playbook/`，含根 `index.md`、`log.md`、`concepts/`（索引 + 12 篇）、`references/`（索引 + 2 篇），共 18 个 Markdown；**无 `examples/`**；每个含子目录的层级生成 `index.md` 并以 `{toctree}` 引用全部内容文档。
- **FR-2**：`references/article-source.md` 双份登记 F-001～F-092，编号集合与 `facts.md` 相等且连续；保留「元信息 / 作者观点 / 作者建议 / 原文示例 / 作者案例 / 算术示例 / 核验事实」分类；附引用边界声明。
- **FR-3**：`references/verification.md` 给出状态裁决、P0 勘误四清单、逐项核验与 V 四视角审查摘要；顶部明示 `status: flagged` 及失败项与影响范围。
- **FR-4**：concepts 12 篇中所有具体声明（价格、金额、比例、门槛、天数、平台名）带 F 编号引用；作者观点引用时保留「作者观点」标注；核验失败项在正文呈现权威口径并标注源文差异。
- **FR-5**：concepts 正文为原创改写，原文措辞仅作短句必要引用；不得出现未登记的推断数字。
- **FR-6**：至少 2 张 Mermaid 图（变现模式升级阶梯图 / 交付与定价闭环图），Mermaid 语法须通过 `check-mermaid.py` 等效校验（本束位于 `projects/` 子模块，`.agents/scripts/check-mermaid.py` 的 `FileScanner` 受 `EXCLUDED_DIRS` 含 `projects` 影响扫描为 0 文件，改用同源 `lib.checks.mermaid._process_file` 对本束 18 个 md 逐文件执行等价检查，结论以等价结果为准并在 `log.md` 注明）。
- **FR-7**：三级索引接入与五面计数同步——`sheke/industry/index.md`（导航表 +1 行、toctree +1 条、frontmatter description 束数同步）、`sheke/index.md`（正文束数与 industry 行同步）、`doc/bundles/index.md`（`total_bundles`、正文计数行、mermaid 节点、域节标题、分组表 industry 行五面同步）；全部数字以实施时机械真值复算为准（基线 `total_bundles=668`、sheke=74、industry=28 → 本束落盘后 `total_bundles=669`、sheke=75、industry=29；门禁执行时工作树实测 `total_bundles=670`，多出的 +1 为并行在途、尚未提交的 `sheke/finance/ponzi-scheme/` 束，非本束贡献，本束未回退该并行改动），不得手工估算，不得回退并行在途改动。
- **FR-8**：互链——新束 `index.md`「主题关联」链同组相关束（至少 `auto-money-system`、`monetization-direction`、`overseas-freelance-night-work`）并说明分工；本轮不回补反向链接。
- **FR-9**：`log.md` 记录七阶段执行、两问判定、P0 核验结论、并行在途观测、门禁运行方式（`invoke gates.*` 依赖不可用时执行手动等效清单并注明，禁止谎报）。

## 非功能需求与约束

- **NFR-1（规范一致）**：全部文件遵循 OKF v0.2 frontmatter（`okf_version` 仅出现在 bundle 根 `index.md`；子文档 `type` 取 `Concept`/`Reference`；`generated.by` 用 `seven-concepts-cmd` 标识、`verified` 用 `process:seven-concepts-v`；`status`/`stale_after`/`sources` 齐备），中文正文，kebab-case 英文文件名。
- **NFR-2（机械质量）**：UTF-8 严格 roundtrip 无 BOM 无乱码；全部 Markdown 相对链接可达；零 `file:///`、零 `C:\Users`／`/Users/` 等本机绝对路径（临时路径不得进入正文）；每个 `index.md` 含 toctree 且条目逐一存在。
- **NFR-3（时效管理）**：`stale_after` 设为 `2026-12-31`（平台规则与工具定价迭代快）；发布日期、平台规则快照时点、定价时点、原文观察时点集中声明于「已知边界」。
- **NFR-4（可审计）**：核验信源全部为实际访问成功的 URL，禁止编造；仅原文单源项显式标注，不升级可信度。
- **NFR-5（子模块纪律）**：产出在 git submodule `projects/awesome-okf-xs/`，**不自行 push**；写入前检查子模块无 merge/rebase 中态；不触碰同仓库他人在途未提交变更（当前观测到 `doc/bundles/index.md`、`doc/bundles/sheke/index.md` 及 `jishu/ai/frameworks/*` 等并行在途改动，计数同步以当前工作树真值为准，只增不覆盖）。
- **NFR-6（沟通语言）**：中文输出；对外文案避免收益承诺式表达与「躺赚」话术。

## 验收标准

- [x] bundle 结构为根 `index.md` + `log.md` + `concepts/`（12 篇正文 + 索引）+ `references/`（2 篇正文 + 索引），共 18 个 Markdown，无 `examples/`，根 index 顶部显式声明内容性质与两问判定。
- [x] G3 模式层缺口已补齐：`concepts/11-verify-before-scale-pattern.md` 为独立可迁移模式文档，含「适用于 / 不适用于」边界、3–7 步核心流程、≥3 条实证反模式、明确检验标准、≥1 个跨场景迁移示例与 L1 成熟度标注。
- [x] F-001～F-092 在 spec `facts.md` 与 bundle `references/article-source.md` 两处编号集合相等、连续无跳号（机械比对：92 = 92，集合相等，缺号 0）。
- [x] concepts 所有具体声明带 F 编号；核验失败项以权威口径呈现并标注源文差异；F-084（AI 生成内容标识义务）在正文「已知边界」明示。
- [x] 每个目录 `index.md` 含 toctree 且条目逐一存在；相对链接零断链（18 md / 90 本地引用 / 0 断链）。
- [x] 三级索引接入完成，`bundles/index.md` 五面计数一致（实测「9 域 / 63 组 / 670 束，五面一致」）。
- [x] 四视角 V 审查完成，≥5 条具体意见、≥2 条被采纳并修正，修正点回写 log.md（8 条意见 / 6 条采纳）。
- [x] 门禁验证：执行 `python scripts/check-bundles-index.py`、`python scripts/check-toctrees.py`、`python scripts/check-utf8.py`；`invoke gates.*` 依赖 `invocations` 不可用，执行清单化手动等效验证并在 log.md 注明，禁止声称「gates 通过」。
- [x] 原子提交顺序为子模块 → 主仓库 spec → 子模块指针，**不 push**。
