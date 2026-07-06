# 项目知识库

## 统计摘要

- **总条目数**：333

| 分类 | 数量 |
|------|------|
| architecture | 1 |
| best-practices | 4 |
| decisions | 1 |
| docs | 8 |
| knowledge | 13 |
| learning | 108 |
| operations | 8 |
| research | 1 |
| standards | 1 |
| troubleshooting | 3 |
| unknown | 185 |

## 按类别浏览

### architecture

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md) | SpecWeave项目治理方法论体系的架构总览文档，定义了治理基建四层递进核心模型，以及围绕该模型形成的5个可复用元洞察模式，包含模式间关系、落地状态和自反性验证案例。 | 2026-06-30 | governance、architecture、methodology、stage-guardrails、patterns、four-layer-model、governance-loop、retrospective、meta-insights |

### best-practices

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Mermaid 图表操作指南](best-practices/mermaid-guide.md) | SpecWeave 项目中 Mermaid 图表的一站式操作手册，涵盖起步模板、安全编码六规则、自动化检查工具详解、渲染问题排查流程和不同图表类型注意事项。 | 2026-06-29 | mermaid、图表、可视化、check-mermaid、安全编码、六规则、模板、ci |
| [多文件编辑操作可靠性指南](best-practices/multi-file-edit-reliability.md) | 基于IDL Wiki章节拆分实战复盘的多文件编辑操作可靠性指南：涵盖章节拆分级联编号成本、Edit工具精确匹配陷阱、串行vs并行Edit策略、Windows管道稳定性四条核心经验，提供决策矩阵和操作Checklist。 | 2026-07-05 | edit、multi-file、reliability、serial-vs-parallel、windows-pipe、cascading-renumber、wiki-split、tool-pitfalls |
| [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md) | 基于MDI项目parser.py（1465行）重构复盘的经验总结：处理半结构化数据（Markdown/自然语言/配置文件）的Parser应预留2-3倍于Generator的时间/代码量预算，遵循三层架构拆分，并先写20+边界case测试。 | 2026-07-03 | parser、复杂度预算、semi-structured-parsing、三层架构、边界case、TDD、checklist |
| [方法论模式第3次验证报告：模板批量升级场景](best-practices/pattern-validation-v3-template-batch-upgrade.md) | 分类处置决策树(Classification-Disposition Decision Tree)与三阶段渐进推广验证(Phased Rollout Validation)两个L2治理模式的第3次验证报告。验证场景为复盘模板v1.2批量标准化升级（61个项目），验证了模式在轻量级模板升级场景下的有效性，记录了P1批量执行后集中格式校验的新增实践。 | 2026-07-06 | pattern-validation、L2-pattern、phased-rollout、classification-disposition、batch-upgrade、governance、methodology-evolution |

### decisions

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md) | 记录将第三方依赖目录从 libs/ 重命名为 vendor/ 的架构决策及其理由 | 2026-06-23 | architecture、naming、directory、vendor、convention |

### docs

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [MDI研究报告 - 执行摘要](mdi-research/00-executive-summary.md) |  | 2026-07-02 | - |
| [MDI研究报告 - 可行性分析](mdi-research/01-feasibility-analysis.md) |  | 2026-07-02 | - |
| [MDI研究报告 - 生态对比分析](mdi-research/02-ecosystem-comparison.md) |  | 2026-07-02 | - |
| [MDI研究报告 - 技术架构深度解析](mdi-research/03-technical-architecture.md) |  | 2026-07-02 | - |
| [MDI研究报告 - 工具链使用指南](mdi-research/04-toolchain-guide.md) |  | 2026-07-02 | - |
| [MDI研究报告 - 版本控制与变更管理最佳实践](mdi-research/05-versioning-best-practices.md) |  | 2026-07-02 | - |
| [MDI研究报告 - 未来演进方向](mdi-research/06-future-evolution.md) |  | 2026-07-02 | - |
| [MDI研究报告 - 结论](mdi-research/07-conclusion.md) |  | 2026-07-02 | - |

### knowledge

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [00、总览：MyST Markdown 统一化接口生态体系](myst-unified-ecosystem/00-overview.md) |  |  | - |
| [01、IDL：接口描述语言](myst-unified-ecosystem/01-idl.md) |  |  | - |
| [02、Interface：行为契约](myst-unified-ecosystem/02-interface.md) |  |  | - |
| [03、API：应用程序编程接口](myst-unified-ecosystem/03-api.md) |  |  | - |
| [04、ABI：应用程序二进制接口](myst-unified-ecosystem/04-abi.md) |  |  | - |
| [05、Protocol：通信协议](myst-unified-ecosystem/05-protocol.md) |  |  | - |
| [06、Implementation：具体实现](myst-unified-ecosystem/06-implementation.md) |  |  | - |
| [07、MCP：Model Context Protocol](myst-unified-ecosystem/07-mcp.md) |  |  | - |
| [08、ACP：Agent Communication Protocol](myst-unified-ecosystem/08-acp.md) |  |  | - |
| [09、A2A：Agent-to-Agent](myst-unified-ecosystem/09-a2a.md) |  |  | - |
| [10、ANP：Agent Network Protocol](myst-unified-ecosystem/10-anp.md) |  |  | - |
| [11、MDI：Markdown Document Interface](myst-unified-ecosystem/11-mdi.md) |  |  | - |
| [12、关系全景：11个概念的形式化关系与交互](myst-unified-ecosystem/12-relationships.md) |  |  | - |

### learning

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Learning Wiki 主题分类体系](learning/CATEGORIES.md) | Learning Wiki 知识库的8主题分类体系设计，包含分类原则、主题关系图、学习路径与各主题完整Wiki清单 | 2026-07-05 | categories、learning-wiki、knowledge-architecture、topic-classification、learning-path |
| [Learning Wiki 学习路径推荐表](learning/LEARNING-PATHS.md) | Learning Wiki知识库59个Wiki的系统化学习路径推荐，包含8主题内部学习顺序、前置依赖、关联知识点、角色定制路径 | 2026-07-05 | learning-path、study-guide、prerequisites、knowledge-graph、curriculum |
| [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/01-agent-protocols-interfaces/agent-communication-protocols-wiki.md) | 系统讲解Agent通信四大协议：MCP（Anthropic 2024，工具层）、ACP（IBM/BeeAI 2025，本地Agent协作）、A2A（Google 2025，跨厂商Agent协作）、ANP（去中心化网络层）。包含协议分层架构、N×M集成问题分析、各协议技术规范对比、代码示例与快速参考。本文档已原子化，详细内容见 agent-communication-protocols/ 子目录。 | 2026-07-03 | agent-protocols、mcp、acp、a2a、anp、multi-agent、communication、open-standard、linux-foundation、interoperability |
| [Agent Skills 开放标准完整指南](learning/01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md) | 基于 agentskills.io 官方完整教程（快速入门/最佳实践/描述优化/质量评估/脚本使用/客户端实现）和 external/agentskills 源码深度核实的 Agent Skills 开放标准完整指南。覆盖目录结构、SKILL.md格式规范、渐进式披露机制、自包含脚本设计、触发准确率优化、评估驱动迭代、skills-ref验证工具使用、客户端5步集成指南，以及与本项目现有Skill体系的对比分析。本文档已原子化，详细内容见 agent-skills-wiki/ 子目录。 | 2026-07-02 | agent-skills、skills、open-standard、specification、ai-agent、skill-development、progressive-disclosure、skills-ref、client-implementation、skill-evals |
| [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/00-overview.md) | 从AI Agent技术实现视角出发的Interface/API/ABI/Protocol四层抽象总览，聚焦MCP/ACP/A2A/ANP生态中的具体体现 | 2026-07-03 | agent、mcp、interface、api、abi、protocol、a2a |
| [Agent Interface：能力契约层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/01-agent-interface.md) | Agent视角的Interface：能力契约，JSON Schema驱动的Tool/Skill/Agent声明模式 | 2026-07-03 | agent、interface、mcp、tool、json-schema、skill |
| [Agent API：可调用方法层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/02-agent-api.md) | Agent视角的API：JSON-RPC 2.0作为Agent API标准，MCP/ACP/A2A的API设计与调用案例 | 2026-07-03 | agent、api、json-rpc、mcp、a2a、rest |
| [Agent ABI：跨语言边界层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/03-agent-abi.md) | Agent视角的ABI：JSON+STDIO/HTTP如何绕过传统二进制兼容问题，实现跨语言Agent互操作 | 2026-07-03 | agent、abi、json、serialization、cross-language、stdio、http |
| [Agent Protocol：通信规则层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/04-agent-protocol.md) | Agent视角的Protocol：MCP/ACP/A2A/ANP四层协议定位、消息流程、握手机制与协作模式 | 2026-07-03 | agent、protocol、mcp、a2a、acp、anp、json-rpc |
| [对比分析：Agent四层技术栈协同](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/05-agent-comparison.md) | Agent语境下Interface/API/ABI/Protocol九维度系统对比、全链路调用图、FAQ与技术选型决策指南 | 2026-07-03 | agent、comparison、architecture、mcp、decision-guide |
| [参考资料与学习路径](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/06-agent-resources.md) | Agent术语表、官方规范参考链接、三条进阶学习路径（Tool开发者/协议设计者/跨语言Runtime） | 2026-07-03 | agent、resources、reference、glossary、learning-path |
| [FFI（外部函数接口）教程总览](learning/01-agent-protocols-interfaces/ffi-wiki/00-overview.md) | FFI（Foreign Function Interface，外部函数接口）系统性技术教程总览，涵盖定义、工作原理、语言实现、应用案例、优劣分析、概念对比与参考资料。 | 2026-07-04 | ffi、foreign-function-interface、overview、tutorial |
| [FFI 定义与核心概念](learning/01-agent-protocols-interfaces/ffi-wiki/01-what-is-ffi.md) | FFI（Foreign Function Interface）的定义、核心概念、发展历史、与 ABI/API 的关系辨析，以及 FFI 解决的核心问题。 | 2026-07-04 | ffi、foreign-function-interface、definition、core-concepts |
| [FFI 工作原理](learning/01-agent-protocols-interfaces/ffi-wiki/02-working-principles.md) | FFI 的底层工作原理：调用约定、名称修饰、数据封送、内存管理、绑定生成机制的详细讲解。 | 2026-07-04 | ffi、calling-convention、name-mangling、marshalling、memory-management、binding |
| [不同编程语言中的 FFI 实现](learning/01-agent-protocols-interfaces/ffi-wiki/03-language-implementations.md) | Python、Java、Go、Rust、Node.js、C# 六种主流编程语言中的 FFI 实现方式、核心 API 与代码示例。 | 2026-07-04 | ffi、python、java、go、rust、nodejs、csharp、language-implementations |
| [实际应用案例与代码示例](learning/01-agent-protocols-interfaces/ffi-wiki/04-use-cases.md) | FFI 实际应用案例：Python 调用 C 实现矩阵运算加速、Rust 集成 C 图形库、Go 通过 cgo 调用 C 压缩库，以及 FFI 最佳实践清单。 | 2026-07-04 | ffi、use-cases、code-examples、best-practices |
| [FFI 的优势与局限性](learning/01-agent-protocols-interfaces/ffi-wiki/05-advantages-limitations.md) | FFI 的优势、局限性、性能开销分析与安全性考量，帮助读者全面评估 FFI 的适用性。 | 2026-07-04 | ffi、advantages、limitations、performance、security |
| [FFI 与相关概念对比](learning/01-agent-protocols-interfaces/ffi-wiki/06-comparison.md) | FFI 与 ABI、API、RPC、IPC、IDL 的多维度对比分析，含选型决策树与常见混淆点澄清。 | 2026-07-04 | ffi、comparison、abi、api、rpc、ipc、idl |
| [术语表与参考资料](learning/01-agent-protocols-interfaces/ffi-wiki/07-resources.md) | FFI 相关术语表（≥15条）、权威参考资料、分难度扩展阅读建议与项目内相关 wiki 交叉引用。 | 2026-07-04 | ffi、glossary、references、further-reading |
| [IDL（接口定义语言）Wiki 教程 - 总览](learning/01-agent-protocols-interfaces/idl-wiki/00-overview.md) | IDL（接口定义语言）Wiki 教程总览，介绍 IDL 在接口技术栈中的定位、9 章导航与阅读路径 | 2026-07-04 | idl、interface-definition-language、overview、tutorial、protobuf、thrift、corba |
| [一、IDL 定义与作用：接口契约的语言中立描述](learning/01-agent-protocols-interfaces/idl-wiki/01-what-is-idl.md) | IDL（接口定义语言）的标准定义、核心特征、发展三阶段时间线与价值定位 | 2026-07-04 | idl、definition、history、concept、interface-contract |
| [二、IDL 类型系统：基本数据类型与注解机制](learning/01-agent-protocols-interfaces/idl-wiki/02-syntax-types.md) | IDL 基本数据类型体系（标量/复合/枚举/容器）与注解注释机制，含 Protobuf/CORBA/Thrift 三语法对照 | 2026-07-04 | idl、syntax、type-system、protobuf、corba-idl、thrift、annotations |
| [三、IDL 接口声明与方法描述：服务契约的通用范式](learning/01-agent-protocols-interfaces/idl-wiki/03-syntax-interface.md) | IDL 接口声明语法与方法描述规范，含参数方向、异常声明、Protobuf/CORBA/Thrift 三语法对照 | 2026-07-04 | idl、syntax、interface、service、rpc、protobuf、corba-idl、thrift |
| [四、主要 IDL 规范介绍：五大主流实现详解](learning/01-agent-protocols-interfaces/idl-wiki/04-major-idl-specs.md) | Protocol Buffers、Apache Thrift、CORBA IDL、COM/DCOM IDL、Apache Avro IDL 五大主流规范详解 | 2026-07-04 | idl、protobuf、thrift、corba、com-idl、avro、specifications |
| [五、IDL 规范对比](learning/01-agent-protocols-interfaces/idl-wiki/05-comparison.md) | Protocol Buffers、Thrift、CORBA IDL、COM IDL、Avro IDL 五大规范的多维度对比与按场景的选型决策指南 | 2026-07-04 | idl、comparison、decision-tree、selection、protobuf、thrift、corba、avro |
| [六、IDL 编译流程与工具链：从源文件到多语言桩代码](learning/01-agent-protocols-interfaces/idl-wiki/06-toolchain.md) | IDL 编译流程图、主流编译器介绍、构建系统集成（Maven/Gradle/Bazel）与 Schema 演进兼容性管理 | 2026-07-04 | idl、toolchain、compiler、codegen、protoc、thrift、maven、gradle、bazel、schema-evolution |
| [七、实际应用案例与最佳实践：IDL 在生产环境的落地](learning/01-agent-protocols-interfaces/idl-wiki/07-use-cases.md) | 三个完整应用案例（gRPC 服务定义、Thrift 微服务接口、CORBA 遗留系统集成）与 IDL 设计最佳实践 | 2026-07-04 | idl、use-cases、grpc、thrift、corba、best-practices、examples |
| [八、与现代接口描述方式对比：从 RPC IDL 到 Web IDL 与 AI-friendly IDL](learning/01-agent-protocols-interfaces/idl-wiki/08-vs-modern-formats.md) | 传统 IDL 与现代接口描述格式（OpenAPI/GraphQL Schema/JSON Schema/AsyncAPI）的边界划分、对比与演进，含 MDI 关联 | 2026-07-04 | idl、openapi、graphql、json-schema、asyncapi、mdi、comparison、modern-formats |
| [九、学习资源与参考资料：术语表、权威规范与扩展阅读](learning/01-agent-protocols-interfaces/idl-wiki/09-resources.md) | IDL 相关术语表、权威参考资料、按难度分级的扩展阅读建议与项目内相关 wiki 交叉引用 | 2026-07-04 | idl、resources、glossary、references、further-reading、specifications |
| [一、概念总览：软件接口的四层抽象](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/00-overview.md) | Interface/API/ABI/Protocol四个核心技术概念的层次总览与阅读指引 | 2026-07-03 | interface、api、abi、protocol、architecture |
| [二、接口（Interface）：语言级行为抽象](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/01-interface.md) | 接口（Interface）的标准定义、核心特征、多范式应用场景与代码案例 | 2026-07-03 | interface、oop、functional-programming、polymorphism、duck-typing |
| [三、API（应用编程接口）：源码与服务级契约](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/02-api.md) | API的精确定义、REST/GraphQL/SOAP/gRPC类型对比、核心特征、应用场景与主流案例 | 2026-07-03 | api、rest、graphql、soap、grpc、web-api、microservices |
| [四、ABI（应用二进制接口）：二进制兼容约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/03-abi.md) | ABI的技术内涵、与API的本质区别、核心技术特征、底层系统应用场景与案例 | 2026-07-03 | abi、binary-compatibility、calling-convention、ffi、shared-library、syscall |
| [五、协议（Protocol）：通信规则约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/04-protocol.md) | 协议的综合定义、网络/软件协议分类、核心特征、主流协议对比与应用场景 | 2026-07-03 | protocol、network、http、tcp、websocket、osi-model、tcp-ip |
| [六、对比分析：四概念系统辨析](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/05-comparison.md) | Interface/API/ABI/Protocol四概念对比表格、关联关系分析、Mermaid架构层次图、常见混淆点澄清与决策指南 | 2026-07-03 | comparison、architecture、abstraction-layers、interface、api、abi、protocol |
| [七、参考资料与扩展阅读](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/06-resources.md) | 术语表、权威参考资料、扩展阅读建议与进阶学习路径 | 2026-07-03 | resources、references、glossary、further-reading、books、rfc |
| [Harness Engineering（驾驭工程）系统性学习Wiki](learning/02-agent-engineering-methodology/harness-engineering-wiki.md) | 阿里技术发布的Harness Engineering深度文章学习笔记，系统讲解从Prompt Engineering到Context Engineering再到Harness Engineering的范式演进，包含四条反直觉铁律、六大工程模式、悟空AI招聘实战案例、行业标杆地图、未来趋势与六条心法。 | 2026-07-04 | Harness Engineering、Agent Engineering、AI Agent、多Agent系统、Prompt Engineering、Context Engineering |
| [Headroom AI Agent上下文压缩中间件完整学习教程](learning/02-agent-engineering-methodology/headroom-context-compression-wiki.md) | 系统学习Headroom AI Agent上下文压缩中间件，掌握给Agent装'压缩层'的完整技术方案，实现1万Token压到1千且质量不降反升，涵盖六种压缩算法、CCR可逆机制、四种接入方式、跨Agent记忆与自动学习等核心特性。 | 2026-07-04 | headroom、context-compression、agent、middleware、token-optimization、ccr、ai-agent |
| [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md) | 源自Andrej Karpathy对LLM编程陷阱观察的四条行为准则（编码前先思考/简约至上/精确编辑/目标驱动），一个CLAUDE.md文件管住AI编程最常犯的毛病。GitHub 61.6k星项目完整教程，包含背景故事、核心原则详解、真实代码正反例、四种分发格式安装指南（CLAUDE.md/Cursor Rules/SKILL.md/插件）、Multica平台架构与multica-cli Skill使用指南、仓库文件结构说明，以及在SpecWeave项目中的整合情况。本文档已原子化，详细内容见 karpathy-llm-coding-guidelines/ 子目录。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、claude、ai-programming、agentic-engineering、claude-code、cursor、skills、plugin、mdc、multica、multica-cli、managed-agents |
| [LongCat-2.0 Agent能力实测Wiki教程](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki.md) | 基于郭震AI实测经验，系统学习美团LongCat-2.0（1.6T参数MoE模型）接入Claude Code的完整流程，涵盖架构解析、配置指南、BI数据看板项目实战、Token效率对比和Loop Engineering方法论。 | 2026-07-04 | longcat、agent、claude-code、moe、loop-engineering、ai-coding、meituan |
| [Vibe Coding 两大神级 Prompt](learning/02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md) | 学习分析卡兹克《Vibe Coding 两大神级 Prompt》一文：第一性原理(管生成)与对抗式审查(管验证)构成完整闭环,是 Vibe Coding 的两大基石。 | 2026-07-04 | vibe-coding、prompt、第一性原理、对抗式审查、ai-agent、代码审查、multi-agent、aihot、可复用模式 |
| [Harness Engineering（驾驭工程）：概述与学习目标](learning/02-agent-engineering-methodology/harness-engineering-wiki/00-overview.md) |  | 2026-07-04 | - |
| [范式演进：三代AI工程](learning/02-agent-engineering-methodology/harness-engineering-wiki/01-paradigm-evolution.md) |  | 2026-07-04 | - |
| [四条反直觉铁律](learning/02-agent-engineering-methodology/harness-engineering-wiki/02-four-iron-laws.md) |  | 2026-07-04 | - |
| [六大工程模式](learning/02-agent-engineering-methodology/harness-engineering-wiki/03-six-patterns.md) |  | 2026-07-04 | - |
| [实战案例：悟空AI招聘](learning/02-agent-engineering-methodology/harness-engineering-wiki/04-wukong-case-study.md) |  | 2026-07-04 | - |
| [行业标杆地图](learning/02-agent-engineering-methodology/harness-engineering-wiki/05-industry-benchmarks.md) |  | 2026-07-04 | - |
| [未来趋势与六条心法](learning/02-agent-engineering-methodology/harness-engineering-wiki/06-future-trends.md) |  | 2026-07-04 | - |
| [批判性思考与评估](learning/02-agent-engineering-methodology/harness-engineering-wiki/07-critical-thinking.md) |  | 2026-07-04 | - |
| [常见问题（FAQ）](learning/02-agent-engineering-methodology/harness-engineering-wiki/08-faq.md) |  | 2026-07-04 | - |
| [资源链接](learning/02-agent-engineering-methodology/harness-engineering-wiki/09-resources.md) |  | 2026-07-04 | - |
| [Karpathy LLM 编程准则：概述与背景](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/00-overview.md) | 源自Andrej Karpathy对LLM编程陷阱观察的四条行为准则，用一个CLAUDE.md文件管住AI编程最常犯的毛病。本教程包含背景介绍、核心原则详解、真实代码正反例、安装使用指南，以及在SpecWeave项目中的整合情况。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、claude、ai-programming、agentic-engineering |
| [四条核心原则详解](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/01-four-principles.md) | 四条核心原则的详细说明：编码前先思考、简约至上、精确编辑、目标驱动，包含每条原则的问题根源、具体要求和检验标准。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、principles、think-before-coding、simplicity、surgical-changes、goal-driven |
| [真实代码正反例](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/02-code-examples.md) | 真实世界代码示例演示四条原则，每个示例展示LLM常见错误做法和正确做法，涵盖隐藏假设、过度抽象、顺手重构、模糊目标等场景。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、examples、python、anti-patterns |
| [快速上手指南](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/03-quickstart.md) | 快速上手安装和使用指南：三种分发格式对比（CLAUDE.md/SKILL.md/Cursor Rules）、Claude Code插件安装、Cursor编辑器集成详解、SKILL.md格式、项目定制方法、贡献者指南。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、claude-code、cursor、installation、quickstart、skills、plugin |
| [SpecWeave 项目整合情况](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/04-specweave-integration.md) | Karpathy LLM编程准则在SpecWeave项目中的整合情况：四条原则如何融入现有规范体系，对应的规范文件位置，以及团队使用方式。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、specweave、integration、rules |
| [资源与参考链接](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/05-resources.md) | 相关资源链接：三个官方仓库（karpathy-skills/multica/multica-cli）的文件结构、分发格式说明、Karpathy原帖、中文报道、Multica平台相关资源等参考资料。 | 2026-07-02 | karpathy、llm、coding、agent、guidelines、resources、references、repository-structure、multica、multica-cli |
| [Multica 平台：AI Agent 协作管理平台](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/06-multica-platform.md) | Multica 是开源的 Managed Agents 平台，将编码 Agent 变成真正的队友——分配任务、跟踪进度、积累技能。本文档介绍 Multica 平台的核心概念、架构、功能模块，以及它与 Karpathy 准则的关系。 | 2026-07-02 | karpathy、llm、coding、agent、multica、platform、managed-agents、agentic-engineering、runtime、daemon、skill、autopilot、squad |
| [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/07-multica-cli-skill.md) | multica-cli 是一个可移植 Skill，教任意本地编码 Agent（Claude Code、Codex、Cursor 等）通过已认证的 multica CLI 安全操作 Multica 平台。本文档按「背景→核心安全原则→命令正反例→快速上手→工作流实战→生态设计理念」六层认知阶梯组织，帮助读者从理解为什么需要到掌握最佳实践。 | 2026-07-02 | karpathy、llm、coding、agent、multica、cli、skill、claude-code、cursor、codex、safety、external-agent |
| [Anthropic Agent 产品线路线图完整学习教程：Conway永久在线智能体、文件记忆、Orbit主动助手、Operon科研平台、BugCrawl代码审计与GPT-5.6竞争分析](learning/03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md) | 深度解析Anthropic即将推出的六条Agent产品线：Conway永久在线智能体、文件级记忆系统、Orbit主动助手、Operon生命科研平台、BugCrawl代码Bug自动修复，以及生态升级细节和GPT-5.6竞争动态分析。 | 2026-07-04 | anthropic、claude、conway、agent、orbit、operon、bugcrawl、file-memory、gpt-5.6、ai-agent、always-on-agent、proactive-ai |
| [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md) | 捕获量子位 2026-06-24 文章《刚刚，Claude Code大升级！卡帕西：LLM第三次变革》核心内容：Anthropic 发布企业协作工具 Claude Tag，定位为 Claude Code 进化，强调团队共享、主动介入（Ambient Mode）、异步执行，卡帕西称其为 LLM 用户界面第三次重大变革。本文档已原子化，详细内容见 claude-tag-article/ 子目录。 | 2026-06-29 | claude、tag、anthropic、agent、enterprise、slack、ambient-mode、opus、karpathy、llm、协作、知识沉淀、复盘闭环、模式入库、已原子化 |
| [Claude Tag：文章概述](learning/03-agent-platforms-tools/claude-tag-article/00-overview.md) | Claude Tag 文章元信息与概述：Anthropic 发布企业协作工具 Claude Tag，卡帕西称其为 LLM 用户界面第三次重大变革。 | 2026-06-29 | claude、tag、anthropic、agent、enterprise、slack、karpathy、llm |
| [Claude Tag：核心观点](learning/03-agent-platforms-tools/claude-tag-article/01-core-insights.md) | Claude Tag 五大核心观点：产品定位（Claude Code进化）、卡帕西LLM三次变革论断、与传统AI助手的根本差异、四大能力（共享上下文/持续记忆/主动介入/异步执行）、企业统一入口战略。 | 2026-06-29 | claude、tag、anthropic、agent、enterprise、ambient-mode、karpathy、llm、协作 |
| [Claude Tag：关键概念与术语](learning/03-agent-platforms-tools/claude-tag-article/02-key-concepts.md) | Claude Tag 关键术语解释：Claude Tag、Ambient Mode（主动介入模式）、共享上下文、持续记忆、异步执行、Claude身份权限隔离、Opus 4.8、Fable 5。 | 2026-06-29 | claude、tag、anthropic、ambient-mode、opus、fable、术语 |
| [Claude Tag：重要数据](learning/03-agent-platforms-tools/claude-tag-article/03-key-data.md) | Claude Tag 重要数据汇总：Anthropic 65%产品代码参与、Opus 4.8唯一支持、率先登陆Slack、30天内取代现有应用、Beta开放对象、扩展计划、Token预算管理等。 | 2026-06-29 | claude、tag、anthropic、opus、slack、数据、统计 |
| [Claude Tag：原文结构框架](learning/03-agent-platforms-tools/claude-tag-article/04-article-structure.md) | 原文四节结构概括：升级概览、先进团队先用Claude、实际部署、社区反响。 | 2026-06-29 | claude、tag、anthropic、slack、fable、社区 |
| [Claude Tag：与 SpecWeave 的关联](learning/03-agent-platforms-tools/claude-tag-article/05-specweave-relevance.md) | Claude Tag 与 SpecWeave 的三点关联：多智能体协作参照（已萃取为team-shared-ai-colleague模式）、组织知识沉淀对照、Agent工作流呼应（已萃取为ambient-proactive-agent模式）。 | 2026-06-29 | claude、tag、specweave、多智能体、知识沉淀、阶段守卫、自我演进 |
| [Claude Tag：知识沉淀闭环](learning/03-agent-platforms-tools/claude-tag-article/06-knowledge-closure.md) | 本知识条目复盘闭环状态：复盘报告索引、已萃取可复用模式（2项L1）、方法论沉淀（2项操作指南）。 | 2026-07-03 | claude、tag、复盘、模式入库、方法论、闭环 |
| [Claude Tag：参考链接](learning/03-agent-platforms-tools/claude-tag-article/07-resources.md) | Claude Tag 相关参考链接汇总：原文、官方产品页、官方博客、媒体报道、复盘报告、已入库模式文件。 | 2026-06-29 | claude、tag、anthropic、参考资料、链接 |
| [scikit-build-core 全面教程：概述与导航](learning/04-docs-markup-tooling/scikit-build-core-wiki/00-overview.md) | scikit-build-core Wiki 教程入口与导航枢纽：3 分钟理解项目定位、核心价值与 7 章阅读路径，含源码版本与学习建议 | 2026-07-04 | scikit-build-core、overview、pep517、cmake、python-packaging |
| [基本概念与架构解析](learning/04-docs-markup-tooling/scikit-build-core-wiki/01-concepts-architecture.md) | 系统讲解 scikit-build-core 的 PEP 517/660 后端机制、CMake 三层抽象、8 步 wheel 构建流程、配置系统四层架构与 File API 状态机 | 2026-07-04 | scikit-build-core、architecture、pep517、pep660、cmake、wheel |
| [项目目录结构与模块功能](learning/04-docs-markup-tooling/scikit-build-core-wiki/02-project-structure.md) | 逐模块解析 src/scikit_build_core/ 的 13 个顶层文件与 14 个子目录，标注源码锚点，覆盖 PEP 517 钩子、配置四层、CMake 三层、File API、元数据插件、可编辑安装、后端适配层 | 2026-07-04 | scikit-build-core、project-structure、modules、source-code |
| [核心 API 使用与配置详解](learning/04-docs-markup-tooling/scikit-build-core-wiki/03-core-api-and-config.md) | 系统讲解 scikit-build-core 的 PEP 517 构建后端钩子与 [tool.scikit-build] 配置项全集，含 Overrides 系统、动态元数据与 CMakeLists.txt 集成标准写法 | 2026-07-04 | scikit-build-core、api、configuration、pep517、pyproject-toml |
| [从入门到进阶操作指南](learning/04-docs-markup-tooling/scikit-build-core-wiki/04-quickstart-to-advanced.md) | 提供三级递进实战路径：从 5 分钟最小 CMake 项目到真实 C++ 扩展包（pybind11/nanobind）再到发版 PyPI、交叉编译与 Stable ABI 高级配置 | 2026-07-04 | scikit-build-core、quickstart、tutorial、cmake、ninja、abi3 |
| [常见问题与最佳实践](learning/04-docs-markup-tooling/scikit-build-core-wiki/05-faq-and-best-practices.md) | 汇总 scikit-build-core 真实项目常见问题与故障排查流程，覆盖 CI、Conda、迁移场景最佳实践与调试技巧 | 2026-07-04 | scikit-build-core、faq、best-practices、troubleshooting、ci、conda |
| [参考资料与扩展阅读](learning/04-docs-markup-tooling/scikit-build-core-wiki/06-resources.md) | 汇总 scikit-build-core 官方资源、教程资料、术语表与扩展阅读路径，含生态项目与进阶学习建议 | 2026-07-04 | scikit-build-core、resources、glossary、references、ecosystem |
| [Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！](learning/05-ai-multimodal-content/animejs-threejs-adapter-analysis.md) | 学习分析《Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！》一文：Anime.js 4.5 推出官方 Three.js 适配器，通过适配器模式、API扁平化和前端语法糖，解决Three.js动画六大痛点，让3D动画写起来像CSS transform一样简单。 | 2026-07-04 | animejs、threejs、3d-animation、webgl、adapter-pattern、前端动画、javascript、动画库 |
| [国产AI模型对比与使用场景推荐](learning/06-business-trends-analysis/domestic-llm-comparison-notes.md) | 系统对比 DeepSeek V4、Kimi K2.7 Code、MiniMax M3、GLM 5.2 四款国产 AI 模型，按不写代码-文案类、不写代码-多模态资料、写代码、高并发批量任务四类人群给出推荐方案，并深入剖析国产模型信任问题，提出'能力是入场券，信任才是留下来的理由'核心洞察。 | 2026-07-04 | llm、domestic-model、model-comparison、glm、kimi、deepseek、minimax、coding、multi-modal、trust、scenario-recommendation、ai-agent |
| [Papi酱关闭公司回归个人IP：创业趋势观察](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki.md) | 系统学习卢松松博客文章《Papi酱把公司全关了，只留七个人》，通过Papi酱十年创业完整时间线，解析\"把公司做小，把IP做大\"的创业新趋势，包含超级IP回归个人案例分析、个人IP vs 平台机构对比、小而美创业模式实践启示。 | 2026-07-04 | papi-jiang、个人IP、内容创业、MCN、创业趋势、小而美、商业模式、卢松松 |
| [AI变现完整指南：从技术到商业的全流程方法论](learning/06-business-trends-analysis/ai-monetization-wiki/00-overview.md) | AI变现完整指南总览，涵盖8大核心模块、3类应用场景与13章阅读路径 | 2026-07-03 | ai-monetization、overview、commercialization、business、guide |
| [核心概念界定：AI变现术语体系](learning/06-business-trends-analysis/ai-monetization-wiki/01-core-concepts.md) | AI变现核心术语界定，含标准定义、AI变现语境释义与示例 | 2026-07-03 | ai-monetization、concepts、terminology、pmf、ltv-cac、moat |
| [市场需求分析：识别与评估AI商业化机会](learning/06-business-trends-analysis/ai-monetization-wiki/02-market-analysis.md) | AI商业化机会识别与评估方法，含市场调研、用户需求挖掘、竞争格局、规模估算与场景适配性评估 | 2026-07-03 | ai-monetization、market-analysis、tam-sam-som、porter-five-forces、user-research |
| [商业模式设计：AI产品的盈利模式选择](learning/06-business-trends-analysis/ai-monetization-wiki/03-business-models.md) | AI产品9类盈利模式、价值主张设计、客户细分与商业模式选择决策树 | 2026-07-03 | ai-monetization、business-model、saas、pricing、canvas、freemium |
| [技术选型：AI技术栈决策框架](learning/06-business-trends-analysis/ai-monetization-wiki/04-tech-selection.md) | AI技术栈决策框架，含算法选型、算力配置、数据策略、部署方式与成本估算 | 2026-07-03 | ai-monetization、tech-selection、algorithm、compute、data-strategy、deployment |
| [产品开发：AI产品的构建与迭代流程](learning/06-business-trends-analysis/ai-monetization-wiki/05-product-development.md) | AI产品开发流程，含原型设计、敏捷迭代、测试验证、数据飞轮与效果度量 | 2026-07-03 | ai-monetization、product-development、mlops、poc、data-flywheel、evaluation |
| [市场推广：AI产品的GTM策略](learning/06-business-trends-analysis/ai-monetization-wiki/06-marketing-strategy.md) | AI产品市场进入策略，含定位、渠道、传播、GTM节奏与冷启动 | 2026-07-03 | ai-monetization、gtm、marketing、positioning、cold-start、channel |
| [盈利策略：定价模型与规模化路径](learning/06-business-trends-analysis/ai-monetization-wiki/07-profitability-strategy.md) | AI产品定价模型、收入结构设计与规模化盈利路径，含单位经济模型优化 | 2026-07-03 | ai-monetization、pricing、revenue-structure、scaling、unit-economics |
| [企业服务场景：ToB AI应用变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/08-scenario-enterprise.md) | ToB AI应用三类变现路径、成功案例剖析与行业挑战应对策略 | 2026-07-03 | ai-monetization、tob、enterprise、saas、customization、platform |
| [消费级产品场景：ToC AI应用变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/09-scenario-consumer.md) | ToC AI应用三类变现路径、成功案例剖析与留存获客挑战应对 | 2026-07-03 | ai-monetization、toc、consumer、freemium、subscription、retention |
| [行业解决方案场景：垂直行业AI变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/10-scenario-industry.md) | 医疗/金融/制造/教育/零售五大垂直行业AI变现路径、案例与挑战应对 | 2026-07-03 | ai-monetization、industry、vertical、healthcare、finance、manufacturing、education、retail |
| [实施步骤与关键成功因素](learning/06-business-trends-analysis/ai-monetization-wiki/11-implementation-steps.md) | AI变现六阶段实施路径与各阶段关键成功因素 | 2026-07-03 | ai-monetization、implementation、ksf、roadmap、stages |
| [风险提示与资源推荐](learning/06-business-trends-analysis/ai-monetization-wiki/12-risks-resources.md) | AI变现五大风险类别规避策略与实用资源推荐、术语速查表 | 2026-07-03 | ai-monetization、risks、resources、compliance、glossary |
| [Papi酱关闭公司回归个人IP：概述与学习目标](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/00-overview.md) |  | 2026-07-04 | papi-jiang、个人IP、内容创业、MCN、创业趋势、小而美、商业模式、卢松松 |
| [Papi酱关闭公司回归个人IP：案例全景与时间线](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/01-case-timeline.md) |  | 2026-07-04 | papi-jiang、个人IP、内容创业、MCN、创业趋势、时间线、papitube、泰洋川禾 |
| [Papi酱关闭公司回归个人IP：核心观点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/02-core-viewpoints.md) |  | 2026-07-04 | papi-jiang、个人IP、内容创业、核心观点、创业思维、商业模式、小而美 |
| [Papi酱关闭公司回归个人IP：行业观察与案例](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/03-industry-trend.md) |  | 2026-07-04 | papi-jiang、个人IP、罗永浩、李子柒、李佳琦、行业趋势、超级IP、MCN |
| [Papi酱关闭公司回归个人IP：模式深度对比](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/04-model-comparison.md) |  | 2026-07-04 | papi-jiang、个人IP、MCN、模式对比、超级个体、平台机构、商业模式 |
| [Papi酱关闭公司回归个人IP：创业启示与实践要点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/05-entrepreneurship-insights.md) |  | 2026-07-04 | papi-jiang、个人IP、创业启示、小而美、实践要点、商业模式、创业建议 |
| [Papi酱关闭公司回归个人IP：总结与Takeaway](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/06-summary.md) |  | 2026-07-04 | papi-jiang、个人IP、总结、takeaway、创业趋势、核心要点 |
| [Papi酱关闭公司回归个人IP：常见问题FAQ](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/07-faq.md) |  | 2026-07-04 | papi-jiang、个人IP、FAQ、常见问题、创业疑问、MCN |
| [Papi酱关闭公司回归个人IP：资源链接](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/08-resources.md) |  | 2026-07-04 | papi-jiang、个人IP、资源链接、卢松松、参考资料、相关阅读 |
| [向日葵（Sunlogin）产品学习系列](learning/07-vendor-product-learning/sunlogin/sunlogin-product-series-index.md) |  | 2026-07-05 | 向日葵、sunlogin、Oray、贝锐科技、远程控制、智能硬件、产品学习、系列索引 |
| [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md) | TuyaOpen 是涂鸦开源的跨平台、跨芯片、跨操作系统的 AI-IoT SDK，核心目标是用一套灵活的 C/C++ SDK，结合涂鸦云的低延迟多模态 AI 能力，简化开放式 AI-IoT 生态的搭建。 | 2026-06-30 | tuya、tuyaopen、iot、sdk、ai、embedded、c、cpp、mcu、esp32、mcp、cloud、tkl、tal、tdd、tdl |
| [TuyaOpen-dev-skills 学习笔记](learning/07-vendor-product-learning/tuya/tuyaopen-dev-skills-learning.md) | TuyaOpen-dev-skills 是面向 TuyaOpen 硬件开发流程的 AI Skills 仓库，以“最小 SKILL.md + references/ 按需加载 + scripts/ 可执行脚本”的三分结构，把环境搭建、编译、代码检查、烧录监控与调试闭环规范化。 | 2026-06-30 | tuya、tuyaopen、skills、agent-skills、cursor、claude、iot、embedded、workflow、ci |
| [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/07-vendor-product-learning/tuya/tuyaopen-folder-learning-path.md) | 针对 external/TuyaOpen 工作区的可执行学习路线：先跑通 LINUX target 构建闭环，再进入硬件烧录与 AI 智能体硬件能力区。 | 2026-06-30 | tuyaopen、learning-path、iot、embedded、sdk、cli、tos |
| [WSL CLI 命令树与架构 Wiki 参考手册](learning/08-systems-infrastructure/wsl-cli-and-architecture-wiki.md) | 基于 external/WSL 源码（src/windows/wslc/ + doc/docs/）深度核实的 WSL CLI 命令树、参数定义、CLI 架构四层模型与官方架构 Mermaid 源图。修正先前学习计划中关于 CLI 命令短形态的误判——list/remove 才是主名，ls/ps/rm/delete 是别名。补充 interop binfmt 机制、systemd 启动流程、wslservice COM 接口、mini_init 多通道拓扑等技术细节。所有信息均有源码文件锚点可追溯。 | 2026-07-01 | wsl、wslc、cli、command-tree、argument-definitions、architecture、mermaid、interop、systemd、wslservice、com、binfmt、hvsocket、source-verification |
| [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md) | 基于 external/WSL 源码 + wsl.dev 开发者文档 + learn.microsoft.com 官方文档制定的系统学习计划，涵盖 Windows/Linux 三层架构、Linux 侧核心进程（mini_init/init/plan9/gns/relay）、Plan9/DrvFs 文件系统互操作、WSLC Container API 三语言投影（C/C#/C++ WinRT）、CMake 跨编译构建、组策略与诊断调试，包含 5 个实操练习、官方端到端示例、完整错误码表与 4 周学习路径。 | 2026-07-01 | wsl、learning-path、linux、windows、container、wslc、plan9、drvfs、cmake、sdk、diagnostics、hvsocket、gns、systemd、winrt、nuget、com、error-codes |

