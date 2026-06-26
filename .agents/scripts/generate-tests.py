#!/usr/bin/env python3
"""测试骨架生成器 —— 从 spec.md 的验收标准章节生成 pytest 测试骨架。

读取 .trae/specs/<change-id>/spec.md 中的 Requirement 定义，
为每个 Requirement 生成一个 pytest test_ 函数骨架，
输出到指定目录或标准输出。

Usage:
    python .agents/scripts/generate-tests.py --spec .trae/specs/my-change/spec.md
    python .agents/scripts/generate-tests.py --spec .trae/specs/my-change/spec.md --output tests/test_my_change.py
    python .agents/scripts/generate-tests.py --all  # 扫描所有 spec 目录

规范要求（来自 check-spec-consistency.py）：
    - Requirement 格式: ### Requirement: XXX
    - Scenario 格式: #### Scenario: XXX (含 WHEN/THEN 结构)
"""

import argparse
import re
import sys
from pathlib import Path

from lib.project import resolve_project_root
from lib.spec import discover_spec_dirs
from lib.cli import print_header, print_pass, print_warn, print_summary

# ── 解析器 ──────────────────────────────────────────────────

def parse_requirements(spec_text: str) -> list[dict]:
    """解析 spec.md 中所有 Requirement 定义。

    Returns:
        [{"name": str, "section": str, "scenarios": [str, ...]}, ...]
    """
    requirements = []
    current_section = "UNKNOWN"
    current_req_name = ""
    current_req_scenarios: list[str] = []

    for line in spec_text.splitlines():
        stripped = line.strip()

        # 章节
        sec_match = re.match(r"^##\s+(ADDED|MODIFIED|REMOVED)\s+Requirements?", stripped, re.IGNORECASE)
        if sec_match:
            # 保存上一个 requirement
            if current_req_name:
                requirements.append({
                    "name": current_req_name,
                    "section": current_section,
                    "scenarios": current_req_scenarios,
                })
            current_section = sec_match.group(1).upper()
            current_req_name = ""
            current_req_scenarios = []
            continue

        # Requirement
        req_match = re.match(r"^###\s+Requirement:\s+(.+)", stripped)
        if req_match:
            if current_req_name:
                requirements.append({
                    "name": current_req_name,
                    "section": current_section,
                    "scenarios": current_req_scenarios,
                })
            current_req_name = req_match.group(1).strip()
            current_req_scenarios = []
            continue

        # Scenario
        scn_match = re.match(r"^####\s+Scenario:\s+(.+)", stripped)
        if scn_match:
            current_req_scenarios.append(scn_match.group(1).strip())

    # 最后一个 requirement
    if current_req_name:
        requirements.append({
            "name": current_req_name,
            "section": current_section,
            "scenarios": current_req_scenarios,
        })

    return requirements


# ── 测试名生成 ──────────────────────────────────────────────

def _to_test_name(req_name: str) -> str:
    """将中文 Requirement 名称转换为合法的 pytest 函数名。

    规则：
      - 提取前 3-5 个关键词（中文 2+ 字 + 英文单词）
      - 蛇形命名，长度 ≤ 60 字符
      - 前缀 "test_"
    """
    keywords = re.findall(r"[\u4e00-\u9fa5]{2,}|[a-zA-Z]{2,}", req_name)
    if not keywords:
        sanitized = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fa5_]", "_", req_name)
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        return f"test_{sanitized}"

    # 取前 4 个关键词
    short = "_".join(keywords[:4])
    if len(short) > 50:
        short = short[:50]
    return f"test_{short}"


def _sanitize_class_name(name: str) -> str:
    """生成合法的 Python 类名。"""
    cleaned = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fa5]", "", name)
    if len(cleaned) > 30:
        cleaned = cleaned[:30]
    return cleaned if cleaned else "TestRequirement"


def _format_docstring(req: dict, indent: str = "    ") -> str:
    """格式化 Requirement 的 docstring。"""
    lines = [
        f'{indent}"""{req["name"]}',
        f'{indent}',
    ]
    if req["scenarios"]:
        lines.append(f'{indent}验收场景：')
        for s in req["scenarios"]:
            lines.append(f'{indent}  - {s}')
    lines.append(f'{indent}"""')
    return "\n".join(lines)


# ── 生成器 ──────────────────────────────────────────────────

