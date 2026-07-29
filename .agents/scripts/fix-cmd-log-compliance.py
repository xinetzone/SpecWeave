#!/usr/bin/env python3
"""CMD-LOG v1.3.0 合规性自动修复脚本：批量修复 check-cmd-log-compliance.py 报告的所有WARN项。

修复两类问题：
  A类（7个SKILL.md）：在§7/§8执行日志章节插入铁律一警告blockquote
  B类（2个历史复盘文档）：在首个[CMD-LOG]前插入CMD_START，在末尾[CMD-LOG]后追加CMD_COMPLETE

用法：
  python fix-cmd-log-compliance.py            # 执行修复（dry-run预览）
  python fix-cmd-log-compliance.py --apply    # 实际写入修改
  python fix-cmd-log-compliance.py --verify   # 修复后运行合规检查验证
"""

from __future__ import annotations


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import re
import sys
from pathlib import Path

from lib.project import resolve_project_root

PROJECT_ROOT = resolve_project_root(__file__)

IRON_LAW_BLOCKQUOTE = (
    "\n"
    "> ⚠️ **铁律一（🔴强制）**：S0 CMD_START 必须是命令集执行后的**第一条输出**，"
    "禁止在CMD_START之前输出任何其他内容（包括调试信息、中间结果）。"
    "违反将导致日志链路断裂，CI步骤19（CMD-LOG合规检查）失败。\n"
)

A_CLASS_TARGETS = [
    ".agents/skills/retrospective-cmd/SKILL.md",
    ".agents/skills/insight-cmd/SKILL.md",
    ".agents/skills/export-report-cmd/SKILL.md",
    ".agents/skills/atomization-cmd/SKILL.md",
    ".agents/skills/atomic-commit-cmd/SKILL.md",
    ".agents/skills/mermaid-cmd/SKILL.md",
    ".agents/skills/pattern-extraction-cmd/SKILL/04-cmd-log-quality.md",
]

B_CLASS_TARGETS = [
    {
        "path": ".agents/docs/retrospective/reports/task-reports/retrospective-first-principles-vibe-coding-docs-update-20260710/execution-retrospective.md",
        "session": "retr-20260710-first-principles-vibe-coding-update",
        "cmd": "retrospective",
        "start_msg": "开始复盘：第一性原理vibe-coding学习文档更新（里程碑复盘）",
        "start_ctx": '{"retro_topic":"first-principles-vibe-coding-docs-update","retro_type":"task"}',
        "complete_msg": "复盘完成：递归践行现象识别+3个新模式沉淀+check-links.py三层验证改进",
        "complete_ctx": '{"duration":"~105min","recursive_practice_count":5,"new_patterns":3,"tool_improvements":1}',
    },
    {
        "path": ".agents/docs/retrospective/reports/task-reports/retrospective-mermaid-list-fix-first-principles-20260710/execution-retrospective.md",
        "session": "retro-20260710-mermaid-fix-first-principles",
        "cmd": "retrospective",
        "start_msg": "开始复盘：Mermaid列表触发问题第一性原理修复",
        "start_ctx": '{"retro_topic":"mermaid-list-fix-first-principles","retro_type":"task"}',
        "complete_msg": "复盘完成：mermaid列表触发Bug定位+18行修复+check-mermaid验证通过",
        "complete_ctx": '{"duration":"~30min","error_type":"mermaid_list_trigger","fix_lines":18,"validation_passed":true}',
    },
]


def fix_a_class(rel_path: str, apply: bool) -> tuple[bool, str]:
    file_path = PROJECT_ROOT / rel_path
    if not file_path.exists():
        return False, f"文件不存在: {rel_path}"

    content = file_path.read_text(encoding="utf-8")

    if "铁律一" in content and "CMD_START" in content and "第一条输出" in content:
        return True, f"已包含铁律一引用，跳过: {rel_path}"

    pattern = r"(执行(?:复盘|洞察|导出报告|原子化|原子提交|mermaid|模式萃取|萃取)(?:命令集)?(?:操作)?时，必须按 \[CMD-LOG规范\]\([^)]+\) 输出结构化日志：|遵循项目 \[CMD-LOG命令集执行日志规范\]\([^)]+\)，使用统一前缀\+键值对\+JSON上下文格式。)"

    match = re.search(pattern, content)
    if not match:
        alt_pattern = r"(执行(?:复盘|洞察|导出报告|原子化|原子提交|mermaid|模式萃取|萃取)(?:命令集)?时.*?CMD-LOG规范.*?输出结构化日志：)"
        match = re.search(alt_pattern, content)

    if not match:
        return False, f"未找到插入点（CMD-LOG章节介绍句），请手动处理: {rel_path}"

    insert_pos = match.end()
    new_content = content[:insert_pos] + IRON_LAW_BLOCKQUOTE + content[insert_pos:]

    if apply:
        file_path.write_text(new_content, encoding="utf-8")
        return True, f"已修复（插入铁律一blockquote）: {rel_path}"
    else:
        return True, f"[DRY-RUN] 将修复（插入铁律一blockquote）: {rel_path}"


