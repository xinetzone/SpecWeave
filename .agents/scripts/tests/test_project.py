"""lib.project 单元测试。"""

from pathlib import Path

import pytest

from lib import project as pj


class TestResolveProjectRoot:

    def test_none_anchor_raises(self):
        with pytest.raises(ValueError, match="必须显式传入"):
            pj.resolve_project_root(None)

    def test_finds_agents_md(self, tmp_path):
        """从子目录向上查找 AGENTS.md。"""
        (tmp_path / "AGENTS.md").write_text("# Project\n", encoding="utf-8")
        sub = tmp_path / ".agents" / "scripts"
        sub.mkdir(parents=True)
        anchor = sub / "test.py"
        anchor.write_text("# anchor\n", encoding="utf-8")
        root = pj.resolve_project_root(str(anchor))
        assert root == tmp_path.resolve()

    def test_file_anchor_uses_parent(self, tmp_path):
        """传入文件路径时先取 parent 再向上查找。"""
        (tmp_path / "AGENTS.md").write_text("# P\n", encoding="utf-8")
        f = tmp_path / "script.py"
        f.write_text("# s\n", encoding="utf-8")
        root = pj.resolve_project_root(str(f))
        assert root == tmp_path.resolve()

    def test_falls_back_to_readme(self, tmp_path):
        """无 AGENTS.md 时回退到含 README.md 的目录。"""
        (tmp_path / "README.md").write_text("# P\n", encoding="utf-8")
        sub = tmp_path / "src"
        sub.mkdir()
        f = sub / "mod.py"
        f.write_text("# m\n", encoding="utf-8")
        root = pj.resolve_project_root(str(f))
        assert root == tmp_path.resolve()

    def test_no_root_raises(self, tmp_path):
        """既无 AGENTS.md 也无 README.md 时抛 FileNotFoundError。"""
        sub = tmp_path / "deep" / "nested"
        sub.mkdir(parents=True)
        f = sub / "x.py"
        f.write_text("# x\n", encoding="utf-8")
        with pytest.raises(FileNotFoundError):
            pj.resolve_project_root(str(f))

    def test_path_object_anchor(self, tmp_path):
        (tmp_path / "AGENTS.md").write_text("# P\n", encoding="utf-8")
        root = pj.resolve_project_root(tmp_path)
        assert root == tmp_path.resolve()


class TestResolveAgentsDir:

    def test_resolves_agents_dir(self, tmp_path):
        (tmp_path / "AGENTS.md").write_text("# P\n", encoding="utf-8")
        sub = tmp_path / ".agents" / "scripts"
        sub.mkdir(parents=True)
        agents_dir = pj.resolve_agents_dir(str(sub / "s.py"))
        assert agents_dir == (tmp_path / ".agents").resolve()


class TestResolveScriptsDir:

    def test_resolves_scripts_dir(self, tmp_path):
        (tmp_path / "AGENTS.md").write_text("# P\n", encoding="utf-8")
        sub = tmp_path / ".agents" / "scripts" / "lib"
        sub.mkdir(parents=True)
        scripts_dir = pj.resolve_scripts_dir(str(sub / "m.py"))
        assert scripts_dir == (tmp_path / ".agents" / "scripts").resolve()
