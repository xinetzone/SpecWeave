---
title: "VibeKnow CLI 源码事实清单（R 阶段）"
description: "以 v0.9.2 @ 93a26ec 固定信源逐条采集的编号事实 F-001~F-042，供 I 阶段洞察推导与 V 阶段独立复核使用"
type: spec-facts
tags: [vibeknow, cli, go, source-code, facts]
generated: { by: "trae:seven-concepts-cmd", at: "2026-10-21T00:00:00+08:00" }
verified: { by: "pending:V-phase", at: "2026-10-21T00:00:00+08:00" }
status: draft
stale_after: "2027-04-21"
source: "external/dao/flows/vibeknow/cli @ v0.9.2 (93a26eca3383d480148c5cfd8da7995ee3352187)"
---

# VibeKnow CLI 源码事实清单

> **信源锚定**：仓库 `external/dao/flows/vibeknow/cli`，tag `v0.9.2`，commit `93a26eca3383d480148c5cfd8da7995ee3352187`，remote `git@github.com:vibeknow/cli.git`，提交时间 2026-09-09 14:56:00 +0800（`chore(release): 0.9.2`）。工作树干净。
>
> **路径约定**：本清单所有路径均为仓库内相对路径（如 `cmd/create.go`），不使用 `file:///` 与本机绝对路径。
>
> **数量口径纪律**：凡「X 个 / Y 处 / N 类」类陈述，均由独立脚本（`count_facts2.py`、`count_command_tree.py`、`count_endpoints.py`）产出，原始匹配数与去重名数分列，统计口径随条目附注。
>
> **G1 事实门**：本清单只记录代码中存在的实体、取值与行为，不含因果连接词与推断性表述（禁词清单见 `.agents/skills/seven-concepts-cmd/references/compiled-methodology.md` 的 G1 条款；被禁词若以字面量出现在引用的后端错误码或字段名中，按原样保留）。

---

## 一、信源与形态

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-001 | 信源固定在 tag `v0.9.2`、commit `93a26eca3383d480148c5cfd8da7995ee3352187`，remote `git@github.com:vibeknow/cli.git`，提交信息 `chore(release): 0.9.2` | `git describe --tags`；`git rev-parse HEAD`；`git log -1` | 仓库共 18 个 tag（v0.1.0…v0.9.2） |
| F-002 | 仓库自述为基于 Cobra 的 Go CLI，附带 npm 分发包装 | `AGENTS.md:1` | — |
| F-003 | 模块路径 `github.com/vibeknow/cli`，Go 工具链声明 `go 1.25.0` | `go.mod:1`、`go.mod:3` | — |
| F-004 | 直接依赖 9 个：`charmbracelet/huh v1.0.0`、`lipgloss v1.1.0`、`gofrs/flock v0.12.1`、`spf13/cobra v1.10.2`、`spf13/pflag v1.0.9`、`zalando/go-keyring v0.2.8`、`golang.org/x/sync v0.20.0`、`golang.org/x/sys v0.43.0`、`golang.org/x/term v0.42.0`、`gopkg.in/yaml.v3 v3.0.1` | `go.mod:7-25` | 按 `require` 块逐行计，含 yaml.v3 共 10 个条目 |
| F-005 | 顶层目录：`cmd/`、`internal/`、`client/`、`skills/`、`tests/`、`npm/`、`scripts/`、`.github/`，另有 `main.go`、`go.mod`、`package.json`、`AGENTS.md`、`build.sh` | 仓库目录树 | — |
| F-006 | `build.sh` 交叉编译 5 个平台（darwin/amd64、darwin/arm64、linux/amd64、linux/arm64、windows/amd64），二进制名 `vibeknow`（Windows 为 `vibeknow.exe`），版本号经 `-ldflags -X github.com/vibeknow/cli/cmd.version` 注入 | `build.sh:1-40` | — |

