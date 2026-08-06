"""SaaS平台配置注册表。

定义各平台的DOM选择器、推荐参数和特殊说明。
飞书配置已通过实测验证，其他平台为候选配置（需实测确认）。
"""

from __future__ import annotations

from typing import Optional

from .models import PlatformConfig


# ============================================================
# 平台配置（飞书已验证，其他为候选配置）
# ============================================================

FEISHU_CONFIG = PlatformConfig(
    name="feishu",
    display_name="飞书云文档",
    domains=["bytedance.larkoffice.com", "feishu.cn", "larksuite.com", "larkoffice.com"],
    container_selector=".bear-web-x-container",
    line_selector=".ace-line",
    scroll_step=400,
    wait_ms=1500,
    initial_wait_ms=2000,
    max_no_new=3,
    max_iterations=30,
    container_selector_fallbacks=[
        ".docx-container",          # 旧版飞书docx
        ".wiki-container",          # 知识库容器变体
        "[data-role='document-container']",
    ],
    line_selector_fallbacks=[
        ".ace-line-content",        # 行内容变体
        "[data-block-type]",        # 数据属性选择器
    ],
    uses_virtual_scroll=True,
    body_is_scrollable=False,
    verified=True,
    notes=(
        "已实测验证（2026-07-31）：\n"
        "- 滚动容器.bear-web-x-container，class含catalogue-opened/docx-in-wiki变体\n"
        "- .ace-line为文本行，innerText含完整链接文本\n"
        "- 虚拟滚动DOM回收阈值：scrollTop≥~800px时顶部DOM移除\n"
        "- scrollHeight动态增长（懒加载，初始2166px→滚动中3345px）\n"
        "- 需scrollBy+dispatchEvent('scroll')触发虚拟滚动渲染\n"
        "- .ace-line内可能含\\n软换行，需split拆分"
    ),
)

DINGTALK_CONFIG = PlatformConfig(
    name="dingtalk",
    display_name="钉钉文档",
    domains=["dingtalk.com", "alidocs.dingtalk.com", "docs.dingtalk.com"],
    # 候选选择器（需实测验证）
    container_selector=".doc-scroll-container",
    line_selector=".doc-line, .text-run, .paragraph",
    scroll_step=400,
    wait_ms=1500,
    initial_wait_ms=2500,          # 钉钉文档可能渲染较慢
    max_no_new=3,
    max_iterations=30,
    container_selector_fallbacks=[
        ".canvas-container",
        ".document-editor",
        ".editor-container",
        "#doc-container",
    ],
    line_selector_fallbacks=[
        ".ne-viewer-line",         # 钉钉文档ne-viewer渲染
        ".page-block",
        "[data-block-id]",
        "p.ne-paragraph",
    ],
    uses_virtual_scroll=True,
    body_is_scrollable=False,
    notes=(
        "候选配置，未实测验证。钉钉文档使用自研ne-viewer引擎，可能Canvas+DOM混合渲染。\n"
        "注意事项：\n"
        "- 钉钉文档登录态依赖钉钉客户端或cookie认证\n"
        "- 部分文档可能使用Canvas渲染文字，DOM提取可能失效\n"
        "- 建议先用通用探测脚本验证选择器有效性"
    ),
)

WECOM_CONFIG = PlatformConfig(
    name="wecom",
    display_name="企业微信文档（腾讯文档）",
    domains=["work.weixin.qq.com", "doc.weixin.qq.com", "docs.qq.com"],
    # 候选选择器（需实测验证）
    container_selector=".dui-dialog-scroll__container, .editor-container",
    line_selector=".text-render, .paragraph-render, .render-unit",
    scroll_step=400,
    wait_ms=1500,
    initial_wait_ms=2500,
    max_no_new=3,
    max_iterations=30,
    container_selector_fallbacks=[
        ".qz-editor-container",     # 腾讯文档编辑器容器
        ".web-doc-container",
        ".sheet-container",
        ".reader-container",
        "#js-doc-container",
    ],
    line_selector_fallbacks=[
        ".dui-text",                # 企业微信dui组件
        ".qz-text",
        ".text-block",
        "[data-type='paragraph']",
        ".para",
    ],
    uses_virtual_scroll=True,
    body_is_scrollable=False,
    notes=(
        "候选配置，未实测验证。企业微信文档底层使用腾讯文档引擎。\n"
        "注意事项：\n"
        "- 腾讯文档有多种形态（智能文档/在线文档/表格），选择器可能不同\n"
        "- 部分版本使用Shadow DOM封装，需要pierce选择器\n"
        "- 文档分享链接可能含密码保护\n"
        "- 建议先用通用探测脚本验证选择器有效性"
    ),
)

YUQUE_CONFIG = PlatformConfig(
    name="yuque",
    display_name="语雀",
    domains=["yuque.com", "antgroup.yuque.com"],
    container_selector=".ne-viewer-body",
    line_selector=".ne-viewer-line, .ne-p, p",
    scroll_step=500,
    wait_ms=1000,
    initial_wait_ms=1500,
    max_no_new=3,
    max_iterations=30,
    container_selector_fallbacks=[
        ".doc-container",
        ".article-content",
        "#content",
        ".lake-content",
    ],
    line_selector_fallbacks=[
        ".lake-content p",
        ".article p",
        "p",
    ],
    uses_virtual_scroll=False,        # 语雀通常非虚拟滚动
    body_is_scrollable=True,          # 语雀通常body滚动
    notes=(
        "候选配置，未实测验证。语雀文档相对飞书更传统，可能使用语义化HTML。\n"
        "注意事项：\n"
        "- 语雀文档结构较规范，标题使用h1-h6，段落使用p\n"
        "- 大部分文档不需要虚拟滚动提取，直接document.body.innerText可能就够了\n"
        "- 长文档（>100页）可能需要滚动"
    ),
)

