---
id: "milestone-doc-governance-program-retrospective-20260831"
title: "近期文档治理工作项目级复盘报告（2026-07~08）"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/concepts/milestone/doc-governance-program-retrospective-20260831.toml"
date: "2026-08-31"
completion_date: "2026-08-31"
type: "Report"
description: "对 2026 年 7-8 月 SpecWeave 文档治理工作的项目级复盘：覆盖知识库迁移、双文档体系边界确立、质量门禁建设与消费、信源路径稳定性（GATE-SPS）、文档生成与模式沉淀五条主线；2691 提交/395 治理类提交/22 份里程碑报告的事实基底；4 条项目级洞察（连接元数据债务本质/迁移引用收敛成本/门禁四段闭环/台账驱动范式演进）；6 项行动项（ACT-G1~G6）"
status: "stable"
source: "retrospective-cmd session retr-20260831-doc-governance（复盘对象：2026-07~08 近期文档治理工作，project 级）"
milestone-name: "近期文档治理工作项目级复盘"
time-range: "2026-07-01..2026-08-31"
methodology: "复盘四步法（收集事实→分析过程→提炼洞察→生成报告），项目级（project scope）"
quality-gates:
  G1: "事实可命令复现 ✅（关键数字均附采集命令，经 Bash 实测）"
  G2: "洞察四元组完整 ✅（4 条洞察，均引用事实主线/编号）"
  G3: "行动项含验收标准 ✅（ACT-G1~G6 均含优先级与验收口径）"
  data_verification: "数据验证三查法 ✅（一查关键数据 Bash 实测、二查无 file:/// 绝对路径、三查章节完整性）"
tags: ["项目级复盘", "文档治理", "双文档体系", "质量门禁", "信源路径稳定性", "GATE-SPS", "知识库迁移", "台账驱动", "连接元数据债务"]
generated: { by: "process:retrospective-cmd", at: "2026-08-31T00:00:00Z" }
stale_after: "2027-08-31"
---

<!-- meta_type: retrospective -->

# 近期文档治理工作项目级复盘报告

> **复盘方法**：复盘四步法（事实→分析→洞察→报告），项目级（project scope）
> **复盘对象**：2026-07~08 近期文档治理工作（SpecWeave 文档中心 + 智能体规范容器双体系）
> **复盘日期**：2026-08-31
> **session**：retr-20260831-doc-governance
> **关联报告**：[docs-full-retrospective-20260831.md](docs-full-retrospective-20260831.md)（docs/ 全量审计单日复盘，本报告案例谱系前例与输入）、[source-path-debt-triage-audit-20260829.md](source-path-debt-triage-audit-20260829.md)（全仓信源路径分诊）、[veadk-a3-a6-closure-retrospective-20260829.md](veadk-a3-a6-closure-retrospective-20260829.md)（GATE-SPS 假阳性修复）

> **审批说明（RACI）**：项目级（project）复盘属重大复盘，按 [复盘指令集 RACI](../../../../../.agents/commands/retrospective.md) 第 42 行，最终审批权归 **co-founder**。本报告生成后待 co-founder 审批方为闭环。

---

## 一、执行摘要

2026 年 7-8 月，SpecWeave 文档治理经历了从"单点行动项"到"台账驱动批量治理"的范式演进。两个月内完成 **2691 次提交**（其中 `docs(retrospective)`/`docs(governance)` 类型 **395 次**），产出 **22 份里程碑复盘报告**，沿五条主线推进：

1. **知识库迁移**（8-29~8-31）：`.agents/docs/knowledge` 与 bundles 集合迁入根 `docs/knowledge`，迁移后跟随独立断链修复提交。
2. **双文档体系边界确立**（8-31）：确立 `docs/`（OKF v0.2 文档中心）与 `.agents/docs/`（智能体配套）边界，建立 R1-R6 规则与跨区引用收敛台账（基线 675/164 处），冻结新增。
3. **质量门禁建设与消费**（贯穿，8-31 闭环）：三门禁（utf8/toctrees/frontmatter）检出 3849 处原始问题，经 ACT-1~6 批量消费，门禁全部归零（2696 文件合规）。
4. **信源路径稳定性 GATE-SPS**（8-29 集中爆发）：新建信源路径扫描工具，修复 568 个假阳性，全仓分诊 13583 文件/7002 引用，信源稳定性门模式 L1→L2→第 3 次验证。
5. **文档生成与模式沉淀**（贯穿）：新增 docx-template-report 等 5+ 技能，沉淀生成-登记同步法（L1.5）、信源稳定性门（L2）等十余个可复用模式。

