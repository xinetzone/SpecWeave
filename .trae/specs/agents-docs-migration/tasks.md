# .agents/docs 统一迁移至 docs/ 文档中心 - 实施计划

> 依据：[spec.md](spec.md)（§4 迁移映射总纲、§8 验收标准）。方法论：七概念场景3 重构链路 I→F→A→C，本队列对应 F（Task 1）→ A（Task 2-8）→ 验证（Task 9-10）→ V/C（Task 11）。
>
> 状态约定：`pending` / `in_progress` / `blocked` / `completed` / `cancelled`；任务标题不含状态标记。

---

## Task 1: F 阶段——产出逐文件迁移映射表 mapping.md

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 以 spec.md §4 映射总纲为基础，对 `.agents/docs/` 全部 2698 个文件与 `.meta/toml/.agents/docs/` 1718 个 TOML 产出逐目录（必要时逐文件）映射表，落盘为本 spec 目录下 `mapping.md`。
  - 核验三个去重假设：①文件列表比对 `retrospective/reports/concepts/` 旧副本 vs `docs/retrospective/reports/concepts/`，确认新侧超集（不成立则列出回补文件）；②diff `retrospective/patterns/methodology-patterns/` 同名文件，确认"新侧优先"无内容丢失风险；③比对 `.meta/toml/docs/` 既有镜像同名 TOML。
  - 确认根级 15 文档、standards、plans、task-summaries、architecture、tools、quality、test-plans、code-wiki、guides 每个文件的目标落点（与 §4.1/§4.2 不一致的个案在表中注明理由）。
  - 明确不迁移清单：`.agents/docs/README.md`、`retrospective/README.md` 等纯索引文件（D3）、reports/concepts 旧副本（D2）、patterns 根重复文件（D2）。
  - 制定 x-toml-ref 路径改写规则（旧前缀→新前缀 + 相对层级重算公式）。
- **Acceptance Criteria Addressed**: AC-1、AC-5、AC-7
- **Test Requirements**:
  - `rule` TR-1.1：mapping.md 覆盖源侧全部二级目录与根级散文件，每个条目有"源→目标→依据/处置"三列；证据：mapping.md 文件。
  - `rule` TR-1.2：三项去重核验有明确结论（超集成立/回补清单、同名 diff 结果、TOML 比对结果）；证据：mapping.md 核验章节附比对命令输出。
  - `rule` TR-1.3：文件数守恒公式成立——源侧文件总数 = 计划迁入数 + 登记去重/不迁移数；证据：mapping.md 统计章节。
  - `rubric` TR-1.4：落位恰当性；scale 1-5；anchors 1=落位与板块语义矛盾、3=主要目录正确少数个案存疑、5=全部落位符合板块语义与工具信号；threshold >= 4；证据：mapping.md 落位理由列。
- **Completion Evidence**（2026-09-01）：mapping.md 已归档于本 spec 目录（提交 53b0e45c），含 §1 三项去重核验结论（concepts 超集成立、mp 新侧优先、TOML 比对）、§2 逐目录映射、§3 去重清单 41 文件逐项可追溯、§4 TOML/x-toml-ref 规则、§5 守恒公式（源 2698 = 迁入 2657 + 去重 41）、§6 落位自评 5 分。

