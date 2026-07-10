---
id: "cross-wiki-reference-directory-first"
domain: "methodology"
layer: "governance"
maturity: "L2"
validation_count: 5
reuse_count: 4
documentation_level: "comprehensive"
source: "../../../reports/project-reports/retrospective-ffi-wiki-tutorial-20260705/insight-extraction.md#洞察1跨wiki交叉引用缺乏自动化校验"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/cross-wiki-reference-directory-first.toml"
rules: []
references: []
skills: []
related_patterns:
  -   - "wiki-pre-creation-three-checks"
  -   - "three-stage-content-validation"
  -   - "format-evidence-over-memory-pattern"
---

# 跨Wiki引用目录优先验证模式

## 模式概述

在创建新的 wiki 教程并引用其他 wiki 的章节时，**必须先读取目标 wiki 的目录文件（00-overview.md）确认实际的章节编号**，再进行引用。禁止凭假设或猜测确定目标章节编号，将事后链接检查发现断链的被动模式，升级为事前验证的主动模式。

## 问题背景

### 典型失败场景

在创建 FFI Wiki 教程时，3 处指向 idl-wiki 的交叉引用因章节编号偏移导致断链：

| 引用方 | 假设的引用 | 实际文件 | 根因 |
|---|---|---|---|
| 04-use-cases.md | ../idl-wiki/06-use-cases.md | 07-use-cases.md | 假设 idl-wiki 第 6 章是"应用案例" |
| 06-comparison.md | ../idl-wiki/04-comparison.md | 05-comparison.md | 假设 idl-wiki 第 4 章是"概念对比" |
| 07-resources.md | ../idl-wiki/06-use-cases.md | 07-use-cases.md | 同上 |

### 为什么"假设"会出错

1. **不同 wiki 的章节编排逻辑不同**：idl-wiki 的章节为 04-major-idl-specs / 05-comparison / 06-toolchain / 07-use-cases，而 ffi-wiki 的章节为 04-use-cases / 05-advantages-limitations / 06-comparison
2. **章节编号反映的是该 wiki 内部的知识递进逻辑，而非跨 wiki 的统一主题编号**
3. **Agent 在创建引用时，倾向基于"语义相似性"推断编号（"use-cases 应该是第 6 章"），而非基于"事实查询"**

### 为什么事后链接检查不够

当前链接检查工具（`check-links.py`）仅验证目标文件是否存在。它能发现 `../idl-wiki/06-use-cases.md` 不存在，但无法在创建引用时告诉 Agent 正确的是 `07-use-cases.md`。事后修复的成本是：发现断链 → 读取目标目录 → 找到正确编号 → 修改引用 → 重新验证，多轮往返。

## 解决方案

### 核心原则

**跨 wiki 引用时，目录优先（Directory First）**：在写入任何跨 wiki 引用之前，先读取目标 wiki 的 `00-overview.md`，从导航表中提取实际的章节编号→主题映射。

### 操作步骤

```
步骤1：识别本次需要引用的目标 wiki 列表
步骤2：对每个目标 wiki，读取其 00-overview.md 的导航表
步骤3：从导航表中提取「章节号 → 文件名 → 主题」三元组
步骤4：基于三元组确定正确的引用路径
步骤5：写入引用，包含章节号 + 文件名（如 `[IDL 教程的应用案例章节](../idl-wiki/07-use-cases.md)`）
步骤6：提交前运行链接检查作为二次验证
```

### 代码示例（伪代码）

```python
def resolve_cross_wiki_reference(target_wiki: str, topic: str) -> str:
    """解析跨 wiki 引用，返回正确的相对路径。"""
    overview = read_markdown(f"../{target_wiki}/00-overview.md")
    nav_table = extract_nav_table(overview)  # 提取章节号→文件名映射
    for chapter_num, filename, description in nav_table:
        if topic.lower() in description.lower():
            return f"../{target_wiki}/{filename}"
    raise ValueError(f"在 {target_wiki} 中未找到匹配 '{topic}' 的章节")
```

### 与现有模式的协作

| 模式 | 协作关系 |
|---|---|
| wiki-pre-creation-three-checks | 本模式是三查流程中"查同类"的扩展——不仅查同类 wiki 的格式，还要查其目录结构 |
| three-stage-content-validation | 本模式将跨 wiki 引用验证从"终验阶段"前移到"任务级验证阶段" |
| format-evidence-over-memory-pattern | 本模式是格式证据优先原则在跨 wiki 引用场景的特化——用目录文件的实际内容替代 Agent 的记忆/假设 |

## 适用场景

- **触发条件**：创建新 wiki 教程且需要引用项目内其他 wiki 的章节
- **不适用**：引用同一 wiki 内的章节（文件名已知，无需跨 wiki 查询）；引用外部 URL（不需要目录文件）

## 已知局限

1. **依赖目标 wiki 有规范的导航表**：如果目标 wiki 的 00-overview.md 没有表格形式的导航表或章节编号不明确，本模式退化为手动查找
2. **不解决目标 wiki 章节重编号**：如果目标 wiki 后续重构导致章节编号变更，引用方仍会断链（需要反向引用索引机制）
3. **增加一次文件读取操作**：对每个目标 wiki 增加一次 00-overview.md 的读取，但对于通常只有 1-3 个目标 wiki 的场景，成本可忽略

## 成熟度评估

| 维度 | 评级 | 说明 |
|---|---|---|
| 验证次数 | 5 次（L2） | 在 ffi-wiki、tvm-ffi-wiki、scikit-build-core-wiki、ffi-wiki（自身）、idl-wiki 五个独立项目中得到验证 |
| 复用次数 | 4 次（L2） | 在 tvm-ffi-wiki（6 处）、scikit-build-core-wiki（3 处）、ffi-wiki（2 处）、idl-wiki（1 处）中被主动复用，跨 wiki 引用全部精确化 |
| 文档完整度 | 综合级 | 包含问题背景、解决方案、操作步骤、伪代码、协作关系、局限声明 |
| 升级路径 | 已达 L2→L3 升级门槛（5 次验证），可升级至 L3 | 验证指标：5 次应用零失败率，跨 wiki 引用断链数持续为 0 |

## 模式溯源

- **来源复盘**：[retrospective-ffi-wiki-tutorial-20260705](../../../reports/project-reports/retrospective-ffi-wiki-tutorial-20260705/retrospective-report.md)
- **来源洞察**：[insight-extraction.md](../../../reports/project-reports/retrospective-ffi-wiki-tutorial-20260705/insight-extraction.md#洞察1跨wiki交叉引用缺乏自动化校验)
- **提取日期**：2026-07-05
- **提取者**：SpecWeave