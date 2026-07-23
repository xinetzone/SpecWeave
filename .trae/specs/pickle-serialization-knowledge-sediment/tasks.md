# Tasks

> **方法论编排 R→I→E 链路任务分解**
> 每个阶段产出须通过对应质量门（G1-G3）后方可推进下一阶段

## R 阶段：复盘事实采集

- [x] Task 1: 从三份源材料提取客观事实，形成复盘事实清单 ✅ G1 通过
  - [x] SubTask 1.1: 从 task-summary-20260723.md 提取修复事实（IdentityTransform 类、环境变量、诊断日志、11 测试、5 决策）
  - [x] SubTask 1.2: 从 DEBUG_PICKLE.md 提取诊断方法（pickle.dumps 诊断、spawn 复现、6 种模式、3 种修复方案）
  - [x] SubTask 1.3: 从 PICKLE_CHECKLIST.md 提取检查流程（5 步流程、代码审查附加项、错误信息对照表）
  - [x] SubTask 1.4: G1 质量门验证 — 事实清单无因果推断词，纯客观描述

## I 阶段：洞察根因分析

- [x] Task 2: 提炼四元组洞察（现象+根因+影响+建议），识别与已有沉淀的互补关系 ✅ G2 通过
  - [x] SubTask 2.1: 形成洞察四元组（现象：forkserver 下 lambda 不可 pickle；根因：pickle 通过 __module__.__qualname__ 引用，lambda qualname 为 <lambda>；影响：所有 Python 3.14+ multiprocessing 项目；建议：源码层修复优先，运行时兼容层兜底）
  - [x] SubTask 2.2: 差异化分析 — 源码层正本清源（治本，可改源码）vs 运行时兼容层（治标，不可改源码）
  - [x] SubTask 2.3: G2 质量门验证 — 四元组完整，根因触及 pickle qualname 本质，差异化定位清晰

## E 阶段：萃取模式入库

- [x] Task 3: 创建代码模式 `pickle-serialization-source-fix.md` ✅ G3 通过
  - [x] SubTask 3.1: 在 `.agents/docs/retrospective/patterns/code-patterns/` 创建文件，包含 frontmatter（id/title/type/date/maturity/source/related_patterns/tags）
  - [x] SubTask 3.2: 编写正文：模式概述、触发场景（可改源码 vs 不可改源码对比）、三种修复方案（命名类/命名函数/functools.partial）、pickle 四条黄金法则、反模式、与已有模式的互补关系声明、迁移验证、相关案例
  - [x] SubTask 3.3: G3 质量门验证 — 模式包含触发条件+核心步骤+反模式+迁移验证

- [x] Task 4: 创建最佳实践 `dataloader-pickle-diagnosis-sop.md` ✅ G3 通过
  - [x] SubTask 4.1: 在 `.agents/docs/knowledge/best-practices/` 创建文件，包含 frontmatter（id/title/category/tags/date/status/summary）
  - [x] SubTask 4.2: 编写正文：5 步诊断流程（复现→定位→识别→修复→验证）、6 种不可序列化模式对照表、3 种修复方案模板、跨启动模式验证矩阵、常见错误信息对照表、环境变量速查、代码审查附加检查项
  - [x] SubTask 4.3: G3 质量门验证 — SOP 可迁移（有触发条件+核心步骤+反模式+迁移验证）

## 索引同步与质量门验证

- [x] Task 5: 更新 code-patterns 索引 ✅
  - [x] SubTask 5.1: 在 `code-patterns/README.md` 模式清单表格新增 `pickle-serialization-source-fix.md` 条目
  - [x] SubTask 5.2: 确认与 `python-314-multiprocessing-fork-compat.md` 的关联在 related_patterns 字段中双向声明

- [x] Task 6: 更新 best-practices 索引 ✅
  - [x] SubTask 6.1: 在 `best-practices/README.md` 文档索引表格新增 `dataloader-pickle-diagnosis-sop.md` 条目
  - [x] SubTask 6.2: 在快速导航新增「序列化诊断」场景分组，关联 `python-version-upgrade-compatibility-check.md`

- [x] Task 7: G4 质量门与收尾验证 ✅ G4 通过
  - [x] SubTask 7.1: G4 验证 — 所有新增/更新文件满足原子化（单一职责、可独立验证）
  - [x] SubTask 7.2: 链接校验 — 新文档内引用使用相对路径，无 `file:///` 绝对路径断链
  - [x] SubTask 7.3: 溯源校验 — frontmatter 的 source 字段标注来源
  - [x] SubTask 7.4: 交叉引用完整性 — 新模式与已有互补模式的双向链接到位

# Task Dependencies

- Task 2 依赖 Task 1（洞察需基于事实）
- Task 3、Task 4 依赖 Task 2（萃取需基于洞察）
- Task 3 与 Task 4 可并行执行（独立文档）
- Task 5 依赖 Task 3，Task 6 依赖 Task 4（索引需文档先就位）
- Task 7 依赖 Task 5、Task 6（收尾验证需索引同步完成）