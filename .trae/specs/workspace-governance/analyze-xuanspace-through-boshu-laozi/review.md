---
status: "draft"
title: "从帛书《老子》视角分析 Xuanspace 并产出项目蓝图与优化建议书 - 独立审查清单"
change-id: "analyze-xuanspace-through-boshu-laozi"
---

# 独立审查清单（Review）

> 对应规格：[spec.md](spec.md) ｜ 实施计划：[tasks.md](tasks.md)
> 用法：实施完成后逐项核验，通过者勾选；未通过者回到 tasks.md 追加修复任务。

## 一、交付物存在性（AC-1）

- [x] 《项目蓝图》文档存在于 `projects/xuanspace/doc/` 且内容非空
- [x] 《优化建议书》文档存在于 `projects/xuanspace/doc/` 且内容非空
- [x] 两份文档均**未添加** YAML frontmatter、以 H1 开头
- [x] 未新建任何 `.meta/toml/` 元数据文件（AC-1 / FR-11 / C-3）

## 二、导航与构建（AC-2 / NFR-2）

- [x] `projects/xuanspace/doc/index.md` 已新增 toctree 分组并登记两份文档
- [x] 现有四个 toctree 的条目与顺序未被破坏
- [x] Sphinx HTML 构建成功
- [x] 构建日志中无指向两份新文档的 orphan / 未收录 warning

## 三、哲学纪律（AC-3 / FR-8）

- [x] 每处《老子》引文均标注版本（马王堆甲本／乙本／今本／郭店楚简本之一）
- [x] 全文无笼统「帛书本」式的引文版本表述（检索命中 0）
- [x] 甲本损掩处已显式标注
- [x] 抽查 ≥3 处引文与 `projects/awesome-okf-xs/doc/bundles/guoxue/laozi/**` 正文逐字一致
- [x] 「道—法—术—器」解构处显式声明「结构类比，非影响关系」，无「老子早就说了」式附会表述

## 四、溯源与事实（AC-4 / FR-9）

- [x] 存在事实清单，条数 ≥25
- [x] 事实清单无因果推断词（因为/导致/因此/所以/使得/从而）——检索命中 0
- [x] 抽查 ≥8 条现状事实陈述，全部带相对路径引用且引用真实存在
- [x] 三条声明一致性线索（`docs/` vs `doc/`、`xs` 子命令数、doc 目录树）**均先核验后使用**，未核验前未作为缺陷断言

## 五、《项目蓝图》质量（AC-8 / AC-11 / FR-1 / FR-2 / FR-6 / FR-7）

- [x] 结构完整：项目定位 → 道—法—术—器四层解构 → 现状能力地图 → 三之位诊断 → 目标态蓝图 → 演进路线
- [x] 四层解构逐层给出「对应实体（带引用） + 承载功能 + 薄弱环节」
- [x] 「三之位」诊断五步齐备（命名二／找关系位／检验非实体性／表述为关系／落地动作）
- [x] 显式命名并规避 ≥1 个反模式
- [x] 「三问检验」自查结果已写入
- [x] rubric 评分：四层解构深度 ≥4（1-5）

## 六、《优化建议书》质量（AC-5 / AC-9 / FR-3 / FR-4 / FR-12）

- [x] 建议按 P0/P1/P2 分级，优先级依据明确
- [x] 每条建议五要素齐备：判据 + 现状证据（相对路径 `#L起-L止`）+ 期望态 + 落地动作 + 验证方式
- [x] 无「正确的废话」条目；每条均可判定为「已做/未做」
- [x] 未在本次落地任何建议（仅产出建议）
- [x] rubric 评分：可执行性与判据强度 ≥4（1-5）

## 七、洞察质量（AC-10 / FR-5）

- [x] 洞察 ≥3 条，每条为完整四元组（陈述 + 证据 + 反常识 + 行动）
- [x] 洞察维度互不重叠
- [x] ≥2 条洞察挑战默认假设
- [x] 每条「反常识点」均有事实支撑
- [x] rubric 评分：洞察质量与反常识性 ≥4（1-5）

## 八、门禁与边界（AC-6 / AC-7 / NFR-3 / NFR-4 / NFR-5）

> **断言范围**：本节涉及 commit / push / tag 的检查项，范围是**本规格任务的实施过程**（Task 1–7）。规格完成后经用户另行授权落地 P0-1 所产生的提交，记于文末「十、P0-1 落地证据」——本节原始记录不回改。

- [x] `check-links.py` 对新增/修改文件报告 0 断链
- [x] `check_mermaid.py` 校验通过（如含 Mermaid）
- [x] 文档内交叉引用全部为相对路径，无 `file:///`，无 `.temp/` 引用
- [x] `projects/xuanspace` 的 `git status` 变更仅限 `doc/`（两份新文档 + `index.md`）
- [x] `projects/xuanspace` 的 HEAD 与 Task 1 记录的基线一致（`git log -1`），无新增 commit
- [x] 未执行 push / tag
- [x] `projects/awesome-okf-xs` 零变更
- [x] 未回滚或覆盖任何既有他人改动

## 九、语言与可读性（NFR-1 / NFR-6）

- [x] 两份文档均为简体中文；术语在全篇一致
- [x] 标题层级不跳级；表格分隔符与列数一致
- [x] 代码、路径、命令保留英文原样

---

## 核验证据（Task 7 留存）

| 检查项 | 命令 / 方法 | 结果 |
|---|---|---|
| 交付物存在性 | 检查 `projects/xuanspace/doc/` 下 `blueprint.md`、`recommendations.md` | 均存在、以 H1 开头、无 YAML frontmatter；未新建 `.meta/toml/` |
| Sphinx 构建 | `python -m sphinx -b html doc doc/_build/html`（cwd = `projects/xuanspace`） | `构建成功。`，无 WARNING / ERROR；`blueprint.html`、`recommendations.html` 均已产出 |
| 链接门禁 | `python .agents/scripts/check-links.py --path doc`（cwd = `projects/xuanspace`） | 两份新文档 **0 断链**；目录内 33 个断链均为存量（`intro.md`、`quickstart.md`、`okf/*.md`） |
| Mermaid 门禁 | `python .agents/scripts/repo-check.py mermaid --path <临时目录副本>` | `扫描文件: 2, 问题文件: 0, 错误: 0, 警告: 0`，通过 |
| AC-3 版本纪律 | `Select-String -Pattern '帛书本'` 于 `doc/*.md` | 命中 **0** |
| 事实清单 | `blueprint.md` 附录「事实清单（R 阶段）」 | 45 条（≥25），每条带相对路径引用；因果词检索命中 **0** |
| 引文逐字对照 | 比对 `guoxue/laozi/boshu-reading/concepts/04-key-variants.md`、`guoxue/laozi/laozi-works/text/boshu-jia.md`、`guoxue/laozi/laozi-lineage/variants/taboo-heng-chang.md` | 「道可道也，非恒道也」「甲本此句残」「避讳『恒』→『常』」三处一致 |
| 边界核对（xuanspace） | `git status --short` / `git log -1` | ` M doc/index.md`、`?? doc/blueprint.md`、`?? doc/recommendations.md`；HEAD `8db593d` 未变 |
| 只读边界（awesome-okf-xs） | `git status --short` | 16 项均为本次会话之前的既存变更，本次零写入 |
| 禁止项 | 检查 git 历史 | 未执行 commit / push / tag |

> 门禁脚本的已知环境约束：`.agents/scripts/constants.py` 的 `EXCLUDED_DIRS` 含 `projects`，故对 `projects/xuanspace` 的扫描须在 xuanspace 内以相对路径执行（链接检查），或复制到不含 `projects` 的临时目录后执行（Mermaid 检查）。

## 十、P0-1 落地证据（规格完成后追加）

> 范围：规格完成后经用户另行授权执行的《优化建议书》**P0-1**（统一根文档目录命名口径为 `doc/`）落地。对应 tasks.md 的 Task 8。本节为独立审查记录，不改写一至九节的原始验收结果。

### 10.1 交付物与提交

