#!/usr/bin/env python3
"""R 阶段数量事实计数脚本 v4：后端端点清单（vibeknow/cli @ v0.9.2 / 93a26ec）。

口径：仅统计 client/ 目录下非测试 Go 文件中，出现在 http.Do / DoRaw / NewRequest
等调用实参里的以 "/v" 开头的路径字面量；fmt.Sprintf 模板按其格式串前缀归一化为
"前缀/{param}" 形式以避免同一端点被参数值撑开成多行。
"""
import re
import sys
from pathlib import Path

FMT = re.compile(r'fmt\.Sprintf\(\s*"(/[^"]*)"')
LIT = re.compile(r'"(/v[0-9][^"]*)"')


def norm(p: str) -> str:
    """把带 %s / %d 的路径归一化成 {param}。"""
    return re.sub(r"%[sdv]", "{param}", p)


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    total: set[str] = set()
    for svc in ("account", "figlens", "vectoria", "vibeknow"):
        d = root / "client" / svc
        eps: set[str] = set()
        for f in sorted(d.glob("*.go")):
            if f.name.endswith("_test.go"):
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
            for m in FMT.finditer(text):
                eps.add(norm(m.group(1)))
            for m in LIT.finditer(text):
                eps.add(norm(m.group(1)))
        total |= eps
        print(f"# client/{svc}: 端点路径去重数 = {len(eps)}")
        for e in sorted(eps):
            print(f"    {e}")
        print()
    print(f"# client/ 四服务端端点路径合计去重数 = {len(total)}")
    print()

    # 每个后端服务被哪个命令族使用（internal/endpoints）
    ep = root / "internal" / "endpoints"
    for f in sorted(ep.glob("*.go")):
        if f.name.endswith("_test.go"):
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        names = re.findall(r'"(account|figlens|vectoria|vibeknow)"', text)
        print(f"# internal/endpoints/{f.name}: 提及服务 = {sorted(set(names))}")
    print()

    # i18n 词条按前缀分组
    s = (root / "internal" / "i18n" / "strings.go").read_text(encoding="utf-8", errors="replace")
    keys = re.findall(r'^\s*"([a-z0-9_.]+)":\s*"', s, re.M)
    print(f"# i18n 词条总数 = {len(keys)}，去重后 = {len(set(keys))}")
    from collections import Counter
    c = Counter(k.split(".")[0] for k in keys)
    for k, v in sorted(c.items(), key=lambda x: -x[1]):
        print(f"    {k}: {v}")
    print()

    # internal 各包行数（非测试）
    print("# internal 各包非测试代码行数")
    rows = []
    for d in sorted({f.parent for f in (root / "internal").rglob("*.go")
                     if not f.name.endswith("_test.go")}):
        n = sum(len(f.read_text(encoding="utf-8", errors="replace").splitlines())
                for f in d.glob("*.go") if not f.name.endswith("_test.go"))
        rows.append((d.relative_to(root).as_posix(), n))
    for p, n in sorted(rows, key=lambda x: -x[1]):
        print(f"    {p}: {n}")
    print(f"# internal 非测试代码总行数 = {sum(n for _, n in rows)}")


if __name__ == "__main__":
    main()
