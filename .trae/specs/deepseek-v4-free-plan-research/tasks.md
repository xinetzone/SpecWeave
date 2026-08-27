---
version: "1.0"
---

# DeepSeek-V4 正式版免费方案深度调研 Tasks

## Task Dependencies

```
Task 1 (R阶段事实采集) → Task 2 (I阶段洞察分析) → Task 3 (E阶段模式萃取)
→ Task 4 (V阶段对抗审查) → Task 5 (文档撰写) → Task 6 (索引更新)
→ Task 7 (独立评审) → Task 8 (修复闭环)
```

---

## Task 1: R阶段——事实清单采集与验证

**Status:** pending
**Priority:** high
**Acceptance Criteria:** AC-01, AC-02

**Description:**
基于已收集的多源信息，整理≥30条客观事实清单，每条事实标注来源编号，剥离所有因果推断和主观判断。重点覆盖：模型规格、免费额度、定价数据、功能清单、限流规则、时间线、竞品对比数据。

**Test Requirements:**

- **rule: TR-1.1** 事实数量≥30条
- **rule: TR-1.2** 无因果推断词（"因为"/"所以"/"导致"/"错误"/"失误"）
- **rule: TR-1.3** 每条事实可追溯到具体来源
- **rule: TR-1.4** 关键数字（价格/额度/并发数/上下文长度等）交叉验证≥2个来源
- **rule: TR-1.5** 不实信息（会员套餐/每日50次等）已明确标记为错误并说明来源

**Completion Evidence:** （待填写）

---

## Task 2: I阶段——核心洞察提炼

**Status:** pending
**Priority:** high
**Acceptance Criteria:** AC-03
**Depends On:** Task 1

**Description:**
基于R阶段事实清单，提炼≥3条核心洞察，每条包含完整四元组（陈述/证据/反常识/行动）。洞察需覆盖：商业模式本质、免费策略设计逻辑、信息不对称风险点。

**Test Requirements:**

- **rule: TR-2.1** 洞察数量≥3条
- **rule: TR-2.2** 每条洞察包含四元组：陈述+证据(引用F-xxx)+反常识+行动建议
- **rule: TR-2.3** 洞察之间维度独立不重叠
- **rule: TR-2.4** 行动建议具体可执行，非空泛口号

**Completion Evidence:** （待填写）

---

## Task 3: E阶段——跨领域模式萃取

**Status:** pending
**Priority:** medium
**Acceptance Criteria:** AC-04
**Depends On:** Task 2

**Description:**
从DeepSeek免费策略中萃取1个可迁移到其他产品分析的模式："大模型产品免费-付费双轨商业模式分析框架"。包含触发场景、核心步骤、反模式、检验标准、跨领域迁移示例。

**Test Requirements:**

- **rule: TR-3.1** 模式包含：名称+触发场景+核心步骤(3-7步)+≥3个反模式+检验标准+≥1个跨领域迁移示例
- **rule: TR-3.2** 反模式来自本次调研的实际教训（如不实会员信息）
- **rubric: TR-3.3** 模式可迁移性评分：0-2分，≥1分通过（评分标准：换一个大模型厂商能否复用该框架分析其免费策略）

**Completion Evidence:** （待填写）

---

## Task 4: V阶段——四视角对抗审查

**Status:** pending
**Priority:** high
**Acceptance Criteria:** AC-05
**Depends On:** Task 3

**Description:**
对R阶段事实和I阶段洞察执行四视角对抗审查：
- 🔴 魔鬼代言人：攻击数据准确性、因果谬误、幸存者偏差
- 🟢 新人视角：攻击术语可理解性、信息缺失、入门门槛
- 🟠 老板视角：攻击实用价值、决策辅助性、成本信息完整性
- 🔵 未来视角：攻击时效性、政策变动风险、二阶效应

审查意见≥5条，至少采纳2条对事实/洞察进行修正。

**Test Requirements:**

- **rule: TR-4.1** 四个视角全部覆盖
- **rule: TR-4.2** 审查意见≥5条且具体（非客套话）
- **rule: TR-4.3** 至少采纳2条意见修正原产出
- **rule: TR-4.4** 所有修正有记录

**Completion Evidence:** （待填写）

---

## Task 5: 原子化文档撰写（11篇wiki文档）

**Status:** pending
**Priority:** high
**Acceptance Criteria:** AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-16
**Depends On:** Task 4

