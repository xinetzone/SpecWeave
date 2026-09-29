# 知乎打卡工作台（zhihu-checkin-hub）- 产品需求文档

> 方法论链路：七概念场景 5（创新突破）F → V → I → C。本 spec 为 F（第一性原理）与 V（四视角对抗审查）的产出固化。

## Overview

- **Summary**：一个本地单用户 Web 应用，把 `projects/monetize/zhihu-monetization/` 执行工作台从「Markdown 手工台账 + 手工浏览器发布」升级为「每日打卡追踪 + 发布前固定门强制 + 浏览器半自动发布 + 存证自动回写」的闭环工作台。
- **Purpose**：降低每日执行摩擦（定位条目、计数、连续追踪、留痕、截图、勾选），并把「发布前三问自检」从靠自觉变为**不过门不可发布**的软件强制门，保证 F-037 AI 协作排除条款在执行层面真正落地。
- **Target Users**：工作台执行人本人（单用户、本机使用）。

## Goals

- G1：以 `tracker.md` 为唯一勾选事实源，提供今日视图、连续天数（streak）、周计数（回答/想法）聚合与关键时间锚点提醒。
- G2：每日打卡、到账、周核对、中断、自检留痕全部文件化落入 gitignore 的 `local/`，零真实数据入库。
- G3：草稿在应用内撰写（本人撰写），发布前强制过三问门；过门后经 kimi-webbridge 自动填充知乎编辑器，**最终「发布」按钮由本人点击**；应用自动抓取发布链接、截图存证、回写 entry 与 tracker。
- G4：覆盖专栏文章、问题回答、想法三类创作形态；WebBridge 不可用时优雅降级（跳转 + 剪贴板），跟踪与记录功能完全离线可用。
- G5：暖灰纸感、阅读优先的极简界面（无纯黑/高对比深色）。

## Non-Goals

- **不做任何 AI 文本生成/润色/扩写功能**（F-037 红线；应用代码不调用任何 LLM 生成接口）。
- 不自动点击知乎「发布」按钮（human-in-the-loop 不可绕过）。
- 不做收益预估、奖池金额展示、个人收入推算（防画饼纪律；到账照抄页面数字，折算仅标注 F-059 口径）。
- 不做多用户、账号体系、云部署、公网监听、移动端原生应用。
- 不做图片自动上传（知乎编辑器图片插入为人工步骤，向导中显式确认）。
- 不做问题池管理 UI（沿用 `local/content-plan.md`，后续迭代）。
- 不集成知乎开放平台 Access Secret（官方接口无发布能力；只读统计为后续 P2）。
- 不修改 bundle/docs 等只读源；不重述 F 编号口径（界面只链接/转述 tracker.md 既有内容）。

## Background & Context

- 执行工作台现状：7 个入库文件（`tracker.md` 18 行动项当前全未勾选、`records.md` 纯模板、`content-plan.md` 方法模板）+ `local/` 数据隔离区（现仅 README.md）。
- **发布通道事实**：知乎官方开放平台（zhihu-cli v0.6.0 `capabilities` 实测）仅有只读/检索接口与知识库文件上传，**无任何发布专栏文章/回答/想法的写接口** → 唯一可行通道为 kimi-webbridge（本地守护 `http://127.0.0.1:10086/command`）驱动本人已登录的真实浏览器。
- 纪律源（引用不重定义）：勾选纪律（勾选+日期戳、不删条目）、发布前三问自检与边缘场景（主路径 §五）、真实数据写 `local/`、平台数字挂 F 编号。
- 用户决策（2026-09-28 确认）：①代码落 `apps/dev-tools/` 新应用；②发布覆盖文章+回答+想法；③自动填充 + 本人点发布；④文件化存储 + 回写 tracker.md。
- V 对抗审查结论（须在设计中兑现）：
  - 知乎编辑器为 contenteditable 富文本，fill 可能失败 → 能力探测 + 剪贴板/跳转降级 + 回读校验。
  - tracker.md 回写易破坏格式 → 行级最小替换 + 写前备份 + round-trip 测试（真实文件副本 fixture）。
  - WebBridge/登录态依赖链长 → 三态健康检查（daemon/浏览器/登录态），核心记录功能离线可用。
  - 误发到错误问题/想法 → 填充后回读页面标题/URL 与草稿目标比对，一致才进入待发布态。
  - 本地端口风险 → 仅绑 127.0.0.1 + CSRF token + Origin 校验。

