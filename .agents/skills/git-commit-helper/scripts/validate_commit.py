#!/usr/bin/env python3
"""
Git Commit Message Validator — 符合 Conventional Commits 规范的提交信息验证器

遵循 PEP 723 内联脚本元数据格式，使用 uv run 或 pipx run 可直接运行无需预安装依赖。

用法:
    python validate_commit.py "feat(auth): 添加JWT刷新"
    python validate_commit.py --dry-run
    uv run validate_commit.py "fix(login): 修复跳转问题 [prevent: test-case]"
"""

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

COMMIT_TYPES = {
    "feat", "fix", "docs", "style", "refactor",
    "perf", "test", "chore", "ci", "revert", "build",
}

TRIVIAL_FIX_KEYWORDS = [
    "拼写", "错字", "typo", "格式", "format", "注释", "comment",
    "清理", "cleanup", "临时文件", "temp", "空格", "whitespace",
    "标点", "punctuation", "换行", "newline",
]

PREVENT_PATTERN = re.compile(r"\[prevent:\s*([a-z\-]+)\]")
ISSUE_REF_PATTERN = re.compile(r"#\d+")

COMMIT_PATTERN = re.compile(
    r"^(?P<type>[a-z]+)"
    r"(?:\((?P<scope>[a-z0-9\-/]+)\))?"
    r"(?P<breaking>!)?"
    r":\s+"
    r"(?P<subject>.+)$"
)


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]
    commit_type: str | None
    scope: str | None
    subject: str | None
    is_breaking: bool


def validate_message(message: str) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    message = message.strip()

    if not message:
        return ValidationResult(
            valid=False,
            errors=["提交信息为空"],
            warnings=[],
            commit_type=None,
            scope=None,
            subject=None,
            is_breaking=False,
        )

    first_line = message.split("\n")[0]
    match = COMMIT_PATTERN.match(first_line)

    if not match:
        errors.append(
            f"格式错误，期望: <type>(<scope>): <subject>，实际: {first_line[:80]}"
        )
        return ValidationResult(
            valid=False,
            errors=errors,
            warnings=warnings,
            commit_type=None,
            scope=None,
            subject=None,
            is_breaking=False,
        )

    commit_type = match.group("type")
    scope = match.group("scope")
    is_breaking = match.group("breaking") == "!"
    subject = match.group("subject")

    if commit_type not in COMMIT_TYPES:
        errors.append(
            f"未知的type: '{commit_type}'，允许的type: {', '.join(sorted(COMMIT_TYPES))}"
        )

    if subject:
        if len(subject) > 50:
            warnings.append(f"subject长度{len(subject)}字符，建议≤50字符")
        if subject.endswith(("。", ".", "！", "!")):
            warnings.append("subject不应以句号/感叹号结尾")
        if re.match(r"^(修复|添加|更新|删除|重构|优化|实现|修改|调整|迁移|整合|替换|移除|新增|改进|完善|解决|处理|支持|升级|降级|合并|拆分|重命名|补充|简化|增强|清理|恢复|回滚)[了过]", subject):
            warnings.append("subject建议使用祈使句（'修复xx'而非'修复了xx'）")

    if scope and len(scope) > 20:
        warnings.append(f"scope长度{len(scope)}字符，建议≤20字符")

    if is_breaking:
        warnings.append("检测到破坏性变更标记(!)，请确保在正文中包含BREAKING CHANGE说明")

    lines = message.split("\n")
    if len(lines) > 1 and lines[1] != "":
        errors.append("subject与正文之间必须空一行")

    if commit_type == "fix":
        has_prevent = PREVENT_PATTERN.search(message) is not None
        has_issue_ref = ISSUE_REF_PATTERN.search(message) is not None
        is_trivial = False
        if subject:
            subject_lower = subject.lower()
            is_trivial = any(kw.lower() in subject_lower for kw in TRIVIAL_FIX_KEYWORDS)
        if not has_prevent and not has_issue_ref and not is_trivial:
            warnings.append(
                "fix类型提交建议在正文中注明预防措施（如[prevent: test-case]、[prevent: check-script]、[prevent: rule-update]），"
                "或引用跟踪Issue（#NNN）；平凡修复（拼写/格式/注释/清理）可使用[prevent: trivial-exempt]标记"
            )
        if has_prevent:
            prevent_match = PREVENT_PATTERN.search(message)
            prevent_type = prevent_match.group(1) if prevent_match else None
            valid_prevent_types = {"test-case", "check-script", "rule-update", "anti-pattern", "architecture", "trivial-exempt"}
            if prevent_type and prevent_type not in valid_prevent_types:
                warnings.append(
                    f"未知的prevent类型: '{prevent_type}'，允许的类型: {', '.join(sorted(valid_prevent_types))}"
                )

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        commit_type=commit_type,
        scope=scope,
        subject=subject,
        is_breaking=is_breaking,
    )


