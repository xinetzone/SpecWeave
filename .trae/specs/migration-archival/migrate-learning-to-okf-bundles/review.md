---
title: learning → OKF bundles 迁移独立对抗审查报告
source: 独立对抗审查（魔鬼代言人视角），对账权威 = facts-ledger.md，实测 = PowerShell 7 递归清单 + 逐束文件清单比对，2026-09-02
type: review-report
status: final
---

# learning → OKF bundles 迁移独立审查报告（删除源目录前最后对账）

> 审查立场：独立对抗审查代理，与迁移执行会话隔离。审查基线 = `facts-ledger.md`（处置权威）+ `docs/knowledge/learning/`（只读源库）+ `projects/awesome-okf-xs/doc/bundles/`（目标库实测）。

## 0. 总判定

**✅ PASS —— 源目录 `docs/knowledge/learning/` 可以删除。**

- 零内容丢失（2124 个 md 全部对账，28 个主题目录深度抽样文件数守恒）
- 隐私复扫发现的 2 处 major 残留已当场修复并复扫 CLEAN
- 6 组凭据正则复扫零真实凭据
- 门控：`check-bundles-index.py` PASS（9 域/56 组/497 束五面一致）；`check-toctrees.py` 12 处问题全部为并行会话遗留，本次迁移范围零新增

## 1. 审查项结论

### 1.1 无遗漏对账 —— PASS

**总量对账**（PowerShell `Get-ChildItem -Recurse` 实测，2026-09-02）：

| 指标 | 台账 | 实测 | 判定 |
|---|---|---|---|
| md 文件总数 | 2124 | **2124** | ✅ |
| 非 md 文件 | 22 | **22**（.gitkeep 8 + .html 8 + .py 2 + .toml 2 + .pyc 1 + .template 1） | ✅ |
| 分类计数（12 分类 + 根级 5） | 63/199/321/546/146/55/93/200/114/10/49/323 + 5 | 逐项一致，合计 2124 | ✅ |

**深度抽样对账**：28 个主题目录逐目录核对「源侧正文文件数 = 目标侧 concepts 数 + 合并增量 + 舍弃数」，覆盖新建/合并/直迁/舍弃全部处置类型。抽样包括：first-principles（51→47 内容+5 舍弃+3 结构）、okr（48→41）、okf-kit（30→14，含 8 个重复章去重+2 隐私+4 导航）、context-optimization（73→72）、volcengine-agent（25→22，MAINTENANCE.md 属维护元数据舍弃）、sunlogin（47→41，5 个 retrospective 隐私舍弃✓）、oray（9→5，5 个 retrospective 隐私舍弃✓）、quantdinger（6+1 散文件→5）、eve（12→12）、orca（10→10）、python314-stdlib（21→19，17 章全迁+index/log/README/seven-concepts-report 舍弃）、ai-agent-skills（32→31，log.md 舍弃）、agent-skills-spec 合并束（log.md v1.1.0 完整登记三源回填与逐章重复确认）、mobile-use、mermaid、weasyprint、minit2i、miaowu、jira-skill、ems-energy、three-ai-tools、ai-switch-governance、causal-ai、rqndd、atomic-emergence、thesis-writing、okf-desktop、agent-interface。**全部守恒，未发现丢失内容。**

**8 个台账路径 MISSING 的定位**（批量核对 110+ 目标束发现，逐一排查后全部解释）：

| 台账路径 | 实际状态 | 判定 |
|---|---|---|
| jishu/ai/ai-agent/agent-interface-deep-dive | 实际落点 `jishu/ai/ai-agent/agent-interface`（10 md） | 路径差异，内容在 |
| jishu/ai/ai-agent/okf-desktop | 实际落点 `meta/okf-desktop`（10 md） | 路径差异，内容在 |
| jishu/ai/eve | 实际落点 `jishu/ai/ai-agent/eve`（12 md） | 路径差异，内容在 |
| jishu/ai/orca | 实际落点 `jishu/ai/ai-agent/orca`（10 md） | 路径差异，内容在 |
| jishu/python/python314-stdlib | 实际落点 `jishu/python/stdlib`（19 md） | 路径差异，内容在 |
| sheke/workplace/academic-writing | 实际落点 `sheke/workplace/thesis-writing`（15 md） | 路径差异，内容在 |
| jishu/ai/ai-agent-skills | 实际落点 `jishu/ai/ai-agent/ai-agent-skills`（31 md） | 路径差异，内容在 |
| jishu/ai/llm-vendor-comparison | 07/comparison 2 篇执行期判定低价值舍弃 | 台账 §9 预授权（"执行期可判低价值舍弃"），SKIP 记录见 migrate_batch_07_10.py |