## 二、命令树与旗标

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-007 | 顶层注册命令目标 19 个：13 个分组命令（`api`/`auth`/`avatar`/`config`/`credits`/`doc`/`jobs`/`kb`/`profile`/`subtitle`/`theme`/`video`/`voice`）+ 6 个非分组命令（`create`/`init`/`update`/`version`/`doctor`/`completion`） | `cmd/root.go:88-102`；`cmd/doctor.go`、`cmd/completion.go`、`cmd/update.go`、`cmd/version.go` 的 `init()` | 脚本原始输出 20 项，其中 `apicmd` 与 `Cmd` 为正则把 `apicmd.Cmd` 切开的伪影，修正后为 19 |
| F-008 | 分组子命令共 41 个：`api` 1、`auth` 4、`avatar` 1、`config` 3、`credits` 1、`doc` 3、`jobs` 3、`kb` 3、`profile` 5、`subtitle` 2、`theme` 1、`video` 13、`voice` 1 | `count_command_tree.py` → `count_tree.txt` | 以 `AddCommand` 调用点为准，非 `Use:` 字符串去重 |
| F-009 | `vk video` 下挂 13 个子命令：`status`、`wait`、`download`、`list`、`url`、`export`、`export-status`、`script`、`edit`、`set`、`pause`、`resume`、`avatar-retry` | `cmd/video/*.go`；`count_tree.txt` | 逐文件对应，`cmd/video/` 下 15 个 `.go` 文件中 `helpers.go` 与 `video.go` 不含独立子命令 |
| F-010 | 根命令挂 3 个持久旗标：`--profile`、`--output`、`--verbose` | `cmd/root.go`；`count_output2.txt` | — |
| F-011 | `cmd/` 目录内旗标注册调用 104 处；按（文件, 旗标名）去重得 103 对；旗标名全局去重得 72 个 | `count_facts2.py` → `count_output2.txt` | 口径：括号配对抓取完整实参列表后取首个字符串字面量，同时兼容 `String`/`StringVar`/`BoolVar`/`IntVar` 等注册形式 |
| F-012 | `vk create` 拥有 23 个自有旗标：`aspect`、`async`、`avatar`、`avatar-position`、`avatar-size`、`bgm`、`confirm`、`engine`、`export`、`from`、`images`、`kb-id`、`language`、`mode`、`pages`、`preset`、`preview-dir`、`prompt`、`script-lock`、`text`、`theme`、`voice`、`yes` | `cmd/create.go:832-856`（22 个）+ `cmd/create_preset.go`（`preset` 1 个） | 按旗标名去重 |
| F-013 | `cmd/video/` 旗标（文件, 旗标名）去重对 44 个 | `count_output2.txt` | — |
| F-014 | 未知旗标触发 `clerr.Validation`（退出码 2），并按 Levenshtein 距离给出最接近旗标名 | `cmd/exitcode.go:28-35`、`cmd/exitcode.go:54-56` | `nearestFlag` 遍历当前命令及父命令的可用旗标 |
| F-015 | `usagePrefixes` 收录 9 条 cobra 命令行解析失败前缀（unknown command / unknown flag / unknown shorthand flag / flag needs an argument / invalid argument / required flag(s) / accepts / requires at least / requires at most），命中即转退出码 2 | `cmd/exitcode.go:104-127` | 脚本计数 9 条 |
| F-016 | `vk api call` 支持 4 个旗标：`--service`、`--method`、`--path`、`--body` | `cmd/api/call.go`；`count_output2.txt` | — |
| F-017 | `vk profile add` 支持 8 个旗标：`--credential-ref`、`--default-project`、`--endpoint-account`、`--endpoint-figlens`、`--endpoint-vectoria`、`--endpoint-vibeknow`、`--is-production`、`--trust` | `cmd/profile/add.go` | — |

