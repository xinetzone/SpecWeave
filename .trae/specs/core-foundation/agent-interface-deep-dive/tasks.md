# Agent系统中Interface/API/ABI/Protocol深度解析 - The Implementation Plan

## [x] Task 1: 创建目标目录和00-overview.md总览
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建目录 docs/knowledge/learning/agent-interface-deep-dive/
  - 创建00-overview.md，包含：
    - YAML frontmatter（id: agent-interface-overview）
    - 引言：说明本教程与通用wiki的区别（Agent视角 vs 通用视角）
    - Agent技术栈四层抽象Mermaid图（Interface→API→ABI→Protocol）
    - 四个概念在Agent中的核心区别速览表（含Agent中对应物）
    - 与已有wiki的关系说明（链接到interface-api-abi-protocol-wiki和agent-communication-protocols）
    - 阅读路径指南
    - 双向导航：下一章01-agent-interface.md、对比章05-agent-comparison.md
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-7, AC-8, AC-10
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录存在，00-overview.md文件存在
  - `programmatic` TR-1.2: 文件行数<300
  - `human-judgement` TR-1.3: Mermaid四层抽象图语法正确，方向TD，节点有样式区分
  - `human-judgement` TR-1.4: 速览表包含"Agent中对应物"列（如MCP Tool Schema、JSON-RPC方法等）
  - `programmatic` TR-1.5: 导航链接文件名与后续规划一致（01-agent-interface.md, 05-agent-comparison.md）
- **Notes**: 参考已有00-overview.md结构，但内容完全聚焦Agent视角

## [x] Task 2: 创建01-agent-interface.md（Agent视角的Interface）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建01-agent-interface.md，包含：
    - YAML frontmatter（id: agent-interface-chapter）
    - 定义：Agent中的Interface是什么（能力契约而非OOP接口）
    - 核心特征：声明式能力、Schema驱动、语言无关、可发现性、组合性
    - Agent Interface具体形态：
      - MCP Tool定义（inputSchema/outputSchema）
      - Skill描述文件（SKILL.md能力声明）
      - Agent Card（A2A Agent Card的能力声明）
    - 代码案例1：TypeScript定义MCP Tool Interface（含JSON Schema）
    - 代码案例2：Python定义Tool函数+类型注解作为隐式Interface
    - 与通用Interface的区别（链接到已有wiki 01-interface.md）
    - 双向导航：上一章00-overview.md、下一章02-agent-api.md、对比章05-agent-comparison.md
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-10
- **Test Requirements**:
  - `programmatic` TR-2.1: 文件存在，行数<300
  - `programmatic` TR-2.2: 导航链接文件名正确
  - `human-judgement` TR-2.3: 至少2个Agent场景代码案例（MCP Tool Schema + Python Tool定义）
  - `human-judgement` TR-2.4: 代码块语言标注正确（typescript/python/json）
  - `human-judgement` TR-2.5: 明确区分Agent Interface与通用OOP Interface，链接到已有wiki
- **Notes**: Tool Interface的核心是JSON Schema而非语言级interface关键字

## [x] Task 3: 创建02-agent-api.md（Agent视角的API）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 创建02-agent-api.md，包含：
    - YAML frontmatter（id: agent-api-chapter）
    - 定义：Agent API是Interface的具体暴露方式（可调用的端点/方法）
    - 核心特征：请求响应模型、方法名标识、参数序列化、错误返回、版本管理
    - Agent API具体形态：
      - MCP JSON-RPC 2.0方法（tools/list, tools/call, resources/read, prompts/get）
      - ACP RESTful API设计
      - A2A Task API（tasks/send, tasks/get, tasks/cancel）
    - 代码案例1：JSON-RPC请求响应示例（tools/call请求和响应）
    - 代码案例2：curl/fetch调用MCP Server over HTTP示例
    - 与通用API的区别（链接到已有wiki 02-api.md）
    - 双向导航：上一章01-agent-interface.md、下一章03-agent-abi.md、对比章05-agent-comparison.md
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-10
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件存在，行数<300
  - `programmatic` TR-3.2: 导航链接文件名正确
  - `human-judgement` TR-3.3: 至少2个Agent API代码案例（JSON-RPC示例 + curl示例）
  - `human-judgement` TR-3.4: 代码块语言标注正确（json/bash）
  - `human-judgement` TR-3.5: 涵盖MCP/ACP/A2A三种Agent API形态
