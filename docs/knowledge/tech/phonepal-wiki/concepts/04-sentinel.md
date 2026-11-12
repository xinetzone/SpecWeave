---
type: Concept
title: "安全闸门：模型之外的 allow / ask / deny"
description: "PolicySentinel 的三级规则、确认词匹配、任务级授权与审计：受保护屏幕、密码框、技能 apps 边界直接拒绝；支付/发送/删除等敏感动作必须询问；技能只能追加确认词"
tags: [phonepal, sentinel, safety, policy, audit, permission]
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

# 安全闸门：模型之外的 allow / ask / deny

PhonePal 的安全设计只有一个核心命题：**模型可以提议，但不能决定**。每一个动作在触达设备之前都要经过 `PolicySentinel`，而 Sentinel 只读三样东西：动作本身、当前屏幕、技能声明。模型说了什么、提示词写了什么，都不影响判定。

## 1. 判定顺序：先拒绝，再询问，最后放行

`evaluate` 的实现只有两行 [F-039]：

```kotlin
private fun evaluate(context: GuardContext, action: Action): Verdict {
    deny(context, action)?.let { return Verdict(Decision.Deny(it)) }
    return ask(context, action) ?: Verdict(Decision.Allow())
}
```

顺序不能交换：**deny 优先于 ask**。否则「受保护页面上的支付按钮」会被确认词命中，变成「询问后可以点」，而正确行为是直接拒绝。

## 2. deny：三种直接拒绝

| 规则 | 触发条件 | 例外 | 依据 |
|---|---|---|---|
| 受保护屏幕 | `screen.secure == true` 且动作会触达设备且不是导航 | `back`、`home`、`wait`；`ask_user`/`finish` 本来就不碰设备 | [F-039] |
| 密码字段 | `type` 的目标是密码节点（指定 `nodeId` 或当前聚焦的可编辑节点） | 无 | [F-039] |
| 技能 apps 边界 | 技能声明了 `apps` 时：`launch`/`deeplink` 指向清单外，或 `tap/long_press/type` 发生在清单外的前台包 | 桌面启动器（12 个默认包名）与 PhonePal 自身 | [F-039/F-044] |

注意第三条的细节：系统 UI（状态栏、权限弹窗）不豁免，只有 `back/home` 与滑动能通过。这条规则防的是「技能说只操作高德，结果模型点进了支付 App」。

## 3. ask：两种必须确认的情况

### 3.1 确认词命中

`tap`、`long_press`、`type` 三类动作会检查三个文本来源 [F-040]：

1. 动作自带的 `target`（模型写的「确认呼叫 按钮」）；
2. 被操作节点的 `text`；
3. 被操作节点的 `description`。

节点解析规则：优先 `nodeId`；没有 id 时，点击类取「包含该点的最小节点」，输入类取当前聚焦的可编辑节点 [F-040]。

匹配到确认词后，弹窗文案也按动作类型区分：

- 点击：「即将点击「确认呼叫」，是否继续？」
- 长按：「即将长按「…」，是否继续？」
- 输入：「即将在「…」输入内容，是否继续？」；`submit = true` 时是「输入并提交」。

### 3.2 内置 17 个确认词

| 类别 | 词 |
|---|---|
| 中文 | 支付、付款、确认支付、立即支付、转账、发送、删除、下单、提交订单、确认呼叫、呼叫、购买 |
| 英文 | pay、send、delete、purchase、order |

匹配是子串匹配，但**拉丁词首尾加词边界**：`order` 命中 `Place Order`，不命中 `border` [F-043]。多个词命中时取最长词作为审批键（`word:<词>`），所以「确认支付」不会退化成「支付」的授权 [F-043]。

## 4. 技能能做什么、不能做什么

