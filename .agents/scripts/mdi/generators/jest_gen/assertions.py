"""Jest断言生成器 - JavaScript expect断言转换。
STATUS: UNVERIFIED - 未经实战验证，参考pytest_gen/mdi.parser使用
"""

from __future__ import annotations

import ast
import logging
import re
from collections.abc import Callable

logger = logging.getLogger(__name__)


def js_response_assertions(
    indent: str,
    expected: object,
    actual_expr: str,
    js_repr_func: Callable[[object], str],
    depth: int = 0,
) -> list[str]:
    """从响应示例数据生成JavaScript expect断言。"""
    lines: list[str] = []
    if depth >= 3:
        logger.debug(
            "[jest-gen] js_response_assertions depth=%d expr=%s: 到达最大递归深度，仅toBeDefined",
            depth, actual_expr,
        )
        lines.append(f"{indent}expect({actual_expr}).toBeDefined();")
        return lines
    if isinstance(expected, dict):
        logger.debug(
            "[jest-gen] js_response_assertions depth=%d expr=%s type=dict keys=%s",
            depth, actual_expr, list(expected.keys()),
        )
        lines.append(f"{indent}expect(typeof {actual_expr}).toBe('object');")
        lines.append(f"{indent}expect({actual_expr}).not.toBeNull();")
        for key, val in expected.items():
            key_js = js_repr_func(key)
            child_expr = f"{actual_expr}[{key_js}]"
            lines.append(f"{indent}expect({child_expr}).toBeDefined();")
            if isinstance(val, (dict, list)) and val:
                lines.extend(js_response_assertions(indent, val, child_expr, js_repr_func, depth + 1))
            elif not isinstance(val, (dict, list)):
                lines.append(f"{indent}expect({child_expr}).toEqual({js_repr_func(val)});")
    elif isinstance(expected, list):
        logger.debug(
            "[jest-gen] js_response_assertions depth=%d expr=%s type=list len=%d",
            depth, actual_expr, len(expected),
        )
        lines.append(f"{indent}expect(Array.isArray({actual_expr})).toBe(true);")
        if expected:
            lines.extend(js_response_assertions(indent, expected[0], f"{actual_expr}[0]", js_repr_func, depth + 1))
    else:
        logger.debug(
            "[jest-gen] js_response_assertions depth=%d expr=%s type=%s value=%r",
            depth, actual_expr, type(expected).__name__, expected,
        )
        lines.append(f"{indent}expect({actual_expr}).toEqual({js_repr_func(expected)});")
    return lines


def py_to_js_assertions(
    indent: str,
    py_lines: list[str],
    js_repr_func: Callable[[object], str],
) -> list[str]:
    """将checklist_converter生成的Python断言行转换为JavaScript expect断言。

    转换规则：
    - assert response.status_code == N → expect(response.status).toBe(N)
    - assert 'key' in data → expect(data).toHaveProperty('key')
    - assert data['key'] == val → expect(data['key']).toEqual(val)
    - 注释行(#)保留为JS注释(//)
    - TODO注释转换为Jest test.todo风格注释
    """
    lines: list[str] = []
    converted = 0
    failed = 0
    comment_count = 0

    status_re = re.compile(r"assert\s+response\.status_code\s*==\s*(\d+)")
    in_re = re.compile(r"assert\s+(.+?)\s+in\s+(data|response)")
    eq_re = re.compile(r"assert\s+data\[(.+?)\]\s*==\s*(.+)")
    contains_re = re.compile(r"assert\s+(.+?)\s+in\s+str\(data\[(.+?)\]\)")

    for raw in py_lines:
        line = raw.strip()
        if line.startswith("#"):
            comment_count += 1
            lines.append(f"{indent}// {line[1:].strip()}")
            continue
        m = status_re.match(line)
        if m:
            lines.append(f"{indent}expect(response.status).toBe({m.group(1)});")
            converted += 1
            continue
        m = in_re.match(line)
        if m:
            key = m.group(1).strip()
            try:
                key_literal = ast.literal_eval(key)
                lines.append(f"{indent}expect({m.group(2)}).toHaveProperty({js_repr_func(key_literal)});")
                converted += 1
                continue
            except Exception as e:
                logger.debug(
                    "[jest-gen] py_to_js_assertions in_re解析失败: key=%r, error=%s",
                    key, e,
                )
        m = eq_re.match(line)
        if m:
            key_expr = m.group(1).strip()
            val_expr = m.group(2).strip()
            try:
                key_literal = ast.literal_eval(key_expr)
                val_literal = ast.literal_eval(val_expr)
                lines.append(f"{indent}expect(data[{js_repr_func(key_literal)}]).toEqual({js_repr_func(val_literal)});")
                converted += 1
                continue
            except Exception as e:
                logger.debug(
                    "[jest-gen] py_to_js_assertions eq_re解析失败: key=%r, val=%r, error=%s",
                    key_expr, val_expr, e,
                )
        m = contains_re.match(line)
        if m:
            needle = m.group(1).strip()
            hay_key = m.group(2).strip()
            try:
                needle_lit = ast.literal_eval(needle)
                key_lit = ast.literal_eval(hay_key)
                lines.append(
                    f"{indent}expect(String(data[{js_repr_func(key_lit)}])).toContain({js_repr_func(needle_lit)});"
                )
                converted += 1
                continue
            except Exception as e:
                logger.debug(
                    "[jest-gen] py_to_js_assertions contains_re解析失败: needle=%r, key=%r, error=%s",
                    needle, hay_key, e,
                )
        failed += 1
        logger.warning(
            "[jest-gen] py_to_js_assertions 无法自动转换 (标记为注释): %r",
            line,
        )
        lines.append(f"{indent}// [自动转换失败] {line}")

    logger.debug(
        "[jest-gen] py_to_js_assertions 转换汇总: 成功=%d, 失败=%d, 注释=%d, 总计=%d",
        converted, failed, comment_count, len(py_lines),
    )
    return lines
