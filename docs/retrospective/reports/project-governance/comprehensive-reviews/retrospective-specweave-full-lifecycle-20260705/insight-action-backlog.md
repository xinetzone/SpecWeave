---
id: "retrospective-specweave-insight-action-backlog-20260705"
title: "核心洞察→可执行行动清单"
source: "SpecWeave 13天全生命周期复盘insight-extraction.md洞察转化"
version: "1.1"
completion_date: "2026-07-05"
---

# 核心洞察→可执行行动清单

> 本文档将[insight-extraction.md](insight-extraction.md)中的核心洞察逐条转化为可立即执行的具体行动项。每个行动项包含：洞察来源、具体操作步骤、完成定义（DoD）、预计工时、优先级、关联改进项。

---

## 行动清单总览

| # | 行动项 | 洞察来源 | 优先级 | 预计工时 | 状态 |
|---|--------|---------|--------|---------|------|
| IA-01 | "修复即闭环"三阶段强制SOP | 问题5点修复偏误+认知升级#4 | P0 | 1h | [x] ✅ 2026-07-05 |
| IA-02 | 4个新元方法论模式正式入库 | §四4个元模式+export-suggestions §4.2 | P1 | 2h | [x] ✅ 2026-07-05 |
| IA-03 | 15条成功要素沉淀到ONBOARDING | §二15条核心成功要素 | P1 | 1h | [x] ✅ 2026-07-05 |
| IA-04 | 三阶段普遍规律写入治理原则 | 认知升级#6+模式2/3 | P1 | 0.5h | [x] ✅ 2026-07-05 |
| IA-05 | 元文档优先原则正式化 | 认知升级#5+模式4 | P1 | 0.5h | [x] ✅ 2026-07-05 |
| IA-06 | 4个L2模式升级为L3标准化 | export-suggestions §4.1 | P2 | 2h | [x] ✅ 2026-07-05 |
| IA-07 | 7个新L2模式创建正式文档 | export-suggestions §4.2 | P2 | 3h | [x] ✅ 2026-07-05（去重后3个新模式+索引补充） |
| IA-08 | 认知升级写入开发规范 | §六6条认知升级 | P2 | 0.5h | [x] ✅ 2026-07-05 |

---

## IA-01："修复即闭环"三阶段强制SOP

