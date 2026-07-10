---
template_name: "four-file-atomic-retrospective"
template_version: "2.2"
template_type: "retrospective"
created_date: "2026-07-05"
updated_date: "2026-07-09"
description: "四文件原子化复盘模板v2.2，融合P0-P4五级优先级+ROI评估+五维分析框架+跨Vendor知识融合+交叉引用规范"
compatible_with: "task-execution-summary v2.4, cross-vendor-knowledge-fusion L1"
source: "external: 目录无README-../../../../vendor/flexloop/apps/chaos/.agents/skills/task-execution-summary + SpecWeave复盘最佳实践 + cross-vendor-knowledge-fusion模式"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/templates/four-file-atomic-retrospective-v2/README.toml"
tags: ["retrospective", "template", "four-file", "P0-P4", "ROI", "atomic-document", "vendor-fusion", "cross-vendor"]
---
# {任务名称}复盘

> **复盘类型**：{任务完成复盘/项目里程碑复盘/故障排查复盘/学习总结复盘/vendor知识融合复盘}
> **复盘日期**：{YYYY-MM-DD}
> **任务名称**：{任务名称}
> **产出物位置**：{指向主要交付物的相对路径}
> **涉及Vendor/外部知识**：{是/否；如"是"，注明来源，如vendor/flexloop/task-execution-summary}

## 📋 复盘文档

| 文档 | 内容 |
|------|------|
| [retrospective-report.md](retrospective-report.md) | 完整复盘报告：执行摘要→事实收集→五维分析→知识融合决策（可选）→过程分析→改进建议 |
| [insight-extraction.md](insight-extraction.md) | 洞察萃取：{N}个可复用模式的5-Whys根因分析与模式描述（含融合类模式专用模板） |
| [export-suggestions.md](export-suggestions.md) | 导出建议：P0-P4五级优先级行动项+ROI评估+短/中/长期计划+模式验证跟踪 |

## 🎯 核心结论

**{一句话核心结论}**

- ✅ **交付成果**：{量化交付数据，如：X个文档/Y行代码/Z个问题修复}
- 💡 **关键洞察**：{N}个可复用洞察（其中P0级{N}个，P1级{N}个）
- 🔀 **知识融合**：{如涉及vendor融合，说明融合了什么；如不涉及填"N/A"}
- 📈 **效率提升**：{如有，量化效率数据}
- 🐛 **问题修复**：{如有，修复问题数量}

## 💡 关键洞察概览

| # | 洞察名称 | 优先级 | 成熟度 | 类型 | 核心价值 |
|---|---------|--------|--------|------|---------|
| 1 | {洞察1名称} | {P0/P1/P2} | {L1候选/L1/L2} | {流程/技术/工具/方法论/协作/融合} | {一句话价值} |
| 2 | {洞察2名称} | {P0/P1/P2} | {L1候选/L1/L2} | {流程/技术/工具/方法论/协作/融合} | {一句话价值} |
| ... | ... | ... | ... | ... | ... |

## 📐 新增/更新可复用模式

| 模式名称 | 成熟度 | 类型 | 触发场景 | 位置 |
|---------|--------|------|---------|------|
| {新模式1} | {L1候选} | {流程/工具/融合/...} | {一句话触发场景} | [链接] |
| {更新模式1} | {L1→L2} | {流程/工具/融合/...} | {一句话触发场景} | [链接] |

## 🔗 关联产出物

- **主要交付物**：{链接列表}
- **前序任务/复盘**：{链接列表}
- **Vendor/外部知识来源**：{如涉及，列出AGENTS.md/SKILL.md等高层文档链接；不涉及填"N/A"}
- **关联模式文档**：{链接列表}
- **关联Spec/任务看板**：{链接列表}

---

## 模板使用说明

### 适用场景
- 中大型任务（5个以上步骤）完成后复盘
- 需要沉淀可复用模式/方法论的任务
- 需要明确行动项跟踪的任务
- 知识库/Wiki/文档类创建任务
- ⭐ **v2.1新增**：吸收vendor子模块/外部开源项目优秀设计的融合类任务

### 不适用场景
- 简单、重复性小任务（使用单文件摘要版即可）
- 任务仍在进行中（不应提前复盘）
- 用户仅要求快速总结不需要沉淀

### 文件职责
| 文件 | 职责 | 核心内容 |
|------|------|---------|
| README.md | 入口导航 | 核心结论、洞察概览、文档索引（单一职责：导航） |
| retrospective-report.md | 事实与分析 | 执行摘要、事实收集、五维分析、**知识融合决策回顾（可选）**、过程分析（单一职责：事实记录与分析） |
| insight-extraction.md | 洞察萃取 | 每个洞察的5-Whys分析、模式描述、验证状态，**含融合类洞察专用模板**（单一职责：知识萃取） |
| export-suggestions.md | 行动落地 | P0-P4行动项、ROI评估、短/中/长期计划、风险预警、**模式验证与成熟度跟踪**（单一职责：落地执行） |

> **实际使用命名变体**：部分复盘使用 `execution-retrospective.md` 替代 `retrospective-report.md`、`insight-action-backlog.md` 替代 `export-suggestions.md`，文件职责相同，仅命名差异。

### 🔗 交叉引用规范（原子化文档互链规则）

**核心原则**：原子化拆分后，读者应能从任意文件跳转到其他任意文件，形成完整的导航闭环。

