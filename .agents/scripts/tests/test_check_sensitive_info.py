"""check-sensitive-info 单元测试。"""

import sys
import tempfile
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.checks.sensitive_info import (
    PHONE, EMAIL, PERSONAL_PATH_WIN, PERSONAL_PATH_UNIX,
    INTERNAL_IP, API_KEY, PASSWORD, DB_CONN, PRIVATE_KEY,
    SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW,
    Finding, scan_file, scan_directory, fix_file,
    SUPPORTED_EXTENSIONS, DEFAULT_EXCLUDE_DIRS, FILE_EXCLUDE_PATTERNS,
)


def _write_temp_file(content: str, suffix: str = ".py") -> Path:
    """创建临时测试文件。"""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, delete=False, encoding="utf-8"
    )
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


class TestPhoneDetection:
    """手机号检测测试。"""

    def test_real_phone_detected(self):
        """真实手机号应被检测到。"""
        content = "联系电话：" + "138" + "1234" + "5678" + "\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            types = [i.type for i in findings]
            assert PHONE in types
        finally:
            f.unlink()

    def test_masked_phone_skipped(self):
        """已脱敏手机号不应检测。"""
        content = "phone: 138****5678\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            phone_findings = [i for i in findings if i.type == PHONE]
            assert len(phone_findings) == 0
        finally:
            f.unlink()

    def test_phone_in_backticks_skipped(self):
        """反引号代码块内的手机号不应检测。"""
        content = "`" + "138" + "1234" + "5678" + "`\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            phone_findings = [i for i in findings if i.type == PHONE]
            assert len(phone_findings) == 0
        finally:
            f.unlink()

    def test_phone_fix_works(self):
        """手机号修复验证：中间4位变****。"""
        content = "联系电话：" + "138" + "1234" + "5678" + "\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            fixed_count = fix_file(f, findings)
            assert fixed_count >= 1
            fixed_content = f.read_text(encoding="utf-8")
            assert "138****5678" in fixed_content
            assert ("138" + "1234" + "5678") not in fixed_content
        finally:
            f.unlink()


