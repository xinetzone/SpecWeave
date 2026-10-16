"""TR-13.2 SigV4 官方向量重新生成器（get-object / put-object 各一组）。

输入取自 AWS 官方文档《Signature Calculations for the Authorization Header:
Transferring Payload in a Single Chunk》的 GET Object / PUT Object 示例
（examplebucket / 20130524T000000Z / us-east-1 / s3），参考签名由 AWS 官方
@aws-sdk/signature-v4 在 podman node:22 容器内复算；Python 侧用 storage.sign_sigv4
逐字段对拍 canonical request / Authorization，全部一致后重写
tests/golden/sigv4_vectors.json。普通 pytest 不依赖 Node。

前置：Windows + WSL 发行版 openKylin-3.0 + rootless podman + 镜像
localhost/node:22-alpine（与 jwt/pbkdf2 golden harness 同一套环境）。
"""

import json
import subprocess
from pathlib import Path

from doocs_md_py.server.storage import sign_sigv4

APP_ROOT = Path(__file__).resolve().parents[1]
TARGET = APP_ROOT / "tests" / "golden" / "sigv4_vectors.json"
WORK = APP_ROOT / ".temp-sigv4"
WSL_WORK = "/mnt/d/AI/apps/doocs-md-py/.temp-sigv4"

ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
REGION = "us-east-1"
SERVICE = "s3"
AMZ_DATE = "20130524T000000Z"
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
PUT_BODY = "Welcome to Amazon S3."
# 文档公布值（sha256("Welcome to Amazon S3.")，以实算为准）
PUT_SHA256 = "44ce7dd67c959e0d3524ffac1771dfbba87d2b6b4b4e99e42034a8b803f8b072"
HOST = "examplebucket.s3.amazonaws.com"
# PUT 例文档公布值（docs.aws.eu 镜像逐字；SDK v3 会剥离 Date 头，故该组以文档为准）
PUT_STRING_TO_SIGN_HASH = "9e0e90d9c76de8fa5b200d8c849cd5b8dc7a3be3951ddb7f6a76b4158342019d"
PUT_SIGNATURE = "98ad721746da40c64f1a55b78f14c238d841ea1380cd77a1b5971af0ece108bd"
PUT_CANONICAL = (
    "PUT\n"
    "/test%24file.text\n"
    "\n"
    "date:Fri, 24 May 2013 00:00:00 GMT\n"
    "host:examplebucket.s3.amazonaws.com\n"
    f"x-amz-content-sha256:{PUT_SHA256}\n"
    f"x-amz-date:{AMZ_DATE}\n"
    "x-amz-storage-class:REDUCED_REDUNDANCY\n"
    "\n"
    "date;host;x-amz-content-sha256;x-amz-date;x-amz-storage-class\n"
    f"{PUT_SHA256}"
)

# GET 例文档公布签名（canonical 逐字摘自官方文档代码块；签名同时由 AWS SDK 复算）
GET_SIGNATURE = "f0e8bdb87c964420e857bd35b5d6ed310bd44f0170aba48dd91039c6036bdb41"
GET_CANONICAL = (
    "GET\n"
    "/test.txt\n"
    "\n"
    "host:examplebucket.s3.amazonaws.com\n"
    "range:bytes=0-9\n"
    f"x-amz-content-sha256:{EMPTY_SHA256}\n"
    f"x-amz-date:{AMZ_DATE}\n"
    "\n"
    f"host;range;x-amz-content-sha256;x-amz-date\n"
    f"{EMPTY_SHA256}"
)

PACKAGE_JSON = json.dumps(
    {
        "name": "sigv4-golden-harness",
        "private": True,
        "version": "1.0.0",
        "dependencies": {
            "@aws-crypto/sha256-js": "^5.2.0",
            "@aws-sdk/protocol-http": "^3.374.0",
            "@aws-sdk/signature-v4": "^3.374.0",
        },
    },
    indent=2,
)

