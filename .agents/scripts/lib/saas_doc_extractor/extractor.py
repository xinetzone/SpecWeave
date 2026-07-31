"""核心SaaS文档提取器。

设计原则：
- 浏览器抽象层：通过PageProtocol协议解耦Playwright依赖，方便mock测试
- 平台配置驱动：选择器和参数由PlatformConfig提供
- 反模式检查：提取前后均运行检查，记录warnings
- 双向扫描：向下→向上→向下三次扫描，防虚拟滚动DOM回收遗漏
- 选择器fallback：主选择器失效时自动尝试备选选择器
"""

from __future__ import annotations

import time
from typing import Any, Optional, Protocol, runtime_checkable

from .anti_patterns import run_post_extraction_checks, run_pre_extraction_checks
from .models import (
    ExtractionConfig,
    ExtractionResult,
    PlatformConfig,
    ResolvedConfig,
)
from .text_cleaner import clean_text


@runtime_checkable
class PageProtocol(Protocol):
    """浏览器页面协议。

    抽象Playwright Page的核心方法，使提取器可在测试中使用mock。
    只需实现evaluate和wait_for_timeout两个方法。
    """

    def evaluate(self, expression: str, arg: Any = None) -> Any:
        """在页面中执行JavaScript表达式。"""
        ...

    def wait_for_timeout(self, timeout: int) -> None:
        """等待指定毫秒数。"""
        ...


