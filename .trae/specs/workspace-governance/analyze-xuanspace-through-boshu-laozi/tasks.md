---
status: "draft"
title: "从帛书《老子》视角分析 Xuanspace 并产出项目蓝图与优化建议书 - 实施计划"
change-id: "analyze-xuanspace-through-boshu-laozi"
---

# 从帛书《老子》视角分析 Xuanspace（玄境）并产出项目蓝图与优化建议书 - 实施计划

> 对应规格：[spec.md](spec.md)
> 落盘目录：`projects/xuanspace/doc/`
> 纪律红线：不改代码；不提交/推送；不写 `projects/xuanspace/doc` 之外路径；不写 `projects/awesome-okf-xs`。

- [x] Task 1: 事实采集与信源核验（R 阶段）
  - **Priority**: high
  - **Depends On**: None
  - **Description**: 建立事实底稿，冻结分析基准；复核阶段约束是否仍有效。
  - [x] SubTask 1.1: 记录基线事实——`projects/xuanspace` 的 HEAD（`git rev-parse HEAD`）与工作树状态（`git status --short`），作为全篇引用与收尾比对的锚点
  - [x] SubTask 1.2: 只读通读帛书老子知识底座的必要正文——`laozi/boshu-reading/`（`01-four-systems.md`、`02-de-before-dao.md`、`04-key-variants.md`、`07-core-concepts-interpretation.md`）、`laozi/dao-san-triads/`（`concepts/01~04`、`examples/`）、`laozi/laozi-lineage/`（版本谱系与禁忌字断代）
  - [x] SubTask 1.3: 采集 xuanspace 现状事实——根 `AGENTS.md`、`README.md`、`CONTRIBUTING.md`、`pyproject.toml`、`CMakePresets.json`、`.gitmodules`、`.github/workflows/{ci,release}.yml`、`.agents/rules/frontmatter.md`、`.meta/`、`apps/`、`libs/`、`tools/{xs,okf,templates}`、`scripts/`、`src/xuanspace/`、`tests/`、`vendor/` 的目录与关键文件
  - [x] SubTask 1.4: 核验三条声明一致性线索——`doc/README.md` 的 `docs/` vs `doc/`；`README.md` 称 `xs`「15 个子命令」vs `tools/xs/src/xs/commands/` 实际命令模块数；`doc/README.md` 目录树 vs 实际 `doc/` 结构
  - [x] SubTask 1.5: 核验 C-3 阶段约束——确认 `projects/xuanspace/.agents/rules/frontmatter.md` 中「Task 20 之前」的表述是否仍然有效（若已失效，回到 spec.md 更新 FR-11）
  - [x] SubTask 1.6: 产出事实清单（**≥25 条**），每条含来源引用（相对路径，关键处到行号）；**严禁出现因果推断词**（因为/导致/因此/所以/使得/从而）
  - **Acceptance Criteria Addressed**: AC-4, AC-6
  - **Test Requirements**:
    - `rule` TR-1.1: 事实清单条数 ≥25，且每条均带相对路径引用；对清单做因果词检索命中 0 次
- [x] Task 2: 洞察萃取（I 阶段）
  - **Priority**: high
  - **Depends On**: Task 1
  - **Description**: 从事实中提炼洞察四元组。
  - [x] SubTask 2.1: 提炼 **≥3 条**洞察，每条为完整四元组（陈述 + 证据 + 反常识 + 行动）
  - [x] SubTask 2.2: 校验维度互不重叠，且 **≥2 条挑战默认假设**
  - [x] SubTask 2.3: 对每条「反常识点」回查是否有事实支撑；无支撑者删除
  - **Acceptance Criteria Addressed**: AC-10
  - **Test Requirements**:
    - `rule` TR-2.1: 洞察 ≥3 条且四元组完整；反常识条目数 ≥2
    - `rubric` TR-2.2: 洞察质量与反常识性；scale 1-5；anchors 1/3/5 见 AC-10；threshold >= 4；evidence = 洞察清单 + 逐条证据对照
- [x] Task 3: 第一性原理与「三之位」诊断（F 阶段 + `dao-san-triads`）
  - **Priority**: high
  - **Depends On**: Task 1
  - **Description**: 从本质约束推导 xuanspace 的结构性张力，并用「三之位」框架定位关系位。
  - [x] SubTask 3.1: 写出第一性原理假设（每条含「若不成立会怎样 / 检验方式」）与公理
  - [x] SubTask 3.2: 执行「三之位」五步——命名二 → 找关系位 → 检验非实体性 → 表述为关系 → 落地动作
  - [x] SubTask 3.3: 显式命名并规避 ≥1 个反模式（把第三项当实体／跳过二直接谈三／停在二无限细分／用第三项回避选择／把结构类比当史实来源）
  - [x] SubTask 3.4: 完成「三问检验」自查并记录结果
  - **Acceptance Criteria Addressed**: AC-11
  - **Test Requirements**:
    - `rule` TR-3.1: 五步与三问检验均可逐项指出；被规避的反模式被明确点名
