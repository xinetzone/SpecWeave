# .agents/docs 统一迁移至 docs/ 文档中心 Spec

## 方法论声明

本规范基于 **R-I-E-C-A-F-V 七概念方法论** 的「场景3：重构优化」链路 **I→F→A→C** 编写（session=`sc-20260831-agents-docs-migration`，depth=deep）：

| 概念 | 阶段 | 在本规范中的体现 |
|------|------|-----------------|
| I（Insight 洞察） | 问题诊断 | §1 背景与现状勘察——源侧/目标侧/门禁/引用四维事实 |
| F（First Principles 第一性原理） | 理想设计 | §4 迁移映射总纲——从"文档中心唯一性"与"门禁机制"推导落位 |
| A（Atomization 原子化） | 拆分方案 | tasks.md 的 11 个原子任务、分批迁移与分批链接改写 |
| C（Atomic Commit 原子提交） | 交付实施 | tasks.md 有序实施步骤；提交动作须用户另行明确授权 |

> 质量门：G1（事实可溯源）、G3（零断链验证）、G4（行动项原子化）内嵌于本规范。F 阶段映射表须经 V（对抗审查）验证——Review 阶段独立复核。

---

## 1. 概述（Overview）

- **Summary**：将旧文档容器 `.agents/docs/`（2698 个文件，其中 Markdown 2661 个）整体迁移至根 `docs/`（OKF v0.2 Sphinx 文档中心）下的恰当位置，同步完成 `.meta/toml` 元数据镜像迁移、全仓引用收敛与规范口径更新，迁移后全仓零断链、三道文档门禁全部通过。
- **Purpose**：结束双文档容器并存的历史局面。ACT-5 治理曾确立"`.agents/docs/retrospective/` 冻结新增、仅作历史归档"的 R3 策略；本任务依据用户新指令**取代 R3 冻结策略**，将旧容器内容一次性并入 `docs/`，使 `docs/` 成为唯一的人类文档中心，`.agents/` 仅保留面向智能体的 Core 规范层与 Tools 执行层。
- **Target Users**：仓库维护者与贡献者（人类读者，经 Sphinx 站点消费文档）；智能体与自动化脚本（经 `.agents/` 路由、CI 门禁与 docgen 工具消费路径）。

## 2. 背景与现状（I 阶段勘察事实）

### 2.1 源侧 `.agents/docs/`（2698 文件）

| 二级条目 | 文件数 | 性质 |
|---|---|---|
| `retrospective/` | 2632 | 复盘体系：patterns 849、reports 1704、templates 19、concepts 11、guides 7、frameworks 5、archives 10、assets 5、根级 21（17 个日期复盘 2026-07-06~2026-08-25 + hardcode-retrospective-report、meta-bootstrap-execution-log、prompt-extraction、terminalworld-benchmark-analysis、README） |
| `superpowers/` | 14 | plans 7 + specs 6 + README |
| `code-wiki/` | 8 | 源码学习 wiki（frontmatter `source` 指向 AGENTS.md 等） |
| `guides/` | 6 | thesis-writing-guide：1 HTML + 4 ttf + 1 mermaid.min.js（**孤儿资产**，全仓无入站链接） |
| `templates/` | 5 | 文档模板（README + 治理 checklist + 3 个 readme 模板） |
| `plans/` | 4 | 治理计划（act04-act08、bus-factor、q4-2026 + README，`type: index`） |
| `task-summaries/` | 4 | 任务执行总结（README 自定位"区别于事后复盘"） |
| `standards/` | 3 | 团队规范（README + cmd-log-specification + act-improvement-validation-template） |
| `architecture/` | 2 | README + multi-agent-collab |
| `test-plans/` | 2 | README + forum-bot-playwright-test-plan |
| `tools/` | 1 | docker-cache.md |
| `quality/` | 1 | mermaid-manual-fix-guide.md |
| 根级散文件 | 15 | project-overview、project-highlights、project-structure、roadmap、tech-stack、related-links、agent-roles、collaboration、development-standards、knowledge-base、raci-governance-standards、reuse-and-generalization、methodology-analysis-report、verification-automation、trae-project-adaptation-guide、README（边界说明） |

