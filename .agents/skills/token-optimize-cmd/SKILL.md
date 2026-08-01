---
name: token-optimize-cmd
version: 1.0.0
description: "当用户提到'token优化'、'省token'、'降低成本'、'Token使用优化'、'prompt优化'、'缓存策略'、'上下文压缩'、'模型路由'、'长文档处理'、'Token成本'、'降本'、'推理成本'、'Token浪费'、'优化LLM成本'时，必须使用此技能。提供LLM Token使用优化全流程指导：P0禁令预检→浪费点审计→方案设计→评审→效果评估。不要凭直觉给优化建议——本Skill封装了27条禁令（P0-P3分级）、5个最佳实践模式、三维权衡框架和渐进式路线图，确保优化方案不踩红线、ROI可控。"
argument-hint: "<operation:audit/design/review/quickwin/roadmap/evaluate> [target]"
user-invocable: true
paths:
  - ".agents/commands/token-optimize.md"
  - ".agents/roles/token-optimizer.md"
  - ".agents/skills/token-optimize-cmd/scripts/check_token_p0.py"
  - "docs/knowledge/learning/llm-token-optimization/"
  - "rules/cmd-log-specification.md"
  - "rules/stage-guardrails.md"
title: "Token优化命令 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/token-optimize-cmd/SKILL.toml"
---
# Token优化命令 Skill

> ⚠️ **本Skill是命令入口门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+决策树+核心步骤+安全清单）
> - L2：[commands/token-optimize.md](../../commands/token-optimize.md)（完整流程）+ [llm-token-optimization知识库](../../docs/knowledge/learning/llm-token-optimization/README.md)（方法论）+ [cmd-log-specification.md](../../rules/cmd-log-specification.md)（日志规范）

## 1. Skill ID
`token-optimize-cmd`

## 2. 功能描述

提供LLM Token使用优化全生命周期指导能力，六种操作方案：

| 方案 | 推荐场景 | 优势 |
|------|---------|------|
| **P0速赢（quickwin）** | ⭐ 从未做过优化，1-2周快速降本30-50% | 立即可做，ROI最高 |
| **浪费审计（audit）** | ⭐ 不知道钱花在哪，需要识别浪费点 | 量化分析，优先级排序 |
| **方案设计（design）** | ⭐ 系统化优化，需要缓存/压缩/路由方案 | 完整方案，三维权衡 |
| **方案评审（review）** | ⭐ 已有优化方案，需要检查风险 | 27条禁令逐条检查 |
| **路线图（roadmap）** | ⭐ 长期规划，四阶段渐进式优化 | 里程碑清晰，预期明确 |
| **效果评估（evaluate）** | 优化上线后验证效果 | ROI分析，反弹预警 |

核心功能：P0禁令预检→现状审计→模式选择(P-001~P-005)→方案设计→评审→效果评估→持续优化。

> **为什么用本Skill而非凭直觉给建议？** Token优化有27条不可逾越的禁令红线——跳过可观测性直接优化（C-003）会导致无法验证效果，语义缓存阈值低于0.9（C-007）会引发线上事故，不设max_tokens（C-012）一次幻觉就能产生巨额账单。手动给建议容易遗漏这些P0级禁令，本Skill强制S0预检确保不踩红线，并按"减少→复用→压缩"ROI顺序推荐方案，避免一步到位上微调/蒸馏的过度工程（C-004）。

## 3. 何时使用本技能

### 触发词

当用户提到以下任何内容时触发：
- "token优化"、"省token"、"降低成本"、"Token使用优化"
- "prompt优化"、"缓存策略"、"上下文压缩"
- "模型路由"、"长文档处理"、"按需加载"
- "Token成本"、"降本"、"推理成本"
- "Token浪费"、"优化LLM成本"
- 需要评审LLM系统架构中的成本效率
- 需要设计Prompt缓存友好结构

### 必用场景
- **新建LLM应用**：架构设计阶段考虑Token优化策略
- **成本飙升**：Token费用异常增长，需要审计和优化
- **方案评审**：团队提出的优化方案需要风险检查
- **上线前检查**：优化方案上线前做P0禁令和灰度策略检查
- **定期审计**：月度/季度Token成本审计，防"优化反弹"

> **关于触发**：即使没有明确说"用token优化命令"，只要涉及LLM推理成本优化、Prompt结构重构、缓存策略设计、上下文管理方案，就应该使用本Skill。Token优化是约束驱动的设计活动，27条禁令是安全底线，跳过本Skill直接给建议风险极高。

## 4. 方案选择决策树

