"""vendor 目录合规性检查（来自 check-vendor.py）。"""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from constants import EXCLUDED_DIRS
from lib.cli import print_header

REQUIRED_ROOT_FILES = ["README.md", "VERSION.md"]
REQUIRED_LIB_FIELDS = ["名称", "版本", "来源", "引入日期", "用途", "许可证"]

VENDOR_README_TPL = """+++
# 此文件由 check-vendor 自动生成，请根据实际情况完善
+++

# Vendor 依赖总览

本目录存放项目引入的第三方依赖库。
- **git 子模块**：通过 `.gitmodules` 管理，会提交 gitlink 至版本控制
- **手动管理依赖**：通过 `.gitignore` 忽略（vendor/* 排除白名单），不提交源码

## 依赖清单

| 库名称 | 版本 | 引入日期 | 用途 |
|---|---|---|---|
{libs_table}

## 使用说明

1. 新增 git 子模块：`git submodule add <url> vendor/<name>`
2. 新增手动管理依赖：运行 `python .agents/scripts/repo-check.py vendor --fix` 创建标准模板
3. 手动管理依赖的每个子目录必须包含 `README.md` 元数据文件
4. 所有依赖版本需同步更新至 `VERSION.md`
5. 定期运行 `python .agents/scripts/repo-check.py vendor --scan-refs` 检查未使用依赖

## 管理规范

详见 [临时依赖管理流程](../.agents/protocols/dependency-management.md)
"""

VENDOR_VERSION_TPL = """+++
# 此文件由 check-vendor 自动生成，请根据实际情况完善
+++

# Vendor 依赖版本清单

| 库名称 | 版本号 | 来源地址 | 引入日期 | 许可证 | 类型 | 备注 |
|---|---|---|---|---|---|---|
{libs_table}

## 更新记录

- {date} | 初始化版本清单
"""

VENDOR_LIB_README_TPL = """+++
# 此文件由 check-vendor 自动生成，请根据实际情况完善
+++

# {lib_name}

## 基本信息

- **名称**：{lib_name}
- **版本**：请填写版本号
- **来源**：请填写 GitHub URL 或下载链接
- **引入日期**：{date}
- **用途**：请填写引入此库的原因和在项目中的作用
- **许可证**：请填写许可证类型（如 MIT、Apache-2.0 等）

## 修改记录

如对上游源码有修改，请在此记录：

| 修改日期 | 修改内容 | 修改原因 |
|---|---|---|
| 无 | - | - |

## 注意事项

- 请定期检查上游更新
- 如不再使用，请从 vendor/ 目录移除并更新 VERSION.md
"""


def _check_gitignore_rule(project_root: Path) -> bool:
    gi = project_root / ".gitignore"
    if not gi.exists():
        return False
    content = gi.read_text(encoding="utf-8")
    return "vendor/" in content or "vendor/*" in content


def _load_submodule_paths(project_root: Path) -> set[str]:
    gm = project_root / ".gitmodules"
    if not gm.exists():
        return set()
    paths = set()
    for line in gm.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("path ="):
            paths.add(s.split("=", 1)[1].strip())
    return paths


def _is_submodule(lib_dir: Path, project_root: Path, submodule_paths: set[str]) -> bool:
    rel_str = str(lib_dir.relative_to(project_root)).replace("\\", "/")
    if rel_str in submodule_paths:
        return True
    git_marker = lib_dir / ".git"
    return git_marker.exists() and git_marker.is_file()


def _get_libs(vendor_dir: Path, submodule_paths: set[str] | None = None) -> list[Path]:
    if not vendor_dir.exists():
        return []
    project_root = vendor_dir.parent
    if submodule_paths is None:
        submodule_paths = _load_submodule_paths(project_root)
    libs = []
    for p in sorted(vendor_dir.iterdir(), key=lambda p: p.name):
        if not p.is_dir() or p.name.startswith("."):
            continue
        if _is_submodule(p, project_root, submodule_paths):
            continue
        libs.append(p)
    return libs


def _check_lib_readme(lib_dir: Path) -> tuple[bool, list[str]]:
    readme = lib_dir / "README.md"
    issues = []
    if not readme.exists():
        return False, ["缺少 README.md 元数据文件"]
    content = readme.read_text(encoding="utf-8")
    for field in REQUIRED_LIB_FIELDS:
        if field not in content:
            issues.append(f"README.md 缺少必需字段：{field}")
    return len(issues) == 0, issues


