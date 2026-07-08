---
title: "平台快速开始"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/platform-quickstart"
x-toml-ref: "../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/02-quickstarts/02-platform-quickstart.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "quickstart", "platform"]
summary: "Minitap平台快速开始指南，使用集中式配置和内置可观测性，无需LLM配置文件。"
---
# 平台快速开始

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/platform-quickstart

**🚀 大多数用户推荐此方式** - 通过集中式配置和内置可观测性更快上手。

**平台模式**使用[platform.mobile-use.ai](https://platform.mobile-use.ai/)在云端管理您的自动化任务和LLM配置。

## 为什么使用平台？

### ⚡ 更快的设置

**无需LLM配置文件** - 数分钟即可开始，无需数小时

### 📊 实时监控

实时追踪成本、执行时间和Agent推理过程

### 🔄 动态更新

无需更改代码即可更新任务提示和LLM模型

### 👥 团队协作

为您的组织集中管理任务和配置文件

### 🤖 所有OpenRouter模型

访问**OpenRouter上所有可用模型** - 无需单独管理API密钥

如果您需要完全控制LLM配置或离线功能，请与[本地开发](01-local-quickstart.md)进行比较。

## 前置条件与安装

**首次使用？** 在继续下面的平台特定配置之前，请先完成通用[安装指南](../01-introduction-installation/02-installation.md)步骤（SDK安装、设备设置等）。

## 配置平台凭证

在项目根目录创建一个`.env`文件，包含您的Minitap平台凭证：

```shellscript
# Minitap平台API密钥（从platform.mobile-use.ai获取）
MINITAP_API_KEY=your_api_key_here

# Minitap平台基础URL（可选 - 这是默认值）
MINITAP_BASE_URL=https://platform.mobile-use.ai/api/v1
```

切勿将`.env`文件提交到版本控制。请将其添加到`.gitignore`中。

**无需LLM配置文件！** 与本地开发不同，平台集中管理所有LLM配置。

---

## 平台任务配置选项

在平台上创建任务时，您有多个配置选项：

**基本字段：**

- **Task Name（任务名称）**：SDK代码中使用的唯一标识符
- **Description（描述）**：帮助团队成员理解任务用途
- **Agent Prompt（Agent提示）**：Agent的详细指令（使用"Generate"按钮获取AI辅助）
- **Output Description（输出描述）**：可选 - 描述结构化输出的预期JSON格式
- **Locked App Package（锁定应用包）**：可选 - 将执行限制在特定应用（如`com.whatsapp`）

**设置：**

- **Enable Tracing（启用追踪）**：在平台上显示完整的LLM提示/响应（出于隐私考虑可禁用）
- **Max Steps（最大步数）**：限制执行步数以防止成本失控（默认：400）

当设置了**Locked App Package**时，任务卡片会显示🔒指示符和包名。在提示中使用`<locked-app-package>`占位符动态引用它。

### LLM配置文件（可选）

默认情况下，任务使用Minitap管理的针对mobile-use优化的配置文件。您可以为以下场景创建自定义配置文件：

- 成本优化（使用更快/更便宜的模型）
- 性能优化（使用更强大的模型）
- 不同的任务类型（简单 vs 复杂）

所有模型使用`minitap`提供商，格式为：`provider/model-name`（例如，`openai/gpt-5`、`google/gemini-2.5-pro`）

平台支持[OpenRouter](https://openrouter.ai/models)上的**所有可用模型**，让您无需管理单独的API密钥即可访问OpenAI、Anthropic、Google、Meta等的最新模型。

**Agent组件：**

mobile-use Agent使用多Agent架构，其中不同的LLM处理特定任务：

#### Cortex（最关键 - 需要视觉能力）

**角色：** 系统的"眼睛"和决策者。分析截图，理解UI元素，决定下一步要采取什么行动。

**要求：** 必须支持视觉/图像输入

**推荐：** 使用可用的最佳视觉模型：

- `google/gemini-2.5-pro` - 出色的视觉 + 推理能力
- `openai/gpt-5` - 强大的视觉能力
- `anthropic/claude-3.5-sonnet` - 良好的视觉理解

**同时配置fallback**以在主模型失败时提高可靠性。

**影响：** 🔴 关键 - Cortex模型差 = 任务失败

#### Planner

**角色：** 将高级目标分解为可执行的子目标。在开始时运行一次，并可能在重新规划期间运行。

**要求：** 强大的推理和规划能力

**推荐：**

- `meta-llama/llama-4-scout` - 快速且能力强
- `openai/gpt-5-nano` - 快速规划
- `anthropic/claude-3-haiku` - 成本效益高

**影响：** 🟡 中等 - 影响执行策略

#### Orchestrator

**角色：** 协调执行流程，决定何时使用hopper vs cortex，管理状态转换。

**要求：** 快速，擅长决策

**推荐：** 快速模型：

- `openai/gpt-oss-120b` - 高效协调
- `openai/gpt-5-nano` - 快速决策

**影响：** 🟡 中等 - 影响执行效率

#### Executor

**角色：** 将高级决策转换为特定的设备操作（点击、滑动、输入）。

**要求：** 指令遵循，快速响应

**推荐：**

- `meta-llama/llama-3.3-70b-instruct` - 出色的指令遵循
- `openai/gpt-5-nano` - 快速执行

**影响：** 🟢 低 - 直接的任务

#### Hopper

**角色：** 挖掘大量数据（历史上下文、屏幕数据）以提取与达成目标最相关的信息。

**要求：** 大上下文窗口（建议256k+ tokens）以处理大量数据批次

**推荐：**

- `openai/gpt-4.1` - 256k上下文
- `google/gemini-2.0-flash` - 大上下文

**影响：** 🟡 中等 - 改进从大数据集中提取信息

#### Outputter

**角色：** 根据输出描述从任务结果中提取结构化输出。

**要求：** JSON格式化，结构化输出能力

**推荐：**

- `openai/gpt-5-nano` - 擅长JSON
- `anthropic/claude-3-haiku` - 结构化输出

**影响：** 🟢 低 - 仅在指定output_description时使用

### 结构化输出示例

对于类型安全的结果，使用Pydantic模型：

```python
from pydantic import BaseModel, Field

class NotificationSummary(BaseModel):
    total: int = Field(..., description="Total notifications")
    unread: int = Field(..., description="Unread count")

result = await agent.run_task(
    request=PlatformTaskRequest[NotificationSummary](
        task="check-notifications",
        profile="default"
    )
)

# result的类型为NotificationSummary | None
if result:
    print(f"Total: {result.total}, Unread: {result.unread}")
```

### 查看任务运行

访问[**Task Runs**](https://platform.mobile-use.ai/tasks/runs)查看执行详情：

点击任意运行查看：

- 执行状态和持续时间
- Agent思考和推理
- 子目标进展
- 成本明细

**追踪内容：**

**任务运行状态**

整个执行过程中的状态转换：

- `pending`：任务已创建，等待开始
- `running`：任务正在执行
- `completed`：任务成功完成并输出结果
- `failed`：任务遇到错误
- `cancelled`：任务被手动取消

**子目标与计划**

Planner Agent创建高级子目标。每个子目标都会被追踪：

- 名称/描述
- 状态：`pending` → `started` → `completed` / `failed`
- 开始和结束时间戳
- 重新规划时的计划更新

**Agent思考**

来自每个Agent组件的推理：

- **Planner**：目标分解和规划
- **Cortex**：视觉理解和决策
- **Orchestrator**：执行协调
- **Executor**：动作转换和执行
- **Hopper**：从大量批次中提取数据
- **Outputter**：结构化输出提取

每个思考都包含时间戳和Agent标识符。

**LLM追踪**

详细的LLM API调用指标（启用追踪时）：

- 使用的模型
- Token计数（输入/输出）
- 成本（美元）
- 延迟
- 请求/响应内容

### PlatformTaskRequest参考

**参数：**

- `task`（必需）：平台中的任务名称
- `profile`（可选）：LLM配置文件名称（默认为Minitap管理的配置文件）
- `api_key`（可选）：覆盖`MINITAP_API_KEY`环境变量
- `record_trace`（可选）：保存本地追踪文件
- `trace_path`（可选）：本地追踪目录

---

## 从平台UI运行任务（云端执行）

除了通过SDK运行任务外，您现在还可以**直接从平台UI**在云设备上执行自动化任务 - 无需本地设置。

**完全基于云**：云端执行完全在Minitap基础设施上运行。无需Python SDK安装，无需本地设备连接。

### 设备状态指示符

| 状态 | 描述 |
| --- | --- |
| **Ready** | 设备已启动并可立即执行 |
| **Starting** | 设备正在启动 |
| **Stopping** | 设备正在关闭 |
| **Stopped** | 设备已关机（将提示启动） |

Ready状态的设备有保持机制以保持可用。您只需为活跃使用时间付费。

### 本地 vs 云端执行对比

| 功能 | 本地（SDK） | 云端执行 |
| --- | --- | --- |
| **所需设置** | Python + SDK安装 + 设备 | 无 |
| **设备** | 物理设备或模拟器 | 云端管理 |
| **执行** | 在您的机器上 | 平台服务器 |
| **最适合** | 开发、调试、自定义集成 | 生产、无代码用户、快速测试 |
| **实时监控** | 通过平台追踪 | 内置并重定向到任务运行 |

---

## 平台 vs 本地对比

### 何时使用本地方式

如果您需要以下功能，请使用[本地方式](01-local-quickstart.md)：

- 完全控制LLM提供商选择和API端点
- 自定义基础设施或隔离环境
- 无需互联网依赖的离线能力
- 使用本地模型配置进行开发和测试

---

## 下一步

- [本地快速开始](01-local-quickstart.md) - 了解本地方式进行比较
- [类型参考](../05-sdk-reference/04-types.md) - PlatformTaskRequest类型文档
- [使用示例](../04-examples/00-overview.md) - 更多平台示例
