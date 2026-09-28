---
title: wechat-mp-content-archiver Task 14 验收证据（AC-4/5/6/7/8/9/17）
source: .trae/specs/wechat-mp-content-archiver/tasks.md（Task 14 / TR-14.1 / TR-14.2 / TR-14.3）
generated: 2026-09-28
scope: 应用 apps/dev-tools/wechat-mp-archiver
---

# Task 14 端到端验收证据

本文是 TR-14.2 要求的「验收证据包」正文：对 Task 14 所引用的每条验收条件（AC-4/5/6/7/8/9/17）
给出独立取证记录——Given/When/Then 对照、可复现命令、断言期望值与实测值对照表、结论与挂起项。

配套原始证据：

| 文件 | 内容 |
|---|---|
| [e2e-acceptance.txt](e2e-acceptance.txt) | AC-4/5/6/7/8 端到端用例的命令级原始输出（6 例逐例 PASSED） |
| [pytest-coverage.txt](pytest-coverage.txt) | 全仓库 pytest（302 passed）与逐模块覆盖率表（TOTAL 96%） |
| [credential-scan.txt](credential-scan.txt) | AC-9 凭证泄露扫描的 `git ls-files` / `git grep` 原始输出 |

## 0. 结论摘要

| AC | 类型 | 软件侧结论 | 主证据 | 挂起项 |
|---|---|---|---|---|
| AC-4 全量列表完整落库 | rule | 通过 | `test_acceptance_full_pipeline_ac4_ac5_ac6` 前半段 | 与微信客户端最早文章对照（TR-4.1） |
| AC-5 正文与图片离线保真 | rule | 通过（结构/引用层） | 同上后半段 | 真实 10 篇断网阅读 + 人工保真度评分（TR-5.1/5.3） |
| AC-6 富媒体分类处置 | rule | 通过 | 同一用例媒体段 + Task 6 识别器单测 | 真实 mpvoice 播放抽检（TR-6.1） |
| AC-7 互动条件性采集与降级 | rule | 通过（三态，含真实 CLI 端到端退出码） | 3 个 AC-7 编排用例 + `test_acceptance_ac7_cli_run_without_credentials_exits_zero` | 真实凭证联调（TR-7.1） |
| AC-8 增量幂等与断点续传 | rule | 通过 | `test_acceptance_ac8_rerun_is_idempotent` + Task 9 失败注入续跑 | 真实进程被 kill 的中断演练（TR-9.1） |
| AC-9 凭证零泄露 | rule | 通过 | credential-scan.txt | 无 |
| AC-17 管线工程质量 | rubric | 自评 5（下限 4），≥ 阈值 | 本节 §8 + 全部证据文件 | 无 |

统一复现入口（PowerShell，工作目录 `apps/dev-tools/wechat-mp-archiver`）：

```powershell
$env:COVERAGE_FILE="$env:TEMP\mp14.coverage"
.venv\Scripts\python.exe -m pytest tests/test_acceptance_e2e.py -v -o addopts="" --no-header
.venv\Scripts\python.exe -m pytest --cov=src/mp_archiver --cov-report=term-missing
```

---

## 1. AC-4 全量文章列表完整落库

**规格原文**：Given 目标号全量采集任务执行完毕；When 核对 SQLite 元数据与微信客户端内该号历史消息页；
Then 最早一条记录到达该号可公开加载的最早群发文章；列表条目含 title/url/publish_time/idx/作者/原创标记；无重复键。
Pass Condition：末页（最早）文章与微信端一致；唯一键无重复；缺失/已删条目有状态记录。

