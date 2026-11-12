---
type: Example
title: "示例：逐行解剖 taxi-home 技能"
description: "把官方示例 taxi-home 的 SKILL.md 与 flow.yaml 拆到字段级：每个 frontmatter 键对应哪条校验、flow 的 6 个步骤各自走哪条执行路径，并对照两个更简单的示例"
tags: [phonepal, example, skill, flow-yaml, taxi-home]
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
  - id: S-02
    resource: ../references/01-api-map.md
    title: 技能与 flow 的类型定义索引
---

# 示例：逐行解剖 taxi-home 技能

`skills/examples/taxi-home/` 是仓库里唯一带 `flow.yaml` 的示例，也是把「声明式固定步骤」和「自由操作」混在一起的最佳样本。

## 1. `SKILL.md` 全文

```markdown
---
name: taxi-home
description: 用高德地图打车回家（读取记忆里的家庭住址，呼叫前需用户确认）
apps: [com.autonavi.minimap]
channel: deeplink-then-gui
confirm_before: [确认呼叫]
memory: [places/家]
deeplinks:
  route: "amapuri://route/plan/?sourceApplication=phonepal&dname={destination}&dev=0&t=0"
---
# 高德打车回家

目标：在高德地图里叫一辆去「家」的车，停在呼叫前让用户确认。

1. 目的地取自记忆 `places/家` 的地址；记忆里没有地址时用 ask_user 询问，不要猜。
2. 先用 deeplink `route` 打开路线规划，`{destination}` 填家的地址；打不开时启动高德，点「打车」，在目的地输入框输入地址。
3. 在打车页选择「快车」（用户偏好记忆里有车型时按偏好），读出预估价和预计接驾时间。
4. 点「确认呼叫」前必须得到用户确认；用户拒绝就 finish 并说明已停止。
5. 呼叫成功后看到「正在为您呼叫」或司机信息即 finish，summary 里写车型、预估价和司机信息。

注意：出现登录、实名认证、验证码或支付页面时用 ask_user 交给用户处理。
```

## 2. 每个字段为什么存在

| 字段 | 值 | 校验 / 运行效果 |
|---|---|---|
| `name` | `taxi-home` | 必须匹配 `^[a-z0-9-]+$`，并与文件夹同名 [F-054/F-055] |
| `description` | 一句话 | 单行非空；只有它进入聊天模型的技能索引，模型靠它挑技能 [F-022] |
| `apps` | `[com.autonavi.minimap]` | Sentinel 在技能声明 apps 时拒绝操作其他包；启动器与 PhonePal 自身除外 [F-039] |
| `channel` | `deeplink-then-gui` | 6 个通道之一；当前代码里是声明性元数据，不改变执行路径 [F-019] |
| `confirm_before` | `[确认呼叫]` | 追加到内置 17 个确认词之后；不能删除内置词 [F-042] |
| `memory` | `[places/家]` | 任务开始时读取该笔记全文，放入操作提示词的「相关资料」分节 [F-023/F-029] |
| `deeplinks` | `route: "amapuri://..."` | 必须是 `scheme://` 形式；`{destination}` 由 `fill` 填值并百分号编码 [F-034] |

正文部分不会进入聊天模型，只在操作模型每一轮的提示词里出现 [F-029]。所以它可以写得很具体：「点哪个按钮」「什么情况问用户」「什么情况结束」。

## 3. `flow.yaml` 全文

```yaml
steps:
  - deeplink: route
  - wait: 1500
  - ai: 切换到打车页，选择快车并读出预估价
  - confirm: 确认呼叫快车回家？
  - tap: 确认呼叫
  - assert: 正在为您呼叫
```

六步分别发生什么 [F-033/F-056]：

| 步骤 | 执行 | 失败时 |
|---|---|---|
| `deeplink: route` | 取 `SKILL.md` 的 `deeplinks.route`，用记忆里的地址填 `{destination}`，发 `Action.OpenDeeplink` | URI 非法、无 App 可打开 |
| `wait: 1500` | `Action.Wait(1500)` | 解析期就限制 0..600000 |
| `ai: 切换到打车页…` | 进入子目标操作循环，模型自由操作 | 子目标失败、卡死、超步数 |
| `confirm: 确认呼叫快车回家？` | 发 `NeedsUser`，用 `isYes` 判定回答 | 用户回答不是肯定词 |
| `tap: 确认呼叫` | 单步约束 `tap`，最多 3 次；仍经 Sentinel（确认词会再问一次） | 三次都没给出 tap / 被拦截 |
| `assert: 正在为您呼叫` | 让操作模型看屏幕判断是否出现该文本 | 模型回答 `ok=false` |

