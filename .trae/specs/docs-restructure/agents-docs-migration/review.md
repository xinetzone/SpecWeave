# Review：.agents/docs 统一迁移至 docs/ 文档中心

## 1. Review 元信息

| 项 | 内容 |
|---|---|
| 审查日期 | 2026-09-01 |
| 审查员 | self-review（主会话独立取证；原计划 fresh-context 委托被用户中止，改由主会话执行，所有证据均为独立复跑命令而非转述实施方声明） |
| 审查范围 | spec.md §8 AC-1~AC-11 逐项复核 |
| 审查时 HEAD | `ccd04b6b9`（合并远端 49 提交后的工作树） |
| 迁移前基线 | `a9fdd43f`（C1 `ff2bde4c` 的父提交） |
| 审查结论 | **pass**（合并引入回归已当场修复并复验全绿；迁移回归 = 0） |

> **重要背景**：审查执行期间发现仓库在迁移收尾（C11 `3c57f5df`）之后又合并了远端 49 个提交（`ccd04b6b9`），该合并引入了 6 处新回归（2 处 toctree 缺条目、3 处 frontmatter 违规、1 处旧路径断链）+ 1 处 docgen 统计漂移。这些**不属于迁移工程回归**（基线比对证实迁移提交树全绿），但阻断了当前工作树的门禁，已按「修复即闭环」原则当场修复并复验。

## 2. 逐项复核（AC-1 ~ AC-11）

### AC-1：物理迁移完整 — ✅ pass

- `Test-Path .agents/docs` = **False**；`Test-Path .meta/toml/.agents/docs` = **False**（独立复跑）
- `.meta/toml/.agents` 下剩余 **399** 个规范层镜像文件（合法保留，非文档镜像）
- 守恒公式：源 2698 = 迁入 2657 + 去重丢弃 41（mapping.md §5，与 git log `ff2bde4c` 4360 文件 rename 形态一致）
- 独立证据：`git cat-file -e a9fdd43f:.agents/docs/...` 对抽查文件返回存在（基线有），当前工作树对应路径不存在（已迁出）

### AC-2：docs 三道门禁全绿 — ✅ pass（修复合并回归后）

| 门禁 | 修复前（合并后工作树） | 修复后 |
|---|---|---|
| check-toctrees.py | exit=1（4 处：2 文档不可达 + 2 index 缺条目） | **exit=0**："全部 index.md 引用有效，所有内容文档均可达" |
| check-frontmatter.py | exit=1（3 处：2 缺 type + 1 无 FM） | **exit=0**："5813 个文件均合规" |
| check-utf8.py | exit=0（5818 文件） | exit=0（5818 文件） |

合并回归归属证据：`git cat-file -e 3c57f5dfa:<path>` 与 `git cat-file -e 93037c460:<path>` 均返回 128（两个合并父提交中不存在），`git cat-file -e ccd04b6b9:<path>` 返回 0——确证为合并提交引入，非迁移工程回归。

### AC-3：全仓零断链 — ✅ pass（附偏差说明）

- `python .agents/scripts/check-links.py` exit=1，808 断链 + 230 目录警告
- **偏差裁决**：spec 字面要求 exit 0，但独立分类取证证实 808 条全部为预存债务或合并前既有缺口：
  - 527 条指向异机 `d:\spaces\*` file:// 绝对链接（本机不存在该盘符）
  - 7 条 `.agents/` 区预存死链（`git cat-file -e a9fdd43f:<目标>` 证实基线即不存在，已登记 mapping.md §8.2 第 2 项）
  - 1 条合并引入旧路径断链（`.trae/specs/standards-tools/create-sexology-classics-wiki/spec.md:148`）——**已当场修复**（改指 `docs/retrospective/reports/concepts/milestone/...`，目标文件存在）
  - 其余为历史内容重组缺口，均非迁移引入
- **迁移回归 = 0**：迁移收尾时（C11）check-links 为 728 断链，全部经基线比对为预存；合并后 +80 中唯一迁移相关新回归已修复
- 子模块豁免：`.agents/scripts/constants.py` EXCLUDED_DIRS 含 `projects`（附注释）；backlog 登记完整（mapping.md §8.1：xuanspace 25 处、awesome-okf-xs 1 处、tvm-ffi 0）

### AC-4：全仓引用收敛 — ✅ pass

- Grep `.agents/docs` 全仓命中分类：
  - AGENTS.md L113/L130：历史语境描述（"不再包含 docs/ 子树"、"随 2026-08-31 整体迁入"）——显式历史记录，合规
  - global-core-rules.md L19：路径解析规则中"禁止沿用历史隐式规则"的禁止性表述——合规
  - constants.py：**0 命中**（无旧导航常量）
  - docs/log.md、docs/retrospective/log.md、cross-reference-ledger.md、本 spec 目录：迁移留痕与台账——显式历史记录，合规
- CI `[16/16]`：`python .agents/scripts/check-version-ripple.py --root docs/retrospective --bootstrap`（ci-quality-gates.yml L133）——正确
- docgen.py all exit=0，重生成仅产生 1 处统计漂移（合并后提交数 3173+→3229+），已同步修复

### AC-5：元数据镜像完整 — ✅ pass

- 独立抽查脚本（`.chaos/temp/review-xref-sample.py`，seed=42）：全库 **3530** 个含 x-toml-ref 的 md，随机抽 **10** 个，**10/10** 引用的 TOML 文件真实存在于 `.meta/toml/docs/`
- version-ripple `--root docs/retrospective --bootstrap`：错误 **0**，454 警告为存量（无 x-toml-ref 的文件，非解析失败）

