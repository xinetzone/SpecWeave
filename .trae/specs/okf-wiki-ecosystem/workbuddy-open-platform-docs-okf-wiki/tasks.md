# WorkBuddy 开放平台官方文档 → OKF Wiki 知识包 - 实施计划

> 任务顺序遵循信源先行：采集台账 → 事实与核验 → concepts → examples → 根索引/log → 索引接入 → 机械门禁 → 独立评审。所有计数以实施时机械真值为准。

## Task 1: 信源采集与页级覆盖登记
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 复核 11 个已声明 URL（D0 `/dashboard` + D1～D10 十篇 `/docs/`）：逐条登记页面标题、正文完整要点（章节骨架与关键声明）、页面内出现的链接清单、HTTP 状态与响应字节数；`/dashboard` 登记为导航面（SPA 外壳，无正文）。
  - 从 `/docs/*` 各页 HTML 内嵌侧栏提取 `/docs/` slug 全集，逐条登记覆盖状态：已处理 10 篇 vs 未采集 7 篇（`api-token` / `contact` / `developer-profile` / `legal-basis-and-examples` / `operations-data` / `service-categories-individual` / `service-categories-enterprise`），未采篇逐条标注「本次未采集，仅登记入口」；显式排除非页面布局资源 `layout-216c2d1532f8d94c` 并给出依据。
  - 采集以纯 HTTP GET 为主；若某页正文缺失（改为客户端渲染），改走受控浏览器渲染读取并记录通道变化；仍不可得则记「未取得」并降级为「仅登记入口」，不以标题或导航推断正文。
  - 产出 spec 目录 `facts.md`（R 阶段事实清单草稿）与 `<束>/references/source-manifest.md`（页级台账七要素 + 侧栏 17 slug 覆盖状态 + 集合比对结论）。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-1.1: 11 个已声明 URL 逐条有台账记录，正文解析状态与实际采集结果一致；`source-manifest.md` 声明的页面集合与已处理集合双向差集为空；10 篇 docs 的正文要点与链接清单逐页可核。
  - `rule` TR-1.2: 每页记录含 URL、访问日期、标题、HTTP 状态与字节数、正文解析状态、知识归属（指向具体 concepts/examples 文件名）、覆盖状态七要素；侧栏 17 slug 逐条含 slug 与覆盖状态，7 篇未采集逐条带「本次未采集，仅登记入口」标注；`layout-216c2d1532f8d94c` 显式排除。
  - `rubric` TR-1.3: 采集深度与证据质量；scale 1-5；anchors 1=只登记 URL 不记内容/3=有要点但章节骨架与链接清单缺失未说明/5=逐页有可核对的章节骨架与关键声明，正文与链接清单完整，未采集项逐条标注并给出补救方式（可另行立束采集）；threshold >= 4；evidence 为 source-manifest.md 通读。
- **Notes**: `/docs/*` 已实测为服务端渲染且无需登录（与同组公告束的登录依赖不同）；不得点击任何提交/申请/购买/授权类按钮。本任务只写 references 与 spec `facts.md`，不动其他束。

- **Completion Evidence**（2026-10-16）：
  - **采集事实**：11 个已声明 URL 全部 **HTTP 200**；D1～D10 十篇 `/docs/` 均为**服务端渲染**（共用正文容器 `div.prose-docs_root__dXUM0`），纯 HTTP GET 即取全文，**无登录依赖**，本次**无采集通道变化**；D0 `/dashboard` 为 SPA 外壳（20,367 B / 8 个 `<script>` / 1 个应用挂载点）。逐页字节数取自 `meta.json` 实测值：D1 179,640 / D2 196,648 / D3 204,634 / D4 203,841 / D5 323,746 / D6 269,332 / D7 286,687 / D8 357,854 / D9 334,620 / D10 422,451。正文提取字符数 10 页合计 **97,917**。
  - **采集工具链**：临时脚本 `projects/awesome-okf-xs/.temp/wb-open-platform/extract.py`（requests + bs4 + markdownify，正文容器自动定位）+ `diag.py`（容器结构诊断）；产出 `meta.json`（页级实测元信息）与 `pages/*.md`（10 页正文提取，表格与代码块完整保留，实测 fences 74 个 / 表格行 936 行）。全部置于 `.temp/`（已 gitignore），依 NFR-6 于 Task 7 用后删除。
  - **产出 A** `spec/facts.md`（R 阶段草稿）：**2,220 行**、`- R-` 草稿条目 **513** 条（D1 21 / D2 47 / D3 32 / D4 20 / D5 66 / D6 41 / D7 44 / D8 69 / D9 88 / D10 85），`F-\d{3}` 命中 **0**（编号留待 Task 2 统一编定）；含覆盖统计表（10 页字节数与 meta.json 逐页一致）与「跨页观察」节（汇总四份分页草稿的提取瑕疵、D6/D7 结构差异、跨页口径不一致清单）。
  - **产出 B** `references/source-manifest.md`：frontmatter 合规（`okf_version` 命中 0、`file:///` 命中 0、`C:\Users` 命中 0）；页级台账 **11 行**（七要素齐备）；侧栏 **18 行**（17 篇 `/docs/` slug 逐条覆盖状态 + 非页面布局资源 `layout-216c2d1532f8d94c` 显式排除并给出四条机械判定依据）；未采集 7 篇逐条标注「本次未采集，仅登记入口」；集合比对「已声明 11 = 已处理 11、双向差集为空」「侧栏 17 篇中已处理 10、未采集 7」，并给出 `doc_links` 并集复现口径与复核脚本示意。
  - **偏差记录（spec 同步校正）**：`spec.md` 页面集合表原先填列的字节数是 .NET 字符串字符长度（`$r.Content.Length`），与采集脚本的 UTF-8 字节数口径不同。已按 meta.json 实测值统一校正为 UTF-8 字节数并改标列名为「核验时点实测（UTF-8 字节）」：D0 17,825→20,367、D1 130,961→179,640、D2 143,627→196,648、D3 150,531→204,634、D4 152,738→203,841、D5 258,745→323,746、D6 209,024→269,332、D7 221,631→286,687、D8 282,934→357,854、D9 255,907→334,620、D10 349,836→422,451。
  - **勘误发现（转 verification.md 登记）**：D5 页示例 MCP 配置中的 URL 原文为 `https://mcptokenSchema 字段.example.com/mcp`，含乱入字段名文本。已回源比对 `connector` 页原始 HTML 确认该字符串**存在于页面 HTML 本体**（非本束提取瑕疵），属**站点自身排版错误**；本束不得将其作为可用端点照抄，须在 `verification.md` 勘误清单登记并标注「以原文为准、疑似编辑错误」。
  - **纪律**：未修改同组既有束任何文件；束目录当前仅含 `references/source-manifest.md` 一个文件；未注册账号、未申请认证、未提交审核、未调用真实接口。
  - TR-1.1 / TR-1.2 / TR-1.3 自验通过（数值均由主会话实测命令核出）。

