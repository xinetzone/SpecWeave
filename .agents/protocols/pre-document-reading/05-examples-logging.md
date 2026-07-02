---
id: "pdr-05"
title: "05 使用示例与PDR-LOG日志规范"
source: "protocols/pre-document-reading.md#05"
x-toml-ref: "../../../.meta/toml/.agents/protocols/pre-document-reading/05-examples-logging.toml"
---

# 05 使用示例与PDR-LOG日志规范


### 完整场景：developer收到任务分配后的读取确认

```
📋 前置文档确认：已读取 [技术方案文档](../../.temp/feature-auth/spec.md)、[任务分解清单](../../.temp/feature-auth/tasks.md)、[开发规范](../../../docs/development-standards.md)、[auth模块现有代码](../../../apps/myapp/src/auth/)

当前为④代码实现阶段，按照方案实现JWT认证中间件：
1. 首先实现token签发功能
2. 然后实现token验证中间件
3. 最后编写单元测试
```

### 完整场景：新会话恢复任务

```
📋 新会话上下文重建：已重新读取 [竹简悟道项目README](../../../apps/zhujian-wudao/README.md)、[技术方案](.temp/zhujian/spec.md)、[任务清单](.temp/zhujian/tasks.md)、[已有代码](../../../apps/zhujian-wudao/src/)

当前进度：④代码实现阶段，对话核心逻辑已完成，待实现竹简渲染模块
待办事项：继续实现竹简渲染模块 → 编写单元测试 → 提交PR
```

---

前置文档读取过程中的关键事件必须输出结构化日志，格式与阶段守卫日志（[SG-LOG]）保持一致，使用`[PDR-LOG]`前缀标识。

### 日志事件类型

| event值 | 级别 | 触发时机 |
|---------|------|---------|
| `PDR_START` | INFO | 开始执行前置文档读取流程 |
| `PDR_DOC_READ` | INFO | 成功读取一份前置文档 |
| `PDR_DOC_SKIP` | DEBUG | 跳过已读取过的文档（新会话恢复场景） |
| `PDR_DOC_MISSING` | WARN | 发现前置文档缺失 |
| `PDR_DOC_REQ_GAP` | WARN | 文档已读取但关键信息缺失（如技术方案中缺少接口定义） |
| `PDR_CONFIRM` | INFO | 输出📋前置文档确认 |
| `PDR_ERROR` | ERROR | 文档读取过程中发生严重错误 |

### 日志格式

```
[PDR-LOG] | level=<LEVEL> | event=<EVENT_TYPE> | stage=<STAGE_ID> | role=<ROLE> | session=<SESSION_ID> | msg=<MESSAGE> | ctx=<CONTEXT_JSON>
```

### 各事件模板与示例

#### PDR_START - 开始读取流程

```
[PDR-LOG] | level=INFO | event=PDR_START | stage=<阶段ID> | role=<角色> | session=<会话ID> | msg=开始前置文档读取,共<N>份文档待读取 | ctx={"required_count":<数量>,"required_docs":["<doc1>"],"resume":<true/false>}
```

示例：
```
[PDR-LOG] | level=INFO | event=PDR_START | stage=S4 | role=developer | session=task-20260629-auth | msg=开始前置文档读取,共4份文档待读取 | ctx={"required_count":4,"required_docs":["技术方案文档","任务分解清单","docs/development-standards.md","相关模块现有代码"],"resume":false}
```

#### PDR_DOC_READ - 文档读取完成

```
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=<阶段ID> | role=<角色> | session=<会话ID> | msg=已读取: <文档标识> | ctx={"doc":"<文档路径或标识>","bytes":<字节数>,"key_points":["<要点1>","<要点2>"]}
```

示例：
```
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S4 | role=developer | session=task-20260629-auth | msg=已读取: docs/development-standards.md | ctx={"doc":"docs/development-standards.md","bytes":8420,"key_points":["Conventional Commits提交规范","测试覆盖率>=80%","禁止硬编码"]}
```

#### PDR_DOC_MISSING - 文档缺失

```
[PDR-LOG] | level=WARN | event=PDR_DOC_MISSING | stage=<阶段ID> | role=<角色> | session=<会话ID> | msg=前置文档缺失: <文档标识> | ctx={"doc":"<缺失文档>","risk":"<风险等级:low/medium/high>","risk_detail":"<风险描述>","action":"<处理措施:request/annotate/abort>"}
```