> 注意 `confirm` 与 `tap` 的双重确认：`confirm` 是流程显式问一次；`tap` 的 target（或被点节点文字）命中内置/技能确认词时，Sentinel 还会再弹一次审批。示例里 `confirm_before: [确认呼叫]` 与内置词重复，`normalize` 会去重 [F-042]，但两次询问仍会发生——这是「流程保证」与「安全保证」两套机制的叠加，不是 bug。

## 4. 两个更简单的对照样本

### 4.1 最小技能：`open-settings-wifi`

```markdown
---
name: open-settings-wifi
description: 打开系统设置的 WLAN 页面，读出当前连接的网络
apps: [com.android.settings]
channel: gui
---
# 打开 WLAN 设置

1. 启动系统设置（com.android.settings）。
2. 点「WLAN」或「Wi-Fi」或「网络和互联网」→「WLAN」；找不到时向下滑动或使用设置里的搜索框搜索「WLAN」。
3. 读出 WLAN 开关状态和当前连接的网络名称，不要切换开关，也不要连接或忘记任何网络。

看到 WLAN 页面后 finish，summary 写开关状态和网络名称。
```

它没有 `flow.yaml`、没有 `memory`、没有 `confirm_before`，完全靠 `ai` 自由操作。适合「步骤因机型而异、但没有不可逆动作」的场景。

### 4.2 带确认与记忆：`takeout-reorder`

```markdown
---
name: takeout-reorder
description: 在美团外卖里把上一单再来一单（提交订单和支付前需用户确认）
apps: [com.sankuai.meituan.takeoutnew]
channel: gui
confirm_before: [提交订单, 支付]
memory: [偏好/外卖]
---
```

它在正文里明确写了「支付页面交给用户完成，不要输入密码」，但真正的保障不是这句话，而是：

- `confirm_before` 追加两个确认词；
- 内置词本来就含「提交订单」「支付」[F-042]；
- 密码框输入会被 Sentinel 直接 deny [F-039]。

## 5. 从这三个样本能学到的写法

| 场景 | 推荐结构 |
|---|---|
| 只读、机型差异大 | 只写 `SKILL.md`，正文给分支与 finish 条件（open-settings-wifi） |
| 有不可逆动作、路径稳定 | `flow.yaml` 固定关键步骤，`confirm` + 内置确认词双保险（taxi-home） |
| 需要用户偏好/地址 | `memory` 引用笔记，正文说明「没有就问，不要猜」（taxi-home / takeout-reorder） |
| 需要打开自家 App 的深链 | `deeplinks` + `flow` 的 `deeplink` 步骤，避免模型拼 URL |
| 页面结构经常变 | 把易变段留给 `ai`，只把入口与收尾写进 flow |

## 6. 提交前的自检单

- [ ] 文件夹名 = `name`，且匹配 `^[a-z0-9-]+$`
- [ ] `description` 是一行，写清「做什么 + 用哪个 App」
- [ ] `apps` 只列真正要操作的包
- [ ] 不可逆动作的确认词写进 `confirm_before`（内置词已覆盖的可以不写）
- [ ] `memory` 引用的 permalink 真实存在
- [ ] 所有 `deeplinks` 都是 `scheme://` 形式，占位符加了引号
- [ ] `flow.yaml` 每个步骤只有一个键值对；`wait` 是 0..600000 的整数
- [ ] 跑过 `python3 cli/phonepal.py lint <dir>`
- [ ] 在真机上 `run --skill <name> --follow` 至少成功一次，并看过轨迹

## 相关概念

- [技能与 flow：字段与校验规则](../concepts/06-skills-and-flows.md)
- [安全闸门：确认词与 apps 边界](../concepts/04-sentinel.md)
- [CLI 实操剧本](02-cli-workflow.md)
- [信源登记](../references/00-source-inventory.md)