## 三、退出码与失败类型

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-018 | `internal/clerr` 定义 6 个退出码常量：`ExitOK=0`、`ExitAPI=1`（通用 API / 兜底）、`ExitValidation=2`（参数或旗标校验未过）、`ExitAuth=3`（令牌缺失 / 无效 / 过期）、`ExitNetwork=4`（DNS / 连接 / 超时）、`ExitInternal=5`（不应出现的缺陷） | `internal/clerr/clerr.go:25-30` | 源码注释原文译述 |
| F-019 | `internal/clerr` 定义 5 个失败类型字符串：`validation`、`auth`、`network`、`api`、`internal` | `internal/clerr/clerr.go:15-19` | 脚本计数 5 |
| F-020 | 退出码 8 常量名为 `ExitBlocked`，定义在 `internal/cmdutil/gate.go:28`；退出码 6 与 7 无命名常量，以 `WithCode(6)` / `WithCode(7)` 形式内联 | `internal/cmdutil/gate.go:28`；`internal/cmdutil/unknown.go`；`cmd/video/export.go:150` | 脚本统计使用点：6 共 9 处（create/video.edit/video.progress/video.script/video.set/video.wait/unknown），7 共 1 处（video.export） |
| F-021 | 退出码 4 亦覆盖后端可重试类失败码：`rate_limited`、`internal_error`、`concurrent_work_limit`、`work_edit_busy` | `AGENTS.md:73-75` | 后端码名按字面量保留 |
| F-022 | 退出码 5 亦覆盖 `insufficient_credits`；退出码 8 覆盖「付费动作已触达但无终端可应答、且事先无授权」的情形 | `AGENTS.md:76-78` | — |
| F-023 | 阻塞至终态的命令（`vk create`、`vk video wait`、`vk video export` 无 `--async`）以终态状态作为退出码；单次读取型命令（`vk video status`、`vk video export-status`）退出 0 并在载荷中报告状态 | `AGENTS.md:160-167` | — |

## 四、付费授权门（exit 8）

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-024 | `cmdutil.Gate` 按四级顺序解析付费动作：① `--yes` 或环境变量 `VIBEKNOW_ASSUME_YES` 非空 → 直接放行；② `--confirm <token>` → 经 `pending.Verify` 校验，匹配则放行，不匹配返回 `clerr.Validation` 并带重新取号的提示；③ 存在 TTY → 交互确认；④ 其余情形 → 写出决策并返回退出码 8 | `internal/cmdutil/gate.go:56-75` | — |
| F-025 | 两个授权边界类型：`export_confirmation`（载荷 `session_id`/`credits`/`operation`）与 `scene_edit_confirmation`（载荷 `session_id`/`scene_index`/`script_only`/`from`/`to`） | `internal/cmdutil/gate.go:30-42`；`AGENTS.md:139-142` | 载荷字段与 AGENTS.md 表格一致 |
| F-026 | `action_id` 为 `act_` 前缀 + HMAC-SHA256 十六进制摘要前 24 位；HMAC 输入为「动作类型字节 + 1 个 0x00 字节 + 规范化载荷字节」 | `internal/pending/pending.go:51`、`internal/pending/pending.go:102-112` | 前缀常量 `TokenPrefix = "act_"` |
| F-027 | 规范化载荷对键名排序后以 `k=<json值>;` 形式拼接，保证同一决策恒定哈希 | `internal/pending/pending.go:133-151` | 键值 JSON 序列化失败时跳过该键 |
| F-028 | 铸造密钥位于 `<config-dir>/action.key`，为 32 字节 `crypto/rand` 随机值，所在目录权限 0o700、文件权限 0o600 | `internal/pending/pending.go:153-159` 及 `secret()` 实现 | 令牌校验用 `subtle.ConstantTimeCompare` |
| F-029 | 阻塞输出落在 stdout：json 格式为 `pending_actions[]`，ndjson 格式为 `type="action.required"`，text 格式为 `status=blocked` + `action_id=` + `resume=` 键值行 | `internal/cmdutil/gate.go` 的 `block()` 实现 | 载荷含 `options[].effect`（`resume` / `none`）与完整 `resume_command` |
| F-030 | `vk video export` 的恢复命令由闭包拼出，形态为 `vk video export <task_id> --session-id <sid> --confirm <token>` | `cmd/video/export.go:64-73` | — |
| F-031 | `vk video edit` 的恢复命令拼出形态为 `vk video edit <task_id> --session-id <sid> --scene <n> --script <quoted> [--script-only] --confirm <token>` | `cmd/video/edit.go:316-323` | 脚本文本经 `shellQuote` 转义 |
| F-032 | 令牌校验为「证据边界」而非安全边界：任何以用户身份运行的进程可读密钥；令牌无法靠会话推理凭空产生 | `AGENTS.md:123-127` | 源码注释同义 |