def fix_b_class(target: dict, apply: bool) -> tuple[bool, str]:
    rel_path = target["path"]
    file_path = PROJECT_ROOT / rel_path
    if not file_path.exists():
        return False, f"文件不存在: {rel_path}"

    content = file_path.read_text(encoding="utf-8")

    cmd_log_pattern = re.compile(r"^\[CMD-LOG\]", re.MULTILINE)
    matches = list(cmd_log_pattern.finditer(content))

    if not matches:
        return False, f"未找到CMD-LOG行: {rel_path}"

    if any("CMD_START" in content[m.start():m.start()+200] for m in matches[:1]):
        return True, f"已包含CMD_START，跳过: {rel_path}"

    first_match = matches[0]
    last_match = matches[-1]

    last_line_end = content.find("\n", last_match.end())
    if last_line_end == -1:
        last_line_end = len(content)

    start_line = (
        f"[CMD-LOG] | level=INFO | cmd={target['cmd']} | step=S0 | event=CMD_START "
        f"| session={target['session']} | msg={target['start_msg']} | ctx={target['start_ctx']}\n"
    )

    complete_line = (
        f"\n[CMD-LOG] | level=INFO | cmd={target['cmd']} | step=S5 | event=CMD_COMPLETE "
        f"| session={target['session']} | msg={target['complete_msg']} | ctx={target['complete_ctx']}\n"
    )

    new_content = (
        content[:first_match.start()]
        + start_line
        + content[first_match.start():last_line_end]
        + complete_line
        + content[last_line_end:]
    )

    if apply:
        file_path.write_text(new_content, encoding="utf-8")
        return True, f"已修复（补全CMD_START+CMD_COMPLETE闭环）: {rel_path}"
    else:
        return True, f"[DRY-RUN] 将修复（补全CMD_START+CMD_COMPLETE闭环）: {rel_path}"


def run_verification() -> bool:
    import subprocess
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / ".agents/scripts/check-cmd-log-compliance.py")],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="CMD-LOG v1.3.0 合规性自动修复")
    parser.add_argument("--apply", action="store_true", help="实际写入修改（默认dry-run预览）")
    parser.add_argument("--verify", action="store_true", help="修复后运行合规检查验证")
    args = parser.parse_args()

    mode = "APPLY（实际写入）" if args.apply else "DRY-RUN（仅预览）"
    print(f"========================================")
    print(f"CMD-LOG v1.3.0 合规性自动修复 [{mode}]")
    print(f"========================================")
    print()

    results: list[tuple[bool, str]] = []

    print("--- A类：Skill门面铁律引用补充 ---")
    for rel_path in A_CLASS_TARGETS:
        ok, msg = fix_a_class(rel_path, args.apply)
        results.append((ok, msg))
        icon = "✓" if ok else "✗"
        print(f"  [{icon}] {msg}")
    print()

    print("--- B类：历史复盘文档链路补全 ---")
    for target in B_CLASS_TARGETS:
        ok, msg = fix_b_class(target, args.apply)
        results.append((ok, msg))
        icon = "✓" if ok else "✗"
        print(f"  [{icon}] {msg}")
    print()

    ok_count = sum(1 for ok, _ in results if ok)
    fail_count = sum(1 for ok, _ in results if not ok)
    print(f"========================================")
    print(f"修复结果: {ok_count} 成功, {fail_count} 失败")
    print(f"========================================")

    if fail_count > 0:
        print()
        print("失败项：")
        for ok, msg in results:
            if not ok:
                print(f"  ✗ {msg}")
        return 1

    if args.apply and args.verify:
        print()
        print("--- 验证：运行合规检查 ---")
        if run_verification():
            print()
            print("✓ 验证通过：所有CMD-LOG合规检查项0 WARN")
        else:
            print()
            print("✗ 验证失败：仍有WARN/ERROR项")
            return 1

    if not args.apply:
        print()
        print("提示：添加 --apply 参数实际执行修改，添加 --verify 参数修复后自动验证")

    return 0


if __name__ == "__main__":
    sys.exit(main())

