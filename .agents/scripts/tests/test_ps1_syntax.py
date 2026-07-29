#!/usr/bin/env python3
"""PS1 语法分析的 pytest 参数化测试。

使用 lib/ps1_test_cases.py 中定义的共享测试用例，
覆盖顶层插入点查找、括号深度计算、here-string 跳过原语等功能。
"""

import sys
from pathlib import Path

import pytest

# 版本校验
_lib_parent = Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310
enforce_python310()

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from lib.ps1_syntax import (
    find_top_level_insert_point,
    find_non_whitespace,
    skip_whitespace_and_comments,
    _calc_brace_depth,
    _skip_ps1_here_string,
    detect_ps_version_from_content,
    _resolve_target_version,
)
from lib.ps1_test_cases import (
    INSERT_POINT_CASES,
    BRACE_DEPTH_CASES,
    HERE_STRING_CASES,
    VERSION_DETECT_CASES,
)


# ── Insert Point Tests ──────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "case",
    INSERT_POINT_CASES,
    ids=[c.id for c in INSERT_POINT_CASES],
)
def test_find_top_level_insert_point(case):
    """测试顶层插入点查找函数。"""
    content = case.content
    search_from = case.search_from

    # 空文件特殊处理
    if not content:
        pos = 0
    else:
        pos = find_non_whitespace(content, search_from)
        pos = skip_whitespace_and_comments(content, pos)

    insert_pos = find_top_level_insert_point(content, pos)

    # 验证插入点位置合理性
    assert insert_pos >= case.expected_min_pos, (
        f"insert_pos={insert_pos} < expected_min_pos={case.expected_min_pos}"
    )
    assert insert_pos <= len(content), (
        f"insert_pos={insert_pos} > len(content)={len(content)}"
    )

    # 验证关键词
    if case.expected_keyword is not None and insert_pos < len(content):
        window_start = insert_pos
        window_end = min(insert_pos + 200, len(content))
        window = content[window_start:window_end]
        pre_window = content[max(0, insert_pos - 50):insert_pos]
        assert case.expected_keyword in window or case.expected_keyword in pre_window, (
            f"keyword '{case.expected_keyword}' not found near insert_pos={insert_pos}\n"
            f"window: {window[:100]!r}"
        )

    # 验证插入点处括号深度为0（非空文件且位置有效时）
    if insert_pos < len(content) and insert_pos > 0:
        pre = content[:insert_pos]
        depth = _calc_brace_depth(pre)
        assert depth == 0, f"brace_depth at insert_pos={insert_pos} is {depth}, expected 0"


# ── Brace Depth Tests ───────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "case",
    BRACE_DEPTH_CASES,
    ids=[c.id for c in BRACE_DEPTH_CASES],
)
def test_calc_brace_depth(case):
    """测试括号深度计算函数。"""
    content = case.content
    end_pos = case.end_pos if case.end_pos >= 0 else len(content)
    target = content[:end_pos]
    depth = _calc_brace_depth(target)
    assert depth == case.expected_depth, (
        f"brace_depth={depth}, expected {case.expected_depth}"
    )


# ── Here-String Skip Tests ──────────────────────────────────────────────────

@pytest.mark.parametrize(
    "case",
    HERE_STRING_CASES,
    ids=[c.id for c in HERE_STRING_CASES],
)
def test_skip_ps1_here_string(case):
    """测试 here-string 跳过原语。"""
    new_pos = _skip_ps1_here_string(case.content, case.position, target_version=case.target_version)
    assert new_pos == case.expected_new_pos, (
        f"new_pos={new_pos}, expected {case.expected_new_pos}\n"
        f"position={case.position}, content length={len(case.content)}"
    )


# ── 版本检测测试 ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("case", VERSION_DETECT_CASES, ids=lambda c: c.id)
def test_detect_ps_version(case):
    """测试从内容启发式检测 PowerShell 版本。"""
    result = detect_ps_version_from_content(case.content)
    assert result == case.expected_version, (
        f"[{case.id}] {case.name}: expected {case.expected_version}, got {result}"
    )


class TestTargetVersionModes:
    """target_version 参数模式测试。"""

    def test_resolve_auto_detects_7x(self):
        """auto 模式：含 ?? 运算符应检测为 7.x。"""
        content = "$x = $null; $y = $x ?? 5"
        assert _resolve_target_version(content, 'auto') == '7.x'

    def test_resolve_auto_detects_51(self):
        """auto 模式：#Requires -Version 5 应检测为 5.1。"""
        content = "#Requires -Version 5\nGet-Process"
        assert _resolve_target_version(content, 'auto') == '5.1'

    def test_resolve_explicit_51(self):
        """显式指定 5.1 应返回 5.1（即使内容有 7.x 特征）。"""
        content = "$x = $y ?? 1"
        assert _resolve_target_version(content, '5.1') == '5.1'

    def test_resolve_explicit_7x(self):
        """显式指定 7.x 应返回 7.x。"""
        content = "#Requires -Version 5\n"
        assert _resolve_target_version(content, '7.x') == '7.x'

    def test_target_version_51_here_string_cr(self):
        """5.1 模式下 CR-only 换行的 here-string 不应被识别。"""
        content = '@"\rline\r"@'
        pos_7x = _skip_ps1_here_string(content, 0, target_version='7.x')
        assert pos_7x == len(content)
        pos_51 = _skip_ps1_here_string(content, 0, target_version='5.1')
        assert pos_51 == 0

    def test_target_version_7x_here_string_cr(self):
        """7.x 模式下 CR-only 换行的 here-string 应被正确跳过。"""
        content = '@"\rhello\r"@'
        pos = _skip_ps1_here_string(content, 0, target_version='7.x')
        assert pos == len(content)

    def test_target_version_51_here_string_crlf(self):
        """5.1 模式下 CRLF 换行的 here-string 应被正确跳过。"""
        content = '@"\r\nhello\r\n"@'
        pos = _skip_ps1_here_string(content, 0, target_version='5.1')
        assert pos == len(content)
