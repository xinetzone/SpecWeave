import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from lib.project import resolve_project_root
from lib.cli import add_common_args

from .constants import BATCH_DEFAULT_TARGETS, PROFILES
from .discovery import collect_md_files
from .scoring import get_grade, compute_metrics, compute_scores
from .reporter import print_single_result, print_batch_result, print_batch_json


def auto_detect_profile(dir_path: str) -> str:
    dir_lower = dir_path.rstrip('/').lower()
    if 'scripts' in dir_lower:
        return 'code'
    if '/.agents' in dir_lower or dir_lower.endswith('.agents') or dir_lower == '.agents':
        return 'specs'
    return 'docs'


def measure_directory(target_dir: Path, project_root: Path, profile_name: str,
                      user_exclude_dirs: set = None, user_exclude_files: set = None,
                      since_date: str = None) -> dict:
    profile = PROFILES[profile_name]
    exclude_dirs = set(user_exclude_dirs or set())
    exclude_dirs.add('.pytest_cache')
    exclude_dirs.add('tests')
    exclude_dirs |= profile['default_exclude_dirs']
    exclude_files = set(user_exclude_files or set()) | profile['default_exclude_files']

    md_files = collect_md_files(target_dir, exclude_dirs, exclude_files)
    metrics = compute_metrics(md_files, project_root, since_date=since_date)
    scores = compute_scores(metrics, weights=profile['weights'])

    rel_dir = target_dir.relative_to(project_root).as_posix() if target_dir.is_relative_to(project_root) else str(target_dir).replace('\\', '/')
    return {
        'dir': rel_dir,
        'dir_abs': str(target_dir),
        'profile': profile_name,
        'profile_desc': profile['description'],
        'metrics': metrics,
        'scores': scores,
        'exclude_dirs': exclude_dirs,
        'exclude_files': exclude_files,
        'user_exclude_dirs': set(user_exclude_dirs or set()),
        'grade': get_grade(scores.get('overall_adoption_score', 0)),
    }


def run_batch(project_root: Path, user_targets: list = None, user_exclude_dirs: set = None,
              user_exclude_files: set = None, since_date: str = None, output_file: str = None,
              use_json: bool = False):
    if user_targets:
        targets = []
        for t in user_targets:
            parts = t.split(':')
            dir_path = parts[0]
            profile = parts[1] if len(parts) > 1 else auto_detect_profile(dir_path)
            targets.append((dir_path, profile))
    else:
        targets = BATCH_DEFAULT_TARGETS

    results = []
    total_files = 0
    total_weighted_score = 0.0

    for dir_str, profile_name in targets:
        target_dir = (project_root / dir_str).resolve()
        if not target_dir.exists():
            print(f'⚠️  目录不存在，跳过: {dir_str}')
            continue
        result = measure_directory(
            target_dir, project_root, profile_name,
            user_exclude_dirs=user_exclude_dirs,
            user_exclude_files=user_exclude_files,
            since_date=since_date
        )
        results.append(result)
        tf = result['metrics']['total_files']
        total_files += tf
        total_weighted_score += result['scores']['overall_adoption_score'] * tf

    global_score = round(total_weighted_score / total_files, 1) if total_files > 0 else 0
    global_grade = get_grade(global_score)

    if use_json:
        print_batch_json(results, global_score, global_grade, total_files, project_root, output_file)
    else:
        print_batch_result(results, global_score, global_grade, total_files, project_root, output_file)

    passed = global_score >= 70
    for r in results:
        if r['scores']['overall_adoption_score'] < 70:
            passed = False
            break
    sys.exit(0 if passed else 1)


