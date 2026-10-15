"""TR-18 MCP 字面值黄金快照重新生成器。

从上游 TS 源树**机械提取**下列事实，写入 tests/golden/mcp_options_snapshot.json：

- config-options.ts：10 组选项数组 + ``codeBlockUrlPrefix`` / ``codeBlockThemeList``；
- shared/configs/ai-service-options.ts：``serviceOptions``（21 项，endpoint 解析
  ``DEFAULT_SERVICE_ENDPOINT`` 标识符到 shared/constants/ai-config.ts）；
- mcp-server/src/index.ts：13 次 ``registerTool`` 的工具名与描述、19 个 zod 入参的
  名称/必填/默认值/枚举/正则（含两条 JS→JSON Schema 去偏规则）、
  ``extensions`` 与 ``options`` 两个字面值块、``levels`` 标题级别数组。

提取器只读 TS 原文（不 import 本包），因此快照是独立的「上游期望值」；
tests/mcp/test_mcp_option_snapshots.py 离线拿它与 Python 转录逐项对拍。

用法：
    python scripts/mcp_options_snapshot_regen.py
"""

import hashlib
import json
import os
import re
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = Path(os.environ.get("MD_UPSTREAM_DIR", APP_ROOT.parents[1] / ".chaos" / "libs" / "md"))
MCP_SRC = UPSTREAM / "packages" / "mcp-server" / "src"
SHARED_SRC = UPSTREAM / "packages" / "shared" / "src"
TARGET = APP_ROOT / "tests" / "golden" / "mcp_options_snapshot.json"

# ---------------------------------------------------------------- 词法工具

# 模板字面量（`` \` `` 转义不提前闭合）
_TEMPLATE = re.compile(r"`((?:[^`\\]|\\.)*)`")
_KEY = re.compile(r"([A-Za-z_$][\w$]*)\s*:")
_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", "`": "`", "$": "$", "'": "'", '"': '"'}
_BRACKETS = {"]": "[", "}": "{", ")": "("}
_REGEX_PREV = set("(,=:[!&|?{};+")


def decode_template(raw: str) -> str:
    """解码 JS 模板字面量内的转义序列（不处理 ``${}`` 插值，出现即报错）。"""
    out: list[str] = []
    i = 0
    while i < len(raw):
        char = raw[i]
        if char != "\\":
            out.append(char)
            i += 1
            continue
        if raw[i + 1 : i + 2] == "{":
            raise ValueError(f"unsupported interpolation: {raw!r}")
        nxt = raw[i + 1]
        if nxt not in _ESCAPES:
            raise ValueError(f"unsupported escape: \\{nxt}")
        out.append(_ESCAPES[nxt])
        i += 2
    return "".join(out)


def _is_regex_start(text: str, index: int) -> bool:
    prev = index - 1
    while prev >= 0 and text[prev] in " \t\r\n":
        prev -= 1
    return prev < 0 or text[prev] in _REGEX_PREV


def _skip_span(text: str, index: int) -> int | None:
    """若 ``index`` 处是模板字面量/注释/正则字面量，返回其结束位置，否则 None。"""
    if text[index] == "`":
        match = _TEMPLATE.match(text, index)
        if match is None:
            raise ValueError(f"unterminated template literal at {index}")
        return match.end()
    if text[index : index + 2] == "//":
        end = text.find("\n", index)
        return len(text) if end < 0 else end + 1
    if text[index : index + 2] == "/*":
        end = text.find("*/", index)
        if end < 0:
            raise ValueError("unterminated block comment")
        return end + 2
    if text[index] == "/" and _is_regex_start(text, index):
        j = index + 1
        while j < len(text):
            if text[j] == "\\":
                j += 2
                continue
            if text[j] == "/":
                return j + 1
            j += 1
        raise ValueError("unterminated regex literal")
    return None


def find_closer(text: str, start: int) -> int:
    """``text[start]`` 为开括号时返回配对闭括号下标（跳过字符串/注释/正则）。"""
    stack = [text[start]]
    i = start + 1
    while i < len(text):
        span = _skip_span(text, i)
        if span is not None:
            i = span
            continue
        char = text[i]
        if char in "[{(":
            stack.append(char)
        elif char in "]})":
            if _BRACKETS[char] != stack[-1]:
                raise ValueError(f"mismatched bracket {char!r} at {i}")
            stack.pop()
            if not stack:
                return i
        i += 1
    raise ValueError(f"unbalanced {text[start]!r} at {start}")


