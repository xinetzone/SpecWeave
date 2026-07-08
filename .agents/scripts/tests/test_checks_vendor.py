"""lib.checks.vendor 单元测试。"""

import argparse
import sys
from pathlib import Path

import pytest

from lib.checks import vendor as vd


@pytest.fixture
def args_default():
    return argparse.Namespace(fix=False, scan_refs=False, path=None, deep=False, debug=False, json=False)


@pytest.fixture
def args_fix():
    return argparse.Namespace(fix=True, scan_refs=False, path=None, deep=False, debug=False, json=False)


@pytest.fixture
def args_scan():
    return argparse.Namespace(fix=False, scan_refs=True, path=None, deep=False, debug=False, json=False)


@pytest.fixture
def args_deep():
    return argparse.Namespace(fix=False, scan_refs=False, path=None, deep=True, debug=False, json=False)


class TestCheckGitignoreRule:
    """_check_gitignore_rule 测试。

    新策略（2026-07-07）：vendor/ 不被根 .gitignore 整体忽略。
    - True  = .gitignore 配置正确（无 vendor/ 整体忽略规则）
    - False = 配置有问题（.gitignore 不存在，或包含 vendor/ 整体忽略）
    """

    def test_missing_gitignore(self, tmp_path):
        assert vd._check_gitignore_rule(tmp_path) is False

    def test_gitignore_without_vendor_rule_passes(self, tmp_path):
        """无 vendor 规则 = vendor 开放 = 正确配置。"""
        (tmp_path / ".gitignore").write_text("*.pyc\nnode_modules/\n.temp/\n", encoding="utf-8")
        assert vd._check_gitignore_rule(tmp_path) is True

    def test_gitignore_with_vendor_blanket_fails(self, tmp_path):
        """包含 vendor/ 整体忽略 = 阻塞子模块操作 = 错误配置。"""
        (tmp_path / ".gitignore").write_text("vendor/\n*.pyc\n", encoding="utf-8")
        assert vd._check_gitignore_rule(tmp_path) is False

    def test_gitignore_with_vendor_star_fails(self, tmp_path):
        """包含 vendor/* 也会阻塞新子模块添加 = 错误配置。"""
        (tmp_path / ".gitignore").write_text("vendor/*\n!vendor/flexloop/\n", encoding="utf-8")
        assert vd._check_gitignore_rule(tmp_path) is False

    def test_gitignore_with_vendor_backslash_fails(self, tmp_path):
        """Windows 反斜杠路径 vendor\\ 也应该被检测为错误配置。"""
        (tmp_path / ".gitignore").write_text("vendor\\\n*.pyc\n", encoding="utf-8")
        assert vd._check_gitignore_rule(tmp_path) is False

    def test_gitignore_with_vendor_backslash_star_fails(self, tmp_path):
        """Windows 反斜杠路径 vendor\\* 也应该被检测。"""
        (tmp_path / ".gitignore").write_text("vendor\\*\n*.pyc\n", encoding="utf-8")
        assert vd._check_gitignore_rule(tmp_path) is False

    def test_gitignore_with_vendor_no_slash_fails(self, tmp_path):
        """vendor（不带斜杠）也视为整体忽略。"""
        (tmp_path / ".gitignore").write_text("vendor\n*.pyc\n", encoding="utf-8")
        assert vd._check_gitignore_rule(tmp_path) is False

    def test_gitignore_with_comment_only_passes(self, tmp_path):
        """注释中提到 vendor 不算忽略规则。"""
        (tmp_path / ".gitignore").write_text(
            "# 第三方依赖（vendor/ 目录不忽略）\n*.pyc\n",
            encoding="utf-8",
        )
        assert vd._check_gitignore_rule(tmp_path) is True


