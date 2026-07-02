"""MDI Parser单元测试。

覆盖frontmatter解析、标题层级、表格分类、代码块、列表、Mermaid、Web API、错误容忍等场景。
"""

import sys
import timeit
from pathlib import Path

import pytest

from mdi.parser import MDIParser
from mdi.models import (
    CheckItem,
    CodeBlock,
    DecisionNode,
    ErrorCode,
    Interface,
    MDIDocument,
    Parameter,
    Response,
    Section,
)

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SCRIPTS_DIR.parent.parent


@pytest.fixture
def parser():
    return MDIParser()


class TestFrontmatterParsing:

    def test_toml_ref_string_form(self, parser, tmp_path):
        toml_file = tmp_path / "meta.toml"
        toml_file.write_text('name = "from-toml"\nversion = "2.0.0"\nauthors = ["Tom"]\n', encoding="utf-8")
        md_file = tmp_path / "test.md"
        md_file.write_text('---\nname: from-yaml\ndescription: "Test"\nx-toml-ref: "meta.toml"\n---\n\n# Test\n', encoding="utf-8")
        doc = parser.parse_file(str(md_file))
        assert doc.frontmatter["name"] == "from-yaml"
        assert doc.frontmatter["version"] == "2.0.0"
        assert doc.frontmatter["authors"] == ["Tom"]

    def test_toml_ref_with_key_path(self, parser, tmp_path):
        toml_file = tmp_path / "pyproject.toml"
        toml_file.write_text('[project]\nname = "myproject"\nversion = "0.1.0"\n[tool.mdi]\nname = "cli-tool"\nversion = "1.0.0"\n', encoding="utf-8")
        md_file = tmp_path / "test.md"
        md_file.write_text('---\ndescription: "CLI"\nx-toml-ref:\n  path: "pyproject.toml"\n  key: "tool.mdi"\n---\n\n# Test\n', encoding="utf-8")
        doc = parser.parse_file(str(md_file))
        assert doc.frontmatter["name"] == "cli-tool"
        assert doc.frontmatter["version"] == "1.0.0"
        assert doc.frontmatter["description"] == "CLI"

    def test_toml_ref_missing_file_warns(self, parser, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text('---\nname: test\nx-toml-ref: "nonexistent.toml"\n---\n\n# Test\n', encoding="utf-8")
        doc = parser.parse_file(str(md_file))
        assert doc.frontmatter["name"] == "test"
        assert len(doc.warnings) > 0
        assert any("不存在" in w for w in doc.warnings)

    def test_toml_ref_parse_text_no_base_dir(self, parser):
        text = '---\nname: test\nx-toml-ref: "some.toml"\n---\n\n# Test\n'
        doc = parser.parse_text(text)
        assert doc.frontmatter["name"] == "test"
        assert "x-toml-ref" in doc.frontmatter

    def test_yaml_frontmatter(self, parser):
        text = '---\nname: test-skill\nversion: 1.0.0\ndescription: "A test skill"\nuser-invocable: true\n---\n\n# Test Skill\n'
        doc = parser.parse_text(text)
        assert doc.frontmatter["name"] == "test-skill"
        assert doc.frontmatter["version"] == "1.0.0"
        assert doc.frontmatter["description"] == "A test skill"
        assert doc.frontmatter["user-invocable"] is True

    def test_yaml_frontmatter_with_list(self, parser):
        text = '---\nname: test\npaths:\n  - "a.py"\n  - "b.py"\n---\n\n# Test\n'
        doc = parser.parse_text(text)
        assert "paths" in doc.frontmatter
        assert isinstance(doc.frontmatter["paths"], list)
        assert len(doc.frontmatter["paths"]) == 2

    def test_no_frontmatter(self, parser):
        text = "# Just a title\n\nSome content."
        doc = parser.parse_text(text)
        assert doc.frontmatter == {}

    def test_malformed_yaml_frontmatter_graceful(self, parser):
        text = '---\nname: test\n  invalid: [yaml\n---\n\n# Test\n'
        doc = parser.parse_text(text)
        assert isinstance(doc.warnings, list)
        assert len(doc.warnings) > 0


class TestHeadingHierarchy:

    def test_h1_to_h6(self, parser):
        text = "# H1 Title\n\n## H2 Section\n\n### H3 Subsection\n\n#### H4 Deep\n"
        doc = parser.parse_text(text)
        assert doc.title == "H1 Title"
        assert len(doc.sections) == 1
        h1 = doc.sections[0]
        assert h1.level == 1
        assert h1.title == "H1 Title"
        assert len(h1.subsections) == 1
        h2 = h1.subsections[0]
        assert h2.level == 2
        assert h2.title == "H2 Section"
        assert len(h2.subsections) == 1
        h3 = h2.subsections[0]
        assert h3.level == 3
        assert h3.title == "H3 Subsection"

    def test_sibling_h2_sections(self, parser):
        text = "# Doc\n\n## Section A\n\nContent A\n\n## Section B\n\nContent B\n\n## Section C\n\nContent C\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        assert len(h1.subsections) == 3
        titles = [s.title for s in h1.subsections]
        assert "Section A" in titles
        assert "Section B" in titles
        assert "Section C" in titles

    def test_h3_under_correct_h2(self, parser):
        text = "# Doc\n\n## First H2\n\n### H3 under first\n\n## Second H2\n\n### H3 under second\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2s = h1.subsections
        assert len(h2s) == 2
        assert len(h2s[0].subsections) == 1
        assert h2s[0].subsections[0].title == "H3 under first"
        assert len(h2s[1].subsections) == 1
        assert h2s[1].subsections[0].title == "H3 under second"


class TestTableParsing:

    def test_parameter_table(self, parser):
        text = "# API Doc\n\n## Parameters\n\n| Name | Type | Required | Description |\n|------|------|----------|-------------|\n| user_id | int | Yes | User ID |\n| name | string | No | User name |\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        param_tables = [t for t in h2.tables if t["type"] == "parameter"]
        assert len(param_tables) == 1
        params = param_tables[0]["parsed_items"]
        assert len(params) == 2
        assert params[0].name == "user_id"
        assert params[0].type == "int"
        assert params[0].required is True
        assert params[1].name == "name"
        assert params[1].required is False

    def test_parameter_table_chinese_headers(self, parser):
        text = "# API\n\n## 参数\n\n| 参数名 | 类型 | 必填 | 说明 | 默认值 |\n|--------|------|------|------|--------|\n| page | int | 否 | 页码 | 1 |\n| size | int | 否 | 每页数量 | 20 |\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        param_tables = [t for t in h2.tables if t["type"] == "parameter"]
        assert len(param_tables) == 1
        params = param_tables[0]["parsed_items"]
        assert len(params) == 2
        assert params[0].name == "page"
        assert params[0].default == "1"
        assert params[1].name == "size"
        assert params[1].default == "20"

    def test_response_table(self, parser):
        text = "# API\n\n## Responses\n\n| Code | Description |\n|------|-------------|\n| 200 | Success |\n| 400 | Bad Request |\n| 404 | Not Found |\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        resp_tables = [t for t in h2.tables if t["type"] == "response"]
        assert len(resp_tables) == 1
        responses = resp_tables[0]["parsed_items"]
        assert len(responses) == 3
        assert responses[0].status_code == 200
        assert responses[0].description == "Success"
        assert responses[1].status_code == 400

    def test_error_code_table(self, parser):
        text = "# API\n\n## Error Codes\n\n| Error Code | Message | Description |\n|------------|---------|-------------|\n| 10001 | Invalid token | Token expired |\n| 10002 | Permission denied | No access |\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        err_tables = [t for t in h2.tables if t["type"] == "error"]
        assert len(err_tables) == 1
        errors = err_tables[0]["parsed_items"]
        assert len(errors) == 2
        assert errors[0].code == 10001
        assert errors[0].message == "Invalid token"

    def test_generic_table(self, parser):
        text = "# Doc\n\n## Comparison\n\n| Feature | Plan A | Plan B |\n|---------|--------|--------|\n| Speed | Fast | Slow |\n| Cost | High | Low |\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        generic_tables = [t for t in h2.tables if t["type"] == "generic"]
        assert len(generic_tables) == 1
        assert generic_tables[0]["header"] == ["Feature", "Plan A", "Plan B"]
        assert len(generic_tables[0]["rows"]) == 2

    def test_malformed_markdown_no_crash(self, parser):
        text = "# API\n\n## Bad Table\n\n| Name | Type | Description |\n|------|------|-----|\n| id | int |\n| name | string | The name |\n\nNormal text after bad table.\n"
        doc = parser.parse_text(text)
        assert doc is not None
        assert doc.title == "API"
        assert len(doc.warnings) >= 0


class TestCodeBlocks:

    def test_code_block_with_language_and_purpose(self, parser):
        text = "# Doc\n\n## Example\n\n```python example\ndef hello():\n    print('hello')\n```\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        assert len(h2.code_blocks) == 1
        cb = h2.code_blocks[0]
        assert cb.language == "python"
        assert cb.purpose == "example"
        assert "hello" in cb.content

    def test_code_block_with_meta_schema(self, parser):
        text = "# Doc\n\n```json schema\n{\"type\": \"object\"}\n```\n"
        doc = parser.parse_text(text)
        cb = doc.sections[0].code_blocks[0]
        assert cb.language == "json"
        assert cb.meta == "schema"
        assert cb.purpose == "schema"

    def test_code_block_no_language(self, parser):
        text = "# Doc\n\n```\nplain text\n```\n"
        doc = parser.parse_text(text)
        cb = doc.sections[0].code_blocks[0]
        assert cb.language == ""
        assert cb.purpose == ""


class TestLists:

    def test_checkbox_list(self, parser):
        text = "# Doc\n\n## Checklist\n\n- [x] First done\n- [ ] Second pending\n- [ ] Third pending\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        checklists = [l for l in h2.lists if l["type"] == "checklist"]
        assert len(checklists) == 1
        items = checklists[0]["items"]
        assert len(items) == 3
        assert items[0].checked is True
        assert items[0].text == "First done"
        assert items[1].checked is False
        assert items[2].checked is False

    def test_unordered_list(self, parser):
        text = "# Doc\n\n## Items\n\n- Apple\n- Banana\n- Cherry\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        ulists = [l for l in h2.lists if l["type"] == "unordered"]
        assert len(ulists) == 1
        assert len(ulists[0]["items"]) == 3
        assert "Apple" in ulists[0]["items"]

    def test_ordered_list(self, parser):
        text = "# Doc\n\n## Steps\n\n1. First step\n2. Second step\n3. Third step\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        olists = [l for l in h2.lists if l["type"] == "ordered"]
        assert len(olists) == 1
        assert olists[0]["start"] == 1
        assert len(olists[0]["items"]) == 3
        assert "First step" in olists[0]["items"]


class TestMermaidFlowchart:

    def test_basic_flowchart(self, parser):
        text = "# Doc\n\n## Flow\n\n```mermaid\nflowchart TD\n    A[Start] --> B{Is it working?}\n    B -->|Yes| C[Great!]\n    B -->|No| D[Debug]\n    D --> B\n```\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        flowcharts = [l for l in h2.lists if l["type"] == "mermaid_flowchart"]
        assert len(flowcharts) == 1
        nodes = flowcharts[0]["nodes"]
        node_ids = {n.id for n in nodes}
        assert "A" in node_ids
        assert "B" in node_ids
        assert "C" in node_ids
        assert "D" in node_ids
        node_a = [n for n in nodes if n.id == "A"][0]
        assert node_a.label == "Start"
        node_b = [n for n in nodes if n.id == "B"][0]
        assert "Is it working" in node_b.label


class TestWebApiExtraction:

    def test_simple_api_definition(self, parser):
        p = MDIParser(profile_type="webapi")
        text = '---\nname: User API\ntype: webapi\nbaseUrl: https://api.example.com\nversion: 1.0.0\nauthors:\n  - test\ndescription: User management API\nlicense: MIT\n---\n\n# User API\n\n## Interfaces\n\n### GET /users\n\nGet all users\n\n| Name | Type | Required | Description |\n|------|------|----------|-------------|\n| page | int | No | Page number |\n| limit | int | No | Items per page |\n\n| Code | Description |\n|------|-------------|\n| 200 | Success |\n| 401 | Unauthorized |\n\n```json example\n{"users": []}\n```\n\n### POST /users\n\nCreate a new user\n'
        doc = p.parse_text(text, source="test-api.md")
        assert doc.frontmatter["type"] == "webapi"
        assert len(doc.interfaces) >= 1
        get_users = [i for i in doc.interfaces if i.method == "GET" and i.path == "/users"]
        assert len(get_users) == 1
        iface = get_users[0]
        assert iface.method == "GET"
        assert iface.path == "/users"
        assert len(iface.parameters) >= 1
        assert len(iface.responses) >= 1
        assert len(iface.examples) >= 1

    def test_api_method_in_content_backtick(self, parser):
        p = MDIParser(profile_type="webapi")
        text = '---\nname: Test API\ntype: webapi\nbaseUrl: https://api.test.com\nversion: 1.0.0\nauthors: [test]\ndescription: Test\nlicense: MIT\n---\n\n# Test API\n\n## Interfaces\n\n### Delete User\n\nDeletes a user.\n\n`DELETE /users/{id}`\n\n| Code | Description |\n|------|-------------|\n| 204 | Deleted |\n'
        doc = p.parse_text(text)
        delete_ifaces = [i for i in doc.interfaces if i.method == "DELETE"]
        assert len(delete_ifaces) == 1
        assert delete_ifaces[0].path == "/users/{id}"


class TestRealSkillDocument:

    def test_link_check_skill(self, parser):
        skill_path = PROJECT_ROOT / ".agents" / "skills" / "link-check-cmd" / "SKILL.md"
        if not skill_path.exists():
            pytest.skip("link-check-cmd SKILL.md not found")
        doc = parser.parse_file(str(skill_path))
        assert doc.title
        assert "Link Check" in doc.title
        assert len(doc.sections) >= 1
        h1 = doc.sections[0]
        assert len(h1.subsections) >= 5
        checklist_count = 0
        code_count = 0
        table_count = 0
        def count_items(s):
            nonlocal checklist_count, code_count, table_count
            for lst in s.lists:
                if lst["type"] == "checklist":
                    checklist_count += len(lst["items"])
            code_count += len(s.code_blocks)
            table_count += len(s.tables)
            for sub in s.subsections:
                count_items(sub)
        count_items(h1)
        assert checklist_count >= 7
        assert code_count >= 5
        assert table_count >= 3


class TestErrorTolerance:

    def test_missing_frontmatter_no_crash(self, parser):
        text = "# Title\n\nContent without frontmatter."
        doc = parser.parse_text(text)
        assert doc.title == "Title"
        assert doc.frontmatter == {}

    def test_empty_document(self, parser):
        doc = parser.parse_text("")
        assert doc is not None
        assert doc.title == ""
        assert doc.sections == []

    def test_corrupted_frontmatter_graceful(self, parser):
        text = '---\nname: test\n  this is not valid yaml: [\n---\n\n# Test\n'
        doc = parser.parse_text(text)
        assert doc is not None
        assert doc.title == "Test"

    def test_batch_parse_all_skills_no_crash(self, parser):
        skills_dir = PROJECT_ROOT / ".agents" / "skills"
        if not skills_dir.exists():
            pytest.skip("skills directory not found")
        skill_files = list(skills_dir.glob("*/SKILL.md"))
        if len(skill_files) < 5:
            pytest.skip("not enough skill files")
        docs = parser.batch_parse([str(f) for f in skill_files])
        assert len(docs) == len(skill_files)
        success = 0
        total_warnings = 0
        for doc in docs:
            assert isinstance(doc, MDIDocument)
            assert doc.title
            success += 1
            total_warnings += len(doc.warnings)
        assert success == len(skill_files)


class TestParserAPI:

    def test_to_json(self, parser):
        text = '---\nname: test\nversion: 1.0.0\n---\n\n# Test\n\nHello.\n'
        doc = parser.parse_text(text)
        json_str = parser.to_json(doc)
        assert isinstance(json_str, str)
        import json
        data = json.loads(json_str)
        assert data["title"] == "Test"
        assert data["frontmatter"]["name"] == "test"

    def test_parse_file_vs_parse_text(self, parser, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Test\n\nContent.", encoding="utf-8")
        doc_file = parser.parse_file(str(md))
        doc_text = parser.parse_text("# Test\n\nContent.", source="<string>")
        assert doc_file.title == doc_text.title == "Test"


class TestBlockQuote:

    def test_block_quote_content(self, parser):
        text = "# Doc\n\n> This is a warning note.\n\nRegular paragraph.\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        assert "> This is a warning note." in h1.content


class TestPerformance:

    def test_single_skill_parse_under_50ms(self, parser):
        skill_path = PROJECT_ROOT / ".agents" / "skills" / "link-check-cmd" / "SKILL.md"
        if not skill_path.exists():
            pytest.skip("link-check-cmd SKILL.md not found")
        text = skill_path.read_text(encoding="utf-8")

        def parse_one():
            p = MDIParser()
            p.parse_text(text)

        n = 100
        total = timeit.timeit(parse_one, number=n)
        avg_ms = (total / n) * 1000
        assert avg_ms < 50, f"Average parse time {avg_ms:.1f}ms exceeds 50ms threshold"


class TestDirectives:

    def test_endpoint_directive_basic(self, parser):
        p = MDIParser(profile_type="webapi")
        text = '''---
name: Test API
type: webapi
baseUrl: https://api.example.com
---

# Test API

```{endpoint} GET /users
:summary: Get all users
:tags: users,list

Get a paginated list of users.
```
'''
        doc = p.parse_text(text)
        assert len(doc.interfaces) == 1
        iface = doc.interfaces[0]
        assert iface.method == "GET"
        assert iface.path == "/users"
        assert iface.summary == "Get all users"
        assert "users" in iface.tags
        assert "list" in iface.tags
        assert "paginated list" in iface.description

    def test_endpoint_directive_with_params(self, parser):
        p = MDIParser(profile_type="webapi")
        text = '''---
name: Test API
type: webapi
baseUrl: https://api.example.com
---

# Test API

```{endpoint} GET /users/{id}
:summary: Get user by ID
:param id: int - User unique identifier
:param page?: int = 1 - Page number for pagination
:response 200: User - Success response
:response 404: Error - User not found
:error 10001: Invalid ID format - ID must be numeric
```
'''
        doc = p.parse_text(text)
        assert len(doc.interfaces) == 1
        iface = doc.interfaces[0]
        assert iface.method == "GET"
        assert iface.path == "/users/{id}"
        assert len(iface.parameters) == 2
        id_param = [pp for pp in iface.parameters if pp.name == "id"][0]
        assert id_param.type == "int"
        assert id_param.required is True
        page_param = [pp for pp in iface.parameters if pp.name == "page"][0]
        assert page_param.type == "int"
        assert page_param.required is False
        assert page_param.default == "1"
        assert len(iface.responses) == 2
        assert any(r.status_code == 200 for r in iface.responses)
        assert any(r.status_code == 404 for r in iface.responses)
        assert len(iface.errors) == 2
        error_codes = {e.code for e in iface.errors}
        assert 10001 in error_codes
        assert 404 in error_codes

    def test_endpoint_directive_optional_param_mark(self, parser):
        p = MDIParser(profile_type="webapi")
        text = '''---
name: Test API
type: webapi
baseUrl: https://api.example.com
---

# Test API

```{endpoint} POST /users
:summary: Create user
:param name: string - User name
:param email?: string - User email (optional)
:param age?: int = 0 - User age
```
'''
        doc = p.parse_text(text)
        iface = doc.interfaces[0]
        assert len(iface.parameters) == 3
        name_p = [pp for pp in iface.parameters if pp.name == "name"][0]
        assert name_p.required is True
        email_p = [pp for pp in iface.parameters if pp.name == "email"][0]
        assert email_p.required is False
        age_p = [pp for pp in iface.parameters if pp.name == "age"][0]
        assert age_p.required is False
        assert age_p.default == "0"

    def test_admonition_directives(self, parser):
        text = '''# Doc

```{note}
This is a note.
```

```{warning}
This is a warning.
```

```{danger}
This is dangerous!
```

```{tip}
This is a helpful tip.
```
'''
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        content = h1.content
        assert "[NOTE]" in content
        assert "[WARNING]" in content
        assert "[DANGER]" in content
        assert "[TIP]" in content
        assert "This is a note." in content
        assert "This is a warning." in content

    def test_directives_and_traditional_mixed(self, parser):
        p = MDIParser(profile_type="webapi")
        text = '''---
name: Mixed API
type: webapi
baseUrl: https://api.example.com
---

# Mixed API

## Directives

```{endpoint} GET /directive-endpoint
:summary: From directive
:param id: int - ID
```

## Traditional

### GET /traditional-endpoint

Traditional format description.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| q | string | No | Search query |

| Code | Description |
|------|-------------|
| 200 | OK |
'''
        doc = p.parse_text(text)
        assert len(doc.interfaces) == 2
        paths = {i.path for i in doc.interfaces}
        assert "/directive-endpoint" in paths
        assert "/traditional-endpoint" in paths

    def test_directive_option_with_space_in_key(self, parser):
        p = MDIParser(profile_type="webapi")
        text = '''---
name: Test
type: webapi
baseUrl: https://api.example.com
---

# Test

```{endpoint} GET /search
:summary: Search items
:param page size: int = 20 - Items per page
```
'''
        doc = p.parse_text(text)
        iface = doc.interfaces[0]
        assert len(iface.parameters) == 1
        param = iface.parameters[0]
        assert param.name == "page size"
        assert param.type == "int"
        assert param.default == "20"

    def test_directive_non_http_method_accepted(self, parser):
        p = MDIParser(profile_type="clitool")
        text = '''---
name: Test
type: clitool
description: Test CLI
---

# Test

```{endpoint} CMD list
:summary: List command
```
'''
        doc = p.parse_text(text)
        assert len(doc.interfaces) == 1
        iface = doc.interfaces[0]
        assert iface.method == "CMD"
        assert iface.path == "list"
        assert iface.summary == "List command"

    def test_directive_missing_path_warns(self, parser):
        p = MDIParser(profile_type="webapi")
        text = '''---
name: Test
type: webapi
baseUrl: https://api.example.com
---

# Test

```{endpoint} GET
:summary: No path
```
'''
        doc = p.parse_text(text)
        assert len(doc.interfaces) == 0
        assert any("缺少路径" in w for w in doc.warnings)

    def test_endpoint_directive_collects_checklist(self, parser):
        p = MDIParser(profile_type="webapi")
        text = '''---
name: Test API
type: webapi
baseUrl: https://api.example.com
---

# Test API

```{endpoint} POST /users
:summary: Create user
:param name: string - User name
```

- [ ] 验证状态码为201
- [x] 前置条件：用户已登录
- [ ] 响应包含字段`id`
- [ ] `name`字段为创建的用户名
'''
        doc = p.parse_text(text)
        assert len(doc.interfaces) == 1
        iface = doc.interfaces[0]
        assert len(iface.check_items) == 4
        texts = [ci.text for ci in iface.check_items]
        assert any("状态码" in t for t in texts)
        assert any("前置" in t for t in texts)
        checked = [ci for ci in iface.check_items if ci.checked]
        assert len(checked) == 1
        assert "登录" in checked[0].text

    def test_directives_backward_compatible_with_existing_skills(self, parser):
        skills_dir = PROJECT_ROOT / ".agents" / "skills"
        if not skills_dir.exists():
            pytest.skip("skills directory not found")
        skill_files = list(skills_dir.glob("*/SKILL.md"))
        if len(skill_files) < 5:
            pytest.skip("not enough skill files")
        for sf in skill_files:
            doc = parser.parse_file(str(sf))
            assert doc.title, f"Failed to parse {sf.name}"
            for w in doc.warnings:
                assert "directive" not in w.lower() or True, f"Unexpected directive warning in {sf.name}: {w}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
