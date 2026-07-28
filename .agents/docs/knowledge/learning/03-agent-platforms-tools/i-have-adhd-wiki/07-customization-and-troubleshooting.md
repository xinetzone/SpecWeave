---
id: i-have-adhd-wiki-custom
title: 八、自定义开发与故障排查
source: external/libs/i-have-adhd/INSTALL.md 自定义与排障整理
---

# 八、自定义开发与故障排查

## 8.1 自定义概述

官方默认规则是通用设计，但每个人的 ADHD 表现和工作习惯不同。i-have-adhd 设计为完全可定制：
- Fork 仓库后直接修改核心规则文件 `SKILL.md`
- 通过自己的 GitHub 用户名分发修改版本
- 所有平台的安装机制都支持自定义 fork

核心原则：**所有规则都在 `skills/i-have-adhd/SKILL.md` 一个文件里**，没有隐藏的硬编码逻辑，修改这一个文件就能改变所有行为。

---

## 8.2 Fork 自定义完整流程（以 Claude Code 为例）

### Step 1: 卸载官方版本

先完全移除上游版本，避免名称冲突：

```bash
claude plugin uninstall i-have-adhd
claude plugin marketplace remove i-have-adhd
```

> **重要**：fork 版本和上游版本共享插件名 `i-have-adhd`，必须先卸载再安装，否则会冲突。

### Step 2: Fork 并编辑

1. 在 GitHub 上 fork `ayghri/i-have-adhd` 到你的账号
2. 克隆你的 fork 到本地
3. 编辑 `skills/i-have-adhd/SKILL.md`，按你的需求修改规则
4. Commit 并 push 到你的 fork 仓库

### Step 3: 安装你的自定义版本

```bash
claude plugin marketplace add <your-username>/i-have-adhd
claude plugin install i-have-adhd@i-have-adhd
```

将 `<your-username>` 替换为你的 GitHub 用户名。

### Step 4: 验证生效

1. **完全重启 Claude Code**（插件索引在启动时读取）
2. 输入 `/i-have-adhd` 激活
3. 测试一个问题，确认输出风格符合你的修改

其他平台的自定义流程类似：Cursor/OpenCode 等支持 npx 的平台直接 `npx skills add <your-username>/i-have-adhd` 即可。

---

## 8.3 常见自定义方向

### 方向 1: 调整规则严格度

默认规则比较激进，如果你觉得太严格，可以放宽某些条目：
- 允许更长的开场白（修改规则 10，保留简单的问候）
- 列表上限从 5 项放宽到 7 项（修改规则 9）
- 允许"希望这有帮助"之类的结束语（删除规则 10 中的 closers 部分）

### 方向 2: 添加领域特定规则

根据你的工作领域追加规则：
- **前端开发**："给出 React 组件时，同时给出 CSS 模块示例"
- **后端开发**："数据库迁移必须同时给出回滚脚本"
- **DevOps**："kubectl 命令必须先带 --dry-run 示例"
- **学术写作**："引用时直接给出 BibTeX 条目"

### 方向 3: 修改语气风格

默认是简洁务实的语气，可以调整为：
- 更口语化/友好
- 更正式/专业
- 带特定的 emoji 使用习惯
- 使用特定语言（如中文输出时的格式调整）

### 方向 4: 增减规则条目

根据个人体验：
- 删掉对你没用的规则
- 添加你自己发现的"摩擦点"对应的规则
- 调整例外情况列表

---

## 8.4 故障排查

### 问题 1：`/i-have-adhd` 不在自动补全中

**症状**：输入 `/` 后补全列表里看不到 `i-have-adhd`。

**原因**：插件/技能索引在 Agent 启动时读取，安装后需要重启才能识别。

**解决方案**：
1. 完全退出并重启你的 AI 编程助手（Claude Code/Cursor/Codex 等）
2. 重启后再次输入 `/` 检查补全列表

---

### 问题 2：Always-On flag 文件无效

**症状**：创建了 `~/.claude/.i-have-adhd-always`，但新会话没有自动激活 ADHD 模式。

**原因**：
- 插件版本过旧，不包含 `hooks/hooks.json`（hooks 是后来加入的功能）
- 没有重启 Claude Code，hooks 在启动时加载

**解决方案**：
1. 更新插件到最新版本：
   ```bash
   claude plugin marketplace update i-have-adhd
   ```
2. 完全重启 Claude Code
3. 开新会话验证

---

### 问题 3：`claude plugin marketplace add` 失败

