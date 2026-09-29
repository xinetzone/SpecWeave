"""提示词压缩服务：5 档规则式压缩 + 保护片段逐字保留 + 自检回退。

**文档证据**（被复刻产品设置面板，源文档 F-095）：
- 5 档提示词压缩：Lite≈15% / Standard≈30% / Aggressive≈50% / Ultra≈75% /
  RTK（工具链去重）60–90%。
- 页面原文：压缩率为**估算值**（规则式实现）；代码块 / 链接 / JSON
  均原样保留，绝不损坏。
- 因此 ``CompressionResult.claimed_ratio`` 只是厂商自述估算值，本实现不把它
  当作承诺指标，也不据此校验 ``estimated_ratio``。

**本实现的合理默认**（源产品为闭源算法，下面口径由本仓库自行定义）：
- 受保护片段的识别范围：Markdown 围栏代码块、内联代码、URL、可解析的 JSON
  对象/数组片段。
- 各档位的具体规则与递进顺序（见 :func:`compress_prompt` 内注释）。
- 自检口径：受保护片段必须逐字仍在结果中且结果非空，否则 ``refused=True``
  并原样返回原文。
- 全文皆为受保护片段（例如纯 JSON / 纯代码块）时判定「无可压缩内容」，
  同样 ``refused=True`` 并原样返回。

实现仅依赖标准库，无第三方依赖。
"""

import json
import re
from dataclasses import dataclass

from ..errors import ByokError, ErrorCode
from ..models import COMPRESSION_SPECS, CompressionLevel

__all__ = ["CompressionResult", "compress_prompt"]

#: 档位递进顺序（下标即“强度等级”，高档位包含低档位的全部规则）
LEVEL_ORDER: tuple[CompressionLevel, ...] = (
    CompressionLevel.LITE,
    CompressionLevel.STANDARD,
    CompressionLevel.AGGRESSIVE,
    CompressionLevel.ULTRA,
    CompressionLevel.RTK,
)

#: 受保护片段的类型标识（``protected`` 字段按此顺序输出）
PROTECT_ORDER: tuple[str, ...] = ("code_block", "inline_code", "url", "json")

#: 占位符：``\x00<index>\x00``，索引指向受保护片段列表
PLACEHOLDER_TEMPLATE = "\x00%d\x00"
_PLACEHOLDER_RE = re.compile(r"\x00(\d+)\x00")

#: 受保护片段的起始特征（用于跳跃扫描，避免逐字符匹配）
_START_RE = re.compile(r"```|~~~|`|https?://|[{[]")

#: 围栏代码块```` ```lang\n...``` ````（要求成对且闭合）
_FENCE_RE = re.compile(r"(`{3,}|~{3,})[^\n]*\n.*?\1", re.DOTALL)

#: 内联代码 `` `code` ``
_INLINE_RE = re.compile(r"`[^`\n]+`")

#: URL（后续剥离结尾标点，避免把句号吞进链接）
_URL_RE = re.compile(r"https?://\S+")

#: JSON 片段的最大扫描长度，防止极端输入上的超长回退
_JSON_MAX_SPAN = 20000

#: 冗余修饰词（合理默认）：英文按词边界整词移除
_EN_FILLERS: tuple[str, ...] = (
    "basically",
    "actually",
    "simply",
    "really",
    "honestly",
    "certainly",
    "kindly",
    "please",
    "quite",
    "very",
)
_EN_FILLER_RE = re.compile(rf"\b(?:{'|'.join(_EN_FILLERS)})\b[ \t]*", re.IGNORECASE)

#: 冗余修饰词（合理默认）：中文按字面量移除，均为副词/话语标记
_CN_FILLERS: tuple[str, ...] = (
    "换句话说",
    "总的来说",
    "顺便提一下",
    "基本上",
    "麻烦你",
    "非常",
    "极其",
    "其实",
)

#: 句子切分：保留末尾标点/换行作为句子的一部分
_SENT_SPLIT_RE = re.compile(r"(?<=[。！？!?;\n])")

#: 工具链输出行特征（git diff / grep / 日志；合理默认）
_TOOL_LINE_RE = re.compile(
    r"^\s*(?:"
    r"diff --git |index [0-9a-f]|@@ |--- |\+\+\+ |[-+]\S|"
    r"[\w./-]+:\d+[: ]|"
    r"\[\d{4}-|"
    r"\d{4}-\d{2}-\d{2}|"
    r"(?:INFO|WARN|WARNING|ERROR|DEBUG|TRACE)[:\s]"
    r")"
)


@dataclass(frozen=True)
class CompressionResult:
    """一次提示词压缩的结果。

    - ``estimated_ratio``：实测压缩比例 ``(原长-压后长)/原长``，落在 [0, 1]。
    - ``claimed_ratio``：``COMPRESSION_SPECS`` 中的厂商自述估算值字符串，
      **不是**承诺指标。
    - ``refused``：自检判定压缩会损坏内容时为 True，此时 ``text`` 等于原文。
    """

    text: str
    original_length: int
    compressed_length: int
    estimated_ratio: float
    claimed_ratio: str
    level: CompressionLevel
    refused: bool
    protected: tuple[str, ...]


