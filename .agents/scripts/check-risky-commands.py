#!/usr/bin/env python3
"""高风险操作拦截检查CLI工具。

用于CI/pre-commit中检查脚本/命令中的高风险操作，也可作为Python库被其他脚本调用。

用法::

    # 检查文件中是否包含高风险命令
    python check-risky-commands.py <file>

    # 从stdin读取命令进行检查
    echo "rm -rf /" | python check-risky-commands.py --stdin

    # 检查单个命令字符串
    python check-risky-commands.py --command "git push --force"

    # 只检查CRITICAL级别（不阻断HIGH）
    python check-risky-commands.py --min-level CRITICAL <file>

    # 详细模式：显示所有匹配过程和决策追踪
    python check-risky-commands.py -v --command "rm -rf /"

    # 调试模式：显示每个正则模式的命中/未命中详情（最详细）
    python check-risky-commands.py -vv --command "rm -rf /prod/db"
"""
from __future__ import annotations


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import logging
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.risk_interceptor import (
    RISK_LEVEL_NAMES,
    RiskLevel,
    assess_risk,
    format_intercept_template,
)

logger = logging.getLogger("check_risky_commands")


def _level_from_name(name: str) -> RiskLevel:
    try:
        return RiskLevel[name.upper()]
    except KeyError:
        valid = ", ".join(RISK_LEVEL_NAMES.values())
        print(f"错误：无效的风险等级 '{name}'，有效值: {valid}", file=sys.stderr)
        sys.exit(2)


def _setup_logging(verbosity: int) -> None:
    """配置日志级别。

    verbosity=0: 静默模式（默认），不添加任何日志handler，仅print输出业务结果
    verbosity=1 (-v): INFO级别，显示评估开始/结束、最终判定结果
    verbosity=2 (-vv): DEBUG级别，显示每个模式匹配详情、决策过程
    verbosity=3+ (-vvv): 最详细（包括未命中的模式，TRACE级别5）
    """
    if verbosity == 0:
        for log_name in ("risk_interceptor", "check_risky_commands"):
            log = logging.getLogger(log_name)
            log.handlers.clear()
            log.addHandler(logging.NullHandler())
            log.setLevel(logging.CRITICAL + 1)
            log.propagate = False
        return

    if verbosity == 1:
        level = logging.INFO
    elif verbosity == 2:
        level = logging.DEBUG
    else:
        level = 5

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    fmt = logging.Formatter(
        "[%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(fmt)

    for log_name in ("risk_interceptor", "check_risky_commands"):
        log = logging.getLogger(log_name)
        log.setLevel(level)
        log.handlers.clear()
        log.addHandler(handler)
        log.propagate = False


def check_text(text: str, source: str, min_level: RiskLevel) -> int:
    """检查文本中的风险命令，返回退出码。"""
    logger.info("check_text: source=%s, min_level=%s, text_length=%d",
                  source, RISK_LEVEL_NAMES.get(min_level, str(min_level)), len(text))

    assessment = assess_risk(text, source=source)

    logger.info("check_text 结果: level=%s, signals=%d, requires_confirmation=%s",
                  RISK_LEVEL_NAMES.get(assessment.level, str(assessment.level)),
                  len(assessment.signals),
                  assessment.requires_confirmation)

    if assessment.level < min_level:
        if assessment.level > RiskLevel.SAFE:
            logger.info("风险等级 %s 低于阻断阈值 %s，仅提示不阻断",
                          RISK_LEVEL_NAMES.get(assessment.level, str(assessment.level)),
                          RISK_LEVEL_NAMES.get(min_level, str(min_level)))
            print(f"  [{source}] 检测到{RISK_LEVEL_NAMES[assessment.level]}级风险信号（低于阻断阈值，仅提示）")
            for sig in assessment.signals:
                print(f"    - {sig.description}: `{sig.matched_text}`")
        else:
            logger.debug("无风险信号，返回退出码0")
        return 0

    logger.warning("风险等级 %s >= 阻断阈值 %s，触发拦截输出",
                     RISK_LEVEL_NAMES.get(assessment.level, str(assessment.level)),
                     RISK_LEVEL_NAMES.get(min_level, str(min_level)))

    print(f"{'=' * 60}")
    print(f"🚨 [{source}] 检测到{RISK_LEVEL_NAMES[assessment.level]}级高风险操作！")
    print(f"{'=' * 60}")
    print()
    print(format_intercept_template(assessment))
    print()
    print(f"{'=' * 60}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="高风险操作拦截检查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="要检查的文件路径",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="从标准输入读取内容检查",
    )
    parser.add_argument(
        "--command",
        metavar="CMD",
        help="直接检查单个命令字符串",
    )
    parser.add_argument(
        "--min-level",
        default="HIGH",
        choices=list(RISK_LEVEL_NAMES.values()),
        help="阻断的最低风险等级（默认HIGH）",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="详细输出（-v=INFO, -vv=DEBUG, -vvv=TRACE）。日志输出到stderr。",
    )

    args = parser.parse_args()
    _setup_logging(args.verbose)

    logger.info("=== check-risky-commands 启动 ===")
    logger.debug("参数: files=%s, stdin=%s, command=%s, min_level=%s, verbose=%d",
                   args.files, args.stdin, bool(args.command), args.min_level, args.verbose)

    min_level = _level_from_name(args.min_level)
    logger.info("阻断阈值: %s", RISK_LEVEL_NAMES.get(min_level, str(min_level)))

    exit_code = 0
    sources_checked = 0

    if args.command:
        logger.info("检查单个命令: %s", args.command[:80])
        code = check_text(args.command, "<command>", min_level)
        exit_code = max(exit_code, code)
        sources_checked += 1

    if args.stdin:
        logger.info("从stdin读取内容...")
        content = sys.stdin.read()
        if content.strip():
            logger.debug("stdin读取完成，长度=%d字符", len(content))
            code = check_text(content, "<stdin>", min_level)
            exit_code = max(exit_code, code)
            sources_checked += 1
        else:
            logger.warning("stdin内容为空，跳过检查")

    for filepath in args.files:
        path = Path(filepath)
        logger.info("检查文件: %s", filepath)
        if not path.exists():
            logger.error("文件不存在: %s", filepath)
            print(f"⚠️  文件不存在，跳过: {filepath}", file=sys.stderr)
            continue
        content = None
        read_errors = []
        for enc in ("utf-8", "utf-8-sig", "gbk", "gb18030", "latin-1"):
            try:
                content = path.read_text(encoding=enc)
                if enc != "utf-8":
                    logger.debug("文件读取成功（编码=%s），长度=%d字符", enc, len(content))
                else:
                    logger.debug("文件读取成功，长度=%d字符", len(content))
                break
            except (OSError, UnicodeDecodeError) as e:
                read_errors.append(f"{enc}: {e}")
        if content is None:
            err_detail = "; ".join(read_errors)
            logger.error("无法读取文件 %s（尝试了utf-8/gbk/gb18030/latin-1编码）: %s", filepath, err_detail[:200])
            print(f"⚠️  无法读取文件 {filepath}（编码问题）", file=sys.stderr)
            continue
        code = check_text(content, str(filepath), min_level)
        exit_code = max(exit_code, code)
        sources_checked += 1

    logger.info("检查完成: 共检查 %d 个来源，最终退出码=%d", sources_checked, exit_code)

    if exit_code == 0:
        print("✅ 未检测到高风险操作。")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