## 五、exit 6 的三态投递判定

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-033 | 退出码 6 的详情载荷含 `delivery` 与 `resend_safe` 两个字段；`delivery` 取值为 `submitted` / `not_submitted` / `indeterminate` 三态 | `internal/cmdutil/unknown.go`（`DeliverySubmitted` / `DeliveryNotSubmitted` / `DeliveryIndeterminate`） | — |
| F-034 | `resend_safe` 仅在 `delivery == not_submitted` 时为 true；`submitted` 与 `indeterminate` 均为 false | `internal/cmdutil/unknown.go` 的 `ResendSafe()` | 判定式为 `u.Delivery == DeliveryNotSubmitted` |
| F-035 | 三态判据：`submitted` 表示后端已有该 session 的 work 行；`not_submitted` 表示后端返回 not_found（work 行在 init 时创建，缺席即无计费）；`indeterminate` 表示探针本身失败 | `AGENTS.md:88-92` | — |
| F-036 | 退出码 6 覆盖三种情形：健康运行的 `--for` 预算耗尽（`error.detail.reason` 为 `wait_budget_expired`）、流在无终止事件时结束、任务处于暂停态（`vk video resume`） | `AGENTS.md:59-63` | — |

## 六、输出格式与事件通道

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-037 | 输出格式共 3 种：`text`、`json`、`ndjson`；非法取值返回失败而非静默回落 | `internal/output/format.go:11-15`、`internal/output/format.go:52-62` | — |
| F-038 | 格式解析优先级：显式 `--output` > 环境变量 `VIBEKNOW_OUTPUT` > 默认 `text`；`flagSet` 参数区分「传了空串」与「未传」 | `internal/output/format.go:42-50` | — |
| F-039 | 源码注释明确不做「检测管道自动切 JSON」，对齐 gh / kubectl / docker 的显式格式约定 | `internal/output/format.go:22-25` | — |
| F-040 | 结构化进度事件走 stderr，每行以 `vk_event=` 前缀开头；stdout 只承载结果 | `internal/events/events.go:1-17`、`internal/events/events.go:29` | — |
| F-041 | 事件通道默认仅在 `--output json` 时开启；环境变量 `VIBEKNOW_EVENTS` 取 `1`/`on`/`true`/`stderr` 开启，取 `0`/`off`/`false`/`none` 关闭；ndjson 模式下事件保留在 stdout，不复制到 stderr | `internal/events/events.go:60-79` | — |
| F-042 | 事件为建议性质：`Emit` 丢弃写入失败，不向调用方返回失败；未开启时返回零值 Emitter，`Emit` 为空操作 | `internal/events/events.go:37-58`、`internal/events/events.go:86-96` | — |