### operations

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md) | 基于Trae IDE集成浏览器（integrated_browser MCP）和Playwright Python脚本操作forum.trae.cn论坛的完整指南，包含DOM选择器参考、Ember框架感知操作方法、操作序列模板、JavaScript代码片段、独立Python脚本使用、故障排查和长期方案（@discourse/mcp）接入指南。v2.1更新：精确化DOM选择器、新增diagnoseButtons诊断函数、补充MCP参数陷阱警告、补全误操作恢复方法、新增MCP vs Playwright操作区别对照表。 | 2026-06-30 | discourse、论坛、自动化、browser、mcp、playwright、发布 |
| [HTML 正文提取操作指南](operations/html-body-extraction.md) | HTML 正文提取双方案：正则提取（首选）与边界标记索引截取法（兜底），含 HTML 清洗六步流程，适用于复杂嵌套 HTML 容器 | 2026-06-29 | html、正文提取、正则、索引截取、边界标记、html清洗、降级策略 |
| [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md) | 一条可落地执行、可观测验收的 Tuya IPC（网络摄像机）端-云-手机最小闭环跑通路径：先明确最小假设，再按步骤给出依赖/验收/排查，并附依赖关系图与闭环验收总表。 | 2026-06-30 | tuya、ipc、iot、闭环、配网、音视频、设备绑定、事件上报、联调、排查、验收 |
| [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md) | 当需要在 SpecWeave 中新增或使用 flexloop 相关功能时，基于三区域边界模型和四不原则的5种合规集成路径决策指南 | 2026-06-29 | vendor、flexloop、agentforge、submodule、集成方案、三区域模型、四不原则 |
| [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md) | 微信公众号文章内容提取双路径决策模型：defuddle CLI 与 PowerShell Invoke-WebRequest 互为兜底，含边界标记索引截取法作为正则失败时的兜底方案 | 2026-06-29 | 微信公众号、内容提取、defuddle、powershell、invoke-webrequest、html提取、反爬、降级策略 |
| [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md) | 记录 Windows PowerShell 环境下 heredoc 语法不可用的替代方案 | 2026-06-23 | windows、powershell、shell、heredoc、git |
| [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md) | 记录 Windows PowerShell 下将 Python 中文 stdout 通过文本管道写入文件时可能发生的转码污染，以及推荐的安全写回方案 | 2026-06-30 | windows、powershell、encoding、utf-8、pipe、set-content、python、docs |
| [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md) | 系统性解决Windows终端中文乱码问题的完整指南，涵盖系统级/用户级/项目级三层配置方案 | 2026-07-01 | windows、powershell、cmd、utf-8、encoding、gbk、chcp、乱码 |

### research

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [MDI (Markdown Interface) 深度研究报告](mdi-research-report.md) |  | 2026-07-02 | - |

### standards

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [MDI Spec v1.0：Markdown即接口规范](mdi-spec-v1.0.md) |  | 2026-07-02 | - |

### troubleshooting

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md) | 记录 AI 智能体因未读取 AGENTS.md 启动协议而导致输出格式、文件路径、文档结构三项错误的完整故障链与修复方案 | 2026-06-24 | agents、protocol、startup、output-format、path、skill-conflict |
| [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md) | 记录 PowerShell Move-Item 重命名目录时 Access Denied 错误的排查与解决方案 | 2026-06-23 | windows、powershell、rename、directory、access-denied |
| [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md) | 记录在 submodule 目录内创建主项目文件导致 submodule 永久 dirty 的故障原因与解决方案，以及 submodule 元数据外置的最佳实践 | 2026-06-29 | git、submodule、vendor、dirty、modified-content |

