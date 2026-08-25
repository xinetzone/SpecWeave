# agency-agents 事实清单

> R阶段事实采集。源码路径：d:\AI\.chaos\libs\agency-agents\
> 采集日期：2026-08-23

## 项目概述

- F-001: 项目名称为"The Agency"，是一个 AI 代理人格集合，每个代理都是具有专业技能、个性和可交付成果的专家 — 源码：`README.md:1,21`
- F-002: 项目源于 Reddit 帖子和数月迭代，提供专业化、个性驱动、可交付成果聚焦、生产就绪的代理 — 源码：`README.md:21-26`
- F-003: 提供原生桌面应用（macOS/Linux/Windows），可浏览整个代理名册并一键安装到 Claude Code、Cursor、Codex、Gemini 等工具 — 源码：`README.md:11-15`
- F-004: 许可证为 MIT — 源码：`README.md:6`

## divisions.json 分类体系

- F-005: divisions.json 是部门集合的唯一真相来源，每个部门映射到显示标签、Lucide 图标名（PascalCase）和品牌色（hex）— 源码：`divisions.json:2`
- F-006: 共定义 17 个部门：academic、design、engineering、finance、game-development、gis、healthcare、marketing、paid-media、product、project-management、sales、security、spatial-computing、specialized、support、testing — 源码：`divisions.json:3-21`
- F-007: engineering 部门图标为 Code，颜色 #3B82F6 — 源码：`divisions.json:6`
- F-008: security 部门图标为 ShieldCheck，颜色 #EF4444 — 源码：`divisions.json:16`
- F-009: integrations/、strategy/、examples/、scripts/ 不是部门，通过 NON_DIVISION_DIRS 排除 — 源码：`divisions.json:2`、`scripts/check-divisions.sh:32`
- F-010: 添加新部门需要：创建目录、在 divisions.json 添加条目、更新 convert.sh 和 lint-agents.sh 中的 AGENT_DIRS — 源码：`CONTRIBUTING.md:40-45`

## tools.json 工具定义

- F-011: tools.json 是支持工具集的唯一真相来源，定义了 16 个工具的安装契约 — 源码：`tools.json:2-3`
- F-012: 支持的工具包括：claude-code、codex、gemini-cli、copilot、qwen、cursor、opencode、osaurus、aider、antigravity、kimi、openclaw、windsurf、hermes、vibe、zcode — 源码：`tools.json:4-19`
- F-013: 每个工具条目包含 id、label、kebab、accent、icon、order、scope（user/project）、detect、version、format、installKind、dest 字段 — 源码：`tools.json:4`
- F-014: installKind 有三种值：per-agent（每代理一个渲染文件）、roster（所有代理合并为一个文件）、plugin（构建产物，不可按代理渲染） — 源码：`tools.json:2`
- F-015: format 字段保证字节相同的输出，两个工具只有在渲染文件完全相同时才能共享 format — 源码：`tools.json:2`
- F-016: claude-code 使用 identity 格式，安装到 .claude/agents/{slug}.md，支持用户和项目范围 — 源码：`tools.json:4`
- F-017: codex 使用 codex-toml 格式，安装到 .codex/agents/{slug}.toml — 源码：`tools.json:5`
- F-018: cursor 使用 cursor-mdc 格式，仅支持项目范围，安装到 .cursor/rules/{slug}.mdc — 源码：`tools.json:9`
- F-019: aider 是 roster 类型，安装为项目根目录的 CONVENTIONS.md — 源码：`tools.json:12`
- F-020: hermes 是 plugin 类型，安装为 .hermes/plugins/agency-agents-router — 源码：`tools.json:17`

## Agent 文件格式

- F-021: Agent 文件使用 YAML frontmatter，必需字段为 name、description、color — 源码：`CONTRIBUTING.md:92-96`、`scripts/lint-agents.sh:34`
- F-022: frontmatter 可选字段包括 emoji、vibe、services（含 name/url/tier） — 源码：`CONTRIBUTING.md:96-101`
- F-023: lint-agents.sh 要求 frontmatter 必须包含 name、description、color（ERROR 级别） — 源码：`scripts/lint-agents.sh:34`
- F-024: 推荐章节包括 Identity、Core Mission、Critical Rules（WARN 级别） — 源码：`scripts/lint-agents.sh:35`
- F-025: Agent 文件正文结构包含：Identity & Memory、Core Mission、Critical Rules、Technical Deliverables、Workflow Process、Communication Style、Learning & Memory、Success Metrics、Advanced Capabilities — 源码：`CONTRIBUTING.md:106-154`
- F-026: Agent 文件分为两组语义部分：Persona（身份、沟通风格、规则）和 Operations（使命、交付物、工作流、指标、高级能力） — 源码：`CONTRIBUTING.md:159-172`
- F-027: Software Architect agent 的 vibe 为"Designs systems that survive the team that built them. Every decision has a trade-off — name it." — 源码：`engineering/engineering-software-architect.md:6`
- F-028: Growth Hacker agent 声明了 tools 字段：WebFetch、WebSearch、Read、Write、Edit — 源码：`marketing/marketing-growth-hacker.md:4`
- F-029: Agents Orchestrator agent 负责协调多代理开发流水线，最大重试次数为 3 次后升级 — 源码：`specialized/agents-orchestrator.md:11,44`

## scripts/lib.sh 脚本库

