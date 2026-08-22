---
id: i-have-adhd-wiki-install
title: 五、跨平台安装指南
source: external/libs/i-have-adhd/INSTALL.md 安装文档整理
---

# 五、跨平台安装指南

## 5.1 安装概述

**i-have-adhd** 技能支持当前主流的 AI 编程助手平台，遵循 `Agent Skills`（原外部链接 2026-07 复检已失效：github.com/anthropics/agent-skills） 开放标准，核心规则文件 `SKILL.md` 在多数平台上可直接复用，无需格式转换。

**支持的平台列表**：
1. Claude Code（Anthropic 官方 CLI）
2. Codex（OpenAI 官方 CLI）
3. Cursor / OpenCode / Amp（编辑器内置 Agent）
4. Gemini CLI（Google 官方 CLI）
5. GitHub Copilot（VS Code + CLI）
6. Zed 编辑器
7. Hermes
8. Pi
9. Antigravity（`agy`）
10. Trae IDE（兼容配置）

**两种激活模式**：
- **按需调用（opt-in，默认）**：安装后不自动生效，用户输入 `/i-have-adhd` 命令才激活当前会话
- **Always-On（持久化，可选）**：每次新会话自动加载规则，无需手动调用（详见第六章）

---

## 5.2 Claude Code 安装

Claude Code 通过官方插件市场分发，支持 flag + hooks 实现的 always-on 模式。

### 安装命令

```bash
claude plugin marketplace add ayghri/i-have-adhd
claude plugin install i-have-adhd@i-have-adhd
```

安装完成后，输入 `/i-have-adhd` 激活技能。

### 验证安装

```bash
claude plugin list
```

### 更新

```bash
claude plugin marketplace update i-have-adhd
```

### 卸载

```bash
claude plugin uninstall i-have-adhd
claude plugin marketplace remove i-have-adhd
```

或者保留安装但临时禁用：

```bash
claude plugin disable i-have-adhd
```

---

## 5.3 Codex 安装

Codex 同样通过插件系统安装，激活命令为 `$i-have-adhd`（而非斜杠命令）。

### 安装命令

```bash
codex plugin marketplace add ayghri/i-have-adhd --ref main
codex plugin add i-have-adhd@i-have-adhd
```

安装完成后，输入 `$i-have-adhd` 激活。

### 验证安装

```bash
codex plugin list
```

### 更新

Codex 更新需要先移除再重新添加：

```bash
codex plugin marketplace upgrade i-have-adhd
codex plugin remove i-have-adhd
codex plugin add i-have-adhd@i-have-adhd
```

### 卸载

```bash
codex plugin remove i-have-adhd
codex plugin marketplace remove i-have-adhd
```

---

## 5.4 Cursor / OpenCode / Amp 安装

这类平台原生支持 Agent Skills 标准，可通过 `npx skills` CLI 工具一键安装，或手动复制文件。

### npx 一键安装

```bash
# 当前工作区
npx skills add ayghri/i-have-adhd

# 全局所有项目
npx skills add ayghri/i-have-adhd -g

# 指定特定平台
npx skills add ayghri/i-have-adhd -a cursor -y
npx skills add ayghri/i-have-adhd -a opencode -y
```

新开会话，输入 `/i-have-adhd` 激活。

### 手动文件复制

无 CLI 时可直接复制技能目录：

```bash
git clone https://github.com/ayghri/i-have-adhd
mkdir -p ~/.cursor/skills
cp -R i-have-adhd/skills/i-have-adhd ~/.cursor/skills/
```

其他平台路径：
- OpenCode：`~/.agents/skills/`
- Amp：参考对应平台文档的 skills 扫描路径

### 验证

```bash
npx skills list
npx skills ls -g    # 全局安装查看
```

### 更新

```bash
npx skills update i-have-adhd
npx skills update -g    # 全局安装更新
```

### 卸载

```bash
npx skills remove i-have-adhd
npx skills remove i-have-adhd -g    # 全局卸载
```

---

## 5.5 Gemini CLI 安装

Gemini CLI 无内置插件市场，提供两种原生安装方式：自定义命令（按需调用）和扩展（always-on）。

