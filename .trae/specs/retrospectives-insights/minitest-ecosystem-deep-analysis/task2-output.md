# minitest-cli Python CLI 架构深度分析

## 1. 项目概览

**minitest-cli** 是 Minitest 测试平台的命令行界面，基于 Python 3.12+ 构建，采用现代异步 HTTP 客户端 httpx + Typer CLI 框架 + Pydantic 数据验证的技术栈。

- **版本**: 0.16.3
- **入口点**: `minitest = "minitest_cli.main:app"`
- **核心依赖**: typer>=0.24.1, httpx>=0.28.1, pydantic>=2.12.5, pydantic-settings>=2.13.1, rich>=14.3.3
- **开发工具**: ruff (lint+format), pyright (type check), pytest (testing)

**关键文件**:
- [pyproject.toml](../../../../apps/ai-code-assistant/pyproject.toml) - 项目配置与依赖
- [AGENTS.md](../../../../external/multica-ai/multica/AGENTS.md) - 编码规范与项目结构

---

## 2. 分层架构

minitest-cli 采用清晰的分层架构，共分为 6 层：

```
┌─────────────────────────────────────────────────────────────┐
│                     main.py (入口层)                         │
│  Typer 应用注册、全局选项(--json/--app/--version)、状态传递    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   commands/ (命令层)                         │
│  每个命令组是独立 Typer 子应用，包含命令定义与业务流程编排       │
│  配套 *_helpers.py 存放辅助逻辑，保持主文件 <150 行           │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                     core/ (核心层)                           │
│  config.py    - pydantic-settings 环境变量加载                │
│  auth.py      - 三种认证凭证优先级、token 自动刷新            │
│  credentials.py - OAuth 凭证持久化(0o600 权限)               │
│  oauth.py     - OAuth PKCE 登录流程(本地回调服务器)           │
│  app_context.py - --app 标志与 MINITEST_APP_ID 解析           │
│  token_exchange.py - Supabase token 交换与错误处理            │
│  tenants.py   - 多租户解析                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                     api/ (客户端层)                          │
│  client.py         - ApiClient 异步上下文管理器               │
│  apps_manager_client.py - apps-manager 服务专用客户端        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   models/ (模型层)                           │
│  Pydantic CamelModel 基类，自动 camelCase 别名序列化          │
│  app.py, batch.py, story_run.py, build.py, user_story.py     │
│  targets.py, base.py                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    utils/ (工具层)                           │
│  output.py      - stdout/stderr 分离输出机制                  │
│  update_check.py - PyPI 版本检查(24h缓存，非阻塞)            │
│  mermaid.py     - Mermaid 图表生成                           │
│  skill_refresh.py - Agent Skill 同步                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 目录结构

```
src/minitest_cli/
├── __init__.py                 # 版本号导出
├── main.py                     # Typer 应用入口
├── api/
│   ├── __init__.py
│   ├── client.py              # 核心异步 HTTP 客户端
│   └── apps_manager_client.py # apps-manager 服务客户端
├── assets/
│   ├── __init__.py
│   └── callback.html          # OAuth 登录成功页面模板
├── commands/
│   ├── __init__.py            # (空文件)
│   ├── init.py                # init 命令 - AI Agent onboarding
│   ├── init_playbook.py       # onboarding playbook 内容
│   ├── auth.py                # auth 命令组 - login/logout/status
│   ├── auth_api_key.py        # auth api-key 子命令
│   ├── apps.py                # apps 命令组 - list/create
│   ├── apps_helpers.py        # apps 创建辅助逻辑
│   ├── apps_dependencies.py   # apps dependencies 子命令
│   ├── user_story.py          # user-story 命令组
│   ├── user_story_helpers.py
│   ├── user_story_criteria.py
│   ├── user_story_bindings.py
│   ├── user_story_modify.py
│   ├── user_story_profiles.py
│   ├── test_profile.py        # test-profile 命令组
│   ├── test_profile_helpers.py
│   ├── test_profile_list.py
│   ├── test_profile_default.py
│   ├── test_file.py           # test-file 命令组
│   ├── test_file_helpers.py
│   ├── test_file_list.py
│   ├── flow_types.py          # flow-types 命令组
│   ├── app_knowledge.py       # app-knowledge 命令组
│   ├── app_knowledge_helpers.py
│   ├── build.py               # build 命令组
│   ├── build_helpers.py
│   ├── env.py                 # env 命令组
│   ├── env_helpers.py
│   ├── run.py                 # run 命令组 - start/status/list/cancel/all
│   ├── run_helpers.py         # run 核心辅助逻辑
│   ├── run_display.py         # run 结果显示
│   ├── run_targets.py         # 构建目标定义(iOS/Android/Web)
│   ├── batch.py               # batch 命令组 - list/get/cancel
│   ├── batch_helpers.py
│   ├── skill.py               # skill 命令组
│   └── upgrade.py             # upgrade 命令组
├── core/
│   ├── __init__.py
│   ├── config.py              # pydantic-settings 配置
│   ├── auth.py                # 认证公共 API
│   ├── credentials.py         # 凭证模型与文件 I/O
│   ├── oauth.py               # OAuth PKCE 流程
│   ├── token_exchange.py      # Supabase token 交换
│   ├── app_context.py         # App ID 解析
│   └── tenants.py             # 租户管理
├── models/
│   ├── __init__.py            # 模型重导出
│   ├── base.py                # CamelModel 基类
│   ├── app.py                 # App/Tenant 模型
│   ├── batch.py               # Batch 相关模型
│   ├── story_run.py           # StoryRun/PlatformRun/CriterionResult
│   ├── build.py               # Build 模型
│   ├── targets.py             # BatchTarget 模型
│   └── user_story.py          # UserStory 相关模型
└── utils/
    ├── __init__.py
    ├── output.py              # 输出工具(stdout/stderr分离)
    ├── mermaid.py             # Mermaid 图表
    ├── update_check.py        # 版本更新检查
    └── skill_refresh.py       # Skill 刷新
