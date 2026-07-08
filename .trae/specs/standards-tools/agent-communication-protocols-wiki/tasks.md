---
version: 1.0
x-toml-ref: "../../../../.meta/toml/.trae/specs/standards-tools/agent-communication-protocols-wiki/tasks.toml"
---
# Agent 通信协议体系（MCP/ACP/A2A/ANP）Wiki 教程 - The Implementation Plan

<!-- changelog -->
- 2026-07-03 | feat | 初始任务分解创建

## [x] Task 1: 创建教程子目录与总览入口文档（00-overview）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建原子化子目录 `docs/knowledge/learning/agent-communication-protocols/`
  - 创建总览入口文档 `docs/knowledge/learning/agent-communication-protocols-wiki.md`，包含：
    - 教程简介与学习路径建议
    - 四大协议全景概述（MCP/ACP/A2A/ANP 一句话定位）
    - 协议分层架构 Mermaid 图（四层：工具层→本地消息层→跨平台协作层→去中心化网络层）
    - 各章节导航链接表
    - 面向读者的阅读建议
  - 创建 `00-overview.md` 子文件作为总览详细章节，包含背景、协议生态全景、为什么需要标准化协议、N×M 集成问题说明
- **Acceptance Criteria Addressed**: AC-1, AC-10
- **Test Requirements**:
  - `programmatic` TR-1.1: 子目录 `docs/knowledge/learning/agent-communication-protocols/` 存在
  - `programmatic` TR-1.2: 总览入口文件存在且包含 TOML frontmatter（version 字段）
  - `programmatic` TR-1.3: `00-overview.md` 存在且包含 Mermaid 架构图
  - `human-judgement` TR-1.4: 总览文档逻辑清晰、导航链接完整、学习路径合理
- **Notes**: 参考现有 agent-skills-wiki 的 00-overview.md 结构风格

## [x] Task 2: 编写 MCP（Model Context Protocol）深度章节（01-mcp）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `01-mcp.md`，内容包括：
    - MCP 定义、发起方（Anthropic）、发布时间（2024年11月）、治理（Linux基金会）
    - 核心定位：Agent↔工具/数据连接（"AI的USB-C接口"类比）
    - 三大核心能力：上下文数据注入、功能路由与调用、提示词编排
    - 架构设计：Client-Server 架构 Mermaid 图
    - 关键概念：Tools、Resources、Prompts 三大原语
    - 传输协议：stdio（本地）、Streamable HTTP（远程）、SSE（流式）
    - 消息格式：JSON-RPC 2.0
    - 认证机制：OAuth 2.1
    - Agent Card/发现机制
    - MCP 在协议栈中的位置（纵向：Agent↔工具）
    - 与其他协议的关系说明
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 文件存在且包含 TOML frontmatter（含 source 溯源字段）
  - `programmatic` TR-2.2: 包含至少 1 个 Mermaid 架构图
  - `human-judgement` TR-2.3: 内容覆盖定义/发起方/核心功能/定位/架构/关键概念/传输/消息格式/安全
  - `human-judgement` TR-2.4: 技术描述准确，与官方规范一致

## [x] Task 3: 编写 ACP（Agent Communication Protocol）深度章节（02-acp）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `02-acp.md`，内容包括：
    - ACP 定义、发起方（IBM Research/BeeAI）、发布时间（2025年3月）、治理（Linux基金会 AI & Data）
    - 核心定位：本地优先/边缘/企业内网的 Agent↔Agent 对等通信（"AI的局域网Wi-Fi"类比）
    - 设计理念：REST原生、零SDK、本地优先、去中心化对等、低延迟
    - 架构设计：去中心化 P2P 架构 Mermaid 图
    - 关键概念：Agent Cards、mDNS本地发现、Task生命周期、MIME类型内容协商
    - 传输协议：RESTful HTTP、gRPC、ZeroMQ、本地总线/IPC（灵活多选）
    - 消息格式：REST + JSON/OpenAPI，MIME多部分消息
    - 离线发现能力（元数据打包在Docker镜像中）
    - 安全机制：DID、RBAC、本地安全模型
    - 无需SDK即可用curl/Postman交互的特点
    - ACP 在协议栈中的位置（横向本地层：Agent↔Agent本地P2P）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件存在且包含 TOML frontmatter
  - `programmatic` TR-3.2: 包含至少 1 个 Mermaid 架构图
  - `human-judgement` TR-3.3: 内容覆盖定义/发起方/核心功能/定位/架构/关键概念/传输/消息格式/安全
  - `human-judgement` TR-3.4: 准确体现 ACP 区别于 A2A 的本地优先、REST原生、零SDK等特性

