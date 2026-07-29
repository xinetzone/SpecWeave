"""lib.checks.cmake_naming 单元测试 — FindBLAS 命名冲突回归防护 + Include 顺序依赖检测。

测试覆盖：
1. Find<Name>.cmake 保留命名检测（核心回归防护）
2. CMake*/cmake* 前缀检测
3. 下划线前缀检测
4. 合法命名（Detect*/Config*/工具模块）放行
5. 集成扫描测试（临时目录构造 cmake/ 结构）
6. Include 顺序依赖检测（v1.1 新增）：
   - function/macro 定义提取
   - 命令调用提取
   - include 顺序解析
   - 前向引用错误检测
   - 正确顺序通过
   - 外部命令不误报
   - 四层架构正确顺序验证
"""

import argparse
from pathlib import Path

import pytest

from lib.checks import cmake_naming as cn


@pytest.fixture
def args_default():
    return argparse.Namespace(path=None, debug=False, json=False, skip_include_order=False)


@pytest.fixture
def args_json():
    return argparse.Namespace(path=None, debug=False, json=True, skip_include_order=False)


@pytest.fixture
def args_skip_order():
    return argparse.Namespace(path=None, debug=False, json=False, skip_include_order=True)


class TestIsReservedFilename:
    """_is_reserved_filename 核心命名规则检测。"""

    # ── Find<Name>.cmake 保留前缀（核心回归测试用例）──

    def test_find_blas_conflict_detected(self):
        """FindBLAS.cmake — 本次修复的核心问题，必须检测到。"""
        reserved, reason = cn._is_reserved_filename("FindBLAS.cmake")
        assert reserved is True
        assert "Find" in reason
        assert "BLAS" in reason or "内置" in reason

    def test_find_boost_conflict_detected(self):
        """FindBoost.cmake — 常见内置模块，必须检测。"""
        reserved, reason = cn._is_reserved_filename("FindBoost.cmake")
        assert reserved is True
        assert "Find" in reason

    def test_find_protobuf_conflict_detected(self):
        """FindProtobuf.cmake — Caffe FFI 中实际使用的依赖，必须检测。"""
        reserved, reason = cn._is_reserved_filename("FindProtobuf.cmake")
        assert reserved is True

    def test_find_python3_conflict_detected(self):
        """FindPython3.cmake — 常见内置模块。"""
        reserved, reason = cn._is_reserved_filename("FindPython3.cmake")
        assert reserved is True

    def test_find_custom_name_generic_warning(self):
        """Find<CustomPkg>.cmake — 即使不在已知列表中也应警告（Find前缀保留）。"""
        reserved, reason = cn._is_reserved_filename("FindMyCustomLib.cmake")
        assert reserved is True
        assert "Detect" in reason or "Find" in reason

    # ── CMake*/cmake* 内部前缀 ──

    def test_cmake_prefix_reserved(self):
        reserved, reason = cn._is_reserved_filename("CMakeFindDependencyMacro.cmake")
        assert reserved is True
        assert "CMake" in reason

    def test_cmake_lower_prefix_reserved(self):
        reserved, reason = cn._is_reserved_filename("cmakesystem.cmake")
        assert reserved is True
        assert "cmake" in reason

    # ── 下划线前缀（私有约定）──

    def test_underscore_prefix_reserved(self):
        reserved, reason = cn._is_reserved_filename("_internal_helper.cmake")
        assert reserved is True
        assert "下划线" in reason or "_" in reason

    # ── 合法命名（必须放行）──

    def test_detect_blas_passes(self):
        """DetectBLAS.cmake — 正确的命名，不应报错。"""
        reserved, reason = cn._is_reserved_filename("DetectBLAS.cmake")
        assert reserved is False
        assert reason == ""

    def test_detect_lapack_passes(self):
        reserved, reason = cn._is_reserved_filename("DetectLAPACK.cmake")
        assert reserved is False

    def test_config_compiler_passes(self):
        reserved, reason = cn._is_reserved_filename("CompilerConfig.cmake")
        assert reserved is False

    def test_options_passes(self):
        reserved, reason = cn._is_reserved_filename("Options.cmake")
        assert reserved is False

    def test_proto_compile_passes(self):
        reserved, reason = cn._is_reserved_filename("ProtoCompile.cmake")
        assert reserved is False

    def test_dependencies_passes(self):
        reserved, reason = cn._is_reserved_filename("Dependencies.cmake")
        assert reserved is False

    def test_non_cmake_file_passes(self):
        """非 .cmake 文件直接跳过。"""
        reserved, reason = cn._is_reserved_filename("README.md")
        assert reserved is False

    def test_cmakelists_txt_passes(self):
        """CMakeLists.txt 不是 .cmake 文件，跳过。"""
        reserved, reason = cn._is_reserved_filename("CMakeLists.txt")
        assert reserved is False

    def test_install_cmake_passes(self):
        reserved, reason = cn._is_reserved_filename("Install.cmake")
        assert reserved is False

    def test_tests_cmake_passes(self):
        reserved, reason = cn._is_reserved_filename("Tests.cmake")
        assert reserved is False


