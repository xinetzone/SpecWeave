# 知乎打卡工作台（zhihu-checkin-hub）- 实施计划

> 任务为依赖有序的垂直切片；每个 Task 至少含一条 TR。代码根：`apps/dev-tools/zhihu-checkin-hub/`；运行时数据根：`projects/monetize/zhihu-monetization/`。

## Task 1: 应用骨架、配置与工作区守卫
- **Status**: `completed`
- **Completion Evidence**:
  - TR-1.1：`tests/test_config_paths.py` 14 用例全过（合法/不存在/非目录/无 tracker/根级守卫/越界/配置优先级/非本地 host）。
  - TR-1.2：scikit-build-core wheel 构建验证（见 build/test-wheel）；CLI help 输出 serve/check 两子命令。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 按仓库约定建 scikit-build-core 纯 Python 包：`pyproject.toml`（`requires=["scikit-build-core>=0.9"]`、build-backend、`[tool.scikit-build]` 的 `wheel.packages=["src/zhihu_checkin_hub"]`、`build-dir="build/{wheel_tag}"`、`minimum-version="0.9"`，无 cmake 段）；包目录 `src/zhihu_checkin_hub/`（`__init__.py`/`__main__.py`）、tests/、README.md。
  - `config.py`：dataclass 配置（workspace 路径、webbridge endpoint `http://127.0.0.1:10086/command`、session 名 `zhihu-checkin-hub`、每日提醒时刻 21:00）；优先级 CLI `--workspace` > 环境变量 `ZHIHU_CHECKIN_WORKSPACE` > 应用内 `config.yaml` > 默认相对路径推算。
  - `cli.py`（typer）：`serve`（启动 Web）、`check`（校验工作区与桥接健康并打印中文报告）两个子命令。
  - 工作区守卫：解析后路径须落在非根级、目录存在且含 `tracker.md`；`local/` 缺失时可自动创建；非法情形 fail-fast 中文指引。
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `rule` TR-1.1: 四种 workspace 输入（不存在/根直接子级/无 tracker.md/合法）行为分别为中文报错或正常加载；pytest 全通过。
  - `rule` TR-1.2: `pip install`（或 `python -m build`）在 py314 环境成功产出 wheel；`python -m zhihu_checkin_hub --help` 可见两子命令。
- **Notes**: 参考 `apps/dev-tools/wechat-mp-archiver/pyproject.toml` 的 scikit-build-core 写法。

## Task 2: tracker.md 解析器
- **Status**: `completed`
- **Completion Evidence**:
  - TR-2.1：真实 fixture 断言 18 个行动项编号集合（W1×8 含 GONOGO/CLOSE、M1×6、O-6、MONTHLY-CHECK、REVIEW×2）、7 行锚点表、章节归属全对。
  - TR-2.2：已勾选+日期戳、放弃/降频、畸形行、未知编号、重复 ID 分支用例全过。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `storage/tracker.py`：解析 frontmatter（保留原文字节供回写）、§一 关键时间锚点表（日期/事件/依据）、各章节行动项（编号正则覆盖 `W1-\d+`/`M1-\d+`/`O-\d+`/「科学季报名 Go/No-Go」/「9.30 收官」/持续期/复核锚点族；复选态；日期戳空或值；标题；所属章节；验收链接保留）。
  - 模型放 `models.py`（dataclass，frozen 解析模型）。
  - 格式漂移（行不符合已知形态）时抛带行号的受控异常，不静默丢弃。
  - tests/fixtures/tracker.md 为当前真实 tracker.md 的副本。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-2.1: 真实 fixture 解析断言：未勾选条目数与实际一致、编号集合一致、锚点表行一致（快照）。
  - `rule` TR-2.2: 构造的「已勾选+日期戳」「放弃/降频」行解析正确；畸形行抛受控异常。

