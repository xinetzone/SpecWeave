---
type: spec
title: "知乎 AI 科学创新工坊第二弹 → OKF v0.2 Wiki 教程知识包"
source: ".trae/specs/zhihu-ai-science-workshop-okf-wiki/raw/article-raw.md"
source_url: "https://zhuanlan.zhihu.com/p/2091930347550109878"
status: active
generated_at: "2026-10-22"
---

# 知乎 AI 科学创新工坊第二弹 → OKF v0.2 Wiki 教程知识包

## Overview

把知乎「知乎科学」机构号发布的专栏文章《两大赛道、40,000 元奖池、海量 Token | AI 科学创新工坊第二弹上线!》转化为 `projects/awesome-okf-xs/doc/bundles/` 下的 OKF v0.2 知识包（Wiki 教程形态）。

按七概念方法论编排（`seven-concepts-cmd`）走**场景 4 知识沉淀链路 R→I→E→V→C**。

| 项 | 值 |
|---|---|
| 源文 URL | https://zhuanlan.zhihu.com/p/2091930347550109878 |
| 源文标题 | 两大赛道、40,000 元奖池、海量 Token \| AI 科学创新工坊第二弹上线! |
| 发布方 | 知乎科学（已认证机构号，署名 zhi-hu-ke-xue） |
| ContentID | 2784687793959661225 |
| 内容敏感度 | **公开内容**（公开发布的知乎专栏文章，无 `share?code=` / `token=` / 邀请码等访问控制参数） |
| 工作流 | 标准工作流（spec 在 `.trae/specs/`，产出物入根 `docs/` 体系下的子项目知识库 `projects/awesome-okf-xs/doc/bundles/`） |
| 目标落点 | `projects/awesome-okf-xs/doc/bundles/sheke/industry/zhihu-ai-science-workshop/` |

## Goals

- G1：产出一个结构完整、事实可溯源的 OKF v0.2 bundle，覆盖该活动的**事实层 / 机制层 / 路径层**三层。
- G2：所有事实挂 F 编号，spec 区 `facts.md` 与 bundle `references/article-source.md` **双份登记且编号集合逐字一致、连续无跳号**。
- G3：P0 核验覆盖全部核心声明（活动存在性、时间窗、奖池算术、双赛道奖励结构、投稿与评选规则、诺奖指涉），产出核验报告与勘误清单。
- G4：三级 toctree（bundle index → 组 index → 总 `bundles/index.md`）与三级计数全部接入且自洽。
- G5：产出物符合 OKF v0.2 frontmatter 规范、相对链接可达、UTF-8 strict roundtrip 通过。

## Non-Goals

- 不设 `examples/`：源文非操作教程（见「骨架判定」），无可复现的代码 / 命令 / 算例可落 examples。
- 不做收益测算、不预测获奖概率、不推荐工具选型、不为任何参赛作品背书。
- 不复刻源文全部标点与空隙，仅逐字保留**规则条款、数字、名称**。
- 不把活动宣称与独立核验混同；平台自述一律标注证据层级。

## Background & Context

### 1. 信源与公开性预检

| 检查项 | 结论 |
|---|---|
| 内容性质 | 公开发布的知乎专栏文章（机构号发布） |
| 访问控制 | 无 `share?code=` / `token=` / 邀请码；匿名可读 |
| 判定 | **公开内容** → 标准工作流 |
| 采集通道 | 知乎开放平台 CLI（`zhihu-cli search zhihu`，16 组锚点滑窗拼接，13 个窗口命中） |
| 通道限制 | 直连 `zhuanlan.zhihu.com` 与 `www.zhihu.com/api/v4/articles/<id>` 均 403（code 40362）；Playwright 无头 Chromium 亦 403。开放平台返回的 `ContentText` 为纯文本片段（每次约 1021~1202 字符），**不含正文内链 href 与图片 src** → 源文 7 处超链接目标不可逐字复核，只能复核锚文本 |
| 原始证据 | `raw/article-raw.md`（合并全文 + 7 处锚文本清单）、`raw/cli-windows.md`（13 窗口原始滑窗） |

### 2. 内容形态与骨架判定（操作可复现性两问）

| 问 | 答 | 依据 |
|---|---|---|
| 第一问：文章是否包含可复现的操作步骤？ | **是** | 含四步流程（选工具 → 选挑战题 → 上传源码到 AI Works「科学季」→ 带话题发介绍文章）、4 条投稿硬性要求、4 条活动说明条件、6 条评选规则 |
| 第二问：读者能否据此独立完成并验证结果？ | **否** | 正文 **0 代码块、0 表格**；全部入口均为外链（豆包下载、看山手册、3 个安装包、内测问卷、上传源码教程），且受通道限制 **href 不可复核**；无任何具体命令、参数、目录结构或可验证产出物；「确保作品可以正常运行」的实际验收标准依赖平台审核而非文章 |

