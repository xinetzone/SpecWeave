"""FR-15 启动配置体检与「密钥不入日志」断言。

覆盖：报告结构（纯布尔/枚举/计数/路径）、功能开关随配置翻转、上传后端就绪判定、
管理员白名单只报数量、单行日志格式，以及 serve() 启动时确实输出体检行——
并以显式凭据常量做机械的泄露断言（报告与日志文本均不得出现任何凭据值）。
"""

import json
import logging
import socket

from doocs_md_py.server.app import serve
from doocs_md_py.server.config import Config
from doocs_md_py.server.config_report import (
    LOGGER_NAME,
    build_config_report,
    format_config_report,
    log_config_report,
)

# 显式凭据常量：任何一条出现在日志/报告中即为泄露
JWT_SECRET = "JWT-SECRET-MUST-NOT-LEAK-9f3a"  # nosec canary 常量（断言日志不泄漏），非真实凭据
OAUTH_CLIENT_SECRET = "OAUTH-SECRET-MUST-NOT-LEAK-1b7c"  # nosec canary 常量（断言日志不泄漏），非真实凭据
OAUTH_CLIENT_ID = "OAUTH-CLIENT-ID-MUST-NOT-LEAK-0a1b"
AFDIAN_TOKEN = "AFDIAN-TOKEN-MUST-NOT-LEAK-2c8d"
AFDIAN_WEBHOOK_TOKEN = "WEBHOOK-TOKEN-MUST-NOT-LEAK-6a2b"
GITHUB_PAT = "GHPAT-MUST-NOT-LEAK-3d9e"
S3_ACCESS_KEY_ID = "S3-KEY-ID-MUST-NOT-LEAK-5f1a"
S3_ACCESS_KEY_SECRET = "S3-SECRET-MUST-NOT-LEAK-4e0f"  # nosec canary 常量（断言日志不泄漏），非真实凭据

SECRETS = (
    JWT_SECRET,
    OAUTH_CLIENT_SECRET,
    OAUTH_CLIENT_ID,
    AFDIAN_TOKEN,
    AFDIAN_WEBHOOK_TOKEN,
    GITHUB_PAT,
    S3_ACCESS_KEY_ID,
    S3_ACCESS_KEY_SECRET,
)


def _full_config(tmp_path, **overrides) -> Config:
    """凭据齐备的配置（不落盘，仅内存对象）。"""
    return Config(
        app_url="https://md.example.com",
        jwt_secret=JWT_SECRET,
        admin_github_logins=("Octocat", "Admin-2"),
        github_client_id=OAUTH_CLIENT_ID,
        github_client_secret=OAUTH_CLIENT_SECRET,
        afdian_user_id="afdian-user",
        afdian_api_token=AFDIAN_TOKEN,
        afdian_webhook_token=AFDIAN_WEBHOOK_TOKEN,
        upload_backend="s3",
        upload_github_tokens=(GITHUB_PAT,),
        upload_s3_bucket="bucket",
        upload_s3_access_key_id=S3_ACCESS_KEY_ID,
        upload_s3_secret_access_key=S3_ACCESS_KEY_SECRET,
        upload_s3_public_url="https://cdn.example.com",
        sqlite_path=str(tmp_path / "db.sqlite"),
        storage_local_dir=str(tmp_path / "uploads"),
        **overrides,
    )


def _assert_no_secrets(text: str) -> None:
    for secret in SECRETS:
        assert secret not in text, f"泄露凭据：{secret}"


def _noop_runner(app, host: str, port: int) -> None:
    return None


