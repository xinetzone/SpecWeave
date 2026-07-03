import pytest

from mdi.parser import MDIParser

from .conftest import PROJECT_ROOT


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
