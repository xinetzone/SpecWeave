"""Spec 元数据扫描 — status 值域校验 + 三件套完整性校验"""

# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import collections
import json
import sys

from pathlib import Path
from lib.frontmatter import parse_frontmatter_unified

PROJ_ROOT = _Path(__file__).resolve().parent.parent.parent  # scripts → .agents → root
SPEC_ROOT = PROJ_ROOT / '.trae' / 'specs'

VALID_STATUSES = {
    'draft', 'planning', 'in-progress', 'approved', 'implemented', 'completed',
    'pending-approval', 'review', 'deprecated', 'archived',
}


def main():
    violations = []
    status_dist = collections.Counter()
    total_specs = 0
    no_frontmatter = 0

    for spec_dir in sorted(SPEC_ROOT.rglob('spec.md')):
        if not spec_dir.parent.is_dir():
            continue
        total_specs += 1
        parent = spec_dir.parent
        rel = spec_dir.relative_to(PROJ_ROOT).as_posix()

        # Check three-piece set
        tasks_md = parent / 'tasks.md'
        checklist_md = parent / 'checklist.md'
        missing = []
        if not tasks_md.exists():
            missing.append('tasks.md')
        if not checklist_md.exists():
            missing.append('checklist.md')
        if missing:
            violations.append({
                'type': 'missing_triad',
                'file': rel,
                'message': f"缺三件套: {', '.join(missing)}",
                'severity': 'error',
            })

        # Parse frontmatter
        try:
            fm = parse_frontmatter_unified(spec_dir)
        except Exception as e:
            violations.append({
                'type': 'fm_parse_error',
                'file': rel,
                'message': f"frontmatter 解析失败: {e}",
                'severity': 'error',
            })
            no_frontmatter += 1
            continue

        if not fm:
            violations.append({
                'type': 'no_frontmatter',
                'file': rel,
                'message': "无 frontmatter（缺失 --- ... --- 或 +++ ... +++ 块）",
                'severity': 'error',
            })
            no_frontmatter += 1
            continue

        status = fm.get('status')
        if status is None:
            violations.append({
                'type': 'missing_status',
                'file': rel,
                'message': "frontmatter 中缺少 status 字段",
                'severity': 'warning',
            })
            status_dist['(none)'] += 1
        else:
            status_str = str(status).strip().lower()
            status_dist[status_str] += 1
            if status_str not in {s.lower() for s in VALID_STATUSES}:
                violations.append({
                    'type': 'invalid_status',
                    'file': rel,
                    'message': f"status 值 '{status}' 不在合法值域内（合法值域: {sorted(VALID_STATUSES)}）",
                    'severity': 'error',
                })

    # Print summary
    sep = '=' * 60
    print(sep)
    print("Spec 元数据扫描报告")
    print(sep)
    print(f"扫描根: {SPEC_ROOT}")
    print(f"总计 spec.md 数: {total_specs}")
    print(f"无 frontmatter:  {no_frontmatter}")
    print()
    print("-- status 值域分布 --")
    illegal_set = {s.lower() for s in VALID_STATUSES}
    for k, v in sorted(status_dist.items(), key=lambda x: -x[1]):
        flag = " [非法]" if k not in illegal_set and k != '(none)' else ""
        print(f"  {k:25s}: {v}{flag}")
    print()

    error_count = sum(1 for v in violations if v['severity'] == 'error')
    warn_count = sum(1 for v in violations if v['severity'] == 'warning')
    print(f"-- 违规清单 ({error_count} 错误, {warn_count} 警告) --")
    by_cat = collections.defaultdict(list)
    for v in violations:
        by_cat[v['type']].append(v)
    for cat, items in sorted(by_cat.items()):
        print(f"\n  [{cat}] ({len(items)}个)")
        for item in items[:20]:
            mark = "[E]" if item['severity'] == 'error' else "[W]"
            print(f"    {mark} {item['file']}")
            print(f"        {item['message']}")
        if len(items) > 20:
            print(f"    ... 还有 {len(items) - 20} 个，已截断")
    print()
    print(sep)
    if error_count == 0:
        print(f"扫描通过（{warn_count} 个警告）")
    else:
        print(f"发现 {error_count} 个错误，{warn_count} 个警告")
    print(sep)

    # Also output JSON for CI integration
    out_path = PROJ_ROOT / '.temp' / 'spec-metadata-violations.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total': total_specs,
            'no_frontmatter': no_frontmatter,
            'error_count': error_count,
            'warning_count': warn_count,
            'violations': violations,
            'status_dist': dict(status_dist),
        }, f, ensure_ascii=False, indent=2)
    print(f"\nJSON 报告已写入: {out_path}")


if __name__ == '__main__':
    main()
