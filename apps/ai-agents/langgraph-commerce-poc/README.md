# LangGraph 商业化 PoC

LangGraph 商业化能力概念验证：**StateGraph 双节点 + MemorySaver 会话持久化 + DeepSeek 接入**，验证选型报告中商业化首选结论（LangGraph）的核心硬需求是否成立。

配套调研报告：[Python 智能体框架选型调研](../../../docs/retrospective/reports/competitive-analysis/retrospective-python-agent-framework-selection-20261021/README.md)

## 商业化验证点

| # | 硬需求 | PoC 验证方式 | 结论 |
|---|--------|--------------|------|
| 1 | 显式状态图（节点/边/条件边） | `graph.py`：`chat` → (条件边) → `tools` ⇄ `chat` → `end` | ✅ 编排原语完整 |
| 2 | 工具调用循环（ReAct 模式） | 问"现在几点"：LLM 决定调工具 → ToolNode 执行 → LLM 汇总 → 结束 | ✅ 循环收敛 |
| 3 | checkpointer 会话持久化 | 同一 `thread_id` 多轮消息累积；不同 `thread_id` 完全隔离 | ✅ 单元测试覆盖 |
| 4 | 模型无关性 | 同一状态图注入 ChatDeepSeek（真实）与自定义 ChatModel（演示）均可运行 | ✅ 任意模型可接入 |
| 5 | 国产模型接入 | `langchain-deepseek` 官方包（ChatDeepSeek） | ✅ 原生支持 |
| 6 | 安全红线 | 工具 `safe_calculator` 用 AST 白名单，拒绝任意代码执行/属性访问/幂 DoS | ✅ 危险表达式全部拒绝 |

**说明**：本 PoC 用 `MemorySaver`（内存态）验证 checkpointer 语义；商业化生产必须换 **SQLite/Postgres checkpointer**（`langgraph-checkpoint-sqlite` / `langgraph-checkpoint-postgres`），并部署 LangGraph Server/Platform 获得持久化、恢复与可观测性——这正是报告 §6.2 所述"生产级硬需求"的下一步。

## 快速开始

```bash
# 安装（editable + dev 依赖）
pip install -e ".[dev]"

# 演示模式（无需任何 API Key，验证状态图全链路）
langgraph-poc --model demo
# 问"现在几点"观察工具循环；/thread <id> 切换会话；/quit 退出

# 真实模式（需 DeepSeek API Key）
# Windows:  $env:DEEPSEEK_API_KEY="sk-..."
# Unix:     export DEEPSEEK_API_KEY="sk-..."
langgraph-poc                       # auto：有 Key 自动用 DeepSeek
langgraph-poc --model deepseek      # 强制真实调用
```

## CLI 用法

| 参数 | 说明 |
|------|------|
| `--model auto` | 默认：有 `DEEPSEEK_API_KEY` 用 DeepSeek，否则演示模式 |
| `--model demo` | 强制演示模式（规则模型，零外部调用） |
| `--model deepseek` | 强制真实调用；无 Key 返回错误码 2 |
| `--thread <id>` | 指定会话 ID（默认随机） |

会话内命令：`/quit` 退出、`/thread <id>` 切换/新建会话、`/reset` 清空当前会话。

## 工程结构

```
src/langgraph_poc/
├── __init__.py    # 包元信息
├── tools.py       # 确定性工具：get_current_time + safe_calculator（AST 白名单）
├── llm.py         # LLM 工厂：ChatDeepSeek（真实）/ RuleBasedChatModel（演示）
├── graph.py       # StateGraph 组装：chat/tools 双节点 + 条件边 + MemorySaver
└── cli.py         # 对话 CLI（thread_id 会话管理）
tests/
├── test_graph.py  # 工具循环 / 直答 / 持久化 / 线程隔离 / 工具安全 / __future__ 守护
└── test_cli.py    # 无 Key 保护路径 / 演示模式退出
```

## 测试

```bash
python -m pytest tests --cov=langgraph_poc --cov-report=term-missing
# 24 用例全绿；总覆盖率 81%；核心模块 graph/llm 100%、tools 97%
# 全部测试零外部 API 调用（演示模型），CI 可离线运行
```

## 工程约束（SpecWeave 项目规范）

- scikit-build-core 构建后端（`pyproject.toml`），`langgraph-poc` CLI 入口
- 禁止 `from __future__ import annotations`（ruff 静态拦截 + `tests/test_graph.py::TestNoFutureAnnotations` 运行时守护）
- 工具安全红线：计算器仅接受 AST 白名单表达式，拒绝任意代码执行

## 已知边界（如实披露）

- 演示模式规则模型不识别中文"计算/算一下"关键词触发计算器（仅时间类关键词触发工具）；真实 DeepSeek 会正确路由到 `safe_calculator`——如需演示计算器工具循环，可直接在测试中构造 tool_call 场景（`tests/test_graph.py` 已覆盖工具循环路径）
- MemorySaver 进程重启即失，生产换持久化 checkpointer
- 真实模式调用 DeepSeek 会产生 API 费用与网络依赖，未在 CI 中自动执行
