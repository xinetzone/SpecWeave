# 开发流程阶段守卫规则

本规则定义功能开发流程的标准阶段序列、每个阶段的操作边界、跨阶段拦截机制与阶段跳转审批流程。所有智能体在执行开发任务时必须遵守本规则，确保在正确的阶段做正确的事。

## 核心原则

> 在需求阶段聊代码，是空中楼阁；在编码阶段改架构，是推倒重来。
> 阶段守卫的本质不是限制自由，而是防止"越做越偏"——每一步的输出是下一步的输入，跨阶段操作等于在流沙上盖楼。

---

## 标准阶段序列

功能开发遵循以下8个标准阶段，顺序不可跳过：

```mermaid
flowchart LR
    S1["①需求接收<br/>orchestrator"] --> S2["②方案设计<br/>architect"]
    S2 --> S3["③任务分配<br/>orchestrator"]
    S3 --> S4["④代码实现<br/>developer"]
    S4 --> S5["⑤测试编写<br/>tester"]
    S5 --> S6["⑥代码审查<br/>reviewer"]
    S6 -->|"通过"| S7["⑦合并代码<br/>orchestrator"]
    S6 -->|"不通过"| S4
    S7 --> S8["⑧完成确认<br/>orchestrator"]
    style S1 fill:#e8f4f8,stroke:#2980b9
    style S2 fill:#e8f4f8,stroke:#2980b9
    style S3 fill:#e8f4f8,stroke:#2980b9
    style S4 fill:#d5f5e3,stroke:#27ae60
    style S5 fill:#fdebd0,stroke:#f39c12
    style S6 fill:#fadbd8,stroke:#e74c3c
    style S7 fill:#d5f5e3,stroke:#27ae60
    style S8 fill:#d5f5e3,stroke:#27ae60
```

### 阶段概览表

| 阶段 | 负责角色 | 核心目标 | 进入条件 | 退出标准 |
|------|---------|---------|---------|---------|
| ①需求接收 | orchestrator | 明确需求边界与验收标准 | 收到用户/产品方需求描述 | 任务分解清单已创建并分配 |
| ②方案设计 | architect | 产出可执行的技术方案 | 收到任务分解清单 | 技术方案经orchestrator确认 |
| ③任务分配 | orchestrator | 匹配角色、明确交付要求 | 技术方案已确认 | 任务分配通知已发送至各角色 |
| ④代码实现 | developer | 按方案完成编码与单元测试 | 收到任务分配+技术方案 | PR已创建，本地测试通过 |
| ⑤测试编写 | tester | 验证功能正确性、发现缺陷 | 代码已提交PR | 测试报告已生成，缺陷已记录 |
| ⑥代码审查 | reviewer | 质量把关、改进建议 | 收到代码实现与测试报告 | 审查报告已输出，合并决策明确 |
| ⑦合并代码 | orchestrator | 合入主干、触发CI | 审查通过，无阻塞问题 | CI流程通过，代码已合并 |
| ⑧完成确认 | orchestrator | 验收确认、关闭任务 | 合并结果+测试报告 | 任务状态已更新，相关方已通知 |

---

## 各阶段操作边界

### ① 需求接收阶段（orchestrator）

**允许操作**：
- 解析需求文档，提取功能描述与验收标准
- 询问用户/产品方澄清需求边界（功能做什么、不做什么）
- 将需求拆分为可独立执行的子任务
- 评估任务优先级与依赖关系
- 识别需求中的风险点和模糊点

**禁止操作**：
- ❌ 讨论具体技术实现方案（如"用Redis还是Memcached"）
- ❌ 指定技术选型或框架
- ❌ 编写任何代码或伪代码
- ❌ 估算代码行数或技术细节
- ❌ 跳过需求澄清直接进入设计

**正例**：
> "这个功能的目标用户是谁？验收标准中'快速响应'具体指多少秒以内？"

**反例**：
> "这个功能我打算用React+Node.js+MongoDB来做，API用RESTful，先写个用户登录接口……"

---

### ② 方案设计阶段（architect）

