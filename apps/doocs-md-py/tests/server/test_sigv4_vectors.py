"""TR-13.2 SigV4 官方测试向量（get-object/put-object 各一组）。

golden 由 scripts/sigv4_vectors_regen.py 生成：输入取自 AWS 官方 S3 SigV4 文档
示例，参考签名为 AWS 官方 @aws-sdk/signature-v4 复算结果；本测试不依赖 Node。
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from doocs_md_py.server.storage import (
    EMPTY_SHA256,
    amz_date_format,
    build_canonical_headers,
    derive_signing_key,
    encode_canonical_path,
    sha256_hex,
    sign_sigv4,
)

GOLDEN_PATH = Path(__file__).resolve().parents[1] / "golden" / "sigv4_vectors.json"


@pytest.fixture(scope="module")
def golden():
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case_index", [0, 1], ids=["get-object", "put-object"])
def test_official_vector_matches_byte_for_byte(golden, case_index):
    case = golden["cases"][case_index]
    creds = golden["credentials"]
    result = sign_sigv4(
        case["method"],
        case["raw_path"],
        "",
        case["headers"],
        case["payload"].encode("utf-8"),
        access_key_id=creds["accessKeyId"],
        secret_access_key=creds["secretAccessKey"],
        region=golden["region"],
        service=golden["service"],
        amz_date=golden["amzDate"],
        payload_hash=case["headers"]["x-amz-content-sha256"],
    )
    # 逐层逐字节：canonical request → string-to-sign → Authorization
    assert result["canonical_request"] == case["canonical_request"]
    assert result["string_to_sign"].rsplit("\n", 1)[-1] == case["string_to_sign_hash"]
    assert result["authorization"] == case["expected_authorization"]
    assert result["signature"] == case["expected_signature"]


def test_put_vector_is_the_documented_signature(golden):
    """PUT 签名必须等于官方文档公布值（Date 与 storage-class 均参与签名）。"""
    case = golden["cases"][1]
    assert case["name"] == "put-object"
    assert case["expected_signature"] == (
        "98ad721746da40c64f1a55b78f14c238d841ea1380cd77a1b5971af0ece108bd"
    )
    assert case["string_to_sign_hash"] == (
        "9e0e90d9c76de8fa5b200d8c849cd5b8dc7a3be3951ddb7f6a76b4158342019d"
    )


def test_get_vector_is_the_documented_signature(golden):
    """GET 签名必须等于 AWS 文档公布的广为人知值（独立于 SDK 输出的第二锚点）。"""
    case = golden["cases"][0]
    assert case["expected_signature"] == (
        "f0e8bdb87c964420e857bd35b5d6ed310bd44f0170aba48dd91039c6036bdb41"
    )


def test_payload_hashes_are_documented(golden):
    # 文档公布的空串与 "Welcome to Amazon S3." SHA256
    assert sha256_hex(b"") == EMPTY_SHA256
    assert sha256_hex(b"Welcome to Amazon S3.") == (
        "44ce7dd67c959e0d3524ffac1771dfbba87d2b6b4b4e99e42034a8b803f8b072"
    )


def test_authorization_header_structure(golden):
    get_case = golden["cases"][0]
    assert get_case["expected_authorization"].startswith("AWS4-HMAC-SHA256 ")
    assert (
        "Credential=AKIAIOSFODNN7EXAMPLE/20130524/us-east-1/s3/aws4_request"
        in get_case["expected_authorization"]
    )
    assert (
        "SignedHeaders=host;range;x-amz-content-sha256;x-amz-date"
        in get_case["expected_authorization"]
    )
    put_case = golden["cases"][1]
    assert (
        "SignedHeaders=date;host;x-amz-content-sha256;x-amz-date;x-amz-storage-class"
        in put_case["expected_authorization"]
    )


def test_canonical_path_encoding():
    # AWS 文档 PUT 示例：$ 必须编码为 %24
    assert encode_canonical_path("/test$file.text") == "/test%24file.text"
    # 分段斜杠保留；~ 属 unreserved 不编码；空格 %20
    assert encode_canonical_path("/a b/c~d") == "/a%20b/c~d"
    # 中文按 UTF-8 百分号编码
    assert encode_canonical_path("/图片/x.png") == (
        "/%E5%9B%BE%E7%89%87/x.png"
    )


def test_canonical_headers_sorted_and_trimmed():
    canonical, signed = build_canonical_headers(
        {
            "X-Amz-Date": " 20130524T000000Z ",
            "Host": "examplebucket.s3.amazonaws.com",
        }
    )
    assert canonical == (
        "host:examplebucket.s3.amazonaws.com\n"
        "x-amz-date:20130524T000000Z\n"
    )
    assert signed == "host;x-amz-date"


def test_amz_date_format_utc():
    assert (
        amz_date_format(datetime(2013, 5, 24, 0, 0, 0, tzinfo=timezone.utc))
        == "20130524T000000Z"
    )


def test_signing_key_changes_with_scope():
    key_a = derive_signing_key("secret", "20130524", "us-east-1", "s3")
    key_b = derive_signing_key("secret", "20130525", "us-east-1", "s3")
    key_c = derive_signing_key("secret", "20130524", "us-west-2", "s3")
    assert key_a != key_b
    assert key_a != key_c
    assert len(key_a) == 32
