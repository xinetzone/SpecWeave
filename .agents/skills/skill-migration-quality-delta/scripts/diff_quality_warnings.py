#!/usr/bin/env python3
"""对比源根与目标根同名 Skill 的质量门警告集合，判断分差是否由迁入引入。"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RESULT_RE = re.compile(r"\[(PASS|WARN|FAIL)\]\s+([^\s:]+):")
SCORE_RE = re.compile(r"^(.+?):\s*(\d+)$")
WEIGHTS = {"FAIL": 15, "WARN": 5}
BODY_PREFIXES = ("why.", "safety.", "decision.", "trigger.", "open_standard.body.")
STRUCTURE_PREFIXES = ("open_standard.structure.", "open_standard.name.")
STRUCTURE_EXACT = {"open_standard.custom_fields", "open_standard.compliance"}


def classify(name):
    if name.startswith("frontmatter."):
        return "frontmatter"
    if name.startswith("description."):
        return "description"
    if name.startswith(STRUCTURE_PREFIXES) or name in STRUCTURE_EXACT:
        return "structure"
    if name.startswith(BODY_PREFIXES) or name == "file.length":
        return "body"
    return "body"


def find_checker(explicit):
    if explicit:
        return Path(explicit).expanduser()
    env = os.environ.get("SPECWEAVE_CHECKER")
    if env:
        return Path(env).expanduser()
    for base in [Path.cwd().resolve(), *Path.cwd().resolve().parents]:
        candidate = base / ".agents" / "scripts" / "check-skill-quality.py"
        if candidate.is_file():
            return candidate
    return None


def run_checker(checker, target):
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    base = [sys.executable, str(checker), "--path", str(target)]
    verbose = subprocess.run(
        base + ["--verbose"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    score = subprocess.run(
        base + ["--score", "--threshold", "100"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return {
        "verbose_exit": verbose.returncode,
        "score_exit": score.returncode,
        "verbose_text": verbose.stdout + verbose.stderr,
        "score_text": score.stdout + score.stderr,
    }


def parse_failures(text):
    failures = {}
    for line in text.splitlines():
        match = RESULT_RE.search(line)
        if not match:
            continue
        severity, name = match.group(1), match.group(2)
        if severity == "PASS":
            continue
        failures[name] = severity
    return failures


def parse_scores(text):
    scores = []
    for line in text.splitlines():
        match = SCORE_RE.match(line.strip())
        if not match:
            continue
        name = match.group(1).strip()
        if name == "平均":
            continue
        scores.append((name, int(match.group(2))))
    return scores


def diff_sets(source, target):
    introduced, eliminated, preexisting = {}, {}, {}
    for name, severity in target.items():
        if name not in source:
            introduced[name] = {"severity": severity, "previous": None}
        elif source[name] == severity:
            preexisting[name] = severity
        elif WEIGHTS[severity] > WEIGHTS[source[name]]:
            introduced[name] = {"severity": severity, "previous": source[name]}
        else:
            eliminated[name] = {"severity": source[name], "current": severity}
    for name, severity in source.items():
        if name not in target:
            eliminated[name] = {"severity": severity, "current": None}
    return introduced, eliminated, preexisting


def weight(severity):
    return WEIGHTS.get(severity, 0)


def verdict_for(introduced, eliminated):
    if introduced:
        body = [n for n in introduced if classify(n) == "body"]
        return "REGRESSION_BODY" if body else "REGRESSION_META"
    body = [n for n in eliminated if classify(n) == "body"]
    return "DIVERGED_REMEDIATED" if body else "CLEAN"


VERDICT_TEXT = {
    "REGRESSION_BODY": "存在本次引入，且含正文检查项：目标正文已偏离源正文，先做保真比对再归因",
    "REGRESSION_META": "存在本次引入，全部落在元数据面：定位对应 frontmatter 字段或 description 改动",
    "DIVERGED_REMEDIATED": "本次未引入新警告，但已消除项含正文检查：两副本正文已分叉（通常是事后修复），不可称逐字复制",
    "CLEAN": "本次未引入新警告，差项仅落在元数据面：迁入未改变正文质量画像",
}


def build_payload(args, checker, source, target):
    introduced, eliminated, preexisting = diff_sets(source["failures"], target["failures"])
    verdict = verdict_for(introduced, eliminated)
    return {
        "checker": str(checker),
        "source": {
            "path": str(args.source_path),
            "name": source["name"],
            "score": source["score"],
            "verbose_exit": source["verbose_exit"],
            "score_exit": source["score_exit"],
            "warn_count": sum(1 for s in source["failures"].values() if s == "WARN"),
            "fail_count": sum(1 for s in source["failures"].values() if s == "FAIL"),
        },
        "target": {
            "path": str(args.target_path),
            "name": target["name"],
            "score": target["score"],
            "verbose_exit": target["verbose_exit"],
            "score_exit": target["score_exit"],
            "warn_count": sum(1 for s in target["failures"].values() if s == "WARN"),
            "fail_count": sum(1 for s in target["failures"].values() if s == "FAIL"),
        },
        "delta": target["score"] - source["score"],
        "introduced": introduced,
        "eliminated": eliminated,
        "preexisting": preexisting,
        "verdict": verdict,
    }


def render(payload):
    src, dst = payload["source"], payload["target"]
    lines = [
        f"SOURCE  {src['path']}",
        f"  name={src['name']}  score={src['score']}  exit(verbose)={src['verbose_exit']}  exit(score)={src['score_exit']}",
        f"  failed={src['warn_count'] + src['fail_count']} (WARN {src['warn_count']} / FAIL {src['fail_count']})",
        f"TARGET  {dst['path']}",
        f"  name={dst['name']}  score={dst['score']}  exit(verbose)={dst['verbose_exit']}  exit(score)={dst['score_exit']}",
        f"  failed={dst['warn_count'] + dst['fail_count']} (WARN {dst['warn_count']} / FAIL {dst['fail_count']})",
        f"DELTA   {payload['delta']:+d}",
        "",
        f"INTRODUCED ({len(payload['introduced'])})",
    ]
    if payload["introduced"]:
        for name, meta in sorted(payload["introduced"].items()):
            was = f" (was {meta['previous']})" if meta["previous"] else ""
            lines.append(
                f"  {name:<40} {meta['severity']:<4} {-weight(meta['severity']):+d}  {classify(name)}{was}"
            )
    else:
        lines.append("  (none)")
    lines.append(f"ELIMINATED ({len(payload['eliminated'])})")
    if payload["eliminated"]:
        for name, meta in sorted(payload["eliminated"].items()):
            now = f" (now {meta['current']})" if meta["current"] else ""
            lines.append(
                f"  {name:<40} {meta['severity']:<4} {weight(meta['severity']):+d}  {classify(name)}{now}"
            )
    else:
        lines.append("  (none)")
    lines.append(f"PREEXISTING ({len(payload['preexisting'])})")
    if payload["preexisting"]:
        for name, severity in sorted(payload["preexisting"].items()):
            lines.append(f"  {name:<40} {severity}")
    else:
        lines.append("  (none)")
    lines += [
        "",
        f"RECONCILE  source {payload['source']['score']} / target {payload['target']['score']}（两次均按 100−5×WARN−15×FAIL 对账通过）",
        f"VERDICT    {payload['verdict']}  {VERDICT_TEXT[payload['verdict']]}",
        "",
        "三段式陈述",
        f"  本次引入 {len(payload['introduced'])} 项",
        f"  已消除 {len(payload['eliminated'])} 项",
        f"  既有缺口 {len(payload['preexisting'])} 项",
    ]
    return "\n".join(lines)


class SideError(Exception):
    def __init__(self, message, code=1):
        super().__init__(message)
        self.code = code


def load_side(label, raw, checker):
    path = Path(raw).expanduser().resolve()
    if not (path / "SKILL.md").is_file():
        raise SideError(f"ERROR: {label} 路径不含 SKILL.md: {path}")
    output = run_checker(checker, path)
    failures = parse_failures(output["verbose_text"])
    scores = parse_scores(output["score_text"])
    if len(scores) != 1:
        raise SideError(f"ERROR: {label} 扫描到 {len(scores)} 份 SKILL.md，请传入单个 Skill 目录: {path}")
    name, score = scores[0]
    expected = max(0, 100 - sum(weight(s) for s in failures.values()))
    if expected != score:
        raise SideError(
            f"ERROR: {label} 对账失败：理论 {expected} 实际 {score}；清单可能漏项，先按 Gotchas 重解析",
            code=3,
        )
    return {
        "name": name,
        "score": score,
        "failures": failures,
        "verbose_exit": output["verbose_exit"],
        "score_exit": output["score_exit"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="对比两个根的同名 Skill 质量门警告集合，判断分差是否由迁入引入"
    )
    parser.add_argument("--source", required=True, help="源 Skill 目录（含 SKILL.md）")
    parser.add_argument("--target", required=True, help="目标 Skill 目录（含 SKILL.md）")
    parser.add_argument("--checker", help="check-skill-quality.py 路径，缺省时向上查找")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    checker = find_checker(args.checker)
    if checker is None or not checker.is_file():
        print(
            "ERROR: 未找到 check-skill-quality.py；用 --checker 或 SPECWEAVE_CHECKER 指定",
            file=sys.stderr,
        )
        return 1

    args.source_path = Path(args.source).expanduser().resolve()
    args.target_path = Path(args.target).expanduser().resolve()
    try:
        source = load_side("source", args.source, checker)
        target = load_side("target", args.target, checker)
    except SideError as exc:
        print(str(exc), file=sys.stderr)
        return exc.code
    payload = build_payload(args, checker, source, target)

    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else render(payload))
    return 0 if payload["verdict"] in ("CLEAN", "DIVERGED_REMEDIATED") else 2


if __name__ == "__main__":
    sys.exit(main())
