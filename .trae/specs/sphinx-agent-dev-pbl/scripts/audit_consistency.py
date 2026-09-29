#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一致性审计脚本（Consistency Audit）

用途：给本方案这类"多文档套装"做完整性审计的自动部分。
来源：R8 完整性审计（session sc-20260929-pbl-audit）固化。
对应需求：spec.md NFR-4（跨文档一致性）。

它做五件事——前两件是"完备性"，后两件是"一致性"（真正的缺陷高发区）：
  1. 相对链接可达性（最弱判据，但成本低，先跑）
  2. 幽灵文件（被引用的文件是否真实存在）
  3. 派生数字（文档声称的行数/张数 vs 实测值）
  4. 可复制命令的逐字一致性（同一命令多处出现是否一致）
  5. 节号引用可达性（"review.md 3.5 节"里的 3.5 是否真的存在）

退出码：0 = 全部通过；1 = 有失败项。
用法：python scripts/audit_consistency.py [--root .]
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

# 允许的"学生待创建文件"白名单——这些被引用但不存在是正常的
PLANNED_ARTIFACTS = {
    "api-draft.md", "api.md", "api.py", "architecture.md",
    "diff-notes.md", "glossary.md",
    "index.md", "usage.md", "xxx.md", "docs.yml",
    "drafts/calculator-draft.md", "docs/api-draft.md", "docs/api.md",
    "docs/drafts/diff-notes.md", "docs/snippets.md",
    ".github/workflows/docs.yml",
}
# ⚠️ 已移出：calculator-draft.md（R9 之前只是"计划中"，现已真实存在于
#    teacher/task6-tier-a/。按 I-15——"实物必须真实存在"——它不能再被豁免，
#    否则"计划中"就成了永不兑现的免死金牌。）

# 演示环境脚本（不在本仓库内，属临时环境）
EXTERNAL_SCRIPTS = {"make_shots.py", "make_shots2.py", "shells.py", "pyvenv.cfg"}

# 会在学生项目中创建、但当前仓库不存在的路径（占位引用）
FUTURE_PATHS = {"drafts/diff-notes.md"}

# 跨领域迁移示例里的文件名——它们出现在"别的领域也适用"的举例中，
# 本仓库刻意不提供这些文件（提供反而是错的）。
# 见 patterns/config-as-artifact.md 的"跨场景迁移示例"。
CROSS_DOMAIN_EXAMPLES = {"config.yaml", "deployment.yaml", "configs/base.yaml"}

# 无路径前缀的裸文件名——它们在文中通常是"泛指某类文件"而非"引用某具体文件"。
# audit_consistency.py 属于此列：文中常以裸名指代"那个审计脚本"，
# 其真实位置在 scripts/ 下，已在 bases 中覆盖。
BARE_NAMES = {"conf.py", "index.md", "index.rst", "requirements.txt",
              "audit_consistency.py"}

# 模式文档——跨领域迁移示例的来源，其举例文件名不应计入幽灵检查
PATTERN_FILES = {"config-as-artifact.md"}

# 审计报告类文件——它们会引用（并批判）错误写法，不应计入一致性冲突；
# 模式文档同理（其举例是"别的领域的文件长这样"）
AUDIT_FILES = {"insight.md", "review.md"} | PATTERN_FILES

# 按相对路径排除的文件（比按文件名精确，避免误伤同名 README）
# scripts/README.md 是审计工具自身的说明文档——它必然要为"举例说明某类缺陷"
# 而引用错误节号，与审计报告同性质。
AUDIT_FILE_PATHS = {"scripts/README.md"}

# 描述性/警示性语境标记——出现这些词的行是在"提醒不要这么写"，不算真的在用
WARNING_MARKERS = ("不要写成", "勿写成", "别写成", "错写成", "那会", "会报", "必失败", "错误写法")


def strip_code(text: str) -> str:
    """去掉围栏代码块与行内代码，避免把示例当链接/文件名。"""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`]*`", "", text)
    return text


def scan_links(root: Path) -> tuple[int, list[tuple[str, str]]]:
    checked, bad = 0, []
    for md in sorted(root.rglob("*.md")):
        t = strip_code(md.read_text(encoding="utf-8"))
        for m in re.finditer(r"\]\(([^)]+)\)", t):
            url = m.group(1).strip().split("#")[0]
            if not url or url.startswith(("http", "#", "mailto:")):
                continue
            checked += 1
            if not (md.parent / url).exists():
                bad.append((str(md.relative_to(root)), url))
    return checked, bad


