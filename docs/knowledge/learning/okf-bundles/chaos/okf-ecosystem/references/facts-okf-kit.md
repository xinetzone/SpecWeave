---
type: Facts
title: "okf-kit 事实清单"
---

# okf-kit 事实清单

> R阶段事实采集。源码路径：d:\AI\.chaos\libs\tests\okf-kit\
> 采集日期：2026-08-23

## 项目元信息

- F-001: 包 `okf_kit` 的 `__version__` 变量值为 `"0.3.3"` — 源码：`okf_kit/__init__.py:3`
- F-002: 模块文档字符串内容为 `"okf-kit — turn any website into a portable, agent-ready OKF bundle."` — 源码：`okf_kit/__init__.py:1`
- F-003: pyproject.toml 中 `[project] name` 值为 `"okf-kit"`，`version` 值为 `"0.3.3"` — 源码：`pyproject.toml:2-3`
- F-004: `requires-python` 值为 `">=3.10"` — 源码：`pyproject.toml:6`
- F-005: `license` 值为 `{ text = "Apache-2.0" }` — 源码：`pyproject.toml:7`
- F-006: 核心运行时依赖声明为 `httpx>=0.27`、`trafilatura>=1.8`、`lxml-html-clean>=0.1`、`selectolax>=0.3.21`、`pyyaml>=6.0` — 源码：`pyproject.toml:16-25`
- F-007: 可选依赖组 `js` 包含 `crawl4ai>=0.6.0`、`trafilatura>=1.8,<2.1` — 源码：`pyproject.toml:31`
- F-008: 可选依赖组 `chat` 包含 `openai>=1.60` — 源码：`pyproject.toml:33`
- F-009: 可选依赖组 `anthropic` 包含 `anthropic>=0.40` — 源码：`pyproject.toml:35`
- F-010: 可选依赖组 `enrich` 包含 `openai>=1.60` — 源码：`pyproject.toml:37`
- F-011: 可选依赖组 `mcp` 包含 `mcp>=1.2.0` — 源码：`pyproject.toml:39`
- F-012: 可选依赖组 `serve` 包含 `fastapi>=0.110`、`uvicorn>=0.27`、`keyring>=24` — 源码：`pyproject.toml:42`
- F-013: 可选依赖组 `all` 值为 `["okf-kit[js,chat,anthropic,enrich,mcp,serve]"]` — 源码：`pyproject.toml:43`
- F-014: 可选依赖组 `dev` 包含 `pytest>=7.0`、`pytest-asyncio>=0.23`、`ruff>=0.6`、`build>=1.0` — 源码：`pyproject.toml:44`
- F-015: 控制台脚本入口点声明为 `okf = "okf_kit.cli:main"` — 源码：`pyproject.toml:53`
- F-016: 构建系统后端为 `setuptools.build_meta`，要求 `setuptools>=68` — 源码：`pyproject.toml:56-57`
- F-017: 包发现配置为 `include = ["okf_kit*"]` — 源码：`pyproject.toml:60`
- F-018: pytest 配置 `asyncio_mode = "auto"`，`testpaths = ["tests"]` — 源码：`pyproject.toml:63-64`
- F-019: ruff 配置 `line-length = 100`，`target-version = "py310"` — 源码：`pyproject.toml:67-68`
- F-020: 项目 Homepage/Repository/Issues URL 均为 `https://github.com/vinodborole/okf-kit` — 源码：`pyproject.toml:47-49`
- F-021: Specification URL 指向 `https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md` — 源码：`pyproject.toml:50`

## CLI 命令结构

- F-030: 函数 `_build_parser()` 返回 `argparse.ArgumentParser` 实例，`prog="okf"` — 源码：`okf_kit/cli.py:22`
- F-031: 子解析器 `dest="command"`，`required=True`，`metavar="<command>"` — 源码：`okf_kit/cli.py:28`
- F-032: 全局参数 `--version`，`action="version"`，版本格式 `f"%(prog)s {__version__}"` — 源码：`okf_kit/cli.py:27`
- F-033: 子命令 `build` 接受位置参数 `url`（Root URL） — 源码：`okf_kit/cli.py:30-31`
- F-034: `build` 选项 `-o/--output`（DIR）、`--max-depth`（int，默认3）、`--max-pages`（int，默认200）、`--js`（store_true）、`--no-robots`（store_true） — 源码：`okf_kit/cli.py:32-36`
- F-035: `build` 选项 `--path-prefix`（PATH）、`--all-paths`（store_true）、`--enrich`（store_true）、`--enrich-model`（默认 `"gpt-4o-mini"`）、`-v/--verbose`（store_true） — 源码：`okf_kit/cli.py:37-50`
- F-036: 子命令 `validate` 接受位置参数 `directory`，选项 `--quiet`（store_true） — 源码：`okf_kit/cli.py:52-54`
- F-037: 子命令 `zip` 接受位置参数 `directory`，选项 `-o/--output`（FILE） — 源码：`okf_kit/cli.py:56-58`
- F-038: 子命令 `sync` 接受位置参数 `directory`，选项 `--max-depth`（int，默认None）、`--max-pages`（int，默认None）、`--force`（store_true） — 源码：`okf_kit/cli.py:60-67`
- F-039: 子命令 `list` 选项 `--remote`（store_true）、`--registry` — 源码：`okf_kit/cli.py:69-71`
- F-040: 子命令 `get` 接受位置参数 `name`，选项 `--registry`、`--yes/-y`（store_true） — 源码：`okf_kit/cli.py:73-76`
- F-041: 子命令 `chat` 接受位置参数 `bundle`，选项 `--provider`、`--model`、`--base-url`、`--trace`（store_true）、`--resume`（store_true）、`--history`（store_true） — 源码：`okf_kit/cli.py:78-85`
- F-042: 子命令 `visualize` 接受位置参数 `directory`，选项 `-o/--output`（FILE） — 源码：`okf_kit/cli.py:87-89`
- F-043: 子命令 `serve-mcp` 接受位置参数 `names`（`nargs="*"`），选项 `--all`（store_true） — 源码：`okf_kit/cli.py:91-93`
- F-044: 子命令 `serve` 选项 `--host`（默认 `"127.0.0.1"`）、`--port`（int，默认0）、`--token`（默认 `"auto"`）、`--ui`（默认None）、`--parent-pid`（int，默认None） — 源码：`okf_kit/cli.py:95-100`
- F-045: 函数 `main(argv: list[str] | None = None) -> int` 为 CLI 入口 — 源码：`okf_kit/cli.py:109`
- F-046: `main` 中 `build` 命令调用 `crawl.build_bundle()`，参数包含 `url`、`output`、`max_depth`、`max_pages`、`js`、`respect_robots`（值为 `not args.no_robots`）、`path_prefix`、`all_paths`、`verbose` — 源码：`okf_kit/cli.py:120-133`
- F-047: `main` 中 `build` 成功且 `args.enrich` 为真时，调用 `enrich.enrich_bundle(target, model=args.enrich_model)` — 源码：`okf_kit/cli.py:134-141`
- F-048: `main` 中 `validate` 命令调用 `okf.validate_bundle(bundle_dir_arg(args.directory), quiet=args.quiet)`，返回 0 或 3 — 源码：`okf_kit/cli.py:142-146`
- F-049: `main` 中 `zip` 命令调用 `okf.zip_bundle(bundle_dir_arg(args.directory), output=args.output)` — 源码：`okf_kit/cli.py:147-152`
- F-050: `main` 中 `sync` 命令调用 `sync.sync_bundle()`，参数为 `directory`、`max_depth`、`max_pages`、`force` — 源码：`okf_kit/cli.py:153-162`
- F-051: `main` 中 `list` 命令调用 `registry.cmd_list(remote=args.remote, registry=args.registry)` — 源码：`okf_kit/cli.py:163-166`
- F-052: `main` 中 `get` 命令调用 `registry.cmd_get(args.name, registry=args.registry, yes=args.yes)` — 源码：`okf_kit/cli.py:167-170`
- F-053: `main` 中 `chat` 命令调用 `chat.repl.run_chat()`，参数为 `bundle`、`provider`、`model`、`base_url`、`trace`、`resume`、`show_history` — 源码：`okf_kit/cli.py:171-182`
- F-054: `main` 中 `visualize` 命令调用 `visualize.visualize(bundle_dir_arg(args.directory), output=args.output)` — 源码：`okf_kit/cli.py:183-188`
- F-055: `main` 中 `serve-mcp` 命令调用 `mcp.serve_mcp(args.names, all_=args.all)` — 源码：`okf_kit/cli.py:189-192`
- F-056: `main` 中 `serve` 命令调用 `serve.run.serve()`，参数为 `host`、`port`、`token`、`ui`、`parent_pid` — 源码：`okf_kit/cli.py:193-197`
- F-057: 模块级变量 `_LATER: dict[str, str] = {}` 初始为空字典 — 源码：`okf_kit/cli.py:19`

