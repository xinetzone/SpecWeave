#!/usr/bin/env python3
"""关键配置文件放置校验工具。

检测受管的关键配置文件与临时目录是否被错误放置到项目根目录。
检测分为两类规则：

1. 精确文件名匹配（MANAGED_FILES）：
   受管文件的标准位置为 .agents/scripts/，若出现在项目根目录则判定为错误放置。
   受管关键文件清单（7 项）：
       - sitecustomize.py     Python 启动自动加载 UTF-8 配置
       - setup-utf8-env.ps1   UTF-8 环境一键配置
       - profile.ps1          PowerShell Profile 持久化配置
       - Install-Profile.ps1  Profile 安装脚本
       - check-encoding.ps1   编码诊断
       - verify-encoding.ps1  编码验证
       - setup-cmd-utf8.ps1   CMD AutoRun UTF-8 配置

2. Glob 模式匹配（GLOB_PATTERNS）：
   根目录下不应出现的临时目录/文件模式，标准位置为 .temp/。
   当前规则：
       - .tmp-ci-logs*        CI 日志临时目录（应位于 .temp/ 下）

用法：
    python check-file-placement.py             # 人类可读报告
    python check-file-placement.py --json      # JSON 格式输出（CI 集成）
    python check-file-placement.py --fix-hint  # 显示详细修复指令

退出码：
    0 = 全部正确（所有受管文件与临时目录均在正确位置）
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

# Glob 模式规则：根目录下不应出现的临时目录/文件
# 每条规则包含：
#   pattern:          glob 模式（相对于项目根目录）
#   description:      用途说明（人类可读）
#   standard_location: 正确位置（相对于项目根目录的目录路径）
#   is_directory:     匹配项是否为目录（True=目录，False=文件）
GLOB_PATTERNS: list[dict] = [
    {
        "pattern": ".tmp-ci-logs*",
        "description": "CI 日志临时目录（应位于 .temp/ 下）",
        "standard_location": ".temp/",
        "is_directory": True,
    },
]


def check_managed_files(project_root: Path) -> list[dict]:
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
        - match_type:        "exact"（精确文件名匹配）
    """
    standard_dir = project_root / STANDARD_SUBDIR
    standard_dir_posix = STANDARD_SUBDIR.as_posix()
    details: list[dict] = []

    for filename, purpose in MANAGED_FILES.items():
        root_candidate = project_root / filename
        standard_candidate = standard_dir / filename
        standard_exists = standard_candidate.exists()

        if root_candidate.exists():
            fix_cmd = f"git mv {filename} {standard_dir_posix}/{filename}"
            details.append({
                "filename": filename,
                "status": "misplaced",
                "current_path": str(root_candidate),
                "standard_path": str(standard_candidate),
                "purpose": purpose,
                "fix_command": fix_cmd,
                "standard_exists": standard_exists,
                "match_type": "exact",
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
                "match_type": "exact",
            })

    return details


def check_glob_patterns(project_root: Path) -> list[dict]:
    """按 glob 模式检测根目录下不应出现的临时目录/文件，返回详细信息列表。

    每条规则使用 project_root.glob(pattern) 查找匹配项，
    匹配到的每个项均判定为 status="misplaced"。

    每项包含字段：
        - filename:          匹配到的目录/文件名
        - status:            "misplaced"
        - current_path:      当前错误位置（绝对路径）
        - standard_path:     建议的正确位置（绝对路径）
        - purpose:           用途说明（来自规则 description）
        - fix_command:       修复指令（Move-Item 命令）
        - standard_exists:   标准位置是否已存在同名项
        - match_type:        "glob"
        - pattern:           匹配的 glob 模式
    """
    details: list[dict] = []
    temp_dir = project_root / ".temp"

    for rule in GLOB_PATTERNS:
        pattern = rule["pattern"]
        description = rule["description"]
        standard_loc = rule["standard_location"]
        is_directory = rule["is_directory"]

        for match in sorted(project_root.glob(pattern)):
            # 跳过 .temp/ 目录自身
            if match.name == ".temp":
                continue

            name = match.name
            current_path = str(match)
            standard_path = str(project_root / standard_loc / name)
            standard_exists = (project_root / standard_loc / name).exists()

            if is_directory and not match.is_dir():
                continue  # 期望目录但匹配到文件，跳过
            if not is_directory and match.is_dir():
                continue  # 期望文件但匹配到目录，跳过

            fix_cmd = f'Move-Item "{name}" "{standard_loc}{name}"'

            details.append({
                "filename": name,
                "status": "misplaced",
                "current_path": current_path,
                "standard_path": standard_path,
                "purpose": description,
                "fix_command": fix_cmd,
                "standard_exists": standard_exists,
                "match_type": "glob",
                "pattern": pattern,
            })

    return details


