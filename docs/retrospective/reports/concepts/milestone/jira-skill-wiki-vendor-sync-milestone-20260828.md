---
id: "milestone-jira-skill-wiki-vendor-sync-20260828"
title: "Jira Skill Wiki 供应商源码同步里程碑复盘报告"
date: "2026-08-28"
completion_date: "2026-08-28"
type: "Report"
description: "基于 vendor/jira-skill v3.29.0 正式子模块同步更新 OKF Wiki 教程的里程碑复盘，覆盖初次转换、子模块引入、供应商同步三次提交的完整过程"
status: "stable"
source: ".trae/specs/migration-archival/jira-skill-wiki-vendor-sync/"
milestone-name: "Jira Skill Wiki 供应商源码同步"
time-range: "2026-08-28 16:17 — 17:09（约52分钟，3次提交）"
methodology: "七概念方法论（R→I→E→V→C链路，standard深度，含4视角对抗审查）"
quality-gates:
  G1: "事实无因果词 ✅（28条事实）"
  G2: "洞察四元组完整 ✅（3条洞察）"
  G3: "模式可迁移验证 ✅（1个模式）"
  G4: "行动项原子化 ✅"
  V: "4视角对抗审查 ✅"
tags: ["里程碑复盘", "七概念", "方法论编排", "OKF", "vendor-sync", "jira-skill", "信源稳定性", "frontmatter合规"]
generated: { by: "process:seven-concepts-cmd", at: "2026-08-28T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T00:00:00Z" }
stale_after: "2027-08-28"
---

<!-- meta_type: retrospective -->

# Jira Skill Wiki 供应商源码同步里程碑复盘报告

> **方法论编排**：七概念 R→I→E→V→C 链路（里程碑复盘场景，standard 深度，启用4视角对抗审查）
> **复盘对象**：jira-skill Wiki 从临时克隆信源迁移至 vendor 子模块的完整过程（3次提交）
> **交付日期**：2026-08-28
> **复盘日期**：2026-08-28
> **session**：sc-20260828-jira-wiki-milestone

---

## 一、R 阶段：事实清单（28条）

> G1 质量门：✅ 通过（28条事实均为可验证的客观陈述，无"因为/所以/导致/错误/失误"等因果推断词或主观判断词）

### 1.1 时间线与提交记录

| 编号 | 事实 |
|------|------|
| F-001 | Commit 209d5bfc 于 2026-08-28 16:17:34 提交，信息为"docs(knowledge): jira-skill-wiki转换为OKF v0.2知识包"，27 文件变更，+2519/-133 行 |
| F-002 | Commit edda3939 于 2026-08-28 16:29:56 提交，信息为"chore(vendor): 引入 jira-skill 第三方子模块 v3.29.0"，5 文件变更，+11 行 |
| F-003 | Commit 189e5f43 于 2026-08-28 17:09:30 提交，信息为"docs(knowledge): 同步jira-skill Wiki信源至vendor子模块并修正OKF v0.2格式合规"，21 文件变更，+501/-130 行 |
| F-004 | 三次提交时间跨度为 51 分 56 秒（16:17:34 至 17:09:30） |

### 1.2 初次转换（Commit 209d5bfc）

| 编号 | 事实 |
|------|------|
| F-005 | 初次转换使用 `.chaos/libs/tests/jira-skill/` 临时克隆目录作为源码信源 |
| F-006 | 初次转换生成的 Wiki 包含 22 个 Markdown 文件：index.md + log.md + concepts/（10篇+索引）+ examples/（3篇+索引）+ references/（3篇+索引）+ README.md |
| F-007 | 初次转换的 frontmatter 使用块格式：`generated:` 下嵌套 `by:` 和 `date:` 字段 |
| F-008 | source-code.md 记录测试文件数为"23个测试文件" |
| F-009 | 01-architecture.md 记录 jira-communication/references/ 为"16 份按主题拆分的参考文档" |
| F-010 | api-reference.md 的 changelog.py 部分列出 3 个函数：extract_status_transitions、compute_time_in_status、classify_transition |
| F-011 | 初次转换的 Review R1 审查结果为 pass |
| F-012 | 初次转换使用 source-code-to-okf-wiki 技能的 R→I→E→V→C 五阶段工作流 |
| F-013 | 初次转换规格目录为 `.trae/specs/okf-wiki-ecosystem/jira-skill-okf-wiki/`，含 spec.md、tasks.md、review.md、facts.md、insights.md |

