#!/usr/bin/env python3
"""CMake 自定义模块静态检查工具。

检查项：
1. 命名冲突检查（v1.0）：验证 cmake/ 目录下的自定义模块文件不使用 Find<Name>.cmake 等保留前缀
2. Include 顺序依赖检查（v1.1）：检测 function/macro 定义与 include 顺序之间的前向引用问题

命名规范：
- 自定义检测模块使用 Detect<Name>.cmake（如 DetectBLAS.cmake）
- 配置模块使用 Config<Name>.cmake（如 ConfigCompiler.cmake）
- 工具模块使用 <Function>.cmake（如 ProtoCompile.cmake）

保留前缀（禁止用于自定义模块）：
- Find*   — CMake 内置 find_package 模块（FindBLAS.cmake、FindBoost.cmake 等）
- CMake*  — CMake 内部模块
- cmake*  — CMake 内部模块（小写）
- _*      — 私有/内部模块前缀

Include 顺序规则（四层架构强制约束链）：
  Options.cmake → Dependencies.cmake → CompilerConfig.cmake → ProtoCompile.cmake
  → TargetBuild.cmake → WindowsDllCopy.cmake → Tests.cmake → Install.cmake
- function/macro 必须在调用之前通过 include() 加载
- 违反顺序会导致 "Unknown CMake command" 错误

CLI 用法:
    python check-cmake-naming.py                   # 默认检查当前项目（所有检查项）
    python check-cmake-naming.py --path /path/to   # 指定项目路径
    python check-cmake-naming.py --json            # JSON 输出
    python check-cmake-naming.py --skip-include-order  # 跳过 include 顺序检查
    python -m lib.checks.cmake_naming              # 模块方式调用
"""


# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

import argparse
import json
import re
import sys
import time
from pathlib import Path

from lib.cli import print_header, print_pass, print_error, print_warn, print_summary, setup_safe_output
from lib.project import resolve_project_root

_DEBUG = False

# CMake 保留命名前缀，自定义模块不得使用
RESERVED_PREFIXES = ("Find", "CMake", "cmake", "_")

# 标准 CMake 内置 Find 模块列表（常见示例，非穷举）
KNOWN_BUILTIN_FIND_MODULES = {
    "BLAS", "Boost", "CURL", "Curses", "Doxygen", "EXPAT", "FLEX",
    "FLTK", "GLEW", "GLUT", "GIF", "GTest", "GTK", "HDF5",
    "Iconv", "Intl", "JNI", "Java", "LAPACK", "LibXml2", "LibXslt",
    "Lua", "MPI", "Matlab", "OpenAL", "OpenGL", "OpenMP", "OpenSSL",
    "PNG", "PackageHandleStandardArgs", "PackageMessage", "Perl",
    "PhysFS", "PkgConfig", "PostgreSQL", "Protobuf", "Python3",
    "PythonInterp", "PythonLibs", "Qt", "QuickTime", "RTI", "Ruby",
    "SDL", "SWIG", "SelfPackers", "SQLite3", "Subversion", "TCL",
    "TIFF", "Threads", "Vulkan", "Wget", "X11", "ZLIB",
}

# 允许使用 Find 前缀的例外（通常是第三方提供的 find 模块）
ALLOWED_FIND_EXCEPTIONS: set[str] = set()

