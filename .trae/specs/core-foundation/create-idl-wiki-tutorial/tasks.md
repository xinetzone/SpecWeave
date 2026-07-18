# Tasks

## 任务总览

本 spec 共 9 个文档创建任务，按章节顺序编排。任务 1-9 之间存在隐式依赖（导航链接需指向前后章节），但内容创作可并行。任务 10 为统一质量验证，必须在任务 1-9 完成后执行。

- [x] Task 1: 创建 `00-overview.md` 教程总览与导航索引
- [x] Task 2: 创建 `01-what-is-idl.md` IDL 定义与作用
- [x] Task 3: 创建 `02-syntax-basics.md` IDL 基本语法结构
- [x] Task 4: 创建 `03-major-idl-specs.md` 主要 IDL 规范介绍
- [x] Task 5: 创建 `04-comparison.md` IDL 规范对比
- [x] Task 6: 创建 `05-toolchain.md` IDL 编译流程与工具链
- [x] Task 7: 创建 `06-use-cases.md` 实际应用案例与最佳实践
- [x] Task 8: 创建 `07-vs-modern-formats.md` 与现代接口描述方式对比
- [x] Task 9: 创建 `08-resources.md` 学习资源与参考资料
- [x] Task 10: 统一质量验证（文件大小、链接、frontmatter、导航）

---

## 任务详细分解

### Task 1: 创建 `00-overview.md` 教程总览与导航索引
- [x] Step 1.1: 在 `docs/knowledge/learning/idl-wiki/` 目录下创建 `00-overview.md`
- [x] Step 1.2: 编写 YAML frontmatter（`id: idl-wiki-overview`、`title`、`x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/idl-wiki/00-overview.toml"`、`source: "spec:create-idl-wiki-tutorial"`、`category: "learning"`、`tags: ["idl", "interface-definition-language", "overview", "tutorial"]`、`date: "2026-07-04"`、`status: "stable"`、`author: "SpecWeave"`、`summary`）
- [x] Step 1.3: 编写教程引言，简述 IDL 在接口技术栈中的定位与学习价值
- [x] Step 1.4: 绘制 Mermaid 概念层次图，展示 IDL 与 Interface/API/ABI/Protocol/OpenAPI/GraphQL 的关系
- [x] Step 1.5: 编写 9 章导航表（章节号 + 标题 + 简要内容描述 + 文件链接）
- [x] Step 1.6: 编写目标读者说明（初中级开发人员、架构师、分布式系统开发者、跨语言调用场景工程师）
- [x] Step 1.7: 编写阅读路径建议（线性阅读 vs 按需查阅），并链接 `interface-api-abi-protocol-wiki/00-overview.md` 作为延伸阅读
- **验证**: 文件 < 300 行；frontmatter 字段完整；导航链接全部使用相对路径

### Task 2: 创建 `01-what-is-idl.md` IDL 定义与作用
- [x] Step 2.1: 创建文件并编写 frontmatter（`id: idl-wiki-what-is-idl`，其余字段按 Task 1 模板）
- [x] Step 2.2: 编写 IDL 标准定义段落（OMG 定义 + 通用工程定义）
- [x] Step 2.3: 编写 ≥5 个核心特征：语言中立、平台中立、可编译生成多语言桩代码、支持类型系统、契约式设计/单一事实源（Single Source of Truth）
- [x] Step 2.4: 绘制 Mermaid 时间线图，展示 IDL 发展三阶段：RPC 时代（CORBA/COM/ONC RPC）→ 序列化框架时代（Protobuf/Thrift/Avro）→ 现代接口描述时代（OpenAPI/GraphQL/gRPC）
- [x] Step 2.5: 编写 "IDL 解决的核心问题" 段落，对比"人工维护多语言接口定义"vs"IDL 单源生成"的痛点
- [x] Step 2.6: 编写 "IDL vs 编程语言原生 interface" 对比表格（如 Go interface / Java interface / TypeScript interface 与 IDL 的本质差异）
- [x] Step 2.7: 添加底部双向导航（无上一章 / 返回目录 `00-overview.md` / 下一章 `02-syntax-basics.md`）
- **验证**: 文件 < 300 行；含 Mermaid 时间线图；含对比表格

