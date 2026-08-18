#!/usr/bin/env python3
"""
JupyterLab API 健康测试脚本
=============================
自动测试 JupyterLab 关键 API 接口是否响应正常，纯标准库实现，无需额外依赖。

测试端点:
  1. GET  /           - 根页面（JupyterLab UI 重定向）
  2. GET  /api        - API 版本信息
  3. GET  /api/status - 服务状态
  4. GET  /api/kernels - Kernel 列表
  5. GET  /api/contents - 文件浏览（根目录）
  6. GET  /api/sessions - Session 列表
  7. GET  /api/terminals - Terminal 列表（如启用）
  8. GET  /lab        - JupyterLab UI 页面
  9. POST /api/kernels - 创建 Kernel 并删除（写权限验证）

用法:
  # 容器内运行（默认）
  python test_jupyter_api.py

  # 宿主机运行
  python test_jupyter_api.py --host localhost --port 8888 --token devcontainer123

  # 通过环境变量配置
  JUPYTER_HOST=localhost JUPYTER_PORT=8888 JUPYTER_TOKEN=xxx python test_jupyter_api.py

退出码:
  0 - 所有测试通过
  1 - 有测试失败
"""

import json
import os
import sys
import urllib.request
import urllib.error
import argparse
import time

# ── 颜色输出 ──────────────────────────────────────────────────────────────
class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def ok(msg):   print(f"  {Color.GREEN}[OK]{Color.RESET} {msg}")
def fail(msg): print(f"  {Color.RED}[FAIL]{Color.RESET} {msg}")
def warn(msg): print(f"  {Color.YELLOW}[WARN]{Color.RESET} {msg}")
def info(msg): print(f"  {Color.CYAN}[INFO]{Color.RESET} {msg}")
def header(msg): print(f"\n{Color.BOLD}{Color.CYAN}{msg}{Color.RESET}")

# ── HTTP 工具函数 ──────────────────────────────────────────────────────────
def make_request(base_url, path, token, method="GET", data=None, timeout=10):
    """发起 HTTP 请求，返回 (status_code, body_dict_or_None, error_message)"""
    url = f"{base_url}{path}"
    if token and path.startswith("/api/"):
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}token={token}"

    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, method=method, headers=headers, data=data)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            status = resp.status
            try:
                parsed = json.loads(body)
            except (json.JSONDecodeError, ValueError):
                parsed = None
            return status, parsed, None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            parsed = None
        return e.code, parsed, str(e)
    except urllib.error.URLError as e:
        return 0, None, f"Connection refused: {e.reason}"
    except Exception as e:
        return 0, None, str(e)


# ── 测试用例 ───────────────────────────────────────────────────────────────
class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.failures = []

    def add_pass(self): self.passed += 1
    def add_fail(self, msg):
        self.failed += 1
        self.failures.append(msg)
    def add_warn(self): self.warnings += 1

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{Color.BOLD}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}  Test Summary:{Color.RESET}")
        print(f"    Total:    {total}")
        print(f"    Passed:   {Color.GREEN}{self.passed}{Color.RESET}")
        if self.failed:
            print(f"    Failed:   {Color.RED}{self.failed}{Color.RESET}")
            for f in self.failures:
                print(f"      - {f}")
        if self.warnings:
            print(f"    Warnings: {Color.YELLOW}{self.warnings}{Color.RESET}")
        print(f"{Color.BOLD}{'='*60}{Color.RESET}")
        return self.failed == 0


def test_root_page(base_url, token, result):
    """测试1: 根页面可达"""
    header("1. Root page (GET /)")
    status, body, err = make_request(base_url, "/", token)
    if status == 200 or status == 302:
        ok(f"Root page accessible (HTTP {status})")
        result.add_pass()
    elif err:
        fail(f"Root page unreachable: {err}")
        result.add_fail(f"Root page: {err}")
    else:
        fail(f"Root page returned HTTP {status}")
        result.add_fail(f"Root page: HTTP {status}")


def test_api_version(base_url, token, result):
    """测试2: API 版本端点"""
    header("2. API Version (GET /api)")
    status, body, err = make_request(base_url, "/api", token)
    if status == 200 and body and "version" in body:
        ok(f"Jupyter Server version: {body.get('version', 'unknown')}")
        result.add_pass()
    elif status == 200 and body:
        ok(f"API responding (version field not in response, but HTTP 200)")
        result.add_pass()
    else:
        fail(f"API version check failed: status={status}, err={err}")
        result.add_fail(f"API version: status={status}")


def test_api_status(base_url, token, result):
    """测试3: API 状态端点"""
    header("3. API Status (GET /api/status)")
    status, body, err = make_request(base_url, "/api/status", token)
    if status == 200 and body:
        connections = body.get("connections", "?")
        kernels = body.get("kernels", "?")
        ok(f"Status OK - connections: {connections}, kernels: {kernels}")
        result.add_pass()
    elif status == 200:
        ok(f"Status endpoint responding (HTTP 200)")
        result.add_pass()
    else:
        warn(f"Status endpoint: status={status}, err={err}")
        result.add_warn()


def test_kernels_list(base_url, token, result):
    """测试4: Kernel 列表"""
    header("4. Kernels List (GET /api/kernels)")
    status, body, err = make_request(base_url, "/api/kernels", token)
    if status == 200 and isinstance(body, list):
        ok(f"Kernel list accessible (currently {len(body)} kernels)")
        result.add_pass()
    else:
        fail(f"Kernel list failed: status={status}, err={err}")
        result.add_fail(f"Kernels list: status={status}")