def _scan_refs(project_root: Path, vendor_dir: Path) -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {}
    vendor_name = vendor_dir.name
    exclude = EXCLUDED_DIRS | {vendor_name}
    exts = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".md", ".json", ".yaml", ".yml",
        ".toml", ".cfg", ".ini", ".ps1", ".sh", ".bat", ".cmd",
    }
    for f in project_root.rglob("*"):
        if not f.is_file():
            continue
        if any(part in exclude for part in f.parts):
            continue
        if f.suffix.lower() not in exts:
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            file_refs = []
            for i, line in enumerate(content.splitlines(), 1):
                s = line.strip()
                if vendor_name in line:
                    if s.startswith("#") or s.startswith("//"):
                        continue
                    if "vendor/" in line or "vendor\\" in line or (vendor_name + "/") in line:
                        file_refs.append(f"L{i}: {s[:80]}")
            if file_refs:
                refs[str(f.relative_to(project_root))] = file_refs
        except (OSError, UnicodeDecodeError):
            continue
    return refs


def _parse_version_md_table(version_md_path: Path) -> tuple[list[str], list[list[str]]]:
    """解析 VERSION.md 中的 Markdown 表格，返回 (表头列表, 数据行列表)。

    表头和数据行都按列分割为字符串列表（已 strip）。
    如果文件不存在或无表格，返回 ([], [])。
    """
    if not version_md_path.exists():
        return [], []
    content = version_md_path.read_text(encoding="utf-8")
    headers: list[str] = []
    rows: list[list[str]] = []
    in_table = False
    separator_seen = False

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table and separator_seen:
                break
            continue
        cells = [c.strip() for c in stripped.split("|")]
        cells = [c for c in cells if c != ""]
        if not cells:
            continue
        if not in_table:
            headers = cells
            in_table = True
            continue
        if not separator_seen:
            if all(re.match(r'^[-:]+$', c) for c in cells):
                separator_seen = True
            else:
                headers = cells
            continue
        rows.append(cells)

    return headers, rows


def _get_submodule_type(project_root: Path, submodule_name: str) -> str:
    """判断子模块类型：third_party（第三方只读）或 owned_collab（自有协作）。

    读取 vendor/VERSION.md 表格，查找包含 submodule_name 的表格行，
    检查"类型"列值是否为 "owned_collab"；如果 VERSION.md 中没有类型列
    或找不到条目，默认返回 "third_party"（向后兼容）。
    """
    vendor_dir = project_root / "vendor"
    version_md = vendor_dir / "VERSION.md"
    headers, rows = _parse_version_md_table(version_md)

    type_col_idx = None
    for idx, h in enumerate(headers):
        if "类型" in h:
            type_col_idx = idx
            break

    if type_col_idx is None:
        return "third_party"

    for row in rows:
        if len(row) > 0 and row[0] == submodule_name:
            if type_col_idx < len(row) and row[type_col_idx].strip() == "owned_collab":
                return "owned_collab"
            return "third_party"

    return "third_party"


