#!/usr/bin/env python3
"""扫描 Markdown 文件中的链接，校验外部 URL 可达性与本地文件引用有效性。
支持 --fix 自动修复可修复的断链，包括：
- file:/// 绝对路径转相对路径
- 相对路径层级自动校正（目录迁移后 ../ 层数不对的问题）
- 目录链接尾部斜杠补全
- 文件名重命名映射
- 外部链接检查：HEAD 请求 + GET Range 回退、结果缓存、并发检测"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import ssl
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from constants import (
    EXCLUDED_DIRS,
    LINK_CHECK_TIMEOUT,
    LINK_CHECK_WORKERS,
    LINK_CHECK_EXCLUDE_DIRS,
    LINK_CHECK_USER_AGENT,
)
from lib.project import resolve_project_root
from lib.link_fixer import is_code_fence_context, INLINE_LINK_RE
from lib.cli import add_common_args, setup_safe_output
from lib.markdown import find_markdown_files

# 匹配引用式链接定义: [ref]: url
REF_LINK_RE = re.compile(r"^\s*\[([^\]]+)\]:\s*(.+)$", re.MULTILINE)
# 匹配引用式链接使用: [text][ref]
REF_USAGE_RE = re.compile(r"\[([^\]]*)\]\[([^\]]*)\]")


CURLY_PLACEHOLDER_RE = re.compile(r"\{[^}]+\}")

CACHE_DIR_NAME = ".agents/cache"
CACHE_FILE_NAME = "external-links-cache.json"
CACHE_TTL_DAYS = 7

EXTERNAL_URL_SUCCESS = 0
EXTERNAL_URL_BROKEN = 1
EXTERNAL_URL_SKIPPED = 2


def _get_cache_path(project_root: Path) -> Path:
    """获取外部链接检查缓存文件路径。"""
    cache_dir = project_root / CACHE_DIR_NAME
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / CACHE_FILE_NAME


def load_cache(project_root: Path) -> dict:
    """加载外部链接检查缓存。"""
    cache_path = _get_cache_path(project_root)
    if not cache_path.exists():
        return {}
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(project_root: Path, cache: dict):
    """保存外部链接检查缓存。"""
    cache_path = _get_cache_path(project_root)
    cache["_metadata"] = {
        "updated_at": datetime.now().isoformat(),
        "ttl_days": CACHE_TTL_DAYS,
    }
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def is_cache_valid(entry: dict, ttl_days: int = CACHE_TTL_DAYS) -> bool:
    """判断缓存条目是否有效（未过期）。"""
    checked_at = entry.get("checked_at")
    if not checked_at:
        return False
    try:
        checked_time = datetime.fromisoformat(checked_at)
    except ValueError:
        return False
    return datetime.now() - checked_time < timedelta(days=ttl_days)


def is_template_placeholder(url: str) -> bool:
    """判断 URL 是否为模板占位符（如 <!-- ... --> 或 {变量名} 格式）。"""
    if url.startswith("<!--") and url.endswith("-->"):
        return True
    if CURLY_PLACEHOLDER_RE.search(url):
        return True
    return False


def parse_links(file_path: Path) -> list[tuple[str, str, int]]:
    """解析 Markdown 文件中的链接，返回 (文本, URL, 行号) 列表。"""
    content = file_path.read_text(encoding="utf-8")
    links = []

    # 收集引用式链接定义
    ref_defs = {}
    for m in REF_LINK_RE.finditer(content):
        ref_id = m.group(1).lower()
        ref_url = m.group(2).strip()
        if not is_template_placeholder(ref_url):
            ref_defs[ref_id] = ref_url

    # 解析内联链接
    for m in INLINE_LINK_RE.finditer(content):
        if is_code_fence_context(content, m.start()):
            continue
        text = m.group(1)
        url = m.group(2).strip()
        if url and not url.startswith("#") and not is_template_placeholder(url):
            line_num = content[: m.start()].count("\n") + 1
            links.append((text, url, line_num))

    # 解析引用式链接使用 (不含定义行)
    for m in REF_USAGE_RE.finditer(content):
        if is_code_fence_context(content, m.start()):
            continue
        ref_id = m.group(2).strip().lower()
        if ref_id and ref_id in ref_defs:
            text = m.group(1)
            line_num = content[: m.start()].count("\n") + 1
            links.append((text, ref_defs[ref_id], line_num))

    return links


def is_external_url(url: str) -> bool:
    """判断 URL 是否为外部链接。"""
    return url.startswith("http://") or url.startswith("https://")


def is_local_ref(url: str) -> bool:
    """判断 URL 是否为本地文件引用。"""
    return not is_external_url(url) and not url.startswith("#") and not url.startswith("mailto:")


def _make_request(url: str, method: str, timeout: int, ctx: ssl.SSLContext):
    """构造并发送 HTTP 请求。"""
    req = urllib.request.Request(url, method=method)
    req.add_header("User-Agent", LINK_CHECK_USER_AGENT)
    req.add_header("Accept", "*/*")
    if method == "GET":
        req.add_header("Range", "bytes=0-0")
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.status, resp.geturl()


def check_external_link(url: str, timeout: int) -> tuple[str, int, str]:
    """检查外部链接是否可达。返回 (url, http_status, error_message)。

    检测策略：
    1. 首先使用 HEAD 请求（快速、不下载内容）
    2. HEAD 失败/不支持时，用 GET Range: bytes=0-0 回退（只获取第一个字节）
    3. 403/405 视为可接受（反爬虫/不支持 HEAD），但记录状态码
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    status = 0
    final_url = url
    error = ""

    for method in ("HEAD", "GET"):
        try:
            status, final_url = _make_request(url, method, timeout, ctx)
            if status < 400 or status in (403, 405):
                return (url, status, "")
            error = f"HTTP {status}"
        except urllib.error.HTTPError as e:
            status = e.code
            if e.code in (405, 403, 401):
                if method == "HEAD":
                    time.sleep(0.3)
                    continue
                return (url, e.code, "")
            error = str(e)
        except urllib.error.URLError as e:
            status = 0
            error = str(e.reason)
            if method == "HEAD":
                time.sleep(0.3)
                continue
        except Exception as e:
            status = 0
            error = str(e)
            if method == "HEAD":
                time.sleep(0.3)
                continue

    return (url, status, error)