### Task 3: 创建 `02-syntax-basics.md` IDL 基本语法结构
- [x] Step 3.1: 创建文件并编写 frontmatter（`id: idl-wiki-syntax-basics`）
- [x] Step 3.2: 编写 "基本数据类型" 段落，覆盖标量类型（int/float/bool/string/bytes）、复合类型（struct/message/record）、枚举、容器类型（list/map/set），每种类型配 Protobuf 与 CORBA IDL 双语法示例
- [x] Step 3.3: 编写 "接口声明语法" 段落，对比 Protobuf `service`、CORBA `interface`、Thrift `service` 的声明方式
- [x] Step 3.4: 编写 "方法描述" 段落，覆盖参数声明（含方向 in/out/inout）、返回值、异常声明（CORBA `raises`、Thrift `throws`）
- [x] Step 3.5: 编写 "注解与注释机制" 段落，覆盖 Protobuf `options`、Thrift 注解、CORBA pragma、各 IDL 的注释语法（`//`、`/* */`、`#`）
- [x] Step 3.6: 添加底部双向导航（上一章 `01-what-is-idl.md` / 返回目录 / 下一章 `03-major-idl-specs.md`）
- **验证**: 文件 < 300 行；每项语法要素配 ≥1 个代码示例；至少包含 Protobuf 与 CORBA IDL 两种对照

### Task 4: 创建 `03-major-idl-specs.md` 主要 IDL 规范介绍
- [x] Step 4.1: 创建文件并编写 frontmatter（`id: idl-wiki-major-idl-specs`）
- [x] Step 4.2: 编写 Protocol Buffers（Google，2001）小节：起源背景、语法示例（含 message/service/enum）、典型应用场景（gRPC、数据存储、配置文件）、生态工具（protoc/buf/protoc-gen-go 等）
- [x] Step 4.3: 编写 Apache Thrift（Facebook，2007）小节：起源背景、语法示例、应用场景（Facebook 内部服务、Cassandra 通信）、生态工具（thrift 编译器、多语言运行时库）
- [x] Step 4.4: 编写 CORBA IDL（OMG，1991）小节：起源背景、语法示例、应用场景（企业级分布式系统、金融/电信遗留系统）、生态工具（ORB 产品如 JacORB/omniORB/TAO）
- [x] Step 4.5: 编写 COM/DCOM IDL（Microsoft，1993）小节：起源背景、MIDL 语法示例、应用场景（Windows COM 组件、Office 自动化、ActiveX）、生态工具（MIDL 编译器、tlbimp）
- [x] Step 4.6: 编写 Apache Avro IDL（Hadoop，2009）小节：起源背景、语法示例（含 protocol/record）、应用场景（Hadoop RPC、Kafka Schema Registry）、生态工具（avro-tools、Confluent Schema Registry）
- [x] Step 4.7: 添加底部双向导航（上一章 `02-syntax-basics.md` / 返回目录 / 下一章 `04-comparison.md`）
- **验证**: 文件 < 300 行；覆盖 5 种 IDL；每种含起源、语法、场景、工具四要素

### Task 5: 创建 `04-comparison.md` IDL 规范对比
- [x] Step 5.1: 创建文件并编写 frontmatter（`id: idl-wiki-comparison`）
- [x] Step 5.2: 编写多维度对比表格，覆盖维度：语法风格、类型系统、二进制格式、Schema 演进策略、工具链生态、学习曲线、性能（序列化速度/体积）、传输协议绑定、社区活跃度
- [x] Step 5.3: 绘制 Mermaid 决策树或流程图，按使用场景（高性能 RPC / Web API / 遗留系统集成 / 大数据序列化 / 跨语言通信）推荐 IDL 方案
- [x] Step 5.4: 编写选型决策指南段落，按场景给出推荐：gRPC 微服务→Protobuf、Facebook 生态/兼容遗留→Thrift、企业遗留系统→CORBA IDL、Windows 生态→COM IDL、大数据/Kafka→Avro
- [x] Step 5.5: 简要提及 FlatBuffers/Cap'n Proto 等零拷贝序列化方案作为补充参考
- [x] Step 5.6: 添加底部双向导航（上一章 `03-major-idl-specs.md` / 返回目录 / 下一章 `05-toolchain.md`）
- **验证**: 文件 < 300 行；含多维度对比表格；含 Mermaid 决策图

