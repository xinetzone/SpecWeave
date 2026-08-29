---
id: "agent-skills-wiki-quickstart"
source: "agent-skills-open-standard-wiki.md#五快速入门创建你的第一个-skill"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/agent-skills-wiki/04-quickstart.toml"
---
## 五、快速入门：创建你的第一个 Skill

### 5.1 最简示例：掷骰子 Skill

创建 `.agents/skills/roll-dice/SKILL.md`：

````markdown
---
name: roll-dice
description: Roll dice using a random number generator. Use when asked to roll a die (d6, d20, etc.), roll dice, or generate a random dice roll.
---

To roll a die, use the following command that generates a random number from 1 to the given number of sides:

```bash
echo $((RANDOM % <sides> + 1))
```

```powershell
Get-Random -Minimum 1 -Maximum (<sides> + 1)
```

Replace `<sides>` with the number of sides on the die (e.g., 6 for a standard die, 20 for a d20).
````

就是这样——一个文件，不到 20 行。

### 5.2 工作原理

1. **发现**：聊天会话开始时，智能体扫描默认技能目录并找到你的技能。它只读取 `name` 和 `description`，刚好够知道何时可能相关。
2. **激活**：当你询问掷骰子时，智能体将你的问题与技能描述匹配，并将完整的 `SKILL.md` 正文加载到上下文中。
3. **执行**：智能体遵循正文中的指令，根据请求的面数调整终端命令。