| 能力 | 机制 | 边界 |
|---|---|---|
| 追加确认词 | `confirm_before: [确认呼叫]` 与内置词合并、去重 | 只能加，不能删；内置 17 个词永远生效 [F-042] |
| 缩小可操作 App | `apps: [com.autonavi.minimap]` | 只会让 deny 更多，不会让 deny 更少 [F-039] |
| 声明自己的 deeplink | `deeplinks:` 模板 | 只有 scheme + host 都匹配模板才免询问；否则一律 ask [F-040] |
| 指定要加载的记忆 | `memory: [places/家]` | 只影响提示词内容，不影响权限 |

一个常见误解是「技能是我写的，所以可以放宽安全」。代码层面做不到：`wordsFor` 的实现是 `ConfirmWords.normalize(baseWords + skill.confirmBefore)`，没有减法路径 [F-042]。

## 5. deeplink 的白名单匹配

`deeplink` 动作如果直接放行，等于允许模型把任意 URI 交给系统打开——可能是支付链接、也可能是钓鱼页。PhonePal 的规则是 [F-040]：

```text
技能的 deeplinks: route = "amapuri://route/plan/?dname={destination}"
动作的 uri:        "amapuri://route/plan/?dname=北京市海淀区..."
                    scheme=amapuri, host=route → 与模板一致 → 免询问
动作的 uri:        "alipays://platformapi/startapp?..." 
                    scheme=alipays, host=platformapi → 不匹配 → 询问
```

比较只看 scheme 与 host，不看 path/query，因为 `{placeholders}` 会变化；没有技能或技能没写模板时，所有 deeplink 都要询问。

## 6. 授权范围与审计

`authorize` 在 `Ask` 之后做的事 [F-041]：

1. 先查本任务已授予的 TASK 级批准，键是 `word:<词>` 或 `deeplink:<scheme://host>`；
2. 没有则经 `ApprovalGateway` 弹审批卡（聊天界面）或通知（通知栏）[F-069/F-081]；
3. 用户选「本次任务都允许」时，把键写入 `taskApprovals[taskId]`；
4. 任务结束由 `endTask(taskId)` 清空；
5. 无论 allow/ask/deny，都写一条 `AuditRecord` 到 `audit.jsonl`。

审批的三种结果会作为聊天进度条出现：「已允许」「本次任务都允许」「已拒绝」[F-069]。

## 7. 审计记录长什么样

`TraceFormat.audit` 输出 6 个字段 [F-071]：

```json
{"time":1761830000300,"run":"r1","step":3,"action":{"type":"tap","nodeId":12},"decision":"ask: confirmation word '确认呼叫' in node text","approved":true}
```

它和 `trace.jsonl` 分开写：`trace.jsonl` 是给开发者看的事件流，`audit.jsonl` 是给安全复核看的决策流。两者都经过 `TraceWriter.mask`，API Key（长度 ≥ 4）会被替换成 `***` [F-071]。

## 8. 这套设计的威胁模型

| 它能挡住的 | 它挡不住的 |
|---|---|
| 模型被页面文字诱导去点支付按钮（确认词 + ask） | 恶意 App 伪造一个看起来无害的按钮文案 |
| 技能偷偷放宽权限（只能追加确认词） | 用户自己连续点「允许」 |
| 在密码页/支付页乱操作（deny + 接管） | 无障碍服务本身的系统级权限被滥用 |
| 技能越界操作其他 App（apps 边界） | 模型把敏感信息写进普通笔记再读出 |
| 事后无法追责（audit.jsonl） | 设备已被 root / 注入的情况 |

它是一条**工程防线**，不是完整的移动安全方案；但在「LLM 驱动 UI 自动化」这个场景里，它把最危险的三类动作（支付、发送、删除）从「模型随时可做」降级为「必须人类点头」。

## 相关概念

- [操作循环：Sentinel 在哪里被调用](03-operator-loop.md)
- [技能与 flow：`apps` 与 `confirm_before` 怎么写](06-skills-and-flows.md)
- [无障碍手眼：密码字段与受保护屏幕怎么识别](07-hands-accessibility.md)
- [关键类型与签名索引](../references/01-api-map.md)