## 七、预览产物、运行账本与异步语义

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-043 | `--preview-dir` 落盘的资产类型为 `cover_image`（KindCover）与 `video_playback`（KindVideo）；事件类型为 `resource_ready` 与 `resource_preview_warning` | `internal/preview/preview.go:38-47` | — |
| F-044 | 预览交付按内容 sha256 哈希去重，写入采用临时文件 + rename | `internal/preview/preview.go:96`、`internal/preview/preview.go:157`、`internal/preview/preview.go:215` | — |
| F-045 | 源资源 URL 不进入事件载荷 | `internal/preview/preview.go`（`Deliver` 实现注释） | 源码注释记录签名 URL 等同发布凭据 |
| F-046 | 运行账本文件路径为 `<config-dir>/jobs.jsonl`，状态取值 6 个：`submitted`、`running`、`succeeded`、`failed`、`unknown`、`paused` | `internal/jobs/jobs.go:39-44`、`internal/jobs/jobs.go:77-82` | — |
| F-047 | 账本写入为单次 `O_APPEND` 追加；行数超过阈值 `compactThreshold = 2000` 时改写文件 | `internal/jobs/jobs.go:72`、`internal/jobs/jobs.go:111`、`internal/jobs/jobs.go:125` | — |
| F-048 | 账本写入为尽力而为：写入失败在 stderr 告警，不使运行失败；账本条目缺失表示「此处未记录」，不表示「运行不存在」 | `AGENTS.md:181-184` | — |
| F-049 | 目标解析三级顺序：显式 `--session-id` 优先 → 本地账本（`jobs.Get(taskID)` / `jobs.Latest()`）→ 后端最近 work（`ListWorks(ctx,1,1)`）；仅给 task_id 而无 session 时不做远程解析 | `cmd/video/helpers.go:56-120` | — |
| F-050 | `--async` 不跳过启动流水线；`asyncDetachTimeout = 60 * time.Second` 为等待后端首个流事件的上限，触顶不致命但会报告 | `cmd/create.go:61-65` | — |
| F-051 | `--async` 与 `--export` 互斥，组合返回 `clerr.Validation`（退出码 2） | `cmd/create.go:122-124` | — |
| F-052 | 同步导出轮询在 `context.Canceled` 或超时情形下以退出码 6 结束；导出失败以 `clerr.New(...).WithCode(7)` 结束（预览就绪、MP4 未就绪） | `cmd/video/export.go:123`、`cmd/video/export.go:128`、`cmd/video/export.go:150` | — |
| F-053 | 后端导出对同一 (user, session) 幂等，返回同一 task_id | `cmd/video/export.go`（`Export` 调用处注释） | — |

## 八、create 参数域与正交组合

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-054 | `--mode` 接受 4 档取值：`replica`、`image`（线上值为 `image2`）、`handdraw`（线上值为 `hand-draw`）、以及弃用别名 `script`（等价于 `--script-lock`）；空值表示不指定 | `cmd/create.go:1191-1208` | 弃用别名命中时向 stderr 输出弃用告警 |
| F-055 | `--engine` 接受 2 档取值：`pipeline`（线上枚举 `EnginePipeline = 0`）与 `agent`（线上枚举 `EngineAgent = 1`）；`pipeline` 对应后端路径 `/v1/agent3forVideo/stream`，`agent` 对应 `/v1/agent2forVideo/stream` | `cmd/create.go:1310`、`client/figlens/engine.go` | — |
| F-056 | agent 引擎与 `replica` / `image2` / `hand-draw` 三种视频类型的任意组合返回校验失败 | `cmd/create.go:1327`（`validateEngineModeCombo`）、`cmd/create.go:141-143` | 校验位于任何上传与计费动作之前 |
| F-057 | agent 引擎禁用 `--theme` 与 `--language`；agent 引擎禁用 `--avatar`；`hand-draw` 禁用 `--avatar`；`replica` 禁用 `--images`；agent 引擎禁用 `--images` | `cmd/create.go:155-197` | 各条均为 `clerr.Validation` |
| F-058 | `--pages` 取值范围 0..20，且仅在 `image2` 视频类型下可用 | `cmd/create.go:144-151` | 上界 20 对应后端 `Image2MaxPageCount` |
| F-059 | `--aspect` 归一为 2 个线上取值：`horizontal` / `vertical`；`16:9` 与 `9:16` 作为别名 | `cmd/create.go:1241-1251` | — |
| F-060 | `--language` 允许 7 个取值：`zh-CN`、`en-US`、`es-ES`、`fr-FR`、`pt-BR`、`ja-JP`、`ko-KR` | `cmd/create.go:1258` | — |
| F-061 | `--images` 接受逗号分隔的 1 基索引（如 `1,3,5`）；重复值与空白被容忍，非正整数或非数字返回校验失败；空输入透传为 nil | `cmd/create.go:1214-1237` | 索引取值与 `vk doc images` 打印的编号一致 |
| F-062 | `--from` 按四种来源分流：文本或 `-`（stdin）→ 上传文本；`doc_id` → 直接使用且必须配 `--kb-id`；`http(s)` URL → 上传 URL；其余按本地文件处理 | `cmd/create.go:220-243` | — |
| F-063 | `--text` 与 `--from` 同时出现返回校验失败；两者同时缺失亦返回校验失败 | `cmd/create.go:107-116` | — |
| F-064 | `doc_id` 识别正则接受两种形态：`doc_` 前缀加 8 位以上字母数字，或 8-4-4-4-12 的小写十六进制 UUID | `cmd/create.go:73-82` | — |
| F-065 | 校验顺序为：preset 展开 → text/from 互斥 → async+export 互斥 → mode → aspect → engine → engine+mode 组合 → pages → theme/language → avatar → images | `cmd/create.go:103-198` | preset 展开位于 `RunE` 起始处，早于其余校验 |
| F-066 | `--voice` 在任何上传动作之前解析，音色引用无效时不产生知识库与已解析文档 | `cmd/create.go:200-215` | — |

