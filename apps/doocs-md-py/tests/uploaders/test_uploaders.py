"""TR-14.1/14.2 13 图床 + dcloud 上传器测试。

两类断言：
1. golden 回放：签名（tests/golden/uploader_signature_vectors.json，crypto-es
   录制）与 S3 presigned URL（tests/golden/s3_presign_vectors.json，
   @aws-sdk 3.1147.0 录制）逐字节比对；
2. MockTransport 请求录制：方法/URL/头/multipart 关键字段与返回 URL 形态，
   覆盖各家 endpoint/pathStyle/CDN 分支与微信两分流、token 缓存等行为。
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest

from doocs_md_py.uploaders import (
    UPLOAD_PROVIDERS,
    AliOSSConfig,
    CloudinaryConfig,
    DefaultConfig,
    DcloudConfig,
    GenericS3Config,
    GithubWebConfig,
    InMemoryMpTokenStore,
    MinioConfig,
    MpConfig,
    QiniuConfig,
    R2Config,
    TelegramConfig,
    TxCOSConfig,
    UpyunConfig,
    UploadFile,
    file_upload,
    resolve_upload_provider,
)
from doocs_md_py.uploaders import default as default_mod
from doocs_md_py.uploaders import github as github_mod
from doocs_md_py.uploaders import mp as mp_mod
from doocs_md_py.uploaders import s3 as s3_mod
from doocs_md_py.uploaders import telegram as telegram_mod
from doocs_md_py.uploaders.base import (
    get_date_filename,
    get_dir,
    require_config,
    trim_trailing_slash,
)
from doocs_md_py.uploaders.cloudinary import cloudinary_signature, cloudinary_upload
from doocs_md_py.uploaders.dcloud import dcloud_sign, dcloud_upload_file
from doocs_md_py.uploaders.form_custom import (
    FormCustomConfig as FCC,
    form_custom_upload,
    register_form_custom,
)
from doocs_md_py.uploaders.qiniu import (
    QINIU_DEFAULT_UPLOAD_URL,
    qiniu_upload,
    qiniu_upload_token,
    resolve_qiniu_upload_url,
)
from doocs_md_py.uploaders.s3_presign import build_presigned_put_url
from doocs_md_py.uploaders.upyun import upyun_signature, upyun_upload

GOLDEN_DIR = Path(__file__).resolve().parents[1] / "golden"
FIXED_UTC_NOW = datetime(2025, 10, 15, 3, 46, 40, tzinfo=timezone.utc)
FIXED_SEC = 1760500000
FIXED_MS = 1760500000123
FIXED_UUID = uuid.UUID("12345678-1234-5678-9abc-123456789abc")
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32


@pytest.fixture
def sample_file() -> UploadFile:
    return UploadFile("shot.PNG", "image/png", PNG)


def make_client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


# --------------------------------------------------------------------------
# base 基础设施
# --------------------------------------------------------------------------


def test_get_dir_utc():
    assert get_dir(FIXED_SEC) == "2025/10/15"


def test_get_date_filename_keeps_extension_verbatim_and_empty_tail():
    name = get_date_filename(
        "a.JPEG", clock_ms=lambda: FIXED_MS, uuid_factory=lambda: FIXED_UUID
    )
    assert name == f"{FIXED_MS}-{FIXED_UUID}.JPEG"
    # JS "noext".split('.').pop() === "noext"：无点时尾段即原名
    no_ext = get_date_filename(
        "noext", clock_ms=lambda: FIXED_MS, uuid_factory=lambda: FIXED_UUID
    )
    assert no_ext == f"{FIXED_MS}-{FIXED_UUID}.noext"
    # 仅以点结尾时尾段为空串
    trailing_dot = get_date_filename(
        "a.", clock_ms=lambda: FIXED_MS, uuid_factory=lambda: FIXED_UUID
    )
    assert trailing_dot.endswith(f"{FIXED_UUID}.")


def test_trim_trailing_slash():
    assert trim_trailing_slash("https://a.com/") == "https://a.com"
    assert trim_trailing_slash("https://a.com") == "https://a.com"


def test_require_config_passes_through_present_values():
    marker = {"cdnHost": "https://a.com/"}
    assert require_config(marker, "cdnHost") is marker
    assert require_config("", "cdnHost") == ""  # 空串是「已配置为空」，不算缺失
    assert require_config(0, "chunkSize") == 0


def test_require_config_raises_with_field_context():
    with pytest.raises(ValueError, match="cdnHost is missing or empty"):
        require_config(None, "cdnHost")
    with pytest.raises(ValueError, match="token is missing or empty"):
        require_config(None, "token")


# --------------------------------------------------------------------------
# golden：四家签名
# --------------------------------------------------------------------------


def test_signature_golden_vectors():
    golden = json.loads(
        (GOLDEN_DIR / "uploader_signature_vectors.json").read_text(encoding="utf-8")
    )
    v = golden["vectors"]

    assert (
        qiniu_upload_token(v["qiniu"]["access_key"], v["qiniu"]["secret_key"], v["qiniu"]["put_policy"])
        == v["qiniu"]["token"]
    )
    # safe64 保留 padding "="
    assert v["qiniu"]["token"].split(":")[1].endswith("=")

    u = v["upyun"]
    assert upyun_signature(u["password"], "PUT", u["uri"], u["date"]) == u["signature"]

    c = v["cloudinary"]
    assert cloudinary_signature(c["params"], c["api_secret"]) == c["signature"]

    d = v["dcloud"]
    assert dcloud_sign(d["data"], d["secret"]) == d["signature"]


# --------------------------------------------------------------------------
# golden：S3 presigned URL 六场景
# --------------------------------------------------------------------------


def test_s3_presign_golden_vectors():
    golden = json.loads(
        (GOLDEN_DIR / "s3_presign_vectors.json").read_text(encoding="utf-8")
    )
    for case in golden["cases"]:
        result = build_presigned_put_url(
            host=case["host"],
            raw_path=case["raw_path"],
            access_key_id=golden["credentials"]["accessKeyId"],
            secret_access_key=golden["credentials"]["secretAccessKey"],
            region=case["region"],
            amz_date=golden["amzDate"],
            expires_in=golden["expiresIn"],
            scheme=case["scheme"],
        )
        assert result["url"] == case["sdk_url"], case["name"]
        assert result["canonical_request"] == case["canonical_request"], case["name"]
        # 结构断言：CRC32 校验参数与 x-id 存在，SignedHeaders 只有 host
        assert "X-Amz-SignedHeaders=host" in case["sdk_url"]
        assert "x-amz-checksum-crc32=AAAAAA%3D%3D" in case["sdk_url"]
        assert case["sdk_url"].endswith("x-id=PutObject")


# --------------------------------------------------------------------------
# qiniu
# --------------------------------------------------------------------------


def test_qiniu_resolve_upload_url():
    assert resolve_qiniu_upload_url("") == QINIU_DEFAULT_UPLOAD_URL
    assert resolve_qiniu_upload_url("  ") == QINIU_DEFAULT_UPLOAD_URL
    assert resolve_qiniu_upload_url("https://upload-z2.qiniup.com") == "https://upload-z2.qiniup.com"
    assert resolve_qiniu_upload_url("z2") == QINIU_DEFAULT_UPLOAD_URL


def test_qiniu_upload_recording(sample_file):
    recorded = {}

    def handler(request: httpx.Request) -> httpx.Response:
        recorded["request"] = request
        body = request.content
        assert b'name="token"' in body
        assert b'name="key"' in body
        # qiniu key = "<path>/<dateFilename>"，无独立日期目录段
        assert b'imgs/' in body
        return httpx.Response(200, json={"key": "ignored"})

    client = make_client(handler)
    cfg = QiniuConfig("AK", "SK", "bucket", path="imgs", domain="https://cdn.q.com")
    url = qiniu_upload(
        cfg, sample_file, client, now_sec=FIXED_SEC, clock_ms=lambda: FIXED_MS
    )
    assert recorded["request"].url == QINIU_DEFAULT_UPLOAD_URL
    assert url.startswith("https://cdn.q.com/imgs/")
    assert url.endswith(".PNG")


def test_qiniu_upload_failure(sample_file):
    client = make_client(lambda r: httpx.Response(401, text="bad token"))
    with pytest.raises(RuntimeError, match="Qiniu upload failed"):
        qiniu_upload(
            QiniuConfig("AK", "SK", "b"),
            sample_file,
            client,
            now_sec=FIXED_SEC,
        )


# --------------------------------------------------------------------------
# upyun
# --------------------------------------------------------------------------


def test_upyun_upload_recording_and_leading_slash(sample_file):
    recorded = {}

    def handler(request: httpx.Request) -> httpx.Response:
        recorded["request"] = request
        return httpx.Response(200)

    client = make_client(handler)
    cfg = UpyunConfig("bucket-1", "op", "pw", path="", domain="https://cdn.u.com")
    url = upyun_upload(
        cfg, sample_file, client, now_sec=FIXED_SEC, clock_ms=lambda: FIXED_MS
    )
    req = recorded["request"]
    # path 为空时 filename 仍以 "/" 开头（逐字）
    assert req.url.path.startswith("/bucket-1//")
    assert req.headers["authorization"].startswith("UPYUN op:")
    assert req.headers["x-date"] == "Wed, 15 Oct 2025 03:46:40 GMT"
    assert req.headers["content-type"] == "image/png"
    assert url.startswith("https://cdn.u.com//")


def test_upyun_upload_failure(sample_file):
    client = make_client(lambda r: httpx.Response(403, text="sign error"))
    with pytest.raises(RuntimeError, match="sign error"):
        upyun_upload(
            UpyunConfig("b", "op", "pw", "p", "https://d"),
            sample_file,
            client,
            now_sec=FIXED_SEC,
        )


# --------------------------------------------------------------------------
# cloudinary
# --------------------------------------------------------------------------


def test_cloudinary_signed_upload_recording(sample_file):
    recorded = {}

    def handler(request: httpx.Request) -> httpx.Response:
        recorded["request"] = request
        return httpx.Response(
            200, json={"secure_url": "https://res.cloudinary.com/cn/image/upload/v1/a.png"}
        )

    client = make_client(handler)
    cfg = CloudinaryConfig(
        cloud_name="cname", api_key="key123", api_secret="sec", folder="f/sub"
    )
    url = cloudinary_upload(cfg, sample_file, client, now_sec=FIXED_SEC)
    assert url == "https://res.cloudinary.com/cn/image/upload/v1/a.png"
    body = recorded["request"].content
    assert b'name="timestamp"' in body
    assert b'name="signature"' in body
    assert b'name="folder"' in body
    assert str(FIXED_SEC).encode() in body
    # 签名必须与独立函数一致（按名字典序 folder + timestamp）
    expected_sig = cloudinary_signature(
        {"folder": "f/sub", "timestamp": str(FIXED_SEC)}, "sec"
    )
    assert expected_sig.encode() in body
    assert recorded["request"].url.path.endswith("/cname/image/upload")


def test_cloudinary_unsigned_preset(sample_file):
    recorded = {}
    client = make_client(
        lambda r: (
            recorded.update(request=r)
            or httpx.Response(200, json={"url": "http://res.cloudinary.com/c/a.png"})
        )
    )
    cfg = CloudinaryConfig(
        cloud_name="cn", api_key="k", api_secret="", upload_preset="unsigned-1"
    )
    url = cloudinary_upload(cfg, sample_file, client, now_sec=FIXED_SEC)
    assert url == "http://res.cloudinary.com/c/a.png"
    assert b'name="upload_preset"' in recorded["request"].content
    assert b'name="signature"' not in recorded["request"].content


def test_cloudinary_missing_preset_raises(sample_file):
    client = make_client(lambda r: httpx.Response(200, json={}))
    with pytest.raises(RuntimeError, match="cloudinaryMissingPreset"):
        cloudinary_upload(
            CloudinaryConfig("cn", "k"), sample_file, client, now_sec=FIXED_SEC
        )


def test_cloudinary_missing_config_raises(sample_file):
    client = make_client(lambda r: httpx.Response(200, json={}))
    with pytest.raises(RuntimeError, match="cloudinaryMissingConfig"):
        cloudinary_upload(
            CloudinaryConfig("", ""), sample_file, client, now_sec=FIXED_SEC
        )


def test_cloudinary_custom_domain_keeps_path_and_query(sample_file):
    client = make_client(
        lambda r: httpx.Response(
            200,
            json={"secure_url": "https://res.cloudinary.com/cn/image/upload/v1/a.png?t=2&q=80"},
        )
    )
    cfg = CloudinaryConfig(
        cloud_name="cn", api_key="k", api_secret="s", domain="https://img.example.com"
    )
    url = cloudinary_upload(cfg, sample_file, client, now_sec=FIXED_SEC)
    assert url == "https://img.example.com/cn/image/upload/v1/a.png?t=2&q=80"


# --------------------------------------------------------------------------
# dcloud
# --------------------------------------------------------------------------


def test_dcloud_requires_config(sample_file):
    client = make_client(lambda r: httpx.Response(200, json={}))
    with pytest.raises(ValueError, match="spaceInfo"):
        dcloud_upload_file(DcloudConfig("", ""), sample_file, client)


def test_dcloud_four_step_flow(sample_file):
    requests_seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests_seen.append(request)
        if request.url.host == "api.bspapp.com":
            if (
                b"anonymousAuthorize" in request.content
                and request.headers.get("x-basement-token") is None
            ):
                return httpx.Response(200, json={"data": {"accessToken": "TOK"}})
            if b"generateProximalSign" in request.content:
                return httpx.Response(
                    200,
                    json={
                        "data": {
                            "host": "oss.example.com",
                            "accessKeyId": "AKI",
                            "signature": "SIG",
                            "id": "rid-1",
                            "ossPath": "public/x.png",
                            "policy": "POL",
                            "cdnDomain": "cdn.example.com",
                        }
                    },
                )
            if b"resource.report" in request.content:
                return httpx.Response(200, json={"ok": True})
            raise AssertionError(f"unexpected bspapp request: {request.content[:80]}")
        if request.url.host == "oss.example.com":
            # OSS 形态断言
            assert request.headers["x-oss-server-side-encrpytion"] == "AES256"
            body = request.content
            for field in (
                b"Cache-Control",
                b"Content-Disposition",
                b"OSSAccessKeyId",
                b"Signature",
                b'name="host"',
                b'name="id"',
                b'name="key"',
                b'name="policy"',
                b"success_action_status",
                b'name="file"',
            ):
                assert field in body, field
            return httpx.Response(200)
        raise AssertionError(f"unexpected host: {request.url.host}")

    clocks = iter([1000, 2000, 3000])
    client = make_client(handler)
    url = dcloud_upload_file(
        DcloudConfig("space-1", "secret"),
        sample_file,
        client,
        name="dir/a.png",
        clock_ms=lambda: next(clocks),
    )
    assert url == "https://cdn.example.com/public/x.png"
    # 三次 bspapp + 一次 OSS
    assert len(requests_seen) == 4
    auth_req, sign_req, oss_req, report_req = requests_seen
    # 首步 body 手拼（紧凑无空格），且时间戳为数字未加引号
    assert auth_req.content == (
        b'{"method":"serverless.auth.user.anonymousAuthorize","params":"{}",'
        b'"spaceId":"space-1","timestamp":1000}'
    )
    # 签名/上报步带 basement token，body 为 JSON.stringify 形态
    assert sign_req.headers["x-basement-token"] == "TOK"
    assert b'"token":"TOK"' in sign_req.content
    assert report_req.headers["x-basement-token"] == "TOK"
    # params 内嵌 JSON 被外层 JSON.stringify 转义
    assert b'"params":"{\\"id\\":\\"rid-1\\"}"' in report_req.content
    # 签名头全部为 32 位 hex（HMAC-MD5）
    for req in (auth_req, sign_req, report_req):
        assert len(req.headers["x-serverless-sign"]) == 32


def test_dcloud_sign_golden_known_answer():
    # 与 Node crypto 对拍的独立定点（纯 ASCII，便于手验）
    sig = dcloud_sign({"b": "2", "a": "1", "timestamp": 100}, "sec")
    assert sig == "36d5dfe8d6736f2d906658db26f63d1a"
    assert len(sig) == 32


# --------------------------------------------------------------------------
# S3 五家行为矩阵
# --------------------------------------------------------------------------


def _recording_put_handler(recorded, status=200):
    def handler(request: httpx.Request) -> httpx.Response:
        recorded["request"] = request
        assert request.method == "PUT"
        assert request.headers["content-type"] == "image/png"
        assert request.content == PNG
        return httpx.Response(status, text="OK")

    return handler


def test_alioss_https_default_url(sample_file):
    recorded = {}
    client = make_client(_recording_put_handler(recorded))
    cfg = AliOSSConfig(
        region="oss-cn-hangzhou",
        bucket="b1",
        access_key_id="AK",
        access_key_secret="SK",
    )
    url = s3_mod.alioss_upload(
        cfg, sample_file, client, now=FIXED_UTC_NOW, clock_ms=lambda: FIXED_MS
    )
    req = recorded["request"]
    assert req.url.host == "b1.oss-cn-hangzhou.aliyuncs.com"
    # 无 path 配置时 key 即 dateFilename（不含日期目录段）
    assert req.url.path.startswith(f"/{FIXED_MS}-")
    assert url == f"https://b1.oss-cn-hangzhou.aliyuncs.com{req.url.path}"


def test_alioss_http_and_cdn(sample_file):
    recorded = {}
    client = make_client(_recording_put_handler(recorded))
    cfg = AliOSSConfig(
        region="oss-cn-hangzhou",
        bucket="b1",
        access_key_id="AK",
        access_key_secret="SK",
        use_ssl=False,
        cdn_host="https://cdn.a.com/",
        path="img",
    )
    url = s3_mod.alioss_upload(
        cfg, sample_file, client, now=FIXED_UTC_NOW, clock_ms=lambda: FIXED_MS
    )
    req = recorded["request"]
    assert str(req.url).startswith("http://b1.oss-cn-hangzhou.aliyuncs.com/img/")
    assert url.startswith("https://cdn.a.com/img/")
    assert not url.startswith("https://cdn.a.com//")


def test_txcos_default_and_cdn_branches(sample_file):
    # path 为空：CDN URL 不拼 path 段
    recorded = {}
    client = make_client(_recording_put_handler(recorded))
    cfg = TxCOSConfig("SID", "SK", "b-123", "ap-guangzhou", path="", cdn_host="https://d.myqcloud.com")
    url = s3_mod.txcos_upload(
        cfg, sample_file, client, now=FIXED_UTC_NOW, clock_ms=lambda: FIXED_MS
    )
    path = recorded["request"].url.path
    assert recorded["request"].url.host == "b-123.cos.ap-guangzhou.myqcloud.com"
    assert url == f"https://d.myqcloud.com{path}"

    # path 非空：CDN URL 显式带 path
    recorded.clear()
    cfg2 = TxCOSConfig("SID", "SK", "b-123", "ap-guangzhou", path="p", cdn_host="https://d.myqcloud.com")
    url2 = s3_mod.txcos_upload(
        cfg2, sample_file, client, now=FIXED_UTC_NOW, clock_ms=lambda: FIXED_MS
    )
    assert url2.startswith("https://d.myqcloud.com/p/")


def test_txcos_default_public_url(sample_file):
    recorded = {}
    client = make_client(_recording_put_handler(recorded))
    cfg = TxCOSConfig("SID", "SK", "b-123", "ap-guangzhou")
    url = s3_mod.txcos_upload(
        cfg, sample_file, client, now=FIXED_UTC_NOW, clock_ms=lambda: FIXED_MS
    )
    assert url == f"https://b-123.cos.ap-guangzhou.myqcloud.com{recorded['request'].url.path}"


def test_minio_endpoint_port_and_no_path_prefix(sample_file):
    recorded = {}
    client = make_client(_recording_put_handler(recorded))
    cfg = MinioConfig(
        endpoint="10.0.0.1", port="9000", use_ssl=False, bucket="imgs",
        access_key="AK", secret_key="SK",
    )
    url = s3_mod.minio_upload(
        cfg, sample_file, client, now=FIXED_UTC_NOW, clock_ms=lambda: FIXED_MS
    )
    req = recorded["request"]
    assert req.url.host == "10.0.0.1"
    assert req.url.port == 9000
    # pathStyle：/<bucket>/<dateFilename>，无配置 path 前缀
    assert req.url.path.startswith("/imgs/")
    assert str(req.url).startswith("http://10.0.0.1:9000/imgs/")
    assert url == str(req.url).split("?", 1)[0]


def test_minio_failure_message(sample_file):
    with pytest.raises(RuntimeError, match="MinIO upload failed: 403"):
        s3_mod.minio_upload(
            MinioConfig("h", "", True, "b", "AK", "SK"),
            sample_file,
            make_client(lambda r: httpx.Response(403)),
            now=FIXED_UTC_NOW,
        )


def test_s3_aws_default_virtual_host(sample_file):
    recorded = {}
    client = make_client(_recording_put_handler(recorded))
    cfg = GenericS3Config(
        endpoint="", region="us-west-2", bucket="bk",
        access_key_id="AK", access_key_secret="SK", path="p",
    )
    url = s3_mod.s3_upload(
        cfg, sample_file, client, now=FIXED_UTC_NOW, clock_ms=lambda: FIXED_MS
    )
    req = recorded["request"]
    assert req.url.host == "bk.s3.us-west-2.amazonaws.com"
    assert req.url.path.startswith("/p/")
    assert url.startswith("https://bk.s3.us-west-2.amazonaws.com/p/")


def test_s3_custom_endpoint_with_scheme_prefix(sample_file):
    recorded = {}
    client = make_client(_recording_put_handler(recorded))
    cfg = GenericS3Config(
        endpoint="s3.example.com", region="auto", bucket="bk",
        access_key_id="AK", access_key_secret="SK",
    )
    url = s3_mod.s3_upload(
        cfg, sample_file, client, now=FIXED_UTC_NOW, clock_ms=lambda: FIXED_MS
    )
    assert recorded["request"].url.host == "bk.s3.example.com"
    assert url.startswith("https://bk.s3.example.com/")


def test_s3_path_style_and_cdn(sample_file):
    recorded = {}
    client = make_client(_recording_put_handler(recorded))
    cfg = GenericS3Config(
        endpoint="https://s3.example.com", region="auto", bucket="bk",
        access_key_id="AK", access_key_secret="SK", path_style=True,
        cdn_host="https://cdn.x.com", path="p",
    )
    url = s3_mod.s3_upload(
        cfg, sample_file, client, now=FIXED_UTC_NOW, clock_ms=lambda: FIXED_MS
    )
    req = recorded["request"]
    assert req.url.host == "s3.example.com"
    assert req.url.path.startswith("/bk/p/")
    assert url.startswith("https://cdn.x.com/p/")


def test_s3_path_style_default_return_http(sample_file):
    client = make_client(_recording_put_handler({}))
    cfg = GenericS3Config(
        endpoint="http://127.0.0.1:9000", region="auto", bucket="bk",
        access_key_id="AK", access_key_secret="SK", path_style=True,
    )
    url = s3_mod.s3_upload(
        cfg, sample_file, client, now=FIXED_UTC_NOW, clock_ms=lambda: FIXED_MS
    )
    assert url.startswith("http://127.0.0.1:9000/bk/")


def test_r2_virtual_host_and_domain(sample_file):
    recorded = {}
    client = make_client(_recording_put_handler(recorded))
    cfg = R2Config(
        account_id="acc", access_key="AK", secret_key="SK",
        bucket="bk", path="img", domain="https://pub.r2.dev",
    )
    url = s3_mod.r2_upload(
        cfg, sample_file, client, now=FIXED_UTC_NOW, clock_ms=lambda: FIXED_MS
    )
    req = recorded["request"]
    assert req.url.host == "bk.acc.r2.cloudflarestorage.com"
    assert req.url.path.startswith("/img/")
    assert url.startswith("https://pub.r2.dev/img/")


def test_r2_domain_used_verbatim_no_slash_trim(sample_file):
    # 逐字：domain 不做尾斜杠裁剪
    client = make_client(_recording_put_handler({}))
    cfg = R2Config(
        account_id="acc", access_key="AK", secret_key="SK",
        bucket="bk", path="", domain="https://pub.r2.dev/",
    )
    url = s3_mod.r2_upload(
        cfg, sample_file, client, now=FIXED_UTC_NOW, clock_ms=lambda: FIXED_MS
    )
    assert "pub.r2.dev//" in url


# --------------------------------------------------------------------------
# 微信公众号
# --------------------------------------------------------------------------


def _mp_token_response(expires_in=7200):
    return httpx.Response(
        200,
        json={"access_token": "MP-TOKEN", "expires_in": expires_in, "errcode": 0},
    )


def test_mp_small_jpeg_uses_uploadimg_and_caches_token(sample_file):
    calls = {"stable_token": 0}
    small_jpeg = UploadFile("a.jpg", "image/jpeg", b"x" * 100)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/cgi-bin/stable_token"):
            calls["stable_token"] += 1
            return _mp_token_response()
        assert request.url.path.endswith("/cgi-bin/media/uploadimg")
        assert "access_token=MP-TOKEN" in str(request.url)
        return httpx.Response(200, json={"url": "https://mmbiz.qpic.cn/a.jpg"})

    client = make_client(handler)
    store = InMemoryMpTokenStore()
    cfg = MpConfig("appid", "secret")
    url1 = mp_mod.mp_upload(cfg, small_jpeg, client, store, now_ms=lambda: 1000)
    url2 = mp_mod.mp_upload(cfg, small_jpeg, client, store, now_ms=lambda: 2000)
    assert url1 == url2 == "https://mmbiz.qpic.cn/a.jpg"
    # 第二次命中缓存（expire=1000+7200_000 > 2000）
    assert calls["stable_token"] == 1
    cached = json.loads(store.get("appid"))
    assert cached["expire"] == 1000 + 7200 * 1000


def test_mp_token_expired_refetches(sample_file):
    calls = [0]
    store = InMemoryMpTokenStore()

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/cgi-bin/stable_token"):
            calls[0] += 1
            return _mp_token_response(expires_in=1)
        return httpx.Response(200, json={"url": "https://mmbiz.qpic.cn/x.jpg"})

    client = make_client(handler)
    cfg = MpConfig("appid", "secret")
    mp_mod.mp_upload(
        cfg, UploadFile("a.jpg", "image/jpeg", b"x"), client, store, now_ms=lambda: 1000
    )
    # 2000ms > 1000 + 1000ms TTL → 重新获取
    mp_mod.mp_upload(
        cfg, UploadFile("a.jpg", "image/jpeg", b"x"), client, store, now_ms=lambda: 2001
    )
    assert calls[0] == 2


def test_mp_large_png_uses_add_material(sample_file):
    big_png = UploadFile("a.png", "image/png", b"x" * (1024 * 1024 + 1))

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/cgi-bin/stable_token"):
            return _mp_token_response()
        assert request.url.path.endswith("/cgi-bin/material/add_material")
        assert request.url.query == b"access_token=MP-TOKEN&type=image"
        return httpx.Response(200, json={"url": "https://mmbiz.qpic.cn/big.png"})

    url = mp_mod.mp_upload(
        MpConfig("appid", "secret"), big_png, make_client(handler), InMemoryMpTokenStore()
    )
    assert url == "https://mmbiz.qpic.cn/big.png"


def test_mp_small_gif_uses_add_material(sample_file):
    gif = UploadFile("a.gif", "image/gif", b"x" * 10)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/cgi-bin/stable_token"):
            return _mp_token_response()
        assert request.url.path.endswith("/cgi-bin/material/add_material")
        return httpx.Response(200, json={"url": "https://mmbiz.qpic.cn/g.gif"})

    mp_mod.mp_upload(
        MpConfig("appid", "secret"), gif, make_client(handler), InMemoryMpTokenStore()
    )


def test_mp_text_plain_body_is_json(sample_file):
    # issue #1877：微信以 text/plain 返回 JSON 也必须正常解析
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/cgi-bin/stable_token"):
            return httpx.Response(
                200,
                headers={"content-type": "text/plain"},
                content=b'{"access_token":"T","expires_in":7200}',
            )
        return httpx.Response(
            200, headers={"content-type": "text/plain"},
            content=b'{"url":"https://mmbiz.qpic.cn/p.jpg"}',
        )

    url = mp_mod.mp_upload(
        MpConfig("a", "s"),
        UploadFile("a.jpg", "image/jpeg", b"x"),
        make_client(handler),
        InMemoryMpTokenStore(),
    )
    assert url == "https://mmbiz.qpic.cn/p.jpg"


def test_mp_token_errcode_raises(sample_file):
    client = make_client(
        lambda r: httpx.Response(200, json={"errcode": 40013, "errmsg": "invalid appid"})
    )
    with pytest.raises(RuntimeError, match=r"accessTokenFailed: \[40013\] invalid appid"):
        mp_mod.mp_upload(
            MpConfig("bad", "s"), sample_file, client, InMemoryMpTokenStore()
        )


def test_mp_upload_no_url_errcode(sample_file):
    def handler(request):
        if request.url.path.endswith("/cgi-bin/stable_token"):
            return _mp_token_response()
        return httpx.Response(200, json={"errcode": 45009, "errmsg": "rate limit"})

    with pytest.raises(RuntimeError, match=r"uploadNoUrl: \[45009\]"):
        mp_mod.mp_upload(
            MpConfig("a", "s"),
            UploadFile("a.jpg", "image/jpeg", b"x"),
            make_client(handler),
            InMemoryMpTokenStore(),
        )


def test_mp_proxy_origin_replaces_prefix_and_wsrv(sample_file):
    def handler(request: httpx.Request) -> httpx.Response:
        if "/stable_token" in str(request.url):
            return _mp_token_response()
        assert request.url.host == "proxy.example.com"
        return httpx.Response(200, json={"url": "https://mmbiz.qpic.cn/a b.jpg"})

    client = make_client(handler)
    cfg = MpConfig("a", "s", proxy_origin="https://proxy.example.com")
    # http(s) 页面 → wsrv 反代
    url = mp_mod.mp_upload(
        cfg,
        UploadFile("a.jpg", "image/jpeg", b"x"),
        client,
        InMemoryMpTokenStore(),
        page_href="http://localhost:5173/edit",
    )
    assert url.startswith("https://wsrv.nl?url=")
    assert "https%3A%2F%2Fmmbiz.qpic.cn%2Fa%20b.jpg" in url


def test_mp_proxy_without_http_page_no_wsrv(sample_file):
    def handler(request):
        if "/stable_token" in str(request.url):
            return _mp_token_response()
        return httpx.Response(200, json={"url": "https://mmbiz.qpic.cn/a.jpg"})

    url = mp_mod.mp_upload(
        MpConfig("a", "s", proxy_origin="https://proxy.example.com"),
        UploadFile("a.jpg", "image/jpeg", b"x"),
        make_client(handler),
        InMemoryMpTokenStore(),
        page_href="",
    )
    assert url == "https://mmbiz.qpic.cn/a.jpg"


# --------------------------------------------------------------------------
# telegram
# --------------------------------------------------------------------------


def test_telegram_two_step_success(sample_file):
    order = []

    def handler(request: httpx.Request) -> httpx.Response:
        order.append(request.url.path)
        if request.url.path.endswith("/sendPhoto"):
            assert b'name="chat_id"' in request.content
            assert b'name="photo"' in request.content
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "result": {
                        "photo": [
                            {"file_id": "small", "file_size": 100},
                            {"file_id": "large", "file_size": 999},
                        ]
                    },
                },
            )
        assert request.url.path.endswith("/getFile")
        assert request.url.query == b"file_id=large"
        return httpx.Response(
            200, json={"ok": True, "result": {"file_path": "photos/file_0.jpg"}}
        )

    url = telegram_mod.telegram_upload(
        TelegramConfig("BOTTOK", "-100123"), sample_file, make_client(handler)
    )
    assert url == "https://api.telegram.org/file/botBOTTOK/photos/file_0.jpg"
    assert len(order) == 2


def test_telegram_send_failure(sample_file):
    client = make_client(
        lambda r: httpx.Response(200, json={"ok": False, "description": "chat not found"})
    )
    with pytest.raises(RuntimeError, match="telegramSendPhotoFailed"):
        telegram_mod.telegram_upload(TelegramConfig("t", "c"), sample_file, client)


def test_telegram_getfile_failure(sample_file):
    def handler(request):
        if request.url.path.endswith("/sendPhoto"):
            return httpx.Response(
                200, json={"ok": True, "result": {"photo": [{"file_id": "f"}]}}
            )
        return httpx.Response(200, json={"ok": False})

    with pytest.raises(RuntimeError, match="telegramGetFileFailed"):
        telegram_mod.telegram_upload(
            TelegramConfig("t", "c"), sample_file, make_client(handler)
        )


# --------------------------------------------------------------------------
# github（Web 客户端版）
# --------------------------------------------------------------------------


def test_github_parse_repo_url_variants():
    assert github_mod.parse_github_repo_url("https://github.com/doocs/md") == ("doocs", "md")
    assert github_mod.parse_github_repo_url("http://github.com/doocs/md") == ("doocs", "md")
    assert github_mod.parse_github_repo_url("github.com/doocs/md") == ("doocs", "md")


def test_github_web_upload_recording(sample_file):
    recorded = {}

    def handler(request: httpx.Request) -> httpx.Response:
        recorded["request"] = request
        assert request.method == "PUT"
        assert request.headers["authorization"] == "token ghp_x"
        return httpx.Response(
            200,
            json={
                "content": {
                    "download_url": "https://raw.githubusercontent.com/doocs/md/master/p/a.png"
                }
            },
        )

    url = github_mod.github_web_upload(
        GithubWebConfig("doocs", "md", "ghp_x"),
        sample_file,
        make_client(handler),
        location_href="https://doocs.github.io/md/",
        now_sec=FIXED_SEC,
        clock_ms=lambda: FIXED_MS,
    )
    req = recorded["request"]
    assert req.url.path.startswith("/repos/doocs/md/contents/2025/10/15/")
    body = json.loads(req.content)
    assert body["branch"] == "master"
    assert body["message"] == "Upload by https://doocs.github.io/md/"
    assert body["content"]  # base64 非空
    assert url == "https://raw.githubusercontent.com/doocs/md/master/p/a.png"


def test_github_web_cdn_rewrite(sample_file):
    def handler(request):
        return httpx.Response(
            200,
            json={
                "content": {
                    "download_url": "https://raw.githubusercontent.com/doocs/md/master/p/a.png"
                }
            },
        )

    cfg = GithubWebConfig("doocs", "md", "t", use_cdn=True)
    url = github_mod.github_web_upload(
        cfg,
        sample_file,
        make_client(handler),
        now_sec=FIXED_SEC,
        clock_ms=lambda: FIXED_MS,
    )
    assert url == "https://fastly.jsdelivr.net/gh/doocs/md@master/p/a.png"


def test_github_web_failure(sample_file):
    client = make_client(lambda r: httpx.Response(401, text="no"))
    with pytest.raises(RuntimeError, match="GitHub upload failed"):
        github_mod.github_web_upload(
            GithubWebConfig("a", "b", "t"), sample_file, client, now_sec=FIXED_SEC
        )


# --------------------------------------------------------------------------
# default（md-api）
# --------------------------------------------------------------------------


def test_default_upload_with_bearer(sample_file):
    recorded = {}

    def handler(request: httpx.Request) -> httpx.Response:
        recorded["request"] = request
        assert request.headers["authorization"] == "Bearer JWT"
        return httpx.Response(200, json={"url": "https://u.com/a.png"})

    url = default_mod.default_upload(
        DefaultConfig("https://api.example.com", "JWT"), sample_file, make_client(handler)
    )
    assert recorded["request"].url.path == "/upload"
    assert url == "https://u.com/a.png"


def test_default_upload_no_auth_header(sample_file):
    recorded = {}
    default_mod.default_upload(
        DefaultConfig("https://api.example.com"),
        sample_file,
        make_client(
            lambda r: (recorded.update(r=r) or httpx.Response(200, json={"url": "u"}))
        ),
    )
    assert "authorization" not in recorded["r"].headers


@pytest.mark.parametrize(
    "payload,expected",
    [
        ({"message": "boom"}, "boom"),
        ({"error": "bad"}, "bad"),
        ({}, "Bad Request"),
    ],
)
def test_default_upload_error_fallback(sample_file, payload, expected):
    client = make_client(lambda r: httpx.Response(400, json=payload))
    with pytest.raises(default_mod.UploadApiError) as exc:
        default_mod.default_upload(DefaultConfig("https://a"), sample_file, client)
    assert exc.value.status == 400
    assert str(exc.value) == expected


def test_default_upload_missing_url_raises(sample_file):
    client = make_client(lambda r: httpx.Response(200, json={}))
    with pytest.raises(default_mod.UploadApiError, match="upload_failed"):
        default_mod.default_upload(DefaultConfig("https://a"), sample_file, client)


# --------------------------------------------------------------------------
# formCustom 注册入口
# --------------------------------------------------------------------------


def test_form_custom_registered_entry_point(sample_file):
    @register_form_custom("test-host")
    def _handler(file, content_b64, util, config, http_client):
        assert util["qiniu_token"]
        return f"https://custom.example.com/{file.name}"

    url = form_custom_upload(
        FCC("test-host", "// raw js kept verbatim"), sample_file, make_client(lambda r: None)
    )
    assert url == "https://custom.example.com/shot.PNG"


def test_form_custom_unknown_raises(sample_file):
    with pytest.raises(KeyError, match="not registered"):
        form_custom_upload(
            FCC("missing"), sample_file, make_client(lambda r: None)
        )


# --------------------------------------------------------------------------
# 注册表与统一调度
# --------------------------------------------------------------------------


def test_provider_registry_order_and_keys():
    ids = [p.id for p in UPLOAD_PROVIDERS]
    assert ids == [
        "default", "github", "aliOSS", "txCOS", "qiniu", "minio", "s3",
        "mp", "r2", "upyun", "telegram", "cloudinary", "formCustom", "dcloud",
    ]
    config_keys = {p.id: p.config_key for p in UPLOAD_PROVIDERS if p.config_key}
    assert config_keys["github"] == "githubConfig"
    assert config_keys["cloudinary"] == "cloudinaryConfig"


@pytest.mark.parametrize("value", ["unknown", "", None, 42])
def test_resolve_upload_provider_fallback(value):
    assert resolve_upload_provider(value).id == "default"


def test_dispatch_default_qiniu_telegram(sample_file):
    # 经统一 file_upload 入口走通三家，验证 provider 解析与 env 过滤
    client = make_client(
        lambda r: httpx.Response(200, json={"url": "https://u/a.png"})
    )
    url = file_upload(
        "default", sample_file, DefaultConfig("https://api"), client
    )
    assert url == "https://u/a.png"

    qclient = make_client(lambda r: httpx.Response(200, json={"key": "k"}))
    url2 = file_upload(
        "qiniu", sample_file, QiniuConfig("AK", "SK", "b", domain="https://d"),
        qclient, env={"now_sec": FIXED_SEC, "clock_ms": lambda: FIXED_MS},
    )
    assert url2.startswith("https://d/")

    def tg_handler(request):
        if request.url.path.endswith("/sendPhoto"):
            return httpx.Response(
                200, json={"ok": True, "result": {"photo": [{"file_id": "f"}]}}
            )
        return httpx.Response(
            200, json={"ok": True, "result": {"file_path": "p.jpg"}}
        )

    url3 = file_upload(
        "telegram", sample_file, TelegramConfig("tok", "chat"), make_client(tg_handler)
    )
    assert url3 == "https://api.telegram.org/file/bottok/p.jpg"