## Task 2: 事实编号、口径分层与核验
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 以 `facts.md` 为源，登记 `F-001` 起编号事实（自本束起编，不与他束编号体系混合）；覆盖：平台定位与八步快速开始、五大业务类型（技能 / 专家 / 专家团 / 连接器 / 外部应用接入）、个人与管理员实名与企业三档认证及认证结果规则、入驻与上传企业信息与企业验证、技能基础结构与子资源目录与技能市场、连接器两种接入方式与元信息/认证与凭证/图标规范/提交前检查、专家与专家团的结构与配置文件与字段与行业分类与专家市场、Buddy 应用六大自定义维度与配置指引与发布流程与企业单管理与设计规范、第三方应用三种形态、Open API 准备工作与七类接口与返回码规范、变现五节（功能概述/开通入驻/发布付费资产/管理收入/常见问题）、口径落差与时效项。
  - 产出 `references/article-source.md`：来源代号表（D0～D10）+ F 编号事实表（每条含声明摘要、来源代号、核验状态）。
  - 产出 `references/verification.md`：核验总表（核验时点 2026-10-16、11 URL 可达性与字节数、侧栏 17 slug）、勘误清单、**五类口径分层并列登记表**、信源距离评估（厂商文档单源）、V 四视角对抗审查表、status 裁决节。
  - 产出 `references/index.md`（无 frontmatter，toctree 收三件）。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-2.1: `article-source.md` 的 `^\|\s*F-\d{3}\s*\|` 表行与 `facts.md` 的 `F-\d{3}` 集合机械比对相等、连续无跳号无重复；来源代号表覆盖 D0～D10 全部实际引用来源。
  - `rule` TR-2.2: `verification.md` 五类口径逐项有独立小节或表格行——①文档口径 vs 平台现状（列出「未实跑」与「官方未给」清单）；②声明集合 vs 站点全集（11 vs 17，7 篇未采集逐条）；③端与接入形态边界（PC 本地助理 / 云侧云端任务与 ACP 与会话产物 / 第三方应用分享与硬件入口）；④免费与付费资产及变现开通门槛；⑤身份与资质三档认证门槛 + 版本时效并列（文档站无统一版本号 vs 5.7.7 vs 5.8.0）。
  - `rule` TR-2.3: 信源全部为实际读取成功的 URL；未取得的页面标「本次未采集，仅登记入口」或「未取得」，不编造能力细节；不得出现「已 GA / 已上线 / 已完成审核」类替官方宣布表述；接口参数、字段取值、审核时长、结算比例凡文档未给一律标「官方未给」。
  - `rubric` TR-2.4: 核验结论可辩论性；scale 1-5；anchors 1=只给结论不给证据/3=有证据但口径混写/5=每条结论挂信源与状态标签、不利证据（未实跑、未采集页、文档无版本号、厂商单源）显式呈现；threshold >= 4；evidence 为独立评审通读。
- **Notes**: 与同组束口径冲突时按「并列表述、不互相替换」处理（与 `workbuddy-official-docs`、`workbuddy-open-platform-sharing-and-promotion`、`wecom-5-0-12-release` 的口径分层先例一致）。跨束引用按「该束 F-xxx 号」表述，不得污染本束 `F-\d{3}` 编号集合。

