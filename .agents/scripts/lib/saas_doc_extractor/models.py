"""SaaS文档提取器数据模型。

定义平台配置、提取配置、提取结果、反模式报告等数据结构。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


# ============================================================
# 提取阈值常量（所有平台通用）
# ============================================================
CONTENT_MIN_LINES: int = 10        # 最小有效行数阈值
CONTENT_MIN_CHARS: int = 200       # 最小有效字符数阈值
EMPTY_LINE_RATIO_THRESHOLD: float = 0.3  # 空行比例告警阈值


@dataclass
class PlatformConfig:
    """SaaS平台DOM配置。

    每个平台定义自己的选择器和参数，通过配置驱动提取逻辑。
    """
    name: str                           # 平台标识：feishu/dingtalk/wecom/yuque/notion/confluence/shimo/wps
    display_name: str                   # 中文显示名
    domains: list[str]                  # 域名关键词列表
    container_selector: str             # 滚动容器CSS选择器
    line_selector: str                  # 文本行CSS选择器
    scroll_step: int = 400              # 推荐滚动步长（px）
    wait_ms: int = 1500                 # 每步等待时间（ms）
    initial_wait_ms: int = 2000         # 页面初始等待时间（ms）
    max_no_new: int = 3                 # 连续无新内容次数阈值
    max_iterations: int = 30            # 最大迭代次数
    container_selector_fallbacks: list[str] = field(default_factory=list)  # 容器备选选择器
    line_selector_fallbacks: list[str] = field(default_factory=list)        # 行备选选择器
    uses_virtual_scroll: bool = True    # 是否使用虚拟滚动
    body_is_scrollable: bool = False    # body是否为主要滚动条（反模式检查依据）
    notes: str = ""                     # 平台特殊说明
    verified: bool = False              # 是否已通过实测验证（True=可用，False=候选配置）

    def get_container_selectors(self) -> list[str]:
        """获取容器选择器列表（主选+备选）"""
        return [self.container_selector] + self.container_selector_fallbacks

    def get_line_selectors(self) -> list[str]:
        """获取行选择器列表（主选+备选）"""
        return [self.line_selector] + self.line_selector_fallbacks


@dataclass
class ExtractionConfig:
    """提取运行时配置（可覆盖平台默认值）"""
    scroll_step: Optional[int] = None
    wait_ms: Optional[int] = None
    initial_wait_ms: Optional[int] = None
    max_no_new: Optional[int] = None
    max_iterations: Optional[int] = None
    bidirectional_scan: bool = True     # 是否执行双向扫描（向上+向下二次扫描）
    verbose: bool = False
    headless: bool = False

    def resolve(self, platform: PlatformConfig) -> "ResolvedConfig":
        """合并平台默认值，返回完整配置"""
        return ResolvedConfig(
            scroll_step=self.scroll_step or platform.scroll_step,
            wait_ms=self.wait_ms or platform.wait_ms,
            initial_wait_ms=self.initial_wait_ms or platform.initial_wait_ms,
            max_no_new=self.max_no_new or platform.max_no_new,
            max_iterations=self.max_iterations or platform.max_iterations,
            bidirectional_scan=self.bidirectional_scan,
            verbose=self.verbose,
        )


@dataclass
class ResolvedConfig:
    """已解析的完整配置（平台默认值+用户覆盖已合并）"""
    scroll_step: int
    wait_ms: int
    initial_wait_ms: int
    max_no_new: int
    max_iterations: int
    bidirectional_scan: bool
    verbose: bool


@dataclass
class AntiPatternReport:
    """反模式检查报告"""
    container_exists: bool = False
    container_scrollable: bool = False
    antipattern_body_scroll: bool = False   # True=反模式（body在滚动）
    initial_lines_ok: bool = False
    content_min_lines: bool = False
    content_min_chars: bool = False
    title_exists: bool = False
    urls_found: int = 0
    empty_line_ratio: float = 0.0
    empty_line_ratio_ok: bool = False
    zerowidth_clean: bool = True
    has_selectors_effective: bool = False   # 选择器是否真正生效（非fallback）
    warnings: list[str] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        """核心检查项是否全部通过"""
        return all([
            self.container_exists,
            self.container_scrollable,
            not self.antipattern_body_scroll,
            self.initial_lines_ok,
            self.content_min_lines,
            self.content_min_chars,
            self.title_exists,
            self.empty_line_ratio_ok,
            self.zerowidth_clean,
            self.has_selectors_effective,
        ])

    @property
    def pass_count(self) -> int:
        """通过的检查项数量"""
        checks = [
            self.container_exists,
            self.container_scrollable,
            not self.antipattern_body_scroll,
            self.initial_lines_ok,
            self.content_min_lines,
            self.content_min_chars,
            self.title_exists,
            self.empty_line_ratio_ok,
            self.zerowidth_clean,
            self.has_selectors_effective,
        ]
        return sum(1 for c in checks if c)

    def to_dict(self) -> dict[str, Any]:
        return {
            "container_exists": self.container_exists,
            "container_scrollable": self.container_scrollable,
            "antipattern_body_scroll": self.antipattern_body_scroll,
            "initial_lines_ok": self.initial_lines_ok,
            "content_min_lines": self.content_min_lines,
            "content_min_chars": self.content_min_chars,
            "title_exists": self.title_exists,
            "urls_found": self.urls_found,
            "empty_line_ratio": round(self.empty_line_ratio, 2),
            "empty_line_ratio_ok": self.empty_line_ratio_ok,
            "zerowidth_clean": self.zerowidth_clean,
            "has_selectors_effective": self.has_selectors_effective,
            "all_passed": self.all_passed,
            "pass_count": self.pass_count,
            "warnings": self.warnings,
        }


@dataclass
class ExtractionResult:
    """文档提取结果"""
    url: str
    platform: str = ""
    title: str = ""
    lines: list[str] = field(default_factory=list)
    urls_found: list[str] = field(default_factory=list)
    scroll_iterations: int = 0
    total_scroll_height: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    anti_pattern: AntiPatternReport = field(default_factory=AntiPatternReport)
    extraction_time_ms: int = 0
    container_selector_used: str = ""
    line_selector_used: str = ""
    used_fallback_container: bool = False
    used_fallback_line: bool = False

    @property
    def content(self) -> str:
        """拼接完整文本"""
        return "\n".join(self.lines)

    @property
    def char_count(self) -> int:
        return len(self.content)

    @property
    def line_count(self) -> int:
        return len(self.lines)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0 and self.char_count >= CONTENT_MIN_CHARS and self.anti_pattern.all_passed

    def to_meta_dict(self, config: Optional[ResolvedConfig] = None) -> dict[str, Any]:
        """导出元数据字典（用于JSON报告）"""
        meta: dict[str, Any] = {
            "url": self.url,
            "platform": self.platform,
            "title": self.title,
            "char_count": self.char_count,
            "line_count": self.line_count,
            "urls_found": self.urls_found,
            "scroll_iterations": self.scroll_iterations,
            "total_scroll_height": self.total_scroll_height,
            "warnings": self.warnings,
            "errors": self.errors,
            "anti_pattern_checks": self.anti_pattern.to_dict(),
            "extraction_time_ms": self.extraction_time_ms,
            "selectors": {
                "container": self.container_selector_used,
                "line": self.line_selector_used,
                "used_fallback_container": self.used_fallback_container,
                "used_fallback_line": self.used_fallback_line,
            },
        }
        if config:
            meta["extraction_params"] = {
                "scroll_step": config.scroll_step,
                "wait_ms": config.wait_ms,
                "initial_wait_ms": config.initial_wait_ms,
                "max_no_new": config.max_no_new,
                "bidirectional_scan": config.bidirectional_scan,
            }
        return meta