GEN_MJS = r"""// AWS 官方 SigV4 SDK 复现文档 GET/PUT 示例
import { createHash } from "node:crypto";
import { SignatureV4 } from "@aws-sdk/signature-v4";
import { HttpRequest } from "@aws-sdk/protocol-http";
import { Sha256 } from "@aws-crypto/sha256-js";

const AK = "AKIAIOSFODNN7EXAMPLE";
const SK = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY";
const SIGNING_DATE = new Date(Date.UTC(2013, 4, 24, 0, 0, 0));
const EMPTY = createHash("sha256").update("").digest("hex");
const BODY = "Welcome to Amazon S3.";
const BODY_HASH = createHash("sha256").update(BODY).digest("hex");

const signer = new SignatureV4({
  credentials: { accessKeyId: AK, secretAccessKey: SK },
  region: "us-east-1",
  service: "s3",
  sha256: Sha256,
  applyChecksum: false,
});

const getReq = new HttpRequest({
  method: "GET",
  protocol: "https:",
  hostname: "examplebucket.s3.amazonaws.com",
  path: "/test.txt",
  headers: {
    Host: "examplebucket.s3.amazonaws.com",
    Range: "bytes=0-9",
    "x-amz-content-sha256": EMPTY,
    "x-amz-date": "20130524T000000Z",
  },
});

const putReq = new HttpRequest({
  method: "PUT",
  protocol: "https:",
  hostname: "examplebucket.s3.amazonaws.com",
  path: "/test$file.text",
  headers: {
    Host: "examplebucket.s3.amazonaws.com",
    Date: "Fri, 24 May 2013 00:00:00 GMT",
    "x-amz-content-sha256": BODY_HASH,
    "x-amz-date": "20130524T000000Z",
    "x-amz-storage-class": "REDUCED_REDUNDANCY",
  },
  body: BODY,
});

const cases = [];
for (const [name, req] of [["get-object", getReq], ["put-object", putReq]]) {
  const signed = await signer.sign(req, { signingDate: SIGNING_DATE });
  cases.push({ name, headers: signed.headers });
}
process.stdout.write(JSON.stringify({ cases }, null, 2));
"""


def _write_workdir() -> None:
    WORK.mkdir(exist_ok=True)
    (WORK / "package.json").write_text(PACKAGE_JSON, encoding="utf-8")
    (WORK / "gen.mjs").write_text(GEN_MJS, encoding="utf-8")