def check_local_link(file_path: Path, url: str) -> tuple[str, str, str]:
    """检查本地文件引用是否有效。返回 (url, status, message)。

    status:
      - "ok": 目标是文件，链接可正常打开
      - "directory": 目标是目录（IDE/Markdown渲染器无法直接打开目录，应链接到README.md）
      - "missing": 目标不存在（断链）
    """
    base_dir = file_path.parent
    clean_url = url.split("#")[0]
    if not clean_url:
        return (url, "ok", "")

    if clean_url.startswith("file:///"):
        from urllib.parse import urlparse, unquote
        parsed = urlparse(clean_url)
        target = Path(unquote(parsed.path.lstrip("/")))
    else:
        target = (base_dir / clean_url).resolve()

    if not target.exists():
        return (url, "missing", f"文件不存在: {target}")
    if target.is_dir():
        readme_candidate = target / "README.md"
        if readme_candidate.exists():
            return (url, "directory", f"链接到目录而非文件（应链接到 {target.name}/README.md）: {target}")
        return (url, "directory", f"链接到目录而非文件（目录内无README.md）: {target}")
    return (url, "ok", "")


def _extract_paths_from_value(value: str) -> list[str]:
    """从字符串值中提取潜在的文件路径。

    处理多种source字段格式：
      - 单个路径: "path/to/file.md"
      - 路径+锚点: "path/to/file.md#section"
      - 多路径分隔: "path1.md + path2.md" 或 "path1.md, path2.md"
      - 路径+描述（旧格式）: "path/to/file.md + 复盘洞察 + 实践验证"（只提取路径部分）

    返回提取到的路径字符串列表。
    """
    if not value or not isinstance(value, str):
        return []
    v = value.strip().strip('"').strip("'")
    if not v:
        return []
    parts = re.split(r'\s*[+|,;]\s*', v)
    paths = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part.startswith(('http://', 'https://', '#', 'mailto:', 'session:', 'external:', 'spec:')):
            continue
        if '{{' in part or '}}' in part:
            continue
        if CURLY_PLACEHOLDER_RE.search(part):
            continue
        if re.search(r'[\u4e00-\u9fff]', part) and not ('.md' in part or '.toml' in part or '.py' in part):
            continue
        if '/' in part or '\\' in part or part.startswith('../') or part.startswith('./'):
            paths.append(part)
        elif re.search(r'\.(md|toml|py|js|ts|json|yaml|yml|sh|ps1)$', part, re.IGNORECASE):
            paths.append(part)
    return paths


def _is_path_value(value: str) -> bool:
    """判断字符串值是否包含需要验证的文件路径（向后兼容，使用_extract_paths_from_value）。"""
    return len(_extract_paths_from_value(value)) > 0


def _normalize_path_value(value: str) -> str:
    """清理路径值，去除引号和首尾空白。"""
    return value.strip().strip('"').strip("'")


def _check_single_path(md_path: Path, field_name: str, path_value: str) -> tuple[Path, str, str, str] | None:
    """检查单个路径值是否有效。返回 (md_path, field_name, path_value, error_message) 或 None（通过）。"""
    v = _normalize_path_value(path_value)
    if not v:
        return None
    if v.startswith('docs/'):
        return (md_path, field_name, v, f"格式问题: 路径使用docs/绝对路径前缀，应使用相对路径")
    clean_path = v.split('#')[0]
    if not clean_path:
        return None
    target = (md_path.parent / clean_path).resolve()
    if not target.exists():
        return (md_path, field_name, v, f"文件不存在: {target}")
    if target.is_dir():
        readme_candidate = target / "README.md"
        if readme_candidate.exists():
            return (md_path, field_name, v, f"链接到目录而非文件（应指向{target.name}/README.md）: {target}")
        return (md_path, field_name, v, f"链接到目录而非文件（目录内无README.md）: {target}")
    return None