## 核心模块与类（okf / writer / mapper / model）

- F-060: 模块 `okf.py` 定义常量 `RESERVED = {"index.md", "log.md"}` — 源码：`okf_kit/okf.py:22`
- F-061: 函数 `frontmatter(fields: dict) -> str` 调用 `yaml.safe_dump(clean, sort_keys=False, allow_unicode=True)`，过滤值为 None/空字符串/空列表的字段 — 源码：`okf_kit/okf.py:25-28`
- F-062: 函数 `dodge_reserved(rel: PurePosixPath) -> PurePosixPath` 将 `index.md` 重命名为 `home.md`，将 `log.md` 重命名为 `history.md` — 源码：`okf_kit/okf.py:31-37`
- F-063: 函数 `write_directory_indexes(bundle_dir: Path, entries: dict[PurePosixPath, str]) -> int` 遍历 entries，按目录分组，写入 `index.md`，包含子目录链接和文件链接 — 源码：`okf_kit/okf.py:40-66`
- F-064: 函数 `write_root_index(bundle_dir: Path, root_url: str | None, page_count: int) -> None` 写入根目录 `index.md`，包含标题、pages 链接 — 源码：`okf_kit/okf.py:69-76`
- F-065: 函数 `validate_bundle(directory, *, quiet: bool = False) -> bool` 遍历 `bundle_dir.rglob("*.md")`，跳过 STATE_DIRNAME 和 RESERVED 文件，检查 frontmatter 是否存在及 `type` 字段是否非空 — 源码：`okf_kit/okf.py:79-112`
- F-066: 函数 `zip_bundle(directory, *, output=None) -> Path` 使用 `zipfile.ZipFile` 打包，压缩方式为 `ZIP_DEFLATED`，顶层文件夹名为 bundle 目录名 — 源码：`okf_kit/okf.py:115-132`
- F-067: 模块 `writer.py` 导入 `STATE_DIRNAME`、`STATE_FILENAME`、`url_to_relpath`、`Page`、`PageRecord`、`content_hash`、`utcnow_iso`、`dodge_reserved`、`frontmatter`、`write_directory_indexes`、`write_root_index` — 源码：`okf_kit/writer.py:23-31`
- F-068: 函数 `bundle_path_for(url: str) -> str` 调用 `dodge_reserved(url_to_relpath(url).with_suffix(".md"))`，返回 `str(PurePosixPath("pages") / rel)` — 源码：`okf_kit/writer.py:34-37`
- F-069: 函数 `write_concept(bundle_dir: Path, page: Page, timestamp: str) -> PageRecord | None`，body 为空时返回 None；写入 frontmatter 字段 `type="Web Page"`、`title`、`description`、`resource`、`timestamp`；正文后追加 `# Citations` 段落 — 源码：`okf_kit/writer.py:40-61`
- F-070: 函数 `compute_edges(pages, present_paths: set[str]) -> list[list[str]]`，优先使用 `page.content_links`，当其为 None 时回退到 `page.links`；返回 `[src_path, dst_path]` 对列表 — 源码：`okf_kit/writer.py:64-77`
- F-071: 函数 `prune_empty_dirs(root: Path) -> None` 逆序遍历目录，删除空子目录 — 源码：`okf_kit/writer.py:80-83`
- F-072: 函数 `append_log(bundle_dir: Path, lines: list[str]) -> None` 追加日志到 `log.md`，按日期分节 — 源码：`okf_kit/writer.py:86-90`
- F-073: 函数 `write_bundle_meta(bundle_dir, records, *, root_url, config, log_lines, last_sync=None, edges=None)` 调用 `write_directory_indexes`、`write_root_index`、`append_log`，写入 `.okf-kit/state.json` — 源码：`okf_kit/writer.py:93-132`
- F-074: state.json 包含字段 `generator`（值 `"okf-kit"`）、`okf_version`（值 `"0.1"`）、`root_url`、`updated_at`、`config`、`page_count`、`pages`（列表，每项含 path/url/title/hash）、`edges` — 源码：`okf_kit/writer.py:115-127`
- F-075: 模块 `mapper.py` 定义 `_PAGE_EXTENSIONS = {".html", ".htm", ".php", ".asp", ".aspx", ".jsp"}` — 源码：`okf_kit/mapper.py:16`
- F-076: 正则 `_UNSAFE_CHARS = re.compile(r'[<>:"\\|?*\x00-\x1f]')` — 源码：`okf_kit/mapper.py:17`
- F-077: 函数 `normalize_url(url: str) -> str` 去除 fragment，去除尾部斜杠，保留 query string — 源码：`okf_kit/mapper.py:20-27`
- F-078: 函数 `_sanitize_segment(segment: str) -> str` 将不安全字符替换为 `-`，strip `.` 和空格，空值返回 `"unnamed"` — 源码：`okf_kit/mapper.py:30-32`
- F-079: 函数 `url_to_relpath(url: str) -> PurePosixPath`，根路径返回 `PurePosixPath("index")`，去除页面扩展名，query string 生成 sha1 前8位后缀 `-q-<digest>` — 源码：`okf_kit/mapper.py:35-59`
- F-080: 模块 `model.py` 定义正则 `_PILCROW = re.compile(r"\s*¶")` 和 `_EXTRA_BLANKS = re.compile(r"\n{3,}")` — 源码：`okf_kit/model.py:10-11`
- F-081: 函数 `content_hash(markdown: str) -> str` 返回 `hashlib.sha256(markdown.encode("utf8")).hexdigest()` — 源码：`okf_kit/model.py:14-18`
- F-082: 函数 `clean_markdown(md: str) -> str` 移除 ¶ 符号，将3个以上连续换行替换为2个，strip 首尾空白 — 源码：`okf_kit/model.py:21-26`
- F-083: 函数 `utcnow_iso() -> str` 返回 `datetime.now(timezone.utc).isoformat()` — 源码：`okf_kit/model.py:57-58`

