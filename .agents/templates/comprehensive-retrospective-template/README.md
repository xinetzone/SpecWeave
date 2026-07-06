---
id: "templates-comprehensive-retrospective-template-readme"
title: "综合复盘报告标准模板使用说明"
source: "retrospective-specweave-full-lifecycle-20260705 (v1.4)"
x-toml-ref: "../../../.meta/toml/.agents/templates/comprehensive-retrospective-template/README.toml"
---

# 综合复盘报告标准模板（多文件SSOT架构）

> **来源**：基于 SpecWeave 13天全生命周期复盘（retrospective-specweave-full-lifecycle-20260705）沉淀，经去重优化后验证通过
> **v1.2.0**：2026-07-06 新增场景适配指南和文件选择矩阵
> **v1.0**：2026-07-05 首次发布

---

## 设计原则：SSOT单一事实源

本模板的核心理念是**每个信息模块有唯一的事实源（SSOT）**，其他文件通过交叉引用获取信息，从架构上消除重复：

| 文件 | SSOT职责 | 行数上限 |
|------|---------|---------|
| `README.md` | 入口导航：文件清单+核心数据摘要+快速链接 | <100行 |
| `execution-retrospective.md` | 执行概览：背景+目标+结果+Mermaid时间线+关键决策 | ~150行 |
| `execution-phases.md` | 阶段事实：按阶段详细记录"做了什么/交付了什么/数据" | ~250行（超限则拆分） |
| `insight-extraction.md` | 洞察萃取：成功/失败模式+根因分析+元方法论模式 | ~300行 |
| `export-suggestions.md` | 改进建议：按优先级排列的具体行动建议+模式成熟度更新 | ~250行 |
| `insight-action-backlog.md` | 行动项清单：含DoD验收标准的可执行行动项 | ~200行 |
| `final-execution-summary.md` | 闭环验证：行动项执行结果+自举验证+最终交付物清单 | ~180行 |

### 可选文件（按需使用）

| 文件 | 适用场景 |
|------|---------|
| `l3-pattern-application-report.md` | 当行动项包含模式升级（L2→L3）并验证时（含§二模板升级详细对比，无需单独l3-template-upgrade-details.md） |

---

## 场景适配指南（文件选择矩阵）

根据复盘项目的规模和周期，选择对应的文件组合：

| 场景类型 | 项目特征 | 必选文件 | 可选文件 | 省略文件 |
|---------|---------|---------|---------|---------|
| **A. 全生命周期大型复盘** | 周期≥1周、提交≥50次、多角色、含行动项闭环验证 | 全部7个核心文件 | l3-pattern-application-report.md（L3升级时） | — |
| **B. 单日/单任务中型复盘** | 单日执行、单类任务、有改进建议但行动项待后续执行 | README + execution-retrospective + execution-phases + insight-extraction + export-suggestions + insight-action-backlog | l3-pattern-application-report.md | final-execution-summary.md（行动项闭环后补充） |
| **C. 小型任务快速复盘** | <3小时、<5个文件变更、无模式升级 | README + insight-extraction + insight-action-backlog | execution-retrospective（如需概览） | execution-phases / export-suggestions / final-execution-summary / l3-*.md |

### execution-phases 组织方式选择

- **时间阶段组织（默认）**：适用于跨天/跨周的项目，按Phase 1/2/3...或日期划分
- **处理批次组织**：适用于批量操作类项目，按P0验证批/P1推广批/P2收尾批划分
- **功能模块组织**：适用于多模块并行项目，按模块A/模块B/模块C划分

---

## 文件拆分规则（Bisect + Overview 模式）

当某个文件超过行数上限时，使用**对半拆分+总览保持**模式：

1. **对半拆分**：按逻辑边界（如时间前半/后半、概览/明细）将内容拆分为两个文件
2. **总览保持**：在原文件保留简短摘要+指向拆分文件的链接
3. **命名约定**：`execution-phases-s1-s3.md` / `execution-phases-s4-s7.md`（按阶段范围）

示例：execution-phases.md 超过250行时 → 拆分为 execution-phases-part1.md + execution-phases-part2.md，原文件保留摘要+链接。

---

## 使用步骤

### Step 1：复制模板

```bash
# 将模板目录复制到目标复盘报告位置
cp -r .agents/templates/comprehensive-retrospective-template/* \
      docs/retrospective/reports/<category>/retrospective-<project-name>-<YYYYMMDD>/
```

### Step 2：替换占位符

所有 `{{占位符}}` 需要替换为实际内容。主要占位符：
- `{{项目名称}}` / `{{复盘主题}}`
- `{{YYYY-MM-DD}}` 系列日期
- `{{N}}` 序号
- 统计数据占位符（提交数、文件变更数等）

### Step 3：按需裁剪

根据上方"场景适配指南"选择文件组合，删除不适用的文件：
- 小型复盘（场景C）阶段<3个时，可合并 execution-phases 到 execution-retrospective
- 没有行动项执行阶段时，省略 final-execution-summary，但需在 execution-retrospective 中说明
- 不涉及L3模式升级时，省略 l3-pattern-application-report.md

### Step 4：遵循行数约束

- 严格遵守每个文件的行数上限，超限即拆分
- README.md 是入口文件，**必须保持 <100行**
- 交叉引用格式：`[描述](文件名.md#锚点)`

### Step 5：验证

完成后运行链接检查：
```bash
python .agents/scripts/check-links.py --path <复盘报告目录>
```

---

## 文件间引用规范

```
README.md（入口）
  ├──→ execution-retrospective.md（概览）
  │     ├──→ execution-phases.md（详细事实）
  │     └──→ insight-extraction.md（洞察，SSOT）
  ├──→ export-suggestions.md（建议，SSOT）
  │     └──→ insight-action-backlog.md（行动项，SSOT）
  └──→ final-execution-summary.md（闭环，SSOT）
        └──→ l3-*.md（可选验证报告）
```

**引用方向规则**：
- 高层文件可以引用低层文件的详细内容
- 低层文件不应重复高层文件的上下文，而是假设读者已通过README导航到达
- 同一信息只在一个文件中详细展开，其他地方用一句话+链接

---

## 与其他模板的关系

| 模板 | 适用场景 | 对比 |
|------|---------|------|
| 本模板（综合复盘） | 项目级/里程碑级/批量操作复盘，含行动项闭环（场景A/B） | 多文件，5-7个核心文件 |
| [insight-extraction-template.md](../insight-extraction-template.md) | 单任务/快速复盘（场景C） | 单文件，3段式 |
| [retrospectives-insights-task-template.md](../theme-templates/retrospectives-insights-task-template.md) | 复盘任务清单（todo） | 任务模板，非报告模板 |

---

## 版本历史

- v1.2.0 (2026-07-06)：新增场景适配指南（A/B/C三种场景文件选择矩阵）、execution-phases组织方式说明，优化"Step 3按需裁剪"指引
- v1.1 (2026-07-05)：l3-template-upgrade-details.md合并入l3-pattern-application-report.md §二，可选文件精简为1个
- v1.0 (2026-07-05)：基于 SpecWeave 13天全生命周期复盘沉淀，7个核心文件+2个可选文件
