#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sitecustomize.py 自动加载验证脚本。

检测 sitecustomize.py 是否在新终端会话中被 Python `site` 模块自动加载，
确保 UTF-8 编码环境在 Python 启动时即生效（无需业务脚本手动 setup）。

检测项:
  1. sys.path / PYTHONPATH 是否包含 .agents/scripts/
  2. sitecustomize 是否已被 site 模块自动加载（sys.modules 检测）
  3. sitecustomize.__file__ 是否指向 .agents/scripts/sitecustomize.py
  4. sys.stdout/sys.stderr 编码是否为 utf-8（_reconfigure_std_streams 副作用）
  5. 项目根目录是否存在冲突的 sitecustomize.py

退出码:
  0 = 自动加载正常
  1 = 需配置（sys.path 未含 .agents/scripts/，sitecustomize 不会被自动加载）
  2 = 存在冲突文件（根目录存在 sitecustomize.py）

用法:
  python verify-sitecustomize-autoload.py           # 人类可读报告
  python verify-sitecustomize-autoload.py --json    # JSON 输出（供 CI 集成）

注意:
  本脚本会在导入 lib.cli 之前捕获 Python 启动状态快照
  （sys.path、stdout/stderr 编码、sys.modules['sitecustomize']），
  以避免 lib.cli.setup_safe_output() 修改 stdout 编码后影响检测结果。
  sitecustomize 由 Python 的 site 模块在解释器启动时（本脚本代码执行之前）
  尝试加载，因此 sys.modules['sitecustomize'] 反映了 site 模块的加载结果。
