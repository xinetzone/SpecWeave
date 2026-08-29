#!/usr/bin/env python3
"""信源引用稳定性扫描（Source Path Stability Gate，GATE-SPS）。

信源稳定性门模式（source-stability-gate）第四步/第五步的工具化实现，
针对反模式"扫描只匹配链接语法"：以路径特征段（.chaos/.tmp/Temp/.cache）
为锚点，覆盖三类引用载体 × 两种斜杠（/ 与 \\）：

  载体1 link        —— Markdown 链接 [text](url) 与自动链接 <...>（含 file:///）
  载体2 frontmatter —— YAML/TOML frontmatter 中的裸路径值
  载体3 prose       —— 正文反引号/裸文本中的绝对路径声明

两种模式：
  audit（默认）   扫描文档中的路径引用，按稳定性分类
                  （temporary / stable / env-bound / relative），
                  并对可解析路径执行存在性复验（Test-Path）。
                  命中 temporary 引用或路径不存在 → 退出码 1。
  --target <目录> 清理前扫描：为待删除目录构建特征签名正则（斜杠双向兼容），
                  报告全部引用位置（任一载体、任一文件类型）。
                  存在引用 → 退出码 1（阻断删除）；零引用 → 0（放行）。

用法：
  python .agents/scripts/check-source-path-stability.py
  python .agents/scripts/check-source-path-stability.py --path bundles/
  python .agents/scripts/check-source-path-stability.py --target .chaos/libs/veadk-python
  python .agents/scripts/check-source-path-stability.py --json

说明：audit 模式全仓扫描时，复盘报告/spec 等历史记录中的时点路径
（事实表、证据表）属预期命中，需按"历史记录 vs 活动引用"判据人工分流，
工具职责是零漏报，不替代语义裁决。

扫描范围：仅持久工作区（docs/、.agents/、.trae/specs/ 等）；
.chaos/、vendor/、.temp/ 与缓存目录在目录级剪枝、不下钻——
临时克隆之间的互引是临时→临时引用，不构成删除阻断。

退出码：0 通过/放行；1 发现命中（门禁拦截）；2 参数错误。
"""

# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import unquote

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import add_common_args  # noqa: E402
from lib.project import resolve_project_root  # noqa: E402

GATE = "GATE-SPS"

# ---------------------------------------------------------------------------
# 稳定性分类特征
# ---------------------------------------------------------------------------
# 临时信源路径段（精确匹配路径分段，小写比较）
TEMP_SEGMENTS = {".chaos", ".tmp", "tmp", ".cache", "temp", "cache-tmp"}
# 临时信源子串特征（归一化为小写正斜杠后匹配）
TEMP_SUBSTRINGS = (
    "appdata/local/temp",
    "/var/folders/",
    "/tmp/",
    ".trae/cache",
    ".agents/cache",
)
# 稳定信源路径段
STABLE_SEGMENTS = {"vendor", "site-packages"}
# 稳定信源子串特征
STABLE_SUBSTRINGS = ("program files", "/usr/", "/usr/local/", "/opt/")

# ---------------------------------------------------------------------------
# 路径提取正则（三类载体 × 两种斜杠）
# ---------------------------------------------------------------------------
# file:/// URL（正斜杠为主，允许反斜杠）
FILE_URL_RE = re.compile(r"file:///[^\s)>\]\"'|`]+")
# Windows 盘符路径：d:/... 或 d:\...；负向后顾防止匹配 https:// 中的 "s:/"
DRIVE_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/][^\s)>\]\"'|`]*")
# 反引号内联代码（prose 载体的主要形态）
BACKTICK_RE = re.compile(r"`([^`\n]{2,})`")
# Markdown 链接与自动链接（link 载体判定）
INLINE_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
AUTOLINK_RE = re.compile(r"<(file:///[^>\s]+)>")
# frontmatter 键值行
FRONTMATTER_KEY_RE = re.compile(r"^\s*[A-Za-z_][\w.-]*\s*[:=]")
# frontmatter 值提取（支持引号包裹与裸值）
FRONTMATTER_VALUE_RE = re.compile(r"""[:=]\s*(?:"([^"\n]*)"|'([^'\n]*)'|([^\n#]+))""")
# frontmatter YAML 列表项裸值行（如 "  - .chaos/libs/foo"；映射项 "- key: v" 含冒号走键值逻辑）
FRONTMATTER_LIST_ITEM_RE = re.compile(r"^\s*-\s+(.+?)\s*$")

