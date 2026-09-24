"""归档 HTML → RAG 纯文本（无 IO 纯函数层，Task 10 / AC-11、AC-18）。

两层职责：

- :func:`html_to_plain_text`：从本地化归档 ``article.html`` 的正文容器
  （``#js_content``）提取段落结构完整的纯文本。块级元素转换行、列表保留
  短横线、代码块保留缩进、图片节点移除、语音/视频等富媒体保留为
  「［音频：标题］」占位行（媒体语义不丢失，真实文件由 media 表与归档目录承载）。
- :func:`clean_plain_text`：保守清洗微信排版模板噪声（文末推广、二维码
  关注引导、互动按钮文案、重复声明、装饰符号行）。

清洗误伤是本模块的首要风险，故遵循两条纪律：

1. **整行强匹配**：噪声判定只作用于去除空白后的短行（≤ ``_MAX_NOISE_LINE_LEN``
   字），且行内必须出现明确的引导动作词（关注/扫码/在看/转发/赞赏/二维码），
   正文段落中讨论"二维码原理"等内容不会被删除；
2. **尾部锚定**：平台推荐块（如「喜欢此内容的人还喜欢」）只在文章后半部
   命中锚点时整段裁剪，锚点出现在前半部分时保守保留。
"""

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup, NavigableString, Tag

CONTENT_SELECTOR = "#js_content"

# <pre> 代码行行首哨兵：规范化阶段据此保留缩进，输出前移除
_PRE_SENTINEL = "\x00"

# 块级元素：闭合处产生换行边界
_BLOCK_TAGS = {
    "p", "div", "section", "ul", "ol", "li",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "blockquote", "tr", "table", "thead", "tbody",
    "header", "footer", "figure", "figcaption", "hr",
}
# 无文本价值节点
_DROP_TAGS = {"script", "style", "noscript", "svg", "img", "input"}
# 富媒体自定义标签 → 占位行前缀
_MEDIA_PREFIX = {
    "mpvoice": "音频",
    "mp-audio": "音频",
    "mpvideo": "视频",
    "mpvideosnap": "视频",
    "mp-common-videosnap": "视频",
    "qqmusic": "音乐",
    "mpmusic": "音乐",
}
_MEDIA_TITLE_ATTRS = ("data-name", "name", "title", "alt", "data-title")

_MAX_NOISE_LINE_LEN = 40

# 整行引导噪声（动作词明确；要求整行语义被引导语占据）
_NOISE_LINE_PATTERNS = tuple(
    re.compile(pattern)
    for pattern in (
        r"^长按.{0,12}(二维码|识别).{0,12}$",
        r"^(微信)?扫一扫.{0,12}(关注|二维码).{0,12}$",
        r"^扫码关注.{0,20}$",
        r"^点击上方.{0,12}(蓝字|公众号|关注).{0,16}$",
        r"^(欢迎)?关注(公众号|我们|本号|作者).{0,20}$",
        r"^(点|给)个?\s*(在看|赞|赞赏|好看).{0,12}$",
        r"^(点亮|动动手指).{0,8}(在看|赞).{0,12}$",
        r"^(在看|赞|好看|转发|分享)\s*\+?\s*(在看|赞|转发|分享|朋友圈)?$",
        r"^(欢迎)?(转发|分享)(到|至|给)?(朋友圈|微信群|群聊|好友|大家).{0,12}$",
        r"^点击.{0,8}(阅读原文|「阅读原文」|下方).{0,12}$",
        r"^(微信)?(扫一扫|长按).{0,8}赞赏.{0,12}$",
        r"^(觉得好看|喜欢).{0,12}(点|点亮|在看|分享|赞).{0,12}$",
        r"^本文.{0,6}(欢迎|仅供).{0,12}$",
    )
)
# 纯装饰行：剥离装饰字符后为空
_DECORATION_CHARS = "·•・-—_*＝=~～～|▲△●◆■★☆✦▶➤➜›»「」『』□◇oO0 "
_DECORATION_RE = re.compile(f"^[{re.escape(_DECORATION_CHARS)}]+$")

# 文末平台模板块锚点（命中后该行及之后的推荐列表整体裁剪）
_TAIL_ANCHORS = (
    "喜欢此内容的人还喜欢",
    "微信扫一扫赞赏作者",
    "长按识别二维码关注",
    "扫码关注我们",
)


@dataclass(frozen=True, slots=True)
class CleanStats:
    """清洗动作计数（可观测性：导出摘要打印，TR-10.2 抽样评阅参考）。"""

    removed_noise_lines: int = 0
    collapsed_duplicates: int = 0
    trimmed_tail_lines: int = 0

    @property
    def touched(self) -> bool:
        return bool(
            self.removed_noise_lines
            or self.collapsed_duplicates
            or self.trimmed_tail_lines
        )


# ---- HTML → 纯文本 ------------------------------------------------------


def _media_placeholder(tag: Tag) -> str:
    kind = _MEDIA_PREFIX.get(tag.name.lower(), "媒体")
    title = ""
    for attr in _MEDIA_TITLE_ATTRS:
        value = (tag.get(attr) or "").strip()
        if value:
            title = value
            break
    return f"［{kind}：{title}］" if title else f"［{kind}］"


