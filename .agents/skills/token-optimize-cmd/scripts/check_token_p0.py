#!/usr/bin/env python3
"""
Token优化P0禁令预检工具 — 自动化检查S0阶段P0级前置条件

在给出Token优化方案前，用此脚本检查关键前置条件是否满足，
避免违反C-003（无可观测性）和C-024（无质量基线）等阻断性禁令。

遵循 PEP 723 内联脚本元数据格式，使用 uv run 或 python 直接运行。

用法:
    python check_token_p0.py
    python check_token_p0.py --target /path/to/project
    python check_token_p0.py --json
"""

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


# P0级禁令定义
P0_CONSTRAINTS = {
    "C-001": {
        "name": "质量底线约束",
        "description": "禁止为省token牺牲不可接受的质量",
        "check_type": "manual",
        "severity": "blocking",
    },
    "C-002": {
        "name": "推理引擎约束",
        "description": "禁止裸用Transformers Pipeline部署生产服务",
        "check_type": "code_scan",
        "severity": "blocking",
    },
    "C-003": {
        "name": "可观测性约束",
        "description": "禁止不做可观测性就开始优化",
        "check_type": "config_scan",
        "severity": "blocking",
    },
    "C-007": {
        "name": "语义缓存阈值约束",
        "description": "禁止语义缓存相似度阈值设置过低(<0.9)",
        "check_type": "config_scan",
        "severity": "blocking",
    },
    "C-012": {
        "name": "输出限制约束",
        "description": "禁止不设max_tokens限制",
        "check_type": "code_scan",
        "severity": "blocking",
    },
    "C-020": {
        "name": "灰度发布约束",
        "description": "禁止全量上线优化而不做灰度/A/B测试",
        "check_type": "manual",
        "severity": "blocking",
    },
    "C-024": {
        "name": "质量基线约束",
        "description": "禁止在没有质量基线的情况下做优化",
        "check_type": "config_scan",
        "severity": "blocking",
    },
}

# 可观测性工具关键词
OBSERVABILITY_TOOLS = [
    "helicone", "langfuse", "portkey", "langsmith", "promptlayer",
    "traceloop", "arize", "phoenix", "wandb", "mlflow",
    "openmeter", "lunary", "braintrust",
]

# vLLM关键词
VLLM_PATTERNS = [
    r"from\s+vllm",
    r"import\s+vllm",
    r"VLLM",
    r"vllm\.",
    r"AsyncLLMEngine",
    r"LLMEngine",
]

# Transformers Pipeline危险模式
PIPELINE_PRODUCTION_PATTERNS = [
    r"from\s+transformers\s+import\s+pipeline",
    r"transformers\.pipeline",
    r"pipeline\(\s*['\"]text-generation",
]

# max_tokens模式
MAX_TOKENS_PATTERNS = [
    r"max_tokens\s*=",
    r"max_new_tokens\s*=",
    r"max_completion_tokens\s*=",
    r"max_output_tokens\s*=",
]

# 语义缓存阈值模式（通用threshold模式使用lookbehind避免匹配similarity_threshold等复合名）
SEMANTIC_CACHE_THRESHOLD_PATTERNS = [
    (r"similarity_threshold\s*=\s*([0-9.]+)", "similarity_threshold"),
    (r"score_threshold\s*=\s*([0-9.]+)", "score_threshold"),
    (r"cosine_threshold\s*=\s*([0-9.]+)", "cosine_threshold"),
    (r"min_similarity\s*=\s*([0-9.]+)", "min_similarity"),
    (r"(?<![a-zA-Z_])threshold\s*=\s*([0-9.]+)", "threshold"),
]

# 黄金测试集/质量基线文件线索
GOLDEN_SET_PATTERNS = [
    "golden", "golden_set", "test_set", "eval_set", "benchmark",
    "quality_baseline", "baseline", "ground_truth", "reference",
    "eval_data", "test_data",
]

# 灰度/A/B测试线索
CANARY_PATTERNS = [
    "canary", "gray_release", "grey_release", "a_b_test", "ab_test",
    "rollout", "gradual_release", "feature_flag", "staged_rollout",
    "shadow", "dark_launch",
]


@dataclass
class CheckItemResult:
    """单个检查项结果。"""

    constraint_id: str
    name: str
    passed: bool
    severity: str
    evidence: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: str = ""