**核心结论**：文档治理的债务本质是**连接元数据债务**（toctree/索引/路径引用/frontmatter 登记），而非内容债务——内容层质量已达标（UTF-8 100%、Sphinx 警告清零、OKF 包 frontmatter 完整）。治理的瓶颈在于"生成-消费断裂"与"门禁报警-灭火断层"，8-31 已打通消费管道；但跨区引用收敛（B1-B5 批次，675 处）仍是未启动的长尾。

---

## 二、复盘范围与方法

本次复盘为 **project 级**，时间跨度 2026-07-01 至 2026-08-31，覆盖 SpecWeave 文档治理全貌。区别于单日的 [docs-full-retrospective-20260831](docs-full-retrospective-20260831.md)（聚焦 `docs/` 全量审计），本报告从更高维度梳理两个月治理工作的脉络、范式演进与系统性问题。

事实来源：git 提交历史（`git log --since=2026-07-01`）、里程碑索引（[milestone/index.md](index.md)）、[cross-reference-ledger.md](../../../cross-reference-ledger.md)、[docs/log.md](../../../../log.md)、[docs-full-retrospective-20260831.md](docs-full-retrospective-20260831.md)。所有关键数字均经 Bash 实测，可复现。

---

## 三、S1 事实清单

> G1 质量门：✅ 通过（事实均为可验证客观陈述，无因果推断词；关键数字附采集命令）

### 3.1 规模与节奏

| 编号 | 事实 |
|------|------|
| F-001 | 2026-07-01 至 2026-08-31 共 2691 次提交（`git log --since=2026-07-01 --oneline \| wc -l` 实测） |
| F-002 | 其中 `docs(retrospective)`/`docs(governance)` 类型提交 395 次（`git log ... \| grep -cE "^docs\(retrospective\)\|^docs\(governance\)"`） |
| F-003 | ACT 系列行动项提交 16+ 条，横跨 7-8 月，含两套编号体系：7 月 ACT-001~015（单点行动项）、8 月 ACT-1~6（台账驱动批量，docs-full 报告） |
| F-004 | 里程碑索引 [milestone/index.md](index.md) 登记报告 22 行，toctree 收录 27 项，7-8 月新增约 22 份里程碑复盘报告 |

### 3.2 主线一：知识库迁移（8-29 ~ 8-31）

| 编号 | 事实 |
|------|------|
| F-005 | `c8d5b50d`（8-29）bundles 知识包集合迁移至 `docs/knowledge/learning/okf-bundles` |
| F-006 | `5f755cd5`（8-30）`.agents/docs/knowledge` 知识库迁移合并至 `docs/knowledge` |
| F-007 | `c0ab4a56`（8-30）迁移后路径一致性修复，消除迁移引入的断链——**为迁移提交后的独立断链修复提交** |
| F-008 | `945b6218`（8-31）模式比较文档从 `.agents/docs/` 归档树迁移至 `docs/` 复盘体系 |
| F-009 | `dd8f4475`（8-30）补齐 7 个存量模式文档的 V2 强制章节，修复迁移遗留质量债 |

### 3.3 主线二：双文档体系边界确立（8-31）

