---
source: d:\AI\.chaos\libs\mobile-use
---

# 工具系统

## 工具架构概览

mobile-use 的工具系统采用 **Wrapper → Tool** 两层架构：

1. **ToolWrapper**：工具定义层，描述工具名称、参数 schema、执行逻辑，不直接绑定设备控制器
2. **LangChain BaseTool**：运行时工具实例，通过 `get_tools_from_wrappers()` 将 Wrapper 与 `MobileUseContext` 绑定生成可执行工具

```
┌─────────────────────────────────────────────────┐
│  ExecutorToolNode (LangGraph ToolNode)          │
│  └─ 接收 AIMessage.tool_calls → 执行工具        │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│  get_tools_from_wrappers(ctx, wrappers)         │
│  └─ 将 ToolWrapper 绑定 ctx 生成 BaseTool       │
└────────────────────┬────────────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼────┐     ┌─────▼─────┐    ┌────▼─────┐
│ tap_   │     │ swipe_    │    │ input_   │  ... 共16+2个
│wrapper │     │ wrapper   │    │ wrapper  │
└────────┘     └───────────┘    └──────────┘
```

## 核心移动操作工具

所有移动工具定义在 `minitap/mobile_use/tools/mobile/` 目录下：

| 工具 | Wrapper变量 | 功能 | 关键参数 |
|---|---|---|---|
| **点击** | `tap_wrapper` | 点击屏幕指定坐标 | `x: int, y: int` |
| **长按** | `long_press_on_wrapper` | 长按屏幕指定位置 | `x: int, y: int, duration: float=1.0` |
| **滑动** | `swipe_wrapper` | 从一点滑动到另一点 | `start_x, start_y, end_x, end_y, duration: float=0.5` |
| **返回** | `back_wrapper` | 按下系统返回键 | 无参数 |
| **按键** | `press_key_wrapper` | 按下指定按键 | `keycode: int`（Android keycode） |
| **删字符** | `erase_one_char_wrapper` | 删除输入框中一个字符 | 无参数 |
| **聚焦输入** | `focus_and_input_text_wrapper` | 点击聚焦并输入文本 | `x: int, y: int, text: str` |
| **聚焦清除** | `focus_and_clear_text_wrapper` | 点击聚焦并清除文本 | `x: int, y: int` |
| **启动App** | `launch_app_wrapper` | 启动指定包名的App | `package_name: str` |
| **停止App** | `stop_app_wrapper` | 强制停止指定App | `package_name: str` |
| **打开链接** | `open_link_wrapper` | 用系统浏览器打开URL | `url: str` |
| **等待** | `wait_for_delay_wrapper` | 等待指定秒数 | `seconds: float=1.0` |

### 视频录制工具（可选）

启用 `with_video_recording_tools()` 后额外提供两个工具：

| 工具 | Wrapper变量 | 功能 |
|---|---|---|
| **开始录屏** | `start_video_recording_wrapper` | 开始设备屏幕录制 |
| **停止录屏** | `stop_video_recording_wrapper` | 停止录制并保存 |

> 视频录制需要 `video_analyzer` Agent 配置支持视频的模型（如 Gemini 1.5/2.0 Flash）。

## Scratchpad：持久化记忆工具

Scratchpad 是 Agent 的"笔记本"——跨步骤持久化的键值存储，使用 `merge_dicts` Reducer 更新。

| 工具 | Wrapper变量 | 功能 |
|---|---|---|
| **保存笔记** | `save_note_wrapper` | 保存一个键值对到记忆 |
| **读取笔记** | `read_note_wrapper` | 读取指定键的笔记 |
| **列出笔记** | `list_notes_wrapper` | 列出所有已保存的笔记键 |

**使用场景示例**：
- 记住列表页看到的部分信息，滑动后继续读取时引用
- 存储中间计算结果
- 在多步骤任务中标记"已完成"的检查项

```python
# Agent 可以这样使用（通过自然语言决策）：
# 1. save_note(key="page1_items", value="Item A, Item B")
# 2. swipe 翻页
# 3. save_note(key="page2_items", value="Item C, Item D")
# 4. read_note(key="page1_items")  # 跨步骤回忆
```