# CMake 内置命令与控制流关键字（白名单——这些命令总是可用，不需要先定义）
# 覆盖 CMake 3.15+ 常用命令，用于排除命令调用检测中的误报
CMAKE_BUILTIN_COMMANDS: frozenset[str] = frozenset({
    # ── 脚本命令 ──
    "cmake_minimum_required", "project", "set", "unset", "list", "string", "math",
    "file", "message", "include", "include_guard", "return", "break", "continue",
    "cmake_policy", "cmake_host_system_information", "cmake_parse_arguments",
    "cmake_language", "cmake_path", "separate_arguments", "mark_as_advanced",
    "configure_file", "option", "find_package", "find_library", "find_path",
    "find_file", "find_program", "get_filename_component",
    # ── 项目命令 ──
    "add_library", "add_executable", "add_custom_command", "add_custom_target",
    "add_subdirectory", "add_dependencies", "add_definitions", "add_compile_options",
    "add_compile_definitions", "add_link_options", "add_test", "enable_language",
    "enable_testing", "aux_source_directory", "build_command",
    # ── Target 命令 ──
    "target_link_libraries", "target_include_directories", "target_compile_definitions",
    "target_compile_features", "target_compile_options", "target_link_directories",
    "target_link_options", "target_sources", "target_precompile_headers",
    "set_target_properties", "get_target_property",
    # ── 属性与变量 ──
    "get_property", "set_property", "get_cmake_property", "get_directory_property",
    "set_directory_properties", "get_filename_component",
    # ── 安装 ──
    "install",
    # ── 测试 ──
    "set_tests_properties", "get_test_property",
    # ── 控制流（不是命令但在行首出现，会被命令匹配器捕获） ──
    "if", "elseif", "else", "endif",
    "foreach", "endforeach", "while", "endwhile",
    "function", "endfunction", "macro", "endmacro",
    "block", "endblock",
    # ── 旧式/兼容命令 ──
    "include_directories", "link_directories", "link_libraries",
    "compile_definitions", "compile_options", "compile_features",
    "remove_definitions", "subdirs", "use_mangled_mesa",
    "exec_program", "make_directory", "remove",
    # ── 生成器表达式辅助 ──
    "install", "export", "generate_product_set",
    # ── CTest/CDash ──
    "ctest_start", "ctest_configure", "ctest_build", "ctest_test", "ctest_memcheck",
    "ctest_submit", "ctest_empty_binary_directory",
    # ── 其他常见 ──
    "get_cmake_property", "variable_watch", "site_name",
    "output_required_files", "load_cache", "save_cache",
    "write_file", "read_file", # 旧式但常见
})


def _set_debug(enabled: bool) -> None:
    global _DEBUG
    _DEBUG = enabled


def _debug(stage: str, msg: str) -> None:
    if not _DEBUG:
        return
    print(f"  [DEBUG:cmake-naming] [{stage}] {msg}", file=sys.stderr, flush=True)


def _is_reserved_filename(filename: str) -> tuple[bool, str]:
    """检查文件名是否使用保留前缀。

    返回 (是否保留, 原因说明)。
    """
    if not filename.endswith(".cmake"):
        return False, ""

    name = filename[:-len(".cmake")]

    # 检查保留前缀
    for prefix in RESERVED_PREFIXES:
        if name.startswith(prefix):
            # Find* 是最常见的冲突源
            if prefix == "Find":
                pkg_name = name[len("Find"):]
                if filename in ALLOWED_FIND_EXCEPTIONS:
                    return False, ""
                if pkg_name in KNOWN_BUILTIN_FIND_MODULES:
                    return True, f"文件名 {filename} 使用保留前缀 'Find' 且匹配已知内置模块 Find{pkg_name}.cmake，" \
                                  f"会与 CMake 内置 find_package({pkg_name}) 产生命名冲突"
                return True, f"文件名 {filename} 使用保留前缀 'Find'，" \
                              f"Find<pkg>.cmake 是 CMake find_package 的标准命名约定，" \
                              f"自定义检测模块应使用 Detect{pkg_name}.cmake 替代"
            if prefix in ("CMake", "cmake"):
                return True, f"文件名 {filename} 使用保留前缀 '{prefix}'，这是 CMake 内部模块的命名空间"
            if prefix == "_":
                return True, f"文件名 {filename} 以下划线开头，这是私有模块的约定命名，不建议用于项目自定义模块"

    return False, ""


def _find_cmake_dirs(project_root: Path) -> list[Path]:
    """发现项目中的 cmake 模块目录。

    搜索策略：
    1. 根目录的 cmake/ 或 CMake/ 目录
    2. 常见 CMake 模块位置
    3. 去重：Windows/macOS 默认大小写不敏感文件系统，cmake 和 CMake 可能指向同一目录
    """
    cmake_dirs: list[Path] = []
    seen_resolved: set[str] = set()

    candidates = [
        project_root / "cmake",
        project_root / "CMake",
        project_root / "cmake" / "Modules",
        project_root / "CMake" / "Modules",
    ]

    for c in candidates:
        if c.is_dir():
            resolved = str(c.resolve())
            if resolved not in seen_resolved:
                seen_resolved.add(resolved)
                cmake_dirs.append(c)
                _debug("discovery", f"发现 CMake 目录: {c}")
            else:
                _debug("discovery", f"跳过重复目录（大小写不敏感文件系统）: {c}")

    return cmake_dirs