```
需要Token优化指导？
├─ 从未做过任何优化？ → quickwin方案（P0速赢5项）
│  └─ max_tokens→vLLM→Prompt重构→精简提示→接入监控
├─ 不知道钱花在哪/浪费点在哪？ → audit方案
│  └─ 分析Token分布→识别Top5浪费→按ROI排序
├─ 需要设计系统化优化方案？ → design方案
│  ├─ 高QPS对话系统 → P-002分层缓存优先
│  ├─ RAG/长文档 → P-005分层分治优先
│  ├─ Agent/工具调用 → P-004按需加载优先
│  ├─ 多用户层级 → P-003动态平衡优先
│  └─ 所有场景 → P-001渐进式（必选基础）
├─ 已有方案需要检查风险？ → review方案
│  └─ 27条禁令逐条检查+反模式识别→风险评级
├─ 需要长期优化规划？ → roadmap方案
│  └─ 四阶段：速赢→质量优化→高级优化→极致优化
└─ 优化已上线需要验证效果？ → evaluate方案
   └─ 成本↓%+质量基线对比+延迟变化+反弹风险
```

### ⚠️ 强制：触发时记录输入参数日志

决策前输出CMD_START日志（session前缀 `tokopt-YYYYMMDD-<topic>`）：
```
[CMD-LOG] | level=INFO | cmd=token-optimize | step=S0 | event=CMD_START | session=tokopt-... | msg=开始Token优化：<简述> | ctx={"operation":"audit/design/...","target":"...","stage":"planning/development/production/optimization"}
```

> **为什么决策前必须记录日志？** Token优化涉及六类操作（audit/design/review/quickwin/roadmap/evaluate），operation选错会导致方向完全偏航——需要审计浪费点却直接给了设计方案，会遗漏关键数据收集。CMD_START记录operation和目标便于回溯决策起点。

### 三大路径强制顺序

所有优化方案必须按以下ROI顺序推进，禁止跳步（C-004）：
1. **减少（Reduce）**：根本不送没用的token（最先做，ROI最高）
2. **复用（Reuse）**：算过的不要再算（必做，缓存命中率决定成本下限）
3. **压缩（Compress）**：用更少token说同样的事（最后做，压缩是双刃剑）

> **为什么不能先做压缩？** 压缩技术（摘要、蒸馏）实施成本高、质量风险大，而减少（max_tokens、精简提示）和复用（缓存）成本极低、风险极小。在还没做减少和复用的情况下直接上压缩，等于"漏水的桶不先补洞反而买更小的桶"——违反ROI优先原则。

## 5. 核心步骤（快速开始）

```
步骤1：读取 [commands/token-optimize.md](../../commands/token-optimize.md) 了解完整S0-S5六步流程
步骤2：强制执行P0预检（可运行 scripts/check_token_p0.py 辅助检查）：
   - [ ] 质量基线是否明确？（C-001）
   - [ ] 可观测性是否建立？（C-003）无监控先建监控
   - [ ] 黄金测试集是否存在？（C-024）无基线先建质量基线
步骤3：根据决策树选择operation方案
步骤4：quickwin方案（立即可做）：
   - 1. 设置合理max_tokens防无限生成
   - 2. 自托管场景升级vLLM（吞吐提升5-10倍）
   - 3. 重构Prompt：静态前缀（系统提示/工具定义）放最前面启用缓存
   - 4. 精简系统提示冗余修饰（但缓存后仅贵10%，不过度缩短）
   - 5. 接入Helicone/Langfuse/Portkey监控
步骤5：design方案：
   - 参考决策树选择P-001~P-005模式组合
   - 按减少→复用→压缩顺序设计
   - 每个方案标注三维权衡（成本↓/质量?/延迟?）
   - 必须包含灰度发布+用户级分流+自动回退
步骤6：review方案：
   - 对照27条禁令P0-P3逐条检查
   - 识别反模式（一步到位/一刀切/只看成本不看质量等）
   - 给出风险等级（🔴阻断/🟡需改进/🟢通过）
步骤7：交付方案时提醒持续监控防"优化反弹"（C-019/C-027）
```

> 完整RACI矩阵、输入参数规范、27条禁令清单、5个模式详解、四阶段路线图见L2文档 [commands/token-optimize.md](../../commands/token-optimize.md) 和 [llm-token-optimization知识库](../../docs/knowledge/learning/llm-token-optimization/README.md)。

## 6. P0禁令检查清单（优化前必过）

- [ ] **C-001** 不牺牲不可接受质量——质量阈值是硬约束
- [ ] **C-002** 不自托管裸用Transformers Pipeline上线——比vLLM贵5-10倍
- [ ] **C-003** 不做无可观测性基线的优化——先接监控再优化
- [ ] **C-004** 不一步到位上微调/蒸馏——先做Quick Wins
- [ ] **C-007** 语义缓存阈值≥0.9——低于0.9会命中错误答案
- [ ] **C-012** 所有接口设max_tokens——防幻觉产生巨额账单
- [ ] **C-020** 不全量上线不做灰度——用户级分流+对照组
- [ ] **C-024** 不在无质量基线时优化——先建黄金测试集
- [ ] 按减少→复用→压缩顺序，不跳步
- [ ] 动态内容不放静态前缀前（C-006）

