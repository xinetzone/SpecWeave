"""链接门禁基线：把已确认的历史断链固化为可审计条目，只报新增。

指纹 =（源文件相对路径, 规范化链接目标），**不含行号**——行号会随文档编辑
漂移，不能作为身份。一个指纹附带 count（出现次数）、since（入账日期）、
reason（分类）与 review_by（复核期限）。

写入与读取都执行同一套自检（违反即视为基线损坏）：
- reason 必须属于 REASON_ENUM；
- source 必须是 git 跟踪的文件；
- source / target 不得以 projects/ 或 vendor/ 前缀开头（二者是扫描排除区）。

`--update-baseline` 只为「新增指纹」要求 reason：既可从 --reason 取批量默认值，
也可用 --reason-map 逐条指定；两者都缺时拒绝执行，避免把未分类的断链写进基线。
"""

import json
import posixpath
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from lib.atomic_write import atomic_write_json

REASON_ENUM = ("moved", "deleted", "depth", "other", "unclassified")
BASELINE_VERSION = 1
DEFAULT_REVIEW_DAYS = 90
EXCLUDED_PREFIXES = ("projects/", "vendor/")
BASELINE_RELATIVE_PATH = ".agents/config/link-baseline.json"


class BaselineError(ValueError):
    """基线内容或写入参数不合法。"""


@dataclass(frozen=True)
class BaselineEntry:
    """一条基线条目（不含行号）。"""

    source: str
    target: str
    count: int
    since: str
    reason: str
    review_by: str

    @property
    def key(self) -> tuple[str, str]:
        return (self.source, self.target)

    def as_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "count": self.count,
            "since": self.since,
            "reason": self.reason,
            "review_by": self.review_by,
        }


def normalize_target(url: str) -> str:
    """规范化链接目标：去锚点/查询串、统一斜杠、折叠 ./ 与 ../。"""
    clean = url.split("#", 1)[0].split("?", 1)[0].strip().replace("\\", "/")
    if not clean:
        return ""
    normalized = posixpath.normpath(clean)
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def normalize_source(source: str | Path) -> str:
    """规范化源文件路径为仓库相对的 posix 路径。"""
    text = str(source).replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text


def fingerprint(source: str | Path, target: str) -> tuple[str, str]:
    """返回基线指纹（源文件, 规范化目标）。"""
    return (normalize_source(source), normalize_target(target))


def default_review_by(since: str, days: int = DEFAULT_REVIEW_DAYS) -> str:
    """按入账日期推算默认复核期限。"""
    base = date.fromisoformat(since)
    return (base + timedelta(days=days)).isoformat()