- 文件类型：`.md` 2661、`.json` 5、`.html` 4、`.txt` 4、`.png` 4、`.hpp` 4、`.py` 4、无后缀 4（.gitkeep/.gitignore）、`.ttf` 4、`.cc` 3、`.js` 1。非 Markdown 资产集中在 `retrospective/patterns/code-patterns/examples/`（C++ 代码样例）与 reports 下的 HTML/JSON/TXT 产物。
- frontmatter 合规率实测：可解析 YAML FM **2468**；含非空 `type` 仅 **677**；YAML 解析错误 **26**；无/无效 FM **167**；有 FM 但缺 `type` **1791**；含 `x-toml-ref` **1803**；README.md **466** 个、index.md **8** 个。
- `.meta/toml/.agents/docs/` 下有 **1718** 个 TOML 元数据镜像文件须随迁；`.meta/toml/` 已存在 `docs/` 镜像根。

### 2.2 目标侧 `docs/`（OKF v0.2 Sphinx 文档中心）

- 六板块：`general/`（通用知识，建设中）、`knowledge/`（OKF 知识库）、`refactor/`（重构）、`retrospective/`（复盘与模式库，含 patterns/ 与 reports/concepts/ 策展集）、`tech/`（本项目技术文档：concepts/ + references/）、`topics/`（设计洞见与深度研究，建设中）；配套 `scripts/`（门禁与修复器）、`tasks/`（invoke 任务）。
- 板块语义依据各 index.md 自述：`tech/` 承载"全部项目技术资产（项目介绍、快速开始、核心功能、贡献指南、变更日志）"；`topics/` 承载"设计哲学、方法论分析、演进研究"；`general/` 承载跨学科通用知识；`retrospective/` 承载复盘报告与可复用模式。

### 2.3 门禁机制（源码级核实，决定迁移成败）

- `docs/scripts/check-frontmatter.py`：`log.md` 全豁免；根 `index.md` 必须有含 `okf_version` 的 FM；**子目录 index.md 不允许有 FM**；**其余所有 .md（含 README.md）必须有可解析 YAML FM 且含非空 `type`**。
- `docs/scripts/check-toctrees.py`：toctree 引用必须解析到真实 .md 或含 index.md 的目录；从 `docs/index.md` BFS 沿 toctree 链，所有非 index、非 README.md 的 .md 必须可达；含 toctree 的 index.md 必须收录目录内全部条目；含内容子目录的目录必须有 index.md。
- `docs/scripts/fix-frontmatter.py`：按 PREFIX_RULES 推断 `type`（retrospective/reports→Report、retrospective/patterns→Pattern、retrospective/→Reference、tech/→Guide、refactor/→Report、general/topics→Concept、DEFAULT Reference）；无 FM 文件追加标准 FM；子 index.md 的 FM 自动剥离；26 个 YAML 错误先尝试模式 A/B 自动修复，失败转 MANUAL 清单。
- `docs/scripts/fix-toctrees.py`：为每个含内容目录自动建/更新 index.md 与 toctree（条目=子目录 index 或无 index 子目录的直接 md + 直接 md，排除 README/index/readme），保留已有 toctree 选项行、替换条目列表。
- `.agents/scripts/check-links.py`：全仓相对链接断链检查；SKIP 段含 `/external/`、`/playground/`、`/.temp/`、`/vendor/flexloop/` 等；`constants.py` 的 `EXCLUDED_DIRS = {".git","vendor",".venv","__pycache__","node_modules",".temp"}`（**`projects/` 与 `.trae/` 不在排除列表**）；支持 `--fix`（file:/// 转相对、层级校正、重命名映射）。
- `.agents/scripts/generate-readme.py`：`find_missing_readmes` 搜索根为 `docs/`；`get_p1_dirs` 已硬编码预期路径——**`docs/superpowers/plans`、`docs/superpowers/specs`、`docs/retrospective/assets`、`docs/retrospective/templates`、`docs/retrospective/reports/insight-extraction`、`docs/retrospective/reports/standards-tools`、`docs/retrospective/patterns/methodology-patterns`**（为"恰当位置"提供权威工具信号）；`LINK_CHECK_EXCLUDE_DIRS` 含 `docs/templates`（模板目录落位信号）。
- `.github/workflows/ci-quality-gates.yml`：`[2/16] check-links.py`、`[9/16] docgen.py all`、`[10/16] generate-readme.py --check`、**`[16/16] check-version-ripple.py --root .agents/docs/retrospective --bootstrap`（硬编码旧路径，迁移后必须改为 `docs/retrospective`）**。
- `.agents/scripts/constants.py:121-122`（docgen 导航常量 `.agents/docs/README.md`）、`.agents/scripts/docgen.py:5,819,1109`（导航生成覆盖旧 README）须适配。

