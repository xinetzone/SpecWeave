"""环境预检：确认 SQLite FTS5 + trigram 分词器可用（中文检索的技术前提）。"""

import sqlite3
import sys

SQL_CREATE = "CREATE VIRTUAL TABLE t USING fts5(body, tokenize='trigram')"
SQL_INSERT = "INSERT INTO t(body) VALUES (?)"
SQL_QUERY = "SELECT body, bm25(t) FROM t WHERE t MATCH ? ORDER BY bm25(t) LIMIT 5"


def main() -> int:
    print(f"sqlite3 版本: {sqlite3.sqlite_version}")
    con = sqlite3.connect(":memory:")
    try:
        con.execute(SQL_CREATE)
    except sqlite3.OperationalError as exc:
        print(f"FTS5/trigram 不可用: {exc}")
        return 1

    print("FTS5 + trigram 分词器: 可用")

    samples = [
        "道家思想的核心是道法自然，无为而无不为。",
        "OKF 知识包采用 concepts / examples / references 三层结构。",
        "Python 3.14 引入了模板字符串字面值与标注的迟延求值。",
    ]
    con.executemany(SQL_INSERT, [(s,) for s in samples])

    for q in ("道法自然", "知识包", "3.14"):
        try:
            rows = con.execute(SQL_QUERY, (q,)).fetchall()
        except sqlite3.OperationalError as exc:
            print(f"查询 {q!r} 失败: {exc}")
            return 1
        print(f"  查询 {q!r} -> {len(rows)} 命中")
        for body, score in rows:
            print(f"    bm25={score:.4f}  {body[:40]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
