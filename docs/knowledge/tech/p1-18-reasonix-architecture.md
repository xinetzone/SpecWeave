---
id: p1-18-reasonix-architecture
title: Reasonix 架构：Python AI Agent 分层设计模式
source: d:\spaces\chaos\hub\dao\src\reasonix
source_type: directory
category: tech
tags:
  - reasonix
  - ai-agent
  - python
  - architecture
  - design-patterns
  - pydantic
  - typer
  - assembler
  - permission-system
archive_status: archived
archive_priority: P1
created_at: 2026-08-02T12:45:00Z
updated_at: 2026-08-02T12:50:00Z
version: v0.1.0
reviewer: chaos-coordinator
review_notes: approved - Python AI Agent 分层架构范例，设计模式提炼完整，参考价值高
summary: DeepSeek-Reasonix 是一个配置驱动、多模型协作的 AI Coding Agent，采用清晰的分层架构（组装器+Provider+Agent+Controller），是 Python AI Agent 项目的优秀架构参考
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\tech\p1-18-reasonix-architecture.md
archived_at: 2026-08-02T04:55:56Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T04:55:56Z archived from d:\spaces\chaos\.agents\knowledge\temp\tech\p1-18-reasonix-architecture.md to D:\spaces\SpecWeave\.agents\docs\knowledge\tech\p1-18-reasonix-architecture.md
---

# Reasonix 架构：Python AI Agent 分层设计模式

## 项目概述

**Reasonix** 是 DeepSeek 开源的配置驱动型 AI coding agent，版本 v0.1.0，采用纯 Python 实现，支持 CLI 交互、非交互式任务执行和 HTTP SSE 服务三种运行模式。

**技术栈**：
| 组件 | 选型 |
|------|------|
| Python 版本 | ≥ 3.11 |
| CLI 框架 | typer + rich（Markdown 渲染） |
| 配置验证 | Pydantic v2 |
| HTTP 服务 | Starlette + Uvicorn（SSE 流式） |
| HTTP 客户端 | httpx + httpx-sse |
| 配置格式 | TOML（tomllib，Python 3.11+ 内置） |
| 构建后端 | hatchling |

## 分层架构总览

```
┌─────────────────────────────────────────────────────────────┐
│  Frontends (CLI / HTTP)                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ run      │  │ chat     │  │ serve    │  （main.py）      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
├───────┼──────────────┼──────────────┼────────────────────────┤
│       ▼              ▼              ▼                        │
│  ┌─────────────────────────────────────────┐                │
│  │  Controller (control/controller.py)     │  ← 统一门面      │
│  │  - send/submit/cancel                   │                │
│  │  - plan_mode / approval                 │                │
│  │  - snapshot/rewind/fork                 │                │
│  └────────────────────┬────────────────────┘                │
├───────────────────────┼─────────────────────────────────────┤
│                       ▼                                      │
│  ┌─────────────────────────────────────────┐                │
│  │  Boot Assembler (boot/assembler.py)     │  ← 组装器模式    │
│  │  BuildOptions → build() → Controller    │                │
│  └───┬──────┬──────┬──────┬──────┬─────────┘                │
│      │      │      │      │      │                           │
│      ▼      ▼      ▼      ▼      ▼                           │
│  ┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐                    │
│  │Config││Prov. ││Tool  ││Perm. ││Event │  核心组件           │
│  │Loader││Factory│Reg.  ││Gate  ││Sink  │                    │
│  └──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘                    │
│     │       │       │       │       │                        │
│     ▼       ▼       ▼       ▼       ▼                        │
│  ┌─────────────────────────────────────────┐                │
│  │  Agent Core (agent/agent.py)            │  ← 会话循环      │
│  │  - stream_model → execute_batch → loop  │                │
│  └─────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## 各层详解

### 1. 入口层：main.py（typer CLI）

四种子命令：

| 命令 | 用途 | 特点 |
|------|------|------|
| `reasonix run <prompt>` | 非交互式执行任务 | 支持 stdin 管道、`--model`、`--max-steps`、`--workspace` |
| `reasonix chat` | 交互式对话 | 斜杠命令（/exit、/plan、/compact、/new、/help） |
| `reasonix serve` | HTTP 服务 | SSE 事件流，默认 127.0.0.1:8080 |
| `reasonix setup` | 配置向导 | 交互式生成 reasonix.toml 和 .env |

### 2. 控制层：Controller（control/controller.py）

前端无关的统一门面，为 CLI/TUI/HTTP 提供一致接口：

```python
class Controller:
    async def send(ctx, user_input) -> str      # 提交输入，返回最终文本
    def submit(ctx, user_input) -> Task         # 异步提交，支持取消
    def cancel()                                 # 取消当前运行
    def set_plan_mode(enabled: bool)             # 计划模式（只读工具限制）
    def approve(allow: bool, remember: bool)     # 响应审批请求
    def is_waiting_approval() -> bool
    def pending_approval() -> dict               # 获取待审批工具信息
    def snapshot() / rewind() / fork()           # 会话管理