@dataclass
class P0CheckResult:
    """P0预检汇总结果。"""

    target_path: str
    passed: bool
    blocking_count: int
    warning_count: int
    manual_checks_needed: list[str] = field(default_factory=list)
    items: list[CheckItemResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "target_path": self.target_path,
            "passed": self.passed,
            "blocking_count": self.blocking_count,
            "warning_count": self.warning_count,
            "manual_checks_needed": self.manual_checks_needed,
            "items": [asdict(item) for item in self.items],
        }


def scan_file_content(path: Path, patterns: list[str]) -> list[tuple[int, str]]:
    """扫描文件内容匹配正则模式，返回匹配的行号和行内容。"""
    matches = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        for i, line in enumerate(content.splitlines(), 1):
            for pat in patterns:
                if re.search(pat, line, re.IGNORECASE):
                    matches.append((i, line.strip()))
                    break
    except (OSError, UnicodeDecodeError):
        pass
    return matches


def extract_threshold_value(content: str, patterns: list[tuple[str, str]]) -> list[tuple[str, float, int]]:
    """从内容中提取阈值数值。"""
    results = []
    for i, line in enumerate(content.splitlines(), 1):
        for pat, name in patterns:
            m = re.search(pat, line, re.IGNORECASE)
            if m:
                try:
                    val = float(m.group(1))
                    results.append((name, val, i))
                except (ValueError, IndexError):
                    pass
    return results


def scan_directory(
    target: Path,
    patterns: list[str],
    file_extensions: Optional[set[str]] = None,
    exclude_dirs: Optional[set[str]] = None,
) -> dict[Path, list[tuple[int, str]]]:
    """扫描目录下所有文件，返回每个文件的匹配结果。"""
    if file_extensions is None:
        file_extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", ".yaml", ".yml", ".json", ".toml", ".env"}
    if exclude_dirs is None:
        exclude_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".temp", "vendor"}

    results = {}
    if not target.exists():
        return results

    for path in target.rglob("*"):
        if not path.is_file():
            continue
        if any(part in exclude_dirs for part in path.parts):
            continue
        if path.suffix.lower() not in file_extensions:
            continue
        matches = scan_file_content(path, patterns)
        if matches:
            results[path] = matches
    return results


def check_directory_has_clue(
    target: Path,
    clues: list[str],
    file_extensions: Optional[set[str]] = None,
) -> list[tuple[Path, str]]:
    """检查目录中是否包含指定线索（目录名/文件名/内容关键词）。"""
    found = []
    if not target.exists():
        return found

    clue_patterns = [re.escape(c) for c in clues]

    # 检查目录名和文件名
    for path in target.rglob("*"):
        name_lower = path.name.lower()
        for clue in clues:
            if clue.lower() in name_lower:
                found.append((path, f"文件名/目录名匹配: {clue}"))
                break

    # 检查配置文件内容
    config_exts = {".py", ".yaml", ".yml", ".json", ".toml", ".env", ".ini", ".cfg", ".md"}
    content_results = scan_directory(target, clue_patterns, config_exts)
    for fpath, matches in content_results.items():
        for line_no, line in matches:
            found.append((fpath, f"内容匹配 L{line_no}: {line[:80]}"))

    return found[:20]  # 限制输出数量