### 方式一：自定义命令（按需调用，推荐）

```bash
mkdir -p ~/.gemini/commands
curl -fsSL https://raw.githubusercontent.com/ayghri/i-have-adhd/main/skills/i-have-adhd/agents/gemini.toml \
  -o ~/.gemini/commands/i-have-adhd.toml
```

新开会话，输入 `/i-have-adhd` 激活，仅对当前会话生效。

### 方式二：扩展（always-on）

```bash
gemini extensions install https://github.com/ayghri/i-have-adhd
```

扩展自动加载 `GEMINI.md`（导入完整 SKILL.md 规则），每次会话从第一条消息开始生效。需要系统安装 `git`。

### 验证

```bash
gemini extensions list          # 检查扩展安装
ls ~/.gemini/commands           # 检查命令文件存在
```

或在会话中输入 `/` 确认 `i-have-adhd` 出现在补全列表。

### 更新

```bash
gemini extensions update i-have-adhd    # 扩展方式
# 命令方式：重新执行上述 curl 命令覆盖文件
```

### 卸载

```bash
gemini extensions uninstall i-have-adhd    # 扩展卸载
rm ~/.gemini/commands/i-have-adhd.toml     # 命令卸载
```

---

## 5.6 GitHub Copilot 安装

GitHub Copilot（VS Code 扩展 + Copilot CLI）原生支持 Agent Skills 标准。

### 安装命令

```bash
# 当前项目
npx skills add ayghri/i-have-adhd -a github-copilot

# 全局所有项目
npx skills add ayghri/i-have-adhd -a github-copilot -g
```

### 手动安装

```bash
git clone https://github.com/ayghri/i-have-adhd
mkdir -p ~/.copilot/skills
cp -R i-have-adhd/skills/i-have-adhd ~/.copilot/skills/
```

**Copilot 扫描目录说明**：
- 项目级：`.github/skills/`、`.claude/skills/`、`.agents/skills/`
- 用户级：`~/.copilot/skills/`、`~/.claude/skills/`、`~/.agents/skills/`

### 验证

在聊天输入框输入 `/` 确认 `i-have-adhd` 出现，或执行：

```bash
npx skills list
npx skills ls -g
```

### 更新

```bash
npx skills update i-have-adhd
```

### 卸载

```bash
npx skills remove i-have-adhd
```

或直接删除 skills 目录中的 `i-have-adhd` 文件夹。

---

## 5.7 Zed 安装

Zed 编辑器原生支持 Agent Skills，相同的 `SKILL.md` 无需转换。

### GUI 方式（从 URL 创建）

1. 打开 Agent Panel → Skills 管理器
2. 选择 **Create skill from URL**（或命令面板执行 `agent: create skill from url`）
3. 粘贴 URL：
   ```
   https://github.com/ayghri/i-have-adhd/blob/main/skills/i-have-adhd/SKILL.md
   ```
4. 选择 **User** 作用域（所有项目生效）或 **Project** 作用域（仅当前项目）
5. 在 Agent Panel 输入 `/i-have-adhd` 激活

### 文件系统方式

```bash
git clone https://github.com/ayghri/i-have-adhd
cp -R i-have-adhd/skills/i-have-adhd ~/.config/zed/skills/
```

### 验证

打开 Skills 管理器确认 `i-have-adhd` 已列出，或输入 `/` 查看补全。

### 更新

- GUI 方式：从同一 URL 重新导入（覆盖）
- 文件方式：`git pull` 后重新复制文件夹

### 卸载

从 Skills 管理器移除，或删除 `~/.config/zed/skills/i-have-adhd`。

---

## 5.8 Hermes 安装

Hermes 通过 `hermes skills` 命令管理技能。

### 直接安装

```bash
hermes skills install ayghri/i-have-adhd/skills/i-have-adhd
```

技能安装到 `~/.hermes/skills/`，下次会话启动时暴露为斜杠命令。

### 通过 Tap 源安装（先浏览后安装）

