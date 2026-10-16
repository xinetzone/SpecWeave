---
type: specification
title: "微信公众号「美因」逆龄基因药博文转 OKF Wiki"
source: "https://mp.weixin.qq.com/s/J86wj_jTrBpXBiuzf_82JQ"
status: draft
methodology: "seven-concepts R → I → E → V → C"
content-sensitivity: public
---

# 微信公众号「美因」逆龄基因药博文转 OKF Wiki

## Overview

- **Summary**：把一篇微信公众号「美因」发布的抗衰老科普兼带货文（ER-100 基因疗法人体首针 + NMN 补充剂推广），转化为一个可溯源、带时效与可信度分层的 OKF v0.2 知识包。
- **Purpose**：该文混合了真实的衰老研究进展、厂商业绩话术与私域带货转化三类信息。若直接改写，会把「8 周逆转 75%」「纯度 99.99%」等未经独立核验的厂商自宣数字固化为知识库事实，并让读者把一篇带货文当成抗衰指南。本 spec 的目标是**分离三层信息、强制 P0 核验、显式披露商业转化**。
- **Target Users**：对抗衰老/长寿话题感兴趣的普通读者；需要判断保健品营销话术可信度的读者；awesome-okf-xs 知识库维护者。

## Goals

- 在 `projects/awesome-okf-xs/doc/bundles/` 下产出一个结构合规、信源可溯、边界清晰的 OKF bundle。
- 全部数字、日期、金额、机构名与文献引用登记 F 编号，零 facts 之外编造。
- 对厂商自宣类成效数字完成 P0 独立核验，核验失败显式降级，不静默照搬源文错误。
- 完整披露文末私域带货（999 → 649 元/瓶），bundle 不含购买入口与推荐话术。
- 三级索引接入与全库计数同步，机械门禁通过。

## Non-Goals

- 不做医学建议、不做产品推荐、不做「抗衰有效/无效」的总判决。
- 不转录文章全文，不保存原页面图片与 HTML 快照。
- 不新建知识分组（单篇博文不新建分组）。
- 不核验文中 8 篇学术文献的全文内容（只核验文献存在性、作者、年份、期刊与卷页）。
- 不评估基因港/NMN 产品的实际质量或安全性。

## Background & Context

### 内容敏感度预检（步骤 2.3）

| 判定项 | 观察 |
|---|---|
| URL 特征 | `https://mp.weixin.qq.com/s/J86wj_jTrBpXBiuzf_82JQ`，无 `share?code=` / `token=` / 邀请码参数 |
| 域名特征 | 微信公众平台公开页面（`mp.weixin.qq.com`），非企业内部域名 |
| 主题特征 | 公开科普兼带货文，非内部会议/商业培训/个人笔记 |
| 结论 | **公开内容（Public）** → 标准工作流；spec 位于 `.trae/specs/okf-wiki-ecosystem/`，产出物位于 `projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/` |

> 边界说明：文末「读者专属通道」是**文章内容中的商业转化**（公开可读的带货段落），不是访问控制；因此仍走公开工作流，处理方式是「披露转化事实、不复制带货话术、不保留购买入口」。

### 文章元信息（已实测提取）

| 项目 | 值 |
|---|---|
| 标题 | 人类第一针「逆龄基因药」打进人体！8 周细胞生物年龄逆转约 75%，我们即将迎来不老时代？ |
| 公众号 | 美因 |
| 发布日期 | 2026-10-15 13:11 |
| 正文结构 | 6 个小标题段 + 「读者专属通道」带货段 + 参考资料（8 篇文献 + 3 条机构信源） |
| 图文卡片 | 正文含 14 张图片，其中至少 1 张承载「Sinclair 抗衰方案清单」、若干张为文献/共识截图 |
| 提取方式 | `mp.weixin.qq.com` 对 WebFetch 反爬确定失败，已用 browser_use 子代理读 `#js_content`（提取成功） |

### 场景与链路（Method Orchestrator 编排）

本任务是**知识点沉淀场景**，链路 `R → I → E → V → C`：

| 阶段 | 概念 | 本任务动作 | 质量门 |
|---|---|---|---|
| R | Retrospective（事实） | 全文事实采集 → F 编号登记（spec `facts.md`）→ P0 权威核验 → 勘误四张清单 | G1：事实无推断词；P0 逐项过筛 |
| I | Insight（洞察） | 骨架判定（操作可复现性两问）→ 三层知识拆分 → 归属位置论证 | 两问皆「是」才设 examples/ |
| E | Extraction（萃取） | 信源先行生成 bundle（references → concepts → index → log） | G3：信源先行、F 编号引用、index 最后写 |
| V | Adversarial Review（对抗审查） | 四视角审查 + 机械门禁 + 三级索引收尾 | G4：双份 F 编号一致、计数同步、链接可达 |
| C | Atomic Commit（原子提交） | 子模块 → 主仓库双层提交 | 显式文件列表、不 push |