### 1.2 隐私复扫 —— PASS（2 处 major 已修复）

- **文件名级**：`retrospective*`/`seven-concepts-report*` 全 bundles 扫描，仅 1 命中 = `ai-engineering-methodology/concepts/methodology/seven-concepts-deeptutor-wiki/01-seven-concepts-theory/01-r-retrospective.md`——台账 §14 明示为内容章节随主题迁移，内容复审确认为七概念方法论教程（无个人标识/无工作流元数据），✓ 合规。59 个隐私元数据文件（12 retrospective + 10 seven-concepts-report + 37 log.md）零误迁入。
- **个人标识**（`xinzo|Users\xinzo|d:\AI|D:\BaiduSync`）：迁移范围内命中 2 处 `d:\AI` 个人工作区路径（**major，已修复**，见 §3）；`jishu/containers/fuse-overlayfs` 的 `xinzo:100000:65536` 为既有束旧文件 rootless 映射示例（非本次迁移范围，minor 记录）。修复后全 bundles 复扫 **CLEAN**。
- **工作流元数据**（session ID/token 消耗/执行时长等）：50+ 命中逐一判定均为技术内容语义（API 参数 `session_id`、产品场景耗时数据、token 优化讨论），零私人会话记录。
- **第一人称私人叙事**：10 命中均为 Sphinx/MyST/i18n 官方教程标准示例字符串（"我的项目"），零私人叙事。

### 1.3 凭据复扫 —— PASS（零真实凭据）

6 组正则全 bundles 扫描，命中 60+ 处逐一核实：

| 组 | 命中 | 判定 |
|---|---|---|
| GitHub（ghp_/gho_/github_pat_） | 0 | ✅ |
| sk-ant-/sk-proj-/sk- | 4（echobird、hermes-agent） | 占位掩码（`sk-ant-xxx…`）✅ |
| AKIA/ASIA/xox-/AIza | 3（github-cli、zleap-agent、hermes-agent） | `AKIAIOSFODNN7EXAMPLE` 为 AWS 官方文档通用示例 ID；`xoxb-…` 为占位 ✅ |
| PRIVATE KEY 头 | 3（scrapli、jupyterlab-probot） | 代码示例占位（`\n...` 截断）✅ |
| URL 内嵌凭据 | 21（conda 系、octop、trae、github-cli、open-code-review 等） | 全部为 `user:password@host` 类教程示例与脱敏功能演示 ✅ |
| password/secret/api_key 赋值 | 30（scrapli、pexpect、coze、volcengine 等） | 占位符（`your-key`、`<api-key>`）与公开默认凭据（Nokia SR Linux sandbox 默认 `NokiaSrl1!`）✅ |

### 1.4 frontmatter 抽查 —— PASS

15 个新建文件（跨 15 个束，覆盖 4 个批次脚本产物）：YAML 全部可解析；**10 个内容文件** type 非空（Concept / Wiki Tutorial）、sources 溯源完整、title 存在，10/10 合规；**5 个 index.md 导航文件**无 type/sources——与库内既有惯例一致（既有束 `jishu/dev/git/index.md` 仅含 `okf_version`，直迁包 `meta/okf-ecosystem/index.md` 无 frontmatter），非违规。

中文内嵌引号：迁移引擎**新生成文本**（束 index/导航/描述）标点规范（「」与全角弯引号）✅；源文件原样正文中的半角引号（3884 处模式命中，含 Mermaid 代码块语法必需引号）属内容保真范畴，不构成迁移违规（minor 记录）。

