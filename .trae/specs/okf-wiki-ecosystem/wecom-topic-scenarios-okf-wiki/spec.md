# 企业微信「话题」场景最佳实践示例页 → OKF Wiki 知识包 - 需求文档

## Overview

- **Summary**：按七概念知识沉淀链路（R→I→E→V）+ `seven-concepts-cmd` 方法论编排，把企业微信官方公开页《了解话题最佳示例》转化为一个 OKF v0.2 知识包（bundle），落位于 `projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/tencent/` 既有分组，与同分组 `wecom-5-0-10-release`、`wecom-5-0-12-release` 企业微信束并列并双向互链。
- **Purpose**：该页是一个**产品功能场景示例页**（非版本发布页、非操作手册），以 5 个平行场景（推进项目协作 / 收集产品意见 / 分享经验知识 / 发布公告通知 / 更多功能及反馈）展示企业微信「话题」功能的使用价值与「群聊 vs 话题」对照论证。需要一份可溯源、带口径分层与时效管理的场景知识快照，让读者能按自身角色快速定位「我该用哪个场景、厂商给了什么依据、哪些是厂商自证而非独立评测」。
- **Target Users**：OKF 知识库读者——关注企业协作工具/办公生态的技术与产品人员、需要评估「话题」是否契合自身团队协作模式的管理者；以及知识库机器审核（Sphinx toctree BFS + 机械门禁）。

## Goals

- 完整登记源页全部可读声明（F-001～F-NN）：5 个场景的「适用对象 + 优势条目 + 群聊/话题对照」、页面结构（标题/平台标识/导航/底部反馈入口）、以及每条内嵌外部链接的存在性。
- 按「事实—场景机制—能力边界」三层产出 5 篇 concepts：1 篇总览（源页定位 + 场景全景 + 职责边界）+ 4 篇场景/能力篇，使读者可按角色跳转。
- 对来源属性、时效、未给项做**显式分层**：①来源为厂商自有发布页单源、无第三方核验；②页面无发布日期/版本号/作者/更新时间，时效只能以抓取日（2026-10-16）为快照基准；③「话题」与同分组 5.0.12 束登记的「频道场景示例页」在命名与场景集上高度重合，二者关系（同源/异源、话题是否为频道内的话题帖单元）**官方未给**，一律并置登记不得择一断言；④页面未给出开通条件、套餐要求、客户端版本门槛、入口路径，属「官方未给项」，必须显式声明而非留给读者臆断。
- 接入 tencent 分组到 `doc/bundles/index.md` 的完整三级索引链与计数。
- 不设 `examples/`：源页无经实测的安装/配置链路，操作可复现性两问皆否。

## Non-Goals

- 不修改/提交 `wecom-5-0-10-release`、`wecom-5-0-12-release` 两束的正文事实；仅允许在**本束**建立互链，并在 5.0.12 束「主题关联/已知边界」处**最多新增 1 行**回链（不重写其内容、不改其计数归属）。
- 不采集、不转述源页内「（点击查看API接口文档）」所指向的目标页面内容（该目标未在本任务取得）；只登记该链接的**存在性与锚文本**。
- 不修复与本任务无关的并行在途工作（其他未跟踪束、其他分组的索引改动）；仅在本束 `log.md` 披露观测结果。
- 不做 git commit / push（用户未要求；提交待用户显式指令，按 `atomic-commit-cmd` 执行）。
- 不新建分组、不新建顶级类目。
- **不把取证过程中意外接触到的页面会话元数据（登录态、企业/账号标识、会话令牌、内部文档 ID 等）写入任何产出物**——包括 spec、facts.md、bundle 与 log。

## Background & Context

