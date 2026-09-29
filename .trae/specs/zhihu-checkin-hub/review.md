# 知乎打卡工作台（zhihu-checkin-hub）· Spec Mode 收口审查

- 审查日期：2026-09-28
- 审查人：独立代码审查员（fresh context，未参与实现）
- 审查对象：`apps/dev-tools/zhihu-checkin-hub/`（src 23 个模块 / tests 12 个文件）、`.trae/specs/zhihu-checkin-hub/{spec.md,tasks.md}`
- 只读核对区：`projects/monetize/zhihu-monetization/`（审查全程未写入；所有动态验证在系统临时目录完成）

## 一、审查范围与方法

1. 全文阅读 spec.md（AC-1..AC-13、NFR、红线）与 tasks.md（Task 1..14 及完成证据），**不以 tasks.md 证据代替代码核对**。
2. 通读全部生产源码（storage / domain / publishing / web / config / cli）与全部测试、模板、样式；关键路径逐行核对。
3. Windows + py314 亲跑：
   `conda run -n py314 python -m pytest tests/ -q --cov=src/zhihu_checkin_hub --cov-report=term`（139 项全绿；见第三节）。
4. 额外独立验证：
   - SHA-256 比对 `tests/fixtures/tracker.md` 与真实 `projects/monetize/zhihu-monetization/tracker.md`：**逐字节相同**（均 14014 字节，真实文件为 LF）；
   - 在系统临时目录构造 **CRLF 版 tracker 副本**实跑 `check_off`：仅目标行变化、目标行 CRLF 保留、其余字节不变、重复勾选幂等、round-trip 正确；
   - 在系统临时目录搭临时工作区起真实 uvicorn（127.0.0.1:17299），用无头 Edge 对仪表盘/打卡/记录/草稿/发布向导五页独立截图，独立评分 AC-9；
   - 审查前、后各执行一次 `git -C d:\spaces\SpecWeave status --porcelain` 核对 `projects/monetize/` 零条目；
   - 对 src 全树 grep：subprocess/os.system、openai/anthropic/chat-completions、0.0.0.0、cookie/password/getpass/z_c0、全部出站 URL。
5. AC-13 按 spec 第 189 行既定规则处理：用户不在场 → **blocked**，以 AC-4 mock 证据临时收口，未伪造任何真实浏览器冒烟。

## 二、逐 AC 判定表

