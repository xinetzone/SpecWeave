---
type: Example
title: "示例：用测试替身跑通一次手机任务"
description: "拆解 core-agent 测试夹具 Harness：ScriptedLlm、FakeDevice、InMemoryMemory、FakeSkills、FakeSentinel、FakeUsers、Events 如何拼出一个无需设备的 Agent；附一个完整测试用例的逐步解读"
tags: [phonepal, example, testing, fakes, kotlin, agent]
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
    title: 关键接口索引
---

# 示例：用测试替身跑通一次手机任务

`core-agent/src/test/.../Fakes.kt` 是一份很值得抄的测试夹具：它把 5 个接口全部换成可脚本化的假实现，于是「聊天 → 工具 → 操作循环 → 安全 → 记忆沉淀」这条完整链路可以在 JVM 上跑，不需要手机、网络或 API Key。

## 1. 夹具总览

| 替身 | 实现的接口 | 行为 |
|---|---|---|
| `ScriptedLlm` | `LlmClient` | 按队列返回预设回复；记录每次 `ChatRequest` |
| `FakeDevice` | `Device` | 按顺序返回屏幕；记录执行过的动作；可注入 `observeError` |
| `InMemoryMemory` | `MemoryStore` | 内存 Map 存笔记；搜索用双字窗口打分 |
| `FakeSkills` | `SkillRepository` | 固定技能列表 |
| `FakeSentinel` | `Sentinel` | 默认全 allow；可按动作返回 Deny/Ask |
| `FakeUsers` | `UserChannel` | 按队列回答；默认「好」 |
| `Events` | `AgentListener` | 收集全部事件，支持按类型过滤 |
| `Stop` | `StopSignal` | 可切换的停止标志 |
| `Harness` | — | 把以上组件装成一个 `PhonePalAgent` |

源码位置：`core-agent/src/test/kotlin/dev/phonepal/agent/Fakes.kt`。

## 2. 三个最有用的设计

### 2.1 模型是「脚本队列」

```kotlin
class ScriptedLlm(...) : LlmClient {
    fun reply(text: String) = apply { script.addLast { ChatResponse(text) } }
    fun tools(vararg calls: ToolCall) = apply { script.addLast { ChatResponse("", calls.toList()) } }
    fun fail(message: String = "boom") = apply { script.addLast { throw LlmException(message, 503, retryable = true) } }
    fun respond(block: (ChatRequest) -> ChatResponse) = apply { script.addLast(block) }
}
```

测试可以精确控制「第几轮返回什么」，并且能断言模型实际收到了什么（`requests` 列表）[F-075]。

### 2.2 设备是「屏幕队列」

```kotlin
class FakeDevice(vararg screens: ScreenState) : Device {
    override suspend fun observe(): ScreenState =
        if (queue.size > 1) queue.removeFirst() else queue.first()
    override suspend fun perform(action: Action): ActionResult { performed += action; ... }
}
```

最后一个屏幕会重复返回，正好模拟「操作后屏幕不变」的卡死场景。`screen(pkg, "WLAN", "蓝牙")` 这个工厂函数还会生成带 bounds、clickable 的 `UiNode`，让节点行文本可断言。

### 2.3 安全是「策略函数」

```kotlin
class FakeSentinel(private val policy: (Action) -> Decision = { Decision.Allow() }) : Sentinel
```

要测「被拦截后模型收到反馈」，只需传 `FakeSentinel { Decision.Deny("测试拦截") }`，不需要构造真实的 `PolicySentinel` 与审批网关。

## 3. 一个完整用例的逐步解读

`PhoneTaskTest.phoneTaskFromChatSucceedsAndLearns` 做了这些事 [F-075]：

```kotlin
val h = Harness(device = FakeDevice(home, settings, wlan))
h.chat.tools(ToolCall("p1", AgentTools.PHONE_TASK, """{"goal": "打开设置里的 WLAN"}""")).reply("已经打开 WLAN 页面。")
h.operator
    .reply(op("""{"type": "launch", "packageName": "com.android.settings"}"""))
    .reply(op("""{"type": "tap", "nodeId": 0, "reason": "进入 WLAN"}"""))
    .reply(op("""{"type": "finish", "success": true, "summary": "WLAN 页面已打开"}"""))

h.agent.handle("帮我打开 WLAN 设置", h.events, h.stop)
```

