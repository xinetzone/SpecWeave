---
source: d:\AI\.chaos\libs\mobile-use
---

# 快速开始

## 前置条件

| 平台 | 必需工具 |
|---|---|
| **通用** | Python 3.12+, [uv](https://github.com/astral-sh/uv) 包管理器 |
| **Android** | [ADB (Android Debug Bridge)](https://developer.android.com/studio/releases/platform-tools) |
| **iOS 模拟器** (仅 macOS) | [Xcode](https://developer.apple.com/xcode/), [fb-idb](https://fbidb.io/docs/installation/) |
| **iOS 真机** | WebDriverAgent (WDA) |

## 安装方式

### 方式一：Docker 快速启动（推荐新手）

Android 设备/模拟器用户可直接用 Docker 脚本，无需配置 Python 环境：

**Linux/macOS:**
```bash
chmod +x mobile-use.sh
bash ./mobile-use.sh \
  "Open Gmail, find first 3 unread emails, and list their sender and subject line" \
  --output-description "A JSON list of objects, each with 'sender' and 'subject' keys"
```

**Windows (PowerShell):**
```powershell
powershell.exe -ExecutionPolicy Bypass -File mobile-use.ps1 `
  "Open Gmail, find first 3 unread emails, and list their sender and subject line" `
  --output-description "A JSON list of objects, each with 'sender' and 'subject' keys"
```

> 设备需通过 USB 连接并开启 USB 调试，且与电脑在同一 WiFi 网络。

### 方式二：从源码安装（开发者）

```bash
# 1. 克隆仓库
git clone https://github.com/minitap-ai/mobile-use.git && cd mobile-use

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 添加你的 API Key（至少配置一个 LLM Provider）

# 3. （可选）自定义 LLM 配置
cp llm-config.override.template.jsonc llm-config.override.jsonc

# 4. 创建虚拟环境并安装依赖
uv venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
uv sync
```

### 方式三：PyPI 安装（SDK使用）

```bash
pip install minitap-mobile-use
```

## 配置 API Key

在 `.env` 文件中至少配置一个 LLM Provider 的 API Key：

```env
# 任选其一或多个
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
ANTHROPIC_API_KEY=sk-ant-...
MINIMAX_API_KEY=...
XAI_API_KEY=...
OPEN_ROUTER_API_KEY=...
AZURE_API_KEY=...
```

> **MiniMax 用户注意**：MiniMax-M2.7 是官方推荐的高性能模型，支持200K上下文，性价比高。设置 `MINIMAX_API_KEY` 后可直接使用。

## 5分钟跑通第一个任务

### CLI 方式

连接好设备后，直接运行：

```bash
# 简单任务：查看电池电量
python ./minitap/mobile_use/main.py "Go to settings and tell me my current battery level"

# 数据抓取：获取未读邮件列表
python ./minitap/mobile_use/main.py \
  "Open Gmail, find all unread emails, and list their sender and subject line" \
  --output-description "A JSON list of objects, each with 'sender' and 'subject' keys"
```

### SDK 方式（推荐集成到自己的项目）

```python
import asyncio
from minitap.mobile_use import Agent

async def main():
    # 1. 创建 Agent 实例
    agent = Agent()
    
    # 2. 初始化（自动探测设备、连接客户端）
    await agent.init()
    
    try:
        # 3. 执行任务
        result = await agent.run_task(
            goal="Open Settings and tell me the battery percentage"
        )
        print("Result:", result)
    finally:
        # 4. 清理资源
        await agent.clean()

asyncio.run(main())
```

### SDK 结构化输出

```python
from pydantic import BaseModel
from minitap.mobile_use import Agent

class EmailInfo(BaseModel):
    sender: str
    subject: str

class EmailList(BaseModel):
    emails: list[EmailInfo]

async def get_unread():
    agent = Agent()
    await agent.init()
    try:
        # 传入 Pydantic 模型直接获得结构化结果
        result = await agent.run_task(
            goal="Open Gmail, find first 3 unread emails",
            output=EmailList  # 结构化输出
        )
        for email in result.emails:
            print(f"From: {email.sender}, Subject: {email.subject}")
    finally:
        await agent.clean()
```

### SDK Builder 模式（高级配置）

```python
from minitap.mobile_use import Agent, Builders

async def advanced_example():
    # 使用 Builder 配置 Agent
    config = (
        Builders.AgentConfig()
        .with_default_profile()
        .with_default_task_config(max_steps=50)  # 最大步数
        .build()
    )
    
    agent = Agent(config=config)
    await agent.init()
    
    try:
        # 使用 Builder 构建任务
        task = (
            agent.new_task("Open WhatsApp and send 'Hello' to Alice")
            .with_locked_app_package("com.whatsapp")  # 锁定在指定App内
            .with_max_steps(30)
            .with_name("send_whatsapp_message")
            .build()
        )
        
        result = await agent.run_task(request=task)
        print(result)
    finally:
        await agent.clean()
```

## 验证安装成功

运行以下命令检查设备连接：

```bash
# 检查 ADB 设备（Android）
adb devices

# 检查 iOS 模拟器（macOS）
xcrun simctl list devices booted
```

如果设备列表中能看到你的设备，运行 CLI 命令时 Agent 会自动探测并连接。

## 常见安装问题

| 问题 | 解决方案 |
|---|---|
| `No device found` | 确保设备已连接、USB调试已开启、ADB已安装 |
| `ExecutableNotFoundError: cli_tools` | 安装 ADB（Android）或确保 Xcode 命令行工具可用（iOS） |
| `Failed to start IDB companion` | 运行 `brew install idb-companion` 安装 fb-idb |
| Docker 无法连接设备IP | 检查防火墙设置，确保设备和电脑在同一WiFi |
| `ghcr.io` 拉取镜像失败 | 运行 `docker logout ghcr.io` 后重试 |

## 下一步

- 学习 [SDK 使用指南](sdk-guide.md) 了解更多 API 用法
- 阅读 [架构解析](architecture.md) 理解 9-Agent 协作原理
- 查看 [sdk/examples/](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/sdk/examples) 目录下的完整示例代码

> **示例代码参考**:
> - [simple_photo_organizer.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/sdk/examples/simple_photo_organizer.py) - 基础本地使用
> - [app_lock_messaging.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/sdk/examples/app_lock_messaging.py) - 锁定App+Builder模式
> - [smart_notification_assistant.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/sdk/examples/smart_notification_assistant.py) - 多Profile高级用法
