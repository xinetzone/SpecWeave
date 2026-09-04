# 文件命名规范验收清单

## 规范文档验收

- [x] `.agents/rules/file-naming-convention.md` 文件已创建
- [x] 规范明确定义语言要求（统一使用英文）
- [x] 规范明确定义允许字符（字母、数字、连字符、下划线）
- [x] 规范明确定义命名格式（kebab-case、snake_case 等）
- [x] 规范明确定义特殊字符限制
- [x] 规范明确定义保留名称

## 文件重命名验收

- [x] `report-as-tracking载体.md` 已重命名为 `report-as-tracking.md`
- [x] 重命名后的文件内容正确（无损坏）
- [x] TOML frontmatter 中的 id 字段已更新（从 `report-as-tracking载体` 改为 `report-as-tracking`）
- [x] 所有引用该文件的文档已更新（methodology-patterns/README.md、retrospective-report-suggestion-execution-and-pattern-import.md 等）

## 检查机制验收

- [x] `.agents/scripts/check-filename-convention.py` 检查脚本已创建
- [x] 检查脚本能正确识别非 ASCII 字符
- [x] 检查脚本能正确识别非 kebab-case/snake_case 格式
- [x] Git pre-commit hook 已配置
- [x] CI 流程 (ci-check.ps1) 已集成文件名检查

## 全局扫描验收

- [x] `docs/` 目录下无其他中英文混合命名的文件
- [x] 项目根目录无违规文件名（vendor 目录为外部依赖，已排除）
- [x] 脚本运行验证通过

## 文档更新验收

- [x] `.agents/scripts/README.md` 已更新（新增脚本说明）
- [x] `docs/retrospective/patterns/methodology-patterns/README.md` 已更新（链接修正）
- [x] `docs/retrospective/reports/` 下相关报告已更新（链接修正）