def check_placement(project_root: Path) -> list[dict]:
    """综合检测所有受管文件与 glob 模式的放置位置，返回详细信息列表。

    合并 check_managed_files() 与 check_glob_patterns() 的结果，
    managed files 在前，glob 匹配项在后。
    """
    details = check_managed_files(project_root)
    details.extend(check_glob_patterns(project_root))
    return details


def render_human_report(
    details: list[dict], project_root: Path, show_fix_hint: bool
) -> int:
    """人类可读报告输出，返回退出码（0=通过，1=存在错误放置）。"""
    standard_dir = project_root / STANDARD_SUBDIR
    print_header("关键配置文件放置校验")
    print(f"  项目根目录: {project_root}")
    print(f"  受管文件标准位置: {standard_dir}")
    print(f"  受管文件数: {len(MANAGED_FILES)}")
    print(f"  Glob 规则数: {len(GLOB_PATTERNS)}")
    print()

    misplaced = [d for d in details if d["status"] == "misplaced"]
    misplaced_exact = [d for d in misplaced if d.get("match_type") == "exact"]
    misplaced_glob = [d for d in misplaced if d.get("match_type") == "glob"]

    missing_in_standard = [
        d for d in details
        if d["status"] == "ok" and not d["standard_exists"]
    ]

    # 精确文件名匹配结果
    for d in details:
        if d.get("match_type") == "glob":
            continue  # glob 匹配项单独输出
        if d["status"] == "misplaced":
            print_error(f"[MISPLACED] {d['filename']}  ({d['purpose']})")
            print(f"      当前错误位置: {d['current_path']}")
            print(f"      正确位置:     {d['standard_path']}")
            if show_fix_hint:
                print_warn(f"      修复指令: {d['fix_command']}")
        else:
            print_pass(f"[OK] {d['filename']}  ({d['purpose']})")

    # Glob 模式匹配结果
    if misplaced_glob:
        print()
        print_warn("--- Glob 模式检测：根目录下不应出现的临时目录/文件 ---")
        for d in misplaced_glob:
            print_error(f"[MISPLACED] {d['filename']}  ({d['purpose']})")
            print(f"      匹配规则: {d.get('pattern', '?')}")
            print(f"      当前错误位置: {d['current_path']}")
            print(f"      建议位置:     {d['standard_path']}")
            if show_fix_hint:
                print_warn(f"      修复指令: {d['fix_command']}")

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
        print_error("  发现错误放置的文件或目录！")
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
            "glob_rules_count":  1,
            "ok_count":          7,
            "misplaced_count":   0,
            "exit_code":         0
          },
          "details": [ { ...每个受管文件与 glob 匹配项的状态... } ]
        }
    """
    misplaced = [d for d in details if d["status"] == "misplaced"]
    output = {
        "summary": {
            "project_root": str(project_root),
            "standard_dir": str(project_root / STANDARD_SUBDIR),
            "managed_count": len(MANAGED_FILES),
            "glob_rules_count": len(GLOB_PATTERNS),
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
        description="关键配置文件放置校验：检测受管文件与临时目录是否被错误放置到项目根目录"
    )
    parser.add_argument(
        "--fix-hint",
        action="store_true",
        help="在人类可读报告中显示详细修复指令",
    )
    add_common_args(parser)
    args = parser.parse_args()

    project_root = resolve_project_root(__file__)

    details = check_placement(project_root)

    if args.json:
        return render_json_report(details, project_root)

    return render_human_report(details, project_root, show_fix_hint=args.fix_hint)


if __name__ == "__main__":
    sys.exit(main())