### unknown

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [stage-guardrails-guide](stage-guardrails-guide.md) |  |  | - |
| [three-layer-routing](three-layer-routing.md) |  |  | - |
| [VENDOR-INTEGRATION](VENDOR-INTEGRATION.md) |  |  | - |
| [B2B/旗舰产品信息源分层采集规范](best-practices/b2b-product-info-collection-sop.md) |  | 2026-07-04 | 信息采集、B2B产品、SOP、多源验证、Defuddle |
| [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md) |  | 2026-07-04 | agent-runtime、agent-protocol、langgraph、openai-assistants、autogen、claude-sdk、mcp、thread、run、checkpoint、artifact、event、human-in-the-loop、error-recovery、multi-agent、observability |
| [国内 Skill/MCP 生态盘点：16 个品牌的 Agent 化浪潮](learning/01-agent-protocols-interfaces/domestic-skill-mcp-ecosystem-wiki.md) |  | 2026-07-04 | skill、mcp、cli、ai-agent、ecosystem、domestic、wechat、feishu、dingtalk、payment |
| [00、概述与背景](learning/01-agent-protocols-interfaces/agent-communication-protocols/00-overview.md) |  |  | - |
| [01、MCP协议详解：Model Context Protocol](learning/01-agent-protocols-interfaces/agent-communication-protocols/01-mcp.md) |  |  | - |
| [02、ACP协议详解：Agent Communication Protocol](learning/01-agent-protocols-interfaces/agent-communication-protocols/02-acp.md) |  |  | - |
| [03、A2A协议详解：Agent-to-Agent Protocol](learning/01-agent-protocols-interfaces/agent-communication-protocols/03-a2a.md) |  |  | - |
| [04、ANP协议概述：Agent Network Protocol](learning/01-agent-protocols-interfaces/agent-communication-protocols/04-anp.md) |  |  | - |
| [05、协议对比与分层架构](learning/01-agent-protocols-interfaces/agent-communication-protocols/05-comparison.md) |  |  | - |
| [06、交互流程与协作模式](learning/01-agent-protocols-interfaces/agent-communication-protocols/06-flows.md) |  |  | - |
| [07、技术实现要点与代码示例](learning/01-agent-protocols-interfaces/agent-communication-protocols/07-implementation.md) |  |  | - |
| [08、典型应用场景](learning/01-agent-protocols-interfaces/agent-communication-protocols/08-scenarios.md) |  |  | - |
| [09、术语表](learning/01-agent-protocols-interfaces/agent-communication-protocols/09-glossary.md) |  |  | - |
| [10、资源与参考链接](learning/01-agent-protocols-interfaces/agent-communication-protocols/10-resources.md) |  |  | - |
| [11、快速参考速查表](learning/01-agent-protocols-interfaces/agent-communication-protocols/11-quick-reference.md) |  |  | - |
| [一、概述](learning/01-agent-protocols-interfaces/agent-skills-wiki/00-overview.md) |  |  | - |
| [二、核心机制：渐进式披露（Progressive Disclosure）](learning/01-agent-protocols-interfaces/agent-skills-wiki/01-progressive-disclosure.md) |  |  | - |
| [三、目录结构规范](learning/01-agent-protocols-interfaces/agent-skills-wiki/02-directory-structure.md) |  |  | - |
| [四、SKILL.md 格式规范](learning/01-agent-protocols-interfaces/agent-skills-wiki/03-skill-md-format.md) |  |  | - |
| [04-quickstart](learning/01-agent-protocols-interfaces/agent-skills-wiki/04-quickstart.md) |  |  | - |
| [[分析标题]](learning/01-agent-protocols-interfaces/agent-skills-wiki/05-best-practices.md) |  |  | - |
| [/// script](learning/01-agent-protocols-interfaces/agent-skills-wiki/06-scripts-guide.md) |  |  | - |
| [此示例使用 Claude Code 的 JSON 输出来检查 Skill 工具调用](learning/01-agent-protocols-interfaces/agent-skills-wiki/07-description-optimization.md) |  |  | - |
| [08-evals](learning/01-agent-protocols-interfaces/agent-skills-wiki/08-evals.md) |  |  | - |
| [验证一个技能目录](learning/01-agent-protocols-interfaces/agent-skills-wiki/09-skills-ref-tool.md) |  |  | - |
| [10-file-references](learning/01-agent-protocols-interfaces/agent-skills-wiki/10-file-references.md) |  |  | - |
| [11-project-comparison](learning/01-agent-protocols-interfaces/agent-skills-wiki/11-project-comparison.md) |  |  | - |
| [技术上无效的 YAML——冒号破坏了解析](learning/01-agent-protocols-interfaces/agent-skills-wiki/12-client-implementation.md) |  |  | - |
| [13-resources](learning/01-agent-protocols-interfaces/agent-skills-wiki/13-resources.md) |  |  | - |
| [My Skill](learning/01-agent-protocols-interfaces/agent-skills-wiki/14-quick-reference.md) |  |  | - |
| [Ch00 - TVM FFI 概述与定位](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/00-overview.md) |  | 2026-07-05 | tvm-ffi、ffi、cross-language、cpp、python、rust |
| [Ch01 - 系统架构与设计理念](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/01-architecture.md) |  | 2026-07-05 | tvm-ffi、ffi、cross-language、cpp、python、rust |
| [02 - C++ 核心 API：Any、Object、Function、Tensor](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/02-cpp-core-api.md) |  | 2026-07-05 | tvm-ffi、ffi、cpp、core-api |
| [03 - 类型系统：DType、Enum、Optional、String](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/03-type-system.md) |  | 2026-07-05 | tvm-ffi、ffi、cpp、core-api |
| [04 - 容器类型：Array、Map、Dict、List、Tuple、Shape、Variant](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/04-containers.md) |  | 2026-07-05 | tvm-ffi、ffi、cpp、core-api |
| [05 - 反射与注册机制](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/05-reflection.md) |  | 2026-07-05 | tvm-ffi、ffi、cpp、core-api |
| [06 - 序列化：JSON、Base64、结构相等与哈希](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/06-serialization.md) |  | 2026-07-05 | tvm-ffi、ffi、cpp、core-api |
| [07 - Python 绑定机制](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/07-python-bindings.md) |  | 2026-07-05 | tvm-ffi、ffi、python、cuda、jit、dlpack |
| [08 - CUDA 支持](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/08-cuda-support.md) |  | 2026-07-05 | tvm-ffi、ffi、python、cuda、jit、dlpack |
| [09 - ORCJIT 扩展](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/09-orcjit-extension.md) |  | 2026-07-05 | tvm-ffi、ffi、python、cuda、jit、dlpack |
| [10 - DLPack 集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/10-dlpack-integration.md) |  | 2026-07-05 | tvm-ffi、ffi、python、cuda、jit、dlpack |
| [编译构建与项目集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/11-build-and-integration.md) |  | 2026-07-05 | tvm-ffi、ffi、build、examples、best-practices、faq、resources |
| [完整实战示例](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/12-examples.md) |  | 2026-07-05 | tvm-ffi、ffi、build、examples、best-practices、faq、resources |
| [最佳实践与性能优化](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/13-best-practices.md) |  | 2026-07-05 | tvm-ffi、ffi、build、examples、best-practices、faq、resources |
| [常见问题解答 (FAQ)](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/14-faq.md) |  | 2026-07-05 | tvm-ffi、ffi、build、examples、best-practices、faq、resources |
| [参考资料与学习路径](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/15-resources.md) |  | 2026-07-05 | tvm-ffi、ffi、build、examples、best-practices、faq、resources |
| [dspark-paper-wiki](learning/02-agent-engineering-methodology/dspark-paper-wiki.md) |  |  | - |
| [AI 四大工程概念演进：Prompt → Context → Harness → Loop](learning/02-agent-engineering-methodology/four-engineering-concepts-wiki.md) |  | 2026-07-04 | prompt-engineering、context-engineering、harness-engineering、loop-engineering、ai-agent、bottleneck-shift、methodology |
| [Headroom：概述与学习目标](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/00-overview.md) |  |  | - |
| [核心架构与设计理念](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/01-core-architecture.md) |  |  | - |
| [六种压缩算法详解](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/02-compression-algorithms.md) |  |  | - |
| [CCR可逆机制深度解析](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/03-ccr-mechanism.md) |  |  | - |
| [四种接入方式详解](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/04-integration-methods.md) |  |  | - |
| [效果验证与数据分析](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/05-performance-data.md) |  |  | - |
| [跨Agent记忆与自动学习](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/06-advanced-features.md) |  |  | - |
| [快速上手指南](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/07-quick-start.md) |  |  | - |
| [深度洞察与模式萃取](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/08-insights-patterns.md) |  |  | - |
| [常见问题与资源链接](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/09-faq-resources.md) |  |  | - |
| [总结与Takeaways](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/10-summary.md) |  |  | - |
| [LongCat-2.0 Agent能力实测：概述与学习目标](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/00-overview.md) |  |  | - |
| [LongCat-2.0核心概念解析](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/01-core-concepts.md) |  |  | - |
| [Claude Code接入LongCat-2.0配置指南](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/02-claude-code-integration.md) |  |  | - |
| [BI数据看板项目实战全流程](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/03-bi-dashboard-demo.md) |  |  | - |
| [Token效率对比分析](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/04-token-efficiency.md) |  |  | - |
| [Loop Engineering方法论解析](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/05-loop-engineering.md) |  |  | - |
| [总结与回顾](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/06-summary.md) |  |  | - |
| [常见问题（FAQ）](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/07-faq.md) |  |  | - |
| [资源与参考链接](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/08-resources.md) |  |  | - |
| [Anthropic Financial Services 完整教程：华尔街的AI金融Agent工具箱](learning/03-agent-platforms-tools/anthropic-financial-services-wiki.md) |  | 2026-07-04 | anthropic、financial-services、ai-agent、claude、mcp、fintech、vertical-industry、investment-banking |
| [AReaL 2.0 自演进 Agent 在线强化学习基础设施学习 Wiki](learning/03-agent-platforms-tools/areal-agent-rl-wiki.md) |  | 2026-07-04 | areal、agentic-rl、online-rl、self-evolving-agent、reinforcement-learning、ant-group、agent-infrastructure、agent-trajectory |
| [BrowserAct 完整学习教程：让Agent真正能操作浏览器的自动化工具](learning/03-agent-platforms-tools/browseract-wiki.md) |  | 2026-07-04 | browseract、ai-agent、browser-automation、playwright、skill-forge、web-automation |
| [EchoBird 百灵鸟项目学习 Wiki 教程](learning/03-agent-platforms-tools/echobird-wiki.md) |  | 2026-07-04 | echobird、ai-agent、tauri、rust、model-nexus、claude-code、codex、openclaw、local-llm、desktop-tool |
| [MopMonk 安全 Agent Wiki 教程](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki.md) |  |  | - |
| [明略科技 Octo 平台学习 Wiki：Private AI 时代的多 Agent 协作基础设施](learning/03-agent-platforms-tools/octo-platform-wiki.md) |  | 2026-07-04 | octo、mininglamp、private-ai、agent-collaboration、a2a、matter、taste、orchestration、multi-agent、trustworthy-ai |
| [Open Code Review 完整学习教程：阿里开源 AI 代码评审工具](learning/03-agent-platforms-tools/open-code-review-wiki.md) |  | 2026-07-04 | open-code-review、ai-code-review、alibaba、cli、agent、aacr-bench、code-quality、devops |
| [QuantDinger：开源AI量化交易基础设施层完整教程](learning/03-agent-platforms-tools/quantdinger-ai-trading-wiki.md) |  | 2026-07-04 | quantdinger、ai-trading、mcp、quantitative-finance、self-hosted、docker、agent-gateway、trading-bot |
| [Rainman Translate Book Wiki 教程](learning/03-agent-platforms-tools/rainman-translate-book-wiki.md) |  |  | - |
| [The Agency 项目完整学习教程](learning/03-agent-platforms-tools/the-agency-project-wiki.md) |  | 2026-07-04 | the-agency、ai-agent、agent-framework、multi-agent、claude-code、cursor |
| [教程概述与学习目标](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/00-overview.md) |  |  | - |
| [核心概念解析（一）：CyberGym、Harness与PoC](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/01-core-concepts.md) |  |  | - |
| [MiniMax M3基座：国产开源的六边形战士](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/02-minimax-m3.md) |  |  | - |
| [三大核心技术：记忆驱动的安全Agent范式](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/03-core-technologies.md) |  |  | - |
| [步骤式学习导读：入门/进阶/深入三层](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/04-learning-guide.md) |  |  | - |
| [常见问题解答（FAQ）](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/05-faq.md) |  |  | - |
| [相关资源链接](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/06-resources.md) |  |  | - |
| [概述与学习目标](learning/03-agent-platforms-tools/open-code-review-wiki/00-overview.md) |  |  | - |
| [核心概念与设计理念](learning/03-agent-platforms-tools/open-code-review-wiki/01-core-concepts.md) |  |  | - |
| [安装与配置指南](learning/03-agent-platforms-tools/open-code-review-wiki/02-installation.md) |  |  | - |
| [使用流程与命令详解](learning/03-agent-platforms-tools/open-code-review-wiki/03-usage.md) |  |  | - |
| [关键技术优化](learning/03-agent-platforms-tools/open-code-review-wiki/04-optimizations.md) |  |  | - |
| [集成与高级用法](learning/03-agent-platforms-tools/open-code-review-wiki/05-integrations.md) |  |  | - |
| [效果验证与质量评估](learning/03-agent-platforms-tools/open-code-review-wiki/06-effectiveness.md) |  |  | - |
| [局限性与对比](learning/03-agent-platforms-tools/open-code-review-wiki/07-limitations.md) |  |  | - |
| [总结与展望](learning/03-agent-platforms-tools/open-code-review-wiki/08-summary.md) |  |  | - |
| [常见问题（FAQ）](learning/03-agent-platforms-tools/open-code-review-wiki/09-faq.md) |  |  | - |
| [资源与参考链接](learning/03-agent-platforms-tools/open-code-review-wiki/10-resources.md) |  |  | - |
| [教程概述与学习目标](learning/03-agent-platforms-tools/rainman-translate-book-wiki/00-overview.md) |  |  | - |
| [核心功能详解](learning/03-agent-platforms-tools/rainman-translate-book-wiki/01-core-concepts.md) |  |  | - |
| [安装部署指南](learning/03-agent-platforms-tools/rainman-translate-book-wiki/02-installation.md) |  |  | - |
| [使用流程](learning/03-agent-platforms-tools/rainman-translate-book-wiki/03-usage.md) |  |  | - |
| [局限性与注意事项](learning/03-agent-platforms-tools/rainman-translate-book-wiki/04-limitations.md) |  |  | - |
| [总结与回顾](learning/03-agent-platforms-tools/rainman-translate-book-wiki/05-summary.md) |  |  | - |
| [常见问题](learning/03-agent-platforms-tools/rainman-translate-book-wiki/06-faq.md) |  |  | - |
| [资源链接](learning/03-agent-platforms-tools/rainman-translate-book-wiki/07-resources.md) |  |  | - |
| [Declarative Partial Updates 完整教程：HTML 声明式局部更新能力解析](learning/04-docs-markup-tooling/declarative-partial-updates-wiki.md) |  | 2026-07-04 | html、declarative-partial-updates、streaming、partial-rendering、web-standards、chrome、declarative-shadow-dom、ssr |
| [ExecutableBooks 与 MyST Markdown 完整学习指南](learning/04-docs-markup-tooling/executablebooks-myst-guide-wiki.md) |  |  | - |
| [ExecutableBooks 生态概览](learning/04-docs-markup-tooling/executablebooks-myst-guide/00-overview.md) |  |  | - |
| [MyST Markdown 核心语法](learning/04-docs-markup-tooling/executablebooks-myst-guide/01-myst-syntax.md) |  |  | - |
| [MyST 项目结构与 myst.yml 配置](learning/04-docs-markup-tooling/executablebooks-myst-guide/02-project-structure.md) |  |  | - |
| [Frontmatter 配置详解](learning/04-docs-markup-tooling/executablebooks-myst-guide/03-frontmatter-config.md) |  |  | - |
| [目录结构（TOC）配置指南](learning/04-docs-markup-tooling/executablebooks-myst-guide/04-table-of-contents.md) |  |  | - |
| [MyST Markdown 使用最佳实践](learning/04-docs-markup-tooling/executablebooks-myst-guide/05-best-practices.md) |  |  | - |
| [参考资源与链接汇总](learning/04-docs-markup-tooling/executablebooks-myst-guide/06-resources.md) |  |  | - |
| [Admonitions（提示框）样式大全](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/admonitions.md) |  |  | - |
| [MyST Markdown 基础语法示例](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/basic-syntax.md) |  |  | - |
| [交叉引用示例](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/cross-references.md) |  |  | - |
| [GitHub Tools MCP Server](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/mcp-server-demo.md) |  |  | - |
| [MyST Roles（行内扩展）示例](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/roles-demo.md) |  |  | - |
| [GitHub Tools MCP Server](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/poc/github-tools.md) |  |  | - |
| [Weather Service MCP Server](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/poc/weather-service.md) |  |  | - |
| [第0章：快速上手（Quick Start）](learning/04-docs-markup-tooling/myst-markdown-tutorial/00-quick-start.md) |  |  | - |
| [第1章：MyST 简介与 CommonMark 对比](learning/04-docs-markup-tooling/myst-markdown-tutorial/01-introduction.md) |  |  | - |
| [第2章：基础语法（上）- 文本与格式](learning/04-docs-markup-tooling/myst-markdown-tutorial/02-basic-syntax-part1.md) |  |  | - |
| [第3章：基础语法（下）- 列表、链接与图片](learning/04-docs-markup-tooling/myst-markdown-tutorial/03-basic-syntax-part2.md) |  |  | - |
| [第4章：高级功能 - Directives 和 Roles](learning/04-docs-markup-tooling/myst-markdown-tutorial/04-advanced-directives-roles.md) |  |  | - |
| [第5章：高级功能 - 交叉引用](learning/04-docs-markup-tooling/myst-markdown-tutorial/05-advanced-cross-references.md) |  |  | - |
| [第6章：高级功能 - 数学公式与代码块](learning/04-docs-markup-tooling/myst-markdown-tutorial/06-advanced-math-code.md) |  |  | - |
| [第7章：高级功能 - 注释、脚注与参考文献](learning/04-docs-markup-tooling/myst-markdown-tutorial/07-advanced-notes-citations.md) |  |  | - |
| [第8章：扩展组件 - 提示框（Admonitions）](learning/04-docs-markup-tooling/myst-markdown-tutorial/08-components-admonitions.md) |  |  | - |
| [第9章：扩展组件 - 卡片、下拉与标签页](learning/04-docs-markup-tooling/myst-markdown-tutorial/09-components-ui.md) |  |  | - |
| [第10章：扩展组件 - 图片与表格](learning/04-docs-markup-tooling/myst-markdown-tutorial/10-components-figures.md) |  |  | - |
| [第11章：工具链集成 - Sphinx + myst-parser](learning/04-docs-markup-tooling/myst-markdown-tutorial/11-tooling-sphinx.md) |  |  | - |
| [第12章：工具链集成 - Jupyter Book v1](learning/04-docs-markup-tooling/myst-markdown-tutorial/12-tooling-jupyter-book.md) |  |  | - |
| [第13章：工具链集成 - mystmd（新一代）](learning/04-docs-markup-tooling/myst-markdown-tutorial/13-tooling-mystmd.md) |  |  | - |
| [第14章：实战案例 - 技术文档写作](learning/04-docs-markup-tooling/myst-markdown-tutorial/14-case-study-tech-docs.md) |  |  | - |
| [第15章：实战案例 - 学术论文与书籍](learning/04-docs-markup-tooling/myst-markdown-tutorial/15-case-study-academic.md) |  |  | - |
| [第16章：常见问题解答（FAQ）](learning/04-docs-markup-tooling/myst-markdown-tutorial/16-faq.md) |  |  | - |
| [附录A：MyST Markdown 速查表](learning/04-docs-markup-tooling/myst-markdown-tutorial/appendix/cheat-sheet.md) |  |  | - |
| [附录B：资源推荐](learning/04-docs-markup-tooling/myst-markdown-tutorial/appendix/resources.md) |  |  | - |
| [示例：Admonitions 提示框样式大全](learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/admonitions-demo.md) |  |  | - |
| [示例：图片与表格](learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/figures-tables-demo.md) |  |  | - |
| [模板：学术论文模板](learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/paper-template.md) |  |  | - |
| [模板：技术文档模板](learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/tech-doc-template.md) |  |  | - |
| [示例：卡片、下拉与标签页](learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/ui-components-demo.md) |  |  | - |
| [Agnes AI 与 Pavo 创作平台完整学习教程：免费多模态API+一站式AI短剧工作流](learning/05-ai-multimodal-content/agnes-pavo-creative-platform-wiki.md) |  | 2026-07-04 | agnes-ai、pavo、ai-video、ai-shortdrama、agent、harness、aigc、creative-platform、free-api、multimodal |
| [AudioX-Turbo 极速音频生成完整学习教程：4步推理+6种任务统一+920万数据集的Anything-to-Audio框架](learning/05-ai-multimodal-content/audiox-turbo-audio-generation-wiki.md) |  | 2026-07-04 | AudioX-Turbo、音频生成、音乐生成、视频配音、扩散模型、模型蒸馏、AI开源、多模态、Anything-to-Audio、Distribution-Matching-Distillation、师生蒸馏 |
| [ian-xiaohei-illustrations](learning/05-ai-multimodal-content/ian-xiaohei-illustrations.md) |  |  | - |
| [LibTV AI 短剧创作工具学习 Wiki](learning/05-ai-multimodal-content/libtv-ai-shortdrama-wiki.md) |  | 2026-07-04 | libtv、ai-shortdrama、ai-video、ai-manhua、character-quality、emotion-control、3d-director、workflow |
| [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/05-ai-multimodal-content/text-to-cad-wiki.md) |  | 2026-07-04 | text-to-cad、cad、ai-agent、build123d、step、urdf、3d-printing、robotics |
| [三个热门AI工具完整指南：微软AI终端、Claudian笔记插件、book-to-skill书籍转Skill](learning/06-business-trends-analysis/three-ai-tools-wiki.md) |  | 2026-07-04 | ai-tools、intelligent-terminal、claudian、book-to-skill、ai-agent、terminal、obsidian、claude-code、agent-skills |
| [火山引擎KickArt一站式电商营销创作Agent完整学习笔记：六大能力+四大场景+全链路闭环的营销视频生产平台](learning/06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md) |  | 2026-07-04 | KickArt、火山引擎、AI视频生成、电商营销、创作Agent、爆款裂变、投前预审、内容分发、Seedance、VLM、AIGC营销、短视频创作 |
| [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md) |  | 2026-07-04 | 贝锐、Oray、OrayClaw、龙虾、AI Agent、MCP、向日葵、蒲公英、花生壳、洋葱头、远程连接、AI执行基础设施、远程运维、SD-WAN、内网穿透、RPA、软硬结合 |
| [向日葵开机盒子产品系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis.md) |  | 2026-07-04 | 向日葵、开机盒子、远程开机、WOL、硬件产品、Oray、贝锐科技、远程办公、IoT、智能硬件 |
| [向日葵USB远程摄像头SU1完整学习教程：400万高清、双全向麦克风、远程视频多面手深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md) |  | 2026-07-04 | 向日葵、USB摄像头、SU1、远程视频、远程监控、远程医疗、视频会议、400万像素、双全向麦克风、免驱、智能硬件、Oray、贝锐科技、远程办公 |
| [向日葵智能远控鼠标MM110/BM110产品学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-mouse-bm110-mm110-analysis.md) |  | 2026-07-04 | 向日葵、智能远控鼠标、MM110、BM110、蓝牙鼠标、远程控制、移动办公、智能硬件、Oray、贝锐科技、硬件对比 |
| [向日葵五款无网远程控制硬件深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki.md) |  | 2026-07-04 | sunlogin、远程控制、硬件、IPKVM、无网远控、蓝牙、HDMI采集、运维 |
| [向日葵智能插线板P4（4G版）与P1Pro（WiFi版）对比学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md) |  | 2026-07-04 | 向日葵、智能插线板、P4、P1Pro、4G智能插座、WiFi智能插座、远程控制、智能硬件、独立分控、电量监控、Oray、贝锐科技、远程办公 |
| [向日葵智能PDU硬件产品完整学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-pdu-hardware-wiki.md) |  | 2026-07-04 | 向日葵、PDU、智能排插、远程电源管理、IPDU、数据中心、机房运维、远程控制、智能硬件、Oray、贝锐科技 |
| [向日葵远程控制安全产品完整学习教程：国民远控的全流程安全体系深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-security-wiki.md) |  | 2026-07-04 | 向日葵、远程控制、网络安全、等保2.0、国密算法、企业安全、零信任、远控安全 |
| [向日葵智能插座C1Pro/C2/C4完整学习教程：远程开机、电量统计、4G户外三款产品对比与深度洞察](learning/07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md) |  | 2026-07-04 | 向日葵、智能插座、远程开机、C1Pro、C2、C4、蓝牙配网、4G联网、电量统计、智能硬件、Oray、贝锐科技、远程办公 |
| [向日葵三个服务页面系统性学习与深度洞察分析报告](learning/sunlogin-service-pages-analysis.md) | 系统分析向日葵三个服务页面（个人屏幕墙、企业CLI、MCP配置指南）的内容结构、关联性、业务逻辑与设计理念，提炼从"看"到"控"到"AI自主操作"的三层演进路径 | 2026-07-06 | 向日葵、Sunlogin、屏幕墙、CLI、MCP、AweSun、远程控制、AI Agent、服务页面分析、产品演进 |
| [概述与产品核心定位](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/00-overview.md) |  | 2026-07-04 | 概述、产品定位、远程办公、目标用户、应用场景、研究背景 |
| [五大核心功能模块详解](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/01-core-features.md) |  | 2026-07-04 | 核心功能、远程开机、定时开机、双网络接入、批量开机、MAC地址开机、网络拓扑 |
| [技术实现解析与硬件规格](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/02-technology-specs.md) |  | 2026-07-04 | 技术实现、WOL原理、魔术包、网络协议栈、硬件规格、软硬协同架构、四层架构 |
| [K3/K4版本差异与产品策略](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/03-version-strategy.md) |  | 2026-07-04 | 版本差异、K3、K4、产品策略、市场分层、功能对比、定价策略 |
| [网页设计与用户体验分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/04-web-ux-analysis.md) |  | 2026-07-04 | 网页设计、用户体验、UX分析、信息架构、视觉设计、文案策略、交互设计 |
| [竞争优势与市场定位分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/05-competitive-advantage.md) |  | 2026-07-04 | 竞争优势、市场定位、竞品分析、差异化、远程开机、WOL局限、软硬件协同 |
| [深度洞察与行业启示](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/06-insights.md) |  | 2026-07-04 | 深度洞察、行业启示、产品设计、智能硬件、痛点解决、生态协同、商业模式 |
| [潜在改进空间与优化建议](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/07-improvement-suggestions.md) |  | 2026-07-04 | 改进建议、优化方向、功能增强、用户体验、安全性、产品迭代、增值服务 |
| [WOL技术背景知识](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/08-wol-technology.md) |  | 2026-07-04 | WOL技术、网络唤醒、魔术包、Wake-on-LAN、技术历史、BIOS设置、故障排查 |
| [相关资源链接](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/09-resources.md) |  | 2026-07-04 | 相关资源、官方链接、技术文档、参考资料、产品页面、帮助中心、社区支持 |
| [概述与学习目标](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/00-overview.md) |  | 2026-07-04 | 概述、学习目标、产品线全景、无网远控价值、阅读导航、产品定位 |
| [无网远程控制核心技术原理](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/01-core-technology.md) |  | 2026-07-04 | 核心技术、IPKVM、HDMI采集、USB仿真、加密、架构模式、蓝牙配网、4G/5G、BIOS控制 |
| [控控2产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/02-product-kongkong2.md) |  | 2026-07-04 | 控控2、旗舰IPKVM、KVM切换器、BIOS控制、看门狗、多上网方式、企业级、机房运维 |
| [Q1产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/03-product-q1.md) |  | 2026-07-04 | Q1、消费级入门、蓝牙5.0、双唤醒、高性价比、百兆网口、中小企业、远程办公 |
| [Q2Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/04-product-q2pro-ble.md) |  | 2026-07-04 | Q2Pro、工业级4G、4K@60Hz、宽温设计、DIN导轨、双电源、医疗工控、防浪涌、文件传输 |
| [Q0.5产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/05-product-q0.5.md) |  | 2026-07-04 | Q0.5、口袋级近场、物理隔离、完全无网、防跳板、涉密运维、便携、USB取电、应急排障 |
| [Q5Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/06-product-q5pro.md) |  | 2026-07-04 | Q5Pro、专业级5G、双卡5G、协同远控、双向语音、USB映射、远程医疗、手术示教、2.5G网口、葵码登录 |
| [五款产品横向对比分析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/07-comparison.md) |  | 2026-07-04 | 产品对比、25维度对比、产品线梯度、技术演进、技术路线对比、选型参考 |
| [应用场景与选型指南](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/08-scenarios.md) |  | 2026-07-04 | 应用场景、选型指南、决策树、八大场景、产品组合、机房运维、医疗工控、涉密场景、选型速查表 |
| [常见问题解答](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/09-faq.md) |  | 2026-07-04 | FAQ、常见问题、BIOS控制、兼容性、安全加密、分辨率帧率、KVM切换器、流量卡、工业级 |
| [参考资料与链接](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/10-resources.md) |  | 2026-07-04 | 参考资料、官方链接、技术名词、市场报告、相关Wiki、版本信息、术语解释 |
| [discourse-api-research](operations/discourse-api-research.md) |  |  | - |

## 标签索引

### 2.5G网口

- [Q5Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/06-product-q5pro.md)

### 25维度对比

- [五款产品横向对比分析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/07-comparison.md)

### 3d-animation

- [Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！](learning/05-ai-multimodal-content/animejs-threejs-adapter-analysis.md)

### 3d-director

- [LibTV AI 短剧创作工具学习 Wiki](learning/05-ai-multimodal-content/libtv-ai-shortdrama-wiki.md)

### 3d-printing

- [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/05-ai-multimodal-content/text-to-cad-wiki.md)

### 400万像素

- [向日葵USB远程摄像头SU1完整学习教程：400万高清、双全向麦克风、远程视频多面手深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md)

### 4G/5G

- [无网远程控制核心技术原理](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/01-core-technology.md)

### 4G智能插座

- [向日葵智能插线板P4（4G版）与P1Pro（WiFi版）对比学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md)

### 4G联网

- [向日葵智能插座C1Pro/C2/C4完整学习教程：远程开机、电量统计、4G户外三款产品对比与深度洞察](learning/07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md)

### 4K@60Hz

- [Q2Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/04-product-q2pro-ble.md)

### a2a

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/01-agent-protocols-interfaces/agent-communication-protocols-wiki.md)
- [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/00-overview.md)
- [Agent API：可调用方法层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/02-agent-api.md)
- [Agent Protocol：通信规则层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/04-agent-protocol.md)
- [明略科技 Octo 平台学习 Wiki：Private AI 时代的多 Agent 协作基础设施](learning/03-agent-platforms-tools/octo-platform-wiki.md)

### aacr-bench

- [Open Code Review 完整学习教程：阿里开源 AI 代码评审工具](learning/03-agent-platforms-tools/open-code-review-wiki.md)

### abi

- [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/00-overview.md)
- [Agent ABI：跨语言边界层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/03-agent-abi.md)
- [FFI 与相关概念对比](learning/01-agent-protocols-interfaces/ffi-wiki/06-comparison.md)
- [一、概念总览：软件接口的四层抽象](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/00-overview.md)
- [四、ABI（应用二进制接口）：二进制兼容约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/03-abi.md)
- [六、对比分析：四概念系统辨析](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/05-comparison.md)

### abi3

- [从入门到进阶操作指南](learning/04-docs-markup-tooling/scikit-build-core-wiki/04-quickstart-to-advanced.md)

### abstraction-layers

- [六、对比分析：四概念系统辨析](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/05-comparison.md)

### access-denied

- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### acp

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/01-agent-protocols-interfaces/agent-communication-protocols-wiki.md)
- [Agent Protocol：通信规则层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/04-agent-protocol.md)

### adapter-pattern

- [Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！](learning/05-ai-multimodal-content/animejs-threejs-adapter-analysis.md)

### advantages

- [FFI 的优势与局限性](learning/01-agent-protocols-interfaces/ffi-wiki/05-advantages-limitations.md)

### agent

- [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/00-overview.md)
- [Agent Interface：能力契约层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/01-agent-interface.md)
- [Agent API：可调用方法层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/02-agent-api.md)
- [Agent ABI：跨语言边界层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/03-agent-abi.md)
- [Agent Protocol：通信规则层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/04-agent-protocol.md)
- [对比分析：Agent四层技术栈协同](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/05-agent-comparison.md)
- [参考资料与学习路径](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/06-agent-resources.md)
- [Headroom AI Agent上下文压缩中间件完整学习教程](learning/02-agent-engineering-methodology/headroom-context-compression-wiki.md)
- [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)
- [LongCat-2.0 Agent能力实测Wiki教程](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki.md)
- [Karpathy LLM 编程准则：概述与背景](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/00-overview.md)
- [四条核心原则详解](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/01-four-principles.md)
- [真实代码正反例](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/02-code-examples.md)
- [快速上手指南](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/03-quickstart.md)
- [SpecWeave 项目整合情况](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/04-specweave-integration.md)
- [资源与参考链接](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/05-resources.md)
- [Multica 平台：AI Agent 协作管理平台](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/06-multica-platform.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)
- [Anthropic Agent 产品线路线图完整学习教程：Conway永久在线智能体、文件记忆、Orbit主动助手、Operon科研平台、BugCrawl代码审计与GPT-5.6竞争分析](learning/03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md)
- [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md)
- [Open Code Review 完整学习教程：阿里开源 AI 代码评审工具](learning/03-agent-platforms-tools/open-code-review-wiki.md)
- [Claude Tag：文章概述](learning/03-agent-platforms-tools/claude-tag-article/00-overview.md)
- [Claude Tag：核心观点](learning/03-agent-platforms-tools/claude-tag-article/01-core-insights.md)
- [Agnes AI 与 Pavo 创作平台完整学习教程：免费多模态API+一站式AI短剧工作流](learning/05-ai-multimodal-content/agnes-pavo-creative-platform-wiki.md)

### Agent Engineering

- [Harness Engineering（驾驭工程）系统性学习Wiki](learning/02-agent-engineering-methodology/harness-engineering-wiki.md)

### agent-collaboration

- [明略科技 Octo 平台学习 Wiki：Private AI 时代的多 Agent 协作基础设施](learning/03-agent-platforms-tools/octo-platform-wiki.md)

### agent-framework

- [The Agency 项目完整学习教程](learning/03-agent-platforms-tools/the-agency-project-wiki.md)

### agent-gateway

- [QuantDinger：开源AI量化交易基础设施层完整教程](learning/03-agent-platforms-tools/quantdinger-ai-trading-wiki.md)

### agent-infrastructure

- [AReaL 2.0 自演进 Agent 在线强化学习基础设施学习 Wiki](learning/03-agent-platforms-tools/areal-agent-rl-wiki.md)

### agent-protocol

- [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md)

### agent-protocols

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/01-agent-protocols-interfaces/agent-communication-protocols-wiki.md)

### agent-runtime

- [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md)

### agent-skills

- [Agent Skills 开放标准完整指南](learning/01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md)
- [三个热门AI工具完整指南：微软AI终端、Claudian笔记插件、book-to-skill书籍转Skill](learning/06-business-trends-analysis/three-ai-tools-wiki.md)
- [TuyaOpen-dev-skills 学习笔记](learning/07-vendor-product-learning/tuya/tuyaopen-dev-skills-learning.md)

### agent-trajectory

- [AReaL 2.0 自演进 Agent 在线强化学习基础设施学习 Wiki](learning/03-agent-platforms-tools/areal-agent-rl-wiki.md)

### agentforge

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### agentic-engineering

- [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)
- [Karpathy LLM 编程准则：概述与背景](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/00-overview.md)
- [Multica 平台：AI Agent 协作管理平台](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/06-multica-platform.md)

### agentic-rl

- [AReaL 2.0 自演进 Agent 在线强化学习基础设施学习 Wiki](learning/03-agent-platforms-tools/areal-agent-rl-wiki.md)

### agents

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### agnes-ai

- [Agnes AI 与 Pavo 创作平台完整学习教程：免费多模态API+一站式AI短剧工作流](learning/05-ai-multimodal-content/agnes-pavo-creative-platform-wiki.md)

### ai

- [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md)

### AI Agent

- [Harness Engineering（驾驭工程）系统性学习Wiki](learning/02-agent-engineering-methodology/harness-engineering-wiki.md)
- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)

### ai-agent

- [Agent Skills 开放标准完整指南](learning/01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md)
- [国内 Skill/MCP 生态盘点：16 个品牌的 Agent 化浪潮](learning/01-agent-protocols-interfaces/domestic-skill-mcp-ecosystem-wiki.md)
- [AI 四大工程概念演进：Prompt → Context → Harness → Loop](learning/02-agent-engineering-methodology/four-engineering-concepts-wiki.md)
- [Headroom AI Agent上下文压缩中间件完整学习教程](learning/02-agent-engineering-methodology/headroom-context-compression-wiki.md)
- [Vibe Coding 两大神级 Prompt](learning/02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md)
- [Anthropic Agent 产品线路线图完整学习教程：Conway永久在线智能体、文件记忆、Orbit主动助手、Operon科研平台、BugCrawl代码审计与GPT-5.6竞争分析](learning/03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md)
- [Anthropic Financial Services 完整教程：华尔街的AI金融Agent工具箱](learning/03-agent-platforms-tools/anthropic-financial-services-wiki.md)
- [BrowserAct 完整学习教程：让Agent真正能操作浏览器的自动化工具](learning/03-agent-platforms-tools/browseract-wiki.md)
- [EchoBird 百灵鸟项目学习 Wiki 教程](learning/03-agent-platforms-tools/echobird-wiki.md)
- [The Agency 项目完整学习教程](learning/03-agent-platforms-tools/the-agency-project-wiki.md)
- [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/05-ai-multimodal-content/text-to-cad-wiki.md)
- [国产AI模型对比与使用场景推荐](learning/06-business-trends-analysis/domestic-llm-comparison-notes.md)
- [三个热门AI工具完整指南：微软AI终端、Claudian笔记插件、book-to-skill书籍转Skill](learning/06-business-trends-analysis/three-ai-tools-wiki.md)

### ai-code-review

- [Open Code Review 完整学习教程：阿里开源 AI 代码评审工具](learning/03-agent-platforms-tools/open-code-review-wiki.md)

### ai-coding

- [LongCat-2.0 Agent能力实测Wiki教程](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki.md)

### ai-manhua

- [LibTV AI 短剧创作工具学习 Wiki](learning/05-ai-multimodal-content/libtv-ai-shortdrama-wiki.md)

### ai-monetization

- [AI变现完整指南：从技术到商业的全流程方法论](learning/06-business-trends-analysis/ai-monetization-wiki/00-overview.md)
- [核心概念界定：AI变现术语体系](learning/06-business-trends-analysis/ai-monetization-wiki/01-core-concepts.md)
- [市场需求分析：识别与评估AI商业化机会](learning/06-business-trends-analysis/ai-monetization-wiki/02-market-analysis.md)
- [商业模式设计：AI产品的盈利模式选择](learning/06-business-trends-analysis/ai-monetization-wiki/03-business-models.md)
- [技术选型：AI技术栈决策框架](learning/06-business-trends-analysis/ai-monetization-wiki/04-tech-selection.md)
- [产品开发：AI产品的构建与迭代流程](learning/06-business-trends-analysis/ai-monetization-wiki/05-product-development.md)
- [市场推广：AI产品的GTM策略](learning/06-business-trends-analysis/ai-monetization-wiki/06-marketing-strategy.md)
- [盈利策略：定价模型与规模化路径](learning/06-business-trends-analysis/ai-monetization-wiki/07-profitability-strategy.md)
- [企业服务场景：ToB AI应用变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/08-scenario-enterprise.md)
- [消费级产品场景：ToC AI应用变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/09-scenario-consumer.md)
- [行业解决方案场景：垂直行业AI变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/10-scenario-industry.md)
- [实施步骤与关键成功因素](learning/06-business-trends-analysis/ai-monetization-wiki/11-implementation-steps.md)
- [风险提示与资源推荐](learning/06-business-trends-analysis/ai-monetization-wiki/12-risks-resources.md)