## Functional Requirements

- **FR-1（工作区与引导）**：应用可通过配置（应用内 `config.yaml`，可被 `--workspace` / `ZHIHU_CHECKIN_WORKSPACE` 覆盖）定位执行工作台；默认相对路径推算至 `projects/monetize/zhihu-monetization/`；启动校验目标目录含 `tracker.md` 与 `local/`（缺失则引导创建 `local/`，不得写库内其他位置）；路径越界（文件系统根直接子级等）fail-fast。
- **FR-2（tracker 解析与今日视图）**：解析 `tracker.md` 行动项（编号 W1-x/M1-x/O-x/Go-No-Go 等、标题、勾选态、日期戳、所属章节）与「关键时间锚点」表；仪表盘展示今日待办、当前阶段、临近锚点（含相对天数）、条目完成进度。
- **FR-3（每日打卡 entry）**：每日记录写 `local/entries/YYYY-MM-DD.yaml`，字段含：创作条目（类型 文章/回答/想法、字数、链接、关联问题 URL）、互动 5 选 3（关注/评论/赞同/收藏/分享，记类型与对象）、备注；连续天数与中断从 entries 机械计算（不依赖手填）；tracker 条目的勾选按条目验收条件达成时回写（如 W1-2 首日打卡 entry 完整→可勾；W1-5 需连续 7 entry 满→可勾），应用给出「可勾选」提示但勾选动作显式触发。
- **FR-4（发布固定门）**：进入发布流程前必须完成：删稿测试（是/否+说明）、占比自检（是/否+说明）、条款留痕（AI 使用环节三级：检索/编辑/调试，多选登记；无则显式选「无」）、边缘场景登记（结构性使用说明，可空但须主动确认）；任一项未完成，发布 API 返回拒绝、按钮不可用；过门结果写入当日 entry，并可按 `records.md` §五 表形导出到 `local/`（真实数据不写模板文件）。
- **FR-5（草稿管理）**：草稿存 `local/posts/<slug>.md`（YAML frontmatter：类型/标题/目标问题 URL/状态/创建更新时间/发布 URL；正文 Markdown）；应用内提供撰写、列表、状态流转（草稿→待发布→已发布）、字数统计（回答 ≥100、想法 ≥20 字门槛给提示，口径标注 F 编号出处链接）。
- **FR-6（WebBridge 发布桥）**：
  - 6a 健康三态：daemon 探活（10086）、浏览器会话（list_tabs）、知乎登录态（cookie `z_c0` / 页面登录元素）；状态在界面常驻指示。
  - 6b 文章：打开 `https://zhihu.com/write` → 定位标题输入与正文 contenteditable → fill → **回读**标题/正文片段与草稿一致 → 进入「待本人发布」。
  - 6c 回答：打开草稿登记的问题 URL → 触发「写回答」入口 → fill 编辑器 → 回读问题标题与登记 URL 一致。
  - 6d 想法：打开知乎首页想法框 → fill（≥20 字）；图片插入为**显式人工步骤**，向导须等待「图片已插入/无需图片」确认。
  - 6e 降级：任一步定位/fill 失败或三态不满足 → 自动转「打开目标页 + 全文置剪贴板」模式并明确提示，不抛未处理异常。
  - 6f 发布确认：本人在浏览器点发布后，在应用点「我已发布」→ 读取当前 tab URL/DOM 判定成功信号（`/p/数字`、`/answer/数字`、`/pin/数字`）→ screenshot 存 `local/screenshots/YYYY-MM-DD-<type>-<ts>.png` → 回填草稿发布 URL 与状态、补全当日 entry；**应用全程不调用任何点击发布按钮的动作**。