def analyze_changes() -> dict:
    try:
        status = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True, text=True, check=True,
        )
        staged = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            capture_output=True, text=True, check=True,
        )
        unstaged = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True, text=True, check=True,
        )
        recent = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True, text=True, check=True,
        )
        return {
            "status": status.stdout.strip(),
            "staged_files": [f for f in staged.stdout.strip().split("\n") if f],
            "unstaged_files": [f for f in unstaged.stdout.strip().split("\n") if f],
            "recent_commits": recent.stdout.strip(),
        }
    except subprocess.CalledProcessError:
        return {"error": "无法获取git状态，请确保在git仓库中运行"}


def suggest_type(files: list[str]) -> str:
    type_scores: dict[str, int] = {t: 0 for t in sorted(COMMIT_TYPES)}

    patterns = {
        "feat": [r"feature", r"(?<![a-z])new(?![a-z])", r"(?<![a-z])add(?![a-z])", r"(?<![a-z])create(?![a-z])"],
        "fix": [r"bugfix", r"hotfix", r"(?<![a-z])fix(?![a-z])", r"(?<![a-z])bug(?![a-z])", r"(?<![a-z])error(?![a-z])", r"(?<![a-z])crash(?![a-z])", r"(?<![a-z])issue(?![a-z])", r"(?<![a-z])patch(?![a-z])"],
        "docs": [r"\.md$", r"readme", r"(?<![a-z])doc(?![a-z])", r"comment"],
        "test": [r"test", r"spec", r"\.test\.", r"_test\."],
        "refactor": [r"refactor", r"rename", r"(?<![a-z])move(?![a-z])", r"restructure"],
        "perf": [r"(?<![a-z])perf(?![a-z])", r"optim", r"(?<![a-z])cache(?![a-z])", r"(?<![a-z])speed(?![a-z])"],
        "style": [r"style", r"format", r"(?<![a-z])lint(?![a-z])", r"whitespace", r"prettier"],
        "chore": [r"package\.json", r"requirements", r"(?<![a-z])deps(?![a-z])", r"(?:^|[/\\])config(?:[/\\.]|$)", r"\.toml$"],
        "ci": [r"\.github[/\\]workflows", r"circleci", r"jenkinsfile", r"\.gitlab-ci"],
        "build": [r"webpack", r"rollup", r"vite\.config", r"tsconfig", r"makefile", r"dockerfile"],
        "revert": [r"revert"],
    }

    for f in files:
        f_lower = f.lower().replace("\\", "/")
        for t, pats in patterns.items():
            for p in pats:
                if re.search(p, f_lower):
                    type_scores[t] += 1

    if all(v == 0 for v in type_scores.values()):
        return "chore"

    max_score = max(type_scores.values())
    candidates = [t for t, s in type_scores.items() if s == max_score]
    if len(candidates) == 1:
        return candidates[0]

    priority = ["ci", "build", "test", "docs", "style", "perf", "refactor", "revert", "feat", "fix", "chore"]
    for p in priority:
        if p in candidates:
            return p
    return candidates[0]


def suggest_scope(files: list[str]) -> str | None:
    if not files:
        return None
    parts = Path(files[0]).parts
    if len(parts) >= 2:
        return parts[0]
    return None


def print_result(result: ValidationResult):
    if result.valid:
        print("✅ 提交信息格式验证通过")
    else:
        print("❌ 提交信息格式验证失败:")
        for e in result.errors:
            print(f"   错误: {e}")

    if result.warnings:
        print("⚠️  警告:")
        for w in result.warnings:
            print(f"   注意: {w}")

    if result.commit_type:
        print(f"\n📋 解析结果:")
        print(f"   Type:    {result.commit_type}")
        print(f"   Scope:   {result.scope or '(无)'}")
        print(f"   Subject: {result.subject}")
        print(f"   Breaking: {'是 ⚠️' if result.is_breaking else '否'}")


def main():
    parser = argparse.ArgumentParser(
        description="验证Git提交信息是否符合Conventional Commits规范"
    )
    parser.add_argument(
        "message", nargs="?", help="要验证的提交信息"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="分析当前暂存区变更，建议commit type和scope"
    )
    args = parser.parse_args()

    if args.dry_run:
        info = analyze_changes()
        if "error" in info:
            print(f"❌ {info['error']}")
            sys.exit(1)

        print("📊 三查暂存法 - 当前变更分析\n")

        print("【工作区状态】")
        print(info["status"] if info["status"] else "（干净）")

        print(f"\n【已暂存文件】({len(info['staged_files'])}个)")
        for f in info["staged_files"]:
            print(f"  {f}")

        print(f"\n【未暂存文件】({len(info['unstaged_files'])}个)")
        for f in info["unstaged_files"]:
            print(f"  {f}")

        print("\n【最近5条提交】")
        print(info["recent_commits"])

        if info["staged_files"]:
            suggested_type = suggest_type(info["staged_files"])
            suggested_scope = suggest_scope(info["staged_files"])
            print(f"\n💡 建议: type={suggested_type}" + (f", scope={suggested_scope}" if suggested_scope else ""))
        return

    if not args.message:
        parser.print_help()
        sys.exit(1)

    result = validate_message(args.message)
    print_result(result)
    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
