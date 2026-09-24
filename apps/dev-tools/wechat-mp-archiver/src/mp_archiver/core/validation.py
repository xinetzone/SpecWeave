"""元数据完整性校验（TR-4.3：title/url/publish_time 100% 非空约定）。"""

from dataclasses import dataclass

_REQUIRED_FIELDS = ("title", "url", "publish_time")


@dataclass(frozen=True, slots=True)
class CompletenessReport:
    total: int
    missing: dict[str, int]

    @property
    def ok(self) -> bool:
        return self.total > 0 and all(value == 0 for value in self.missing.values())

    def rates(self) -> dict[str, float]:
        if self.total == 0:
            return {field: 0.0 for field in self.missing}
        return {
            field: 1.0 - count / self.total
            for field, count in self.missing.items()
        }


def check_metadata_completeness(conn, account_biz: str) -> CompletenessReport:
    """统计账号下文章 title/url/publish_time 的缺失行数。"""
    total = conn.execute(
        "SELECT COUNT(*) AS n FROM articles WHERE biz = ?", (account_biz,)
    ).fetchone()["n"]
    missing: dict[str, int] = {}
    for field in _REQUIRED_FIELDS:
        missing[field] = conn.execute(
            f"SELECT COUNT(*) AS n FROM articles WHERE biz = ? "
            f"AND ({field} IS NULL OR {field} = '')",
            (account_biz,),
        ).fetchone()["n"]
    return CompletenessReport(total=int(total), missing=missing)
