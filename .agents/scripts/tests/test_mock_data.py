"""Mock 数据生成器单元测试。"""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mdi.models import Parameter
from mdi.mock_data import (
    generate_mock_value,
    generate_mock_values,
    generate_mock_body,
    generate_mock_query,
    generate_mock_path,
    generate_edge_value,
    _seed_for,
)


def make_param(name: str, type_: str = "string", required: bool = True,
               default: str | None = None, location: str = "body",
               description: str = "") -> Parameter:
    return Parameter(
        name=name, type=type_, required=required,
        default=default, location=location, description=description,
    )


class TestMockValueTypes:
    def test_string_default(self):
        p = make_param("title", "string")
        val = generate_mock_value(p)
        assert isinstance(val, str)
        assert len(val) > 0

    def test_integer_default(self):
        p = make_param("count", "integer")
        val = generate_mock_value(p)
        assert isinstance(val, int)

    def test_number_default(self):
        p = make_param("price", "number")
        val = generate_mock_value(p)
        assert isinstance(val, float)

    def test_boolean_default(self):
        p = make_param("enabled", "boolean")
        val = generate_mock_value(p)
        assert isinstance(val, bool)

    def test_array_type(self):
        p = make_param("tags", "array")
        val = generate_mock_value(p)
        assert val == []

    def test_object_type(self):
        p = make_param("metadata", "object")
        val = generate_mock_value(p)
        assert val == {}

    def test_null_type(self):
        p = make_param("extra", "null")
        val = generate_mock_value(p)
        assert val is None

    def test_empty_type_string(self):
        p = make_param("name", "")
        val = generate_mock_value(p)
        assert isinstance(val, str)


class TestMockValueSemantic:
    def test_email_field(self):
        p = make_param("email", "string")
        val = generate_mock_value(p)
        assert "@" in val
        assert "example.com" in val

    def test_user_id_field(self):
        p = make_param("user_id", "string")
        val = generate_mock_value(p)
        assert val.startswith("usr_")

    def test_generic_id_field(self):
        p = make_param("data_id", "string")
        val = generate_mock_value(p)
        assert val.startswith("data_")

    def test_phone_field(self):
        p = make_param("phone", "string")
        val = generate_mock_value(p)
        assert val.startswith("138") or val.isdigit()

    def test_url_field(self):
        p = make_param("avatar_url", "string")
        val = generate_mock_value(p)
        assert val.startswith("https://")

    def test_password_field(self):
        p = make_param("password", "string")
        val = generate_mock_value(p)
        assert len(val) >= 8

    def test_page_default(self):
        p = make_param("page", "integer")
        assert generate_mock_value(p) == 1

    def test_page_size_default(self):
        p = make_param("page_size", "integer")
        assert generate_mock_value(p) == 20

    def test_limit_default(self):
        p = make_param("limit", "integer")
        assert generate_mock_value(p) == 10

    def test_offset_default(self):
        p = make_param("offset", "integer")
        assert generate_mock_value(p) == 0

    def test_order_default(self):
        p = make_param("order", "string")
        assert generate_mock_value(p) == "desc"

    def test_format_default(self):
        p = make_param("format", "string")
        assert generate_mock_value(p) == "json"

    def test_age_semantic(self):
        p = make_param("age", "integer")
        val = generate_mock_value(p)
        assert 18 <= val <= 60

    def test_price_semantic(self):
        p = make_param("price", "number")
        val = generate_mock_value(p)
        assert val >= 0.99
        assert isinstance(val, float)

    def test_is_boolean_semantic(self):
        p = make_param("is_active", "boolean")
        assert generate_mock_value(p) is True


class TestDefaultValues:
    def test_boolean_default_true(self):
        p = make_param("verbose", "boolean", default="true")
        assert generate_mock_value(p) is True

    def test_boolean_default_false(self):
        p = make_param("dry_run", "boolean", default="false")
        assert generate_mock_value(p) is False

    def test_integer_default(self):
        p = make_param("limit", "integer", default="50")
        assert generate_mock_value(p) == 50

    def test_number_default(self):
        p = make_param("rate", "number", default="0.75")
        assert generate_mock_value(p) == pytest.approx(0.75)

    def test_string_default(self):
        p = make_param("format", "string", default="xml")
        assert generate_mock_value(p) == "xml"


class TestDeterminism:
    def test_same_input_same_output(self):
        p = make_param("email", "string")
        v1 = generate_mock_value(p)
        v2 = generate_mock_value(p)
        assert v1 == v2

    def test_different_params_different_values(self):
        p1 = make_param("name_a", "string")
        p2 = make_param("name_b", "string")
        assert generate_mock_value(p1) != generate_mock_value(p2)

    def test_seed_consistent(self):
        assert _seed_for("email") == _seed_for("email")
        assert _seed_for("email") != _seed_for("phone")


class TestEdgeValues:
    def test_empty_string(self):
        p = make_param("name", "string")
        assert generate_edge_value(p, "empty") == ""

    def test_empty_integer(self):
        p = make_param("count", "integer")
        assert generate_edge_value(p, "empty") == 0

    def test_empty_boolean(self):
        p = make_param("active", "boolean")
        assert generate_edge_value(p, "empty") is False

    def test_empty_array(self):
        p = make_param("items", "array")
        assert generate_edge_value(p, "empty") == []

    def test_negative_integer(self):
        p = make_param("age", "integer")
        assert generate_edge_value(p, "negative") == -1

    def test_negative_float(self):
        p = make_param("price", "number")
        val = generate_edge_value(p, "negative")
        assert val < 0

    def test_too_long_string(self):
        p = make_param("name", "string")
        val = generate_edge_value(p, "too_long")
        assert isinstance(val, str)
        assert len(val) == 1000

    def test_null_value(self):
        p = make_param("name", "string")
        assert generate_edge_value(p, "null") is None

    def test_invalid_type_for_int(self):
        p = make_param("count", "integer")
        val = generate_edge_value(p, "invalid_type")
        assert isinstance(val, str)

    def test_invalid_type_for_bool(self):
        p = make_param("active", "boolean")
        val = generate_edge_value(p, "invalid_type")
        assert isinstance(val, str)


class TestBatchGeneration:
    def test_generate_mock_values(self):
        params = [
            make_param("id", "string"),
            make_param("name", "string"),
            make_param("age", "integer"),
        ]
        result = generate_mock_values(params)
        assert isinstance(result, dict)
        assert set(result.keys()) == {"id", "name", "age"}
        assert isinstance(result["id"], str)
        assert isinstance(result["name"], str)
        assert isinstance(result["age"], int)

    def test_generate_mock_body_filters_location(self):
        params = [
            make_param("name", "string", location="body"),
            make_param("user_id", "string", location="path"),
            make_param("page", "integer", location="query"),
        ]
        result = generate_mock_body(params)
        assert "name" in result
        assert "user_id" not in result
        assert "page" not in result

    def test_generate_mock_query_filters_location(self):
        params = [
            make_param("name", "string", location="body"),
            make_param("page", "integer", location="query"),
            make_param("keyword", "string", location="query"),
        ]
        result = generate_mock_query(params)
        assert "page" in result
        assert "keyword" in result
        assert "name" not in result

    def test_generate_mock_path_filters_location(self):
        params = [
            make_param("name", "string", location="body"),
            make_param("user_id", "string", location="path"),
        ]
        result = generate_mock_path(params)
        assert "user_id" in result
        assert "name" not in result