class TestEmailDetection:
    """邮箱检测测试。"""

    def test_real_email_detected(self):
        """真实邮箱应被检测到。"""
        content = "联系我：" + "zhangsan" + "@" + "company.com" + "\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            types = [i.type for i in findings]
            assert EMAIL in types
        finally:
            f.unlink()

    def test_example_email_skipped(self):
        """example.com 测试邮箱不应检测。"""
        content = "user" + "@" + "example.com\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            email_findings = [i for i in findings if i.type == EMAIL]
            assert len(email_findings) == 0
        finally:
            f.unlink()

    def test_test_email_skipped(self):
        """test.com 测试邮箱不应检测。"""
        content = "admin" + "@" + "test.com\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            email_findings = [i for i in findings if i.type == EMAIL]
            assert len(email_findings) == 0
        finally:
            f.unlink()

    def test_email_fix_works(self):
        """邮箱修复验证：首字符+***+尾字符格式。"""
        content = "邮箱：" + "zhangsan" + "@" + "company.com" + "\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            fixed_count = fix_file(f, findings)
            assert fixed_count >= 1
            fixed_content = f.read_text(encoding="utf-8")
            assert ("z***n@" + "company.com") in fixed_content
            assert ("zhangsan" + "@" + "company.com") not in fixed_content
        finally:
            f.unlink()

    def test_short_email_skipped(self):
        """用户名<2位的极简邮箱（a@b.com）不应检测。"""
        content = "test: a@b.com\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            email_findings = [i for i in findings if i.type == EMAIL]
            assert len(email_findings) == 0
        finally:
            f.unlink()

    def test_git_ssh_skipped(self):
        """Git SSH地址（git@github.com）不应检测。"""
        content = "git remote: git@github.com:user/repo.git\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            email_findings = [i for i in findings if i.type == EMAIL]
            assert len(email_findings) == 0
        finally:
            f.unlink()

    def test_systemd_service_skipped(self):
        """包含systemd单元后缀的不应检测。"""
        content = "podman-kube@.service.in\n"
        f = _write_temp_file(content, suffix=".txt")
        try:
            findings = scan_file(f)
            email_findings = [i for i in findings if i.type == EMAIL]
            assert len(email_findings) == 0
        finally:
            f.unlink()

    def test_public_role_email_low_severity(self):
        """公开企业角色邮箱（support@）应降为LOW风险。"""
        content = "contact: support@minitap.ai\n"  # nosec
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            email_findings = [i for i in findings if i.type == EMAIL]
            assert len(email_findings) == 1
            assert email_findings[0].severity == SEVERITY_LOW
        finally:
            f.unlink()

    def test_public_role_email_not_fixable(self):
        """公开企业角色邮箱（support@等）不应自动脱敏（fixable=False）。"""
        test_cases = [
            "support" + "@" + "minitap.ai",
            "info" + "@" + "company.com",
            "admin" + "@" + "corporation.org",
            "contact" + "@" + "business.com",
            "hello" + "@" + "startup.io",
            "sales" + "@" + "enterprise.com",
            "help" + "@" + "support.net",
        ]
        for email in test_cases:
            content = f"contact: {email}\n"
            f = _write_temp_file(content, suffix=".md")
            try:
                findings = scan_file(f)
                email_findings = [i for i in findings if i.type == EMAIL]
                assert len(email_findings) == 1, f"{email} should be detected"
                assert email_findings[0].fixable is False, f"{email} should NOT be fixable (public role email)"
            finally:
                f.unlink()

    def test_complex_package_name_skipped(self):
        """包含超过2个连字符的复杂包名不应检测。"""
        content = "other-daocollective-daoapps-podman@packages.example.com\n"
        f = _write_temp_file(content, suffix=".txt")
        try:
            findings = scan_file(f)
            email_findings = [i for i in findings if i.type == EMAIL]
            assert len(email_findings) == 0
        finally:
            f.unlink()

    def test_placeholder_email_skipped(self):
        """占位符邮箱（xxx/test/example）不应检测。"""
        test_cases = [
            "xxx@company.com",
            "test@company.com",
            "john.doe@example.com",
        ]
        for content in test_cases:
            f = _write_temp_file(content + "\n", suffix=".txt")
            try:
                findings = scan_file(f)
                email_findings = [i for i in findings if i.type == EMAIL]
                assert len(email_findings) == 0, f"{content} should be skipped"
            finally:
                f.unlink()


