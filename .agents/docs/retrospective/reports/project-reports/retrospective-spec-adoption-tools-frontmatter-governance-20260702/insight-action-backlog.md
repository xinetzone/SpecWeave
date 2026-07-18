---
title: 规范度量工具增强与Frontmatter治理闭环复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "external: 模板引用-comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/reports/project-reports/retrospective-spec-adoption-tools-frontmatter-governance-20260702/insight-action-backlog.toml"
project: retrospective-spec-adoption-tools-frontmatter-governance-20260702
template_upgrade: 2026-07-06（模板v1.2补建）
ssot:
  suggestions_source: export-suggestions.md
  insight_source: insight-extraction.md
---
# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。全部4项行动项均已闭环完成。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | 行动项1 | check-spec-adoption.py添加--profile参数 | P0 | ✅ 已完成 | --profile docs/specs/code可用，权重自动调整，specs profile实测.agents/综合评分91.3/A | 2026-07-02 |
| IMP-002 | 行动项2 | gitignore-validation模式补充新工具Checklist | P0 | ✅ 已完成 | 模式文档包含新增工具→检查产出物→更新.gitignore流程，8项强制Checklist+.pytest_cache遗漏案例 | 2026-07-02 |
| IMP-003 | 行动项3 | cross-platform-encoding模式补充stdin-bytes方案 | P1 | ✅ 已完成 | 模式文档包含Python subprocess stdin-bytes代码示例，新增方案D含完整git_commit函数 | 2026-07-02 |
| IMP-004 | 行动项4 | add-agents-frontmatter.py添加格式校验 | P1 | ✅ 已完成 | 自动检测TOML/YAML混合语法并报错，新增detect_mixed_syntax函数 | 2026-07-02 |

## 行动项详情

### IMP-001: check-spec-adoption.py添加--profile参数
- **优先级**: P0
- **执行结果**: 添加--profile参数支持目录类型自适应权重（docs/specs/code三预设配置），specs profile实测.agents/综合评分91.3/A级
- **产出物**: [check-spec-adoption.py](../../../../../scripts/check-spec-adoption.py)
- **状态**: ✅ 已完成（前序实现）

---

### IMP-002: gitignore-validation模式补充新工具Checklist
- **优先级**: P0
- **执行结果**: 补充.pytest_cache/案例和"新工具引入Checklist"（8项强制检查清单+.pytest_cache遗漏案例+Why解释）
- **产出物**: [gitignore-validation.md](../../../patterns/code-patterns/gitignore-validation.md)
- **状态**: ✅ 已完成

---

### IMP-003: cross-platform-encoding模式补充stdin-bytes方案
- **优先级**: P1
- **执行结果**: 补充Python stdin-bytes修复方案（方案D：subprocess直接传递UTF-8字节绕过shell编码），含完整git_commit函数代码+4个关键要点+可靠性说明
- **产出物**: [cross-platform-encoding-enforcement.md](../../../patterns/code-patterns/cross-platform-encoding-enforcement.md)
- **状态**: ✅ 已完成

---

### IMP-004: add-agents-frontmatter.py添加格式校验
- **优先级**: P1
- **执行结果**: 新增detect_mixed_syntax函数，检测混合=/:赋值并标记error，自动检测TOML/YAML混合语法
- **产出物**: [add-agents-frontmatter.py](../../../../../scripts/add-agents-frontmatter.py)
- **状态**: ✅ 已完成

## 模式沉淀

| 模式名称 | 目标路径 | 成熟度 | 沉淀时间 |
|---------|---------|--------|---------|
| metric-tool-exclusion-profiling（度量工具排除与配置画像） | [metric-tool-exclusion-profiling.md](../../../patterns/methodology-patterns/tools-automation/metric-tool-exclusion-profiling.md) | L1 | 2026-07-02 |

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| IMP-001~004 | 2026-07-02 | - | 全部4项行动计划闭环完成，含2个代码模式文档更新、1个工具功能验证、1个工具增强、1个新模式沉淀（95分） |

## Changelog

- 2026-07-06 | create | 模板v1.2升级补建：从export-suggestions.md迁移4项已完成行动项至独立backlog文件
