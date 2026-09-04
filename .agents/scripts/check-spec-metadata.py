"""Spec 元数据扫描 — 薄包装脚本（向后兼容）

已整合进 spec_tool 工具链，本脚本仅作为兼容入口保留。
推荐用法：
  python -m lib.spec_tool check --meta-only
  python -m lib.spec_tool check --meta-only --json

新增非法 status 的归一化映射请到 lib/spec_tool/constants.py 的
STATUS_NORMALIZATION_MAP 中添加。
"""

# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310
enforce_python310()

import argparse
import json
from pathlib import Path

from lib.spec_tool.metadata_checker import scan_spec_metadata, format_terminal_report
from lib.spec_tool.constants import VALID_STATUSES

PROJ_ROOT = Path(__file__).resolve().parent.parent.parent
SPEC_ROOT = PROJ_ROOT / ".trae" / "specs"


def main():
    parser = argparse.ArgumentParser(description="Spec 元数据扫描（兼容入口，推荐使用 spec_tool check --meta-only）")
    parser.add_argument("--path", type=Path, default=None, help="spec 根目录（默认: .trae/specs）")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出到终端")
    parser.add_argument("--output", type=Path, default=None, help="JSON 报告输出路径（默认: .temp/spec-metadata-violations.json）")
    args = parser.parse_args()

    spec_root = args.path or SPEC_ROOT
    report = scan_spec_metadata(spec_root, PROJ_ROOT)

    # 终端输出
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_terminal_report(report, spec_root))

    # 写入 JSON 文件（CI 集成用）
    out_path = args.output or (PROJ_ROOT / ".temp" / "spec-metadata-violations.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    if not args.json:
        print(f"\nJSON 报告已写入: {out_path}")

    return 1 if report["error_count"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