```

---

## 4. 命令体系表

main.py 注册了 **15 个命令组**，通过 `app.add_typer()` 挂载到根应用：

| 命令组 | 文件 | 核心子命令 | 功能说明 |
|--------|------|-----------|----------|
| `init` | `init.py` | (默认) | 输出 AI Agent onboarding playbook，自动检测 agent 环境 |
| `auth` | [auth.py](../../../../.agents/scripts/forum_bot/auth.py) | login, logout, status, api-key | OAuth PKCE 登录、登出、状态查看、API Key 管理 |
| `apps` | `apps.py` | list, create, dependencies | 应用列表、创建(支持多平台/icon上传)、依赖管理 |
| `user-story` | user_story.py | create, list, get, update, criteria, bindings | 用户故事 CRUD、验收标准、绑定管理 |
| `test-profile` | test_profile.py | list, get, create, default | 测试配置文件管理 |
| `test-file` | test_file.py | list, upload | 测试文件管理 |
| `flow-types` | flow_types.py | list | 流类型列表 |
| `app-knowledge` | `app_knowledge.py` | get, update | 应用知识库读取/更新(--content/--content-file) |
| `build` | build.py | list, get, upload | 构建管理与上传 |
| `env` | env.py | list, set, unset | 应用环境变量管理 |
| `run` | [run.py](../../../../external/anthropics/cwc-workshops/agent-decomposition/evals/run.py) | start, status, list, cancel, all | 测试执行：启动、轮询、列表、取消、全量运行 |
| `batch` | [batch.py](../../../../external/anthropics/claude-quickstarts/computer-use-best-practices/computer_use/tools/batch.py) | list, get, cancel | 批量执行管理(多故事) |
| `skill` | skill.py | refresh | Agent Skill 管理 |
| `upgrade` | upgrade.py | (默认) | CLI 自更新 |
| `user-story-bindings` | user_story_bindings.py | - | 用户故事绑定管理 |

---

## 5. ApiClient 设计

**位置**: [api/client.py](../../../../external/anthropics/claude-agent-sdk-python/src/claude_agent_sdk/client.py)

### 5.1 异步上下文管理器

`ApiClient` 实现了 `__aenter__`/`__aexit__` 异步上下文管理器协议，必须使用 `async with` 使用：

```python
async with ApiClient(settings) as client:
    response = await client.get("/api/v1/apps")