- **FR-7（记录区）**：到账记录（日期/完成动作/盐粒页面显示原文照抄/备注，只增不删可更正留痕）；周核对（回答/想法计数从 entries 自动聚合，周目标 ≥3/≥2 对照，人工确认）；中断登记（日期/天数/原因/恢复日）；周期复盘（周期盐粒合计、折算按 F-059 口径标注「以平台实际规则为准」、对照退出阈值三选一决策）。全部存 `local/` YAML/Markdown。
- **FR-8（时间锚点与提醒）**：解析 tracker §一 锚点表；仪表盘显示下一个关键日期与相对天数；当日打卡未完成（截至本地时间可配置阈值，默认 21:00）在界面提示（不做系统通知，MVP 仅界面内）。
- **FR-9（本地安全）**：服务仅绑 `127.0.0.1`；所有 POST 校验一次性 CSRF token 与 Origin/Referer 为本地；应用不存储、不读取、不展示任何知乎密码/cookie/Access Secret（cookie 存在于用户浏览器，经浏览器扩展通道间接使用）。

## Non-Functional Requirements

- **NFR-1（技术栈）**：Python 3.14（本机 py314 实测可装）；FastAPI + Jinja2 服务端渲染 + uvicorn；原生 CSS（无构建链）+ 极少量原生 JS；YAML 用 PyYAML；HTTP 用标准库/httpx 之一（取依赖少者）。包构建按仓库硬性约定使用 **scikit-build-core 纯 Python 包**（`wheel.packages`、`build-dir`、`minimum-version = "0.9"`）。
- **NFR-2（文件化存储）**：零数据库；所有运行时状态为人类可读 YAML/Markdown/PNG；写入原子化（临时文件 + replace）；tracker.md 写前备份至 `local/backups/`。
- **NFR-3（离线可用）**：WebBridge daemon 停止、未登录、断网时，跟踪/打卡/记录/草稿/勾选功能 100% 可用，仅发布桥相关能力降级并明示。
- **NFR-4（测试）**：关键模块（tracker 解析/回写、门、聚合）覆盖率 ≥90%，整体 ≥80%；tracker 回写测试使用当前真实 `tracker.md` 副本 fixture；WebBridge 客户端用 mock HTTP 测试，不依赖真实浏览器。
- **NFR-5（UI 品质）**：暖灰纸感（暖灰底、米白卡片、深灰褐文字），层级柔和、留白舒适，阅读优先；不使用纯黑背景与高对比深色模式；≥1280px 桌面主场景，窄屏可读不崩坏。
- **NFR-6（性能）**：本地页面 P95 响应 < 300ms（无网络依赖的页面）；启动到可交互 < 3s。
- **NFR-7（仓库卫生）**：运行时产物全部落在 `local/`；应用在该工作台产生的任何文件不得出现在 `git status`（由现有 `.gitignore` 的 `local/*` 规则保证，测试中断言）；代码遵循现有风格与 Conventional Commits 中文提交。

## Constraints

- **Technical**：Windows 本机运行；浏览器通道仅 kimi-webbridge（v1.11.6+，端点 10086，session 名 `zhihu-checkin-hub`）；PowerShell 调用 daemon 的中文编码经验（请求体 UTF-8 落盘 + `--data-binary`）由桥接层内部消化；服务仅本地。
- **Business**：F-037 人类主导红线；固定门口径以主路径 §五 当期版本为准（界面摘引条文并给源链接，不重定义）；规则按期滚动（F-067），应用不硬编码任何平台数字门槛（字数提示从 tracker/content-plan 已登记口径渲染并标注 F 链接）。
- **Dependencies**：kimi-webbridge daemon 与用户浏览器（仅发布桥需要）；执行工作台目录；Python py314 环境。
- **区域**：代码属 `apps/dev-tools/zhihu-checkin-hub/`（主仓库直接管理，新增后登记 apps 路由表与 README）；运行时数据属 `projects/monetize/zhihu-monetization/`（普通目录非 submodule，遵守其 AGENTS.md 读写纪律：可写 tracker.md，真实数据只写 local/）。