class TestWindowsPathDetection:
    """Windows个人路径检测测试。"""

    def test_win_path_detected(self):
        """Windows用户目录路径应被检测到。"""
        content = "C:" + "\\Users\\" + "zhangsan" + "\\Documents\n"
        f = _write_temp_file(content, suffix=".txt")
        try:
            findings = scan_file(f)
            types = [i.type for i in findings]
            assert PERSONAL_PATH_WIN in types
        finally:
            f.unlink()

    def test_system_user_path_skipped(self):
        """系统用户目录（public）不应检测。"""
        content = "C:\\Users\\public\\Documents\n"
        f = _write_temp_file(content, suffix=".txt")
        try:
            findings = scan_file(f)
            path_findings = [i for i in findings if i.type == PERSONAL_PATH_WIN]
            assert len(path_findings) == 0
        finally:
            f.unlink()

    def test_win_path_fix_works(self):
        """Windows路径修复验证：替换为<USER_HOME>\\。"""
        content = "config = C:" + "\\Users\\" + "zhangsan" + "\\.config\n"
        f = _write_temp_file(content, suffix=".txt")
        try:
            findings = scan_file(f)
            fixed_count = fix_file(f, findings)
            assert fixed_count >= 1
            fixed_content = f.read_text(encoding="utf-8")
            assert "<USER_HOME>\\" in fixed_content
            assert "zhangsan" not in fixed_content
        finally:
            f.unlink()

    def test_generic_win_users_skipped(self):
        """通用Windows用户名（user/admin/xxx/test/demo等）不应检测。"""
        generic_users = ["user", "admin", "xxx", "test", "demo", "shared", "Guest"]
        for username in generic_users:
            content = f"C:\\Users\\{username}\\Documents\n"
            f = _write_temp_file(content, suffix=".txt")
            try:
                findings = scan_file(f)
                path_findings = [i for i in findings if i.type == PERSONAL_PATH_WIN]
                assert len(path_findings) == 0, f"C:\\Users\\{username}\\ should be skipped"
            finally:
                f.unlink()

    def test_real_username_xinzo_detected(self):
        """真实用户名C:\\Users\\xinzo\\应被检测到。"""
        content = "C:" + "\\Users\\" + "xinzo" + "\\Documents\n"
        f = _write_temp_file(content, suffix=".txt")
        try:
            findings = scan_file(f)
            path_findings = [i for i in findings if i.type == PERSONAL_PATH_WIN]
            assert len(path_findings) == 1
        finally:
            f.unlink()

    def test_markdown_path_dots_skipped(self):
        """Markdown省略号路径（C:\\Users\\...）不应检测。"""
        content = "C:\\Users\\...\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            path_findings = [i for i in findings if i.type == PERSONAL_PATH_WIN]
            assert len(path_findings) == 0
        finally:
            f.unlink()

    def test_path_in_code_block_with_example_comment_detected(self):
        """代码块中包含"示例"注释的个人路径仍应被检测（非上下文敏感类型）。"""
        content = "```powershell\n# 输出示例：C:\\Users\\realuser\\AppData\\Roaming\\npm\n```\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            path_findings = [i for i in findings if i.type == PERSONAL_PATH_WIN]
            assert len(path_findings) == 1
            assert "realuser" in path_findings[0].match
        finally:
            f.unlink()


class TestUnixPathDetection:
    """Unix个人路径检测测试。"""

    def test_unix_home_path_detected(self):
        """/home/ 目录路径应被检测到。"""
        content = "/home" + "/" + "zhangsan" + "/project\n"
        f = _write_temp_file(content, suffix=".sh")
        try:
            findings = scan_file(f)
            types = [i.type for i in findings]
            assert PERSONAL_PATH_UNIX in types
        finally:
            f.unlink()

    def test_unix_users_path_detected(self):
        """/Users/ 目录路径应被检测到（macOS）。"""
        content = "/Users" + "/" + "zhangsan" + "/project\n"
        f = _write_temp_file(content, suffix=".sh")
        try:
            findings = scan_file(f)
            types = [i.type for i in findings]
            assert PERSONAL_PATH_UNIX in types
        finally:
            f.unlink()

    def test_unix_path_fix_works(self):
        """Unix路径修复验证：替换为 ~/。"""
        content = "cd /home" + "/" + "zhangsan" + "/project\n"
        f = _write_temp_file(content, suffix=".sh")
        try:
            findings = scan_file(f)
            fixed_count = fix_file(f, findings)
            assert fixed_count >= 1
            fixed_content = f.read_text(encoding="utf-8")
            assert "~/" in fixed_content
            assert "zhangsan" not in fixed_content
        finally:
            f.unlink()

    def test_generic_unix_users_skipped(self):
        """通用Unix用户名（user/admin/xxx/test/root等）不应检测。"""
        generic_users = ["user", "admin", "xxx", "test", "demo", "shared", "root"]
        for username in generic_users:
            content = f"/home/{username}/project\n"
            f = _write_temp_file(content, suffix=".sh")
            try:
                findings = scan_file(f)
                path_findings = [i for i in findings if i.type == PERSONAL_PATH_UNIX]
                assert len(path_findings) == 0, f"/home/{username}/ should be skipped"
            finally:
                f.unlink()

    def test_unix_users_admin_skipped(self):
        """/Users/admin/（macOS）不应检测。"""
        content = "/Users/admin/project\n"
        f = _write_temp_file(content, suffix=".sh")
        try:
            findings = scan_file(f)
            path_findings = [i for i in findings if i.type == PERSONAL_PATH_UNIX]
            assert len(path_findings) == 0
        finally:
            f.unlink()