### 2.4 引用分布（`.agents/docs` 字符串命中）

| 范围 | 文件数 | 处置 |
|---|---|---|
| `docs/` | 216（knowledge 193、retrospective 18、tech 4、index.md 1） | 链接改写（抽查 6/6 目标真实存在，为活链接） |
| 根目录 | 5：AGENTS.md（11 处）、README.md（15 处）、CONTRIBUTING.md、check_mermaid.py（陈旧 `d:\spaces\...` 绝对路径）、count_wikis.py（`base = d:\AI\.agents/docs\knowledge\learning`，已失效） | 链接/路径改写 |
| `.agents/`（非 docs） | 32：global-core-rules（8）、capability-registry、checklists、commands、17 个脚本（含 constants.py、docgen.py、check-version-ripple.py、hooks/pre_commit.py 等）、4 个 SKILL.md、4 个 templates | 链接/路径改写 |
| `apps/` | 24 | 链接改写（主仓库直管，可改） |
| `.github/` | 3（CI 工作流 2 + issue 模板 1） | 路径改写 |
| `.trae/specs/` | 157 | 历史 spec 档案，链接批量改写保活（见 §7 决策 D5） |
| `projects/`（git 子模块） | 多处：xuanspace（caffe-ffi 等经 `../../../../` 回指旧侧 patterns/reports，含 GitHub blob URL）、awesome-okf-xs bundles 的 log.md `resource:` 文本引用 | **不可直改**，门禁豁免 + backlog 登记（见 §7 决策 D4） |
| `vendor/` | — | check-links 已整体排除，无需处置 |

### 2.5 去重事实

- `.agents/docs/retrospective/reports/concepts/` 是新侧 `docs/retrospective/reports/concepts/` 策展集的**旧副本**；新侧为超集（如 milestone/ 多出 blog-to-okf-bundle、tvm-ffi-200、screenshot-tool 等）。
- `.agents/docs/retrospective/patterns/docker-template-pattern-extraction-20260722.md` 已迁至 `docs/retrospective/patterns/` 根（迁移先例：多模式汇总文件放 patterns/ 根），旧侧为副本。
- `docs/retrospective/patterns/methodology-patterns/` 新侧已策展（concepts/ 18 概念文件 + 3 根级模式文件 + index/log）；旧侧 `methodology-patterns/` 含 ai-collaboration 等约 80 文件的全集，须合并且同名文件以新侧为准（F 阶段逐文件 diff 验证）。

## 3. 目标与非目标

### 3.1 目标（Goals）

1. `.agents/docs/` 全部内容按 §4 映射总纲迁移至 `docs/` 下恰当位置，`.agents/docs/` 目录在工作树中消失；`.meta/toml/.agents/docs/` 镜像同步迁移。
2. 迁移后 `docs/` 三道门禁（check-toctrees、check-frontmatter、check-utf8）全部 exit 0；全仓 check-links 零断链；generate-readme、check-version-ripple、文件名规范检查全部通过。
3. 全仓引用收敛：`docs/`、根 AGENTS.md/README.md/CONTRIBUTING.md、`.agents/`、`apps/`、`.github/` 中不再存在指向 `.agents/docs/` 的活链接或硬编码路径。
4. 规范口径更新：AGENTS.md 文档边界条款、global-core-rules 路径解析规则、cross-reference-ledger（R3 冻结策略废止、B1-B5 批次结项）、capability-registry、CI 工作流、docgen/constants 适配单文档中心。
5. 子模块引用有明确处置（门禁豁免 + backlog 登记），不留下未声明的断链风险。

### 3.2 非目标（Non-Goals）

