---
id: "trust-first-metadata"
source: "../../../reports/competitive-analysis/retrospective-knowledge-catalog-wiki-20260815/insights/insight-03-trust-first.md"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
related_patterns:
  - "provenance-driven-trust"
  - "verifiable-knowledge-claim"
  - "credibility-dual-track"
  - "knowledge-as-code-paradigm"
  - "metadata-layering"
tags:
  - metadata-design
  - trust-model
  - ai-native
  - knowledge-representation
  - schema-design
  - provenance
  - lifecycle
  - agent-consumption
---
# 信任优先元数据：AI原生知识体系的字段设计优先级倒置法

## 模式概述

设计面向AI Agent消费的知识/元数据格式时，将**信任（trust）、来源（provenance）、生命周期（lifecycle）字段提升为一等公民**，优先级高于内容表示字段。核心反直觉洞察：AI Agent时代元数据的主要消费者从人变成Agent。人能根据经验判断可信度，Agent不会"判断"只会"使用"——没有内置信任信号的元数据，Agent要么幻觉（盲目信任机器生成内容），要么保守（拒绝使用外部知识）。传统元数据格式（JSON Schema、JSON-LD、dbt schema.yml）把90%精力放在内容表示上，信任字段缺失或边缘化，这是AI原生知识系统的第一大设计错误。

该模式由Google OKF（Open Knowledge Format）v0.2架构演进实践验证。

## 问题现象

传统元数据设计的典型失败模式：

1. **内容优先设计**：schema中90%字段描述内容（名称、类型、描述、属性），信任字段（来源、验证者、过期时间）要么缺失要么放在可选位置
2. **Agent幻觉消费**：LLM自动生成的元数据没有明确标记为"机器生成"，Agent盲目信任导致下游错误
3. **无法判断时效性**：没有过期时间/最后验证时间，Agent可能使用3年前的过时知识做决策
4. **来源黑盒**：不知道一条知识是谁写的、基于什么数据源、被多少人使用过
5. **自证悖论**：Agent生成的内容自己标记为"已验证/可信"，形成信任循环
6. **二值信任**：只有"可信/不可信"二元判断，没有渐进式信任层级，导致要么全信要么全不信
7. **检索排序错位**：检索时优先匹配关键词而非可信度和新鲜度，Agent拿到的最匹配结果可能是最不可信的

根因：默认假设"元数据主要给人看，人能判断可信度"。这个假设在人读时代成立，但Agent作为主要消费者后不再成立。

## 核心设计原则：信任优先级倒置

传统设计 vs 信任优先设计：

```
┌─────────────────────────────────────────────────────────────────────┐
│  传统元数据设计               信任优先元数据设计                      │
├─────────────────────────────────────────────────────────────────────┤
│  内容字段  ████████████ 90%   信任字段  ████████ 40%                  │
│  信任字段  ██ 10%            内容字段  ██████ 35%                    │
│                           生命周期  ████ 25%                         │
│                                                      │
│  核心问题："怎么表示?"       核心问题："敢不敢用?"                    │
│  消费者：人（能判断可信度）   消费者：Agent（需要显式信任信号）        │
└─────────────────────────────────────────────────────────────────────┘
```

### 三类一等公民字段

| 字段类别 | 核心字段 | 作用 | 必填性 |
|---------|---------|------|--------|
| **🔒 信任字段（Trust）** | `sources[]`（来源列表）、`generated_by`（生成者）、`verified_by`（验证者）、`trust_tier`（信任等级） | 回答"能不能信" | **强制必填** |
| **⏰ 生命周期字段（Lifecycle）** | `created_at`、`last_modified`、`last_verified`、`stale_after`（过期时间）、`status`（active/deprecated/archived） | 回答"过不过期" | **强制必填** |
| **📝 内容字段（Content）** | `name`、`type`、`description`、`schema`、`properties`、`body` | 回答"是什么" | 必填但可以渐进补充 |

### Trust Tier 渐进信任模型

不是二元的"信/不信"，而是三级渐进式信任：

```
  unverified          machine-confirmed        human-reviewed
      │                      │                       │
      ▼                      ▼                       ▼
  ┌─────────┐          ┌──────────┐          ┌────────────┐
  │ 来源未知  │  ──→   │ 机器验证过 │  ──→    │ 人工审核过  │
  │ 或LLM生成│          │ (可验证)   │          │ (高置信度)  │
  └─────────┘          └──────────┘          └────────────┘
  Agent使用策略:        Agent使用策略:          Agent使用策略:
  ⚠️ 高度警惕/        ✅ 可用于一般场景     ✅✅ 可用于关键决策
  仅用于探索/          (需通过attester验证)    (仍需attester验证)
  必须人工确认
```

