"""命令行入口。"""

import argparse
import sys
from pathlib import Path

from .config import Config
from .publisher import Publisher


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="okf-zhihu-publisher",
        description="将 OKF 知识包批量发布到知乎知识库",
    )
    parser.add_argument(
        "--access-secret",
        help="知乎开放平台 Access Secret（也可通过 ZHIHU_ACCESS_SECRET 环境变量设置）",
    )
    parser.add_argument(
        "--base-url",
        default="https://developer.zhihu.com/api/v1",
        help="API 基础 URL",
    )
    parser.add_argument(
        "--state-file",
        default="publish-state.json",
        help="状态文件路径",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="详细输出"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # sync 子命令
    sync_p = subparsers.add_parser("sync", help="同步知识包到知乎知识库")
    sync_p.add_argument(
        "--bundles-dir",
        required=True,
        help="OKF bundles 根目录",
    )
    sync_p.add_argument(
        "--domain",
        help="只同步指定域（如 jishu）",
    )
    sync_p.add_argument(
        "--top-n",
        type=int,
        help="只同步前 N 个 bundle",
    )
    sync_p.add_argument(
        "--bundles",
        help="只同步指定的 bundle（逗号分隔，如 ai-agent,rag,mcp）",
    )
    sync_p.add_argument(
        "--kb-id",
        help="目标知识库 ID（不指定则使用默认知识库）",
    )
    sync_p.add_argument(
        "--dry-run",
        action="store_true",
        help="预览操作，不实际上传",
    )

    # status 子命令
    status_p = subparsers.add_parser("status", help="查看同步状态")
    status_p.add_argument(
        "--bundles-dir",
        default="doc/bundles",
        help="OKF bundles 根目录",
    )

    # list-kb 子命令
    list_p = subparsers.add_parser("list-kb", help="列出知识库")
    list_p.add_argument(
        "--scope",
        default="all",
        choices=["all", "created", "subscribed"],
        help="范围",
    )

    # quota 子命令
    quota_p = subparsers.add_parser("quota", help="查看额度")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # 构建配置
    config = Config.from_env()
    if args.access_secret:
        config.access_secret = args.access_secret
    config.base_url = args.base_url
    config.state_file = Path(args.state_file)
    config.verbose = args.verbose

    if args.command == "sync":
        config.bundles_dir = Path(args.bundles_dir)
        config.domain_filter = args.domain
        config.top_n = args.top_n
        config.default_kb_id = args.kb_id
        config.dry_run = args.dry_run

        # 解析 bundle 白名单
        bundle_whitelist = None
        if args.bundles:
            bundle_whitelist = {
                b.strip() for b in args.bundles.split(",") if b.strip()
            }

        errors = config.validate()
        if errors:
            for e in errors:
                print(f"❌ {e}", file=sys.stderr)
            return 1

        pub = Publisher(config)
        pub.sync(
            domain_filter=config.domain_filter,
            top_n=config.top_n,
            bundle_whitelist=bundle_whitelist,
            dry_run=config.dry_run,
        )
        return 0

    elif args.command == "status":
        config.bundles_dir = Path(args.bundles_dir)
        pub = Publisher(config)
        status = pub.status()
        print("📊 同步状态")
        print(f"  已跟踪文件数：{status['total_tracked']}")
        print(f"  默认知识库：{status['default_kb_id'] or '未设置'}")
        return 0

    elif args.command == "list-kb":
        from .api_client import ZhihuKbApiClient

        if not config.access_secret:
            print("❌ 请设置 ZHIHU_ACCESS_SECRET", file=sys.stderr)
            return 1

        with ZhihuKbApiClient(config.access_secret, config.base_url) as api:
            kbs = api.list_knowledge_bases(scope=args.scope)
            print(f"📚 知识库列表（{len(kbs)} 个）")
            for kb in kbs:
                flag = " ★默认" if kb.is_default else ""
                print(f"  [{kb.knowledge_base_id}] {kb.name}{flag}")
                print(f"      内容数：{kb.content_count}，可见性：{kb.visibility}")
        return 0

    elif args.command == "quota":
        from .api_client import ZhihuKbApiClient

        if not config.access_secret:
            print("❌ 请设置 ZHIHU_ACCESS_SECRET", file=sys.stderr)
            return 1

        with ZhihuKbApiClient(config.access_secret, config.base_url) as api:
            quotas = api.get_quota()
            print("💰 额度信息")
            for q in quotas:
                print(
                    f"  {q.api_name} ({q.api_id}): "
                    f"{q.remaining_quota}/{q.total_quota} 剩余"
                )
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
