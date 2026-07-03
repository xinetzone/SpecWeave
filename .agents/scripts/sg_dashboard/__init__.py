"""sg-dashboard — 阶段守卫日志聚合可视化仪表盘生成工具。

基于 [SG-LOG]/[PDR-LOG] 结构化日志，聚合分析后生成自包含HTML仪表盘。

拆分结构（遵循单一职责原则）：
- constants: 正则表达式、阶段顺序/名称、事件集合
- models: 数据模型（LogEntry/SessionStats/AggregateStats）
- parser: 日志解析+文件收集（parse_ctx/parse_log_file/collect_log_files）
- aggregator: 统计聚合（aggregate_entries）
- charts: Mermaid图表生成（pie/xychart）
- demo: Demo演示数据生成
- renderer: HTML渲染（CSS+模板+Mermaid初始化）
- cli: argparse命令行入口

使用方式：
  # 使用内置demo数据生成仪表盘
  python -m sg_dashboard --demo

  # 扫描日志目录生成仪表盘
  python -m sg_dashboard --log-dir .agents/logs/

  # 输出JSON统计数据
  python -m sg_dashboard --demo --json
"""

import sys


def main() -> None:
    from .cli import main as _main
    sys.exit(_main())


__all__ = ["main"]