**允许操作**：
- 分析任务的技术可行性
- 进行架构设计与模块划分
- 完成技术选型与接口定义（API签名、数据模型）
- 识别技术风险并给出应对策略
- 评估影响范围（哪些现有模块会受影响）

**禁止操作**：
- ❌ 编写业务逻辑代码
- ❌ 直接修改已有代码文件
- ❌ 跳过风险评估直接给出"理想方案"
- ❌ 在需求未澄清的情况下强行出方案
- ❌ 指定具体实现细节（如变量名、函数内部逻辑）

**正例**：
> "用户模块采用分层架构：Controller→Service→Repository，接口定义如下……缓存策略建议用Redis，过期时间30分钟。"

**反例**：
> "我直接把代码写出来给你看吧：function login(username, password) { const user = db.query(...)……"

---

### ③ 任务分配阶段（orchestrator）

**允许操作**：
- 依据技术方案调整任务分解
- 按角色能力匹配任务
- 明确任务交付时间与验收标准
- 确定任务优先级与执行顺序

**禁止操作**：
- ❌ 修改技术方案的核心内容（架构、选型、接口定义）
- ❌ 直接开始编码
- ❌ 跳过architect确认自行决定技术方案
- ❌ 分配超出角色能力边界的任务（如让tester写业务代码）

**正例**：
> "根据方案，将任务拆为3个：用户认证（developer-A）、权限验证（developer-B）、集成测试（tester）。每个任务的验收标准见方案文档第3节。"

**反例**：
> "这个方案我觉得用GraphQL更好，我直接改了方案然后让developer按新方案做。"

---

### ④ 代码实现阶段（developer）

**允许操作**：
- 依据技术方案进行编码实现
- 编写单元测试并保证本地通过
- 遵循项目编码规范与代码风格
- 在方案范围内选择具体实现方式（变量名、函数内部逻辑等）
- 提交代码并发起Pull Request

**禁止操作**：
- ❌ 擅自变更架构决策（如把分层架构改成单体直接调用）
- ❌ 擅自更换技术选型（如方案用PostgreSQL，私改用MongoDB）
- ❌ 跳过单元测试直接提交
- ❌ 在未读取技术方案文档的情况下开始编码
- ❌ 实现方案中未包含的功能（"顺手"加了功能）

**正例**：
> "📋 前置文档确认：已读取技术方案文档、任务分解清单、开发规范。按照方案的分层架构实现，单元测试覆盖核心路径。"

**反例**：
> "方案写的用Repository模式太麻烦了，我直接在Controller里查数据库，简单直接。顺便加了个导出Excel功能，用户没提但肯定需要。"

---

### ⑤ 测试编写阶段（tester）

**允许操作**：
- 依据需求与技术方案设计测试用例
- 编写自动化测试代码（单元测试、集成测试、E2E测试）
- 执行测试并记录结果
- 发现缺陷时反馈至developer
- 验证修复后的缺陷是否解决

**禁止操作**：
- ❌ 自行修复发现的缺陷（必须反馈给developer）
- ❌ 修改业务逻辑代码
- ❌ 在未读取需求和技术方案的情况下设计测试用例
- ❌ 跳过缺陷记录直接标记测试通过
- ❌ 仅测试"happy path"忽略边界条件和异常情况

**正例**：
> "发现3个缺陷：①登录失败时返回500而非401 ②空密码未校验 ③并发登录未处理。已记录至缺陷清单，反馈developer修复。"

**反例**：
> "测试发现登录报错，我直接改了auth.js里的判断逻辑，现在正常了。"

---

### ⑥ 代码审查阶段（reviewer）

**允许操作**：
- 审查代码规范、功能正确性、测试覆盖
- 检查安全性与性能指标
- 给出审查意见与改进建议
- 审查通过则批准合并，否则退回developer修改

**禁止操作**：
- ❌ 直接修改业务代码
- ❌ 在未读取前置文档的情况下给出审查结论
- ❌ 基于个人偏好而非规范要求提出修改意见
- ❌ 跳过安全检查和性能检查
- ❌ 不给出具体改进建议直接打回