### Task 6: 创建 `05-toolchain.md` IDL 编译流程与工具链
- [x] Step 6.1: 创建文件并编写 frontmatter（`id: idl-wiki-toolchain`）
- [x] Step 6.2: 绘制 Mermaid 编译流程图：`source.idl → [IDL Compiler] → codegen plugins → target language stubs (Java/Python/Go/...) + descriptor file`
- [x] Step 6.3: 编写主流编译器介绍段落：protoc（含插件机制）、thrift compiler、avro-tools、MIDL、idlj（CORBA IDL→Java），每个编译器说明输入输出与典型命令
- [x] Step 6.4: 编写构建系统集成示例：Maven（protobuf-maven-plugin）、Gradle（protobuf-gradle-plugin）、Bazel（proto_library 规则），各配 1 个最小配置示例
- [x] Step 6.5: 编写 Schema 演进与兼容性管理段落：向前兼容/向后兼容规则、字段编号不可复用、Protobuf `reserved` 关键字、Buf 工具的 breaking change 检测
- [x] Step 6.6: 编写代码生成配置示例，展示如何自定义生成输出（如 Protobuf 的 `--go_out`、`--java_out`、`option java_package`）
- [x] Step 6.7: 添加底部双向导航（上一章 `04-comparison.md` / 返回目录 / 下一章 `06-use-cases.md`）
- **验证**: 文件 < 300 行；含编译流程 Mermaid 图；含 ≥3 个主流编译器介绍；含构建系统集成示例

### Task 7: 创建 `06-use-cases.md` 实际应用案例与最佳实践
- [x] Step 7.1: 创建文件并编写 frontmatter（`id: idl-wiki-use-cases`）
- [x] Step 7.2: 编写应用案例 1：gRPC 服务定义——含 `.proto` 源码（service + message）、生成 Go 代码片段、客户端/服务端调用示例
- [x] Step 7.3: 编写应用案例 2：Thrift 微服务接口——含 `.thrift` 源码、生成 Python 代码片段、客户端调用示例
- [x] Step 7.4: 编写应用案例 3：CORBA 遗留系统集成——含 `.idl` 源码、生成 Java 桩代码片段、简述 ORB 调用流程
- [x] Step 7.5: 编写最佳实践清单（≥5 条）：命名规范（snake_case vs camelCase 按语言约定）、版本管理（package/namespace 版本号）、向后兼容（新增字段用 optional/默认值）、字段编号规则（保留 1-15 给常用字段、留出跳号空间）、错误处理（错误码枚举 + status 字段）
- [x] Step 7.6: 简要交叉引用项目内 `agent-interface-deep-dive` wiki，说明 IDL 在 AI Agent 工具定义场景下的延伸应用
- [x] Step 7.7: 添加底部双向导航（上一章 `05-toolchain.md` / 返回目录 / 下一章 `07-vs-modern-formats.md`）
- **验证**: 文件 < 300 行；含 3 个完整案例（IDL 源码 + 生成代码 + 调用示例）；含 ≥5 条最佳实践