## Task 3: tracker.md 安全回写器
- **Status**: `completed`
- **Completion Evidence**:
  - TR-3.1：真实副本勾选 W1-1/M1-1（含重复幂等），逐行断言仅目标行变化、标记 `[x] 2026-09-28`、日期戳同步、备份落 local/backups/、round-trip 计数=2。
  - TR-3.2：未知条目文件字节不变并抛受控错误；备份文件等于原始字节。累计 24 用例全过。
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `check_off(item_id, date)`：行级最小替换（仅目标行 `- [ ]` → `- [x] YYYY-MM-DD`，日期戳占位 `____` 同步）；重复勾选幂等；不支持「取消勾选」（勾选纪律不删条目标识，放弃走备注，不在 MVP）。
  - 写前把原文件复制到 `local/backups/tracker-<ts>.md`；原子写（同目录临时文件 + os.replace）。
  - 回写后重新解析校验目标状态并返回 diff 行数。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-3.1: 真实副本上勾选两条目（含重复一次）：除预期行外字节级不变（精确 diff 断言）；备份文件存在；round-trip 状态正确。
  - `rule` TR-3.2: 目标条目不存在 / 已勾选不同日期：行为明确（受控错误或幂等返回），文件不变。

## Task 4: local 文件存储层
- **Status**: `completed`
- **Completion Evidence**:
  - TR-4：entries（YAML round-trip、合格门槛 100/20 字+3 互动、排序、gate blob）、drafts（frontmatter round-trip、slug 防穿越、draft→ready→published 单向）、records（盐粒整数校验+corrections 追加、weekly upsert、中断、复核 F-059 折算标注）全部用例通过；所有写入路径断言位于 local/ 内。累计 35 用例全过。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 目录布局：`local/entries/YYYY-MM-DD.yaml`、`local/posts/<slug>.md`、`local/screenshots/`、`local/backups/`、`local/records/earnings.yaml`、`local/records/weekly.yaml`、`local/records/interruptions.yaml`、`local/records/reviews.yaml`。
  - `storage/entries.py`：当日 entry dataclass 读写（创作条目列表：类型/字数/URL/问题 URL；互动 5 选 3；备注）；YAML 人类可读，原子写，缺失即默认空模板。
  - `storage/drafts.py`：Markdown + YAML frontmatter 草稿 CRUD 与状态机（draft→ready→published）；slug 安全化。
  - `storage/records.py`：到账记录只增可更正（更正保留留痕字段）、周核对、中断、复盘表。
  - 全部写入路径断言位于 workspace `local/` 之内（越界即异常）。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 临时 workspace 中完成 entry/草稿/四类记录读写，文件均落在 `local/` 对应路径，YAML/frontmatter 可被重复解析（幂等往返）。
  - `rule` TR-4.2: 所有写入 API 对路径越界（`..` 逃逸 slug 等）抛受控异常。

## Task 5: 领域聚合（streak / 周计数 / 锚点提醒）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-5.1：连续段/今天宽限/断 1 天/断 3 天复核提示/周目标 3 回答+2 想法（含 W2 空周）/W1-2 与 W1-5 缺口判定全部手算对拍通过。
  - TR-5.2：注入时钟 2026-09-28，下一锚点为 9.29 Go/No-Go、相对 1 天；章节进度 二、=(0,8)。累计 42 用例全过。
- **Priority**: high
- **Depends On**: Task 2, Task 4
- **Description**:
  - `domain/streak.py`：从 entries 机械计算当前连续打卡天数（当日/昨日口径）、最长连续、断档日期；中断 ≥3 天返回「先回 tracker 复核锚点再恢复」提示。
  - 周聚合：自然周/执行周（W1 起跑可配，默认 2026-09-25）回答 ≥3、想法 ≥2 对照 M1-2/M1-3。
  - 锚点：tracker §一 表按当前日期输出下一个关键锚点与相对天数；条目完成进度（勾选/总数，分章节）。
  - tracker「可勾选」判定：W1-2（首日 entry 含 ≥100 字创作 + 3 互动）、W1-5（连续 7 个合格 entry）等映射为纯函数规则，返回可勾/不可勾+缺口说明；不自动勾选。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-5.1: 构造 entries 场景（连续段/中断 1 天/中断 3 天/类型混合/缺互动）断言 streak、周计数、可勾选判定与手算一致。
  - `rule` TR-5.2: 锚点表在固定「今天」（注入时钟 2026-09-28）输出正确的下一锚点（9.29 Go/No-Go）与相对天数。

