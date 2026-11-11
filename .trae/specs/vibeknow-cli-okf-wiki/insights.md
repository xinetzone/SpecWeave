---
title: "VibeKnow CLI 架构洞察与知识地图（I 阶段）"
description: "基于 F-001~F-104 的 5 条洞察四元组（陈述/证据/反常识/行动）与 OKF bundle 文档分组、学习路径设计"
type: spec-insights
tags: [vibeknow, cli, go, architecture, insights]
generated: { by: "trae:seven-concepts-cmd", at: "2026-10-21T00:00:00+08:00" }
verified: { by: "pending:V-phase", at: "2026-10-21T00:00:00+08:00" }
status: draft
stale_after: "2027-04-21"
source: ".trae/specs/vibeknow-cli-okf-wiki/facts.md"
---

# VibeKnow CLI 架构洞察与知识地图

> 上游事实清单：[facts.md](facts.md)（104 条编号事实，信源 `v0.9.2 @ 93a26eca`）。
> 本文件只做「从事实到结构」的跃迁，事实本身不在此重复。

---

## 洞察 I-1：退出码是契约本体，JSON 只是载荷补充

**陈述**：这个 CLI 把「调用结果」整体编码进退出码，8 档状态码各自对应一种可判定的失败语义，结构化输出（`--output json`）承担的是「补充细节」而非「表达结论」的职责。

**证据**：
- F-018~F-022：退出码 0/1/2/3/4/5 在 `internal/clerr` 以常量形式集中定义，8 由 `cmdutil.ExitBlocked` 单点定义，6/7 走 `WithCode(n)` 内联。
- F-023：阻塞至终态的命令（`create` / `video wait` / `video export`）以终态状态决定退出码；单次读取型命令（`video status` / `video export-status`）退出 0 并在载荷中报告状态——同一件事的两种读法被显式区分。
- F-014/F-015：命令行层面的拼写、缺值、枚举越界全部收敛到退出码 2，并在提示里给出最接近的真实旗标名。
- F-103：随仓发布的 AI Skill 契约把「不要自行解析」写成硬约束。

**反常识**：面向 AI 编程助手的 CLI 常见做法是「一律输出 JSON，让模型自己读」。此设计反其道而行——模型只需要 `if [ $? -eq 8 ]` 一行即可分流，JSON 里的长文本是给人看的补充说明。代价是新增失败形态必须新增状态码（6、7、8 三个码就是这样长出来的），状态码空间并非取之不尽。

**行动**：
1. 任何自动化脚本的分支逻辑**只按退出码写**，不 grep stdout 文本。
2. 退出码 2 = 我写错了（改命令行）；3 = 凭证过期（重登）；4 = 等一会重试；5 = 停下（钱不够 / 内部缺陷）；6 = 状态未知（先 `vk video status` 查，不要直接重跑）；7 = 部分成功（预览在、MP4 不在）；8 = 需要人来决定（把 `action_id` 原样带回）。
3. 需要细粒度原因时再开 `--output json`，读 `error.detail`（如 `resend_safe`）与 `next_actions`。

---

## 洞察 I-2：付费动作被拆成「显示条款」与「授予同意」两段，凭据是载荷的哈希

**陈述**：需要花钱的动作不在原地弹出交互提示，而是先把「要花什么钱、作用于哪一次运行」渲染出来交还给调用方，再由调用方把一个与该条款绑定的令牌带回来；令牌是「动作类型 + 决策载荷」的 HMAC 摘要，条款一变，令牌即失效。

**证据**：
- F-024：`cmdutil.Gate` 四级解析——授权声明 → 令牌校验 → TTY 交互 → 写出决策并以退出码 8 结束。
- F-026/F-027/F-028：令牌为 `act_` 前缀 + HMAC-SHA256 前 24 位十六进制，输入是「动作类型 + 0x00 + 规范化载荷」，密钥是 `<config-dir>/action.key` 的 32 字节随机值，规范化对键名排序以保证同一决策恒定哈希。
- F-025/F-030/F-031：两个边界类型各自带一套载荷（`export_confirmation` 带 `credits`，`scene_edit_confirmation` 带 `from`/`to`），恢复命令由 CLI 逐字拼好一并给出。
- F-032：源码自述这是「证据边界」而非安全边界——防的是凭空编造，不是蓄意绕过。

