---
type: plan
title: "AI 图像服务与内容变现 OKF Wiki 实施队列"
source: "spec.md"
status: draft
methodology: seven-concepts-cmd
content-sensitivity: public
---

# AI 图像服务与内容变现：实施计划

## 批准边界

用户已通过完整 spec.md 与 tasks.md 的 NotifyUser 预览批准实施；公开原创教程与补采多媒体仍遵守已确认的采集边界。
当前进入实施，批准不包含安装依赖、Git 提交或推送。
`review.md` 仅在实施队列清空后创建。Git 提交、推送不在范围内。

## 拟定文件地图

- Spec：`spec.md`、`tasks.md`、实施中的 `facts.md`，Review 阶段的 `review.md`。
- Bundle：根 `index.md`、`log.md`。
- `concepts/`：索引、阅读与证据边界、定制服务、素材产品、内容获客、线下周边、成本与交付、授权与合规、学习节奏、洞察与验证模式。
- `references/`：索引、来源清单、文章事实、多媒体覆盖、关键主张核验、知识地图。
- 暂不建 `examples/`；最终篇目按采集内容收敛，但不得静默删减已批准主题。

## Task 1: 补采公开图片与视频并建立来源清单
- **Status**：`completed`
- **Completion Evidence**：
  - 2026-11-01 snapshot 与 DOM 回验正文至结尾、账号署名日期；source-manifest.md 记录全部六组正文章节。
  - media-coverage.md 逐项登记 I1～I13 与 V1～V5；8 个有效图片、5 个空占位、5 个可加载但部分核读视频。私人聊天排除，签名媒体 URL 未落盘；ASR 未安装且未获安装授权，音轨未转录。
  - TR-1.1、TR-1.2 自验通过：覆盖状态、位置、日期和证据通道齐备，无未读视频实质结论或全文镜像。
- **Priority**：high
- **Depends On**：None
- **Description**：
  - 先建立 `references/source-manifest.md`，回验账号、署名、日期与正文章节。
  - 逐项盘点图片和 5 段既知视频，核读可公开访问部分；视频内容有音轨时按适用转录技能处理。
  - 不绕过登录、验证码、付费或邀请限制；不将原始全文或隐私截图写入公共目录。
  - 为受限项记录停止原因、覆盖范围与后续合法补采条件。
- **Acceptance Criteria Addressed**：AC-1
- **Test Requirements**：
  - `rule` TR-1.1：章节和媒体清单每项均有位置、状态、采集时间及证据来源；5 段既知视频逐项对账，发现增减须说明。
  - `rule` TR-1.2：未核读内容不出现在实质摘要中；公共产物无完整原文镜像或个人信息。

## Task 2: 登记事实并核验收益、平台与授权声明
- **Status**：`completed`
- **Completion Evidence**：
  - facts.md 与 article-source.md 全行机械比较相等，F-001～F-048 连续；verification.md 有 48 项逐条裁决。TR-2.1 通过。
  - Midjourney 条款、标识办法、米画师权利说明已回读；昵图与 huashilm 页面已读取。涂鸦旧页改版、VJS 身份、AI 投稿准入、收益及引语缺口均单源或 flagged；TR-2.2 通过。
  - 乘法自验 600～3000，明确 30 天假设、订单量未证实、毛收入未扣成本；TR-2.3 通过，不认证截图为净收益。
- **Priority**：high
- **Depends On**：Task 1
- **Description**：
  - 建立连续 F 编号及页面事实、作者主张分类；双份登记与核验表关联。
  - 核验收益算术、报价口径、素材与接单平台身份及 AI 准入政策。
  - 回验 Midjourney 条款、AI 标识法规版本和引语归属；不可得项明确降级。
  - 查证日期版本、成效数字、统计口径、引文归属四张清单。
- **Acceptance Criteria Addressed**：AC-2
- **Test Requirements**：
  - `rule` TR-2.1：F 编号 >= 20 条且连续，Spec 与 bundle 编号集合机械比对完全一致。
  - `rule` TR-2.2：关键主张均有实际读取的权威证据或明确单源/flagged 状态；法规主体义务不混写。
  - `rule` TR-2.3：收益算术有输入假设、600–3000 毛收入结果及成本未扣说明；不将截图价格或付款数当净收益。

