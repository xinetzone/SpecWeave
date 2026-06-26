"""Markdown 链接修复工具。

提供检测和修复 Markdown 文档中断链的能力，核心功能：
- 检测 file:/// 本地绝对路径链接
- 将绝对路径自动转换为正确的相对路径
- 修复相对路径深度错误（文件/目录重构后）
- 处理原子化目录引用（xxx.md → xxx/ 目录形式）
- 处理同文件自引用（简化为纯锚点）
- 支持文件名映射（文件重命名场景）
- 支持行号偏移映射（内容移位场景）
- 自动跳过代码块内的示例链接
- 自动跳过模板占位符链接
- Dry-run 模式预览变更不写入

典型用法：
    from lib.link_fixer import fix_directory_links

    rename_map = {"竹简悟道.html": "竹简悟道_完整版.html"}
    fixes = fix_directory_links(
        root_dir=Path("apps/zhujian-wudao"),
        project_root=Path("."),
        rename_map=rename_map,
        dry_run=True,
    )
"""

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

FILE_URL_RE = re.compile(
    r"file:///([A-Za-z]:/[^\s)]+|/[^\s)]+)"
)

INLINE_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

TEMPLATE_LINK_TEXTS = {
    "link", "path", "url", "来源", "pattern-name.md",
    "old_name.md", "new_name.md", "xxx", "xxx.md",
}

TEMPLATE_URL_PATTERNS = [
    re.compile(r"^path(/|$)"),
    re.compile(r"^URL$"),
]

_GENERIC_FILENAMES = {"README.md", "index.md", ".gitkeep"}
_DIR_FILENAMES = {"README.md"}


@dataclass
class LinkFix:
    """记录一次链接修复操作。"""
    file_path: Path
    line_num: int
    link_text: str
    old_url: str
    new_url: str
    fix_type: str
    reason: str = ""

    def __str__(self) -> str:
        return f"  L{self.line_num}: [{self.link_text}] {self.old_url} → {self.new_url} ({self.fix_type})"


def parse_file_url(url: str) -> tuple[str, str]:
    """解析 file:/// URL，返回 (文件路径部分, 锚点部分)。"""
    if "#" in url:
        path_part, anchor = url.split("#", 1)
        return path_part, f"#{anchor}"
    return url, ""


def extract_filename_from_url(file_url_path: str) -> str:
    """从 file:/// 路径中提取文件名。"""
    return Path(file_url_path).name


def _is_excluded_path(path: Path, project_root: Path) -> bool:
    """判断路径是否应排除（不搜索）。"""
    excluded_names = {".git", "vendor", ".venv", "__pycache__", "node_modules", ".temp"}
    try:
        rel = path.resolve().relative_to(project_root.resolve())
    except ValueError:
        return True
    return any(part in excluded_names for part in rel.parts)


def _find_all_matches(
    filename: str,
    project_root: Path,
    search_subdir: Path | None = None,
    *,
    find_dir: bool = False,
) -> list[Path]:
    """查找所有匹配的文件/目录，返回排序后的列表（近源优先）。"""
    project_root = project_root.resolve()
    matches: list[Path] = []

    search_dirs = []
    if search_subdir is not None:
        first_try = (project_root / search_subdir).resolve()
        if first_try.exists():
            search_dirs.append(first_try)
    search_dirs.append(project_root)

    for search_dir in search_dirs:
        for candidate in search_dir.rglob(filename):
            if _is_excluded_path(candidate, project_root):
                continue
            if find_dir and candidate.is_dir():
                readme = candidate / "README.md"
                if readme.exists():
                    matches.append(candidate.resolve())
            elif not find_dir and candidate.is_file():
                matches.append(candidate.resolve())

    return matches