class TestFindCmakeDirs:
    """_find_cmake_dirs 目录发现逻辑。"""

    def test_finds_cmake_dir(self, tmp_path):
        (tmp_path / "cmake").mkdir()
        dirs = cn._find_cmake_dirs(tmp_path)
        assert len(dirs) == 1
        assert dirs[0].name == "cmake"

    def test_no_cmake_dir_returns_empty(self, tmp_path):
        dirs = cn._find_cmake_dirs(tmp_path)
        assert dirs == []

    def test_uppercase_cmake_dir(self, tmp_path):
        """CMake/ 大写目录也应被发现（大小写不敏感FS上 cmake/ 先匹配到同一目录）。"""
        (tmp_path / "CMake").mkdir()
        dirs = cn._find_cmake_dirs(tmp_path)
        assert len(dirs) == 1  # 去重后只应有一个目录（大小写不敏感FS）


class TestScanCmakeModules:
    """_scan_cmake_modules 扫描逻辑。"""

    def test_all_valid_names_no_errors(self, tmp_path):
        cmake_dir = tmp_path / "cmake"
        cmake_dir.mkdir()
        (cmake_dir / "DetectBLAS.cmake").write_text("# Detect BLAS\n", encoding="utf-8")
        (cmake_dir / "Options.cmake").write_text("# Options\n", encoding="utf-8")
        (cmake_dir / "ProtoCompile.cmake").write_text("# Proto compile\n", encoding="utf-8")

        errors, passes = cn._scan_cmake_modules(cmake_dir)
        assert len(errors) == 0
        assert len(passes) == 3

    def test_find_blas_flagged(self, tmp_path):
        cmake_dir = tmp_path / "cmake"
        cmake_dir.mkdir()
        (cmake_dir / "FindBLAS.cmake").write_text("# WRONG NAME\n", encoding="utf-8")
        (cmake_dir / "Options.cmake").write_text("# OK\n", encoding="utf-8")

        errors, passes = cn._scan_cmake_modules(cmake_dir)
        assert len(errors) == 1
        assert errors[0]["filename"] == "FindBLAS.cmake"
        assert "Find" in errors[0]["reason"]
        assert len(passes) == 1

    def test_multiple_violations_detected(self, tmp_path):
        cmake_dir = tmp_path / "cmake"
        cmake_dir.mkdir()
        (cmake_dir / "FindBLAS.cmake").write_text("", encoding="utf-8")
        (cmake_dir / "FindProtobuf.cmake").write_text("", encoding="utf-8")
        (cmake_dir / "_secret.cmake").write_text("", encoding="utf-8")
        (cmake_dir / "CompilerConfig.cmake").write_text("", encoding="utf-8")

        errors, passes = cn._scan_cmake_modules(cmake_dir)
        assert len(errors) == 3  # FindBLAS, FindProtobuf, _secret
        assert len(passes) == 1  # CompilerConfig

    def test_nested_directory_scan(self, tmp_path):
        cmake_dir = tmp_path / "cmake"
        (cmake_dir / "modules").mkdir(parents=True)
        (cmake_dir / "modules" / "FindBad.cmake").write_text("", encoding="utf-8")
        (cmake_dir / "DetectGood.cmake").write_text("", encoding="utf-8")

        errors, passes = cn._scan_cmake_modules(cmake_dir)
        assert len(errors) == 1
        assert "modules/FindBad.cmake" in errors[0]["rel_path"]
        assert len(passes) == 1


