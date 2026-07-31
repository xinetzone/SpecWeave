---
id: "volcengine-agentkit-wiki-10"
title: "术语表与参考资源"
source: "seven-concepts: volcengine-agentkit-wiki"
category: "learning"
tags: ["AgentKit", "术语表", "参考资源", "贡献指南"]
date: "2026-07-31"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "AgentKit 官方参考资源清单（产品/文档/社区/教程 4 大类）、30+ 专业术语表、12 个跨 Wiki 交叉引用链接、贡献者指南与版本更新日志。"
last_verified: "2026-07-31"
wiki_version: "1.0"
agentkit_version_target: "2026Q3"

---

# 10 术语表与参考资源

## Part A：官方参考资源清单

| 类别 | 名称 | URL | 更新频率 | 说明 |
|------|------|-----|---------|------|
| 官方产品类 | AgentKit 产品主页 | https://www.volcengine.com/product/agentkit | 月度更新 | 产品核心价值、功能模块、客户案例、定价入口 |
| 官方产品类 | AgentKit 产品简介白皮书 | https://www.volcengine.com/docs/agentkit/overview-whitepaper | 季度更新 | 产品定位、架构全景、行业场景深度解析 PDF |
| 官方产品类 | AgentKit 产品动态新闻 | https://www.volcengine.com/notice/agentkit | 实时更新 | 版本发布、功能上线、活动公告等动态 |
| 官方产品类 | AgentKit 定价文档 | https://www.volcengine.com/pricing/agentkit | 月度更新 | Local/Hybrid/Cloud 三种模式计费规则、阶梯定价计算器 |
| 官方产品类 | AgentKit 控制台入口 | https://console.volcengine.com/agentkit | 实时更新 | 应用创建、配置部署、观测评测、账单查询统一入口 |
| 开发文档类 | VeADK 开发指南（Python） | https://www.volcengine.com/docs/agentkit/veadk-python | 双周更新 | SDK 安装、快速入门、API 参考、装饰器用法 |
| 开发文档类 | VeADK 开发指南（Go） | https://www.volcengine.com/docs/agentkit/veadk-go | 双周更新 | Go SDK 安装、初始化、Harness 定义、Tool 注册示例 |
| 开发文档类 | VeADK 开发指南（Java） | https://www.volcengine.com/docs/agentkit/veadk-java | 双周更新 | Java SDK Maven 依赖、Spring Boot 集成、最佳实践 |
| 开发文档类 | AgentKit CLI 命令参考 | https://www.volcengine.com/docs/agentkit/cli-reference | 月度更新 | init/config/build/deploy/launch 五条命令参数详解 |
| 开发文档类 | Gateway REST API 文档 | https://www.volcengine.com/docs/agentkit/api-gateway | 月度更新 | Tool 接入、A2A 编排、会话管理等 OpenAPI 规范 |
| 场景白皮书类 | 金融行业 Agent 落地白皮书 | https://www.volcengine.com/docs/agentkit/whitepaper-finance | 季度更新 | 金融客服、投顾辅助、风控审查、合规审计场景方案 |
| 场景白皮书类 | 智能客服行业白皮书 | https://www.volcengine.com/docs/agentkit/whitepaper-customer-service | 季度更新 | 多轮对话、工单处理、知识库问答、人工转接方案 |
| 场景白皮书类 | AIOps 智能运维白皮书 | https://www.volcengine.com/docs/agentkit/whitepaper-aiops | 季度更新 | 故障排查、根因分析、告警收敛、自动化修复方案 |
| 场景白皮书类 | 企业知识库问答方案 | https://www.volcengine.com/docs/agentkit/whitepaper-rag | 季度更新 | Knowledge 模块配置、RAG 检索优化、多模态知识方案 |
| 视频教程类 | B 站火山引擎官方账号 | https://space.bilibili.com/volcengine-official | 周更新 | AgentKit 入门实操、VeADK 代码演示、行业案例直播回放 |
| 视频教程类 | 抖音火山引擎官方账号 | https://www.douyin.com/user/volcengine-tech | 周更新 | 60 秒快速上手、功能亮点短视频、开发者访谈 |
| 视频教程类 | YouTube Volcengine Channel | https://www.youtube.com/@volcengine-official | 双周更新 | 英文教程、全球开发者大会演讲、国际客户案例 |
| 社区与支持类 | VeADK GitHub Issues（Python） | https://github.com/volcengine/veadk-python/issues | 实时响应 | SDK Bug 反馈、功能建议、代码贡献讨论 |
| 社区与支持类 | 火山引擎开发者论坛 | https://developer.volcengine.com/forums/agentkit | 工作日响应 | 使用交流、场景讨论、经验分享、问题互助 |
| 社区与支持类 | 工单支持中心（企业版） | https://console.volcengine.com/ticket | 15分钟/2小时SLA | 生产故障、计费问题、架构咨询专属技术支持 |
| 社区与支持类 | 火山引擎技术博客 | https://www.volcengine.com/blog?category=agentkit | 周更新 | 深度技术文章、落地实践复盘、架构设计解读 |

