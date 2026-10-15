---
type: spec
title: "WorkBuddy OPC 白皮书学习 → OKF Wiki 知识包"
status: "completed"
methodology: seven-concepts-cmd
content-sensitivity: public
source:
  - https://www.workbuddy.link/p/FVCdAodl3HBHMMPypCogBi
  - https://workbuddy-space-static.codebuddy.work/page/FVCdAodl3HBHMMPypCogBi/4/opc-whitepaper-mobile.html
  - https://workbuddy-space-static.codebuddy.work/page/FVCdAodl3HBHMMPypCogBi/4/janus.data.json
---

# WorkBuddy OPC 白皮书学习 → OKF Wiki 知识包

## 概述

- **目的**：全面学习腾讯云 WorkBuddy 团队发布的《WorkBuddy OPC 白皮书——AI 时代一人公司的商业与技术重构》（发行日期 2026 年 6 月，分享页共 32 页：封面 + 目录 + 六章 + 结语），把「OPC 创业趋势 → 范式转移与商业模式 → 中国政策与园区 → WorkBuddy 三层架构 → 能力图鉴与用户案例 → 生态共建与认证」转化为可溯源、口径分层、有时效管理的中文 OKF v0.2 知识包。
- **读者**：关注 AI 一人公司/超级个体赛道的创业者与研究读者；评估 OPC 扶持政策的园区与地方政府从业者；评估 WorkBuddy 能力矩阵与生态合作路径的产品与商务负责人。
- **目标目录**：`projects/awesome-okf-xs/doc/bundles/sheke/industry/workbuddy-opc-whitepaper/`（社会科学域 / AI 行业与商业趋势分组，与既有 `ai-solo-company-truth`、`ai-one-person-micro-product`、`workbuddy-content-system` 同组）。
- **基线**：本束为**新建**，事实编号自 `F-001` 起，与同项目既有束编号体系互不干涉。
- **工作流**：七概念知识沉淀链路 `R→I→E→V`；实施前经批准门，完成后由独立上下文审查。Git 提交须另获用户明确授权（默认不执行）。

## 目标与非目标

### 目标

- 白皮书全部 32 页、六章与结语的章节集合，均有采集记录、知识归属与覆盖状态；不以「读了目录/摘要」代替正文覆盖。
- 按「事实层 → 机制层 → 判读层 → 查证层」组织：concepts 回答「趋势与数据是什么／范式与商业模式怎么变／政策与园区落地到哪里／WorkBuddy 三层架构怎么接／能力矩阵与案例说明什么／生态与认证怎么共建」，references 提供逐条查证。
- **口径分层硬要求（六类，一律不得抹平）**：
  1. **厂商自宣 vs 官方统计 vs 第三方研究 vs 行业报告**：平台能力数字（235 位专家、250 个 Skill、86 个专区能力）为**厂商自述**；OPC 存量/立信数据挂**协会与市场监管总局口径**；效率倍数（HACR 1:72、8-10 倍、Anthropic 80%→96% 区间）挂**对应研究/机构与年份**；政策资金上限挂**政府公报/官媒报道**。四层来源须各挂来源，不得混同为白皮书独立结论。
  2. **文档内部自相矛盾（勘误项）**：§4.4.1 写「OPC 一人专区：20 个专家团 + 31 位单体专家 + 35 个精选 Skill（合计 86 个能力）」，§5.1 写「OPC 一人专区（13 个核心专家团 + 31 位单体专家 + 35 个精选 Skill）」——同一专区两种专家团口径，须并列表述 + 勘误登记。
  3. **案例数字为受访者自述**：§5.2 三个用户案例（韦优／蔡琛律师／智觉·李殿鹏）的量化数据由受访者本人提供、经 WorkBuddy 团队访谈核实，属**厂商背书下的客户自述**，不得作为独立评测结论或跨行业基准。
  4. **口号式/单一来源比例**：§2.7 的 5%／10%／70%／15% 分层、§1.5 的「80% AI + 20% 品味」、「Polsia 周增长 9%」等为单一来源或口号式表述，须标注「单一来源/口号性表述」，不得升级为统计事实。
  5. **白皮书自我定位与合作邀约属性**：第六章为厂商生态合作邀约（「欢迎政府、产业园区、媒体、KOL、行业专家、工具伙伴和我们一起」），属营销语汇；其合作模式表须原样保留「双方各自提供什么」的框架性定位，不得作为已达成的合作事实。
  6. **时效口径**：政策与平台能力数字明确截至 2026 年 6 月（§3 章首、§5.2 数据说明、§4.4.1）；白皮书发行日期 2026 年 6 月；引用须带时点。
