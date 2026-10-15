"""阅读时间统计（upstream: packages/shared/src/utils/readingTime.ts 1:1）。

计数口径：CJK 字符（日文假名/韩文/中文/扩展 B 区）逐字计词；ANSI 单词按空白边界；
标点不计。每分钟 200 词。
"""

from dataclasses import dataclass

_CJK_RANGES = (
    (0x3040, 0x309F),
    (0x4E00, 0x9FFF),
    (0xAC00, 0xD7A3),
    (0x20000, 0x2EBE0),
)
_ANSI_WORD_BOUND = " \n\r\t"
_PUNCT_RANGES = (
    (0x21, 0x2F),
    (0x3A, 0x40),
    (0x5B, 0x60),
    (0x7B, 0x7E),
    (0x3000, 0x303F),
    (0xFF00, 0xFFEF),
)


@dataclass(slots=True)
class ReadTimeResults:
    text: str
    time: int
    words: int
    minutes: float


def _in_ranges(code: int, ranges: tuple[tuple[int, int], ...]) -> bool:
    return any(lo <= code <= hi for lo, hi in ranges)


def reading_time(text: str, words_per_minute: int = 200) -> ReadTimeResults:
    """upstream: readingTime.ts:54。

    按 UTF-16 code unit 遍历，与 JS ``charCodeAt`` 口径一致（扩展 B 区字符在 JS
    中为代理对、不落入 CJK 范围；Python 若按码点遍历会产生计数偏差）。
    """
    # upstream: const normalizedText = `${text}\n`（末词靠追加换行形成边界）
    units = (text + "\n").encode("utf-16-le")

    def code_at(index: int) -> int | None:
        offset = index * 2
        if offset + 1 >= len(units):
            return None
        return int.from_bytes(units[offset : offset + 2], "little")

    def is_word_bound(ch: int | None) -> bool:
        return ch is not None and chr(ch) in _ANSI_WORD_BOUND

    words = 0
    start = 0
    end = len(text) - 1

    while start <= end and is_word_bound(code_at(start)):
        start += 1
    while end >= start and is_word_bound(code_at(end)):
        end -= 1

    index = start
    while index <= end:
        ch = code_at(index)
        nxt = code_at(index + 1)
        is_cjk = ch is not None and _in_ranges(ch, _CJK_RANGES)
        if is_cjk or (
            not is_word_bound(ch) and (is_word_bound(nxt) or (nxt is not None and _in_ranges(nxt, _CJK_RANGES)))
        ):
            words += 1

        if is_cjk:
            while index <= end:
                after = code_at(index + 1)
                if after is not None and (
                    _in_ranges(after, _PUNCT_RANGES) or is_word_bound(after)
                ):
                    index += 1
                else:
                    break
        index += 1

    minutes = words / words_per_minute
    time_ms = round(minutes * 60 * 1000)
    # JS: Math.ceil(Number(minutes.toFixed(2)))
    displayed = _ceil_to_fixed_2(minutes)

    return ReadTimeResults(text=f"{displayed} min read", time=time_ms, words=words, minutes=minutes)


def _ceil_to_fixed_2(value: float) -> int:
    import math

    return math.ceil(float(f"{value:.2f}"))