## Task 6: 发布前固定门服务
- **Status**: `completed`
- **Completion Evidence**:
  - TR-6：四项全绿放行并写当日 entry gates + 导出 gate-exports Markdown；任一否/缺说明/「无」与三级冲突均拒绝且零写入；过门留痕按次追加。累计 45 用例全过。
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - `domain/gate.py`：门输入（删稿测试 bool+说明、占比自检 bool+说明、条款留痕三级多选+「无」显式项、边缘场景确认/说明）；四项全绿才放行；任一「否」即拒绝；产出 GateResult 并序列化进当日 entry（含时间戳）。
  - 门文案为源文摘引（删稿测试/占比自检/条款留痕/边缘场景原文），代码常量中标注源链接（主路径 §五），不重写口径。
  - 提供「导出为 records §五 表形 Markdown 到 local」能力。
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-6.1: 全分支表驱动测试：缺项/否/未确认边缘场景→拒绝；全绿→通过且留痕结构完整；重复过门记历史不覆盖。
  - `rule` TR-6.2: 导出的 Markdown 表列与 records.md §五 一致且写入 `local/`。

## Task 7: WebBridge 客户端与三态健康检查
- **Status**: `completed`
- **Completion Evidence**:
  - TR-7：请求信封（顶层 session/args）全 action 覆盖；传输异常、success:false、error 负载均归一为 BridgeError；注入假 transport 验证 READY/DAEMON_DOWN/BROWSER_DISCONNECTED/LOGGED_OUT 四态。累计 52 用例全过。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `publishing/bridge.py`：对 `127.0.0.1:10086/command` 的 JSON POST 客户端（顶层 session；请求 UTF-8 编码内部消化）；封装 navigate/find_tab/snapshot/click/fill/evaluate/screenshot/list_tabs。
  - 三态健康：daemon（HTTP 可达）、浏览器会话（list_tabs 成功）、知乎登录态（在 zhihu.com 页 evaluate 读 `z_c0` cookie，兼容页面登录元素判据）；返回三态枚举与中文指引。
  - 超时/连接拒绝/JSON 错误归一为受控结果类型（不向外抛传输异常）。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-7.1: mock HTTP 层测试：daemon down/会话失败/未登录/已登录四态判定与指引正确；命令 JSON 结构（args 闭合、session 顶层）正确。
  - `rule` TR-7.2: screenshot 命令能按返回 path 把文件登记/移动到 workspace `local/screenshots/`（mock 返回虚拟路径场景用临时替身）。

## Task 8: 发布编排器（三类型填充 / 回读 / 降级 / 确认存证）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-8：文章（标题+正文回读）、回答（问题 URL+写回答入口+回读）、想法（≥20 字门槛）三条 happy path 到确认存证（URL 信号 /p//answer//pin/、截图入 local/screenshots、草稿 published、entry 回填）；错误 URL 阻断且零副作用；选择器全败降级（目标页+剪贴板+中文指引）；源码静态断言不含 client.click 与最终发布按钮文本。累计 90 用例全过。
- **Priority**: high
- **Depends On**: Task 6, Task 7
- **Description**:
  - `publishing/publisher.py` 状态机：`idle → gate_passed → filled → awaiting_human → confirmed`（任何阶段失败 → `degraded`）。
  - 文章：navigate `/write` → 选择器定位标题/正文（选择器集合 + snapshot 兜底）→ fill → evaluate 回读做一致性包含校验。
  - 回答：navigate 草稿问题 URL → 触发「写回答/添加回答」→ fill → 回读问题标题与 URL 双重比对，防误发。
  - 想法：fill 想法框（≥20 字校验）→ 等待「图片已插入/无需图片」显式确认。
  - 降级：定位/fill 失败 → 打开目标页 + 正文（及标题）写系统剪贴板 + 中文指引；degraded 不产生勾选/存证。
  - 确认：`confirm()` 读当前 tab URL，正则 `/p/(?P<id>\d+)`、`/answer/\d+`、`/pin/\d+` 判定成功；成功后 screenshot 存证、更新草稿状态/发布 URL、补全当日 entry 创作条目。
  - **硬约束**：代码中不得存在任何对「发布」按钮的 click 调用；静态测试守护。
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-8
- **Test Requirements**:
  - `rule` TR-8.1: mock bridge 表驱动测试三类型 happy path（填充→回读一致→等待→确认 URL→截图与 entry 断言）。
  - `rule` TR-8.2: 四失败情形（未登录/选择器缺失/回读不一致/确认时 URL 无信号）均安全转 degraded 或受控错误，无半成品写入。
  - `rule` TR-8.3: 静态扫描断言 publisher 代码无发布按钮点击语义（点击目标白名单：仅「写回答」等编辑入口）。