- **不修改** `projects/`、`vendor/` 子模块内任何文件（gitlink 追踪，本仓无法提交）。
- **不重写、不再加工**文档正文内容；仅做 frontmatter/toctree/链接/路径等机械治理，以及索引/边界说明类文件的必要更新。
- **不迁移、不改写** `.trae/specs/` 之外的历史档案（如 `.temp/`、playground）。
- **不改变** Sphinx 构建配置、主题与 `docs/conf.py` 既有设置。
- **不执行 git commit**：用户未明确要求提交；迁移完成后按 atomic-commit-cmd 规范另行请示。
- 不合并内容重叠的文档（如 project-overview 与 tech/concepts/intro 的重叠仅登记，不做内容融合）。

## 4. 迁移映射总纲（F 阶段第一性原理设计）

**根本原则**：①`docs/` 是唯一人类文档中心，落位服从板块语义（§2.2）；②工具内建信号（generate-readme `get_p1_dirs`、LINK_CHECK_EXCLUDE_DIRS、PREFIX_RULES）为权威落位依据；③门禁机制可机械治理的（FM/toctree）交给修复器，策展型索引进人工复核；④git mv 保留历史，去重必须显式登记。

### 4.1 目录级映射

| 源（`.agents/docs/` 下） | 目标（`docs/` 下） | 依据 |
|---|---|---|
| `retrospective/patterns/{analysis-cards,architecture-patterns,checklists,code-patterns,documentation-patterns,process-patterns}` | `retrospective/patterns/` 同名兄弟目录（含 code-patterns/examples 代码样例资产） | 复盘模式库归位 |
| `retrospective/patterns/methodology-patterns/` | `retrospective/patterns/methodology-patterns/` **合并**：旧侧独有文件全部迁入；同名文件以新侧策展版为准（F 阶段 diff 核验） | 新侧已策展 |
| `retrospective/patterns/docker-template-pattern-extraction-20260722.md` | **丢弃**（新侧 patterns/ 根已有正式版） | 迁移先例 |
| `retrospective/reports/<22 个分类目录>` | `retrospective/reports/` 同名兄弟目录（含 HTML/JSON/TXT 等非 md 资产随迁） | 复盘报告归位；generate-readme 信号确认 insight-extraction、standards-tools 落位 |
| `retrospective/reports/concepts/` | **丢弃**（新侧 reports/concepts/ 为超集策展集，F 阶段文件列表比对验证） | 去重 |
| `retrospective/{archives,assets,concepts,frameworks,guides,templates}` | `retrospective/` 同名并入 | 复盘配套资产；generate-readme 信号确认 assets、templates 落位 |
| `retrospective/*.md` 根级 21 文件 | 17 个日期复盘 + hardcode-retrospective-report + meta-bootstrap-execution-log + terminalworld-benchmark-analysis → `retrospective/reports/` 根；`prompt-extraction.md` → `retrospective/patterns/methodology-patterns/`（提示词工程模式）；`README.md` **不迁移**（新侧 retrospective/index.md 承担索引） | 报告归 reports、模式归 patterns |
| `superpowers/`（plans + specs + README） | `superpowers/`（顶层新板块） | generate-readme `get_p1_dirs` 权威信号 |
| `templates/` | `templates/`（顶层） | LINK_CHECK_EXCLUDE_DIRS 含 `docs/templates` |
| `code-wiki/` | `tech/code-wiki/` | 源码学习 wiki 属本项目技术资产 |
| `standards/` | `tech/standards/` | 团队技术规范属 tech 板块 |
| `plans/` | `retrospective/plans/` | 治理行动计划与复盘报告配套（ACT 系列） |
| `task-summaries/` | `retrospective/reports/task-reports/` 并入（README 中"区别于事后复盘"的定位说明保留） | 任务报告容器 |
| `architecture/multi-agent-collab.md` | `tech/concepts/` | 架构概念文档 |
| `tools/docker-cache.md`、`quality/mermaid-manual-fix-guide.md` | `tech/references/` | 工具/质量指南属技术参考 |
| `test-plans/` | `tech/test-plans/` | 测试计划属技术资产 |
| `guides/thesis-writing-guide/`（HTML+ttf+js 孤儿资产） | `_static/thesis-writing-guide/` | Sphinx 静态资产目录，不触发 md 门禁、无需 toctree 可达 |
| 根级 15 个项目文档 | 见 §4.2 细分 | tech/topics 板块语义 |
| `README.md`（旧容器边界说明） | **不迁移**（`docs/index.md` 承担总导航；其历史口径已过时） | 索引替代 |

