---
id: "dependency-governance-index"
title: "依赖治理"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/project-governance/dependency-governance/README.toml"
---
# 依赖治理

> 本主题存放外部依赖与子模块治理相关复盘报告，涵盖 Git submodule 管理模式、边界模型、访问控制、跨平台兼容性等依赖质量保障工作。
>
> 本主题共包含 1 份报告，记录了从"单一模式禁止修改"到"双模式分类治理"的子模块治理框架升级过程，沉淀了双模式治理、条件导入、沙箱隔离、跨平台兼容等可复用实践。

## 报告列表

| 报告 | 日期 | 核心内容 | 子模块导航 |
|------|------|---------|-----------|
| [retrospective-vendor-flexloop-governance-adjustment-20260629/](retrospective-vendor-flexloop-governance-adjustment-20260629/) | 2026-06-29 | flexloop 子模块从第三方只读升级为自有协作模式，建立双模式子模块治理框架，萃取5个可复用模式 | [README](retrospective-vendor-flexloop-governance-adjustment-20260629/README.md) · [execution-retrospective.md](retrospective-vendor-flexloop-governance-adjustment-20260629/execution-retrospective.md) · [insight-extraction.md](retrospective-vendor-flexloop-governance-adjustment-20260629/insight-extraction.md) · [export-suggestions.md](retrospective-vendor-flexloop-governance-adjustment-20260629/export-suggestions.md) |

## 高频复用资产

| 资产 | 位置 | 用途 |
|------|------|------|
| 双模式子模块治理框架 | [patterns/methodology-patterns/governance-strategy/dual-mode-submodule-governance.md](../../../patterns/methodology-patterns/governance-strategy/dual-mode-submodule-governance.md) | 分类管理第三方只读和自有协作子模块 |
| 条件导入安全模式 | [patterns/code-patterns/temporary-syspath-modification.md](../../../patterns/code-patterns/temporary-syspath-modification.md) | 临时修改 sys.path 导入可选依赖，不污染全局状态 |
| 跨平台编码强制设置 | [patterns/code-patterns/cross-platform-encoding-enforcement.md](../../../patterns/code-patterns/cross-platform-encoding-enforcement.md) | 避免 Windows GBK 终端 UnicodeEncodeError |
| 路径锚点语义化 | [patterns/code-patterns/path-anchor-semantization.md](../../../patterns/code-patterns/path-anchor-semantization.md) | 避免链式 parent 计算差一级的常见 bug |
| 新检测规则存量暴露效应 | [patterns/methodology-patterns/tools-automation/legacy-exposure-effect.md](../../../patterns/methodology-patterns/tools-automation/legacy-exposure-effect.md) | 新 linter/checker 落地前先扫描存量问题 |

---
[返回项目治理报告索引](../README.md)
