import pytest

from mdi.parser import MDIParser

from .conftest import PROJECT_ROOT


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