def test_contents(base_url, token, result):
    """测试5: 内容浏览（根目录）"""
    header("5. Contents API (GET /api/contents)")
    status, body, err = make_request(base_url, "/api/contents", token)
    if status == 200 and body and "content" in body:
        name = body.get("name", "/")
        item_count = len(body.get("content", []))
        ok(f"Contents accessible: '{name}' ({item_count} items)")
        result.add_pass()
    elif status == 200 and body:
        ok(f"Contents endpoint responding (HTTP 200)")
        result.add_pass()
    else:
        fail(f"Contents failed: status={status}, err={err}")
        result.add_fail(f"Contents API: status={status}")


def test_sessions(base_url, token, result):
    """测试6: Session 列表"""
    header("6. Sessions List (GET /api/sessions)")
    status, body, err = make_request(base_url, "/api/sessions", token)
    if status == 200 and isinstance(body, list):
        ok(f"Session list accessible (currently {len(body)} sessions)")
        result.add_pass()
    else:
        fail(f"Sessions failed: status={status}, err={err}")
        result.add_fail(f"Sessions list: status={status}")


def test_terminals(base_url, token, result):
    """测试7: Terminal 列表（如果启用）"""
    header("7. Terminals List (GET /api/terminals)")
    status, body, err = make_request(base_url, "/api/terminals", token)
    if status == 200 and isinstance(body, list):
        ok(f"Terminals accessible (currently {len(body)} terminals)")
        result.add_pass()
    elif status == 404:
        warn("Terminals endpoint not available (terminals may be disabled)")
        result.add_warn()
    else:
        warn(f"Terminals endpoint: status={status} (non-critical)")
        result.add_warn()


def test_lab_ui(base_url, token, result):
    """测试8: JupyterLab UI 页面"""
    header("8. JupyterLab UI (GET /lab)")
    status, body, err = make_request(base_url, "/lab", token)
    if status == 200:
        ok(f"JupyterLab UI accessible (HTTP 200)")
        result.add_pass()
    elif status == 302:
        ok(f"JupyterLab UI redirecting (HTTP 302 - normal)")
        result.add_pass()
    else:
        fail(f"JupyterLab UI failed: status={status}, err={err}")
        result.add_fail(f"Lab UI: status={status}")


def test_kernel_create_delete(base_url, token, result):
    """测试9: 创建并删除 Kernel（写权限验证）"""
    header("9. Kernel Create+Delete (POST/DELETE /api/kernels)")
    # 创建 kernel
    status, body, err = make_request(base_url, "/api/kernels", token, method="POST", data={"name": "python3"})
    if status in (200, 201) and body and "id" in body:
        kernel_id = body["id"]
        kernel_name = body.get("name", "python3")
        ok(f"Kernel created: {kernel_name} (id={kernel_id[:8]}...)")

        # 等待 kernel 启动
        time.sleep(2)

        # 删除 kernel
        del_status, _, del_err = make_request(base_url, f"/api/kernels/{kernel_id}", token, method="DELETE")
        if del_status in (200, 204):
            ok(f"Kernel deleted successfully (write permissions verified)")
            result.add_pass()
        else:
            warn(f"Kernel created but delete returned HTTP {del_status}: {del_err}")
            # 尝试清理
            make_request(base_url, f"/api/kernels/{kernel_id}", token, method="DELETE")
            result.add_warn()
    else:
        warn(f"Kernel creation skipped: status={status}, err={err} (may require additional config)")
        result.add_warn()


# ── 主函数 ─────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="JupyterLab API Health Test")
    parser.add_argument("--host", default=os.environ.get("JUPYTER_HOST", "127.0.0.1"),
                        help="Jupyter host (default: 127.0.0.1 or JUPYTER_HOST env)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("JUPYTER_PORT", "8888")),
                        help="Jupyter port (default: 8888 or JUPYTER_PORT env)")
    parser.add_argument("--token", default=os.environ.get("JUPYTER_TOKEN", ""),
                        help="Jupyter token (default: JUPYTER_TOKEN env or empty)")
    parser.add_argument("--protocol", default=os.environ.get("JUPYTER_PROTOCOL", "http"),
                        help="Protocol (http/https, default: http)")
    args = parser.parse_args()

    base_url = f"{args.protocol}://{args.host}:{args.port}"

    print(f"{Color.BOLD}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}  JupyterLab API Health Test{Color.RESET}")
    print(f"  Target: {base_url}")
    print(f"  Token:  {'*'*8}{args.token[-4:] if len(args.token) > 4 else '(empty)' if not args.token else '(set)'}")
    print(f"{Color.BOLD}{'='*60}{Color.RESET}")

    result = TestResult()
    tests = [
        test_root_page,
        test_api_version,
        test_api_status,
        test_kernels_list,
        test_contents,
        test_sessions,
        test_terminals,
        test_lab_ui,
        test_kernel_create_delete,
    ]

    for test_fn in tests:
        try:
            test_fn(base_url, args.token, result)
        except Exception as e:
            fail(f"Test {test_fn.__name__} raised exception: {e}")
            result.add_fail(f"{test_fn.__name__}: {e}")

    success = result.summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