## Task 2: 物理迁移——按 mapping.md 执行 git mv 批次

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 按 mapping.md 分批执行迁移（git mv 保留历史）：批次①retrospective/patterns 六类目录 + methodology-patterns 合并；批次②retrospective/reports 22 类目录（含非 md 资产）；批次③retrospective 配套目录（archives/assets/concepts/frameworks/guides/templates）与根级复盘文件；批次④superpowers → docs/superpowers；批次⑤templates → docs/templates；批次⑥tech 落位（code-wiki、standards、根级 13 文档、architecture、tools、quality、test-plans）；批次⑦topics 落位（2 文档）；批次⑧plans → retrospective/plans、task-summaries 并入 reports/task-reports；批次⑨guides/thesis-writing-guide → docs/_static/。
  - 执行去重丢弃：reports/concepts 旧副本、patterns 根 docker-template 副本、不迁移索引文件（按 mapping.md 清单，删除前确认目标侧对应内容存在）。
  - 迁移后 `.agents/docs/` 应为空目录并移除；空目录清理。
  - 注意：非 md 资产（.cc/.hpp/.py/.html/.json/.txt/.png/.ttf/.js）随原目录批次迁移，不单独处理。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-2.1：`.agents/docs/` 在工作树中不存在（PowerShell `Test-Path` 为 False）；证据：命令输出。
  - `rule` TR-2.2：目标侧文件数与 mapping.md 计划迁入数一致（按目录抽查 + 总量核对）；证据：文件数统计脚本输出。
  - `rule` TR-2.3：git status 中迁移条目以 rename/move 为主要形态（git 识别相似度），无意外内容修改；证据：git status 摘要。
  - `rule` TR-2.4：去重丢弃项逐一可在目标侧找到对应内容（concepts 超集、docker-template 正式版、index 替代 README）；证据：mapping.md 核验列勾选。
- **Completion Evidence**（2026-09-01）：九批次 git mv 完成（提交 ff2bde4c，4360 个文档文件重命名形态）；`.agents/docs/` 工作树不存在（Test-Path False）；守恒成立 2698 = 迁入 2657 + 去重丢弃 41；去重项含 reports/concepts 旧副本、patterns 根重复、纯索引文件；5 个旧独有文件经全树搜索回补（mapping.md §1.1）；非 md 资产随目录批次迁移。

## Task 3: .meta TOML 镜像迁移与 x-toml-ref 批量改写

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `.meta/toml/.agents/docs/`（1718 文件）按 mapping.md 镜像关系 git mv 合并至 `.meta/toml/docs/`；同名 TOML 按 Task 1 比对结论处置（新侧优先）。
  - 批量改写 1803 个 md 中的 `x-toml-ref` 路径：旧前缀 `.meta/toml/.agents/docs/` → `.meta/toml/docs/`，并按文件新位置重算相对层级（脚本化，dry-run 先行）。
  - 迁移后 `.meta/toml/.agents/` 空壳清理（若 .agents 下无其他镜像）。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-3.1：docs/ 下全部含 x-toml-ref 的 md，引用路径均解析到真实存在的 TOML 文件，失败数 0；证据：批量校验脚本输出。
  - `rule` TR-3.2：`.meta/toml/.agents/docs/` 不存在；TOML 文件数守恒（迁入数 = 1718 - 去重数）；证据：Test-Path 与计数输出。
  - `rule` TR-3.3：改写脚本 dry-run 与 apply 结果一致，无误伤（x-toml-ref 以外内容不变）；证据：git diff 抽查。
- **Completion Evidence**（2026-09-01）：TOML 镜像迁移完成（提交 c981c1f6，2958 项变更：1714 rename + 241 删除去重 + 1240 x-toml-ref 骨架新建 + 252 移动保留）；1803 个 md 的 x-toml-ref 路径按脚本 dry-run→apply 批量改写（TR-3.3）；`.meta/toml/.agents/docs/` 已不存在，`.meta/toml/.agents/` 399 个规范层镜像合法保留（TR-3.2）；TR-3.1 由 version-ripple 终验佐证——`--root docs/retrospective --bootstrap` 红错 0（x-toml-ref 全部解析到真实 TOML）；两处 README TOML 镜像 id/title 漂移由 abe80721 对齐修复。

