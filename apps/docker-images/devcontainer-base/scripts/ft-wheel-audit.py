#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Free-Threading Wheel ABI 审计器。

检测当前 conda/pip 环境中已安装包的 wheel ABI 兼容性，识别：
  1. 非 cp314t 的 C 扩展 wheel（会静默重启用 GIL）
  2. sdist 源码编译安装的 C 扩展（无 wheel tag，无法保证 ft-safe）
  3. abi3 stable ABI 包（3.14t 上未经过 free-threading 验证）
  4. conda 安装包的 build string 是否包含 cp314t

背景（PEP 703/779）：free-threading 构建中，C 扩展需在 Py_mod_gil slot
声明 ft-safe 才会保持 GIL 禁用。cp314 wheel 无此声明，import 时解释器
会静默拉起 GIL（进程级保险丝），多线程并行收益归零且无明显报错。

用法：
    python ft-wheel-audit.py                  # 标准审计（检查所有包）
    python ft-wheel-audit.py -q               # 静默模式，仅输出违规项
    python ft-wheel-audit.py --strict         # 严格模式：abi3/sdist 也报错
    python ft-wheel-audit.py --json           # JSON 格式输出（供 CI 使用）
    python ft-wheel-audit.py package1 pkg2    # 只审计指定包

退出码：
    0 = 所有 C 扩展均为 cp314t（安全）
    1 = 发现非 ft-safe 的 C 扩展 wheel
    2 = 非 free-threading 构建
    3 = 严格模式下发现 sdist/abi3 包
