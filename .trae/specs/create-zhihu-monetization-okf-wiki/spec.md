# 知乎变现体系深度学习 · OKF Wiki 与个人变现路径 Spec

## 问题、用户与目标

### 问题

知乎站内存在多个面向创作者的内容激励与变现入口（项目广场、创作打卡挑战、主题活动等），其规则分散在活动页面中且多为 JS 重渲染，普通学习者面临三个障碍：① 规则不可见（页面无法直接静态读取）；② 数字与机制未经交叉核验（奖池规模、盐粒兑换、门槛条件多为平台单方口径）；③ 学完之后不知道"对我而言从哪开始、按什么顺序做、多久可见收益"——即从知识到行动的转化断裂。

### 用户

- 主要用户：希望通过内容创作在知乎获得第一份可验证收益的个人创作者（技术背景，具备持续输出优质图文的能力）；
- 次要用户：任何想系统了解"知乎创作者激励与变现机制"的 OKF 知识库读者。

### 目标

1. 对三个指定信源（知乎项目广场 + 两个活动 campaign 页）执行七概念方法论全链路学习（R→I→E→V→C，路径设计叠加 F→V），产出可溯源、经 P0 核验的 OKF Wiki 教程 bundle；
2. 基于该 Wiki 生成一份**公开（脱敏）**的「个人变现路径」文档：角色化路径矩阵（≥3 类创作者角色）+ 针对 AI/技术内容创作者背景的主路径详解，每条路径满足"可达、可操作"（有起点条件、准入门槛、分阶段行动清单、预期收益区间、退出/切换条件）；
3. 全程通过质量门（G1-G4 + OKF 机械门禁），以原子提交交付到既定仓库位置。

### 非目标

- 不覆盖知乎全部商业产品（如广告投放主视角的知+、品牌方后台），仅从**创作者个人变现**视角展开；
- 不产出代码/工具（本项目为知识沉淀任务，无仓库代码变更）；
- 不 push 到远端（用户未要求时不推送）；
- 不做收益承诺——所有收益区间必须标注信源口径与"非承诺"声明；
- 不改动 `vendor/`、不改动子模块内既有 bundle 的正文内容。

## 信源与内容敏感度（预检结论）

| 信源 | URL | 探测结论 |
|---|---|---|
| S1 项目广场 | https://www.zhihu.com/project-square | 公开无访问控制；JS SPA，静态提取仅得"加载失败"，**必须 browser_use 兜底** |
| S2 活动页 A | https://www.zhihu.com/parker/campaign/2083977679355889635?zh_hide_nav_bar=true | 公开可访问；创作打卡挑战性质（盐粒奖池、周打卡/全勤翻倍、答题/想法/彩蛋任务、十大话题领域）；正文重渲染需 browser_use 补全 |
| S3 活动页 B | https://www.zhihu.com/parker/campaign/2081789902673426369?zh_hide_nav_bar=true | 公开可访问；开源主题活动（报名制，"开源问题/开源知识/开源观察"板块）；需 browser_use 补全 |

**敏感度判定**：三信源均为公开页面（无 code/token/邀请码参数、无登录墙）→ **公开内容**，标准工作流：
- 规划区：`.trae/specs/create-zhihu-monetization-okf-wiki/`
- Wiki bundle：`projects/awesome-okf-xs/doc/bundles/`（OKF v0.2，归属见"约束"）
- 变现路径：`docs/` 下公开位置（脱敏；经用户确认）
- 私域零残留：产出物中禁止出现 `file:///` 绝对路径、本机绝对路径、个人敏感信息

## 功能性需求

### FR1 信源全文提取（R-a）

按 blog-article-to-okf-wiki 技能的信源获取链执行：WebFetch → browser_use 子代理 → 仍失败则请用户提供正文/截图。提取全文按信源分别存档于 spec 区； campaign 页若含关键规则截图，截图一并存档。单信源提取失败不得静默跳过。

### FR2 事实采集与 P0 核验（R-b / R-c）

- F-001 起连续编号登记全部关键声明（项目清单、奖励机制与奖池规模、参与门槛、话题领域、时间规则、盐粒/提现规则），作者观点显式标注"作者观点"；
- 信源距离判定：知乎活动页为**平台官方口径**（非厂商自宣第三方，但仍属平台单方声明）——所有成效/收益数字（奖池规模、盐粒兑换比、任务奖励额度）默认 P0，须以 WebSearch 官方源（知乎创作平台规则页/帮助中心/官方公告）核验；无法核验的显式标注"仅平台活动页单源"，禁止伪造官方 URL；
- 勘误四张清单逐项过筛：① 日期/版本表 ② 成效数字溯源表 ③ 口径对照表（地域/时间/统计限定词）④ 引文逐字核对表。

