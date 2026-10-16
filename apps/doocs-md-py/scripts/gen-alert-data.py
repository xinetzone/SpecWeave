"""从上游 alert.ts 派生 render/extensions/alert_data.py。

upstream: packages/core/src/extensions/alert.ts（ICON_* 常量 + defaultAlertVariant）。
上游更新后重新执行即可对齐；对象按文件内出现顺序保留。
用法：python scripts/gen-alert-data.py [path/to/alert.ts]
"""

import pathlib
import re
import sys

_HERE = pathlib.Path(__file__).resolve().parent
_DEFAULT_SRC = (
    _HERE.parent.parent.parent
    / ".chaos"
    / "libs"
    / "md"
    / "packages/core/src/extensions/alert.ts"
)

_ICON_CONST_RE = re.compile(r"const (ICON_[A-Z]+)\s*=\s*`([^`]*)`")
_OBJECT_RE = re.compile(
    r"\{\s*type:\s*`([^`]+)`(?:,\s*title:\s*`([^`]*)`)?,\s*icon:\s*"
    r"(?:`([^`]*)`|(ICON_[A-Z]+)),\s*\}",
    re.DOTALL,
)
_ARRAY_RANGE = ("const defaultAlertVariant", "]")


def parse(ts_text: str):
    icons = dict(_ICON_CONST_RE.findall(ts_text))

    start = ts_text.index(_ARRAY_RANGE[0])
    end_m = re.search(r"^\]", ts_text[start:], re.MULTILINE)
    body = ts_text[start : start + end_m.start()]

    variants = []
    for m in _OBJECT_RE.finditer(body):
        vtype, vtitle = m.group(1), m.group(2)
        icon_inline, icon_ref = m.group(3), m.group(4)
        icon = icon_inline if icon_inline is not None else icons[icon_ref]
        variants.append((vtype, vtitle, icon))
    return variants


def render_py(variants) -> str:
    lines = [
        '"""Alert 变体默认表（GFM + Obsidian + 学术环境，含 octicon SVG）。',
        "",
        "upstream: packages/core/src/extensions/alert.ts defaultAlertVariant。",
        "由 scripts/gen-alert-data.py 原样派生，请勿手工编辑。",
        '"""',
        "",
        "# (type, title|None, icon)；title 缺省时渲染端按 ucfirst(type) 兜底",
        "VARIANTS: list[tuple[str, str | None, str]] = [",
    ]
    for vtype, vtitle, icon in variants:
        lines.append(f"    ({vtype!r}, {vtitle!r}, {icon!r}),")
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else _DEFAULT_SRC
    variants = parse(src.read_text(encoding="utf-8"))
    if len(variants) < 30:
        raise SystemExit(f"alert 变体数异常（{len(variants)}），中止生成")
    required = {"note", "warning", "tip", "theorem", "definition", "remark", "faq", "cite"}
    missing = required - {v[0] for v in variants}
    if missing:
        raise SystemExit(f"缺少关键变体：{sorted(missing)}")
    out = _HERE.parent / "src" / "doocs_md_py" / "render" / "extensions" / "alert_data.py"
    out.write_text(render_py(variants), encoding="utf-8")
    print(f"wrote {out} with {len(variants)} variants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