## Task 3: 形成知识地图并生成原创原子化教程
- **Status**：`completed`
- **Completion Evidence**：
  - 18 篇 Markdown 实际统计一致：9 教程、5 参考正文、3 索引、1 日志。九篇覆盖全部批准主题，knowledge-map.md 逐篇映射 F；未核平台、视频与收益均就地降级。TR-3.1 通过。
  - 严格 UTF-8 解码、无 BOM、必需字段与 root-only okf_version 自验通过；全部 sources 使用 resource。TR-3.2 通过。
  - TR-3.3 自评 5/5：四路径各有用途判断，成本有三账，合规有六层，学习有停止边界；三洞察四元组完整，模式含五步、五反模式、五检验及非图像迁移假设。明确无实测，不复制正文或承诺收益。最终分数由独立 Review 复核。
- **Priority**：high
- **Depends On**：Task 2
- **Description**：
  - 分事实、机制假设、迁移实践三层组织内容，记录操作可复现性两问结论。
  - 先完成信源与核验参考，再生成概念教程，最后补根索引与学习路径。
  - 覆盖四条商业路径及成本交付、授权合规、学习节奏；至少 3 条有证据的四元组洞察。
  - 写 1 个 L1 单案例待验证模式，跨场景迁移仅作为假设，不冒充真实试验。
  - 以决策表和检查单承载实践建议，不伪造工具实测。
- **Acceptance Criteria Addressed**：AC-2、AC-3、AC-4
- **Test Requirements**：
  - `rule` TR-3.1：所有已批准主题均有正文覆盖和 F 编号映射；核验失败项在相关正文就地说明。
  - `rule` TR-3.2：frontmatter 使用 `sources[].resource`，非保留文档必需字段齐备，只有根 index 声明 okf_version。
  - `rubric` TR-3.3：原创性与行动质量；scale 1-5；1 = 摘抄/承诺收益，3 = 主题齐但边界或行动缺口，5 = 原创可执行、洞察和模式要素完整；threshold >= 4；证据为正文、知识地图和自验说明。

## Task 4: 接入导航并验证结构与构建
- **Status**：`completed`
- **Completion Evidence**：
  - 本包相关门禁复跑通过（py314 环境，不安装依赖）：`invoke gates.utf8` 通过（12670 文件均为有效 UTF-8）；`invoke gates.toctrees` 通过（全部 index.md 引用有效、所有内容文档可达）；`invoke gates.bundles` 通过（9 域 / 64 组 / 698 束，frontmatter、计数行、节标题、分组表、toctree 五面一致）。TR-4.1 结构项通过。
  - 链接检查以显式 18 个文件输入：18 个 Markdown / 63 内联 / 7 外部 / 56 本地引用全部存在，frontmatter 路径检查通过；7 个外链未启用 `--check-external`，不作可达性声明。
  - 文档构建：`sphinx-build -b html doc _build/html` 报告 `build succeeded, 282 warnings.`，本包目录实际产出 18 个 HTML；进程退出码为 1，日志末尾为 TRAE Sandbox 拦截 jieba `__pycache__` 写入，非文档缺陷。日志中未见任何本包 WARNING/ERROR；282 warnings 与 `Document or section may not begin with a transition` 分布于其他既有包，与本包无关。TR-4.1 构建项以「Sphinx 构建成功 + 沙箱导致的非零退出码」如实记录，不写作构建失败也不写作零告警。
  - TR-4.2：`git diff --check` 无输出；路径级 diff 仅本包新增与五个必需索引增量，保留既有 douyin-compute-ai-ecommerce 条目与其未跟踪包，未删除、未回滚他方内容。
  - TR-4.3：扫描所得工作树计数 698／87／38 与 HEAD 已提交口径 696／85／36 清楚分离；本轮只增一束，未把在途新文件规模写成已提交事实。
  - 范围外阻塞（用户已批准按范围外处理）：全套 `invoke gates.all` 在资产基线检查退出 1——HEAD 字节 98040859，工作区归一后 98160209，残差 +119350 超出容差；根因是工作区含本轮新包与开工前已有的并发在途变更，规则要求提交或 stash 后复跑，但本轮无该授权且不得处置其他会话内容。用户裁定保留该失败为已披露范围外问题、按本包相关验收项继续；未修改检查器、未伪造通过、未提交或暂存他方内容。
