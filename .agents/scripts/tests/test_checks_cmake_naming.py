"""lib.checks.cmake_naming 单元测试 — FindBLAS 命名冲突回归防护。

测试覆盖：
1. Find<Name>.cmake 保留命名检测（核心回归防护）
2. CMake*/cmake* 前缀检测
3. 下划线前缀检测
4. 合法命名（Detect*/Config*/工具模块）放行
5. 集成扫描测试（临时目录构造 cmake/ 结构）
"""

import argparse
from pathlib import Path

import pytest

from lib.checks import cmake_naming as cn


@pytest.fixture
def args_default():
    return argparse.Namespace(path=None, debug=False, json=False)


@pytest.fixture
def args_json():
    return argparse.Namespace(path=None, debug=False, json=True)


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
