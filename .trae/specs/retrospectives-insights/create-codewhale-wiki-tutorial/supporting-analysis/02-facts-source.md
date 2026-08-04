# CodeWhale 源码事实清单

> 本文档为纯客观事实记录，不包含任何因果分析或价值判断。所有事实均可追溯到源码文件路径。

## 项目元数据

- F-SRC-001: 项目名称为 CodeWhale，在 `Cargo.toml` 的 `[workspace.package]` 中定义，仓库地址为 `https://github.com/Hmbown/CodeWhale`
- F-SRC-002: 项目采用 Rust 语言开发，`rust-toolchain.toml` 指定使用 stable 工具链，`Cargo.toml` 中 `rust-version = "1.88"`，`edition = "2024"`
- F-SRC-003: 项目版本号为 `0.9.4`，在 `Cargo.toml` 的 `[workspace.package]` 中定义
- F-SRC-004: 项目采用 MIT 许可证，`LICENSE` 文件记载版权年份为 2024-2025
- F-SRC-005: 项目根目录包含 `AGENTS.md`（Agent 配置）、`CLAUDE.md`（导入 `AGENTS.md`）、`CHANGELOG.md`、`CODE_OF_CONDUCT.md`、`CONTRIBUTING.md`、`SECURITY.md` 等规范文件
- F-SRC-006: README 存在 9 种语言版本：英文（`README.md`）、简体中文（`README.zh-CN.md`）、日文（`README.ja-JP.md`）、韩文（`README.ko-KR.md`）、印尼文（`README.id.md`）、越南文（`README.vi.md`）、西班牙文（`README.es-419.md`）、葡萄牙文（`README.pt-BR.md`）、俄文（`README.ru.md`）、乌克兰文（`README.uk.md`）
- F-SRC-007: 项目官方网站为 `https://codewhale.net/`，NPM 包名为 `codewhale`，crates.io 包名为 `codewhale-cli`
- F-SRC-008: `Cargo.toml` 中 `[workspace]` 的 `default-members` 包含 3 个 crate：`crates/cli`、`crates/app-server`、`crates/tui`
- F-SRC-009: `Cargo.toml` 中 `[workspace.dependencies]` 列出了 30 个共享依赖，包括 `tokio`、`serde`、`reqwest`、`rusqlite`、`rquickjs`、`axum`、`clap` 等
- F-SRC-010: `Cargo.toml` 中 `[profile.release]` 配置了 `lto = true`、`strip = true`、`codegen-units = 1`
- F-SRC-011: `Cargo.toml` 中包含一个 `[patch.crates-io]` 补丁，用本地 `patches/unicode-width-0.2.2` 替换 `unicode-width` 以修复 CJK 终端宽度计算问题

## 模块架构（crates/）

