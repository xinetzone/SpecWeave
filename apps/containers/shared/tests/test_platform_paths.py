"""platform_paths 的平台分支测试（无 daemon、无网络）。"""
import platform as _platform

from jpman_common import platform_paths as pp


def test_normalize_windows_drive_path():
    assert pp.normalize_path_str("D:\\foo\\bar") == "/mnt/d/foo/bar"
    assert pp.normalize_path_str("c:\\Users\\x") == "/mnt/c/Users/x"


def test_normalize_windows_posix_passthrough():
    # 以 / 开头（含 /mnt/d 与裸 Unix 绝对路径）原样返回
    assert pp.normalize_path_str("/mnt/d/ws") == "/mnt/d/ws"
    assert pp.normalize_path_str("/workspace") == "/workspace"


def test_normalize_windows_relative_backslashes():
    assert pp.normalize_path_str("rel\\path") == "rel/path"
    assert pp.normalize_path_str("plain") == "plain"


def test_normalize_non_windows_passthrough(monkeypatch):
    monkeypatch.setattr(pp.platform, "system", lambda: "Linux")
    raw = "D:\\foo\\bar"
    assert pp.normalize_path_str(raw) == raw
    assert pp.normalize_path_str("/any/path") == "/any/path"


def test_to_posix_path_real_platform(tmp_path):
    result = pp.to_posix_path(tmp_path)
    if _platform.system() == "Windows":
        assert result.startswith("/mnt/")
        assert ":" not in result
        assert "\\" not in result
    else:
        assert result == str(tmp_path.resolve())


def test_to_posix_path_non_windows(monkeypatch, tmp_path):
    monkeypatch.setattr(pp.platform, "system", lambda: "Linux")
    assert pp.to_posix_path(tmp_path) == str(tmp_path.resolve())
