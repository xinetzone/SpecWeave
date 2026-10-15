"""中英混合文本相似度：零依赖、免向量、可解释。

从第一性原理推下来只有一句话：**关联的本质是共享语义单元**。

- 中文没有空格，词边界不可靠，最小稳定单元是**汉字二元组**（"待办"→"待办"，
  "整理待办"→"理待"/"待办"，二者共享 "待办"）；
- 二元组只在**标点切出的段内**生成——跨标点配对会造出 "法把" 这类假词，
  既污染标签又凭空制造相似度（详见 :func:`_cjk_segments`）；
- 英文/数字有天然分隔符，最小稳定单元是**词元**。

于是指纹 = 拉丁词元 ∪ 汉字二元组，重合度用 Dice 系数：

    sim = 2 · |A ∩ B| / (|A| + |B|)

选 Dice 而非 Jaccard，是因为录入内容长度差异极大（一句话 vs 一整篇资料），
Dice 对长度不平衡更宽容——长文档不会因为分母大而把真正相关的短条目压到阈值以下。

不引入向量模型是**刻意**的：本应用要能在零密钥环境下完整工作，
关联能力若依赖 embedding 端点，降级后就变成"点了没反应"，违背地基约定。
"""

import re
from collections import Counter

_LATIN_RE = re.compile(r"[A-Za-z]+|\d+")
_CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")

# 中文停用字：出现频次极高但几乎不携带区分度，进指纹只会稀释信号。
_STOP_ZH = frozenset(
    "的了是在我有和就不人都一一个上也很到说要去你会着没有看好自己这那"
    "被把从对与为以但还吧呢啊哦嘛过可以这个我们他们什么怎么因为所以"
)

_STOP_EN = frozenset(
    {
        "the", "a", "an", "and", "or", "but", "if", "then", "than", "that",
        "this", "these", "those", "is", "are", "was", "were", "be", "been",
        "am", "do", "does", "did", "to", "of", "in", "on", "at", "for",
        "with", "as", "by", "it", "its", "i", "you", "he", "she", "we",
        "they", "my", "your", "his", "her", "our", "their", "not", "no",
    }
)

# URL 结构性片段：复制链接是很自然的录入方式，但 http/com/www 不是内容。
_STOP_URL = frozenset(
    {"http", "https", "www", "com", "cn", "org", "net", "io", "html", "htm", "php", "index"}
)


def _latin_tokens(text: str) -> list[str]:
    """拉丁词元：小写化，丢弃单字符、停用词与 URL 结构片段。"""
    out: list[str] = []
    for raw in _LATIN_RE.findall(text):
        token = raw.lower()
        if len(token) > 1 and token not in _STOP_EN and token not in _STOP_URL:
            out.append(token)
    return out


def _cjk_segments(text: str) -> list[str]:
    """按非汉字字符切段。

    切段是**正确性**要求而非优化：若把过滤后的字序列直接拼成二元组，
    标点两侧的字会被强行配对——"想法：把周报" 会产出 "法把"，"周报聚合"
    会产出 "报聚"。这些假词同时污染标签与关联判断，且会凭空制造相似度。
    每段内部取二元组后，"跨标点的相邻字" 这个伪关系自然消失。
    """
    segments: list[str] = []
    buffer: list[str] = []
    for char in text:
        if _CJK_RE.match(char) and char not in _STOP_ZH:
            buffer.append(char)
        elif buffer:
            segments.append("".join(buffer))
            buffer = []
    if buffer:
        segments.append("".join(buffer))
    return segments


def _cjk_units(text: str) -> list[str]:
    """段内汉字二元组；单字段落退化为单字，避免短句指纹为空。"""
    out: list[str] = []
    for segment in _cjk_segments(text):
        if len(segment) == 1:
            out.append(segment)
            continue
        out.extend(segment[index:index + 2] for index in range(len(segment) - 1))
    return out


def fingerprint(text: str) -> Counter:
    """文本 → 语义单元多重集。"""
    counts: Counter = Counter(_latin_tokens(text))
    counts.update(_cjk_units(text))
    return counts


def similarity(a: str, b: str) -> float:
    """Dice 系数，取值 [0, 1]。任一指纹为空则返回 0.0。"""
    fa, fb = fingerprint(a), fingerprint(b)
    total_a = sum(fa.values())
    total_b = sum(fb.values())
    if not total_a or not total_b:
        return 0.0
    overlap = sum((fa & fb).values())
    return round(2.0 * overlap / (total_a + total_b), 4)


def keyword_score(query: str, text: str) -> float:
    """检索打分：查询词对文本的覆盖率 × 命中强度。

    与 :func:`similarity` 不同，检索是**单向**的——查询很短、文档很长，
    Dice 会被长文档的分母压扁，所以这里改用「查询侧单元有多少落在文档里」。
    """
    fq, ft = fingerprint(query), fingerprint(text)
    if not fq or not ft:
        return 0.0
    hit = sum((fq & ft).values())
    return round(hit / sum(fq.values()), 4)


def top_terms(text: str, limit: int = 5) -> list[str]:
    """提取高频语义单元，作为无大模型时的标签兜底。"""
    counts = fingerprint(text)
    if not counts:
        return []
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [term for term, _ in ranked[:limit]]
