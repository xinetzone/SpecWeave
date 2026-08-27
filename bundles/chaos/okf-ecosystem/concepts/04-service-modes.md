---
type: Concept
title: MCP/Chat/HTTP 三模服务架构
description: okf-kit 三种服务模式共享同一导航内核（list_directory/read_concept/search_bundle），涵盖 MCP 工具注册、Chat Agent 循环、HTTP API 路由、token 鉴权与 provider 抽象
tags: [okf, mcp, chat, http, fastapi, agent, provider, sse, token-auth]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: okf-kit-source
    resource: "/references/okf-kit-source.md"
    title: okf-kit 源码
  - id: facts-okf-kit
    resource: "/references/facts-okf-kit.md"
    title: okf-kit 事实清单
---

# MCP/Chat/HTTP 三模服务架构

okf-kit 对外提供三种交互服务模式——MCP（stdio 协议，供 AI IDE 调用）、Chat（CLI REPL，人机对话）、Serve（FastAPI HTTP + SSE，供前端消费）。这三种模式并非三套独立实现，而是共享同一组三个原子导航操作：`list_directory`、`read_concept`、`search_bundle`。「是否使用 LLM」被抽象为一个开关：provider 为 none 时走纯关键词检索，否则走 LLM 工具调用循环。

## 导航内核三原语

三个导航函数定义在 `bundle_nav.py` 中，是整个生态的「系统调用表」。

### list_directory

`list_directory(bundle_dir, path="/")` 返回排序后的目录条目列表 [F-255]：

```python
def list_directory(bundle_dir, path: str = "/") -> str:
    target = _safe(bundle_dir, path)
    entries = []
    for item in sorted(target.iterdir()):
        if item.name == STATE_DIRNAME:
            continue
        kind = "dir" if item.is_dir() else "file"
        entries.append(f"{kind}:  {item.name}")
    return "\n".join(entries)
```

输出格式为 `"dir:  <name>"` 或 `"file: <name>"`，排除 `.okf-kit` 目录。

### read_concept

`read_concept(bundle_dir, path)` 读取文件内容并截断至 `MAX_FILE_CHARS = 12000` 字符 [F-253][F-256]。这防止 LLM 上下文被过长文件撑爆。`_safe()` 函数使用 `.resolve()` 进行路径遍历防护，target 必须在 bundle 根目录内才返回 [F-254]。

### search_bundle

`search_bundle(bundle_dir, query, limit=5)` 对 pages 目录下所有 .md 文件进行关键词搜索 [F-257]：

```python
def search_bundle(bundle_dir, query: str, limit: int = 5) -> list[dict]:
    tokens = _TOKEN.findall(query.lower())
    results = []
    for md_file in bundle_dir.rglob("*.md"):
        # title 权重为 body 的 3 倍
        score = title_hits * 3 + body_hits
        results.append({"path": ..., "title": ..., "score": score, "snippet": ...})
    return sorted(results, key=lambda x: -x["score"])[:limit]
```

搜索是纯线性扫描，无倒排索引。title 命中权重为 body 的 3 倍，返回 path/title/score/snippet。

## MCP 模式

MCP（Model Context Protocol）模式通过 stdio 与 AI IDE（如支持 MCP 的编辑器）通信。`serve_mcp(names, *, all_=False)` 函数延迟导入 mcp 包 [F-103]，若未安装则输出安装提示 [F-101]。

### Bundle 解析

`_resolve_bundles(names, all_)` 确定要服务的 bundle 集合 [F-102]：`all_=True` 或 names 为空时，扫描 `bundles_dir().glob("*/.okf-kit/state.json")` 自动发现所有本地 bundle。

### 工具注册

创建 `Server("okf-kit")` 实例 [F-104]，注册四个工具：