- 接入社会科学域分组到 bundles 总索引的三级导航与计数（industry → sheke → bundles 总索引），并在新束向同组相关束建立单向互链。
- 操作可复现性两问判定（**两问皆否**）：白皮书为趋势报告与产品能力罗列，**无**读者可照做的安装/配置/代码/调用/实测流程，也未提供版本、输入输出、步骤顺序等可复现要素 → **不设 `examples/`**，description 标注「行业白皮书解读，非操作教程」。

### 非目标

- 不复制白皮书正文（不做全文镜像），只做原创归纳 + 事实登记；不搬运原页面的 HTML/CSS 制品与页面截图。
- 不替白皮书「证实」任何平台能力数字、案例成效或效率倍数，不做收益承诺式表达。
- 不新建分组；不修改同项目既有束的事实、计数与正文（正向互链仅在新束 `index.md` 内声明；若需在既有束回补反向链接，须另立任务并经 User 批准，本轮不做）。
- 不修复与本任务无关的并行在途变更与索引漂移（仅在 `log.md` 披露观测结果）。
- 不执行 `git commit/push`（遵循「未明确要求不提交」；完成后另行请示）。

## 背景与范围

### 信源与获取方式

分享页 `https://www.workbuddy.link/p/FVCdAodl3HBHMMPypCogBi` 为 **SPA（客户端渲染）**：纯 HTTP 抓取仅得 4 526 字节壳页（`window.__PUBLISH_BOOTSTRAP__` 指向静态制品基址）。正文经页面静态制品提取。内容敏感度判定为**公开内容（Public）**：URL 无 `code/token`/邀请码参数、无登录要求（页面内 `share/userinfo` 返回 `not login` 而正文制品仍可取）、具备社交平台分享卡片 meta（`og:title` = WorkBuddy OPC 白皮书）且出品方为腾讯云 WorkBuddy 团队、正文含公开合作邀约 → 走标准工作流，产出物入 `doc/bundles/`。页面 `robots` 为 `noindex, nofollow`（不索引），不构成访问控制，故不影响公开性判定，在 `source-manifest.md` 如实登记。

| 代号 | URL | 性质 | 状态 |
| --- | --- | --- | --- |
| W0 | `https://www.workbuddy.link/p/FVCdAodl3HBHMMPypCogBi` | 白皮书分享页入口（SPA 壳页，4 526 B） | 已访问（壳页解析出制品基址与 `publishVersion: 4`） |
| P0 | `https://workbuddy-space-static.codebuddy.work/page/FVCdAodl3HBHMMPypCogBi/4/opc-whitepaper-mobile.html` | 页面 HTML 制品（262 925 B，`div.page` 分页 A4 版式，语义标签齐备） | **已获取并解析——本束正文提取基准**（32 页 / 25 508 字符 Markdown） |
| P1 | `https://workbuddy-space-static.codebuddy.work/page/FVCdAodl3HBHMMPypCogBi/4/janus.data.json` | 页面正文数据源（717 277 B，3 385 节点，与 HTML 的 `data-page-node-id` 一一对应） | 已获取（交叉参照与 P0 对照） |
| X1 | 白皮书 PDF 原册 | 版式母本 | **未取得**（本分享页未随附下载入口） |

### 白皮书章节结构与归属映射

