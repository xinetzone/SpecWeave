"""lib.checks.vendor 单元测试。"""

import argparse
from pathlib import Path

import pytest

from lib.checks import vendor as vd


@pytest.fixture
def args_default():
    return argparse.Namespace(fix=False, scan_refs=False, path=None)


@pytest.fixture
def args_fix():
    return argparse.Namespace(fix=True, scan_refs=False, path=None)


@pytest.fixture
def args_scan():
    return argparse.Namespace(fix=False, scan_refs=True, path=None)


class TestCheckGitignoreRule:
    """_check_gitignore_rule 测试。"""

    def test_missing_gitignore(self, tmp_path):
        assert vd._check_gitignore_rule(tmp_path) is False

    def test_gitignore_without_vendor(self, tmp_path):
        (tmp_path / ".gitignore").write_text("*.pyc\nnode_modules/\n", encoding="utf-8")
        assert vd._check_gitignore_rule(tmp_path) is False

    def test_gitignore_with_vendor(self, tmp_path):
        (tmp_path / ".gitignore").write_text("vendor/\n*.pyc\n", encoding="utf-8")
        assert vd._check_gitignore_rule(tmp_path) is True

    def test_gitignore_with_vendor_star(self, tmp_path):
        (tmp_path / ".gitignore").write_text("vendor/*\n!vendor/flexloop/\n", encoding="utf-8")
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

    def test_readme_partial_fields(self, tmp_path):
        lib_dir = tmp_path / "mylib"
        lib_dir.mkdir()
        content = "- **名称**：mylib\n- **版本**：1.0.0\n"
        (lib_dir / "README.md").write_text(content, encoding="utf-8")
        ok, issues = vd._check_lib_readme(lib_dir)
        assert ok is False
        assert len(issues) == 4


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

    def test_skips_comment_lines(self, tmp_path):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / "main.py").write_text(
            "# vendor/oldlib is deprecated\nimport os\n",
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
        assert "创建 vendor" in out
        assert (tmp_path / "vendor" / "README.md").exists()

    def test_clean_vendor_passes(self, tmp_path, args_default, capsys):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("vendor/\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        ret = vd.run(tmp_path, args_default)
        assert ret == 0
        out = capsys.readouterr().out
        assert "检查通过" in out

    def test_missing_gitignore_rule(self, tmp_path, args_default, capsys):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        ret = vd.run(tmp_path, args_default)
        assert ret == 1
        out = capsys.readouterr().out
        assert "缺少 vendor/ 忽略规则" in out

    def test_missing_root_files(self, tmp_path, args_default, capsys):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("vendor/\n", encoding="utf-8")
        ret = vd.run(tmp_path, args_default)
        assert ret == 1
        out = capsys.readouterr().out
        assert "缺少必需文件" in out

    def test_lib_missing_readme(self, tmp_path, args_default, capsys):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("vendor/\n", encoding="utf-8")
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        (vendor_dir / "badlib").mkdir()
        ret = vd.run(tmp_path, args_default)
        assert ret == 1
        out = capsys.readouterr().out
        assert "badlib" in out

    def test_submodule_skipped_in_lib_check(self, tmp_path, args_default, capsys):
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        (tmp_path / ".gitignore").write_text("vendor/*\n!vendor/flexloop/\n", encoding="utf-8")
        (tmp_path / ".gitmodules").write_text(
            '[submodule "vendor/flexloop"]\n'
            '    path = vendor/flexloop\n'
            '    url = git@example.com:flexloop.git\n',
            encoding="utf-8",
        )
        (vendor_dir / "README.md").write_text("# Vendor\n", encoding="utf-8")
        (vendor_dir / "VERSION.md").write_text("# Versions\n", encoding="utf-8")
        (vendor_dir / "flexloop").mkdir()
        (vendor_dir / "flexloop" / "README.md").write_text("Upstream project readme without our fields\n", encoding="utf-8")
        ret = vd.run(tmp_path, args_default)
        assert ret == 0
        out = capsys.readouterr().out
        assert "子模块" in out
        assert "flexloop" in out
        assert "检查通过" in out
