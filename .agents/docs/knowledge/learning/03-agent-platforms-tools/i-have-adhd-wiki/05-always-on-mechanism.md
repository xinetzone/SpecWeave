---
id: i-have-adhd-wiki-persistence
title: 六、持久化机制详解
source: external/libs/i-have-adhd/hooks/ 钩子系统分析
---

# 六、持久化机制详解

## 6.1 为什么需要持久化

默认的按需调用模式存在一个摩擦点：**每次新会话都需要手动输入 `/i-have-adhd`**。对于高频使用者来说，这个重复动作很快会成为负担。

Always-On（持久化）模式解决了这个问题：
- 每次新会话自动加载 ADHD 友好输出规则
- 无需记忆或输入斜杠命令
- 从会话第一条消息开始就遵循规则格式
- 保留临时关闭能力（说 "stop adhd mode"）

不同平台采用不同的持久化实现方案，但目标一致：**在用户显式 opt-in 的前提下，让规则自动生效**。

---

## 6.2 Claude Code 的 flag + hooks 方案

Claude Code 是唯一提供**原生钩子系统**的平台，i-have-adhd 利用 `SessionStart` 钩子 + flag 文件实现了零侵入的持久化方案。

### 启用与关闭

**启用 always-on**：创建一个空的 flag 文件即可

```bash
touch ~/.claude/.i-have-adhd-always
```

如果你的 Claude 配置目录不在默认位置，honors `$CLAUDE_CONFIG_DIR` 环境变量。

**恢复按需模式**：删除 flag 文件

```bash
rm ~/.claude/.i-have-adhd-always
```

### hooks.json 配置解析

钩子配置位于 `file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/hooks/hooks.json`：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "sh \"${CLAUDE_PLUGIN_ROOT}/hooks/always-on.sh\"",
            "timeout": 5,
            "statusMessage": "Checking i-have-adhd always-on flag..."
          }
        ]
      }
    ]
  }
}
```

**配置要点**：
- **钩子类型**：`SessionStart` 在会话启动时触发
- **matcher 匹配**：`startup|resume|clear|compact` 覆盖四种场景
  - `startup`：全新会话启动
  - `resume`：恢复历史会话
  - `clear`：执行 `/clear` 清空上下文后
  - `compact`：执行上下文压缩后
- **命令类型**：执行 shell 命令，5 秒超时（防止阻塞会话启动）
- **路径变量**：`${CLAUDE_PLUGIN_ROOT}` 由 Claude Code 自动注入，指向插件安装目录

### always-on.sh 脚本工作原理

脚本位于 `file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/hooks/always-on.sh`，采用纯 POSIX sh 编写，保证跨平台兼容（macOS/Linux 的 sh、Windows 的 Git Bash）。

**完整脚本带注释**：

```sh
#!/usr/bin/env sh
# SessionStart hook: 用户创建 ~/.claude/.i-have-adhd-always 时注入完整规则集
# 设计原则：任何失败都 exit 0，绝不阻塞会话启动

# 1. 确定配置目录，支持自定义 CLAUDE_CONFIG_DIR
claude_dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
flag_path="$claude_dir/.i-have-adhd-always"

# 2. 关键：flag 文件不存在则直接退出（默认不激活，opt-in 设计）
[ -f "$flag_path" ] || exit 0

# 3. 解析脚本自身路径，定位 SKILL.md（不依赖环境变量，更可靠）
script_dir=$(dirname -- "$0")
skill_path="$script_dir/../skills/i-have-adhd/SKILL.md"
[ -f "$skill_path" ] || exit 0

