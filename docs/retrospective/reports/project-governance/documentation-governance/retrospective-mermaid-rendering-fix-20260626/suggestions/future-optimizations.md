+++
id = "mermaid-retro-future-optimizations"
date = "2026-06-26"
type = "future-optimization"
priority = "low"
scope = "mermaid-tooling"
source = "../export-suggestions.md#四"
+++

# 后续优化方向

本次复盘建立了 Mermaid 渲染防护的基础体系（规范 + 脚本 + CI + 模板），以下为长期优化方向，供后续迭代参考。

## 优化方向清单

### 1. 工具链增强

**方向**：将 Mermaid 语法检测从人工经验升级为自动化工具

**现状**：已在零依赖原则下实现了 Python 正则检测脚本 `check-mermaid.py`，覆盖 5 类常见问题。

**可探索方向**：
- 引入 Mermaid 官方解析器（mermaid-parser）做 AST 级别校验，减少正则误报/漏报
- 支持更多图表类型（classDiagram、stateDiagram、erDiagram 等）的专用规则
- 添加自动修复预览（diff 展示）功能

### 2. 模板化预防

**方向**：在生成 Mermaid 代码的模板/脚本中内置安全格式，从生产端杜绝问题

**现状**：已在 [.agents/templates/mermaid-templates/](../../../../../../../.agents/templates/mermaid-templates/) 提供 5 种常用图表的安全格式模板。

**可探索方向**：
- 在智能体生成 Mermaid 的系统提示词中强制注入五规则
- 为各类工作流生成的 Mermaid 图表提供专用模板
- 考虑开发 Mermaid 代码片段生成器（脚手架）

### 3. 跨渲染器测试

**方向**：引入多渲染器兼容性测试，确保在主流环境中均正常渲染

**背景**：不同平台（GitHub/GitLab/飞书/Notion/VS Code）使用的 Mermaid 版本和解析器存在差异，本地通过的语法可能在其他平台失败。

**可探索方向**：
- 建立多平台渲染验证流程
- 记录各平台 Mermaid 版本差异和已知问题
- 在 CI 中增加渲染截图对比

### 4. 知识传播

**方向**：将 Mermaid 安全编码规则纳入智能体系统提示词，使 AI 生成 Mermaid 时自动遵循

**现状**：规则已写入项目记忆（`project_memory.md`）和[开发规范](../../../../../../development-standards.md)。

**可探索方向**：
- 在智能体系统提示词中嵌入 Mermaid 安全编码规则
- 在开发者角色提示词中增加 Mermaid 规范校验职责
- 建立规则更新机制，确保新发现的陷阱及时传播

## 当前状态

- [x] 工具链增强（基础版）：check-mermaid.py 已完成
- [x] 模板化预防（基础版）：5 种安全模板已创建
- [ ] 跨渲染器测试：待规划
- [x] 知识传播：项目记忆、开发规范已更新

---
*来源：[Mermaid 渲染问题修复复盘](../README.md)*