### 1.3 子模块引入（Commit edda3939）

| 编号 | 事实 |
|------|------|
| F-014 | vendor/jira-skill 以 third_party 类型注册为 git submodule，模式 160000，无 branch 字段 |
| F-015 | 远程仓库地址为 `git@github.com:netresearch/jira-skill.git` |
| F-016 | 版本固定于 v3.29.0 tag，commit hash 为 b0dba28674f768242411b256fa316f9f27c84b6c |
| F-017 | 许可证为 MIT AND CC-BY-SA-4.0（双许可） |
| F-018 | `.chaos/libs/tests/jira-skill/` 临时克隆目录在子模块引入后被删除 |

### 1.4 供应商同步（Commit 189e5f43）

| 编号 | 事实 |
|------|------|
| F-019 | 同步更新规格目录为 `.trae/specs/migration-archival/jira-skill-wiki-vendor-sync/`，含 spec.md（9条AC）、tasks.md（8个任务）、review.md |
| F-020 | 7 处 `file:///` URL 从 `.chaos` 路径更新为 `file:///d:/AI/vendor/jira-skill/`（source-code.md 3处、api-reference.md 4处） |
| F-021 | log.md 中 1 处 Windows 路径从 `d:\AI\.chaos\libs\tests\jira-skill` 更新为 `d:\AI\vendor\jira-skill` |
| F-022 | 17 个文件的 frontmatter 从块格式 `date:` 转换为 OKF v0.2 inline flow `at:` 格式 |
| F-023 | 根 index.md 仅含 `generated` 字段无 `verified` 字段，其余 16 个内容文件均含 generated+verified |
| F-024 | 测试文件数修正为"24个 test_*.py + conftest.py（共25个 Python 文件）" |
| F-025 | 参考文档数修正为"17 份按主题拆分的参考文档" |
| F-026 | changelog.py 函数从 3 个补全为 7 个，新增 parse_jira_datetime、extract_status_transitions_with_authors、find_transition_window、format_timedelta |
| F-027 | pyproject.toml 实际包含 17 行，仅含 `[tool.ruff]` 和 `[tool.bandit]` 配置段，无 `[project]` 表；运行时依赖通过 PEP 723 内联元数据声明 |
| F-028 | V 阶段执行了 100 处 bundle-relative 交叉链接验证，全部目标文件存在 |

### 1.5 过程与工具

| 编号 | 事实 |
|------|------|
| F-029 | 13 个概念/示例文件的 frontmatter 通过 PowerShell 批量脚本替换完成 |
| F-030 | 内容修正（数字校正、API 补全、路径替换）通过 Edit 工具逐个完成 |
| F-031 | 补全的 4 个函数名通过 Grep `^def ` 在源码 changelog.py 中验证存在 |
| F-032 | V 阶段发现 1 个问题：log.md 初始描述"8处file:///URL"计数不精确，修正为"7处file:///URL + 1处Windows路径" |
| F-033 | 同步更新中未新增或删除任何 Wiki 文件（22 个文件保持不变） |
| F-034 | 内容保留度 rubric 评分为 5/5，正文仅做必要事实修正 |
| F-035 | atlassian-python-api 依赖在 PEP 723 中固定为 `>=3.41.0,<4`，不升级到 v4 |

---

## 二、I 阶段：核心洞察（3条）