### 信源距离预判

**信源距离类别：厂商自宣 / 带货**。

- 公众号「美因」为膳食补充剂品牌方账号，文末以「私域通道」把 999 元/瓶降为 649 元/瓶，属**厂商自宣**距离。
- 因此：文中**所有成效数字（8 周/75%、寿命近乎翻倍、纯度 99.99%、连续多年供应哈佛实验室）默认 P0 必核验**；index.md 顶部必须加「厂商自述数据」提示块。
- 文中的学术文献引用属**第三方综述/一手文献**层，可作辅助信源，但**不得**把厂商自述升级为研究结论。

### 骨架判定（操作可复现性两问）

| 问 | 判定 | 依据 |
|---|---|---|
| ① 文章是否有读者可照做的安装/配置/代码/实测流程？ | **否** | 全文含「三个选购标准（看纯度/看原料/看科研背书）」，属选购判断而非固定输入—步骤—输出的可复现流程；无实验协议、无版本、无命令、无输入输出 |
| ② 这些流程是否经作者实测、具备可复现性？ | **否** | 无作者实测记录；全部数字来自转述与厂商自述 |

**结论：不设 `examples/`**。bundle 骨架 = `index.md` + `knowledge-map.md` + `concepts/` + `references/` + `log.md`，`description` 标注「非操作教程」。

### 归属位置分析（归属判定决策树）

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `sheke/personal-growth/` | ✅ **选定** | ① 该分组已容纳 4 个同类微信博文转化束（`naval-learn-build-link`、`wechat-presence-joy-meditation`、`wechat-public-expression-lift`、`wechat-certainty-fogg-prompt`），形态完全一致：单源二手内容 + 商业转化披露 + flagged/draft 状态；② 分组说明明确收录「跨书籍的综合方法论与实操教程」及「单篇公开文章原创教程」，`guard-quality-life` 已含「健康」域、`how-to-live-better` 已含「循证健康决策」，健康类个人决策先例充分 |
| `yixue/` | ❌ | yixue 域自设收录边界为「古籍文献学习资料」并附医学免责声明，其域总览明示「现代性学著作归 sheke 域」——现代生命科学资讯不属其收录范围；该域 6 个分组（tcm/huangdi-neijing/medicine/daoyi/yangsheng/fangzhong）全部为典籍阅读类，语义不符 |
| `sheke/industry/` | ❌ | 该分组定位为「AI 行业快照分析」，文章主线是抗衰科学与保健品，非 AI 行业商业趋势 |
| `kexue/` | ❌ | kexue 域为化学/物理/数学经典元典与前沿资讯速报（数学），无现代生命科学资讯位 |
| `sheke/marketing/` | ❌ | 文章虽有厂商自宣层，但主线实体是「抗衰老干预」，营销只是承载形式；按「主线实体优先」不落营销组 |
| 新建分组 | ❌ | 单篇博文不新建分组，违反最小变更原则，会造成目录体系碎片化 |

**bundle 路径**：`projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/wechat-anti-aging-er100-nmn/`

### 知识地图（三层知识拆分预案）

| # | 文件 | 层 | 内容定位 |
|---|---|---|---|
| 00 | `concepts/00-er100-first-in-human.md` | 事件时间线层（What/When/Who） | ER-100 与 Life Biosciences、Sinclair 身份、1 月 FDA 批准 → 3 月首例注射 → 10 月一期数据的时间线、动物实验口径（75%/寿命翻倍）、「先选眼睛」的临床设计边界 |
| 01 | `concepts/01-aging-information-theory.md` | 驱动逻辑层（Why） | 衰老信息论（表观基因组信息丢失 vs 机械磨损隐喻）、OSK 三基因部分重编程、为何 6–8 周自动停下、Sinclair「不会变老还会得阿尔茨海默吗」反问的观点属性 |
| 02 | `concepts/02-nad-nmn-pathway.md` | 驱动逻辑层（Why） | NAD+ 作为供能与修复原料、40 岁前后水平口径、NMN 作为直接前体、2013 年 NMN 研究溯源、共识与文献的存在性核验结果 |
| 03 | `concepts/03-cost-and-access-timeline.md` | 可及性层 | 单次 >10 万美元的构成与来源、口服小分子动物实验、2035–2040 预期、生殖衰老旁证、从眼睛到全身 5–10 年 |
| 04 | `concepts/04-supplement-claims-and-reading-discipline.md` | 商业与迁移层 | 基因港/王骏背景、全酶法/99.99%/纯 β 型等厂商自宣声明逐条分层、三个选购标准、带货漏斗识别与保健品内容阅读纪律 |
| — | `knowledge-map.md` | 三层汇总 | 事实层 / 机制层（单源须标注为假设）/ 迁移层 + 四元组洞察 |

