---
id: "echobird-wiki-tool-registry"
title: "工具注册表"
source: "echobird-source-wiki-learning"
category: "learning"
tags: ["echobird", "tool-registry", "config.json", "paths.json", "tool-manager"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "EchoBird 工具注册表的 config.json/paths.json 结构、26+ 工具清单、已装工具检测、配置写入与官方端点恢复机制"
last_verified: "2026-08-04"
wiki_version: "1.0"
---

# 07 工具注册表

**工具注册表（Tool Registry）** 是 EchoBird 的"工具清单 + 配置字典"：它用统一的 `config.json` 与 `paths.json` 两个文件描述每一个受支持 AI 工具的模型配置写入方式和可执行文件位置，从而让 App Manager 能在不写死任何路径的前提下，自动检测已安装工具、并把 Model Nexus 的模型配置一键写入各工具的原生配置文件。本张基于源码 `external/tools/EchoBird/tools/` 与 `src-tauri/src/services/` 下的真实实现整理。

先看一个关键概念：**Model Nexus（模型中心）** 是 EchoBird 的统一模型数据中心，用户在此配置 API Key / Base URL / 模型名；工具注册表负责把这份中心配置"翻译"成每个工具自己的配置文件格式。**App Manager（应用管理器）** 是前端页面，用于展示已检测到的工具、绑定点模型、恢复官方端点。

## 7.1 注册表整体结构

`tools/` 目录下每个受支持工具都有一个独立子目录，内含两个标准文件：

```
tools/
├── claudecode/                 # Claude Code CLI
│   ├── config.json             # 模型配置读写映射
│   └── paths.json              # 各平台安装路径
├── codex/                      # Codex CLI + Desktop 集成资产
│   ├── config.json
│   ├── paths.json
│   └── README.md
├── reversi/                    # 内置游戏工具（无 config.json，用 models.json）
│   ├── models.json
│   ├── paths.json
│   └── default-skills/…
└── ...                         # 其余工具
```

运行时的加载流程（对应 `tool_manager.rs` 的 `load_tool_definitions`）：

1. **扫描**：遍历 `tools/` 下每个子目录；
2. **解析**：读取每个工具的 `paths.json` 与 `config.json`（或 `models.json`）；
3. **检测**：依据 `paths.json` 的可执行文件候选路径判断工具是否已安装；
4. **展示**：在 App Manager 页面显示已检测工具；
5. **应用**：用户绑定模型时，把配置写入工具的原生配置文件。

> 说明：`reversi`、`translator` 两个内置游戏没有 `config.json`，而是使用 **`models.json`**（只含 `write` 映射的极简文件）。`tool_manager.rs` 在选择模型映射文件时优先读取 `models.json`，找不到再回退到 `config.json`，以兼容旧版工具。

## 7.2 config.json 结构：模型配置读写映射

`config.json` 定义"如何从工具读取模型配置"与"如何把模型配置写入工具"。标准字段如下：

| 字段 | 含义 |
|------|------|
| `docs` | 官方文档 URL |
| `configFile` | 工具配置文件路径（如 `~/.claude/settings.json`） |
| `format` | 配置文件格式：`json` / `toml` / `yaml` / `env` |
| `read` | 读取当前配置的路径映射（`model` / `baseUrl` / `apiKey`，值为路径数组，按优先级排列） |
| `write` | 写入新配置的路径映射（键为配置路径，值为 ModelInfo 字段名） |
| `custom` | 可选布尔标记，为 `true` 时走各工具的专属写入函数（见 7.6） |

### 7.2.1 示例：Claude Code 写入 `~/.claude/settings.json`

`tools/claudecode/config.json` 的真实内容如下：

```json
{
    "docs": "https://docs.anthropic.com/en/docs/claude-code/settings",
    "configFile": "~/.claude/settings.json",
    "format": "json",
    "read": {
        "model": ["env.ANTHROPIC_MODEL"],
        "baseUrl": ["env.ANTHROPIC_BASE_URL"],
        "apiKey": ["env.ANTHROPIC_AUTH_TOKEN", "env.ANTHROPIC_API_KEY"]
    },
    "write": {
        "env.ANTHROPIC_MODEL": "model",
        "env.ANTHROPIC_SMALL_FAST_MODEL": "model",
        "env.ANTHROPIC_DEFAULT_SONNET_MODEL": "model",
        "env.ANTHROPIC_DEFAULT_OPUS_MODEL": "model",
        "env.ANTHROPIC_DEFAULT_HAIKU_MODEL": "model",
        "env.ANTHROPIC_BASE_URL": "baseUrl",
        "env.ANTHROPIC_AUTH_TOKEN": "apiKey",
        "env.ANTHROPIC_API_KEY": "",
        "env.API_TIMEOUT_MS": "3000000",
        "env.CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
    }
}
```

要点解读：

- **`env.` 前缀**表示路径最终落在 `settings.json` 的 `env` 对象里。`tool_manager.rs` 的 `get_nested_value` / `set_nested_value` 用点分路径（如 `env.ANTHROPIC_MODEL`）读写 JSON 嵌套对象。
- **`read` 的数组**表示按优先级依次尝试多个来源：例如 `apiKey` 优先读 `ANTHROPIC_AUTH_TOKEN`，找不到再读 `ANTHROPIC_API_KEY`。
- **`write` 的多个键指向同一字段**：`model` 被同时写入 `ANTHROPIC_MODEL`、`ANTHROPIC_DEFAULT_SONNET_MODEL` 等五个变量，因为 Claude Code 会在不同场景使用不同的默认模型名。
- **值为固定字符串**的条目（如 `API_TIMEOUT_MS: "3000000"`、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC: "1"`）是常量覆盖，与模型字段无关。
- **`ANTHROPIC_API_KEY: ""`** 表示写入空字符串（置空该环境变量）。

### 7.2.2 各工具配置格式差异

不同工具使用不同的配置格式，`format` 字段驱动写入器选择：

| 工具 | 配置文件 | 格式 |
|------|---------|------|
| claudecode | `~/.claude/settings.json` | json |
| codex / chatgptdesktop | `~/.codex/config.toml` | toml |
| aider | `~/.aider.conf.yml` | yaml |
| qwencode | `~/.qwen/settings.json` | json |
| vibe-trading | `~/.vibe-trading/.env` | env |
| grok | `~/.grok/config.toml`（分节 TOML） | toml |
| kimicode | `~/.kimi-code/config.toml` | toml |
| opencode / opencodedesktop | `~/.config/opencode/opencode.jsonc` | jsonc |
| workbuddy | `~/.workbuddy/models.json` | json |
| reversi / translator | `~/.echobird/reversi.json` 等 | json |

> 说明：`config.json` 中 `custom: true` 的工具（如 codex、aider、qwencode、vibe-trading、grok、kimicode、opencode、workbuddy、openclaw、mimocode、zcode、openscience、pi 等）在 `tool_config_manager.rs` 中都有独立的 `apply_*` / `read_*` 专属函数，处理各自特殊的写入逻辑（如 Codex 的协议代理、Claude Code 的中继模式、Aider 的 YAML 解析等），不会走通用 `apply_generic_json`。

## 7.3 paths.json 结构：可执行文件候选路径

`paths.json` 描述该工具在三个平台的**可执行文件候选路径**，用于检测工具是否已安装。除 `paths` 外，还包含 `name`、`category`、`command`、`configDir`、`configFile`、`envVar` 等元数据。

`tools/claudecode/paths.json` 的真实内容（节选）：

```json
{
    "name": "Claude Code",
    "category": "CLI Code",
    "apiProtocol": ["anthropic"],
    "command": "claude",
    "startCommand": "claude",
    "envVar": "CCS_CLAUDE_PATH",
    "configDir": "~/.claude",
    "configFile": "~/.claude/settings.json",
    "requireConfigFile": false,
    "paths": {
        "win32": [
            "%USERPROFILE%\\.local\\bin\\claude.exe",
            "%APPDATA%\\npm\\claude.cmd",
            "%USERPROFILE%\\.bun\\bin\\claude.exe",
            "%LOCALAPPDATA%\\Microsoft\\WinGet\\Links\\claude.exe",
            "%LOCALAPPDATA%\\pnpm\\claude.exe"
        ],
        "darwin": [
            "/usr/local/bin/claude",
            "/opt/homebrew/bin/claude",
            "~/.local/bin/claude",
            "~/.bun/bin/claude",
            "~/.npm-global/bin/claude",
            "~/Library/pnpm/claude"
        ],
        "linux": [
            "/usr/local/bin/claude",
            "/usr/bin/claude",
            "~/.local/bin/claude",
            "~/.bun/bin/claude",
            "~/.npm-global/bin/claude",
            "~/.local/share/pnpm/claude"
        ]
    }
}
```

关键字段：

| 字段 | 含义 |
|------|------|
| `name` | 工具显示名 |
| `category` | 分类字符串（`CLI Code` / `Desktop` / `Agent` / `Game` / `IDE` / `Science` 等），会被 `parse_category` 映射为枚举 |
| `command` | CLI 命令名（用于在 PATH 中查找），桌面应用为空字符串 |
| `startCommand` | **显式启动命令**，仅当显式定义时返回，不回退到 `command` |
| `envVar` | 自定义环境变量名，若设置则优先读取该变量指向的路径 |
| `configDir` / `configFile` | 配置目录 / 配置文件路径 |
| `requireConfigFile` | 为 `true` 时，即使找到可执行文件，也要求配置文件存在才算已安装 |
| `paths.win32/darwin/linux` | 各平台候选可执行文件路径数组，按顺序检测，命中即停 |

**路径变量**：`~` 表示用户主目录；`%APPDATA%` / `%LOCALAPPDATA%` / `%USERPROFILE%` 为 Windows 环境变量。`tool_manager.rs` 的 `expand_path` 会展开 `~` 与 `%ENV_VAR%`。

**Codex Desktop 的 Store 安装**：`tools/codex/paths.json` 除 Programs 路径外，还记录了 Microsoft Store 的 AUMID（`shell:AppsFolder\...`），用于 `launch_uri` 激活 Store 安装的 ChatGPT 桌面应用。

## 7.4 已支持工具清单

`tools/` 目录共包含 **27 个工具子目录**（25 个外部工具 + 2 个内置游戏）。按技术阵营与类型分类如下：

### 7.4.1 Claude 系

| 工具 | 类型 | 说明 |
|------|------|------|
| claudecode | CLI | Claude Code CLI，写 `~/.claude/settings.json` |
| claudedesktop | Desktop | Claude Desktop，写 `claude_desktop_config.json` 的 3P 配置 |
| claudescience | Science | Claude Science（展示类，无模型配置，仅 macOS/Linux） |

### 7.4.2 Codex 系

| 工具 | 类型 | 说明 |
|------|------|------|
| codex | CLI | Codex CLI，通过 Rust 协议代理（127.0.0.1:53682）做 Responses↔Chat 转换 |
| chatgptdesktop | Desktop | ChatGPT（原 Codex Desktop），与 codex 共享 `~/.codex/config.toml` |

### 7.4.3 开源 Agent（CLI）

| 工具 | 类型 | 说明 |
|------|------|------|
| aider | CLI | Aider AI 结对编程，写 YAML 配置 |
| openclaw | Agent | OpenClaw agent，写 `~/.openclaw/openclaw.json` |
| hermes | Agent | Hermes agent |
| opencode | Agent | Open Code，写 `~/.config/opencode/opencode.jsonc` |
| opencodedesktop | Desktop | OpenCode Desktop，与 opencode 共享同一配置文件 |
| mimocode | Agent | MiMo Code（小米 fork），写 `~/.config/mimocode/mimocode.jsonc` |
| kimicode | CLI | Kimi Code（Moonshot），写 `~/.kimi-code/config.toml` |
| qwencode | CLI | Qwen Code，写 `~/.qwen/settings.json` |
| pi | Agent | Pi assistant（earendil-works/pi），写 `~/.pi/agent/` |
| coffeecli | CLI | Coffee CLI |
| grok | CLI | Grok Build CLI（xAI），分节 TOML |
| openscience | Science | OpenScience（开源 Claude Science 替代，本机 `openscience serve`） |
| vibe-trading | Quant | AI 量化研究/市场分析 agent，写 `~/.vibe-trading/.env` |
| workbuddy | Agent | WorkBuddy（腾讯 CodeBuddy 办公版），写 `~/.workbuddy/models.json` |
| zcode | Agent | Z.AI 桌面 OpenCode fork，写 `~/.zcode/v2/config.json` |

### 7.4.4 IDE 集成

| 工具 | 类型 | 说明 |
|------|------|------|
| cursor | IDE | Cursor IDE |
| vscode | IDE | VS Code 扩展（通过 `extensionPaths` 检测） |
| trae | IDE | Trae IDE |
| traecn | IDE | Trae CN IDE |

### 7.4.5 桌面应用

| 工具 | 类型 | 说明 |
|------|------|------|
| geminidesktop | Desktop | Gemini Desktop |

### 7.4.6 内置游戏（Embedded）

| 工具 | 类型 | 说明 |
|------|------|------|
| reversi | Game | 黑白棋（AI 对战），测试模型连接，`alwaysInstalled: true` |
| translator | Game | 翻译器游戏，`alwaysInstalled: true` |

> 注：内置游戏无外部可执行文件（`alwaysInstalled: true`），其运行时 HTML 位于 `public/tools/{id}.html`，而非 `tools/{id}/`。任务描述中"26+ 个 CLI 工具"为概数，实际所有外部工具为 25 个（含 3 个桌面应用、4 个 IDE），加上 2 个游戏共 27 个工具目录。

## 7.5 工具检测：tool_manager.rs

`tool_manager.rs` 的 `detect_tool` 是核心检测函数，按优先级依次尝试以下方式：

1. **内置工具**：若 `alwaysInstalled` 为 `true`，直接判定已安装（游戏类）。
2. **MSIX/Store 应用（Windows）**：按启动 URI 的 AUMID 在 `%LOCALAPPDATA%\Packages` 下匹配已安装包（身份匹配、忽略发布者哈希，并接受 `<Identity>Beta` 通道）。
3. **自定义环境变量**：若设置了 `envVar`，展开其指向的路径，存在即判定已安装。
4. **PATH 查找**：若 `command` 非空，用 `command_exists` 在 PATH 中查找命令；若 `requireConfigFile` 为 `true`，还需配置文件存在。
5. **Python 模块**：若定义了 `python_module`，检查 `python -m <module>` 是否可用（pip 安装的 CLI 工具）。
6. **平台路径**：遍历 `paths.win32/darwin/linux` 的候选路径，`expand_path` 后存在即命中。
7. **Install-hints 兜底**：当硬编码路径全部未命中时，按平台扫描系统安装信息：
   - Windows：读取注册表 `HKLM/HKCU\SOFTWARE\...\Uninstall\*` 的 `DisplayName` / `DisplayIcon` / `InstallLocation` / `UninstallString`；
   - macOS：检查 `/Applications`、`~/Applications`，并用 `mdfind` 兜底；
   - Linux：扫描 `/usr/share/applications/*.desktop` 等。
8. **VS Code 扩展路径**：对定义了 `extensionPaths` 的工具，用 glob 前缀匹配扩展目录。
9. **配置目录兜底**：若 `detectByConfigDir` 为 `true` 且无更强的检测器（无平台路径、无 install-hints），则配置目录存在即视为已安装；否则残留的配置目录不算"已安装"（防止卸载后 `~/.<tool>` 残留被误判——这是 WorkBuddy 的回归修复）。

检测完成后，`scan_tools` 通过 `tokio::spawn` 对每个工具**并发**执行 `scan_single_tool`，并读取技能目录、版本号、当前激活模型，最终返回 `DetectedTool` 列表供前端展示。

**用户路径覆盖**：用户可编辑 `~/.echobird/tool-paths.json` 为工具添加自定义安装路径（键为工具 id，值为路径数组），`apply_user_path_overrides` 会把用户路径插入到候选列表最前，且该文件在更新后保留，不会被随包文件覆盖。

## 7.6 配置写入：tool_config_manager.rs

`tool_config_manager.rs` 是写入的枢纽，入口为 `apply_model_to_tool(tool_id, model_info)`，按工具分发到专属处理函数：

- 先调用 `normalize_model_info_for_tool` 做规范化（如 Claude Code 的 anthropic 协议会去掉 baseUrl 末尾多余的 `/v1`）；
- 再按 `tool_id` 分发到 `apply_claudecode` / `apply_codex` / `apply_aider` / `apply_grok` / `apply_kimicode` / `apply_zcode` / `apply_openscience` / `apply_mimocode` / `apply_opencode` / `apply_claudedesktop` / `apply_workbuddy` / `apply_vibe_trading` / `apply_pi` 等专属函数；
- 若匹配到 `config.json` 中 `custom: true` 的工具，走 `apply_echobird_relay`（写入 `~/.echobird/<toolId>.json` 中继侧信道）；
- 其余工具走通用 `apply_generic_json`（依据 `config.json` 的 `read`/`write` 映射操作 JSON 文件）。

以 `apply_claudecode` 为例，它写入 `~/.claude/settings.json`：

1. 读取现有 `settings.json`（若文件已存在但不是合法 JSON 对象，则**中止写入**，避免覆盖用户手写的 `allowedTools` / `hooks` / `MCP` 配置）；
2. 在 `env` 对象中写入 `ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN`、`API_TIMEOUT_MS=3000000`、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`，并**删除**残留的 `ANTHROPIC_API_KEY`（避免 x-api-key 与 Bearer 冲突）；
3. 根据 `relay_mode` 分两种模式：
   - **中继模式**：写入真实的上游 URL 与密钥，并把模型 id 写入 `ANTHROPIC_MODEL` 等五个模型变量（可选追加 `[1m]` 表示 1M 上下文窗口）；
   - **桥接模式**：`ANTHROPIC_BASE_URL` 指向本地代理 `http://127.0.0.1:53682/claudecode`，密钥用占位符 `echobird-local-proxy`，并移除模型变量；
4. 用 `write_json_file` 写回，同时把真实上游信息写入 `~/.echobird/claudecode.json` 中继侧信道，供代理实时读取。

**读取**：`get_tool_model_info` 按工具分发到 `read_*` 函数，把工具当前配置读回为 `ModelInfo`，供 App Manager 展示当前激活模型。

**API Key 安全**：写入前进行加密，加密后的 Key 带 `enc:v1:` 前缀，解密仅在启动工具时进行。

## 7.7 官方端点恢复：officialEndpoints.ts

`src/data/officialEndpoints.ts` 定义 **`OFFICIAL_ENDPOINTS`** 表，供 App Manager 的 **Restore（恢复）** 按钮把工具从第三方/代理 URL 一键恢复为厂商官方地址。该设计受 `cc-switch` 启发。

每个条目包含（`OfficialEndpoint` 接口）：

| 字段 | 含义 |
|------|------|
| `name` | 界面/提示中展示的官方名 |
| `baseUrl` | OpenAI 协议 base URL（无则空字符串） |
| `anthropicUrl` | Anthropic 协议 URL（可选） |
| `protocol` | 写入工具配置的协议：`openai` / `anthropic` |
| `modelId` | 仅当工具尚无模型时作为种子，不强制覆盖已有模型 |

**已注册的官方端点**：

| 工具 | 官方名 | baseUrl | 协议 |
|------|--------|---------|------|
| claudecode | Anthropic Official | `https://api.anthropic.com` | anthropic |
| claudedesktop | Anthropic Official | `https://api.anthropic.com` | anthropic |
| codex | OpenAI Official | `https://api.openai.com/v1` | openai |
| chatgptdesktop | OpenAI Official | `https://api.openai.com/v1` | openai |
| grok | xAI Official | `https://api.x.ai/v1` | openai |
| mimocode | Xiaomi MiMo Official | `https://api.xiaomimimo.com/v1` | openai |

**特殊处理**：
- **Claude Desktop**：Restore 会把 `deploymentMode` 翻回 `1p` 并删除 3P 配置/中继；URL 字段仅展示用（官方模式走 Anthropic OAuth，无 API Key）。
- **MiMo Code**：Restore 会删除 EchoBird 写入的 provider 块，回退到用户原生 `/connect` 凭据。
- **Kimi Code**：因 Moonshot 有 `.ai`（全球）与 `.cn`（中国）两个独立平台，无法选取单一"官方"端点，故**不显示官方端点卡片**，用户在其模型目录中自选平台。
- **OpenClaw / Hermes / OpenCode** 等社区开源工具无厂商官方 URL，**Restore 按钮隐藏**。

**恢复动作**：`tool_config_manager.rs::restore_tool_to_official` 对 codex/chatgptdesktop、claudedesktop、claudecode、grok、opencode/opencodedesktop、mimocode、zcode、pi、kimicode、openscience 走各自的 `restore_*_to_official` 函数，其余工具删除配置文件（或中继侧信道文件），让工具在下次启动时自行生成厂商默认配置。

**前端哨兵**：`officialModelSentinel(toolId)` 返回 `__official__<toolId>` 作为"官方端点"待选标记，`isOfficialModelSentinel` 判断该标记，用于区分普通模型选择与官方端点恢复。

## 7.8 打包安装资产：bundled_assets.rs

`src-tauri/src/services/bundled_assets.rs` 负责把"智能安装"所需的文本资产在编译期嵌入二进制（`include_str!`），实现离线优先安装。

- **公共安装 JSON**：存于公共仓库 `docs/api/tools/install/`，编译期硬编码进 `BundledAssets`（`install_index_json` + `install_refs` 线性表），由公共 crate 在 `register()` 中注入，运行时不经文件系统。
- **`INSTALLABLE_TOOL_IDS` 常量**：列出所有带打包安装引用的工具 id，共 **25 个**，与 `get_install_ref` 的键一一对应：

  `claudecode, codex, qwencode, aider, pi, hermes, openclaw, opencode, mimocode, kimicode, claudedesktop, chatgptdesktop, geminidesktop, opencodedesktop, coffeecli, claudescience, openscience, vscode, cursor, trae, traecn, grok, vibe-trading, workbuddy, zcode`

- **`build_embedded_refs_section`**：把所有工具安装 JSON 与 Quick-Action 任务脚本拼装成一个会被追加到系统提示词（Mother Agent）的"离线优先"引用块，提示 Agent 优先使用内嵌引用而非 `web_fetch` 抓取 echobird.ai，保证网络不可靠时仍能完成智能安装。
- **内部资产**：Mother Agent 系统提示词、欢迎提示、以及 Quick-Action 任务脚本（`network-info` / `security-audit` / `detect-cuda` / `install-cuda` / `install-git`）为内部行为，不对外公开，通过 `get_tool_script` 按名读取。

> 说明：内置游戏（reversi、translator）是 `alwaysInstalled`，无需安装引用，故不在 `INSTALLABLE_TOOL_IDS` 中；因此"25 个可安装工具 + 2 个内置游戏 = 27 个工具目录"。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [06 Codex Proxy 协议转换](./06-codex-proxy.md) | [README](./README.md) | → [08 高级功能模块](./08-advanced-pages.md) |