**正例**：
> "📋 前置文档确认：已读取需求文档、技术方案、代码实现、测试报告。审查发现：①第45行SQL注入风险，建议使用参数化查询 ②单元测试缺少异常分支覆盖，请补充。"

**反例**：
> "这代码写得不好，重写。"（无具体原因，无改进建议）

---

### ⑦ 合并代码阶段（orchestrator）

**允许操作**：
- 确认审查通过且无阻塞问题
- 确认CI流程全部通过
- 执行代码合并至主干分支
- 触发持续集成与部署流程

**禁止操作**：
- ❌ 在审查未通过时强行合并
- ❌ 跳过CI检查直接合并
- ❌ 合并后不通知相关角色
- ❌ 忽略冲突警告强制合并

---

### ⑧ 完成确认阶段（orchestrator）

**允许操作**：
- 核对验收标准是否全部满足
- 更新任务状态为已完成
- 通知相关角色任务结束
- 归档项目文档

**禁止操作**：
- ❌ 在验收标准未全部满足时标记完成
- ❌ 跳过回归验证直接关闭任务
- ❌ 不通知相关方单方面关闭任务

---

## 跨阶段拦截机制

当智能体在某个阶段尝试执行其他阶段的操作时，必须**显式拦截**，不得执行越界操作。

### 拦截输出格式

拦截时必须使用以下标准格式输出：

```
⚠️ 阶段守卫拦截：当前为【X阶段】，【Y操作】属于【Z阶段】的职责。
请先完成当前阶段：[当前阶段的退出标准]
如需跳过或回退阶段，请参考"阶段跳转审批流程"。
```

### 拦截行为规范

1. **立即停止**：检测到跨阶段操作后，立即停止当前越界操作的执行
2. **明确告知**：清晰说明当前阶段、越界操作、正确阶段
3. **给出出路**：提示当前阶段的退出标准，或跳转审批流程
4. **不替用户决策**：不得自行判断"这个越界没关系"而放行
5. **记录拦截**：拦截事件应在交接文档或任务状态中记录

### 拦截示例

**场景**：在需求讨论中，用户说"这个用Redis做缓存吧"，developer角色的AI直接开始写Redis配置代码。

**正确拦截输出**：
```
⚠️ 阶段守卫拦截：当前为【①需求接收】阶段，【编写Redis配置代码】属于【④代码实现】阶段的职责。
请先完成当前阶段：明确功能边界与验收标准，输出任务分解清单。
如需在需求阶段讨论技术可行性，可转由architect进行技术预研，但不得直接编写代码。
```

---

## 阶段跳转审批流程

正常情况下阶段必须按顺序执行。因特殊原因需要跳过阶段或逆向回退时，必须经过审批。

```mermaid
flowchart TD
    A{"需要跳过或回退阶段?"} --> B{"跳转类型"}
    B -->|"正向跳过"| C["orchestrator评估必要性"]
    B -->|"逆向回退"| D["orchestrator + reviewer联合评估"]
    C --> E{"理由是否充分?"}
    D --> F{"回退范围确认"}
    E -->|"是"| G["orchestrator批准并记录原因"]
    E -->|"否"| H["拒绝跳转,返回当前阶段"]
    F --> G
    G --> I["在交接文档中注明跳转原因和审批人"]
    I --> J["执行跳转"]
    H --> K["继续当前阶段"]
```

### 正向跳过

**定义**：跳过某个尚未执行的阶段，直接进入后续阶段。

**适用场景示例**：
- 功能极其简单（如修改一个文案），可以跳过方案设计阶段
- Bug修复且影响范围极小，可以跳过任务分配阶段

**审批要求**：
- 必须由orchestrator明确批准
- 跳过原因必须记录在交接文档中
- 跳过方案设计时，developer必须自行确认影响范围

### 逆向回退

**定义**：从当前阶段返回到之前的阶段（如从代码实现回到方案设计）。

**适用场景示例**：
- 编码过程中发现技术方案有重大缺陷，需要重新设计
- 测试过程中发现需求理解有误，需要重新澄清需求
- 审查过程中发现架构性问题，需要回到方案阶段

