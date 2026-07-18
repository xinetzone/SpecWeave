#!/usr/bin/env python3
"""关键配置文件放置校验工具。

检测受管的关键配置文件是否被错误放置到项目根目录。
所有受管文件的标准位置为 .agents/scripts/，若出现在项目根目录则判定为错误放置。

受管关键文件清单（7 项）：
    - sitecustomize.py     Python 启动自动加载 UTF-8 配置
    - setup-utf8-env.ps1   UTF-8 环境一键配置
    - profile.ps1          PowerShell Profile 持久化配置
    - Install-Profile.ps1  Profile 安装脚本
    - check-encoding.ps1   编码诊断
    - verify-encoding.ps1  编码验证
    - setup-cmd-utf8.ps1   CMD AutoRun UTF-8 配置

用法：
    python check-file-placement.py             # 人类可读报告
    python check-file-placement.py --json      # JSON 格式输出（CI 集成）
    python check-file-placement.py --fix-hint  # 显示详细修复指令

退出码：
    0 = 全部正确（所有受管文件均在正确位置）
    1 = 存在错误放置
"""

import argparse
import json
import sys
from pathlib import Path

# 将 .agents/scripts/ 加入 sys.path 以便复用 lib/
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import (
    print_pass,
    print_warn,
    print_error,
    print_header,
    print_summary,
    setup_safe_output,
    add_common_args,
)
from lib.project import resolve_project_root

# 标准位置子目录（相对于项目根）
STANDARD_SUBDIR = Path(".agents") / "scripts"

# 受管关键文件清单：文件名 → 用途说明
MANAGED_FILES: dict[str, str] = {
    "sitecustomize.py": "Python 启动自动加载 UTF-8 配置",
    "setup-utf8-env.ps1": "UTF-8 环境一键配置",
    "profile.ps1": "PowerShell Profile 持久化配置",
    "Install-Profile.ps1": "Profile 安装脚本",
    "check-encoding.ps1": "编码诊断",
    "verify-encoding.ps1": "编码验证",
    "setup-cmd-utf8.ps1": "CMD AutoRun UTF-8 配置",
}


def check_placement(project_root: Path) -> list[dict]:
    """逐个检查受管文件放置位置，返回详细信息列表。

    判定规则：
        - 受管文件出现在项目根目录 → status="misplaced"
        - 否则 → status="ok"

    每项包含字段：
        - filename:          受管文件名
        - status:            "ok" | "misplaced"
        - current_path:      当前错误位置（仅 misplaced 时为字符串，否则 None）
        - standard_path:     正确位置（绝对路径字符串）
        - purpose:           用途说明
        - fix_command:       修复指令（仅 misplaced 时为字符串，否则 None）
        - standard_exists:   标准位置是否已存在该文件（辅助诊断缺失情况）
    """
    standard_dir = project_root / STANDARD_SUBDIR
    standard_dir_posix = STANDARD_SUBDIR.as_posix()
    details: list[dict] = []

    for filename, purpose in MANAGED_FILES.items():
        root_candidate = project_root / filename
        standard_candidate = standard_dir / filename
        standard_exists = standard_candidate.exists()

        if root_candidate.exists():
            # 错误放置：受管文件出现在项目根目录
            fix_cmd = f"git mv {filename} {standard_dir_posix}/{filename}"
            details.append({
                "filename": filename,
                "status": "misplaced",
                "current_path": str(root_candidate),
                "standard_path": str(standard_candidate),
                "purpose": purpose,
                "fix_command": fix_cmd,
                "standard_exists": standard_exists,
            })
        else:
            details.append({
                "filename": filename,
                "status": "ok",
                "current_path": None,
                "standard_path": str(standard_candidate),
                "purpose": purpose,
                "fix_command": None,
                "standard_exists": standard_exists,
            })

    return details


def render_human_report(
    details: list[dict], project_root: Path, show_fix_hint: bool
) -> int:
    """人类可读报告输出，返回退出码（0=通过，1=存在错误放置）。"""
    standard_dir = project_root / STANDARD_SUBDIR
    print_header("关键配置文件放置校验")
    print(f"  项目根目录: {project_root}")
    print(f"  标准位置:   {standard_dir}")
    print(f"  受管文件数: {len(MANAGED_FILES)}")
    print()

    misplaced = [d for d in details if d["status"] == "misplaced"]
    missing_in_standard = [
        d for d in details
        if d["status"] == "ok" and not d["standard_exists"]
    ]

    for d in details:
        if d["status"] == "misplaced":
            print_error(f"[MISPLACED] {d['filename']}  ({d['purpose']})")
            print(f"      当前错误位置: {d['current_path']}")
            print(f"      正确位置:     {d['standard_path']}")
            if show_fix_hint:
                print_warn(f"      修复指令: {d['fix_command']}")
        else:
            print_pass(f"[OK] {d['filename']}  ({d['purpose']})")

    # 辅助提示：受管文件既不在根目录也不在标准位置（可能丢失）
    if missing_in_standard:
        print()
        print_warn("以下受管文件在根目录与标准位置均不存在（可能缺失，不影响退出码）:")
        for d in missing_in_standard:
            print_warn(f"  - {d['filename']}  ({d['purpose']})")

    print()
    print_summary(
        pass_count=len(details) - len(misplaced),
        warn_count=len(missing_in_standard),
        error_count=len(misplaced),
    )

    if misplaced:
        print()
        print_error("  发现错误放置的关键配置文件！")
        print_warn("  修复指令（在项目根目录执行）:")
        for d in misplaced:
            print(f"    {d['fix_command']}")
        return 1

    return 0


def render_json_report(details: list[dict], project_root: Path) -> int:
    """JSON 格式输出供 CI 集成，返回退出码（0=通过，1=存在错误放置）。

    JSON 结构：
        {
          "summary": {
            "project_root":      "...",
            "standard_dir":      "...",
            "managed_count":     7,
            "ok_count":          7,
            "misplaced_count":   0,
            "exit_code":         0
          },
          "details": [ { ...每个受管文件的状态... } ]
        }
    """
    misplaced = [d for d in details if d["status"] == "misplaced"]
    output = {
        "summary": {
            "project_root": str(project_root),
            "standard_dir": str(project_root / STANDARD_SUBDIR),
            "managed_count": len(MANAGED_FILES),
            "ok_count": len(details) - len(misplaced),
            "misplaced_count": len(misplaced),
            "exit_code": 1 if misplaced else 0,
        },
        "details": details,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 1 if misplaced else 0


def main() -> int:
    setup_safe_output()
    parser = argparse.ArgumentParser(
        description="关键配置文件放置校验：检测受管文件是否被错误放置到项目根目录"
    )
    parser.add_argument(
        "--fix-hint",
        action="store_true",
        help="在人类可读报告中显示详细修复指令",
    )
    add_common_args(parser)
    args = parser.parse_args()

    # 项目根目录定位：
    # 优先使用 lib.project.resolve_project_root（基于 AGENTS.md 标记向上查找，
    # 等价于 Path(__file__).resolve().parent.parent.parent 推算但更稳健）。
    project_root = resolve_project_root(__file__)

    details = check_placement(project_root)

    if args.json:
        return render_json_report(details, project_root)

    return render_human_report(details, project_root, show_fix_hint=args.fix_hint)


if __name__ == "__main__":
    sys.exit(main())
