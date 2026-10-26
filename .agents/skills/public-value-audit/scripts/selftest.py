#!/usr/bin/env python3
"""公开值取值域审计 · Skill 自检。

对内置夹具跑两个工具，断言它们的判定结果符合预期：
    pre-fix     夹具（P1-14 形态：表级授权 + 客户端请求标识列 + 入参决定路径）→ 必须判 FAIL
    p115-only   夹具（P1-15 形态：列级授权已收紧，但值里仍内嵌 owner uid）→ 必须判 FAIL
    post-fix    夹具（收口后：服务端拼装 + 列级授权 + 客户端白名单对齐）→ 必须判 PASS

用法：
    python selftest.py            # 跑全部断言
    python selftest.py --verbose  # 打印工具原始输出

退出码：0 = 自检通过；1 = 自检失败。
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIXTURES = os.path.join(ROOT, "tests", "fixtures")
SCAN = os.path.join(HERE, "scan_public_identifiers.py")
CHECK = os.path.join(HERE, "check_public_value_invariants.py")


def run(script, target, extra=()):
    cmd = [sys.executable, script, target] + list(extra)
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def main():
    verbose = "--verbose" in sys.argv
    failures = []

    def expect(name, cond, detail=""):
        if cond:
            print("  ok   %s" % name)
        else:
            print("  FAIL %s%s" % (name, ("  " + detail) if detail else ""))
            failures.append(name)

    # ── 扫描器 ──────────────────────────────────────────────────────
    print("== 扫描器 ==")
    rc, out = run(SCAN, os.path.join(FIXTURES, "pre-fix"))
    if verbose:
        print(out)
    expect("pre-fix 判为有高危（退出码 1）", rc == 1, "rc=%d" % rc)
    expect("pre-fix 命中 H2（列级授权含标识列）", "[H2]" in out)
    expect("pre-fix 命中 H3（客户端请求标识列）", "[H3]" in out)
    expect("pre-fix 命中 H6（值域由调用方决定）", "[H6]" in out)

    rc, out = run(SCAN, os.path.join(FIXTURES, "p115-only"))
    if verbose:
        print(out)
    expect("p115-only 判为有高危（退出码 1）", rc == 1, "rc=%d" % rc)
    expect("p115-only 命中 H6（服务端用调用方标识拼路径）", "[H6]" in out)
    expect("p115-only 命中 H7（字面量路径内嵌标识段）", "[H7]" in out)

    rc, out = run(SCAN, os.path.join(FIXTURES, "post-fix"))
    if verbose:
        print(out)
    expect("post-fix 无高危（退出码 0）", rc == 0, "rc=%d" % rc)
    # H6 在 post-fix 仍会作为「中危」出现（入参是受形状约束的 slug，不承载标识），
    # 因此判据是「高危段里没有 H6」，而不是「输出里没有 H6」。
    rcj, outj = run(SCAN, os.path.join(FIXTURES, "post-fix"), extra=["--json"])
    import json as _json
    data = _json.loads(outj)
    expect("post-fix 高危段无 H6",
           not [f for f in data["findings"] if f["rule"] == "H6" and f["severity"] == "high"])
    expect("post-fix 高危段无 H7",
           not [f for f in data["findings"] if f["rule"] == "H7" and f["severity"] == "high"])

    # ── 不变量断言器 ────────────────────────────────────────────────
    print("== 不变量断言器 ==")
    rc, out = run(CHECK, os.path.join(FIXTURES, "pre-fix"))
    if verbose:
        print(out)
    expect("pre-fix 存在 FAIL（退出码 1）", rc == 1, "rc=%d" % rc)
    for inv in ("I1", "I2", "I3", "I5", "I6"):
        expect("pre-fix 报出 %s" % inv, inv in out)

    rc, out = run(CHECK, os.path.join(FIXTURES, "p115-only"))
    if verbose:
        print(out)
    expect("p115-only 存在 FAIL（退出码 1）", rc == 1, "rc=%d" % rc)
    expect("p115-only 报出 I3（值域由入参决定）", "I3" in out)
    expect("p115-only 报出 I7（字面量含标识）", "I7" in out)
    expect("p115-only 不报 I1 FAIL（列级授权已收紧）", "❌ I1" not in out)

    rc, out = run(CHECK, os.path.join(FIXTURES, "post-fix"))
    if verbose:
        print(out)
    expect("post-fix 无 FAIL（退出码 0）", rc == 0, "rc=%d" % rc)
    expect("post-fix 不报 I2（客户端白名单已对齐）", "❌ I2" not in out)

    rc, out = run(CHECK, os.path.join(FIXTURES, "post-fix"),
                  extra=["--allow-row-isolated", "registrations"])
    if verbose:
        print(out)
    expect("豁免表名归一化生效（裸名 registrations 也能豁免）", "已豁免 1" in out or "已豁免 2" in out)

    # ── 覆盖率守卫：空目录不得报「全绿」 ──────────────────────────
    import tempfile
    with tempfile.TemporaryDirectory() as empty:
        rc, out = run(CHECK, empty)
        expect("空目录 → 退出码 3（工具未生效，不是项目没问题）", rc == 3, "rc=%d" % rc)
        rc, out = run(SCAN, empty)
        expect("扫描器空目录 → 退出码 3", rc == 3, "rc=%d" % rc)

    print("")
    if failures:
        print("自检失败 %d 项：%s" % (len(failures), ", ".join(failures)))
        return 1
    print("自检全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
