---
title: "简单照片整理器"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/examples/simple-photo-organizer"
x-toml-ref: "../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/04-examples/01-simple-photo-organizer.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "examples", "beginner", "pydantic"]
summary: "最基础的入门示例，展示如何使用默认配置创建 Agent、执行任务并获取结构化输出。"
---
# 简单照片整理器

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/examples/simple-photo-organizer

本示例演示了一种无需 Builder 或高级配置的简单 SDK 使用方式，执行一个真实世界的自动化任务。

本示例代码可在 GitHub 获取：[simple_photo_organizer.py](https://github.com/minitap-ai/mobile-use/blob/main/minitap/mobile_use/sdk/examples/simple_photo_organizer.py)

## 示例功能

本示例自动完成以下任务：
1. 打开照片/图库应用
2. 查找指定日期拍摄的照片
3. 创建新相册
4. 将照片移动到相册中
5. 返回结构化的整理结果

## 核心概念

### 简单 Agent 创建
使用默认配置，最少的设置即可开始

### 结构化输出
返回类型化的 Pydantic 模型，获得类型安全的结果

### 直接使用 run_task
简单任务无需使用 Builder

### 错误处理
规范的 try/except/finally 模式

## 完整代码

```python
import asyncio
from datetime import date, timedelta
from pydantic import BaseModel, Field
from minitap.mobile_use.sdk import Agent

class PhotosResult(BaseModel):
    """照片搜索的结构化结果。"""

    found_photos: int = Field(..., description="找到的照片数量")
    date_range: str = Field(..., description="找到照片的日期范围")
    album_created: bool = Field(..., description="是否创建了相册")
    album_name: str = Field(..., description="创建的相册名称")
    photos_moved: int = Field(0, description="移动到相册的照片数量")

async def main() -> None:
    # 使用默认配置创建简单的 Agent
    agent = Agent()

    try:
        # 初始化 Agent（查找设备、启动必要的服务）
        await agent.init()

        # 计算昨天的日期作为示例
        yesterday = date.today() - timedelta(days=1)
        formatted_date = yesterday.strftime("%B %d")  # 例如 "August 22"

        print(f"Looking for photos from {formatted_date}...")

        # 第一个任务：搜索照片并整理，带类型化输出
        result = await agent.run_task(
            goal=(
                f"Open the Photos/Gallery app. Find photos taken on {formatted_date}. "
                f"Create a new album named '{formatted_date} Memories' and "
                f"move those photos into it. Count how many photos were moved."
            ),
            output=PhotosResult,
            name="organize_photos",
        )

        # 处理并显示结果
        if result:
            print("\n=== Photo Organization Complete ===")
            print(f"Found: {result.found_photos} photos from {result.date_range}")

            if result.album_created:
                print(f"Created album: '{result.album_name}'")
                print(f"Moved {result.photos_moved} photos to the album")
            else:
                print("No album was created")
        else:
            print("Failed to organize photos")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 始终清理资源
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

## 代码详解

### 1. 定义输出结构

```python
class PhotosResult(BaseModel):
    found_photos: int = Field(..., description="Number of photos found")
    date_range: str = Field(..., description="Date range of photos found")
    album_created: bool = Field(..., description="Whether an album was created")
    album_name: str = Field(..., description="Name of the created album")
    photos_moved: int = Field(0, description="Number of photos moved to the album")
```

使用详细的字段描述帮助 LLM 准确提取数据。字段描述越清晰，LLM 返回的结果越准确。

### 2. 使用默认配置创建 Agent

```python
agent = Agent()
```

对于简单用例，无需任何配置。Agent 将使用默认设置。

### 3. 初始化 Agent

```python
await agent.init()
```

这会连接到第一个可用设备并启动必要的服务。

> **注意**：`init()` 现在是异步方法，必须使用 await 调用。

### 4. 使用结构化输出运行任务

```python
result = await agent.run_task(
    goal="...",  # 自然语言目标
    output=PhotosResult,  # Pydantic 输出模型
    name="organize_photos"  # 可选的任务名称
)
```

结果会自动验证并类型化为 `PhotosResult | None`。

### 5. 始终清理资源

```python
finally:
    await agent.clean()
```

始终在 `finally` 块中调用 `await agent.clean()` 以确保资源被释放。

> **注意**：`clean()` 现在也是异步方法。

## 运行示例

确保已：
1. 安装了 Mobile Use SDK
2. 配置了 LLM（通过 `llm-config.override.jsonc` 或环境变量）
3. 连接了 Android/iOS 设备或模拟器
4. 设备上有照片应用

运行命令：

```shellscript
python simple_photo_organizer.py
```

## 预期输出

```text
Looking for photos from October 08...

=== Photo Organization Complete ===
Found: 12 photos from October 08
Created album: 'October 08 Memories'
Moved 12 photos to the album
```

## 自定义想法

### 修改日期范围

```python
# 上周
week_ago = date.today() - timedelta(days=7)

# 特定日期
specific_date = date(2024, 10, 1)
```

### 按照片类型筛选

```python
goal = (
    f"Find all selfie photos from {formatted_date} and "
    f"create an album called 'Selfies - {formatted_date}'"
)
```

### 创建多个相册

```python
# 依次运行多个任务
for i in range(7):
    day = date.today() - timedelta(days=i)
    await agent.run_task(
        goal=f"Organize photos from {day.strftime('%B %d')}",
        output=PhotosResult
    )
```

## 下一步

- **应用锁消息示例**：学习如何将执行限制在特定应用内
- **智能通知助手**：探索包含多 Profile 的更高级示例
- **SDK 参考**：浏览完整 SDK 文档