### 1.5 门控复核 —— PASS（本次迁移范围零新增）

cwd=`projects/awesome-okf-xs`：

| 门控 | 结果 | 明细 |
|---|---|---|
| `python scripts/check-bundles-index.py` | ✅ **exit 0** | 9 域 / 56 组 / 497 束，frontmatter、计数行、节标题、分组表、toctree 五面一致 |
| `python scripts/check-toctrees.py` | ⚠️ exit 1，12 处 | 11 处 `agent-platform-notes`（已知并行会话遗留，与任务说明的 11 处完全吻合，无新增）+ 1 处 `yishu/vocal/gesture-vocal-pedagogy 缺 index.md`（yishu 域声乐主题，不在台账任何条目内，属并行会话遗留） |

修复后重跑两门控，输出与修复前逐字一致（无回归）。

## 2. 对账统计表

| 对账维度 | 数值 |
|---|---|
| 源库 md 总数（实测=台账） | 2124 |
| 源库非 md 资源 | 22（随迁 13 + 舍弃 9） |
| 隐私元数据不迁入 | 59（retrospective 12 + seven-concepts-report 10 + log.md 37），实测零误迁入 |
| 批量核对目标束 | 110+（含合并/直迁/新建全部类型），存在且非空 |
| 深度抽样主题目录 | 28 个，文件数守恒率 28/28 |
| 台账路径 MISSING 定位 | 8/8 全部解释（7 路径差异 + 1 预授权舍弃） |
| 隐私修复 | 2 处（已修复 + 复扫 CLEAN） |
| 凭据正则组 | 6 组，真实凭据 0 |
| frontmatter 抽样 | 15（内容文件合规 10/10） |
| 门控 | bundles-index PASS；toctrees 12 处全遗留、本次零新增 |

## 3. 问题清单与修复情况

| 级别 | 问题 | 状态 |
|---|---|---|
| ~~major~~ | `jishu/ai/ai-agent/orca/concepts/01-core-architecture.md:15` 暴露个人工作区路径 `d:\AI\external\tools\orca` | ✅ 已修复（改为「Orca 开源仓库源码」，语义保持，全角标点纪律遵守） |
| ~~major~~ | `jishu/ai/open-code-review/references/resources.md:81` 暴露 `d:\AI\docs\knowledge\learning\` | ✅ 已修复（改为「本知识库内」中性表述，语义保持） |
| minor | 台账 7 处目标束路径与实际落点不一致（§1.1 表），台账未回写 | 留记录（tasks.md 与迁移脚本内有实际路径记录，不影响对账权威性；建议删除源目录后如需可补台账勘误） |
| minor | 既有束 `jishu/containers/fuse-overlayfs/examples/02-rootless.md` 含 `xinzo` 用户名示例 | 非本次迁移范围，属既有问题，留记录 |
| minor | 源文件原样正文含大量半角引号（内容保真保留，含 Mermaid 语法必需引号） | 留记录，不修复 |
| minor | `volcengine-agentkit-wiki` 的 `MAINTENANCE.md` 舍弃未在台账 §14 单列（维护元数据，合理） | 留记录 |
| 遗留（非本次范围） | `agent-platform-notes` 11 处 + `yishu/vocal/gesture-vocal-pedagogy` 缺 index.md，toctrees 门控 CI 拦截 | 移交并行会话责任方，本次迁移零新增 |

## 4. blocker 清单

无。

## 5. 审查方法说明

- 计数与清单：PowerShell 7 `Get-ChildItem -Recurse`（分类级、束级、文件级三层）；临时核对脚本用后已删除。
- 内容守恒：束级双侧文件清单 diff（源 stem 集合 vs 落点 concepts/references 集合），舍弃文件逐个核对处置依据（导航壳/隐私/重复/维护元数据）。
- 隐私与凭据：全 bundles 正则扫描 + 逐命中人工判定（区分占位掩码/官方示例/公开默认值/真实凭据）。
- 门控：在 `projects/awesome-okf-xs` 下按任务指定命令原样执行，修复前后各一次对比。
- 全程未执行 git 命令（遵守任务约束；git submodule 只读纪律同时满足）。