风险等级说明：
- `low`：文档缺失但不影响核心工作（如参考文档），可标注风险后继续
- `medium`：文档缺失影响部分工作质量（如缺少编码规范），标注风险继续但需后续补充
- `high`：文档缺失导致无法工作（如缺少技术方案），必须请求获取或中止当前阶段

示例：
```
[PDR-LOG] | level=WARN | event=PDR_DOC_MISSING | stage=S4 | role=developer | session=task-20260629-auth | msg=前置文档缺失: src/auth.py（相关模块现有代码） | ctx={"doc":"src/auth.py","risk":"medium","risk_detail":"不了解现有认证逻辑可能导致实现不一致","action":"request"}
```

#### PDR_DOC_REQ_GAP - 文档内容不完整

```
[PDR-LOG] | level=WARN | event=PDR_DOC_REQ_GAP | stage=<阶段ID> | role=<角色> | session=<会话ID> | msg=文档内容不完整: <缺失内容描述> | ctx={"doc":"<文档路径>","missing_sections":["<缺失章节>"],"impact":"<影响描述>"}
```

示例：
```
[PDR-LOG] | level=WARN | event=PDR_DOC_REQ_GAP | stage=S2 | role=architect | session=task-20260629-auth | msg=文档内容不完整: 技术方案缺少错误码定义 | ctx={"doc":"spec.md","missing_sections":["错误码规范"],"impact":"developer实现时可能自行定义错误码导致不一致"}
```

#### PDR_CONFIRM - 读取确认输出

```
[PDR-LOG] | level=INFO | event=PDR_CONFIRM | stage=<阶段ID> | role=<角色> | session=<会话ID> | msg=前置文档确认完成: <M>份已读取,<K>份缺失已标注风险 | ctx={"read_count":<已读数量>,"missing_count":<缺失数量>,"missing_with_risk":<已标注风险的缺失数>,"ready_to_proceed":<true/false>}
```

示例：
```
[PDR-LOG] | level=INFO | event=PDR_CONFIRM | stage=S4 | role=developer | session=task-20260629-auth | msg=前置文档确认完成: 3份已读取,1份缺失已标注风险 | ctx={"read_count":3,"missing_count":1,"missing_with_risk":1,"ready_to_proceed":true}
```

#### PDR_ERROR - 严重错误

```
[PDR-LOG] | level=ERROR | event=PDR_ERROR | stage=<阶段ID> | role=<角色> | session=<会话ID> | msg=<错误描述> | ctx={"error_type":"<错误类型>","doc":"<相关文档>","detail":"<错误详情>","recovery":"<恢复建议>"}
```

错误类型枚举：
- `CRITICAL_MISSING`：关键文档缺失且风险等级为high，无法继续
- `PARSE_ERROR`：文档解析失败（格式损坏、编码错误等）
- `PERMISSION_DENIED`：无权限读取文档
- `CIRCULAR_REF`：文档引用形成循环依赖

示例：
```
[PDR-LOG] | level=ERROR | event=PDR_ERROR | stage=S2 | role=architect | session=task-20260629-auth | msg=关键前置文档缺失: 任务分解清单不存在 | ctx={"error_type":"CRITICAL_MISSING","doc":"任务分解清单","detail":"需求接收阶段未产出任务分解清单","recovery":"退回S1需求接收阶段,要求orchestrator补全任务分解清单"}
```

### 日志输出要求

1. PDR日志与SG-LOG使用相同的结构化格式和字段约定
2. 每份文档读取后立即输出PDR_DOC_READ，不得批量延迟输出
3. PDR_CONFIRM必须与面向用户的📋确认输出同时出现
4. PDR_DOC_MISSING必须在请求获取文档之前输出
5. PDR_ERROR级别的日志必须在阶段守卫检查脚本中有对应记录
6. 新会话恢复时，跳过已读取文档可输出PDR_DOC_SKIP（DEBUG级别），不需要重复输出PDR_DOC_READ

---

---

## 相关模式

- [渐进式上下文披露](../../../docs/retrospective/patterns/methodology-patterns/ai-collaboration/progressive-context-disclosure.md)
- [上下文恢复协议](../../../docs/retrospective/patterns/methodology-patterns/ai-collaboration/context-recovery-protocol.md)
---

← 上一章: [04 二次暴露治理检查点](04-second-exposure-governance.md) | **[返回索引](../pre-document-reading.md)** | 下一章: [06 与现有体系的关联](06-system-relations.md) →