class TestLoadSubmodulePaths:
    """_load_submodule_paths 测试。"""

    def test_no_gitmodules(self, tmp_path):
        assert vd._load_submodule_paths(tmp_path) == set()

    def test_parses_gitmodules(self, tmp_path):
        (tmp_path / ".gitmodules").write_text(
            '[submodule "vendor/flexloop"]\n'
            '    path = vendor/flexloop\n'
            '    url = git@example.com:flexloop.git\n',
            encoding="utf-8",
        )
        paths = vd._load_submodule_paths(tmp_path)
        assert paths == {"vendor/flexloop"}

    def test_multiple_submodules(self, tmp_path):
        (tmp_path / ".gitmodules").write_text(
            '[submodule "vendor/a"]\n'
            '    path = vendor/a\n'
            '    url = git@example.com:a.git\n'
            '[submodule "vendor/b"]\n'
            '    path = vendor/b\n'
            '    url = git@example.com:b.git\n',
            encoding="utf-8",
        )
        paths = vd._load_submodule_paths(tmp_path)
        assert paths == {"vendor/a", "vendor/b"}

    def test_discovers_unregistered_submodule_via_git_file(self, tmp_path):
        """通过 .git 文件发现未在 .gitmodules 登记的子模块。"""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        unreg = vendor_dir / "unregistered"
        unreg.mkdir()
        (unreg / ".git").write_text("gitdir: ../.git/modules/vendor/unregistered\n", encoding="utf-8")
        paths = vd._load_submodule_paths(tmp_path)
        assert "vendor/unregistered" in paths


class TestGetLibs:
    """_get_libs 测试。"""

    def test_nonexistent_dir(self, tmp_path):
        assert vd._get_libs(tmp_path / "vendor") == []

    def test_empty_dir(self, tmp_path):
        (tmp_path / "vendor").mkdir()
        assert vd._get_libs(tmp_path / "vendor") == []

    def test_sorted_libs(self, tmp_path):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (vendor_dir / "zlib").mkdir()
        (vendor_dir / "alpha").mkdir()
        (vendor_dir / "beta").mkdir()
        libs = vd._get_libs(vendor_dir)
        assert [p.name for p in libs] == ["alpha", "beta", "zlib"]

    def test_excludes_dot_dirs(self, tmp_path):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (vendor_dir / "mylib").mkdir()
        (vendor_dir / ".hidden").mkdir()
        (vendor_dir / ".cache").mkdir()
        libs = vd._get_libs(vendor_dir)
        assert [p.name for p in libs] == ["mylib"]

    def test_excludes_files(self, tmp_path):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (vendor_dir / "mylib").mkdir()
        (vendor_dir / "README.md").write_text("test", encoding="utf-8")
        libs = vd._get_libs(vendor_dir)
        assert [p.name for p in libs] == ["mylib"]

    def test_excludes_submodules_via_gitmodules(self, tmp_path):
        (tmp_path / ".gitmodules").write_text(
            '[submodule "vendor/flexloop"]\n'
            '    path = vendor/flexloop\n'
            '    url = git@example.com:flexloop.git\n',
            encoding="utf-8",
        )
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (vendor_dir / "flexloop").mkdir()
        (vendor_dir / "mylib").mkdir()
        libs = vd._get_libs(vendor_dir)
        assert [p.name for p in libs] == ["mylib"]

    def test_excludes_submodules_via_git_file(self, tmp_path):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        sub_mod = vendor_dir / "submod"
        sub_mod.mkdir()
        (sub_mod / ".git").write_text("gitdir: ../.git/modules/vendor/submod\n", encoding="utf-8")
        (vendor_dir / "mylib").mkdir()
        libs = vd._get_libs(vendor_dir)
        assert [p.name for p in libs] == ["mylib"]