def check_frontmatter_paths(
    md_files: list[Path],
    fields: list[str] | None = None,
    check_related_fields: bool = True,
) -> list[tuple[Path, str, str, str]]:
    """校验 Markdown 文件 frontmatter 中包含路径的字段是否指向有效文件。

    通用的 frontmatter 路径检查机制，支持：
      - 显式指定的字段列表（默认: source, x-toml-ref）
      - 自动检测 related_ 前缀的字段（related_insights, related_patterns, parent_retrospective 等）
      - 字符串值和列表值（如 source: ["a.md", "b.md"]）
      - 多路径字符串（用 +、|、,、; 分隔的多个路径）
      - 路径+描述混合文本（如 "path/to/file.md + 复盘洞察"）
      - 自动跳过非路径值（URL、session:引用、占位符、纯ID、中文描述等）
      - 格式问题检测（docs/前缀绝对路径）

    返回:
      问题列表 [(md_path, field_name, path_value, error_message), ...]
    """
    from lib.frontmatter import parse_frontmatter_unified

    if fields is None:
        fields = ['source', 'x-toml-ref']

    broken = []
    for md_path in md_files:
        meta = parse_frontmatter_unified(md_path)
        if not meta:
            continue
        for field_name, value in meta.items():
            is_target_field = field_name in fields
            is_related_field = check_related_fields and field_name.startswith('related_')
            if not is_target_field and not is_related_field:
                continue
            values_to_check: list[str] = []
            if isinstance(value, str):
                values_to_check.extend(_extract_paths_from_value(value))
            elif isinstance(value, list):
                for v in value:
                    values_to_check.extend(_extract_paths_from_value(str(v)))
            for v in values_to_check:
                result = _check_single_path(md_path, field_name, v)
                if result:
                    broken.append(result)
    return broken


# ===== frontmatter 路径自动修复（--fix --check-frontmatter-paths）=====


@dataclass
class FrontmatterFix:
    """记录一次 frontmatter 路径字段的修复操作。"""
    file_path: Path
    field_name: str
    old_value: str
    new_value: str
    fix_type: str  # 'docs_prefix' | 'path_depth'
    reason: str = ""


def _relpath_posix(from_dir: Path, to_path: Path) -> str:
    """计算从 from_dir 到 to_path 的相对路径，输出 POSIX 格式（/ 分隔，含 ../）。"""
    rel = os.path.relpath(str(to_path.resolve()), str(from_dir.resolve()))
    return rel.replace("\\", "/")


def _classify_path_issue(error: str) -> str:
    """根据 _check_single_path 返回的错误信息分类问题类型。"""
    if "docs/绝对路径前缀" in error or "docs/前缀" in error:
        return "docs_prefix"
    if "文件不存在" in error:
        return "missing_file"
    if "链接到目录而非文件" in error:
        return "directory_link"
    return "unknown"


def _replace_path_in_text(text: str, old: str, new: str) -> str:
    """安全替换 frontmatter 文本中的路径字符串。

    使用正则前瞻断言确保只匹配完整路径（后跟锚点、引号、空白、列表结束符、
    分隔符或行尾），避免子串误伤（如 "../../foo.md" 误伤 "../../foo.md#section"
    或 "../foo.md.bak"）。

    自动处理 YAML 双引号字符串的转义：路径值在 YAML 双引号字符串中可能被转义
    （如 "d:\\\\AI\\\\docs\\\\..." 实际值为 "d:\\AI\\docs\\..."），
    因此同时尝试原始字符串和反斜杠转义后的字符串两种形式。
    """
    new_text = text

    # 尝试原始形式和 YAML 转义形式（\ → \\）
    candidates = [old]
    escaped_form = old.replace("\\", "\\\\")
    if escaped_form != old:
        candidates.append(escaped_form)

    for candidate in candidates:
        escaped_pattern = re.escape(candidate)
        pattern = escaped_pattern + r'(?=[#"\'\s\]\),|+;]|$)'
        new_text = re.sub(pattern, lambda m: new, new_text)

    return new_text


# 通用路径段集合：在路径关键词匹配验证中视为"无区分性"，跳过
_GENERIC_PATH_PARTS = {
    # 顶级目录
    "docs", "retrospective", "reports", "patterns", "assets",
    "knowledge", "operations", "methodology-patterns",
    # 报告分类目录
    "competitive-analysis", "project-reports", "task-reports",
    "insight-extraction", "external-learning", "tools-and-automation",
    "project-governance", "knowledge-content",
    # 模式分类目录
    "ai-collaboration", "spec-workflow", "tools-automation",
    "document-architecture", "product-growth",
    # 通用文件名（去 .md 后缀）
    "README", "index", "insight-extraction",
    "execution-retrospective", "retrospective-report",
    "export-suggestions", "insight-action-backlog",
    # 通用代码目录
    "skills", "libs", "src", "tests", "scripts",
    "actions", "insights",
    # 跨项目可能出现的顶级目录
    "AI", ".chaos",
    # 其他
    "SKILL", "SKILL.md",
}


