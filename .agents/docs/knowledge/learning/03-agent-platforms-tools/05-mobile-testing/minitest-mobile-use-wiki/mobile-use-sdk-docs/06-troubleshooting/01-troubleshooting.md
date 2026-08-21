---
title: "常见问题排查"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/troubleshooting"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/06-troubleshooting/01-troubleshooting.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "troubleshooting", "debugging", "device-connection", "server-issues"]
summary: "诊断和解决使用 Mobile Use SDK 时的常见问题，包括设备连接、服务器启动、任务执行、LLM API 和系统环境问题。"
---
# 常见问题排查

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/troubleshooting

本指南帮助您诊断和解决使用 Mobile Use SDK 时的常见问题。

## 设备连接问题

### 未找到设备

**症状**
- 错误：`DeviceNotFoundError: No device found. Exiting.`
- Agent 初始化失败

**解决方案**

**1. 验证设备连接**

```shellscript
adb devices
```

您应该看到设备列出，状态为"device"

```shellscript
idevice_id -l
```

**2. 启用 USB 调试（Android）**

- 设置 → 关于手机 → 点击"版本号"7次
- 设置 → 开发者选项 → USB 调试

**3. 信任电脑（iOS）**

- 解锁设备
- 出现提示时点击"信任"

**4. 重置 ADB**

```shellscript
adb kill-server
adb start-server
```

**5. 手动指定设备**

```python
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import DevicePlatform

config = (
    Builders.AgentConfig
    .for_device(platform=DevicePlatform.ANDROID, device_id="your_device_id")
    .build()
)
agent = Agent(config=config)
```

---

### USB 连接不稳定

**症状**
- 自动化过程中随机断开连接
- `adb: error: device 'xxx' not found`

**解决方案**

**1. 使用高质量 USB 线**

质量差的线缆可能导致间歇性连接。

**2. 直接连接到电脑**

避免使用可能导致不稳定的 USB 集线器。

**3. 增加 ADB 超时时间**

```shellscript
adb shell settings put global adb_timeout 0
```

**4. 使用无线调试**

```shellscript
# 启用 TCP/IP 模式
adb tcpip 5555

# 无线连接
adb connect <device_ip>:5555
```

确保无线调试时 Wi-Fi 连接稳定。

---

## 服务器相关问题

### 服务器启动失败

**症状**
- 初始化期间出现 `ServerStartupError`
- 端口已被占用
- 先前运行留下的僵尸进程

**解决方案**

**1. 强制清理僵尸服务器**

```python
agent = Agent()

# 终止任何现有的 mobile-use 服务器
agent.clean(force=True)

# 现在初始化
agent.init()
```

**2. 验证平台工具已安装**

```shellscript
adb version
```