## 数据模型

- F-090: 数据类 `Page` 使用 `@dataclass` 装饰器 — 源码：`okf_kit/model.py:29`
- F-091: `Page` 字段：`url: str`、`title: str | None`、`markdown: str`、`description: str | None = None` — 源码：`okf_kit/model.py:33-36`
- F-092: `Page` 字段：`links: list[str] = field(default_factory=list)` — 源码：`okf_kit/model.py:39`
- F-093: `Page` 字段：`content_links: list[str] | None = None` — 源码：`okf_kit/model.py:43`
- F-094: `Page` 字段：`depth: int = 0` — 源码：`okf_kit/model.py:44`
- F-095: 数据类 `PageRecord` 使用 `@dataclass` 装饰器 — 源码：`okf_kit/model.py:47`
- F-096: `PageRecord` 字段：`path: str`、`url: str`、`title: str | None`、`content_hash: str` — 源码：`okf_kit/model.py:51-54`

## MCP 服务接口

- F-100: 模块 `mcp.py` 导入 `list_directory`、`read_concept`、`search_bundle`、`bundles_dir`、`resolve_bundle` — 源码：`okf_kit/mcp.py:14-16`
- F-101: 常量 `_INSTALL_HINT = "MCP support needs the extra:  pip install 'okf-kit[mcp]'"` — 源码：`okf_kit/mcp.py:18`
- F-102: 函数 `_resolve_bundles(names: list[str], all_: bool) -> dict[str, Path]`，`all_` 为真或 names 为空时扫描 `bundles_dir().glob("*/.okf-kit/state.json")` — 源码：`okf_kit/mcp.py:21-32`
- F-103: 函数 `serve_mcp(names: list[str], *, all_: bool = False) -> int`，延迟导入 `mcp.server.Server`、`mcp.server.stdio.stdio_server`、`mcp.types.TextContent`、`mcp.types.Tool` — 源码：`okf_kit/mcp.py:35-41`
- F-104: 创建 `Server("okf-kit")` 实例 — 源码：`okf_kit/mcp.py:47`
- F-105: 注册 MCP 工具 `list_bundles`，inputSchema 为空 properties 对象 — 源码：`okf_kit/mcp.py:52-53`
- F-106: 注册 MCP 工具 `list_directory`，参数 `bundle`（string）、`path`（string），两者均 required — 源码：`okf_kit/mcp.py:54-57`
- F-107: 注册 MCP 工具 `read_concept`，参数 `bundle`（string）、`path`（string），两者均 required — 源码：`okf_kit/mcp.py:58-61`
- F-108: 注册 MCP 工具 `search_bundle`，参数 `bundle`（string）、`query`（string），两者均 required — 源码：`okf_kit/mcp.py:62-65`
- F-109: `@server.call_tool()` 装饰的异步函数 `_call(name: str, arguments: dict) -> list["TextContent"]` 调用 `_dispatch()` — 源码：`okf_kit/mcp.py:68-70`
- F-110: 函数 `_dispatch(bundles: dict[str, Path], name: str, args: dict) -> str`，`list_bundles` 返回换行连接的排序 bundle 名；`list_directory` 调用 `list_directory(d, args.get("path", "/"))`；`read_concept` 调用 `read_concept(d, args.get("path", "/index.md"))`；`search_bundle` 调用 `json.dumps(search_bundle(d, args.get("query", ""), limit=5), indent=2)` — 源码：`okf_kit/mcp.py:88-102`

## Chat 模块

