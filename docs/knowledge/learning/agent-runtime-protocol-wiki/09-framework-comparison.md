# 09 框架对比：九条设计原则遵循度评估

> 本章是[08章](08-protocol-design-principles.md)九条设计原则的落地延伸，通过星级评分系统对比五大主流Agent框架对协议设计原则的遵循程度，帮助读者快速评估框架成熟度和生产适用性。

## 评分标准

| 评分 | 含义 |
|-----|------|
| ⭐⭐⭐⭐⭐ | 完全遵循：该原则是框架的核心理念，有完整的一等公民实现 |
| ⭐⭐⭐⭐ | 良好遵循：有清晰的实现，支持核心场景，仅存在次要缺陷 |
| ⭐⭐⭐ | 部分遵循：有相关能力，但设计不系统或存在明显缺口 |
| ⭐⭐ | 弱遵循：有零散支持，但没有形成完整的设计范式 |
| ⭐ | 基本未体现：框架中几乎找不到该原则的影子 |

---

## 九条设计原则跨框架对比表

| 设计原则 | LangGraph | OpenAI Assistants | OpenAI Agents SDK | AutoGen | Claude SDK |
|---------|-----------|------------------|------------------|---------|-----------|
| **原则一：对象先于API**<br>先定义Thread/Run/Step/Event/Artifact/Checkpoint对象语义，再设计API。对象边界比具体API方法名更持久。 | ⭐⭐⭐⭐⭐<br>Thread/Run/Checkpoint/StreamPart都是显式一等对象，整个API围绕对象生命周期设计。 | ⭐⭐⭐⭐⭐<br>Assistant/Thread/Message/Run/Run Step是核心REST资源模型，API天然对象中心化。 | ⭐⭐⭐<br>有RunContext/Agent/Handoff概念，但缺少显式Checkpoint和Artifact一等对象。 | ⭐⭐<br>以Agent/Message/Team为核心，缺少显式Run/Checkpoint/Artifact边界定义。 | ⭐⭐<br>Session/ToolResult隐式存在，没有形成完整的Protocol对象体系。 |
| **原则二：Run是执行边界**<br>超时/取消/成本/权限/Trace/错误/产物归属都挂在Run上，Thread只承载上下文。 | ⭐⭐⭐⭐⭐<br>Run是显式执行单元，Thread和Run通过`configurable.thread_id`严格分离，所有执行属性归属Run。 | ⭐⭐⭐⭐⭐<br>Run是核心资源，status/usage/required_action/last_error等全部执行属性挂在Run上。 | ⭐⭐⭐<br>Runner管理执行，但Run边界隐式，没有显式Run ID贯穿全链路追踪。 | ⭐⭐<br>Team管理多Agent，Run边界模糊在对话流中，缺少独立的执行单元抽象。 | ⭐⭐<br>Session管理对话，但没有显式的执行边界对象分离。 |
| **原则三：Checkpoint是恢复契约**<br>Checkpoint不只是"保存对话历史"，而是"可以从这里继续执行"的完整契约，要求状态/工具副作用/外部资源/权限上下文都能重新对齐。 | ⭐⭐⭐⭐⭐<br>Checkpointer完整实现：parent_id版本链、pending_writes、content-addressed存储、支持任意节点回滚。 | ⭐⭐<br>Thread保存消息历史，但没有真正的Checkpoint——无法回滚到特定步骤、无法从任意执行点恢复。 | ⭐<br>无内置持久化机制，完全没有Checkpoint概念。 | ⭐<br>无内置持久化，`save_state()`需要开发者手动实现且不保证恢复一致性。 | ⭐<br>无持久化能力，无Checkpoint，`interrupt()`后只能从头重新开始。 |
| **原则四：Event是一等公民**<br>不要只在最后返回结果。状态变更/工具调用/产物增量/错误都应该以Event形式实时推送，前端和监控系统依赖事件流而非最终答案。 | ⭐⭐⭐⭐⭐<br>多模式Stream（messages/updates/events/debug/custom），事件粒度细，支持自定义事件。 | ⭐⭐⭐⭐<br>SSE支持丰富的event type（thread.run.created/step.created/tool_calls.done等），覆盖关键状态变更。 | ⭐⭐⭐<br>StreamEvent回调机制存在，但主要面向本地消费，不是面向跨进程的事件流设计。 | ⭐⭐<br>异步生成器产出Message对象，缺少结构化的事件类型体系。 | ⭐⭐<br>有事件hook机制，但事件类型和粒度都比较有限。 |
| **原则五：错误优先作为数据**<br>工具错误和LLM可处理的失败应该作为Error-as-Data返回给模型，只有模型无法处理的系统级故障才打断执行流。 | ⭐⭐⭐⭐⭐<br>`handle_tool_errors=True`默认开启，error-as-data和raise-exception两种模式可配置，错误节点可被LLM"看见"并修复。 | ⭐⭐⭐⭐<br>工具错误作为Function output返回LLM，Run标记failed但不自动中断，模型可以看到错误内容。 | ⭐⭐⭐<br>以Python Exception为主，Guardrail可拦截，但不是系统化的Error-as-Data设计范式。 | ⭐⭐⭐<br>异常可转为错误消息传给GroupChat，但没有形成统一的Error-as-Data哲学。 | ⭐⭐<br>Hook可通知错误，但主要是传统异常处理模式，错误不作为一等数据回流给模型。 |
| **原则六：控制面与数据面分离**<br>权限/Guardrail/预算/审批是控制面；状态/事件/Trace/Artifact是数据面。控制面决定"能不能做"，数据面决定"做了什么"。 | ⭐⭐⭐⭐<br>`interrupt()`+Checkpoint实现审批流；控制面需要结合LangSmith或自建Harness；权限/Guardrail是Harness层能力而非框架核心。 | ⭐⭐⭐<br>服务端内置部分控制面（metadata/tool_choice），但Guardrail和人类审批机制有限，灵活性不足。 | ⭐⭐⭐⭐<br>Guardrails是显式的Runtime一等能力：InputGuardrail/OutputGuardrail/HandoffGuardrail三层防护。 | ⭐⭐<br>控制面能力弱，主要靠代码逻辑硬编码控制，缺少统一的控制面抽象。 | ⭐⭐⭐⭐<br>permissions模式和hooks是框架核心设计特性，控制面做得较好。 |
| **原则七：工具协议与Runtime解耦**<br>工具定义/发现/调用应该独立于具体的Runtime Loop承载方式，一个工具应该能被图式/代码式/托管式Runtime复用（如MCP的价值）。 | ⭐⭐⭐⭐<br>`@tool`装饰器+`bind_tools()`，支持MCP适配，ToolNode可独立复用；历史上与LangChain Tool绑定较深是主要扣分项。 | ⭐⭐⭐<br>Function Calling格式是模型绑定的，不是Runtime解耦设计；不支持MCP，工具只能在OpenAI生态内复用。 | ⭐⭐<br>`@function_tool`是SDK特定wrapper，切换框架需要重写所有工具定义。 | ⭐⭐<br>FunctionTool是AutoGen特定格式，与框架绑定紧密。 | ⭐⭐⭐<br>Tool定义相对独立，但不支持MCP，是Claude生态绑定的，跨框架复用性差。 |
| **原则八：并发语义必须显式定义**<br>同一个Thread上多个Run如何处理？排队？拒绝？取消？分叉？乐观并发？Protocol必须明确写进Run创建语义，不能留给实现自行决定。 | ⭐⭐⭐⭐<br>通过Checkpointer和Thread并发配置可实现多种策略；Send API支持fan-out/fan-in并行，并发语义有文档定义。 | ⭐⭐<br>同一Thread上同时只能有一个in_progress Run（隐式拒绝策略），没有提供排队/分叉/乐观并发等其他选项。 | ⭐<br>完全没有内置并发语义，多Run并发行为未定义。 | ⭐⭐⭐<br>GroupChat支持并行发言，但这是Agent间并发而非同一Thread上的Run并发，语义不清晰。 | ⭐<br>没有并发考虑，完全不支持多Run并发场景。 |
| **原则九：可观测性从Day 1开始**<br>Trace ID/Run ID/Step ID应该贯穿所有Event/Log和Artifact。没有可观测性的Protocol，出问题就是黑盒。 | ⭐⭐⭐⭐⭐<br>LangSmith是一等公民集成：Trace树、Span嵌套、Token统计、运行时回放、与Checkpoint深度集成可回溯。 | ⭐⭐⭐<br>Run Steps提供有限可见性，但Trace不透明，无法看到LLM内部决策链，也无法自定义埋点。 | ⭐⭐⭐<br>SDK Traces功能存在，但能力有限，没有配套的完整Trace平台支持。 | ⭐⭐<br>以Console日志输出为主，缺少结构化Trace体系，Span概念薄弱。 | ⭐<br>基本没有可观测性能力，出问题后难以调试。 |
| **总分（满分45）** | **42/45** | **31/45** | **24/45** | **20/45** | **19/45** |

