---
version: "1.0"
---
# 技术接口概念Wiki教程 - The Implementation Plan

## [x] Task 1: 创建教程目录与总览文档（00-overview.md）
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建目录 `docs/knowledge/learning/interface-api-abi-protocol-wiki/`
  - 编写00-overview.md，包含：教程引言、四个概念层次概览（Mermaid图）、阅读路径指南、目标读者说明
  - 添加正确的YAML frontmatter
  - 设置后续章节导航链接
- **Acceptance Criteria Addressed**: AC-1, AC-7, AC-9
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录存在，00-overview.md文件存在 ✅
  - `human-judgement` TR-1.2: 包含概念层次Mermaid图，阅读路径清晰 ✅
  - `programmatic` TR-1.3: frontmatter字段完整（id/title/category/tags/date/status/author/summary） ✅
- **Notes**: 参考agent-skills-wiki/00-overview.md的结构风格
- **Completion**: 69行，包含四层抽象Mermaid层次图、核心区别速览表、完整章节目录

## [x] Task 2: 编写接口（Interface）章节（01-interface.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 软件工程通用概念定义 + OOP特定含义
  - 至少5个核心特征：抽象性、规范性、多态支持、可实现性、契约性、解耦性
  - OOP接口（TypeScript/Java/Go示例）与函数式编程接口（TypeScript类型别名/Python Protocol）场景
  - 至少2个代码案例：(1) 支付网关接口OOP示例；(2) 函数式回调接口示例
  - 添加双向导航（上一章→00-overview，下一章→02-api）
- **Acceptance Criteria Addressed**: AC-2, AC-7, AC-9
- **Test Requirements**:
  - `human-judgement` TR-2.1: 定义清晰，区分通用概念与OOP特定含义 ✅
  - `human-judgement` TR-2.2: 至少列出5个核心特征并解释 ✅（6个特征）
  - `human-judgement` TR-2.3: 包含OOP和函数式编程两种范式场景说明 ✅
  - `human-judgement` TR-2.4: 至少2个可运行/说明性代码案例 ✅
  - `programmatic` TR-2.5: 双向导航链接正确，frontmatter完整 ✅
- **Completion**: 164行，6个核心特征，2个TypeScript代码案例（支付网关多态+函数式策略模式）

## [x] Task 3: 编写API章节（02-api.md）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - API精确定义，区分与Interface的层次关系
  - 主要API类型：REST（HTTP/JSON）、GraphQL（查询语言）、SOAP（XML/WS-*）、gRPC（Protobuf/HTTP2）
  - 核心特征：调用方式（同步/异步）、数据格式（JSON/XML/Protobuf）、协议支持（HTTP/TCP）、版本控制、认证授权
  - 应用场景：系统集成、服务调用、第三方开发、微服务通信
  - 至少3个主流API案例：(1) GitHub REST API；(2) Stripe支付API；(3) GraphQL GitHub API示例
  - 代码示例：curl请求、JavaScript fetch调用
  - 添加双向导航（上一章→01-interface，下一章→03-abi）
- **Acceptance Criteria Addressed**: AC-3, AC-7, AC-9
- **Test Requirements**:
  - `human-judgement` TR-3.1: 精确定义API，明确与Interface的层次区别 ✅
  - `human-judgement` TR-3.2: 详述REST/GraphQL/SOAP/gRPC四种类型特点 ✅（共5种含库API）
  - `human-judgement` TR-3.3: 核心特征覆盖调用方式/数据格式/协议/版本控制 ✅
  - `human-judgement` TR-3.4: 至少3个主流API实际案例 ✅
  - `programmatic` TR-3.5: 双向导航链接正确，frontmatter完整 ✅
- **Completion**: 144行，5种API类型对比表，3个主流案例，含curl/fetch/GraphQL代码示例

## [x] Task 4: 编写ABI章节（03-abi.md）
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - ABI技术内涵定义，与API的本质区别（源码兼容vs二进制兼容）
  - 核心技术特征：数据类型表示（大小/对齐/字节序）、函数调用约定（cdecl/stdcall/fastcall/寄存器使用）、内存布局（结构体偏移/虚表）、符号命名修饰（name mangling）、系统调用号
  - 应用场景：编译器开发、跨语言调用（FFI）、操作系统系统调用接口、动态链接库（DLL/.so）、插件系统
  - 至少1个底层系统案例：(1) C语言调用约定x86示例（用代码注释说明栈布局）；或(2) Python ctypes调用C共享库示例
  - 添加双向导航（上一章→02-api，下一章→04-protocol）
- **Acceptance Criteria Addressed**: AC-4, AC-7, AC-9
- **Test Requirements**:
  - `human-judgement` TR-4.1: 清晰说明ABI与API的本质区别 ✅
  - `human-judgement` TR-4.2: 至少列出3个核心技术特征并解释 ✅（5个特征）
  - `human-judgement` TR-4.3: 覆盖编译器/跨语言调用/OS接口场景 ✅
  - `human-judgement` TR-4.4: 至少1个底层系统案例 ✅（Python ctypes调用C库）
  - `programmatic` TR-4.5: 双向导航链接正确，frontmatter完整 ✅
- **Completion**: 132行，API vs ABI对比表，5个核心技术特征，Python ctypes实战案例

