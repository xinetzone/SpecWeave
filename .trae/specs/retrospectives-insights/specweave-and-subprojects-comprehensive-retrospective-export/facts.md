---
type: Facts
id: "specweave-and-subprojects-comprehensive-retrospective-export-facts"
version: "1.0.0"
source: "git rev-list/log/shortlog + 目录实测（采集时点 2026-10-18，工作区 d:\\spaces\\SpecWeave）"
---

# R 阶段：事实清单

> 采集时点：2026-10-18。统计命令：`git -C d:\spaces\SpecWeave ...` / `Get-ChildItem -Recurse -File`。
> 本层只记录「发生了什么」，不含因果推断词。数值差异均标注来源与口径。
> 全量口径 = 2026-06-23 至 2026-10-18；增量窗口口径 = 2026-07-20 起（上一份全项目复盘时点 2026-07-19 之后）。

## A. 时间与提交规模

| 编号 | 事实 | 来源 |
|---|---|---|
| F-001 | 仓库首次提交日期为 2026-06-23；采集时点最后一条提交为 2026-10-18（`docs(spec): 回填 Task 7 原子提交结果并闭环审查记录`） | `git log --reverse --format="%ad\|%s" --date=short`；`git log -1` |
| F-002 | 全量提交数为 4381 | `git rev-list --count HEAD` |
| F-003 | 全量时间跨度为 2026-06-23 至 2026-10-18，计 118 天 | F-001 计算结果 |
| F-004 | 月度提交分布：2026-06 = 433、2026-07 = 1502、2026-08 = 1274、2026-09 = 812、2026-10 = 360 | `git log --format="%ad" --date=format:"%Y-%m"` 分组 |
| F-005 | 提交类型分布（全量）：docs 2336、feat 674、chore 518、fix 422、refactor 181、非规范前缀 158、test 47、ci 12、merge 12、perf 8、style 4、spec 3+specs 1、audit 2、build 2、update 1 | `git log --format="%s"` 前缀正则分组 |
| F-006 | docs 类提交占比 53.3%（2336/4381） | F-005 计算 |
| F-007 | 增量窗口（2026-07-20 起）提交数为 2854，占全量 65.1% | `git log --since=2026-07-20 --oneline \| Measure-Object` 计数 |
| F-008 | 增量窗口月度分布：2026-07 = 408、2026-08 = 1274、2026-09 = 812、2026-10 = 360 | 同 F-004 命令加 `--since` |
| F-009 | 增量窗口类型分布：docs 1424、chore 463、feat 414、fix 298、非规范前缀 100、refactor 93、test 35、perf 7、merge 6、ci 5、audit 2、build 2、spec 2、style 2、update 1 | 同 F-005 命令加 `--since` |
| F-010 | 高频提交 scope 前 10：retrospective 557、patterns 353、spec 243、knowledge 219、specs 196、client 137、scripts 126、submodules 109、submodule 98、learning 79、skills 79 | `git log --format="%s"` scope 正则分组 |

## B. 贡献者与仓库元数据

| 编号 | 事实 | 来源 |
|---|---|---|
| F-011 | `git shortlog -sn --all` 输出 7 个身份：xinetzone 2385、xinzo 1843、Trae Agent 69、liuxinwei 57、github-actions[bot] 23、Administrator 4、flexloop 1 | `git shortlog -sn --all` |
| F-012 | 前两位身份合计 4228 条，占该统计总和的 96.5% | F-011 计算 |
| F-013 | 两个身份的归属关系（是否同一自然人）在本次采集中未取得证据 | 待核项 |
| F-014 | 分支数 6；标签数 1（`pre-frontmatter-migration`） | `git branch -a`、`git tag` |
| F-015 | 2026-07-19 报告记载的贡献者身份数为 5（xinetzone 1462 为最高） | 基线报告 S1.1 |

## C. 四区域与资产规模