def _verify_path_candidate(original_path: str, candidate: Path) -> bool:
    """验证搜索到的候选目标是否与原路径匹配。

    通过检查候选路径是否包含原路径的"有区分性"关键词，避免误匹配到同名
    但内容不同的文件（如多个 insight-extraction.md、多个 SKILL.md）。

    Args:
        original_path: 原始路径字符串（已解析的 YAML 值，单反斜杠）。
        candidate: find_target_by_stem 找到的候选目标。

    Returns:
        True 表示候选可信可修复，False 表示应跳过（避免误修）。
    """
    # 规范化为正斜杠，合并双反斜杠（YAML 转义残留）
    normalized = original_path.replace("\\\\", "/").replace("\\", "/")
    parts = [p for p in normalized.split("/") if p and p not in (".", "..")]
    if not parts:
        return True  # 原路径无有效段，信任 finder 评分

    # 提取有区分性的部分（跳过通用目录名、通用文件名、盘符、纯数字）
    distinctive_parts: list[str] = []
    for part in parts:
        stem = part[:-3] if part.endswith(".md") else part
        if stem in _GENERIC_PATH_PARTS or part in _GENERIC_PATH_PARTS:
            continue
        if part.isdigit() or stem.isdigit():
            continue
        if re.match(r"^[a-zA-Z]:$", part):  # 盘符如 d:
            continue
        distinctive_parts.append(part.lower())

    if not distinctive_parts:
        return True  # 原路径全是通用段，无法验证，信任 finder

    # 候选路径必须包含至少一个有区分性的部分
    candidate_str = str(candidate).lower().replace("\\", "/")
    for dp in distinctive_parts:
        if dp in candidate_str:
            return True

    return False


def _compute_frontmatter_fix(
    md_path: Path,
    old_path: str,
    project_root: Path,
    issue_type: str,
) -> str | None:
    """计算 frontmatter 路径字段的修复值。

    策略：
    - docs_prefix：将 docs/前缀路径解析为 (project_root / docs/...) 后计算相对路径
      若目标不存在，则降级为 find_target_by_stem 搜索 + 候选验证
    - directory_link：链接指向目录，若目录内有README.md则改为指向README.md
    - missing_file（路径深度错误或文件名变化）：用 find_target_by_stem 搜索目标，
      但必须通过候选验证（候选路径必须包含原路径的有区分性关键词）

    保留锚点（#section）。

    Args:
        md_path: 当前 Markdown 文件路径。
        old_path: 原始路径值（已解析的 YAML 值）。
        project_root: 项目根目录。
        issue_type: 问题类型（'docs_prefix' / 'missing_file' / 'directory_link' / 'unknown'）。

    Returns:
        修复后的路径字符串，或 None（无法安全修复时）。
    """
    from lib.link_fixer.finder import find_target_by_stem

    # 分离锚点
    anchor = ""
    clean_path = old_path
    if "#" in old_path:
        clean_path, anchor_part = old_path.split("#", 1)
        anchor = "#" + anchor_part

    # 处理 docs/ 前缀：直接从项目根解析（100% 安全的修复）
    if issue_type == "docs_prefix" and clean_path.startswith("docs/"):
        target = (project_root / clean_path).resolve()
        if target.exists():
            return _relpath_posix(md_path.parent, target) + anchor

    # 处理目录链接：若目录内有README.md，改为指向README.md
    if issue_type == "directory_link":
        dir_target = (md_path.parent / clean_path.rstrip("/")).resolve()
        readme_target = dir_target / "README.md"
        if readme_target.exists():
            base = clean_path.rstrip("/")
            return _relpath_posix(md_path.parent, readme_target) + anchor

    # 路径不存在：用文件名/目录名搜索目标
    target = find_target_by_stem(
        clean_path,
        project_root,
        near=md_path,
    )
    if target is None:
        return None

    # 候选验证：避免误匹配到同名但内容不同的文件
    if not _verify_path_candidate(clean_path, target):
        return None

    return _relpath_posix(md_path.parent, target) + anchor