- F-120: 模块 `chat/__init__.py` 文档字符串为 `"Chat with a bundle (M3): providers, REPL, local history."` — 源码：`okf_kit/chat/__init__.py:1`
- F-121: 模块 `chat/agent.py` 导入 `list_directory`、`read_concept` — 源码：`okf_kit/chat/agent.py:12`
- F-122: 常量 `MAX_STEPS = 16` — 源码：`okf_kit/chat/agent.py:14`
- F-123: 常量 `SYSTEM` 为多行字符串，定义 agent 角色和导航策略，包含 `list_directory(path)` 和 `read_concept(path)` 工具说明 — 源码：`okf_kit/chat/agent.py:16-29`
- F-124: 常量 `TOOLS` 为列表，包含两个 function 类型工具定义：`list_directory` 和 `read_concept`，每个工具均有 `name`、`description`、`parameters`（含 `path` string 属性，required） — 源码：`okf_kit/chat/agent.py:31-56`
- F-125: 函数 `ask(bundle_dir, question: str, provider, *, max_steps: int = MAX_STEPS) -> dict`，首先调用 `read_concept(bundle_dir, "/index.md")` 获取根索引 — 源码：`okf_kit/chat/agent.py:59-66`
- F-126: `ask` 函数循环最多 `max_steps` 次，调用 `provider.complete(messages, TOOLS)`；若 `turn.tool_calls` 为空则设置 answer 并 break — 源码：`okf_kit/chat/agent.py:71-76`
- F-127: `ask` 函数对每个 tool_call，`read_concept` 调用 `read_concept(bundle_dir, path)`，其他调用 `list_directory(bundle_dir, path)`；记录 steps 和 read_paths — 源码：`okf_kit/chat/agent.py:77-86`
- F-128: `ask` 函数在 answer 为 None 时追加 user 消息 `"Stop exploring and answer from what you've read."` 并再次调用 `provider.complete(messages, [])` — 源码：`okf_kit/chat/agent.py:88-90`
- F-129: `ask` 返回字典 `{"answer": answer or "", "steps": steps, "sources": read_paths}` — 源码：`okf_kit/chat/agent.py:92`
- F-130: 类 `History` 定义于 `chat/history.py`，方法 `__init__(self, bundle_name: str, session: str | None = None)` — 源码：`okf_kit/chat/history.py:15-16`
- F-131: `History.__init__` 设置 `self.dir = chats_dir() / bundle_name`，创建目录；session 给定时 `self.path = self.dir / f"{session}.jsonl"`，否则使用 UTC 时间戳替换冒号为短横线 — 源码：`okf_kit/chat/history.py:17-22`
- F-132: `History.append(self, role: str, content: str, meta: dict | None = None) -> None` 以 JSONL 格式追加记录，包含 `ts`、`role`、`content`，可选 `meta` — 源码：`okf_kit/chat/history.py:24-29`
- F-133: `History.load(self) -> list[dict]` 读取 JSONL 文件，逐行 `json.loads` — 源码：`okf_kit/chat/history.py:31-34`
- F-134: `@classmethod` 方法 `History.latest(cls, bundle_name: str) -> "History | None"` 返回最新的 jsonl 会话或 None — 源码：`okf_kit/chat/history.py:36-42`
- F-135: `@classmethod` 方法 `History.list_sessions(cls, bundle_name: str) -> list[tuple[str, int]]` 返回 `(session_name, user_turn_count)` 元组列表 — 源码：`okf_kit/chat/history.py:44-50`
- F-136: 数据类 `ToolCall` 使用 `@dataclass`，字段 `id: str`、`name: str`、`arguments: dict` — 源码：`okf_kit/chat/providers.py:28-32`
- F-137: 数据类 `Turn` 使用 `@dataclass`，字段 `text: str | None = None`、`tool_calls: list[ToolCall] = field(default_factory=list)` — 源码：`okf_kit/chat/providers.py:35-38`
- F-138: 字典 `_PRESETS` 包含三个键：`openai`（base_url=None，key_env=`OPENAI_API_KEY`，default_model=`gpt-4o-mini`）、`ollama`（base_url=`http://localhost:11434/v1`，key_env=None，default_model=`llama3.1`）、`openrouter`（base_url=`https://openrouter.ai/api/v1`，key_env=`OPENROUTER_API_KEY`，default_model=`openai/gpt-4o-mini`） — 源码：`okf_kit/chat/providers.py:20-25`
- F-139: 类 `OpenAICompatProvider`，`__init__(self, model: str, base_url: str | None, api_key: str)` 延迟导入 `openai.OpenAI`，创建 `self._client = OpenAI(base_url=base_url, api_key=api_key)` — 源码：`okf_kit/chat/providers.py:41-48`
- F-140: `OpenAICompatProvider.complete(self, messages: list[dict], tools: list[dict]) -> Turn` 调用 `self._client.chat.completions.create(model=self.model, messages=messages, tools=tools or None)` — 源码：`okf_kit/chat/providers.py:50-59`
- F-141: `OpenAICompatProvider.assistant_message(self, turn: Turn) -> dict` 构造 assistant 消息字典，tool_calls 存在时包含 `id`、`type="function"`、`function`（name 和 arguments JSON 字符串） — 源码：`okf_kit/chat/providers.py:61-69`
- F-142: `@staticmethod` 方法 `OpenAICompatProvider.tool_result_message(call: ToolCall, content: str) -> dict` 返回 `{"role": "tool", "tool_call_id": call.id, "content": content}` — 源码：`okf_kit/chat/providers.py:71-73`
- F-143: 类 `AnthropicProvider`，`__init__(self, model: str, api_key: str)` 延迟导入 `anthropic.Anthropic`，设置 `self._system = None` — 源码：`okf_kit/chat/providers.py:76-84`
- F-144: `AnthropicProvider.complete` 调用 `_split_system(messages)` 分离 system 消息，调用 `self._client.messages.create(model=self.model, max_tokens=2048, system=system or "", messages=msgs, tools=atools or [])` — 源码：`okf_kit/chat/providers.py:86-95`
- F-145: `AnthropicProvider.complete` 遍历 `resp.content`，`block.type == "text"` 时收集文本，`block.type == "tool_use"` 时构造 `ToolCall(id=block.id, name=block.name, arguments=dict(block.input))` — 源码：`okf_kit/chat/providers.py:96-102`
- F-146: `AnthropicProvider.assistant_message` 返回 `{"role": "assistant", "content": [...]}`，content 列表包含 text 和 tool_use 类型块 — 源码：`okf_kit/chat/providers.py:104-110`
- F-147: `@staticmethod` 方法 `AnthropicProvider.tool_result_message` 返回 `{"role": "user", "content": [{"type": "tool_result", "tool_use_id": call.id, "content": content}]}` — 源码：`okf_kit/chat/providers.py:112-115`
- F-148: 函数 `make_provider(provider: str | None, model: str | None, base_url: str | None, api_key: str | None = None)` — 源码：`okf_kit/chat/providers.py:118-119`
- F-149: `make_provider` 中 provider 为 None 或 `"none"` 时返回 None；provider 为 `"anthropic"` 时使用 `ANTHROPIC_API_KEY` 环境变量或传入 api_key，返回 `AnthropicProvider(model or "claude-sonnet-5", key)` — 源码：`okf_kit/chat/providers.py:125-131`
- F-150: `make_provider` 中 provider 在 `_PRESETS` 或为 `"custom"` 时，构造 `OpenAICompatProvider`；ollama 时 key 默认为 `"ollama"`，并调用 `_detect_ollama_model` — 源码：`okf_kit/chat/providers.py:132-144`
- F-151: 函数 `_detect_ollama_model(base_url: str, fallback: str) -> str` 请求 `<base>/api/tags`，优先返回 fallback 模型（若已安装），否则返回第一个已安装模型 — 源码：`okf_kit/chat/providers.py:148-159`
- F-152: 函数 `describe_provider_error(exc: Exception, provider: str | None, model: str | None) -> str` 根据异常类型名和消息内容返回错误提示字符串，处理 NotFound/Conn/Auth 等错误 — 源码：`okf_kit/chat/providers.py:162-182`
- F-153: 函数 `run_chat(name_or_dir: str, *, provider=None, model=None, base_url=None, trace=False, resume=False, show_history=False) -> int` 定义于 `chat/repl.py` — 源码：`okf_kit/chat/repl.py:13-22`
- F-154: `run_chat` 调用 `resolve_bundle(name_or_dir)` 解析 bundle 目录，取 `Path(bundle_dir).name` 为 bundle_name — 源码：`okf_kit/chat/repl.py:23-24`
- F-155: `run_chat` 中 `show_history` 为真时调用 `History.list_sessions(bundle_name)` 并打印后返回 0 — 源码：`okf_kit/chat/repl.py:26-32`
- F-156: `run_chat` 调用 `make_provider(provider, model, base_url)` 创建 provider，`resume` 为真时调用 `History.latest(bundle_name)` — 源码：`okf_kit/chat/repl.py:34-37`
- F-157: `run_chat` 主循环中，provider 为 None 时调用 `retrieval.answer(bundle_dir, question)`，否则调用 `agent.ask(bundle_dir, question, prov)` — 源码：`okf_kit/chat/repl.py:56-59`
- F-158: `run_chat` 异常时调用 `describe_provider_error(exc, provider, getattr(prov, "model", model))` — 源码：`okf_kit/chat/repl.py:60-62`
- F-159: 模块 `chat/retrieval.py` 导入 `search_bundle` — 源码：`okf_kit/chat/retrieval.py:13`
- F-160: 函数 `answer(bundle_dir, question: str, *, limit: int = 3) -> dict` 调用 `search_bundle(bundle_dir, question, limit=limit)`，无命中时返回固定提示消息；有命中时返回编号列表含 title、path、snippet — 源码：`okf_kit/chat/retrieval.py:16-35`