- [x] Task 4: 撰写《项目蓝图》
  - **Priority**: high
  - **Depends On**: Task 2, Task 3
  - **Description**: 落盘蓝图文档到 `projects/xuanspace/doc/`。
  - [x] SubTask 4.1: 组织章节——项目定位 → 「道—法—术—器」四层解构 → 现状能力地图 → 「三之位」诊断 → 目标态蓝图 → 演进路线（另附事实底稿与洞察）
  - [x] SubTask 4.2: 四层解构逐层给出「对应实体（带引用） + 承载功能 + 薄弱环节」，每层标注「结构类比，非影响关系」
  - [x] SubTask 4.3: 《老子》引文逐处标注版本（甲本/乙本/今本/郭店楚简本），甲本损掩处标注
  - [x] SubTask 4.4: 以 H1 开头，**不添加 YAML frontmatter**，**不创建 `.meta/toml/`**
  - [x] SubTask 4.5: 如含 Mermaid，一律按安全编码规则书写
  - **Acceptance Criteria Addressed**: AC-1, AC-3, AC-8, AC-11
  - **Test Requirements**:
    - `rule` TR-4.1: 文件存在于 `projects/xuanspace/doc/`；无 YAML frontmatter；无新增 `.meta/toml/`
    - `rule` TR-4.2: 引文版本标注完整，无笼统「帛书本」表述
    - `rubric` TR-4.3: 「道—法—术—器」解构深度；scale 1-5；anchors 1/3/5 见 AC-8；threshold >= 4；evidence = 该章节内容与对照引用
- [x] Task 5: 撰写《优化建议书》
  - **Priority**: high
  - **Depends On**: Task 3
  - **Description**: 落盘建议书文档到 `projects/xuanspace/doc/`。
  - [x] SubTask 5.1: 按 P0/P1/P2 分级组织建议清单
  - [x] SubTask 5.2: 每条建议补齐五要素：判据 + 现状证据（相对路径 `#L起-L止`）+ 期望态 + 落地动作 + 验证方式
  - [x] SubTask 5.3: 逐条剔除「正确的废话」；保证每条可判定为「已做/未做」
  - [x] SubTask 5.4: 给出优先级依据与整体汇总
  - [x] SubTask 5.5: 以 H1 开头，**不添加 YAML frontmatter**
  - **Acceptance Criteria Addressed**: AC-1, AC-3, AC-5, AC-9
  - **Test Requirements**:
    - `rule` TR-5.1: 每条建议五要素齐备率 100%
    - `rubric` TR-5.2: 建议可执行性与判据强度；scale 1-5；anchors 1/3/5 见 AC-9；threshold >= 4；evidence = 建议清单 + 判据/验证方式抽查
- [x] Task 6: toctree 登记与文档门禁
  - **Priority**: high
  - **Depends On**: Task 4, Task 5
  - **Description**: 让两份文档进入站内导航并通过构建、链接与图表门禁。
  - [x] SubTask 6.1: 在 `projects/xuanspace/doc/index.md` 新增「规划」toctree 分组，登记两份文档；不破坏现有四个 toctree
  - [x] SubTask 6.2: 运行 Sphinx HTML 构建，确认成功且新增文档无 orphan/未收录告警
  - [x] SubTask 6.3: 运行 `check-links.py`（对新增/修改文件），确认 0 断链
  - [x] SubTask 6.4: 运行 `check_mermaid.py`（若含 Mermaid），确认通过
  - **Acceptance Criteria Addressed**: AC-2, AC-7
  - **Test Requirements**:
    - `rule` TR-6.1: 构建成功；无指向新增文档的 warning
    - `rule` TR-6.2: `check-links.py` 对新增/修改文件 0 断链；`check_mermaid.py` 通过
- [x] Task 7: 边界核对与收尾
  - **Priority**: medium
  - **Depends On**: Task 6
  - **Description**: 确认无越界写入、无 git 副作用，并留存证据。
  - [x] SubTask 7.1: 在 `projects/xuanspace` 执行 `git status` 与 `git log -1`，确认变更仅限 `doc/`（两份新文档 + `index.md`）、HEAD 与 Task 1 记录一致
  - [x] SubTask 7.2: 确认 `projects/awesome-okf-xs` 零变更
  - [x] SubTask 7.3: 确认未执行任何 commit / push / tag，未清理或回滚任何既有改动
    - **断言范围**：本条仅覆盖**本规格任务的实施过程**（Task 1–7）。规格完成后，用户另行授权落地《优化建议书》P0-1，由此产生的提交见文末「后续任务：P0-1 落地」——该追加不改写本条原始验收记录。
  - [x] SubTask 7.4: 保留 `doc/_build/` 产物若已生成——按需清理或保留（不得删除他人已有产物）
  - **Acceptance Criteria Addressed**: AC-6
  - **Test Requirements**:
    - `rule` TR-7.1: 两仓 `git status` 输出符合 AC-6 范围；`git log -1` 与基线 HEAD 一致

# Task Dependencies

- Task 2 依赖 Task 1
- Task 3 依赖 Task 1
- Task 4 依赖 Task 2、Task 3
- Task 5 依赖 Task 3
- Task 6 依赖 Task 4、Task 5
- Task 7 依赖 Task 6

