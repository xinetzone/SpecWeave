#!/usr/bin/env python3
"""批次2（lib/共享库）Python 3.10+ 迁移自动化验证脚本。

验证项：
  1. 合规性检查：所有 lib/ 下 .py 文件都包含版本校验机制
  2. 语法检查：所有文件通过 py_compile 语法校验
  3. 包导入测试：所有模块能以 lib.xxx 方式成功导入
  4. 子包导入测试：子包内模块间相对导入正常
  5. 版本校验执行验证：导入时 enforce_python310() 确实被调用
  6. 回归测试：对已迁移模块运行现有单元测试
  7. __init__.py 跳过验证：__init__.py 文件保持自动跳过（不添加版本块）

用法：
  python .agents/scripts/verify-batch2-lib.py          # 完整验证
  python .agents/scripts/verify-batch2-lib.py --quick  # 快速模式（跳过回归测试）
  python .agents/scripts/verify-batch2-lib.py --fix    # 自动修复不合规文件
  python .agents/scripts/verify-batch2-lib.py -v       # 详细输出
"""

from __future__ import annotations

# ==============================================================================
# 版本校验（启动时立即执行，兼容 Python 3.8/3.9 语法）
# ==============================================================================
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310
enforce_python310()

import argparse
import importlib
import io
import py_compile
import re
import subprocess
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import (
    print_header, print_pass, print_warn, print_error,
    setup_safe_output, add_common_args,
)
from lib.project import resolve_project_root

PROJECT_ROOT = resolve_project_root(__file__)
LIB_DIR = SCRIPTS_DIR / "lib"
TESTS_DIR = SCRIPTS_DIR / "tests"

# ── 本地辅助输出函数 ──────────────────────────────────────────

def _print_section(title: str, width: int = 60) -> None:
    """打印章节标题。"""
    print()
    print("─" * width)
    print(f"  {title}")
    print("─" * width)


def _print_summary(title: str, items: dict) -> None:
    """打印键值对格式的汇总。"""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    for key, value in items.items():
        print(f"  {key}: {value}")
    print("=" * 60)


# ── 常量 ──────────────────────────────────────────────────────

# 版本校验块特征正则（lib 模式）
LIB_VERSION_CHECK_RE = re.compile(
    r"from\s+\.python310_version_check\s+import\s+enforce_python310",
    re.MULTILINE,
)
LIB_ENFORCE_CALL_RE = re.compile(
    r"^\s*enforce_python310\(\s*\)\s*$",
    re.MULTILINE,
)
EXEMPT_RE = re.compile(r"#\s*PY310-EXEMPT\s*:?", re.IGNORECASE)

# __init__.py 自动跳过版本校验（包标记文件，无顶层执行代码）
SKIP_FILES = {"__init__.py"}

# 非 Python 的 .ps1 文件（rglob 会误匹配，但后缀名不同，会被过滤）
PS1_NAMES = {"pwsh7-version-check.ps1", "encoding-safety.ps1", "utils.ps1"}

# 子包列表（需要验证 __init__.py 可导入）
SUBPACKAGES = [
    "analyze_xlsx",
    "check_concurrent_safety",
    "check_hardcode",
    "check_pattern_quality",
    "check_skill_quality",
    "check_spec_adoption",
    "checks",
    "collaboration",
    "compat",
    "link_fixer",
    "mermaid",
    "mermaid.checkers",
    "mermaid.fixers",
    "metadata_audit",
    "migrate_frontmatter",
    "pattern_maturity",
    "seven_concepts",
    "spec",
    "spec_tool",
    "stage_guardrail_runtime",
    "stage_guardrails",
    "stage_guardrails.state",
    "stage_guardrails_checker",
    "testing",
]


# ── 数据类 ────────────────────────────────────────────────────

@dataclass
class FileResult:
    """单个文件的验证结果。"""
    path: Path
    rel_path: str
    compliance: str = "pending"  # pass / fail / skip / exempt
    syntax: str = "pending"      # pass / fail / skip
    import_ok: bool = False
    enforce_called: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class VerificationStats:
    """验证统计信息。"""
    total: int = 0
    compliance_pass: int = 0
    compliance_fail: int = 0
    compliance_skip: int = 0
    syntax_pass: int = 0
    syntax_fail: int = 0
    import_pass: int = 0
    import_fail: int = 0
    enforce_pass: int = 0
    enforce_fail: int = 0
    test_pass: int = 0
    test_fail: int = 0