NOTION_CONFIG = PlatformConfig(
    name="notion",
    display_name="Notion",
    domains=["notion.site", "notion.so"],
    container_selector=".notion-frame",
    line_selector=".notion-text-block, [data-block-id]",
    scroll_step=500,
    wait_ms=1000,
    initial_wait_ms=2000,
    max_no_new=3,
    max_iterations=40,
    container_selector_fallbacks=[
        ".notion-page-content",
        "#notion-app",
    ],
    line_selector_fallbacks=[
        "[data-content-editable-root]",
        ".notion-page-block",
        "div[placeholder]",
    ],
    uses_virtual_scroll=True,
    body_is_scrollable=False,
    notes=(
        "候选配置，未实测验证。Notion使用[data-block-id]标识内容块。\n"
        "注意事项：\n"
        "- Notion内容块（block）粒度比行更粗，一个block可能是标题/段落/列表项\n"
        "- 公开页面不需要登录，但私有页面需要\n"
        "- 部分页面嵌套在iframe中"
    ),
)

CONFLUENCE_CONFIG = PlatformConfig(
    name="confluence",
    display_name="Confluence",
    domains=["atlassian.net", "confluence"],
    container_selector="#main-content",
    line_selector=".wiki-content p, .wiki-content h1, .wiki-content h2, .wiki-content h3, .wiki-content li",
    scroll_step=600,
    wait_ms=800,
    initial_wait_ms=1500,
    max_no_new=3,
    max_iterations=30,
    container_selector_fallbacks=[
        ".wiki-content-container",
        "#content",
        ".aui-page-panel",
    ],
    line_selector_fallbacks=[
        "#main-content p",
        "#main-content h1, #main-content h2, #main-content h3",
        "p, h1, h2, h3, li",
    ],
    uses_virtual_scroll=False,
    body_is_scrollable=True,
    notes=(
        "候选配置，未实测验证。Confluence通常是服务端渲染的语义化HTML。\n"
        "注意事项：\n"
        "- Confluence内容结构化程度高，标题/段落/列表使用标准HTML标签\n"
        "- 企业自建Confluence可能有自定义主题和class\n"
        "- 通常不需要虚拟滚动，直接提取即可"
    ),
)

SHIMO_CONFIG = PlatformConfig(
    name="shimo",
    display_name="石墨文档",
    domains=["shimo.im", "shimo.cn"],
    container_selector=".document-container",
    line_selector=".editor-row, .paragraph, .text-block",
    scroll_step=400,
    wait_ms=1200,
    initial_wait_ms=2000,
    max_no_new=3,
    max_iterations=30,
    container_selector_fallbacks=[
        ".sheet-container",
        ".editor-container",
        "#canvas-container",
    ],
    line_selector_fallbacks=[
        ".cell-content",
        "[data-line-id]",
        ".text-run",
    ],
    uses_virtual_scroll=True,
    body_is_scrollable=False,
    notes="候选配置，未实测验证。石墨文档使用Canvas+DOM混合渲染。",
)

WPS_CONFIG = PlatformConfig(
    name="wps",
    display_name="WPS/金山文档",
    domains=["kdocs.cn", "wps.cn", "doc.wps.cn"],
    container_selector=".editor-scroll-container",
    line_selector=".page-text, .paragraph-text",
    scroll_step=500,
    wait_ms=1200,
    initial_wait_ms=2500,
    max_no_new=3,
    max_iterations=30,
    container_selector_fallbacks=[
        ".doc-container",
        "#kdocs-container",
        ".wps-doc-container",
    ],
    line_selector_fallbacks=[
        ".text-run",
        ".content-p",
        "p",
    ],
    uses_virtual_scroll=True,
    body_is_scrollable=False,
    notes="候选配置，未实测验证。WPS在线文档使用Canvas渲染概率较高。",
)


# ============================================================
# 注册表与查找函数
# ============================================================

PLATFORM_CONFIGS: dict[str, PlatformConfig] = {
    cfg.name: cfg for cfg in [
        FEISHU_CONFIG,
        DINGTALK_CONFIG,
        WECOM_CONFIG,
        YUQUE_CONFIG,
        NOTION_CONFIG,
        CONFLUENCE_CONFIG,
        SHIMO_CONFIG,
        WPS_CONFIG,
    ]
}


def detect_platform(url: str) -> Optional[str]:
    """根据URL检测所属SaaS平台。

    Args:
        url: 文档URL

    Returns:
        平台标识（feishu/dingtalk/wecom/...），未识别返回None
    """
    if not url:
        return None
    url_lower = url.lower()
    for name, cfg in PLATFORM_CONFIGS.items():
        if any(domain in url_lower for domain in cfg.domains):
            return name
    return None


def get_platform_config(name: str) -> Optional[PlatformConfig]:
    """根据平台名获取配置。

    Args:
        name: 平台标识

    Returns:
        PlatformConfig，未找到返回None
    """
    return PLATFORM_CONFIGS.get(name)


def list_supported_platforms() -> list[tuple[str, str, bool]]:
    """列出所有支持的平台及其验证状态。

    Returns:
        [(name, display_name, verified), ...]
        verified=True表示已通过实测验证
    """
    verified = {"feishu"}  # 目前只有飞书已实测验证
    return [
        (cfg.name, cfg.display_name, cfg.name in verified)
        for cfg in PLATFORM_CONFIGS.values()
    ]
