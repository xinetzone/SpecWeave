# 模式2：C扩展Wheel依赖捆绑（Wheel-Dep-Bundling）

> **核心原则**：conda环境下编译的C扩展wheel必须捆绑非系统共享库依赖，通过RPATH=$ORIGIN实现自包含。
>
> **问题本质**：`libtvm.so`通过DT_NEEDED记录了对libLLVM、libicu、libxml2等conda库的依赖，干净环境中这些路径不存在。
>
> **源洞察**：184MB wheel中有11个捆绑共享库（libLLVM-22 186MB、libicu 32MB等），手动ldd→复制→patchelf→RECORD更新流程实现自包含

---

## 片段A：bundle_wheel_deps.py — 独立依赖捆绑脚本

将此脚本放在项目中，在wheel unpack后、repack前执行：

```python
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
    """获取单个.so文件的直接非系统依赖

    使用 ldd 分析ELF动态链接依赖，过滤掉系统库（glibc/libm/libpthread等）。
    返回 {库名: 真实路径} 字典。
    """
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
        # 匹配格式: libfoo.so.1 => /path/to/libfoo.so.1 (0x...)
        # 也处理静态链接/无依赖的行（linux-vdso等）
        m = re.match(r'\s*(\S+)\s*=>\s*(\S+)\s*\(0x[0-9a-fA-F]+\)', line)
        if not m:
            continue
        lib_name, lib_path = m.groups()
        real_path = Path(lib_path).resolve()
        # 跳过系统库
        if str(real_path).startswith(SYSTEM_LIB_PREFIXES):
            continue
        if real_path.exists() and real_path.is_file():
            deps[lib_name] = real_path
    return deps


def collect_all_deps(so_files: list[Path]) -> dict[str, Path]:
    """BFS递归收集所有非系统依赖（包含间接依赖）

    遍历依赖图，避免重复和循环引用。返回 {库名: 真实路径} 字典。
    """
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
    """复制依赖库到_libs目录，处理符号链接

    返回所有复制/已存在的库文件路径列表。
    """
    libs_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []

    for lib_name, lib_path in all_deps.items():
        dest = libs_dir / lib_name
        real_path = lib_path.resolve()
        real_dest = libs_dir / real_path.name

        # 复制主文件（可能是符号链接）
        if not dest.exists():
            shutil.copy2(lib_path, dest)
            copied.append(dest)

        # 复制真实文件（符号链接指向的实际文件）
        if real_path != lib_path and not real_dest.exists():
            shutil.copy2(real_path, real_dest)
            copied.append(real_dest)
        elif real_path != lib_path and real_dest.exists():
            copied.append(real_dest)

        # 如果dest已经是符号链接或不同文件，也确保real_dest存在
        if not dest.exists() and real_dest.exists():
            pass  # real_dest已存在即可

    return copied


def set_rpath_origin(so_files: list[Path]) -> None:
    """对所有.so文件设置RPATH=$ORIGIN

    $ORIGIN是ELF动态链接器的特殊变量，指向.so文件自身所在目录。
    设置后，动态链接器会优先在.so同级目录查找依赖。
    """
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
    """计算文件的sha256 hash（base64 url-safe编码，匹配wheel RECORD格式）和大小"""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    digest = base64.urlsafe_b64encode(h.digest()).rstrip(b'=').decode()
    size = filepath.stat().st_size
    return f'sha256={digest}', size


def update_record(wheel_unpacked: Path, affected_paths: list[Path]) -> None:
    """更新wheel的RECORD文件

    patchelf修改.so后，文件内容变化导致sha256 hash不匹配，pip install会报hash mismatch。
    此函数重新计算所有受影响文件的hash和大小，更新RECORD。

    RECORD格式（CSV）：
        path/to/file,sha256=<base64hash>,<size>
    """
    dist_infos = list(wheel_unpacked.glob('*.dist-info'))
    if not dist_infos:
        print('  Warning: no .dist-info directory found, skipping RECORD update',
              file=sys.stderr)
        return

    record_path = dist_infos[0] / 'RECORD'
    if not record_path.exists():
        print(f'  Warning: RECORD not found at {record_path}', file=sys.stderr)
        return

    # 读取现有RECORD
    rows: list[list[str]] = []
    existing_paths: set[str] = set()
    with open(record_path, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and len(row) >= 1:
                rows.append(row)
                existing_paths.add(row[0])

    # 更新/添加受影响文件的hash
    affected_rel_paths = {p.relative_to(wheel_unpacked).as_posix() for p in affected_paths}
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

    # RECORD文件自身不记录hash（pip会特殊处理）
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
    """执行完整的wheel依赖捆绑流程

    Args:
        wheel_unpacked: 解压后的wheel目录路径
        libs_subdir: 库存放的相对路径（相对于wheel_unpacked）

    Returns:
        统计信息字典
    """
    libs_dir = wheel_unpacked / libs_subdir

    # 步骤1：找到wheel中所有.so文件
    so_files = [f for f in wheel_unpacked.rglob('*.so') if f.is_file()]
    so_files += [f for f in wheel_unpacked.rglob('*.so.*') if f.is_file() and '.so' in f.name]
    print(f'Found {len(so_files)} .so files in wheel')

    # 步骤2：递归收集依赖
    all_deps = collect_all_deps(so_files)
    print(f'Found {len(all_deps)} non-system dependencies:')
    for name, path in sorted(all_deps.items()):
        print(f'  {name} -> {path}')

    # 步骤3：复制依赖到_libs目录
    copied = copy_deps_to_libs(all_deps, libs_dir)
    print(f'Copied {len(copied)} library files to {libs_dir}')

    # 步骤4：patchelf设置RPATH=$ORIGIN
    all_sos = list(libs_dir.glob('*.so*')) + so_files
    set_rpath_origin(all_sos)
    print(f'Set RPATH=$ORIGIN for {len(all_sos)} .so files')

    # 步骤5：更新RECORD
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
    args = parser.parse_args()

    if not args.wheel_dir.is_dir():
        print(f'Error: {args.wheel_dir} is not a directory', file=sys.stderr)
        sys.exit(1)

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
```