# 清理前扫描的文本文件扩展名（比 audit 更宽，脚本中的硬编码路径也是活动引用）
CLEANUP_EXTENSIONS = {
    ".md", ".py", ".ps1", ".sh", ".toml", ".yaml", ".yml",
    ".txt", ".json", ".cfg", ".ini", ".bat", ".cmd",
}
# 排除目录：单段名直接匹配；多段名（如 ".trae/cache"）按相对前缀匹配。
# .chaos 为临时工作区（gitignore）：克隆之间的互引是临时→临时引用，
# 不构成对持久工作区的删除阻断；且克隆体积巨大（数百 MB 源码），
# 下钻扫描会导致清理前扫描耗时放大一个数量级。
DEFAULT_EXCLUDED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv",
    "__pycache__", ".idea", ".vscode", ".tox", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", "dist", "build", "target",
    ".trae/cache", ".agents/cache", "vendor", ".temp", ".chaos",
}

_TRAILING_PUNCT = ".,;:)]}'\""


@dataclass
class Finding:
    """单条路径引用命中。"""

    file: str
    line: int
    col: int
    token: str
    form: str          # link / frontmatter / prose
    stability: str     # temporary / stable / env-bound / relative / unknown
    exists: Optional[bool]  # True/False/None（不可解析时不检查）
    in_code_block: bool


# ---------------------------------------------------------------------------
# 归一化与分类
# ---------------------------------------------------------------------------
def normalize_token(token: str) -> str:
    """剥离 URL 前缀、片段锚点与尾随标点，得到可比的路径字符串。"""
    t = token.strip()
    if t.startswith("file:///"):
        rest = unquote(t[len("file:///"):])
        # file:///d:/... → d:/...（Windows）；file:///home/... → /home/...（POSIX）
        if re.match(r"^[A-Za-z]:[\\/]", rest):
            t = rest
        else:
            t = "/" + rest
    # 剥离片段锚点（如 #L10-L20、#章节）：文件系统路径不含锚点，
    # 否则带行号锚点的链接存在性复验会全部误报为不存在
    t = t.split("#", 1)[0]
    return t.rstrip(_TRAILING_PUNCT).rstrip("\\/")


def _norm_slash(path_str: str) -> str:
    return path_str.replace("\\", "/").lower()


def classify_stability(token: str) -> str:
    """按路径特征段分类稳定性：temporary / stable / env-bound / relative。"""
    norm = _norm_slash(token)
    segments = [s for s in re.split(r"[\\/]", token) if s]
    seg_lower = {s.lower() for s in segments}
    if seg_lower & TEMP_SEGMENTS or any(sub in norm for sub in TEMP_SUBSTRINGS):
        return "temporary"
    if seg_lower & STABLE_SEGMENTS or any(sub in norm for sub in STABLE_SUBSTRINGS):
        return "stable"
    if DRIVE_RE.match(token) or token.startswith("/"):
        # 绝对路径但既非临时特征也非稳定特征：绑定开发者机器环境
        return "env-bound"
    return "relative"


def resolve_fs_path(token: str, project_root: Path) -> Optional[Path]:
    """把引用 token 解析为文件系统路径；不可靠解析时返回 None。"""
    t = normalize_token(token)
    if re.match(r"^[A-Za-z]:[\\/]", t):
        return Path(t)
    if t.startswith("/"):
        return Path(t)  # POSIX 绝对路径（Windows 上通常不存在，复验会标注）
    # 项目相对路径：仅对已知根段（.chaos/vendor/.temp 等）解析，避免误判
    first = t.split("/", 1)[0].split("\\", 1)[0].lower()
    if first in TEMP_SEGMENTS or first in STABLE_SEGMENTS:
        return (project_root / t.replace("\\", "/")).resolve()
    return None


def _is_path_like(text: str) -> bool:
    """反引号内容是否构成路径引用（含斜杠且具备盘符/临时段/稳定段特征）。"""
    if "/" not in text and "\\" not in text:
        return False
    if DRIVE_RE.search(text) or FILE_URL_RE.search(text):
        return True
    norm = _norm_slash(text)
    segments = {s.lower() for s in re.split(r"[\\/]", text) if s}
    if segments & TEMP_SEGMENTS or segments & STABLE_SEGMENTS:
        return True
    return any(sub in norm for sub in TEMP_SUBSTRINGS + STABLE_SUBSTRINGS)