def iter_objects(body: str):
    """逐个产出 ``body`` 中的顶层 ``{...}`` 文本。"""
    i = 0
    while i < len(body):
        span = _skip_span(body, i)
        if span is not None:
            i = span
            continue
        if body[i] == "{":
            end = find_closer(body, i)
            yield body[i : end + 1]
            i = end + 1
            continue
        i += 1


def parse_object(obj_text: str) -> list[tuple[str, str]]:
    """把 ``{k: expr, ...}`` 拆成 ``[(k, expr_text)]``，保持源码顺序。"""
    inner = obj_text[1:-1]
    pairs: list[tuple[str, str]] = []
    i = 0
    while i < len(inner):
        span = _skip_span(inner, i)
        if span is not None:
            i = span
            continue
        char = inner[i]
        if char in " \t\r\n,":
            i += 1
            continue
        key_match = _KEY.match(inner, i)
        if key_match is None:
            raise ValueError(f"unexpected token: {inner[i : i + 24]!r}")
        i = key_match.end()
        start = i
        depth = 0
        while i < len(inner):
            span = _skip_span(inner, i)
            if span is not None:
                i = span
                continue
            char = inner[i]
            if char in "[{(":
                depth += 1
            elif char in "]})":
                depth -= 1
            elif char == "," and depth == 0:
                break
            i += 1
        pairs.append((key_match.group(1), inner[start:i].strip()))
        if i < len(inner) and inner[i] == ",":
            i += 1
    return pairs


def split_commas(text: str) -> list[str]:
    """按顶层逗号切分（跳过字符串/注释/正则与嵌套括号）。"""
    parts: list[str] = []
    start = 0
    depth = 0
    i = 0
    while i < len(text):
        span = _skip_span(text, i)
        if span is not None:
            i = span
            continue
        char = text[i]
        if char in "[{(":
            depth += 1
        elif char in "]})":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(text[start:i])
            start = i + 1
        i += 1
    parts.append(text[start:])
    return [part.strip() for part in parts if part.strip()]


def eval_expr(expr: str, constants: dict[str, object]):
    """求值受限 TS 表达式：模板字面量（可 ``+`` 拼接）、数组字面量、true/false、标识符。"""
    text = expr.strip()
    if text in ("true", "false"):
        return text == "true"
    if text in constants:
        return constants[text]
    if text.startswith("[") and text.endswith("]"):
        return [eval_expr(part, constants) for part in split_commas(text[1:-1])]
    if text.startswith("`"):
        out: list[str] = []
        i = 0
        while i < len(text):
            if text[i] == "`":
                match = _TEMPLATE.match(text, i)
                if match is None:
                    raise ValueError(f"unterminated template literal: {text!r}")
                out.append(decode_template(match.group(1)))
                i = match.end()
                continue
            if text[i] in " \t\r\n+":
                i += 1
                continue
            raise ValueError(f"unsupported expression: {text!r}")
        return "".join(out)
    raise ValueError(f"unsupported expression: {text!r}")


# ---------------------------------------------------------------- 提取器


def block_after(text: str, pattern: str) -> str:
    """匹配 ``pattern``（须以开括号结尾）后取其配对块内部文本。"""
    matches = list(re.finditer(pattern, text))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {pattern!r}, got {len(matches)}")
    start = matches[0].end() - 1
    return text[start + 1 : find_closer(text, start)]


def parse_options_array(text: str, export_name: str) -> list[dict[str, str]]:
    """解析 ``export const <name> = [...] as const`` 的 ``{key: `lit`}`` 数组。"""
    body = block_after(text, rf"export const {export_name}\b[^=]*=\s*\[")
    options: list[dict[str, str]] = []
    for obj_text in iter_objects(body):
        entries = parse_object(obj_text)
        options.append({key: eval_expr(expr, {}) for key, expr in entries})
    return options