**骨架判定结论**：两问第二问为「否」→ **不设 `examples/`**，采用 `index.md + concepts/ + references/ + log.md` 四段骨架。
同簇先例一致：`zhihu-monetization`（10+2）、`big-tech-pontzi-track-selection`（8）、`ai-side-hustle-playbook`（12+2）均无 `examples/`。
bundle `description` 须标注「非操作教程」，防止读者误判为可跟做的教程。

### 3. 归属决策

| 候选位置 | 判定 | 理由 |
|---|---|---|
| **`sheke/industry/` 新建独立束** | ✅ **采用** | ①与同平台先例 `zhihu-monetization` 同属「知乎站内创作者激励」，且 `sheke/industry/` 已有 2 个知乎源转化先例（`big-tech-pontzi-track-selection`、`ai-side-hustle-playbook`）；②本活动是**独立活动实体**——主办方（知乎科学机构号 vs 知乎×科普中国）、时间窗（10/9–10/31 vs 09.30–10.30）、玩法（双赛道工具链 vs 问答/开源内容）、奖励形态（现金双赛道 vs 盐粒+万元科普奖）均不同；③`zhihu-monetization` 已含「科学季 2026」（F-044~F-058），与本活动**不是同一活动**，合并会造成口径混用 |
| 并入 `zhihu-monetization` | ❌ | 该束 F 编号已用至 F-067 且围绕「AI Works 广场 / 打卡挑战赛 / 科学季」三信源；塞入会突破其「三信源」结构前提，并制造跨活动口径混用 |
| `jishu/ai/practice/` | ❌ | 该域为技术实践（源码教程 / 工具实操），本活动为活动规则解读，非技术实操 |
| 新建分组 | ❌ | 违反「单篇博文禁止新建分组」原则；`sheke/industry/` 已是恰当分组 |

**束名**：`zhihu-ai-science-workshop`（与 `zhihu-monetization` 保持 `zhihu-` 前缀簇序）
**互链**：与 `zhihu-monetization`、`big-tech-pontzi-track-selection`、`ai-side-hustle-playbook`、`ai-monetization` 建立主题关联（须写明「科学季 2026 ≠ AI 科学创新工坊」的防混用注记）。

### 4. 三层知识拆分

| 层 | 承担 | 文档 |
|---|---|---|
| **事实层** | 只登记源文明示内容，逐条挂 F 编号，零因果推断 | `00-overview` / `01-campaign-facts` / `02-track-rules` / `03-toolchain` / `04-science-challenges` / `05-participant-works` |
| **机制层** | 双赛道设计意图、有效作品门槛、Token 与现金双激励的机制解读，显式标「洞察/推断」 | `06-mechanism-insights` |
| **路径层** | 选题路径、执行路径、评审路径、风险边界，收益一律挂 F 或标「待验证」 | `07-participation-path` / `08-risks-and-boundaries` |

### 5. 计数基线（磁盘现值，2026-10-22 核实）

权威口径来自 `projects/awesome-okf-xs/scripts/check-bundles-index.py`（递归计数：直挂 `concepts/`/`examples/`/`references/` 任一者为锚点束计 1；含带 `index.md` 内容子目录者为导航目录递归求和；叶子束计 1）。

| 位置 | 现值 | 本次新增后 | 依据 |
|---|---|---|---|
| `doc/bundles/index.md` → `total_bundles` | 670 | **671** | 权威脚本现跑通过：9 域 / 63 组 / 670 束，五面一致 |
| `doc/bundles/index.md` → `groups` | 63 | 63（不变） | 同上 |
| `doc/bundles/index.md` → `domains` | 9 | 9（不变） | 同上 |
| `bundles/index.md` 正文「当前共 **N 个知识包**」 | 670 | **671** | 计数行 |
| `bundles/index.md` mermaid sheke 行 | 75 束 | **76 束** | 生态概览图 |
| `bundles/index.md` 社科域节标题 | 75 束 | **76 束** | `### 👥 [社会科学](sheke/index.md) · N 束 · 9 组` |
| `bundles/index.md` 社科域分组表 industry 行 | 29 | **30** | 分组表数据行 |
| `sheke/index.md` 域导航表 industry 行 | 29 束 | **30 束** | 域内分组导航表 |
| `sheke/index.md` 域简介 AI 行业段 | 29 束 | **30 束** | 域简介正文 |
| `sheke/industry/index.md` → `total_bundles` | 29 | **30** | 组级 frontmatter |
| `sheke/industry/index.md` 描述 / 导航表 / toctree | 29 | **30** | 三处同步 |

