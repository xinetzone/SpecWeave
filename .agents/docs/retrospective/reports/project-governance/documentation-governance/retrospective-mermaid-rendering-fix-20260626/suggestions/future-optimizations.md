---
id: "mermaid-retro-future-optimizations"
title: "后续优化方向"
source: "../export-suggestions.md#四"
x-toml-ref: "../../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/documentation-governance/retrospective-mermaid-rendering-fix-20260626/suggestions/future-optimizations.toml"
---
# 后续优化方向

> 本次复盘已建立"规范+脚本+CI+模板"基础防护体系。以下为尚未执行的长期优化方向。
> 执行结果见 [export-suggestions.md](../export-suggestions.md)，渲染器差异分析见 [insight-07](../insights/insight-07-renderer-tolerance.md)。

## 待执行项

| 方向 | 具体措施 | 价值 | 状态 |
|------|---------|------|------|
| 工具链增强 | 引入 Mermaid 官方解析器（mermaid-parser）做 AST 级别校验，替代正则检测；支持 classDiagram/erDiagram 等更多图表类型 | 减少正则误报/漏报，覆盖更多图表类型 | 🟡 大部分完成：检测器已重构为按图表类型分发架构，支持 10 种图表（flowchart/graph/stateDiagram-v2/sequenceDiagram/pie/gantt/timeline/mindmap/xychart-beta/quadrantChart），覆盖 7 种节点形状（圆形/体育场/子程序/标签/矩形/菱形/圆角）、14 种箭头类型，添加 --dry-run 修复预览 diff 功能，检测含空格英文文本、style语句中文警告；剩余 AST 校验需引入 Node.js 依赖，暂缓 |
| 模板化预防 | 在智能体生成 Mermaid 的系统提示词中强制注入五规则；为各类工作流生成的 Mermaid 图表提供专用模板；开发 Mermaid 代码片段生成器 | 从生产端杜绝问题，而非仅在检测端拦截 | ✅ 已完成：向 developer/architect/reviewer 三角色系统提示词注入Mermaid安全编码五规则（含空行禁令、文本引号、列表触发规避、Subgraph安全格式、模板优先使用）；`.agents/templates/mermaid-templates/` 提供 7 种安全模板（flowchart-LR/TB/with-subgraphs/decision、sequenceDiagram、stateDiagram、mindmap），修正圆形节点语法错误并补充状态图/思维导图模板；代码片段生成器需IDE支持，暂缓 |
| 跨渲染器测试 | 建立多平台（GitHub/GitLab/飞书/Notion/VS Code）渲染验证流程；记录各平台 Mermaid 版本差异和已知问题；CI 中增加渲染截图对比 | 解决"本地正常、线上失败"问题 | ⏳ 待执行：依赖基础设施建设 |

## 核心思路

防护体系采用**双防线策略**：
- **预防端**：模板内置安全格式 + 智能体提示词注入规范，减少错误 Mermaid 的产生
- **检测端**：check-mermaid.py + CI 集成，在提交前拦截遗漏问题

当前双防线中，**检测端**已达到生产可用水平（10种图表类型分发检测、7种节点形状、14种箭头、dry-run预览、CI门禁、自动修复51个代码块）；**预防端**已完成提示词注入+7种安全模板，从生产端杜绝常见错误。剩余待执行项为跨渲染器测试（依赖基础设施）和AST级别校验（需引入Node.js依赖）。

---
*来源：[Mermaid 渲染问题修复复盘](../README.md)*
