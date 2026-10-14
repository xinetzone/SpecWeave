#!/usr/bin/env python3
"""V 阶段 API 真实性独立验证：提取束内 12 篇内容文档反引号中的类名/关键函数，到快照源码核验存在性。"""
import re, pathlib, sys

B = pathlib.Path(r"d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\bundles\jishu\ai\frameworks\ai-agent\kylin-agent-runtime")
S = pathlib.Path(r"d:\spaces\SpecWeave\external\dao\action\openkylin\agent-runtime")

# 构建快照源码符号池（.py，跳过 tests/.git）
cls, funcs, alltext = set(), set(), {}
for p in S.rglob("*.py"):
    if ".git" in p.parts or "tests" in p.parts:
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"^class ([A-Za-z_]\w*)", t, re.M):
        cls.add(m.group(1))
    for m in re.finditer(r"^def ([a-z_]\w*)|^    def ([a-z_]\w*)", t, re.M):
        funcs.add(m.group(1) or m.group(2))
    alltext[p.name] = t

# 每篇文档提取反引号 token
docs = list((B/"concepts").glob("*.md")) + list((B/"examples").glob("*.md"))
rx_class = re.compile(r"`([A-Z][A-Za-z0-9_]+)`")
rx_func = re.compile(r"`([a-z][a-z0-9_]{4,})`")
WHITE_FUNCS = {"chat"}  # 示例中白名单
missing = {}
checked_c, checked_f = set(), set()
for d in docs:
    t = d.read_text(encoding="utf-8")
    for name in set(rx_class.findall(t)):
        if name in ("ABC", "MCP", "ACP", "LSP", "CLI", "TUI", "API", "SDK", "PID",
                    "SQLite", "FastMCP", "FastAPI", "UVicorn", "JSON", "YAML", "FTS5",
                    "OpenAI", "Anthropic", "Bedrock", "Gemini", "Codex", "Cron", "MIT",
                    "WebUI", "Ink", "React", "Vite", "Python", "Linux", "Termux",
                    "Docker", "Nix", "HMAC", "SHA", "Fernet", "UV", "Pydantic", "RSS",
                    "CUA", "SDKs", "HTTP", "WS", "STDIO", "GPL", "AGPL", "CJK", "OS",
                    "ProcessHandle", "Protocol", "ABCs", "None", "True", "False",
                    "OrderedDict", "FrozenSpec", "Literal"):
            continue
        checked_c.add(name)
        # class 池未命中时，回退全文搜索（模块常量/枚举成员/环境变量/os 标志等大写标识符）
        if name not in cls and not any(name in txt for txt in alltext.values()):
            missing.setdefault(d.name, []).append("symbol " + name)
    for name in set(rx_func.findall(t)):
        if name in WHITE_FUNCS or not name.endswith(("_server", "_loop", "_guard")) and name not in (
            "init_agent", "discover_builtin_tools", "register_transport", "get_transport",
            "run_mcp_server", "create_mcp_server", "start_server", "run_setup_wizard",
            "run_curator_review", "maybe_run_curator", "apply_anthropic_cache_control",
            "probe_gemini_tier", "resolve_provider_client", "decide_image_input_mode",
            "handle_computer_use", "get_computer_use_schema", "reconcile_desktop_job_sessions",
            "discover_plugins", "invoke_hook", "load_gateway_config", "preprocess_skill_content",
            "scan_bundles", "scan_skill_commands", "snapshot_skills", "estimate_usage_cost",
            "fetch_account_usage", "parse_rate_limit_headers", "build_system_prompt",
            "execute_tool_calls_concurrent", "execute_tool_calls_sequential", "classify_api_error",
            "jittered_backoff", "save_trajectory", "start_gateway", "create_session",
            "search_messages", "search_sessions", "append_message", "discover_and_load",
            "get_active_provider", "register_provider", "list_providers", "run_conversation",
            "coerce_tool_args", "handle_function_call", "get_tool_definitions"):
            continue
        checked_f.add(name)
        if name not in funcs and not any(name in txt for txt in alltext.values()):
            missing.setdefault(d.name, []).append("func " + name)

print(f"核验类名 {len(checked_c)} 个、关键函数 {len(checked_f)} 个")
if missing:
    print("未命中（需人工判定）:")
    for f, items in missing.items():
        for i in sorted(set(items)):
            print(f"  {f}: {i}")
    sys.exit(1)
print("全部命中（在快照 class/def 或全文中存在）")
