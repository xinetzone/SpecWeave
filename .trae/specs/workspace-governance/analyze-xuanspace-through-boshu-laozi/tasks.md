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

## 后续任务：声明一致性门禁扩容与残余漂移清理（第八轮授权）

> 本节记录规格完成后**第八轮**经用户另行授权执行的工作：① 把 `scripts/check_declaration_consistency.py` 从三类断言扩容至**六类**（新增 D vendor 清单、E 子模块声明、F 项目索引）；② 清理两处残余漂移（`doc/architecture.md` 失实的 `CMakeLists.txt` 行、`vendor/README.md` 的「待实际添加后更新此表」占位符）。本轮兑现《项目蓝图》目标态特征 1「所有可机械提取的声明（子项目清单、命令清单、目录树）要么由脚本生成，要么受 CI 断言约束」。不改写 Task 1–18 的原始记录。

- [x] Task 19: 声明一致性门禁扩容至六类断言并清理残余漂移
  - **Priority**: medium
  - **Depends On**: Task 18
  - **Description**: 既有门禁仅覆盖 A（CLI 命令清单）、B（子项目清单生成块）、C（目录名口径）三类，`vendor/README.md` 子项目表、`CONTRIBUTING.md` 子模块计数与表、`README.md` 项目索引表三处声明仍无断言守护。本轮补齐 D/E/F 三类，并把新增的 `submodules` 事实纳入清单快照；同时清除两处与磁盘不符的残余陈述。
  - [x] SubTask 19.1: 新增解析助手与事实/声明提取函数——`_section`（截二级标题间正文）、`_table_first_column`（只解析首张连续表首列）、`extract_dir_names`、`extract_submodules`（解析 `.gitmodules` 的 `path`）、`extract_vendor_submodules`、`declared_vendor_projects`、`declared_contributing_submodules`、`declared_submodule_count`、`declared_index_projects`、`expected_index_projects`（tools/ ∪ libs/ ∪ vendor/ 子模块）
  - [x] SubTask 19.2: `run_checks` 新增 D（vendor 表 ↔ `.gitmodules` vendor 子模块）、E（`包含 N 个上游子模块` 计数与子模块表 ↔ `.gitmodules`）、F（「项目索引」表 ↔ tools/ + libs/ 磁盘 ∪ vendor 子模块）三段；`collect_manifest` 加 `submodules` 键，快照比对改为遍历 manifest 全键（新增键自动纳入校验）
  - [x] SubTask 19.3: 清理两处残余漂移——`doc/architecture.md` 删根目录树中失实的 `CMakeLists.txt` 行（该项目为纯 Python 枢纽包，`wheel.cmake = false`）；`vendor/README.md`「现有子项目」表前删「（待实际添加后更新此表）」占位符
  - [x] SubTask 19.4: 同步口径文案——脚本模块 docstring「覆盖三类声明」→「覆盖六类声明」（列 A–F）、成功输出与 argparse description 同步；`scripts/declaration-snapshot.json` 刷新纳入 `submodules` 键；`.github/workflows/ci.yml` 步骤注释同步为六类
  - **Acceptance Criteria Addressed**: AC-6（范围仅限 `projects/xuanspace` 内脚本与文档）
  - **Test Requirements**:
    - `rule` TR-19.1: 校验模式退出码 = 0，输出「声明与实现一致：CLI 命令清单 / 子项目清单 / 目录名口径 / vendor 清单 / 子模块声明 / 项目索引 全部通过。」
    - `rule` TR-19.2: 负向探针 4/4 PASS——基线（无漂移）+ D（vendor 表删 `caffe` 行）+ E（`包含 4 个上游子模块` 改 `5 个`）+ F（项目索引插 `ghost` 行）均按预期退出码与关键词命中；探针在 `tempfile` 夹具上执行，不触碰真实仓库
    - `rule` TR-19.3: 生成模式幂等——`--generate` 二次运行输出「已是目标状态，跳过」且退出码 = 0
    - `rule` TR-19.4: `--json` → `{"ok": true, "failures": [], "notes": []}`
    - `rule` TR-19.5: `ruff check scripts/check_declaration_consistency.py` 通过
    - `rule` TR-19.6: `check-links.py --paths doc vendor scripts`（cwd = `projects/xuanspace`）本轮 4 文件 **0 新增断链**（33 处为存量）
    - `rule` TR-19.7: 根仓 `git ls-tree HEAD projects/xuanspace` 的 gitlink = 子模块 HEAD