- F-SRC-012: `crates/` 目录包含 18 个子模块：`agent`、`app-server`、`build-support`、`cli`、`config`、`core`、`execpolicy`、`hooks`、`lane`、`mcp`、`paths`、`protocol`、`release`、`secrets`、`state`、`tools`、`tui`、`workflow`、`workflow-js`
- F-SRC-013: `crates/tui` 是最核心的 crate，`Cargo.toml` 中 `description` 为 "Terminal UI for open-source and open-weight coding models"，其 `Cargo.toml` 中依赖了 `ratatui`（v0.30）、`crossterm`（v0.29）、`rmcp`（v2.2.0）等 TUI 相关库
- F-SRC-014: `crates/tui` 的 `Cargo.toml` 中定义了两个二进制目标：`codewhale-tui`（主程序）和 `codewhale`（通过 `default-run` 指定）
- F-SRC-015: `crates/tui` 的 `Cargo.toml` 中 `[features]` 定义了 `tui`、`web`、`json`、`toml`、`long-running-tests` 五个 feature
- F-SRC-016: `crates/tui` 的 `src/` 目录包含约 200 个 `.rs` 源文件，涵盖 TUI 界面、核心引擎、工具系统、Fleet 管理、LSP 集成、沙箱等多个子系统
- F-SRC-017: `crates/tui` 的 `locales/` 目录包含 15 种语言翻译文件（`ca.json`、`de.json`、`en.json`、`es-419.json`、`fr.json`、`hi.json`、`id.json`、`ja.json`、`ko.json`、`pt-BR.json`、`ru.json`、`uk.json`、`vi.json`、`zh-Hans.json`、`zh-Hant.json`）
- F-SRC-018: `crates/tui` 的 `assets/skills/` 目录包含 35 个内置 Skill 包（如 `batch`、`best-of-n`、`debug`、`review`、`security-review`、`webapp-testing` 等），每个包含 `SKILL.md`
- F-SRC-019: `crates/tui` 的 `tests/` 目录包含 `qa_pty.rs`、`palette_audit.rs`、`skill_cli.rs`、`eval_harness.rs`、`cache_guard.rs` 等测试文件
- F-SRC-020: `crates/cli` 的 `Cargo.toml` 中 `description` 为 "Agentic terminal facade for open-source and open-weight coding models"，定义了 `codewhale` 和 `codew`（短别名）两个二进制目标
- F-SRC-021: `crates/config` 的 `Cargo.toml` 中 `description` 为 "Config schema and precedence model for Codewhale"，`src/` 目录包含 `catalog/`、`route/`、`pricing/` 等子模块
- F-SRC-022: `crates/config` 的 `src/route/` 目录包含 `candidate.rs`、`capabilities.rs`、`descriptor.rs`、`ids.rs`、`offering.rs`、`resolver.rs`、`errors.rs`、`tests.rs`、`conformance_tests.rs` 等文件，实现路由解析
- F-SRC-023: `crates/config` 的 `assets/` 目录包含 `models_dev.bundled.json`，为内置模型目录数据
- F-SRC-024: `crates/agent` 的 `Cargo.toml` 中 `description` 为 "Model/provider registry and fallback strategy for Codewhale"，`src/lib.rs` 中定义了 `ModelFamily` 枚举（含 11 个模型家族：DeepSeek、Anthropic、OpenAI、Google、Meta、Mistral、Qwen、Grok、Cohere、GptOss、Inferencer）和 `ModelInfo`、`ModelResolution` 结构体
- F-SRC-025: `crates/lane` 的 `Cargo.toml` 中 `description` 为 "Lane registry and Runtime backends for Codewhale workflow instances"，`src/` 目录包含 `control.rs`、`lib.rs`、`registry.rs`、`runtime.rs`、`worktree.rs` 五个源文件
- F-SRC-026: `crates/lane` 的 `src/lib.rs` 中注释说明 Lane 是运行中的工作流实例，Runtime 拥有其执行位置（tmux、inline、vm、ci），持久化路径为 `$CODEWHALE_HOME/lanes/<lane-id>.json` 和 `$CODEWHALE_HOME/lanes/logs/<lane-id>.ndjson`
- F-SRC-027: `crates/core` 的 `Cargo.toml` 中 `description` 为 "Core runtime boundaries for Codewhale"，依赖了 `codewhale-agent`、`codewhale-config`、`codewhale-execpolicy`、`codewhale-hooks`、`codewhale-mcp`、`codewhale-protocol`、`codewhale-state`、`codewhale-tools` 等 8 个内部 crate
- F-SRC-028: `crates/workflow` 的 `Cargo.toml` 中 `description` 为 "Typed Workflow IR and validation for Codewhale"，`src/lib.rs` 中注释说明该 crate 刻意停在 Rust 拥有的 IR 边界，运行时工具暴露、工作树应用、重放和模型执行层叠在其上
- F-SRC-029: `crates/workflow` 的 `src/` 目录包含 `fleet_exact.rs`、`fleet_composition.rs`、`fleet_preflight.rs`、`fleet_reasoning.rs`、`fleet_snapshot.rs`、`reasoning_router.rs`、`gates.rs`、`replay.rs`、`redaction.rs`、`elevation.rs` 等 Fleet 与 Workflow 相关模块
- F-SRC-030: `crates/workflow-js` 的 `Cargo.toml` 中 `description` 为 "Dynamic Workflow runtime: sandboxed rquickjs scripts that dispatch Codewhale subagents"，依赖 `rquickjs`（v0.12）作为 JavaScript 运行时
- F-SRC-031: `crates/workflow-js` 的 `Cargo.toml` 中注释明确说明 QuickJS VM 保持单线程，通过 channel 与多线程引擎桥接（参考 `crates/workflow-js`）
- F-SRC-032: `crates/execpolicy` 的 `Cargo.toml` 中 `description` 为 "Execution policy and approval model for Codewhale"
- F-SRC-033: `crates/hooks` 的 `Cargo.toml` 中 `description` 为 "Hook dispatch and notifications support for Codewhale"
- F-SRC-034: `crates/mcp` 的 `Cargo.toml` 中 `description` 为 "MCP server lifecycle and tool proxy compatibility for Codewhale"
- F-SRC-035: `crates/protocol` 的 `Cargo.toml` 中 `description` 为 "App-server protocol frames for Codewhale runtime integrations"
- F-SRC-036: `crates/state` 的 `Cargo.toml` 中 `description` 为 "Session/thread persistence and recovery model for Codewhale"，依赖 `rusqlite`
- F-SRC-037: `crates/secrets` 的 `Cargo.toml` 中 `description` 为 "Secret storage backends for Codewhale, with OS keyring and file fallback"，分别针对 macOS（`keyring` + `apple-native`）、Windows（`keyring` + `windows-native`）、Linux（`keyring` + `linux-native-sync-persistent`）配置了不同依赖
- F-SRC-038: `crates/tools` 的 `Cargo.toml` 中 `description` 为 "Tool invocation lifecycle, schema validation, and scheduler parallelism for Codewhale"
- F-SRC-039: `crates/app-server` 的 `Cargo.toml` 中 `description` 为 "App-server transport for Codewhale runtime integrations"，依赖 `axum` 作为 HTTP 框架
- F-SRC-040: `crates/paths` 的 `Cargo.toml` 中 `description` 为 "User-scoped runtime path authority for Codewhale"，仅依赖 `dirs`
- F-SRC-041: `crates/release` 的 `Cargo.toml` 中 `description` 为 "Shared Codewhale release discovery and version comparison helpers"
- F-SRC-042: `crates/build-support` 的 `Cargo.toml` 中 `description` 为 "Shared build-script helpers for embedding Codewhale build metadata"，无运行时依赖