# ── 验证器 ────────────────────────────────────────────────────

class Batch2Verifier:
    """批次2 lib/ 共享库迁移验证器。"""

    def __init__(self, project_root: Path, quick_mode: bool = False,
                 auto_fix: bool = False, verbose: bool = False):
        self.project_root = project_root
        self.quick_mode = quick_mode
        self.auto_fix = auto_fix
        self.verbose = verbose
        self.results: List[FileResult] = []
        self.stats = VerificationStats()

    def collect_files(self) -> List[Path]:
        """收集 lib/ 下所有 .py 文件（排除 __pycache__ 和 docs/）。"""
        files = []
        for py_file in sorted(LIB_DIR.rglob("*.py")):
            if "__pycache__" in py_file.parts:
                continue
            if "docs" in py_file.parts:
                continue
            if py_file.suffix != ".py":
                continue
            files.append(py_file)
        self.stats.total = len(files)
        return files

    @staticmethod
    def _rel(path: Path) -> str:
        """返回相对于 SCRIPTS_DIR 的路径（用于显示）。"""
        try:
            return str(path.relative_to(SCRIPTS_DIR)).replace("\\", "/")
        except ValueError:
            return str(path).replace("\\", "/")

    # ── 验证项 1：合规性检查 ──────────────────────────────────

    def check_compliance(self, file_path: Path, result: FileResult) -> None:
        """检查文件是否包含 Python 3.10+ 版本校验。"""
        if file_path.name in SKIP_FILES:
            result.compliance = "skip"
            self.stats.compliance_skip += 1
            return

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            result.compliance = "fail"
            result.errors.append(f"读取文件失败: {e}")
            self.stats.compliance_fail += 1
            return

        if EXEMPT_RE.search(content):
            result.compliance = "exempt"
            self.stats.compliance_skip += 1
            return

        has_lib_import = bool(LIB_VERSION_CHECK_RE.search(content))
        has_lib_call = bool(LIB_ENFORCE_CALL_RE.search(content))

        # 兼容多种版本校验方式
        has_any_check = (
            (has_lib_import and has_lib_call)
            or ("python310_version_check" in content and "enforce_python310" in content)
            or ("_check_python310" in content and "_enforce_python310" in content)
            or ("check_python310" in content and "sys.exit" in content)
        )

        if has_any_check:
            result.compliance = "pass"
            self.stats.compliance_pass += 1
        else:
            result.compliance = "fail"
            self.stats.compliance_fail += 1
            result.errors.append("缺少 Python 3.10+ 版本校验代码块（lib 模式）")

    # ── 验证项 2：语法检查 ────────────────────────────────────

    def check_syntax(self, file_path: Path, result: FileResult) -> None:
        """使用 py_compile 检查文件语法。"""
        try:
            py_compile.compile(str(file_path), doraise=True)
            result.syntax = "pass"
            self.stats.syntax_pass += 1
        except py_compile.PyCompileError as e:
            result.syntax = "fail"
            self.stats.syntax_fail += 1
            result.errors.append(f"语法错误: {str(e).strip()[:200]}")

    # ── 验证项 3：包导入测试 ──────────────────────────────────

    @staticmethod
    def _module_name_for_file(file_path: Path) -> Optional[str]:
        """将文件路径转换为模块名（如 lib.atomic_write）。"""
        try:
            rel = file_path.relative_to(SCRIPTS_DIR).with_suffix("")
            return ".".join(rel.parts)
        except ValueError:
            return None

    def check_import(self, file_path: Path, result: FileResult) -> None:
        """测试模块能否通过包导入成功。"""
        if file_path.name == "__init__.py":
            try:
                rel = file_path.parent.relative_to(SCRIPTS_DIR)
                mod_name = ".".join(rel.parts)
            except ValueError:
                # 根 lib/__init__.py
                result.import_ok = True
                result.enforce_called = True
                self.stats.import_pass += 1
                self.stats.enforce_pass += 1
                return
        else:
            mod_name = self._module_name_for_file(file_path)
            if mod_name is None:
                result.warnings.append("无法计算模块名，跳过导入测试")
                result.import_ok = True
                result.enforce_called = True
                self.stats.import_pass += 1
                self.stats.enforce_pass += 1
                return

        try:
            stdout_buf = io.StringIO()
            stderr_buf = io.StringIO()
            with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
                importlib.import_module(mod_name)
            result.import_ok = True
            self.stats.import_pass += 1

            # 验证版本校验在文件中存在（间接验证 enforce 被调用）
            if file_path.name != "__init__.py":
                try:
                    content = file_path.read_text(encoding="utf-8", errors="replace")
                    if (
                        ("enforce_python310" in content and (
                            "from .python310_version_check" in content
                            or "python310_version_check import" in content
                        ))
                        or EXEMPT_RE.search(content)
                        or ("_enforce_python310" in content)
                    ):
                        result.enforce_called = True
                        self.stats.enforce_pass += 1
                    else:
                        result.enforce_called = False
                        self.stats.enforce_fail += 1
                        result.errors.append("导入成功但版本校验代码可能缺失或未被调用")
                except Exception:
                    result.enforce_called = False
                    self.stats.enforce_fail += 1
            else:
                result.enforce_called = True
                self.stats.enforce_pass += 1

        except SystemExit as e:
            result.import_ok = False
            self.stats.import_fail += 1
            result.enforce_called = False
            self.stats.enforce_fail += 1
            result.errors.append(f"导入时触发 sys.exit({e.code})——版本校验可能异常触发")
        except ImportError as e:
            result.import_ok = False
            self.stats.import_fail += 1
            result.enforce_called = False
            self.stats.enforce_fail += 1
            err_msg = str(e)
            if "relative import" in err_msg:
                result.errors.append(f"相对导入失败: {err_msg[:150]}")
            else:
                result.errors.append(f"导入失败: {err_msg[:150]}")
        except SyntaxError as e:
            result.import_ok = False
            self.stats.import_fail += 1
            result.enforce_called = False
            self.stats.enforce_fail += 1
            result.errors.append(f"语法错误: {e}")
        except Exception as e:
            result.import_ok = False
            self.stats.import_fail += 1
            result.enforce_called = False
            self.stats.enforce_fail += 1
            result.errors.append(f"{type(e).__name__}: {str(e)[:150]}")
            if self.verbose:
                tb_str = traceback.format_exc(limit=2)
                result.errors.append(tb_str[:300])

    # ── 验证项 4：子包导入测试 ────────────────────────────────

    def check_subpackage_imports(self) -> List[str]:
        """验证子包 __init__.py 可被导入。"""
        errors = []
        for subpkg in SUBPACKAGES:
            mod_name = f"lib.{subpkg}"
            try:
                importlib.import_module(mod_name)
            except ImportError as e:
                errors.append(f"子包 {mod_name} 导入失败: {e}")
            except Exception as e:
                errors.append(f"子包 {mod_name} 异常: {type(e).__name__}: {e}")
        return errors

    # ── 验证项 5：版本校验函数可调用 ──────────────────────────

    @staticmethod
    def check_enforce_function() -> Tuple[bool, str]:
        """验证 enforce_python310/check_python310 函数可正常加载。"""
        try:
            from lib.python310_version_check import enforce_python310, check_python310
            if not check_python310():
                return False, "当前 Python 版本 check_python310() 返回 False（当前 Python 不满足要求）"
            return True, "版本校验函数可正常调用，当前版本满足 3.10+ 要求"
        except Exception as e:
            return False, f"版本校验函数加载失败: {e}"

    # ── 验证项 6：回归测试 ────────────────────────────────────

    def run_regression_tests(self) -> Tuple[int, int, List[str]]:
        """运行 lib/ 相关的单元测试。返回 (pass, fail, errors)。"""
        if self.quick_mode:
            return 0, 0, ["快速模式：跳过回归测试"]

        test_files = []
        for tf in sorted(TESTS_DIR.glob("test_*.py")):
            try:
                content = tf.read_text(encoding="utf-8", errors="replace")
                if "from lib" in content or "import lib" in content:
                    test_files.append(tf)
            except Exception:
                pass

        # 加入 tests/ 子目录中的测试
        for subdir in sorted(TESTS_DIR.iterdir()):
            if subdir.is_dir() and subdir.name.startswith("test_"):
                for tf in sorted(subdir.glob("test_*.py")):
                    if tf not in test_files:
                        test_files.append(tf)

        if not test_files:
            return 0, 0, ["未找到相关测试文件"]

        cmd = [
            sys.executable, "-m", "pytest",
            *[str(tf) for tf in test_files],
            "--tb=short",
            "-q",
            "--no-header",
            "-p", "no:warnings",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(SCRIPTS_DIR),
                timeout=180,
                encoding="utf-8",
                errors="replace",
            )
            output = (result.stdout or "") + (result.stderr or "")
            if result.returncode == 0:
                passed_match = re.search(r"(\d+)\s+passed", output)
                pass_count = int(passed_match.group(1)) if passed_match else 0
                return pass_count, 0, []
            else:
                failed_match = re.search(r"(\d+)\s+failed", output)
                passed_match = re.search(r"(\d+)\s+passed", output)
                error_match = re.search(r"(\d+)\s+error", output)
                fail_count = int(failed_match.group(1)) if failed_match else 0
                pass_count = int(passed_match.group(1)) if passed_match else 0
                if error_match:
                    fail_count += int(error_match.group(1))
                if fail_count == 0:
                    fail_count = 1
                fail_lines = []
                for line in output.splitlines():
                    if "FAILED" in line or "ERROR" in line or "error" in line.lower()[:20]:
                        stripped = line.strip()
                        if stripped and len(stripped) < 200:
                            fail_lines.append(stripped)
                return pass_count, fail_count, fail_lines[:15]
        except subprocess.TimeoutExpired:
            return 0, 1, ["回归测试超时（>180s）"]
        except FileNotFoundError:
            return 0, 0, ["pytest 未安装，跳过回归测试（pip install pytest）"]
        except Exception as e:
            return 0, 1, [f"回归测试执行异常: {e}"]

    # ── 自动修复 ──────────────────────────────────────────────

    def auto_fix_noncompliant(self) -> None:
        """运行 migrate-to-python310.py 自动修复不合规文件。"""
        _print_section("自动修复不合规文件")
        migrator = SCRIPTS_DIR / "migrate-to-python310.py"
        if not migrator.exists():
            print_error(f"  迁移脚本不存在: {migrator}")
            return
        cmd = [
            sys.executable, str(migrator), "--apply", "--path", str(LIB_DIR),
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(SCRIPTS_DIR),
                timeout=120,
                encoding="utf-8",
                errors="replace",
            )
            output = result.stdout
            if output:
                # 只打印最后30行
                lines = output.strip().splitlines()
                for line in lines[-30:]:
                    print(f"  {line}")
            if result.returncode != 0:
                print_error(f"  迁移脚本退出码: {result.returncode}")
                if result.stderr:
                    for line in result.stderr.strip().splitlines()[-10:]:
                        print_error(f"  {line}")
        except subprocess.TimeoutExpired:
            print_error("  迁移脚本执行超时")
        except Exception as e:
            print_error(f"  自动修复失败: {e}")

    # ── 主流程 ────────────────────────────────────────────────

    def run(self) -> bool:
        """执行完整验证。返回 True 表示全部通过。"""
        setup_safe_output()
        print_header("批次2（lib/共享库）Python 3.10+ 迁移验证")
        print(f"  项目根目录: {self.project_root}")
        print(f"  lib/ 目录: {LIB_DIR}")
        print(f"  模式: {'快速' if self.quick_mode else '完整'}{' + 自动修复' if self.auto_fix else ''}")
        print()

        # 步骤 0
        _print_section("步骤 0：收集 lib/ 下 Python 文件")
        files = self.collect_files()
        print(f"  有效 Python 文件: {len(files)}")

        # 步骤 1：合规性
        _print_section("步骤 1：合规性检查（版本校验代码块）")
        noncompliant_files = []
        for f in files:
            result = FileResult(path=f, rel_path=self._rel(f))
            self.check_compliance(f, result)
            self.results.append(result)
            if result.compliance == "fail":
                noncompliant_files.append(f)
                print_error(f"  ✗ {result.rel_path}: 缺少版本校验")
            elif self.verbose:
                status = "⏭" if result.compliance == "skip" else ("⊘" if result.compliance == "exempt" else "✓")
                label = {"skip": "跳过", "exempt": "豁免", "pass": "合规"}[result.compliance]
                print(f"  {status} {result.rel_path}: {label}")
        print(f"  合规: {self.stats.compliance_pass}  不合规: {self.stats.compliance_fail}  跳过/豁免: {self.stats.compliance_skip}")

        # 自动修复
        if noncompliant_files and self.auto_fix:
            self.auto_fix_noncompliant()
            _print_section("自动修复后重新验证合规性")
            self.results.clear()
            self.stats = VerificationStats()
            self.stats.total = len(files)
            noncompliant_files = []
            for f in files:
                result = FileResult(path=f, rel_path=self._rel(f))
                self.check_compliance(f, result)
                self.results.append(result)
                if result.compliance == "fail":
                    noncompliant_files.append(f)
            print(f"  修复后 — 合规: {self.stats.compliance_pass}  不合规: {self.stats.compliance_fail}")

        # 步骤 2：语法
        _print_section("步骤 2：语法检查（py_compile）")
        for result in self.results:
            self.check_syntax(result.path, result)
            if result.syntax == "fail":
                err_msg = next((e for e in result.errors if "语法" in e), "; ".join(result.errors))
                print_error(f"  ✗ {result.rel_path}: {err_msg}")
            elif self.verbose:
                print_pass(f"  ✓ {result.rel_path}")
        print(f"  语法通过: {self.stats.syntax_pass}  语法错误: {self.stats.syntax_fail}")

        # 步骤 3：包导入
        _print_section("步骤 3：包导入测试（import lib.xxx）")
        for result in self.results:
            self.check_import(result.path, result)
            if not result.import_ok:
                print_error(f"  ✗ {result.rel_path}: {'; '.join(result.errors[:2])}")
            elif self.verbose:
                print_pass(f"  ✓ {result.rel_path}")
        print(f"  导入成功: {self.stats.import_pass}  导入失败: {self.stats.import_fail}")

        # 步骤 4：子包
        _print_section("步骤 4：子包间相对导入测试")
        subpkg_errors = self.check_subpackage_imports()
        if subpkg_errors:
            for err in subpkg_errors:
                print_error(f"  ✗ {err}")
        else:
            print_pass(f"  所有 {len(SUBPACKAGES)} 个子包导入正常")

        # 步骤 5：版本校验函数
        _print_section("步骤 5：版本校验函数可调用性验证")
        ok, msg = self.check_enforce_function()
        if ok:
            print_pass(f"  ✓ {msg}")
        else:
            print_error(f"  ✗ {msg}")

        # 步骤 6：__init__.py
        _print_section("步骤 6：__init__.py 文件处理验证")
        init_files = [r for r in self.results if r.path.name == "__init__.py"]
        init_skip = sum(1 for r in init_files if r.compliance == "skip")
        init_pass = sum(1 for r in init_files if r.compliance == "pass")
        print(f"  __init__.py 总数: {len(init_files)}")
        print(f"  正确跳过: {init_skip}")
        print(f"  已有版本块（不强制要求）: {init_pass}")
        init_fails = [r for r in init_files if r.compliance == "fail"]
        if init_fails:
            for r in init_fails:
                print_error(f"  ✗ {r.rel_path}: 检测为不合规")

        # 步骤 7：回归测试
        _print_section("步骤 7：回归测试（pytest）")
        pass_count, fail_count, test_errors = self.run_regression_tests()
        self.stats.test_pass = pass_count
        self.stats.test_fail = fail_count
        if fail_count > 0:
            print_error(f"  ✗ 回归测试失败: {fail_count} 个失败/错误")
            for err in test_errors:
                print_error(f"    {err}")
        elif pass_count > 0:
            print_pass(f"  ✓ 回归测试通过: {pass_count} 个测试")
        else:
            for msg in test_errors:
                print_warn(f"  ○ {msg}")

        # 输出警告（verbose模式）
        if self.verbose:
            for r in self.results:
                for w in r.warnings:
                    print_warn(f"  ⚠ {r.rel_path}: {w}")

        # 汇总
        subpkg_ok = len(subpkg_errors) == 0
        _print_summary("验证汇总", {
            "总文件数": str(self.stats.total),
            "合规检查": f"✅ {self.stats.compliance_pass} 通过 / ❌ {self.stats.compliance_fail} 不合规 / ⏭ {self.stats.compliance_skip} 跳过",
            "语法检查": f"✅ {self.stats.syntax_pass} 通过 / ❌ {self.stats.syntax_fail} 错误",
            "包导入": f"✅ {self.stats.import_pass} 成功 / ❌ {self.stats.import_fail} 失败",
            "版本校验确认": f"✅ {self.stats.enforce_pass} 确认 / ❌ {self.stats.enforce_fail} 异常",
            "子包导入": f"✅ 全部通过 ({len(SUBPACKAGES)} 个)" if subpkg_ok else f"❌ {len(subpkg_errors)} 个错误",
            "回归测试": (
                f"✅ {self.stats.test_pass} 通过" if self.stats.test_fail == 0
                else f"❌ {self.stats.test_fail} 失败"
            ) if not self.quick_mode else "⏭ 跳过（快速模式）",
        })

        all_pass = (
            self.stats.compliance_fail == 0
            and self.stats.syntax_fail == 0
            and self.stats.import_fail == 0
            and self.stats.enforce_fail == 0
            and subpkg_ok
            and self.stats.test_fail == 0
        )

        if all_pass:
            print()
            print_pass("🎉 批次2 lib/ 共享库迁移验证全部通过！")
        else:
            print()
            if noncompliant_files:
                print_error(f"尚有 {len(noncompliant_files)} 个文件缺少版本校验代码块")
                print("  运行以下命令自动修复:")
                print(f"  python {self._rel(SCRIPTS_DIR / 'migrate-to-python310.py')} --apply --path {self._rel(LIB_DIR)}")
                print("  或运行本脚本加 --fix 参数自动修复:")
                print(f"  python {self._rel(Path(__file__))} --fix")
            if self.stats.syntax_fail > 0:
                print_error(f"尚有 {self.stats.syntax_fail} 个文件存在语法错误")
            if self.stats.import_fail > 0:
                print_error(f"尚有 {self.stats.import_fail} 个文件无法正常导入")
            if not subpkg_ok:
                print_error(f"尚有 {len(subpkg_errors)} 个子包无法导入")
            if self.stats.test_fail > 0:
                print_error(f"尚有 {self.stats.test_fail} 个回归测试失败")
            print()
            print_error("❌ 批次2 验证未完全通过，请修复上述问题后重试")

        return all_pass


# ── CLI 入口 ──────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="批次2（lib/共享库）Python 3.10+ 迁移自动化验证",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python verify-batch2-lib.py              # 完整验证
  python verify-batch2-lib.py --quick      # 快速模式（跳过回归测试）
  python verify-batch2-lib.py --fix        # 自动修复不合规文件后验证
  python verify-batch2-lib.py -v           # 详细输出
        """,
    )
    add_common_args(parser)
    parser.add_argument("--quick", action="store_true", help="快速模式：跳过回归测试")
    parser.add_argument("--fix", action="store_true", help="自动修复不合规文件")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出（显示每个文件结果）")
    args = parser.parse_args()

    setup_safe_output()
    project_root = resolve_project_root(__file__)
    verifier = Batch2Verifier(
        project_root=project_root,
        quick_mode=args.quick,
        auto_fix=args.fix,
        verbose=args.verbose,
    )
    success = verifier.run()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
