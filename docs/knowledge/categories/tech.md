---
type: Reference
title: "分类索引：tech"
---

# 分类索引：tech

- [返回分类总索引](../category-index.md)
- [返回知识库首页](../README.md)
- [按标签检索](../tags/README.md)

> 本分片收录 **1** 个子分类，共 **36** 条条目。

### tech

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [caffe-ffi Conv v4 OpenMP 并行优化技术总结](../tech/caffe-ffi-conv-v4-optimization-summary.md) | caffe-ffi Conv 层 OpenMP 并行优化（v4）的技术总结，覆盖并行策略、环境变量配置、抖动诊断与生产部署指南，供团队内部分享。 |  | - |
| [GLM 大模型调用可复用示例（本地加载 + API 调用）](../tech/glm-model-call-example.md) | 从 chaos/flexloop/models 沉淀的 GLM 大模型调用可复用示例：本地模型加载（transformers + torch）与 Z.AI 云端 API 调用（zai-sdk）两种方式，含脱敏代码与环境变量配置说明。 | 2026-08-07 | glm、llm、transformers、zai、huggingface、python |
| [ListenHub API 规范——Authentication（认证与基础 URL）](../tech/listenhub-api-authentication.md) | 沉淀 ListenHub 开放平台的统一认证规范：环境变量 LISTENHUB_API_KEY、基础 URL、必备请求头（Authorization/Content-Type/X-Source）、curl 模板与安全注意事项。所有 Key 均以占位符表示。 | 2026-08-07 | listenhub、api、authentication、security、marswave |
| [ListenHub API 规范——Image Generation（AI 图片生成）](../tech/listenhub-api-image.md) | 沉淀 ListenHub AI 图片生成接口规范：POST /images/generation，记录请求参数（provider/prompt/model/imageConfig/referenceImages）、宽高比表、参考图 URL/base64 两种格式、同步 base64 返回与调用要点。 | 2026-08-07 | listenhub、api、image-gen、image-generation、gemini、marswave |
| [ListenHub API 规范——Podcast（播客节目生成）](../tech/listenhub-api-podcast.md) | 沉淀 ListenHub 播客生成接口规范：POST /podcast/episodes 创建节目、GET /podcast/episodes/{episodeId} 查询状态结果，记录接口用途、关键参数（speakers/query/sources/language/mode）与调用要点（异步轮询、两段式生成）。 | 2026-08-07 | listenhub、api、podcast、marswave |
| [ListenHub API 规范——Speakers（主播列表）](../tech/listenhub-api-speakers.md) | 沉淀 ListenHub 主播列表接口规范：GET /speakers/list，记录查询参数（language/status）、响应字段（name/speakerId/demoAudioUrl/gender/language）与调用要点；含内置默认主播表。 | 2026-08-07 | listenhub、api、speakers、marswave |
| [ListenHub API 规范——Storybook（解说视频/故事本）](../tech/listenhub-api-storybook.md) | 沉淀 ListenHub 解说视频（Storybook）接口规范：POST /v1/storybook/episodes 创建、GET 查询状态结果、POST /v1/storybook/episodes/{episodeId}/video 触发视频生成，记录参数（sources/speakers/language/mode）、mode 取值与调用要点。 | 2026-08-07 | listenhub、api、storybook、explainer、video、marswave |
| [ListenHub API 规范——TTS / Speech（文本转语音）](../tech/listenhub-api-tts.md) | 沉淀 ListenHub 文本转语音（TTS）两套接口规范：/v1/tts（单声、低延迟、同步 MP3 流）与 /v1/speech（多角色脚本转音频），记录接口用途、关键参数与调用要点。 | 2026-08-07 | listenhub、api、tts、speech、marswave |
| [ListenHub 技能集总览——asr/tts/podcast/image-gen/content-parser/explainer 设计模式与共享规范](../tech/listenhub-skill-set-overview.md) | 沉淀 flexloop chaos 技能库中 6 个内容生成类 AI 技能（asr/tts/podcast/image-gen/content-parser/explainer）的触发词、能力定位、API 依赖与共享通用模式（异步轮询/错误处理/@file/交互式参数收集），并说明已废弃的 listenhub 单体技能状态。 | 2026-08-07 | listenhub、skill、ai-skill、api-integration、design-pattern、marswave |
| [DaoMind 项目概览（道家哲学 TypeScript 框架）](../tech/p1-09-daomind-project-overview.md) | DaoMind 是基于道家哲学宇宙论的现代化 TypeScript 框架，采用 pnpm monorepo 架构，核心包覆盖无/有/行动/应用/时序/道宇宙六层抽象，含函数式错误处理与 DaoUniverse 桥接体系。 |  | - |
| [道衍 DaoYan 项目概览（帛书道德经 AI 对话系统）](../tech/p1-10-daoyan-project-overview.md) | 道衍是以马王堆帛书版《道德经》为权威底本的 AI 智慧对话系统，融合道家无为、佛家直心与 ψ=ψ(ψ) 万物理论，支持 5 大 AI 模型切换与 Agent API/MCP 开放接入。 |  | - |
| [DaoMind 2.0 哲学架构：无名/有名与 TypeScript 类型系统映射](../tech/p1-13-daomind-philosophy-architecture.md) | DaoMind 2.0 将帛书《道德经》"无名/有名"哲学概念与 TypeScript 类型/值空间进行映射，建立了独特的哲学驱动架构设计模式 |  | - |
| [MCP 技能开发与 REST API 集成规范——以道衍为例](../tech/p1-17-daoyan-mcp-skill-spec.md) | 以道衍（DaoYan）MCP Server 为例，说明 AI IDE 技能（Skill）定义、MCP 工具配置、REST API 调用与回答规范的完整模式 |  | - |
| [Reasonix 架构：Python AI Agent 分层设计模式](../tech/p1-18-reasonix-architecture.md) | DeepSeek-Reasonix 是一个配置驱动、多模型协作的 AI Coding Agent，采用清晰的分层架构（组装器+Provider+Agent+Controller），是 Python AI Agent 项目的优秀架构参考 |  | - |
| [TVM Relax 前端 MLP 实验记录](../tech/p2-13-tvm-relax-mlp-experiment.md) | TVM Relax 前端 nn.Module API 的最小 MLP 实验，展示从模型定义到 export 导出链路的验证样例，可作为 Relax 前端学习与回归参考。 |  | - |
| [Python 3.14 Free-Threading 适用场景分析](../tech/python-314-free-threading-scenario-analysis.md) |  | 2026-08-19 | python、free-threading、no-gil、concurrency、performance |
| [Python 与 Rust 技术对比分析报告 Wiki · 总览](../tech/python-rust-comparison/00-overview.md) | 基于最新标准（Python 3.14 / Rust 1.97.1）从零创作的 Python 与 Rust 技术对比分析 Wiki，覆盖语言机制、性能、工程化、生态、应用场景、决策矩阵与迁移路径。 | 2026-08-07 | python、rust、技术选型、性能、混合架构 |
| [Python 与 Rust 技术对比 · 语言与运行时基础](../tech/python-rust-comparison/01-language-runtime.md) | 从最新标准对比 Python 与 Rust 在语法、类型、内存、并发与运行时上的机制差异。 | 2026-08-07 | python、rust、类型系统、内存、并发、异步 |
| [Python 与 Rust 技术对比 · 性能与工程化](../tech/python-rust-comparison/02-performance-engineering.md) | 对比 Python 与 Rust 在运行时性能、资源占用与工程化工具链上的差异。 | 2026-08-07 | python、rust、性能、工具链、工程化 |
| [Python 与 Rust 技术对比 · 生态、应用场景与代码示例](../tech/python-rust-comparison/03-ecosystem-scenarios.md) | 对比 Python 与 Rust 的生态成熟度、典型应用场景，并提供对照代码示例。 | 2026-08-07 | python、rust、生态、应用场景、代码示例 |
| [Python 与 Rust 技术对比 · 决策矩阵与迁移路径](../tech/python-rust-comparison/04-decision-migration.md) | 提供 Python 与 Rust 选型决策矩阵、场景化建议、迁移路径与结论。 | 2026-08-07 | python、rust、决策矩阵、选型建议、迁移、混合架构 |
| [Python 迁移到 Rust 简易检查清单](../tech/python-rust-comparison/05-migration-checklist.md) | 基于《Python 与 Rust 技术对比》报告萃取的迁移到 Rust 的简易检查清单，覆盖决策、热点识别、PoC、逐模块迁移、测试、培训与灰度回退。 | 2026-08-07 | python、rust、迁移、检查清单、混合架构 |
| [TVM FFI 教程总览](../tech/tvm-ffi-wiki/00-overview.md) | Apache TVM FFI 中文wiki教程总览 | 2026-07-28 | tvm-ffi、ffi、c++、python、ml-system |
| [项目结构说明](../tech/tvm-ffi-wiki/01-project-structure.md) |  | 2026-07-28 | tvm-ffi、project-structure |
| [Any/AnyView 类型系统](../tech/tvm-ffi-wiki/02-any-type.md) |  | 2026-07-28 | tvm-ffi、type-system、any、type-erasure |
| [Object 对象系统](../tech/tvm-ffi-wiki/03-object-system.md) |  | 2026-07-28 | tvm-ffi、object、reference-counting、inheritance |
| [Function 函数与全局注册表](../tech/tvm-ffi-wiki/04-function-registry.md) |  | 2026-07-28 | tvm-ffi、function、packed-func、registry |
| [Container 容器类型](../tech/tvm-ffi-wiki/05-containers.md) |  | 2026-07-28 | tvm-ffi、container、array、map、tensor |
| [Reflection 反射系统](../tech/tvm-ffi-wiki/06-reflection.md) |  | 2026-07-28 | tvm-ffi、reflection、dataclass、stubgen |
| [Module 模块系统](../tech/tvm-ffi-wiki/07-module-system.md) |  | 2026-07-28 | tvm-ffi、module、dynamic-loading、dll |
| [C++ 开发指南](../tech/tvm-ffi-wiki/08-cpp-guide.md) |  | 2026-07-28 | tvm-ffi、cpp、guide、cmake、build |
| [Python 开发指南](../tech/tvm-ffi-wiki/09-python-guide.md) |  | 2026-07-28 | tvm-ffi、python、guide、cython |
| [构建与打包](../tech/tvm-ffi-wiki/10-build-packaging.md) |  | 2026-07-28 | tvm-ffi、build、cmake、packaging、wheel |
| [实战案例](../tech/tvm-ffi-wiki/11-examples.md) |  | 2026-07-28 | tvm-ffi、examples、tutorial、kernel |
| [常见问题解答 (FAQ)](../tech/tvm-ffi-wiki/12-faq.md) |  | 2026-07-28 | tvm-ffi、faq、troubleshooting |
| [核心源码解析（进阶）](../tech/tvm-ffi-wiki/13-source-analysis.md) |  | 2026-07-28 | tvm-ffi、source-code、internals、advanced |

---

*索引自动生成于 2026-08-21 15:32:36*