## 提交记录（证据，第八轮）

| 仓库 | 提交 | 说明 |
|---|---|---|
| `projects/xuanspace` | `fd6d7e6` | `feat(scripts): 声明一致性门禁扩容至六类断言并清理残余漂移`（5 文件，+149/−19：`scripts/check_declaration_consistency.py` + `scripts/declaration-snapshot.json` + `doc/architecture.md` + `vendor/README.md` + `.github/workflows/ci.yml`） |
| 根仓 | `8d5872424` | `chore(xuanspace): 前移子模块指针并回写门禁扩容证据`（`tasks.md` + `review.md` + gitlink） |

> 未 push、未 tag。子模块 HEAD 为 `fd6d7e6bdc2447b8e027d56b6f4f5f65338c6a55`，根仓 gitlink 与之对齐。根仓 `?? .trae/specs/financial-economics-okf-wiki/` 与 ` ? projects/awesome-okf-xs` 为**并行会话在途改动**，本轮未触碰、未提交。

## 后续任务：依赖方向门禁（第九轮授权）

> 本节记录规格完成后**第九轮**经用户另行授权执行的工作：兑现《项目蓝图》目标态三特征中**唯一未兑现**的特征 3「方向可断言」——把 `libs/README.md`「依赖规则」一节的分区依赖规则从「只写在文档里」变为 CI 可判定。不改写 Task 1–19 的原始记录。

- [x] Task 20: 新增依赖方向门禁（分区依赖规则可断言）
  - **Priority**: medium
  - **Depends On**: Task 19
  - **Description**: 蓝图目标态三特征中，特征 1（声明可核对，第八轮六类断言）与特征 2（单一事实来源，P1-4① 生成块 + 快照）已兑现，特征 3「方向可断言」仍只在文档里——蓝图洞察 I4 明言该依赖方向约束「只写在图里、未被任何检查断言」。本轮新增 `scripts/check_dependency_direction.py`：以 `ast` 解析 `libs/` 下全部 Python 源码的 import，断言不依赖 `apps/`、`scripts/`、`attic/`、`vendor/`，与 `libs/README.md`「依赖规则」同源。
  - [x] SubTask 20.1: 新建 `scripts/check_dependency_direction.py`——规则常量 `FORBIDDEN_IMPORTS` 登记为单一事实来源；`ast.walk` 取绝对导入顶层模块名（`Import` 与 `ImportFrom`，`level > 0` 的相对导入不检查）；`_submodule_paths` / `_is_nested_submodule` 排除 `.gitmodules` 声明的子模块（`libs/mystx`、`libs/tvm-book`）；`IGNORED_DIR_NAMES` 跳过构建产物与缓存目录；`main() -> int` 返回 0/1/2，输出「文件:行号:顶层模块」定位
  - [x] SubTask 20.2: 接入 CI——`.github/workflows/ci.yml` quality job 在 declaration 之后增「Check dependency direction」步骤；并修正该 job 头注释（原「五项」与所列六项不符）为「七项」并纳入 `dependency`
  - [x] SubTask 20.3: `scripts/README.md`「现有脚本示例」表补 `check_dependency_direction.py` 行（校验类、幂等=是）；并修正 `check_declaration_consistency.py` 行描述（第八轮扩至六类后仍写三类）
  - [x] SubTask 20.4: `libs/README.md`「依赖规则」一节补注脚——声明该规则由脚本在 CI 中机械断言，其 `FORBIDDEN_IMPORTS` 为单一事实来源
  - [x] SubTask 20.5: 决策记录——`doc/blueprint.md` 事实清单第 14/15/17 行的行号引用（`libs/README.md#L106-L111`、`#L115-L118`）与洞察 I4 行动项中的同址引用，系**带基线 `8db593d5` 的时点快照事实**（其漂移本身即 P1-4① 注入生成块所致，已在第八轮登记）；按项目「不改动历史事实快照」约束**不予回改**，仅在本规格留痕
  - **Acceptance Criteria Addressed**: AC-6（范围仅限 `projects/xuanspace` 内脚本与文档）
  - **Test Requirements**:
    - `rule` TR-20.1: 基线退出码 = 0，输出「扫描到 291 个 Python 文件（分区：libs）」与「全部通过依赖方向校验：libs 未依赖 apps, scripts, attic, vendor。」
    - `rule` TR-20.2: 负向探针 3/3 命中——在 `libs/xuan-core/src/xuan_core/` 临时注入 `from scripts import x` / `import vendor.caffe` / `from attic.old import y`，退出码 = 1 且逐条输出 `文件:行号: 禁止导入 '<分区>'（来自 '<模块>'）`；清理探针后恢复退出码 = 0
    - `rule` TR-20.3: 相对导入不误报——`from . import x` / `from ..mod import y`（`level > 0`）不进入检查，探针验证通过
    - `rule` TR-20.4: `ruff check` 与 `ruff format --check` 对新脚本通过（新脚本省略 `# -*- coding: utf-8 -*-` 且不含 `from __future__ import annotations`，符合 py314 规范）
    - `rule` TR-20.5: 既有门禁无回归——`check_declaration_consistency.py` 退出码 = 0（六类全通过）、`check_pyproject_style.py` 退出码 = 0（12 个 pyproject.toml）
    - `rule` TR-20.6: `check-links.py --paths libs/README.md scripts/README.md doc/blueprint.md`（cwd = `projects/xuanspace`）本轮 3 文件 **0 新增断链**
    - `rule` TR-20.7: 根仓 `git ls-tree HEAD projects/xuanspace` 的 gitlink = 子模块 HEAD