- **Completion Evidence**（2026-10-16）：
  - **产出 A** `references/article-source.md`：来源代号表 D0～D10（D0 显式标注「导航面，无文档级声明，不产生 F 编号」）；**F 编号事实表 439 行**，列序 `| F 编号 | 声明摘要 | 来源代号 | 所属页面章节 | 核验状态 |`，行首为 F 编号，满足 `^\|\s*F-\d{3}\s*\|`；编号 **F-001～F-439 连续、无跳号、无重复**（机械复算 `Compare-Object` 差集 0、min/max = 1/439、unique 439）；含编号统计与来源覆盖、四类去重口径（跨页重复只计一次／同章节同义合并／跨页口径不一致并列保留／未写明项不入表）与抽查 8 条回源记录（F-022、F-062、F-083、F-143、F-165、F-226、F-346、F-393 逐条与采集缓存正文一致）。
  - **产出 B** `spec/facts.md`（由产出 A 机械派生）：**439 条** F 编号事实，含编号统计、逐来源代号条数表、**多来源事实表 25 条**、F 编号事实清单（行格式 `- **F-xxx**｜摘要｜来源｜章节｜核验状态`）。**机械比对（主会话实跑）**：`article-source.md` 表行 F 集合（439 unique）与 `facts.md` 的 `F-\d{3}` 唯一集合（439）**`Compare-Object` 差集为空**（相等）。
  - **产出 C** `references/verification.md`（八节齐备，16,788 字符）：一、核验总表（含 11 URL 逐页 URL/标题/UTF-8 字节数表，数值与 `source-manifest.md` 逐条一致）；二、勘误清单 **E1～E3**（E1 = D5 示例 MCP URL 含乱入文本，对应 **F-105**，回源 HTML 证实属站点自身错误，处置为「不得作为可用端点照抄，标明原文如此、疑似编辑错误」；E2 = D2「开发者真实姓名 / 真实姓名」并列，对应 **F-040**，处置为照抄并列不合并；E3 = D5/D6/D7 正文悬空章节引用「见 6.3／6.4／第六节／第九节」，附回源实例，处置为不得据编号推断）；三、**五类口径分层并列登记表**（①文档口径 vs 平台现状、②声明集合 vs 站点全集 11 vs 17、③端与接入形态边界 **含与同组公告束的互证小节**、④免费/付费资产与变现两步门槛、⑤身份资质三档门槛 + 版本时效三方并列）；四、跨页口径不一致并列登记 **2 组**（F-308 `PSS` vs F-346 `PKCS#1`；F-285 `24h` vs F-366 `expires_in: 3600`）；五、官方未给清单 **10 条**；六、信源距离评估（厂商单源）；七、V 四视角对抗审查表（四视角共 13 个攻击点 + 处置，并留 Task 7 门禁结果占位行）；八、status 裁决（`stable` + 三条降级条件）。
  - **产出 D** `references/index.md`：**无 frontmatter**，首行为 `{toctree}`，条目 `article-source` / `source-manifest` / `verification` 三件对应文件均存在。
  - **机械门禁（主会话实跑）**：`article-source.md` 的 `okf_version` 0 命中、`C:\Users` 0 命中；`verification.md` 的 `okf_version` 0 命中、`file:///` 0 命中、`C:\Users` 0 命中，`## ` 二级标题 8 个与规划逐一对齐。`article-source.md` 的 `file:///` 命中 **1 处**，系 **F-423 引述官方文档所述 Artifact 本地 URI 协议形态**（「本地形如 file:///…」），非仓库路径引用；「已 GA / 已上线 / 已完成审核」命中 3 处**全部位于该文件自身的禁止性条款**（「本表不得出现…类表述」），非正文断言。
  - **偏差记录**：`facts.md` 初版为 R 阶段逐页草稿（2,220 行 / 513 条 `R-<slug>-NN`）。定稿时改为**由 `article-source.md` 机械派生**（而非人工重写两份），以按构造保证两处 F 编号集合相等、消除人工复制的漂移风险；R 阶段逐页细节（字段表、目录树）不再重复入库，其原始正文存于采集缓存。
  - TR-2.1 / TR-2.2 / TR-2.3 / TR-2.4 自验通过（集合比对、口径五类、勘误与未给清单、抽查回源均有实测证据）。

## Task 3: concepts 十一篇 + concepts/index.md
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 产出 `concepts/00-overview-and-quickstart.md`、`01-onboarding-and-qualification.md`、`02-skill-development-and-marketplace.md`、`03-connector-development-and-access-modes.md`、`04-expert-and-expert-team.md`、`05-buddy-app-develop-and-publish.md`、`06-third-party-app-access.md`、`07-openapi-auth-and-conventions.md`、`08-openapi-endpoint-catalog.md`、`09-monetization-and-revenue.md`、`10-boundaries-versions-and-known-gaps.md` 共 11 篇，每篇回答一个明确问题，所有步骤、字段名、章节名、接口名、业务类型名、门槛条件与状态码声明均挂 F 编号。
  - 至少 1 张 Mermaid 图：建议 `00` 篇含「注册入驻 → 资质认证 → 创建业务类型 → 完善基础信息与能力配置 → 测试环境调试 → 提交平台审核 → 审核通过发布上线 → 持续查看运行数据与版本维护」八步上架 flowchart；或 `07` 篇含 OAuth 2.1 授权码换取凭证的 sequenceDiagram（用户 → 客户端 → `/authorize` → 授权码 → `/token` → access_token/refresh_token → 调接口）。
  - `05` 篇含 Buddy 应用六大自定义维度表；`08` 篇含七类接口总表（认证授权 / 个人资料 / 本地助理 / 云端任务 / ACP 通道 / 会话产物 / 兑换码核销），逐类标注端或形态归属与权限要求。
  - `10` 篇汇总五类口径分层、7 篇未采集页清单、时效项与「官方未给」清单。
  - `concepts/index.md`：toctree 收 00～10，并给一句话导读表（读者问题 → 篇名）。
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `rule` TR-3.1: 11 篇文件全部存在，每篇 frontmatter 完整（`type`=Concept、`sources` 只列该篇实际引用信源、`generated`/`verified`/`status`/`stale_after` 齐备）；Grep 抽查关键声明（八步流程名、业务类型名、接口名、字段名、状态码）均带 F 引用。
  - `rule` TR-3.2: 至少 1 张 Mermaid 图存在且节点或说明挂 F 依据；五类口径标签（文档口径/未实跑、采集覆盖、端与形态边界、免费付费与变现门槛、资质门槛+时效）在各篇至少合计出现且与 `facts.md` 状态一致；`08` 篇七类接口逐类含权限或形态标注。
  - `rubric` TR-3.3: 分层清晰度（对应 AC-6）；scale 1-5；anchors 1=按文档顺序平铺翻译/3=有分层但层间重复或跨篇跳转不清/5=每篇回答一个明确问题、篇间阅读路径明确、层内无重复、接口分类与形态边界一目了然；threshold >= 4；evidence 独立评审逐篇评分。
- **Notes**: 跨束引用用相对路径；`concepts/` 位于子目录，引用同组平级束需 `../../` 深度（既有束曾因误用 `../` 产生断链，实施后必须机械 `Test-Path` 复核）。若实读章节骨架与 spec 中「已核验的页面章节骨架」不一致，按实读为准并在本任务 `Completion Evidence` 记录偏差。