## 内置宪法

- F-SRC-043: `.codewhale/constitution.json` 文件定义了项目内置宪法，`schema_version` 为 1
- F-SRC-044: 内置宪法中 `authority` 数组定义了五级优先级：用户请求（当前回合）> 本宪法 > 项目法与指令（最近范围优先）> 用户全局偏好 > 记忆与上轮交接
- F-SRC-045: 内置宪法中 `protected_invariants` 定义了 5 条受保护的不变量：保持首轮工具目录头部字节稳定（DeepSeek KV 前缀缓存不变量）、保留旧会话转录重放、仅使用 Stable Rust（edition 2024）、保持 CLI 调度器与 TUI 二进制同步、优先级仅在 BASE_PROMPT 中声明
- F-SRC-046: 内置宪法中 `branch_policy` 为"从 live 分支和 handoff truth 开始，永远不直接提交到 main"
- F-SRC-047: 内置宪法中 `verification_policy` 包含三项：运行对应 crate 的聚焦测试、回读已修改文件、不声标未执行的验证
- F-SRC-048: 内置宪法中 `escalate_when` 定义了三种升级条件：破坏性/难以撤销的操作、更改 provider/auth/config、删除/覆写非自己创建的文件

## 配置文件

- F-SRC-049: `config.example.toml` 文件共约 1364 行，包含完整的配置项定义和注释
- F-SRC-050: `config.example.toml` 中 `provider` 默认值为 `"deepseek"`，列出 30 个可用的 provider 标识符（如 `deepseek`、`openai`、`ollama`、`vllm`、`sglang` 等）
- F-SRC-051: `config.example.toml` 中 `default_text_model` 默认值为 `"deepseek-v4-pro"`
- F-SRC-052: `config.example.toml` 中 `reasoning_effort` 默认值为 `"max"`，可选值包括 `"off"`、`"low"`、`"medium"`、`"high"`、`"max"`
- F-SRC-053: `config.example.toml` 中定义了 20 个 `[providers.*]` 配置段：`deepseek`、`nvidia_nim`、`openai`、`atlascloud`、`wanjie_ark`、`volcengine`、`openrouter`、`xiaomi_mimo`、`novita`、`fireworks`、`siliconflow`、`siliconflow-CN`、`arcee`、`moonshot`、`zai`、`stepfun`、`minimax`、`sglang`、`vllm`、`ollama`、`huggingface`、`deepinfra`、`sakana`、`longcat`、`opencode_go`、`opencode_zen`、`meta`、`xai`、`together`、`qianfan`、`anthropic`、`openmodel`、`openai_codex`
- F-SRC-054: `config.example.toml` 中 `[features]` 段定义了 6 个特性开关：`shell_tool`、`subagents`、`web_search`、`apply_patch`、`mcp`、`exec_policy`（均默认为 `true`）
- F-SRC-055: `config.example.toml` 中 `[tui]` 段定义了 `alternate_screen`、`mouse_capture`、`terminal_probe_timeout_ms`、`stream_chunk_timeout_secs`、`osc8_links` 等 TUI 配置项
- F-SRC-056: `config.example.toml` 中 `[tui]` 段支持 `locale` 配置项，可选值包括 `auto`、`en`、`ja`、`zh-Hans`、`zh-Hant`、`pt-BR`、`es-419`、`vi`、`ko`、`ca`、`de`、`fr`、`id`、`hi`、`ru`、`uk`
- F-SRC-057: `config.example.toml` 中 `[lsp]` 段定义了内置语言服务器映射：rust → rust-analyzer、go → gopls、python → pyright、typescript → typescript-language-server、java → jdtls、php → intelephense、vue → vue-language-server、c/cpp → clangd
- F-SRC-058: `config.example.toml` 中 `[hooks]` 段定义了 11 个生命周期事件：`session_start`、`session_end`、`message_submit`、`tool_call_before`、`tool_call_after`、`mode_change`、`on_error`、`turn_end`、`subagent_spawn`、`subagent_complete`、`shell_env`
- F-SRC-059: `config.example.toml` 中 `[fleet]` 段定义了 `default_trust_level`（默认 `"sandbox"`）、`max_spawn_depth`（默认 3）、以及 `[fleet.exec]` 子段
- F-SRC-060: `config.example.toml` 中 `[workflow]` 段定义了 `automatic`、`auto_start_read_only`、`require_approval_for_writes`、`auto_start_child_limit`（16）、`max_children`（1000）、`max_concurrent`（16）、`max_depth`（2）、`default_token_budget`（120000）
- F-SRC-061: `config.example.toml` 中 `[snapshots]` 段定义了工作区快照功能，默认保留 7 天，最大工作区限制 2 GB
- F-SRC-062: `config.example.toml` 中 `[retry]` 段定义了 `max_retries = 3`、`initial_delay = 1.0`、`max_delay = 60.0`
- F-SRC-063: `config.example.toml` 中 `[context]` 段定义了分层上下文接缝：`verbatim_window_turns = 16`、`l1_threshold = 192000`、`l2_threshold = 384000`、`l3_threshold = 576000`、`seam_model = "deepseek-v4-flash"`
- F-SRC-064: `config.example.toml` 中 `[search]` 段列出了 9 个搜索后端：`duckduckgo`、`bing`、`tavily`、`bocha`、`metaso`、`searxng`、`baidu`、`volcengine`、`sofya`
- F-SRC-065: `config.example.toml` 中 `max_subagents` 默认值为 10，可选范围 1-20

