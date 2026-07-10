"""敏感信息检测模块。

检测代码和文档中的手机号、邮箱、API密钥、密码、个人路径、内网IP、
数据库连接串、会话ID、私钥等敏感信息，支持自动脱敏部分类型。

支持自动脱敏：手机号、邮箱、Windows/Unix 个人路径
高风险不自动修复：API_KEY、PASSWORD、DB_CONN、SESSION_ID、PRIVATE_KEY

CLI 用法:
    python -m lib.checks.sensitive_info          # 扫描当前目录
    python check-sensitive-info.py              # 顶层入口脚本
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from re import Match, Pattern
from collections.abc import Callable

from lib.cli import (
    print_header, print_pass, print_error, print_warn, print_summary,
    setup_safe_output,
)
from lib.project import resolve_project_root

__all__ = [
    "PHONE", "EMAIL", "IDCARD", "API_KEY", "PASSWORD",
    "PERSONAL_PATH_WIN", "PERSONAL_PATH_UNIX", "INTERNAL_IP",
    "DB_CONN", "SESSION_ID", "PRIVATE_KEY",
    "SEVERITY_HIGH", "SEVERITY_MEDIUM", "SEVERITY_LOW",
    "Rule", "Finding",
    "RULES",
    "scan_file", "scan_directory", "fix_file",
    "SUPPORTED_EXTENSIONS", "DEFAULT_EXCLUDE_DIRS",
    "register_args", "run", "build_parser", "main",
]

PHONE = "phone"
EMAIL = "email"
IDCARD = "idcard"
API_KEY = "api_key"
PASSWORD = "password"
PERSONAL_PATH_WIN = "personal_path_win"
PERSONAL_PATH_UNIX = "personal_path_unix"
INTERNAL_IP = "internal_ip"
DB_CONN = "db_conn"
SESSION_ID = "session_id"
PRIVATE_KEY = "private_key"

SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"

SUPPORTED_EXTENSIONS = {
    ".py", ".md", ".markdown", ".rst", ".txt", ".json", ".yaml", ".yml", ".toml",
    ".ini", ".cfg", ".conf", ".sh", ".bash", ".zsh", ".ps1",
    ".bat", ".env", ".js", ".ts", ".tsx", ".jsx",
}

MARKDOWN_CODE_BLOCK_EXTS = {".md", ".markdown", ".rst"}

CODE_BLOCK_EXAMPLE_SKIP_TYPES = {PHONE, EMAIL, API_KEY, PASSWORD, INTERNAL_IP, DB_CONN, SESSION_ID}

DEFAULT_EXCLUDE_DIRS = {
    "vendor", "external", "playground", "__pycache__", ".git",
    ".venv", "node_modules", ".pytest_cache", ".mypy_cache",
    ".meta", "reports", ".trae", ".temp",
}

SYSTEM_WIN_USERS = {
    "public", "default", "all users", "default user", "defaultuser0",
    "user", "admin", "xxx", "test", "demo", "shared", "guest",
    "wdagutilityaccount", "$user", "{username}", "<user>",
}

SYSTEM_UNIX_USERS = {
    "user", "admin", "xxx", "test", "demo", "shared", "root",
    "$user", "{username}", "<user>",
}

GIT_SSH_DOMAINS = {"github.com", "gitlab.com", "bitbucket.org", "gitee.com", "gitcode.com"}

INTERNAL_DOMAIN_SUFFIXES = {".container", ".internal", ".local", ".lan"}

SYSTEMD_UNIT_SUFFIXES = {
    ".service", ".socket", ".device", ".mount", ".automount",
    ".swap", ".target", ".path", ".timer", ".slice", ".scope",
}

PLACEHOLDER_EMAIL_USERNAMES = {"xxx", "test", "example", "dummy", "fake", "占位", "work"}

PLACEHOLDER_EMAIL_DOMAINS = {"xxx.", "example.", "test.", "invalid.", "localhost"}

PUBLIC_ROLE_EMAIL_PREFIXES = {
    "support", "info", "admin", "contact", "hello",
    "noreply", "no-reply", "sales", "help",
}

CONTEXT_AWARE_TYPES = {PHONE, EMAIL, API_KEY, PASSWORD, INTERNAL_IP, DB_CONN}

EXAMPLE_CODE_BLOCK_KEYWORDS = re.compile(
    r'(?<![非不无])(?:正例|反例|示例|例子|用法|演示)|'
    r'\b(?:example|sample|demo)\b',
    re.IGNORECASE
)

FILE_EXCLUDE_PATTERNS = {".env.example"}


@dataclass
class Rule:
    """检测规则定义。"""

    name: str
    type: str
    severity: str
    pattern: Pattern[str]
    placeholder_patterns: list[Pattern[str]] = field(default_factory=list)
    fix_func: Callable[[Match[str]], str] | None = None
    suggestion: str = ""


@dataclass
class Finding:
    """检测到的敏感信息项。"""

    file: Path
    line: int
    col: int
    type: str
    severity: str
    match: str
    rule_name: str
    suggestion: str
    fixable: bool


def _fix_phone(m: Match[str]) -> str:
    """手机号脱敏：中间4位替换为****。"""
    s = m.group(0)
    return s[:3] + "****" + s[7:]


def _fix_email(m: Match[str]) -> str:
    """邮箱脱敏：用户名部分保留首字符+***+尾字符。"""
    s = m.group(0)
    at_idx = s.rfind("@")
    if at_idx <= 1:
        return s
    user = s[:at_idx]
    domain = s[at_idx:]
    if len(user) <= 2:
        masked_user = user[0] + "***"
    else:
        masked_user = user[0] + "***" + user[-1]
    return masked_user + domain


def _fix_personal_path_win(m: Match[str]) -> str:
    """Windows个人路径脱敏：替换为 <USER_HOME>\。"""
    return "<USER_HOME>\\"


def _fix_personal_path_unix(m: Match[str]) -> str:
    """Unix个人路径脱敏：替换为 ~/。"""
    return "~/"


def _is_example_context(line: str) -> bool:
    """检查行是否包含示例/文档上下文关键词。"""
    if re.search(r'[\u4e00-\u9fa5]*(?:示例|例如|脱敏|演示|样例|占位|测试数据|样例数据)[\u4e00-\u9fa5]*', line):
        return True
    if re.search(r'\b(?:example|sample|demo|placeholder|mock|dummy|fake)\b', line, re.IGNORECASE):
        if not re.search(r'example\.(?:com|org|net|io)', line, re.IGNORECASE):
            return True
    if re.search(r'\b(?:e\.g\.|for instance|for demonstration|test data)\b', line, re.IGNORECASE):
        return True
    return False


def _is_comment_note_context(line: str) -> bool:
    """检查行是否包含注释标记（TODO/FIXME/NOTE）。"""
    return bool(re.search(r'(?:#|//|/\*|;)\s*(?:TODO|FIXME|NOTE)\b', line, re.IGNORECASE))


def _has_nosec_marker(line: str) -> bool:
    """检查行尾是否包含 nosec 或 sensitive-ignore 标记。

    支持的标记（不区分大小写）：
    - # nosec、# sensitive-ignore（Python/Shell/Ruby 等）
    - // nosec（C/C++/Java/JS/TS 等）
    - /* nosec */（C 风格块注释行尾）
    - <!-- nosec -->（HTML/XML 注释）
    - %% nosec（Mermaid 图表注释）
    - -- nosec（SQL/Lua 等）
    """
    nosec_pattern = re.compile(
        r'(?:'
        r'#\s*(?:nosec|sensitive-ignore)'
        r'|//\s*(?:nosec|sensitive-ignore)'
        r'|/\*\s*(?:nosec|sensitive-ignore)\s*\*/'
        r'|<!--\s*(?:nosec|sensitive-ignore)\s*-->'
        r'|%%\s*(?:nosec|sensitive-ignore)'
        r'|--\s*(?:nosec|sensitive-ignore)'
        r')\s*$',
        re.IGNORECASE
    )
    return bool(nosec_pattern.search(line))


def _contains_chinese(s: str) -> bool:
    """检查字符串是否包含中文字符。"""
    return bool(re.search(r'[\u4e00-\u9fa5]', s))


def _is_all_dots(s: str) -> bool:
    """检查字符串是否全是点号。"""
    return bool(s) and all(c == '.' for c in s)


def _should_skip_email(match_str: str) -> tuple[bool, str | None, bool]:
    """检查邮箱匹配是否应该跳过或降级。

    返回:
        (should_skip, override_severity, is_public_role) - 如果should_skip为True则跳过，
        如果override_severity不为None则使用指定等级，否则使用默认等级，
        is_public_role表示是否为公开角色邮箱（不应自动脱敏）。
    """
    at_idx = match_str.rfind("@")
    if at_idx < 2:
        return True, None, False

    user = match_str[:at_idx]
    domain = match_str[at_idx + 1:].lower()

    if user.lower() == "git" and domain in GIT_SSH_DOMAINS:
        return True, None, False

    for suffix in SYSTEMD_UNIT_SUFFIXES:
        if suffix in match_str:
            return True, None, False

    for internal_suffix in INTERNAL_DOMAIN_SUFFIXES:
        if domain.endswith(internal_suffix):
            return True, None, False

    user_lower = user.lower()
    for placeholder in PLACEHOLDER_EMAIL_USERNAMES:
        if placeholder in user_lower:
            return True, None, False

    for placeholder_domain in PLACEHOLDER_EMAIL_DOMAINS:
        if domain.startswith(placeholder_domain):
            return True, None, False

    if user.count("-") > 2:
        return True, None, False

    for role_prefix in PUBLIC_ROLE_EMAIL_PREFIXES:
        if user_lower == role_prefix or user_lower.startswith(role_prefix + "+"):
            return False, SEVERITY_LOW, True

    return False, None, False


def _is_valid_path_username(username: str) -> bool:
    """检查路径用户名是否有效（不是...、模板变量或包含特殊字符）。"""
    if not username:
        return False
    if _is_all_dots(username):
        return False
    if username in ("...", "..", "."):
        return False
    if re.match(r'^[<${].*[>}]$', username):
        return False
    if re.search(r'[`/\\<>:"|?*{}]', username):
        return False
    if username.startswith(".") or username.endswith("."):
        return False
    return True


RULES: list[Rule] = [
    Rule(
        name="中国大陆手机号",
        type=PHONE,
        severity=SEVERITY_HIGH,
        pattern=re.compile(
            r"(?<![>\"'`\w\d])1[3-9]\d{9}(?![\w@\d])"
        ),
        placeholder_patterns=[
            re.compile(r"1[3-9]\d{9}\.example", re.IGNORECASE),
            re.compile(r"13800138000"),
        ],
        fix_func=_fix_phone,
        suggestion="手机号属于个人隐私信息，请脱敏后再提交，可使用自动修复功能",
    ),
    Rule(
        name="邮箱地址",
        type=EMAIL,
        severity=SEVERITY_MEDIUM,
        pattern=re.compile(
            r"[a-zA-Z0-9._%+-]{2,}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        ),
        placeholder_patterns=[
            re.compile(r"@example\.(com|org|net)$", re.IGNORECASE),
            re.compile(r"@test\.(com|org|net)$", re.IGNORECASE),
            re.compile(r"^your[-_]?.*@", re.IGNORECASE),
            re.compile(r"^admin@test", re.IGNORECASE),
            re.compile(r"^noreply@", re.IGNORECASE),
            re.compile(r"@mystmd\.org$", re.IGNORECASE),
            re.compile(r"@volcengine\.com$"),
            re.compile(r"@example\.com$", re.IGNORECASE),
            re.compile(r"user@example", re.IGNORECASE),
            re.compile(r"test@test", re.IGNORECASE),
        ],
        fix_func=_fix_email,
        suggestion="邮箱可能泄露个人身份，请确认是否为真实邮箱，测试邮箱请使用example.com",
    ),
    Rule(
        name="Windows个人目录路径",
        type=PERSONAL_PATH_WIN,
        severity=SEVERITY_MEDIUM,
        pattern=re.compile(
            r"([A-Za-z]:[\\/])Users[\\/](?!(?:" + "|".join(re.escape(u) for u in SYSTEM_WIN_USERS) + r")(?:[\\/]|$))([^\\/<>\"|?*\n\r\t]+)[\\/]",
            re.IGNORECASE
        ),
        placeholder_patterns=[],
        fix_func=_fix_personal_path_win,
        suggestion="Windows用户路径包含本地用户名，可能泄露个人信息，请替换为 <USER_HOME>\\",
    ),
    Rule(
        name="Unix个人目录路径",
        type=PERSONAL_PATH_UNIX,
        severity=SEVERITY_MEDIUM,
        pattern=re.compile(
            r"/(?:Users|home)/(?!(?:" + "|".join(re.escape(u) for u in SYSTEM_UNIX_USERS) + r")(?:/|$))([^/\n\r\t`]+)/"
        ),
        placeholder_patterns=[],
        fix_func=_fix_personal_path_unix,
        suggestion="Unix用户路径包含本地用户名，可能泄露个人信息，请替换为 ~/",
    ),
    Rule(
        name="内网IP地址",
        type=INTERNAL_IP,
        severity=SEVERITY_LOW,
        pattern=re.compile(
            r"\b((?:192\.168\.\d{1,3}\.\d{1,3})|(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3})|(?:172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}))\b"
        ),
        placeholder_patterns=[
            re.compile(r"^127\.0\.0\.1$"),
            re.compile(r"^0\.0\.0\.0$"),
        ],
        fix_func=None,
        suggestion="内网IP可能泄露网络拓扑结构，如为示例请使用文档说明",
    ),
    Rule(
        name="API密钥",
        type=API_KEY,
        severity=SEVERITY_HIGH,
        pattern=re.compile(
            r"(?:sk-(?=[A-Za-z0-9]*[A-Za-z])(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{20,}|"
            r"AKIA[0-9A-Z]{16}|"
            r"(?:api[_-]?key|apikey|secret[_-]?key|access[_-]?key)\s*[:=]\s*['\"][^\s'\"\\u4e00-\\u9fa5]{16,}['\"])"
        ),
        placeholder_patterns=[
            re.compile(r"sk-?x{3,}", re.IGNORECASE),
            re.compile(r"your[-_]?api[-_]?key", re.IGNORECASE),
            re.compile(r"<api[-_]?key>", re.IGNORECASE),
            re.compile(r"YOUR_API_KEY", re.IGNORECASE),
            re.compile(r"xxxx+", re.IGNORECASE),
            re.compile(r"sk-[A-Za-z0-9]{0,19}$"),
            re.compile(r"['\"]sk-", re.IGNORECASE),
            re.compile(r"AKIA[0-9A-Z]{0,10}$"),
        ],
        fix_func=None,
        suggestion="API密钥泄露可能导致资产损失，请立即轮换密钥并从历史记录中清除",
    ),
    Rule(
        name="密码",
        type=PASSWORD,
        severity=SEVERITY_HIGH,
        pattern=re.compile(
            r"(?:password|passwd|pwd|secret)\s*[:=]\s*['\"]([^'\"]{4,})['\"]"
        ),
        placeholder_patterns=[
            re.compile(r"your[-_]?password", re.IGNORECASE),
            re.compile(r"changeme", re.IGNORECASE),
            re.compile(r"['\"]xxx['\"]", re.IGNORECASE),
            re.compile(r"['\"]secret['\"]", re.IGNORECASE),
            re.compile(r"['\"]placeholder['\"]", re.IGNORECASE),
            re.compile(r"['\"]\*{3,}['\"]", re.IGNORECASE),
        ],
        fix_func=None,
        suggestion="明文密码泄露风险极高，请使用环境变量或密钥管理服务",
    ),
    Rule(
        name="数据库连接串",
        type=DB_CONN,
        severity=SEVERITY_HIGH,
        pattern=re.compile(
            r"(?:mysql|postgres(?:ql)?|mongodb|redis|mssql|oracle)://"
            r"(?:[^@\s/]+@)?"
            r"(?!(?:localhost|127\.0\.0\.1)(?::\d+)?(?:/|$))"
            r"[^\s'\"]+"
        ),
        placeholder_patterns=[
            re.compile(r"://[^@]*@?(?:localhost|127\.0\.0\.1)"),
        ],
        fix_func=None,
        suggestion="数据库连接串可能包含用户名密码和内网地址，请使用环境变量注入",
    ),
    Rule(
        name="会话/设备ID",
        type=SESSION_ID,
        severity=SEVERITY_MEDIUM,
        pattern=re.compile(
            r"\b\d{15,}:[a-fA-F0-9]{32,}\b"
        ),
        placeholder_patterns=[],
        fix_func=None,
        suggestion="会话ID和设备ID可能关联真实用户，请确认是否为测试数据",
    ),
    Rule(
        name="私钥",
        type=PRIVATE_KEY,
        severity=SEVERITY_HIGH,
        pattern=re.compile(
            r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"
        ),
        placeholder_patterns=[],
        fix_func=None,
        suggestion="私钥泄露会导致身份伪造，请立即吊销对应公钥并轮换密钥对",
    ),
]


def _is_placeholder(match_str: str, rule: Rule) -> bool:
    """检查匹配结果是否为占位符/示例值。"""
    for pp in rule.placeholder_patterns:
        if pp.search(match_str):
            return True
    return False


def _should_skip_line(line: str, in_code_block: bool) -> bool:
    """判断该行是否应该跳过。

    仅跳过空行。上下文感知的跳过由 per-rule 逻辑处理
    （CONTEXT_AWARE_TYPES + is_example、CODE_BLOCK_EXAMPLE_SKIP_TYPES + code_block_is_example），
    不在行级别全局跳过，以避免遗漏个人路径、私钥等不受示例上下文影响的敏感类型。
    """
    stripped = line.strip()
    if not stripped:
        return False
    return False


def _is_in_markdown_code(line: str, match_start: int) -> bool:
    """检查匹配位置是否在Markdown代码符号后面（行内代码）。"""
    prefix = line[:match_start]
    if prefix.endswith(">") or prefix.endswith("`"):
        return True
    if prefix.rstrip().endswith("`"):
        return True
    return False


def _is_in_url_path(line: str, match_start: int, match_end: int) -> bool:
    """检查匹配是否在URL路径中（/path/138xxxxxxx 这种格式）。"""
    if match_start == 0:
        return False
    before_char = line[match_start - 1]
    if before_char in ("/", "\\"):
        return True
    prefix_window = line[max(0, match_start - 10):match_start]
    if "/" in prefix_window and not re.search(r"[\s：:，,（(）)]", prefix_window):
        return True
    return False


def _is_example_code_block(lines: list[str], start_idx: int) -> bool:
    """检查从 start_idx 开始的代码块是否是示例代码块。

    向上查看最多 8 行非空行（先跳过紧邻代码块的空行），
    查找包含"示例""example"等关键词的行或标题，
    如果包含示例关键词则返回 True。
    """
    i = start_idx - 1
    while i >= 0 and not lines[i].strip():
        i -= 1

    non_empty_count = 0
    while i >= 0 and non_empty_count < 8:
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i -= 1
            continue
        if EXAMPLE_CODE_BLOCK_KEYWORDS.search(stripped):
            return True
        if stripped.startswith('#'):
            break
        non_empty_count += 1
        i -= 1
    return False


def scan_file(file_path: Path) -> list[Finding]:
    """扫描单个文件中的敏感信息。

    参数:
        file_path: 要扫描的文件路径。
    返回:
        检测到的敏感信息 Finding 列表。
    """
    if file_path.name in FILE_EXCLUDE_PATTERNS:
        return []

    ext = file_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return []

    use_code_block_context = ext in MARKDOWN_CODE_BLOCK_EXTS

    try:
        lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    except OSError:
        return []

    findings: list[Finding] = []
    in_code_block = False
    code_block_is_example = False

    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()
        if use_code_block_context and stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_block_is_example = _is_example_code_block(lines, line_no - 1)
            else:
                in_code_block = False
                code_block_is_example = False
            continue

        if _should_skip_line(line, in_code_block):
            continue

        if _has_nosec_marker(line):
            continue

        is_example = _is_example_context(line)
        is_note = _is_comment_note_context(line)

        for rule in RULES:
            for m in rule.pattern.finditer(line):
                match_str = m.group(0)
                match_start = m.start()
                match_end = m.end()
                override_severity = None
                is_public_role_email = False
                is_fixable = rule.fix_func is not None

                if _is_placeholder(match_str, rule):
                    continue

                if rule.type == EMAIL:
                    skip_email, override_severity, is_public_role_email = _should_skip_email(match_str)
                    if skip_email:
                        continue
                    if is_public_role_email:
                        is_fixable = False

                if rule.type in (PERSONAL_PATH_WIN, PERSONAL_PATH_UNIX):
                    if rule.type == PERSONAL_PATH_WIN and len(m.groups()) >= 2:
                        username = m.group(2)
                        if not _is_valid_path_username(username):
                            continue
                        if username.lower() in SYSTEM_WIN_USERS:
                            continue
                    elif rule.type == PERSONAL_PATH_UNIX and len(m.groups()) >= 1:
                        username = m.group(1)
                        if not _is_valid_path_username(username):
                            continue
                        if username.lower() in SYSTEM_UNIX_USERS:
                            continue

                if rule.type == PASSWORD:
                    if len(m.groups()) >= 1:
                        pwd_value = m.group(1)
                        if _is_all_dots(pwd_value):
                            continue
                        if ' ' in pwd_value:
                            continue
                        if _contains_chinese(pwd_value):
                            continue

                if rule.type == API_KEY:
                    if (match_str.startswith('api_key') or match_str.startswith('apikey') or
                        match_str.startswith('secret_key') or match_str.startswith('secret-key') or
                        match_str.startswith('access_key') or match_str.startswith('access-key')):
                        value_match = re.search(r"""['"]([^'"]+)['"]""", match_str)
                        if value_match:
                            value = value_match.group(1)
                            if len(value) < 16:
                                continue
                            if ' ' in value:
                                continue
                            if _contains_chinese(value):
                                continue

                if rule.type == PHONE:
                    if _is_in_markdown_code(line, match_start):
                        continue
                    if _is_in_url_path(line, match_start, match_end):
                        continue
                    before_char = line[match_start - 1] if match_start > 0 else ""
                    if before_char in ("/", "\\"):
                        continue

                if in_code_block and code_block_is_example:
                    if rule.type in CODE_BLOCK_EXAMPLE_SKIP_TYPES:
                        continue

                if rule.type in CONTEXT_AWARE_TYPES and is_example:
                    continue

                current_severity = rule.severity
                if in_code_block and code_block_is_example and rule.type == PRIVATE_KEY:
                    current_severity = SEVERITY_LOW
                elif rule.type == PRIVATE_KEY and is_example:
                    current_severity = SEVERITY_MEDIUM
                elif rule.type in CONTEXT_AWARE_TYPES and is_note and not is_example:
                    if current_severity == SEVERITY_HIGH:
                        current_severity = SEVERITY_MEDIUM
                    elif current_severity == SEVERITY_MEDIUM:
                        current_severity = SEVERITY_LOW

                if rule.type == EMAIL and override_severity is not None:
                    current_severity = override_severity

                if rule.type == INTERNAL_IP and match_str in ("127.0.0.1", "localhost"):
                    continue

                findings.append(Finding(
                    file=file_path,
                    line=line_no,
                    col=match_start + 1,
                    type=rule.type,
                    severity=current_severity,
                    match=match_str,
                    rule_name=rule.name,
                    suggestion=rule.suggestion,
                    fixable=is_fixable,
                ))

    return findings


def scan_directory(
    root: Path,
    exclude_dirs: set[str] | None = None,
) -> list[Finding]:
    """递归扫描目录下所有支持的文件。

    参数:
        root: 要扫描的根目录。
        exclude_dirs: 要排除的目录名集合，默认使用 DEFAULT_EXCLUDE_DIRS。
    返回:
        所有检测到的敏感信息 Finding 列表。
    """
    if exclude_dirs is None:
        exclude_dirs = DEFAULT_EXCLUDE_DIRS.copy()

    all_findings: list[Finding] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        rel_parts = path.relative_to(root).parts
        if any(part in exclude_dirs for part in rel_parts):
            continue

        findings = scan_file(path)
        all_findings.extend(findings)

    return all_findings


def fix_file(file_path: Path, findings: list[Finding]) -> int:
    """对文件中可自动修复的finding执行脱敏。

    参数:
        file_path: 要修复的文件路径。
        findings: 该文件对应的 Finding 列表。
    返回:
        成功修复的数量。
    """
    fixable_findings = [f for f in findings if f.fixable and f.file == file_path]
    if not fixable_findings:
        return 0

    try:
        lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    except OSError:
        return 0

    line_fix_map: dict[int, list[tuple[Finding, Rule]]] = {}
    for f in fixable_findings:
        rule = next((r for r in RULES if r.type == f.type), None)
        if rule and rule.fix_func:
            if f.line not in line_fix_map:
                line_fix_map[f.line] = []
            line_fix_map[f.line].append((f, rule))

    fixed_count = 0
    for line_num, fix_list in line_fix_map.items():
        idx = line_num - 1
        if idx >= len(lines):
            continue

        line = lines[idx]
        fix_list.sort(key=lambda x: x[0].col, reverse=True)

        for finding, rule in fix_list:
            col_start = finding.col - 1
            col_end = col_start + len(finding.match)
            original_text = line[col_start:col_end]
            if original_text != finding.match:
                for m in rule.pattern.finditer(line):
                    if m.group(0) == finding.match:
                        col_start = m.start()
                        col_end = m.end()
                        break

            if rule.fix_func:
                synthetic_match = re.match(rule.pattern, finding.match)
                if synthetic_match:
                    replaced = rule.fix_func(synthetic_match)
                    line = line[:col_start] + replaced + line[col_end:]
                    fixed_count += 1

        lines[idx] = line

    if fixed_count > 0:
        try:
            file_path.write_text("".join(lines), encoding="utf-8")
        except OSError:
            return 0

    return fixed_count


def _simple_test() -> None:
    """简单自测试。"""
    import tempfile

    phone_real = "138" + "1234" + "5678"
    phone_test = "138" + "0013" + "8000"
    email_real = "zhang.san" + "@" + "company.com"
    email_example = "user" + "@" + "example.com"
    email_volc = "dev" + "@" + "volcengine.com"
    sk_key = "sk-" + "1234567890abcdefghijklmnop"
    pwd_value = "my" + "secretpass123"
    priv_key_header = "-----BEGIN " + "RSA PRIVATE KEY-----"
    session_id = "121377507783968" + ":" + "5e488b49a1b2c3d4e5f6a7b8c9d0e1f2"
    db_user = "root"
    db_pass = "password" + "123"
    db_host = "10.0.0" + ".5"
    db_scheme = "mysql" + "://"
    db_conn = f"{db_scheme}{db_user}:{db_pass}@{db_host}:3306/mydb"
    win_path_user = "test" + "user"
    unix_path_prefix = "/home" + "/"
    unix_path_user = "dev" + "user"
    ip_internal = "192.168" + ".1.100"
    ip_example = "192.168" + ".1.1"
    pwd_keyword = "pass" + "word"

    test_content = f"""# 测试文件