def parse_services(text: str, export_name: str, constants: dict[str, str]) -> list[dict[str, object]]:
    """解析 ``export const <name>: T[] = [...]`` 的服务数组（含 models 字面量数组）。"""
    body = block_after(text, rf"export const {export_name}\b[^=]*=\s*\[")
    services: list[dict[str, object]] = []
    for obj_text in iter_objects(body):
        services.append({key: eval_expr(expr, constants) for key, expr in parse_object(obj_text)})
    return services


def extract_block_entries(text: str, key: str) -> list[dict[str, object]]:
    """提取 ``jsonText({ <key>: [ {...}, ... ] })`` 中的条目数组。"""
    body = block_after(text, rf"{key}:\s*\[")
    return [{k: eval_expr(v, {}) for k, v in parse_object(obj_text)} for obj_text in iter_objects(body)]


def extract_tool_names(text: str) -> list[str]:
    return re.findall(r"server\.registerTool\(\s*`([^`]+)`", text)


def extract_tool_descriptions(text: str) -> dict[str, str]:
    descriptions: dict[str, str] = {}
    for match in re.finditer(r"server\.registerTool\(\s*`([^`]+)`", text):
        paren = text.index("(", match.start())
        region = text[paren + 1 : find_closer(text, paren)]
        brace = region.index("{")
        entries = dict(parse_object(region[brace : find_closer(region, brace) + 1]))
        descriptions[match.group(1)] = eval_expr(entries["description"], {})
    return descriptions


def extract_schema(text: str, code_block_theme_urls: list[str]) -> dict[str, object]:
    """按 2 空格缩进提取 zod ``object({...})`` 的 19 个顶层字段属性。

    ``codeBlockTheme`` 的枚举来自 ``codeBlockThemeOptions.map(option => option.value)``
    （upstream: index.ts:127），在字面量侧已提取，此处直接注入。
    """
    lines = text.splitlines()
    marker = "export const renderMarkdownInputSchema = z.object({"
    start = next(i for i, line in enumerate(lines) if marker in line)
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("})"))

    fields: list[tuple[str, str]] = []
    current: list[str] | None = None
    for line in lines[start + 1 : end]:
        field_match = re.match(r"^ {2}(\w+): z", line)
        if field_match:
            if current is not None:
                fields.append((current[0], "\n".join(current[1:])))
            current = [field_match.group(1), line.strip()]
        elif current is not None:
            current.append(line.strip())
    if current is not None:
        fields.append((current[0], "\n".join(current[1:])))

    names: list[str] = []
    required: list[str] = []
    defaults: dict[str, object] = {}
    enums: dict[str, list[str]] = {}
    patterns: dict[str, str] = {}
    for name, expr in fields:
        names.append(name)
        if ".optional()" not in expr:
            required.append(name)
        default_match = re.search(r"\.default\(([^)]*)\)", expr)
        if default_match:
            defaults[name] = eval_expr(default_match.group(1), {})
        enum_match = re.search(r"z\s*\.enum\(\s*(\[[^\]]*\])", expr)
        if enum_match:
            enums[name] = [
                decode_template(match.group(1)) for match in _TEMPLATE.finditer(enum_match.group(1))
            ]
        elif "codeBlockThemeOptions.map" in expr:
            enums[name] = list(code_block_theme_urls)
        pattern_match = re.search(r"\.regex\(/((?:[^/\\]|\\.)*)/([a-z]*)", expr)
        if pattern_match:
            patterns[name] = debias_regex(pattern_match.group(1), pattern_match.group(2))
    return {
        "fields": names,
        "required": required,
        "defaults": defaults,
        "enums": enums,
        "patterns": patterns,
    }


def debias_regex(source: str, flags: str) -> str:
    """JS 正则 → JSON Schema ``pattern`` 的两条去偏（upstream: index.ts:35/48/53/58）。

    ① JS ``\\d`` 只匹配 ASCII 数字，Python ``re`` 默认 Unicode → 一律写 ``[0-9]``；
    ② JSON Schema 无 ``/i`` 标志 → 十六进制类展开为 ``[0-9A-Fa-f]``。
    """
    out = source.replace(r"\d", "[0-9]")
    if "i" in flags:
        out = out.replace("[0-9A-F]", "[0-9A-Fa-f]")
    return out


