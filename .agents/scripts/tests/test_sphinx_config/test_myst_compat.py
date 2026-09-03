import os

from sphinx_config import myst_compat


def _reload_env_settings():
    myst_compat._ENV_QUOTE_DATES = os.environ.get("SW_MYST_COMPAT_QUOTE_DATES", "1") not in {
        "0",
        "false",
        "off",
    }
    myst_compat._ENV_DEDUPE_H1 = os.environ.get("SW_MYST_COMPAT_DEDUPE_H1", "1") not in {
        "0",
        "false",
        "off",
    }


def _make_source(md_text):
    return [md_text]


class _FakeDoctree:
    def __init__(self, children=None):
        self.children = list(children or [])

    def __iter__(self):
        return iter(self.children)

    def __len__(self):
        return len(self.children)

    def remove(self, node):
        self.children.remove(node)

    def extend(self, iterable):
        self.children.extend(iterable)


class _FakeSection(list):
    pass


def test_quote_frontmatter_dates_yaml_only_no_toml():
    md = "+++\ndate = 2026-08-28\n+++\n# Hi\n"
    source = _make_source(md)
    before = md
    myst_compat.quote_frontmatter_dates(None, "x", source)
    assert source[0] == before


def test_quote_frontmatter_dates_adds_quotes_to_standalone_date():
    md = "---\ndate: 2026-08-28\n---\n# Hello\n"
    source = _make_source(md)
    myst_compat.quote_frontmatter_dates(None, "x", source)
    assert 'date: "2026-08-28"' in source[0]


def test_quote_frontmatter_dates_does_not_touch_description():
    md = (
        "---\ndate: 2026-08-28\n"
        "description: 2026-08-28这是关于技术的长描述文字，不是纯日期值\n"
        "---\n# T\n"
    )
    source = _make_source(md)
    myst_compat.quote_frontmatter_dates(None, "x", source)
    assert '"2026-08-28"' in source[0]
    count = source[0].count('"2026-08-28"')
    assert count == 1, f"description中间不该加引号，实际加了 {count} 次\n{source[0]}"


def test_quote_frontmatter_dates_env_off(monkeypatch):
    monkeypatch.setenv("SW_MYST_COMPAT_QUOTE_DATES", "0")
    _reload_env_settings()
    try:
        md = "---\ndate: 2026-08-28\n---\n# H\n"
        source = _make_source(md)
        myst_compat.quote_frontmatter_dates(None, "x", source)
        assert source[0] == md
    finally:
        monkeypatch.delenv("SW_MYST_COMPAT_QUOTE_DATES", raising=False)
        _reload_env_settings()


def test_quote_frontmatter_dates_no_frontmatter_no_change():
    md = "# Just a heading\nNo frontmatter at all.\n"
    source = _make_source(md)
    myst_compat.quote_frontmatter_dates(None, "x", source)
    assert source[0] == md


def test_quote_frontmatter_dates_end_of_line_comment_after_date():
    md = "---\ndate: 2026-08-28  # trailing comment\n---\n# H\n"
    source = _make_source(md)
    myst_compat.quote_frontmatter_dates(None, "x", source)
    assert 'date: "2026-08-28"' in source[0]


def test_dedupe_injected_h1_removes_empty_first_section(monkeypatch):
    class Title:
        pass

    import docutils.nodes as nodes

    def _section_class(children):
        s = nodes.section("")
        s.children = list(children)
        return s

    doctree = _FakeDoctree()
    doctree.children = [
        _section_class([nodes.title("", "")]),
        _section_class([nodes.title("", ""), nodes.paragraph("", "")]),
    ]
    injected = doctree.children[0]
    real = doctree.children[1]
    myst_compat.dedupe_injected_h1(None, doctree)
    assert real in doctree.children
    assert injected not in doctree.children


def test_dedupe_injected_h1_single_section_noops(monkeypatch):
    import docutils.nodes as nodes

    def _sc(c):
        s = nodes.section("")
        s.children = list(c)
        return s

    doctree = _FakeDoctree()
    doctree.children = [_sc([nodes.title("", ""), nodes.paragraph("", "")])]
    before = list(doctree.children)
    myst_compat.dedupe_injected_h1(None, doctree)
    assert list(doctree.children) == before


def test_dedupe_injected_h1_env_off(monkeypatch):
    import docutils.nodes as nodes

    monkeypatch.setenv("SW_MYST_COMPAT_DEDUPE_H1", "0")
    _reload_env_settings()
    try:
        def _sc(c):
            s = nodes.section("")
            s.children = list(c)
            return s

        doctree = _FakeDoctree()
        injected = _sc([nodes.title("", "")])
        real = _sc([nodes.title("", ""), nodes.paragraph("", "")])
        doctree.children = [injected, real]
        myst_compat.dedupe_injected_h1(None, doctree)
        assert injected in doctree.children
    finally:
        monkeypatch.delenv("SW_MYST_COMPAT_DEDUPE_H1", raising=False)
        _reload_env_settings()


def test_register_hooks_registers_two_events_with_priority_400_on_dedupe():
    class FakeApp:
        def __init__(self):
            self.events = []

        def connect(self, name, fn, priority=None):
            self.events.append((name, fn, priority))

    app = FakeApp()
    myst_compat.register_hooks(app)
    names = [e[0] for e in app.events]
    assert names == ["source-read", "doctree-read"]
    assert app.events[1][2] == 400


def test_fm_delim_regex_matches_three_delimiters():
    for delimiter in ("---", "+++", "..."):
        assert myst_compat._FM_DELIM.search(delimiter + "\n") is not None