| 仓库 | 提交 | 变更规模 |
|---|---|---|
| `projects/xuanspace` | `207256c` refactor(xs): 重命名 docs 子命令为 doc 并对齐仓库目录约定 | 16 文件，52 insertions / 52 deletions（BREAKING） |
| `projects/xuanspace` | `aed2e5b` refactor(xs): 重命名 docs_cmd 模块为 doc_cmd 并统一函数名前缀 | 3 文件，13 / 13，`rename ... (94%)` |
| `projects/xuanspace` | `cc5c5b1` docs(changelog): 补记 xs doc 改名的破坏性变更 | 1 文件，+7 |
| 根仓 `SpecWeave` | `b86f2a98e` chore(submodule): 更新 xuanspace 子模块指针至 cc5c5b1 | 1 文件，+1 / −1（仅 gitlink） |

未 push、未 tag。

### 10.2 门禁与核验

| 检查项 | 命令 / 方法 | 结果 |
|---|---|---|
| CLI 注册表 | `from xs.cli import app` → `[g.name for g in app.registered_groups]` | `['toolchain','deps','doc','version','meta','archive','lfs']`；`has doc: True`、`has docs: False` |
| 模块解析 | `import xs.commands.doc_cmd` | `...\commands\doc_cmd.py`（非 `docs_cmd`） |
| 子命令可用 | `python -m xs.cli doc --help` | exit=0；`build` / `serve` / `clean` / `linkcheck` 四子命令齐备 |
| 符号可达 | 导入 `doc_build`/`doc_serve`/`doc_clean`/`doc_linkcheck`/`_get_docs_dir` | 全部可导入；`_get_docs_dir(...)` → `projects\xuanspace\doc` |
| 残留引用 | `rg 'docs_cmd\|docs_app\|docs_build\|docs_serve\|docs_clean\|docs_linkcheck'`（xuanspace 全仓） | **命中 0** |
| 单元测试 | `pytest tests -q`（`PYTHONPATH=tools/xs/src`） | `1 failed, 20 passed`；失败项 `test_check_python_version` 为**环境性**（本机 Python 3.14.3 < 仓库要求 3.14.6），改动前即失败 |
| 断链门禁 | `check-links.py --path doc`（cwd = `projects/xuanspace`） | 本地 33 / 外部 0，与改动前基线一致，**0 新增** |
| Mermaid 门禁 | `repo-check.py mermaid` 不覆盖子模块内文件（按主仓 git 索引扫描），改以人工核对块边界 | `doc/` 下 3 处 mermaid 块（`dependency-report.md:50`、`blueprint.md:108`、`architecture.md:7`）与本次改动行**均不相交**，0 新增 |
| 保留项未误改 | 检查 `_get_docs_dir` / `("doc","docs")` 兼容回退 / 变量名 `docs_dir` | 全部保留（其语义为「目录集合」而非「命令名」） |
| 边界核对（xuanspace） | `git status --short` / `git submodule status` | 提交后工作树清空；`libs/mystx`、`libs/tvm-book`、`vendor/caffe`、`vendor/tvm-ffi` 四子模块指针干净 |
| 边界核对（根仓） | `git ls-tree HEAD projects/xuanspace` / `git submodule status projects/xuanspace` | gitlink = `cc5c5b1356...`，与子模块 HEAD 一致 |

### 10.3 过程发现（反模式记录）

**`git commit -- <paths>` 无法提交 rename 的旧路径。**

- **现象**：以 `git-commit-utf8.py <点名路径>` 提交「重命名 + 内容修改」时，工作树虽已 `git add`，但提交后旧文件仍以 `D` 状态残留于暂存区。
- **复现**（沙箱，`$TEMP\gitpathspec-probe`）：
  - `git mv a.py b.py` → 改 `b.py` → `git add b.py` → `git commit -- b.py` → 结果 `A b.py`，并残留 `D  a.py`（旧路径未进提交）。
  - 改为 `git commit -- a.py b.py` → 结果 `D a.py` 被正确记录。
- **根因**：`git commit -- <paths>` 的语义是「**HEAD + 点名路径的工作树态**」；未点名的暂存**删除**不进入本次提交。而 `git add <旧路径>` 会因文件不存在报错，故工具的 `check_staged_matches`（对 rename 只列新路径的 `--name-only` 做集合等值校验）无法与含旧路径的点名列表同时满足。
- **处置**：先显式 `git add` 三个目标路径 → 以 `git diff --cached --name-status` 核验暂存集恰为 `M / M / R094` → 再以 UTF-8 消息文件经 bytes 通道提交该索引；提交后用 `git show --name-status` 复核 rename 成立。
- **可迁移纪律**：**涉及重命名（删除+新增）的原子提交，不能用「只点名新路径」的 path 级提交**；须把旧路径一并纳入 pathspec，或改为「核验暂存集后提交整索引」。

## 十一、P0-1 主体 + P0-2/P0-3 落地证据（规格完成后追加，第二轮）

> 范围：规格完成后**第二轮**经用户另行授权执行的《优化建议书》落地——P0-1 主体的文档级 7 处引用、P0-2（`apps/` 与 `apps/xs-cli/` 失实声明）、P0-3（上游子模块数 3→4），以及同源残余引用清理。对应 tasks.md 的 Task 9–13。本节为独立审查记录，不改写一至十节的原始验收结果。

### 11.1 交付物与提交

| 仓库 | 提交 | 变更规模 |
|---|---|---|
| `projects/xuanspace` | `d681e4c` refactor(doc): 补齐根文档目录命名漂移的 7 处引用 | 6 文件，+7 / −7 |
| `projects/xuanspace` | `349afa6` docs(xuanspace): 修正 apps/ 与上游子模块数量的失实声明 | 4 文件，+12 / −8（P0-2 + P0-3） |
| `projects/xuanspace` | `edce88f` docs(xuanspace): 清理 apps/xs-cli 残余引用 | 2 文件，+1 / −3 |
| 根仓 `SpecWeave` | `abc724559` chore(submodule): 更新 xuanspace 子模块指针至 edce88f | 1 文件，+1 / −1（仅 gitlink） |

未 push、未 tag。子模块 HEAD 最终为 `edce88f4a3bd96cf3fe7761383d0dbd08937df7c`，根仓 gitlink 与之对齐（`abc724559`）。

### 11.2 门禁与核验

| 检查项 | 命令 / 方法 | 结果 |
|---|---|---|
| P0-1 目标清零 | 白名单 `rg -n "docs/" --hidden --glob '!vendor/**' --glob '!libs/**' --glob '!.git/**' --glob '!.trae/**' --glob '!attic/**' --glob '!doc/blueprint.md' --glob '!doc/recommendations.md'`（cwd = xuanspace） | 目标 7 处**全清零**；剩余 8 行全部落排除项（`doc_cmd.py:21/24`、`doctor_cmd.py:200/210` 兼容实现、`CONTRIBUTING.md:316` 分支命名 `docs/<name>`、`CHANGELOG.md:12/19` 历史记录、`tests/test_doctor_sphinx.py:19` 兼容注释） |
| `--hidden` 必要性 | 上述扫描含 `.agents/` 下 1 处命中 | 该处（`.agents/ONBOARDING.md`）须 `--hidden` 方可扫到——正是本项目记录的失效模式 |
| P0-3 数字 | `rg -n "3 个上游子模块" CONTRIBUTING.md` | rc=1（**无命中**） |
| P0-3 事实源 | `git config -f .gitmodules --get-regexp '^submodule\..*\.path'` | 4 条（`vendor/tvm-ffi`、`libs/tvm-book`、`vendor/caffe`、`libs/mystx`） |
| 磁盘事实（P0-2 依据） | 列 `apps/` 目录 | 仅 `.gitkeep` + `README.md`，「当前为空目录」成立 |
| 残余引用 | `rg -n "apps[\\/]xs-cli" --hidden --glob '!.git/**'`（cwd = xuanspace） | 剩余命中仅为否定式表述（`tools/README.md:32`）、建议书原文（`doc/recommendations.md:66/67`）、历史归档（`attic/README.md:178`） |
| 断链门禁 | `check-links.py --path .`（cwd = `projects/xuanspace`） | 128 处**均为存量**（集中 `libs/caffe-ffi/docs/`、`doc/okf/`）；本轮改动 4 文件 **0 新增** |
| Sphinx 构建 | `python -m sphinx -b html doc doc/_build/html -q --keep-going`（cwd = xuanspace） | rc=0 |
| 边界核对（xuanspace） | `git status --short` | 提交后工作树为空（干净） |
| 边界核对（根仓） | `git diff --submodule=short` / `git ls-tree HEAD projects/xuanspace` | gitlink 前移至 `edce88f`，与子模块 HEAD 一致 |

