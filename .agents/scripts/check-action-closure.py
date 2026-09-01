#!/usr/bin/env python3
"""P-2 洞察到行动的闭环检查器。

基于可复用模式「洞察到行动的闭环（insight-to-action-closed-loop）」，扫描复盘报告中的
行动项，检查每个行动项是否具备可行动要素（优先级 / Owner / 验收标准 / 闭环状态），
并标记「假闭环」风险（洞察产出但未落为可验证行动的清单）。

用法：
  python check-action-closure.py                          # 扫描默认目录 docs/retrospective/reports
  python check-action-closure.py --path <文件或目录>      # 指定目标
  python check-action-closure.py --path <dir> --json      # JSON 输出

退出码：
  0  所有行动项要素齐备，无假闭环风险
  1  存在要素缺失或假闭环风险
  2  路径不存在或参数错误

与相关脚本的边界：
  - check-action-items.py：提取「行动计划表格」中「待规划」状态的条目（表格 + 待办提取）；
    本脚本聚焦「列表式行动项」的「闭环质量检查」（可行动要素 + 假闭环风险），互补不重复。
"""

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from lib.cli import (
    setup_safe_output,
    print_pass,
    print_warn,
    print_error,
    print_summary,
    add_common_args,
)
from lib.project import resolve_project_root

DEFAULT_REPORTS_DIR = (
    resolve_project_root(__file__) / ".agents" / "docs" / "retrospective" / "reports"
)

# 行动项章节标题（兼容中英文、编号前缀）
SECTION_RE = re.compile(
    r"^#{1,4}\s*[^#\n]*?(行动项|行动计划|行动清单|Action\s*Items?)[^#\n]*$",
    re.IGNORECASE,
)
# 加粗 ID 列表项：- **ACT-1**（优先级：高）：描述
ITEM_RE = re.compile(r"^\s*[-*]\s+\*\*(?P<id>[^*]+?)\*\*\s*(?P<rest>.*)$")
# checkbox 列表项：- [ ] 描述 / - [x] 描述
CHECKBOX_RE = re.compile(r"^\s*[-*]\s+\[(?P<state>[ xX])\]\s+(?P<text>.*)$")
# 缩进子属性：  - 验收标准：xxx
SUB_RE = re.compile(r"^\s{2,}[-*]\s+(?P<key>[^:：]+?)[:：]\s*(?P<value>.*)$")

PRIORITY_IN_TEXT = re.compile(r"优先级[:：]\s*([高中低])")


@dataclass
class ActionItem:
    """复盘报告中的一条行动项。"""

    id: str
    title: str
    line: int
    priority: str = ""
    owner: str = ""
    acceptance: str = ""
    status: str = ""


def _extract_priority(text: str) -> str:
    """从文本中提取优先级标注，支持「优先级：高」与 P0/P1 编号形式。"""
    m = PRIORITY_IN_TEXT.search(text)
    if m:
        return m.group(1)
    # P0/P1 → 高/中（P0 最高优先级），P2 及以后视为低
    pm = re.search(r"(?<!\w)P(?P<n>[0-3])(?!\w)", text)
    if pm:
        return {"0": "高", "1": "中", "2": "低", "3": "低"}[pm.group("n")]
    return ""


def _clean_title(text: str) -> str:
    """清理行动项标题：移除优先级标注与残留的空括号/冒号前缀。"""
    text = PRIORITY_IN_TEXT.sub("", text)
    text = re.sub(r"[（(]\s*[）)]\s*[：:]?\s*", "", text)
    return text.strip().lstrip("：:").strip()


def scan_file(file_path: Path) -> list[ActionItem]:
    """扫描单个 Markdown 文件，返回其行动项列表。"""
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []

    items: list[ActionItem] = []
    in_section = False
    current: ActionItem | None = None

    def _flush():
        nonlocal current
        if current is not None:
            items.append(current)
            current = None

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()

        # 标题切换：进入行动项章节，或遇到其他标题时结束章节
        if stripped.startswith("#"):
            _flush()
            in_section = bool(SECTION_RE.match(stripped))
            continue

        if not in_section:
            continue

        m = ITEM_RE.match(line)
        if m:
            _flush()
            rest = m.group("rest").strip()
            current = ActionItem(
                id=m.group("id").strip(),
                title=_clean_title(rest),
                line=idx,
            )
            current.priority = _extract_priority(rest)
            continue

        cm = CHECKBOX_RE.match(line)
        if cm:
            _flush()
            text = cm.group("text").strip()
            current = ActionItem(
                id=f"checkbox:{idx}",
                title=_clean_title(text),
                line=idx,
                status=("已完成" if cm.group("state") in ("x", "X") else ""),
            )
            current.priority = _extract_priority(text)
            continue

        sm = SUB_RE.match(line)
        if sm and current is not None:
            key = sm.group("key").strip()
            value = sm.group("value").strip()
            if "优先级" in key:
                current.priority = value
            elif "验收" in key or "Acceptance" in key.lower():
                current.acceptance = value
            elif "Owner" in key or "负责人" in key or "责任人" in key:
                current.owner = value
            elif "状态" in key:
                current.status = value
            continue

    if current is not None:
        _flush()

    return items