def _require_text(value, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BaselineError(f"字段 {field} 必须是非空字符串")
    return value


def _check_excluded_prefix(value: str, field: str) -> None:
    normalized = value.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    normalized = normalized.lstrip("/")
    for prefix in EXCLUDED_PREFIXES:
        if normalized.startswith(prefix):
            raise BaselineError(
                f"基线损坏：{field}={value!r} 命中排除目录前缀 {prefix!r}"
                "（projects/ 与 vendor/ 不参与扫描，不应出现在基线中）"
            )


def validate_entry(
    entry: BaselineEntry, tracked: set[str], *, where: str = "基线"
) -> None:
    """校验单条基线条目；不合法时抛 BaselineError。"""
    if not isinstance(entry.count, int) or isinstance(entry.count, bool) or entry.count < 1:
        raise BaselineError(f"{where}条目 {entry.source} -> {entry.target} 的 count 必须是正整数")
    if entry.reason not in REASON_ENUM:
        raise BaselineError(
            f"{where}条目 {entry.source} -> {entry.target} 的 reason={entry.reason!r} "
            f"不在枚举 {REASON_ENUM} 中"
        )
    for field, value in (("since", entry.since), ("review_by", entry.review_by)):
        try:
            date.fromisoformat(value)
        except ValueError as exc:
            raise BaselineError(
                f"{where}条目 {entry.source} -> {entry.target} 的 {field}={value!r} 不是 ISO 日期"
            ) from exc
    if date.fromisoformat(entry.review_by) < date.fromisoformat(entry.since):
        raise BaselineError(
            f"{where}条目 {entry.source} -> {entry.target} 的 review_by 早于 since"
        )
    _check_excluded_prefix(entry.source, "source")
    _check_excluded_prefix(entry.target, "target")
    if entry.source not in tracked:
        raise BaselineError(
            f"基线损坏：source={entry.source!r} 不是 git 跟踪的文件"
            "（基线只收受版本控制的源文件）"
        )


def _entry_from_dict(raw: dict) -> BaselineEntry:
    if not isinstance(raw, dict):
        raise BaselineError("基线 entries 元素必须是对象")
    missing = [
        field
        for field in ("source", "target", "count", "since", "reason", "review_by")
        if field not in raw
    ]
    if missing:
        raise BaselineError(f"基线条目缺少字段: {', '.join(missing)}")
    return BaselineEntry(
        source=_require_text(raw["source"], "source"),
        target=_require_text(raw["target"], "target"),
        count=raw["count"],
        since=_require_text(raw["since"], "since"),
        reason=_require_text(raw["reason"], "reason"),
        review_by=_require_text(raw["review_by"], "review_by"),
    )


def load_baseline(
    path: Path, tracked: set[str]
) -> dict[tuple[str, str], BaselineEntry]:
    """加载并校验基线文件；文件不存在时返回空字典。"""
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BaselineError(f"基线文件无法解析: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BaselineError("基线文件根节点必须是对象")
    if payload.get("version") != BASELINE_VERSION:
        raise BaselineError(
            f"基线版本不支持: {payload.get('version')!r}（期望 {BASELINE_VERSION}）"
        )
    raw_entries = payload.get("entries")
    if not isinstance(raw_entries, list):
        raise BaselineError("基线 entries 必须是数组")
    entries: dict[tuple[str, str], BaselineEntry] = {}
    for raw in raw_entries:
        entry = _entry_from_dict(raw)
        entry = BaselineEntry(
            source=normalize_source(entry.source),
            target=normalize_target(entry.target),
            count=entry.count,
            since=entry.since,
            reason=entry.reason,
            review_by=entry.review_by,
        )
        validate_entry(entry, tracked)
        if entry.key in entries:
            raise BaselineError(
                f"基线存在重复指纹: {entry.source} -> {entry.target}"
            )
        entries[entry.key] = entry
    return entries


def save_baseline(
    path: Path,
    entries: dict[tuple[str, str], BaselineEntry],
    tracked: set[str],
) -> None:
    """校验并原子写入基线文件（按 source、target 排序，保证可复现）。"""
    ordered = sorted(entries.values(), key=lambda e: (e.source, e.target))
    seen: set[tuple[str, str]] = set()
    for entry in ordered:
        validate_entry(entry, tracked)
        if entry.key in seen:
            raise BaselineError(f"基线存在重复指纹: {entry.source} -> {entry.target}")
        seen.add(entry.key)
    payload = {
        "version": BASELINE_VERSION,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "entries": [entry.as_dict() for entry in ordered],
    }
    atomic_write_json(path, payload)


def load_reason_map(path: Path) -> dict[tuple[str, str], str]:
    """加载逐条原因映射（JSON 数组，元素含 source/target/reason）。"""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BaselineError(f"reason-map 无法解析: {path}: {exc}") from exc
    if isinstance(raw, dict):
        raw = raw.get("entries")
    if not isinstance(raw, list):
        raise BaselineError("reason-map 必须是数组（或含 entries 数组的对象）")
    mapping: dict[tuple[str, str], str] = {}
    for item in raw:
        if not isinstance(item, dict):
            raise BaselineError("reason-map 元素必须是对象")
        reason = item.get("reason")
        if reason not in REASON_ENUM:
            raise BaselineError(
                f"reason-map 中 reason={reason!r} 不在枚举 {REASON_ENUM} 中"
            )
        key = fingerprint(
            _require_text(item.get("source"), "source"),
            _require_text(item.get("target"), "target"),
        )
        mapping[key] = reason
    return mapping


def build_updated_entries(
    current: dict[tuple[str, str], int],
    existing: dict[tuple[str, str], BaselineEntry],
    *,
    reason: str | None,
    reason_map: dict[tuple[str, str], str] | None,
    since: str,
    review_by: str | None,
) -> tuple[dict[tuple[str, str], BaselineEntry], dict[str, int]]:
    """合并当前断链与既有基线，返回 (新基线, 统计)。

    既有指纹保留原 since/review_by，仅刷新 count；若 reason-map 显式指定了
    该指纹的 reason，则同时改写既有条目的分类（用于把 unclassified 归位）。
    新指纹必须有 reason（reason-map 优先于 --reason）。缺失时抛 BaselineError
    拒绝写入。
    """
    if reason is not None and reason not in REASON_ENUM:
        raise BaselineError(f"reason={reason!r} 不在枚举 {REASON_ENUM} 中")
    review = review_by or default_review_by(since)
    date.fromisoformat(since)
    date.fromisoformat(review)
    mapping = reason_map or {}
    merged: dict[tuple[str, str], BaselineEntry] = {}
    missing: list[str] = []
    added = kept = reclassified = 0
    for key, count in current.items():
        old = existing.get(key)
        if old is not None:
            entry_reason = mapping.get(key, old.reason)
            if entry_reason != old.reason:
                reclassified += 1
            merged[key] = BaselineEntry(
                source=old.source,
                target=old.target,
                count=count,
                since=old.since,
                reason=entry_reason,
                review_by=old.review_by,
            )
            kept += 1
            continue
        entry_reason = mapping.get(key, reason)
        if entry_reason is None:
            missing.append(f"{key[0]} -> {key[1]}")
            continue
        merged[key] = BaselineEntry(
            source=key[0],
            target=key[1],
            count=count,
            since=since,
            reason=entry_reason,
            review_by=review,
        )
        added += 1
    if missing:
        preview = "\n  ".join(missing[:10])
        more = f"\n  ……另有 {len(missing) - 10} 条" if len(missing) > 10 else ""
        raise BaselineError(
            "新增断链缺少 reason，拒绝写入基线（请用 --reason 或 --reason-map 指定）：\n  "
            + preview
            + more
        )
    stale = len(set(existing) - set(current))
    return merged, {
        "added": added,
        "kept": kept,
        "reclassified": reclassified,
        "stale": stale,
        "total": len(merged),
    }


def diff_baseline(
    current: dict[tuple[str, str], int],
    baseline: dict[tuple[str, str], BaselineEntry],
) -> tuple[list[tuple[str, str, int, int]], int]:
    """返回 (新增/增多的条目, 已消失条目数)。

    新条目的 count 大于基线 count 时也算新增（同一目标多出了一处断链）。
    """
    fresh: list[tuple[str, str, int, int]] = []
    for key, count in current.items():
        old = baseline.get(key)
        if old is None:
            fresh.append((key[0], key[1], count, 0))
        elif count > old.count:
            fresh.append((key[0], key[1], count, old.count))
    stale = len(set(baseline) - set(current))
    return sorted(fresh), stale