### ai-programming

- [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)
- [Karpathy LLM 编程准则：概述与背景](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/00-overview.md)

### ai-shortdrama

- [Agnes AI 与 Pavo 创作平台完整学习教程：免费多模态API+一站式AI短剧工作流](learning/05-ai-multimodal-content/agnes-pavo-creative-platform-wiki.md)
- [LibTV AI 短剧创作工具学习 Wiki](learning/05-ai-multimodal-content/libtv-ai-shortdrama-wiki.md)

### ai-tools

- [三个热门AI工具完整指南：微软AI终端、Claudian笔记插件、book-to-skill书籍转Skill](learning/06-business-trends-analysis/three-ai-tools-wiki.md)

### ai-trading

- [QuantDinger：开源AI量化交易基础设施层完整教程](learning/03-agent-platforms-tools/quantdinger-ai-trading-wiki.md)

### ai-video

- [Agnes AI 与 Pavo 创作平台完整学习教程：免费多模态API+一站式AI短剧工作流](learning/05-ai-multimodal-content/agnes-pavo-creative-platform-wiki.md)
- [LibTV AI 短剧创作工具学习 Wiki](learning/05-ai-multimodal-content/libtv-ai-shortdrama-wiki.md)

### aigc

- [Agnes AI 与 Pavo 创作平台完整学习教程：免费多模态API+一站式AI短剧工作流](learning/05-ai-multimodal-content/agnes-pavo-creative-platform-wiki.md)

### AIGC营销

- [火山引擎KickArt一站式电商营销创作Agent完整学习笔记：六大能力+四大场景+全链路闭环的营销视频生产平台](learning/06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md)

### aihot

- [Vibe Coding 两大神级 Prompt](learning/02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md)

### AI开源

- [AudioX-Turbo 极速音频生成完整学习教程：4步推理+6种任务统一+920万数据集的Anything-to-Audio框架](learning/05-ai-multimodal-content/audiox-turbo-audio-generation-wiki.md)

### AI执行基础设施

- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)

### AI视频生成

- [火山引擎KickArt一站式电商营销创作Agent完整学习笔记：六大能力+四大场景+全链路闭环的营销视频生产平台](learning/06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md)

### algorithm

- [技术选型：AI技术栈决策框架](learning/06-business-trends-analysis/ai-monetization-wiki/04-tech-selection.md)

### alibaba

- [Open Code Review 完整学习教程：阿里开源 AI 代码评审工具](learning/03-agent-platforms-tools/open-code-review-wiki.md)

### always-on-agent

- [Anthropic Agent 产品线路线图完整学习教程：Conway永久在线智能体、文件记忆、Orbit主动助手、Operon科研平台、BugCrawl代码审计与GPT-5.6竞争分析](learning/03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md)

### ambient-mode

- [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md)
- [Claude Tag：核心观点](learning/03-agent-platforms-tools/claude-tag-article/01-core-insights.md)
- [Claude Tag：关键概念与术语](learning/03-agent-platforms-tools/claude-tag-article/02-key-concepts.md)

### animejs

- [Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！](learning/05-ai-multimodal-content/animejs-threejs-adapter-analysis.md)

### annotations

- [二、IDL 类型系统：基本数据类型与注解机制](learning/01-agent-protocols-interfaces/idl-wiki/02-syntax-types.md)

### anp

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/01-agent-protocols-interfaces/agent-communication-protocols-wiki.md)
- [Agent Protocol：通信规则层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/04-agent-protocol.md)

### ant-group

- [AReaL 2.0 自演进 Agent 在线强化学习基础设施学习 Wiki](learning/03-agent-platforms-tools/areal-agent-rl-wiki.md)

### anthropic

- [Anthropic Agent 产品线路线图完整学习教程：Conway永久在线智能体、文件记忆、Orbit主动助手、Operon科研平台、BugCrawl代码审计与GPT-5.6竞争分析](learning/03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md)
- [Anthropic Financial Services 完整教程：华尔街的AI金融Agent工具箱](learning/03-agent-platforms-tools/anthropic-financial-services-wiki.md)
- [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md)
- [Claude Tag：文章概述](learning/03-agent-platforms-tools/claude-tag-article/00-overview.md)
- [Claude Tag：核心观点](learning/03-agent-platforms-tools/claude-tag-article/01-core-insights.md)
- [Claude Tag：关键概念与术语](learning/03-agent-platforms-tools/claude-tag-article/02-key-concepts.md)
- [Claude Tag：重要数据](learning/03-agent-platforms-tools/claude-tag-article/03-key-data.md)
- [Claude Tag：原文结构框架](learning/03-agent-platforms-tools/claude-tag-article/04-article-structure.md)
- [Claude Tag：参考链接](learning/03-agent-platforms-tools/claude-tag-article/07-resources.md)

### anti-patterns

- [真实代码正反例](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/02-code-examples.md)

### Anything-to-Audio

- [AudioX-Turbo 极速音频生成完整学习教程：4步推理+6种任务统一+920万数据集的Anything-to-Audio框架](learning/05-ai-multimodal-content/audiox-turbo-audio-generation-wiki.md)

### api

- [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/00-overview.md)
- [Agent API：可调用方法层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/02-agent-api.md)
- [FFI 与相关概念对比](learning/01-agent-protocols-interfaces/ffi-wiki/06-comparison.md)
- [一、概念总览：软件接口的四层抽象](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/00-overview.md)
- [三、API（应用编程接口）：源码与服务级契约](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/02-api.md)
- [六、对比分析：四概念系统辨析](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/05-comparison.md)
- [核心 API 使用与配置详解](learning/04-docs-markup-tooling/scikit-build-core-wiki/03-core-api-and-config.md)

### architecture

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)
- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)
- [对比分析：Agent四层技术栈协同](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/05-agent-comparison.md)
- [一、概念总览：软件接口的四层抽象](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/00-overview.md)
- [六、对比分析：四概念系统辨析](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/05-comparison.md)
- [基本概念与架构解析](learning/04-docs-markup-tooling/scikit-build-core-wiki/01-concepts-architecture.md)
- [WSL CLI 命令树与架构 Wiki 参考手册](learning/08-systems-infrastructure/wsl-cli-and-architecture-wiki.md)

### areal

- [AReaL 2.0 自演进 Agent 在线强化学习基础设施学习 Wiki](learning/03-agent-platforms-tools/areal-agent-rl-wiki.md)

### argument-definitions

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/08-systems-infrastructure/wsl-cli-and-architecture-wiki.md)

### artifact

- [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md)

### asyncapi

- [八、与现代接口描述方式对比：从 RPC IDL 到 Web IDL 与 AI-friendly IDL](learning/01-agent-protocols-interfaces/idl-wiki/08-vs-modern-formats.md)

### AudioX-Turbo

- [AudioX-Turbo 极速音频生成完整学习教程：4步推理+6种任务统一+920万数据集的Anything-to-Audio框架](learning/05-ai-multimodal-content/audiox-turbo-audio-generation-wiki.md)

### autogen

- [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md)

### autopilot

- [Multica 平台：AI Agent 协作管理平台](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/06-multica-platform.md)

### avro

- [四、主要 IDL 规范介绍：五大主流实现详解](learning/01-agent-protocols-interfaces/idl-wiki/04-major-idl-specs.md)
- [五、IDL 规范对比](learning/01-agent-protocols-interfaces/idl-wiki/05-comparison.md)

### B2B产品

- [B2B/旗舰产品信息源分层采集规范](best-practices/b2b-product-info-collection-sop.md)

### batch-upgrade

- [方法论模式第3次验证报告：模板批量升级场景](best-practices/pattern-validation-v3-template-batch-upgrade.md)

### bazel

- [六、IDL 编译流程与工具链：从源文件到多语言桩代码](learning/01-agent-protocols-interfaces/idl-wiki/06-toolchain.md)

### best-practices

- [实际应用案例与代码示例](learning/01-agent-protocols-interfaces/ffi-wiki/04-use-cases.md)
- [七、实际应用案例与最佳实践：IDL 在生产环境的落地](learning/01-agent-protocols-interfaces/idl-wiki/07-use-cases.md)
- [编译构建与项目集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/11-build-and-integration.md)
- [完整实战示例](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/12-examples.md)
- [最佳实践与性能优化](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/13-best-practices.md)
- [常见问题解答 (FAQ)](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/14-faq.md)
- [参考资料与学习路径](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/15-resources.md)
- [常见问题与最佳实践](learning/04-docs-markup-tooling/scikit-build-core-wiki/05-faq-and-best-practices.md)

### binary-compatibility

- [四、ABI（应用二进制接口）：二进制兼容约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/03-abi.md)

### binding

- [FFI 工作原理](learning/01-agent-protocols-interfaces/ffi-wiki/02-working-principles.md)

### binfmt

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/08-systems-infrastructure/wsl-cli-and-architecture-wiki.md)

### BIOS控制

- [无网远程控制核心技术原理](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/01-core-technology.md)
- [控控2产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/02-product-kongkong2.md)
- [常见问题解答](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/09-faq.md)

### BIOS设置

- [WOL技术背景知识](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/08-wol-technology.md)

### BM110

- [向日葵智能远控鼠标MM110/BM110产品学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-mouse-bm110-mm110-analysis.md)

### book-to-skill

- [三个热门AI工具完整指南：微软AI终端、Claudian笔记插件、book-to-skill书籍转Skill](learning/06-business-trends-analysis/three-ai-tools-wiki.md)

### books

- [七、参考资料与扩展阅读](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/06-resources.md)

### bottleneck-shift

- [AI 四大工程概念演进：Prompt → Context → Harness → Loop](learning/02-agent-engineering-methodology/four-engineering-concepts-wiki.md)

### browser

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### browser-automation

- [BrowserAct 完整学习教程：让Agent真正能操作浏览器的自动化工具](learning/03-agent-platforms-tools/browseract-wiki.md)

### browseract

- [BrowserAct 完整学习教程：让Agent真正能操作浏览器的自动化工具](learning/03-agent-platforms-tools/browseract-wiki.md)

### bugcrawl

- [Anthropic Agent 产品线路线图完整学习教程：Conway永久在线智能体、文件记忆、Orbit主动助手、Operon科研平台、BugCrawl代码审计与GPT-5.6竞争分析](learning/03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md)

### build

- [编译构建与项目集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/11-build-and-integration.md)
- [完整实战示例](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/12-examples.md)
- [最佳实践与性能优化](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/13-best-practices.md)
- [常见问题解答 (FAQ)](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/14-faq.md)
- [参考资料与学习路径](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/15-resources.md)

### build123d

- [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/05-ai-multimodal-content/text-to-cad-wiki.md)

### business

- [AI变现完整指南：从技术到商业的全流程方法论](learning/06-business-trends-analysis/ai-monetization-wiki/00-overview.md)

### business-model

- [商业模式设计：AI产品的盈利模式选择](learning/06-business-trends-analysis/ai-monetization-wiki/03-business-models.md)

### c

- [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md)

### C1Pro

- [向日葵智能插座C1Pro/C2/C4完整学习教程：远程开机、电量统计、4G户外三款产品对比与深度洞察](learning/07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md)

### C2

- [向日葵智能插座C1Pro/C2/C4完整学习教程：远程开机、电量统计、4G户外三款产品对比与深度洞察](learning/07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md)

### C4

- [向日葵智能插座C1Pro/C2/C4完整学习教程：远程开机、电量统计、4G户外三款产品对比与深度洞察](learning/07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md)

### cad

- [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/05-ai-multimodal-content/text-to-cad-wiki.md)

### calling-convention

- [FFI 工作原理](learning/01-agent-protocols-interfaces/ffi-wiki/02-working-principles.md)
- [四、ABI（应用二进制接口）：二进制兼容约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/03-abi.md)

### canvas

- [商业模式设计：AI产品的盈利模式选择](learning/06-business-trends-analysis/ai-monetization-wiki/03-business-models.md)

### cascading-renumber

- [多文件编辑操作可靠性指南](best-practices/multi-file-edit-reliability.md)

### categories

- [Learning Wiki 主题分类体系](learning/CATEGORIES.md)

### ccr

- [Headroom AI Agent上下文压缩中间件完整学习教程](learning/02-agent-engineering-methodology/headroom-context-compression-wiki.md)

### channel

- [市场推广：AI产品的GTM策略](learning/06-business-trends-analysis/ai-monetization-wiki/06-marketing-strategy.md)

### character-quality

- [LibTV AI 短剧创作工具学习 Wiki](learning/05-ai-multimodal-content/libtv-ai-shortdrama-wiki.md)

### chcp

- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### check-mermaid

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### checklist

- [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md)

### checkpoint

- [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md)

### chrome

- [Declarative Partial Updates 完整教程：HTML 声明式局部更新能力解析](learning/04-docs-markup-tooling/declarative-partial-updates-wiki.md)

### ci

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)
- [常见问题与最佳实践](learning/04-docs-markup-tooling/scikit-build-core-wiki/05-faq-and-best-practices.md)
- [TuyaOpen-dev-skills 学习笔记](learning/07-vendor-product-learning/tuya/tuyaopen-dev-skills-learning.md)

### classification-disposition

- [方法论模式第3次验证报告：模板批量升级场景](best-practices/pattern-validation-v3-template-batch-upgrade.md)

### claude

- [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)
- [Karpathy LLM 编程准则：概述与背景](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/00-overview.md)
- [Anthropic Agent 产品线路线图完整学习教程：Conway永久在线智能体、文件记忆、Orbit主动助手、Operon科研平台、BugCrawl代码审计与GPT-5.6竞争分析](learning/03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md)
- [Anthropic Financial Services 完整教程：华尔街的AI金融Agent工具箱](learning/03-agent-platforms-tools/anthropic-financial-services-wiki.md)
- [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md)
- [Claude Tag：文章概述](learning/03-agent-platforms-tools/claude-tag-article/00-overview.md)
- [Claude Tag：核心观点](learning/03-agent-platforms-tools/claude-tag-article/01-core-insights.md)
- [Claude Tag：关键概念与术语](learning/03-agent-platforms-tools/claude-tag-article/02-key-concepts.md)
- [Claude Tag：重要数据](learning/03-agent-platforms-tools/claude-tag-article/03-key-data.md)
- [Claude Tag：原文结构框架](learning/03-agent-platforms-tools/claude-tag-article/04-article-structure.md)
- [Claude Tag：与 SpecWeave 的关联](learning/03-agent-platforms-tools/claude-tag-article/05-specweave-relevance.md)
- [Claude Tag：知识沉淀闭环](learning/03-agent-platforms-tools/claude-tag-article/06-knowledge-closure.md)
- [Claude Tag：参考链接](learning/03-agent-platforms-tools/claude-tag-article/07-resources.md)
- [TuyaOpen-dev-skills 学习笔记](learning/07-vendor-product-learning/tuya/tuyaopen-dev-skills-learning.md)

### claude-code

- [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)
- [LongCat-2.0 Agent能力实测Wiki教程](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki.md)
- [快速上手指南](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/03-quickstart.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)
- [EchoBird 百灵鸟项目学习 Wiki 教程](learning/03-agent-platforms-tools/echobird-wiki.md)
- [The Agency 项目完整学习教程](learning/03-agent-platforms-tools/the-agency-project-wiki.md)
- [三个热门AI工具完整指南：微软AI终端、Claudian笔记插件、book-to-skill书籍转Skill](learning/06-business-trends-analysis/three-ai-tools-wiki.md)

### claude-sdk

- [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md)

### claudian

- [三个热门AI工具完整指南：微软AI终端、Claudian笔记插件、book-to-skill书籍转Skill](learning/06-business-trends-analysis/three-ai-tools-wiki.md)

### cli

- [国内 Skill/MCP 生态盘点：16 个品牌的 Agent 化浪潮](learning/01-agent-protocols-interfaces/domestic-skill-mcp-ecosystem-wiki.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)
- [Open Code Review 完整学习教程：阿里开源 AI 代码评审工具](learning/03-agent-platforms-tools/open-code-review-wiki.md)
- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/07-vendor-product-learning/tuya/tuyaopen-folder-learning-path.md)
- [WSL CLI 命令树与架构 Wiki 参考手册](learning/08-systems-infrastructure/wsl-cli-and-architecture-wiki.md)

### client-implementation

- [Agent Skills 开放标准完整指南](learning/01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md)

### cloud

- [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md)

### cmake

- [scikit-build-core 全面教程：概述与导航](learning/04-docs-markup-tooling/scikit-build-core-wiki/00-overview.md)
- [基本概念与架构解析](learning/04-docs-markup-tooling/scikit-build-core-wiki/01-concepts-architecture.md)
- [从入门到进阶操作指南](learning/04-docs-markup-tooling/scikit-build-core-wiki/04-quickstart-to-advanced.md)
- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### cmd

- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### code-examples

- [实际应用案例与代码示例](learning/01-agent-protocols-interfaces/ffi-wiki/04-use-cases.md)

### code-quality

- [Open Code Review 完整学习教程：阿里开源 AI 代码评审工具](learning/03-agent-platforms-tools/open-code-review-wiki.md)

### codegen

- [六、IDL 编译流程与工具链：从源文件到多语言桩代码](learning/01-agent-protocols-interfaces/idl-wiki/06-toolchain.md)

### codex

- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)
- [EchoBird 百灵鸟项目学习 Wiki 教程](learning/03-agent-platforms-tools/echobird-wiki.md)

### coding

- [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)
- [Karpathy LLM 编程准则：概述与背景](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/00-overview.md)
- [四条核心原则详解](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/01-four-principles.md)
- [真实代码正反例](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/02-code-examples.md)
- [快速上手指南](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/03-quickstart.md)
- [SpecWeave 项目整合情况](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/04-specweave-integration.md)
- [资源与参考链接](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/05-resources.md)
- [Multica 平台：AI Agent 协作管理平台](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/06-multica-platform.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)
- [国产AI模型对比与使用场景推荐](learning/06-business-trends-analysis/domestic-llm-comparison-notes.md)

### cold-start

- [市场推广：AI产品的GTM策略](learning/06-business-trends-analysis/ai-monetization-wiki/06-marketing-strategy.md)

### com

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/08-systems-infrastructure/wsl-cli-and-architecture-wiki.md)
- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### com-idl

- [四、主要 IDL 规范介绍：五大主流实现详解](learning/01-agent-protocols-interfaces/idl-wiki/04-major-idl-specs.md)

### command-tree

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/08-systems-infrastructure/wsl-cli-and-architecture-wiki.md)

### commercialization

- [AI变现完整指南：从技术到商业的全流程方法论](learning/06-business-trends-analysis/ai-monetization-wiki/00-overview.md)

### communication

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/01-agent-protocols-interfaces/agent-communication-protocols-wiki.md)

### comparison

- [对比分析：Agent四层技术栈协同](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/05-agent-comparison.md)
- [FFI 与相关概念对比](learning/01-agent-protocols-interfaces/ffi-wiki/06-comparison.md)
- [五、IDL 规范对比](learning/01-agent-protocols-interfaces/idl-wiki/05-comparison.md)
- [八、与现代接口描述方式对比：从 RPC IDL 到 Web IDL 与 AI-friendly IDL](learning/01-agent-protocols-interfaces/idl-wiki/08-vs-modern-formats.md)
- [六、对比分析：四概念系统辨析](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/05-comparison.md)

### compiler

- [六、IDL 编译流程与工具链：从源文件到多语言桩代码](learning/01-agent-protocols-interfaces/idl-wiki/06-toolchain.md)

### compliance

- [风险提示与资源推荐](learning/06-business-trends-analysis/ai-monetization-wiki/12-risks-resources.md)

### compute

- [技术选型：AI技术栈决策框架](learning/06-business-trends-analysis/ai-monetization-wiki/04-tech-selection.md)

### concept

- [一、IDL 定义与作用：接口契约的语言中立描述](learning/01-agent-protocols-interfaces/idl-wiki/01-what-is-idl.md)

### concepts

- [核心概念界定：AI变现术语体系](learning/06-business-trends-analysis/ai-monetization-wiki/01-core-concepts.md)

### conda

- [常见问题与最佳实践](learning/04-docs-markup-tooling/scikit-build-core-wiki/05-faq-and-best-practices.md)

### configuration

- [核心 API 使用与配置详解](learning/04-docs-markup-tooling/scikit-build-core-wiki/03-core-api-and-config.md)

### consumer

- [消费级产品场景：ToC AI应用变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/09-scenario-consumer.md)

### container

- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### Context Engineering

- [Harness Engineering（驾驭工程）系统性学习Wiki](learning/02-agent-engineering-methodology/harness-engineering-wiki.md)

### context-compression

- [Headroom AI Agent上下文压缩中间件完整学习教程](learning/02-agent-engineering-methodology/headroom-context-compression-wiki.md)

### context-engineering

- [AI 四大工程概念演进：Prompt → Context → Harness → Loop](learning/02-agent-engineering-methodology/four-engineering-concepts-wiki.md)

### convention

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)

### conway

- [Anthropic Agent 产品线路线图完整学习教程：Conway永久在线智能体、文件记忆、Orbit主动助手、Operon科研平台、BugCrawl代码审计与GPT-5.6竞争分析](learning/03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md)

### corba

- [IDL（接口定义语言）Wiki 教程 - 总览](learning/01-agent-protocols-interfaces/idl-wiki/00-overview.md)
- [四、主要 IDL 规范介绍：五大主流实现详解](learning/01-agent-protocols-interfaces/idl-wiki/04-major-idl-specs.md)
- [五、IDL 规范对比](learning/01-agent-protocols-interfaces/idl-wiki/05-comparison.md)
- [七、实际应用案例与最佳实践：IDL 在生产环境的落地](learning/01-agent-protocols-interfaces/idl-wiki/07-use-cases.md)

### corba-idl

- [二、IDL 类型系统：基本数据类型与注解机制](learning/01-agent-protocols-interfaces/idl-wiki/02-syntax-types.md)
- [三、IDL 接口声明与方法描述：服务契约的通用范式](learning/01-agent-protocols-interfaces/idl-wiki/03-syntax-interface.md)

### core-api

- [02 - C++ 核心 API：Any、Object、Function、Tensor](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/02-cpp-core-api.md)
- [03 - 类型系统：DType、Enum、Optional、String](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/03-type-system.md)
- [04 - 容器类型：Array、Map、Dict、List、Tuple、Shape、Variant](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/04-containers.md)
- [05 - 反射与注册机制](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/05-reflection.md)
- [06 - 序列化：JSON、Base64、结构相等与哈希](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/06-serialization.md)

### core-concepts

- [FFI 定义与核心概念](learning/01-agent-protocols-interfaces/ffi-wiki/01-what-is-ffi.md)

### cpp

- [Ch00 - TVM FFI 概述与定位](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/00-overview.md)
- [Ch01 - 系统架构与设计理念](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/01-architecture.md)
- [02 - C++ 核心 API：Any、Object、Function、Tensor](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/02-cpp-core-api.md)
- [03 - 类型系统：DType、Enum、Optional、String](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/03-type-system.md)
- [04 - 容器类型：Array、Map、Dict、List、Tuple、Shape、Variant](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/04-containers.md)
- [05 - 反射与注册机制](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/05-reflection.md)
- [06 - 序列化：JSON、Base64、结构相等与哈希](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/06-serialization.md)
- [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md)

### creative-platform

- [Agnes AI 与 Pavo 创作平台完整学习教程：免费多模态API+一站式AI短剧工作流](learning/05-ai-multimodal-content/agnes-pavo-creative-platform-wiki.md)

### cross-language

- [Agent ABI：跨语言边界层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/03-agent-abi.md)
- [Ch00 - TVM FFI 概述与定位](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/00-overview.md)
- [Ch01 - 系统架构与设计理念](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/01-architecture.md)

### csharp

- [不同编程语言中的 FFI 实现](learning/01-agent-protocols-interfaces/ffi-wiki/03-language-implementations.md)

### cuda

- [07 - Python 绑定机制](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/07-python-bindings.md)
- [08 - CUDA 支持](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/08-cuda-support.md)
- [09 - ORCJIT 扩展](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/09-orcjit-extension.md)
- [10 - DLPack 集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/10-dlpack-integration.md)

### curriculum

- [Learning Wiki 学习路径推荐表](learning/LEARNING-PATHS.md)

### cursor

- [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)
- [快速上手指南](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/03-quickstart.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)
- [The Agency 项目完整学习教程](learning/03-agent-platforms-tools/the-agency-project-wiki.md)
- [TuyaOpen-dev-skills 学习笔记](learning/07-vendor-product-learning/tuya/tuyaopen-dev-skills-learning.md)

### customization

- [企业服务场景：ToB AI应用变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/08-scenario-enterprise.md)

### daemon

- [Multica 平台：AI Agent 协作管理平台](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/06-multica-platform.md)

### data-flywheel

- [产品开发：AI产品的构建与迭代流程](learning/06-business-trends-analysis/ai-monetization-wiki/05-product-development.md)

### data-strategy

- [技术选型：AI技术栈决策框架](learning/06-business-trends-analysis/ai-monetization-wiki/04-tech-selection.md)

### decision-guide

- [对比分析：Agent四层技术栈协同](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/05-agent-comparison.md)

### decision-tree

- [五、IDL 规范对比](learning/01-agent-protocols-interfaces/idl-wiki/05-comparison.md)

### declarative-partial-updates

- [Declarative Partial Updates 完整教程：HTML 声明式局部更新能力解析](learning/04-docs-markup-tooling/declarative-partial-updates-wiki.md)

### declarative-shadow-dom

- [Declarative Partial Updates 完整教程：HTML 声明式局部更新能力解析](learning/04-docs-markup-tooling/declarative-partial-updates-wiki.md)

### deepseek

- [国产AI模型对比与使用场景推荐](learning/06-business-trends-analysis/domestic-llm-comparison-notes.md)

### definition

- [FFI 定义与核心概念](learning/01-agent-protocols-interfaces/ffi-wiki/01-what-is-ffi.md)
- [一、IDL 定义与作用：接口契约的语言中立描述](learning/01-agent-protocols-interfaces/idl-wiki/01-what-is-idl.md)

### Defuddle

- [B2B/旗舰产品信息源分层采集规范](best-practices/b2b-product-info-collection-sop.md)

### defuddle

- [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md)

### deployment

- [技术选型：AI技术栈决策框架](learning/06-business-trends-analysis/ai-monetization-wiki/04-tech-selection.md)

### desktop-tool

- [EchoBird 百灵鸟项目学习 Wiki 教程](learning/03-agent-platforms-tools/echobird-wiki.md)

### devops

- [Open Code Review 完整学习教程：阿里开源 AI 代码评审工具](learning/03-agent-platforms-tools/open-code-review-wiki.md)

### diagnostics

- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### dingtalk

- [国内 Skill/MCP 生态盘点：16 个品牌的 Agent 化浪潮](learning/01-agent-protocols-interfaces/domestic-skill-mcp-ecosystem-wiki.md)

### DIN导轨

- [Q2Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/04-product-q2pro-ble.md)

### directory

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### dirty

- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### discourse

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### Distribution-Matching-Distillation

- [AudioX-Turbo 极速音频生成完整学习教程：4步推理+6种任务统一+920万数据集的Anything-to-Audio框架](learning/05-ai-multimodal-content/audiox-turbo-audio-generation-wiki.md)

### dlpack

- [07 - Python 绑定机制](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/07-python-bindings.md)
- [08 - CUDA 支持](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/08-cuda-support.md)
- [09 - ORCJIT 扩展](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/09-orcjit-extension.md)
- [10 - DLPack 集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/10-dlpack-integration.md)

### docker

- [QuantDinger：开源AI量化交易基础设施层完整教程](learning/03-agent-platforms-tools/quantdinger-ai-trading-wiki.md)

### docs

- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)

### domestic

- [国内 Skill/MCP 生态盘点：16 个品牌的 Agent 化浪潮](learning/01-agent-protocols-interfaces/domestic-skill-mcp-ecosystem-wiki.md)

### domestic-model

- [国产AI模型对比与使用场景推荐](learning/06-business-trends-analysis/domestic-llm-comparison-notes.md)

### drvfs

- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### duck-typing

- [二、接口（Interface）：语言级行为抽象](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/01-interface.md)

### echobird

- [EchoBird 百灵鸟项目学习 Wiki 教程](learning/03-agent-platforms-tools/echobird-wiki.md)

