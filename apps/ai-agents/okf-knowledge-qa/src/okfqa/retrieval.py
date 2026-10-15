"""知识检索：SQLite FTS5（trigram 分词）+ BM25 排序。

为什么用 FTS5 而不是手写 TF-IDF 倒排索引：
- 语料 19.2M 字符、单束最大 786K 字符且分布极斜（p50=615, p99=100K），按知识包分片极不均衡；
- FTS5 由 SQLite 维护倒排索引并按页惰性读取，冷启动零加载，查询毫秒级；
- sqlite3 属于标准库，不引入任何第三方检索依赖。

三条失效边界（对抗性审查 V1/V2/V6），本模块专门加固：
- V1：FTS5 的 MATCH 有自己的查询语法，用户输入含 `.`、`"`、`*`、`-` 等字符会抛
  ``fts5: syntax error`` 导致整个检索崩溃。故必须先抽词再用双引号包裹转义。
- V2：trigram 分词器以三元组为最小单位，长度 < 3 的查询词（如 ``AI``、``C++``）
  永远无法命中。故必须提供 LIKE 兜底路径。
- V6：中文无词边界，整串作短语查询要求原文逐字连续匹配，
  「道法自然是什么」这类自然语言问句必然零命中。故中文串切重叠三元组后 OR 连接。
"""

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

# BM25 列权重（对应 title, body, 四个 UNINDEXED 列）。
# 标题仅 3 倍而非 10 倍：早期取 10 倍时，标题命中两个泛化三元组
# （如「复利的三层结构」）就能压过正文命中三个专有三元组（如 OKF 三层结构原文），
# 实测导致「OKF 三层结构」类查询被无关的「三层结构」标题劫持。
BM25_WEIGHTS = "3.0, 1.0, 0.0, 0.0, 0.0, 0.0"

MIN_TERM_LEN = 3          # trigram 分词器的最小可匹配长度
MAX_QUERY_TERMS = 24      # 参与检索的三元组上限，避免超长查询拖慢 BM25
LIKE_FALLBACK_LIMIT = 40  # 兜底 LIKE 扫描的候选上限

# 抽取查询词元：中文串 / 拉丁+数字混合词 / 纯数字（含小数点版本号）
TERM_RE = re.compile(r"[\u4e00-\u9fff]+|[A-Za-z][A-Za-z0-9_.+#-]*|\d+(?:\.\d+)*")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")

# 中文高频功能词与疑问式套话。
# 它们几乎出现在所有文档里却几乎不携带区分度：若参与 OR 检索，
# 「道法自然是什么意思」会被遍布 FAQ 标题的「是什么意思」主导，
# 真正的「道法自然」反而被挤出前列（对抗性审查 V7）。故检索前先行剥离。
STOP_PATTERNS = [
    "是什么意思", "什么意思", "是什么", "什么是", "有哪些", "介绍一下", "请介绍",
    "我想知道", "请问", "帮我", "如何", "怎么", "怎样", "为什么", "为何",
    "说说", "讲讲", "谈谈", "以及", "关于", "对于",
    "的", "了", "和", "与", "或", "在", "是", "有", "也", "就", "都",
    "而", "及", "等", "吗", "呢", "吧", "啊", "什么", "这个", "那个",
    "可以", "需要", "应该",
]
# 长词优先，避免「有哪些」被先拆成「有」而残留「哪些」
_STOP_RE = re.compile(
    "|".join(sorted((re.escape(p) for p in STOP_PATTERNS), key=len, reverse=True))
)


def strip_stopwords(query: str) -> str:
    """剥离中文功能词与疑问套话，保留内容词。"""
    return _STOP_RE.sub(" ", query)


class KnowledgeBaseUnavailable(RuntimeError):
    """检索索引缺失或不可读。

    按「显式报错优于静默降级」原则，索引缺失必须暴露为明确的 503，
    而不是返回空结果让用户误以为知识库里没有答案。
    """


@dataclass(frozen=True)
class Hit:
    """一条检索命中的知识片段。"""

    chunk_id: int
    title: str
    body: str
    bundle: str
    grp: str
    domain: str
    path: str
    score: float


def _expand(term: str) -> list[str]:
    """把词元展开为可交给 trigram 检索的最小单元。

    中文没有词边界：若把整串当作短语提交，FTS5 会要求原文逐字连续匹配，
    于是「道法自然是什么」这类自然语言问句必然零命中（对抗性审查 V6）。
    故中文串切分为重叠三元组，配合外层的 OR 语义，由 BM25 按命中三元组
    的数量与 IDF 权重排序——召回与相关性同时保住。

    拉丁/数字词保留整词：FTS5 会自行切三元组并要求全部命中，
    等价于整词精确匹配，这正是对英文术语所期望的行为。
    """
    if len(term) < MIN_TERM_LEN:
        return []
    if not CJK_RE.match(term):
        return [term]
    if len(term) == MIN_TERM_LEN:
        return [term]
    return [term[i : i + MIN_TERM_LEN] for i in range(len(term) - MIN_TERM_LEN + 1)]


