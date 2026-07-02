"""checklist_converter 单元测试。

覆盖：
- 检查项分类（前置/断言/后置/注释）
- 状态码断言生成
- 字段存在断言生成
- 字段值断言生成
- 边界情况（空文本、非断言文本）
- get_checklist_assertions/get_checklist_setup 便捷函数
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mdi.checklist_converter import (
    ChecklistStep,
    convert_check_items,
    get_checklist_assertions,
    get_checklist_setup,
)
from mdi.models import CheckItem, Interface, Parameter


def _make_iface(check_texts: list[tuple[str, bool]]) -> Interface:
    items = [CheckItem(text=t, checked=c, line=i + 1) for i, (t, c) in enumerate(check_texts)]
    return Interface(
        name="test",
        method="GET",
        path="/test",
        summary="test",
        check_items=items,
    )


class TestClassification:
    def test_empty_text_returns_none(self):
        from mdi.checklist_converter import _convert_single
        assert _convert_single(CheckItem(text="", checked=False, line=1)) is None

    def test_pre_condition_keywords(self):
        iface = _make_iface([
            ("前置条件：用户已登录", True),
            ("准备测试数据", False),
            ("before each test setup", False),
        ])
        steps = convert_check_items(iface)
        pre_steps = [s for s in steps if s.step_type == "pre"]
        assert len(pre_steps) == 3

    def test_assert_keywords_chinese(self):
        iface = _make_iface([
            ("验证响应状态码为200", False),
            ("确认返回字段包含id", False),
            ("检查响应不为空", False),
        ])
        steps = convert_check_items(iface)
        assert_steps = [s for s in steps if s.step_type == "assert"]
        assert len(assert_steps) == 3

    def test_assert_keywords_english(self):
        iface = _make_iface([
            ("assert response contains id field", False),
            ("expect status code 200", False),
            ("should return valid json", False),
        ])
        steps = convert_check_items(iface)
        assert_steps = [s for s in steps if s.step_type == "assert"]
        assert len(assert_steps) == 3

    def test_post_condition_keywords(self):
        iface = _make_iface([
            ("后置清理测试数据", False),
            ("teardown after test", False),
        ])
        steps = convert_check_items(iface)
        post_steps = [s for s in steps if s.step_type == "post"]
        assert len(post_steps) == 2

    def test_note_for_non_actionable_text(self):
        iface = _make_iface([
            ("接口说明详见文档", False),
        ])
        steps = convert_check_items(iface)
        note_steps = [s for s in steps if s.step_type == "note"]
        assert len(note_steps) == 1
        assert note_steps[0].code_lines[0].startswith("# 检查项:")


class TestStatusCodeAssertions:
    def test_chinese_status_code(self):
        iface = _make_iface([("验证状态码为200", False)])
        asserts = get_checklist_assertions(iface)
        assert any("response.status_code == 200" in line for line in asserts)

    def test_english_status_code(self):
        iface = _make_iface([("expect status code 201", False)])
        asserts = get_checklist_assertions(iface)
        assert any("response.status_code == 201" in line for line in asserts)

    def test_status_code_400(self):
        iface = _make_iface([("检查返回状态码400", False)])
        asserts = get_checklist_assertions(iface)
        assert any("response.status_code == 400" in line for line in asserts)


class TestFieldAssertions:
    def test_field_exists_chinese(self):
        iface = _make_iface([("响应包含字段`id`", False)])
        asserts = get_checklist_assertions(iface)
        assert any("'id' in data" in line for line in asserts)

    def test_field_exists_english(self):
        iface = _make_iface([("response contains field 'name'", False)])
        asserts = get_checklist_assertions(iface)
        assert any("'name' in data" in line for line in asserts)

    def test_field_value_equals_string(self):
        iface = _make_iface([("`status`字段为'success'", False)])
        asserts = get_checklist_assertions(iface)
        assert any("data['status'] == 'success'" in line for line in asserts)

    def test_field_value_equals_number(self):
        iface = _make_iface([("`code`字段等于0", False)])
        asserts = get_checklist_assertions(iface)
        assert any("data['code'] == 0" in line for line in asserts)

    def test_field_value_equals_boolean(self):
        iface = _make_iface([("`success`字段为true", False)])
        asserts = get_checklist_assertions(iface)
        assert any("data['success'] == True" in line or "data['success'] is True" in line for line in asserts)


class TestConvenienceFunctions:
    def test_get_checklist_assertions_filters_only_asserts(self):
        iface = _make_iface([
            ("前置条件：登录", True),
            ("验证状态码为200", False),
            ("后置清理", False),
        ])
        asserts = get_checklist_assertions(iface)
        assert len(asserts) > 0
        for line in asserts:
            assert "前置" not in line or "前置条件:" in line
            assert not line.startswith("# TODO: 后置")

    def test_get_checklist_setup_returns_pre(self):
        iface = _make_iface([
            ("前置：准备数据", False),
            ("验证状态码为200", False),
        ])
        setup = get_checklist_setup(iface)
        assert len(setup) > 0

    def test_empty_checklist_returns_empty(self):
        iface = Interface(name="empty", method="GET", path="/empty", summary="empty")
        assert get_checklist_assertions(iface) == []
        assert get_checklist_setup(iface) == []
        assert convert_check_items(iface) == []


class TestStepOrder:
    def test_ordering_pre_then_assert_then_post_then_note(self):
        iface = _make_iface([
            ("清理资源", False),
            ("验证状态码为200", False),
            ("准备数据", False),
            ("备注说明", False),
        ])
        steps = convert_check_items(iface)
        types = [s.step_type for s in steps]
        assert types == ["pre", "assert", "post", "note"]


class TestCheckedFlag:
    def test_pre_checked_flag_preserved(self):
        iface = _make_iface([("验证状态码为200", True)])
        steps = convert_check_items(iface)
        assert steps[0].is_pre_checked is True

    def test_unchecked_flag(self):
        iface = _make_iface([("验证状态码为200", False)])
        steps = convert_check_items(iface)
        assert steps[0].is_pre_checked is False
