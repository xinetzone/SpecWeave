---
type: Research-Facts
id: "vibeknow-video-expert-20261021-facts-technical-cli"
topic: vibeknow-technical-cli
report: retrospective-vibeknow-video-expert-20261021
appendix: A
collected_date: 2026-10-21
security_level: public
source: "公开信源（npm registry 页面 vibeknow-cli、GitHub 仓库 vibeknow/cli 的 README 原文）；本文件为 VibeKnow 视频专家全面调研报告（session=sc-20261021-vibeknow-research）R 阶段技术维度事实附录，条目编号与正文引用一致"
---

# VibeKnow 技术与 CLI · 客观事实清单

采集日期：2026-10-21。本清单仅陈述可验证的公开事实，不含因果与判断。来源优先级：官方仓库 README > npm registry 元数据。

## A. 发布形态与工程基线

| 编号 | 事实 | 来源URL | 访问日期 |
|---|---|---|---|
| TEC-01 | 官方 CLI 以 Go 编写，源码构建要求 Go v1.25 及以上；npm 仅为分发渠道，仓库提供 `make build` / `make test`（带 race detector）/ `make lint`（go vet）三条开发命令。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-02 | npm 包 `vibeknow-cli` 当前版本为 0.9.2，页面标注 18 个历史版本、0 个依赖项、发布于「一个月前」、许可证为 MIT。 | https://www.npmjs.com/package/vibeknow-cli | 2026-10-21 |
| TEC-03 | CLI 源码仓库位于 github.com/vibeknow/cli，README 同时提供中文版（README.zh.md）与英文版两个入口。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-04 | CLI 定位表述为「one command, zero editing skills」，一条 `vibeknow create --from report.pdf` 命令覆盖文档解析、脚本生成、TTS、分镜设计、渲染与打包全流程。 | https://github.com/vibeknow/cli | 2026-10-21 |

## B. Agent Skills 与运行时兼容

| 编号 | 事实 | 来源URL | 访问日期 |
|---|---|---|---|
| TEC-05 | 仓库 `skills/` 目录以开放的 Agent Skills 规范（agentskills.io）提供三个技能：vibeknow-core（profile 配置、鉴权管理、环境诊断、凭证配置）、vibeknow-create（端到端视频生成、状态等待下载、声音选择、异步流程）、vibeknow-doc（文档上传、解析状态轮询、文档获取）。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-06 | 技能安装命令为 `npx skills add vibeknow/cli`，支持 `-g` 全局安装与 `--skill <name>` 单技能安装；工具自动探测本地已安装的 agent 并把技能 symlink 进各自 skill 目录，README 声明兼容 55+ AI agent 运行时（Claude Code、Cursor、OpenCode、GitHub Copilot、Gemini CLI 等）。 | https://github.com/vibeknow/cli ; https://www.npmjs.com/package/vibeknow-cli | 2026-10-21 |

## C. 认证与凭证

| 编号 | 事实 | 来源URL | 访问日期 |
|---|---|---|---|
| TEC-07 | 认证采用浏览器 Device Flow，两阶段 agent 流程：`auth login --no-wait` 立即向 stdout 输出 JSON（`device_code`、`user_code`、`verification_uri`、`expires_in: 900`、`hint`），宿主读取 URL 后由人类在浏览器批准，代理再用 `--device-code` 续轮询；README 注明交互次数为「每个 token 一次」而非「每个命令一次」。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-08 | 凭证来源优先级为 `VIBEKNOW_TOKEN` 环境变量最高，其次为 OS 原生 keychain 存储的令牌；PAT 支持经 stdin 传入（`--with-token`），用于 CI 场景。 | https://github.com/vibeknow/cli ; https://www.npmjs.com/package/vibeknow-cli | 2026-10-21 |
| TEC-09 | 环境变量共四个：`VIBEKNOW_TOKEN`（全服务 JWT）、`VIBEKNOW_CONFIG_HOME`（覆盖配置目录，默认 `~/.config/vibeknow`）、`VIBEKNOW_TRACE`（置 1 显示 trace ID）、`VIBEKNOW_DEBUG`（置 1 开启 verbose 日志）。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-10 | `auth status --output json` 输出当前身份、令牌来源、profile 与过期状态，其中包含 `pending_authorization` 状态标记。 | https://www.npmjs.com/package/vibeknow-cli | 2026-10-21 |

## D. 流水线、进度流与退出码

| 编号 | 事实 | 来源URL | 访问日期 |
|---|---|---|---|
| TEC-11 | 视频生成以 SSE 流式返回四阶段进度：outline → tts → render → publish，同时提供人类可读进度条与机器可读 NDJSON 两种形态。 | https://github.com/vibeknow/cli ; https://www.npmjs.com/package/vibeknow-cli | 2026-10-21 |
| TEC-12 | `vibeknow video wait --for 90s --output json` 在等待预算耗尽时以退出码 6 返回，理由为 `wait_budget_expired`，语义为「继续等待」；渲染失败以退出码 7 返回。 | https://github.com/vibeknow/cli ; https://www.npmjs.com/package/vibeknow-cli | 2026-10-21 |
| TEC-13 | `--async` 模式在后端确认 run 已 live 后即返回（秒级），渲染在 CLI 断开后于服务端继续；输入错误或积分不足等立即拒绝由 `--async` 自身以非零退出码报告，README 声明「打印出 task_id 即代表 run 确已启动」。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-14 | `vibeknow create` 的编排路径为「文档上传 → 视频生成（SSE）→ 导出与下载」，后端为多服务架构，各服务按领域划分（auth、documents、video pipeline 等）。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-15 | 流水线默认停在 preview 阶段，输出形如 `share_url=https://vibeknow.com/share/tok_abc` 的浏览器可播放分享地址；导出 MP4 需另行执行 `vk video export 42 --session-id sess_xxx`，README 标注耗时数分钟并产生额外积分消耗。 | https://github.com/vibeknow/cli | 2026-10-21 |