class TestInternalIpDetection:
    """内网IP检测测试。"""

    def test_internal_ip_detected(self):
        """内网IP地址应被检测到。"""
        content = "服务器地址：" + "192.168" + ".1.100\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            types = [i.type for i in findings]
            assert INTERNAL_IP in types
        finally:
            f.unlink()

    def test_localhost_skipped(self):
        """127.0.0.1回环地址不应检测。"""
        content = "127.0.0.1\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            ip_findings = [i for i in findings if i.type == INTERNAL_IP]
            assert len(ip_findings) == 0
        finally:
            f.unlink()

    def test_example_context_ip_skipped(self):
        """示例上下文中的IP不应检测。"""
        content = "示例 " + "192.168" + ".1.1\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            ip_findings = [i for i in findings if i.type == INTERNAL_IP]
            assert len(ip_findings) == 0
        finally:
            f.unlink()


class TestApiKeyDetection:
    """API密钥检测测试。"""

    def test_sk_key_detected(self):
        """真实sk-开头密钥应被检测到（HIGH风险）。"""
        content = "API密钥：" + "sk-" + "1234567890abcdef1234567890abcdef" + "\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            key_findings = [i for i in findings if i.type == API_KEY]
            assert len(key_findings) == 1
            assert key_findings[0].severity == SEVERITY_HIGH
        finally:
            f.unlink()

    def test_placeholder_key_skipped(self):
        """占位符密钥不应检测。"""
        content = 'api_key = "sk-xxxx"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            key_findings = [i for i in findings if i.type == API_KEY]
            assert len(key_findings) == 0
        finally:
            f.unlink()

    def test_your_api_key_skipped(self):
        """your-api-key占位符不应检测。"""
        content = 'api_key = "your-api-key"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            key_findings = [i for i in findings if i.type == API_KEY]
            assert len(key_findings) == 0
        finally:
            f.unlink()


class TestPasswordDetection:
    """密码检测测试。"""

    def test_password_detected(self):
        """真实密码应被检测到（HIGH风险）。"""
        content = 'password = "' + "my_secret_pass123" + '"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            pwd_findings = [i for i in findings if i.type == PASSWORD]
            assert len(pwd_findings) == 1
            assert pwd_findings[0].severity == SEVERITY_HIGH
        finally:
            f.unlink()

    def test_changeme_skipped(self):
        """changeme占位密码不应检测。"""
        content = 'password = "changeme"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            pwd_findings = [i for i in findings if i.type == PASSWORD]
            assert len(pwd_findings) == 0
        finally:
            f.unlink()

    def test_xxx_password_skipped(self):
        """xxx占位密码不应检测。"""
        content = 'password = "xxx"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            pwd_findings = [i for i in findings if i.type == PASSWORD]
            assert len(pwd_findings) == 0
        finally:
            f.unlink()


class TestDbConnDetection:
    """数据库连接串检测测试。"""

    def test_mysql_conn_detected(self):
        """远程数据库连接串应被检测到（HIGH风险）。"""
        content = "mysql" + "://" + "user:pass" + "@" + "db.example.com:3306/mydb\n"
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            conn_findings = [i for i in findings if i.type == DB_CONN]
            assert len(conn_findings) == 1
            assert conn_findings[0].severity == SEVERITY_HIGH
        finally:
            f.unlink()

    def test_localhost_conn_skipped(self):
        """localhost本地连接串不应检测。"""
        content = "mysql://root@localhost:3306/test\n"
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            conn_findings = [i for i in findings if i.type == DB_CONN]
            assert len(conn_findings) == 0
        finally:
            f.unlink()


