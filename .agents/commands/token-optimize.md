---
id: "token-optimize"
title: "Token优化指令集"
source: "AGENTS.md#token-optimize指令;roles/token-optimizer.md"
x-toml-ref: "../../.meta/toml/.agents/commands/token-optimize.toml"
---
# Token优化指令集

## 触发条件

- 用户需要对LLM应用进行Token使用优化，降低推理成本
- 现有Prompt/上下文结构需要重构以提高缓存命中率
- 需要设计分层缓存策略、上下文压缩方案或模型路由策略
- 长文档处理需要分层分治方案设计
- 需要评估Token优化效果、建立度量基线
- 评审已有优化方案，识别风险和反模式
- 制定渐进式Token优化路线图

## 输入规范

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| operation | string | 是 | 操作类型：audit/design/review/quickwin/roadmap/evaluate |
| target | string | 否 | 优化目标描述：系统/Prompt/对话流程/RAG管线/Agent架构 |
| stage | string | 否 | 当前项目阶段：planning/development/production/optimization |
| quality_baseline | string | 否 | 质量基线要求（如"准确率≥95%"、"用户满意度≥4.5"），默认从黄金测试集获取 |
| cost_target | string | 否 | 成本优化目标（如"降本50%"），不指定则按ROI排序 |
| observability | boolean | 否 | 是否已建立可观测性（Helicone/Langfuse/Portkey等），默认false需先建基线 |

**operation类型说明**：

| operation | 用途 | 典型输出 |
|-----------|------|---------|
| audit | Token使用审计，识别浪费点 | 浪费点清单+优先级排序+P0速赢项 |
| design | 优化方案设计 | 方案文档+技术选型+实施步骤 |
| review | 已有优化方案评审 | 风险清单+C编号禁令检查+改进建议 |
| quickwin | P0速赢项实施指导 | 立即可做的5项Quick Wins+操作步骤 |
| roadmap | 渐进式优化路线图 | 四阶段路线图+里程碑+预期收益 |
| evaluate | 优化效果评估 | 指标对比+ROI分析+反弹风险预警 |

## RACI责任分配矩阵

**RACI模型说明**：
- **R** = 负责执行（Responsible）：实际完成工作的角色
- **A** = 最终审批（Accountable）：对结果负最终责任，每项活动有且仅有一个A
- **C** = 需咨询（Consulted）：决策前需征求意见、提供专业输入的角色，双向沟通
- **I** = 需知会（Informed）：决策后需告知进展与结果的角色，单向沟通

| Token优化核心活动 | orchestrator | architect | token-optimizer | developer | reviewer | co-founder |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 触发与范围确认 | **R/A** | C | C | C | I | I |
| P0禁令预检与基线检查 | C | C | **R/A** | I | C | I |
| 架构方案与技术选型 | C | **R/A** | C | C | C | I |
| 优化方案详细设计 | I | C | **R/A** | C | C | I |
| Prompt结构/缓存设计指导 | I | C | **R/A** | C | I | I |
| 代码实施与配置调整 | I | C | C | **R/A** | I | I |
| 优化方案评审与风险识别 | I | C | **R** | C | **A** | I |
| 质量基线与效果验证 | C | C | C | C | **R/A** | I |
| 灰度发布与回退策略设计 | I | C | **R/A** | C | C | C |
| 重大架构变更/成本决策审批 | R | C | C | I | C | **A** |

### 审批权限边界

- P0速赢项（max_tokens/vLLM升级/Prompt重构/精简系统提示/接入监控）：token-optimizer指导→developer实施→reviewer验收
- 常规优化方案（缓存策略/上下文压缩/对话管理）：token-optimizer设计→reviewer评审→developer实施
- 架构级变更（模型路由/分层分治/按需加载架构）：architect设计→token-optimizer方案→reviewer评审→co-founder知悉
- 涉及牺牲质量阈值的决策：必须co-founder审批，禁止token-optimizer自行决定

## 执行步骤

### S0：启动与P0禁令预检

- 确认operation类型和优化目标
- **强制执行P0禁令检查**（参考[09-constraints.md](../docs/knowledge/learning/llm-token-optimization/09-constraints.md)）：
  - C-001：确认质量底线，禁止牺牲不可接受质量
  - C-003：检查是否已有可观测性基线，无基线先建监控
  - C-024：检查是否有黄金测试集，无基线先建质量基线
- 记录CMD-LOG: CMD_START