- **Priority**：high
- **Depends On**：Task 3
- **Description**：
  - 重读共享索引和当前 git 状态，局部追加新包导航与对应工作树计数。
  - 新包链接已有 AI 副业及相关变现知识包，不改相邻包正文。
  - 执行子项目编码、toctree、计数门及链接验证、文档构建。
  - 资产规模基线按 HEAD 已提交口径处理；不把在途新文件规模写成已提交事实。
  - 环境失败记录真实原因，不改工具或全局配置伪造通过。
- **Acceptance Criteria Addressed**：AC-4
- **Test Requirements**：
  - `rule` TR-4.1：UTF-8、相对链接、toctree、五面计数检查均通过，文档构建成功，有命令和输出证据。
  - `rule` TR-4.2：路径级 diff 显示仅本包和必需索引增量，无其他会话内容删除或回滚。
  - `rule` TR-4.3：扫描所得工作树计数与 HEAD 资产基线清楚分离，不使用历史 697 束快照硬编码新值。

## Task 5: 整理实施完成证据以供独立审查
- **Status**：`completed`
- **Completion Evidence**：
  - `log.md` 已按 2026-11-01 记录真实 R／I／E 阶段、采集缺口（图片空占位、视频仅局部核读、ASR 未运行、两次目标截图仅得首屏）、核验局限（涂鸦旧页改版、VJS 身份、平台 AI 准入未确认、引语未读原始出处）与门禁／构建结果；未把历史摘要重构为当时未输出的 CMD-LOG。
  - 机械对账：Spec `facts.md` 与 bundle `references/article-source.md` 各 48 个唯一 F 编号（末号 F-048，连续）；`references/verification.md` 48 项裁决，三者数量一致。篇目计数：bundle 共 18 篇 Markdown = 9 教程 + 5 参考正文 + 3 索引 + 1 日志（`concepts/` 10 文件含索引、`references/` 6 文件含索引）。TR-5.1 通过。
  - AC/TR 对账：AC-1↔Task 1（TR-1.1/1.2）、AC-2↔Task 2 与 Task 3（TR-2.1/2.2/2.3）、AC-3↔Task 3（TR-3.1/3.2/3.3）、AC-4↔Task 4（TR-4.1/4.2/4.3）、AC-5↔Task 5 与后续 Review；五条 AC 均有承接任务与真实 Completion Evidence。
  - TR-5.2：`git log -1` 仍为开工前提交 `6e115703`，无本轮新提交；`review.md` 不存在（Test-Path 为 False），未提前创建；未安装依赖、未 stash 他方内容。
- **Priority**：medium
- **Depends On**：Task 4
- **Description**：
  - 在 `log.md` 记录实际七概念阶段、采集缺口、核验局限和门禁结果。
  - 对账全部 AC/TR、事实范围与篇目计数，消除跨文件口径漂移。
  - 形成独立 Review 输入，任务队列清空后才进入 Review。
- **Acceptance Criteria Addressed**：AC-1、AC-2、AC-3、AC-4、AC-5
- **Test Requirements**：
  - `rule` TR-5.1：日志中的采集、事实、文件和门禁数量与机械统计一致；每个 completed 任务都有真实 Completion Evidence。
  - `rule` TR-5.2：没有未经授权 commit 或 push，没有提前创建 review.md。

## 后续 Review 流程

上述实施任务自验完成后，创建 `review.md`，向恰好一个全新上下文委托只读审查，覆盖全部 AC/TR 及魔鬼代言人、新人、业务、未来四视角。
发现可行动问题时，先写 Review History，再新增结构化 pending issue，修复并回验后开启新一轮独立 Review。
没有为了满足数量要求而虚构意见或修正；只有最新 Review 为 pass、无受阻检查时才宣称完成。