---

## 关键发现与分析

### 🏆 LangGraph：唯一生产级选择（42/45）

LangGraph是目前唯一一个在九条Protocol设计原则上都做到良好及以上遵循的框架。它的核心优势集中在**生产级可靠性**相关维度：

- **Checkpoint恢复契约（⭐⭐⭐⭐⭐）**：这是LangGraph与其他框架最本质的区别——它真正实现了"从任意点继续执行"，而不只是保存聊天记录。
- **可观测性（⭐⭐⭐⭐⭐）**：LangSmith与框架深度集成，Trace/Checkpoint/回放形成完整的调试闭环。
- **Error-as-Data（⭐⭐⭐⭐⭐）**：错误默认作为数据回流给模型，这是长时运行任务不崩溃的关键。

**扣分项分析**：
- 原则六（控制面分离）扣1星：Guardrail和权限控制不是LangGraph核心，需要结合Deep Agents等Harness层补齐
- 原则七（工具解耦）扣1星：历史包袱导致与LangChain Tool生态有绑定，MCP适配是后补的

### ☁️ OpenAI Assistants API：托管方案的取舍（31/45）

托管方案的优势和劣势都非常明显：
- **优势**：对象建模（原则一）和Run边界（原则二）拿到满分，REST API天然要求先定义资源模型再设计接口，这是托管服务的架构优势。
- **劣势**：Checkpoint（⭐⭐）、并发（⭐⭐）、可观测性（⭐⭐⭐）三个维度受限于托管模式——你得到零运维，但也失去了对状态、并发策略和内部Trace的控制权。

