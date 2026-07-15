---
version: "1.0"
source: "./insight-extraction.md"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/knowledge-content/retrospective-agent-proto-wiki-20260703/export-suggestions.toml"
id: "retro-agent-proto-wiki-export"
title: "Agent通信协议Wiki教程 - 改进建议与导出"
---
# Agent通信协议Wiki教程 — 改进建议与导出

## 六、改进建议

| 问题 | 改进措施 | 优先级 | 预期效果 | 状态 |
|------|---------|--------|---------|------|
| 子agent指令未自包含所有约束 | 提炼"技术文档章节创建"指令模板，将文件名/结构/格式/安全/风格/篇幅6大约束前置为标准模板 | 高 | 减少文件名错误、导航缺失等低级问题，预计降低50%的事后修复 | 已完成 |
| Mermaid合规性无自动检测 | 编写脚本扫描mermaid代码块，检测click/HTML/end节点ID/classDef/script违规 | 中 | 从人工检查变为自动检测，消除遗漏风险 | 已完成 |
| 子agent输出篇幅失控 | 对于内容型任务采用"先大纲后展开"两阶段模式，或在指令中设置硬上限 | 中 | 控制章节长度在合理范围，提升信息密度 | 已完成 |
| 07-implementation代码示例未运行验证 | 补充实际可运行的最小示例（至少MCP+A2A的Python/TypeScript），标注SDK版本 | 低 | 提升教程实用性，读者可直接复制运行 | 已完成 |
| ANP章节内容较薄 | ANP规范成熟后补充技术细节和交互流程 | 低 | 保持教程时效性 | 已完成 |

## 七、行动计划

| 优先级 | 改进项 | 具体措施 | 建议时间 | 状态 |
|--------|--------|---------|---------|------|
| 高 | 子agent指令模板化 | 升级subagent-atomic-task-template.md为六要素模板，新增Mermaid安全规则作为第六要素 | 2026-07-03 | 已完成 |
| 中 | Mermaid自动检测脚本 | 在lib/checks/mermaid.py中新增_check_security函数，检测click/HTML/end节点ID/javascript URL/事件处理器 | 2026-07-03 | 已完成 |
| 中 | 篇幅控制两阶段模式 | 沉淀two-stage-outline-then-expand.md模式文档至ai-collaboration目录 | 2026-07-03 | 已完成 |
| 低 | 代码示例验证 | 为MCP/A2A SDK示例补充安装命令和版本标注（mcp>=1.26.0/a2a-sdk） | 2026-07-03 | 已完成 |
| 低 | ANP章节补充 | 搜索ANP最新进展，补充三层协议架构/ADP规范/did:wba方法/发现机制 | 2026-07-03 | 已完成 |

## 八、模式成熟度更新

| 模式 ID | 成熟度变化 | 触发原因 | 更新时间 | 验证/复用次数 |
|---------|-----------|---------|---------|-------------|
| 原子化技术文档组织 | L2（已验证） | 本项目成功复用agent-skills-wiki模式 | 2026-07-03 | 2次 |
| 子agent约束前置 | L1→L2（已验证） | 从五要素升级为六要素，新增Mermaid安全规则，在2个项目中验证 | 2026-07-03 | 2次 |
| 类比锚点教学法 | L2（已验证） | 四层协议类比在多处验证有效，已补充USB-C/Wi-Fi/HTTP/互联网案例 | 2026-07-03 | 多次 |
| 三段式内容验证 | L1（已沉淀） | 本项目中终验发现自检遗漏问题，已沉淀至governance-strategy目录 | 2026-07-03 | 1次 |
| Mermaid安全检测 | L1（新提炼） | 从人工检查升级为自动化安全检测，覆盖click/HTML/script/end等6类违规 | 2026-07-03 | 1次 |
| 篇幅控制两阶段模式 | L1（新提炼） | 从改进建议中提炼"先大纲后展开"模式，已沉淀至ai-collaboration目录 | 2026-07-03 | 1次 |

## 九、知识沉淀路径

### 应沉淀至模式库的模式
1. **子agent约束前置指令模式**（P2）：✅ 已完成 → `docs/retrospective/patterns/methodology-patterns/ai-collaboration/subagent-atomic-task-template.md`（升级为六要素，新增Mermaid安全规则）
2. **三段式内容验证模式**（P4）：✅ 已完成 → `docs/retrospective/patterns/methodology-patterns/governance-strategy/three-stage-content-validation.md`
3. **篇幅控制两阶段模式**：✅ 已完成 → `docs/retrospective/patterns/methodology-patterns/ai-collaboration/two-stage-outline-then-expand.md`（先大纲后展开，控制子代理输出篇幅）

### 应更新现有方法论
- **原子化文档组织模式**（P1）：已有类似模式，补充"技术教程"这一适用场景
- **类比锚点教学法**（P3）：✅ 已完成 → `docs/retrospective/patterns/methodology-patterns/creative-design/cognitive-anchor-visualization.md`（补充四层协议栈类比案例：USB-C/Wi-Fi/HTTP/互联网）
- **Mermaid安全编码规则**：✅ 已完成 → `lib/checks/mermaid.py` 新增 `_check_security` 函数，覆盖click事件/危险HTML标签/事件处理器/javascript URL/end节点ID共6类安全违规检测

### 应更新教程内容
- **07-implementation代码示例**：✅ 已完成 → 为MCP Python/TypeScript SDK和A2A Python SDK示例补充安装命令（`pip install mcp>=1.26.0`/`npm install @modelcontextprotocol/sdk`/`pip install a2a-sdk`）和版本标注
- **04-anp章节**：✅ 已完成 → 补充ANP三层协议架构（身份层/元协议层/应用层）、did:wba DID方法、Agent Description Protocol (ADP) JSON-LD示例、Agent发现机制、IETF Draft状态更新

### 已可复用的资产
- 总览入口文件的frontmatter和导航表格式 → 可复用于其他wiki类教程
- 章节末尾导航表格格式 → 标准化
- 四大协议MCP/ACP/A2A/ANP的知识内容 → 可作为Agent通信领域的基础知识库