**审批要求**：
- 必须由orchestrator批准
- **必须由reviewer确认回退范围**（哪些已完成的工作需要作废/修改）
- 回退原因必须记录
- 如果涉及代码回退，必须包含回滚策略
- 回退后重新推进时，所有经过的阶段必须重新执行（不能跳过）

### 禁止跳转场景

以下情况不得跳转：
- 任何阶段跳至完成确认（不得跳过验证直接标记完成）
- 代码审查不通过时跳过修复直接合并（必须退回developer修复）
- 测试发现严重缺陷时跳过修复直接进入审查
- 未经审批自行决定跳过阶段

---

## 关键节点日志输出规范

为便于排查阶段守卫执行过程中的潜在问题（误拦截、漏拦截、审批缺失、上下文断裂等），所有智能体在执行阶段守卫相关操作时必须输出结构化日志。

### 日志级别定义

| 级别 | 标识 | 使用场景 | 示例 |
|------|------|---------|------|
| `DEBUG` | 🔍 | 细粒度调试信息，用于排查具体问题 | 文档内容匹配详情、条件判断分支 |
| `INFO` | ℹ️ | 正常流程节点事件 | 阶段进入/退出、文档读取完成、审批通过 |
| `WARN` | ⚠️ | 异常但可恢复的情况，需关注 | 拦截事件、文档缺失但已标注风险、条件满足度不足 |
| `ERROR` | ❌ | 严重错误，必须人工介入 | 未经审批的阶段跳转、关键前置文档缺失且无法获取、越界操作已执行 |

### 关键事件节点

以下8类关键事件必须输出日志：

```mermaid
flowchart LR
    E1["①阶段进入"] --> E2["②前置文档检查"]
    E2 --> E3["③操作边界校验"]
    E3 --> E4["④跨阶段拦截"]
    E4 --> E5["⑤阶段跳转申请"]
    E5 --> E6["⑥阶段跳转审批"]
    E6 --> E7["⑦阶段退出"]
    E7 --> E8["⑧异常与错误"]
    style E1 fill:#d5f5e3,stroke:#27ae60
    style E4 fill:#fadbd8,stroke:#e74c3c
    style E5 fill:#fdebd0,stroke:#f39c12
    style E6 fill:#fdebd0,stroke:#f39c12
    style E8 fill:#fadbd8,stroke:#e74c3c
```

### 结构化日志格式

每条日志必须包含以下字段，以`|`分隔的键值对格式输出，便于机器解析：

```
[SG-LOG] | level=<LEVEL> | event=<EVENT_TYPE> | stage=<STAGE_ID> | role=<ROLE> | session=<SESSION_ID> | msg=<MESSAGE> | ctx=<CONTEXT_JSON>
```

**字段说明**：

| 字段 | 必填 | 说明 |
|------|-----|------|
| `level` | ✅ | 日志级别：DEBUG/INFO/WARN/ERROR |
| `event` | ✅ | 事件类型（见下文事件类型枚举） |
| `stage` | ✅ | 当前阶段ID：S1~S8，如 `S4`（代码实现） |
| `role` | ✅ | 执行角色：orchestrator/architect/developer/tester/reviewer |
| `session` | ✅ | 会话标识：使用当前会话/任务ID |
| `msg` | ✅ | 人类可读的日志消息 |
| `ctx` | ❌ | 附加上下文JSON（目标阶段、缺失文档、审批人等），无额外上下文时省略 |

**事件类型枚举**：

