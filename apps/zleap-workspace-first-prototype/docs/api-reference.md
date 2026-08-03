# Zleap-Agent Workspace-first 原型 API 参考速查表

> 从 `docs/technical-implementation.md` 提取核心公式与接口清单，形成快速查阅的 API 速查表。
> 版本：v1.0 | 日期：2026-07-06

## 1. 核心公式

```
Context = System Prompt + Workspace Prompt + Tools + Memory + History
```

## 2. 模块与接口速查

### 2.1 Workspace（workspace.py）— 工作区单元

| 方法 | 签名 | 说明 |
|------|------|------|
| `bind_tool` | `(tool)` | 绑定工具到当前工作区 |
| `get_visible_tools` | `() -> List[Tool]` | 获取可见工具列表 |
| `get_tool_schemas` | `() -> List[Dict]` | 获取工具 schema（计入上下文） |
| `add_history` | `(entry)` | 追加一条历史轨迹 |

**构造参数**：`workspace_id, name, workspace_prompt="", system_prompt="", model="default", permission="", private=False`

### 2.2 WorkspaceRegistry（workspace.py）— 工作区注册中心

| 方法 | 签名 | 说明 |
|------|------|------|
| `register` | `(workspace) -> Workspace` | 注册工作区 |
| `set_main` | `(workspace)` | 设置 Main 调度台 |
| `get` | `(workspace_id) -> Workspace` | 按 ID 查询 |
| `get_main` | `() -> Workspace` | 获取 Main 调度台 |
| `all` | `() -> List[Workspace]` | 返回全部工作区 |

### 2.3 ContextAssembler（context.py）— 上下文装配

| 方法 | 签名 | 说明 |
|------|------|------|
| `set_global_system_prompt` | `(prompt)` | 设置全局 System Prompt |
| `assemble` | `(workspace, memory=None, include_history=True, load_mode="prefetch") -> Dict` | 按公式装配上下文 |
| `to_text` | `(context) -> str` | 上下文转文本 |

**load_mode**：`prefetch`（预取全分区）/ `agentic`（按需读取 people notes）

### 2.4 ToolRegistry（tools.py）— 工具注册中心

| 方法 | 签名 | 说明 |
|------|------|------|
| `register_tool` | `(tool)` | 注册工具到全局池 |
| `bind_to_workspace` | `(workspace, tool_name)` | 绑定工具到工作区 |
| `bind_many` | `(workspace, tool_names)` | 批量绑定 |
| `get_global` | `(tool_name) -> Tool` | 从全局池获取 |
| `visible_to` | `(workspace) -> List[Tool]` | 工作区可见工具 |

**内置工具**：`read_file`、`write_file`、`search_web`、`run_sql`、`process_receipt`

### 2.5 MemoryManager（memory.py）— 记忆管理器

| 方法 | 签名 | 说明 |
|------|------|------|
| `write` | `(partition, key, value)` | 向分区写入记忆 |
| `read` | `(partition, key) -> Any` | 读取记忆 |
| `read_partition` | `(partition) -> Dict` | 读取整个分区 |
| `write_people_note` | `(key, value)` | A 线：写用户偏好 |
| `write_core_record` | `(key, value)` | B 线：写工作事件 |
| `write_experience` | `(content, key="") -> bool` | 写经验（准入规则） |
| `all_partitions` | `() -> Dict` | 返回全部分区 |

**分区**：`people`（人）、`task`（事）、`experience`（经验）
**准入规则**：允许 4 类（可复用流程/失败模式/验证习惯/恢复策略），禁止 6 类（公司名/客户名/项目名/财务事实/私有路径/一次性任务结果）

### 2.6 RuntimeRecorder（runtime.py）— 运行轨迹

| 方法 | 签名 | 说明 |
|------|------|------|
| `record` | `(workspace_id, action, context_snapshot, result) -> RuntimeTrace` | 记录轨迹 |
| `query` | `(workspace_id="") -> List[RuntimeTrace]` | 查询轨迹 |
| `audit` | `(workspace_id="") -> List[Dict]` | 审计视图 |

### 2.7 BoundaryChecker（boundary.py）— 四类边界检查

| 方法 | 签名 | 说明 |
|------|------|------|
| `mark_sensitive` | `(data_desc)` | 标记敏感数据 |
| `check_data_boundary` | `(data_desc, workspace) -> bool` | 数据边界 |
| `check_tool_boundary` | `(workspace, tool_name) -> bool` | 工具边界 |
| `set_allowed_models` | `(workspace_id, models)` | 设置模型白名单 |
| `check_model_boundary` | `(workspace) -> bool` | 模型边界 |
| `mark_memory_private` | `(partition)` | 标记私有记忆分区 |
| `check_memory_boundary` | `(partition) -> bool` | 记忆边界 |
| `check_all` | `(workspace) -> bool` | 全量边界检查 |

**异常**：`BoundaryViolation`（越权时抛出）

### 2.8 ModelRouter（router.py）— 多模型路由（P0 新增）

| 方法 | 签名 | 说明 |
|------|------|------|
| `add_strategy` | `(strategy)` | 注册路由策略（按优先级排序） |
| `route` | `(workspace_id, task, task_type="", complexity=0.0) -> str` | 路由返回目标模型 |
| `get_trace` | `() -> List[Dict]` | 返回路由轨迹 |

**策略类**：`DataBoundaryStrategy`（敏感→本地，优先级100）、`ComplexityStrategy`（复杂→强模型，优先级50）、`CostStrategy`（简单查询→便宜模型，优先级30）、`FallbackStrategy`（兜底默认，优先级0）

## 3. 运行命令

```bash
cd apps/zleap-workspace-first-prototype
python main.py          # 运行完整演示
python -m unittest discover -s tests -p "test_*.py" -v   # 运行全部测试
```

## 4. 目录结构

```
apps/zleap-workspace-first-prototype/
├── workspace.py   # 工作区单元 + 注册中心
├── context.py     # 上下文装配
├── tools.py       # 工具注册 + 绑定
├── memory.py      # 记忆管理
├── runtime.py     # 轨迹记录
├── boundary.py    # 四类边界
├── router.py      # 多模型路由（P0 新增）
├── main.py        # 演示入口
├── docs/
│   ├── technical-implementation.md
│   ├── multi-model-routing-plan.md
│   └── api-reference.md（本文件）
└── tests/
    ├── test_workspace_context.py
    ├── test_memory.py
    └── test_router.py（待新增）
```