---
source: d:\AI\.chaos\libs\mobile-use
---

# 最佳实践

## 任务描述编写（Goal Writing）

任务描述（goal）是Planner和Cortex理解用户意图的唯一入口，直接决定任务成功率。

### ✅ 好的任务描述

```python
# 具体、明确、包含验证标准
goal="打开微信，找到最近聊天的'张三'，给他发送消息'明天下午3点开会'，确认消息发送成功"

# 包含约束条件
goal="在设置中查看电池使用情况，按耗电量从高到低列出前5个应用，记录各自的使用时长和耗电百分比"

# 包含数据提取要求
goal="打开美团App，搜索'火锅'，按距离排序，截图保存前3家店的名称、评分和距离，将信息整理成列表返回"
```

### ❌ 差的任务描述

```python
# 太模糊
goal="帮我操作手机"

# 目标不明确
goal="看看微信里有什么"

# 包含主观判断但无标准
goal="找几个好用的App"
```

### Goal 编写原则

| 原则 | 说明 | 示例 |
|---|---|---|
| **具体动作** | 明确说明要做什么操作 | "点击搜索按钮" > "搜索一下" |
| **可验证结果** | 描述期望的最终状态 | "看到已发送标记" > "发消息" |
| **必要上下文** | 提供识别所需的关键信息 | "找到群聊'产品部'" > "找到那个群" |
| **避免歧义** | 不使用"适当的"、"一些"等模糊词 | "点击红色按钮" > "点击那个按钮" |
| **单任务原则** | 一次任务只做一件事，复杂任务拆分为多个run_task | ❌ "登录账号并发邮件给张三同时设置闹钟" |

## 设备与环境准备

### Android设备准备清单

```
□ 开发者选项已开启（连续点击版本号7次）
□ USB调试已开启
□ USB安装（允许通过USB安装应用）已开启
□ USB调试（安全设置）已开启（允许模拟点击）
□ 屏幕自动旋转关闭（固定竖屏或横屏）
□ 屏幕休眠设置为"永不"或最长时间
□ 通知栏权限允许ADB访问
□ 连接方式选择"传输文件"而非"仅充电"
□ 已通过 adb devices 验证设备已识别
□ 设备未被其他ADB进程占用（关闭Android Studio、手机助手等）
```

### iOS设备准备清单

```
□ WebDriverAgent 已成功安装到设备
□ WDA 服务已启动（tidevice wdaproxy 或 xcodebuild test）
□ 设备未锁屏
□ 开发者模式已开启（iOS 16+）
□ 可通过 curl http://localhost:8100/status 验证WDA正常
```

### 云设备准备（Limrun/BrowserStack）

```
□ API Key 已配置到环境变量
□ 设备类型选择正确（Android/iOS + 版本号）
□ App包已上传或提供可下载URL
□ 网络策略允许访问云设备服务端点
```

## 任务执行优化

### 限制App范围提升准确率

```python
# ✅ 好：锁定到特定App，减少Agent在桌面迷路的概率
config = (
    Builders.AgentConfig()
    .with_locked_app_package("com.tencent.mm")  # 微信包名
    .build()
)
agent = Agent(config=config)
await agent.init()
result = await agent.run_task(
    goal="查看最近聊天列表，找到未读消息最多的对话"
)
# 整个执行过程不会离开微信
```

locked_app_package的作用：
1. Planner规划时限制子目标不涉及离开App
2. Executor如果发现跳转到其他App会自动返回
3. Convergence检查时如果当前App不对会触发重规划

### 使用Pydantic模型强制结构化输出

```python
from pydantic import BaseModel, Field
from typing import List

class AppUsage(BaseModel):
    app_name: str = Field(description="应用名称")
    package: str = Field(description="应用包名")
    battery_percent: float = Field(description="耗电百分比")
    screen_time_minutes: int = Field(description="屏幕使用时间（分钟）")

class BatteryReport(BaseModel):
    report_time: str = Field(description="报告生成时间")
    total_screen_time: str = Field(description="总屏幕使用时间")
    top_apps: List[AppUsage] = Field(description="耗电量前5的应用列表")

# 使用结构化输出
result = await agent.run_task(
    goal="查看电池使用情况，提取前5个耗电应用信息",
    output_schema=BatteryReport
)

# 直接获得结构化数据
battery_data: BatteryReport = result.structured_output
for app in battery_data.top_apps:
    print(f"{app.app_name}: {app.battery_percent}% - {app.screen_time_minutes}分钟")
```

