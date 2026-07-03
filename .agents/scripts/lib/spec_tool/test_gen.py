import re
from pathlib import Path

from lib.cli import print_header, print_pass, print_warn, print_summary
from lib.project import resolve_project_root
from lib.spec import discover_spec_dirs

from .constants import _REQ_SEC_RE, _REQ_HDR_RE, _SCN_HDR_RE


def _parse_requirements(spec_text: str) -> list[dict]:
    requirements = []
    cur_section = "UNKNOWN"
    cur_name = ""
    cur_scenarios: list[str] = []

    def flush():
        nonlocal cur_name
        if cur_name:
            requirements.append({"name": cur_name, "section": cur_section, "scenarios": list(cur_scenarios)})
            cur_name = ""
            cur_scenarios.clear()

    for line in spec_text.splitlines():
        s = line.strip()
        m = _REQ_SEC_RE.match(s)
        if m:
            flush()
            cur_section = m.group(1).upper()
            continue
        m = _REQ_HDR_RE.match(s)
        if m:
            flush()
            cur_name = m.group(1).strip()
            continue
        m = _SCN_HDR_RE.match(s)
        if m:
            cur_scenarios.append(m.group(1).strip())

    flush()
    return requirements


def _to_test_name(req_name: str) -> str:
    keywords = re.findall(r"[\u4e00-\u9fa5]{2,}|[a-zA-Z]{2,}", req_name)
    if not keywords:
        san = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fa5_]", "_", req_name)
        return f"test_{san[:50]}"
    short = "_".join(keywords[:4])
    return f"test_{short[:50]}"


def _sanitize_class_name(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fa5]", "", name)
    return (cleaned[:30] if cleaned else "TestRequirement")


def _format_docstring(req: dict, indent: str = "    ") -> str:
    lines = [f'{indent}"""{req["name"]}', f"{indent}"]
    if req["scenarios"]:
        lines.append(f"{indent}验收场景：")
        for s in req["scenarios"]:
            lines.append(f"{indent}  - {s}")
    lines.append(f'{indent}"""')
    return "\n".join(lines)


def _generate_test_file(requirements: list[dict], spec_id: str, indent: str = "    ") -> str:
    lines = [
        f'"""自动生成的测试骨架',
        f"",
        f"来源：.trae/specs/{spec_id}/spec.md",
        f"生成工具：.agents/scripts/spec-tool.py gen-tests",
        f"",
        f"注意：本文件为骨架代码，每个测试函数内部的断言需根据",
        f"实际业务逻辑手动填写。Scenario 注释提供了验收场景指引。",
        f'"""',
        f"",
        f"import pytest",
        f"",
        f"",
    ]
    if not requirements:
        lines.append("# 无 Requirement 定义，跳过测试类生成")
        lines.append("")
        return "\n".join(lines)

    cls = f"Test{_sanitize_class_name(spec_id.replace('-', '_'))}"
    lines.append(f"class {cls}:")
    lines.append(f'{indent}"""对应 spec: {spec_id}"""')
    lines.append("")
    for req in requirements:
        tn = _to_test_name(req["name"])
        lines.append(f"{indent}def {tn}(self):")
        lines.append(_format_docstring(req, indent * 2))
        lines.append(f"{indent}{indent}# TODO: 根据验收场景编写具体测试逻辑")
        lines.append(f"{indent}{indent}# Requirement 来自 {req['section']} 章节")
        lines.append(f"{indent}{indent}pass")
        lines.append("")
    return "\n".join(lines)


def _gen_for_spec(spec_dir: Path, output_path: Path | None, dry_run: bool) -> int:
    spec_file = spec_dir / "spec.md"
    if not spec_file.exists():
        print_warn(f"跳过 {spec_dir.name}: 缺少 spec.md")
        return 0
    text = spec_file.read_text(encoding="utf-8")
    reqs = _parse_requirements(text)
    if not reqs:
        print_warn(f"跳过 {spec_dir.name}: 无 Requirement 定义")
        return 0

    code = _generate_test_file(reqs, spec_dir.name)
    if dry_run or output_path is None:
        print(code)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(code, encoding="utf-8")
        print_pass(f"{spec_dir.name} → {output_path} ({len(reqs)} 个 Requirement)")
    return len(reqs)


def cmd_gen_tests(args) -> int:
    root = args.path or resolve_project_root(__file__)

    if args.spec:
        spec_dir = Path(args.spec)
        if not spec_dir.is_absolute():
            spec_dir = root / args.spec
        out = None
        if args.output:
            out = Path(args.output)
        elif not args.dry_run:
            out = spec_dir / "tests" / f"test_{spec_dir.name}.py"
        _gen_for_spec(spec_dir, out, args.dry_run)
        return 0

    spec_dirs = discover_spec_dirs(root)
    if not spec_dirs:
        print_warn("未找到任何 spec 目录")
        return 0

    out_dir = Path(args.output_dir) if args.output_dir else (root / "tests" / "generated")
    total = 0

    print_header("测试骨架生成")
    print(f"输出目录: {out_dir}")
    print()

    for sd in spec_dirs:
        out_path = out_dir / f"test_{sd.name}.py"
        n = _gen_for_spec(sd, out_path, args.dry_run)
        total += n

    print()
    print_summary(total, 0, 0)
    return 0
