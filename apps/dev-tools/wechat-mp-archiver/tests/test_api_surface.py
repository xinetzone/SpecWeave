"""OpenAPI 端点发现器测试。"""

from mp_archiver.adapters.api_surface import ApiSurface

SPEC = {
    "paths": {
        "/api/login/init": {"post": {}},
        "/api/login/status/abc": {"get": {}},
        "/api/official-accounts/search": {
            "get": {
                "parameters": [
                    {"name": "query", "in": "query"},
                    {"name": "begin", "in": "query"},
                    {"name": "count", "in": "query"},
                    {"name": "session_id", "in": "path"},
                ]
            }
        },
        "/api/articles/history": {
            "get": {
                "parameters": [
                    {"name": "__biz", "in": "query"},
                    {"name": "offset", "in": "query"},
                    {"name": "count", "in": "query"},
                    {"name": "f", "in": "query"},
                ]
            }
        },
        "/api/articles/history/export": {"post": {}},
    }
}


def test_discover_finds_endpoints_and_query_params():
    surface = ApiSurface.discover(SPEC)
    assert surface.search.path == "/api/official-accounts/search"
    assert surface.search.method == "GET"
    assert "query" in surface.search.query_params
    assert "session_id" not in surface.search.query_params  # path 参数不纳入
    assert surface.history.path == "/api/articles/history"
    assert "__biz" in surface.history.query_params


def test_login_and_export_paths_are_excluded():
    surface = ApiSurface.discover(SPEC)
    assert surface.history.path != "/api/articles/history/export"


def test_prefers_get_over_post():
    spec = {"paths": {"/api/search": {
        "post": {"parameters": []},
        "get": {"parameters": [{"name": "query", "in": "query"}]},
    }}}
    surface = ApiSurface.discover(spec)
    assert surface.search.method == "GET"


def test_missing_endpoints_return_none():
    surface = ApiSurface.discover({"paths": {"/api/health": {"get": {}}}})
    assert surface.search is None
    assert surface.history is None


def test_override_existing_path_uses_spec():
    surface = ApiSurface.discover(SPEC, search_override="/api/official-accounts/search")
    assert surface.search.method == "GET"


def test_override_unknown_path_is_trusted_as_get():
    surface = ApiSurface.discover(SPEC, history_override="/custom/list")
    assert surface.history.path == "/custom/list"
    assert surface.history.method == "GET"
    assert surface.history.query_params == ()
