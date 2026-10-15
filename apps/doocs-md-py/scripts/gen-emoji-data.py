"""从上游 emoji-data.ts 派生 render/extensions/emoji_data.py。

upstream: packages/core/src/extensions/emoji-data.ts（EMOJI_SHORTCODES）。
该脚本是一次性/可再生成的数据搬运工具：上游更新后重新执行即可对齐。
用法：python scripts/gen-emoji-data.py [path/to/emoji-data.ts]
"""

import pathlib
import re
import sys

_HERE = pathlib.Path(__file__).resolve().parent
_DEFAULT_SRC = _HERE.parent.parent.parent / ".chaos" / "libs" / "md" / (
    "packages/core/src/extensions/emoji-data.ts"
)

# 仅匹配映射主体内的 `  'name': `char`,` 行（反引号模板值，emoji 不含反引号）
_LINE_RE = re.compile(r"^  '((?:[^'\\]|\\.)*)': `([^`]*)`,?$")


def parse_entries(ts_text: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    in_map = False
    for line in ts_text.splitlines():
        if line.startswith("export const EMOJI_SHORTCODES"):
            in_map = True
            continue
        if not in_map:
            continue
        if line == "}":
            break
        m = _LINE_RE.match(line)
        if m:
            entries.append((m.group(1), m.group(2)))
    return entries


def render_py(entries: list[tuple[str, str]]) -> str:
    lines = [
        '"""GitHub 兼容 emoji shortcode 表。',
        "",
        "upstream: packages/core/src/extensions/emoji-data.ts EMOJI_SHORTCODES。",
        "由 scripts/gen-emoji-data.py 原样派生，请勿手工编辑；未知 shortcode 保留字面。",
        '"""',
        "",
        "EMOJI_SHORTCODES: dict[str, str] = {",
    ]
    for name, char in entries:
        lines.append(f"    {name!r}: {char!r},")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else _DEFAULT_SRC
    ts_text = src.read_text(encoding="utf-8")
    entries = parse_entries(ts_text)
    if len(entries) < 200:
        raise SystemExit(f"emoji 条目数异常（{len(entries)}），中止生成")
    for alias in ("+1", "-1"):
        if alias not in dict(entries):
            raise SystemExit(f"缺少关键别名 {alias}")
    out = _HERE.parent / "src" / "doocs_md_py" / "render" / "extensions" / "emoji_data.py"
    out.write_text(render_py(entries), encoding="utf-8")
    print(f"wrote {out} with {len(entries)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