- **Notes**: JSON-RPC 2.0是Agent API的核心标准，需展示完整请求响应结构

## [x] Task 4: 创建03-agent-abi.md（Agent视角的ABI）
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 创建03-agent-abi.md，包含：
    - YAML frontmatter（id: agent-abi-chapter）
    - 定义：Agent ABI是跨运行时/跨语言的二进制兼容边界
    - 核心特征：序列化格式约定、传输层抽象、内存隔离、字节级兼容
    - Agent ABI具体形态：
      - 跨语言调用边界（Python Server ↔ Node.js Client）
      - JSON作为通用序列化格式（跨越语言ABI边界）
      - STDIO/HTTP/SSE作为传输抽象（绕过原生语言ABI）
      - MessagePack/Protobuf等二进制序列化
    - 为什么MCP不用原生语言绑定：直接用JSON+STDIO/HTTP消除ABI问题
    - 代码案例1：Python MCP Server + Node.js Client跨语言交互示意
    - 代码案例2：JSON序列化如何抹平Python dict与JS Object的差异
    - WebAssembly作为新兴Agent ABI边界
    - 与通用ABI的区别（链接到已有wiki 03-abi.md）
    - 双向导航：上一章02-agent-api.md、下一章04-agent-protocol.md、对比章05-agent-comparison.md
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-10
- **Test Requirements**:
  - `programmatic` TR-4.1: 文件存在，行数<300
  - `programmatic` TR-4.2: 导航链接文件名正确
  - `human-judgement` TR-4.3: 至少2个Agent ABI案例（跨语言交互 + JSON序列化）
  - `human-judgement` TR-4.4: 解释清楚"为什么Agent生态选择JSON+HTTP而非原生绑定"
  - `human-judgement` TR-4.5: 代码块语言标注正确（python/typescript/json）
- **Notes**: 这是四个概念中在Agent语境下最反直觉的一个——Agent生态通过标准化序列化+传输层"绕过"了传统ABI问题

## [x] Task 5: 创建04-agent-protocol.md（Agent视角的Protocol）
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 创建04-agent-protocol.md，包含：
    - YAML frontmatter（id: agent-protocol-chapter）
    - 定义：Agent Protocol是Agent间/Agent与系统间通信的完整规则集
    - 核心特征：分层设计、状态管理、流控、安全认证、能力协商
    - Agent Protocol具体形态：
      - MCP协议（JSON-RPC over STDIO/HTTP）：工具调用层
      - ACP协议（REST原生）：本地消息层
      - A2A协议（HTTP+SSE+JSON-RPC）：跨Agent协作层
      - ANP协议（DID+JSON-LD）：去中心化网络层
    - MCP/A2A消息格式规范
    - 传输层对比：STDIO vs HTTP vs SSE
    - 代码案例1：MCP initialize握手消息序列
    - 代码案例2：A2A Task委派消息流程（Mermaid序列图）
    - 与通用Protocol的区别（链接到已有wiki 04-protocol.md）
    - 双向导航：上一章03-agent-abi.md、下一章05-agent-comparison.md、总览00-overview.md
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-7, AC-10
- **Test Requirements**:
  - `programmatic` TR-5.1: 文件存在，行数<300
  - `programmatic` TR-5.2: 导航链接文件名正确
  - `human-judgement` TR-5.3: 至少2个案例（消息序列示例 + Mermaid序列图）
  - `human-judgement` TR-5.4: Mermaid序列图语法正确
  - `human-judgement` TR-5.5: 涵盖四层协议（MCP/ACP/A2A/ANP）定位
- **Notes**: 链接到agent-communication-protocols/获取更详细协议信息，本章聚焦Protocol与Interface/API/ABI的关系