def _scan_cmake_modules(cmake_dir: Path) -> tuple[list[dict], list[dict]]:
    """扫描单个 cmake 目录下的所有 .cmake 文件。

    返回 (问题列表, 通过列表)。
    """
    errors: list[dict] = []
    passes: list[dict] = []

    for cmake_file in sorted(cmake_dir.rglob("*.cmake")):
        rel_path = cmake_file.relative_to(cmake_dir.parent if cmake_dir.name in ("cmake", "CMake") else cmake_dir).as_posix()
        filename = cmake_file.name

        is_reserved, reason = _is_reserved_filename(filename)
        if is_reserved:
            errors.append({
                "file": str(cmake_file),
                "filename": filename,
                "rel_path": rel_path,
                "reason": reason,
            })
            _debug("scan", f"  ✗ {rel_path}: {reason}")
        else:
            passes.append({
                "file": str(cmake_file),
                "filename": filename,
                "rel_path": rel_path,
            })
            _debug("scan", f"  ✓ {rel_path}")

    # 额外检查：CMakeLists.txt 中 include() 命令引用的文件是否存在
    root_cmakelists = cmake_dir.parent / "CMakeLists.txt"
    if root_cmakelists.exists():
        _debug("scan", f"检查 CMakeLists.txt include 引用: {root_cmakelists}")
        content = root_cmakelists.read_text(encoding="utf-8", errors="replace")
        # 简单匹配 include(xxx) 模式
        for m in re.finditer(r'^\s*include\s*\(\s*([^)\s]+)', content, re.MULTILINE):
            included = m.group(1).strip()
            if not included.endswith(".cmake"):
                # include(xxx) 不带扩展名会自动查找 xxx.cmake
                included_file = cmake_dir / f"{included}.cmake"
                if not included_file.exists():
                    _debug("scan", f"  ⚠ include({included}): 引用的文件 {included_file} 不存在")

    return errors, passes


# ────────────────────────────────────────────────────────────
# Include 顺序依赖检测（v1.1 新增）
# ────────────────────────────────────────────────────────────

