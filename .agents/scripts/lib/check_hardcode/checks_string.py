import ast
import re

from .constants import (
    CHINESE_RE, FULL_EN_SENTENCE_RE, FULL_URL_RE, LOCALHOST_RE,
    PATH_SEP_RE, FILE_EXT_RE, HEX_COLOR_RE, CSS_UNIT_RE,
    ENCODING_RE, MIME_RE, SAFE_STRING_VALUES, RA_ALLOWED_FUNCS,
)


class StringChecksMixin:
    def _check_string_arg(self, arg, category: str, message: str, severity: str = "warn"):
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            val = arg.value
            if self._is_safe_string(val):
                return
            if CHINESE_RE.search(val) or (len(val) > 20 and FULL_EN_SENTENCE_RE.match(val)):
                self.issues.append(self._make_issue(
                    category=category,
                    severity=severity,
                    message=message + f"：「{val[:50]}」",
                    line=arg.lineno if hasattr(arg, 'lineno') else 0,
                ))
        elif isinstance(arg, ast.JoinedStr):
            for val in arg.values:
                if isinstance(val, ast.Constant) and isinstance(val.value, str):
                    if CHINESE_RE.search(val.value):
                        self.issues.append(self._make_issue(
                            category=category,
                            severity=severity,
                            message=message + f"：f-string中文片段「{val.value[:30]}」",
                            line=arg.lineno if hasattr(arg, 'lineno') else 0,
                        ))

    def _check_string_value(self, value_node, category: str, message: str):
        if isinstance(value_node, ast.Constant) and isinstance(value_node.value, str):
            val = value_node.value
            if self._is_safe_string(val):
                return
            if category == "HARD-URL":
                if not FULL_URL_RE.match(val):
                    return
                if LOCALHOST_RE.match(val):
                    return
                if any(kw in self.function_name.lower() for kw in ["test", "mock", "fake", "demo"]):
                    return
                if re.match(r'^https?://(test|mock|fake|dummy|sample|localhost|127\.0\.0\.1|0\.0\.0\.0)[:/]', val):
                    return
            if category == "HARD-PATH":
                if not PATH_SEP_RE.search(val):
                    return
                is_absolute = val.startswith("/") or val.startswith("\\") or re.match(r'^[a-zA-Z]:[\\/]', val)
                is_project_relative = re.match(r'^(docs|lib|vendor|\.agents|scripts|config|templates|skills|commands|rules|protocols|workflows|roles|modules|teams|capabilities|worlds|cases|prompts|tools|generated|src|tests|output)[/\\]', val)
                if val.startswith(".") or is_project_relative:
                    sev = "warn" if not is_absolute else "error"
                    msg = message + "（项目相对路径，建议使用Path拼接）" if is_project_relative else message
                elif not is_absolute:
                    return
                else:
                    sev = "error"
                    msg = message
                self._add_issue(
                    category=category,
                    severity=sev,
                    message=msg + f"：「{val[:60]}」",
                    line=value_node.lineno,
                    snippet=self._get_snippet(value_node.lineno),
                )
                return
            self._add_issue(
                category=category,
                severity="error" if category in {"HARD-URL", "HARD-PATH"} else "warn",
                message=message + f"：「{val[:60]}」",
                line=value_node.lineno,
                snippet=self._get_snippet(value_node.lineno),
            )

    def _is_safe_string(self, val: str) -> bool:
        if not val:
            return True
        if val in SAFE_STRING_VALUES:
            return True
        if ENCODING_RE.match(val) or MIME_RE.match(val):
            return False
        if val.startswith("**") and val.endswith("**"):
            return True
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', val):
            return True
        return False

    def _check_string_constant(self, val: str, line_no: int, snippet: str):
        if self.in_test_function:
            return
        if self._is_safe_string(val):
            return

        if FULL_URL_RE.match(val):
            if LOCALHOST_RE.match(val):
                return
            if val.startswith("http://") and not any(c.isalnum() for c in val[7:]):
                return
            if any(kw in self.function_name.lower() for kw in ["test", "mock", "fake", "demo"]):
                return
            if re.match(r'^https?://(test|mock|fake|dummy|sample|localhost|127\.0\.0\.1|0\.0\.0\.0)[:/]', val):
                return
            if self._already_reported(line_no, "HARD-URL"):
                return
            self._add_issue(
                category="HARD-URL",
                severity="error",
                message=f"硬编码URL端点：「{val[:80]}」",
                line=line_no,
                snippet=snippet,
            )
            return

        if len(val) > 2 and PATH_SEP_RE.search(val) and FILE_EXT_RE.search(val):
            if any(name in snippet for name in RA_ALLOWED_FUNCS):
                return
            if val.startswith("."):
                return
            is_absolute = val.startswith("/") or val.startswith("\\") or re.match(r'^[a-zA-Z]:[\\/]', val)
            has_chinese = CHINESE_RE.search(val)
            is_user_agent = "Mozilla/" in val or "AppleWebKit" in val
            is_gitignore_entry = re.match(r'^[*#\[\]!]', val) or val.endswith("/")
            is_project_relative = re.match(r'^(docs|lib|vendor|\.agents|scripts|config|templates|skills|commands|rules|protocols|workflows|roles|modules|teams|capabilities|worlds|cases|prompts|tools|generated|src|tests|output)[/\\]', val)
            is_prompt_text = has_chinese and len(val) > 30
            is_fstring_fragment = self.in_fstring and val.startswith("/") and not re.match(r'^/(etc|usr|home|var|tmp|opt|root|proc|sys|dev|bin|sbin|lib|lib64|boot|mnt|media|srv|run|Applications|Users|System|Windows|Program)[/\\]', val)
            if is_user_agent or is_gitignore_entry or is_project_relative or is_prompt_text or is_fstring_fragment:
                return
            if not is_absolute:
                return
            if self._already_reported(line_no, "HARD-PATH"):
                return
            self._add_issue(
                category="HARD-PATH",
                severity="error",
                message=f"硬编码文件路径：「{val[:80]}」",
                line=line_no,
                snippet=snippet,
            )
            return

        if ENCODING_RE.match(val) or MIME_RE.match(val):
            self.issues.append(self._make_issue(
                category="HARD-ENC",
                severity="warn",
                message=f"硬编码编码/MIME值：「{val}」——建议抽取为常量统一管理",
                line=line_no,
                snippet=snippet,
            ))
            return

        if HEX_COLOR_RE.match(val):
            self.issues.append(self._make_issue(
                category="HARD-STYLE",
                severity="warn",
                message=f"硬编码颜色值：「{val}」——建议使用设计令牌/主题变量",
                line=line_no,
                snippet=snippet,
            ))
            return

        if CSS_UNIT_RE.match(val):
            self.issues.append(self._make_issue(
                category="HARD-STYLE",
                severity="warn",
                message=f"硬编码样式值：「{val}」——建议使用设计系统变量",
                line=line_no,
                snippet=snippet,
            ))
            return

        if CHINESE_RE.search(val):
            context = snippet[:30]
            is_log = any(kw in context for kw in ["log", "print", "raise", "error", "warn", "info", "debug"])
            severity = "warn"
            msg = f"硬编码中文字符串：「{val[:50]}」"
            if is_log and not self.in_test_function:
                msg += "（建议外部化到消息字典/i18n资源）"
            elif self.in_test_function:
                return
            self.issues.append(self._make_issue(
                category="HARD-STR",
                severity=severity,
                message=msg,
                line=line_no,
                snippet=snippet,
            ))
            return

        if FULL_EN_SENTENCE_RE.match(val) and len(val) > 15:
            self.issues.append(self._make_issue(
                category="HARD-STR",
                severity="warn",
                message=f"硬编码英文字符串：「{val[:60]}」",
                line=line_no,
                snippet=snippet,
            ))