**Description:**
按照spec.md中的Requirements创建11篇原子化wiki文档，存放在 `.agents/docs/knowledge/learning/07-vendor-product-learning/deepseek/` 目录下。每篇文档包含YAML frontmatter、章节导航、结构化内容。

文档清单：
1. `00-overview.md` — 总览与导航
2. `01-web-app-free.md` — 网页/App免费使用
3. `02-api-free-tier.md` — API新用户免费额度
4. `03-api-pricing-comparison.md` — API定价与对比
5. `04-v4-pro-capabilities.md` — V4-Pro能力详解
6. `05-v4-flash-capabilities.md` — V4-Flash能力详解
7. `06-self-hosting.md` — 开源自托管
8. `07-third-party-free.md` — 第三方免费路径
9. `08-free-vs-paid.md` — 免费vs付费对比
10. `09-faq-mythbusting.md` — FAQ与误区澄清
11. `10-glossary.md` — 术语表（≥15个术语）

**Test Requirements:**

- **rule: TR-5.1** 11个文件全部存在于指定目录
- **rule: TR-5.2** 每个文件包含有效YAML frontmatter（title/description/source/updated_at字段）
- **rule: TR-5.3** 所有价格/额度/数字数据与R阶段事实验证一致
- **rule: TR-5.4** 术语表≥15个术语，每个术语有中英文+一句话解释
- **rule: TR-5.5** FAQ≥12个问题，覆盖会员/收费/额度/限流/选型等核心疑问
- **rule: TR-5.6** 不实信息已明确标注为谣言并说明事实
- **rule: TR-5.7** 00-overview.md包含三层免费路径对比表
- **rule: TR-5.8** 03-api-pricing-comparison.md包含完整峰谷价格表
- **rule: TR-5.9** 08-free-vs-paid.md包含多维度对比决策表
- **rubric: TR-5.10** 信息准确性评分：0-2分，≥2分通过（所有关键数据与官方文档一致）
- **rubric: TR-5.11** 易理解性评分：0-2分，≥1分通过（新人视角：术语有解释、步骤清晰、无阅读障碍）
- **rubric: TR-5.12** 完整性评分：0-2分，≥2分通过（覆盖用户问题的所有方面：功能/限制/条件/期限/额度/能力/对比）

**Completion Evidence:** （待填写）

---

## Task 6: 导航索引更新

**Status:** pending
**Priority:** medium
**Acceptance Criteria:** AC-17
**Depends On:** Task 5

**Description:**
更新 `07-vendor-product-learning/README.md`，在厂商列表中添加deepseek条目及子目录链接。遵循现有README格式。

**Test Requirements:**

- **rule: TR-6.1** README.md已更新，包含deepseek条目
- **rule: TR-6.2** 链接路径正确可访问
- **rule: TR-6.3** 不破坏现有README格式和其他条目

**Completion Evidence:** （待填写）

---

## Task 7: 预提交验证

**Status:** pending
**Priority:** high
**Acceptance Criteria:** AC-18
**Depends On:** Task 6

**Description:**
执行预提交验证：链接检查、Markdown格式检查、文件名规范检查。

**Test Requirements:**

- **rule: TR-7.1** 所有内部链接可访问（无断链）
- **rule: TR-7.2** 文件名遵循kebab-case纯英文规范
- **rule: TR-7.3** 无中文文件名
- **rule: TR-7.4** YAML frontmatter格式正确

**Completion Evidence:** （待填写）

---

## Task 8: 独立评审

**Status:** pending
**Priority:** high
**Acceptance Criteria:** AC-19
**Depends On:** Task 7

**Description:**
由独立fresh context执行评审，检查所有AC是否满足、信息是否准确、文档是否完整、质量门是否通过。

**Test Requirements:**

- **rule: TR-8.1** 所有rule类型AC有独立验证证据
- **rule: TR-8.2** 所有rubric类型AC有评分和理由
- **rule: TR-8.3** 无遗留actionable finding
- **rubric: TR-8.4** 评审 thoroughness：0-2分，≥1分通过

**Completion Evidence:** （待填写）

---

## Task 9: 修复闭环（如需）

**Status:** pending
**Priority:** high
**Depends On:** Task 8

**Description:**
如果独立评审发现问题，修复所有actionable findings后重新提交验证。

**Test Requirements:**

- **rule: TR-9.1** 所有评审问题已修复或标记为wontfix（附理由）
- **rule: TR-9.2** 修复后重新通过验证

**Completion Evidence:** （待填写）
