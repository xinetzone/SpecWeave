# Tasks

## 阶段 1：概念规范定义（当前阶段）

- [x] Task 1: 创建统一化生态体系知识库目录结构
  - [x] 创建 `docs/knowledge/myst-unified-ecosystem/` 目录
  - [x] 创建 README.md 入口索引（含四层分类架构图、概念速查表、阅读路径）
  - [x] 创建 `00-overview.md` 总览文档（可行性分析、架构图、关系全景）

- [x] Task 2: 撰写元概念层文档（IDL）
  - [x] 创建 `01-idl.md`：IDL 概念定义、IDL 与其他概念的 describes 关系、主流 IDL 对比（OpenAPI/Protobuf/MDI）、IDL 选型决策树

- [x] Task 3: 撰写设计抽象层文档（Interface、API、ABI、Protocol、Implementation）
  - [x] 创建 `02-interface.md`：Interface 概念定义、与 API/ABI 的区别、MyST Directive 声明方式
  - [x] 创建 `03-api.md`：API 概念定义、与 Interface 的 depends-on 关系、MCP/A2A/ACP 中的 API 体现
  - [x] 创建 `04-abi.md`：ABI 概念定义、与 Implementation 的 constrains 关系、JSON/STDIO/HTTP 作为 Agent ABI
  - [x] 创建 `05-protocol.md`：Protocol 概念定义、composes API+ABI、与 MCP/ACP/A2A/ANP 的 instantiates 关系
  - [x] 创建 `06-implementation.md`：Implementation 概念定义、implements 关系、受 ABI constrains

- [x] Task 4: 撰写协议实例层文档（MCP、ACP、A2A、ANP）
  - [x] 创建 `07-mcp.md`：MCP 作为 Protocol 实例，Interface/API/ABI 在 MCP 中的具体体现
  - [x] 创建 `08-acp.md`：ACP 作为 Protocol 实例，与 MCP/A2A 的差异与互补
  - [x] 创建 `09-a2a.md`：A2A 作为 Protocol 实例，企业级特性与跨域协作
  - [x] 创建 `10-anp.md`：ANP 作为 Protocol 实例，去中心化愿景与当前成熟度

- [x] Task 5: 撰写载体层文档（MDI）
  - [x] 创建 `11-mdi.md`：MDI 作为 IDL 的 MyST Markdown 承载，carries 所有概念，MyST Directive 完整清单

- [x] Task 6: 撰写概念关系与交互全景文档
  - [x] 创建 `12-relationships.md`：7 类关系形式化定义、关系矩阵（11×11）、概念交互场景示例（Mermaid 序列图）、统一化体系的价值总结
  - [x] 更新 README.md 导航表，确保所有文档链接正确

# Task Dependencies

- Task 2、3、4、5 依赖 Task 1（目录结构创建后并行开展）
- Task 6 依赖 Task 2、3、4、5（所有概念文档完成后汇总关系）
- 阶段 2-5 的详细任务在阶段 1 完成后根据实际产出制定