def find_file_in_project(
    filename: str,
    project_root: Path,
    search_subdir: Path | None = None,
    *,
    find_dir: bool = False,
    near: Path | None = None,
) -> Path | None:
    """在项目中查找指定文件名的文件或目录。

    Args:
        filename: 要查找的文件名（含扩展名）或目录名。
        project_root: 项目根目录。
        search_subdir: 优先搜索的子目录（相对于 project_root）。
        find_dir: True=查找目录，False=查找文件。
        near: 优先返回距离此路径最近的匹配。

    Returns:
        匹配路径的绝对路径，或 None。
    """
    matches = _find_all_matches(filename, project_root, search_subdir, find_dir=find_dir)
    if not matches:
        return None

    if near is not None:
        near = near.resolve()
        def _shared_depth(p: Path) -> int:
            try:
                rel_p = p.relative_to(project_root)
                rel_near = near.relative_to(project_root)
            except ValueError:
                return -1
            shared = 0
            for a, b in zip(rel_p.parts, rel_near.parts):
                if a == b:
                    shared += 1
                else:
                    break
            return shared

        matches.sort(key=lambda p: -_shared_depth(p))

    return matches[0]


def _extract_search_terms(url_path: str) -> list[str]:
    """从 URL 路径中提取有意义的搜索关键词（过滤掉 . 和 ..）。"""
    parts = Path(url_path).parts
    terms = []
    for part in parts:
        if part in (".", "..", ""):
            continue
        name = part
        if name.endswith(".md"):
            name = name[:-3]
        if name and name not in {"docs", "retrospective", "reports", "patterns", "assets"}:
            terms.append(name)
    return terms


def _try_root_based_path(url_path: str, project_root: Path) -> Path | None:
    """当 URL 以项目顶级目录开头时，尝试作为项目根相对路径解析。

    动态检测 project_root 下的实际顶级目录（含子项目自己的目录结构），
    而非依赖硬编码列表，确保主项目和子项目（如 apps/xxx/）都能正确识别。
    """
    pr = project_root.resolve()
    cleaned = url_path.replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    parts = [p for p in cleaned.split("/") if p and p != ".."]
    if not parts:
        return None

    first_part = parts[0]
    # 动态构建顶级目录集合：project_root 下的直接子目录 + 兼容常见文件名
    top_dirs = {
        p.name for p in pr.iterdir() if p.is_dir()
    } if pr.exists() else set()
    # 常见顶级 Markdown 文件（不在目录内的根级文件）
    top_files = {
        p.name for p in pr.iterdir() if p.is_file() and p.suffix in {".md", ".html"}
    } if pr.exists() else set()

    if first_part in top_dirs:
        candidate = pr.joinpath(*parts)
        if candidate.is_dir():
            readme = candidate / "README.md"
            if readme.exists():
                return readme
            return candidate
        if candidate.exists():
            return candidate
        if not candidate.suffix:
            readme = candidate / "README.md"
            if readme.exists():
                return readme
    elif first_part in top_files and len(parts) == 1:
        candidate = pr / first_part
        if candidate.exists():
            return candidate
    return None