| 编号 | 事实 |
|------|------|
| F-010 | `5914d4c5`（8-31）确立 `docs/` 与 `.agents/docs/` 双文档体系边界并登记跨区引用收敛台账 |
| F-011 | [cross-reference-ledger.md](../../../cross-reference-ledger.md) 登记基线：`docs/` → `.agents/` 跨区引用 675 处/227 文件；`.agents/docs/` → `docs/` 反向引用 164 处/82 文件 |
| F-012 | 跨区引用按目标前缀分布：`.agents/docs/` 404 处（冻结+分批改写）、`.agents/scripts/` 154 处（合法保留）、其余执行层引用约 240 处 |
| F-013 | R1-R6 边界规则落位根 AGENTS.md 文档边界条款 + global-core-rules 路径解析规则；R2 冻结生效，新增跨区引用数=0 |
| F-014 | 台账 B1-B5 批次**全部状态为"未启动"**（[ledger 第三章](../../../cross-reference-ledger.md)） |
| F-015 | 8-31 前根 AGENTS.md 声明"根目录 `docs/` 已废弃为空壳"与 docs/index.md 声明"SpecWeave 官方文档中心"互斥（[docs-full F-024](docs-full-retrospective-20260831.md)），ACT-5 修订对齐 |

### 3.4 主线三：质量门禁建设与消费（贯穿，8-31 闭环）

| 编号 | 事实 |
|------|------|
| F-016 | docs 内置三道质量门：[check-utf8.py](../../../../scripts/check-utf8.py)、[check-toctrees.py](../../../../scripts/check-toctrees.py)、[check-frontmatter.py](../../../../scripts/check-frontmatter.py) + [tasks/gates.py](../../../../tasks/gates.py) invoke 封装 |
| F-017 | 8-31 [docs-full 复盘](docs-full-retrospective-20260831.md) 实测门禁原始检出合计 3849 处：导航 2245（断链 7 + 未收录 2187）+ frontmatter 1604 |
| F-018 | ACT-1：7 处 toctree 断链归零 |
| F-019 | ACT-2：fix-toctrees 四轮收敛（220 个 toctree 新建、343 个更新），未收录数 2187→0 |
| F-020 | ACT-3：frontmatter 批量治理（53 处 YAML 修复 + 21 处剥离 + 98 个补 frontmatter + 1506 个补 type + 1 处手工），违规数 1604→0（2695 文件合规） |
| F-021 | ACT-4：retrospective 索引修复——6 处断链改指 concepts 层级、模式清单表去重补登至 22 行、里程碑报告表补录至 22 行 |
| F-022 | 门禁回归：check-toctrees / check-frontmatter / check-utf8 全部 exit=0（2696 文件） |
| F-023 | Sphinx 警告多次清零：`40ae9840` 30→0、[okf-wiki-conversion](okf-wiki-conversion-milestone-20260828.md) 421→0、awesome-okf-xs 898→0（`12fa1743`） |
| F-024 | [docs/log.md](../../../../log.md) 8-22 至 8-31 间无修复记录，8-31 集中留痕 ACT-1~6 |

### 3.5 主线四：信源路径稳定性 GATE-SPS（8-29 集中爆发）

| 编号 | 事实 |
|------|------|
| F-025 | `42b6c8e6`（8-29）新增 GATE-SPS 信源路径稳定性扫描工具 |
| F-026 | `a2e37b25`（8-29）GATE-SPS 新增行号锚点越界复验（ACT-2） |
| F-027 | `ba8272c6`（8-29）GATE-SPS 归一化时剥离 `file:///` 链接片段锚点 |
| F-028 | [veadk-a3-a6 报告](veadk-a3-a6-closure-retrospective-20260829.md) 修复 GATE-SPS 568 个存量假阳性，测试 30→32 |
| F-029 | [source-path-debt-triage-audit-20260829.md](source-path-debt-triage-audit-20260829.md) 全仓分诊：13583 文件 / 7002 引用双维聚类；A 类历史快照约 2750 条不改写、B 类约 1050 条不改写、C 类工具误报约 200 条登记 backlog、D-1~D-5 活动债务分批修复 |
| F-030 | 信源稳定性门模式成熟度演进：L1→L2（双案例验证）→第 3 次验证回灌（`51c8d823`），validation_count 递增 |
| F-031 | `ef3688e9`（8-29）重定向 722 个断链 x-toml-ref 至双轨镜像正确路径 |