| 页 | 章 / 节 | 知识归属 |
| --- | --- | --- |
| P1 | 封面（标题、副题、出品方、日期） | concepts/00（元信息） |
| P2 | 目录（六章 32 节） | concepts/00 |
| P3-P4 | 第一章导语 · §1.1 规模数据 · §1.2 超级个体定义 · §1.3 效率革命量化 | concepts/01 |
| P5-P7 | §1.4 创业生命周期重置 · §1.5 Polsia 极致实验 · §1.6 AI 原生创业三个陷阱 · 本章小结 | concepts/01 |
| P8-P9 | 第二章导语 · §2.1 硅基员工 · §2.2 80/20 范式 · §2.3 三层能力模型 · §2.4 六大商业模式 | concepts/02 |
| P10-P11 | §2.5 六条已验证 C 端赛道 · §2.6 万能套利公式 · §2.7 能力洗牌（王佳梁分层） · 本章小结 | concepts/02 |
| P12-P14 | 第三章导语 · §3.1 北京朝阳政策（7 维度 10 措施） · §3.2 深圳行动计划 · §3.3 全国 20+ 省市 · §3.4 政策配套缺口 | concepts/03 |
| P15-P16 | §3.5 园区与本地化生态 · 本章小结 | concepts/03 |
| P17-P18 | 第四章导语 · §4.1 超级个体为何需要团队（四重结构需要） · §4.2 组织竞争力公式 · §4.3 三种超级团队形态 | concepts/04 |
| P19-P20 | §4.4 三层产品架构 · §4.4.1 起步期专家矩阵 · §4.4.2 扩张期助理 · §4.4.3 联合期 Teams · §4.5 混合架构 · 本章小结 | concepts/04 |
| P21-P24 | 第五章导语 · §5.1 全流程解决方案（七个经营环节：立项与验证 / 产品开发 / 内容创作分发 / 销售变现 / 数据分析 / 财税法务 / 个人 IP） | concepts/05 |
| P25-P26 | §5.2 OPC 用户案例（韦优 / 蔡琛律师 / 智觉·李殿鹏） · 本章小结与数据说明 | concepts/05 |
| P27-P29 | 第六章导语 · §6.1 四个建设维度 · §6.2 各维度核心需求 · §6.3 WorkBuddy 定位 · §6.4 OPC 从业者认证体系 | concepts/06 |
| P30-P31 | §6.5 合作形式（政府园区 / 媒体智库 / KOL 自媒体 / 行业专家生态伙伴） | concepts/06 |
| P32 | 结语（生态共建呼吁与 WorkBuddy 定位复述） | concepts/06 |

### 知识包分层设计（新束结构，共 14 个 Markdown）

```
workbuddy-opc-whitepaper/
├── index.md
├── log.md
├── concepts/    （index.md + 00～06 七篇）
└── references/  （index.md + source-manifest.md + article-source.md + verification.md）
```

| 层 | 文档 | 读者要回答的问题 |
| --- | --- | --- |
| concepts | `00-whitepaper-provenance-and-reading-guide` | 这是谁出的白皮书、什么时候发的、正文从哪来、六类口径分层怎么看、该怎么读这本知识包 |
| concepts | `01-opc-landscape-and-super-individual` | OPC 规模有多大、超级个体怎么定义、效率革命的量化证据是什么、创业生命周期怎么被重置、Polsia 上限在哪、三个新陷阱是什么 |
| concepts | `02-from-execution-orchestration-to-business-models` | 硅基员工是什么、80/20 怎么分工、三层能力模型怎么分、六种商业模式与六条 C 端赛道是什么、万能套利公式是什么、能力洗牌怎么发生 |
| concepts | `03-china-policy-and-local-ecosystem` | 北京朝阳与深圳政策各给了什么、全国 20+ 省市怎么覆盖、政策落地的配套缺口是什么、园区如何把政策变成实体载体 |
| concepts | `04-super-team-and-workbuddy-architecture` | 超级个体为什么还需要团队、组织竞争力公式是什么、三种超级团队形态是什么、WorkBuddy 三层架构如何承接 OPC 三阶段、混合架构为何是最优解 |
| concepts | `05-opc-capability-map-and-user-cases` | OPC 一人专区按七个经营环节排列了哪些专家团/Skill、三个用户案例各自破了什么局、案例数据该怎么读 |
| concepts | `06-ecosystem-certification-and-cooperation` | OPC 生态四个维度分别解决什么、WorkBuddy 定位在哪两层、从业者认证体系是什么、四类合作方的合作模式如何设计 |
| references | `source-manifest` / `article-source` / `verification` | 正文从哪采来的、每条说法的出处、核验结论与勘误 |

## 功能需求

