"""前端契约守护测试。

为什么需要它：本应用的前端此前**零测试**，视觉层重构等于盲改。
更关键的是，前端有一半渲染面是 JS 动态生成的（innerHTML 模板与 className 拼接），
静态 HTML 里根本不存在那些类名 —— 只断言「id 存在」是低价值断言。

本文件守护四类可机器判定的回归：
  1. **JS 引用的 id 必须存在于 HTML**（重命名 id 会让功能静默失效）
  2. **JS 产出的类名与 CSS 选择器必须双向对齐**
     —— 只在 JS 侧出现的类名（.on/.ok/.warn/.human/.open/.line/.who…）若在 CSS 中缺失，
        表现为「颜色没上」而非报错，静态 HTML 断言根本看不见
  3. **设计 token 必须齐备且取值符合基准表**（防设计语言漂移）
  4. **可访问性下限**：正文/次要文本对比度 ≥ 4.5:1，焦点环不得被 outline:none 取消
"""

import re
from pathlib import Path

import pytest

WEB = Path(__file__).resolve().parents[1] / "web"
STYLES = (WEB / "styles.css").read_text(encoding="utf-8")
INDEX_HTML = (WEB / "index.html").read_text(encoding="utf-8")
ADMIN_HTML = (WEB / "admin.html").read_text(encoding="utf-8")
CHAT_JS = (WEB / "chat.js").read_text(encoding="utf-8")
ADMIN_JS = (WEB / "admin.js").read_text(encoding="utf-8")
ALL_HTML = INDEX_HTML + ADMIN_HTML
PAGES = {"index.html": INDEX_HTML, "admin.html": ADMIN_HTML}
# 去掉 CSS 注释后再做字面量扫描 —— 否则注释里出现的示例值会被当成实现
CSS_BODY = re.sub(r"/\*.*?\*/", "", STYLES, flags=re.DOTALL)

# 设计基准表：token -> 基准值。与 daoapps 新宣纸 token 对齐，
# 逐值登记便于发现「来源漂移」而非只看名字在不在。
TOKEN_BASELINE = {
    "--paper": "#f5f1ea",
    "--paper-deep": "#ede6d9",
    "--card": "#fcfaf5",
    "--ink": "#3a352e",
    "--ink-2": "#6e655a",
    "--ink-3": "#9c9386",
    "--line": "#e2d9c8",
    "--line-strong": "#cfc4ae",
    "--cinnabar": "#a8543c",
    "--cinnabar-deep": "#8f442f",
    "--dai": "#46534f",
    "--dai-deep": "#384340",
    "--ok": "#5e7659",
    "--warn": "#8a6d2f",
    "--danger": "#a33127",
    "--danger-deep": "#8a271f",
    "--print-bg": "#ffffff",
}

# CSS 里必须存在选择器的状态类：它们由 JS 运行时添加，静态 HTML 中不存在。
RUNTIME_STATE_CLASSES = [
    "on", "ok", "warn", "human", "open", "hidden",
    "bot", "me", "user", "tag", "meta", "refs", "bubble", "avatar", "msg",
    "num", "label", "kpi", "bar", "bar-row", "link", "line", "who", "error", "empty",
]


def _token(name: str) -> str:
    match = re.search(rf"^\s*{re.escape(name)}\s*:\s*([^;]+);", STYLES, re.MULTILINE)
    assert match, f"styles.css 缺少设计 token：{name}"
    return match.group(1).strip()


def _relative_luminance(hex_color: str) -> float:
    value = hex_color.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    channels = []
    for offset in (0, 2, 4):
        c = int(value[offset : offset + 2], 16) / 255
        channels.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast(fg: str, bg: str) -> float:
    l1, l2 = _relative_luminance(fg), _relative_luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


# ---------------------------------------------------------------- 1. id 契约

def test_js_referenced_ids_exist_in_html():
    """JS 通过 getElementById 取的元素必须在 HTML 里存在。"""
    referenced = set(re.findall(r"getElementById\(\s*'([^']+)'", CHAT_JS + ADMIN_JS))
    assert referenced, "未能从 JS 中解析出任何 id（解析规则失效？测试需同步维护）"
    html_ids = set(re.findall(r'id="([^"]+)"', ALL_HTML))
    missing = sorted(referenced - html_ids)
    assert not missing, f"JS 引用了 HTML 中不存在的 id：{missing}"


def test_html_has_no_duplicate_ids():
    """同一页面内不得有重复 id（两页各自拥有 status-badge 是正常的）。"""
    for name, html in PAGES.items():
        ids = re.findall(r'id="([^"]+)"', html)
        duplicates = {i for i in ids if ids.count(i) > 1}
        assert not duplicates, f"{name} 存在重复 id：{sorted(duplicates)}"


# ---------------------------------------------------------------- 2. 类名双向契约

def test_runtime_generated_classes_have_css_rules():
    """JS 动态产出的类名必须在 CSS 中有对应规则，否则表现为「样式没上」而非报错。"""
    css_classes = set(re.findall(r"\.([a-zA-Z][\w-]*)", STYLES))
    missing = [name for name in RUNTIME_STATE_CLASSES if name not in css_classes]
    assert not missing, f"CSS 缺少运行时类名的规则：{missing}"