class TestCheckLibReadme:
    """_check_lib_readme 测试。"""

    def test_missing_readme(self, tmp_path):
        lib_dir = tmp_path / "mylib"
        lib_dir.mkdir()
        ok, issues = vd._check_lib_readme(lib_dir)
        assert ok is False
        assert any("缺少 README.md" in i for i in issues)

    def test_readme_missing_fields(self, tmp_path):
        lib_dir = tmp_path / "mylib"
        lib_dir.mkdir()
        (lib_dir / "README.md").write_text("# MyLib\n\n这是一个库。\n", encoding="utf-8")
        ok, issues = vd._check_lib_readme(lib_dir)
        assert ok is False
        assert len(issues) == len(vd.REQUIRED_LIB_FIELDS)

    def test_readme_complete(self, tmp_path):
        lib_dir = tmp_path / "mylib"
        lib_dir.mkdir()
        content = """
- **名称**：mylib
- **版本**：1.0.0
- **来源**：https://example.com
- **引入日期**：2026-01-01
- **用途**：测试
- **许可证**：MIT
"""
        (lib_dir / "README.md").write_text(content, encoding="utf-8")
        ok, issues = vd._check_lib_readme(lib_dir)
        assert ok is True
        assert issues == []

    def test_readme_complete_no_colon(self, tmp_path):
        """字段格式为 **名称**（无冒号）也应该被识别。"""
        lib_dir = tmp_path / "mylib"
        lib_dir.mkdir()
        content = """
- **名称**mylib
- **版本**1.0.0
- **来源**https://example.com
- **引入日期**2026-01-01
- **用途**测试
- **许可证**MIT
"""
        (lib_dir / "README.md").write_text(content, encoding="utf-8")
        ok, issues = vd._check_lib_readme(lib_dir)
        assert ok is True
        assert issues == []

    def test_readme_partial_fields(self, tmp_path):
        lib_dir = tmp_path / "mylib"
        lib_dir.mkdir()
        content = "- **名称**：mylib\n- **版本**：1.0.0\n"
        (lib_dir / "README.md").write_text(content, encoding="utf-8")
        ok, issues = vd._check_lib_readme(lib_dir)
        assert ok is False
        assert len(issues) == 4


class TestShouldScanFile:
    """_should_scan_file 测试。"""

    def test_directory_not_scanned(self, tmp_path):
        (tmp_path / "subdir").mkdir()
        assert vd._should_scan_file(tmp_path / "subdir") is False

    def test_binary_extension_not_scanned(self, tmp_path):
        f = tmp_path / "data.bin"
        f.write_bytes(b"binary")
        assert vd._should_scan_file(f) is False

    def test_source_extensions_scanned(self, tmp_path):
        for ext in [".py", ".js", ".ts", ".md", ".yaml", ".json"]:
            f = tmp_path / f"test{ext}"
            f.write_text("test", encoding="utf-8")
            assert vd._should_scan_file(f) is True, f"{ext} should be scanned"

    def test_uppercase_extension_handled(self, tmp_path):
        f = tmp_path / "TEST.PY"
        f.write_text("test", encoding="utf-8")
        assert vd._should_scan_file(f) is True


class TestIsCommentLine:
    """_is_comment_line 测试。"""

    def test_empty_line_is_comment(self):
        assert vd._is_comment_line("", ".py") is True
        assert vd._is_comment_line("   ", ".py") is True

    def test_python_hash_comment(self):
        assert vd._is_comment_line("# this is a comment", ".py") is True
        assert vd._is_comment_line("  # indented comment", ".sh") is True
        assert vd._is_comment_line("code() # not comment", ".py") is False

    def test_js_double_slash_comment(self):
        assert vd._is_comment_line("// comment", ".js") is True
        assert vd._is_comment_line("  // indented", ".ts") is True

    def test_js_block_comment_start(self):
        assert vd._is_comment_line("/* block comment", ".js") is True

    def test_c_block_comment_continuation(self):
        assert vd._is_comment_line("* continued", ".c") is True

    def test_html_comment(self):
        assert vd._is_comment_line("<!-- comment -->", ".html") is True

    def test_markdown_no_comments(self):
        assert vd._is_comment_line("# This is a heading, not comment", ".md") is False
        assert vd._is_comment_line("<!-- html in md but not skipped -->", ".md") is False

    def test_yaml_hash_comment(self):
        assert vd._is_comment_line("# yaml comment", ".yaml") is True