> 门禁脚本环境约束（与第十节同源）：`.agents/scripts/constants.py` 的 `EXCLUDED_DIRS` 含 `projects`，故从根仓以 `--path projects/xuanspace` 调用 `check-links.py` 会扫到 **0 个文件**；须在 `projects/xuanspace` 内以 `--path .` 执行。

### 11.3 同源残余发现

Task 10 收敛 `apps/xs-cli/` 主引用后，`rg` 发现同源残余两处，改由 Task 12 一并清理（随 `edce88f` 落地）：

- `CONTRIBUTING.md` §4.2（L273）与 §4.3（L288）：`uv pip install -e apps/xs-cli` / `pip install -e apps/xs-cli` ——照抄会失败（路径不存在），且与紧邻的 `-e tools/xs` 重复。
- `.agents/context-routing.md#L20`：routing 表中 `[../apps/xs-cli/]` 为失效链接。

退化的排除项（**不改**，语义不同或属历史）：`tools/README.md:32` 的否定式表述（「不存在 `apps/xs-cli/` 包装层」）、`doc/recommendations.md:66/67` 的建议书原文、`attic/README.md:178` 的历史归档。

## 十二、规格收口与看板登记证据（第三轮，纯登记性）

> 范围：不新增分析内容，仅收口本规格——勾选已实际解决的 Open Questions，并补齐**创建时遗漏**的看板登记（`.trae/specs/README.md`「新增 Spec 指南」第 5 步）。对应 tasks.md 的 Task 14。本节为独立审查记录，不改写一至十一节的原始验收结果。

### 12.1 交付物

| 文件 | 变更 |
|---|---|
| `analyze-xuanspace-through-boshu-laozi/spec.md` | Open Questions 5 条 `- [ ]` → `- [x]` 并各附结论 |
| `analyze-xuanspace-through-boshu-laozi/tasks.md` | 追加 Task 14 + 第三轮提交记录 |
| `analyze-xuanspace-through-boshu-laozi/review.md` | 追加本节（第十二节） |
| `.trae/specs/workspace-governance/README.md` | marker 区新增第 3 行（本规格），30 → 31 行；表头 `**Spec 数量**：29` → `31` |
| `.trae/specs/okf-wiki-ecosystem/README.md` | 连带刷新：marker 区新增 1 行（`create-contest-writing-guide`），全表序号后移 1 |
| `.trae/specs/README.md` | 全局看板：workspace-governance 30 → 31、okf-wiki-ecosystem 214 → 215、合计 738 → 740；生成日期 2026-10-26 → 2026-10-27 |

### 12.2 门禁与核验

| 检查项 | 命令 / 方法 | 结果 |
|---|---|---|
| 主题看板登记 | `docgen.py theme-dashboards`（cwd = 根仓） | `workspace-governance（31 spec）`；本规格登记于第 3 行（字母序） |
| 主题看板行数 = 表头 | `Read` 逐行核对 marker 区 | 31 行（序号 1–31），与表头 `**Spec 数量**：31` 一致 |
| 全局看板计数 | `docgen.py update-spec-readme` | 本主题 30 → 31；合计 738 → 740（740 = 738 + 本规格 + 并行的 `create-contest-writing-guide`） |
| 未回改既有记录 | `git diff --stat` | 一至十一节验收表**零改动**；改动仅限 Open Questions、两处追加小节与看板 |
| 边界核对 | `git status --short` | 根仓仅本轮 4 个具名文件（+ 无关 `?? .creative-design/`）；`projects/xuanspace` 的 `M src/xuanspace/__init__.py` 为**并行会话在途改动**，本轮未触碰、未提交 |

### 12.3 连带 diff 的处置判断

`docgen.py theme-dashboards` 全量扫描 50 个主题后，仅 2 个主题 README 产生 diff：本篇所属 `workspace-governance`（本规格登记）与 `okf-wiki-ecosystem`（注册并行会话已提交但未登记的 `create-contest-writing-guide`，纯插入 1 行 + 全表序号后移，无内容改写）。

纳入本轮的理由（非扩权，而是**一致性强制**）：

- 全局看板 `.trae/specs/README.md` 的同一表格内**同时**含 `workspace-governance` 与 `okf-wiki-ecosystem` 两行计数，无法按 hunk 拆分；若只提交其一，两级看板将互相矛盾。
- 且下一轮 `docgen` 会再次写回同一结果，回退该行反而制造新的漂移。

故 6 个文件作**单一原子提交**（三件套 spec/tasks/review + 两级看板 README + okf 主题看板连带刷新）；未触碰其余 11 个主题 README（无 diff，天然幂等）。

## 十三、P1/P2 落地证据（规格完成后追加，第四轮）

> 范围：规格完成后**第四轮**经用户另行授权执行的《优化建议书》落地——P1（一致性缺口）的 P1-1/P1-2/P1-3/P1-4/P1-6 与 P2（精确化）的 P2-1/P2-2/P2-3/P2-4，共 9 项。对应 tasks.md 的 Task 15。本节为独立审查记录，不改写一至十二节的原始验收结果。

### 13.1 交付物与提交

| 仓库 | 提交 | 变更规模 |
|---|---|---|
| `projects/xuanspace` | `4c9a346` docs(xuanspace): 对齐文档与实现的一致性缺口与精确化（P1/P2） | 8 文件，+54 / −11 |
| 根仓 `SpecWeave` | `d0d531e2c` chore(xuanspace): 前移子模块指针至 4c9a346（文档一致性 P1/P2 落地） | 1 文件，+1 / −1（仅 gitlink） |

未 push、未 tag。子模块 HEAD 为 `4c9a3467a30e35cb820bb9784cec19593d2e31e6`，根仓 gitlink 与之对齐。

涉及文件（8）：`doc/intro.md`、`doc/architecture.md`、`README.md`、`libs/README.md`、`tools/README.md`、`.meta/README.md`、`.agents/rules/frontmatter.md`、`AGENTS.md`。

### 13.2 逐项对照

| 条款 | 落地文件 | 变更要点 |
|---|---|---|
| P1-1 统一 CLI 命令清单口径 | `doc/intro.md` | 命令表补 `xs archive` / `xs lfs` / `xs affected`，12 → 15 一级项 |
| P1-2 同步依赖声明示例 | `doc/architecture.md` | `docs` 示例 2 → 6 项；显式 `test`/`lint`/`build`；`dev` 由 `xuanspace[...]` 引用式改 `[dependency-groups]` 展开式 |
| P1-3 统一 scikit-build-core 下限 | `libs/README.md` | `>=0.5` → `>=0.11` |
| P1-4 「现有子项目」清单 | `libs/README.md`、`tools/README.md`、`README.md` | libs 2 → 8 项（附免责注）；tools 补 `native-ffi/`；README 项目索引 9 → 13 行 |
| P1-6 元数据规范冲突 | `.meta/README.md`、`.agents/rules/frontmatter.md` | 新增「当前阶段冻结」节；补 Task 20 解冻触发条件 |
| P2-1 引文补版本标注 | `doc/intro.md` | 标注传世本（王弼本系统）并给甲/乙本对照 |
| P2-2 上下文漂移 | `doc/architecture.md` | 「SpecWeave 主仓库」→「上层工作区」 |
| P2-3 mypy 范围口径 | `AGENTS.md` | 补「范围以 CI 为准（`tools/xs libs/xuan-core libs/xuan-ext-demo`）」 |
| P2-4 Mermaid 重名节点 | `README.md` | `Conventions[AGENTS.md]` → `AgentsMd[AGENTS.md]` |

### 13.3 门禁与核验

| 检查项 | 命令 / 方法 | 结果 |
|---|---|---|
| 断链门禁 | `check-links.py --path .`（cwd = `projects/xuanspace`） | rc=1；127 处**均为存量**（MyST 无扩展名交叉引用 `doc/intro.md:68-71`、`libs/caffe-ffi` 跨仓链接、目录链接警告）；本轮 8 文件 **0 新增** |
| Mermaid 门禁 | `check_mermaid.py` | **不适用**——该脚本硬编码无关路径（`04-architecture.md`），执行报 `FileNotFoundError`；改以人工核对：P2-4 节点重名已消除，`doc/` 内 3 处 mermaid 块与改动行不相交 |
| 命令表口径 | 核对 `doc/intro.md` 表行数 | 15 行，与 `cli.py`（7 组 + 8 直接命令）一致 |
| 版本下限 | `rg "scikit-build-core>=" libs/ tools/ pyproject.toml` | 全仓 `>=0.11`，示例同步后一致 |
| 边界核对（xuanspace） | `git status --short` | 提交后 5 项 dirty 全为**并行会话在途改动**（`.gitignore`/`pyproject.toml`/`__init__.py`/`version_cmd.py`/`discovery.py`），本轮未触碰 |
| 边界核对（根仓） | `git ls-tree HEAD projects/xuanspace` | gitlink = `4c9a346`，与子模块 HEAD 一致 |

