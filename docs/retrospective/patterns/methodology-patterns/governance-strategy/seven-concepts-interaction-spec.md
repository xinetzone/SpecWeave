---
id: seven-concepts-interaction-spec
title: 七概念交互机制与接口规范
source: spec.md Task 5 + 前四个产出
x-toml-ref: ../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/seven-concepts-interaction-spec.toml
---

# 七概念交互机制与接口规范

> 概念缩写：R=复盘 | I=洞察 | E=萃取 | C=原子提交 | A=原子化 | F=第一性原理 | V=对抗性审查

## 一、单概念数据契约（7组）

| 概念 | 输入格式（JSON Schema） | 输出格式 |
|------|------------------------|---------|
| **R** | `{events:[{timestamp,actor,action,artifact,verifiable:true}],context:{},no_causal_words:true}` | `{timeline:[],counterfactuals:[{condition:"X",outcome:"Y",confidence:0-1}],causal_links:[]}` |
| **I** | `{source_type:"R|F",facts:[],axioms:[]}` | `{condition:"触发条件C",mechanism:"因果机制M",action:"做A",outcome:"导致B",falsifiable:true,migration_scenarios:[]}` |
| **E** | `{insights:[],level:0}` (0=事件→1=洞察→2=模式→3=原则) | `{level:1-3,abstraction:"通用表述",applicable_scenarios:[],anti_patterns:[]}` |
| **C** | `{changes:[{file,type:feat/fix/docs,scope,single_responsibility:true}],message:{type,scope,subject,body}}` | `{commit_hash,revertible:true,review_jumps:0,related_insights:[]}` |
| **A** | `{target_artifact,cognitive_load:1-10,navigation_cost:1-10,dependencies:[]}` | `{granularity_score:0-100,units:[{path,single_responsibility:true,links_intact:true}],operations:split|merge[]}` |
| **F** | `{problem_statement,assumptions:[{stated,hidden:true}],boundary_conditions:[]}` | `{axioms:[{statement,non_falsifiable:true}],deduction_chain:[],reconstruction:solution}` |
| **V** | `{subject,hypothesis,attack_vectors:["逻辑矛盾","边界反例","隐含假设","数据证伪"]}` | `{passed:boolean,counterexamples:[{scenario,why_it_breaks}],recommendations:[]}` |

**原子化粒度评分简化公式**：`granularity_score = 100 - |cognitive_load - navigation_cost|×10 - max(0,cognitive_load+navigation_cost-10)×5`
- 评分≥70为合格（平衡点附近）
- cognitive_load和navigation_cost均按1-10主观评估（1=极低/10=极高）
- 理想状态：两者均在4-6区间且差值≤2

## 二、接口调用规范（前置/后置/回退）

| 调用路径 | 前置条件（Pre） | 后置验证（Post） | 回退机制 |
|---------|----------------|-----------------|---------|
| R→I | 事实无因果词（禁"因为/所以/导致"），可验证事件≥3（小任务例外：P2/P3Bug修复≥2条） | 洞察四元组完整，可证伪，附≥1迁移场景 | 发现事实混入判断→回退R.S1重采集 |
| I→E | 洞察≥1条（里程碑复盘≥3条），每条四元组完整，V验证通过 | 抽象层级标注正确，配套≥1反模式 | V发现反例击破→回退I修正条件边界 |
| E→知识库 | level≥1，validation_count≥2，maturity≥L1 | frontmatter完整（id/title/source/maturity/tags） | 成熟度不足→标记draft，不入库 |
| A→C | U型曲线评分≥70，链接完整性100%，无断链 | 单文件≤500行，提交可独立revert | 链接断裂→回退A修复链接，不提交 |
| F→I | 公理体系自洽（无矛盾），假设已剥离列出 | 洞察从公理可推导，无跳跃 | V发现公理矛盾→回退F重审公理 |
| V→任意 | 待验证对象完整（洞察/模式/方案） | 验证记录可追溯，反例≥2个 | 验证失败→标记rejected，回退上一步 |
| 任意→C | 所有前置质量门通过 | 提交信息符合Conventional Commits | CI失败→revert到上一提交，修复后重试 |

## 三、四层漏斗数据流转规范

| 层级 | 输出格式标准 | 元数据要求 |
|------|-------------|-----------|
| **L0 事件** | 原始事实记录，时序化，无判断 | `{timestamp, source, verifiable: true}` |
| **L1 洞察** | 三元组「C→M→A→B」 | `{insight_id, source_retro, falsifiable: true, confidence: 0-1}` |
| **L2 模式** | 抽象通用规则，≥2案例支持 | `{pattern_id, source_insights:[≥2], anti_pattern_id, maturity: L1/L2, validation_count}` |
| **L3 原则** | 跨领域公理级表述 | `{principle_id, source_patterns:[≥3], domain: "通用/特定", first_principles_derived: true}` |