> G2 质量门：✅ 通过（3条洞察均包含完整四元组：陈述+证据+反常识+行动，维度独立不重叠）

### 洞察 I-1：临时信源的"路径断裂延迟"现象

- **陈述**：以临时克隆目录为信源生成的文档，其 `file:///` 引用在信源目录被清理后立即断裂，但断裂在文档生成时不可见——审查验证的是内容准确性而非信源持久性
- **证据**：F-005（使用 .chaos 临时克隆）、F-018（临时目录被删除）、F-020（7处URL断裂）、F-011（Review R1 通过但未发现路径问题）
- **反常识**：初次转换的 Review R1 标记为 pass，验证了 API 名称和交叉链接，但未验证信源路径的持久性。审查通过 ≠ 引用可持续——内容正确和链接可达是两个独立的质量维度
- **行动**：在 source-code-to-okf-wiki 技能的 V 阶段增加"信源持久性检查"步骤：(1) 分类信源为 stable/temporary；(2) temporary 信源必须在生成前升级为 stable（如 git submodule）或标记预期生命周期；(3) 删除临时目录前 Grep 文档中的路径引用

### 洞察 I-2：计数类事实的"人工审查盲区"

- **陈述**：文档中关于源码文件数量的陈述（测试文件数、参考文档数、API函数数）在人工审查中系统性地漏检，因为审查者倾向于验证"名称是否存在"而非"数量是否完整"
- **证据**：F-008（写23实际25）、F-009（写16实际17）、F-010（列3实际7）、F-011（R1 pass未发现）、F-031（Grep `^def` 可轻易发现遗漏）
- **反常识**：API 名称通过 Grep 验证了存在性（21个脚本+10个关键API），但函数总数没有通过同样的 Grep 计数来验证。验证"样本存在"和验证"全集完整"需要不同的检查策略——前者用 Grep 匹配，后者需要 Glob 计数 + 集合比对
- **行动**：在 V 阶段检查清单中增加"计数断言验证"：对文档中所有"X个文件/Y份文档/Z个函数"类陈述，自动执行 Glob/Grep `^def` 计数并与文档数字比对

### 洞察 I-3：规范演进的"回溯性不合规"技术债

- **陈述**：当规范格式要求发生变化（OKF frontmatter 从块格式 `date:` 演进为 inline flow `at:`），已发布的文档在无任何内容变更的情况下变为不合规，这种技术债不是由错误引起而是由标准演进引起
- **证据**：F-007（初次使用块格式 date:）、F-022（17个文件需转为 inline flow at:）、F-011（初次转换时按当时规范审查通过）、F-033（同步更新中22个文件无一增删）
- **反常识**：初次转换在生成时遵循了当时的格式规范并通过了审查，但规范演进使"正确的"变成了"错误的"。这不同于传统技术债（由妥协或疏忽引起），而是由外部标准变化引起的"被动技术债"——预防方式不是更仔细的审查，而是格式与内容的解耦和自动化迁移
- **行动**：(1) 文档 frontmatter 中声明 `okf_version` 以标记合规版本；(2) 开发格式迁移脚本（如本次 PowerShell 批量替换可固化为工具）；(3) 在 CI 中加入 frontmatter 格式检查，使规范演进时能批量发现不合规文件

---

## 三、E 阶段：模式萃取（1个）

> G3 质量门：✅ 通过（模式名称4-8字、有触发场景与边界、3+反模式来自实际案例、有检验标准、有跨场景迁移示例）

### 模式 E-1：信源稳定性门（Source Stability Gate）

- **ID**: `source-stability-gate`
- **名称**: 信源稳定性门
- **触发场景**：
  - 适用于：从外部源码/仓库生成包含 `file:///` 或绝对路径引用的文档时
  - 适用于：AI 智能体基于本地克隆/临时目录生成知识库时
  - 不适用于：纯外部 URL 引用（https:// 不受本地文件生命周期影响）
  - 不适用于：临时笔记/草稿（不需要长期持久性）
