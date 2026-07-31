---
id: "volcengine-agentkit-wiki-03"
title: "VeADK 智能体开发框架"
source: "seven-concepts: volcengine-agentkit-wiki"
category: "learning"
tags: ["AgentKit", "VeADK", "火山引擎", "SDK", "开发框架"]
date: "2026-07-31"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "VeADK（Volcengine Agent Development Kit）智能体开发框架详解：三语言 SDK 安装、与 Google ADK 兼容说明、VeADK Family 20+ 产品融合矩阵、DeepResearch 6 大构建特性、GitHub 开源仓库清单。"
last_verified: "2026-07-31"
wiki_version: "1.0"
agentkit_version_target: "2026Q3"

---

# 03 VeADK 智能体开发框架

## 什么是 VeADK？与 Google ADK 的兼容性

VeADK 全称为 Volcengine Agent Development Kit，是火山引擎推出的企业级智能体开发套件，面向开发者提供 Python、Go、Java 三种主流语言的 SDK 支持，覆盖大模型接入、提示词工程、工具执行、记忆存储、知识库检索、可观测评测与云部署全流程能力。VeADK 作为 AgentKit 平台的代码侧入口，是连接开发者本地工程与云端托管运行时的标准桥梁，支持本地调试、混合部署与云托管三种交付模式。

VeADK 在设计阶段即与 Google ADK（Agent Development Kit）实现完全兼容，核心 API 语义、组件抽象、消息协议均保持一致。这一兼容性设计带来两方面直接收益：其一，已经基于 Google ADK 构建的智能体项目可实现无缝迁移，仅需替换 SDK 包名与认证配置，核心业务代码无需改写，迁移成本接近于零；其二，开发者学习曲线显著平滑，Google ADK 生态中的既有经验、代码范式、最佳实践均可直接复用到 VeADK 开发中，降低团队上手门槛与培训成本。同时，VeADK 在 Google ADK 基础上扩展了火山引擎产品矩阵的深度集成能力，通过 LiteLLM 兼容层支持各类主流大模型接入，为企业提供开放而不失深度的开发体验。

## 三语言安装

### Python SDK 安装

方式一：PyPI 官方镜像（稳定版 latest）
```bash
pip install veadk-python -i https://pypi.tuna.tsinghua.edu.cn/simple
```

方式二：GitHub 主仓库主分支预览版
```bash
pip install git+https://github.com/volcengine/veadk-python.git@main
```

方式三：火山引擎私有镜像指定版本（如 0.2.20）
```bash
pip install veadk-python==0.2.20 --index-url https://pypi.volces.com/simple
```

### Go SDK 安装

方式一：go get GitHub 主仓库
```bash
go get github.com/volcengine/veadk-go@latest
```

方式二：go get Gitee 镜像仓库（国内加速）
```bash
go get gitee.com/volcengine/veadk-go@latest
```

方式三：go mod 指定版本
```bash
go get github.com/volcengine/veadk-go@v0.2.20
```

### Java SDK 安装

方式一：Maven pom.xml 引入（groupId: com.volcengine.veadk）
```xml
<dependency>
    <groupId>com.volcengine.veadk</groupId>
    <artifactId>veadk-java</artifactId>
    <version>0.2.20</version>
</dependency>
```

方式二：Gradle 依赖声明
```groovy
dependencies {
    implementation 'com.volcengine.veadk:veadk-java:0.2.20'
}
```

方式三：Gradle Kotlin DSL
```kotlin
dependencies {
    implementation("com.volcengine.veadk:veadk-java:0.2.20")
}
```

## VeADK Family 产品融合矩阵

VeADK Family 产品矩阵覆盖 9 大类组件，与火山引擎 20+ 款产品深度融合，开发者可按需组合使用。下表列出核心映射关系：