### 候选事实清单（待 R 阶段正式编号，预估 F-001 ~ F-060）

以下为需要在 R 阶段登记与核验的候选声明，按主题聚类（**本表仅为规划，正式编号与状态在 `facts.md` 落地**）：

| 主题 | 候选声明 | 预估核验级别 |
|---|---|---|
| 事件 | ER-100 出自 David Sinclair 联合创办的 Life Biosciences；1 月 FDA 批准、3 月第一位患者注射、10 月一期数据公布；安全性良好、两名受试者出现视力改善迹象 | **P0**（日期/官方表态） |
| 数字 | 动物实验 6–8 周细胞生物年龄回退约 75%；垂暮小鼠剩余寿命近乎翻倍；恶性肿瘤细胞失去失控增殖特征、部分凋亡 | **P0**（成效数字，厂商/媒体自宣） |
| 机制 | 衰老信息论；表观基因组「谁开谁关」错乱；OSK 三基因重编程；6–8 周后自动停下、不会退回胚胎状态 | P1（能力声明，可挂文献） |
| 机制 | 同一组基因让失明视网膜重新感光；多发性硬化、肝病模型好转；植入人类阿尔茨海默基因小鼠症状消退 | P1（动物模型声明） |
| 反转述 | Sinclair 反问「如果你从来不会变老，你会得阿尔茨海默症吗」 | **P2**（须显式标注「信源转述/作者观点」） |
| 时间线 | 从眼睛到全身业内普遍认为至少还要 5 到 10 年 | P1（行业预期，非承诺） |
| 成本 | 单次干预费用预计超过 10 万美元；口服小分子制剂已在动物实验成功；面向大众的逆龄口服药有望 2035–2040 问世 | **P0**（金额/时间） |
| 旁证 | 已停止排卵的老年雌性动物干预后卵巢功能与卵子质量恢复迹象、重新产下健康后代 | **P0**（成效数字） |
| NAD+ | 人到 40 岁前后体内 NAD+ 水平大约只剩 20 岁时的一半 | **P0**（数量口径） |
| 溯源 | 2013 年 Sinclair 实验室首次证实补充 NMN 可提升 NAD+ 水平 | **P0**（年份/首发声明，对照文献[3]） |
| 共识 | 2026 年中华医学会老年医学分会发布《NAD+ 在衰老相关疾病中的作用及临床应用中国专家共识》，把器官 NAD+ 逐年衰减列为共同生理基础，明确口服 NMN 是安全便捷补充途径之一 | **P0**（官方表态，**高度可疑须重点核验**） |
| 文献 | 参考资料列 8 篇文献（Cell 2023 / Nature 2020 / Cell 2013 / Cell Metabolism 2016 / Science 2017 / Endocrine Journal 2020 / Science 2021 / 中华老年医学杂志 2026） | **P0**（存在性 + 作者/年份/期刊/卷页逐项） |
| 厂商 | 基因港创始人王骏博士是 1975 年诺贝尔生理学或医学奖得主霍华德·特明的学生、前香港中文大学医学院教授、深耕生物合成 30 余年、带队实现全球首个全酶法 NMN 工业化量产 | **P0**（人物履历，可独立核验） |
| 厂商 | 基因港连续多年为哈佛 Sinclair 实验室供应 NMN 原料用于衰老研究 | **P0**（厂商自宣，须找独立出处，无出处即标「厂商自述」） |
| 厂商 | 全酶法绿色合成无化学溶剂、纯度稳定 99.99% 以上、纯 β 型天然构型、无内毒素/无化学残留、植物素食胶囊、一物一码可溯源 | P1（产品自宣，正文须标「厂商自述」） |
| 商业 | 公域统一价 999 元/瓶；本文私域通道特惠 649 元/瓶；本品为膳食营养补充剂不能替代药物；未成年人/孕妇/哺乳期/长期服药/重症人群建议咨询医生 | **P0**（价格时点）+ 边界事实 |
| 源文瑕疵 | 正文「人体目前只是第一步……」整段在第二节与第三节重复出现；「David Sinclair」介绍段重复出现 | 编辑瑕疵，须在 verification 单列注记 |

