---
type: Pattern
id: "verifiable-knowledge-claim"
source: "../../../reports/competitive-analysis/retrospective-knowledge-catalog-wiki-20260815/insights/insight-04-attested-computation.md"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
related_patterns:
  - "provenance-driven-trust"
  - "knowledge-as-code-paradigm"
  - "credibility-dual-track"
  - "vendor-neutral-three-layer-learning"
tags:
  - verifiable-computation
  - agent-safety
  - knowledge-representation
  - metadata-design
  - trust-model
  - deterministic-verification
  - openapi-pattern
---
# 可验证知识声明：从自然语言描述到可执行规范

## 模式概述

在设计面向AI Agent消费的知识/元数据/指标体系时，对于数值型、规则型、可计算的知识条目，不应只提供自然语言描述，而应采用**可执行声明+独立验证**模式：明确运行时环境、参数化逻辑、执行器说明、确定性验证代码。消费者不需要信任生产者，只需在自己的环境运行验证代码即可确认结果正确性。这与OpenAPI从"手写API文档"演进到"可执行API规范"是同一逻辑路径，是解决Agent幻觉（尤其是SQL/计算类幻觉）的核心架构模式。

该模式由Google OKF（Open Knowledge Format）v0.2的`Attested Computation`类型实践验证。

## 问题现象

AI Agent知识消费中的常见失败模式：

1. **自然语言歧义导致SQL幻觉**：指标用自然语言定义（如"月活跃用户数"）+示例SQL，Agent根据自然语言理解生成SQL，幻觉率极高
2. **无法验证数据正确性**：Agent拿到一个数值，无法判断是否正确，只能盲目相信或拒绝使用
3. **指标定义变更无法检测**：指标定义变了，历史数据是否仍符合新定义无法自动判断
4. **信任依赖于人**：必须人工审核每条知识的正确性，无法自动化扩展
5. **黑盒知识**：生产者说"这个值是对的"，消费者无法独立验证，信任建立在权威而非证据上

根因：传统元数据设计停留在"描述"阶段，没有提供"执行+验证"机制。自然语言描述永远有歧义，Agent无法可靠地将自然语言转换为正确的计算逻辑。

## 核心设计模型

可验证知识声明的五元组结构：

```
┌─────────────────────────────────────────────────────────────────────┐
│  可验证知识声明（Verifiable Knowledge Claim）                        │
├─────────────────────────────────────────────────────────────────────┤
│  📌 1. runtime（运行时声明）                                         │
│     指定执行环境：bigquery / dbt / python / sql / duckdb / ...     │
│     消费者必须在匹配的runtime中执行                                   │
├─────────────────────────────────────────────────────────────────────┤
│  📌 2. parameters（参数接口）                                        │
│     显式声明输入参数（名称、类型、范围、默认值）                      │
│     Agent只能绑定参数值，不能修改计算逻辑                              │
│     → 类比函数签名：def metric(start_date: date, end_date: date)     │
├─────────────────────────────────────────────────────────────────────┤
│  📌 3. executor（执行器定义）                                        │
│     可执行的计算逻辑（SQL查询、Python函数、dbt模型等）                │
│     固定逻辑，参数化输入                                             │
│     执行后返回计算结果 + receipt（执行收据：输入哈希+输出哈希+时间戳） │
├─────────────────────────────────────────────────────────────────────┤
│  📌 4. attester（确定性验证器）                                      │
│     ⭐ 关键：独立的验证代码，不是生产者自证                           │
│     约束：无LLM调用、纯代码、确定性（相同输入永远相同输出）           │
│     验证内容：结果类型、值域合理性、业务约束、交叉校验                 │
│     → 消费者在自己环境运行attester验证executor的输出                 │
├─────────────────────────────────────────────────────────────────────┤
│  📌 5. documentation（语义文档链接）                                 │
│     业务概念文档（自然语言）通过Markdown链接引用，不内联计算逻辑      │
│     自然语言给人看，executor/attester给机器跑                        │
└─────────────────────────────────────────────────────────────────────┘
```

