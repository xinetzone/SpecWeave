+++
id = "mermaid-insight-renderer-tolerance"
date = "2026-06-26"
type = "insight"
scope = "mermaid,compatibility"
source = "../insight-extraction.md#一、发现4"
+++

# 洞察07：渲染器容错度差异导致"本地正常、线上失败"

## 核心命题

不同 Markdown 渲染器对 Mermaid 的容错度不同。本地预览正常不能保证在所有渲染环境中正常。最安全的做法是遵循最严格的语法规范，而非依赖渲染器的容错能力。

## 事实支撑

- GitHub 的 Mermaid 渲染器相对宽容，某些不严格的语法仍能正常渲染
- 飞书等部分渲染器更严格，对空行、未引号文本、列表触发模式等零容忍
- 本次故障中，本地 VS Code 预览看似正常，但飞书文档中渲染失败

## 深层含义

"在我机器上能跑"（Works on my machine）问题同样存在于文档渲染领域。Mermaid 语法标准虽然统一，但各平台实现的版本、解析策略、Markdown 预处理逻辑存在差异：

| 平台 | Mermaid 版本 | 容错度 | 已知严格点 |
|------|-------------|--------|-----------|
| GitHub | 较新 | 宽松 | 一般问题都能渲染 |
| VS Code 预览 | 取决于插件 | 中等 | 空行可能不报错 |
| 飞书文档 | 定制版 | 严格 | 列表触发、空行零容忍 |
| GitLab | 较新 | 中等 | 部分语法有差异 |

## 实践原则

1. **遵循最严规范**：编写时就按照最严格渲染器的要求来，不要依赖容错
2. **自动化验证**：使用 `check-mermaid.py` 脚本系统性扫描，而非人工预览
3. **目标平台测试**：重要文档在最终部署平台验证一次
4. **使用安全模板**：从 [mermaid-templates/](../../../../../../.agents/templates/mermaid-templates/README.md) 开始编写，内置安全格式

## 关联洞察

- [insight-01-no-blank-lines.md](insight-01-no-blank-lines.md) — 空行规则是最严格渲染器的共同要求
- [insight-03-markdown-list-avoidance.md](insight-03-markdown-list-avoidance.md) — 列表触发是飞书等严格渲染器的常见报错点
- [insight-06-layered-verification.md](insight-06-layered-verification.md) — 分层验证法包含目标平台验证步骤

---
*来源：[Mermaid 渲染问题修复复盘](../README.md)*
