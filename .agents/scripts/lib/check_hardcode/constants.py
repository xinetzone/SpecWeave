import re

HTTP_STATUS_CODES = {100, 101, 102, 103, 200, 201, 202, 203, 204, 205, 206, 207, 208, 226,
                     300, 301, 302, 303, 304, 305, 306, 307, 308,
                     400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413,
                     414, 415, 416, 417, 418, 421, 422, 423, 424, 425, 426, 428, 429, 431,
                     451, 500, 501, 502, 503, 504, 505, 506, 507, 508, 510, 511}
CONTROL_FLOW_NUMS = {-1, 0, 1, 2}
UNIT_CONVERSION_NUMS = {8, 16, 32, 64, 100, 128, 256, 512, 1000, 1024, 2048, 4096, 8192,
                        60, 3600, 86400}
SENTINEL_NUMS = {-1, 0, 1}

CHINESE_RE = re.compile(r'[\u4e00-\u9fff]')
FULL_EN_SENTENCE_RE = re.compile(r'^[A-Z][a-z]+(\s+[a-zA-Z]+){3,}[.!?]?$')
URL_RE = re.compile(r'^https?://[a-zA-Z0-9]')
LOCALHOST_RE = re.compile(r'^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0)(:\d+)?')
FULL_URL_RE = re.compile(r'^https?://[a-zA-Z0-9][a-zA-Z0-9.-]+(?::\d+)?(/|$)')
PATH_SEP_RE = re.compile(r'[/\\]')
FILE_EXT_RE = re.compile(r'\.\w{1,5}$')
HEX_COLOR_RE = re.compile(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')
CSS_UNIT_RE = re.compile(r'^\d+(\.\d+)?(px|em|rem|pt|vh|vw|%)$')
ENCODING_RE = re.compile(r'^(utf-?8|ascii|latin-?1|gbk|gb2312|utf-?16|utf-?32|big5)$', re.IGNORECASE)
MIME_RE = re.compile(r'^(text|application|image|audio|video|message|multipart)/[a-zA-Z0-9.+-]+(;\s*charset=\S+)?$')
REGEX_PREFIX_RE = re.compile(r'^r["\']')

LOGGING_CALLS = {"debug", "info", "warning", "error", "critical", "exception", "log", "warn"}
PRINT_LIKE = {"print"}
RAISE_CALLS = {"raise"}
TEST_LOCAL_VARS = {"expected", "result", "actual", "mock_data", "test_str", "sample"}
RA_ALLOWED_FUNCS = {"resolve_project_root", "resolve_agents_dir", "resolve_scripts_dir", "Path"}

SAFE_STRING_VALUES = {
    "", " ", "\n", "\t", "\r", ",", ".", ":", ";", "-", "_", "/", "\\",
    "|", "*", "?", "!", "@", "#", "$", "%", "^", "&", "(", ")", "[", "]",
    "{", "}", "<", ">", "=", "+", "~", "`",
    "utf-8", "utf8", "UTF-8", "UTF8",
    "r", "w", "a", "rb", "wb", "ab", "r+", "w+", "a+",
    ".", "..",
}
