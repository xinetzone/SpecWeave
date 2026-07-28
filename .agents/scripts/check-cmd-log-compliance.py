#!/usr/bin/env python3
"""CMD-LOG v1.3.0 合规性检查器：自动验证命令集执行日志是否符合强制日志纪律。

基于 .agents/rules/cmd-log-specification.md §8 强制日志纪律（不可跳过）：
  铁律一（🔴）：S0 CMD_START 必须是命令集执行后的第一条输出
  铁律二（🔴）：CMD_START 必须包含完整 ctx 字段
  铁律三（🟡）：步骤连续性 STEP_ENTER → STEP_COMPLETE 成对出现
  铁律四（🔴）：CMD_COMPLETE/CMD_ERROR 必须是最后一条输出且session闭环
  铁律五（🟡）：日志断裂时必须事后补全

检查维度：
  1. Skill门面规范检查（--skills）：验证7个CMD-LOG命令集的SKILL.md包含日志规范章节和强制纪律引用
  2. 复盘文档链路检查（--retros）：扫描execution-retrospective.md中的CMD-LOG日志块，验证链路完整性
  3. 全部检查（--all，默认）

用法：
  python check-cmd-log-compliance.py                     # 全部检查
  python check-cmd-log-compliance.py --skills            # 仅检查Skill规范
  python check-cmd-log-compliance.py --retros            # 仅检查复盘文档链路
  python check-cmd-log-compliance.py --json              # JSON格式输出
  python check-cmd-log-compliance.py --verbose           # 显示详情
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from lib.project import resolve_project_root
from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, add_common_args, setup_safe_output

PROJECT_ROOT = resolve_project_root(__file__)
SKILLS_DIR = PROJECT_ROOT / ".agents" / "skills"
RETROS_DIR = PROJECT_ROOT / ".agents" / "docs" / "retrospective" / "reports" / "task-reports"
CMD_LOG_SPEC = PROJECT_ROOT / ".agents" / "rules" / "cmd-log-specification" / "03-events-steps.md"

CMD_LOG_COMMANDS = {
    "retrospective-cmd": {"cmd": "retrospective", "session_prefix": "retr-", "steps": 6, "name": "复盘"},
    "insight-cmd": {"cmd": "insight", "session_prefix": "insgt-", "steps": 7, "name": "洞察"},
    "export-report-cmd": {"cmd": "export-report", "session_prefix": "exprt-", "steps": 7, "name": "导出报告"},
    "atomization-cmd": {"cmd": "atomization", "session_prefix": "atom-", "steps": 7, "name": "原子化"},
    "atomic-commit-cmd": {"cmd": "atomic-commit", "session_prefix": "cmt-", "steps": 7, "name": "原子提交"},
    "mermaid-cmd": {"cmd": "mermaid", "session_prefix": "merm-", "steps": 7, "name": "Mermaid图表"},
    "pattern-extraction-cmd": {"cmd": "pattern-extraction", "session_prefix": "ptrn-", "steps": 6, "name": "模式萃取"},
}

CMD_LOG_LINE_RE = re.compile(
    r"\[CMD-LOG\]\s*\|\s*level=(\w+)\s*\|\s*cmd=([\w-]+)\s*\|\s*step=(\w+)\s*\|\s*event=(\w+)\s*\|\s*session=([\w-]+)\s*\|\s*msg=(.*?)(?:\s*\|\s*ctx=(.*))?$"
)

CMD_LOG_V130_DATE = "2026-07-28"
HISTORICAL_CUTOFF_MSG = "（v1.3.0规范生效日期前的历史债务，非阻塞）"


@dataclass
class CheckResult:
    name: str
    passed: bool
    severity: str
    message: str
    file: str | None = None
    line: int | None = None
    rule_id: str | None = None


@dataclass
class LogEntry:
    level: str
    cmd: str
    step: str
    event: str
    session: str
    msg: str
    ctx: str | None
    line_no: int


@dataclass
class SessionChain:
    session_id: str
    cmd: str
    entries: list[LogEntry] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.entries:
            self.errors.append("空session（无日志条目）")
            return

        first = self.entries[0]
        last = self.entries[-1]

        if first.event != "CMD_START":
            self.errors.append(
                f"违反铁律一：第一条日志是 {first.event} 而非 CMD_START（行{first.line_no}）"
            )
        elif first.step != "S0":
            self.errors.append(
                f"违反铁律一：CMD_START 的 step={first.step} 应为 S0（行{first.line_no}）"
            )

        if first.event == "CMD_START":
            if not first.ctx or first.ctx.strip() in ("", "{}", "null"):
                self.warnings.append(
                    f"违反铁律二：CMD_START 缺少 ctx 字段（行{first.line_no}）"
                )

        if last.event not in ("CMD_COMPLETE", "CMD_ERROR"):
            self.errors.append(
                f"违反铁律四：最后一条日志是 {last.event} 而非 CMD_COMPLETE/CMD_ERROR（行{last.line_no}）— 链路未闭环"
            )

        open_steps: dict[str, LogEntry] = {}
        for entry in self.entries:
            if entry.event == "STEP_ENTER":
                if entry.step in open_steps:
                    self.warnings.append(
                        f"STEP_ENTER {entry.step} 嵌套但未STEP_COMPLETE前一个（行{entry.line_no}）"
                    )
                open_steps[entry.step] = entry
            elif entry.event == "STEP_COMPLETE":
                if entry.step not in open_steps:
                    self.warnings.append(
                        f"STEP_COMPLETE {entry.step} 无对应STEP_ENTER（行{entry.line_no}）"
                    )
                else:
                    del open_steps[entry.step]

        for step, enter_entry in open_steps.items():
            self.warnings.append(
                f"STEP_ENTER {step}（行{enter_entry.line_no}）无对应STEP_COMPLETE — 违反铁律三"
            )

        if first.event == "CMD_START" and last.event in ("CMD_COMPLETE", "CMD_ERROR"):
            if first.session != last.session:
                self.errors.append(
                    f"违反铁律四：session ID不一致（开头{first.session} vs 结尾{last.session}）"
                )


def parse_cmd_log_lines(content: str) -> list[LogEntry]:
    entries: list[LogEntry] = []
    for i, line in enumerate(content.split("\n"), 1):
        line_stripped = line.strip()
        if "[CMD-LOG]" not in line_stripped:
            continue
        if line_stripped.startswith("`") or line_stripped.startswith("[CMD-LOG]"):
            cleaned = line_stripped.lstrip("`").rstrip("`").strip()
            m = CMD_LOG_LINE_RE.match(cleaned)
            if m:
                entries.append(LogEntry(
                    level=m.group(1),
                    cmd=m.group(2),
                    step=m.group(3),
                    event=m.group(4),
                    session=m.group(5),
                    msg=m.group(6).strip(),
                    ctx=m.group(7).strip() if m.group(7) else None,
                    line_no=i,
                ))
    return entries


def group_by_session(entries: list[LogEntry]) -> dict[str, SessionChain]:
    sessions: dict[str, SessionChain] = {}
    for entry in entries:
        if entry.session not in sessions:
            sessions[entry.session] = SessionChain(session_id=entry.session, cmd=entry.cmd)
        sessions[entry.session].entries.append(entry)
    return sessions


def check_skill_file(skill_dir: Path, cmd_info: dict) -> list[CheckResult]:
    results: list[CheckResult] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        results.append(CheckResult(
            name=f"Skill门面存在性",
            passed=False,
            severity="ERROR",
            message=f"缺少SKILL.md文件",
            file=str(skill_md.relative_to(PROJECT_ROOT)),
            rule_id="SKILL-MISSING",
        ))
        return results

    content = skill_md.read_text(encoding="utf-8", errors="replace")

    has_cmd_log_section = bool(re.search(r"CMD-LOG|执行日志|日志规范", content, re.IGNORECASE))
    if not has_cmd_log_section:
        results.append(CheckResult(
            name=f"CMD-LOG规范章节",
            passed=False,
            severity="ERROR",
            message=f"SKILL.md缺少CMD-LOG执行日志规范章节（铁律一的设计层面违反）",
            file=str(skill_md.relative_to(PROJECT_ROOT)),
            rule_id="SKILL-NO-CMDLOG-SECTION",
        ))
    else:
        results.append(CheckResult(
            name=f"CMD-LOG规范章节",
            passed=True,
            severity="PASS",
            message=f"包含CMD-LOG执行日志规范",
            file=str(skill_md.relative_to(PROJECT_ROOT)),
        ))

    has_start_first = bool(re.search(r"CMD_START.*第一条|首条.*CMD_START|S0.*第一条|第一条.*输出", content))
    if not has_start_first:
        results.append(CheckResult(
            name=f"首条日志铁律引用",
            passed=False,
            severity="WARN",
            message=f"SKILL.md未明确提及'S0 CMD_START必须是第一条输出'铁律（v1.3.0要求）",
            file=str(skill_md.relative_to(PROJECT_ROOT)),
            rule_id="SKILL-NO-FIRST-LOG-RULE",
        ))
    else:
        results.append(CheckResult(
            name=f"首条日志铁律引用",
            passed=True,
            severity="PASS",
            message=f"包含首条日志铁律引用",
            file=str(skill_md.relative_to(PROJECT_ROOT)),
        ))

    has_session_prefix = cmd_info["session_prefix"] in content
    if not has_session_prefix:
        results.append(CheckResult(
            name=f"Session ID前缀声明",
            passed=False,
            severity="WARN",
            message=f"未在SKILL.md中声明session前缀 {cmd_info['session_prefix']}",
            file=str(skill_md.relative_to(PROJECT_ROOT)),
            rule_id="SKILL-NO-SESSION-PREFIX",
        ))
    else:
        results.append(CheckResult(
            name=f"Session ID前缀声明",
            passed=True,
            severity="PASS",
            message=f"声明了session前缀 {cmd_info['session_prefix']}",
            file=str(skill_md.relative_to(PROJECT_ROOT)),
        ))

    return results


def _is_historical_file(file_path: Path) -> bool:
    match = re.search(r"(\d{8})", str(file_path))
    if match:
        file_date_str = match.group(1)
        return file_date_str < CMD_LOG_V130_DATE.replace("-", "")
    return False


def check_retrospective_file(file_path: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    rel_path = str(file_path.relative_to(PROJECT_ROOT))
    is_historical = _is_historical_file(file_path)

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        results.append(CheckResult(
            name="文件读取",
            passed=False,
            severity="ERROR",
            message=f"无法读取文件: {e}",
            file=rel_path,
            rule_id="IO-ERROR",
        ))
        return results

    entries = parse_cmd_log_lines(content)
    if not entries:
        return results

    sessions = group_by_session(entries)
    for session_id, chain in sessions.items():
        chain.validate()
        for err in chain.errors:
            severity = "WARN" if is_historical else "ERROR"
            msg = err + HISTORICAL_CUTOFF_MSG if is_historical else err
            results.append(CheckResult(
                name=f"链路完整性 [{session_id}]",
                passed=False,
                severity=severity,
                message=msg,
                file=rel_path,
                rule_id="CHAIN-BROKEN" if not is_historical else "CHAIN-HISTORICAL",
            ))
        for warn in chain.warnings:
            msg = warn + HISTORICAL_CUTOFF_MSG if is_historical else warn
            results.append(CheckResult(
                name=f"链路完整性 [{session_id}]",
                passed=False,
                severity="WARN",
                message=msg,
                file=rel_path,
                rule_id="CHAIN-WARNING",
            ))
        if not chain.errors and not chain.warnings:
            results.append(CheckResult(
                name=f"链路完整性 [{session_id}]",
                passed=True,
                severity="PASS",
                message=f"CMD-LOG链路完整（{len(chain.entries)}条日志，cmd={chain.cmd}）",
                file=rel_path,
            ))

    return results


def run_checks(check_skills: bool, check_retros: bool, verbose: bool) -> list[CheckResult]:
    all_results: list[CheckResult] = []

    if check_skills:
        for skill_dir_name, cmd_info in CMD_LOG_COMMANDS.items():
            skill_dir = SKILLS_DIR / skill_dir_name
            if not skill_dir.exists():
                all_results.append(CheckResult(
                    name=f"Skill目录存在性",
                    passed=False,
                    severity="WARN",
                    message=f"Skill目录不存在: {skill_dir_name}",
                    file=str(skill_dir.relative_to(PROJECT_ROOT)),
                    rule_id="SKILL-DIR-MISSING",
                ))
                continue
            all_results.extend(check_skill_file(skill_dir, cmd_info))

    if check_retros:
        retro_files = list(RETROS_DIR.rglob("execution-retrospective.md"))
        for retro_file in retro_files:
            all_results.extend(check_retrospective_file(retro_file))

    return all_results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CMD-LOG v1.3.0 合规性检查器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_common_args(parser)
    parser.add_argument("--skills", action="store_true", help="仅检查Skill门面规范合规性")
    parser.add_argument("--retros", action="store_true", help="仅检查复盘文档CMD-LOG链路完整性")
    parser.add_argument("--all", action="store_true", help="全部检查（默认）")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")
    args = parser.parse_args()

    setup_safe_output()

    check_skills = args.skills or args.all or (not args.skills and not args.retros)
    check_retros = args.retros or args.all or (not args.skills and not args.retros)

    print_header("CMD-LOG v1.3.0 合规性检查")

    results = run_checks(check_skills, check_retros, args.verbose)

    errors = [r for r in results if r.severity == "ERROR" and not r.passed]
    warns = [r for r in results if r.severity == "WARN" and not r.passed]
    passes = [r for r in results if r.passed]

    if args.json:
        output = {
            "checker": "check-cmd-log-compliance",
            "version": "1.3.0",
            "summary": {"total": len(results), "pass": len(passes), "error": len(errors), "warn": len(warns)},
            "results": [
                {"name": r.name, "passed": r.passed, "severity": r.severity, "message": r.message,
                 "file": r.file, "line": r.line, "rule_id": r.rule_id}
                for r in results
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        for r in results:
            if not r.passed:
                loc = f"{r.file}:" if r.file else ""
                if r.severity == "ERROR":
                    print_error(f"  ✗ {r.name}: {r.message} ({loc}{r.rule_id or ''})")
                else:
                    print_warn(f"  ⚠ {r.name}: {r.message} ({loc}{r.rule_id or ''})")
            elif args.verbose:
                loc = f"{r.file}:" if r.file else ""
                print_pass(f"  ✓ {r.name}: {r.message} ({loc})")

        print()
        print_summary(len(passes), len(warns), len(errors))

        if errors:
            print()
            print_error(f"  {len(errors)} 个ERROR级违规（违反🔴强制铁律）：")
            for e in errors:
                loc = f"[{e.file}]" if e.file else ""
                print_error(f"    - {e.name}: {e.message} {loc}")
        if warns:
            print()
            print_warn(f"  {len(warns)} 个WARN级警告（违反🟡建议条款）：")
            for w in warns:
                loc = f"[{w.file}]" if w.file else ""
                print_warn(f"    - {w.name}: {w.message} {loc}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
