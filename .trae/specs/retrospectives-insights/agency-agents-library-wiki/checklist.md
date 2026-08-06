# Checklist

## 阶段 0：规划与事实采集

- [x] Task 1 完成：源文件夹已系统研读，关键事实（部门数量、Agent 数量、文件格式、脚本用法、集成清单、CI 检查项）已采集
- [x] 事实采集覆盖：顶层文件、部门目录、scripts/、integrations/、strategy/、.github/workflows/、examples/ 全部区域

## 阶段 1：Wiki 章节撰写

- [x] 章节 00-overview 已创建，包含概述、核心价值、整体架构图、章节导航表
- [x] 章节 01-architecture 已创建，覆盖文件夹整体架构与设计哲学
- [x] 章节 02-agent-format 已创建，解析 Agent 文件格式（frontmatter + 章节结构）
- [x] 章节 03-roster-divisions 已创建，覆盖各部门名册与功能
- [x] 章节 04-scripts-tooling 已创建，覆盖脚本体系
- [x] 章节 05-integrations 已创建，覆盖多工具集成
- [x] 章节 06-usage-examples 已创建，包含使用示例
- [x] 章节 07-strategy-playbooks 已创建，覆盖策略与运行手册
- [x] 章节 08-faq-troubleshooting 已创建，包含常见问题解答
- [x] 章节 09-best-practices 已创建，包含最佳实践指南
- [x] 章节 10-summary-resources 已创建，包含总结与资源
- [x] 11 个章节全部包含 YAML frontmatter（id/title/source/date/category/tags）
- [x] 每个章节包含表格与/或 Mermaid 图，内容层次清晰
- [x] 章节间存在导航链接（上一章/下一章/目录）

## 阶段 2：索引与质量校验

- [x] 知识库父目录索引已更新，Wiki 可从父 README 发现
- [x] 链接检查通过：所有内部相对链接指向真实存在的目标文件
- [x] 文件名规范通过：全部为 kebab-case，无中文文件名
- [x] frontmatter 一致性核验通过：11 个章节字段一致
- [x] Mermaid 图语法正确
- [x] 覆盖范围完整：教程包含整体架构、各子模块功能、核心代码/文件解析、使用示例、常见问题解答、最佳实践指南六个核心部分
- [x] Wiki 内容语言通俗易懂，结构清晰，适合不同技术水平开发者阅读