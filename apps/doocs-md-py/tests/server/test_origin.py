"""origin.ts 1:1 行为测试。"""

from doocs_md_py.server.origin import (
    default_origin,
    is_allowed_origin,
    is_browser_extension_origin,
    match_pattern,
    resolve_redirect,
)


class TestMatchPattern:
    def test_exact(self):
        assert match_pattern("https://md.doocs.org", "https://md.doocs.org")

    def test_single_label_wildcard(self):
        pattern = "https://*.example.com"
        assert match_pattern("https://a.example.com", pattern)
        # [^./]+：不跨点
        assert not match_pattern("https://a.b.example.com", pattern)
        # 不跨斜杠
        assert not match_pattern("https://a.example.com/evil", pattern)

    def test_wildcard_anchor_blocks_suffix_attack(self):
        pattern = "https://*.example.com"
        assert not match_pattern("https://a.example.com.evil.com", pattern)

    def test_localhost_port_wildcard(self):
        pattern = "http://localhost:*"
        assert match_pattern("http://localhost:5173", pattern)
        assert match_pattern("http://localhost:8800", pattern)
        # scheme 不匹配
        assert not match_pattern("https://localhost:5173", pattern)

    def test_netlify_preview_double_dash(self):
        pattern = "https://*--doocs-md.netlify.app"
        assert match_pattern("https://deploy-123--doocs-md.netlify.app", pattern)
        assert not match_pattern("https://x--doocs-md.netlify.app.evil.com", pattern)

    def test_empty_pattern_and_no_wildcard(self):
        assert not match_pattern("https://a", "")
        assert not match_pattern("https://a", "https://b")

    def test_multiple_wildcards(self):
        assert match_pattern("https://a-b.example.com", "https://*-*.example.com")
        assert not match_pattern("https://a.b-c.example.com", "https://*-*.example.com")


class TestAllowedOrigin:
    app_url = "https://md.doocs.org, https://*.doocs.org,http://localhost:*"

    def test_csv_patterns(self):
        assert is_allowed_origin(self.app_url, "https://md.doocs.org")
        assert is_allowed_origin(self.app_url, "https://blog.doocs.org")
        assert is_allowed_origin(self.app_url, "http://localhost:3000")

    def test_rejected(self):
        assert not is_allowed_origin(self.app_url, "https://md.doocs.org.evil.com")
        assert not is_allowed_origin(self.app_url, None)
        assert not is_allowed_origin(self.app_url, "")

    def test_extension_origins(self):
        assert is_browser_extension_origin("chrome-extension://abcdef")
        assert is_browser_extension_origin("moz-extension://uuid")
        assert is_browser_extension_origin("safari-web-extension://ABC")
        assert not is_browser_extension_origin("https://chrome-extension.example.com")
        assert not is_browser_extension_origin(None)


class TestRedirect:
    app_url = "https://md.doocs.org,https://preview.doocs.org"

    def test_default_prefers_literal(self):
        assert default_origin(self.app_url) == "https://md.doocs.org"

    def test_default_first_when_all_wildcards(self):
        assert default_origin("https://*.doocs.org") == "https://*.doocs.org"
        assert default_origin("") == ""

    def test_resolve_allowed_with_path(self):
        url = "https://preview.doocs.org/callback?code=1"
        assert resolve_redirect(self.app_url, url) == url

    def test_resolve_rejected_falls_back(self):
        assert (
            resolve_redirect(self.app_url, "https://evil.com/phish")
            == "https://md.doocs.org"
        )

    def test_resolve_invalid_falls_back(self):
        assert resolve_redirect(self.app_url, "not-a-url") == "https://md.doocs.org"
        assert resolve_redirect(self.app_url, None) == "https://md.doocs.org"