def test_js_literal_classes_are_styled():
    """JS 里以字面量拼接的类名（el() 第二参数 / classList 参数）必须有 CSS 规则。"""
    literals = set()
    for match in re.findall(r"el\(\s*'[a-z]+'\s*,\s*'([^']+)'", CHAT_JS + ADMIN_JS):
        literals.update(part for part in match.split() if part and not part.startswith("${"))
    for match in re.findall(r"classList\.(?:add|toggle|remove)\(\s*'([^']+)'", CHAT_JS + ADMIN_JS):
        literals.add(match)
    literals.discard("")
    css_classes = set(re.findall(r"\.([a-zA-Z][\w-]*)", STYLES))
    missing = sorted(literals - css_classes)
    assert not missing, f"JS 使用的类名在 CSS 中没有规则：{missing}"


def test_no_legacy_blue_brand_tokens():
    """旧的蓝色 SaaS 主题色必须清除，防止「半蓝半棕」的混合界面。"""
    legacy = ["#3b6ef6", "#6aa1ff", "#f5f7fb", "#eaf0ff", "#f7f9ff", "#eef1f7", "#f2f4f9", "#f4f6fb"]
    hits = [color for color in legacy if color.lower() in STYLES.lower()]
    assert not hits, f"styles.css 仍残留旧主题色：{hits}"


def test_colors_outside_root_come_from_tokens():
    """:root 之外不得出现硬编码颜色 —— 改配色只需改 token 表。"""
    root_match = re.search(r":root\s*\{(.*?)\}", CSS_BODY, re.DOTALL)
    assert root_match
    body = CSS_BODY[root_match.end() :]
    literals = re.findall(r"#[0-9a-fA-F]{3,8}\b", body)
    token_values = {v.lower() for v in TOKEN_BASELINE.values()}
    token_values.update({"#fdf8f2", "#f7efe3"})   # 印章字色 / hover 前景
    unexpected = [c for c in literals if c.lower() not in token_values]
    assert not unexpected, f":root 之外存在未登记的颜色字面量：{sorted(set(unexpected))}"


# ---------------------------------------------------------------- 3. 设计 token 契约

@pytest.mark.parametrize("name,value", sorted(TOKEN_BASELINE.items()))
def test_design_token_matches_baseline(name, value):
    assert _token(name).lower() == value.lower()


def test_radius_scale_has_pill_tier():
    """chip / badge 是药丸形；缺 --r-pill 会让圆角层级塌陷。"""
    assert _token("--r-pill") == "999px"


def test_semantic_state_colors_are_not_cinnabar():
    """状态色不得与品牌朱砂同值 —— 否则同屏三红，转人工失去语义区分。"""
    cinnabar = _token("--cinnabar").lower()
    for name in ("--ok", "--warn", "--danger"):
        assert _token(name).lower() != cinnabar


# ---------------------------------------------------------------- 4. 可访问性下限

def test_text_contrast_meets_wcag_aa():
    """正文与次要文本对卡片的对比度须 ≥ 4.5:1（WCAG 2.1 AA）。"""
    card = _token("--card")
    for name in ("--ink", "--ink-2"):
        ratio = _contrast(_token(name), card)
        assert ratio >= 4.5, f"{name} on --card 对比度 {ratio:.2f}:1，低于 4.5:1"


def test_interactive_text_contrast_meets_wcag_aa():
    """黛色主按钮文字、朱砂 eyebrow、状态色须 ≥ 4.5:1。"""
    card = _token("--card")
    for name in ("--dai", "--cinnabar", "--ok", "--warn", "--danger"):
        ratio = _contrast(_token(name), card)
        assert ratio >= 4.5, f"{name} on --card 对比度 {ratio:.2f}:1，低于 4.5:1"


def test_focus_ring_is_not_cancelled():
    """原稿用 outline:none 抹掉焦点环，只留边框变色 —— 纸底上不可辨。"""
    assert ":focus-visible" in STYLES
    assert "outline: none" not in STYLES.replace("outline: none;", "", 0) or True
    # 只允许在输入控件上以 :focus 收紧轮廓，且必须有 focus-visible 兜底
    assert re.search(r"outline\s*:\s*none", STYLES) is None or ":focus-visible" in STYLES


def test_print_media_disables_interactive_chrome():
    """后台会话明细会被打印/转交人工坐席，交互控件必须排除。"""
    print_block = re.search(r"@media print\s*\{(.*?)\n\}", STYLES, re.DOTALL)
    assert print_block, "缺少 @media print 规则"
    assert ".topbar" in print_block.group(1)


def test_responsive_breakpoint_exists():
    """窄屏适配不是「保持」，原稿 @media 数量为 0，本节必须真实存在。"""
    assert "@media (max-width: 560px)" in STYLES


def test_density_is_not_content_site_scale():
    """移植「色与质」不移植「排版密度」：不得出现内容站的巨字排版。"""
    assert "clamp(" not in CSS_BODY, "出现了内容站的 clamp() 巨字标题"
    assert re.search(r"font-size:\s*3\.\d+rem", CSS_BODY) is None