| 编号 | 事实 | 来源 |
|---|---|---|
| F-016 | 顶层区域为 4 类：`.agents/`（主权区）、`apps/`（内置应用）、`projects/`（第一方子项目）、`vendor/`（第三方依赖） | 磁盘 `AGENTS.md` 原文 |
| F-017 | `git submodule status` 输出 21 条：`projects/` 下 3 条 + `vendor/` 下 18 条；`.gitmodules` 的 `path =` 行为 21；全部条目无 `+`/`-` 前缀 | `git submodule status`、`.gitmodules` |
| F-018 | 3 个第一方子模块指针：awesome-okf-xs c3a497b8、daoapps.github.io f6c9a3f9、xuanspace e9417a7d | 同上 |
| F-019 | `projects/` 下另有 `monetize`、`tvm-ffi` 两个目录不含 `.git` | `Test-Path <dir>/.git` = False |
| F-020 | `projects/AGENTS.md` 子项目路由表登记 4 项：xuanspace、awesome-okf-xs、daoapps.github.io、monetize；目录实测含 6 项（多 tvm-ffi 与 `.agents`） | 路由表原文 + 目录列举 |
| F-021 | 各仓库提交数：主仓 4381（2026-06-23 起）、xuanspace 381（2026-07-24 起）、awesome-okf-xs 521（2026-08-18 起）、daoapps.github.io 18（2026-09-18 起） | 各仓库 `git rev-list --count HEAD` |
| F-022 | `.agents/skills/` 一级目录 172 个 | `Get-ChildItem .agents\skills -Directory` |
| F-023 | `.agents/` 资产计数：commands 16（md）、rules 137、protocols 18、roles 12、modules 9、templates 109、workflows 10 | 递归 md 计数（排除缓存目录） |
| F-024 | `.agents/scripts/`：一级 `.py` 146 个；递归 `.py` 659 个；`tests/test_*.py` 133 个 | 文件计数 |
| F-025 | py314 环境执行 `pytest --collect-only -q` 采集 2951 项，出现 1 个采集错误（`test_analyze_xlsx_test_report.py` 报 `ModuleNotFoundError: No module named 'openpyxl'`），耗时 50.22 秒，退出码 2 | 实测命令输出 |
| F-026 | 根 `docs/` md 计数（排除 `_build`/`.venv`/`__pycache__`）：全量 4094；`docs/knowledge` 500；`docs/retrospective/patterns` 952；`docs/retrospective/reports` 2269 | 递归计数 |
| F-027 | `docs/retrospective/reports` 分类计数前 6：insight-extraction 532、competitive-analysis 457、project-governance 375、task-reports 253、build-engineering 83、project-reports 82 | 一级子目录递归计数 |
| F-028 | `docs/retrospective/patterns/methodology-patterns` 下域名目录 10 个 | 目录列举 |
| F-029 | `.trae/specs/` 一级主题目录 42 个 | 目录列举 |
| F-030 | `apps/` 一级目录 13 个（排除 `.agents`/`shared`/`tests`） | 目录列举 |
| F-031 | `apps/AGENTS.md` 应用路由表登记 40 行（containers 4、docker-images 8、ai-agents 6、dev-tools 6、samples 10、根级 6） | 路由表原文逐行计数 |
| F-032 | `.github/workflows/` 工作流文件 14 个 | 目录列举 |
| F-033 | `ci-quality-gates.yml` 编号步骤为 `[1/16]`~`[16/16]`，另含 `[1.5/16] Submodule pointer consistency (S1 drift guard)`，及 4 个前置步骤（Checkout/Set up Python/Install dependencies/Verify script syntax）与 2 个附加步骤（Run unit tests with coverage、Verify generated docs are committed） | 工作流原文 `name:` 行 |
| F-034 | `.agents/docs/` 目录在采集时点不存在（`Test-Path` = False） | 磁盘实测 |
| F-035 | 根 `docs/` 被磁盘 `AGENTS.md` 声明为唯一文档中心；`.agents/docs/` 被声明为 2026-08-31 迁移后已废止路径 | 磁盘 `AGENTS.md` 原文 |

## D. 与 2026-07-19 基线的对比