### attester ≠ unit test（关键区分）

表面上attester和unit test都是"验证代码正确性"，但有本质区别：

| 维度 | unit test | attester |
|------|----------|----------|
| **执行方** | 生产者（开发团队自己跑） | 消费者（在自己信任域内跑） |
| **目的** | 验证代码逻辑正确 | 验证知识声明结果可信 |
| **信任模型** | 信任生产者的测试质量 | 不需要信任生产者 |
| **运行时机** | CI/CD构建时 | 消费时每次执行（或缓存命中时跳过） |
| **验证对象** | 代码行为 | 数据结果（值域/约束/业务规则） |
| **独立性** | 和代码同仓库、同团队维护 | 可以由消费者独立编写 |

attester的思想更接近：密码学中的签名验证、可重复构建的哈希校验、HTTPS的证书验证——**验证方不依赖对生产方的信任**。

### 信任模型：密码学思想的迁移

| 传统信任模型 | 可验证声明信任模型 |
|------------|-----------------|
| 信任生产者的权威/声誉 | 不需要信任，只验证证据 |
| 人来审核确认正确性 | attester代码自动验证 |
| 审核一次，信任很久 | 每次消费都可以验证 |
| 知识传递依赖信任链 | 知识传递附带验证方法 |

这直接借鉴了密码学/分布式系统的核心思想：
- **零知识证明的近亲**：不透露如何计算，但提供验证方法
- **Reproducible Build（可重复构建）**：确定性构建→二进制可验证
- **Checksum校验**：数据完整性通过哈希验证而非信任传输方
- **OpenAPI演进**：手写文档→可执行规范→自动Mock/SDK生成/测试

## 标准实施步骤

### 步骤1：识别适用知识类型

判断哪些知识条目需要可验证声明：

| 知识类型 | 是否需要可验证声明 | 原因 |
|---------|-----------------|------|
| 业务KPI/指标（DAU、GMV、转化率） | ✅ 必须 | Agent经常需要查数、计算、做决策 |
| 数据质量规则（非空率、唯一性、范围） | ✅ 必须 | 可以自动执行检查 |
| 合规规则（PII检测、权限校验） | ✅ 必须 | 合规要求必须可审计可验证 |
| 业务概念定义（什么是"活跃用户"） | ⚠️ 可选 | 纯概念定义用自然语言+示例即可 |
| 架构决策记录（ADR） | ❌ 不需要 | 不是可计算的知识 |
| 操作手册/How-to | ❌ 不需要 | 是流程指导，不是声明式知识 |

### 步骤2：定义五元组结构

为每个需要声明的知识条目定义：

1. **runtime选择**：选择消费者可获得的runtime（BigQuery/SQLite/Python/dbt/...），优先选择广泛可用的runtime
2. **parameters设计**：明确参数名称、类型、约束；越少越好（最小接口原则）
3. **executor实现**：编写确定性的计算逻辑；不依赖外部不稳定API；返回结果+receipt
4. **attester编写**（最关键）：
   - 验证结果类型和schema
   - 验证值域（如：转化率必须在[0,1]区间）
   - 验证业务约束（如：活跃用户数≤总用户数）
   - 用替代算法交叉验证（可选但推荐）
   - **禁止调用LLM**（attester本身必须是确定性的）
5. **documentation链接**：业务含义用自然语言写在独立文档中，executor中只放链接

### 步骤3：设计receipt格式

receipt是执行收据，用于后续审计和缓存：
```yaml
# receipt示例
receipt:
  executor_id: "monthly_active_users_v2"
  executor_version: "2.1.0"
  parameters_hash: "sha256:a1b2c3..."  # 参数哈希
  result_hash: "sha256:d4e5f6..."      # 结果哈希
  executed_at: "2026-08-17T10:30:00Z"
  runtime: "bigquery"
  attester_version: "1.0.0"
  attestation_passed: true
```

### 步骤4：建立attester审查流程