## E. 视频模式与生成引擎

| 编号 | 事实 | 来源URL | 访问日期 |
|---|---|---|---|
| TEC-16 | CLI 暴露的视频模式包括：`--mode replica`（PPT/PDF 逐页成片）、`--mode image`（每页一张 AI 插图，配 `--pages 8`）、`--mode handdraw`（手绘动画，README 注明过程中出现静默属正常）。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-17 | `--script-lock` 以逐字方式朗读原文而不改写为脚本，该开关可叠加在任何模式之上；其前身 `--mode script` 仍可用但会输出弃用警告。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-18 | 风格与语言随模式一并生效：`vk theme list --mode image` 可浏览某模式的风格目录，`--theme <theme_id>` 指定风格，`--language en-US` 同时指定脚本与旁白语言。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-19 | 生成引擎可选：`--engine agent` 对应 v=2 引擎（README 标注「与前端开关同 parity」），`--engine pipeline` 对应 v=3 流水线引擎（默认）。 | https://github.com/vibeknow/cli | 2026-10-21 |

## F. 数字人、字幕与知识库

| 编号 | 事实 | 来源URL | 访问日期 |
|---|---|---|---|
| TEC-20 | 数字人以 `--avatar sys_<id>`（系统预设）或 `--avatar ua_<id>`（用户自训）指定，可配 `--avatar-position` 与 `--avatar-size`；README 注明数字人不可与 `--mode handdraw` 或 `--engine agent` 同用。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-21 | 数字人场景下 `video export` 被拒时可执行 `vk video avatar-retry`（README 标注为免费）后重新导出。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-22 | 字幕可读性被定义为组合效果而非独立设置项：`vk subtitle presets` 列出设计团队出厂预设（白字·黑底 `rgba(8,8,12,0.68)` 底板无描边；白字·黑边 `Noto Sans SC 600` 3px 描边无底板），`vk subtitle fonts` 列出允许使用的字体族；单项参数仍可在预设之上叠加。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-23 | 知识库清理命令为 `vk kb list --output json --size 5` 与 `vk kb prune --pattern 'vibeknow-cli-*'`；prune 默认为 dry-run，须追加 `--yes` 才实际删除。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-24 | 单镜头改写能力为 `vk video edit --scene N --script`，仅重写指定场景脚本并重渲；`--script-only` 仅重做配音，README 标注其更省积分。 | https://www.npmjs.com/package/vibeknow-cli | 2026-10-21 |

## G. Profile、诊断与安全设计

| 编号 | 事实 | 来源URL | 访问日期 |
|---|---|---|---|
| TEC-25 | Profile 机制支持多环境（prod/staging/dev）、per-service 端点覆盖与独立鉴权；示例命令 `vibeknow profile add dev --endpoint-figlens http://localhost:<port> --credential-ref vibeknow.dev --trust dev --is-production=false` 同时声明端点、凭证引用、信任级别与生产标记。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-26 | `vibeknow doctor` 提供环境诊断，覆盖配置目录、keychain、locale 与 endpoint 可达性检查。 | https://github.com/vibeknow/cli ; https://www.npmjs.com/package/vibeknow-cli | 2026-10-21 |
| TEC-27 | 安全设计包含五项：OS 原生 keychain 凭证存储、ANSI 转义字符清理、verbose 日志中的凭证脱敏、非生产端点的信任边界，以及多服务架构下的独立鉴权。 | https://github.com/vibeknow/cli ; https://www.npmjs.com/package/vibeknow-cli | 2026-10-21 |
| TEC-28 | 原始 API 逃生通道为 `vibeknow api call --service <service> --method <METHOD> --path /v1/<resource> [--body '<json>' \| --body @file]`，可直连后端任意端点。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-29 | 输出格式默认为人读文本并按 TTY 自动探测，非 TTY 管道环境自动切换为 JSON；显式 `--output json` 可覆盖。 | https://github.com/vibeknow/cli | 2026-10-21 |

## H. 预设包与扣费防护

| 编号 | 事实 | 来源URL | 访问日期 |
|---|---|---|---|
| TEC-30 | preset 是存放风格开关的 YAML 文件（默认目录 `~/.config/vibeknow/presets/brand.yaml`），内容覆盖 mode、aspect、theme、voice、language、bgm 与 avatar 位置；preset 仅提供默认值，命令行显式参数优先。 | https://github.com/vibeknow/cli | 2026-10-21 |
| TEC-31 | preset 不允许携带 `--export`、`--yes`、`--confirm` 三个开关，README 明确该约束的目的是「打开他人 preset 永远不会批准一笔扣费」；完整契约置于仓库 AGENTS.md。 | https://github.com/vibeknow/cli | 2026-10-21 |