## Functional Requirements

- **FR-1**：产出 OKF v0.2 bundle `wechat-anti-aging-er100-nmn`，位于 `projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/`，含 `index.md`、`knowledge-map.md`、`concepts/`（5 篇 + index）、`references/`（article-source.md + verification.md + index）、`log.md`。
- **FR-2**：图文卡片中的事实（尤其「Sinclair 抗衰方案清单」）须经视觉识读后**转述**入库；图片本身不入库，临时图片文件用完即删。
- **FR-3**：全部具体声明引用 F 编号；F 编号在 spec `facts.md` 与 bundle `references/article-source.md` 双份登记且集合一致。
- **FR-4**：P0 声明逐项核验并给出独立权威 URL，或显式标注 `single-source` / `single-source/flagged`；核验发现源文错误时新增 F 编号记正确值，`verification.md` 单列勘误，正文呈现正确值并标注源文口径。
- **FR-5**：`index.md` 含「内容边界」段，显式披露：厂商自述数据提示块、私域带货转化（999→649）、非医疗建议声明、`status` 与 `stale_after` 依据。
- **FR-6**：接入三级索引——`sheke/personal-growth/index.md` 导航表加行 + toctree 追加 + 计数；`sheke/index.md` 分组说明与束数更新；`bundles/index.md` 的 `total_bundles`、域束数、组束数与正文数字同步（现为 635 / 61 / 9）。
- **FR-7**：`log.md` 记录创建、核验、勘误与索引变动；`stale_after` 设为 2027-06-30（价格与共识类信息时点敏感，短于一般年末设置）。
- **FR-8**：`status` 依核验结果定档——若「中华医学会共识存在性」或「8 周/75% 口径」等**核心声明**核验失败且无法给出正确值，置 `status: flagged` 并在 verification 顶部明示；非核心声明失败可 `stable` + 完整勘误。

## Non-Functional Requirements

- **NFR-1 可溯源性**：正文零「facts 之外」的数字/模型名/机构名；观点与事实分层，作者/信源观点显式标注。
- **NFR-2 合规性**：不发医学建议、不做产品推荐、不提供购买入口、不复制带货话术；只处理公开可观察内容，不镜像全文。
- **NFR-3 结构一致性**：三级 index 均含 `{toctree}` 块；每篇非保留 `.md` 含非空 `type` 的合法 YAML frontmatter。
- **NFR-4 语言与命名**：正文中文，文件名 kebab-case 纯英文。
- **NFR-5 幂等性**：开工前先查目标 bundle 目录与 spec 目录是否已存在；已存在时读 `log.md`/`index.md` 判定为「更新/补核验」还是「重建」，禁止静默覆盖；索引计数先读现值再 +1。

## Constraints

- **技术**：产出位于 `projects/awesome-okf-xs`（git submodule），spec 位于主仓库 `.trae/specs/`，提交需分层；`invoke gates.*` 依赖 `invocations`（optional-dependencies.doc），环境未装时**必须走 §7 手动等效验证清单并在 log.md 注明，禁止谎报「gates 通过」**。
- **技术**：`mp.weixin.qq.com` 对 WebFetch 反爬确定失败，采集走 browser_use 子代理。
- **技术**：交叉引用一律相对路径，禁止 `file:///` 绝对路径；引用本仓外路径时用 `~/` 替代家目录绝对路径。
- **业务**：不修改 `projects/awesome-okf-xs/doc/bundles/` 之外的子模块内容；不新建分组。
- **依赖**：核验依赖 WebSearch 权威来源（Life Biosciences 官网、FDA/ClinicalTrials.gov、中华医学会期刊官网、PubMed/DOI、基因港官网）。

## Assumptions

- 文末 8 篇文献的标题与卷页抄录自文章，可能存在转述误差，故文献核验只做「存在性 + 元数据」而非全文比对。
- 「美因」为品牌方公众号（带货主体），按厂商自宣距离处理；若后续证实为第三方媒体转述，仍按保守层级处理（就高不就低）。
- 14 张图片的视觉识读结论可能与正文文字重复，重复内容不重复编号。

## Acceptance Criteria

