---
type: Concept
title: "技能与 flow：用两个文件教会 App 一个新场景"
description: "技能是 SKILL.md（7 个 frontmatter 键 + Markdown 说明）加可选 flow.yaml（8 种声明式步骤）；加载时校验、坏技能隔离、用户技能覆盖内置；flow 的占位符、单步约束与断言"
tags: [phonepal, skills, flow-yaml, parser, validation]
generated:
  by: specweave-agent
  at: "2026-11-12T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-11-12T00:00:00+08:00"
status: stable
stale_after: "2027-05-12"
sources:
  - id: S-01
    resource: ../references/00-source-inventory.md
    title: 信源登记：PhonePal 源码快照
---

# 技能与 flow：用两个文件教会 App 一个新场景

PhonePal 把「支持一个新 App」的成本压到了两个文本文件：`SKILL.md` 告诉模型这是什么场景、怎么走；`flow.yaml` 可选地把关键步骤固定下来。没有编译、没有插件签名、没有代码执行。

## 1. 目录与放置

```text
taxi-home/
├── SKILL.md      # 必需：frontmatter + 给操作模型的 Markdown
└── flow.yaml     # 可选：固定步骤
```

手机上的用户技能目录是 `<external files>/skills/<name>/`，即 `/sdcard/Android/data/dev.phonepal.app/files/skills/`；内置示例技能从 APK assets 解压到 `filesDir/bundled-skills/` [F-067/F-072]。

加载顺序是「内置, 用户」：**同名时用户技能覆盖内置技能**；用户技能损坏时，同名内置技能保持生效 [F-053]。

## 2. `SKILL.md` 的 7 个键

| 键 | 必需 | 取值与约束 |
|---|---|---|
| `name` | 是 | `^[a-z0-9-]+$`，与文件夹同名且唯一；不一致会报问题但仍按 frontmatter 名加载 [F-054/F-055] |
| `description` | 是 | 单行、非空；聊天模型靠它挑技能，要写清「做什么 + 用哪个 App」 |
| `apps` | 否 | 包名列表；声明后 Sentinel 拒绝操作清单外的 App（启动器与自身除外）[F-039] |
| `channel` | 否 | 6 值之一：`api/cli/deeplink/gui/deeplink-then-gui/mixed`，默认 `gui` [F-019] |
| `confirm_before` | 否 | 追加确认词；只能加在内置 17 个词之后，不能删 [F-042] |
| `memory` | 否 | 笔记 permalink 列表，加载进操作提示词 [F-019] |
| `deeplinks` | 否 | `名称: "scheme://..."`；`{占位符}` 由操作模型填写；必须是 `scheme://` 形式 |

**未知键会报错**，不是忽略 [F-054]。这是故意的：`confirm-before`（少一个下划线）这种拼写错误如果被静默忽略，安全确认词就悄悄失效了。

frontmatter 之后的 Markdown 是写给**操作模型**的，不会进入聊天模型的上下文 [F-022/F-029]。写的时候可以假设读者已经看到了当前屏幕。

## 3. `flow.yaml` 的 8 种步骤

```yaml
steps:
  - launch: com.autonavi.minimap               # 包名；声明了 apps 时必须在 apps 内
  - deeplink: route                            # deeplinks 的键名，或字面 URI
  - wait: 1500                                 # 毫秒，0..600000
  - ai: 切换到打车页，选择快车并读出预估价        # 子目标，交给自由操作循环
  - type: { target: 目的地, text: "{destination}" }
  - confirm: 确认呼叫快车回家？                  # 明确问用户
  - tap: 确认呼叫                               # 点最匹配该文字的元素
  - assert: 正在为您呼叫                        # 让操作模型判断屏幕是否出现该内容
```

每种步骤的语义 [F-033/F-056]：

| 步骤 | 执行方式 | 失败条件 |
|---|---|---|
| `launch` | `Action.LaunchApp` | 包名非法、不在 `apps` 内、App 未安装 |
| `deeplink` | `Action.OpenDeeplink` | 既不是 deeplinks 键也不是 `scheme://` URI |
| `ai` | `OperatorLoop.run(subGoal = ...)` | 子目标循环失败 |
| `confirm` | `UserChannel.ask`，`isYes` 判定 | 用户回答不是肯定词 |
| `tap` | 单步约束 `tap`，最多 3 次 | 三次都没给出 tap 或被拦截 |
| `type` | 单步约束 `type`，文本可被 flow 覆盖 | 同上 |
| `wait` | `Action.Wait`，最长 600000 ms | 运行时不失败（超范围在解析期就报错） |
| `assert` | 操作模型判断屏幕是否显示指定文本 | 模型回答 `ok=false` 或多次解析失败 |