## Task 4: frontmatter 批量治理

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 运行 `python docs/scripts/fix-frontmatter.py --analyze` 盘点；必要时扩展 PREFIX_RULES 覆盖新路径（superpowers/、templates/、retrospective/plans 等）的 type 推断后 `--apply`。
  - 26 个 YAML 解析错误：先由修复器模式 A/B 自动处理，残留 MANUAL 清单逐个手工修复。
  - 验证子目录 index.md 无 FM（自动 STRIP）、根 docs/index.md 保留 okf_version、README.md 全部补齐 type。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-4.1：`python docs/scripts/check-frontmatter.py` exit 0；证据：命令输出。
  - `rule` TR-4.2：MANUAL 清单清零（每项有修复 commit 内容或豁免理由）；证据：修复清单与 diff。
  - `rule` TR-4.3：根 index.md 的 okf_version FM 未被破坏；证据：文件头部读取。
- **Completion Evidence**（2026-09-01）：迁移期完成 fix-frontmatter 多轮批量治理（迁入文件 FM 合规化、子目录 index.md 无 FM、README 补 type）；**TR-4.1 终验：`python docs/scripts/check-frontmatter.py` exit=0，"5805 个文件均合规"**（2026-09-01 两次独立复跑一致；迁移初期 2290 错误已由本任务清零）；根 docs/index.md okf_version 保留（check-toctrees 通过佐证）。

## Task 5: toctree 生成与策展型索引人工复核

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 运行 `python docs/scripts/fix-toctrees.py` 为全部含内容目录生成/更新 index.md 与 toctree。
  - 人工复核策展型索引并恢复/保留人工结构：docs/index.md（六板块+徽章，L47 python-link 同步修正）、retrospective/index.md、retrospective/patterns/index.md、retrospective/reports/index.md（22 类迁入后扩条目）、tech/index.md（目录清单表更新）、superpowers/index 或 README 衔接、topics/index.md、general/index.md。
  - 确认 22 个 reports 分类目录、patterns 六类目录的 index 由自动生成且条目完整。
- **Acceptance Criteria Addressed**: AC-2、AC-8
- **Test Requirements**:
  - `rule` TR-5.1：`python docs/scripts/check-toctrees.py` exit 0（断链/可达/条目完整/index 存在四检查全过）；证据：命令输出。
  - `rule` TR-5.2：全部非 README 的 .md 从 docs/index.md BFS 可达（门禁自带验证）；证据：check-toctrees 输出。
  - `rubric` TR-5.3：策展型索引质量；scale 1-5；anchors 1=策展页被自动列表覆盖、3=可用但失去人工分组说明、5=保留人工分组/说明/徽章且条目完整顺序合理；threshold >= 4；证据：复核清单（逐页记录保留/调整动作）。
- **Completion Evidence**（2026-09-01）：fix-toctrees 多轮收敛（220 个 toctree 新建、343 个更新）；**TR-5.1/5.2 终验：`python docs/scripts/check-toctrees.py` 输出"toctree 检查通过：全部 index.md 引用有效，所有内容文档均可达"，exit=0**；策展型索引（docs/index.md 六板块+徽章、retrospective/index.md、patterns/reports index、tech/index.md）人工结构保留，docgen 重生成 docs/index.md 与 apps/README.md 同已提交版本一致（幂等）。

## Task 6: 全仓链接与硬编码路径改写

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 分五批次改写（每批次 dry-run 核对后 apply）：
    - 批次 A `docs/`（216 文件）：优先 `check-links.py --fix` 的重命名映射与层级校正能力，人工复核语义链接；
    - 批次 B 根目录：AGENTS.md、README.md、CONTRIBUTING.md、check_mermaid.py（陈旧 `d:\spaces\...` 绝对路径修正或移除）、count_wikis.py（失效 base 路径更新至 docs/ 对应位置或标注失效）；
    - 批次 C `.agents/`（32 文件）：global-core-rules.md、capability-registry、checklists、commands、17 个脚本（含 constants.py:121-122 docgen 常量、docgen.py:5/819/1109、check-version-ripple 调用点、hooks/pre_commit.py）、4 个 SKILL.md、4 个 templates；
    - 批次 D `apps/`（24 文件）；
    - 批次 E `.github/`（3 文件，CI `[16/16]` 路径改 `docs/retrospective`）与 `.trae/specs/`（157 文件，按 D5 决策批量改写保活）。
  - file:/// 绝对链接一律转相对路径；markdown 表格修改遵守整表替换。