def run_p0_checks(target: Path) -> P0CheckResult:
    """执行所有P0禁令检查。"""
    results = []
    blocking_count = 0
    warning_count = 0
    manual_checks = []

    # C-002: 检查是否裸用Transformers Pipeline
    pipeline_hits = scan_directory(target, PIPELINE_PRODUCTION_PATTERNS, {".py"})
    vllm_hits = scan_directory(target, VLLM_PATTERNS, {".py"})
    c002_passed = not pipeline_hits or bool(vllm_hits)
    c002_evidence = []
    if pipeline_hits:
        for fpath, matches in list(pipeline_hits.items())[:3]:
            for line_no, line in matches[:2]:
                c002_evidence.append(f"{fpath}:{line_no}: {line}")
        if not vllm_hits:
            c002_details = "检测到Transformers Pipeline使用但未发现vLLM，生产环境建议升级vLLM"
        else:
            c002_details = f"检测到Pipeline（{len(pipeline_hits)}文件）但同时存在vLLM，需确认生产环境使用vLLM"
    else:
        c002_details = "未检测到裸用Transformers Pipeline"
    results.append(CheckItemResult(
        constraint_id="C-002",
        name=P0_CONSTRAINTS["C-002"]["name"],
        passed=c002_passed,
        severity="blocking",
        evidence=c002_evidence,
        details=c002_details,
    ))
    if not c002_passed:
        blocking_count += 1

    # C-003: 检查可观测性工具
    obs_hits = check_directory_has_clue(target, OBSERVABILITY_TOOLS)
    c003_passed = bool(obs_hits)
    c003_evidence = [f"{p}: {desc}" for p, desc in obs_hits[:5]]
    c003_details = (
        f"发现{len(obs_hits)}处可观测性相关线索"
        if c003_passed
        else "未发现可观测性工具配置（Helicone/Langfuse/Portkey等），必须先建立监控基线"
    )
    results.append(CheckItemResult(
        constraint_id="C-003",
        name=P0_CONSTRAINTS["C-003"]["name"],
        passed=c003_passed,
        severity="blocking",
        evidence=c003_evidence,
        details=c003_details,
    ))
    if not c003_passed:
        blocking_count += 1

    # C-007: 检查语义缓存阈值
    code_exts = {".py", ".js", ".ts", ".jsx", ".tsx", ".yaml", ".yml", ".json", ".toml"}
    threshold_violations = []
    threshold_ok = []
    for fpath in target.rglob("*"):
        if not fpath.is_file() or fpath.suffix.lower() not in code_exts:
            continue
        if any(part in {".git", "node_modules", "__pycache__", "vendor"} for part in fpath.parts):
            continue
        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        thresholds = extract_threshold_value(content, SEMANTIC_CACHE_THRESHOLD_PATTERNS)
        for name, val, line_no in thresholds:
            if val < 0.9:
                threshold_violations.append((fpath, name, val, line_no))
            else:
                threshold_ok.append((fpath, name, val, line_no))

    c007_passed = len(threshold_violations) == 0
    c007_evidence = []
    for fpath, name, val, line_no in threshold_violations[:5]:
        c007_evidence.append(f"{fpath}:{line_no}: {name}={val}（<0.9，危险）")
    if threshold_ok:
        for fpath, name, val, line_no in threshold_ok[:2]:
            c007_evidence.append(f"{fpath}:{line_no}: {name}={val}（合规）")
    c007_details = (
        f"发现{len(threshold_violations)}处阈值<0.9"
        if threshold_violations
        else "未发现语义缓存阈值<0.9的配置" if threshold_ok else "未检测到语义缓存配置（如果使用了语义缓存请检查阈值）"
    )
    if not threshold_ok and not threshold_violations:
        # 没有检测到语义缓存配置，不算失败但要提醒
        results.append(CheckItemResult(
            constraint_id="C-007",
            name=P0_CONSTRAINTS["C-007"]["name"],
            passed=True,
            severity="blocking",
            warnings=["未检测到语义缓存配置，如使用语义缓存请确保阈值≥0.9"],
            details=c007_details,
        ))
    else:
        results.append(CheckItemResult(
            constraint_id="C-007",
            name=P0_CONSTRAINTS["C-007"]["name"],
            passed=c007_passed,
            severity="blocking",
            evidence=c007_evidence,
            details=c007_details,
        ))
        if not c007_passed:
            blocking_count += 1

    # C-012: 检查max_tokens设置
    max_tokens_hits = scan_directory(target, MAX_TOKENS_PATTERNS, code_exts)
    # 检查是否有LLM调用文件但没设max_tokens
    llm_call_patterns = [
        r"openai\.", r"chat\.completions", r"completions\.create",
        r"ChatOpenAI", r"OpenAI\(", r"Anthropic\(", r"chat\(",
        r"generate", r"invoke\(", r"predict", r"client\.chat",
    ]
    llm_call_hits = scan_directory(target, llm_call_patterns, {".py", ".js", ".ts", ".jsx", ".tsx"})
    c012_passed = bool(max_tokens_hits) or not bool(llm_call_hits)
    c012_evidence = []
    if max_tokens_hits:
        for fpath, matches in list(max_tokens_hits.items())[:3]:
            for line_no, line in matches[:2]:
                c012_evidence.append(f"{fpath}:{line_no}: {line}")
    c012_details = (
        f"在{len(max_tokens_hits)}个文件中发现max_tokens配置"
        if max_tokens_hits
        else "未检测到max_tokens配置，所有LLM调用接口必须设置合理输出上限" if llm_call_hits
        else "未检测到LLM调用代码"
    )
    results.append(CheckItemResult(
        constraint_id="C-012",
        name=P0_CONSTRAINTS["C-012"]["name"],
        passed=c012_passed,
        severity="blocking",
        evidence=c012_evidence,
        details=c012_details,
    ))
    if not c012_passed:
        blocking_count += 1

    # C-024: 检查质量基线/黄金测试集
    golden_hits = check_directory_has_clue(target, GOLDEN_SET_PATTERNS)
    c024_passed = bool(golden_hits)
    c024_evidence = [f"{p}: {desc}" for p, desc in golden_hits[:5]]
    c024_details = (
        f"发现{len(golden_hits)}处质量基线相关线索"
        if c024_passed
        else "未发现黄金测试集/质量基线配置，优化前必须建立质量基线"
    )
    results.append(CheckItemResult(
        constraint_id="C-024",
        name=P0_CONSTRAINTS["C-024"]["name"],
        passed=c024_passed,
        severity="blocking",
        evidence=c024_evidence,
        details=c024_details,
    ))
    if not c024_passed:
        blocking_count += 1

    # C-020: 检查灰度发布机制
    canary_hits = check_directory_has_clue(target, CANARY_PATTERNS)
    c020_passed = bool(canary_hits)
    c020_evidence = [f"{p}: {desc}" for p, desc in canary_hits[:5]]
    c020_details = (
        f"发现{len(canary_hits)}处灰度发布相关线索"
        if c020_passed
        else "未检测到灰度发布/A/B测试机制，优化上线必须有灰度方案"
    )
    results.append(CheckItemResult(
        constraint_id="C-020",
        name=P0_CONSTRAINTS["C-020"]["name"],
        passed=c020_passed,
        severity="blocking",
        evidence=c020_evidence,
        details=c020_details,
    ))
    if not c020_passed:
        warning_count += 1  # 灰度是部署阶段检查，不是设计阶段阻断
        # 注意：设计阶段灰度可以后续补，所以算warning不是blocking

    # C-001: 质量底线（人工确认）
    manual_checks.append("C-001: 质量底线约束 - 需要人工确认质量阈值Q_min已定义")
    results.append(CheckItemResult(
        constraint_id="C-001",
        name=P0_CONSTRAINTS["C-001"]["name"],
        passed=True,  # 需人工确认，默认通过但标记需检查
        severity="blocking",
        warnings=["需要人工确认：质量底线阈值Q_min已明确定义"],
        details="此项无法自动检测，请人工确认优化不会导致质量下降超过可接受范围",
    ))

    # 修正C-020：设计阶段不是阻断项
    for item in results:
        if item.constraint_id == "C-020" and not item.passed:
            item.warnings.append("设计阶段可后续补充灰度方案，但上线前必须落实")
            # 注意：C-020保持passed=True如果是设计阶段
            # 这里不改动passed，因为脚本不知道当前阶段

    all_passed = blocking_count == 0

    return P0CheckResult(
        target_path=str(target),
        passed=all_passed,
        blocking_count=blocking_count,
        warning_count=warning_count,
        manual_checks_needed=manual_checks,
        items=results,
    )