## Assumptions

- 用户在发布时本人在场，能完成登录、图片插入、点击发布三个动作。
- kimi-webbridge 的 `fill` 对知乎 contenteditable 编辑器在多数情形可用；失败频次可接受（有剪贴板降级保底），具体成功率在实现期实测并记录。
- tracker.md 条目格式在本应用生命周期内保持「`- [ ] **编号 标题**：…｜日期戳：____｜`」族形态；格式漂移时解析器 fail-fast 提示手工处理而非静默错解析。
- 一台机器、一个工作台、一个本地用户；无并发写入（单进程 + 文件锁防双开）。

## Acceptance Criteria

### AC-1：tracker.md 真实文件完整解析
- **Type**：`rule`
- **Given**：仓库当前真实的 `projects/monetize/zhihu-monetization/tracker.md`
- **When**：解析器加载该文件
- **Then**：全部行动项（W1/M1/Go-No-Go/收官/持续期/复核锚点）被解析，编号、勾选态、日期戳、所属章节正确；关键时间锚点表行被解析为日期-事件-依据结构
- **Pass Condition**：测试断言解析出的未勾选条目数与文件实际一致、锚点表条目数一致（快照 fixture）
- **Evidence**：pytest 用例 `test_tracker_parse_real_fixture`

### AC-2：tracker.md 回写安全且幂等
- **Type**：`rule`
- **Given**：真实 tracker.md 的临时副本
- **When**：对指定条目执行勾选（日期 2026-09-28），再重复执行一次，再勾选另一条目
- **Then**：仅目标行的复选框与日期戳变化；frontmatter、其他行、其他条目的字节完全不变；重复勾选幂等（无第二个日期戳）；备份写入 `local/backups/`；未勾选态→已勾选的替换符合 `[x] 2026-09-28` 形态
- **Pass Condition**：diff 只剩预期行；round-trip 再解析状态正确
- **Evidence**：pytest 字节级 diff 断言

### AC-3：固定门不过不可发布
- **Type**：`rule`
- **Given**：一篇草稿，三问任一项未完成或任一「是/否」为「否」
- **When**：调用发布启动接口 / 点击发布按钮
- **Then**：服务端返回拒绝（422/409 语义），不产生任何 WebBridge navigate/fill 副作用；门记录不生成
- **Pass Condition**：四项全绿才放行；服务端与 UI 双重拦截，测试覆盖全部分支
- **Evidence**：pytest `test_gate_blocks_publish*`

### AC-4：发布桥三态降级不崩溃
- **Type**：`rule`
- **Given**：daemon 未启动 / 浏览器无会话 / 知乎未登录 / fill 选择器找不到 四种情形
- **When**：启动发布流程
- **Then**：分别给出明确中文状态与指引，自动或一键转入「打开页面+剪贴板」降级；无未捕获异常、无半成品勾选/存证
- **Pass Condition**：mock 四情形测试通过；真实未登录环境手工冒烟通过
- **Evidence**：pytest + 冒烟记录（review 期）

### AC-5：发布确认后自动存证回填
- **Type**：`rule`
- **Given**：填充完成且本人已在浏览器发布
- **When**：用户点「我已发布」
- **Then**：应用读到成功 URL 信号（/p/、/answer/、/pin/ 之一），截图落 `local/screenshots/`（PNG 存在且 >10KB），草稿 frontmatter 与当日 entry 写入发布 URL、时间、类型
- **Pass Condition**：三类型各有测试（URL 判定正则 + 文件写入）；真实文章流程至少 1 次手工冒烟
- **Evidence**：pytest + 冒烟截图文件

### AC-6：真实数据零入库
- **Type**：`rule`
- **Given**：应用完成若干打卡/草稿/到账/截图/发布操作
- **When**：在仓库根执行 `git status --porcelain`
- **Then**：除应用代码目录与预期入库文件外，`projects/monetize/zhihu-monetization/local/` 下无任何文件出现为未跟踪/修改
- **Pass Condition**：所有运行时写入路径断言位于 `local/` 之内；git status 验证 clean（local 范围）
- **Evidence**：集成测试 + git status 输出

