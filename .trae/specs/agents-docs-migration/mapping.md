# 逐文件迁移映射表（mapping.md）

> 任务：`.agents/docs/`（2698 文件）统一迁移至 `docs/` 文档中心。
> 依据：[spec.md](spec.md) §4 迁移映射总纲、§7.3 决策 D1-D6（已批准）；[tasks.md](tasks.md) Task 1。
> 方法论：七概念场景3 重构链路 I→F→A→C，本表为 F（First Principles）阶段产出，是 Task 2 物理迁移的执行依据。
> 盘点方式：`mapping-inventory.py` / `verify-concepts.py` 实测（2026-08-31），仓库根 `d:\AI`。

---

## 1. 三项去重核验结论（TR-1.2）

### 1.1 核验①：`retrospective/reports/concepts/` 旧副本 vs 新侧策展集

- 旧侧 36 文件；新侧 `docs/retrospective/reports/concepts/` 40 文件。
- **超集假设部分不成立**：5 个旧侧独有里程碑复盘在 `docs/` 全树（精确名 + stem[:40] 模糊匹配）均不存在，**必须回补迁入** `docs/retrospective/reports/concepts/milestone/`（目标目录存在、5 文件均确认 absent）：
  1. `blog-to-okf-bundle-12posts-milestone-retrospective-20260829.md`
  2. `blog-to-okf-bundle-llm-hallucination-governance-20260829.md`
  3. `blog-to-okf-bundle-milestone-retrospective-20260828.md`
  4. `screenshot-tool-event-driven-guardian-retrospective-20260825.md`
  5. `tvm-ffi-200-perspectives-milestone-retrospective-20260824.md`
- 其余 31 文件为新侧同名/策展版子集 → 丢弃（D2）；14 个同名但内容有差异的文件以新侧策展版为准（D2）。

### 1.2 核验②：`patterns/methodology-patterns/` 同名合并

- 旧侧 498 文件；新侧 23 文件（concepts/ 18 + 根级 5：index.md、log.md、destructive-probe-gate.md、history-based-doc-repair.md、preflight-integrity-gate.md）。
- 同名冲突 2 个：`concepts/index.md`（内容不同）→ **新侧策展版优先**，旧侧丢弃；`log.md`（md5 两侧完全一致 `b48e77df...`，5465 字节）→ 旧侧丢弃，零损失。
- 其余 496 个旧侧独有文件全部迁入（含 CATEGORIES.md、README.md 及 ai-collaboration/、creative-design/、document-architecture/、governance-strategy/、product-growth/、research-knowledge/、retrospective-knowledge/、spec-workflow/、tools-automation/ 等子树）。

### 1.3 核验③：`.meta/toml` 镜像与新旧 reports 根文件

- `.meta/toml/.agents/docs/` 1718 TOML vs `.meta/toml/docs/` 1076 TOML：**同名冲突 0、内容差异 0** → 按相同映射关系干净合并。
- `retrospective/reports/log.md`：旧/新 md5 完全一致（`57ea0999f642c8550df2d4a7cf82c2c2`）→ 旧侧丢弃，零损失。
- `retrospective/reports/index.md`：新旧不同；新侧为"策展概念目录表 + toctree"混合页且已包含旧版全部四行概念目录表（旧版另有 `okf_version` FM，而子目录 index.md 依门禁不允许 FM）→ 旧侧丢弃，零独有内容损失；22 类报告迁入后由 Task 5 扩 toctree 并人工复核。
- **假设修正**：spec §2.5 称 `patterns/docker-template-pattern-extraction-20260722.md` 已迁至新侧——全仓搜索证实该文件**仅存于旧侧**（此前迁移的是 pattern-comparison 另一份文件），故该文件**改为迁入** `docs/retrospective/patterns/` 根（与已落位的 pattern-comparison 文件同例：多模式汇总文件放 patterns/ 根），不做丢弃。

---

## 2. 逐目录映射表（TR-1.1）

路径均省略公共前缀：源 = `.agents/docs/`，目标 = `docs/`。

### 2.1 retrospective/patterns/（模式库，849 文件）