## 提交记录（证据，第九轮）

| 仓库 | 提交 | 说明 |
|---|---|---|
| `projects/xuanspace` | `c50f18e` | `feat(scripts): 新增依赖方向门禁并同步文档与 CI`（4 文件，+164/−2：`scripts/check_dependency_direction.py`（新建）+ `scripts/README.md` + `libs/README.md` + `.github/workflows/ci.yml`） |
| 根仓 | `06f37e234` | `chore(xuanspace): 前移子模块指针并回写依赖方向门禁证据`（`tasks.md` + `review.md` + gitlink） |

> 未 push、未 tag。子模块 HEAD 为 `c50f18eb26f62e3d0f56cb60c10655e5e50dd233`，根仓 gitlink 与之对齐。本轮 `projects/xuanspace` 工作树仅含本轮 4 项变更（无并行会话残留）；根仓在途改动（并行会话已自行提交 `b40d65e82`、`68f5f0b79`）本轮未触碰。

## 后续任务：存量断链修复（第十轮授权）

> 本节记录规格完成后**第十轮**经用户另行授权执行的工作：清理 `doc/` 目录内 33 处「省略 `.md` 扩展名」的相对链接——该批断链自第一轮（Task 7 取证）起即由根仓 `check-links.py` 报出，长期以「存量」挂账。本轮**先做根因判定再修**，避免照单全改。不改写 Task 1–20 的原始记录。

