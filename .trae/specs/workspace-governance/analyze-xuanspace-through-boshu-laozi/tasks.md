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
