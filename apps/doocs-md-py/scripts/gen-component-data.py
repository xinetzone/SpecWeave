"""从 component.ts 机械派生内置组件注册表数据。

源：packages/core/src/extensions/component.ts 的 BUILT_IN_COMPONENTS。
输出：src/doocs_md_py/render/extensions/component_data.py。

模板文本按反引号模板字面量逐字提取（内含 {{}} 占位与双引号），
运行时不需要 example 字段，故不提取。
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT.parents[1] / ".chaos" / "libs" / "md" / "packages" / "core" / "src" / "extensions" / "component.ts"
OUT = ROOT / "src" / "doocs_md_py" / "render" / "extensions" / "component_data.py"

QUOTE_CHARS = ("`", '"', "'")


def iter_top_level_objects(text: str, start: int) -> list[str]:
    """切分起始 '[' 直属的 '{'...'}' 对象（按括号栈，跟踪字符串状态）。"""
    assert text[start] == "["
    stack: list[str] = ["["]
    obj_start = -1
    quote = ""
    objects: list[str] = []
    i = start + 1
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = ""
        else:
            if ch in QUOTE_CHARS:
                quote = ch
            elif ch in "[{":
                if ch == "{" and stack == ["["]:
                    obj_start = i
                stack.append(ch)
            elif ch in "]}":
                stack.pop()
                if ch == "}" and obj_start >= 0 and stack == ["["]:
                    objects.append(text[obj_start : i + 1])
                    obj_start = -1
                if not stack:
                    break
        i += 1
    return objects


def backtick_field(obj: str, key: str) -> str | None:
    """提取 ``key: `value``` 反引号字面量（逐字，不做转义处理）。"""
    m = re.search(re.escape(key) + r":\s*`", obj)
    if not m:
        return None
    start = m.end()
    end = start
    while end < len(obj):
        if obj[end] == "\\":
            end += 2
            continue
        if obj[end] == "`":
            break
        end += 1
    return obj[start:end]


def bool_field(obj: str, key: str) -> bool:
    return re.search(re.escape(key) + r":\s*true\b", obj) is not None


def extract_props(obj: str) -> list[dict]:
    m = re.search(r"props:\s*\[", obj)
    if not m:
        return []
    prop_objs = iter_top_level_objects(obj, m.end() - 1)
    props = []
    for p in prop_objs:
        name = backtick_field(p, "name")
        if name is None:
            continue
        prop = {"name": name, "required": bool_field(p, "required")}
        default = backtick_field(p, "default")
        if default is not None:
            prop["default"] = default
        ptype = backtick_field(p, "type")
        if ptype is not None:
            prop["type"] = ptype
        props.append(prop)
    return props


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    m = re.search(r"export const BUILT_IN_COMPONENTS[^=]*=\s*\[", text)
    assert m, "未找到 BUILT_IN_COMPONENTS 数组"
    objects = iter_top_level_objects(text, m.end() - 1)
    assert len(objects) == 8, f"期望 8 个组件，实际 {len(objects)}"

    components = []
    for obj in objects:
        name = backtick_field(obj, "name")
        assert name, f"组件缺 name: {obj[:80]}"
        template = backtick_field(obj, "template")
        assert template is not None, f"{name} 缺 template"
        components.append(
            {
                "name": name,
                "inline": bool_field(obj, "inline"),
                "template": template,
                "props": extract_props(obj),
            }
        )

    names = {c["name"] for c in components}
    expected = {
        "MpProfile", "QRCodeBlock", "AuthorBlock", "TipBlock",
        "TableBlock", "InfoGrid", "BadgeGroup", "Emoji",
    }
    assert names == expected, f"组件名不符: {names}"

    lines = [
        '"""内置自定义组件数据（由 scripts/gen-component-data.py 机械派生，勿手改）。',
        " ",
        "upstream: packages/core/src/extensions/component.ts BUILT_IN_COMPONENTS。",
        '"""',
        "",
        "from .component import ComponentDef, PropDef",
        "",
        "BUILT_IN_COMPONENTS: tuple[ComponentDef, ...] = (",
    ]
    for comp in components:
        props = ", ".join(
            "PropDef(name="
            + json.dumps(p["name"], ensure_ascii=False)
            + (", required=True" if p["required"] else "")
            + (f", default={json.dumps(p['default'], ensure_ascii=False)}" if "default" in p else "")
            + (f", type={json.dumps(p['type'], ensure_ascii=False)}" if "type" in p else "")
            + ")"
            for p in comp["props"]
        )
        lines.append(
            "    ComponentDef(name="
            + json.dumps(comp["name"], ensure_ascii=False)
            + f", inline={comp['inline']}"
            + ", template="
            + json.dumps(comp["template"], ensure_ascii=False)
            + f", props=({props},)),"
        )
    lines.append(")")
    lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(components)} components")


if __name__ == "__main__":
    main()
