"""TR-10.2 JWT HS256 互认向量重新生成器。

在 podman node:22 容器中安装与上游锁定完全一致的 hono@4.13.13，用其 hono/jwt：
  ① 对 Python PyJWT 签发的令牌做 verify（Py → Node 互认）；
  ② sign 出 node_token 供 Python 侧 pytest verify（Node → Py 互认）；
  ③ 过期/错 secret/篡改三类负向量必须被 Node 拒绝。

输出 tests/golden/jwt_interop.json；普通 pytest 不依赖 Node。
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import jwt

APP_ROOT = Path(__file__).resolve().parents[1]
TARGET = APP_ROOT / "tests" / "golden" / "jwt_interop.json"
WORK = APP_ROOT / ".temp-jwt"
WSL_WORK = "/mnt/d/AI/apps/doocs-md-py/.temp-jwt"

SECRET = "interop-secret-0123456789-abcdef-ghijkl"
CLAIMS = {"sub": "fixed-user-001", "login": "octocat", "exp": 2_000_000_000}
EXPIRED_CLAIMS = {"sub": "fixed-user-001", "login": "octocat", "exp": 1_000_000_000}

VERIFY_MJS = r"""// TR-10.2 hono/jwt 互认核验
import { readFileSync, writeFileSync } from "node:fs"
import { sign, verify } from "hono/jwt"

const input = JSON.parse(readFileSync("/w/input.json", "utf-8"))
const result = { checks: {} }

// Node 侧签发（Node → Py 方向的固定向量）
result.node_token = await sign(input.claims, input.secret, "HS256")

// PyJWT 签发的令牌必须被 hono 验签且 claims 全等
const pyClaims = await verify(input.py_token, input.secret, "HS256")
result.checks.py_token_verified_by_node =
  pyClaims.sub === input.claims.sub &&
  pyClaims.login === input.claims.login &&
  pyClaims.exp === input.claims.exp

const selfClaims = await verify(result.node_token, input.secret, "HS256")
result.checks.node_token_self_verified =
  selfClaims.sub === input.claims.sub && selfClaims.login === input.claims.login

async function rejected(fn) {
  try { await fn(); return false } catch { return true }
}

result.checks.py_expired_rejected_by_node = await rejected(
  () => verify(input.py_expired_token, input.secret, "HS256"))
result.checks.wrong_secret_rejected = await rejected(
  () => verify(result.node_token, input.secret + "x", "HS256"))

// 篡改签名末字符
const tampered = result.node_token.slice(0, -1) +
  (result.node_token.endsWith("A") ? "B" : "A")
result.checks.tampered_rejected = await rejected(
  () => verify(tampered, input.secret, "HS256"))

writeFileSync("/w/output.json", JSON.stringify(result, null, 2), "utf-8")
"""


def main() -> int:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)

    py_token = jwt.encode(CLAIMS, SECRET, algorithm="HS256")
    py_expired_token = jwt.encode(EXPIRED_CLAIMS, SECRET, algorithm="HS256")
    (WORK / "input.json").write_text(
        json.dumps(
            {
                "secret": SECRET,
                "claims": CLAIMS,
                "py_token": py_token,
                "py_expired_token": py_expired_token,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (WORK / "verify.mjs").write_text(VERIFY_MJS, encoding="utf-8")

    # 容器内执行脚本落盘，避免多层引号嵌套；LF 行尾供 alpine sh
# fmt: off
    run_sh = (
        "set -e\n"
        "cd /w\n"
        "npm init -y >/dev/null 2>&1\n"
        "npm install --silent --no-audit --no-fund hono@4.13.13 >/tmp/npm.log 2>&1\n"
        "node verify.mjs\n"
        "node -e \"console.log('hono_version='+require('/w/node_modules/hono/package.json').version)\"\n"
    )
# fmt: on
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
        timeout=600,
    )
    if proc.returncode != 0:
        print(proc.stdout[-3000:])
        print(proc.stderr[-3000:])
        return 1

    output = json.loads((WORK / "output.json").read_text(encoding="utf-8"))
    hono_version = ""
    for line in proc.stdout.splitlines():
        if line.startswith("hono_version="):
            hono_version = line.split("=", 1)[1].strip()

    golden = {
        "generated_by": "podman node:22 + hono/jwt (hono 精确版本见下) 与 PyJWT 互认",
        "node_pkg": f"hono@{hono_version}",
        "algorithm": "HS256",
        "secret": SECRET,
        "claims": CLAIMS,
        "expired_claims": EXPIRED_CLAIMS,
        "py_token_generated_by": "PyJWT (本仓库 venv 锁定版本)",
        "node_token": output["node_token"],
        "checks": output["checks"],
    }
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(golden, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(golden["checks"], indent=2))
    print(f"regenerated: {TARGET} ({golden['node_pkg']})")
    return 0 if all(golden["checks"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