### 13.4 未落项与后续

- **P1-4 期望态的「生成物 / 断言对象」形式未实现**：本轮按「补全清单 + 免责注」最小实现落地（清单与磁盘一致），期望态给出的两条路径（① 生成标记由脚本注入；② 在 P0-4 检查中增加「清单条目 ⊆ 磁盘目录」断言）**均未实现**，作为后续项。
- **建议书文末的存量陈述**：`doc/recommendations.md` 文末仍写「本轮不执行任何建议项，仅提出清单」——该句在 P0/P1/P2 陆续落地后已与事实不符。本轮范围锁定为「规格三件套 + 看板」，未扩权修改建议书本体，此句留待后续统一处置。

## 十四、P0-4 落地证据（规格完成后追加，第五轮）

> 范围：规格完成后**第五轮**经用户另行授权执行的《优化建议书》**P0-4**（建立「声明—实现一致性」门禁）落地。P0-4 是建议书中最后一个未落地的 P0 项。对应 tasks.md 的 Task 16。本节为独立审查记录，不改写一至十三节的原始验收结果。

### 14.1 交付物与提交

| 仓库 | 提交 | 变更规模 |
|---|---|---|
| `projects/xuanspace` | `2750078` ci(xuanspace): 新增声明—实现一致性门禁（P0-4） | 4 文件，+304 / −5 |
| 根仓 `SpecWeave` | `3a6d95193` chore(xuanspace): 前移子模块指针至 2750078 并回写 P0-4 落地证据 | 3 文件，+78 / −1（gitlink + 本规格 `tasks.md`/`review.md`） |

未 push、未 tag。子模块 HEAD 为 `2750078e2386ee4efd3e09c0a3155bd43abaffd4`，根仓 gitlink 与之对齐。

新增/变更文件（4）：`scripts/check_declaration_consistency.py`（新）、`scripts/declaration-snapshot.json`（新）、`.github/workflows/ci.yml`、`scripts/README.md`。

### 14.2 三类声明覆盖与实现要点

| 类别 | 声明源 | 事实源 | 断言 |
|---|---|---|---|
| A. CLI 命令清单 | `README.md`「N 个子命令」；`doc/intro.md`「项目状态」命令表 | `tools/xs/src/xs/cli.py` 注册表（`app.add_typer(..., name=)` + `app.command("...")`） | 计数相等 + 命令名集合双向相等 |
| B. 子项目清单 | `libs/README.md`「现有子项目」表 | `libs/` 磁盘目录（忽略隐藏项与 `__pycache__`/`.git`/`node_modules`） | 集合双向相等（即 P1-4 遗留的「清单 ⊆ 磁盘」断言之实现） |
| C. 目录名口径 | `README.md`「目录结构」围栏块声明的顶层目录 | 磁盘目录存在性 | 声明目录均存在 + 顶层禁 `docs/` + 必有 `doc/` |

- 双模式：默认**校验模式**（退出码 0 / 1 / 2）；`--generate` **生成模式**写 `scripts/declaration-snapshot.json` 快照；`--json` 结构化输出。
- 校验模式末尾额外比对快照：磁盘事实若与已提交快照不一致即失败（提示 `--generate` 刷新），从而把「实现变更未同步声明」也纳入门禁。
- 脚本自包含（不导入 `libs/`/`apps/` 内部包），符合 `scripts/README.md` §6；共享库 `SpecWeave/.agents/scripts/lib/` 不在本仓内、单仓 CI 检出不可导入，仅镜像其表格解析思路（详见脚本 docstring）。

### 14.3 门禁与核验

| 检查项 | 命令 / 方法 | 结果 |
|---|---|---|
| **验收动作（正）** | `README.md`「15 个子命令」→「14」，`python scripts/check_declaration_consistency.py` | 退出码 **1**；输出「README.md 声明 14 个子命令，tools/xs/src/xs/cli.py 实际注册 15 个」 |
| **验收动作（反）** | 改回「15」后重跑 | 退出码 **0**；「声明与实现一致：CLI 命令清单 / 子项目清单 / 目录名口径 全部通过。」 |
| 生成模式幂等 | `--generate` 连跑两次 | 首次刷新快照；第二次「清单快照已是目标状态，跳过」，退出码 0 |
| 快照内容 | `Read scripts/declaration-snapshot.json` | 15 命令 + 8 子项目，与 `cli.py` 注册表、`libs/` 磁盘一致 |
| 静态检查 | `ruff check scripts/`、`ruff format --check scripts/` | `All checks passed!`、`2 files already formatted` |
| 断链门禁 | `check-links.py --path .`（cwd = `projects/xuanspace`） | rc=1；127 处**均为存量**（与第四轮基线一致），本轮 4 文件 **0 新增** |
| 事实源未受并行改动影响 | `git diff -- tools/xs/src/xs/cli.py` | 并行会话改动仅涉导入与版本解析（`_dist_version` 回退），**未触及** `add_typer`/`command` 注册行；15 个一级项在 HEAD 与工作树一致 |
| 边界核对（xuanspace） | `git status --short` | 提交后剩余 8 项 dirty 全为**并行会话在途改动**（`.gitignore`/`pyproject.toml`/`__init__.py`/`tools/xs/README.md`/`tools/xs/src/xs/{__init__,cli}.py`/`version_cmd.py`/`discovery.py`），本轮未触碰 |
| 边界核对（根仓） | `git ls-tree HEAD projects/xuanspace` | gitlink = `2750078`，与子模块 HEAD 一致 |

### 14.4 遗留与后续

- **建议书文末的存量陈述**（承 13.4）：`doc/recommendations.md` 文末「本轮不执行任何建议项，仅提出清单」仍未处置；本轮范围锁定为「脚本 + 快照 + CI + 规格三件套」，未扩权修改建议书本体。
- **P1-4 期望态的第 ① 条**（生成标记由脚本注入文档）仍未实现；第 ② 条（清单 ⊆ 磁盘目录断言）已由本轮的 B 类断言覆盖（见 14.2）。

## 十五、建议书文末陈述收口证据（规格完成后追加，第六轮）

> 范围：规格完成后**第六轮**经用户另行授权执行的收口——处置《优化建议书》文末在 P0/P1/P2 落地后已失真的存量陈述。对应 tasks.md 的 Task 17。本节为独立审查记录，不改写一至十四节的原始验收结果。

### 15.1 交付物与提交

| 仓库 | 提交 | 变更规模 |
|---|---|---|
| `projects/xuanspace` | `d2dc124` docs(xuanspace): 修正建议书文末与落地事实不符的存量陈述 | 1 文件（`doc/recommendations.md`） |
| 根仓 `SpecWeave` | `4b538fa72` chore(xuanspace): 前移子模块指针并回写建议书收口证据 | 3 文件（`tasks.md` + `review.md` + gitlink） |

未 push、未 tag。

### 15.2 处置前后对照

| 项 | 处置前 | 处置后 |
|---|---|---|
| `doc/recommendations.md` 文末末句 | 「本轮不执行任何建议项，仅提出清单。」 | 列明已闭环项（P0-1~P0-4、P1-1~P1-4 与 P1-6、P2-1~P2-4；P1-5 随「文档入口合并」消解）并指向根仓本主题规格三件套 |

**失真成因**：该句为建议书产出批次（`sc-20261027-xuanspace-boshu-blueprint`）写就时的历史状态陈述；此后 P0/P1/P2 经第一至第五轮陆续落地，该句未同步，遂与事实不符。前两轮（§13.4 / §14.4）均已登记为「留待后续统一处置」，本轮处置。

### 15.3 门禁与核验

| 检查项 | 命令 / 方法 | 结果 |
|---|---|---|
| 失真陈述清零 | `rg "本轮不执行任何建议项" doc/`（cwd = `projects/xuanspace`） | 命中 **0** |
| 断链门禁 | `check-links.py --path .`（cwd = `projects/xuanspace`） | 本轮 1 文件 **0 新增**（127 处为存量） |
| 边界核对（xuanspace） | `git status --short` | 除本轮 1 文件外，其余 dirty 全为**并行会话在途改动**，本轮未触碰 |
| 边界核对（根仓） | `git ls-tree HEAD projects/xuanspace` | gitlink = 子模块 HEAD |