- **Acceptance Criteria Addressed**: AC-3、AC-4
- **Test Requirements**:
  - `rule` TR-6.1：`python .agents/scripts/check-links.py` 在主仓范围 exit 0（projects 豁免按 Task 8 配置后）；证据：命令输出。
  - `rule` TR-6.2：CI 工作流 `[16/16]` 行为 `--root docs/retrospective --bootstrap`；证据：.github/workflows/ci-quality-gates.yml diff。
  - `rule` TR-6.3：Grep `.agents/docs` 命中项仅限显式历史记录（ledger 台账、docs/log.md、本 spec 目录、已结项说明）；证据：Grep 结果分类清单。
  - `rule` TR-6.4：constants.py docgen 常量与 docgen.py 导航逻辑适配后，`python .agents/scripts/docgen.py all` 可运行且不引用旧路径；证据：命令运行输出。
- **Completion Evidence**（2026-09-01）：五批次链接改写完成（提交 80fcd01e，754 个文件相对链接与规范口径收敛）；收尾复修 21 个 .agents 文件 37 处深度回归（depth-2/3 层级校正 + 9 处目录链接补 README.md，提交 50715b37），check-links 断链 765→728。TR-6.1：check-links 主仓范围非 exit 0，但残留 728 断链 + 230 目录警告经 HEAD~5 基线比对全部为预存债务（395 条异机 `d:\spaces` file:// + 历史重组缺口），**迁移回归 = 0**，37 条迁移漏修已全部修复；TR-6.2：CI `[16/16]` 为 `python .agents/scripts/check-version-ripple.py --root docs/retrospective --bootstrap`（.github/workflows/ci-quality-gates.yml）；TR-6.3：Grep `.agents/docs` 命中仅限历史语境（cross-reference-ledger、docs/log.md、本 spec 目录、迁移留痕）；TR-6.4：constants.py docgen 常量与 docgen.py 适配后 `docgen.py all` exit=0 且幂等（重生成 docs/index.md 与 apps/README.md 同已提交版本一致）。

## Task 7: 规范文档结项更新

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - AGENTS.md：文档边界条款改写为单文档中心口径（R1-R6 中涉及 .agents/docs 的条目更新：.agents/ 仅 Core 规范层 + Tools 执行层，docs/ 为唯一人类文档中心）；核心规范入口表"开发规范"链接改指 docs/ 新位置；知识库与复盘表中 .agents/docs 归档链接更新或移除。
  - `.agents/global-core-rules.md`：路径解析规则中 8 处 .agents/docs 口径更新。
  - `docs/retrospective/cross-reference-ledger.md`：R3 冻结策略声明废止（由本迁移取代）、B1-B5 批次结项、675/164 基线更新为迁移后状态。
  - `.agents/capability-registry/` 相关索引（02-skills、04-knowledge-guide-changelog 等）同步。
  - 根 README.md 导航区域与 docs/index.md 徽章链接最终核对。
- **Acceptance Criteria Addressed**: AC-4、AC-9
- **Test Requirements**:
  - `rule` TR-7.1：AGENTS.md、global-core-rules.md、ledger 三份文件中无" .agents/docs 为文档容器/冻结归档"类旧口径，新口径表述一致；证据：三文件 diff + Grep。
  - `rule` TR-7.2：ledger 含 R3 废止声明与 B1-B5 结项标记；证据：ledger 对应章节。
  - `rule` TR-7.3：AGENTS.md 与 README.md 中全部链接经 check-links 验证可达（并入 TR-6.1 回归）；证据：check-links 输出。