# 并行建议

- Task 2 与 Task 3 在 Task 1 完成后可并行推进
- Task 4 与 Task 5 在各自前置满足后可并行推进（两者写入不同文件，无共享状态）

# 后续任务：P0-1 落地（规格完成后追加）

> 本节记录**规格完成后**、经用户另行授权执行的《优化建议书》P0-1 落地及其提交。它不改写 Task 1–7 的原始验收记录；Task 7.3 关于 commit 的断言以本规格任务的实施过程为范围（见该条「断言范围」注）。

- [x] Task 8: 落地 P0-1（统一根文档目录命名口径为 `doc/`）
  - **Priority**: high
  - **Depends On**: Task 7
  - **Description**: 依《优化建议书》P0-1，以磁盘目录名 `doc/` 为唯一命名事实，消除 CLI 名、脚手架生成目录与文档/CI 示例的口径分裂，并收口模块命名约定。
  - [x] SubTask 8.1: CLI 子命令 `xs docs` → `xs doc`（按裁定不保留别名）；`xs init` 脚手架生成目录 `docs/` → `doc/`（含模板文本）；文档与 CI 示例同步，共 16 文件
  - [x] SubTask 8.2: 模块 `commands/docs_cmd.py` → `commands/doc_cmd.py`；公开函数统一 `doc_*` 前缀（`doc_build`／`doc_serve`／`doc_clean`／`doc_linkcheck`）；`cli.py` 导入与 Typer 别名同步为 `doc_app`
  - [x] SubTask 8.3: `doc/recommendations.md` 的排除项分类（`CHANGELOG.md#L12` 由「语义不同」移入「历史记录与归档」）、路径引用与验证白名单同步
  - [x] SubTask 8.4: `CHANGELOG.md` 补记 `Unreleased` 段（两项 BREAKING + 模块重命名），v0.1.0 历史发布记录不改写
  - [x] SubTask 8.5: 根仓推进 `projects/xuanspace` 子模块指针
  - **Acceptance Criteria Addressed**: AC-6（范围仅限 `projects/xuanspace` 内的具名文件与 `CHANGELOG.md`）
  - **Test Requirements**:
    - `rule` TR-8.1: CLI 注册表 groups 含 `doc` 且不含 `docs`；`xs doc --help` exit=0 且 build/serve/clean/linkcheck 四子命令齐备
    - `rule` TR-8.2: `docs_cmd|docs_app|docs_build|docs_serve|docs_clean|docs_linkcheck` 全仓检索命中 0
    - `rule` TR-8.3: `pytest tests` 无新增失败（现存 1 项 `test_check_python_version` 为环境性——本机 Python 3.14.3 < 仓库要求 3.14.6，改动前即失败）
    - `rule` TR-8.4: 根仓 `git ls-tree HEAD projects/xuanspace` 的 gitlink 等于子模块 HEAD

## 提交记录（证据）

| 仓库 | 提交 | 说明 |
|---|---|---|
| `projects/xuanspace` | `207256c` | `refactor(xs): 重命名 docs 子命令为 doc 并对齐仓库目录约定`（16 文件，BREAKING） |
| `projects/xuanspace` | `aed2e5b` | `refactor(xs): 重命名 docs_cmd 模块为 doc_cmd 并统一函数名前缀`（3 文件，rename 94%） |
| `projects/xuanspace` | `cc5c5b1` | `docs(changelog): 补记 xs doc 改名的破坏性变更`（1 文件） |
| 根仓 | `b86f2a98e` | `chore(submodule): 更新 xuanspace 子模块指针至 cc5c5b1`（仅 gitlink，+1/−1） |

> 未 push、未 tag。根仓存在并行会话的在途暂存改动（`docs/retrospective/patterns/methodology-patterns/governance-strategy/` 9 项），本次 gitlink 提交按 path 级钉死，未卷入其中。

# 后续任务：P0-1 主体 + P0-2/P0-3 落地（规格完成后追加，第二轮授权）

> 本节记录规格完成后**第二轮**经用户另行授权执行的《优化建议书》落地：P0-1 主体的文档级 7 处引用 + P0-2（`apps/` 与 `apps/xs-cli/` 失实声明）+ P0-3（上游子模块数 3→4）。不改写 Task 1–8 的原始记录。

- [x] Task 9: 落地 P0-1 主体（文档级 7 处 `docs/` → `doc/`）
  - **Priority**: high
  - **Depends On**: Task 8
  - **Description**: Task 8 已收口 CLI 名与脚手架生成目录；本轮补齐**文档层**残余 7 处 `docs/` 引用，使根文档目录命名口径在文档层一致。
  - [x] SubTask 9.1: 修正 6 文件 7 处——`AGENTS.md#L66`、`.agents/ONBOARDING.md#L103`、`CHANGELOG.md#L20`、`doc/architecture.md#L71`、`doc/dependency-report.md#L28`、`CONTRIBUTING.md#L709` 与 §12.1 目录树首行（L714）
  - [x] SubTask 9.2: 以白名单 `rg --hidden` 复核——剩余 8 行**全部**落入既有排除项（`doc_cmd.py` / `doctor_cmd.py` 兼容实现、`CONTRIBUTING.md#L316` 分支命名 `docs/<name>`、`CHANGELOG.md#L12/19` 历史记录、`tests/test_doctor_sphinx.py#L19` 兼容注释）
  - **Acceptance Criteria Addressed**: AC-6
  - **Test Requirements**:
    - `rule` TR-9.1: 白名单 `rg` 扫描下 P0-1 目标 7 处零命中
