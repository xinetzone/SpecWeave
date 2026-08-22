---
title: "本地快速开始"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/quickstart"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/02-quickstarts/01-local-quickstart.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "quickstart", "local-development"]
summary: "本地开发快速开始指南，通过配置文件管理LLM设置，完全控制执行环境。"
---
# 本地快速开始

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/quickstart

本指南介绍**本地开发**模式，您可以通过配置文件配置LLM，并完全控制执行环境。

**想要更快的设置？** 请查看[平台快速开始](02-platform-quickstart.md) - 无需LLM配置文件，内置可观测性！

在继续之前，请确保您已完成[安装指南](../01-introduction-installation/02-installation.md)中的步骤。

## 配置LLM设置

### 1. 创建LLM配置文件

创建一个`llm-config.override.jsonc`文件来配置您的LLM模型。此文件将覆盖[默认配置](https://github.com/minitap-ai/mobile-use/blob/main/llm-config.defaults.jsonc)。

```jsonc
// 您的自定义LLM配置
{
  "planner": {
    "provider": "openai",
    "model": "gpt-5-nano"
  },
  "orchestrator": {
    "provider": "openai",
    "model": "gpt-5-nano"
  },
  "contextor": {
    // 可选：仅在使用应用锁功能时需要
    "provider": "openai",
    "model": "gpt-5-nano",
    "fallback": {
      "provider": "openai",
      "model": "gpt-5-mini"
    }
  },
  "cortex": {
    // 重要提示：需要视觉能力！
    // 推荐：gpt-4o、gpt-5或等效的支持视觉的模型
    "provider": "openai",
    "model": "gpt-4o",
    "fallback": {
      "provider": "openai",
      "model": "gpt-5"
    }
  },
  "executor": {
    "provider": "openai",
    "model": "gpt-5-nano"
  },
  "utils": {
    "hopper": {
      // 至少需要256k上下文窗口
      "provider": "openai",
      "model": "gpt-5-nano"
    },
    "outputter": {
      "provider": "openai",
      "model": "gpt-5-nano"
    }
  }
}
```

### 2. 配置环境变量

在项目根目录创建一个`.env`文件，包含必要的API密钥：

```shellscript
# LLM API密钥（仅包含您需要的）
OPENAI_API_KEY=your_key_here
XAI_API_KEY=your_key_here
OPEN_ROUTER_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# 可选：用于本地LLM或自定义OpenAI兼容端点
# OPENAI_BASE_URL=http://localhost:1234/v1
```

切勿将`.env`文件提交到版本控制。请将其添加到`.gitignore`中。

---

## 创建您的第一个自动化脚本

让我们编写一个简单的脚本，打开计算器应用并执行基本计算。

更多示例请查看GitHub上的[mobile-use SDK示例目录](https://github.com/minitap-ai/mobile-use/tree/main/minitap/mobile_use/sdk/examples)。

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import AgentProfile
from minitap.mobile_use.sdk.builders import Builders

async def main():
    # 创建Agent配置文件
    default_profile = AgentProfile(
        name="default",
        from_file="llm-config.override.jsonc"
    )

    # 配置Agent
    agent_config = Builders.AgentConfig.with_default_profile(default_profile).build()
    agent = Agent(config=agent_config)

    try:
        # 初始化Agent（连接到第一个可用设备）
        await agent.init()

        # 定义简单的任务目标
        result = await agent.run_task(
            goal="Open the calculator app, calculate 123 * 456, and tell me the result",
            name="calculator_demo"
        )

        # 打印结果
        print(f"Result: {result}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 完成后始终清理资源
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

### 运行脚本

```shellscript
python calculator_demo.py
```

## 获取结构化输出

Mobile-use SDK可以使用Pydantic模型返回结构化数据：

```python
import asyncio
from pydantic import BaseModel, Field
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import AgentProfile
from minitap.mobile_use.sdk.builders import Builders

# 定义结构化输出模型
class CalculationResult(BaseModel):
    expression: str = Field(..., description="The mathematical expression calculated")
    result: float = Field(..., description="The result of the calculation")
    app_used: str = Field(..., description="The name of the calculator app used")

async def main():
    # 创建Agent
    default_profile = AgentProfile(
        name="default",
        from_file="llm-config.override.jsonc"
    )
    agent_config = Builders.AgentConfig.with_default_profile(default_profile).build()
    agent = Agent(config=agent_config)

    try:
        await agent.init()

        # 使用Pydantic模型请求结构化输出
        result = await agent.run_task(
            goal="Open the calculator app, calculate 123 * 456, and tell me the result",
            output=CalculationResult,
            name="structured_calculator"
        )

        if result:
            print(f"Expression: {result.expression}")
            print(f"Result: {result.result}")
            print(f"App used: {result.app_used}")

    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

使用Pydantic模型可确保自动化任务获得类型安全、经过验证的输出。

## 代码理解

### Agent配置文件

```python
default_profile = AgentProfile(
    name="default", 
    from_file="llm-config.override.jsonc"
)
```

`AgentProfile`定义了哪些LLM模型为Agent的不同组件提供支持。

### Agent配置

```python
agent_config = Builders.AgentConfig.with_default_profile(default_profile).build()
```

`Builders.AgentConfig`提供了流式API来配置您的Agent。

### 运行任务

```python
result = await agent.run_task(
    goal="Your instruction here",
    output=YourPydanticModel,  # 可选
    name="task_name"  # 可选
)
```

任务以异步方式执行，并可返回结构化输出。

## 本地模式 vs 平台模式

### ✅ 何时使用本地模式

- 需要完全控制LLM提供商选择和API端点
- 需要自定义基础设施或离线环境
- 需要离线能力，不依赖互联网
- 使用本地模型配置进行开发和测试

### 🚀 何时使用平台模式

- 希望快速设置，无需配置LLM文件
- 需要实时监控成本、执行时间和Agent推理
- 希望动态更新任务提示和LLM模型而无需更改代码
- 需要团队协作功能
- 希望访问OpenRouter上的所有模型

## 下一步

- [核心概念](../03-core-concepts/00-overview.md) - 了解架构和组件
- [使用示例](../04-examples/00-overview.md) - 探索更多实际示例
- [SDK参考](../05-sdk-reference/00-overview.md) - 详细的SDK文档
- [故障排除](../06-troubleshooting/00-overview.md) - 常见问题和解决方案