### 15.4 遗留与后续

- **P1-4 期望态的第 ① 条**（生成标记由脚本注入文档）仍未实现（承 §14.4）；第 ② 条已由第五轮 B 类断言覆盖。
- 本轮为该规格的纯收口轮次，P0/P1/P2 已全量闭环；除上述 P1-4 ① 外，建议书无剩余可执行项。

## 十六、P1-4① 落地与建议书彻底精简证据（规格完成后追加，第七轮）

> 范围：规格完成后**第七轮**经用户另行授权执行的工作——① P1-4 期望态第 ① 条（清单改由脚本注入的生成块派生）；② 按用户指令彻底清空 `doc/recommendations.md` 中全部已闭环条目。对应 tasks.md 的 Task 18。本节为独立审查记录，不改写一至十五节的原始验收结果。

### 16.1 交付物与提交

| 仓库 | 提交 | 变更规模 |
|---|---|---|
| `projects/xuanspace` | `fc4fe25` refactor(xuanspace): libs 子项目清单改由脚本生成块派生 | 3 文件（`scripts/check_declaration_consistency.py` + `libs/README.md` + `scripts/README.md`，+96 / −34） |
| `projects/xuanspace` | `f9e2b2c` docs(xuanspace): 优化建议书移除已闭环条目并收口为终态 | 1 文件（`doc/recommendations.md`，+2 / −166） |
| 根仓 `SpecWeave` | `f92d2ebe1` chore(xuanspace): 前移子模块指针并回写 P1-4① 落地证据 | 3 文件（`tasks.md` + `review.md` + gitlink） |

未 push、未 tag。子模块 HEAD 为 `f9e2b2cde2c04055dd58026b7c38d168e2ce274a`，根仓 gitlink 与之对齐。

### 16.2 生成块设计（P1-4①）

| 要素 | 内容 |
|---|---|
| 标记 | `libs/README.md` 清单块由 `<!-- BEGIN GENERATED: libs-projects -->` / `<!-- END GENERATED: libs-projects -->` 包裹，块内禁止手改 |
| 单一事实源 | 「类型 / 说明」迁入脚本内嵌映射 `LIB_PROJECT_META`（8 项）；目录名集合由 `libs/` 磁盘派生——手写真源清零 |
| 门禁升级 | 由「比对条目集合」升级为「**块内容 == 脚本渲染结果**」；`LIB_PROJECT_META` 缺登记项亦判失败 |
| 生成 | `--generate` 重写该块（幂等），与快照刷新合并为同一命令 |

### 16.3 门禁与核验

| 检查项 | 命令 / 方法 | 结果 |
|---|---|---|
| 校验模式 | `python scripts/check_declaration_consistency.py` | 退出码 **0**；「声明与实现一致：CLI 命令清单 / 子项目清单 / 目录名口径 全部通过。」 |
| 负向探针 | 新建 `libs/probe-tmp/` 后重跑 | 退出码 **1**；三项报错（生成块缺元数据登记 / 生成块已过期 / 快照 `lib_projects` 已过期）；探针已清理 |
| 生成模式幂等 | `--generate` 连跑两次 | 「清单快照已是目标状态，跳过」+「生成块已是目标状态，跳过」，退出码 0 |
| 结构化输出 | `--json` | `{"ok": true, "failures": [], "notes": []}` |
| 静态检查 | `ruff check scripts/check_declaration_consistency.py` | `All checks passed!` |
| 断链门禁 | `check-links.py --paths doc libs scripts`（cwd = `projects/xuanspace`） | rc=1；127 处**均为存量**（集中在 `libs/caffe-ffi/docs`、`libs/mystx/doc` 与 `doc/okf`），本轮 4 文件 **0 新增** |
| 行号引用一致性 | 核对 `recommendations.md` 曾引用的两处 `#L` 区间 | `check_declaration_consistency.py#L207-L217`（B 段）与 `libs/README.md#L106-L123`（生成块）均与磁盘一致（收口后该两处引用随条目移除） |
| 边界核对（xuanspace） | `git status --short` | 除本轮 4 文件外，其余 dirty 全为**并行会话在途改动**，本轮未触碰 |
| 边界核对（根仓） | `git ls-tree HEAD projects/xuanspace` | gitlink = 子模块 HEAD |

### 16.4 遗留与后续

- **P1-4 至此完整闭环**——期望态第 ① 条（本轮）与第 ② 条（第五轮 B 类断言）均已落地。
- `doc/recommendations.md` 已收口为「全量闭环、无待办」终态：P0/P1/P2 全部条目及其正文均移除，逐条证据由 git 历史与根仓本主题规格三件套承载。
- 《优化建议书》至此**无剩余可执行项**；本规格亦无遗留任务。

## 十七、声明一致性门禁扩容与残余漂移清理证据（规格完成后追加，第八轮）

> 范围：规格完成后**第八轮**经用户另行授权执行的工作——① `scripts/check_declaration_consistency.py` 由三类断言扩容至**六类**（新增 D vendor 清单、E 子模块声明、F 项目索引）；② 清除两处残余漂移。对应 tasks.md 的 Task 19。本节为独立审查记录，不改写一至十六节的原始验收结果。

### 17.1 交付物与提交

| 仓库 | 提交 | 变更规模 |
|---|---|---|
| `projects/xuanspace` | `fd6d7e6` feat(scripts): 声明一致性门禁扩容至六类断言并清理残余漂移 | 5 文件（`scripts/check_declaration_consistency.py` + `scripts/declaration-snapshot.json` + `doc/architecture.md` + `vendor/README.md` + `.github/workflows/ci.yml`，+149 / −19） |
| 根仓 `SpecWeave` | `8d5872424` chore(xuanspace): 前移子模块指针并回写门禁扩容证据 | 3 文件（`tasks.md` + `review.md` + gitlink） |

未 push、未 tag。子模块 HEAD 为 `fd6d7e6bdc2447b8e027d56b6f4f5f65338c6a55`，根仓 gitlink 与之对齐。

### 17.2 六类断言设计

| 类别 | 声明方（文档） | 事实方（磁盘） | 新增/既有 |
|---|---|---|---|
| A CLI 命令清单 | `README.md`「N 个子命令」+ `doc/intro.md` 命令表 | `tools/xs/src/xs/cli.py` 注册表 | 既有 |
| B 子项目清单 | `libs/README.md` 生成块 | `libs/` 磁盘目录 + `LIB_PROJECT_META` | 既有 |
| C 目录名口径 | `README.md`「目录结构」块 | 磁盘存在性（且顶层不得出现 `docs/`） | 既有 |
| D vendor 清单 | `vendor/README.md`「现有子项目」表 | `.gitmodules` 中 `vendor/` 子模块 | **本轮新增** |
| E 子模块声明 | `CONTRIBUTING.md`「N 个上游子模块」计数与子模块表 | `.gitmodules` | **本轮新增** |
| F 项目索引 | `README.md`「项目索引」表 | `tools/` + `libs/` 磁盘目录 ∪ `vendor/` 子模块 | **本轮新增** |

解析底座：`_section`（按二级标题截取章节正文）+ `_table_first_column`（只解析章节内**首张连续**表格首列，遇非 `|` 行即停，避免误吞同章节后续表格）+ `_GITMODULES_PATH_RE`（解析 `path =` 行）。快照新增 `submodules` 键，`run_checks` 快照比对改为遍历 `manifest` 全键，后续新增事实键自动纳入校验。

### 17.3 门禁与核验