### 4.2 根级 15 个项目文档落位

| 文件 | 目标 |
|---|---|
| project-overview、project-highlights、project-structure、roadmap、tech-stack、related-links、verification-automation、trae-project-adaptation-guide、agent-roles、collaboration、development-standards、raci-governance-standards、knowledge-base | `tech/references/`（项目级参考文档；避免与 tech/concepts/ 既有结构化章节冲突，内容重叠只登记不融合） |
| methodology-analysis-report、reuse-and-generalization | `topics/`（板块自述承载"方法论分析、演进研究、泛化复用"） |

> F 阶段（tasks.md Task 1）产出逐文件映射表 `mapping.md`，对上述每一条落位做文件级确认；如发现语义不符的个案，以映射表为准并在表中注明理由。

### 4.3 元数据镜像

- `.meta/toml/.agents/docs/`（1718 TOML）→ `.meta/toml/docs/` 合并迁移；同名 TOML 以内容比对确认（新侧优先）。
- 1803 个 md 的 `x-toml-ref` 路径批量改写：`.meta/toml/.agents/docs/...` → `.meta/toml/docs/...`（迁移后相对层级随文件新位置重算）。

## 5. 功能需求（Functional Requirements）

- **FR-1**：按 §4 映射总纲完成全部文件的物理迁移（git mv 优先，保留历史），去重丢弃项有显式清单。
- **FR-2**：`.meta/toml` 镜像随迁，全部 `x-toml-ref` 可解析到真实 TOML 文件。
- **FR-3**：迁移后 docs 树全部 .md 满足 frontmatter 门禁（含 type、子 index 无 FM、根 index 保留 okf_version）；26 个 YAML 错误经自动修复或人工修复清零。
- **FR-4**：docs 树全部含内容目录具备 index.md 且 toctree 无断链、无遗漏条目、全部非 README md 可达；策展型 index（docs/index、retrospective/index、patterns/index、reports/index、tech/index、superpowers 等）经人工复核保持可读策展结构。
- **FR-5**：全仓（docs、根、.agents、apps、.github、.trae/specs）指向 `.agents/docs` 的链接与硬编码路径全部改写为新位置；CI 工作流 `[16/16]` 路径改为 `docs/retrospective`；constants.py/docgen.py 适配。
- **FR-6**：AGENTS.md 文档边界条款改写为单文档中心口径；global-core-rules 路径解析规则更新；cross-reference-ledger 中 R3 冻结策略废止、B1-B5 批次结项、子模块 backlog 登记；capability-registry 等索引同步。
- **FR-7**：projects 子模块引用处置落地：check-links 门禁豁免配置 + backlog 清单（含 xuanspace caffe-ffi、awesome-okf-xs bundles log.md 等已知命中点）。
- **FR-8**：迁移过程在 docs/log.md（及相关板块 log.md）留痕。

## 6. 非功能需求（Non-Functional Requirements）

- **NFR-1（零断链）**：迁移后 `python .agents/scripts/check-links.py` 全仓 exit 0（豁免范围仅限 vendor/ 既有排除与经批准的 projects/ 子模块）。
- **NFR-2（门禁绿）**：check-toctrees、check-frontmatter、check-utf8、generate-readme --check、check-version-ripple（新路径）、check-filename-convention 全部 exit 0。
- **NFR-3（可审计）**：迁移以 git mv 为主，git 能识别 rename；去重/丢弃/不迁移项全部登记在 mapping.md，可逐项追溯。
- **NFR-4（不回归）**：不破坏既有 docs/ 内容与 Sphinx 构建（可选 sphinx-build 阅读阶段验证）；不修改子模块。
- **NFR-5（规范合规）**：新增/移动文件遵循文件名 kebab-case 纯英文禁中文、Markdown 表格整表替换、相对路径引用（禁 file:///）、根目录不新增文件。

## 7. 约束、假设与待批准决策

### 7.1 约束（Constraints）

