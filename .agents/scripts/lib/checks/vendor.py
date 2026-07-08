"""vendor 目录合规性检查。

验证 vendor/ 目录结构、元数据完整性、子模块配置和 .gitignore 策略。

策略（2026-07-08 更新）：
- vendor/ 目录不被根 .gitignore 整体忽略
- 子模块通过 gitlink 跟踪，元数据文件正常纳入版本控制
- 手动管理依赖的源码须自行配置 .gitignore 规则
- --deep 模式使用 ThreadPoolExecutor 并行执行子模块检查（max_workers=min(N,8)）
- --deep 模式 git 命令使用优化参数：--no-optional-locks（减少锁开销）-uno（跳过未跟踪文件扫描）
- 所有检查步骤均记录精确耗时（time.perf_counter），文本/JSON 双模式输出

CLI 用法:
    python -m lib.checks.vendor              # 默认检查
    python -m lib.checks.vendor --fix        # 自动修复缺失模板
    python -m lib.checks.vendor --scan-refs  # 扫描引用
    python -m lib.checks.vendor --deep       # 深度验证子模块（并行）
    python -m lib.checks.vendor --json       # JSON 输出
    python check-vendor.py                   # 顶层入口脚本
"""

import argparse
import json
import re
import sys
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from lib.cli import print_header, print_pass, print_error, print_warn, print_summary, setup_safe_output
from lib.project import resolve_project_root

_DEBUG = False


def _set_debug(enabled: bool) -> None:
    global _DEBUG
    _DEBUG = enabled


def _debug(stage: str, msg: str) -> None:
    if not _DEBUG:
        return
    print(f"  [DEBUG:vendor] [{stage}] {msg}", file=sys.stderr, flush=True)


REQUIRED_LIB_FIELDS = ["名称", "版本", "来源", "引入日期", "用途", "许可证"]

VENDOR_ROOT_FILES = ["README.md", "VERSION.md"]

SCAN_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".vue", ".go", ".rs", ".java",
    ".c", ".cpp", ".h", ".hpp", ".rb", ".php", ".sh", ".bash", ".zsh",
    ".md", ".rst", ".txt", ".yaml", ".yml", ".json", ".toml", ".ini",
    ".cfg", ".conf", ".html", ".css", ".scss", ".less",
}

README_TEMPLATE = """# Vendor 依赖管理

本目录存放项目引入的外部依赖，通过 Git 子模块和手动管理两种方式引入。

## 依赖清单

| 名称 | 类型 | 版本 | 引入日期 | 用途 |
|---|---|---|---|---|
| （暂无依赖） | - | - | - | - |

## 管理说明

- **Git 子模块（third_party）**：第三方只读依赖，固定 commit，禁止本地修改
- **Git 子模块（owned_collab）**：自有协作项目，跟踪分支，允许开发
- **手动管理依赖**：仅提交元数据（README.md），源码通过 .gitignore 忽略

## 更新记录

- 初始化：创建 vendor 目录结构
"""

VERSION_TEMPLATE = """# Vendor 版本清单

| 库名称 | 版本号 | 来源 | 引入日期 | 许可证 | 类型 | 跟踪分支 | 用途 |
|---|---|---|---|---|---|---|---|

## 更新记录

- 初始化：创建版本清单
"""

LIB_README_TEMPLATE = """# {lib_name}

- **名称**：{lib_name}
- **版本**：
- **来源**：
- **引入日期**：
- **用途**：
- **许可证**：

## 修改记录

（如有定制修改，请在此记录）
"""


def _check_gitignore_rule(project_root: Path) -> bool:
    """检查 .gitignore 是否正确配置 vendor 策略。

    新策略：vendor/ 目录不被整体忽略，子模块通过 gitlink 跟踪。
    - .gitignore 不存在 → False
    - .gitignore 包含 `vendor/` 整体忽略规则 → False（会阻塞子模块操作）
    - .gitignore 包含 `vendor/*` 但无对应白名单 → False（同样会阻塞新子模块）
    - .gitignore 不包含 vendor 忽略规则 → True（正确：vendor 目录开放）
    """
    gi = project_root / ".gitignore"
    _debug("gitignore", f"检查路径: {gi}")
    if not gi.exists():
        _debug("gitignore", ".gitignore 文件不存在，返回 False")
        return False
    content = gi.read_text(encoding="utf-8")
    for lineno, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            _debug("gitignore", f"  L{lineno}: 跳过空行/注释 -> {stripped!r}")
            continue
        if stripped == "vendor/" or stripped == "vendor" or stripped == "vendor\\":
            _debug("gitignore", f"  L{lineno}: 命中 vendor 整体忽略规则 {stripped!r}，返回 False")
            return False
        if stripped == "vendor/*" or stripped == "vendor\\*":
            _debug("gitignore", f"  L{lineno}: 命中 vendor/* 忽略规则，返回 False")
            return False
        _debug("gitignore", f"  L{lineno}: 非 vendor 规则 -> {stripped!r}")
    _debug("gitignore", "未发现 vendor 整体忽略规则，返回 True")
    return True


