"""共享 pytest 夹具：迁移完成的内存 SQLite 连接。"""

import pytest

from doocs_md_py.server import db


@pytest.fixture
def conn():
    connection = db.connect(":memory:")
    db.apply_migrations(connection)
    yield connection
    connection.close()


@pytest.fixture
def user_id(conn):
    """插入并返回一个用户 id。"""
    uid = "user-001"
    db.upsert_user(
        conn,
        {
            "id": uid,
            "github_id": 10001,
            "login": "octocat",
            "name": "The Octocat",
            "avatar": "https://example.com/a.png",
        },
    )
    return uid
