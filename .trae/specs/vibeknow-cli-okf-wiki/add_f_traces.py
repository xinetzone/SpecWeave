#!/usr/bin/env python3
"""为每篇 concept 文档在 H1 之后插入事实编号溯源行（幂等）。"""
import re
from pathlib import Path

B = Path(r"d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\bundles\jishu\ai\products\vibeknow-cli\concepts")

TRACE = {
    "00-cli-overview.md": "F-001~F-006、F-086~F-094",
    "01-exit-code-contract.md": "F-014~F-023、F-037~F-039",
    "02-paid-action-gate.md": "F-024~F-032",
    "03-output-and-events.md": "F-037~F-042、F-095~F-100",
    "04-run-ledger-and-async.md": "F-043~F-053",
    "05-create-parameter-space.md": "F-054~F-066",
    "06-preset-contract.md": "F-067~F-072",
    "07-subtitle-style-and-work-edit.md": "F-073~F-080",
    "08-preview-artifacts.md": "F-043~F-045",
    "09-cleanup-safety-contract.md": "F-081~F-085",
    "10-ai-skill-contract.md": "F-101~F-104",
}

for name, rng in TRACE.items():
    p = B / name
    text = p.read_text(encoding="utf-8")
    line = f"\n> **事实编号**：{rng}（完整清单见 [/references/source-facts.md](/references/source-facts.md)）\n"
    if "**事实编号**" in text:
        print(f"skip (已存在): {name}")
        continue
    m = re.search(r"^# .+$", text, re.M)
    if not m:
        print(f"NO H1: {name}")
        continue
    new = text[: m.end()] + "\n" + line + text[m.end() :]
    p.write_text(new, encoding="utf-8")
    print(f"ok: {name} <- {rng}")
