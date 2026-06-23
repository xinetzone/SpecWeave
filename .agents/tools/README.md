# 工具规范索引

本目录收录了智能体在执行任务过程中所使用的全部工具规范，按照功能类别进行组织。所有智能体在调用工具前应先查阅对应规范，确保参数格式、输出处理与使用约束符合约定。

## 工具分类表

| 类别 | 规范文件 | 涵盖工具 | 适用场景 |
|---|---|---|---|
| 文件操作 | [file-operations.md](./file-operations.md) | read_file、write_file、edit_file、delete_file、list_directory | 文件读写、编辑、删除、目录列举 |
| 代码执行 | [code-execution.md](./code-execution.md) | run_command、run_tests、build_project | 终端命令执行、测试运行、项目构建 |
| 搜索 | [search.md](./search.md) | grep_search、glob_find、semantic_search | 内容正则搜索、文件名匹配、语义搜索 |
| 通信 | [communication.md](./communication.md) | send_message、handoff_task、sync_status | 智能体间消息传递、任务交接、状态同步 |

## 使用说明

### 1. 工具选择原则

- **优先使用专用工具**：所有文件操作、搜索任务必须使用本目录定义的专用工具，禁止使用 shell 命令（如 `cat`、`grep`、`find`、`sed` 等）替代。
- **精确匹配优先 grep**：当需要精确文本或符号匹配时，使用 `grep_search`；当需要按意图查找代码时，使用 `semantic_search`。
- **路径必须为绝对路径**：所有涉及文件路径的工具参数，必须使用完整绝对路径，禁止相对路径。

### 2. 规范查阅流程

1. 根据任务类型确定所需工具类别（文件操作、代码执行、搜索、通信）。
2. 打开对应规范文件，查阅工具清单与输入参数 Schema。
3. 严格按照使用约束执行工具调用。
4. 按照输出格式解析返回结果，处理成功与失败两种情况。

### 3. 工具调用最佳实践

- **批量调用**：独立的工具调用应并行执行，单次响应中并行调用数量不超过 5 个。
- **先读后写**：对已存在文件执行写入或编辑前，必须先读取文件内容。
- **错误处理**：工具调用失败时，不应盲目重试相同操作，应分析错误原因并调整策略。
- **敏感文件保护**：禁止操作 `.env`、`credentials.json`、密钥文件等敏感文件。

### 4. 与协作协议的关系

通信类工具（`send_message`、`handoff_task`、`sync_status`）的调用必须遵循 `.agents/protocols/` 目录下的协作协议：

- `send_message` 遵循 [messaging.md](../protocols/messaging.md) 消息传递协议
- `handoff_task` 遵循 [handoff.md](../protocols/handoff.md) 任务交接协议
- 冲突场景遵循 [conflict-resolution.md](../protocols/conflict-resolution.md) 冲突解决协议

### 5. 规范维护

- 工具新增或废弃时，应同步更新本索引与对应规范文件。
- 规范变更应经过 architect 智能体评审，并通过 orchestrator 通知所有相关智能体。
- 所有规范文件使用 Markdown 格式，遵循统一的章节结构（工具清单、输入参数 Schema、输出格式、使用约束、示例）。