| 源 | 目标 | 文件数 | 依据/处置 |
|---|---|---|---|
| `retrospective/patterns/analysis-cards/` | `retrospective/patterns/analysis-cards/` | 6 | 模式库六类兄弟目录归位；目标目录 absent，新建 |
| `retrospective/patterns/architecture-patterns/` | `retrospective/patterns/architecture-patterns/` | 93 | 同上 |
| `retrospective/patterns/checklists/` | `retrospective/patterns/checklists/` | 2 | 同上 |
| `retrospective/patterns/code-patterns/` | `retrospective/patterns/code-patterns/` | 223 | 同上；含 examples/ 下 11 个 C++/Python 代码样例资产随迁 |
| `retrospective/patterns/documentation-patterns/` | `retrospective/patterns/documentation-patterns/` | 3 | 同上 |
| `retrospective/patterns/process-patterns/` | `retrospective/patterns/process-patterns/` | 22 | 同上 |
| `retrospective/patterns/methodology-patterns/` | `retrospective/patterns/methodology-patterns/`（合并） | 496 迁入 / 2 冲突丢弃 | 新侧已策展 23 文件；`concepts/index.md` 新侧优先、`log.md` 两侧一致（§1.2） |
| `retrospective/patterns/docker-template-pattern-extraction-20260722.md` | `retrospective/patterns/docker-template-pattern-extraction-20260722.md` | 1 | 多模式汇总文件落 patterns/ 根（§1.3 修正）；Task 5 加入策展表 |
| `retrospective/patterns/README.md` | — | 1 丢弃 | D3 纯索引，新侧 patterns/index.md 承担 |

小计：迁入 846，丢弃 3。

### 2.2 retrospective/reports/（报告库，1704 文件）

| 源 | 目标 | 文件数 | 依据/处置 |
|---|---|---|---|
| `retrospective/reports/adversarial-reviews/` | `retrospective/reports/adversarial-reviews/` | 31 | 22 类报告目录同名归位；目标均 absent，新建；非 md 资产随迁 |
| `retrospective/reports/atomization/` | 同名 | 54 | 同上 |
| `retrospective/reports/bug-fix/` | 同名 | 13 | 同上 |
| `retrospective/reports/bugfix/` | 同名 | 14 | 同上 |
| `retrospective/reports/build-engineering/` | 同名 | 46 | 同上 |
| `retrospective/reports/code-optimization/` | 同名 | 55 | 同上 |
| `retrospective/reports/competitive-analysis/` | 同名 | 359 | 含 3 png + 1 html + manifest.txt + report.json 资产随迁 |
| `retrospective/reports/documentation-governance/` | 同名 | 5 | 同上 |
| `retrospective/reports/environment-setup/` | 同名 | 12 | 含 1 png + 2 json 随迁 |
| `retrospective/reports/exported/` | 同名 | 2 | 含 1 txt 随迁 |
| `retrospective/reports/feature-development/` | 同名 | 2 | 同上 |
| `retrospective/reports/incident-reports/` | 同名 | 10 | 同上 |
| `retrospective/reports/insight-extraction/` | 同名 | 440 | generate-readme 信号确认落位；含 1 json 随迁 |
| `retrospective/reports/iteration-reports/` | 同名 | 3 | 同上 |
| `retrospective/reports/knowledge-content/` | 同名 | 10 | 同上 |
| `retrospective/reports/project-governance/` | 同名 | 304 | 同上 |
| `retrospective/reports/project-reports/` | 同名 | 57 | 同上 |
| `retrospective/reports/roles-teams/` | 同名 | 12 | 同上 |
| `retrospective/reports/spec-system/` | 同名 | 43 | 同上 |
| `retrospective/reports/standards-tools/` | 同名 | 14 | generate-readme 信号确认落位 |
| `retrospective/reports/task-reports/` | 同名 | 179 | 含 1 txt + 1 json；task-summaries/ 4 文件并入本目录（见 §2.4） |
| `retrospective/reports/concepts/` | `retrospective/reports/concepts/milestone/`（仅 5 文件回补） | 5 迁入 / 31 丢弃 | §1.1：5 个旧独有里程碑复盘回补；其余为新侧子集 |
| `retrospective/reports/index.md` | — | 1 丢弃 | 新侧 index.md 已含同表（§1.3） |
| `retrospective/reports/log.md` | — | 1 丢弃 | 新旧 md5 一致（§1.3） |
| `retrospective/reports/README.md` | — | 1 丢弃 | D3 纯索引 |

