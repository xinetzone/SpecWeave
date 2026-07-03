"""forum-bot 操作模块。

包含读帖、编辑、回复、草稿清理等具体业务操作。
"""

from .read import do_read
from .edit import do_edit
from .reply import do_reply
from .drafts import do_clean_drafts

__all__ = ["do_read", "do_edit", "do_reply", "do_clean_drafts"]
