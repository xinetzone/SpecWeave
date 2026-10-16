"""NFR-6 渲染与同步批处理性能基准（留档脚本，非 CI 红门）。

spec.md:79 NFR-6：单篇 100KB Markdown 渲染（含全部扩展短样例）P95 < 500ms
（本机 Windows，纯库调用）；同步 push 100 文档批处理 < 1s（SQLite 本地）。
该指标为非强制 CI 门槛，以本基准脚本记录为准。

实现约束：
- 仅用标准库计时（time.perf_counter + statistics.quantiles）；
- 渲染走库调用流水线 render_markdown（前置解析 + 渲染 + 净化），不启 HTTP 层；
- 同步批处理走 db.push_changes（SQLite 本地），每轮独立临时库，排除迁移耗时；
- 样本数与阈值集中在本模块顶部常量，便于随机器/规模调整。

用法：
    python scripts/bench_render.py
"""

import statistics
import sys
import tempfile
import time
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
_SRC = str(APP_ROOT / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from doocs_md_py.render import IOpts, init_renderer  # noqa: E402
from doocs_md_py.render.markdown import render_markdown  # noqa: E402
from doocs_md_py.server import db  # noqa: E402
from doocs_md_py.server.types import SyncDocument, SyncSetting  # noqa: E402

# NFR-6 阈值与规模
RENDER_SAMPLE_BYTES = 100 * 1024
RENDER_SAMPLES = 20
RENDER_P95_LIMIT_MS = 500.0
PUSH_BATCH_DOCUMENTS = 100
PUSH_DOCUMENT_BYTES = 2 * 1024
PUSH_SAMPLES = 10
PUSH_P95_LIMIT_SEC = 1.0

# statistics.quantiles(n=20) 的末位切点即 95% 分位
_QUANTILE_CUTS = 20

BENCH_USER_ID = "bench-user-001"
BENCH_USER = {
    "id": BENCH_USER_ID,
    "github_id": 999001,
    "login": "bench",
    "name": "Bench",
    "avatar": None,
}

# 全部渲染扩展的短样例（语法取自各扩展模块的规则定义）
_EXTENSION_SHOWCASE = """---
title: 性能基准样张
---

[TOC]

# 一级标题

## 二级标题

正文段落，含 ==高亮==、++下划线++、~波浪~、^上标^ 与行内公式 $a^2+b^2=c^2$。

> [!NOTE]
> 提示块内容。

> [!WARNING]
> 告警块内容。

:::tip 自定义标题
容器块内容。
:::

[漢字]{かんじ} 与 [上海]{shang-hai} 注音。

![示例图](https://example.com/a.png|300x200)

<![](https://example.com/a.png),![](https://example.com/b.png)>

<Emoji id="liulei" />

```javascript
export const sum = (a, b) => a + b;
console.log(sum(1, 2));
```

```mermaid
graph TD;
    A-->B
```

```plantuml
@startuml
A->B
@enduml
```

```infographic
{"type": "chart"}
```

$$
ITE_{i}=Y_{i,1}-Y_{i,0} \\tag{1}
$$

| 列一 | 列二 |
| --- | --- |
| 值一 | 值二 |

带脚注的引用[^1]。

[^1]: 脚注正文。
"""

_FILLER_PARAGRAPH = (
    "填充段落：渲染吞吐基准用于测量解析、扩展注入、代码高亮与净化的整体开销，"
    "该段不含任何扩展语法，仅用于把样张体量逼近目标字节数。\n\n"
)


def _p95(samples: list[float]) -> float:
    """样本 P95（样本不足 2 个时退化为最大值）。"""
    if len(samples) < 2:
        return max(samples)
    return statistics.quantiles(samples, n=_QUANTILE_CUTS)[-1]


def _build_document() -> str:
    """构造 100KB 级 Markdown 样张（扩展短样例 + 纯文本填充）。"""
    parts = [_EXTENSION_SHOWCASE]
    size = len(_EXTENSION_SHOWCASE.encode("utf-8"))
    while size < RENDER_SAMPLE_BYTES:
        parts.append(_FILLER_PARAGRAPH)
        size += len(_FILLER_PARAGRAPH.encode("utf-8"))
    return "".join(parts)


def _build_documents(round_index: int) -> list[SyncDocument]:
    """构造 100 篇约 2KB 的同步文档（每轮独立 id，强制走插入路径）。"""
    unit = "同步批处理基准内容。"
    repeat = max(1, PUSH_DOCUMENT_BYTES // len(unit.encode("utf-8")))
    content = unit * repeat
    stamp = db.now_ms()
    return [
        SyncDocument(
            id=f"bench-{round_index}-{i:03d}",
            title=f"基准文档 {i}",
            content=content,
            parent_id=None,
            create_datetime=stamp,
            update_datetime=stamp,
        )
        for i in range(PUSH_BATCH_DOCUMENTS)
    ]


def _build_settings() -> list[SyncSetting]:
    stamp = db.now_ms()
    return [
        SyncSetting(key=f"bench-setting-{i}", value=f"value-{i}", updated_at=stamp)
        for i in range(5)
    ]


def _bench_render() -> dict:
    renderer = init_renderer(IOpts())
    document = _build_document()
    samples: list[float] = []
    for _ in range(RENDER_SAMPLES):
        started = time.perf_counter()
        render_markdown(document, renderer)
        samples.append(time.perf_counter() - started)
    return {
        "bytes": len(document.encode("utf-8")),
        "samples": samples,
        "p50_ms": statistics.median(samples) * 1000,
        "p95_ms": _p95(samples) * 1000,
        "max_ms": max(samples) * 1000,
        "limit_ms": RENDER_P95_LIMIT_MS,
    }


def _bench_push() -> dict:
    samples: list[float] = []
    with tempfile.TemporaryDirectory(prefix="mdpy-bench-") as tmp:
        for round_index in range(PUSH_SAMPLES):
            conn = db.connect(Path(tmp) / f"bench-{round_index}.db")
            try:
                db.apply_migrations(conn)
                db.upsert_user(conn, BENCH_USER)
                documents = _build_documents(round_index)
                settings = _build_settings()
                started = time.perf_counter()
                db.push_changes(conn, BENCH_USER_ID, documents, settings)
                samples.append(time.perf_counter() - started)
            finally:
                conn.close()
    return {
        "documentsPerBatch": PUSH_BATCH_DOCUMENTS,
        "samples": samples,
        "p50_sec": statistics.median(samples),
        "p95_sec": _p95(samples),
        "max_sec": max(samples),
        "limit_sec": PUSH_P95_LIMIT_SEC,
    }


def _verdict(value: float, limit: float) -> str:
    return "达标" if value <= limit else "超阈值"


def main() -> int:
    render = _bench_render()
    push = _bench_push()

    print("NFR-6 性能基准（本机 Windows；非 CI 门槛，仅留档）")
    print(
        f"[渲染] 样张 {render['bytes']} 字节 / {RENDER_SAMPLES} 次采样"
        f" → P50 {render['p50_ms']:.1f}ms，P95 {render['p95_ms']:.1f}ms，"
        f"MAX {render['max_ms']:.1f}ms；阈值 P95 < {render['limit_ms']:.0f}ms "
        f"→ {_verdict(render['p95_ms'], render['limit_ms'])}"
    )
    print(
        f"[同步] 每轮 {push['documentsPerBatch']} 篇文档 / {PUSH_SAMPLES} 轮"
        f" → P50 {push['p50_sec'] * 1000:.1f}ms，P95 {push['p95_sec'] * 1000:.1f}ms，"
        f"MAX {push['max_sec'] * 1000:.1f}ms；阈值 P95 < {push['limit_sec'] * 1000:.0f}ms "
        f"→ {_verdict(push['p95_sec'], push['limit_sec'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
