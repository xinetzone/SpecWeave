# Tasks

- [x] Task 1：R 阶段——事实采集，深入通读 cordis 与 paper 两个文件夹内容
  - [x] SubTask 1.1：读取 cordis 根配置（package.json、tsconfig.base.json、vitest.config.ts、yakumo.yml、yarnrc.yml）与整体目录结构，梳理 monorepo 工作区划分
  - [x] SubTask 1.2：通读 core 包源码（context/events/fiber/logger/reflect/registry/service/utils），提取各文件职责
  - [x] SubTask 1.3：通读 loader/hmr/create/group/include/logger-console/timer/utils 各包源码与 README，提取功能要点
  - [x] SubTask 1.4：读取 paper/README.md 并解析 paper.pdf 全文（用 PDF 技能提取文本），提取论文核心概念、机制与贡献

- [x] Task 2：I 阶段——洞察，提炼核心概念与技术要点
  - [x] SubTask 2.1：归纳"时间可组合性/空间可组合性"两大维度与"可逆效应/响应式协同效应"两大机制的定义
  - [x] SubTask 2.2：归纳 Context/Service/Fiber/Registry 四类核心抽象的关系与职责边界
  - [x] SubTask 2.3：归纳论文（theory）与 Cordis（implementation）的对应关系，形成术语表

- [x] Task 3：E 阶段——萃取产出，编写原子化中文 Wiki 章节
  - [x] SubTask 3.1：创建教程目录 `docs/knowledge/learning/03-agent-platforms-tools/cordis-spatiotemporal-composability-wiki/`
  - [x] SubTask 3.2：编写 00-overview.md（概述与用途）、01-background-paper.md（论文背景与理论）
  - [x] SubTask 3.3：编写 02-repo-structure.md（文件结构与 monorepo 解析）、03-core-architecture.md（核心抽象）
  - [x] SubTask 3.4：编写 04-effects-coeffects.md（可逆效应与响应式协同效应机制）、05-plugin-system.md（插件与依赖注入）
  - [x] SubTask 3.5：编写 06-lifecycle.md（Fiber 状态机与生命周期）、07-loader-config.md（loader 声明式加载与配置合并）
  - [x] SubTask 3.6：编写 08-hmr.md（热更新）、09-aux-packages.md（create/group/include/logger-console/timer/utils）
  - [x] SubTask 3.7：编写 10-usage-examples.md（代码示例与 Mermaid 架构图）
  - [x] SubTask 3.8：编写 11-faq-notes.md（常见问题与注意事项）、12-summary-resources.md（总结与资源）

- [x] Task 4：编写方法论报告 seven-concepts-report.md（R→I→E + G1-G3 质量门记录）
  - [x] SubTask 4.1：记录事实采集清单与来源
  - [x] SubTask 4.2：记录洞察四元组（现象/根因/影响/建议）与术语表
  - [x] SubTask 4.3：记录萃取产出模式与质量门通过情况

- [x] Task 5：更新父目录导航 `docs/knowledge/learning/03-agent-platforms-tools/README.md`，纳入新教程入口

# Task Dependencies

- Task 2 依赖 Task 1
- Task 3 依赖 Task 2（章节内容需基于已提炼的概念）
- Task 4 依赖 Task 1、Task 2、Task 3（方法论报告覆盖全链路）
- Task 5 依赖 Task 3（教程章节落定后更新索引）