class SaasDocExtractor:
    """通用SaaS云文档DOM提取器。

    用法（Playwright）::

        from lib.saas_doc_extractor import SaasDocExtractor, get_platform_config, ExtractionConfig

        platform_cfg = get_platform_config('feishu')
        extractor = SaasDocExtractor(platform_cfg, ExtractionConfig(verbose=True))
        result = extractor.extract(page, url)
        if result.success:
            print(result.content)

    用法（自定义浏览器）::

        实现PageProtocol协议（evaluate + wait_for_timeout），传入即可。
    """

    def __init__(
        self,
        platform: PlatformConfig,
        config: Optional[ExtractionConfig] = None,
    ):
        self.platform = platform
        self.user_config = config or ExtractionConfig()
        self.cfg: ResolvedConfig = self.user_config.resolve(platform)

        # 选择器状态（提取时决定使用主选还是fallback）
        self._effective_container_sel: str = platform.container_selector
        self._effective_line_sel: str = platform.line_selector
        self._used_fallback_container = False
        self._used_fallback_line = False

    def extract(self, page: PageProtocol, url: str) -> ExtractionResult:
        """执行完整提取流程。

        Args:
            page: 实现PageProtocol的页面对象（Playwright Page或mock）
            url: 文档URL

        Returns:
            ExtractionResult
        """
        result = ExtractionResult(url=url, platform=self.platform.name)
        start = time.time()

        # Step 1: 解析配置
        cfg = self.cfg
        if cfg.verbose:
            self._log(f"平台: {self.platform.display_name} ({self.platform.name})")
            self._log(f"参数: step={cfg.scroll_step}px, wait={cfg.wait_ms}ms, "
                      f"init_wait={cfg.initial_wait_ms}ms, bidirectional={cfg.bidirectional_scan}")

        # Step 2: 等待初始渲染
        page.wait_for_timeout(cfg.initial_wait_ms)

        # Step 3: 检测有效容器选择器（含fallback链）
        container_info = self._detect_container(page, result)
        if container_info is None:
            # 容器不存在，直接添加错误并返回
            result.errors.append(
                f"未找到滚动容器（已尝试: {', '.join(self.platform.get_container_selectors())}）。"
                "可能原因：页面未完全加载、DOM结构更新、非文档页面、需登录认证。"
            )
            result.extraction_time_ms = int((time.time() - start) * 1000)
            return result
        if result.errors:
            result.extraction_time_ms = int((time.time() - start) * 1000)
            return result

        # Step 4: 检测有效文本行选择器
        initial_line_count = self._detect_line_selector(page, result)

        # Step 5: 提取前反模式检查
        body_scrollable = page.evaluate("() => document.body.scrollHeight > window.innerHeight + 100")
        run_pre_extraction_checks(container_info, initial_line_count, body_scrollable,
                                  self.platform, result)

        # Step 6: 提取标题
        self._extract_title(page, result)

        # Step 7: 重置到顶部
        self._scroll_to_top(page)
        page.wait_for_timeout(cfg.wait_ms)

        # Step 8: 向下滚动提取（第一遍）
        self._scroll_collect(page, result, direction="down")

        # Step 9: 双向扫描（向上补扫→再次向下）
        if cfg.bidirectional_scan:
            if cfg.verbose:
                self._log("执行双向扫描...")
            self._scroll_collect(page, result, direction="up")
            self._scroll_to_top(page)
            page.wait_for_timeout(cfg.wait_ms)
            self._scroll_collect(page, result, direction="down")

        # Step 10: 提取后反模式检查
        run_post_extraction_checks(result, self.platform, cfg)

        # Step 11: 记录选择器使用情况
        result.container_selector_used = self._effective_container_sel
        result.line_selector_used = self._effective_line_sel
        result.used_fallback_container = self._used_fallback_container
        result.used_fallback_line = self._used_fallback_line

        result.extraction_time_ms = int((time.time() - start) * 1000)
        return result

    # ---- 选择器检测 ----

    def _detect_container(self, page: PageProtocol, result: ExtractionResult) -> Optional[dict]:
        """检测有效的滚动容器选择器（尝试主选+fallback）"""
        for sel in self.platform.get_container_selectors():
            info = page.evaluate(f"""() => {{
                const c = document.querySelector('{sel}');
                if (!c) return null;
                return {{
                    tag: c.tagName,
                    scrollHeight: c.scrollHeight,
                    clientHeight: c.clientHeight,
                    scrollTop: c.scrollTop,
                    className: (c.className || '').substring(0, 100)
                }};
            }}""")
            if info is not None:
                if sel != self.platform.container_selector:
                    self._used_fallback_container = True
                    result.warnings.append(f"容器使用fallback选择器: {sel}")
                self._effective_container_sel = sel
                if self.cfg.verbose:
                    self._log(f"容器选择器: {sel} (scrollHeight={info['scrollHeight']}px)")
                return info

        # 所有选择器都失败
        return None

    def _detect_line_selector(self, page: PageProtocol, result: ExtractionResult) -> int:
        """检测有效的文本行选择器，返回初始行数"""
        container_sel = self._effective_container_sel
        for sel in self.platform.get_line_selectors():
            count = page.evaluate(f"""() => {{
                const c = document.querySelector('{container_sel}');
                if (!c) return 0;
                return c.querySelectorAll('{sel}').length;
            }}""")
            if count > 0:
                if sel != self.platform.line_selector:
                    self._used_fallback_line = True
                    result.warnings.append(f"文本行使用fallback选择器: {sel}")
                self._effective_line_sel = sel
                if self.cfg.verbose:
                    self._log(f"行选择器: {sel} (初始可见{count}行)")
                return count

        self._effective_line_sel = self.platform.line_selector
        return 0

    # ---- 标题提取 ----

    def _extract_title(self, page: PageProtocol, result: ExtractionResult) -> None:
        """提取文档标题"""
        c_sel = self._effective_container_sel
        l_sel = self._effective_line_sel
        title = page.evaluate(f"""() => {{
            const c = document.querySelector('{c_sel}');
            if (!c) return '';
            const lines = c.querySelectorAll('{l_sel}');
            return lines.length > 0 ? (lines[0].innerText || '').trim() : '';
        }}""")
        if title:
            result.title = clean_text(title.split('\n')[0])  # 标题取第一行
        else:
            # fallback: document.title
            doc_title = page.evaluate("() => document.title || ''")
            result.title = clean_text(doc_title)
            if result.title:
                for suffix in [' - 飞书云文档', ' - 钉钉文档', ' - 腾讯文档', ' - 语雀', ' - Notion']:
                    result.title = result.title.replace(suffix, '')
                result.warnings.append("从行选择器获取标题失败，使用document.title fallback")

    # ---- 滚动控制 ----

    def _scroll_to_top(self, page: PageProtocol) -> None:
        """滚动到容器顶部，触发scroll事件"""
        sel = self._effective_container_sel
        page.evaluate(f"""() => {{
            const c = document.querySelector('{sel}');
            if (c) {{
                c.scrollTo({{top: 0, behavior: 'auto'}});
                c.dispatchEvent(new Event('scroll', {{bubbles: true}}));
            }}
        }}""")

    def _scroll_by(self, page: PageProtocol, delta: int) -> None:
        """滚动指定像素数，触发scroll事件"""
        sel = self._effective_container_sel
        page.evaluate(f"""() => {{
            const c = document.querySelector('{sel}');
            if (c) {{
                c.scrollBy({{top: {delta}, behavior: 'auto'}});
                c.dispatchEvent(new Event('scroll', {{bubbles: true}}));
            }}
        }}""")

    def _is_at_boundary(self, page: PageProtocol, direction: str) -> bool:
        """检查是否到达滚动边界"""
        sel = self._effective_container_sel
        return page.evaluate(f"""() => {{
            const c = document.querySelector('{sel}');
            if (!c) return true;
            if ('{direction}' === 'down') {{
                return c.scrollTop + c.clientHeight >= c.scrollHeight - 10;
            }} else {{
                return c.scrollTop <= 10;
            }}
        }}""")

    # ---- 核心滚动收集 ----

    def _scroll_collect(
        self,
        page: PageProtocol,
        result: ExtractionResult,
        direction: str = "down",
    ) -> None:
        """分段滚动+去重保序收集。

        反模式防护（基于实测）：
        - scrollBy+dispatchEvent确保虚拟滚动触发
        - 容器作用域querySelectorAll避免UI噪音
        - JS端拆分.ace-line内\\n软换行
        - JS端清理零宽字符
        - Set去重处理虚拟滚动DOM回收
        """
        cfg = self.cfg
        c_sel = self._effective_container_sel
        l_sel = self._effective_line_sel
        step = cfg.scroll_step if direction == "down" else -cfg.scroll_step

        collected: set[str] = set(result.lines)
        ordered: list[str] = list(result.lines)
        no_new_count = 0

        # 向上滚动时先偏移2步
        if direction == "up":
            self._scroll_by(page, -cfg.scroll_step * 2)
            page.wait_for_timeout(cfg.wait_ms)

        for i in range(cfg.max_iterations):
            # 收集当前可见行（JS端完成：容器作用域查询→拆分换行→清理零宽→过滤空行）
            js_collect = f"""() => {{
                const c = document.querySelector('{c_sel}');
                if (!c) return [];
                const lines = [];
                c.querySelectorAll('{l_sel}').forEach(el => {{
                    const text = el.innerText || '';
                    text.split('\\n').forEach(seg => {{
                        const clean = seg.replace(/[\\u200b-\\u200f\\u2028-\\u202f\\ufeff]/g, '').trim();
                        if (clean) lines.push(clean);
                    }});
                }});
                return lines;
            }}"""
            raw_lines = page.evaluate(js_collect)

            new_found: list[str] = []
            for line in raw_lines:
                clean = clean_text(line)
                if clean and clean not in collected:
                    collected.add(clean)
                    new_found.append(clean)

            if direction == "down":
                ordered.extend(new_found)
            else:
                # 向上扫描时，越先发现的是越早的内容，反转后插入前面以保序
                for line in reversed(new_found):
                    ordered.insert(0, line)

            result.scroll_iterations += 1

            if len(new_found) == 0:
                no_new_count += 1
            else:
                no_new_count = 0
                if cfg.verbose:
                    self._log(f"  {direction} 迭代{i+1}: +{len(new_found)}行, 总计{len(ordered)}行")

            if no_new_count >= cfg.max_no_new:
                if cfg.verbose:
                    self._log(f"  连续{cfg.max_no_new}次无新内容，停止{direction}扫描")
                break

            if self._is_at_boundary(page, direction):
                if cfg.verbose:
                    self._log(f"  到达{'底部' if direction == 'down' else '顶部'}边界")
                break

            self._scroll_by(page, step)
            page.wait_for_timeout(cfg.wait_ms)

        result.lines = ordered
        # 更新total_scroll_height（动态读取，支持懒加载增长）
        sh = page.evaluate(f"""() => {{
            const c = document.querySelector('{c_sel}');
            return c ? c.scrollHeight : 0;
        }}""")
        if sh > result.total_scroll_height:
            result.total_scroll_height = sh

    # ---- 工具 ----

    def _log(self, msg: str) -> None:
        print(f"  [INFO] {msg}")