def _json_span(text: str, start: int) -> int | None:
    """尝试从 ``start`` 解析一个 JSON 对象/数组，返回结束下标（不含）或 None。

    仅当括号配对且能被 ``json.loads`` 解析为 dict/list 时才判定为 JSON 片段，
    避免把散文里的 ``{name}`` 之类误判为 JSON。
    """
    pairs = {"}": "{", "]": "["}
    stack: list[str] = []
    in_string = False
    escaped = False
    limit = min(len(text), start + _JSON_MAX_SPAN)
    i = start
    while i < limit:
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
        elif ch in "{[":
            stack.append(ch)
        elif ch in "}]":
            if not stack or stack.pop() != pairs[ch]:
                return None
            if not stack:
                candidate = text[start : i + 1]
                if len(candidate) < 2:
                    return None
                try:
                    parsed = json.loads(candidate)
                except ValueError:
                    return None
                if isinstance(parsed, dict | list):
                    return i + 1
                return None
        i += 1
    return None


def _match_protected(text: str, start: int) -> tuple[str, int] | None:
    """判定 ``start`` 处是否为受保护片段，返回 ``(类型, 结束下标)``。"""
    fence = _FENCE_RE.match(text, start)
    if fence is not None:
        return "code_block", fence.end()
    inline = _INLINE_RE.match(text, start)
    if inline is not None:
        return "inline_code", inline.end()
    url = _URL_RE.match(text, start)
    if url is not None:
        raw = url.group()
        trimmed = raw.rstrip(".,;:!?")
        end = start + len(trimmed) if trimmed else url.end()
        return "url", end
    if text[start] in "{[":
        end = _json_span(text, start)
        if end is not None:
            return "json", end
    return None


def extract_protected(text: str) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    """扫描文本，把受保护片段替换为占位符。

    返回 ``(工作文本, 受保护片段元组, 类型元组)``；工作文本中除占位符外的
    部分即为可安全压缩的自由文本。
    """
    spans: list[str] = []
    kinds: list[str] = []
    chunks: list[str] = []
    cursor = 0
    while cursor < len(text):
        found = _START_RE.search(text, cursor)
        if found is None:
            break
        start = found.start()
        if start > cursor:
            chunks.append(text[cursor:start])
        matched = _match_protected(text, start)
        if matched is None:
            # 未闭合的反引号、非 JSON 的括号等：按普通字符处理
            chunks.append(text[start])
            cursor = start + 1
            continue
        kind, end = matched
        chunks.append(PLACEHOLDER_TEMPLATE % len(spans))
        spans.append(text[start:end])
        kinds.append(kind)
        cursor = end
    chunks.append(text[cursor:])
    return "".join(chunks), tuple(spans), tuple(kinds)


def _restore(working: str, spans: tuple[str, ...]) -> str:
    """把占位符还原为原始片段（逐字）。"""

    def _sub(match: re.Match) -> str:
        idx = int(match.group(1))
        return spans[idx] if 0 <= idx < len(spans) else match.group(0)

    return _PLACEHOLDER_RE.sub(_sub, working)


def _has_placeholder(segment: str) -> bool:
    """该片段是否锚定了受保护内容（锚定片段永不被删除）。"""
    return _PLACEHOLDER_RE.search(segment) is not None


def _split_sentences(text: str) -> list[str]:
    return [part for part in _SENT_SPLIT_RE.split(text) if part]


def _drop_fillers(text: str) -> str:
    """去除冗余修饰词（Aggressive 起）。"""
    text = _EN_FILLER_RE.sub("", text)
    for filler in _CN_FILLERS:
        text = text.replace(filler, "")
    return text


def _dedupe_sentences(text: str) -> str:
    """去除重复句子（Aggressive 起）；含占位符的句子一律保留。"""
    seen: set[str] = set()
    kept: list[str] = []
    for sentence in _split_sentences(text):
        if _has_placeholder(sentence):
            kept.append(sentence)
            continue
        key = sentence.strip()
        if not key:
            kept.append(sentence)
            continue
        if key in seen:
            continue
        seen.add(key)
        kept.append(sentence)
    return "".join(kept)


def _trim_long_paragraphs(text: str) -> str:
    """长段落摘要式裁剪（Ultra 起）：保留首尾句，裁掉中段。"""
    paragraphs: list[str] = []
    for paragraph in text.split("\n\n"):
        sentences = _split_sentences(paragraph)
        droppable = [
            idx
            for idx, sentence in enumerate(sentences)
            if sentence.strip() and not _has_placeholder(sentence)
        ]
        if len(sentences) > 3 and len(droppable) >= 3:
            middle = set(droppable[1 : len(droppable) - 1])
            sentences = [s for idx, s in enumerate(sentences) if idx not in middle]
        paragraphs.append("".join(sentences))
    return "\n\n".join(paragraphs)


