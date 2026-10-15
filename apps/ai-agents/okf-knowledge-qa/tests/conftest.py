"""测试夹具：构造一个与生产同构的迷你 FTS5 索引。

刻意复用 build_index.py 的建表语句与 trigram 分词器，
使检索行为（含 V1/V2 两条失效边界）在测试中与线上一致。
"""

import sqlite3

import pytest

from okfqa import config

SCHEMA_SQL = """
CREATE VIRTUAL TABLE chunks USING fts5(
    title,
    body,
    bundle UNINDEXED,
    grp UNINDEXED,
    domain UNINDEXED,
    path UNINDEXED,
    tokenize='trigram'
)
"""

SAMPLE_DOCS = [
    (
        "道法自然",
        "道家思想的核心是道法自然，主张无为而无不为，顺应万物自身的节律。",
        "guoxue/daojia/laozi",
        "daojia",
        "guoxue",
        "guoxue/daojia/laozi/concepts/01-natural.md",
    ),
    (
        "OKF 知识包三层结构",
        "OKF 知识包采用 concepts、examples、references 三层结构组织内容，"
        "分别承载概念讲解、实战示例与信源参考。",
        "meta/okf-spec",
        "okf-spec",
        "meta",
        "meta/okf-spec/index.md",
    ),
    (
        "Python 3.14 新特性",
        "Python 3.14 引入模板字符串字面值 t-string，并按 PEP 649 默认启用标注的迟延求值。",
        "jishu/python",
        "python",
        "jishu",
        "jishu/python/concepts/01-whats-new.md",
    ),
    (
        "大模型推理优化",
        "AI 推理优化常采用量化、蒸馏与投机采样等手段降低成本，人工智能落地的关键在推理成本。",
        "jishu/ai",
        "ai",
        "jishu",
        "jishu/ai/concepts/03-inference.md",
    ),
]


@pytest.fixture
def kb_db(tmp_path, monkeypatch):
    """写入迷你索引，并把 OKF_DB_PATH 指向它，返回数据库路径。"""
    db = tmp_path / "test_knowledge.db"
    con = sqlite3.connect(db)
    con.execute(SCHEMA_SQL)
    con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    con.executemany(
        "INSERT INTO chunks(title, body, bundle, grp, domain, path) VALUES (?,?,?,?,?,?)",
        SAMPLE_DOCS,
    )
    con.executemany(
        "INSERT INTO meta(key, value) VALUES (?,?)",
        [("chunk_count", str(len(SAMPLE_DOCS))), ("bundle_count", "4"), ("tokenizer", "fts5-trigram")],
    )
    con.commit()
    con.close()

    monkeypatch.setenv("OKF_DB_PATH", str(db))
    return db


@pytest.fixture
def no_llm(monkeypatch):
    """清除大模型凭据，强制走降级路径。"""
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


@pytest.fixture(autouse=True)
def _isolate_from_real_index(monkeypatch, tmp_path):
    """默认把索引指向临时目录，避免单测误读开发机上 161MB 的真实索引。"""
    monkeypatch.setenv("OKF_DB_PATH", str(tmp_path / "missing.db"))


@pytest.fixture
def real_db():
    """真实索引路径；未构建时由用例自行 skip。"""
    return config.DEFAULT_DB_PATH
