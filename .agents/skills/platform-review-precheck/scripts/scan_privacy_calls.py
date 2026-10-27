#!/usr/bin/env python3
"""平台提审合规预检 · 隐私接口调用扫描器。

从代码侧静态提取小程序的「隐私相关接口 / 组件」调用面，
并映射到平台《用户隐私保护指引》要求声明的「处理的信息」类型。

平台的判定逻辑是：**本次提审版本的隐私接口调用情况** 与 **已填写的隐私协议内容**
逐项比对，只要代码调了某个隐私接口而协议里没有对应条目，审核即拦截。
所以「代码里调了什么」是协议清单的唯一事实来源——本脚本就是把这个事实提取出来。

用法：
    python scan_privacy_calls.py <项目根目录> [--json] [--only-ids] [--verbose]

退出码：
    0 = 未发现 FAIL 级隐私接口调用
    1 = 发现 FAIL 级隐私接口调用（必然需要在平台侧声明）
    2 = 用法错误
"""

import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# 隐私接口 → 平台《用户隐私保护指引》「处理的信息」类型 映射
#
# 数据来源：微信官方《小程序用户隐私保护指引内容介绍》
# https://developers.weixin.qq.com/miniprogram/dev/framework/user-privacy/miniprogram-intro
# 观测于 2026-10-26。官方会随版本增补，改本表前请先核对该页。
#
# 强度分级（沿用「误报比漏报更伤」原则）：
#   strong = 明确指向某类个人信息，调用即需声明 → FAIL
#   weak   = 需运行时上下文才能确定是否真收集 → WARN
#   gone   = 官方已回收的接口，调用即不可用 → FAIL（且不是隐私声明问题）
# ---------------------------------------------------------------------------
PRIVACY_API_MAP = {
    # —— 收集你选中的照片或视频信息 ——
    "chooseImage": ("收集你选中的照片或视频信息", "strong"),
    "chooseMedia": ("收集你选中的照片或视频信息", "strong"),
    "chooseVideo": ("收集你选中的照片或视频信息", "strong"),
    # —— 收集你的昵称、头像 ——
    "getUserProfile": ("收集你的昵称、头像", "gone"),
    "getUserInfo": ("收集你的昵称、头像", "gone"),
    # —— 收集你的手机号 ——
    "getRealtimePhoneNumber": ("收集你的手机号", "strong"),
    # —— 收集你的位置信息 ——
    "getLocation": ("收集你的位置信息", "strong"),
    "startLocationUpdate": ("收集你的位置信息", "strong"),
    "startLocationUpdateBackground": ("收集你的位置信息", "strong"),
    "getFuzzyLocation": ("收集你的位置信息", "strong"),
    "moveToLocation": ("收集你的位置信息", "strong"),
    # —— 收集你选择的位置信息 ——
    "choosePoi": ("收集你选择的位置信息", "strong"),
    "chooseLocation": ("收集你选择的位置信息", "strong"),
    # —— 收集你的地址 ——
    "chooseAddress": ("收集你的地址", "strong"),
    # —— 收集你的发票信息 ——
    "chooseInvoiceTitle": ("收集你的发票信息", "strong"),
    "chooseInvoice": ("收集你的发票信息", "strong"),
    # —— 收集你的微信运动步数 ——
    "getWeRunData": ("收集你的微信运动步数", "strong"),
    # —— 收集你选中的文件 ——
    "chooseMessageFile": ("收集你选中的文件", "strong"),
    # —— 访问你的麦克风 ——
    "startRecord": ("访问你的麦克风", "strong"),
    # —— 访问你的摄像头 ——
    "createVKSession": ("访问你的摄像头", "strong"),
    # —— 使用你的相册（仅写入）权限 ——
    "saveImageToPhotosAlbum": ("使用你的相册（仅写入）权限", "strong"),
    "saveVideoToPhotosAlbum": ("使用你的相册（仅写入）权限", "strong"),
    # —— 读取你的剪切板 ——
    "setClipboardData": ("读取你的剪切板", "strong"),
    "getClipboardData": ("读取你的剪切板", "strong"),
    # —— 收集你的车牌号 ——
    "chooseLicensePlate": ("收集你的车牌号", "strong"),
    # —— 写通讯录 / 日历（仅写入） ——
    "addPhoneContact": ("使用你的通讯录（仅写入）权限", "strong"),
    "addPhoneCalendar": ("使用你的日历（仅写入）权限", "strong"),
    "addPhoneRepeatCalendar": ("使用你的日历（仅写入）权限", "strong"),
    # —— 传感器类 ——
    "startAccelerometer": ("调用你的加速传感器", "strong"),
    "startCompass": ("调用你的磁场传感器", "strong"),
    "startDeviceMotionListening": ("调用你的方向传感器", "strong"),
    "startGyroscope": ("调用你的陀螺仪传感器", "strong"),
}