- **核心做法**（5步）：
  1. **信源分类**：在生成文档前，将所有信源路径分类为 `stable`（git submodule、系统安装目录、版本化发布包）或 `temporary`（临时克隆、/tmp、.cache、开发者个人目录）
  2. **临时信源升级**：若信源为 temporary，在生成文档前将其升级为 stable——注册为 git submodule、复制到 vendor/ 目录、或记录确切的 commit hash + 获取方式
  3. **路径引用生成**：文档中的 `file:///` 引用只指向 stable 信源；若必须引用 temporary 信源，标注 `transient: true` 和预期清理日期
  4. **清理前扫描**：删除任何临时目录前，执行 `grep -r "<目录路径>" docs/` 确认无文档引用
  5. **持久性验证**：V 阶段对所有 `file:///` URL 执行 `Test-Path` 验证，并额外检查信源类型是否为 stable
- **反模式**（来自本次案例）：
  1. **生成即遗忘**：从临时克隆生成文档后直接删除克隆目录，不更新文档中的路径引用（本次 F-005 + F-018）
  2. **审查只看内容不看信源**：Review 验证了 API 名称和交叉链接，但未验证 `file:///` 路径指向的目录是否会持续存在（本次 F-011 + F-020）
  3. **绝对路径绑定开发者环境**：在文档中硬编码 `d:\AI\.chaos\libs\...` 等开发者个人目录路径，换机器或换用户即断裂
- **检验标准**：
  - 文档中所有 `file:///` URL 指向的路径在全新克隆上可解析
  - 信源路径中不含 `.chaos`、`.tmp`、`/tmp/`、`AppData/Local/Temp` 等临时目录特征
  - 每个信源在文档 frontmatter 的 `sources` 中有对应的 stable 类型标注
- **跨场景迁移示例**：
  - **场景A（当前）**：OKF Wiki 生成——从 git submodule 信源生成 API 参考文档
  - **场景B（代码文档）**：Sphinx/MkDocs 文档生成——`conf.py` 中引用的源码路径应指向已安装包或 git submodule，而非开发者的 virtualenv 路径
  - **场景C（AI训练数据）**：RAG 知识库的文档索引中记录的文件路径应指向版本化数据目录，而非下载缓存目录

---

## 四、V 阶段：4视角对抗审查

> V 门：✅ 通过（4视角共12条审查意见，采纳4条对报告进行修正）

### 🔴 视角1：魔鬼代言人

| # | 攻击点 | 回应/修正 |
|---|--------|-----------|
| V-1 | 3条洞察是否都是"正确的废话"？"临时路径会断裂"和"人工计数会出错"是常识，反常识性不足 | I-1 的反常识在于"审查通过但路径仍然断裂"——审查维度的盲区比"临时路径不可靠"更深层；I-2 的反常识在于"验证了存在性但没验证完整性"——这是两种不同的验证策略。洞察价值不在于现象本身，而在于指出了现有流程的具体盲区 |
| V-2 | 52分钟3次提交是否构成"里程碑"？这更像是一个快速修复任务 | 时间跨度短不影响里程碑的复盘价值。本次任务涉及3个不同性质的提交（初次转换2519行、子模块引入、同步修正501行），且暴露了跨提交的流程问题，符合里程碑复盘的"完整交付单元"定义 |
| V-3 | F-035（atlassian-python-api pin 在 <4）与本次复盘主题无关，属于无关事实 | 保留。该事实记录了源码的依赖约束特征，未来版本同步时是关键决策上下文，属于"不可从代码库重新推导的外部资源坐标"类事实 |

### 🟢 视角2：新人视角

