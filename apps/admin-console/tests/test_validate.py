"""输入校验测试（AC-5 / AC-4 边界分支）。"""

from admin_console.validate import (
    BODY_MAX,
    clean_item,
    clean_page,
    clean_sort,
    clean_taxonomy,
    clean_tags,
    slugify,
)


def test_clean_item_requires_title():
    data, errors = clean_item({"title": "  "})
    assert errors.get("title")


def test_clean_item_rejects_bad_status():
    _, errors = clean_item({"title": "标题", "status": "unknown"})
    assert errors.get("status")


def test_clean_item_rejects_oversized_body():
    _, errors = clean_item({"title": "标题", "body": "x" * (BODY_MAX + 1)})
    assert errors.get("body")


def test_clean_item_generates_slug_from_title():
    data, errors = clean_item({"title": "Hello 世界", "slug": ""})
    assert not errors
    assert data["slug"]


def test_clean_item_normalizes_tags():
    data, _ = clean_item({"title": "标题", "tags": "产品, 公告,产品,,"})
    assert data["tags"] == ["产品", "公告"]


def test_clean_item_partial_allows_subset():
    data, errors = clean_item({"summary": "只改摘要"}, partial=True)
    assert not errors
    assert data["summary"] == "只改摘要"
    assert "title" not in data


def test_clean_item_rejects_non_object():
    _, errors = clean_item(["not", "a", "dict"])
    assert errors


def test_clean_taxonomy():
    data, errors = clean_taxonomy({"name": "资讯"}, "category")
    assert not errors and data["name"] == "资讯"
    _, errors = clean_taxonomy({}, "tag")
    assert errors.get("name")


def test_clean_tags_limits_and_dedups():
    assert clean_tags(["a", "a", "b"]) == ["a", "b"]
    assert len(clean_tags([str(i) for i in range(50)])) == 20


def test_clean_page_guards_negative_and_oversized():
    assert clean_page("-1", "0", 20, 100) == (1, 20)
    assert clean_page("2", "9999", 20, 100) == (2, 100)


def test_clean_sort_falls_back_safely():
    assert clean_sort("title", "asc") == ("title", "asc")
    assert clean_sort("; drop table", ";;") == ("updated_at", "desc")


def test_slugify_is_url_safe():
    assert slugify("Hello, World! 你好") == "hello-world-你好"
    assert slugify("") == "item"
    assert "/" not in slugify("a/b")
