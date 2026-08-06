#!/usr/bin/env python3
"""SaaS云文档内容提取CLI（飞书/钉钉/企微等）。

基于lib.saas_doc_extractor共享库，原feishu-doc-extract.py重构为多平台通用CLI。

使用方式：
  python feishu-doc-extract.py <url> [--output dir] [--cookies file] [--headless] [--platform feishu|dingtalk|wecom|...]

示例：
  python feishu-doc-extract.py https://bytedance.larkoffice.com/wiki/xxx
  python feishu-doc-extract.py https://feishu.cn/docx/xxx --output ./extracted --cookies cookies.json
  python feishu-doc-extract.py https://xxx.feishu.cn/docx/xxx --headless -v
  python feishu-doc-extract.py https://alidocs.dingtalk.com/xxx --platform dingtalk
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("错误：需要安装playwright。请运行：pip install playwright && playwright install chromium", file=sys.stderr)
    sys.exit(1)

from lib.cli import print_pass, print_warn, print_error
from lib.saas_doc_extractor import (
    ExtractionConfig,
    CONTENT_MIN_CHARS,
    CONTENT_MIN_LINES,
    EMPTY_LINE_RATIO_THRESHOLD,
    detect_platform,
    extract_urls,
    get_platform_config,
    list_supported_platforms,
    SaasDocExtractor,
)


def extract_doc(
    url: str,
    output_dir: Optional[Path] = None,
    cookies_file: Optional[Path] = None,
    headless: bool = False,
    platform_name: Optional[str] = None,
    scroll_step: Optional[int] = None,
    wait_ms: Optional[int] = None,
    initial_wait_ms: Optional[int] = None,
    max_iterations: Optional[int] = None,
    bidirectional: bool = True,
    verbose: bool = False,
):
    """提取单个SaaS云文档（多平台通用入口）。"""
    # 检测平台
    detected = detect_platform(url)
    if platform_name:
        if detected and detected != platform_name:
            print_warn(f"URL检测为{detected}，但手动指定为{platform_name}，使用手动指定")
        pname = platform_name
    elif detected:
        pname = detected
    else:
        pname = 'feishu'
        print_warn(f"无法自动识别URL所属平台，默认使用feishu。可用平台：{[n for n,_,_ in list_supported_platforms()]}")

    platform_cfg = get_platform_config(pname)
    if not platform_cfg:
        print_error(f"未知平台: {pname}")
        print_error(f"支持平台: {[n for n,_,_ in list_supported_platforms()]}")
        sys.exit(1)

    config_kwargs = {"verbose": verbose, "bidirectional_scan": bidirectional}
    if scroll_step is not None:
        config_kwargs["scroll_step"] = scroll_step
    if wait_ms is not None:
        config_kwargs["wait_ms"] = wait_ms
    if initial_wait_ms is not None:
        config_kwargs["initial_wait_ms"] = initial_wait_ms
    if max_iterations is not None:
        config_kwargs["max_iterations"] = max_iterations
    extraction_cfg = ExtractionConfig(**config_kwargs)

    extractor = SaasDocExtractor(platform_cfg, extraction_cfg)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})

        if cookies_file and cookies_file.exists():
            cookies = json.loads(cookies_file.read_text(encoding='utf-8'))
            context.add_cookies(cookies)
            if verbose:
                print(f"  [INFO] 已加载cookies: {cookies_file}")

        page = context.new_page()

        if verbose:
            print(f"  [INFO] 导航到{platform_cfg.display_name}: {url}")
        try:
            page.goto(url, wait_until='networkidle', timeout=30000)
        except PlaywrightTimeout:
            from lib.saas_doc_extractor import ExtractionResult
            result = ExtractionResult(url=url, platform=pname)
            result.errors.append("页面加载超时，请检查URL是否正确和网络连接")
            browser.close()
            return result

        # 执行提取（核心逻辑在SaasDocExtractor中）
        result = extractor.extract(page, url)
        browser.close()

    # 提取URLs（JS端innerText中已包含，Python端二次提取兼容fallback）
    if result.content:
        result.urls_found = extract_urls(result.content)

    # 保存输出
    if output_dir and result.success:
        output_dir.mkdir(parents=True, exist_ok=True)
        title_slug = re.sub(r'[^\w\u4e00-\u9fff-]', '-', result.title)[:50].strip('-')
        if not title_slug:
            title_slug = f'{pname}-doc'
        output_file = output_dir / f"{title_slug}.txt"
        output_file.write_text(result.content, encoding='utf-8')

        meta_file = output_dir / f"{title_slug}.meta.json"
        meta = result.to_meta_dict(extractor.cfg)
        meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')

        if verbose:
            print_pass(f"已保存: {output_file}")
            print_pass(f"元数据: {meta_file}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description='SaaS云文档内容提取工具（支持飞书/钉钉/企微/语雀/Notion/Confluence/石墨/WPS）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python feishu-doc-extract.py https://bytedance.larkoffice.com/wiki/xxx
  python feishu-doc-extract.py https://feishu.cn/docx/xxx --output ./extracted
  python feishu-doc-extract.py https://alidocs.dingtalk.com/xxx --platform dingtalk -v
  python feishu-doc-extract.py <url> --no-bidirectional -v
        """
    )
    parser.add_argument('url', nargs='?', help='文档URL')
    parser.add_argument('--output', '-o', type=Path, help='输出目录')
    parser.add_argument('--cookies', '-c', type=Path, help='cookies JSON文件路径（用于认证）')
    parser.add_argument('--headless', action='store_true', help='无头模式（默认有界面）')
    parser.add_argument('--platform', '-p', type=str, default=None,
                        help=f'手动指定平台（{[n for n,_,_ in list_supported_platforms()]}，默认自动检测）')
    parser.add_argument('--scroll-step', type=int, default=None,
                        help='滚动步长(px)，默认使用平台推荐值(飞书400)')
    parser.add_argument('--wait-ms', type=int, default=None,
                        help='每步等待时间(ms)，默认使用平台推荐值(飞书1500)')
    parser.add_argument('--initial-wait-ms', type=int, default=None,
                        help='初始加载等待(ms)，默认使用平台推荐值(飞书2000)')
    parser.add_argument('--max-iterations', type=int, default=None,
                        help='最大滚动迭代次数，默认30')
    parser.add_argument('--no-bidirectional', action='store_true',
                        help='禁用双向扫描（更快但可能遗漏虚拟滚动回收内容）')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--list-platforms', action='store_true', help='列出所有支持的平台并退出')

    args = parser.parse_args()

    if args.list_platforms:
        print("支持的平台：")
        for name, display, verified in list_supported_platforms():
            status = "✓ 已验证" if verified else "○ 候选配置"
            print(f"  {name:12s} ({display:8s}) {status}")
        return 0

    if not args.url:
        parser.error("缺少url参数")

    result = extract_doc(
        url=args.url,
        output_dir=args.output,
        cookies_file=args.cookies,
        headless=args.headless,
        platform_name=args.platform,
        scroll_step=args.scroll_step,
        wait_ms=args.wait_ms,
        initial_wait_ms=args.initial_wait_ms,
        max_iterations=args.max_iterations,
        bidirectional=not args.no_bidirectional,
        verbose=args.verbose,
    )

    # 输出结果摘要
    print()
    print("=" * 60)
    if result.success:
        print_pass("提取成功！")
    else:
        print_error("提取失败！")

    print(f"  平台: {result.platform}")
    if result.title:
        print(f"  标题: {result.title}")
    print(f"  字符数: {result.char_count}")
    print(f"  行数: {result.line_count}")
    print(f"  URL数: {len(result.urls_found)}")
    print(f"  滚动迭代: {result.scroll_iterations}")
    print(f"  耗时: {result.extraction_time_ms}ms")
    if result.used_fallback_container or result.used_fallback_line:
        print_warn(f"  使用了fallback选择器: container={result.container_selector_used}, line={result.line_selector_used}")

    for err in result.errors:
        print_error(f"  [错误] {err}")
    for w in result.warnings:
        print_warn(f"  [警告] {w}")

    if args.verbose and result.lines:
        print("\n内容预览（前5行）：")
        for i, line in enumerate(result.lines[:5]):
            print(f"  {i+1}. {line[:80]}")

    return 0 if result.success else 1


if __name__ == '__main__':
    sys.exit(main())
