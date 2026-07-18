---
title: "最佳实践"
category: "learning"
source: "https://www.minitap.ai/docs"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/best-practices.toml"
date: "2026-07-07"
tags: ["best-practices", "minitest", "mobile-use", "最佳实践", "guidelines"]
summary: "从官方文档中提取的minitest产品使用和mobile-use SDK开发最佳实践，帮助用户高效使用工具并避免常见陷阱。"
---
# 最佳实践

> **来源**: https://www.minitap.ai/docs

本页面汇总了使用minitest和mobile-use SDK的最佳实践建议，帮助您充分发挥工具潜力并避免常见陷阱。

---

## 第一部分：minitest 产品使用最佳实践

### 用户故事编写

#### 实践1：基于用户任务而非UI元素编写故事

**核心原则**：测试的单元应该是应用要完成的"任务"(job)，而不是绑定在某个界面上的脚本。

**✅ 推荐做法**：
```
作为用户，我希望能够登录账户
- 给定我在登录页面
- 当我输入有效的用户名和密码并点击登录按钮
- 那么我应该成功进入主页
- 并且看到欢迎消息
```

**❌ 避免做法**：
```
测试登录按钮
- 点击id为"btn-login"的元素
- 检查文本是否为"Login"
- 验证跳转到"/home"路由
```

**理由**：基于用户意图的测试能够适应UI重构，而基于选择器的测试在UI变化后会失效。

#### 实践2：编写清晰、可观察的验收标准

每个验收标准应该是：
- **可观察的**：通过屏幕上可见的结果验证，而非内部状态
- **具体的**：避免模糊的描述如"应该正常工作"
- **独立的**：每个标准验证一件事
- **业务导向的**：反映真实用户关心的结果

**示例**：
| 不好的标准 | 好的标准 |
|---|---|
| "登录功能应该工作" | "点击登录后，应显示包含用户名的欢迎消息" |
| "表单应该验证" | "提交空表单时，每个必填字段下应显示红色错误提示" |

#### 实践3：合理组织套件结构

- **按用户旅程组织**：将相关的用户故事组织在一起（如注册流程、购物流程、账户设置）
- **控制故事粒度**：一个故事测试一个完整的用户旅程，不要拆得太碎也不要太复杂
- **使用前置条件**：利用Profile和配置文件处理登录状态等前置条件，避免每个故事都从登录开始

---

### 测试运行策略

#### 实践4：在CI中集成minitest，每次PR自动运行

- 将minitest作为PR检查的一部分，确保每次代码变更都经过回归测试
- 测试通过时显示绿色检查标记，测试失败时阻止合并
- 利用Slack集成实时通知失败情况，附带视频时间戳和修复提示

**典型工作流**：
1. 开发者提交PR
2. minitest自动运行完整回归测试（30-60分钟）
3. 测试通过 → PR显示绿色标记，可安全合并
4. 测试失败 → Slack通知，包含视频、复现步骤、修复提示
5. 开发者根据提示修复问题，推送更新，重新运行测试

#### 实践5：充分利用Mini的自主能力

- **让Mini自动维护套件**：Mini会在功能发布时添加故事，在功能消失时停用故事，在屏幕更改时重写标准
- **信任Mini的分类，但保留最终决定权**：Mini会自动推断问题严重性，但您可以按问题覆盖它
- **关注Suggestions（建议）**：Suggestions会标记验收标准之外的视觉回归、文案更改等问题，不要忽略

#### 实践6：配置合适的Profile和测试数据

- 为不同用户角色创建独立的Profile（普通用户、管理员、付费用户等）
- 使用专用测试账号，避免使用生产环境账号
- 在Mini's Memory中提供应用的额外上下文，帮助Mini更好地理解您的应用
- 通过MCP服务器或CLI设置Mini's Memory，记录应用的特殊导航路径或已知问题

---

### 问题分类与处理

#### 实践7：及时分类问题，建立反馈闭环

- **Acknowledge（确认）**：确认收到问题，让团队知道您在处理
- **标记非bug**：如果问题是预期行为或误报，标记为非bug，Mini会学习
- **标记已解决**：修复后标记为已解决，验证修复效果
- 大多数分类可以直接在Slack线程中完成，无需切换到仪表板

