import pytest
from pathlib import Path

from mdi.parser import MDIParser
from mdi.models import MDIDocument

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent
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
