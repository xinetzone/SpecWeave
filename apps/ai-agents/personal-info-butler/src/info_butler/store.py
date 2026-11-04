"""存储层：Supabase（PostgREST）优先，内存回退。

两条实现必须**行为等价**——否则「本地跑得好好的，接了云端就变样」会变成一类
最难排查的缺陷。因此对外的查询语义（过滤、排序、截断）在基类里定死，
两个子类只是把同样的语义翻译成不同方言：内存用 Python 过滤，云端用 PostgREST 查询串。

检索刻意**不在数据库侧做**：中文全文检索要配 zhparser/tsvector，而 Supabase 免费档
不一定装；关键词打分本来也要在应用层做二次排序。于是统一策略是
「按过滤条件取候选集 → 本地打分排序」，两条存储路径共用同一份打分代码。
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone

import httpx

from .config import Settings
from .http_client import http_client

ISO = "%Y-%m-%dT%H:%M:%S.%f%z"


def now_iso() -> str:
    """UTC 时间戳；统一由存储层生成，避免各调用点格式漂移。"""
    return datetime.now(timezone.utc).isoformat()


class StoreError(RuntimeError):
    """云端存储不可用。内存存储不会抛此异常。"""


class Store(ABC):
    """存储契约。"""

    #: ``"cloud"`` 或 ``"memory"``，直接暴露给前端徽标。
    mode: str = "memory"

    #: 实现名（``memory`` / ``supabase`` / ``workbuddy-cloud``）。
    #: 与 ``mode`` 分开是因为 mode 只回答「数据会不会丢」，
    #: backend 才回答「数据存在哪」——两者都要能被诊断接口读出来。
    backend: str = "memory"

    @abstractmethod
    def list_items(
        self,
        *,
        kind: str | None = None,
        tag: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """按过滤条件取候选集，按创建时间倒序。"""

    @abstractmethod
    def get_item(self, item_id: str) -> dict | None: ...

    @abstractmethod
    def create_item(self, item: dict) -> dict: ...

    @abstractmethod
    def update_item(self, item_id: str, patch: dict) -> dict | None: ...

    @abstractmethod
    def delete_item(self, item_id: str) -> bool: ...

    @abstractmethod
    def create_links(self, src_id: str, scored: list[dict]) -> list[dict]: ...

    @abstractmethod
    def list_links(self, item_id: str) -> list[dict]: ...

    @abstractmethod
    def list_summaries(self, limit: int = 10) -> list[dict]: ...

    @abstractmethod
    def create_summary(self, summary: dict) -> dict: ...


class MemoryStore(Store):
    """进程内存存储：零配置可用，重启即失。

    只用于本地体验与单元测试，**不承诺持久化**。
    """

    mode = "memory"
    backend = "memory"

    def __init__(self) -> None:
        self._items: dict[str, dict] = {}
        self._links: list[dict] = []
        self._summaries: list[dict] = []

    def _sorted(self) -> list[dict]:
        return sorted(
            self._items.values(), key=lambda it: it.get("created_at", ""), reverse=True
        )

    def list_items(
        self,
        *,
        kind: str | None = None,
        tag: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        rows = self._sorted()
        if kind:
            rows = [r for r in rows if r.get("kind") == kind]
        if status:
            rows = [r for r in rows if r.get("status") == status]
        if tag:
            rows = [r for r in rows if tag in (r.get("tags") or [])]
        return rows[:limit]

    def get_item(self, item_id: str) -> dict | None:
        return self._items.get(item_id)

    def create_item(self, item: dict) -> dict:
        record = dict(item)
        record.setdefault("id", uuid.uuid4().hex)
        record.setdefault("created_at", now_iso())
        record.setdefault("updated_at", record["created_at"])
        self._items[record["id"]] = record
        return record

    def update_item(self, item_id: str, patch: dict) -> dict | None:
        current = self._items.get(item_id)
        if current is None:
            return None
        current.update({k: v for k, v in patch.items() if v is not None})
        current["updated_at"] = now_iso()
        return current

    def delete_item(self, item_id: str) -> bool:
        if item_id not in self._items:
            return False
        del self._items[item_id]
        self._links = [
            ln for ln in self._links if ln["src_id"] != item_id and ln["dst_id"] != item_id
        ]
        return True

    def create_links(self, src_id: str, scored: list[dict]) -> list[dict]:
        created: list[dict] = []
        for entry in scored:
            link = {
                "id": uuid.uuid4().hex,
                "src_id": src_id,
                "dst_id": entry["id"],
                "score": entry.get("score", 0.0),
                "reason": entry.get("reason", ""),
                "created_at": now_iso(),
            }
            self._links.append(link)
            created.append(link)
        return created

    def list_links(self, item_id: str) -> list[dict]:
        return [
            ln for ln in self._links if ln["src_id"] == item_id or ln["dst_id"] == item_id
        ]

    def list_summaries(self, limit: int = 10) -> list[dict]:
        return sorted(
            self._summaries, key=lambda s: s.get("created_at", ""), reverse=True
        )[:limit]

    def create_summary(self, summary: dict) -> dict:
        record = dict(summary)
        record.setdefault("id", uuid.uuid4().hex)
        record.setdefault("created_at", now_iso())
        self._summaries.append(record)
        return record


class SupabaseStore(Store):
    """Supabase / PostgREST 存储。

    用 service role key 直连 REST 层，绕开客户端 SDK——本服务本身就是后端，
    再套一层 SDK 只会多一层要维护的依赖。
    """

    mode = "cloud"
    backend = "supabase"

    def __init__(self, settings: Settings):
        self._base = f"{settings.supabase_url}/rest/v1"
        self._timeout = settings.http_timeout
        self._headers = {
            "apikey": settings.supabase_key,
            "Authorization": f"Bearer {settings.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    def _request(self, method: str, path: str, **kwargs) -> list[dict]:
        url = f"{self._base}/{path}"
        try:
            with http_client(url, self._timeout) as client:
                response = client.request(method, url, headers=self._headers, **kwargs)
        except httpx.HTTPError as exc:  # pragma: no cover - 依赖外部网络
            raise StoreError(f"云端存储不可达：{exc}") from exc
        if response.status_code >= 400:
            raise StoreError(
                f"云端存储返回 {response.status_code}：{response.text[:200]}"
            )
        if not response.content:
            return []
        try:
            data = response.json()
        except ValueError as exc:
            raise StoreError("云端存储响应不是合法 JSON") from exc
        return data if isinstance(data, list) else [data]

    def list_items(
        self,
        *,
        kind: str | None = None,
        tag: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        params = ["select=*", "order=created_at.desc", f"limit={max(1, limit)}"]
        if kind:
            params.append(f"kind=eq.{kind}")
        if status:
            params.append(f"status=eq.{status}")
        if tag:
            params.append(f"tags=cs.{{{tag}}}")
        return self._request("GET", f"items?{'&'.join(params)}")

    def get_item(self, item_id: str) -> dict | None:
        rows = self._request("GET", f"items?id=eq.{item_id}&select=*&limit=1")
        return rows[0] if rows else None

    def create_item(self, item: dict) -> dict:
        record = dict(item)
        record.setdefault("created_at", now_iso())
        record.setdefault("updated_at", record["created_at"])
        rows = self._request("POST", "items", json=record)
        return rows[0] if rows else record

    def update_item(self, item_id: str, patch: dict) -> dict | None:
        body = {k: v for k, v in patch.items() if v is not None}
        if not body:
            return self.get_item(item_id)
        body["updated_at"] = now_iso()
        rows = self._request("PATCH", f"items?id=eq.{item_id}", json=body)
        return rows[0] if rows else None

    def delete_item(self, item_id: str) -> bool:
        self._request("DELETE", f"item_links?src_id=eq.{item_id}")
        self._request("DELETE", f"item_links?dst_id=eq.{item_id}")
        self._request("DELETE", f"items?id=eq.{item_id}")
        return True

    def create_links(self, src_id: str, scored: list[dict]) -> list[dict]:
        if not scored:
            return []
        payload = [
            {
                "src_id": src_id,
                "dst_id": entry["id"],
                "score": entry.get("score", 0.0),
                "reason": entry.get("reason", ""),
                "created_at": now_iso(),
            }
            for entry in scored
        ]
        return self._request("POST", "item_links", json=payload)

    def list_links(self, item_id: str) -> list[dict]:
        query = f"or=(src_id.eq.{item_id},dst_id.eq.{item_id})"
        return self._request("GET", f"item_links?select=*&{query}")

    def list_summaries(self, limit: int = 10) -> list[dict]:
        return self._request(
            "GET", f"summaries?select=*&order=created_at.desc&limit={max(1, limit)}"
        )

    def create_summary(self, summary: dict) -> dict:
        record = dict(summary)
        record.setdefault("created_at", now_iso())
        rows = self._request("POST", "summaries", json=record)
        return rows[0] if rows else record


class WorkBuddyCloudStore(Store):
    """WorkBuddy 云服务（托管 PostgreSQL / PostgREST）存储。

    与 :class:`SupabaseStore` 的差异是**协议级**的，不是配置差异：

    - 数据面路径是 ``/.cloud/database/rest/<table>``（不是 ``/rest/v1/``）；
    - 鉴权头是 ``x-wb-webapp-access-key``，且 publishableKey **只能**放这个头，
      不能当 Bearer 令牌用；
    - 列级授权是「全有或全无」：请求列清单里只要有 1 列未授权，整表报
      ``42501``（不是「少一列」）。因此这里的 ``select=*`` 必须与云端
      授权的列集合严格对齐。

    这些差异无法通过参数化复用 Supabase 的实现，故独立成类；但**对外查询
    语义**（过滤、排序、截断）与另两种实现保持一致，由基类定义。
    """

    mode = "cloud"
    backend = "workbuddy-cloud"

    def __init__(self, settings: Settings):
        self._base = f"{settings.wb_cloud_endpoint.rstrip('/')}/.cloud/database/rest"
        self._timeout = settings.http_timeout
        self._headers = {
            "x-wb-webapp-access-key": settings.wb_publishable_key,
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    def _request(self, method: str, path: str, **kwargs) -> list[dict]:
        url = f"{self._base}/{path}"
        try:
            with http_client(url, self._timeout) as client:
                response = client.request(method, url, headers=self._headers, **kwargs)
        except httpx.HTTPError as exc:  # pragma: no cover - 依赖外部网络
            raise StoreError(f"云端存储不可达：{exc}") from exc
        if response.status_code >= 400:
            raise StoreError(
                f"云端存储返回 {response.status_code}：{response.text[:200]}"
            )
        if not response.content:
            return []
        try:
            data = response.json()
        except ValueError as exc:
            raise StoreError("云端存储响应不是合法 JSON") from exc
        return data if isinstance(data, list) else [data]

    def list_items(
        self,
        *,
        kind: str | None = None,
        tag: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        params = ["select=*", "order=created_at.desc", f"limit={max(1, limit)}"]
        if kind:
            params.append(f"kind=eq.{kind}")
        if status:
            params.append(f"status=eq.{status}")
        if tag:
            params.append(f"tags=cs.{{{tag}}}")
        return self._request("GET", f"items?{'&'.join(params)}")

    def get_item(self, item_id: str) -> dict | None:
        rows = self._request("GET", f"items?id=eq.{item_id}&select=*&limit=1")
        return rows[0] if rows else None

    def create_item(self, item: dict) -> dict:
        record = dict(item)
        record.setdefault("created_at", now_iso())
        record.setdefault("updated_at", record["created_at"])
        rows = self._request("POST", "items", json=record)
        return rows[0] if rows else record

    def update_item(self, item_id: str, patch: dict) -> dict | None:
        body = {k: v for k, v in patch.items() if v is not None}
        if not body:
            return self.get_item(item_id)
        body["updated_at"] = now_iso()
        rows = self._request("PATCH", f"items?id=eq.{item_id}", json=body)
        return rows[0] if rows else None

    def delete_item(self, item_id: str) -> bool:
        self._request("DELETE", f"item_links?src_id=eq.{item_id}")
        self._request("DELETE", f"item_links?dst_id=eq.{item_id}")
        self._request("DELETE", f"items?id=eq.{item_id}")
        return True

    def create_links(self, src_id: str, scored: list[dict]) -> list[dict]:
        if not scored:
            return []
        payload = [
            {
                "src_id": src_id,
                "dst_id": entry["id"],
                "score": entry.get("score", 0.0),
                "reason": entry.get("reason", ""),
                "created_at": now_iso(),
            }
            for entry in scored
        ]
        return self._request("POST", "item_links", json=payload)

    def list_links(self, item_id: str) -> list[dict]:
        query = f"or=(src_id.eq.{item_id},dst_id.eq.{item_id})"
        return self._request("GET", f"item_links?select=*&{query}")

    def list_summaries(self, limit: int = 10) -> list[dict]:
        return self._request(
            "GET", f"summaries?select=*&order=created_at.desc&limit={max(1, limit)}"
        )

    def create_summary(self, summary: dict) -> dict:
        record = dict(summary)
        record.setdefault("created_at", now_iso())
        rows = self._request("POST", "summaries", json=record)
        return rows[0] if rows else record


def create_store(settings: Settings) -> Store:
    """按配置可用性选择存储。

    优先级：WorkBuddy 云服务 > Supabase > 内存。
    WorkBuddy 云服务排在最前，是因为它是平台托管环境——同一份代码在平台上
    跑时，平台注入的 ``WB_CLOUD_*`` 变量应该直接生效，而不是被本机残留的
    Supabase 变量截胡。
    """
    if settings.wb_cloud_ready:
        return WorkBuddyCloudStore(settings)
    if settings.cloud_ready:
        return SupabaseStore(settings)
    return MemoryStore()
