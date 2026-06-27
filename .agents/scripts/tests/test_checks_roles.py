"""lib.checks.roles 单元测试。"""

import argparse
import json
from pathlib import Path

import pytest

from lib.checks import roles as rl


@pytest.fixture
def args_default():
    return argparse.Namespace(path=None, json=False)


@pytest.fixture
def args_json():
    return argparse.Namespace(path=None, json=True)


def _write_role(roles_dir: Path, name: str, frontmatter: str) -> Path:
    """Helper: 写入带 TOML frontmatter 的角色文件。"""
    p = roles_dir / name
    p.write_text(f"+++\n{frontmatter}\n+++\n\n# Role\n", encoding="utf-8")
    return p


class TestFindRoleFiles:
    """_find_role_files 测试。"""

    def test_finds_role_files(self, tmp_path):
        _write_role(tmp_path, "developer.md", 'id = "dev"')
        _write_role(tmp_path, "architect.md", 'id = "arch"')
        files = rl._find_role_files(tmp_path)
        names = sorted(f.name for f in files)
        assert names == ["architect.md", "developer.md"]

    def test_excludes_readme(self, tmp_path):
        _write_role(tmp_path, "developer.md", 'id = "dev"')
        (tmp_path / "README.md").write_text("# Roles\n", encoding="utf-8")
        files = rl._find_role_files(tmp_path)
        names = [f.name for f in files]
        assert "README.md" not in names
        assert "developer.md" in names

    def test_empty_dir(self, tmp_path):
        assert rl._find_role_files(tmp_path) == []

    def test_sorted_order(self, tmp_path):
        for name in ["tester.md", "architect.md", "developer.md"]:
            _write_role(tmp_path, name, 'id = "x"')
        files = rl._find_role_files(tmp_path)
        names = [f.name for f in files]
        assert names == sorted(names)


class TestExtractTier:
    """_extract_tier 测试。"""

    def test_explicit_tier(self):
        fm = 'tier = "co-founder"\n'
        assert rl._extract_tier(fm) == "co-founder"

    def test_default_standard(self):
        fm = 'id = "developer"\n'
        assert rl._extract_tier(fm) == "standard"

    def test_empty_frontmatter(self):
        assert rl._extract_tier("") == "standard"


class TestExtractPermissions:
    """_extract_permissions 测试。"""

    def test_no_permissions_table(self):
        fm = 'tier = "standard"\n'
        has_perm, view, manage = rl._extract_permissions(fm)
        assert has_perm is False
        assert view is None
        assert manage is None

    def test_complete_permissions(self):
        fm = '[permissions]\nview = "core-team"\nmanage = "co-founders"\n'
        has_perm, view, manage = rl._extract_permissions(fm)
        assert has_perm is True
        assert view == "core-team"
        assert manage == "co-founders"

    def test_permissions_missing_view(self):
        fm = '[permissions]\nmanage = "admins"\n'
        has_perm, view, manage = rl._extract_permissions(fm)
        assert has_perm is True
        assert view is None
        assert manage == "admins"

    def test_permissions_missing_manage(self):
        fm = '[permissions]\nview = "public"\n'
        has_perm, view, manage = rl._extract_permissions(fm)
        assert has_perm is True
        assert view == "public"
        assert manage is None

    def test_permissions_with_following_table(self):
        fm = '[permissions]\nview = "team"\nmanage = "leads"\n\n[bindings]\nrules = []\n'
        has_perm, view, manage = rl._extract_permissions(fm)
        assert has_perm is True
        assert view == "team"
        assert manage == "leads"