def fix_frontmatter_paths(
    md_files: list[Path],
    project_root: Path,
    dry_run: bool = False,
) -> list[FrontmatterFix]:
    """修复 Markdown 文件 frontmatter 中的路径字段。

    可修复两类问题：
    - docs/ 前缀：转换为正确的相对路径（从 md_path.parent 到 project_root/docs/... 的相对路径）
    - 路径深度错误：通过 find_target_by_stem 搜索目标后计算正确相对路径

    不可修复的问题（跳过）：
    - x-toml-ref 指向不存在的 TOML 文件（需手动创建 TOML）
    - 搜索不到任何候选目标的路径

    修复范围仅限于 frontmatter 区域（--- ... --- 或 +++ ... +++ 之间），
    不影响正文中的链接。

    Args:
        md_files: 待修复的 Markdown 文件列表。
        project_root: 项目根目录（用于解析 docs/ 前缀路径和搜索目标文件）。
        dry_run: True=仅预览不写入文件，False=实际写入修复后的内容。

    Returns:
        修复记录列表，每条记录包含文件路径、字段名、原值、新值、修复类型。
    """
    from lib.frontmatter import (
        _YAML_FRONTMATTER_RE,
        _FRONTMATTER_RE,
        parse_frontmatter_unified,
    )

    target_fields = ["source", "x-toml-ref"]
    fixes: list[FrontmatterFix] = []

    for md_path in md_files:
        try:
            content = md_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        # 定位 frontmatter 文本范围（仅修复 frontmatter 内的路径）
        yaml_match = _YAML_FRONTMATTER_RE.match(content)
        toml_match = _FRONTMATTER_RE.match(content) if not yaml_match else None

        if yaml_match:
            fm_start = yaml_match.start(1)
            fm_end = yaml_match.end(1)
            fm_text = yaml_match.group(1)
        elif toml_match:
            fm_start = toml_match.start(1)
            fm_end = toml_match.end(1)
            fm_text = toml_match.group(1)
        else:
            continue

        # 解析合并后的元数据（含 x-toml-ref 加载的 TOML 字段）
        meta = parse_frontmatter_unified(md_path)
        if not meta:
            continue

        # 解析外部 TOML 文件路径（用于修复 TOML 中的 source 字段）
        toml_path: Path | None = None
        x_toml_ref_val = meta.get("x-toml-ref")
        if x_toml_ref_val and isinstance(x_toml_ref_val, str):
            toml_ref_clean = x_toml_ref_val.split("#")[0]
            resolved = (md_path.parent / toml_ref_clean).resolve()
            if resolved.exists():
                toml_path = resolved

        # 收集本文件所有需要修复的路径（field, old_value, new_value, fix_type, reason）
        file_fixes: list[tuple[str, str, str, str, str]] = []

        for field_name, value in meta.items():
            is_target = field_name in target_fields
            is_related = field_name.startswith("related_")
            if not is_target and not is_related:
                continue

            values_to_check: list[str] = []
            if isinstance(value, str):
                values_to_check.extend(_extract_paths_from_value(value))
            elif isinstance(value, list):
                for v in value:
                    values_to_check.extend(_extract_paths_from_value(str(v)))

            for v in values_to_check:
                result = _check_single_path(md_path, field_name, v)
                if not result:
                    continue  # 路径有效，跳过

                _, _, path_value, error = result
                issue_type = _classify_path_issue(error)

                # 跳过不可修复问题：x-toml-ref 指向不存在的 TOML 文件
                if field_name == "x-toml-ref" and issue_type == "missing_file":
                    continue

                new_path = _compute_frontmatter_fix(
                    md_path, path_value, project_root, issue_type
                )
                if new_path and new_path != path_value:
                    file_fixes.append((
                        field_name,
                        path_value,
                        new_path,
                        issue_type,
                        error.split(":")[0] if ":" in error else error,
                    ))

        if not file_fixes:
            continue

        # 在 frontmatter 文本范围内执行安全替换，并记录每条修复是否在 YAML 中生效
        new_fm_text = fm_text
        yaml_applied: list[bool] = []
        for field, old_v, new_v, fix_type, reason in file_fixes:
            before = new_fm_text
            new_fm_text = _replace_path_in_text(new_fm_text, old_v, new_v)
            yaml_applied.append(new_fm_text != before)

        # 重组文件内容（保留 frontmatter 标记 ---/+++）
        new_content = content[:fm_start] + new_fm_text + content[fm_end:]

        if not dry_run and new_content != content:
            md_path.write_text(new_content, encoding="utf-8", newline="")

        # 修复外部 TOML 文件中的路径（YAML 中未找到的字段回退写入 TOML）
        toml_pending = [
            (i, file_fixes[i])
            for i, applied in enumerate(yaml_applied)
            if not applied
        ]
        if toml_pending and toml_path and not dry_run:
            try:
                toml_content = toml_path.read_text(encoding="utf-8")
                new_toml_content = toml_content
                for _, (field, old_v, new_v, fix_type, reason) in toml_pending:
                    new_toml_content = _replace_path_in_text(
                        new_toml_content, old_v, new_v
                    )
                if new_toml_content != toml_content:
                    toml_path.write_text(
                        new_toml_content, encoding="utf-8", newline=""
                    )
            except (OSError, UnicodeDecodeError):
                pass

        for field, old_v, new_v, fix_type, reason in file_fixes:
            fixes.append(FrontmatterFix(
                file_path=md_path,
                field_name=field,
                old_value=old_v,
                new_value=new_v,
                fix_type=fix_type,
                reason=reason,
            ))

    return fixes


