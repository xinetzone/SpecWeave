"""检查清单→测试步骤转换器。

将MDI文档中的检查清单项（- [ ] / - [x]）转换为可嵌入测试函数的
前置条件、后置断言和验证步骤。

转换策略：
- 包含"前置"/"准备"/"before"/"setup"/"given"关键词 → 前置条件（fixture/setup）
- 包含"验证"/"确认"/"断言"/"assert"/"expect"/"should"/"返回"/"状态码" → 断言
- 包含"后置"/"清理"/"teardown"/"after" → 后置清理
- 其他 → 注释说明（不生成代码，仅添加#注释）

中文关键词优先，其次英文。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from mdi.models import CheckItem, Interface


@dataclass
class ChecklistStep:
    """转换后的测试步骤。"""

    step_type: str
    description: str
    code_lines: list[str] = field(default_factory=list)
    is_pre_checked: bool = False


_PRE_KEYWORDS = ("前置", "准备", "before", "setup", "given", "前提", "登录", "认证")
_ASSERT_KEYWORDS = (
    "验证", "确认", "断言", "检查", "assert", "expect", "should",
    "返回", "状态码", "包含", "字段", "响应", "status", "json",
    "返回值", "不为空", "大于", "小于", "等于", "是", "为",
    "contain", "include", "has", "have", "field", "property", "return", "response",
)
_POST_KEYWORDS = ("后置", "清理", "teardown", "after", "cleanup")


_STATUS_CODE_RE = re.compile(r"(?:状态码|status\s*code)[^\d]*?(\d{3})", re.IGNORECASE)
_FIELD_EXISTS_RE = re.compile(
    r"(?:包含|存在|has|contain|contains|include|有|have)[^，。；]*?(?:字段|field|key|属性|property)[^，。；]*?[`'\"]?([a-zA-Z_][a-zA-Z0-9_]*)[`'\"]?",
    re.IGNORECASE,
)
_FIELD_VALUE_RE = re.compile(
    r"[`'\"]?([a-zA-Z_][a-zA-Z0-9_]*)[`'\"]?\s*(?:字段|field)?\s*(?:等于|为|是|=|==)\s*[`'\"]?([^`'\"，。；]+)[`'\"]?",
)


def convert_check_items(iface: Interface) -> list[ChecklistStep]:
    """将接口关联的所有check_items转换为测试步骤列表。

    Args:
        iface: 接口定义对象。

    Returns:
        有序的ChecklistStep列表，pre→assert→post顺序。
    """
    steps: list[ChecklistStep] = []
    for ci in iface.check_items:
        step = _convert_single(ci)
        if step is not None:
            steps.append(step)

    pre_steps = [s for s in steps if s.step_type == "pre"]
    assert_steps = [s for s in steps if s.step_type == "assert"]
    post_steps = [s for s in steps if s.step_type == "post"]
    note_steps = [s for s in steps if s.step_type == "note"]
    return pre_steps + assert_steps + post_steps + note_steps


def get_checklist_assertions(iface: Interface) -> list[str]:
    """获取checklist转换后的断言代码行（供pytest_gen直接嵌入）。

    只返回 assert 类型步骤的code_lines。
    """
    lines: list[str] = []
    for step in convert_check_items(iface):
        if step.step_type == "assert":
            lines.extend(step.code_lines)
    return lines


def get_checklist_setup(iface: Interface) -> list[str]:
    """获取checklist转换后的前置条件代码行。"""
    lines: list[str] = []
    for step in convert_check_items(iface):
        if step.step_type == "pre":
            lines.extend(step.code_lines)
    return lines


def _convert_single(ci: CheckItem) -> ChecklistStep | None:
    text = ci.text.strip()
    if not text:
        return None

    lower_text = text.lower()
    step_type = _classify(text, lower_text)
    code_lines = _generate_code(text, lower_text, step_type)

    return ChecklistStep(
        step_type=step_type,
        description=text,
        code_lines=code_lines,
        is_pre_checked=ci.checked,
    )


def _classify(text: str, lower_text: str) -> str:
    for kw in _PRE_KEYWORDS:
        if kw in lower_text or kw in text:
            return "pre"
    for kw in _POST_KEYWORDS:
        if kw in lower_text or kw in text:
            return "post"
    for kw in _ASSERT_KEYWORDS:
        if kw in lower_text or kw in text:
            return "assert"
    return "note"


def _generate_code(text: str, lower_text: str, step_type: str) -> list[str]:
    if step_type == "note":
        return [f"# 检查项: {text}"]

    if step_type == "pre":
        return [f"# 前置条件: {text}", f"# TODO: {text}"]

    if step_type == "post":
        return [f"# 后置清理: {text}", f"# TODO: {text}"]

    return _generate_assertion_code(text, lower_text)


def _generate_assertion_code(text: str, lower_text: str) -> list[str]:
    lines: list[str] = []

    sc_match = _STATUS_CODE_RE.search(text)
    if sc_match:
        code = sc_match.group(1)
        lines.append(f"# 验证状态码为{code}（来自检查项）")
        lines.append(f"assert response.status_code == {code}")

    field_matches = _FIELD_EXISTS_RE.findall(text)
    for field_name in field_matches:
        lines.append(f"# 验证字段'{field_name}'存在")
        lines.append(f"assert {repr(field_name)} in data")

    fv_matches = _FIELD_VALUE_RE.findall(text)
    for field_name, expected_value in fv_matches:
        val = expected_value.strip()
        if field_name in ("status_code",):
            continue
        if not val or len(val) > 50:
            continue
        py_val = _to_python_literal(val)
        if py_val is not None:
            lines.append(f"# 验证字段'{field_name}'等于{val}")
            lines.append(f"assert data[{repr(field_name)}] == {py_val}")
        else:
            lines.append(f"# 验证字段'{field_name}'包含'{val}'")
            lines.append(f"assert {repr(val)} in str(data[{repr(field_name)}])")

    if not lines:
        lines.append(f"# 断言: {text}")
        lines.append(f"# TODO: 实现断言逻辑: {text}")

    return lines


def _to_python_literal(val: str) -> str | None:
    v = val.strip().strip('`"\'')
    if v.lower() in ("true", "是", "yes"):
        return "True"
    if v.lower() in ("false", "否", "no"):
        return "False"
    if v.lower() in ("null", "none", "空"):
        return "None"
    try:
        int(v)
        return v
    except ValueError:
        pass
    try:
        float(v)
        return v
    except ValueError:
        pass
    return repr(v)
