"""vendor 检查主入口模块。

整合所有检查功能，提供 run() 主函数执行完整检查流程。
"""

from __future__ import annotations

from pathlib import Path

from lib.cli import print_header

from .checks_base import _check_gitignore_rule, _check_lib_readme, _get_libs
from .checks_deps import _check_pytest_excludes_vendor, _check_reverse_dependency
from .checks_imports import _check_illegal_imports
from .checks_submodule import (
    _check_branch_tracking,
    _check_submodule_clean,
    _check_submodule_initialized,
    _check_submodule_metadata,
)
from .constants import REQUIRED_ROOT_FILES
from .git_ops import _is_submodule, _load_submodule_paths
from .parser import _get_submodule_type
from .scanner import _scan_refs
from .templates import _create_templates


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