```

关键代码位置：
- `__aenter__` 方法: [client.py:30-40](../../../../external/anthropics/claude-agent-sdk-python/src/claude_agent_sdk/client.py#L30-L40)
- `__aexit__` 方法: [client.py:42-49](../../../../external/anthropics/claude-agent-sdk-python/src/claude_agent_sdk/client.py#L42-L49)

### 5.2 自动认证注入

在 `__aenter__` 中自动调用 `load_token()` 获取认证 token，注入 `Authorization: Bearer` 头：

```python
token = self._token_override or load_token(self._settings)
self._client = httpx.AsyncClient(
    base_url=self._settings.api_url,
    headers={
        "Authorization": f"Bearer {token}",
        CHANNEL_HEADER: CHANNEL_VALUE,
    },
    timeout=DEFAULT_TIMEOUT,
)
```

位置：[client.py:31-39](../../../../external/anthropics/claude-agent-sdk-python/src/claude_agent_sdk/client.py#L31-L39)

### 5.3 X-Minitest-Channel 头

所有请求自动携带 `X-Minitest-Channel: cli` 头，用于后端识别请求来源：

```python
CHANNEL_HEADER = "X-Minitest-Channel"
CHANNEL_VALUE = "cli"
```

位置：[client.py:10-11](../../../../external/anthropics/claude-agent-sdk-python/src/claude_agent_sdk/client.py#L10-L11)

### 5.4 超时配置

| 类型 | 超时值 | 用途 |
|------|--------|------|
| `DEFAULT_TIMEOUT` | 30.0 秒 | 普通 API 请求 |
| `UPLOAD_TIMEOUT` | 300.0 秒 (5分钟) | 文件上传(`upload_file()` 方法) |

位置：
- 默认超时: [client.py:12](../../../../external/anthropics/claude-agent-sdk-python/src/claude_agent_sdk/client.py#L12)
- 上传超时: [client.py:13](../../../../external/anthropics/claude-agent-sdk-python/src/claude_agent_sdk/client.py#L13)

### 5.5 文件上传

`upload_file()` 方法专门处理 multipart 文件上传，使用扩展超时：

```python
async def upload_file(
    self,
    path: str,
    *,
    files: dict[str, Any],
    data: dict[str, str] | None = None,
    timeout: float = UPLOAD_TIMEOUT,
    **kwargs: Any,
) -> httpx.Response:
```

位置：[client.py:77-94](../../../../external/anthropics/claude-agent-sdk-python/src/claude_agent_sdk/client.py#L77-L94)

### 5.6 HTTP 方法

支持标准 HTTP 方法：`get()`, `post()`, `put()`, `patch()`, `delete()`，均委托给底层 httpx.AsyncClient。

---

## 6. 三种认证凭证优先级

**位置**: [core/auth.py](../../../../.agents/scripts/forum_bot/auth.py)

`load_token()` 函数按以下优先级解析认证凭证：

### 优先级 1: MINITEST_TOKEN 环境变量

```python
if settings.token:
    return settings.token
```

位置：[auth.py:99-100](../../../../.agents/scripts/forum_bot/auth.py#L99-L100)

### 优先级 2: MINITEST_API_KEY 环境变量

```python
if settings.api_key:
    return settings.api_key.get_secret_value()
```

位置：[auth.py:102-103](../../../../.agents/scripts/forum_bot/auth.py#L102-L103)

注意：`api_key` 使用 `SecretStr` 类型存储，需要通过 `get_secret_value()` 获取明文。

### 优先级 3: OAuth 持久化凭证 (~/.minitest/credentials.json)

```python
try:
    creds = load_or_refresh_credentials(settings)