```

**InteractiveApprover**：基于 asyncio.Event 的交互式审批实现，支持 remember 规则记忆。

### 3. 组装层：Boot Assembler（boot/assembler.py）

**组装器模式**是 Reasonix 架构的核心，通过 `build(options: BuildOptions)` 函数完成从配置到可用 Controller 的完整组装：

**组装步骤（10步流水线）**：
1. 加载配置（多层合并 + CLI 覆盖）
2. 解析默认模型，校验可用 provider
3. 验证 API key 存在
4. 通过工厂创建 Provider 实例
5. 构建系统提示词（支持文件/字符串/默认）
6. 创建 Session（system_prompt 前缀）
7. 构建 Tool Registry 并注册内置工具；按 `tools.enabled` 过滤
8. 从配置构建 Permission Policy 和 Gate
9. 创建 Agent 实例（注入 provider/registry/session/gate/sink）
10. 创建 Controller 并返回

**BuildOptions**：
```python
@dataclass
class BuildOptions:
    workspace_dir: str | Path = "."
    config_path: str = ""
    model: str = ""                    # CLI 覆盖模型
    max_steps: int | None = None       # CLI 覆盖最大步数
    require_key: bool = True
    sink: Sink | None = None           # 事件输出
    broadcaster: Broadcaster | None = None
    plan_mode: bool = False
```

### 4. 配置层：Config Loader（config/）

**多层配置合并**（优先级从低到高）：
```
DEFAULT_CONFIG
  ↓ 覆盖
~/.config/reasonix/config.toml (用户级)
  ↓ 覆盖
./reasonix.toml (项目级)
  ↓ 合并
./.mcp.json (自动发现 MCP 插件)
  ↓ 覆盖
CLI flags (cli_overrides)
  ↓ 展开
${VAR:-default} 环境变量
  ↓ 验证
Config.model_validate() (Pydantic v2)
```

**关键特性**：
- 环境变量展开支持 `${VAR}` 和 `${VAR:-default}` 语法
- `.env` 文件自动加载（workspace > home，不覆盖已有环境变量）
- MCP 服务器自动从 `.mcp.json` 发现并合并到 plugins
- 跨平台配置目录（Windows: `%APPDATA%/reasonix`，Linux/macOS: `~/.config/reasonix`）
- `render_toml()` 将 Config 序列化回 TOML（配置向导用）

### 5. Provider 抽象层（provider/base.py）

抽象工厂模式，支持多种模型后端：

```python
class Provider(ABC):
    @abstractmethod
    def name(self) -> str
    @abstractmethod
    async def stream(ctx, request: ProviderRequest) -> AsyncIterator[ProviderChunk]

# 工厂注册
_registry: dict[str, type[Provider]] = {}
def register_provider(kind: str, factory: type[Provider])
def get_provider_factory(kind: str) -> type[Provider] | None
```

**流式分块类型**：
- `kind="text"` → 文本增量
- `kind="reasoning"` → 思考过程（用于 thinking 模型）
- `kind="tool_call"` → 工具调用收集
- `kind="usage"` → token 用量统计
- `kind="done"` → 流结束
- `kind="error"` → 错误

**数据模型**：
- `Message`：role/content/tool_call_id/tool_calls，支持 `to_openai()` 转换
- `ToolSchema`：name/description/parameters，支持 `to_openai()` 函数调用格式
- `ProviderRequest`：messages/tools/temperature/max_tokens
- `AuthError`：认证失败异常，包含 provider_name 和 key_source

### 6. 工具层：Tool Registry（tool/）

**Tool 抽象接口**：
```python
class Tool(ABC):
    @abstractmethod def name(self) -> str
    @abstractmethod def description(self) -> str
    @abstractmethod def schema(self) -> dict[str, Any]      # JSON Schema
    @abstractmethod async def execute(ctx, args) -> str
    def read_only(self) -> bool       # True = 可并行执行，默认 False