- [x] Task 10: 落地 P0-2（`apps/` 与 `apps/xs-cli/` 失实声明）
  - **Priority**: high
  - **Depends On**: Task 9
  - **Description**: 磁盘事实为 `apps/` 仅含 `.gitkeep` 与 `README.md`（无应用），但 `doc/architecture.md`、`apps/README.md`、`tools/README.md` 仍以「现有子项目」口径描述 `xs-cli/`、`zhujian-wudao/`。按《优化建议书》P0-2 期望态改为「当前为空目录，预留应用位」，示例标注为模板示意。
  - [x] SubTask 10.1: `doc/architecture.md` 目录树 L59 精简为「可执行应用（当前为空目录，预留应用位）」；L85 子项目分类表末列同步
  - [x] SubTask 10.2: `apps/README.md` L87-96「现有子项目示例」改为「子项目清单」，明示「当前为空目录」，示例表改标「模板示意，非磁盘现状」
  - [x] SubTask 10.3: `tools/README.md#L32` 与 L80 消除 `apps/xs-cli/` 包装层的失实描述（实现全部位于 `tools/xs/`，发行版名 `xs-cli`）
  - **Acceptance Criteria Addressed**: AC-6
  - **Test Requirements**:
    - `rule` TR-10.1: `rg 'apps[\\/]xs-cli'` 命中仅剩否定式表述 / 建议书原文 / 历史归档
- [x] Task 11: 落地 P0-3（上游子模块数 3 → 4，补 `libs/mystx`）
  - **Priority**: high
  - **Depends On**: Task 9
  - **Description**: `.gitmodules` 实有 4 条（`vendor/tvm-ffi`、`libs/tvm-book`、`vendor/caffe`、`libs/mystx`），而 `CONTRIBUTING.md` §3.5 记为「3 个上游子模块」且未提 `libs/mystx`。
  - [x] SubTask 11.1: `CONTRIBUTING.md#L212` 数字改为 4；子模块表补 `libs/mystx` 行（用途：可选 Sphinx 文档主题，缺失时回退 `sphinx-book-theme`）
  - [x] SubTask 11.2: §3.5「初始化时机」补 `libs/mystx` 条目（与 `doc/conf.py` 的 `mystx → sphinx_book_theme → alabaster` 回退链一致）
  - **Acceptance Criteria Addressed**: AC-6
  - **Test Requirements**:
    - `rule` TR-11.1: `rg '3 个上游子模块' CONTRIBUTING.md` 零命中；`git config -f .gitmodules` 条目数 = 4
- [x] Task 12: 清理同源残余引用
  - **Priority**: medium
  - **Depends On**: Task 10
  - **Description**: Task 10 收敛 `apps/xs-cli/` 主引用后，清理同源残余：照抄会失败的安装命令与 routing 表的失效链接。
  - [x] SubTask 12.1: `CONTRIBUTING.md` §4.2/§4.3 删除 `uv pip install -e apps/xs-cli` / `pip install -e apps/xs-cli`（与紧邻 `-e tools/xs` 重复且旧路径不存在）
  - [x] SubTask 12.2: `.agents/context-routing.md#L20` 移除 `[../apps/xs-cli/]` 失效链接
  - **Acceptance Criteria Addressed**: AC-6
- [x] Task 13: 收尾核验与根仓 gitlink 前移
  - **Priority**: medium
  - **Depends On**: Task 12
  - **Description**: 对全轮改动跑门禁（链接、Sphinx 构建），并把子模块指针前移提交到根仓。
  - [x] SubTask 13.1: `check-links.py --path .`（cwd = `projects/xuanspace`）——本轮改动文件 0 新增断链（目录内 128 处为存量，集中 `libs/caffe-ffi/docs/` 与 `doc/okf/`）
  - [x] SubTask 13.2: `python -m sphinx -b html doc doc/_build/html -q --keep-going` → rc=0
  - [x] SubTask 13.3: 根仓推进 `projects/xuanspace` 子模块指针至 `edce88f`
  - **Acceptance Criteria Addressed**: AC-6
  - **Test Requirements**:
    - `rule` TR-13.1: 根仓 `git ls-tree HEAD projects/xuanspace` 的 gitlink = 子模块 HEAD `edce88f`

## 提交记录（证据，第二轮）

