"""ref 模块测试：知识库参考主题内容与相对路径存在性。"""

from okw import ref

from conftest import REPO_ROOT

class TestTopics:
    def test_series_content(self):
        t = ref.get_topic("series")
        assert t is not None
        text = ref.format_topic(t)
        assert "yangtze" in text and "nile" in text and "huanghe" in text
        assert "3.0" in text

    def test_wsl_troubleshoot_content(self):
        t = ref.get_topic("wsl-troubleshoot")
        text = ref.format_topic(t)
        assert "E_UNEXPECTED" in text or "E_ABORT" in text
        assert "wsl --shutdown" in text
        assert "passwd" in text

    def test_okbs_content(self):
        t = ref.get_topic("okbs")
        text = ref.format_topic(t)
        assert "upload.build.openkylin.top:2121" in text
        assert "dput okbs" in text
        assert "paramiko" in text

    def test_verify_content(self):
        t = ref.get_topic("verify")
        text = ref.format_topic(t)
        assert "dpkg-query -W" in text
        assert "systemd" in text

    def test_unknown_topic(self):
        assert ref.get_topic("nope") is None

    def test_list_topics(self):
        names = ref.list_topics()
        assert set(names) == {"series", "wsl-troubleshoot", "okbs", "verify"}

    def test_source_paths_exist(self):
        """每条相对路径在仓库内真实存在。"""
        missing = []
        for name in ref.list_topics():
            t = ref.get_topic(name)
            assert t is not None
            for src in t.sources:
                if not (REPO_ROOT / src).exists():
                    missing.append(src)
        assert missing == [], f"知识库相对路径不存在：{missing}"
