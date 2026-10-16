"""测试夹具：注入假 urlopen，全部测试离线可跑（不依赖真实 Supabase）。"""

import pytest

from admin_console import http_client


class FakeResponse:
    def __init__(self, status: int = 200, body: bytes = b"[]", headers=None) -> None:
        self.status = status
        self._body = body
        self.headers = headers or {}

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc) -> bool:
        return False


class HttpSpy:
    def __init__(self) -> None:
        self.calls = []
        self._next = FakeResponse()

    def set_response(self, response: FakeResponse) -> None:
        self._next = response

    def last_url(self) -> str:
        return self.calls[-1]["url"] if self.calls else ""


@pytest.fixture
def http():
    spy = HttpSpy()

    def fake_urlopen(req, timeout=None):
        spy.calls.append({
            "url": req.full_url,
            "method": req.get_method(),
            "data": req.data,
            "headers": dict(req.headers),
        })
        return spy._next

    http_client.set_urlopen(fake_urlopen)
    yield spy
    http_client.set_urlopen(None)
