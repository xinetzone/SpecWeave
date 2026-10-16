"""检索层测试：覆盖对抗性审查发现的两条失效边界（V1 语法注入 / V2 短查询）。"""

import sqlite3

import pytest

from okfqa import config, retrieval


# ---------------------------------------------------------------- V1：查询净化


@pytest.mark.parametrize(
    "query,expected",
    [
        # 中文串按重叠三元组展开（V6），拉丁/数字整词保留
        ("道法自然", '"道法自" OR "法自然"'),
        ("OKF 知识包", '"OKF" OR "知识包"'),
        ("Python 3.14 新特性", '"Python" OR "3.14" OR "新特性"'),
    ],
)
def test_build_match_expr_basic(query: str, expected: str) -> None:
    assert retrieval.build_match_expr(query) == expected


@pytest.mark.parametrize(
    "query",
    [
        "3.14",           # 含小数点——未转义会触发 fts5: syntax error（已实证）
        "C++ 与 Rust",     # 含加号
        "foo.bar",        # 含小数点且会被保留进 MATCH 表达式——未转义会触发 fts5: syntax error
        '他说 "道法自然"',  # 含双引号，必须转义为 "" 否则表达式失衡
        "A AND B",        # 含 FTS5 布尔运算符
        "(test)",         # 含括号
        "foo-bar_baz",    # 含连字符与下划线
    ],
)
def test_build_match_expr_never_breaks_fts_syntax(query: str) -> None:
    """净化后的表达式必须能被 FTS5 解析，不得抛 OperationalError。"""
    expr = retrieval.build_match_expr(query)
    if expr is None:
        pytest.skip("该查询无 trigram 可用词元，走 LIKE 兜底路径")
    con = sqlite3.connect(":memory:")
    con.execute(
        "CREATE VIRTUAL TABLE chunks USING fts5(title, body, tokenize='trigram')"
    )
    con.execute("INSERT INTO chunks(title, body) VALUES ('t', '示例文本 sample text 3.14')")
    con.execute("SELECT rowid FROM chunks WHERE chunks MATCH ?", (expr,)).fetchall()
    con.close()


def test_asterisk_never_reaches_fts_expression() -> None:
    """`*` 不在词元字符集内，分词阶段即被丢弃，永远不会进入 FTS5 表达式。

    独立审查指出原用例 `abc*def` 给出的是「星号已覆盖」的假保证：
    星号在 build_match_expr 之前就被丢弃了。此处如实记录该行为，
    真正的特殊字符覆盖改由 `foo.bar`（小数点会被保留）承担。
    """
    assert retrieval.build_match_expr("abc*def") == '"abc" OR "def"'


def test_build_match_expr_deduplicates_and_caps() -> None:
    expr = retrieval.build_match_expr("道法自然 道法自然")
    assert expr == '"道法自" OR "法自然"'
    # 30 个互不相同的汉字 → 28 个互不重复的三元组 → 必须被截断到上限
    long_query = "".join(chr(0x4E00 + i) for i in range(30))
    got = retrieval.build_match_expr(long_query)
    assert got is not None
    assert len(got.split(" OR ")) == retrieval.MAX_QUERY_TERMS


# ---------------------------------------------------------------- V2：短查询兜底


@pytest.mark.parametrize("query", ["AI", "C++", "ab", ""])
def test_short_query_has_no_fts_terms(query: str) -> None:
    """trigram 最小单位为三元组，长度 < 3 的词元无法命中，须返回 None 走兜底。"""
    assert retrieval.build_match_expr(query) is None


def test_short_query_falls_back_to_like(kb_db) -> None:
    con = retrieval.connect(kb_db)
    try:
        hits = retrieval.search(con, "AI", top_k=5)
    finally:
        con.close()
    assert hits, "短查询必须经 LIKE 兜底命中，而非返回空结果"
    assert any("AI" in h.body for h in hits)


# ---------------------------------------------------------------- 检索行为


def test_search_returns_ranked_hits(kb_db) -> None:
    con = retrieval.connect(kb_db)
    try:
        hits = retrieval.search(con, "道法自然", top_k=3)
    finally:
        con.close()
    assert hits
    assert "道法自然" in hits[0].body
    assert hits[0].bundle == "guoxue/daojia/laozi"