- **技术**：Windows + PowerShell 环境（无 bash heredoc，脚本走临时 .py 文件）；git submodule 边界（projects/、vendor/ 不可直改）；门禁脚本规则见 §2.3；不得在仓库根目录新建文件。
- **业务**：遵循 Conventional Commits；用户未授权前不 commit；MDI v1.0 YAML frontmatter 规范；Markdown 引用用相对路径。
- **依赖**：fix-frontmatter.py / fix-toctrees.py / check-links.py --fix 为主要自动化手段；必要时允许扩展 fix-frontmatter 的 PREFIX_RULES 以覆盖 superpowers/、templates/ 等新路径（type 推断规则）。

### 7.2 假设（Assumptions）

- 新侧 `docs/retrospective/reports/concepts/` 为旧侧同名目录的超集（Task 1 以文件列表比对验证；若不成立，缺失文件回补迁入）。
- generate-readme `get_p1_dirs` 的硬编码路径代表仓库维护者对落位的官方预期。
- 旧侧 466 个 README.md 随迁后由 fix-frontmatter 补 type、由 toctree 门禁豁免可达性要求，无需人工逐个处理。
- `.meta/toml/docs/` 既有镜像与迁入镜像合并不冲突（同名以新侧为准，Task 1 抽查）。

### 7.3 待批准决策（Approve 阶段请用户确认）

- **D1**：`projects/` 子模块加入 check-links 排除（与 vendor/ 同策略——外部仓库的链接修复须在上游子模块仓库进行），并在 cross-reference-ledger 登记 backlog 清单。**建议批准**，否则迁移后主仓门禁必然因子模块断链失败且本仓无法修复。
- **D2**：`retrospective/reports/concepts/` 旧副本与 patterns 根重复文件去重丢弃（§2.5）。**建议批准**。
- **D3**：旧 `.agents/docs/README.md` 与 `retrospective/README.md` 等纯索引文件不迁移内容（由新侧 index 承担）。**建议批准**。
- **D4**：根级 15 个项目文档按 §4.2 落 tech/references 与 topics/。
- **D5**：`.trae/specs/` 157 个历史 spec 文件中的旧链接做批量改写保活（链接指向同一文档的新位置，档案语义无损），而非冻结豁免。**建议批准**。
- **D6**：thesis-writing-guide 孤儿 HTML 资产落 `docs/_static/`。

## 8. 验收标准（Acceptance Criteria）

### AC-1：物理迁移完整
- **Type**：`rule`
- **Given**：迁移任务执行完毕
- **When**：检查工作树
- **Then**：`.agents/docs/` 与 `.meta/toml/.agents/docs/` 均不存在；mapping.md 登记的全部源文件均有目标落点；去重丢弃项与登记清单一致
- **Pass Condition**：`Test-Path .agents/docs` 为 False；源侧文件数 = 迁入文件数 + 登记去重数；git status 中迁移项以 rename/move 为主
- **Evidence**：mapping.md 清单、git status 统计、PowerShell Test-Path 输出

### AC-2：docs 三道门禁全绿
- **Type**：`rule`
- **Given**：迁移与 FM/toctree 治理完成
- **When**：在 `docs/` 下依次运行 `python scripts/check-toctrees.py`、`python scripts/check-frontmatter.py`、`python scripts/check-utf8.py`
- **Then**：三个脚本均 exit 0，无 WARNING/ERROR
- **Pass Condition**：三条命令退出码均为 0
- **Evidence**：命令输出日志

### AC-3：全仓零断链
- **Type**：`rule`
- **Given**：链接改写与子模块豁免配置完成
- **When**：运行 `python .agents/scripts/check-links.py`
- **Then**：主仓范围零断链；projects/ 豁免在 constants 配置中显式存在且 backlog 清单登记完整
- **Pass Condition**：check-links exit 0；豁免配置与 backlog 文档可查
- **Evidence**：check-links 输出、constants.py 变更、cross-reference-ledger backlog 章节

### AC-4：全仓引用收敛
- **Type**：`rule`
- **Given**：改写完成
- **When**：全仓 Grep `.agents/docs`（排除 .trae/specs 历史档案中的结项说明、ledger 台账等显式历史记录）
- **Then**：AGENTS.md、根 README.md、CONTRIBUTING.md、`.agents/`、`apps/`、`.github/`、`docs/` 中无指向旧容器的活链接/硬编码；CI `[16/16]` 路径为 `docs/retrospective`；constants.py/docgen.py 无旧导航常量
- **Pass Condition**：Grep 命中项全部为显式历史记录（台账/日志/本 spec）；CI 与脚本路径验证通过
- **Evidence**：Grep 结果分类清单、CI 工作流 diff

