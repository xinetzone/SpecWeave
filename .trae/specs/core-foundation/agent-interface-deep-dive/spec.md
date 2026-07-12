# Agent系统中Interface/API/ABI/Protocol深度解析 - Product Requirement Document

## Overview
- **Summary**: 创建一份从AI Agent技术实现与交互视角出发的深度技术文档，系统分析Interface、API、ABI、Protocol四个核心概念在Agent系统中的具体作用、实现方式、数据格式规范、调用机制，以及它们如何协同支持Agent与外部系统或其他Agent之间的通信与交互。文档采用原子化多文件结构（7个文件），遵循"概念对比中心教程结构"模式，将对比分析作为核心价值章节。
- **Purpose**: 已有的interface-api-abi-protocol-wiki从通用软件开发角度讲解了四个概念的基础定义，但缺乏Agent系统视角下的具体实现细节。随着MCP/ACP/A2A/ANP等Agent通信协议生态的快速发展，开发者需要理解这四个基础概念如何映射到Agent系统的各个技术层面：从Agent内部的Tool接口定义（Interface）、到MCP Server的API暴露（API）、到不同语言运行时的二进制兼容性（ABI）、再到Agent间通信的协议规范（Protocol）。本教程填补这一认知空白。
- **Target Users**: 
  - Agent框架开发者（MCP Server/Client、Agent Runtime开发）
  - 多Agent系统架构师（设计跨Agent协作方案）
  - 工具/技能开发者（为Agent开发可复用工具）
  - 对Agent互操作性感兴趣的中高级开发者

## Goals
- 从Agent系统视角重新定义四个概念，明确它们在Agent技术栈中的具体位置
- 详细说明每个概念在Agent中的实现方式：Tool Interface定义模式、MCP/ACP API设计、Python/Node.js ABI注意事项、MCP/A2A协议规范
- 提供真实Agent场景的代码案例：MCP Tool定义、JSON-RPC调用、跨语言Tool Server、Agent间消息协议
- 系统对比四个概念在Agent语境下的区别与联系，包含分层协作模型图
- 提供Agent通信选型决策指南：何时定义Interface、何时设计API、何时关注ABI、何时选择Protocol
- 建立Agent技术栈的四层抽象模型：Agent Interface → Agent API → Agent ABI → Agent Protocol

## Non-Goals (Out of Scope)
- 不重复已有通用wiki中的基础定义（如Interface在OOP中的含义、OSI七层模型详解），但会提供链接指向已有wiki
- 不做MCP/ACP/A2A/ANP四个协议的完整教程（已有agent-communication-protocols/目录覆盖）
- 不提供从零构建Agent框架的完整教程
- 不深入密码学/网络安全细节（如TLS握手过程、DID具体实现）
- 不涉及特定Agent框架（LangChain/AutoGen/CrewAI）的API使用教程

## Background & Context
- **前置资产**：
  - 已有通用wiki：[interface-api-abi-protocol-wiki/](../../../../docs/knowledge/learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/)（基础定义参考）
  - 已有Agent协议wiki：[agent-communication-protocols/](../../../../docs/knowledge/learning/01-agent-protocols-interfaces/agent-communication-protocols/)（MCP/ACP/A2A/ANP详解）
  - 已沉淀模式：concept-comparison-tutorial-structure（本教程遵循此模式）
- **技术生态背景**：
  - MCP（Model Context Protocol）使用JSON-RPC 2.0作为API调用协议
  - MCP Tool定义本质是Interface契约
  - Python MCP Server与Node.js Client交互时存在ABI边界
  - A2A协议基于HTTP+SSE实现Agent间通信