## [x] Task 5: 编写协议（Protocol）章节（04-protocol.md）
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 网络协议与软件协议的综合定义，协议vs接口的关系
  - 核心特征：规则性（语法/语义/时序）、层次性（分层架构）、交互性（请求-响应/发布-订阅）、标准化、可扩展性
  - 网络通信协议：OSI七层模型/TCP-IP四层模型简述
  - 至少3种主流网络协议对比：HTTP/HTTPS（应用层）、TCP（传输层）、WebSocket（全双工）（可选：MQTT、gRPC协议）
  - 软件协议场景：进程间通信（IPC）、数据库协议（MySQL wire protocol）、消息队列协议（AMQP）
  - 添加双向导航（上一章→03-abi，下一章→05-comparison）
- **Acceptance Criteria Addressed**: AC-5, AC-7, AC-9
- **Test Requirements**:
  - `human-judgement` TR-5.1: 给出网络与软件协议的综合定义 ✅
  - `human-judgement` TR-5.2: 至少列出3个核心特征 ✅（5个特征）
  - `human-judgement` TR-5.3: 对比至少3种主流网络协议特点与场景 ✅（5种协议对比表）
  - `human-judgement` TR-5.4: 覆盖网络通信/数据交换/系统协作场景 ✅
  - `programmatic` TR-5.5: 双向导航链接正确，frontmatter完整 ✅
- **Completion**: 115行，协议三要素详解，OSI/TCP-IP分层模型，5种主流协议对比表

## [x] Task 6: 编写对比分析章节（05-comparison.md）
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 制作四维度对比表格：定义、抽象层次、应用范围、实现方式、关注问题、典型使用者、变化影响范围
  - 概念关联分析：
    - API与协议的关系：API常基于协议实现
    - 接口与ABI的联系：源码级接口→编译后ABI
    - 从抽象到具体的层次链：Interface → API → ABI → Protocol
  - 软件系统架构中的定位总结（Mermaid层次图，展示从高级语言到底层网络的抽象栈）
  - 常见混淆点澄清：如"HTTP是API还是协议？"
  - 决策指南：何时需要定义哪个层次的接口
  - 添加双向导航（上一章→04-protocol，下一章→06-resources）
- **Acceptance Criteria Addressed**: AC-6, AC-7, AC-9
- **Test Requirements**:
  - `human-judgement` TR-6.1: 对比表格维度完整，四概念区分清晰 ✅（9维度对比表）
  - `human-judgement` TR-6.2: 关联关系分析准确，层次链逻辑清晰 ✅（5组关系）
  - `human-judgement` TR-6.3: Mermaid架构层次图正确 ✅
  - `human-judgement` TR-6.4: 包含常见混淆点澄清与决策指南 ✅（5个FAQ + 决策表）
  - `programmatic` TR-6.5: 双向导航链接正确，frontmatter完整 ✅
- **Completion**: 139行，9维度对比表，5组关联关系，Mermaid抽象栈图，5个FAQ，分场景决策指南

## [x] Task 7: 编写参考资料章节（06-resources.md）
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 
  - 术语表（Glossary）：整理文中出现的专业术语
  - 参考资料：权威书籍、RFC文档、编程语言规范、官方文档链接
  - 扩展阅读建议：按进阶方向分类（编程语言理论→系统编程→网络编程→API设计）
  - 添加双向导航（上一章→05-comparison，返回目录→00-overview，无下一章标记）
- **Acceptance Criteria Addressed**: AC-10, AC-7, AC-9
- **Test Requirements**:
  - `human-judgement` TR-7.1: 术语表覆盖主要专业术语 ✅（17个术语）
  - `human-judgement` TR-7.2: 参考资料来源权威，分类清晰 ✅（书籍/RFC/语言规范三分类）
  - `human-judgement` TR-7.3: 扩展阅读有明确进阶路径指引 ✅（4个进阶方向）
  - `programmatic` TR-7.4: 导航链接正确，frontmatter完整 ✅
- **Completion**: 107行，17个术语术语表，三分类权威参考资料，4方向扩展阅读建议

## [x] Task 8: 质量验证与收尾
- **Priority**: high
- **Depends On**: Task 7
- **Description**: 
  - 补全所有文档的YAML frontmatter（统一date为2026-07-03，author为"SpecWeave"，status为"stable"，category为"learning"）
  - 运行文件大小检查：确保每个文件<300行
  - 运行链接检查：验证所有内部相对路径有效，无file:///绝对路径
  - 更新docs/knowledge/README.md的学习目录索引（如有必要）
- **Acceptance Criteria Addressed**: AC-1, AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-8.1: 运行 `python .agents/scripts/check-file-size.py --path docs/knowledge/learning/interface-api-abi-protocol-wiki/` 全部通过 ✅
  - `programmatic` TR-8.2: 运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning/interface-api-abi-protocol-wiki/` 全部通过 ✅（20个本地链接100%有效）
  - `programmatic` TR-8.3: 所有7个文件frontmatter字段完整且正确 ✅
  - `human-judgement` TR-8.4: 人工通读检查技术准确性与可读性 ✅
- **Completion**: 
  - 7个文件共870行，每文件均<200行（最大164行）
  - 20个本地链接全部有效
  - 所有frontmatter字段完整，source/category统一正确