- **源**：`https://page.weixin.qq.com/smartpage/p/b1_AJ8AUgbdAFwUCVMuy2qS5mGPhvZ?p=HXPk2x`，页面大标题《了解话题最佳示例》，平台标识为「使用 智能文档 发布」（企业微信智能文档发布形态）。正文经 JS 渲染并**分页**，`?p=` 为页标识：`HXPk2x`=推进项目协作、`htt4Bf`=收集产品意见、`ptlD2c`=分享经验知识、`tR2p63`=发布公告通知、`BMbevB`=更多功能及反馈。
- **取证过程（可审计）**：WebFetch 失败；直接 HTTP 取回 200 但 `basicClientVars` 显示 `isLogin:false`/`userType:guest`/`padType:blankpage`，静态 HTML 仅含 UI 文案（"企业微信文档/智能文档"），无正文；未登录访客访问命中登录墙（企业身份/个人身份/扫码）。最终经浏览器渲染态逐页取 `document.body.innerText`，5 页全文均已取得（合计约 3.1K 字符），逐字内容见实施阶段 facts.md。
- **可达性事实（须入束）**：该页对未登录访客**不可直读**；需企业微信登录态方可在浏览器中渲染出正文。此为该信源的客观可达性属性，须在 references/verification.md 与根 index「已知边界」中声明。
- **内容敏感度裁决（2026-10-16，用户确认）**：源页命中「需登录态才能访问」的私域信号；经向用户确认，用户明确选择**仍落 `doc/bundles` 公开知识库**（标准 Spec Mode）。本 spec 依该裁决执行，并以上述「可达性事实入束」作为对冲——公开产出物中如实标注信源需登录，不制造"任何人均可直读"的假象。
- **格式基准**：同分组 `wecom-5-0-12-release` 束（10 文件、4 概念、51 条事实、R1 pass）为本任务直接基准：OKF v0.2 frontmatter、无 examples、references 双件（article-source.md + verification.md）、根 index「内容性质/可信度状态/已知边界/主题关联/一句话结论」结构。
- **子模块状态**：`projects/awesome-okf-xs` 为 git submodule（只读引用区，但同分组已有落盘先例，按子模块工作流落盘文档、不提交）。计数必须以机械真值（目录树 + 门禁脚本）为准。
- **同分组计数基线（2026-10-16 读盘）**：tencent 分组 17 束 / 135 概念 / 48 示例 / 76 信源登记 / 2832 条编号事实。实际数字以实施时复算为准。

## Functional Requirements

