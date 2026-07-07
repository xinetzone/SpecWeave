---
title: "综合术语表"
category: "learning"
source: "https://www.minitap.ai/docs"
date: "2026-07-07"
tags: ["glossary", "minitest", "mobile-use", "术语表", "terminology"]
summary: "整合minitest和mobile-use SDK的术语定义，确保术语翻译统一，方便查阅。"
---

# 综合术语表

> **来源**: https://www.minitap.ai/docs

本术语表整合了minitest产品和mobile-use SDK中使用的所有术语，提供统一的中文翻译和定义。当文档和仪表板术语不一致时，以本文档为准。

---

## A

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **Acceptance criterion** (复数criteria) | 验收标准 | 用户故事中的单个可观察条件。不是"assertion（断言）"、"check（检查）"或"step（步骤）"。 | minitest |
| **ADB (Android Debug Bridge)** | Android调试桥 | Android平台的命令行工具，用于与设备通信、安装应用、调试等。 | mobile-use SDK |
| **Agent** | 代理 | 驱动设备的AI。在技术上下文中是Mini的同义词。在mobile-use SDK中，Agent是移动自动化的中央协调器类。 | 两者 |
| **AgentNotInitializedError** | Agent未初始化错误 | mobile-use SDK中的异常，在未调用`agent.init()`就运行任务时抛出。 | mobile-use SDK |
| **App** | 应用 | 工作区内配置的移动应用。 | minitest |
| **Architecture** | 架构 | 系统的组件组织方式，mobile-use采用分层架构（Agent层、任务层、设备交互层等）。 | 两者 |
| **Async/Await** | 异步/等待 | Python异步编程模式，mobile-use SDK使用异步API。 | mobile-use SDK |

---

## B

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **Build** | 构建 | 运行所针对的`.ipa`（iOS）或`.apk`（Android）产物。 | minitest |
| **Builders** | 构建器模式 | mobile-use SDK中用于配置Agent和任务的流式API（Builder Pattern），提供链式调用方式配置复杂对象。 | mobile-use SDK |
| **Bug** | 缺陷/ Bug | 软件中的错误或问题。注意：在minitest中，使用"Issue（问题）"而非"bug"来指代需要分类的失败标准。 | 两者 |

---

## C

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **Capability** | 能力范围 | 产品能做什么和不能做什么的边界说明。参考[能力范围文档](minitest-docs/05-reference/01-capabilities.md)。 | minitest |
| **CI/CD (Continuous Integration/Continuous Deployment)** | 持续集成/持续部署 | 自动化软件构建、测试和部署的实践。minitest可以集成到CI/CD流程中，在PR上显示检查标记。 | 两者 |
| **CLI (Command Line Interface)** | 命令行界面 | `minitest`命令行工具，可用于与minitest交互、触发运行、配置Mini's Memory等。 | minitest |
| **Contextor** | 上下文收集器 | mobile-use多Agent架构中的组件，负责收集设备上下文、执行应用锁约束。需要快速文本模型。 | mobile-use SDK |
| **Cortex** | 核心推理器 | mobile-use多Agent架构中的核心组件，负责高级推理和决策（系统的"眼睛"），分析截图和UI层次结构。**需要视觉能力**的LLM。 | mobile-use SDK |
| **Criticality** | 严重性 | 问题上的重要性标签：Critical、Warning或Pass。Mini在运行时推断它，用户可以按问题覆盖。 | minitest |

---