class TestScanRefs:
    """_scan_refs 测试。"""

    def test_no_refs(self, tmp_path):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        src = tmp_path / "src"
        src.mkdir()
        (src / "main.py").write_text("print('hello')\n", encoding="utf-8")
        refs = vd._scan_refs(tmp_path, vendor_dir)
        assert refs == {}

    def test_finds_vendor_path_ref(self, tmp_path):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / "main.py").write_text(
            'import sys\nsys.path.insert(0, "vendor/mylib")\n',
            encoding="utf-8",
        )
        refs = vd._scan_refs(tmp_path, vendor_dir)
        assert "main.py" in refs
        assert any("vendor/mylib" in line for lines in refs.values() for line in lines)

    def test_finds_vendor_backslash_ref(self, tmp_path):
        """Windows 反斜杠路径也应该被检测。"""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / "main.py").write_text(
            'sys.path.insert(0, "vendor\\\\mylib")\n',
            encoding="utf-8",
        )
        refs = vd._scan_refs(tmp_path, vendor_dir)
        assert "main.py" in refs

    def test_skips_comment_lines(self, tmp_path):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / "main.py").write_text(
            "# vendor/oldlib is deprecated\nimport os\n",
            encoding="utf-8",
        )
        refs = vd._scan_refs(tmp_path, vendor_dir)
        assert refs == {}

    def test_skips_js_comments(self, tmp_path):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / "main.js").write_text(
            "// vendor/oldlib is deprecated\nconst x = 1;\n",
            encoding="utf-8",
        )
        refs = vd._scan_refs(tmp_path, vendor_dir)
        assert refs == {}

    def test_skips_vendor_dir_itself(self, tmp_path):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (vendor_dir / "mylib").mkdir()
        (vendor_dir / "mylib" / "mod.py").write_text(
            "# this is in vendor/lib.py\n",
            encoding="utf-8",
        )
        refs = vd._scan_refs(tmp_path, vendor_dir)
        assert refs == {}

    def test_respects_file_extensions(self, tmp_path):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / "data.bin").write_bytes(b"vendor/mylib binary content")
        refs = vd._scan_refs(tmp_path, vendor_dir)
        assert refs == {}

    def test_skips_agents_directory(self, tmp_path):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        agents_dir = tmp_path / ".agents"
        agents_dir.mkdir()
        (agents_dir / "test.py").write_text(
            '"vendor/test" reference in .agents should be skipped\n',
            encoding="utf-8",
        )
        refs = vd._scan_refs(tmp_path, vendor_dir)
        assert refs == {}


class TestCreateTemplates:
    """_create_templates 测试。"""

    def test_creates_vendor_dir_and_root_files(self, tmp_path):
        vendor_dir = tmp_path / "vendor"
        created = vd._create_templates(tmp_path, vendor_dir)
        assert vendor_dir.exists()
        assert (vendor_dir / "README.md").exists()
        assert (vendor_dir / "VERSION.md").exists()
        assert "vendor/README.md" in created
        assert "vendor/VERSION.md" in created

    def test_does_not_overwrite_existing(self, tmp_path):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (vendor_dir / "README.md").write_text("custom", encoding="utf-8")
        created = vd._create_templates(tmp_path, vendor_dir)
        assert "vendor/README.md" not in created
        assert (vendor_dir / "README.md").read_text(encoding="utf-8") == "custom"

    def test_creates_lib_readmes(self, tmp_path):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (vendor_dir / "mylib").mkdir()
        created = vd._create_templates(tmp_path, vendor_dir)
        assert "vendor/mylib/README.md" in created
        content = (vendor_dir / "mylib" / "README.md").read_text(encoding="utf-8")
        assert "mylib" in content
        assert "名称" in content

    def test_no_libs_empty_state(self, tmp_path):
        vendor_dir = tmp_path / "vendor"
        created = vd._create_templates(tmp_path, vendor_dir)
        readme = (vendor_dir / "README.md").read_text(encoding="utf-8")
        assert "暂无依赖" in readme