### ecosystem

- [国内 Skill/MCP 生态盘点：16 个品牌的 Agent 化浪潮](learning/01-agent-protocols-interfaces/domestic-skill-mcp-ecosystem-wiki.md)
- [参考资料与扩展阅读](learning/04-docs-markup-tooling/scikit-build-core-wiki/06-resources.md)

### edit

- [多文件编辑操作可靠性指南](best-practices/multi-file-edit-reliability.md)

### education

- [行业解决方案场景：垂直行业AI变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/10-scenario-industry.md)

### embedded

- [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md)
- [TuyaOpen-dev-skills 学习笔记](learning/07-vendor-product-learning/tuya/tuyaopen-dev-skills-learning.md)
- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/07-vendor-product-learning/tuya/tuyaopen-folder-learning-path.md)

### emotion-control

- [LibTV AI 短剧创作工具学习 Wiki](learning/05-ai-multimodal-content/libtv-ai-shortdrama-wiki.md)

### encoding

- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)
- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### enterprise

- [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md)
- [Claude Tag：文章概述](learning/03-agent-platforms-tools/claude-tag-article/00-overview.md)
- [Claude Tag：核心观点](learning/03-agent-platforms-tools/claude-tag-article/01-core-insights.md)
- [企业服务场景：ToB AI应用变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/08-scenario-enterprise.md)

### error-codes

- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### error-recovery

- [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md)

### esp32

- [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md)

### evaluation

- [产品开发：AI产品的构建与迭代流程](learning/06-business-trends-analysis/ai-monetization-wiki/05-product-development.md)

### event

- [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md)

### examples

- [七、实际应用案例与最佳实践：IDL 在生产环境的落地](learning/01-agent-protocols-interfaces/idl-wiki/07-use-cases.md)
- [编译构建与项目集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/11-build-and-integration.md)
- [完整实战示例](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/12-examples.md)
- [最佳实践与性能优化](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/13-best-practices.md)
- [常见问题解答 (FAQ)](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/14-faq.md)
- [参考资料与学习路径](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/15-resources.md)
- [真实代码正反例](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/02-code-examples.md)

### external-agent

- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)

### fable

- [Claude Tag：关键概念与术语](learning/03-agent-platforms-tools/claude-tag-article/02-key-concepts.md)
- [Claude Tag：原文结构框架](learning/03-agent-platforms-tools/claude-tag-article/04-article-structure.md)

### faq

- [编译构建与项目集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/11-build-and-integration.md)
- [完整实战示例](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/12-examples.md)
- [最佳实践与性能优化](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/13-best-practices.md)
- [常见问题解答 (FAQ)](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/14-faq.md)
- [参考资料与学习路径](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/15-resources.md)
- [常见问题与最佳实践](learning/04-docs-markup-tooling/scikit-build-core-wiki/05-faq-and-best-practices.md)

### FAQ

- [Papi酱关闭公司回归个人IP：常见问题FAQ](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/07-faq.md)
- [常见问题解答](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/09-faq.md)

### feishu

- [国内 Skill/MCP 生态盘点：16 个品牌的 Agent 化浪潮](learning/01-agent-protocols-interfaces/domestic-skill-mcp-ecosystem-wiki.md)

### ffi

- [FFI（外部函数接口）教程总览](learning/01-agent-protocols-interfaces/ffi-wiki/00-overview.md)
- [FFI 定义与核心概念](learning/01-agent-protocols-interfaces/ffi-wiki/01-what-is-ffi.md)
- [FFI 工作原理](learning/01-agent-protocols-interfaces/ffi-wiki/02-working-principles.md)
- [不同编程语言中的 FFI 实现](learning/01-agent-protocols-interfaces/ffi-wiki/03-language-implementations.md)
- [实际应用案例与代码示例](learning/01-agent-protocols-interfaces/ffi-wiki/04-use-cases.md)
- [FFI 的优势与局限性](learning/01-agent-protocols-interfaces/ffi-wiki/05-advantages-limitations.md)
- [FFI 与相关概念对比](learning/01-agent-protocols-interfaces/ffi-wiki/06-comparison.md)
- [术语表与参考资料](learning/01-agent-protocols-interfaces/ffi-wiki/07-resources.md)
- [四、ABI（应用二进制接口）：二进制兼容约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/03-abi.md)
- [Ch00 - TVM FFI 概述与定位](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/00-overview.md)
- [Ch01 - 系统架构与设计理念](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/01-architecture.md)
- [02 - C++ 核心 API：Any、Object、Function、Tensor](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/02-cpp-core-api.md)
- [03 - 类型系统：DType、Enum、Optional、String](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/03-type-system.md)
- [04 - 容器类型：Array、Map、Dict、List、Tuple、Shape、Variant](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/04-containers.md)
- [05 - 反射与注册机制](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/05-reflection.md)
- [06 - 序列化：JSON、Base64、结构相等与哈希](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/06-serialization.md)
- [07 - Python 绑定机制](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/07-python-bindings.md)
- [08 - CUDA 支持](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/08-cuda-support.md)
- [09 - ORCJIT 扩展](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/09-orcjit-extension.md)
- [10 - DLPack 集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/10-dlpack-integration.md)
- [编译构建与项目集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/11-build-and-integration.md)
- [完整实战示例](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/12-examples.md)
- [最佳实践与性能优化](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/13-best-practices.md)
- [常见问题解答 (FAQ)](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/14-faq.md)
- [参考资料与学习路径](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/15-resources.md)

### file-memory

- [Anthropic Agent 产品线路线图完整学习教程：Conway永久在线智能体、文件记忆、Orbit主动助手、Operon科研平台、BugCrawl代码审计与GPT-5.6竞争分析](learning/03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md)

### finance

- [行业解决方案场景：垂直行业AI变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/10-scenario-industry.md)

### financial-services

- [Anthropic Financial Services 完整教程：华尔街的AI金融Agent工具箱](learning/03-agent-platforms-tools/anthropic-financial-services-wiki.md)

### fintech

- [Anthropic Financial Services 完整教程：华尔街的AI金融Agent工具箱](learning/03-agent-platforms-tools/anthropic-financial-services-wiki.md)

### flexloop

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### foreign-function-interface

- [FFI（外部函数接口）教程总览](learning/01-agent-protocols-interfaces/ffi-wiki/00-overview.md)
- [FFI 定义与核心概念](learning/01-agent-protocols-interfaces/ffi-wiki/01-what-is-ffi.md)

### four-layer-model

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### free-api

- [Agnes AI 与 Pavo 创作平台完整学习教程：免费多模态API+一站式AI短剧工作流](learning/05-ai-multimodal-content/agnes-pavo-creative-platform-wiki.md)

### freemium

- [商业模式设计：AI产品的盈利模式选择](learning/06-business-trends-analysis/ai-monetization-wiki/03-business-models.md)
- [消费级产品场景：ToC AI应用变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/09-scenario-consumer.md)

### functional-programming

- [二、接口（Interface）：语言级行为抽象](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/01-interface.md)

### further-reading

- [术语表与参考资料](learning/01-agent-protocols-interfaces/ffi-wiki/07-resources.md)
- [九、学习资源与参考资料：术语表、权威规范与扩展阅读](learning/01-agent-protocols-interfaces/idl-wiki/09-resources.md)
- [七、参考资料与扩展阅读](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/06-resources.md)

### gbk

- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### git

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### glm

- [国产AI模型对比与使用场景推荐](learning/06-business-trends-analysis/domestic-llm-comparison-notes.md)

### glossary

- [参考资料与学习路径](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/06-agent-resources.md)
- [术语表与参考资料](learning/01-agent-protocols-interfaces/ffi-wiki/07-resources.md)
- [九、学习资源与参考资料：术语表、权威规范与扩展阅读](learning/01-agent-protocols-interfaces/idl-wiki/09-resources.md)
- [七、参考资料与扩展阅读](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/06-resources.md)
- [参考资料与扩展阅读](learning/04-docs-markup-tooling/scikit-build-core-wiki/06-resources.md)
- [风险提示与资源推荐](learning/06-business-trends-analysis/ai-monetization-wiki/12-risks-resources.md)

### gns

- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### go

- [不同编程语言中的 FFI 实现](learning/01-agent-protocols-interfaces/ffi-wiki/03-language-implementations.md)

### goal-driven

- [四条核心原则详解](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/01-four-principles.md)

### governance

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)
- [方法论模式第3次验证报告：模板批量升级场景](best-practices/pattern-validation-v3-template-batch-upgrade.md)

### governance-loop

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### gpt-5.6

- [Anthropic Agent 产品线路线图完整学习教程：Conway永久在线智能体、文件记忆、Orbit主动助手、Operon科研平台、BugCrawl代码审计与GPT-5.6竞争分析](learning/03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md)

### gradle

- [六、IDL 编译流程与工具链：从源文件到多语言桩代码](learning/01-agent-protocols-interfaces/idl-wiki/06-toolchain.md)

### graphql

- [八、与现代接口描述方式对比：从 RPC IDL 到 Web IDL 与 AI-friendly IDL](learning/01-agent-protocols-interfaces/idl-wiki/08-vs-modern-formats.md)
- [三、API（应用编程接口）：源码与服务级契约](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/02-api.md)

### grpc

- [七、实际应用案例与最佳实践：IDL 在生产环境的落地](learning/01-agent-protocols-interfaces/idl-wiki/07-use-cases.md)
- [三、API（应用编程接口）：源码与服务级契约](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/02-api.md)

### gtm

- [市场推广：AI产品的GTM策略](learning/06-business-trends-analysis/ai-monetization-wiki/06-marketing-strategy.md)

### guide

- [AI变现完整指南：从技术到商业的全流程方法论](learning/06-business-trends-analysis/ai-monetization-wiki/00-overview.md)

### guidelines

- [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)
- [Karpathy LLM 编程准则：概述与背景](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/00-overview.md)
- [四条核心原则详解](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/01-four-principles.md)
- [真实代码正反例](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/02-code-examples.md)
- [快速上手指南](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/03-quickstart.md)
- [SpecWeave 项目整合情况](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/04-specweave-integration.md)
- [资源与参考链接](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/05-resources.md)

### harness

- [Agnes AI 与 Pavo 创作平台完整学习教程：免费多模态API+一站式AI短剧工作流](learning/05-ai-multimodal-content/agnes-pavo-creative-platform-wiki.md)

### Harness Engineering

- [Harness Engineering（驾驭工程）系统性学习Wiki](learning/02-agent-engineering-methodology/harness-engineering-wiki.md)

### harness-engineering

- [AI 四大工程概念演进：Prompt → Context → Harness → Loop](learning/02-agent-engineering-methodology/four-engineering-concepts-wiki.md)

### HDMI采集

- [向日葵五款无网远程控制硬件深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki.md)
- [无网远程控制核心技术原理](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/01-core-technology.md)

### headroom

- [Headroom AI Agent上下文压缩中间件完整学习教程](learning/02-agent-engineering-methodology/headroom-context-compression-wiki.md)

### healthcare

- [行业解决方案场景：垂直行业AI变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/10-scenario-industry.md)

### heredoc

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)

### history

- [一、IDL 定义与作用：接口契约的语言中立描述](learning/01-agent-protocols-interfaces/idl-wiki/01-what-is-idl.md)

### html

- [Declarative Partial Updates 完整教程：HTML 声明式局部更新能力解析](learning/04-docs-markup-tooling/declarative-partial-updates-wiki.md)
- [HTML 正文提取操作指南](operations/html-body-extraction.md)

### html提取

- [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md)

### html清洗

- [HTML 正文提取操作指南](operations/html-body-extraction.md)

### http

- [Agent ABI：跨语言边界层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/03-agent-abi.md)
- [五、协议（Protocol）：通信规则约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/04-protocol.md)

### human-in-the-loop

- [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md)

### hvsocket

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/08-systems-infrastructure/wsl-cli-and-architecture-wiki.md)
- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### idl

- [FFI 与相关概念对比](learning/01-agent-protocols-interfaces/ffi-wiki/06-comparison.md)
- [IDL（接口定义语言）Wiki 教程 - 总览](learning/01-agent-protocols-interfaces/idl-wiki/00-overview.md)
- [一、IDL 定义与作用：接口契约的语言中立描述](learning/01-agent-protocols-interfaces/idl-wiki/01-what-is-idl.md)
- [二、IDL 类型系统：基本数据类型与注解机制](learning/01-agent-protocols-interfaces/idl-wiki/02-syntax-types.md)
- [三、IDL 接口声明与方法描述：服务契约的通用范式](learning/01-agent-protocols-interfaces/idl-wiki/03-syntax-interface.md)
- [四、主要 IDL 规范介绍：五大主流实现详解](learning/01-agent-protocols-interfaces/idl-wiki/04-major-idl-specs.md)
- [五、IDL 规范对比](learning/01-agent-protocols-interfaces/idl-wiki/05-comparison.md)
- [六、IDL 编译流程与工具链：从源文件到多语言桩代码](learning/01-agent-protocols-interfaces/idl-wiki/06-toolchain.md)
- [七、实际应用案例与最佳实践：IDL 在生产环境的落地](learning/01-agent-protocols-interfaces/idl-wiki/07-use-cases.md)
- [八、与现代接口描述方式对比：从 RPC IDL 到 Web IDL 与 AI-friendly IDL](learning/01-agent-protocols-interfaces/idl-wiki/08-vs-modern-formats.md)
- [九、学习资源与参考资料：术语表、权威规范与扩展阅读](learning/01-agent-protocols-interfaces/idl-wiki/09-resources.md)

### implementation

- [实施步骤与关键成功因素](learning/06-business-trends-analysis/ai-monetization-wiki/11-implementation-steps.md)

### industry

- [行业解决方案场景：垂直行业AI变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/10-scenario-industry.md)

### installation

- [快速上手指南](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/03-quickstart.md)

### integration

- [SpecWeave 项目整合情况](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/04-specweave-integration.md)

### intelligent-terminal

- [三个热门AI工具完整指南：微软AI终端、Claudian笔记插件、book-to-skill书籍转Skill](learning/06-business-trends-analysis/three-ai-tools-wiki.md)

### interface

- [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/00-overview.md)
- [Agent Interface：能力契约层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/01-agent-interface.md)
- [三、IDL 接口声明与方法描述：服务契约的通用范式](learning/01-agent-protocols-interfaces/idl-wiki/03-syntax-interface.md)
- [一、概念总览：软件接口的四层抽象](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/00-overview.md)
- [二、接口（Interface）：语言级行为抽象](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/01-interface.md)
- [六、对比分析：四概念系统辨析](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/05-comparison.md)

### interface-contract

- [一、IDL 定义与作用：接口契约的语言中立描述](learning/01-agent-protocols-interfaces/idl-wiki/01-what-is-idl.md)

### interface-definition-language

- [IDL（接口定义语言）Wiki 教程 - 总览](learning/01-agent-protocols-interfaces/idl-wiki/00-overview.md)

### interop

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/08-systems-infrastructure/wsl-cli-and-architecture-wiki.md)

### interoperability

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/01-agent-protocols-interfaces/agent-communication-protocols-wiki.md)

### investment-banking

- [Anthropic Financial Services 完整教程：华尔街的AI金融Agent工具箱](learning/03-agent-platforms-tools/anthropic-financial-services-wiki.md)

### invoke-webrequest

- [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md)

### IoT

- [向日葵开机盒子产品系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis.md)

### iot

- [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md)
- [TuyaOpen-dev-skills 学习笔记](learning/07-vendor-product-learning/tuya/tuyaopen-dev-skills-learning.md)
- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/07-vendor-product-learning/tuya/tuyaopen-folder-learning-path.md)
- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### ipc

- [FFI 与相关概念对比](learning/01-agent-protocols-interfaces/ffi-wiki/06-comparison.md)
- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### IPDU

- [向日葵智能PDU硬件产品完整学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-pdu-hardware-wiki.md)

### IPKVM

- [向日葵五款无网远程控制硬件深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki.md)
- [无网远程控制核心技术原理](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/01-core-technology.md)

### java

- [不同编程语言中的 FFI 实现](learning/01-agent-protocols-interfaces/ffi-wiki/03-language-implementations.md)

### javascript

- [Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！](learning/05-ai-multimodal-content/animejs-threejs-adapter-analysis.md)

### jit

- [07 - Python 绑定机制](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/07-python-bindings.md)
- [08 - CUDA 支持](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/08-cuda-support.md)
- [09 - ORCJIT 扩展](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/09-orcjit-extension.md)
- [10 - DLPack 集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/10-dlpack-integration.md)

### json

- [Agent ABI：跨语言边界层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/03-agent-abi.md)

### json-rpc

- [Agent API：可调用方法层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/02-agent-api.md)
- [Agent Protocol：通信规则层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/04-agent-protocol.md)

### json-schema

- [Agent Interface：能力契约层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/01-agent-interface.md)
- [八、与现代接口描述方式对比：从 RPC IDL 到 Web IDL 与 AI-friendly IDL](learning/01-agent-protocols-interfaces/idl-wiki/08-vs-modern-formats.md)

### K3

- [K3/K4版本差异与产品策略](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/03-version-strategy.md)

### K4

- [K3/K4版本差异与产品策略](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/03-version-strategy.md)

### karpathy

- [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)
- [Karpathy LLM 编程准则：概述与背景](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/00-overview.md)
- [四条核心原则详解](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/01-four-principles.md)
- [真实代码正反例](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/02-code-examples.md)
- [快速上手指南](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/03-quickstart.md)
- [SpecWeave 项目整合情况](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/04-specweave-integration.md)
- [资源与参考链接](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/05-resources.md)
- [Multica 平台：AI Agent 协作管理平台](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/06-multica-platform.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)
- [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md)
- [Claude Tag：文章概述](learning/03-agent-platforms-tools/claude-tag-article/00-overview.md)
- [Claude Tag：核心观点](learning/03-agent-platforms-tools/claude-tag-article/01-core-insights.md)

### KickArt

- [火山引擎KickArt一站式电商营销创作Agent完整学习笔记：六大能力+四大场景+全链路闭环的营销视频生产平台](learning/06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md)

### kimi

- [国产AI模型对比与使用场景推荐](learning/06-business-trends-analysis/domestic-llm-comparison-notes.md)

### knowledge-architecture

- [Learning Wiki 主题分类体系](learning/CATEGORIES.md)

### knowledge-graph

- [Learning Wiki 学习路径推荐表](learning/LEARNING-PATHS.md)

### ksf

- [实施步骤与关键成功因素](learning/06-business-trends-analysis/ai-monetization-wiki/11-implementation-steps.md)

### KVM切换器

- [控控2产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/02-product-kongkong2.md)
- [常见问题解答](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/09-faq.md)

### L2-pattern

- [方法论模式第3次验证报告：模板批量升级场景](best-practices/pattern-validation-v3-template-batch-upgrade.md)

### langgraph

- [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md)

### language-implementations

- [不同编程语言中的 FFI 实现](learning/01-agent-protocols-interfaces/ffi-wiki/03-language-implementations.md)

### learning-path

- [Learning Wiki 主题分类体系](learning/CATEGORIES.md)
- [Learning Wiki 学习路径推荐表](learning/LEARNING-PATHS.md)
- [参考资料与学习路径](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/06-agent-resources.md)
- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/07-vendor-product-learning/tuya/tuyaopen-folder-learning-path.md)
- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### learning-wiki

- [Learning Wiki 主题分类体系](learning/CATEGORIES.md)

### libtv

- [LibTV AI 短剧创作工具学习 Wiki](learning/05-ai-multimodal-content/libtv-ai-shortdrama-wiki.md)

### limitations

- [FFI 的优势与局限性](learning/01-agent-protocols-interfaces/ffi-wiki/05-advantages-limitations.md)

### linux

- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### linux-foundation

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/01-agent-protocols-interfaces/agent-communication-protocols-wiki.md)

### llm

- [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)
- [Karpathy LLM 编程准则：概述与背景](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/00-overview.md)
- [四条核心原则详解](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/01-four-principles.md)
- [真实代码正反例](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/02-code-examples.md)
- [快速上手指南](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/03-quickstart.md)
- [SpecWeave 项目整合情况](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/04-specweave-integration.md)
- [资源与参考链接](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/05-resources.md)
- [Multica 平台：AI Agent 协作管理平台](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/06-multica-platform.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)
- [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md)
- [Claude Tag：文章概述](learning/03-agent-platforms-tools/claude-tag-article/00-overview.md)
- [Claude Tag：核心观点](learning/03-agent-platforms-tools/claude-tag-article/01-core-insights.md)
- [国产AI模型对比与使用场景推荐](learning/06-business-trends-analysis/domestic-llm-comparison-notes.md)

### local-llm

- [EchoBird 百灵鸟项目学习 Wiki 教程](learning/03-agent-platforms-tools/echobird-wiki.md)

### longcat

- [LongCat-2.0 Agent能力实测Wiki教程](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki.md)

### loop-engineering

- [AI 四大工程概念演进：Prompt → Context → Harness → Loop](learning/02-agent-engineering-methodology/four-engineering-concepts-wiki.md)
- [LongCat-2.0 Agent能力实测Wiki教程](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki.md)

### ltv-cac

- [核心概念界定：AI变现术语体系](learning/06-business-trends-analysis/ai-monetization-wiki/01-core-concepts.md)

### MAC地址开机

- [五大核心功能模块详解](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/01-core-features.md)

### managed-agents

- [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)
- [Multica 平台：AI Agent 协作管理平台](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/06-multica-platform.md)

### manufacturing

- [行业解决方案场景：垂直行业AI变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/10-scenario-industry.md)

### market-analysis

- [市场需求分析：识别与评估AI商业化机会](learning/06-business-trends-analysis/ai-monetization-wiki/02-market-analysis.md)

### marketing

- [市场推广：AI产品的GTM策略](learning/06-business-trends-analysis/ai-monetization-wiki/06-marketing-strategy.md)

### marshalling

- [FFI 工作原理](learning/01-agent-protocols-interfaces/ffi-wiki/02-working-principles.md)

### matter

- [明略科技 Octo 平台学习 Wiki：Private AI 时代的多 Agent 协作基础设施](learning/03-agent-platforms-tools/octo-platform-wiki.md)

### maven

- [六、IDL 编译流程与工具链：从源文件到多语言桩代码](learning/01-agent-protocols-interfaces/idl-wiki/06-toolchain.md)

### MCN

- [Papi酱关闭公司回归个人IP：创业趋势观察](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki.md)
- [Papi酱关闭公司回归个人IP：概述与学习目标](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/00-overview.md)
- [Papi酱关闭公司回归个人IP：案例全景与时间线](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/01-case-timeline.md)
- [Papi酱关闭公司回归个人IP：行业观察与案例](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/03-industry-trend.md)
- [Papi酱关闭公司回归个人IP：模式深度对比](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/04-model-comparison.md)
- [Papi酱关闭公司回归个人IP：常见问题FAQ](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/07-faq.md)

### mcp

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/01-agent-protocols-interfaces/agent-communication-protocols-wiki.md)
- [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md)
- [国内 Skill/MCP 生态盘点：16 个品牌的 Agent 化浪潮](learning/01-agent-protocols-interfaces/domestic-skill-mcp-ecosystem-wiki.md)
- [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/00-overview.md)
- [Agent Interface：能力契约层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/01-agent-interface.md)
- [Agent API：可调用方法层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/02-agent-api.md)
- [Agent Protocol：通信规则层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/04-agent-protocol.md)
- [对比分析：Agent四层技术栈协同](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/05-agent-comparison.md)
- [Anthropic Financial Services 完整教程：华尔街的AI金融Agent工具箱](learning/03-agent-platforms-tools/anthropic-financial-services-wiki.md)
- [QuantDinger：开源AI量化交易基础设施层完整教程](learning/03-agent-platforms-tools/quantdinger-ai-trading-wiki.md)
- [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md)
- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### MCP

- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)

### mcu

- [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md)

### mdc

- [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)

### mdi

- [八、与现代接口描述方式对比：从 RPC IDL 到 Web IDL 与 AI-friendly IDL](learning/01-agent-protocols-interfaces/idl-wiki/08-vs-modern-formats.md)

### meituan

- [LongCat-2.0 Agent能力实测Wiki教程](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki.md)

### memory-management

- [FFI 工作原理](learning/01-agent-protocols-interfaces/ffi-wiki/02-working-principles.md)

### mermaid

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)
- [WSL CLI 命令树与架构 Wiki 参考手册](learning/08-systems-infrastructure/wsl-cli-and-architecture-wiki.md)

### meta-insights

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### methodology

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)
- [AI 四大工程概念演进：Prompt → Context → Harness → Loop](learning/02-agent-engineering-methodology/four-engineering-concepts-wiki.md)

### methodology-evolution

- [方法论模式第3次验证报告：模板批量升级场景](best-practices/pattern-validation-v3-template-batch-upgrade.md)

### microservices

- [三、API（应用编程接口）：源码与服务级契约](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/02-api.md)

### middleware

- [Headroom AI Agent上下文压缩中间件完整学习教程](learning/02-agent-engineering-methodology/headroom-context-compression-wiki.md)

### minimax

- [国产AI模型对比与使用场景推荐](learning/06-business-trends-analysis/domestic-llm-comparison-notes.md)

### mininglamp

- [明略科技 Octo 平台学习 Wiki：Private AI 时代的多 Agent 协作基础设施](learning/03-agent-platforms-tools/octo-platform-wiki.md)

### mlops

- [产品开发：AI产品的构建与迭代流程](learning/06-business-trends-analysis/ai-monetization-wiki/05-product-development.md)

### MM110

- [向日葵智能远控鼠标MM110/BM110产品学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-mouse-bm110-mm110-analysis.md)

### moat

- [核心概念界定：AI变现术语体系](learning/06-business-trends-analysis/ai-monetization-wiki/01-core-concepts.md)

### model-comparison

- [国产AI模型对比与使用场景推荐](learning/06-business-trends-analysis/domestic-llm-comparison-notes.md)

### model-nexus

- [EchoBird 百灵鸟项目学习 Wiki 教程](learning/03-agent-platforms-tools/echobird-wiki.md)

### modern-formats

- [八、与现代接口描述方式对比：从 RPC IDL 到 Web IDL 与 AI-friendly IDL](learning/01-agent-protocols-interfaces/idl-wiki/08-vs-modern-formats.md)

### modified-content

- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### modules

- [项目目录结构与模块功能](learning/04-docs-markup-tooling/scikit-build-core-wiki/02-project-structure.md)

### moe

- [LongCat-2.0 Agent能力实测Wiki教程](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki.md)

### multi-agent

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/01-agent-protocols-interfaces/agent-communication-protocols-wiki.md)
- [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md)
- [Vibe Coding 两大神级 Prompt](learning/02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md)
- [明略科技 Octo 平台学习 Wiki：Private AI 时代的多 Agent 协作基础设施](learning/03-agent-platforms-tools/octo-platform-wiki.md)
- [The Agency 项目完整学习教程](learning/03-agent-platforms-tools/the-agency-project-wiki.md)

### multi-file

- [多文件编辑操作可靠性指南](best-practices/multi-file-edit-reliability.md)

### multi-modal

- [国产AI模型对比与使用场景推荐](learning/06-business-trends-analysis/domestic-llm-comparison-notes.md)

### multica

- [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)
- [资源与参考链接](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/05-resources.md)
- [Multica 平台：AI Agent 协作管理平台](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/06-multica-platform.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)

### multica-cli

- [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)
- [资源与参考链接](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/05-resources.md)

### multimodal

- [Agnes AI 与 Pavo 创作平台完整学习教程：免费多模态API+一站式AI短剧工作流](learning/05-ai-multimodal-content/agnes-pavo-creative-platform-wiki.md)

### name-mangling

- [FFI 工作原理](learning/01-agent-protocols-interfaces/ffi-wiki/02-working-principles.md)

### naming

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)

### network

- [五、协议（Protocol）：通信规则约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/04-protocol.md)

### ninja

- [从入门到进阶操作指南](learning/04-docs-markup-tooling/scikit-build-core-wiki/04-quickstart-to-advanced.md)

### nodejs

- [不同编程语言中的 FFI 实现](learning/01-agent-protocols-interfaces/ffi-wiki/03-language-implementations.md)

### nuget

- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### observability

- [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md)

### obsidian

- [三个热门AI工具完整指南：微软AI终端、Claudian笔记插件、book-to-skill书籍转Skill](learning/06-business-trends-analysis/three-ai-tools-wiki.md)

### octo

- [明略科技 Octo 平台学习 Wiki：Private AI 时代的多 Agent 协作基础设施](learning/03-agent-platforms-tools/octo-platform-wiki.md)

### online-rl