def print_frontmatter_fix_report(fixes: list[FrontmatterFix], dry_run: bool = False) -> None:
    """打印 frontmatter 路径修复报告。"""
    mode = "预览" if dry_run else "已修复"
    print(f"\n  frontmatter 路径修复（{mode}）: 共 {len(fixes)} 处")

    # 按文件分组统计
    by_file: dict[Path, list[FrontmatterFix]] = {}
    for fix in fixes:
        by_file.setdefault(fix.file_path, []).append(fix)

    # 按修复类型统计
    type_counts: dict[str, int] = {}
    for fix in fixes:
        type_counts[fix.fix_type] = type_counts.get(fix.fix_type, 0) + 1

    type_labels = {
        "docs_prefix": "docs/前缀转换",
        "path_depth": "路径深度校正",
        "missing_file": "路径深度校正",
        "directory_link": "目录→README.md",
        "unknown": "未知类型",
    }
    type_summary = ", ".join(
        f"{type_labels.get(t, t)}={c}" for t, c in type_counts.items()
    )
    print(f"  修复类型分布: {type_summary}")

    # 每个文件打印前 5 条修复，超出折叠
    for file_path, file_fixes in by_file.items():
        print(f"\n  [{file_path}] ({len(file_fixes)} 处)")
        for fix in file_fixes[:5]:
            print(f"    {fix.field_name}: {fix.old_value}")
            print(f"      → {fix.new_value}  ({fix.fix_type})")
        if len(file_fixes) > 5:
            print(f"    ... 其余 {len(file_fixes) - 5} 处省略")