class TestRun:
    """run() 集成测试。"""

    def test_vendor_dir_not_exist_no_fix(self, tmp_path, args_default, capsys):
        ret = vd.run(tmp_path, args_default)
        assert ret == 0
        out = capsys.readouterr().out
        assert "vendor 目录不存在" in out
        assert "提示" in out

    def test_vendor_dir_not_exist_with_fix(self, tmp_path, args_fix, capsys):
        ret = vd.run(tmp_path, args_fix)
        assert ret == 0
        out = capsys.readouterr().out
        assert "已创建" in out
        assert (tmp_path / "vendor" / "README.md").exists()

    def test_clean_vendor_passes(self, tmp_path, args_default, capsys):
        """干净配置：.gitignore 无 vendor/ 规则 + 根文件齐全 + 无子模块问题。"""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n.temp/\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        ret = vd.run(tmp_path, args_default)
        out = capsys.readouterr().out
        assert ret == 0, f"Expected pass, got output:\n{out}"
        assert "检查通过" in out

    def test_gitignore_has_vendor_blanket_rule(self, tmp_path, args_default, capsys):
        """.gitignore 包含 vendor/ 整体忽略 = 错误。"""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("vendor/\n*.pyc\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        ret = vd.run(tmp_path, args_default)
        assert ret == 1
        out = capsys.readouterr().out
        assert "整体忽略" in out

    def test_missing_gitignore_file(self, tmp_path, args_default, capsys):
        """没有 .gitignore 文件 = 错误。"""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        ret = vd.run(tmp_path, args_default)
        assert ret == 1
        out = capsys.readouterr().out
        assert ".gitignore 文件不存在" in out

    def test_missing_root_files(self, tmp_path, args_default, capsys):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        ret = vd.run(tmp_path, args_default)
        assert ret == 1
        out = capsys.readouterr().out
        assert "缺少必需文件" in out

    def test_lib_missing_readme(self, tmp_path, args_default, capsys):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        (vendor_dir / "badlib").mkdir()
        ret = vd.run(tmp_path, args_default)
        assert ret == 1
        out = capsys.readouterr().out
        assert "badlib" in out

    def test_submodule_skipped_in_lib_check(self, tmp_path, args_default, capsys):
        """子模块目录不检查 README.md 元数据。"""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        (tmp_path / ".gitmodules").write_text(
            '[submodule "vendor/flexloop"]\n'
            '    path = vendor/flexloop\n'
            '    url = git@example.com:flexloop.git\n',
            encoding="utf-8",
        )
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        (vendor_dir / "flexloop").mkdir()
        (vendor_dir / "flexloop" / "README.md").write_text("Upstream readme\n", encoding="utf-8")
        ret = vd.run(tmp_path, args_default)
        out = capsys.readouterr().out
        assert ret == 0, f"Expected pass, got output:\n{out}"
        assert "子模块" in out
        assert "flexloop" in out
        assert "检查通过" in out

    def test_submodules_with_no_manual_libs(self, tmp_path, args_default, capsys):
        """全部是子模块，无手动依赖 = 通过。"""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n.temp/\n", encoding="utf-8")
        (tmp_path / ".gitmodules").write_text(
            '[submodule "vendor/flexloop"]\n'
            '    path = vendor/flexloop\n'
            '    url = git@example.com:flexloop.git\n'
            '[submodule "vendor/ark-cli"]\n'
            '    path = vendor/ark-cli\n'
            '    url = git@example.com:ark-cli.git\n',
            encoding="utf-8",
        )
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        (vendor_dir / "flexloop").mkdir()
        (vendor_dir / "ark-cli").mkdir()
        ret = vd.run(tmp_path, args_default)
        out = capsys.readouterr().out
        assert ret == 0, f"Expected pass, got output:\n{out}"
        assert "检查通过" in out

    def test_warnings_do_not_cause_failure(self, tmp_path, capsys):
        """警告不应导致返回码为 1（只有 errors 才会）。"""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        sm_dir = vendor_dir / "uninit_submod"
        sm_dir.mkdir()
        (tmp_path / ".gitmodules").write_text(
            '[submodule "vendor/uninit_submod"]\n'
            '    path = vendor/uninit_submod\n'
            '    url = git@example.com:test.git\n',
            encoding="utf-8",
        )
        args = argparse.Namespace(fix=False, scan_refs=False, path=None, deep=False, debug=False, json=False)
        ret = vd.run(tmp_path, args)
        out = capsys.readouterr().out
        assert ret == 0, f"Warnings should not cause failure, got:\n{out}"
        assert "未初始化" in out

    def test_debug_outputs_to_stderr(self, tmp_path, capsys):
        """--debug 模式应输出日志到 stderr。"""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        args = argparse.Namespace(fix=False, scan_refs=False, path=None, deep=False, debug=True, json=False)
        vd.run(tmp_path, args)
        captured = capsys.readouterr()
        assert "[DEBUG:vendor]" in captured.err


class TestBuildParser:
    """CLI 参数解析器测试。"""

    def test_default_args(self):
        """默认参数值正确。"""
        parser = vd.build_parser()
        args = parser.parse_args([])
        assert args.fix is False
        assert args.scan_refs is False
        assert args.deep is False
        assert args.debug is False
        assert args.json is False
        assert args.path is None

    def test_fix_flag(self):
        parser = vd.build_parser()
        args = parser.parse_args(["--fix"])
        assert args.fix is True

    def test_scan_refs_flag(self):
        parser = vd.build_parser()
        args = parser.parse_args(["--scan-refs"])
        assert args.scan_refs is True

    def test_deep_flag(self):
        parser = vd.build_parser()
        args = parser.parse_args(["--deep"])
        assert args.deep is True

    def test_debug_flag(self):
        parser = vd.build_parser()
        args = parser.parse_args(["--debug"])
        assert args.debug is True

    def test_json_flag(self):
        parser = vd.build_parser()
        args = parser.parse_args(["--json"])
        assert args.json is True

    def test_path_option(self):
        parser = vd.build_parser()
        args = parser.parse_args(["--path", "/tmp/test-proj"])
        assert args.path == "/tmp/test-proj"

    def test_combined_flags(self):
        parser = vd.build_parser()
        args = parser.parse_args(["--fix", "--deep", "--json", "--debug"])
        assert args.fix is True
        assert args.deep is True
        assert args.json is True
        assert args.debug is True

    def test_prog_name(self):
        parser = vd.build_parser()
        assert parser.prog == "vendor-check"


class TestCliMain:
    """独立 CLI main() 入口测试。"""

    def test_main_clean_project(self, tmp_path, capsys):
        """干净项目应返回 0。"""
        import sys
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n__pycache__/\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n\n| 名称 | 类型 | 版本 |\n|---|---|---|\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n\n| 库名称 | 版本号 |\n|---|---|\n", encoding="utf-8")
        ret = vd.main(["--path", str(tmp_path)])
        assert ret == 0
        out = capsys.readouterr().out
        assert "vendor 目录检查通过" in out

    def test_main_json_output(self, tmp_path, capsys):
        """--json 应输出有效的 JSON。"""
        import json as _json
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        ret = vd.main(["--path", str(tmp_path), "--json"])
        assert ret == 0
        out = capsys.readouterr().out
        data = _json.loads(out)
        assert data["tool"] == "vendor-check"
        assert data["passed"] is True
        assert "summary" in data
        assert "checks" in data
        assert data["summary"]["error"] == 0

    def test_main_fix_creates_vendor(self, tmp_path, capsys):
        """--fix 在 vendor 不存在时创建标准结构。"""
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        ret = vd.main(["--path", str(tmp_path), "--fix"])
        assert ret == 0
        assert (tmp_path / "vendor" / "README.md").exists()
        assert (tmp_path / "vendor" / "VERSION.md").exists()

    def test_main_fix_json(self, tmp_path, capsys):
        """--fix --json 在 vendor 不存在时输出 JSON 结果。"""
        import json as _json
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        ret = vd.main(["--path", str(tmp_path), "--fix", "--json"])
        assert ret == 0
        out = capsys.readouterr().out
        data = _json.loads(out)
        assert data["passed"] is True
        assert data["summary"]["error"] == 0

    def test_main_vendor_missing_no_fix(self, tmp_path, capsys):
        """vendor 不存在且无 --fix 时返回 0（警告）。"""
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        ret = vd.main(["--path", str(tmp_path)])
        assert ret == 0
        out = capsys.readouterr().out
        assert "vendor 目录不存在" in out

    def test_main_gitignore_error(self, tmp_path, capsys):
        """.gitignore 包含 vendor/ 规则时返回 1。"""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("vendor/\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        ret = vd.main(["--path", str(tmp_path)])
        assert ret == 1
        out = capsys.readouterr().out
        assert "vendor/ 整体忽略规则" in out

    def test_main_gitignore_error_json(self, tmp_path, capsys):
        """JSON 模式下 .gitignore 错误应返回错误结果。"""
        import json as _json
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("vendor/\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        ret = vd.main(["--path", str(tmp_path), "--json"])
        assert ret == 1
        out = capsys.readouterr().out
        data = _json.loads(out)
        assert data["passed"] is False
        assert data["summary"]["error"] >= 1
        gitignore_checks = [c for c in data["checks"] if c["name"] == "gitignore"]
        assert len(gitignore_checks) == 1
        assert gitignore_checks[0]["status"] == "error"

    def test_main_deep_flag(self, tmp_path, capsys):
        """--deep 应执行子模块深度检查。"""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        ret = vd.main(["--path", str(tmp_path), "--deep"])
        assert ret == 0
        out = capsys.readouterr().out
        assert "子模块深度集成验证" in out

    def test_main_version_flag(self, tmp_path, capsys):
        """--version 应输出版本号并退出（SystemExit）。"""
        import pytest
        with pytest.raises(SystemExit) as exc_info:
            vd.main(["--version"])
        assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "vendor-check 1.0.0" in out

    def test_main_help_flag(self, tmp_path, capsys):
        """--help 应输出帮助并退出（SystemExit）。"""
        import pytest
        with pytest.raises(SystemExit) as exc_info:
            vd.main(["--help"])
        assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "vendor 目录合规性检查工具" in out
        assert "--fix" in out
        assert "--json" in out

    def test_main_argv_none_uses_sysargv(self, tmp_path, monkeypatch, capsys):
        """main(argv=None) 应使用 sys.argv[1:]。"""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        monkeypatch.setattr("sys.argv", ["vendor-check", "--path", str(tmp_path)])
        ret = vd.main()
        assert ret == 0


class TestCheckVendorScript:
    """顶层 check-vendor.py 脚本集成测试。"""

    def test_script_importable(self):
        """check-vendor.py 作为模块应可导入并调用 main。"""
        import importlib.util
        script_path = Path(__file__).parent.parent / "check-vendor.py"
        spec = importlib.util.spec_from_file_location("check_vendor_script", str(script_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert hasattr(module, "main")
        assert callable(module.main)

    def test_script_json_output_subprocess(self, tmp_path):
        """通过 subprocess 调用 check-vendor.py --json 应输出有效 JSON。"""
        import subprocess
        import json as _json
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        script_path = Path(__file__).parent.parent / "check-vendor.py"
        result = subprocess.run(
            [sys.executable, str(script_path), "--path", str(tmp_path), "--json"],
            capture_output=True, text=True, timeout=30,
            cwd=str(Path(__file__).parent.parent),
        )
        assert result.returncode == 0
        data = _json.loads(result.stdout)
        assert data["tool"] == "vendor-check"
        assert data["passed"] is True


class TestTiming:
    """步骤耗时日志测试。"""

    def test_json_output_contains_step_timings(self, tmp_path, capsys):
        """JSON 输出应包含 step_timings_ms 和 total_duration_ms 字段。"""
        import json as _json
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        args = argparse.Namespace(fix=False, scan_refs=False, path=str(tmp_path),
                                  deep=False, debug=False, json=True)
        ret = vd.run(tmp_path, args)
        assert ret == 0
        out = capsys.readouterr().out
        data = _json.loads(out)
        assert "step_timings_ms" in data
        assert "total_duration_ms" in data
        assert data["total_duration_ms"] >= 0
        steps = {s["step"] for s in data["step_timings_ms"]}
        assert "submodules" in steps
        assert "gitignore" in steps
        assert "root_files" in steps
        assert "manual_libs" in steps
        for s in data["step_timings_ms"]:
            assert "duration_ms" in s
            assert s["duration_ms"] >= 0

    def test_json_checks_have_duration_ms(self, tmp_path, capsys):
        """每个 check 条目应包含 duration_ms 字段。"""
        import json as _json
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        args = argparse.Namespace(fix=False, scan_refs=False, path=str(tmp_path),
                                  deep=False, debug=False, json=True)
        vd.run(tmp_path, args)
        data = _json.loads(capsys.readouterr().out)
        for check in data["checks"]:
            assert "duration_ms" in check, f"check '{check['name']}' missing duration_ms"
            assert check["duration_ms"] >= 0

    def test_text_output_shows_step_timings(self, tmp_path, capsys):
        """文本输出应显示每个步骤的耗时和总耗时。"""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        args = argparse.Namespace(fix=False, scan_refs=False, path=str(tmp_path),
                                  deep=False, debug=False, json=False)
        vd.run(tmp_path, args)
        out = capsys.readouterr().out
        assert "耗时:" in out
        assert "总耗时:" in out
        assert "submodules:" in out
        assert "gitignore:" in out

    def test_text_timing_units(self, tmp_path, capsys):
        """耗时单位应自适应（μs/ms/s）。"""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        args = argparse.Namespace(fix=False, scan_refs=False, path=str(tmp_path),
                                  deep=False, debug=False, json=False)
        vd.run(tmp_path, args)
        out = capsys.readouterr().out
        assert "μs" in out or "ms" in out

    def test_vendor_missing_fix_json_timing(self, tmp_path, capsys):
        """vendor 目录不存在 + --fix 快速路径也应包含耗时。"""
        import json as _json
        args = argparse.Namespace(fix=True, scan_refs=False, path=str(tmp_path),
                                  deep=False, debug=False, json=True)
        vd.run(tmp_path, args)
        data = _json.loads(capsys.readouterr().out)
        assert "total_duration_ms" in data
        assert "step_timings_ms" in data
        assert data["total_duration_ms"] > 0

    def test_debug_output_has_timing_logs(self, tmp_path, capsys):
        """--debug 模式下 stderr 应包含 timing 模块的调试日志。"""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        args = argparse.Namespace(fix=False, scan_refs=False, path=str(tmp_path),
                                  deep=False, debug=True, json=False)
        vd.run(tmp_path, args)
        err = capsys.readouterr().err
        assert "[timing]" in err
        assert "步骤开始:" in err
        assert "步骤完成:" in err
        assert "总耗时:" in err