手机号：{phone_real}
手机号URL路径中：/api/user/{phone_real}/info
测试邮箱占位符：{email_example}
企业公开邮箱：{email_volc}
真实邮箱：{email_real}
Windows路径：C:\\Users\\{win_path_user}\\Documents
Unix路径：{unix_path_prefix}{unix_path_user}/project
内网IP：{ip_internal}
API密钥：{sk_key}
{pwd_keyword} = "{pwd_value}"
私钥头：{priv_key_header}
会话ID：{session_id}
数据库连接：{db_conn}

## 示例（不应报警）

手机号示例（Markdown代码）：`{phone_test}`
测试邮箱：user@test.com
示例IP（在example上下文中）：{ip_example}
占位符密钥：sk-xxxx
示例密码：{pwd_keyword} = "changeme"
本地数据库：mysql://localhost:3306/test
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(test_content)
        tmp_path = Path(f.name)

    print("=== 敏感信息检测自测试 ===")
    print(f"测试文件: {tmp_path}")
    print()

    findings = scan_file(tmp_path)
    print(f"检测到 {len(findings)} 个问题：")
    for finding in findings:
        print(f"  [{finding.severity.upper()}] {finding.rule_name} (L{finding.line}:{finding.col})")
        print(f"    匹配: {finding.match}")
        print(f"    建议: {finding.suggestion}")
        print(f"    可修复: {finding.fixable}")
        print()

    fixable = [f for f in findings if f.fixable]
    print(f"可自动修复: {len(fixable)} 个")
    if fixable:
        fixed = fix_file(tmp_path, findings)
        print(f"已修复: {fixed} 个")
        print()
        print("修复后内容:")
        print("-" * 40)
        print(tmp_path.read_text(encoding="utf-8"))
        print("-" * 40)

    tmp_path.unlink()
    print("\n自测试完成。")