**两层引用结构**：
1. **头部快速导航（blockquote引用区）**：每个子文件（非README）的frontmatter之后、正文之前，用 `>` 引用块添加一行导航，方便读者刚打开文件时快速跳转：
   ```markdown
   > 来源：[README.md](README.md) → [execution-retrospective.md](execution-retrospective.md)
   > 相关文档：[洞察萃取](insight-extraction.md) | [行动项Backlog](insight-action-backlog.md) | [主索引](README.md)
   ```
2. **末尾关联文档章节**：每个子文件末尾设「关联文档」章节，列出所有兄弟文件链接及一句话说明，方便读者读完当前文件后导航：
   ```markdown
   ## 关联文档

   - **洞察萃取**：[insight-extraction.md](insight-extraction.md) - 5个可复用洞察及5-Whys根因分析
   - **执行复盘**：[execution-retrospective.md](execution-retrospective.md) - 任务时间线、事实数据、过程分析
   - **主索引**：[README.md](README.md) - 复盘目录索引与核心结论
   ```

**互链矩阵（四文件必须全部满足）**：
| 从↓ 到→ | README | execution-retrospective | insight-extraction | insight-action-backlog |
|---------|--------|------------------------|--------------------|-----------------------|
| README | — | ✅ 文档索引表链接 | ✅ 文档索引表链接 | ✅ 文档索引表链接 |
| execution-retrospective | ✅ | — | ✅ 末尾关联文档 | ✅ 末尾关联文档 |
| insight-extraction | ✅ | ✅ | — | ✅ 头部+末尾双链接 |
| insight-action-backlog | ✅ | ✅ | ✅ | — |

**路径规则**：
- 同目录文件互链使用**纯文件名相对路径**（如 `[文本](insight-extraction.md)`），不要加 `./`
- 引用外部模式/知识库文件使用正确层级的 `../` 相对路径
- 不要使用绝对路径或 `docs/` 前缀
- 原子化拆分后务必运行 `finalize-atomization.py`，脚本会自动校正相对路径层级错误

**反模式（禁止）**：
- ❌ 单方向引用（A能跳到B但B跳不回A）
- ❌ 只有末尾关联没有头部导航（长文件需要在顶部就能看到导航）
- ❌ 孤立文件（某个文件没有任何其他文件链接到它）
- ❌ README中不列出子文件索引（读者打开README后无法找到子文件）

**验证方法**：拆分完成后运行 `check-links.py --path <目录>`，正文本地引用应100%通过；手动检查每个文件的头部和末尾都有互链。

### 条件性章节标记说明
模板中用以下标记表示可选章节：
- 🔀 **【可选·vendor融合任务专用】**：当任务涉及吸收vendor/外部优秀设计时填写，其他任务可直接跳过
- 👥 **【可选·多角色协作专用】**：多人/多Agent协作时填写
- 📊 **【可选·有量化数据时填写】**：有明确量化数据时填写，没有可跳过

### v2.1 新增特性（整合跨Vendor知识融合三步法）
1. 🔀 **知识融合决策回顾章节**：在复盘报告中新增可选章节，包含理解Vendor/认知自我/优势互补的结构化决策记录
2. ✅ **融合决策检查清单**：6项自检问题，避免全盘照搬和NIH综合征两个极端反模式
3. 🧩 **三栏决策表模板**：✅吸收/⚠️适配/❌不吸收的结构化记录
4. 💡 **融合类洞察专用模板**：洞察萃取中增加知识融合类模式的专用结构
5. 📈 **模式成熟度升级跟踪**：导出建议中增加新模式从L1候选→L1→L2的验证跟踪
6. ⚠️ **反模式自检表**：5个绝对禁止的融合反模式自检

### v2.0 已有特性（基于vendor task-execution-summary）
1. ✅ **P0-P4五级优先级**：替代原高/中/低三级，更精细的优先级排序
2. ✅ **ROI评估字段**：每个行动项包含预期收益、实施难度、ROI评级
3. ✅ **五维分析框架**：目标达成度/时间效能/资源利用/问题模式/协作效果
4. ✅ **问题模式统计**：跨问题共性识别，不只是单个问题分析
5. ✅ **风险预警矩阵**：可能性×影响程度的风险评估
6. ✅ **短/中/长期行动分组**：1周内/1个月内/持续进行

### 关联模式参考
- 使用本模板做vendor融合类复盘时，参考：[cross-vendor-knowledge-fusion.md](../../patterns/methodology-patterns/research-knowledge/cross-vendor-knowledge-fusion.md)
- 研究vendor仓库时，第一步使用：[vendor-high-level-doc-first-research.md](../../patterns/methodology-patterns/research-knowledge/vendor-high-level-doc-first-research.md)
- 遇到工具故障时，参考：[tool-failure-three-tier-degradation.md](../../patterns/methodology-patterns/tools-automation/tool-failure-three-tier-degradation.md)

---

> **模板版本**：v2.2 (2026-07-09)
> **变更记录**：
> - v2.2 (2026-07-09)：新增交叉引用规范（两层引用结构+互链矩阵+路径规则+反模式+验证方法）；补充实际使用命名变体说明（execution-retrospective/insight-action-backlog）
> - v2.1 (2026-07-05)：整合cross-vendor-knowledge-fusion L1模式，新增知识融合决策回顾可选章节、融合检查清单、三栏决策表、融合类洞察模板、模式成熟度跟踪
> - v2.0 (2026-07-05)：融合vendor task-execution-summary skill设计，新增P0-P4优先级、ROI评估、五维分析框架
