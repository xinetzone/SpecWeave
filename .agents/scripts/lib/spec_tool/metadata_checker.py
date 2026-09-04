"""Spec 元数据校验器。

校验项：
- spec.md + tasks.md + review.md 三件套完整性
- frontmatter 存在性
- status 字段存在性
- status 值合法性（以 VALID_STATUSES 为准）
- 提供 status 值域分布统计

常量（VALID_STATUSES、三件套命名）统一从 constants.py 引入，
确保整个工具链的单一事实来源。
"""

# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

import collections
import warnings
from pathlib import Path
from typing import Any

from lib.frontmatter import parse_frontmatter_unified
from .constants import VALID_STATUSES, SPEC_TRIPLET


def check_spec_metadata(spec_md_path: Path, project_root: Path) -> dict[str, Any]:
    """校验单个 spec.md 的元数据。

    返回：
      - violations: list[dict] 违规列表
      - status: str | None  当前 status 值
      - has_frontmatter: bool
    """
    result: dict[str, Any] = {
        "file": spec_md_path.relative_to(project_root).as_posix(),
        "violations": [],
        "status": None,
        "has_frontmatter": False,
    }

    parent = spec_md_path.parent
    rel = result["file"]

    # === 三件套完整性 ===
    missing = []
    for name in SPEC_TRIPLET:
        if not (parent / name).exists():
            missing.append(name)
    if missing:
        result["violations"].append({
            "type": "missing_triad",
            "file": rel,
            "message": f"缺三件套: {', '.join(missing)}（规范：spec.md + tasks.md + review.md）",
            "severity": "error",
        })

    # === frontmatter 存在性 & status 校验 ===
    try:
        with warnings.catch_warnings():
            # 校验工具需要识别所有格式（包括已废弃的 TOML），静默处理即可
            warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*TOML frontmatter.*")
            fm = parse_frontmatter_unified(spec_md_path)
    except Exception as e:
        result["violations"].append({
            "type": "fm_parse_error",
            "file": rel,
            "message": f"frontmatter 解析失败: {e}",
            "severity": "error",
        })
        return result

    if not fm:
        result["violations"].append({
            "type": "no_frontmatter",
            "file": rel,
            "message": "无 frontmatter（缺失 --- ... --- 或 +++ ... +++ 块）",
            "severity": "error",
        })
        return result

    result["has_frontmatter"] = True

    status = fm.get("status")
    if status is None:
        result["violations"].append({
            "type": "missing_status",
            "file": rel,
            "message": "frontmatter 中缺少 status 字段",
            "severity": "warning",
        })
        return result

    status_str = str(status).strip()
    result["status"] = status_str
    if status_str not in VALID_STATUSES:
        result["violations"].append({
            "type": "invalid_status",
            "file": rel,
            "message": f"status 值 '{status_str}' 不在合法值域内（合法值域: {sorted(VALID_STATUSES)}）",
            "severity": "error",
        })

    return result


def scan_spec_metadata(spec_root: Path, project_root: Path) -> dict[str, Any]:
    """批量扫描 spec_root 下所有 spec.md 的元数据。

    返回汇总报告：
      - total: int
      - no_frontmatter: int
      - error_count: int
      - warning_count: int
      - violations: list[dict]
      - status_dist: dict[str, int]
      - per_file: dict[str, dict]  每个文件的详细结果
    """
    violations: list[dict] = []
    status_dist: collections.Counter[str] = collections.Counter()
    total = 0
    no_frontmatter = 0
    per_file: dict[str, dict] = {}

    if not spec_root.exists():
        return {
            "total": 0, "no_frontmatter": 0,
            "error_count": 0, "warning_count": 0,
            "violations": [], "status_dist": {}, "per_file": {},
        }

    for spec_md in sorted(spec_root.rglob("spec.md")):
        total += 1
        r = check_spec_metadata(spec_md, project_root)
        per_file[r["file"]] = r
        violations.extend(r["violations"])

        if not r["has_frontmatter"]:
            no_frontmatter += 1
            status_dist["(none)"] += 1
        elif r["status"] is None:
            status_dist["(none)"] += 1
        else:
            status_dist[r["status"]] += 1

    error_count = sum(1 for v in violations if v["severity"] == "error")
    warn_count = sum(1 for v in violations if v["severity"] == "warning")

    return {
        "total": total,
        "no_frontmatter": no_frontmatter,
        "error_count": error_count,
        "warning_count": warn_count,
        "violations": violations,
        "status_dist": dict(status_dist),
        "per_file": per_file,
    }


def format_terminal_report(report: dict, spec_root: Path) -> str:
    """生成终端可读的文本报告。"""
    lines = []
    sep = "=" * 60
    lines.append(sep)
    lines.append("Spec 元数据扫描报告")
    lines.append(sep)
    lines.append(f"扫描根: {spec_root}")
    lines.append(f"总计 spec.md 数: {report['total']}")
    lines.append(f"无 frontmatter:  {report['no_frontmatter']}")
    lines.append("")
    lines.append("-- status 值域分布 --")
    for k, v in sorted(report["status_dist"].items(), key=lambda x: -x[1]):
        flag = " [非法]" if k not in VALID_STATUSES and k != "(none)" else ""
        lines.append(f"  {k:25s}: {v}{flag}")
    lines.append("")

    ec = report["error_count"]
    wc = report["warning_count"]
    lines.append(f"-- 违规清单 ({ec} 错误, {wc} 警告) --")

    by_cat: dict[str, list[dict]] = collections.defaultdict(list)
    for v in report["violations"]:
        by_cat[v["type"]].append(v)

    for cat, items in sorted(by_cat.items()):
        lines.append(f"\n  [{cat}] ({len(items)}个)")
        for item in items[:20]:
            mark = "[E]" if item["severity"] == "error" else "[W]"
            lines.append(f"    {mark} {item['file']}")
            lines.append(f"        {item['message']}")
        if len(items) > 20:
            lines.append(f"    ... 还有 {len(items) - 20} 个，已截断")

    lines.append("")
    lines.append(sep)
    if ec == 0:
        lines.append(f"扫描通过（{wc} 个警告）")
    else:
        lines.append(f"发现 {ec} 个错误，{wc} 个警告")
    lines.append(sep)
    return "\n".join(lines)
