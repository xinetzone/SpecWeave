"""TR-14.2 S3 presigned-PUT 向量重新生成器（六场景）。

用上游锁版 @aws-sdk/client-s3@3.1147.0 + @aws-sdk/s3-request-presigner@3.1147.0
在 podman node:22 容器内生成 PutObject presigned URL；Python 侧用
uploaders.s3_presign.build_presigned_put_url 复算整条 URL（含全部查询参数），
逐字节对拍后重写 tests/golden/s3_presign_vectors.json。普通 pytest 不依赖 Node。

场景覆盖：AWS 虚拟主机、自定义 endpoint 虚拟主机/path-style（http 与 https）、
region=auto（MinIO/R2）、含特殊字符（``$`` 与空格）的 key、Content-Type 是否
进入签名集合以 SDK 实际录制为准。
"""

import json
import subprocess
from pathlib import Path

from doocs_md_py.uploaders.s3_presign import build_presigned_put_url

APP_ROOT = Path(__file__).resolve().parents[1]
TARGET = APP_ROOT / "tests" / "golden" / "s3_presign_vectors.json"
WORK = APP_ROOT / ".temp-s3presign"
WSL_WORK = "/mnt/d/AI/apps/doocs-md-py/.temp-s3presign"

ACCESS_KEY_ID = "AKIDTEST1234567890EXAMPLE"
SECRET_ACCESS_KEY = "SECRETSIGNINGKEY-For-Golden-Vectors-0123"
AMZ_DATE = "20261015T034640Z"
EXPIRES_IN = 300
CONTENT_TYPE = "image/png"

# (name, region, endpoint|None, force_path_style, bucket, key)
SCENARIOS = [
    ("aws-vhost", "us-east-1", None, False, "demo-bucket", "2026/10/15/100-shot.png"),
    ("custom-vhost-https", "auto", "https://acc1234.r2.cloudflarestorage.com", False, "mybucket", "dir/a.png"),
    ("custom-path-https", "auto", "https://minio.example.com", True, "mybucket", "dir/a.png"),
    ("minio-http-path", "auto", "http://10.0.0.1:9000", True, "imgs", "2026/10/15/x.png"),
    ("alioss-vhost", "oss-cn-hangzhou", "https://oss-cn-hangzhou.aliyuncs.com", False, "ali-bucket", "p/a$b c.png"),
    ("cos-vhost", "ap-guangzhou", "https://cos.ap-guangzhou.myqcloud.com", False, "cos-bucket-1234567890", "p/a.png"),
]

PACKAGE_JSON = json.dumps(
    {
        "name": "s3-presign-golden-harness",
        "private": True,
        "version": "1.0.0",
        "dependencies": {
            "@aws-sdk/client-s3": "3.1147.0",
            "@aws-sdk/s3-request-presigner": "3.1147.0",
        },
        "type": "module",
    },
    indent=2,
)

GEN_MJS = r"""import { readFileSync } from "node:fs";
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const AK = "AKIDTEST1234567890EXAMPLE";
const SK = "SECRETSIGNINGKEY-For-Golden-Vectors-0123";
const SIGNING_DATE = new Date(Date.UTC(2026, 9, 15, 3, 46, 40));

const scenarios = JSON.parse(readFileSync("/work/scenarios.json", "utf8"));
const out = [];
for (const s of scenarios) {
  const client = new S3Client({
    region: s.region,
    credentials: { accessKeyId: AK, secretAccessKey: SK },
    ...(s.endpoint ? { endpoint: s.endpoint } : {}),
    forcePathStyle: s.forcePathStyle,
  });
  const command = new PutObjectCommand({
    Bucket: s.bucket,
    Key: s.key,
    ContentType: "image/png",
  });
  const url = await getSignedUrl(client, command, {
    expiresIn: 300,
    signingDate: SIGNING_DATE,
  });
  out.push({ name: s.name, url });
}
process.stdout.write(JSON.stringify(out, null, 2));
"""


def _write_workdir() -> None:
    WORK.mkdir(exist_ok=True)
    (WORK / "package.json").write_text(PACKAGE_JSON, encoding="utf-8")
    (WORK / "gen.mjs").write_text(GEN_MJS, encoding="utf-8")