## Part B：核心术语表

### 1. 架构与组件类

**AgentKit**：火山引擎推出的企业级 AI Agent 基础设施平台，提供从代码开发到云端托管运行的全生命周期能力。

**VeADK**：Volcengine Agent Development Kit，火山引擎智能体开源开发套件，提供 Python/Go/Java 三语言 SDK，兼容 Google ADK。

**Harness**：智能体编排配置单元，定义模型、System Prompt、Tool 挂载列表、会话参数等，AgentKit 支持 Session 内热切换。

**Runtime**：智能体运行时模块，提供托管执行环境、运行管理、部署调度能力，支持 Local/Hybrid/Cloud 三种模式。

**Identity**：统一鉴权模块，提供 Agent 独立身份管理、凭据托管、权限边界控制、属性级鉴权能力。

**Gateway**：工具接入统一入口，负责外部系统连接、路由转发、调用治理（超时/重试/熔断）、支持 MCP Server 与 REST 转换双接入。

**A2A**：Agent to Agent 协议，用于构建多 Agent 编排场景，实现跨 Agent 任务分发、结果回传与状态同步。

**Session**：会话管理模块，负责多轮对话中的短期上下文持久化，默认 TTL 7 天可配置自动过期。

**Memory**：长期记忆模块，支持跨会话的信息沉淀与召回，数据经济属性为知识资产，有写入闸门与质量审计机制。

**Knowledge**：知识检索与调优模块，提供向量检索、知识分片、混合检索、知识库管理等 RAG 标准组件能力。

**Observability**：全链路观测模块，覆盖模型/Runtime/Gateway/Tool/Memory-Knowledge 五环节 Trace，支持问题定位。

**Evaluation**：评测与质量闭环模块，提供离线数据集评测、在线流量抽样评测、发布闸门自动化绑定能力。

### 2. 开发与 API 类

**Entrypoint**：智能体入口函数，使用 VeADK 的 `@app.entrypoint` 装饰器定义，是 Runtime 调用的执行起点。

**Tool Decorator**：VeADK 工具注册装饰器 `@app.tool`，将普通 Python/Go/Java 函数包装为 Agent 可调用的 Tool，自动生成参数 Schema。

**Service**：AgentKit Platform 服务集成单元，包含 Memory 服务、Knowledge 服务、MCP Gateway 服务三项核心 Platform Service。

**MCP Server**：Model Context Protocol 标准服务器，通过标准化协议向 Agent 暴露工具能力，支持流式响应与结构化错误码。

**OpenAPI Adapter**：Gateway 模块中 REST/OpenAPI 自动转换适配器，导入 Swagger/OpenAPI 规范自动生成 Tool 定义，无需编写 MCP Server。

### 3. 部署与运维类

**Local 模式**：AgentKit 三种部署模式之一，完全本地运行 VeADK SDK，Platform 服务使用 mock 或最小化实例，适用于开发调试。

