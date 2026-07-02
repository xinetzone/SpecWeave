---
id: "tools-communication"
title: "通信工具规范"
source: "AGENTS.md#工具规范"
x-toml-ref: "../../.meta/toml/.agents/tools/communication.toml"
---
# 通信工具规范

本规范定义了智能体之间进行消息传递、任务交接以及状态同步时所使用的工具集合、参数格式、输出约定以及使用约束，确保多智能体协作过程有序、可追溯且符合协作协议。

## 工具清单

| 工具名称 | 功能 | 输入参数 | 输出格式 |
|---|---|---|---|
| send_message | 发送消息给其他智能体 | receiver: string, message_type: string, content: string, priority: string | 投递状态 |
| handoff_task | 任务交接 | receiver: string, context: string, completed: string, pending: string, risks: string | 交接确认 |
| sync_status | 状态同步 | status: string, progress: number | 同步确认 |

## 输入参数 Schema

### send_message

```json
{
  "receiver": {
    "type": "string",
    "description": "消息接收方智能体标识，如 orchestrator、developer、reviewer、architect 等",
    "required": true
  },
  "message_type": {
    "type": "string",
    "enum": ["task_assignment", "status_update", "question", "review_request", "handoff", "conflict_report"],
    "description": "消息类型，详见 messaging.md 协议",
    "required": true
  },
  "content": {
    "type": "string",
    "description": "消息正文内容，应为结构化文本",
    "required": true
  },
  "priority": {
    "type": "string",
    "enum": ["high", "medium", "low"],
    "description": "消息优先级，默认为 medium",
    "required": false,
    "default": "medium"
  }
}
```

### handoff_task

```json
{
  "receiver": {
    "type": "string",
    "description": "任务交接的接收方智能体标识",
    "required": true
  },
  "context": {
    "type": "string",
    "description": "任务上下文与背景描述，包含任务目标、相关需求等",
    "required": true
  },
  "completed": {
    "type": "string",
    "description": "已完成的工作列表，描述已完成的步骤与产出",
    "required": true
  },
  "pending": {
    "type": "string",
    "description": "待办事项列表，描述尚未完成的工作",
    "required": true
  },
  "risks": {
    "type": "string",
    "description": "风险提示，包含已知风险与潜在问题",
    "required": false
  }
}
```

### sync_status

```json
{
  "status": {
    "type": "string",
    "enum": ["idle", "in_progress", "blocked", "completed", "failed"],
    "description": "当前智能体状态",
    "required": true
  },
  "progress": {
    "type": "number",
    "minimum": 0,
    "maximum": 100,
    "description": "任务完成进度百分比，0 表示未开始，100 表示已完成",
    "required": true
  }
}
```

## 输出格式

### send_message 输出示例

```json
{
  "status": "success",
  "data": {
    "message_id": "msg-2026-06-23-001",
    "receiver": "developer",
    "message_type": "task_assignment",
    "priority": "high",
    "timestamp": "2026-06-23T10:00:00Z",
    "delivered": true
  },
  "error": null
}
```

### handoff_task 输出示例

```json
{
  "status": "success",
  "data": {
    "handoff_id": "handoff-2026-06-23-001",
    "from": "orchestrator",
    "to": "developer",
    "received": true,
    "acknowledged": true,
    "timestamp": "2026-06-23T10:05:00Z"
  },
  "error": null
}
```

### sync_status 输出示例

```json
{
  "status": "success",
  "data": {
    "agent": "developer",
    "previous_status": "idle",
    "current_status": "in_progress",
    "progress": 35,
    "timestamp": "2026-06-23T10:10:00Z",
    "synced": true
  },
  "error": null
}
```

## 使用约束

1. **遵循 messaging.md 协议格式**：`send_message` 的消息格式必须符合 `.agents/protocols/messaging.md` 中定义的 YAML 消息结构，包含 `from`、`to`、`type`、`content`、`priority`、`timestamp` 字段。
2. **遵循 handoff.md 协议格式**：`handoff_task` 的交接内容必须符合 `.agents/protocols/handoff.md` 中定义的 YAML 交接结构，包含 `from`、`to`、`task_context`、`completed_work`、`pending_items`、`risks`、`timestamp` 字段。
3. **消息类型合规**：`message_type` 必须使用 messaging.md 中枚举的类型之一，禁止使用未定义的类型。
4. **优先级合理使用**：`high` 优先级仅用于阻塞性问题、紧急任务分配或冲突报告；常规沟通使用 `medium`；非紧急通知使用 `low`。
5. **交接完整性**：`handoff_task` 必须提供完整的 `context`、`completed`、`pending` 字段，确保接收方能够无缝接续工作。
6. **状态同步频率**：`sync_status` 应在任务状态变更时调用，包括开始任务、遇到阻塞、完成任务等节点；长任务应每隔 30 分钟同步一次进度。
7. **接收方存在性校验**：发送消息或交接任务前，应确认接收方智能体标识有效且在线。
8. **消息内容结构化**：`content` 字段应使用结构化文本，避免冗长叙述；复杂信息应使用列表或表格格式。
9. **避免消息风暴**：单次任务中向同一接收方发送消息不应超过 10 条，频繁沟通应考虑合并消息或提升为同步会议。
10. **时间戳统一**：所有消息与交接记录使用 ISO 8601 格式时间戳（如 `2026-06-23T10:00:00Z`），时区统一为 UTC。

## 示例

### 示例 1：分配任务给开发智能体

```json
{
  "tool": "send_message",
  "parameters": {
    "receiver": "developer",
    "message_type": "task_assignment",
    "content": "任务：实现用户登录接口\n目标文件：d:/AI/src/auth/login.ts\n要求：\n1. 支持邮箱密码登录\n2. 密码使用 bcrypt 加密\n3. 返回 JWT token\n截止时间：2026-06-23 18:00",
    "priority": "high"
  }
}
```

### 示例 2：任务交接给审查智能体

```json
{
  "tool": "handoff_task",
  "parameters": {
    "receiver": "reviewer",
    "context": "用户登录接口开发任务已完成，需要进行代码审查",
    "completed": "1. 实现邮箱密码登录逻辑\n2. 集成 bcrypt 加密\n3. 生成 JWT token\n4. 编写单元测试（覆盖率 90%）",
    "pending": "1. 代码审查反馈处理\n2. 集成测试待补充",
    "risks": "JWT 密钥目前硬编码在代码中，需后续迁移至环境变量"
  }
}
```

### 示例 3：同步任务进度

```json
{
  "tool": "sync_status",
  "parameters": {
    "status": "in_progress",
    "progress": 65
  }
}
```