def _make_dist(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<!DOCTYPE html><html><body>hi</body></html>", encoding="utf-8")
    return dist


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


# ---- 报告结构 ----


def test_report_is_flat_and_credential_free(tmp_path):
    config = _full_config(tmp_path)
    report = build_config_report(config)

    assert report["oauth"] is True
    assert report["jwt"] is True
    assert report["afdian"] is True
    assert report["upload"] == {"enabled": True, "backend": "s3", "ready": True}
    assert report["emoji"] == {"backend": "local"}
    assert report["adminLogins"] == 2
    assert report["storage"] == {
        "sqlite": str(tmp_path / "db.sqlite"),
        "localDir": str(tmp_path / "uploads"),
    }
    # 报告可 JSON 序列化，且任何叶子值都不是凭据
    serialized = json.dumps(report, ensure_ascii=False)
    _assert_no_secrets(serialized)


def test_report_all_disabled_for_default_config(tmp_path):
    config = Config(jwt_secret="", sqlite_path=str(tmp_path / "db.sqlite"))
    report = build_config_report(config)

    assert report["oauth"] is False
    assert report["jwt"] is False
    assert report["afdian"] is False
    # 默认 local 后端零配置恒就绪
    assert report["upload"] == {"enabled": True, "backend": "local", "ready": True}
    assert report["adminLogins"] == 0


def test_upload_switch_and_backend_readiness(tmp_path):
    disabled = Config(
        upload_enabled=False,
        upload_backend="s3",
        upload_s3_bucket="bucket",
        upload_s3_access_key_id=S3_ACCESS_KEY_ID,
        upload_s3_secret_access_key=S3_ACCESS_KEY_SECRET,
    )
    report = build_config_report(disabled)
    assert report["upload"]["enabled"] is False
    assert report["upload"]["backend"] == "s3"
    assert report["upload"]["ready"] is True

    # s3 缺凭证 → 未就绪；未知后端名归一化为 local
    missing_creds = Config(
        upload_backend="s3", upload_s3_bucket="bucket", upload_s3_public_url="https://x"
    )
    assert build_config_report(missing_creds)["upload"]["ready"] is False
    unknown = Config(upload_backend="oss")
    assert build_config_report(unknown)["upload"]["backend"] == "local"


def test_admin_logins_reports_count_only(tmp_path):
    config = _full_config(tmp_path)
    text = format_config_report(build_config_report(config))

    assert "admin=2" in text
    assert "Octocat" not in text
    assert "Admin-2" not in text


# ---- 日志文本 ----


def test_format_is_single_line_with_switches(tmp_path):
    text = format_config_report(build_config_report(_full_config(tmp_path)))

    assert "\n" not in text
    assert "oauth=on" in text
    assert "jwt=on" in text
    assert "afdian=on" in text
    assert "upload=s3 enabled=on ready=on" in text
    assert f"sqlite={tmp_path / 'db.sqlite'}" in text
    _assert_no_secrets(text)


def test_log_config_report_returns_report_and_logs_without_secrets(tmp_path, caplog):
    config = _full_config(tmp_path)

    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        report = log_config_report(config)

    assert report == build_config_report(config)
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.name == LOGGER_NAME
    assert record.getMessage().startswith("启动配置体检：")
    _assert_no_secrets(record.getMessage())
    _assert_no_secrets(caplog.text)


def test_log_config_report_accepts_injected_logger(tmp_path):
    captured: list[str] = []

    class _Spy(logging.Logger):
        def info(self, msg, *args, **kwargs):  # type: ignore[override]
            captured.append(msg % args)
            return None

    spy = _Spy("spy")
    log_config_report(_full_config(tmp_path), spy)

    assert len(captured) == 1
    _assert_no_secrets(captured[0])


# ---- serve() 接线 ----


def test_serve_emits_config_report_and_leaks_nothing(tmp_path, caplog):
    config = _full_config(tmp_path)

    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        assert serve(port=_free_port(), config=config, web_dist=_make_dist(tmp_path), runner=_noop_runner) == 0

    lines = [record.getMessage() for record in caplog.records if record.name == LOGGER_NAME]
    assert len(lines) == 1
    assert lines[0].startswith("启动配置体检：")
    assert "jwt=on" in lines[0]
    _assert_no_secrets(caplog.text)