**Hybrid 模式**：本地 Runtime 结合云端治理服务的混合部署模式，满足数据合规（本地）与治理能力复用（云端）双重需求。

**Cloud 模式**：全托管 Serverless 部署模式，Runtime 秒级弹性扩缩容、多租户数据严格隔离，适用于生产规模化运行。

**Serverless 弹性**：Cloud 模式底层基于 VeFaaS 函数计算，按并发数/CPU/内存阈值自动扩缩容，无流量时缩容到 0 计费归零。

**多租户隔离**：Cloud 模式通过逻辑软隔离（行级租户 ID 强制透传）或硬隔离（独立 Runtime 实例）实现租户间资源与数据严格隔离。

**冷启动**：Serverless 模式首次请求或长时间无流量后实例从零启动的过程，包含依赖加载、连接建立等，优化后可降到 1 秒内。

**热启动**：实例池预热或请求命中已加载实例的启动过程，仅需执行业务逻辑，响应延迟显著低于冷启动。

### 4. 安全与治理类

**属性级鉴权**：Identity 模块支持基于用户/Agent 属性（部门、角色、安全等级、地理位置等）的动态权限决策，比静态 RBAC 更灵活。

**IdP**：Identity Provider 身份提供商，企业版支持自定义 IdP（如企业微信、钉钉、Okta、Azure AD）通过 OIDC/SAML 协议集成单点登录。

**凭据托管**：Identity 模块内置 Secret Manager，统一管理外部系统 AK/SK/Token，代码与配置文件中零明文密钥存储。

**内容护栏**：Identity 模块中用户输入与模型输出的安全管控规则集，包含敏感词拦截、Prompt 注入检测、合规输出校验等。

**最小权限原则**：Agent 权限治理核心原则，仅授予完成特定任务场景所必需的最小 Tool 白名单与数据访问范围，而非管理员权限。

### 5. 质量与评测类

**离线评测**：Evaluation 模块中基于固定标注数据集的自动化评测，在发布前执行，用于验证新 Agent 版本核心能力达标情况。

**在线评测**：Evaluation 模块中基于真实生产流量抽样的评测，对比新版本与稳定版本在真实用户输入下的表现差异。

**A/B 实验**：Evaluation 模块支持的流量分割评测方法，将一定比例流量路由到新版本，与基线版本统计对比核心业务指标。

**发布闸门**：CI/CD Pipeline 中绑定的 Evaluation 自动化拦截规则，新版本评测通过率低于阈值（默认 90%）则自动阻止发布。

**Trace ID**：全链路唯一请求标识，贯穿 Observability 五环节，用于串联单次请求各阶段的耗时、状态码、输入输出摘要。

**用户满意度**：在线评测指标之一，通过对话结束后人工点赞点踩（CSAT）或后续行为转化率间接衡量 Agent 回答质量。

### 6. 协议与标准类

**MCP**：Model Context Protocol 模型上下文协议，由 Anthropic 主导的 Agent 工具接入行业标准，AgentKit Gateway 原生支持。

**A2A**：Agent to Agent 协议，由 Google 主导的多 Agent 协作标准，定义 Agent 间任务分发、状态同步、结果回传规范。

**OIDC**：OpenID Connect 开放身份连接协议，基于 OAuth 2.0 的轻量级身份认证标准，用于 IdP 集成与单点登录。

**SAML**：Security Assertion Markup Language 安全断言标记语言，企业级 SSO 传统标准，大型企业 IdP 集成常用协议。

**OpenAPI Spec**：REST API 描述规范（原 Swagger），定义 API 的 URL、Method、参数 Schema、响应格式，Gateway 导入后可自动生成 Tool。

**RESTful**：Representational State Transfer 表现层状态转移，基于 HTTP 动词的 Web API 设计风格，AgentKit Gateway 自动转换存量接口。

## Part C：社区贡献指南

### 1. 开源提交流程