def print_result(result: P0CheckResult) -> None:
    """以可读格式打印检查结果。"""
    print("=" * 70)
    print("🔍 Token优化P0禁令预检报告")
    print("=" * 70)
    print(f"目标路径: {result.target_path}")
    print()

    pass_icon = "✅"
    fail_icon = "❌"
    warn_icon = "⚠️"

    for item in result.items:
        icon = pass_icon if item.passed else fail_icon
        print(f"{icon} [{item.constraint_id}] {item.name}")
        if item.details:
            print(f"   {item.details}")
        for ev in item.evidence:
            print(f"   📍 {ev}")
        for w in item.warnings:
            print(f"   {warn_icon} {w}")
        print()

    if result.manual_checks_needed:
        print("📋 需要人工确认的项目:")
        for m in result.manual_checks_needed:
            print(f"   • {m}")
        print()

    print("-" * 70)
    if result.passed:
        print(f"✅ P0预检通过（{result.blocking_count}个阻断项, {result.warning_count}个警告）")
        print("   可以开始Token优化方案设计")
    else:
        print(f"❌ P0预检未通过（{result.blocking_count}个阻断项, {result.warning_count}个警告）")
        print("   必须先解决阻断项再开始优化！")
        print()
        print("🔴 阻断项修复优先级:")
        for item in result.items:
            if not item.passed:
                print(f"   • [{item.constraint_id}] {item.name}: {item.details}")

    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Token优化P0禁令预检工具 - 检查优化前必须满足的前置条件"
    )
    parser.add_argument(
        "--target", "-t",
        default=".",
        help="要检查的项目目录路径（默认当前目录）"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="以JSON格式输出结果"
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()

    if not target.exists():
        print(f"❌ 目标路径不存在: {target}", file=sys.stderr)
        sys.exit(1)

    result = run_p0_checks(target)

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print_result(result)

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