# ---------------------------------------------------------------------------
# 文件扫描
# ---------------------------------------------------------------------------
def _is_excluded_dir(rel_parts: tuple[str, ...], dirname: str) -> bool:
    """目录是否命中排除规则：单段名命中，或多段相对前缀（.trae/cache）命中。"""
    if dirname in DEFAULT_EXCLUDED_DIRS:
        return True
    return "/".join(rel_parts + (dirname,)) in DEFAULT_EXCLUDED_DIRS


def _iter_text_files(root: Path, extensions: set[str]) -> Iterable[Path]:
    if root.is_file():
        if root.suffix.lower() in extensions:
            yield root
        return

    def _on_error(_exc: OSError) -> None:
        return None

    for dirpath, dirnames, filenames in os.walk(root, onerror=_on_error):
        # 目录级剪枝：原地修改 dirnames 阻止 os.walk 下钻排除目录
        rel = Path(dirpath).relative_to(root)
        rel_parts = () if str(rel) == "." else rel.parts
        dirnames[:] = sorted(
            d for d in dirnames if not _is_excluded_dir(rel_parts, d)
        )
        for fn in sorted(filenames):
            if Path(fn).suffix.lower() in extensions:
                yield Path(dirpath) / fn


def _line_regions(text: str) -> tuple[set[int], set[int]]:
    """返回 (frontmatter 行号集合, fenced code block 行号集合)。"""
    lines = text.splitlines()
    frontmatter_lines: set[int] = set()
    code_lines: set[int] = set()

    # frontmatter：文件首部 --- 或 +++ 围栏对
    if lines and lines[0].strip() in ("---", "+++"):
        marker = lines[0].strip()
        for i in range(1, len(lines)):
            if lines[i].strip() == marker:
                frontmatter_lines = set(range(1, i))  # 0-based，不含围栏行
                break

    # fenced code block：``` 或 ~~~
    fence_stack = 0
    fence_marker: Optional[str] = None
    for idx, raw in enumerate(lines):
        m = re.match(r"^(\s*)(```+|~~~+)", raw)
        if m:
            marker = m.group(2)
            char, length = marker[0], len(marker)
            if fence_stack == 0:
                fence_stack = 1
                fence_marker = char * length
                code_lines.add(idx)
            elif fence_marker and char == fence_marker[0] and length >= len(fence_marker):
                code_lines.add(idx)
                fence_stack = 0
                fence_marker = None
            continue
        if fence_stack > 0:
            code_lines.add(idx)
    return frontmatter_lines, code_lines


def _extract_tokens(line: str, in_frontmatter: bool = False) -> list[tuple[int, int, str]]:
    """提取一行中全部路径 token：(col_start, col_end, token)，去重重叠。"""
    spans: list[tuple[int, int, str]] = []
    for m in FILE_URL_RE.finditer(line):
        spans.append((m.start(), m.end(), m.group(0)))
    for m in DRIVE_RE.finditer(line):
        spans.append((m.start(), m.end(), m.group(0)))
    for m in BACKTICK_RE.finditer(line):
        inner = m.group(1)
        if _is_path_like(inner):
            # 定位 inner 在行内的实际列
            inner_start = m.start(1)
            for sub in DRIVE_RE.finditer(inner):
                spans.append((inner_start + sub.start(), inner_start + sub.end(), sub.group(0)))
            for sub in FILE_URL_RE.finditer(inner):
                spans.append((inner_start + sub.start(), inner_start + sub.end(), sub.group(0)))
            # 反引号内整体相对路径（如 vendor/foo 或 .chaos/libs/foo）
            if not DRIVE_RE.search(inner) and not FILE_URL_RE.search(inner):
                spans.append((m.start(1), m.end(1), inner.strip()))

    # frontmatter 裸值（无反引号/盘符的相对路径，如 source: "vendor/foo"）
    if in_frontmatter:
        for m in FRONTMATTER_VALUE_RE.finditer(line):
            value = next((g for g in m.groups() if g is not None), "").strip()
            if value and _is_path_like(value):
                start = m.start() + m.group(0).index(value)
                spans.append((start, start + len(value), value))
        # YAML 列表项裸值（如 "  - .chaos/libs/foo"）；含冒号/等号的映射项由键值逻辑处理，
        # 盘符路径已由 DRIVE_RE 覆盖，此处仅补裸相对路径
        m_list = FRONTMATTER_LIST_ITEM_RE.match(line)
        if m_list:
            list_val = m_list.group(1).strip().strip("\"'")
            if (
                list_val
                and ":" not in list_val
                and "=" not in list_val
                and _is_path_like(list_val)
            ):
                spans.append((m_list.start(1), m_list.end(1), list_val))

    # 去重重叠（保留最先命中的较长 span）
    spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))
    deduped: list[tuple[int, int, str]] = []
    for start, end, tok in spans:
        if deduped and start < deduped[-1][1]:
            continue
        deduped.append((start, end, tok))
    return deduped