### AC-7：连续与周聚合机械正确
- **Type**：`rule`
- **Given**：一组构造的 entries（含连续段、1 天中断、3 天中断、类型混合）
- **When**：计算 streak、各周回答/想法计数
- **Then**：streak 与手算一致；中断 ≥3 天触发「复核锚点」提示（对齐 tracker 顶部说明）；周计数与 entries 明细一致
- **Pass Condition**：构造用例断言通过
- **Evidence**：pytest

### AC-8：零 AI 生成与零凭证
- **Type**：`rule`
- **Given**：应用全部源码与依赖声明
- **When**：静态审计（依赖清单 + 调用点 grep/import 审计）
- **Then**：不存在 LLM/生成式 API 调用（zhihu-cli answer、openai 类 SDK、chat completions 等）；不存在 cookie/密码/secret 读写代码；剪贴板内容仅来自用户本人草稿正文
- **Pass Condition**：审计清单逐项有证据
- **Evidence**：测试用例静态扫描 + 依赖表评审

### AC-9：暖灰纸感阅读优先界面
- **Type**：`rubric`
- **Dimension**：视觉与信息设计契合度（暖灰纸感、阅读优先、层级柔和、留白舒适、无纯黑/高对比深色）
- **Scale**：1-5
- **Anchors**：1 = 通用 Bootstrap 感/高对比或纯白刺眼；3 = 配色中性但层次普通；5 = Notion/Obsidian 文档工作台质感，暖灰底+米白卡片+深灰褐文字，长时阅读舒适
- **Pass Threshold**：>= 4
- **Evidence**：仪表盘/打卡/编辑器/发布向导四页面截图，评审打分

### AC-10：离线核心可用
- **Type**：`rule`
- **Given**：关闭 webbridge daemon 并断网
- **When**：完成查看今日、写 entry、勾选 tracker、记到账、写草稿全套操作
- **Then**：全部成功且数据落盘正确；界面发布入口显示降级态而非错误页
- **Pass Condition**：手工冒烟通过
- **Evidence**：冒烟记录

### AC-11：工作区路径守卫
- **Type**：`rule`
- **Given**：workspace 指向不存在目录、指向文件系统根直接子级、指向无 tracker.md 的目录、指向合法工作台 四种输入
- **When**：应用启动校验
- **Then**：前三种 fail-fast 并给中文指引；第四种正常加载
- **Pass Condition**：四分支测试通过
- **Evidence**：pytest

### AC-12：本地服务安全
- **Type**：`rule`
- **Given**：服务运行于 127.0.0.1
- **When**：用外部 Origin 头、无 CSRF token、错误 token 发起 POST
- **Then**：一律拒绝（403）；绑定地址断言非 0.0.0.0；正常同源带 token 请求成功
- **Pass Condition**：测试覆盖三类拒绝
- **Evidence**：pytest

### AC-13：真实浏览器文章发布冒烟
- **Type**：`rubric`
- **Dimension**：文章发布桥端到端顺滑度（登录态识别→填充准确→回读一致→降级提示清晰→确认存证闭环）
- **Scale**：1-5
- **Anchors**：1 = 填充失败且无有效指引；3 = 主流程可用但需 ≥2 次人工补救；5 = 一次通过，仅人工点发布与插图
- **Pass Threshold**：>= 3（受第三方页面 DOM 制约，3 为可接受底线；失败路径必须有降级保底，保底由 AC-4 兜底）
- **Evidence**：用户在场时真实冒烟记录（可能在 Implement 后期执行；若环境不具备则 Review 标 blocked 并以 AC-4 mock 证据临时收口，冒烟转后续手动项）

## Open Questions

- [ ] 主攻领域（数码/教育）待用户确认——影响问题池但**不影响本应用**（问题池非 MVP），无需阻塞。
- [ ] 真实冒烟依赖用户本人在浏览器登录知乎；时间由用户指定。