def test_natural_language_question_still_recalls(kb_db) -> None:
    """回归 V6：整句提问不得因短语精确匹配而零命中。

    「道法自然是什么」中只有「道法自然」出现在原文里，
    若把整串当短语提交，原文不含「是什么」就会漏召回。
    """
    con = retrieval.connect(kb_db)
    try:
        hits = retrieval.search(con, "道法自然是什么？", top_k=3)
    finally:
        con.close()
    assert hits, "自然语言问句必须能召回，短语精确匹配会导致漏召回"
    assert "道法自然" in hits[0].body


def test_stopwords_stripped_before_retrieval() -> None:
    """疑问套话与功能词必须先剥离，否则会淹没真正的内容词。"""
    assert retrieval.strip_stopwords("道法自然是什么意思").strip() == "道法自然"
    # 功能词被替换为空格而非直接删除，
    # 使「知识包」与「三层结构」成为两个独立词元——这对检索是有利的。
    assert retrieval.strip_stopwords("OKF 知识包的三层结构是什么").split() == [
        "OKF",
        "知识包",
        "三层结构",
    ]

    expr = retrieval.build_match_expr("道法自然是什么意思")
    assert expr is not None
    assert "道法自" in expr and "法自然" in expr
    assert "什么" not in expr and "意思" not in expr


def test_search_respects_top_k(kb_db) -> None:
    con = retrieval.connect(kb_db)
    try:
        hits = retrieval.search(con, "知识包 结构", top_k=1)
    finally:
        con.close()
    assert len(hits) == 1


def test_search_no_hit_returns_empty(kb_db) -> None:
    con = retrieval.connect(kb_db)
    try:
        assert retrieval.search(con, "量子纠缠与超弦理论", top_k=5) == []
    finally:
        con.close()


def test_search_blank_returns_empty(kb_db) -> None:
    con = retrieval.connect(kb_db)
    try:
        assert retrieval.search(con, "   ", top_k=5) == []
    finally:
        con.close()


def test_hit_carries_provenance(kb_db) -> None:
    con = retrieval.connect(kb_db)
    try:
        hit = retrieval.search(con, "OKF 三层结构", top_k=1)[0]
    finally:
        con.close()
    assert hit.domain == "meta"
    assert hit.path.endswith(".md")
    assert isinstance(hit.score, float)


# ---------------------------------------------------------------- 失效边界 V5


def test_connect_missing_db_raises_clearly(tmp_path) -> None:
    """索引缺失必须显式报错，而不是静默返回空结果。"""
    with pytest.raises(retrieval.KnowledgeBaseUnavailable) as exc:
        retrieval.connect(tmp_path / "nope.db")
    assert "build_index.py" in str(exc.value)


def test_failure_messages_leak_no_server_paths(tmp_path) -> None:
    """索引相关异常的消息会直达客户端，不得内插服务端绝对路径。

    R1-F4 指出该泄露后，首轮修复只去掉了 health 响应里的 db_path 字段，
    却漏掉了异常消息本身仍在插值——故此处直接对消息内容设卡。
    """
    with pytest.raises(retrieval.KnowledgeBaseUnavailable) as exc:
        retrieval.connect(tmp_path / "nope.db")
    message = str(exc.value)
    assert "build_index.py" in message, "仍需给出可操作的构建指引"
    assert str(tmp_path) not in message, "异常消息泄露了服务端绝对路径"
    assert "nope.db" not in message


def test_stats_reads_metadata(kb_db) -> None:
    con = retrieval.connect(kb_db)
    try:
        meta = retrieval.stats(con)
    finally:
        con.close()
    assert meta["chunk_count"] == "4"
    assert meta["tokenizer"] == "fts5-trigram"


# ---------------------------------------------------------------- 真实索引集成


def test_real_index_integration(real_db) -> None:
    """对真实索引（161MB / 74955 片段）做冒烟验证；未构建时跳过。"""
    if not real_db.is_file():
        pytest.skip("未构建真实索引，跳过集成冒烟")

    con = retrieval.connect(real_db)
    try:
        hits = retrieval.search(con, "道法自然", top_k=3)
        assert hits, "真实索引应能命中常识性中文查询"
        assert all(h.body.strip() for h in hits)

        # 回归：含小数点的查询曾导致 fts5: syntax error
        assert retrieval.search(con, "Python 3.14", top_k=3)
    finally:
        con.close()


def test_default_db_path_is_inside_app() -> None:
    assert config.DEFAULT_DB_PATH.name == "knowledge.db"
    assert config.DEFAULT_DB_PATH.parent.name == "data"
