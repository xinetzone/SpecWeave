#!/usr/bin/env python3
"""
C扩展Wheel依赖捆绑工具
Pattern: Wheel-Dep-Bundling
Source: XMNN retrospective 2026-07-22

用法:
    python bundle_wheel_deps.py <wheel_unpacked_dir> [--libs-dir tvm/_libs] [--exclude system]

功能:
    1. 递归扫描wheel中所有.so的非系统共享库依赖
    2. 复制到wheel内指定_libs目录
    3. patchelf设置RPATH=$ORIGIN
    4. 重新计算sha256更新RECORD文件
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import os
import re
import shutil
import subprocess
import sys
from collections import deque
from pathlib import Path


SYSTEM_LIB_PREFIXES = (
    '/lib/', '/usr/lib/', '/lib64/', '/usr/lib64/',
    '/lib/x86_64-linux-gnu/', '/usr/lib/x86_64-linux-gnu/',
)


def get_system_prefixes() -> tuple[str, ...]:
    """返回系统库路径前缀——这些库由基础镜像提供，不需要捆绑"""
    return SYSTEM_LIB_PREFIXES


def get_direct_deps(so_path: Path) -> dict[str, Path]:
    """获取单个.so文件的直接非系统依赖"""
    try:
        result = subprocess.run(
            ['ldd', str(so_path)],
            capture_output=True, text=True, timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f'  Warning: ldd failed for {so_path}: {e}', file=sys.stderr)
        return {}

    deps: dict[str, Path] = {}
    for line in result.stdout.splitlines():
        m = re.match(r'\s*(\S+)\s*=>\s*(\S+)\s*\(0x[0-9a-fA-F]+\)', line)
        if not m:
            continue
        lib_name, lib_path = m.groups()
        real_path = Path(lib_path).resolve()
        if str(real_path).startswith(SYSTEM_LIB_PREFIXES):
            continue
        if real_path.exists() and real_path.is_file():
            deps[lib_name] = real_path
    return deps


def collect_all_deps(so_files: list[Path]) -> dict[str, Path]:
    """BFS递归收集所有非系统依赖（包含间接依赖）"""
    all_deps: dict[str, Path] = {}
    queue: deque[Path] = deque(so_files)
    visited: set[Path] = set()

    while queue:
        current = queue.popleft()
        real_current = current.resolve()
        if real_current in visited:
            continue
        visited.add(real_current)

        if not str(real_current).startswith('/'):
            continue

        direct = get_direct_deps(real_current)
        for name, path in direct.items():
            real_path = path.resolve()
            if name not in all_deps:
                all_deps[name] = real_path
                queue.append(real_path)

    return all_deps


def copy_deps_to_libs(all_deps: dict[str, Path], libs_dir: Path) -> list[Path]:
    """复制依赖库到_libs目录，处理符号链接"""
    libs_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []

    for lib_name, lib_path in all_deps.items():
        dest = libs_dir / lib_name
        real_path = lib_path.resolve()
        real_dest = libs_dir / real_path.name

        if not dest.exists():
            shutil.copy2(lib_path, dest)
            copied.append(dest)

        if real_path != lib_path and not real_dest.exists():
            shutil.copy2(real_path, real_dest)
            copied.append(real_dest)
        elif real_path != lib_path and real_dest.exists():
            copied.append(real_dest)

    return copied


def set_rpath_origin(so_files: list[Path]) -> None:
    """对所有.so文件设置RPATH=$ORIGIN"""
    for so in so_files:
        try:
            subprocess.run(
                ['patchelf', '--set-rpath', '$ORIGIN', str(so)],
                check=True, capture_output=True, timeout=10,
            )
        except subprocess.CalledProcessError as e:
            print(f'  Warning: patchelf failed for {so}: {e.stderr.decode()}',
                  file=sys.stderr)
        except FileNotFoundError:
            print('  Error: patchelf not found. Install with: apt install patchelf',
                  file=sys.stderr)
            sys.exit(1)


def sha256_file(filepath: Path) -> tuple[str, int]:
    """计算文件的sha256 hash（base64 url-safe编码）和大小"""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    digest = base64.urlsafe_b64encode(h.digest()).rstrip(b'=').decode()
    size = filepath.stat().st_size
    return f'sha256={digest}', size


def update_record(wheel_unpacked: Path, affected_paths: list[Path]) -> None:
    """更新wheel的RECORD文件"""
    dist_infos = list(wheel_unpacked.glob('*.dist-info'))
    if not dist_infos:
        print('  Warning: no .dist-info directory found, skipping RECORD update',
              file=sys.stderr)
        return

    record_path = dist_infos[0] / 'RECORD'
    if not record_path.exists():
        print(f'  Warning: RECORD not found at {record_path}', file=sys.stderr)
        return

    rows: list[list[str]] = []
    with open(record_path, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and len(row) >= 1:
                rows.append(row)

    for so_file in wheel_unpacked.rglob('*.so*'):
        rel_path = so_file.relative_to(wheel_unpacked).as_posix()
        hash_str, size = sha256_file(so_file)
        found = False
        for i, row in enumerate(rows):
            if row[0] == rel_path:
                rows[i] = [rel_path, hash_str, str(size)]
                found = True
                break
        if not found:
            rows.append([rel_path, hash_str, str(size)])

    record_rel = record_path.relative_to(wheel_unpacked).as_posix()
    for i, row in enumerate(rows):
        if row[0] == record_rel:
            rows[i] = [record_rel, '', '']
            break

    with open(record_path, 'w', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerows(rows)


def bundle_wheel_deps(
    wheel_unpacked: Path,
    libs_subdir: str = 'tvm/_libs',
) -> dict:
    """执行完整的wheel依赖捆绑流程"""
    libs_dir = wheel_unpacked / libs_subdir

    so_files = [f for f in wheel_unpacked.rglob('*.so') if f.is_file()]
    so_files += [f for f in wheel_unpacked.rglob('*.so.*') if f.is_file() and '.so' in f.name]
    print(f'Found {len(so_files)} .so files in wheel')

    all_deps = collect_all_deps(so_files)
    print(f'Found {len(all_deps)} non-system dependencies:')
    for name, path in sorted(all_deps.items()):
        print(f'  {name} -> {path}')

    copied = copy_deps_to_libs(all_deps, libs_dir)
    print(f'Copied {len(copied)} library files to {libs_dir}')

    all_sos = list(libs_dir.glob('*.so*')) + so_files
    set_rpath_origin(all_sos)
    print(f'Set RPATH=$ORIGIN for {len(all_sos)} .so files')

    all_affected = all_sos + copied
    update_record(wheel_unpacked, all_affected)
    print('Updated RECORD file with new hashes')

    return {
        'so_count': len(so_files),
        'dep_count': len(all_deps),
        'copied_count': len(copied),
        'libs_dir': str(libs_dir),
    }


def verify_bundle(wheel_unpacked: Path, libs_subdir: str = 'tvm/_libs') -> bool:
    """验证捆绑完整性：所有.so的ldd无not found"""
    libs_dir = wheel_unpacked / libs_subdir
    all_ok = True

    for so in wheel_unpacked.rglob('*.so*'):
        if not so.is_file():
            continue
        try:
            result = subprocess.run(
                ['ldd', str(so)],
                capture_output=True, text=True, timeout=10,
                env={**os.environ, 'LD_LIBRARY_PATH': f'{libs_dir}:{os.environ.get("LD_LIBRARY_PATH", "")}'},
            )
            missing = [l for l in result.stdout.splitlines() if 'not found' in l]
            if missing:
                print(f'FAIL: {so.name} has missing deps:')
                for m in missing:
                    print(f'  {m.strip()}')
                all_ok = False
        except Exception as e:
            print(f'Warning: could not check {so}: {e}')

    return all_ok


def main():
    parser = argparse.ArgumentParser(
        description='Bundle non-system shared library dependencies into a C-extension wheel'
    )
    parser.add_argument('wheel_dir', type=Path, help='Path to unpacked wheel directory')
    parser.add_argument('--libs-dir', default='tvm/_libs',
                        help='Subdirectory for bundled libraries (default: tvm/_libs)')
    parser.add_argument('--verify', action='store_true',
                        help='Verify bundle after completion (ldd check)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Only show what would be done, do not modify files')
    args = parser.parse_args()

    if not args.wheel_dir.is_dir():
        print(f'Error: {args.wheel_dir} is not a directory', file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        # Dry run: just show deps without modifying
        so_files = [f for f in args.wheel_dir.rglob('*.so') if f.is_file()]
        so_files += [f for f in args.wheel_dir.rglob('*.so.*') if f.is_file() and '.so' in f.name]
        print(f'=== DRY RUN ===')
        print(f'Found {len(so_files)} .so files')
        all_deps = collect_all_deps(so_files)
        print(f'Found {len(all_deps)} non-system dependencies:')
        for name, path in sorted(all_deps.items()):
            exists_in_libs = (args.wheel_dir / args.libs_dir / name).exists()
            status = "ALREADY BUNDLED" if exists_in_libs else "NEEDS BUNDLING"
            print(f'  {name} -> {path}  [{status}]')
        bundled_count = sum(1 for n in all_deps if (args.wheel_dir / args.libs_dir / n).exists())
        print(f'\nSummary: {bundled_count}/{len(all_deps)} already bundled, {len(all_deps) - bundled_count} need bundling')
        return

    stats = bundle_wheel_deps(args.wheel_dir, args.libs_dir)

    if args.verify:
        print('\nVerifying bundle...')
        ok = verify_bundle(args.wheel_dir, args.libs_dir)
        if ok:
            print('Verification PASSED: all shared library dependencies resolved')
        else:
            print('Verification FAILED: some dependencies are missing', file=sys.stderr)
            sys.exit(1)

    print(f'\nBundle complete: {stats["dep_count"]} deps, {stats["copied_count"]} files copied')


if __name__ == '__main__':
    main()
