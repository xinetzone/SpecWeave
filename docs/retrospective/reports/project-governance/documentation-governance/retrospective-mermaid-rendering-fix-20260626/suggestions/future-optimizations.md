+++
id = "mermaid-retro-future-optimizations"
date = "2026-06-26"
type = "future-optimization"
priority = "low"
scope = "mermaid-tooling"
source = "../export-suggestions.md#四"
+++

# 后续优化方向

> 本次复盘已建立"规范+脚本+CI+模板"基础防护体系。以下为尚未执行的长期优化方向。
> 执行结果见 [export-suggestions.md](../export-suggestions.md)，渲染器差异分析见 [insight-07](../insights/insight-07-renderer-tolerance.md)。

## 待执行项

| 方向 | 具体措施 | 价值 |
|------|---------|------|
| 工具链增强 | 引入 Mermaid 官方解析器（mermaid-parser）做 AST 级别校验，替代正则检测；支持 classDiagram/stateDiagram/erDiagram 等更多图表类型；添加自动修复预览 | 减少正则误报/漏报，覆盖更多图表类型 |
| 模板化预防 | 在智能体生成 Mermaid 的系统提示词中强制注入五规则；为各类工作流生成的 Mermaid 图表提供专用模板；开发 Mermaid 代码片段生成器 | 从生产端杜绝问题，而非仅在检测端拦截 |
| 跨渲染器测试 | 建立多平台（GitHub/GitLab/飞书/Notion/VS Code）渲染验证流程；记录各平台 Mermaid 版本差异和已知问题；CI 中增加渲染截图对比 | 解决"本地正常、线上失败"问题 |

## 核心思路

防护体系采用**双防线策略**：
- **预防端**：模板内置安全格式 + 智能体提示词注入规范，减少错误 Mermaid 的产生
- **检测端**：check-mermaid.py + CI 集成，在提交前拦截遗漏问题

当前双防线均为基础版（正则检测+5种静态模板），未来优化方向围绕提升两端的覆盖度和精确度展开。

---
*来源：[Mermaid 渲染问题修复复盘](../README.md)*