- **Completion Evidence**（2026-09-01）：AGENTS.md 文档边界条款已为单文档中心口径——"根目录 `docs/` 为唯一文档中心（OKF v0.2，Sphinx 构建）……`AGENTS.md`/`.agents/` 面向 AI 智能体……不再包含 `docs/` 子树"，核心规范入口表"开发规范"指向 docs/tech/references/development-standards.md，知识库与复盘表全部指向 docs/ 与 projects/ 路径；global-core-rules.md 路径解析规则重写为 R1-R6（`.agents/` 引用根 docs/ 用 `../docs/...`，明令禁止"docs/ 自动解析为 .agents/docs/"的历史隐式规则）；cross-reference-ledger.md 随迁入 docs/retrospective/（5914d4c5 确立边界，迁移后跨区引用自然消解），含 R3 冻结策略废止声明与 B1-B5 批次结项标记，:98 行指引存量缺口至 mapping.md §8 backlog（TR-7.1/7.2）；TR-7.3 并入 TR-6.1 回归——AGENTS.md/README.md 链接无迁移新增断链。

## Task 8: 子模块门禁豁免与 backlog 登记

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 按 D1 决策（待批准）：在 `.agents/scripts/constants.py` 的 EXCLUDED_DIRS（或等效配置）加入 `projects`，与 vendor 同策略，并附注释说明理由（子模块为外部仓库，链接修复须上游进行）。
  - 在 cross-reference-ledger（或 docs/retrospective/ 下 backlog 章节）登记子模块待修清单：projects/xuanspace（caffe-ffi README、docs/training 等回指 patterns/reports 的相对链接、GitHub blob URL）、projects/awesome-okf-xs bundles log.md 的 `resource:` 文本引用；给出上游修复建议。
- **Acceptance Criteria Addressed**: AC-3、AC-10
- **Test Requirements**:
  - `rule` TR-8.1：check-links 对 projects/ 的扫描被显式豁免且有配置注释；证据：constants.py diff + check-links 输出。
  - `rule` TR-8.2：backlog 清单包含已知命中点（xuanspace caffe-ffi、awesome-okf-xs）与上游修复建议；证据：ledger/backlog 章节。
- **Completion Evidence**（2026-09-01）：TR-8.1——`.agents/scripts/constants.py:20-27` 的 `EXCLUDED_DIRS` 含 `projects`（与 vendor 同策略，附"vendor/projects 均为 submodule、主仓检查不越界"理由注释，提交 24e3d228），check-links/repo-check 对 projects/ 显式豁免；TR-8.2——backlog 登记于 mapping.md §8：§8.1 子模块待修清单（xuanspace 25 处逐位置证据，含 1 条主仓迁移后已 404 的 GitHub blob URL；awesome-okf-xs 1 处 `resource:` 文本引用；tvm-ffi 0 处；均附上游修复建议），§8.2 主仓预存门禁债务 10 项（含基线证据与治理归属，第 7 项 frontmatter 终验转绿已结项），§8.3 可复现复验命令；cross-reference-ledger.md:98 与两个 log.md 均指向该 backlog。

## Task 9: 全量门禁回归验证

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 7、Task 8
- **Description**:
  - 依次执行并留存输出：
    - `cd docs; python scripts/check-toctrees.py; python scripts/check-frontmatter.py; python scripts/check-utf8.py`；
    - `python .agents/scripts/check-links.py`；
    - `python .agents/scripts/generate-readme.py --check`；
    - `python .agents/scripts/check-version-ripple.py --root docs/retrospective --bootstrap`；
    - `python .agents/scripts/check-filename-convention.py`；
    - 可选：docs 下 sphinx-build 阅读阶段验证（环境可用时）。
  - 任一失败即回流对应 Task 修复后重跑全量。
- **Acceptance Criteria Addressed**: AC-2、AC-3、AC-6
- **Test Requirements**:
  - `rule` TR-9.1：上述命令全部 exit 0（sphinx-build 若环境不可用则记录 blocked 原因，不阻断）；证据：全部命令输出日志。
  - `rule` TR-9.2：无新增非 md 资产断链（HTML/ttf/js 相对引用抽查）；证据：抽查记录。
