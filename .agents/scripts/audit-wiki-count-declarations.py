#!/usr/bin/env python3
"""OKF 知识包交付的「计数类声明」取证与对账脚本。

用途：把交付文档里写下的计数声明（文件数、事实编号数、引用条数、最长引用长度、
最长原文公共子串）用可复现的方式重新量一遍，避免「按记忆计数」导致的声明失真。

设计约束（与 private-encrypted-pdf-to-okf-wiki Skill 的 S5/S6 对应）：
  1. 口令只从环境变量读取，不接受 --password 参数（命令行会进 shell 历史）
  2. 只读：不修改交付目录，不复制源 PDF
  3. 输出同时给出 rows 与 unique —— 编号被「待核验清单」复述时两者不等，属正常现象
  4. 最长公共子串与「引号内引用最长长度」分开报，二者是不同指标

用法:
    # 仅做交付目录内自洽统计（无需源 PDF）
    python .agents/scripts/audit-wiki-count-declarations.py --wiki playground/wiki/xxx

    # 加密源 PDF 对照（口令走环境变量，不落盘、不回显）
    $env:WIKI_SOURCE_PASSWORD='...'
    python .agents/scripts/audit-wiki-count-declarations.py --wiki playground/wiki/xxx \\
        --source-pdf playground/books/xxx.pdf

    # 机器可读输出
    python .agents/scripts/audit-wiki-count-declarations.py --wiki <dir> --json

退出码:
    0 - 未发现红线问题（重复编号等仅作 WARN 报告）
    1 - 发现红线问题（凭据残留 / 最长公共子串 ≥ 阈值 / 引用超长 / 链接检查失败）
    2 - 参数或路径错误
    3 - 指定了 --source-pdf 但缺少 pypdf 依赖
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

DEFAULT_PASSWORD_ENV = "WIKI_SOURCE_PASSWORD"
DEFAULT_QUOTE_MIN_LEN = 8
DEFAULT_CITATION_LIMIT = 30

QUOTE_RE = re.compile(r"「([^」]{1,200})」")
FACT_ID_RE = re.compile(r"^\|\s*(F-\d{3})\s*\|", re.MULTILINE)
TEXT_SUFFIXES = {".md", ".py", ".toml", ".json", ".txt", ".log", ".yaml", ".yml", ".ps1", ".sh"}
# 归一化：去空白与中英文标点，使「换个说法但标点不同」的引用可比
NOISE_RE = re.compile(r"[\s\u3000，。、；：！？「」『』（）()【】《》,.;:!?\"'\-—…·*#>|`/\\]")


def normalize(text):
    """去掉空白与标点，用于逐字比对。"""
    return NOISE_RE.sub("", text)


def collect_markdown(root):
    """收集交付目录下的全部 Markdown 文件（不跟踪符号链接）。"""
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def count_fact_ids(texts):
    """统计事实编号：返回 rows（表格行数）、unique（唯一编号数）、duplicates。"""
    counter = Counter()
    rows = 0
    for text in texts:
        for match in FACT_ID_RE.finditer(text):
            rows += 1
            counter[match.group(1)] += 1
    duplicates = {fid: n for fid, n in counter.items() if n > 1}
    return {"rows": rows, "unique": len(counter), "duplicates": duplicates}


def analyze_quotes(wiki_text, source_text=None, min_len=DEFAULT_QUOTE_MIN_LEN):
    """统计引号内引用，并在有源文本时判定是否逐字命中。"""
    quotes = QUOTE_RE.findall(wiki_text)
    normalized = [normalize(q) for q in quotes]
    result = {
        "quotes_total": len(quotes),
        "quotes_unique": len({q for q in normalized if q}),
        "max_quote_len": max((len(q) for q in normalized), default=0),
    }
    if source_text is None:
        return result

    source_norm = normalize(source_text)
    hits = [q for q in normalized if len(q) >= min_len and q in source_norm]
    result.update(
        {
            "quote_min_len": min_len,
            "quotes_hit_source": len(hits),
            "quotes_hit_unique": len(set(hits)),
            "max_hit_quote_len": max((len(q) for q in hits), default=0),
        }
    )
    return result


def longest_common_substring_len(left, right):
    """返回两段文本的最长公共子串长度。

    用「k-gram 集合 + 二分」而非 difflib.SequenceMatcher：后者的比对开销随
    文本长度平方增长，十几万字的交付目录与源文本相乘会长时间卡死。
    """
    if not left or not right:
        return 0

    def has_common(k):
        if k <= 0:
            return True
        grams = {right[i : i + k] for i in range(len(right) - k + 1)}
        return any(left[i : i + k] in grams for i in range(len(left) - k + 1))

    lo, hi = 0, min(len(left), len(right))
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if has_common(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo


def find_longest_common_substring(markdown_files, source_text):
    """逐文件比对，返回最长公共子串的 {len, file}；比整包串联更能定位来源。"""
    source_norm = normalize(source_text)
    best = {"len": 0, "file": ""}
    for path, text in markdown_files:
        size = longest_common_substring_len(normalize(text), source_norm)
        if size > best["len"]:
            best = {"len": size, "file": str(path)}
    return best


def scan_for_secret(root, secret):
    """在交付目录的文本文件中回扫凭据；返回命中的相对路径列表。"""
    if not secret:
        return []
    hits = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if secret in content:
            hits.append(str(path.relative_to(root)))
    return hits


def run_link_check(wiki_root):
    """复用既有 check-links.py，不重复实现链接逻辑。"""
    script = SCRIPTS_DIR / "check-links.py"
    if not script.exists():
        return {"returncode": None, "tail": "check-links.py 不存在，已跳过"}
    proc = subprocess.run(
        [sys.executable, str(script), "--path", str(wiki_root)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    lines = [line.strip() for line in (proc.stdout or "").splitlines() if line.strip()]
    summary = [
        line for line in lines
        if any(key in line for key in ("内联链接:", "本地引用:", "通过: 所有本地引用", "失败:"))
    ]
    return {
        "returncode": proc.returncode,
        "tail": " | ".join(summary) if summary else (lines[-1] if lines else ""),
    }


def extract_pdf_text(pdf_path, password):
    """解密并抽取 PDF 文本层；返回逐页文本列表。"""
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    if reader.is_encrypted:
        if not password:
            raise ValueError(
                "源 PDF 已加密，但未提供口令。请先设置环境变量 "
                f"{DEFAULT_PASSWORD_ENV}（命令行参数会进入 shell 历史，故不提供）。"
            )
        if reader.decrypt(password) == 0:
            raise ValueError("口令无效，PDF 解密失败。")
    return [page.extract_text() or "" for page in reader.pages]


def die(code, message):
    """打印错误并以指定退出码终止（2=参数/路径，3=依赖缺失）。"""
    print(f"[ERROR] {message}", file=sys.stderr)
    raise SystemExit(code)


def build_report(args):
    wiki_root = Path(args.wiki).resolve()
    if not wiki_root.is_dir():
        die(2, f"交付目录不存在: {wiki_root}")

    files = collect_markdown(wiki_root)
    if not files:
        die(2, f"交付目录内没有 Markdown 文件: {wiki_root}")

    texts = [p.read_text(encoding="utf-8", errors="replace") for p in files]
    wiki_all = "\n".join(texts)
    pairs = [(p.relative_to(wiki_root).as_posix(), text) for p, text in zip(files, texts)]

    report = {
        "wiki_root": str(wiki_root),
        "files": len(files),
        "bytes": sum(p.stat().st_size for p in files),
        "facts": count_fact_ids(texts),
    }

    password = os.environ.get(args.password_env, "")
    source_text = None
    if args.source_pdf:
        pdf_path = Path(args.source_pdf).resolve()
        if not pdf_path.is_file():
            die(2, f"源 PDF 不存在: {pdf_path}")
        try:
            pages = extract_pdf_text(pdf_path, password)
        except ImportError:
            die(3, "缺少 pypdf 依赖：pip install pypdf")
        except ValueError as exc:
            die(2, str(exc))
        source_text = "\n".join(pages)
        report["source_pages"] = len(pages)

    report["quotes"] = analyze_quotes(wiki_all, source_text)
    if source_text is not None:
        report["longest_common_substring"] = find_longest_common_substring(pairs, source_text)

    report["secret_hits"] = scan_for_secret(wiki_root, password)
    if not args.skip_links:
        report["links"] = run_link_check(wiki_root)
    return report


def evaluate(report, citation_limit):
    """把统计结果判成红线清单；返回 (failures, warnings)。"""
    failures = []
    warnings = []

    quotes = report["quotes"]
    if "quotes_hit_source" in quotes:
        # 红线只判「逐字引用源文本」的引语；「」内还可能是术语与清单，不是引用
        if quotes["max_hit_quote_len"] > citation_limit:
            failures.append(
                f"逐字引用最长 {quotes['max_hit_quote_len']} 字，超过红线 {citation_limit} 字"
            )
    else:
        warnings.append(
            f"未提供源 PDF，引用红线未判定（「」内全部内容最长 {quotes['max_quote_len']} 字，"
            "该值含术语与清单，不等于引用长度）"
        )
    lcs = report.get("longest_common_substring")
    if lcs and lcs["len"] >= citation_limit:
        failures.append(
            f"最长公共子串 {lcs['len']} 字（{lcs['file']}），达到红线 {citation_limit} 字"
        )

    if report["secret_hits"]:
        failures.append(f"凭据残留于 {len(report['secret_hits'])} 个文件")

    facts = report["facts"]
    if facts["duplicates"]:
        warnings.append(
            f"编号重复 {len(facts['duplicates'])} 个（rows={facts['rows']} / unique={facts['unique']}，"
            "常见于「待核验清单」复述，声明时须同时写 rows 与 unique）"
        )

    links = report.get("links")
    if links and links["returncode"] not in (0, None):
        failures.append(f"链接检查未通过：{links['tail']}")
    return failures, warnings


def print_report(report):
    facts = report["facts"]
    quotes = report["quotes"]
    print("=" * 60)
    print("OKF 知识包计数声明取证")
    print("=" * 60)
    print(f"交付目录: {report['wiki_root']}")
    print(f"Markdown: {report['files']} 个 / {report['bytes']} 字节")
    print(f"事实编号（全交付目录，含审计文件复述）: rows={facts['rows']} unique={facts['unique']}")
    if facts["duplicates"]:
        detail = ", ".join(f"{fid}×{n}" for fid, n in sorted(facts["duplicates"].items()))
        print(f"  重复编号: {detail}")
    print(f"引号内引用: 共 {quotes['quotes_total']} 条 / 去重 {quotes['quotes_unique']} 条")
    print(f"  「」内全部内容最长（含术语与清单，不等于引用）: {quotes['max_quote_len']} 字")
    if "quotes_hit_source" in quotes:
        print(
            f"  与源逐字命中（归一化后 ≥{quotes['quote_min_len']} 字）: "
            f"{quotes['quotes_hit_source']} 条 / 去重 {quotes['quotes_hit_unique']} 条"
            f" / 其中最长 {quotes['max_hit_quote_len']} 字"
        )
        print(f"源 PDF 页数: {report.get('source_pages')}")
    if "longest_common_substring" in report:
        lcs = report["longest_common_substring"]
        print(f"全文最长公共子串: {lcs['len']} 字（{lcs['file']}）")
    print(f"凭据回扫命中: {len(report['secret_hits'])} 个文件")
    for hit in report["secret_hits"]:
        print(f"  - {hit}")
    links = report.get("links")
    if links:
        state = "跳过" if links["returncode"] is None else ("通过" if links["returncode"] == 0 else "失败")
        print(f"链接检查: {state}（{links['tail']}）")
    print("=" * 60)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="OKF 知识包交付的计数声明取证（只读，口令仅走环境变量）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  python .agents/scripts/audit-wiki-count-declarations.py --wiki playground/wiki/demo\n"
            "  $env:WIKI_SOURCE_PASSWORD='***'; python .agents/scripts/"
            "audit-wiki-count-declarations.py --wiki <dir> --source-pdf <pdf>\n"
        ),
    )
    parser.add_argument("--wiki", required=True, help="OKF 知识包交付目录")
    parser.add_argument("--source-pdf", help="源 PDF（可选；用于引用逐字比对与公共子串实测）")
    parser.add_argument(
        "--password-env",
        default=DEFAULT_PASSWORD_ENV,
        help=f"存放 PDF 口令的环境变量名（默认 {DEFAULT_PASSWORD_ENV}）",
    )
    parser.add_argument(
        "--citation-limit",
        type=int,
        default=DEFAULT_CITATION_LIMIT,
        help=f"引用红线字数（默认 {DEFAULT_CITATION_LIMIT}）",
    )
    parser.add_argument("--skip-links", action="store_true", help="跳过 check-links.py 调用")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    args = parser.parse_args(argv)

    report = build_report(args)
    failures, warnings = evaluate(report, args.citation_limit)

    if args.json:
        payload = dict(report)
        payload["failures"] = failures
        payload["warnings"] = warnings
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_report(report)
        for item in warnings:
            print(f"[WARN] {item}")
        for item in failures:
            print(f"[ERROR] {item}")
        print("结论: " + ("通过" if not failures else f"未通过（{len(failures)} 项红线）"))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