def generate_test_file(
    requirements: list[dict],
    spec_id: str,
    indent: str = "    ",
) -> str:
    """生成完整的 pytest 测试文件内容。

    Args:
        requirements: parse_requirements() 的返回值。
        spec_id: spec 目录名，用于生成文件名和类名。
        indent: 缩进字符串。

    Returns:
        完整的 .py 文件源代码。
    """
    lines = [
        f'"""自动生成的测试骨架',
        f'',
        f'来源：.trae/specs/{spec_id}/spec.md',
        f'生成工具：.agents/scripts/generate-tests.py',
        f'',
        f'注意：本文件为骨架代码，每个测试函数内部的断言需根据',
        f'实际业务逻辑手动填写。Scenario 注释提供了验收场景指引。',
        f'"""',
        f'',
        f'import pytest',
        f'',
        f'',
    ]

    if not requirements:
        lines.append("# 无 Requirement 定义，跳过测试类生成")
        lines.append("")
        return "\n".join(lines)

    class_name = f"Test{_sanitize_class_name(spec_id.replace('-', '_'))}"
    lines.append(f"class {class_name}:")
    lines.append(f'{indent}"""对应 spec: {spec_id}"""')
    lines.append("")

    for req in requirements:
        test_name = _to_test_name(req["name"])
        lines.append(f"{indent}def {test_name}(self):")
        lines.append(_format_docstring(req, indent * 2))
        lines.append(f"{indent}{indent}# TODO: 根据验收场景编写具体测试逻辑")
        lines.append(f"{indent}{indent}# Requirement 来自 {req['section']} 章节")
        lines.append(f"{indent}{indent}pass")
        lines.append("")

    return "\n".join(lines)


# ── 主流程 ──────────────────────────────────────────────────

def generate_for_spec(spec_dir: Path, output_path: Path | None = None) -> str | None:
    """为单个 spec 目录生成测试骨架。

    Args:
        spec_dir: spec 目录路径。
        output_path: 输出路径，为 None 时打印到 stdout。

    Returns:
        生成的文件路径，如果 spec 不含 requirement 则返回 None。
    """
    spec_file = spec_dir / "spec.md"
    if not spec_file.exists():
        print_warn(f"跳过 {spec_dir.name}: 缺少 spec.md")
        return None

    spec_text = spec_file.read_text(encoding="utf-8")
    requirements = parse_requirements(spec_text)

    if not requirements:
        print_warn(f"跳过 {spec_dir.name}: 无 Requirement 定义")
        return None

    spec_id = spec_dir.name
    code = generate_test_file(requirements, spec_id)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(code, encoding="utf-8")
        print_pass(f"{spec_dir.name} → {output_path} ({len(requirements)} 个 Requirement)")
        return str(output_path)
    else:
        print(code)
        return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="从 spec.md 生成 pytest 测试骨架",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--spec", type=str, help="单个 spec 目录路径")
    group.add_argument("--all", action="store_true", help="扫描所有 spec 目录")
    parser.add_argument("--output", type=str, default=None, help="输出文件路径（单文件模式）")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="输出目录（--all 模式，每个 spec 生成独立文件）",
    )
    parser.add_argument("--dry-run", action="store_true", help="仅打印生成内容，不写入文件")

    args = parser.parse_args()
    project_root = resolve_project_root(__file__)

    if args.spec:
        spec_dir = Path(args.spec)
        if not spec_dir.is_absolute():
            spec_dir = project_root / args.spec

        output_path = None
        if args.output:
            output_path = Path(args.output)
        elif not args.dry_run:
            # 默认输出到 spec 目录下的 tests/ 子目录
            output_path = spec_dir / "tests" / f"test_{spec_dir.name}.py"

        generate_for_spec(spec_dir, output_path)
        return 0

    # --all 模式
    spec_dirs = discover_spec_dirs(project_root)
    if not spec_dirs:
        print_warn("未找到任何 spec 目录")
        return 0

    output_dir = Path(args.output_dir) if args.output_dir else (project_root / "tests" / "generated")
    total_reqs = 0

    print_header("测试骨架生成")
    print(f"输出目录: {output_dir}")
    print()

    for spec_dir in spec_dirs:
        spec_id = spec_dir.name
        out_path = output_dir / f"test_{spec_id}.py"
        result = generate_for_spec(spec_dir, out_path)
        if result:
            # 统计 requirement 数量
            spec_text = (spec_dir / "spec.md").read_text(encoding="utf-8")
            reqs = parse_requirements(spec_text)
            total_reqs += len(reqs)

    print()
    print_summary(total_reqs, 0, 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