#### 实践8：善用修复提示（Fix Prompt）

- Mini为每个失败标准生成的修复提示可以直接粘贴到Cursor或Claude中
- 修复提示包含根本原因分析、复现步骤和建议修复方案
- 结合设备日志可以更快定位问题

#### 实践9：利用会话回放调试

- 失败时提供的完整会话回放视频是调试的宝贵资源
- 视频带时间戳，可以直接跳转到失败时刻
- 结合运行时日志和复现步骤，快速定位问题根源

---

### 集成与协作

#### 实践10：从团队已经使用的工具触发运行

minitest支持从多个地方触发运行，选择团队最习惯的方式：
- **CI/CD**：GitHub Actions等（推荐用于自动化流程）
- **仪表板**：手动触发测试
- **Slack**：通过Slash命令快速触发
- **CLI/MCP**：从Cursor、Claude Code等AI编辑器中触发

**关键**：无论从哪里触发，结果都统一汇总到仪表板的问题标签页中。

#### 实践11：理解能力边界，设置合理预期

在使用前阅读[能力范围文档](minitest-docs/05-reference/01-capabilities.md)，了解：
- ✅ Mini能做什么
- 🔄 即将推出什么
- ❌ Mini目前不能做什么
- 🚫 不在路线图上的功能

这将帮助您避免在不支持的场景上浪费时间，并合理规划测试策略。

---

## 第二部分：Mobile Use SDK 开发最佳实践

### 环境设置

#### 实践12：使用Python 3.12+和虚拟环境

- 始终使用Python 3.12或更高版本
- 使用uv或venv创建独立的虚拟环境，避免依赖冲突
- 使用uv进行包管理（更快、更可靠）：

```shellscript
# 推荐：使用uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.12
source .venv/bin/activate
uv add minitap-mobile-use
```

#### 实践13：正确配置环境变量

- 使用.env文件管理API密钥和配置
- 不要将API密钥硬编码在代码中
- 确保.env文件在.gitignore中

```python
from dotenv import load_dotenv
load_dotenv()  # 显式加载.env文件
```

必要的API密钥（根据使用的LLM配置）：
```
OPENAI_API_KEY=sk-...
XAI_API_KEY=xai-...
OPEN_ROUTER_API_KEY=sk-or-...
GOOGLE_API_KEY=...
```

---

### 任务设计

#### 实践14：任务目标要具体明确

**❌ 模糊的目标**：
```python
goal = "Check the weather"
```

**✅ 具体的目标**：
```python
goal = "Open the Weather app, check the current temperature in Celsius for New York, and tell me tomorrow's forecast"
```

好的目标应该包含：
- 要打开的应用或位置
- 要执行的具体操作
- 期望的结果或要提取的信息
- 任何相关的上下文（位置、用户名等）

#### 实践15：复杂任务分解为小步骤

不要试图在一个任务中完成太多操作：

**❌ 过于复杂**：
```python
await agent.run_task(
    goal="Open settings, go to network, enable airplane mode, "
         "wait 5 seconds, then disable airplane mode, "
         "then check if network is restored"
)
```

**✅ 分解为步骤**：
```python
await agent.run_task(goal="Open settings and go to network settings")
await agent.run_task(goal="Enable airplane mode")
await asyncio.sleep(5)
await agent.run_task(goal="Disable airplane mode")
await agent.run_task(goal="Verify network connection is restored")
```

#### 实践16：使用Pydantic定义结构化输出

始终使用Pydantic模型定义期望的输出结构，这可以：
- 获得类型安全的结果
- 帮助LLM理解应该返回什么
- 自动验证输出格式

```python
from pydantic import BaseModel, Field
from typing import List

class ProductInfo(BaseModel):
    name: str = Field(..., description="Product name")
    price: float = Field(..., description="Product price in USD")
    rating: float = Field(..., description="Product rating out of 5")
    in_stock: bool = Field(..., description="Whether the product is in stock")

class SearchResults(BaseModel):
    products: List[ProductInfo] = Field(..., description="List of products found")
    total_results: int = Field(..., description="Total number of results")

result = await agent.run_task(
    goal="Search Amazon for 'wireless headphones' and get info for the first 3 products",
    output=SearchResults
)
```