## Task 9: Web 框架、安全与应用装配
- **Status**: `completed`
- **Completion Evidence**:
  - TR-9.1：`web/security.py` CSRF 双提交令牌（cookie `zhihu_checkin_csrf` + 字段 `_csrf`，`secrets.compare_digest`），无 cookie/错 token POST 拒（403）；Origin 存在时非本地拒绝、无 Origin 时回退 Referer 白名单（单测表驱动）。
  - TR-9.2：`config.load_config` 只允许 127.0.0.1/localhost/::1；`SingleInstanceLock` 对 `local/.serve.lock` 加字节区间锁（Windows msvcrt / POSIX fcntl），真实子进程持锁时第二实例获 `WorkspaceError` 中文提示；release 后可重获、幂等。
- **Priority**: high
- **Depends On**: Task 5, Task 6, Task 8
- **Description**:
  - `web/app.py`：FastAPI factory（Jinja2Templates、静态资源、服务依赖注入 workspace）；uvicorn 仅绑 `127.0.0.1:<port>`（端口可配，默认 17253）。
  - `web/security.py`：每会话一次性 CSRF token（模板注入、POST 校验）；Origin/Referer 白名单（127.0.0.1/localhost 本地端口）；非浏览器 GET 不限、POST 强校验。
  - 单进程文件锁防双开（workspace 内锁文件，随进程释放）。
- **Acceptance Criteria Addressed**: AC-12
- **Test Requirements**:
  - `rule` TR-9.1: TestClient 用例：无 token/错 token/外部 Origin 的 POST 返回 403；正常同源带 token POST 成功。
  - `rule` TR-9.2: 配置断言监听 host 为 127.0.0.1（启动参数单测）；双开第二次给出中文提示并退出。

## Task 10: 核心页面（仪表盘 / 打卡 / 记录 / 草稿）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-10.1：六模板（base/dashboard/checkin/records/drafts/draft_edit）TestClient 全 200，关键字段（今日日期、W1-1 等条目、门入口、idle 健康态）渲染；打卡 POST 端到端落 `local/entries/2026-09-28.yaml` 且 tracker 勾选回写为 `- [x] 2026-09-28`（test_web.py）。
  - TR-10.2 自评 **4/5**：Edge headless（1360 宽）对 /、/checkin、/records、/drafts、/publish 五页整页截图——暖灰纸感（--bg #f3efe7/米白卡片/深褐文字，无纯黑）、层级清晰、无错位溢出、零第三方 CDN；自评中发现并修复两处缺陷：① 仪表盘勾选提示标题重复携带编号（streak `_short_title` 去前缀，补单测）② 互动双字标签被挤压换行（`.gate-item label{white-space:nowrap}`）。未达 5 分：空状态页（无草稿时发布向导）信息密度偏低，留待真实使用迭代。
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 仪表盘：今日打卡卡片（创作 1+互动 3 完成态）、streak、本周回答/想法计数、下一锚点、条目进度、三态健康指示；数据全来自前述服务。
  - 打卡页：当日 entry 表单（类型选择、字数、链接、互动 5 选 3）；tracker 条目列表（章节分组、可勾条目显「勾选+日期」按钮接回写器，幂等按钮态）。
  - 记录页：到账表（照抄录入）、周核对（自动聚合+人工确认）、中断登记、周期复盘（F-059 口径标注原文链接、退出阈值三选一）。
  - 草稿页：列表（状态徽章）+ Markdown 编辑器（textarea + 预览 toggle + 字数与门槛提示）。
  - `static/styles.css`：暖灰纸感体系（暖灰底/米白卡片/深灰褐文字/柔边框/舒适留白），无纯黑深色；无第三方 CSS/JS CDN（零外网依赖）。