## Serve/Web 模块

- F-170: 模块 `serve/__init__.py` 文档字符串说明 `okf serve` 为本地 HTTP API，需要 `[serve]` extra — 源码：`okf_kit/serve/__init__.py:1-4`
- F-171: 模块 `serve/app.py` 常量 `_API = "0"` — 源码：`okf_kit/serve/app.py:29`
- F-172: 模块级变量 `_registry_cache: dict = {"at": 0.0, "entries": None}`，`_REGISTRY_TTL = 300` — 源码：`okf_kit/serve/app.py:30-31`
- F-173: 函数 `create_app(token: str, ui_dir: str | None = None)` 延迟导入 fastapi 组件，创建 `FastAPI(title="okf serve", version=__version__)` — 源码：`okf_kit/serve/app.py:34-39`
- F-174: 内部函数 `require_token(request: Request)` 从 `Authorization: Bearer` 头或 `token` 查询参数获取 token，使用 `hmac.compare_digest` 比较，失败时抛出 401 — 源码：`okf_kit/serve/app.py:41-48`
- F-175: 路由 `GET /api/health` 返回 `{"ok": True, "version": __version__, "okf_home": str(home_dir()), "api": _API}` — 源码：`okf_kit/serve/app.py:56-58`
- F-176: 路由 `GET /api/status` 返回 `{"provider": s["provider"], "model": s["model"], "online": _provider_online(s)}` — 源码：`okf_kit/serve/app.py:60-63`
- F-177: 路由 `GET /api/registry` 为 async 函数，使用 `run_in_threadpool(load_registry, DEFAULT_REGISTRY)` 加载注册表，带 300 秒缓存；返回 entries 列表含 name/title/source_url/publisher/category/tag/pages/license/description/installed 字段 — 源码：`okf_kit/serve/app.py:66-91`
- F-178: 路由 `GET /api/books` 返回 `[_book_view(b["name"]) for b in local_bundles()]` — 源码：`okf_kit/serve/app.py:94-96`
- F-179: 路由 `GET /api/books/{name}` 调用 `_book_view(name)`，不存在时抛出 404 — 源码：`okf_kit/serve/app.py:98-103`
- F-180: 路由 `POST /api/books/{name}/install` 返回 `StreamingResponse`，media_type 为 `"text/event-stream"`；SSE 事件顺序为 `progress`（downloading/extracting/validating）、`done` 或 `error` — 源码：`okf_kit/serve/app.py:105-125`
- F-181: 路由 `DELETE /api/books/{name}` 删除 bundle 目录和对应 chats 目录，返回 `{"removed": True}` — 源码：`okf_kit/serve/app.py:127-138`
- F-182: 路由 `GET /api/books/{name}/toc` 调用 `reader.build_toc(reader.ordered_concepts(d))` — 源码：`okf_kit/serve/app.py:141-144`
- F-183: 路由 `GET /api/books/{name}/concept` 接受查询参数 `id`，调用 `reader.concept_view(d, id.lstrip("/"), reader.ordered_concepts(d))` — 源码：`okf_kit/serve/app.py:146-152`
- F-184: 路由 `GET /api/books/{name}/chats` 调用 `_list_chats(name)` — 源码：`okf_kit/serve/app.py:155-157`
- F-185: 路由 `POST /api/books/{name}/chats` 创建 `History(name)` 实例，返回 `{"id": h.path.stem, "title": "New chat"}` — 源码：`okf_kit/serve/app.py:159-162`
- F-186: 路由 `GET /api/books/{name}/chats/{sid}` 调用 `_get_chat(name, sid)` — 源码：`okf_kit/serve/app.py:164-166`
- F-187: 路由 `DELETE /api/books/{name}/chats/{sid}` 删除 jsonl 文件，返回 `{"removed": True}` — 源码：`okf_kit/serve/app.py:168-174`
- F-188: 路由 `POST /api/books/{name}/chats/{sid}/ask` 接受 JSON body 含 `question` 字段，返回 SSE StreamingResponse；事件顺序为 `token`（分块文本）、`sources`、`done` 或 `error` — 源码：`okf_kit/serve/app.py:176-195`
- F-189: 路由 `GET /api/settings` 返回 `settings_mod.public_settings()` — 源码：`okf_kit/serve/app.py:198-200`
- F-190: 路由 `PUT /api/settings` 接受 JSON body，provider 限制为 `"none"/"ollama"/"openai"/"openrouter"/"anthropic"/"custom"`，调用 `settings_mod.save_settings()` — 源码：`okf_kit/serve/app.py:202-209`
- F-191: 路由 `POST /api/shutdown` 使用 `threading.Timer(0.2, lambda: os._exit(0))` 延迟退出 — 源码：`okf_kit/serve/app.py:211-216`
- F-192: `ui_dir` 存在且为目录时，挂载 `StaticFiles(directory=ui_dir, html=True)` 到 `/` — 源码：`okf_kit/serve/app.py:219-222`
- F-193: 异常处理器 `@app.exception_handler(HTTPException)` 返回统一格式 `{"error": {"code": code, "message": exc.detail}}`，code 映射 400→bad_request、401→unauthorized、404→not_found、409→conflict、502→upstream — 源码：`okf_kit/serve/app.py:224-229`
- F-194: 函数 `_book_view(name: str) -> dict | None` 读取 state.json，返回字典含 name/title/source_url/tag/pages/size_bytes/synced_at/conformant/chat_count — 源码：`okf_kit/serve/app.py:245-265`
- F-195: 函数 `_run_ask(bundle, name, sid, question, s: dict) -> dict`，provider 为 None 时调用 `retrieval.answer`，否则调用 `agent.ask`；调用 `reader.enrich_sources` 丰富来源；写入 History；返回 answer/sources/message — 源码：`okf_kit/serve/app.py:309-320`
- F-196: 函数 `_chunks(text: str, size: int = 24)` 为生成器，按空格分词，每 24 字符左右 yield 一块 — 源码：`okf_kit/serve/app.py:352-363`
- F-197: 模块 `serve/reader.py` 定义正则 `_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*$")` 和 `_TOKEN = re.compile(r"[a-z0-9]{2,}")` — 源码：`okf_kit/serve/reader.py:16-17`
- F-198: 函数 `slug(text: str) -> str` 将文本转为 GitHub 风格锚点：小写、去除非单词字符、空格和下划线替换为短横线 — 源码：`okf_kit/serve/reader.py:20-22`
- F-199: 函数 `ordered_concepts(bundle_dir) -> list[dict]` 遍历所有非保留 .md 文件，返回 `{id, title, resource}` 列表，按路径排序 — 源码：`okf_kit/serve/reader.py:25-41`
- F-200: 函数 `build_toc(concepts: list[dict]) -> list[dict]` 将 concepts 嵌套为树形结构，节点类型为 `"section"`（含 children）或 `"concept"`（含 id/title/resource）；折叠单层公共前缀 — 源码：`okf_kit/serve/reader.py:44-67`
- F-201: 函数 `concept_view(bundle_dir, cid: str, ordered: list[dict]) -> dict | None` 返回字典含 id/title/type/tags/resource/markdown/headings（level/text/id）/prev/next — 源码：`okf_kit/serve/reader.py:70-95`
- F-202: 函数 `enrich_sources(bundle_dir, source_paths: list[str], question: str) -> list[dict]` 返回列表含 concept_id/title/section/anchor/snippet — 源码：`okf_kit/serve/reader.py:98-121`
- F-203: 模块 `serve/run.py` 函数 `serve(*, host="127.0.0.1", port=0, token="auto", ui=None, parent_pid=None) -> int`，延迟导入 uvicorn — 源码：`okf_kit/serve/run.py:17-23`
- F-204: `serve` 函数中 token 为 `"auto"` 时调用 `secrets.token_hex(16)`；port 为 0 时调用 `_free_port(host)` — 源码：`okf_kit/serve/run.py:27-29`
- F-205: `serve` 函数打印 JSON 格式 ready 行 `{"event": "ready", "url": ..., "token": ..., "pid": ...}`，flush=True — 源码：`okf_kit/serve/run.py:32-33`
- F-206: `serve` 函数在 parent_pid 给定时调用 `_watch_parent(parent_pid)`，随后 `uvicorn.run(app, host=host, port=port, log_level="warning")` — 源码：`okf_kit/serve/run.py:35-38`
- F-207: 函数 `_watch_parent(pid: int)` 启动 daemon 线程，每 2 秒 `os.kill(pid, 0)` 检测父进程，失败时 `os._exit(0)` — 源码：`okf_kit/serve/run.py:50-58`
- F-208: 模块 `serve/settings.py` 常量 `SERVICE = "okf-kit"`，`_DEFAULTS = {"provider": "none", "model": None, "base_url": None}` — 源码：`okf_kit/serve/settings.py:17-18`
- F-209: 函数 `load_settings() -> dict` 从 `home_dir() / "settings.json"` 读取，异常时返回默认值 — 源码：`okf_kit/serve/settings.py:29-37`
- F-210: 函数 `save_settings(provider, model, base_url, api_key=None) -> dict` 写入 settings.json（不含 api_key），api_key 非空时调用 `_store_key` — 源码：`okf_kit/serve/settings.py:40-48`
- F-211: 函数 `get_key(provider: str) -> str | None` 优先使用 `keyring.get_password(SERVICE, provider)`，失败时回退到 `~/.okf/.secrets.json` — 源码：`okf_kit/serve/settings.py:51-65`
- F-212: 函数 `_store_key(provider, api_key)` 优先使用 `keyring.set_password`，失败时写入 `.secrets.json` 并 `os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)` — 源码：`okf_kit/serve/settings.py:68-88`
- F-213: 函数 `public_settings() -> dict` 返回 provider/model/base_url/has_key，不返回密钥本身 — 源码：`okf_kit/serve/settings.py:91-98`