- **Completion Evidence**（2026-10-16）：
  - **产出**：`concepts/` 建成 **12 个文件**（11 篇内容文档 + **无 frontmatter** 的 `index.md`，首行 `{toctree}`、`:hidden:`/`:maxdepth: 2`、**11 条目**对应文件全部存在，导读表 11 行）。逐篇行数：`00` 102 / `01` 104 / `02` 149 / `03` 218 / `04` 256 / `05` 210 / `06` 219 / `07` 206 / `08` 369 / `09` 103 / `10` 144（`04`/`06` 含本轮补写 +5/+7）。
  - **机械校验（主会话实跑，bundle 全量脚本）**：content 文档 `okf_version` 命中 **0**；`C:\Users` 命中 **0**；`.temp` 路径引用 **0**；**相对链接断链 0**（Task 3 完成时指向 `examples/` 的 5 条待建链接已在 Task 4 落地后转为 0）。
  - **F 引用**：累计 **863 处**，**distinct 439 / 439 全覆盖、越界 0**。首轮复算发现 **7 条 F 未被任何概念文档引用**（F-181 / F-185 / F-186 属 D6·D7；F-324 / F-330 / F-332 / F-345 属 D9），已按「修复即闭环」补写织补——F-181 落「六、内置 MCP 与连接器依赖」、F-185/F-186 落「注意事项」子条（F-186 安全红线加粗）、F-324/F-345/F-330+F-332 落 `06` 篇消息负载与 PC 端链接小节；补写后覆盖率 439/439、原有内容与既有 F 引用零删改。
  - **Mermaid**：**2 张**（`00` 篇八步上架 flowchart；`07` 篇 OAuth 2.1 授权码 sequenceDiagram，含刷新/过期分支），经仓库脚本 `.agents/scripts/check-mermaid-quotes.py` 实跑——「扫描 2 文件 / **通过 2 项** / 所有 Mermaid 代码块引号检查通过」。
  - **口径落地抽测**：「官方未给」83 处、「本次未采集，仅登记入口」16 处、「并列」76 处、「不择一」20 处、「原文瑕疵」2 处；替官方宣布短语 37 处**逐行核查全部处于禁止性/澄清性语境**（无一条为断言式使用）。
  - **`file:///` 例外登记**：concepts 内 3 处命中**全部位于 `08` 篇**，系 F-423 所述 Artifact 本地 URI 协议形态（`本地形如 file:///…`）及其显式「引述原文协议形态」标注（L283 / L291），**非仓库路径引用**。
  - **偏差记录（如实登记原文张力）**：① `05` 篇：原文措辞为「六个维度」而正文仅列 5 个 h3 小节 → 如实登记「原文分别表述为…」，明言第六项官方未给，**不凑数**；② `04` 篇：`tags` 字段并列「4 项」与「固定 3 个」两种措辞；③ `05` 篇：规格并列「3–5」与「2–4」两种口径——三处均按「并列表述、不替官方判定」处理。
  - TR-3.1 / TR-3.2 / TR-3.3 自验通过（frontmatter 逐文件合规、Mermaid 机械通过、F 引用越界 0 且覆盖 439/439、口径标签齐备）。

## Task 4: examples 五篇 + examples/index.md
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 产出 `examples/00-onboarding-and-certification.md`（个人认证 → 管理员实名认证 → 企业认证 → 认证结果与规则 → 入驻开放平台 → 上传企业信息 → 完成企业验证）。
  - 产出 `examples/01-build-and-submit-a-skill.md`（技能基础结构与子资源目录 → 元信息与能力配置 → 本地调试 → 提交审核 → 技能市场上架）。
  - 产出 `examples/02-build-and-submit-a-connector.md`（选择 CLI + Skill 或 MCP + Skill 接入方式 → Skill 文件与连接器元信息 → 认证与凭证 → 图标规范 → 提交前检查）。
  - 产出 `examples/03-oauth-and-call-openapi.md`（准备工作 → `/authorize` 取授权码 → `/token` 换 access_token/refresh_token → 调个人资料与本地助理接口 → 刷新凭证 → 按返回码规范处理错误）。
  - 产出 `examples/04-publish-and-manage-a-paid-asset.md`（开通入驻 → 发布付费资产 → 管理收入 → 常见问题排查）。
  - 每篇含前置条件、操作步骤、结果判据、限制与边界；未在本机实跑的步骤显式标注「未在本机实跑，依据官方文档（F-xxx）」。
  - `examples/index.md`：toctree 收 00～04 + 场景导览表。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 5 篇文件全部存在，frontmatter 合规；每篇含「前置条件 / 操作步骤 / 结果判据 / 限制与边界」四段结构；所有未实跑步骤含显式标注（Grep 抽查）。
  - `rule` TR-4.2: 步骤中出现的功能名、页面路径、配置项名、接口名与字段名均可在对应 concepts 或文档页找到出处（F 编号），无凭空补全的操作路径；不得编造文档未给出的接口参数、审核时长与结算比例。
  - `rubric` TR-4.3: 操作可用性；scale 1-5；anchors 1=步骤缺失无法照做/3=步骤完整但结果判据含糊或前置不清/5=前置/输入/步骤/判据/限制完整，读者可据此判断能否在本机复现以及哪一步必须依赖平台审核；threshold >= 4；evidence 独立评审抽查。
- **Notes**: 不注册账号、不申请认证、不提交审核、不生成密钥与 token、不调用真实接口；示例中的命名与门槛一律以文档为准，不虚构。