- F-030: lib.sh 是 convert.sh 和 install.sh 的纯 Bash 共享辅助库，无外部依赖，兼容 Bash 3.2+ — 源码：`scripts/lib.sh:1-5`
- F-031: get_field() 函数使用 awk 提取 YAML frontmatter 字段值 — 源码：`scripts/lib.sh:20-26`
- F-032: get_body() 函数去除前导 frontmatter 块返回文件正文 — 源码：`scripts/lib.sh:29-31`
- F-033: slugify() 函数将字符串转为 kebab-case（"Frontend Developer" → "frontend-developer"） — 源码：`scripts/lib.sh:34-37`
- F-034: agent_slug() 从文件的 name frontmatter 派生 slug，是 convert + install 一致的唯一真相来源 — 源码：`scripts/lib.sh:40-44`
- F-035: is_agent_file() 检查文件是否以 YAML frontmatter 分隔符 `---` 开头 — 源码：`scripts/lib.sh:47-49`
- F-036: incr() 是 set -e 安全的数值递增函数 — 源码：`scripts/lib.sh:56`
- F-037: 终端能力函数包括 supports_color()、supports_unicode()、term_cols()、term_rows() — 源码：`scripts/lib.sh:62-66`
- F-038: init_ansi() 填充 C_* 颜色变量和方框绘制字符（UTF-8 或 ASCII 回退） — 源码：`scripts/lib.sh:69-80`

## scripts/install.sh 安装脚本

- F-039: install.sh 从 integrations/ 读取转换后的文件并复制到各工具的配置目录 — 源码：`scripts/install.sh:6-7`
- F-040: 支持选择参数：--tool、--division、--agent、--agents-file — 源码：`scripts/install.sh:33-36`
- F-041: 支持模式参数：--link（符号链接而非复制）、--path（覆盖安装目录） — 源码：`scripts/install.sh:39-40`
- F-042: 支持行为参数：--interactive、--no-interactive、--no-convert、--dry-run、--list、--parallel、--jobs — 源码：`scripts/install.sh:43-49`
- F-043: 支持 Linux、macOS（需 Bash 3.2+）、Windows Git Bash/WSL — 源码：`scripts/install.sh:59`

## scripts/check-divisions.sh 验证脚本

- F-044: check-divisions.sh 强制执行部门集合的单一真相来源，验证 5 个位置的一致性 — 源码：`scripts/check-divisions.sh:3-11`
- F-045: 验证对象包括：磁盘上的顶级代理目录、convert.sh 的 AGENT_DIRS、lint-agents.sh 的 AGENT_DIRS、lint-agents.yml 的路径过滤器 — 源码：`scripts/check-divisions.sh:5-10`
- F-046: canonical() 函数使用 awk/grep/sed 从 divisions.json 提取部门名称 — 源码：`scripts/check-divisions.sh:42-46`
- F-047: actual_dirs() 使用 `git ls-files` 而非文件系统 glob，确保与 CI 的干净检出一致 — 源码：`scripts/check-divisions.sh:53-60`
- F-048: 每个部门必须包含至少一个以 `---` frontmatter 开头的 .md 文件 — 源码：`scripts/check-divisions.sh:111-129`
- F-049: 脚本无 jq 依赖，仅使用 bash 3.2 + coreutils，确保 macOS 和 CI 上行为一致 — 源码：`scripts/check-divisions.sh:15`

## scripts/lint-agents.sh Lint 脚本

- F-050: lint 脚本验证代理 Markdown 文件：YAML frontmatter 必须存在且包含 name/description/color — 源码：`scripts/lint-agents.sh:3-6`
- F-051: AGENT_DIRS 数组列出 17 个部门目录，需与 convert.sh 和 divisions.json 保持同步 — 源码：`scripts/lint-agents.sh:14-32`
- F-052: classify_header_target() 将章节头部分类为 'soul'（身份/学习记忆/沟通/风格/关键规则）或 'agents' — 源码：`scripts/lint-agents.sh:40-53`

## 国际化脚本

- F-053: localize-agents-zh.ps1 是 PowerShell 脚本，将已安装代理的 name 和 description 本地化为中文 — 源码：`scripts/i18n/localize-agents-zh.ps1:1-9`
- F-054: 默认目标目录为 ~/.github/agents 和 ~/.copilot/agents — 源码：`scripts/i18n/localize-agents-zh.ps1:2-5`
- F-055: 使用 agent-names-zh.json 映射文件进行名称替换 — 源码：`scripts/i18n/localize-agents-zh.ps1:8-9`
- F-056: 脚本读取文件→解析 frontmatter→替换 name/description→写回，使用 UTF-8 编码 — 源码：`scripts/i18n/localize-agents-zh.ps1:17-31`

## strategy/ 策略文档

- F-057: NEXUS（Network of EXperts, Unified in Strategy）将代理转变为协调流水线 — 源码：`strategy/QUICKSTART.md:7-9`
- F-058: NEXUS 提供三种模式：Full（12-24 周，全代理）、Sprint（2-6 周，15-25 代理）、Micro（1-5 天，5-10 代理） — 源码：`strategy/QUICKSTART.md:13-17`
- F-059: NEXUS-Full 流水线包含 7 个阶段（Phase 0-6）：发现→策略→基础→构建→加固→发布→运营 — 源码：`strategy/QUICKSTART.md:31-38`
- F-060: 每阶段之间有质量门控，所有评估需要证据，每任务最大重试 3 次 — 源码：`strategy/QUICKSTART.md:40-41`

## integrations/ 集成模式

- F-061: integrations/ 目录包含各支持工具的转换格式输出 — 源码：`integrations/README.md:3-4`
- F-062: 支持 15 种工具格式，包括 Claude Code（.md）、Antigravity（SKILL.md）、Cursor（.mdc）、Aider（CONVENTIONS.md）、Windsurf（.windsurfrules）等 — 源码：`integrations/README.md:8-22`
- F-063: 项目范围工具（OpenCode、Cursor、Aider、Windsurf、Qwen）需从目标项目根目录运行安装程序 — 源码：`integrations/README.md:54-57`
