import copy

from sphinx_config._utils import deep_merge


def test_deep_merge_basic_nested():
    base = {"a": {"b": 1, "c": 2}}
    override = {"a": {"c": 20, "d": 30}}
    result = deep_merge(base, override)
    assert result == {"a": {"b": 1, "c": 20, "d": 30}}


def test_deep_merge_base_untouched_independent():
    base = {"a": {"b": 1}}
    override = {"a": {"c": 2}}
    base_copy = copy.deepcopy(base)
    deep_merge(base, override)
    assert base == base_copy


def test_deep_merge_value_replace():
    base = {"project": "Old"}
    override = {"project": "New"}
    assert deep_merge(base, override)["project"] == "New"


def test_deep_merge_override_dict_is_untouched():
    base = {"a": {"b": [1, 2, 3]}}
    override = {"a": {"c": ["x"]}}
    override_copy = copy.deepcopy(override)
    deep_merge(base, override)
    assert override == override_copy


def test_deep_merge_list_overwrite():
    base = {"exclude": ["a"]}
    override = {"exclude": ["b", "c"]}
    result = deep_merge(base, override)
    assert result["exclude"] == ["b", "c"]


def test_deep_merge_value_replace():
    base = {"project": "Old"}
    override = {"project": "New"}
    assert deep_merge(base, override)["project"] == "New"


def test_deep_merge_three_level():
    base = {"html_theme_options": {"footer": {"items": "x,y,z"}}}
    override = {
        "html_theme_options": {
            "footer": {"items": "a,b,c"},
            "logo": {"text": "Hi"},
        }
    }
    merged = deep_merge(base, override)
    assert merged["html_theme_options"]["footer"]["items"] == "a,b,c"
    assert merged["html_theme_options"]["logo"]["text"] == "Hi"


def test_deep_merge_none_override_is_noop():
    base = {"a": 1}
    assert deep_merge(base, None) == {"a": 1}


def test_deep_merge_empty_override_is_noop():
    base = {"a": {"b": 1}}
    before = copy.deepcopy(base)
    out = deep_merge(base, {})
    assert out == before