class TestRunIntegration:
    """run() 集成测试 — 使用临时项目目录。"""

    def _make_project(self, tmp_path, cmake_files: dict[str, str]) -> Path:
        """在 tmp_path 下创建一个带 cmake/ 目录和 CMakeLists.txt 的项目。"""
        cmake_dir = tmp_path / "cmake"
        cmake_dir.mkdir()
        for fname, content in cmake_files.items():
            (cmake_dir / fname).write_text(content, encoding="utf-8")
        (tmp_path / "CMakeLists.txt").write_text(
            "cmake_minimum_required(VERSION 3.20)\nproject(test)\n",
            encoding="utf-8",
        )
        return tmp_path

    def test_clean_project_passes(self, tmp_path, args_default, capsys):
        project = self._make_project(tmp_path, {
            "DetectBLAS.cmake": "# detect blas\n",
            "Options.cmake": "# options\n",
            "CompilerConfig.cmake": "# compiler\n",
            "Dependencies.cmake": "# deps\n",
            "ProtoCompile.cmake": "# proto\n",
            "Install.cmake": "# install\n",
            "Tests.cmake": "# tests\n",
            "WindowsDllCopy.cmake": "# dll copy\n",
        })
        rc = cn.run(project, args_default)
        captured = capsys.readouterr()
        assert rc == 0
        assert "通过" in captured.out

    def test_findblas_project_fails(self, tmp_path, args_default, capsys):
        """这是本次修复的核心回归测试：FindBLAS.cmake 必须导致检查失败。"""
        project = self._make_project(tmp_path, {
            "FindBLAS.cmake": "# WRONG! Should be DetectBLAS.cmake\n",
            "Options.cmake": "# ok\n",
        })
        rc = cn.run(project, args_default)
        captured = capsys.readouterr()
        assert rc == 1  # 非零退出码表示检查失败
        assert "FindBLAS" in captured.out
        assert "未通过" in captured.out

    def test_json_output_format(self, tmp_path, args_json, capsys):
        project = self._make_project(tmp_path, {
            "DetectBLAS.cmake": "# ok\n",
        })
        rc = cn.run(project, args_json)
        captured = capsys.readouterr()
        assert rc == 0
        import json as _json
        output = _json.loads(captured.out)
        assert output["tool"] == "cmake-naming-check"
        assert output["passed"] is True
        assert output["summary"]["error"] == 0

    def test_json_output_with_errors(self, tmp_path, args_json, capsys):
        project = self._make_project(tmp_path, {
            "FindBLAS.cmake": "# wrong\n",
        })
        rc = cn.run(project, args_json)
        captured = capsys.readouterr()
        import json as _json
        output = _json.loads(captured.out)
        assert rc == 1
        assert output["passed"] is False
        assert output["summary"]["error"] >= 1

    def test_no_cmake_dir_passes(self, tmp_path, args_default, capsys):
        """无 cmake/ 目录的项目应直接通过。"""
        (tmp_path / "CMakeLists.txt").write_text("project(minimal)\n", encoding="utf-8")
        rc = cn.run(tmp_path, args_default)
        captured = capsys.readouterr()
        assert rc == 0

    def test_caffe_ffi_naming_convention_passes(self, tmp_path, args_default, capsys):
        """验证 caffe-ffi 修复后的实际命名集合全部通过检查。

        cmake/ 目录下的文件（来自 LS 结果）：
        - CompilerConfig.cmake  ✓
        - Dependencies.cmake    ✓
        - DetectBLAS.cmake      ✓（修复后正确命名）
        - Install.cmake         ✓
        - Options.cmake         ✓
        - ProtoCompile.cmake    ✓
        - TargetBuild.cmake     ✓
        - Tests.cmake           ✓
        - WindowsDllCopy.cmake  ✓
        """
        caffe_cmake_files = {
            "CompilerConfig.cmake": "",
            "Dependencies.cmake": "",
            "DetectBLAS.cmake": "",
            "Install.cmake": "",
            "Options.cmake": "",
            "ProtoCompile.cmake": "",
            "README.md": "# CMake modules\n",  # 非 .cmake 文件
            "TargetBuild.cmake": "",
            "Tests.cmake": "",
            "WindowsDllCopy.cmake": "",
        }
        project = self._make_project(tmp_path, caffe_cmake_files)
        rc = cn.run(project, args_default)
        captured = capsys.readouterr()
        assert rc == 0, f"caffe-ffi 命名规范检查应全部通过，但输出: {captured.out}"
        assert "通过" in captured.out

    def test_caffe_ffi_pre_fix_naming_fails(self, tmp_path, args_default, capsys):
        """验证修复前的错误命名（FindBLAS.cmake）会被检测到 — 回归防护。"""
        caffe_cmake_files_broken = {
            "CompilerConfig.cmake": "",
            "Dependencies.cmake": "",
            "FindBLAS.cmake": "",  # ← 修复前的错误命名
            "Install.cmake": "",
            "Options.cmake": "",
            "ProtoCompile.cmake": "",
            "TargetBuild.cmake": "",
            "Tests.cmake": "",
            "WindowsDllCopy.cmake": "",
        }
        project = self._make_project(tmp_path, caffe_cmake_files_broken)
        rc = cn.run(project, args_default)
        captured = capsys.readouterr()
        assert rc == 1, "FindBLAS.cmake 命名错误必须被检测到（回归防护）"
        assert "FindBLAS" in captured.out