### AC-1: 双份 F 编号一致且连续
- **Type**: `rule`
- **Given**: spec `facts.md` 与 bundle `references/article-source.md` 各自维护 F 编号表行
- **When**: 用正则 `^\|\s*\|\s*F-(\d{3})\s*\|`（或等价锚定模式）分别提取两侧编号集合
- **Then**: 两集合相等且连续，无跳号；如有跳号须有显式注记
- **Pass Condition**: 集合相等 && 无未注记跳号
- **Evidence**: 两侧提取结果与比对输出，写入 `log.md` 与 `review.md`

### AC-2: 正文零 facts 之外编造
- **Type**: `rule`
- **Given**: bundle 全部 concepts 与 knowledge-map 正文
- **When**: 逐一比对文中数字/日期/金额/机构名/文献引用与 `facts.md` 条目
- **Then**: 每个具体声明均可回溯到 F 编号；观点段有「作者观点/信源转述」标注
- **Pass Condition**: 零无出处具体声明，零观点与事实混同
- **Evidence**: 抽查记录 + 抽样清单

### AC-3: P0 核验覆盖率 100%
- **Type**: `rule`
- **Given**: `facts.md` 中标为 P0 的声明（成效数字、日期时间线、金额、价格、共识与文献存在性、人物履历）
- **When**: 逐项检索独立权威来源
- **Then**: 每项给出独立权威 URL，或显式标注 `single-source` / `single-source/flagged`；零「硬编 URL」的假核验
- **Pass Condition**: P0 项核验状态字段 100% 填写且无可疑空缺
- **Evidence**: `references/verification.md` 的核验表（含 ✅/⚠️/❌ 统计）

### AC-4: 源文错误不静默照搬
- **Type**: `rule`
- **Given**: 核验发现的源文错误（含正文重复段落等编辑瑕疵）
- **When**: 检查 `verification.md` 与相应 concepts 正文
- **Then**: 新增 F 编号记录正确值与差异；`verification.md` 单列「勘误」；正文呈现正确值并标注源文口径；无法核验的标「仅博文单源」
- **Pass Condition**: 勘误条目零遗漏，正文无照搬的错误值
- **Evidence**: `verification.md` 勘误小节 + 对应正文段落

### AC-5: 商业转化完整披露且不复制带货话术
- **Type**: `rule`
- **Given**: 文末「读者专属通道」段（999→649 元/瓶私域价）
- **When**: 检查 bundle `index.md` 内容边界段与专篇正文
- **Then**: 带货事实被显式登记与披露；bundle 内零购买入口、零推荐话术、零「领取专属价」类引导
- **Pass Condition**: 披露存在 && 引导话术零命中
- **Evidence**: index 内容边界段文本 + 全 bundle 关键词检索结果

### AC-6: 厂商自宣与独立核验事实分层呈现
- **Type**: `rule`
- **Given**: 厂商自宣类声明（纯度 99.99%、连续多年供应哈佛实验室、全酶法量产等）
- **When**: 检查相应 concepts 正文与 index 提示块
- **Then**: 每项标注「厂商自述」或「无独立出处」；index 顶部有「厂商自述数据」提示块
- **Pass Condition**: 标注覆盖率 100% && 提示块存在
- **Evidence**: 标注清单 + index 提示块文本

### AC-7: 三级 toctree 完整且条目逐一可达
- **Type**: `rule`
- **Given**: bundle 根 `index.md`、`concepts/index.md`、`references/index.md`
- **When**: 提取 toctree 条目（排除 `:` 开头的指令行）并逐一 `Test-Path` 对应文件
- **Then**: 每个 index 均含 toctree 块；全部条目对应真实文件存在；根 index 收录 `concepts/index`、`knowledge-map`、`references/index`、`log`
- **Pass Condition**: 零缺失文件、零缺 toctree 块
- **Evidence**: 检查器输出

### AC-8: 全库计数三处同步
- **Type**: `rule`
- **Given**: `bundles/index.md` 的 `total_bundles` / 域束数 / 组束数，与 `sheke/index.md`、`sheke/personal-growth/index.md` 的导航表行数与 `total_bundles`
- **When**: 新增一束后重新统计并比对
- **Then**: `total_bundles` 635 → 636；personal-growth 组 14 → 15；sheke 域 67 → 68；正文 prose 数字同步
- **Pass Condition**: 三处（frontmatter 计数行 / 人类导航表束数列 / 机器 toctree 条目）数字一致
- **Evidence**: `invoke gates.bundles` 输出或 `scripts/check-bundles-index.py` 输出