为每个字段提供清晰的description，这对LLM理解输出格式至关重要。

---

### Agent配置

#### 实践17：为不同组件选择合适的LLM

Mobile Use SDK使用多Agent架构，不同组件对模型的要求不同：

| 组件 | 模型要求 | 推荐模型 |
|---|---|---|
| **Planner** | 快速推理 | gpt-5-nano、gemini-2.5-flash |
| **Cortex** | **需要视觉能力**（核心组件） | o4-mini、gpt-5、gemini-2.5-pro |
| **Executor** | 指令遵循 | 小型快速模型即可 |
| **Hopper** | 大上下文窗口（256k+） | 支持长上下文的模型 |

**不要为所有组件使用同一个模型**——这会增加成本并降低速度。为非核心组件使用更便宜更快的模型，为Cortex保留最强的视觉模型。

**配置示例**：
```python
from minitap.mobile_use.config import LLM, LLMConfig, LLMWithFallback

profile = AgentProfile(
    name="cost-effective",
    llm_config=LLMConfig(
        planner=LLM(provider="openai", model="gpt-5-nano"),
        orchestrator=LLM(provider="google", model="gemini-2.5-flash"),
        contextor=LLM(provider="openai", model="gpt-5-nano"),
        cortex=LLMWithFallback(
            provider="openai",
            model="o4-mini",
            fallback=LLM(provider="google", model="gemini-2.5-pro")
        ),
        executor=LLM(provider="openrouter", model="meta-llama/llama-4-scout"),
        hopper=LLM(provider="openai", model="gpt-5"),
        outputter=LLM(provider="openai", model="gpt-5-nano")
    )
)
```

#### 实践18：为关键配置添加Fallback

为Cortex等核心组件配置fallback模型，在主模型不可用时自动切换：

```python
cortex=LLMWithFallback(
    provider="openai",
    model="o4-mini",
    fallback=LLM(provider="google", model="gemini-2.5-pro")
)
```

#### 实践19：根据任务复杂度调整max_steps

默认max_steps是400，对于简单任务足够；对于复杂任务，适当增加：

```python
# 简单任务：使用默认值即可
# 中等复杂度任务
task = agent.new_task("Do something moderately complex").with_max_steps(500).build()

# 复杂任务
task = agent.new_task("Very complex multi-step task").with_max_steps(800).build()
```

注意：max_steps不是越大越好，过大的max_steps可能导致任务陷入循环而不及时失败。

---

### 调试与可观测性

#### 实践20：开发期间始终启用追踪

开发和调试时，启用追踪录制可以帮助您理解Agent的决策过程：

```python
from pathlib import Path
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
trace_path = Path(f"./traces/{timestamp}")

task = (
    agent.new_task("Your task goal")
    .with_trace_recording(enabled=True, path=trace_path)
    .with_thoughts_output_saving(path=f"{trace_path}/thoughts.txt")
    .with_llm_output_saving(path=f"{trace_path}/output.json")
    .build()
)
```

任务完成后，检查追踪目录：
- 查看截图了解Agent看到了什么
- 读取thoughts.txt理解Agent的推理过程
- 检查output.json查看结构化输出
- 观看GIF回放了解完整执行过程

#### 实践21：启用调试日志

遇到问题时，启用详细日志：

```python
import logging

# 全局调试日志
logging.basicConfig(level=logging.DEBUG)

# 或专门针对mobile-use
from minitap.mobile_use.utils.logger import get_logger
logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)
```

#### 实践22：正确清理资源

始终确保Agent资源被正确清理：

```python
agent = Agent()
try:
    await agent.init()
    result = await agent.run_task(goal="Your task")
finally:
    await agent.clean()
```

或者使用上下文管理器（如果支持）：
```python
async with Agent() as agent:
    await agent.init()
    result = await agent.run_task(goal="Your task")
```

遇到服务器问题时，使用force clean：
```python
agent.clean(force=True)
agent.init()
```

---

### 设备连接

#### 实践23：优先使用有线连接，无线调试作为备选