| event值 | 对应节点 | 触发时机 |
|---------|---------|---------|
| `STAGE_ENTER` | ①阶段进入 | 智能体开始执行新阶段任务时 |
| `DOC_CHECK` | ②前置文档检查 | 检查前置文档是否已读取时 |
| `DOC_READ` | ②前置文档检查 | 实际读取每份前置文档后 |
| `DOC_MISSING` | ②前置文档检查 | 发现前置文档缺失时 |
| `BOUNDARY_CHECK` | ③操作边界校验 | 执行操作合法性校验时 |
| `BOUNDARY_PASS` | ③操作边界校验 | 操作通过边界检查时 |
| `INTERCEPT` | ④跨阶段拦截 | 检测到跨阶段操作并拦截时 |
| `BYPASS_DETECTED` | ④跨阶段拦截 | 检测到疑似绕过拦截的行为时 |
| `JUMP_REQUEST` | ⑤阶段跳转申请 | 角色提出阶段跳转请求时 |
| `JUMP_APPROVED` | ⑥阶段跳转审批 | 跳转获得批准时 |
| `JUMP_REJECTED` | ⑥阶段跳转审批 | 跳转被拒绝时 |
| `STAGE_EXIT` | ⑦阶段退出 | 阶段完成准备进入下一阶段时 |
| `ERROR` | ⑧异常与错误 | 发生严重错误时 |

### 各节点日志输出模板

#### ① 阶段进入（STAGE_ENTER）

```
[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=<阶段ID> | role=<角色> | session=<会话ID> | msg=进入<阶段名称>阶段，开始执行<核心目标> | ctx={"entry_condition":"<进入条件满足情况>","prev_stage":"<上一阶段ID或null>"}
```

**示例**：
```
[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S4 | role=developer | session=task-20260629-auth | msg=进入代码实现阶段，开始按方案完成编码与单元测试 | ctx={"entry_condition":"任务分配通知已收到,技术方案已确认","prev_stage":"S3"}
```

#### ② 前置文档检查（DOC_CHECK / DOC_READ / DOC_MISSING）

```
[SG-LOG] | level=INFO | event=DOC_CHECK | stage=<阶段ID> | role=<角色> | session=<会话ID> | msg=开始前置文档检查，共<N>份必读文档 | ctx={"required_docs":["<doc1>","<doc2>"]}

[SG-LOG] | level=INFO | event=DOC_READ | stage=<阶段ID> | role=<角色> | session=<会话ID> | msg=已读取前置文档: <文档路径> | ctx={"doc_path":"<路径>","doc_summary":"<文档要点摘要>"}

[SG-LOG] | level=WARN | event=DOC_MISSING | stage=<阶段ID> | role=<角色> | session=<会话ID> | msg=前置文档缺失: <文档路径或描述> | ctx={"missing_doc":"<缺失文档>","risk":"<风险描述>","action":"<已采取的处理措施>"}
```

**示例**：
```
[SG-LOG] | level=INFO | event=DOC_CHECK | stage=S4 | role=developer | session=task-20260629-auth | msg=开始前置文档检查，共4份必读文档 | ctx={"required_docs":["技术方案文档","任务分解清单","docs/development-standards.md","相关模块现有代码"]}
[SG-LOG] | level=INFO | event=DOC_READ | stage=S4 | role=developer | session=task-20260629-auth | msg=已读取前置文档: docs/development-standards.md | ctx={"doc_path":"docs/development-standards.md","doc_summary":"代码风格:Conventional Commits,测试覆盖率>=80%"}
[SG-LOG] | level=WARN | event=DOC_MISSING | stage=S4 | role=developer | session=task-20260629-auth | msg=前置文档缺失: 相关模块现有代码auth.py | ctx={"missing_doc":"src/auth.py","risk":"可能不了解现有认证逻辑导致实现不一致","action":"正在请求获取文件路径,标注风险后继续"}
```

#### ③ 操作边界校验（BOUNDARY_CHECK / BOUNDARY_PASS）

```
[SG-LOG] | level=DEBUG | event=BOUNDARY_CHECK | stage=<阶段ID> | role=<角色> | session=<会话ID> | msg=校验操作合法性: <操作描述> | ctx={"operation":"<操作>","allowed_ops":["<该阶段允许操作列表>"]}

[SG-LOG] | level=DEBUG | event=BOUNDARY_PASS | stage=<阶段ID> | role=<角色> | session=<会话ID> | msg=操作通过边界检查: <操作描述> | ctx={"operation":"<操作>"}
```