def _closure_category(status: str) -> str:
    """对行动项状态进行闭环归类，返回 closed/explicit-skip/open/unknown。"""
    s = status.lower()
    if not status.strip():
        return "unknown"
    if any(k in s for k in ("完成", "✅", "done", "关闭", "已闭环", "已提交", "closed", "已推送")):
        return "closed"
    if any(k in s for k in ("不行动", "won't", "豁免", "不需要", "不再", "无需", "skip")):
        return "explicit-skip"
    return "open"


def check_item(item: ActionItem) -> list[str]:
    """检查单个行动项的可行动要素，返回问题列表。"""
    issues: list[str] = []
    if not item.priority:
        issues.append("缺优先级（P-2 要求行动项可排序）")
    if not item.owner:
        issues.append("缺 Owner（P-2 要求可追踪到人）")
    if not item.acceptance:
        issues.append("缺验收标准（无法判断闭环是否达成）")

    cat = _closure_category(item.status)
    if cat == "unknown":
        issues.append("未标注状态，无法验证闭环")
    elif cat == "open":
        issues.append(f"状态为「待处理/进行中」，尚未闭环：{item.status}")
    return issues


def scan_path(path: Path) -> list[tuple[Path, list[ActionItem]]]:
    """扫描文件或目录，返回 [(文件路径, 行动项列表), ...]。"""
    if path.is_file():
        return [(path, scan_file(path))]
    if path.is_dir():
        results = []
        for md in sorted(path.rglob("*.md")):
            items = scan_file(md)
            if items:
                results.append((md, items))
        return results
    return []


def _to_dict(path: Path, items: list[ActionItem]) -> dict:
    records = []
    closed = 0
    for it in items:
        issues = check_item(it)
        cat = _closure_category(it.status)
        if cat in ("closed", "explicit-skip") and not issues:
            closed += 1
        records.append({
            "id": it.id,
            "title": it.title,
            "line": it.line,
            "priority": it.priority,
            "owner": it.owner,
            "acceptance": it.acceptance,
            "status": it.status,
            "issues": issues,
        })
    total = len(items)
    return {
        "report": str(path),
        "total_count": total,
        "closed_count": closed,
        "open_count": total - closed,
        "closure_rate": round(closed / total, 2) if total else 0.0,
        "fake_closure_risk": any(("缺验收标准" in i or "未标注状态" in i) for r in records for i in r["issues"]),
        "action_items": records,
    }


def main() -> int:
    setup_safe_output()
    parser = argparse.ArgumentParser(
        description="P-2 洞察到行动的闭环检查器（可行动要素 + 假闭环风险）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_common_args(parser)
    args = parser.parse_args()

    target = args.path if args.path else DEFAULT_REPORTS_DIR
    if not target.exists():
        print_error(f"路径不存在：{target}")
        return 2

    results = scan_path(target)
    if not results:
        print_pass("未发现含行动项的报告文件")
        return 0

    total_items = 0
    total_pass = 0
    total_warn = 0
    all_records = []

    for path, items in results:
        if args.json:
            all_records.append(_to_dict(path, items))
            total_items += len(items)
            continue

        print()
        print(f"文件: {path.name}（{len(items)} 条行动项）")
        for idx, it in enumerate(items, 1):
            issues = check_item(it)
            flags = []
            flags.append(f"优先级:{it.priority or '—'}")
            flags.append(f"Owner:{it.owner or '—'}")
            flags.append(f"验收:{'✓' if it.acceptance else '—'}")
            flags.append(f"状态:{it.status or '—'}")
            print(f"  [{idx}] {it.id}  {it.title[:60]}")
            print(f"       {' | '.join(flags)}")
            for issue in issues:
                print_warn(f"{it.id}: {issue}")
                total_warn += 1
            if not issues:
                total_pass += 1
        total_items += len(items)

    if args.json:
        print(json.dumps(all_records, ensure_ascii=False, indent=2))
        return 1 if total_items == 0 else 0

    print()
    print_summary(pass_count=total_pass, warn_count=total_warn, error_count=0)
    print(f"行动项总数：{total_items} | 要素完整项：{total_pass} | 存在问题项：{total_warn}")
    print("提示：缺 Owner / 验收标准 / 状态的行动项存在「假闭环」风险，需补齐后跟踪到提交。")
    return 1 if total_warn > 0 else 0


if __name__ == "__main__":
    sys.exit(main())