#!/usr/bin/env python3
"""检查 Windows PowerShell 文本管道写中文文档的高风险模式。

目标：
  - 扫描 .agents/scripts/ 下的 .py / .ps1 / .sh
  - 识别类似 `python ... | Set-Content ...README.md` 的高风险写法
  - 输出 WARN，但默认不阻断 CI（退出码始终为 0，除非参数错误）
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from lib.project import resolve_project_root, resolve_scripts_dir
from lib.cli import add_common_args, print_header, print_summary, print_warn, print_pass, setup_safe_output

TARGET_EXTENSIONS = {".py", ".ps1", ".sh"}

COMMAND_START_RE = re.compile(r"^(?:python(?:\d+(?:\.\d+)?)?|py)\b", re.IGNORECASE)
PYTHON_CMD_RE = re.compile(r"\bpython(?:\d+(?:\.\d+)?)?\b", re.IGNORECASE)
SET_CONTENT_RE = re.compile(r"\|\s*Set-Content\b", re.IGNORECASE)
RISKY_TARGET_RE = re.compile(
    r"(README\.md|[A-Za-z0-9_.-]+\.md\b|generate_api_docs|docgen|report)",
    re.IGNORECASE,
)


@dataclass
class Finding:
    file_path: Path
    line_number: int
    line_text: str
    reason: str


def is_risky_powershell_pipe(line: str) -> bool:
    """判断单行是否命中高风险 PowerShell 文本管道写文档模式。"""
    stripped = line.strip()
    return bool(
        COMMAND_START_RE.search(stripped)
        and PYTHON_CMD_RE.search(stripped)
        and SET_CONTENT_RE.search(stripped)
        and RISKY_TARGET_RE.search(stripped)
    )


def scan_file(file_path: Path, root_dir: Path) -> list[Finding]:
    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = file_path.read_text(encoding="utf-8", errors="replace")

    findings: list[Finding] = []
    for idx, line in enumerate(content.splitlines(), start=1):
        if not is_risky_powershell_pipe(line):
            continue
        findings.append(
            Finding(
                file_path=file_path.relative_to(root_dir),
                line_number=idx,
                line_text=line.strip(),
                reason="检测到 `python ... | Set-Content ...` 且疑似直接写 Markdown/README，Windows 下可能污染中文内容",
            )
        )
    return findings


def collect_targets(scripts_dir: Path) -> list[Path]:
    result: list[Path] = []
    for path in sorted(scripts_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TARGET_EXTENSIONS:
            continue
        result.append(path)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="检查 PowerShell 文本管道写文档的高风险模式",
    )
    add_common_args(parser)
    return parser


def main() -> int:
    setup_safe_output()
    parser = build_parser()
    args = parser.parse_args()

    project_root = Path(args.path).resolve() if args.path else resolve_project_root(__file__)
    scripts_dir = resolve_scripts_dir(__file__)
    if args.path:
        scripts_dir = project_root / ".agents" / "scripts"

    targets = collect_targets(scripts_dir)
    findings: list[Finding] = []
    for file_path in targets:
        findings.extend(scan_file(file_path, project_root))

    if args.json:
        print(
            json.dumps(
                {
                    "ok": True,
                    "warning_count": len(findings),
                    "findings": [
                        {
                            "file": str(f.file_path).replace("\\", "/"),
                            "line": f.line_number,
                            "reason": f.reason,
                            "text": f.line_text,
                        }
                        for f in findings
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    print_header("PowerShell Pipe Safety Check")
    print(f"扫描目录: {scripts_dir}")
    print(f"扫描文件数: {len(targets)}")
    print()

    if findings:
        for finding in findings:
            print_warn(
                f"{finding.file_path}:{finding.line_number} - {finding.reason}\n"
                f"       命中内容: {finding.line_text}\n"
                f"       建议: 使用 Python 直接 write_text(..., encoding='utf-8')，避免通过 Set-Content 承接文档生成 stdout"
            )
    else:
        print_pass("未发现 PowerShell 文本管道写 Markdown/README 的高风险模式")

    print()
    print_summary(pass_count=1 if not findings else 0, warn_count=len(findings), error_count=0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
