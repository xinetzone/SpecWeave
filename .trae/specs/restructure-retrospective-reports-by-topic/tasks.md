# 任务清单

## 任务列表

- [x] 任务 1：创建主题子文件夹结构
  - [x] 子任务 1.1：在 `docs/retrospective/reports/` 下创建 5 个主题子文件夹：`atomization/`、`insight-extraction/`、`spec-system/`、`roles-teams/`、`project-governance/`

- [x] 任务 2：移动 atomization（原子化与文档重构）主题报告（9 份）
  - [x] 子任务 2.1：移动以下报告的原子化子目录及对应源 .md 文件至 `atomization/`

- [x] 任务 3：移动 insight-extraction（洞察与萃取）主题报告（8 份）
  - [x] 子任务 3.1：移动以下报告的原子化子目录及对应源 .md 文件至 `insight-extraction/`

- [x] 任务 4：移动 spec-system（规范体系建设）主题报告（7 份）
  - [x] 子任务 4.1：移动以下报告的原子化子目录及对应源 .md 文件至 `spec-system/`

- [x] 任务 5：移动 roles-teams（角色与团队管理）主题报告（3 份）
  - [x] 子任务 5.1：移动以下报告的原子化子目录及对应源 .md 文件至 `roles-teams/`

- [x] 任务 6：移动 project-governance（项目治理）主题报告（7 份）
  - [x] 子任务 6.1：移动原子化子目录及对应源 .md 文件至 `project-governance/`
  - [x] 子任务 6.2：将 `reports-duplication-optimization-report.md` 移动至 `project-governance/`

- [x] 任务 7：修正原子化子目录 README.md 的 TOML frontmatter `source` 字段路径
  - [x] 子任务 7.1：扫描全部 34 个原子化子目录的 `README.md` 文件
  - [x] 子任务 7.2：将 `source` 字段中的路径更新为新的主题子文件夹内路径

- [x] 任务 8：修正原子化子目录 README.md 中的关联报告相对链接
  - [x] 子任务 8.1：扫描全部 README.md 中"关联报告"部分的相对链接
  - [x] 子任务 8.2：将跨主题的 `../topic/report/` 更新为 `../../topic/report/`，同主题更新为 `../report/`

- [x] 任务 9：修正各子模块文档中的跨目录相对链接
  - [x] 子任务 9.1：扫描子模块文档中的相对链接
  - [x] 子任务 9.2：将 `](../../patterns/` 更新为 `](../../../patterns/`（适配深度 3 的新路径）

- [x] 任务 10：创建 `docs/retrospective/reports/README.md` 分类索引文件
  - [x] 子任务 10.1：编撰分类标准说明
  - [x] 子任务 10.2：列出每个主题下的完整报告清单
  - [x] 子任务 10.3：说明文件组织规则
  - [x] 子任务 10.4：添加快速查找指南

- [x] 任务 11：更新 `docs/retrospective/README.md`
  - [x] 子任务 11.1：更新目录树中 `reports/` 部分
  - [x] 子任务 11.2：更新"按主题分类"的报告索引

## 任务依赖

- 任务 2~6 依赖于任务 1（先创建目录再移入）
- 任务 7~9 依赖于任务 2~6（移动完成后才能确定准确的目标路径）
- 任务 10、11 依赖于任务 2~6（移动完成后才能编写准确的路径索引）
- 任务 2~6 之间无依赖，可并行执行
- 任务 7~9 之间无依赖，可并行执行
- 任务 10 和 11 可并行执行
