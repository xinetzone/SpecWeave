#!/usr/bin/env python3
"""R 阶段数量事实计数脚本 v3：命令树拓扑（vibeknow/cli @ v0.9.2 / 93a26ec）。

口径说明（与 v1/v2 不同，避免口径混用）：
- 顶层命令 = root.go 与 cmd/*.go 中 rootCmd.AddCommand(...) 的去重目标 + 各分组包的 Cmd 变量；
- 分组命令 = 13 个子包各自的 Cmd（api/auth/avatar/config/credits/doc/jobs/kb/profile/subtitle/theme/video/voice）；
- 叶子命令 = 顶层非分组命令 + 各分组的子命令；
- 统计以 AddCommand 调用点为准（排除 *_test.go），不使用 Use 字符串去重（会漏掉同名子命令）。
"""
import re
import sys
from pathlib import Path

GROUP_PKGS = [
    "api", "auth", "avatar", "config", "credits", "doc",
    "jobs", "kb", "profile", "subtitle", "theme", "video", "voice",
]


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    cmd_root = root / "cmd"
    files = [p for p in cmd_root.rglob("*.go") if not p.name.endswith("_test.go")]

    # 1. rootCmd.AddCommand 目标（顶层）
    top: list[str] = []
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"rootCmd\.AddCommand\(([^)]*)\)", text):
            for tok in re.findall(r"([A-Za-z_][A-Za-z0-9_]*)", m.group(1)):
                if tok not in top:
                    top.append(tok)
    print(f"# rootCmd.AddCommand 顶层目标 = {len(top)}")
    for t in top:
        print(f"  {t}")
    print()

    # 2. 各分组的 AddCommand（叶子）
    group_leaves: dict[str, list[str]] = {}
    for g in GROUP_PKGS:
        leaves: list[str] = []
        for f in sorted((cmd_root / g).glob("*.go")):
            if f.name.endswith("_test.go"):
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"Cmd\.AddCommand\(([^)]*)\)", text):
                for tok in re.findall(r"([A-Za-z_][A-Za-z0-9_]*)", m.group(1)):
                    if tok not in leaves:
                        leaves.append(tok)
        group_leaves[g] = leaves
        print(f"# vk {g} 子命令 = {len(leaves)}: {', '.join(leaves)}")
    print()

    # 3. create / init / doctor / version / update / completion 的子命令
    for name, f in (("create", cmd_root / "create.go"),):
        text = f.read_text(encoding="utf-8", errors="replace")
        subs = re.findall(r"createCmd\.AddCommand\(([^)]*)\)", text)
        print(f"# vk {name} 子命令 AddCommand 调用 = {len(subs)} -> {subs}")
    print()

    total_leaves = sum(len(v) for v in group_leaves.values())
    group_count = len(GROUP_PKGS)
    non_group_top = [t for t in top if not t.endswith("cmd.Cmd")]
    print(f"# 分组命令数 = {group_count}")
    print(f"# 顶层非分组命令数 = {len(non_group_top)}: {', '.join(non_group_top)}")
    print(f"# 叶子命令总数（分组子命令 + 顶层非分组）= {total_leaves} + {len(non_group_top)} = {total_leaves + len(non_group_top)}")
    print(f"# 命令节点总数（顶层 + 叶子）= {len(top)} + {total_leaves} = {len(top) + total_leaves}")
    print()

    # 4. video 分组细分
    print("# cmd/video 目录（叶子命令）")
    for f in sorted((cmd_root / "video").glob("*.go")):
        if f.name.endswith("_test.go"):
            continue
        print(f"  cmd/video/{f.name}")
    print()

    # 5. i18n 字符串条目数
    i18n = root / "internal" / "i18n"
    for f in sorted(i18n.glob("*.go")):
        if f.name.endswith("_test.go"):
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        n = len(re.findall(r'^\s*"[a-z0-9_.]+":\s*"', text, re.M))
        print(f"# i18n/{f.name} 词条数 = {n}")
    print()

    # 6. client 四个后端服务的端点数
    for svc in ("account", "figlens", "vectoria", "vibeknow"):
        d = root / "client" / svc
        eps: list[str] = []
        for f in sorted(d.glob("*.go")):
            if f.name.endswith("_test.go"):
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r'(?:url|path|Path)\s*[:=]\s*"(/[^"]*)"', text):
                eps.append(m.group(1))
        print(f"# client/{svc}: 端点路径字面量去重数 = {len(set(eps))}")
        for e in sorted(set(eps)):
            print(f"    {e}")
    print()


if __name__ == "__main__":
    main()
