# Zleap-Agent Workspace-first 架构原型技术实现文档

> 本文档记录 `apps/zleap-workspace-first-prototype/` 原型的技术实现核心逻辑，基于已通过测试（33 个用例）的代码。
> 版本：v1.0 | 日期：2026-07-06

## 1. 架构总览

原型采用 **Workspace-first** 设计哲学，核心思想是"**先选工作区、再组装上下文**"。模块划分遵循五大概念边界：

```
┌─────────────────────────────────────────────────────────┐
│                    WorkspaceRegistry                     │
│   (Main 调度台 + 业务工作区，每个工作区独立运行单元)      │
├──────────┬──────────┬──────────┬──────────┬──────────────┤
│ Context  │  Tools   │  Memory  │ Runtime  │  Boundary    │
│ 上下文装配│ 工具绑定 │ 记忆分区 │ 轨迹审计 │ 四类边界检查   │
└──────────┴──────────┴──────────┴──────────┴──────────────┘
```

| 模块 | 文件 | 核心职责 |
|------|------|---------|
| Workspace | `workspace.py` | 工作区单元 + 注册中心 |
| Context | `context.py` | 上下文装配公式 + 加载模式 |
| Tools | `tools.py` | 工具注册 + 工作区绑定 |
| Memory | `memory.py` | 记忆三分区 + 双线 + 准入规则 |
| Runtime | `runtime.py` | 可审计运行轨迹 |
| Boundary | `boundary.py` | 四类边界检查 |

## 2. 核心公式与机制

### 2.1 上下文装配公式

```
Context = System Prompt + Workspace Prompt + Tools + Memory + History
```

实现于 `ContextAssembler.assemble()`，各组成部分独立存放，支持两种加载模式：

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| `prefetch` | 一次取全部分区 | 短的、准的、可控的上下文 |
| `agentic` | 按需读取（先取 people notes） | 大上下文按需加载 |

### 2.2 工具按工作区绑定（不全局暴露）

工具通过 `ToolRegistry.bind_to_workspace()` 绑定到具体工作区，模型进入哪个工作区就只看当前工作区的工具。**工具不全局暴露**，缩小模型的动作空间，降低审计成本。

### 2.3 记忆三分区 + 双线设计

记忆分为三个分区，对应双线设计：

| 分区 | 双线 | 存储内容 |
|------|------|---------|
| `people` | A 线 people notes | 用户偏好、稳定画像 |
| `task` | B 线 core records | 工作事件、项目事实 |
| `experience` | B 线 core records | 经验（脱敏处理） |

**经验记忆准入规则**：允许 4 类（可复用流程/失败模式/验证习惯/恢复策略）、禁止 6 类（公司名/客户名/项目名/财务事实/私有路径/一次性任务结果）。

### 2.4 四类边界检查

| 边界 | 检查内容 | 拦截条件 |
|------|---------|---------|
| 数据边界 | 敏感数据不出内网 | 敏感数据 + 工作区非私有 |
| 工具边界 | 工具按工作区可见 | 工具未绑定到当前工作区 |
| 模型边界 | 模型按工作区绑定 | 模型不在工作区白名单 |
| 记忆边界 | 不跨用户/任务读取 | 读取私有记忆分区 |

## 3. 关键实现细节

### 3.1 工作区注册与调度

```python
registry = WorkspaceRegistry()
registry.set_main(main)        # 设置 Main 调度台
registry.register(file_ws)     # 注册业务工作区
target = registry.get("finance")  # 按 ID 查询
```

Main 调度台不承担所有上下文，只负责理解用户目标、判断进入哪个业务工作区。

### 3.2 上下文装配

```python
assembler = ContextAssembler()
context = assembler.assemble(workspace, memory=memory, load_mode="prefetch")
```

装配结果包含 `system_prompt`、`workspace_prompt`、`tools`、`memory`、`history` 五个部分。

### 3.3 日志埋点

原型在 Memory 与 Boundary 模块的核心逻辑处埋入结构化日志，便于排查：

| 位置 | 日志级别 | 内容 |
|------|---------|------|
| MemoryStore 写入/读取 | `INFO` | 分区、key、value |
| MemoryManager 经验准入 | `INFO` | 写入成功/拦截原因 |
| 未知分区写入 | `ERROR` | 分区名 |
| Boundary 检查通过 | `INFO` | 边界类型、工作区 |
| Boundary 越权拦截 | `WARNING` | 越权类型、详情 |

## 4. 测试覆盖

33 个单元测试全部通过（`python -m unittest discover -s tests -p "test_*.py" -v`）：

| 测试文件 | 覆盖模块 | 用例数 |
|---------|---------|:---:|
| `tests/test_workspace_context.py` | Workspace/Context/Tools | 17 |
| `tests/test_memory.py` | Memory | 16 |

### 覆盖的关键行为

- **工作区**：注册、Main 调度、查询、异常处理
- **上下文**：装配公式、两种加载模式、to_text 转换
- **工具**：按工作区绑定、不全局暴露、schema 获取
- **记忆**：三分区隔离、双线写入、准入规则（允许 4 类 + 禁止 6 类）
- **边界**：卸载拦截、四类边界检查

## 5. 运行方式

```bash
cd apps/zleap-workspace-first-prototype
python main.py          # 运行完整演示
python -m unittest discover -s tests -p "test_*.py" -v   # 运行测试
```

## 6. 接口清单

| 类 | 关键方法 |
|----|---------|
| `Workspace` | `bind_tool()` / `get_visible_tools()` / `get_tool_schemas()` / `add_history()` |
| `WorkspaceRegistry` | `register()` / `set_main()` / `get()` / `get_main()` / `all()` |
| `ContextAssembler` | `assemble()` / `to_text()` / `set_global_system_prompt()` |
| `ToolRegistry` | `register_tool()` / `bind_to_workspace()` / `bind_many()` / `visible_to()` |
| `MemoryManager` | `write()` / `read()` / `write_people_note()` / `write_core_record()` / `write_experience()` |
| `RuntimeRecorder` | `record()` / `query()` / `audit()` |
| `BoundaryChecker` | `check_data_boundary()` / `check_tool_boundary()` / `check_model_boundary()` / `check_memory_boundary()` / `check_all()` |