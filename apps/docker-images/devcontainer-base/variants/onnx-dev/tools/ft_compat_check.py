#!/usr/bin/env python3
"""
Free-Threading (no-GIL) 包兼容性检查工具
基于 python-free-threading-package-exclusion-shim 模式的五步法实现。

用法:
  # 基本检查（使用内置已知不兼容列表）
  python ft_compat_check.py

  # 自定义要导入的包列表
  python ft_compat_check.py --import onnx onnxruntime onnxsim

  # 指定应当缺席的包（镜像构建期验证）
  python ft_compat_check.py --expect-absent onnxoptimizer torch

  # 运行时兼容模式（作为库导入，发出warnings）
  python -c "from ft_compat_check import runtime_check; runtime_check()"

  # JSON输出（CI集成）
  python ft_compat_check.py --json
"""
from __future__ import annotations

import dataclasses
import importlib
import importlib.util
import json
import sys
import sysconfig
import warnings
from typing import Any


@dataclasses.dataclass
class PkgResult:
    """单个包的检查结果"""
    name: str
    status: str  # "ok" | "import_error" | "absent" | "present_unexpected" | "crash"
    version: str | None = None
    error: str | None = None
    note: str | None = None


@dataclasses.dataclass
class FTReport:
    """完整兼容性报告"""
    is_free_threading: bool
    python_version: str
    gil_enabled: bool | None
    results: list[PkgResult]
    known_incompatible: dict[str, str]  # pkg -> reason
    alternatives: dict[str, str]  # pkg -> alternative info

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_free_threading": self.is_free_threading,
            "python_version": self.python_version,
            "gil_enabled": self.gil_enabled,
            "results": [dataclasses.asdict(r) for r in self.results],
            "known_incompatible": self.known_incompatible,
            "alternatives": self.alternatives,
            "summary": self.summary(),
        }

    def summary(self) -> dict[str, int]:
        counts = {"ok": 0, "import_error": 0, "absent": 0, "present_unexpected": 0, "crash": 0}
        for r in self.results:
            counts[r.status] = counts.get(r.status, 0) + 1
        return counts

    def passed(self) -> bool:
        """构建期检查：所有import成功且expected-absent包确实缺席"""
        return all(
            r.status in ("ok", "absent")
            for r in self.results
        )


# ── 已知不兼容包列表（持续维护） ──────────────────────────
KNOWN_INCOMPATIBLE: dict[str, str] = {
    "onnxoptimizer": "CPython内部API #111506，free-threading下ImportError",
    "triton": "不支持free-threading，import时临时启用GIL",
}

# 替代方案映射
ALTERNATIVES: dict[str, str] = {
    "onnxoptimizer": "onnxsim（已覆盖常量折叠、算子融合等核心优化）",
    "triton": "暂无可替代；需临时设PYTHON_GIL=1使用",
}

# 推荐核心包（onnx-dev场景默认值）
DEFAULT_IMPORT_PACKAGES: list[str] = [
    "numpy", "onnx", "onnxruntime", "onnxsim", "onnxscript",
]

DEFAULT_EXPECT_ABSENT: list[str] = [
    "onnxoptimizer",
]


def is_free_threading_build() -> tuple[bool, bool | None]:
    """检测当前Python是否为free-threading构建。
    返回 (is_ft_build, gil_currently_enabled)。
    """
    # 方法1：检查SOABI标签包含't'后缀（如 cpython-314t-x86_64-linux-gnu）
    soabi = sysconfig.get_config_var("SOABI") or ""
    is_ft = "t" in soabi.split("-")[1] if "-" in soabi else False

    # 方法2：Py_GIL_DISABLED 编译标志
    if not is_ft:
        gil_disabled = sysconfig.get_config_var("Py_GIL_DISABLED")
        is_ft = bool(gil_disabled)

    # 当前GIL状态
    gil_enabled = getattr(sys, "_is_gil_enabled", None)
    gil_enabled = gil_enabled() if gil_enabled is not None else None

    return is_ft, gil_enabled