**症状**：执行 marketplace add 命令报错。

**常见原因**：
- 使用了错误的格式（需要 `owner/repo` 形式，不是完整 URL）
- 本地路径参数指向了错误目录（必须指向仓库根目录，不是 `.claude-plugin/` 子目录）

**解决方案**：
- 正确格式：`claude plugin marketplace add ayghri/i-have-adhd`
- 如果使用本地路径，确保路径指向包含 `plugin.json` 的仓库根目录

---

### 问题 4：安装后回复仍有开场白/套话

**症状**：激活 `/i-have-adhd` 后，回答仍然以"好的，让我来帮你..."之类的开场白开头。

**原因**：
- 当前会话是在激活前创建的，需要新开会话
- SKILL.md 措辞不够强硬，模型没有严格遵循

**解决方案**：
1. 开一个**全新的会话**（不是在当前会话继续）
2. 在新会话中重新运行 `/i-have-adhd`
3. 如果仍有偏差，考虑 Fork 后收紧 `SKILL.md` 中的措辞——用更明确的命令式语句（"MUST NOT"、"DO NOT"）替代建议式语句（"avoid"、"try to"）

---

### 问题 5：`npx skills add` 后技能缺失

**症状**：用 npx 安装成功，但 Cursor/OpenCode 中找不到技能。

**原因**：
- 需要新开会话才能索引到新技能
- 技能文件夹没有放在 Agent 扫描的正确路径下
- SKILL.md frontmatter 中的 `name` 与文件夹名不匹配

**解决方案**：
1. 完全重启 Agent 或开新的聊天会话
2. 确认文件夹位置正确：
   - Cursor: `~/.cursor/skills/i-have-adhd/`
   - OpenCode: `.agents/skills/i-have-adhd/`
3. 检查 `skills/i-have-adhd/SKILL.md` 头部的 `name: i-have-adhd` 与文件夹名一致

---

## 8.5 跨平台适配文件结构

i-have-adhd 采用"**一份核心规则 + 多平台适配文件**"的架构，确保跨平台一致性的同时适配各平台特性。

### 核心文件（所有平台共用）

```
skills/i-have-adhd/
└── SKILL.md          # 核心规则文件，所有平台共用
```

这是唯一的规则来源，所有平台最终都加载这一个文件的内容。

### 平台适配文件

```
skills/i-have-adhd/agents/
├── gemini.toml       # Gemini CLI 自定义命令配置
└── openai.yaml       # OpenAI/Codex 配置

plugin.json           # Antigravity (agy) 插件定义
gemini-extension.json # Gemini 扩展配置
GEMINI.md             # Gemini 扩展入口（导入 SKILL.md）

hooks/                # Claude Code 钩子系统
├── hooks.json        # SessionStart 钩子注册
└── always-on.sh      # flag 检测 + 规则注入脚本

.claude-plugin/       # Claude Code 市场元数据
├── plugin.json
└── marketplace.json

.codex-plugin/        # Codex 插件元数据
└── plugin.json

.cursor/skills/       # Cursor 技能市场元数据
└── i-have-adhd/
    └── SKILL.md
```

### 文件职责说明

| 文件/目录 | 作用 | 是否必须 |
|-----------|------|----------|
| `skills/i-have-adhd/SKILL.md` | 核心规则，所有平台共用 | ✅ 必须 |
| `hooks/hooks.json` | Claude Code 注册 SessionStart 钩子 | Claude Code always-on 需要 |
| `hooks/always-on.sh` | Claude Code 钩子执行脚本 | Claude Code always-on 需要 |
| `skills/i-have-adhd/agents/gemini.toml` | Gemini CLI 自定义命令定义 | Gemini 命令方式需要 |
| `gemini-extension.json` + `GEMINI.md` | Gemini 扩展 always-on 入口 | Gemini 扩展方式需要 |
| `plugin.json` | Antigravity 插件清单 | agy 需要 |
| `.claude-plugin/plugin.json` | Claude Code 插件清单 | Claude Code 市场需要 |
| `.codex-plugin/plugin.json` | Codex 插件清单 | Codex 需要 |
| `.cursor/skills/` | Cursor 技能目录 | Cursor 市场需要 |

**自定义开发时**：
- 修改 `skills/i-have-adhd/SKILL.md` 即可改变所有平台的行为
- 只有在需要适配新平台或修改钩子逻辑时才需要动其他文件
- 参考各平台的官方插件文档了解各配置文件的完整格式
