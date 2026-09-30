"""scaffold 模块测试：deb 骨架与 dput 配置生成。"""

import pytest

from okw import scaffold
from okw.scaffold import ScaffoldError

class TestScaffoldDeb:
    @pytest.mark.parametrize("series,expected_codename", [
        ("yangtze", "yangtze"), ("1.0", "yangtze"),
        ("nile", "nile"), ("2.0", "nile"),
        ("huanghe", "huanghe"), ("3.0", "huanghe"),
    ])
    def test_series_parametrized(self, tmp_path, series, expected_codename):
        files = scaffold.scaffold_deb("demo", series, "0.1.0", tmp_path)
        paths = {p.name: p for p in files}
        assert set(paths) == {"control", "changelog", "rules", "compat", "format"}
        changelog = paths["changelog"].read_text(encoding="utf-8")
        assert changelog.startswith(f"demo (0.1.0) {expected_codename}; urgency=medium")
        control = paths["control"].read_text(encoding="utf-8")
        assert "Package: demo" in control and "Architecture: amd64" in control
        assert "Source: demo" in control
        assert paths["compat"].read_text(encoding="utf-8").strip() == "12"
        assert paths["format"].read_text(encoding="utf-8").strip() == "3.0 (quilt)"
        assert "dh $@" in paths["rules"].read_text(encoding="utf-8")

    def test_unknown_series(self, tmp_path):
        with pytest.raises(ScaffoldError):
            scaffold.scaffold_deb("demo", "fedora", "0.1.0", tmp_path)

    def test_empty_project(self, tmp_path):
        with pytest.raises(ScaffoldError):
            scaffold.scaffold_deb("", "huanghe", "0.1.0", tmp_path)

class TestScaffoldDput:
    def test_fields_match_kb(self):
        text, written = scaffold.scaffold_dput("myopenkylinid")
        assert "[okbs]" in text
        assert "fqdn = upload.build.openkylin.top:2121" in text
        assert "method = sftp" in text
        assert "incoming = %(okbs)s" in text
        assert "login = myopenkylinid" in text
        assert "dput okbs:~myopenkylinid/ppa" in text
        assert written is None  # 默认不写文件

    def test_write_output(self, tmp_path):
        out = tmp_path / "dput.cf"
        text, written = scaffold.scaffold_dput("id2", output=out)
        assert written == out and out.read_text(encoding="utf-8") == text

    def test_empty_id(self):
        with pytest.raises(ScaffoldError):
            scaffold.scaffold_dput("   ")

    def test_series_alias_table(self):
        assert scaffold.SERIES_ALIASES["1.0"] == "yangtze"
        assert scaffold.SERIES_ALIASES["2.0"] == "nile"
        assert scaffold.SERIES_ALIASES["3.0"] == "huanghe"
        assert scaffold.OKBS_FQDN == "upload.build.openkylin.top:2121"
