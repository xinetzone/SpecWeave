# AgentForge 复用案例

`vendor/flexloop/` 目录下的 AgentForge 项目是本规范体系在实际项目中的**落地案例**，证明了角色体系、协作协议、自我演进模块等核心机制的可迁移性。

## 复用对照

| 复用要素 | 原项目（本体系） | 落地项目（AgentForge） |
|---------|----------------|---------------------|
| 入口机制 | AGENTS.md 全局契约 | AGENTS.md 全局契约 |
| 角色体系 | 5 个核心角色 + 扩展角色 | engineering + governance 双角色体系 |
| 规范容器 | .agents/ 目录结构 | .agents/ 目录结构（13 个子目录） |
| 验证脚本 | 7 个验证脚本 | 25+ 验证与检查脚本 |
| 模板系统 | 任务/交接模板 | 多类模板 + 启动脚手架 |
| Spec 驱动 | .trae/specs/ 规格文档 | .trae/specs/ 规格文档（12 个 spec） |

## 特色模式观察

| 模式 | 位置 | 性质 | SpecWeave 处置 |
|------|------|------|----------------|
| 知识/哲学角色 | `vendor/flexloop/.agents/roles/boshu-laozi.md`（帛书版道德经导师） | flexloop "哲学驱动"原则的具象化，属"知识角色"非工程角色 | 待观察模式：暂不引用、暂不萃取。触发萃取条件见 [VENDOR-INTEGRATION.md 第11.3节](../../docs/knowledge/VENDOR-INTEGRATION.md) |
