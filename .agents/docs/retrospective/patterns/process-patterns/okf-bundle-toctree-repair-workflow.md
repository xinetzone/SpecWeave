---
id: "okf-bundle-toctree-repair-workflow"
title: "OKF bundle 目录树完整性修复工作流"
type: process-pattern
date: 2026-08-24
maturity: L1-draft
maturity_note: "单案例验证（awesome-okf-xs 4888 警告清零、867 文件修复），待二次验证"
source: "../../reports/documentation-governance/retrospective-sphinx-toctree-clear-20260824/README.md#3-e-萃取g3-通过模式可迁移"
related_patterns:
  - "pdf-book-to-okf-wiki.md"
  - "../methodology-patterns/document-architecture/content-entry-index-trinity.md"
  - "../methodology-patterns/tools-automation/toctree-dynamic-verification.md"
tags: ["toctree", "sphinx", "myst", "okf", "knowledge-base", "navigation-tree", "content-completeness"]
validation_count: 1
reuse_count: 0
---

# OKF bundle 目录树完整性修复工作流

## 触发场景

- 当基于 Sphinx + MyST-Parser 的知识库/文档集出现大量 `toc.not_included` 警告（文档未加入任何目录树）时
- 当**任意**目录树驱动的内容组织（本案例为 OKF bundle——一类按主题组织的文档集合）目录缺 `index.md`、或已有 `index.md` 但缺 `{toctree}`、或已有 `{toctree}` 但缺目录条目时

> **术语说明**：`toctree` 是 Sphinx/MyST 的目录树指令（MyST 语法为 ` ```{toctree} ` 代码围栏块）；OKF bundle 是本文档工程的按主题文档集合单元。"游离闭合标记"指 toctree 代码围栏的闭合 ` ``` ` 被破坏。

**识别信号**：
- 构建日志中 `toc.not_included` 警告数达到**百/千级**（本案例初始 4888 个）——低于百级警告建议先人工/局部处理，不值得走全流程脚本
- 扫描发现大量 `index.md` 不含 `{toctree}`（本案例 907 个 `index.md` 仅 34 个含 `{toctree}`，约 96% 缺失）
- 部分子目录无 `index.md`，子文档"游离"无法导航

## 不适用场景（反目标用户/场景）

- **只修内容质量问题的团队**：目标是处理 `myst.header`/`myst.topmatter` 等内容告警——本模式只修目录树完整性，对内容质量问题不适用
- **单目录/无层级文档集**：无目录树结构、无 toctree 导航需求，本模式不适用
- **首次搭建的新文档集**：内容尚未积累，应走"生成即带 toctree"的规范约束（A-1）预防源头问题，而非事后批量修复——对零存量问题场景不适用
- **精心人工编排导航的站点**：目录树即首页精选链接等人工编排艺术，自动化批量追加不适合，可能破坏设计

## 问题背景

知识库/文档集采用"目录即导航"的组织方式（Sphinx toctree / MyST `{toctree}`）时，内容生产与目录树维护脱节会导致系统性结构缺陷：

1. **bundle 生成未带目录树**：批量生成 `index.md` 时未同时写入 `{toctree}`，导致文档"有内容但导航不到"（I-1）。
2. **顶层元数据文档游离**：父索引 toctree 与目录文件清单不同步，`log`/`spec` 等条目人工维护易漏（I-2）。
3. **批量脚本覆盖边界不全**：全量脚本不处理"无 index 目录"与"已含 toctree 缺条目"两类边界，首次运行后需二次定向补漏（I-4）。
4. **盲目字符串拼接破坏已有结构**：追加 toctree 条目时未定位闭合标记，破坏 4 个已有 toctree 文件的格式（游离 ``` 闭合标记）（I-5）。

本模式通过"全量扫描分类 → 三类处理（建索引/追加/补充）→ 精确追加定位闭合 → dry-run 验证 → git 兜底回滚"系统性修复目录树完整性。

## 核心步骤（5步）

1. **全量扫描分类**：扫描所有 bundle 目录，将问题归类为三类——
   - 类A：目录含子文档但无 `index.md` → **建索引**（新建 index.md）
   - 类B：有 `index.md` 但无 `{toctree}` → **追加**（生成 toctree 并引子目录）
   - 类C：已有 `{toctree}` 但缺 `log`/`spec` 等条目 → **补充**（在 toctree 内追加条目）
2. **三分类批量处理**：按类别分别处理。类A 需同时处理"目录含子目录即强制生成 index.md"；类C 需按目录文件清单补齐条目。
3. **精确追加定位闭合**：对已有 toctree 的文件，追加条目前先定位 toctree 块闭合标记（`` ``` ``），在闭合前插入条目——**禁止**盲目在文件末尾/随意位置拼接（R-12 教训：游离闭合标记破坏 4 文件）。
4. **dry-run 验证排序**：脚本先 dry-run 输出预期变更（正确排序：CER 子目录前、meta 后、辅助文件最后），人工核对后再实际执行（R-9）。
5. **git 兜底回滚**：批量修改前确认在版本控制下；执行后如发现格式损坏（如游离 ```），用 git 恢复后改为更精确的追加逻辑重试（R-12）。

> **验证闭环**：修复后运行 dummy 构建确认 `toc.not_included` 归零（本案例 4888 → 0），并运行 CI 门禁 `check-toctrees.py`（含断链 + 可达性 + 目录文件清单一致性）二次确认（R-10/R-15）。

## 反模式（不要这么做）

- ❌ **AP-1 盲目拼接**：追加 toctree 条目时不定位闭合标记，直接在文件末尾或字符串拼接处插入 → 破坏已有 toctree 格式（游离 ```），本案例损坏 4 文件需 git 回滚 → **正确做法**：追加前定位 toctree 块闭合位置，在闭合前插入条目。
- ❌ **AP-2 一次性脚本不覆盖边界**：只写"给所有 index.md 加 toctree"的全量脚本，不处理"无 index 目录"（类A）与"已含 toctree 缺条目"（类C）两类边界 → 首次运行后需二次定向补漏 → **正确做法**：脚本须覆盖建索引、追加、补充三类场景。
- ❌ **AP-3 只建索引不建 toctree**：生成 index.md 但不同时写入 `{toctree}` → 文档仍游离，构建继续告警（96% 缺失的根因）→ **正确做法**：生成规范要求"index.md 必须带 toctree"（A-1 行动项）。
- ❌ **AP-4 无 git 兜底就批量落地**：跳过 dry-run 与 dummy 构建验证，直接对数百文件写入，且无版本控制回滚预案 → 一旦追加逻辑破坏已有结构（本案例损坏 4 个已有 toctree 文件的闭合标记），只能靠 git 恢复止损，若无兜底则损坏永久丢失 → **正确做法**：dry-run 先行 + dummy 构建 `toc.not_included=0` 验证 + 确认在版本控制下执行并预留 git 回滚。

