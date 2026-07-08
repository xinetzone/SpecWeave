---
version: 1.0
x-toml-ref: "../../../../.meta/toml/.trae/specs/standards-tools/agent-communication-protocols-wiki/checklist.toml"
---
# Agent 通信协议体系 Wiki 教程 - Verification Checklist

<!-- changelog -->
- 2026-07-03 | feat | 初始验证清单创建

## 文档结构与位置
- [ ] 原子化子目录 `docs/knowledge/learning/agent-communication-protocols/` 已创建
- [ ] 总览入口文件 `docs/knowledge/learning/agent-communication-protocols-wiki.md` 已创建
- [ ] 编号分章文件齐全：00-overview 至 11-quick-reference（共12个子文件）
- [ ] 每个文件遵循单一职责原则，聚焦一个主题

## Frontmatter 规范
- [ ] 所有 .md 文件包含 TOML frontmatter（--- 包裹）
- [ ] 每个文件包含 `version` 字段
- [ ] 子文件包含 `source` 字段标记溯源
- [ ] 总览入口包含 changelog 章节，使用 `<!-- changelog -->` 标记包裹

## Mermaid 图表合规
- [ ] 所有 Mermaid 代码块遵循安全编码六规则（对照 mermaid-guide.md）
- [ ] 无 click 事件绑定
- [ ] 无 HTML 标签注入
- [ ] 无 `end` 关键字（flowchart 用正确节点名替代）
- [ ] 无外部 CSS class 引用
- [ ] 无 JavaScript/script 注入风险
- [ ] 节点 ID 使用安全字符（字母数字下划线）
- [ ] 架构图（至少1个）存在于 00-overview.md
- [ ] 每个协议章节（01-04）包含至少1个架构图
- [ ] 05-comparison.md 包含分层架构图和选型决策树（至少2个图）
- [ ] 06-flows.md 包含至少4个时序图和1个状态图

## 内容完整性
- [ ] 00-overview.md：包含背景、生态全景、N×M集成问题、学习路径、章节导航
- [ ] 01-mcp.md：定义/发起方/核心功能/Client-Server架构/Tools/Resources/Prompts/JSON-RPC/stdio/HTTP/SSE/OAuth2.1
- [ ] 02-acp.md：定义/IBM-BeeAI/REST原生/零SDK/本地优先/mDNS发现/MIME/多传输支持（gRPC/ZeroMQ/本地总线）/离线发现/DID
- [ ] 03-a2a.md：定义/Google/50+合作伙伴/Agent Card/Task状态机/SSE/Well-Known URI/Push Notification/OAuth2/mTLS/TextPart/FilePart/DataPart/Artifact/生态现状
- [ ] 04-anp.md：定义/去中心化/W3C DID/JSON-LD/Agent市场/早期阶段说明
- [ ] 05-comparison.md：四层分层架构图、多维度对比表、ACP vs A2A深度对比、互补关系说明、选型决策树、分阶段采用路线图
- [ ] 06-flows.md：MCP工具调用时序图、A2A任务委派时序图、ACP本地协同时序图、混合场景端到端时序图、任务状态机状态图、协作模式分类
- [ ] 07-implementation.md：Agent Card JSON示例、MCP JSON-RPC示例、A2A tasks/send/get/SSE示例、ACP REST示例、curl命令、Python最小代码片段、常见陷阱
- [ ] 08-scenarios.md：企业数字员工团队、跨组织SaaS协作、边缘IoT/机器人、去中心化市场、AI编码助手（至少4类场景），每个场景含推荐协议组合和架构要点
- [ ] 09-glossary.md：≥15个术语，按字母排序，每个术语含中英文名称、定义、使用协议、交叉引用
- [ ] 10-resources.md：官方规范、GitHub仓库、学术论文（arXiv:2505.02279/2505.03864）、SDK工具、中文资源，分类整理
- [ ] 11-quick-reference.md：快速对比表、选型CheckList、API速查表、Agent Card模板、FAQ

## 交叉引用与链接
- [ ] 所有内部交叉引用使用相对路径，无 `file:///` 绝对路径
- [ ] 运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning/agent-communication-protocols` 无断链
- [ ] 总览入口的章节导航链接指向正确的子文件
- [ ] 术语表交叉引用指向对应详细章节
- [ ] 资源章节外部链接格式正确（Markdown链接）

## 内容质量
- [ ] 技术描述与官方规范一致，无事实性错误
- [ ] 客观中立，无厂商偏向性表述
- [ ] 中文为主，技术术语保留英文并附中文解释
- [ ] 协议间"互补而非竞争"的核心观点清晰传达
- [ ] ANP章节客观反映其早期发展阶段，不做过度推测
- [ ] 代码示例语法正确，可作为开发者参考
- [ ] JSON示例格式合法
- [ ] curl命令参数完整、可直接运行
- [ ] 对比维度全面（至少10个维度）
- [ ] 应用场景贴近实际，协议推荐理由充分

## 知识整合
- [ ] 内容与已有知识库文档（如agent-skills-wiki、karpathy-llm-coding-guidelines）风格一致
- [ ] 不重复已有文档内容（如MCP相关操作指南），聚焦于协议体系本身
- [ ] 为后续协议更新预留扩展空间（编号留有余量）