**知识资产入库元数据标准**：
```yaml
id: <kebab-case唯一标识>
title: <简明标题>
source: <来源文件/提交/复盘>
maturity: draft/L1/L2/L3
created_at: <ISO日期>
validation_count: <验证次数>
reuse_count: <复用次数>
confidence: <0.3/0.5/0.7/0.9>
tags: [<分类标签>]
related: [<关联资产id>]
```

**confidence四档标定标准**：
| confidence | 含义 | 适用场景 |
|-----------|------|---------|
| **0.9** | 高度可信 | 经过≥3个独立案例验证，核心机制稳定，边界条件明确，无已知反例 |
| **0.7** | 中等可信 | 经过1-2个案例验证，核心逻辑自洽，但可能存在未发现的边界条件 |
| **0.5** | 初步可信 | 逻辑推导成立，有单个案例支持，但尚未经过二次验证（新萃取模式默认值） |
| **0.3** | 推测/待验证 | 仅有理论假设或单个案例的初步观察，需要更多验证，存在较大不确定性 |

**原子提交↔原子化粒度传递契约**：
- A输出单元 → C中一个提交对应一个原子单元，禁止跨单元混提交
- C回滚粒度 = A拆分粒度，保证revert不破坏其他单元
- A的links_intact检查在C前必须100%通过

## 四、冲突解决机制（5条）

| # | 冲突场景 | 仲裁规则 | 处理流程 |
|---|---------|---------|---------|
| CR1 | F推导结果 vs R经验矛盾 | 边界检查优先：F适用于未知领域（无足够案例），R适用于重复场景（≥3次验证） | 1.标注矛盾点→2.检查案例样本量→3.样本<3→用F并补充验证；样本≥3→用R并重新审视F公理边界→4.记录决策理由 |
| CR2 | V审查与F公理冲突 | V优先级更高：公理必须可证伪，V找到反例则公理边界需收缩 | 1.V提交反例→2.F重新审视假设剥离是否彻底→3.收缩公理适用边界→4.重新推导→5.记录反例为公理限定条件 |
| CR3 | A粒度寻优 vs C原子性冲突 | 可回滚性优先：粒度以revert意愿为判断标准 | 1.评估"如果需要回滚，希望回退到哪一步"→2.按回滚点确定提交边界→3.粒度不足则先A再C |
| CR4 | 多个I洞察互相矛盾 | 证伪测试优先：哪个能被反例击破则淘汰 | 1.列出双方洞察→2.V分别构造反例→3.被击破者淘汰→4.都未击破则标注为context-dependent，明确各自适用条件 |
| CR5 | 紧急止血 vs 完整流程冲突 | 恢复优先：先止血后补流程 | 1.第一阶段：仅恢复服务（跳过所有方法论）→2.服务稳定后（MTTR后1小时内）追加R→I→E→C完整闭环→3.记录为何跳过流程 |

## 五、7×7概念交互矩阵

| ↓调用方\目标方→ | R | I | E | C | A | F | V |
|-----------------|---|---|---|---|---|---|---|
| **R** | - | ✅直接调用，Pre:事实完整 | ✅经I间接 | ❌禁止直连 | ❌禁止直连 | ✅触发F分析，Pre:遇未知问题 | ❌禁止直连，经I/E |
| **I** | ❌反向调用 | - | ✅直接调用，Pre:三元组完整 | ❌禁止直连 | ❌禁止直连 | ✅F输入公理推导 | ✅V验证迁移性 |
| **E** | ❌反向调用 | ❌反向调用 | - | ✅入库提交，Pre:成熟度≥L1 | ❌禁止直连 | ❌禁止直连 | ✅V验证模式质量 |
| **C** | ✅事后R效果 | ❌禁止直连 | ❌禁止直连 | - | ❌A在C前 | ❌禁止直连 | ✅提交前V审查 |
| **A** | ✅A后R效果 | ❌禁止直连 | ❌禁止直连 | ✅粒度确定后调用C，Pre:链接完整 | - | ❌禁止直连 | ✅V验证等价性 |
| **F** | ✅F分析后R记录 | ✅F输出公理供I推导 | ✅经I间接 | ❌禁止直连，经I/C | ❌禁止直连 | - | ✅V必须验证公理自洽 |
| **V** | ✅发现问题回退R补事实 | ✅发现问题回退I修正 | ✅发现问题回退E重抽象 | ✅V不通过则C不执行 | ✅等价性不通过回退A | ✅公理矛盾回退F | - |

**交互条件速查**：
- ✅绿格：可直接调用，表中标注前置条件
- ❌红格：禁止直连，需经中间概念路由
- V（对抗性审查）作为横切层，可作用于R/I/E/F/A输出，但从不作为被调用目标（仅其他概念调用V做验证）
- 合法正向调用路径共15条（不含V回退路径），V回退路径共6条（V→R/I/E/C/A/F），总路径21条

---
**接口规范数量**：22个（7单概念契约+7调用规范+4流转规范+4元数据契约<含confidence四档标定>）
**冲突解决机制**：5条
