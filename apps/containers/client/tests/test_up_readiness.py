"""`up` 的服务就绪探测单测（C21，无 daemon：仅本机回环 socket）。

核心命题：**TCP 连上 ≠ 服务就绪**。rootless 端口转发器（rootlessport）在容器
起来的瞬间就 accept 宿主端口，而后端 jupyter 要数十秒才 listen，窗口期内连接
被接受后立即关闭且零字节返回——浏览器报 `ERR_EMPTY_RESPONSE`（而非更易理解的
`ECONNREFUSED`）。故就绪判据必须是**应用层应答**；下面的「假阳性守卫」用例把
这条纪律钉死：只 accept 不说话的 socket 必须被判为**未就绪**。
"""

import contextlib
import http.server
import socket
import threading

from jpman_client.tasks import utils as u


@contextlib.contextmanager
def _http_server(status: int = 302):
    """本机回环 HTTP 服务，记录收到的请求路径。"""
    seen_paths: list[str] = []

    class _Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self):  # noqa: N802（stdlib 命名约定）
            seen_paths.append(self.path)
            self.send_response(status)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, *args):  # 静音
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    try:
        yield srv.server_address[1], seen_paths
    finally:
        srv.shutdown()
        srv.server_close()
        thread.join(timeout=5)


@contextlib.contextmanager
def _silent_tcp_server():
    """只 accept 后立即关闭、零字节回应的监听者（= rootlessport 窗口期语义）。"""
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(8)
    srv.settimeout(0.2)
    port = srv.getsockname()[1]
    stop = threading.Event()

    def _loop():
        while not stop.is_set():
            try:
                conn, _ = srv.accept()
            except (TimeoutError, OSError):
                continue
            conn.close()

    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        stop.set()
        srv.close()
        thread.join(timeout=5)


def _closed_port() -> int:
    """拿一个确定无人监听的端口号。"""
    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    return port


def test_tcp_accept_without_http_is_not_ready():
    """假阳性守卫：连得上但零字节 → 未就绪（这正是 ERR_EMPTY_RESPONSE 的成因）。"""
    with _silent_tcp_server() as port:
        ready, detail = u.wait_http_ready(port, timeout=1.5)
    assert ready is False
    assert "无 HTTP 应答" in detail


def test_http_answer_marks_ready():
    """Jupyter 未带 token 时回 302，属正常应答，必须判为就绪。"""
    with _http_server(status=302) as (port, seen):
        ready, detail = u.wait_http_ready(port, timeout=1.5)
    assert ready is True
    assert "HTTP 302" in detail
    assert seen == [u.UP_READY_PATH]


def test_path_is_configurable():
    with _http_server(status=200) as (port, seen):
        ready, _ = u.wait_http_ready(port, path="/api/status", timeout=1.5)
    assert ready is True
    assert seen == ["/api/status"]


def test_closed_port_times_out_without_raising():
    """超时**不抛异常**：容器确实 Up，调用方要打印指引而非中断。"""
    ready, detail = u.wait_http_ready(_closed_port(), timeout=1.5)
    assert ready is False
    assert "无 HTTP 应答" in detail


def test_progress_callback_fires_during_long_wait(monkeypatch):
    """长窗口期必须有反馈（否则用户面对的是「卡住」的假象）。"""
    monkeypatch.setattr(u, "UP_READY_PROGRESS_S", 0.0)
    waited: list[float] = []
    with _silent_tcp_server() as port:
        ready, _ = u.wait_http_ready(port, timeout=1.5, on_progress=waited.append)
    assert ready is False
    assert waited and waited[0] >= 0.0