**Trust Tier判定规则**：

| Tier | 判定条件 | Agent使用权限 |
|------|---------|-------------|
| `unverified` | 没有verification记录；或由LLM生成且未经独立验证 | 仅用于探索性分析；关键决策必须人工确认 |
| `machine-confirmed` | 有确定性attester验证通过（见[verifiable-knowledge-claim](verifiable-knowledge-claim.md)）；或来自可信数据源的自动同步 | 可用于一般业务逻辑；高风险决策仍需人工审核 |
| `human-reviewed` | 经过领域专家Sign-off审核；或有≥3次独立成功复用记录 | 可用于关键决策；作为RAG检索优先结果 |

**关键约束**：
- ❌ **禁止Agent自我升级信任等级**：Agent生成的内容必须标记`generated: true`，且**禁止Agent自己标记`trust_tier: human-reviewed`**
- ✅ 信任升级需要独立实体（另一个Agent验证→machine-confirmed；人审核→human-reviewed）
- ⬇️ 信任可以自动降级（超过`stale_after`自动降级为`unverified`）
- ⬆️ 信任升级必须有显式证据（attester结果/审核记录）

## 标准实施步骤

### 步骤1：元数据Schema审查

对现有元数据格式做信任字段审计：
- [ ] 是否有明确的`sources`字段记录来源？
- [ ] 是否区分`generated_by`和`verified_by`（生产者≠验证者）？
- [ ] 是否有`trust_tier`或等效的可信度分级？
- [ ] 是否有`stale_after`过期机制？
- [ ] 是否禁止生产者自证（自己标记自己为已验证）？
- [ ] 检索排序是否考虑信任等级和新鲜度？

如果以上任一项为"否"，就需要按本模式重构。

### 步骤2：定义一等公民信任字段

最小信任字段集（所有知识条目必填）：

```yaml
# 最小信任+生命周期字段（frontmatter）
---
id: "unique-identifier"
type: "concept | metric | rule | fact | attested_computation"
trust_tier: "unverified | machine-confirmed | human-reviewed"
generated_by: "agent:enrichment-v2 | human:zhang.san | sync:bigquery-metadata"
verified_by: null | "human:li.si | attester:metric-validator-v1"
sources:
  - uri: "https://..."
    author: "Google Cloud"
    trust_tier: "human-reviewed"
    last_modified: "2026-01-15"
created_at: "2026-08-15T10:00:00Z"
last_modified: "2026-08-15T10:00:00Z"
last_verified: null
stale_after: "2026-11-15"  # 3个月后过期
status: "active"
---
```

### 步骤3：实现Trust Tier状态机

信任等级不是静态标签，而是有状态转换规则：

```
初始状态（创建时）：
  - LLM/Agent生成 → trust_tier = unverified, generated_by = agent:*
  - 人工创建     → trust_tier = unverified（创建≠审核）, generated_by = human:*
  - 可信数据源同步 → trust_tier = machine-confirmed, generated_by = sync:*

状态升级：
  - attester验证通过 → unverified → machine-confirmed
  - 人工审核Sign-off → machine-confirmed → human-reviewed
  - 人工审核Sign-off → unverified → human-reviewed（跳过机器验证）

状态降级（自动）：
  - 超过stale_after → 自动降级为unverified
  - 上游source被标记为deprecated/incorrect → 自动降级
  - attester重新验证失败 → 降级为unverified
  - 发现反例/冲突证据 → 降级为unverified并标记冲突
```

### 步骤4：Agent消费协议

Agent使用元数据时必须遵循信任感知策略：

1. **检索时**：优先返回`human-reviewed` > `machine-confirmed` > `unverified`；信任等级相同时按`last_modified`/`stale_after`新鲜度排序
2. **使用前**：检查`trust_tier`和`stale_after`；过期的自动降级不使用
3. **生成后**：Agent生成内容必须标记`generated_by: agent:*`和`trust_tier: unverified`，禁止自标记为已验证
4. **验证后**：attester通过后可升级为`machine-confirmed`；人审核后才能升级为`human-reviewed`
5. **冲突时**：同一事实有多个冲突条目时，优先高trust_tier；同tier时优先更新的；无法判定时请求人工或标记不确定性