### FR3 三层知识拆分与 bundle 生成（I / E）

- **骨架判定（操作可复现性两问）**：信源为活动规则宣告页而非作者实测流程，预期判定为"商业分析/平台机制类"骨架（index + concepts/ + references/ + log，无 examples/）；若两问判定结果相反，须在 log.md 记录理由。操作步骤（报名/打卡/提现）以 concepts 篇目承载，不设空 examples 目录；
- **三层拆分**：事实层（三个信源的项目与规则，What/When/Who）→ 机制层（盐粒经济学、打卡/任务/彩蛋的激励结构、平台为何如此设计，Why；因果分析属洞察须与事实分层）→ 路径层（对不同角色创作者的进入顺序与组合策略）；
- **信源先行**：references/（article-source.md + verification.md）→ concepts/ → 各级 index.md 最后写；
- **归属决策**：单篇不新建顶级分组。候选对照：`sheke/industry`（已有 ai-monetization、monetization-essence、douyin-vibecoding、overseas-freelance-night-work 等同主题簇，18 束）vs 其他 sheke 子组；预期落 `sheke/industry`，理由写入 spec/tasks。

### FR4 个人变现路径设计与文档生成（F → V → 产出）

- **第一性原理推导**：从"个人可变现能力 × 平台激励结构 × 时间约束"出发，反推路径而非堆砌入口；
- **角色化矩阵**（≥3 类角色，如：零基础新手 / 垂直领域知识创作者 / AI·技术背景创作者），每角色一条子路径；
- **主路径详解**：针对"AI/技术内容创作者"背景的单一路径（起点条件 → 准入门槛 → 第 1 周/第 1 月/持续期行动清单 → 预期收益区间 → 退出/切换条件）；
- **可达可操作的硬标准**：每个行动项原子化（单一职责、可独立验证、有验收标准）；收益/门槛声明可追溯 bundle F 编号或标注"待验证"；无 F 支撑的收益数字禁止出现；
- **文档落点**：`docs/` 下公开位置（具体子目录由落盘前三查确定，参考既有先例 `docs/retrospective/reports/competitive-analysis/`）；个人细节脱敏；frontmatter 带 `source` 溯源字段。

## 非功能性需求

| 编号 | 需求 |
|---|---|
| NFR1 | **可溯源**：bundle 与路径文档中一切具体声明（数字/规则/门槛/时间）必须挂 F 编号或核验来源，禁止 facts.md 之外的编造 |
| NFR2 | **时效管理**：campaign 属活动性内容，bundle `stale_after` ≤ 2026-12-31（单篇活动解析 ≤ 3 个月）；路径文档标注规则时点 |
| NFR3 | **治理合规**：遵守 Spec Mode 产物规范（spec.md + tasks.md + review.md，禁 checklist.md）；OKF frontmatter 十字段齐备；中文正文、kebab-case 英文文件名 |
| NFR4 | **提交纪律**：Conventional Commits 中文描述；子模块先提交、主仓库后提交、指针更新最后；不 push |
| NFR5 | **门禁纪律**：依赖可用时跑 `invoke gates.*`；不可用时执行手动等效验证清单并在 log.md 注明；禁止谎报"gates 通过" |

## 约束、依赖与假设

**约束**
- bundle 归属不新建顶级分组；落既有分组（预期 `sheke/industry`）；
- 知乎活动页 JS 重渲染 → R 阶段必须预留 browser_use 兜底（S1 静态提取已确认失败）；
- 平台单方口径数字（奖池/盐粒）未经独立核验不得作为承诺性收益呈现，正文须标"平台口径/非承诺"；
- 不修改子模块内既有 bundle 正文；仅追加新 bundle 与索引行/计数。

**依赖**
- `projects/awesome-okf-xs` submodule 已初始化（已确认存在）；
- awesome-okf-xs 内 `invoke gates.*` 可用（依赖 `invocations`，缺依赖时走手动等效清单）；
- WebSearch 可检索知乎官方规则页（帮助中心/创作平台/官方公告）。

**假设**
- 三信源对未登录用户公开可读（已探测确认）；
- 用户不要求 push；
- browser_use 可渲染知乎页面（若被反爬拦截，升级为用户提供正文/截图）。

**待决问题（实施阶段按规则自行决策并留痕）**
1. bundle 是否设 examples/ → 两问判定（预期无，理由入 log.md）；
2. 变现路径 docs/ 具体子目录 → 落盘前三查（查 docs/ 结构、查同类先例、查规范原文）；
3. S1 项目广场的"全部项目"清单内容 → 以 browser_use 实渲染结果为准，禁止据 URL 名臆测项目清单。

## 影响面