def try_adjust_relative_depth(
    url_without_anchor: str,
    source_file: Path,
    max_adjust: int = 3,
) -> Path | None:
    """通过增减 ../ 层级数来校正断链的相对路径。

    这是目录迁移/重构后最常见的断链类型：文件移动到更深（或更浅）的目录后，
    相对路径中 ../ 的数量需要相应增减，但路径的后半段（目标文件名和中间目录）是正确的。

    策略：
    1. 统计现有 ../ 的数量 N
    2. 尝试 N+1, N+2, ..., N+max_adjust（增加层级，文件被移到更深位置）
    3. 尝试 N-1, N-2, ..., max(0, N-max_adjust)（减少层级，文件被移到更浅位置）
    4. 优先尝试增加层级（这是更常见的场景：目录原子化拆分导致深度增加）
    5. 对每个候选路径检查目标是否存在，返回第一个有效的目标

    Args:
        url_without_anchor: 不含锚点的相对 URL 路径。
        source_file: 包含该链接的源文件绝对路径。
        max_adjust: 最大调整层数（默认 3）。

    Returns:
        找到的目标文件绝对路径，或 None。
    """
    if not url_without_anchor or url_without_anchor.startswith("/"):
        return None

    cleaned = url_without_anchor.replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]

    parts = cleaned.split("/")
    dotdot_count = 0
    for p in parts:
        if p == "..":
            dotdot_count += 1
        else:
            break

    if dotdot_count == 0 and not any(p == ".." for p in parts):
        return None

    remaining_parts = parts[dotdot_count:]
    if not remaining_parts:
        return None

    base_dir = source_file.parent.resolve()

    candidates: list[tuple[int, Path]] = []

    for delta in range(1, max_adjust + 1):
        new_dotdot = dotdot_count + delta
        candidate_parts = [".."] * new_dotdot + remaining_parts
        candidate_url = "/".join(candidate_parts)
        target = (base_dir / candidate_url).resolve()
        if target.exists():
            candidates.append((delta, target))

    for delta in range(1, min(dotdot_count, max_adjust) + 1):
        new_dotdot = dotdot_count - delta
        if new_dotdot < 0:
            break
        candidate_parts = [".."] * new_dotdot + remaining_parts if new_dotdot > 0 else remaining_parts
        candidate_url = "/".join(candidate_parts)
        target = (base_dir / candidate_url).resolve()
        if target.exists():
            candidates.append((delta + max_adjust, target))

    for depth_delta in [0, 1, 2]:
        target = (base_dir / cleaned).resolve()
        if target.exists() and target.is_dir():
            for suffix in ["README.md", "index.md"]:
                readme = target / suffix
                if readme.exists():
                    candidates.append((100 + depth_delta, readme))
                    break
            break

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0])
    best = candidates[0][1]

    if best.is_dir():
        readme = best / "README.md"
        if readme.exists():
            return readme
        return best

    return best


def find_target_by_stem(
    url_path: str,
    project_root: Path,
    search_subdir: Path | None = None,
    *,
    near: Path | None = None,
) -> Path | None:
    """通过 URL 路径的关键段在项目中查找目标。

    策略：
    1. 如果最后段是通用文件名（README.md 等），用其父目录名搜索
    2. 否则用文件名搜索 .md 文件和同名目录
    3. 对候选结果评分：共享路径深度 + URL关键词匹配数
    4. 排除与源文件自身相同的候选

    Args:
        url_path: 不含锚点的 URL 路径部分。
        project_root: 项目根目录。
        search_subdir: 优先搜索的子目录。
        near: 源文件位置，用于选择最近的匹配。

    Returns:
        找到的目标文件（.md 或目录下的 README.md），或 None。
    """
    p = Path(url_path)
    last_part = p.name

    if not last_part:
        return None

    search_terms = _extract_search_terms(url_path)
    near_resolved = near.resolve() if near else None
    pr = project_root.resolve()
    root_based_resolved = None

    use_dir_search = last_part.endswith(".md") or ("." not in last_part)

    if last_part in _DIR_FILENAMES and last_part.endswith(".md"):
        parent_name = p.parent.name
        if parent_name and parent_name not in (".", "..", ""):
            dir_matches = _find_all_matches(parent_name, project_root, search_subdir, find_dir=True)
            candidates = [d / "README.md" for d in dir_matches]
        else:
            candidates = []
    else:
        if last_part.endswith(".md"):
            md_name = last_part
            dir_name = last_part[:-3]
        elif "." not in last_part:
            md_name = last_part + ".md"
            dir_name = last_part
        else:
            md_name = last_part
            dir_name = None

        root_based = _try_root_based_path(url_path, project_root)
        candidates = []
        if root_based is not None:
            root_based_resolved = root_based.resolve()
            candidates.append(root_based)

        file_matches = _find_all_matches(md_name, project_root, search_subdir, find_dir=False)
        candidates.extend(file_matches)

        if dir_name:
            dir_matches = _find_all_matches(dir_name, project_root, search_subdir, find_dir=True)
            candidates.extend(d / "README.md" for d in dir_matches)

        if not candidates and last_part.endswith(".md"):
            stem = last_part[:-3]
            dir_matches2 = _find_all_matches(stem, project_root, search_subdir, find_dir=True)
            candidates.extend(d / "README.md" for d in dir_matches2)

    if not candidates:
        return None

    if near_resolved is not None:
        try:
            near_rel = near_resolved.relative_to(pr)
        except ValueError:
            near_rel = None

        def _score(candidate: Path) -> tuple[int, int, int]:
            try:
                cand_rel = candidate.relative_to(pr)
            except ValueError:
                return (-1, -1, len(candidate.parts))

            shared = 0
            if near_rel is not None:
                for a, b in zip(cand_rel.parts, near_rel.parts):
                    if a == b:
                        shared += 1
                    else:
                        break

            keyword_hits = 0
            cand_str = str(cand_rel).lower()
            for term in search_terms:
                if term.lower() in cand_str:
                    keyword_hits += 1

            is_self = 0
            if candidate.resolve() == near_resolved:
                is_self = -100

            root_bonus = 50 if root_based_resolved and candidate.resolve() == root_based_resolved else 0

            return (shared + keyword_hits + is_self + root_bonus, shared, -len(cand_rel.parts))

        candidates.sort(key=_score, reverse=True)

    if near_resolved is not None and candidates[0].resolve() == near_resolved:
        return candidates[0] if len(candidates) == 1 else None

    return candidates[0]


