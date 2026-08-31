# 概念文档

- [00 - mobile-use 项目概览](00-overview.md) — 项目定位、功能特性、CLI 用法、核心依赖与模块架构总览
- [01 - 多 Agent 协作架构](01-multi-agent-architecture.md) — 9 个 Agent 节点职责、LangGraph 图节点与边、条件门路由、子目标状态机
- [02 - 设备控制抽象层](02-device-control.md) — MobileDeviceController Protocol、Android/iOS 实现、Factory 工厂、UnifiedMobileController 门面
- [03 - 工具系统与执行节点](03-tools-system.md) — ToolWrapper 注册机制、15 个 mobile 工具、scratchpad 草稿、ExecutorToolNode 顺序执行
- [04 - LLM 配置与可插拔体系](04-llm-configuration.md) — LLMConfig 层级模型、9 个提供商、fallback 机制、JSONC 配置加载、环境变量凭据
- [05 - SDK 双层 API 与生命周期](05-sdk-layer.md) — Agent 类核心入口、AgentConfigBuilder 流式配置、TaskRequestBuilder、本地与云手机双路径
- [06 - 图结构与状态管理](06-graph-state.md) — StateGraph 编译、State 字段与 reducer、条件门路由、消息通道隔离、遥测集成

```{toctree}
:maxdepth: 2

00-overview
01-multi-agent-architecture
02-device-control
03-tools-system
04-llm-configuration
05-sdk-layer
06-graph-state
```