## 失败案例

- **案例1（游离闭合标记破坏 4 文件）**：一次性追加脚本在 4 个已有 toctree 的 index.md 末尾追加条目，未定位 toctree 块闭合标记（`` ``` ``），导致闭合标记游离、格式损坏；依赖 git 回滚后改为"定位闭合位置再插入"的精确追加逻辑才成功（R-12）。**失败根因**：假设"文件末尾追加即安全"，忽略 toctree 是需闭合的结构化块。
- **案例2（全量脚本漏覆盖边界）**：首轮全量脚本只给"已有 index.md 的目录"补 toctree，漏掉"无 index 目录"（类A）与"已含 toctree 缺条目"（类C）两类边界，首次运行后需二次定向补漏（I-4）。**失败根因**：以"覆盖面越大越好"代替"按问题类型分桶处理"。

## 检验标准

- [ ] dummy 构建 `toc.not_included` 警告为 0（本案例 4888 → 0）
- [ ] 目录含子文档的 bundle 均有 index.md（无"游离子文档"）
- [ ] 已有 toctree 文件经一致性检查无缺失条目（`check_consistency` 真实树零缺失）
- [ ] 修改文件数与 git 变更记录一致（本案例 867 files changed, 9209 insertions）
- [ ] 已有 toctree 文件格式无损坏（无游离 ``` 闭合标记）

## 迁移示例

- **场景1（其他静态站点生成器）**：Hugo/VuePress/Jekyll 站点的导航清单（menus/nav 配置）与目录文件清单同步修复——批量补导航条目时同样需"定位结构闭合 + dry-run + git 回滚"。
- **场景2（API 文档工程）**：OpenAPI/代码注释自动生成 API 文档后，批量补充"目录索引缺失"条目——三类分类（建索引/追加/补充）与"精确追加定位闭合"逻辑直接复用。
- **场景3（软件包目录）**：仓库 README 目录索引与子目录清单一致性修复——`index.md`+toctree 可类比为"根 README 的目录链接清单"。

## 与其他模式的关系

| 关联模式 | 关系类型 | 关系说明 |
|---------|---------|---------|
| [pdf-book-to-okf-wiki.md](pdf-book-to-okf-wiki.md) | 互补 | 该模式讲"如何从 PDF 生成 OKF 文档"，本模式讲"如何修复已生成文档的目录树完整性"；其"确定性校验修复"步骤与本模式验证闭环一致 |
| [content-entry-index-trinity.md](../methodology-patterns/document-architecture/content-entry-index-trinity.md) | 理论补充 | 该模式讲"内容-入口-索引三位一体"的结构原则，本模式给出目录树完整性修复的具体工作流 |
| [toctree-dynamic-verification.md](../methodology-patterns/tools-automation/toctree-dynamic-verification.md) | 配套验证 | 本模式负责"修复"，该模式负责"验证"，二者构成修复+门禁闭环 |
| [spec-as-code-automated-gates.md](../methodology-patterns/tools-automation/spec-as-code-automated-gates.md) | 支撑 | 目录树完整性约束应写成自动化门禁脚本（A-2 已并入 check-toctrees.py），而非仅靠人自觉 |

## 验证状态

- ✅ 本次任务验证：awesome-okf-xs 4888 个 `toc.not_included` 警告清零，867 文件变更，2 个原子提交
- ⚠️ 待推广：需在第二类文档集（其他 Sphinx/知识库项目）上二次验证后升级 L2
- 🔲 关联行动项 A-1：OKF bundle 生成规范纳入"必须生成 index.md 并带 toctree"约束（防源头）

## 关联资源

- 来源复盘：[awesome-okf-xs Sphinx toctree 警告清零里程碑复盘](../../reports/documentation-governance/retrospective-sphinx-toctree-clear-20260824/README.md)
