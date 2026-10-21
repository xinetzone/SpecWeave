#!/usr/bin/env python3
"""R 阶段数量事实计数脚本 v2（vibeknow/cli @ v0.9.2 / 93a26ec）。

修正 v1 的旗标正则缺陷：v1 只匹配了「首参为字符串字面量」的注册形式，
漏掉 StringVar/BoolVar/IntVar 等「首参为指针」的形式，旗标名去重数被低估为 4。

v2 改用「抓取注册调用的完整实参列表，再取第一个字符串字面量」的口径，
并对同一文件内的同名旗标按 (文件, 旗标名) 计数，避免跨命令同名旗标被误合并。
"""
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

FLAG_TYPES = (
    "String|StringVar|StringP|StringVarP|Bool|BoolVar|BoolP|BoolVarP|"
    "Int|IntVar|IntP|IntVarP|Duration|DurationVar|"
    "StringSlice|StringSliceVar|StringArray|StringArrayVar|Float64|Float64Var|Count"
)
# Flags().X( / PersistentFlags().X( / FlagSet 上的同名方法
REG = re.compile(r"\.(?:Flags\(\)|PersistentFlags\(\)|PersistentFlags|Flags)\.(" + FLAG_TYPES + r")\(")


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def match_args(text: str, open_idx: int) -> str:
    """从 '(' 起做括号配对，返回参数字符串。"""
    depth = 0
    i = open_idx
    in_str = False
    esc = False
    quote = ""
    while i < len(text):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == quote:
                in_str = False
        else:
            if ch in "\"'`":
                in_str = True
                quote = ch
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return text[open_idx + 1:i]
        i += 1
    return ""


STR_LIT = re.compile(r'"([^"\\]*)"')


def flag_names_in_file(text: str) -> list[str]:
    names = []
    for m in REG.finditer(text):
        args = match_args(text, m.end() - 1)
        lits = STR_LIT.findall(args)
        if not lits:
            continue
        # 旗标名总是第一个字符串字面量；用法说明里的字面量在它之后
        name = lits[0]
        if not name or not re.match(r"^[a-zA-Z][a-zA-Z0-9-]*$", name):
            continue
        names.append(name)
    return names


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    print(f"# 信源: {git(root, 'describe', '--tags', '--always')} @ {git(root, 'rev-parse', 'HEAD')}")
    print()

    cmd_root = root / "cmd"
    files = sorted(p for p in cmd_root.rglob("*.go") if not p.name.endswith("_test.go"))

    per_file: list[tuple[str, int]] = []
    file_names: dict[str, list[str]] = {}
    all_pairs: set[tuple[str, str]] = set()
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        names = flag_names_in_file(text)
        if not names:
            continue
        rel = f.relative_to(root).as_posix()
        file_names[rel] = names
        per_file.append((rel, len(names)))
        for n in names:
            all_pairs.add((rel, n))

    per_file.sort(key=lambda x: -x[1])
    total = sum(n for _, n in per_file)
    print(f"# cmd/ 旗标注册调用总数（去重前，含同名重复注册）= {total}")
    print(f"# cmd/ (文件,旗标名) 去重对数 = {len(all_pairs)}")
    print(f"# cmd/ 旗标名全局去重数 = {len({n for _, n in all_pairs})}")
    print()
    print("## 每文件旗标数")
    for p, n in per_file:
        print(f"  {p}: {n}  -> {', '.join(sorted(set(file_names[p])))}")
    print()

    # create 命令旗标（AGENTS.md 称 vk create 有 21 个旗标）
    create_text = (cmd_root / "create.go").read_text(encoding="utf-8", errors="replace")
    preset_text = (cmd_root / "create_preset.go").read_text(encoding="utf-8", errors="replace")
    create_names = set(flag_names_in_file(create_text)) | set(flag_names_in_file(preset_text))
    print(f"# vk create 自有旗标数（create.go + create_preset.go，去重）= {len(create_names)}")
    print("  " + ", ".join(sorted(create_names)))
    print()

    # video 子命令旗标
    vid = sorted((cmd_root / "video").glob("*.go"))
    vid_pairs = set()
    for f in vid:
        if f.name.endswith("_test.go"):
            continue
        rel = f.relative_to(root).as_posix()
        for n in flag_names_in_file(f.read_text(encoding="utf-8", errors="replace")):
            vid_pairs.add((rel, n))
    print(f"# cmd/video 旗标 (文件,名) 去重对数 = {len(vid_pairs)}")
    print()

    # 事件类型（events 包 + 各处 vk_event type 字面量）
    ev_types: set[str] = set()
    for p in root.rglob("*.go"):
        if p.name.endswith("_test.go"):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r'"type"\s*:\s*"([a-z0-9_.]+)"', text):
            ev_types.add(m.group(1))
    print(f"# 代码中出现的 type 字面量去重数 = {len(ev_types)}")
    for t in sorted(ev_types):
        print(f"  {t}")
    print()

    # clerr 类型
    cl = (root / "internal" / "clerr" / "clerr.go").read_text(encoding="utf-8", errors="replace")
    types = re.findall(r"Type([A-Za-z]+)\s*=\s*\"(\w+)\"", cl)
    print(f"# clerr 错误类型 = {len(types)}")
    for k, v in types:
        print(f"  {v}")
    print()

    # 退出码使用点
    code_hits: dict[int, list[str]] = defaultdict(list)
    for p in root.rglob("*.go"):
        if p.name.endswith("_test.go"):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"WithCode\((\d+)\)", text):
            code_hits[int(m.group(1))].append(p.relative_to(root).as_posix())
        for m in re.finditer(r"^\s*Exit[A-Za-z]+\s*=\s*(\d+)", text, re.M):
            code_hits[int(m.group(1))].append(p.relative_to(root).as_posix() + " (const)")
    print(f"# 退出码使用点分布（WithCode / const 定义）")
    for c in sorted(code_hits):
        print(f"  exit {c}: {len(code_hits[c])} 处 -> {', '.join(sorted(set(code_hits[c])))}")
    print()

    # SKILL.md frontmatter
    for sk in sorted((root / "skills").rglob("SKILL.md")):
        text = sk.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^---\n(.*?)\n---", text, re.S)
        name = desc = ""
        if m:
            fm = m.group(1)
            nm = re.search(r"^name:\s*(.+)$", fm, re.M)
            ds = re.search(r"^description:\s*(.+)$", fm, re.M)
            name = nm.group(1).strip() if nm else ""
            desc = ds.group(1).strip() if ds else ""
        print(f"SKILL {sk.relative_to(root).as_posix()}: name={name!r} lines={len(text.splitlines())}")
        print(f"    desc={desc[:160]}")
    print()

    # npm wrapper
    pkg = root / "package.json"
    if pkg.exists():
        print("# package.json")
        print(pkg.read_text(encoding="utf-8", errors="replace"))
    npm_dir = root / "npm"
    if npm_dir.exists():
        for p in sorted(npm_dir.rglob("*")):
            if p.is_file():
                print(f"  npm/{p.relative_to(npm_dir).as_posix()} ({len(p.read_text(encoding='utf-8', errors='replace').splitlines())} lines)")


if __name__ == "__main__":
    main()
