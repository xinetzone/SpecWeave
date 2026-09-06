"""知乎知识库 API 客户端。

封装以下接口：
- 知识库列表 (knowledge_bases)
- 知识库内容列表 (knowledge_base_items)
- 知识库文件上传 (knowledge_file_upload)
- 知识库检索 (knowledge_search)
- 额度查询 (quota)
"""

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import httpx


# ── 数据结构 ──────────────────────────────────────────────


@dataclass
class KnowledgeBase:
    """知识库元数据。"""

    knowledge_base_id: str
    name: str
    description: str
    relation: str  # created / subscribed / both
    is_default: bool
    visibility: str  # private / public
    content_count: int
    updated_at: int


@dataclass
class KnowledgeItem:
    """知识库内容项。"""

    recall_content_id: str
    content_type: str  # unknown / file / answer / article
    title: str
    abstract: str
    created_at: int
    updated_at: int
    origin_url: str


@dataclass
class UploadResult:
    """文件上传结果。"""

    knowledge_base_id: str
    recall_content_id: str
    file_name: str
    file_size: int
    title: str
    abstract: str
    origin_url: str


@dataclass
class QuotaItem:
    """额度项。"""

    api_id: str
    api_name: str
    total_quota: int
    total_used: int
    remaining_quota: int


@dataclass
class SearchItem:
    """检索结果项。"""

    content: list[str]
    knowledge_base_id: str
    doc_name: str
    recall_content_id: str
    origin_url: str


class ZhihuApiError(Exception):
    """知乎 API 调用错误。"""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


# ── API 客户端 ──────────────────────────────────────────


