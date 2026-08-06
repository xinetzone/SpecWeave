---
source: d:\AI\.chaos\libs\mobile-use
---

# mobile-use Wiki 教程

> **项目**: mobile-use (minitap-mobile-use) v3.6.3
> **定位**: 自然语言控制手机的AI多智能体自动化框架
> **论文**: [Do Multi-Agents Dream of Electric Screens?](https://arxiv.org/abs/2602.07787)
> **基准**: AndroidWorld 100% 准确率（首个满分框架）

## 文档定位

本 Wiki 面向希望理解、使用或二次开发 mobile-use 的开发者，系统说明其多智能体架构、SDK 使用方式、设备适配层、工具系统和扩展机制。

mobile-use 不是简单的脚本自动化工具，而是一个基于 LangGraph 构建的 **9-Agent 分层协作系统**，通过自然语言指令驱动真实 Android/iOS 设备完成复杂任务。

## 核心特性

| 特性 | 说明 |
|---|---|
| 🗣️ 自然语言控制 | 用母语描述任务，Agent 自动拆解并执行 |
| 📱 UI感知自动化 | 基于无障碍树（Accessibility Tree）智能导航界面 |
| 📊 数据抓取 | 从任意App提取信息并结构化输出（JSON/Pydantic） |
| 🔧 可扩展LLM | 支持 OpenAI/Google/Anthropic/xAI/OpenRouter/MiniMax/Azure/Cerebras 等 |
| ☁️ 云端设备 | 支持 Limrun/BrowserStack/Minitap Cloud 云手机 |
| 🎬 视频分析 | 可选视频录制+多模态模型分析执行过程 |

## 文档目录

| 文档 | 内容 |
|---|---|
| [快速开始](quickstart.md) | 环境准备、安装、5分钟跑通第一个任务 |
| [架构解析](architecture.md) | 9-Agent 协作系统、LangGraph 状态机、执行循环详解 |
| [SDK 使用指南](sdk-guide.md) | Agent 类、Builder 模式、多 Profile、结构化输出 |
| [工具系统](tools.md) | 16个移动操作工具、Scratchpad 记忆、工具扩展 |
| [设备适配](devices.md) | Android/iOS/云设备控制器架构、客户端层详解 |
| [配置体系](configuration.md) | LLM 配置、环境变量、Fallback 降级机制 |
| [扩展开发](extending.md) | 新增 Agent/工具/控制器/LLM Provider |
| [最佳实践](best-practices.md) | 任务设计、Prompt 技巧、调试方法、常见陷阱 |
| [故障排查](troubleshooting.md) | 设备连接、Agent执行、LLM调用、Docker部署问题解决 |

## 快速理解路径

```mermaid
flowchart LR
    A["快速开始"] --> B["SDK 使用指南"]
    B --> C["架构解析"]
    C --> D["工具系统"]
    D --> E["设备适配"]
    E --> F["配置体系"]
    F --> G["扩展开发"]
    G --> H["最佳实践"]
    H --> I["故障排查"]
```

**如果你只想快速用起来**：直接读 [快速开始](quickstart.md) → [SDK 使用指南](sdk-guide.md)。

**如果你想理解为什么这么设计**：按顺序阅读 [架构解析](architecture.md) → [工具系统](tools.md) → [设备适配](devices.md)。

**如果你想二次开发**：读完前面的文档后看 [扩展开发](extending.md) 和 [最佳实践](best-practices.md)。

## 技术栈速览

| 层级 | 技术选型 |
|---|---|
| Agent 框架 | LangGraph ≥1.0.2（状态图+流式执行） |
| LLM 抽象 | LangChain ≥1.0.0（统一多Provider接口） |
| Android 控制 | adbutils + uiautomator2 |
| iOS 模拟器 | fb-idb |
| iOS 真机 | WebDriverAgent (facebook-wda) |
| 云设备 | Limrun API、BrowserStack、Minitap Cloud |
| CLI | Typer |
| 配置 | Pydantic Settings + python-dotenv + JSONC |
| 遥测 | PostHog（可关闭） |
| 视频录制 | 设备原生录屏 + PIL 图像处理 |
| Python 版本 | ≥3.12 |

## 源码位置速查

| 模块 | 路径 |
|---|---|
| SDK 入口 | `minitap/mobile_use/sdk/agent.py` |
| LangGraph 图定义 | `minitap/mobile_use/graph/graph.py` |
| 全局状态 | `minitap/mobile_use/graph/state.py` |
| 9个Agent实现 | `minitap/mobile_use/agents/*/` |
| 设备控制器 | `minitap/mobile_use/controllers/` |
| 底层客户端 | `minitap/mobile_use/clients/` |
| 移动操作工具 | `minitap/mobile_use/tools/mobile/` |
| LLM服务 | `minitap/mobile_use/services/llm.py` |
| CLI入口 | `minitap/mobile_use/main.py` |
| SDK示例 | `minitap/mobile_use/sdk/examples/` |

> **源码位置参考**: [agent.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/sdk/agent.py), [graph.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/graph/graph.py), [state.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/graph/state.py)