```

**FunctionTool**：便捷包装器，从普通函数（同步/异步）创建 Tool：
```python
FunctionTool(name, description, parameters, fn, read_only=False)
```

**Registry**（保持插入顺序）：
- `add(tool)`：注册工具（同名替换，首次添加记录顺序）
- `get(name)` / `names()` / `schemas()`：查询与 schema 导出
- `remove_prefix(prefix)`：按前缀批量移除（用于插件卸载）
- `canonicalize_schema()`：schema 规范化（自动补 `type: "object"` 和 `properties:{}`）

### 7. Agent 核心层（agent/agent.py）

**会话循环（Agent.run）**：
```
while steps < max_steps and not cancelled:
    1. stream_model() → (text, tool_calls)
       - 向 provider 发送 messages + tool_schemas
       - plan_mode 时不发送 tools（模型无法调用工具）
       - 流式接收 chunk，emit 事件
    2. 如果有 tool_calls：
       a. 权限检查（Gate.check）
       b. 判断并行性：全只读 → asyncio.gather 并行；否则串行
       c. execute_batch() → results
       d. assistant 消息（含 tool_calls）加入 session
       e. tool 结果逐个加入 session
       f. 风暴检测：同一工具连续失败 ≥3 次提示换方法
    3. 如果没有 tool_calls：
       - 最终答案，break
```

**关键常量**：
- `MAX_TOOL_OUTPUT = 20_000`：工具输出截断阈值（超过后保留头尾各半）
- `MAX_PARALLEL = 8`：最大并行工具数
- `MAX_STORM_FAILURES = 3`：连续失败风暴检测阈值

### 8. 权限系统（permission/policy.py）

**决策优先级**：`deny > ask > allow > fallback`

**规则格式**：
- `bash`：匹配所有 bash 调用
- `bash(rm -rf *)`：匹配特定命令模式（支持 fnmatch 通配符）

**Policy 规则引擎**：
```python
@dataclass
class Policy:
    mode: str = "ask"               # 写工具默认模式：ask/allow/deny
    allow_rules: list[Rule]
    ask_rules: list[Rule]
    deny_rules: list[Rule]

    def decide(tool_name, read_only, args) -> Decision