- **文档规范**：
  - 遵循原子化原则：每文件<300行
  - 使用统一YAML frontmatter（id/title/category/tags/date/status/author/summary）
  - 双向导航链接
  - Mermaid图使用```mermaid标记

## Functional Requirements
- **FR-1**: 创建00-overview.md，包含Agent技术栈四层抽象Mermaid图、四个概念在Agent中的速览表、与已有wiki的关系说明、阅读路径
- **FR-2**: 创建01-agent-interface.md，从Agent视角讲解Interface：Tool/Skill Interface定义、能力声明模式、输入输出Schema（JSON Schema）、TypeScript/Python Interface定义代码案例、MCP Tool Interface的具体实现
- **FR-3**: 创建02-agent-api.md，从Agent视角讲解API：MCP API方法（tools/list, tools/call等）、JSON-RPC 2.0作为Agent API标准、ACP RESTful API、Tool API的请求响应模型、curl/fetch调用MCP Server的代码案例
- **FR-4**: 创建03-agent-abi.md，从Agent视角讲解ABI：跨语言MCP Server/Client交互的二进制边界、Python/Node.js/Go运行时的序列化兼容性、JSON作为跨ABI通用格式、为什么MCP用STDIO/HTTP而非原生语言绑定、ctypes/WebAssembly边界案例
- **FR-5**: 创建04-agent-protocol.md，从Agent视角讲解Protocol：MCP/ACP/A2A/ANP的协议分层、JSON-RPC消息格式规范、传输层（STDIO/HTTP/SSE）对比、Agent发现/能力协商/任务委派的协议机制、消息序列图案例
- **FR-6**: 创建05-agent-comparison.md（核心章节）：Agent语境下的四概念9维度对比表、四层抽象如何在Agent调用链中协同工作、MCP调用全链路Mermaid图、≥6个Agent特有FAQ、Agent技术选型决策指南（何时定义Tool Interface vs 暴露MCP API vs 选择Protocol）
- **FR-7**: 创建06-agent-resources.md：Agent术语表（≥15个术语）、Agent协议规范参考链接（MCP/ACP/A2A官方文档）、进阶阅读路径（从Tool开发到协议设计的学习路线）

## Non-Functional Requirements
- **NFR-1**: 每个文件严格<300行（含frontmatter），违反需拆分
- **NFR-2**: 每个概念章节至少包含2个Agent场景代码案例（如MCP Tool定义、JSON-RPC请求示例等）
- **NFR-3**: 所有Mermaid图语法正确可渲染
- **NFR-4**: 所有本地链接使用相对路径，不使用绝对路径
- **NFR-5**: 代码块使用正确语言标注（typescript/python/json/bash/mermaid等）
- **NFR-6**: 双向导航完整：每章包含上一章/下一章/总览/对比分析的导航链接
- **NFR-7**: frontmatter必填字段完整（id/title/x-toml-ref/source/category/tags/date/status/author/summary）

## Constraints
- **Technical**: Markdown格式，Mermaid图表，无外部依赖；代码案例使用TypeScript/Python/JSON（MCP生态主流语言）
- **Business**: 本次会话内完成，不跨会话
- **Dependencies**: 参考已有wiki内容但不复制，保持独立性；链接到已有wiki而非重复基础概念

## Assumptions
- 读者已具备基本的Agent概念（知道什么是LLM Agent、Tool Use）
- 读者已了解基础编程概念（函数、接口、HTTP），不需要从零解释
- 读者可能不熟悉MCP/ACP/A2A具体细节，教程会在涉及处简要说明
- 文档存放路径：docs/knowledge/learning/agent-interface-deep-dive/

## Acceptance Criteria

### AC-1: 文档结构完整性
- **Given**: 教程创建完成
- **When**: 检查目标目录
- **Then**: 存在7个.md文件（00-overview到06-resources），每个文件包含完整frontmatter
- **Verification**: `programmatic`
- **Notes**: 运行LS确认文件数量，读取每个文件frontmatter确认字段完整

### AC-2: 原子化合规
- **Given**: 7个文件全部创建
- **When**: 运行check-file-size.py检查
- **Then**: 所有文件行数<300
- **Verification**: `programmatic`

### AC-3: 链接有效性
- **Given**: 文档创建完成且导航链接已添加
- **When**: 运行check-links.py检查
- **Then**: 所有本地链接（含双向导航、wiki引用）均有效
- **Verification**: `programmatic`

### AC-4: Agent视角独特性
- **Given**: 阅读01-04章内容
- **When**: 人工审查
- **Then**: 每个概念章节明确聚焦Agent场景，包含Agent特定技术内容（Tool Interface、MCP API、跨语言序列化、Agent Protocol），而非重复通用编程概念
- **Verification**: `human-judgment`
- **Notes**: 审查要点：是否有MCP/JSON-RPC/Tool Schema等Agent特有内容

### AC-5: 代码案例充分性
- **Given**: 01-04概念章节
- **When**: 统计代码案例
- **Then**: 每章至少包含2个Agent场景代码示例（如Tool Schema定义、JSON-RPC请求、MCP调用等）
- **Verification**: `human-judgment`

### AC-6: 对比分析核心价值
- **Given**: 05-agent-comparison.md创建完成
- **When**: 人工审查
- **Then**: 包含Agent语境9维度对比表、四层调用链路Mermaid图、≥6个FAQ、决策指南
- **Verification**: `human-judgment`

### AC-7: Mermaid图可渲染
- **Given**: 文档中所有Mermaid代码块
- **When**: 逐块检查语法
- **Then**: 所有Mermaid图语法正确，包含方向声明（TD/LR）和节点样式
- **Verification**: `human-judgment`

### AC-8: 与已有资产正确关联
- **Given**: 文档中引用已有wiki的链接
- **When**: 人工审查
- **Then**: 对已有通用wiki和Agent协议wiki的引用链接正确，基础概念提供跳转而非重复解释
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: check-links验证链接可达，人工审查引用合理性

### AC-9: 知识库索引入库
- **Given**: 全部文件创建并通过验证
- **When**: 运行generate_index.py
- **Then**: 新文档目录成功纳入知识库索引
- **Verification**: `programmatic`

### AC-10: 导航一致性
- **Given**: 所有章节的双向导航链接
- **When**: 逐章检查导航文件名
- **Then**: 所有导航链接中的文件名与实际文件名完全一致，无05-practice vs 05-comparison类偏差
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要增加"Agent调用全链路追踪"作为独立子章节放入05-comparison？（建议放入对比章作为协同案例）
- [ ] 代码案例是否需要包含Go语言MCP Server示例？（建议仅用TypeScript+Python保持简洁，Go可在参考资料中提及）