## D

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **Dashboard** | 仪表板 | 位于[app.minitap.ai](https://app.minitap.ai/)的Web应用，是minitest的主要用户界面。 | minitest |
| **Device Controller** | 设备控制器 | mobile-use中处理设备控制的组件：Android使用ADB+UIAutomator2，iOS使用IDB。负责执行点击、滑动、输入等物理操作。 | mobile-use SDK |
| **DeviceNotFoundError** | 设备未找到错误 | mobile-use SDK中的异常，在未检测到连接的设备时抛出。 | mobile-use SDK |

---

## E

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **E2E Testing (End-to-End Testing)** | 端到端测试 | 测试完整用户流程从开始到结束的测试方法。传统E2E测试使用脚本（Appium、Maestro、Playwright），minitest使用AI代理。 | 两者 |
| **Executor** | 执行器 | mobile-use多Agent架构中的组件，负责将决策转换为具体的设备操作（点击、滑动、输入等）。需要良好的指令遵循模型。 | mobile-use SDK |

---

## F

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **Failure** | 失败 | 测试未通过的状态。注意：在minitest中，使用"Issue（问题）"来指代需要分类的失败标准。 | 两者 |
| **Fallback** | 回退/备选 | LLM配置中的备用模型，当主模型不可用时自动切换使用。推荐为Cortex等核心组件配置fallback。 | mobile-use SDK |
| **Fix prompt** | 修复提示 | Mini为每个失败标准生成的可粘贴到剪贴板的文本块，包含根本原因、复现步骤和建议修复。可直接用于Cursor或Claude。 | minitest |
| **Flake** | 不稳定测试/Flaky测试 | 非确定性的测试，在相同条件下有时通过有时失败。传统脚本测试flake率高（Google数据显示消耗2-16%计算资源），minitest架构目标是零flake。 | 两者 |

---

## G-H

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **GitHub Action** | GitHub动作 | minitest提供的GitHub Action，可在CI中自动运行测试。 | minitest |
| **GitHub Integration** | GitHub集成 | minitest与GitHub的集成，支持PR检查、自动构建等功能。 | minitest |
| **Hopper** | 信息提取器 | mobile-use多Agent架构中的工具组件，负责从大量数据中提取相关信息。需要大上下文窗口的模型（256k+）。 | mobile-use SDK |
| **IDB (iOS Development Bridge)** | iOS开发桥 | iOS平台的命令行工具，用于与iOS模拟器和设备通信。Android对应工具是ADB。 | mobile-use SDK |
| **Issue** | 问题 | 需要分类的失败标准。存在于Issues标签页。不是"failure（失败）"或"bug（缺陷）"。 | minitest |

---

## I-J

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **Integration** | 集成 | minitest与外部工具的连接，包括GitHub、Slack、Cursor、Claude等。 | minitest |
| **iOS** | iOS | Apple的移动操作系统，minitest和mobile-use全面支持iOS。 | 两者 |
| **LangGraph** | LangGraph | LangChain推出的构建有状态Agent的框架，mobile-use SDK利用LangGraph实现Agent推理、分步执行和动态适应。 | mobile-use SDK |
| **LLM (Large Language Model)** | 大语言模型 | 如GPT-5、Gemini、Claude等，mobile-use使用多个LLM组件协作完成任务。 | 两者 |

---

## K-L

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **Local Mode** | 本地模式 | mobile-use SDK的运行模式之一，完全控制LLM配置，本地连接设备。适用于开发调试和自定义环境。与Platform模式相对。 | mobile-use SDK |
| **Log** | 日志 | 运行时产生的记录信息，用于调试。minitest在失败报告中包含设备日志。 | 两者 |

---

## M

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **max_steps** | 最大步数 | mobile-use中任务执行的最大步骤数限制，默认400。复杂任务可适当增加，但过大可能导致循环。 | mobile-use SDK |
| **MCP (Model Context Protocol)** | 模型上下文协议 | 一种协议，允许AI模型与外部工具和数据源交互。minitest提供MCP服务器，支持Cursor、Claude Code等MCP客户端。 | minitest |
| **MCP server** | MCP服务器 | Cursor、Claude Code和其他MCP客户端连接到的Model Context Protocol界面。 | minitest |
| **MCP tools** | MCP工具 | MCP服务器暴露的各个调用接口，允许AI编辑器与minitest交互。参考[MCP工具文档](minitest-docs/05-reference/04-mcp-tools.md)。 | minitest |
| **Memory (Mini's memory)** | Mini的记忆 | Mini在每次运行前读取的关于应用的额外上下文。通过MCP服务器或CLI设置。 | minitest |
| **Mini** | Mini（迷你） | 驱动设备、编写用户故事和分类问题的AI代理。产品名是**minitest**（小写m，大写T），AI代理名叫**Mini**。 | minitest |
| **minitest** | minitest | 产品名称。注意拼写：小写m，大写T。CLI二进制文件是`minitest`（全小写）。是完全自主的AI QA工程师产品。 | minitest |
| **mobile-use** | mobile-use | Minitap开源的移动自动化SDK，是minitest产品的技术基座。GitHub: [github.com/minitap-ai/mobile-use](https://github.com/minitap-ai/mobile-use) | mobile-use SDK |
| **Multi-agent Architecture** | 多Agent架构 | mobile-use SDK采用的架构，包含Planner、Orchestrator、Contextor、Cortex、Executor等多个专门化Agent组件协作完成任务。 | mobile-use SDK |

---

## N-O

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **Normalized Coordinates** | 规范化坐标 | mobile-use中的坐标抽象技术，统一跨平台坐标表示，使Agent可以在不同分辨率和平台上一致地操作。 | mobile-use SDK |
| **Observability** | 可观测性 | 系统运行状态的可见程度。mobile-use内置执行追踪、GIF录制和平台可视化功能。 | mobile-use SDK |
| **Orchestrator** | 编排器 | mobile-use多Agent架构中的组件，负责协调执行流程、管理状态转换。需要快速决策模型。 | mobile-use SDK |
| **Outputter** | 输出提取器 | mobile-use多Agent架构中的工具组件，负责提取结构化输出。需要良好的结构化输出能力。 | mobile-use SDK |

---

## P-Q

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **Passed** | 通过 | Verdict（判定结果）之一，表示运行或故事成功通过。 | minitest |
| **Persona** | 用户角色 | 测试中模拟的不同用户类型（普通用户、管理员、付费用户等）。通过Profile配置。 | minitest |
| **Platform Mode** | 平台模式 | mobile-use SDK的运行模式之一，使用Minitap云端平台管理任务和LLM配置。适用于团队协作和快速上手。与Local模式相对。 | mobile-use SDK |
| **Planner** | 规划器 | mobile-use多Agent架构中的组件，负责将自然语言目标分解为高级子目标。需要快速推理模型。 | mobile-use SDK |
| **PR check** | PR检查 | MiniTest GitHub App在Pull Request上发布的GitHub状态检查，显示测试通过或失败。 | minitest |
| **Profile (Agent Profile)** | Agent配置文件 | mobile-use中自定义Agent行为和LLM配置的命名配置。 | mobile-use SDK |
| **Profile (Test Profile)** | 配置文件（测试） | 附加到用户故事的命名凭据集（用户名、密码、备注）。Mini在运行期间使用它登录。 | minitest |
| **Pydantic** | Pydantic | Python的数据验证库，mobile-use使用Pydantic模型定义结构化输出类型，提供类型安全的结果。 | mobile-use SDK |
| **Python 3.12+** | Python 3.12+ | mobile-use SDK要求的最低Python版本。 | mobile-use SDK |

---

## R

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **React Native** | React Native | 跨平台移动应用框架，minitest支持。 | 两者 |
| **Regression Testing** | 回归测试 | 修改代码后重新运行测试以确保没有引入新bug。minitest支持30-60分钟完整无人值守回归。 | 两者 |
| **Run** | 运行 | 一次执行事件。点击**Run tests**，N个故事一起运行。不是"batch（批次）"。 | minitest |
| **Re-run** | 重新运行 | 再次执行测试运行。 | minitest |
| **Report** | 报告 | 测试运行结果的详细展示，包括视频、日志、复现步骤、修复提示等。 | minitest |
| **Repro steps (Reproduction steps)** | 复现步骤 | 重现问题的清晰步骤说明，minitest在失败报告中自动提供。 | minitest |

---

## S

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **SDK (Software Development Kit)** | 软件开发工具包 | mobile-use SDK，允许开发者编程控制移动设备的工具包。 | mobile-use SDK |
| **ServerStartupError** | 服务器启动错误 | mobile-use SDK中的异常，在设备控制服务器启动失败时抛出（通常因端口占用或僵尸进程）。 | mobile-use SDK |
| **Session ID** | 会话ID | 错误输出中显示的UUID，用于帮助调试问题。报告Bug时必须包含。 | 两者 |
| **Session Replay** | 会话回放 | 测试运行的完整视频记录，带时间戳，可回放查看发生了什么。 | minitest |
| **Slack Integration** | Slack集成 | minitest与Slack的集成，支持实时通知、从Slack触发运行、在Slack中分类问题。 | minitest |
| **Status** | 状态 | 问题的生命周期状态（open、acknowledged、resolved）。与Verdict（判定结果）不同。 | minitest |
| **Structured Output** | 结构化输出 | mobile-use通过Pydantic模型返回的类型安全结果，而非非结构化文本。 | mobile-use SDK |
| **Suggestion** | 建议 | Mini在运行故事时标记的UX观察——验收标准之外看起来不对的东西。不是"finding（发现）"或"recommendation（推荐）"。包括视觉回归、文案更改、损坏的导航等。 | minitest |
| **Suite** | 套件 | 一个应用的所有用户故事的集合。 | minitest |
| **Swift** | Swift | Apple的原生iOS开发语言，minitest支持。 | 两者 |

---

## T

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **Task** | 任务 | mobile-use中基于目标的自动化工作流，由自然语言目标、可选的结构化输出、追踪配置等定义。 | mobile-use SDK |
| **TaskTimeoutError** | 任务超时错误 | mobile-use SDK中的异常，任务执行超过max_steps或时间限制时抛出。 | mobile-use SDK |
| **Test Configuration** | 测试配置 | 仪表板中每个应用的设置屏幕（配置文件、环境变量、Mini的记忆）。指代屏幕时作为专有名词大写；在散文中使用小写。 | minitest |
| **Trace** | 追踪 | mobile-use的执行记录功能，记录每一步的截图、Agent思考过程、LLM输入输出等，用于调试。 | mobile-use SDK |
| **Triage** | 分类 | 对测试发现的问题进行确认、标记、处理的过程。minitest支持从Slack或仪表板分类问题。 | minitest |

---

## U-V

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **UIAutomator2** | UIAutomator2 | Android的UI自动化框架，mobile-use在Android上使用ADB+UIAutomator2实现可靠的UI自动化。 | mobile-use SDK |
| **Unprocessable** | 无法处理 | Verdict（判定结果）之一，表示Mini无法处理该故事或运行。 | minitest |
| **User story** | 用户故事 | 用通俗易懂的语言描述的应用中的一段旅程，带有验收标准。不是"test（测试）"、"flow（流程）"或"scenario（场景）"。是minitest中的核心测试单元。 | minitest |
| **uv** | uv | 快速的Python包管理器，推荐用于安装mobile-use SDK。 | mobile-use SDK |
| **venv** | venv | Python内置的虚拟环境模块。 | mobile-use SDK |
| **Verdict** | 判定结果 | 运行或运行中故事的结果：Passed、Warning、Failed或Unprocessable。不是"result（结果）"或"status（状态）"。 | minitest |
| **Video Analyzer** | 视频分析器 | mobile-use多Agent架构中的可选工具组件，负责分析视频内容。需要Gemini视频模型等支持视频理解的模型。 | mobile-use SDK |

---

## W-X

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **Warning** | 警告 | Verdict（判定结果）之一，表示存在问题但不严重；也用于Criticality（严重性）标签中的中级严重性。 | minitest |
| **Workspace** | 工作区 | 容纳应用、成员、集成和计费的顶级容器。 | minitest |

---

## Y-Z

| 术语 | 中文翻译 | 定义 | 适用模块 |
|---|---|---|---|
| **Zero Script** | 零脚本 | minitest的核心理念：无需人工编写或维护测试脚本，AI代理自动生成和维护测试套件。 | minitest |
| **Zero Maintenance** | 零维护 | minitest的核心理念：测试套件自动适应UI变化，无需人工维护。 | minitest |

---

## 术语使用规范

### 拼写注意事项

| 正确 | 错误 | 说明 |
|---|---|---|
| **minitest** | Minitest、MiniTest、MINITEST | 产品名：小写m，大写T |
| **Mini** | mini、MINI | AI代理名：首字母大写 |
| **mobile-use** | mobile_use、MobileUse、mobileUse | SDK名：全小写，连字符分隔 |
| **Minitap** | minitap、MiniTap | 公司名：首字母大写M和T |

### 术语选择规范

| 场景 | 使用 | 不使用 |
|---|---|---|
| 测试单元 | 用户故事（User story） | 测试（test）、流程（flow）、场景（scenario） |
| 验证条件 | 验收标准（Acceptance criterion） | 断言（assertion）、检查（check）、步骤（step） |
| 一次执行 | 运行（Run） | 批次（batch） |
| 测试结果 | 判定结果（Verdict） | 结果（result）、状态（status） |
| 发现的问题 | 问题（Issue） | 失败（failure）、缺陷（bug） |
| UX观察 | 建议（Suggestion） | 发现（finding）、推荐（recommendation） |
| 问题严重性 | 严重性（Criticality） | 优先级（priority） |
| 问题生命周期 | 状态（Status） | 判定结果（verdict） |

---

> **返回总览**：[教程首页](../minitest-mobile-use-official-docs-wiki.md)
