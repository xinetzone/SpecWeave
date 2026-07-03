from .conftest import mf, create_toml_md


class TestComputeTomlRefPath:
    def test_root_level_file(self):
        ref = mf.compute_toml_ref_path("README.md")
        assert ref == ".meta/toml/README.toml"
        assert "\\" not in ref

    def test_one_level_deep(self):
        ref = mf.compute_toml_ref_path("docs/README.md")
        assert ref == "../.meta/toml/docs/README.toml"

    def test_two_levels_deep(self):
        ref = mf.compute_toml_ref_path("docs/knowledge/README.md")
        assert ref == "../../.meta/toml/docs/knowledge/README.toml"

    def test_three_levels_deep(self):
        ref = mf.compute_toml_ref_path("docs/retrospective/patterns/factory.md")
        assert ref == "../../../.meta/toml/docs/retrospective/patterns/factory.toml"

    def test_four_levels_deep(self):
        ref = mf.compute_toml_ref_path("a/b/c/d/e/file.md")
        assert ref == "../../../../../.meta/toml/a/b/c/d/e/file.toml"

    def test_uses_forward_slashes(self):
        ref = mf.compute_toml_ref_path("docs/guide/intro.md")
        assert "\\" not in ref
        assert "/" in ref


class TestWindowsPathHandling:
    def test_rel_path_uses_forward_slash(self, tmp_path):
        md_path = tmp_path / "sub" / "dir" / "win.md"
        create_toml_md(md_path, {"id": "w"}, "# Body\n")

        result = mf.convert_file(md_path, tmp_path, dry_run=False, backup=False)
        assert "\\" not in result["path"]
        assert "/" in result["path"] or result["path"] == "win.md"

    def test_toml_ref_uses_forward_slash(self):
        ref = mf.compute_toml_ref_path("a/b/c.md")
        assert "\\" not in ref
