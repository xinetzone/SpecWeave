---
id: "scripts-shared-lib-insights-index"
title: "脚本共享库提取复盘洞察索引"
source: "../insight-extraction.md"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-scripts-shared-lib-extraction-20260626/insights/README.toml"
---
# 脚本共享库提取复盘洞察索引

> 本目录存放从脚本共享库提取复盘中萃取的核心洞察。通用规律已归档至正式模式库，本目录文件保留事件发现叙事。
>
> 📖 **正式模式**：
> - 大规模重复消除五步法：[large-scale-duplication-elimination.md](../../../../../patterns/methodology-patterns/document-architecture/large-scale-duplication-elimination.md)（L2）
> - 工具自生验证7项检查清单：[tool-self-validation.md](../../../../../patterns/methodology-patterns/tools-automation/tool-self-validation.md)（L2）
> - 通用误报过滤规则引擎：[lib/rules.py](../../../../../../../scripts/lib/rules.py) + [config/false-positive-rules.toml](../../../../../../../scripts/config/false-positive-rules.toml)
>
> 🔗 **关联模式升级**：
> - diff-driven-refactoring L1→L2 | multi-agent-parallel-execution L2→L3 | structure-first-extension L2→L3

## 洞察清单

### 关键发现

| 文件 | 核心发现 | 归档至 |
|------|---------|--------|
| [finding-01-duplication-threshold.md](finding-01-duplication-threshold.md) | 重复代码的"3次阈值"规律——1-2次可接受、3-5次审计、6+次强制提取 | large-scale-duplication-elimination 量化阈值 |
| [finding-02-refactoring-bug-finder.md](finding-02-refactoring-bug-finder.md) | 重构即Bug发现器——统一实现暴露副本差异，发现路径解析bug | diff-driven-refactoring 价值公式验证 |
| [finding-03-concept-domain-separation.md](finding-03-concept-domain-separation.md) | 共享库的"概念域分离"原则——按概念域而非功能类型组织模块 | structure-first-extension 模式验证 |
| [finding-04-parallel-file-partition.md](finding-04-parallel-file-partition.md) | 并行子代理的"非重叠文件集"分工策略——按文件维度划分消除写冲突 | multi-agent-parallel-execution L3验证 |

### 规律认知

| 文件 | 核心规律 | 归档至 |
|------|---------|--------|
| [law-01-duplication-entropy.md](law-01-duplication-entropy.md) | 重复代码的"熵增定律"——无治理下随项目规模O(n^1.5)超线性增长 | 定期审计策略依据 |
| [law-02-shared-lib-gravity.md](law-02-shared-lib-gravity.md) | 共享库的"引力效应"——覆盖≥5概念域时正反馈启动 | "先查共享库"约定依据 |
| [law-03-spec-driven-planning.md](law-03-spec-driven-planning.md) | Spec驱动重构的"规划收益"——10+文件任务先规划后执行遗漏风险大幅降低 | Spec工作流验证 |

### 元洞察

| 文件 | 核心元洞察 | 归档至 |
|------|----------|--------|
| [meta-01-three-layer-value.md](meta-01-three-layer-value.md) | 重构的"三层价值"——消除重复50% + 发现Bug 30% + 结构基础20% | diff-driven-refactoring 价值公式扩展 |
| [meta-02-audit-scale-economy.md](meta-02-audit-scale-economy.md) | 审计先行的"规模效应"——≥10文件任务审计必选 | large-scale-duplication-elimination 第一步 |

### 执行过程新发现

| 文件 | 核心发现 | 归档至 |
|------|---------|--------|
| [finding-05-fp-three-categories.md](finding-05-fp-three-categories.md) | 静态分析工具的"误报三分类"——有意转发层/语言样板/真实重复 | false-positive-rules.toml 规则设计依据 |
| [finding-06-powershell-encoding-trap.md](finding-06-powershell-encoding-trap.md) | Windows PowerShell编码陷阱——需UTF-8 BOM+CRLF | 脚本开发规范补充 |
| [finding-07-tool-self-validation.md](finding-07-tool-self-validation.md) | "工具自生验证"模式——新linter立即扫描自身代码库 | tool-self-validation L2模式 |

## 落地状态总览

4项潜在机会全部落地：
- ✅ 自动化重复检测工具 → `check-duplication.py`
- ✅ 共享库API文档 → `lib/README.md` 自动生成
- ✅ "先查共享库"开发约定 → `.agents/docs/development-standards.md` + `AGENTS.md`
- ✅ 定期重构审计 → CI第10步集成

---
*数据来源：[脚本共享库提取复盘](../README.md)*
