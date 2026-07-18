#!/usr/bin/env python3
"""学术来源自动化验证脚本（L0-L2 MVP）。

功能：
- L0: 从Markdown文件中提取DOI和arXiv ID，支持多种格式
- L1: 通过CrossRef API验证DOI存在性，带缓存、并发、超时、优雅降级
- L2: 元数据一致性比对（标题模糊匹配、年份精确匹配、第一作者姓氏匹配）
- 输出文本报告或JSON报告
- 只读工具，不修改任何被扫描文件

明确不做（MVP边界）：
- 不抓取引用计数（代理指标陷阱）
- 不做可信度评级（需领域判断）
- 不自动修复文件（需人工判断）
- arXiv API验证（MVP仅格式校验）
- L3撤稿检测（后续迭代）
"""

import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.error
import ssl
from difflib import SequenceMatcher
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.project import resolve_project_root
from lib.cli import add_common_args, print_pass, print_warn, print_error, print_header, print_summary
from lib.markdown import find_markdown_files
from lib.atomic_write import atomic_write_json

CROSSREF_API_URL = "https://" + "api.crossref.org/works/{doi}"
CACHE_DIR_NAME = ".agents/cache"
CACHE_FILE_NAME = "academic-sources-cache.json"
CACHE_TTL_DAYS = 7
DEFAULT_TIMEOUT = 10
DEFAULT_WORKERS = 3
USER_AGENT = "AcademicSourceChecker/1.0 (SpecWeave Project; mailto:null@example.com)"

STATUS_PASS = "pass"
STATUS_WARN = "warn"
STATUS_ERROR = "error"
STATUS_SKIPPED = "skipped"
STATUS_INFO = "info"

DOI_PATTERNS = [
    re.compile(r"https?://(?:dx\.)?doi\.org/(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", re.IGNORECASE),
    re.compile(r"(?<!\d)(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", re.IGNORECASE),
]

ARXIV_PATTERNS = [
    re.compile(r"arXiv:(\d{4}\.\d{4,5}(?:v\d+)?)", re.IGNORECASE),
    re.compile(r"arxiv\.org/abs/(\d{4}\.\d{4,5}(?:v\d+)?)", re.IGNORECASE),
    re.compile(r"arXiv:([a-z\-]+/\d{7}(?:v\d+)?)", re.IGNORECASE),
]

YEAR_IN_CONTEXT_RE = re.compile(
    r"(?:19|20)\d{2}",
)

YEAR_BEFORE_DOI_RE = re.compile(
    r"\((19[5-9]\d|20[0-2]\d)\)(?:[^()]{0,80}?)DOI:",
    re.IGNORECASE,
)

FIRST_AUTHOR_RE = re.compile(
    r"(?:by|作者|By|BY)\s*([A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z]+|[A-Z][a-z]+\s+et\s+al\.)",
)


def normalize_doi(doi: str) -> str:
    doi = doi.strip()
    doi = re.sub(r'https?://(dx\.)?doi\.org/', '', doi)
    doi = doi.lower()
    doi = re.sub(r"[).,;:]+$", "", doi)
    return doi


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def text_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def _get_cache_path(project_root: Path) -> Path:
    cache_dir = project_root / CACHE_DIR_NAME
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / CACHE_FILE_NAME