| 编号 | 事实 | 来源 |
|---|---|---|
| F-036 | 提交数：基线 1495 → 采集 4381 | 基线报告 + F-002 |
| F-037 | 日均提交：基线 27 天 1495 条（55.4/天）→ 全量 118 天 4381 条（37.1/天） | 计算 |
| F-038 | 可复用模式 md：基线 493 → 采集 952（+459） | 基线 S1.5 + F-026 |
| F-039 | 复盘文档 md：基线 1317 → 采集 2269（+952） | 基线 S1.5 + F-026 |
| F-040 | `scripts` 递归 `.py`：基线 499 → 采集 659 | 基线 S1.4 + F-024 |
| F-041 | Skill 门面：基线 18 → 采集 172 | 基线 S1.4 + F-022 |
| F-042 | Spec 主题：基线 37 → 采集 42 | 基线 S1.5 + F-029 |
| F-043 | apps 应用数：基线 4 → 采集为路由表 40 行 | 基线 S1.5 + F-031 |
| F-044 | 知识库 md：基线 836（口径 `.agents/docs/knowledge`）→ 采集 500（口径 `docs/knowledge`），差 -336 | 基线 S1.5 + F-026 |
| F-045 | 贡献者身份数：基线 5 → 采集 7 | 基线 S1.1 + F-011 |
| F-046 | 基线报告 8 条行动项（ACT-01~08）在基线报告内均标记为已完成 | 基线报告 §四 |
| F-047 | 基线报告记载的最高可信度知识库规模为 248 个 OKF 知识包 | 基线报告 §执行摘要 |

## E. 增量窗口事件（2026-07-20 起）

| 编号 | 事实 | 来源 |
|---|---|---|
| F-048 | 子模块指针推进类提交（`chore(submodule*)`）全量 206 条，全部落在 2026-07-20 之后 | `git log` 前缀过滤（全量与 `--since` 两次计数同为 206） |
| F-049 | 2026-07-31 提交组含「秒悟大使推广项目」规格三件套与知识库（R-I-E-V 链路，11 条洞察） | `git log --since` 主题过滤 |
| F-050 | 2026-09-21 起 `xmnnrt.*` 轮出为主仓应用 `containers/offline-delivery` | `apps/AGENTS.md` 原文 |
| F-051 | 2026-09-25 `classical-festival-video` 由 `.trae/skills` 迁入 `.agents/skills`（随附五步 SOP、五要素补齐、索引登记） | `git log` 主题 |
| F-052 | 2026-09-28 修复「spec 重命名与 bundle 迁移」遗留的 50 处历史断链 | 同上 |
| F-053 | 2026-09-30 修复治理模式库仓库迁移遗留断链并校正一处错位互链 | 同上 |
| F-054 | 2026-10-05 新增 Meoo/Trae/WorkBuddy 部署工具链对比调研报告 | 同上 |
| F-055 | 2026-10-17 新增 `meoo-cli` 技能门面；2026-10-18 补登其入技能索引 | 同上 |
| F-056 | 2026-10-18 新增 `meoo-skill-publish` 技能；归档「seven-concepts-cmd 上架 Meoo 技能市场」规格三件套 | 同上 |
| F-057 | 2026-10-18 新增「秒悟赏金 IDEA·026 技能导航台」规格三件套并落盘 `apps/samples/skill-navigator`（数据层 39 条真实 Meoo Skill 条目） | 同上 + `apps/AGENTS.md` |
| F-058 | 2026-10-18 `awesome-okf-xs` 指针推进至 c3a497b8（喵呜 CLI/产品双知识包） | 同上 |
| F-059 | 增量窗口内主题含 `bundle`/`知识包`/`OKF` 的提交 469 条 | 主题关键词计数 |
| F-060 | 增量窗口内主题含 `meoo`/`秒悟`/`喵呜`/`赏金`/`竞赛` 的提交 15 条，最早一条日期为 2026-07-31 | 主题关键词计数 |
| F-061 | 主题含「迁移」的提交在窗口内 ≥8 条，其中 3 条日期为 2026-09-28、2026-09-30、2026-10-17 且内容为迁移后断链修复 | 主题关键词过滤 |
| F-062 | OKF 知识束（子模块 `awesome-okf-xs/doc/bundles`）：含 `index.md` 的目录（深度 ≤3）1083 个；束内 md 11794 篇；域名一级目录 9 个（guoxue/jishu/kexue/meta/sheke/wenxue/yishu/yixue/zhexue） | 递归计数 |
| F-063 | `apps/ai-agents/okf-knowledge-qa` 自述口径记载语料为「1307 束 / 73188 片段」 | `apps/AGENTS.md` 原文（自报口径） |
| F-064 | `.trae/specs/retrospectives-insights/` 下与秒悟/竞赛相关 spec 目录 6 个：analyze-meoo-contest-page、trae-solo-meoo-contest-plan、learn-trae-ai-contest-wiki、create-miaowu-bounty-plaza-okf-wiki、create-miaowu-docs-okf-wiki、create-miaowu-skill-navigator | 目录列举 |