## 文档资源

- F-SRC-066: `docs/` 目录包含约 60 个 Markdown 文档，涵盖架构、配置、安装、模式、Fleet、Skills、MCP、Sandbox、工作流、本地化、运行时 API 等主题
- F-SRC-067: `docs/ARCHITECTURE.md` 记录了当前边界说明（v0.9.1）：`crates/tui` 是 TUI、运行时 API、任务管理器和工具执行循环的实时运行入口，其他 workspace crate 正在逐步拆分
- F-SRC-068: `docs/ARCHITECTURE.md` 记录了 swarm agent 系统在 v0.8.5 被移除，当前活跃的子 agent 表面仅为单个 `agent` 工具
- F-SRC-069: `docs/ARCHITECTURE.md` 记录了 LSP 子系统完全接入引擎的后工具执行路径（`core/engine/lsp_hooks.rs`），在 `File` 写入、编辑和补丁操作后提供内联诊断
- F-SRC-070: `docs/ARCHITECTURE.md` 记录了数据流：交互式会话（用户输入→引擎处理→LLM 响应→流式→工具调用→Hook→结果聚合→渲染）、崩溃恢复与离线队列、工具执行、后台任务、运行时线程/回合时间线、持久化模式门控
- F-SRC-071: `docs/ARCHITECTURE.md` 记录了三个扩展点：添加新工具（在 `tools/` 中创建处理器，在 `tools/registry.rs` 中注册）、添加 MCP 服务器（在 `~/.codewhale/mcp.json` 中配置）、创建 Skill（创建 `SKILL.md` 目录）
- F-SRC-072: `docs/ARCHITECTURE.md` 记录了 6 项关键设计决策：流式优先、工具安全、可扩展性、跨平台、最小依赖、本地优先运行时 API
- F-SRC-073: `docs/ARCHITECTURE.md` 记录了配置文件的目录结构，包括 `~/.codewhale/config.toml`、`~/.codewhale/mcp.json`、`~/.codewhale/skills/`、`~/.codewhale/sessions/`、`~/.codewhale/snapshots/`、`~/.codewhale/tasks/`、`~/.codewhale/audit.log`
- F-SRC-074: `docs/MODES.md` 定义了三种 TUI 模式：Plan（设计优先，只读）、Act（Agent，多步工具使用）、Operate（多任务调度），以及通过 `Tab` 键循环切换
- F-SRC-075: `docs/MODES.md` 定义了四种权限姿态：`suggest`（Ask，默认）、`auto`（Auto-Review）、`bypass`（Full Access）、`never`，通过 `Shift+Tab` 键循环切换
- F-SRC-076: `docs/FLEET.md` 定义了 Fleet 的 CLI 命令集：`init`、`run`、`status`、`inspect`、`logs`、`artifacts`、`interrupt`、`restart`、`resume`、`stop`
- F-SRC-077: `docs/FLEET.md` 定义了两种 Fleet 类型：Exact Fleet（冻结每个 worker 的 provider、model、reasoning 和权限上限）和 Reasoning Router（可复用服务，仅选择推理层级）
- F-SRC-078: `docs/FLEET.md` 定义了四个信任级别：`sandbox`（默认）、`local`、`remote-verified`、`operator`
- F-SRC-079: `docs/FLEET.md` 定义了 Fleet 的验证上限：单次 Workflow 运行最多 1000 个 worker agent、最多 16 个同时活跃的 worker、最多 5 个递归 Fleet 环（默认用户配置为 2）
- F-SRC-080: `docs/FLEET.md` 定义了 6 种 Fleet 告警事件类型：`stale`、`restart_exhausted`、`needs_human`、`budget_exceeded`、`verifier_failed`、`run_completed`
- F-SRC-081: `docs/FLEET.md` 定义了 Fleet 管理器运行手册的 4 种 worker 分类：`transient failure`、`task failure`、`verifier failure`、`needs-human`
- F-SRC-082: `docs/GUIDE.md` 记录了安装路径：npm（`npm install -g codewhale`）、Cargo（`cargo install codewhale-cli --locked` + `cargo install codewhale-tui --locked`）、Homebrew（`brew tap Hmbown/deepseek-tui`）、Docker
- F-SRC-083: `docs/SKILLS.md` 定义了 Skills 管理器四层架构：Root Catalog（单一来源和所有权）、Audit（只读磁盘清单）、Mutation Controller（安装/导入/更新/移除/信任的唯一写入者）、Skills Manager View（TUI 视图）
- F-SRC-084: `docs/SKILLS.md` 定义了可写根目录（`<workspace>/.codewhale/skills/` 和 `~/.codewhale/skills/`）和只读兼容根目录（`.claude/skills`、`.cursor/skills`、`.opencode/skills` 等）
- F-SRC-085: `docs/CONFIGURATION.md` 记录了配置文件的多个指令层面：内置全局宪法、用户全局宪法（`/constitution` 或 `/setup` 管理）、仓库本地宪法（`.codewhale/constitution.json`）、`AGENTS.md`（跨 agent 项目指令）、Memory 和 handoffs
- F-SRC-086: `docs/INSTALL.md` 记录了支持平台矩阵：Linux（x64、arm64、riscv64）、macOS（x64、arm64）、Windows（x64、arm64）、Android/Termux（arm64，预览阶段），以及 FreeBSD/OpenBSD（需从源码构建）
- F-SRC-087: `docs/INSTALL.md` 记录了 Linux x64 发布资产自 v0.8.65 起为静态 musl 构建，Linux arm64 为 GNU libc 构建

