"""TR-12.2 PBKDF2-SHA256 互认向量重新生成器。

在 podman node:22 容器中使用与上游 share-password.ts 完全相同的 WebCrypto
（crypto.subtle.importKey/deriveBits）：
  ① 固定 password/salt/iterations，Node deriveBits 必须等于 Python hashlib 结果；
  ② Python hash_share_password 生成的存储串（随机盐），Node 拆串重算必须相等；
  ③ Node 生成随机盐存储串，Python verify_share_password 必须接受正确密码、拒绝错密码。

输出 tests/golden/share_pbkdf2_interop.json；普通 pytest 不依赖 Node。
"""

import base64
import json
import os
import shutil
import subprocess
from pathlib import Path

from doocs_md_py.server.share_password import (
    PBKDF2_ITERATIONS,
    derive_password_hash,
    hash_share_password,
    verify_share_password,
)

APP_ROOT = Path(__file__).resolve().parents[1]
TARGET = APP_ROOT / "tests" / "golden" / "share_pbkdf2_interop.json"
WORK = APP_ROOT / ".temp-pbkdf2"
WSL_WORK = "/mnt/d/AI/apps/doocs-md-py/.temp-pbkdf2"

PASSWORD = "abcd1234"  # nosec 黄金向量再生成夹具，非真实凭据
WRONG_PASSWORD = "abcd1235"  # nosec 黄金向量再生成夹具，非真实凭据
FIXED_SALT_B64 = "Zml4ZWQtc2FsdC0xNmJ5IQ=="  # b"fixed-salt-16by!"

DERIVE_MJS = r"""// TR-12.2 WebCrypto PBKDF2 互认核验（与上游 share-password.ts 同 API）
import { readFileSync, writeFileSync } from "node:fs"

const input = JSON.parse(readFileSync("/w/input.json", "utf-8"))
const enc = new TextEncoder()

function toBase64(bytes) {
  return Buffer.from(bytes).toString("base64")
}
function fromBase64(value) {
  return new Uint8Array(Buffer.from(value, "base64"))
}
async function derive(password, saltB64, iterations) {
  const key = await crypto.subtle.importKey(
    "raw", enc.encode(password), "PBKDF2", false, ["deriveBits"])
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt: fromBase64(saltB64), iterations, hash: "SHA-256" },
    key, 256)
  return toBase64(new Uint8Array(bits))
}

// 解析存储串 pbkdf2:<iter>:<saltB64>:<hashB64> 并用 WebCrypto 重算
async function verifyStored(password, stored) {
  const [, iterStr, saltB64] = stored.split(":")
  const actual = await derive(password, saltB64, Number(iterStr))
  const expected = stored.split(":")[3]
  return actual === expected
}

const result = { checks: {} }

// ① 固定向量
result.node_fixed_hash_b64 = await derive(
  input.password, input.fixed_salt_b64, input.iterations)
result.checks.fixed_vector_matches =
  result.node_fixed_hash_b64 === input.py_fixed_hash_b64

// ② Python 随机盐存储串，Node 重算相等
result.checks.py_stored_verified_by_node =
  await verifyStored(input.password, input.py_stored)
result.checks.py_stored_rejects_wrong_by_node =
  (await verifyStored(input.wrong_password, input.py_stored)) === false

// ③ Node 生成随机盐存储串，供 Python 侧验证（见 regen 主流程 checks）
const nodeSalt = crypto.getRandomValues(new Uint8Array(16))
const nodeHashB64 = await derive(input.password, toBase64(nodeSalt), input.iterations)
result.node_stored =
  `pbkdf2:${input.iterations}:${toBase64(nodeSalt)}:${nodeHashB64}`

writeFileSync("/w/output.json", JSON.stringify(result, null, 2), "utf-8")
"""


def main() -> int:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)

    fixed_hash = derive_password_hash(
        PASSWORD, base64.b64decode(FIXED_SALT_B64), PBKDF2_ITERATIONS
    )
    py_fixed_hash_b64 = base64.b64encode(fixed_hash).decode("ascii")
    py_stored = hash_share_password(PASSWORD)

    (WORK / "input.json").write_text(
        json.dumps(
            {
                "password": PASSWORD,
                "wrong_password": WRONG_PASSWORD,
                "fixed_salt_b64": FIXED_SALT_B64,
                "iterations": PBKDF2_ITERATIONS,
                "py_fixed_hash_b64": py_fixed_hash_b64,
                "py_stored": py_stored,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (WORK / "derive.mjs").write_text(DERIVE_MJS, encoding="utf-8")

    run_sh = "set -e\ncd /w\nnode --version\nnode derive.mjs\n"
    (WORK / "run.sh").write_bytes(run_sh.encode("utf-8").replace(b"\r\n", b"\n"))

    wsl = Path(os.environ["WINDIR"]) / "System32" / "wsl.exe"
    proc = subprocess.run(
        [
            str(wsl), "-d", "openKylin-3.0", "-e", "bash", "-lc",
            f"podman run --rm --network slirp4netns "
            f"-v '{WSL_WORK}':/w -w /w localhost/node:22-alpine "
            f"sh /w/run.sh",
        ],
        text=True,
        capture_output=True,
        timeout=300,
    )
    if proc.returncode != 0:
        print(proc.stdout[-3000:])
        print(proc.stderr[-3000:])
        return 1

    output = json.loads((WORK / "output.json").read_text(encoding="utf-8"))
    node_version = next(
        (line.strip() for line in proc.stdout.splitlines() if line.startswith("v")),
        "",
    )

    # Python 侧验证 Node 存储串
    node_stored = output["node_stored"]
    checks = dict(output["checks"])
    checks["node_stored_verified_by_python"] = verify_share_password(
        PASSWORD, node_stored
    )
    checks["node_stored_rejects_wrong_by_python"] = not verify_share_password(
        WRONG_PASSWORD, node_stored
    )

    golden = {
        "generated_by": "podman node:22 WebCrypto crypto.subtle（上游 share-password.ts 同 API）"
                        " 与 Python hashlib.pbkdf2_hmac 互认",
        "node": node_version,
        "algorithm": "PBKDF2-HMAC-SHA256",
        "iterations": PBKDF2_ITERATIONS,
        "password": PASSWORD,
        "fixed_salt_b64": FIXED_SALT_B64,
        "fixed_hash_b64": py_fixed_hash_b64,
        "node_stored": node_stored,
        "checks": checks,
    }
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(golden, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(checks, indent=2))
    print(f"regenerated: {TARGET}")
    return 0 if all(checks.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
