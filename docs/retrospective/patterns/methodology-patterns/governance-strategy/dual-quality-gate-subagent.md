---
id: "dual-quality-gate-subagent"
source: "../../../reports/competitive-analysis/retrospective-sunlogin-bootbox-analysis-20260704/insight-extraction.md#pattern-3"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/dual-quality-gate-subagent.toml"
maturity: "L2"
validation_count: 4
reuse_count: 0
documentation_level: "detailed"
related_patterns:
  - "subagent-output-quality-checklist"
  - "three-stage-content-validation"
  - "batched-creation-independent-review"
  - "subagent-atomic-task-template"
  - "output-behavior-specification"
---
# 子代理双重质量门模式（事前约束+事后校验）

## 模式概述

委托子代理生成内容（特别是长文本、多轮调用场景）时，采用"事前输出约束+事后内容校验"的双重质量门机制，从源头减少问题发生概率，并兜底捕获漏网之鱼。两层门共同保障输出内容纯净度，避免工具标签、XML、思考过程等违禁内容污染最终文档。

## 核心逻辑

```
子代理输出质量 = 事前约束（委托query中明确禁止项） ⊕ 事后校验（输出后关键词扫描）
             ≠ 只靠子代理"自觉"（不可靠，总有失误）
             ≠ 只做事后检查（问题已经写入文件，修复成本高）
```

**核心洞察**：子代理不是100%可靠的——即使告诉它"不要输出工具调用"，长上下文下仍可能出现标签残留、格式漂移等问题。事前约束从源头降低问题发生率（将问题率从20%降到5%），事后校验作为兜底捕获剩余问题（将漏网率从5%降到0），两层结合才能可靠保障输出质量。

## 第一层：事前约束（委托时P0强制）

在每个子代理委托query的末尾，**必须**附加明确的输出格式安全约束：

```
【输出格式强制约束】
1. 你的输出必须是纯净的Markdown文档内容，只包含文档本身的文字
2. 严禁输出任何工具调用标签（如<|FunctionCallBegin|>、<toolcall>、TodoWrite等）
3. 严禁输出XML标签、JSON代码块、内部思考过程
4. 严禁输出"好的，我来..."、"以下是..."等对话式开头
5. 严禁在文档中插入任何与文档内容无关的说明文字
6. 如果对内容有疑问或需要确认，请直接生成你认为最合理的内容，不要输出疑问
7. 直接写入文件后，只返回"完成"两个字，不要有其他输出
```

**约束模板已落地为标准模板**：参见 [subagent-output-quality-checklist.md](../../../../../.agents/templates/subagent-output-quality-checklist.md)

## 第二层：事后校验（输出后P1扫描）

子代理返回内容、写入文件后，执行关键词扫描校验，检查是否有违禁内容残留。

### P1强制扫描关键词清单

| 违禁内容类型 | 扫描关键词 |
|------------|-----------|
| 工具调用标签 | `<toolcall>`, `<|FunctionCallBegin|>`, `TodoWrite`, `todo_write`, `functions.` |
| XML/HTML标签污染 | `<thinking>`, `<answer>`, `<system>`, `<｜`, `｜>` |
| 对话式开头 | `好的`, `我来`, `以下是`, `当然可以`, `没问题` |
| 内部思考标记 | `让我思考`, `首先我需要`, `我应该先` |
| 工具执行痕迹 | `toolcall_result`, `function call`, `执行命令` |

### 校验执行时机

1. **写入文件前**：如果是主代理直接写入，先在内存中扫描关键词
2. **写入文件后**：文件写入后，用Grep工具扫描文件内容
3. **批量完成后**：全部分批完成后，统一对所有文件做一次全量扫描

### 校验处理流程

1. 发现违禁内容 → 立即定位具体位置
2. 使用Edit工具删除/替换违禁内容
3. 重新扫描确认已清理干净
4. 记录问题类型，后续优化事前约束

## 正反例

### 正例：开机盒子分析任务改进前后对比

