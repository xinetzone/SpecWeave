"""front-matter.ts 黄金场景 1:1。"""

from doocs_md_py.render.frontmatter import parse_front_matter


def test_no_fence_returns_original():
    result = parse_front_matter("# Hello")
    assert result.attributes == {}
    assert result.body == "# Hello"


def test_parses_yaml_and_leaves_body():
    result = parse_front_matter("---\ntitle: Test\n---\n\n# Body")
    assert result.attributes == {"title": "Test"}
    assert result.body == "\n# Body"


def test_crlf_and_bom():
    result = parse_front_matter("\uFEFF---\r\ntitle: CRLF\r\n---\r\nBody")
    assert result.attributes == {"title": "CRLF"}
    assert result.body == "Body"


def test_non_object_document_becomes_empty():
    result = parse_front_matter("---\njust a string\n---\n# Body")
    assert result.attributes == {}
    assert result.body == "# Body"


def test_markdown_star_lists_become_sequences():
    markdown = """---
title: Agent
tags:

* AI
* Agent
categories:
* 技术
draft: false
---

# Body"""
    result = parse_front_matter(markdown)
    assert result.attributes == {
        "title": "Agent",
        "tags": ["AI", "Agent"],
        "categories": ["技术"],
        "draft": False,
    }
    assert result.body == "\n# Body"


def test_empty_yaml_block_is_empty_mapping():
    result = parse_front_matter("---\n\n---\n# Body")
    assert result.attributes == {}
    assert result.body == "# Body"


def test_invalid_yaml_keeps_original_text():
    markdown = "---\nfoo: [unterminated\n---\n# Body"
    result = parse_front_matter(markdown)
    assert result.attributes == {}
    assert result.body == markdown


def test_dot_dot_dot_closer_and_yaml_directive():
    result = parse_front_matter("---\na: 1\n...\nrest")
    assert result.attributes == {"a": 1}
    assert result.body == "rest"
    result2 = parse_front_matter("= yaml =\na: 2\n= yaml =\nrest2")
    assert result2.attributes == {"a": 2}
    assert result2.body == "rest2"
