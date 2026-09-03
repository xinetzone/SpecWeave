import pytest

from sphinx_config.themes import DEFAULT_THEME_PRIORITY, resolve_theme, resolve_theme_options


def test_resolve_theme_always_returns_alabaster_as_fallback(monkeypatch):
    def _has_nothing(_name):
        return False
    monkeypatch.setattr("sphinx_config.themes.has_module", _has_nothing)
    assert resolve_theme() == "alabaster"


def test_resolve_theme_extra_before_priority_over_defaults(monkeypatch):
    installed = {"my_custom_theme": True, "mystx": True}
    monkeypatch.setattr("sphinx_config.themes.has_module", lambda n: installed.get(n, False))
    assert resolve_theme(extra_before=("my_custom_theme",)) == "my_custom_theme"


def test_resolve_theme_extra_after_is_before_alabaster_but_after_defaults(monkeypatch):
    only_extra_after_installed = {"fallback_theme": True}
    monkeypatch.setattr("sphinx_config.themes.has_module", lambda n: only_extra_after_installed.get(n, False))
    assert resolve_theme(extra_after=("fallback_theme",)) == "fallback_theme"


def test_resolve_theme_uses_explicit_priority(monkeypatch):
    installed = {"custom_first": True, "default_ignored": True}
    monkeypatch.setattr("sphinx_config.themes.has_module", lambda n: installed.get(n, False))
    assert resolve_theme(("custom_first", "default_ignored")) == "custom_first"


def test_resolve_theme_options_for_book_theme_uses_defaults():
    opts = resolve_theme_options("sphinx_book_theme")
    assert opts["use_repository_button"] is True
    assert opts["toc_title"] == "目录"
    assert "path_to_docs" in opts


def test_resolve_theme_options_override_deep_merges():
    opts = resolve_theme_options(
        "mystx",
        override={"collapse_navbar": True, "toc_title": "Contents", "path_to_docs": "docs"},
    )
    assert opts["collapse_navbar"] is True
    assert opts["toc_title"] == "Contents"
    assert opts["path_to_docs"] == "docs"
    assert opts["use_repository_button"] is True


def test_resolve_theme_options_for_non_book_theme_returns_override_only():
    opts = resolve_theme_options("alabaster", override={"nosidebar": True})
    assert opts == {"nosidebar": True}


def test_default_priority_has_mystx_sphinx_book_theme_alabaster():
    assert DEFAULT_THEME_PRIORITY[0] == "mystx"
    assert DEFAULT_THEME_PRIORITY[-1] == "alabaster"
