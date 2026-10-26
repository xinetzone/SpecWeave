#!/usr/bin/env python3
"""平台提审合规预检 · 声明面 / 调用面 对账断言器。

平台的提审拦截规则是**逐项比对**：
    代码调用的隐私接口所对应的「处理的信息」类型
    ⊆ 已填写的《用户隐私保护指引》所声明的类型
任一类型缺失即拦截。

本脚本把这个比对固化成可回归的不变量：
    D1  声明面覆盖调用面        —— 代码调了但协议没声明 → 必被拦截
    D2  声明面无死项            —— 声明了但代码没调 → 多余声明（不拦截但会被追问）
    D3  隐私接口有授权兜底      —— 调用点无 onNeedPrivacyAuthorization/requirePrivacyAuthorize 兜底
    D4  平台侧声明文件存在且非空 —— 协议正文缺失 → 提审入口2 直接拦截

用法：
    python check_declaration_alignment.py <项目根目录> [--declaration <声明文件>]
                                       [--json] [--only D1,D2]

退出码：0 = 无 FAIL；1 = 存在 FAIL；2 = 用法错误。
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from scan_privacy_calls import (  # noqa: E402
    PRIVACY_API_MAP, COMPONENT_RULES, SCOPE_MAP, scan, summarize, iter_source_files,
    detect_project_type, strip_comments,
)

SKIP_DIRS = {"node_modules", "miniprogram_npm", "vendor", ".git", "dist", "build", "coverage", ".temp"}

# 平台侧《用户隐私保护指引》可能的落地形态：
#   1) 仓库内的声明草稿（md/txt/json），供人工誊到 mp 后台
#   2) mp 后台导出（txt）
DECL_SUFFIX = (".md", ".txt", ".json")

# 声明文件中「处理的信息」类型的识别特征
DECL_TYPE_ALIASES = {
    "收集你选中的照片或视频信息": ["选中的照片或视频", "选中的照片", "选中的视频"],
    "收集你的昵称、头像": ["昵称", "头像", "用户信息"],
    "收集你的手机号": ["手机号"],
    "收集你的位置信息": ["位置信息", "地理位置"],
    "收集你选择的位置信息": ["选择的位置", "选择的地址位置"],
    "收集你的地址": ["地址", "收货地址"],
    "收集你的发票信息": ["发票"],
    "收集你的微信运动步数": ["运动步数", "微信运动"],
    "收集你选中的文件": ["选中的文件", "选择的文件"],
    "访问你的麦克风": ["麦克风", "录音"],
    "访问你的摄像头": ["摄像头"],
    "使用你的相册（仅写入）权限": ["相册（仅写入）", "相册(仅写入)", "相册"],
    "使用你的通讯录（仅写入）权限": ["通讯录"],
    "使用你的日历（仅写入）权限": ["日历"],
    "读取你的剪切板": ["剪切板", "剪贴板"],
    "收集你的车牌号": ["车牌号"],
    "访问你的蓝牙": ["蓝牙"],
}

AUTH_HOOK_NAMES = ("onNeedPrivacyAuthorization", "requirePrivacyAuthorize", "getPrivacySetting")


def find_declaration_files(root):
    """寻找平台侧声明草稿：优先 README 里的《用户隐私保护指引》章节，其次独立文件。"""
    candidates = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(DECL_SUFFIX):
                continue
            path = os.path.join(dirpath, name)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    text = fh.read()
            except (UnicodeDecodeError, OSError):
                continue
            if "隐私保护指引" in text or "隐私保护指引" in name:
                candidates.append((os.path.relpath(path, root).replace("\\", "/"), text))
    return candidates


def declared_types(text):
    """从声明文本中识别已声明的「处理的信息」类型。

    ⚠️ 只解析**声明条目行**，不做全文子串匹配。
    实测教训：对全文匹配时，说明性文字会误命中别名——
    协议里写「本指引不声明收集你的手机号」「服务内容声明」都会让
    别名「手机号」「地址」被当成已声明，进而把 D1/D2 判反。
    声明条目行的特征：以 `- ` 开头（列表项）或落在「开发者处理的信息」章节内。
    """
    lines = text.split("\n")
    in_section = False
    entry_text = []
    for raw in lines:
        line = raw.strip()
        # 进入「开发者处理的信息」章节
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
            in_section = ("处理的信息" in heading or "开发者处理" in heading)
            continue
        if not in_section:
            continue
        # 章节内的列表项 = 声明条目
        if line.startswith("- ") or line.startswith("* "):
            entry_text.append(line)

    # 若未识别到章节，退回全文里的一级列表项（兜底）
    if not entry_text:
        entry_text = [l.strip() for l in lines if l.strip().startswith("- ")]

    scope = "\n".join(entry_text)
    found = set()
    for canonical, aliases in DECL_TYPE_ALIASES.items():
        if any(alias in scope for alias in aliases):
            found.add(canonical)
    return found


def find_auth_hooks(root):
    """定位所有出现授权钩子的文件（用于 D3 的覆盖判断）。"""
    hooked = set()
    for path in iter_source_files(root):
        ext = os.path.splitext(path)[1]
        if ext not in (".js", ".ts", ".jsx", ".mjs"):
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                text = fh.read()
        except (UnicodeDecodeError, OSError):
            continue
        if any(name in text for name in AUTH_HOOK_NAMES):
            hooked.add(os.path.relpath(path, root).replace("\\", "/"))
    return hooked


# 「处理的信息类型」→ 该类型对应的采集接口/组件名单。
# 用于判定：声明了这一类型，但代码里是否存在**任何**采集路径。
# 取自微信官方《小程序用户隐私保护指引内容介绍》的接口↔类型对应关系。
COLLECTION_PATHS = {
    "收集你的昵称、头像": ["getUserProfile", "getUserInfo", "chooseAvatar", "nickname", "userInfo"],
    "收集你的手机号": ["getPhoneNumber", "getRealtimePhoneNumber"],
    "收集你的位置信息": ["getLocation", "startLocationUpdate", "getFuzzyLocation",
                        "userLocation", "userFuzzyLocation", "userLocationBackground",
                        "moveToLocation"],
    "收集你选择的位置信息": ["choosePoi", "chooseLocation"],
    "收集你的地址": ["chooseAddress"],
    "收集你的发票信息": ["chooseInvoiceTitle", "chooseInvoice"],
    "收集你的微信运动步数": ["getWeRunData", "werun"],
    "收集你的车牌号": ["chooseLicensePlate"],
    "收集你选中的照片或视频信息": ["chooseImage", "chooseMedia", "chooseVideo"],
    "收集你选中的文件": ["chooseMessageFile"],
    "访问你的麦克风": ["startRecord", "scope.record", "RecorderManager", "live-pusher",
                       "joinVoIPChat"],
    "访问你的摄像头": ["createVKSession", "scope.camera", "camera", "live-pusher", "voip-room"],
    "访问你的蓝牙": ["openBluetoothAdapter", "createBLEPeripheralServer", "scope.bluetooth"],
    "使用你的相册（仅写入）权限": ["saveImageToPhotosAlbum", "saveVideoToPhotosAlbum",
                                  "writePhotosAlbum"],
    "使用你的通讯录（仅写入）权限": ["addPhoneContact", "scope.addPhoneContact"],
    "使用你的日历（仅写入）权限": ["addPhoneCalendar", "addPhoneRepeatCalendar",
                                 "scope.addPhoneCalendar"],
    "读取你的剪切板": ["setClipboardData", "getClipboardData"],
    "调用你的加速传感器": ["startAccelerometer"],
    "调用你的磁场传感器": ["startCompass"],
    "调用你的方向传感器": ["startDeviceMotionListening"],
    "调用你的陀螺仪传感器": ["startGyroscope"],
}


def has_collection_path(root, info_type):
    """判定该「处理的信息」类型在代码里是否存在任何采集接口/组件调用。

    扫描范围覆盖 .js/.ts/.wxml/.json（组件型调用如 open-type="getPhoneNumber"
    只出现在 wxml 里），但**排除注释**——注释里的接口名不算采集路径。

    ⚠️ 必须排除**测试文件**与**声明文档本身**：
    实测教训——测试里的正则 `/getPhoneNumber|getRealtimePhoneNumber/.test(code)`
    与协议文档里「代码中不存在 wx.getPhoneNumber 调用」的说明文字，
    都会被当成真实采集路径，导致超范围承诺判不出来（误判方向相反，同样致命）。
    """
    paths = COLLECTION_PATHS.get(info_type)
    if not paths:
        # 映射表未收录的类型：不做判定（交人工），避免误判。
        return True

    for path in iter_source_files(root):
        rel = os.path.relpath(path, root).replace("\\", "/")
        # 排除测试与声明文档
        if "/tests/" in "/" + rel or rel.startswith("tests/"):
            continue
        if "/test/" in "/" + rel:
            continue
        base = os.path.basename(rel)
        if base.endswith(".test.js") or base.endswith(".spec.js") or base.endswith("_test.py"):
            continue
        if "privacy-declaration" in rel or "privacy.json" in rel:
            continue
        ext = os.path.splitext(path)[1]
        if ext not in (".js", ".ts", ".jsx", ".mjs", ".wxml", ".json"):
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                text = fh.read()
        except (UnicodeDecodeError, OSError):
            continue
        text = strip_comments(text, ext)
        for token in paths:
            if token in text:
                return True
    return False


def check(root, declaration_path=None, only=None):
    results = []

    def add(gate, level, title, detail, evidence=None):
        if only and gate not in only:
            return
        results.append({
            "gate": gate, "level": level, "title": title,
            "detail": detail, "evidence": evidence or [],
        })

    # ---- D0：项目类型适用性 ----
    # 映射表与声明格式只对微信小程序成立。在非小程序项目上输出
    # 「必须在《用户隐私保护指引》中声明」是虚假通用性——换个平台就全错。
    is_mp, mp_reason = detect_project_type(root)
    if not is_mp:
        add("D0", "FAIL", "目标不是微信小程序项目",
            "本 Skill 的接口映射表与《用户隐私保护指引》声明格式只对微信小程序成立。"
            "判定依据：%s。请改用对应平台的合规检查手段，"
            "或先确认目标工程确实是小程序。" % mp_reason)
        return results, {}, set(), []

    add("D0", "PASS", "目标为微信小程序项目", mp_reason)

    findings = scan(root)
    required = summarize(findings)

    # ---- D4：平台侧声明文件存在且非空 ----
    decl_text = ""
    decl_files = []
    if declaration_path:
        if os.path.isfile(declaration_path):
            with open(declaration_path, "r", encoding="utf-8") as fh:
                decl_text = fh.read()
            decl_files = [os.path.relpath(declaration_path, root).replace("\\", "/")]
        else:
            add("D4", "FAIL", "声明文件不存在",
                "指定的声明文件不存在：%s" % declaration_path)
    else:
        candidates = find_declaration_files(root)
        if not candidates:
            add("D4", "FAIL", "缺少平台侧声明文件",
                "仓库内未找到《用户隐私保护指引》声明草稿。"
                "提审入口2（管理-版本管理-提交代码审核-信息填写页面）需要填写协议内容，"
                "空协议或缺项会被直接拦截。",
                ["建议新建 docs/privacy-declaration.md 或在 README 增设该章节"])
        else:
            # 取内容最长者作为主声明
            decl_files = [p for p, _ in candidates]
            decl_text = max((t for _, t in candidates), key=len)
            if not decl_text.strip():
                add("D4", "FAIL", "声明文件为空", "声明文件内容为空。", decl_files)
            else:
                add("D4", "PASS", "平台侧声明文件存在",
                    "声明文件：%s" % ", ".join(decl_files), decl_files)

    declared = declared_types(decl_text)

    # ---- D1：声明面覆盖调用面 ----
    missing = sorted(set(required) - declared)
    if missing:
        add("D1", "FAIL", "声明面未覆盖调用面",
            "代码调用了以下隐私接口，但《用户隐私保护指引》缺少对应声明：%s" % "；".join(missing),
            ["%s ← %s" % (t, ", ".join(required[t])) for t in missing])
    elif required:
        add("D1", "PASS", "声明面覆盖调用面",
            "调用面 %d 类信息全部已在声明中出现。" % len(required),
            ["%s ← %s" % (t, ", ".join(required[t])) for t in sorted(required)])
    else:
        add("D1", "PASS", "声明面覆盖调用面", "未检出隐私接口调用，无需声明。")

    # ---- D2：声明面无死项 / 无超范围承诺 ----
    # 「声明了但代码里没检出对应调用」有两种截然不同的性质，必须分开：
    #   (a) 死项：调用存在但静态分析看不到（如 SDK 内部、云函数内）→ WARN，人工确认即可；
    #   (b) 超范围承诺：代码里**根本不存在**该采集路径 → 对用户做了无实际依据的
    #       个人信息处理承诺，平台审核会追问，且构成不必要的承诺 → 独立 FAIL 级提示。
    # 实证：某项目协议里声明「收集你的昵称、头像」「收集你的手机号」，
    # 而代码中不存在 getUserProfile / getPhoneNumber 任一调用——属 (b)。
    extra = sorted(declared - set(required))
    overclaim = []
    dead_items = []
    for info_type in extra:
        if has_collection_path(root, info_type):
            dead_items.append(info_type)
        else:
            overclaim.append(info_type)

    if overclaim:
        add("D2", "FAIL", "声明存在超范围承诺（无实际采集路径）",
            "以下类型在声明中出现，但代码中不存在任何对应的采集接口调用——"
            "属于对用户做了无实际依据的个人信息处理承诺，平台审核会追问，"
            "且构成不必要的承诺。请核实：若确无该采集路径，应从声明中移除；"
            "若有（藏在 SDK 内部或云函数里），请在声明中说明采集途径：%s"
            % "；".join(overclaim),
            overclaim)
    if dead_items:
        add("D2", "WARN", "声明面存在无调用对应的条目",
            "声明了但静态分析未检出对应调用（可能由 SDK 内部或云函数完成，需人工确认）：%s"
            % "；".join(dead_items),
            dead_items)
    if not overclaim and not dead_items:
        add("D2", "PASS", "声明面无死项且无超范围承诺", "声明条目与检出调用一致。")

    # ---- D3：隐私接口有授权兜底 ----
    hooked = find_auth_hooks(root)
    strong_files = sorted({f["file"] for f in findings if f["level"] == "FAIL" and f["kind"] == "api"})
    if strong_files and not hooked:
        add("D3", "FAIL", "隐私接口调用缺少授权兜底",
            "检出隐私接口调用（%s），但全仓未发现 onNeedPrivacyAuthorization / "
            "requirePrivacyAuthorize / getPrivacySetting 任一授权钩子。"
            "自 2023-09-15 起隐私接口默认受管控，未接钩子时真机调用会静默失败。" % ", ".join(strong_files),
            strong_files)
    elif strong_files:
        add("D3", "PASS", "隐私接口调用存在授权兜底",
            "授权钩子位于：%s" % ", ".join(sorted(hooked)), sorted(hooked))
    else:
        add("D3", "PASS", "无需授权兜底", "未检出强隐私接口调用。")

    return results, required, declared, findings


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    decl = None
    only = None
    for i, a in enumerate(argv):
        if a == "--declaration" and i + 1 < len(argv):
            decl = argv[i + 1]
        if a == "--only" and i + 1 < len(argv):
            only = set(x.strip() for x in argv[i + 1].split(","))
    if not args:
        print(__doc__)
        return 2
    root = os.path.abspath(args[0])
    if not os.path.isdir(root):
        print("错误：路径不存在或不是目录：%s" % root, file=sys.stderr)
        return 2

    results, required, declared, _ = check(root, decl, only)

    if "--json" in flags:
        print(json.dumps({
            "root": root, "results": results,
            "required": required, "declared": sorted(declared),
        }, ensure_ascii=False, indent=2))
        return 1 if any(r["level"] == "FAIL" for r in results) else 0

    print("== 声明面 / 调用面 对账 ==")
    for r in results:
        print("[%s] %s（%s）" % (r["level"], r["title"], r["gate"]))
        print("      %s" % r["detail"])
        for e in r["evidence"][:8]:
            print("      - %s" % e)

    fail = sum(1 for r in results if r["level"] == "FAIL")
    warn = sum(1 for r in results if r["level"] == "WARN")
    print()
    print("FAIL=%d  WARN=%d" % (fail, warn))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
