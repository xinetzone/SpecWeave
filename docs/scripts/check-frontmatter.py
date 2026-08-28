#!/usr/bin/env python3
"""CI gate：检查 docs/ 下 Markdown 文件的 frontmatter 合规性。

检查项：
  1) 所有非保留文件（非 index.md/log.md）必须包含可解析的 YAML frontmatter，
     且含非空 type 字段；
  2) 仅文档根 index.md 可携带 okf_version 字段；子目录 index.md 不得有 frontmatter；
  3) frontmatter 必须是合法 YAML（可解析）。

用法:
    python scripts/check-frontmatter.py            # 扫描 docs/（默认）
    python scripts/check-frontmatter.py [PATH...]  # 扫描指定目录/文件
    python scripts/check-frontmatter.py --self-test  # 自检

退出码:
    0  全部合规（CI 通过）；或自检通过
    1  存在违规（CI gate 拦截）；或自检发现 gate 失效
"""
import re
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    print("错误: 需要 PyYAML（pip install pyyaml）", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCAN = (ROOT,)
EXCLUDE_DIRS = {"_build", "_static", "_templates", ".git", "__pycache__"}

_FM_DELIM = re.compile(r"^---\s*$", re.MULTILINE)


def _display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_frontmatter(text: str) -> tuple[dict | None, str | None]:
    """解析 YAML frontmatter。返回 (data, error)。"""
    if not text.startswith("---"):
        return None, "无 frontmatter"
    delims = list(_FM_DELIM.finditer(text))
    if len(delims) < 2:
        return None, "frontmatter 未闭合"
    fm_text = text[delims[0].end(): delims[1].start()]
    try:
        data = yaml.safe_load(fm_text)
        if data is None:
            return {}, None
        if not isinstance(data, dict):
            return None, "frontmatter 不是 YAML 映射"
        return data, None
    except yaml.YAMLError as exc:
        return None, f"YAML 解析失败: {exc}"


def iter_md_files(paths) -> list[Path]:
    files: list[Path] = []
    for base in paths:
        p = Path(base)
        if not p.exists():
            print(f"错误: 路径不存在: {p}", file=sys.stderr)
            continue
        if p.is_file() and p.suffix == ".md":
            files.append(p)
        elif p.is_dir():
            for f in p.rglob("*.md"):
                if f.is_file() and not any(part in EXCLUDE_DIRS for part in f.parts):
                    files.append(f)
    return sorted(set(files))


def check_file(path: Path) -> list[str]:
    """检查单个文件，返回错误列表。"""
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"读取失败: {_display(path)}: {exc}"]

    is_root_index = path.resolve() == (ROOT / "index.md").resolve()
    name = path.name

    data, err = parse_frontmatter(text)

    if name == "log.md":
        return errors

    if name == "index.md":
        if is_root_index:
            if data is None:
                errors.append(f"根 index.md 应有 frontmatter: {_display(path)}: {err}")
            elif "okf_version" not in data:
                errors.append(f"根 index.md 缺少 okf_version 字段: {_display(path)}")
        else:
            if data is not None:
                errors.append(f"子目录 index.md 不应有 frontmatter: {_display(path)}")
        return errors

    if data is None:
        errors.append(f"缺少或无效 frontmatter: {_display(path)}: {err}")
        return errors

    if not data.get("type"):
        errors.append(f"缺少 type 字段: {_display(path)}")

    return errors


def self_test() -> bool:
    """自检：验证 gate 能拦截坏文件也能放好文件。"""
    ok = True
    tmp = Path(tempfile.mkdtemp("checkfm-docs"))
    try:
        # 好文件：完整 frontmatter
        good = tmp / "good.md"
        good.write_text(
            "---\ntype: Concept\ntitle: Test\n---\n# Test\n",
            encoding="utf-8",
        )
        if check_file(good):
            print("自检失败: 合规文件被误判", file=sys.stderr)
            ok = False
        else:
            print("自检: 合规文件 → 放行正确")

        # 坏文件：无 type
        no_type = tmp / "no-type.md"
        no_type.write_text(
            "---\ntitle: Test\n---\n# Test\n",
            encoding="utf-8",
        )
        if not check_file(no_type):
            print("自检失败: 缺 type 的文件未被拦截", file=sys.stderr)
            ok = False
        else:
            print("自检: 缺 type → 拦截正确")

        # 坏文件：无 frontmatter
        no_fm = tmp / "no-fm.md"
        no_fm.write_text("# Test\n", encoding="utf-8")
        if not check_file(no_fm):
            print("自检失败: 无 frontmatter 的文件未被拦截", file=sys.stderr)
            ok = False
        else:
            print("自检: 无 frontmatter → 拦截正确")

        # 子目录 index 不应有 frontmatter
        sub_idx = tmp / "sub" / "index.md"
        sub_idx.parent.mkdir(parents=True)
        sub_idx.write_text("---\nokf_version: 0.2\n---\n# Sub\n", encoding="utf-8")
        if not check_file(sub_idx):
            print("自检失败: 子目录 index.md 带 frontmatter 未被拦截", file=sys.stderr)
            ok = False
        else:
            print("自检: 子目录 index 带 frontmatter → 拦截正确")

        if ok:
            print("自检通过: check-frontmatter.py 功能正常。")
        return ok
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return 0 if self_test() else 1

    targets = DEFAULT_SCAN if not args else [Path(a) for a in args if not a.startswith("--")]
    files = iter_md_files(targets)
    if not files:
        print("未找到任何 Markdown 文件", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for f in files:
        all_errors.extend(check_file(f))

    if all_errors:
        print(f"\n检测到 {len(all_errors)} 处 frontmatter 违规，CI gate 拦截：")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print(f"frontmatter 检查通过: {len(files)} 个文件均合规。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