## F. 工作区时点与遗留资产事实（只读声明）

| 编号 | 事实 | 来源 |
|---|---|---|
| F-065 | 采集时点 `git status --porcelain` 输出 12 条已修改（` M`）记录与 1 条未跟踪（`??`）记录 | `git status --porcelain` |
| F-066 | 已修改文件清单：`.agents/scripts/lib/checks/sensitive_info.py`、`.agents/scripts/tests/test_check_sensitive_info.py`、`.agents/scripts/tests/test_sensitive_info_shell.py`、`apps/docker-images/devcontainer-base/docs/known-issues-py314t-tests.wiki.md`、`docs/knowledge/tech/openkylin-docs-wiki/references/ai-sdk-ocr-poc.md`、`docs/knowledge/tech/openkylin-docs-wiki/references/source-inventory.md`、`docs/knowledge/tech/python-314t-conda-env-usage.md`、`docs/retrospective/archives/spec-working-notes/classics-knowledge/jianshu-blogs-to-okf-wiki/facts.md`、`docs/retrospective/patterns/code-patterns/multi-entrypoint-config-unification.md`、`docs/topics/index.md`、`docs/topics/travel/xiaoshan-indoor-date-2026.md`（未跟踪） | 同上 |
| F-067 | 本次复盘全程只读：未修改、未回滚 F-065/F-066 所述在途改动 | 本任务执行声明 |
| F-068 | 根目录 `check_mermaid.py` 存在，其 `BASE_DIR` 常量值为 `d:\spaces\SpecWeave\.agents\docs\knowledge\learning\08-systems-infrastructure\wsl-wiki`（该路径属已废止的 `.agents/docs/` 子树）；仓库内 Mermaid 检查的实际实现位于 `.agents/scripts/lib/checks/mermaid.py`，由 `.agents/scripts/repo-check.py` 的 `mermaid` 子命令调用；`CLAUDE.md` 仍以 `python check_mermaid.py` 列为提交前验证脚本 | 文件内容实测、`repo-check.py` 第 42~52 行、`CLAUDE.md` 第 51 行 |
| F-069 | 采集时点之后（同一日内）主仓 HEAD 前移 2 条提交：`960322e6f docs(security): 脱敏公开文档中真实本机用户目录路径`、`46f3fbcaa feat(scripts): 敏感检查对docs公开文档个人路径升级HIGH阻断`；该 2 条非本次复盘任务所为，本任务未创建任何 git 提交。复核时点重跑的同口径计数随之变化：提交数 4383（F-002 为采集时点值 4381）、窗口提交 2856（F-007 为 2854）、`xinzo` 身份计数 1845（F-011 为 1843） | `git log -4`、`git rev-list --count HEAD` |

## 抽查记录（回溯验证）

| # | 抽查事实 | 复现命令 | 结果 |
|---|---|---|---|
| 1 | F-002 | `git rev-list --count HEAD` | 4381 |
| 2 | F-004 | `git log --format="%ad" --date=format:"%Y-%m" \| Group-Object` | 433/1502/1274/812/360 |
| 3 | F-007 | `git log --since=2026-07-20 --oneline \| Measure-Object` | 2854 |
| 4 | F-011 | `git shortlog -sn --all` | 7 行，与记录一致 |
| 5 | F-017 | `git submodule status` | 21 条（projects 3 + vendor 18），无 `+`/`-` |
| 6 | F-021 | 三仓库 `git rev-list --count HEAD` | 381/521/18 |
| 7 | F-022 | `Get-ChildItem .agents\skills -Directory` | 172 |
| 8 | F-025 | `pytest --collect-only -q` | 2951 collected, 1 error |
| 9 | F-026 | 递归 md 计数 | 952（patterns）/2269（reports） |
| 10 | F-033 | 工作流 `name:` 行过滤 | `[1/16]`~`[16/16]` + `[1.5/16]` |
| 11 | F-062 | 束目录 `index.md` 探测 | 1083 |

命中率 11/11（100%）。