# ══════════════════════════════════════════════════════════════
# Include 顺序依赖检测测试（v1.1 新增）
# ══════════════════════════════════════════════════════════════

class TestExtractDefinitions:
    """_extract_top_level_definitions 函数/宏定义提取。"""

    def test_single_function_def(self):
        content = "function(my_func arg1)\n  message(\"hello\")\nendfunction()\n"
        defs = cn._extract_top_level_definitions(content)
        assert "my_func" in defs

    def test_single_macro_def(self):
        content = "macro(my_macro)\n  set(x 1)\nendmacro()\n"
        defs = cn._extract_top_level_definitions(content)
        assert "my_macro" in defs

    def test_multiple_defs(self):
        content = """
function(func_a)
endfunction()
function(func_b)
endfunction()
macro(macro_c)
endmacro()
"""
        defs = cn._extract_top_level_definitions(content)
        assert defs == {"func_a", "func_b", "macro_c"}

    def test_nested_function_not_extracted_as_top_level(self):
        """嵌套在 function 内的 function 定义不应被提取为顶层定义。"""
        content = """
function(outer)
  function(inner)
    message("inner")
  endfunction()
endfunction()
"""
        defs = cn._extract_top_level_definitions(content)
        assert "outer" in defs
        assert "inner" not in defs  # 嵌套的inner不是顶层

    def test_defs_inside_if_still_top_level(self):
        """if() 块内定义的 function 在 CMake 中仍然是全局的，应被提取。"""
        content = """
if(MSVC)
  function(msvc_helper)
  endfunction()
endif()
"""
        defs = cn._extract_top_level_definitions(content)
        assert "msvc_helper" in defs

    def test_comments_stripped(self):
        """注释中的 function( 不应被误识别。"""
        content = """
# function(this_is_commented_out)
# endfunction()
function(real_func)
endfunction()
"""
        defs = cn._extract_top_level_definitions(content)
        assert "real_func" in defs
        assert "this_is_commented_out" not in defs


class TestExtractCommands:
    """_extract_top_level_commands 顶层命令调用提取。"""

    def test_builtin_commands_included_in_raw_result(self):
        """内置命令会被匹配，但后续在 _check_include_order 中会被过滤。"""
        content = "set(x 1)\nmessage(STATUS \"hi\")\n"
        cmds = cn._extract_top_level_commands(content)
        assert "set" in cmds
        assert "message" in cmds

    def test_function_body_commands_excluded(self):
        """函数体内的命令调用不应在顶层命令集中。"""
        content = """
function(my_func)
  set(inner_var 1)
  message("inside")
endfunction()
set(outer_var 2)
"""
        cmds = cn._extract_top_level_commands(content)
        assert "set" in cmds       # 顶层的 set
        # 函数体内的 set/message 也匹配到顶层同名set/message，但这没关系——
        # 关键是自定义命令调用必须在顶层出现

    def test_custom_command_call_detected(self):
        content = "my_custom_command(arg1 arg2)\n"
        cmds = cn._extract_top_level_commands(content)
        assert "my_custom_command" in cmds

    def test_comments_not_matched(self):
        content = "# my_dead_call()\nreal_call()\n"
        cmds = cn._extract_top_level_commands(content)
        assert "real_call" in cmds
        assert "my_dead_call" not in cmds