# 组件/标签型调用（出现在 wxml 中）
#   (编译后的正则, 信息类型, 强度, 说明)
COMPONENT_RULES = [
    (re.compile(r'open-type\s*=\s*"getPhoneNumber"'), "收集你的手机号", "strong", "button getPhoneNumber"),
    (re.compile(r'open-type\s*=\s*"getRealtimePhoneNumber"'), "收集你的手机号", "strong", "button getRealtimePhoneNumber"),
    (re.compile(r'open-type\s*=\s*"chooseAvatar"'), "收集你的昵称、头像", "strong", "button chooseAvatar"),
    (re.compile(r'open-type\s*=\s*"userInfo"'), "收集你的昵称、头像", "gone", "button userInfo（官方已回收）"),
    (re.compile(r'type\s*=\s*"nickname"'), "收集你的昵称、头像", "weak", "input type=nickname"),
    (re.compile(r"<live-pusher"), "访问你的麦克风", "weak", "live-pusher 组件（可能同时涉摄像头）"),
    (re.compile(r"<camera"), "访问你的摄像头", "weak", "camera 组件"),
    (re.compile(r"<voip-room"), "访问你的摄像头", "weak", "voip-room 组件"),
]

# authorize scope → 信息类型
SCOPE_MAP = {
    "scope.userLocation": "收集你的位置信息",
    "scope.userLocationBackground": "收集你的位置信息",
    "scope.userFuzzyLocation": "收集你的位置信息",
    "scope.record": "访问你的麦克风",
    "scope.camera": "访问你的摄像头",
    "scope.writePhotosAlbum": "使用你的相册（仅写入）权限",
    "scope.addPhoneContact": "使用你的通讯录（仅写入）权限",
    "scope.addPhoneCalendar": "使用你的日历（仅写入）权限",
    "scope.werun": "收集你的微信运动步数",
    "scope.bluetooth": "访问你的蓝牙",
}

SCAN_EXT = (".js", ".ts", ".wxml", ".json", ".jsx", ".mjs", ".wxs")

SKIP_DIRS = {
    "node_modules", "miniprogram_npm", "vendor", ".git", "dist", "build",
    "coverage", ".temp", "__pycache__",
}

# 注释剥离：JS 行注释 / 块注释 / HTML 注释
_LINE_COMMENT = re.compile(r"//[^\n]*")
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)

# wx.<api>( 与 .<api>( 两种调用形态
_API_CALL = re.compile(r"(?<![\w.$])(?:wx\.)?([a-z][A-Za-z0-9_]*)\s*\(")
_SCOPE = re.compile(r"scope\s*:\s*['\"]([a-zA-Z.]+)['\"]")


def strip_comments(text, ext):
    if ext in (".js", ".ts", ".jsx", ".mjs", ".wxs"):
        text = _BLOCK_COMMENT.sub(" ", text)
        text = _LINE_COMMENT.sub(" ", text)
    elif ext == ".wxml":
        text = _HTML_COMMENT.sub(" ", text)
    return text


def iter_source_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(SCAN_EXT):
                yield os.path.join(dirpath, name)


def scan(root):
    findings = []
    seen = set()

    for path in iter_source_files(root):
        ext = os.path.splitext(path)[1]
        try:
            with open(path, "r", encoding="utf-8") as fh:
                raw = fh.read()
        except (UnicodeDecodeError, OSError):
            continue
        text = strip_comments(raw, ext)
        rel = os.path.relpath(path, root).replace("\\", "/")
        lines = text.split("\n")

        for api, (info_type, strength) in PRIVACY_API_MAP.items():
            # 必须带 `wx.` 前缀：微信隐私接口在代码里一律写作 wx.<api>。
            # 允许裸函数名会把同名本地函数误报成接口（实测：一个非小程序项目里的
            # `function pickMedia(){ return chooseMedia({...}) }` 被误判为 wx.chooseMedia）。
            # 「误报比漏报更伤」——一个在非小程序项目上满屏假警报的工具会被直接弃用。
            pattern = re.compile(r"(?<![\w.$])wx\.%s\s*\(" % re.escape(api))
            for m in pattern.finditer(text):
                key = (rel, api, info_type)
                if key in seen:
                    continue
                seen.add(key)
                line_no = text.count("\n", 0, m.start()) + 1
                findings.append({
                    "level": "FAIL" if strength in ("strong", "gone") else "WARN",
                    "kind": "api",
                    "symbol": "wx." + api,
                    "info_type": info_type,
                    "strength": strength,
                    "file": rel,
                    "line": line_no,
                    "snippet": lines[line_no - 1].strip()[:160] if line_no <= len(lines) else "",
                })

        if ext in (".wxml", ".js", ".ts", ".jsx", ".mjs"):
            for pattern, info_type, strength, desc in COMPONENT_RULES:
                for m in pattern.finditer(text):
                    key = (rel, desc, info_type)
                    if key in seen:
                        continue
                    seen.add(key)
                    line_no = text.count("\n", 0, m.start()) + 1
                    findings.append({
                        "level": "FAIL" if strength in ("strong", "gone") else "WARN",
                        "kind": "component",
                        "symbol": desc,
                        "info_type": info_type,
                        "strength": strength,
                        "file": rel,
                        "line": line_no,
                        "snippet": lines[line_no - 1].strip()[:160] if line_no <= len(lines) else "",
                    })

        for m in _SCOPE.finditer(text):
            scope = m.group(1)
            info_type = SCOPE_MAP.get(scope)
            if not info_type:
                continue
            key = (rel, scope, info_type)
            if key in seen:
                continue
            seen.add(key)
            line_no = text.count("\n", 0, m.start()) + 1
            findings.append({
                "level": "WARN",
                "kind": "scope",
                "symbol": scope,
                "info_type": info_type,
                "strength": "weak",
                "file": rel,
                "line": line_no,
                "snippet": lines[line_no - 1].strip()[:160] if line_no <= len(lines) else "",
            })

    findings.sort(key=lambda f: (f["level"] != "FAIL", f["file"], f["line"]))
    return findings


