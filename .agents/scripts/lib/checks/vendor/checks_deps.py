"""vendor 依赖检查模块。

反向依赖检测、pytest配置隔离检查等功能。
"""

from __future__ import annotations

import re
from pathlib import Path


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

    md_issues = []
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

        file_warns = []
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
                        if link_path.exists():
                            pass
                        else:
                            file_warns.append(f"  L{i}: 失效外链（目标不存在）: {link_clean}")
                except (OSError, ValueError):
                    pass

        if file_warns:
            rel_path = str(md_file.relative_to(project_root)).replace("\\", "/")
            md_issues.append(f"Markdown 文件 {rel_path}（失效外链，不阻断）:")
            md_issues.extend(file_warns)

    if md_issues:
        issues.extend(md_issues)

    return len(issues) == 0, issues


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