def _run_node_harness() -> list[dict]:
    scenarios_json = json.dumps(
        [
            {
                "name": name,
                "region": region,
                "endpoint": endpoint,
                "forcePathStyle": force,
                "bucket": bucket,
                "key": key,
            }
            for name, region, endpoint, force, bucket, key in SCENARIOS
        ],
        ensure_ascii=False,
    )
    # 经环境变量传 JSON，避开多层 shell 引号
    env_hint = "SCENARIOS"
    wsl = r"C:\Windows\System32\wsl.exe"
    # gen.mjs 从文件读场景，避免 argv 引号地狱
    (WORK / "scenarios.json").write_text(scenarios_json, encoding="utf-8")
    inner = (
        "podman run --rm --network slirp4netns "
        f"-v {WSL_WORK}:/work:Z localhost/node:22-alpine sh -c \""
        "mkdir -p /tmp/build && cp /work/package.json /work/gen.mjs /tmp/build/ "
        "&& cd /tmp/build "
        "&& npm install --no-audit --no-fund >/tmp/npm.log 2>&1 "
        "&& node gen.mjs > /work/sdk_out.json && echo DONE\""
    )
    assert env_hint
    result = subprocess.run(
        [wsl, "-d", "openKylin-3.0", "-e", "bash", "-lc", inner],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if "DONE" not in result.stdout:
        raise RuntimeError(
            f"node harness failed:\nSTDOUT={result.stdout}\nSTDERR={result.stderr}"
        )
    return json.loads((WORK / "sdk_out.json").read_text(encoding="utf-8"))


def main() -> None:
    _write_workdir()
    sdk_urls = _run_node_harness()
    sdk_by_name = {item["name"]: item["url"] for item in sdk_urls}

    cases_out = []
    for name, region, endpoint, force, bucket, key in SCENARIOS:
        sdk_url = sdk_by_name[name]
        if endpoint:
            scheme, bare = endpoint.split("://", 1)
        else:
            scheme, bare = "https", f"s3.{region}.amazonaws.com"
        if force:
            host = bare
            raw_path = f"/{bucket}/{key}"
        elif endpoint:
            host = f"{bucket}.{bare}"
            raw_path = f"/{key}"
        else:
            host = f"{bucket}.s3.{region}.amazonaws.com"
            raw_path = f"/{key}"

        result = build_presigned_put_url(
            host=host,
            raw_path=raw_path,
            access_key_id=ACCESS_KEY_ID,
            secret_access_key=SECRET_ACCESS_KEY,
            region=region,
            amz_date=AMZ_DATE,
            expires_in=EXPIRES_IN,
            scheme=scheme,
        )
        if result["url"] != sdk_url:
            raise AssertionError(
                f"[{name}] URL mismatch:\n SDK={sdk_url}\n PY ={result['url']}"
            )
        print(f"{name}: Python == @aws-sdk 3.1147.0")
        cases_out.append(
            {
                "name": name,
                "region": region,
                "endpoint": endpoint,
                "force_path_style": force,
                "bucket": bucket,
                "key": key,
                "content_type": CONTENT_TYPE,
                "host": host,
                "raw_path": raw_path,
                "scheme": scheme,
                "sdk_url": sdk_url,
                "canonical_request": result["canonical_request"],
            }
        )

    golden = {
        "source": {
            "reference_implementation": "@aws-sdk/client-s3@3.1147.0 + "
            "@aws-sdk/s3-request-presigner@3.1147.0 on Node.js v22 (podman node:22-alpine)",
            "note": "PutObject presigned URL（query 签名），expiresIn=300，签名注入时间 "
            "2026-10-15T03:46:40Z；最终 URL 与 SDK 输出逐字节一致。",
        },
        "credentials": {"accessKeyId": ACCESS_KEY_ID, "secretAccessKey": SECRET_ACCESS_KEY},
        "amzDate": AMZ_DATE,
        "expiresIn": EXPIRES_IN,
        "cases": cases_out,
    }
    TARGET.write_text(
        json.dumps(golden, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"golden written: {TARGET}")
    print(f"harness 目录保留在 {WORK}，可用 WSL rm -rf 清理")


if __name__ == "__main__":
    main()
