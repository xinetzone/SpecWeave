---
name: specweave-slash-alias-resolution
version: 1.0.0
description: "当用户输入 SpecWeave 斜杠别名（如 /七概念）、中文指令别名，或怀疑某技能不存在、未注册、不在可用列表中时，必须使用此技能。按别名→指令文件→Skill 门面→登记行四步解析，先确认真实入口再决定执行、回答或写记忆，避免把运行时技能列表当成仓库指令面而误报不存在。触发词包括斜杠命令、slash alias、别名解析、七概念、方法论编排、指令集入口、为什么没有这个技能。不用于创建或登记新 Skill。"
argument-hint: "<slash-alias> [参数]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/specweave-slash-alias-resolution/**"
  - ".agents/commands/**"
  - ".agents/capability-registry/**"
title: "Slash 别名解析（Slash Alias Resolution）"
x-toml-ref: "../../../.meta/toml/.agents/skills/specweave-slash-alias-resolution/SKILL.toml"
source: "来源会话 e8c7e024-fe41-4ee6-8899-1602e510715c 的七概念别名误判与四步解析实证"
---

# Slash 别名解析（Slash Alias Resolution）

用户发来的 `/七概念` 不是技能名，而是仓库里的斜杠指令别名。先解析到真实入口，再谈执行。

## 1. 这个技能解决什么

实测失败：用户首句 `/七概念 请记住…`，我按 Qoder 注入的可用技能列表判断「不在当前可用技能列表中，未执行对应动作」。事实是：`.agents/commands/seven-concepts.md` 是元指令，`.agents/skills/seven-concepts-cmd/SKILL.md` 是对应门面，两处登记面均有条目。

> **为什么运行时技能列表不能当作唯一事实来源？** 注入列表只覆盖当前加载的技能注册表；`.agents/commands/` 是独立的斜杠指令库，别名、中文名与门面名三者未必同名。把「没在列表里」直接说成「技能不存在」，会把成熟入口判死。

结论必须落到三选一，而不是笼统的「有/没有」：

- 未注册到当前运行时（可能刚写入、需重启，或尚未建用户级联接）
- 已注册但注入列表未展示
- 仓库里确实没有

## 2. 适用边界

使用本技能：

- 用户输入 `/xxx` 或中文斜杠别名（如 `/七概念`、`/复盘`）
- 用户说「这个技能不存在吗」「为什么没有这个技能」「帮我按 XX 指令做」
- 需要在执行前确认别名指向的指令正文、Skill 门面与登记行

不适用：

| 任务 | 交给 |
|---|---|
| 从零创建或更新 Skill | `skill-creator` |
| 四处登记与用户级联接 | `native-skill-surface-registration` |
| 自动推荐 JSON 的 create/update 分诊 | `skill-recommendation-disk-triage` |
| 会话取证与证据审计 | `chat-session-evidence-audit` |

> **为什么把创建与登记分出去？** 别名解析的产物是「入口映射」，不是新资产。把解析失败当成「缺技能」去创建，会与既有门面重复，制造第二份真相。

## 3. 解析四步

### S1 归一化

去掉前导 `/`，保留中文 token，记录尾随参数（如 `scenario=milestone`、`subject=...`）。不要先把中文猜成拼音；拼音只作为补充检索词。

### S2 有界检索

用 Grep 工具，指定路径与 `head_limit`：

| 顺序 | 路径 | 目的 |
|---|---|---|
| 1 | `.agents/commands/` | 指令正文与 `id` |
| 2 | `.agents/capability-registry/` | Skill 行与指令行 |
| 3 | `.agents/skills/README.md` | 门面表行 |
| 4 | `AGENTS.md`、`.agents/ONBOARDING.md` | 入口与路由声明 |

检索词至少两组：中文别名原文，加上可能的英文 `id`。命中后记录文件与行号。

> **为什么不用 `bash grep -rIl` 全仓扫？** 实测在仓库根执行 `grep -rIl "七概念" --exclude-dir=.git` 会超时并被转入后台，需要 `TaskStop` 收尾，且结果不完整。Grep 工具带路径与 `head_limit` 是可控替代；需要索引级检索时用 `git grep -n <词> -- .agents`。

### S3 读语义

1. 读指令文件 frontmatter：`id`、`title`、`source`；读「触发条件」与「不应触发」两节。
2. 读门面 `SKILL.md` 的 `description` 与触发词，确认它确实回链到该指令正文。
3. 门面与正文职责不同：门面是 L1 索引，正文是 L2 编排逻辑；不要只读门面就宣称理解了执行细节。

### S4 核对登记并用 Read 验证