def compute_relative_path(source_file: Path, target_file: Path) -> str:
    """计算从 source_file 到 target_file 的相对路径（POSIX 格式）。

    如果 target 是 README.md（表示目录链接），返回目录的相对路径加斜杠。
    如果 source 和 target 是同一文件，返回空字符串。
    """
    source_file = source_file.resolve()
    target_file = target_file.resolve()

    if source_file == target_file:
        return ""

    if target_file.name == "README.md":
        target_dir = target_file.parent
        source_dir = source_file.parent
        if source_dir == target_dir:
            return "./"
        rel = os_path_to_posix(Path(os.path.relpath(str(target_dir), str(source_dir))))
        return rel + "/"

    if target_file.is_dir():
        source_dir = source_file.parent
        if source_dir == target_file:
            return "./"
        rel = os_path_to_posix(Path(os.path.relpath(str(target_file), str(source_dir))))
        return rel + "/"

    source_dir = source_file.parent
    return os_path_to_posix(Path(os.path.relpath(str(target_file), str(source_dir))))


def os_path_to_posix(path: Path | str) -> str:
    """将 OS 路径转换为 POSIX 格式（Markdown 链接通用）。"""
    return str(path).replace("\\", "/")


def apply_filename_mapping(file_path: str, rename_map: dict[str, str] | None) -> str:
    """应用文件名映射，处理文件重命名场景。"""
    if not rename_map:
        return file_path

    p = Path(file_path)
    old_name = p.name
    if old_name in rename_map:
        new_name = rename_map[old_name]
        return os_path_to_posix(p.parent / new_name) if p.parent.name else new_name
    return file_path


def apply_line_remap(anchor: str, line_remap: dict[str, dict[int, int]] | None, source_filename: str) -> str:
    """应用行号重映射，处理文件内容移位后行号变化的场景。"""
    if not line_remap or not anchor or not anchor.startswith("#L"):
        return anchor

    basename = Path(source_filename).name
    if basename not in line_remap:
        return anchor

    mapping = line_remap[basename]
    line_spec = anchor[2:]

    def _parse_line_num(s: str) -> int | None:
        s = s.lstrip("L")
        try:
            return int(s)
        except ValueError:
            return None

    if "-" in line_spec:
        start_str, end_str = line_spec.split("-", 1)
        start_line = _parse_line_num(start_str)
        end_line = _parse_line_num(end_str)
        if start_line is not None and end_line is not None:
            new_start = mapping.get(start_line, start_line)
            new_end = mapping.get(end_line, end_line)
            return f"#L{new_start}-L{new_end}"
        return anchor
    else:
        line_num = _parse_line_num(line_spec)
        if line_num is not None:
            new_line = mapping.get(line_num, line_num)
            return f"#L{new_line}"
        return anchor