| # | 攻击点 | 回应/修正 |
|---|--------|-----------|
| V-4 | OKF、Bundle、frontmatter inline flow 等术语未解释 | 已在洞察 I-3 中补充"OKF frontmatter 从块格式 `date:` 演进为 inline flow `at:`"的具体格式对照示例；报告 frontmatter 的 tags 包含相关术语便于检索。完整术语定义见 OKF 规范文档 |
| V-5 | 为什么初次转换不用 vendor 子模块而用 .chaos 临时目录？ | 时间线显示（F-001 → F-002），初次转换在 16:17 完成，子模块在 16:29 才引入——初次转换时子模块尚不存在。这正是洞察 I-1 所描述的问题：文档生成先于信源稳定化 |
| V-6 | "信源稳定性门"模式的第一步如何判断 stable vs temporary？有没有可操作的判据？ | 已补充具体判据：stable 包括 git submodule、系统安装目录、版本化发布包；temporary 包括临时克隆、/tmp、.cache、开发者个人目录。路径中含 `.chaos`/`.tmp`/`/tmp/`/`AppData/Local/Temp` 即为 temporary |

### 🟠 视角3：老板视角

| # | 攻击点 | 回应/修正 |
|---|--------|-----------|
| V-7 | 初次转换的缺陷（3个计数错误+7个断链）在52分钟后就需要修复，返工成本是多少？ | 同步提交 501 增 130 删，其中约 100 行来自 frontmatter 格式转换（规范演进），约 30 行来自事实修正和 API 补全（初次缺陷），约 280 行来自规格文档。初次缺陷的直接返工量约 30 行修改，但加上规格编写、V阶段验证和审查，总耗时约 40 分钟 |
| V-8 | V阶段只发现1个问题（log.md计数不精确），是否说明验证不够充分？ | V 阶段验证了9条AC，执行了 Grep `.chaos` 零匹配、Grep `generated:{` 计数17、Grep `^def` 函数验证、100处链接检查、pyproject.toml 逐行比对、git diff 内容保留度评估。发现的1个问题属于文档自描述的精确性，非功能性缺陷。验证覆盖面较全面 |
| V-9 | 模式萃取只有1个，是否太少？ | 里程碑复盘场景标准预期为1-2个模式。本次萃取的"信源稳定性门"模式具有明确的跨场景迁移性（代码文档、AI训练数据等），质量优先于数量。洞察 I-2 和 I-3 也可在未来积累更多案例后独立萃取为模式 |

### 🔵 视角4：未来视角

| # | 攻击点 | 回应/修正 |
|---|--------|-----------|
| V-10 | OKF 规范如果继续演进到 v0.3，是否还需要批量修改17个文件？ | 这正是洞察 I-3 提出的问题。建议的行动项包括开发格式迁移脚本和在 CI 中加入 frontmatter 格式检查，将下次规范演进的迁移成本从"手动修改17个文件"降低为"运行脚本+验证" |
| V-11 | jira-skill 发布 v4 时（atlassian-python-api 升级），Wiki 同步流程是什么？ | 当前无自动化同步机制。vendor 子模块固定在 v3.29.0，版本升级需要：(1) 更新子模块到新 tag；(2) 重新运行 source-code-to-okf-wiki 技能做差异对比；(3) V阶段验证。信源稳定性门模式确保了路径不会再断裂，但内容同步仍需人工触发 |
| V-12 | "信源稳定性门"是否应该直接内置到 source-code-to-okf-wiki 技能中而非仅作为文档模式？ | 是的，这是最佳落地路径。模式 E-1 的核心步骤可转化为技能的预检清单（pre-flight checklist），在 R 阶段开始前自动执行信源分类和持久性验证。本次复盘的 C 阶段行动项已包含此建议 |

### V 阶段修正记录

| 修正项 | 来源 | 修正内容 |
|--------|------|----------|
| V-6 | 新人视角 | 补充了 stable/temporary 的具体路径判据 |
| V-5 | 新人视角 | 在洞察 I-1 中补充了时间线解释（初次转换时子模块尚未引入） |
| V-12 | 未来视角 | 在行动项中增加"将信源稳定性门内置于 source-code-to-okf-wiki 技能" |
| V-3 | 魔鬼代言人 | F-035 保留但标注了保留理由 |

