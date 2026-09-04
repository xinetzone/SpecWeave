#!/usr/bin/env python3
"""V阶段门驱动同步：以「暂存态快照树真值」为地面真值，修复提交态索引计数面与 toctree。

变更范围（仅工作树文件，后续显式 git add）：
1. doc/bundles/index.md          — frontmatter/计数行/域节标题/分组表束数列/幽灵表行
2. doc/bundles/jishu/index.md    — 域节计数文本/分组表/toctree 幽灵组（iot）
3. doc/bundles/jishu/ai/index.md — toctree 幽灵条目（mobile-use/tiktoken）
4. ai-app-survival 束 3 个 index.md — 补 toctree 接线（concepts/references/log）

真值来源：.temp/gate-snapshot（git checkout-index 导出的暂存态，含我方 3 束，
不含他会话 untracked WIP）。CI 在干净 checkout 运行门禁，语义等价。
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

REPO = Path(r"d:\spaces\SpecWeave\projects\awesome-okf-xs")
SNAP = REPO / ".temp" / "gate-snapshot"
APPLY = "--apply" in sys.argv

# --- 从快照脚本加载门禁自身的树计数/解析逻辑（保证口径与 gate 完全一致）---
spec = importlib.util.spec_from_file_location(
    "gate_bundles", SNAP / "scripts" / "check-bundles-index.py"
)
gate = importlib.util.module_from_spec(spec)
sys.modules["gate_bundles"] = gate
spec.loader.exec_module(gate)

tree = gate.scan_tree(SNAP / "doc" / "bundles")
print(
    f"[真值] 快照树: {tree.total_domains} 域 / {tree.total_groups} 组 / "
    f"{tree.total_bundles} 束"
)
plan: list[str] = []


def resolve_in_snap(link: str) -> Path | None:
    return gate._resolve_row_link(link, SNAP / "doc" / "bundles")


# ===========================================================================
# 1) doc/bundles/index.md —— 总索引五面对账
# ===========================================================================
def fix_total_index() -> None:
    p = REPO / "doc" / "bundles" / "index.md"
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    out: list[str] = []
    current_dom: str | None = None
    in_toctree = False
    changed = 0

    for ln in lines:
        bare = ln.rstrip("\n").rstrip("\r")
        if gate._FENCE_OPEN.match(bare):
            in_toctree = True
            out.append(ln)
            continue
        if in_toctree:
            if gate._FENCE_CLOSE.match(bare):
                in_toctree = False
            out.append(ln)
            continue

        # 1a) frontmatter
        m = re.match(r"^(total_bundles|groups|domains)\s*:\s*(\d+)\s*$", bare)
        if m:
            key = m.group(1)
            val = {
                "total_bundles": tree.total_bundles,
                "groups": tree.total_groups,
                "domains": tree.total_domains,
            }[key]
            if int(m.group(2)) != val:
                plan.append(f"[总索引] FM {key}: {m.group(2)} -> {val}")
                ln = f"{key}: {val}\n"
                changed += 1
            out.append(ln)
            continue

        # 1b) 正文计数行：「当前共 **N 个知识包**……**N 个技术域、N 个分组**」
        if _COUNT_LINE_BUNDLES.search(bare):
            new = _COUNT_LINE_BUNDLES.sub(f"**{tree.total_bundles} 个知识包**", bare)
            new = _COUNT_LINE_SPLIT.sub(
                f"**{tree.total_domains} 个技术域、{tree.total_groups} 个分组**", new
            )
            if new != bare:
                plan.append("[总索引] 正文计数行 -> 同步树真值")
                changed += 1
            out.append(new + "\n")
            continue

        # 1c) 域节标题
        sec = gate._SECTION.match(bare)
        if sec:
            dom = sec.group("link").split("/")[0]
            current_dom = dom
            tb = sum(tree.domains.get(dom, {}).values())
            tg = len(tree.domains.get(dom, {}))
            if int(sec.group("bundles")) != tb or int(sec.group("groups")) != tg:
                plan.append(f"[总索引] {dom}/ 节标题 {sec.group('bundles')}束{sec.group('groups')}组 -> {tb}束{tg}组")
                new = re.sub(
                    r"·\s*\d+\s*束\s*·\s*\d+\s*组",
                    f"· {tb} 束 · {tg} 组",
                    bare,
                )
                out.append(new + "\n")
                changed += 1
                continue
            out.append(ln)
            continue

        # 1d) 分组表行
        row = gate._TABLE_ROW.match(bare)
        if row and current_dom:
            link = row.group("link")
            resolved = resolve_in_snap(link)
            if resolved is None:
                plan.append(f"[总索引] {current_dom}/ 删除幽灵表行: 「{link}」(快照树不存在)")
                changed += 1
                continue  # 丢弃整行
            parts = [x for x in link.split("/") if x]
            if link == f"{current_dom}/index.md":
                truth = sum(tree.domains.get(current_dom, {}).values())
            elif len(parts) >= 2:
                truth = tree.domains.get(current_dom, {}).get(parts[1], 0)
            else:
                truth = int(row.group("count"))
            if int(row.group("count")) != truth:
                plan.append(f"[总索引] {current_dom}/ 表行 {link} 束数 {row.group('count')} -> {truth}")
                new = re.sub(
                    r"^(\|\s*\[[^\]]*\]\([^)]+\)\s*\|\s*)\d+(\s*\|)",
                    lambda m: f"{m.group(1)}{truth}{m.group(2)}",
                    bare,
                    count=1,
                )
                out.append(new + "\n")
                changed += 1
                continue
            out.append(ln)
            continue

        if bare.startswith("#"):
            current_dom = None
        out.append(ln)

    if APPLY:
        p.write_text("".join(out), encoding="utf-8")
    print(f"[总索引] 变更 {changed} 处")


_COUNT_LINE_BUNDLES = re.compile(r"\*\*\s*(\d+)\s*个知识包\s*\*\*")
_COUNT_LINE_SPLIT = re.compile(r"\*\*\s*(\d+)\s*个(?:技术|学科)域、(\d+)\s*个分组\s*\*\*")


# ===========================================================================
# 2) doc/bundles/jishu/index.md —— 技术域索引（计数文本 + 分组表 + toctree）
# ===========================================================================
def fix_jishu_index() -> None:
    p = REPO / "doc" / "bundles" / "jishu" / "index.md"
    text = p.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    groups = tree.domains["jishu"]  # {group: bundles}
    out: list[str] = []
    in_toctree = False
    changed = 0

    _row = re.compile(r"^\|\s*\[(?P<title>[^\]]*)\]\((?P<link>[^)]+)\)\s*\|\s*(?P<count>\d+)\s*\|")

    for ln in lines:
        bare = ln.rstrip("\n").rstrip("\r")
        if gate._FENCE_OPEN.match(bare):
            in_toctree = True
            out.append(ln)
            continue
        if in_toctree:
            body = bare.strip()
            if gate._FENCE_CLOSE.match(bare):
                in_toctree = False
            elif body and not body.startswith(":"):
                entry_grp = body.split("/")[0]
                if entry_grp not in groups:
                    plan.append(f"[jishu索引] toctree 删除幽灵条目: {body}")
                    changed += 1
                    continue
            out.append(ln)
            continue

        m = _row.match(bare)
        if m:
            parts = [x for x in m.group("link").split("/") if x]
            grp = parts[0] if parts else ""
            if grp not in groups:
                plan.append(f"[jishu索引] 删除幽灵表行: 「{m.group('link')}」(快照树无 {grp}/)")
                changed += 1
                continue
            truth = groups[grp]
            if int(m.group("count")) != truth:
                plan.append(f"[jishu索引] 表行 {grp} 束数 {m.group('count')} -> {truth}")
                new = re.sub(
                    r"^(\|\s*\[[^\]]*\]\([^)]+\)\s*\|\s*)\d+(\s*\|)",
                    lambda mm: f"{mm.group(1)}{truth}{mm.group(2)}",
                    bare,
                    count=1,
                )
                out.append(new + "\n")
                changed += 1
                continue
            out.append(ln)
            continue

        out.append(ln)

    if APPLY:
        p.write_text("".join(out), encoding="utf-8")
    print(f"[jishu索引] 变更 {changed} 处")


# ===========================================================================
# 3) doc/bundles/jishu/ai/index.md —— 删除 toctree 幽灵条目
# ===========================================================================
def fix_ai_index() -> None:
    p = REPO / "doc" / "bundles" / "jishu" / "ai" / "index.md"
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    out: list[str] = []
    in_toctree = False
    changed = 0
    # 快照树中 ai 下真实存在的组目录（含 index.md 的子目录）
    ai_dir = SNAP / "doc" / "bundles" / "jishu" / "ai"
    live = {d.name for d in ai_dir.iterdir() if d.is_dir() and (d / "index.md").is_file()}

    for ln in lines:
        bare = ln.rstrip("\n").rstrip("\r")
        if gate._FENCE_OPEN.match(bare):
            in_toctree = True
            out.append(ln)
            continue
        if in_toctree:
            body = bare.strip()
            if gate._FENCE_CLOSE.match(bare):
                in_toctree = False
            elif body and not body.startswith(":"):
                grp = body.split("/")[0]
                if grp not in live:
                    plan.append(f"[ai索引] toctree 删除幽灵条目: {body}（快照树无 {grp}/）")
                    changed += 1
                    continue
            out.append(ln)
            continue
        out.append(ln)

    if APPLY:
        p.write_text("".join(out), encoding="utf-8")
    print(f"[ai索引] 变更 {changed} 处")


# ===========================================================================
# 4) ai-app-survival 束补 toctree（文件完整但缺接线）
# ===========================================================================
def fix_survival_toctrees() -> None:
    base = REPO / "doc" / "bundles" / "jishu" / "ai" / "ai-agent" / "ai-app-survival"
    blocks = {
        "index.md": ["concepts/index", "references/index", "log"],
        "concepts/index.md": [
            "00-triple-squeeze",
            "01-token-economics",
            "02-model-engulfment",
            "03-model-as-app",
            "04-avoidance-trap",
            "05-two-escape-routes",
        ],
        "references/index.md": ["article-source", "verification"],
    }
    for rel, entries in blocks.items():
        f = base / rel
        text = f.read_text(encoding="utf-8")
        if "toctree" in text:
            plan.append(f"[survival] {rel} 已有 toctree，跳过")
            continue
        block = "\n\n```{toctree}\n:maxdepth: 1\n\n" + "\n".join(entries) + "\n```\n"
        plan.append(f"[survival] {rel} 追加 toctree（{len(entries)} 条目）")
        if APPLY:
            f.write_text(text.rstrip() + block, encoding="utf-8")
    print(f"[survival] 处理 {len(blocks)} 个文件")


if __name__ == "__main__":
    print("=" * 70)
    print("DRY RUN" if not APPLY else "APPLY")
    print("=" * 70)
    fix_total_index()
    fix_jishu_index()
    fix_ai_index()
    fix_survival_toctrees()
    print("-" * 70)
    for item in plan:
        print(" ", item)
    print(f"\n共 {len(plan)} 项计划变更" + ("（已写入）" if APPLY else "（未写入，加 --apply 执行）"))
