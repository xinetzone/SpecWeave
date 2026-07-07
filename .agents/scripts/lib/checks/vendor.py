"""vendor 目录合规性检查。

验证 vendor/ 目录结构、元数据完整性、子模块配置和 .gitignore 策略。

策略（2026-07-07 更新）：
- vendor/ 目录不被根 .gitignore 整体忽略
- 子模块通过 gitlink 跟踪，元数据文件正常纳入版本控制
- 手动管理依赖的源码须自行配置 .gitignore 规则
"""

import re
import sys
import subprocess
from pathlib import Path

from lib.cli import print_header, print_pass, print_error, print_warn, print_summary

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
    """vendor 目录合规性检查主入口。"""
    debug = getattr(args, "debug", False)
    _set_debug(debug)

    if debug:
        _debug("run", f"vendor 检查启动，项目根: {project_root}")
        _debug("run", f"args: fix={getattr(args, 'fix', False)}, "
               f"scan_refs={getattr(args, 'scan_refs', False)}, "
               f"deep={getattr(args, 'deep', False)}")

    print_header("vendor 目录合规性检查")
    print()

    vendor_dir = project_root / "vendor"
    errors = 0
    warnings = 0
    passes = 0

    _debug("run", f"vendor_dir 路径: {vendor_dir}, exists={vendor_dir.exists()}")

    if not vendor_dir.exists():
        _debug("run", "vendor 目录不存在")
        if getattr(args, "fix", False):
            print("  vendor 目录不存在，自动创建标准结构...")
            created = _create_templates(project_root, vendor_dir)
            for f in created:
                print_pass(f"已创建 {f}")
            print()
            print_summary(2, 0, 0)
            print()
            print_pass("vendor 目录已创建，请在其中添加依赖")
            return 0
        print_warn("vendor 目录不存在")
        print("  提示：运行 with --fix 可自动创建标准目录结构")
        print_summary(0, 1, 0)
        return 0

    submodules = _load_submodule_paths(project_root)
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
    print()

    print("2. 检查 .gitignore 配置...")
    gi_ok = _check_gitignore_rule(project_root)
    if not gi_ok:
        gi = project_root / ".gitignore"
        if not gi.exists():
            _debug("run", ".gitignore 不存在 -> ERROR")
            print_error(".gitignore 文件不存在")
        else:
            _debug("run", ".gitignore 包含 vendor 忽略规则 -> ERROR")
            print_error(".gitignore 包含 vendor/ 整体忽略规则，会阻塞子模块操作（应移除 vendor/ 忽略规则）")
        errors += 1
    else:
        _debug("run", ".gitignore 配置正确 -> PASS")
        print_pass(".gitignore 配置正确（vendor/ 目录未被整体忽略）")
        passes += 1
    print()

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
    print()

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
    print()

    if getattr(args, "scan_refs", False):
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
        print()
    else:
        print("5. 引用扫描已跳过（使用 --scan-refs 启用）")
        print()

    if getattr(args, "deep", False):
        print("6. 子模块深度集成验证...")
        _debug("run", "--deep 模式：执行子模块深度集成验证")
        deep_errors = 0
        for sm in sorted(submodules):
            sm_dir = project_root / sm
            if not sm_dir.is_dir():
                print_error(f"  {sm}：目录不存在")
                deep_errors += 1
                continue
            if not (sm_dir / ".git").exists():
                print_error(f"  {sm}：未初始化（.git 文件不存在）")
                deep_errors += 1
                continue
            try:
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True, text=True, cwd=str(sm_dir),
                    timeout=10,
                )
                if result.returncode != 0:
                    _debug("deep", f"{sm} git status 失败: {result.stderr.strip()}")
                    print_warn(f"  {sm}：git status 执行失败: {result.stderr.strip()[:80]}")
                    warnings += 1
                elif result.stdout.strip():
                    dirty = result.stdout.strip().splitlines()
                    _debug("deep", f"{sm} 工作区不干净: {len(dirty)} 个变更")
                    print_warn(f"  {sm}：子模块工作区有未提交变更（{len(dirty)} 个文件）")
                    warnings += 1
                else:
                    _debug("deep", f"{sm} 工作区干净")
                    print_pass(f"  {sm}：工作区干净")
                    passes += 1
            except FileNotFoundError:
                _debug("deep", "git 命令未找到")
                print_error("  git 命令未找到，无法验证子模块状态")
                deep_errors += 1
            except subprocess.TimeoutExpired:
                _debug("deep", f"{sm} git status 超时")
                print_warn(f"  {sm}：git status 超时")
                warnings += 1
            except Exception as e:
                _debug("deep", f"{sm} 检查异常: {e}")
                print_error(f"  {sm}：检查异常: {e}")
                deep_errors += 1
        errors += deep_errors
        print()
    else:
        _debug("run", "--deep 未启用，跳过深度验证")

    _debug("run", f"检查完成: passes={passes}, warnings={warnings}, errors={errors}")

    print_summary(passes, warnings, errors)
    print()

    if errors > 0:
        print_error("检查未通过，请修复上述错误")
        return 1
    print_pass("vendor 目录检查通过！")
    return 0