---

## 五、行动项

| # | 行动项 | 类型 | 优先级 | 状态 |
|---|--------|------|--------|------|
| A-1 | 在 source-code-to-okf-wiki 技能的 V 阶段检查清单中增加"计数断言验证"：对文档中所有"X个/Y份/Z个"类陈述执行 Glob/Grep 计数比对 | 流程改进 | high | ✅ 已完成（2026-08-29，技能 v1.3.0：V 阶段检查清单第 8 项 + Prompt 模板计数断言项 + L2 模式文档同步；首次实践即 GATE-SPS 全量扫描"15 克隆/298 处引用"均以工具输出为准，提交 1ed76273） |
| A-2 | 将"信源稳定性门"模式的5步预检流程内置于 source-code-to-okf-wiki 技能的 R 阶段之前 | 工具增强 | high | ✅ 已完成（2026-08-29，技能 v1.3.0 阶段0 Pre-flight 预检/G0 质量门：信源分类→临时信源升级（submodule 固定不可变 tag+hash）→路径只指 stable→清理前扫描→持久性 audit；配套 GATE-SPS 工具 check-source-path-stability.py，提交 42b6c8e6/1ed76273） |
| A-3 | 开发 frontmatter 格式迁移脚本（块格式 ↔ inline flow），固化本次 PowerShell 批量替换逻辑为可复用工具 | 工具建设 | medium | ⊙ 已由现有工具兑现，无需新建（2026-08-29 核查：`.agents/scripts/migrate-frontmatter.py` 薄封装 + `lib/migrate_frontmatter/` 完整包已提供 scan/convert/rollback/verify/report 能力；`check-frontmatter.py` 第 5 条已内置"扁平结构（无多行缩进嵌套）"门禁） |
| A-4 | 在 CI 中加入 frontmatter 格式检查（Grep `  date:` 零匹配 + Grep `generated: {` 计数），使规范演进时可批量发现不合规文件 | CI增强 | medium | 待执行（2026-08-29 核查：ci-check.ps1 流水线中尚无 frontmatter 格式检查项，check-frontmatter.py 未接入 CI） |

---

## 六、复盘结论

本次里程碑在52分钟内完成了3次提交，实现了 jira-skill Wiki 从临时克隆信源到正式 vendor 子模块的迁移。初次转换暴露了三类问题：

1. **信源持久性盲区**（I-1）：审查验证内容但不验证信源生命周期
2. **计数完整性盲区**（I-2）：验证 API 存在性但不验证数量完整性
3. **规范演进被动债**（I-3）：标准变化使已审查通过的文档回溯性不合规

萃取的"信源稳定性门"模式提供了5步可操作的预防流程，可迁移至代码文档生成、AI训练数据索引等场景。4项行动项聚焦于将复盘发现转化为 source-code-to-okf-wiki 技能的内置检查和工具增强。

---

## 附录：关键提交索引

| Commit | 时间 | 类型 | 文件数 | 增/删行 |
|--------|------|------|--------|---------|
| [209d5bfc](file:///d:/AI/.git) | 16:17:34 | docs(knowledge) | 27 | +2519/-133 |
| [edda3939](file:///d:/AI/.git) | 16:29:56 | chore(vendor) | 5 | +11 |
| [189e5f43](file:///d:/AI/.git) | 17:09:30 | docs(knowledge) | 21 | +501/-130 |
| [42b6c8e6](file:///d:/AI/.git) | 2026-08-29 | feat(scripts) | 2 | +863 |
| [1ed76273](file:///d:/AI/.git) | 2026-08-29 | docs(skill) | 4 | +117/-13 |
| （本提交） | 2026-08-29 | docs(retrospective) | 2 | 行动项 A-1/A-2 闭环回写（A-3 标注已兑现、A-4 保持待执行） |
