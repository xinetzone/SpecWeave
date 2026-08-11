#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""demo_async_polling_podcast.py

可运行测试脚本：把「AI 播客自动生成」实战示例（api-integration-worked-example.md）整理成
一个零外部依赖（仅标准库）的端到端测试。

它用一个内置的 HTTP mock 服务器模拟异步播客 API，忠实复现四个通用 API 集成模式：
  1. @file 传长文本请求体（submit 时把 sources 写入临时 JSON 文件再提交）
  2. 异步接口「两段式」：前台 POST 提交取 episodeId + 后台轮询 processStatus
  3. 错误处理与重试：HTTP 429 退避、5xx 重试、应用错误码（21007/25429）判断
  4. 交互式参数收集：AskUserQuestion 属于智能体工具，脚本内以参数/配置项接收
     （对应实战示例中"由 AskUserQuestion 收集后传入"的环节）

直接运行：
    python demo_async_polling_podcast.py

运行后会执行 6 个场景（成功/失败/超时/429退避/5xx重试/无效Key），逐个打印 PASS/FAIL，
全部通过则退出码 0，任一失败则退出码 1。无需真实 API Key，无需联网。

关联知识条目：SpecWeave/.agents/docs/knowledge/best-practices/api-integration-worked-example.md
及 api-async-polling-pattern / api-error-handling-retry-strategy / api-long-text-file-parameter
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ---------------------------------------------------------------------------
# 测试参数（缩短真实值以保证秒级完成；真实生产请用示例文档中的值）
# ---------------------------------------------------------------------------
POLL_INTERVAL = 0.1          # 轮询间隔（示例默认 10s，测试缩短）
MAX_POLLS = 8                # 最大轮询次数
RATE_LIMIT_RETRIES = 3       # 429 限流最多退避重试次数
RATE_LIMIT_BACKOFF = 0.2     # 429 退避基础时长（示例 15s）
SERVER_ERROR_RETRIES = 3     # 5xx 最多重试 3 次
SERVER_ERROR_INTERVAL = 0.2  # 5xx 重试间隔（示例 5s）
NETWORK_ERROR_RETRIES = 3    # 网络错误重试 3 次
API_KEY = "test-api-key"     # 仅测试占位，不涉及真实密钥
X_SOURCE = "skills"


# ---------------------------------------------------------------------------
# 业务异常
# ---------------------------------------------------------------------------
class ApiError(Exception):
    """携带 HTTP 状态码与应用错误码的业务异常。"""

    def __init__(self, http_code: int, app_code: int, message: str = ""):
        super().__init__(message or f"HTTP {http_code} / code {app_code}")
        self.http_code = http_code
        self.app_code = app_code


# ---------------------------------------------------------------------------
# 模拟异步播客 API（Mock Server）
# ---------------------------------------------------------------------------
# 场景基础配置（复位基准，避免上一场景的字段残留污染后续场景）
_BASE_SCENARIO = {
    "poll_before_success": 2,   # GET 前 2 次返回 pending，之后 success
    "fail_after": None,         # 若设 n：GET 第 n 次返回 failed
    "always_pending": False,    # 若 True：永远 pending（触发超时）
    "rate_limits_first_n": 0,   # 若 >0：GET 前 n 次返回 HTTP 429
    "server_errors_first_n": 0, # 若 >0：GET 前 n 次返回 HTTP 500
}


