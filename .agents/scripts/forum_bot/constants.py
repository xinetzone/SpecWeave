"""forum-bot 常量定义。

包含URL、超时配置、CSS选择器、ANSI颜色码、AI发布声明文本等。
"""

from __future__ import annotations


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

from pathlib import Path

FORUM_URL = "https://" + "forum.trae.cn"
STATE_FILE = Path(__file__).resolve().parent.parent / "config" / "forum-state.json"

DEFAULT_WAIT = 2000
ACTION_DELAY = 3
ELEMENT_TIMEOUT = 8000
RETRY_MAX = 2

AI_NOTICE_KEYWORD = "本文由 AI 智能体协助撰写"
AI_NOTICE_TEXT = (
    "---\n\n"
    "> 🤖 **本文由 AI 智能体协助撰写与发布** "
    "| 内容经人工审核确认，观点归属作者本人。\n\n"
    "---\n\n"
)

ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RED = "\033[91m"
ANSI_CYAN = "\033[96m"
ANSI_BOLD = "\033[1m"
ANSI_GREY = "\033[90m"
ANSI_RESET = "\033[0m"

SELECTOR_COOKED = ".cooked"
SELECTOR_EDITOR_TEXTAREA = "textarea.d-editor-input"
SELECTOR_EDIT_BTN = ".post-action-menu__edit"
SELECTOR_SAVE_BTN = "button.btn-primary"
SELECTOR_REMOVE_DRAFT = ".remove-draft"
SELECTOR_USER_AVATAR = 'a[href^="/u/"]'

