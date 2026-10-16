"""数据仓储：Supabase（PostgREST）为主，内存为降级实现。

设计要点（对应 spec FR-2~FR-5、FR-7、AC-3~AC-8）：
- 表名/列名/排序字段一律走白名单映射，过滤值一律 `urlencode`，杜绝 PostgREST 注入。
- 云端不可达即切内存仓储并置 `degraded`，功能仍可演示，绝不抛未捕获异常。
- 写操作统一落审计日志；删除前做引用计数检查。
"""

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlencode

from .config import Config
from .http_client import request
from .security import hash_password, verify_password
from .validate import STATUSES, clean_page, clean_sort, clean_tags

ADMIN_ROLES = ("admin", "editor")

#: 表白名单——任何进入 URL 的表名必须在此集合内。
TABLES = (
    "ac_admins",
    "ac_categories",
    "ac_tags",
    "ac_items",
    "ac_item_tags",
    "ac_attachments",
    "ac_audit_logs",
)


class Conflict(Exception):
    """业务冲突（引用占用 / 乐观并发失败），映射为 HTTP 409。"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def new_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _first(row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    return row if isinstance(row, dict) else None


class SupabaseStore:
    """Supabase PostgREST 仓储。"""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.degraded = False

    # ---- 底层 ---------------------------------------------------------

    def _headers(self, prefer: str = "") -> Dict[str, str]:
        headers = {
            "apikey": self.cfg.supabase_service_role_key,
            "authorization": f"Bearer {self.cfg.supabase_service_role_key}",
            "accept": "application/json",
        }
        if prefer:
            headers["prefer"] = prefer
        return headers

    def _call(
        self,
        method: str,
        table: str,
        params: Optional[List[Tuple[str, str]]] = None,
        body: Optional[bytes] = None,
        prefer: str = "",
    ) -> Tuple[int, Dict[str, str], Any]:
        if table not in TABLES:
            raise ValueError(f"未知表名：{table}")
        url = f"{self.cfg.rest_base}/{table}"
        query = urlencode(params or [], encoding="utf-8")
        if query:
            url = f"{url}?{query}"
        headers = self._headers(prefer)
        if body is not None:
            headers["content-type"] = "application/json"
        resp = request(method, url, headers=headers, body=body,
                       timeout=self.cfg.http_timeout, retries=self.cfg.http_retries)
        if resp.status == 0:
            self.degraded = True
        return resp.status, resp.headers, resp.json()

    def _rows(self, table: str, params: List[Tuple[str, str]], with_count: bool = False) -> Tuple[List[Dict], int]:
        prefer = "count=exact" if with_count else ""
        status, headers, payload = self._call("GET", table, params, prefer=prefer)
        rows = payload if isinstance(payload, list) else []
        total = len(rows)
        if with_count:
            range_header = headers.get("content-range") or ""
            if "/" in range_header:
                try:
                    total = int(range_header.rsplit("/", 1)[1])
                except ValueError:
                    total = len(rows)
        return rows, (total if status == 200 else len(rows))

    def _insert(self, table: str, row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        _, _, payload = self._call("POST", table, body=json.dumps(row, ensure_ascii=False).encode("utf-8"),
                                   prefer="return=representation")
        if isinstance(payload, list):
            return _first(payload[0] if payload else None)
        return _first(payload)

    def _update(self, table: str, filters: List[Tuple[str, str]], patch: Dict[str, Any]) -> List[Dict[str, Any]]:
        _, _, payload = self._call("PATCH", table, filters,
                                   body=json.dumps(patch, ensure_ascii=False).encode("utf-8"),
                                   prefer="return=representation")
        return payload if isinstance(payload, list) else []

    def _delete(self, table: str, filters: List[Tuple[str, str]]) -> None:
        self._call("DELETE", table, filters)

    def _count(self, table: str, filters: List[Tuple[str, str]]) -> int:
        _, total = self._rows(table, [("select", "id"), *filters], with_count=True)
        return total

    # ---- 健康 ---------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        if not self.cfg.cloud_ready:
            return {"mode": "memory", "degraded": True, "detail": "未配置 SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY"}
        _, total = self._rows("ac_items", [("select", "id"), ("limit", "1")], with_count=True)
        if self.degraded:
            return {"mode": "memory", "degraded": True, "detail": "云端不可达，已降级为内存仓储"}
        return {"mode": "supabase", "degraded": False, "detail": "", "reachable": True, "sampled": total >= 0}

    # ---- 管理员 -------------------------------------------------------

    def admin_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        rows, _ = self._rows("ac_admins", [("select", "*"), ("email", f"eq.{email.lower()}"), ("limit", "1")])
        return _first(rows[0] if rows else None)

    def create_admin(self, email: str, password: str, display_name: str = "", role: str = "admin") -> Dict[str, Any]:
        salt, digest = hash_password(password)
        row = {
            "id": new_id(),
            "email": email.lower(),
            "password_hash": digest,
            "salt": salt,
            "display_name": display_name or email.split("@")[0],
            "role": role if role in ADMIN_ROLES else "admin",
            "created_at": now_iso(),
            "last_login_at": "",
        }
        saved = self._insert("ac_admins", row)
        return saved or row

    def count_admins(self) -> int:
        return self._count("ac_admins", [])

    def touch_login(self, admin_id: str) -> None:
        self._update("ac_admins", [("id", f"eq.{admin_id}")], {"last_login_at": now_iso()})

    def verify_credentials(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        admin = self.admin_by_email(email)
        if not admin:
            # 恒定开销：避免通过响应时间枚举账号是否存在
            verify_password(password, "00" * 16, "00" * 32)
            return None
        if not verify_password(password, str(admin.get("salt") or ""), str(admin.get("password_hash") or "")):
            return None
        return admin

    # ---- 分类 / 标签 ---------------------------------------------------

    def list_categories(self) -> List[Dict[str, Any]]:
        rows, _ = self._rows("ac_categories", [("select", "*"), ("order", "sort_order.asc"), ("limit", "200")])
        return rows

    def create_category(self, data: Dict[str, Any]) -> Dict[str, Any]:
        row = {
            "id": new_id(),
            "name": data["name"],
            "slug": data["slug"],
            "sort_order": int(data.get("sort_order") or 100),
            "created_at": now_iso(),
        }
        return self._insert("ac_categories", row) or row

    def update_category(self, category_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        patch = {k: v for k, v in data.items() if k in ("name", "slug", "sort_order")}
        if not patch:
            return None
        rows = self._update("ac_categories", [("id", f"eq.{category_id}")], patch)
        return _first(rows[0] if rows else None)

    def delete_category(self, category_id: str) -> None:
        used = self._count("ac_items", [("category_id", f"eq.{category_id}")])
        if used:
            raise Conflict(f"该分类下仍有 {used} 条内容，请先迁移或删除")
        self._delete("ac_categories", [("id", f"eq.{category_id}")])

    def list_tags(self) -> List[Dict[str, Any]]:
        rows, _ = self._rows("ac_tags", [("select", "*"), ("order", "name.asc"), ("limit", "500")])
        return rows

    def create_tag(self, data: Dict[str, Any]) -> Dict[str, Any]:
        existing, _ = self._rows("ac_tags", [("select", "*"), ("name", f"eq.{data['name']}"), ("limit", "1")])
        if existing:
            return existing[0]
        row = {"id": new_id(), "name": data["name"], "slug": data["slug"], "created_at": now_iso()}
        return self._insert("ac_tags", row) or row

    def delete_tag(self, tag_id: str) -> None:
        used = self._count("ac_item_tags", [("tag_id", f"eq.{tag_id}")])
        if used:
            raise Conflict(f"该标签仍被 {used} 条内容引用，请先移除引用")
        self._delete("ac_tags", [("id", f"eq.{tag_id}")])

    # ---- 条目 ---------------------------------------------------------

    def _attach_tags(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not items:
            return items
        ids = [str(row.get("id")) for row in items if row.get("id")]
        if not ids:
            return items
        tags = {str(t.get("id")): str(t.get("name") or "") for t in self.list_tags()}
        links, _ = self._rows("ac_item_tags", [("select", "item_id,tag_id"), ("item_id", f"in.({','.join(ids)})")])
        bucket: Dict[str, List[str]] = {}
        for link in links:
            name = tags.get(str(link.get("tag_id")))
            if name:
                bucket.setdefault(str(link.get("item_id")), []).append(name)
        for row in items:
            row["tags"] = sorted(bucket.get(str(row.get("id")), []))
        return items

    def list_items(self, params: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], int]:
        page, size = clean_page(params.get("page"), params.get("page_size"),
                                self.cfg.page_size, self.cfg.max_page_size)
        sort_field, order = clean_sort(params.get("sort"), params.get("order"))
        filters: List[Tuple[str, str]] = [("select", "*")]

        keyword = str(params.get("q") or "").strip()
        if keyword:
            like = f"*.{keyword}.*"
            filters.append(("or", f"(title.ilike.{like},summary.ilike.{like},body.ilike.{like},slug.ilike.{like})"))
        status = str(params.get("status") or "").strip().lower()
        if status in STATUSES:
            filters.append(("status", f"eq.{status}"))
        category_id = str(params.get("category_id") or "").strip()
        if category_id == "__none__":
            filters.append(("category_id", "is.null"))
        elif category_id:
            filters.append(("category_id", f"eq.{category_id}"))
        tag = str(params.get("tag") or "").strip()
        if tag:
            matched, _ = self._rows("ac_tags", [("select", "id"), ("name", f"eq.{tag}"), ("limit", "1")])
            if not matched:
                return [], 0
            tag_id = str(matched[0].get("id"))
            links, _ = self._rows("ac_item_tags", [("select", "item_id"), ("tag_id", f"eq.{tag_id}"), ("limit", "500")])
            item_ids = [str(x.get("item_id")) for x in links]
            if not item_ids:
                return [], 0
            filters.append(("id", f"in.({','.join(item_ids)})"))

        rows, total = self._rows(
            "ac_items",
            [*filters, ("order", f"{sort_field}.{order}"), ("offset", str((page - 1) * size)), ("limit", str(size))],
            with_count=True,
        )
        return self._attach_tags(rows), total

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        rows, _ = self._rows("ac_items", [("select", "*"), ("id", f"eq.{item_id}"), ("limit", "1")])
        if not rows:
            return None
        return self._attach_tags(rows)[0]

    def create_item(self, data: Dict[str, Any], actor: str = "") -> Dict[str, Any]:
        stamp = now_iso()
        row = {
            "id": new_id(),
            "title": data["title"],
            "slug": data.get("slug") or "",
            "summary": data.get("summary") or "",
            "body": data.get("body") or "",
            "status": data.get("status") or "draft",
            "category_id": data.get("category_id") or None,
            "cover_url": data.get("cover_url") or "",
            "published_at": stamp if data.get("status") == "published" else None,
            "created_by": actor,
            "created_at": stamp,
            "updated_at": stamp,
        }
        saved = self._insert("ac_items", row) or row
        self._set_item_tags(str(saved.get("id")), data.get("tags") or [])
        self.add_log(actor, "create", str(saved.get("id")), f"新建内容「{row['title']}」")
        saved["tags"] = sorted(data.get("tags") or [])
        return saved

    def update_item(self, item_id: str, data: Dict[str, Any], actor: str = "",
                    expected_updated_at: str = "") -> Optional[Dict[str, Any]]:
        current = self.get_item(item_id)
        if not current:
            return None
        if expected_updated_at and str(current.get("updated_at") or "") != expected_updated_at:
            raise Conflict("内容已被其他会话修改，请刷新后重试")
        patch: Dict[str, Any] = {}
        for key in ("title", "slug", "summary", "body", "status", "category_id", "cover_url"):
            if key in data:
                patch[key] = data[key]
        if data.get("status") == "published" and not current.get("published_at"):
            patch["published_at"] = now_iso()
        patch["updated_at"] = now_iso()
        rows = self._update("ac_items", [("id", f"eq.{item_id}")], patch)
        saved = _first(rows[0] if rows else None) or {**current, **patch}
        if "tags" in data:
            self._set_item_tags(item_id, data.get("tags") or [])
        self.add_log(actor, "update", item_id, f"更新内容「{saved.get('title', '')}」")
        saved["tags"] = sorted(data.get("tags") or []) if "tags" in data else current.get("tags", [])
        return saved

    def delete_item(self, item_id: str, actor: str = "") -> bool:
        current = self.get_item(item_id)
        self._delete("ac_item_tags", [("item_id", f"eq.{item_id}")])
        self._delete("ac_items", [("id", f"eq.{item_id}")])
        self.add_log(actor, "delete", item_id, f"删除内容「{(current or {}).get('title', '')}」")
        return True

    def bulk_update(self, ids: List[str], action: str, actor: str = "") -> int:
        if action == "delete":
            for item_id in ids:
                self.delete_item(item_id, actor)
            return len(ids)
        if action in STATUSES:
            patch: Dict[str, Any] = {"status": action, "updated_at": now_iso()}
            if action == "published":
                patch["published_at"] = now_iso()
            self._update("ac_items", [("id", f"in.({','.join(ids)})")], patch)
            self.add_log(actor, "bulk", "", f"批量{action} {len(ids)} 条内容")
            return len(ids)
        raise Conflict(f"不支持的批量动作：{action}")

    def _set_item_tags(self, item_id: str, names: Iterable[str]) -> None:
        self._delete("ac_item_tags", [("item_id", f"eq.{item_id}")])
        for name in clean_tags(list(names)):
            tag = self.create_tag({"name": name, "slug": name})
            self._insert("ac_item_tags", {"item_id": item_id, "tag_id": str(tag.get("id"))})

    # ---- 附件 ---------------------------------------------------------

    def list_attachments(self, item_id: str = "") -> List[Dict[str, Any]]:
        filters: List[Tuple[str, str]] = [("select", "*"), ("order", "created_at.desc"), ("limit", "200")]
        if item_id:
            filters.append(("item_id", f"eq.{item_id}"))
        rows, _ = self._rows("ac_attachments", filters)
        return rows

    def add_attachment(self, meta: Dict[str, Any], actor: str = "") -> Dict[str, Any]:
        row = {
            "id": new_id(),
            "item_id": meta.get("item_id") or None,
            "filename": meta["filename"],
            "path": meta["path"],
            "url": meta["url"],
            "content_type": meta.get("content_type") or "application/octet-stream",
            "size": int(meta.get("size") or 0),
            "created_by": actor,
            "created_at": now_iso(),
        }
        self.add_log(actor, "upload", str(row["id"]), f"上传附件「{row['filename']}」")
        return self._insert("ac_attachments", row) or row

    def get_attachment(self, attachment_id: str) -> Optional[Dict[str, Any]]:
        rows, _ = self._rows("ac_attachments", [("select", "*"), ("id", f"eq.{attachment_id}"), ("limit", "1")])
        return _first(rows[0] if rows else None)

    def delete_attachment(self, attachment_id: str, actor: str = "") -> Optional[Dict[str, Any]]:
        row = self.get_attachment(attachment_id)
        if not row:
            return None
        self._delete("ac_attachments", [("id", f"eq.{attachment_id}")])
        self.add_log(actor, "delete_file", attachment_id, f"删除附件「{row.get('filename', '')}」")
        return row

    # ---- 日志与看板 -----------------------------------------------------

    def add_log(self, actor: str, action: str, target: str, detail: str = "") -> None:
        self._insert("ac_audit_logs", {
            "id": new_id(),
            "actor": actor or "system",
            "action": action,
            "target": target,
            "detail": detail,
            "created_at": now_iso(),
        })

    def list_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        rows, _ = self._rows("ac_audit_logs", [("select", "*"), ("order", "created_at.desc"),
                                               ("limit", str(max(min(limit, 100), 1)))])
        return rows

    def dashboard(self) -> Dict[str, Any]:
        by_status = {status: self._count("ac_items", [("status", f"eq.{status}")]) for status in STATUSES}
        total = sum(by_status.values())
        categories = self.list_categories()
        by_category = []
        for category in categories[:8]:
            count = self._count("ac_items", [("category_id", f"eq.{category['id']}")])
            by_category.append({"id": category["id"], "name": category.get("name", ""), "count": count})

        since = (datetime.now(timezone.utc) - timedelta(days=13)).date().isoformat()
        recent, _ = self._rows("ac_items", [("select", "created_at"), ("created_at", f"gte.{since}"),
                                            ("limit", "5000")])
        buckets: Dict[str, int] = {}
        for index in range(14):
            day = (datetime.now(timezone.utc) - timedelta(days=13 - index)).date().isoformat()
            buckets[day] = 0
        for row in recent:
            day = str(row.get("created_at") or "")[:10]
            if day in buckets:
                buckets[day] += 1
        trend = [{"date": day, "count": count} for day, count in sorted(buckets.items())]

        attachments, _ = self._rows("ac_attachments", [("select", "size"), ("limit", "5000")])
        total_bytes = sum(int(row.get("size") or 0) for row in attachments)

        return {
            "total": total,
            "by_status": by_status,
            "by_category": by_category,
            "trend": trend,
            "attachments": {"count": len(attachments), "bytes": total_bytes},
            "categories": len(categories),
            "tags": self._count("ac_tags", []),
            "logs": self.list_logs(10),
        }


class MemoryStore:
    """内存仓储：云端未配置或不可达时的降级实现（不持久化，仅演示）。"""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.degraded = True
        self.admins: Dict[str, Dict[str, Any]] = {}
        self.categories: Dict[str, Dict[str, Any]] = {}
        self.tags: Dict[str, Dict[str, Any]] = {}
        self.items: Dict[str, Dict[str, Any]] = {}
        self.item_tags: Dict[str, set] = {}
        self.attachments: Dict[str, Dict[str, Any]] = {}
        self.logs: List[Dict[str, Any]] = []
        self._seed()

    def _seed(self) -> None:
        stamp = now_iso()
        for name in ("未分类", "资讯", "教程"):
            cid = new_id()
            self.categories[cid] = {"id": cid, "name": name, "slug": name, "sort_order": 100, "created_at": stamp}
        sample_tags = ["示例", "草稿素材"]
        tag_ids = []
        for name in sample_tags:
            tid = new_id()
            self.tags[tid] = {"id": tid, "name": name, "slug": name, "created_at": stamp}
            tag_ids.append(tid)
        first_category = next(iter(self.categories), None)
        for index in range(1, 4):
            iid = new_id()
            self.items[iid] = {
                "id": iid,
                "title": f"示例内容 {index}",
                "slug": f"sample-{index}",
                "summary": "这是内存降级模式下的示例内容，配置 Supabase 后将替换为云端数据。",
                "body": "在 Supabase 控制台执行 schema.sql 并配置 SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 后，这里会显示真实云端数据。",
                "status": "published" if index % 2 else "draft",
                "category_id": first_category,
                "cover_url": "",
                "published_at": stamp if index % 2 else None,
                "created_by": "demo",
                "created_at": stamp,
                "updated_at": stamp,
            }
            self.item_tags[iid] = {tag_ids[0]} if index % 2 else set()
        # 本地降级模式下的演示账号（生产环境由 Config 关闭，fail-closed）
        if self.cfg.demo_admin_enabled:
            self.create_admin(self.cfg.demo_admin_email, self.cfg.demo_admin_password,
                              display_name="演示管理员", role="admin")

    # ---- 健康 ---------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        return {"mode": "memory", "degraded": True, "detail": "内存降级模式：数据不会持久化"}

    # ---- 管理员 -------------------------------------------------------

    def admin_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        for admin in self.admins.values():
            if str(admin.get("email")) == email.lower():
                return admin
        return None

    def create_admin(self, email: str, password: str, display_name: str = "", role: str = "admin") -> Dict[str, Any]:
        salt, digest = hash_password(password)
        admin = {
            "id": new_id(),
            "email": email.lower(),
            "password_hash": digest,
            "salt": salt,
            "display_name": display_name or email.split("@")[0],
            "role": role if role in ADMIN_ROLES else "admin",
            "created_at": now_iso(),
            "last_login_at": "",
        }
        self.admins[admin["id"]] = admin
        return admin

    def count_admins(self) -> int:
        return len(self.admins)

    def touch_login(self, admin_id: str) -> None:
        if admin_id in self.admins:
            self.admins[admin_id]["last_login_at"] = now_iso()

    def verify_credentials(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        admin = self.admin_by_email(email)
        if not admin:
            verify_password(password, "00" * 16, "00" * 32)
            return None
        if not verify_password(password, str(admin.get("salt")), str(admin.get("password_hash"))):
            return None
        return admin

    # ---- 分类 / 标签 ---------------------------------------------------

    def list_categories(self) -> List[Dict[str, Any]]:
        return sorted(self.categories.values(), key=lambda r: (int(r.get("sort_order") or 0), r.get("name", "")))

    def create_category(self, data: Dict[str, Any]) -> Dict[str, Any]:
        row = {"id": new_id(), "name": data["name"], "slug": data["slug"],
               "sort_order": int(data.get("sort_order") or 100), "created_at": now_iso()}
        self.categories[row["id"]] = row
        return row

    def update_category(self, category_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if category_id not in self.categories:
            return None
        for key in ("name", "slug", "sort_order"):
            if key in data:
                self.categories[category_id][key] = data[key]
        return self.categories[category_id]

    def delete_category(self, category_id: str) -> None:
        used = sum(1 for row in self.items.values() if row.get("category_id") == category_id)
        if used:
            raise Conflict(f"该分类下仍有 {used} 条内容，请先迁移或删除")
        self.categories.pop(category_id, None)

    def list_tags(self) -> List[Dict[str, Any]]:
        return sorted(self.tags.values(), key=lambda r: str(r.get("name", "")))

    def create_tag(self, data: Dict[str, Any]) -> Dict[str, Any]:
        for tag in self.tags.values():
            if str(tag.get("name")) == data["name"]:
                return tag
        row = {"id": new_id(), "name": data["name"], "slug": data["slug"], "created_at": now_iso()}
        self.tags[row["id"]] = row
        return row

    def delete_tag(self, tag_id: str) -> None:
        used = sum(1 for names in self.item_tags.values() if tag_id in names)
        if used:
            raise Conflict(f"该标签仍被 {used} 条内容引用，请先移除引用")
        self.tags.pop(tag_id, None)

    # ---- 条目 ---------------------------------------------------------

    def _tag_names(self, item_id: str) -> List[str]:
        names = [str(self.tags[t].get("name", "")) for t in self.item_tags.get(item_id, set()) if t in self.tags]
        return sorted(n for n in names if n)

    def _with_tags(self, row: Dict[str, Any]) -> Dict[str, Any]:
        row["tags"] = self._tag_names(str(row.get("id")))
        return row

    def list_items(self, params: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], int]:
        page, size = clean_page(params.get("page"), params.get("page_size"),
                                self.cfg.page_size, self.cfg.max_page_size)
        sort_field, order = clean_sort(params.get("sort"), params.get("order"))
        keyword = str(params.get("q") or "").strip().lower()
        status = str(params.get("status") or "").strip().lower()
        category_id = str(params.get("category_id") or "").strip()
        tag = str(params.get("tag") or "").strip()

        rows = list(self.items.values())
        if keyword:
            rows = [r for r in rows if keyword in " ".join(
                [str(r.get("title", "")), str(r.get("summary", "")), str(r.get("body", "")), str(r.get("slug", ""))]
            ).lower()]
        if status in STATUSES:
            rows = [r for r in rows if str(r.get("status")) == status]
        if category_id == "__none__":
            rows = [r for r in rows if not r.get("category_id")]
        elif category_id:
            rows = [r for r in rows if str(r.get("category_id")) == category_id]
        if tag:
            rows = [r for r in rows if tag in self._tag_names(str(r.get("id")))]

        def sort_key(row: Dict[str, Any]) -> str:
            value = row.get(sort_field)
            return str(value) if value is not None else ""

        rows.sort(key=sort_key, reverse=(order == "desc"))
        total = len(rows)
        start = (page - 1) * size
        return [self._with_tags(dict(r)) for r in rows[start:start + size]], total

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        row = self.items.get(item_id)
        return self._with_tags(dict(row)) if row else None

    def create_item(self, data: Dict[str, Any], actor: str = "") -> Dict[str, Any]:
        stamp = now_iso()
        row = {
            "id": new_id(),
            "title": data["title"],
            "slug": data.get("slug") or "",
            "summary": data.get("summary") or "",
            "body": data.get("body") or "",
            "status": data.get("status") or "draft",
            "category_id": data.get("category_id") or None,
            "cover_url": data.get("cover_url") or "",
            "published_at": stamp if data.get("status") == "published" else None,
            "created_by": actor,
            "created_at": stamp,
            "updated_at": stamp,
        }
        self.items[row["id"]] = row
        self._set_item_tags(row["id"], data.get("tags") or [])
        self.add_log(actor, "create", row["id"], f"新建内容「{row['title']}」")
        return self._with_tags(dict(row))

    def update_item(self, item_id: str, data: Dict[str, Any], actor: str = "",
                    expected_updated_at: str = "") -> Optional[Dict[str, Any]]:
        current = self.items.get(item_id)
        if not current:
            return None
        if expected_updated_at and str(current.get("updated_at") or "") != expected_updated_at:
            raise Conflict("内容已被其他会话修改，请刷新后重试")
        for key in ("title", "slug", "summary", "body", "status", "category_id", "cover_url"):
            if key in data:
                current[key] = data[key]
        if data.get("status") == "published" and not current.get("published_at"):
            current["published_at"] = now_iso()
        current["updated_at"] = now_iso()
        if "tags" in data:
            self._set_item_tags(item_id, data.get("tags") or [])
        self.add_log(actor, "update", item_id, f"更新内容「{current.get('title', '')}」")
        return self._with_tags(dict(current))

    def delete_item(self, item_id: str, actor: str = "") -> bool:
        current = self.items.pop(item_id, None)
        self.item_tags.pop(item_id, None)
        self.add_log(actor, "delete", item_id, f"删除内容「{(current or {}).get('title', '')}」")
        return current is not None

    def bulk_update(self, ids: List[str], action: str, actor: str = "") -> int:
        if action == "delete":
            for item_id in list(ids):
                self.delete_item(item_id, actor)
            return len(ids)
        if action not in STATUSES:
            raise Conflict(f"不支持的批量动作：{action}")
        for item_id in ids:
            row = self.items.get(item_id)
            if not row:
                continue
            row["status"] = action
            row["updated_at"] = now_iso()
            if action == "published" and not row.get("published_at"):
                row["published_at"] = now_iso()
        self.add_log(actor, "bulk", "", f"批量{action} {len(ids)} 条内容")
        return len(ids)

    def _set_item_tags(self, item_id: str, names: Iterable[str]) -> None:
        bucket = self.item_tags.setdefault(item_id, set())
        bucket.clear()
        for name in clean_tags(list(names)):
            tag = self.create_tag({"name": name, "slug": name})
            bucket.add(str(tag["id"]))

    # ---- 附件 ---------------------------------------------------------

    def list_attachments(self, item_id: str = "") -> List[Dict[str, Any]]:
        rows = [dict(r) for r in self.attachments.values()]
        if item_id:
            rows = [r for r in rows if str(r.get("item_id")) == item_id]
        rows.sort(key=lambda r: str(r.get("created_at") or ""), reverse=True)
        return rows

    def add_attachment(self, meta: Dict[str, Any], actor: str = "") -> Dict[str, Any]:
        row = {
            "id": new_id(),
            "item_id": meta.get("item_id") or None,
            "filename": meta["filename"],
            "path": meta["path"],
            "url": meta["url"],
            "content_type": meta.get("content_type") or "application/octet-stream",
            "size": int(meta.get("size") or 0),
            "created_by": actor,
            "created_at": now_iso(),
        }
        self.attachments[row["id"]] = row
        self.add_log(actor, "upload", row["id"], f"上传附件「{row['filename']}」")
        return row

    def get_attachment(self, attachment_id: str) -> Optional[Dict[str, Any]]:
        return self.attachments.get(attachment_id)

    def delete_attachment(self, attachment_id: str, actor: str = "") -> Optional[Dict[str, Any]]:
        row = self.attachments.pop(attachment_id, None)
        if row:
            self.add_log(actor, "delete_file", attachment_id, f"删除附件「{row.get('filename', '')}」")
        return row

    # ---- 日志与看板 -----------------------------------------------------

    def add_log(self, actor: str, action: str, target: str, detail: str = "") -> None:
        self.logs.append({
            "id": new_id(),
            "actor": actor or "system",
            "action": action,
            "target": target,
            "detail": detail,
            "created_at": now_iso(),
        })

    def list_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        rows = sorted(self.logs, key=lambda r: str(r.get("created_at") or ""), reverse=True)
        return rows[: max(min(limit, 100), 1)]

    def dashboard(self) -> Dict[str, Any]:
        by_status = {status: sum(1 for r in self.items.values() if r.get("status") == status) for status in STATUSES}
        by_category = []
        for category in self.list_categories()[:8]:
            by_category.append({
                "id": category["id"],
                "name": category.get("name", ""),
                "count": sum(1 for r in self.items.values() if r.get("category_id") == category["id"]),
            })
        buckets: Dict[str, int] = {}
        for index in range(14):
            day = (datetime.now(timezone.utc) - timedelta(days=13 - index)).date().isoformat()
            buckets[day] = 0
        for row in self.items.values():
            day = str(row.get("created_at") or "")[:10]
            if day in buckets:
                buckets[day] += 1
        trend = [{"date": day, "count": count} for day, count in sorted(buckets.items())]
        total_bytes = sum(int(r.get("size") or 0) for r in self.attachments.values())
        return {
            "total": len(self.items),
            "by_status": by_status,
            "by_category": by_category,
            "trend": trend,
            "attachments": {"count": len(self.attachments), "bytes": total_bytes},
            "categories": len(self.categories),
            "tags": len(self.tags),
            "logs": self.list_logs(10),
        }


def build_store(cfg: Config):
    """按配置选择仓储：云端就绪用 Supabase，否则内存降级。"""
    if cfg.cloud_ready:
        store = SupabaseStore(cfg)
        if not store.health().get("degraded"):
            return store
    return MemoryStore(cfg)
