"""API 输入输出模型。

约束与 :mod:`info_butler.config` 同源：**宽松**。只有 ``content`` 是必填，
其余全部可空——录入界面只有一个文本框，逼用户先想清楚"这是想法还是资料"
本身就违背"随手记"的产品前提。
"""

from pydantic import BaseModel, Field

KIND_IDEA = "idea"
KIND_MATERIAL = "material"
KIND_TODO = "todo"
KINDS = (KIND_IDEA, KIND_MATERIAL, KIND_TODO)

STATUS_OPEN = "open"
STATUS_DONE = "done"
STATUS_ARCHIVED = "archived"
STATUSES = (STATUS_OPEN, STATUS_DONE, STATUS_ARCHIVED)


class ItemIn(BaseModel):
    """录入请求。``kind`` 留空表示交给模型/启发式判定。"""

    content: str = Field(min_length=1, max_length=8000)
    kind: str | None = None
    title: str | None = None
    tags: list[str] = Field(default_factory=list)
    source: str = "web"


class ItemPatch(BaseModel):
    """局部更新：只传需要改的字段。"""

    title: str | None = None
    content: str | None = None
    summary: str | None = None
    kind: str | None = None
    tags: list[str] | None = None
    status: str | None = None
    priority: int | None = None
    due_date: str | None = None


class AskIn(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    limit: int = 8


class ExtractIn(BaseModel):
    limit: int = 40
    scope: str = "recent"


class SummaryIn(BaseModel):
    days: int = 7
    limit: int = 200