def load_cache(project_root: Path) -> dict:
    cache_path = _get_cache_path(project_root)
    if not cache_path.exists():
        return {}
    try:
        with open(cache_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(project_root: Path, cache: dict):
    cache_path = _get_cache_path(project_root)
    cache["_metadata"] = {
        "updated_at": datetime.now().isoformat(),
        "ttl_days": CACHE_TTL_DAYS,
    }
    atomic_write_json(cache_path, cache, ensure_ascii=False, indent=2)


def is_cache_valid(entry: dict, ttl_days: int = CACHE_TTL_DAYS) -> bool:
    checked_at = entry.get("checked_at")
    if not checked_at:
        return False
    try:
        checked_time = datetime.fromisoformat(checked_at)
    except ValueError:
        return False
    return datetime.now() - checked_time < timedelta(days=ttl_days)


def extract_identifiers_from_file(file_path: Path) -> list:
    identifiers = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return identifiers

    lines = content.split("\n")
    seen_dois = set()
    seen_arxivs = set()

    for line_num, line in enumerate(lines, start=1):
        for pattern in DOI_PATTERNS:
            for match in pattern.finditer(line):
                doi = normalize_doi(match.group(1))
                if doi and doi not in seen_dois:
                    seen_dois.add(doi)
                    identifiers.append({
                        "type": "doi",
                        "id": doi,
                        "file": str(file_path),
                        "line": line_num,
                        "context": line,
                    })

        for pattern in ARXIV_PATTERNS:
            for match in pattern.finditer(line):
                arxiv_id = match.group(1)
                arxiv_id = re.sub(r"[).,;:]+$", "", arxiv_id)
                if arxiv_id and arxiv_id not in seen_arxivs:
                    seen_arxivs.add(arxiv_id)
                    identifiers.append({
                        "type": "arxiv",
                        "id": arxiv_id,
                        "file": str(file_path),
                        "line": line_num,
                        "context": line,
                    })

    return identifiers


def extract_doc_metadata(context: str) -> dict:
    metadata = {"title": None, "year": None, "first_author_surname": None}

    year_match = YEAR_BEFORE_DOI_RE.search(context)
    if not year_match:
        year_match = YEAR_IN_CONTEXT_RE.search(context)
    if year_match:
        try:
            year_str = year_match.group(1) if year_match.lastindex else year_match.group(0)
            metadata["year"] = int(year_str)
        except (ValueError, IndexError):
            pass

    author_match = FIRST_AUTHOR_RE.search(context)
    if author_match:
        name = author_match.group(1)
        if " et al." in name:
            surname = name.split(" et al.")[0].split()[-1]
        else:
            parts = name.split()
            surname = parts[-1] if parts else None
        metadata["first_author_surname"] = surname.lower() if surname else None

    return metadata


def query_crossref(doi: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    url = CROSSREF_API_URL.format(doi=urllib.request.quote(doi, safe=""))
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Accept", "application/json")

    ctx = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                message = data.get("message", {})
                return parse_crossref_message(doi, message)
            else:
                return {"doi": doi, "exists": False, "status_code": response.status, "error": f"HTTP {response.status}"}
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"doi": doi, "exists": False, "status_code": 404, "error": "DOI not found (404)"}
        return {"doi": doi, "exists": False, "status_code": e.code, "error": f"HTTP error: {e.code}"}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return {"doi": doi, "exists": None, "error": f"Network error: {type(e).__name__}: {e}"}


def parse_crossref_message(doi: str, message: dict) -> dict:
    result = {"doi": doi, "exists": True, "status_code": 200}

    title_list = message.get("title", [])
    result["title"] = title_list[0] if title_list else None

    authors = message.get("author", [])
    result["authors"] = []
    result["first_author_surname"] = None
    result["first_author_given"] = None
    if authors:
        first_author = authors[0]
        family = first_author.get("family", "")
        given = first_author.get("given", "")
        result["first_author_surname"] = family.lower() if family else None
        result["first_author_given"] = given
        for a in authors:
            a_family = a.get("family", "")
            a_given = a.get("given", "")
            if a_family:
                result["authors"].append(f"{a_given} {a_family}".strip())

    issued = message.get("issued", {})
    date_parts = issued.get("date-parts", [[]])
    if date_parts and date_parts[0]:
        result["year"] = date_parts[0][0]
    else:
        result["year"] = None

    container = message.get("container-title", [])
    result["journal"] = container[0] if container else None

    result["type"] = message.get("type", None)
    result["publisher"] = message.get("publisher", None)

    return result


def compare_metadata(doc_meta: dict, api_meta: dict) -> list:
    issues = []

    if api_meta.get("title") and doc_meta.get("title"):
        similarity = text_similarity(doc_meta["title"], api_meta["title"])
        if similarity >= 0.99:
            issues.append(("title", STATUS_PASS, "标题匹配"))
        elif similarity >= 0.85:
            issues.append(("title", STATUS_WARN,
                           f"标题近似（相似度{similarity:.0%}），建议人工确认"))
        else:
            issues.append(("title", STATUS_ERROR,
                           f"标题不匹配（相似度{similarity:.0%}）"))
    elif not doc_meta.get("title"):
        issues.append(("title", STATUS_INFO, "文档未显式记录标题，可从API补充"))

    if api_meta.get("year") and doc_meta.get("year"):
        if api_meta["year"] == doc_meta["year"]:
            issues.append(("year", STATUS_PASS, f"年份匹配（{api_meta['year']}）"))
        else:
            issues.append(("year", STATUS_WARN,
                           f"年份需确认：文档记{doc_meta['year']}，API返回{api_meta['year']}（可能是同句引用多篇论文）"))
    elif not doc_meta.get("year"):
        issues.append(("year", STATUS_INFO, f"文档未显式记录年份，API返回{api_meta.get('year', '未知')}"))

    if api_meta.get("first_author_surname") and doc_meta.get("first_author_surname"):
        api_surname = api_meta["first_author_surname"].lower()
        doc_surname = doc_meta["first_author_surname"].lower()
        if api_surname == doc_surname:
            issues.append(("author", STATUS_PASS, f"第一作者姓氏匹配（{api_surname.title()}）"))
        else:
            issues.append(("author", STATUS_ERROR,
                           f"第一作者不一致：文档记{doc_surname.title()}，API返回{api_surname.title()}"))
    elif not doc_meta.get("first_author_surname"):
        authors_str = ", ".join(api_meta.get("authors", [])[:3])
        if authors_str:
            issues.append(("author", STATUS_INFO, f"文档未显式记录作者，API返回：{authors_str}"))

    return issues


def verify_one_doi(identifier: dict, cache: dict, use_cache: bool, timeout: int) -> dict:
    doi = identifier["id"]
    result = {
        **identifier,
        "api_metadata": None,
        "validation_issues": [],
        "overall_status": STATUS_SKIPPED,
    }

    if use_cache and doi in cache and is_cache_valid(cache[doi]):
        cached = cache[doi]
        result["api_metadata"] = cached.get("api_metadata")
        result["from_cache"] = True
    else:
        api_result = query_crossref(doi, timeout=timeout)
        result["api_metadata"] = api_result
        result["from_cache"] = False
        cache[doi] = {
            "checked_at": datetime.now().isoformat(),
            "api_metadata": api_result,
        }

    api_meta = result["api_metadata"]

    if api_meta is None:
        result["overall_status"] = STATUS_SKIPPED
        result["validation_issues"].append(("existence", STATUS_SKIPPED, "API查询失败，无缓存"))
        return result

    if api_meta.get("exists") is False:
        result["overall_status"] = STATUS_ERROR
        result["validation_issues"].append(("existence", STATUS_ERROR, api_meta.get("error", "DOI不存在")))
        return result

    if api_meta.get("exists") is None:
        result["overall_status"] = STATUS_SKIPPED
        result["validation_issues"].append(("existence", STATUS_SKIPPED, api_meta.get("error", "网络异常")))
        return result

    result["validation_issues"].append(("existence", STATUS_PASS, "DOI存在"))

    doc_meta = extract_doc_metadata(identifier["context"])
    issues = compare_metadata(doc_meta, api_meta)
    result["validation_issues"].extend(issues)

    statuses = [s for _, s, _ in result["validation_issues"]]
    if STATUS_ERROR in statuses:
        result["overall_status"] = STATUS_ERROR
    elif STATUS_WARN in statuses:
        result["overall_status"] = STATUS_WARN
    elif STATUS_INFO in statuses and STATUS_PASS in statuses:
        result["overall_status"] = STATUS_PASS
    else:
        result["overall_status"] = STATUS_PASS

    return result


def verify_arxiv(identifier: dict) -> dict:
    result = {
        **identifier,
        "api_metadata": None,
        "validation_issues": [],
        "overall_status": STATUS_INFO,
        "note": "arXiv ID格式校验通过（MVP不查询arXiv API）",
    }
    arxiv_id = identifier["id"]
    if re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", arxiv_id) or re.match(r"^[a-z\-]+/\d{7}(v\d+)?$", arxiv_id):
        result["validation_issues"].append(("format", STATUS_PASS, f"arXiv ID格式正确：{arxiv_id}"))
        result["overall_status"] = STATUS_PASS
    else:
        result["validation_issues"].append(("format", STATUS_ERROR, f"arXiv ID格式异常：{arxiv_id}"))
        result["overall_status"] = STATUS_ERROR
    return result


def print_text_report(results_by_file: dict, stats: dict):
    print_header("学术来源验证报告")
    print()

    for file_path, results in sorted(results_by_file.items()):
        rel_path = Path(file_path)
        try:
            project_root = resolve_project_root(__file__)
            rel_path = Path(file_path).relative_to(project_root)
        except ValueError:
            pass
        print(f"📄 {rel_path}")
        for r in results:
            id_str = r["id"]
            line = r["line"]
            status = r["overall_status"]

            if status == STATUS_PASS:
                icon = "✅"
                printer = print_pass
            elif status == STATUS_WARN:
                icon = "⚠️"
                printer = print_warn
            elif status == STATUS_ERROR:
                icon = "❌"
                printer = print_error
            elif status == STATUS_SKIPPED:
                icon = "⏭️"
                printer = print_warn
            else:
                icon = "ℹ️"
                printer = print_pass

            type_label = "DOI" if r["type"] == "doi" else "arXiv"
            printer(f"  L{line} [{type_label}] {id_str}")

            for field, issue_status, msg in r["validation_issues"]:
                if issue_status == STATUS_PASS:
                    mark = "✓"
                elif issue_status == STATUS_WARN:
                    mark = "⚠"
                elif issue_status == STATUS_ERROR:
                    mark = "✗"
                elif issue_status == STATUS_SKIPPED:
                    mark = "⊘"
                else:
                    mark = "ℹ"
                print(f"      {mark} {msg}")

            if r.get("from_cache"):
                print(f"      ℹ 使用缓存结果")

            if r.get("note"):
                print(f"      ℹ {r['note']}")
        print()

    print_summary(
        pass_count=stats["pass"],
        warn_count=stats["warn"],
        error_count=stats["error"],
        width=60,
    )
    skipped = stats.get("skipped", 0)
    info = stats.get("info", 0)
    if skipped:
        print_warn(f"⏭️  跳过: {skipped} 个（网络异常或超时）")
    if info:
        print_pass(f"ℹ️  信息: {info} 个（元数据缺失，可补充）")


def main():
    parser = argparse.ArgumentParser(
        description="学术来源自动化验证脚本（L0-L2 MVP）"
    )
    add_common_args(parser)
    parser.add_argument("--no-cache", action="store_true", help="跳过缓存，强制刷新API查询")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"HTTP请求超时秒数（默认{DEFAULT_TIMEOUT}）")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help=f"并发线程数（默认{DEFAULT_WORKERS}）")
    args = parser.parse_args()

    project_root = resolve_project_root(__file__)
    scan_path = Path(args.path) if args.path else project_root
    if not scan_path.is_absolute():
        scan_path = (project_root / scan_path).resolve()

    md_files = find_markdown_files(scan_path)
    if not md_files:
        print_warn(f"在 {scan_path} 下未找到Markdown文件")
        return 0

    print_header("学术来源自动化验证（L0-L2 MVP）")
    print(f"扫描目录: {scan_path}")
    print(f"找到 {len(md_files)} 个Markdown文件")
    print()

    all_identifiers = []
    for f in md_files:
        ids = extract_identifiers_from_file(f)
        all_identifiers.extend(ids)

    if not all_identifiers:
        print_pass("未发现DOI或arXiv ID引用，无需验证")
        print_summary(pass_count=0, warn_count=0, error_count=0)
        return 0

    doi_count = sum(1 for i in all_identifiers if i["type"] == "doi")
    arxiv_count = sum(1 for i in all_identifiers if i["type"] == "arxiv")
    print(f"提取到 {len(all_identifiers)} 个学术ID：{doi_count} 个DOI，{arxiv_count} 个arXiv")
    print()

    cache = load_cache(project_root)
    use_cache = not args.no_cache

    results = []
    results_by_file = {}

    arxiv_identifiers = [i for i in all_identifiers if i["type"] == "arxiv"]
    for ident in arxiv_identifiers:
        r = verify_arxiv(ident)
        results.append(r)
        results_by_file.setdefault(r["file"], []).append(r)

    doi_identifiers = [i for i in all_identifiers if i["type"] == "doi"]
    if doi_identifiers:
        print_header("CrossRef API验证（DOI）")
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(verify_one_doi, ident, cache, use_cache, args.timeout): ident
                for ident in doi_identifiers
            }
            for future in as_completed(futures):
                try:
                    r = future.result()
                    results.append(r)
                    results_by_file.setdefault(r["file"], []).append(r)
                except Exception as e:
                    ident = futures[future]
                    print_error(f"验证{ident['id']}时发生异常: {e}")

    save_cache(project_root, cache)

    stats = {"pass": 0, "warn": 0, "error": 0, "skipped": 0, "info": 0}
    for r in results:
        s = r["overall_status"]
        if s in stats:
            stats[s] += 1
        else:
            stats[s] = 1

    if args.json:
        json_output = {
            "scan_path": str(scan_path),
            "file_count": len(md_files),
            "identifier_count": len(all_identifiers),
            "doi_count": doi_count,
            "arxiv_count": arxiv_count,
            "stats": stats,
            "results": results,
        }
        print(json.dumps(json_output, ensure_ascii=False, indent=2, default=str))
    else:
        print()
        print_text_report(results_by_file, stats)

    return 1 if stats["error"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