## [x] Task 6: 创建05-agent-comparison.md（核心对比分析章）
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 创建05-agent-comparison.md（核心章节），包含：
    - YAML frontmatter（id: agent-comparison-chapter）
    - Agent语境下四概念9维度对比表（维度：抽象层级、Agent中作用、数据格式、调用机制、错误处理、典型协议/标准、变更影响、调试工具、违反后果）
    - 四层抽象在Agent调用链中的协同工作（从Tool定义到消息传输的完整链路）
    - Agent调用全链路Mermaid图：用户请求→LLM决定调用Tool→Tool Interface匹配→API方法调用→跨ABI序列化→Protocol传输→远端执行→结果返回
    - ≥6个Agent特有FAQ：
      1. MCP Tool定义是Interface还是API？
      2. JSON-RPC是API还是Protocol？
      3. Agent需要关心ABI吗？
      4. A2A和MCP是什么关系？
      5. 为什么MCP用JSON不用Protobuf？
      6. 开发Agent工具时应该先定义Interface还是先设计API？
    - Agent技术选型决策指南（决策树/表格）：
      - 定义Tool能力 → Interface
      - 暴露可调用方法 → API
      - 跨语言交互 → ABI（选择JSON/MessagePack）
      - 与外部Agent通信 → Protocol（选择MCP/A2A/ANP）
    - 双向导航：上一章04-agent-protocol.md、下一章06-agent-resources.md、总览00-overview.md
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-6, AC-7, AC-10
- **Test Requirements**:
  - `programmatic` TR-6.1: 文件存在，行数<300
  - `programmatic` TR-6.2: 导航链接文件名正确（特别注意06-agent-resources.md不是06-summary.md）
  - `human-judgement` TR-6.3: 9维度对比表完整，每个维度有Agent语境下的具体值
  - `human-judgement` TR-6.4: Agent调用全链路Mermaid图语法正确
  - `human-judgement` TR-6.5: ≥6个FAQ，全部是Agent特有问题
  - `human-judgement` TR-6.6: 决策指南可操作（明确的if-then指引）
- **Notes**: 本章是核心价值章节，需特别关注文件名一致性（06-agent-resources.md）

## [x] Task 7: 创建06-agent-resources.md（参考资料章）
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 
  - 创建06-agent-resources.md，包含：
    - YAML frontmatter（id: agent-resources-chapter）
    - Agent术语表（≥15个术语）：Tool/Skill/MCP Server/MCP Client/JSON-RPC/Agent Card/Task/SSE/STDIO Transport/Tool Schema/Agent Runtime/Tool Call/Function Calling/ACP/A2A/ANP等
    - 协议规范参考链接（分类列出）：
      - MCP官方规范链接
      - A2A官方文档链接
      - ACP GitHub链接
      - JSON-RPC 2.0规范链接
      - JSON Schema规范链接
    - 进阶阅读路径：
      - 路径1：Tool开发者路线（Interface→JSON Schema→MCP Server开发）
      - 路径2：协议设计者路线（API→JSON-RPC→协议分层→A2A）
      - 路径3：跨语言Agent路线（ABI→序列化→WASM→多语言Runtime）
    - 相关wiki链接：interface-api-abi-protocol-wiki、agent-communication-protocols、agent-skills-wiki
    - 双向导航：上一章05-agent-comparison.md、总览00-overview.md
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5, AC-8, AC-10
- **Test Requirements**:
  - `programmatic` TR-7.1: 文件存在，行数<300
  - `programmatic` TR-7.2: 导航链接文件名正确
  - `human-judgement` TR-7.3: 术语表≥15个Agent相关术语
  - `human-judgement` TR-7.4: 参考链接分类清晰，覆盖MCP/A2A/ACP核心规范
  - `human-judgement` TR-7.5: 3条进阶阅读路径有明确的学习阶段指引
- **Notes**: 外部链接使用官方URL；本地链接使用相对路径

## [x] Task 8: 全量验证与知识库索引更新
- **Priority**: high
- **Depends On**: Task 7
- **Description**: 
  - 执行全量验证：
    1. 运行check-file-size.py确认所有7个文件<300行
    2. 运行check-links.py确认所有本地链接有效
    3. 逐章核对导航文件名一致性（重点检查05→06链接）
    4. 确认每个frontmatter字段完整
  - 运行generate_index.py更新知识库索引
  - 更新tasks.md标记所有任务完成
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-8.1: check-file-size.py通过，所有文件<300行
  - `programmatic` TR-8.2: check-links.py通过，所有本地链接有效（0个断链）
  - `programmatic` TR-8.3: generate_index.py成功，新目录被收录
  - `human-judgement` TR-8.4: 人工快速扫描每个文件frontmatter确认字段完整
- **Notes**: 如果发现链接错误或文件超标，立即修正后重新验证