| 检查项 | 命令 / 方法 | 结果 |
|---|---|---|
| 校验模式 | `python scripts/check_declaration_consistency.py` | 退出码 **0**；「声明与实现一致：CLI 命令清单 / 子项目清单 / 目录名口径 / vendor 清单 / 子模块声明 / 项目索引 全部通过。」 |
| 负向探针 | `tempfile` 夹具构造三类漂移后重跑 | **4/4 PASS**——基线（exit 0）+ D（vendor 表删 `caffe` 行，命中「vendor/README.md『现有子项目』表」）+ E（`包含 4 个上游子模块` 改 `5 个`，命中计数不符）+ F（项目索引插 `ghost` 行）均按预期退出码与关键词命中 |
| 生成模式幂等 | `--generate` 连跑两次 | 二次运行「已是目标状态，跳过」，退出码 0 |
| 结构化输出 | `--json` | `{"ok": true, "failures": [], "notes": []}` |
| 静态检查 | `ruff check scripts/check_declaration_consistency.py` | `All checks passed!` |
| 断链门禁 | `check-links.py --paths doc vendor scripts`（cwd = `projects/xuanspace`） | rc=1；33 处**均为存量**（集中在 `doc/intro.md`、`doc/quickstart.md`、`doc/okf/**` 的省略扩展名写法），本轮 4 文件 **0 新增** |
| 边界核对（xuanspace） | `git status --short` | 除本轮 5 文件外，其余 dirty 全为**并行会话在途改动**，本轮未触碰 |
| 边界核对（根仓） | `git ls-tree HEAD projects/xuanspace` | gitlink = 子模块 HEAD（`fd6d7e6…`） |

### 17.4 残余漂移清理

| 文件 | 清理内容 |
|---|---|
| `doc/architecture.md` | 删根目录树中失实的 `CMakeLists.txt` 行——该项目为纯 Python 枢纽包（`[tool.scikit-build.wheel] cmake = false`），磁盘无根级 `CMakeLists.txt`；`CMakePresets.json` 保留 |
| `vendor/README.md` | 「现有子项目」表前删「（待实际添加后更新此表）」占位符，表体（`tvm-ffi/`、`caffe/`）与 `.gitmodules` 对齐 |

### 17.5 遗留与后续

- 本轮兑现《项目蓝图》目标态特征 1：子项目清单、命令清单、目录树、vendor 清单、子模块声明、项目索引六类可机械提取的声明均已受 CI 断言约束。
- **可选遗留**（本轮未获授权，未启动）：`doc/intro.md`、`doc/quickstart.md`、`doc/okf/**` 的 33 处**省略扩展名**存量断链——属 `check-links.py` 对无扩展名相对链接的既有误报模式，非本轮引入，需另行评估是否加白名单或批量补扩展名。
- 本规格至此无遗留任务；如后续再启动收口轮次，沿用「子模块原子提交 → 根仓前移 gitlink → 三件套回写」既定流程。

## 十八、依赖方向门禁证据（规格完成后追加，第九轮）

> 范围：规格完成后**第九轮**经用户另行授权执行的工作——兑现《项目蓝图》目标态三特征中唯一未兑现的特征 3「方向可断言」。对应 tasks.md 的 Task 20。本节为独立审查记录，不改写一至十七节的原始验收结果。

### 18.1 交付物与提交

| 仓库 | 提交 | 变更规模 |
|---|---|---|
| `projects/xuanspace` | `c50f18e` feat(scripts): 新增依赖方向门禁并同步文档与 CI | 4 文件（`scripts/check_dependency_direction.py`（新建）+ `scripts/README.md` + `libs/README.md` + `.github/workflows/ci.yml`，+164 / −2） |
| 根仓 `SpecWeave` | `06f37e234` chore(xuanspace): 前移子模块指针并回写依赖方向门禁证据 | 3 文件（`tasks.md` + `review.md` + gitlink） |

未 push、未 tag。子模块 HEAD 为 `c50f18eb26f62e3d0f56cb60c10655e5e50dd233`，根仓 gitlink 与之对齐。

### 18.2 蓝图三特征兑现对照

| 目标态特征（`doc/blueprint.md` L205–207） | 兑现轮次 | 证据 |
|---|---|---|
| 1 声明可核对 | 第八轮 | A–F 六类断言（`check_declaration_consistency.py`） |
| 2 单一事实来源 | 第七/八轮 | `libs/README.md` 生成块（P1-4①）+ `scripts/declaration-snapshot.json` |
| 3 **方向可断言** | **第九轮（本节）** | `scripts/check_dependency_direction.py` + CI quality job |

> 蓝图洞察 I4（L56）亲口点名：「四层解构的真正价值不在于把东西分成四类，而在于它**隐含了一个依赖方向约束**……而当前这份约束只写在图里、未被任何检查断言。」本轮即把该约束从「描述」升为「规范」。

### 18.3 规则来源与检查设计

| 维度 | 设计 |
|---|---|
| 规则单一事实来源 | 脚本 `FORBIDDEN_IMPORTS` 常量，与 `libs/README.md`「依赖规则」一节同源；`libs/README.md` 已加注脚双向指认 |
| 检查对象 | `libs/` 下全部 `.py` 源码（本轮基线 291 个文件） |
| 检查方法 | `ast` 解析，取**绝对导入**顶层模块名（`Import` / `ImportFrom`）；`level > 0` 的相对导入视为 lib 内部引用，不检查 |
| 禁止集合（libs） | `apps`、`scripts`、`attic`、`vendor`；`tools` 属「谨慎依赖」，**不拦截**（尊重 `libs/README.md` 的语义分级，未用纯层级序机械推导） |
| 排除项 | `.gitmodules` 声明的子模块（`libs/mystx`、`libs/tvm-book`）+ 构建产物/缓存目录（`build`、`dist`、`__pycache__`、`.mypy_cache` 等） |
| 输出与退出码 | `文件:行号: 禁止导入 '<分区>'（来自 '<模块>'）`；0 通过 / 1 违规（或源码不可解析）/ 2 脚本自身错误（未扫描到源码） |

### 18.4 门禁与核验

| 检查项 | 命令 / 方法 | 结果 |
|---|---|---|
| 基线 | `python scripts/check_dependency_direction.py` | 退出码 **0**；「扫描到 291 个 Python 文件（分区：libs）」「全部通过依赖方向校验：libs 未依赖 apps, scripts, attic, vendor。」 |
| 负向探针 | 在 `libs/xuan-core/src/xuan_core/_dep_probe.py` 注入 `from scripts import …` / `import vendor.caffe` / `from attic.old import …` | **3/3 命中**，退出码 **1**，逐条输出 `libs/xuan-core/src/xuan_core/_dep_probe.py:<行>: 禁止导入 '<分区>'（来自 '<模块>'）`；清理探针后恢复退出码 0（扫描数回落 291） |
| 相对导入 | `level > 0` 分支代码审查 + 全量基线无 `..` 误报 | 不误报（`libs/xuan-compose` 等大量 `from .` 导入全部通过） |
| 静态检查 | `ruff check` / `ruff format --check scripts/check_dependency_direction.py` | `All checks passed!` / `1 file already formatted` |
| 既有门禁无回归 | `check_declaration_consistency.py`、`check_pyproject_style.py` | 均退出码 **0**（六类全通过 / 12 个 pyproject.toml 全通过） |
| 断链门禁 | `check-links.py --paths libs/README.md scripts/README.md doc/blueprint.md`（cwd = `projects/xuanspace`） | 退出码 **0**，121 处本地引用全部有效，**0 新增断链** |
| 边界核对（xuanspace） | `git status --short` | 仅本轮 4 项变更，无并行会话残留 |
| 边界核对（根仓） | `git ls-tree HEAD projects/xuanspace` | gitlink = 子模块 HEAD（`c50f18e…`） |

### 18.5 附带口径修正

| 文件 | 修正内容 |
|---|---|
| `.github/workflows/ci.yml` | quality job 头注释原为「五项自动化检查」而实列 6 项；本轮增 `dependency` 后统一为「七项（pyproject/declaration/dependency/doctor/meta/lfs/docs）」 |
| `scripts/README.md` | `check_declaration_consistency.py` 行描述第八轮扩至六类后仍写三类 → 补齐六类；新增 `check_dependency_direction.py` 行 |

### 18.6 决策记录：不回改蓝图时点快照

`doc/blueprint.md` 事实清单第 14/15/17 行（`libs/README.md#L106-L111`、`#L115-L118`）与洞察 I4 行动项中的同址引用，因 P1-4① 注入生成块而**行号漂移**。该文件首部显式声明**基线 `HEAD = 8db593d5fc1ee999c8311f83951e40f15024e2d9`**，其事实清单是**时点快照**；按项目「不改动历史事实快照」约束**不予回改**，漂移本身已在本规格第八轮登记。此为本轮**有意不做的动作**，非遗漏。

### 18.7 遗留与后续