**适用场景**：不需要复杂状态机、不需要崩溃恢复、对可观测性要求不高的简单短任务场景（如客服Bot、简单问答）。

### 🔧 代码式SDK三杰：原型快速，生产需补全

OpenAI Agents SDK（24）、AutoGen（20）、Claude SDK（19）这三个代码式Runtime有共同的短板：
1. **Checkpoint恢复（⭐）**：三个框架都没有真正的持久化Checkpoint，进程崩溃意味着任务丢失
2. **Run边界模糊（⭐⭐）**：执行单元隐式存在，没有贯穿全链路的Run ID追踪
3. **可观测性薄弱（⭐-⭐⭐⭐）**：出问题后调试困难，缺少生产级Trace能力

它们的定位是**快速原型和简单任务**：
- **Agents SDK**：Guardrail设计最好（原则六⭐⭐⭐⭐），适合需要输入输出校验的OpenAI生态应用
- **AutoGen**：多Agent并行能力相对较强（原则八⭐⭐⭐），适合10+Agent的大规模协作实验
- **Claude SDK**：permissions/hooks控制面设计优雅（原则六⭐⭐⭐⭐），适合Claude生态的简单应用

---

## 实践启示

### 选型决策矩阵

根据你的场景需求，按以下维度选择框架：

| 场景需求 | 推荐框架 | 原因 |
|---------|---------|------|
| 快速原型/Demo验证 | Agents SDK / Claude SDK | 上手快，API简洁，不需要考虑持久化 |
| 简单客服Bot/短任务 | OpenAI Assistants | 零运维，托管省事，不需要复杂状态 |
| 10+Agent大规模协作实验 | AutoGen | 事件驱动模型适合多Agent并发场景 |
| 复杂工作流/审批流/长时任务 | LangGraph | 唯一支持Checkpoint回滚、崩溃恢复、HITL的生产级选择 |
| 需要跨平台工具复用 | LangGraph + MCP | 目前MCP支持最好的组合 |
| 需要完整可观测性调试 | LangGraph + LangSmith | Trace/回放/Checkpoint深度集成 |

### 使用本评估表的三个用途

1. **评估新框架**：当新的Agent框架出现时，用这九条原则快速打分，可以在30分钟内判断它的成熟度和定位，避免被营销文案误导。

2. **自建Runtime检查清单**：如果你决定自己实现Agent Runtime，这九条原则就是你的需求清单——每一条原则后面都是一个必须解决的工程问题。

3. **识别生产缺口**：如果你已经选择了某个框架，可以通过对比表快速发现哪些维度需要自行补齐。例如使用Claude SDK做生产应用时，你需要自己实现：Checkpoint持久化、显式Run ID追踪、结构化Trace体系、Error-as-Data错误处理。

### 核心理念回顾

这个对比再次验证了原文的核心观点：**用哪个框架不重要，理解Protocol设计原则才重要**。框架是会更迭的Runtime实现，而九条设计原则背后是Agent系统的本质问题——状态边界、执行契约、恢复语义、可观测性——这些问题不会因为新框架出现而消失。

理解了这九条原则，你就拥有了一个"框架不可知论"的判断标准：无论未来出现什么新框架，你都能快速看穿它的能力边界，做出适合场景的技术选型。

---

## 相关章节

- 上一章：[08 Protocol对象映射与设计原则](08-protocol-design-principles.md) — 九条设计原则的原始定义
- 延伸阅读：[10 企业级选型指南](10-enterprise-selection-guide.md) — 基于九条原则的企业级扩展评估与分层选型架构
- 下一章：[11 跨维度分析](09-cross-dimensional-analysis.md) — 设计决策持久性判断与行业趋势
- 返回：[00 总览](00-overview.md)