随后断言四件事：

1. **动作序列**：设备实际执行了 `LaunchApp` 与 `Tap(nodeId = 0)`；
2. **结果回灌**：聊天的第二次请求里，`tool` 消息包含 `"success":true` 与摘要；
3. **操作提示词**：`jsonMode = true`、含截图 `ImagePng`、含节点行 `[0] TextView "WLAN" (0,0,1000,90) clickable`、含上一步历史；
4. **学习沉淀**：记忆里出现 `howto/com.android.settings`，类型 `howto`，观察为 `[path] 打开 com.android.settings → WLAN #com.android.settings`。

它还断言了事件顺序：

```text
PhoneTaskStarted → StepPlanned → StepExecuted → StepPlanned → StepExecuted
→ StepPlanned → MemoryUpdated → PhoneTaskFinished → Reply
```

这条断言把「事件契约」固化成了测试：以后谁改了事件顺序，测试会立刻红。

## 4. 自己写一个循环测试的模板

```kotlin
@Test
fun stuckScreenFailsAfterWarning() = runTest {
    val same = screen("com.example.app", "下一步")
    val h = Harness(device = FakeDevice(same))          // 永远同一屏
    repeat(5) {
        h.operator.reply(op("""{"type": "tap", "nodeId": 0}"""))
    }
    val result = h.agent.runPhoneTask("点下一步", null, h.events, h.stop)

    assertFalse(result.success)
    assertTrue(h.events.of<AgentEvent.StepExecuted>().isNotEmpty())
    // 第 3 次不变 → 警告；再触发 → STUCK_FAILED
}
```

要点：

- 用 `FakeDevice(同一屏幕)` 制造卡死；
- 给足脚本回复，避免 `ScriptedLlm` 抛「no scripted response left」；
- 断言 `PhoneTaskFinished.success = false`，而不是断言具体文案（文案会变）。

## 5. 还可以测什么

| 目标 | 怎么搭 |
|---|---|
| 审批被拒后任务中止 | `FakeSentinel { Decision.Deny("x") }` |
| 受保护屏幕转交用户 | `screen(..., secure = true)` + `FakeUsers("已完成")` |
| flow 的 `tap` 单步约束 | `FakeSkills(skill(..., flow = Flow(listOf(FlowStep.Tap("确认")))))` |
| JSON 解析容错 | `h.operator.reply("```json\n{...}\n```")` |
| 模型 503 重试 | `h.operator.fail().reply(op(...))` |
| 记忆去重 | 连续两次成功任务，断言 `howto` 只有一条观察 |

## 6. 这个夹具没有覆盖的部分

| 未覆盖 | 原因 | 替代验证 |
|---|---|---|
| 真实无障碍节点树 | `AccessibilityNodeInfo` 是 Android 类 | Robolectric 仅做 warmup；真机验证 |
| HTTP 细节 | `ScriptedLlm` 跳过网络 | `core-llm` 用 MockWebServer 测 |
| 文件原子写 | `InMemoryMemory` 不落盘 | `FileMemoryStoreTest` 用临时目录 |
| YAML 解析 | `FakeSkills` 直接给对象 | `SkillParserTest` / `FlowParserTest` |
| UI 状态 | 测试不碰 Compose | 手动/截图验证 |

这也解释了测试分布：20 个 Kotlin 测试文件里，`core-agent` 4 个、`core-memory` 2 个、`core-skills` 3 个、`core-sentinel` 1 个、`core-llm` 1 个、`hands` 4 个、`app` 3 个、`core-api` 1 个，另有 `app/src/testDebug` 1 个 [F-075]。

## 相关概念

- [分层与依赖：为什么能这样测](../concepts/01-architecture.md)
- [操作循环：被脚本化的正是这些分支](../concepts/03-operator-loop.md)
- [CLI 实操剧本](02-cli-workflow.md)
- [信源登记](../references/00-source-inventory.md)
