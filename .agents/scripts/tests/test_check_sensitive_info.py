"""check-sensitive-info 单元测试。"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

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
    _is_public_doc_file, DOC_PERSONAL_PATH_SUGGESTION,
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
        content = "联系我：" + "realuser" + "@" + "company.com" + "\n"
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

    def test_rfc2606_subdomain_email_skipped(self):
        """RFC 2606 保留域子域（proxy.example.com）邮箱不应检测。"""
        content = "proxy_user = " + '"' + "password@proxy.example.com" + '"' + "\n"
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            email_findings = [i for i in findings if i.type == EMAIL]
            assert len(email_findings) == 0
        finally:
            f.unlink()

    def test_ofl_license_attribution_email_skipped(self):
        """SIL OFL 许可证版权声明中的署名邮箱不应检测（法定公开署名）。"""
        content = (
            "Copyright (c) 2011, Denis Masharov (denis.masharov" + "@" + "gmail.com)\n"
            "\n"
            "This Font Software is licensed under the SIL Open Font License, Version 1.1.\n"
        )
        f = _write_temp_file(content, suffix=".txt")
        try:
            findings = scan_file(f)
            email_findings = [i for i in findings if i.type == EMAIL]
            assert len(email_findings) == 0
        finally:
            f.unlink()

    def test_email_fix_works(self):
        """邮箱修复验证：首字符+***+尾字符格式。"""
        content = "邮箱：" + "realuser" + "@" + "company.com" + "\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            fixed_count = fix_file(f, findings)
            assert fixed_count >= 1
            fixed_content = f.read_text(encoding="utf-8")
            assert ("r***r@" + "company.com") in fixed_content
            assert ("realuser" + "@" + "company.com") not in fixed_content
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
        content = "C:" + "\\Users\\" + "realuser" + "\\Documents\n"
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
        content = "config = C:" + "\\Users\\" + "realuser" + "\\.config\n"
        f = _write_temp_file(content, suffix=".txt")
        try:
            findings = scan_file(f)
            fixed_count = fix_file(f, findings)
            assert fixed_count >= 1
            fixed_content = f.read_text(encoding="utf-8")
            assert "<USER_HOME>\\" in fixed_content
            assert "realuser" not in fixed_content
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

    def test_env_var_placeholder_win_user_skipped(self):
        """%USERNAME% 环境变量占位（文档通用示例）不应检测。"""
        content = "C:" + "\\Users\\" + "%USERNAME%" + "\\AppData\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            path_findings = [i for i in findings if i.type == PERSONAL_PATH_WIN]
            assert len(path_findings) == 0
        finally:
            f.unlink()

    def test_devuser_win_path_skipped(self):
        """devuser（Windows 容器镜像固定账户，与 Unix 侧对称）不应检测。"""
        content = "C:" + "\\Users\\" + "devuser" + "\\workspace\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            path_findings = [i for i in findings if i.type == PERSONAL_PATH_WIN]
            assert len(path_findings) == 0
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
        content = "/home" + "/" + "realuser" + "/project\n"
        f = _write_temp_file(content, suffix=".sh")
        try:
            findings = scan_file(f)
            types = [i.type for i in findings]
            assert PERSONAL_PATH_UNIX in types
        finally:
            f.unlink()

    def test_unix_users_path_detected(self):
        """/Users/ 目录路径应被检测到（macOS）。"""
        content = "/Users" + "/" + "realuser" + "/project\n"
        f = _write_temp_file(content, suffix=".sh")
        try:
            findings = scan_file(f)
            types = [i.type for i in findings]
            assert PERSONAL_PATH_UNIX in types
        finally:
            f.unlink()

    def test_unix_path_fix_works(self):
        """Unix路径修复验证：替换为 ~/。"""
        content = "cd /home" + "/" + "realuser" + "/project\n"
        f = _write_temp_file(content, suffix=".sh")
        try:
            findings = scan_file(f)
            fixed_count = fix_file(f, findings)
            assert fixed_count >= 1
            fixed_content = f.read_text(encoding="utf-8")
            assert "~/" in fixed_content
            assert "realuser" not in fixed_content
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

    def test_chinese_placeholder_unix_user_skipped(self):
        """/Users/你的用户名/（中文文档占位，与 Win 侧对称）不应检测。"""
        content = "/Users/" + "你的用户名" + "/project\n"
        f = _write_temp_file(content, suffix=".md")
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

    def test_canonical_doc_example_ips_skipped(self):
        """网络文档通用示例 IP（网络地址 + 示例首主机）不应检测。"""
        example_ips = ["10.0.0.0", "10.0.0.1", "10.0.0.2",
                       "192.168.0.0", "192.168.1.0", "192.168.1.1", "172.16.0.0"]
        for ip in example_ips:
            content = f"网关地址：{ip}\n"
            f = _write_temp_file(content, suffix=".md")
            try:
                findings = scan_file(f)
                ip_findings = [i for i in findings if i.type == INTERNAL_IP]
                assert len(ip_findings) == 0, f"{ip} should be skipped"
            finally:
                f.unlink()

    def test_real_internal_ip_detected(self):
        """真实内网地址（非示例形态）仍应检测。"""
        content = "服务器地址：" + "10.16" + ".11.3\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            ip_findings = [i for i in findings if i.type == INTERNAL_IP]
            assert len(ip_findings) == 1
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

    def test_uppercase_password_detected(self):
        """大写配置键（PASSWORD=）应命中——大小写不敏感（SF-036 修复）。"""
        content = 'PASSWORD = "' + "Sup3rSecretValue" + '"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            pwd_findings = [i for i in findings if i.type == PASSWORD]
            assert len(pwd_findings) == 1
            assert pwd_findings[0].severity == SEVERITY_HIGH
        finally:
            f.unlink()

    def test_capitalized_secret_detected(self):
        """首字母大写 Secret: 应命中——大小写不敏感（SF-036 修复）。"""
        content = 'Secret: "' + "a1b2c3d4e5f6" + '"\n'
        f = _write_temp_file(content, suffix=".yaml")
        try:
            findings = scan_file(f)
            pwd_findings = [i for i in findings if i.type == PASSWORD]
            assert len(pwd_findings) == 1
        finally:
            f.unlink()

    def test_literal_password_word_skipped(self):
        """「默认密码为 password」字面占位值不应检测。"""
        content = 'PASSWORD = "' + "password" + '"\n'
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
    """私钥块级检测测试（头 + base64 体，2026-10-20 头体分离改造）。"""

    # 拼接构造：源码中不出现完整 PEM 头 + 体的连续匹配串
    _KEY_HEADER = "-----BEGIN " + "RSA PRIVATE KEY-----"
    _KEY_BODY = "MIIE" + "pAIBAAKCAQEA" + "A" * 120
    # 标准多行 PEM 体（每行 64）
    _KEY_LINE = "QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVphYmNkZWZnaGlqa2xtbm9wcXJz" + "dHV2d3g="

    def test_private_key_block_detected(self):
        """PEM 头 + base64 体（单行长体）应被检测到（HIGH风险）。"""
        content = self._KEY_HEADER + "\n" + self._KEY_BODY + "\n"
        f = _write_temp_file(content, suffix=".txt")
        try:
            findings = scan_file(f)
            key_findings = [i for i in findings if i.type == PRIVATE_KEY]
            assert len(key_findings) == 1
            assert key_findings[0].severity == SEVERITY_HIGH
            # match 只存头部，不把整块密钥写进报告
            assert key_findings[0].match == self._KEY_HEADER
        finally:
            f.unlink()

    def test_private_key_multiline_block_detected(self):
        """标准多行 PEM（每行 64）应被检测到（HIGH风险）。"""
        content = (
            self._KEY_HEADER + "\n"
            + self._KEY_LINE + "\n" + self._KEY_LINE + "\n"
            + "-----END " + "RSA PRIVATE KEY-----\n"
        )
        f = _write_temp_file(content, suffix=".txt")
        try:
            findings = scan_file(f)
            key_findings = [i for i in findings if i.type == PRIVATE_KEY]
            assert len(key_findings) == 1
            assert key_findings[0].severity == SEVERITY_HIGH
        finally:
            f.unlink()

    def test_private_key_header_only_skipped(self):
        """单独提及 PEM 头（文档说明格式）不应报警——头体分离的误报根治点。"""
        content = "PEM 格式以 " + self._KEY_HEADER + " 开头，后接 base64 体。\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            key_findings = [i for i in findings if i.type == PRIVATE_KEY]
            assert len(key_findings) == 0
        finally:
            f.unlink()

    def test_private_key_header_with_prose_skipped(self):
        """PEM 头后跟英文散文（无 64 连续 base64 串）不应报警。"""
        content = (
            self._KEY_HEADER + "\n"
            + "The key body follows in base64 encoding on the subsequent lines "
            + "of this document for illustration purposes only.\n"
        )
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            key_findings = [i for i in findings if i.type == PRIVATE_KEY]
            assert len(key_findings) == 0
        finally:
            f.unlink()

    def test_private_key_header_with_fingerprint_skipped(self):
        """PEM 头后跟 40 位指纹（短跑不成段）不应报警。"""
        content = (
            self._KEY_HEADER + "\n"
            + "SHA256 fingerprint: " + "d41d8cd98f00b204e9800998ecf8427e12345678" + "\n"
        )
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            key_findings = [i for i in findings if i.type == PRIVATE_KEY]
            assert len(key_findings) == 0
        finally:
            f.unlink()

    def test_private_key_single_line_escaped_detected(self):
        """JSON/YAML 中转义为单行的私钥块（头+体同行）应被检测到。"""
        content = '{"key": "' + self._KEY_HEADER + "\\n" + self._KEY_BODY + '"}\n'
        f = _write_temp_file(content, suffix=".json")
        try:
            findings = scan_file(f)
            key_findings = [i for i in findings if i.type == PRIVATE_KEY]
            assert len(key_findings) == 1
        finally:
            f.unlink()

    def test_private_key_example_context_downgraded(self):
        """示例上下文中的私钥块降级为 MEDIUM（仍可见、不阻断）。"""
        # 与旧行级规则同口径：示例关键词须在头部所在行
        content = "示例：" + self._KEY_HEADER + "\n" + self._KEY_BODY + "\n"
        f = _write_temp_file(content, suffix=".txt")
        try:
            findings = scan_file(f)
            key_findings = [i for i in findings if i.type == PRIVATE_KEY]
            assert len(key_findings) == 1
            assert key_findings[0].severity == SEVERITY_MEDIUM
        finally:
            f.unlink()

    def test_private_key_in_example_code_block_downgraded(self):
        """示例代码块（fenced + example 关键词）内的私钥块降级为 LOW。"""
        content = (
            "# 用法示例\n\n```\n"
            + self._KEY_HEADER + "\n" + self._KEY_BODY + "\n"
            + "```\n"
        )
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            key_findings = [i for i in findings if i.type == PRIVATE_KEY]
            assert len(key_findings) == 1
            assert key_findings[0].severity == SEVERITY_LOW
        finally:
            f.unlink()

    def test_public_key_block_skipped(self):
        """公钥块（头+体）不应按私钥检测。"""
        content = "-----BEGIN " + "PUBLIC KEY-----\n" + self._KEY_BODY + "\n"
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
        content = "email = " + '"' + "realuser" + "@" + "company.com" + '"  # sensitive-ignore\n'
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

    def test_scan_directory_handles_broken_symlink(self, tmp_path):
        """扫描含断裂符号链接的目录不应崩溃（OSError 容错）。

        回归：Windows 下 vendor 内指向不存在目标的符号链接（如
        pycaffe/venv/lib64）曾导致 is_file() 抛 OSError 使全量扫描中断。
        """
        target = tmp_path / "nonexistent_target.txt"
        link = tmp_path / "broken_link.txt"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            pytest.skip("无法创建符号链接（需要权限或平台不支持）")

        normal_file = tmp_path / "normal.py"
        normal_file.write_text("# 联系电话：" + "138" + "1234" + "5678" + "\n", encoding="utf-8")

        # 不应抛异常，且正常文件仍被扫描
        findings = scan_directory(tmp_path)
        finding_files = {f.file.name for f in findings}
        assert "normal.py" in finding_files


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
        email_user = "realuser"
        email_domain = "company.com"
        win_user = "realuser"
        unix_user = "realuser"
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


class TestPublicDocsPathEscalation:
    """docs/ 对外文档目录中真实个人路径升级为 HIGH（提交阻断）。"""

    def test_win_path_in_docs_escalated_to_high(self, tmp_path):
        """docs/ 内真实 Windows 用户路径应为 HIGH。"""
        f = tmp_path / "docs" / "guide.md"
        f.parent.mkdir(parents=True)
        f.write_text("路径：" + "C:" + "\\Users\\" + "realuser" + "\\Documents\n", encoding="utf-8")
        findings = scan_file(f)
        path_findings = [i for i in findings if i.type == PERSONAL_PATH_WIN]
        assert len(path_findings) == 1
        assert path_findings[0].severity == SEVERITY_HIGH
        assert path_findings[0].suggestion == DOC_PERSONAL_PATH_SUGGESTION

    def test_unix_path_in_docs_escalated_to_high(self, tmp_path):
        """docs/ 内真实 Unix 用户路径应为 HIGH。"""
        f = tmp_path / "docs" / "guide.md"
        f.parent.mkdir(parents=True)
        f.write_text("cd /home" + "/" + "realuser" + "/project\n", encoding="utf-8")
        findings = scan_file(f)
        path_findings = [i for i in findings if i.type == PERSONAL_PATH_UNIX]
        assert len(path_findings) == 1
        assert path_findings[0].severity == SEVERITY_HIGH

    def test_wsl_mnt_path_in_docs_escalated_to_high(self, tmp_path):
        """docs/ 内 WSL 挂载形态 /mnt/c/Users/<user>/ 应为 HIGH 且归类 Win。"""
        f = tmp_path / "docs" / "wsl.md"
        f.parent.mkdir(parents=True)
        f.write_text("/mnt/c/Users/" + "realuser" + "/ai-poc/\n", encoding="utf-8")
        findings = scan_file(f)
        assert len(findings) == 1
        assert findings[0].type == PERSONAL_PATH_WIN
        assert findings[0].severity == SEVERITY_HIGH

    def test_angle_placeholder_in_docs_not_flagged(self, tmp_path):
        """docs/ 内尖括号占位路径不应检测（Windows 与 Unix 双形态）。"""
        f = tmp_path / "docs" / "guide.md"
        f.parent.mkdir(parents=True)
        f.write_text(
            "D:\\Users\\<用户名>\\anaconda3\n"
            "WORKSPACE=/home/<your-user>/specweave\n",
            encoding="utf-8",
        )
        findings = scan_file(f)
        assert not [i for i in findings if i.type in (PERSONAL_PATH_WIN, PERSONAL_PATH_UNIX)]

    def test_env_var_placeholder_in_docs_not_flagged(self, tmp_path):
        """docs/ 内 %USERPROFILE% 环境变量占位路径不应检测。"""
        f = tmp_path / "docs" / "guide.md"
        f.parent.mkdir(parents=True)
        f.write_text("%USERPROFILE%" + "\\.trae-cn\\skills\\tts\\SKILL.md\n", encoding="utf-8")
        findings = scan_file(f)
        assert not [i for i in findings if i.type in (PERSONAL_PATH_WIN, PERSONAL_PATH_UNIX)]

    def test_generic_placeholders_in_docs_not_flagged(self, tmp_path):
        """docs/ 内泛指占位用户名（me/someone/yourname）不应检测。"""
        f = tmp_path / "docs" / "guide.md"
        f.parent.mkdir(parents=True)
        f.write_text(
            "C:\\Users\\me\\sample.png\n"
            "C:\\Users\\someone\\downloads\n"
            "C:\\Users\\yourname\\.config\n",
            encoding="utf-8",
        )
        findings = scan_file(f)
        assert not [i for i in findings if i.type == PERSONAL_PATH_WIN]

    def test_unicode_ellipsis_in_docs_not_flagged(self, tmp_path):
        """docs/ 内省略号掩码 C:\\Users\\…\\ 不应检测。"""
        f = tmp_path / "docs" / "guide.md"
        f.parent.mkdir(parents=True)
        f.write_text("C:\\Users\\…\\AppData\\Local\\Temp\n", encoding="utf-8")
        findings = scan_file(f)
        assert not [i for i in findings if i.type == PERSONAL_PATH_WIN]

    def test_container_accounts_in_docs_not_flagged(self, tmp_path):
        """docs/ 内容器/CI 固定账户（devuser/runner 等）不应检测。"""
        f = tmp_path / "docs" / "container.md"
        f.parent.mkdir(parents=True)
        accounts = ["devuser", "appuser", "builder", "jupyteruser", "runner", "openkylin"]
        f.write_text("".join(f"/home/{u}/app\n" for u in accounts), encoding="utf-8")
        findings = scan_file(f)
        assert not [i for i in findings if i.type == PERSONAL_PATH_UNIX]

    def test_path_in_playground_not_escalated(self, tmp_path):
        """playground/ 私域内真实个人路径保持 MEDIUM，不升级。"""
        f = tmp_path / "playground" / "u" / "notes.md"
        f.parent.mkdir(parents=True)
        f.write_text("C:" + "\\Users\\" + "realuser" + "\\Notes\n", encoding="utf-8")
        findings = scan_file(f)
        path_findings = [i for i in findings if i.type == PERSONAL_PATH_WIN]
        assert len(path_findings) == 1
        assert path_findings[0].severity == SEVERITY_MEDIUM

    def test_path_in_vendor_docs_not_escalated(self, tmp_path):
        """vendor/ 第三方子模块内即使含 docs 段也不升级。"""
        f = tmp_path / "vendor" / "libx" / "docs" / "page.md"
        f.parent.mkdir(parents=True)
        f.write_text("/home/" + "realuser" + "/project\n", encoding="utf-8")
        findings = scan_file(f)
        path_findings = [i for i in findings if i.type == PERSONAL_PATH_UNIX]
        assert len(path_findings) == 1
        assert path_findings[0].severity == SEVERITY_MEDIUM

    def test_path_outside_docs_stays_medium(self, tmp_path):
        """docs/ 之外的真实个人路径保持 MEDIUM（脚本/配置不升级）。"""
        f = tmp_path / "scripts" / "run.ps1"
        f.parent.mkdir(parents=True)
        f.write_text("Set-Location C:" + "\\Users\\" + "realuser" + "\\work\n", encoding="utf-8")
        findings = scan_file(f)
        path_findings = [i for i in findings if i.type == PERSONAL_PATH_WIN]
        assert len(path_findings) == 1
        assert path_findings[0].severity == SEVERITY_MEDIUM

    def test_nosec_marker_in_docs_skips_escalation(self, tmp_path):
        """docs/ 内行尾 nosec 标记仍可豁免（仅限示例/测试数据的逃生口）。"""
        f = tmp_path / "docs" / "demo.md"
        f.parent.mkdir(parents=True)
        f.write_text("C:" + "\\Users\\" + "realuser" + "\\demo  # nosec\n", encoding="utf-8")
        findings = scan_file(f)
        assert len(findings) == 0

    def test_is_public_doc_file_predicate(self, tmp_path):
        """目录谓词边界：docs 命中、私域/第三方豁免、非文档不命中。"""
        assert _is_public_doc_file(tmp_path / "docs" / "a.md")
        assert _is_public_doc_file(tmp_path / "apps" / "x" / "docs" / "a.md")
        assert not _is_public_doc_file(tmp_path / "playground" / "u" / "docs" / "a.md")
        assert not _is_public_doc_file(tmp_path / "vendor" / "x" / "docs" / "a.md")
        assert not _is_public_doc_file(tmp_path / "scripts" / "a.py")
        # 子模块文档目录使用单数 doc，不命中
        assert not _is_public_doc_file(tmp_path / "projects" / "x" / "doc" / "a.md")


class TestWslMntPathDetection:
    """WSL 挂载形态 /mnt/<drive>/Users/<user>/ 检测归类与去重。"""

    def test_wsl_mnt_path_detected_as_win(self):
        """/mnt/c/Users/<user>/ 应归 personal_path_win。"""
        content = "/mnt/c/Users/" + "realuser" + "/ai-poc/\n"
        f = _write_temp_file(content, suffix=".sh")
        try:
            findings = scan_file(f)
            assert any(i.type == PERSONAL_PATH_WIN for i in findings)
        finally:
            f.unlink()

    def test_wsl_mnt_path_no_unix_duplicate(self):
        """同一 WSL 路径不得同时报 win 与 unix 两条。"""
        content = "/mnt/c/Users/" + "realuser" + "/ai-poc/\n"
        f = _write_temp_file(content, suffix=".sh")
        try:
            findings = scan_file(f)
            assert len(findings) == 1
            assert findings[0].type == PERSONAL_PATH_WIN
        finally:
            f.unlink()

    def test_wsl_mnt_fix_preserves_mount_prefix(self):
        """WSL 形态自动脱敏应保留 /mnt/c/Users 前缀。"""
        content = "/mnt/c/Users/" + "realuser" + "/ai-poc/\n"
        f = _write_temp_file(content, suffix=".sh")
        try:
            findings = scan_file(f)
            fixed_count = fix_file(f, findings)
            assert fixed_count == 1
            fixed_content = f.read_text(encoding="utf-8")
            assert "/mnt/c/Users/<USER_HOME>/" in fixed_content
            assert "realuser" not in fixed_content
        finally:
            f.unlink()

    def test_classic_drive_path_fix_unchanged(self):
        """盘符形态脱敏行为保持 <USER_HOME>\\ 不变（回归保护）。"""
        content = "C:" + "\\Users\\" + "realuser" + "\\Documents\n"
        f = _write_temp_file(content, suffix=".txt")
        try:
            findings = scan_file(f)
            fixed_count = fix_file(f, findings)
            assert fixed_count >= 1
            fixed_content = f.read_text(encoding="utf-8")
            assert "<USER_HOME>\\" in fixed_content
        finally:
            f.unlink()


class TestBuildDirExclusion:
    """文档构建产物目录 _build 应在目录扫描时排除。"""

    def test_scan_directory_excludes_build(self, tmp_path):
        """_build/ 内的文件不应扫描（与 node_modules 等构建产物同类）。"""
        build_dir = tmp_path / "docs" / "_build"
        build_dir.mkdir(parents=True)
        build_file = build_dir / "page.html.txt"
        build_file.write_text("C:" + "\\Users\\" + "realuser" + "\\file\n", encoding="utf-8")

        normal_file = tmp_path / "docs" / "page.md"
        normal_file.write_text("正常文档\n", encoding="utf-8")

        findings = scan_directory(tmp_path)
        finding_files = {f.file.name for f in findings}
        assert "page.html.txt" not in finding_files

    def test_build_in_default_excludes(self):
        """_build 应登记在默认排除集合中。"""
        assert "_build" in DEFAULT_EXCLUDE_DIRS


class TestVendorCredentialDetection:
    """供应商特定凭据检测测试（微信/腾讯云/GitHub/Slack，2026-10-19 新增）。"""

    # 检测夹具一律拼接构造：运行期值完整、源码中不出现连续匹配串，
    # 避免测试文件自身被扫描器命中（与既有手机号测试同款约定）
    FAKE_WX_ID = "wx" + "4c629ec6cd51a2d6"
    FAKE_WX_SECRET_HEX = "5f4dcc3b" + "5aa765d61d8327deb882cf99"
    FAKE_AKID = "AKID" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6"
    FAKE_GH = "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
    FAKE_SLACK = "xoxb-" + "2498137-0aBcDeFgHiJk"
    FAKE_SK = "sk-" + "abc123def456ghi789jkl012mno345"
    FAKE_SECRET_KEY = "Zp9Kq2Xm4" + "Rt7Vb1Wy8Uc3Dz6Ha5Jf0Gk"

    def test_wechat_app_id_detected(self):
        """真实形态微信 AppID 应被检测到。"""
        content = f'MP_ARCHIVER_WECHAT_APP_ID = "{self.FAKE_WX_ID}"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            assert any(i.rule_name == "微信AppID" for i in findings)
        finally:
            f.unlink()

    def test_wechat_app_id_redacted_form_skipped(self):
        """脱敏形态 wx4c62… 不应检测。"""
        content = "AppID=wx4c62…\n"
        f = _write_temp_file(content, suffix=".md")
        try:
            findings = scan_file(f)
            assert not any(i.rule_name == "微信AppID" for i in findings)
        finally:
            f.unlink()

    def test_wechat_app_id_sequential_placeholder_skipped(self):
        """顺序占位 wx0123456789abcdef 不应检测。"""
        content = 'APP_ID = "wx0123456789abcdef"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            assert not any(i.rule_name == "微信AppID" for i in findings)
        finally:
            f.unlink()

    def test_wechat_app_id_explicit_dummy_skipped(self):
        """显式无效值 wx-not-a-real-id 不应检测。"""
        content = 'APP_ID = "wx-not-a-real-id"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            assert not any(i.rule_name == "微信AppID" for i in findings)
        finally:
            f.unlink()

    def test_wechat_app_secret_detected(self):
        """真实形态 AppSecret（32 位 hex）应被检测到。"""
        content = f'MP_ARCHIVER_WECHAT_APP_SECRET={self.FAKE_WX_SECRET_HEX}\n'
        f = _write_temp_file(content, suffix=".env")
        try:
            findings = scan_file(f)
            assert any(i.rule_name == "微信AppSecret" for i in findings)
        finally:
            f.unlink()

    def test_wechat_app_secret_sequential_skipped(self):
        """顺序占位 0123456789abcdef×2 不应检测。"""
        content = 'APP_SECRET = "0123456789abcdef0123456789abcdef"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            assert not any(i.rule_name == "微信AppSecret" for i in findings)
        finally:
            f.unlink()

    def test_wechat_app_secret_empty_value_skipped(self):
        """空占位（.env.example 形态）不应检测。"""
        content = "MP_ARCHIVER_WECHAT_APP_SECRET=\n"
        f = _write_temp_file(content, suffix=".env")
        try:
            findings = scan_file(f)
            assert not any(i.rule_name == "微信AppSecret" for i in findings)
        finally:
            f.unlink()

    def test_tencent_akid_detected(self):
        """腾讯云 SecretId（AKID 前缀）应被检测到。"""
        content = f'secret_id = "{self.FAKE_AKID}"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            assert any(i.rule_name == "腾讯云SecretId" for i in findings)
        finally:
            f.unlink()

    def test_github_token_detected(self):
        """GitHub Token（ghp_ 前缀）应被检测到。"""
        content = f'token = "{self.FAKE_GH}"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            assert any(i.rule_name == "GitHubToken" for i in findings)
        finally:
            f.unlink()

    def test_github_token_placeholder_skipped(self):
        """your_ 前缀占位 Token 不应检测。"""
        content = 'token = "ghp_your_token_here"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            assert not any(i.rule_name == "GitHubToken" for i in findings)
        finally:
            f.unlink()

    def test_slack_token_detected(self):
        """Slack Token（xoxb- 前缀）应被检测到。"""
        content = f'slack = "{self.FAKE_SLACK}"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            assert any(i.rule_name == "SlackToken" for i in findings)
        finally:
            f.unlink()

    def test_secret_key_context_detected(self):
        """32 位随机 SecretKey 赋值应被检测到。"""
        content = f'SECRET_KEY = "{self.FAKE_SECRET_KEY}"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            assert any(i.rule_name == "通用SecretKey上下文" for i in findings)
        finally:
            f.unlink()

    def test_jwt_style_secret_with_dashes_skipped(self):
        """带连字符的 JWT 测试密钥不应被新规则误报。"""
        content = 'SECRET = "interop-secret-0123456789-abcdef-ghijkl"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            assert not any(i.rule_name == "通用SecretKey上下文" for i in findings)
        finally:
            f.unlink()

    def test_existing_sk_rule_unaffected(self):
        """既有 sk- 规则行为不受新增规则影响。"""
        content = f'key = "{self.FAKE_SK}"\n'
        f = _write_temp_file(content, suffix=".py")
        try:
            findings = scan_file(f)
            assert any(i.type == API_KEY for i in findings)
        finally:
            f.unlink()

    def test_sequential_value_helper(self):
        """顺序/重复值判定函数边界。"""
        from lib.checks.sensitive_info import _is_sequential_or_dummy_value as is_dummy
        assert is_dummy("0123456789abcdef0123456789abcdef")
        assert is_dummy("0000000000000000")
        assert is_dummy("xxxxxxxxxxxxxxxx")
        assert is_dummy("1234567890abcdef")
        assert not is_dummy("5f4dcc3b5aa765d61d8327deb882cf99")
        assert not is_dummy("Zp9Kq2Xm4Rt7Vb1Wy8Uc3Dz6Ha5Jf0Gk")
        assert not is_dummy("short")

