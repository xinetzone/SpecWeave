# 概念文档

## 入门组（00-05）

* [00 — veadk-python 概览](00-overview.md) — 定位、架构分层、版本依赖、默认常量与生态组成
* [01 — Agent 核心类与生命周期](01-agent-lifecycle.md) — Pydantic 字段体系、model_post_init 装配、模型实例化、工具挂载与流程选择
* [02 — AgentBuilder 与 YAML 配置驱动](02-agent-builder.md) — OmegaConf 加载、AGENT_TYPES 映射、递归子代理构建与工具动态导入
* [03 — Agent 类型体系](03-agent-types.md) — LoopAgent、ParallelAgent、SequentialAgent 与 SuperviseAgent 监督模式
* [04 — 配置系统](04-configuration.md) — VeADKConfig、ModelConfig、config.yaml 结构、环境变量前缀映射
* [05 — Runner 运行器](05-runner.md) — run 方法、消息拦截装饰器、多模态转换、Tracing 与会话管理

## 进阶组（06-11）

* [06 — 记忆系统](06-memory-system.md) — 短期/长期记忆、8 种后端、会话压缩与 Profile 生成
* [07 — LLM 模型抽象](07-llm-models.md) — ArkLlm 与 LiteLlm 双轨、fallback 机制、ArkEmbedding 与 API Key 优先级
* [08 — 知识库](08-knowledgebase.md) — KnowledgeBase 统一接口、8 种后端、CRUD 方法与 Profile 自动生成
* [09 — 评估系统](09-evaluation.md) — BaseEvaluator、EvalTestCase、MetricResult 与 ADK/DeepEval 双评估器
* [10 — CLI 工具集](10-cli-tools.md) — 16 个子命令全景，覆盖创建、部署、评估、Web 服务等生命周期
* [11 — 高级特性](11-advanced.md) — A2A 协议、多模态、认证、Prompt 管理、Harness 扩展与运行时抽象
