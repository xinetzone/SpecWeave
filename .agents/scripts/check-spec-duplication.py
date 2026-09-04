"""Spec 近名目录查重门禁 — 防止新建 spec 与已有目录近名并存。

用法：
    python check-spec-duplication.py            # 全量扫描，输出并存对
    python check-spec-duplication.py --new <dir> # 单目录增量检查（CI 场景）

CI 集成（exit code）：
    0 = 无新并存，通过
    1 = 发现近名并存，失败（CI 阻断）
"""

import argparse
import sys
from pathlib import Path
from collections import defaultdict

# 版本校验
import site
site_pkg = Path(site.getsitepackages()[0]).resolve()
_sys_path = str(site_pkg.parent / ".." / "lib")  # 兼容
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

from lib.frontmatter import parse_frontmatter_unified

PROJ_ROOT = Path(__file__).resolve().parent.parent.parent
SPEC_ROOT = PROJ_ROOT / ".trae" / "specs"

# 相似度阈值：Levenshtein 距离 / 较长串长度 <= 此值视为近名
SIMILARITY_THRESHOLD = 0.4


def levenshtein(a: str, b: str) -> int:
    """计算两个字符串的 Levenshtein 距离。"""
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            insert_ = prev[j] + 1
            delete_ = curr[j - 1] + 1
            replace_ = prev[j - 1] + (ca != cb)
            curr.append(min(insert_, delete_, replace_))
        prev = curr
    return prev[-1]


def is_similar(a: str, b: str) -> bool:
    """判断两个名称是否近名（阈值 SIMILARITY_THRESHOLD）。"""
    if a == b:
        return True
    max_len = max(len(a), len(b))
    if max_len == 0:
        return False
    ratio = levenshtein(a, b) / max_len
    return ratio <= SIMILARITY_THRESHOLD


def collect_spec_dirs(root: Path) -> list[tuple[str, Path]]:
    """收集所有 spec 目录（含 spec.md 的子目录），返回 (name, path) 列表。"""
    dirs = []
    for d in root.rglob("spec.md"):
        parent = d.parent
        # 跳过 README 等文件本身
        if parent.name == "README.md":
            continue
        rel = parent.relative_to(root)
        dirs.append((rel.as_posix(), parent))
    return dirs


def find_duplicates(all_dirs: list[tuple[str, Path]]) -> list[tuple[str, str, Path, Path]]:
    """找出所有近名并存对。"""
    names = [name for name, _ in all_dirs]
    pairs = []
    seen = set()
    for i, (name_a, path_a) in enumerate(all_dirs):
        for name_b, path_b in all_dirs[i + 1:]:
            if is_similar(name_a, name_b):
                key = tuple(sorted([name_a, name_b]))
                if key not in seen:
                    seen.add(key)
                    pairs.append((name_a, name_b, path_a, path_b))
    return pairs


def check_single(new_dir_name: str, all_dirs: list[tuple[str, Path]]) -> list[tuple[str, str, Path, Path]]:
    """检查单个新目录是否与已有目录近名。"""
    pairs = []
    for name_exist, path_exist in all_dirs:
        if is_similar(new_dir_name, name_exist):
            # 找到路径
            new_path = SPEC_ROOT / new_dir_name.replace("/", "\\").replace("/", "\\")
            # 用相对路径表示
            pairs.append((new_dir_name, name_exist, SPEC_ROOT / new_dir_name, path_exist))
    return pairs


def main():
    parser = argparse.ArgumentParser(description="Spec 近名目录查重门禁")
    parser.add_argument("--new", metavar="DIR_NAME", help="增量模式：检查指定新目录是否与已有 spec 近名")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args()

    if not SPEC_ROOT.exists():
        print(f"ERROR: 规格目录不存在: {SPEC_ROOT}", file=sys.stderr)
        sys.exit(1)

    all_dirs = collect_spec_dirs(SPEC_ROOT)
    total = len(all_dirs)

    if args.new:
        # 增量检查模式
        new_name = args.new.rstrip("/")
        dupes = check_single(new_name, all_dirs)
        if dupes:
            print(f"CONFLICT: 新目录 '{new_name}' 与以下已有 spec 近名：", file=sys.stderr)
            for name_new, name_exist, _, path_exist in dupes:
                rel = path_exist.relative_to(SPEC_ROOT)
                print(f"  - '{name_exist}' ({rel})", file=sys.stderr)
            if args.json:
                print(json.dumps([{"new": n, "exist": e} for n, e, _, _ in dupes], ensure_ascii=False))
            sys.exit(1)
        else:
            print(f"OK: '{new_name}' 无近名并存（共 {total} 个已有 spec）", file=sys.stderr)
            sys.exit(0)
    else:
        # 全量扫描
        dupes = find_duplicates(all_dirs)
        if args.json:
            import json
            result = []
            for name_a, name_b, path_a, path_b in dupes:
                result.append({
                    "pair": [name_a, name_b],
                    "a_rel": str(path_a.relative_to(SPEC_ROOT)),
                    "b_rel": str(path_b.relative_to(SPEC_ROOT)),
                })
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"Spec 查重报告（共 {total} 个 spec，近名阈值 {SIMILARITY_THRESHOLD}）")
            print(f"{'=' * 60}")
            if not dupes:
                print("✓ 未发现近名并存对")
                sys.exit(0)
            print(f"发现 {len(dupes)} 组近名并存：\n")
            for name_a, name_b, path_a, path_b in dupes:
                rel_a = path_a.relative_to(SPEC_ROOT)
                rel_b = path_b.relative_to(SPEC_ROOT)
                print(f"  [{name_a}]  ↔  [{name_b}]")
                print(f"    → {rel_a}")
                print(f"    → {rel_b}")
                print()
            print(f"提示：以上为历史存量并存，C-5 门禁仅防增量新增")
            # 存量并存不阻断 CI（仅 warn）
            sys.exit(0)


if __name__ == "__main__":
    main()