class TestPrivateKeyDetection:
    """私钥检测测试。"""

    def test_private_key_detected(self):
        """私钥头应被检测到（HIGH风险）。"""
        content = "-----BEGIN " + "RSA PRIVATE KEY-----\n"
        f = _write_temp_file(content, suffix=".txt")
        try:
            findings = scan_file(f)
            key_findings = [i for i in findings if i.type == PRIVATE_KEY]
            assert len(key_findings) == 1
            assert key_findings[0].severity == SEVERITY_HIGH
        finally:
            f.unlink()

    def test_public_key_skipped(self):
        """公钥头不应检测。"""
        content = "-----BEGIN PUBLIC KEY-----\n"
        f = _write_temp_file(content, suffix=".txt")
        try:
            findings = scan_file(f)
            key_findings = [i for i in findings if i.type == PRIVATE_KEY]
            assert len(key_findings) == 0
        finally:
            f.unlink()


class TestNosecMarker:
    """nosec 注释标记测试。"""

    def test_nosec_python_comment_skips_line(self):
        """# nosec 注释应跳过该行所有检测。"""
        content = "phone = " + '"' + "138" + "1234" + "5678" + '"  # nosec\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            assert len(findings) == 0
        finally:
            f.unlink()

    def test_sensitive_ignore_python_comment_skips_line(self):
        """# sensitive-ignore 注释应跳过该行所有检测。"""
        content = "email = " + '"' + "zhangsan" + "@" + "company.com" + '"  # sensitive-ignore\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            assert len(findings) == 0
        finally:
            f.unlink()

    def test_nosec_double_slash_skips_line(self):
        """// nosec 注释应跳过该行所有检测。"""
        content = "const key = " + '"' + "sk-" + "1234567890abcdef1234567890abcdef" + '"' + "; // nosec\n"
        f = _write_temp_file(content, suffix=".js")
        try:
            findings = scan_file(f)
            assert len(findings) == 0
        finally:
            f.unlink()

    def test_nosec_block_comment_skips_line(self):
        """/* nosec */ 注释应跳过该行所有检测（JS文件）。"""
        content = "const pwd = " + '"' + "my_secret_pass123" + '"' + "; /* nosec */\n"
        f = _write_temp_file(content, suffix=".js")
        try:
            findings = scan_file(f)
            assert len(findings) == 0
        finally:
            f.unlink()

    def test_nosec_html_comment_skips_line(self):
        """<!-- nosec --> 注释应跳过该行所有检测。"""
        content = "<!-- phone: " + "138" + "1234" + "5678" + " --> <!-- nosec -->\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            assert len(findings) == 0
        finally:
            f.unlink()

    def test_nosec_case_insensitive(self):
        """nosec 不区分大小写。"""
        content = "key = " + '"' + "sk-" + "1234567890abcdef1234567890abcdef" + '"  # NOSEC\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            assert len(findings) == 0
        finally:
            f.unlink()