- **FR-1**：新建 bundle `workbuddy-opc-whitepaper/`，含根 `index.md`、`log.md`、`concepts/`（索引 + 7 篇）、`references/`（索引 + 3 篇），共 14 个 Markdown；**无 `examples/`**；每个含子目录的层级生成 `index.md` 并以 `{toctree}` 引用全部内容文档。
- **FR-2**：`references/source-manifest.md` 登记 W0/P0/P1 三个信源与 X1 未取得项的采集台账（URL、访问日期、获取方式、取得体量、`publishVersion: 4`、知识归属、覆盖状态），并按上表「章节结构与归属映射」逐页/逐章登记覆盖状态；对 SPA 壳页与静态制品的两种获取路径显著区分；如实登记 `noindex, nofollow` 与公开性判定依据。
- **FR-3**：R 阶段产出 spec 目录 `facts.md`，登记 `F-001` 起编号事实（预计 150~200 条，以实际连续编号为准）；`references/article-source.md` 双份登记同一编号集合，两处正则 `^\|\s*F-(\d{3})\s*\|` 提取的集合相等、连续无跳号；每条区分「页面事实 / 厂商自述 / 第三方研究口径 / 官方或协会口径 / 白皮书观点 / 合作邀约语汇」。
- **FR-4**：`references/verification.md` 给出核验总表（发行日期与 `publishVersion` 快照、OPC 存量数据、效率倍数、政策资金上限、平台能力数字、案例数字、认证费用）、**六类口径分层**表、勘误清单（含 §4.4.1 vs §5.1 专家团数量冲突、§5.1 表内专家团条目数与「13 个核心专家团」的自洽性核对、目录与正文标题微差）、V 四视角对抗审查表与 `status` 裁决。
- **FR-5**：concepts 7 篇中所有具体声明（数字、金额、日期、政策名称、产品／专家团／Skill 名称、机构名称）带 F 编号引用；六类口径分层在全束一致落地；至少 1 张 Mermaid 图（OPC 三阶段 × WorkBuddy 三层架构承接关系图）+ 1 张流程／结构图（OPC 生态四维度或政策落地链条）。
- **FR-6**：concepts 正文为原创改写；原文措辞仅做短句必要引用并标注（>40 字直引须严格逐字且必要）；不得出现未登记的推断数字（尤其比例类）。
- **FR-7**：三级索引接入与计数同步——`sheke/industry/index.md`（导航表 +1 行、toctree +1 条、frontmatter description 束数同步）、`sheke/index.md`（正文束数与 industry 行同步）、`doc/bundles/index.md`（`total_bundles`、正文计数、mermaid 节点、域节标题、分组表 industry 行五面同步）；全部数字以实施时机械真值复算为准（基线：`total_bundles=637`、sheke=68、industry 注册=磁盘=25），不得手工估算，不得回退并行在途改动。
- **FR-8**：互链——新束 `index.md`「主题关联」链同组相关束（至少 `ai-solo-company-truth`、`ai-one-person-micro-product`、`workbuddy-content-system`、`papi-jiang-solo-ip`），并说明分工；本轮不回补反向链接。
- **FR-9**：`log.md` 记录七阶段执行、口径决策、两问判定、并行在途观测、门禁运行方式（`invoke gates.*` 不可用时执行手动等效清单并注明，禁止谎报）。

## 非功能需求与约束