- USB连接通常比无线连接更稳定
- 使用高质量USB线，避免USB集线器，直接连接到电脑
- 如遇连接不稳定，尝试重置ADB：`adb kill-server && adb start-server`
- 无线调试时确保Wi-Fi网络稳定

#### 实践24：Android设备正确配置

```shellscript
# 1. 启用开发者选项
# 设置 → 关于手机 → 点击"版本号"7次

# 2. 启用USB调试
# 设置 → 开发者选项 → USB调试

# 3. 验证连接
adb devices
# 应该看到设备列出，状态为"device"

# 4. 如遇连接问题
adb kill-server
adb start-server
adb devices
```

#### 实践25：iOS设备正确配置

```shellscript
# 1. 安装idb_companion
brew install idb-companion

# 2. 解锁设备，信任电脑
# 连接设备时，在设备上点击"信任"

# 3. 验证连接
idevice_id -l

# 4. 检查idb_companion状态
pgrep -l idb_companion
# 如未运行，启动：idb_companion --udid booted
```

---

### 性能与成本优化

#### 实践26：多提供商负载均衡避免速率限制

```python
llm_config = LLMConfig(
    planner=LLM(provider="openai", model="gpt-5-nano"),
    cortex=LLM(provider="google", model="gemini-2.5-flash"),
    executor=LLM(provider="openrouter", model="meta-llama/llama-4-scout")
)
```

在多个LLM提供商之间分配负载，避免单一提供商的速率限制。

#### 实践27：批量任务之间添加延迟

```python
import asyncio

tasks = ["task1", "task2", "task3"]
for task_goal in tasks:
    await agent.run_task(goal=task_goal)
    await asyncio.sleep(1)  # 短暂延迟避免触发速率限制
```

#### 实践28：复用Agent实例

不要为每个任务创建新的Agent实例，复用同一个实例可以避免重复的初始化开销：

```python
# ✅ 好：复用Agent
agent = Agent()
await agent.init()

for goal in task_goals:
    await agent.run_task(goal=goal)

await agent.clean()

# ❌ 不好：每次都创建新Agent
for goal in task_goals:
    agent = Agent()
    await agent.init()
    await agent.run_task(goal=goal)
    await agent.clean()
```

---

### 错误处理

#### 实践29：检查初始化结果

```python
agent = Agent()
if not await agent.init():
    print("Agent初始化失败，请检查设备连接和配置")
    exit(1)

# 初始化成功后再运行任务
result = await agent.run_task(goal="Your task")
```

#### 实践30：捕获并适当处理异常

```python
from minitap.mobile_use.sdk.exceptions import (
    DeviceNotFoundError,
    ServerStartupError,
    AgentNotInitializedError,
    TaskTimeoutError
)

try:
    agent = Agent()
    await agent.init()
    result = await agent.run_task(goal="Your task")
except DeviceNotFoundError:
    print("错误：未找到设备，请检查设备连接")
except ServerStartupError:
    print("错误：服务器启动失败，尝试清理后重试")
    agent.clean(force=True)
    await agent.init()
except AgentNotInitializedError:
    print("错误：Agent未初始化，请先调用agent.init()")
except TaskTimeoutError:
    print("错误：任务超时，请简化任务或增加max_steps")
except Exception as e:
    print(f"未知错误: {e}")
finally:
    await agent.clean()
```

---

### 报告Bug

#### 实践31：报告Bug时包含完整信息

报告问题时，请务必包含：

1. **Session ID**：错误输出中显示的UUID，帮助开发人员快速定位问题
2. **问题描述**：发生了什么？您期望发生什么？
3. **复现步骤**：最小化的复现步骤
4. **环境信息**：
   - 操作系统
   - Python版本（`python --version`）
   - SDK版本（`pip show minitap-mobile-use`）
   - 设备类型（Android/iOS，物理设备/模拟器）
5. **错误消息**：完整的错误日志和堆栈跟踪
6. **视觉证据**：截图、录屏或追踪文件（如适用）

Session ID示例：
```text
Session ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

在Pilot Extension中，Session ID显示在设备屏幕下方，点击即可复制。

---

> **返回总览**：[教程首页](../minitest-mobile-use-official-docs-wiki.md)