def register_args(parser: argparse.ArgumentParser) -> None:
    """注册 sensitive-info-check 的 CLI 参数。"""
    parser.add_argument(
        "--fix",
        action="store_true",
        default=False,
        help="自动修复可修复的问题（手机号、邮箱、个人路径脱敏）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="以 JSON 格式输出结果",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="指定报告输出文件路径（JSON模式下可指定文件输出）",
    )
    parser.add_argument(
        "--exclude",
        type=str,
        default=None,
        help="额外排除的目录（逗号分隔，可叠加默认排除）",
    )
    parser.add_argument(
        "--only-severity",
        type=str,
        choices=["high", "medium", "low"],
        default="low",
        help="只报告指定等级及以上（high/medium/low，默认 low）",
    )


def _build_parser() -> argparse.ArgumentParser:
    """构建 sensitive-info-check CLI 参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="sensitive-info-check",
        description="敏感信息脱敏检查工具：检测代码和文档中的手机号、邮箱、API密钥、密码、个人路径等敏感信息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python check-sensitive-info.py                  # 默认扫描
  python check-sensitive-info.py --fix            # 自动修复可脱敏问题
  python check-sensitive-info.py --json           # JSON 格式输出
  python check-sensitive-info.py --only-severity high  # 只显示高风险问题
  python check-sensitive-info.py --exclude temp,build  # 额外排除目录
  python -m lib.checks.sensitive_info --test      # 运行自测试
        """,
    )
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="指定项目根目录路径（默认自动发现项目根）",
    )
    register_args(parser)
    parser.add_argument(
        "--version",
        action="version",
        version="sensitive-info-check 1.0.0",
    )
    return parser


