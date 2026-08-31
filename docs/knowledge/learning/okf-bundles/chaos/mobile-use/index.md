# mobile-use 知识包

本知识包（bundle）系统梳理 minitap-mobile-use（版本 3.6.3）的架构与实现。mobile-use 是一个基于 LangGraph 的 AI 多智能体系统，通过底层控制实现真实 Android 和 iOS 设备的自然语言自动化。内容涵盖多 Agent 协作架构、设备控制抽象层、工具系统、LLM 可插拔配置、SDK 双层 API 和图状态管理，遵循 OKF v0.2 规范。

## 目录分组

* [concepts/](concepts/index.md) - 核心概念：7 篇概念文档，按编号排列，覆盖从项目概览到多 Agent 架构到 SDK 接口的完整知识体系
  * [mobile-use 项目概览](concepts/00-overview.md)
  * [多 Agent 协作架构](concepts/01-multi-agent-architecture.md)
  * [设备控制抽象层](concepts/02-device-control.md)
  * [工具系统与执行节点](concepts/03-tools-system.md)
  * [LLM 配置与可插拔体系](concepts/04-llm-configuration.md)
  * [SDK 双层 API 与生命周期](concepts/05-sdk-layer.md)
  * [图结构与状态管理](concepts/06-graph-state.md)
* [examples/](examples/index.md) - 使用示例：CLI 命令实际用法
  * [CLI 命令使用示例](examples/cli-usage.md)
* [references/](references/index.md) - 信源登记簿：3 篇信源文件，含 R 阶段事实清单、I 阶段洞察、源码登记
  * [事实清单](references/facts.md)
  * [架构洞察](references/insights.md)
  * [mobile-use 源码](references/mobile-use-source.md)
* [验证报告](verification-report.md) - V 阶段验证报告，结构检查、API 验证与修复记录

```{toctree}
:maxdepth: 2

concepts/index
examples/index
references/index
log
verification-report
```