## Fetch/Crawl 模块

- F-220: 模块 `fetch/__init__.py` 文档字符串为 `"Fetchers: pluggable ways to turn a URL into a Page (markdown + links)."` — 源码：`okf_kit/fetch/__init__.py:1`
- F-221: 类 `HttpFetcher`，类属性 `kind = "http"` — 源码：`okf_kit/fetch/http.py:54-55`
- F-222: `HttpFetcher.__init__(self, *, respect_robots=True, timeout=20.0, concurrency=8, verbose=False)` 创建 `httpx.AsyncClient`（follow_redirects=True，timeout=timeout，User-Agent 头）、`asyncio.Semaphore(concurrency)`、`_robots` 字典和 `_robots_lock` — 源码：`okf_kit/fetch/http.py:57-74`
- F-223: `HttpFetcher.fetch(self, url: str) -> Page | None` 为 async 方法，通过 semaphore 限流，检查 robots.txt，HTTP GET，status>=400 返回 None，content-type 不含 html 返回 None — 源码：`okf_kit/fetch/http.py:76-107`
- F-224: `HttpFetcher.fetch` 调用 `_extract_markdown(html)` 和 `self._parse(html, str(resp.url))`，markdown 为空时调用 `self._fallback(html, title)`，最终调用 `clean_markdown` — 源码：`okf_kit/fetch/http.py:89-107`
- F-225: `HttpFetcher.close(self) -> None` 为 async 方法，调用 `self._client.aclose()` — 源码：`okf_kit/fetch/http.py:109-110`
- F-226: `HttpFetcher._allowed(self, url: str) -> bool` 为 async 方法，按 host 缓存 RobotFileParser，调用 `rp.can_fetch(_USER_AGENT, url)` — 源码：`okf_kit/fetch/http.py:114-120`
- F-227: `HttpFetcher._parse(html: str, base_url: str) -> tuple` 为 `@staticmethod`，使用 selectolax HTMLParser 提取 title、meta description、所有链接和 content_links — 源码：`okf_kit/fetch/http.py:135-189`
- F-228: `_parse` 方法处理 `meta[http-equiv="refresh"]` 重定向，正则提取 url 目标并插入 links 列表头部 — 源码：`okf_kit/fetch/http.py:168-178`
- F-229: `_parse` 方法中 content_links 从 `main`/`article`/`body` 元素提取，先 decompose `nav/header/footer/aside/[role="navigation"]` 节点 — 源码：`okf_kit/fetch/http.py:183-188`
- F-230: `HttpFetcher._fallback(html: str, title: str | None) -> str` 为 `@staticmethod`，移除 `_SKIP_TAGS` 标签，提取 h1-h4/p/li 文本，组装为 markdown — 源码：`okf_kit/fetch/http.py:191-216`
- F-231: 常量 `_USER_AGENT = f"okf-kit/{__version__} (+https://github.com/vinodborole/okf-kit)"` — 源码：`okf_kit/fetch/http.py:24`
- F-232: 常量 `_SKIP_TAGS = ("script", "style", "noscript", "svg", "nav", "footer", "header")` — 源码：`okf_kit/fetch/http.py:25`
- F-233: 变量 `_NO_FALLBACK_KW` 通过 `inspect.signature` 检测 trafilatura.extract 参数名，值为 `"fast"` 或 `"no_fallback"` — 源码：`okf_kit/fetch/http.py:31-33`
- F-234: 正则 `_PERMALINK = re.compile(r"\s*\[[¶#§🔗\s​]*\]\(#[^)]*\)")` — 源码：`okf_kit/fetch/http.py:39`
- F-235: 函数 `_extract_markdown(html: str) -> str | None` 调用 `trafilatura.extract`，参数 output_format="markdown"、include_tables=True、include_formatting=True、include_links=True，使用 `_NO_FALLBACK_KW=True`；结果通过 `_PERMALINK.sub("", md)` 清理 — 源码：`okf_kit/fetch/http.py:42-51`
- F-236: 类 `BrowserFetcher`，类属性 `kind = "browser"` — 源码：`okf_kit/fetch/browser.py:20-21`
- F-237: `BrowserFetcher.__init__(self, *, verbose: bool = False, **_)` 延迟导入 `crawl4ai.AsyncWebCrawler` 和 `BrowserConfig`，创建 `BrowserConfig(headless=True, verbose=verbose)` — 源码：`okf_kit/fetch/browser.py:23-30`
- F-238: `BrowserFetcher.fetch(self, url: str) -> Page | None` 为 async 方法，调用 `crawler.arun(url, config=CrawlerRunConfig())`，从 result.markdown.raw_markdown 获取 markdown，从 result.links.internal 获取链接 — 源码：`okf_kit/fetch/browser.py:38-60`
- F-239: `BrowserFetcher.close(self) -> None` 为 async 方法，调用 `self._crawler.__aexit__(None, None, None)` — 源码：`okf_kit/fetch/browser.py:62-64`
- F-240: 模块 `crawl.py` 常量 `_SHORT_PAGE_CHARS = 200`，`_JS_HINT_RATIO = 0.30` — 源码：`okf_kit/crawl.py:19-20`
- F-241: 函数 `_default_output(seed: str) -> Path` 返回 `Path(f"./{host}-okf")`，host 从 urlparse netloc 获取，冒号替换为下划线 — 源码：`okf_kit/crawl.py:23-25`
- F-242: 函数 `make_fetcher(js: bool, *, respect_robots: bool = True, verbose: bool = False)`，js 为真时返回 `BrowserFetcher(verbose=verbose)`，否则返回 `HttpFetcher(respect_robots=respect_robots, verbose=verbose)` — 源码：`okf_kit/crawl.py:28-35`
- F-243: 函数 `normalize_prefix(prefix: str) -> str` 确保前缀有首尾斜杠 — 源码：`okf_kit/crawl.py:38-41`
- F-244: 函数 `scope_prefix_for(url: str) -> str` 从 URL 路径推导爬取范围：文件路径取其目录，无扩展名路径取自身 — 源码：`okf_kit/crawl.py:44-60`
- F-245: 函数 `crawl_site(seed, *, fetcher, max_depth, max_pages, path_prefix=None, scope=True, on_page=None) -> tuple[list[Page], str]` 为 async 函数，执行 BFS 爬取 — 源码：`okf_kit/crawl.py:69-78`
- F-246: `crawl_site` 使用 `asyncio.gather(*(fetcher.fetch(u) for u in batch))` 并发获取页面；首个页面设置 prefix；同 host、未访问、在范围内的链接收录到 next_level — 源码：`okf_kit/crawl.py:96-131`
- F-247: `crawl_site` 跳过无 markdown 内容的页面和重复路径，设置 `page.depth = depth`，调用 `on_page(page, path)` 回调 — 源码：`okf_kit/crawl.py:120-130`
- F-248: 函数 `build_bundle(url, *, output=None, max_depth=3, max_pages=200, js=False, respect_robots=True, path_prefix=None, all_paths=False, verbose=False) -> int` 调用 `asyncio.run(_build(...))` — 源码：`okf_kit/crawl.py:137-161`
- F-249: 异步函数 `_build` 调用 `normalize_url`、`_default_output`、`make_fetcher`、`crawl_site`，finally 中调用 `await fetcher.close()` — 源码：`okf_kit/crawl.py:164-187`
- F-250: `_build` 对每个 page 调用 `write_concept(bundle_dir, p, ts)`，过滤 None 得到 records；调用 `write_bundle_meta` 写入元数据和 edges — 源码：`okf_kit/crawl.py:196-212`
- F-251: `_build` 当短页面比例超过 `_JS_HINT_RATIO` 且非 js 模式时，输出提示安装 `okf-kit[js]` 的消息到 stderr — 源码：`okf_kit/crawl.py:214-220`
- F-252: `_build` 最后调用 `validate_bundle(bundle_dir)`，返回 0 或 3 — 源码：`okf_kit/crawl.py:222-224`
- F-253: 模块 `bundle_nav.py` 常量 `MAX_FILE_CHARS = 12000`，正则 `_TOKEN = re.compile(r"[a-z0-9]{2,}")` — 源码：`okf_kit/bundle_nav.py:17-18`
- F-254: 函数 `_safe(bundle_dir: Path, path: str) -> Path | None` 使用 `.resolve()` 进行路径遍历防护，target 在 root 内才返回 — 源码：`okf_kit/bundle_nav.py:21-26`
- F-255: 函数 `list_directory(bundle_dir, path: str = "/") -> str` 返回排序后的条目列表，格式为 `"dir:  <name>"` 或 `"file: <name>"`，排除 STATE_DIRNAME — 源码：`okf_kit/bundle_nav.py:29-39`
- F-256: 函数 `read_concept(bundle_dir, path: str) -> str` 读取文件内容，截断至 `MAX_FILE_CHARS`（12000 字符） — 源码：`okf_kit/bundle_nav.py:42-47`
- F-257: 函数 `search_bundle(bundle_dir, query: str, limit: int = 5) -> list[dict]` 对 pages 目录下所有 .md 文件进行关键词搜索，title 权重为 body 的 3 倍，返回 path/title/score/snippet — 源码：`okf_kit/bundle_nav.py:71-88`
- F-258: 模块 `bundle_reader.py` 正则 `_LINK = re.compile(r"\]\(\s*([^)\s]+)")`，常量 `RESERVED = {"index.md", "log.md"}` — 源码：`okf_kit/bundle_reader.py:18-19`
- F-259: 函数 `read_bundle(bundle_dir) -> dict` 遍历所有非保留 .md 文件，解析 frontmatter 和 body，从 markdown 链接和 state.json edges 两个来源构建边集 — 源码：`okf_kit/bundle_reader.py:46-89`
- F-260: 函数 `_target_id(target: str, from_id: str) -> str | None` 将 markdown 链接目标解析为 concept id，去除 fragment 和 query，要求以 `.md` 结尾，解析相对路径，拒绝 `..` 和绝对路径 — 源码：`okf_kit/bundle_reader.py:32-43`