- [AReaL 2.0 自演进 Agent 在线强化学习基础设施学习 Wiki](learning/03-agent-platforms-tools/areal-agent-rl-wiki.md)

### oop

- [二、接口（Interface）：语言级行为抽象](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/01-interface.md)

### open-code-review

- [Open Code Review 完整学习教程：阿里开源 AI 代码评审工具](learning/03-agent-platforms-tools/open-code-review-wiki.md)

### open-standard

- [Agent 通信协议完整教程：MCP/ACP/A2A/ANP 四层协议栈](learning/01-agent-protocols-interfaces/agent-communication-protocols-wiki.md)
- [Agent Skills 开放标准完整指南](learning/01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md)

### openai-assistants

- [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md)

### openapi

- [八、与现代接口描述方式对比：从 RPC IDL 到 Web IDL 与 AI-friendly IDL](learning/01-agent-protocols-interfaces/idl-wiki/08-vs-modern-formats.md)

### openclaw

- [EchoBird 百灵鸟项目学习 Wiki 教程](learning/03-agent-platforms-tools/echobird-wiki.md)

### operon

- [Anthropic Agent 产品线路线图完整学习教程：Conway永久在线智能体、文件记忆、Orbit主动助手、Operon科研平台、BugCrawl代码审计与GPT-5.6竞争分析](learning/03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md)

### opus

- [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md)
- [Claude Tag：关键概念与术语](learning/03-agent-platforms-tools/claude-tag-article/02-key-concepts.md)
- [Claude Tag：重要数据](learning/03-agent-platforms-tools/claude-tag-article/03-key-data.md)

### Oray

- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)
- [向日葵开机盒子产品系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis.md)
- [向日葵USB远程摄像头SU1完整学习教程：400万高清、双全向麦克风、远程视频多面手深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md)
- [向日葵智能远控鼠标MM110/BM110产品学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-mouse-bm110-mm110-analysis.md)
- [向日葵智能插线板P4（4G版）与P1Pro（WiFi版）对比学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md)
- [向日葵智能PDU硬件产品完整学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-pdu-hardware-wiki.md)
- [向日葵（Sunlogin）产品学习系列](learning/07-vendor-product-learning/sunlogin/sunlogin-product-series-index.md)
- [向日葵智能插座C1Pro/C2/C4完整学习教程：远程开机、电量统计、4G户外三款产品对比与深度洞察](learning/07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md)

### OrayClaw

- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)

### orbit

- [Anthropic Agent 产品线路线图完整学习教程：Conway永久在线智能体、文件记忆、Orbit主动助手、Operon科研平台、BugCrawl代码审计与GPT-5.6竞争分析](learning/03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md)

### orchestration

- [明略科技 Octo 平台学习 Wiki：Private AI 时代的多 Agent 协作基础设施](learning/03-agent-platforms-tools/octo-platform-wiki.md)

### osi-model

- [五、协议（Protocol）：通信规则约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/04-protocol.md)

### output-format

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### overview

- [FFI（外部函数接口）教程总览](learning/01-agent-protocols-interfaces/ffi-wiki/00-overview.md)
- [IDL（接口定义语言）Wiki 教程 - 总览](learning/01-agent-protocols-interfaces/idl-wiki/00-overview.md)
- [scikit-build-core 全面教程：概述与导航](learning/04-docs-markup-tooling/scikit-build-core-wiki/00-overview.md)
- [AI变现完整指南：从技术到商业的全流程方法论](learning/06-business-trends-analysis/ai-monetization-wiki/00-overview.md)

### P1Pro

- [向日葵智能插线板P4（4G版）与P1Pro（WiFi版）对比学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md)

### P4

- [向日葵智能插线板P4（4G版）与P1Pro（WiFi版）对比学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md)

### papi-jiang

- [Papi酱关闭公司回归个人IP：创业趋势观察](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki.md)
- [Papi酱关闭公司回归个人IP：概述与学习目标](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/00-overview.md)
- [Papi酱关闭公司回归个人IP：案例全景与时间线](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/01-case-timeline.md)
- [Papi酱关闭公司回归个人IP：核心观点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/02-core-viewpoints.md)
- [Papi酱关闭公司回归个人IP：行业观察与案例](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/03-industry-trend.md)
- [Papi酱关闭公司回归个人IP：模式深度对比](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/04-model-comparison.md)
- [Papi酱关闭公司回归个人IP：创业启示与实践要点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/05-entrepreneurship-insights.md)
- [Papi酱关闭公司回归个人IP：总结与Takeaway](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/06-summary.md)
- [Papi酱关闭公司回归个人IP：常见问题FAQ](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/07-faq.md)
- [Papi酱关闭公司回归个人IP：资源链接](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/08-resources.md)

### papitube

- [Papi酱关闭公司回归个人IP：案例全景与时间线](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/01-case-timeline.md)

### parser

- [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md)

### partial-rendering

- [Declarative Partial Updates 完整教程：HTML 声明式局部更新能力解析](learning/04-docs-markup-tooling/declarative-partial-updates-wiki.md)

### path

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### pattern-validation

- [方法论模式第3次验证报告：模板批量升级场景](best-practices/pattern-validation-v3-template-batch-upgrade.md)

### patterns

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### pavo

- [Agnes AI 与 Pavo 创作平台完整学习教程：免费多模态API+一站式AI短剧工作流](learning/05-ai-multimodal-content/agnes-pavo-creative-platform-wiki.md)

### payment

- [国内 Skill/MCP 生态盘点：16 个品牌的 Agent 化浪潮](learning/01-agent-protocols-interfaces/domestic-skill-mcp-ecosystem-wiki.md)

### PDU

- [向日葵智能PDU硬件产品完整学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-pdu-hardware-wiki.md)

### pep517

- [scikit-build-core 全面教程：概述与导航](learning/04-docs-markup-tooling/scikit-build-core-wiki/00-overview.md)
- [基本概念与架构解析](learning/04-docs-markup-tooling/scikit-build-core-wiki/01-concepts-architecture.md)
- [核心 API 使用与配置详解](learning/04-docs-markup-tooling/scikit-build-core-wiki/03-core-api-and-config.md)

### pep660

- [基本概念与架构解析](learning/04-docs-markup-tooling/scikit-build-core-wiki/01-concepts-architecture.md)

### performance

- [FFI 的优势与局限性](learning/01-agent-protocols-interfaces/ffi-wiki/05-advantages-limitations.md)

### phased-rollout

- [方法论模式第3次验证报告：模板批量升级场景](best-practices/pattern-validation-v3-template-batch-upgrade.md)

### pipe

- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)

### plan9

- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### platform

- [Multica 平台：AI Agent 协作管理平台](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/06-multica-platform.md)
- [企业服务场景：ToB AI应用变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/08-scenario-enterprise.md)

### playwright

- [BrowserAct 完整学习教程：让Agent真正能操作浏览器的自动化工具](learning/03-agent-platforms-tools/browseract-wiki.md)
- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### plugin

- [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)
- [快速上手指南](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/03-quickstart.md)

### pmf

- [核心概念界定：AI变现术语体系](learning/06-business-trends-analysis/ai-monetization-wiki/01-core-concepts.md)

### poc

- [产品开发：AI产品的构建与迭代流程](learning/06-business-trends-analysis/ai-monetization-wiki/05-product-development.md)

### polymorphism

- [二、接口（Interface）：语言级行为抽象](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/01-interface.md)

### porter-five-forces

- [市场需求分析：识别与评估AI商业化机会](learning/06-business-trends-analysis/ai-monetization-wiki/02-market-analysis.md)

### positioning

- [市场推广：AI产品的GTM策略](learning/06-business-trends-analysis/ai-monetization-wiki/06-marketing-strategy.md)

### powershell

- [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md)
- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)
- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### prerequisites

- [Learning Wiki 学习路径推荐表](learning/LEARNING-PATHS.md)

### pricing

- [商业模式设计：AI产品的盈利模式选择](learning/06-business-trends-analysis/ai-monetization-wiki/03-business-models.md)
- [盈利策略：定价模型与规模化路径](learning/06-business-trends-analysis/ai-monetization-wiki/07-profitability-strategy.md)

### principles

- [四条核心原则详解](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/01-four-principles.md)

### private-ai

- [明略科技 Octo 平台学习 Wiki：Private AI 时代的多 Agent 协作基础设施](learning/03-agent-platforms-tools/octo-platform-wiki.md)

### proactive-ai

- [Anthropic Agent 产品线路线图完整学习教程：Conway永久在线智能体、文件记忆、Orbit主动助手、Operon科研平台、BugCrawl代码审计与GPT-5.6竞争分析](learning/03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md)

### product-development

- [产品开发：AI产品的构建与迭代流程](learning/06-business-trends-analysis/ai-monetization-wiki/05-product-development.md)

### progressive-disclosure

- [Agent Skills 开放标准完整指南](learning/01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md)

### project-structure

- [项目目录结构与模块功能](learning/04-docs-markup-tooling/scikit-build-core-wiki/02-project-structure.md)

### prompt

- [Vibe Coding 两大神级 Prompt](learning/02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md)

### Prompt Engineering

- [Harness Engineering（驾驭工程）系统性学习Wiki](learning/02-agent-engineering-methodology/harness-engineering-wiki.md)

### prompt-engineering

- [AI 四大工程概念演进：Prompt → Context → Harness → Loop](learning/02-agent-engineering-methodology/four-engineering-concepts-wiki.md)

### protobuf

- [IDL（接口定义语言）Wiki 教程 - 总览](learning/01-agent-protocols-interfaces/idl-wiki/00-overview.md)
- [二、IDL 类型系统：基本数据类型与注解机制](learning/01-agent-protocols-interfaces/idl-wiki/02-syntax-types.md)
- [三、IDL 接口声明与方法描述：服务契约的通用范式](learning/01-agent-protocols-interfaces/idl-wiki/03-syntax-interface.md)
- [四、主要 IDL 规范介绍：五大主流实现详解](learning/01-agent-protocols-interfaces/idl-wiki/04-major-idl-specs.md)
- [五、IDL 规范对比](learning/01-agent-protocols-interfaces/idl-wiki/05-comparison.md)

### protoc

- [六、IDL 编译流程与工具链：从源文件到多语言桩代码](learning/01-agent-protocols-interfaces/idl-wiki/06-toolchain.md)

### protocol

- [Agent视角：Interface/API/ABI/Protocol四层技术栈总览](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/00-overview.md)
- [Agent Protocol：通信规则层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/04-agent-protocol.md)
- [一、概念总览：软件接口的四层抽象](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/00-overview.md)
- [五、协议（Protocol）：通信规则约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/04-protocol.md)
- [六、对比分析：四概念系统辨析](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/05-comparison.md)
- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### pyproject-toml

- [核心 API 使用与配置详解](learning/04-docs-markup-tooling/scikit-build-core-wiki/03-core-api-and-config.md)

### python

- [不同编程语言中的 FFI 实现](learning/01-agent-protocols-interfaces/ffi-wiki/03-language-implementations.md)
- [Ch00 - TVM FFI 概述与定位](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/00-overview.md)
- [Ch01 - 系统架构与设计理念](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/01-architecture.md)
- [07 - Python 绑定机制](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/07-python-bindings.md)
- [08 - CUDA 支持](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/08-cuda-support.md)
- [09 - ORCJIT 扩展](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/09-orcjit-extension.md)
- [10 - DLPack 集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/10-dlpack-integration.md)
- [真实代码正反例](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/02-code-examples.md)
- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)

### python-packaging

- [scikit-build-core 全面教程：概述与导航](learning/04-docs-markup-tooling/scikit-build-core-wiki/00-overview.md)

### Q0.5

- [Q0.5产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/05-product-q0.5.md)

### Q1

- [Q1产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/03-product-q1.md)

### Q2Pro

- [Q2Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/04-product-q2pro-ble.md)

### Q5Pro

- [Q5Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/06-product-q5pro.md)

### quantdinger

- [QuantDinger：开源AI量化交易基础设施层完整教程](learning/03-agent-platforms-tools/quantdinger-ai-trading-wiki.md)

### quantitative-finance

- [QuantDinger：开源AI量化交易基础设施层完整教程](learning/03-agent-platforms-tools/quantdinger-ai-trading-wiki.md)

### quickstart

- [快速上手指南](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/03-quickstart.md)
- [从入门到进阶操作指南](learning/04-docs-markup-tooling/scikit-build-core-wiki/04-quickstart-to-advanced.md)

### reference

- [参考资料与学习路径](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/06-agent-resources.md)

### references

- [术语表与参考资料](learning/01-agent-protocols-interfaces/ffi-wiki/07-resources.md)
- [九、学习资源与参考资料：术语表、权威规范与扩展阅读](learning/01-agent-protocols-interfaces/idl-wiki/09-resources.md)
- [七、参考资料与扩展阅读](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/06-resources.md)
- [资源与参考链接](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/05-resources.md)
- [参考资料与扩展阅读](learning/04-docs-markup-tooling/scikit-build-core-wiki/06-resources.md)

### reinforcement-learning

- [AReaL 2.0 自演进 Agent 在线强化学习基础设施学习 Wiki](learning/03-agent-platforms-tools/areal-agent-rl-wiki.md)

### reliability

- [多文件编辑操作可靠性指南](best-practices/multi-file-edit-reliability.md)

### rename

- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### repository-structure

- [资源与参考链接](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/05-resources.md)

### resources

- [参考资料与学习路径](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/06-agent-resources.md)
- [九、学习资源与参考资料：术语表、权威规范与扩展阅读](learning/01-agent-protocols-interfaces/idl-wiki/09-resources.md)
- [七、参考资料与扩展阅读](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/06-resources.md)
- [编译构建与项目集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/11-build-and-integration.md)
- [完整实战示例](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/12-examples.md)
- [最佳实践与性能优化](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/13-best-practices.md)
- [常见问题解答 (FAQ)](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/14-faq.md)
- [参考资料与学习路径](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/15-resources.md)
- [资源与参考链接](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/05-resources.md)
- [参考资料与扩展阅读](learning/04-docs-markup-tooling/scikit-build-core-wiki/06-resources.md)
- [风险提示与资源推荐](learning/06-business-trends-analysis/ai-monetization-wiki/12-risks-resources.md)

### rest

- [Agent API：可调用方法层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/02-agent-api.md)
- [三、API（应用编程接口）：源码与服务级契约](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/02-api.md)

### retail

- [行业解决方案场景：垂直行业AI变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/10-scenario-industry.md)

### retention

- [消费级产品场景：ToC AI应用变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/09-scenario-consumer.md)

### retrospective

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### revenue-structure

- [盈利策略：定价模型与规模化路径](learning/06-business-trends-analysis/ai-monetization-wiki/07-profitability-strategy.md)

### rfc

- [七、参考资料与扩展阅读](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/06-resources.md)

### risks

- [风险提示与资源推荐](learning/06-business-trends-analysis/ai-monetization-wiki/12-risks-resources.md)

### roadmap

- [实施步骤与关键成功因素](learning/06-business-trends-analysis/ai-monetization-wiki/11-implementation-steps.md)

### robotics

- [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/05-ai-multimodal-content/text-to-cad-wiki.md)

### RPA

- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)

### rpc

- [FFI 与相关概念对比](learning/01-agent-protocols-interfaces/ffi-wiki/06-comparison.md)
- [三、IDL 接口声明与方法描述：服务契约的通用范式](learning/01-agent-protocols-interfaces/idl-wiki/03-syntax-interface.md)

### rules

- [SpecWeave 项目整合情况](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/04-specweave-integration.md)

### run

- [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md)

### runtime

- [Multica 平台：AI Agent 协作管理平台](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/06-multica-platform.md)

### rust

- [不同编程语言中的 FFI 实现](learning/01-agent-protocols-interfaces/ffi-wiki/03-language-implementations.md)
- [Ch00 - TVM FFI 概述与定位](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/00-overview.md)
- [Ch01 - 系统架构与设计理念](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/01-architecture.md)
- [EchoBird 百灵鸟项目学习 Wiki 教程](learning/03-agent-platforms-tools/echobird-wiki.md)

### saas

- [商业模式设计：AI产品的盈利模式选择](learning/06-business-trends-analysis/ai-monetization-wiki/03-business-models.md)
- [企业服务场景：ToB AI应用变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/08-scenario-enterprise.md)

### safety

- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)

### scaling

- [盈利策略：定价模型与规模化路径](learning/06-business-trends-analysis/ai-monetization-wiki/07-profitability-strategy.md)

### scenario-recommendation

- [国产AI模型对比与使用场景推荐](learning/06-business-trends-analysis/domestic-llm-comparison-notes.md)

### schema-evolution

- [六、IDL 编译流程与工具链：从源文件到多语言桩代码](learning/01-agent-protocols-interfaces/idl-wiki/06-toolchain.md)

### scikit-build-core

- [scikit-build-core 全面教程：概述与导航](learning/04-docs-markup-tooling/scikit-build-core-wiki/00-overview.md)
- [基本概念与架构解析](learning/04-docs-markup-tooling/scikit-build-core-wiki/01-concepts-architecture.md)
- [项目目录结构与模块功能](learning/04-docs-markup-tooling/scikit-build-core-wiki/02-project-structure.md)
- [核心 API 使用与配置详解](learning/04-docs-markup-tooling/scikit-build-core-wiki/03-core-api-and-config.md)
- [从入门到进阶操作指南](learning/04-docs-markup-tooling/scikit-build-core-wiki/04-quickstart-to-advanced.md)
- [常见问题与最佳实践](learning/04-docs-markup-tooling/scikit-build-core-wiki/05-faq-and-best-practices.md)
- [参考资料与扩展阅读](learning/04-docs-markup-tooling/scikit-build-core-wiki/06-resources.md)

### SD-WAN

- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)

### sdk

- [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md)
- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/07-vendor-product-learning/tuya/tuyaopen-folder-learning-path.md)
- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### security

- [FFI 的优势与局限性](learning/01-agent-protocols-interfaces/ffi-wiki/05-advantages-limitations.md)

### Seedance

- [火山引擎KickArt一站式电商营销创作Agent完整学习笔记：六大能力+四大场景+全链路闭环的营销视频生产平台](learning/06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md)

### selection

- [五、IDL 规范对比](learning/01-agent-protocols-interfaces/idl-wiki/05-comparison.md)

### self-evolving-agent

- [AReaL 2.0 自演进 Agent 在线强化学习基础设施学习 Wiki](learning/03-agent-platforms-tools/areal-agent-rl-wiki.md)

### self-hosted

- [QuantDinger：开源AI量化交易基础设施层完整教程](learning/03-agent-platforms-tools/quantdinger-ai-trading-wiki.md)

### semi-structured-parsing

- [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md)

### serial-vs-parallel

- [多文件编辑操作可靠性指南](best-practices/multi-file-edit-reliability.md)

### serialization

- [Agent ABI：跨语言边界层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/03-agent-abi.md)

### service

- [三、IDL 接口声明与方法描述：服务契约的通用范式](learning/01-agent-protocols-interfaces/idl-wiki/03-syntax-interface.md)

### set-content

- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)

### shared-library

- [四、ABI（应用二进制接口）：二进制兼容约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/03-abi.md)

### shell

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)

### simplicity

- [四条核心原则详解](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/01-four-principles.md)

### skill

- [国内 Skill/MCP 生态盘点：16 个品牌的 Agent 化浪潮](learning/01-agent-protocols-interfaces/domestic-skill-mcp-ecosystem-wiki.md)
- [Agent Interface：能力契约层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/01-agent-interface.md)
- [Multica 平台：AI Agent 协作管理平台](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/06-multica-platform.md)
- [Multica CLI Skill：让外部 Agent 安全操作 Multica](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/07-multica-cli-skill.md)

### skill-conflict

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### skill-development

- [Agent Skills 开放标准完整指南](learning/01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md)

### skill-evals

- [Agent Skills 开放标准完整指南](learning/01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md)

### skill-forge

- [BrowserAct 完整学习教程：让Agent真正能操作浏览器的自动化工具](learning/03-agent-platforms-tools/browseract-wiki.md)

### skills

- [Agent Skills 开放标准完整指南](learning/01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md)
- [Karpathy LLM 编程准则完整教程](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)
- [快速上手指南](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/03-quickstart.md)
- [TuyaOpen-dev-skills 学习笔记](learning/07-vendor-product-learning/tuya/tuyaopen-dev-skills-learning.md)

### skills-ref

- [Agent Skills 开放标准完整指南](learning/01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md)

### slack

- [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md)
- [Claude Tag：文章概述](learning/03-agent-platforms-tools/claude-tag-article/00-overview.md)
- [Claude Tag：重要数据](learning/03-agent-platforms-tools/claude-tag-article/03-key-data.md)
- [Claude Tag：原文结构框架](learning/03-agent-platforms-tools/claude-tag-article/04-article-structure.md)

### soap

- [三、API（应用编程接口）：源码与服务级契约](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/02-api.md)

### SOP

- [B2B/旗舰产品信息源分层采集规范](best-practices/b2b-product-info-collection-sop.md)

### source-code

- [项目目录结构与模块功能](learning/04-docs-markup-tooling/scikit-build-core-wiki/02-project-structure.md)

### source-verification

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/08-systems-infrastructure/wsl-cli-and-architecture-wiki.md)

### specification

- [Agent Skills 开放标准完整指南](learning/01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md)

### specifications

- [四、主要 IDL 规范介绍：五大主流实现详解](learning/01-agent-protocols-interfaces/idl-wiki/04-major-idl-specs.md)
- [九、学习资源与参考资料：术语表、权威规范与扩展阅读](learning/01-agent-protocols-interfaces/idl-wiki/09-resources.md)

### specweave

- [SpecWeave 项目整合情况](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/04-specweave-integration.md)
- [Claude Tag：与 SpecWeave 的关联](learning/03-agent-platforms-tools/claude-tag-article/05-specweave-relevance.md)

### squad

- [Multica 平台：AI Agent 协作管理平台](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/06-multica-platform.md)

### ssr

- [Declarative Partial Updates 完整教程：HTML 声明式局部更新能力解析](learning/04-docs-markup-tooling/declarative-partial-updates-wiki.md)

### stage-guardrails

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### stages

- [实施步骤与关键成功因素](learning/06-business-trends-analysis/ai-monetization-wiki/11-implementation-steps.md)

### startup

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### stdio

- [Agent ABI：跨语言边界层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/03-agent-abi.md)

### step

- [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/05-ai-multimodal-content/text-to-cad-wiki.md)

### streaming

- [Declarative Partial Updates 完整教程：HTML 声明式局部更新能力解析](learning/04-docs-markup-tooling/declarative-partial-updates-wiki.md)

### study-guide

- [Learning Wiki 学习路径推荐表](learning/LEARNING-PATHS.md)

### SU1

- [向日葵USB远程摄像头SU1完整学习教程：400万高清、双全向麦克风、远程视频多面手深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md)

### submodule

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)
- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### subscription

- [消费级产品场景：ToC AI应用变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/09-scenario-consumer.md)

### sunlogin

- [向日葵五款无网远程控制硬件深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki.md)
- [向日葵（Sunlogin）产品学习系列](learning/07-vendor-product-learning/sunlogin/sunlogin-product-series-index.md)

### surgical-changes

- [四条核心原则详解](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/01-four-principles.md)

### syntax

- [二、IDL 类型系统：基本数据类型与注解机制](learning/01-agent-protocols-interfaces/idl-wiki/02-syntax-types.md)
- [三、IDL 接口声明与方法描述：服务契约的通用范式](learning/01-agent-protocols-interfaces/idl-wiki/03-syntax-interface.md)

### syscall

- [四、ABI（应用二进制接口）：二进制兼容约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/03-abi.md)

### systemd

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/08-systems-infrastructure/wsl-cli-and-architecture-wiki.md)
- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### tag

- [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md)
- [Claude Tag：文章概述](learning/03-agent-platforms-tools/claude-tag-article/00-overview.md)
- [Claude Tag：核心观点](learning/03-agent-platforms-tools/claude-tag-article/01-core-insights.md)
- [Claude Tag：关键概念与术语](learning/03-agent-platforms-tools/claude-tag-article/02-key-concepts.md)
- [Claude Tag：重要数据](learning/03-agent-platforms-tools/claude-tag-article/03-key-data.md)
- [Claude Tag：原文结构框架](learning/03-agent-platforms-tools/claude-tag-article/04-article-structure.md)
- [Claude Tag：与 SpecWeave 的关联](learning/03-agent-platforms-tools/claude-tag-article/05-specweave-relevance.md)
- [Claude Tag：知识沉淀闭环](learning/03-agent-platforms-tools/claude-tag-article/06-knowledge-closure.md)
- [Claude Tag：参考链接](learning/03-agent-platforms-tools/claude-tag-article/07-resources.md)

### takeaway

- [Papi酱关闭公司回归个人IP：总结与Takeaway](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/06-summary.md)

### tal

- [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md)

### tam-sam-som

- [市场需求分析：识别与评估AI商业化机会](learning/06-business-trends-analysis/ai-monetization-wiki/02-market-analysis.md)

### taste

- [明略科技 Octo 平台学习 Wiki：Private AI 时代的多 Agent 协作基础设施](learning/03-agent-platforms-tools/octo-platform-wiki.md)

### tauri

- [EchoBird 百灵鸟项目学习 Wiki 教程](learning/03-agent-platforms-tools/echobird-wiki.md)

### tcp

- [五、协议（Protocol）：通信规则约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/04-protocol.md)

### tcp-ip

- [五、协议（Protocol）：通信规则约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/04-protocol.md)

### TDD

- [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md)

### tdd

- [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md)

### tdl

- [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md)

### tech-selection

- [技术选型：AI技术栈决策框架](learning/06-business-trends-analysis/ai-monetization-wiki/04-tech-selection.md)

### terminal

- [三个热门AI工具完整指南：微软AI终端、Claudian笔记插件、book-to-skill书籍转Skill](learning/06-business-trends-analysis/three-ai-tools-wiki.md)

### terminology

- [核心概念界定：AI变现术语体系](learning/06-business-trends-analysis/ai-monetization-wiki/01-core-concepts.md)

### text-to-cad

- [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/05-ai-multimodal-content/text-to-cad-wiki.md)

### the-agency

- [The Agency 项目完整学习教程](learning/03-agent-platforms-tools/the-agency-project-wiki.md)

### think-before-coding

- [四条核心原则详解](learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/01-four-principles.md)

### thread

- [Agent Runtime Protocol 完整教程：生产级 Agent 运行时协议对象与八大维度解析](learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md)

### threejs

- [Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！](learning/05-ai-multimodal-content/animejs-threejs-adapter-analysis.md)

### thrift

- [IDL（接口定义语言）Wiki 教程 - 总览](learning/01-agent-protocols-interfaces/idl-wiki/00-overview.md)
- [二、IDL 类型系统：基本数据类型与注解机制](learning/01-agent-protocols-interfaces/idl-wiki/02-syntax-types.md)
- [三、IDL 接口声明与方法描述：服务契约的通用范式](learning/01-agent-protocols-interfaces/idl-wiki/03-syntax-interface.md)
- [四、主要 IDL 规范介绍：五大主流实现详解](learning/01-agent-protocols-interfaces/idl-wiki/04-major-idl-specs.md)
- [五、IDL 规范对比](learning/01-agent-protocols-interfaces/idl-wiki/05-comparison.md)
- [六、IDL 编译流程与工具链：从源文件到多语言桩代码](learning/01-agent-protocols-interfaces/idl-wiki/06-toolchain.md)
- [七、实际应用案例与最佳实践：IDL 在生产环境的落地](learning/01-agent-protocols-interfaces/idl-wiki/07-use-cases.md)

### tkl

- [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md)

### tob

- [企业服务场景：ToB AI应用变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/08-scenario-enterprise.md)

### toc

- [消费级产品场景：ToC AI应用变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/09-scenario-consumer.md)

### token-optimization

- [Headroom AI Agent上下文压缩中间件完整学习教程](learning/02-agent-engineering-methodology/headroom-context-compression-wiki.md)

### tool

- [Agent Interface：能力契约层](learning/01-agent-protocols-interfaces/agent-interface-deep-dive/01-agent-interface.md)

### tool-pitfalls

- [多文件编辑操作可靠性指南](best-practices/multi-file-edit-reliability.md)

### toolchain

- [六、IDL 编译流程与工具链：从源文件到多语言桩代码](learning/01-agent-protocols-interfaces/idl-wiki/06-toolchain.md)

### topic-classification

- [Learning Wiki 主题分类体系](learning/CATEGORIES.md)

### tos

- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/07-vendor-product-learning/tuya/tuyaopen-folder-learning-path.md)

### trading-bot

- [QuantDinger：开源AI量化交易基础设施层完整教程](learning/03-agent-platforms-tools/quantdinger-ai-trading-wiki.md)