- **NFR-1（规范一致）**：全部文件遵循 OKF v0.2 frontmatter（`okf_version` 仅出现在 bundle 根 `index.md`；子文档 `type` 取 `Concept`/`Reference`；`generated.by` 用 `seven-concepts-cmd` 标识、`verified` 用 `process:seven-concepts-v`；`status`/`stale_after`/`sources` 齐备），中文正文，kebab-case 英文文件名。
- **NFR-2（机械质量）**：UTF-8 严格 roundtrip 无 BOM 无乱码；全部 Markdown 相对链接可达（含 `concepts/` 层引用兄弟束须用 `../../` 深度）；零 `file:///`、零 `C:\Users`／`/Users/` 等本机绝对路径；每个 `index.md` 含 toctree 且条目逐一存在。
- **NFR-3（时效管理）**：`stale_after` 设为 `2026-12-31`（政策与产品能力数字为 2026-06 快照，迭代快）；发行日期、`publishVersion`、政策时点、平台能力数字时点、案例自述属性在「已知边界」集中声明，引用必带核验时点。
- **NFR-4（可审计）**：核验信源全部为实际访问成功的 URL，禁止编造；「仅白皮书单源」项显式标注，不升级可信度。
- **NFR-5（子模块纪律）**：产出在 git submodule `projects/awesome-okf-xs/`，**不提交**；写入前检查子模块无 merge/rebase 进行中；保护其他会话变更，不改无关共享索引。
- **NFR-6（临时文件隔离）**：采集缓存（壳页 HTML、制品 HTML、`janus.data.json`、提取脚本、提取后的 Markdown）留在 `d:\spaces\SpecWeave\.temp\workbuddy-opc\`，任务完成后清理，**不入库、不入 bundle**；最终资料仅入目标 bundle，规划仅入本 spec 目录。

## 约束

- **Technical**：Windows + PowerShell 7 + Python（3.13/3.14 可用，BeautifulSoup 4.13.5 + lxml 已具备）；门禁脚本在子模块根目录直接 `python scripts/<name>.py` 运行（`check-toctrees.py`、`check-utf8.py`、`check-bundles-index.py`）。
- **Business**：遵循 SpecWeave 启动协议与文档边界（公开内容标准工作流，spec 在 `.trae/specs/okf-wiki-ecosystem/`）；用户沟通中文、动作导向。
- **Dependencies**：分享页与静态制品可访问性（R 阶段已验证）；`publishVersion: 4` 制品快照；门禁脚本可用性；同组先例束（`ai-solo-company-truth`、`workbuddy-content-system`）作为体例与互链锚点。

## 假设

- **归属 `sheke/industry/` 的论证**（主线实体 + 查先例 + 不新建分组）：

  | 候选位置 | 判定 | 理由 |
  | --- | --- | --- |
  | `sheke/industry`（社会科学 / AI 行业与商业趋势） | ✅ 采纳 | 白皮书主线实体是 **OPC（一人公司）创业现象**——六章中前三章为纯行业趋势（规模数据、范式转移、中国政策），后三章为厂商解法；该组《收录边界》明文为「聚焦行业趋势、商业模式与产品生态分析」；组内已有 4 个强相关束（`ai-solo-company-truth`、`ai-one-person-micro-product`、`workbuddy-content-system`、`overseas-freelance-night-work`），互链价值高 |
  | `jishu/ai/ecosystems/tencent`（腾讯开源生态） | 否 | 该组定位为腾讯系产品/技术项目知识包（含在途的 `workbuddy-hardware-integration-whitepaper` 技术接入白皮书）；本白皮书**无技术实现内容**（无接口、无代码、无接入链路），归技术域会让「技术为器」与「趋势为道」边界失焦 |
  | `sheke/marketing` | 否 | 仅 §6.5.2/§6.5.3（媒体与 KOL 合作）片段属传播，全文是创业趋势与生态分析 |
  | 新建分组 | 否 | 单篇白皮书不新建分组（过度工程） |

- 骨架按「行业白皮书解读」判定：操作可复现性两问皆**否** → 不设 `examples/`（先例：`ai-solo-company-truth`、`auto-money-system`、`tencent-buddy-family`）。
- 分享页 `publishVersion: 4` 的制品即本束快照基准；白皮书以「发行日期 2026 年 6 月」为版本口径，此后官方更新不在本束范围（`stale_after` 到期复核）。
- P1 制品 `opc-whitepaper-mobile.html` 的正文文本经脚本提取为 Markdown（32 页 / 25 508 字符）；`janus.data.json` 仅作节点级交叉参照，不作为事实来源（两者为同一文档的不同序列化）。
- 用户所说「恰当位置」授权按上述归属判定落入 `sheke/industry`；若审批时改判他组，须回到 Specify 重排受影响的索引与互链范围。
- 时间戳生成标识沿用同组先例（`generated.by: seven-concepts-cmd`、`verified.by: process:seven-concepts-v`），`at` 取实施当日。

## 验收标准

### AC-1：白皮书章节覆盖完整

- **Type**: `rule`
- **通过条件**：白皮书 32 页／六章／结语的章节集合，与 `source-manifest.md` 中登记的知识归属集合双向差集为空；每章均有归属文档与覆盖状态；目录、封面、本章小结、数据说明等非正文页亦有归属（`concepts/00`）；W0（壳页）与 P0/P1（制品）两条获取路径在台账中区分记录；X1（PDF 母本未取得）显式登记而非静默跳过。
- **证据**：`references/source-manifest.md` 逐页清单 + 集合差异机械比对输出。

### AC-2：事实编号连续且可溯源

- **Type**: `rule`
- **通过条件**：spec `facts.md` 与 `references/article-source.md` 的 `F-\d{3}` 编号集合相等、连续无跳号、无重复；每条指向白皮书实际页／节；所有数字、金额、日期、政策名、机构名、专家团／Skill 名标明来源与核验口径；无未标注的推断；不做任何 F 编号重排（本束自 F-001 起）。
- **证据**：正则集合比对输出 + article-source.md 来源代号表 + verification.md 核验表。

### AC-3：口径分层与勘误准确

- **Type**: `rule`
- **通过条件**：六类口径在 `verification.md` 与相关 concepts 中均有独立小节或表格行；**平台能力数字（235 专家／250 Skill／86 专区能力）标注为厂商自述**；**§4.4.1（20 个专家团）与 §5.1（13 个核心专家团）的冲突并列登记并给出勘误**；**三个用户案例数字标注为受访者自述并经厂商团队核实**；**5%／10%／70%／15% 与「80% AI + 20% 品味」标注为单一来源／口号式表述**；**第六章合作模式表保留「双方各自提供」框架性定位，不得写成已达成的合作事实**；**全部政策与平台数字带「截至 2026 年 6 月」时点**；不得出现替白皮书「证实」平台成效或给出收益承诺的表述。
- **证据**：verification.md 口径并存表 + 勘误清单 + Grep 抽查记录。

### AC-4：三级索引与计数同步

- **Type**: `rule`
- **通过条件**：`python scripts/check-bundles-index.py` 在无并行写入窗口退出码 0（五面计数一致）；新束在 `sheke/industry/index.md` 导航表与 toctree 均出现且条目可达；三级索引写入的数字与脚本输出逐项相等（基线 637/68/25 → 本束增量 638/69/26）；`check-toctrees.py` 全量输出过滤本束名零命中（既有/并行污染项只在 `log.md` 列名披露）。
- **证据**：门禁脚本输出 + 机械复算记录 + `git diff` 范围证明（并行在途改动零回退）。

### AC-5：机械门禁与独立审查

- **Type**: `rule`
- **通过条件**：`check-utf8.py` 通过；全部新增文件的相对链接 Test-Path 存活（含 `concepts/` 内 `../../` 深度）；零 `file:///`、零本机绝对路径；frontmatter 必填字段逐文件核对通过；定向 Sphinx dummy 构建无本束引入的错误；最新独立 Review 结果为 `pass`。全库既有/并行问题按归属隔离并如实报告，不声称全库通过。
- **证据**：门禁脚本输出、构建结果、review.md。