- [x] Task 21: 修复 `doc/` 目录 33 处省略扩展名的相对链接
  - **Priority**: medium
  - **Depends On**: Task 20
  - **Description**: 33 处断链分布在 7 个文件；目标文件全部**真实存在**，差异仅在链接未写 `.md`。故本轮的关键不是「改 33 处」而是**先定性**：是文档缺陷，还是检查器误报？定性决定修复对象（改文档 vs 改检查器）。
  - [x] SubTask 21.1: 根因判定（I+F，三项独立验证）——
    ① **渲染验证**（决定性）：`sphinx -b html` 产物 `doc/_build/probe/intro.html` 中 `[快速开始](quickstart)` 渲染为 `<a class="reference internal" href="quickstart.html"><span class="doc std std-doc">快速开始</span></a>`，与 `.md` 写法产物**逐字一致** → **渲染无缺陷**，`check-links.py` 判为断链属**误报**（该脚本未实现 MyST docname 解析）；
    ② **约定验证**：仓内唯一书面化的链接格式规则是 `doc/okf/synthesis.md` L12 的 `` `- [<title>](<相对路径>.md)` ``，且 `doc/index.md`、`doc/okf/synthesis.md` 均照此写 → 这 33 处**违反仓内书面约定**；
    ③ **门禁验证**：CI 走的是 `xs doc linkcheck`（Sphinx linkcheck，只校外链），根仓 `check-links.py` 才拦本地相对链接 → 该批断链的**真实影响面**是「仓内链接门禁常红、PR 要求无法满足」，而非站点 404
  - [x] SubTask 21.2: 修复 33 处（7 文件，33 增 33 删）——`doc/intro.md`（4）、`doc/quickstart.md`（4）、`doc/okf/architecture.md`（4）、`doc/okf/bundle.md`（11）、`doc/okf/commands.md`（3）、`doc/okf/conformance.md`（1）、`doc/okf/quickstart.md`（6）；逐条与检查器输出的 `文件:行号` 对齐核对
  - [x] SubTask 21.3: 预防（修复即闭环）——`CONTRIBUTING.md` §12.4「文档风格建议」增一行：交叉引用一律使用带 `.md` 扩展名的相对路径，并说明省略扩展名会被链接门禁判为断链。选点理由：该文件经 `{include} ../CONTRIBUTING.md` 进入 `doc/contributing.md`，是文档作者的通用入口，而原约定只写在 `okf/synthesis.md`（OKF 教程局部），故顶层与 okf 教程作者看不到——这正是漂移得以存续九轮的机制
  - [x] SubTask 21.4: 决策记录——**不修改**根仓 `.agents/scripts/check-links.py`。该脚本未实现 MyST docname 解析，是误报来源；但它是**主权区共享资产**，改动影响全仓所有 app，需另行授权；且「带/不带 `.md` 两种写法都合法」会造成口径分裂，与单一事实来源相悖。本轮取「统一文档到已书面化的 `.md` 约定」路线，把检查器局限作为**已知限制**登记而非就地修补
  - **Acceptance Criteria Addressed**: AC-6（范围仅限 `projects/xuanspace`）、AC-7（门禁不回归）
  - **Test Requirements**:
    - `rule` TR-21.1: `check-links.py --path doc`（cwd = `projects/xuanspace`）退出码 = 0，输出「校验通过: 所有链接均有效」（修复前：33 断链、退出码 1）
    - `rule` TR-21.2: 残留检索 `\]\((?:trust|attested|conformance|commands|synthesis|plugins|bundle|index|architecture|build-system|contributing|cli/index|quickstart)\)` 于 `doc/**/*.md` 命中 = **0**（修复前 32 + `quickstart` 1 = 33）
    - `rule` TR-21.3: `sphinx -b html doc doc/_build/probe2` 构建成功、无 WARNING/ERROR；抽验产物 `okf/bundle.html` 的 `href`（`trust.html`、`attested.html`）与修复前逐字一致 → 修复为**纯口径统一、零渲染变化**
    - `rule` TR-21.4: `git diff --stat` 恰为 7 文件 **33 增 33 删**（无附带改动）
    - `rule` TR-21.5: 既有门禁无回归——`check_pyproject_style.py`（12 个 pyproject.toml）退出码 = 0；`check_declaration_consistency.py`（六类）退出码 = 0；`check_dependency_direction.py`（291 文件）退出码 = 0；`check-links.py --path CONTRIBUTING.md` 退出码 = 0（新增预防条款未引入本地引用误报）

## 提交记录（证据，第十轮）

| 仓库 | 提交 | 说明 |
|---|---|---|
| `projects/xuanspace` | `13b98b3` | `docs(xuanspace): 统一 doc/ 相对链接为带 .md 扩展名的仓内约定`（8 文件，+34/−33：7 个 `doc/**` 文档 33 处链接 + `CONTRIBUTING.md` 预防条款） |
| 根仓 | `f8e60d147` | `chore(xuanspace): 前移子模块指针并回写存量断链修复证据`（`tasks.md` + `review.md` + gitlink） |

> 未 push、未 tag。本轮 `projects/xuanspace` 工作树仅含本轮 8 项变更。

## 后续任务：过程性文档清理（第十一轮授权）

> 本节记录规格完成后**第十一轮**经用户裁定执行的文档生命周期处置：删除两份**过程性分析产物** `doc/blueprint.md`（《项目蓝图》）与 `doc/recommendations.md`（《优化建议书》），并清理其导航登记与交叉引用。裁定依据见 review.md §20。不改写 Task 1–21 的原始记录，亦不回改 §一 AC-1 的勾选（历史可审计性）。