"""

import argparse
import json
import os
import sys
from pathlib import Path

# ============================================================================
# 启动状态快照
# 必须在任何可能修改 stdout/stderr/sys.path/sys.modules 的导入之前捕获。
# ============================================================================

# 捕获初始 stdout/stderr 编码（sitecustomize._reconfigure_std_streams 的副作用）
_INITIAL_STDOUT_ENCODING = getattr(sys.stdout, 'encoding', None)
_INITIAL_STDERR_ENCODING = getattr(sys.stderr, 'encoding', None)

# 捕获 sitecustomize 是否已被 site 模块自动加载
_INITIAL_SITECUSTOMIZE_MODULE = sys.modules.get('sitecustomize')
_INITIAL_SITECUSTOMIZE_AUTO_LOADED = _INITIAL_SITECUSTOMIZE_MODULE is not None
_INITIAL_SITECUSTOMIZE_FILE = (
    getattr(_INITIAL_SITECUSTOMIZE_MODULE, '__file__', None)
    if _INITIAL_SITECUSTOMIZE_MODULE is not None
    else None
)

# 捕获初始 sys.path（Python 自动将脚本所在目录插入 sys.path[0]，
# 因此该快照已包含 .agents/scripts/；真正反映 site 加载时机的是 PYTHONPATH
# 环境变量与 sys.modules['sitecustomize'] 的状态）
_INITIAL_SYS_PATH = list(sys.path)


# ============================================================================
# 路径定位
# ============================================================================

# 脚本位于 .agents/scripts/ 下；SCRIPTS_DIR 为脚本所在目录
SCRIPTS_DIR = Path(__file__).resolve().parent
# 项目根目录：从 SCRIPTS_DIR 上溯两级（.agents/scripts/ → .agents/ → 项目根）
PROJECT_ROOT = SCRIPTS_DIR.parent.parent
# 期望被自动加载的 sitecustomize.py 完整路径
EXPECTED_SITECUSTOMIZE = SCRIPTS_DIR / "sitecustomize.py"

# 将 SCRIPTS_DIR 加入 sys.path 以便导入 lib 模块
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import (  # noqa: E402
    add_common_args,
    print_pass,
    print_warn,
    print_error,
    print_header,
    print_summary,
    setup_safe_output,
)


# ============================================================================
# 退出码常量
# ============================================================================

EXIT_OK = 0              # 自动加载正常
EXIT_NEEDS_CONFIG = 1    # 需配置
EXIT_CONFLICT = 2        # 存在冲突文件


# ============================================================================
# 工具函数
# ============================================================================

def _is_utf8(encoding):
    """判断给定编码名称是否为 UTF-8 系列（含 utf-8、utf8-sig、cp65001）。"""
    if not isinstance(encoding, str):
        return False
    normalized = encoding.lower().replace('-', '').replace('_', '')
    return normalized in ('utf8', 'utf8sig', 'cp65001')


def _paths_equal(path_a, path_b):
    """判断两个路径是否指向同一文件系统位置（resolve 后比较）。"""
    try:
        return Path(path_a).resolve() == Path(path_b).resolve()
    except (OSError, ValueError):
        return Path(path_a) == Path(path_b)


# ============================================================================
# 检测函数
# ============================================================================

def check_sys_path():
    """检测 sys.path 与 PYTHONPATH 是否包含 .agents/scripts/。

    使用初始 sys.path 快照，避免本脚本 import lib 时插入的路径干扰。
    PYTHONPATH 检查是持久化配置的关键标志：只有 PYTHONPATH 含该目录，
    新终端会话的 site 模块才能在启动时自动加载 sitecustomize.py。
    """
    in_initial_sys_path = any(
        _paths_equal(p, SCRIPTS_DIR) for p in _INITIAL_SYS_PATH if p
    )
    in_current_sys_path = any(
        _paths_equal(p, SCRIPTS_DIR) for p in sys.path if p
    )
    pythonpath = os.environ.get('PYTHONPATH', '')
    pythonpath_entries = [p for p in pythonpath.split(os.pathsep) if p]
    in_pythonpath = any(
        _paths_equal(p, SCRIPTS_DIR) for p in pythonpath_entries
    )
    return {
        'in_initial_sys_path': in_initial_sys_path,
        'in_current_sys_path': in_current_sys_path,
        'in_pythonpath': in_pythonpath,
        'scripts_dir': str(SCRIPTS_DIR),
        'pythonpath': pythonpath,
    }


def check_sitecustomize_loaded():
    """检测 sitecustomize 是否已被 site 模块自动加载。

    使用启动快照中的 sys.modules 状态，避免后续 import 干扰。
    若未被自动加载，则尝试手动 import 以验证可访问性。
    """
    if _INITIAL_SITECUSTOMIZE_AUTO_LOADED:
        return {
            'auto_loaded': True,
            'file': _INITIAL_SITECUSTOMIZE_FILE,
            'source': 'sys.modules (site 模块启动时自动加载)',
            'manual_import_attempted': False,
            'manual_import_succeeded': None,
        }

    # 未被自动加载，尝试手动 import 验证可访问性
    manual_succeeded = False
    manual_file = None
    try:
        import sitecustomize  # noqa: F401
        manual_succeeded = True
        manual_file = getattr(sitecustomize, '__file__', None)
    except ImportError:
        manual_succeeded = False

    return {
        'auto_loaded': False,
        'file': manual_file,
        'source': (
            '手动 import 成功（但未被 site 自动加载，PYTHONPATH 可能未持久化）'
            if manual_succeeded
            else 'import 失败（sitecustomize.py 不在 sys.path，无法被加载）'
        ),
        'manual_import_attempted': True,
        'manual_import_succeeded': manual_succeeded,
    }


def check_file_path(loaded_info):
    """检测 sitecustomize.__file__ 是否指向 .agents/scripts/sitecustomize.py。"""
    file_path = loaded_info.get('file')
    if not file_path:
        return {
            'match': False,
            'actual': None,
            'expected': str(EXPECTED_SITECUSTOMIZE),
            'reason': 'sitecustomize 未被加载，无法获取 __file__',
        }
    match = _paths_equal(file_path, EXPECTED_SITECUSTOMIZE)
    return {
        'match': match,
        'actual': str(file_path),
        'expected': str(EXPECTED_SITECUSTOMIZE),
        'reason': '路径匹配' if match else '路径不匹配（可能加载到其他 sitecustomize.py）',
    }


def check_encoding():
    """检测 stdout/stderr 编码是否为 utf-8（sitecustomize 副作用）。

    使用启动快照中的编码值，避免 setup_safe_output() 干扰。
    """
    return {
        'stdout_encoding': _INITIAL_STDOUT_ENCODING,
        'stderr_encoding': _INITIAL_STDERR_ENCODING,
        'stdout_utf8': _is_utf8(_INITIAL_STDOUT_ENCODING),
        'stderr_utf8': _is_utf8(_INITIAL_STDERR_ENCODING),
    }


def check_root_conflict():
    """检测项目根目录是否存在冲突的 sitecustomize.py。

    根目录的 sitecustomize.py 会被 Python 优先加载（若根目录在 sys.path），
    导致 .agents/scripts/sitecustomize.py 被遮蔽，需告警提示删除。
    """
    conflict_path = PROJECT_ROOT / 'sitecustomize.py'
    exists = conflict_path.exists()
    return {
        'exists': exists,
        'path': str(conflict_path),
    }


# ============================================================================
# 结果汇总与退出码判定
# ============================================================================

def run_checks():
    """运行全部检测项，返回结果字典。"""
    sys_path_info = check_sys_path()
    loaded_info = check_sitecustomize_loaded()
    file_info = check_file_path(loaded_info)
    enc_info = check_encoding()
    conflict_info = check_root_conflict()

    return {
        'project_root': str(PROJECT_ROOT),
        'scripts_dir': str(SCRIPTS_DIR),
        'expected_sitecustomize': str(EXPECTED_SITECUSTOMIZE),
        'sys_path': sys_path_info,
        'sitecustomize': loaded_info,
        'file_match': file_info,
        'encoding': enc_info,
        'root_conflict': conflict_info,
    }


def determine_exit_code(results):
    """根据检测结果决定退出码。

    优先级:
      - 根目录冲突 -> 2 (EXIT_CONFLICT)
      - 自动加载未生效 -> 1 (EXIT_NEEDS_CONFIG)
      - 全部通过 -> 0 (EXIT_OK)

    自动加载正常的充分判定:
      1. sitecustomize 已被 site 模块自动加载（auto_loaded=True）
      2. __file__ 路径匹配 EXPECTED_SITECUSTOMIZE
      3. stdout 与 stderr 编码均为 utf-8

    注: sys.path 含 .agents/scripts/ 是必要但不充分条件
        （Python 自动加入脚本目录到 sys.path，但 site 模块加载时机更早，
         真正的持久化标志是 PYTHONPATH 与 auto_loaded 状态）
    """
    if results['root_conflict']['exists']:
        return EXIT_CONFLICT

    loaded = results['sitecustomize']
    file_match = results['file_match']['match']
    enc = results['encoding']

    if (
        loaded['auto_loaded']
        and file_match
        and enc['stdout_utf8']
        and enc['stderr_utf8']
    ):
        return EXIT_OK

    return EXIT_NEEDS_CONFIG


# ============================================================================
# 报告输出
# ============================================================================

def print_report(results):
    """以人类可读格式打印检测报告。"""
    print_header("sitecustomize.py 自动加载验证")
    print(f"  项目根目录:          {results['project_root']}")
    print(f"  .agents/scripts/:    {results['scripts_dir']}")
    print(f"  期望 sitecustomize:  {results['expected_sitecustomize']}")
    print()

    # ── 检测 1/4: sys.path / PYTHONPATH ─────────────────────────
    sp = results['sys_path']
    print("[检测 1/4] sys.path / PYTHONPATH 包含 .agents/scripts/")
    if sp['in_initial_sys_path']:
        print_pass(".agents/scripts/ 在初始 sys.path 中")
    else:
        print_error(".agents/scripts/ 不在初始 sys.path 中")
    if sp['in_pythonpath']:
        print_pass(".agents/scripts/ 已在 PYTHONPATH 环境变量中（持久化配置生效）")
    else:
        print_warn(".agents/scripts/ 不在 PYTHONPATH 中（新终端会话将无法自动加载）")
    print()

    # ── 检测 2/4: sitecustomize 自动加载 ─────────────────────────
    loaded = results['sitecustomize']
    print("[检测 2/4] sitecustomize 被 site 模块自动加载")
    if loaded['auto_loaded']:
        print_pass("sitecustomize 已被 site 模块自动加载")
    elif loaded['manual_import_succeeded']:
        print_warn("sitecustomize 未被自动加载，但可手动 import")
        print_warn("       （PYTHONPATH 可能未持久化，新终端会话无法自动加载）")
    else:
        print_error("sitecustomize 未被自动加载，且无法 import")
    print(f"    来源: {loaded['source']}")
    print()

    # ── 检测 3/4: __file__ 路径匹配 ─────────────────────────────
    fm = results['file_match']
    print("[检测 3/4] sitecustomize.__file__ 路径匹配")
    if fm['match']:
        print_pass(f"路径匹配: {fm['actual']}")
    else:
        print_error("路径不匹配")
        print(f"    期望: {fm['expected']}")
        print(f"    实际: {fm['actual']}")
        print(f"    原因: {fm['reason']}")
    print()

    # ── 检测 4/4: 编码副作用 ────────────────────────────────────
    enc = results['encoding']
    print("[检测 4/4] stdout/stderr 编码为 utf-8（_reconfigure_std_streams 副作用）")
    if enc['stdout_utf8']:
        print_pass(f"sys.stdout.encoding = {enc['stdout_encoding']}")
    else:
        print_error(f"sys.stdout.encoding = {enc['stdout_encoding']} (期望 utf-8)")
    if enc['stderr_utf8']:
        print_pass(f"sys.stderr.encoding = {enc['stderr_encoding']}")
    else:
        print_error(f"sys.stderr.encoding = {enc['stderr_encoding']} (期望 utf-8)")
    print()

    # ── 根目录冲突告警 ──────────────────────────────────────────
    conflict = results['root_conflict']
    if conflict['exists']:
        print_warn(f"[冲突] 项目根目录存在 sitecustomize.py: {conflict['path']}")
        print_warn("       根目录副本可能与 .agents/scripts/sitecustomize.py 冲突")
        print_warn("       建议: 删除根目录副本，统一使用 .agents/scripts/sitecustomize.py")
        print()

    # ── 总结 ────────────────────────────────────────────────────
    exit_code = determine_exit_code(results)
    if exit_code == EXIT_OK:
        print_pass("自动加载正常: sitecustomize.py 在 Python 启动时被正确自动加载")
    elif exit_code == EXIT_CONFLICT:
        print_warn("存在冲突文件: 项目根目录存在 sitecustomize.py，需删除后重新验证")
    else:
        print_error("需配置: sitecustomize.py 不会被自动加载")
        print()
        print("  解决方案（任选其一）:")
        print("    1. 运行配置脚本: .\\.agents\\scripts\\setup-utf8-env.ps1")
        print("    2. 在 PowerShell 中加载 profile: .\\.agents\\scripts\\profile.ps1")
        print("    3. 手动将 .agents/scripts/ 加入 PYTHONPATH 环境变量")
        print()
        print("  配置完成后新开终端会话，重新运行本脚本验证。")
    print()

    # ── 检查摘要 ────────────────────────────────────────────────
    pass_count = sum([
        sp['in_initial_sys_path'],
        loaded['auto_loaded'],
        fm['match'],
        enc['stdout_utf8'],
        enc['stderr_utf8'],
    ])
    warn_count = 1 if conflict['exists'] else 0
    error_count = 5 - pass_count
    print_summary(pass_count=pass_count, warn_count=warn_count, error_count=error_count)


def print_json_report(results):
    """以 JSON 格式输出检测结果（供 CI 集成）。"""
    exit_code = determine_exit_code(results)
    exit_meaning = {
        0: '自动加载正常',
        1: '需配置',
        2: '存在冲突文件',
    }
    output = {
        'ok': exit_code == EXIT_OK,
        'exit_code': exit_code,
        'exit_code_meaning': exit_meaning.get(exit_code, '未知'),
        'project_root': results['project_root'],
        'scripts_dir': results['scripts_dir'],
        'expected_sitecustomize': results['expected_sitecustomize'],
        'checks': {
            'sys_path': {
                'pass': results['sys_path']['in_initial_sys_path'],
                'detail': results['sys_path'],
            },
            'autoload': {
                'pass': results['sitecustomize']['auto_loaded'],
                'detail': results['sitecustomize'],
            },
            'file_path': {
                'pass': results['file_match']['match'],
                'detail': results['file_match'],
            },
            'encoding': {
                'pass': (
                    results['encoding']['stdout_utf8']
                    and results['encoding']['stderr_utf8']
                ),
                'detail': results['encoding'],
            },
            'root_conflict': {
                'pass': not results['root_conflict']['exists'],
                'detail': results['root_conflict'],
            },
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


# ============================================================================
# CLI 入口
# ============================================================================

def build_parser():
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        description='sitecustomize.py 自动加载验证脚本',
    )
    add_common_args(parser)
    return parser


def main():
    # setup_safe_output 配置 stdout/stderr 为 UTF-8，防止 GBK 终端输出中文崩溃
    # 注意: 此时初始编码已通过模块级快照捕获，不受 setup_safe_output 影响
    setup_safe_output()

    parser = build_parser()
    args = parser.parse_args()

    results = run_checks()
    exit_code = determine_exit_code(results)

    if args.json:
        print_json_report(results)
    else:
        print_report(results)

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