> 磁盘实际目录数复核：`sheke/industry/` 下实有 **29** 个子目录，与组级声明 29 束一致（无既有漂移）。全库域级目录计数 guoxue=16 组 / jishu=19 / kexue=3 / meta=3 / sheke=9 / wenxue=2 / yishu=3 / yixue=6 / zhexue=2 → 合计 63 组，与 `groups: 63` 一致。

### 6. P0 核验关键结论（首轮，详见 `verification.md`）

| 编号 | 结论 | 备注 |
|---|---|---|
| C1 | ✅ 活动与机构号真实存在，有权威媒体转载 | |
| C2 | ✅ 时间窗 2026-10-09 ~ 10-31 | |
| C3 | ✅ 40,000 元奖池 | 与 C16 算术互证 |
| C4 / C5 | ✅ 双赛道奖励结构逐字 | |
| C8 | ✅ 豆包下载页可达 | |
| C10 / C19 | ✅ 上一期活动页与发布时间 2026-09-15 | 上一期时间窗 9/3–9/30 |
| C11 | ✅ AI Works 一键代部署教程存在 | |
| C12 | ✅ 20 工作日公布 / 公布后 20 工作日发放 | |
| C14 | ✅ 内测问卷 + 24h + 退出重登流程 | |
| C16 | ✅ 奖池算术自洽 | 单赛道 20,000 × 2 = 40,000；10 张会员卡与商汤周边**不计入**奖池 |
| C6 | ⚠️ 「商汤技术支持」仅平台自述 | 商汤官网仅见「代码小浣熊/办公小浣熊」，无看山条目；小浣熊徽章/杯与商汤小浣熊 IP 吻合可旁证；「内测」获参赛者「活动邀请使用阶段」佐证 |
| C7 | ⚠️ 三种安装包属平台口径 | href 不可复核 |
| C9 | ⚠️ AI Works「科学季」筛选项前端渲染不可见 | 项目广场页可达 + 上传源码有官方教程 |
| C15 | ⚠️ 8 挑战题确认；诺奖指涉获官方公告证实 | **第二轮重大修正**：官方为「**诺贝尔物理学奖 2026**」（2026-10-06 瑞典皇家科学院公布），获奖者**仅 Francis Halzen 一人独享**（Prize share 1/1），非「Halzen 与 IceCube 团队」；2025 年度奖为 Clarke/Devoret/Martinis（超导量子隧穿），与本活动无关。另：公布日早于活动起始日 **3 天**，「落在活动窗口内」的说法错误 |
| C17 | ⚠️ 「豆包标准模式会员卡」非官方产品名 | 官方为「豆包专业版·标准套餐」（标准/加强/高级三档）；标准套餐四档价：连续包月 **¥68**、连续包年 **¥688**、单次购买·1 个月 **¥80**、单次购买·1 年 **¥828**；「专家模式」才是豆包功能名 |
| C18 | ✅ 独立参赛作品 **6 篇** | 第二轮去重修正：p/2093792060528649287 与 p/2093028032369932182 同作者同署名同句，**非独立佐证**，7 篇去重为 6 篇 |
| **C13（自我纠错）** | ⚠️ **首轮判「实为 5 项」为误判** | 回溯 `raw/cli-windows.md` 6 个窗口逐字比对：第四步投稿要求恒为 **4 条**（原创图文≥500 字 / 配图≥3 张 / 嵌入作品链接 / 标注赛道）；首轮把「活动说明 4 条条件」误并入投稿要求计数。已列为勘误 F-077 |
| **「650 亿」（新增勘误）** | ⚠️ 参赛者文转述失真 | IceCube 官方口径为「约 **100 万亿**/秒穿过人体」；「**650 亿**」的官方原始表述是「每秒约 650 亿个**太阳中微子**穿过你的**小指甲**」。参赛者文数量级少 1000 倍且指称对象错位 |

## Functional Requirements

| ID | 需求 |
|---|---|
| FR-1 | 创建 bundle 目录 `sheke/industry/zhihu-ai-science-workshop/`，含 `index.md`、`log.md`、`concepts/`（含 `index.md`）、`references/`（含 `index.md`、`article-source.md`、`verification.md`） |
| FR-2 | `references/article-source.md` 承载完整 F 编号事实表，含「已知口径缺口」段与「本表不含推断」声明 |
| FR-3 | `references/verification.md` 承载 P0 核验结论表 + 勘误四张清单过筛记录 + 源文错误与勘误 + flagged 判定 + 单源标注清单 + 证据 URL 全量清单 |
| FR-4 | `concepts/` 下 9 篇内容文档，按事实层 / 机制层 / 路径层组织；事实层逐条挂 F 编号；机制层显式标「洞察/推断」；路径层收益零承诺 |
| FR-5 | `index.md` 最后写，含 frontmatter（`okf_version: "0.2"` / `type: bundle` / `title` / `description`（含 flagged 与「非操作教程」声明）/ `tags` / `generated` / `verified` / `status: flagged` / `stale_after` / `sources`）、阅读地图、内容导航、主题关联互链、已知边界、隐藏 toctree |
| FR-6 | `log.md` 含九个小节：骨架判定 / 归属决策 / 三层结构 / G3 生成顺序 / 双份一致性 / 核验状态 / 防混用对照 / 索引更新 / 结构范式 |
| FR-7 | 三级索引接入：组级 `sheke/industry/index.md`（description + 导航表 + toctree + 束数 29→30）→ 域级 `sheke/index.md`（导航表 + 简介 29→30）→ 总 `bundles/index.md`（`total_bundles` 670→671、计数行、mermaid sheke 75→76、社科域节标题 75→76、社科域分组表 industry 行 29→30） |
| FR-8 | 全量相对链接可达、`UTF-8 strict roundtrip`、双份 F 编号正则比对一致、三级 toctree `Test-Path` 全通 |