def _prepare_content(soup: BeautifulSoup) -> Tag:
    """定位正文容器并就地规范化（去噪节点、块边界插换行、富媒体占位）。"""
    content = soup.select_one(CONTENT_SELECTOR)
    if content is None:
        content = soup.find("article") or soup.find("body") or soup

    for tag in content.find_all(list(_DROP_TAGS)):
        tag.decompose()

    # 富媒体自定义标签 → 占位文本（保留媒体语义，供检索与人工识别）
    for tag in content.find_all(True):
        if tag.name and tag.name.lower() in _MEDIA_PREFIX:
            tag.replace_with(NavigableString(_media_placeholder(tag)))

    # <pre><code> 保留原始缩进：逐行打哨兵标记，规范化时不做 lstrip
    for pre in content.find_all("pre"):
        code_lines = pre.get_text().strip("\n").splitlines()
        marked = "\n" + "\n".join(_PRE_SENTINEL + line for line in code_lines) + "\n"
        pre.replace_with(NavigableString(marked))

    # 块级闭合边界：在块标签末尾追加换行，get_text 后形成段落分隔
    for tag in content.find_all(list(_BLOCK_TAGS)):
        tag.append("\n")
    for br in content.find_all("br"):
        br.replace_with("\n")
    for li in content.find_all("li"):
        li.insert(0, NavigableString("- "))

    return content


def _normalize_lines(raw_text: str) -> list[str]:
    """get_text 原始输出 → 规范行列表（空白收敛、空行折叠为段落分隔）。"""
    lines: list[str] = []
    blank = False
    for raw_line in raw_text.splitlines():
        # \xa0/\u3000 等不间断空白规范化；行内 tab 转空格；保留行内普通空格（代码缩进）
        line = raw_line.replace("\xa0", " ").replace("\u3000", " ").replace("\t", " ")
        if line.startswith(_PRE_SENTINEL):
            # 代码行：去哨兵、仅去尾部空白，保留缩进
            lines.append(line[1:].rstrip())
            blank = False
            continue
        line = line.rstrip()
        stripped = line.strip()
        if not stripped:
            if not blank:
                lines.append("")
            blank = True
            continue
        blank = False
        lines.append(stripped)

    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return lines


def html_to_plain_text(raw_html: str) -> str:
    """归档文章 HTML → 段落结构完整的纯文本。

    容器选择顺序：``#js_content`` → ``<article>`` → ``<body>`` → 文档根，
    兼容归档 HTML 与容器缺失的畸形页。
    """
    soup = BeautifulSoup(raw_html, "html.parser")
    content = _prepare_content(soup)
    lines = _normalize_lines(content.get_text())
    return "\n".join(lines)


# ---- 模板噪声清洗 -------------------------------------------------------


def _is_indented(line: str) -> bool:
    """代码缩进行保护：中文公众号正文段落顶格排版，前导空白即代码特征。"""
    return line.startswith((" ", "\t"))


def _is_noise_line(line: str) -> bool:
    if _is_indented(line):
        return False
    if len(line) > _MAX_NOISE_LINE_LEN:
        return False
    if _DECORATION_RE.match(line):
        return True
    return any(pattern.match(line) for pattern in _NOISE_LINE_PATTERNS)


def clean_plain_text(text: str) -> tuple[str, CleanStats]:
    """清洗纯文本模板噪声，返回 ``(清洗后文本, 动作统计)``。

    操作：①全文删除短引导/装饰行（整行强匹配）；②相邻完全重复行折叠；
    ③后半部平台推荐锚点整段裁剪。输入无尾换行，输出同样无尾换行。
    """
    lines = text.splitlines()
    total = len(lines)

    # ① 整行强噪声过滤
    kept: list[str] = []
    removed_noise = 0
    for line in lines:
        if line and _is_noise_line(line):
            removed_noise += 1
            continue
        kept.append(line)

    # ③ 平台推荐块尾部裁剪（锚点须位于文章后半部，防正文误伤）
    trimmed_tail = 0
    for index, line in enumerate(kept):
        if (
            not _is_indented(line)
            and len(line) <= _MAX_NOISE_LINE_LEN
            and index >= max(1, len(kept) // 2)
            and any(anchor in line for anchor in _TAIL_ANCHORS)
        ):
            trimmed_tail = len(kept) - index
            del kept[index:]
            break

    # ② 相邻完全重复行折叠（空行不参与）
    deduped: list[str] = []
    duplicates = 0
    for line in kept:
        if line and deduped and line == deduped[-1]:
            duplicates += 1
            continue
        deduped.append(line)

    # 过滤后再收敛一次空行（代码缩进行受保护，不走 _normalize_lines 的 strip）
    normalized: list[str] = []
    blank = False
    for line in "\n".join(deduped).splitlines():
        if _is_indented(line):
            normalized.append(line.rstrip())
            blank = False
        elif not line.strip():
            if not blank:
                normalized.append("")
            blank = True
        else:
            normalized.append(line.strip())
            blank = False
    while normalized and not normalized[0]:
        normalized.pop(0)
    while normalized and not normalized[-1]:
        normalized.pop()
    stats = CleanStats(
        removed_noise_lines=removed_noise,
        collapsed_duplicates=duplicates,
        trimmed_tail_lines=trimmed_tail,
    )
    return "\n".join(normalized), stats