21 个整迁目录文件数合计 1665；小计：迁入 1670（1665 + 5 回补），丢弃 34（31 + 3 根级）。

### 2.3 retrospective/ 配套目录与根级文件（79 文件）

| 源 | 目标 | 文件数 | 依据/处置 |
|---|---|---|---|
| `retrospective/archives/` | `retrospective/archives/` | 10 | 复盘配套资产同名并入；目标 absent（含 .gitignore + 3 .gitkeep） |
| `retrospective/assets/` | `retrospective/assets/` | 5 | generate-readme 信号确认落位 |
| `retrospective/concepts/` | `retrospective/concepts/` | 11 | 复盘概念配套，目标 absent |
| `retrospective/frameworks/` | `retrospective/frameworks/` | 5 | 同名并入 |
| `retrospective/guides/` | `retrospective/guides/` | 7 | 同名并入 |
| `retrospective/templates/` | `retrospective/templates/` | 19 | generate-readme 信号确认落位 |
| 17 个日期复盘（`2026-07-06-*` ~ `2026-08-25-*`） | `retrospective/reports/` 根 | 17 | 日期复盘属报告；目标根无同名文件 |
| `retrospective/hardcode-retrospective-report.md` | `retrospective/reports/` 根 | 1 | 报告归 reports |
| `retrospective/meta-bootstrap-execution-log.md` | `retrospective/reports/` 根 | 1 | 执行日志归 reports |
| `retrospective/terminalworld-benchmark-analysis.md` | `retrospective/reports/` 根 | 1 | 分析报告归 reports |
| `retrospective/prompt-extraction.md` | `retrospective/patterns/methodology-patterns/prompt-extraction.md` | 1 | 提示词工程模式，归方法论模式库 |
| `retrospective/README.md` | — | 1 丢弃 | D3 纯索引，新侧 retrospective/index.md 承担 |

小计：迁入 78，丢弃 1。

### 2.4 其余顶层目录（66 文件）

| 源 | 目标 | 文件数 | 依据/处置 |
|---|---|---|---|
| `superpowers/`（plans 7 + specs 6 + README 1） | `superpowers/` | 14 | 顶层新板块；generate-readme `get_p1_dirs` 权威信号（plans/specs 须有 README） |
| `templates/` | `templates/` | 5 | 顶层；LINK_CHECK_EXCLUDE_DIRS 含 `docs/templates` 信号 |
| `code-wiki/`（7 md + README） | `tech/code-wiki/` | 8 | 源码学习 wiki 属本项目技术资产 |
| `standards/` | `tech/standards/` | 3 | 团队技术规范属 tech 板块 |
| `test-plans/` | `tech/test-plans/` | 2 | 测试计划属技术资产 |
| `plans/`（3 计划 + README） | `retrospective/plans/` | 4 | 治理行动计划与复盘配套（ACT 系列）；目标 absent |
| `task-summaries/`（3 个任务总结） | `retrospective/reports/task-reports/` | 3 迁入 | 任务总结报告并入 task-reports（3 文件目标均 absent） |
| `task-summaries/README.md` | — | 1 丢弃 | **执行期新增决策**：纯容器链接索引（指向旧容器 reports/patterns/superpowers/skills），目标 `task-reports/README.md` 已有正式文档表索引，同 D3 类 |
| `architecture/multi-agent-collab.md` | `tech/concepts/multi-agent-collab.md` | 1 | 架构概念文档 |
| `architecture/README.md` | — | 1 丢弃 | 旧容器板块索引（D3 类）：正文为 multi-agent-collab.md 的摘要表，链接面向 `.agents/` 内部；新侧 tech/concepts/index.md 承担索引 |
| `tools/docker-cache.md` | `tech/references/docker-cache.md` | 1 | 工具指南属技术参考 |
| `quality/mermaid-manual-fix-guide.md` | `tech/references/mermaid-manual-fix-guide.md` | 1 | 质量指南属技术参考 |
| `guides/thesis-writing-guide/`（1 html + 4 ttf + 1 js） | `_static/thesis-writing-guide/` | 6 | D6：Sphinx 静态资产，不触发 md 门禁、无需 toctree 可达；孤儿资产 |
| 根级 13 个项目文档（见 §2.5） | `tech/references/` | 13 | 项目级参考文档 |
| 根级 2 个研究文档（见 §2.5） | `topics/` | 2 | 方法论分析/泛化复用属 topics 语义 |
| 根级 `README.md` | — | 1 丢弃 | D3：旧容器边界说明，口径过时；docs/index.md 承担总导航 |

