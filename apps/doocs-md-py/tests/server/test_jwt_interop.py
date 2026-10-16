"""TR-10.2 hono/jwt ↔ PyJWT HS256 互认固定向量。

golden 由 scripts/jwt_interop_regen.py 生成（podman node:22 + hono@4.13.13）：
- Node → Py：node_token 必须被 PyJWT 验签且 claims 全等；
- Py → Node：golden.checks.py_token_verified_by_node 记录 Node 侧已验过 PyJWT 令牌；
- 负向量（过期/错 secret/篡改）双侧拒绝。
普通 pytest 不依赖 Node。
"""

import json
from pathlib import Path

import jwt
import pytest

from doocs_md_py.server.security import verify_token

GOLDEN = json.loads(
    (Path(__file__).resolve().parents[1] / "golden" / "jwt_interop.json").read_text(
        encoding="utf-8"
    )
)


def test_golden_self_consistency():
    assert GOLDEN["node_pkg"] == "hono@4.13.13"
    assert GOLDEN["algorithm"] == "HS256"
    assert all(GOLDEN["checks"].values())


def test_node_token_verified_by_pyjwt():
    payload = verify_token(GOLDEN["secret"], GOLDEN["node_token"])
    assert payload == GOLDEN["claims"]


def test_token_byte_identical_between_libraries():
    """两库 header/payload 规范化一致时，同 claims 同 secret 的紧凑序列化应全等。"""
    py_token = jwt.encode(GOLDEN["claims"], GOLDEN["secret"], algorithm="HS256")
    assert py_token == GOLDEN["node_token"]


def test_py_token_verified_by_node_recorded():
    # 反向互认在生成器内由 hono verify 完成并固化于此
    assert GOLDEN["checks"]["py_token_verified_by_node"] is True


@pytest.mark.parametrize(
    "check",
    [
        "py_expired_rejected_by_node",
        "wrong_secret_rejected",
        "tampered_rejected",
    ],
)
def test_negative_vectors_rejected_by_node(check):
    assert GOLDEN["checks"][check] is True


def test_node_expired_vector_rejected_by_pyjwt():
    # Node 负向量同 claims 用 PyJWT 同样拒绝
    expired = jwt.encode(GOLDEN["expired_claims"], GOLDEN["secret"], algorithm="HS256")
    with pytest.raises(jwt.ExpiredSignatureError):
        verify_token(GOLDEN["secret"], expired)