**示例**：
```
[SG-LOG] | level=DEBUG | event=BOUNDARY_CHECK | stage=S2 | role=architect | session=task-20260629-auth | msg=校验操作合法性: 设计用户认证模块分层架构 | ctx={"operation":"架构设计","allowed_ops":["技术可行性分析","架构设计","技术选型","接口定义","风险评估"]}
[SG-LOG] | level=DEBUG | event=BOUNDARY_PASS | stage=S2 | role=architect | session=task-20260629-auth | msg=操作通过边界检查: 设计用户认证模块分层架构 | ctx={"operation":"架构设计"}
```

#### ④ 跨阶段拦截（INTERCEPT / BYPASS_DETECTED）

```
[SG-LOG] | level=WARN | event=INTERCEPT | stage=<当前阶段ID> | role=<执行角色> | session=<会话ID> | msg=阶段守卫拦截: <违规操作>属于<目标阶段>职责 | ctx={"current_stage":"<当前阶段>","violating_operation":"<违规操作>","target_stage":"<目标阶段>","exit_criteria":"<当前阶段退出标准>"}

[SG-LOG] | level=ERROR | event=BYPASS_DETECTED | stage=<阶段ID> | role=<角色> | session=<会话ID> | msg=疑似绕过阶段守卫: <描述> | ctx={"detection_reason":"<检测原因>","evidence":"<证据摘要>"}
```

**示例**：
```
[SG-LOG] | level=WARN | event=INTERCEPT | stage=S1 | role=developer | session=task-20260629-auth | msg=阶段守卫拦截: 编写Redis配置代码属于S4代码实现阶段职责 | ctx={"current_stage":"S1","violating_operation":"编写Redis配置代码","target_stage":"S4","exit_criteria":"明确功能边界与验收标准,输出任务分解清单"}
```

#### ⑤⑥ 阶段跳转申请与审批（JUMP_REQUEST / JUMP_APPROVED / JUMP_REJECTED）

```
[SG-LOG] | level=INFO | event=JUMP_REQUEST | stage=<当前阶段ID> | role=<申请角色> | session=<会话ID> | msg=申请阶段跳转: <跳转描述> | ctx={"jump_type":"<skip/rollback>","from_stage":"<起始阶段>","to_stage":"<目标阶段>","reason":"<跳转理由>","requested_by":"<申请人>"}

[SG-LOG] | level=INFO | event=JUMP_APPROVED | stage=<当前阶段ID> | role=<审批角色> | session=<会话ID> | msg=阶段跳转已批准: <跳转描述> | ctx={"jump_type":"<skip/rollback>","approved_by":"<审批人>","rollback_scope":"<回退范围（仅回退时）>","conditions":"<附加条件>"}

[SG-LOG] | level=WARN | event=JUMP_REJECTED | stage=<当前阶段ID> | role=<审批角色> | session=<会话ID> | msg=阶段跳转被拒绝: <跳转描述> | ctx={"jump_type":"<skip/rollback>","rejected_by":"<拒绝人>","reject_reason":"<拒绝理由>"}
```

**示例**：
```
[SG-LOG] | level=INFO | event=JUMP_REQUEST | stage=S2 | role=developer | session=task-20260629-typo | msg=申请阶段跳转: 从S2方案设计正向跳至S4代码实现 | ctx={"jump_type":"skip","from_stage":"S2","to_stage":"S4","reason":"修改文案为极简单点修复,无需独立方案设计","requested_by":"developer"}
[SG-LOG] | level=INFO | event=JUMP_APPROVED | stage=S2 | role=orchestrator | session=task-20260629-typo | msg=阶段跳转已批准: S2→S4跳过方案设计 | ctx={"jump_type":"skip","approved_by":"orchestrator","conditions":"developer自行确认影响范围不超过文案修改"}
[SG-LOG] | level=INFO | event=JUMP_REQUEST | stage=S4 | role=architect | session=task-20260629-auth | msg=申请阶段跳转: 从S4代码实现逆向回退至S2方案设计 | ctx={"jump_type":"rollback","from_stage":"S4","to_stage":"S2","reason":"编码中发现JWT方案不适合微服务架构需重新设计","requested_by":"architect"}
[SG-LOG] | level=INFO | event=JUMP_APPROVED | stage=S4 | role=orchestrator | session=task-20260629-auth | msg=阶段跳转已批准: S4→S2逆向回退 | ctx={"jump_type":"rollback","approved_by":"orchestrator","rollback_scope":"auth.py已实现的50行JWT代码作废,service层接口需重新定义","conditions":"回退后重新推进时S3/S4必须重新执行"}
```

