---
type: Pattern
id: pattern-blog-article-to-okf-bundle
title: 博文类文章→OKF知识包转化模式
date: 2026-08-28
last_updated: 2026-08-29
source:
  - spec-deepseek-vision-blog-okf-wiki-20260828
  - spec-bytedance-ai-consolidation-blog-okf-wiki-20260828
  - milestone-blog-to-okf-bundle-12posts-20260829（12 篇批量转化复盘，84 项 P0 核验）
maturity: validated
maturity_level: L3
validation_count: 13
reuse_count: 11
tags: [博文转化, OKF, 知识包, 模型选型, 知识沉淀, 信源溯源, 商业分析, 事实核验, P0核验, 勘误模式]
pattern_type: methodology
category: documentation
---

# 博文类文章→OKF知识包转化模式

## 触发场景

当用户提供博文/资讯类文章 URL（微信公众号文章、技术博客、新闻稿、产品发布资讯等），要求将其转化为 OKF wiki 教程/知识包时。此类任务的特征：

- **无本地源码**：信源是单篇外部文章（URL），不存在可遍历分析的 vendor/源码目录
- **信源单一**：全部事实来自同一篇文章，需要 F 编号登记 + 单源声明管理
- **含时效性信息**：价格、版本号、发布资讯、免费政策等会随时间失效的内容
- **混杂作者观点**：选型建议、总结口诀等主观判断与客观事实交织，需区分处理

**与源码类转化（source-code-to-okf-wiki Skill）的区别**：

| 维度 | 源码类转化 | 博文类转化（本模式） |
|------|-----------|---------------------|
| 信源形态 | 本地 vendor 源码，结构可遍历 | 单篇外部 URL，内容一次性读取 |
| 事实来源 | 源码 + 官方文档，天然权威 | 博文叙述，需核验升级可信度 |
| 时效性 | 代码相对稳定，弱时效 | 价格/版本/发布信息快速过期 |
| 结构推导 | 从目录/模块层次推导章节 | 从文章叙述层次提炼三层知识 |
| 归属判定 | 源码仓库名即归属锚点 | 文章主线实体需决策树判定 |
| 可信度管理 | 源码即事实 | 区分博文事实/核验事实/作者观点 |

**Skill 门面**：本模式已封装为可自动触发的 Skill [`blog-article-to-okf-wiki`](../../../../.agents/skills/blog-article-to-okf-wiki/SKILL.md)（L1 门面：触发词 + 七阶段骨架 + 安全清单；本文件为 L2 完整方法论，判据以本文件为准）。信源为本地源码目录时使用姊妹 Skill [`source-code-to-okf-wiki`](../../../../.agents/skills/source-code-to-okf-wiki/SKILL.md)。

## 核心步骤

### 步骤1：内容敏感度预检（工作流分流）

1. 检查 URL 特征：微信公众号公开文章、公开技术博客、官方新闻页等无访问控制内容 → **公开**；含 `share?code=`/`token=`/邀请码等访问控制参数、企业内部域名 → **私域**
2. 公开内容 → 标准工作流：spec 位于 `.trae/specs/<theme>/`，产出物位于 OKF bundles 目录
3. 私域内容 → 私域工作流：跳过 `.trae/specs/` 公共规划区，产出物直接放 `playground/` 对应用户目录（或用户指定目录）
4. 不确定时默认按私域处理，或向用户确认
5. **产出**：敏感度判定结论写入 spec 的"内容敏感度预检"段落

### 步骤2：内容性质分流与骨架判定（决定目录骨架）

归属判定之前，先判定文章内容性质。

**L3 核心判据——examples/ 的取舍不看"是否技术"，看"操作可复现性"两问**（源自 12 篇批量验证：threeui 开源组件库、a2a-mcp 协议综述均为硬核技术内容但正确地无 examples/）：

1. 博文中是否有读者可照做的安装/配置/代码/调用/实测流程？
2. 这些流程是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？

