"""vendor 模板生成模块。

自动创建 vendor 目录标准结构和元数据模板文件。
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .checks_base import _get_libs
from .constants import VENDOR_LIB_README_TPL, VENDOR_README_TPL, VENDOR_VERSION_TPL
from .git_ops import _is_submodule, _load_submodule_paths


def _create_templates(project_root: Path, vendor_dir: Path) -> list[str]:
    """创建 vendor 目录标准模板文件。"""
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
