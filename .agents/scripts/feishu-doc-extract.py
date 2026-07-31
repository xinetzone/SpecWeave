#!/usr/bin/env python3
"""飞书云文档内容提取脚本 - 遵循feishu-doc-dom-extraction模式。

功能：
- 使用Playwright自动登录（需预先配置cookies或已登录的browser context）
- 自动定位.bear-web-x-container滚动容器和.ace-line文本行
- 分段滚动+去重保序提取完整正文
- 反模式检查：验证选择器可用性、内容完整性、链接保留度
- 输出纯文本和元数据报告
- 遵循feishu-doc-dom-extraction模式的所有反模式防护

使用方式：
  python feishu-doc-extract.py <url> [--output dir] [--cookies file] [--headless]

前置条件：
  pip install playwright
  playwright install chromium
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeout
except ImportError:
    print("错误：需要安装playwright。请运行：pip install playwright && playwright install chromium", file=sys.stderr)
    sys.exit(1)

from lib.cli import print_pass, print_warn, print_error, print_info


# === 提取参数（基于实测验证的最优值）===
DEFAULT_SCROLL_STEP = 400       # 每次滚动像素（实测600px可能导致长段落截断）
DEFAULT_WAIT_MS = 1500          # 每步等待渲染时间（毫秒）
DEFAULT_MAX_NO_NEW = 3          # 连续无新内容次数阈值
DEFAULT_MAX_ITERATIONS = 30     # 最大滚动迭代次数（安全限制）
CONTENT_MIN_LINES = 10          # 最小有效行数阈值
CONTENT_MIN_CHARS = 200         # 最小有效字符数阈值
URL_PATTERN = re.compile(r'https?://[^\s\u200b\）\)】}]+')


@dataclass
class ExtractionResult:
    """飞书文档提取结果"""
    url: str
    title: str = ""
    content: str = ""
    lines: list[str] = field(default_factory=list)
    urls_found: list[str] = field(default_factory=list)
    scroll_iterations: int = 0
    total_scroll_height: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    anti_pattern_checks: dict = field(default_factory=dict)
    extraction_time_ms: int = 0

    @property
    def char_count(self) -> int:
        return len(self.content)

    @property
    def line_count(self) -> int:
        return len(self.lines)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0 and self.char_count >= CONTENT_MIN_CHARS


class FeishuExtractor:
    """飞书云文档提取器，集成反模式检查"""

    # 反模式1：使用window滚动而非容器滚动
    # 反模式2：一次滚到底部
    # 反模式3：使用标准HTML标签选择器
    # 反模式4：不做去重
    # 反模式5：source字段使用衍生URL
    CONTAINER_SELECTOR = '.bear-web-x-container'
    LINE_SELECTOR = '.ace-line'

    def __init__(
        self,
        scroll_step: int = DEFAULT_SCROLL_STEP,
        wait_ms: int = DEFAULT_WAIT_MS,
        max_no_new: int = DEFAULT_MAX_NO_NEW,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        verbose: bool = False,
    ):
        self.scroll_step = scroll_step
        self.wait_ms = wait_ms
        self.max_no_new = max_no_new
        self.max_iterations = max_iterations
        self.verbose = verbose

    def extract(self, page: Page, url: str) -> ExtractionResult:
        """执行完整提取流程"""
        result = ExtractionResult(url=url)
        start_time = time.time()

        # Step 1: 导航到页面
        print_info(f"导航到飞书文档: {url}")
        try:
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(2000)
        except PlaywrightTimeout:
            result.errors.append("页面加载超时，请检查URL是否正确和网络连接")
            return result

        # Step 2: 反模式检查 - 验证容器选择器可用性
        self._check_container(page, result)
        if result.errors:
            return result

        # Step 3: 提取标题
        self._extract_title(page, result)

        # Step 4: 分段滚动提取（向下）
        self._scroll_and_collect(page, result, direction='down')

        # Step 5: 反模式检查 - 双向扫描验证（回到顶部再向下做二次扫描补全）
        if not self._check_content_completeness(result):
            print_warn("首次提取内容可能不完整，执行二次扫描...")
            self._scroll_and_collect(page, result, direction='up')
            page.evaluate(f"() => {{ const c = document.querySelector('{self.CONTAINER_SELECTOR}'); c.scrollTop = 0; }}")
            page.wait_for_timeout(self.wait_ms)
            self._scroll_and_collect(page, result, direction='down')

        # Step 6: 反模式检查 - 链接保留验证
        self._check_urls_preserved(page, result)

        # Step 7: 反模式检查 - 内容阈值验证
        self._check_content_thresholds(result)

        # Step 8: 拼接最终内容
        result.content = '\n'.join(result.lines)
        result.extraction_time_ms = int((time.time() - start_time) * 1000)

        return result

    def _check_container(self, page: Page, result: ExtractionResult):
        """反模式检查：验证滚动容器和文本行选择器可用性"""
        checks = {}

        # 检查容器是否存在
        container_exists = page.evaluate(f"() => !!document.querySelector('{self.CONTAINER_SELECTOR}')")
        checks['container_exists'] = container_exists
        if not container_exists:
            result.errors.append(
                f"未找到滚动容器 '{self.CONTAINER_SELECTOR}'。"
                "可能原因：页面未完全加载、飞书更新了DOM结构、不是飞书文档页面、需要登录认证。"
            )
            result.anti_pattern_checks = checks
            return

        # 获取容器信息
        container_info = page.evaluate(f"""() => {{
            const c = document.querySelector('{self.CONTAINER_SELECTOR}');
            return {{
                tag: c.tagName,
                scrollHeight: c.scrollHeight,
                clientHeight: c.clientHeight,
                className: c.className.substring(0, 100)
            }};
        }}""")
        checks['container_info'] = container_info
        result.total_scroll_height = container_info['scrollHeight']

        if self.verbose:
            print_info(f"  容器: {container_info['tag']}, 滚动高度: {container_info['scrollHeight']}px, 可见高度: {container_info['clientHeight']}px")

        # 反模式检查：容器是否可滚动
        if container_info['scrollHeight'] <= container_info['clientHeight']:
            result.warnings.append(
                f"容器scrollHeight({container_info['scrollHeight']}) <= clientHeight({container_info['clientHeight']})，"
                "内容可能无需滚动即可完整显示，或页面未完全渲染"
            )
            checks['container_scrollable'] = False
        else:
            checks['container_scrollable'] = True

        # 检查初始.ace-line
        initial_lines = page.evaluate(f"() => document.querySelectorAll('{self.LINE_SELECTOR}').length")
        checks['initial_ace_lines'] = initial_lines
        if initial_lines == 0:
            result.warnings.append(
                f"初始状态下未找到任何 '{self.LINE_SELECTOR}' 元素。"
                "可能需要等待更长时间让内容渲染，或飞书更新了文本行class名。"
            )
        elif self.verbose:
            print_info(f"  初始可见文本行: {initial_lines}")

        # 反模式检查：检测是否误用了body/window滚动
        body_scrollable = page.evaluate("() => document.body.scrollHeight > window.innerHeight + 100")
        checks['body_scrollable'] = body_scrollable

        result.anti_pattern_checks = checks

    def _extract_title(self, page: Page, result: ExtractionResult):
        """提取文档标题"""
        # 优先从.ace-line第一个元素获取标题
        title = page.evaluate(f"""() => {{
            const lines = document.querySelectorAll('{self.LINE_SELECTOR}');
            return lines.length > 0 ? lines[0].innerText?.trim() : '';
        }}""")
        if title:
            result.title = title.replace('\u200b', '').strip()
        else:
            # fallback: document.title
            result.title = page.title().replace(' - 飞书云文档', '').strip()
            result.warnings.append("从.ace-line获取标题失败，使用document.title作为fallback")

        if self.verbose:
            print_info(f"  文档标题: {result.title}")

    def _scroll_and_collect(self, page: Page, result: ExtractionResult, direction: str = 'down'):
        """核心提取逻辑：分段滚动+去重保序收集。

        反模式防护：
        - 使用container.scrollTop而非window.scrollTo（反模式1）
        - 分段滚动而非一次到底（反模式2）
        - 使用.ace-line选择器而非h1/p等标准标签（反模式3）
        - Set去重而非直接拼接（反模式4）
        """
        collected = set(result.lines)  # 用已有内容初始化
        ordered = list(result.lines)
        no_new_count = 0
        step = self.scroll_step if direction == 'down' else -self.scroll_step

        if direction == 'up':
            # 向上滚动时先到当前位置的上方
            current_top = page.evaluate(f"() => document.querySelector('{self.CONTAINER_SELECTOR}').scrollTop")
            page.evaluate(f"() => {{ const c = document.querySelector('{self.CONTAINER_SELECTOR}'); c.scrollTop = {max(0, current_top - 500)}; }}")
            page.wait_for_timeout(self.wait_ms)

        for i in range(self.max_iterations):
            # 收集当前可见的文本行（使用container.querySelectorAll而非document，避免UI噪音）
            new_lines = page.evaluate(f"""() => {{
                const c = document.querySelector('{self.CONTAINER_SELECTOR}');
                if (!c) return [];
                return Array.from(c.querySelectorAll('{self.LINE_SELECTOR}'))
                    .map(el => el.innerText?.trim())
                    .filter(t => t && t.length > 0);
            }}""")

            new_count = 0
            for line in new_lines:
                clean_line = line.replace('\u200b', '').strip()
                if clean_line and clean_line not in collected:
                    collected.add(clean_line)
                    if direction == 'down':
                        ordered.append(clean_line)
                    else:
                        ordered.insert(0, clean_line)
                    new_count += 1

            result.scroll_iterations += 1

            # 判断是否继续
            if new_count == 0:
                no_new_count += 1
            else:
                no_new_count = 0
                if self.verbose:
                    print_info(f"  {direction} 迭代{i+1}: +{new_count}行, 总计{len(ordered)}行")

            if no_new_count >= self.max_no_new:
                if self.verbose:
                    print_info(f"  连续{self.max_no_new}次无新内容，停止滚动")
                break

            # 检查是否到达边界
            at_boundary = page.evaluate(f"""() => {{
                const c = document.querySelector('{self.CONTAINER_SELECTOR}');
                if ('{direction}' === 'down') {{
                    return c.scrollTop + c.clientHeight >= c.scrollHeight - 10;
                }} else {{
                    return c.scrollTop <= 10;
                }}
            }}""")
            if at_boundary:
                break

            # 滚动一步
            page.evaluate(f"""() => {{
                const c = document.querySelector('{self.CONTAINER_SELECTOR}');
                c.scrollTop += {step};
            }}""")
            page.wait_for_timeout(self.wait_ms)

        result.lines = ordered
        result.anti_pattern_checks[f'{direction}_pass_iterations'] = i + 1 if 'i' in dir() else 0

    def _check_urls_preserved(self, page: Page, result: ExtractionResult):
        """反模式检查：链接保留验证

        验证提取的文本中是否包含URL（飞书文档中的链接通常以内嵌文本形式保留在.ace-line的innerText中）
        """
        full_text = '\n'.join(result.lines)
        urls = URL_PATTERN.findall(full_text)
        result.urls_found = list(set(urls))  # 去重

        checks = {
            'urls_found_count': len(result.urls_found),
            'urls_found': result.urls_found[:20],  # 最多记录20个
        }

        # 检查页面中实际存在的链接数
        page_link_count = page.evaluate(f"""() => {{
            const c = document.querySelector('{self.CONTAINER_SELECTOR}');
            return c ? c.querySelectorAll('a[href]').length : 0;
        }}""")
        checks['page_link_elements'] = page_link_count

        if page_link_count > 0 and len(result.urls_found) == 0:
            result.warnings.append(
                f"页面中检测到{page_link_count}个链接元素，但提取文本中未发现URL。"
                "可能原因：链接使用了特殊渲染方式（如飞书卡片链接），需手动检查。"
            )
        elif self.verbose:
            print_info(f"  提取到URL: {len(result.urls_found)}个")

        result.anti_pattern_checks.update(checks)

    def _check_content_completeness(self, result: ExtractionResult) -> bool:
        """简单内容完整性启发式检查"""
        if len(result.lines) < CONTENT_MIN_LINES:
            return False
        if result.char_count < CONTENT_MIN_CHARS:
            return False
        # 检查是否包含常见的文档结构词
        content = result.content
        structure_markers = ['什么是', '如何', '参与', '方向', '链接', 'http']
        found_markers = sum(1 for m in structure_markers if m in content)
        return found_markers >= 2

    def _check_content_thresholds(self, result: ExtractionResult):
        """反模式检查：内容阈值验证"""
        checks = {}

        # 最小行数检查
        if result.line_count < CONTENT_MIN_LINES:
            result.warnings.append(
                f"提取行数({result.line_count})低于最小阈值({CONTENT_MIN_LINES})。"
                "内容可能不完整，建议检查选择器或增大等待时间。"
            )
            checks['min_lines'] = False
        else:
            checks['min_lines'] = True

        # 最小字符数检查
        if result.char_count < CONTENT_MIN_CHARS:
            result.warnings.append(
                f"提取字符数({result.char_count})低于最小阈值({CONTENT_MIN_CHARS})。"
                "内容可能不完整。"
            )
            checks['min_chars'] = False
        else:
            checks['min_chars'] = True

        # 检查空行比例（过多空行说明提取有问题）
        empty_lines = sum(1 for l in result.lines if len(l.strip()) <= 1)
        empty_ratio = empty_lines / max(result.line_count, 1)
        checks['empty_line_ratio'] = round(empty_ratio, 2)
        if empty_ratio > 0.5:
            result.warnings.append(
                f"空行比例过高({empty_ratio:.0%})，可能是选择器匹配到了装饰性元素"
            )

        # 检查是否有标题行
        has_title = any('计划' in l or '介绍' in l or '概述' in l or len(l) < 30 for l in result.lines[:5])
        checks['has_title_like_first_lines'] = has_title

        result.anti_pattern_checks.update(checks)

    @staticmethod
    def detect_saas_platform(url: str) -> Optional[str]:
        """检测URL属于哪个SaaS平台，返回平台标识或None"""
        domain_checks = {
            'feishu': ['bytedance.larkoffice.com', 'feishu.cn', 'larksuite.com'],
            'dingtalk': ['dingtalk.com', 'alidocs.dingtalk.com'],
            'wecom': ['work.weixin.qq.com', 'doc.weixin.qq.com'],
            'notion': ['notion.site', 'notion.so'],
            'confluence': ['atlassian.net', 'confluence'],
            'yuque': ['yuque.com'],
            'shimo': ['shimo.im'],
            'wps': ['kdocs.cn', 'wps.cn'],
        }
        for platform, domains in domain_checks.items():
            if any(d in url for d in domains):
                return platform
        return None


def extract_feishu_doc(
    url: str,
    output_dir: Optional[Path] = None,
    cookies_file: Optional[Path] = None,
    headless: bool = False,
    scroll_step: int = DEFAULT_SCROLL_STEP,
    wait_ms: int = DEFAULT_WAIT_MS,
    verbose: bool = False,
) -> ExtractionResult:
    """便捷函数：提取单个飞书文档"""
    extractor = FeishuExtractor(
        scroll_step=scroll_step,
        wait_ms=wait_ms,
        verbose=verbose,
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})

        # 加载cookies（如果提供）
        if cookies_file and cookies_file.exists():
            cookies = json.loads(cookies_file.read_text(encoding='utf-8'))
            context.add_cookies(cookies)
            if verbose:
                print_info(f"已加载cookies: {cookies_file}")

        page = context.new_page()
        result = extractor.extract(page, url)

        browser.close()

    # 保存输出
    if output_dir and result.success:
        output_dir.mkdir(parents=True, exist_ok=True)
        # 生成文件名
        title_slug = re.sub(r'[^\w\u4e00-\u9fff-]', '-', result.title)[:50].strip('-')
        if not title_slug:
            title_slug = 'feishu-doc'
        output_file = output_dir / f"{title_slug}.txt"
        output_file.write_text(result.content, encoding='utf-8')

        # 保存元数据报告
        meta_file = output_dir / f"{title_slug}.meta.json"
        meta = {
            'url': result.url,
            'title': result.title,
            'char_count': result.char_count,
            'line_count': result.line_count,
            'urls_found': result.urls_found,
            'scroll_iterations': result.scroll_iterations,
            'warnings': result.warnings,
            'errors': result.errors,
            'anti_pattern_checks': result.anti_pattern_checks,
            'extraction_time_ms': result.extraction_time_ms,
            'extraction_params': {
                'scroll_step': scroll_step,
                'wait_ms': wait_ms,
            }
        }
        meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')

        if verbose:
            print_pass(f"已保存: {output_file}")
            print_pass(f"元数据: {meta_file}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description='飞书云文档内容提取工具（遵循feishu-doc-dom-extraction模式）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python feishu-doc-extract.py https://bytedance.larkoffice.com/wiki/xxx
  python feishu-doc-extract.py https://feishu.cn/docx/xxx --output ./extracted --cookies cookies.json
  python feishu-doc-extract.py https://xxx.feishu.cn/docx/xxx --headless --verbose
        """
    )
    parser.add_argument('url', help='飞书文档URL')
    parser.add_argument('--output', '-o', type=Path, help='输出目录')
    parser.add_argument('--cookies', '-c', type=Path, help='cookies JSON文件路径（用于认证）')
    parser.add_argument('--headless', action='store_true', help='无头模式（默认有界面）')
    parser.add_argument('--scroll-step', type=int, default=DEFAULT_SCROLL_STEP, help=f'滚动步长(默认{DEFAULT_SCROLL_STEP}px)')
    parser.add_argument('--wait-ms', type=int, default=DEFAULT_WAIT_MS, help=f'等待时间(默认{DEFAULT_WAIT_MS}ms)')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')

    args = parser.parse_args()

    # 检测平台
    platform = FeishuExtractor.detect_saas_platform(args.url)
    if platform != 'feishu':
        print_warn(f"URL未识别为飞书域名(检测到: {platform})，仍尝试提取...")

    result = extract_feishu_doc(
        url=args.url,
        output_dir=args.output,
        cookies_file=args.cookies,
        headless=args.headless,
        scroll_step=args.scroll_step,
        wait_ms=args.wait_ms,
        verbose=args.verbose,
    )

    # 输出结果摘要
    print()
    print("=" * 60)
    if result.success:
        print_pass(f"提取成功！")
        print(f"  标题: {result.title}")
        print(f"  字符数: {result.char_count}")
        print(f"  行数: {result.line_count}")
        print(f"  URL数: {len(result.urls_found)}")
        print(f"  迭代轮次: {result.scroll_iterations}")
        print(f"  耗时: {result.extraction_time_ms}ms")
    else:
        print_error(f"提取失败！")
        for err in result.errors:
            print_error(f"  错误: {err}")

    if result.warnings:
        for w in result.warnings:
            print_warn(f"  警告: {w}")

    # 输出内容预览
    if args.verbose and result.lines:
        print("\n内容预览（前5行）：")
        for i, line in enumerate(result.lines[:5]):
            print(f"  {i+1}. {line[:80]}")

    return 0 if result.success else 1


if __name__ == '__main__':
    sys.exit(main())