| 类别 | 组件名 | 对应火山引擎产品 | 能力说明 | 是否开源 |
|------|--------|-----------------|---------|---------|
| 大模型接入 | ModelClient LiteLLM | 火山方舟 Ark | 多模型统一接入，兼容 LiteLLM 推理协议，支持 Doubao/Llama/Qwen 等 | ✓ |
| 大模型接入 | ModelRouter | 火山方舟 Ark | 多模型智能路由、降级切换、成本优化与质量对比 | ✓ |
| 提示词工程 | PromptTemplate Engine | 火山方舟 Prompt 管理 | 版本化提示词模板、变量注入、A/B 测试与效果追踪 | ✓ |
| 提示词工程 | PromptOptimizer | 火山方舟 Ark | 提示词自动优化、Token 压缩、意图对齐增强 | ✗ |
| 工具执行 | ToolExecutor | AgentKit Gateway | 工具注册、调用治理、超时重试、熔断限流与审计日志 | ✓ |
| 工具执行 | MCP Adapter | AgentKit Gateway | MCP Server 接入、REST/OpenAPI 自动转换为 Tool | ✓ |
| 记忆存储 | ShortTermMemory | AgentKit Session | 多轮会话上下文持久化、滑动窗口截断与摘要压缩 | ✓ |
| 记忆存储 | LongTermMemory | Viking DB 向量库 | 跨会话信息沉淀、向量检索召回、知识图谱关联 | ✓ |
| 知识库 | KnowledgeRetriever | AgentKit Knowledge | 知识库文档切片、语义检索、Rerank 重排与引用溯源 | ✗ |
| 知识库 | KnowledgeIngestor | 火山方舟 Knowledge | 多格式文档（PDF/Word/Markdown）解析入库、增量同步 | ✗ |
| 可观测 | TraceCollector | APMPlus 应用性能监控 | 调用链路追踪、耗时统计、错误定位与火焰图分析 | ✓ |
| 可观测 | MetricExporter | 云监控 VolcMonitor | Token 用量、请求 QPS、成功率、延迟分位指标采集 | ✓ |
| 可观测 | AuditLogger | TLS 日志服务 | 全量审计日志、敏感操作记录、合规检索与告警 | ✗ |
| 评测 | EvalRunner | AgentKit Evaluation | 上线前评测集执行、准确率/相关性/幻觉率多维度打分 | ✓ |
| 评测 | EvalComparator | AgentKit Evaluation | 多模型/多版本智能体效果对比、发布闸门控制 | ✗ |
| 评测 | AdversarialTester | 对抗审查框架 | Prompt 注入测试、越权检测、越狱攻击防护验证 | ✓ |
| 云部署 | CloudDeployer | AgentKit Runtime | 一键部署到 Serverless 运行时、版本管理与灰度发布 | ✓ |
| 云部署 | AutoScaler | VeFaaS 函数服务 | 秒级弹性扩缩容、冷启动优化、并发度控制 | ✗ |
| 云部署 | SecretsManager | 密钥管理服务 KMS | AK/SK、API Key 等敏感凭据托管、自动轮换与加密 | ✗ |

## DeepResearch 6 大构建特性

### 特性一：多生态与模型兼容
**能力描述**：基于 LiteLLM 兼容层设计，VeADK 可接入火山方舟（Doubao 系列）、OpenAI、Anthropic Claude、Google Gemini、智谱 AI、通义千问等主流大模型，统一 API 屏蔽底层差异。支持多模型并行调用与路由策略，可按成本、延迟、质量维度动态选择最优模型。
**产品支撑**：火山方舟 Ark + ModelRouter 组件
**使用场景**：企业多模型混用、跨云模型容灾切换、按任务复杂度选择不同规格模型降本增效。

### 特性二：完善的记忆与知识库支持
**能力描述**：内置短期记忆（Session 级上下文持久化）与长期记忆（跨会话向量检索召回）分层架构，提供滑动窗口截断、摘要压缩、语义去重等记忆优化策略。知识库侧支持多格式文档解析、增量同步、语义检索 + Rerank 重排 + 引用溯源的标准 RAG 流水线。
**产品支撑**：Viking DB 向量库 + AgentKit Knowledge 组件
**使用场景**：企业内部知识库问答、多轮对话需要长期记忆的助理类应用、跨会话信息沉淀的客户服务场景。

### 特性三：内置丰富工具和生态集成
**能力描述**：Tool 执行层内置 MCP Server 适配器与 REST/OpenAPI 自动转换工具，可将企业现有业务 API 零代码转化为智能体可调用工具。预置搜索、文件读写、代码执行、日历邮件等通用工具集，支持自定义工具注册与权限粒度控制。
**产品支撑**：AgentKit Gateway + MCP Adapter 组件
**使用场景**：存量业务系统智能化改造、内部 REST API 快速开放给智能体调用、多企业系统统一接入治理。