def _normalize_tool_line(line: str) -> str:
    """归一化工具链输出行：抹掉时间戳、耗时与数字差异，便于识别重复。"""
    line = re.sub(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?", "<TIME>", line)
    line = re.sub(r"\b\d+(?:\.\d+)?\s*(?:ms|s)\b", "<DUR>", line)
    return re.sub(r"\d+", "#", line).strip()


def _dedupe_tool_lines(text: str) -> str:
    """工具链重复行去重（RTK 档）：保留首次出现，后续同构行折叠。"""
    seen: set[str] = set()
    kept: list[str] = []
    for line in text.split("\n"):
        if _has_placeholder(line):
            kept.append(line)
            continue
        stripped = line.strip()
        if len(stripped) >= 8 and _TOOL_LINE_RE.match(line):
            key = _normalize_tool_line(stripped)
            if key in seen:
                continue
            seen.add(key)
        kept.append(line)
    return "\n".join(kept)


def _compress_free(working: str, rank: int) -> str:
    """对自由文本（占位符已剔除受保护内容）按档位递进压缩。"""
    # Lite：折叠多余空行与行尾空白
    working = re.sub(r"[^\S\n]+\n", "\n", working)
    working = re.sub(r"\n{3,}", "\n\n", working)
    if rank >= 1:
        # Standard：合并行内连续空白，清理空白行
        working = re.sub(r"[^\S\n]{2,}", " ", working)
        working = re.sub(r"\n[^\S\n]+\n", "\n\n", working)
        working = re.sub(r"\n{3,}", "\n\n", working)
    if rank >= 2:
        # Aggressive：去冗余修饰词 + 重复句去重
        working = _drop_fillers(working)
        working = _dedupe_sentences(working)
    if rank >= 3:
        # Ultra：长段落句子级去重与摘要式裁剪
        working = _dedupe_sentences(working)
        working = _trim_long_paragraphs(working)
    if rank >= 4:
        # RTK：工具链输出（git diff / grep / 日志）重复行去重
        working = _dedupe_tool_lines(working)
        working = re.sub(r"\n{3,}", "\n\n", working)
    return working.strip()


def _self_check(result: str, spans: tuple[str, ...]) -> bool:
    """自检：受保护片段必须逐字仍在结果中，且结果不能为空。"""
    if not result.strip():
        return False
    return all(span in result for span in spans)


def _result(
    text: str,
    original: str,
    level: CompressionLevel,
    claimed_ratio: str,
    refused: bool,
    protected: tuple[str, ...],
) -> CompressionResult:
    """统一构造结果；``refused`` 时 ``text`` 已等于原文，故压缩比例为 0。"""
    original_length = len(original)
    compressed_length = len(text)
    ratio = 0.0
    if refused:
        compressed_length = original_length
    elif original_length:
        ratio = (original_length - compressed_length) / original_length
        ratio = max(0.0, min(1.0, ratio))
    return CompressionResult(
        text=text,
        original_length=original_length,
        compressed_length=compressed_length,
        estimated_ratio=ratio,
        claimed_ratio=claimed_ratio,
        level=level,
        refused=refused,
        protected=protected,
    )


def compress_prompt(text: str, level: CompressionLevel) -> CompressionResult:
    """按档位压缩提示词；受保护片段（代码块 / 链接 / JSON）逐字保留。

    参数
    ----
    text:
        原始提示词。空串或纯空白输入直接原样返回。
    level:
        :class:`CompressionLevel` 枚举；也可传其字符串值（如 ``"ultra"``），
        非法值抛 :class:`ByokError`（``ErrorCode.INVALID_REQUEST``）。

    无法安全压缩时（全文皆受保护片段，或自检发现受保护片段丢失/结果为空）
    返回 ``refused=True`` 且 ``text`` 为原文。
    """
    if not isinstance(level, CompressionLevel):
        try:
            level = CompressionLevel(str(level))
        except ValueError as exc:
            raise ByokError(ErrorCode.INVALID_REQUEST, f"未知的压缩档位: {level!r}") from exc

    original = text if isinstance(text, str) else ""
    claimed_ratio = COMPRESSION_SPECS[level][0]

    if not original.strip():
        # 空输入：无需压缩，也不存在可损坏的内容
        return _result(original, original, level, claimed_ratio, False, ())

    working, spans, kinds = extract_protected(original)
    protected = tuple(kind for kind in PROTECT_ORDER if kind in kinds)

    free_text = _PLACEHOLDER_RE.sub("", working)
    if not free_text.strip():
        # 全文皆为受保护片段（纯代码块 / 纯 JSON 等）：无可压缩内容，拒绝压缩
        return _result(original, original, level, claimed_ratio, True, protected)

    compressed = _restore(_compress_free(working, LEVEL_ORDER.index(level)), spans)
    if not _self_check(compressed, spans):
        # 自检不通过：原样返回，绝不损坏内容
        return _result(original, original, level, claimed_ratio, True, protected)

    return _result(compressed, original, level, claimed_ratio, False, protected)