def scan_ghost_files(root: Path) -> list[str]:
    """扫描被反引号包起来的文件名，检查是否存在（含多基准解析）。"""
    pat = re.compile(r"`([A-Za-z0-9_\-./]+\.(?:md|py|png|txt|bat|sh|yml|yaml|toml|cfg|example|json))`")
    bases = [root, root / "handbook", root / "teacher",
             root / "warmup-docs", root / "templates", root / "handbook" / "shots",
             root / "teacher" / "task6-tier-a", root / "starters",
             root / "starters" / ".github" / "workflows"]
    ghosts = []
    seen = set()
    for md in sorted(root.rglob("*.md")):
        if md.name in AUDIT_FILES:
            continue  # 审计报告会为"批判"而提及幽灵文件名
        for m in pat.finditer(md.read_text(encoding="utf-8")):
            name = m.group(1)
            if name in seen or name.startswith(("../", "http")):
                continue
            seen.add(name)
            if (name in PLANNED_ARTIFACTS or name in EXTERNAL_SCRIPTS
                    or name in BARE_NAMES or name in FUTURE_PATHS
                    or name in CROSS_DOMAIN_EXAMPLES):
                continue
            if not any((b / name).exists() for b in bases):
                ghosts.append(name)
    return sorted(ghosts)


def scan_derived_counts(root: Path) -> tuple[list[tuple[str, int, int]], list[tuple[str, str, int, int]]]:
    """比对文档中声称的行数/张数与实测值。"""
    real: list[tuple[str, int, int]] = []      # (file, claimed, actual)
    # 1) "N 行" 声明（仅检查 top-level md 的自述表）
    guide = root / "teacher" / "TEACHER-GUIDE.md"
    if guide.exists():
        txt = guide.read_text(encoding="utf-8")
        # 匹配 `文件名.md` ... N 行
        for m in re.finditer(r"`(?:[\w\-]*/)?([\w\-]+\.md)`[^|]*\|\s*(?:≈)?\s*(\d+)\s*行", txt):
            fname, claimed = m.group(1), int(m.group(2))
            p = root / "teacher" / fname
            if not p.exists():
                p = root / fname
            if p.exists():
                actual = len(p.read_text(encoding="utf-8").splitlines())
                # 允许 ±5 行误差（≈ 前缀）
                real.append((fname, claimed, actual))
    # 2) 截图张数声明
    shots_dir = root / "handbook" / "shots"
    pngs: list[tuple[str, str, int, int]] = []
    if shots_dir.exists():
        actual_png = len(list(shots_dir.glob("*.png")))
        for md in sorted(root.rglob("*.md")):
            txt = md.read_text(encoding="utf-8")
            for m in re.finditer(r"(\d+)\s*张(?:已填|示意图|PNG)", txt):
                claimed = int(m.group(1))
                if claimed != actual_png:
                    pngs.append((str(md.relative_to(root)), f"声称 {claimed} 张", claimed, actual_png))
    return real, pngs


def scan_command_consistency(root: Path) -> list[tuple[str, str]]:
    """
    扫描关键命令在所有文档中的出现形式。

    区分两类：
      - 错误写法（会失败）：`sphinx-build -b html . _build/html`（在根目录找 conf.py）
      - 等价写法（都正确）：`python -m sphinx -b html docs ...` 与 `sphinx-build -b html docs ...`
        —— 后者等价，不算冲突，仅提示统一。
    审计报告类文件（insight.md / review.md）引用错误写法是为批判它，不计入。
    """
    wrong = r"sphinx-build -b html \.\s+_build/html"
    right_forms = [
        r"python -m sphinx -b html docs docs/_build/html",
        r"sphinx-build -b html docs docs/_build/html",
    ]
    issues: list[tuple[str, str]] = []

    # 1) 错误写法：任何非审计文件出现即报错（排除"警示语境"）
    wrong_hits = []
    for md in sorted(root.rglob("*.md")):
        rel = str(md.relative_to(root))
        if md.name in AUDIT_FILES:
            continue
        for line in md.read_text(encoding="utf-8").splitlines():
            if re.search(wrong, line) and not any(w in line for w in WARNING_MARKERS):
                wrong_hits.append(f"{rel}:{line.strip()[:70]}")
                break
    if wrong_hits:
        issues.append(("错误构建命令（在根目录构建，必失败）",
                       " ｜ ".join(wrong_hits)))

    # 2) 等价写法混用：仅提示，不判失败
    forms = {p: [] for p in right_forms}
    for md in sorted(root.rglob("*.md")):
        rel = str(md.relative_to(root))
        if md.name in AUDIT_FILES:
            continue
        raw = md.read_text(encoding="utf-8")
        for p in right_forms:
            if re.search(p, raw, re.M):
                forms[p].append(rel)
    used = {p: v for p, v in forms.items() if v}
    if len(used) > 1:
        detail = " ｜ ".join(f"`{p}`: {len(v)} 处" for p, v in used.items())
        issues.append(("等价写法未统一（非错误，建议统一为 python -m 形式）", detail))
    return issues


