"""TR-14.1 图床签名向量重新生成器（qiniu/upyun/cloudinary/dcloud 四家）。

qiniu/upyun/cloudinary 的浏览器侧签名经锁版 crypto-es@3.1.3 录制（apps/web
依赖），dcloud 经 md-cli 真实环境 node:crypto HMAC-MD5 录制；Python 侧用
标准库 hmac/hashlib 复算，全部一致后重写
tests/golden/uploader_signature_vectors.json。输入刻意包含中文与 ``+//=``
等 Base64 敏感字符，以覆盖 UTF-8 编码与 safe64 padding 保留语义。
"""

import json
import subprocess
from pathlib import Path

from doocs_md_py.uploaders.cloudinary import cloudinary_signature
from doocs_md_py.uploaders.dcloud import dcloud_sign
from doocs_md_py.uploaders.qiniu import qiniu_upload_token
from doocs_md_py.uploaders.upyun import upyun_signature

APP_ROOT = Path(__file__).resolve().parents[1]
TARGET = APP_ROOT / "tests" / "golden" / "uploader_signature_vectors.json"
WORK = APP_ROOT / ".temp-uploader-sig"
WSL_WORK = "/mnt/d/AI/apps/doocs-md-py/.temp-uploader-sig"

PACKAGE_JSON = json.dumps(
    {
        "name": "uploader-sig-harness",
        "private": True,
        "version": "1.0.0",
        "type": "module",
        "dependencies": {"crypto-es": "^3.1.3"},
    },
    indent=2,
)

GEN_MJS = r"""import crypto from "node:crypto";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const CryptoES = require("crypto-es");

const out = {};

// ---- qiniu（providers.ts:111-125 + tokenTools safe64）----
{
  const AK = "qiniu-ak-中文";
  const SK = "qiniu-secret-密钥/+==";
  const putPolicy = { scope: "test-bucket", deadline: 1760503600, isPrefixalScope: 1 };
  const safe64 = (b64) => b64.replace(/\+/g, "-").replace(/\//g, "_");
  const encoded = safe64(
    Buffer.from(JSON.stringify(putPolicy), "utf8").toString("base64"),
  );
  // crypto-es@3.x enc.Base64 即平铺导出 Base64（见上游 crypto-js-compat.ts:96）
  const sign = safe64(
    CryptoES.HmacSHA1(encoded, SK).toString(CryptoES.Base64),
  );
  out.qiniu = {
    access_key: AK, secret_key: SK, put_policy: putPolicy, encoded,
    token: `${AK}:${sign}:${encoded}`,
  };
}

// ---- upyun（providers.ts:540-548）----
{
  const password = "upyun-pw-密码";
  const uri = "/upyun-bucket/图床/2026/a.png";
  const date = "Wed, 15 Oct 2025 03:46:40 GMT";
  const passwordMd5 = CryptoES.MD5(password).toString();
  const signStr = `PUT&${uri}&${date}`;
  out.upyun = {
    password, uri, date,
    password_md5: passwordMd5,
    signature: CryptoES.HmacSHA1(signStr, passwordMd5).toString(CryptoES.Base64),
  };
}

// ---- cloudinary（providers.ts:645-653，键序 sort + & join + secret 后 SHA1）----
{
  const params = {
    folder: "f/中文 目录",
    timestamp: "1760503600",
    upload_preset: "preset-01",
  };
  const apiSecret = "cloud-secret/+=中文";
  const toSign =
    Object.keys(params).sort().map((k) => `${k}=${params[k]}`).join("&") + apiSecret;
  out.cloudinary = {
    params, api_secret: apiSecret,
    signature: CryptoES.SHA1(toSign).toString(),
  };
}

// ---- dcloud（md-cli/util.js:58-64，node:crypto HMAC-MD5 hex）----
{
  const data = {
    method: "serverless.auth.user.anonymousAuthorize",
    params: "{}",
    spaceId: "sp-空间-id",
    timestamp: 1760503600,
  };
  const secret = "dcloud-client-secret-中文";
  const str = Object.keys(data)
    .sort()
    .reduce((acc, cur) => `${acc}&${cur}=${data[cur]}`, "")
    .slice(1);
  out.dcloud = {
    data, secret,
    string_to_sign: str,
    signature: crypto.createHmac("md5", secret).update(str).digest("hex"),
  };
}

process.stdout.write(JSON.stringify(out, null, 2));
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
        "&& node gen.mjs > /work/sig_out.json && echo DONE\""
    )
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
    return json.loads((WORK / "sig_out.json").read_text(encoding="utf-8"))


def main() -> None:
    _write_workdir()
    ref = _run_node_harness()

    # qiniu
    q = ref["qiniu"]
    py_token = qiniu_upload_token(q["access_key"], q["secret_key"], q["put_policy"])
    assert py_token == q["token"], f"qiniu mismatch:\n{py_token}\n{q['token']}"
    print(f"qiniu: Python == crypto-es -> {py_token}")

    # upyun
    u = ref["upyun"]
    py_sig = upyun_signature(u["password"], "PUT", u["uri"], u["date"])
    assert py_sig == u["signature"], f"upyun mismatch:\n{py_sig}\n{u['signature']}"
    print(f"upyun: Python == crypto-es -> {py_sig}")

    # cloudinary
    c = ref["cloudinary"]
    py_sig = cloudinary_signature(c["params"], c["api_secret"])
    assert py_sig == c["signature"], f"cloudinary mismatch:\n{py_sig}\n{c['signature']}"
    print(f"cloudinary: Python == crypto-es -> {py_sig}")

    # dcloud
    d = ref["dcloud"]
    py_sig = dcloud_sign(d["data"], d["secret"])
    assert py_sig == d["signature"], f"dcloud mismatch:\n{py_sig}\n{d['signature']}"
    print(f"dcloud: Python == node:crypto -> {py_sig}")

    golden = {
        "source": {
            "reference_implementation": "crypto-es@3.1.3 (apps/web 锁版) + "
            "node:crypto (md-cli 真实环境) on Node.js v22 (podman node:22-alpine)",
            "note": "qiniu safe64 保留 Base64 padding；HMAC 密钥与消息一律 UTF-8；"
            "upyun 的 HMAC 密钥为 MD5 密码的 32 位 hex 字符串（非摘要字节）。",
        },
        "vectors": ref,
    }
    TARGET.write_text(
        json.dumps(golden, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"golden written: {TARGET}")
    print(f"harness 目录保留在 {WORK}，可用 WSL rm -rf 清理")


if __name__ == "__main__":
    main()
