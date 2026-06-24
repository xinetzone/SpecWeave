# 检查清单

## 目录结构

- [x] `docs/retrospective/reports/` 下存在 5 个主题子文件夹：`atomization/`、`insight-extraction/`、`spec-system/`、`roles-teams/`、`project-governance/`
- [x] `docs/retrospective/reports/` 根层级无遗留的原子化子目录（全部已移入主题子文件夹）
- [x] `docs/retrospective/reports/` 根层级无遗留的独立 .md 源文件（全部已移入主题子文件夹，除 README.md）

## 文件完整性

- [x] `atomization/` 包含 9 个原子化子目录 + 8 个对应源 .md 文件（`retrospective-report-reports-atomization-comprehensive-20260624` 无对应源文件，原始即无）
- [x] `insight-extraction/` 包含 8 个原子化子目录 + 8 个对应源 .md 文件
- [x] `spec-system/` 包含 7 个原子化子目录 + 7 个对应源 .md 文件
- [x] `roles-teams/` 包含 3 个原子化子目录 + 3 个对应源 .md 文件
- [x] `project-governance/` 包含 7 个原子化子目录 + 6 个对应源 .md 文件 + 1 个独立报告 (`reports-duplication-optimization-report.md`)（`retrospective-comprehensive-20260623` 无对应源文件，原始即无）
- [x] 总计 67 个文件/目录全部位于预期的主题子文件夹中

## TOML frontmatter source 路径

- [x] 所有原子化子目录 README.md 的 `source` 字段路径已更新为新的主题子文件夹内路径
- [x] 示例：`source = "docs/retrospective/reports/retrospective-report-agents-spec-system.md"` → `source = "docs/retrospective/reports/spec-system/retrospective-report-agents-spec-system.md"`

## 内部链接有效性

- [x] 所有原子化子目录 README.md 中子模块导航表的链接正确跳转到同目录文件
- [x] 所有原子化子目录 README.md 中"关联报告"部分的链接正确跳转到目标报告
- [x] 所有子模块文档（execution-retrospective.md 等）中的跨目录相对链接已修正（`../../patterns/` → `../../../patterns/`）
- [x] 不存在 `[xxx]()` 形式的空链接

## 上级 README 一致性

- [x] `docs/retrospective/README.md` 目录树中 `reports/` 部分反映 5 个主题子文件夹结构
- [x] `docs/retrospective/README.md` 中"按主题分类"的报告索引路径已更新
- [x] `docs/retrospective/README.md` 中报告索引的路径链接均有效

## 分类 README 完整性

- [x] `docs/retrospective/reports/README.md` 存在且内容完整
- [x] 包含 5 个主题类别的定义与说明
- [x] 包含每个类别下的完整报告清单（含简要描述）
- [x] 包含文件组织规则说明
- [x] 包含快速查找指南