except SessionRevokedError:
    auth_error(...)
if creds is not None:
    return creds.access_token
```

位置：[auth.py:105-113](../../../../.agents/scripts/forum_bot/auth.py#L105-L113)

### 自动刷新机制

`load_or_refresh_credentials()` 检查凭证是否过期（提前 5 分钟刷新缓冲区），过期则自动调用 `refresh_token()`：

```python
REFRESH_BUFFER_SECONDS = 300  # refresh when < 5 minutes remain

@property
def is_expired(self) -> bool:
    return time.time() >= (self.expires_at - REFRESH_BUFFER_SECONDS)
```

位置：
- 刷新缓冲区: [credentials.py:15](../../../../external/anthropics/anthropic-sdk-python/src/anthropic/resources/beta/vaults/credentials.py#L15)
- is_expired 属性: [credentials.py:28-31](../../../../external/anthropics/anthropic-sdk-python/src/anthropic/resources/beta/vaults/credentials.py#L28-L31)
- 自动刷新逻辑: [auth.py:76-92](../../../../.agents/scripts/forum_bot/auth.py#L76-L92)

### 凭证文件安全

OAuth 凭证存储在 `~/.minitest/credentials.json`，文件权限设置为 `0o600`（仅所有者可读写）：

```python
CREDENTIALS_FILE_MODE = 0o600  # owner read/write only
```

位置：[credentials.py:14](../../../../external/anthropics/anthropic-sdk-python/src/anthropic/resources/beta/vaults/credentials.py#L14)

### 优先级冲突警告

当 `MINITEST_TOKEN` 和 `MINITEST_API_KEY` 同时设置时，输出一次警告到 stderr：

```python
if settings.token and settings.api_key:
    print(
        "[minitest] MINITEST_TOKEN and MINITEST_API_KEY are both set. "
        "MINITEST_TOKEN takes precedence. Unset one to silence this warning.",
        file=sys.stderr,
    )