## 九、preset 契约

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-067 | preset 允许设置的 `create` 旗标共 14 个：`mode`、`script-lock`、`aspect`、`bgm`、`engine`、`pages`、`images`、`theme`、`language`、`voice`、`prompt`、`avatar`、`avatar-position`、`avatar-size` | `internal/preset/preset.go:80-95` | 脚本计数 14 |
| F-068 | preset 拒绝的键共 9 个，每个附带拒绝理由：`export`、`yes`、`confirm`、`from`、`text`、`kb-id`、`async`、`preview-dir`、`output` | `internal/preset/preset.go:100-110` | 脚本计数 9 |
| F-069 | preset 展开跳过已被用户显式设置的旗标（`pflag` 的 `Changed` 标志），即 preset 只提供默认值 | `internal/preset/preset.go` 的 `Apply(fs *pflag.FlagSet, f *File)` | — |
| F-070 | preset 文件的 `schema_version` 声明值不等于 `1` 时被拒绝读取；顶层拼错的键由 `dec.KnownFields(true)` 拒绝 | `internal/preset/preset.go:64`、`internal/preset/preset.go:203-207` | — |
| F-071 | preset 搜索目录为 `<config-dir>/presets`；裸名称按 `.yaml` / `.yml` 两种后缀查找；不存在时提示信息附可用名称列表；该特性不提供 `vk preset list` 子命令 | `internal/preset/preset.go:112-119`、`internal/preset/preset.go:132-162` | — |
| F-072 | preset 展开失败一律以退出码 2 结束，失败发生在任何上传动作之前 | `cmd/create_preset.go`（`applyCreatePreset`） | — |

## 十、字幕样式与工作修改

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-073 | 字幕样式采用「读-改-写」方式写入，不做只写 | `cmd/video/set.go:195-197` | 后端整体保存样式 |
| F-074 | 写入前先以 `figlens.ParseSubtitleStyle(work.SubtitleStyle)` 解析出既有样式对象，再逐字段覆盖 | `cmd/video/set.go:197` | — |
| F-075 | 字幕样式旗标共 10 个：`subtitle-preset`、`subtitle-size`、`subtitle-color`、`subtitle-font`、`subtitle-font-weight`、`subtitle-bg-color`、`subtitle-bottom`、`subtitle-stroke-color`、`subtitle-stroke-width`、`subtitle-animation` | `cmd/video/set.go:43-47` | — |
| F-076 | `--subtitle-preset` 的应用顺序在其它字幕旗标之前，preset 先落、单个旗标后落并覆盖 preset 的同名字段 | `cmd/video/set.go:199-236` | — |
| F-077 | `strokeWidth` 取值 0 表示无描边，样式合并以指针字段保留「0」与「未设置」的区别 | `cmd/video/set.go:229`、`cmd/video/set.go:449` | — |
| F-078 | `--subtitle-stroke-width` 取值范围 0..12（`figlens.SubtitleStrokeWidthMax`） | `cmd/video/set.go:326-329` | — |
| F-079 | `vk video set` 触及 work 的旗标集合为 `bgm`、`bgm-volume`、`subtitle` 加 10 个字幕样式旗标；`--title` 不在其中 | `cmd/video/set.go:51`、`cmd/video/set.go:98-103` | — |
| F-080 | `vk video set` 的任何 work 级修改都会使已渲染 MP4 失效；改名 `--title` 为例外，不触及输出 | `cmd/video/set.go:49-51`、`cmd/video/set.go:78-81` | — |

