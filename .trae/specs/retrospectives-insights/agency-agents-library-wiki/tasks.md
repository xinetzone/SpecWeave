# Tasks

## 阶段 0：规划与事实采集（R 阶段）

- [x] Task 1: 系统研读 `d:\AI\.chaos\libs\agency-agents` 源文件夹并采集客观事实
  - [x] 研读顶层文件：README.md、LICENSE、CONTRIBUTING.md、SECURITY.md、divisions.json、tools.json
  - [x] 研读部门目录结构与代表性 Agent 文件（engineering、design、marketing、specialized 等）
  - [x] 研读 `scripts/` 脚本体系（install.sh、convert.sh、lib.sh、check-*.sh、i18n/）
  - [x] 研读 `integrations/` 多工具集成（claude-code、cursor、codex、opencode、kimi 等 15+ 工具）
  - [x] 研读 `strategy/`（coordination、playbooks、runbooks、EXECUTIVE-BRIEF、QUICKSTART）
  - [x] 研读 `.github/workflows/`（check-divisions、check-runbooks、check-tools、lint-agents）
  - [x] 研读 `examples/`（nexus-spatial-discovery、workflow-*）
  - [x] 记录关键事实：部门数量、Agent 数量、文件格式、脚本用法、集成清单、CI 检查项

## 阶段 1：Wiki 章节撰写（E 阶段，原子化）

- [x] Task 2: 撰写章节 00-overview.md（概述、核心价值、整体架构图、章节导航）
- [x] Task 3: 撰写章节 01-architecture.md（文件夹整体架构、顶层文件、目录结构、设计哲学）
- [x] Task 4: 撰写章节 02-agent-format.md（Agent 角色文件格式解析：frontmatter + 章节结构）
- [x] Task 5: 撰写章节 03-roster-divisions.md（各部门名册与功能介绍）
- [x] Task 6: 撰写章节 04-scripts-tooling.md（scripts/ 脚本体系：install/convert/lib/check）
- [x] Task 7: 撰写章节 05-integrations.md（多工具集成：integrations/ 目录详解）
- [x] Task 8: 撰写章节 06-usage-examples.md（使用示例：安装、选择、激活、自定义）
- [x] Task 9: 撰写章节 07-strategy-playbooks.md（strategy/ 策略与运行手册）
- [x] Task 10: 撰写章节 08-faq-troubleshooting.md（常见问题解答）
- [x] Task 11: 撰写章节 09-best-practices.md（最佳实践指南）
- [x] Task 12: 撰写章节 10-summary-resources.md（总结与资源）

## 阶段 2：索引与质量校验（V → C 阶段）

- [x] Task 13: 更新知识库父目录索引（`docs/knowledge/learning/03-agent-platforms-tools/` 或学习根 README），纳入 Wiki 导航
- [x] Task 14: 质量校验
  - [x] 运行链接检查脚本，修复所有断链
  - [x] 校验文件名 kebab-case 规范（`check-filename-convention.py`）
  - [x] 核验 11 个章节 YAML frontmatter 字段一致性
  - [x] 核验 Mermaid 图语法正确性
  - [x] 核验章节总数与覆盖范围（整体架构/子模块/代码解析/使用示例/FAQ/最佳实践）

## Task Dependencies

- Task 1（事实采集）是后续所有章节的前提
- Task 2-12（章节撰写）由 Task 1 产出支撑，章节间可并行，但依赖统一的格式约定与事实库
- Task 13（索引更新）依赖 Task 2-12 完成
- Task 14（质量校验）依赖全部章节与索引完成