> **为什么P0预检必须在S0？** C-003和C-024是"没有就不能开始优化"的硬性前提——没有度量就无法验证优化效果，没有质量基线就无法判断优化是否导致质量下降。跳过预检直接给方案，等同于在没有尺子的情况下做裁剪。

### S1：现状审计与浪费点识别

- 查阅[快速参考卡](../docs/knowledge/learning/llm-token-optimization/10-quick-reference.md)了解核心数据
- 根据operation类型执行：
  - **audit**：分析Token使用分布，识别Top 5浪费点
  - **design/review**：收集现有系统Prompt结构、缓存策略、上下文管理方式
  - **quickwin**：直接识别5项P0速赢项
  - **roadmap**：评估当前成熟度阶段
  - **evaluate**：收集优化前后指标数据
- 参考[决策树](../docs/knowledge/learning/llm-token-optimization/06-decision-framework/01-decision-tree.md)选择优化路径
- 记录CMD-LOG: AUDIT_COMPLETED

### S2：方案设计与技术选型

- 根据审计结果选择三大路径实施顺序：**减少(Reduce) → 复用(Reuse) → 压缩(Compress)**
- 参考[选型矩阵](../docs/knowledge/learning/llm-token-optimization/06-decision-framework/02-selection-matrix.md)选择技术组合
- 参考[最佳实践模式](../docs/knowledge/learning/llm-token-optimization/06-decision-framework/03-patterns.md)选择适用模式（P-001~P-005）：
  - **P-001 渐进式优化**：所有场景必选，按四阶段路线图推进
  - **P-002 分层缓存**：高流量系统必选（静态前缀→语义→会话三层）
  - **P-003 质量-成本动态平衡**：多用户层级/多任务复杂度场景必选
  - **P-004 按需加载懒加载**：代码助手/工具调用型Agent必选
  - **P-005 分层分治处理**：RAG/长文档场景必选
- 对每个方案明确：三维权衡（成本↓/质量?/延迟?）、ROI预估、实施周期
- 检查C编号禁令合规性（逐条对照P0-P2禁令）
- 记录CMD-LOG: DESIGN_COMPLETED

### S3：实施指导（按operation类型）

- **audit模式**：输出浪费点审计报告，按ROI排序
- **design模式**：输出详细方案文档，包含：
  - Prompt结构重构方案（静态前缀排序、缓存友好设计）
  - 缓存策略（KV缓存/前缀缓存/语义缓存层级设计）
  - 上下文压缩方案（摘要策略/实体提取/滑动窗口）
  - 模型路由策略（大小模型分级、任务复杂度路由）
  - 长文档处理方案（MapReduce/分层分治/语义切块）
  - 灰度发布与回退策略
- **review模式**：输出评审报告：
  - P0-P2禁令逐条检查结果
  - 识别反模式（参考[反模式清单](../docs/knowledge/learning/llm-token-optimization/06-decision-framework/04-anti-patterns.md)）
  - 风险等级评估（🔴阻断/🟡需改进/🟢通过）
  - 改进建议
- **quickwin模式**：输出5项P0速赢操作步骤：
  1. 设置合理max_tokens
  2. 升级vLLM（自托管场景）
  3. 重构Prompt静态前缀排序
  4. 精简系统提示冗余修饰
  5. 接入可观测性监控
- **roadmap模式**：输出四阶段路线图（参考[快速参考卡](../docs/knowledge/learning/llm-token-optimization/10-quick-reference.md)四阶段表）
- **evaluate模式**：输出效果评估报告
- 记录CMD-LOG: GUIDANCE_PROVIDED

### S4：质量门禁检查

- reviewer执行质量门禁：
  - [ ] P0禁令全部遵守（C-001/C-002/C-007/C-012/C-020）
  - [ ] 方案有明确三维权衡分析（成本/质量/延迟）
  - [ ] 有灰度发布和自动回退策略（C-020/C-021）
  - [ ] 用户级分流（非请求级）（C-013）
  - [ ] 语义缓存阈值≥0.9（C-007）
  - [ ] 不涉及动态内容在静态前缀前（C-006）
  - [ ] max_tokens已设置合理值（C-012）
  - [ ] 有持续监控计划防"优化反弹"（C-019/C-027）
- 记录CMD-LOG: GATE_PASSED/GATE_FAILED

### S5：交付与后续跟踪建议

- 交付优化方案/报告/路线图
- 建议建立持续优化机制：
  - 月度Token成本审计
  - 黄金测试集定期回归
  - 缓存命中率监控
  - 优化反弹预警
- 提醒参考[跨行业案例](../docs/knowledge/learning/llm-token-optimization/04-cases/01-case-studies.md)设定期望值
- 记录CMD-LOG: CMD_COMPLETE