## [x] Task 4: 编写 A2A（Agent-to-Agent Protocol）深度章节（03-a2a）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `03-a2a.md`，内容包括：
    - A2A 定义、发起方（Google）、发布时间（2025年4月）、治理（Linux基金会，2025年6月捐赠）
    - 核心定位：跨厂商/跨平台/跨组织的 Agent↔Agent 协作（"智能体互联网的HTTP"类比）
    - 五大设计原则：拥抱智能体能力、基于现有标准、默认安全、支持长时任务、模态无关
    - 架构设计：Client-Server 模型 Mermaid 图（User/Client/Server 三方）
    - 关键概念：Agent Card、Task（有状态任务）、Artifact（工件）、Message、Part（TextPart/FilePart/DataPart）
    - 传输协议：HTTP/HTTPS（强制），JSON-RPC 2.0 over HTTP
    - 流式通信：SSE（Server-Sent Events）
    - 发现机制：Well-Known URI（`/.well-known/agent.json`）、注册中心
    - 交互模式：同步请求/响应、SSE流式、Push Notification Webhook
    - 任务状态机：Submitted→Working→Input-Required→Completed/Failed/Canceled
    - 安全机制：OAuth2、API Key、mTLS、DID/VC，认证凭证在HTTP Header
    - 模态支持：文本、文件（图像/文档/Base64/URI）、结构化数据/表单
    - A2A 在协议栈中的位置（横向跨平台层：Agent↔Agent跨厂商协作）
    - 生态现状：50+初始合作伙伴、150+组织支持、全语言SDK
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-4.1: 文件存在且包含 TOML frontmatter
  - `programmatic` TR-4.2: 包含至少 1 个 Mermaid 架构图
  - `human-judgement` TR-4.3: 内容覆盖定义/发起方/核心功能/定位/架构/关键概念/传输/消息格式/安全/生态
  - `human-judgement` TR-4.4: 准确体现 A2A 区别于 ACP 的跨厂商、Web原生、企业级安全、长任务支持等特性

## [x] Task 5: 编写 ANP（Agent Network Protocol）概述章节（04-anp）
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 创建 `04-anp.md`，内容包括：
    - ANP 定义：面向开放网络/去中心化 Agent 市场的协议
    - 核心定位：去中心化 Agent 发现与安全协作（"Agent经济的互联网层"类比）
    - 关键技术：W3C DID（去中心化标识符）、JSON-LD 图谱
    - 设计目标：开放网络中的 Agent 发现、身份验证、可信协作
    - 与其他三层协议的关系：在 A2A 之上扩展去中心化能力
    - 当前发展阶段：新兴协议，处于早期阶段
    - 应用场景：Agent 市场/经济、跨信任域协作
  - 说明：ANP 规范尚在早期，本节以概述为主，深度可适当低于前三个协议
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-5.1: 文件存在且包含 TOML frontmatter
  - `human-judgement` TR-5.2: 内容客观反映 ANP 的早期阶段，不做过度推测
  - `human-judgement` TR-5.3: 清晰说明 ANP 与其他协议的分层关系

## [x] Task 6: 编写协议对比与分层架构章节（05-comparison）
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5
- **Description**:
  - 创建 `05-comparison.md`，内容包括：
    - 四层协议栈分层模型 Mermaid 图（MCP工具层→ACP本地消息层→A2A跨平台层→ANP去中心化层）
    - 多维度技术对比表：发起方/发布时间/核心定位/传输层/消息格式/发现机制/SDK依赖/交互模式/安全模型/典型场景/生态规模/延迟特性/网络依赖
    - ACP vs A2A 深度对比小节（架构哲学差异、优劣势分析）
    - MCP vs ACP/A2A 关系说明（纵向 vs 横向，USB-C vs Wi-Fi vs HTTP 类比）
    - 互补关系说明：三者不是竞争关系而是分层协作
    - 选型决策树 Mermaid flowchart（基于场景选择协议组合）
    - 分阶段采用路线图（学术论文建议：MCP→ACP→A2A→ANP）
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-6.1: 文件存在且包含 TOML frontmatter
  - `programmatic` TR-6.2: 包含至少 2 个 Mermaid 图（分层架构图 + 选型决策树）
  - `human-judgement` TR-6.3: 对比维度全面、客观、无厂商偏向
  - `human-judgement` TR-6.4: 清晰传达"互补而非竞争"的核心观点

