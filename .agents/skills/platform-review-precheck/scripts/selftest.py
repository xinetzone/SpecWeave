#!/usr/bin/env python3
"""平台提审合规预检 · Skill 自检。

对内置前后对照夹具跑两个工具，断言它们的判定结果符合预期：
    pre-fix  夹具必须被判为「有 FAIL」（整改前确实存在拦截项）
    post-fix 夹具必须被判为「无 FAIL」（整改后确实过审）

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
SCAN = os.path.join(HERE, "scan_privacy_calls.py")
CHECK = os.path.join(HERE, "check_declaration_alignment.py")

PRE = os.path.join(FIXTURES, "pre-fix")
POST = os.path.join(FIXTURES, "post-fix")


def run(script, target, extra=()):
    cmd = [sys.executable, script, target] + list(extra)
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, proc.stdout + proc.stderr


def main():
    verbose = "--verbose" in sys.argv
    failures = []

    def expect(name, cond, detail=""):
        if cond:
            print("  ok   %s" % name)
        else:
            print("  FAIL %s%s" % (name, ("  " + detail) if detail else ""))
            failures.append(name)

    print("== 扫描器 ==")
    rc, out = run(SCAN, PRE)
    if verbose:
        print(out)
    expect("pre-fix 被判为有 FAIL（退出码 1）", rc == 1, "rc=%d" % rc)
    expect("pre-fix 命中 wx.chooseMedia", "wx.chooseMedia" in out)
    expect("pre-fix 命中 button getPhoneNumber", "getPhoneNumber" in out)
    expect("pre-fix 命中 wx.chooseMessageFile", "wx.chooseMessageFile" in out)
    expect("pre-fix 列出「收集你选中的照片或视频信息」",
           "收集你选中的照片或视频信息" in out)
    expect("pre-fix 列出「收集你的手机号」", "收集你的手机号" in out)

    rc, out = run(SCAN, POST)
    if verbose:
        print(out)
    expect("post-fix 仍检出隐私接口（整改不改变调用面）", "wx.chooseMedia" in out)
    expect("post-fix 不再命中 wx.chooseMessageFile", "wx.chooseMessageFile" not in out)

    print("== 误报防护 ==")
    # 非小程序项目里的同名本地函数不应被误报成 wx.chooseMedia
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        fake = os.path.join(tmp, "not-a-mp")
        os.makedirs(fake)
        with open(os.path.join(fake, "app.js"), "w", encoding="utf-8") as fh:
            fh.write("function pick() { return chooseMedia({ count: 1 }) }\n")
        rc, out = run(SCAN, fake)
        if verbose:
            print(out)
        expect("非小程序项目的同名本地函数不误报", "wx.chooseMedia" not in out, "rc=%d" % rc)
        expect("非小程序项目被判为非小程序", "非微信小程序项目" in out)

    print("== 声明/调用面对账器 ==")
    rc, out = run(CHECK, PRE)
    if verbose:
        print(out)
    expect("pre-fix 存在 FAIL（退出码 1）", rc == 1, "rc=%d" % rc)
    expect("pre-fix 报出 D1（声明面未覆盖调用面）", "D1" in out and "FAIL" in out)
    expect("pre-fix 报出 D3（缺少授权兜底）", "D3" in out and "FAIL" in out)
    expect("pre-fix 报出 D4（缺少声明文件）", "D4" in out and "FAIL" in out)

    rc, out = run(CHECK, POST)
    if verbose:
        print(out)
    expect("post-fix 无 FAIL（退出码 0）", rc == 0, "rc=%d" % rc)
    expect("post-fix D0 通过（确认为小程序项目）", "D0" in out and "PASS" in out)
    expect("post-fix D1 通过", "D1" in out and "PASS" in out)
    expect("post-fix D3 通过", "D3" in out and "PASS" in out)
    expect("post-fix D4 通过", "D4" in out and "PASS" in out)

    print()
    if failures:
        print("自检失败 %d 项：" % len(failures))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("自检全部通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
