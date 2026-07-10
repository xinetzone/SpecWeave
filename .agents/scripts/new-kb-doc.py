#!/usr/bin/env python3
"""新建知识库/复盘/规范文档，自动生成符合项目规范的YAML frontmatter骨架。

解决手动复制模板容易遗漏字段的问题。支持多种文档类型，自动计算x-toml-ref路径。

用法:
    python new-kb-doc.py <filename> --title "标题" --type knowledge
    python new-kb-doc.py 14-new-chapter.md --title "新章节" --type knowledge
    python new-kb-doc.py retrospective-my-project-20260710/README.md --title "项目复盘" --type retrospective
    python new-kb-doc.py new-pattern.md --title "新模式" --type pattern --category methodology

设计原则:
    1. 不覆盖已存在文件（安全优先）
    2. 自动计算相对路径和x-toml-ref
    3. 自动填充日期、初始版本、draft状态
    4. 支持知识库/复盘/模式/Spec等多种文档类型
"""

import argparse
import sys
from datetime import date
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import print_pass, print_warn, print_error, print_header

PROJECT_ROOT = SCRIPTS_DIR.parent.parent

DOC_TYPES = {
    'knowledge': {
        'required_fields': ['id', 'title', 'category', 'date', 'version', 'status'],
        'optional_fields': ['source', 'tags', 'maturity'],
        'default_status': 'draft',
        'default_category': 'knowledge',
        'toml_subdir': 'docs/knowledge',
    },
    'retrospective': {
        'required_fields': ['id', 'title', 'date', 'source', 'type', 'status', 'version'],
        'optional_fields': ['tags', 'session_id', 'x-toml-ref', 'maturity'],
        'default_status': 'draft',
        'default_category': None,
        'toml_subdir': 'docs/retrospective',
    },
    'pattern': {
        'required_fields': ['id', 'title', 'date', 'status', 'version', 'maturity'],
        'optional_fields': ['category', 'tags', 'source'],
        'default_status': 'draft',
        'default_category': 'methodology-patterns',
        'toml_subdir': 'docs/retrospective/patterns',
    },
    'spec': {
        'required_fields': ['id', 'title', 'date', 'status', 'version'],
        'optional_fields': ['category', 'tags'],
        'default_status': 'draft',
        'default_category': 'spec',
        'toml_subdir': '.trae/specs',
    },
}


def compute_toml_ref(file_path: Path, doc_type: str) -> str:
    """计算x-toml-ref相对路径（从文件所在目录到.meta/toml/下对应位置）。"""
    try:
        rel_path = file_path.resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        return ''

    depth = len(rel_path.parts) - 1
    prefix = '../' * depth
    toml_rel = str(rel_path.with_suffix('.toml')).replace('\\', '/')
    toml_path = f'.meta/toml/{toml_rel}'
    return prefix + toml_path


def generate_frontmatter(
    doc_id: str,
    title: str,
    doc_type: str,
    category: str | None,
    source: str | None,
    tags: list[str] | None,
    file_path: Path,
) -> str:
    """生成YAML frontmatter字符串。"""
    config = DOC_TYPES[doc_type]
    today = date.today().isoformat()

    lines = ['---']
    lines.append(f'id: "{doc_id}"')
    lines.append(f'title: "{title}"')

    if category and 'category' in (config['required_fields'] + config['optional_fields']):
        lines.append(f'category: "{category}"')

    lines.append(f'date: "{today}"')

    if 'source' in config['required_fields']:
        lines.append(f'source: ""')
    elif source and 'source' in config['optional_fields']:
        lines.append(f'source: ""')

    if doc_type == 'retrospective':
        retro_type = 'project'
        lines.append(f'type: "{retro_type}"')

    lines.append(f'status: "draft"')
    lines.append(f'version: "0.1"')

    if tags:
        tags_str = ', '.join(f'"{t}"' for t in tags)
        lines.append(f'tags: [{tags_str}]')

    if doc_type == 'retrospective':
        lines.append(f'session_id: ""')

    toml_ref = compute_toml_ref(file_path, doc_type)
    if toml_ref:
        lines.append(f'x-toml-ref: "{toml_ref}"')

    if 'maturity' in (config['required_fields'] + config['optional_fields']) and doc_type == 'pattern':
        lines.append(f'maturity: "L1"')

    lines.append('---')
    return '\n'.join(lines)


