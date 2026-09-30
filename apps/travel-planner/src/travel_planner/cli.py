"""命令行入口：``travel-planner serve`` 启动本地 Web，``travel-planner check`` 自检。"""

import argparse
import sys

from . import __version__
from .config import (
    AppConfig,
    ensure_data_dir,
    load_llm_config,
    resolve_data_dir,
)
from .lock import InstanceLock


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="travel-planner",
        description="旅行规划工作台：本地多行程编排/预算/打包清单 + BYOK AI 行程草稿",
    )
    parser.add_argument("--version", action="version", version=f"travel-planner {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="启动本地 Web 服务（仅 127.0.0.1）")
    serve.add_argument("--data-dir", default=None, help="数据目录（默认 playground/travel-planner/data）")
    serve.add_argument("--host", default="127.0.0.1", help="监听地址（仅允许回环）")
    serve.add_argument("--port", type=int, default=8765, help="监听端口（默认 8765）")

    check = sub.add_parser("check", help="检查数据目录与 LLM 配置状态")
    check.add_argument("--data-dir", default=None, help="数据目录")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "serve":
        return _serve(args)
    if args.command == "check":
        return _check(args)
    parser.print_help()
    return 2


def _serve(args: argparse.Namespace) -> int:
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        print(f"拒绝监听非回环地址：{args.host}（本应用仅限本机使用）", file=sys.stderr)
        return 1
    try:
        data_dir = ensure_data_dir(resolve_data_dir(args.data_dir))
    except Exception as exc:  # ConfigError 等
        print(f"启动失败：{exc}", file=sys.stderr)
        return 1
    config = AppConfig(data_dir=data_dir, host=args.host, port=args.port)
    lock = InstanceLock(data_dir)
    try:
        lock.acquire_nowait()
    except Exception as exc:
        print(f"启动失败：{exc}", file=sys.stderr)
        return 1
    from .storage import TripStore
    from .web.app import create_app

    app = create_app(TripStore(data_dir, backup_keep=config.backup_keep), load_llm_config(data_dir))
    print(f"travel-planner 已就绪：http://{config.host}:{config.port}/（数据目录 {data_dir}）")
    try:
        import uvicorn

        uvicorn.run(app, host=config.host, port=config.port, log_level="warning")
    except KeyboardInterrupt:
        pass
    finally:
        lock.release()
    return 0


def _check(args: argparse.Namespace) -> int:
    try:
        data_dir = ensure_data_dir(resolve_data_dir(args.data_dir))
    except Exception as exc:
        print(f"[✗] {exc}")
        return 1
    print(f"[✓] 数据目录：{data_dir}")
    from .storage import TripStore

    store = TripStore(data_dir)
    trips = store.list_trips()
    print(f"[✓] 行程数量：{len(trips)}")
    for err in store.load_errors:
        print(f"[!] 损坏文件已忽略：{err}")
    llm = load_llm_config(data_dir)
    if llm.configured:
        key_from = "环境变量" if __import__("os").environ.get("TRAVEL_PLANNER_API_KEY") else "config.yaml"
        print(f"[✓] LLM 已配置：{llm.model} @ {llm.base_url}（密钥来源 {key_from}，超时 {llm.timeout:.0f}s）")
    else:
        print("[!] LLM 未配置：AI 行程生成不可用，其余功能不受影响（配置见 README）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