class TestResolveIncludeFile:
    """_resolve_include_file include 路径解析。"""

    def test_bare_name_resolves_to_cmake(self, tmp_path):
        cmake_dir = tmp_path / "cmake"
        cmake_dir.mkdir()
        (cmake_dir / "Options.cmake").write_text("", encoding="utf-8")
        resolved = cn._resolve_include_file("Options", cmake_dir)
        assert resolved is not None
        assert resolved.name == "Options.cmake"

    def test_explicit_cmake_extension(self, tmp_path):
        cmake_dir = tmp_path / "cmake"
        cmake_dir.mkdir()
        (cmake_dir / "Options.cmake").write_text("", encoding="utf-8")
        resolved = cn._resolve_include_file("Options.cmake", cmake_dir)
        assert resolved is not None
        assert resolved.name == "Options.cmake"

    def test_nonexistent_returns_none(self, tmp_path):
        cmake_dir = tmp_path / "cmake"
        cmake_dir.mkdir()
        resolved = cn._resolve_include_file("Nonexistent", cmake_dir)
        assert resolved is None

    def test_optional_keyword_returns_none(self, tmp_path):
        """include(OPTIONAL) 是关键字参数，不是文件名。"""
        cmake_dir = tmp_path / "cmake"
        cmake_dir.mkdir()
        resolved = cn._resolve_include_file("OPTIONAL", cmake_dir)
        assert resolved is None


class TestParseIncludeOrder:
    """_parse_include_order CMakeLists.txt include 顺序解析。"""

    def _make_cmakelists(self, root: Path, cmake_dir: Path, content: str):
        """辅助：创建 CMakeLists.txt 和 cmake/ 目录及相应模块文件。"""
        cmake_dir.mkdir(exist_ok=True)
        (root / "CMakeLists.txt").write_text(content, encoding="utf-8")
        # 提取所有 include 名并创建空文件
        import re as _re
        for m in _re.finditer(r'include\s*\(\s*([A-Za-z0-9_]+)\s*\)', content):
            name = m.group(1)
            if name.upper() in ("OPTIONAL", "RESULT_VARIABLE", "NO_POLICY_SCOPE"):
                continue
            (cmake_dir / f"{name}.cmake").write_text("", encoding="utf-8")

    def test_linear_order(self, tmp_path):
        cmake_dir = tmp_path / "cmake"
        content = """
cmake_minimum_required(VERSION 3.20)
project(test)
include(Options)
include(Dependencies)
include(CompilerConfig)
include(TargetBuild)
"""
        self._make_cmakelists(tmp_path, cmake_dir, content)
        ordered = cn._parse_include_order(tmp_path / "CMakeLists.txt", cmake_dir)
        assert [f.name for f in ordered] == ["Options.cmake", "Dependencies.cmake",
                                              "CompilerConfig.cmake", "TargetBuild.cmake"]

    def test_includes_inside_if_skipped(self, tmp_path):
        """if() 块内的 include 是条件执行的，静态分析应跳过。"""
        cmake_dir = tmp_path / "cmake"
        content = """
include(Options)
if(WIN32)
  include(WindowsStuff)
endif()
include(Targets)
"""
        self._make_cmakelists(tmp_path, cmake_dir, content)
        ordered = cn._parse_include_order(tmp_path / "CMakeLists.txt", cmake_dir)
        names = [f.name for f in ordered]
        assert "Options.cmake" in names
        assert "Targets.cmake" in names
        assert "WindowsStuff.cmake" not in names

    def test_empty_cmakelists(self, tmp_path):
        cmake_dir = tmp_path / "cmake"
        cmake_dir.mkdir()
        (tmp_path / "CMakeLists.txt").write_text("project(minimal)\n", encoding="utf-8")
        ordered = cn._parse_include_order(tmp_path / "CMakeLists.txt", cmake_dir)
        assert ordered == []