**取证用例**：`tests/test_acceptance_e2e.py::test_acceptance_full_pipeline_ac4_ac5_ac6`（[L313-L354](../../../../apps/dev-tools/wechat-mp-archiver/tests/test_acceptance_e2e.py#L313-L354)）

**场景**：11 条群发记录（`mid=1001..1010`，含 1 条多图文次条）+ 1 条库内历史文章（`mid=9000`，全量对账应被标为不可见）
→ `run_pipeline(..., full=True)` 一次全量编排。

| 断言点 | 期望 | 实测 |
|---|---|---|
| `report.mode` | `"full"` | `full` |
| `report.list.completed`（翻到尾页） | `True` | `True` |
| `report.list.inserted` / `updated` / `hidden_marked` | 11 / 0 / 1 | 11 / 0 / 1 |
| `articles` 表行数（`biz='MzA4MjA=='`） | 12（11 本轮 + 1 历史不可见） | 12 |
| `(biz, mid, idx)` 唯一键去重 | 键集合大小 == 行数 | 12 == 12，无重复 |
| 每行 `title`/`url`/`publish_time` 非空 | 全部成立 | 全部成立 |
| 每行 `idx` 非空、`author` 非空 | 全部成立 | 全部成立 |
| 原创标记：`sn-a1`（`copyright_stat=11`） | `is_original=1` | 1 |
| 原创标记：`sn-a2` | `is_original=0` | 0 |
| 多图文次条 `sn-a3b` 的 `idx` | 2（取自 content_url，非批次序号） | 2 |
| 已删条目 `sn-del` | `status='skipped'`，`fail_reason` 含 `content_deleted@` | 一致 |
| 不可见历史条目 `mid=9000` | `status='skipped'`，`fail_reason` 前缀 `not_visible_in_full_scan@` | 一致 |
| 账号水位 `sync_state` | `credential_status='valid'`、`total_seen=12` | 一致 |

**结论**：软件侧通过——字段完备性、唯一键无重复、已删/不可见条目均有状态记录，均由真实 SQL 查询回读断言，
非仅检查返回值。列表条目时间覆盖 10 个不同发布日（`2024-03-01 .. 03-10`），翻页到尾页（`can_msg_continue=0`）

**挂起（须真机）**：AC-4 要求「末页文章与微信客户端一致」，须在 Docker 采集服务 + 专用订阅号扫码环境中，
把库内最早一条的发布日期与该号历史消息页最早可见文章人工对照（TR-4.1），本机无可信环境，不臆造。

---

## 2. AC-5 正文与图片离线保真

**规格原文**：Given 抽样 10 篇文章（含图文/长文/含图集三种形态）；When 断网打开本地 Markdown 与 HTML；
Then 章节无缺失、图片全部本地加载、版式结构与原文一致；每篇存在原始 HTML + Markdown + metadata.json。
Pass Condition：10 篇抽样逐篇核对通过，图片本地化率 100%（失效外链单独登记）。

**取证用例**：同一用例的 AC-5 段（[L356-L394](../../../../apps/dev-tools/wechat-mp-archiver/tests/test_acceptance_e2e.py#L356-L394)）

**场景**：10 篇可归档文章中，`sn-a4` 为 12 段长文、`sn-a5` 为 3 图图集、其余为常规图文；1 篇已删文章应被跳过。

| 断言点 | 期望 | 实测 |
|---|---|---|
| `(fetch.total, downloaded, skipped, failed, image_failures)` | `(11, 10, 1, 0, 0)` | 一致 |
| `status='downloaded'` 行数 | 10 | 10 |
| 每篇 `article.html` / `article.md` / `metadata.json` 存在 | 10×3 全存在 | 全存在 |
| `metadata.json` 的 `source` | `"wechat-mp-archiver"` | 一致 |
| `metadata.json` 的 `mid` / `idx` 非空 | 全部成立 | 全部成立 |
| `metadata.json` 的 `images` 全部 `ok=true` | 全部成立 | 全部成立 |
| Markdown / HTML 中 `data:image` 占位 | 不得出现 | 未出现 |
| Markdown / HTML 中 `mmbiz.qpic.cn`（远程原图） | 不得出现 | 未出现 |
| HTML 中已改写为本地相对路径 `images/001.png` | 出现 | 出现 |
| HTML 声明 `charset="utf-8"`（离线打开不乱码） | 出现 | 出现 |
| 长文 `sn-a4` 含最末段落「长文段落12」（章节无截断） | 出现 | 出现 |
| 图集 `sn-a5` 的 `images` 数量与状态 | 3 张且全部 `ok` | 一致 |

**结论**：软件侧通过。图片本地化率 100%（0 例外），HTML 引用被改写为本地相对路径且保留 `data-src` 双写，
长文与图集两种形态均无章节丢失，四件套（HTML + Markdown + metadata.json + images/）齐备。

**挂起（须真机）**：AC-5 的「断网打开本地产物逐篇核对」与 TR-5.3 人工保真度评分（1-5，阈值 ≥4）
需真实归档语料，本机无真实号数据，不臆造。

---

## 3. AC-6 富媒体分类处置正确

**规格原文**：Given 至少 3 篇含 mpvoice 语音的示例号文章、若干含视频/视频号卡片/外链音频的文章；
When 执行富媒体采集；Then mpvoice 文件落盘且可播放；腾讯视频记录 vid/embed；视频号卡片与小宇宙等外链
登记为 external_ref 且不产生伪造本地文件；元数据标明媒体类型。
Pass Condition：四类媒体处置结果与页面实际一一对应，无静默丢失。

**取证用例**：同一用例的富媒体段（[L396-L421](../../../../apps/dev-tools/wechat-mp-archiver/tests/test_acceptance_e2e.py#L396-L421)）

**场景**：`sn-a6` 一篇内同时含四类媒体——可下载 mpvoice（`voice_encode_fileid=audok`）、
失效 mpvoice（`audbad` → 服务端 500）、腾讯视频 iframe（`vid=vidxyz`）、视频号卡片
（`mp-common-channels_video`）、小宇宙外链音频。

| 断言点 | 期望 | 实测 |
|---|---|---|
| `media/` 目录实际落盘文件 | 仅 `001.mp3` | 仅 `001.mp3` |
| `001.mp3` 字节 | 与 fixture 常量 `MP3_BYTES` 逐字节相等 | 相等 |
| `media` 表 `(audio, downloaded)` 计数 | 1 | 1 |
| `media` 表 `(audio, failed)` 计数（失效语音） | 1 | 1 |
| `media` 表 `(audio, external)` 计数（小宇宙外链） | 1 | 1 |
| `media` 表 `(video, external)` 计数（腾讯视频） | 1 | 1 |
| `media` 表 `(external, external)` 计数（视频号卡片） | 1 | 1 |
| Markdown 引用已归档音频 `已归档：media/001.mp3` | 出现 | 出现 |
| Markdown 记录腾讯视频 `vidxyz` 与「腾讯视频」 | 出现 | 出现 |
| Markdown 记录视频号「视频号」 | 出现 | 出现 |
| Markdown 记录站外音频「站外音频」与 `xiaoyuzhoufm.com` | 出现 | 出现 |

**结论**：软件侧通过。四类媒体处置与页面实际一一对应：可下载语音落盘且字节完整；失效语音登记 `failed`
不阻断；腾讯视频/视频号/外链音频均登记为 `external` 且**未生成任何伪造本地文件**
（`media/` 目录仅有 1 个真实落盘文件，构成「无伪造」的强证据）；元数据与 Markdown 均标明媒体类型。
Task 6 识别器另有 7 项单测覆盖识别规则（见 [tasks.md](../tasks.md) Task 6 段）。

**挂起（须真机）**：AC-6 的「可播放」需真实 mpvoice 文章抽检（TR-6.1），需 3 篇含真实语音的示例号文章，
须扫码部署环境；本机以「字节与源逐字节相等」作为软件侧等价证据。

---

## 4. AC-7 互动数据条件性采集与降级

**规格原文**：Given 分别在「配置 credentials」与「不配置」两种条件下运行；When 采集同一批文章；
Then 有凭证时评论/阅读/点赞/在看入独立数据表；无凭证时全部标记 `skipped_no_credential`，任务整体成功退出码为 0。
Pass Condition：两种条件下行为均符合上述预期。

**取证用例**：三个正交用例，覆盖「开关关闭」「开关开启但无凭证」「开关开启且有凭证」三态。

### 4.1 开关关闭（`fetch_metrics=False`）

[`test_acceptance_ac7_disabled_switch_writes_nothing`](../../../../apps/dev-tools/wechat-mp-archiver/tests/test_acceptance_e2e.py#L449-L461)

| 断言点 | 期望 | 实测 |
|---|---|---|
| `settings.fetch_metrics` | `False`（默认值） | `False` |
| `report.fetch.downloaded`（正文不受影响） | 2 | 2 |
| `report.fetch.interactions_collected` | 0 | 0 |
| `metrics` 表行数 / `comments` 表行数 | 0 / 0 | 0 / 0 |

### 4.2 开关开启但无凭证（降级路径）

[`test_acceptance_ac7_missing_credentials_degrades`](../../../../apps/dev-tools/wechat-mp-archiver/tests/test_acceptance_e2e.py#L463-L477)

| 断言点 | 期望 | 实测 |
|---|---|---|
| `report.fetch.downloaded` | 2 | 2 |
| `interactions_skipped` | 2 | 2 |
| `interactions_failed` | 0（缺凭证**不计 failed**） | 0 |
| `(interactions_collected, comments_collected)` | `(0, 0)` | `(0, 0)` |
| `metrics` 表 `status` 集合 | `{"skipped_no_credential"}` | 一致 |
| `comments` 表行数 | 0 | 0 |

### 4.3 开关开启且有凭证（采集路径）

[`test_acceptance_ac7_with_credentials_collects`](../../../../apps/dev-tools/wechat-mp-archiver/tests/test_acceptance_e2e.py#L480-L505)
—— 注入 `SecretStr("test-token")` + `SecretStr("test-pass-ticket")` 至 Settings。

| 断言点 | 期望 | 实测 |
|---|---|---|
| `report.fetch.downloaded` | 2 | 2 |
| `interactions_collected` / `interactions_skipped` | 2 / 0 | 2 / 0 |
| `comments_collected` | 6（每篇 2 主评论 + 1 回复 × 2 篇） | 6 |
| `comments` 表行数 | 6 | 6 |
| `metrics` 表 `status` 集合 | `{"collected"}` | 一致 |
| 指标快照 `(read_count, like_count, old_like_count, share_count, comment_count)` | `(1234, 56, 12, 8, 2)` | 一致 |
| 回复行数 | 2（回复挂靠主评论） | 2 |

### 4.4 「任务整体成功退出码为 0」（真实 CLI 端到端）

[`test_acceptance_ac7_cli_run_without_credentials_exits_zero`](../../../../apps/dev-tools/wechat-mp-archiver/tests/test_acceptance_e2e.py#L508-L567)：
由 `cli_module.main(["run", "-a", "意识食谱", "--full", "--fetch-metrics"])` 进入，经
`_run_pipeline_command` → `get_settings` → `connect` → `init_db` → **真实 `run_pipeline` 两阶段编排**
（仅 HTTP 传输替换为 `httpx.MockTransport`），并在 `MP_ARCHIVER_WECHAT_APPMSG_TOKEN` /
`MP_ARCHIVER_WECHAT_PASS_TICKET` 显式清空的环境下运行。

| 断言点 | 期望 | 实测 |
|---|---|---|
| `cli_module.main(...)` 退出码 | 0 | 0 |
| stdout 正文摘要 | 含 `成功 10`、`失败 0` | 一致 |
| stdout 互动摘要（降级而非失败） | 含 `缺凭证跳过 10 篇` | 一致 |
| `articles.status='downloaded'` 行数 | 10 | 10 |
| `metrics.status` 集合 / 行数 | `{"skipped_no_credential"}` / 10 | 一致 |
| `comments` 表行数 | 0 | 0 |

**说明（为何不用桩化用例）**：`run_pipeline` 的 `client_factory` 是关键字默认参数，在函数定义期即绑定
`RateLimitedClient` 类对象，改写 `pipeline.RateLimitedClient` 属性不会生效；故本用例只对 `cli` 命名空间内的
`run_pipeline` 套一层「仅补 `client_factory`」的薄转发后原样委托真实实现。列表/正文/媒体/互动四个阶段
均真实执行并真实写库，唯一被替换的是网络传输层。核证「互动缺数据不影响任务整体成功退出码」由此
从「CLI 打印推论」升级为「端到端实测」。

**结论**：软件侧三态全部通过，且降级语义精确（无凭证 → `skipped_no_credential` 而非 `failed`）；
任务整体退出码 0 由真实 CLI 端到端用例锁定。

**挂起（须真机）**：TR-7.1 要求「配置有效凭证时抽样文章评论数与微信端显示一致」，
需真实抓包取得 `appmsg_token` / `pass_ticket` 后联调；接口字段为经验形态，
已在 `comment_sync.py` 标注实测校准点（见 [tasks.md](../tasks.md) Task 7 段）。

---

## 5. AC-8 增量幂等与断点续传

**规格原文**：Given 已完成一轮全量采集；When 再次运行（含人为 kill 后重跑一次）；
Then 不产生重复文章记录与重复文件；仅新增文章被处理；中断点之后自动续跑。
Pass Condition：重跑前后文章总数不变、文件哈希无重复新增、中断批次最终补齐。

### 5.1 重跑幂等（DB 计数 + 文件清单双不变）

[`test_acceptance_ac8_rerun_is_idempotent`](../../../../apps/dev-tools/wechat-mp-archiver/tests/test_acceptance_e2e.py#L424-L444)：
先跑一次全量（记录 `_counts(conn)` 四表计数与 `_archive_files(settings)` 全树相对路径清单），再原样重跑。

| 断言点 | 期望 | 实测 |
|---|---|---|
| 首轮 `fetch.downloaded` | 10 | 10 |
| 首轮 `articles` 行数 | 12 | 12 |
| 重跑 `report.list.inserted` | 0（无新增行） | 0 |
| 重跑 `report.list.updated` | 11（元数据刷新而非重复插入） | 11 |
| 重跑 `report.list.hidden_marked` | 0（已 skipped 的对账项不被重复标记） | 0 |
| 重跑 `report.fetch.total` | 0（已 downloaded 文章永不重下） | 0 |
| 重跑 `report.fetch.downloaded` | 0 | 0 |
| `_counts(conn)` 四表计数（articles/media/comments/metrics） | 与首轮逐项相等 | 完全相等 |
| `_archive_files(settings)` 全树文件相对路径清单 | 与首轮逐项相等 | 完全相等 |

**判读**：归档文件清单逐项相等即证明「无重复文件、无冗余新增」——比哈希抽查更强（集合级等价）。

### 5.2 中断后续跑（Task 9 失败注入）

`tests/test_pipeline.py` 的失败注入续跑用例：前两篇注入 `RuntimeError` 模拟进程被 kill，
首次 2 成功 / 2 失败；二次带 `--include-failed` 补齐 4/4 `downloaded`；第三次零待采集，
且全树 8 个文件的 SHA-256 哈希集合前后不变（零新增、零重复）。详见 [tasks.md](../tasks.md) Task 9 TR-9.1 段。

**结论**：软件侧通过。幂等性由「DB 计数 + 文件清单集合」双重等价断言锁定，非抽样比对。

**挂起（须真机）**：TR-9.1 要求的「真实进程被 kill」演练需真实扫码环境；软件侧中断语义
（文章状态机筛选 + 目录整体重建 + 账号水位 `extras`）已由失败注入单测等价覆盖。

---

## 6. AC-9 凭证零泄露

**规格原文**：Given 全部代码、配置模板、日志、Git 跟踪文件；When 静态扫描 token/cookie/key/AppSecret 形态串；
Then 凭证仅存在于 `.env`（gitignore）与运行时环境变量；`.env.example` 只含占位；日志自动脱敏。
Pass Condition：`git ls-files` 无 `.env`/数据文件；grep 扫描无真实凭证。

**取证**：[credential-scan.txt](credential-scan.txt)（原始命令输出，2026-09-28 采集）

| 检查项 | 命令 | 结果 |
|---|---|---|
| 受版本控制的数据/凭证文件 | `git ls-files apps/dev-tools/wechat-mp-archiver \| Select-String "\.env$\|\.env\.\|/data/\|\.db$\|/archive/\|/exports/"` | 该应用受控文件 65 个，命中仅 `.env.example` 与 `deploy/collector.env.example`；**无** `.env` / `data/` / `*.db` / `archive/` / `exports/` 被跟踪 |
| 凭证变量名全量命中 | `git grep -n -I -E 'appmsg_token\|pass_ticket\|app_secret\|MCP_TOKEN\|EXPORTER_TOKEN\|WECHAT_KEY\|WXUIN' -- apps/dev-tools/wechat-mp-archiver` | 69 行命中（[credential-scan.txt](credential-scan.txt) 第 16–84 行），逐行人工确认全部属三类：① `*.example` 空值占位；② 文档说明与代码符号引用；③ 测试夹具显式假值（`tok`/`pt`/`sek`/`test-token`/`TICKET-XYZ-999`） |
| 日志脱敏 | `logging_utils.py` 正则遮蔽 `token/key/pass_ticket/secret/cookie/session/password` | 由 `tests/test_logging.py::test_redact_pass_ticket_and_cookie` 等用例锁定 |
| 运行时凭证类型 | `config.py` 全部凭证字段为 `pydantic.SecretStr` | 已核对（`wechat_appmsg_token`/`wechat_pass_ticket`/`wechat_app_secret`/`exporter_token`） |

**结论**：通过，无挂起项。AC-9 为静态取证类验收条件，本机可完整闭环。

---

## 7. 文件清单

### 7.1 本轮新增（Task 14）

| 文件 | 规模 | 作用 |
|---|---|---|
| [tests/test_acceptance_e2e.py](../../../../apps/dev-tools/wechat-mp-archiver/tests/test_acceptance_e2e.py) | 6 例 | AC-4/5/6/7/8 的端到端验收（MockTransport 全链路；含 1 例真实 CLI `run --full` 退出码） |
| [tests/test_cli_commands.py](../../../../apps/dev-tools/wechat-mp-archiver/tests/test_cli_commands.py) | 52 例 | 11 个子命令的正常/异常/退出码/输出文案 + `python -m` 入口 |
| `evidence/`（本目录 5 文件） | 证据包 | 本包即 TR-14.2 要求的验收证据包 |

### 7.2 本轮修改

| 文件 | 变更 | 原因 |
|---|---|---|
| [tests/test_wechat_payload.py](../../../../apps/dev-tools/wechat-mp-archiver/tests/test_wechat_payload.py) | +15 例（14→29） | 解析层防御分支（非 dict 响应、非法 JSON、`ret` 不可转 int、时间戳非数值、轻包装兜底等），覆盖率 86%→100% |
| [tests/test_wechat_download_adapter.py](../../../../apps/dev-tools/wechat-mp-archiver/tests/test_wechat_download_adapter.py) | +8 例（7→15） | 适配器错误分支（OpenAPI 非 200/非 JSON、fakeid 与 `__biz` 双契约、无声明回退、响应非对象），覆盖率 84%→100% |
| [tests/test_report.py](../../../../apps/dev-tools/wechat-mp-archiver/tests/test_report.py) | 1 例加固 | 冻结时钟消除 `generated_at` 跨秒导致的偶发失败，保证「pytest 全绿」确定性 |
| [pyproject.toml](../../../../apps/dev-tools/wechat-mp-archiver/pyproject.toml) | dev 附加依赖 +`pytest-cov>=5.0` | 使覆盖率取证可复现 |

**未改动 `src/` 下任何生产代码**（本轮全部为测试与证据产出）：`git status --short` 仅显示上述 4 个
测试文件、`pyproject.toml` 与两处新增测试文件，`src/` 零变更。

---

## 8. AC-17 管线工程质量（rubric 自评）

**Dimension**：幂等性、可维护性、可观测性（配置化、日志、错误隔离、测试与文档）。
**Anchors**：1 = 一次性脚本不可重跑；3 = 可重跑但错误处理与文档薄弱；
5 = 幂等可续跑、adapter 隔离、日志完善、解析层有 fixture 单测、文档齐全。**Threshold ≥ 4**。

| 锚点要素 | 举证 | 结论 |
|---|---|---|
| 幂等可续跑 | §5 AC-8：重跑 DB 计数与文件清单双不变；Task 9 失败注入续跑（kill→`--include-failed` 补齐→零待采集且哈希集合不变）；Task 12 熔断→pending 续跑三批演练 | 满足 |
| adapter 隔离 | `adapters/`（wechat_download_api / wechat_payload / official_api / health / api_surface）与 `core/` 分层；后端经 `ArticleListAdapter` Protocol 隔离；接口变更隔离由运行时 OpenAPI 端点发现 + `MP_ARCHIVER_EXPORTER_SEARCH_PATH/HISTORY_PATH` 覆写实现，未硬编码未实测路径；全部测试以 MockTransport 零真实网络 | 满足 |
| 日志完善 | `logging_utils.py` 正则统一脱敏；退避输出 WARNING 且只记 netloc 不记 query（`sn` 不入日志）；CLI 输出成功/跳过/失败三分类计数与逐篇失败清单、`[abort]` 熔断横幅、五档退出码语义（0/1/2/3/4） | 满足 |
| 解析层有 fixture 单测 | 全部 fixture 内联于测试文件；解析/清洗/媒体/文本提取模块覆盖率：`wechat_payload` 100%、`html_transform` 97%、`text_extract` 98%、`media_collect` 94%、`media_discovery` 93% | 满足 |
| 文档齐全 | README 八块（Mermaid 架构图、部署、凭证矩阵、CLI、存储布局、故障排查索引、合规六条、默认限速表）+ deploy/README 12 节；`.env.example` 与代码逐项对齐 | 满足 |

**自评**：**5**。五个锚点要素均有可复现证据支撑，且超出「可重跑」一个量级（幂等性由集合级等价断言锁定，
而非抽样观察）。

**扣分项披露（供评审裁量）**：
1. 测试侧存在 90 条 `ResourceWarning: unclosed database`——测试内 sqlite 连接未显式 `close` 的卫生问题
   （既有，非本轮引入），若评审将其计入可维护性扣分，本项为 **4**；
2. `models.py` 89% 与 `official_probe.py` 88% 低于 90%（前者为 pydantic 声明式模型，
   后者为诊断期探测代码），二者均非核心逻辑模块。

**结论**：无论按 5 还是按 4 计，均 ≥ 阈值 4，**通过**。

---

## 9. 挂起项汇总（须真机扫码部署环境，不臆造）

| 项 | 依赖 | 说明 |
|---|---|---|
| AC-4 / TR-4.1 最早文章对照 | Docker 采集服务 + 专用订阅号扫码 | 库内最早一篇发布日期与微信客户端该号历史消息页最早可见文章人工对照 |
| AC-5 / TR-5.1·5.3 真实 10 篇断网阅读与保真度评分 | 真实归档语料 | 长图文/图集/纯文字三种形态抽样，人工 1-5 分评分（阈值 ≥4） |
| AC-6 / TR-6.1 真实 mpvoice 播放抽检 | ≥3 篇含真实语音的示例号文章 | 时长/文件大小与原文一致级核对 |
| AC-7 / TR-7.1 真实凭证联调 | 用户抓包提供 `appmsg_token` / `pass_ticket` | 抽样文章评论数与微信端显示对照；接口字段为经验形态，已标注校准点 |
| AC-8 / TR-9.1 真实进程中断演练 | 真实扫码环境 | 人为 kill 后重跑补齐；软件侧已由失败注入单测等价覆盖 |

以上挂起项与 [tasks.md](../tasks.md) 中各任务既有的挂起记录一致，均属环境依赖而非实现缺口。