- **Completion Evidence**（2026-10-16）：
  - **产出**：`examples/` 建成 **6 个文件**（5 篇内容文档 + **无 frontmatter** 的 `index.md`，首行 `{toctree}`、`:hidden:`/`:maxdepth: 2`、**5 条目**按文件名升序、场景导览表 5 行齐备）。逐篇行数：`00` 82 / `01` 116 / `02` 262 / `03` 236 / `04` 84。
  - **四段结构**：5 篇**全部 4/4** 齐备（`## 前置条件` / `## 操作步骤` / `## 结果判据` / `## 限制与边界`）。
  - **未实跑标注**：「未在本机实跑」在 5 篇内分别命中 **14 / 15 / 13 / 11 / 15** 处，逐步骤标注到位（步骤编号 1–13 连续标注）。
  - **机械校验（主会话实跑）**：content 文档 `okf_version` 命中 **0**；`C:\Users` **0**；`.temp` **0**；**相对链接断链 0**；F 引用 **519 处、distinct 177、越界 0**。
  - **口径落地**：① **E1**（D5 示例 MCP URL 含乱入文本，F-105）处置于 `02` 篇勘误框与限制边界——「原文如此（含乱入文本），疑似编辑错误，**以官方页面为准**」、「**不得**作为可用端点照抄」；② **E2**（D2「开发者真实姓名 / 真实姓名」并列）处置于 `00` 篇操作步骤第 2 步——照抄并列、不合并、不推断；③ 两处跨页口径冲突并列于 `03` 篇「两处官方口径并列（不择一）」——签名填充 `PSS`（F-308）/ `PKCS#1`（F-346）、凭证有效期 `24h`（F-285）/ `expires_in: 3600`（F-366），注明各自来源页面；④ 端/形态边界带端别（本地助理属 **PC 端本机**、云端任务/ACP/会话产物属**云侧**）；⑤ 分成比例与结算周期标「**官方未给**」。
  - **`file:///` 例外登记**：examples 内 5 处命中**全部位于 `03` 篇**——L191 引述 Artifact `uri` 形态（`agent:///…`、`file:///…`）、L192 显式「**引述原文协议形态**」标注、L233「`file:///` 使用边界」澄清声明，**均为引述字面量而非仓库路径引用**。
  - **纪律**：未注册账号、未申请认证、未提交审核、未生成密钥与 token、**未调用任何真实接口**、未产生任何真实收入数据。
  - TR-4.1 / TR-4.2 / TR-4.3 自验通过（四段结构齐备、未实跑逐步骤标注、E1/E2 与两处冲突按合同处置、F 引用越界 0 且均可在 F 表定位）。

## Task 5: 根 index.md、log.md 与 references 收口
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - `index.md`：OKF v0.2 frontmatter（`okf_version: "0.2"`、`type: bundle`、`status`、`stale_after: 2027-04-16`、`sources` 全列 D0～D10）、内容性质块（开发者文档教程化、设 examples 的理由与未实跑声明）、可信度状态块、「这束知识包讲什么」分层导读表、已知边界（五类口径 + 单源清单 + 未实跑声明 + 7 篇未采集清单 + 时效项）、主题关联（同组既有 3 束 + codebuddy）、一句话结论、toctree（`concepts/index`、`examples/index`、`references/index`、`log`）。
  - `log.md`：初始版本条目，记录七阶段执行、口径决策（范围收敛与单束裁定取自用户批准）、覆盖统计、并行在途观测、门禁运行方式与未运行 `invoke` 的声明、独立评审结论留位。
  - 收口 `references/index.md` 与各子目录 index 的 toctree 完整性。
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `rule` TR-5.1: 根 `index.md` 的 toctree 四条目（`concepts/index`、`examples/index`、`references/index`、`log`）对应文件全部存在；`okf_version` 仅出现在根 `index.md`，子文档不含。
  - `rule` TR-5.2: `log.md` 无 frontmatter、日期标题为 `YYYY-MM-DD` 倒序结构，内容含七阶段、覆盖页数（11 URL / 17 slug）、口径决策、门禁方式四类信息。
  - `rubric` TR-5.3: 已知边界可决策性；scale 1-5；anchors 1=边界缺失或与正文矛盾/3=主要边界有但分散/5=集中声明且每条挂 F 编号，读者可直接判断「谁能入驻 / 能开发哪些业务类型与接口 / 哪些页未采集 / 哪些为官方未给」；threshold >= 4。
- **Notes**: 「已知边界」需明确区分「官方未宣告」与「本束未采集」，不得把未采集写成不存在，也不得把未实跑写成已验证。

- **Completion Evidence**（2026-10-16）：
  - **产出**：`index.md`（**83 行**）+ `log.md`（**57 行**）；全束 Markdown 总数达 **24 个**（束根 2 + concepts 12 + examples 6 + references 4）。
  - **`okf_version` 位置校验**：全束命中 **1 处**，**仅在束根 `index.md`**（脚本逐文件核出，其余 23 个文件命中 0）。
  - **束根 toctree**：4 条目 `concepts/index` / `examples/index` / `references/index` / `log` **对应文件全部存在**；三个子目录 `index.md` 的 toctree 条目（concepts 11 / examples 5 / references 3）**逐条对应文件均存在、无缺失**。
  - **`index.md` 必备块**：内容性质块（含「设 examples/ 的理由 = 文档给出步骤化链路但审核与上架结果由平台判定、本机无法闭环」与未实跑声明）、可信度状态块（厂商单源、`/docs/*` 服务端渲染**无登录依赖**、与同组公告束登录条件对比）、「这束知识包讲什么」分层导读表（11 concepts + 实操 + 查证三行）、**已知边界 8 条**（①厂商自述无第三方核验 ②未在本机实跑 ③未采集 ≠ 不存在（7 篇 slug 逐条 + 非页面资源排除）④官方未给清单 ⑤跨页口径不一致并列 ⑥版本时效三方并列并注明后两个数字属同组束 ⑦勘误 E1～E3 ⑧端/形态边界带端别）、**主题关联 4 束平级互链**（`../workbuddy-official-docs/index.md`、`../workbuddy-open-platform-sharing-and-promotion/index.md`、`../workbuddy-hardware-integration-whitepaper/index.md`、`../codebuddy/index.md`）、一句话结论。
  - **`log.md` 必备内容**：**无 frontmatter**、倒序日期标题 `## 2026-10-16`；覆盖七阶段执行、覆盖统计（11 URL / 17 篇侧栏（处理 10、未采集 7）/ F-439 / 24 个 Markdown / 97,917 字符）、口径决策（范围收敛与单束裁定**源自用户批准门**）、采集方式与登录依赖对比、勘误与偏差（E1～E3 + `05` 篇六维度措辞张力、`04` 篇 tags 两种口径、`05` 篇规格 3–5 vs 2–4）、**门禁运行方式（显式声明直接跑子模块底层脚本、未运行 `invoke gates.*`，不谎报）**、独立评审结论留位、并行在途观测留位。
  - **机械校验（主会话实跑，全量 24 文件）**：`okf_version` **1**；**相对链接断链 0**；`C:\Users` **0**；`.temp` 路径引用 **0**；断言式「替官方宣布」可疑行 **0**（脚本对每行判定是否含禁止性/澄清性标记，无一漏判）；F 引用累计 **2,034 处、distinct 439/439**。
  - TR-5.1 / TR-5.2 / TR-5.3 自验通过（`okf_version` 位置合规、`log.md` 结构合规、已知边界就绪）。