| 仓库 | 提交 | 说明 |
|---|---|---|
| `projects/xuanspace` | `d681e4c` | `refactor(doc): 补齐根文档目录命名漂移的 7 处引用`（6 文件，+7/−7） |
| `projects/xuanspace` | `349afa6` | `docs(xuanspace): 修正 apps/ 与上游子模块数量的失实声明`（4 文件，+12/−8，含 P0-2 + P0-3） |
| `projects/xuanspace` | `edce88f` | `docs(xuanspace): 清理 apps/xs-cli 残余引用`（2 文件，+1/−3） |
| 根仓 | `abc724559` | `chore(submodule): 更新 xuanspace 子模块指针至 edce88f`（仅 gitlink，+1/−1） |

> 未 push、未 tag。子模块 HEAD 最终为 `edce88f4a3bd96cf3fe7761383d0dbd08937df7c`，根仓 gitlink 与之对齐。

## 后续任务：规格收口与看板登记（第三轮，纯登记性）

> 范围：不新增分析内容，仅收口本规格自身——勾选已实际解决的 Open Questions，并按 `.trae/specs/README.md`「新增 Spec 指南」第 5 步补齐本规格**创建时遗漏**的看板登记。未改动一至十三节既有记录。

- [x] Task 14: 规格收口与看板登记
  - **Priority**: medium
  - **Depends On**: Task 13
  - **Description**: 本规格三件套的「内容」在 Task 1–7 已完成，但「登记与状态」未收口：spec.md 五条 Open Questions 在实施中已实际定论却未回填；主题/全局看板均未收录本规格（创建时漏跑「新增 Spec 指南」第 5 步）。
  - [x] SubTask 14.1: spec.md「Open Questions」5 条全部改为 `[x]` 并附结论（文件名 / 分组 caption / 提交授权 / frontmatter 约束 / P0 落地）
  - [x] SubTask 14.2: 运行 `docgen.py theme-dashboards`，本规格登记为 workspace-governance 第 3 行（31 行）
  - [x] SubTask 14.3: 运行 `docgen.py update-spec-readme`，全局看板 workspace-governance 30 → 31、合计 738 → 740
  - [x] SubTask 14.4: 修正主题看板表头漂移 `**Spec 数量**：29` → `31`（marker 之外，docgen 不覆盖）
  - **Acceptance Criteria Addressed**: AC-6（一致性口径）
  - **Test Requirements**:
    - `rule` TR-14.1: 主题看板 marker 区内行数 = 31，且含 `analyze-xuanspace-through-boshu-laozi`
    - `rule` TR-14.2: 主题看板表头数字 = marker 区行数；全局看板本主题计数 = 主题看板行数

## 提交记录（证据，第三轮）

| 仓库 | 提交 | 说明 |
|---|---|---|
| 根仓 | 见 [review.md](review.md) 第十二节 | `docs(spec): 收口 analyze-xuanspace-through-boshu-laozi 并登记进看板`（6 文件：三件套 spec/tasks/review + 两级看板 README + okf 主题看板连带刷新） |

> 未 push、未 tag。本轮不涉及 `projects/xuanspace`，子模块无变更。

## 后续任务：P1/P2 落地（第四轮授权）

> 本节记录规格完成后**第四轮**经用户另行授权执行的《优化建议书》落地：P1（一致性缺口）的 P1-1/P1-2/P1-3/P1-4/P1-6 与 P2（精确化）的 P2-1/P2-2/P2-3/P2-4，共 9 项。P1-5 已于「文档入口合并」轮次消解，本轮不含。不改写 Task 1–14 的原始记录。

