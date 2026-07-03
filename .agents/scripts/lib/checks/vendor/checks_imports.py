"""vendor 非法导入检查模块。

检测项目中对 vendor 的非法引用，包括 sys.path hack 和未受保护的 import。
"""

from __future__ import annotations

import re
from pathlib import Path


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