class ZhihuKbApiClient:
    """知乎知识库 API 客户端。"""

    def __init__(
        self,
        access_secret: str,
        base_url: str = "https://developer.zhihu.com/api/v1",
        timeout: float = 30.0,
    ):
        self.access_secret = access_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    # ── 内部工具 ──────────────────────────────────────

    def _headers(self) -> dict[str, str]:
        """生成统一鉴权请求头。"""
        return {
            "Authorization": f"Bearer {self.access_secret}",
            "X-Request-Timestamp": str(int(time.time())),
        }

    def _check_response(self, resp: httpx.Response) -> dict[str, Any]:
        """检查响应并返回 Data 字段。"""
        resp.raise_for_status()
        body = resp.json()
        code = body.get("Code", -1)
        message = body.get("Message", "")
        if code != 0:
            raise ZhihuApiError(code, message)
        return body.get("Data", {})

    # ── 知识库列表 ────────────────────────────────────

    def list_knowledge_bases(self, scope: str = "all") -> list[KnowledgeBase]:
        """获取知识库列表。

        Args:
            scope: all / created / subscribed
        """
        resp = self._client.get(
            f"{self.base_url}/knowledge/bases",
            headers=self._headers(),
            params={"Scope": scope},
        )
        data = self._check_response(resp)
        items = data.get("Items", [])
        return [
            KnowledgeBase(
                knowledge_base_id=item["KnowledgeBaseID"],
                name=item["Name"],
                description=item.get("Description", ""),
                relation=item["Relation"],
                is_default=item.get("IsDefault", False),
                visibility=item["Visibility"],
                content_count=item.get("ContentCount", 0),
                updated_at=item.get("UpdatedAt", 0),
            )
            for item in items
        ]

    def get_default_kb_id(self) -> Optional[str]:
        """获取默认知识库 ID。"""
        for kb in self.list_knowledge_bases(scope="created"):
            if kb.is_default:
                return kb.knowledge_base_id
        return None

    # ── 知识库内容列表 ────────────────────────────────

    def list_knowledge_items(
        self,
        knowledge_base_id: str,
        limit: int = 20,
    ) -> tuple[list[KnowledgeItem], int, bool, str]:
        """获取知识库内容列表（第一页）。

        Returns:
            (items, total, has_more, next_cursor)
        """
        resp = self._client.get(
            f"{self.base_url}/knowledge/bases/{knowledge_base_id}/items",
            headers=self._headers(),
            params={"Limit": limit},
        )
        data = self._check_response(resp)
        items = [
            KnowledgeItem(
                recall_content_id=item.get("RecallContentID", ""),
                content_type=item.get("ContentType", "unknown"),
                title=item.get("Title", ""),
                abstract=item.get("Abstract", ""),
                created_at=item.get("CreatedAt", 0),
                updated_at=item.get("UpdatedAt", 0),
                origin_url=item.get("OriginUrl", ""),
            )
            for item in data.get("Items", [])
        ]
        return (
            items,
            data.get("Total", 0),
            data.get("HasMore", False),
            data.get("NextCursor", ""),
        )

    def list_all_knowledge_items(
        self, knowledge_base_id: str
    ) -> list[KnowledgeItem]:
        """分页获取知识库全部内容项。"""
        all_items: list[KnowledgeItem] = []
        cursor = ""
        while True:
            resp = self._client.get(
                f"{self.base_url}/knowledge/bases/{knowledge_base_id}/items",
                headers=self._headers(),
                params={"Limit": 20, "Cursor": cursor} if cursor else {"Limit": 20},
            )
            data = self._check_response(resp)
            for item in data.get("Items", []):
                all_items.append(
                    KnowledgeItem(
                        recall_content_id=item.get("RecallContentID", ""),
                        content_type=item.get("ContentType", "unknown"),
                        title=item.get("Title", ""),
                        abstract=item.get("Abstract", ""),
                        created_at=item.get("CreatedAt", 0),
                        updated_at=item.get("UpdatedAt", 0),
                        origin_url=item.get("OriginUrl", ""),
                    )
                )
            if not data.get("HasMore", False):
                break
            cursor = data.get("NextCursor", "")
            if not cursor:
                break
        return all_items

    # ── 文件上传 ──────────────────────────────────────

    def upload_file(
        self,
        file_path: Path,
        knowledge_base_id: Optional[str] = None,
    ) -> UploadResult:
        """上传文件到知识库。

        Args:
            file_path: 本地文件路径
            knowledge_base_id: 目标知识库 ID，None 则使用默认库
        """
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        with open(file_path, "rb") as f:
            files = {"File": (file_path.name, f)}
            data = {}
            if knowledge_base_id:
                data["KnowledgeBaseID"] = knowledge_base_id

            resp = self._client.post(
                f"{self.base_url}/knowledge/files",
                headers=self._headers(),
                files=files,
                data=data if data else None,
            )

        result = self._check_response(resp)
        return UploadResult(
            knowledge_base_id=result["KnowledgeBaseID"],
            recall_content_id=result["RecallContentID"],
            file_name=result["FileName"],
            file_size=result.get("FileSize", 0),
            title=result.get("Title", ""),
            abstract=result.get("Abstract", ""),
            origin_url=result.get("OriginUrl", ""),
        )

    # ── 检索 ──────────────────────────────────────────

    def search(
        self,
        query: str,
        knowledge_base_ids: Optional[list[str]] = None,
        recall_scopes: Optional[list[str]] = None,
        limit: int = 10,
    ) -> list[SearchItem]:
        """知识库 RAG 检索。

        knowledge_base_ids 和 recall_scopes 至少有一个非空。
        """
        if not knowledge_base_ids and not recall_scopes:
            raise ValueError("knowledge_base_ids 和 recall_scopes 至少有一个非空")

        body: dict[str, Any] = {"Query": query, "Limit": limit}
        if knowledge_base_ids:
            body["KnowledgeBaseIDs"] = knowledge_base_ids
        if recall_scopes:
            body["RecallScopes"] = recall_scopes

        resp = self._client.post(
            f"{self.base_url}/knowledge/search",
            headers={**self._headers(), "Content-Type": "application/json"},
            json=body,
        )
        data = self._check_response(resp)
        return [
            SearchItem(
                content=item.get("Content", []),
                knowledge_base_id=item["KnowledgeBaseID"],
                doc_name=item["DocName"],
                recall_content_id=item.get("RecallContentID", ""),
                origin_url=item.get("OriginUrl", ""),
            )
            for item in data.get("Items", [])
        ]

    # ── 额度查询 ──────────────────────────────────────

    def get_quota(self, api_ids: Optional[list[str]] = None) -> list[QuotaItem]:
        """查询额度。

        Args:
            api_ids: 要查询的 API ID 列表，None 则返回全部
        """
        params = {}
        if api_ids:
            params["APIIDs"] = ",".join(api_ids)

        resp = self._client.get(
            f"{self.base_url}/quota",
            headers=self._headers(),
            params=params if params else None,
        )
        data = self._check_response(resp)
        # 额度接口 Data 是数组
        items = data if isinstance(data, list) else data.get("Items", [])
        return [
            QuotaItem(
                api_id=item["APIID"],
                api_name=item["APIName"],
                total_quota=item.get("TotalQuota", 0),
                total_used=item.get("TotalUsed", 0),
                remaining_quota=item.get("RemainingQuota", 0),
            )
            for item in items
        ]

    def get_knowledge_quota(self) -> Optional[QuotaItem]:
        """获取 knowledge 额度池信息。"""
        for item in self.get_quota(["knowledge"]):
            if item.api_id == "knowledge":
                return item
        return None

    # ── 资源清理 ──────────────────────────────────────

    def close(self) -> None:
        """关闭 HTTP 客户端。"""
        self._client.close()

    def __enter__(self) -> "ZhihuKbApiClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
