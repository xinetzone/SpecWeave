"""vendor 目录合规性检查（来自 check-vendor.py）。"""

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

本目录存放项目手动引入的第三方依赖库。所有依赖均已在 `.gitignore` 中配置忽略，不会提交至版本控制。

## 依赖清单

| 库名称 | 版本 | 引入日期 | 用途 |
|---|---|---|---|
{libs_table}

## 使用说明

1. 新增依赖时，请先运行 `python .agents/scripts/repo-check.py vendor --fix` 创建标准模板
2. 每个依赖子目录必须包含 `README.md` 元数据文件
3. 所有依赖版本需同步更新至 `VERSION.md`
4. 定期运行 `python .agents/scripts/repo-check.py vendor --scan-refs` 检查未使用依赖

## 管理规范

详见 [临时依赖管理流程](../.agents/protocols/dependency-management.md)
"""

VENDOR_VERSION_TPL = """+++
# 此文件由 check-vendor 自动生成，请根据实际情况完善
+++

# Vendor 依赖版本清单

| 库名称 | 版本号 | 来源地址 | 引入日期 | 许可证 | 备注 |
|---|---|---|---|---|---|
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
    return "vendor/" in gi.read_text(encoding="utf-8")


def _get_libs(vendor_dir: Path) -> list[Path]:
    if not vendor_dir.exists():
        return []
    return sorted(
        [p for p in vendor_dir.iterdir() if p.is_dir() and not p.name.startswith(".")],
        key=lambda p: p.name,
    )


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


def _create_templates(project_root: Path, vendor_dir: Path) -> list[str]:
    created = []
    vendor_dir.mkdir(parents=True, exist_ok=True)
    libs = _get_libs(vendor_dir)
    lib_names = [lib.name for lib in libs]
    today = datetime.now().strftime("%Y-%m-%d")

    if lib_names:
        libs_table = "\n".join(f"| {n} | 待填写 | {today} | 待填写 |" for n in lib_names)
        ver_table = "\n".join(f"| {n} | 待填写 | 待填写 | {today} | 待填写 | |" for n in lib_names)
    else:
        libs_table = "| （暂无依赖） | - | - | - |"
        ver_table = "| （暂无依赖） | - | - | - | - | - |"

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


def run(project_root: Path, args) -> int:
    vendor_dir = project_root / "vendor"
    print_header("Vendor 目录合规性检查")

    do_fix = getattr(args, "fix", False)
    do_scan_refs = getattr(args, "scan_refs", False)

    if not vendor_dir.exists():
        print(f"\nℹ️  vendor 目录不存在（这是正常状态，表示当前无手动引入的第三方依赖）")
        if do_fix:
            print("\n正在创建 vendor 目录标准结构...")
            created = _create_templates(project_root, vendor_dir)
            for f in created:
                print(f"   ✅ 创建: {f}")
            print(f"\n✅ 已创建 vendor 目录，共生成 {len(created)} 个文件")
        else:
            print("   提示: 如需引入第三方依赖，请运行 `python .agents/scripts/repo-check.py vendor --fix` 初始化目录结构")
        print("\n" + "=" * 60)
        return 0

    print(f"\n📂 检查目录: {vendor_dir}")
    errors = 0
    warnings = 0

    print("\n1. 检查 .gitignore 规则...")
    if _check_gitignore_rule(project_root):
        print("   ✅ .gitignore 已配置 vendor/ 忽略规则")
    else:
        print("   ❌ .gitignore 缺少 vendor/ 忽略规则！临时依赖可能被意外提交")
        errors += 1

    if do_fix:
        print("\n2. 自动修复缺失文件...")
        created = _create_templates(project_root, vendor_dir)
        if created:
            for f in created:
                print(f"   ✅ 创建: {f}")
            print(f"   共创建 {len(created)} 个模板文件，请完善模板中的占位内容")
        else:
            print("   ✅ 所有必需文件已存在，无需修复")

    print("\n3. 检查根目录必需文件...")
    for rf in REQUIRED_ROOT_FILES:
        if (vendor_dir / rf).exists():
            print(f"   ✅ {rf} 存在")
        else:
            print(f"   ❌ 缺少必需文件: {rf}")
            errors += 1

    print("\n4. 检查依赖库元数据...")
    libs = _get_libs(vendor_dir)
    if not libs:
        print("   ℹ️  vendor 目录为空（无第三方依赖）")
    else:
        print(f"   发现 {len(libs)} 个依赖目录:")
        for ld in libs:
            ok, issues = _check_lib_readme(ld)
            if ok:
                print(f"   ✅ {ld.name}/README.md 元数据完整")
            else:
                print(f"   ❌ {ld.name}:")
                for issue in issues:
                    print(f"      - {issue}")
                errors += 1

    if do_scan_refs:
        print("\n5. 扫描代码中对 vendor 的引用...")
        refs = _scan_refs(project_root, vendor_dir)
        if refs:
            print(f"   发现 {len(refs)} 个文件引用了 vendor 路径:")
            for fp, lines in refs.items():
                print(f"   📄 {fp}:")
                for line in lines[:5]:
                    print(f"      {line}")
                if len(lines) > 5:
                    print(f"      ... 还有 {len(lines) - 5} 处引用")
        else:
            print("   ℹ️  代码中未发现对 vendor 的引用")
            warnings += 1

    print("\n" + "=" * 60)
    if errors > 0:
        print(f"❌ 检查失败: 发现 {errors} 个错误", end="")
        print(f"，{warnings} 个警告" if warnings else "")
        print("提示: 运行 `python .agents/scripts/repo-check.py vendor --fix` 可自动修复缺失文件")
        print("=" * 60)
        return 1
    if warnings > 0:
        print(f"⚠️  检查通过，有 {warnings} 个警告")
    else:
        print("✅ 检查通过: vendor 目录结构合规")
    print("=" * 60)
    return 0