## 十一、批量清理安全契约

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-081 | `vk kb prune` 必须至少带 `--pattern` 或 `--older-than` 其一，否则返回校验失败（退出码 2） | `cmd/kb/prune.go`（`validatePruneFilters`） | — |
| F-082 | `vk kb prune` 默认走 dry-run，json 输出含 `dry_run: true`、`matched` 计数与 `items` 列表；加 `--yes` 才执行删除 | `cmd/kb/prune.go` | — |
| F-083 | `vk kb prune` 分页尺寸常量 `prunePageSize = 100` | `cmd/kb/prune.go` | — |
| F-084 | `vk jobs prune` 接受 `--terminal`、`--older-than`、`--all` 三个旗标；不带旗标的裸调用被拒绝 | `cmd/jobs/prune.go`；`AGENTS.md:176-179` | — |
| F-085 | `vk kb delete` 保留交互提示：销毁性但不计费 | `AGENTS.md:157-158` | — |

## 十二、后端端点与规模

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-086 | `client/` 下 4 个服务客户端：`account`、`figlens`、`vectoria`、`vibeknow` | `client/` 目录树；`internal/endpoints/defaults.go` | — |
| F-087 | 后端端点路径去重合计 39 个：`account` 5、`figlens` 26、`vectoria` 6、`vibeknow` 2 | `count_endpoints.py` → `count_endpoints.txt` | 口径：仅取 `client/` 非测试文件中 HTTP 调用实参里的 `/v` 开头路径字面量，`fmt.Sprintf` 格式串归一化 `%s`/`%d` 为 `{param}` |
| F-088 | `account` 服务端点为 `/v1/auth/device/code`、`/v1/auth/device/token`、`/v1/auth/logout`、`/v1/auth/token/refresh`、`/v1/user/profile` | `client/account/` | — |
| F-089 | `vectoria` 服务端点为 `/v1/knowledgebases`、`/v1/knowledgebases/{param}`、`/v1/knowledgebases/{param}/documents/file`、`/v1/knowledgebases/{param}/documents/url`、`/v1/knowledgebases/{param}/documents/{param}`、`/v1/knowledgebases?offset={param}&limit={param}` | `client/vectoria/` | — |
| F-090 | `vibeknow` 服务端点为 `/v1/credits/balance` 与 `/v1/pipeline-voices` | `client/vibeknow/` | — |
| F-091 | `figlens` 服务端点含 `/v1/tasks/init`、`/v1/works/subtitleStyle`、`/v1/works/subtitleSwitch`、`/v1/works/bgmSwitch`、`/v1/works/bgmVolume`、`/v1/works/subtitleFonts`、`/v1/works/subtitlePresets`、`/v1/pipeline/pause`、`/v1/pipeline/resume`、`/v1/scene/edit`、`/v1/avatar/catalog`、`/v1/avatar/scenes/retry` 等 26 个 | `client/figlens/`；`count_endpoints.txt` | 完整清单见 `count_endpoints.txt` |
| F-092 | i18n 词条 392 条，去重后 196 条；按前缀分布为 create 152、auth 68、kb 34、video 32、export 20、init 18、edit 10、doctor 8、avatar 8、update 8、err 6、msg 6、credits 6、theme 6、subtitle 4、download 4、root 2 | `internal/i18n/strings.go`；`count_endpoints.txt` | 计数为源码词条数，中文与英文各占一份 |
| F-093 | `internal/` 各包非测试代码行数合计 6803 行；体量前三为 `httpclient` 861、`cmdutil` 812、`keychain` 558 | `count_endpoints.txt` | 口径：按 `len(splitlines())` 计，排除 `*_test.go` |
| F-094 | 配置目录解析顺序为 `VIBEKNOW_CONFIG_HOME` > Windows `%AppData%/vibeknow` > `$XDG_CONFIG_HOME/vibeknow` > `~/.config/vibeknow`；profiles 文件为 `<config-dir>/profiles.yaml` | `internal/config/path.go:12-30` | 目录不自动创建 |