### 3.6 主线五：文档生成与模式沉淀（贯穿）

| 编号 | 事实 |
|------|------|
| F-032 | 新增文档生成/运维技能：docx-template-report、blog-article-to-okf-wiki、source-code-to-okf-wiki v1.3.0（内置信源稳定性预检）、wsl-ops-cmd、jpman-podman-ops |
| F-033 | 沉淀可复用模式十余个：生成-登记同步法（bp-nav-co-registration, L1.5）、信源稳定性门（L2）、导航收敛修复法（L2）、级联缺陷定位法（L1）、规范→固化→自建→收敛四层生态建设法、标准库系统优化四步法、Sphinx 大文档构建加速（L1）等 |
| F-034 | `4267ca8a`（8-29）新增 docx-template-report 模板驱动报告生成技能；其后多轮脱敏与模板扩展（v1.3.1~v1.3.3） |

---

## 四、S2 过程分析

### 4.1 成功因素

1. **门禁四段闭环已打通**：8-31 闭环证明"感知（脚本）→消费（台账）→修复（批量）→复验（归零）"四段管道完整建立（F-016~F-022）。此前的"报警-灭火断层"在 8-31 被闭合。
2. **模式萃取常态化**：每个治理动作都伴随模式沉淀，validation_count 递增验证（F-030、F-033）。信源稳定性门模式经 3 次验证，生成-登记同步法双案例互证。
3. **工具先行支撑批量治理**：GATE-SPS、fix-toctrees、check-* 系列工具将手工治理转为脚本化批量（F-019、F-025）。
4. **台账驱动显性化隐性债务**：cross-reference-ledger（F-011）与 source-path-debt-triage（F-029）把跨区引用、信源路径等隐性债务显性化、分批化。

### 4.2 失败原因与系统性问题

1. **门禁报警-灭火断层长期存在**：3849 处检出悬置数周，8-31 才批量消费（F-017、F-024）。门禁结果长期未被消费。
2. **迁移是过程不是事件**：两次迁移的文件移动各一次提交完成，但引用修复是独立后续提交（F-007），且迁移前结构仍被索引引用（[docs-full F-018](docs-full-retrospective-20260831.md)）。
3. **双体系声明互斥长期未对齐**：根 AGENTS.md 与 docs/index.md 对"哪个是正式文档中心"的表述矛盾至 8-31 才修订（F-015）。
4. **工具假阳性**：GATE-SPS 568 个假阳性（F-028）、x-toml-ref 722 断链（F-031）——工具检出数 ≠ 实际债务数，需判据验证分流。
5. **生成-消费断裂**：内容批量生产但导航登记手工跟随，2187 处未收录、10 个编号目录整体不可达（[docs-full I-1](docs-full-retrospective-20260831.md)）。

### 4.3 流程瓶颈

1. **导航登记手工化**：未收录 2187 处、编号目录整体不可达，登记速率与生成速率失配。
2. **跨区引用密度高**：675 处跨区引用，B1-B5 批次全未启动（F-014），长尾治理压力集中。
3. **frontmatter 补全手工**：1604 处违规需脚本化批量推断补全。

### 4.4 改进机会

1. 生成-登记同步法落地到生成管线（ACT-G3）。
2. 启动 cross-reference-ledger B1 批次（ACT-G1）。
3. 门禁前移为生成时伴随校验。
4. 工具假阳性治理常态化，检出数与实际债务数对账（ACT-G4）。

---

## 五、S3 核心洞察（4 条）

> G2 质量门：✅ 通过（每条洞察含完整四元组：陈述/证据/反常识/行动；证据均引用 F 编号；四条洞察分别对应债务本质/迁移成本/门禁闭环/范式演进，维度不重叠）

### 洞察 I-1：文档治理的债务本质是"连接元数据"债务，而非"内容"债务

