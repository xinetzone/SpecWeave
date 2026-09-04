# Checklist

本 checklist 对应 spec.md 中的 12 条验收标准（AC-1 ~ AC-12），用于在实现完成后逐项验证。每条 checkpoint 通过后请打勾。

## AC-1: 目录结构完整
- [x] `docs/knowledge/learning/idl-wiki/` 目录存在
- [x] 包含 `00-overview.md` 到 `08-resources.md` 共 9 个文件
- [x] 运行 `python .agents/scripts/check-file-size.py --path docs/knowledge/learning/idl-wiki/` 无超长文件（每个 < 300 行）

## AC-2: IDL 定义与作用完整（`01-what-is-idl.md`）
- [x] 包含 IDL 标准定义（OMG 定义 + 通用工程定义）
- [x] 包含 ≥5 个核心特征说明（语言中立/平台中立/可编译生成/类型系统/契约式设计）
- [x] 包含 IDL 发展三阶段时间线（Mermaid 图）
- [x] 包含 IDL 解决的核心问题段落（多语言重复定义痛点）
- [x] 包含 IDL 与编程语言原生 interface 的对比表格

## AC-3: 基本语法结构完整（`02-syntax-basics.md`）
- [x] 包含基本数据类型段落（标量/复合类型/枚举/容器）
- [x] 包含接口声明语法段落（对比 Protobuf `service` / CORBA `interface` / Thrift `service`）
- [x] 包含方法描述段落（参数方向 in/out/inout、返回值、异常声明）
- [x] 包含注解与注释机制段落（Protobuf options / Thrift 注解 / CORBA pragma）
- [x] 每项语法要素配 ≥1 个代码示例，至少包含 Protobuf 与 CORBA IDL 两种语法对照

## AC-4: 主要 IDL 规范覆盖完整（`03-major-idl-specs.md`）
- [x] 覆盖 Protocol Buffers（含起源/语法示例/场景/工具）
- [x] 覆盖 Apache Thrift（含起源/语法示例/场景/工具）
- [x] 覆盖 CORBA IDL（含起源/语法示例/场景/工具）
- [x] 覆盖 COM/DCOM IDL（含起源/语法示例/场景/工具）
- [x] 覆盖 Apache Avro IDL（含起源/语法示例/场景/工具）

## AC-5: 规范对比系统（`04-comparison.md`）
- [x] 包含多维度对比表格（语法风格/类型系统/二进制格式/Schema 演进/工具链/学习曲线/性能/传输协议/社区活跃度）
- [x] 包含 Mermaid 决策树或流程图（按场景推荐 IDL 方案）
- [x] 包含选型决策指南段落（按场景给出推荐）
- [x] 简要提及 FlatBuffers/Cap'n Proto 作为补充参考

## AC-6: 工具链章节完整（`05-toolchain.md`）
- [x] 包含 IDL 编译流程 Mermaid 图（source → IDL → compiler → codegen → target language stubs）
- [x] 介绍 ≥3 个主流编译器（protoc/thrift compiler/avro-tools/MIDL/idlj 等）
- [x] 包含构建系统集成示例（Maven/Gradle/Bazel 至少 1 个最小配置）
- [x] 包含 Schema 演进与兼容性管理说明（向前/向后兼容、字段编号规则、reserved 关键字、Buf 检测）
- [x] 包含代码生成配置示例（自定义输出语言与包路径）

## AC-7: 应用案例充分（`06-use-cases.md`）
- [x] 包含 ≥3 个完整应用案例
- [x] 案例 1（gRPC 服务定义）含 `.proto` 源码 + 生成代码片段 + 调用示例
- [x] 案例 2（Thrift 微服务）含 `.thrift` 源码 + 生成代码片段 + 调用示例
- [x] 案例 3（CORBA 遗留系统）含 `.idl` 源码 + 生成桩代码片段 + ORB 调用流程说明
- [x] 包含 ≥5 条最佳实践（命名规范/版本管理/向后兼容/字段编号/错误处理）

## AC-8: 与现代格式对比完整（`07-vs-modern-formats.md`）
- [x] 包含传统 IDL vs 现代 IDL 边界划分段落
- [x] 包含对比表格覆盖 OpenAPI / GraphQL Schema / JSON Schema / AsyncAPI
- [x] 包含 Mermaid 演进关系图（RPC IDL → 序列化 IDL → Web IDL → AI-friendly IDL）
- [x] 包含各格式适用场景说明
- [x] 包含与 MDI（Markdown Interface）的关联段落，引用项目内 MDI 复盘洞察

## AC-9: 元数据规范
- [x] 所有 9 个文档包含完整 YAML frontmatter
- [x] `id` 字段值符合 `idl-wiki-*` 命名约定
- [x] `source` 字段值统一为 `spec:create-idl-wiki-tutorial`
- [x] `category` 字段值为 `learning`
- [x] `x-toml-ref` 字段指向 `.meta/toml/docs/knowledge/learning/idl-wiki/` 下对应 TOML 路径
- [x] `tags`、`date`、`status`、`author`、`summary` 字段完整

## AC-10: 链接有效
- [x] 运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning/idl-wiki/` 通过
- [x] 无 `file:///` 绝对路径断链
- [x] 所有内部链接使用相对路径
- [x] 项目内交叉引用（如 MDI 复盘报告、`interface-api-abi-protocol-wiki`、`agent-interface-deep-dive`）链接可达

## AC-11: 双向导航
- [x] `01-what-is-idl.md` 到 `07-vs-modern-formats.md` 每个文件底部包含三向导航
- [x] 导航包含：上一章链接、返回目录（`00-overview.md`）链接、下一章链接
- [x] `01-what-is-idl.md` 的"上一章"为 `00-overview.md` 或标注"无"
- [x] `08-resources.md` 的"下一章"标注"教程已完成"或类似提示

## AC-12: 参考资料完整（`08-resources.md`）
- [x] 术语表包含 ≥15 个 IDL 相关术语（IDL/Stub/Skeleton/ORB/POA/IIOP/Codec/Schema/Protobuf/Thrift/CORBA/COM/MIDL/Avro/Schema Evolution/Backward Compatibility/Code Generation 等）
- [x] 包含权威参考资料链接（OMG CORBA 规范、Google Protobuf 官方文档、Apache Thrift 文档、Apache Avro 规范、Microsoft MIDL 文档、OpenAPI 规范、GraphQL 规范）
- [x] 包含按难度分级的扩展阅读建议（入门/进阶/高级）
- [x] 包含项目内相关 wiki 交叉引用（`interface-api-abi-protocol-wiki`、`agent-interface-deep-dive`、MDI 复盘报告）

---

## 附加质量检查

- [x] 所有代码示例标注语言类型（如 `protobuf`、`thrift`、`idl`、`java`、`go`、`python` 等）
- [x] 所有 Mermaid 图表语法正确，可在 Markdown 渲染器中正常显示
- [x] 文档语言为中文，技术术语准确（参考权威来源如 OMG 规范、Google Protobuf 官方文档）
- [x] 命名遵循项目 kebab-case + 数字前缀排序规范
- [x] 无重复内容（每个文件聚焦单一职责，跨文件引用使用链接而非复制）