# 4. 用 awk 剥离 YAML frontmatter（--- 包裹的头部元数据）
body=$(awk '
  NR == 1 && $0 ~ /^---[[:space:]]*$/ { in_fm = 1; next }
  in_fm && $0 ~ /^---[[:space:]]*$/   { in_fm = 0; next }
  !in_fm                              { print }
' "$skill_path") || exit 0

# 5. 输出激活提示 + 规则正文，注入到会话上下文
printf 'ADHD MODE ACTIVE (always-on). The ruleset below applies to every response. "stop adhd mode" turns it off for this session; delete %s to turn always-on off for good.\n\n%s\n' \
  "$flag_path" "$body"
```

**设计亮点**：
- **纯 POSIX sh**：无需 Node.js/Python 依赖，任何能跑 Claude Code 的环境都能执行
- **容错设计**：每个可能失败的步骤后都有 `|| exit 0`，钩子出错绝不影响正常使用
- **opt-in 安全**：默认不创建 flag 文件就完全无副作用，安装插件本身不改变任何行为
- **自包含路径**：通过 `$0`（脚本自身路径）定位 SKILL.md，不依赖容易出错的环境变量
- **YAML 剥离**：frontmatter 是给插件系统看的元数据，注入给模型时需要去掉

---

## 6.3 其他平台的 AGENTS.md 方案

对于没有 SessionStart 钩子系统的平台（Codex、Zed、Hermes、Pi、Copilot、Cursor 等），通用方案是将精简版规则块粘贴到平台的持久化指令文件中。

### 标准规则块模板（10条精简版 + 例外说明）

```markdown
## Output style

The reader has ADHD. Shape every response so it can be acted on:

1. Lead with the answer or next action: command, path, or snippet first.
2. Number multi-step work; one bounded action per step.
3. End with one next action doable in under two minutes.
4. Finish the current issue before raising a new one.
5. Restate progress each turn ("step 3 of 5 done").
6. Give time estimates in concrete units, never "a bit".
7. After a change, show what now works.
8. Errors: state location, cause, and fix. No drama.
9. Cap lists at 5 items.
10. No preamble, no recaps, no closers.

Exceptions: explain fully when asked to explain. Confirm before destructive actions. After three failed fixes, stop and name the doubtful assumption. If the request is ambiguous, ask one short question.
```

### 各平台配置文件路径

| 平台 | 持久化配置文件路径 | 作用域 |
|------|-------------------|--------|
| **Codex** | `~/.codex/AGENTS.md` | 全局所有项目 |
| **Zed** | `~/.config/zed/AGENTS.md` | 全局用户级 |
| **Hermes** | 工作目录 `AGENTS.md` 或 persona `SOUL.md` | 项目级 / 全局 persona |
| **Pi** | 项目 `AGENTS.md` | 项目级 |
| **GitHub Copilot** | 项目 `.github/copilot-instructions.md` | 项目级 |
| **Cursor** | Settings → Rules → User Rules，或 `.cursor/rules/` 下 `alwaysApply: true` 的规则文件 | 用户级 / 项目级 |
| **OpenCode** | `~/.config/opencode/AGENTS.md` | 全局 |
| **Antigravity (agy)** | `~/.gemini/GEMINI.md` | 全局 |

---

## 6.4 Gemini extension 方案

Gemini CLI 提供了原生 extension 机制实现 always-on，是第三种持久化方案：

```bash
gemini extensions install https://github.com/ayghri/i-have-adhd
```

**工作原理**：
1. 扩展安装后，Gemini CLI 自动加载仓库根目录的 `GEMINI.md`
2. `GEMINI.md` 通过导入机制引入完整的 `skills/i-have-adhd/SKILL.md` 规则
3. 从会话第一条消息开始，规则就已经在上下文中

这种方式介于 Claude Code 的钩子方案和 AGENTS.md 粘贴方案之间：
- ✅ 无需手动复制粘贴规则块
- ✅ 官方扩展机制，更新方便（`gemini extensions update`）
- ❌ 只能全局启用，不能按项目切换
- ❌ 安装即生效，没有 flag 文件那样的"开关"粒度

---

## 6.5 关闭方式

Always-On 提供两级关闭机制，灵活应对不同场景：

| 关闭范围 | 操作 | 适用场景 |
|----------|------|----------|
| **当前会话临时关闭** | 输入 `"stop adhd mode"` 或 `"normal mode"` | 某次会话需要详细解释、头脑风暴、或不想受格式约束 |
| **永久关闭 always-on** | Claude Code: `rm ~/.claude/.i-have-adhd-always`<br>其他平台: 从 AGENTS.md/规则文件中删除规则块<br>Gemini: `gemini extensions uninstall i-have-adhd` | 不再需要默认 ADHD 模式，回到按需调用 |
| **完全卸载** | 参考第五章对应平台的卸载命令 | 不再使用该技能 |

**重要**：临时关闭只对当前会话有效，下次新会话 always-on 会重新激活。

---

## 6.6 设计亮点：默认不自动激活（opt-in）

i-have-adhd 的持久化机制有一个核心设计原则值得强调：**默认 opt-in，绝不强制改变用户体验**。

具体表现：
1. **安装插件本身不激活规则**：Claude Code 中即使装了插件，如果没创建 flag 文件，也不会注入任何规则
2. **flag 文件是唯一开关**：一个空文件的存在与否决定了是否启用，语义清晰，容易理解和操作
3. **有明确的临时退出路径**：即使开了 always-on，任何时候说 "stop adhd mode" 就能在当前会话回到正常风格
4. **失败静默**：钩子脚本任何一步出错都静默退出，不会因为技能本身的 bug 导致用户无法正常使用 Agent

这种设计避免了许多"智能"工具常犯的错误：**安装后自作主张改变默认行为，让老用户感到困惑或被冒犯**。用户始终拥有完全的控制权。