**反常识**：直觉上「防误扣费」应该靠权限系统或二次密码；此设计把防线的位置放在**证据链**上：令牌无法从对话推理中产生，拿到令牌就意味着代码路径已经把真实条款展示给人看过。同时，载荷进哈希这件事让「条款变了旧令牌还能用」这一类漏洞在结构上不可达——代价是任何字段变化（如 `scene_edit` 的 `from` 文本）都会让旧令牌立即作废。

**行动**：
1. 收到退出码 8 时，**先把 `payload` 里的真实数字念给用户听**，再把 `action_id` 与 `resume_command` 原样回传；绝不自行拼 `--confirm` 值，也绝不主动加 `--yes`。
2. 令牌作废是正常路径（条款已变），重新执行一次拿到新 `action_id` 即可，不要试图复用旧值。
3. 自动化流水线的无人值守场景，要么让调用方显式声明 `--yes` / `VIBEKNOW_ASSUME_YES`（自担授权责任），要么接受退出码 8 交给人。

---

## 洞察 I-3：「未知」被拆成可操作的三态，而不是一个布尔

**陈述**：当一次运行的最终状态无法确认时，CLI 不返回「失败」也不返回「成功」，而是返回退出码 6，并在 `error.detail` 中给出 `delivery` 三态与由它唯一决定的 `resend_safe` 布尔——调用方要回答的问题不是「成没成」，而是「重跑会不会再花一次钱」。

**证据**：
- F-033/F-034：`delivery ∈ {submitted, not_submitted, indeterminate}`；`resend_safe` 仅在 `not_submitted` 时为 true，判定式是 `u.Delivery == DeliveryNotSubmitted`。
- F-035：判据落到后端事实——work 行在 init 时创建，后端返回 not_found 即「没有计费发生」。
- F-036：退出码 6 覆盖三种成因：预算耗尽、流无终止事件、任务被暂停。
- F-046/F-048：本地账本为 append-only JSONL，写入是 best-effort，条目缺失只表示「此处未记录」。

**反常识**：`indeterminate`（探针本身失败）刻意给出 `resend_safe: false`——保守方向选的是「等」而不是「重发」。理由写在源码注释里：等一次丢失的运行只损失时间，重发一次没丢失的运行损失用户的钱。另外，「本地没有记录」被反复强调不等于「后端不存在」，这条纪律把「本地缓存」与「权威状态」的边界钉死了。

**行动**：
1. 遇到退出码 6，**先执行 `vk video status` 查一次**再决定；不要直接重跑 `vk create`（可能二次计费）。
2. `resend_safe: true` 才允许重发；`false` 时优先用 `vk video resume` 或等待。
3. 长任务用 `vk jobs list` 找回 `(task_id, session_id)`，显式传 `--session-id` 绕过本地账本缺失。

---

## 洞察 I-4：三条通道各司其职——stdout 是答案、stderr 是过程、磁盘是记忆

**陈述**：CLI 把「给人看的结果」「给程序看的进度」「跨会话的记忆」彻底分成三个通道：stdout 只承载最终结果，stderr 承载带 `vk_event=` 前缀的结构化进度事件，本地账本 `jobs.jsonl` 承载跨进程的运行指针。

**证据**：
- F-040：事件行以 `vk_event=` 前缀写在 stderr，注释明示 stdout 只承载答案。
- F-041：事件通道默认只在 `--output json` 时开启（json 意味着「有程序在读」，散文的听众不存在）；`VIBEKNOW_EVENTS` 可强制开或关；ndjson 模式下事件保留在 stdout 不复制。
- F-042：事件是 advisory——写入失败被丢弃，不让一次已完成的渲染变成失败命令。
- F-037~F-039：输出格式只有 `text`/`json`/`ndjson` 三种，优先级为 `--output` > `VIBEKNOW_OUTPUT` > `text`；源码注释明确拒绝「检测到管道就自动切 JSON」。
- F-043~F-045：预览产物落盘时，源资源 URL 不进入事件载荷，只留内容哈希与类型标识。