- **陈述**：7-8 月所有重大文档治理动作（迁移断链、导航未收录、frontmatter 缺失、跨区引用、x-toml-ref 断链）都属连接层/元数据层失效；内容层质量已达标。
- **证据**：F-017（3849 处门禁问题均非内容）、F-005~F-009（迁移断链）、F-011（675 跨区引用）、F-031（722 x-toml-ref 断链）、[docs-full F-009](docs-full-retrospective-20260831.md)（UTF-8 100% 通过）、F-023（Sphinx 警告清零）。
- **反常识**：默认假设是"文档治理=写好文档"。实测相反——内容层质量高，失效的是内容间的连接（toctree 收录、索引登记、路径引用、frontmatter 登记）。文件存在但不可达，等价于"不存在"。
- **行动**：治理资源从"内容生产"向"连接登记"倾斜；生成-登记同步法（E-1）落地到生成管线（ACT-G3）。

### 洞察 I-2：迁移的隐性成本是引用收敛而非文件移动，且引用修复与迁移提交解耦导致债务复发

- **陈述**：两次知识库迁移的文件移动各一次提交完成，但引用修复是独立后续提交；迁移前结构仍被索引引用，每次新报告沿用旧路径都使债务复发。
- **证据**：F-006→F-007（`5f755cd5` 迁移 → `c0ab4a56` 独立断链修复）、[docs-full F-018/F-025](docs-full-retrospective-20260831.md)（retrospective/index.md 6 断链指向迁移前结构）、F-021（ACT-4 索引修复）。
- **反常识**：默认假设是"迁移=移动文件，一次提交完成"。实测引用修复工作量与存量引用密度成正比，与文件数不成正比；引用修复不随迁移提交终结。
- **行动**：引用收敛作为迁移的验收条件而非后续优化；迁移提交必须包含引用修复 + 三门禁复验（ACT-G5）。

### 洞察 I-3：质量门禁的完整形态是"感知→消费→修复→复验"四段闭环，缺消费段则门禁退化为背景噪音

- **陈述**：门禁检出能力早已具备，但检出结果长期无修复行动流，直到 8-31 才建立"门禁结果→台账→批量修复→复验归零"闭环。
- **证据**：F-017（3849 处悬置至 8-31）、F-024（log.md 8-22~8-31 无修复记录）、F-022（8-31 门禁归零）、F-028（GATE-SPS 568 假阳性）。
- **反常识**：默认假设是"建立质量门禁=质量有保障"。实测门禁只是感知层；30 条 Sphinx 警告能集中清零（F-023）证明修复能力与意愿都存在，缺的是消费管道。门禁结果若不消费，退化为被忽略的背景噪音。
- **行动**：门禁结果必入台账分批消费；假阳性与真实缺陷同罪，由真实案例校准（ACT-G4）。

### 洞察 I-4：文档治理已从"单点修复"演进到"台账驱动批量治理"范式，但跨区引用收敛仍是未启动的长尾

- **陈述**：7-8 月治理范式从早期 ACT-001~015 单点行动项，演进到 8-31 的台账驱动（cross-reference-ledger B1-B5、source-path-debt D-1~D-5）批量治理；但跨区引用 675 处的 B1-B5 批次全部未启动。
- **证据**：F-003（ACT 两套编号体系：7 月单点 → 8 月台账批量）、F-014（B1-B5 全未启动）、F-029（source-path-debt D-1~D-5 分诊）、F-022（docs/ 内部门禁归零，但跨区引用未动）。
- **反常识**：默认假设是"门禁归零=治理完成"。实测门禁归零只覆盖 `docs/` 内部，跨区引用 675 处长尾未动；台账建立 ≠ 台账消费。
- **行动**：启动 B1 批次（ACT-G1，P1）；建立台账季度复盘机制（ACT-G6），防止台账沦为"登记了但不推进"的僵尸台账。

---

## 六、改进行动项

> G3 质量门：✅ 通过（每项含验收标准、优先级、当前状态）