- [x] Task 15: 落地 P1/P2 一致性缺口与精确化（9 项）
  - **Priority**: medium
  - **Depends On**: Task 14
  - **Description**: 依《优化建议书》P1（一致性缺口）与 P2（精确化）两级清单，逐项对齐 `projects/xuanspace` 文档与实现的缺口。
  - [x] SubTask 15.1（P1-1）: `doc/intro.md` 命令表补 `xs archive` / `xs lfs` / `xs affected` 三行，12 → 15 个一级项，与 `tools/xs/src/xs/cli.py`（7 命令组 + 8 直接命令）及 `README.md`「15 个子命令」口径齐平
  - [x] SubTask 15.2（P1-2）: `doc/architecture.md` 依赖示例扩为 `docs` 6 项（`sphinx`/`myst-parser`/`sphinx-book-theme`/`sphinx-design`/`sphinx-copybutton`/`sphinxcontrib-mermaid`），并显式列出 `test`/`lint`/`build` 与 `[dependency-groups]` 的 `dev` 展开式，替换原 `xuanspace[docs,test,lint,build]` 引用式
  - [x] SubTask 15.3（P1-3）: `libs/README.md` 示例 `scikit-build-core>=0.5` → `>=0.11`，与全仓实际声明（根 `pyproject.toml`、`tools/xs`、`tools/okf`、`libs/xuan-core`、`libs/xuan-ext-demo`）一致
  - [x] SubTask 15.4（P1-4）: 三份「现有子项目」清单补全至磁盘现状——`libs/README.md` 由 2 项改 8 项（按字母序，附免责注）；`tools/README.md` 目录树与模板表补 `native-ffi/`；`README.md` 项目索引表补 `mystx`/`xuan-compose`/`xuan-core`/`xuan-ext-demo` 4 行（9 → 13）。**期望态的「生成物/断言对象」形式未实现，列为后续**（见 review.md 第十三节 13.4）
  - [x] SubTask 15.5（P1-6）: `.meta/README.md` 于「概述」后新增「当前阶段冻结（重要）」节（Task 20 前禁止加 frontmatter / 建 TOML 镜像，规则层优先）；`.agents/rules/frontmatter.md` 补 **Task 20 解冻触发条件**（`xs meta scan` / `xs meta sync` 端到端可用时）
  - [x] SubTask 15.6（P2-1）: `doc/intro.md` 开篇《老子》引文后补版本标注——明示依**传世本**（王弼本系统）面貌，并给出马王堆甲本／乙本相应文句（乙本此句完整、甲本此句残、「恒」字据帛书通释；「恒」改「常」系避汉文帝刘恒讳）
  - [x] SubTask 15.7（P2-2）: `doc/architecture.md`「自建库（projects/）」节「SpecWeave 主仓库」→「上层工作区」，消除与文件所在语境的指代漂移
  - [x] SubTask 15.8（P2-3）: `AGENTS.md` 验收基线 mypy 行补范围口径——「检查范围以 CI 为准（当前为 `tools/xs libs/xuan-core libs/xuan-ext-demo`，见 `.github/workflows/ci.yml`）」
  - [x] SubTask 15.9（P2-4）: `README.md` Mermaid `法` 子图重名节点 `Conventions[AGENTS.md]` → `AgentsMd[AGENTS.md]`，节点标识唯一
  - **Acceptance Criteria Addressed**: AC-6（范围仅限 `projects/xuanspace` 内文档与规范文件）
  - **Test Requirements**:
    - `rule` TR-15.1: `check-links.py --path .`（cwd = `projects/xuanspace`）本轮 8 文件 **0 新增断链**（目录内 127 处为存量）
    - `rule` TR-15.2: `doc/intro.md` 命令表条目数 = 15；`rg "scikit-build-core>="` 于 `libs/` `tools/` 与 `pyproject.toml` 一致（`>=0.11`）
    - `rule` TR-15.3: 根仓 `git ls-tree HEAD projects/xuanspace` 的 gitlink = 子模块 HEAD `4c9a346`

## 提交记录（证据，第四轮）

| 仓库 | 提交 | 说明 |
|---|---|---|
| `projects/xuanspace` | `4c9a346` | `docs(xuanspace): 对齐文档与实现的一致性缺口与精确化（P1/P2）`（8 文件，+54/−11） |
| 根仓 | `d0d531e2c` | `chore(xuanspace): 前移子模块指针至 4c9a346（文档一致性 P1/P2 落地）`（仅 gitlink，+1/−1） |

> 未 push、未 tag。子模块 HEAD 最终为 `4c9a3467a30e35cb820bb9784cec19593d2e31e6`，根仓 gitlink 与之对齐。子模块工作树残留 5 项（`.gitignore`、`pyproject.toml`、`src/xuanspace/__init__.py`、`tools/xs/src/xs/commands/version_cmd.py`、`tools/xs/src/xs/discovery.py`）为**并行会话在途改动**，本轮未触碰、未提交。

## 后续任务：P0-4 落地（第五轮授权）

> 本节记录规格完成后**第五轮**经用户另行授权执行的《优化建议书》**P0-4**（建立「声明—实现一致性」门禁）落地。P0-4 是建议书中最后一个未落地的 P0 项（P0-1/P0-2/P0-3 已在前四轮闭环，P1/P2 全量 9 项已在第四轮闭环）。不改写 Task 1–15 的原始记录。

