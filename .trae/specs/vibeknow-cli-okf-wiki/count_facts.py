#!/usr/bin/env python3
"""R 阶段数量事实计数脚本（vibeknow/cli @ v0.9.2 / 93a26ec）。

纪律：所有 "X 个 / N 份 / Z 处" 数量陈述必须由本脚本产出，R 阶段人工枚举结果不得作为唯一来源。
用法：python count_facts.py <cli-root>
"""
import re
import subprocess
import sys
from pathlib import Path


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def go_files(root: Path, sub: str, tests: bool = True) -> list[Path]:
    files = sorted((root / sub).rglob("*.go"))
    if not tests:
        files = [f for f in files if not f.name.endswith("_test.go")]
    return files


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    print(f"# 信源锚定")
    print(f"commit: {git(root, 'rev-parse', 'HEAD')}")
    print(f"tag: {git(root, 'describe', '--tags', '--always')}")
    print()

    # ---- 1. 目录/文件规模 ----
    print(f"# 规模计数")
    for sub in ("cmd", "internal", "client", "tests", "skills", "npm", "scripts"):
        d = root / sub
        if not d.exists():
            print(f"{sub}: MISSING")
            continue
        gos = go_files(root, sub)
        non_test = [f for f in gos if not f.name.endswith("_test.go")]
        pkg_dirs = sorted({f.parent for f in non_test})
        print(f"{sub}: go_all={len(gos)} go_non_test={len(non_test)} pkg_dirs={len(pkg_dirs)}")
    all_go = list(root.rglob("*.go"))
    all_non_test = [f for f in all_go if not f.name.endswith("_test.go")]
    print(f"repo_total: go_all={len(all_go)} go_non_test={len(all_non_test)}")
    print()

    # ---- 2. cmd/ 包目录与文件 ----
    cmd_root = root / "cmd"
    cmd_pkgs = sorted({f.parent for f in go_files(root, "cmd", tests=False)})
    print(f"# cmd 包目录 ({len(cmd_pkgs)})")
    for p in cmd_pkgs:
        rel = p.relative_to(root).as_posix()
        n = len([f for f in p.glob("*.go") if not f.name.endswith("_test.go")])
        print(f"  {rel}: {n}")
    print()

    # ---- 3. Cobra 子命令（Use 字段）----
    # 只统计 *Command{ 变量声明中的 Use: 首词
    cmd_re = re.compile(r"\bUse:\s*\"([^\"]+)\"")
    uses: dict[str, list[str]] = {}
    for f in go_files(root, "cmd", tests=False):
        text = f.read_text(encoding="utf-8", errors="replace")
        for m in cmd_re.finditer(text):
            raw = m.group(1).strip()
            head = raw.split()[0] if raw.split() else ""
            uses.setdefault(head, []).append(f"{f.relative_to(root).as_posix()}:{raw}")
    # 顶层命令：root.go 的 Use 与各子包 AddCommand
    print(f"# cobra Use 取值去重数 = {len(uses)}")
    for k in sorted(uses):
        print(f"  {k}  (x{len(uses[k])})")
    print()

    # ---- 4. 顶层命令树（root.go）----
    root_go = (cmd_root / "root.go").read_text(encoding="utf-8", errors="replace")
    addcmd = re.findall(r"AddCommand\(([^)]*)\)", root_go, re.S)
    top_cmds: list[str] = []
    for grp in addcmd:
        for token in re.findall(r"([A-Za-z_][A-Za-z0-9_]*)Cmd\b", grp):
            if token not in top_cmds:
                top_cmds.append(token)
    print(f"# root.go AddCommand 组数 = {len(addcmd)}")
    print(f"# root.go 顶层命令变量（去重）= {len(top_cmds)}")
    for t in top_cmds:
        print(f"  {t}")
    print()

    # ---- 5. 旗标注册（Flags()/String()/Bool() 等）----
    flag_pat = re.compile(
        r"\.(?:Flags\(\)\.|PersistentFlags\(\)\.)"
        r"(String|StringVar|StringP|Bool|BoolVar|BoolP|Int|IntVar|IntP|Duration|"
        r"StringSlice|StringArray|Float64|Count)\("
    )
    flag_total = 0
    per_file: list[tuple[str, int]] = []
    for f in go_files(root, "cmd", tests=False):
        text = f.read_text(encoding="utf-8", errors="replace")
        n = len(flag_pat.findall(text))
        if n:
            per_file.append((f.relative_to(root).as_posix(), n))
            flag_total += n
    per_file.sort(key=lambda x: -x[1])
    print(f"# cmd/ 旗标注册调用总数 = {flag_total}（含重复名，不同文件各自统计）")
    for p, n in per_file[:15]:
        print(f"  {p}: {n}")
    print()

    # ---- 6. 旗标名去重 ----
    flagname = re.compile(
        r"\.(?:Flags\(\)\.|PersistentFlags\(\)\.)"
        r"(?:String|StringVar|StringP|Bool|BoolVar|BoolP|Int|IntVar|IntP|Duration|"
        r"StringSlice|StringArray|Float64|Count)\(\s*\"([a-zA-Z0-9][a-zA-Z0-9-]*)\""
    )
    names: set[str] = set()
    for f in go_files(root, "cmd", tests=False):
        text = f.read_text(encoding="utf-8", errors="replace")
        names.update(flagname.findall(text))
    print(f"# cmd/ 旗标名去重数 = {len(names)}")
    print("  " + ", ".join(sorted(names)))
    print()

    # ---- 7. 退出码 ----
    exitfile = cmd_root / "exitcode.go"
    ec_text = exitfile.read_text(encoding="utf-8", errors="replace")
    ec_defs = re.findall(r"^\s*(Exit[A-Za-z0-9]+)\s+(?:int|=\s*)", ec_text, re.M)
    ec_const = re.findall(r"(Exit[A-Za-z0-9]+)\s*=\s*(\d+)", ec_text)
    print(f"# cmd/exitcode.go 退出码常量 = {len(ec_const)}")
    for k, v in ec_const:
        print(f"  {k} = {v}")
    print()

    # ---- 8. skills ----
    sk = root / "skills"
    if sk.exists():
        skill_dirs = sorted(d for d in sk.iterdir() if d.is_dir())
        skill_files = sorted(sk.rglob("SKILL.md"))
        print(f"# skills: 目录数 = {len(skill_dirs)}, SKILL.md 数 = {len(skill_files)}")
        for d in skill_dirs:
            print(f"  {d.name}")
        print()

    # ---- 9. tests/integration ----
    tdir = root / "tests"
    if tdir.exists():
        tgo = go_files(root, "tests")
        tnames = sorted({f.name for f in tgo})
        print(f"# tests/: go 文件数 = {len(tgo)}, 去重文件名数 = {len(tnames)}")
        for n in tnames:
            print(f"  {n}")
        print()

    # ---- 10. internal 包清单 ----
    ipkgs = sorted({f.parent for f in go_files(root, "internal", tests=False)})
    print(f"# internal 包目录数 = {len(ipkgs)}")
    for p in ipkgs:
        print(f"  {p.relative_to(root).as_posix()}")
    print()

    # ---- 11. client 包清单 ----
    cpkgs = sorted({f.parent for f in go_files(root, "client", tests=False)})
    print(f"# client 包目录数 = {len(cpkgs)}")
    for p in cpkgs:
        print(f"  {p.relative_to(root).as_posix()}")
    print()

    # ---- 12. 关键符号存在性（V 阶段将换独立手段复核）----
    symbols = [
        "cmdutil.Gate", "ActionID", "action.key", "jobs.jsonl",
        "VIBEKNOW_ASSUME_YES", "VIBEKNOW_OUTPUT",
        "wait_budget_expired", "resend_safe", "not_submitted", "indeterminate",
        "export_confirmation", "scene_edit_confirmation",
        "resource_ready", "SubtitleStylePatch",
    ]
    print("# 关键符号出现位置")
    for sym in symbols:
        hits = subprocess.run(
            ["git", "-C", str(root), "grep", "-n", "--", sym],
            capture_output=True, text=True,
        ).stdout.strip().splitlines()
        print(f"  {sym}: {len(hits)} 处")
        for h in hits[:4]:
            print(f"      {h}")


if __name__ == "__main__":
    main()
