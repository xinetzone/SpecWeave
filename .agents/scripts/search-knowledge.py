#!/usr/bin/env python3
"""知识库检索 CLI 工具。

支持全文搜索、多维标签筛选、完整性过滤等综合检索能力。

用法：
  python search-knowledge.py "加密"                    # 全文搜索
  python search-knowledge.py "方法论" --type metacognitive  # 组合搜索
  python search-knowledge.py "" --type procedural          # 按类型筛选
  python search-knowledge.py "" --status verified          # 已验证条目
  python search-knowledge.py "" --level internal           # 内部条目
  python search-knowledge.py "" --tag security             # 按标签筛选
  python search-knowledge.py "review" --max 10             # 限制结果数
  python search-knowledge.py "query" --json                # JSON 输出
  python search-knowledge.py "query" --include-damaged     # 包含损坏条目
  python search-knowledge.py "query" --stats-only          # 仅统计信息
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.knowledge_search import search_knowledge, sanitize_query
from lib.knowledge_classification import (
    VALID_KNOWLEDGE_TYPES,
    VALID_VALIDATION_STATUSES,
)


def main():
    parser = argparse.ArgumentParser(
        description="知识库检索 CLI 工具",
    )
    parser.add_argument(
        "query", nargs="?", default="",
        help="搜索关键词（留空则仅按标签筛选）",
    )
    parser.add_argument(
        "--type", dest="knowledge_type",
        choices=sorted(VALID_KNOWLEDGE_TYPES),
        help="按知识类型筛选",
    )
    parser.add_argument(
        "--status", dest="validation_status",
        choices=sorted(VALID_VALIDATION_STATUSES),
        help="按验证状态筛选",
    )
    parser.add_argument(
        "--level", dest="security_level",
        choices=["public", "internal", "confidential"],
        help="按安全级别筛选",
    )
    parser.add_argument(
        "--tag", action="append", dest="tags",
        help="按标签筛选（可多次指定）",
    )
    parser.add_argument(
        "--max", type=int, default=20,
        help="最大返回结果数（默认 20）",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="以 JSON 格式输出",
    )
    parser.add_argument(
        "--include-damaged", action="store_true",
        help="包含损坏条目",
    )
    parser.add_argument(
        "--stats-only", action="store_true",
        help="仅输出统计信息",
    )

    args = parser.parse_args()

    # 查询安全验证
    if args.query:
        sanitized, safe, err = sanitize_query(args.query)
        if not safe:
            print(f"查询不安全: {err}", file=sys.stderr)
            return 1
    else:
        sanitized = ""

    # 执行搜索
    result = search_knowledge(
        query=sanitized,
        knowledge_type=args.knowledge_type,
        validation_status=args.validation_status,
        security_level=args.security_level,
        tags=args.tags,
        max_results=args.max,
        exclude_damaged=not args.include_damaged,
    )

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.stats_only:
        print(json.dumps(result["stats"], indent=2, ensure_ascii=False))
        return 0

    # 文本输出
    print(f"检索结果: {result['filtered']} / {result['total']} 个条目")
    if result["query"]:
        print(f"查询: \"{result['query']}\"")
    if args.knowledge_type:
        print(f"类型: {args.knowledge_type}")
    if args.validation_status:
        print(f"状态: {args.validation_status}")
    if args.security_level:
        print(f"安全级别: {args.security_level}")
    if args.tags:
        print(f"标签: {', '.join(args.tags)}")
    print()

    if result["damaged"]:
        print(f"⚠ 已排除 {len(result['damaged'])} 个损坏条目")
        print()

    if not result["results"]:
        print("无匹配结果")
        return 0

    for i, r in enumerate(result["results"], 1):
        title = r.get("title", "?")
        file_path = r.get("file", "")
        kt = r.get("knowledge_type", "")
        vs = r.get("validation_status", "")
        score = r.get("score", 0)
        integrity = r.get("integrity_status", "?")

        line = f"{i}. {title}"
        if score > 0:
            line += f" [score={score}]"
        if args.include_damaged:
            line += f" [{integrity}]"
        print(line)
        print(f"   docs/knowledge/{file_path}  {kt}  {vs}")

        matched = r.get("matched_keywords", [])
        if matched:
            print(f"   匹配关键词: {', '.join(matched)}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())