def generate_body(title: str, doc_type: str) -> str:
    """生成文档初始正文骨架。"""
    if doc_type == 'knowledge':
        return f'\n# {title}\n\n---\n\n## 1. 概述\n\n（在此处编写内容）\n'
    elif doc_type == 'retrospective':
        return f'\n# {title}\n\n> 📅 {date.today().isoformat()} | 类型：项目复盘（project）| 状态：🚧 草稿\n>\n> **项目本质**：（在此处简述复盘对象）\n\n## 执行摘要\n\n（在此处编写执行摘要）\n'
    elif doc_type == 'pattern':
        return f'\n# {title}\n\n## 模式描述\n\n（在此处描述模式的核心要素）\n\n## 适用场景\n\n（在此处列出适用场景）\n'
    elif doc_type == 'spec':
        return f'\n# {title}\n\n## 目标\n\n（在此处描述目标）\n'
    return f'\n# {title}\n\n（在此处编写内容）\n'


def derive_id_from_filename(file_path: Path) -> str:
    """从文件名推导id。

    - 文件名为README.md时，使用父目录名
    - 其他情况使用文件名stem
    """
    stem = file_path.stem
    if stem.lower() == 'readme':
        parent = file_path.parent
        if parent != Path('.'):
            return parent.name
    return stem


def main():
    parser = argparse.ArgumentParser(
        description='新建文档 - 自动生成符合项目规范的YAML frontmatter骨架',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s 14-new-topic.md --title "新主题" --type knowledge
  %(prog)s retrospective-my-proj-20260710/README.md --title "我的项目复盘" --type retrospective
  %(prog)s new-pattern.md --title "新模式名" --type pattern
        """
    )
    parser.add_argument('filename', help='要创建的文件路径（相对于当前目录）')
    parser.add_argument('--title', required=True, help='文档标题')
    parser.add_argument('--type', required=True, choices=list(DOC_TYPES.keys()),
                        help='文档类型: knowledge(知识库)/retrospective(复盘)/pattern(模式)/spec(规划)')
    parser.add_argument('--category', help='文档分类（可选，有默认值）')
    parser.add_argument('--source', help='来源信息（可选）')
    parser.add_argument('--tag', action='append', dest='tags', help='标签（可多次指定）')
    parser.add_argument('--id', help='文档ID（默认从文件名推导）')
    parser.add_argument('--dry-run', action='store_true', help='仅显示将要生成的内容，不创建文件')

    args = parser.parse_args()

    file_path = Path(args.filename).resolve()

    if file_path.exists() and not args.dry_run:
        print_error(f"文件已存在，拒绝覆盖: {file_path}")
        return 1

    doc_id = args.id or derive_id_from_filename(file_path)

    config = DOC_TYPES[args.type]
    category = args.category or config.get('default_category')

    frontmatter = generate_frontmatter(
        doc_id=doc_id,
        title=args.title,
        doc_type=args.type,
        category=category,
        source=args.source,
        tags=args.tags,
        file_path=file_path,
    )
    body = generate_body(args.title, args.type)
    content = frontmatter + body

    print_header("新建文档")
    print(f"  文件: {file_path}")
    print(f"  类型: {args.type}")
    print(f"  ID: {doc_id}")
    print(f"  标题: {args.title}")
    if category:
        print(f"  分类: {category}")
    print()

    if args.dry_run:
        print_warn("[DRY RUN] 以下内容将被写入文件：")
        print()
        print(content)
        return 0

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding='utf-8')

    print_pass(f"文件创建成功: {file_path}")
    print(f"  提示: status初始为draft，完成后请更新为completed")
    print(f"  提示: source字段初始为空，请补充来源信息")

    return 0


if __name__ == '__main__':
    sys.exit(main())
