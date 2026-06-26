# 协议索引与使用流程

本目录收录了多智能体协作过程中所遵循的全部协议，涵盖任务交接、消息传递、冲突解决以及临时依赖管理。所有智能体在协作前应熟悉本目录协议，确保协作行为符合约定。

## 协议清单表

| 协议名称 | 协议文件 | 核心内容 | 适用场景 |
|---|---|---|---|
| 任务交接协议 | [handoff.md](./handoff.md) | 交接 YAML 格式、字段定义、交接流程图、使用约束 | 智能体间任务转移、上下文传递 |
| 消息传递协议 | [messaging.md](./messaging.md) | 消息 YAML 格式、消息类型枚举、优先级枚举、使用约束 | 智能体间日常沟通、任务分配、状态汇报 |
| 冲突解决协议 | [conflict-resolution.md](./conflict-resolution.md) | 冲突类型、升级路径流程图、仲裁规则 | 职责冲突、技术分歧、资源竞争 |
| 临时依赖管理流程 | [dependency-management.md](./dependency-management.md) | 存放位置、vendor 标准结构、元数据规范、清理机制、禁止提交条款、自动化验证脚本 | 第三方依赖管理、vendor 目录治理、临时文件处理、仓库整洁维护 |

## 使用流程示例

### 场景一：orchestrator 向 developer 分配任务

1. **查阅协议**：orchestrator 查阅 [messaging.md](./messaging.md) 确认消息格式与类型。
2. **构造消息**：按照消息格式构造 `task_assignment` 类型消息，设置 `priority` 为 `high`。
3. **发送消息**：通过 `send_message` 工具（见 [communication.md](../tools/communication.md)）发送消息。
4. **接收确认**：developer 收到消息后，通过 `sync_status` 工具同步状态为 `in_progress`。
5. **进度汇报**：developer 在任务执行过程中，定期通过 `status_update` 类型消息向 orchestrator 汇报进度。

### 场景二：developer 向 reviewer 交接任务

1. **查阅协议**：developer 查阅 [handoff.md](./handoff.md) 确认交接格式与字段。
2. **准备交接文档**：按照交接格式填写 `task_context`、`completed_work`、`pending_items`、`risks` 字段。
3. **执行交接**：通过 `handoff_task` 工具（见 [communication.md](../tools/communication.md)）发起交接。
4. **接收确认**：reviewer 收到交接后，明确确认接受或退回。
5. **状态同步**：developer 通过 `sync_status` 工具同步状态为 `completed`。

### 场景三：developer 与 reviewer 发生技术分歧

1. **识别冲突**：developer 识别到与 reviewer 的技术分歧属于冲突类型。
2. **查阅协议**：查阅 [conflict-resolution.md](./conflict-resolution.md) 确认冲突类型与解决方式。
3. **报告冲突**：通过 `send_message` 工具发送 `conflict_report` 类型消息给 architect。
4. **等待仲裁**：architect 根据"技术分歧"仲裁规则进行决策。
5. **执行决策**：相关智能体执行 architect 的仲裁结果。
6. **记录留存**：冲突报告与仲裁结果留存备查。

### 场景四：引入第三方依赖

1. **查阅流程**：查阅 [dependency-management.md](./dependency-management.md) 确认存放位置与规范。
2. **评估必要性**：确认无法通过包管理器安装后，决定引入至 `vendor/` 目录。
3. **初始化标准结构**：运行 `python .agents/scripts/check-vendor.py --fix` 创建标准目录结构和模板文件。
4. **存放依赖**：将第三方库放入 `vendor/` 对应子目录，按模板填写元数据（版本、来源、用途、许可证等）。
5. **更新版本清单**：在 `vendor/VERSION.md` 中记录新依赖信息。
6. **验证合规性**：运行 `python .agents/scripts/check-vendor.py` 确认目录结构合规。
7. **确认忽略规则**：确认 `.gitignore` 已配置 `vendor/` 忽略规则。
8. **定期审计**：定期运行 `python .agents/scripts/check-vendor.py --scan-refs` 检查未使用依赖。

## 协议维护说明

- 协议新增或变更应经过 architect 评审，并通过 orchestrator 通知所有相关智能体。
- 所有协议文件使用 Markdown 格式，遵循统一的章节结构。
- 协议变更应记录版本号与变更日期，便于追溯。
- 智能体在协作过程中如发现协议存在歧义或缺失，应通过 `question` 类型消息向 orchestrator 反馈。