### 使用方式

```bash
# 1. 解压wheel
mkdir -p /tmp/wheel_unpacked
cd /tmp/wheel_unpacked
unzip /path/to/xmnn-1.2.2a0-cp314-cp314-linux_x86_64.whl

# 2. 执行依赖捆绑（自动递归→复制→patchelf→RECORD更新）
python bundle_wheel_deps.py . --libs-dir tvm/_libs --verify

# 3. 重新打包wheel
cd /tmp/wheel_unpacked
zip -r /path/to/xmnn-1.2.2a0-cp314-cp314-linux_x86_64.whl .

# 4. 在干净镜像中验证
docker run --rm -v /path/to/wheel.whl:/w.whl python:3.14-slim \
    bash -c "pip install /w.whl && python -c 'import tvm; print(\"OK\")'"
```

---

## 片段B：CMakeLists.txt 集成（scikit-build-core）

```cmake
# 在CMake install阶段后自动调用依赖捆绑
# 将此片段添加到项目的CMakeLists.txt中

find_program(PATCHELF_EXECUTABLE patchelf)
if(NOT PATCHELF_EXECUTABLE)
    message(FATAL_ERROR "patchelf is required for wheel dependency bundling")
endif()

# 安装后处理：依赖捆绑
install(CODE "
    execute_process(
        COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/cmake/bundle_wheel_deps.py
                \${CMAKE_INSTALL_PREFIX}/{{PY_PACKAGE_DIR}}
                --libs-dir {{LIB_DIR}}/_libs
                --verify
        RESULT_VARIABLE BUNDLE_RESULT
    )
    if(NOT BUNDLE_RESULT EQUAL 0)
        message(FATAL_ERROR \"Wheel dependency bundling failed\")
    endif()
")
```

---

## 片段C：shell版本快速捆绑脚本（无Python依赖场景）

```bash
#!/bin/bash
# bundle_wheel_deps.sh — Shell版本快速依赖捆绑
# 适用于不便使用Python脚本的Docker构建场景
set -euo pipefail

WHEEL_DIR="${1:-.}"
LIBS_DIR="${WHEEL_DIR}/tvm/_libs"
SYSTEM_PREFIXES="/lib/ /usr/lib/ /lib64/ /usr/lib64/ /lib/x86_64-linux-gnu/ /usr/lib/x86_64-linux-gnu/"

mkdir -p "$LIBS_DIR"

is_system_lib() {
    local path="$1"
    for prefix in $SYSTEM_PREFIXES; do
        if [[ "$path" == "$prefix"* ]]; then return 0; fi
    done
    return 1
}

echo "Bundling dependencies from $WHEEL_DIR ..."

# 找到所有.so文件并递归复制依赖
find "$WHEEL_DIR" -name "*.so*" -type f | while read -r so; do
    ldd "$so" 2>/dev/null | grep -oP '\S+ => \S+' | while read -r line; do
        lib_path="${line#*=> }"
        if [ -f "$lib_path" ] && ! is_system_lib "$lib_path"; then
            real_path=$(realpath "$lib_path" 2>/dev/null || echo "$lib_path")
            lib_name=$(basename "$lib_path")
            real_name=$(basename "$real_path")
            cp -n "$lib_path" "$LIBS_DIR/" 2>/dev/null || true
            [ "$real_path" != "$lib_path" ] && cp -n "$real_path" "$LIBS_DIR/" 2>/dev/null || true
        fi
    done
done

# patchelf所有.so
find "$WHEEL_DIR" -name "*.so*" -type f -exec patchelf --set-rpath '$ORIGIN' {} \;

echo "Bundling complete. Libraries in $LIBS_DIR:"
ls -lh "$LIBS_DIR/" 2>/dev/null || echo "  (none)"
```

---

## 反模式速查（Do NOT）

| ❌ 反模式 | ✅ 正确做法 |
|-----------|-----------|
| 只捆绑顶层.so的直接依赖 | BFS递归收集所有间接依赖 |
| patchelf后不更新RECORD | patchelf后必须重新计算sha256更新RECORD |
| RPATH设置为绝对路径（`/opt/xmnn/libs`） | 永远使用`$ORIGIN`（相对路径） |
| 捆绑系统库（libc.so.6等） | 只捆绑conda/pip安装的非系统第三方库 |
| 在构建环境验证通过就发布 | 必须在`python:slim`全新容器中验证 |
| 内联Python到shell heredoc中处理复杂逻辑 | 使用独立.py文件，避免转义地狱 |
| `wheel pack`重新打包（可能改变RECORD格式） | 使用zipfile/zip -r直接操作zip |