#### ⑦ 阶段退出（STAGE_EXIT）

```
[SG-LOG] | level=INFO | event=STAGE_EXIT | stage=<阶段ID> | role=<角色> | session=<会话ID> | msg=阶段<阶段名称>已完成,退出标准满足 | ctx={"exit_criteria_met":["<满足的退出标准>"],"duration":"<阶段耗时>","output_artifacts":["<产出物清单>"],"next_stage":"<下一阶段ID>"}
```

**示例**：
```
[SG-LOG] | level=INFO | event=STAGE_EXIT | stage=S2 | role=architect | session=task-20260629-auth | msg=阶段方案设计已完成,退出标准满足 | ctx={"exit_criteria_met":["技术方案已完成","风险评估已覆盖","接口定义已明确"],"duration":"15min","output_artifacts":["技术方案文档","接口定义文档","风险评估报告"],"next_stage":"S3"}
```

#### ⑧ 异常与错误（ERROR）

```
[SG-LOG] | level=ERROR | event=ERROR | stage=<阶段ID> | role=<角色> | session=<会话ID> | msg=<错误描述> | ctx={"error_type":"<错误类型>","error_detail":"<错误详情>","impact":"<影响范围>","recovery_hint":"<建议恢复措施>"}
```

**错误类型枚举**：
- `UNAUTHORIZED_JUMP`：未经审批的阶段跳转已发生
- `CRITICAL_DOC_MISSING`：关键前置文档缺失且无法获取
- `VIOLATION_EXECUTED`：越界操作已被执行（拦截失败）
- `INVALID_STATE`：阶段状态不一致（如同时处于多个阶段）
- `APPROVAL_CONFLICT`：审批意见冲突无法仲裁

**示例**：
```
[SG-LOG] | level=ERROR | event=ERROR | stage=S4 | role=developer | session=task-20260629-auth | msg=检测到未经审批的阶段跳转: 代码实现阶段跳过测试直接进入审查 | ctx={"error_type":"UNAUTHORIZED_JUMP","error_detail":"S4→S6跳转无orchestrator批准记录","impact":"代码未经测试可能引入缺陷","recovery_hint":"退回S5测试编写阶段,补充测试用例后重新提交审查"}
```

### 日志输出要求

1. **必须输出**：上述8类关键事件，只要发生就必须输出对应级别的日志，不得省略
2. **即时输出**：日志应在事件发生时立即输出，不得延迟到阶段结束批量输出
3. **信息完整**：必填字段（level/event/stage/role/session/msg）必须全部填写，不得为空
4. **中文消息**：`msg`字段使用中文描述，便于人类阅读；`ctx`中的键名使用英文，便于机器解析
5. **单行输出**：每条日志必须在单行内完成，不得换行（ctx中的JSON必须压缩为单行）
6. **不替代交互**：日志是辅助排查工具，不替代面向用户的正式输出（如拦截警告、审批结果通知）
7. **交接文档联动**：WARN及以上级别的日志事件（INTERCEPT、JUMP_REQUEST/REJECTED、ERROR）必须在任务交接文档中记录

### 自动化检查脚本

可使用 `.agents/scripts/check-stage-guardrails.py` 对开发过程输出的日志进行离线分析，检测以下问题：
- 是否存在未输出STAGE_ENTER直接输出STAGE_EXIT的阶段
- INTERCEPT事件后是否仍继续执行了越界操作
- JUMP_REQUEST是否有对应的JUMP_APPROVED/JUMP_REJECTED
- ERROR类型日志是否有对应的恢复处理记录
- 关键文档缺失（DOC_MISSING）是否标注了风险

检查脚本使用方式：
```bash
python .agents/scripts/check-stage-guardrails.py --log-file <session_log_path> [--json]
```
