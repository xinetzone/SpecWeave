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
    detect_project_type,
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
    """从声明文本中识别已声明的「处理的信息」类型。"""
    found = set()
    for canonical, aliases in DECL_TYPE_ALIASES.items():
        if any(alias in text for alias in aliases):
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

    # ---- D2：声明面无死项 ----
    extra = sorted(declared - set(required))
    if extra:
        add("D2", "WARN", "声明面存在无调用对应的条目",
            "声明了但代码中未检出对应调用：%s" % "；".join(extra),
            extra)
    else:
        add("D2", "PASS", "声明面无死项", "声明条目与检出调用一致。")

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
