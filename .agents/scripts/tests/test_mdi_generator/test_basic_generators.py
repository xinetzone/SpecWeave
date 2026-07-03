import json
import pytest

from mdi.generators import (
    PythonGenerator,
    TypeScriptGenerator,
    OpenAPIGenerator,
    MCPGenerator,
    MarkdownGenerator,
    CLIGenerator,
)


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
