# Tasks

> 方法论：seven-concepts 场景 4（知识沉淀），链路 R→I→E→V→C；G1-G4 质量门强制。

- [x] Task 1: R 复盘——采集 AGENTS.md 与 .agents/ 结构事实清单
  - [x] 1.1 枚举根 AGENTS.md 的核心章节与启动协议要点
  - [x] 1.2 枚举 .agents/ 顶层目录与关键子目录结构
  - [x] 1.3 提炼 ≥20 条客观事实（无因果词，G1），区分「SpecWeave 特有要素」与「通用可泛化要素」
- [x] Task 2: I 洞察——提炼可泛化的核心模式
  - [x] 2.1 输出 ≥3 条四元组洞察（现象/根因/影响/建议，G2）
  - [x] 2.2 识别「启动协议」「四大区域对称结构」「渐进式披露」「内容敏感度分流」等可泛化要素
- [x] Task 3: E 萃取——生成通用脚手架
  - [x] 3.1 创建 `templates/README.md`（索引）
  - [x] 3.2 创建 `templates/agent-workspace-hub/AGENTS.md`（通用模板，占位符参数化）
  - [x] 3.3 创建 `templates/agent-workspace-hub/.agents/` 精简骨架（关键子目录 + 占位 README）
  - [x] 3.4 创建 `templates/agent-workspace-hub/README.md`（使用说明）
- [x] Task 4: E 萃取——沉淀可复用模式文档
  - [x] 4.1 创建 `docs/retrospective/patterns/architecture-patterns/agent-workspace-template.md`
  - [x] 4.2 补充 TOML frontmatter（id/domain/layer/maturity/validation_count/source 等，G3）
  - [x] 4.3 更新模式库索引并建立双向导航链接
- [x] Task 5: V 对抗审查——四视角攻击并修正
  - [x] 5.1 以魔鬼代言人/新人/老板/未来四视角审查模板与模式文档
  - [x] 5.2 产出 ≥5 条具体意见并采纳 ≥2 条修正
- [x] Task 6: C 原子提交——校验与交付
  - [x] 6.1 文件命名/frontmatter/链接/单文件行数预提交校验
  - [x] 6.2 三查暂存法 + Conventional Commits 原子提交（UTF-8，G4）

# Task Dependencies
- Task 2 依赖 Task 1
- Task 3、Task 4 依赖 Task 2（可并行）
- Task 5 依赖 Task 3、Task 4
- Task 6 依赖 Task 5