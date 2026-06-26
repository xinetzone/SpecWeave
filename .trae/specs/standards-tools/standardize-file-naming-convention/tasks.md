# 文件命名规范实施任务列表

## 任务 1：创建文件命名规范文档

- [x] 在 `.agents/rules/file-naming-convention.md` 创建规范文档
  - 定义语言要求（统一使用英文）
  - 定义允许字符（字母、数字、连字符、下划线）
  - 定义命名格式（kebab-case、snake_case 等）
  - 定义特殊字符限制
  - 定义保留名称

## 任务 2：重命名现有违规文件

- [x] 重命名 `docs/retrospective/patterns/methodology-patterns/report-as-tracking载体.md` 为 `report-as-tracking.md`
  - 更新文件内容中的内部链接（如有）
  - 更新 TOML frontmatter 中的 id 字段（从 `report-as-tracking载体` 改为 `report-as-tracking`）
  - 更新所有引用该文件的文档

## 任务 3：检查其他目录是否存在类似问题

- [x] 扫描 `docs/` 目录下是否存在其他中英文混合命名的文件
- [x] 扫描项目根目录是否存在其他违规文件名
  - 结果：vendor 目录中有外部依赖文件，已排除

## 任务 4：建立命名审核机制

- [x] 创建 Git pre-commit hook 脚本 `.agents/scripts/check-filename-convention.py`
  - 检查文件名是否包含非 ASCII 字符
  - 检查是否使用 kebab-case 或 snake_case
  - 检查 Windows 保留名称
- [x] 将检查脚本集成到 CI 流程 (ci-check.ps1)
- [x] 更新 pre-commit hook 集成文件名检查

## 任务 5：更新相关文档和索引

- [x] 更新 `.agents/scripts/README.md`（新增脚本说明）
- [x] 更新 `docs/retrospective/patterns/methodology-patterns/README.md`（链接修正）
- [x] 更新 `docs/retrospective/reports/` 下相关报告（链接修正）

## 任务依赖

- 任务 2 依赖于任务 1（需先有规范定义）✅
- 任务 4 依赖于任务 1 ✅
- 任务 5 依赖于任务 2 和任务 4 ✅
