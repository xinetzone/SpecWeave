#!/usr/bin/env python3
"""Comprehensive test of MyST-MCP PoC: tools, resources, prompts."""
import asyncio, sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from myst_mcp_server import parse_myst_mcp, build_mcp_server


def get_schema_prop(schema: dict, prop_name: str) -> dict | None:
    """从JSON Schema中提取属性定义，处理anyOf可空类型包装。"""
    props = schema.get("properties", {})
    if prop_name not in props:
        return None
    prop = props[prop_name]
    if "anyOf" in prop:
        for sub in prop["anyOf"]:
            if sub.get("type") != "null":
                merged = dict(sub)
                if "default" in prop:
                    merged["default"] = prop["default"]
                return merged
    return prop


async def main():
    md_path = Path(__file__).parent / "github-tools.md"
    sd = parse_myst_mcp(md_path.read_text(encoding="utf-8"))
    mcp = build_mcp_server(sd)

    tm = mcp._tool_manager
    rm = mcp._resource_manager
    pm = mcp._prompt_manager

    ok = 0
    fail = 0
    def check(name, condition, detail=""):
        nonlocal ok, fail
        if condition:
            print(f"  [PASS] {name}")
            ok += 1
        else:
            print(f"  [FAIL] {name} {detail}")
            fail += 1

    # === Tools ===
    print("=" * 60)
    print("SECTION 1: Tools")
    print("=" * 60)

    tools = tm.list_tools()
    check("4 tools registered", len(tools) == 4)
    tool_names = {t.name for t in tools}
    check("All expected tools present",
          tool_names == {"list_repositories", "create_issue", "get_issue", "search_code"})

    create_issue = next(t for t in tools if t.name == "create_issue")
    check("create_issue has correct required params",
          create_issue.parameters.get("required") == ["repo", "title"])
    check("create_issue has 5 properties",
          set(create_issue.parameters["properties"].keys()) == {"repo", "title", "body", "labels", "assignees"})

    list_repos = next(t for t in tools if t.name == "list_repositories")
    check("list_repositories has no required params",
          list_repos.parameters.get("required", []) == [])

    per_page_prop = get_schema_prop(list_repos.parameters, "per_page")
    check("per_page default is integer 30",
          per_page_prop is not None
          and per_page_prop.get("default") == 30
          and isinstance(per_page_prop.get("default"), int)
          and per_page_prop.get("type") == "integer")

    type_prop = get_schema_prop(list_repos.parameters, "type")
    check("type has enum values",
          type_prop is not None
          and type_prop.get("enum") == ["owner", "all", "public", "private", "member"])

    sort_prop = get_schema_prop(list_repos.parameters, "sort")
    check("sort has description in schema",
          sort_prop is not None and "description" in sort_prop)

    repo_prop = get_schema_prop(create_issue.parameters, "repo")
    check("repo param has description",
          repo_prop is not None and "description" in repo_prop)

    # Call create_issue
    result = await tm.call_tool("create_issue", {
        "repo": "octocat/Hello-World", "title": "Test bug"
    })
    items = result if isinstance(result, list) else getattr(result, 'content', [])
    check("call_tool returns content", len(items) > 0 and hasattr(items[0], 'text'))
    check("response mentions tool name",
          any("create_issue" in c.text for c in items if hasattr(c, 'text')))

    # Call with defaults
    result = await tm.call_tool("list_repositories", {})
    items = result if isinstance(result, list) else getattr(result, 'content', [])
    check("list_repositories works with empty args", len(items) > 0)
    check("default values applied (type=owner, per_page=30)",
          any('"type": "owner"' in c.text and '"per_page": 30' in c.text
              for c in items if hasattr(c, 'text')))

    # Call with integer param
    result = await tm.call_tool("get_issue", {"repo": "a/b", "issue_number": 42})
    items = result if isinstance(result, list) else getattr(result, 'content', [])
    check("get_issue accepts integer issue_number",
          any('"issue_number": 42' in c.text for c in items if hasattr(c, 'text')))

    # Call with enum value validation (valid enum)
    result = await tm.call_tool("list_repositories", {"type": "public", "per_page": 10})
    items = result if isinstance(result, list) else getattr(result, 'content', [])
    check("accepts valid enum value for 'type'", len(items) > 0)
    check("enum and int params passed through correctly",
          any('"type": "public"' in c.text and '"per_page": 10' in c.text
              for c in items if hasattr(c, 'text')))

    # Validation error
    try:
        await tm.call_tool("create_issue", {"repo": "test/repo"})
        check("validation catches missing title", False)
    except Exception:
        check("validation catches missing title", True)

    # === Resources ===
    print()
    print("=" * 60)
    print("SECTION 2: Resources")
    print("=" * 60)

    static_resources = rm.list_resources()
    check("static resources registered", len(static_resources) >= 1)
    static_uris = {str(r.uri) for r in static_resources}
    check("server-info resource present",
          any("server-info" in u for u in static_uris))

    templates = rm.list_templates()
    check("resource templates registered", len(templates) >= 1)
    template_uris = {str(t.uri_template) for t in templates}
    check("repo-readme template present",
          any("repo" in u and "readme" in u for u in template_uris))

    # Read static resource (get_resource is async)
    server_info_res = await rm.get_resource("github://server-info")
    check("get_resource finds server-info", server_info_res is not None)
    if server_info_res is not None and hasattr(server_info_res, 'fn'):
        try:
            read_result = server_info_res.fn()
            if asyncio.iscoroutine(read_result):
                read_result = await read_result
            check("static resource readable", read_result is not None)
            if hasattr(read_result, 'contents'):
                for c in read_result.contents:
                    if hasattr(c, 'text'):
                        check("resource has text content", len(c.text) > 0)
                        check("resource has correct mime type",
                              c.mimeType == "application/json")
                        try:
                            data = json.loads(c.text)
                            check("static resource is valid JSON", isinstance(data, dict))
                            check("JSON contains server name", data.get("server") == "github-tools")
                            check("JSON lists capabilities", "capabilities" in data)
                        except json.JSONDecodeError:
                            check("static resource is valid JSON", False)
        except Exception as e:
            check("static resource readable", False, str(e))
            import traceback; traceback.print_exc()

    # Read template resource
    readme_tmpl = next((t for t in templates if "readme" in str(t.uri_template)), None)
    check("readme template found", readme_tmpl is not None)
    if readme_tmpl is not None and hasattr(readme_tmpl, 'fn'):
        try:
            read_result = readme_tmpl.fn(repo="SpecWeave/myst-mcp")
            if asyncio.iscoroutine(read_result):
                read_result = await read_result
            check("template resource readable with param", read_result is not None)
            if hasattr(read_result, 'contents'):
                for c in read_result.contents:
                    if hasattr(c, 'text'):
                        check("template content non-empty", len(c.text) > 0)
                        check("template resolved URI correctly",
                              "SpecWeave/myst-mcp" in str(c.uri))
                        check("template body has {repo} replaced",
                              "SpecWeave/myst-mcp" in c.text and "{repo}" not in c.text)
        except Exception as e:
            check("template resource readable", False, str(e))
            import traceback; traceback.print_exc()

    # === Prompts ===
    print()
    print("=" * 60)
    print("SECTION 3: Prompts")
    print("=" * 60)

    prompts = pm.list_prompts()
    check("prompts registered", len(prompts) >= 1)
    prompt_names = {p.name for p in prompts}
    check("create-bug-report prompt present", "create-bug-report" in prompt_names)

    bug_prompt = pm.get_prompt("create-bug-report")
    check("get_prompt finds create-bug-report", bug_prompt is not None)
    if bug_prompt is not None:
        check("prompt has 2 arguments", len(bug_prompt.arguments) == 2)
        arg_names = {a.name for a in bug_prompt.arguments}
        check("prompt args are repo + feature_name",
              arg_names == {"repo", "feature_name"})
        check("repo is required",
              any(a.name == "repo" and a.required for a in bug_prompt.arguments))
        check("feature_name is optional",
              any(a.name == "feature_name" and not a.required for a in bug_prompt.arguments))

    # Render prompt with arguments
    try:
        messages = pm.render_prompt("create-bug-report", {
            "repo": "SpecWeave/myst-mcp",
            "feature_name": "MyST Parser"
        })
        if asyncio.iscoroutine(messages):
            messages = await messages
        msg_list = list(messages) if not isinstance(messages, list) else messages
        check("render_prompt returns messages", len(msg_list) > 0)
        for msg in msg_list:
            if hasattr(msg, 'content') and hasattr(msg.content, 'text'):
                check("prompt text contains repo name",
                      "SpecWeave/myst-mcp" in msg.content.text)
                check("prompt text contains feature name",
                      "MyST Parser" in msg.content.text)
                check("prompt follows Bug Report structure",
                      "Bug" in msg.content.text or "bug" in msg.content.text or "复现" in msg.content.text)
                break
    except Exception as e:
        check("render_prompt works", False, str(e))
        import traceback; traceback.print_exc()

    # Render prompt with default for optional arg
    try:
        messages = pm.render_prompt("create-bug-report", {
            "repo": "test/project"
        })
        if asyncio.iscoroutine(messages):
            messages = await messages
        msg_list = list(messages) if not isinstance(messages, list) else messages
        check("render_prompt works with only required args", len(msg_list) > 0)
        for msg in msg_list:
            if hasattr(msg, 'content') and hasattr(msg.content, 'text'):
                check("optional arg uses default value",
                      "该功能" in msg.content.text)
                break
    except Exception as e:
        check("render_prompt with defaults works", False, str(e))

    # === Summary ===
    print()
    print("=" * 60)
    print(f"RESULTS: {ok} passed, {fail} failed")
    print("=" * 60)

    if fail > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