def _create_templates(project_root: Path, vendor_dir: Path) -> list[str]:
    created = []
    vendor_dir.mkdir(parents=True, exist_ok=True)
    submodule_paths = _load_submodule_paths(project_root)
    libs = _get_libs(vendor_dir, submodule_paths)

    all_dirs = sorted(
        [p for p in vendor_dir.iterdir() if p.is_dir() and not p.name.startswith(".")],
        key=lambda p: p.name,
    )
    sm_names = {p.name for p in all_dirs if _is_submodule(p, project_root, submodule_paths)}
    today = datetime.now().strftime("%Y-%m-%d")

    readme_rows = []
    ver_rows = []
    for d in all_dirs:
        if d.name in sm_names:
            readme_rows.append(f"| {d.name} | 子模块 | - | 外部依赖（git submodule） |")
            ver_rows.append(f"| {d.name} | 见子模块 | 见 .gitmodules | - | 见子模块 | third_party | 子模块 |")
        else:
            readme_rows.append(f"| {d.name} | 待填写 | {today} | 待填写 |")
            ver_rows.append(f"| {d.name} | 待填写 | 待填写 | {today} | 待填写 | third_party | |")
    if not all_dirs:
        readme_rows = ["| （暂无依赖） | - | - | - |"]
        ver_rows = ["| （暂无依赖） | - | - | - | - | - | - |"]
    libs_table = "\n".join(readme_rows)
    ver_table = "\n".join(ver_rows)

    root_readme = vendor_dir / "README.md"
    if not root_readme.exists():
        root_readme.write_text(VENDOR_README_TPL.format(libs_table=libs_table), encoding="utf-8")
        created.append("vendor/README.md")

    root_ver = vendor_dir / "VERSION.md"
    if not root_ver.exists():
        root_ver.write_text(VENDOR_VERSION_TPL.format(libs_table=ver_table, date=today), encoding="utf-8")
        created.append("vendor/VERSION.md")

    for lib_dir in libs:
        lib_readme = lib_dir / "README.md"
        if not lib_readme.exists():
            lib_readme.write_text(VENDOR_LIB_README_TPL.format(lib_name=lib_dir.name, date=today), encoding="utf-8")
            created.append(f"vendor/{lib_dir.name}/README.md")
    return created


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess | None:
    """执行 git 命令，返回 CompletedProcess 或 None（git 不可用时）。"""
    try:
        return subprocess.run(
            ["git"] + args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None


def _check_submodule_initialized(project_root: Path, submodule_path: str) -> tuple[bool, list[str]]:
    """检查 submodule 是否已正确初始化。

    验证三项：
    1. submodule 目录存在且非空
    2. .gitmodules 中有对应条目
    3. submodule 的 .git 是文件指针（指向主仓库 .git/modules）
    """
    issues = []
    sm_dir = project_root / submodule_path

    if not sm_dir.exists():
        issues.append(f"submodule 目录不存在: {submodule_path}")
        return False, issues
    if not any(sm_dir.iterdir()):
        issues.append(f"submodule 目录为空（可能未执行 git submodule update --init）: {submodule_path}")
        return False, issues

    gm = project_root / ".gitmodules"
    if gm.exists():
        gm_content = gm.read_text(encoding="utf-8")
        if submodule_path not in gm_content:
            issues.append(f".gitmodules 中未找到 {submodule_path} 条目")

    git_marker = sm_dir / ".git"
    if not git_marker.exists():
        issues.append(f"submodule 未初始化（缺少 .git 文件指针）: {submodule_path}")
    elif not git_marker.is_file():
        issues.append(f"submodule 的 .git 不是文件指针（应为 git submodule 格式）: {submodule_path}")
    else:
        content = git_marker.read_text(encoding="utf-8").strip()
        if not content.startswith("gitdir:"):
            issues.append(f"submodule 的 .git 文件格式异常（应以 'gitdir:' 开头）: {submodule_path}")

    return len(issues) == 0, issues


def _check_submodule_clean(project_root: Path, submodule_path: str, submodule_type: str = "third_party") -> tuple[bool, list[str]]:
    """检查 submodule 工作树是否清洁，无未提交修改或冲突。

    区分两种状态：
    - 未提交的工作树修改 → 错误（所有类型）
    - 本地提交领先远程 → owned_collab 仅 INFO，third_party 警告
    - detached HEAD 状态下跳过"领先远程"检测
    """
    issues = []
    sm_dir = project_root / submodule_path

    result = _run_git(["status", "--porcelain"], cwd=sm_dir)
    if result is None:
        issues.append("ERROR: git 命令不可用，无法检查 submodule 工作树状态")
        return False, issues
    if result.returncode != 0:
        issues.append(f"ERROR: git status 执行失败: {result.stderr.strip()}")
    else:
        status_output = result.stdout.strip()
        if status_output:
            dirty_files = [l for l in status_output.splitlines() if l.strip()]
            issues.append(f"ERROR: submodule 有 {len(dirty_files)} 个未提交的修改")

    result2 = _run_git(["submodule", "status", submodule_path], cwd=project_root)
    if result2 is not None and result2.returncode == 0:
        for line in result2.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            prefix = line[0] if line else " "
            if prefix == "+":
                parts = line.split()
                issues.append(f"ERROR: submodule checkout 的 commit 与 index 不同（当前 {parts[0][1:]} 与记录不一致）")
            elif prefix == "-":
                issues.append("ERROR: submodule 未初始化")
            elif prefix == "U":
                issues.append("ERROR: submodule 存在合并冲突")
    elif result2 is not None and result2.returncode != 0:
        issues.append(f"ERROR: git submodule status 执行失败: {result2.stderr.strip()}")

    is_detached = False
    result_sym = _run_git(["symbolic-ref", "--short", "HEAD"], cwd=sm_dir)
    if result_sym is not None:
        if result_sym.returncode != 0:
            is_detached = True

    if not is_detached:
        result_ahead = _run_git(["rev-list", "@{upstream}..HEAD", "--count"], cwd=sm_dir)
        if result_ahead is not None and result_ahead.returncode == 0:
            count_str = result_ahead.stdout.strip()
            try:
                ahead_count = int(count_str)
                if ahead_count > 0:
                    if submodule_type == "owned_collab":
                        issues.append(f"INFO: submodule 有 {ahead_count} 个本地提交领先远程（请记得推送）")
                    else:
                        issues.append(f"WARNING: submodule 有 {ahead_count} 个本地提交领先远程（第三方子模块不应有本地修改）")
            except ValueError:
                pass
        elif result_ahead is not None and result_ahead.returncode != 0:
            err = result_ahead.stderr.strip()
            if "no upstream" not in err.lower() and "no tracking" not in err.lower():
                pass

    has_errors = any(iss.startswith("ERROR:") for iss in issues)
    return not has_errors, issues


def _parse_version_md_for_submodule(version_md_path: Path, submodule_name: str) -> str | None:
    """解析 VERSION.md 中指定 submodule 的版本/commit 信息。

    返回条目字符串（表格行），未找到则返回 None。
    """
    if not version_md_path.exists():
        return None
    content = version_md_path.read_text(encoding="utf-8")
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("|") and submodule_name in line:
            cells = [c.strip() for c in line.split("|")]
            cells = [c for c in cells if c]
            if len(cells) >= 1 and cells[0] == submodule_name:
                return line
    return None


def _extract_commit_from_version_entry(entry_line: str) -> str | None:
    """从 VERSION.md 表格行中提取 commit 哈希。"""
    match = re.search(r'\b([0-9a-f]{7,40})\b', entry_line)
    if match:
        return match.group(1)
    return None


def _check_submodule_metadata(project_root: Path, submodule_name: str) -> tuple[bool, list[str]]:
    """检查 submodule 元数据完整性：VERSION.md 条目及 commit 一致性。"""
    issues = []
    vendor_dir = project_root / "vendor"
    version_md = vendor_dir / "VERSION.md"

    if not version_md.exists():
        issues.append("vendor/VERSION.md 不存在")
        return False, issues

    entry = _parse_version_md_for_submodule(version_md, submodule_name)
    if entry is None:
        issues.append(f"vendor/VERSION.md 中缺少 {submodule_name} 的条目")
        return False, issues

    recorded_commit = _extract_commit_from_version_entry(entry)
    if recorded_commit is None:
        issues.append(f"vendor/VERSION.md 中 {submodule_name} 条目未包含具体 commit 哈希（可能是占位符）")

    sm_path = f"vendor/{submodule_name}"
    sm_dir = project_root / sm_path
    result = _run_git(["rev-parse", "HEAD"], cwd=sm_dir)
    if result is not None and result.returncode == 0:
        actual_commit = result.stdout.strip()
        if recorded_commit and not actual_commit.startswith(recorded_commit):
            issues.append(
                f"VERSION.md 记录的 commit ({recorded_commit}) 与 submodule 当前 HEAD ({actual_commit[:8]}) 不一致"
            )

    return len(issues) == 0, issues


def _is_conditional_import(lines: list[str], idx: int) -> bool:
    """检测第 idx 行（0-based）的 vendor import 是否在 try/except ImportError 保护下。

    简化实现：向前看最多5行是否有 try:，向后看最多5行是否有 except ImportError。
    """
    look_back = min(5, idx + 1)
    in_try = False
    try_depth = 0
    for j in range(idx - 1, max(-1, idx - look_back - 1), -1):
        stripped = lines[j].strip()
        if stripped == "try:":
            in_try = True
            try_depth = j
            break
        if re.match(r'^(def|class|if|for|while|with)\s', stripped):
            break

    if not in_try:
        return False

    look_ahead = min(5, len(lines) - idx - 1)
    current_indent = len(lines[idx]) - len(lines[idx].lstrip())
    try_indent = len(lines[try_depth]) - len(lines[try_depth].lstrip())

    for j in range(idx + 1, min(len(lines), idx + look_ahead + 1)):
        stripped = lines[j].strip()
        if not stripped:
            continue
        line_indent = len(lines[j]) - len(lines[j].lstrip())
        if line_indent <= try_indent:
            if re.match(r'except\s+(ImportError|ModuleNotFoundError|Exception)', stripped):
                return True
            break
        if re.match(r'except\s+(ImportError|ModuleNotFoundError|Exception)', stripped):
            return True

    return False


def _check_illegal_imports(project_root: Path, vendor_dir: Path, submodule_types: dict[str, str] | None = None) -> tuple[bool, list[tuple[str, list[str], str]]]:
    """扫描项目中非法引用 vendor 的 Python import 语句。

    检测模式：
    - sys.path.insert/append 包含 "vendor" 路径 → 对所有类型报错
    - import vendor. 或 from vendor. 开头的 import：
      - 条件导入（try/except ImportError 保护）→ 对 owned_collab 允许
      - 裸导入 → third_party 报错，owned_collab 警告
    跳过注释行（# 开头）和排除目录。
    """
    if submodule_types is None:
        submodule_types = {}

    violations = []
    exclude_dirs = {"vendor", ".venv", ".temp", "__pycache__", ".git", ".agents", "node_modules"}

    for py_file in project_root.rglob("*.py"):
        if not py_file.is_file():
            continue
        rel_parts = py_file.relative_to(project_root).parts
        if any(part in exclude_dirs for part in rel_parts):
            continue
        try:
            lines = py_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        file_errors = []
        file_warnings = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if re.search(r'sys\.path\.(insert|append)\s*\(.*vendor', line):
                file_errors.append(f"L{i}: {stripped[:100]}")
                continue
            if re.match(r'^(import\s+vendor\.|from\s+vendor\.)', stripped):
                match = re.match(r'^(?:import|from)\s+vendor\.(\w+)', stripped)
                sm_name = match.group(1) if match else ""
                sm_path = f"vendor/{sm_name}"
                sm_type = submodule_types.get(sm_path, submodule_types.get(sm_name, "third_party"))

                idx = i - 1
                if _is_conditional_import(lines, idx):
                    continue
                else:
                    if sm_type == "owned_collab":
                        file_warnings.append(f"L{i}: {stripped[:100]} (owned_collab 裸导入，建议使用 try/except ImportError)")
                    else:
                        file_errors.append(f"L{i}: {stripped[:100]}")
        if file_errors:
            rel_path = str(py_file.relative_to(project_root)).replace("\\", "/")
            violations.append((rel_path, file_errors, "ERROR"))
        if file_warnings:
            rel_path = str(py_file.relative_to(project_root)).replace("\\", "/")
            violations.append((rel_path, file_warnings, "WARNING"))

    return len(violations) == 0, violations


def _check_reverse_dependency(project_root: Path, submodule_path: str) -> tuple[bool, list[str]]:
    """检查子模块是否存在反向依赖（引用 vendor/ 外部的项目代码）。

    检测内容：
    a. Python 文件中 sys.path.insert/append 包含上级目录路径（.. 或指向 vendor/ 外的路径）
    b. Python 文件中 from .. 或 from ... 相对导入超出 vendor/ 边界
    c. Markdown 文件中链接解析后是否指向子模块目录之外（且不是外部 URL）

    返回 (bool, issues) 格式，排除 .git 和 __pycache__ 目录。
    """
    issues = []
    sm_dir = project_root / submodule_path
    sm_dir_resolved = sm_dir.resolve()
    if not sm_dir.exists():
        return False, [f"submodule 目录不存在: {submodule_path}"]

    sm_parts = Path(submodule_path).parts
    vendor_depth = len(sm_parts)

    for py_file in sm_dir.rglob("*.py"):
        if not py_file.is_file():
            continue
        rel_parts = py_file.relative_to(sm_dir).parts
        if any(p in (".git", "__pycache__") for p in rel_parts):
            continue
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        file_issues = []
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if re.search(r'sys\.path\.(insert|append)\s*\(', line):
                if ".." in line or str(project_root).replace("\\", "/") in line.replace("\\", "/"):
                    file_issues.append(f"  L{i}: sys.path 修改包含上级路径: {stripped[:100]}")

            dotdot_match = re.match(r'^from\s+(\.+)\s+import', stripped)
            if dotdot_match:
                dots = dotdot_match.group(1)
                levels_up = len(dots)
                file_dir_depth = len(rel_parts) - 1
                if levels_up > file_dir_depth + 1:
                    file_issues.append(f"  L{i}: 相对导入超出 submodule 边界: {stripped[:100]}")

        if file_issues:
            rel_path = str(py_file.relative_to(project_root)).replace("\\", "/")
            issues.append(f"Python 文件 {rel_path}:")
            issues.extend(file_issues)

    for md_file in sm_dir.rglob("*.md"):
        if not md_file.is_file():
            continue
        rel_parts = md_file.relative_to(sm_dir).parts
        if any(p in (".git", "__pycache__") for p in rel_parts):
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        file_issues = []
        md_file_dir = md_file.parent
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            links = re.findall(r'\]\(([^)]+)\)', stripped)
            for link in links:
                link_clean = link.split("#")[0].split("?")[0].strip()
                if link_clean.startswith(("http", "mailto:", "/", "file:")):
                    continue
                try:
                    link_path = (md_file_dir / link_clean).resolve()
                    try:
                        link_path.relative_to(sm_dir_resolved)
                    except ValueError:
                        file_issues.append(f"  L{i}: 链接超出 submodule 边界: {link_clean}")
                except (OSError, ValueError):
                    pass

        if file_issues:
            rel_path = str(md_file.relative_to(project_root)).replace("\\", "/")
            issues.append(f"Markdown 文件 {rel_path}:")
            issues.extend(file_issues)

    return len(issues) == 0, issues


def _check_branch_tracking(project_root: Path, submodule_path: str) -> tuple[bool, list[str]]:
    """检查 submodule 是否配置了 branch 跟踪。

    读取 .gitmodules，检查指定 submodule 是否配置了 `branch = ` 字段。
    如果子模块类型是 owned_collab 但未配置 branch，返回警告。
    """
    issues = []
    gm = project_root / ".gitmodules"
    if not gm.exists():
        return True, issues

    content = gm.read_text(encoding="utf-8")
    lines = content.splitlines()

    has_branch = False
    target_path = submodule_path.replace("\\", "/")
    current_path_matches = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[submodule"):
            current_path_matches = False
            continue
        if stripped.startswith("path") and "=" in stripped:
            pval = stripped.split("=", 1)[1].strip().replace("\\", "/")
            current_path_matches = (pval == target_path)
            continue
        if current_path_matches and stripped.startswith("branch") and "=" in stripped:
            bval = stripped.split("=", 1)[1].strip()
            if bval:
                has_branch = True

    sm_type = _get_submodule_type(project_root, Path(target_path).name)
    if sm_type == "owned_collab" and not has_branch:
        issues.append(f"WARNING: owned_collab 类型子模块未配置 branch 跟踪，建议在 .gitmodules 中添加 branch = <branch-name>")
        return False, issues

    if has_branch:
        issues.append("INFO: 已配置 branch 跟踪")
    else:
        issues.append("INFO: 未配置 branch 跟踪（third_party 类型可接受）")

    return True, issues


def _find_pytest_configs(project_root: Path) -> list[tuple[Path, str]]:
    """查找项目中的 pytest 配置文件，返回 (路径, 类型) 列表。"""
    configs = []
    candidates = [
        (project_root / "pytest.ini", "ini"),
        (project_root / "setup.cfg", "cfg"),
        (project_root / "tox.ini", "ini"),
    ]
    for path, ctype in candidates:
        if path.exists():
            configs.append((path, ctype))
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        configs.append((pyproject, "toml"))
    return configs


def _check_pytest_excludes_vendor(project_root: Path) -> tuple[bool, list[str], bool]:
    """检查 pytest 配置是否排除了 vendor 目录。

    返回 (是否通过, 问题列表, 是否找到配置文件)。
    如果没有找到配置文件，返回警告而非错误。
    """
    issues = []
    configs = _find_pytest_configs(project_root)

    if not configs:
        return True, ["未找到 pytest 配置文件（pytest.ini/pyproject.toml/setup.cfg/tox.ini），建议添加配置排除 vendor/"], False

    vendor_excluded = False
    for config_path, _ in configs:
        try:
            content = config_path.read_text(encoding="utf-8")
        except OSError:
            continue
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith(";"):
                continue
            if re.search(r'norecursedirs\s*=.*vendor', stripped):
                vendor_excluded = True
                break
        if vendor_excluded:
            break

    if not vendor_excluded:
        issues.append(
            "pytest 配置中未排除 vendor/ 目录，建议在 norecursedirs 中添加 vendor 以避免测试第三方代码"
        )
        issues.append("  示例配置（pytest.ini）: norecursedirs = vendor .venv .temp __pycache__")
        return False, issues, True

    return True, ["pytest 已正确排除 vendor/ 目录"], True


def run(project_root: Path, args) -> int:
    vendor_dir = project_root / "vendor"
    print_header("Vendor 目录合规性检查")

    do_fix = getattr(args, "fix", False)
    do_scan_refs = getattr(args, "scan_refs", False)
    do_deep = getattr(args, "deep", False)

    if not vendor_dir.exists():
        print(f"\n[INFO] vendor 目录不存在（这是正常状态，表示当前无手动引入的第三方依赖）")
        if do_fix:
            print("\n正在创建 vendor 目录标准结构...")
            created = _create_templates(project_root, vendor_dir)
            for f in created:
                print(f"   [OK] 创建: {f}")
            print(f"\n[OK] 已创建 vendor 目录，共生成 {len(created)} 个文件")
        else:
            print("   提示: 如需引入第三方依赖，请运行 `python .agents/scripts/repo-check.py vendor --fix` 初始化目录结构")
        print("\n" + "=" * 60)
        return 0

    print(f"\n[DIR] 检查目录: {vendor_dir}")
    errors = 0
    warnings = 0
    step = 0

    step += 1
    print(f"\n{step}. 检查 .gitignore 规则...")
    if _check_gitignore_rule(project_root):
        print("   [OK] .gitignore 已配置 vendor/ 忽略规则")
    else:
        print("   [FAIL] .gitignore 缺少 vendor/ 忽略规则！临时依赖可能被意外提交")
        errors += 1

    if do_fix:
        step += 1
        print(f"\n{step}. 自动修复缺失文件...")
        created = _create_templates(project_root, vendor_dir)
        if created:
            for f in created:
                print(f"   [OK] 创建: {f}")
            print(f"   共创建 {len(created)} 个模板文件，请完善模板中的占位内容")
        else:
            print("   [OK] 所有必需文件已存在，无需修复")

    step += 1
    print(f"\n{step}. 检查根目录必需文件...")
    for rf in REQUIRED_ROOT_FILES:
        if (vendor_dir / rf).exists():
            print(f"   [OK] {rf} 存在")
        else:
            print(f"   [FAIL] 缺少必需文件: {rf}")
            errors += 1

    step += 1
    print(f"\n{step}. 检查依赖库元数据...")
    submodule_paths = _load_submodule_paths(project_root)
    libs = _get_libs(vendor_dir, submodule_paths)
    all_dirs = sorted(
        [p for p in vendor_dir.iterdir() if p.is_dir() and not p.name.startswith(".")],
        key=lambda p: p.name,
    )
    submodules = []
    submodule_full_paths = []
    submodule_types: dict[str, str] = {}
    for d in all_dirs:
        if _is_submodule(d, project_root, submodule_paths):
            sm_name = d.name
            sm_rel_path = str(d.relative_to(project_root)).replace("\\", "/")
            submodules.append(sm_name)
            submodule_full_paths.append(sm_rel_path)
            sm_type = _get_submodule_type(project_root, sm_name)
            submodule_types[sm_rel_path] = sm_type
            submodule_types[sm_name] = sm_type
    if submodules:
        print(f"   [SUB] 发现 {len(submodules)} 个 git 子模块（跳过元数据检查）:")
        for sm in submodules:
            sm_type = submodule_types.get(sm, "third_party")
            print(f"      [OK] {sm}/ (子模块, {sm_type})")
    if not libs:
        if not submodules:
            print("   [INFO] vendor 目录为空（无第三方依赖）")
    else:
        print(f"   发现 {len(libs)} 个手动管理依赖目录:")
        for ld in libs:
            ok, issues = _check_lib_readme(ld)
            if ok:
                print(f"   [OK] {ld.name}/README.md 元数据完整")
            else:
                print(f"   [FAIL] {ld.name}:")
                for issue in issues:
                    print(f"      - {issue}")
                errors += 1

    if do_scan_refs:
        step += 1
        print(f"\n{step}. 扫描代码中对 vendor 的引用...")
        refs = _scan_refs(project_root, vendor_dir)
        if refs:
            print(f"   发现 {len(refs)} 个文件引用了 vendor 路径:")
            for fp, lines in refs.items():
                print(f"   [FILE] {fp}:")
                for line in lines[:5]:
                    print(f"      {line}")
                if len(lines) > 5:
                    print(f"      ... 还有 {len(lines) - 5} 处引用")
        else:
            print("   [INFO] 代码中未发现对 vendor 的引用")
            warnings += 1

    if do_deep:
        step += 1
        print(f"\n{step}. Submodule 深度检查...")
        if not submodules:
            print("   [INFO] 未发现 git 子模块，跳过深度检查")
        else:
            for i, sm_name in enumerate(submodules):
                sm_path = submodule_full_paths[i]
                sm_type = submodule_types.get(sm_path, "third_party")
                print(f"   [SUB] {sm_name} ({sm_type}):")

                ok_init, issues_init = _check_submodule_initialized(project_root, sm_path)
                if ok_init:
                    print(f"      [OK] 初始化检查通过")
                else:
                    print(f"      [FAIL] 初始化检查失败:")
                    for issue in issues_init:
                        print(f"         - {issue}")
                    errors += 1

                ok_clean, issues_clean = _check_submodule_clean(project_root, sm_path, sm_type)
                has_clean_errors = False
                has_clean_warnings = False
                for iss in issues_clean:
                    if iss.startswith("ERROR:"):
                        has_clean_errors = True
                    elif iss.startswith("WARNING:"):
                        has_clean_warnings = True
                if ok_clean and not has_clean_warnings:
                    print(f"      [OK] 工作树清洁")
                else:
                    for iss in issues_clean:
                        if iss.startswith("ERROR:"):
                            print(f"      [FAIL] {iss[7:]}")
                        elif iss.startswith("WARNING:"):
                            print(f"      [WARN] {iss[9:]}")
                            warnings += 1
                        elif iss.startswith("INFO:"):
                            print(f"      [INFO] {iss[6:]}")
                    if has_clean_errors:
                        errors += 1

                ok_meta, issues_meta = _check_submodule_metadata(project_root, sm_name)
                if ok_meta:
                    print(f"      [OK] 元数据完整且 commit 一致")
                else:
                    print(f"      [FAIL] 元数据检查失败:")
                    for issue in issues_meta:
                        print(f"         - {issue}")
                    errors += 1

                ok_branch, issues_branch = _check_branch_tracking(project_root, sm_path)
                for iss in issues_branch:
                    if iss.startswith("WARNING:"):
                        print(f"      [WARN] {iss[9:]}")
                        warnings += 1
                    elif iss.startswith("INFO:"):
                        print(f"      [OK] {iss[6:]}")

                if sm_type == "owned_collab":
                    ok_rev, issues_rev = _check_reverse_dependency(project_root, sm_path)
                    if ok_rev:
                        print(f"      [OK] 无反向依赖")
                    else:
                        print(f"      [WARN] 检测到反向依赖问题:")
                        for issue in issues_rev:
                            print(f"         - {issue}")
                        warnings += 1

        step += 1
        print(f"\n{step}. 非法引用检查...")
        ok_imports, violations = _check_illegal_imports(project_root, vendor_dir, submodule_types)
        if ok_imports:
            print("   [OK] 未发现非法 vendor 引用（sys.path hack 或直接 import vendor.）")
        else:
            error_count = sum(1 for _, _, vtype in violations if vtype == "ERROR")
            warn_count = sum(1 for _, _, vtype in violations if vtype == "WARNING")
            print(f"   [FAIL] 发现 {error_count} 个错误, {warn_count} 个警告:")
            for fp, lines, vtype in violations:
                icon = "[FAIL]" if vtype == "ERROR" else "[WARN]"
                print(f"   [FILE] {fp} {icon}:")
                for line in lines[:5]:
                    print(f"      {line}")
            errors += error_count
            warnings += warn_count

        step += 1
        print(f"\n{step}. 测试路径隔离检查...")
        ok_pytest, pytest_issues, found_config = _check_pytest_excludes_vendor(project_root)
        if found_config:
            if ok_pytest:
                for msg in pytest_issues:
                    print(f"   [OK] {msg}")
            else:
                for msg in pytest_issues:
                    print(f"   [FAIL] {msg}")
                errors += 1
        else:
            for msg in pytest_issues:
                print(f"   [WARN] {msg}")
                warnings += 1

    print("\n" + "=" * 60)
    if errors > 0:
        print(f"[FAIL] 检查失败: 发现 {errors} 个错误", end="")
        print(f"，{warnings} 个警告" if warnings else "")
        print("提示: 运行 `python .agents/scripts/repo-check.py vendor --fix` 可自动修复缺失文件")
        print("=" * 60)
        return 1
    if warnings > 0:
        print(f"[WARN] 检查通过，有 {warnings} 个警告")
    else:
        print("[OK] 检查通过: vendor 目录结构合规")
    print("=" * 60)
    return 0