小计：迁入 63，丢弃 3。

### 2.5 根级 15 个项目文档落位（D4）

| 目标 `tech/references/`（13） | 目标 `topics/`（2） |
|---|---|
| project-overview.md、project-highlights.md、project-structure.md、roadmap.md、tech-stack.md、related-links.md、verification-automation.md、trae-project-adaptation-guide.md、agent-roles.md、collaboration.md、development-standards.md、raci-governance-standards.md、knowledge-base.md | methodology-analysis-report.md、reuse-and-generalization.md |

> 与 tech/concepts/ 既有结构化章节的内容重叠仅登记不融合（spec §3.2 非目标）。

---

## 3. 不迁移/去重清单（41 文件，逐项可追溯）

| # | 文件（源相对路径） | 处置 | 理由 |
|---|---|---|---|
| 1 | `README.md` | 丢弃 | D3 旧容器总索引 |
| 2 | `retrospective/README.md` | 丢弃 | D3 板块索引 |
| 3 | `retrospective/patterns/README.md` | 丢弃 | D3 板块索引 |
| 4 | `retrospective/reports/README.md` | 丢弃 | D3 板块索引 |
| 5 | `architecture/README.md` | 丢弃 | D3 类板块索引，内容为子文档摘要 |
| 6 | `retrospective/reports/index.md` | 丢弃 | 新侧 index.md 已含全部概念目录表 |
| 7 | `retrospective/reports/log.md` | 丢弃 | md5 与新侧完全一致 |
| 8 | `retrospective/patterns/methodology-patterns/concepts/index.md` | 丢弃 | 同名冲突，新侧策展版优先（§1.2） |
| 9 | `retrospective/patterns/methodology-patterns/log.md` | 丢弃 | 同名且 md5 两侧完全一致（§1.2） |
| 10 | `task-summaries/README.md` | 丢弃 | 执行期新增：纯容器链接索引，目标 task-reports/README.md 已承担（§2.4） |
| 11–41 | `retrospective/reports/concepts/` 下 31 文件 | 丢弃 | 新侧策展集超集（D2）；5 个旧独有文件已回补（§1.1） |

---

## 4. .meta 元数据镜像迁移与 x-toml-ref 改写规则

### 4.1 TOML 镜像迁移

- 源 `.meta/toml/.agents/docs/`（1718 文件）→ 目标 `.meta/toml/docs/`，**逐文件遵循与 md 相同的映射关系**（非简单前缀替换）：
  - 整迁目录（如 `retrospective/reports/insight-extraction/`）：TOML 子树同构平移；
  - 改落位文件（如 `architecture/multi-agent-collab.md` → `tech/concepts/`）：对应 TOML 同步落 `.meta/toml/docs/tech/concepts/multi-agent-collab.toml`；
  - §3 丢弃的 39 个 md 其对应 TOML 一并丢弃（Task 3 脚本计算精确计数）。
- 零碰撞前提：同名冲突 0、内容差异 0（§1.3）。

### 4.2 x-toml-ref 改写规则

实测格式（相对 md 文件所在目录的相对路径）：

```yaml
# 旧（.agents/docs/architecture/multi-agent-collab.md，深度 3）：
x-toml-ref: "../../../.meta/toml/.agents/docs/architecture/multi-agent-collab.toml"
# 新（docs/tech/concepts/multi-agent-collab.md，深度 3）：
x-toml-ref: "../../../.meta/toml/docs/tech/concepts/multi-agent-collab.toml"
```

改写公式：