### troubleshooting

- [常见问题与最佳实践](learning/04-docs-markup-tooling/scikit-build-core-wiki/05-faq-and-best-practices.md)

### trust

- [国产AI模型对比与使用场景推荐](learning/06-business-trends-analysis/domestic-llm-comparison-notes.md)

### trustworthy-ai

- [明略科技 Octo 平台学习 Wiki：Private AI 时代的多 Agent 协作基础设施](learning/03-agent-platforms-tools/octo-platform-wiki.md)

### tutorial

- [FFI（外部函数接口）教程总览](learning/01-agent-protocols-interfaces/ffi-wiki/00-overview.md)
- [IDL（接口定义语言）Wiki 教程 - 总览](learning/01-agent-protocols-interfaces/idl-wiki/00-overview.md)
- [从入门到进阶操作指南](learning/04-docs-markup-tooling/scikit-build-core-wiki/04-quickstart-to-advanced.md)

### tuya

- [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md)
- [TuyaOpen-dev-skills 学习笔记](learning/07-vendor-product-learning/tuya/tuyaopen-dev-skills-learning.md)
- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### tuyaopen

- [TuyaOpen 全面学习报告](learning/07-vendor-product-learning/tuya/tuya-open-learning-report.md)
- [TuyaOpen-dev-skills 学习笔记](learning/07-vendor-product-learning/tuya/tuyaopen-dev-skills-learning.md)
- [TuyaOpen 目录学习路径（从 LINUX 闭环到 AI 能力区）](learning/07-vendor-product-learning/tuya/tuyaopen-folder-learning-path.md)

### tvm-ffi

- [Ch00 - TVM FFI 概述与定位](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/00-overview.md)
- [Ch01 - 系统架构与设计理念](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/01-architecture.md)
- [02 - C++ 核心 API：Any、Object、Function、Tensor](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/02-cpp-core-api.md)
- [03 - 类型系统：DType、Enum、Optional、String](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/03-type-system.md)
- [04 - 容器类型：Array、Map、Dict、List、Tuple、Shape、Variant](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/04-containers.md)
- [05 - 反射与注册机制](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/05-reflection.md)
- [06 - 序列化：JSON、Base64、结构相等与哈希](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/06-serialization.md)
- [07 - Python 绑定机制](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/07-python-bindings.md)
- [08 - CUDA 支持](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/08-cuda-support.md)
- [09 - ORCJIT 扩展](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/09-orcjit-extension.md)
- [10 - DLPack 集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/10-dlpack-integration.md)
- [编译构建与项目集成](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/11-build-and-integration.md)
- [完整实战示例](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/12-examples.md)
- [最佳实践与性能优化](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/13-best-practices.md)
- [常见问题解答 (FAQ)](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/14-faq.md)
- [参考资料与学习路径](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/15-resources.md)

### type-system

- [二、IDL 类型系统：基本数据类型与注解机制](learning/01-agent-protocols-interfaces/idl-wiki/02-syntax-types.md)

### unit-economics

- [盈利策略：定价模型与规模化路径](learning/06-business-trends-analysis/ai-monetization-wiki/07-profitability-strategy.md)

### urdf

- [text-to-cad 完整学习教程：用AI生成可编辑CAD源代码](learning/05-ai-multimodal-content/text-to-cad-wiki.md)

### USB仿真

- [无网远程控制核心技术原理](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/01-core-technology.md)

### USB取电

- [Q0.5产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/05-product-q0.5.md)

### USB摄像头

- [向日葵USB远程摄像头SU1完整学习教程：400万高清、双全向麦克风、远程视频多面手深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md)

### USB映射

- [Q5Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/06-product-q5pro.md)

### use-cases

- [实际应用案例与代码示例](learning/01-agent-protocols-interfaces/ffi-wiki/04-use-cases.md)
- [七、实际应用案例与最佳实践：IDL 在生产环境的落地](learning/01-agent-protocols-interfaces/idl-wiki/07-use-cases.md)

### user-research

- [市场需求分析：识别与评估AI商业化机会](learning/06-business-trends-analysis/ai-monetization-wiki/02-market-analysis.md)

### utf-8

- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)
- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### UX分析

- [网页设计与用户体验分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/04-web-ux-analysis.md)

### vendor

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)
- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)
- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### vertical

- [行业解决方案场景：垂直行业AI变现路径](learning/06-business-trends-analysis/ai-monetization-wiki/10-scenario-industry.md)

### vertical-industry

- [Anthropic Financial Services 完整教程：华尔街的AI金融Agent工具箱](learning/03-agent-platforms-tools/anthropic-financial-services-wiki.md)

### vibe-coding

- [Vibe Coding 两大神级 Prompt](learning/02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md)

### VLM

- [火山引擎KickArt一站式电商营销创作Agent完整学习笔记：六大能力+四大场景+全链路闭环的营销视频生产平台](learning/06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md)

### Wake-on-LAN

- [WOL技术背景知识](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/08-wol-technology.md)

### web-api

- [三、API（应用编程接口）：源码与服务级契约](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/02-api.md)

### web-automation

- [BrowserAct 完整学习教程：让Agent真正能操作浏览器的自动化工具](learning/03-agent-platforms-tools/browseract-wiki.md)

### web-standards

- [Declarative Partial Updates 完整教程：HTML 声明式局部更新能力解析](learning/04-docs-markup-tooling/declarative-partial-updates-wiki.md)

### webgl

- [Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！](learning/05-ai-multimodal-content/animejs-threejs-adapter-analysis.md)

### websocket

- [五、协议（Protocol）：通信规则约定](learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/04-protocol.md)

### wechat

- [国内 Skill/MCP 生态盘点：16 个品牌的 Agent 化浪潮](learning/01-agent-protocols-interfaces/domestic-skill-mcp-ecosystem-wiki.md)

### wheel

- [基本概念与架构解析](learning/04-docs-markup-tooling/scikit-build-core-wiki/01-concepts-architecture.md)

### WiFi智能插座

- [向日葵智能插线板P4（4G版）与P1Pro（WiFi版）对比学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md)

### wiki-split

- [多文件编辑操作可靠性指南](best-practices/multi-file-edit-reliability.md)

### windows

- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)
- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Windows PowerShell 文本管道可能污染中文文档输出](operations/windows-powershell-pipe-utf8.md)
- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### windows-pipe

- [多文件编辑操作可靠性指南](best-practices/multi-file-edit-reliability.md)

### winrt

- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### WOL

- [向日葵开机盒子产品系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis.md)

### WOL原理

- [技术实现解析与硬件规格](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/02-technology-specs.md)

### WOL局限

- [竞争优势与市场定位分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/05-competitive-advantage.md)

### WOL技术

- [WOL技术背景知识](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/08-wol-technology.md)

### workflow

- [LibTV AI 短剧创作工具学习 Wiki](learning/05-ai-multimodal-content/libtv-ai-shortdrama-wiki.md)
- [TuyaOpen-dev-skills 学习笔记](learning/07-vendor-product-learning/tuya/tuyaopen-dev-skills-learning.md)

### wsl

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/08-systems-infrastructure/wsl-cli-and-architecture-wiki.md)
- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### wslc

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/08-systems-infrastructure/wsl-cli-and-architecture-wiki.md)
- [WSL 系统学习计划](learning/08-systems-infrastructure/wsl-learning-plan.md)

### wslservice

- [WSL CLI 命令树与架构 Wiki 参考手册](learning/08-systems-infrastructure/wsl-cli-and-architecture-wiki.md)

### 三区域模型

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### 三层架构

- [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md)

### 专业级5G

- [Q5Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/06-product-q5pro.md)

### 个人IP

- [Papi酱关闭公司回归个人IP：创业趋势观察](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki.md)
- [Papi酱关闭公司回归个人IP：概述与学习目标](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/00-overview.md)
- [Papi酱关闭公司回归个人IP：案例全景与时间线](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/01-case-timeline.md)
- [Papi酱关闭公司回归个人IP：核心观点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/02-core-viewpoints.md)
- [Papi酱关闭公司回归个人IP：行业观察与案例](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/03-industry-trend.md)
- [Papi酱关闭公司回归个人IP：模式深度对比](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/04-model-comparison.md)
- [Papi酱关闭公司回归个人IP：创业启示与实践要点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/05-entrepreneurship-insights.md)
- [Papi酱关闭公司回归个人IP：总结与Takeaway](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/06-summary.md)
- [Papi酱关闭公司回归个人IP：常见问题FAQ](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/07-faq.md)
- [Papi酱关闭公司回归个人IP：资源链接](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/08-resources.md)

### 中小企业

- [Q1产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/03-product-q1.md)

### 乱码

- [Windows终端UTF-8编码完整配置指南](operations/windows-terminal-utf8-complete-guide.md)

### 事件上报

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 交互设计

- [网页设计与用户体验分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/04-web-ux-analysis.md)

### 产品学习

- [向日葵（Sunlogin）产品学习系列](learning/07-vendor-product-learning/sunlogin/sunlogin-product-series-index.md)

### 产品定位

- [概述与产品核心定位](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/00-overview.md)
- [概述与学习目标](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/00-overview.md)

### 产品对比

- [五款产品横向对比分析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/07-comparison.md)

### 产品策略

- [K3/K4版本差异与产品策略](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/03-version-strategy.md)

### 产品线全景

- [概述与学习目标](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/00-overview.md)

### 产品线梯度

- [五款产品横向对比分析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/07-comparison.md)

### 产品组合

- [应用场景与选型指南](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/08-scenarios.md)

### 产品设计

- [深度洞察与行业启示](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/06-insights.md)

### 产品迭代

- [潜在改进空间与优化建议](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/07-improvement-suggestions.md)

### 产品页面

- [相关资源链接](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/09-resources.md)

### 代码审查

- [Vibe Coding 两大神级 Prompt](learning/02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md)

### 企业安全

- [向日葵远程控制安全产品完整学习教程：国民远控的全流程安全体系深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-security-wiki.md)

### 企业级

- [控控2产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/02-product-kongkong2.md)

### 优化方向

- [潜在改进空间与优化建议](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/07-improvement-suggestions.md)

### 便携

- [Q0.5产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/05-product-q0.5.md)

### 信息架构

- [网页设计与用户体验分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/04-web-ux-analysis.md)

### 信息采集

- [B2B/旗舰产品信息源分层采集规范](best-practices/b2b-product-info-collection-sop.md)

### 免驱

- [向日葵USB远程摄像头SU1完整学习教程：400万高清、双全向麦克风、远程视频多面手深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md)

### 八大场景

- [应用场景与选型指南](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/08-scenarios.md)

### 六规则

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 兼容性

- [常见问题解答](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/09-faq.md)

### 内容分发

- [火山引擎KickArt一站式电商营销创作Agent完整学习笔记：六大能力+四大场景+全链路闭环的营销视频生产平台](learning/06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md)

### 内容创业

- [Papi酱关闭公司回归个人IP：创业趋势观察](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki.md)
- [Papi酱关闭公司回归个人IP：概述与学习目标](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/00-overview.md)
- [Papi酱关闭公司回归个人IP：案例全景与时间线](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/01-case-timeline.md)
- [Papi酱关闭公司回归个人IP：核心观点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/02-core-viewpoints.md)

### 内容提取

- [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md)

### 内网穿透

- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)

### 决策树

- [应用场景与选型指南](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/08-scenarios.md)

### 分辨率帧率

- [常见问题解答](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/09-faq.md)

### 创业启示

- [Papi酱关闭公司回归个人IP：创业启示与实践要点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/05-entrepreneurship-insights.md)

### 创业建议

- [Papi酱关闭公司回归个人IP：创业启示与实践要点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/05-entrepreneurship-insights.md)

### 创业思维

- [Papi酱关闭公司回归个人IP：核心观点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/02-core-viewpoints.md)

### 创业疑问

- [Papi酱关闭公司回归个人IP：常见问题FAQ](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/07-faq.md)

### 创业趋势

- [Papi酱关闭公司回归个人IP：创业趋势观察](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki.md)
- [Papi酱关闭公司回归个人IP：概述与学习目标](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/00-overview.md)
- [Papi酱关闭公司回归个人IP：案例全景与时间线](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/01-case-timeline.md)
- [Papi酱关闭公司回归个人IP：总结与Takeaway](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/06-summary.md)

### 创作Agent

- [火山引擎KickArt一站式电商营销创作Agent完整学习笔记：六大能力+四大场景+全链路闭环的营销视频生产平台](learning/06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md)

### 前端动画

- [Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！](learning/05-ai-multimodal-content/animejs-threejs-adapter-analysis.md)

### 功能增强

- [潜在改进空间与优化建议](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/07-improvement-suggestions.md)

### 功能对比

- [K3/K4版本差异与产品策略](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/03-version-strategy.md)

### 加密

- [无网远程控制核心技术原理](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/01-core-technology.md)

### 动画库

- [Anime.js 4.5 + Three.js，前端3D动画王炸组合来了！](learning/05-ai-multimodal-content/animejs-threejs-adapter-analysis.md)

### 医疗工控

- [Q2Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/04-product-q2pro-ble.md)
- [应用场景与选型指南](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/08-scenarios.md)

### 协作

- [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md)
- [Claude Tag：核心观点](learning/03-agent-platforms-tools/claude-tag-article/01-core-insights.md)

### 协同远控

- [Q5Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/06-product-q5pro.md)

### 卢松松

- [Papi酱关闭公司回归个人IP：创业趋势观察](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki.md)
- [Papi酱关闭公司回归个人IP：概述与学习目标](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/00-overview.md)
- [Papi酱关闭公司回归个人IP：资源链接](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/08-resources.md)

### 参考资料

- [Claude Tag：参考链接](learning/03-agent-platforms-tools/claude-tag-article/07-resources.md)
- [Papi酱关闭公司回归个人IP：资源链接](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/08-resources.md)
- [相关资源链接](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/09-resources.md)
- [参考资料与链接](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/10-resources.md)

### 双全向麦克风

- [向日葵USB远程摄像头SU1完整学习教程：400万高清、双全向麦克风、远程视频多面手深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md)

### 双卡5G

- [Q5Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/06-product-q5pro.md)

### 双向语音

- [Q5Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/06-product-q5pro.md)

### 双唤醒

- [Q1产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/03-product-q1.md)

### 双电源

- [Q2Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/04-product-q2pro-ble.md)

### 双网络接入

- [五大核心功能模块详解](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/01-core-features.md)

### 反爬

- [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md)

### 发布

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### 口袋级近场

- [Q0.5产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/05-product-q0.5.md)

### 可复用模式

- [Vibe Coding 两大神级 Prompt](learning/02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md)

### 可视化

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 向日葵

- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)
- [向日葵开机盒子产品系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis.md)
- [向日葵USB远程摄像头SU1完整学习教程：400万高清、双全向麦克风、远程视频多面手深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md)
- [向日葵智能远控鼠标MM110/BM110产品学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-mouse-bm110-mm110-analysis.md)
- [向日葵智能插线板P4（4G版）与P1Pro（WiFi版）对比学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md)
- [向日葵智能PDU硬件产品完整学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-pdu-hardware-wiki.md)
- [向日葵（Sunlogin）产品学习系列](learning/07-vendor-product-learning/sunlogin/sunlogin-product-series-index.md)
- [向日葵远程控制安全产品完整学习教程：国民远控的全流程安全体系深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-security-wiki.md)
- [向日葵智能插座C1Pro/C2/C4完整学习教程：远程开机、电量统计、4G户外三款产品对比与深度洞察](learning/07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md)

### 商业模式

- [Papi酱关闭公司回归个人IP：创业趋势观察](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki.md)
- [Papi酱关闭公司回归个人IP：概述与学习目标](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/00-overview.md)
- [Papi酱关闭公司回归个人IP：核心观点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/02-core-viewpoints.md)
- [Papi酱关闭公司回归个人IP：模式深度对比](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/04-model-comparison.md)
- [Papi酱关闭公司回归个人IP：创业启示与实践要点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/05-entrepreneurship-insights.md)
- [深度洞察与行业启示](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/06-insights.md)

### 四不原则

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### 四层架构

- [技术实现解析与硬件规格](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/02-technology-specs.md)

### 国密算法

- [向日葵远程控制安全产品完整学习教程：国民远控的全流程安全体系深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-security-wiki.md)

### 图表

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 增值服务

- [潜在改进空间与优化建议](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/07-improvement-suggestions.md)

### 复杂度预算

- [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md)

### 复盘

- [Claude Tag：知识沉淀闭环](learning/03-agent-platforms-tools/claude-tag-article/06-knowledge-closure.md)

### 复盘闭环

- [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md)

### 多Agent系统

- [Harness Engineering（驾驭工程）系统性学习Wiki](learning/02-agent-engineering-methodology/harness-engineering-wiki.md)

### 多上网方式

- [控控2产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/02-product-kongkong2.md)

### 多智能体

- [Claude Tag：与 SpecWeave 的关联](learning/03-agent-platforms-tools/claude-tag-article/05-specweave-relevance.md)

### 多模态

- [AudioX-Turbo 极速音频生成完整学习教程：4步推理+6种任务统一+920万数据集的Anything-to-Audio框架](learning/05-ai-multimodal-content/audiox-turbo-audio-generation-wiki.md)

### 多源验证

- [B2B/旗舰产品信息源分层采集规范](best-practices/b2b-product-info-collection-sop.md)

### 学习目标

- [概述与学习目标](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/00-overview.md)

### 安全加密

- [常见问题解答](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/09-faq.md)

### 安全性

- [潜在改进空间与优化建议](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/07-improvement-suggestions.md)

### 安全编码

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 完全无网

- [Q0.5产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/05-product-q0.5.md)

### 官方链接

- [相关资源链接](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/09-resources.md)
- [参考资料与链接](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/10-resources.md)

### 定价策略

- [K3/K4版本差异与产品策略](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/03-version-strategy.md)

### 定时开机

- [五大核心功能模块详解](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/01-core-features.md)

### 实践要点

- [Papi酱关闭公司回归个人IP：创业启示与实践要点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/05-entrepreneurship-insights.md)

### 宽温设计

- [Q2Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/04-product-q2pro-ble.md)

### 对抗式审查

- [Vibe Coding 两大神级 Prompt](learning/02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md)

### 小而美

- [Papi酱关闭公司回归个人IP：创业趋势观察](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki.md)
- [Papi酱关闭公司回归个人IP：概述与学习目标](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/00-overview.md)
- [Papi酱关闭公司回归个人IP：核心观点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/02-core-viewpoints.md)
- [Papi酱关闭公司回归个人IP：创业启示与实践要点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/05-entrepreneurship-insights.md)

### 工业级

- [常见问题解答](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/09-faq.md)

### 工业级4G

- [Q2Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/04-product-q2pro-ble.md)

### 差异化

- [竞争优势与市场定位分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/05-competitive-advantage.md)

### 已原子化

- [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md)

### 市场分层

- [K3/K4版本差异与产品策略](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/03-version-strategy.md)

### 市场定位

- [竞争优势与市场定位分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/05-competitive-advantage.md)

### 市场报告

- [参考资料与链接](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/10-resources.md)

### 师生蒸馏

- [AudioX-Turbo 极速音频生成完整学习教程：4步推理+6种任务统一+920万数据集的Anything-to-Audio框架](learning/05-ai-multimodal-content/audiox-turbo-audio-generation-wiki.md)

### 帮助中心

- [相关资源链接](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/09-resources.md)

### 常见问题

- [Papi酱关闭公司回归个人IP：常见问题FAQ](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/07-faq.md)
- [常见问题解答](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/09-faq.md)

### 平台机构

- [Papi酱关闭公司回归个人IP：模式深度对比](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/04-model-comparison.md)

### 应急排障

- [Q0.5产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/05-product-q0.5.md)

### 应用场景

- [概述与产品核心定位](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/00-overview.md)
- [应用场景与选型指南](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/08-scenarios.md)

### 开机盒子

- [向日葵开机盒子产品系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis.md)

### 微信公众号

- [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md)

### 总结

- [Papi酱关闭公司回归个人IP：总结与Takeaway](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/06-summary.md)

### 手术示教

- [Q5Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/06-product-q5pro.md)

### 扩散模型

- [AudioX-Turbo 极速音频生成完整学习教程：4步推理+6种任务统一+920万数据集的Anything-to-Audio框架](learning/05-ai-multimodal-content/audiox-turbo-audio-generation-wiki.md)

### 批量开机

- [五大核心功能模块详解](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/01-core-features.md)

### 技术历史

- [WOL技术背景知识](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/08-wol-technology.md)

### 技术名词

- [参考资料与链接](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/10-resources.md)

### 技术实现

- [技术实现解析与硬件规格](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/02-technology-specs.md)

### 技术文档

- [相关资源链接](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/09-resources.md)

### 技术演进

- [五款产品横向对比分析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/07-comparison.md)

### 技术路线对比

- [五款产品横向对比分析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/07-comparison.md)

### 投前预审

- [火山引擎KickArt一站式电商营销创作Agent完整学习笔记：六大能力+四大场景+全链路闭环的营销视频生产平台](learning/06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md)

### 排查

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 控控2

- [控控2产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/02-product-kongkong2.md)

### 改进建议

- [潜在改进空间与优化建议](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/07-improvement-suggestions.md)

### 故障排查

- [WOL技术背景知识](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/08-wol-technology.md)

### 数据

- [Claude Tag：重要数据](learning/03-agent-platforms-tools/claude-tag-article/03-key-data.md)

### 数据中心

- [向日葵智能PDU硬件产品完整学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-pdu-hardware-wiki.md)

### 文件传输

- [Q2Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/04-product-q2pro-ble.md)

### 文案策略

- [网页设计与用户体验分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/04-web-ux-analysis.md)

### 方法论

- [Claude Tag：知识沉淀闭环](learning/03-agent-platforms-tools/claude-tag-article/06-knowledge-closure.md)

### 旗舰IPKVM

- [控控2产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/02-product-kongkong2.md)

### 无网远控

- [向日葵五款无网远程控制硬件深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki.md)

### 无网远控价值

- [概述与学习目标](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/00-overview.md)

### 时间线

- [Papi酱关闭公司回归个人IP：案例全景与时间线](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/01-case-timeline.md)

### 智能排插

- [向日葵智能PDU硬件产品完整学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-pdu-hardware-wiki.md)

### 智能插座

- [向日葵智能插座C1Pro/C2/C4完整学习教程：远程开机、电量统计、4G户外三款产品对比与深度洞察](learning/07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md)

### 智能插线板

- [向日葵智能插线板P4（4G版）与P1Pro（WiFi版）对比学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md)

### 智能硬件

- [向日葵开机盒子产品系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis.md)
- [向日葵USB远程摄像头SU1完整学习教程：400万高清、双全向麦克风、远程视频多面手深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md)
- [向日葵智能远控鼠标MM110/BM110产品学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-mouse-bm110-mm110-analysis.md)
- [向日葵智能插线板P4（4G版）与P1Pro（WiFi版）对比学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md)
- [向日葵智能PDU硬件产品完整学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-pdu-hardware-wiki.md)
- [向日葵（Sunlogin）产品学习系列](learning/07-vendor-product-learning/sunlogin/sunlogin-product-series-index.md)
- [向日葵智能插座C1Pro/C2/C4完整学习教程：远程开机、电量统计、4G户外三款产品对比与深度洞察](learning/07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md)
- [深度洞察与行业启示](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/06-insights.md)

### 智能远控鼠标

- [向日葵智能远控鼠标MM110/BM110产品学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-mouse-bm110-mm110-analysis.md)

### 未分类