class TestDirectoryScan:
    """目录扫描与文件排除测试。"""

    def test_scan_directory_excludes_vendor(self, tmp_path):
        """扫描时应排除 vendor 目录。"""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        vendor_file = vendor_dir / "secret.py"
        vendor_file.write_text("# 联系电话：" + "138" + "1234" + "5678" + "\n", encoding="utf-8")

        normal_file = tmp_path / "normal.py"
        normal_file.write_text("# 联系电话：" + "138" + "1234" + "5678" + "\n", encoding="utf-8")

        findings = scan_directory(tmp_path)
        finding_files = {f.file.name for f in findings}
        assert "normal.py" in finding_files
        assert "secret.py" not in finding_files

    def test_scan_directory_excludes_temp(self, tmp_path):
        """扫描时应排除 .temp 目录。"""
        temp_dir = tmp_path / ".temp"
        temp_dir.mkdir()
        temp_file = temp_dir / "secret.py"
        temp_file.write_text("# 联系电话：" + "138" + "1234" + "5678" + "\n", encoding="utf-8")

        normal_file = tmp_path / "normal.py"
        normal_file.write_text("# 联系电话：" + "138" + "1234" + "5678" + "\n", encoding="utf-8")

        findings = scan_directory(tmp_path)
        finding_files = {f.file.name for f in findings}
        assert "normal.py" in finding_files
        assert "secret.py" not in finding_files

    def test_env_example_skipped(self, tmp_path):
        """.env.example 文件不应检测。"""
        env_file = tmp_path / ".env.example"
        env_file.write_text('API_KEY="' + "sk-real-key-1234567890abcdef" + '"\n', encoding="utf-8")

        findings = scan_file(env_file)
        assert len(findings) == 0

    def test_supported_extensions_only(self, tmp_path):
        """二进制文件/不支持的扩展名不应扫描。"""
        bin_file = tmp_path / "test.bin"
        bin_file.write_bytes(b'\x00\x01\x02\x03phone' + b'138' + b'1234' + b'5678')

        findings = scan_file(bin_file)
        assert len(findings) == 0


class TestFindingDataclass:
    """Finding 数据类测试。"""

    def test_finding_attributes(self):
        """验证 Finding 属性正确。"""
        test_file = Path("/test/file.py")
        finding = Finding(
            file=test_file,
            line=10,
            col=5,
            type=PHONE,
            severity=SEVERITY_HIGH,
            match="138" + "1234" + "5678",
            rule_name="中国大陆手机号",
            suggestion="测试建议",
            fixable=True,
        )
        assert finding.file == test_file
        assert finding.line == 10
        assert finding.col == 5
        assert finding.type == PHONE
        assert finding.severity == SEVERITY_HIGH
        assert finding.match == "138" + "1234" + "5678"
        assert finding.rule_name == "中国大陆手机号"
        assert finding.suggestion == "测试建议"
        assert finding.fixable is True

    def test_fixable_flag(self):
        """验证PHONE/EMAIL/PATH类是fixable，高风险类型不可修复。"""
        fixable_types = {PHONE, EMAIL, PERSONAL_PATH_WIN, PERSONAL_PATH_UNIX}
        non_fixable_types = {API_KEY, PASSWORD, DB_CONN, PRIVATE_KEY, INTERNAL_IP}

        phone_num = "138" + "1234" + "5678"
        email_user = "zhangsan"
        email_domain = "company.com"
        win_user = "zhangsan"
        unix_user = "zhangsan"
        sk_val = "sk-" + "1234567890abcdef1234567890abcdef"
        pwd_val = "secret123"
        db_scheme = "mysql" + "://"
        db_auth = "u:p"
        db_host = "db:3306/db"
        priv_key_p1 = "-----BEGIN "
        priv_key_p2 = "RSA PRIVATE KEY-----"
        ip_val = "192.168" + ".1.1"

        content_lines = [
            "电话：" + phone_num,
            "邮箱：" + email_user + "@" + email_domain,
            "winpath: C:" + "\\Users\\" + win_user + "\\Documents\\",
            "unixpath: /home" + "/" + unix_user + "/project/",
            "密钥：" + sk_val,
            'password = "' + pwd_val + '"',
            db_scheme + db_auth + "@" + db_host,
            priv_key_p1 + priv_key_p2,
            "服务器：" + ip_val,
        ]
        content = "\n".join(content_lines) + "\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            findings_by_type = {f.type: f for f in findings}

            for t in fixable_types:
                assert t in findings_by_type, f"{t} should be detected, got {list(findings_by_type.keys())}"
                assert findings_by_type[t].fixable is True, f"{t} should be fixable"

            for t in non_fixable_types:
                if t in findings_by_type:
                    assert findings_by_type[t].fixable is False, f"{t} should not be fixable"
        finally:
            f.unlink()