def scan_section_refs(root: Path) -> list[tuple[str, str, str]]:
    """
    扫描"文档 + 节号"形式的引用，验证目标文档中确实存在该节号。

    来源：R12 抓到的真实缺陷——多处写"S7-3 → review.md 3.5 节"，
    但 review.md 并无 3.5 节（真实位置是 SCORING-SHEET.md §3.5）。
    这类"指向错文件/错节号"的引用不会被链接检查发现（链接本身可达），
    也不会被幽灵检查发现（文件名有歧义），属**独立缺陷类型**。

    返回 [(引用所在文件, 被引文档, 节号)]
    """
    # 形如 `xxx.md` §3.5 / `xxx.md` 3.5 节 / xxx.md 第 3.5 节
    pat = re.compile(r"`?([A-Za-z0-9_\-]+\.md)`?\s*(?:§|第)?\s*(\d+\.\d+)\s*(?:节|节「)?")
    issues: list[tuple[str, str, str]] = []
    for md in sorted(root.rglob("*.md")):
        rel = str(md.relative_to(root)).replace("\\", "/")
        if md.name in AUDIT_FILES or rel in AUDIT_FILE_PATHS:
            continue  # 审计报告/工具文档会引用（并批判）错误节号
        for m in pat.finditer(md.read_text(encoding="utf-8")):
            target, sec = m.group(1), m.group(2)
            # 定位被引文档
            cands = list(root.rglob(target))
            if not cands:
                continue  # 文件不存在由幽灵检查负责
            tdoc = cands[0]
            if tdoc.resolve() == md.resolve():
                continue
            tt = tdoc.read_text(encoding="utf-8")
            # 目标文档中是否存在该节号（标题或表格行开头）
            if not re.search(rf"(?:^|\n)#{{1,4}}\s*{re.escape(sec)}\b", tt):
                issues.append((rel, target, sec))
    return issues


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="方案根目录")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    print("=" * 68)
    print("一致性审计（Consistency Audit）  root =", root)
    print("=" * 68)
    failed = False

    # 1. 链接
    checked, bad = scan_links(root)
    print(f"\n[1/5] 相对链接可达性 … 检查 {checked} 条，断链 {len(bad)} 条")
    for f, u in bad:
        print(f"      ✗ {f} -> {u}")
    if bad:
        failed = True

    # 2. 幽灵文件
    ghosts = scan_ghost_files(root)
    print(f"\n[2/5] 幽灵文件 … 发现 {len(ghosts)} 个")
    for g in ghosts:
        print(f"      ✗ {g}")
    if ghosts:
        failed = True

    # 3. 派生数字
    lines, pngs = scan_derived_counts(root)
    n_bad = 0
    print(f"\n[3/5] 派生数字（行数 / 张数）")
    for fname, claimed, actual in lines:
        ok = abs(claimed - actual) <= 5
        mark = "✓" if ok else "✗"
        if not ok:
            n_bad += 1
        print(f"      {mark} {fname}: 声称 {claimed} 行 / 实际 {actual} 行")
    for f, label, claimed, actual in pngs:
        n_bad += 1
        print(f"      ✗ {f}: {label} / 实际 {actual} 张")
    if n_bad == 0:
        print("      ✓ 派生数字与实测一致")
    else:
        failed = True

    # 4. 命令一致性
    cmds = scan_command_consistency(root)
    hard = [c for c in cmds if "必失败" in c[0]]   # 真错误：会跑不起来
    soft = [c for c in cmds if "非错误" in c[0]]   # 提示：等价写法未统一
    print(f"\n[4/5] 可复制命令的一致性 … 错误写法 {len(hard)} 处 / 等价混用 {len(soft)} 处")
    for label, detail in cmds:
        mark = "✗" if "必失败" in label else "⚠"
        print(f"      {mark} {label}")
        print(f"        {detail}")
    if not cmds:
        print("      ✓ 关键命令在各处写法一致")
    if hard:
        failed = True

    # 5. 节号引用可达性
    srefs = scan_section_refs(root)
    print(f"\n[5/5] 节号引用可达性 … 失效 {len(srefs)} 处")
    for src, tgt, sec in srefs:
        print(f"      ✗ {src}: 引用 `{tgt}` §{sec} —— 该节号在目标文档中不存在")
    if srefs:
        failed = True

    print("\n" + "=" * 68)
    print("总判定：" + ("❌ 存在失败项，请修复后重跑" if failed else "✅ 全部通过"))
    print("=" * 68)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