def _classify_form(line: str, token: str, in_frontmatter: bool) -> str:
    if in_frontmatter and (
        FRONTMATTER_KEY_RE.match(line) or FRONTMATTER_LIST_ITEM_RE.match(line)
    ):
        return "frontmatter"
    for m in INLINE_LINK_RE.finditer(line):
        if token in m.group(1):
            return "link"
    for m in AUTOLINK_RE.finditer(line):
        if token in m.group(1):
            return "link"
    return "prose"


def scan_file(path: Path, project_root: Path) -> list[Finding]:
    """audit 模式：扫描单个文件，返回全部路径引用 Finding。"""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    frontmatter_lines, code_lines = _line_regions(text)
    findings: list[Finding] = []
    try:
        rel_display = str(path.resolve().relative_to(project_root))
    except ValueError:
        rel_display = str(path)

    for idx, raw in enumerate(text.splitlines()):
        in_fm = idx in frontmatter_lines
        in_code = idx in code_lines
        for col, _end, tok in _extract_tokens(raw, in_frontmatter=in_fm):
            token = normalize_token(tok)
            if not token:
                continue
            stability = classify_stability(token)
            if stability == "relative" and not in_fm:
                # 正文相对路径（如 bundle-relative /concepts/...）不属信源引用
                continue
            fs_path = resolve_fs_path(token, project_root)
            exists: Optional[bool]
            if fs_path is None:
                exists = None
            else:
                try:
                    exists = fs_path.exists()
                except OSError:
                    exists = False
            findings.append(Finding(
                file=rel_display,
                line=idx + 1,
                col=col + 1,
                token=token,
                form=_classify_form(raw, token, in_fm),
                stability=stability,
                exists=exists,
                in_code_block=in_code,
            ))
    return findings


def build_target_signature(target: Path, project_root: Path) -> str:
    """清理前扫描：为待删除目录构建斜杠双向兼容的特征签名正则。

    目标在项目根内时取项目相对路径；跨项目/跨盘符时取末 3 级特征段。
    """
    try:
        rel = target.resolve().relative_to(project_root.resolve())
        parts = rel.parts
    except ValueError:
        parts = tuple(
            p for p in target.parts if not re.match(r"^[A-Za-z]:\\?$", p)
        )
        parts = parts[-3:]  # 跨项目目标：末级目录名最具区分度
    if len(parts) < 2:
        raise ValueError(
            f"目标路径特征不足（至少需要2级目录段）：{target}"
        )
    return r"(?:^|[\\/])" + r"[\\/]".join(re.escape(p) for p in parts)


