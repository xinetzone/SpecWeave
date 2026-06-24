+++
id = "retrospective-report-file-naming-convention-project-overview"
date = "2026-06-24"
type = "project-overview"
source = "docs/retrospective/reports/retrospective-report-file-naming-convention.md#一"
+++

# 一、项目概述

## 1.1 项目背景

项目中存在中英文混合命名的文件（如 `report-as-tracking载体.md`），导致跨平台兼容性问题、搜索排序不一致及规范不统一。用户提出制定并实施文件命名规范的需求。

## 1.2 项目目标

- 制定明确的文件命名规范（语言要求、字符限制、命名格式）
- 修复现有违规文件
- 建立命名审核机制（pre-commit hook、CI 检查）
- 更新相关文档和索引

## 1.3 交付物清单

| 交付物 | 类型 | 状态 |
|--------|------|------|
| `.agents/rules/file-naming-convention.md` | 规范文档 | ✅ 已完成 |
| `.agents/scripts/check-filename-convention.py` | 检查脚本 | ✅ 已完成 |
| `.git/hooks/pre-commit`（更新） | Git 钩子 | ✅ 已完成 |
| `.agents/scripts/ci-check.ps1`（更新） | CI 脚本 | ✅ 已完成 |
| `report-as-tracking.md`（重命名） | 模式文件 | ✅ 已完成 |
| 相关文档引用更新 | 文档维护 | ✅ 已完成 |

---