def is_template_link(text: str, url: str) -> bool:
    """判断链接是否为模板/示例占位符（不应修复）。"""
    text_clean = text.strip()
    url_clean = url.strip().split("#")[0].rstrip("/")

    if text_clean in TEMPLATE_LINK_TEXTS:
        return True

    for pattern in TEMPLATE_URL_PATTERNS:
        if pattern.match(url_clean):
            return True

    if text_clean.endswith(".md") and url_clean == "path":
        return True
    if "->" in text_clean or "→" in text_clean:
        if url_clean in {"path", "path/old_name.md", "old_name.md", "URL"}:
            return True

    return False


def fix_link_url(
    old_url: str,
    source_file: Path,
    project_root: Path,
    rename_map: dict[str, str] | None = None,
    line_remap: dict[str, dict[int, int]] | None = None,
    prefer_subdir: Path | None = None,
    link_text: str = "",
) -> tuple[str, str, str] | None:
    """修复单个链接 URL，返回 (new_url, fix_type, reason) 或 None（无需修复）。

    修复策略（按优先级）：
    1. file:/// 绝对路径 → 解析目标文件位置并计算相对路径
    2. 相对路径断链 → 通过文件名/目录名搜索找到正确目标并重算路径
    3. 文件名映射 → 替换重命名的文件名
    4. 同文件引用 → 简化为纯锚点
    5. 行号重映射 → 调整移位后的行号
    """
    anchor = ""
    file_part = old_url

    file_url_match = FILE_URL_RE.match(old_url)
    if file_url_match:
        raw_path = file_url_match.group(1)
        file_part, anchor = parse_file_url(raw_path)
        filename = extract_filename_from_url(file_part)
        filename = apply_filename_mapping(filename, rename_map)

        search_url = file_part.replace("\\", "/")
        target_file = find_target_by_stem(search_url, project_root, prefer_subdir, near=source_file)
        if target_file is None:
            target_file = find_target_by_stem(filename, project_root, prefer_subdir, near=source_file)
        if target_file is None:
            return None

        anchor = apply_line_remap(anchor, line_remap, target_file.name)
        rel_path = compute_relative_path(source_file, target_file)

        if rel_path == "":
            new_url = anchor if anchor else "#"
            fix_type = "same_file_anchor"
            reason = "同文件引用简化为纯锚点"
        else:
            new_url = f"{rel_path}{anchor}"
            fix_type = "absolute_to_relative"
            reason = f"绝对路径 → 相对路径（目标: {target_file.name}）"

        return (new_url, fix_type, reason)

    if old_url.startswith("#"):
        return None

    if old_url.startswith("http://") or old_url.startswith("https://") or old_url.startswith("mailto:"):
        return None

    if link_text and is_template_link(link_text, old_url):
        return None

    url_without_anchor = old_url.split("#")[0]
    if not url_without_anchor:
        return None

    anchor_part = old_url[len(url_without_anchor):]

    resolved = (source_file.parent / url_without_anchor).resolve()
    if resolved.exists():
        if resolved.is_dir() and not url_without_anchor.endswith("/"):
            new_url = url_without_anchor + "/" + anchor_part
            return (new_url, "dir_slash", "目录链接补充尾部斜杠")
        return None

    depth_adjusted = try_adjust_relative_depth(url_without_anchor, source_file)
    if depth_adjusted is not None:
        rel_path = compute_relative_path(source_file, depth_adjusted)
        anchor_part = apply_line_remap(anchor_part, line_remap, depth_adjusted.name)
        if rel_path == "":
            new_url = anchor_part if anchor_part else "#"
            fix_type = "same_file_anchor"
            reason = "同文件引用简化为纯锚点"
        else:
            new_url = f"{rel_path}{anchor_part}"
            fix_type = "depth_adjusted"
            old_depth = url_without_anchor.count("../")
            new_depth = rel_path.count("../")
            depth_diff = new_depth - old_depth
            direction = f"增加 {depth_diff} 层 ../" if depth_diff > 0 else f"减少 {-depth_diff} 层 ../"
            reason = f"相对路径层级校正（{direction}）：{url_without_anchor} → {rel_path.rstrip('/')}"
        return (new_url, fix_type, reason)

    target_filename = Path(url_without_anchor).name

    if rename_map and target_filename in rename_map:
        new_filename = rename_map[target_filename]
        p = Path(url_without_anchor)
        new_clean = os_path_to_posix(p.parent / new_filename) if p.parent.name else new_filename
        new_target = (source_file.parent / new_clean).resolve()
        if new_target.exists():
            anchor_part = apply_line_remap(anchor_part, line_remap, new_filename)
            new_url = f"{new_clean}{anchor_part}"
            return (new_url, "filename_mapped", f"文件名映射: {target_filename} → {new_filename}")

    guessed = find_target_by_stem(url_without_anchor, project_root, prefer_subdir, near=source_file)
    if guessed is not None:
        rel_path = compute_relative_path(source_file, guessed)
        anchor_part = apply_line_remap(anchor_part, line_remap, guessed.name)

        if rel_path == "":
            new_url = anchor_part if anchor_part else "#"
            fix_type = "same_file_anchor"
            reason = "同文件引用简化为纯锚点"
        else:
            new_url = f"{rel_path}{anchor_part}"
            fix_type = "broken_relative_fixed"
            reason = f"相对路径断链修复: {url_without_anchor} → {rel_path.rstrip('/')}"

        return (new_url, fix_type, reason)

    return None