| 对象 | 影响 |
|---|---|
| `projects/awesome-okf-xs/doc/bundles/sheke/industry/` | 新增 bundle `zhihu-monetization/`；组 index 导航表 +1 行、toctree +1 条、束数 18→19（以执行时读取现值为基准） |
| `projects/awesome-okfxs/doc/bundles/index.md` | total_bundles +1（以执行时读取现值为基准）、sheke 域束数 +1，三处计数同步 |
| `docs/` | 新增「知乎个人变现路径」公开文档（脱敏，frontmatter 带 source） |
| `.trae/specs/create-zhihu-monetization-okf-wiki/` | 新增 spec 区（spec.md / tasks.md / facts.md / verification 记录 / log） |
| 既有内容 | 只追加不改写；既有 bundle 正文零改动 |

## 验收标准

| 编号 | 类型 | 标准 |
|---|---|---|
| AC-1 | rule | spec 区 `facts.md` 存在，F 编号连续无跳号（跳号须显式注记），三信源的关键声明均有对应事实条目；作者观点显式标注 |
| AC-2 | rule | P0 类声明（奖池规模/盐粒兑换比/活动时间/参与门槛/规则条款）100% 有核验记录：官方权威 URL 或显式"仅平台活动页单源"标注；勘误四张清单逐项过筛并记录于 verification.md |
| AC-3 | rule | bundle 落于既有分组（预期 `sheke/industry/zhihu-monetization/`），未新建顶级分组，归属理由已留痕；组 index 与总 index 的导航表行、toctree 条目、束数计数三面同步（以读取现值 +1 为准，不凭记忆写数字） |
| AC-4 | rule | bundle 结构符合 OKF v0.2：根 index.md + concepts/ + references/（article-source.md + verification.md）+ log.md；examples/ 取舍由两问判定且理由入 log.md；frontmatter 十字段（okf_version/type/title/description/tags/generated/verified/status/stale_after/sources）齐备，sources 同时含信源 URL 与核验权威 URL |
| AC-5 | rule | 三级 toctree 完整（根/子目录/组 index 均含 toctree 块，条目排除 `:` 指令行逐一 Test-Path 可达）；全部新增/修改 .md 相对链接可达、零 `file:///`；UTF-8 strict roundtrip 无乱码 |
| AC-6 | rule | facts.md 与 references/article-source.md 双份 F 编号集合一致（正则比对） |
| AC-7 | rule | 在 awesome-okf-xs 子项目内 `invoke gates.all` 三 gate 全绿；依赖不可用时执行手动等效验证清单并在 log.md 注明，且未谎报 gates 状态 |
| AC-8 | rule | 变现路径文档位于 `docs/` 公开位置且脱敏，包含：起点条件、角色化路径矩阵（≥3 类角色）、每角色分阶段行动清单（第 1 周/第 1 月/持续期）、每路径准入门槛与退出/切换条件、针对 AI/技术内容创作者的主路径详解、frontmatter `source` 溯源字段；每个收益/门槛声明可追溯 bundle F 编号或标注"待验证" |
| AC-9 | rubric | **路径可达性**（0-2 分）：V 阶段四视角对抗审查（事实溯源/结构规范/读者可用性/时效边界）无 fails；魔鬼代言人视角逐条证伪"画饼路径"；每条路径通过"新人视角 + 每日 ≤2 小时资源约束"可行性检验。阈值：≥1.5 且无任何一条路径未通过证伪 |
| AC-10 | rubric | **七概念质量门**（0-2 分）：G1 事实无推断词、G2 洞察四元组完整（现象+根因+影响+建议）、G3 模式含触发场景+核心步骤+反模式+迁移验证、G4 行动项原子化（单一职责/可独立验证/有验收标准）；F（第一性原理）后有 V（对抗审查）。阈值：≥1.5 |
| AC-11 | rule | 提交顺序：① awesome-okf-xs 子模块内提交（bundle + 组 index + 总 index）→ ② 主仓库提交 spec 区 → ③ 主仓库提交 docs/ 变现路径 + 子模块指针；使用 git-commit-utf8.py 显式列文件；Conventional Commits 中文描述；未 push（git log 验证） |

## 关联资产

- 方法论：seven-concepts-cmd（本任务元编排）→ blog-article-to-okf-wiki（七阶段转化工作流，R/I/E/V/C 细节以其 L2 模式文档为准）
- 先例 bundle：`sheke/industry/ai-monetization`、`monetization-essence`、`overseas-freelance-night-work`（同主题簇，索引互链参考）
- 先例报告：`docs/retrospective/reports/competitive-analysis/research-china-side-income-platforms-20260919/`（副业平台全景调研，路径文档的体例参考）
- OKF 规范：`projects/awesome-okf-xs/.agents/rules/frontmatter.md`、toctree 规范