## [x] Task 7: 编写交互流程与协作模式章节（06-flows）
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 创建 `06-flows.md`，内容包括：
    - 流程1：单 Agent 通过 MCP 调用工具（Mermaid sequenceDiagram）
      - 用户→Agent→MCP Client→MCP Server→外部API/数据库→结果返回链
    - 流程2：多 Agent 通过 A2A 跨平台任务委派（Mermaid sequenceDiagram）
      - Client Agent 发现 Agent Card → 协商协议 → 提交 Task → 流式状态更新（SSE）→ Artifact 返回
    - 流程3：本地多 Agent 通过 ACP 对等协作（Mermaid sequenceDiagram）
      - mDNS 发现 → 能力广播 → 任务委派（REST）→ 结果返回
    - 流程4：混合场景——企业数字员工团队端到端协作（Mermaid sequenceDiagram）
      - 展示 MCP+ACP+A2A 如何协同工作
    - 任务生命周期状态转换 Mermaid stateDiagram（以 A2A 为例）
    - 典型协作模式分类：中心化编排、去中心化P2P、分层混合
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-7.1: 文件存在且包含 TOML frontmatter
  - `programmatic` TR-7.2: 包含至少 4 个 Mermaid 时序图 + 1 个状态图
  - `human-judgement` TR-7.3: 时序图消息方向正确、步骤逻辑清晰
  - `human-judgement` TR-7.4: 混合场景体现三协议协同工作方式

## [x] Task 8: 编写技术实现要点与代码示例章节（07-implementation）
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 创建 `07-implementation.md`，内容包括：
    - Agent Card 格式详解与 JSON 示例（A2A Well-Known URI 格式 + ACP 元数据格式对比）
    - MCP 核心 API 示例：
      - 工具注册与调用（JSON-RPC 请求/响应示例）
      - curl 调用 MCP Server 示例
    - A2A 核心 API 示例：
      - tasks/send 任务提交请求/响应
      - tasks/get 状态查询
      - SSE 流式消息格式
      - curl 调用 A2A Agent 示例
      - Python SDK 最小示例
    - ACP 核心 API 示例：
      - POST /tasks 任务创建
      - 任务状态轮询
      - curl 直接调用示例（突出零SDK特性）
    - 消息结构详解（Message/Part/Artifact 数据模型）
    - 安全认证配置要点
    - 常见集成陷阱与最佳实践
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-8.1: 文件存在且包含 TOML frontmatter
  - `programmatic` TR-8.2: JSON 示例格式合法（人工审核）
  - `programmatic` TR-8.3: curl 命令格式正确、参数完整
  - `human-judgement` TR-8.4: 代码示例语法正确、可作为开发者参考
  - `human-judgement` TR-8.5: 覆盖至少 3 种协议的 API 调用示例

## [x] Task 9: 编写典型应用场景章节（08-scenarios）
- **Priority**: medium
- **Depends On**: Task 6, Task 7
- **Description**:
  - 创建 `08-scenarios.md`，内容包括：
    - 场景1：企业数字员工团队（HR Agent→财务Agent→法务Agent→IT Agent）
      - 推荐协议组合：A2A（跨系统）+ MCP（接企业SaaS）
      - 协作流程说明
    - 场景2：跨组织/跨SaaS协作（Salesforce Agent ↔ SAP Agent ↔ 客户自定义Agent）
      - 推荐协议：A2A（跨厂商）+ MCP
      - 安全认证与权限控制要点
    - 场景3：边缘设备/IoT/机器人集群（无人机群、IoT传感器网络）
      - 推荐协议：ACP（本地低延迟）+ 可选 MCP（本地工具）
      - 离线/断网场景处理
    - 场景4：去中心化 Agent 市场/经济
      - 推荐协议：ANP（发现/身份）+ A2A（协作）+ MCP（工具）
    - 场景5：AI 编码助手多工具协作（IDE 内 Agent 调用 linter/debugger/deploy）
      - 推荐协议：MCP（工具连接）
    - 每个场景包含：场景描述、推荐协议组合、架构示意图（Mermaid 简化图）、关键实现要点
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-9.1: 文件存在且包含 TOML frontmatter
  - `human-judgement` TR-9.2: 至少覆盖 4 类场景（企业内部/跨组织/边缘IoT/去中心化市场）
  - `human-judgement` TR-9.3: 每个场景协议推荐合理、理由充分
  - `human-judgement` TR-9.4: 场景描述贴近实际、可落地参考