VeADK 开源仓库贡献四步走：
1. **Fork 仓库**：在 GitHub 上 fork 对应语言仓库（veadk-python / veadk-go / veadk-java）到个人账号
2. **创建新分支**：从 main 分支拉取 feature/fix 分支，命名规范 `feature/{描述}` 或 `fix/{issue编号}`
3. **提交规范**：遵循 Conventional Commits 规范（`feat(scope): 中文描述` / `fix(scope): 中文描述`），单次提交单一职责，附单元测试
4. **Pull Request**：提交 PR 指向上游 main 分支，PR 描述包含变更动机、改动点、测试验证结果，等待 Maintainer Review 后合入

### 2. Issue 模板与标签

GitHub Issues 统一使用预设模板分类：
- **Bug 类标签（bug）**：功能与文档描述不一致、运行报错、性能异常；需附复现步骤、环境版本、错误日志截图
- **功能需求类标签（enhancement）**：新增功能、API 扩展、性能优化建议；需附使用场景、期望行为、备选方案讨论
- **问题咨询类标签（question）**：使用疑问、文档歧义、最佳实践咨询；优先搜索 closed issues 和论坛避免重复提问

### 3. 文档改进指引

发现文档错误或有改进建议时，两种反馈渠道：
1. **文档评论反馈**：官方文档站（volcengine.com/docs/agentkit）每页底部有「文档是否有用」评价按钮与评论框，直接留言问题，文档团队 2 个工作日内响应
2. **提交修复 PR**：技术文档部分（如 VeADK 代码示例、CLI 参数说明）可直接在对应 VeADK 仓库中找到 Markdown 源文件，按上述开源提交流程提交文档修复 PR

## Part D：教程版本历史

| 版本 | 发布日期 | 主要更新 |
|------|---------|---------|
| v1.0 | 2026-07-31 | 初版发布，11 章完整教程（概述→产品介绍→核心架构→部署→可观测→安全→核心功能→对比→FAQ→术语表），术语 37 条，FAQ 16 条，Mermaid 图 8 个 |
| v1.1 | 预留行 | 待补充：DeepResearch 专项章节、多 Agent 实战案例、金融行业深度方案、性能调优指南 |

## 最后结语

感谢您完整阅读本套 AgentKit 教程。从产品定位、核心架构、部署模式，到治理四板斧、功能详解、竞品对比，再到 FAQ 与最佳实践，我们力求构建一份「可落地、可审计、可复用」的系统化知识库，而非零散的功能介绍合集。

如果您在学习或落地过程中遇到任何问题，欢迎通过以下渠道反馈：GitHub Issues（SDK Bug / 功能建议）、火山引擎开发者论坛（使用交流 / 场景讨论）、工单系统（企业版生产故障 / 架构咨询）。您的每一条反馈都是下一个版本迭代的重要输入。

最后，建议您将本教程的方法论与「R-I-E-V 持续学习循环」结合：**R**ead（重读核心章节，对照实际项目场景）→ **I**mplement（按最佳实践在 Local 模式跑通第一个 Agent）→ **E**valuate（用 12 项检查清单做生产化验收，记录评测指标）→ **V**alidate（上线后用 Observability 数据复盘差距，补充 FAQ 与用例）→ 回到 R。持续迭代循环，才能将 AgentKit 的平台能力真正内化为团队的工程生产力。

## 本章小结

本章提供了**官方资源、术语体系、社区协作、版本追踪**四方面的支撑体系：

1. **官方资源清单**：5 大类共 21 条资源链接（产品/文档/白皮书/视频/社区），域名均为火山引擎官方域名，覆盖从入门到生产全阶段
2. **核心术语表**：6 大类共 37 条术语（架构 12 + 开发 5 + 部署 7 + 安全 5 + 质量 6 + 协议 6），每条给出 20-50 字精确定义，建立统一沟通语言
3. **社区贡献指南**：开源提交四步流程、三类 Issue 标签规范、文档改进双渠道反馈机制
4. **版本历史 + 方法论寄语**：以 R-I-E-V 循环收束全文，从知识消费走向持续生产

---

**导航：**
← [09 FAQ 与最佳实践](./09-faq-best-practices.md) | [返回目录](./README.md) | → 教程结束 🎉