def fix_file_links(
    file_path: Path,
    project_root: Path,
    rename_map: dict[str, str] | None = None,
    line_remap: dict[str, dict[int, int]] | None = None,
    prefer_subdir: Path | None = None,
    dry_run: bool = False,
) -> list[LinkFix]:
    """修复单个 Markdown 文件中的断链。"""
    file_path = file_path.resolve()
    content = file_path.read_text(encoding="utf-8")
    fixes: list[LinkFix] = []
    new_content = content

    offset = 0
    for m in INLINE_LINK_RE.finditer(content):
        text = m.group(1)
        old_url = m.group(2).strip()

        if is_code_fence_context(content, m.start()):
            continue

        result = fix_link_url(
            old_url,
            file_path,
            project_root,
            rename_map=rename_map,
            line_remap=line_remap,
            prefer_subdir=prefer_subdir,
            link_text=text,
        )

        if result is None:
            continue

        new_url, fix_type, reason = result
        old_link = f"[{text}]({old_url})"
        new_link = f"[{text}]({new_url})"

        start = m.start() + offset
        end = m.end() + offset
        new_content = new_content[:start] + new_link + new_content[end:]
        offset += len(new_link) - len(old_link)

        line_num = content[:m.start()].count("\n") + 1
        fixes.append(LinkFix(
            file_path=file_path,
            line_num=line_num,
            link_text=text,
            old_url=old_url,
            new_url=new_url,
            fix_type=fix_type,
            reason=reason,
        ))

    if fixes and not dry_run:
        file_path.write_text(new_content, encoding="utf-8")

    return fixes


def is_code_fence_context(content: str, pos: int) -> bool:
    """判断位置 pos 是否在代码块或行内代码内部（避免修改代码示例中的链接）。"""
    before = content[:pos]
    fence_count = before.count("```")
    if fence_count % 2 == 1:
        return True
    line_start = before.rfind("\n") + 1
    line_before = before[line_start:]
    tick_count = 0
    i = 0
    while i < len(line_before):
        if line_before[i] == "`":
            run = 1
            while i + run < len(line_before) and line_before[i + run] == "`":
                run += 1
            if run <= 2:
                tick_count += 1
            i += run
        else:
            i += 1
    return tick_count % 2 == 1