## 配置系统与 Registry

- F-270: 模块 `config.py` 函数 `home_dir() -> Path` 返回 `Path(os.environ.get("OKF_HOME", Path.home() / ".okf"))`，创建目录 — 源码：`okf_kit/config.py:9-13`
- F-271: 函数 `bundles_dir() -> Path` 返回 `home_dir() / "bundles"`，创建目录 — 源码：`okf_kit/config.py:16-19`
- F-272: 函数 `chats_dir() -> Path` 返回 `home_dir() / "chats"`，创建目录 — 源码：`okf_kit/config.py:22-25`
- F-273: 常量 `STATE_DIRNAME = ".okf-kit"`，`STATE_FILENAME = "state.json"` — 源码：`okf_kit/config.py:29-30`
- F-274: 模块 `registry.py` 常量 `DEFAULT_REGISTRY = "https://raw.githubusercontent.com/vinodborole/awesome-okf-kit/main/registry.yaml"` — 源码：`okf_kit/registry.py:21-23`
- F-275: 函数 `load_registry(source: str) -> list[dict]`，source 以 http/https 开头时使用 httpx GET，否则读取本地文件；使用 yaml.safe_load 解析，要求结果为 list — 源码：`okf_kit/registry.py:26-35`
- F-276: 函数 `local_bundles() -> list[dict]` 扫描 `bundles_dir().glob("*/.okf-kit/state.json")`，返回 name/root_url/pages/updated 字典列表 — 源码：`okf_kit/registry.py:38-51`
- F-277: 函数 `cmd_list(*, remote: bool, registry: str) -> int`，remote 为真时加载远程注册表并打印，否则列出本地 bundles — 源码：`okf_kit/registry.py:54-70`
- F-278: 函数 `cmd_get(name: str, *, registry: str, yes: bool) -> int` 查找注册表条目，确认后 httpx 下载 zip，调用 `_extract_zip` 解压到 `bundles_dir() / name`，调用 `validate_bundle` 验证 — 源码：`okf_kit/registry.py:73-101`
- F-279: 函数 `_extract_zip(buf, dest: Path)` 删除已有 dest，解压 zip，剥离单层顶层文件夹，拒绝含 `..` 的路径 — 源码：`okf_kit/registry.py:104-123`
- F-280: 函数 `resolve_bundle(name_or_dir: str) -> Path` 严格解析：本地路径含 index.md 则返回，否则查找 `bundles_dir() / name_or_dir`，都不存在则 SystemExit — 源码：`okf_kit/registry.py:126-138`
- F-281: 函数 `bundle_dir_arg(name_or_dir: str) -> Path` 宽松解析：路径存在则原样返回，否则查找 bundles_dir，不存在时返回原始 Path — 源码：`okf_kit/registry.py:141-152`

