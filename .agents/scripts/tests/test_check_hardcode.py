"""check-hardcode.py 单元测试。"""

import importlib.util
import sys
import tempfile
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

_spec = importlib.util.spec_from_file_location(
    "check_hardcode", SCRIPTS_DIR / "check-hardcode.py"
)
hc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hc)


def _write_py(content: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8")
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


class TestUrlDetection:
    def test_hardcoded_external_url_detected(self):
        code = 'API_URL = "https://api.example.com/v1/users"\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            cats = [i.category for i in report.issues]
            assert "HARD-URL" in cats
        finally:
            f.unlink()

    def test_localhost_url_skipped(self):
        code = 'TEST_URL = "http://localhost:8000/api/test"\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            cats = [i.category for i in report.issues]
            assert "HARD-URL" not in cats
        finally:
            f.unlink()

    def test_url_scheme_prefix_not_detected(self):
        code = 'prefix = "https://"\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            cats = [i.category for i in report.issues]
            assert "HARD-URL" not in cats
        finally:
            f.unlink()

    def test_127_url_skipped(self):
        code = 'URL = "http://127.0.0.1:5000"\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            cats = [i.category for i in report.issues]
            assert "HARD-URL" not in cats
        finally:
            f.unlink()

    def test_test_hostname_url_skipped(self):
        code = 'HA_URL = "http://test:8123"\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            cats = [i.category for i in report.issues]
            assert "HARD-URL" not in cats
        finally:
            f.unlink()

    def test_no_duplicate_url_report(self):
        code = 'FORUM_URL = "https://forum.example.com/api"\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            url_issues = [i for i in report.issues if i.category == "HARD-URL"]
            assert len(url_issues) <= 1
        finally:
            f.unlink()


class TestPathDetection:
    def test_hardcoded_absolute_path_detected(self):
        code = 'CONFIG = "/etc/app/config.yaml"\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            cats = [i.category for i in report.issues]
            assert "HARD-PATH" in cats
        finally:
            f.unlink()

    def test_relative_path_dot_prefix_skipped(self):
        code = 'TEMPLATE = "./templates/email.html"\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            cats = [i.category for i in report.issues]
            assert "HARD-PATH" not in cats
        finally:
            f.unlink()

    def test_project_relative_path_not_error(self):
        code = 'DOCS = "docs/knowledge/architecture.md"\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            path_errors = [i for i in report.issues if i.category == "HARD-PATH" and i.severity == "error"]
            assert len(path_errors) == 0
        finally:
            f.unlink()

    def test_user_agent_string_skipped(self):
        code = 'headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            path_issues = [i for i in report.issues if i.category == "HARD-PATH"]
            assert len(path_issues) == 0
        finally:
            f.unlink()

    def test_windows_absolute_path_detected(self):
        code = 'DATA = "C:\\\\Users\\\\admin\\\\data.csv"\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            cats = [i.category for i in report.issues]
            assert "HARD-PATH" in cats
        finally:
            f.unlink()


class TestChineseStringDetection:
    def test_raise_chinese_message_detected(self):
        code = 'raise ValueError("配置文件格式不正确")\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            cats = [i.category for i in report.issues]
            assert "HARD-STR" in cats
        finally:
            f.unlink()

    def test_docstring_chinese_skipped(self):
        code = '"""模块文档字符串。这是中文描述。"""\n\ndef foo():\n    pass\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            str_issues = [i for i in report.issues if i.category == "HARD-STR" and i.line == 1]
            assert len(str_issues) == 0
        finally:
            f.unlink()

    def test_test_function_chinese_skipped(self):
        code = 'def test_foo():\n    msg = "中文测试消息"\n    assert msg\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            str_issues = [i for i in report.issues if i.category == "HARD-STR"]
            assert len(str_issues) == 0
        finally:
            f.unlink()


class TestConfigParamDetection:
    def test_timeout_hardcoded_detected(self):
        code = 'response = requests.get(url, timeout=30)\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            cats = [i.category for i in report.issues]
            assert "HARD-CFG" in cats
        finally:
            f.unlink()

    def test_sentinel_zero_skipped(self):
        code = 'val = 0\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            cfg_issues = [i for i in report.issues if i.category == "HARD-CFG"]
            assert len(cfg_issues) == 0
        finally:
            f.unlink()

    def test_http_status_code_skipped(self):
        code = 'if resp.status_code == 404:\n    return None\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            num_issues = [i for i in report.issues if i.category == "HARD-NUM"]
            assert len(num_issues) == 0
        finally:
            f.unlink()


class TestEncodingDetection:
    def test_nonstandard_encoding_detected_as_warn(self):
        code = 'content = data.decode("gbk")\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            enc_issues = [i for i in report.issues if i.category == "HARD-ENC"]
            assert len(enc_issues) == 1
            assert enc_issues[0].severity == "warn"
        finally:
            f.unlink()

    def test_utf8_standard_encoding_skipped(self):
        code = 'content = data.encode("utf-8")\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            enc_issues = [i for i in report.issues if i.category == "HARD-ENC"]
            assert len(enc_issues) == 0
        finally:
            f.unlink()

    def test_mime_type_detected(self):
        code = 'header = {"Content-Type": "application/json"}\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            enc_issues = [i for i in report.issues if i.category == "HARD-ENC"]
            assert len(enc_issues) >= 1
        finally:
            f.unlink()


class TestCleanFile:
    def test_clean_code_no_issues(self):
        code = (
            '"""Clean module."""\n'
            'import os\n'
            'from config import API_BASE_URL, HTTP_TIMEOUT\n'
            'def fetch():\n'
            '    url = f"{API_BASE_URL}/v1/data"\n'
            '    return requests.get(url, timeout=HTTP_TIMEOUT)\n'
        )
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            errors = [i for i in report.issues if i.severity == "error"]
            assert len(errors) == 0
        finally:
            f.unlink()

    def test_syntax_error_handled(self):
        code = 'def foo(\n'
        f = _write_py(code)
        try:
            report = hc.scan_python_file(f, f.parent)
            parse_issues = [i for i in report.issues if i.category == "parse-error"]
            assert len(parse_issues) == 1
        finally:
            f.unlink()