### 合理设置max_steps防止无限循环

```python
# 简单任务（查信息、点按钮）：20步足够
result = await agent.run_task(goal="查看电池电量", max_steps=20)

# 中等任务（发消息、跨2-3个页面）：50步
result = await agent.run_task(goal="在微信给张三发消息", max_steps=50)

# 复杂任务（多步表单、数据提取）：80-100步
result = await agent.run_task(goal="填写注册表单并提交", max_steps=100)

# 批量/长任务：150步以上
result = await agent.run_task(goal="遍历通讯录前20人发节日祝福", max_steps=200)
```

> 如果任务频繁因max_steps超时，考虑：
> 1. 检查goal是否太宽泛
> 2. 将大任务拆分为多个小任务
> 3. 使用locked_app_package限制范围
> 4. 检查LLM是否出现循环决策（可从agent_thoughts看出）

### 选择合适的LLM Profile

根据任务复杂度选择Profile（参考[配置体系](configuration.md#profile-机制多套llm配置切换)）：

| 任务类型 | 推荐Profile | 预期步数 | 单步耗时 |
|---|---|---|---|
| 简单信息查询 | fast（全mini） | 10-20步 | 2-5秒/步 |
| 常规操作（发消息、设置） | 默认配置 | 20-50步 | 3-8秒/步 |
| 复杂决策（多步表单、验证） | smart（Cortex/Planner用强模型） | 30-80步 | 5-15秒/步 |
| 视频/动效分析 | video（启用video_analyzer） | 20-60步 | 5-10秒/步 |

## 调试与可观测性

### 开启详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 只看mobile-use相关日志
logging.getLogger("minitap.mobile_use").setLevel(logging.DEBUG)
```

### 监听事件流观察执行过程

```python
from minitap.mobile_use import EventType

def on_event(event):
    event_type = event["event"]
    data = event["data"]
    
    if event_type == EventType.CORTEX_DECISION.value:
        decision = data.get("decision", "unknown")
        thought = data.get("thought", "")[:100]
        print(f"🧠 Cortex决策: {decision}")
        print(f"   思考: {thought}...")
    
    elif event_type == EventType.EXECUTOR_ACTION.value:
        action = data.get("action", {})
        tool_name = action.get("name", "unknown")
        args = action.get("args", {})
        print(f"⚡ Executor执行: {tool_name}")
        if tool_name == "tap_element":
            print(f"   位置: ({args.get('x')}, {args.get('y')})")
        elif tool_name == "input_text":
            print(f"   输入: {args.get('text', '')[:50]}")
    
    elif event_type == EventType.TASK_COMPLETED.value:
        print(f"✅ 任务完成!")
        print(f"   结果: {data.get('result', '')[:200]}")
    
    elif event_type == EventType.ERROR.value:
        print(f"❌ 错误: {data.get('error')}")

# 执行任务并监听事件
result = await agent.run_task(
    goal="查看电量",
    on_event=on_event
)
```

### 保存执行轨迹用于事后分析

```python
# 完整执行轨迹在 result.metadata 中
print(f"总步数: {result.total_steps}")
print(f"总耗时: {result.duration_seconds:.1f}秒")

# 查看每一步的详细信息
for i, trace in enumerate(result.execution_traces):
    print(f"\n--- Step {i+1} ---")
    print(f"当前页面: {trace.get('current_app')} - {trace.get('activity')}")
    print(f"Agent思考: {trace.get('agents_thoughts', '')[:200]}")
    if trace.get('action'):
        print(f"执行动作: {trace['action'].get('name')} {trace['action'].get('args')}")
```

## 批量任务处理模式

```python
from minitap.mobile_use import Agent, Builders, EventType

async def batch_send_messages(contacts: list[str], message: str):
    """批量发送消息给多个联系人"""
    config = Builders.AgentConfig().with_locked_app_package("com.tencent.mm").build()
    agent = Agent(config=config)
    await agent.init()
    
    results = {}
    try:
        for contact in contacts:
            print(f"正在给 {contact} 发送消息...")
            try:
                result = await agent.run_task(
                    goal=f"找到联系人'{contact}'，发送消息'{message}'，确认发送成功",
                    max_steps=30
                )
                results[contact] = {
                    "success": result.success,
                    "message": result.result_message,
                    "steps": result.total_steps
                }
            except Exception as e:
                results[contact] = {"success": False, "error": str(e)}
            
            # 每个任务之间回到微信首页，避免上下文污染
            await agent.run_task(goal="返回微信首页聊天列表", max_steps=10)
    
    finally:
        await agent.clean()
    
    return results

# 使用
contacts = ["张三", "李四", "王五", "赵六"]
results = await batch_send_messages(contacts, "大家好，明天下午3点开会")
```

## 常见反模式（Anti-Patterns）

### ❌ 反模式1：在循环中重复创建Agent

```python
# 错误：每次run_task都重新创建Agent，慢且资源泄漏
for contact in contacts:
    agent = Agent(config=config)  # 不要在循环里创建！
    await agent.init()             # 每次都重新初始化设备连接
    result = await agent.run_task(...)
    await agent.clean()
```

```python
# 正确：Agent生命周期复用
agent = Agent(config=config)
await agent.init()
try:
    for contact in contacts:
        result = await agent.run_task(...)
finally:
    await agent.clean()
```

### ❌ 反模式2：忽略错误直接重试

```python
# 错误：无脑重试，可能导致重复操作（如重复付款、重复发送）
for _ in range(3):
    try:
        result = await agent.run_task(goal="点击支付按钮")
        break
    except:
        continue
```

```python
# 正确：检查状态后再决定
result = await agent.run_task(goal="查看是否已完成支付")
if "支付成功" in result.result_message:
    print("已支付，无需重试")
else:
    result = await agent.run_task(goal="点击支付按钮")
```

### ❌ 反模式3：任务描述包含实现步骤

```python
# 错误：过度约束实现路径，限制Agent的灵活性
goal="点击右上角的三个点按钮，然后点击设置，再点击账号与安全，最后查看登录设备列表"
# Agent被要求严格按步骤走，如果中间页面变化就会失败
```

```python
# 正确：描述目标而非实现路径
goal="在账号安全设置中查看当前登录设备列表"
# Agent会自己找到路径，即使UI变化也能适应
```

### ❌ 反模式4：不处理Agent的清理

```python
# 错误：没有clean()，可能导致：
# - ADB连接泄漏
# - WDA会话残留
# - 云设备会话不释放产生费用
agent = Agent(config=config)
await agent.init()
result = await agent.run_task(...)
# 没有 await agent.clean()！
```

```python
# 正确：使用 try/finally 保证清理
agent = Agent(config=config)
await agent.init()
try:
    result = await agent.run_task(...)
finally:
    await agent.clean()
```

## 稳定性提升技巧

1. **先手动验证流程**：先用手机手动操作一遍，确认流程可行，再让Agent执行
2. **保持App在前台**：任务开始前确保目标App在前台，Agent不会从锁屏状态开始
3. **稳定的网络环境**：LLM调用需要稳定网络，考虑配置fallback模型
4. **充足的电量**：设备低电量模式可能限制后台活动和性能
5. **关闭不相关的通知**：通知弹窗可能遮挡元素，影响Agent识别
6. **固定屏幕方向**：关闭自动旋转，避免横竖屏切换导致坐标错乱

> **源码参考**:
> - [sdk/agent.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/sdk/agent.py) - Agent生命周期与事件
> - [sdk/builders/](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/sdk/builders/) - 各类Builder
