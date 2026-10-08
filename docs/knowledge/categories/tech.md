---
type: Reference
title: "分类索引：tech"
---

# 分类索引：tech

- [返回分类总索引](../category-index.md)
- [返回知识库首页](../README.md)
- [按标签检索](../tags/README.md)

> 本分片收录 **1** 个子分类，共 **48** 条条目。

## tech

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
| [onnx-pytorch v1.1.0 发布说明](../tech/release-onnx-pytorch-v1-1.md) |  | 2026-08-15 | - |
| [onnx-quantized v2.0.0 发布说明](../tech/release-onnx-quantized-v2.md) |  | 2026-08-14 | - |
| [Fedora CoreOS 系统性知识分析：不可变容器 OS 的机制、模式与边界](../tech/fedora-coreos/index.md) | 以七概念方法论（R→I→E→V，deep）对 Fedora CoreOS 做系统理解：77 条一手事实、4 条四元组洞察、2 个可迁移模式（镜像基座契约 / 图控灰度更新）、4 视角对抗审查与采纳修正、与本仓 Podman/WSL 栈的关系界定。 | 2026-09-15 | - |
| [openEuler 与 openKylin 系统性对比：后端根社区与桌面根社区的分工、治理、生命周期与选型](../tech/openeuler-vs-openkylin/index.md) | 以七概念方法论（R→I→E→V→C，standard）系统对比 openEuler 与 openKylin：新采集 openEuler 侧 35 条带来源客观事实（O-001~O-035，2010 EulerOS 起源至 2026-09 装机 2000 万口径与 24.03 LTS SP4），以 12 条锚点（K-001~K-012）引用本地 openKylin 知识包 62 条事实，形成 5 条四元组洞察与 1 个 L1-draft 可迁移模式（场景区间选型法）。核心结论：两者不是直接竞品，而是同一开放原子基金会体系内后端基础设施根社区与桌面/AI 终端根社区的产业分工，麒麟软件同时为两边参与者且其服务器/桌面商业版分别以两者为上游。知识包按问题域拆为画像、定位场景、治理生态、版本生命周期、技术栈、选型指南 6 个概念页，附信源台账与对抗审查记录。 | 2026-09-30 | - |
| [openKylin 官方文档平台学习教程（OKF Wiki）：237 篇社区文档的逆向导读](../tech/openkylin-docs-wiki/index.md) | 以七概念方法论（R→I→E→V→C，standard）系统学习 openKylin 官方文档平台 docs.openkylin.top：递归解析 Gitee 源仓库 3181 条目/237 篇中文文档、精读 35 篇代表性文档、提取 44 条客观事实，形成 4 条四元组洞察与 1 个 L1 可迁移模式（逆序文档学习法）。教程按学习者问题域重组为平台地图、版本生命周期、安装路径、桌面使用、AI 三层体系、开发者基础设施、社区治理 7 个概念页，附信源台账与完整文档分类地图。 | 2026-09-29 | - |
| [openKylin 3.0 架构适配评估草案：纸面预评估、风险登记与 POC 验证方案](../tech/openkylin-docs-wiki/references/openkylin-v3-adaptation-assessment.md) | 基于同知识包两份已验证报告（62 条项目事实、44 条文档平台事实与 3.0 WSL 本机实测），对 openKylin 3.0（Huanghe）做适配前纸面预评估：覆盖工具链跨代、不可变系统、多架构、图形栈、后量子安全、智能体底座、工程供应链 7 个维度，登记 12 项风险，给出软件/硬件/AI 智能体三类适配主体的工作路径、版本策略矩阵与 P0–P5 六阶段 POC 方案。本文为草案 v0.1，所有结论未经实机 POC 验证。 | 2026-09-29 | - |
| [openKylin 全面调研：从桌面根社区到 Agent OS 的事实、洞察与模式](../tech/openkylin-docs-wiki/references/project-overview.md) | 以七概念方法论（R→I→E→V，standard）全面调研 openKylin：62 条多源事实（2022 社区成立至 2026-09 openKylin 3.0）、4 条四元组洞察、2 个可迁移模式（根社区—商业发行版双轮 / OS 智能体原生化四级演进）、4 视角对抗审查与采纳修正、与优麒麟/银河麒麟/统信 UOS/openEuler 的版图界定。 | 2026-09-29 | - |
| [openKylin 3.0 双 WSL 镜像对照与选型参考（Desktop WSL 远程核验，未落机实测）](../tech/openkylin-docs-wiki/references/wsl-dual-image-selection.md) |  | 2026-09-30 | - |
| [openKylin 3.0 WSL 安装与稀疏 VHD 实操指南（Windows 10 实测）](../tech/openkylin-docs-wiki/references/wsl-install-sparse-vhd-guide.md) |  | 2026-09-29 | - |
| [公网服务器安全加固教程](../tech/public-server-hardening/index.md) | 以七概念方法论（F→V→I 风险证伪 + R→I→E→V 知识沉淀，standard）分析'IP 地址暴露是否有风险'并沉淀为公网服务器加固教程：提取 30 条客观事实、形成 4 条四元组洞察与 1 个 L1 可迁移模式（假设暴露·分层加固法）。教程按运维问题域重组为 8 个概念页：IP 暴露风险本质、暴露面盘点与防火墙、SSH 与暴力破解防御、补丁与源站隐藏、Web 服务加固、最小权限与隔离、监控备份与韧性、非技术人员执行摘要，附信源台账与对抗审查记录。 | 2026-09-30 | server-security、hardening、ssh、firewall、ddos、cdn、backup、ip-exposure |
| [AI Harness 与 Agent Python 包全景调研：从 AutoGPT 退潮到 harness 品类成型](../tech/python-agent-harness/index.md) | 以七概念方法论（R→I→E→V→C，standard）调研 2025-2026 年 AI harness/agent 方向的主流 Python 包：采集 45 条带来源客观事实，覆盖 15+ 个框架/SDK 与编码 agent 赛道，形成 4 条四元组洞察与 1 个可迁移模式（最小充分脚手架选型法，3 个外部独立案例支撑，入库定级 L1-draft）。知识包按问题域拆为生态格局、harness 解剖、框架目录、编码 agent 赛道、选型模式 5 个概念页，附信源台账与对抗审查记录。 | 2026-09-30 | - |
| [Python 与 Rust 技术对比分析报告 Wiki · 总览](../tech/python-rust-comparison/00-overview.md) | 基于最新标准（Python 3.14 / Rust 1.97.1）从零创作的 Python 与 Rust 技术对比分析 Wiki，覆盖语言机制、性能、工程化、生态、应用场景、决策矩阵与迁移路径。 | 2026-08-07 | python、rust、技术选型、性能、混合架构 |
| [Python 与 Rust 技术对比 · 语言与运行时基础](../tech/python-rust-comparison/01-language-runtime.md) | 从最新标准对比 Python 与 Rust 在语法、类型、内存、并发与运行时上的机制差异。 | 2026-08-07 | python、rust、类型系统、内存、并发、异步 |
| [Python 与 Rust 技术对比 · 性能与工程化](../tech/python-rust-comparison/02-performance-engineering.md) | 对比 Python 与 Rust 在运行时性能、资源占用与工程化工具链上的差异。 | 2026-08-07 | python、rust、性能、工具链、工程化 |
| [Python 与 Rust 技术对比 · 生态、应用场景与代码示例](../tech/python-rust-comparison/03-ecosystem-scenarios.md) | 对比 Python 与 Rust 的生态成熟度、典型应用场景，并提供对照代码示例。 | 2026-08-07 | python、rust、生态、应用场景、代码示例 |
| [Python 与 Rust 技术对比 · 决策矩阵与迁移路径](../tech/python-rust-comparison/04-decision-migration.md) | 提供 Python 与 Rust 选型决策矩阵、场景化建议、迁移路径与结论。 | 2026-08-07 | python、rust、决策矩阵、选型建议、迁移、混合架构 |
| [Python 迁移到 Rust 简易检查清单](../tech/python-rust-comparison/05-migration-checklist.md) | 基于《Python 与 Rust 技术对比》报告萃取的迁移到 Rust 的简易检查清单，覆盖决策、热点识别、PoC、逐模块迁移、测试、培训与灰度回退。 | 2026-08-07 | python、rust、迁移、检查清单、混合架构 |
| [量子密信调研：中国电信量子安全办公平台与 QKD+PQC 融合体系](../tech/quantum-secret-messaging/index.md) | 以七概念方法论（R→I→E→V→C，standard）对「量子密信」开展系统性案头研究：采集 50 条带来源客观事实，覆盖产品定义、从量子密话到量子密信的演进、融 QKD 与 PQC 的三层分布式密码体系、16 城量子城域网基础设施、国际安全机构立场与用户评价；形成 4 条四元组洞察与 1 个可迁移模式（双轨分层迁移法，多源支撑但未做本项目实测，入库定级 L1-draft）。知识包按问题域拆为产品定位、演进时间线、技术架构、基础设施、安全边界、采用模式 6 个概念页，附信源台账与对抗审查记录。 | 2026-09-30 | - |
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

*索引自动生成于 2026-10-07 19:07:31*