**反常识**：多数 CLI 把进度条和结果混在同一 stdout；此设计给出「stdout 纯净」这一更强约束，代价是使用者要同时读两个流才能看到完整过程。`--output json` 才开事件这条默认也反直觉——在 text 模式刻意不产出结构化噪音。

**行动**：
1. 消费结果只读 stdout；需要过程就单独抓 stderr 里的 `vk_event=` 行；两者不要 `2>&1` 合并（合并后无法区分结果与过程）。
2. 想要全程结构化就显式 `--output json`（事件自动开），或设 `VIBEKNOW_OUTPUT=json`。
3. 落盘产物用 `resource_ready` 事件里的 `asset_kind` + 内容哈希去重，不要指望事件里带回 URL。

---

## 洞察 I-5：preset 只描述「长相与声音」，输入与授权永远留在命令行

**陈述**：preset 是一张严格受限的默认值表——14 个允许键全是「每次运行都一样的样式/声音参数」，9 个拒绝键全是「描述本次调用或授予权限的参数」；preset 展开时跳过用户已显式设置的旗标，展开失败一律退出码 2 且发生在任何上传之前。

**证据**：
- F-067：允许键 14 个（mode / script-lock / aspect / bgm / engine / pages / images / theme / language / voice / prompt / avatar / avatar-position / avatar-size）。
- F-068：拒绝键 9 个（export / yes / confirm / from / text / kb-id / async / preview-dir / output），每个附带拒绝理由文案。
- F-069：展开时检查 `pflag` 的 `Changed` 标志，用户已指定的旗标不被覆盖。
- F-070~F-072：`schema_version` 不等于 1 时拒绝读取；顶层拼错的键被 `KnownFields(true)` 拒绝；展开失败是退出码 2，且位于上传动作之前。
- F-065：整条 create 的校验顺序是「preset 展开 → 输入互斥 → async/export 互斥 → mode → aspect → engine → 组合 → …」。

**反常识**：preset 看起来像「命令模板」，实际是「样式档案」。把 `--export` 写进 preset 会让一次普通的样式复用变成一次隐式授权，因此被列入拒绝表。另一处反直觉的设计是「preset 展开排在所有校验最前面」——看起来应该先校验用户输入再叠加默认值，实际顺序保证了下游所有代码看到的是同一份旗标集，preset 值与手敲值不可区分。

**行动**：
1. 建 preset 只放样式与声音参数；输入源（`--from`/`--text`/`--kb-id`）与授权开关（`--export`/`--yes`/`--confirm`）永远在命令行。
2. preset 报「不认识的键」时按 `schema_version: 1` 与允许键名表改写。
3. 复现一个 preset 场景时，命令行上显式传的旗标优先级更高，排查时先看命令行。

---

## 知识地图

### 文档分组（bundle 内 concepts/ 与 examples/ 的分工）

| 分组 | 主题 | 覆盖事实 | 面向读者 |
|---|---|---|---|
| 入门 | CLI 形态、命令树、配置目录、包结构、后端服务划分 | F-001~F-017、F-086~F-094 | 第一次接触本 CLI 的开发者与 Agent |
| 核心 | 退出码契约、付费授权门、输出与事件通道、运行账本与异步 | F-018~F-052 | 需要写自动化脚本的调用方 |
| 进阶 | create 参数域与正交组合、preset 契约、字幕样式与工作修改、预览产物 | F-053~F-080 | 需要定制生成结果的使用者 |
| 运维 | 批量清理安全契约、AI Skill 运行契约、端点全表 | F-081~F-104 | 维护者与集成者 |

### 依赖关系（学习前置）