## 十三、统一快照契约

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-095 | `internal/video/snapshot` 定义统一快照结构 `Snapshot`，字段含 TaskID、SessionID、WorkID、Engine、Title、DurationMs、CoverURL、Preview、Export、NextActions | `internal/video/snapshot/snapshot.go:20` | — |
| F-096 | 快照状态常量为 4 个：`idle`、`running`、`succeeded`、`failed` | `internal/video/snapshot/snapshot.go:53-56` | — |
| F-097 | 预览就绪判定为「work 状态为 Active 且分享令牌非空」 | `internal/video/snapshot/snapshot.go:97` | — |
| F-098 | 快照渲染分三种：`RenderText` 输出键值块并在 stderr 追加提示行；`Render` 按格式分派；`RenderNDJSON` 在载荷中置 `type="snapshot"` | `internal/video/snapshot/snapshot.go:146`、`176`、`190` | — |
| F-099 | 目标串构造 `Target(taskID, sessionID)`：task_id 为 0 时输出 `--session-id <sid>` | `internal/video/snapshot/snapshot.go:243` | — |
| F-100 | `nextActions` 按导出状态分四支给出后续动作（idle / running / succeeded / failed） | `internal/video/snapshot/snapshot.go:250-273` | — |

## 十四、AI Skill 资产

| ID | 事实 | 信源 | 口径 / 备注 |
|---|---|---|---|
| F-101 | `skills/` 目录下有 3 个 Skill：`vibeknow-core`、`vibeknow-create`、`vibeknow-doc`；连同 references 目录共 12 个文件 | `skills/` 目录树 | SKILL.md 行数分别为 131、438、109 |
| F-102 | Skill frontmatter 字段含 `name`、`description`、`version`（0.9.2）、`emoji`、`homepage`、`allowed-tools`（`Bash(vibeknow:*)`）、`metadata.openclaw.requires.bins/install/primaryEnv/envVars` | `skills/vibeknow-create/SKILL.md:1-30` | — |
| F-103 | `vibeknow-create` Skill 的运行契约含三条硬约束：对同一请求不重复执行 `vibeknow create`（第二次 create 即第二次计费渲染）；不合并两个流（`2>&1` 破坏契约）；不自行编造 `--confirm` 值、不主动追加 `--yes` | `skills/vibeknow-create/SKILL.md`（Run Contract 段） | — |
| F-104 | `vibeknow-create` Skill 的工作流分 4 阶段：outline → tts → render → publish | `skills/vibeknow-create/SKILL.md` | — |

---

## 审计轨迹

| 轮次 | 事项 | 处理 |
|---|---|---|
| R1 | 旗标计数脚本 v1 只匹配「首参为字符串字面量」的注册形式，漏掉 `StringVar`/`BoolVar`/`IntVar` 等指针首参形式，旗标名去重数被低估 | v2 改为括号配对抓取完整实参列表再取首个字符串字面量，并分列「(文件,旗标名)去重对数」与「旗标名全局去重数」两个口径，得出 103 / 72（F-011） |
| R2 | 退出码常量在 `cmd/exitcode.go` 提取结果为 0 | 改扫全仓 `Exit*` 常量定义，定位到 `internal/clerr/clerr.go`（0-5）与 `internal/cmdutil/gate.go`（8）；6/7 为内联 `WithCode`（F-020） |
| R3 | 端点路径按「变量赋值形式」提取，四服务端均为 0 | 改为扫 HTTP 调用实参中的 `/v` 开头字面量，得 39 个去重端点（F-087） |
| R4 | 命令树以 `Use:` 字符串去重得 49，且顶层列表把 `apicmd.Cmd` 切成两项 | 改以 `AddCommand` 调用点为准，顶层修正为 19（F-007、F-008） |