**任何解析问题都会让整个 flow 返回 null** [F-056]：宁可拒绝执行，也不执行「理解了一半」的流程。这与 `SKILL.md` 的处理一致——有问题的技能不会被加载 [F-053]。

## 4. 占位符怎么填

`flow.yaml` 里可以写 `{destination}`、`{地点}` 这样的占位符，解析规则是 [F-034]：

```mermaid
flowchart LR
    T[模板 {destination}] --> K{任务里已有值?}
    K -->|是| R[直接替换]
    K -->|否| M[问操作模型<br/>{"values": {...}}]
    M -->|给了值| R
    M -->|没给| U[问用户]
    U --> R
    R --> E[URL 场景做 percent-encode]
```

- 占位符正则允许字母、数字、下划线、连字符与汉字；
- `deeplink` 场景会做 UTF-8 百分号编码（空格转 `%20`），`ai`/`type` 场景不编码；
- 模型被明确要求「不知道的参数不要编造，留空字符串」，留空则回退问用户。

## 5. `confirm` 的 `isYes` 判定

`FlowRunner.isYes` 是一个很实用的小函数 [F-035]：

- 空串、以「不 / 别 / no」开头 → 否；
- 以「是 / 好 / 确认 / 确定 / 可以 / 行 / 对 / 嗯」开头 → 是；
- 英文 `yes/ok/okay/y/sure/yeah`，且后面不是字母（避免 `yesterday` 被当成 yes）→ 是；
- 其余 → 否。

它不追求语义理解，只覆盖「用户被问 yes/no」的典型回答。复杂回答应该走 `ask_user` 让模型处理。

## 6. 校验：加载时就把错误说清楚

`SkillParser` 与 `FlowParser` 的所有问题都带文件名与 1-based 行号 [F-054/F-057]：

```text
taxi-home/SKILL.md:9: unknown key 'confirm-before'; expected one of name, description, apps, channel, confirm_before, memory, deeplinks
taxi-home/flow.yaml:3: step 2 (wait): expected milliseconds as an integer 0..600000
```

CLI 的 `lint` 与 App 使用同一套规则、同样的报错顺序与行号 [F-074]。所以「本地 lint 通过」基本等价于「手机上能加载」；唯一差异是 App 还会检查同名技能冲突。

## 7. 最容易踩的五个坑

| 坑 | 现象 | 正确写法 |
|---|---|---|
| 键名拼错 | 整个技能不加载，报 unknown key | 只用 7 个合法键 [F-054] |
| `text: {destination}` 没加引号 | YAML 把它当 flow mapping，报 `type` 期望字符串 | `text: "{destination}"` [F-034] |
| `name` 与文件夹名不一致 | 报问题但仍加载，可能造成「以为没生效」 | 保持两者一致 [F-055] |
| `launch` 的包名不在 `apps` 内 | flow 解析期直接报错 | 要么补进 `apps`，要么删掉 `apps`（不推荐）[F-056] |
| 把支付/密码写进技能或记忆 | Sentinel 仍会 deny/ask，但信息已泄露 | 不写密码、不写 API Key |

## 8. 写一个技能的推荐顺序

1. 先写 `SKILL.md` 的 `name`/`description`/`apps`，用 `lint` 过一遍；
2. 在真机上用 `run --skill <name>` 让自由操作循环跑一遍，看轨迹确认路径；
3. 把稳定的关键步骤抽成 `flow.yaml`（`deeplink` → `ai` → `confirm` → `tap` → `assert`）；
4. 把易变的部分留给 `ai`，把不可逆动作放在 `confirm` 之后；
5. 再 `lint`，再 `run`，最后把 `howto` 笔记里的路径与 flow 对齐。

示例拆解见 [示例：技能解剖](../examples/01-skill-anatomy.md)。

## 相关概念

- [操作循环：`ai` 步骤进入哪个循环](03-operator-loop.md)
- [安全闸门：`apps` 与 `confirm_before` 的实际效果](04-sentinel.md)
- [CLI 与轨迹：lint / push / run / traces](09-cli-and-traces.md)
- [示例：技能解剖](../examples/01-skill-anatomy.md)
