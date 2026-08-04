---
id: "echobird-wiki-advanced-pages"
title: "高级功能模块"
source: "echobird-source-wiki-learning"
category: "learning"
tags: ["echobird", "advanced", "aipulse", "aicareer", "skills", "ssh", "usage"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "EchoBird 高级功能模块（AiPulse/AiCareer/MotherAgent/Skills/SSH/用量查询/自更新）的实现要点"
last_verified: "2026-08-04"
wiki_version: "1.0"
---

# 08 高级功能模块

除四大核心场景（安装修复 Agent / 一键本地大模型 / 我的 AI 项目 / 应用管理器）外，EchoBird 还内置了一批**高级功能模块**，用于把 Agent 工具从"配置器"升级为"日常信息中枢"。本章基于前端 `src/pages/` 与后端 `src-tauri/src/services/` 下的真实源码整理，覆盖 AiPulse 新闻流、AiCareer 职业统计、MotherAgent 母亲 Agent、Skills 技能模块、SSH 客户端、用量查询、自更新与反馈八个模块。

先厘清两个贯穿本章的概念：

- **ReAct 循环（Reason → Act → Observe → Repeat）** 是一种让大模型自主决策的对话范式：模型先"思考"（Reason）要调用哪个工具，再"执行"（Act）该工具，读取工具返回的"观察"（Observe）结果，然后循环往复直到完成任务。MotherAgent 的对话内核即基于此。
- **用量查询（Usage Query）** 指调用各模型平台自身的 API 接口，读取账户的余额、额度消耗百分比、重置时间等数据，在应用内以进度条/数字形式展示给用户。

## 8.1 AiPulse（AI 新闻流）

AiPulse 是 EchoBird 的 **AI 资讯聚合页**，位于 `src/pages/AiPulse/AiPulse.tsx`。它把每日 AI 新闻与明星项目以"信息流"形式呈现，并按语言提供两套并行的数据源：

- **中文源（zh）**：来自 SuYxh 的 `ai-news-aggregator` 双语聚合仓库，约 6000 条（多为国内内容），文件 `latest-7d.json`；
- **英文源（en）**：由 `scripts/build_en_pulse.py` 从 Hacker News Algolia + AI 实验室 RSS + GitHub Trending 自建，仅美国/全球来源，文件 `latest-7d-en.json`。

**镜像链（mirror chain）** 是 AiPulse 网络层的核心设计：为兼顾国内可达性与全球速度，每个源都配置了 4 个镜像（中文源为 `echobird.ai` → GitHub Pages → jsDelivr CDN → GitHub raw），`fetchOneFeed` 会按顺序尝试，每个镜像超时 10 秒即自动切换下一个，并记录"首选镜像"下标以便后续请求优先命中。英文源主镜像失败时还会回退到中文源（取其英文子集），保证页面永不空白。

**双视图划分** 依据 URL 特征判断条目是"新闻"还是"明星项目"：`isProjectItem` 检查是否命中 `github.com` 仓库、`huggingface.co/{spaces|models|datasets}`，或 source 中出现 `Trending`/`开源` 标记。新闻与项目是互斥分区，每个条目恰好落入一个 Tab。

**归档（archive）** 是其真正区别于普通 RSS 阅读器的能力：因为上游只提供 7 天滑动窗口，错过即永久丢失，所以每次抓取都会把条目**按本地日期扇出（fan-out）**到磁盘归档，见 `pulse_archive.rs`：

- 磁盘布局为 `~/.echobird/pulse/YYYY/MM/DD_{lang}.json`，每个文件含 `schema`、`date`、`lang`、`item_count`、`items` 字段；
- 写入采用**原子写**（先写 `tmp` 文件再 `rename`），部分写入不会留下半解析状态；
- 按 URL 去重合并（新条目覆盖旧条目），排序键使用 `effective_ts`（带"未来时间戳守卫"），防止部分聚合商把北京时间误标为 UTC 导致条目落入"未来日期"文件；
- 读取 `load_all` 会自愈：丢弃日期晚于今天超过 1 天的文件，避免历史坏数据长期占据去重窗口。

前端 `AiPulseProvider` 通过 `pulse_load_all` / `pulse_save` 两个 Tauri 命令与 Rust 归档交互。相比旧版 localStorage 缓存（上限 3000 条且 WebView 重置即清空），磁盘归档**无上限、不依赖 WebView**，并会自动把旧 localStorage 数据一次性迁移到磁盘。

## 8.2 AiCareer（AI 职业）

AiCareer（"我的 AI 生涯"）是跨工具的**会话历史聚合 + 贡献统计**模块，位于 `src/pages/AiCareer/`，后端逻辑在 `ai_career.rs`。它直接扫描五个"一等公民工具族"在磁盘上的会话存储，不依赖 EchoBird 自身的工具检测，从而把桌面版与 CLI 版会话合并到同一家族：

| 家族 | 数据根目录 | 存储形态 | 扫描深度 |
|------|-----------|---------|---------|
| Claude | `~/.claude/projects` | JSONL | 2 |
| Codex | `~/.codex/sessions` | JSONL rollout | 4 |
| OpenCode | `~/.local/share/opencode` | SQLite（`opencode.db`） | 直接读库 |
| Hermes | `<HERMES_HOME>/state.db` | SQLite（`state.db`） | 直接读库 |
| MiMo | `~/.local/share/mimocode` | SQLite（`mimocode.db`） | 直接读库 |

两种消费界面：

1. **分页历史列表**（`AiCareerPanel.tsx`）：一次只加载一个家族，每页 30 条，滚动到哨兵节点时通过 `IntersectionObserver` 增量拉取；标题从真实用户消息提取，并过滤掉工具注入的系统标签（如 `<environment_context>`、`# AGENTS.md`、Claude 压缩摘要前缀等），并为 Codex Desktop 剥离"# Files mentioned by the user"前缀。
2. **贡献热力图 ContributionHeatmap**（`ContributionHeatmap.tsx` + `heatmapData.ts`）：30 周 × 7 天的网格，`buildGrid` 生成单元格，`levelFor` 用**平方根缩放**将消息数映射到 0–4 级色阶（类似 GitHub 热力图，避免单日爆发压扁其余格子）。网格入场动画由 `requestAnimationFrame` 逐帧驱动（刻意不用 CSS `@keyframes`，因为部分引擎对 `background-color` 动画到 `var()` 值会静默失败）。

页面顶部还展示五项统计（`deriveStats`）：总会话数、总消息数、活跃天数、当前连续天数、最长连续天数。后端 `message_heatmap()` 以 210 天为回看窗口，对历史 JSONL 文件按 mtime 做**磁盘计数缓存**（`~/.echobird/cache/ai-career-heatmap-counts.json`），文件未变则跳过重扫；SQLite 家族则直接查库。`estimate_token_bytes()` 用各会话文件字节数估算"约 N tokens"（前端按 `TOKENS_PER_BYTE = 12` 放大），对不返回真实用量的第三方模型尤为有用。

## 8.3 MotherAgent（母亲 Agent）

MotherAgent（母亲 Agent）模块位于 `src/pages/MotherAgent/`，是 EchoBird 的**通用 Agent 对话/编排页**——用户可与任意已配置模型对话，并让 Agent 在本地或远程服务器上执行工具，而不再局限于某个具体编码工具。

**对话内核**是后端 `agent_loop.rs` 实现的 **ReAct 循环**，前端通过 `MotherAgentProvider.tsx` 订阅事件流：

- 事件类型（`AgentEvent`）包括 `text_delta`（流式文本）、`thinking`（思考，前端刻意不展示）、`tool_call_start` / `tool_call_args` / `tool_result`（工具调用全程）、`done` / `error` / `state`；
- 会话有**防失控保险**：`MAX_TOOL_LOOPS = 150` 作为工具调用次数的兜底上限（不是任务预算）；`MAX_CONTEXT_BYTES = 300_000`（约 300KB）按字节裁剪上下文，避免超大工具结果撑爆内存；`recent_calls` 环形缓冲（容量 8）检测连续重复的 `(工具, 参数)` 调用，重复第 3 次即注入"你在循环"的合成结果打断模型。

**协议自适应**：模型请求的协议由配置决定，绝不猜测——只有当模型带 `anthropicUrl`（明确支持 `/v1/messages`）时才走 Anthropic Messages API，否则走 OpenAI 兼容的 `base_url`。每个会话只固定一种协议，中途不切换。

**Parasite 模式（寄生模式）**：当用户选择"寄生"到已安装的 Claude Code CLI（`parasiteAgent === 'claudecode'`，当前唯一受支持 id）时，本轮对话不再由 EchoBird 自己的 `agent_loop` 处理，而是委托给 `claude` 子进程执行，其工具/记忆/模型配置全部归属 Claude Code 自身。此模式下服务器列表被置灰（`parasiteLocked`），因为不会替它发起 SSH。

**会话持久化**：`useChatPersistence` 会把每服务器对话按 `agent_<serverId>` 键写入磁盘，`toDisk`/`fromDisk` 双向映射，工具调用以 JSON 形态保存以重建时间线；`clearChat` 同时清空本地与后端 `reset_agent`。

## 8.4 Skills（技能模块）

Skills 模块位于 `src/pages/Skills/Skills.tsx`，是**面向"如何用 AI 交付"的精选技能清单**（偏 vibe coding、Agent 编排、内容创作、AI 创业实用方向，而非研究/训练 LLM）。它有两层内容：

1. **官方精选目录**：以 JSON 发布在 `echobird.ai/skills`（CF Worker），GitHub raw 的 `docs/skills/{cn,en,zh-Hant,ja}.json` 为镜像，6 小时缓存窗口；前端以 `SKILLS_MIRRORS` 镜像链抓取，并按语言（en/zh-Hans/zh-Hant/ja）分流。内置的 `CN_SKILLS`/`EN_SKILLS` 数组作为离线兜底。
2. **用户收藏**：通过 `skill_manager.rs` 提供 CRUD，持久化到 `~/.echobird/config/skills.json`。`SkillConfig` 含 `id`（`s-xxxxxx` 格式）、`name`、`url`、`category`、`description`、`created_at`；`add_skill`/`delete_skill`/`update_skill` 三个函数支撑"收藏 → 编辑 → 删除"全流程。

**两个 Tab**：`hot`（热门，官方目录按语言过滤后 Fisher-Yates 洗牌，避免 22 条精选总以固定顺序出现）与 `fav`（我的收藏，含添加/编辑/删除）。卡片会为 GitHub 仓库 URL 预抓取星标数（`fetchGithubStars` 在 localStorage 缓存 7 天），添加时可用 `fetchRepoInfo` 从仓库自动填充名称与描述。

**default-skills 参考**：内置工具 `reversi` 的 `tools/reversi/default-skills/` 演示了"以 SKILL.md 形式打包技能"的范式——每个技能目录含一个 `SKILL.md`，frontmatter 记录 `name` 与 `description`，正文为可注入模型的指令（如 `reversi-master/SKILL.md` 教 AI 按角落/边/X-square 等策略下黑白棋）。这类"技能即 Markdown 指令"的思路与 Skills 模块的收藏/分类理念一脉相承。

## 8.5 SSH 客户端

SSH 客户端位于 `src-tauri/src/commands/ssh_commands.rs`，让 MotherAgent 的 Agent 能连接本地或远程服务器执行命令。它基于 `async_ssh2_tokio` 异步 SSH 库，维护一个**连接池**：

```rust
pub type SSHPool = Arc<Mutex<HashMap<String, Client>>>;
```

`create_ssh_pool` 创建以服务器 ID 为键的连接池。关键能力：

- **连接测试** `ssh_test_connection`：连接后执行 `uname -a` 验证命令执行能力，并对系统本地化错误码做**清洗**（如 `os error 11001` → "DNS 解析失败"、`10060/10061` → "超时或被拒"、`10013` → "防火墙拒绝"），避免中文 Windows 上报原始错误码；
- **自动重连** `auto_connect_ssh`：当池中无连接或健康检查（`echo ok` 3 秒超时）失败时，从磁盘读取凭据并重连，供 `agent_tools` 在 Agent 需要时按需调用；
- **持久化**：服务器列表存于 `~/.echobird/config/ssh_servers.json`，密码以 `enc:v1:` 前缀加密存储（`model_manager::decrypt_key_for_use` 解密），前端 `MotherAgentPanel.tsx` 的服务器管理弹窗支持"测试连接 + 加密/解密 + 增删改"。

前端服务器列表固定把 `local`（127.0.0.1）放在首位，之后是用户添加的 SSH 服务器；切换到服务器后，Agent 的 `server_ids` 参数会携带该服务器 ID，指挥后端在远程执行工具。侧栏还内置"SSH 指南"手风琴，覆盖 Cloud Server / Windows / macOS / Linux / Android(Termux) / iOS(iSH) 六类开启 SSH 的步骤。

## 8.6 用量查询

用量查询模块位于 `src-tauri/src/services/usage_providers/`，通过统一的 `UsageProvider` trait 抽象，让 EchoBird 能查询 **11 个模型平台**的 API 用量/余额。核心数据结构：

- `UsageQuota`：`percentage`（消耗百分比 0-100）、`reset_at`（重置时间戳 ms）、`balance`/`balance_unit`（可选，用于 DeepSeek 等展示剩余余额的平台）；
- `ModelUsageData`：一组 `quotas` + `last_updated`；
- `UsageResult`：`success` + `data` + `error` 三态封装。

调度入口 `detect_provider(base_url)` 按 `base_url` 匹配平台，`query_model_usage` 统一装配。每个平台一个模块，实现 `query_usage(api_key, base_url)`、`can_handle(base_url)`、`name()` 三个方法。11 个提供方一览：

| 提供方 | 模块 | 查询 URL | 返回内容 |
|--------|------|---------|---------|
| DeepSeek | `deepseek.rs` | `GET api.deepseek.com/user/balance` | 账户余额（`total_balance` + 币种），百分比置 0 改显余额 |
| Kimi | `kimi.rs` | `GET api.kimi.com/coding/v1/usages` | 5 小时窗口 + 每周额度（`limit`/`remaining`/`resetTime`） |
| MiniMax | `minimaxi.rs` | `GET api.minimaxi.com/v1/usage`（或 `.io`） | 用量配额 |
| Volcengine | `volcengine.rs` | ARK API Sig V4 签名 POST | 会话/周/月三级额度（AK/SK 方案，需 `volc_aksk.json`） |
| Novita | `novita.rs` | `GET api.novita.ai/v3/user/balance` | 账户余额 |
| OpenRouter | `openrouter.rs` | `GET openrouter.ai/api/v1/credits` | 信用额度（`total_usage`/`total_credits` 算百分比） |
| SiliconFlow | `siliconflow.rs` | `GET api.siliconflow.cn/v1/user/info`（或 `.com`） | 用户信息/额度 |
| StepFun | `stepfun.rs` | `GET api.stepfun.com/v1/accounts` | 账户额度 |
| Sub2API | `sub2api.rs` | 兜底：`{host}/v1/usage` | 通用中转站用法（`can_handle` 恒真，排最后） |
| ZenMux | `zenmux.rs` | — | 聚合平台用量 |
| Zhipu | `zhipu.rs` | `GET open.bigmodel.cn/api/paas/v4/usage`（或 `api.z.ai`） | 智谱用量 |

几个值得注意的实现细节：

- **Volcengine 特殊处理**：它不用推理 API Key，而是用**按模型（internal_id）存储的 AK/SK**（`volc_aksk.json`，AES 加密），走 `query_usage_for_model` 绕过空 Key 检查；请求需用 AWS Sig V4 变体对 `ark.{region}.volcengineapi.com` 签名，并依次尝试 6 个 Action × 6 种 body 变体，遇认证错误立即停止（避免用坏 Key 空烧 36 次调用）。
- **Sub2API 兜底位置**：`can_handle` 恒为 true，因此必须排在 `detect_provider` 最后，专门承接通用中转/聚合站。
- 前端会识别 `balance` 字段：若平台返回余额（如 DeepSeek）则显示余额而非百分比进度条。

## 8.7 自更新

自更新位于 `src-tauri/src/services/self_update.rs`，是**Windows 专属的 DIY 更新流程**：从 GitHub Releases **下载安装包 → 启动官方安装向导 → 退出应用**，让安装器覆盖当前运行的 exe。

与 `tauri-plugin-updater` 静默更新方案不同，此流程**不做签名校验、不做静默安装**，而是让用户手动点完官方安装器（后者需要签名密钥 + 更新清单，暂未采用）。非 Windows 平台不提供应用内更新，调用方改为打开下载页。

Windows 实现要点：

- 目标资产固定为 `EchoBird_{version}_Windows_x64-setup.exe`，来源仅 GitHub Releases；
- `pick_fastest` 用 6 秒超时的 `Range: bytes=0-2047` 小请求探测各候选源，返回最快的那个；
- 下载过程通过 `self-update-progress` 事件向设置弹窗报告进度（`speed_test` / `downloading` / `launching` / `error`）；
- 下载后用**字节数校验**防御被截断的包（无签名/哈希校验时"总字节数不匹配即拒绝"是唯一完整性防线）；
- 安装器以 `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP` 标志**分离启动**，随后延迟 600ms 优雅退出（`app.exit(0)`），使自身 exe 解锁、让安装器替换。

## 8.8 反馈

反馈页面位于 `src/pages/Feedback/Feedback.tsx`，是**引导用户抓取故障日志并提交到 GitHub Issue** 的两步流程：

1. **复制日志**：前端调用 `readLogTail(30)` 读取 `<app_log_dir>/echobird.log` 的最后 30 行后端日志并复制到剪贴板（与开发模式 CMD 窗口同源）。30 行足够覆盖一次用户操作及其失败轨迹，又不至于撑爆 issue 正文。
2. **提交问题**：默认打开 GitHub Issues 新建页；国内（zh-Hans）用户因 GitHub 常被墙，改提供 **Gitcode 镜像** `gitcode.com/edison7009/EchoBird/issues/create`；非中文用户则回退到复制支持邮箱 `hi@echobird.ai`（复制邮箱而非触发 `mailto:`，避免多数用户未配置桌面邮件客户端时弹系统选择器）。

页面按语言（`isZh = locale === 'zh-Hans'`）决定回退渠道，并附带网络提示说明不同地区可达性。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [07 工具注册表](./07-tool-registry.md) | [README](./README.md) | → [09 快速上手指南](./09-quickstart.md) |