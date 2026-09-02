"""CLI：`python -m agent_monetize demo` 跑通沙箱闭环；`--help` 查看用法。"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import Any

from . import __version__
from .channels.content_pricing import ContentPricingChannel
from .channels.data_service import DataServiceChannel
from .channels.registry import ChannelRegistry
from .channels.rest_report import RestReportChannel
from .config import Config, load_config
from .core.ffi_bridge import FfiBridge, default_bridge
from .core.loop import AgentLoop

APP_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_CONFIG = os.path.join(APP_ROOT, "config.yaml")


def _resolve(path: str, base: str) -> str:
    return path if os.path.isabs(path) else os.path.join(base, path)


def build_registry(config: Config) -> ChannelRegistry:
    """按配置构建通道注册表（沙箱通道默认启用；真实适配器默认关闭）。"""
    registry = ChannelRegistry()

    cc = config.channels.get("content_pricing")
    if cc is not None and cc.enabled:
        registry.register(ContentPricingChannel(cc.params, seed=config.app.seed))

    dc = config.channels.get("data_service")
    if dc is not None and dc.enabled:
        registry.register(DataServiceChannel(dc.params, seed=config.app.seed + 1))

    rc = config.channels.get("rest_report")
    if rc is not None and rc.enabled:
        registry.register(
            RestReportChannel(
                rc.params,
                seed=config.app.seed + 2,
                enable_real=bool(rc.params.get("enable_real", False)),
                confirmed_behaviors=list(config.compliance.confirmed_behaviors),
            )
        )
    return registry


def build_bridge(config: Config) -> FfiBridge:
    """按配置构建 ffi 桥接器：探测 → 原生 → 参考实现降级。"""
    native_paths = []
    if config.ffi.native_lib:
        native_paths.append(_resolve(config.ffi.native_lib, APP_ROOT))
    return default_bridge(
        native_lib_paths=native_paths, fallback_to_reference=config.ffi.fallback_to_reference
    )


def run_demo(config: Config, verbose: bool = True) -> dict[str, Any]:
    """跑通沙箱闭环：机会发现 → 决策 → 执行 → 反馈 → 进化。"""
    registry = build_registry(config)
    bridge = build_bridge(config)
    loop = AgentLoop(config=config, registry=registry, bridge=bridge)

    print("=" * 64)
    print(f"agent-monetize v{__version__} —— 智能体自动变现平台（沙箱演示）")
    print(f"FFI 后端：{bridge.backend}（tvm_ffi 可用={bridge.tvm_ffi_available}）")
    print(f"通道：{', '.join(c.channel_id for c in registry.enabled())}")
    print("=" * 64)

    records = loop.run(config.loop.rounds)
    summary = loop.summary()

    if verbose:
        print("\n--- 每轮日志 ---")
        running_balance = 0.0
        for rec in records:
            d = rec.decision
            if d.action == "act":
                assert rec.action_result is not None
                running_balance = round(running_balance + rec.action_result.net, 3)
                print(
                    f"[round {rec.round:>2}] 行动 -> {d.channel_id:<16} "
                    f"score={d.score:.3f} net={rec.action_result.net:+.2f} "
                    f"balance={running_balance:.2f}"
                )
            else:
                print(f"[round {rec.round:>2}] 待时 -> (no-op)  {d.reason}")

    print("\n--- 最终收益（沙箱虚拟货币） ---")
    print(f"总轮数   : {summary['rounds']}")
    print(f"总收入   : {summary['total_revenue']:.2f}")
    print(f"总成本   : {summary['total_cost']:.2f}")
    print(f"净收益   : {summary['balance']:.2f}")
    print("--- 各通道 ---")
    for cid, ch in summary["channels"].items():
        print(
            f"  {cid:<16} weight={ch['weight']:.3f} revenue={ch['revenue']:.2f} "
            f"cost={ch['cost']:.2f} net={ch['net']:+.2f} actions={ch['actions']}"
        )
    print("=" * 64)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-monetize",
        description="Python 3.14+ 智能体自动变现平台（沙箱虚拟货币演示，不接真实资金）",
    )
    parser.add_argument("--version", action="version", version=f"agent-monetize {__version__}")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="YAML 配置文件路径")
    parser.add_argument("--rounds", type=int, default=None, help="覆盖配置中的循环轮数")
    sub = parser.add_subparsers(dest="command", help="子命令")
    sub.add_parser("demo", help="跑通沙箱闭环（机会发现→决策→执行→反馈→进化）")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

    config = load_config(args.config)
    if args.rounds is not None:
        config.loop.rounds = args.rounds

    if args.command == "demo":
        run_demo(config)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI 入口
    sys.exit(main())
