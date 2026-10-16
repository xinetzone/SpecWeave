"""相似度模块的单元测试：指纹构成、Dice 系数、检索打分、标签提取。"""

from info_butler.similarity import fingerprint, keyword_score, similarity, top_terms


def test_chinese_shares_bigrams():
    """中文没有空格，靠汉字二元组共享语义单元。"""
    assert similarity("整理待办清单", "待办清单") > 0.5
    assert similarity("整理待办清单", "周末去爬山") < 0.2


def test_latin_tokens_are_case_insensitive():
    assert similarity("Design Doc", "design doc") == 1.0


def test_empty_side_scores_zero():
    assert similarity("", "") == 0.0
    assert similarity("内容", "") == 0.0
    assert similarity("", "内容") == 0.0


def test_stopwords_do_not_create_false_affinity():
    """两句话只有停用词相同，不应产生高分。"""
    score = similarity("我今天有一个想法", "我明天有一个问题")
    assert score < 0.35


def test_identical_text_scores_one():
    assert similarity("同一段文字", "同一段文字") == 1.0


def test_fingerprint_mixes_latin_and_cjk():
    counts = fingerprint("RAG 检索增强生成")
    assert "rag" in counts
    assert any("检索" in key for key in counts)


def test_keyword_score_is_directional():
    """检索是单向的：短查询对长文档的覆盖率，不应被长文档分母压扁。"""
    doc = "定价方案需要重新评估" + "补充材料" * 50
    assert keyword_score("定价", doc) > 0.0
    assert keyword_score("定价", doc) > similarity("定价", doc)


def test_keyword_score_zero_without_overlap():
    assert keyword_score("定价", "周末去爬山") == 0.0
    assert keyword_score("", "任意文本") == 0.0


def test_top_terms_returns_distinct_terms():
    terms = top_terms("定价 定价 定价 客户 访谈", limit=3)
    assert terms
    assert len(terms) == len(set(terms))


def test_top_terms_empty_for_stopwords_only():
    assert top_terms("的了是在") == []


# -- 分段：跨标点配对是**正确性**问题，不是精度调优 --------------------------


def test_bigrams_do_not_straddle_punctuation():
    """标点两侧的字被强行配对，会造出 "法把" 这类假词。

    假词同时污染标签与关联判断，还会凭空制造相似度——两个风马牛不相及的句子
    只要标点位置巧合就会「相关」。所以二元组必须在标点切出的段内生成。
    """
    counts = fingerprint("想法：把周报聚合")
    assert "法把" not in counts
    assert "想法" in counts
    assert "周报" in counts


def test_segmented_bigrams_reduce_spurious_similarity():
    """内容毫不相干、只是断句位置相同，不应因为假二元组而互相靠近。"""
    assert similarity("定价、方案", "成本、结构") < 0.34


def test_single_char_segment_still_enters_the_fingerprint():
    """单字段落要退化为单字，否则这种短词永远匹配不上（停用字除外）。"""
    assert fingerprint("钱")
    assert similarity("钱", "钱") == 1.0
    assert not fingerprint("好"), "停用字不进指纹，单字也不应例外"


def test_url_structural_fragments_are_not_terms():
    """复制链接是很自然的录入方式，但 http/www/com 不是内容。"""
    terms = set(top_terms("看 https://www.example.com/report 这份资料"))
    assert not terms & {"https", "www", "com"}
    assert "report" in terms, "真正的路径词仍然要保留"