- **Acceptance Criteria Addressed**: AC-9, AC-10
- **Test Requirements**:
  - `rule` TR-10.1: 各页面 TestClient 200 且关键字段渲染（今日日期、条目编号、门入口、健康态）；打卡提交后 entry 落盘、勾选后 tracker 副本变化（端到端临时 workspace）。
  - `rubric` TR-10.2: 视觉契合度（AC-9 同维）；scale 1-5；anchors 1 通用模板感/3 中性普通/5 Notion 级纸感；threshold >= 4；evidence = 四页面浏览器截图自评分与理由。

## Task 11: 发布向导页面（门 → 健康 → 填充 → 等待 → 存证）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-11.1：ScriptedBridge 下端到端走通 选 ready 草稿→四问门全绿（303）→填充回读→`awaiting_human`→「我已发布」按 `/p/123456` 信号确认（303），草稿转 published、截图登记、当日 entry 回填；门缺项/边缘未确认返回 422；未过门直接 POST /publish/fill 返回 409。
  - TR-11.2：全部选择器失败时 fill 返回 degraded：页面给「打开目标页 + 正文入剪贴板 + 本人手动发布」中文指引，草稿不转态、无 entry 回填；publish.html 全程显著标注「不含 AI 生成、最终发布按钮永远由你本人点击」。
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 向导四步：① 选草稿 → ② 固定门表单（四项不全绿按钮禁用，服务端二次校验）→ ③ 健康三态与「开始填充」（失败直接展示降级按钮：打开页面+复制草稿）→ ④ 填充完成后展示「请在浏览器中本人点击发布；图片请手动插入」等待页 +「我已发布」按钮 → 成功页（发布 URL + 截图缩略图 + entry/勾选提示）。
  - 想法类型的「图片已插入/无需图片」确认控件；回答类型展示目标问题标题与 URL 供肉眼复核。
  - 全程显著声明「内容须本人撰写、应用不含 AI 生成」。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-13
- **Test Requirements**:
  - `rule` TR-11.1: TestClient 走完门拒绝→全绿→mock 填充→mock 确认 的状态机；跳过门直接调填充接口返回 4xx。
  - `rule` TR-11.2: degraded 路径页面正确给出剪贴板/打开指引，且无 entry 回填。

## Task 12: 静态审计、覆盖率与离线冒烟
- **Status**: `completed`
- **Completion Evidence**:
  - TR-12.1：`tests/test_audit.py`（6 用例）AST/正则扫描 `src/` 与模板——无 openai/anthropic/chat-completions/LLM 域名、无 document.cookie/z_c0/password/getpass/Access Secret、无 `client.click(`、无知乎发布 CLI subprocess；pyproject 依赖逐项落在白名单（fastapi/uvicorn/jinja2/typer/pyyaml/httpx/python-multipart），构建后端 scikit-build-core。
  - TR-12.2：`pytest --cov` 全 143 用例通过（review 后由 139 增补 4 项 P1 回归 + 1 项 CRLF 回归）；整体覆盖率 92%，关键模块 tracker 96% / gate 97% / streak 98% / publisher 100% / cli 100%（均 ≥90%，整体 ≥80%）。离线冒烟：tmp 副本完成 entry/earning/draft/checkoff 全写入且 Web 页面 200；桥指向关闭端口稳定返回 `daemon_down` 不抛原始异常。
  - TR-12.3：`git -C <仓库根> status --porcelain` 过滤 `projects/monetize/zhihu-monetization/local/` 条目数为 0（测试内真实执行，非跳过；手工复跑同为 0）。注：`tests/fixtures/tracker.md` 为真实 tracker 原样复制，其相对链接在夹具位置必然失效（54 条），属测试语料非文档，check-links 仅对 README 单文件校验通过。
- **Priority**: medium
- **Depends On**: Task 11
- **Description**:
  - `tests/test_audit.py`：扫描源码 import/字符串，断言无 LLM 生成端点/SDK（openai、chat/completions、zhihu-cli answer 调用等）、无 cookie/secret 持久化代码；依赖清单评审记录。
  - 覆盖率：关键模块（tracker/gate/streak/publisher）≥90%，整体 ≥80%（pytest --cov 配置）。
  - 离线冒烟：daemon 关闭条件下跑打卡/记录/草稿/勾选全流程测试。
  - 入库卫生：在临时副本完成全套真实写入后，于仓库根执行 `git status --porcelain`，断言 `projects/monetize/zhihu-monetization/local/` 下零条目出现（AC-6 收尾证据）。