- [x] Task 22: 删除 `doc/blueprint.md` 与 `doc/recommendations.md`
  - **Priority**: low
  - **Depends On**: Task 21
  - **Description**: 两份文档为**一次性过程性分析产物**，其权威载体已转移至本规格三件套（决策与证据）与 git 历史（变更事实）；`recommendations.md` 已收口为终态空壳（12 行，条目全部闭环后正文移除），`blueprint.md` 内容基于基线 `8db593d` 已与现状不一致（其标记「薄弱」的事项多数已在第七至十轮闭环）。活文档与现状不一致即**失真源**，故删除。
  - [x] SubTask 22.1: 洞察（I）——机械提取引用面：`doc/index.md` L64–70 的「规划」toctree 登记两项；`blueprint.md` L308 ↔ `recommendations.md` L3/L12 互引。确认二者是**活的 doc/ 文档**（非规格历史快照）
  - [x] SubTask 22.2: 第一性原理（F）——剥离叙事看本质：蓝图＝分析结论、建议书＝待办清单，均属**一次性产物**；结构叙事已由 `README.md` 与 `doc/architecture.md` 承载，无需第三份重复且易腐
  - [x] SubTask 22.3: 删除两份文档（`doc/blueprint.md`、`doc/recommendations.md`）
  - [x] SubTask 22.4: 清理导航与引用——移除 `doc/index.md` 的「规划」toctree（两项全删后该分组变空）
  - [x] SubTask 22.5: 决策记录——**不回改** review.md §一 AC-1 的勾选记录（该断言的范围是规格实施过程，删除属规格完成后经用户裁定的新决策，二者不矛盾）
  - **Acceptance Criteria Addressed**: AC-6（范围仅限 `projects/xuanspace`）、AC-7（门禁不回归）
  - **Test Requirements**:
    - `rule` TR-22.1: `check-links.py --path doc`（cwd = `projects/xuanspace`）退出码 = 0（20 个 Markdown 文件、35 处本地引用全有效；删除后「规划」toctree 与互引一并消失，无新增断链）
    - `rule` TR-22.2: 残留检索 `blueprint|recommendations` 于 `doc/**/*.md` 命中 = **0**
    - `rule` TR-22.3: `sphinx -b html doc doc/_build/probe3` 构建成功、无 WARNING/ERROR、无 orphan 警告
    - `rule` TR-22.4: 变更面恰为 3 项（`doc/blueprint.md` D、`doc/recommendations.md` D、`doc/index.md` M）

## 提交记录（证据，第十一轮）

| 仓库 | 提交 | 说明 |
|---|---|---|
| `projects/xuanspace` | `91ba03d` | `docs(xuanspace): 删除已闭环的过程性分析文档并清理导航`（3 文件：`doc/blueprint.md` D、`doc/recommendations.md` D、`doc/index.md` M） |
| 根仓 | `575f839d1` | `chore(xuanspace): 前移子模块指针并回写过程性文档清理证据`（`tasks.md` + `review.md` + gitlink） |

> 未 push、未 tag。本轮 `projects/xuanspace` 工作树仅含本轮 3 项变更。

## 后续任务：文档易腐性清理与门禁扩容（第十二轮授权）

> 本节记录规格完成后**第十二轮**经用户裁定执行的工作：①删除手工维护的时点快照 `doc/dependency-report.md`（及其 `.meta` 元数据镜像）；②修复活文档 `doc/cli/index.md` 的命令清单失真；③把门禁断言 A 扩容覆盖该文件以预防同类漂移。裁定依据见 review.md §21。不改写 Task 1–22 的原始记录，亦不回改历史验收勾选。