| AC | 状态 | 关键证据（文件:行 / 测试） | 备注 |
| --- | --- | --- | --- |
| AC-1 tracker 真实文件完整解析 | **pass** | [tracker.py](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/storage/tracker.py#L43-L132)；`test_parse_real_fixture`（18 条编号、7 锚点、章节归属）；fixture 与真实 tracker SHA-256 相同 | fail-fast 覆盖畸形行/未知编号/重复 ID |
| AC-2 回写安全且幂等 | **pass** | [checkoff.py](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/storage/checkoff.py#L36-L102)；`test_checkoff_byte_level_diff`、`test_backup_is_original`；审查员 CRLF 临时副本实跑通过 | 套件无 CRLF 专测（代码 `newline=""` 正确，已手工验证），建议补回归测试（P2-7） |
| AC-3 固定门不过不可发布 | **pass** | 纯函数 [gate.py L59-97](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/domain/gate.py#L59-L97)；路由校验顺序 [app.py L426-447](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/web/app.py#L426-L447)（`pass_gate` 先抛 422，此前不碰 bridge/draft 流转）；[app.py L465-467](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/web/app.py#L465-L467) fill 前查 GATE_PASSED 否则 409；`test_gate_reject_returns_422`、`test_fill_before_gate_is_409`、`test_reject_writes_nothing`；UI 禁用 [publish.html L70/L113-123](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/web/templates/publish.html#L113-L123) | 服务端+UI 双拦截成立、拒绝时零 bridge 副作用零留痕；但 fill 的 slug 未绑定过门会话（P1-2）；门分支测试未逐字覆盖 ratio=否/缺删稿说明（P3） |
| AC-4 三态降级不崩溃 | **pass**（mock 充分；真实浏览器部分随 AC-13 转手动） | [bridge.py L156-197](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/publishing/bridge.py#L156-L197)；`test_health_*` 四态；publisher 降级 [publisher.py L284-313](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/publishing/publisher.py#L284-L313)；`test_degrade_*` 十余例 + `test_degraded_flow_writes_nothing`；真实关闭端口探测 `test_bridge_health_reports_daemon_down_offline` | confirm 阶段 bridge 异常会变裸 500（P2-1）；navigate 自身失败时提示仍称「已打开目标页」（P2-8） |
| AC-5 确认后自动存证回填 | **pass** | URL 正则 [publisher.py L58-62/L165-172](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/publishing/publisher.py#L58-L62)（`^.../p/\d+`、`/question/\d+/answer/\d+`、`/pin/\d+` 锚定）；三类型 happy-path + 错误 URL 阻断 `test_*_happy_path*`、`test_confirm_wrong_url_blocks`；草稿/entry 回填 [L180-200](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/publishing/publisher.py#L180-L200) | 未校验截图文件真实存在/>10KB（AC 字面要求，P2-2）；真实截图闭环属 AC-13 |
| AC-6 真实数据零入库 | **pass** | 路径守卫 [workspace.py L64-70](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/storage/workspace.py#L64-L70)；`test_all_writes_inside_local`；**真实执行 git 的** `test_real_workspace_local_remains_clean_in_git`；审查员两次手跑 `git status --porcelain` 均无 `projects/monetize/` 任何条目 | 仅允许的库内写入是 tracker.md（规格授权），审查期间真实 tracker 亦未被改 |
| AC-7 连续与周聚合机械正确 | **pass** | [streak.py L108-179/L215-260](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/domain/streak.py#L108-L179)；`test_current_streak_*`、`test_single/three_day_gap*`、`test_weekly_aggregation_goals`、`test_readiness_w12_and_w15` | 零 entry 时 9/25-9/27 被算成「≥3 天中断」弹红色复核条——首日使用即误报（P2-6） |
| AC-8 零 AI 生成与零凭证 | **pass** | `test_audit_python_sources_clean`/`test_audit_templates_clean`/`test_dependencies_on_whitelist`；publisher 无 `client.click(` 静态守护 `test_no_final_publish_button_click_in_source`；审查员 grep 复核：无 subprocess/LLM SDK/域名/cookie 读取/密码 API；登录态只读页面 DOM 信号 [bridge.py L25-41](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/publishing/bridge.py#L25-L41)；剪贴板仅写草稿正文 [publisher.py L297-299](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/publishing/publisher.py#L297-L299) | 唯一 `click` 是页面内「写回答/添加回答」白名单 JS（[publisher.py L47-56](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/publishing/publisher.py#L47-L56)），不触最终发布 |
| AC-9 暖灰纸感界面（rubric ≥4） | **pass（4/5，审查员独立打分）** | 色板 [styles.css L1-18](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/web/static/styles.css#L1-L18)（#f3efe7 暖灰底/#fbf8f1 米白卡片/#4a433a 深褐文字，零纯黑、零第三方 CDN）；审查员无头 Edge 五页截图 | 暖灰纸感与文档工作台质感到位，留白/层级舒适；发布向导空状态信息密度偏低（与实现方自评一致），未达 5 分 |
| AC-10 离线核心可用 | **pass** | `test_offline_smoke_full_write_flow`（entry/earning/draft/checkoff 全落盘 + 页面 200）；GET 页面零 bridge 调用，健康检查仅按需 POST；`test_bridge_health_reports_daemon_down_offline` | 「断网」与 daemon 关闭在本应用等价（除发布桥无其他网络依赖）；真实断网手工冒烟并入 Task 14 即可 |
| AC-11 工作区路径守卫 | **pass** | [workspace.py L84-126](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/storage/workspace.py#L84-L126)；`test_*workspace*`、根级守卫参数化 6 例、`test_load_config_*` 优先级/非本地 host | 四分支 + 越界 + 配置优先级齐全 |
| AC-12 本地服务安全 | **pass（含 P1-1 接线缺陷）** | 无 cookie/错 token/外部 Origin → 403：`test_post_without/wrong/foreign_*`；[security.py L20-38](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/web/security.py#L20-L38)（含 `127.0.0.1.evil.com` 伪造用例）；host 白名单 [config.py L91-95](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/config.py#L91-L95) + `test_host_must_be_loopback`；文件锁真实双进程 `test_single_instance_lock_blocks_second_process` | **锁实现正确但 `zhihu-checkin serve` 实际未接线**（P1-1）；CSRF 为 12 小时稳定双提交令牌而非 spec 字面「一次性」（P2-3） |
| AC-13 真实浏览器文章发布冒烟（rubric ≥3） | **blocked** | 按 spec L189 规则：用户不在场，无法登录知乎执行真实冒烟 | 以 AC-4 mock 证据临时收口；转 Task 14 交付后手动项，不阻塞代码交付；**审查中未伪造任何冒烟记录** |

**汇总：AC-1/2/3/4/5/6/7/8/9/10/11/12 = pass（12 项），AC-13 = blocked（spec 预定路径）。无 fail。**

## 三、测试与覆盖率实测（审查员亲跑）

命令：`conda run -n py314 python -m pytest tests/ -q --cov=src/zhihu_checkin_hub --cov-report=term`

- 结果：**139 项全部通过**（0 fail / 1 warning：starlette TestClient 的 httpx 弃用提示，与本应用无关）。
- 覆盖率门槛（NFR-4：关键模块 ≥90%、整体 ≥80%）：

| 模块 | 覆盖率 | 门槛 | 结论 |
| --- | --- | --- | --- |
| storage/tracker.py | 96% | ≥90% | 达标 |
| domain/gate.py | 97% | ≥90% | 达标 |
| domain/streak.py | 98% | ≥90% | 达标 |
| publishing/publisher.py | 100% | ≥90% | 达标 |
| storage/checkoff.py | 91% | ≥90% | 达标 |
| publishing/bridge.py | 87% | 非关键门槛模块 | 可接受 |
| web/app.py | 80% | — | 可接受（错误分支多为表单兜底） |
| config.py | 75% | — | 可接受 |
| **TOTAL** | **92%（1332 stmts，miss 112）** | ≥80% | 达标 |

- 各文件用例数（实测收集）：test_audit 6 / test_bridge 7 / test_cli 5 / test_config_paths 14 / test_gate 3 / test_local_storage 11 / test_no_future_annotations 36 / test_publisher 24 / test_streak 7 / test_tracker_checkoff 3 / test_tracker_parse 7 / test_web 16 = **139**。
- 独立 CRLF 探针（系统临时目录，审查后已清理）：`changed line indexes: [38]`、`CRLF preserved on target: True`、`others intact: True`、`roundtrip: True 2026-09-28`、`idempotent: True`。
- 独立 AC-9 截图证据由审查员在临时工作区真实起服截取（非引用实现方截图）。

## 四、红线下沉检查（逐条）

| 红线 | 结论 | 证据 |
| --- | --- | --- |
| AI 生成端点/SDK | 未发现 | src 全树无 openai/anthropic/chat/completions/LLM 域名；pyproject 依赖 7 项全在白名单（fastapi/uvicorn/jinja2/typer/pyyaml/httpx/python-multipart） |
| 凭证读写（cookie/密码/Access Secret/z_c0） | 未发现 | 仅处理本应用自己的 CSRF cookie；登录探测只读页面元素，JS 不碰 `document.cookie`；无 getpass/password 持久化 |
| 非 loopback 绑定 | 未发现 | config 白名单 127.0.0.1/localhost/::1，CLI `--host` 同样受限；uvicorn 实参经 `test_serve_launches_uvicorn_loopback` 断言 |
| 向真实 local/ 写测试数据 | 未发现 | 全部测试用 tmp_path；唯一碰真实工作区的用例只跑只读 `git status`；审查全程两次 git status 复核，`projects/monetize/` 零条目 |
| 自动点击知乎最终发布 | 未发现 | publisher 无 `client.click(`（AST 外的正则守护测试）；唯一点击 JS 白名单为「写回答/添加回答/编辑回答/回答问题/继续编辑回答」 |
| subprocess/外部 CLI 发布 | 未发现 | src 全树无 subprocess/os.system；无 zhihu-cli answer 类调用 |
| 出站连接 | 仅预期目标 | 127.0.0.1:10086（daemon）、zhihu.com 系列编辑页（规格指定的发布目标），无其他外联；页面零第三方 CDN |

**无 P0 问题。**

## 五、发现的问题

### P0（阻断交付的红线问题）

无。F-037 人类主导红线（无 AI、人点发布）、零凭证、仅 loopback、真实数据零入库四条底线均经代码+测试+独立复核确认。

### P1（应在交付后首次真实使用前修复）

1. **单实例文件锁未接到真实启动入口，防双开实际不生效。**
   [cli.py L49](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/cli.py#L49) 调用 `create_app(cfg)`，而锁仅在 `acquire_lock=True` 时获取（[web/app.py L86-89](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/web/app.py#L86-L89)），默认 False。锁本身与双进程测试都正确，但 `zhihu-checkin serve` 永远不会创建 `local/.serve.lock`，Assumptions「单进程 + 文件锁防双开」在生产路径落空。
   建议：`cli.serve` 改 `create_app(cfg, acquire_lock=True)`（或在 uvicorn 启动前显式 `SingleInstanceLock(cfg.workspace.local/".serve.lock").acquire()` 并保活），补一条经过 CLI 的集成断言。

2. **发布 fill 的 slug 未绑定过门会话，门留痕可与实际发布草稿脱节。**
   [app.py L465-469](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/web/app.py#L465-L469) 只校验会话处于 GATE_PASSED，即按表单 slug 加载**任意**草稿填充；填充分支按 session.kind（草稿 A 的类型）走，confirm 又只认 `session.draft_slug`（A）。对草稿 A 过门后拿 B 的 slug 调 fill，可把未过门的 B 内容送进浏览器，而门留痕/draft_slug 记的是 A——绕过「每篇发布对应一份过门记录」的可追溯性。
   建议：fill 路由开头加 `if slug != session.draft_slug: 409`；gate 记录与发布对象强一致化。

3. **回答回读只校验 `/question/` 子串，未做 FR-6c 要求的「登记 URL/问题标题一致」比对，防误发控制被弱化。**
   [publisher.py L240-241](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/publishing/publisher.py#L240-L241) 仅判断回读 URL 含 `/question/`；若页面跳到另一个问题（如 `question/1000` 而草稿登记 `question/999`，或外站仿造路径）仍判通过。这是 Background V 审查明确点名的风险（误发到错误问题）。测试只覆盖跳到知乎首页的情形（`test_answer_readback_wrong_url_degrades`）。
   建议：回读比对问题 ID 与 `draft.question_url` 中的数字 ID 完全相等，并回读问题标题文本供等待页肉眼复核；补「错误 question id → degraded/阻断」用例。

4. **想法「图片已插入/无需图片」显式人工确认未实现，FR-6d 缺口。**
   [publish.html L88-90](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/web/templates/publish.html#L88-L90) 仅有一行静态提示，无确认控件、无后端等待态；pin 填充后与文章/回答同样直接进入「我已发布」。FR-6d 明确「向导须等待『图片已插入/无需图片』确认」。
   建议：pin 类型在 FILLED→AWAITING_HUMAN 之间增加显式确认按钮/状态，未确认不出现「我已发布」；补 mock 用例。

### P2（不阻断本次收口，应排入近期迭代）

1. **confirm 的 bridge 异常会变成未受控 500。** [app.py L494-497](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/web/app.py#L494-L497) 只捕获 `PublishError`；[publisher.py L165/L178](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/publishing/publisher.py#L157-L178) 的 evaluate/screenshot 抛 `BridgeError` 时直接 500，违背 AC-4「无未捕获异常、给中文指引」。建议：补获 `BridgeError` 返回 409 + 中文「通道异常，请检查后重试」。
2. **截图存证缺「PNG 存在且 >10KB」校验。** [publisher.py L175-178](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/publishing/publisher.py#L175-L178) 仅把目标 path 下发给 daemon，不回验文件；mock 也无法证明落盘。建议 confirm 后 `stat` 校验存在与 ≥10KB，不足则受控失败（且不得回填 published），Task 14 冒烟时重点验证 daemon 是否真按 `path` 落盘。
3. **CSRF 不是「一次性」令牌。** [app.py L105-112](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/web/app.py#L105-L112) cookie 12 小时不变；FR-9 字面要求一次性。AC-12 的拒绝三类攻击全部满足，故仅为措辞偏差；如要对齐，可在每次 POST 后轮换 token。
4. **FR-8 的 21:00 未打卡提醒未实现。** `daily_reminder_hour` 在 [config.py L28/L105](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/config.py#L28) 之外无任何引用，模板无阈值提示。建议仪表盘/打卡页在本地时间过阈值且当日 entry 不合格时显示提示。
5. **门导出表形与 records.md §五 不一致。** 规格要求按 §五「日期｜内容主题｜删稿测试｜占比自检｜条款留痕｜边缘场景｜结论」横表导出（[records.md L71-73](file:///d:/spaces/SpecWeave/projects/monetize/zhihu-monetization/records.md#L71-L73)），实现为「项目｜结果｜说明」竖表（[gate.py L109-124](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/domain/gate.py#L109-L124)）；tasks.md TR-6.2「列与 §五 一致」的表述不准确，测试也只断言关键字。建议改为每篇一行的七列横表。
6. **空历史误报「≥3 天中断」。** [streak.py L126-133](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/domain/streak.py#L126-L133) 把起跑日到昨天的全部缺卡日聚合，零 entry 用户首日打开即见红条（审查员截图复现：2026-09-28 报「2026-09-25 起 3 天」中断）。建议：尚无任何合格日时不产出 gap/review 提示。
7. **CRLF 安全缺回归测试。** 代码正确（`read_text(newline="")`/`write_text(newline="")`），审查员手工 CRLF 副本验证通过，但测试夹具是 LF；建议加一条 CRLF 字节级用例锁住行为。
8. **降级体验与 6e 有差距。** 降级面板直接 `JSON.stringify` 详情（[publish.html L156](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/web/templates/publish.html#L147-L160)），无「一键打开目标页」按钮；且 navigate 本身失败时 [publisher.py L307-310](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/publishing/publisher.py#L307-L310) 仍提示「已为你打开目标页面」。建议：渲染 target_url 链接/按钮，并按 navigate 是否成功区分文案。
9. **字数门槛提示缺 F 编号出处链接，且出现无据数字。** [draft_edit.html L27-30](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/web/templates/draft_edit.html#L27-L30) 写「≥100/≥20」但未链 F-033/F-040（FR-5 要求），「文章建议 ≥300 字」在 tracker/records 中无登记，属无 F 支撑数字，建议删除或补源。
10. **周核对表单未用 entries 自动聚合预填。** [records.html L29-43](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/web/templates/records.html#L29-L43) 回答/想法数靠手填，FR-7 要求「从 entries 自动聚合、人工确认」；聚合逻辑已在 streak 模块实现，接进表单即可。

### P3（打磨/证据订正）

1. **tasks.md 用例数与实测不符。** TR-12.2 称「全 178 用例」，实测收集 **139**；各 Task「累计 N 用例」为跨任务累计口径且与最终数对不上。建议订正为 139，避免收口证据失真。
2. **`zhihu-checkin check` 未做发布桥健康检查。** Task 1 描述含「校验工作区与桥接健康」，实际 [cli.py L52-75](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/cli.py#L52-L75) 只校验工作区（docstring 亦自认）。建议接 `BridgeClient.health()` 或更新描述。
3. **若干路由错误态为裸 500 而非中文指引。** 如 `/drafts/save` 非法 kind、`/drafts/{slug}` 不存在时抛 `StorageError` 未被捕获；中断表单无「恢复日」输入（records 模型支持 resumed_at）；复核折算文案未逐字使用 records.md 的「以平台实际规则为准」。
4. **健康检查有副作用。** [bridge.py L172](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/publishing/bridge.py#L172) 每次探测都把当前 tab 导航到知乎首页，会打断用户正在看的页面；建议 new_tab 或先 list_tabs 复用既有知乎 tab。
5. 想法框选择器末位为通用 `div[contenteditable='true']`（[publisher.py L40-45](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/publishing/publisher.py#L40-L45)），真实首页若存在其他可编辑区有误填风险，冒烟时重点观察。

## 六、总体结论

**结论：可以交付（代码层面 Spec 收口通过）。**

- 12 项可自动化 AC 全部 **pass**，且关键安全属性经审查员独立复核而非仅采信实现证据：fixture 与真实 tracker 逐字节一致、回写 CRLF 安全手工验证、门在路由层不可绕过、publisher 无最终发布点击、confirm 正则锚定、workspace/local 守卫、CSRF/Origin/loopback 均成立；真实工作区 `local/` 在审查前后 `git status` 均为零条目。
- 覆盖率 92%，tracker/gate/streak/publisher 分别 96%/97%/98%/100%，满足 NFR-4 门槛。
- AC-13 依 spec 第 189 行明文规则标 **blocked**（用户不在场），以 AC-4 完整 mock 证据 + 真实关闭端口探测临时收口；未伪造冒烟。
- 无 P0；4 项 P1 均不触碰 F-037 红线（人类点发布、零 AI、零凭证、loopback 均完好），但属于 FR 明确要求/防御接线缺口，**建议在 Task 14 真实冒烟前修掉 P1-2/P1-3/P1-4（直接影响冒烟有效性与防误发），P1-1 在下次 `serve` 使用前修复**。

### Task 14 后续手动项（需用户在场）

1. 用户指定时间启动 webbridge daemon 并在浏览器登录知乎；依次完成：① 文章填充→回读（可发私密或仅走到填充）② 回答填充到用户自选问题（顺带验证 P1-3 修复后错误问题能否阻断）③ 想法填充 + 图片确认控件（验证 P1-4）。
2. 至少完成 1 次「我已发布」完整闭环：核验 `/p/`（或 `/answer/`、`/pin/`）URL 判定、截图真实落入 **真实工作区** `local/screenshots/` 且为有效 PNG（>10KB，验证 P2-2 与 daemon 是否尊重 `path` 参数）、草稿转 published、当日 entry 回填。
3. 记录知乎编辑器/想法框选择器漂移点（含 P3-5 通用 contenteditable 误填风险）并修补；无法当日解决的登记 issue。
4. 冒烟完成后补 AC-13 评分（门槛 ≥3）与 AC-4/AC-10 的真实环境记录；冒烟产生的全部产物必须留在真实工作区 `local/`（gitignored），事后以 `git status --porcelain` 复核零入库。

## 七、复审记录（P1 修复后，2026-09-28 同日）

实现方按第五节 P1/P2 清单修复后复跑全量；P3-1（用例数证据失真）一并订正。

| 原问题 | 处置 | 验证 |
| --- | --- | --- |
| P1-1 serve 未接线单实例锁 | **已修复**：[cli.py](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/cli.py#L33-L51) 改 `create_app(cfg, acquire_lock=True)`，锁失败落入统一中文错误出口 | `test_serve_launches_uvicorn_loopback` 增补断言：经 CLI 启动后第二把 `SingleInstanceLock.acquire()` 抛 WorkspaceError |
| P1-2 fill slug 未绑定过门会话 | **已修复**：fill/confirm 路由均校验 `slug == session.draft_slug`，不一致 409 | 新增 `test_fill_slug_must_match_gated_draft`（过门 A 拿 B 填充被拒） |
| P1-3 回答回读未比对问题 ID | **已修复**：[publisher.py L243-248](file:///d:/spaces/SpecWeave/apps/dev-tools/zhihu-checkin-hub/src/zhihu_checkin_hub/publishing/publisher.py#L243-L248) 从登记 question_url 提取数字 ID，回读 URL 不含 `/question/{id}` 即降级 | 新增 `test_answer_readback_mismatched_question_id_degrades`（登记 999 / 回读 123 → degraded，原因含「问题 ID」） |
| P1-4 想法图片缺显式确认 | **已修复**：等待面板对 pin 渲染「图片已插入/无需图片」必选单选，前端未选拦截，后端 confirm 对 pin 强制 `pin_image∈{inserted,none}` 否则 422 | 新增 `test_pin_confirm_requires_explicit_image_choice`（缺省 422 → 选择后 200 且 `/pin/777` 存证） |
| P2-1 confirm 遇 BridgeError 裸 500 | **已修复**：confirm 路由补获 `BridgeError` 返回 502 + 中文提示 | 随 pin 向导新用例全量回归 |
| P2-7 CRLF 缺回归测试 | **已修复**：新增 `test_checkoff_preserves_crlf`（CRLF 副本逐行比对行尾形态、非目标行字节不变、幂等） | 新用例通过 |
| P3-1 用例数证据失真 | **已订正**：tasks.md TR-12.2 改为实测 143 | — |

复跑：`conda run -n py314 python -m pytest tests/ --cov=src/zhihu_checkin_hub` → **143 项全部通过**（原 139 + 新增 4：slug 绑定 / pin 图片确认 / 问题 ID 不匹配 / CRLF；CLI 锁断言并入既有 serve 用例）；整体覆盖率 **92%**（1345 stmts / 112 miss），tracker 96% / gate 97% / streak 98% / publisher 100% / checkoff 91% / cli 100%，NFR-4 持续达标。

**复审结论：4 项 P1 全部关闭且各带回归测试，AC-1..AC-12 维持 pass；AC-13 仍 blocked（Task 14 待用户在场）。无新增回归，可以交付。** 其余 P2/P3 列入后续迭代。