- **FR-1**：新建 bundle `wecom-topic-scenarios/`，含根 index.md、log.md、concepts/（index + 5 篇）、references/（index + article-source.md + verification.md），共 11 个文件；**无 examples/**。
  - 计数更正（2026-10-16 实施期）：原稿写「13 个文件」系枚举清单求和笔误（1+1+1+5+1+1+1=11），与同分组基准 `wecom-5-0-12-release`（1+1+1+4+1+1+1=10）同口径，故按枚举清单修正为 11，文件清单本身未变。
- **FR-2**：`article-source.md` 与 spec 目录 `facts.md` 双份登记同一 F 编号集合（`F-001…F-NN`，连续无跳号、集合相等）；每条含声明摘要、来源代号（如 W/A1…）、核验状态。
- **FR-3**：concepts 五篇职责分离——①总览：源页定位、5 场景全景、信源属性与时效、未给项；②任务协作与意见收集；③知识分享与公告通知；④公告发布的进阶能力（已读状态/编辑更正等）；⑤通用能力与反馈入口。每篇所有具体声明（场景名、适用对象、优势条目、对照论证）均带 F 编号引用；厂商自述/单源/未给项/官方未披露四类措辞显式标注；含至少 1 张 Mermaid 场景全景图（节点带 F 依据）。
- **FR-4**：`verification.md` 给出：信源清单与可达性记录、核验总表（页面结构/5 场景/对照论证/链接存在性）、勘误与存疑清单、口径分层表（源单源属性、话题 vs 频道命名张力、适用对象描述性 vs 规范性、未给项）、V 四视角对抗审查表、状态裁决（预期 `stable`，单源与未给项充分标注）。
- **FR-5**：三级索引接入——`tencent/index.md`（导航表行 + 相关链接 + 计数 + toctree）、`ecosystems/index.md`（腾讯行）、`jishu/ai/index.md`、`jishu/index.md`、`doc/bundles/index.md`；计数以门禁脚本机械复算为准（本任务预期：束 17→18、概念 135→141、示例 48 不变、信源 76→78、事实 2832→2832+NN）。
- **FR-6**：双向互链——本束根 index「主题关联」链 5.0.10 与 5.0.12 束；5.0.12 束 index.md 回补最多 1 行指向本束（就其登记的「场景示例页」smartpage 与本束源页的关系作显式口径声明）。
- **FR-7**：`log.md` 记录七概念执行链路、口径决策、并行在途观测、门禁运行方式与实际输出（脚本不可用时不谎报，如实声明）。

## Non-Functional Requirements

- **NFR-1（规范一致）**：全部文件遵循 OKF v0.2 frontmatter（根文件含 `okf_version: "0.2"`、`type`、`title`、`description`、`tags`、`generated`、`verified`、`status`、`stale_after`、`sources`；子文档 `type`=Concept/Reference，`generated`/`verified` 标识为 `process:seven-concepts-*`，`status`/`stale_after`/`sources` 齐备）；中文正文；文件名 ASCII kebab-case。
- **NFR-2（机械质量）**：UTF-8 严格 roundtrip；全部 Markdown 相对链接可达；零 `file:///`、零家目录绝对路径；每个 index.md 含 toctree 块且条目逐一存在；不引用 `.temp/` 等临时路径。
- **NFR-3（时效管理）**：源页无版本号/发布日期，`stale_after` 对齐同分组版本资讯束基线 **2027-01-31**，到期复核页面是否仍存续及其内容漂移；单源/未给项在「已知边界」集中声明。
- **NFR-4（可审计与零编造）**：核验信源均为实际访问成功的 URL；无法核验项标「仅官方单源 / 未取得 / 官方未给」，不得升级可信度、不得编造页面未出现的事实；派生产物 frontmatter 携带 `source` 字段标注来源。
- **NFR-5（隐私红线）**：产出物中不得出现任何页面会话/账号元数据（登录态、企业名、用户标识、内部文档 ID 等）；R 阶段的临时取证文件与脚本一律置于 `.temp/` 并在收尾清理。

## Constraints

- **Technical**：Windows + PowerShell 7 + Python py314；产出在 git submodule `projects/awesome-okf-xs/`（不提交）；门禁脚本在子模块根目录以 `python scripts/<name>.py` 直接运行。
- **Business**：遵循 AGENTS.md 启动协议与文档边界（内容敏感度经用户裁决为公开工作流，spec 落 `okf-wiki-ecosystem/`）；沟通中文、动作导向。
- **Dependencies**：源页可访问性（须浏览器渲染态逐页取得，已验证）；同分组索引与门禁脚本现状；实施时源页内容可能与抓取时点（2026-10-16）漂移，以事实采集时点为准。

## Assumptions

- 归属 `jishu/ai/ecosystems/tencent/` 无争议：主线实体为企业微信（腾讯），同分组已有 2 个企业微信束先例，不单新建分组。
- 骨架按「产品场景示例页：index + concepts + references + log，无 examples」——与 5.0.12 束同型，仅 concepts 篇数按场景数调整。
- 「话题」为源页自述的功能名；其与 5.0.12 束登记的「频道场景示例页」的关系官方未给，按并置登记处理，不做单方断言。

## Acceptance Criteria

### AC-1: Bundle 结构与规范完整
- **Type**: `rule`
- **Given**: bundle 目录 `jishu/ai/ecosystems/tencent/wecom-topic-scenarios/`
- **When**: 实施完成
- **Then**: 11 个文件全部存在（index.md、log.md、concepts/index.md + 5 篇、references/index.md + article-source.md + verification.md），无 `examples/` 目录；每个 index.md 含 toctree 块且条目逐一可解析存在；根 index.md frontmatter 含 `okf_version: "0.2"`、`status`、`stale_after`、`sources`，`sources` 覆盖实际引用的全部来源代号
- **Pass Condition**: 文件清单、toctree 条目、frontmatter 必填字段逐项机械核对全部通过
- **Evidence**: 目录列表 + toctree/frontmatter 机械核对结果

### AC-2: 双份 F 编号一致且核验真实
- **Type**: `rule`
- **Given**: spec 目录 `facts.md` 与 bundle `references/article-source.md`
- **When**: V 阶段用正则提取两文件的 `F-\d{3}` 编号集合
- **Then**: 两集合相等、连续无跳号（`F-001…F-NN`，NN 与两文件表行数一致）；每条外部 URL 来自 R 阶段实际访问记录；四条口径分层（源单源属性、话题 vs 频道命名张力、适用对象描述性 vs 规范性、官方未给项）在 `verification.md` 与 concepts 正文中均有呈现
- **Pass Condition**: 集合比对零差异；四条口径项 4/4 在正文落地
- **Evidence**: 正则集合比对输出 + verification.md 口径分层节

### AC-3: 三级索引与计数机械同步
- **Type**: `rule`
- **Given**: `tencent/index.md`、`ecosystems/index.md`、`jishu/ai/index.md`、`jishu/index.md`、`doc/bundles/index.md`
- **When**: 在无并行写入窗口运行时
- **Then**: bundle 索引门禁脚本退出码 0（五面计数一致）；本束在 tencent 分组导航表、相关链接与 toctree 三处到位；本束相关 toctree 断链过滤复检零命中
- **Pass Condition**: 门禁脚本退出码 0 且输出含本束的五面计数一致；toctree 检查过滤 `wecom-topic-scenarios` 零命中
- **Evidence**: 脚本原始输出

### AC-4: 链接 / 编码 / 溯源机械门禁
- **Type**: `rule`
- **Given**: 全部新增/修改的 .md 文件
- **When**: V 阶段执行
- **Then**: UTF-8 检查通过；全部 Markdown 相对链接可达；零 `file:///`、零 `C:\Users` 等家目录路径、零 `.temp/` 引用；派生产物 frontmatter 含 `source` 溯源字段；双向互链成立（本束→5.0.10/5.0.12 各 ≥1 条，5.0.12 index→本束 ≥1 条）
- **Pass Condition**: 各项检查零命中违规
- **Evidence**: 门禁脚本输出 + Grep/Test-Path 核对记录

### AC-5: 内容可信度与读者可用性
- **Type**: `rubric`
- **Dimension**: 口径分层与读者决策可用性
- **Scale**: 1-5
- **Anchors**: 1 = 厂商自述、未给项与可核实事实混写，读者无法判断可信度；3 = 主要声明有出处但口径分层不统一、个别场景条目无 F 编号；5 = 每条场景名/适用对象/优势条目可回溯 F 编号，「厂商自述单源 / 官方未给 / 命名张力 / 信源需登录」四类标签全文一致，「已知边界」可直接支持读者「用不用、怎么用、还缺什么」的决策
- **Pass Threshold**: >= 4
- **Evidence**: 五篇 concepts + 根 index「已知边界」；独立评审逐篇抽查

### AC-6: 知识结构与来源忠实度
- **Type**: `rubric`
- **Dimension**: 三层结构（源页定位→场景机制→能力边界）与来源忠实度
- **Scale**: 1-5
- **Anchors**: 1 = 按源页顺序平铺翻译、无分层与互链、夹带页面外推断；3 = 有分层但层间重复、跨篇跳转不清、个别断言超出源页可支撑范围；5 = 总览答「这是什么页 / 5 场景怎么分 / 信源与时效」，场景篇答「谁适用 / 优势是什么 / 厂商对照论证是什么」，边界篇答「官方没说什么 / 读者还需自行确认什么」，篇间阅读路径明确、Mermaid 节点有 F 依据、无一条断言超出源页可支撑范围
- **Pass Threshold**: >= 4
- **Evidence**: 5 篇 concepts 结构与独立评审评分 + 超范围断言扫描

### AC-7: 隐私红线与零编造
- **Type**: `rule`
- **Given**: 全部产出物（spec 目录 + bundle）
- **When**: V 阶段执行关键词扫描
- **Then**: 零会话/账号元数据泄漏（无登录态令牌、企业名、用户标识、内部文档 ID、`xsrf`/`tinyid`/`corp_id` 等）；无页面未出现的事实断言；`.temp/` 取证产物已清理且无产出物引用之
- **Pass Condition**: 关键词扫描零命中；抽查 5 条声明全部可在源页逐字命中
- **Evidence**: 扫描命令输出 + 逐字比对记录

## Open Questions

- 无阻断性开放问题。以下为实施时按既有裁决执行、无需再次确认的事项：①不提交 git；②计数以机械真值为准、并行漂移只披露不修复；③`stale_after=2027-01-31`；④`status` 目标 `stable`（若 V 阶段发现核心声明证伪则转 `flagged`）；⑤内容按用户裁决落公开知识库，同时以「信源需登录」可达性声明对冲。