- [x] Task 23: 删除 `doc/dependency-report.md` 并修复 `doc/cli/index.md` 失真 + 门禁扩容
  - **Priority**: low
  - **Depends On**: Task 22
  - **Description**: `dependency-report.md` 是**手工维护的时点快照**（全仓无生成器），必然随实现演进而漂移，且已实证偏离（CI job 表误列已不存在的 `lint`、漏 `py-compat`；子模块树仅列 2 项、实际 4 项；`apps/` 仍标「空，待填充」），其持久事实已由 `architecture.md`/`build-system.md`/`CONTRIBUTING.md` 承载 → 删除。`cli/index.md` 是**活参考文档**（README 以其为 CLI 参考链接）却仅列 13 条命令，缺 `xs archive`/`xs lfs`（README 声明 15 条）→ 补全，并扩容门禁断言 A 覆盖之。
  - [x] SubTask 23.1: 洞察（I）——机械提取引用面：`doc/index.md` L60「项目」toctree；`.meta/toml/doc/dependency-report.toml`（`x-toml-ref` 目标）；文档自引三处。核验命令口径：`cli.py` 实际注册 **15** 项（7 `add_typer` + 8 `app.command`），`intro.md` 已列全、`cli/index.md` 仅列 13
  - [x] SubTask 23.2: 第一性原理（F）——区分**活文档**与**时点快照**：报告类产物若不自带生成器，其功能等价于「过期风险载体」；CLI 参考的功能是「与注册表一致」，故唯一正确形态是受门禁约束的活文档
  - [x] SubTask 23.3: 属性判定——`dependency-report.md` ＝ 时点快照（处置：删除）；`cli/index.md` ＝ 活文档但内容过期（处置：更新对齐 + 门禁约束）
  - [x] SubTask 23.4: 删除 `doc/dependency-report.md` 与 `.meta/toml/doc/dependency-report.toml`，移出 `doc/index.md`「项目」toctree
  - [x] SubTask 23.5: 补全 `doc/cli/index.md` 的 `xs archive`（archive/unarchive）与 `xs lfs`（check/patterns）两条，含总览表行与细则章节
  - [x] SubTask 23.6: 结论化（C）——扩容 `check_declaration_consistency.py` 断言 A：新增 `CLI_REF_FILE` 常量与 `declared_cli_ref_commands()`，共用 `_DOC_CMD_ROW_RE`，`run_checks` 增加「`cli/index.md` 命令总览 ↔ 注册表」集合比对
  - **Acceptance Criteria Addressed**: AC-6（范围仅限 `projects/xuanspace`）、AC-7（门禁不回归且**增强**）
  - **Test Requirements**:
    - `rule` TR-23.1: `check_declaration_consistency.py` 退出码 = 0（六类全通过，含新增的 `cli/index.md` 覆盖）
    - `rule` TR-23.2: 负向回归（内存预演，不动磁盘文件）——将 `cli/index.md` 内存副本移除 `xs archive` 行后重跑 `run_checks`，失败项含 `doc/cli/index.md 命令总览 与事实不一致（声明缺：['archive']；声明多：[]）`，证明新断言有效
    - `rule` TR-23.3: `check-links.py --path doc`（cwd = `projects/xuanspace`）退出码 = 0（19 个 Markdown 文件、35 处本地引用全有效）
    - `rule` TR-23.4: `sphinx -b html doc doc/_build/probe5` 构建成功、无 WARNING/ERROR、无 orphan 警告
    - `rule` TR-23.5: 残留检索 `dependency-report|dependency_report` 全仓命中 = **0**
    - `rule` TR-23.6: `xs meta validate` 报出条目**无一条**落在 `doc/` 或 `.meta/`（122 项均为 `libs/caffe-ffi`、`libs/mystx`、`vendor/caffe`、`tools/okf/tests/fixtures` 既有问题）
    - `rule` TR-23.7: 变更面恰为 5 项（两删除 + `doc/index.md`、`doc/cli/index.md`、`scripts/check_declaration_consistency.py` 修改）

## 提交记录（证据，第十二轮）

| 仓库 | 提交 | 说明 |
|---|---|---|
| `projects/xuanspace` | `72898a2` | `docs(xuanspace): 删除失效的依赖报告并补全 CLI 参考与门禁覆盖`（5 文件，+53/−143） |
| 根仓 | `ROOT_COMMIT_PLACEHOLDER` | `chore(xuanspace): 前移子模块指针并回写文档易腐性清理证据`（`tasks.md` + `review.md` + gitlink） |

> 未 push、未 tag。本轮 `projects/xuanspace` 工作树仅含本轮 5 项变更。