def try_import(pkg_name: str) -> PkgResult:
    """尝试导入单个包，返回结果"""
    spec = importlib.util.find_spec(pkg_name)
    if spec is None:
        return PkgResult(name=pkg_name, status="absent")

    try:
        mod = importlib.import_module(pkg_name)
        ver = getattr(mod, "__version__", None)
        return PkgResult(name=pkg_name, status="ok", version=ver)
    except ImportError as e:
        return PkgResult(name=pkg_name, status="import_error", error=str(e))
    except Exception as e:
        return PkgResult(name=pkg_name, status="crash", error=f"{type(e).__name__}: {e}")


def check_packages(
    import_packages: list[str] | None = None,
    expect_absent: list[str] | None = None,
    extra_incompatible: dict[str, str] | None = None,
    extra_alternatives: dict[str, str] | None = None,
) -> FTReport:
    """执行完整兼容性检查。

    Parameters
    ----------
    import_packages : 要尝试导入的包列表（None=使用默认列表）
    expect_absent : 应当缺席的包列表（None=使用默认列表）
    extra_incompatible : 追加已知不兼容包 dict[pkg]->reason
    extra_alternatives : 追加替代方案 dict[pkg]->alternative_desc
    """
    is_ft, gil_enabled = is_free_threading_build()

    known = dict(KNOWN_INCOMPATIBLE)
    alts = dict(ALTERNATIVES)
    if extra_incompatible:
        known.update(extra_incompatible)
    if extra_alternatives:
        alts.update(extra_alternatives)

    pkgs_to_import = list(import_packages or DEFAULT_IMPORT_PACKAGES)
    pkgs_expect_absent = list(expect_absent or DEFAULT_EXPECT_ABSENT)

    results: list[PkgResult] = []

    # Step 2: 导入冒烟测试
    for pkg in pkgs_to_import:
        r = try_import(pkg)
        if is_ft and r.status == "ok" and pkg in known:
            r.note = f"WARNING: {pkg} 在已知不兼容列表中但导入成功，请验证运行时稳定性"
        results.append(r)

    # Step 1+3: 检查应当缺席的包
    for pkg in pkgs_expect_absent:
        spec = importlib.util.find_spec(pkg)
        if spec is not None:
            # 包存在但被期望缺席 → 尝试导入看是否真的不可用
            r = try_import(pkg)
            if r.status == "ok":
                results.append(PkgResult(
                    name=pkg, status="present_unexpected",
                    version=r.version,
                    note=f"包存在，但根据排除策略应当缺席。原因: {known.get(pkg, '未记录')}",
                ))
            else:
                # 存在但不能导入 → 标记absent（符合预期），附带错误信息
                results.append(PkgResult(
                    name=pkg, status="absent",
                    error=r.error,
                    note=f"包安装但无法导入（符合排除预期）: {known.get(pkg, '未知原因')}",
                ))
        else:
            results.append(PkgResult(
                name=pkg, status="absent",
                note=f"已正确排除。替代方案: {alts.get(pkg, '无')}",
            ))

    return FTReport(
        is_free_threading=is_ft,
        python_version=sys.version.split()[0],
        gil_enabled=gil_enabled,
        results=results,
        known_incompatible=known,
        alternatives=alts,
    )