## Task 6: 五级索引接入、计数复算与同组互链
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - `tencent/index.md`：导航表 +1 行、toctree +1 条、「关于本分组」段追加本束说明与生成来源（含束数与概念/示例/信源/事实计数按机械真值复算）、「相关链接」+1 行。
  - `ecosystems/index.md`（腾讯生态行与类计数）、`jishu/ai/index.md`（frontmatter description 与正文计数及 ecosystems 行）、`jishu/index.md`（ai 行）、`doc/bundles/index.md`（`total_bundles`、正文计数行、mermaid `jishu` 节点文字、节标题、分组表 ai 行）逐层同步。
  - `workbuddy-official-docs/index.md` 与 `workbuddy-open-platform-sharing-and-promotion/index.md` 各回补 1 条指向新束的链接（`git diff` 核对各仅新增 1 行超链接）。
  - 机械复算：自包含脚本按 marker 目录（concepts/examples/references）+ 锚点束=1 口径清点 tencent/ai/jishu 三级真值，与 `check-bundles-index.py` 输出对齐；临时脚本用后删除。
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-6.1: `python scripts/check-bundles-index.py` 在无并行写入窗口退出码 0、五面一致；输出计数与写入索引的数字逐项相等。
  - `rule` TR-6.2: `python scripts/check-toctrees.py` 全量输出过滤本束名零命中；既有/并行污染项只在 `log.md` 列名披露，不顺手修复。
  - `rule` TR-6.3: 两束既有 `index.md` 的 `git diff` 各恰为 +1 条互链，其事实、计数、正文其他部分零改动；新束 `index.md`「主题关联」含反向链接；本束未修改同组其他束文件（`git status` 逐文件核对）。
- **Notes**: 若观察并行会话实时改写总索引，以最后一次无写入窗口的脚本输出为准并在 `log.md` 记录观测事实；既有束「信源」基数若不可由显式口径复现，按既有先例只记增量、不重定基数（同组 `workbuddy-open-platform-sharing-and-promotion` 束已披露同类观测）。

- **Completion Evidence**（2026-10-16，数字均由主会话复跑脚本独立核出）：
  - **五级索引接入（改动前 → 改动后）**：`tencent/index.md` **16 / 124 / 43 / 72 / 2393 → 17 / 135 / 48 / 76 / 2832**（束 / 概念 / 示例 / 信源 / 事实）；`ecosystems/index.md` **类总 92 → 93、腾讯行 16 → 17**；`jishu/ai/index.md` **244 → 245、ecosystems 行 92 → 93**；`jishu/index.md` **ai 行 244 → 245**；`doc/bundles/index.md` —— `total_bundles` **639 → 640**、正文计数行 **639 → 640**、mermaid `jishu` 节点文字 **473 → 474**、节标题 **473 → 474**、分组表 ai 行 **244 → 245**。`tencent/index.md` 另新增导航表 1 行、toctree 1 条（`workbuddy-open-platform-docs/index`）、「关于本分组」本束生成说明 1 段、「相关链接」1 行。
  - **门禁结果**：`python scripts/check-bundles-index.py` **改前退出码 1**（3 处漂移：`total_bundles` / 节标题 / 分组表各差 +1，即脚本已识出新束而索引未同步），**改后退出码 0** —— 输出「**9 域 / 61 组 / 640 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致」；`python scripts/check-toctrees.py` **改前退出码 1**（25 处，**全部归属本束**：24 条未收录 + 1 条缺失条目），**改后退出码 0** —— 「全部 index.md 引用有效，所有内容文档均可达」。主会话**独立复跑**两道门禁，均为 **EXIT=0**，输出与上一致。
  - **同组互链（最小改动纪律）**：`workbuddy-official-docs/index.md` 与 `workbuddy-open-platform-sharing-and-promotion/index.md` 各回补 1 条指向新束的链接，`git diff --numstat` **各为 `1  0`**（恰 +1 行、零删除）；新增行内容分别为「平台开发接入 vs 产品本体能力互补读法」与「D9 文档口径（PC 端 + ≥5.8.0）与两篇公告互证、文档站无统一版本号可与『公告先行于产品文档』落差并列阅读」。
  - **改动范围核对**：`git status --short` 显示**仅 7 个受跟踪索引文件被修改**（`doc/bundles/index.md`、`jishu/index.md`、`jishu/ai/index.md`、`jishu/ai/ecosystems/index.md`、`jishu/ai/ecosystems/tencent/index.md`、`tencent/workbuddy-official-docs/index.md`、`tencent/workbuddy-open-platform-sharing-and-promotion/index.md`）+ 新束目录**未跟踪**；**同组其他束零改动**（`git diff --name-only` 逐文件核对）。
  - **计数口径观察（披露不修复）**：「信源」基数**不可由显式口径复现**——按同组既有束口径（`references/` 下文件数含 index）机械求和为 **79**，而声明基数为 **76**，故**按增量 +4 登记、不重定基数**（与同组 `workbuddy-open-platform-sharing-and-promotion` 束披露的同类观测一致）；该观察已记入新束 `log.md`「### 九、索引接入与门禁实测」。
  - **未执行** git commit / push。
  - TR-6.1 / TR-6.2 / TR-6.3 自验通过（五面一致退出码 0、本束名零命中、两束回链各 +1 行且其余零改动）。