> **为什么P0预检是强制的？** 违反5条P0禁令（C-001/C-002/C-007/C-012/C-020）的后果是：C-001导致用户流失、C-007导致线上事故返回错误答案、C-012一次幻觉产生巨额账单——这些不是"建议"而是"事故预防红线"。跳过预检直接给方案，等同于不带安全网走钢丝。

## 7. 安全检查清单（优化方案质量门）

- [ ] P0级禁令（5条）零违反
- [ ] 方案明确标注三维权衡影响（成本降低%/质量影响%/延迟变化%）
- [ ] 灰度发布策略包含用户级分流（非请求级，C-013）
- [ ] 质量低于阈值时自动回退机制（C-021）
- [ ] 不搞一刀切策略，按任务复杂度/用户层级分级（C-008）
- [ ] 静态前缀在Prompt最前面，动态内容在后面（C-006）
- [ ] 语义缓存阈值≥0.9（C-007）
- [ ] max_tokens已设合理值（C-012）
- [ ] 有持续监控计划防"优化反弹"（C-019/C-027）
- [ ] 量化收益说明三个前提：适用场景、团队基线、测量方法（C-025）

## 8. 执行日志（CMD-LOG）

执行token-optimize命令集时，必须按 [CMD-LOG规范](../../rules/cmd-log-specification.md) 输出结构化日志：
> ⚠️ **铁律一（🔴强制）**：S0 CMD_START 必须是命令集执行后的**第一条输出**，禁止在CMD_START之前输出任何其他内容。违反将导致日志链路断裂。

- `cmd=token-optimize`，session前缀 `tokopt-YYYYMMDD-<topic>`
- 步骤编号 S0-S5（启动预检→审计→设计→实施指导→门禁→交付）
- 10个特有事件：`P0_CHECK_PASSED`、`P0_CHECK_FAILED`、`AUDIT_COMPLETED`、`DESIGN_COMPLETED`、`REVIEW_RESULT`、`QUICKWINS_IDENTIFIED`、`ROADMAP_GENERATED`、`EVALUATION_COMPLETED`、`GATE_PASSED`、`GATE_FAILED`

