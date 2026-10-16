"""构建 OKF 知识包检索索引（SQLite FTS5 + trigram）。

产出 `data/knowledge.db`：
- `chunks` 虚拟表：FTS5(trigram) 全文索引，中文按三元组切分，BM25 排序
- `meta` 表：构建元信息与派生产物溯源字段

设计取舍（与手写 TF-IDF 倒排索引对比）：
- 语料 19.2M 字符、单束最大 786K 字符且分布极斜，按「束」分片不均衡；
- FTS5 由 SQLite 维护倒排索引并按页惰性读取，冷启动零加载、查询毫秒级；
- sqlite3 为标准库，不引入任何第三方检索依赖。

用法：
    python scripts/build_index.py                    # 全量构建
    python scripts/build_index.py --limit 50         # 只处理前 50 个知识包（冒烟用）
    python scripts/build_index.py --root <路径>       # 指定知识包根目录
"""

import argparse
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
COPIED_BUNDLES_ROOT = APP_ROOT / ".corpus" / "bundles"
DEFAULT_DB_PATH = APP_ROOT / "data" / "knowledge.db"


def default_bundles_root() -> Path:
    """定位知识包语料：优先仓库子模块，其次部署时复制进来的 .corpus 副本。

    必须惰性计算：本地开发时应用目录位于仓库三层之下，
    而 Vercel 的部署根就是应用目录本身，其 parents 层级不足——
    在模块级求值会在导入阶段直接抛 IndexError，导致整个构建失败。
    """
    for depth in (2, 1, 0):
        if len(APP_ROOT.parents) > depth:
            candidate = APP_ROOT.parents[depth] / "projects" / "awesome-okf-xs" / "doc" / "bundles"
            if candidate.is_dir():
                return candidate
    return COPIED_BUNDLES_ROOT

MAX_CHUNK = 900          # 单段最大字符数
MIN_CHUNK = 120          # 过短碎片并入上一段
EXCLUDED_NAMES = {"log.md", "changelog.md", "CHANGELOG.md"}

FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`([^`]{1,200})`")
HTML_TAG_RE = re.compile(r"<[^>]{1,200}>")
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
MD_IMG_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
WS_RE = re.compile(r"[ \t]{2,}")
BLANK_RE = re.compile(r"\n{3,}")


def clean_markdown(raw: str) -> str:
    """把 Markdown 归一化为参与检索的纯文本。"""
    text = FRONTMATTER_RE.sub("", raw, count=1)
    text = MD_IMG_RE.sub(" ", text)
    text = FENCE_RE.sub(" ", text)
    text = HTML_TAG_RE.sub(" ", text)
    text = MD_LINK_RE.sub(r"\1", text)
    text = INLINE_CODE_RE.sub(r"\1", text)
    text = WS_RE.sub(" ", text)
    text = BLANK_RE.sub("\n\n", text)
    return text.strip()


def extract_title(raw: str, fallback: str) -> str:
    """优先取首个一级标题，其次 frontmatter 的 title，最后退回文件名。"""
    m = re.search(r"^#\s+(.+)$", raw, re.MULTILINE)
    if m:
        return m.group(1).strip()[:120]
    m = re.search(r"^title:\s*[\"']?(.+?)[\"']?\s*$", raw, re.MULTILINE)
    if m:
        return m.group(1).strip().strip("\"'")[:120]
    return fallback


def split_sections(text: str) -> list[tuple[str, str]]:
    """按 Markdown 标题切分为 (小标题, 正文) 序列。"""
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        return [("", text)]

    sections: list[tuple[str, str]] = []
    lead = text[: matches[0].start()].strip()
    if lead:
        sections.append(("", lead))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.end() : end].strip()
        if body:
            sections.append((m.group(2).strip(), body))
    return sections


def pack_chunks(text: str, max_len: int = MAX_CHUNK) -> list[str]:
    """把长正文按段落边界打包成不超过 max_len 的片段。"""
    if len(text) <= max_len:
        return [text]

    chunks: list[str] = []
    buf = ""
    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        if buf and len(buf) + len(para) + 2 > max_len:
            chunks.append(buf)
            buf = para
        else:
            buf = f"{buf}\n\n{para}" if buf else para
        while len(buf) > max_len:  # 单段落超长：按 max_len 硬切
            chunks.append(buf[:max_len])
            buf = buf[max_len:]
    if buf:
        chunks.append(buf)

    # 合并过短碎片，避免索引被噪声片段稀释
    merged: list[str] = []
    for c in chunks:
        if merged and len(c) < MIN_CHUNK:
            merged[-1] = f"{merged[-1]}\n\n{c}"
        else:
            merged.append(c)
    return merged


# `examples/` 与 `references/` 是知识包内部的子目录，自身也可能带 index.md。
# 若不排除，它们会被误判为独立知识包，使本应剔除的示例/信源内容重新混入索引。
EXCLUDED_DIR_PARTS = {"examples", "references"}


def iter_bundle_dirs(root: Path) -> list[Path]:
    """知识包 = 直接含 index.md 的目录。

    排除三类误纳：bundles 根自身的总索引、examples/ 与 references/ 子目录。
    """
    dirs = sorted(p.parent for p in root.rglob("index.md"))
    return [
        d
        for d in dirs
        if d != root and not EXCLUDED_DIR_PARTS.intersection(d.relative_to(root).parts)
    ]


def bundle_files(bundle_dir: Path) -> list[Path]:
    """取知识核心：包索引 + concepts/ 下文档。

    排除 examples/（代码样例）与 references/（外部信源），
    二者对自然语言问答的语义贡献低而体量占比高。
    """
    targets = [bundle_dir / "index.md"]
    concepts = bundle_dir / "concepts"
    if concepts.is_dir():
        targets.extend(sorted(concepts.rglob("*.md")))
    return [f for f in targets if f.is_file() and f.name not in EXCLUDED_NAMES]


def create_schema(con: sqlite3.Connection) -> None:
    # grp 而非 group —— group 是 SQL 关键字
    con.execute(
        """
        CREATE VIRTUAL TABLE chunks USING fts5(
            title,
            body,
            bundle UNINDEXED,
            grp UNINDEXED,
            domain UNINDEXED,
            path UNINDEXED,
            tokenize='trigram'
        )
        """
    )
    con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")


def build(bundles_root: Path, db_path: Path, limit: int | None) -> int:
    if not bundles_root.is_dir():
        raise SystemExit(
            f"知识包根目录不存在：{bundles_root}\n"
            f"请通过 --root 指定，或先执行 scripts/prepare_corpus.py 复制语料到 {COPIED_BUNDLES_ROOT}"
        )

    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    started = time.time()
    con = sqlite3.connect(db_path)
    create_schema(con)

    bundle_dirs = iter_bundle_dirs(bundles_root)
    if limit:
        bundle_dirs = bundle_dirs[:limit]

    total_chunks = 0
    total_bundles = 0
    batch: list[tuple[str, str, str, str, str, str]] = []

    for bd in bundle_dirs:
        rel = bd.relative_to(bundles_root)
        parts = rel.parts
        domain = parts[0] if parts else ""
        grp = parts[1] if len(parts) > 1 else ""
        bundle = "/".join(parts) if parts else bd.name

        written_here = 0
        for f in bundle_files(bd):
            raw = f.read_text(encoding="utf-8", errors="ignore")
            text = clean_markdown(raw)
            if len(text) < 30:
                continue
            doc_title = extract_title(raw, f.stem)
            for sec_title, sec_body in split_sections(text):
                heading = sec_title or doc_title
                for piece in pack_chunks(sec_body):
                    batch.append(
                        (heading, piece, bundle, grp, domain, str(f.relative_to(bundles_root)).replace("\\", "/"))
                    )
                    written_here += 1
        if written_here:
            total_bundles += 1
        total_chunks += written_here

        if len(batch) >= 2000:
            con.executemany(
                "INSERT INTO chunks(title, body, bundle, grp, domain, path) VALUES (?,?,?,?,?,?)", batch
            )
            con.commit()
            batch.clear()

    if batch:
        con.executemany("INSERT INTO chunks(title, body, bundle, grp, domain, path) VALUES (?,?,?,?,?,?)", batch)
        con.commit()

    con.execute("INSERT INTO meta(key, value) VALUES ('source', ?)", (str(bundles_root),))
    con.execute("INSERT INTO meta(key, value) VALUES ('built_at', ?)", (datetime.now(timezone.utc).isoformat(),))
    con.execute("INSERT INTO meta(key, value) VALUES ('chunk_count', ?)", (str(total_chunks),))
    con.execute("INSERT INTO meta(key, value) VALUES ('bundle_count', ?)", (str(total_bundles),))
    con.execute("INSERT INTO meta(key, value) VALUES ('tokenizer', 'fts5-trigram')")
    con.commit()
    con.execute("VACUUM")
    con.close()

    mb = db_path.stat().st_size / 1_048_576
    print(f"知识包根目录 : {bundles_root}")
    print(f"产出索引     : {db_path}")
    print(f"知识包/片段数: {total_bundles} / {total_chunks}")
    print(f"索引体积     : {mb:.1f} MB")
    print(f"耗时         : {time.time() - started:.1f}s")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="构建 OKF 知识包 FTS5 检索索引")
    ap.add_argument("--root", type=Path, default=None, help="知识包根目录（默认自动探测）")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="输出数据库路径")
    ap.add_argument("--limit", type=int, default=None, help="只处理前 N 个知识包（冒烟测试）")
    args = ap.parse_args()

    root = args.root
    if root is None:
        # 有 .corpus 副本时优先用它（部署态），否则回落到仓库子模块（开发态）
        root = COPIED_BUNDLES_ROOT if COPIED_BUNDLES_ROOT.is_dir() else default_bundles_root()
    return build(root, args.db, args.limit)


if __name__ == "__main__":
    sys.exit(main())