## Task 7: V 阶段机械门禁与四视角自审
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 运行 `python scripts/check-utf8.py`；Grep 全部新增文件的 Markdown 链接并逐一 `Test-Path`；Grep 零 `file:///`、零 `C:\Users`/家目录路径；逐文件核对 frontmatter 必填字段与 `okf_version` 位置。
  - 正则比对 `facts.md` 与 `article-source.md` 的 F 编号集合相等。
  - 定向 Sphinx dummy 构建验证本束无引入错误（不声称全库通过）。
  - 四视角自审（魔鬼代言人 / 新人 / 业务方 / 未来维护者）结论并入 `verification.md`；可当场收口的 advisory 当场收口。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4
- **Test Requirements**:
  - `rule` TR-7.1: UTF-8 门禁通过；束内全部相对链接 `Test-Path` 存活；零 `file:///`、零本机绝对路径；frontmatter 与 `okf_version` 位置合规。
  - `rule` TR-7.2: F 编号双份集合比对相等；定向构建无本束引入错误。
  - `rubric` TR-7.3: 四视角攻击覆盖度；scale 1-5；anchors 1=自审走过场/3=有攻击点无处置记录/5=每视角有具体攻击点、处置方式与可复核证据；threshold >= 4；evidence 为 verification.md 自审表。
- **Notes**: 全库既有断链/编码问题按归属隔离，如实报告，不扩大修复范围。本阶段只做核验与最小收口，不新增功能。

- **Completion Evidence**（2026-10-16，主会话独立复跑核出）：
  - **八项门禁实测（工作目录 = 子模块根；直接运行底层脚本，`invoke gates.*` 本次未使用）**：
    ① `python scripts/check-utf8.py` **EXIT 0**（11,675 文件均为有效 UTF-8）；
    ② `python scripts/check-toctrees.py` **EXIT 0** —— 「全部 index.md 引用有效，所有内容文档均可达」，**本束名零命中**；
    ③ `python scripts/check-bundles-index.py` **EXIT 0** —— 「9 域 / 61 组 / **640 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致」；
    ④ **相对链接存活 242 / 242、失败 0**（24 个文件的 Markdown 相对链接逐条 `Test-Path`）；
    ⑤ `file:///` 命中 12 行（原始 6 行 / 3 文件）、`C:\Users` **0** 命中；`file:///` 全部为**引述官方文档所述 Artifact `uri` 协议形态**（`concepts/08`、`examples/03`、`references/article-source.md`）并**逐处有显式标注**；
    ⑥ **frontmatter 逐文件核对通过**：`okf_version` **仅 1 处（束根 `index.md`）**；`log.md` 与三个子目录 `index.md` **无 frontmatter**；11 篇 `Concept` / 5 篇 `Example` / 3 篇 `Reference` 均含 `generated`+`verified`+`status`+`stale_after` 与 `sources`；
    ⑦ **F 编号双份集合比对**：`facts.md` 与 `article-source.md` 均为 **439**、**差集 0**、F-001～F-439 **连续无重复**（主会话复跑确认）；
    ⑧ **定向 Sphinx dummy 构建 EXIT 0**：全库 245 warnings 属既有/并行束，**提及本束的 WARNING = 0**（按归属隔离，不声称全库通过）。
  - **门禁抓出的本束缺陷：1 项（advisory 类，已当场收口）** —— `references/article-source.md` 中 F-423 行的 `file:///…` 引述**缺少显式标注**，已在文件末补「**`file:///` 例外（引述原文协议形态）**」说明节（L497），与 `concepts/08`、`examples/03` 的同类标注一致。
  - **四视角自审**：`verification.md` 第七节原占位行已**替换为「机械门禁实测小结（Task 7，2026-10-16）」**（L275），并新增 2 条四视角攻击点行；既有 13 个攻击点与处置、以及第三节五类口径结构、第五节官方未给 10 条**均保持原样未动**。
  - **`log.md` 追加**「### 十、机械门禁实测（Task 7）」（L92），既有小节一～九未动。
  - **临时产物清理（NFR-6）**：采集缓存 `projects/awesome-okf-xs/.temp/wb-open-platform/`（采集脚本、诊断脚本、派生脚本、校验脚本、`meta.json`、`pages/`、`facts/`）**已整体删除**，`Test-Path` 复验为 `False`；本次定向构建副产物（`_build/dummy-bundle*`、门禁日志）一并清理，`_build/` 下其他目录属他任务未动。
  - TR-7.1 / TR-7.2 / TR-7.3 自验通过（八项门禁退出码/存活比/命中分类/集合比对/定向构建 WARNING 归属均有实测输出）。