> 完整字段说明、事件表格、日志示例见L2文档 [commands/token-optimize.md §CMD-LOG日志规范](../../commands/token-optimize.md#cmd-log日志规范)。

## 9. 常见错误处理

| 问题场景 | 处理方式 |
|---------|---------|
| P0预检失败（无监控/无质量基线） | 明确指出缺失的前置条件，建议先建立可观测性和黄金测试集，不给出具体优化方案 |
| 用户要求"尽可能省token"（无质量约束） | 主动确认质量底线（Q_min），引用C-001说明质量阈值是硬约束，拒绝无底线优化 |
| 团队想直接上微调/蒸馏 | 引用C-004和ROI数据，建议先完成阶段1-2 Quick Wins再评估是否需要高级优化 |
| 语义缓存阈值想设0.85"提高命中率" | 引用C-007说明<0.9的风险——错误答案复用引发线上事故，建议从0.95起步逐步调优 |
| 优化方案不设回退机制 | 引用C-021要求必须有质量护栏，质量低于阈值自动升级模型/降低压缩率 |
| 跨场景/跨用户一刀切策略 | 引用C-008说明一刀切的危害，建议按任务复杂度/用户层级设计分级策略 |

## 10. Gotchas（陷阱与反直觉行为）

> **为什么需要Gotchas？** 错误处理记录"已知错误码及修复方式"，Gotchas记录"容易踩的坑、反直觉行为"——不会报错但会导致优化效果差或隐性风险。

- **缓存后系统提示词成本仅10%，不要为省几个token过度缩短系统提示**：这是最常见的反直觉陷阱——开发者看到系统提示占了大量token就疯狂删减，但Prompt Caching/APC命中后静态前缀成本仅为普通输入的10%。过度缩短系统提示导致提示词遵循率下降、输出质量波动，损失远大于缓存后那点成本差异（C-005）。
- **max_tokens限制的是输出不是输入，但输出价格是输入的3-8倍**：设置max_tokens=2000不影响输入上下文长度，但能防止模型无限生成或幻觉输出——一次不设限的幻觉请求可能输出几万token，成本飙升10-100倍（C-012）。这是投入产出比最高的优化项，没有之一。
- **减少路径优先≠压缩路径无用**：三大路径顺序是实施优先级而非价值判断——减少最先做是因为成本最低、风险最小，但成熟系统减少路径收益递减后，缓存（复用）和高级压缩技术（语义缓存、模型路由、蒸馏）才是降本主力。不要因为"减少最先做"就认为压缩不重要。
- **"优化反弹"是沉默的成本杀手**：优化上线后不是结束而是开始——提示词修改、新功能上线、模型版本更新、业务量变化都会导致Token成本悄悄涨回优化前水平。3-6个月后可能成本回到原点，之前的投入全部白费（C-019/C-027）。必须建立月度审计和缓存命中率监控。
- **初级团队不要直接上阶段3/4高级优化**：没有LLM运维经验的团队应先完成阶段1（P0速赢），阶段2（结构化输出、RAG优化）做扎实后再考虑模型路由、语义缓存、LoRA等高级技术。初级团队高级优化的时间估算应乘以2-3倍，强行上阶段3/4大概率项目延期或做不出来（C-026）。
- **语义缓存不是传统缓存，阈值设定是安全问题不是性能问题**：语义缓存通过embedding相似度匹配，阈值0.95意味着只复用高度相似的问题答案，阈值0.85会把不相关问题的答案返回给用户——这不是"缓存命中率低一点"的性能问题，而是"AI给用户错误回答"的产品事故（C-007）。
- **Prompt中静态前缀放前面不是代码风格问题而是成本问题**：Prompt Caching要求静态前缀（系统提示、工具定义、少样本示例）必须在最前面且顺序不变，动态内容（用户问题、上下文变量）放后面。动态内容插在静态前缀中间会导致每次前缀变化缓存全部失效，前缀缓存命中率从90%+降到0%，成本上升2-5倍（C-006）。

## 11. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 完整命令文档（RACI/参数/步骤/日志） | L2 | [commands/token-optimize.md](../../commands/token-optimize.md) | 每次使用必读 |
| LLM Token优化知识库首页 | L2 | [llm-token-optimization/README.md](../../docs/knowledge/learning/llm-token-optimization/README.md) | 了解知识体系 |
| 快速参考卡（3分钟速查） | L2 | [10-quick-reference.md](../../docs/knowledge/learning/llm-token-optimization/10-quick-reference.md) | P0速赢+核心数据 |
| 27条禁令清单 | L2 | [09-constraints.md](../../docs/knowledge/learning/llm-token-optimization/09-constraints.md) | review时逐条检查 |
| 决策树 | L2 | [01-decision-tree.md](../../docs/knowledge/learning/llm-token-optimization/06-decision-framework/01-decision-tree.md) | 技术选型 |
| 选型矩阵 | L2 | [02-selection-matrix.md](../../docs/knowledge/learning/llm-token-optimization/06-decision-framework/02-selection-matrix.md) | 技术组合选择 |
| 最佳实践模式P-001~P-005 | L2 | [03-patterns.md](../../docs/knowledge/learning/llm-token-optimization/06-decision-framework/03-patterns.md) | design模式选择 |
| 反模式与常见陷阱 | L2 | [04-anti-patterns.md](../../docs/knowledge/learning/llm-token-optimization/06-decision-framework/04-anti-patterns.md) | review时风险识别 |
| 跨行业案例 | L2 | [01-case-studies.md](../../docs/knowledge/learning/llm-token-optimization/04-cases/01-case-studies.md) | 设定期望值 |
| 评估指标体系 | L2 | [01-metrics-framework.md](../../docs/knowledge/learning/llm-token-optimization/05-evaluation/01-metrics-framework.md) | evaluate效果评估 |
| P0预检辅助脚本 | L1工具 | [scripts/check_token_p0.py](scripts/check_token_p0.py) | S0预检自动化 |
| CMD-LOG日志规范 | L2 | [cmd-log-specification.md](../../rules/cmd-log-specification.md) | 日志格式规范 |
| 阶段守卫规则 | L2 | [stage-guardrails.md](../../rules/stage-guardrails.md) | 判断当前阶段约束 |
| Token Optimizer角色定义 | L2 | [roles/token-optimizer.md](../../roles/token-optimizer.md) | 角色职责边界 |

## 12. 与其他Skill的协作

| 协作场景 | 配合Skill | 协作方式 |
|---------|----------|---------|
| 架构方案设计阶段 | architect角色 | architect负责系统架构，token-optimizer在架构确定后给出优化方案 |
| 优化方案评审 | reviewer角色 | token-optimizer做专业审查，reviewer做最终质量门禁 |
| 优化效果分析 | insight-cmd | evaluate方案中用insight-cmd做数据分析和根因诊断 |
| 优化方案导出报告 | export-report-cmd | 方案完成后用export-report-cmd导出正式报告 |
| 代码实施 | developer角色 | token-optimizer给出设计指导，developer负责具体代码实现 |

## 13. Changelog

- **v1.0.0** (2026-08-01): 初始版本，基于llm-token-optimization知识库封装为命令门面Skill，支持audit/design/review/quickwin/roadmap/evaluate六种操作，封装27条P0-P3禁令检查和5个最佳实践模式。
