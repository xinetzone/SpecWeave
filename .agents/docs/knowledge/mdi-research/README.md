---
id: "mdi-research-index"
title: "MDI/MyST 文档工具研究"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/mdi-research/README.toml"
category: "mdi-research"
date: "2026-07-09"
---
# MDI/MyST 文档工具研究

## 🎯 研究背景

> **MDI（Markdown Interface Specification）** 是一种以 Markdown 文件作为接口定义载体的规范体系，核心设计理念是 **"一份文档，两种读者"**——人类可自然阅读，机器可自动解析。
>
> 本研究系列通过原型验证和三个端到端案例测试，系统评估 MDI 在 AI Agent Skill 文档、轻量级 RESTful API、CLI 工具定义等场景的可行性、技术架构、工具链完整性，并对比主流 IDL 生态给出落地建议。

### 核心发现（执行摘要）

| 指标 | 结果 | 说明 |
|------|------|------|
| ⚡ 解析性能 | 平均 3.6ms/文件 | 远优于 50ms 设计目标 |
| 🔧 工具链完整度 | Parser→Validator→Generator 三层 | 支持 9 种输出格式 |
| ✅ 测试覆盖 | 221 个单元测试 + 3 个 E2E 案例 | 全部通过 |
| 🎯 适用场景 | AI Skill 文档、内部 API、快速原型 | 人类可读优先场景 |

---

## 📚 报告章节导航

本研究系列共 8 篇报告，按逻辑顺序组织：

| 编号 | 标题 | 核心内容 |
|------|------|---------|
| [00](00-executive-summary.md) | **执行摘要** | 研究结论概览、核心发现数据、下一步阅读指引 |
| [01](01-feasibility-analysis.md) | **可行性分析** | 7 项核心优势矩阵、5 项局限性分析及缓解措施、适用场景决策树 |
| [02](02-ecosystem-comparison.md) | **生态对比分析** | 与 OpenAPI/AsyncAPI/Protobuf/GraphQL 等 6 种主流 IDL 的 13 维特性对比、互补关系定位 |
| [03](03-technical-architecture.md) | **技术架构深度解析** | Parser/Validator/Generator 三层架构、核心数据模型、扩展机制设计 |
| [04](04-toolchain-guide.md) | **工具链使用指南** | 环境要求、安装方法、CLI 命令参考、9 种输出格式使用示例 |
| [05](05-versioning-best-practices.md) | **版本控制最佳实践** | SemVer 语义化版本规范、变更严重性判定、diff 工具使用、兼容性检测 |
| [06](06-future-evolution.md) | **未来演进方向** | v1.1/v1.2-v2.0 规划路线图、插件系统、生态扩展方向 |
| [07](07-conclusion.md) | **结论** | 最终采用建议、4 级场景分级、生产可用性评估 |

---

## 🔑 关键结论

### 场景采用建议

| 采用级别 | 场景 | 建议 |
|---------|------|------|
| ✅ **立即采用** | AI Agent Skill 文档 | MDI 是最佳选择，AI 天然理解 Markdown，文档即代码 |
| ✅ **推荐使用** | 小团队内部 API、快速原型、教学文档 | 零学习成本、开发效率高 |
| ⚠️ **谨慎评估** | 对外公开 API、企业级 API 治理 | MDI 作为编辑格式，导出 OpenAPI 复用现有生态 |
| ❌ **不适用** | gRPC/二进制协议、已有成熟 OpenAPI 体系的大规模项目 | 使用 Protobuf/OpenAPI 更合适 |

### MDI vs OpenAPI 定位

> MDI 并非要取代 OpenAPI，而是填补 **"人类可读优先"** 的生态位：
> - **MDI**：编辑/阅读/AI Agent 消费优先
> - **OpenAPI**：网关/CodeGen/Mock Server/企业治理优先
> - 两者可双向转换，互补共存

---

## 🧭 阅读路径

### 快速了解（15分钟）
1. [00-executive-summary.md](00-executive-summary.md) → 看核心发现和结论
2. [07-conclusion.md](07-conclusion.md) → 看最终采用建议

### 评估决策（1小时）
1. [00-executive-summary.md](00-executive-summary.md)
2. [01-feasibility-analysis.md](01-feasibility-analysis.md) → 判断优势/局限是否匹配你的场景
3. [02-ecosystem-comparison.md](02-ecosystem-comparison.md) → 对比现有技术栈
4. [07-conclusion.md](07-conclusion.md) → 最终决策

### 技术落地（完整阅读）
1. 按编号顺序 00→07 完整阅读
2. 重点关注 [03-technical-architecture.md](03-technical-architecture.md) 和 [04-toolchain-guide.md](04-toolchain-guide.md)
3. 结合 [05-versioning-best-practices.md](05-versioning-best-practices.md) 制定团队规范

---

## 🔗 相关资源

- [🏠 知识库首页](../README.md) - 返回知识库总入口
- [📁 MyST 规范学习](../learning/04-docs-markup-tooling/executablebooks-myst-guide/README.md) - ExecutableBooks MyST 指南
- [📁 MyST 教程](../learning/04-docs-markup-tooling/myst-markdown-tutorial/README.md) - MyST Markdown 系统教程
- [📁 团队最佳实践库](../best-practices/README.md) - 文档规范最佳实践
