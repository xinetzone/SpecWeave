# 来源会话证据

取证日期：2026-10-28。来源会话：`e8c7e024-fe41-4ee6-8899-1602e510715c`，标题为「/七概念 请记住新建的skill只能是 .agents/skills，写入记忆中」。

## 1. 失败经过

| 轮次 | 原文/事实 |
|---|---|
| 用户第 1 句 | `/七概念 请记住新建的skill只能是 .agents/skills，写入记忆中` |
| 我的回复 | 只处理了记忆部分，并追加「`/七概念` 不在当前可用技能列表中，未执行对应动作」 |
| 用户纠正 | 追加一轮「把七概念单独写入记忆」 |
| 纠正后 | 用 Grep 定位到指令正文、Skill 门面与两处登记行，写入项目记忆 |

失败原因不是别名不存在，而是把 Qoder 注入的运行时技能列表当成了仓库斜杠指令面的全集。

## 2. 成功解析的四条命中

以下路径当时均实际命中并读取：

```text
.agents/commands/seven-concepts.md
  frontmatter id: seven-concepts，title: 七概念方法论编排指令集
  正文声明为元指令（Orchestrator Command），不直接执行具体操作

.agents/skills/seven-concepts-cmd/SKILL.md
  name: seven-concepts-cmd，触发词含「七概念」「方法论编排」「用方法论」

.agents/capability-registry/02-skills.md
  ⭐ seven-concepts-cmd 技能行，触发词列含「七概念」（别名）

.agents/capability-registry/03-commands-workflows-protocols-rules.md
  ⭐ 方法论编排 | seven-concepts | …，路径指向 commands/seven-concepts.md
```

行号会随登记面增删漂移，因此正文只把行号当定位线索，引用前必须重新 Read。

## 3. 工具失败记录

首轮尝试在仓库根执行无界搜索：

```text
cd /d/spaces/SpecWeave && grep -rIl "七概念" --exclude-dir=.git --exclude-dir=node_modules . | head -30
```

结果：命令超时并被转入后台（任务 ID `b0qvs4q2e`），随后用 `TaskStop` 收尾；该次搜索没有产出可用结果。改用 Grep 工具（带 `path` 与 `head_limit`）后一次命中四条。

## 4. 最小复现检索

```text
Grep(pattern="七概念", path=".agents/commands", output_mode="content")
Grep(pattern="seven-concepts", path=".agents/capability-registry", output_mode="content")
```

若需要索引级检索：

```text
git grep -n "七概念" -- .agents
```

不要退回 `grep -rIl` 全仓扫描。

## 5. 结论

- 别名解析必须查四个面：指令目录、能力登记、Skill 门面表、根入口声明。
- 「不在注入列表」只能推出「当前运行时未注册」，不能推出「仓库内不存在」。
- 解析结果要落到实际动作；只回一张映射表等于没完成任务。
