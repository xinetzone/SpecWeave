import pytest

from sphinx_config.presets.minimal_myst import build_config as build_min
from sphinx_config.presets.okf_docs import build_config as build_okf
from sphinx_config.extensions import resolve_extensions


class _FakeApp:
    def __init__(self):
        self.connections = []

    def connect(self, name, fn, priority=None):
        self.connections.append((name, fn, priority))


def test_build_okf_infers_site_url_from_github_repo_url():
    cfg = build_okf({
        "project": "Project-X",
        "repository_url": "https://github.com/acme-org/project-x.git",
    })
    assert cfg["ogp_site_url"] == "https://acme-org.github.io/project-x/"
    assert cfg["html_baseurl"] == "https://acme-org.github.io/project-x/"


def test_build_okf_intersphinx_defaults_exist_and_can_be_override():
    cfg = build_okf({"project": "Y"})
    mapping = cfg["intersphinx_mapping"]
    assert "python" in mapping
    assert "myst-parser" in mapping

    cfg2 = build_okf({
        "project": "Y",
        "intersphinx_mapping": {"mylib": ("https://example.com/mylib", None)},
    })
    assert "mylib" in cfg2["intersphinx_mapping"]
    assert "python" in cfg2["intersphinx_mapping"]


def test_build_okf_extensions_count_matches_expected_defaults():
    cfg = build_okf({"project": "Z"})
    assert "myst_parser" in cfg["extensions"]
    assert "sphinx_design" in cfg["extensions"]
    assert "sphinx.ext.intersphinx" in cfg["extensions"]
    assert len(cfg["extensions"]) >= 10


def test_build_min_has_only_core_extensions():
    cfg = build_min({"project": "Notes"})
    assert cfg["extensions"] == ["myst_parser"]


def test_build_min_setup_registers_source_read_hook():
    cfg = build_min({"project": "Notes"})
    app = _FakeApp()
    cfg["setup"](app)
    names = [c[0] for c in app.connections]
    assert "source-read" in names


def test_build_okf_setup_calls_user_setup_if_provided():
    trace = []

    def user_setup(app):
        trace.append("ran_user")

    cfg = build_okf({"project": "Z", "setup": user_setup})
    app = _FakeApp()
    cfg["setup"](app)
    assert "ran_user" in trace


def test_build_okf_theme_options_has_path_to_docs_from_override():
    cfg = build_okf({"project": "Z", "path_to_docs": "source/docs"})
    assert cfg["html_theme_options"]["path_to_docs"] == "source/docs"


def test_resolve_extensions_conditional_predicate_true_adds_ext(monkeypatch):
    monkeypatch.setattr(
        "sphinx_config.extensions.has_module", lambda n: n in {"myst_parser", "sphinx_sitemap"}
    )
    exts = resolve_extensions(
        required=("myst_parser",),
        optional=(),
        conditional=(("sphinx_sitemap", lambda: True),),
    )
    assert "sphinx_sitemap" in exts


def test_resolve_extensions_predicate_false_skips():
    exts = resolve_extensions(
        required=(),
        optional=(),
        conditional=(("never_installed_xyz", lambda: False),),
    )
    assert "never_installed_xyz" not in exts


def test_resolve_extensions_missing_required_raises_import_error(monkeypatch):
    monkeypatch.setattr("sphinx_config.extensions.has_module", lambda n: False)
    with pytest.raises(ImportError):
        resolve_extensions(required=("myst_parser",))


def test_build_okf_release_detection_from_package_name_not_found_then_fallback():
    cfg = build_okf({
        "project": "A",
        "package_name": None,
        "version": "2.0.0",
    })
    assert cfg["release"] == "2.0.0"
    assert cfg["version"] == "2.0.0"