如果未安装，请下载 [Android SDK Platform Tools](https://developer.android.com/tools/adb)

```shellscript
idb --help
```

如果未安装，通过以下方式安装：`brew install idb-companion`

**3. 检查 idb_companion 状态（iOS）**

```shellscript
# 检查 idb_companion 是否正在运行
pgrep -l idb_companion

# 如果需要，启动 idb_companion
idb_companion --udid booted
```

**4. 检查端口冲突**

```shellscript
# Linux/Mac
lsof -i :8000
lsof -i :8001

# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :8001
```

---

## 任务执行问题

### Agent 未初始化

**症状**
- 错误：`AgentNotInitializedError`

**解决方案**

始终在运行任务前调用 `agent.init()`：

```python
agent = Agent()

# 先初始化！
if not agent.init():
    print("初始化失败")
    exit(1)

# 现在可以运行任务
await agent.run_task(goal="Your task")
```

---

### 任务超时或失败

**症状**
- 任务卡住或无法完成
- 达到 max_steps 限制
- 意外结果

**解决方案**

**1. 简化任务目标**

将复杂任务分解为更小的步骤：

```python
# ❌ 过于复杂
await agent.run_task(
    goal="Open settings, go to network, enable airplane mode, "
         "wait 5 seconds, then disable airplane mode"
)

# ✅ 分解为步骤
await agent.run_task(goal="Open settings and go to network settings")
await agent.run_task(goal="Enable airplane mode")
await asyncio.sleep(5)
await agent.run_task(goal="Disable airplane mode")
```

**2. 增加 max_steps 限制**

```python
task = (
    agent.new_task("Complex goal...")
    .with_max_steps(500)  # 默认值为 400
    .build()
)

await agent.run_task(request=task)
```

**3. 启用追踪进行调试**

```python
task = (
    agent.new_task("Your goal")
    .with_trace_recording(enabled=True)
    .build()
)

await agent.run_task(request=task)
# 在 mobile-use-traces/ 目录中检查追踪
```

**4. 目标描述更具体**

```python
# ❌ 模糊
goal = "Check the weather"

# ✅ 具体
goal = "Open the Weather app, check the current temperature in Celsius for New York, and tell me tomorrow's forecast"
```

---

### 任务结果不正确

**症状**
- 任务返回意外或不完整的数据
- 结构化输出字段缺失或不正确

**解决方案**

**1. 使用带有清晰描述的结构化输出**

```python
from pydantic import BaseModel, Field

class WeatherInfo(BaseModel):
    current_temp: float = Field(
        ..., 
        description="Current temperature in Celsius"
    )
    condition: str = Field(
        ..., 
        description="Current weather condition (sunny, cloudy, rainy, etc.)"
    )
    tomorrow_forecast: str = Field(
        ..., 
        description="Detailed weather forecast for tomorrow"
    )

result = await agent.run_task(
    goal="Check weather for today and tomorrow",
    output=WeatherInfo
)
```

**2. 在目标中提供更多上下文**

```python
# ❌ 不清晰
goal = "Get product info"

# ✅ 清晰
goal = "Go to Amazon, search for 'wireless headphones', open the first result, and get the product name, price, and rating"
```

**3. 为 cortex 使用更好的 LLM 模型**

```python
from minitap.mobile_use.config import LLM, LLMConfig, LLMWithFallback

profile = AgentProfile(
    name="accurate",
    llm_config=LLMConfig(
        cortex=LLMWithFallback(
            provider="openai",
            model="o4-mini",  # 更强大的模型
            fallback=LLM(provider="openai", model="gpt-5")
        ),
        # ... 其他组件
    )
)
```

---

## LLM 和 API 问题

### API 密钥认证

**症状**
- 401 未授权错误
- 认证失败错误

**解决方案**

**1. 在 .env 文件中验证 API 密钥**

```shellscript
# 根据您的 LLM 配置需要
OPENAI_API_KEY=sk-...
XAI_API_KEY=xai-...
OPEN_ROUTER_API_KEY=sk-or-...
GOOGLE_API_KEY=...
```

**2. 加载环境变量**

SDK 会自动加载 `.env` 文件，但您也可以手动设置：

```python
import os
from dotenv import load_dotenv

load_dotenv()  # 显式加载

# 或编程方式设置
os.environ["OPENAI_API_KEY"] = "your_key"
```

**3. 检查 API 密钥有效性**

直接测试您的密钥：

```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[{"role": "user", "content": "test"}]
)
print("API 密钥有效！")
```

---

### 速率限制

**症状**
- 429 Too Many Requests 错误
- 任务随时间变慢

**解决方案**

**1. 使用不同的提供商**

在多个 LLM 提供商之间分配负载：

```python
llm_config = LLMConfig(
    planner=LLM(provider="openai", model="gpt-5-nano"),
    cortex=LLM(provider="google", model="gemini-2.5-flash"),
    executor=LLM(provider="openrouter", model="meta-llama/llama-4-scout")
)
```

**2. 使用层级限制**

检查您的 API 层级限制并在需要时升级。

**3. 在任务之间添加延迟**

```python
import asyncio

for task_goal in task_list:
    await agent.run_task(goal=task_goal)
    await asyncio.sleep(2)  # 短暂延迟
```

---

## 系统环境问题

### Python 版本兼容性

**症状**
- 导入错误或语法错误
- `SyntaxError` 或 `ModuleNotFoundError`

**解决方案**

确保您使用 Python 3.12 或更高版本：

```shellscript
python --version
# 应为 3.12.x 或更高
```

**创建兼容环境：**

- 使用 uv：

```shellscript
# UV 自动处理 Python 版本
curl -LsSf https://astral.sh/uv/install.sh | sh

uv venv --python 3.12
source .venv/bin/activate
uv add minitap-mobile-use
```

- 使用 venv：

```shellscript
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install minitap-mobile-use
```

---

### 导入错误

**症状**
- `ModuleNotFoundError: No module named 'minitap'`
- SDK 组件的导入错误

**解决方案**

**1. 验证安装**

```shellscript
pip list | grep minitap
# 应显示：minitap-mobile-use
```

**2. 重新安装 SDK**

```shellscript
pip uninstall minitap-mobile-use
pip install minitap-mobile-use
```

**3. 检查虚拟环境**

确保您在正确的虚拟环境中：

```shellscript
which python
# 应指向您的 venv
```

---

## 调试最佳实践

### 启用全面日志记录

```python
import logging

# 启用调试日志
logging.basicConfig(level=logging.DEBUG)

# 或专门针对 mobile-use
from minitap.mobile_use.utils.logger import get_logger

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)
```

### 使用追踪录制

开发期间始终启用追踪：

```python
from pathlib import Path
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
trace_path = Path(f"/tmp/debug_traces/{timestamp}")

task = (
    agent.new_task("Your goal")
    .with_trace_recording(enabled=True, path=trace_path)
    .with_thoughts_output_saving(path=f"{trace_path}/thoughts.txt")
    .with_llm_output_saving(path=f"{trace_path}/output.json")
    .build()
)
```

### 检查追踪内容

任务失败后，检查追踪：

```shellscript
ls /tmp/debug_traces/20241009_175416/

# 查看截图以了解 Agent 看到了什么
# 读取 thoughts.txt 了解 Agent 推理过程
# 检查 output.json 查看结构化结果
```

---

## 获取帮助

### GitHub Issues

搜索现有问题或创建新问题

### Discord 社区

从社区获取帮助

### 提交 Bug 报告

提交问题时，请包含：

1. **Session ID** - 帮助我们快速调试您的问题（见下文）
2. **描述** - 发生了什么 vs. 您期望什么
3. **复现步骤** - 我们如何重现问题？
4. **环境** - 操作系统、Python 版本、设备类型（Android/iOS）
5. **错误消息** - 任何错误日志或堆栈跟踪
6. **截图/录屏** - 如适用的视觉证据

## 快速参考

**清理僵尸服务器**
```python
agent.clean(force=True)
agent.init()
```

**检查设备连接**
```shellscript
# Android
adb devices

# iOS
idevice_id -l
```

**启用调试日志**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**启用追踪**
```python
task = agent.new_task(goal).with_trace_recording(True).build()
```

**重置 ADB**
```shellscript
adb kill-server
adb start-server
```

## 下一步

- **SDK 参考**：完整的 SDK 文档
- **使用示例**：可运行的代码示例