**三大路径决策树**：
```
需要Token优化？
├─ 还没做过任何优化？ → 先做P0速赢（quickwin模式）
│  └─ max_tokens → vLLM → Prompt重构 → 精简提示 → 接入监控
├─ 已有基础优化，需要系统化设计？ → design模式
│  ├─ 高QPS系统 → P-002分层缓存优先
│  ├─ RAG/长文档 → P-005分层分治优先
│  ├─ Agent/工具调用 → P-004按需加载优先
│  ├─ 多用户层级 → P-003动态平衡优先
│  └─ 所有场景 → P-001渐进式（必选基础）
├─ 已有方案需要评审？ → review模式
│  └─ 对照27条禁令+反模式清单逐条检查
├─ 需要评估优化效果？ → evaluate模式
│  └─ 成本↓% + 质量基线对比 + 延迟变化
└─ 需要长期规划？ → roadmap模式
   └─ 四阶段路线图：速赢→质量优化→高级优化→极致优化
```

## 输出规范

| 产出物 | 格式 | 说明 |
|--------|------|------|
| 浪费点审计报告 | Markdown表格 | 浪费点+严重度+ROI+建议模式（audit） |
| 优化方案文档 | Markdown | 含技术选型+实施步骤+三维权衡+灰度策略（design） |
| 方案评审报告 | Markdown | 禁令检查+风险等级+改进建议（review） |
| P0速赢操作指南 | Markdown清单 | 5项速赢+具体操作步骤（quickwin） |
| 优化路线图 | Markdown表格 | 四阶段+时间+预期收益+里程碑（roadmap） |
| 效果评估报告 | Markdown | 指标对比+ROI+反弹风险（evaluate） |
| CMD-LOG日志 | 控制台输出 | 结构化日志，见下方规范 |

## 质量验收

- P0级禁令（C-001/C-002/C-007/C-012/C-020）零违反
- 方案明确标注三维权衡影响（成本降低幅度/质量影响预估/延迟变化）
- 所有涉及上线的方案包含灰度发布和自动回退策略
- Quick Wins项1-2周可落地，预期降本30-50%
- 渐进式路线图四阶段完整，不跳步（C-004）
- 引用知识库文档路径正确，术语使用[术语表](../docs/knowledge/learning/llm-token-optimization/glossary.md)标准定义

## 约束条件

- 严格遵守27条禁令（P0-P3分级），P0禁令违反即阻断
- 不在架构方案未确定阶段给出具体优化实施方案（受阶段守卫规则约束）
- 不在未读取需求文档和架构设计方案的情况下给出具体优化建议（遵守前置文档强制读取协议）
- 不做脱离质量底线的极端成本优化，质量阈值是硬约束
- 不负责具体代码实现（归developer），不负责系统整体架构设计（归architect）
- 不负责Mermaid图表的编写、审查与渲染验证（归developer/reviewer/tester）
- 优化建议必须基于可观测性数据，禁止"凭感觉"给建议（C-003）
- 语义缓存相似度阈值不得低于0.9（C-007）
- 所有量化收益必须说明三个前提：适用场景、团队基线、测量方法（C-025）

## CMD-LOG日志规范

- cmd标识：token-optimize
- Session ID前缀：tokopt-
- Session格式：tokopt-YYYYMMDD-<topic>
- 步骤：S0-S5共6步

**特有事件定义**：

| 时机 | level | event | msg模板 | ctx必填字段 |
|------|-------|-------|---------|------------|
| P0预检完成 | INFO | P0_CHECK_PASSED | P0禁令预检通过：已确认质量基线/可观测性/黄金测试集 | quality_baseline, observability, has_golden_set |
| P0预检失败 | WARN | P0_CHECK_FAILED | P0预检未通过：<原因>，需先解决前置条件 | failed_checks, blocking_reasons |
| 审计完成 | INFO | AUDIT_COMPLETED | Token审计完成：发现<N>个浪费点，Top3：<points> | waste_count, top_waste_points, estimated_savings |
| 方案设计完成 | INFO | DESIGN_COMPLETED | 优化方案设计完成：采用<patterns>，预期降本<percent>% | patterns_selected, expected_cost_reduction, quality_impact, latency_impact |
| 评审结果 | INFO/WARN | REVIEW_RESULT | 方案评审<结果>：<N>个🔴阻断项，<M>个🟡改进项 | result, blocking_count, warning_count, c_violations |
| 速赢项识别 | INFO | QUICKWINS_IDENTIFIED | P0速赢项识别完成：<N>项可立即实施，预期1-2周降本<percent>% | quickwin_count, expected_quickwin_savings, implementation_time |
| 路线图生成 | INFO | ROADMAP_GENERATED | 渐进式路线图生成：四阶段，预计<N>月达到<percent>%降本 | phases, total_duration, target_reduction, milestones |
| 效果评估 | INFO | EVALUATION_COMPLETED | 效果评估完成：成本降低<cost>%，质量变化<quality>%，延迟变化<latency>% | cost_reduction, quality_change, latency_change, roi, rebound_risk |
| 质量门禁通过 | INFO | GATE_PASSED | 质量门禁通过：方案满足P0禁令和三维权衡约束 | gate_checks_passed |
| 质量门禁失败 | WARN | GATE_FAILED | 质量门禁失败：<原因>，需返工 | failed_gates, required_fixes |