# ---------------------------------------------------------------- 载荷构造
# 下列投影逐条对应上游 index.ts 的 jsonText 实参（行号见注释）。


def _label_value_desc(options: list[dict[str, str]]) -> list[dict[str, str]]:
    """upstream 惯用投影 ``{label, value, description}``。"""
    return [
        {"label": option["label"], "value": option["value"], "description": option["desc"]}
        for option in options
    ]


def _value_label_desc(options: list[dict[str, str]]) -> list[dict[str, str]]:
    """upstream 投影 ``{value, label, description}``（list_colors）。"""
    return [
        {"value": option["value"], "label": option["label"], "description": option["desc"]}
        for option in options
    ]


def build_tool_payloads(raw: dict[str, object]) -> dict[str, object]:
    return {
        # upstream: index.ts:173-179
        "list_themes": {
            "themes": [
                {"value": t["value"], "label": t["label"], "author": t["desc"] or "official"}
                for t in raw["theme_options"]
            ]
        },
        # upstream: index.ts:190-196
        "list_colors": {"colors": _value_label_desc(raw["color_options"])},
        # upstream: index.ts:204-210
        "list_fonts": {"fonts": _label_value_desc(raw["font_family_options"])},
        # upstream: index.ts:218-224
        "list_font_sizes": {"fontSizes": _label_value_desc(raw["font_size_options"])},
        # upstream: index.ts:232-238
        "list_legend_formats": {"legendFormats": _label_value_desc(raw["legend_options"])},
        # upstream: index.ts:246-254
        "list_heading_styles": {
            "headingStyles": _label_value_desc(raw["heading_style_options"]),
            "levels": list(raw["heading_levels"]),
        },
        # upstream: index.ts:261-273
        "list_spacing_options": {
            "lineHeights": _label_value_desc(raw["line_height_options"]),
            "blockSpacings": _label_value_desc(raw["block_spacing_options"]),
        },
        # upstream: index.ts:280-292
        "list_color_options": {
            "linkColors": _label_value_desc(raw["link_color_options"]),
            "blockquoteBackgrounds": _label_value_desc(raw["blockquote_background_options"]),
        },
        # upstream: index.ts:299-306
        "list_code_block_themes": {"codeBlockThemes": _label_value_desc(raw["code_block_theme_options"])},
        # upstream: index.ts:316-323
        "list_ai_services": {
            "services": [
                {
                    "value": service["value"],
                    "label": service["label"],
                    "endpoint": service["endpoint"],
                    "models": list(service["models"]),
                }
                for service in raw["service_options"]
            ]
        },
        # upstream: index.ts:333-398
        "explain_extensions": {"extensions": raw["extensions"]},
        # upstream: index.ts:408-430
        "get_renderer_options": {"options": raw["renderer_options"]},
    }


# ---------------------------------------------------------------- 主流程

_OPTION_ARRAYS = (
    "colorOptions",
    "themeOptions",
    "fontFamilyOptions",
    "fontSizeOptions",
    "lineHeightOptions",
    "blockSpacingOptions",
    "linkColorOptions",
    "blockquoteBackgroundOptions",
    "legendOptions",
    "headingStyleOptions",
)

# 选项数组 → 快照 raw 键（snake_case，与 Python 侧 options.py 常量名对应）
_RAW_KEYS = {
    "colorOptions": "color_options",
    "themeOptions": "theme_options",
    "fontFamilyOptions": "font_family_options",
    "fontSizeOptions": "font_size_options",
    "lineHeightOptions": "line_height_options",
    "blockSpacingOptions": "block_spacing_options",
    "linkColorOptions": "link_color_options",
    "blockquoteBackgroundOptions": "blockquote_background_options",
    "legendOptions": "legend_options",
    "headingStyleOptions": "heading_style_options",
}

# 各组条目数（上游实测；数量变化须人工复核而非静默通过）
_EXPECTED_COUNTS = {
    "color_options": 11,
    "theme_options": 3,
    "font_family_options": 3,
    "font_size_options": 5,
    "line_height_options": 5,
    "block_spacing_options": 5,
    "link_color_options": 3,
    "blockquote_background_options": 3,
    "legend_options": 6,
    "heading_style_options": 5,
    "code_block_theme_options": 10,
    "service_options": 21,
    "extensions": 11,
    "renderer_options": 19,
}