build_parser = _build_parser


def _truncate_match(text: str, max_len: int = 50) -> str:
    """截断匹配内容用于显示。"""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def _severity_rank(severity: str) -> int:
    """风险等级排序：high=3, medium=2, low=1。"""
    return {"high": 3, "medium": 2, "low": 1}.get(severity, 0)


def run(project_root: Path, args: argparse.Namespace) -> int:
    """敏感信息脱敏检查主入口。

    返回退出码：
        0 = 无问题
        1 = 有 HIGH 风险问题
        2 = 有 MEDIUM 问题（无 HIGH）
    """
    use_json = getattr(args, "json", False)
    auto_fix = getattr(args, "fix", False)
    only_severity = getattr(args, "only_severity", "low")
    output_path = getattr(args, "output", None)
    extra_exclude = getattr(args, "exclude", None)

    exclude_dirs = DEFAULT_EXCLUDE_DIRS.copy()
    if extra_exclude:
        for d in extra_exclude.split(","):
            d = d.strip()
            if d:
                exclude_dirs.add(d)

    findings = scan_directory(project_root, exclude_dirs)

    min_rank = _severity_rank(only_severity)
    findings = [f for f in findings if _severity_rank(f.severity) >= min_rank]

    findings_by_severity: dict[str, list[Finding]] = defaultdict(list)
    for f in findings:
        findings_by_severity[f.severity].append(f)

    high_count = len(findings_by_severity.get("high", []))
    medium_count = len(findings_by_severity.get("medium", []))
    low_count = len(findings_by_severity.get("low", []))
    total_count = len(findings)

    fixed_count = 0
    backup_files: list[Path] = []

    if auto_fix:
        fixable_findings = [f for f in findings if f.fixable]
        if fixable_findings:
            findings_by_file: dict[Path, list[Finding]] = defaultdict(list)
            for f in fixable_findings:
                findings_by_file[f.file].append(f)

            for file_path, file_findings in findings_by_file.items():
                backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                try:
                    shutil.copy2(file_path, backup_path)
                    backup_files.append(backup_path)
                except OSError:
                    continue

                fixed = fix_file(file_path, file_findings)
                fixed_count += fixed

            for backup in backup_files:
                try:
                    backup.unlink()
                except OSError:
                    pass

    unfixable_count = total_count - fixed_count

    if use_json:
        result = {
            "tool": "sensitive-info-check",
            "version": "1.0.0",
            "project_root": str(project_root),
            "summary": {
                "total": total_count,
                "high": high_count,
                "medium": medium_count,
                "low": low_count,
                "fixed": fixed_count,
                "unfixable": unfixable_count,
            },
            "findings": [],
        }

        for severity in ["high", "medium", "low"]:
            for f in findings_by_severity.get(severity, []):
                rel_path = f.file.relative_to(project_root).as_posix()
                result["findings"].append({
                    "file": rel_path,
                    "line": f.line,
                    "col": f.col,
                    "type": f.type,
                    "severity": f.severity,
                    "rule_name": f.rule_name,
                    "match": _truncate_match(f.match, 200),
                    "suggestion": f.suggestion,
                    "fixable": f.fixable,
                })

        output_str = json.dumps(result, ensure_ascii=False, indent=2)
        if output_path:
            Path(output_path).write_text(output_str, encoding="utf-8")
        else:
            print(output_str)
    else:
        print_header("敏感信息脱敏检查")
        print()

        if total_count == 0:
            print_pass("未检测到敏感信息")
        else:
            for severity in ["high", "medium", "low"]:
                sev_findings = findings_by_severity.get(severity, [])
                if not sev_findings:
                    continue

                severity_label = {
                    "high": "高风险 (HIGH)",
                    "medium": "中风险 (MEDIUM)",
                    "low": "低风险 (LOW)",
                }[severity]

                if severity == "high":
                    print_error(f"【{severity_label}】共 {len(sev_findings)} 项：")
                elif severity == "medium":
                    print_warn(f"【{severity_label}】共 {len(sev_findings)} 项：")
                else:
                    print(f"  【{severity_label}】共 {len(sev_findings)} 项：")

                findings_by_file: dict[Path, list[Finding]] = defaultdict(list)
                for f in sev_findings:
                    findings_by_file[f.file].append(f)

                for file_path, file_findings in sorted(findings_by_file.items()):
                    rel_path = file_path.relative_to(project_root).as_posix()
                    print(f"    文件: {rel_path}")
                    for f in sorted(file_findings, key=lambda x: x.line):
                        match_display = _truncate_match(f.match.strip(), 60)
                        status_icon = "✗" if severity == "high" else ("⚠" if severity == "medium" else "!")
                        fix_tag = " [可修复]" if f.fixable else " [需人工处理]"
                        print(f"      L{f.line}:{f.col} {status_icon} {f.rule_name}{fix_tag}")
                        print(f"        匹配: {match_display}")
                        print(f"        建议: {f.suggestion}")
                print()

            if auto_fix and fixed_count > 0:
                print_pass(f"自动修复完成：共修复 {fixed_count} 项（手机号、邮箱、个人路径已脱敏）")
                if unfixable_count > 0:
                    print_warn(f"剩余 {unfixable_count} 项需人工处理（API密钥、密码等无法自动修复）")
                print()

    if high_count > 0:
        exit_code = 1
    elif medium_count > 0:
        exit_code = 2
    else:
        exit_code = 0

    if not use_json:
        pass_count = 1 if total_count == 0 else 0
        warn_count = medium_count + low_count
        error_count = high_count
        print_summary(pass_count, warn_count, error_count)
        print()
        if exit_code == 0:
            print_pass("敏感信息检查通过！")
        elif exit_code == 1:
            print_error("检测到高风险敏感信息，请立即处理！")
        else:
            print_warn("检测到中风险敏感信息，建议处理")

    return exit_code


def main(argv: list[str] | None = None) -> int:
    """sensitive-info-check 独立 CLI 入口。"""
    setup_safe_output()

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        _simple_test()
        return 0

    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.path:
        project_root = Path(args.path).resolve()
    else:
        project_root = resolve_project_root(__file__)

    return run(project_root, args)


if __name__ == "__main__":
    sys.exit(main())