- [x] Task 16: 落地 P0-4（声明—实现一致性门禁）
  - **Priority**: high
  - **Depends On**: Task 15
  - **Description**: 依《优化建议书》P0-4，把仓库中**可机械提取的文档声明**与**磁盘/代码事实**做成自动化门禁——新增 `scripts/check_declaration_consistency.py`（生成/校验双模式），覆盖三类声明，并接入 `ci.yml` 的 `quality` job，使声明与实现的静默漂移在 CI 期即失败。
  - [x] SubTask 16.1: 新增 `scripts/check_declaration_consistency.py`——校验模式（默认，退出码 0/1/2）+ 生成模式（`--generate` 刷新清单快照，幂等）+ `--json` 输出；三类断言：**A. CLI 命令清单**（`README.md`「N 个子命令」计数与 `doc/intro.md` 命令表 ↔ `tools/xs/src/xs/cli.py` 注册表）、**B. 子项目清单**（`libs/README.md`「现有子项目」表 ↔ `libs/` 磁盘目录）、**C. 目录名口径**（`README.md`「目录结构」块声明的目录磁盘存在性 + 顶层禁止 `docs/` + 必须有 `doc/`）；末尾比对 `scripts/declaration-snapshot.json` 快照
  - [x] SubTask 16.2: 生成 `scripts/declaration-snapshot.json`（15 一级命令 + 8 `libs/` 子项目）
  - [x] SubTask 16.3: `ci.yml` `quality` job 于 `Check pyproject.toml canonical style` 之后插入 `Check declaration consistency` step（`python scripts/check_declaration_consistency.py`），步骤序号顺延，job 表头注释更新为「五项自动化检查」
  - [x] SubTask 16.4: `scripts/README.md` 登记新脚本（「现有脚本示例」表 + 「脚本目录结构」不变）；于 §1「Shebang 和编码声明」补 **Python 3.14 例外**说明（py314 下 ruff `UP009` 视编码声明多余，新脚本省略该行），消解 README 字面要求与 ruff 配置的叙述张力
  - [x] SubTask 16.5: 落实建议书规定的**验收动作**——故意把 `README.md` 的「15」改为「14」，校验应失败；改回后应通过
  - [x] SubTask 16.6: 顺带覆盖 P1-4 遗留的「清单条目 ⊆ 磁盘目录」断言（第四轮 review.md §13.4 记为后续项）——B 类断言即 `libs/README.md` 表与 `libs/` 磁盘目录的双向集合比对
  - **Acceptance Criteria Addressed**: AC-6（范围仅限 `projects/xuanspace` 内新增脚本、快照、CI 配置与脚本目录 README）
  - **Test Requirements**:
    - `rule` TR-16.1: **验收动作**——`README.md`「15 个子命令」改为「14」时 `python scripts/check_declaration_consistency.py` 退出码 = 1 且报出「声明 14 … 实际注册 15」；改回后退出码 = 0
    - `rule` TR-16.2: 生成模式幂等——连续两次 `--generate` 第二次输出「清单快照已是目标状态，跳过」且退出码 = 0
    - `rule` TR-16.3: `ruff check` 与 `ruff format --check` 对 `scripts/` 双绿
    - `rule` TR-16.4: `check-links.py --path .`（cwd = `projects/xuanspace`）本轮 **0 新增断链**（127 处为存量）
    - `rule` TR-16.5: 根仓 `git ls-tree HEAD projects/xuanspace` 的 gitlink = 子模块 HEAD

## 提交记录（证据，第五轮）

| 仓库 | 提交 | 说明 |
|---|---|---|
| `projects/xuanspace` | `2750078` | `ci(xuanspace): 新增声明—实现一致性门禁（P0-4）`（4 文件，+304/−5：`scripts/check_declaration_consistency.py` + `scripts/declaration-snapshot.json` + `.github/workflows/ci.yml` + `scripts/README.md`） |
| 根仓 | `3a6d95193` | `chore(xuanspace): 前移子模块指针至 2750078 并回写 P0-4 落地证据`（3 文件，+78/−1：`review.md` + `tasks.md` + 子模块 gitlink） |

> 未 push、未 tag。子模块 HEAD 为 `2750078e2386ee4efd3e09c0a3155bd43abaffd4`，根仓 gitlink 与之对齐。子模块工作树残留 8 项（`.gitignore`、`pyproject.toml`、`src/xuanspace/__init__.py`、`tools/xs/README.md`、`tools/xs/src/xs/__init__.py`、`tools/xs/src/xs/cli.py`、`tools/xs/src/xs/commands/version_cmd.py`、`tools/xs/src/xs/discovery.py`）为**并行会话在途改动**，本轮未触碰、未提交。

## 后续任务：建议书文末陈述收口（第六轮授权）

> 本节记录规格完成后**第六轮**经用户另行授权执行的收口：处置《优化建议书》文末「本轮不执行任何建议项，仅提出清单」这一**在 P0/P1/P2 陆续落地后已与事实不符**的存量陈述（承第四轮 review.md §13.4、第五轮 §14.4 两轮登记的「留待后续统一处置」）。仅修正陈述与回写证据，不改写 Task 1–16 的原始记录。

- [x] Task 17: 修正《优化建议书》文末失真陈述并回写收口证据
  - **Priority**: low
  - **Depends On**: Task 16
  - **Description**: `doc/recommendations.md` 文末「本轮不执行任何建议项，仅提出清单」在 P0-1~P0-4、P1 全量、P2 全量落地后已失真；改写为反映实际闭环状态的陈述，并在规格三件套回写本轮证据。
  - [x] SubTask 17.1: 改写 `doc/recommendations.md` 文末末句——列明已闭环项（P0-1~P0-4、P1-1~P1-4 与 P1-6、P2-1~P2-4；P1-5 随「文档入口合并」消解）并指向根仓本主题规格三件套
  - [x] SubTask 17.2: `tasks.md` / `review.md` 回写第六轮收口证据（本节 + review.md 第十五节）
  - **Acceptance Criteria Addressed**: AC-6（范围仅限 `projects/xuanspace` 文档陈述与根仓规格三件套）
  - **Test Requirements**:
    - `rule` TR-17.1: `rg "本轮不执行任何建议项" doc/` 命中 0
    - `rule` TR-17.2: `check-links.py --path .`（cwd = `projects/xuanspace`）本轮 **0 新增断链**（127 处为存量）
    - `rule` TR-17.3: 根仓 `git ls-tree HEAD projects/xuanspace` 的 gitlink = 子模块 HEAD

## 提交记录（证据，第六轮）