| 工具名 | 参数 | 功能 |
|--------|------|------|
| `list_bundles` | 无 | 列出所有可用 bundle 名称 [F-105] |
| `list_directory` | `bundle`（string, required）、`path`（string, required） | 列出 bundle 内目录 [F-106] |
| `read_concept` | `bundle`（string, required）、`path`（string, required） | 读取概念文件内容 [F-107] |
| `search_bundle` | `bundle`（string, required）、`query`（string, required） | 关键词搜索 [F-108] |

### 分发逻辑

`@server.call_tool()` 装饰的异步函数调用 `_dispatch()` [F-109][F-110]：
- `list_bundles`：返回换行连接的排序 bundle 名
- `list_directory`：委托给 `bundle_nav.list_directory(d, path)`，path 默认 `/`
- `read_concept`：委托给 `bundle_nav.read_concept(d, path)`，path 默认 `/index.md`
- `search_bundle`：委托给 `bundle_nav.search_bundle(d, query, limit=5)`，结果 JSON 序列化

## Chat 模式

Chat 模式提供终端交互式 REPL，支持 LLM 工具调用和无 LLM 检索两种路径。

### Agent 循环

`ask(bundle_dir, question, provider, *, max_steps=MAX_STEPS)` 是 LLM 模式的核心 [F-125]。`MAX_STEPS = 16` [F-122] 是浏览步数上限而非 token 上限。

SYSTEM 常量定义了 agent 角色和导航策略 [F-123]，指示 LLM 使用 `list_directory(path)` 和 `read_concept(path)` 两个工具探索知识包。TOOLS 定义了两个 function 类型工具，每个工具有 name/description/parameters（含 path string 属性，required）[F-124]。

循环流程 [F-126][F-127][F-128]：
1. 首先调用 `read_concept(bundle_dir, "/index.md")` 获取根索引作为导航起点
2. 循环最多 max_steps 次，调用 `provider.complete(messages, TOOLS)`
3. 若 turn.tool_calls 为空，设置 answer 并 break
4. 对每个 tool_call：`read_concept` 调用 `read_concept(bundle_dir, path)`，其他调用 `list_directory(bundle_dir, path)`
5. 记录 steps 和 read_paths
6. 若循环结束 answer 仍为 None，追加 user 消息 "Stop exploring and answer from what you've read." 并再次调用 `provider.complete(messages, [])`（无工具）强制收尾

返回字典 `{"answer": answer or "", "steps": steps, "sources": read_paths}` [F-129]。

### 检索降级路径

无 LLM 时（provider 为 None），`retrieval.answer(bundle_dir, question, limit=3)` 提供纯关键词检索 [F-159][F-160]：调用 `search_bundle()`，无命中时返回固定提示消息，有命中时返回编号列表（含 title、path、snippet）。

### Provider 抽象

`make_provider(provider, model, base_url, api_key)` 工厂函数支持多种 LLM 后端 [F-148]：

**预设**（`_PRESETS` 字典）[F-138]：
| Provider | base_url | key_env | 默认模型 |
|----------|----------|---------|---------|
| `openai` | None（官方） | `OPENAI_API_KEY` | `gpt-4o-mini` |
| `ollama` | `http://localhost:11434/v1` | None | `llama3.1` |
| `openrouter` | `https://openrouter.ai/api/v1` | `OPENROUTER_API_KEY` | `openai/gpt-4o-mini` |

- `OpenAICompatProvider`：兼容 OpenAI API 的 provider（OpenAI、Ollama、OpenRouter、custom）[F-139][F-140]。其 `complete()` 调用 `chat.completions.create`，`assistant_message()` 和 `tool_result_message()` 处理消息格式 [F-141][F-142]。
- `AnthropicProvider`：使用 Anthropic Messages API [F-143]。`complete()` 分离 system 消息，调用 `messages.create(max_tokens=2048)`，遍历 content blocks 收集 text 和 tool_use [F-144][F-145]。消息格式与 OpenAI 不同（tool_result 在 user content 数组中）[F-146][F-147]。
- provider 为 None 或 `"none"` 时返回 None，触发检索降级路径 [F-149]。
- Ollama 模式下调用 `_detect_ollama_model()` 请求 `/api/tags`，优先使用 fallback 模型（若已安装），否则返回第一个已安装模型 [F-151]。