## 其他工程结构

- F-SRC-088: `extensions/` 目录包含一个 VS Code 扩展（`vscode/`），包含 `runtime.ts`、`status.ts` 等源文件
- F-SRC-089: `npm/` 目录包含 `codewhale/`（NPM 包）、`deepseek-tui/`（旧品牌名 NPM 包）、`runtime-sdk/`（运行时 SDK NPM 包）三个子目录
- F-SRC-090: `web/` 目录包含一个完整的 Next.js 网站项目，含 `app/`（路由页面）、`components/`（React 组件）、`lib/`（工具函数）等目录
- F-SRC-091: `scripts/` 目录包含 `installer/`（NSIS 安装脚本）、`release/`（发布脚本）、`ohos/`（OpenHarmony 脚本）、`remote-smoke/`（远程冒烟测试）等子目录
- F-SRC-092: `.github/workflows/` 目录包含 14 个 CI/CD 工作流文件：`ci.yml`、`nightly.yml`、`release.yml`、`pr-gate.yml`、`issue-gate.yml`、`web.yml`、`ohos.yml`、`auto-tag.yml`、`cargo-deny.yml`、`dco.yml`、`stale.yml`、`sync-cnb.yml`、`triage.yml`、`claude.yml`
- F-SRC-093: `fleets/` 目录包含 `stopship.toml` 和 `v0868-stopship.toml` 两个 Fleet 配置文件
- F-SRC-094: `.devcontainer/` 目录包含 `Dockerfile` 和 `devcontainer.json`，支持 VS Code Dev Container 开发环境
- F-SRC-095: `nix/` 目录包含 `package.nix` 和一个 `flake.nix` 文件，支持 Nix 包管理
- F-SRC-096: 项目根目录 `Dockerfile` 支持 Docker 容器化部署
- F-SRC-097: 项目根目录 `package.json` 和 `package-lock.json` 表明项目也包含 Node.js 层面的脚本和依赖管理
- F-SRC-098: `docs/rfcs/` 目录包含 3 个 RFC 文档：`1364-hooks-lifecycle.md`、`3209-workrooms.md`、`REMOTE_SETUP_DESIGN.md`
- F-SRC-099: `docs/skills/` 目录包含两个示例 Skill：`gh-file-issue/SKILL.md` 和 `gh-find-prs/SKILL.md`
- F-SRC-100: `docs/evidence/` 目录包含 `hotbar-qa-matrix.md`，为 QA 验证证据文档