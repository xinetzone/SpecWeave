---
title: Vendor外部子模块协同框架复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "external: 模板引用-comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/spec-system/retrospective-vendor-submodule-collaboration-20260629/insight-action-backlog.toml"
project: retrospective-vendor-submodule-collaboration-20260629
template_upgrade: 2026-07-06（模板v1.2补建）
ssot:
  suggestions_source: export-suggestions.md
  insight_source: insight-extraction.md
---
# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | 行动计划高 | 沉淀可复用模式（四不原则/三区域/元数据外置） | 高 | 📋 待执行 | 3个方法论模式文件沉淀到patterns/ | - |
| IMP-002 | 行动计划高 | 更新知识库索引 | 高 | 📋 待执行 | VENDOR-INTEGRATION.md登记到docs/knowledge/README.md | - |
| IMP-003 | 改进建议/行动计划中 | Windows终端emoji编码自适应 | 中 | 📋 待规划 | lib/cli.py添加终端编码检测，GBK环境自动降级ASCII符号 | - |
| IMP-004 | 改进建议/行动计划中 | check-links.py Windows file:// URL解析bug修复 | 中 | 📋 待规划 | 正确处理Windows盘符路径，Windows环境链接检查准确率100% | - |
| IMP-005 | 改进建议/行动计划低 | CI集成vendor深度检查 | 低 | 📋 待规划 | pre-commit hook或CI添加repo-check.py vendor --deep检查 | - |

## 行动项详情

### IMP-001: 沉淀可复用模式
- **优先级**: 高
- **来源**: export-suggestions.md §4.2 行动计划
- **说明**: 将"四不原则"（不侵入/不直引/不跟版/不裸考）、三区域边界模型（SpecWeave主权区/flexloop主权区/接口层）、submodule元数据外置策略沉淀为方法论模式
- **建议产出物**: 
  - [三区域边界模型](../../../patterns/methodology-patterns/governance-strategy/three-zone-boundary-model.md)（L1）
  - `外部依赖四不原则（vendor-dependency-four-negatives.md）`（L1）
  - [Submodule元数据外置策略](../../../patterns/architecture-patterns/submodule-metadata-externalization.md)（L1）
- **状态**: 📋 待执行

---

### IMP-002: 更新知识库索引
- **优先级**: 高
- **来源**: export-suggestions.md §4.2 行动计划
- **说明**: 将VENDOR-INTEGRATION.md相关内容登记到docs/knowledge/README.md，新增troubleshooting条目：submodule内创建文件导致modified content
- **建议产出物**: [docs/knowledge/README.md](../../../../knowledge/README.md) 索引更新
- **状态**: 📋 待执行

---

### IMP-003: Windows终端emoji编码自适应
- **优先级**: 中
- **来源**: export-suggestions.md §4.1 改进建议
- **说明**: 在lib/cli.py中添加终端编码检测，GBK环境自动降级为ASCII符号（[✓][✗][!]），消除Windows用户运行脚本时的UnicodeEncodeError
- **建议产出物**: lib/cli.py编码检测功能
- **状态**: 📋 待规划

---

### IMP-004: check-links.py Windows file:// URL解析bug修复
- **优先级**: 中
- **来源**: export-suggestions.md §4.1 改进建议
- **说明**: 修复file:///d:/路径解析逻辑，正确处理Windows盘符
- **建议产出物**: check-links.py路径解析修复
- **状态**: 📋 待规划

---

### IMP-005: CI集成vendor深度检查
- **优先级**: 低
- **来源**: export-suggestions.md §4.1 改进建议
- **说明**: 考虑在pre-commit hook或CI中添加repo-check.py vendor --deep检查，防止PR引入非法vendor引用
- **建议产出物**: CI配置更新
- **状态**: 📋 待规划

## 模式成熟度新增

| 模式 ID | 成熟度 | 触发原因 | 更新时间 |
|---------|--------|---------|---------|
| three-zone-boundary-model（三区域边界模型） | L1 | 本次首次成功实践三区域划分管理submodule | 2026-06-29 |
| vendor-dependency-four-negatives（外部依赖四不原则） | L1 | 本次从实践中提炼出"不侵入/不直引/不跟版/不裸考" | 2026-06-29 |
| submodule-metadata-externalization（submodule元数据外置） | L1 | 实践证明在submodule外管理元数据可避免dirty状态 | 2026-06-29 |
| spec-implementation-elastic-adjustment（Spec实施弹性调整） | L1 | 实施过程中基于事实调整checklist项，标注N/A及原因 | 2026-06-29 |

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| - | - | - | - |

## Changelog

- 2026-07-06 | create | 模板v1.2升级补建：从export-suggestions.md迁移5项行动项至独立backlog文件
