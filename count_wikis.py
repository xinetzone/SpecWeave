"""统计 docs/knowledge/learning 下各分类 Wiki 数量（一次性迁移辅助脚本，已退役）。

历史：本脚本服务 2026-08 的 docs/knowledge 迁移，最终统计 151 个 Wiki 并与
CATEGORIES.md 对账一致，结论固化在
.trae/specs/migration-archival/docs-to-knowledge-okf-migration/review.md。
原 base 硬编码为本机绝对路径 d:\\AI\\docs\\knowledge\\learning，在其他机器上
必然 FileNotFoundError；其后 learning 目录整体重组，0x 分类与 -wiki 目录结构
在主仓已不存在，内容迁入 OKF 知识包子模块
projects/awesome-okf-xs/doc/bundles/，知识包清单由该子模块
doc/_ext/okf_inventory_builder.py 权威维护。

2026-11-16 修复：base 改为基于 __file__ 的仓库自定位路径；目标缺失时输出
显式退役诊断并以退出码 2 结束，替代裸崩溃或误导性的零计数。原统计逻辑
原样保留在 main(base) 中，对仍持有旧结构归档的检出仍可复用。
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_BASE = REPO_ROOT / "docs" / "knowledge" / "learning"

NON_WIKI_WIKIS = {
    'first-principles', 'deep-learning-atomic-design', 'ai-engineering-notes',
    'causal-ai', 'atomic-emergence', 'quantdinger', 'ai-switch-governance',
    'rqndd', 'miaowu',
    # 无 -wiki 后缀但有 README.md 的 wiki 目录
    'pyinvoke-wiki', 'executablebooks-myst-guide', 'mdx-graphql-guide',
    'myst-markdown-tutorial',
    'baidu', 'deepseek', 'google-cloud', 'openai', 'oray',
    'conda-dev-github-wiki', 'conda-dev-source-wiki', 'git-baidu-sync',
    'ai-powershell5-hell-wiki',
}


def main(base):
    if not Path(base).is_dir():
        sys.stderr.write(
            "count_wikis.py 已退役：统计目标不存在\n"
            f"  期望路径: {base}\n"
            "  原因: docs/knowledge/learning 的 0x 分类与 -wiki 目录结构已整体重组，\n"
            "        内容迁入 OKF 知识包子模块 projects/awesome-okf-xs/doc/bundles/。\n"
            "  历史结论: 迁移最终统计 151 个 Wiki，见\n"
            "        .trae/specs/migration-archival/docs-to-knowledge-okf-migration/review.md\n"
            "  现行清单: projects/awesome-okf-xs/doc/_ext/okf_inventory_builder.py\n"
        )
        return 2

    base = str(base)
    categories = sorted([d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)) and (d.startswith('0') or d.startswith('10-'))])

    result = {}
    for cat in categories:
        cat_path = os.path.join(base, cat)
        wiki_dirs_all = []
        single_md_all = []
        for root, dirs, files in os.walk(cat_path):
            rel = os.path.relpath(root, base)
            parts = rel.split(os.sep)
            # Count all wiki dirs at any depth >= 2 (cat/subdir or deeper)
            if len(parts) >= 2:
                name = parts[-1]
                if "README.md" in files and not name.startswith('.') and not name.startswith('_'):
                    if name.endswith("-wiki") or name in NON_WIKI_WIKIS:
                        wiki_dirs_all.append(name)
            # Count single -wiki.md files at ANY depth (>= 1, includes root of cat)
            if len(parts) >= 1:
                for f in files:
                    if f.endswith("-wiki.md"):
                        single_md_all.append(f)
        result[cat] = {"wiki_dirs": sorted(set(wiki_dirs_all)), "single_md": sorted(set(single_md_all))}

    total_all = 0
    print("=" * 80)
    print("FINAL COUNT (wiki dirs + single -wiki.md files at all depths)")
    print("=" * 80)
    for cat, counts in result.items():
        w = counts['wiki_dirs']
        s = counts['single_md']
        t = len(w) + len(s)
        total_all += t
        print(f"{cat}: wiki_dirs({len(w)})  single_md({len(s)})  total={t}")
        if len(w) <= 20:
            print(f"  dirs: {w}")
        else:
            print(f"  dirs: {w[:10]}... ({len(w)} total)")
        if s:
            print(f"  md:   {s}")

    print(f"\nGrand total: {total_all}")
    return 0


if __name__ == "__main__":
    sys.exit(main(DEFAULT_BASE))