```

位置：[auth.py:57-63](../../../../.agents/scripts/forum_bot/auth.py#L57-L63)

---

## 7. --json stdout/stderr 分离机制

**位置**: `utils/output.py`

### 核心设计原则

> stdout 保留给结构化数据（--json 时输出 JSON，否则输出表格），stderr 用于诊断、警告和进度消息。

位置：`output.py:3-6`

### 双 Console 设计

- `err_console = Console(stderr=True)` - 绑定到 stderr，永远不会被管道捕获
- `console = Console()` - 默认绑定到 stdout，用于输出数据

位置：
- err_console: `output.py:29`
- stdout console: `output.py:63`

### 输出函数

| 函数 | 输出目标 | 用途 |
|------|---------|------|
| `print_json()` | stdout | JSON 序列化输出(camelCase for Pydantic) |
| `print_table()` | stdout | Rich 表格输出 |
| `print_error()` | stderr | 红色错误消息 |
| `print_warning()` | stderr | 黄色警告消息 |
| `print_success()` | stderr | 绿色成功消息(✓) |
| `print_info()` | stderr | dim 灰色信息消息 |
| `output()` | 自动 | 统一出口: json_mode=True→print_json, 否则表格/键值对 |

位置：`output.py:32-93`

### Pydantic 模型自动 camelCase 转换

`_to_jsonable()` 递归转换 Pydantic 模型为 camelCase 别名字典：

```python
def _to_jsonable(data: Any) -> Any:
    if isinstance(data, BaseModel):
        return data.model_dump(mode="json", by_alias=True)
    if isinstance(data, dict):
        return {k: _to_jsonable(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_to_jsonable(v) for v in data]
    return data
```

位置：`output.py:17-25`

### 全局 --json 标志传递

`main.py` 的 callback 将 `json_mode` 存储到 `typer.Context`：

```python
ctx.json_mode = json  # type: ignore[attr-defined]
```

位置：[main.py:91](../../../../playground/chaos/libs/Nuitka/tests/distutils/example_3_dependencies_poetry_pyproject/src/main.py#L91)

各命令通过 `typer.Context.json_mode` 读取该标志。

---

## 8. 退出码定义

| 退出码 | 含义 | 定义位置 |
|--------|------|---------|
| **0** | 成功 | Typer 默认 |
| **1** | 通用错误 | `app_context.py:7` (EXIT_CODE_GENERAL_ERROR) |
| **2** | 认证错误 | `token_exchange.py:16` (EXIT_CODE_AUTH_ERROR) |
| **3** | 网络/API 错误 | `run_helpers.py:29` (EXIT_NETWORK_ERROR) |
| **4** | 资源未找到 | `run_helpers.py:30` (EXIT_NOT_FOUND) |
| **5** | 构建无效 | AGENTS.md 定义 |

### 退出码触发场景

| 退出码 | 触发条件 |
|--------|---------|
| 1 | 参数错误(如无效 UUID)、缺少必需参数、同时设置 --content 和 --content-file |
| 2 | 未认证、token 过期无法刷新、MINITEST_TOKEN 设置时尝试 OAuth login/logout |
| 3 | httpx.HTTPError(网络错误)、API 返回 4xx/5xx(非404) |
| 4 | API 返回 404、外键约束违反、user story 名称未找到 |
| 5 | Build 验证失败 |

位置：
- HTTP 错误处理: `run_helpers.py:92-107`
- 网络错误捕获: `run_helpers.py:110-116`

---

## 9. 关键命令流程分析

### 9.1 init 命令流程

**文件**: `init.py`

```
1. 检测执行环境
   ├─ agent_flag=True (--agent) → agent 模式
   ├─ json_mode=True (--json) → agent 模式
   ├─ 检测 AI Agent 环境变量 (CLAUDECODE, CURSOR_TRACE_ID, OPENCODE, etc.)
   └─ not sys.stdout.isatty() → 非交互式终端
2. 输出策略
   ├─ --json → print_json({"playbook": PLAYBOOK})
   ├─ agent 模式 → 直接写 PLAYBOOK 到 stdout (无装饰)
   └─ 人类交互模式 → err_console 输出介绍，Rich 渲染 Markdown，err_console 输出提示
```

关键位置：
- Agent 检测: `init.py:35-40`
- 环境变量列表: `init.py:13-26`

### 9.2 auth login 流程 (OAuth PKCE)

**文件**: `oauth.py`

```
1. PKCE 挑战生成
   ├─ code_verifier = secrets.token_urlsafe(64)
   └─ code_challenge = base64url(sha256(code_verifier))
2. 启动本地回调服务器 (127.0.0.1:随机端口)
3. 动态注册 OAuth 客户端 (Supabase /auth/v1/oauth/clients/register)
4. 构建授权 URL 并打开浏览器
5. 等待回调 (2分钟超时)
   ├─ 成功 → 获取 authorization code
   └─ 失败 → 输出错误到 stderr，exit 2
6. 用 code 交换 token (Supabase /auth/v1/oauth/token)
   ├─ grant_type=authorization_code
   ├─ code_verifier 用于 PKCE 验证
   └─ timeout=15s
7. 解析 token 响应，保存凭证到 ~/.minitest/credentials.json (0o600)
```

关键位置：
- PKCE 生成: `oauth.py:82-85`
- 回调服务器: `oauth.py:91-123`
- 客户端注册: `oauth.py:126`
- Token 交换: `oauth.py:165-177`
- 超时设置: `oauth.py:146-152`

### 9.3 run start 流程

**文件**: [run.py](../../../../external/anthropics/cwc-workshops/agent-decomposition/evals/run.py)

```
1. resolve_app() → 认证 + 解析 app_id
   ├─ require_auth(settings) → 加载 token
   └─ resolve_app_id(settings, app_flag) → --app 优先，其次 MINITEST_APP_ID
2. build_targets(ios_build, android_build, web) → 构建目标列表
3. 异步执行:
   ├─ async with ApiClient(settings) as client
   ├─ resolve_user_story_id(client, app_id, user_story)
   │  ├─ 是 UUID → 直接返回
   │  └─ 不是 UUID → GET /user-stories?page_size=100，大小写不敏感名称匹配
   ├─ POST /api/v1/apps/{app_id}/batches (CreateBatchRequest)
   └─ --watch=True → poll_run_status() 轮询
4. poll_run_status():
   ├─ 每 2 秒 GET /story-runs/{run_id}
   ├─ Rich spinner 显示状态到 stderr
   └─ 直到状态 in TERMINAL_STATUSES (completed/failed/cancelled)
5. 输出结果
   ├─ --json → print_json(run)
   └─ 否则 → display_run_result() 显示结果表格
```

关键位置：
- start 命令: [run.py:48-83](../../../../external/anthropics/cwc-workshops/agent-decomposition/evals/run.py#L48-L83)
- resolve_app: `run_helpers.py:57-65`
- resolve_user_story_id: `run_helpers.py:124-149`
- poll_run_status: `run_helpers.py:173-195`
- POLL_INTERVAL_SECONDS: `run_helpers.py:36`
- TERMINAL_STATUSES: `run_helpers.py:42`

### 9.4 batch 流程

**文件**: [batch.py](../../../../external/anthropics/claude-quickstarts/computer-use-best-practices/computer_use/tools/batch.py), [batch_helpers.py]

Batch 是多 user-story 的批量执行：

- `batch list` - 分页列出 batches，支持 status/result/commit/user-story 过滤、--all 获取所有页
- `batch get <id>` - 获取单个 batch 详情，包含 targets 统计表和 story runs 列表
- `batch cancel <id>` - 取消 batch 及其所有 pending/running story runs

关键位置：
- list_batches: [batch.py:47-106](../../../../external/anthropics/claude-quickstarts/computer-use-best-practices/computer_use/tools/batch.py#L47-L106)
- get_batch: [batch.py:109-171](../../../../external/anthropics/claude-quickstarts/computer-use-best-practices/computer_use/tools/batch.py#L109-L171)

### 9.5 app-knowledge update 流程

**文件**: `app_knowledge.py`

```
1. 参数校验
   ├─ 必须提供 --content 或 --content-file (不能同时)
   └─ 内容不能为空
2. --content-file → 读取文件内容 (UTF-8)
3. require_auth(settings)
4. PUT /api/v1/apps/{app_id}/app-knowledge {"content": "..."}
5. 输出
   ├─ --json → print_json(record)
   └─ 否则 → print_success + 输出版本号到 stdout
```

关键位置：
- 内容解析: `app_knowledge.py:128-145`
- update 命令: `app_knowledge.py:76-125`

### 9.6 apps create 流程 (含文件上传)

**文件**: `apps.py`

```
1. require_auth(settings)
2. 至少一个 --platform (ios/android/web)
3. 租户解析
   ├─ --tenant 指定 → 直接使用
   └─ 未指定 → fetch_user_tenants() 获取用户租户列表
      ├─ 单个租户 → 自动选择
      └─ 多个租户 → TTY 下提示选择 (err_console 输出)
4. create_app_request() → 调用 apps-manager API
   ├─ 有 --icon → client.upload_file() (300s 超时)
   └─ 无 icon → 普通 POST
5. 输出
   ├─ --json → print_json(created)
   └─ 否则 → print_success + 输出 app id 到 stdout
```

关键位置：
- create_app: `apps.py:97-193`
- 租户解析: `apps.py:163-169`

---

## 10. 配置管理

**文件**: [core/config.py](../../../../apps/prompt_extraction/config.py)

使用 pydantic-settings，自动从环境变量和 `.env` 文件加载配置：

```python
model_config = SettingsConfigDict(
    env_prefix="MINITEST_",
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore",
)
```

位置：[config.py:19-24](../../../../apps/prompt_extraction/config.py#L19-L24)

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|---------|--------|------|
| `api_url` | MINITEST_API_URL | `https://testing-service.app.minitap.ai` | testing-service 基地址 |
| `apps_manager_url` | MINITEST_APPS_MANAGER_URL | `https://apps-manager.app.minitap.ai` | apps-manager 基地址 |
| `integrations_url` | MINITEST_INTEGRATIONS_URL | `https://integrations.minitap.ai` | integrations 基地址 |
| `config_dir` | MINITEST_CONFIG_DIR | `~/.minitest` | 配置目录 |
| `token` | MINITEST_TOKEN | None | API 认证 token (优先级最高) |
| `api_key` | MINITEST_API_KEY | None | 租户级 API Key (SecretStr) |
| `app_id` | MINITEST_APP_ID | None | 默认应用 ID |
| `supabase_url` | MINITEST_SUPABASE_URL | `https://auth.minitap.ai` | Supabase OAuth URL |
| `supabase_publishable_key` | MINITEST_SUPABASE_PUBLISHABLE_KEY | (内置) | Supabase publishable key |

关键位置：[config.py:16-66](../../../../apps/prompt_extraction/config.py#L16-L66)

---

## 11. 数据模型设计

**基类**: [models/base.py](../../../../.agents/scripts/mdi/generators/base.py) - `CamelModel`，自动配置 camelCase 别名。

### 核心模型关系

```
CamelModel (base)
├── AppResponse
│   └── AppDetailResponse (extra=allow 兼容后端字段扩展)
├── AppListResponse { apps: list[AppResponse] }
├── TenantResponse
├── BatchStatus (StrEnum: pending/awaiting_build/running/completed/failed/cancelled)
├── BatchCounters
├── BatchTargetView
├── GitHubContextResponse (CI 触发信息)
├── CreateBatchRequest { user_story_ids?, targets?, commit_sha?, tag_name? }
├── BatchResponse { targets, story_runs, headline_status, github_context? }
├── BatchListItem (轻量，不含 story_runs)
├── BatchListResponse { items, total, page, page_size }
├── CriterionResult (验收标准结果)
├── PlatformRun (per-platform 执行状态: execution_state, verdict, counters)
├── StoryRunResponse { platforms, results }
└── StoryRunListResponse
```

### PlatformRun 模型演进

旧版使用平铺的 `ios_*`/`android_*` 字段，新版统一为 `platforms: list[PlatformRun]`，每个平台有独立的生命周期：
- `execution_state`: pending/running/completed/failed/blocked/skipped
- `verdict`: criticality-aware 结果
- `cancellation_requested_at`: 用户请求取消的时间戳

位置：`story_run.py:26-56`

---

## 12. 开发规范

### 12.1 代码质量工具链

| 工具 | 用途 | 配置位置 |
|------|------|---------|
| **ruff** | Lint + Format | [pyproject.toml:60-111](../../../../apps/ai-code-assistant/pyproject.toml#L60-L111) |
| **pyright** | 静态类型检查 | pyrightconfig.json |
| **pytest** | 单元测试 | [pyproject.toml:113-136](../../../../apps/ai-code-assistant/pyproject.toml#L113-L136) |

常用命令：
```bash
uv run ruff check .      # Lint
uv run ruff format .     # Format
uv run pyright           # Type check
uv run pytest            # Test
```

### 12.2 文件长度限制

**Keep files under 150 lines when possible**

位置：[AGENTS.md:44](../../../../external/multica-ai/multica/AGENTS.md#L44)

实现方式：将业务逻辑拆分到 `*_helpers.py` 文件中，主命令文件保持精简（如 run.py 190行，但核心逻辑在 run_helpers.py、run_display.py、run_targets.py）。

### 12.3 导入规范

- **绝对导入**（ruff 禁止相对导入）
  ```
  [tool.ruff.lint.flake8-tidy-imports]
  ban-relative-imports = "all"
  ```
  位置：[pyproject.toml:104-105](../../../../apps/ai-code-assistant/pyproject.toml#L104-L105)
- 导入顺序：标准库 → 第三方 → 本地导入
- 所有导入位于文件顶部

### 12.4 类型注解规范

- 使用 `X | None` 语法（而非 `Optional[X]`）
- Typer 参数使用 `Annotated[Type, ...]` 包装
- 枚举继承自 `str, Enum`（即 `StrEnum`）

位置：[AGENTS.md:45-47](../../../../external/multica-ai/multica/AGENTS.md#L45-L47)

### 12.5 命名规范

| 类型 | 规范 |
|------|------|
| 文件/模块 | `snake_case.py` |
| 类 | `PascalCase` |
| 函数/变量 | `snake_case` |
| 常量 | `UPPER_SNAKE_CASE` |
| 测试文件 | `test_*.py` |
| 测试函数 | `test_<action>_<scenario>` |

位置：[AGENTS.md:36-41](../../../../external/multica-ai/multica/AGENTS.md#L36-L41)

### 12.6 输出约定

- `--json` 模式：JSON 到 stdout，诊断到 stderr
- 非 `--json` 模式：Rich 人类友好表格到 stdout，诊断到 stderr
- 禁止交互式提示（所有输入通过 flags、env vars 或 stdin）

位置：[AGENTS.md:49-56](../../../../external/multica-ai/multica/AGENTS.md#L49-L56)

### 12.7 Ruff 配置详情

- line-length = 100
- indent-width = 4
- target-version = py312
- select = ["E", "F", "TID", "UP"] (pycodestyle, pyflakes, flake8-tidy-imports, pyupgrade)
- quote-style = "double"
- init_playbook.py 豁免 E501（行过长）

位置：[pyproject.toml:90-111](../../../../apps/ai-code-assistant/pyproject.toml#L90-L111)

### 12.8 Agent Skill 同步规范

CLI 命令变更时必须同步更新 Agent Skill 文档：

> When you add, remove, or change a CLI command/flag:
> 1. Update `repos/agent-skills/skills/minitest-cli/SKILL.md` in a paired PR
> 2. Update the Quick Reference table and any relevant sections

位置：[AGENTS.md:63-68](../../../../external/multica-ai/multica/AGENTS.md#L63-L68)

---

## 13. 关键设计模式总结

### 13.1 Typer Context 全局状态传递

通过 `typer.Context` 的动态属性传递全局状态：

```python
# main.py callback 中设置
ctx.json_mode = json
ctx.app_flag = app_id
ctx.settings = settings

# 各命令中读取
settings = typer.Context.settings
json_mode = typer.Context.json_mode
```

位置：[main.py:90-93](../../../../playground/chaos/libs/Nuitka/tests/distutils/example_3_dependencies_poetry_pyproject/src/main.py#L90-L93)

### 13.2 异步运行封装

`run_api_call()` 封装 `asyncio.run()` 并统一处理网络错误：

```python
def run_api_call[T](coro: Coroutine[Any, Any, T]) -> T:
    try:
        return asyncio.run(coro)
    except httpx.HTTPError as exc:
        print_error(f"Network error: {exc}")
        raise typer.Exit(code=EXIT_NETWORK_ERROR) from exc
```

位置：`run_helpers.py:110-116`

### 13.3 非阻塞更新检查

`check_for_updates()` 在 main callback 中调用，24小时缓存，不阻塞命令执行：

位置：[main.py:96](../../../../playground/chaos/libs/Nuitka/tests/distutils/example_3_dependencies_poetry_pyproject/src/main.py#L96)

### 13.4 统一错误处理

`handle_response_error()` 将 HTTP 状态码映射到退出码：
- 404 → exit 4 (Not Found)
- 500 + foreign key violation → exit 4
- 其他 4xx/5xx → exit 3 (Network/API Error)

位置：`run_helpers.py:92-107`
