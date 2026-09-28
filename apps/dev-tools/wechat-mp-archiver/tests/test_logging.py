"""凭证脱敏日志测试。"""

import logging

from mp_archiver.logging_utils import RedactingFormatter, configure_logging, redact


def test_redact_query_string_secrets():
    raw = "GET /api?token=abc123secret&key=456&biz=MzA%3D%3D"
    out = redact(raw)
    assert "abc123secret" not in out
    assert "456" not in out
    assert "biz=MzA" in out  # 非敏感参数保留


def test_redact_pass_ticket_and_cookie():
    raw = "cookie: sessionid=deadbeef; pass_ticket=TICKET-XYZ-999"
    out = redact(raw)
    assert "deadbeef" not in out
    assert "TICKET-XYZ-999" not in out


def test_redact_bearer_header():
    raw = "Authorization: Bearer eyJhbGciOi.JzdWIiOiJhZG1pbiJ9.signature"
    out = redact(raw)
    assert "eyJhbGciOi" not in out


def test_redact_none_safe():
    assert redact(None) == ""


def test_formatter_redacts_record():
    record = logging.LogRecord(
        name="t", level=logging.INFO, pathname=__file__, lineno=1,
        msg="login with token=%s password: %s",
        args=("PLAINTEXT-TOKEN", "hunter2"), exc_info=None,
    )
    out = RedactingFormatter("%(message)s").format(record)
    assert "PLAINTEXT-TOKEN" not in out
    assert "hunter2" not in out


def test_configure_logging_idempotent():
    logger = configure_logging("INFO")
    before = len(logger.handlers)
    configure_logging("WARNING")
    assert len(logger.handlers) == before
    assert logger.level == logging.WARNING
