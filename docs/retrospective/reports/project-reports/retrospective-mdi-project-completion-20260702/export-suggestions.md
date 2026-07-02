---
version: 1.1
id: mdi-export-suggestions
title: "MDI项目复盘导出建议"
category: retrospective
type: project-reports
source: "MDI项目复盘归档沉淀方案"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/project-reports/retrospective-mdi-project-completion-20260702/export-suggestions.toml"
date: 2026-07-02
---
# MDI项目复盘导出建议

## 导出目标

1. **模式库索引更新**：将3个新模式添加到对应目录的README.md ✅ 已完成
2. **docgen导航更新**：研究报告和复盘报告加入文档导航 ⏳ 待执行（本次更新后运行docgen）
3. **知识沉淀确认**：核心洞察已记录到insight-extraction.md ✅ 已完成
4. **路径规范修复**：修复绝对路径引用，统一使用相对路径 ✅ 已完成
5. **frontmatter补全**：所有文件补全必要的元数据字段 ✅ 已完成

## 导出渠道

| 渠道 | 内容 | 格式 |
|------|------|------|
| 模式库 | 3个新模式文档 | Markdown + TOML frontmatter |
| 复盘报告 | execution-retrospective.md | Markdown |
| 洞察文档 | insight-extraction.md | Markdown |
| 研究报告 | docs/knowledge/mdi-research-report.md | Markdown（已存在） |
| 文档导航 | docgen nav更新 | 自动生成 |

## 不需要额外导出的内容

- 源代码已通过原子提交入库
- 测试用例已在tests/目录
- 验证案例产物已在examples/mdi-output/

## Changelog

<!-- changelog -->
- 2026-07-02 | docs | v1.1：补全frontmatter，更新导出目标状态标记，新增路径规范修复和frontmatter补全项
- 2026-07-02 | docs | v1.0：初始版本，定义导出目标、渠道和不需要导出的内容
