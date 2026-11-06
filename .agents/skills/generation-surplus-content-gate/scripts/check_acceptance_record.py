#!/usr/bin/env python3
"""验收记录校验器（零第三方依赖）。

契约：
  0  通过
  2  [CHECK-FAILED] 记录不满足验收门
  3  [IO-ERROR]     文件不存在 / JSON 解析失败
  --selftest 走内建正负样本，不读写外部文件，退出 0 表示自检行为符合预期。

退出码刻意不使用 1：Python 未捕获异常固定返回 1，与「契约检出」混淆。
"""

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REQUIRED_STRING_FIELDS = (
    "record_id",
    "artifact",
    "artifact_type",
    "check_method",
    "conclusion",
)
REQUIRED_LIST_FIELDS = (
    "expected",
    "negative_constraints",
    "missing_items",
    "surplus_items",
)
VALID_TYPES = {"bitmap", "text", "code", "data"}
VALID_CONCLUSIONS = {"clean", "surplus_found", "missing_found", "both_found", "not_checked"}


def validate(record):
    """返回问题列表；空列表表示通过。"""
    problems = []

    if not isinstance(record, dict):
        return ["记录根节点必须是 JSON 对象"]

    for field in REQUIRED_STRING_FIELDS:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            problems.append("GSG_REQUIRED: %s 必须是非空字符串" % field)

    for field in REQUIRED_LIST_FIELDS:
        value = record.get(field)
        if not isinstance(value, list):
            problems.append("GSG_REQUIRED: %s 必须是数组" % field)

    artifact_type = record.get("artifact_type")
    if isinstance(artifact_type, str) and artifact_type not in VALID_TYPES:
        problems.append("GSG_TYPE: artifact_type 必须是 %s 之一" % "/".join(sorted(VALID_TYPES)))

    conclusion = record.get("conclusion")
    if isinstance(conclusion, str) and conclusion not in VALID_CONCLUSIONS:
        problems.append("GSG_TYPE: conclusion 必须是 %s 之一" % "/".join(sorted(VALID_CONCLUSIONS)))

    negative = record.get("negative_constraints")
    if isinstance(negative, list) and not negative:
        problems.append("GSG_001: negative_constraints 为空，生成前未建立负向清单")

    applied = record.get("negative_constraints_applied_before_generation")
    if applied is not True:
        problems.append("GSG_001: negative_constraints_applied_before_generation 必须为 true")

    surplus = record.get("surplus_items")
    missing = record.get("missing_items")
    if isinstance(surplus, list) and isinstance(missing, list):
        has_surplus = len(surplus) > 0
        has_missing = len(missing) > 0
        if conclusion == "clean" and (has_surplus or has_missing):
            problems.append("GSG_002: conclusion=clean 与差异项非空矛盾")
        if conclusion == "surplus_found" and not has_surplus:
            problems.append("GSG_002: conclusion=surplus_found 但 surplus_items 为空")
        if conclusion == "missing_found" and not has_missing:
            problems.append("GSG_002: conclusion=missing_found 但 missing_items 为空")

    if isinstance(surplus, list):
        for index, item in enumerate(surplus):
            if not isinstance(item, dict):
                problems.append("GSG_002: surplus_items[%d] 必须是对象" % index)
                continue
            for key in ("item", "location", "evidence"):
                if not isinstance(item.get(key), str) or not item.get(key).strip():
                    problems.append("GSG_002: surplus_items[%d].%s 必须是非空字符串" % (index, key))

    artifact = record.get("artifact")
    if isinstance(artifact, str):
        # 同时覆盖 Windows 反斜杠与正斜杠两种盘符写法，以及 UNC / 协议前缀。
        if re.match(r"^[A-Za-z]:[\\/]", artifact) or artifact.startswith(("/", "\\\\")) or "://" in artifact:
            problems.append("GSG_003: artifact 必须是相对路径，不得含盘符或协议前缀")

    method = record.get("check_method")
    if conclusion == "clean" and isinstance(method, str) and not method.strip():
        problems.append("GSG_004: 结论为 clean 时必须写明检查方式")

    return problems


def _sample():
    return {
        "record_id": "selftest-001",
        "artifact": "assets/poster.png",
        "artifact_type": "bitmap",
        "expected": ["主体：仙女", "橙色主调"],
        "negative_constraints": ["no text", "no watermark"],
        "negative_constraints_applied_before_generation": True,
        "missing_items": [],
        "surplus_items": [],
        "check_method": "目视审 + 负向清单逐项",
        "conclusion": "clean",
    }


def selftest():
    positives = [_sample()]
    positives.append(dict(_sample(), surplus_items=[
        {"item": "标题文字", "location": "左上", "evidence": "目视审"}
    ], conclusion="surplus_found"))

    negatives = [
        ("缺负向清单", dict(_sample(), negative_constraints=[])),
        ("负向清单未在生成前应用",
         dict(_sample(), negative_constraints_applied_before_generation=False)),
        ("结论与差异项矛盾", dict(_sample(), conclusion="clean", surplus_items=[
            {"item": "水印", "location": "右下", "evidence": "目视审"}
        ])),
        ("命中项缺位置", dict(_sample(), surplus_items=[{"item": "文字", "evidence": "目视审"}],
                            conclusion="surplus_found")),
        ("绝对路径", dict(_sample(), artifact="D:/work/poster.png")),
    ]

    failures = []
    for index, sample in enumerate(positives):
        problems = validate(sample)
        if problems:
            failures.append("正样本 %d 被误拦: %s" % (index, problems))
    for label, sample in negatives:
        problems = validate(sample)
        if not problems:
            failures.append("负样本「%s」未被拦下" % label)

    if failures:
        print("[SELFTEST-FAILED] %d 项异常" % len(failures))
        for line in failures:
            print("  - " + line)
        return 2
    print("[SELFTEST-OK] 正样本 %d / 负样本 %d 行为符合契约" % (len(positives), len(negatives)))
    return 0


def main():
    parser = argparse.ArgumentParser(description="校验生成型产物验收记录")
    parser.add_argument("record", nargs="?", help="验收记录 JSON 路径")
    parser.add_argument("--selftest", action="store_true", help="跑内建正负样本自检")
    args = parser.parse_args()

    if args.selftest:
        return selftest()
    if not args.record:
        print("[IO-ERROR] 请提供记录路径，或使用 --selftest")
        return 3

    path = Path(args.record)
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print("[IO-ERROR] 无法读取或解析记录: %s" % exc)
        return 3

    problems = validate(record)
    if problems:
        print("[CHECK-FAILED] %s: %d 项" % (path.name, len(problems)))
        for line in problems:
            print("  - " + line)
        return 2
    print("[CHECK-OK] %s: 验收记录通过" % path.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