## [x] Task 10: 编写术语表章节（09-glossary）
- **Priority**: medium
- **Depends On**: Task 2, Task 3, Task 4, Task 5
- **Description**:
  - 创建 `09-glossary.md`，内容包括：
    - 按字母顺序排列的关键术语解释，至少 15 个术语
    - 术语应覆盖：JSON-RPC、SSE（Server-Sent Events）、Agent Card、Task、Artifact、Part、Message、DID（Decentralized Identifier）、mDNS、MIME、OAuth 2.1、SDK、Client-Server架构、P2P（Peer-to-Peer）、流式通信（Streaming）、Webhook、OpenAPI、JSON-LD、Well-Known URI、状态机、Long-running Task、Human-in-the-loop、Tool/Resource/Prompt原语
    - 每个术语包含：中英文名称、简明定义、在哪个协议中使用、交叉引用到详细章节
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-10.1: 文件存在且包含 TOML frontmatter
  - `programmatic` TR-10.2: 术语数量 ≥ 15 个
  - `human-judgement` TR-10.3: 术语定义准确、简明、易于理解
  - `human-judgement` TR-10.4: 交叉引用链接正确

## [x] Task 11: 编写资源与参考链接章节（10-resources）
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 创建 `10-resources.md`，内容包括：
    - 官方规范链接：
      - MCP 官方文档与规范
      - ACP 官方文档（agentcommunicationprotocol.dev）、IBM Research博客
      - A2A 官方文档（a2a-protocol.org / a2aprotocol.ai）、规范（v0.2.5）
      - ANP 相关资料
    - GitHub 仓库：
      - MCP SDK 仓库
      - ACP 官方仓库（i-am-bee/acp）
      - A2A 官方仓库、SDK
    - 学术论文：
      - arXiv:2505.02279（四大协议综述）
      - arXiv:2505.03864（A2A+MCP集成分析）
    - SDK 与工具：
      - Python/JS/Java/Go SDK 链接
      - A2A Inspector 调试工具
    - 相关文章与中文解读资源
    - 分类整理，每类附简要说明
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-11.1: 文件存在且包含 TOML frontmatter
  - `programmatic` TR-11.2: 链接格式正确（Markdown链接）
  - `human-judgement` TR-11.3: 资源分类清晰、覆盖官方规范/GitHub/论文/SDK四大类

## [x] Task 12: 编写快速参考/速查表章节（11-quick-reference）
- **Priority**: low
- **Depends On**: Task 6, Task 7
- **Description**:
  - 创建 `11-quick-reference.md`，内容包括：
    - 四大协议快速对比表（精简版，一眼看懂）
    - 协议选型 CheckList（回答几个问题快速选协议）
    - 核心 API 端点速查表
    - Agent Card 最小可用模板
    - 常见问题 FAQ（5-8个常见疑问）
- **Acceptance Criteria Addressed**: AC-1（补充导航完整性）
- **Test Requirements**:
  - `programmatic` TR-12.1: 文件存在且包含 TOML frontmatter
  - `human-judgement` TR-12.2: 速查表简洁实用、便于快速查阅

## [x] Task 13: 更新知识库索引与导航
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12
- **Description**:
  - 确认所有子文件与总览入口之间的交叉引用正确
  - 运行知识库索引生成脚本（如有）或手动确保新文档可被发现
  - 确认总览入口文档（agent-communication-protocols-wiki.md）包含完整章节导航
  - 更新各子文件中的相对路径交叉引用
  - 确保所有 Mermaid 图表遵循安全编码六规则
  - 检查所有 TOML frontmatter 格式正确
- **Acceptance Criteria Addressed**: AC-9, AC-10, AC-11, AC-12
- **Test Requirements**:
  - `programmatic` TR-13.1: 所有文件位于正确目录（docs/knowledge/learning/agent-communication-protocols/ + 入口文件在learning/根目录）
  - `programmatic` TR-13.2: 运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning/agent-communication-protocols` 无断链、无 file:/// 绝对路径
  - `programmatic` TR-13.3: 所有 Mermaid 代码块对照 mermaid-guide.md 六规则人工审核通过
  - `programmatic` TR-13.4: 所有 .md 文件包含 TOML frontmatter（含 version 字段），子文件含 source 字段
  - `human-judgement` TR-13.5: 交叉引用链接指向正确章节
