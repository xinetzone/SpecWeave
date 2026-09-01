---
id: "sg-guide-03"
title: "03 日志示例与格式规范"
source: "rules/stage-guardrails-guide.md#03"
x-toml-ref: "../../../.meta/toml/.agents/rules/stage-guardrails-guide/03-logging-examples.toml"
---

# 03 日志示例与格式规范


### 1. 正常放行（BOUNDARY_PASS）

```
[SG-LOG] | level=DEBUG | event=BOUNDARY_PASS | stage=S4 | role=developer | session=task-001 | msg=操作通过边界检查：执行write_code | ctx={"operation":"write_code"}
```

### 2. 越界拦截（INTERCEPT）

```
[SG-LOG] | level=WARN | event=INTERCEPT | stage=S1 | role=orchestrator | session=task-001 | msg=阶段守卫拦截: 直接开始编写登录模块代码（编写代码属于S4代码实现阶段职责） | ctx={"current_stage":"S1","violating_operation":"write_code","target_stage":"S4","violation_type":"STAGE_BOUNDARY_VIOLATION","detail":"直接开始编写登录模块代码（编写代码属于S4代码实现阶段职责）","session":"task-001"}
```

用户看到的拦截消息：
```
⚠️ 阶段守卫拦截：当前为【S1需求接收】阶段，【直接开始编写登录模块代码（编写代码属于S4代码实现阶段职责）】。
请先完成当前阶段：明确功能边界与验收标准，输出任务分解清单
如需跳至S4（代码实现）阶段，请提交正向跳过申请并经orchestrator批准。
```

### 3. 阶段进入（STAGE_ENTER）

```
[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S4 | role=developer | session=task-001 | msg=进入代码实现阶段 | ctx={"prev_stage":"S3","via_jump":false}
```

### 4. 阶段退出（STAGE_EXIT）

```
[SG-LOG] | level=INFO | event=STAGE_EXIT | stage=S1 | role=orchestrator | session=task-001 | msg=需求澄清完成 | ctx={"exit_criteria_met":["需求已澄清","任务已分解"],"output_artifacts":["需求文档","任务清单"],"next_stage":"S2","duration":120.5}
```

### 5. 跳转申请（JUMP_REQUEST）

```
[SG-LOG] | level=INFO | event=JUMP_REQUEST | stage=S1 | role=orchestrator | session=task-001 | msg=申请skip跳转: S1→S4 | ctx={"jump_id":"jump-task-001-1","jump_type":"skip","from_stage":"S1","to_stage":"S4","reason":"简单bug修复，跳过设计阶段"}
```

### 6. 跳转批准（JUMP_APPROVED）

```
[SG-LOG] | level=INFO | event=JUMP_APPROVED | stage=S1 | role=orchestrator | session=task-001 | msg=跳转已批准: S1→S4（skip） | ctx={"jump_id":"jump-task-001-1","jump_type":"skip","approved_by":"orchestrator","conditions":"确保补充单元测试"}
```

### 7. 回退自动进入目标阶段

```
[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S2 | role=architect | session=task-001 | msg=通过逆向回退进入S2 | ctx={"jump_id":"jump-task-001-2","via_jump":true}
```

### 8. 绕过检测（BYPASS_DETECTED）

```
[SG-LOG] | level=ERROR | event=BYPASS_DETECTED | stage=S1 | role=orchestrator | session=task-001 | msg=检测到疑似绕过阶段守卫行为：疑似通过替代操作绕过拦截: write_code -> modify_business_code | ctx={"operation":"modify_business_code","detection_reason":"疑似通过替代操作绕过拦截: write_code -> modify_business_code","evidence":"原操作write_code被拦截，改用modify_business_code执行同类行为"}
```

### 9. 错误事件（ERROR）

```
[SG-LOG] | level=ERROR | event=ERROR | stage=S1 | role=orchestrator | session=task-001 | msg=阶段转换错误: DUPLICATE_ENTRY - 重复进入阶段S1（S1已处于活跃状态） | ctx={"error_type":"DUPLICATE_ENTRY","error_detail":"重复进入阶段S1（S1已处于活跃状态）","impact":"可能导致阶段状态混乱，跳过必要的退出标准检查","recovery_hint":"先退出当前阶段或提交JUMP_REQUEST获得审批"}
```

### 10. 前置文档检查（DOC_CHECK + PDR_CONFIRM）

```
[SG-LOG] | level=INFO | event=DOC_CHECK | stage=S1 | role=orchestrator | session=task-001 | msg=前置文档检查完成：共3份必读文档 | ctx={"required_docs":["AGENTS.md","stage-guardrails.md","development-standards.md"]}
[SG-LOG] | level=INFO | event=PDR_CONFIRM | stage=S1 | role=orchestrator | session=task-001 | msg=前置文档读取流程完成
```

```
[SG-LOG] | level=<LEVEL> | event=<EVENT> | stage=<STAGE> | role=<ROLE> | session=<SID> | msg=<MSG> [| ctx=<JSON>]
```

| 字段 | 说明 | 取值 |
|------|------|------|
| level | 日志级别 | `DEBUG`（检查/放行）、`INFO`（正常流转）、`WARN`（拦截）、`ERROR`（绕过/异常） |
| event | 事件类型 | STAGE_ENTER/STAGE_EXIT/DOC_CHECK/PDR_CONFIRM/BOUNDARY_CHECK/BOUNDARY_PASS/INTERCEPT/BYPASS_DETECTED/JUMP_REQUEST/JUMP_APPROVED/JUMP_REJECTED/ERROR |
| stage | 当前阶段 | S1~S8 或 NONE（无活跃阶段） |
| role | 执行角色 | orchestrator/architect/developer/tester/reviewer |
| session | 会话ID | 用于关联同一任务的所有日志 |
| msg | 人类可读消息 | UTF-8中文描述 |
| ctx | 可选JSON上下文 | 事件相关的结构化数据 |

---

## 相关模式

- [三层检查工具模式](../../../docs/retrospective/patterns/code-patterns/three-tier-check-tool.md)
- [双通道分级日志](../../../docs/retrospective/patterns/code-patterns/dual-channel-tiered-logging.md)
---

← 上一章: [02 8阶段权限速查表](02-permissions-reference.md) | **[返回索引](../stage-guardrails-guide.md)** | 下一章: [04 常见拦截原因与解决方案](04-common-interceptions.md) →