## ToolWrapper 基类

### ToolWrapper

```python
class ToolWrapper:
    name: str                      # 工具名称
    description: str               # 工具描述（LLM通过此理解用途）
    params_schema: dict            # JSON Schema 定义参数
    def run(self, ctx, **kwargs):  # 执行逻辑（接收MobileUseContext）
        ...
```

### CompositeToolWrapper

批量组织多个工具的包装器，工具索引由其管理。

## 控制器适配层

工具的 `run()` 方法不直接调用 ADB/WDA，而是通过 `ctx` 中的控制器执行，这实现了"工具定义"与"平台实现"的解耦：

```python
# tap_wrapper 内部伪代码
async def run(self, ctx: MobileUseContext, x: int, y: int):
    # 通过 ctx 获取对应平台的控制器
    controller = get_controller(ctx)  # AndroidController / iOSController / ...
    await controller.tap(x, y)        # 统一接口，不同平台不同实现
```

这意味着同一套工具定义自动适配 Android/iOS/云设备，无需为每个平台重写工具。

## ExecutorToolNode：工具执行节点

`ExecutorToolNode` 继承自 LangGraph 的 `ToolNode`，定制了：

- **错误处理**：工具执行失败时将错误信息写入 `executor_messages`，让 Executor LLM 看到错误并重试
- **追踪记录**：工具调用前后记录到 trace 目录，支持GIF回放
- **消息键隔离**：使用 `executor_messages` 而非全局 `messages`，避免污染高层上下文

## 工具扩展：添加自定义工具

### 方式一：直接添加 ToolWrapper

```python
from minitap.mobile_use.tools.tool_wrapper import ToolWrapper
from minitap.mobile_use.tools.index import EXECUTOR_WRAPPERS_TOOLS

# 定义自定义工具
def my_custom_tool(ctx, param1: str) -> str:
    """工具描述（对LLM可见）"""
    # 实现逻辑，使用 ctx 访问设备控制器
    return f"Result for {param1}"

my_wrapper = ToolWrapper(
    name="my_custom_tool",
    description="Description that tells the LLM when to use this tool",
    params_schema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param1"]
    },
    run=my_custom_tool
)

# 注册到工具列表
EXECUTOR_WRAPPERS_TOOLS.append(my_wrapper)
```

### 方式二：通过控制器扩展（推荐跨平台工具）

如果自定义工具需要跨平台支持，应该：

1. 在 `MobileDeviceController` 基类添加抽象方法
2. 在 `AndroidController`、`iOSController` 等实现具体逻辑
3. 创建 ToolWrapper 调用控制器方法

参考 `controllers/device_controller.py` 的现有抽象方法。

## 工具选择策略

Cortex 决定使用哪些工具时遵循的隐式规则（从 prompt 模板推导）：

1. **能用 tap 就不用 input**：如果 UI 上有按钮/选项，优先点击而非输入
2. **滑动前先等待**：页面切换后优先 wait_for_delay，避免UI未就绪
3. **launch_app 是硬切换**：需要跳转到其他App时用 launch_app，不要试图按Home键找图标
4. **back 是安全退路**：走错路时用 back 返回，不要乱点
5. **输入前先聚焦**：用 focus_and_input_text 而非先 tap 再 input，减少步骤

## 工具执行的幂等性与安全

- tap/swipe/back 等操作天然幂等（重复执行无副作用）
- erase_one_char/focus_and_clear_text 重复执行会清空更多内容，Executor 需注意
- launch_app 重复调用会重启App，Orchestrator 会管理App状态
- 没有"确认框"机制——所有操作直接执行，锁定App包名（locked_app_package）是主要的安全边界

> **源码参考**:
> - [tools/index.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/tools/index.py) - 工具索引与注册
> - [tools/tool_wrapper.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/tools/tool_wrapper.py) - ToolWrapper基类
> - [tools/mobile/](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/tools/mobile/) - 13个移动操作工具实现