- `.agents/capability-registry/02-skills.md`：找 Skill 行（触发词里常写「别名」）。
- `.agents/capability-registry/03-commands-workflows-protocols-rules.md`：找指令 `id` 行。
- 引用任何路径前，用 Read 或 `ls` 确认文件真实存在；不要凭登记行推断文件存在。

> **为什么解析要落到两处登记？** 只有指令行说明它是命令，只有 Skill 行说明它能被技能路由触发。缺一条就要在结论里写清缺哪条，而不是笼统说「有/没有」。

## 4. 解析后的动作

| 解析结果 | 动作 |
|---|---|
| 指令与门面都存在 | 按门面流程完成用户的真实请求；映射表只作为开头一句，不代替执行 |
| 只有指令，无门面 | 读指令正文并按其步骤执行；明确说明「无原生技能门面，本次按指令集执行」 |
| 检索面穷尽仍无 | 列出已检索的四个面与检索词，报「未找到」；不得写成「技能不存在」 |
| 别名夹带记忆指令（「请记住…」） | 先完成解析，再把指令路径、门面路径、两处登记行写入项目记忆；不要只写一句结论 |
| 别名与门面同名但行为不同 | 以指令正文的触发条件与步骤为准，门面只做路由 |

> **为什么映射表不能当交付？** 用户发 `/七概念 分析 X` 要的是分析，不是一张「别名→文件」对照表。解析是前置，执行才是交付。

## 5. 输出契约

开头一行给结论，然后给映射：

```text
别名：/七概念 → 指令 seven-concepts（.agents/commands/seven-concepts.md）
门面：seven-concepts-cmd（.agents/skills/seven-concepts-cmd/SKILL.md）
登记：02-skills.md 技能行；03-commands-workflows-protocols-rules.md 指令行
动作：按门面流程执行 scenario=auto
```

缺项写「无」，不要省略。未找到时输出：

```text
已检索：.agents/commands/、.agents/capability-registry/、.agents/skills/README.md、AGENTS.md
检索词：<原文>、<英文候选>
结论：仓库内未找到该别名；当前运行时也未注册。
```

## 6. 幂等与重复解析

- 同一别名在本次会话已解析过，直接复用映射，不重复全量检索。
- 映射已存在时不要新建 Skill、不要复制门面；需要新增入口走 `native-skill-surface-registration` 或 `skill-creator` 的 Update 流程。
- 写入记忆前先查 `MEMORY.md` 是否已有同主题条目，已存在则更新而非新增。
- 收尾验证：映射中的每个路径都能被 Read 打开；登记行号只用于定位，不作为长期契约（文件会漂移）。

## 7. Gotchas（陷阱与反直觉行为）

1. **别名不是技能名**：`/七概念` 指向元指令 `seven-concepts`，不是一个叫「七概念」的 Skill；不要为它新建技能。
2. **中文别名不要先猜拼音**：先搜原文；拼音命中率低且容易误配到同音词。
3. **「不在可用列表」不等于「不存在」**：注入列表是运行时注册表，仓库指令面独立存在。
4. **`grep -rIl` 会超时**：全仓无界搜索在 SpecWeave 会转后台；用 Grep 工具或 `git grep` 加路径。
5. **登记行不是文件存在证明**：登记面可能领先或落后于磁盘；引用前必须 Read。
6. **门面只读不够**：门面描述编排能力，具体参数与质量门在指令正文里。
7. **元指令有子场景**：`/七概念` 下的 R/F/I/E/V/A/C 不是七个独立斜杠命令，不要逐个去找。
8. **别名夹带任务时先解析再干活**：跳过解析直接做，容易用错方法论或漏掉质量门。

## 8. 安全检查清单（逐项确认）

- [ ] 已做内容敏感度预检，未把私域内容写入公开目录
- [ ] 已用 Grep 工具做有界检索，未使用无界 `grep -rIl`
- [ ] 已确认指令文件与门面文件的真实路径，且两者都已 Read 验证存在
- [ ] 已核对 `02-skills.md` 与 `03-commands-workflows-protocols-rules.md` 两处登记行
- [ ] 结论已区分「未注册到运行时」「注入列表未展示」「仓库内不存在」
- [ ] 未为别名新建 Skill，未复制门面
- [ ] 映射表后已继续执行用户真实请求，未把映射当交付
- [ ] 写入记忆前已检查既有条目，已更新而非重复新增

## 9. 参考

- 来源会话证据：[references/verified-case.md](references/verified-case.md)
- 指令集目录：`.agents/commands/README.md`
- 能力登记：`.agents/capability-registry/02-skills.md`、`.agents/capability-registry/03-commands-workflows-protocols-rules.md`

## 10. 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-10-28 | 初始版本：四步别名解析、动作决策表、输出契约、幂等与 8 条 Gotchas；萃取自会话 e8c7e024 |