## Non-Functional Requirements

| ID | 需求 |
|---|---|
| NFR-1 | 事实层**零因果推断词**（「因为」「导致」「所以」），机制层因果表述必须显式标注为「洞察/推断」 |
| NFR-2 | 所有数字、日期、名称、规则条款与源文逐字一致；金额单位、位次、条数不得转述变形 |
| NFR-3 | 平台自述与独立核验严格分层，单源项必须带标注；`status: flagged` + `stale_after` |
| NFR-4 | 跨活动防混用注记必须出现在涉及「科学季 / AI Works / 奖励结构」的文档中 |
| NFR-5 | 文档路径用相对路径，禁止 `file:///` 绝对路径 |

## Constraints

- OKF v0.2：`type` 为唯一必填字段；`okf_version: "0.2"` **仅**出现在 bundle 根 `index.md`；子目录 `index.md` 需含隐藏 toctree；保留文件名 `index.md` / `log.md`。
- 派生产物 frontmatter 须携带 `source` 字段标注来源。
- 子模块 `projects/awesome-okf-xs/` 为 git submodule，**禁止本地直接修改后提交主仓**——须先在子模块内提交，再在主仓提交 gitlink 指针。
- 提交遵循 Conventional Commits（`type(scope): subject`，主体中文）；修复类提交须标注预防措施类型；**不 push**。
- 数量声明须区分「磁盘现值」与「目录树地面真值」两种口径。

## Assumptions

- A1：源文正文以 CLI 滑窗拼接取得，13 窗口覆盖全文，三段衔接处逐字一致，无缺口——已在 `raw/article-raw.md` 记录窗口重叠校验。
- A2：7 处超链接 href 不可复核这一通道限制为**已知且显式登记**的限制，不据锚文本反推 URL。
- A3：活动窗口（10/9–10/31）内文提到的「今年的诺贝尔奖成果」指 2025 年度诺贝尔奖（2026-10-06 公布）；此为核验推断，源文未写年份。
- A4：后台核验补齐的证据 URL 清单若与首轮结论冲突，以 URL 实证为准并登记新勘误。

## Acceptance Criteria

| ID | 判据（rule） | 判据（rubric） |
|---|---|---|
| AC-1 | `python scripts/check-bundles-index.py` 退出码 0，输出 9 域 / 63 组 / **671 束**，五面一致 | 无 ERROR 行；计数与目录树地面真值完全相等 |
| AC-2 | `python scripts/check-toctrees.py` 退出码 0 | 三级 toctree 全部条目 `Test-Path` 为真，无 orphan / 断链 |
| AC-3 | `python scripts/check-utf8.py` 退出码 0 | 全部产出物 UTF-8 strict roundtrip 通过，无替换字符 |
| AC-4 | spec `facts.md` 与 bundle `references/article-source.md` 的 F 编号集合正则比对完全相等、连续无跳号 | 两侧编号数量相同、集合差集为空、无重复编号 |
| AC-5 | 事实层文档无未标注因果词；机制层因果表述均带「洞察/推断」标记 | 逐篇抽检 G1 判据全部通过 |
| AC-6 | 勘误清单落实：C17 措辞、C15 溯源限定、C13 自我纠错、商汤关联层级、诺奖「650 亿」跨语境标注均在正文显式出现 | 5 项逐条可在正文检索命中 |
| AC-7 | 所有相对链接可达且无 `file:///` 绝对路径 | 逐条 `Test-Path` 通过 |

## Open Questions

- Q1：源文 7 处 href 不可复核 → 是否在 `stale_after` 前补一次浏览器通道复核？（当前受知乎 403 限制，已在 known gaps 登记）
- Q2：活动结束后的获奖名单与真实投稿数据若公开，是否追加「结果层」文档？（本 bundle 只登记活动规则，不登记结果）