```bash
hermes skills tap add ayghri/i-have-adhd
hermes skills search adhd
hermes skills install ayghri/i-have-adhd/skills/i-have-adhd
```

安装后输入 `/i-have-adhd` 激活。

### 验证

```bash
hermes skills list
```

### 更新

```bash
hermes skills update i-have-adhd
```

### 卸载

```bash
hermes skills uninstall i-have-adhd
```

同时移除 tap 源：

```bash
hermes skills tap remove ayghri/i-have-adhd
```

---

## 5.9 Pi 安装

Pi 实现了 Agent Skills 标准，技能调用语法为 `/skill:<name>`。

### npx 安装

```bash
npx skills add ayghri/i-have-adhd -a pi -y
```

### 手动安装

```bash
git clone https://github.com/ayghri/i-have-adhd
mkdir -p ~/.pi/agent/skills
cp -R i-have-adhd/skills/i-have-adhd ~/.pi/agent/skills/
```

**Pi 扫描目录**：
- 用户级：`~/.pi/agent/skills/`、`~/.agents/skills/`
- 项目级：`.pi/skills/`、`.agents/skills/`

启用技能斜杠命令，在 `settings.json` 中添加：

```json
{ "enableSkillCommands": true }
```

新开会话，输入 `/skill:i-have-adhd` 激活。

### 验证

```bash
npx skills list
```

或在会话中输入 `/skill:` 确认 `i-have-adhd` 已列出。

### 更新

```bash
npx skills update i-have-adhd
```

### 卸载

```bash
npx skills remove i-have-adhd
```

或删除 `~/.pi/agent/skills/i-have-adhd`。

---

## 5.10 Antigravity（`agy`）安装

Antigravity 通过 `agy plugin` 命令管理。

### 安装

```bash
agy plugin install https://github.com/ayghri/i-have-adhd
```

### 验证

```bash
agy plugin list
```

### 更新

先卸载再重新安装：

```bash
agy plugin uninstall i-have-adhd
agy plugin install https://github.com/ayghri/i-have-adhd
```

### 卸载

```bash
agy plugin uninstall i-have-adhd
```

或临时禁用：

```bash
agy plugin disable i-have-adhd
```

---

## 5.11 Trae IDE 适配说明

> **【SpecWeave 方法论补充】** 本节为基于 Agent Skills 开放标准的推理适配内容，非原项目官方文档。Trae IDE 兼容该标准，参考 Cursor 配置方式推理得出。

Trae IDE 兼容 Agent Skills 开放标准，可参考 Cursor 的配置方式进行适配：

1. **手动复制方式**：将仓库中的 `skills/i-have-adhd/` 目录复制到 Trae 的 skills 扫描路径
2. **npx skills 方式**：尝试使用通用 Agent Skills CLI：
   ```bash
   npx skills add ayghri/i-have-adhd
   ```
3. **Always-On 方式**：在 Trae 的全局规则/AGENTS.md 配置中粘贴精简规则块（见 6.3 节）

具体 skills 路径请参考 Trae IDE 官方文档中的技能目录配置说明。核心 `SKILL.md` 文件无需修改即可使用。

---

## 5.12 激活机制说明

安装后技能有三种状态：

| 状态 | 行为 | 触发条件 |
|------|------|----------|
| **未安装 / 未调用** | 规则完全不生效 | Claude Code 中 `disable-model-invocation: true` 阻止自动加载；其他平台按各自默认行为 |
| **按需调用** | 当前会话生效，新会话需重新激活 | 用户输入 `/i-have-adhd`（或 Codex 的 `$i-have-adhd`、Pi 的 `/skill:i-have-adhd`） |
| **Always-On 持久化** | 每次会话自动加载规则 | Claude Code 创建 flag 文件；其他平台在 AGENTS.md/规则文件中粘贴规则块；Gemini 安装扩展 |

**重要设计原则**：默认 **opt-in（选择加入）**，安装本身不会改变任何输出行为——只有用户主动调用或显式开启 always-on 后规则才生效，避免用户在不知情的情况下被强制改变输出风格。

当前会话中输入 `"stop adhd mode"` 或 `"normal mode"` 可临时关闭规则。