class TestValidateRoleFile:
    """_validate_role_file 测试。"""

    def test_missing_frontmatter(self, tmp_path):
        p = tmp_path / "bad.md"
        p.write_text("# No frontmatter\n", encoding="utf-8")
        result = rl._validate_role_file(p)
        assert result["valid"] is False
        assert result["file"] == "bad.md"
        assert any("frontmatter" in e for e in result["errors"])

    def test_valid_standard_role(self, tmp_path):
        p = _write_role(tmp_path, "dev.md", 'id = "developer"\ntier = "standard"\n')
        result = rl._validate_role_file(p)
        assert result["valid"] is True
        assert result["tier"] == "standard"
        assert result["errors"] == []

    def test_valid_cofounder_role(self, tmp_path):
        p = _write_role(
            tmp_path, "cf.md",
            'tier = "co-founder"\n\n[permissions]\nview = "core"\nmanage = "founders"\n'
        )
        result = rl._validate_role_file(p)
        assert result["valid"] is True
        assert result["tier"] == "co-founder"
        assert result["has_permissions"] is True
        assert result["view"] == "core"
        assert result["manage"] == "founders"

    def test_invalid_tier_value(self, tmp_path):
        p = _write_role(tmp_path, "bad.md", 'tier = "admin"\n')
        result = rl._validate_role_file(p)
        assert result["valid"] is False
        assert any("tier 字段值非法" in e for e in result["errors"])

    def test_cofounder_missing_permissions_table(self, tmp_path):
        p = _write_role(tmp_path, "cf.md", 'tier = "co-founder"\n')
        result = rl._validate_role_file(p)
        assert result["valid"] is False
        assert any("缺少 [permissions] 表" in e for e in result["errors"])

    def test_cofounder_missing_view_field(self, tmp_path):
        p = _write_role(
            tmp_path, "cf.md",
            'tier = "co-founder"\n\n[permissions]\nmanage = "founders"\n'
        )
        result = rl._validate_role_file(p)
        assert result["valid"] is False
        assert any("缺少 view 字段" in e for e in result["errors"])

    def test_cofounder_missing_manage_field(self, tmp_path):
        p = _write_role(
            tmp_path, "cf.md",
            'tier = "co-founder"\n\n[permissions]\nview = "core"\n'
        )
        result = rl._validate_role_file(p)
        assert result["valid"] is False
        assert any("缺少 manage 字段" in e for e in result["errors"])

    def test_standard_role_no_permissions_ok(self, tmp_path):
        """standard 角色没有 [permissions] 表是合法的。"""
        p = _write_role(tmp_path, "dev.md", 'id = "dev"\ntier = "standard"\n')
        result = rl._validate_role_file(p)
        assert result["valid"] is True


class TestRun:
    """run() 集成测试。"""

    def test_nonexistent_dir(self, tmp_path, args_default, capsys):
        args = argparse.Namespace(path=str(tmp_path / "nonexistent"), json=False)
        ret = rl.run(tmp_path, args)
        assert ret == 1

    def test_all_valid_text_output(self, tmp_path, args_default, capsys):
        _write_role(tmp_path, "dev.md", 'id = "dev"\ntier = "standard"\n')
        _write_role(
            tmp_path, "cf.md",
            'tier = "co-founder"\n\n[permissions]\nview = "core"\nmanage = "founders"\n'
        )
        args = argparse.Namespace(path=str(tmp_path), json=False)
        ret = rl.run(tmp_path, args)
        assert ret == 0
        out = capsys.readouterr().out
        assert "frontmatter 有效" in out
        assert "tier 字段值合法" in out
        assert "权限声明完整" in out

    def test_json_output(self, tmp_path, args_json, capsys):
        _write_role(tmp_path, "dev.md", 'id = "dev"\ntier = "standard"\n')
        args = argparse.Namespace(path=str(tmp_path), json=True)
        ret = rl.run(tmp_path, args)
        assert ret == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["summary"]["total_files"] == 1
        assert data["summary"]["errors"] == 0
        assert data["files"][0]["file"] == "dev.md"

    def test_invalid_file_returns_1(self, tmp_path, args_default, capsys):
        (tmp_path / "bad.md").write_text("# no frontmatter\n", encoding="utf-8")
        args = argparse.Namespace(path=str(tmp_path), json=False)
        ret = rl.run(tmp_path, args)
        assert ret == 1
        out = capsys.readouterr().out
        assert "失败" in out

    def test_json_output_with_errors(self, tmp_path, capsys):
        bad = tmp_path / "bad.md"
        bad.write_text("# no fm\n", encoding="utf-8")
        args = argparse.Namespace(path=str(tmp_path), json=True)
        ret = rl.run(tmp_path, args)
        assert ret == 1
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["summary"]["errors"] == 1