- [MDI (Markdown Interface) 深度研究报告](mdi-research-report.md)
- [MDI Spec v1.0：Markdown即接口规范](mdi-spec-v1.0.md)
- [stage-guardrails-guide](stage-guardrails-guide.md)
- [three-layer-routing](three-layer-routing.md)
- [VENDOR-INTEGRATION](VENDOR-INTEGRATION.md)
- [00、概述与背景](learning/01-agent-protocols-interfaces/agent-communication-protocols/00-overview.md)
- [01、MCP协议详解：Model Context Protocol](learning/01-agent-protocols-interfaces/agent-communication-protocols/01-mcp.md)
- [02、ACP协议详解：Agent Communication Protocol](learning/01-agent-protocols-interfaces/agent-communication-protocols/02-acp.md)
- [03、A2A协议详解：Agent-to-Agent Protocol](learning/01-agent-protocols-interfaces/agent-communication-protocols/03-a2a.md)
- [04、ANP协议概述：Agent Network Protocol](learning/01-agent-protocols-interfaces/agent-communication-protocols/04-anp.md)
- [05、协议对比与分层架构](learning/01-agent-protocols-interfaces/agent-communication-protocols/05-comparison.md)
- [06、交互流程与协作模式](learning/01-agent-protocols-interfaces/agent-communication-protocols/06-flows.md)
- [07、技术实现要点与代码示例](learning/01-agent-protocols-interfaces/agent-communication-protocols/07-implementation.md)
- [08、典型应用场景](learning/01-agent-protocols-interfaces/agent-communication-protocols/08-scenarios.md)
- [09、术语表](learning/01-agent-protocols-interfaces/agent-communication-protocols/09-glossary.md)
- [10、资源与参考链接](learning/01-agent-protocols-interfaces/agent-communication-protocols/10-resources.md)
- [11、快速参考速查表](learning/01-agent-protocols-interfaces/agent-communication-protocols/11-quick-reference.md)
- [一、概述](learning/01-agent-protocols-interfaces/agent-skills-wiki/00-overview.md)
- [二、核心机制：渐进式披露（Progressive Disclosure）](learning/01-agent-protocols-interfaces/agent-skills-wiki/01-progressive-disclosure.md)
- [三、目录结构规范](learning/01-agent-protocols-interfaces/agent-skills-wiki/02-directory-structure.md)
- [四、SKILL.md 格式规范](learning/01-agent-protocols-interfaces/agent-skills-wiki/03-skill-md-format.md)
- [04-quickstart](learning/01-agent-protocols-interfaces/agent-skills-wiki/04-quickstart.md)
- [[分析标题]](learning/01-agent-protocols-interfaces/agent-skills-wiki/05-best-practices.md)
- [/// script](learning/01-agent-protocols-interfaces/agent-skills-wiki/06-scripts-guide.md)
- [此示例使用 Claude Code 的 JSON 输出来检查 Skill 工具调用](learning/01-agent-protocols-interfaces/agent-skills-wiki/07-description-optimization.md)
- [08-evals](learning/01-agent-protocols-interfaces/agent-skills-wiki/08-evals.md)
- [验证一个技能目录](learning/01-agent-protocols-interfaces/agent-skills-wiki/09-skills-ref-tool.md)
- [10-file-references](learning/01-agent-protocols-interfaces/agent-skills-wiki/10-file-references.md)
- [11-project-comparison](learning/01-agent-protocols-interfaces/agent-skills-wiki/11-project-comparison.md)
- [技术上无效的 YAML——冒号破坏了解析](learning/01-agent-protocols-interfaces/agent-skills-wiki/12-client-implementation.md)
- [13-resources](learning/01-agent-protocols-interfaces/agent-skills-wiki/13-resources.md)
- [My Skill](learning/01-agent-protocols-interfaces/agent-skills-wiki/14-quick-reference.md)
- [dspark-paper-wiki](learning/02-agent-engineering-methodology/dspark-paper-wiki.md)
- [Harness Engineering（驾驭工程）：概述与学习目标](learning/02-agent-engineering-methodology/harness-engineering-wiki/00-overview.md)
- [范式演进：三代AI工程](learning/02-agent-engineering-methodology/harness-engineering-wiki/01-paradigm-evolution.md)
- [四条反直觉铁律](learning/02-agent-engineering-methodology/harness-engineering-wiki/02-four-iron-laws.md)
- [六大工程模式](learning/02-agent-engineering-methodology/harness-engineering-wiki/03-six-patterns.md)
- [实战案例：悟空AI招聘](learning/02-agent-engineering-methodology/harness-engineering-wiki/04-wukong-case-study.md)
- [行业标杆地图](learning/02-agent-engineering-methodology/harness-engineering-wiki/05-industry-benchmarks.md)
- [未来趋势与六条心法](learning/02-agent-engineering-methodology/harness-engineering-wiki/06-future-trends.md)
- [批判性思考与评估](learning/02-agent-engineering-methodology/harness-engineering-wiki/07-critical-thinking.md)
- [常见问题（FAQ）](learning/02-agent-engineering-methodology/harness-engineering-wiki/08-faq.md)
- [资源链接](learning/02-agent-engineering-methodology/harness-engineering-wiki/09-resources.md)
- [Headroom：概述与学习目标](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/00-overview.md)
- [核心架构与设计理念](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/01-core-architecture.md)
- [六种压缩算法详解](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/02-compression-algorithms.md)
- [CCR可逆机制深度解析](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/03-ccr-mechanism.md)
- [四种接入方式详解](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/04-integration-methods.md)
- [效果验证与数据分析](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/05-performance-data.md)
- [跨Agent记忆与自动学习](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/06-advanced-features.md)
- [快速上手指南](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/07-quick-start.md)
- [深度洞察与模式萃取](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/08-insights-patterns.md)
- [常见问题与资源链接](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/09-faq-resources.md)
- [总结与Takeaways](learning/02-agent-engineering-methodology/headroom-context-compression-wiki/10-summary.md)
- [LongCat-2.0 Agent能力实测：概述与学习目标](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/00-overview.md)
- [LongCat-2.0核心概念解析](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/01-core-concepts.md)
- [Claude Code接入LongCat-2.0配置指南](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/02-claude-code-integration.md)
- [BI数据看板项目实战全流程](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/03-bi-dashboard-demo.md)
- [Token效率对比分析](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/04-token-efficiency.md)
- [Loop Engineering方法论解析](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/05-loop-engineering.md)
- [总结与回顾](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/06-summary.md)
- [常见问题（FAQ）](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/07-faq.md)
- [资源与参考链接](learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/08-resources.md)
- [MopMonk 安全 Agent Wiki 教程](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki.md)
- [Rainman Translate Book Wiki 教程](learning/03-agent-platforms-tools/rainman-translate-book-wiki.md)
- [教程概述与学习目标](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/00-overview.md)
- [核心概念解析（一）：CyberGym、Harness与PoC](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/01-core-concepts.md)
- [MiniMax M3基座：国产开源的六边形战士](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/02-minimax-m3.md)
- [三大核心技术：记忆驱动的安全Agent范式](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/03-core-technologies.md)
- [步骤式学习导读：入门/进阶/深入三层](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/04-learning-guide.md)
- [常见问题解答（FAQ）](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/05-faq.md)
- [相关资源链接](learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/06-resources.md)
- [概述与学习目标](learning/03-agent-platforms-tools/open-code-review-wiki/00-overview.md)
- [核心概念与设计理念](learning/03-agent-platforms-tools/open-code-review-wiki/01-core-concepts.md)
- [安装与配置指南](learning/03-agent-platforms-tools/open-code-review-wiki/02-installation.md)
- [使用流程与命令详解](learning/03-agent-platforms-tools/open-code-review-wiki/03-usage.md)
- [关键技术优化](learning/03-agent-platforms-tools/open-code-review-wiki/04-optimizations.md)
- [集成与高级用法](learning/03-agent-platforms-tools/open-code-review-wiki/05-integrations.md)
- [效果验证与质量评估](learning/03-agent-platforms-tools/open-code-review-wiki/06-effectiveness.md)
- [局限性与对比](learning/03-agent-platforms-tools/open-code-review-wiki/07-limitations.md)
- [总结与展望](learning/03-agent-platforms-tools/open-code-review-wiki/08-summary.md)
- [常见问题（FAQ）](learning/03-agent-platforms-tools/open-code-review-wiki/09-faq.md)
- [资源与参考链接](learning/03-agent-platforms-tools/open-code-review-wiki/10-resources.md)
- [教程概述与学习目标](learning/03-agent-platforms-tools/rainman-translate-book-wiki/00-overview.md)
- [核心功能详解](learning/03-agent-platforms-tools/rainman-translate-book-wiki/01-core-concepts.md)
- [安装部署指南](learning/03-agent-platforms-tools/rainman-translate-book-wiki/02-installation.md)
- [使用流程](learning/03-agent-platforms-tools/rainman-translate-book-wiki/03-usage.md)
- [局限性与注意事项](learning/03-agent-platforms-tools/rainman-translate-book-wiki/04-limitations.md)
- [总结与回顾](learning/03-agent-platforms-tools/rainman-translate-book-wiki/05-summary.md)
- [常见问题](learning/03-agent-platforms-tools/rainman-translate-book-wiki/06-faq.md)
- [资源链接](learning/03-agent-platforms-tools/rainman-translate-book-wiki/07-resources.md)
- [ExecutableBooks 与 MyST Markdown 完整学习指南](learning/04-docs-markup-tooling/executablebooks-myst-guide-wiki.md)
- [ExecutableBooks 生态概览](learning/04-docs-markup-tooling/executablebooks-myst-guide/00-overview.md)
- [MyST Markdown 核心语法](learning/04-docs-markup-tooling/executablebooks-myst-guide/01-myst-syntax.md)
- [MyST 项目结构与 myst.yml 配置](learning/04-docs-markup-tooling/executablebooks-myst-guide/02-project-structure.md)
- [Frontmatter 配置详解](learning/04-docs-markup-tooling/executablebooks-myst-guide/03-frontmatter-config.md)
- [目录结构（TOC）配置指南](learning/04-docs-markup-tooling/executablebooks-myst-guide/04-table-of-contents.md)
- [MyST Markdown 使用最佳实践](learning/04-docs-markup-tooling/executablebooks-myst-guide/05-best-practices.md)
- [参考资源与链接汇总](learning/04-docs-markup-tooling/executablebooks-myst-guide/06-resources.md)
- [Admonitions（提示框）样式大全](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/admonitions.md)
- [MyST Markdown 基础语法示例](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/basic-syntax.md)
- [交叉引用示例](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/cross-references.md)
- [GitHub Tools MCP Server](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/mcp-server-demo.md)
- [MyST Roles（行内扩展）示例](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/roles-demo.md)
- [GitHub Tools MCP Server](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/poc/github-tools.md)
- [Weather Service MCP Server](learning/04-docs-markup-tooling/executablebooks-myst-guide/examples/poc/weather-service.md)
- [第0章：快速上手（Quick Start）](learning/04-docs-markup-tooling/myst-markdown-tutorial/00-quick-start.md)
- [第1章：MyST 简介与 CommonMark 对比](learning/04-docs-markup-tooling/myst-markdown-tutorial/01-introduction.md)
- [第2章：基础语法（上）- 文本与格式](learning/04-docs-markup-tooling/myst-markdown-tutorial/02-basic-syntax-part1.md)
- [第3章：基础语法（下）- 列表、链接与图片](learning/04-docs-markup-tooling/myst-markdown-tutorial/03-basic-syntax-part2.md)
- [第4章：高级功能 - Directives 和 Roles](learning/04-docs-markup-tooling/myst-markdown-tutorial/04-advanced-directives-roles.md)
- [第5章：高级功能 - 交叉引用](learning/04-docs-markup-tooling/myst-markdown-tutorial/05-advanced-cross-references.md)
- [第6章：高级功能 - 数学公式与代码块](learning/04-docs-markup-tooling/myst-markdown-tutorial/06-advanced-math-code.md)
- [第7章：高级功能 - 注释、脚注与参考文献](learning/04-docs-markup-tooling/myst-markdown-tutorial/07-advanced-notes-citations.md)
- [第8章：扩展组件 - 提示框（Admonitions）](learning/04-docs-markup-tooling/myst-markdown-tutorial/08-components-admonitions.md)
- [第9章：扩展组件 - 卡片、下拉与标签页](learning/04-docs-markup-tooling/myst-markdown-tutorial/09-components-ui.md)
- [第10章：扩展组件 - 图片与表格](learning/04-docs-markup-tooling/myst-markdown-tutorial/10-components-figures.md)
- [第11章：工具链集成 - Sphinx + myst-parser](learning/04-docs-markup-tooling/myst-markdown-tutorial/11-tooling-sphinx.md)
- [第12章：工具链集成 - Jupyter Book v1](learning/04-docs-markup-tooling/myst-markdown-tutorial/12-tooling-jupyter-book.md)
- [第13章：工具链集成 - mystmd（新一代）](learning/04-docs-markup-tooling/myst-markdown-tutorial/13-tooling-mystmd.md)
- [第14章：实战案例 - 技术文档写作](learning/04-docs-markup-tooling/myst-markdown-tutorial/14-case-study-tech-docs.md)
- [第15章：实战案例 - 学术论文与书籍](learning/04-docs-markup-tooling/myst-markdown-tutorial/15-case-study-academic.md)
- [第16章：常见问题解答（FAQ）](learning/04-docs-markup-tooling/myst-markdown-tutorial/16-faq.md)
- [附录A：MyST Markdown 速查表](learning/04-docs-markup-tooling/myst-markdown-tutorial/appendix/cheat-sheet.md)
- [附录B：资源推荐](learning/04-docs-markup-tooling/myst-markdown-tutorial/appendix/resources.md)
- [示例：Admonitions 提示框样式大全](learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/admonitions-demo.md)
- [示例：图片与表格](learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/figures-tables-demo.md)
- [模板：学术论文模板](learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/paper-template.md)
- [模板：技术文档模板](learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/tech-doc-template.md)
- [示例：卡片、下拉与标签页](learning/04-docs-markup-tooling/myst-markdown-tutorial/examples/ui-components-demo.md)
- [ian-xiaohei-illustrations](learning/05-ai-multimodal-content/ian-xiaohei-illustrations.md)
- [MDI研究报告 - 执行摘要](mdi-research/00-executive-summary.md)
- [MDI研究报告 - 可行性分析](mdi-research/01-feasibility-analysis.md)
- [MDI研究报告 - 生态对比分析](mdi-research/02-ecosystem-comparison.md)
- [MDI研究报告 - 技术架构深度解析](mdi-research/03-technical-architecture.md)
- [MDI研究报告 - 工具链使用指南](mdi-research/04-toolchain-guide.md)
- [MDI研究报告 - 版本控制与变更管理最佳实践](mdi-research/05-versioning-best-practices.md)
- [MDI研究报告 - 未来演进方向](mdi-research/06-future-evolution.md)
- [MDI研究报告 - 结论](mdi-research/07-conclusion.md)
- [00、总览：MyST Markdown 统一化接口生态体系](myst-unified-ecosystem/00-overview.md)
- [01、IDL：接口描述语言](myst-unified-ecosystem/01-idl.md)
- [02、Interface：行为契约](myst-unified-ecosystem/02-interface.md)
- [03、API：应用程序编程接口](myst-unified-ecosystem/03-api.md)
- [04、ABI：应用程序二进制接口](myst-unified-ecosystem/04-abi.md)
- [05、Protocol：通信协议](myst-unified-ecosystem/05-protocol.md)
- [06、Implementation：具体实现](myst-unified-ecosystem/06-implementation.md)
- [07、MCP：Model Context Protocol](myst-unified-ecosystem/07-mcp.md)
- [08、ACP：Agent Communication Protocol](myst-unified-ecosystem/08-acp.md)
- [09、A2A：Agent-to-Agent](myst-unified-ecosystem/09-a2a.md)
- [10、ANP：Agent Network Protocol](myst-unified-ecosystem/10-anp.md)
- [11、MDI：Markdown Document Interface](myst-unified-ecosystem/11-mdi.md)
- [12、关系全景：11个概念的形式化关系与交互](myst-unified-ecosystem/12-relationships.md)
- [discourse-api-research](operations/discourse-api-research.md)

### 术语

- [Claude Tag：关键概念与术语](learning/03-agent-platforms-tools/claude-tag-article/02-key-concepts.md)

### 术语解释

- [参考资料与链接](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/10-resources.md)

### 机房运维

- [向日葵智能PDU硬件产品完整学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-pdu-hardware-wiki.md)
- [控控2产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/02-product-kongkong2.md)
- [应用场景与选型指南](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/08-scenarios.md)

### 李佳琦

- [Papi酱关闭公司回归个人IP：行业观察与案例](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/03-industry-trend.md)

### 李子柒

- [Papi酱关闭公司回归个人IP：行业观察与案例](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/03-industry-trend.md)

### 架构模式

- [无网远程控制核心技术原理](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/01-core-technology.md)

### 核心功能

- [五大核心功能模块详解](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/01-core-features.md)

### 核心技术

- [无网远程控制核心技术原理](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/01-core-technology.md)

### 核心要点

- [Papi酱关闭公司回归个人IP：总结与Takeaway](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/06-summary.md)

### 核心观点

- [Papi酱关闭公司回归个人IP：核心观点](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/02-core-viewpoints.md)

### 概述

- [概述与产品核心定位](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/00-overview.md)
- [概述与学习目标](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/00-overview.md)

### 模型蒸馏

- [AudioX-Turbo 极速音频生成完整学习教程：4步推理+6种任务统一+920万数据集的Anything-to-Audio框架](learning/05-ai-multimodal-content/audiox-turbo-audio-generation-wiki.md)

### 模式入库

- [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md)
- [Claude Tag：知识沉淀闭环](learning/03-agent-platforms-tools/claude-tag-article/06-knowledge-closure.md)

### 模式对比

- [Papi酱关闭公司回归个人IP：模式深度对比](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/04-model-comparison.md)

### 模板

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 正则

- [HTML 正文提取操作指南](operations/html-body-extraction.md)

### 正文提取

- [HTML 正文提取操作指南](operations/html-body-extraction.md)

### 泰洋川禾

- [Papi酱关闭公司回归个人IP：案例全景与时间线](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/01-case-timeline.md)

### 洋葱头

- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)

### 流量卡

- [常见问题解答](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/09-faq.md)

### 消费级入门

- [Q1产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/03-product-q1.md)

### 涉密场景

- [应用场景与选型指南](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/08-scenarios.md)

### 涉密运维

- [Q0.5产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/05-product-q0.5.md)

### 深度洞察

- [深度洞察与行业启示](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/06-insights.md)

### 火山引擎

- [火山引擎KickArt一站式电商营销创作Agent完整学习笔记：六大能力+四大场景+全链路闭环的营销视频生产平台](learning/06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md)

### 爆款裂变

- [火山引擎KickArt一站式电商营销创作Agent完整学习笔记：六大能力+四大场景+全链路闭环的营销视频生产平台](learning/06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md)

### 版本信息

- [参考资料与链接](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/10-resources.md)

### 版本差异

- [K3/K4版本差异与产品策略](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/03-version-strategy.md)

### 物理隔离

- [Q0.5产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/05-product-q0.5.md)

### 独立分控

- [向日葵智能插线板P4（4G版）与P1Pro（WiFi版）对比学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md)

### 生态协同

- [深度洞察与行业启示](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/06-insights.md)

### 用户体验

- [网页设计与用户体验分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/04-web-ux-analysis.md)
- [潜在改进空间与优化建议](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/07-improvement-suggestions.md)

### 电商营销

- [火山引擎KickArt一站式电商营销创作Agent完整学习笔记：六大能力+四大场景+全链路闭环的营销视频生产平台](learning/06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md)

### 电量监控

- [向日葵智能插线板P4（4G版）与P1Pro（WiFi版）对比学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md)

### 电量统计

- [向日葵智能插座C1Pro/C2/C4完整学习教程：远程开机、电量统计、4G户外三款产品对比与深度洞察](learning/07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md)

### 痛点解决

- [深度洞察与行业启示](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/06-insights.md)

### 百兆网口

- [Q1产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/03-product-q1.md)

### 目标用户

- [概述与产品核心定位](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/00-overview.md)

### 相关Wiki

- [参考资料与链接](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/10-resources.md)

### 相关资源

- [相关资源链接](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/09-resources.md)

### 相关阅读

- [Papi酱关闭公司回归个人IP：资源链接](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/08-resources.md)

### 看门狗

- [控控2产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/02-product-kongkong2.md)

### 知识沉淀

- [Claude Tag 文章知识捕获](learning/03-agent-platforms-tools/claude-tag-article.md)
- [Claude Tag：与 SpecWeave 的关联](learning/03-agent-platforms-tools/claude-tag-article/05-specweave-relevance.md)

### 短视频创作

- [火山引擎KickArt一站式电商营销创作Agent完整学习笔记：六大能力+四大场景+全链路闭环的营销视频生产平台](learning/06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md)

### 研究背景

- [概述与产品核心定位](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/00-overview.md)

### 硬件

- [向日葵五款无网远程控制硬件深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki.md)

### 硬件产品

- [向日葵开机盒子产品系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis.md)

### 硬件对比

- [向日葵智能远控鼠标MM110/BM110产品学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-mouse-bm110-mm110-analysis.md)

### 硬件规格

- [技术实现解析与硬件规格](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/02-technology-specs.md)

### 社区

- [Claude Tag：原文结构框架](learning/03-agent-platforms-tools/claude-tag-article/04-article-structure.md)

### 社区支持

- [相关资源链接](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/09-resources.md)

### 移动办公

- [向日葵智能远控鼠标MM110/BM110产品学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-mouse-bm110-mm110-analysis.md)

### 竞争优势

- [竞争优势与市场定位分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/05-competitive-advantage.md)

### 竞品分析

- [竞争优势与市场定位分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/05-competitive-advantage.md)

### 第一性原理

- [Vibe Coding 两大神级 Prompt](learning/02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md)

### 等保2.0

- [向日葵远程控制安全产品完整学习教程：国民远控的全流程安全体系深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-security-wiki.md)

### 系列索引

- [向日葵（Sunlogin）产品学习系列](learning/07-vendor-product-learning/sunlogin/sunlogin-product-series-index.md)

### 索引截取

- [HTML 正文提取操作指南](operations/html-body-extraction.md)

### 统计

- [Claude Tag：重要数据](learning/03-agent-platforms-tools/claude-tag-article/03-key-data.md)

### 网络协议栈

- [技术实现解析与硬件规格](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/02-technology-specs.md)

### 网络唤醒

- [WOL技术背景知识](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/08-wol-technology.md)

### 网络安全

- [向日葵远程控制安全产品完整学习教程：国民远控的全流程安全体系深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-security-wiki.md)

### 网络拓扑

- [五大核心功能模块详解](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/01-core-features.md)

### 网页设计

- [网页设计与用户体验分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/04-web-ux-analysis.md)

### 罗永浩

- [Papi酱关闭公司回归个人IP：行业观察与案例](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/03-industry-trend.md)

### 联调

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 自动化

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### 自我演进

- [Claude Tag：与 SpecWeave 的关联](learning/03-agent-platforms-tools/claude-tag-article/05-specweave-relevance.md)

### 花生壳

- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)

### 葵码登录

- [Q5Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/06-product-q5pro.md)

### 蒲公英

- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)

### 蓝牙

- [向日葵五款无网远程控制硬件深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki.md)

### 蓝牙5.0

- [Q1产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/03-product-q1.md)

### 蓝牙配网

- [向日葵智能插座C1Pro/C2/C4完整学习教程：远程开机、电量统计、4G户外三款产品对比与深度洞察](learning/07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md)
- [无网远程控制核心技术原理](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/01-core-technology.md)

### 蓝牙鼠标

- [向日葵智能远控鼠标MM110/BM110产品学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-mouse-bm110-mm110-analysis.md)

### 行业启示

- [深度洞察与行业启示](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/06-insights.md)

### 行业趋势

- [Papi酱关闭公司回归个人IP：行业观察与案例](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/03-industry-trend.md)

### 视觉设计

- [网页设计与用户体验分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/04-web-ux-analysis.md)

### 视频会议

- [向日葵USB远程摄像头SU1完整学习教程：400万高清、双全向麦克风、远程视频多面手深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md)

### 视频配音

- [AudioX-Turbo 极速音频生成完整学习教程：4步推理+6种任务统一+920万数据集的Anything-to-Audio框架](learning/05-ai-multimodal-content/audiox-turbo-audio-generation-wiki.md)

### 论坛

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### 设备绑定

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 贝锐

- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)

### 贝锐科技

- [向日葵开机盒子产品系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis.md)
- [向日葵USB远程摄像头SU1完整学习教程：400万高清、双全向麦克风、远程视频多面手深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md)
- [向日葵智能远控鼠标MM110/BM110产品学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-mouse-bm110-mm110-analysis.md)
- [向日葵智能插线板P4（4G版）与P1Pro（WiFi版）对比学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md)
- [向日葵智能PDU硬件产品完整学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-pdu-hardware-wiki.md)
- [向日葵（Sunlogin）产品学习系列](learning/07-vendor-product-learning/sunlogin/sunlogin-product-series-index.md)
- [向日葵智能插座C1Pro/C2/C4完整学习教程：远程开机、电量统计、4G户外三款产品对比与深度洞察](learning/07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md)

### 资源链接

- [Papi酱关闭公司回归个人IP：资源链接](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/08-resources.md)

### 超级IP

- [Papi酱关闭公司回归个人IP：行业观察与案例](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/03-industry-trend.md)

### 超级个体

- [Papi酱关闭公司回归个人IP：模式深度对比](learning/06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki/04-model-comparison.md)

### 软硬件协同

- [竞争优势与市场定位分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/05-competitive-advantage.md)

### 软硬协同架构

- [技术实现解析与硬件规格](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/02-technology-specs.md)

### 软硬结合

- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)

### 边界case

- [Parser 复杂度预算 Checklist](best-practices/parser-complexity-budget.md)

### 边界标记

- [HTML 正文提取操作指南](operations/html-body-extraction.md)

### 运维

- [向日葵五款无网远程控制硬件深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki.md)

### 远控安全

- [向日葵远程控制安全产品完整学习教程：国民远控的全流程安全体系深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-security-wiki.md)

### 远程办公

- [向日葵开机盒子产品系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis.md)
- [向日葵USB远程摄像头SU1完整学习教程：400万高清、双全向麦克风、远程视频多面手深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md)
- [向日葵智能插线板P4（4G版）与P1Pro（WiFi版）对比学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md)
- [向日葵智能插座C1Pro/C2/C4完整学习教程：远程开机、电量统计、4G户外三款产品对比与深度洞察](learning/07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md)
- [概述与产品核心定位](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/00-overview.md)
- [Q1产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/03-product-q1.md)

### 远程医疗

- [向日葵USB远程摄像头SU1完整学习教程：400万高清、双全向麦克风、远程视频多面手深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md)
- [Q5Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/06-product-q5pro.md)

### 远程开机

- [向日葵开机盒子产品系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis.md)
- [向日葵智能插座C1Pro/C2/C4完整学习教程：远程开机、电量统计、4G户外三款产品对比与深度洞察](learning/07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md)
- [五大核心功能模块详解](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/01-core-features.md)
- [竞争优势与市场定位分析](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/05-competitive-advantage.md)

### 远程控制

- [向日葵智能远控鼠标MM110/BM110产品学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/sunlogin-mouse-bm110-mm110-analysis.md)
- [向日葵五款无网远程控制硬件深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki.md)
- [向日葵智能插线板P4（4G版）与P1Pro（WiFi版）对比学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md)
- [向日葵智能PDU硬件产品完整学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-pdu-hardware-wiki.md)
- [向日葵（Sunlogin）产品学习系列](learning/07-vendor-product-learning/sunlogin/sunlogin-product-series-index.md)
- [向日葵远程控制安全产品完整学习教程：国民远控的全流程安全体系深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-security-wiki.md)

### 远程电源管理

- [向日葵智能PDU硬件产品完整学习教程](learning/07-vendor-product-learning/sunlogin/sunlogin-pdu-hardware-wiki.md)

### 远程监控

- [向日葵USB远程摄像头SU1完整学习教程：400万高清、双全向麦克风、远程视频多面手深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md)

### 远程视频

- [向日葵USB远程摄像头SU1完整学习教程：400万高清、双全向麦克风、远程视频多面手深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md)

### 远程运维

- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)

### 远程连接

- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)

### 选型参考

- [五款产品横向对比分析](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/07-comparison.md)

### 选型指南

- [应用场景与选型指南](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/08-scenarios.md)

### 选型速查表

- [应用场景与选型指南](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/08-scenarios.md)

### 配网

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 链接

- [Claude Tag：参考链接](learning/03-agent-platforms-tools/claude-tag-article/07-resources.md)

### 闭环

- [Claude Tag：知识沉淀闭环](learning/03-agent-platforms-tools/claude-tag-article/06-knowledge-closure.md)
- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 阅读导航

- [概述与学习目标](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/00-overview.md)

### 防浪涌

- [Q2Pro产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/04-product-q2pro-ble.md)

### 防跳板

- [Q0.5产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/05-product-q0.5.md)

### 阶段守卫

- [Claude Tag：与 SpecWeave 的关联](learning/03-agent-platforms-tools/claude-tag-article/05-specweave-relevance.md)

### 降级策略

- [HTML 正文提取操作指南](operations/html-body-extraction.md)
- [微信公众号文章内容提取操作指南](operations/wechat-mp-content-extraction.md)

### 集成方案

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### 零信任

- [向日葵远程控制安全产品完整学习教程：国民远控的全流程安全体系深度解析](learning/07-vendor-product-learning/sunlogin/sunlogin-security-wiki.md)

### 音乐生成

- [AudioX-Turbo 极速音频生成完整学习教程：4步推理+6种任务统一+920万数据集的Anything-to-Audio框架](learning/05-ai-multimodal-content/audiox-turbo-audio-generation-wiki.md)

### 音视频

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 音频生成

- [AudioX-Turbo 极速音频生成完整学习教程：4步推理+6种任务统一+920万数据集的Anything-to-Audio框架](learning/05-ai-multimodal-content/audiox-turbo-audio-generation-wiki.md)

### 验收

- [Tuya IPC 最小闭环跑通路径](operations/tuya-ipc-minimal-closed-loop.md)

### 高性价比

- [Q1产品详解](learning/07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki/03-product-q1.md)

### 魔术包

- [技术实现解析与硬件规格](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/02-technology-specs.md)
- [WOL技术背景知识](learning/07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis/08-wol-technology.md)

### 龙虾

- [贝锐（Oray）AI产品矩阵系统性学习与深度洞察分析报告](learning/07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)

## 最近更新

| 标题 | 日期 | 分类 |
|------|------|------|
| [方法论模式第3次验证报告：模板批量升级场景](best-practices/pattern-validation-v3-template-batch-upgrade.md) | 2026-07-06 | best-practices |
| [多文件编辑操作可靠性指南](best-practices/multi-file-edit-reliability.md) | 2026-07-05 | best-practices |
| [Learning Wiki 主题分类体系](learning/CATEGORIES.md) | 2026-07-05 | learning |
| [Learning Wiki 学习路径推荐表](learning/LEARNING-PATHS.md) | 2026-07-05 | learning |
| [Ch00 - TVM FFI 概述与定位](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/00-overview.md) | 2026-07-05 | unknown |
| [Ch01 - 系统架构与设计理念](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/01-architecture.md) | 2026-07-05 | unknown |
| [02 - C++ 核心 API：Any、Object、Function、Tensor](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/02-cpp-core-api.md) | 2026-07-05 | unknown |
| [03 - 类型系统：DType、Enum、Optional、String](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/03-type-system.md) | 2026-07-05 | unknown |
| [04 - 容器类型：Array、Map、Dict、List、Tuple、Shape、Variant](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/04-containers.md) | 2026-07-05 | unknown |
| [05 - 反射与注册机制](learning/01-agent-protocols-interfaces/tvm-ffi-wiki/05-reflection.md) | 2026-07-05 | unknown |

## 相关资源

### 回溯报告

- [项目硬编码问题系统性复盘报告](../retrospective/hardcode-retrospective-report.md)
- [提示词工程 — 可迁移模式、模板与方法论萃取](../retrospective/prompt-extraction.md)
- [复盘文档体系](../retrospective/README.md)

### 任务总结

- [任务执行总结报告](../task-summaries/task-summary-atomic-commit-20260706.md)
- [任务执行总结报告](../task-summaries/task-summary-git-local-clone-bug-20260701.md)
- [任务执行总结报告](../task-summaries/task-summary-readme-creation-20260623.md)

## 使用指南

### 如何添加知识条目

1. 在 `docs/knowledge/` 下选择对应的分类目录（如 `operations/`、`platform/` 等）
2. 复制 `template.md` 作为模板，创建新的 `.md` 文件
3. 填写 YAML frontmatter 元数据（标题、分类、标签、日期、摘要等）
4. 在正文中按照模板结构编写内容
5. 运行 `python scripts/generate_index.py` 重新生成索引

### 如何检索

- **按类别浏览**：使用上方的「按类别浏览」章节，按操作、平台、排错等分类查找
- **按标签检索**：使用上方的「标签索引」章节，按关键词标签快速定位
- **按时间排序**：查看「最近更新」章节，了解最新添加的知识条目
- **全文搜索**：在项目根目录使用 `grep -r "关键词" docs/knowledge/` 进行全文搜索

### 如何维护

- **定期整理**：每月检查一次知识条目，更新过时内容，补充遗漏信息
- **标签规范化**：使用统一的标签命名，避免同义词分散（如 `powershell` 和 `ps`）
- **及时归档**：完成任务或解决问题后，及时将经验沉淀为知识条目
- **索引更新**：每次添加、修改或删除知识条目后，运行本脚本重新生成索引

---

*索引自动生成于 2026-07-06 10:02:35*