### AC-9: UTF-8 严格解码、无绝对路径残留
- **Type**: `rule`
- **Given**: 全部新增/修改 `.md` 文件
- **When**: 用 strict 模式 UTF-8 解码；Grep `file:///`、`/Users/`、`C:\Users\`
- **Then**: 全部解码成功；绝对路径与家目录路径零命中
- **Pass Condition**: 解码 100% 成功 && 命中数 = 0
- **Evidence**: `invoke gates.utf8` 或 `scripts/check-utf8.py` 输出 + Grep 结果

### AC-10: Frontmatter 齐备且双信源
- **Type**: `rule`
- **Given**: bundle 根 `index.md` 与各子文档 frontmatter
- **When**: 逐项检查 `okf_version`/`type`/`title`/`description`/`tags`/`generated`/`verified`/`status`/`stale_after`/`sources`
- **Then**: 字段齐备；`sources` 同时含博文 URL 与至少一条核验权威 URL
- **Pass Condition**: 字段缺失数 = 0 && 双信源存在
- **Evidence**: frontmatter 抽样清单

### AC-11: bundle 读者可用性与边界清晰（评价性）
- **Type**: `rubric`
- **Dimension**: 读者能否在不被误导的前提下理解「已知 / 厂商自述 / 未知」三类边界
- **Scale**: 1-5
- **Anchors**: 1 = 事实与厂商话术混杂、读者会把带货文当抗衰指南；3 = 有边界声明但分层不彻底，个别数字仍未标注来源距离；5 = 事实层/机制层/迁移层清晰分离，每项厂商自述与未核验数字均可一眼识别，且有迁移性阅读纪律
- **Pass Threshold**: >= 4
- **Evidence**: 独立审查者通读 5 篇 concepts + knowledge-map 的分层评估与理由

### AC-12: 产出结构合规且门禁可复现（评价性）
- **Type**: `rubric`
- **Dimension**: OKF v0.2 结构合规度与门禁可复现性
- **Scale**: 1-5
- **Anchors**: 1 = 结构缺失、门禁未跑也未做等效验证就声称通过；3 = 结构合规但门禁走手动清单时未在 log 注明；5 = 结构完全合规，`invoke gates.*` 或手动等效验证均执行且结论如实记入 `log.md`
- **Pass Threshold**: >= 4
- **Evidence**: `log.md` 的门禁记录 + 独立审查复核

## 关联 bundle 先例

- [wechat-certainty-fogg-prompt/](../../../../projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/wechat-certainty-fogg-prompt/)（同分组微信博文转化束：单源标注、商业转化披露、knowledge-map 结构参考）
- [naval-learn-build-link/](../../../../projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/naval-learn-build-link/)（flagged 状态与「源文框架对勘」参考）
- [wechat-presence-joy-meditation/](../../../../projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/wechat-presence-joy-meditation/)（健康/身心类内容 + 非医疗边界声明的 stable 先例）
- [guard-quality-life/](../../../../projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/guard-quality-life/)（健康域 + 证据分级 A·B·C 先例）
- [how-to-live-better/](../../../../projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/how-to-live-better/)（P0 核验 + 证据分级双轴方法参考）
- [blog-article-to-okf-wiki](../../../../.agents/skills/blog-article-to-okf-wiki/SKILL.md)（七阶段工作流与勘误四张清单权威规范）

## Open Questions

- [ ] 「2026 年中华医学会老年医学分会《NAD+ 在衰老相关疾病中的作用及临床应用中国专家共识》」是否真实存在？若查无实据 → 新增 F 编号记「未检索到」，`verification.md` ❌ + 勘误，正文改述为「源文宣称存在该共识，未获独立证实」；若属实 → 补官方 DOI/期刊链接。此结论直接影响 AC-8 的 `status` 定档。
- [ ] 「6 到 8 周细胞生物年龄回退约 75%」的原始出处与统计口径（是表观遗传时钟读数、单一器官还是多器官、小鼠还是灵长类）？需与 Life Biosciences 官方公告口径对照，警惕「拔高与省略」类型口径错误。
- [ ] 14 张图文中「Sinclair 抗衰方案清单」的具体条目内容——只有视觉识读可得，正文文字未给出。识读结果若与正文冲突，以公开权威来源为准并勘误。
- [ ] 若 `invocations` 依赖不可用且手动等效验证出现无法覆盖的门禁项，是否接受以 `blocked` 记录并在 `review.md` 留痕？