### Task 8: 创建 `07-vs-modern-formats.md` 与现代接口描述方式对比
- [x] Step 8.1: 创建文件并编写 frontmatter（`id: idl-wiki-vs-modern-formats`）
- [x] Step 8.2: 编写 "传统 IDL vs 现代 IDL" 边界划分段落：传统 IDL 关注跨语言 RPC 与二进制序列化，现代 IDL 关注 Web API 文档化、人机可读、生态集成
- [x] Step 8.3: 编写对比表格，覆盖 OpenAPI、GraphQL Schema、JSON Schema、AsyncAPI，对比维度：关注点、序列化格式、传输协议、工具链生态、AI 友好度、Schema 演进
- [x] Step 8.4: 绘制 Mermaid 演进关系图：`RPC IDL（CORBA/COM）→ 序列化 IDL（Protobuf/Thrift）→ Web IDL（OpenAPI/GraphQL）→ AI-friendly IDL（MDI）`
- [x] Step 8.5: 编写各格式适用场景说明：OpenAPI→REST API 文档与 SDK 生成、GraphQL Schema→客户端驱动查询、JSON Schema→数据校验、AsyncAPI→事件驱动架构
- [x] Step 8.6: 编写 "与 MDI（Markdown Interface）的关联" 段落，引用项目内 MDI 复盘洞察（[insight-extraction.md#L43-L47](../../../../.agents/docs/retrospective/reports/project-reports/retrospective-mdi-project-completion-20260702/insight-extraction.md#L43-L47)），简述 Markdown 作为 AI 友好 IDL 的价值
- [x] Step 8.7: 添加底部双向导航（上一章 `06-use-cases.md` / 返回目录 / 下一章 `08-resources.md`）
- **验证**: 文件 < 300 行；含对比表格覆盖 4 种现代格式；含 Mermaid 演进图；含 MDI 洞察引用

### Task 9: 创建 `08-resources.md` 学习资源与参考资料
- [x] Step 9.1: 创建文件并编写 frontmatter（`id: idl-wiki-resources`）
- [x] Step 9.2: 编写术语表（Glossary），覆盖 ≥15 个 IDL 相关术语：IDL、Stub、Skeleton、ORB、POA、IIOP、Codec、Schema、Protobuf、Thrift、CORBA、COM、MIDL、Avro、Schema Evolution、Backward Compatibility、Code Generation 等
- [x] Step 9.3: 编写权威参考资料链接清单：OMG CORBA 规范、Google Protocol Buffers 官方文档、Apache Thrift 文档、Apache Avro 规范、Microsoft MIDL 文档、OpenAPI 规范、GraphQL 规范
- [x] Step 9.4: 编写按难度分级的扩展阅读建议：入门（Protobuf 教程、gRPC 快速开始）、进阶（Schema 演进策略、Buf 工具链）、高级（CORBA 规范精读、零拷贝序列化原理）
- [x] Step 9.5: 编写 "项目内相关 wiki 交叉引用" 段落，链接到 `interface-api-abi-protocol-wiki/00-overview.md`、`agent-interface-deep-dive`、MDI 复盘报告
- [x] Step 9.6: 添加底部双向导航（上一章 `07-vs-modern-formats.md` / 返回目录 / 无下一章，提示"教程已完成"）
- **验证**: 文件 < 300 行；术语表 ≥15 条；含权威资料链接；含项目内交叉引用

### Task 10: 统一质量验证
- [x] Step 10.1: 运行 `python .agents/scripts/check-file-size.py --path docs/knowledge/learning/idl-wiki/` 验证所有文件 < 300 行
- [x] Step 10.2: 运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning/idl-wiki/` 验证所有相对路径链接有效，无 `file:///` 绝对路径断链
- [x] Step 10.3: 抽查每个文件 frontmatter，确认 `source: "spec:create-idl-wiki-tutorial"` 与 `category: "learning"` 字段正确
- [x] Step 10.4: 抽查 01-07 文件底部导航链接，确认上一章/返回目录/下一章三向链接完整且指向正确文件
- [x] Step 10.5: 抽查关键章节内容覆盖度：`03-major-idl-specs.md` 覆盖 5 种 IDL、`06-use-cases.md` 含 3 个案例 + 5 条最佳实践、`08-resources.md` 术语表 ≥15 条
- [x] Step 10.6: 修复任何验证失败项（文件超长需拆分内容、断链需修正路径、frontmatter 缺失需补全）
- **验证**: 所有验证脚本通过；人工抽查内容覆盖度达标

---

# Task Dependencies

- **Task 1（00-overview.md）** 是其他所有章节的导航枢纽，建议优先完成，但内容上不阻塞后续任务
- **Task 2-9** 相互独立，可并行执行（导航链接使用约定的文件名，无需等待其他章节实际完成）
- **Task 10（质量验证）** 严格依赖 Task 1-9 全部完成，必须最后执行
- **建议执行顺序**：
  - 阶段一：Task 1（建立导航框架）
  - 阶段二：Task 2-9 并行（8 个章节可分派给不同 sub-agent）
  - 阶段三：Task 10（统一质量验证与修复）