def fix_directory_links(
    root_dir: Path,
    project_root: Path,
    rename_map: dict[str, str] | None = None,
    line_remap: dict[str, dict[int, int]] | None = None,
    prefer_subdir: Path | None = None,
    dry_run: bool = True,
    exclude_dirs: set[str] | None = None,
) -> list[LinkFix]:
    """递归修复目录下所有 Markdown 文件中的断链。"""
    from constants import EXCLUDED_DIRS

    if exclude_dirs is None:
        exclude_dirs = set()
    all_excluded = EXCLUDED_DIRS | exclude_dirs

    root_dir = root_dir.resolve()
    project_root = project_root.resolve()
    all_fixes: list[LinkFix] = []

    for md_path in sorted(root_dir.rglob("*.md")):
        parts = set(md_path.parts)
        if all_excluded & parts:
            continue
        fixes = fix_file_links(
            md_path,
            project_root,
            rename_map=rename_map,
            line_remap=line_remap,
            prefer_subdir=prefer_subdir,
            dry_run=dry_run,
        )
        all_fixes.extend(fixes)

    return all_fixes


def print_fix_report(fixes: list[LinkFix], dry_run: bool = True) -> None:
    """打印修复报告。"""
    if not fixes:
        print("  未发现需要修复的断链。")
        return

    mode = "预览（未写入）" if dry_run else "已修复"
    print(f"\n链接修复{mode}，共 {len(fixes)} 处：")

    by_type: dict[str, int] = {}
    for fix in fixes:
        by_type[fix.fix_type] = by_type.get(fix.fix_type, 0) + 1

    type_names = {
        "absolute_to_relative": "绝对路径→相对路径",
        "same_file_anchor": "同文件锚点简化",
        "filename_mapped": "文件名映射",
        "broken_relative_fixed": "相对路径断链修复（文件名搜索）",
        "depth_adjusted": "相对路径层级校正",
        "dir_slash": "目录链接斜杠补全",
        "line_remapped": "行号重映射",
    }
    type_summary = ", ".join(f"{type_names.get(t, t)}: {c}" for t, c in sorted(by_type.items()))
    print(f"  修复类型分布: {type_summary}")

    by_file: dict[Path, list[LinkFix]] = {}
    for fix in fixes:
        by_file.setdefault(fix.file_path, []).append(fix)

    for file_path, file_fixes in sorted(by_file.items()):
        try:
            display = file_path.relative_to(Path.cwd())
        except ValueError:
            display = file_path
        print(f"\n  {display}（{len(file_fixes)} 处）：")
        for fix in file_fixes:
            print(f"  L{fix.line_num}: [{fix.link_text}] {fix.old_url}")
            print(f"         → {fix.new_url}  [{fix.fix_type}]")