attester代码是信任的根基，必须严格审查：
- attester代码独立于executor维护
- attester必须经过人工Code Review
- attester变更需要版本号升级
- 禁止在attester中引入不确定因素（随机数、网络调用、LLM）

### 步骤5：Agent消费协议

Agent使用可验证声明的标准流程：
1. **查找**：知识检索时，优先查找有可验证声明的条目（而非自然语言描述）
2. **执行**：用自己的参数调用executor，获取结果+receipt
3. **验证**：在自己的信任域内运行attester验证结果
4. **使用**：attester通过→使用结果；attester失败→降级处理/请求人工审核/拒绝使用
5. **缓存**：根据receipt的参数哈希和结果哈希做缓存（相同参数+相同版本可复用）

## 演进路径参考：从文档到可执行规范

这不是一个全新的发明，而是多个领域反复出现的相同演进模式：

| 领域 | 阶段1：自然语言描述 | 阶段2：可执行规范 | 阶段3：生态工具 |
|------|-----------------|----------------|-------------|
| **API设计** | 手写Word/PDF文档 | OpenAPI/Swagger规范 | 自动生成SDK/测试/Mock |
| **基础设施** | 手工部署文档 | Terraform/Pulumi IaC | 计划预览/合规检查/漂移检测 |
| **数据构建** | 文档描述指标 | dbt model + tests | 自动文档/数据血缘/测试 |
| **知识元数据** | 自然语言+示例SQL | Attested Computation | 自动验证/Agent安全消费（当前） |
| **软件构建** | 手工编译打包 | Makefile/Bazel | 可重复构建/签名验证 |

洞察：每当一个领域从"人读"演进到"机器消费"，都会经历这个从描述到可执行规范的转变。知识元数据正在经历同样的转变。

## 实战案例

### 案例1：OKF Attested Computation（Google Cloud）

OKF v0.2引入`type: Attested Computation`，是该模式的标杆实现：
- executor支持BigQuery SQL和Python两种runtime
- parameters显式声明类型和约束
- attester要求确定性纯代码，无LLM调用
- Agent（如Enrichment Agent）在消费数值型知识时强制要求attestation通过
- 业务概念文档通过Markdown链接引用，不与SQL混在一起

### 案例2：dbt tests

dbt的`tests`机制是该模式在数据工程领域的实现：
- model（executor）：SQL定义数据转换
- tests（attester）：schema tests + data tests验证数据正确性
- 每次dbt run自动执行tests，不通过则构建失败
- 这是数据工程领域已经验证的实践

### 案例3：OpenAPI/Swagger

- 阶段1：手写API文档（Word/Confluence）→经常过时、不一致
- 阶段2：OpenAPI规范→可机器解析、可验证、可生成SDK
- 阶段3：生态工具链→自动Mock、自动测试、类型安全客户端
- 知识元数据的演进路径完全相同

### 案例4：可重复构建（Reproducible Builds）

- 问题：如何确保二进制文件确实由声明的源代码构建？
- 解决：确定性构建环境+构建过程哈希校验
- 思想同源：不依赖信任，依赖可验证的证据

## 反模式

### 反模式1：自证清白——executor和attester合一

executor自己声明结果正确，没有独立验证。**后果**：生产者可以通过有bug的executor产生错误结果，而attester永远通过，验证形同虚设。

**正确做法**：attester必须独立编写，用不同逻辑路径验证，最好由不同人/团队维护。

### 反模式2：LLM验证——在attester中调用LLM判断正确性

用LLM来验证计算结果是否正确。**后果**：LLM本身就有幻觉，用幻觉验证幻觉不增加任何可信度；attester失去确定性，相同输入可能得到不同结果。

**正确做法**：attester必须是确定性纯代码。如果需要语义理解，放在documentation层给人看。

### 反模式3：全量可验证——试图让所有知识都可验证

给纯概念性、不可计算的知识也强加executor/attester结构。**后果**：形式主义，增加不必要复杂度；attester写成恒为true的空壳。