| 编号 | 行动项 | 验收标准 | 优先级 | 当前状态（2026-08-31） |
|------|--------|---------|--------|----------------------|
| ACT-G1 | 启动 cross-reference-ledger B1 批次：`docs/` → `.agents/docs/retrospective/` 镜像引用（404 处主体）改指 `docs/retrospective/` 新体系 | B1 批次跨区引用数归零；每批在 log.md 留痕；三门禁复验通过 | P1 | 未启动（台账已建，B1-B5 全未启动） |
| ACT-G2 | 生成-登记同步法（bp-nav-co-registration）第 3 个跨项目案例正向验证后升级 L2 | validation_count ≥ 3；新生成文件门禁增量=0 | P2 | 部分完成（L1.5 已入库，待第 3 案例） |
| ACT-G3 | 门禁前移：OKF 包生成 / Wiki 转换 / 报告归档管线内置"导航登记"后置强制步骤 | 新生成文件 toctree 收录率=100%；门禁增量=0 | P1 | 未启动（模式已萃取，未落地到管线） |
| ACT-G4 | 工具假阳性治理常态化：GATE-SPS / check-toctrees 检出数经判据验证后分流，假阳性登记 backlog | 检出数与实际债务数对账记录；假阳性 backlog 维护 | P2 | 部分实践（veadk-a3-a6 已修 568 假阳性，未制度化） |
| ACT-G5 | 迁移验收规则制度化：迁移提交必须包含引用修复 + 三门禁复验，禁止"内容先提交、引用后补" | 后续迁移提交无独立断链修复跟进；规则落位开发规范 | P1 | 待制度化（已有反模式 AP-1，未落规范） |
| ACT-G6 | 台账季度复盘机制：cross-reference-ledger 与 source-path-debt 每季度复盘进度 | 每季度 log.md 留痕；台账状态更新 | P2 | 未启动 |

---

## 七、经验总结

1. **连接元数据是文档治理的真正债务**：内容生产已规模化达标，失效的是内容间的连接层（toctree/索引/路径/frontmatter）。治理资源应向连接登记倾斜（洞察 I-1）。
2. **迁移是过程不是事件**：迁移提交只完成文件移动，引用收敛才是隐性成本，且必须作为迁移验收条件而非后续优化（洞察 I-2）。
3. **门禁价值在消费而非检出**：门禁只是感知层，"感知→消费→修复→复验"四段缺一段则门禁形同虚设（洞察 I-3）。
4. **工具检出数 ≠ 实际债务数**：GATE-SPS 568 假阳性、x-toml-ref 722 断链表明，工具检出须经判据验证分流，假阳性与真实缺陷同罪（F-028、F-031）。
5. **台账驱动优于单点修复**：从 ACT-001~015 单点到 B1-B5 台账批量，是治理范式升级；但台账建立 ≠ 台账消费，需季度复盘防止僵尸台账（洞察 I-4）。
6. **全量审计与局部复盘互补**：此前 20 余份里程碑复盘均以单一对象为主，项目级全量梳理才发现"局部健康、整体负债"的系统性问题。

---

## 附录：采集命令清单（可复现性）

| 数据 | 命令 |
|------|------|
| 7-8 月提交总量 | `git log --since=2026-07-01 --until=2026-09-01 --oneline \| wc -l` → 2691 |
| 治理类提交数 | `git log --since=2026-07-01 --pretty=format:"%s" \| grep -cE "^docs\(retrospective\)\|^docs\(governance\)"` → 395 |
| ACT 系列提交 | `git log --since=2026-07-01 --pretty=format:"%h %ad %s" --date=short \| grep -iE "ACT-[0-9]"` |
| 知识库迁移提交 | `git log ... \| grep -iE "迁移\|migration\|merge.*knowledge\|bundles.*迁移"` |
| GATE-SPS 提交 | `git log ... \| grep -iE "GATE-SPS\|信源.*稳定"` |
| Sphinx/导航/frontmatter 修复提交 | `git log ... \| grep -iE "Sphinx\|toctree\|frontmatter\|导航\|断链"` |
| 跨区引用基线 | 见 [cross-reference-ledger.md 第四章复验方法](../../../cross-reference-ledger.md) |
| 门禁实测 | `python docs/scripts/check-toctrees.py; python docs/scripts/check-frontmatter.py; python docs/scripts/check-utf8.py` |