- 本轮兑现《项目蓝图》目标态**第 3 项（末项）特征**；三特征至此全部具备 CI 断言。
- 门禁当前仅覆盖 `libs` 分区（`FORBIDDEN_IMPORTS` 表的唯一键）。`tools`、`apps` 等分区的依赖方向**尚未登记规则**——`libs/README.md` 未对其声明禁止集合，故本轮不臆造规则、不越界扩展（避免制造无文档依据的断言）。
- **可选遗留**（本轮未获授权，未启动）：`doc/intro.md`、`doc/quickstart.md`、`doc/okf/**` 的 33 处**省略扩展名**存量断链——属 `check-links.py` 既有误报模式，非本轮引入。
- 本规格至此无遗留任务；如后续再启动收口轮次，沿用「子模块原子提交 → 根仓前移 gitlink → 两段式（占位符 + `docs(spec)` 回填）提交 → 三件套回写」既定流程。

## 十九、存量断链修复证据（规格完成后追加，第十轮）

> 范围：规格完成后**第十轮**经用户另行授权执行的工作——清理 `doc/` 目录内 33 处「省略 `.md` 扩展名」的相对链接（自第一轮 Task 7 取证起长期以「存量」挂账）。对应 tasks.md 的 Task 21。本节为独立审查记录，不改写一至十八节的原始验收结果。

### 19.1 交付物与提交

| 仓库 | 提交 | 变更规模 |
|---|---|---|
| `projects/xuanspace` | `13b98b3` docs(xuanspace): 统一 doc/ 相对链接为带 .md 扩展名的仓内约定 | 8 文件（7 个 `doc/**` 文档共 33 处链接 + `CONTRIBUTING.md` §12.4 预防条款，+34 / −33） |
| 根仓 `SpecWeave` | `f8e60d147` chore(xuanspace): 前移子模块指针并回写存量断链修复证据 | 3 文件（`tasks.md` + `review.md` + gitlink） |

未 push、未 tag。

### 19.2 根因判定（先定性，后修复）

| 假说 | 验证方法 | 结论 |
|---|---|---|
| H1 渲染缺陷（链接真的断） | `sphinx -b html doc doc/_build/probe`，查 `doc/intro.html` 中 `[快速开始](quickstart)` 的渲染结果 | **否**——渲染为 `<a class="reference internal" href="quickstart.html"><span class="doc std std-doc">快速开始</span></a>`，与 `.md` 写法产物**逐字一致**；MyST **实现了 docname 解析** |
| H2 检查器误报 | 对照 `check-links.py` 链接解析逻辑 + 该批链接的目标文件**全部真实存在** | **是**——该脚本未实现 MyST docname 解析（区分对待 `foo` 与 `foo.md`），是断链被报出的直接原因 |
| H3 违反仓内书面约定 | 核 `doc/okf/synthesis.md` L12 与 `doc/index.md` L32 的写法 | **是**——仓内唯一书面化的格式规则是 `` `<相对路径>.md` ``，且 `index.md`/`synthesis.md` 均照此写；33 处为**少数派写法** |

> 三项共同指向：**渲染无缺陷、书面约定被违反、链接门禁常红**。故本轮取「统一文档到已书面化的 `.md` 约定」，而非「就地修补检查器」——理由见 19.4。

### 19.3 门禁与核验

| 检查项 | 命令 / 方法 | 结果 |
|---|---|---|
| 断链门禁（修前） | `check-links.py --path doc`（cwd = `projects/xuanspace`） | 退出码 **1**；33 断链（7 文件，逐条含 `文件:行号`） |
| 断链门禁（修后） | 同上 | 退出码 **0**；「校验通过: 所有链接均有效」（157 处本地引用全有效） |
| 残留检索 | `]\((?:trust\|attested\|conformance\|commands\|synthesis\|plugins\|bundle\|index\|architecture\|build-system\|contributing\|cli/index\|quickstart)\)` 于 `doc/**/*.md` | 命中 **0**（修前 32 + `quickstart` 1 = 33） |
| 编辑规模 | `git diff --stat` | 恰 7 文件 **33 增 33 删**（无附带改动） |
| 渲染回归 | `sphinx -b html doc doc/_build/probe2` + 抽验 `okf/bundle.html` | `构建成功。`（无 WARNING/ERROR）；`href="trust.html"`、`href="attested.html"` 与修前**逐字一致** → 零渲染变化 |
| 既有门禁无回归 | `check_pyproject_style.py` / `check_declaration_consistency.py` / `check_dependency_direction.py` | 均退出码 **0**（12 个 pyproject.toml / 六类断言 / 291 文件） |
| 预防条款自检 | `check-links.py --path CONTRIBUTING.md` | 退出码 **0**（新条款以非链接语法书写，未引入本地引用误报） |
| 边界核对（xuanspace） | `git status --short` | 仅本轮 8 项变更 |
| 边界核对（根仓） | `git ls-tree HEAD projects/xuanspace` | gitlink = 子模块 HEAD |

### 19.4 决策记录：不修改根仓 `check-links.py`

该脚本未实现 MyST docname 解析，是本批断链被报出的直接原因。**本轮有意不改**，理由三条：

1. **归属**：`check-links.py` 位于根仓 `.agents/scripts/`（主权区共享资产），改动影响全仓所有 app，超出本轮授权范围；
2. **口径**：让「带扩展名/不带扩展名两种写法都合法」会在仓内制造**双标准**，与单一事实来源相悖——`doc/okf/synthesis.md` L12 已书面规定 `.md` 形式；
3. **最小化**：修文档（33 处补扩展名）零渲染变化、零新风险，且使门禁由红转绿；检查器局限作为**已知限制**登记，待需要时另行立项。

### 19.5 预防（修复即闭环）

| 维度 | 内容 |
|---|---|
| 根因 | 链接格式约定只写在 `doc/okf/synthesis.md` L12（OKF 教程**局部**），顶层文档与 okf 教程作者看不到 → 漂移得以存续九轮 |
| 预防 | `CONTRIBUTING.md` §12.4「文档风格建议」增一行：交叉引用一律写带 `.md` 扩展名的相对路径，并说明省略扩展名会被链接门禁判为断链。该文件经 `{include} ../CONTRIBUTING.md` 进入 `doc/contributing.md`，是文档作者的**通用入口** |
| 闭环 | 「修后门禁 exit 0 + 残留检索 0 + 渲染零变化 + 既有门禁无回归 + 预防条款落位」五项齐备 |

### 19.6 遗留与后续

- 承 §17.5 / §18.7 的「可选遗留」**本轮已闭环**：33 处存量断链全部清除，`check-links.py --path doc` 首次通过。
- 剩余已知限制：`check-links.py` 对 MyST 无扩展名链接的误报行为**未改变**（本轮选择适配约定而非改脚本，见 19.4）；若后续仍写无扩展名链接，门禁会再次报出——这正是 19.5 预防条款存在的意义。
- 本规格至此无遗留任务；如后续再启动收口轮次，沿用「子模块原子提交 → 根仓前移 gitlink → 两段式（占位符 + `docs(spec)` 回填）提交 → 三件套回写」既定流程。

## 二十、过程性文档清理证据（规格完成后追加，第十一轮）

> 范围：规格完成后**第十一轮**经用户裁定执行的工作——删除两份过程性分析产物（`doc/blueprint.md`、`doc/recommendations.md`）并清理其导航登记与交叉引用。对应 tasks.md 的 Task 22。本节为独立审查记录，不改写一至十九节的原始验收结果；§一 AC-1 的勾选按「历史可审计性」约束**不回改**。

### 20.1 处置与提交

| 仓库 | 提交 | 变更规模 |
|---|---|---|
| `projects/xuanspace` | `91ba03d` docs(xuanspace): 删除已闭环的过程性分析文档并清理导航 | 3 文件（`doc/blueprint.md` 删除、`doc/recommendations.md` 删除、`doc/index.md` 移除「规划」toctree） |
| 根仓 `SpecWeave` | `575f839d1` chore(xuanspace): 前移子模块指针并回写过程性文档清理证据 | 3 文件（`tasks.md` + `review.md` + gitlink） |

未 push、未 tag。

### 20.2 定性依据（先定性，后处置）