def summarize(findings):
    required = {}
    for f in findings:
        if f["level"] != "FAIL":
            continue
        required.setdefault(f["info_type"], [])
        if f["symbol"] not in required[f["info_type"]]:
            required[f["info_type"]].append(f["symbol"])
    return {k: sorted(v) for k, v in sorted(required.items())}


def detect_project_type(root):
    """判定目标是否为微信小程序项目。

    返回 (is_miniprogram, reason)：
      - project.config.json 里 compileType == "miniprogram" → 是
      - 有 app.json + app.js 且 project.config.json 缺失或声明 miniprogram → 是
      - 否则 → 否

    为什么要有这道判定：本 Skill 的映射表与声明格式**只对微信小程序成立**。
    在非小程序项目上强行跑，会输出「必须在《用户隐私保护指引》中声明」这种
    无意义的结论——那是**虚假通用性**：看起来通用，实际换个平台就全错。
    """
    cfg_path = os.path.join(root, "project.config.json")
    if os.path.isfile(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as fh:
                cfg = json.load(fh)
            compile_type = str(cfg.get("compileType", "")).strip()
            if compile_type == "miniprogram":
                return True, "project.config.json 声明 compileType=miniprogram"
            return False, "project.config.json 声明 compileType=%s（非小程序）" % (compile_type or "空")
        except (ValueError, OSError):
            pass
    if os.path.isfile(os.path.join(root, "app.json")) and os.path.isfile(os.path.join(root, "app.js")):
        return True, "存在 app.json + app.js（小程序工程结构）"
    return False, "未检出小程序工程标志（project.config.json 的 compileType=miniprogram，或 app.json + app.js）"


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    if not args:
        print(__doc__)
        return 2

    root = os.path.abspath(args[0])
    if not os.path.isdir(root):
        print("错误：路径不存在或不是目录：%s" % root, file=sys.stderr)
        return 2

    is_mp, mp_reason = detect_project_type(root)

    findings = scan(root)
    required = summarize(findings)
    fail_count = sum(1 for f in findings if f["level"] == "FAIL")
    warn_count = sum(1 for f in findings if f["level"] == "WARN")

    if "--json" in flags:
        print(json.dumps({
            "root": root,
            "is_miniprogram": is_mp,
            "project_type_reason": mp_reason,
            "findings": findings,
            "required_info_types": required,
            "fail_count": fail_count,
            "warn_count": warn_count,
        }, ensure_ascii=False, indent=2))
        return 1 if fail_count else 0

    print("== 项目类型判定 ==")
    print("%s（%s）" % ("微信小程序项目" if is_mp else "非微信小程序项目", mp_reason))
    if not is_mp:
        print("⚠ 本 Skill 的映射表与声明格式只对微信小程序成立。")
        print("  下方结果仅供定位 wx.* 形式的调用点，**不代表该平台需要隐私保护指引**。")

    print()
    print("== 隐私接口调用面 ==")
    if not findings:
        print("未发现隐私相关接口调用。")
    else:
        for f in findings:
            print("[%s] %s → %s" % (f["level"], f["symbol"], f["info_type"]))
            print("      %s:%d" % (f["file"], f["line"]))
            if "--verbose" in flags and f["snippet"]:
                print("      | %s" % f["snippet"])

    print()
    print("== 平台侧必须声明的「处理的信息」清单 ==")
    if not required:
        print("（空）")
    else:
        for info_type, symbols in required.items():
            print("- %s ← %s" % (info_type, ", ".join(symbols)))

    print()
    print("FAIL=%d  WARN=%d" % (fail_count, warn_count))
    if fail_count:
        print("→ 上述 FAIL 项在《用户隐私保护指引》中必须有对应声明，否则提审被拦截。")
    return 1 if fail_count else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