class MockPodcastAPI(BaseHTTPRequestHandler):
    """模拟 ListenHub 风格的异步生成接口。

    scenario 通过类属性注入（基于 _BASE_SCENARIO 复位后 update）。默认行为：
    POST 返回 episodeId，GET 轮询若干次后返回 success。鉴权头必须匹配 API_KEY，
    否则返回 401 + code 21007（Key 无效）。
    """

    scenario = dict(_BASE_SCENARIO)
    poll_count = 0

    def log_message(self, *args):  # 静默，避免测试输出噪声
        pass

    def _send_json(self, http_code: int, body: dict) -> None:
        data = json.dumps(body).encode("utf-8")
        self.send_response(http_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _reject_unauthorized(self) -> bool:
        """鉴权失败时返回 401 + code 21007，返回 True；通过返回 False。"""
        if self.headers.get("Authorization") == f"Bearer {API_KEY}":
            return False
        self._send_json(401, {"code": 21007, "message": "invalid api key", "data": {}})
        return True

    def do_POST(self):
        if self._reject_unauthorized():
            return
        # 模拟 @file 提交：读取请求体（含长文本 sources）
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        payload = json.loads(body)
        assert payload.get("sources"), "sources 不能为空"
        assert payload.get("speakers"), "speakers 不能为空"
        self._send_json(200, {"code": 0, "message": "", "data": {"episodeId": "ep-001"}})

    def do_GET(self):
        if self._reject_unauthorized():
            return

        s = MockPodcastAPI.scenario
        MockPodcastAPI.poll_count += 1
        n = MockPodcastAPI.poll_count

        if s["server_errors_first_n"] > 0 and n <= s["server_errors_first_n"]:
            self._send_json(500, {"code": 0, "message": "server error", "data": {}})
            return
        if s["rate_limits_first_n"] > 0 and n <= s["rate_limits_first_n"]:
            self._send_json(429, {"code": 25429, "message": "rate limited", "data": {}})
            return
        if s["always_pending"]:
            self._send_json(200, {"code": 0, "message": "", "data": {"processStatus": "pending"}})
            return
        if s["fail_after"] is not None and n == s["fail_after"]:
            self._send_json(200, {"code": 0, "message": "", "data": {"processStatus": "failed"}})
            return
        if n <= s["poll_before_success"]:
            self._send_json(200, {"code": 0, "message": "", "data": {"processStatus": "pending"}})
            return
        self._send_json(200, {"code": 0, "message": "", "data": {"processStatus": "success",
                                                                "audioUrl": "https://example.com/audio.mp3"}})


# ---------------------------------------------------------------------------
# API 客户端：复现四个模式
# ---------------------------------------------------------------------------
class PodcastClient:
    """把实战示例的 Bash 逻辑移植为 Python，完整覆盖四个模式。"""

    def __init__(self, base_url: str, api_key: str = API_KEY):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    # -- 模式② @file 长文本 + 模式③a 前台提交 -----------------------------
    def submit_episode(self, speakers: list, language: str, mode: str, sources: list) -> str:
        payload = {
            "speakers": [{"speakerId": sid} for sid in speakers],
            "language": language,
            "mode": mode,
            "sources": sources,  # 长文本在此，写入临时文件
        }
        # 用 @file 传长文本：写入临时 JSON 文件，curl 用 -d @file 读取
        fd, path = tempfile.mkstemp(suffix=".json", prefix="lh-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f)
            with open(path, "rb") as data:
                resp = self._request("POST", f"{self.base_url}/podcast/episodes", data=data.read(),
                                     content_type="application/json")
        finally:
            os.unlink(path)  # 用后清理临时文件
        return resp["data"]["episodeId"]

    # -- 模式③b 后台轮询 + 模式④ 错误处理与重试 ------------------------------
    def wait_episode(self, episode_id: str) -> dict:
        url = f"{self.base_url}/podcast/episodes/{episode_id}"
        for _ in range(MAX_POLLS):
            resp = self._request("GET", url)
            status = (resp.get("data") or {}).get("processStatus", "pending")
            if status in ("success", "completed"):
                return {"status": "success", "episodeId": episode_id, "data": resp["data"]}
            if status in ("failed", "error"):
                return {"status": "failed", "episodeId": episode_id, "data": resp["data"]}
            time.sleep(POLL_INTERVAL)
        return {"status": "timeout", "episodeId": episode_id}

    # -- 底层请求：HTTP/应用错误码分级 + 各类错误独立预算重试 -----------------
    def _request(self, method: str, url: str, data: bytes | None = None,
                 content_type: str | None = None) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Source": X_SOURCE,
        }
        if content_type:
            headers["Content-Type"] = content_type

        # 429、5xx、网络错误分别持有独立重试预算，互不挤占；预算耗尽即抛 ApiError
        rate_budget = RATE_LIMIT_RETRIES
        server_budget = SERVER_ERROR_RETRIES
        network_budget = NETWORK_ERROR_RETRIES

        while True:
            try:
                req = urllib.request.Request(url, data=data, headers=headers, method=method)
                with urllib.request.urlopen(req) as r:
                    raw = r.read()
                body = json.loads(raw.decode("utf-8"))
            except urllib.error.HTTPError as e:
                raw = e.read() if hasattr(e, "read") else b""
                try:
                    body = json.loads(raw.decode("utf-8")) if raw else {}
                except json.JSONDecodeError:
                    body = {}
                app_code = body.get("code", 0)
                if e.code == 429 or app_code == 25429:      # 限流 → 独立退避预算
                    if rate_budget <= 0:
                        raise ApiError(e.code, app_code, body.get("message", ""))
                    rate_budget -= 1
                    time.sleep(RATE_LIMIT_BACKOFF)
                    continue
                if e.code >= 500:                            # 5xx → 独立重试预算
                    if server_budget <= 0:
                        raise ApiError(e.code, app_code, body.get("message", ""))
                    server_budget -= 1
                    time.sleep(SERVER_ERROR_INTERVAL)
                    continue
                raise ApiError(e.code, app_code, body.get("message", ""))
            except urllib.error.URLError:                    # 网络错误 → 独立重试预算
                if network_budget <= 0:
                    raise ApiError(0, -1, "network retries exhausted")
                network_budget -= 1
                continue

            # HTTP 200 但应用错误码非 0
            code = body.get("code", 0)
            if code == 25429:                                # 应用层限流 → 独立退避预算
                if rate_budget <= 0:
                    raise ApiError(200, 25429, "rate limited")
                rate_budget -= 1
                time.sleep(RATE_LIMIT_BACKOFF)
                continue
            if code == 21007:                                # Key 无效 → 不重试
                raise ApiError(200, 21007, "invalid api key")
            return body


# ---------------------------------------------------------------------------
# 测试场景
# ---------------------------------------------------------------------------
def _reset():
    MockPodcastAPI.scenario = dict(_BASE_SCENARIO)  # 复位到基础配置，避免字段残留
    MockPodcastAPI.poll_count = 0


def _run_scenario(server, name: str, scenario: dict, expected: str,
                  api_key: str = API_KEY) -> bool:
    _reset()
    MockPodcastAPI.scenario.update(scenario)
    base = f"http://127.0.0.1:{server.server_port}"
    client = PodcastClient(base, api_key=api_key)
    try:
        ep = client.submit_episode(["cozy-man-english"], "en", "story",
                                   [{"type": "text", "content": "A very long article text..." * 200}])
        result = client.wait_episode(ep)
    except ApiError as e:                                  # 重试预算耗尽等 → 记为 error
        result = {"status": "error", "detail": f"HTTP {e.http_code} / code {e.app_code}"}
    ok = result["status"] == expected
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: status={result['status']} (期望 {expected})")
    return ok


def run_all(server) -> bool:
    results = []
    # 场景1：正常成功（轮询 2 次 pending 后 success）
    results.append(_run_scenario(server, "成功路径（轮询后完成）", {"poll_before_success": 2}, "success"))
    # 场景2：失败（第 3 次轮询返回 failed）
    results.append(_run_scenario(server, "失败路径", {"poll_before_success": 99, "fail_after": 3}, "failed"))
    # 场景3：超时（永远 pending）
    results.append(_run_scenario(server, "超时路径", {"always_pending": True}, "timeout"))
    # 场景4：HTTP 429 限流退避后成功
    results.append(_run_scenario(server, "429 限流退避后成功",
                                 {"poll_before_success": 3, "rate_limits_first_n": 2}, "success"))
    # 场景5：5xx 服务端错误重试后成功
    results.append(_run_scenario(server, "5xx 重试后成功",
                                 {"poll_before_success": 3, "server_errors_first_n": 2}, "success"))
    # 场景6：无效 Key（mock 返回 401 + 21007，不重试 → error）
    results.append(_run_scenario(server, "无效 Key 不重试", {"poll_before_success": 2}, "error",
                                 api_key="wrong-key"))

    passed = sum(results)
    total = len(results)
    print(f"\n结果: {passed}/{total} 通过")
    return passed == total


class _QuietServer(ThreadingHTTPServer):
    daemon_threads = True


@contextmanager
def _running_server():
    server = _QuietServer(("127.0.0.1", 0), MockPodcastAPI)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()


def main() -> int:
    with _running_server() as server:
        return 0 if run_all(server) else 1


if __name__ == "__main__":
    sys.exit(main())