**两问皆"是" → 设 examples/**；任一为"否" → 无论主题多技术，均用概念骨架（examples/ 为空制造伪结构比没有更糟）。

内容性质对照表（辅助判定）：

| 内容性质 | 识别特征 | 目录骨架 | frontmatter |
|---------|---------|---------|-------------|
| **技术教程/选型** | 含可复现操作步骤：API 调用、安装配置、代码/实测流程、可演练决策工具 | index + concepts/ + examples/ + references/ + log | type: bundle |
| **技术综述/资讯盘点** | 主题是技术但形态为观点/盘点/趋势分析，无可复现步骤（正例：a2a-mcp 协议综述、threeui 组件盘点） | index + concepts/ + references/ + log（**无 examples/**） | type: bundle，description 标注"技术综述/资讯，非操作教程" |
| **商业分析/战略资讯** | 组织架构、市场格局、资本开支、作者观点为主 | index + concepts/ + references/ + log（**无 examples/**） | type: bundle，description 显式标注"商业分析/战略资讯，非源码教程" |
| **资讯速报** | 单一事件、事实简短、无方法论 | index + references/ + log（concepts 可仅 1 篇） | stale_after 缩短至 1-2 月 |

**分组 index 接入规则**：非源码教程类不要硬塞进分组既有的"源码教程/学习资源"板块；若分组已有板块语义不符，新增一个分类（如"📰 战略资讯"），并在分组导语说明该类 bundle 的方法论链路（博文核验 R→I→E→V，区别于源码教程的源码深读 R→I→E→V→C）。

### 步骤3：归属判定决策树

按以下顺序判定 bundle 落位：

1. **文章主线实体优先**：文章围绕哪个实体展开（如 DeepSeek 主线 → `ai/deepseek` 分组）；"A+B 协作"类文章以承担核心角色（推理/主流程）的实体为归属锚点
2. **查分组内非源码类 bundle 先例**：确认目标分组已有资源列表、应用模型介绍、API 教程等非源码类 bundle（证明分组可容纳博文转化产物）；存在可交叉引用的既有 bundle 更佳
3. **单篇博文禁止新建分组**：一篇博文新建顶级分组属过度工程，违反最小变更原则——一律落入既有分组
4. **主线不明时列候选位置对照表**：在 spec 中给出"候选位置 | 判定 | 理由"表格（含排除理由）向用户论证
5. **产出**：spec 中的"归属位置分析"段落 + 选定 bundle 路径

### 步骤4：事实采集（R 阶段）

0. **信源获取**：微信公众号文章（`mp.weixin.qq.com`）WebFetch 通常被反爬拦截，直接使用 browser_use 子代理提取全文；其他公开博客优先 WebFetch/Defuddle，失败再回退 browser_use。
1. 全文通读博文，提取所有可验证事实（模型名、价格、格式支持、能力声明、模式描述、组织变动、数字声明）
2. **F-001 起编号**登记到 spec 的 `facts.md`，按主题分组（元信息/推荐事实/落地模式/总结），每条可标注原文位置
3. **区分客观事实与作者观点**：观点条目显式标注"作者观点"，防止后续被转述为事实；外媒转述（如"据彭博/雅虎报道"）标注转述层级
4. **信源距离预判**（L3 新增，核验前必做）：转化前先标注博文性质——官方发布 / 作者一手实测 / 开源项目文档 / 第三方综述 / **厂商自宣**（作者即厂商主体或厂商赞助报道）。12 篇批量验证规律：核验失效率与"营销叙事浓度"正相关、与技术深度无关——4 项 ❌ 硬性错误全部出自厂商自宣或二手转述文章，一手实测/官方发布类零错误。厂商自宣类的**所有成效数字（提效倍数、节省工时、成本下降）默认 P0 必核验**，且 bundle index 顶部加"厂商自述数据"提示块。
5. **关键声明核验**（WebSearch 权威来源）：
   - **P0 必核验**：数字/金额/日期、官方表态、产品发布与功能时间线、成效数字（这些是博文最易出错且最影响决策的声明）
   - **P1 选核验**：模型能力、市场份额等难以快速权威证实的声明
   - **P2 可单源**：背景叙述、作者明确标注的个人观点
   - **勘误四张清单**（L3 新增，P0 核验逐项过筛；12 篇 25 项问题全部收敛于此四类）：
     | 清单 | 核验要点 | 典型反例 |
     |------|---------|---------|
     | ① 日期/版本表 | GA/发布日期、模型版本号、年份归属逐项对官方源 | AWS AgentCore GA 日期误安到 2026-08（实为 2025-10-13）；Wan2.5 实为 2.7；采购额年份错配 |
     | ② 成效数字溯源表 | 提效倍数/节省工时/成本下降须找到原始出处；无出处即 ❌ | "10倍效率/30%吞吐"无权威来源且归因失实；"官方预置连接器"无任何官方证据 |
     | ③ 口径对照表 | 规模数字核对地域/时间/统计口径限定词，警惕拔高 | "900余款/600余家" vs 官方"超800款/500余家"且省略"中国"限定；以偏概全的百分比 |
     | ④ 引文逐字核对表 | 官方定位/高管引语须核对原文，意译不得加引号；报告须查发布方身份（厂商赞助须披露） | A2A 官方"complement MCP"被意译为"not a replacement"；西门子联合发布报告被写成独立第三方 |
   - 核验通过 → 补充官方信源 + 核验补充事实（续 F 编号），在 facts.md 记录核验结论与差异说明
   - **核验发现源文错误**（如年份错配、口径混淆）→ 不得静默照搬，新增 F 编号记录正确值与差异，在 references/verification.md 单列"勘误"，bundle 正文呈现正确值并标注源文口径
   - 无法核验 → 标注"仅博文单源"，引用时需提示读者甄别
6. **产出**：`facts.md`（唯一合法事实集）+ 核验记录

### 步骤5：知识结构三层拆分（I 阶段）

按内容性质映射 concepts 篇目：

- **技术教程/选型类**：
  1. 发布事实层：事件本身（模型发布、API 能力、能力边界）→ concepts 首篇
  2. 选型矩阵层/方法论层：核心方法论（场景×推荐矩阵、选型维度框架）→ concepts 中部
  3. 架构模式层：文章提出的架构/协作模式 → concepts 尾篇
  4. 示例与决策工具（演练、结构设计、决策树）→ examples
- **商业分析/战略资讯与技术综述/资讯盘点类**（均无 examples，按步骤2"操作可复现性两问"判定）：
  1. 事件时间线层（What/When/Who）→ concepts 首篇
  2. 驱动逻辑层（Why：成本、战略、因果链；技术综述类为机制/协议/架构原理）→ concepts 中部（因果分析属作者洞察，须与事实分层）
  3. 竞争/格局层（外部对标、市场位置；技术综述类为生态/趋势研判）→ concepts 尾篇
  4. 无 examples；Mermaid 组织架构/时间线/协议交互图可放入 concepts
- **产出**：知识地图（concepts 篇目清单 + examples 清单或"无 examples"理由及两问判定记录），写入 spec 的 ADDED Requirements

### 步骤6：bundle 生成（E 阶段）

1. 目录结构按步骤2骨架判定：含可复现操作的 `index.md` + `concepts/` + `examples/` + `references/` + `log.md`；商业分析/技术综述/资讯盘点类无 `examples/`，并在 index.md 顶部显著声明内容性质（"商业分析/战略资讯，非源码教程"或"技术综述/资讯，非操作教程"）（+ 各子目录 index.md）
2. **信源先行**：先写 references（博文事实清单 + 核验报告），再写 concepts、examples
3. **所有具体声明引用 F 编号**：数字/模型名/API 声明/组织变动必须有 F 出处，禁止 facts.md 之外的编造；作者观点引用其 F 编号时保留"作者观点"标注
4. 伪代码/推导内容显著标注"**非官方**"
5. **时效性声明双落地**：index.md 已知边界（实验版本、价格时点、弱信源、单源声明、资讯时效）+ frontmatter `stale_after` 字段
6. frontmatter 遵循 OKF v0.2（okf_version/type/title/description/tags/generated/verified/status/stale_after/sources），`sources` 同时指向博文 URL 与核验权威 URL（多信源时全部列出）
7. **核验失败的状态管理**（L3 新增）：P0 核验出现 ❌ 且失败项为博文**核心声明**（文章主结论/主推事实）时，bundle frontmatter `status: flagged`，verification.md 顶部明示含失败项与影响范围，index.md 已知边界段提示；非核心声明失败可用 status: stable 但勘误必须完整。flagged bundle 在 stale_after 前须安排一次复核（证实/证伪后更新状态）。正例：tushare-ai-office（"官方预置连接器"核心声明无证据 → flagged）。
8. **同主题多 bundle 互链**（L3 新增）：同一主题多篇博文产出多个 bundle 时（如豆包工作主题簇：实测篇/上下文层篇/组织生产力篇），各 bundle index.md 增加"主题关联"段，两两互链并说明分工差异，防止同主题知识碎片化。
9. **产出**：完整 bundle 文件集 + log.md 生成记录

### 步骤7：对抗审查与索引收尾（V 阶段）

1. **四视角对抗审查**全部内容文档：
   - 事实溯源：逐条比对 F 编号，无 facts.md 之外的数字/模型名；核验勘误是否在正文落实（不得照搬源文错误数字）
   - 结构规范：frontmatter 完整、toctree 覆盖、Mermaid 语法合规
   - 读者可用性：相对链接逐一验证可达、内容可独立 follow
   - 时效边界：单源声明、价格时点、弱信源、观点/事实分层到位
2. **事实编号双份登记一致性核对**（L3 新增）：spec `facts.md` 与 bundle `references/article-source.md` 存在两份 F 编号登记，V 阶段必须正则提取两边编号集合比对——编号须连续无跳号（跳号须在 facts.md 显式注记"预留/跳用"原因）；V 阶段补充的核验事实若不回转 article-source，须在 log.md 注记原因（批量验证中曾出现 460 vs 458 漂移与 F-028 跳号瑕疵）
3. **父级分组 index 接入**：导航表新增条目 + toctree 追加 + 分组束数计数；非源码教程类按步骤2规则决定新增分类或归入既有板块
4. **全库计数同步**：`bundles/index.md` 域束数与 total_bundles 同步 +1（含正文计数），核对 frontmatter 与正文数字一致
5. **溯源补全**：引用核验事实的子文档 frontmatter `sources` 补充权威信源条目
6. **门禁验证**：
   - **环境前置**：`invoke gates.*` 依赖 `pyproject.toml` 的 `[project.optional-dependencies].doc`（含 `invocations>=4.0`），需 `pip install -e ".[doc]"` 后才能运行
   - 依赖可用时运行 `invoke gates.toctrees` 与 `invoke gates.utf8`（无孤立文档、无断链、编码合规）
   - **依赖不可用时禁止直接声称"gates 通过"**，必须执行清单化手动等效验证并在 log.md 注明：① 三级 toctree 条目逐一对应存在文件 ② Grep 出全部 .md 相对链接逐一核对目标存在 ③ PowerShell `UTF8Encoding(strict)` 解码全部 md 文件 ④ spec/bundle 双份 F 编号集合比对（见本步骤第 2 条）
7. **产出**：审查修复记录（log.md）+ 接入完成、可达可溯源的知识包

## 演示案例（demo）

**案例**：微信公众号"湖北"博文《DeepSeek 多模态视觉实验模型发布！》（2026-08-21）→ `ai/deepseek/vision-model-selection/` bundle（2026-08-28 完成）

- 完整方案：[spec.md](../../../../.trae/specs/okf-wiki-ecosystem/deepseek-vision-blog-okf-wiki/spec.md)
- 事实集：[facts.md](../../../../.trae/specs/okf-wiki-ecosystem/deepseek-vision-blog-okf-wiki/facts.md)
- 产出物：[vision-model-selection/index.md](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/deepseek/vision-model-selection/index.md)

### 逐步对照（案例1：技术选型类）

**步骤1 对照**：微信公开博文 URL（`mp.weixin.qq.com`，无访问控制参数）→ 公开内容 → 标准工作流（spec 位于 `.trae/specs/okf-wiki-ecosystem/deepseek-vision-blog-okf-wiki/`，产出物位于 `projects/awesome-okf-xs/doc/bundles/`）。

**步骤2 对照（性质分流）**：博文含 API、模型参数、价格表、可演练选型决策 → 判定为**技术教程/选型类** → 骨架含 `examples/`。

**步骤3 对照**（候选位置对照表，摘自 spec）：

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `ai/deepseek/`（选定） | ✅ | ① 主线是 DeepSeek 视觉模型发布，双模型管线中 DeepSeek 负责推理判断；② 分组内已有非源码先例（`awesome-deepseek-agent` 资源列表、`deepseek-ocr`/`deepseek-ocr2` 应用模型），文中推荐的 DeepSeek-OCR-2 已有 bundle 可交叉引用；③ 分组定位可自然扩展为"DeepSeek 模型生态" |
| `ai/agnes-ai/` | ❌ | 特定厂商（AgnesAI）平台教程，主题不符 |
| `ai/ai-agent/` | ❌ | Agent 框架源码解读，主题不符 |
| `ml/` | ❌ | ONNX 模型生态，聚焦模型交换格式与推理后端 |
| 新建分组 | ❌ | 单篇博文新建分组属过度工程，违反最小变更原则 |

**步骤4 对照**：共 **36 条事实**（F-001 ~ F-033 来自博文 33 条 + F-034 ~ F-036 核验补充 3 条）；F-032 显式标注"作者观点"；完成**三项关键声明官方核验**：

| 核验对象 | 官方来源 | 结论 |
|---------|---------|------|
| DeepSeek-V4-Flash-Vision-Exp 发布信息 | DeepSeek 官方新闻（api-docs.deepseek.com） | ✅ 通过，补充官方细节 F-034（单图 384 tokens） |
| GLM-4.6V-Flash 免费 + FlashX 定价 | 智谱官方文档 + z.ai 定价页 | ✅ 通过，价格与博文完全一致 |
| Doubao-Seed-2.0-mini 模态与价格 | 火山引擎官方价格文档 | ✅ 通过，含阶梯定价细节 F-036 |

Gemini 2.5 Flash-Lite、GPT-5 nano、MiniCPM-V 4.6、DeepSeek-OCR-2/GLM-OCR 相关声明标注"仅博文单源"。核验详情见 [references/verification.md](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/deepseek/vision-model-selection/references/verification.md)。

**步骤5 对照**（三层映射）：

| 博文内容层 | 映射篇目 |
|-----------|---------|
| 发布事实层 | `concepts/00-deepseek-vision-exp.md`（模型详解） |
| 选型矩阵层 | `concepts/01-selection-landscape.md`（选型全景）+ `concepts/02-scenario-matrix.md`（场景矩阵） |
| 架构模式层 | `concepts/03-vision-reasoning-pipeline.md`（视觉-推理协作架构） |
| 示例与决策工具 | `examples/`：成本演练 + 输出结构设计 + 选型决策树 |

**步骤6 对照**：**14 个文件**（4 概念 + 3 示例 + 2 信源 + 3 子目录索引 + 根 index + log）；所有价格/模型名带 F 编号；`pipeline-output-structure.md` 伪代码双重标注"非官方 API 文档"；`stale_after: 2026-12-31`，已知边界声明 Exp 实验性质与 2026-08 价格时点；`sources` 双信源（博文 URL + DeepSeek 官方新闻）。

**步骤7 对照**（四视角审查发现的 **4 项修复**）：

1. `ai/deepseek/index.md` 接入：导航表"应用模型与资源"新增条目、toctree 追加、束数 12→13
2. `bundles/index.md` 计数同步：DeepSeek 分组 12→13、ai 域 95→96、全库 268→269（含正文计数）
3. 溯源补全：`concepts/01`、`concepts/02`、`examples/cost-scenario-walkthrough` 引用核验事实的子文档 frontmatter `sources` 补充官方核验信源
4. 根 `index.md` 的 `verified` 升级为列表，追加本次审查事件

修复后 `invoke gates.toctrees` 复核通过（无孤立文档、无断链）。完整审查记录见 [log.md](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/deepseek/vision-model-selection/log.md)。

### 逐步对照（案例2：商业分析类，L2 验证）

**案例**：微信公众号"窥见比特"博文《字节把TRAE、扣子都并进豆包，图什么？》（作者"比特一哥"，2026-08-27）→ `ai/trae/bytedance-ai-consolidation/` bundle（2026-08-28 完成）。

- 完整方案：[spec.md](../../../../.trae/specs/okf-wiki-ecosystem/bytedance-ai-consolidation-blog-okf-wiki/spec.md)
- 事实集：[facts.md](../../../../.trae/specs/okf-wiki-ecosystem/bytedance-ai-consolidation-blog-okf-wiki/facts.md)
- 产出物：[bytedance-ai-consolidation/index.md](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/trae/bytedance-ai-consolidation/index.md)

**步骤1 对照**：公开博文 → 标准工作流。

**步骤2 对照（性质分流，本案例驱动模式升级）**：博文为组织架构变动+资本开支+竞争格局分析，作者标注"个人观点，仅供参考"，无可运行示例 → 判定为**商业分析/战略资讯类** → 骨架**无 examples/**，index 顶部声明"非源码教程"。

**步骤3 对照**：通过 AskUserQuestion 确认归属 `ai/trae/`（主线实体 TRAE/扣子/豆包均属字节 AI 产品矩阵，TRAE 分组为最贴近锚点）；不新建分组。

**步骤4 对照（核验捕获源文错误，本模式核心价值例证）**：21 条事实（F-001~F-017 博文 + F-018~F-021 核验补充）；8 项 P0 声明核验，7 项通过、1 项发现源文错误——博文将 2025 年实际 AI 芯片采购额 850 亿误作 2026 年预算（2026 年预计约 1000 亿）；同时识别彭博 700 亿美元为"讨论中上限"与 SCMP 确认的 2000 亿元（300 亿美元）为不同口径。F-004（赛马机制）/F-016（门票论）标注作者观点；F-009 利润暴跌补充字节官方李亮回应。

**步骤5 对照**：商业分析三层映射——整合时间线 → `00-consolidation-timeline.md`（含 Mermaid 组织架构图）；成本驱动逻辑 → `01-cost-driven-rationale.md`；竞争格局 → `02-competitive-landscape.md`。

**步骤6 对照**：**9 个文件**（3 概念 + 2 信源 + 2 子目录索引 + 根 index + log，无 examples）；双信源（博文 + 36氪独家）；`stale_after: 2026-12-31`；4 条已知边界（个人观点/资本开支口径混杂/资讯时效/单源声明）。

**步骤7 对照**：
1. 四视角审查修复 1 项（article-source.md 客观事实计数 14→13）
2. `ai/trae/index.md` 新增"📰 战略资讯"分类（该分组原 12 个 bundle 均为源码教程），束数 12→13，导语补充两类方法论链路说明
3. `bundles/index.md` 计数同步：TRAE 组 12→13、ai 域 96→97、全库 269→270
4. **门禁环境问题**：`invoke gates.*` 报 `ModuleNotFoundError: invocations`（该依赖在 `pyproject.toml` 的 optional-dependencies.doc 中，未默认安装），改用清单化手动等效验证（toctree/链接/UTF-8）并在 log.md 注明——此发现反哺本模式步骤7的环境前置说明

## 反模式

| 反模式 | 后果 | 正确做法 |
|--------|------|---------|
| 无信源转述（把博文观点当事实写） | 作者个人判断被固化成"官方结论"误导读者 | 所有声明登记 F 编号，观点标注"作者观点" |
| 忽视时效性（不设 stale_after、不声明价格时点） | 过期价格/版本信息误导采购与技术决策 | 设 stale_after + 已知边界声明价格时点与实验版本 |
| 单篇博文新建分组 | 分组碎片化，目录体系膨胀 | 落入既有分组，靠 bundle 承载单篇内容 |
| 核验不过硬编官方 URL | 假核验，可信度虚假升级 | 仅在 WebSearch 确认官方来源后补充信源，否则标注单源 |
| 伪代码不标注非官方 | 读者误当官方 API 文档使用 | 文内显著标注"非官方" |
| 接入后不跑 gates 或无 gates 就声称通过 | 孤立文档/断链静默存在；环境问题被掩盖 | 依赖可用时跑 `invoke gates.*`；不可用时执行手动等效验证清单并在 log 注明，禁止声称"gates 通过" |
| 私域内容进公共 specs 区 | 访问控制内容泄露到公共区域 | 含 code/token 的私域链接走 playground 工作流 |
| 商业分析类硬塞 examples/ 或源码教程板块 | 空 examples/ 制造伪结构，板块语义错配 | 按步骤2性质分流，商业分析类无 examples 并在分组 index 新增匹配分类 |
| 核验发现源文错误却静默照搬 | 把源文错误固化为知识库错误，可信度低于源文 | 新增 F 编号记录正确值，verification.md 单列勘误，正文呈现正确值并标注源文口径 |
| 微信文章直接 WebFetch | 微信反爬返回空/拦截页面 | 直接用 browser_use 子代理提取全文 |
| 厂商自宣成效数字不标"自述"即入库（L3 新增） | 提效倍数/节省工时被读者当作独立事实引用，营销数据污染知识库 | 信源距离预判标"厂商自宣"，成效数字一律 P0 核验溯源；无独立出处时正文标注"厂商/客户自述"，index 顶部加提示块 |
| 技术主题想当然设 examples/（L3 新增） | 技术综述/资讯盘点类文章硬凑 examples，空目录或伪示例制造结构噪声 | 以"操作可复现性两问"为判据：无可照做且实测可复现的流程就不设 examples/（正例：a2a-mcp 综述、threeui 盘点均无 examples） |
| 核心声明核验失败仍发 stable 状态 bundle（L3 新增） | 文章主结论被证伪但 bundle 状态无警示，下游无法识别可信度 | 核心声明 ❌ → frontmatter `status: flagged` + verification 顶部明示 + stale_after 前安排复核（正例：tushare-ai-office） |

## 迁移验证

**L1→L2（2026-08-28，2 案例）**：

- ✅ 案例1 vision-model-selection（2026-08-28，技术选型类，36 事实/3 项官方核验/14 文件）
- ✅ 案例2 bytedance-ai-consolidation（2026-08-28，商业分析类，21 事实/8 项核验捕获1处年份错配/9 文件）—— 驱动 L1→L2：新增性质分流、P0 核验分级、gates 环境前置、勘误处理

**L2→L3（2026-08-29，批量 12 案例验证，84 项 P0 核验：59✅/21⚠️/4❌，460 事实/123 文件）**：

- ✅ 案例3 qwen-creative-platform-news（产品发布新闻，39 事实/5✅3⚠️，Wan 版本号过时勘误）
- ✅ 案例4 qwen-ui-agent（开源工具实测，44 事实/5✅2⚠️1❌ 硬件要求旧版信息，含 examples）
- ✅ 案例5 threeui（开源组件资讯盘点，42 事实/4✅3⚠️0❌，**技术内容但无 examples 正例**）
- ✅ 案例6 a2a-mcp-convergence（技术综述，53 事实/6✅5⚠️1❌ AWS GA 日期硬错，**技术内容但无 examples 正例**；引文意译/报告身份勘误）
- ✅ 案例7 doubao-work（一手实测评测，43 事实/**8✅0⚠️0❌ 零勘误**）
- ✅ 案例8 tushare-ai-office（厂商自宣，32 事实/3✅2⚠️1❌ 核心声明无证据，**首个 flagged bundle**）
- ✅ 案例9 doubao-work-context-layer（产品分析，39 事实/4✅1⚠️1❌ 效率数据归因失实）
- ✅ 案例10 doubao-work-org-productivity（行业分析，40 事实/5✅1⚠️0❌，豆包主题簇）
- ✅ 案例11 claude-vision-skill（开源技术教程，35 事实/**6✅0⚠️0❌**，含 examples，12 文件）
- ✅ 案例12 siemens-industrial-agent（企业推广/行业分析，36 事实/3✅3⚠️0❌，平台数字拔高+报告赞助身份未披露）

L3 升级增量：①骨架判据改"操作可复现性两问"（案例5/6 驱动）；②信源距离预判+勘误四张清单（4❌21⚠️ 归因萃取）；③flagged 状态管理（案例8 实践固化）；④同主题 bundle 互链（豆包主题簇）；⑤双份事实编号一致性核对（460 vs 458 漂移驱动）；⑥反模式 10→13。

**L3 定稿后新增验证（2026-08-29）**：

- ✅ 案例13 agora-gemini-transcribe（资讯速报骨架，厂商自宣新闻稿，32 事实/6 项 P0：5✅1⚠️0❌/10 文件，stale_after 2026-11-30）——**"资讯速报"骨架首个独立案例**，补齐骨架覆盖；唯一 ⚠️ 为"全球首个 Realtime API"措辞归属（API 为 OpenAI 产品，Agora 为 2024-10 首发语音合作方、2025-09-04 GA）。

**骨架覆盖说明**：技术教程/选型骨架（含 examples）经 3 案例验证（案例1/4/11）；商业分析/技术综述骨架（无 examples）经 9 案例验证；"资讯速报"骨架（单事件、stale_after 1-2 月）经案例13 验证（agora-gemini-transcribe，2026-08-29）。四类骨架全部有案例覆盖。

**复盘报告**：[12篇批量转化里程碑复盘](../../reports/concepts/milestone/blog-to-okf-bundle-12posts-milestone-retrospective-20260829.md)（含 30 条事实、4 条洞察、勘误四模式萃取全过程）；[首批 2 篇复盘](../../reports/concepts/milestone/blog-to-okf-bundle-milestone-retrospective-20260828.md)。

- 🔄 可迁移到：其他博文类 URL——产品发布资讯、价格政策解读、技术选型文章、组织/融资/财报类商业分析、行业事件速报；勘误四模式（日期版本/成效溯源/口径对照/引文逐字）可迁移至一切"二手内容→可信知识库"转化任务（网页学习笔记、竞品分析、行业报告解读）。
