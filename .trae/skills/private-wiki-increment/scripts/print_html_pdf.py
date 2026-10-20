# -*- coding: utf-8 -*-
"""Playwright Chromium 无头打印 HTML -> PDF（A4，无页边距，带背景）。

为什么不用 Edge：本机安全层会拦截 Edge 启动时写系统账户缓存（OneAuth/
TokenBroker 等），即便非沙箱执行也报 hit restricted。Playwright 自带
Chromium 不碰这些路径。

用法:
    python print_html_pdf.py <input.html> <output.pdf>

前置（一次性）:
    python -m playwright install chromium
若 chrome-headless-shell 可执行体缺失（INSTALLATION_COMPLETE 标记在但 exe
不在，本机曾出现），脚本自动回退到完整版 chrome-win64/chrome.exe。
"""
import glob
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def resolve_chromium_exe() -> str | None:
    """优先完整版 Chrome for Testing（headless-shell 曾解压不全）。"""
    base = os.path.expandvars(r"%LOCALAPPDATA%\ms-playwright")
    candidates = sorted(
        glob.glob(os.path.join(base, "chromium-*", "chrome-win64", "chrome.exe")),
        reverse=True,
    )
    return candidates[0] if candidates else None


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: print_html_pdf.py <input.html> <output.pdf>", file=sys.stderr)
        return 2

    src = Path(sys.argv[1]).resolve()
    dst = Path(sys.argv[2]).resolve()
    if not src.is_file():
        print(f"input not found: {src}", file=sys.stderr)
        return 2
    dst.parent.mkdir(parents=True, exist_ok=True)

    launch_kwargs: dict = {"headless": True}
    exe = resolve_chromium_exe()
    if exe:
        launch_kwargs["executable_path"] = exe
        print(f"chromium: {exe}")
    else:
        print("chromium: playwright default (run `python -m playwright install chromium` if missing)")

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        page = browser.new_page()
        page.goto(src.as_uri(), wait_until="networkidle")
        page.emulate_media(media="print")
        page.pdf(
            path=str(dst),
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        browser.close()

    print(f"written: {dst} ({dst.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