```

**fallback 逻辑**：
- 只读工具 → 直接 `ALLOW`
- 写工具 → 按 `mode` 默认值

**Gate**：组合 Policy 和 Approver：
```python
async def check(tool_name, read_only, args) -> (Decision, reason)
```
- DENY → 直接返回拒绝原因
- ASK → 调用 Approver（交互模式弹审批/Headless 自动允许）
- ALLOW → 通过

**Subject 提取**（用于规则匹配）：
优先级：`command` > `file_path/path` > `pattern`

### 9. 事件系统（event/events.py）

观察者模式，通过 Sink 解耦 Agent 与前端：
- `Sink.emit(event)`：事件接收接口
- `CollectSink`：收集所有事件（用于非交互模式获取结果）
- `FuncSink(fn)`：函数适配器
- `Broadcaster`：多订阅者广播

**事件类型**：turn_started、turn_done、text、reasoning、tool_dispatch、tool_result、usage、error_event

### 10. 配置模型（config/models.py）

Pydantic v2 数据模型：

| 模型 | 用途 |
|------|------|
| `Pricing` | Token 单价（input/output/cache_hit/currency） |
| `ProviderEntry` | 模型提供商（name/kind/base_url/model/models/api_key_env/context_window/price） |
| `AgentConfig` | Agent 行为（system_prompt/max_steps/temperature/planner_model/output_style） |
| `ToolsConfig` | 工具启用列表 |
| `PermissionsConfig` | 权限策略（mode/allow/ask/deny） |
| `SandboxConfig` | 沙箱（workspace_root/allow_write/bash/network） |
| `PluginEntry` | MCP 插件（type=stdio/url，command/args/env 或 url/headers） |
| `SkillsConfig` | 技能搜索路径 |
| `CodegraphConfig` | 代码图谱集成 |
| `Config` | 顶层配置，包含 `resolve_model()`（支持 provider/model、provider、bare-model 三种引用形式） |

## 核心设计模式总结

| 模式 | 应用位置 | 价值 |
|------|----------|------|
| **组装器（Builder/Assembler）** | `boot/assembler.py` | 集中式组件装配，配置→实例的确定性流水线 |
| **抽象工厂** | `provider/base.py` 工厂注册 | Provider 可插拔（OpenAI、DeepSeek、Anthropic 等） |
| **策略模式** | `permission/policy.py` Policy | 权限规则可配置，支持 allow/ask/deny 组合 |
| **门面模式** | `control/controller.py` | 前端无关的统一接口，CLI/HTTP 复用同一逻辑 |
| **观察者模式** | `event/events.py` Sink | 事件流解耦，支持多种输出方式（终端/HTTP/TUI） |
| **模板方法** | `agent/agent.py` 会话循环 | 固定 Agent 循环骨架，Provider/Tool 可替换 |
| **数据类配置** | Pydantic v2 + TOML | 多层配置合并 + 验证 + 序列化，类型安全 |

## 可复用最佳实践

1. **BuildOptions 显式组装**：不依赖全局状态，所有依赖通过 build() 注入，易测试
2. **只读/写工具自动并行**：通过 `read_only()` 标记自动判断执行策略，无需人工标注并行性
3. **多层配置合并**：默认 < 用户 < 项目 < CLI，支持环境变量展开，是 CLI 工具的黄金标准
4. **风暴检测**：连续失败提示，防止 Agent 陷入死循环
5. **工具输出截断**：自动保留头尾，避免上下文爆炸
6. **计划模式**：只读模式先规划再执行，安全预览
7. **Subject 提取**：权限规则不止匹配工具名，还匹配参数（如 bash 命令内容），粒度更细
8. **MCP 自动发现**：`.mcp.json` 自动加载插件，零配置扩展

## 与其他 Agent 框架对比

| 特性 | Reasonix | LangChain | AutoGPT |
|------|----------|-----------|---------|
| 架构复杂度 | 简洁（9个模块） | 重（多层抽象） | 中等 |
| 配置驱动 | ✅ TOML + 多层合并 | ❌ 代码配置 | ❌ 环境变量 |
| 权限系统 | ✅ Policy + Gate + 交互审批 | ❌ 无 | ❌ 基础 |
| 多前端统一 | ✅ Controller 门面 | ❌ 绑定特定接口 | ❌ CLI only |
| 流式处理 | ✅ SSE + 分块事件 | ⚠️ 部分支持 | ❌ |
| 计划模式 | ✅ 内置 | ⚠️ 需自行实现 | ⚠️ 有 |
| MCP 支持 | ✅ 自动发现 .mcp.json | ❌ | ❌ |

---

**来源参考**：
- 项目目录：[src/reasonix/](file:///d:/spaces/chaos/hub/dao/src/reasonix/)
- 入口点：[main.py](file:///d:/spaces/chaos/hub/dao/src/reasonix/main.py)
- 组装器：[boot/assembler.py](file:///d:/spaces/chaos/hub/dao/src/reasonix/boot/assembler.py)
- Agent 核心：[agent/agent.py](file:///d:/spaces/chaos/hub/dao/src/reasonix/agent/agent.py)
- 权限系统：[permission/policy.py](file:///d:/spaces/chaos/hub/dao/src/reasonix/permission/policy.py)
- 配置加载：[config/loader.py](file:///d:/spaces/chaos/hub/dao/src/reasonix/config/loader.py)
- 配置模型：[config/models.py](file:///d:/spaces/chaos/hub/dao/src/reasonix/config/models.py)
- 项目配置：[pyproject.toml](file:///d:/spaces/chaos/hub/dao/pyproject.toml)
