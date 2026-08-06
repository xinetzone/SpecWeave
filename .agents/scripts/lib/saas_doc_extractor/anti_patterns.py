"""反模式检查逻辑。

独立于浏览器的纯Python检查逻辑，在提取前/后运行。
所有检查返回(warnings, errors, updated_report)三元组。
"""

from __future__ import annotations

from typing import Optional

from .models import (
    CONTENT_MIN_CHARS,
    CONTENT_MIN_LINES,
    EMPTY_LINE_RATIO_THRESHOLD,
    AntiPatternReport,
    ExtractionResult,
    PlatformConfig,
    ResolvedConfig,
)
from .text_cleaner import extract_urls, has_zero_width_chars


def run_pre_extraction_checks(
    container_info: Optional[dict],
    initial_line_count: int,
    body_scrollable: bool,
    platform: PlatformConfig,
    result: ExtractionResult,
) -> AntiPatternReport:
    """提取前检查（容器可用性、选择器有效性、body滚动反模式等）。

    Args:
        container_info: 容器信息字典{tag, scrollHeight, clientHeight, className}或None
        initial_line_count: 初始可见文本行数
        body_scrollable: body是否可滚动
        platform: 平台配置
        result: 提取结果对象（用于追加warnings/errors）

    Returns:
        AntiPatternReport（部分填充）
    """
    report = AntiPatternReport()

    # 1. 容器存在性
    if container_info is None:
        report.container_exists = False
        result.errors.append(
            f"未找到滚动容器 '{platform.container_selector}'。"
            "可能原因：页面未完全加载、DOM结构更新、非文档页面、需登录认证。"
        )
        return report
    report.container_exists = True

    # 2. 容器可滚动性
    sh = container_info.get("scrollHeight", 0)
    ch = container_info.get("clientHeight", 0)
    result.total_scroll_height = sh
    report.container_scrollable = sh > ch
    if not report.container_scrollable and sh > 0:
        result.warnings.append(
            f"容器scrollHeight({sh}) <= clientHeight({ch})，内容可能无需滚动"
        )

    # 3. body滚动反模式检查
    report.antipattern_body_scroll = body_scrollable
    if body_scrollable and not platform.body_is_scrollable:
        result.warnings.append(
            "检测到body可滚动（反模式）。该平台应使用自定义容器滚动。"
        )
    elif body_scrollable and platform.body_is_scrollable:
        report.antipattern_body_scroll = False  # 该平台预期body滚动，非反模式

    # 4. 初始行数
    report.initial_lines_ok = initial_line_count >= 3
    if initial_line_count == 0:
        result.warnings.append(
            f"初始状态未找到 '{platform.line_selector}' 元素，可能需要等待更长时间"
        )
    elif initial_line_count < 3:
        result.warnings.append(
            f"初始可见文本行仅{initial_line_count}行，可能渲染不完整"
        )

    result.anti_pattern = report
    return report


def run_post_extraction_checks(
    result: ExtractionResult,
    platform: PlatformConfig,
    config: ResolvedConfig,
) -> AntiPatternReport:
    """提取后检查（内容阈值、URL保留、空行比例、零宽字符、标题等）。

    Args:
        result: 提取结果对象（lines已填充）
        platform: 平台配置
        config: 运行时配置

    Returns:
        AntiPatternReport（完整填充）
    """
    report = result.anti_pattern
    content = result.content
    lines = result.lines

    # 5. 最小行数
    report.content_min_lines = len(lines) >= CONTENT_MIN_LINES
    if not report.content_min_lines:
        result.warnings.append(
            f"提取行数({len(lines)})低于最小阈值({CONTENT_MIN_LINES})"
        )

    # 6. 最小字符数
    report.content_min_chars = len(content) >= CONTENT_MIN_CHARS
    if not report.content_min_chars:
        result.warnings.append(
            f"提取字符数({len(content)})低于最小阈值({CONTENT_MIN_CHARS})"
        )

    # 7. 标题存在性
    report.title_exists = bool(result.title and len(result.title) > 0)
    if not report.title_exists:
        result.warnings.append("未能提取到文档标题")

    # 8. URL提取
    result.urls_found = extract_urls(content)
    report.urls_found = len(result.urls_found)

    # 9. 空行比例
    empty_lines = sum(1 for l in lines if len(l.strip()) <= 1)
    ratio = empty_lines / max(len(lines), 1)
    report.empty_line_ratio = ratio
    report.empty_line_ratio_ok = ratio <= EMPTY_LINE_RATIO_THRESHOLD
    if not report.empty_line_ratio_ok:
        result.warnings.append(
            f"空行比例过高({ratio:.0%})，阈值{EMPTY_LINE_RATIO_THRESHOLD:.0%}，"
            "可能是选择器匹配了装饰性元素"
        )

    # 10. 零宽字符残留检查
    remaining_zw = sum(1 for l in lines if has_zero_width_chars(l))
    report.zerowidth_clean = remaining_zw == 0
    if not report.zerowidth_clean:
        result.warnings.append(
            f"有{remaining_zw}行仍包含零宽字符，清理不彻底"
        )

    # 11. 选择器有效性标记（如果lines有内容则认为选择器生效）
    report.has_selectors_effective = len(lines) > 0 and len(content) > 50

    # 合并warnings
    report.warnings = list(result.warnings)

    result.anti_pattern = report
    return report