`describe_provider_error()` 将异常转换为用户友好的错误提示，处理 NotFound/Connection/Auth 等错误类型 [F-152]。

### 会话历史

`History` 类以 JSONL 格式持久化对话 [F-130]：
- 存储于 `chats_dir() / bundle_name / {session}.jsonl` [F-131]
- `append(role, content, meta)` 追加记录（含 ts、role、content，可选 meta）[F-132]
- `load()` 读取所有记录 [F-133]
- `History.latest(bundle_name)` 返回最新会话或 None（用于 `--resume`）[F-134]
- `History.list_sessions(bundle_name)` 返回 `(session_name, user_turn_count)` 列表（用于 `--history`）[F-135]

### REPL

`run_chat(name_or_dir, ...)` 是交互式入口 [F-153]：解析 bundle [F-154]，处理 `--history` [F-155]，创建 provider 和可选恢复历史 [F-156]，主循环中根据 provider 是否存在选择 `retrieval.answer` 或 `agent.ask` [F-157]。

## HTTP 模式

HTTP 模式通过 `okf serve` 启动 FastAPI 应用，提供 REST API 和 SSE 流式响应，供 Web 前端和桌面端消费。

### 应用工厂与鉴权

`create_app(token, ui_dir=None)` 创建 FastAPI 实例 [F-173]。`require_token(request)` 从 `Authorization: Bearer` 头或 `token` 查询参数获取 token，使用 `hmac.compare_digest` 进行恒定时间比较，失败抛出 401 [F-174]。