_SOURCES = (
    "packages/mcp-server/src/config-options.ts",
    "packages/mcp-server/src/index.ts",
    "packages/shared/src/configs/ai-service-options.ts",
    "packages/shared/src/constants/ai-config.ts",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_snapshot() -> dict[str, object]:
    config_text = (MCP_SRC / "config-options.ts").read_text(encoding="utf-8")
    index_text = (MCP_SRC / "index.ts").read_text(encoding="utf-8")
    services_text = (SHARED_SRC / "configs" / "ai-service-options.ts").read_text(encoding="utf-8")
    ai_config_text = (SHARED_SRC / "constants" / "ai-config.ts").read_text(encoding="utf-8")

    raw: dict[str, object] = {}
    for export_name in _OPTION_ARRAYS:
        raw[_RAW_KEYS[export_name]] = parse_options_array(config_text, export_name)

    # upstream: config-options.ts:105-124
    prefix = eval_expr(re.search(r"const codeBlockUrlPrefix = (`[^`]*`)", config_text).group(1), {})
    raw["code_block_url_prefix"] = prefix
    raw["code_block_theme_options"] = [
        {"label": name, "value": f"{prefix}{name}.min.css", "desc": ""}
        for name in parse_literal_list(config_text, "const codeBlockThemeList = [")
    ]

    endpoint = eval_expr(
        re.search(r"export const DEFAULT_SERVICE_ENDPOINT = (`[^`]*`)", ai_config_text).group(1), {}
    )
    raw["default_service_endpoint"] = endpoint
    raw["service_options"] = parse_services(
        services_text, "serviceOptions", {"DEFAULT_SERVICE_ENDPOINT": endpoint}
    )

    raw["heading_levels"] = parse_literal_list(index_text, "levels: [")
    raw["extensions"] = extract_block_entries(index_text, "extensions")
    raw["renderer_options"] = extract_block_entries(index_text, "options")

    for key, expected in _EXPECTED_COUNTS.items():
        actual = len(raw[key])
        if actual != expected:
            raise ValueError(f"{key}: expected {expected} entries, extracted {actual}")

    tool_order = extract_tool_names(index_text)
    if len(tool_order) != 13:
        raise ValueError(f"expected 13 registered tools, extracted {len(tool_order)}")

    theme_urls = [option["value"] for option in raw["code_block_theme_options"]]
    schema = extract_schema(index_text, theme_urls)
    # upstream: index.ts:26-137 实测 20 个 zod 字段（含入参 markdown）；
    # spec.md 背景事实与 tasks.md TR-18.1 中的「19 个入参」系把 get_renderer_options
    # 的 19 行选项表与 schema 字段数混算，以磁盘源码为准（spec A1）。
    if len(schema["fields"]) != 20:
        raise ValueError(f"expected 20 zod fields, extracted {len(schema['fields'])}")

    return {
        "generated_by": "scripts/mcp_options_snapshot_regen.py",
        "upstream_dir": str(UPSTREAM),
        "sources": {relative: f"sha256:{_sha256(UPSTREAM / relative)}" for relative in _SOURCES},
        "tool_order": tool_order,
        "tool_descriptions": extract_tool_descriptions(index_text),
        "schema": schema,
        "raw": raw,
        "tools": build_tool_payloads(raw),
    }


def parse_literal_list(text: str, pattern: str) -> list[str]:
    """提取 ``<pattern>``（按字面文本匹配）起始的字面量数组元素（如 ``levels: [`h1`, ...]``）。"""
    body = block_after(text, re.escape(pattern))
    literals = _TEMPLATE.findall(body)
    leftover = _TEMPLATE.sub("", body)
    if leftover.replace(",", "").strip():
        raise ValueError(f"unexpected non-literal content in {pattern!r}: {leftover!r}")
    return [decode_template(literal) for literal in literals]


def main() -> int:
    snapshot = build_snapshot()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"regenerated: {TARGET} "
        f"(tools={len(snapshot['tools'])}, schema_fields={len(snapshot['schema']['fields'])}, "
        f"extensions={len(snapshot['raw']['extensions'])}, "
        f"renderer_options={len(snapshot['raw']['renderer_options'])})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