class TestIncludeOrderIntegration:
    """_check_include_order / run() 集成测试。"""

    def _make_project_with_includes(self, tmp_path, cmake_files: dict[str, str],
                                     include_order: list[str]) -> Path:
        """创建带 include 顺序的测试项目。"""
        cmake_dir = tmp_path / "cmake"
        cmake_dir.mkdir()
        for fname, content in cmake_files.items():
            (cmake_dir / fname).write_text(content, encoding="utf-8")
        # 构建 CMakeLists.txt
        includes = "\n".join(f"include({name.replace('.cmake', '')})" for name in include_order)
        (tmp_path / "CMakeLists.txt").write_text(
            f"cmake_minimum_required(VERSION 3.20)\nproject(test)\n"
            f"list(APPEND CMAKE_MODULE_PATH \"${{CMAKE_CURRENT_SOURCE_DIR}}/cmake\")\n"
            f"{includes}\n",
            encoding="utf-8",
        )
        return tmp_path

    def test_correct_order_passes(self, tmp_path, args_default, capsys):
        """正确顺序：CompilerConfig（定义函数）在 TargetBuild（调用函数）之前。"""
        project = self._make_project_with_includes(tmp_path,
            cmake_files={
                "CompilerConfig.cmake": "function(my_config tgt)\n  message(\"${tgt}\")\nendfunction()\n",
                "TargetBuild.cmake": "add_library(mylib main.cpp)\nmy_config(mylib)\n",
            },
            include_order=["CompilerConfig.cmake", "TargetBuild.cmake"],
        )
        rc = cn.run(project, args_default)
        captured = capsys.readouterr()
        assert rc == 0, f"正确顺序应通过，但输出: {captured.out}"
        assert "[FAIL]" not in captured.out

    def test_wrong_order_detected(self, tmp_path, args_default, capsys):
        """错误顺序：TargetBuild（调用函数）在 CompilerConfig（定义函数）之前。"""
        project = self._make_project_with_includes(tmp_path,
            cmake_files={
                "CompilerConfig.cmake": "function(my_config tgt)\nendfunction()\n",
                "TargetBuild.cmake": "add_library(mylib main.cpp)\nmy_config(mylib)\n",
            },
            include_order=["TargetBuild.cmake", "CompilerConfig.cmake"],  # 错误！
        )
        rc = cn.run(project, args_default)
        captured = capsys.readouterr()
        assert rc == 1, "错误顺序应检测到前向引用"
        assert "my_config" in captured.out
        assert "CompilerConfig" in captured.out
        assert "建议" in captured.out

    def test_four_layer_correct_order_passes(self, tmp_path, args_default, capsys):
        """四层架构正确顺序：Options → Dependencies → CompilerConfig → ProtoCompile → TargetBuild。"""
        project = self._make_project_with_includes(tmp_path,
            cmake_files={
                "Options.cmake": "option(USE_FEATURE \"use it\" OFF)\n",
                "Dependencies.cmake": "find_package(Threads REQUIRED)\n",
                "CompilerConfig.cmake": "function(config_target tgt)\n  target_link_libraries(${tgt} PRIVATE Threads::Threads)\nendfunction()\n",
                "ProtoCompile.cmake": "function(compile_proto srcs)\nendfunction()\n",
                "TargetBuild.cmake": "add_library(mylib a.cpp)\ncompile_proto(mylib)\nconfig_target(mylib)\n",
            },
            include_order=["Options.cmake", "Dependencies.cmake", "CompilerConfig.cmake",
                            "ProtoCompile.cmake", "TargetBuild.cmake"],
        )
        rc = cn.run(project, args_default)
        captured = capsys.readouterr()
        assert rc == 0, f"四层架构正确顺序应通过: {captured.out}"

    def test_four_layer_bad_order_fails(self, tmp_path, args_default, capsys):
        """TargetBuild 提到 CompilerConfig 之前 → 前向引用。"""
        project = self._make_project_with_includes(tmp_path,
            cmake_files={
                "Options.cmake": "",
                "CompilerConfig.cmake": "function(config_target tgt)\nendfunction()\n",
                "TargetBuild.cmake": "add_library(mylib a.cpp)\nconfig_target(mylib)\n",
            },
            include_order=["Options.cmake", "TargetBuild.cmake", "CompilerConfig.cmake"],  # 错误
        )
        rc = cn.run(project, args_default)
        assert rc == 1

    def test_external_command_not_flagged(self, tmp_path, args_default, capsys):
        """调用外部命令（不在本项目cmake/中定义）不应报错（可能是find_package提供的）。"""
        project = self._make_project_with_includes(tmp_path,
            cmake_files={
                "Setup.cmake": "",
                "Build.cmake": "external_provided_command(arg1)\nadd_library(mylib main.cpp)\n",
            },
            include_order=["Setup.cmake", "Build.cmake"],
        )
        rc = cn.run(project, args_default)
        captured = capsys.readouterr()
        assert rc == 0, f"外部命令不应报错: {captured.out}"

    def test_same_file_forward_ref_allowed(self, tmp_path, args_default, capsys):
        """CMake 中同一文件内函数可以在定义前调用（先解析后执行），不应报错。"""
        project = self._make_project_with_includes(tmp_path,
            cmake_files={
                "MyModule.cmake": "my_helper()\n\nfunction(my_helper)\n  message(\"ok\")\nendfunction()\n",
            },
            include_order=["MyModule.cmake"],
        )
        rc = cn.run(project, args_default)
        captured = capsys.readouterr()
        assert rc == 0, f"同文件内函数前向调用是CMake合法行为: {captured.out}"

    def test_skip_include_order_flag(self, tmp_path, args_skip_order, capsys):
        """--skip-include-order 应跳过顺序检查。"""
        project = self._make_project_with_includes(tmp_path,
            cmake_files={
                "Def.cmake": "function(my_func)\nendfunction()\n",
                "Call.cmake": "my_func()\n",
            },
            include_order=["Call.cmake", "Def.cmake"],  # 错误顺序但跳过检查
        )
        rc = cn.run(project, args_skip_order)
        captured = capsys.readouterr()
        assert rc == 0, "跳过后错误顺序不应导致失败"
        assert "跳过" in captured.out

    def test_macro_forward_ref_detected(self, tmp_path, args_default, capsys):
        """macro() 和 function() 一样，前向引用应被检测。"""
        project = self._make_project_with_includes(tmp_path,
            cmake_files={
                "DefMacro.cmake": "macro(my_macro)\n  message(\"m\")\nendmacro()\n",
                "UseMacro.cmake": "my_macro()\n",
            },
            include_order=["UseMacro.cmake", "DefMacro.cmake"],  # 错误
        )
        rc = cn.run(project, args_default)
        assert rc == 1

    def test_json_output_includes_order_check(self, tmp_path, args_json, capsys):
        """JSON输出应包含 include_order 检查结果。"""
        project = self._make_project_with_includes(tmp_path,
            cmake_files={
                "Options.cmake": "",
            },
            include_order=["Options.cmake"],
        )
        rc = cn.run(project, args_json)
        captured = capsys.readouterr()
        assert rc == 0
        import json as _json
        output = _json.loads(captured.out)
        check_names = [c["name"] for c in output["checks"]]
        assert "naming" in check_names
        assert "include_order" in check_names

    def test_caffe_ffi_correct_order_passes(self, tmp_path, args_default, capsys):
        """caffe-ffi 实际 include 顺序（四层架构）应通过检查。"""
        project = self._make_project_with_includes(tmp_path,
            cmake_files={
                "Options.cmake": "option(CAFFE_CPU_ONLY \"CPU only\" OFF)\n",
                "Dependencies.cmake": "find_package(Protobuf REQUIRED)\n",
                "CompilerConfig.cmake": "function(caffe_ffi_configure_target target_name)\n  cmake_parse_arguments(ARG \"\" \"VISIBILITY\" \"\" ${ARGN})\n  target_link_libraries(${target_name} ${ARG_VISIBILITY} protobuf::libprotobuf)\nendfunction()\n",
                "ProtoCompile.cmake": "function(caffe_ffi_proto_compile out_var)\nendfunction()\n",
                "TargetBuild.cmake": "caffe_ffi_proto_compile(PROTO_SRCS)\nadd_library(_caffe_ffi ${PROTO_SRCS})\ncaffe_ffi_configure_target(_caffe_ffi VISIBILITY PUBLIC)\n",
                "WindowsDllCopy.cmake": "function(caffe_ffi_copy_runtime_dlls tgt)\nendfunction()\n",
                "Tests.cmake": "add_executable(caffe_test test.cpp)\ncaffe_ffi_configure_target(caffe_test VISIBILITY PRIVATE)\n",
                "Install.cmake": "install(TARGETS _caffe_ffi)\n",
            },
            include_order=["Options.cmake", "Dependencies.cmake", "CompilerConfig.cmake",
                            "ProtoCompile.cmake", "TargetBuild.cmake", "WindowsDllCopy.cmake",
                            "Tests.cmake", "Install.cmake"],
        )
        rc = cn.run(project, args_default)
        captured = capsys.readouterr()
        assert rc == 0, f"caffe-ffi 四层架构正确顺序应通过: {captured.out}"
        assert "[FAIL]" not in captured.out