| 仓库 | 提交 | 说明 |
|---|---|---|
| `projects/xuanspace` | `d2dc124` | `docs(xuanspace): 修正建议书文末与落地事实不符的存量陈述`（`doc/recommendations.md`） |
| 根仓 | `4b538fa72` | `chore(xuanspace): 前移子模块指针并回写建议书收口证据`（`tasks.md` + `review.md` + gitlink） |

> 未 push、未 tag。

## 后续任务：P1-4① 落地与建议书彻底精简（第七轮授权）

> 本节记录规格完成后**第七轮**经用户另行授权执行的工作：① 落地《优化建议书》P1-4 期望态遗留的**第 ① 条**（清单改由脚本注入的生成块派生）；② 按用户指令把 `doc/recommendations.md` 中的**已闭环条目彻底清空**——P1-4 在本轮 ① 落地后即闭环，故该条目亦随之移除，文件收口为「全量闭环、无待办」终态。不改写 Task 1–17 的原始记录。

- [x] Task 18: 落地 P1-4①（libs 子项目清单改为脚本生成块）并收口建议书
  - **Priority**: medium
  - **Depends On**: Task 17
  - **Description**: P1-4 期望态第 ② 条（清单 ⊆ 磁盘目录断言）已于第五轮由 B 类断言覆盖；本轮落地第 ① 条——把 `libs/README.md`「现有子项目」表改为由 `scripts/check_declaration_consistency.py` 从 `libs/` 磁盘目录派生的生成块，并把「类型 / 说明」两列收进脚本内嵌映射 `LIB_PROJECT_META`，消灭最后一处手写真源；随后按用户指令清空建议书中全部已闭环条目。
  - [x] SubTask 18.1: `check_declaration_consistency.py` 新增 `LIBS_GENERATED_BEGIN`/`LIBS_GENERATED_END` 标记常量与 `LIB_PROJECT_META`（8 项：目录名 → (类型, 说明)）；新增 `_generated_block()`、`render_lib_projects_table()`、`inject_lib_projects_block()`；删除 `_LIB_ROW_RE`、`_section()`、`declared_lib_projects()`（不再解析手写表）
  - [x] SubTask 18.2: 校验模式 B 段重写——比对「生成块内容 == 脚本渲染结果」，且 `LIB_PROJECT_META` 缺登记项亦判失败；`--generate` 增加「刷新清单生成块」职责（幂等）
  - [x] SubTask 18.3: `libs/README.md` 手写表改为「引语 + 生成标记块」；`scripts/README.md` 该脚本行说明同步为「子项目清单（`libs/README.md` 生成块）…`--generate` 刷新快照与清单生成块」
  - [x] SubTask 18.4: `doc/recommendations.md` 彻底清空已闭环条目（P0-1~P0-4、P1-1~P1-6、P2-1~P2-4，含本轮闭环的 P1-4），收口为终态说明（166 行 → 12 行）
  - **Acceptance Criteria Addressed**: AC-6（范围仅限 `projects/xuanspace` 内脚本与文档）
  - **Test Requirements**:
    - `rule` TR-18.1: 校验模式退出码 = 0；新增 `libs/<probe>/` 目录后退出码 = 1 且报「生成块缺元数据登记」「已过期」「快照 lib_projects 已过期」，探针清理后复现通过
    - `rule` TR-18.2: 生成模式幂等——`--generate` 输出「清单快照已是目标状态，跳过」与「生成块已是目标状态，跳过」且退出码 = 0
    - `rule` TR-18.3: `ruff check scripts/check_declaration_consistency.py` 通过（新脚本省略 `# -*- coding: utf-8 -*-`，符合 py314 `UP009`）
    - `rule` TR-18.4: `check-links.py --paths doc libs scripts`（cwd = `projects/xuanspace`）本轮 4 文件 **0 新增断链**（127 处为存量）
    - `rule` TR-18.5: 根仓 `git ls-tree HEAD projects/xuanspace` 的 gitlink = 子模块 HEAD

## 提交记录（证据，第七轮）

| 仓库 | 提交 | 说明 |
|---|---|---|
| `projects/xuanspace` | `fc4fe25` | `refactor(xuanspace): libs 子项目清单改由脚本生成块派生`（3 文件：`scripts/check_declaration_consistency.py` + `libs/README.md` + `scripts/README.md`，+96/−34） |
| `projects/xuanspace` | `f9e2b2c` | `docs(xuanspace): 优化建议书移除已闭环条目并收口为终态`（1 文件：`doc/recommendations.md`，+2/−166） |
| 根仓 | `f92d2ebe1` | `chore(xuanspace): 前移子模块指针并回写 P1-4① 落地证据`（`tasks.md` + `review.md` + gitlink） |

> 未 push、未 tag。子模块 HEAD 为 `f9e2b2cde2c04055dd58026b7c38d168e2ce274a`，根仓 gitlink 与之对齐。子模块工作树残留项（`.gitignore`、`pyproject.toml`、`src/xuanspace/__init__.py`、`tools/xs/**`、`libs/xuan-compose/**`、`libs/caffe-ffi/**`、`libs/npu-ffi/**`、`libs/demo-ffi/**`）为**并行会话在途改动**，本轮未触碰、未提交。