def main(argv=None) -> int:
    setup_safe_output()
    parser = argparse.ArgumentParser(
        description="扫描 Markdown 文件中的链接，校验外部 URL 可达性与本地文件引用有效性。"
    )
    add_common_args(parser)
    parser.add_argument(
        "--paths",
        type=Path,
        nargs="+",
        default=None,
        help="指定多个目标目录（与 --path 互斥，支持批量扫描多个目录）",
    )
    parser.add_argument(
        "--check-external",
        action="store_true",
        default=False,
        help="同时检查外部 HTTP/HTTPS 链接（默认仅检查本地文件引用）",
    )
    parser.add_argument(
        "--check-frontmatter-paths",
        action="store_true",
        default=False,
        help="校验 frontmatter 中所有路径字段（source, x-toml-ref, related_*等）的有效性（推荐）",
    )
    parser.add_argument(
        "--check-x-toml-ref",
        action="store_true",
        default=False,
        help="[已废弃] 请使用 --check-frontmatter-paths，功能更全面",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=LINK_CHECK_TIMEOUT,
        help="外部链接检查超时秒数（默认 10 秒）",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=LINK_CHECK_WORKERS,
        help="并发检查外部链接的线程数（默认 5）",
    )
    parser.add_argument(
        "--exclude",
        type=str,
        nargs="*",
        default=LINK_CHECK_EXCLUDE_DIRS,
        help="额外排除的目录名称（默认排除 docs/templates）",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        default=False,
        help="自动修复可修复的断链（绝对路径转相对路径、相对路径层级校正、目录斜杠补全等）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="与 --fix 配合使用，仅预览修复内容不写入文件",
    )
    parser.add_argument(
        "--rename",
        type=str,
        nargs="*",
        default=[],
        metavar="OLD=NEW",
        help="文件名重命名映射（用于文件迁移后修复引用），如 --rename 旧名.html=新名.html",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        default=False,
        help="外部链接检查时不使用缓存，强制重新请求所有 URL",
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        default=False,
        help="清除外部链接检查缓存后退出",
    )
    parser.add_argument(
        "--cache-ttl",
        type=int,
        default=CACHE_TTL_DAYS,
        help=f"外部链接缓存有效期天数（默认 {CACHE_TTL_DAYS} 天）",
    )
    args = parser.parse_args(argv)

    project_root = resolve_project_root(__file__)
    if args.paths and args.path:
        print("错误: --paths 与 --path 互斥，请仅使用其中一个", file=sys.stderr)
        return 1
    if args.paths:
        roots = list(args.paths)
    elif args.path:
        roots = [args.path]
    else:
        roots = [project_root]
    for r in roots:
        if not r.exists():
            print(f"错误: 路径不存在: {r}", file=sys.stderr)
            return 1

    if args.clear_cache:
        cache_path = _get_cache_path(project_root)
        if cache_path.exists():
            cache_path.unlink()
            print(f"已清除外部链接缓存: {cache_path}")
        else:
            print("无外部链接缓存文件，无需清除")
        return 0

    exclude_dirs = set(args.exclude)
    print("=" * 60)
    print("Markdown 链接校验")
    print("=" * 60)

    # 查找 Markdown 文件（支持多目录扫描）
    md_files = []
    file_root_map = {}  # 文件 -> 其所属扫描根目录（用于相对路径显示）
    for root in roots:
        print(f"\n扫描目录: {root}")
        if exclude_dirs:
            print(f"排除目录: {', '.join(sorted(exclude_dirs))}")
        root_md_files = find_markdown_files(root, exclude_dirs)
        print(f"找到 {len(root_md_files)} 个 Markdown 文件")
        for md_file in root_md_files:
            resolved = md_file.resolve()
            if resolved not in file_root_map:
                file_root_map[resolved] = root
                md_files.append(md_file)
    print(f"\n合计: {len(md_files)} 个 Markdown 文件（已去重）")

    # 自动修复（--fix）
    rename_map = {}
    for mapping in args.rename:
        if "=" in mapping:
            old, new = mapping.split("=", 1)
            rename_map[old] = new

    if args.fix:
        from lib.link_fixer import fix_directory_links, print_fix_report, _infer_project_root
        dry_run = args.dry_run
        mode_str = "预览修复（dry-run）" if dry_run else "自动修复"
        print(f"\n0. {mode_str}...")
        for root in roots:
            inferred_root = _infer_project_root(root)
            fixes = fix_directory_links(
                root, inferred_root,
                rename_map=rename_map or None,
                dry_run=dry_run,
                exclude_dirs=exclude_dirs,
            )
            if fixes:
                print_fix_report(fixes, dry_run=dry_run)
            else:
                print(f"  {root}: 未发现需要修复的断链。")

        # frontmatter 路径字段自动修复（需配合 --check-frontmatter-paths 触发）
        if args.check_frontmatter_paths or args.check_x_toml_ref:
            print(f"\n0.1 {mode_str} frontmatter 路径字段...")
            inferred_root = _infer_project_root(roots[0]) if roots else project_root
            fm_fixes = fix_frontmatter_paths(md_files, inferred_root, dry_run=dry_run)
            if fm_fixes:
                print_frontmatter_fix_report(fm_fixes, dry_run=dry_run)
            else:
                print("  未发现可自动修复的 frontmatter 路径问题。")

    # 解析所有链接
    all_links: list[tuple[Path, str, str, int]] = []  # (文件, 文本, URL, 行号)
    for md_file in md_files:
        links = parse_links(md_file)
        for text, url, line_num in links:
            all_links.append((md_file, text, url, line_num))

    # 分类链接
    external_links = [(f, t, u, ln) for f, t, u, ln in all_links if is_external_url(u)]
    local_links = [(f, t, u, ln) for f, t, u, ln in all_links if is_local_ref(u)]
    other_links = [(f, t, u, ln) for f, t, u, ln in all_links if not is_external_url(u) and not is_local_ref(u)]

    print(f"  内联链接: {len(all_links)}")
    print(f"  外部链接: {len(external_links)}")
    print(f"  本地引用: {len(local_links)}")
    print(f"  其他链接: {len(other_links)}（锚点/mailto 等）")

    # 检查本地文件引用
    broken_local = []
    warning_local = []
    print(f"\n1. 检查本地文件引用（共 {len(local_links)} 个）...")
    for file_path, text, url, line_num in local_links:
        url_str, status, message = check_local_link(file_path, url)
        if status == "missing":
            file_root = file_root_map.get(file_path.resolve(), roots[0])
            rel_path = file_path.relative_to(file_root) if file_root in file_path.parents else file_path
            broken_local.append((rel_path, line_num, text, url_str, message))
        elif status == "directory":
            file_root = file_root_map.get(file_path.resolve(), roots[0])
            rel_path = file_path.relative_to(file_root) if file_root in file_path.parents else file_path
            warning_local.append((rel_path, line_num, text, url_str, message))

    if broken_local:
        print(f"   失败: {len(broken_local)} 个断链")
        for rel_path, line_num, text, url, error in broken_local:
            print(f"     [{rel_path}:{line_num}] {text} -> {url} ({error})")
    else:
        print(f"   通过: 所有本地引用均存在")

    if warning_local:
        print(f"   警告: {len(warning_local)} 个链接指向目录（IDE无法直接打开，建议链接到README.md）")
        for rel_path, line_num, text, url, msg in warning_local:
            print(f"     [{rel_path}:{line_num}] {text} -> {url} ({msg})")

    # 检查外部链接（可选）
    broken_external = []
    cached_results = {}
    urls_to_check = set()

    if args.check_external and external_links:
        unique_urls = set(u for _, _, u, _ in external_links)
        print(f"\n2. 检查外部链接（共 {len(unique_urls)} 个唯一 URL，超时 {args.timeout}s）...")

        cache = load_cache(project_root) if not args.no_cache else {}
        cache.pop("_metadata", None)

        for url in unique_urls:
            entry = cache.get(url)
            if entry and is_cache_valid(entry, args.cache_ttl) and not args.no_cache:
                cached_results[url] = (entry.get("status", 0), entry.get("error", ""))
            else:
                urls_to_check.add(url)

        cached_count = len(cached_results)
        if cached_count > 0:
            print(f"   使用缓存结果: {cached_count} 个（TTL {args.cache_ttl} 天），需重新检查: {len(urls_to_check)} 个")

        url_results = dict(cached_results)
        if urls_to_check:
            with ThreadPoolExecutor(max_workers=args.workers) as executor:
                futures = {executor.submit(check_external_link, url, args.timeout): url for url in urls_to_check}
                for future in as_completed(futures):
                    url, status, error = future.result()
                    url_results[url] = (status, error)
                    cache[url] = {
                        "status": status,
                        "error": error,
                        "checked_at": datetime.now().isoformat(),
                        "ok": status > 0 and (status < 400 or status in (403, 405)),
                    }

            if not args.no_cache:
                save_cache(project_root, cache)

        for file_path, text, url, line_num in external_links:
            status, error = url_results.get(url, (0, "未检查"))
            if status == 0 or (status >= 400 and status not in (403, 405, 401)):
                file_root = file_root_map.get(file_path.resolve(), roots[0])
                rel_path = file_path.relative_to(file_root) if file_root in file_path.parents else file_path
                broken_external.append((rel_path, line_num, text, url, status, error))

        if broken_external:
            ok_count = len(unique_urls) - len(set(u for _, _, u, _, _, _ in broken_external))
            print(f"   可达: {ok_count}，不可达: {len(broken_external)}")
            for rel_path, line_num, text, url, status, error in broken_external:
                print(f"     [{rel_path}:{line_num}] {text} -> {url} (HTTP {status}: {error})")
        else:
            print(f"   通过: 所有外部链接均可达")
    elif not args.check_external:
        print(f"\n2. 跳过外部链接检查（使用 --check-external 启用）")
        print(f"   共 {len(external_links)} 个外部链接待检查")

    # 检查 frontmatter 路径字段
    broken_frontmatter = []
    check_fm = args.check_frontmatter_paths or args.check_x_toml_ref
    if check_fm:
        print(f"\n3. 检查 frontmatter 路径字段有效性（共 {len(md_files)} 个文件）...")
        if args.check_x_toml_ref and not args.check_frontmatter_paths:
            print("   注意: --check-x-toml-ref 已废弃，自动升级为 --check-frontmatter-paths（检查source/x-toml-ref/related_*等所有路径字段）")
        broken_frontmatter = check_frontmatter_paths(md_files)
        if broken_frontmatter:
            print(f"   失败: {len(broken_frontmatter)} 个 frontmatter 路径问题")
            for md_path, field_name, ref, error in broken_frontmatter:
                file_root = file_root_map.get(md_path.resolve(), roots[0])
                try:
                    rel_path = md_path.relative_to(file_root) if file_root in file_root_map and file_root in md_path.parents else md_path
                except ValueError:
                    rel_path = md_path
                print(f"     [{rel_path}] {field_name}: {ref} ({error})")
        else:
            print(f"   通过: 所有 frontmatter 路径字段均有效")

    # JSON 输出
    if args.json:
        result = {
            "summary": {
                "total_files": len(md_files),
                "total_links": len(all_links),
                "external_links": len(external_links),
                "local_links": len(local_links),
                "other_links": len(other_links),
                "broken_local": len(broken_local),
                "warning_local": len(warning_local),
                "broken_external": len(broken_external),
                "broken_frontmatter": len(broken_frontmatter),
            },
            "broken_local": [
                {
                    "file": str(f),
                    "line": ln,
                    "text": t,
                    "url": u,
                    "error": e,
                }
                for f, ln, t, u, e in broken_local
            ],
            "warning_local": [
                {
                    "file": str(f),
                    "line": ln,
                    "text": t,
                    "url": u,
                    "warning": w,
                }
                for f, ln, t, u, w in warning_local
            ],
            "broken_external": [
                {
                    "file": str(f),
                    "line": ln,
                    "text": t,
                    "url": u,
                    "status": s,
                    "error": e,
                }
                for f, ln, t, u, s, e in broken_external
            ],
            "broken_frontmatter": [
                {
                    "file": str(f),
                    "field": field,
                    "value": v,
                    "error": e,
                }
                for f, field, v, e in broken_frontmatter
            ],
        }
        print("\n" + json.dumps(result, ensure_ascii=False, indent=2))

    # 汇总
    print("\n" + "=" * 60)
    total_broken = len(broken_local) + len(broken_external) + len(broken_frontmatter)
    total_warnings = len(warning_local)
    if total_broken == 0:
        if total_warnings == 0:
            print("校验通过: 所有链接均有效")
        else:
            print(f"校验通过（有 {total_warnings} 个警告）: 无断链，但存在目录链接建议修复")
        print("=" * 60)
        return 0
    else:
        parts = [f"本地 {len(broken_local)}", f"外部 {len(broken_external)}"]
        if check_fm:
            parts.append(f"frontmatter {len(broken_frontmatter)}")
        if total_warnings > 0:
            parts.append(f"目录链接警告 {total_warnings}")
        print(f"校验失败: 发现 {total_broken} 个断链（{', '.join(parts)}）")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())