1. 对每个迁入 md，取其新路径相对 `docs/` 的部分 `<new-rel>`（如 `tech/concepts/multi-agent-collab`）；
2. 计算新文件目录到仓库根的相对深度 `d`（`docs/tech/concepts/` → 3 级 `../`）；
3. 新值 = `d 个 ../` + `.meta/toml/docs/<new-rel>.toml`；
4. 脚本化执行，dry-run 先行；仅改写 `x-toml-ref` 行，其余内容零触碰；
5. TOML 文件内部若含路径字段，Task 3 抽查并按同规则改写；
6. 验证（AC-5）：docs/ 下全部 x-toml-ref 解析到真实 TOML，失败数 0。

---

## 5. 文件数守恒公式（TR-1.3）

```
源侧总数 2698
= retrospective 2632 + 非 retrospective 66

retrospective 2632 = patterns 849 + reports 1704 + 配套与根级 79
  patterns 849  = 迁入 846（六类目录 349 + mp 合并 496 + docker-template 1）+ 丢弃 3
  reports  1704 = 迁入 1670（21 目录 1665 + 5 回补）+ 丢弃 34
  配套/根级 79  = 迁入 78（配套目录 57 + reports 根 20 + mp 1）+ 丢弃 1
  → retrospective 迁入 2594 + 丢弃 38 = 2632 ✓

非 retrospective 66 = 迁入 63 + 丢弃 3（根 README、architecture/README、task-summaries/README）✓

总计：迁入 2657 + 丢弃 41 = 2698 ✓
（预检实测：整目录平移 2107 + thesis 6 + 逐文件 544 = 2657；git 实测 R=2657 / D=41）
```

.meta 镜像（Task 3 已执行实测）：1718 TOML = 迁入 1714（随 md 同构 1712 + 2 个历史孤立 TOML 同构平移）+ 丢弃 4（41 个丢弃 md 中仅 4 个有镜像 TOML）；目标镜像 1076 + 1714 = 2790。x-toml-ref 改写 1783 行；改写后 2329 引用解析正常，1044 个悬空引用经 HEAD 树核验为**迁移前既有缺口**（knowledge 953 / retrospective 91，镜像从未覆盖），登记 backlog，非本次回归。

---

## 6. 落位恰当性自评（TR-1.4，rubric 1-5）

**自评：5 分。**

- 全部目录级落位与 OKF v0.2 六板块语义一致：复盘体系（patterns/reports/templates/plans/配套资产）入 `retrospective/`；项目技术资产（code-wiki、standards、test-plans、工具/质量指南、架构概念、13 个项目文档）入 `tech/`；方法论分析与泛化复用入 `topics/`；superpowers 独立成板块；模板入 `templates/`；Sphinx 静态资产入 `_static/`。
- 与工具内建信号逐项对齐：generate-readme `get_p1_dirs` 七个硬编码预期路径（superpowers/plans、superpowers/specs、retrospective/assets、retrospective/templates、reports/insight-extraction、reports/standards-tools、patterns/methodology-patterns）全部为迁入目标；LINK_CHECK_EXCLUDE_DIRS 含 `docs/templates`；PREFIX_RULES 覆盖 retrospective/tech/topics 主路径（superpowers/templates 新路径 Task 4 扩展）。
- 目标侧碰撞已实测：绝大多数落位目录 absent（新建零碰撞）；三个合并点（mp 23 文件、reports/concepts 40 文件、reports 根 index/log）均有显式冲突处置规则。
- 去重 39 文件逐项登记理由，5 个旧独有文件经全树搜索确认回补，无未声明的内容丢失。

## 7. Task 2 执行备注

- 九批次顺序按 tasks.md Task 2（①patterns 六类+mp 合并+docker-template → ②reports 21 目录+5 回补 → ③retro 配套目录与根级文件 → ④superpowers → ⑤templates → ⑥tech 落位 → ⑦topics 2 文档 → ⑧plans/task-summaries → ⑨thesis 入 _static）。
- 每批次 git mv 前运行碰撞预检（目标已存在且不在 §1 合并清单内即报错中止）；迁移后 `.agents/docs/` 空目录移除。
- 非 md 资产（.cc/.hpp/.py/.html/.json/.txt/.png/.ttf/.js/.gitkeep/.gitignore）随原目录批次迁移，不单独处理。