### 特性四：可观测性与评估能力
**能力描述**：全链路观测区分模型调用、Runtime 执行、Gateway 路由、Tool 执行、Memory/Knowledge 检索各环节，提供调用链追踪、Token 用量指标、成功率/延迟监控与审计日志。评测体系支持离线评测集、线上 A/B 对比、对抗性攻击测试三类质量验证手段，形成发布闸门。
**产品支撑**：APMPlus + AgentKit Evaluation + TLS 日志服务
**使用场景**：生产环境问题排障、智能体版本迭代效果验证、合规审计与敏感操作追踪。

### 特性五：云原生架构与快速部署
**能力描述**：基于 Serverless 底座设计，智能体应用打包为标准容器镜像后一键部署，秒级弹性扩缩容，无需管理底层服务器。支持版本管理、灰度发布、流量切分、自动回滚等云原生发布能力。三种部署模式（Local/Hybrid/Cloud）灵活切换，实现本地调试与云端交付的一致性体验。
**产品支撑**：AgentKit Runtime + VeFaaS 函数服务
**使用场景**：从 Demo 快速投产到生产环境、应对突增流量的弹性伸缩、需要多环境隔离的企业级交付。

### 特性六：企业级安全防护
**能力描述**：三层安全防护模型：身份管控层（用户身份 + 智能体身份 + 工具访问权限统一治理）、云身份管控层（基于 IAM 的细粒度授权与凭据托管）、内容护栏层（输入输出敏感信息过滤、Prompt 注入检测、越狱攻击防护、内容合规审核）。多租户数据与资源严格隔离。
**产品支撑**：AgentKit Identity + IAM + KMS 密钥管理
**使用场景**：金融/政企等高合规行业部署、多部门共享智能体平台的权限隔离、敏感数据防泄漏治理。

## 开源仓库清单

VeADK 三语言 SDK 均在 GitHub 开源，接受社区 Issue 与 Pull Request 贡献，同步提供国内镜像加速访问：

| 仓库名 | GitHub URL | 镜像 URL（Gitee） | 语言 | 主要内容 |
|--------|-----------|-----------------|------|---------|
| veadk-python | https://github.com/volcengine/veadk-python | https://gitee.com/volcengine/veadk-python | Python | Python SDK 核心实现、示例工程、单元测试、文档 |
| veadk-go | https://github.com/volcengine/veadk-go | https://gitee.com/volcengine/veadk-go | Go | Go SDK 核心实现、泛型工具层、集成测试 |
| veadk-java | https://github.com/volcengine/veadk-java | https://gitee.com/volcengine/veadk-java | Java | Java SDK 核心实现、Spring Boot Starter、Maven 插件 |
| veadk-examples | https://github.com/volcengine/veadk-examples | https://gitee.com/volcengine/veadk-examples | 多语言 | 官方示例工程集合：HelloWorld、RAG 问答、多 Agent 协作、工具接入 |
| veadk-tool-registry | https://github.com/volcengine/veadk-tool-registry | https://gitee.com/volcengine/veadk-tool-registry | Python/Go | 社区贡献工具集：搜索、文件、日历、邮件、代码执行等通用 Tool 实现 |
| veadk-helm-charts | https://github.com/volcengine/veadk-helm-charts | https://gitee.com/volcengine/veadk-helm-charts | YAML/Smarty | Kubernetes 部署 Helm Charts，支持 Hybrid 模式私有化部署 |

## 本章小结

本章系统介绍了 VeADK 智能体开发框架的定位与核心能力：它作为火山引擎与 Google ADK 完全兼容的三语言开发套件，是连接开发者本地工程与 AgentKit 云端运行时的标准入口。VeADK Family 产品矩阵通过 9 大类组件与火山引擎 20+ 产品深度融合，覆盖从模型接入到云部署的全流程能力；DeepResearch 6 大构建特性（多生态兼容、记忆知识库、丰富工具集、可观测评测、云原生部署、企业级安全）为企业级智能体开发提供开箱即用的能力底座；6 个核心开源仓库（三语言 SDK + 示例 + 工具集 + Helm 部署）形成完整的社区生态支撑。

掌握 VeADK 开发框架后，下一章将进入 AgentKit SDK & CLI 工具链的学习，了解如何基于装饰器式 API 优雅开发智能体应用，以及如何使用 CLI 命令实现一键初始化、构建、部署与运行。

← [02 架构](./02-core-architecture.md) | [README](./README.md) | → [04 SDK & CLI](./04-agentkit-sdk-cli.md)