# 匹配 function(Name ...) 或 macro(Name ...)
_RE_FUNCTION_DEF = re.compile(r'^\s*function\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)', re.MULTILINE)
_RE_MACRO_DEF = re.compile(r'^\s*macro\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)', re.MULTILINE)
# 匹配行首命令调用：command(args)
_RE_COMMAND_CALL = re.compile(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', re.MULTILINE)
# 匹配 include(Name) 或 include(Name.cmake)
_RE_INCLUDE_CALL = re.compile(r'^\s*include\s*\(\s*([A-Za-z0-9_./-]+)', re.MULTILINE)
# 匹配行注释（# 到行尾，但要避开字符串内的#；简化处理：#在字符串外才注释）
_RE_LINE_COMMENT = re.compile(r'(?<!\\)#.*$', re.MULTILINE)
# 匹配括号注释 #[[ ... ]]
_RE_BRACKET_COMMENT = re.compile(r'#\[\[.*?\]\]', re.DOTALL)
# 匹配字符串 "..."（简化，不处理转义引号的所有情况，足够用于过滤误匹配）
_RE_STRING_LITERAL = re.compile(r'"(?:[^"\\]|\\.)*"', re.DOTALL)

# 控制流闭合关键字（用于追踪嵌套深度）
_BLOCK_OPEN_KEYWORDS = {"function", "macro", "if", "foreach", "while", "block"}
_BLOCK_CLOSE_KEYWORDS = {"endfunction", "endmacro", "endif", "endforeach", "endwhile", "endblock"}


def _strip_noise(content: str) -> str:
    """移除 CMake 源码中的注释和字符串字面量，避免误匹配命令调用。"""
    # 先移除括号注释（多行）
    content = _RE_BRACKET_COMMENT.sub(" ", content)
    # 再移除行注释
    content = _RE_LINE_COMMENT.sub("", content)
    # 移除字符串字面量（避免字符串内的内容被误识别为命令）
    content = _RE_STRING_LITERAL.sub('""', content)
    return content


def _extract_top_level_definitions(content: str) -> set[str]:
    """提取文件中在顶层定义的 function/macro 名称集合。

    注意：只提取顶层定义（不在 function/macro 内部嵌套定义的）。
    CMake 允许 function 嵌套定义，但嵌套定义只在外层函数被调用时才生效，
    跨模块调用场景下顶层定义即可覆盖绝大多数情况。
    """
    cleaned = _strip_noise(content)
    # 追踪 function/macro 嵌套深度（只关心 function/macro 的嵌套，因为其他块
    # 如 if/foreach/while 内定义的 function/macro 仍然是全局的——CMake 中
    # function() 定义在任何位置都在当前作用域生效，而不是按块作用域）
    # 但为了避免误匹配 endfunction/endmacro 内部的模式，简单做深度计数。
    defs: set[str] = set()
    depth = 0
    # 逐行处理，追踪 function/endfunction 配对
    for line in cleaned.splitlines():
        stripped = line.strip()
        # 检查是否是 function( 或 macro( 开头（定义）
        m_func = _RE_FUNCTION_DEF.match(line)
        m_macro = _RE_MACRO_DEF.match(line)
        if m_func and depth == 0:
            defs.add(m_func.group(1))
            depth += 1
            continue
        if m_macro and depth == 0:
            defs.add(m_macro.group(1))
            depth += 1
            continue
        # 检查 endfunction/endmacro（简化：只要行首包含关键字就减深度）
        if re.match(r'^\s*endfunction\s*\(', line) or re.match(r'^\s*endmacro\s*\(', line):
            if depth > 0:
                depth -= 1
            continue
        # 注意：if/foreach/while 块内的 function() 定义仍然是全局的，
        # 所以我们不在 if/foreach/while 处增加 depth（不把它们当作作用域边界）
    return defs


def _extract_top_level_commands(content: str) -> set[str]:
    """提取文件顶层调用的命令名称集合（排除内置命令和已在本文件定义的命令）。

    "顶层"指不在 function/macro 定义体内——因为函数体内的命令在函数被调用时
    才执行，此时所有 include 已完成，不会产生前向引用问题。
    """
    cleaned = _strip_noise(content)
    commands: set[str] = set()
    depth = 0  # function/macro 嵌套深度
    for line in cleaned.splitlines():
        # 检查进入/离开 function/macro
        if _RE_FUNCTION_DEF.match(line) or _RE_MACRO_DEF.match(line):
            depth += 1
            continue
        if re.match(r'^\s*endfunction\s*\(', line) or re.match(r'^\s*endmacro\s*\(', line):
            if depth > 0:
                depth -= 1
            continue
        if depth > 0:
            continue  # 函数体内，跳过
        # 在顶层，提取命令调用
        m = _RE_COMMAND_CALL.match(line)
        if m:
            cmd = m.group(1)
            commands.add(cmd)
    return commands


def _resolve_include_file(include_name: str, cmake_dir: Path) -> Path | None:
    """将 include() 中的模块名解析为实际 .cmake 文件路径。

    include(Xxx) → cmake/Xxx.cmake
    include(Xxx.cmake) → cmake/Xxx.cmake
    """
    name = include_name.strip()
    # 移除可能的前导路径前缀（如 cmake/Modules/xxx），简化处理：只取basename
    base_name = Path(name).name
    # 处理 OPTIONAL/RESULT_VARIABLE 等 include 关键字参数——如果第一个参数不是文件名则跳过
    if base_name.upper() in ("OPTIONAL", "RESULT_VARIABLE", "NO_POLICY_SCOPE"):
        return None
    if not base_name.endswith(".cmake"):
        base_name = base_name + ".cmake"
    candidate = cmake_dir / base_name
    if candidate.exists():
        return candidate
    return None


def _parse_include_order(root_cmakelists: Path, cmake_dir: Path) -> list[Path]:
    """解析 CMakeLists.txt 中的顶层 include 顺序，返回被 include 的 .cmake 文件路径列表。

    简化策略：只解析 CMakeLists.txt 顶层（不在 if/foreach/function 等块内）的 include() 调用，
    因为条件块内的 include 是运行时条件的，静态分析无法确定是否执行。
    同时跳过 include_guard()、CMake 内置模块（不带路径的内置模块名）。
    """
    if not root_cmakelists.exists():
        return []
    content = root_cmakelists.read_text(encoding="utf-8", errors="replace")
    cleaned = _strip_noise(content)
    ordered_files: list[Path] = []
    seen: set[str] = set()
    # 追踪块深度（只追踪会导致条件执行的块：if/foreach/while/function/macro）
    depth = 0
    for line in cleaned.splitlines():
        stripped = line.strip()
        # 块开始
        if re.match(r'^\s*(if|foreach|while|function|macro)\s*\(', line):
            depth += 1
            continue
        # 块结束
        if re.match(r'^\s*(endif|endforeach|endwhile|endfunction|endmacro)\s*\(', line):
            if depth > 0:
                depth -= 1
            continue
        if depth > 0:
            continue  # 条件块或函数体内，不参与静态顺序分析
        # 顶层 include()
        m = _RE_INCLUDE_CALL.match(line)
        if m:
            inc_name = m.group(1).strip()
            resolved = _resolve_include_file(inc_name, cmake_dir)
            if resolved is not None:
                resolved_s = str(resolved.resolve())
                if resolved_s not in seen:
                    seen.add(resolved_s)
                    ordered_files.append(resolved)
    return ordered_files


def _check_include_order(cmake_dir: Path) -> list[dict]:
    """检查 CMakeLists.txt 中 include 顺序是否满足 function/macro 先定义后使用。

    算法：
    1. 解析 CMakeLists.txt 的顶层 include 顺序
    2. 预先扫描每个 .cmake 文件，提取其定义的 function/macro 集合和调用的自定义命令集合
    3. 按 include 顺序模拟加载：维护"已定义命令"集合；include 每个模块前，检查该模块
       顶层调用的自定义命令是否都已定义；include 后将该模块定义的命令加入集合
    4. 对于未在 cmake/ 目录内定义的命令（可能来自外部 find_package 或 vendor），
       标记为"外部依赖"而非错误（用户可用 --debug 查看）

    返回错误列表（每个错误是 dict，包含 file/rel_path/reason/used_command/defined_in 字段）。
    """
    errors: list[dict] = []
    root_cmakelists = cmake_dir.parent / "CMakeLists.txt"
    ordered_includes = _parse_include_order(root_cmakelists, cmake_dir)
    if not ordered_includes:
        _debug("include-order", "未找到有效的顶层 include 顺序")
        return errors

    _debug("include-order", f"include 顺序: {[f.name for f in ordered_includes]}")

    # 预扫描：收集每个 .cmake 文件的定义和调用
    module_defs: dict[str, set[str]] = {}   # filepath -> set of defined command names
    module_calls: dict[str, set[str]] = {}  # filepath -> set of called custom commands
    all_defined: set[str] = set()

    for cmake_file in cmake_dir.rglob("*.cmake"):
        try:
            content = cmake_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        defs = _extract_top_level_definitions(content)
        cmds = _extract_top_level_commands(content)
        key = str(cmake_file.resolve())
        module_defs[key] = defs
        # 过滤掉内置命令，只保留可能是自定义的命令
        custom_calls = {c for c in cmds if c not in CMAKE_BUILTIN_COMMANDS}
        module_calls[key] = custom_calls
        all_defined.update(defs)
        _debug("include-order", f"  {cmake_file.name}: defines={sorted(defs)}, calls={sorted(custom_calls)}")

    # 按 include 顺序模拟加载
    available: set[str] = set()  # 已加载模块定义的命令
    for inc_file in ordered_includes:
        key = str(inc_file.resolve())
        rel_name = inc_file.name
        calls = module_calls.get(key, set())
        # 检查：每个调用的自定义命令是否已经 available（之前 include 的模块定义的）
        # 注意：同文件内定义的函数可以在定义前调用（CMake 先解析后执行），所以排除本文件内的 defs
        self_defs = module_defs.get(key, set())
        for cmd in sorted(calls):
            if cmd in available or cmd in self_defs:
                continue
            if cmd in all_defined:
                # 该命令定义在后面的模块里 → 顺序错误
                # 找到定义它的模块
                defined_in = ""
                for fp, defs in module_defs.items():
                    if cmd in defs:
                        defined_in = Path(fp).name
                        break
                errors.append({
                    "file": str(inc_file),
                    "rel_path": rel_name,
                    "reason": f"前向引用错误: {rel_name} 调用了自定义命令 '{cmd}'，"
                              f"但该命令定义在 '{defined_in}' 中，且 '{defined_in}' 在 include 顺序中位于 {rel_name} 之后。"
                              f"请调整 include 顺序，确保定义 '{cmd}' 的模块在调用它的模块之前被 include",
                    "used_command": cmd,
                    "defined_in": defined_in,
                    "error_type": "forward_reference",
                })
            else:
                # 不在本项目任何 cmake/ 模块中定义 → 可能是外部依赖（find_package 提供的目标等）
                _debug("include-order", f"  {rel_name} 调用 '{cmd}': 未在本项目 cmake/ 中定义（可能是外部依赖，跳过）")
        # 加载本模块：将其定义加入 available
        available.update(self_defs)

    return errors


def run(project_root: Path, args) -> int:
    """CMake 静态检查主入口（命名冲突 + Include 顺序依赖）。

    返回退出码：0=通过，1=有错误。
    """
    debug = getattr(args, "debug", False)
    use_json = getattr(args, "json", False)
    skip_include_order = getattr(args, "skip_include_order", False)
    _set_debug(debug)

    _t_total_start = time.perf_counter()

    errors = 0
    warnings = 0
    passes = 0
    results: dict = {
        "tool": "cmake-naming-check",
        "version": "1.1.0",
        "project_root": str(project_root),
        "checks": [],
        "summary": {},
    }

    def _record(name: str, status: str, message: str, details: list | None = None) -> None:
        entry = {"name": name, "status": status, "message": message}
        if details:
            entry["details"] = details
        results["checks"].append(entry)

    cmake_dirs = _find_cmake_dirs(project_root)

    if not cmake_dirs:
        if use_json:
            _record("cmake_dirs", "pass", "未发现 cmake/ 目录（项目可能不使用自定义 CMake 模块）")
            results["summary"] = {"pass": 1, "warn": 0, "error": 0}
            results["passed"] = True
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print_header("CMake 自定义模块命名检查")
            print()
            print_pass("未发现 cmake/ 目录（项目可能不使用自定义 CMake 模块）")
            print()
            print_summary(1, 0, 0)
        return 0

    if not use_json:
        print_header("CMake 静态检查")
        print()
        print(f"  扫描目录: {', '.join(str(d) for d in cmake_dirs)}")
        checks_desc = ["命名冲突"]
        if not skip_include_order:
            checks_desc.append("Include顺序依赖")
        print(f"  检查项: {', '.join(checks_desc)}")
        print()

    all_errors: list[dict] = []
    all_passes: list[dict] = []

    for cmake_dir in cmake_dirs:
        _debug("run", f"扫描目录: {cmake_dir}")
        dir_errors, dir_passes = _scan_cmake_modules(cmake_dir)
        all_errors.extend(dir_errors)
        all_passes.extend(dir_passes)

    if all_errors:
        for err in all_errors:
            msg = f"[命名] {err['rel_path']}: {err['reason']}"
            if use_json:
                _record("naming", "error", msg)
            else:
                print_error(msg)
                # 给出修复建议
                filename = err["filename"]
                if filename.startswith("Find"):
                    pkg = filename[4:-6]  # FindXXX.cmake -> XXX
                    print(f"    建议: 重命名为 Detect{pkg}.cmake，并更新 CMakeLists.txt 中的 include 引用")
            errors += 1
    else:
        msg = f"所有 {len(all_passes)} 个 CMake 自定义模块命名合规"
        if use_json:
            _record("naming", "pass", msg)
        else:
            print_pass(f"[命名] {msg}")
        passes += 1

    # ── Include 顺序依赖检查 ──
    include_order_errors: list[dict] = []
    include_order_passes = 0
    if not skip_include_order and cmake_dirs:
        if not use_json:
            print()  # 分隔
        for cmake_dir in cmake_dirs:
            io_errors = _check_include_order(cmake_dir)
            include_order_errors.extend(io_errors)
        if include_order_errors:
            for err in include_order_errors:
                msg = f"[顺序] {err['rel_path']}: {err['reason']}"
                if use_json:
                    _record("include_order", "error", msg, details={
                        "used_command": err.get("used_command"),
                        "defined_in": err.get("defined_in"),
                    })
                else:
                    print_error(msg)
                    print(f"    建议: 将 include({err['defined_in'][:-6]}) 移动到 include({err['rel_path'][:-6]}) 之前")
                errors += 1
        else:
            msg = "Include 顺序正确，无 function/macro 前向引用"
            if use_json:
                _record("include_order", "pass", msg)
            else:
                print_pass(f"[顺序] {msg}")
            passes += 1
    elif skip_include_order:
        if not use_json:
            print_warn("[顺序] Include 顺序检查已跳过（--skip-include-order）")
        else:
            _record("include_order", "skip", "Include 顺序检查已跳过")

    total_ms = (time.perf_counter() - _t_total_start) * 1000

    if use_json:
        results["summary"] = {"pass": passes, "warn": warnings, "error": errors}
        results["total_files_scanned"] = len(all_passes) + len(all_errors)
        results["passed"] = errors == 0
        results["total_duration_ms"] = round(total_ms, 1)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print()
        print_summary(passes, warnings, errors)
        print()
        print(f"  总耗时: {total_ms:.1f}ms")
        print()

        if errors > 0:
            print_error("检查未通过，请修复上述问题")
            return 1
        print_pass("CMake 静态检查通过！")

    return 0 if errors == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    """构建 CLI 参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="cmake-naming-check",
        description="CMake 静态检查工具：命名冲突检查 + Include 顺序依赖检查，防止 Find<Name>.cmake 命名冲突和 function/macro 前向引用错误",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
检查项说明：
  1. 命名冲突检查：防止自定义模块使用 Find<Name>.cmake 等保留前缀
  2. Include 顺序依赖检查：检测 function/macro 调用在 include 顺序中先于定义的前向引用错误

命名规范说明：
  自定义检测模块  → Detect<Name>.cmake  (如 DetectBLAS.cmake)
  配置模块        → Config<Name>.cmake  (如 ConfigCompiler.cmake)
  工具函数模块    → <Function>.cmake    (如 ProtoCompile.cmake)
  禁止使用        → Find<Name>.cmake    (CMake 内置 find_package 保留命名)

Include 顺序规则（四层架构）：
  Options → Dependencies → CompilerConfig → ProtoCompile → TargetBuild → Tests → Install
  function/macro 定义模块必须在调用它的模块之前被 include

示例:
  python check-cmake-naming.py                        # 检查当前项目（所有检查项）
  python check-cmake-naming.py --path ./build         # 指定项目路径
  python check-cmake-naming.py --json                 # JSON 输出（CI 集成）
  python check-cmake-naming.py --skip-include-order   # 仅做命名检查
  python -m lib.checks.cmake_naming                   # 模块方式调用
        """,
    )
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="指定项目根目录路径（默认自动发现项目根）",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="输出详细调试日志到 stderr",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="以 JSON 格式输出检查结果（用于 CI 集成）",
    )
    parser.add_argument(
        "--skip-include-order",
        action="store_true",
        default=False,
        help="跳过 Include 顺序依赖检查（仅做命名冲突检查）",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="cmake-naming-check 1.1.0",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """独立 CLI 入口。"""
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