| 改进前（无双重门） | 改进后（有双重门） |
|------------------|------------------|
| 子代理输出中混入TodoWrite工具标签 | 委托query末尾附加强制约束，标签问题大幅减少 |
| 标签写入文件后很久才发现，需要逐章排查 | 每批完成后立即扫描，发现问题即时修复 |
| 修复一个标签时容易破坏文档格式 | 问题小范围发现，修复成本低 |
| 问题反复出现，没有系统性预防 | 约束模板沉淀，后续所有任务复用 |

改进结果：落地双重质量门后，后续4个硬件Wiki任务中标签污染问题发生率降为0。

### 反模式

| 反模式 | 表现 | 问题 |
|--------|------|------|
| **信任子代理"自觉"** | 只说"写一篇分析报告"，不附加格式约束 | 子代理在长上下文下容易"忘记"格式要求，输出污染 |
| **只做事前不做事后** | query里说了不能输出标签，但写完不检查 | 小概率问题成为漏网之鱼，直到最后才发现 |
| **只做事后不做事前** | 不做约束，等问题出现再一个个修 | 问题率高，修复成本高，容易遗漏 |
| **约束太笼统** | "请注意输出格式"这种模糊要求 | 子代理不知道具体不能输出什么，约束无效 |
| **发现问题不修复** | 看到标签残留觉得"不影响阅读"就放过 | 小问题累积，最后文档质量面目全非 |
| **修复不沉淀模板** | 每次遇到问题临时修复，不总结约束模板 | 同样问题反复踩坑 |

## 适用边界

### 适用场景

- ✅ 任何子代理委托场景，特别是生成长文本/文档内容时
- ✅ 多轮子代理调用，上下文较长时
- ✅ 子代理输出需要写入文件时
- ✅ 批量委托多个子代理并行工作时

### 不适用场景

- ❌ 子代理只做数据分析/计算不返回文本内容
- ❌ 交互式对话（问答/头脑风暴），不需要最终文档产出
- ❌ 子代理明确只返回JSON/结构化数据（用schema约束即可）

## 落地资源

本模式已落地为以下可复用资源：

1. **P0约束模板**：[.agents/templates/subagent-output-quality-checklist.md](../../../../../.agents/templates/subagent-output-quality-checklist.md)
2. **Wiki验收清单**：[.agents/templates/subagent-wiki-delivery-checklist.md](../../../../../.agents/templates/subagent-wiki-delivery-checklist.md)（含内容纯净性检查项）

## 实施步骤

1. **复制P0约束**：每次子代理委托时，将输出格式强制约束复制到query末尾
2. **委托执行**：执行子代理委托
3. **即时扫描**：子代理返回后，立即用关键词列表扫描输出内容
4. **即时修复**：发现违禁内容立即修复，不要拖延
5. **最终扫描**：所有内容生成完毕后，对所有输出文件做一次全量扫描
6. **沉淀改进**：如果发现新的违禁模式，更新约束模板和扫描关键词

## 与其他模式的关系

| 关系模式 | 关系类型 | 说明 |
|---------|---------|------|
| [batched-creation-independent-review.md](../ai-collaboration/batched-creation-independent-review.md) | 配套使用 | 分批创作+独立质检是流程框架，双重质量门是质检环节的具体手段 |
| [three-stage-content-validation.md](three-stage-content-validation.md) | 上位模式 | 双重质量门是三阶段验证中"格式合规性验证"的具体实现 |
| [subagent-atomic-task-template.md](../ai-collaboration/subagent-atomic-task-template.md) | 模板配套 | 子原子任务模板中应包含输出格式约束 |
| [output-behavior-specification.md](../ai-collaboration/output-behavior-specification.md) | 理论基础 | 输出行为规范是事前约束的理论依据 |
| [subagent-output-quality-checklist.md](../../../../../.agents/templates/subagent-output-quality-checklist.md) | 落地模板 | 本模式的具体落地checklist模板 |