### 步骤5：生命周期管理

知识不是永恒的，必须管理过期和废弃：
- 每条知识必须设置`stale_after`（建议默认：事实类3-6个月，指标定义6-12个月，架构原则1-2年）
- 临近过期（stale_after前30天）触发复审通知
- 过期后自动从Agent优先检索结果中移除（降级为unverified，仅在显式搜索历史时出现）
- 被验证为错误的知识标记`status: deprecated`并记录替代链接，不是直接删除（保留历史审计轨迹）

## 实战案例

### 案例1：OKF v0.2（Google Cloud）

OKF从v0.1到v0.2的核心架构变化就是信任优先：
- v0.1：核心是类型系统（Fact, Metric, Concept...），信任是附加属性
- v0.2：信任、来源、生命周期提升为一等公民：
  - `sources[]`数组要求记录每个来源的author、usage_count、last_modified
  - `generated`+`verified`双字段分离（生产者≠验证者）
  - Trust Tier自动推导：unverified → machine-confirmed → human-reviewed
  - `status`+`stale_after`生命周期管理
  - Attested Computation让机器生成的指标可验证（[verifiable-knowledge-claim](verifiable-knowledge-claim.md)模式）

效果：Enrichment Agent生成的元数据自动标记为unverified，经过attester验证后升级为machine-confirmed，人工审核后升级为human-reviewed，Agent消费时根据tier决定使用策略。

### 案例2：dbt schema.yml（反面案例）

dbt的schema.yml是传统内容优先设计的典型：
- 90%字段描述column类型、tests、description
- 没有trust_tier、没有stale_after、没有generated_by/verified_by分离
- description由人写或AI生成，无法区分
- 后果：AI辅助生成的description和tests无法自动识别可信度，团队不知道哪些是AI生成的需要人工审核

改进方向：在meta字段中扩展信任字段（dbt支持meta自定义扩展）。

### 案例3：知识图谱/RDF（传统方案的问题）

RDF/OWL等传统知识图谱格式：
- 核心是三元组（subject-predicate-object）表示
- 有provenance标准（PROV-O），但使用复杂，多数实现不强制
- 没有trust tier、没有stale_after、没有生成者/验证者分离
- 适合推理，不适合Agent安全消费

### 案例4：Web内容可信度标注（同构思想）

Web安全领域的Content Security Policy、SSL证书等级（DV/OV/EV）是同源思想：
- DV证书（域名验证）≈ machine-confirmed
- OV证书（组织验证）≈ human-reviewed
- 浏览器根据证书等级决定安全标识（锁标/绿色地址栏/警告）
- Agent对知识的信任分级应类比浏览器对网站的信任分级

## 反模式

### 反模式1：自证可信——生产者=验证者

知识条目由同一实体生成和验证（如Agent自己标记"已验证"，或人自己写的内容自己approve）。**后果**：信任信号无意义，无法区分"自己说自己对"和"独立验证通过"。

**正确做法**：generated_by和verified_by必须是不同实体；Agent生成内容初始tier=unverified。

### 反模式2：二元信任——只有"可信/不可信"

简单的is_trusted布尔字段，没有中间等级。**后果**：要么过度信任（只要标记为可信就全信），要么过度保守（只要有一个疑点全不信）；无法表达"机器验证过但人还没看"这种常见中间状态。

**正确做法**：使用三级trust_tier（unverified/machine-confirmed/human-reviewed），允许渐进式信任。

### 反模式3：长生不老知识——没有过期机制

知识创建后永远有效，没有stale_after或last_verified更新。**后果**：Agent使用3年前过时的API文档、废弃的政策、已更名的术语做出错误决策。

**正确做法**：每条知识必须设置stale_after；过期自动降级；定期复审机制。

### 反模式4：信任字段边缘化——把trust放在meta的meta里

把信任字段放在深层嵌套的可选meta字段中（如`metadata.annotations.trust.score`），而不是frontmatter的顶层。**后果**：消费方需要解析多层嵌套才能获取信任信息；很多Agent会忽略非顶层字段；信任检查容易被跳过。

**正确做法**：信任字段（trust_tier, sources, stale_after, generated_by, verified_by）放在frontmatter/元数据顶层，与id/type/name同级。