**典型日志示例**：

```
[CMD-LOG] | level=INFO | cmd=token-optimize | step=S0 | event=CMD_START | session=tokopt-20260801-chatbot | msg=开始Token优化：智能客服系统设计阶段优化 | ctx={"operation":"design","target":"智能客服对话系统","stage":"development","quality_baseline":"准确率≥95%","observability":false}
[CMD-LOG] | level=WARN | cmd=token-optimize | step=S0 | event=P0_CHECK_FAILED | session=tokopt-20260801-chatbot | msg=P0预检未通过：无可观测性基线、无黄金测试集，需先建立监控和质量基线 | ctx={"failed_checks":["C-003","C-024"],"blocking_reasons":["无监控无法度量","无质量基线无法验证"]}
[CMD-LOG] | level=INFO | cmd=token-optimize | step=S2 | event=DESIGN_COMPLETED | session=tokopt-20260801-chatbot | msg=优化方案设计完成：采用P-001+P-002+P-003，预期降本75% | ctx={"patterns_selected":["P-001","P-002","P-003"],"expected_cost_reduction":"75%","quality_impact":"-1~2%（可接受范围）","latency_impact":"TTFT降低40%（缓存命中）"}
[CMD-LOG] | level=INFO | cmd=token-optimize | step=S5 | event=CMD_COMPLETE | session=tokopt-20260801-chatbot | msg=Token优化方案交付完成，建议建立月度审计机制 | ctx={"duration":"~1h","deliverables":["方案文档","灰度策略","回退机制"],"follow_up":"月度成本审计+黄金集回归"}
```

## 关联资源

- [Token Optimizer角色定义](../roles/token-optimizer.md)
- [LLM Token优化知识库](../docs/knowledge/learning/llm-token-optimization/README.md)
- [快速参考卡（3分钟速查）](../docs/knowledge/learning/llm-token-optimization/10-quick-reference.md)
- [27条禁令清单（P0-P3分级）](../docs/knowledge/learning/llm-token-optimization/09-constraints.md)
- [决策树](../docs/knowledge/learning/llm-token-optimization/06-decision-framework/01-decision-tree.md)
- [选型矩阵](../docs/knowledge/learning/llm-token-optimization/06-decision-framework/02-selection-matrix.md)
- [最佳实践模式P-001~P-005](../docs/knowledge/learning/llm-token-optimization/06-decision-framework/03-patterns.md)
- [反模式与常见陷阱](../docs/knowledge/learning/llm-token-optimization/06-decision-framework/04-anti-patterns.md)
- [跨行业案例参考](../docs/knowledge/learning/llm-token-optimization/04-cases/01-case-studies.md)
- [评估指标体系](../docs/knowledge/learning/llm-token-optimization/05-evaluation/01-metrics-framework.md)
- [术语表](../docs/knowledge/learning/llm-token-optimization/glossary.md)
- [token-optimize-cmd Skill门面](../skills/token-optimize-cmd/SKILL.md)
- [CMD-LOG日志规范](../rules/cmd-log-specification.md)
- [阶段守卫规则](../rules/stage-guardrails.md)

### 知识库资料档案

- [Token优化快速参考](../docs/knowledge/learning/llm-token-optimization/10-quick-reference.md) — 3分钟速查卡，涵盖P0速赢清单、模式选择决策树、三维权衡速查表、常见陷阱预警。指令集定义"做什么"（执行流程），快速参考提供"怎么做"（操作细节）
- [Token优化知识库总览](../docs/knowledge/learning/llm-token-optimization/README.md) — 29份结构化文档完整索引，含原理/方法/工具/案例/评估/决策框架全模块
