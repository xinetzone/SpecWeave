from .helpers import _parse_doc, _make_graphql_doc_md
from mdi.profiles import CliToolProfile
from mdi.profiles.webapi_profile import WebApiProfile

class TestBackwardCompatibility:
    """确保get_full_text()的fence重建不破坏其他Profile的现有验证。"""

    def test_skill_doc_still_validates(self, parser, validator):
        """Skill profile文档应继续正常验证（不受fence重建影响）。"""
        md = """---
name: test-skill
version: "1.0.0"
description: "当用户提到测试时使用本技能。这是一个足够长的描述用于验证测试。"
argument-hint: "[test]"
user-invocable: true
paths: []
---

# test-skill

## 1. 功能描述

这是测试技能的功能描述。

> **为什么需要此功能？** 为了测试。

## 2. 何时使用

当用户需要测试时使用。

## 3. 核心步骤

1. 步骤一：准备
2. 步骤二：执行
3. 步骤三：**必须**验证结果

> **为什么步骤三必须验证？** 确保操作成功。
"""
        doc = _parse_doc(parser, md, source_path="test-skill.md")
        report = validator.validate_document(doc, source_path="test-skill.md")
        assert report.profile_type == "skill"
        assert report.score > 0, "Skill文档评分应>0"

    def test_webapi_doc_get_full_text_includes_fences(self, parser):
        """WebApiProfile的get_full_text也应包含fence header（一致性测试）。"""
        from mdi.profiles.webapi_profile import WebApiProfile

        md = """---
name: test-api
version: "1.0.0"
description: "Test REST API with enough description for validation."
baseUrl: "https://api.example.com"
type: webapi
---

# Test API

## 1. 概述

Test API overview.

> **为什么？** Testing.

## 2. Endpoints

### Get User

```http
GET /users/{id}
```

```json
{"id": "1", "name": "Test"}
```
"""
        doc = _parse_doc(parser, md, source_path="test-api.md")
        profile = WebApiProfile()
        full_text = profile.get_full_text(doc)

        assert "```http" in full_text, "WebApiProfile的full_text也应包含http fence header"
        assert "GET /users" in full_text, "full_text应包含http请求内容"
        assert "```json" in full_text, "full_text应包含json fence header"



class TestCliToolBackwardCompat:
    """测试CliToolProfile的fence处理向后兼容性。"""

    def test_clitool_get_full_text_includes_fences(self, parser):
        """CliToolProfile的get_full_text也应包含fence header（一致性测试）。"""
        md = """---
name: test-cli
version: "1.0.0"
description: "Test CLI tool with enough description for validation testing."
type: clitool
---

# Test CLI

## 1. 概述

Test CLI tool.

> **为什么？** Testing.

## 2. 用法

### 基本命令

```bash
mycli run --help
```

```bash
mycli init
```
"""
        doc = _parse_doc(parser, md, source_path="test-cli.md")
        profile = CliToolProfile()
        full_text = profile.get_full_text(doc)

        assert "```bash" in full_text, "CliToolProfile的full_text应包含bash fence header"
        assert "mycli run --help" in full_text, "full_text应包含命令内容"