def print_report(report: FTReport) -> None:
    """人类可读格式打印报告"""
    print("=" * 60)
    print("Free-Threading 包兼容性检查报告")
    print("=" * 60)
    print(f"  Python版本    : {report.python_version}")
    print(f"  Free-Threading: {'✅ 是 (cp314t/cp313t no-GIL)' if report.is_free_threading else '❌ 否 (标准GIL构建)'}")
    if report.gil_enabled is not None:
        print(f"  当前GIL状态   : {'🔒 已启用' if report.gil_enabled else '🔓 已禁用 (free-threading active)'}")
    print()

    # 结果表格
    print(f"{'包名':<20} {'状态':<20} {'版本/备注'}")
    print("-" * 70)
    status_emoji = {
        "ok": "✅ 正常",
        "absent": "🚫 缺席(符合预期)",
        "import_error": "❌ 导入失败",
        "present_unexpected": "⚠️  不应存在",
        "crash": "💥 崩溃",
    }
    for r in report.results:
        detail = r.version or ""
        if r.error:
            detail = f"{detail} | {r.error}"
        if r.note:
            detail = f"{detail} | {r.note}"
        print(f"  {r.name:<18} {status_emoji.get(r.status, r.status):<22} {detail}")

    print()
    s = report.summary()
    print(f"汇总: ✅{s['ok']}个正常, 🚫{s['absent']}个已排除, ❌{s['import_error']}个导入失败, ⚠️ {s['present_unexpected']}个异常存在, 💥{s['crash']}个崩溃")

    if report.is_free_threading:
        print("\n📋 已知不兼容包参考列表:")
        for pkg, reason in report.known_incompatible.items():
            alt = report.alternatives.get(pkg, "无")
            print(f"  - {pkg}: {reason}")
            print(f"    替代: {alt}")

    passed = report.passed()
    print()
    if passed:
        print("✅ 检查通过：所有包导入成功，排除包确认缺席")
    else:
        print("❌ 检查未通过：存在导入失败或异常存在的包（详见上方）")

    if not report.is_free_threading:
        print("\nℹ️  当前Python为标准GIL构建，不兼容包列表仅作参考（在GIL模式下这些包可能正常工作）")


def runtime_check(
    warn_packages: list[str] | None = None,
    extra_incompatible: dict[str, str] | None = None,
) -> None:
    """运行时兜底检查：在free-threading环境下检测已导入的不兼容包并发出warnings。
    可在应用入口处调用：from ft_compat_check import runtime_check; runtime_check()
    """
    is_ft, gil_enabled = is_free_threading_build()
    if not is_ft or (gil_enabled is not None and gil_enabled):
        return  # 非free-threading或GIL已启用，无需警告

    known = dict(KNOWN_INCOMPATIBLE)
    if extra_incompatible:
        known.update(extra_incompatible)

    check_list = warn_packages or list(known.keys())
    for pkg in check_list:
        if importlib.util.find_spec(pkg) is not None:
            try:
                importlib.import_module(pkg)
                warnings.warn(
                    f"{pkg} 在 free-threading 模式下可能不稳定。"
                    f"原因: {known.get(pkg, '未记录')}。"
                    f"建议: 设置 PYTHON_GIL=1 启用GIL，或使用替代方案。",
                    RuntimeWarning,
                    stacklevel=2,
                )
            except ImportError:
                pass  # 包存在但不能导入，不影响运行


def main() -> int:
    """CLI入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Free-Threading (no-GIL) Python 包兼容性检查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python ft_compat_check.py                              # 默认检查
  python ft_compat_check.py --import onnx onnxruntime    # 自定义导入列表
  python ft_compat_check.py --expect-absent torch        # 自定义排除列表
  python ft_compat_check.py --json                       # JSON输出（CI集成）
        """,
    )
    parser.add_argument(
        "--import", dest="import_pkgs", nargs="*", default=None,
        help="要尝试导入的包列表（空格分隔）",
    )
    parser.add_argument(
        "--expect-absent", dest="expect_absent", nargs="*", default=None,
        help="应当缺席（不兼容）的包列表（空格分隔）",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="以JSON格式输出报告",
    )
    parser.add_argument(
        "--runtime-check", action="store_true",
        help="运行时模式：仅对不兼容包发出warnings，不做完整报告",
    )
    args = parser.parse_args()

    if args.runtime_check:
        runtime_check()
        return 0

    report = check_packages(
        import_packages=args.import_pkgs,
        expect_absent=args.expect_absent,
    )

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        print_report(report)

    return 0 if report.passed() else 1


if __name__ == "__main__":
    sys.exit(main())