| 维度 | 判定 | 证据 |
|---|---|---|
| 身份 | 两份均为**活的 doc/ 文档**，非规格历史快照 | `doc/index.md` L64–70 的「规划」toctree 登记两项；两文档互引 |
| `recommendations.md` 状态 | **终态空壳**（12 行） | P0/P1/P2 条目全部闭环后正文移除，仅余一句终态声明 |
| `blueprint.md` 状态 | **与现状不一致** | 基于基线 `8db593d`；其标记「薄弱」的声明一致性、`apps/` 失实声明、子模块数量口径、命令清单口径等，多数已在第七至十轮闭环 |
| 本质（F） | 一次性过程性产物 | 蓝图＝分析结论、建议书＝待办清单；权威载体已转移至规格三件套（决策与证据）与 git 历史（变更事实），结构叙事由 `README.md` 与 `doc/architecture.md` 承载 |

> 判定要点：**活文档与现状不一致即失真源**。「不删又不更新」比删除更糟——它会把已修复的问题当作现存问题持续展示。

### 20.3 门禁与核验

| 检查项 | 命令 / 方法 | 结果 |
|---|---|---|
| 断链门禁 | `check-links.py --path doc`（cwd = `projects/xuanspace`） | 退出码 **0**；20 个 Markdown 文件、35 处本地引用全有效（删除后「规划」toctree 与互引一并消失，无新增断链） |
| 残留检索 | `blueprint\|recommendations` 于 `doc/**/*.md` | 命中 **0** |
| 构建回归 | `sphinx -b html doc doc/_build/probe3` | `构建成功。`（无 WARNING/ERROR，无 orphan 警告） |
| 变更面 | `git status --short` | 恰 3 项（两删除 + `doc/index.md` 修改） |

### 20.4 决策记录：不回改 AC-1 勾选

review.md §一 AC-1「交付物存在性」曾断言两份文档存在于 `doc/`，与规格实施过程一致。本轮删除属**规格完成后经用户裁定的新决策**，与该历史断言不矛盾；按项目「不改动历史事实快照」约束，§一 原始勾选**不予回改**，处理经过记于本节。

### 20.5 遗留与后续

- 承 §17.5 / §18.7 / §19.6 的「本规格无遗留任务」：本轮为可选的文档生命周期清理，非规格欠账。
- 本规格至此仍无遗留任务；如后续再启动收口轮次，沿用「子模块原子提交 → 根仓前移 gitlink → 两段式（占位符 + `docs(spec)` 回填）提交 → 三件套回写」既定流程。

## 二十一、文档易腐性清理与门禁扩容证据（规格完成后追加，第十二轮）

> 范围：规格完成后**第十二轮**经用户裁定执行的工作——① 删除手工维护、无生成器的时点快照 `doc/dependency-report.md`（及 `.meta` 镜像）；② 补全活文档 `doc/cli/index.md` 的命令总览与细则（缺 `archive`、`lfs` 两条）；③ 扩容 `check_declaration_consistency.py` 断言 A 覆盖该文件，预防同类漂移复发。对应 tasks.md 的 Task 23。本节为独立审查记录，不改写一至二十节的原始验收结果。

### 21.1 处置与提交

| 仓库 | 提交 | 变更规模 |
|---|---|---|
| `projects/xuanspace` | `72898a2` docs(xuanspace): 删除失效的依赖报告并补全 CLI 参考与门禁覆盖 | 5 文件（`doc/dependency-report.md` 删除、`.meta/toml/doc/dependency-report.toml` 删除、`doc/index.md` 移除「项目」toctree 中的 `dependency-report`、`doc/cli/index.md` 补两条命令、`scripts/check_declaration_consistency.py` 扩容，+53 / −143） |
| 根仓 `SpecWeave` | `ROOT_COMMIT_PLACEHOLDER` | 3 文件（`tasks.md` + `review.md` + gitlink） |

未 push、未 tag。

### 21.2 定性依据（先定性，后处置）

| 对象 | 身份 | 失实证据 | 处置 |
|---|---|---|---|
| `doc/dependency-report.md` | **时点快照**（手工维护，全仓无生成器） | §7 CI 表误列已不存在的 `lint`、漏 `py-compat`（实为 4 job：test / quality / template-validation / py-compat）；§2 子模块树仅列 2 项（`.gitmodules` 实为 4 项：vendor/tvm-ffi、libs/tvm-book、vendor/caffe、libs/mystx）；§1 `apps/` 仍标「空，待填充」 | **删除**（连同 `.meta` 镜像） |
| `doc/cli/index.md` | **活文档但内容过期** | `README.md` L101 声明「15 个子命令」并以其为 CLI 参考链接，该参考原仅列 13 条（缺 `archive`、`lfs`）；`cli.py` 实际注册 **15** 项（7 `add_typer` + 8 `app.command`），`doc/intro.md` 已列全 | **更新对齐 + 门禁约束** |

> 判定要点同 §20.2：**活文档与现状不一致即失真源**。报告类产物若不自带生成器，其功能等价于「过期风险载体」——其持久事实（架构、构建流程、目录口径）已由 `doc/architecture.md`、`doc/build-system.md`、`CONTRIBUTING.md` 承载，历史内容可由 git 追溯。

### 21.3 门禁扩容（预防）

| 维度 | 内容 |
|---|---|
| 根因 | 断言 A 只覆盖 `README.md` + `doc/intro.md`，未覆盖作为 CLI 参考链接目标的 `doc/cli/index.md` → 该文件漂移静默积累 |
| 改动 | `check_declaration_consistency.py` 新增 `CLI_REF_FILE = "doc/cli/index.md"` 常量与 `declared_cli_ref_commands()`；原 `doc/intro.md` 专用行正则泛化为共用 `_DOC_CMD_ROW_RE`（底座 `_declared_doc_commands(root, rel)`）；`run_checks` 增加「`doc/cli/index.md` 命令总览 ↔ 注册表」集合比对 |
| 预防逻辑 | 只修文档不改门禁＝「修复即复发」；扩容后三个声明源（README 计数、intro 命令表、cli/index 命令表）同受断言约束 |

### 21.4 门禁与核验

| 检查项 | 命令 / 方法 | 结果 |
|---|---|---|
| 声明一致性（正向） | `python scripts/check_declaration_consistency.py` | 退出码 **0**；六类全通过（含新增 cli/index 比对） |
| 负向回归（内存预演，不动磁盘文件） | `importlib` 加载门禁脚本 + `monkeypatch _read_text` 将 `cli/index.md` 内存副本移除 `xs archive` 行后重跑 `run_checks` | 命中 1 项：`doc/cli/index.md 命令总览 与事实不一致（声明缺：['archive']；声明多：[]）` → 证明新断言有效 |
| 断链门禁 | `check-links.py --path doc`（cwd = `projects/xuanspace`） | 退出码 **0**；19 个 Markdown 文件、35 处本地引用全有效 |
| 构建回归 | `sphinx -b html doc doc/_build/probe5` | `构建成功。`（无 WARNING / ERROR） |
| 残留检索 | `dependency-report\|dependency_report` 全仓 | 命中 **0** |
| 元数据校验 | `xs meta validate` | 退出码 **0**；报出 122 项**无一条**落在 `doc/` 或 `.meta/`（全为 `libs/caffe-ffi`、`libs/mystx`、`vendor/caffe`、`tools/okf/tests/fixtures` 既有问题），与本轮无关 |
| 边界核对（xuanspace） | `git status --short` | 仅本轮 5 项变更 |
| 边界核对（根仓） | `git ls-tree HEAD projects/xuanspace` | gitlink = 子模块 HEAD（`72898a2…`） |

### 21.5 决策记录

- 本轮「删除 / 修复 / 门禁扩容」三项均经用户裁定授权（AskUserQuestion：删除 `dependency-report.md` 推荐；一并修复 `doc/cli/index.md` + 扩容门禁推荐）。
- `doc/dependency-report.md` 的持久事实未丢失——架构、构建、目录口径已由其他活文档承载，历史内容可由 git 追溯。
- review.md 一至二十节原始验收结果**不回改**（沿用「不改动历史事实快照」约束）。

### 21.6 遗留与后续

- 承 §20.5「本规格无遗留任务」：本轮为可选的文档生命周期清理 + 门禁补强，非规格欠账。
- 本轮定性复查聚焦 `doc/` 目录，已处理对象为上表两项；同类「时点快照 / 活文档失真」对象的进一步筛查属可选后续，非本轮授权范围。
- 本规格至此仍无遗留任务；如后续再启动收口轮次，沿用「子模块原子提交 → 根仓前移 gitlink → 两段式（占位符 + `docs(spec)` 回填）提交 → 三件套回写」既定流程。