```
00 CLI 形态与命令树
 ├─→ 01 退出码契约 ──┬─→ 02 付费授权门（exit 8）
 │                   └─→ 03 输出格式与事件通道
 └─→ 04 运行账本、目标解析与异步语义
         ↓
      05 create 参数域与正交组合 ──→ 06 preset 契约
         ↓
      07 字幕样式与工作修改
         ↓
      08 预览产物落盘与去重
         ↓
      09 批量清理安全契约 / 10 AI Skill 运行契约
```

### 学习路径（三条）

- **路径 A（30 分钟上手）**：00 → 01 → 示例 00（首次生成一条视频）→ 01 的退出码速查表。
- **路径 B（写自动化）**：00 → 01 → 02 → 03 → 04 → 示例 01（Agent 安全调用纪律）→ 10（随仓 Skill 的运行契约）。
- **路径 C（定制产出）**：00 → 05 → 06 → 07 → 08 → 示例 02（样式复用与批量维护）。

### E 阶段文档清单（分批计划，每批 ≤7）

**references/（信源先行，第 1 批）**

| 文件 | 内容 | 对应事实 |
|---|---|---|
| `source-code-map.md` | 源码结构地图（目录、包、命令文件与后端服务归属） | F-002~F-009、F-086、F-094 |
| `exit-code-contract.md` | 退出码全表、失败类型、错误详情字段 | F-018~F-023、F-033~F-036 |
| `flag-inventory.md` | 旗标清单（按文件分布、去重口径、create 23 项、video 44 对） | F-010~F-017 |
| `backend-endpoints.md` | 39 个后端端点全表与四服务划分 | F-087~F-091 |

**concepts/（第 2~4 批）**

| 批 | 文件 | 覆盖事实 |
|---|---|---|
| 2 | `00-cli-overview.md` | F-001~F-009、F-086、F-094 |
| 2 | `01-exit-code-contract.md` | F-018~F-023、F-033~F-036 |
| 2 | `02-paid-action-gate.md` | F-024~F-032 |
| 2 | `03-output-and-events.md` | F-037~F-042 |
| 3 | `04-run-ledger-and-async.md` | F-043~F-052 |
| 3 | `05-create-parameter-space.md` | F-053~F-066 |
| 3 | `06-preset-contract.md` | F-067~F-072 |
| 4 | `07-subtitle-and-work-edit.md` | F-073~F-080 |
| 4 | `08-preview-resources.md` | F-043~F-045、F-098~F-100 |
| 4 | `09-bulk-maintenance-safety.md` | F-081~F-085 |
| 4 | `10-ai-skill-contract.md` | F-101~F-104 |

**examples/（第 5 批）**

| 文件 | 场景 |
|---|---|
| `00-first-video.md` | 首次生成一条视频：create → 预览 → export 的完整链路与退出码观察点 |
| `01-agent-safe-automation.md` | Agent 无人值守调用：退出码分流、exit 8 回交、exit 6 处置 |
| `02-style-reuse-and-maintenance.md` | preset 复用样式、字幕调整、kb/jobs 批量维护 |

**index 与 log（第 6 批，最后写）**

- `index.md`（根，含 `okf_version` frontmatter + `{toctree}`）、`concepts/index.md`、`examples/index.md`、`references/index.md`、`log.md`

### 父级索引同步项

- `jishu/ai/products/index.md`：束导航表追加 1 行 + `{toctree}` 追加 `vibeknow-cli/index`；该目录束数/目录数 30 → 31。
- `doc/bundles/index.md`：按 `invoke gates.bundles` 口径核对总束数后同步。

---

## G2 自检

| 判据 | 结果 |
|---|---|
| 洞察条数 ≥3 | 5 条（I-1 ~ I-5） |
| 每条含陈述/证据/反常识/行动四元组 | 5/5 齐备 |
| 每条证据可回溯到 facts.md 的 F 编号 | 5/5 齐备（编号逐条标注） |
| 每条含反常识（与直觉相悖的具体点） | 5/5 齐备 |
| 每条含可执行行动 | 5/5 齐备 |
| 知识地图含分组、依赖关系、学习路径 | 三者齐备 |
| 与上游事实无矛盾 | 逐条核对 F 编号，无冲突 |
