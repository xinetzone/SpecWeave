"""运营与后台服务：广告位、公告、系统配置、审计日志、后台八模块概览。

鉴权口径（源文档 F-099）：``/api/ads`` 与 ``/api/news`` **无鉴权公开**；
用户类 API 未鉴权返回 401，admin 类返回 403。
"""

import secrets

from ..logging_utils import get_logger
from ..models import AdItem, AdminConfig, AuditEvent, NewsItem
from ..storage import Store

logger = get_logger("services.ops")

#: 后台八模块（源文档 F-097）
ADMIN_MODULES: tuple[tuple[str, str], ...] = (
    ("users", "用户管理"),
    ("catalog", "厂商目录"),
    ("plans", "套餐与订单"),
    ("redemption", "人工核销"),
    ("usage", "用量总览"),
    ("content", "公告与广告位"),
    ("config", "系统配置"),
    ("audit", "审计日志"),
)


class OpsService:
    def __init__(self, store: Store) -> None:
        self.store = store

    def ensure_seed(self) -> None:
        """初始化运营内容（演示数据，非真实投放）。"""
        if not self.store.ads.all():
            self.store.ads.add(
                AdItem(
                    id=secrets.token_hex(6),
                    title="示例广告位",
                    body="本复刻不含真实投放与返佣短链（源产品相关风险见 README）",
                    url="",
                    enabled=True,
                )
            )
        if not self.store.news.all():
            for index in range(5):
                self.store.news.add(
                    NewsItem(
                        id=secrets.token_hex(6),
                        title=f"示例公告 {index + 1}",
                        summary="演示用公告条目，不含真实资讯",
                        url="",
                        featured=index == 0,
                        enabled=True,
                    )
                )

    def ads(self, *, enabled_only: bool = True) -> tuple[AdItem, ...]:
        rows = self.store.ads.all()
        if enabled_only:
            rows = [a for a in rows if a.enabled]
        return tuple(rows)

    def news(self, *, enabled_only: bool = True) -> tuple[NewsItem, ...]:
        rows = self.store.news.all()
        if enabled_only:
            rows = [n for n in rows if n.enabled]
        return tuple(rows)

    def add_ad(self, title: str, body: str = "", url: str = "") -> AdItem:
        item = AdItem(id=secrets.token_hex(6), title=title, body=body, url=url)
        self.store.ads.add(item)
        return item

    def add_news(self, title: str, summary: str = "", *, featured: bool = False) -> NewsItem:
        item = NewsItem(
            id=secrets.token_hex(6), title=title, summary=summary, featured=featured
        )
        self.store.news.add(item)
        return item

    # ------------------------------------------------------------- 配置
    def config(self) -> AdminConfig:
        return self.store.ensure_admin_config()

    def set_config(self, **updates) -> AdminConfig:
        current = self.config()
        unknown = set(updates) - set(AdminConfig.model_fields)
        if unknown:
            raise ValueError(f"未知配置项 {sorted(unknown)}")
        updated = current.model_copy(update=updates)
        return self.store.set_admin_config(updated)

    # ------------------------------------------------------------- 审计
    def audit(self, *, actor_user_id: str, action: str, target_id: str = "", result: str = "ok") -> AuditEvent:
        event = AuditEvent(
            id=secrets.token_hex(8),
            actor_user_id=actor_user_id,
            action=action,
            target_id=target_id,
            result=result,
        )
        self.store.audit.add(event)
        logger.info("审计：%s by %s → %s", action, actor_user_id, result)
        return event

    def audit_log(self, limit: int = 100) -> tuple[AuditEvent, ...]:
        rows = sorted(self.store.audit.all(), key=lambda e: e.created_at, reverse=True)
        return tuple(rows[:limit])

    def modules(self) -> tuple[dict[str, str], ...]:
        return tuple({"key": key, "label": label} for key, label in ADMIN_MODULES)


__all__ = ["ADMIN_MODULES", "OpsService"]