### API 路由全景

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/health` | 健康检查，返回 version/okf_home/api 版本 [F-175] |
| GET | `/api/status` | Provider 状态（provider/model/online）[F-176] |
| GET | `/api/registry` | 远程注册表（300秒缓存，线程池加载）[F-177] |
| GET | `/api/books` | 本地 bundle 列表 [F-178] |
| GET | `/api/books/{name}` | 单个 bundle 详情 [F-179] |
| POST | `/api/books/{name}/install` | SSE 安装（progress/done/error 事件）[F-180] |
| DELETE | `/api/books/{name}` | 删除 bundle 及其 chats [F-181] |
| GET | `/api/books/{name}/toc` | 目录树 [F-182] |
| GET | `/api/books/{name}/concept` | 概念内容（id 查询参数）[F-183] |
| GET | `/api/books/{name}/chats` | 会话列表 [F-184] |
| POST | `/api/books/{name}/chats` | 创建会话 [F-185] |
| GET | `/api/books/{name}/chats/{sid}` | 获取会话 [F-186] |
| DELETE | `/api/books/{name}/chats/{sid}` | 删除会话 [F-187] |
| POST | `/api/books/{name}/chats/{sid}/ask` | SSE 问答（token/sources/done 事件）[F-188] |
| GET | `/api/settings` | 获取设置 [F-189] |
| PUT | `/api/settings` | 保存设置（provider 白名单校验）[F-190] |
| POST | `/api/shutdown` | 延迟退出（timer 0.2s 后 os._exit）[F-191] |

### SSE 流式问答

`/ask` 端点接受 JSON body `{"question": "..."}`，返回 `StreamingResponse`（media_type `text/event-stream`）[F-188]。事件序列：
1. `token`：分块文本（由 `_chunks(text, size=24)` 生成器按约 24 字符分块）[F-196]
2. `sources`：来源信息（经 `reader.enrich_sources()` 丰富）
3. `done`：完成
4. 或 `error`：错误

`_run_ask()` 的 provider 分支逻辑与 CLI Chat 完全一致 [F-195]：provider 为 None 时调用 `retrieval.answer`，否则调用 `agent.ask`。

### Reader 层

`serve/reader.py` 在原子导航操作之上叠加了 UI 友好的视图层：
- `ordered_concepts(bundle_dir)`：遍历所有非保留 .md 文件，返回 `{id, title, resource}` 列表，按路径排序 [F-199]
- `build_toc(concepts)`：将扁平列表嵌套为树形结构，节点类型为 `"section"`（含 children）或 `"concept"`（含 id/title/resource），折叠单层公共前缀 [F-200]
- `concept_view(bundle_dir, cid, ordered)`：返回含 id/title/type/tags/resource/markdown/headings（level/text/id）/prev/next 的字典 [F-201]
- `enrich_sources()`：返回来源列表含 concept_id/title/section/anchor/snippet [F-202]
- `slug(text)`：GitHub 风格锚点生成 [F-198]

### 静态文件托管

`ui_dir` 存在且为目录时，挂载 `StaticFiles(directory=ui_dir, html=True)` 到 `/` [F-192]。这使得 FastAPI 同时在 `/` 提供 UI 和在 `/api` 提供 API，实现「单源无 CORS」。桌面端正是利用这一点。

### 异常处理

统一异常处理器返回 `{"error": {"code": code, "message": exc.detail}}` [F-193]，HTTP 状态码到错误码映射：400→bad_request、401→unauthorized、404→not_found、409→conflict、502→upstream。

### 服务启动

`serve(*, host, port, token, ui, parent_pid)` 函数 [F-203]：
- token 为 `"auto"` 时调用 `secrets.token_hex(16)` 生成 [F-204]
- port 为 0 时调用 `_free_port(host)` 发现空闲端口
- 打印 JSON 格式 ready 行 `{"event": "ready", "url": ..., "token": ..., "pid": ...}` [F-205]
- parent_pid 给定时启动 `_watch_parent` daemon 线程，每 2 秒检测父进程，失败时 `os._exit(0)` [F-206][F-207]
- 调用 `uvicorn.run(app, host=host, port=port, log_level="warning")` [F-206]

### 设置与密钥存储

`serve/settings.py` 管理持久化设置 [F-208]：
- 设置存储于 `~/.okf/settings.json`，默认 `{"provider": "none", "model": None, "base_url": None}` [F-209]
- `save_settings()` 写入设置（不含 api_key），api_key 非空时调用 `_store_key()` [F-210]
- 密钥优先通过 `keyring.set_password()` 存储到 OS 密钥链，失败时回退到 `~/.okf/.secrets.json`（权限设为 600）[F-211][F-212]
- `public_settings()` 返回 provider/model/base_url/has_key，不返回密钥本身 [F-213]

## 三模式对照

| 维度 | MCP | Chat (CLI) | Serve (HTTP) |
|------|-----|-----------|-------------|
| 协议 | stdio | 终端 REPL | HTTP + SSE |
| 导航原语 | 直接委托 | agent.ask / retrieval.answer | reader 视图层 + 原语 |
| LLM 支持 | 由 IDE 端 LLM 驱动 | 内置 provider 循环 | 内置 provider 循环 |
| 无 LLM 降级 | 不适用 | retrieval.answer | retrieval.answer |
| 会话持久化 | 由 IDE 管理 | JSONL History | JSONL History（通过 API） |
| 流式输出 | 不适用 | 终端输出 | SSE token 事件 |
| 鉴权 | 无（stdio 本地） | 无（本地进程） | Bearer token / query token |

三种模式共享的不仅是三个导航函数，还包括 provider 抽象、History 持久化、retrieval 降级路径。新增接入模式（如 Discord bot、Slack app）时，只需在协议层调用这三个原子操作，无需重写检索逻辑。

## 相关概念

- [OKF 知识包生态概览](/concepts/00-okf-overview.md)
- [Bundle 数据模型与语义边](/concepts/01-bundle-data-model.md)
- [桌面应用同进程架构与打包](/concepts/05-desktop-architecture.md)
- [CLI 使用示例](/examples/cli-usage.md)