def scan_references_to_target(
    target: Path, roots: list[Path], project_root: Path
) -> list[Finding]:
    """清理前扫描：在 roots 下查找对待删除目录的全部引用。"""
    pattern = re.compile(build_target_signature(target, project_root))
    findings: list[Finding] = []
    for root in roots:
        for f in _iter_text_files(root, CLEANUP_EXTENSIONS):
            try:
                text = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            try:
                rel_display = str(f.resolve().relative_to(project_root))
            except ValueError:
                rel_display = str(f)
            frontmatter_lines, code_lines = _line_regions(text)
            for idx, raw in enumerate(text.splitlines()):
                m = pattern.search(raw)
                if not m:
                    continue
                token = normalize_token(m.group(0).lstrip("\\/"))
                findings.append(Finding(
                    file=rel_display,
                    line=idx + 1,
                    col=m.start() + 1,
                    token=token,
                    form=_classify_form(
                        raw, token, idx in frontmatter_lines
                    ),
                    stability=classify_stability(token),
                    exists=None,
                    in_code_block=(idx in code_lines),
                ))
    return findings


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------
def _print_findings(findings: list[Finding], title: str) -> None:
    print(f"[{GATE}] {title}")
    print("=" * 88)
    current_file: Optional[str] = None
    for f in sorted(findings, key=lambda x: (x.file, x.line, x.col)):
        if f.file != current_file:
            current_file = f.file
            print(f"\n📄 {f.file}")
        code_tag = " [代码块内]" if f.in_code_block else ""
        exists_tag = (
            "" if f.exists is None else ("  ✅存在" if f.exists else "  ❌不存在")
        )
        print(
            f"  L{f.line}:C{f.col}  [{f.form}/{f.stability}]{code_tag}{exists_tag}"
        )
        print(f"       {f.token}")
    print("=" * 88)


def _findings_to_json(findings: list[Finding], **extra) -> str:
    return json.dumps(
        {"gate": GATE, "findings": [asdict(f) for f in findings], **extra},
        ensure_ascii=False,
        indent=2,
    )


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="信源引用稳定性扫描：三类载体×两种斜杠的临时信源引用检测与清理前扫描",
    )
    add_common_args(p)
    p.add_argument(
        "--target",
        default=None,
        help="清理前扫描模式：待删除目录路径，报告全部引用（存在引用则退出码1）",
    )
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)
    project_root = resolve_project_root(__file__)

    roots: list[Path]
    if args.path:
        root = Path(args.path)
        if not root.exists():
            print(f"[{GATE}] 参数错误：路径不存在 -> {root}", file=sys.stderr)
            return 2
        roots = [root.resolve()]
    else:
        roots = [project_root]

    if args.target:
        target = Path(args.target)
        if not target.is_absolute():
            target = (project_root / target).resolve()
        if not target.exists():
            print(f"[{GATE}] 参数错误：目标路径不存在 -> {target}", file=sys.stderr)
            return 2
        try:
            findings = scan_references_to_target(target, roots, project_root)
        except ValueError as exc:
            print(f"[{GATE}] 参数错误：{exc}", file=sys.stderr)
            return 2
        if args.json:
            print(_findings_to_json(
                findings, mode="cleanup-scan", target=str(target),
                scanned_roots=[str(r) for r in roots],
            ))
            return 1 if findings else 0
        print(
            f"[{GATE}] 清理前扫描：目标 {target}，"
            f"发现 {len(findings)} 处引用。"
        )
        if findings:
            _print_findings(findings, "结果：❌ 阻断删除——请先迁移/评估以上引用")
            return 1
        print(f"[{GATE}] 结果：✅ 放行——零引用，可安全删除。")
        return 0

    # audit 模式
    findings: list[Finding] = []
    scanned = 0
    for root in roots:
        for md in _iter_text_files(root, {".md"}):
            scanned += 1
            findings.extend(scan_file(md, project_root))

    blocking = [
        f for f in findings if f.stability == "temporary" or f.exists is False
    ]
    env_bound = [f for f in findings if f.stability == "env-bound"]

    if args.json:
        print(_findings_to_json(
            findings, mode="audit", scanned_files=scanned,
            blocking_count=len(blocking), env_bound_count=len(env_bound),
        ))
        return 1 if blocking else 0

    print(
        f"[{GATE}] audit 扫描完成：{scanned} 个 Markdown 文件，"
        f"{len(findings)} 条路径引用"
        f"（临时 {sum(1 for f in findings if f.stability == 'temporary')}、"
        f"不存在 {sum(1 for f in findings if f.exists is False)}、"
        f"环境绑定 {len(env_bound)}）。"
    )
    if blocking:
        _print_findings(blocking, "结果：❌ 拦截——存在临时信源引用或失效路径")
        if env_bound:
            print(f"[{GATE}] 另有 {len(env_bound)} 条环境绑定绝对路径（警告，不拦截）。")
        return 1
    if env_bound:
        print(f"[{GATE}] 结果：⚠️ 通过但有警告——{len(env_bound)} 条环境绑定绝对路径。")
        return 0
    print(f"[{GATE}] 结果：✅ 通过——无临时信源引用，全部路径复验可达。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