"""

from __future__ import annotations

import argparse
import importlib.machinery
import json
import os
import sys
import sysconfig
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

import importlib.metadata as importlib_metadata


# ── 已知在 3.14t 上安全的 abi3 包白名单（经过验证不会拉起 GIL） ──
ABI3_SAFE_WHITELIST: set[str] = set()

# ── 纯 Python 包（无 C 扩展）无需审计 ──
SKIP_PACKAGES: set[str] = {
    "pip", "setuptools", "wheel", "packaging", "six", "python-dateutil",
    "pyparsing", "cycler", "kiwisolver", "fonttools", "pillow",  # pillow 有 C 扩展但新版本已 ft-safe
}


@dataclass
class PackageAudit:
    """单个包的审计结果"""
    name: str
    version: str
    install_type: str  # "wheel-ft" | "wheel-gil" | "wheel-abi3" | "sdist" | "conda" | "pure-python" | "editable"
    wheel_tag: Optional[str] = None
    has_cext: bool = False
    is_safe: bool = True
    warnings: list[str] = field(default_factory=list)
    details: str = ""


def get_expected_abi() -> Optional[str]:
    """获取当前 Python 期望的 free-threading ABI tag，如 cp314t。"""
    soabi = sysconfig.get_config_var("SOABI") or ""
    py_major = sys.version_info.major
    py_minor = sys.version_info.minor
    if "t" in soabi:
        return f"cp{py_major}{py_minor}t"
    return None


def get_conda_build_string(package_name: str) -> Optional[str]:
    """尝试获取 conda 安装包的 build string（如 h1234567_1_cp314t）。"""
    conda_meta = Path(sysconfig.get_config_var("CONDA_PREFIX") or "/opt/conda/envs/main")
    meta_dir = conda_meta / "conda-meta"
    if not meta_dir.exists():
        # 尝试从 site-packages 反推
        for sp in sysconfig.get_paths().values():
            candidate = Path(sp).parent.parent.parent / "conda-meta"
            if candidate.exists():
                meta_dir = candidate
                break
    if not meta_dir.exists():
        return None
    for json_file in meta_dir.glob(f"{package_name}-*-*.json"):
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
            return data.get("build", "")
        except (json.JSONDecodeError, OSError):
            continue
    return None


def has_c_extensions(dist: importlib_metadata.Distribution) -> bool:
    """检测分发包是否包含 C 扩展（.so/.pyd 文件）。"""
    dist_dir = dist.locate_file("")
    if not dist_dir or not Path(str(dist_dir)).exists():
        return False
    suffixes = importlib.machinery.EXTENSION_SUFFIXES
    for ext in suffixes:
        if list(Path(str(dist_dir)).rglob(f"*{ext}")):
            return True
    return False


def get_wheel_tag(dist: importlib_metadata.Distribution) -> Optional[str]:
    """从 WHEEL metadata 文件中提取 wheel Tag。"""
    for f in dist.files or []:
        if str(f).endswith(".dist-info/WHEEL"):
            wheel_file = dist.locate_file(f)
            try:
                with open(str(wheel_file), encoding="utf-8") as wf:
                    for line in wf:
                        line = line.strip()
                        if line.startswith("Tag:"):
                            return line.split(":", 1)[1].strip()
            except (OSError, UnicodeDecodeError):
                return None
    return None


def is_editable_install(dist: importlib_metadata.Distribution) -> bool:
    """检测是否为可编辑安装（editable install）。"""
    for f in dist.files or []:
        if str(f).endswith(".dist-info/direct_url.json"):
            url_file = dist.locate_file(f)
            try:
                with open(str(url_file), encoding="utf-8") as uf:
                    data = json.load(uf)
                return data.get("dir_info", {}).get("editable", False)
            except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                return False
    return False


def audit_package(dist: importlib_metadata.Distribution, strict: bool = False) -> PackageAudit:
    """审计单个包的 ABI 兼容性。"""
    name = dist.metadata.get("Name", "unknown")
    version = dist.version or "unknown"
    audit = PackageAudit(name=name, version=version, install_type="pure-python")

    # 可编辑安装
    if is_editable_install(dist):
        audit.install_type = "editable"
        audit.warnings.append("editable install - cannot verify ABI")
        return audit

    # 检测 C 扩展
    audit.has_cext = has_c_extensions(dist)
    if not audit.has_cext:
        audit.install_type = "pure-python"
        audit.is_safe = True
        return audit

    # 有 C 扩展，检查 wheel tag
    wheel_tag = get_wheel_tag(dist)
    audit.wheel_tag = wheel_tag

    # 检查是否为 conda 包
    conda_build = get_conda_build_string(name.lower())
    if conda_build is not None and not wheel_tag:
        audit.install_type = "conda"
        if "cp314t" in conda_build or "_cp314t" in conda_build:
            audit.is_safe = True
            audit.details = f"conda build: {conda_build}"
        else:
            audit.install_type = "conda"
            audit.is_safe = False
            audit.warnings.append(f"conda build string missing cp314t: {conda_build}")
            audit.details = f"conda build: {conda_build}"
        return audit

    if wheel_tag:
        expected_abi = get_expected_abi()
        if expected_abi and expected_abi in wheel_tag:
            audit.install_type = "wheel-ft"
            audit.is_safe = True
            audit.details = f"wheel tag: {wheel_tag}"
        elif "abi3" in wheel_tag:
            audit.install_type = "wheel-abi3"
            # abi3 包在 strict 模式下需要警告
            if strict and name.lower() not in ABI3_SAFE_WHITELIST:
                audit.is_safe = False
                audit.warnings.append(
                    "abi3 wheel - built for stable ABI, not explicitly free-thread-safe; "
                    "importing MAY re-enable GIL"
                )
            else:
                audit.is_safe = True  # 宽松模式下假设安全（会被运行时检测捕获）
                audit.warnings.append(
                    "abi3 wheel - stable ABI, ft-safety not guaranteed (runtime check recommended)"
                )
            audit.details = f"wheel tag: {wheel_tag}"
        else:
            audit.install_type = "wheel-gil"
            audit.is_safe = False
            audit.warnings.append(
                f"non-ft wheel tag ({wheel_tag}) - WILL re-enable GIL on import"
            )
            audit.details = f"wheel tag: {wheel_tag}"
    else:
        # sdist 安装（无 WHEEL 文件或 tag 为空）
        audit.install_type = "sdist"
        if strict:
            audit.is_safe = False
            audit.warnings.append(
                "sdist/source install - compiled without Py_mod_gil declaration; "
                "WILL re-enable GIL on import"
            )
        else:
            audit.is_safe = True  # 宽松模式下只警告，不报错
            audit.warnings.append(
                "sdist/source install - no wheel tag; ft-safety unverified (runtime check recommended)"
            )
        audit.details = "installed from source (sdist)"

    return audit


def print_report(results: list[PackageAudit], expected_abi: str, verbose: bool = False):
    """打印人类可读的审计报告。"""
    violations = [r for r in results if r.install_type == "wheel-gil"]
    sdist_cext = [r for r in results if r.install_type == "sdist" and r.has_cext]
    abi3_pkgs = [r for r in results if r.install_type == "wheel-abi3"]
    conda_ft = [r for r in results if r.install_type == "conda" and r.is_safe]
    conda_violations = [r for r in results if r.install_type == "conda" and not r.is_safe]
    ft_wheels = [r for r in results if r.install_type == "wheel-ft"]
    pure_python = [r for r in results if r.install_type == "pure-python"]
    editable = [r for r in results if r.install_type == "editable"]

    print("=" * 68)
    print(f"Free-Threading Wheel ABI 审计 (期望 ABI: {expected_abi})")
    print("=" * 68)
    print(f"Python: {sys.version.split()[0]}")
    print(f"可执行文件: {sys.executable}")
    print()

    # 违规项（最高优先级）
    if violations or conda_violations:
        all_violations = violations + conda_violations
        print(f"┌{'─'*66}┐")
        print(f"│ [CRITICAL] 发现 {len(all_violations)} 个会重启用 GIL 的 C 扩展包！")
        print(f"└{'─'*66}┘")
        for r in sorted(all_violations, key=lambda x: x.name):
            print(f"  [X] {r.name:30s} {r.version:12s} {r.details}")
            for w in r.warnings:
                print(f"      → {w}")
        print()

    # 警告项
    warnings_list = sdist_cext + abi3_pkgs
    if warnings_list:
        print(f"┌{'─'*66}┐")
        print(f"│ [WARN] {len(warnings_list)} 个包 ft-safety 未经验证（需运行时检查）")
        print(f"└{'─'*66}┘")
        for r in sorted(warnings_list, key=lambda x: x.name):
            tag_marker = "sdist" if r.install_type == "sdist" else "abi3"
            print(f"  [!] {r.name:30s} {r.version:12s} [{tag_marker}]")
            if verbose:
                for w in r.warnings:
                    print(f"      → {w}")
        print()

    # 统计摘要
    print("─" * 68)
    print("审计摘要：")
    print(f"  ✅ ft-safe C 扩展 (cp{expected_abi[2:]}t wheel/conda) : {len(ft_wheels) + len(conda_ft)}")
    print(f"  ⚠️  sdist 编译的 C 扩展      : {len(sdist_cext)}")
    print(f"  ⚠️  abi3 stable ABI 包       : {len(abi3_pkgs)}")
    print(f"  ❌ 非 ft wheel (会拉 GIL)   : {len(violations)}")
    print(f"  ❌ conda 非 ft build        : {len(conda_violations)}")
    print(f"  📦 纯 Python 包            : {len(pure_python)}")
    if editable:
        print(f"  ✏️  editable 安装          : {len(editable)}")
    print(f"  ─────────────────────────────────────")
    print(f"  总计审计包数               : {len(results)}")
    print()

    if violations or conda_violations:
        print("┌──────────────────────────────────────────────────────────────┐")
        print("│ [行动建议]                                                   │")
        print("│ 1. 上述 [X] 标记的包会在 import 时静默重启用 GIL            │")
        print("│ 2. 升级到包含 cp314t wheel 的版本，或寻找替代包             │")
        print("│ 3. 运行 check_gil_state.py 验证 GIL 运行时状态             │")
        print("│ 4. CPU 密集任务考虑使用 multiprocessing 而非 threading      │")
        print("└──────────────────────────────────────────────────────────────┘")
    elif warnings_list:
        print("[OK] 无明确 GIL 拉起风险，但建议运行 check_gil_state.py 确认运行时状态")
    else:
        print("[OK] 所有已安装 C 扩展包均为 free-threading 兼容构建 ✓")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Free-Threading Wheel ABI 审计器 - 检测非 ft-safe 的 C 扩展包",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("packages", nargs="*", help="只审计指定包（默认审计全部）")
    ap.add_argument("-q", "--quiet", action="store_true", help="静默模式：仅输出违规项")
    ap.add_argument("-v", "--verbose", action="store_true", help="详细模式：输出所有警告详情")
    ap.add_argument("--strict", action="store_true", help="严格模式：sdist/abi3 也视为违规（CI 推荐）")
    ap.add_argument("--json", action="store_true", help="JSON 格式输出（供自动化工具解析）")
    args = ap.parse_args()

    expected_abi = get_expected_abi()
    if not expected_abi:
        if args.json:
            print(json.dumps({"error": "not a free-threading build", "status": "non-ft"}))
        elif not args.quiet:
            print("[INFO] 当前 Python 不是 free-threading 构建，ABI 审计不适用。")
        return 2

    # 收集所有已安装包
    all_packages: list[importlib_metadata.Distribution] = []
    if args.packages:
        for pkg_name in args.packages:
            try:
                dist = importlib_metadata.distribution(pkg_name)
                all_packages.append(dist)
            except importlib_metadata.PackageNotFoundError:
                print(f"[WARN] Package not found: {pkg_name}", file=sys.stderr)
    else:
        all_packages = list(importlib_metadata.distributions())

    # 执行审计
    results = [audit_package(dist, strict=args.strict) for dist in all_packages]
    results.sort(key=lambda r: r.name.lower())

    if args.json:
        output = {
            "expected_abi": expected_abi,
            "python_version": sys.version.split()[0],
            "total_packages": len(results),
            "violations": [asdict(r) for r in results if not r.is_safe],
            "warnings": [asdict(r) for r in results if r.warnings and r.is_safe],
            "ft_safe_count": sum(1 for r in results if r.is_safe and r.has_cext),
            "pure_python_count": sum(1 for r in results if r.install_type == "pure-python"),
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return 1 if output["violations"] else 0

    if args.quiet:
        # 静默模式：只输出违规项
        quiet_violations = [r for r in results if not r.is_safe]
        for r in quiet_violations:
            print(f"{r.name}=={r.version}: {'; '.join(r.warnings) or r.details}")
        return 1 if quiet_violations else 0

    print_report(results, expected_abi, verbose=args.verbose)

    # 返回退出码
    has_violations = any(not r.is_safe and r.install_type in ("wheel-gil", "conda") for r in results)
    if has_violations:
        return 1
    if args.strict:
        has_strict_violations = any(not r.is_safe for r in results)
        if has_strict_violations:
            return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
