"""SQLite 迁移注册表。

SQL 文件原样移植自上游 apps/api/migrations（Wrangler D1 迁移机制替换为内置
_migrations 表的幂等应用器，见 doocs_md_py.server.db.apply_migrations）。
每个文件只在其序号未登记时执行一次；DDL 内的 IF NOT EXISTS 仅作辅助防线。
"""

from pathlib import Path

MIGRATION_DIR = Path(__file__).resolve().parent

# (序号, 文件名)；顺序即应用顺序，必须与上游 0001-0008 一一对应
MIGRATIONS: tuple[tuple[int, str], ...] = tuple(
    (int(p.name[:4]), p.name)
    for p in sorted(MIGRATION_DIR.glob("*.sql"))
)


def load_migration(name: str) -> str:
    return (MIGRATION_DIR / name).read_text(encoding="utf-8")