### AC-6：教程可用性与知识分层质量

- **Type**: `rubric`
- **维度**：从「看懂 OPC 趋势与数据口径」到「判断政策与园区是否可对接」再到「判断 WorkBuddy 三层架构与能力矩阵是否匹配自身阶段、生态合作怎么谈」的可用性，以及事实—机制—判读—查证四层的分层清晰度。
- **量表**：1-5。
- **锚点**：1 = 六章按顺序平铺翻译、观点当事实、无边界；3 = 主题齐全、事实分层正确但洞察停留在复述、口径标签不统一；5 = 每篇回答一个明确问题，趋势数据与厂商自宣分层可辩、§4.4.1/§5.1 冲突被显式处理、案例以「受访者自述」读法呈现、政策与平台数字带时点、含触发条件+核心步骤+反模式+迁移验证的可迁移模式（如「OPC 三阶段 × AI 排产」判读框架），读者能据此做出更优决策且不会误读为收益或成效承诺。
- **通过阈值**：>= 4。
- **证据**：concepts 7 篇 + index「已知边界」；独立评审逐篇抽查评分。

### AC-7：OKF 规范符合度

- **Type**: `rubric`
- **维度**：与 OKF v0.2 规范及同组先例（`ai-solo-company-truth`、`workbuddy-content-system`）的一致性。
- **量表**：1-5。
- **锚点**：1 = 缺 frontmatter 字段／结构混乱；3 = 字段齐备但体例与先例有明显参差；5 = 根 index 九字段齐备（含 `okf_version`）、子文档不带 `okf_version` 且 `sources` 体例与先例同款、toctree 与表格双轨齐备、`stale_after` 与互链符合先例惯例、读感与同组成熟束一致。
- **通过阈值**：>= 4。
- **证据**：frontmatter 逐文件核对 + 与先例对照记录。

## 待决事项

- 无阻断性范围歧义。以下为实施时按既有裁决执行、无需再确认的事项：①不执行 git commit/push；②计数以机械真值复算为准，并行漂移只披露不修复；③`stale_after: 2026-12-31`；④`status` 目标 `stable`（若 V 阶段发现核心声明证伪或核心事实全部单源则转 `flagged`）；⑤不回补既有束的反向链接；⑥X1（PDF 母本）按「未取得」登记，不据版式推断内容。