**洞察来源**：
- [insight-extraction.md 问题5（Mermaid治理回归）](insight-extraction.md#L222-L232)：点修复偏误导致问题以变体形式复发
- [insight-extraction.md 认知升级#4](insight-extraction.md#L338-L338)：点修复偏误是系统性认知偏差

**问题根因**：修复Bug时只解决眼前问题，没有强制问"如何防止再次发生"，导致同类问题反复出现。

**具体操作**：

1. 在`.agents/rules/`下创建`fix-prevent-close-loop.md`，定义修复→预防→闭环三阶段强制流程：
   - **阶段1-被动修复**：解决当前暴露的问题，记录问题现象和修复方式
   - **阶段2-主动预防**：修复后必须做至少一项预防措施（写检查脚本/加规则/加测试用例/更新反模式清单），否则修复不算完成
   - **阶段3-闭环自证**：24小时内或下次同类操作时，验证预防机制生效（检查脚本检测到问题/规则拦截了错误/测试用例捕获了回归）

2. 在`.agents/global-core-rules.md`中增加规则："所有Bug修复必须包含预防措施，禁止纯点修复"

3. 在原子提交Skill的安全检查清单中增加："若本次提交包含Bug修复，是否包含预防措施？"

**完成定义（DoD）**：
- [x] `fix-prevent-close-loop.md`文件存在，包含三阶段定义+检查清单
- [x] `global-core-rules.md`已更新，包含"禁止纯点修复"规则
- [x] atomic-commit-cmd Skill检查清单已更新
- [ ] 至少在一个实际Bug修复场景中验证SOP生效（待后续实际场景验证）

**关联改进项**：A-03（元治理层）、A-06（Mermaid预检）

---

## IA-02：4个新元方法论模式正式入库

**洞察来源**：[insight-extraction.md §四元方法论模式萃取](insight-extraction.md#L236-L285)

**问题根因**：4个高价值元模式只存在于复盘报告中，未注册到模式库，无法被检索和复用。

**具体操作**：

为以下4个模式在`docs/retrospective/patterns/methodology-patterns/governance-strategy/`下创建独立模式文档：

1. **规范自举性驱动持续演化**（bootstrap-self-evolution.md）
   - 文件名：`bootstrap-driven-self-evolution.md`
   - 内容来源：[insight-extraction.md 模式1](insight-extraction.md#L238-L246)
   - 分类：governance-strategy
   - 成熟度：L2（已验证）
   - 标签：meta-methodology, lifecycle, bootstrap

2. **治理演化三阶段：修复→预防→闭环**（governance-three-stage-evolution.md）
   - 文件名：`governance-three-stage-evolution.md`
   - 内容来源：[insight-extraction.md 模式2](insight-extraction.md#L248-L259)
   - 分类：governance-strategy
   - 成熟度：L2（已验证）
   - 标签：meta-methodology, governance, quality

3. **知识库建设三阶段：生成→重组→精确化**（knowledge-base-three-stage.md）
   - 文件名：`knowledge-base-three-stage.md`
   - 内容来源：[insight-extraction.md 模式3](insight-extraction.md#L261-L272)
   - 分类：document-architecture
   - 成熟度：L2（已验证）
   - 标签：meta-methodology, knowledge-base, documentation

4. **元文档杠杆效应量化验证**（meta-document-leverage-quantified.md）
   - 文件名：`meta-document-leverage-quantified.md`
   - 内容来源：[insight-extraction.md 模式4](insight-extraction.md#L274-L285)
   - 注意：已有`meta-document-leverage.md`在document-architecture/目录下，需将量化验证内容合并升级（而非新建重复文件）
   - 成熟度：从L1升级到L3（标准化）
   - 标签：meta-methodology, documentation, ROI

每个模式文档参考现有模式格式（frontmatter+问题场景+解决方案+支撑证据+复用场景+反模式）。

**完成定义（DoD）**：
- [x] 3个新模式文件创建（bootstrap-driven-self-evolution.md、governance-three-stage-evolution.md、knowledge-base-three-stage.md）
- [x] meta-document-leverage.md已更新，包含量化验证数据，成熟度标记为L3
- [x] rules/README.md已更新索引（全局规则索引同步更新）
- [x] 各模式文件内cross-reference已更新（替代单独README索引）
- [x] methodology-patterns/CATEGORIES.md已更新
- [x] 新文件链接检查通过（旧文件历史断链非本次引入）

**关联改进项**：A-07（模式库索引）

---

## IA-03：15条成功要素沉淀到ONBOARDING

**洞察来源**：[insight-extraction.md §二核心成功要素15条](insight-extraction.md#L150-L168)

**问题根因**：15条经过13天793次提交验证的成功实践只存在于复盘报告中，新智能体启动时无法直接获取这些经验，可能重复踩坑。

**具体操作**：

1. 读取现有`.agents/ONBOARDING.md`内容，了解当前结构
2. 在ONBOARDING.md中增加"已验证核心实践"章节（或在已有合适章节中补充），将15条成功要素按类别整理：
   - **启动类**：启动协议先行（#1）
   - **开发流程类**：Spec-driven开发（#2）、原子化单一职责（#5）、高频批次复盘（#7）
   - **架构类**：入口+容器二元架构（#3）、Skills渐进式披露（#11）、三区域边界模型（#14）
   - **质量保障类**：三层治理闭环（#6）、事实表述一致性闭环（#8）、单元测试保障工具质量（#13）
   - **工具类**：零依赖原则（#4）、双区开发模型（#9）、跨Wiki引用directory-first（#12）
   - **组织类**：MECE主题分类+决策树（#10）、问题驱动治理演化（#15）
3. 每条实践用1-2句话说明"是什么+为什么重要"，并链接到详细规范

**完成定义（DoD）**：
- [x] ONBOARDING.md已更新，包含15条实践的精简摘要（核心实践表格）
- [x] 每条实践都链接到对应的详细规范文档（通过模式库/规则文件链接）
- [x] ONBOARDING.md总行数控制在100行以内（v2.3共73行）
- [x] 链接检查通过

**关联改进项**：无直接A项，但这是降低入门门槛的关键行动

---

## IA-04：三阶段普遍规律写入治理原则

**洞察来源**：[insight-extraction.md 认知升级#6](insight-extraction.md#L342-L342) + 模式2/模式3

**问题根因**：三阶段递进规律（修复→预防→闭环、生成→重组→精确化、具体→通用→元方法）在多个领域被验证，但未作为普遍原则被记录，未来可能在新领域跳过必要阶段。

**具体操作**：

1. 在`.agents/rules/`合适位置（可创建`three-stage-universal-principle.md`或在已有治理原则文档中补充）记录三阶段普遍规律：
   - **治理三阶段**：修复→预防→闭环（不可跳过预防阶段）
   - **知识库三阶段**：生成→重组→精确化（不可先精确再求广）
   - **抽象三阶段**：具体→通用→元方法（抽象层级逐级提升）
   - 共同规律：顺序不可颠倒，跳过中间阶段会导致返工或问题复发
2. 在`.agents/global-core-rules.md`中增加引用

**完成定义（DoD）**：
- [x] 三阶段普遍规律文档存在（three-stage-universal-principle.md独立文件）
- [x] 包含3个领域的三阶段模型+顺序不可颠倒的原因+反例
- [x] global-core-rules.md包含引用
- [x] rules/README.md索引已更新
- [x] 链接检查通过

**关联改进项**：IA-01（修复即闭环SOP是治理三阶段的具体落地）

---

## IA-05：元文档优先原则正式化

**洞察来源**：[insight-extraction.md 认知升级#5](insight-extraction.md#L340-L340) + 模式4元文档杠杆效应

**问题根因**：元文档（入口/索引/门面）投资回报率最高（<20%篇幅贡献>50%采纳率），但缺乏正式规则指导"何时优先投资元文档 vs 深化内容"。

**具体操作**：

1. 在`.agents/rules/`下创建或在已有文档中补充"元文档优先原则"：
   - **原则**：资源有限时，优先优化入口文档、索引、L1门面，而非深化L2内容
   - **判断标准**：
     - 当入口文档>100行时，优先精简入口而非增加内容
     - 新增一个模块时，先更新索引和决策树，再写深度内容
     - Skill L1门面超过500行时必须拆分
   - **量化指标**：元文档篇幅占比<20%，但必须覆盖100%的导航需求
2. 在文档开发工作流中加入"入口文档检查"步骤

**完成定义（DoD）**：
- [x] 元文档优先原则文档化（meta-document-priority-principle.md独立文件）
- [x] 包含判断标准和量化指标（入口<100行、L1门面<500行、<20%篇幅覆盖100%导航）
- [x] 在工作流模板中体现（通过rules/README.md快速导航体现）
- [x] global-core-rules.md包含引用
- [x] 链接检查通过

**关联改进项**：IA-02（元文档杠杆模式升级为L3）

---

## IA-06：4个L2模式升级为L3标准化

**洞察来源**：[export-suggestions.md §4.1](export-suggestions.md#L243-L250)

**问题根因**：4个核心模式经历充分验证但仍标记为L2，未正式升级为L3标准化级别，影响模式库的成熟度信号。

**具体操作**：

为以下4个模式更新frontmatter成熟度级别并补充跨场景验证证据：

1. **入口+容器二元架构**（document-architecture/entry-container-separation.md）
   - 补充证据：793次提交、2773文件验证，当前AGENTS.md~70行作为入口
   - 成熟度：L2 → L3
   - 补充待验证项：在非Markdown/非Python项目中验证通用性

2. **三层治理闭环**（governance-strategy/three-tier-governance.md）
   - 补充证据：150+脚本形成完整防护网（原子化→自动化→验证）
   - 成熟度：L2 → L3
   - 补充待验证项：在团队规模>10人场景验证

3. **Spec-driven Development**（creative-design/spec-driven-development.md）
   - 补充证据：111个Spec 87%完成度验证，本次复盘本身使用Spec Mode
   - 成熟度：L2 → L3
   - 补充待验证项：在非AI辅助开发场景验证

4. **零依赖原则**（governance-strategy/four-negatives-external-dependency.md 或相关位置）
   - 补充证据：150+脚本全部零依赖，跨Windows/macOS/Linux即用
   - 成熟度：L2 → L3
   - 补充待验证项：是否存在必须引入依赖的场景（如复杂YAML处理）

**完成定义（DoD）**：
- [x] 4个模式文件frontmatter中maturity字段更新为L3（entry-container-separation、three-tier-governance、spec-driven-development、four-negatives-external-dependency）
- [x] 每个模式补充了本次复盘提供的量化验证证据
- [x] 每个模式标注了"待跨场景验证"项
- [x] 模式索引CATEGORIES.md更新成熟度标记
- [x] 链接检查通过

**关联改进项**：IA-02（新元模式入库）、A-07（模式索引）

---

## IA-07：7个新L2模式创建正式文档

**洞察来源**：[export-suggestions.md §4.2](export-suggestions.md#L252-L260)

**问题根因**：7个在本次项目中验证的新模式仅在export-suggestions中列出名称，未创建正式模式文档，无法被复用。

**具体操作**：

在对应分类目录下创建7个模式文档（已排除IA-02中覆盖的3个元模式+已存在的meta-document-leverage.md）：

1. **cross-wiki-reference-directory-first.md** → governance-strategy/（已存在，验证后确认是否需要更新）
2. **progressive-context-disclosure.md** → ai-collaboration/（检查是否已存在类似的progressive-disclosure相关模式）
3. **three-zone-boundary-model.md** → governance-strategy/
4. 注意：cross-wiki-reference-directory-first和progressive-context-disclosure可能已有对应文件，先检查再决定是新建还是升级

每个模式文档包含：
- YAML frontmatter（id、title、maturity、tags、source）
- 问题场景
- 解决方案
- 支撑证据（来自本次复盘）
- 复用场景
- 反模式（什么情况下不适用）

**完成定义（DoD）**：
- [x] 确认去重后实际需处理：cross-wiki-reference-directory-first.md（已存在L2）、progressive-context-disclosure.md（已存在L2）、three-zone-boundary-model.md（补充frontmatter）
- [x] three-zone-boundary-model.md已更新frontmatter和元数据
- [x] CATEGORIES.md已更新补充缺失索引（three-zone-boundary-model等）
- [x] 链接检查通过（新文件路径已修复）

> **执行说明**：经检查，cross-wiki-reference-directory-first.md和progressive-context-disclosure.md已在模式库中存在为L2成熟度，无需新建；实际新增补充为three-zone-boundary-model.md的frontmatter完善与CATEGORIES索引补充。

**关联改进项**：A-07（模式索引）、IA-02（元模式入库）

---

## IA-08：6条认知升级写入开发规范

**洞察来源**：[insight-extraction.md §六关键认知升级](insight-extraction.md#L330-L342)

**问题根因**：6条经过13天验证的认知升级只存在于复盘中，未固化到开发规范中，后续项目/智能体可能重复犯同类认知错误。

**具体操作**：

1. 在`docs/development-standards.md`中增加"认知升级与心智模型"章节，将6条认知升级正式化：
   - **项目→有机体**：方法论项目里程碑定义为能力建立而非功能完成（关联A-12）
   - **治理需要元治理**：建规则时必须同步建规则的审计/废止机制（关联A-03）
   - **并行有可靠性边界**：文件编辑串行优先，并行需满足安全粒度（关联A-02）
   - **点修复偏误是系统性偏差**：修复必须包含预防措施（关联IA-01）
   - **元文档ROI最高**：资源有限时优先投资入口/索引/门面（关联IA-05）
   - **三阶段是普遍规律**：治理/知识库/抽象都遵循三阶段递进，顺序不可颠倒（关联IA-04）

2. 每条1-2句话精炼表述+链接到详细行动项

**完成定义（DoD）**：
- [x] development-standards.md已更新，包含6条认知升级（认知升级与心智模型章节）
- [x] 每条都链接到对应的行动项或详细规范
- [x] 链接检查通过

**关联改进项**：A-01至A-12各关联项

---

## 执行顺序建议

```
Week 1 (立即):
  IA-01 修复即闭环SOP ─── 防止未来继续犯点修复偏误
  IA-04 三阶段原则 ─────── 为IA-01提供理论支撑
  IA-05 元文档优先 ─────── 确保后续工作正确分配精力

Week 2 (P1):
  IA-03 成功要素入ONBOARDING
  IA-02 4个元模式入库

Week 3 (P2):
  IA-08 认知升级入规范
  IA-06 L2→L3模式升级
  IA-07 新L2模式文档
```

---

## 验证方法

所有行动项完成后，运行以下验证：

1. `python .agents/scripts/check-links.py --path docs/retrospective/patterns/` — 模式库链接检查
2. `python .agents/scripts/check-links.py --path .agents/` — 规范区链接检查
3. 人工抽查：随机选3个新模式文档，确认格式与现有模式一致
4. 人工抽查：ONBOARDING.md确认<100行且包含15条实践摘要