def fix_broken_links(
    target: str | Path,
    *,
    project_root: str | Path | None = None,
    rename_map: dict[str, str] | None = None,
    line_remap: dict[str, dict[int, int]] | None = None,
    prefer_subdir: str | Path | None = None,
    exclude_dirs: set[str] | None = None,
    dry_run: bool = True,
    verbose: bool = True,
) -> list[LinkFix]:
    """一站式断链修复便捷函数，自动推断项目根目录，一行调用即可修复。

    Args:
        target: 要修复的目录或文件路径（字符串或 Path 对象）。
        project_root: 项目根目录，默认自动从 target 向上查找含 .agents/ 的目录。
        rename_map: 文件名重命名映射 ``{"旧名.html": "新名.html"}``。
        line_remap: 行号重映射 ``{"文件名.md": {旧行号: 新行号}}``。
        prefer_subdir: 查找目标文件时优先搜索的子目录（如 ``"apps"``）。
        exclude_dirs: 额外排除的目录名集合。
        dry_run: True=仅预览不写入（默认），False=实际写入修复。
        verbose: True=打印修复报告，False=静默返回结果。

    Returns:
        修复操作列表（LinkFix 对象）。

    Examples:
        >>> # 最简用法：预览整个项目的断链
        >>> fixes = fix_broken_links(".")
        >>>
        >>> # 修复指定目录，同时处理文件重命名
        >>> fixes = fix_broken_links(
        ...     "apps/myapp",
        ...     rename_map={"old.html": "new.html"},
        ...     dry_run=False,
        ... )
        >>>
        >>> # 修复单个文件
        >>> fixes = fix_broken_links("docs/README.md", dry_run=False)
    """
    target_path = Path(target).resolve()

    if project_root is None:
        project_root = _infer_project_root(target_path)
    else:
        project_root = Path(project_root).resolve()

    prefer_subdir_path = Path(prefer_subdir).resolve() if prefer_subdir else None
    if prefer_subdir_path is not None and not prefer_subdir_path.is_absolute():
        prefer_subdir_path = (project_root / prefer_subdir).resolve()

    if verbose:
        mode = "预览（dry-run）" if dry_run else "实际修复"
        print(f"[link_fixer] 目标: {target_path}")
        print(f"[link_fixer] 项目根: {project_root}")
        print(f"[link_fixer] 模式: {mode}")

    if target_path.is_file():
        fixes = fix_file_links(
            target_path, project_root,
            rename_map=rename_map,
            line_remap=line_remap,
            prefer_subdir=prefer_subdir_path,
            dry_run=dry_run,
        )
    else:
        fixes = fix_directory_links(
            target_path, project_root,
            rename_map=rename_map,
            line_remap=line_remap,
            prefer_subdir=prefer_subdir_path,
            dry_run=dry_run,
            exclude_dirs=exclude_dirs,
        )

    if verbose:
        print_fix_report(fixes, dry_run=dry_run)

    return fixes


def _infer_project_root(start: Path) -> Path:
    """从起始路径向上查找包含 .agents/ 目录的项目根目录。"""
    current = start if start.is_dir() else start.parent
    for candidate in [current, *current.parents]:
        if (candidate / ".agents").is_dir():
            return candidate.resolve()
    return Path.cwd().resolve()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Markdown 断链自动修复工具",
        epilog="示例:\n"
               "  python -m lib.link_fixer --path apps/myapp           # 预览修复\n"
               "  python -m lib.link_fixer --path . --apply             # 修复全项目\n"
               "  python -m lib.link_fixer --path docs/README.md --apply\n"
               "  python -m lib.link_fixer --path apps --rename 旧.html=新.html",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--path", type=Path, required=True, help="要修复的目录或文件路径")
    parser.add_argument("--project-root", type=Path, default=None, help="项目根目录（默认自动推断）")
    parser.add_argument("--apply", action="store_true", default=False, help="实际写入修复（默认 dry-run 预览）")
    parser.add_argument("--prefer-subdir", type=str, default=None, help="查找目标文件时优先搜索的子目录")
    parser.add_argument("--exclude", type=str, nargs="*", default=[], help="额外排除的目录名")
    parser.add_argument(
        "--rename",
        nargs="*",
        default=[],
        metavar="OLD=NEW",
        help="文件名重命名映射，如 --rename 竹简悟道.html=竹简悟道_完整版.html",
    )
    args = parser.parse_args()

    rename_map = {}
    for mapping in args.rename:
        if "=" in mapping:
            old, new = mapping.split("=", 1)
            rename_map[old] = new

    exclude_set = set(args.exclude) if args.exclude else None

    fix_broken_links(
        target=args.path,
        project_root=args.project_root,
        rename_map=rename_map or None,
        prefer_subdir=args.prefer_subdir,
        exclude_dirs=exclude_set,
        dry_run=not args.apply,
        verbose=True,
    )