def build_match_expr(query: str) -> str | None:
    """把自由文本查询编译为安全的 FTS5 MATCH 表达式。

    返回 None 表示查询中没有可用于 trigram 检索的词元，调用方应走兜底路径。
    """
    units: list[str] = []
    for raw in TERM_RE.findall(strip_stopwords(query)):
        units.extend(_expand(raw.strip("._-+#")))
    if not units:
        return None

    unique = list(dict.fromkeys(units))[:MAX_QUERY_TERMS]
    # 双引号包裹使 FTS5 将其视为字面短语，内部的 " 需转义为 ""
    # ——这一步同时消除了 `.` `*` `-` `(` `)` 等字符被当作查询语法的风险（V1）
    return " OR ".join(f'"{u.replace(chr(34), chr(34) * 2)}"' for u in unique)


def _escape_like(term: str) -> str:
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def connect(db_path: Path) -> sqlite3.Connection:
    """以只读模式打开索引。

    只读 URI 模式既避免误写，也让 SQLite 跳过锁与日志开销；
    打开大文件本身是 O(1) 的，无需缓存连接，从而规避多线程共享连接的隐患。
    """
    if not db_path.is_file():
        # 刻意不内插 db_path：本异常的消息会经 /api/health 的 error 字段
        # 与 /api/ask 的 503 detail 原样返回客户端，内插即泄露服务端目录结构。
        raise KnowledgeBaseUnavailable(
            "检索索引不存在。部署环境请确认 buildCommand 已执行 python scripts/build_index.py；"
            "本地环境请先运行该脚本构建索引。"
        )
    # SQLite URI 要求正斜杠；Windows 盘符路径形如 D:/a/b.db，需补前导斜杠，
    # 否则 `file:D:\a\b.db` 会被当成相对路径而打开失败。
    posix = db_path.resolve().as_posix()
    if not posix.startswith("/"):
        posix = "/" + posix
    try:
        con = sqlite3.connect(f"file://{posix}?mode=ro", uri=True)
        con.execute("SELECT count(*) FROM chunks LIMIT 1").fetchone()
    except sqlite3.Error as exc:
        # 同样不回显原始异常文本：SQLite 的错误消息可能包含文件绝对路径。
        raise KnowledgeBaseUnavailable(f"检索索引不可读或已损坏（{type(exc).__name__}）") from exc
    return con


def _search_fts(con: sqlite3.Connection, expr: str, top_k: int) -> list[Hit]:
    sql = (
        "SELECT rowid, title, body, bundle, grp, domain, path, "
        f"bm25(chunks, {BM25_WEIGHTS}) AS score "
        "FROM chunks WHERE chunks MATCH ? ORDER BY score LIMIT ?"
    )
    try:
        rows = con.execute(sql, (expr, top_k)).fetchall()
    except sqlite3.OperationalError:
        # MATCH 表达式仍可能触发语法错误，此处兜底为零命中而非崩溃（V1 二次防御）
        return []
    return [
        Hit(
            chunk_id=r[0],
            title=r[1],
            body=r[2],
            bundle=r[3],
            grp=r[4],
            domain=r[5],
            path=r[6],
            score=float(r[7]),
        )
        for r in rows
    ]


def _search_like(con: sqlite3.Connection, query: str, top_k: int) -> list[Hit]:
    """兜底检索：用于短查询（V2）与 FTS 零命中场景。

    LIKE 是全表扫描，故用 LIKE_FALLBACK_LIMIT 限制候选规模后再按长度截断。
    """
    needle = _escape_like(query.strip())
    if not needle:
        return []
    pattern = f"%{needle}%"
    # 标题命中优先：标题是对片段语义最凝练的概括，命中标题的片段通常更对题。
    sql = (
        "SELECT rowid, title, body, bundle, grp, domain, path, "
        "CASE WHEN title LIKE ? ESCAPE '\\' THEN 0 ELSE 1 END AS t_rank "
        "FROM chunks WHERE body LIKE ? ESCAPE '\\' OR title LIKE ? ESCAPE '\\' "
        "ORDER BY t_rank, rowid LIMIT ?"
    )
    rows = con.execute(sql, (pattern, pattern, pattern, LIKE_FALLBACK_LIMIT)).fetchall()
    return [
        Hit(
            chunk_id=r[0],
            title=r[1],
            body=r[2],
            bundle=r[3],
            grp=r[4],
            domain=r[5],
            path=r[6],
            score=0.0,
        )
        for r in rows
    ][:top_k]


def search(con: sqlite3.Connection, query: str, top_k: int) -> list[Hit]:
    """检索入口：优先 FTS5 + BM25，零命中时回落到 LIKE。"""
    query = query.strip()
    if not query:
        return []
    cleaned = strip_stopwords(query).strip() or query
    expr = build_match_expr(query)
    if expr is None:
        return _search_like(con, cleaned, top_k)
    hits = _search_fts(con, expr, top_k)
    return hits if hits else _search_like(con, cleaned, top_k)


def stats(con: sqlite3.Connection) -> dict[str, str]:
    """读取构建期写入的索引元信息（含派生产物溯源字段）。

    索引可打开但元信息读不出，说明文件损坏或不完整——
    此时必须显式报错，否则健康检查会上报 `db_ready: true` 而 stats 为空，
    把索引损坏伪装成正常运行。
    """
    try:
        rows = con.execute("SELECT key, value FROM meta").fetchall()
    except sqlite3.Error as exc:
        raise KnowledgeBaseUnavailable(f"检索索引元信息不可读，索引可能已损坏（{type(exc).__name__}）") from exc
    return {k: v for k, v in rows}