## 同步与可视化

- F-290: 模块 `sync.py` 常量 `_SAFETY_MIN_PAGES = 4`，`_SAFETY_RATIO = 0.5` — 源码：`okf_kit/sync.py:33-34`
- F-291: 函数 `sync_bundle(directory, *, max_depth=None, max_pages=None, force=False) -> int` 调用 `asyncio.run(run_sync(...))`，返回 0 或 3 — 源码：`okf_kit/sync.py:37-47`
- F-292: 异步函数 `run_sync(directory, *, max_depth=None, max_pages=None, force=False, post_sync=()) -> dict`，读取 state.json 获取 root_url 和 config — 源码：`okf_kit/sync.py:50-67`
- F-293: `run_sync` 根据 config.fetcher 判断是否使用 browser 模式，调用 `make_fetcher` 和 `crawl_site`；保留原始 path_prefix（pre-0.1.3 bundle 默认 "/"） — 源码：`okf_kit/sync.py:72-89`
- F-294: `run_sync` 计算 added/removed/changed 三个集合：added = 新页面 - 旧页面，removed = 旧页面 - 新页面，changed = 两者交集且 hash 不同 — 源码：`okf_kit/sync.py:93-103`
- F-295: `run_sync` 安全阀门：非 force 时，若旧页面数 > 4 且新页面数 < 旧页面数 * 0.5，抛出 SystemExit — 源码：`okf_kit/sync.py:105-114`
- F-296: `run_sync` 删除 removed 文件，调用 `prune_empty_dirs`，对 added+changed 调用 `write_concept`；调用 `write_bundle_meta` 更新状态 — 源码：`okf_kit/sync.py:118-147`
- F-297: `run_sync` 遍历 `post_sync` 异步钩子并 await，最后调用 `validate_bundle(bundle_dir, quiet=True)` — 源码：`okf_kit/sync.py:149-157`
- F-298: 模块 `visualize.py` 函数 `visualize(directory, *, output=None) -> Path` 调用 `read_bundle` 和 `_data`，输出 HTML 文件，默认路径为 `<bundle>/viz.html` — 源码：`okf_kit/visualize.py:67-73`
- F-299: 函数 `_data(bundle_dir: Path) -> dict` 调用 `read_bundle`，构建 links/backlinks 邻接表，每个 node 的 `_deg` 为出度+入度，body 截断至 12000 字符 — 源码：`okf_kit/visualize.py:45-64`
- F-300: 函数 `_tree(concepts: list[dict]) -> list[dict]` 将 concepts 按 id 路径嵌套为树形结构，叶子节点含 name/page/deg，目录节点含 name/children/count — 源码：`okf_kit/visualize.py:19-42`
- F-301: `_HTML` 为内嵌的自包含 HTML 字符串，包含 CSS（含暗色模式 `prefers-color-scheme:dark`）和 JavaScript，实现树形导航、搜索、Markdown 渲染、链接和反向链接展示 — 源码：`okf_kit/visualize.py:76-230`

## Enrich 模块

- F-310: 模块 `enrich.py` 导入 `yaml`、`_concept_files`、`_split_frontmatter`、`frontmatter` — 源码：`okf_kit/enrich.py:14-17`
- F-311: 常量 `_SYSTEM` 为 OpenAI system prompt，要求返回单句事实描述和 3-7 个小写关键词 — 源码：`okf_kit/enrich.py:19-22`
- F-312: 常量 `_SCHEMA` 定义 JSON schema，name 为 `"page_summary"`，strict=True，包含 `description`（string）和 `tags`（string array），两者均 required — 源码：`okf_kit/enrich.py:23-35`
- F-313: 函数 `_openai_enricher(model: str)` 从环境变量 `OPENAI_API_KEY` 获取密钥，延迟导入 `openai.OpenAI`，返回闭包函数 `enrich(title, body) -> dict` — 源码：`okf_kit/enrich.py:38-61`
- F-314: 闭包 `enrich` 调用 `client.chat.completions.create`，使用 response_format `{"type": "json_schema", "json_schema": _SCHEMA}`，body 截断至 6000 字符 — 源码：`okf_kit/enrich.py:48-59`
- F-315: 函数 `enrich_bundle(bundle_dir, *, model="gpt-4o-mini", enricher=None) -> int` 遍历 `_concept_files(bundle_dir)`，解析 YAML frontmatter，调用 enricher，将 description 和 tags 写回 frontmatter，返回处理计数 — 源码：`okf_kit/enrich.py:64-88`