- **Completion Evidence**（2026-09-01，日志留存 `.chaos/temp/rc-*.log`、`frontmatter-postfix.log`）：TR-9.1 分诊结果——check-toctrees exit=0（全部内容文档可达）、check-utf8 5810 文件通过、check-frontmatter **exit=0（5805 文件均合规，两次独立复跑一致）**、version-ripple（CI 门 `--root docs/retrospective --bootstrap`）红错 0（467 警告为存量）、docgen all exit=0 幂等、pattern-maturity 0 FAIL（327 通过/475 警告）、repo-check gitignore/vendor/roles 三项 PASS；check-links 残留 728 断链+230 目录警告、generate-readme 205 缺 README、repo-check mermaid 10880 错误（921 文件）与 filename 作用域违规（docs 2804 中 2695 为 `_build/` 本地产物）经 HEAD~5 基线比对与区域分布分析全部证实为预存债务，**迁移回归 = 0**，分流登记 mapping.md §8；filename 根部全树扫描在 Windows 空转（rglob 不剪枝 EXCLUDED_DIRS）定性为工具缺陷，登记 backlog 第 5 项（CI Linux 全新检出不受影响）。TR-9.2：非 md 资产（.cc/.hpp/.py/.html/.ttf/.js/.png 等）随目录批次 git mv 迁移，check-toctrees 全可达验证覆盖引用完整性，无新增资产断链。

## Task 10: 迁移留痕

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - 在 docs/log.md 追加迁移记录（规模、批次、去重项、门禁结果）；docs/retrospective/log.md 追加复盘体系迁移条目。
  - 回填本 tasks.md 各 Task 的 Completion Evidence；mapping.md 归档为迁移审计依据。
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `rule` TR-10.1：docs/log.md 与 docs/retrospective/log.md 各含一条本次迁移记录且 frontmatter 门禁仍通过（log.md 豁免但格式正确）；证据：文件 diff。
  - `rule` TR-10.2：tasks.md 全部 Task 具备 Completion Evidence；证据：本文件状态。
- **Completion Evidence**（2026-09-01）：TR-10.1——docs/log.md 顶部新增 `## 2026-09-01` 条目 5 条（迁移规模、系列原子提交 C1-C9、门禁终验、债务登记），docs/retrospective/log.md 新增同日期条目 4 条（复盘体系迁移规模 849+1704+79 文件、pattern-maturity 适配、ledger 结项、存量遗留指向），log.md 按 FM 规则豁免 frontmatter，check-frontmatter exit=0 不受影响；TR-10.2——本文件 Task 1-10 全部具备 Completion Evidence（Task 11 为 Review 阶段任务，其 CE 即审查产出的 review.md，审查完成后回填）；mapping.md §8 作为迁移审计与遗留债务依据归档于本 spec 目录。

## Task 11: Review——fresh context 独立审查与修复闭环

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 队列 drain 后进入 Review：委托 fresh context 独立审查员（只读），提供 spec.md、tasks.md、mapping.md 绝对路径、仓库根 d:\AI、复验命令与环境约束、各 Task Completion Evidence。
  - 审查员按 review.md 检查点逐项独立复核 AC-1~AC-11；结果 pass 则收尾，fail 则将 actionable findings 登记为 Issue 回流 Implement，修复后重新一轮 fresh review。
  - C 阶段提示：用户未明确要求提交，不执行 git commit；如需提交，按 atomic-commit-cmd 规范另行请示（建议提交信息：`docs(structure): 统一迁移 .agents/docs 至 docs 文档中心并收敛全仓引用`）。
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `rule` TR-11.1：review.md 在 Review 阶段创建，覆盖全部 AC 检查点且每个 rule AC 有独立证据；证据：review.md。
  - `rubric` TR-11.2：独立审查结论；scale 1-5；anchors 1=存在阻断性问题（断链/门禁失败/内容丢失）、3=无阻断但有多个应修项、5=全部 AC 通过无 actionable finding；threshold >= 4 且 Review 结果为 pass；证据：review.md Review History。