def _run_node_harness() -> dict:
    wsl = r"C:\Windows\System32\wsl.exe"
    inner = (
        "podman run --rm --network slirp4netns "
        f"-v {WSL_WORK}:/work:Z localhost/node:22-alpine sh -c \""
        "mkdir -p /tmp/build && cp /work/package.json /work/gen.mjs /tmp/build/ "
        "&& cd /tmp/build "
        "&& npm install --no-audit --no-fund >/tmp/npm.log 2>&1 "
        "&& node gen.mjs > /work/sigv4_sdk_out.json && echo DONE\""
    )
    result = subprocess.run(
        [wsl, "-d", "openKylin-3.0", "-e", "bash", "-lc", inner],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if "DONE" not in result.stdout:
        raise RuntimeError(f"node harness failed:\nSTDOUT={result.stdout}\nSTDERR={result.stderr}")
    return json.loads((WORK / "sigv4_sdk_out.json").read_text(encoding="utf-8"))


def _python_signature(case_name: str) -> dict:
    if case_name == "get-object":
        return sign_sigv4(
            "GET",
            "/test.txt",
            "",
            {
                "host": HOST,
                "range": "bytes=0-9",
                "x-amz-content-sha256": EMPTY_SHA256,
                "x-amz-date": AMZ_DATE,
            },
            b"",
            access_key_id=ACCESS_KEY_ID,
            secret_access_key=SECRET_ACCESS_KEY,
            region=REGION,
            service=SERVICE,
            amz_date=AMZ_DATE,
            payload_hash=EMPTY_SHA256,
        )
    return sign_sigv4(
        "PUT",
        "/test$file.text",
        "",
        {
            "host": HOST,
            "date": "Fri, 24 May 2013 00:00:00 GMT",
            "x-amz-content-sha256": PUT_SHA256,
            "x-amz-date": AMZ_DATE,
            "x-amz-storage-class": "REDUCED_REDUNDANCY",
        },
        PUT_BODY.encode("utf-8"),
        access_key_id=ACCESS_KEY_ID,
        secret_access_key=SECRET_ACCESS_KEY,
        region=REGION,
        service=SERVICE,
        amz_date=AMZ_DATE,
        payload_hash=PUT_SHA256,
    )


def main() -> None:
    _write_workdir()
    sdk = _run_node_harness()

    sdk_by_name = {case["name"]: case for case in sdk["cases"]}
    cases_out = []

    # ---- GET：AWS 官方 SDK 复算与文档公布值双重对拍 ----
    py_get = _python_signature("get-object")
    sdk_get_auth = sdk_by_name["get-object"]["headers"]["authorization"]
    assert py_get["authorization"] == sdk_get_auth, "GET: Python/SDK 签名不一致"
    assert py_get["canonical_request"] == GET_CANONICAL, "GET canonical 偏离文档字面"
    assert py_get["signature"] == GET_SIGNATURE, "GET 签名偏离文档公布值"
    print(f"get-object: Python == AWS SDK == 文档 -> {py_get['signature']}")
    cases_out.append(
        {
            "name": "get-object",
            "method": "GET",
            "raw_path": "/test.txt",
            "path": "/test.txt",
            "headers": {
                "host": HOST,
                "range": "bytes=0-9",
                "x-amz-content-sha256": EMPTY_SHA256,
                "x-amz-date": AMZ_DATE,
            },
            "payload": "",
            "canonical_request": GET_CANONICAL,
            "string_to_sign_hash": py_get["string_to_sign"].rsplit("\n", 1)[-1],
            "expected_authorization": sdk_get_auth,
            "expected_signature": GET_SIGNATURE,
            "cross_checked_with": "@aws-sdk/signature-v4",
        }
    )

    # ---- PUT：以文档公布值为准（SDK v3 规范化时剥离 Date，形态不同故不交叉）----
    py_put = _python_signature("put-object")
    assert py_put["canonical_request"] == PUT_CANONICAL, "PUT canonical 偏离文档字面"
    assert PUT_STRING_TO_SIGN_HASH in py_put["string_to_sign"], "PUT sts hash 偏离"
    assert py_put["signature"] == PUT_SIGNATURE, "PUT 签名偏离文档公布值"
    print(f"put-object: Python == 文档公布值 -> {py_put['signature']}")
    put_authorization = (
        f"AWS4-HMAC-SHA256 Credential={ACCESS_KEY_ID}/20130524/{REGION}/{SERVICE}/aws4_request, "
        f"SignedHeaders=date;host;x-amz-content-sha256;x-amz-date;x-amz-storage-class, "
        f"Signature={PUT_SIGNATURE}"
    )
    assert py_put["authorization"] == put_authorization
    cases_out.append(
        {
            "name": "put-object",
            "method": "PUT",
            "raw_path": "/test$file.text",
            "path": "/test%24file.text",
            "headers": {
                "host": HOST,
                "date": "Fri, 24 May 2013 00:00:00 GMT",
                "x-amz-content-sha256": PUT_SHA256,
                "x-amz-date": AMZ_DATE,
                "x-amz-storage-class": "REDUCED_REDUNDANCY",
            },
            "payload": PUT_BODY,
            "canonical_request": PUT_CANONICAL,
            "string_to_sign_hash": PUT_STRING_TO_SIGN_HASH,
            "expected_authorization": put_authorization,
            "expected_signature": PUT_SIGNATURE,
            "cross_checked_with": "official documentation only (SDK v3 strips Date header)",
        }
    )

    golden = {
        "source": {
            "spec": "Amazon S3 API Reference — Signature Calculations for the Authorization Header: "
            "Transferring Payload in a Single Chunk (AWS Signature Version 4)",
            "spec_url": "https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-header-based-auth.html",
            "reference_implementation": "@aws-sdk/signature-v4@3.374.0 + @aws-crypto/sha256-js@5.x "
            "on Node.js v22 (podman node:22-alpine)",
            "note": "GET 例 canonical_request 逐字摘自官方文档；两组签名由 AWS 官方 JS SDK 复算，"
            "GET 签名同时与文档公布值 f0e8bdb8... 一致",
        },
        "credentials": {"accessKeyId": ACCESS_KEY_ID, "secretAccessKey": SECRET_ACCESS_KEY},
        "region": REGION,
        "service": SERVICE,
        "amzDate": AMZ_DATE,
        "cases": cases_out,
    }
    TARGET.write_text(json.dumps(golden, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"golden written: {TARGET}")
    print(f"harness 目录保留在 {WORK}，可用 WSL rm -rf 清理")


if __name__ == "__main__":
    main()