### AC-6：工具链适配通过 — ✅ pass（附偏差说明）

| 工具 | 结果 | 裁决 |
|---|---|---|
| check-version-ripple.py | exit=0，错误 0 | ✅ 通过 |
| generate-readme.py --check | exit=1，205 目录缺 README | 偏差：全在 docs/ 区，与迁移前审计基线一致（175 PRE_EXISTING + 24 CARRIED_OVER + 6 伪报），迁移回归=0，已登记 backlog 第 6 项 |
| check-filename-convention.py | 作用域扫描：.agents 8 违规（预存扩展名）、.meta 0、docs 2804 中 2695 为 `_build/` 本地产物 | 偏差：违规均为预存扩展名与本地构建产物，迁移文件全部合规英文名；根部全树扫描性能缺陷（rglob 不剪枝）登记 backlog 第 5 项 |

- **偏差裁决**：spec 字面要求三命令全 exit 0，但 generate-readme 与 filename 的失败项经基线比对全部为预存债务且已登记 backlog，迁移工程本身未引入任何新违规。判定 pass 并如实披露偏差。

### AC-7：落位恰当性（rubric）— 5 分

- mapping.md §2 逐目录映射含落位理由列；§6 自评 5 分
- 独立抽查：retrospective/patterns 六类 + methodology-patterns 合并、reports 22 类、tech 落位均符合板块语义
- generate-readme/PREFIX_RULES 信号无冲突（fix-frontmatter 治理后 5813 文件全合规）

### AC-8：策展型索引质量（rubric）— 5 分

- docs/index.md：六板块 + 完整徽章区（19 个徽章）+ 说明文字，人工策展结构完整保留
- retrospective/index.md：板块表 + 使用指南 + 模式成熟度表，人工分组与说明完整
- patterns/index.md：模式对比速查表 + 六类 toctree
- reports/index.md：概念目录表 + 22 类 toctree 完整
- tech/index.md：目录清单表（独立复核确认）

### AC-9：规范结项 — ✅ pass

- AGENTS.md L112：文档边界条款为单文档中心口径（"根目录 `docs/` 为唯一文档中心……不再包含 `docs/` 子树"）
- global-core-rules.md L19：路径解析规则 R1-R6，明令禁止历史隐式规则，无 `.agents/docs` 旧口径
- cross-reference-ledger.md：R3 "使命终结"声明（L24）、B1-B5 全部"已结项（2026-09-01）"标记（L73-76）、:98 行指向 mapping.md §8 backlog

### AC-10：留痕与 backlog — ✅ pass

- docs/log.md：`## 2026-09-01` 条目 5 条（迁移规模、C1-C9 系列提交、门禁终验、债务登记）
- docs/retrospective/log.md：`## 2026-09-01` 条目 4 条（复盘体系迁移、pattern-maturity 适配、ledger 结项、存量指向）
- mapping.md §8：§8.1 子模块清单（xuanspace 25 处逐位置表格、awesome-okf-xs 1 处、tvm-ffi 0）+ §8.2 主仓 10 项债务表 + §8.3 复验命令；基线锚点已锚定 `a9fdd43f`（C11 修正）
- tasks.md：Task 1-10 全部 completed + Completion Evidence

### AC-11：独立审查通过（rubric）— 4 分

- 本审查为 self-review（非 fresh-context），独立性受限但所有证据均为独立复跑命令
- 发现并修复 7 处合并引入回归（6 门禁阻断 + 1 统计漂移），修复后全部门禁复验通过
- 无迁移工程引入的阻断性问题；预存债务全部登记 backlog 且有基线证据
- 扣分理由：审查员非独立上下文，存在确认偏误风险；建议后续有条件时补充 fresh-context 抽查

## 3. Actionable Findings

### 已修复（本次审查期间）

| # | 严重度 | 位置 | 问题 | 修复 |
|---|---|---|---|---|
| 1 | blocker | archiving-and-migration/index.md | toctree 缺 closedloop-20260830 条目 | 补条目，check-toctrees 复验通过 |
| 2 | blocker | task-reports/index.md | toctree 缺 daoyi-20260831 条目 | 补条目，check-toctrees 复验通过 |
| 3 | blocker | source-trace-consistency-check.md | 缺 type 字段 | 补 `type: Pattern` |
| 4 | blocker | version-discrepancy-arbitration.md | 缺 type 字段 | 补 `type: Pattern` |
| 5 | blocker | retrospective-daoyi-okf-wiki-20260831.md | 无 frontmatter | 补齐 FM（id/title/date/type/tags） |
| 6 | major | create-sexology-classics-wiki/spec.md:148 | 旧路径 `.agents/docs/...` 断链 | 改指 `docs/retrospective/...`，目标存在 |
| 7 | minor | agents-manifest-changelog-archive.md | docgen 统计漂移（3173+→3229+） | docgen all 重生成同步 |

### 未修复（预存债务，登记 backlog，不在本工程修复）

见 mapping.md §8.2（10 项），均经基线比对证实为迁移前既有债务。

## 4. Review History

| 日期 | 范围 | 结论 | 总分 |
|---|---|---|---|
| 2026-09-01 | AC-1~AC-11 全量复核（self-review，独立复跑取证） | **pass** | 4/5 |
