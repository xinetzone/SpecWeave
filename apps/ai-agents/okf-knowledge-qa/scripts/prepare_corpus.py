"""把 OKF 知识包语料复制到应用内的 `.corpus/bundles`，供部署时构建索引。

为什么需要这一步：
- 知识包本体位于 git submodule `projects/awesome-okf-xs/doc/bundles/`，不在本应用目录内；
- Vercel 部署以本应用目录为根，只上传该目录内的文件；
- 因此部署前必须把构建索引所需的语料复制进来，交由 buildCommand 阶段构建索引。

关键约束：文件筛选逻辑**必须直接复用 build_index.py**，不得自行实现一份。
早期两处各写一套筛选规则，导致本地（读子模块）与线上（读 .corpus 副本）
产出 74955 / 74827 两个不可复现的片段数。单一事实来源是消除该偏差的根本手段。

用法：
    python scripts/prepare_corpus.py              # 增量复制（默认非破坏）
    python scripts/prepare_corpus.py --prune      # 先清空目标目录再复制

默认不删除任何文件：目标目录常有数千个文件，静默 rmtree 会触发工作区
批量删除保护，且一旦中断就会留下半截语料。清理改为显式 opt-in，
常规重跑只做覆盖式复制——由于新筛选范围总是旧范围的子集，
增量复制足以保证内容正确，代价仅是残留少量无用文件（只影响上传体积，不影响索引）。
"""

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_index import bundle_files, default_bundles_root, iter_bundle_dirs  # noqa: E402

APP_ROOT = Path(__file__).resolve().parents[1]
TARGET_ROOT = APP_ROOT / ".corpus" / "bundles"


def main() -> int:
    ap = argparse.ArgumentParser(description="复制 OKF 知识包语料到 .corpus/bundles")
    ap.add_argument(
        "--prune",
        action="store_true",
        help="复制前先清空目标目录（会删除其中全部文件，需显式指定）",
    )
    args = ap.parse_args()

    source = default_bundles_root()
    if not source.is_dir():
        print(f"未找到知识包语料：{source}", file=sys.stderr)
        print("请确认 awesome-okf-xs 子模块已初始化：git submodule update --init", file=sys.stderr)
        return 1

    if args.prune and TARGET_ROOT.exists():
        shutil.rmtree(TARGET_ROOT)
    TARGET_ROOT.mkdir(parents=True, exist_ok=True)

    bundle_dirs = iter_bundle_dirs(source)  # 全量 rglob，只算一次
    copied = 0
    total = 0
    for bundle_dir in bundle_dirs:
        for src in bundle_files(bundle_dir):
            dst = TARGET_ROOT / src.relative_to(source)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
            total += src.stat().st_size

    print(f"语料来源 : {source}")
    print(f"复制到   : {TARGET_ROOT}")
    print(f"知识包数 : {len(bundle_dirs)}")
    print(f"文件数   : {copied}")
    print(f"体量     : {total / 1_048_576:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