## Task 8: 独立上下文评审 R1 与收尾
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 队列清空后新建 `review.md`（CP-R1～R6 规则检查点 + CP-U1/U2 量规，覆盖 AC-1～AC-6）。
  - 委派 fresh-context 只读子代理执行独立评审（提供绝对路径、运行命令与评审合同：11 URL 覆盖与编号双份、五类口径分层、链接与编码门禁、五级计数一致、同组互链最小改动、examples 未实跑标注与「官方未给」纪律）。
  - 结果路由：`pass` 则写 Review History 并向用户汇报、给出 C 阶段提交方案供决策；`fail` 则把可行动发现固化为 pending 修复 issue 回 Implement，回归后开新 R2；`blocked` 则记录阻塞并请求解决。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-8.1: `review.md` 每个 AC 至少被一个检查点覆盖；R1 结果为 `pass`（若 `fail` 必有非空 pending 修复队列且回归后开 R2）。
  - `rubric` TR-8.2: 评审独立性与证据质量；scale 1-5；anchors 1=主会话自审冒充/3=独立评审但证据笼统/5=fresh 子代理逐检查点给出命令与文件证据并独立复核页面；threshold >= 4。
- **Notes**: 本任务只在 Review 阶段创建/修改 `review.md`；不执行 git commit；评审通过后在汇报中给出 C 阶段提交方案（子模块 → 主仓 spec → 子模块指针，显式文件列表）供用户决策。

- **Completion Evidence**（2026-10-16）：
  - **`review.md` 建成**：CP-R1～CP-R6 六项 `rule` 检查点 + CP-U1 / CP-U2 两项 `rubric`（含 Scale/Anchors/Threshold），**覆盖 AC-1～AC-6 全部标准**，并含 Review History R1。
  - **独立评审执行**：委派 **fresh-context 只读子代理**——**未参与实施、未参考实施者自验结论**，全程**未修改任何文件、无 git 写操作**；评审者**自行复算全部数字**（不采信 `tasks.md` 中的实施者证据），自跑三道具名门禁、`git status`/`git diff --numstat`、自写正则脚本（F 双份集合、24 文件 frontmatter、242 条链接存活）、断言措辞逐行判定、examples 结构与标注计数、定向 Sphinx 构建，并**以 HTTP GET 回源 9 个官方页面做反证抽查 13 条 F 事实**，最后自行清理 `_build/review-dummy*`。
  - **裁决：`pass`** —— **CP-R1～CP-R6 六项 `rule` 全部 `pass`**；**CP-U1 = 5/5**（教程可用性与知识分层质量）、**CP-U2 = 5/5**（评审独立性与证据质量），阈值均 ≥4；**可行动发现 0 条**。
  - **advisory 发现 1 条，已当场收口**：**F1** —— `references/verification.md` 门禁小结第 5 行原写「`file:///` 原始内容命中 6 行 / 3 文件」与实测不符；已改为精确口径「全束 `file:///` 共 **12 行命中、无一处为仓库路径用法**；其中 **3 处为引述**（`concepts/08`、`examples/03`、`article-source.md` F-423 行）且**每处引述均相邻标注『引述原文协议形态』**；其余 9 行为标注行与说明性提及」。advisory 类不阻塞验收。
  - **评审侧独立复核结果（与实施者证据一致）**：`check-bundles-index.py` / `check-toctrees.py` / `check-utf8.py` **均 EXIT 0**；定向构建 **EXIT 0**、**本束 WARNING = 0**；两既有束 `git diff` **各恰 +1 行、零删除**，全库仅 7 个受跟踪文件被改 + 本束未跟踪；F 双份集合 **439 / 439、差集 0、连续无重复**；链接**存活 242 / 失败 0**；frontmatter 逐文件合规（`okf_version` 仅束根）。
  - **收尾**：`log.md` 第七节（独立评审结论）与第八节（并行在途观测）已**据实回填**、第六节留位句已改为「已补充」指向第九/十节；spec 目录四件产物齐备（`spec.md` / `tasks.md` / `facts.md` / `review.md`）。
  - **未执行** git commit / push；C 阶段提交方案随交付汇报提交用户决策。
  - **C 阶段提交实测（2026-10-16）**：主仓 `git commit` 的 **pre-commit 敏感信息钩子**拦下 `facts.md` L444 中的手机号示例值 `13812345678`。**已回源核实**该值系 D10 `/docs/openapi`「个人资料 API › 验证用户联系方式」**手机号格式要求**的**官方示例值**（该页 9 处命中，正文形如 `"phone_number": "+8613812345678"`），**非真实个人信息**，故不脱敏以保原文保真；处置采用钩子**明文允许**的「示例数据行尾 `# nosec`」标记后再提交，**未使用 `SENSITIVE_CHECK_SKIP`、`SENSITIVE_CHECK_WARN_ONLY` 或 `--no-verify` 等任何跳过手段**。同源示例值在束内 `concepts/08-openapi-endpoint-catalog.md` 与 `references/article-source.md` 保持逐字原文（该值属官方文档内容，两束文件已随子模块提交入库）。
  - TR-8.1 / TR-8.2 自验通过（每个 AC 至少一个检查点覆盖、R1 结果 `pass` 且无 pending 修复队列、评审独立性与证据质量 5/5）。

## 依赖关系

- Task 2 依赖 Task 1（无台账无法登记事实归属）。
- Task 3 依赖 Task 2（concepts 的 F 引用须先有编号事实）。
- Task 4 依赖 Task 3（examples 的功能口径与 concepts 一致）。
- Task 5 依赖 Task 4（根索引导读表需覆盖全部篇目）。
- Task 6 依赖 Task 5（计数复算需文件集合已固定）。
- Task 7 依赖 Task 6（门禁需索引已写入）。
- Task 8 依赖 Task 7（评审以队列清空为前置）。
- 无并行：Task 6 的机械复算与 Task 7 的门禁须串行，避免写读冲突。

## 批准门

本规格与任务计划已提交用户审查，**获得显式批准前不进入实施**。批准范围不含：注册开放平台账号、申请个人/管理员实名/企业认证、提交任何资产审核、创建真实应用、生成真实密钥与 token、调用真实 Open API 端点、采集侧栏未声明的 7 篇页面正文、修改同组既有束事实与计数（仅各 1 条互链除外）、执行 git commit/push。实施前须先检查 `projects/awesome-okf-xs/` 子模块无 merge/rebase 进行中。