- **Acceptance Criteria Addressed**: AC-6, AC-8, AC-10
- **Test Requirements**:
  - `rule` TR-12.1: 审计测试通过且依赖白名单（fastapi/uvicorn/jinja2/pyyaml/typer/httpx 或等价最小集）逐项说明。
  - `rule` TR-12.2: 覆盖率达标输出；离线冒烟脚本/步骤与结果入完成证据。
  - `rule` TR-12.3: 全套写入后 `git status --porcelain` 中 local/ 范围为空（允许代码目录变更），输出入完成证据。

## Task 13: README 与 apps 区域登记
- **Status**: `completed`
- **Completion Evidence**:
  - TR-13.1：`apps/dev-tools/zhihu-checkin-hub/README.md` 覆盖定位/py314 安装/`zhihu-checkin serve|check` 用法/工作区定位顺序/local 数据边界/webbridge 前置/无 AI·无凭证·仅本地安全边界/F-037 声明；命令与 `--help` 输出逐项核对一致（serve/check、-w/--workspace、--host、-p/--port）。
  - 路由登记：`apps/AGENTS.md` 应用路由表与边界声明各加一行；`apps/README.md` dev-tools 清单补 zhihu-checkin-hub（同时补齐漏登的 wechat-mp-archiver、计数更正为 5）；对 README.md / apps/README.md / apps/AGENTS.md 运行 `.agents/scripts/check-links.py` 全部通过。
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 应用 README：定位、安装（py314）、`zhihu-checkin serve/check` 用法、工作区与 local 边界、发布桥前置（webbridge daemon + 浏览器登录）、安全边界（无 AI/无凭证/仅本地）、F-037 合规声明。
  - 更新 `apps/AGENTS.md` 应用路由表与 `apps/README.md`（如该文件维护应用清单）登记新应用一行；不新增 AGENTS.md（简单应用遵循根规范）。
- **Acceptance Criteria Addressed**: 无新增 AC（治理任务；支撑 NFR-7）
- **Test Requirements**:
  - `rule` TR-13.1: README 中命令与实际 CLI help 一致（人工核对截图/输出）；路由表条目链接相对路径有效（运行仓库 check-links 脚本对变更目录）。

## Task 14: 真实浏览器冒烟（需用户在场登录知乎）
- **Status**: `blocked`（用户不在场；按本条 Notes 与 spec AC-13 规则处理）
- **Completion Evidence**:
  - 2026-09-28 收口审查（review.md 第二节/第七节）：AC-13 标 blocked，以 AC-4 完整 mock 证据（143 项测试、publisher 100% 覆盖）+ 真实关闭端口 daemon_down 探测临时收口；未伪造真实冒烟。
  - 手动执行清单见 review.md「Task 14 后续手动项」4 步（webbridge daemon + 登录知乎 → 三类型填充含问题 ID 阻断/想法图片确认 → 至少一次「我已发布」闭环核验截图 >10KB 与 entry 回填 → 补 AC-13 评分 ≥3 并复核 local/ 零入库）。用户在场时随时可执行。
- **Priority**: medium
- **Depends On**: Task 11
- **Description**:
  - 用户指定时间：确保 webbridge daemon 运行、用户在浏览器登录知乎；依次做 ① 文章草稿（测试文案，可发私密/不发布亦可，至少走到填充回读）② 回答填充到一个用户自选问题 ③ 想法填充（含图片确认控件）④ 至少完成一次「我已发布」完整闭环并验证截图与 entry 回填。
  - 记录选择器漂移点并修补；无法当日解决的登记 issue。
- **Acceptance Criteria Addressed**: AC-4（真实部分）, AC-13
- **Test Requirements**:
  - `rule` TR-14.1: 三类型填充均有真实执行记录（成功或已登记缺陷 issue）；至少 1 条端到端发布闭环证据（URL + 截图文件）。
  - `rubric` TR-14.2: AC-13 同维顺滑度；scale 1-5；threshold >= 3；evidence = 冒烟记录与截图。
- **Notes**: 若实施期用户无法在场，本项保持 pending 并在 Review 时按 AC-13 约定处理（blocked，以 AC-4 mock 证据临时收口，冒烟列为交付后手动项），不得因此阻塞代码交付。