def _load_submodule_paths(project_root: Path) -> set[str]:
    """从 .gitmodules 解析所有子模块路径，同时检测 .git 文件标识的子模块。"""
    paths: set[str] = set()
    gm = project_root / ".gitmodules"
    _debug("submodule", f"加载子模块路径，项目根: {project_root}")
    if gm.exists():
        _debug("submodule", f".gitmodules 存在: {gm}")
        text = gm.read_text(encoding="utf-8")
        for m in re.finditer(r"^\s*path\s*=\s*(.+)$", text, re.MULTILINE):
            p = m.group(1).strip()
            if p:
                normalized = p.replace("\\", "/")
                paths.add(normalized)
                _debug("submodule", f"  .gitmodules 解析到子模块: {normalized}")
    else:
        _debug("submodule", ".gitmodules 不存在")
    vendor_dir = project_root / "vendor"
    if vendor_dir.is_dir():
        _debug("submodule", f"扫描 vendor/ 目录下的 .git 文件标识: {vendor_dir}")
        for child in sorted(vendor_dir.iterdir(), key=lambda p: p.name.lower()):
            if child.is_dir() and (child / ".git").exists():
                rel = child.relative_to(project_root).as_posix()
                if rel not in paths:
                    _debug("submodule", f"  通过 .git 文件发现未登记子模块: {rel}")
                paths.add(rel)
            elif child.is_dir():
                _debug("submodule", f"  {child.name}/ 无 .git 文件（非子模块目录）")
    else:
        _debug("submodule", "vendor/ 目录不存在，跳过 .git 文件扫描")
    _debug("submodule", f"最终子模块集合: {sorted(paths)}")
    return paths


