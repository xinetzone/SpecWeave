"""AC-16 覆盖率门禁校验：总覆盖率 ≥80%，关键模块 per-module ≥90%。

关键模块定义（spec.md AC-16）：render / server（同步、分享、市场、上传、爱发电）
/ uploaders / mcp。入口 shim（``__init__.py`` / ``__main__.py``）不计入关键模块。

overall 门槛已由 pyproject 的 ``[tool.coverage.report] fail_under`` 在 pytest 内
快速拦截；本脚本消费 ``--cov-report=json`` 产物做 per-module 逐文件判定，是
「关键模块 ≥90%」的唯一机械门禁。

用法：
    pytest --cov --cov-report=json:coverage.json
    python scripts/check_coverage.py                      # 默认读 coverage.json
    python scripts/check_coverage.py --json path/to.json
"""

import argparse
import json
import sys
from pathlib import Path

DEFAULT_JSON = "coverage.json"
OVERALL_MIN_PERCENT = 80.0
MODULE_MIN_PERCENT = 90.0

# 关键模块前缀（相对仓库根的覆盖路径段；比对前统一归一化到 doocs_md_py/ 起点）
_PACKAGE_MARKER = "doocs_md_py/"
CRITICAL_PREFIXES = (
    "doocs_md_py/render/",
    "doocs_md_py/server/",
    "doocs_md_py/uploaders/",
    "doocs_md_py/mcp_server/",
)
# 入口 shim 不承担逻辑，不纳入关键模块判定
CRITICAL_EXCLUDED_SUFFIXES = ("/__init__.py", "/__main__.py")


def _normalize(path: str) -> str:
    """把 coverage.json 中的任意路径归一化为 ``doocs_md_py/...`` 形式。"""
    posix = path.replace("\\", "/")
    index = posix.find(_PACKAGE_MARKER)
    return posix[index:] if index >= 0 else posix


def _is_critical(module_key: str) -> bool:
    if module_key.endswith(CRITICAL_EXCLUDED_SUFFIXES):
        return False
    return any(module_key.startswith(prefix) for prefix in CRITICAL_PREFIXES)


def _load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(
            f"未找到覆盖率报告 {path}；请先运行 "
            "pytest --cov --cov-report=json:coverage.json"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AC-16 覆盖率门禁校验")
    parser.add_argument("--json", default=DEFAULT_JSON, help="coverage.json 路径")
    parser.add_argument(
        "--overall-min", type=float, default=OVERALL_MIN_PERCENT, help="总覆盖率门槛"
    )
    parser.add_argument(
        "--module-min", type=float, default=MODULE_MIN_PERCENT, help="关键模块门槛"
    )
    args = parser.parse_args(argv)

    report = _load(Path(args.json))
    totals = report.get("totals", {})
    overall = float(totals.get("percent_covered", 0.0))
    files = report.get("files", {})

    critical_total = 0
    breaches: list[tuple[str, float]] = []
    for raw_path, entry in sorted(files.items()):
        key = _normalize(raw_path)
        if not _is_critical(key):
            continue
        critical_total += 1
        percent = float(entry.get("summary", {}).get("percent_covered", 0.0))
        if percent < args.module_min:
            breaches.append((key, percent))

    print(f"总覆盖率 {overall:.2f}%（门槛 {args.overall_min:.0f}%）")
    print(f"关键模块 {critical_total - len(breaches)}/{critical_total} 达标（门槛 {args.module_min:.0f}%）")

    failed = False
    if overall < args.overall_min:
        print(f"  [不达标] 总覆盖率 {overall:.2f}% < {args.overall_min:.0f}%")
        failed = True
    if breaches:
        print("  关键模块低于门槛：")
        for key, percent in breaches:
            print(f"    {key} {percent:.2f}%")
        failed = True
    if failed:
        return 1
    print("AC-16 覆盖率门禁通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