def main(argv=None):
    parser = argparse.ArgumentParser(description='规范落地度量指标跟踪工具')
    parser.add_argument('--dir', help='目标目录（递归扫描）')
    parser.add_argument('--file', help='单个文件路径')
    parser.add_argument('--since', help='只度量指定日期(YYYY-MM-DD)后修改的文件')
    parser.add_argument('--profile', choices=list(PROFILES.keys()), default='docs',
                        help='度量预设配置：docs(文档区默认)/specs(规范区)/code(代码区)，自动调整指标权重和默认排除项')
    parser.add_argument('--list-profiles', action='store_true', help='列出所有可用预设配置及其说明')
    parser.add_argument('--exclude-dirs', action='append', default=[], dest='exclude_dirs',
                        help='排除的目录名（可多次指定，如 --exclude-dirs skills --exclude-dirs .pytest_cache）')
    parser.add_argument('--exclude', action='append', default=[], dest='_exclude_legacy',
                        help=argparse.SUPPRESS)
    parser.add_argument('--exclude-files', action='append', default=[], dest='exclude_files',
                        help='排除的具体文件名（可多次指定，如 --exclude-files ONBOARDING.md）')
    parser.add_argument('--batch', action='store_true', help='批量扫描所有主要目录并生成对比报告')
    parser.add_argument('--batch-dirs', nargs='+', dest='batch_dirs',
                        help='批量扫描指定目录列表，格式为 dir:profile（如 docs/:docs .agents/:specs），不指定profile则自动检测')
    parser.add_argument('--output', help='批量模式下将对比报告导出为Markdown文件')
    add_common_args(parser)
    args = parser.parse_args(argv)

    if args.list_profiles:
        print('可用预设配置（--profile）：')
        print()
        for name, cfg in PROFILES.items():
            print(f'  {name:<8} {cfg["description"]}')
            print(f'           权重: {", ".join(f"{k}={v}" for k, v in cfg["weights"].items())}')
            if cfg['default_exclude_dirs']:
                print(f'           默认排除目录: {", ".join(cfg["default_exclude_dirs"])}')
            if cfg['default_exclude_files']:
                print(f'           默认排除文件: {", ".join(cfg["default_exclude_files"])}')
            print()
        sys.exit(0)

    project_root = resolve_project_root(__file__)

    if args.batch or args.batch_dirs:
        user_excludes = set(args.exclude_dirs) | set(args._exclude_legacy)
        user_exclude_files = set(args.exclude_files)
        run_batch(
            project_root,
            user_targets=args.batch_dirs,
            user_exclude_dirs=user_excludes,
            user_exclude_files=user_exclude_files,
            since_date=args.since,
            output_file=args.output,
            use_json=args.json,
        )
        return

    if not args.dir and not args.file:
        print('⚠️  请指定 --dir、--file 或 --batch')
        print()
        print('常用用法:')
        print('  python check-spec-adoption.py --dir docs/              # 单目录度量')
        print('  python check-spec-adoption.py --batch                   # 批量对比报告')
        print('  python check-spec-adoption.py --batch --output report.md # 批量+导出报告')
        sys.exit(1)

    user_exclude_dirs = set(args.exclude_dirs) | set(args._exclude_legacy)
    user_exclude_files = set(args.exclude_files)

    if args.file:
        target = Path(args.file).resolve()
        md_files = [target]
        metrics = compute_metrics(md_files, project_root, since_date=args.since)
        scores = compute_scores(metrics, weights=PROFILES[args.profile]['weights'])
        rel_dir = target.parent.relative_to(project_root).as_posix() if target.parent.is_relative_to(project_root) else str(target.parent).replace('\\', '/')
        result = {
            'dir': rel_dir,
            'dir_abs': str(target.parent),
            'profile': args.profile,
            'profile_desc': PROFILES[args.profile]['description'],
            'metrics': metrics,
            'scores': scores,
            'exclude_dirs': user_exclude_dirs | {'.pytest_cache', 'tests'} | PROFILES[args.profile]['default_exclude_dirs'],
            'exclude_files': user_exclude_files | PROFILES[args.profile]['default_exclude_files'],
            'user_exclude_dirs': user_exclude_dirs,
            'grade': get_grade(scores.get('overall_adoption_score', 0)),
        }
    else:
        target_dir = Path(args.dir).resolve() if args.dir else project_root
        result = measure_directory(
            target_dir, project_root, args.profile,
            user_exclude_dirs=user_exclude_dirs,
            user_exclude_files=user_exclude_files,
            since_date=args.since,
        )

    if args.json:
        output = {
            'metrics': result['metrics'],
            'scores': result['scores'],
            'profile': result['profile'],
            'timestamp': datetime.now().isoformat(),
            'project_root': str(project_root),
        }
        del output['metrics']['files_scanned']
        print(json.dumps(output, ensure_ascii=False, indent=2))
        sys.exit(0)

    print_single_result(result, args, project_root)
    sys.exit(0 if result['scores']['overall_adoption_score'] >= 70 else 1)
