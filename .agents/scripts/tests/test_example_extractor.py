"""example_extractor 单元测试。

覆盖：
- JSON响应示例提取
- JSON请求示例提取
- Python断言代码块提取
- curl命令解析
- HTTP原始格式解析
- 空输入/无效JSON处理
- 便捷函数(get_request_example/get_response_example/get_python_assertions)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mdi.models import CodeBlock, Interface, Parameter
from mdi.example_extractor import (
    ExtractedExample,
    extract_examples,
    get_request_example,
    get_response_example,
    get_python_assertions,
)


def _make_cb(language: str, content: str, purpose: str = "", meta: str = "") -> CodeBlock:
    return CodeBlock(language=language, meta=meta, content=content, purpose=purpose)


def _make_iface(
    method: str = "GET",
    path: str = "/users",
    examples: list[CodeBlock] | None = None,
) -> Interface:
    return Interface(
        name=path,
        method=method,
        path=path,
        parameters=[],
        responses=[],
        errors=[],
        examples=examples or [],
    )


class TestExtractExamples:
    def test_empty_examples_list(self):
        iface = _make_iface()
        result = extract_examples(iface)
        assert result == []

    def test_empty_code_block_content_skipped(self):
        iface = _make_iface(examples=[_make_cb("json", "")])
        result = extract_examples(iface)
        assert result == []

    def test_json_response_example(self):
        content = '{"id": 1, "name": "test"}'
        iface = _make_iface(examples=[_make_cb("json", content, purpose="example")])
        result = extract_examples(iface)
        assert len(result) == 1
        ex = result[0]
        assert ex.example_type == "response_body"
        assert ex.data == {"id": 1, "name": "test"}
        assert ex.language == "json"

    def test_json_request_example_by_purpose(self):
        content = '{"name": "Alice", "email": "a@b.com"}'
        iface = _make_iface(examples=[_make_cb("json", content, purpose="request")])
        result = extract_examples(iface)
        assert len(result) == 1
        assert result[0].example_type == "request_body"
        assert result[0].data == {"name": "Alice", "email": "a@b.com"}

    def test_json_request_example_by_meta_part(self):
        content = '{"q": "search"}'
        iface = _make_iface(examples=[_make_cb("json", content, purpose="example", meta="part=request")])
        result = extract_examples(iface)
        assert result[0].example_type == "request_body"

    def test_json_mock_purpose_treated_as_request(self):
        content = '{"name": "Bob"}'
        iface = _make_iface(examples=[_make_cb("json", content, purpose="mock")])
        result = extract_examples(iface)
        assert result[0].example_type == "request_body"

    def test_json_example_no_language_but_json_like(self):
        content = '{"ok": true}'
        iface = _make_iface(examples=[_make_cb("", content, purpose="response")])
        result = extract_examples(iface)
        assert len(result) == 1
        assert result[0].data == {"ok": True}

    def test_invalid_json_skipped(self):
        iface = _make_iface(examples=[_make_cb("json", "{not valid json}")])
        result = extract_examples(iface)
        assert result == []

    def test_json_array_example(self):
        content = '[{"id": 1}, {"id": 2}]'
        iface = _make_iface(examples=[_make_cb("json", content, purpose="example")])
        result = extract_examples(iface)
        assert result[0].example_type == "response_body"
        assert result[0].data == [{"id": 1}, {"id": 2}]

    def test_status_code_from_meta(self):
        content = '{"error": "not found"}'
        iface = _make_iface(examples=[_make_cb("json", content, purpose="example", meta="status=404")])
        result = extract_examples(iface)
        assert result[0].meta["status"] == "404"

    def test_python_assertion_block(self):
        content = "assert response.json()['id'] == 1\nassert response.json()['name'] == 'test'"
        iface = _make_iface(examples=[_make_cb("python", content, purpose="test")])
        result = extract_examples(iface)
        assert len(result) == 1
        assert result[0].example_type == "python_assertion"
        assert result[0].raw_content == content

    def test_python_block_no_purpose_still_recognized(self):
        content = "assert response.status_code == 200"
        iface = _make_iface(examples=[_make_cb("python", content)])
        result = extract_examples(iface)
        assert len(result) == 1
        assert result[0].example_type == "python_assertion"

    def test_py_alias_for_python(self):
        iface = _make_iface(examples=[_make_cb("py", "assert True")])
        result = extract_examples(iface)
        assert len(result) == 1
        assert result[0].language == "py"

    def test_curl_get_example(self):
        content = 'curl https://api.example.com/users'
        iface = _make_iface(examples=[_make_cb("bash", content)])
        result = extract_examples(iface)
        assert len(result) == 1
        assert result[0].example_type == "curl_request"
        assert result[0].data["method"] == "GET"
        assert result[0].data["url"] == "https://api.example.com/users"

    def test_curl_post_with_json_body(self):
        content = (
            'curl -X POST https://api.example.com/users '
            '-H "Content-Type: application/json" '
            '-H "Authorization: Bearer token123" '
            '-d \'{"name": "Alice"}\''
        )
        iface = _make_iface(examples=[_make_cb("curl", content)])
        result = extract_examples(iface)
        ex = result[0]
        assert ex.data["method"] == "POST"
        assert "Authorization" in ex.data["headers"]
        assert ex.data["body"] == {"name": "Alice"}

    def test_curl_put_method(self):
        content = 'curl -X PUT https://api.example.com/users/1 -d \'{"name": "Bob"}\''
        iface = _make_iface(examples=[_make_cb("shell", content)])
        result = extract_examples(iface)
        assert result[0].data["method"] == "PUT"

    def test_http_response_format(self):
        content = (
            "HTTP/1.1 200 OK\n"
            "Content-Type: application/json\n"
            "\n"
            '{"id": 1, "name": "test"}'
        )
        iface = _make_iface(examples=[_make_cb("http", content)])
        result = extract_examples(iface)
        assert len(result) == 1
        assert result[0].example_type == "response_body"
        assert result[0].meta["status"] == "200"
        assert result[0].data == {"id": 1, "name": "test"}

    def test_http_request_format(self):
        content = (
            "POST /users HTTP/1.1\n"
            "Content-Type: application/json\n"
            "\n"
            '{"name": "Alice"}'
        )
        iface = _make_iface(examples=[_make_cb("http", content)])
        result = extract_examples(iface)
        assert result[0].example_type == "request_body"
        assert result[0].data["method"] == "POST"
        assert result[0].data["body"] == {"name": "Alice"}

    def test_multiple_examples_preserved_in_order(self):
        cb1 = _make_cb("json", '{"id": 1}', purpose="response", meta="status=200")
        cb2 = _make_cb("python", "assert response.status_code == 200", purpose="test")
        cb3 = _make_cb("json", '{"error": "not found"}', purpose="response", meta="status=404")
        iface = _make_iface(examples=[cb1, cb2, cb3])
        result = extract_examples(iface)
        assert len(result) == 3
        assert result[0].meta["status"] == "200"
        assert result[1].example_type == "python_assertion"
        assert result[2].meta["status"] == "404"

    def test_unknown_language_not_extracted(self):
        iface = _make_iface(examples=[_make_cb("xml", "<root/>")])
        result = extract_examples(iface)
        assert result == []

    def test_schema_purpose(self):
        content = '{"type": "object", "properties": {"id": {"type": "integer"}}}'
        iface = _make_iface(examples=[_make_cb("json", content, purpose="schema")])
        result = extract_examples(iface)
        assert result[0].example_type == "schema"


class TestGetRequestExample:
    def test_returns_none_when_no_examples(self):
        iface = _make_iface()
        assert get_request_example(iface) is None

    def test_returns_request_body_dict(self):
        iface = _make_iface(examples=[_make_cb("json", '{"name": "A"}', purpose="request")])
        assert get_request_example(iface) == {"name": "A"}

    def test_ignores_response_examples(self):
        iface = _make_iface(examples=[_make_cb("json", '{"id": 1}', purpose="response")])
        assert get_request_example(iface) is None


class TestGetResponseExample:
    def test_returns_none_when_no_examples(self):
        iface = _make_iface()
        assert get_response_example(iface) is None

    def test_returns_first_success_response_by_default(self):
        cb200 = _make_cb("json", '{"id": 1}', purpose="example", meta="status=200")
        cb404 = _make_cb("json", '{"error": "x"}', purpose="example", meta="status=404")
        iface = _make_iface(examples=[cb200, cb404])
        assert get_response_example(iface) == {"id": 1}

    def test_filters_by_status_code(self):
        cb200 = _make_cb("json", '{"id": 1}', purpose="example", meta="status=200")
        cb404 = _make_cb("json", '{"error": "x"}', purpose="example", meta="status=404")
        iface = _make_iface(examples=[cb200, cb404])
        assert get_response_example(iface, status_code=404) == {"error": "x"}

    def test_returns_none_for_missing_status(self):
        cb200 = _make_cb("json", '{"id": 1}', purpose="example", meta="status=200")
        iface = _make_iface(examples=[cb200])
        assert get_response_example(iface, status_code=500) is None


class TestGetPythonAssertions:
    def test_returns_empty_list_when_none(self):
        iface = _make_iface()
        assert get_python_assertions(iface) == []

    def test_returns_all_python_snippets(self):
        cb1 = _make_cb("python", "assert response.status_code == 200", purpose="test")
        cb2 = _make_cb("python", "assert 'id' in response.json()", purpose="test")
        cb3 = _make_cb("json", '{"id": 1}', purpose="example")
        iface = _make_iface(examples=[cb1, cb2, cb3])
        result = get_python_assertions(iface)
        assert len(result) == 2
        assert "assert response.status_code == 200" in result[0]
        assert "assert 'id' in response.json()" in result[1]


class TestMetaParsing:
    def test_meta_string_parsed_to_dict(self):
        cb = _make_cb("json", '{"a":1}', meta="status=201 part=response")
        iface = _make_iface(examples=[cb])
        result = extract_examples(iface)
        assert result[0].meta["status"] == "201"
        assert result[0].meta["part"] == "response"

    def test_empty_meta(self):
        cb = _make_cb("json", '{"a":1}')
        iface = _make_iface(examples=[cb])
        result = extract_examples(iface)
        assert result[0].meta.get("status") == "200"