### 反模式5：信任不变——一旦验证永远可信

人工审核过的内容trust_tier永久标记为human-reviewed，不随时间降级。**后果**：3年前审核通过的内容可能已经过时但仍被当作高信任度知识使用；审核者离职/知识更新后tier不变化。

**正确做法**：即使human-reviewed，超过stale_after也要降级；知识内容变更后tier重置为unverified需重新验证。

### 反模式6：内容字段先行——先把内容填完再补信任信息

知识入库流程先完善内容字段（description、properties、schema），信任字段"以后再说"。**后果**：大量知识条目缺少信任信号，Agent不敢用或盲目用；补填信任信息的工作永远排不上优先级。

**正确做法**：信任字段是必填项，没有信任字段的知识条目不允许进入知识库（或只允许进入staging区，不对Agent开放消费）。

### 反模式7：关键词优先检索——检索只看内容匹配度

RAG检索排序只考虑语义相似度/关键词匹配，不考虑trust_tier和新鲜度。**后果**：一条3年前LLM自动生成的高匹配度但unverified内容排在1周前人工审核的略低匹配度内容前面。

**正确做法**：检索排序公式中trust_tier权重≥内容匹配度权重；新鲜度（stale_after距离）作为重要排序因子。

## 适用边界

### 适用场景

- ✅ AI Agent消费的知识库/RAG系统（消除Agent对知识可信度的盲目信任）
- ✅ 人机协作的知识管理平台（区分人和AI生成的内容）
- ✅ 元数据格式设计（新建或改造schema时）
- ✅ 数据目录/数据治理平台（数据资产可信度分级）
- ✅ 需要知识审计和治理的企业知识管理系统
- ✅ 多Agent协作系统（Agent间传递知识需要信任背书）

### 不适用场景

- ❌ 纯人工消费的文档系统（人可以自行判断可信度）
- ❌ 个人笔记（信任模型不需要如此正式，成本高于收益）
- ❌ 完全确定且永不过时的知识（如数学定理——但仍建议有来源标注）
- ❌ 实时数据流处理（数据流的信任通过传输层安全如TLS保证，不是元数据层）

## 检验标准

| 维度 | 检验点 |
|------|-------|
| 字段优先级 | 信任字段在schema顶层，与id/type同级，不在嵌套meta中 |
| 生产者验证者分离 | generated_by ≠ verified_by，禁止自证 |
| Trust Tier三级 | 有unverified/machine-confirmed/human-reviewed三个明确等级 |
| 状态机完备 | 有明确的升级和降级规则，升级需证据，降级可自动 |
| 过期机制 | 每条知识有stale_after，过期自动降级 |
| Agent禁止自验证 | Agent无法将自己生成的内容标记为human-reviewed |
| 检索排序 | 信任等级和新鲜度在检索排序中有明确权重 |
| 内容渐进 | 信任字段必填，内容字段可渐进补充（信任优先于完整） |

## 与其他模式的关系

| 关系模式 | 关系类型 | 说明 |
|---------|---------|------|
| [provenance-driven-trust.md](provenance-driven-trust.md) | 基础设施层互补 | 溯源驱动信任是信任**基础设施**（哈希校验、仅追加日志、Sign-off凭证），本模式是元数据**schema设计原则**（字段优先级），两者构成完整信任栈 |
| [verifiable-knowledge-claim.md](verifiable-knowledge-claim.md) | 具体实现手段 | 可验证知识声明是machine-confirmed的核心升级路径——attester验证通过才能从unverified升级为machine-confirmed |
| [credibility-dual-track.md](../../methodology-patterns/research-knowledge/credibility-dual-track.md) | 来源评估互补 | 可信度双轨制评估来源可信度（人写vs机器生成），本模式管理知识条目自身的trust_tier |
| [knowledge-as-code-paradigm.md](knowledge-as-code-paradigm.md) | 架构思想支撑 | 知识即代码提供"复用SE范式"的思想；本模式中trust_tier类比代码review状态（draft/CI-passed/approved），stale_after类比@Deprecated |
| [metadata-layering.md](metadata-layering.md) | 架构分层指导 | 元数据分层模式提供分层架构（内容层/元数据层/溯源层/凭证层），本模式规定各层的优先级顺序 |

---

*模式版本：v1.0 | 创建日期：2026-08-17 | maturity: L1（validation_count=1：OKF v0.2实践验证）*