**正确做法**：只对可计算、可验证的知识类型（指标、规则、合规检查）使用该模式。

### 反模式4：网络依赖——attester依赖外部API调用

attester中调用第三方API、数据库查询、网络服务。**后果**：验证结果依赖外部可用性，不可重复；网络超时/API变更导致验证失败或错误通过。

**正确做法**：attester只验证executor返回的结果本身，executor可以有依赖，但attester必须纯本地、无网络、确定性。

### 反模式5：参数爆炸——parameters设计过于复杂

暴露大量细粒度参数，让Agent可以微调executor行为。**后果**：参数组合爆炸，测试覆盖困难；Agent可能构造出executor未预料的参数组合，导致错误结果。

**正确做法**：最小参数接口原则——只暴露必要参数，逻辑固定在executor内部。

### 反模式6：自然语言混入executor——在SQL中嵌入业务解释

在executor的SQL/Python代码中用大量注释解释业务含义。**后果**：业务逻辑变更时需要同时改代码和注释，容易不一致；自然语言和可执行逻辑耦合。

**正确做法**：业务解释放在独立的Markdown文档中，executor/attester只放可执行逻辑，通过链接关联。

## 适用边界

### 适用场景

- ✅ AI Agent消费的指标/KPI体系（消除SQL幻觉）
- ✅ 数据质量规则与合规检查（自动验证）
- ✅ 高可信度要求的知识系统（决策辅助、金融、医疗）
- ✅ 需要审计追溯的数据产品（谁在什么时候用什么参数验证了什么结果）
- ✅ 跨团队数据契约（生产者和消费者用attester约定正确性标准）

### 不适用场景

- ❌ 纯概念/理论性知识（无法编码为确定性计算）
- ❌ 个人笔记/非系统化知识（成本高于收益）
- ❌ 探索性分析（快速迭代阶段不需要严格验证）
- ❌ 所有输入都来自LLM生成且无ground truth的场景（attester无法验证LLM输出的事实正确性）

## 检验标准

| 维度 | 检验点 |
|------|-------|
| attester独立性 | attester由不同逻辑路径验证结果，不是executor的重跑 |
| attester确定性 | 相同输入运行attester 100次，结果100次相同 |
| attester无LLM | attester代码中无任何LLM/网络/随机数调用 |
| 参数最小化 | parameters数量≤5个（经验值），每个参数有明确约束 |
| 失败处理 | Agent在attester失败时有明确降级策略（拒绝使用/人工审核/告警） |
| receipt可审计 | receipt包含足够信息可以事后复现和验证 |
| 文档分离 | 业务含义在独立文档，executor中只有链接 |

## 与其他模式的关系

| 关系模式 | 关系类型 | 说明 |
|---------|---------|------|
| [provenance-driven-trust.md](provenance-driven-trust.md) | 基础设施互补 | 溯源驱动信任是信任基础设施层（校验码/日志/sign-off），本模式是知识表示层的可验证声明，两者互补构成完整信任链 |
| [knowledge-as-code-paradigm.md](knowledge-as-code-paradigm.md) | 架构思想支撑 | 知识即代码提供"复用SE范式"的思想，本模式是其在信任/验证维度的具体落地（executor≈代码，attester≈测试） |
| [credibility-dual-track.md](../methodology-patterns/research-knowledge/credibility-dual-track.md) | 来源信任互补 | 可信度双轨解决来源可信度评级问题（人写的vs机器生成的），本模式解决内容可验证问题，正交 |
| [vendor-neutral-three-layer-learning.md](../methodology-patterns/research-knowledge/vendor-neutral-three-layer-learning.md) | 发现方法 | 三层剥离学习法可用于发现Attested Computation模式——OKF规范层定义了attested_computation类型，工具层提供执行器 |

---

*模式版本：v1.0 | 创建日期：2026-08-17 | maturity: L1（validation_count=1：OKF实践验证，dbt tests/OpenAPI/Reproducible Builds为同构先例佐证）*