def _get_libs(vendor_dir: Path) -> list[Path]:
    """获取 vendor 下的非子模块库目录（排除点目录、文件、子模块）。"""
    _debug("libs", f"扫描手动管理依赖目录: {vendor_dir}")
    if not vendor_dir.is_dir():
        _debug("libs", "vendor 目录不存在，返回空列表")
        return []
    submodule_paths: set[str] = set()
    project_root = vendor_dir.parent
    gm = project_root / ".gitmodules"
    if gm.exists():
        text = gm.read_text(encoding="utf-8")
        for m in re.finditer(r"^\s*path\s*=\s*(.+)$", text, re.MULTILINE):
            submodule_paths.add(m.group(1).strip().replace("\\", "/"))
        _debug("libs", f"从 .gitmodules 加载子模块路径: {sorted(submodule_paths)}")
    libs = []
    for child in sorted(vendor_dir.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir():
            _debug("libs", f"  跳过（非目录）: {child.name}")
            continue
        if child.name.startswith("."):
            _debug("libs", f"  跳过（点目录）: {child.name}")
            continue
        rel = child.relative_to(project_root).as_posix()
        if rel in submodule_paths:
            _debug("libs", f"  跳过（子模块，.gitmodules 登记）: {rel}")
            continue
        if (child / ".git").exists():
            _debug("libs", f"  跳过（子模块，含 .git 文件）: {rel}")
            continue
        _debug("libs", f"  识别为手动管理依赖: {rel}")
        libs.append(child)
    _debug("libs", f"手动管理依赖共 {len(libs)} 个: {[l.name for l in libs]}")
    return libs


def _check_lib_readme(lib_dir: Path) -> tuple[bool, list[str]]:
    """检查单个手动管理依赖的 README.md 元数据完整性。

    返回 (是否通过, 问题列表)。
    """
    issues: list[str] = []
    readme = lib_dir / "README.md"
    _debug("readme", f"检查 {lib_dir.name} 的 README: {readme}")
    if not readme.exists():
        _debug("readme", f"  {lib_dir.name} 缺少 README.md")
        issues.append(f"{lib_dir.name}：缺少 README.md 元数据文件")
        return False, issues
    content = readme.read_text(encoding="utf-8")
    missing = []
    for f in REQUIRED_LIB_FIELDS:
        marker1 = f"**{f}**"
        marker2 = f"**{f}**："
        if marker1 not in content and marker2 not in content:
            missing.append(f)
    _debug("readme", f"  {lib_dir.name} 字段检查: 必需={REQUIRED_LIB_FIELDS}, 缺失={missing}")
    for f in missing:
        issues.append(f"{lib_dir.name}/README.md：缺少必需字段「{f}」")
    return (len(issues) == 0), issues


def _should_scan_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SCAN_EXTENSIONS


def _is_comment_line(line: str, ext: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if ext in {".py", ".rb", ".sh", ".bash", ".zsh", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf"}:
        return stripped.startswith("#")
    if ext in {".js", ".ts", ".tsx", ".jsx", ".vue", ".go", ".rs", ".java", ".c", ".cpp", ".h", ".hpp", ".php"}:
        return stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*")
    if ext in {".html"}:
        return stripped.startswith("<!--")
    if ext in {".md", ".rst"}:
        return False
    return False


def _scan_refs(project_root: Path, vendor_dir: Path) -> dict[str, list[str]]:
    """扫描代码中对 vendor/ 路径的引用（排除 vendor/ 目录自身）。"""
    refs: dict[str, list[str]] = {}
    vendor_resolved = vendor_dir.resolve()
    skip_dirs = {".git", "__pycache__", "node_modules", ".venv", ".temp", ".agents"}
    _debug("scan-refs", f"开始扫描 vendor/ 引用，项目根: {project_root}")
    _debug("scan-refs", f"vendor 解析路径: {vendor_resolved}")
    _debug("scan-refs", f"跳过目录: {sorted(skip_dirs)}")
    scanned = 0
    skipped_resolved = 0
    skipped_dir = 0
    skipped_ext = 0
    read_errors = 0
    for path in project_root.rglob("*"):
        if not _should_scan_file(path):
            skipped_ext += 1
            continue
        scanned += 1
        try:
            resolved = path.resolve()
            if str(resolved).startswith(str(vendor_resolved)):
                skipped_resolved += 1
                continue
        except OSError as e:
            _debug("scan-refs", f"  路径解析失败 {path}: {e}")
            read_errors += 1
            continue
        rel_parts = path.relative_to(project_root).parts
        if any(part in skip_dirs for part in rel_parts):
            skipped_dir += 1
            continue
        ext = path.suffix.lower()
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as e:
            _debug("scan-refs", f"  读取失败 {path}: {e}")
            read_errors += 1
            continue
        matches = []
        for i, line in enumerate(lines, 1):
            if _is_comment_line(line, ext):
                continue
            if "vendor/" in line or "vendor\\" in line:
                matches.append(f"  L{i}: {line.strip()}")
        if matches:
            rel = path.relative_to(project_root).as_posix()
            refs[rel] = matches
            _debug("scan-refs", f"  发现引用 {rel}: {len(matches)} 处")
    _debug("scan-refs", f"扫描完成: 扫描文件={scanned}, 跳过(扩展名)={skipped_ext}, "
           f"跳过(vendor内)={skipped_resolved}, 跳过(忽略目录)={skipped_dir}, "
           f"读取错误={read_errors}, 命中文件={len(refs)}")
    return refs


def _create_templates(project_root: Path, vendor_dir: Path) -> list[str]:
    """创建标准模板文件，返回创建的文件路径列表（不覆盖已有文件）。"""
    created: list[str] = []
    _debug("templates", f"创建模板，目标目录: {vendor_dir}")
    vendor_dir.mkdir(parents=True, exist_ok=True)
    readme = vendor_dir / "README.md"
    if not readme.exists():
        readme.write_text(README_TEMPLATE, encoding="utf-8")
        created.append("vendor/README.md")
        _debug("templates", "已创建 vendor/README.md")
    else:
        _debug("templates", "vendor/README.md 已存在，跳过")
    version = vendor_dir / "VERSION.md"
    if not version.exists():
        version.write_text(VERSION_TEMPLATE, encoding="utf-8")
        created.append("vendor/VERSION.md")
        _debug("templates", "已创建 vendor/VERSION.md")
    else:
        _debug("templates", "vendor/VERSION.md 已存在，跳过")
    libs = _get_libs(vendor_dir)
    for lib in libs:
        lib_readme = lib / "README.md"
        if not lib_readme.exists():
            content = LIB_README_TEMPLATE.format(lib_name=lib.name)
            lib_readme.write_text(content, encoding="utf-8")
            created.append(f"vendor/{lib.name}/README.md")
            _debug("templates", f"已创建 vendor/{lib.name}/README.md")
        else:
            _debug("templates", f"vendor/{lib.name}/README.md 已存在，跳过")
    _debug("templates", f"模板创建完成，共创建 {len(created)} 个文件: {created}")
    return created


def run(project_root: Path, args) -> int:
    """vendor 目录合规性检查主入口。

    支持 args 属性：fix, scan_refs, deep, debug, json, path。
    返回退出码：0=通过，1=有错误。
    """
    debug = getattr(args, "debug", False)
    use_json = getattr(args, "json", False)
    _set_debug(debug)

    _t_total_start = time.perf_counter()
    _t_step_start: float | None = None
    _step_timings: list[tuple[str, float]] = []

    def _start_step(name: str) -> None:
        nonlocal _t_step_start
        _t_step_start = time.perf_counter()
        _debug("timing", f"步骤开始: {name}")

    def _end_step(name: str) -> float:
        nonlocal _t_step_start
        if _t_step_start is None:
            return 0.0
        elapsed_ms = (time.perf_counter() - _t_step_start) * 1000
        _step_timings.append((name, elapsed_ms))
        _debug("timing", f"步骤完成: {name} ({elapsed_ms:.1f}ms)")
        _t_step_start = None
        return elapsed_ms

    def _fmt_ms(ms: float) -> str:
        if ms < 1:
            return f"{ms*1000:.0f}μs"
        if ms < 1000:
            return f"{ms:.1f}ms"
        return f"{ms/1000:.2f}s"

    if debug:
        _debug("run", f"vendor 检查启动，项目根: {project_root}")
        _debug("run", f"args: fix={getattr(args, 'fix', False)}, "
               f"scan_refs={getattr(args, 'scan_refs', False)}, "
               f"deep={getattr(args, 'deep', False)}, "
               f"json={use_json}")

    vendor_dir = project_root / "vendor"
    errors = 0
    warnings = 0
    passes = 0
    results: dict = {
        "tool": "vendor-check",
        "version": "1.0.0",
        "project_root": str(project_root),
        "vendor_dir": str(vendor_dir),
        "checks": [],
        "step_timings_ms": [],
        "summary": {},
    }

    def _record(name: str, status: str, message: str, details: list | None = None, duration_ms: float | None = None) -> None:
        entry = {"name": name, "status": status, "message": message}
        if details:
            entry["details"] = details
        if duration_ms is not None:
            entry["duration_ms"] = round(duration_ms, 1)
        results["checks"].append(entry)

    _debug("run", f"vendor_dir 路径: {vendor_dir}, exists={vendor_dir.exists()}")

    if not vendor_dir.exists():
        _debug("run", "vendor 目录不存在")
        if getattr(args, "fix", False):
            _start_step("create_vendor")
            created = _create_templates(project_root, vendor_dir)
            step_ms = _end_step("create_vendor")
            if use_json:
                _record("vendor_dir", "pass", "vendor 目录不存在，已自动创建标准结构", created, step_ms)
                total_ms = (time.perf_counter() - _t_total_start) * 1000
                results["step_timings_ms"] = [{"step": n, "duration_ms": round(t, 1)} for n, t in _step_timings]
                results["total_duration_ms"] = round(total_ms, 1)
                results["summary"] = {"pass": len(created) + 1, "warn": 0, "error": 0}
                results["passed"] = True
                print(json.dumps(results, ensure_ascii=False, indent=2))
                return 0
            print_header("vendor 目录合规性检查")
            print()
            print("  vendor 目录不存在，自动创建标准结构...")
            for f in created:
                print_pass(f"已创建 {f}")
            print()
            total_ms = (time.perf_counter() - _t_total_start) * 1000
            print_summary(len(created) + 1, 0, 0)
            print()
            print_pass("vendor 目录已创建，请在其中添加依赖")
            _debug("timing", f"总耗时: {_fmt_ms(total_ms)}")
            return 0
        if use_json:
            total_ms = (time.perf_counter() - _t_total_start) * 1000
            _record("vendor_dir", "warn", "vendor 目录不存在", ["运行 with --fix 可自动创建标准目录结构"])
            results["step_timings_ms"] = [{"step": n, "duration_ms": round(t, 1)} for n, t in _step_timings]
            results["total_duration_ms"] = round(total_ms, 1)
            results["summary"] = {"pass": 0, "warn": 1, "error": 0}
            results["passed"] = False
            print(json.dumps(results, ensure_ascii=False, indent=2))
            return 0
        print_header("vendor 目录合规性检查")
        print()
        print_warn("vendor 目录不存在")
        print("  提示：运行 with --fix 可自动创建标准目录结构")
        total_ms = (time.perf_counter() - _t_total_start) * 1000
        print_summary(0, 1, 0)
        _debug("timing", f"总耗时: {_fmt_ms(total_ms)}")
        return 0

    if not use_json:
        print_header("vendor 目录合规性检查")
        print()

    _start_step("submodules")
    submodules = _load_submodule_paths(project_root)
    if use_json:
        sm_details = []
        for sm in sorted(submodules):
            sm_dir = project_root / sm
            sm_init = sm_dir.is_dir() and (sm_dir / ".git").exists()
            sm_details.append({"path": sm, "initialized": sm_init})
            if sm_init:
                passes += 1
            else:
                warnings += 1
        sm_ms = _end_step("submodules")
        _record("submodules", "pass" if submodules else "info",
                f"检测到 {len(submodules)} 个 Git 子模块" if submodules else "未检测到 Git 子模块",
                sm_details if submodules else None, sm_ms)
    else:
        if submodules:
            print(f"1. 检测到 {len(submodules)} 个 Git 子模块：")
            for sm in sorted(submodules):
                sm_dir = project_root / sm
                sm_git = sm_dir / ".git"
                sm_init = sm_dir.is_dir() and sm_git.exists()
                _debug("run", f"子模块 {sm}: 目录存在={sm_dir.is_dir()}, .git存在={sm_git.exists()}, 已初始化={sm_init}")
                status = " [未初始化]" if not sm_init else ""
                print_pass(f"子模块 {sm}{status}")
                if sm_init:
                    passes += 1
                else:
                    warnings += 1
                    print_warn(f"  子模块 {sm} 未初始化，需运行 git submodule update --init")
        else:
            print("1. 未检测到 Git 子模块")
        sm_ms = _end_step("submodules")
        print(f"   耗时: {_fmt_ms(sm_ms)}")
        print()

    _start_step("gitignore")
    if not use_json:
        print("2. 检查 .gitignore 配置...")
    gi_ok = _check_gitignore_rule(project_root)
    if not gi_ok:
        gi = project_root / ".gitignore"
        if not gi.exists():
            msg = ".gitignore 文件不存在"
            if use_json:
                gi_ms = _end_step("gitignore")
                _record("gitignore", "error", msg, duration_ms=gi_ms)
            else:
                _debug("run", ".gitignore 不存在 -> ERROR")
                gi_ms = _end_step("gitignore")
                print_error(msg)
                print(f"   耗时: {_fmt_ms(gi_ms)}")
        else:
            msg = ".gitignore 包含 vendor/ 整体忽略规则，会阻塞子模块操作（应移除 vendor/ 忽略规则）"
            if use_json:
                gi_ms = _end_step("gitignore")
                _record("gitignore", "error", msg, duration_ms=gi_ms)
            else:
                _debug("run", ".gitignore 包含 vendor 忽略规则 -> ERROR")
                gi_ms = _end_step("gitignore")
                print_error(msg)
                print(f"   耗时: {_fmt_ms(gi_ms)}")
        errors += 1
    else:
        msg = ".gitignore 配置正确（vendor/ 目录未被整体忽略）"
        gi_ms = _end_step("gitignore")
        if use_json:
            _record("gitignore", "pass", msg, duration_ms=gi_ms)
        else:
            _debug("run", ".gitignore 配置正确 -> PASS")
            print_pass(msg)
            print(f"   耗时: {_fmt_ms(gi_ms)}")
        passes += 1
    if not use_json:
        print()

    _start_step("root_files")
    if use_json:
        missing_root = [f for f in VENDOR_ROOT_FILES if not (vendor_dir / f).exists()]
        root_details = [{"file": f, "exists": (vendor_dir / f).exists()} for f in VENDOR_ROOT_FILES]
        if missing_root:
            for f in missing_root:
                _record("root_files", "error", f"缺少必需文件 vendor/{f}")
            errors += len(missing_root)
            if getattr(args, "fix", False):
                fix_start = time.perf_counter()
                created = _create_templates(project_root, vendor_dir)
                fix_ms = (time.perf_counter() - fix_start) * 1000
                _record("root_files_fix", "pass", "--fix 模式：已自动创建缺失模板", created, fix_ms)
        else:
            _record("root_files", "pass", "vendor/ 根目录必需文件完整", root_details)
            passes += len(VENDOR_ROOT_FILES)
        rf_ms = _end_step("root_files")
        for entry in results["checks"]:
            if entry["name"] in ("root_files", "root_files_fix") and "duration_ms" not in entry:
                entry["duration_ms"] = round(rf_ms, 1)
    else:
        print("3. 检查 vendor/ 根目录必需文件...")
        missing_root = [f for f in VENDOR_ROOT_FILES if not (vendor_dir / f).exists()]
        _debug("run", f"根文件检查: 必需={VENDOR_ROOT_FILES}, 缺失={missing_root}")
        if missing_root:
            for f in missing_root:
                print_error(f"缺少必需文件 vendor/{f}")
            errors += len(missing_root)
            if getattr(args, "fix", False):
                print("  --fix 模式：自动创建缺失模板...")
                created = _create_templates(project_root, vendor_dir)
                for f in created:
                    print_pass(f"已创建 {f}")
        else:
            for f in VENDOR_ROOT_FILES:
                fpath = vendor_dir / f
                size = fpath.stat().st_size if fpath.exists() else 0
                _debug("run", f"根文件 vendor/{f} 存在, 大小={size} bytes")
                print_pass(f"vendor/{f} 存在")
            passes += len(VENDOR_ROOT_FILES)
        rf_ms = _end_step("root_files")
        print(f"   耗时: {_fmt_ms(rf_ms)}")
        print()

    _start_step("manual_libs")
    if use_json:
        libs = _get_libs(vendor_dir)
        if not libs:
            _record("manual_libs", "pass", "无手动管理依赖（所有依赖均为 Git 子模块）", duration_ms=0)
            passes += 1
        else:
            lib_errors = 0
            for lib in libs:
                ok, issues = _check_lib_readme(lib)
                if ok:
                    _record("manual_libs", "pass", f"{lib.name}：元数据完整")
                    passes += 1
                else:
                    for issue in issues:
                        _record("manual_libs", "error", issue)
                    lib_errors += 1
                    errors += len(issues)
                    if getattr(args, "fix", False):
                        lib_readme = lib / "README.md"
                        if not lib_readme.exists():
                            content = LIB_README_TEMPLATE.format(lib_name=lib.name)
                            lib_readme.write_text(content, encoding="utf-8")
                            _record("manual_libs_fix", "pass", f"--fix：已创建 {lib.name}/README.md 模板")
            if lib_errors == 0:
                passes += 1
        ml_ms = _end_step("manual_libs")
        for entry in results["checks"]:
            if entry["name"] in ("manual_libs", "manual_libs_fix") and "duration_ms" not in entry:
                entry["duration_ms"] = round(ml_ms, 1)
    else:
        print("4. 检查手动管理依赖的元数据...")
        libs = _get_libs(vendor_dir)
        if not libs:
            _debug("run", "无手动管理依赖（全部为子模块或目录为空）")
            print_pass("无手动管理依赖（所有依赖均为 Git 子模块）")
            passes += 1
        else:
            lib_errors = 0
            for lib in libs:
                ok, issues = _check_lib_readme(lib)
                if ok:
                    _debug("run", f"手动依赖 {lib.name}: 元数据完整 -> PASS")
                    print_pass(f"{lib.name}：元数据完整")
                    passes += 1
                else:
                    _debug("run", f"手动依赖 {lib.name}: 元数据问题 {len(issues)} 个 -> ERROR")
                    for issue in issues:
                        print_error(issue)
                    lib_errors += 1
                    errors += len(issues)
                    if getattr(args, "fix", False):
                        lib_readme = lib / "README.md"
                        if not lib_readme.exists():
                            content = LIB_README_TEMPLATE.format(lib_name=lib.name)
                            lib_readme.write_text(content, encoding="utf-8")
                            print_pass(f"  --fix：已创建 {lib.name}/README.md 模板")
            if lib_errors == 0:
                passes += 1
        ml_ms = _end_step("manual_libs")
        print(f"   耗时: {_fmt_ms(ml_ms)}")
        print()

    if getattr(args, "scan_refs", False):
        _start_step("scan_refs")
        if use_json:
            refs = _scan_refs(project_root, vendor_dir)
            if refs:
                for filepath, lines in sorted(refs.items()):
                    _record("scan_refs", "warn", f"{filepath}：发现对 vendor/ 路径的引用", lines)
                    warnings += 1
            else:
                _record("scan_refs", "pass", "未发现直接引用 vendor/ 路径的代码")
                passes += 1
            sr_ms = _end_step("scan_refs")
            for entry in results["checks"]:
                if entry["name"] == "scan_refs" and "duration_ms" not in entry:
                    entry["duration_ms"] = round(sr_ms, 1)
        else:
            print("5. 扫描代码中对 vendor/ 的引用...")
            refs = _scan_refs(project_root, vendor_dir)
            if refs:
                for filepath, lines in sorted(refs.items()):
                    print_warn(f"{filepath}：")
                    for ln in lines:
                        print(f"    {ln}")
                    warnings += 1
            else:
                _debug("run", "引用扫描未发现问题 -> PASS")
                print_pass("未发现直接引用 vendor/ 路径的代码")
                passes += 1
            sr_ms = _end_step("scan_refs")
            print(f"   耗时: {_fmt_ms(sr_ms)}")
            print()
    else:
        if not use_json:
            print("5. 引用扫描已跳过（使用 --scan-refs 启用）")
            print()

    if getattr(args, "deep", False):
        _start_step("deep")
        if not use_json:
            print("6. 子模块深度集成验证...")
            _debug("run", "--deep 模式：并行执行子模块深度集成验证")

        def _check_one_submodule(sm: str) -> dict:
            sm_dir = project_root / sm
            _debug("deep", f"  → 开始检查子模块: {sm}")
            if not sm_dir.is_dir():
                _debug("deep", f"  ← {sm} 目录不存在，跳过")
                return {"sm": sm, "status": "error", "msg": "目录不存在", "err": True, "elapsed_ms": 0.0}
            if not (sm_dir / ".git").exists():
                _debug("deep", f"  ← {sm} 未初始化（.git 文件不存在），跳过")
                return {"sm": sm, "status": "error", "msg": "未初始化（.git 文件不存在）", "err": True, "elapsed_ms": 0.0}
            try:
                t0 = time.perf_counter()
                _debug("deep", f"  ↻ {sm} 执行 git status --porcelain -uno")
                result = subprocess.run(
                    ["git", "--no-optional-locks", "status", "--porcelain", "-uno"],
                    capture_output=True, text=True, cwd=str(sm_dir),
                    timeout=10,
                )
                elapsed = (time.perf_counter() - t0) * 1000
                if result.returncode != 0:
                    _debug("deep", f"  ✗ {sm} git status 失败 ({elapsed:.1f}ms): {result.stderr.strip()[:80]}")
                    return {"sm": sm, "status": "warn",
                            "msg": f"git status 执行失败: {result.stderr.strip()[:80]}",
                            "stderr": result.stderr.strip(), "elapsed_ms": elapsed}
                if result.stdout.strip():
                    dirty = result.stdout.strip().splitlines()
                    _debug("deep", f"  ⚠ {sm} 有未提交变更（{len(dirty)} 个文件，{elapsed:.1f}ms）")
                    return {"sm": sm, "status": "warn",
                            "msg": f"子模块工作区有未提交变更（{len(dirty)} 个文件）",
                            "dirty_count": len(dirty), "elapsed_ms": elapsed}
                _debug("deep", f"  ✓ {sm} 工作区干净（{elapsed:.1f}ms）")
                return {"sm": sm, "status": "pass", "msg": "工作区干净（已跟踪文件无变更）", "elapsed_ms": elapsed}
            except FileNotFoundError:
                _debug("deep", f"  ✗ {sm} git 命令未找到")
                return {"sm": None, "status": "fatal", "msg": "git 命令未找到，无法验证子模块状态", "err": True, "elapsed_ms": 0.0}
            except subprocess.TimeoutExpired:
                elapsed = 10000.0
                _debug("deep", f"  ✗ {sm} git status 超时（>{elapsed:.0f}ms）")
                return {"sm": sm, "status": "warn", "msg": "git status 超时", "elapsed_ms": elapsed}
            except Exception as e:
                _debug("deep", f"  ✗ {sm} 检查异常: {e}")
                return {"sm": sm, "status": "error", "msg": f"检查异常: {e}", "err": True, "elapsed_ms": 0.0}

        sm_list = sorted(submodules)
        results_parallel: list[dict] = []
        if sm_list:
            max_workers = min(len(sm_list), 8)
            _debug("deep", f"并行检查 {len(sm_list)} 个子模块，max_workers={max_workers}")
            t_parallel_start = time.perf_counter()
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_sm = {executor.submit(_check_one_submodule, sm): sm for sm in sm_list}
                for future in as_completed(future_to_sm):
                    results_parallel.append(future.result())
            t_parallel_elapsed = (time.perf_counter() - t_parallel_start) * 1000
            results_parallel.sort(key=lambda r: r.get("sm") or "")

            _debug("deep", f"─── 并行执行汇总 ───")
            total_serial_ms = 0.0
            for r in results_parallel:
                sm_name = r.get("sm") or "(unknown)"
                ems = r.get("elapsed_ms", 0.0)
                total_serial_ms += ems
                st = r.get("status", "?")
                status_icon = {"pass": "✓", "warn": "⚠", "error": "✗", "fatal": "✗"}.get(st, "?")
                _debug("deep", f"  {status_icon} {sm_name}: {ems:.1f}ms [{st}]")
            if total_serial_ms > 0 and t_parallel_elapsed > 0:
                speedup = total_serial_ms / t_parallel_elapsed
                _debug("deep", f"  串行估计: {total_serial_ms:.1f}ms | 并行实际: {t_parallel_elapsed:.1f}ms | 加速比: {speedup:.2f}x")
            _debug("deep", f"────────────────────")
        else:
            _debug("deep", "无子模块，跳过深度检查")

        deep_errors = 0
        git_not_found = False
        for r in results_parallel:
            sm = r["sm"]
            status = r["status"]
            msg = r["msg"]
            ems = r.get("elapsed_ms")
            if status == "fatal":
                git_not_found = True
                break
            if status == "pass":
                if use_json:
                    _record("deep", "pass", f"{sm}：{msg}", duration_ms=ems)
                else:
                    _debug("deep", f"{sm} 工作区干净")
                    print_pass(f"  {sm}：{msg}")
                passes += 1
            elif status == "warn":
                if use_json:
                    _record("deep", "warn", f"{sm}：{msg}", duration_ms=ems)
                else:
                    _debug("deep", f"{sm} {msg}")
                    print_warn(f"  {sm}：{msg}")
                warnings += 1
            elif status == "error":
                if use_json:
                    _record("deep", "error", f"{sm}：{msg}", duration_ms=ems)
                else:
                    _debug("deep", f"{sm} {msg}")
                    print_error(f"  {sm}：{msg}")
                deep_errors += 1

        if git_not_found:
            if use_json:
                _record("deep", "error", "git 命令未找到，无法验证子模块状态")
            else:
                _debug("deep", "git 命令未找到")
                print_error("  git 命令未找到，无法验证子模块状态")
            deep_errors += 1

        errors += deep_errors
        dp_ms = _end_step("deep")
        if use_json:
            for entry in results["checks"]:
                if entry["name"] == "deep" and "duration_ms" not in entry:
                    entry["duration_ms"] = round(dp_ms, 1)
            if sm_list:
                serial_estimate = sum(r.get("elapsed_ms", 0.0) for r in results_parallel)
                results["parallel_summary"] = {
                    "submodules": [
                        {"path": r.get("sm"), "status": r.get("status"),
                         "elapsed_ms": round(r.get("elapsed_ms", 0.0), 1)}
                        for r in results_parallel
                    ],
                    "serial_estimate_ms": round(serial_estimate, 1),
                    "parallel_wall_ms": round(dp_ms, 1),
                    "speedup": round(serial_estimate / dp_ms, 2) if dp_ms > 0 else None,
                    "max_workers": min(len(sm_list), 8),
                }
        else:
            print(f"   耗时: {_fmt_ms(dp_ms)}（并行检查 {len(sm_list)} 个子模块）")
            print()
    else:
        if not use_json:
            _debug("run", "--deep 未启用，跳过深度验证")

    _debug("run", f"检查完成: passes={passes}, warnings={warnings}, errors={errors}")
    total_ms = (time.perf_counter() - _t_total_start) * 1000

    if use_json:
        results["step_timings_ms"] = [{"step": n, "duration_ms": round(t, 1)} for n, t in _step_timings]
        results["total_duration_ms"] = round(total_ms, 1)
        results["summary"] = {"pass": passes, "warn": warnings, "error": errors}
        results["passed"] = errors == 0
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_summary(passes, warnings, errors)
        print()
        print(f"  总耗时: {_fmt_ms(total_ms)}")
        for step_name, step_t in _step_timings:
            print(f"    - {step_name}: {_fmt_ms(step_t)}")
        print()
        _debug("timing", f"总耗时: {_fmt_ms(total_ms)}")

    if errors > 0:
        if not use_json:
            print_error("检查未通过，请修复上述错误")
        return 1
    if not use_json:
        print_pass("vendor 目录检查通过！")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """构建 vendor-check CLI 参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="vendor-check",
        description="vendor 目录合规性检查工具：验证 vendor/ 目录结构、元数据完整性、子模块配置和 .gitignore 策略",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python check-vendor.py                  # 默认检查（基础5项）
  python check-vendor.py --fix            # 自动创建缺失的标准模板文件
  python check-vendor.py --scan-refs      # 扫描代码中对 vendor/ 目录的引用
  python check-vendor.py --deep           # 子模块深度集成验证
  python check-vendor.py --json           # JSON 格式输出结果
  python check-vendor.py --fix --deep     # 组合使用：修复 + 深度验证
  python check-vendor.py --path /other/proj  # 指定项目路径
  python -m lib.checks.vendor --help      # 查看帮助
        """,
    )
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="指定项目根目录路径（默认自动发现项目根）",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        default=False,
        help="自动创建缺失的标准模板文件（vendor/README.md, vendor/VERSION.md, lib/README.md）",
    )
    parser.add_argument(
        "--scan-refs",
        action="store_true",
        default=False,
        help="扫描代码中对 vendor/ 路径的直接引用（排除 vendor/ 目录自身、.git/、.agents/ 等）",
    )
    parser.add_argument(
        "--deep",
        action="store_true",
        default=False,
        help="执行子模块深度集成验证：检查初始化状态、工作区清洁度（git status）",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="输出详细调试日志到 stderr（用于排查边界情况）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="以 JSON 格式输出检查结果（用于 CI 集成或程序化处理）",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="vendor-check 1.0.0",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """vendor-check 独立 CLI 入口。

    参数:
        argv: 命令行参数列表（None 则使用 sys.argv[1:]）。
    返回:
        退出码：0=通过，1=有错误。
    """
    setup_safe_output()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.path:
        project_root = Path(args.path).resolve()
    else:
        project_root = resolve_project_root(__file__)

    return run(project_root, args)


if __name__ == "__main__":
    sys.exit(main())