### AC-5：元数据镜像完整
- **Type**：`rule`
- **Given**：.meta 迁移与 x-toml-ref 改写完成
- **When**：扫描 docs/ 下全部含 x-toml-ref 的 md
- **Then**：每个引用路径解析到 `.meta/toml/docs/` 下真实存在的 TOML 文件
- **Pass Condition**：解析失败数为 0
- **Evidence**：批量校验脚本输出

### AC-6：工具链适配通过
- **Type**：`rule`
- **Given**：全部改写完成
- **When**：运行 `python .agents/scripts/generate-readme.py --check`、`python .agents/scripts/check-version-ripple.py --root docs/retrospective --bootstrap`、`python .agents/scripts/check-filename-convention.py`
- **Then**：全部 exit 0
- **Pass Condition**：三条命令退出码均为 0
- **Evidence**：命令输出日志

### AC-7：落位恰当性
- **Type**：`rubric`
- **Dimension**：迁移落位与板块语义、工具内建信号的一致性
- **Scale**：1-5
- **Anchors**：1 = 大量文件落位与板块语义矛盾或工具信号冲突；3 = 主要目录落位正确，少数个案需人工调整；5 = 全部落位符合板块语义且与 generate-readme/LINK_CHECK_EXCLUDE_DIRS/PREFIX_RULES 信号一致
- **Pass Threshold**：>= 4
- **Evidence**：mapping.md 落位理由列、Review 阶段独立复核

### AC-8：策展型索引质量
- **Type**：`rubric`
- **Dimension**：自动生成 toctree 经人工复核后的可读性与策展质量
- **Scale**：1-5
- **Anchors**：1 = 策展页被自动条目列表覆盖、结构混乱；3 = 自动列表可用但失去人工分组与说明文字；5 = 策展页保留人工分组/说明/徽章等结构，条目完整且顺序合理
- **Pass Threshold**：>= 4
- **Evidence**：docs/index.md、retrospective/index.md、patterns/index.md、reports/index.md、tech/index.md 等复核记录

### AC-9：规范结项
- **Type**：`rule`
- **Given**：规范更新完成
- **When**：审查 AGENTS.md、global-core-rules.md、cross-reference-ledger.md
- **Then**：AGENTS.md 文档边界为单文档中心口径（.agents/ 仅 Core+Tools、docs/ 为唯一人类文档中心）；ledger 中 R3 冻结策略声明废止、B1-B5 批次标记结项；路径解析规则不再出现 .agents/docs 口径
- **Pass Condition**：三份文件 diff 符合上述要求且无旧口径残留
- **Evidence**：文件 diff、Grep 验证

### AC-10：留痕与 backlog
- **Type**：`rule`
- **Given**：迁移完成
- **When**：检查 docs/log.md 与 cross-reference-ledger
- **Then**：迁移动作有日志记录；子模块 backlog 含已知命中点清单（xuanspace caffe-ffi、awesome-okf-xs bundles 等）与上游修复建议
- **Pass Condition**：log 条目与 backlog 清单存在且信息完整
- **Evidence**：docs/log.md、ledger backlog 章节

### AC-11：独立审查通过
- **Type**：`rubric`
- **Dimension**：fresh context 独立审查对全部 AC 的复核结论
- **Scale**：1-5
- **Anchors**：1 = 存在阻断性问题（断链/门禁失败/内容丢失）；3 = 无阻断问题但有多个应修项；5 = 全部 AC 有独立证据通过，无 actionable finding
- **Pass Threshold**：>= 4 且 Review 结果为 pass
- **Evidence**：review.md（Review 阶段创建）

## 9. 开放问题（Open Questions）

- [ ] §7.3 决策 D1-D6 待用户在 Approve 阶段确认（均有建议方案）。
- [ ] Task 1 映射表核验后，若 reports/concepts 超集假设不成立，回补缺失文件（不影响整体方案）。
- [ ] tech/references/ 与 tech/concepts/ 既有内容的重叠文档清单（如 project-overview vs intro）仅登记不融合；是否在后续任务中融合，由用户另行决定。
