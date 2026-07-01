"""MDI Generator单元测试。

覆盖Python/TypeScript/OpenAPI/MCP/Markdown/CLI代码生成、MDIGenerator门面类等场景。
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

from mdi.parser import MDIParser
from mdi.models import MDIDocument, Interface, Parameter, Response
from mdi.generator import MDIGenerator
from mdi.generators import (
    PythonGenerator,
    TypeScriptGenerator,
    OpenAPIGenerator,
    MCPGenerator,
    MarkdownGenerator,
    CLIGenerator,
    PytestGenerator,
)
from mdi.generators.utils import (
    snake_to_pascal,
    snake_to_camel,
    map_python_type,
    map_typescript_type,
    map_json_schema_type,
    make_interface_name,
    sanitize_identifier,
)

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SCRIPTS_DIR.parent.parent


@pytest.fixture
def parser():
    return MDIParser()


@pytest.fixture
def sample_webapi_doc():
    text = '''---
name: test-api
version: 1.0.0
description: A test web API
baseUrl: https://api.example.com/v1
---

# Test API

This is a test API document.

### `GET /users` Get Users

Get a list of users.

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | Page number |
| limit | integer | 否 | Items per page |
| status | string | 否 | Filter by status |

| 状态码 | 描述 |
|--------|------|
| 200 | Successful response |
| 400 | Bad request |

### `POST /users` Create User

Create a new user.

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| name | string | 是 | User name |
| email | string | 是 | User email |
| age | integer | 否 | User age |

| 状态码 | 描述 |
|--------|------|
| 201 | User created |
| 400 | Invalid input |
'''
    p = MDIParser(profile_type="webapi")
    return p.parse_text(text)


@pytest.fixture
def sample_skill_doc():
    skill_path = PROJECT_ROOT / ".agents/skills/link-check-cmd/SKILL.md"
    if skill_path.exists():
        p = MDIParser()
        return p.parse_file(skill_path)
    return MDIDocument(
        frontmatter={"name": "test-skill", "description": "A test skill"},
        title="Test Skill",
        description="Test skill description",
    )


class TestUtils:

    def test_snake_to_pascal(self):
        assert snake_to_pascal("user_id") == "UserId"
        assert snake_to_pascal("create_user") == "CreateUser"
        assert snake_to_pascal("hello_world_test") == "HelloWorldTest"
        assert snake_to_pascal("") == ""

    def test_snake_to_camel(self):
        assert snake_to_camel("user_id") == "userId"
        assert snake_to_camel("create_user") == "createUser"

    def test_map_python_type(self):
        assert map_python_type("string") == "str"
        assert map_python_type("integer") == "int"
        assert map_python_type("number") == "float"
        assert map_python_type("boolean") == "bool"
        assert map_python_type("array") == "list"
        assert map_python_type("object") == "dict"
        assert "Optional" in map_python_type("optional string")

    def test_map_typescript_type(self):
        assert map_typescript_type("string") == "string"
        assert map_typescript_type("integer") == "number"
        assert map_typescript_type("boolean") == "boolean"
        assert "undefined" in map_typescript_type("optional string")

    def test_map_json_schema_type(self):
        assert map_json_schema_type("string")["type"] == "string"
        assert map_json_schema_type("integer")["type"] == "integer"
        assert map_json_schema_type("boolean")["type"] == "boolean"
        assert map_json_schema_type("array")["type"] == "array"

    def test_sanitize_identifier(self):
        assert sanitize_identifier("user-id") == "user_id"
        assert sanitize_identifier("123abc").startswith("_")

    def test_make_interface_name(self):
        assert make_interface_name("get_users") == "GetUsers"
        assert make_interface_name("create-user") == "CreateUser"


class TestPythonGenerator:

    def test_python_generate_compiles(self, sample_webapi_doc, tmp_path):
        gen = PythonGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) > 0
        for f in files:
            assert f.exists()
            content = f.read_text(encoding="utf-8")
            if f.suffix == ".py":
                try:
                    compile(content, str(f), "exec")
                except SyntaxError as e:
                    pytest.fail(f"Python syntax error in {f}: {e}")

    def test_python_contains_typed_dict(self, sample_webapi_doc, tmp_path):
        gen = PythonGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        py_files = [f for f in files if f.suffix == ".py"]
        assert len(py_files) > 0
        all_content = ""
        for f in py_files:
            all_content += f.read_text(encoding="utf-8")
        assert "TypedDict" in all_content
        assert "class" in all_content


class TestTypeScriptGenerator:

    def test_typescript_generate_structure(self, sample_webapi_doc, tmp_path):
        gen = TypeScriptGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) > 0
        ts_file = files[0]
        assert ts_file.suffix == ".ts"
        content = ts_file.read_text(encoding="utf-8")
        assert "interface" in content
        assert "export" in content


class TestOpenAPIGenerator:

    def test_openapi_required_fields(self, sample_webapi_doc, tmp_path):
        gen = OpenAPIGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) == 1
        json_file = files[0]
        assert json_file.suffix == ".json"
        content = json_file.read_text(encoding="utf-8")
        spec = json.loads(content)
        assert "openapi" in spec
        assert "info" in spec
        assert "paths" in spec
        assert spec["openapi"].startswith("3.0")
        assert "title" in spec["info"]
        assert "/users" in spec["paths"]

    def test_openapi_paths_have_methods(self, sample_webapi_doc, tmp_path):
        gen = OpenAPIGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        spec = json.loads(files[0].read_text(encoding="utf-8"))
        users_path = spec["paths"]["/users"]
        assert "get" in users_path
        assert "post" in users_path


class TestMCPGenerator:

    def test_mcp_tool_structure(self, sample_webapi_doc, tmp_path):
        gen = MCPGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) == 1
        content = files[0].read_text(encoding="utf-8")
        tools = json.loads(content)
        assert isinstance(tools, list)
        assert len(tools) > 0
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            schema = tool["inputSchema"]
            assert schema["type"] == "object"
            assert "properties" in schema

    def test_mcp_tool_has_required(self, sample_webapi_doc, tmp_path):
        gen = MCPGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        tools = json.loads(files[0].read_text(encoding="utf-8"))
        create_tool = [t for t in tools if "create" in t["name"].lower() or "post" in t.get("description", "").lower()]
        if create_tool:
            schema = create_tool[0]["inputSchema"]
            assert "required" in schema
            assert "name" in schema["required"]


class TestMarkdownGenerator:

    def test_markdown_generate(self, sample_webapi_doc, tmp_path):
        gen = MarkdownGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) == 1
        md_file = files[0]
        assert md_file.suffix == ".md"
        content = md_file.read_text(encoding="utf-8")
        assert content.startswith("---")
        assert "# " in content
        assert "| 参数名" in content or "| 参数" in content


class TestCLIGenerator:

    def test_cli_generate_compiles(self, sample_webapi_doc, tmp_path):
        gen = CLIGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) > 0
        for f in files:
            if f.suffix == ".py":
                content = f.read_text(encoding="utf-8")
                try:
                    compile(content, str(f), "exec")
                except SyntaxError as e:
                    pytest.fail(f"Python syntax error in CLI file {f}: {e}")

    def test_cli_imports_click(self, sample_webapi_doc, tmp_path):
        gen = CLIGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        cli_py = [f for f in files if f.name == "cli.py"]
        assert len(cli_py) > 0
        content = cli_py[0].read_text(encoding="utf-8")
        assert "import click" in content
        assert "@click.group" in content or "@click.command" in content


class TestPytestGenerator:

    def test_pytest_generate_compiles(self, sample_webapi_doc, tmp_path):
        gen = PytestGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) > 0
        for f in files:
            if f.suffix == ".py":
                content = f.read_text(encoding="utf-8")
                try:
                    compile(content, str(f), "exec")
                except SyntaxError as e:
                    pytest.fail(f"Python syntax error in generated test {f}: {e}")

    def test_pytest_contains_test_classes(self, sample_webapi_doc, tmp_path):
        gen = PytestGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        test_files = [f for f in files if f.name.startswith("test_") and f.suffix == ".py"]
        assert len(test_files) >= 1
        content = test_files[0].read_text(encoding="utf-8")
        assert "import pytest" in content
        assert "import requests" in content
        assert "class Test" in content
        assert "def test_" in content
        assert "api_client" in content
        assert "base_url" in content

    def test_pytest_generates_conftest(self, sample_webapi_doc, tmp_path):
        gen = PytestGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        conftest = [f for f in files if f.name == "conftest.py"]
        assert len(conftest) == 1
        content = conftest[0].read_text(encoding="utf-8")
        assert "@pytest.fixture" in content
        assert "api_client" in content
        assert "base_url" in content

    def test_pytest_conftest_not_overwritten(self, sample_webapi_doc, tmp_path):
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text("# existing conftest", encoding="utf-8")
        gen = PytestGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert conftest_path.read_text(encoding="utf-8") == "# existing conftest"

    def test_pytest_success_test_asserts_status(self, sample_webapi_doc, tmp_path):
        gen = PytestGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        test_files = [f for f in files if f.name.startswith("test_")]
        content = test_files[0].read_text(encoding="utf-8")
        assert "assert response.status_code ==" in content

    def test_pytest_error_tests_for_error_codes(self, tmp_path):
        text = '''---
name: test-api
version: 1.0.0
description: Test
baseUrl: https://api.example.com
type: webapi
---

# Test

```{endpoint} POST /items
:summary: Create item
:param name: string - 名称
:response 201: Created
:error 400: VALIDATION_ERROR - 参数校验失败
:error 409: ALREADY_EXISTS - 资源已存在
```
'''
        doc = MDIParser(profile_type="webapi").parse_text(text)
        gen = PytestGenerator()
        files = gen.generate(doc, tmp_path)
        test_files = [f for f in files if f.name.startswith("test_")]
        content = test_files[0].read_text(encoding="utf-8")
        assert "VALIDATION_ERROR" not in content or "400" in content
        assert "ALREADY_EXISTS" in content
        assert "response.status_code == 409" in content


class TestMDIGeneratorFacade:

    def test_supported_languages(self):
        langs = MDIGenerator.supported_languages()
        assert "python" in langs
        assert "typescript" in langs
        assert "openapi" in langs
        assert "mcp" in langs
        assert "markdown" in langs
        assert "cli" in langs
        assert "pytest" in langs

    def test_invalid_language_raises(self):
        with pytest.raises(ValueError):
            MDIGenerator(lang="invalid_lang")

    def test_generate_python_from_doc(self, sample_webapi_doc, tmp_path):
        gen = MDIGenerator(lang="python")
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) > 0
        assert any(f.suffix == ".py" for f in files)

    def test_generate_typescript(self, sample_webapi_doc, tmp_path):
        gen = MDIGenerator(lang="typescript")
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) > 0
        assert any(f.suffix == ".ts" for f in files)

    def test_generate_openapi(self, sample_webapi_doc, tmp_path):
        gen = MDIGenerator(lang="openapi")
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) == 1
        spec = json.loads(files[0].read_text(encoding="utf-8"))
        assert "openapi" in spec

    def test_generate_mcp(self, sample_webapi_doc, tmp_path):
        gen = MDIGenerator(lang="mcp")
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) == 1
        tools = json.loads(files[0].read_text(encoding="utf-8"))
        assert isinstance(tools, list)

    def test_generate_markdown(self, sample_webapi_doc, tmp_path):
        gen = MDIGenerator(lang="markdown")
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) == 1
        assert files[0].suffix == ".md"

    def test_generate_cli(self, sample_webapi_doc, tmp_path):
        gen = MDIGenerator(lang="cli")
        files = gen.generate(sample_webapi_doc, tmp_path)
        cli_py = [f for f in files if f.name == "cli.py"]
        assert len(cli_py) > 0

    def test_generate_pytest(self, sample_webapi_doc, tmp_path):
        gen = MDIGenerator(lang="pytest")
        files = gen.generate(sample_webapi_doc, tmp_path)
        test_py = [f for f in files if f.name.startswith("test_") and f.suffix == ".py"]
        assert len(test_py) >= 1
        conftest = [f for f in files if f.name == "conftest.py"]
        assert len(conftest) == 1

    def test_generate_file(self, tmp_path):
        skill_path = PROJECT_ROOT / ".agents/skills/link-check-cmd/SKILL.md"
        if skill_path.exists():
            out_dir = tmp_path / "out"
            gen = MDIGenerator(lang="python")
            files = gen.generate_file(skill_path, out_dir)
            assert len(files) > 0
