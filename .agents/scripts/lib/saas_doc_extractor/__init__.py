"""企业SaaS云文档DOM提取工具库。

提供通用的虚拟滚动文档提取框架，支持飞书/钉钉/企微/语雀等平台。
核心设计：平台配置驱动 + 反模式检查 + 可注入浏览器抽象层。

使用方式：
    from lib.saas_doc_extractor import (
        ExtractionConfig, ExtractionResult, PlatformConfig,
        SaasDocExtractor, get_platform_config, detect_platform,
        clean_text, extract_urls, ZERO_WIDTH_CHARS,
    )
"""

from .models import (
    CONTENT_MIN_CHARS,
    CONTENT_MIN_LINES,
    EMPTY_LINE_RATIO_THRESHOLD,
    AntiPatternReport,
    ExtractionConfig,
    ExtractionResult,
    PlatformConfig,
    ResolvedConfig,
)
from .platforms import (
    PLATFORM_CONFIGS,
    detect_platform,
    get_platform_config,
    list_supported_platforms,
)
from .text_cleaner import (
    ZERO_WIDTH_CHARS,
    clean_text,
    extract_urls,
    has_zero_width_chars,
    split_lines,
)
from .extractor import PageProtocol, SaasDocExtractor
from .anti_patterns import run_post_extraction_checks, run_pre_extraction_checks

__all__ = [
    # Constants
    "CONTENT_MIN_CHARS",
    "CONTENT_MIN_LINES",
    "EMPTY_LINE_RATIO_THRESHOLD",
    # Config & Result
    "ExtractionConfig",
    "ExtractionResult",
    "PlatformConfig",
    "ResolvedConfig",
    "AntiPatternReport",
    # Platforms
    "PLATFORM_CONFIGS",
    "detect_platform",
    "get_platform_config",
    "list_supported_platforms",
    # Text utilities
    "ZERO_WIDTH_CHARS",
    "clean_text",
    "split_lines",
    "extract_urls",
    "has_zero_width_chars",
    # Core extractor
    "SaasDocExtractor",
    "PageProtocol",
    "run_pre_extraction_checks",
    "run_post_extraction_checks",
]
