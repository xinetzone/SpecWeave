"""Supabase Storage 接入测试（AC-6）。"""

import pytest

from admin_console.config import Config
from admin_console.storage import Storage, StorageError, sanitize_filename, sanitize_object_path

from conftest import FakeResponse


def test_sanitize_filename_strips_traversal():
    assert sanitize_filename("../../etc/passwd") == "passwd"
    assert sanitize_filename("a\\b\\c.png") == "c.png"
    assert sanitize_filename("") == "file"
    assert sanitize_filename("报告 2026.pdf") == "报告_2026.pdf"


def test_sanitize_object_path_removes_dot_segments():
    assert ".." not in sanitize_object_path("../../etc/passwd")
    assert sanitize_object_path("uploads/2026/10/a.png") == "uploads/2026/10/a.png"
    assert sanitize_object_path("///") == ""


def test_upload_rejects_oversized():
    cfg = Config(supabase_url="", supabase_service_role_key="", max_upload_bytes=1024)
    with pytest.raises(StorageError) as exc:
        Storage(cfg).upload("big.png", "image/png", b"x" * 2048)
    assert exc.value.status == 413


def test_upload_rejects_unsupported_type():
    cfg = Config(supabase_url="", supabase_service_role_key="")
    with pytest.raises(StorageError) as exc:
        Storage(cfg).upload("x.exe", "application/x-msdownload", b"MZ")
    assert exc.value.status == 415


def test_upload_rejects_empty():
    cfg = Config(supabase_url="", supabase_service_role_key="")
    with pytest.raises(StorageError):
        Storage(cfg).upload("empty.png", "image/png", b"")


def test_upload_degrades_without_cloud():
    cfg = Config(supabase_url="", supabase_service_role_key="")
    result = Storage(cfg).upload("photo.png", "image/png", b"\x89PNG")
    assert result["degraded"] is True
    assert result["url"].startswith("memory://")


def test_upload_uses_service_role_header_only_server_side(http):
    cfg = Config(supabase_url="https://demo.supabase.co", supabase_service_role_key="service-key")
    http.set_response(FakeResponse(200, b'{"Key":"uploads/2026/10/x.png"}'))
    result = Storage(cfg).upload("photo.png", "image/png", b"\x89PNG")
    assert result["degraded"] is False
    assert "service-key" in http.calls[0]["headers"].get("Authorization", "")
    assert "/storage/v1/object/ac-uploads/" in http.last_url()


def test_delete_ignores_missing_object(http):
    cfg = Config(supabase_url="https://demo.supabase.co", supabase_service_role_key="service-key")
    http.set_response(FakeResponse(404, b""))
    assert Storage(cfg).delete("uploads/2026/10/x.png") is True


def test_public_url_built_from_bucket():
    cfg = Config(supabase_url="https://demo.supabase.co", supabase_service_role_key="k")
    url = Storage(cfg).public_url("uploads/2026/10/a.png")
    assert url.endswith("/storage/v1/object/public/ac-uploads/uploads/2026/10/a.png")
