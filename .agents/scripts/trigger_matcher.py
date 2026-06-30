#!/usr/bin/env python3
"""触发词三级信号匹配器（Keyless 渐进式披露模式）

从 SKILL.md 解析 T0/T1/T2 触发词配置，对输入文本进行逐级匹配，
输出详细的匹配过程日志，记录每个信号级的扫描、命中、决策全过程。

用法：
  python trigger_matcher.py "画个流程图"
  python trigger_matcher.py "这个图不错" --verbose
  python trigger_matcher.py "检查mermaid" --cmd-log
  python trigger_matcher.py "生成时序图" --json
  python trigger_matcher.py "画个流程图" --fuzzy -v   # 模糊匹配变体
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from lib.project import resolve_project_root
from lib.cli import setup_safe_output

SKILLS_DIR = ".agents/skills"

# CMD-LOG 事件常量
EVENT_START = "TRIGGER_START"
EVENT_SCAN = "TIER_SCAN_START"
EVENT_HIT = "TRIGGER_HIT"
EVENT_MISS = "TRIGGER_MISS"
EVENT_TIER_MATCHED = "TIER_MATCHED"
EVENT_TIER_NO_MATCH = "TIER_NO_MATCH"
EVENT_NO_MATCH = "TRIGGER_NO_MATCH"
EVENT_FUZZY_HIT = "TRIGGER_FUZZY_HIT"
EVENT_LOAD_DECISION = "LOAD_DECISION"

# 信号级到匹配事件的映射
TIER_EVENTS = {"T0": "TRIGGER_T0_MATCH", "T1": "TRIGGER_T1_MATCH", "T2": "TRIGGER_T2_MATCH"}

# ANSI 颜色
COLORS = {
    "INFO": "\033[92m",
    "DEBUG": "\033[90m",
    "WARN": "\033[93m",
    "ERROR": "\033[91m",
}
RESET = "\033[0m"
TIER_COLORS = {"T0": "\033[90m", "T1": "\033[94m", "T2": "\033[95m"}


@dataclass
class TriggerTier:
    """单个信号级的触发词配置"""
    level: str
    name: str
    triggers: list[str] = field(default_factory=list)
    action: str = ""


@dataclass
class TierMatchResult:
    """单个信号级的匹配结果"""
    level: str
    name: str
    matched: list[str] = field(default_factory=list)
    unmatched: list[str] = field(default_factory=list)
    fuzzy_matched: list[str] = field(default_factory=list)

    @property
    def is_matched(self) -> bool:
        return len(self.matched) > 0 or len(self.fuzzy_matched) > 0

    @property
    def all_matched(self) -> list[str]:
        return self.matched + self.fuzzy_matched


class Logger:
    """统一日志输出，支持人类可读和 CMD-LOG 两种格式"""

    def __init__(self, cmd_log: bool = False, verbose: bool = False, json_mode: bool = False):
        self.cmd_log = cmd_log
        self.verbose = verbose
        self.json_mode = json_mode
        self.entries: list[dict] = []

    def log(self, level: str, event: str, msg: str, ctx: Optional[dict] = None) -> None:
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        ctx = ctx or {}

        entry = {"timestamp": ts, "level": level, "event": event, "msg": msg, "ctx": ctx}
        self.entries.append(entry)

        if self.json_mode:
            return

        if level == "DEBUG" and not self.verbose:
            return

        if self.cmd_log:
            ctx_str = " ".join(f"{k}={v}" for k, v in ctx.items())
            print(f"level={level} cmd=mermaid event={event} {ctx_str} msg=\"{msg}\"")
        else:
            color = COLORS.get(level, "")
            tier_color = ""
            if "tier" in ctx:
                tier_color = TIER_COLORS.get(ctx["tier"], "")
            ctx_str = ""
            if ctx:
                ctx_str = " " + " ".join(f"{k}={v}" for k, v in ctx.items())
            print(f"[{ts}] {color}{level}{RESET} {tier_color}{event}{RESET}{ctx_str} {msg}")


def parse_skill_triggers(skill_md_path: Path) -> dict[str, TriggerTier]:
    """从 SKILL.md 解析 T0/T1/T2 触发词配置

    解析三级信号表格行，格式：
    | **T0 弱信号** | 语义 | `词1`、`词2` | 加载动作 |
    """
    content = skill_md_path.read_text(encoding="utf-8")
    tiers: dict[str, TriggerTier] = {}

    tier_specs = [
        (r"T0\s*弱信号", "T0", "弱信号"),
        (r"T1\s*中信号", "T1", "中信号"),
        (r"T2\s*强信号", "T2", "强信号"),
    ]

    for pattern, level, name in tier_specs:
        row_pattern = re.compile(
            rf"\|\s*\**\s*{pattern}\s*\**\s*\|[^|]*\|\s*([^|]+)\|\s*([^|]*)\|",
            re.MULTILINE,
        )
        match = row_pattern.search(content)
        if not match:
            continue
        triggers_text = match.group(1)
        action_text = match.group(2).strip()
        triggers = re.findall(r"`([^`]+)`", triggers_text)
        tiers[level] = TriggerTier(level=level, name=name, triggers=triggers, action=action_text)

    return tiers


def fuzzy_match(trigger: str, text: str, max_gap: int = 2) -> tuple[bool, int, str]:
    """带间距约束的子序列匹配

    检查 trigger 的字符是否按序出现在 text 中，且相邻字符间距不超过 max_gap。
    用于处理"画个流程图"匹配"画流程图"（中间插入"个"）等变体。

    返回：(是否匹配, 起始位置, 匹配的文本片段)
    """
    if not trigger or not text:
        return False, -1, ""

    positions: list[int] = []
    first = text.find(trigger[0])
    if first == -1:
        return False, -1, ""
    positions.append(first)

    for i in range(1, len(trigger)):
        search_start = positions[i - 1] + 1
        search_end = search_start + max_gap + 1
        found = text.find(trigger[i], search_start, search_end)
        if found == -1:
            return False, -1, ""
        positions.append(found)

    start = positions[0]
    matched_text = text[start:positions[-1] + 1]
    return True, start, matched_text


def match_tier(text: str, tier: TriggerTier, logger: Logger,
               fuzzy: bool = False, max_gap: int = 2) -> TierMatchResult:
    """匹配单个信号级的所有触发词，输出逐词匹配日志

    精确匹配优先，未命中时若 fuzzy=True 则尝试模糊子序列匹配。
    """
    result = TierMatchResult(level=tier.level, name=tier.name)

    logger.log("DEBUG", EVENT_SCAN, f"开始匹配{tier.name}（{len(tier.triggers)}个触发词）",
               ctx={"tier": tier.level, "trigger_count": len(tier.triggers), "fuzzy": fuzzy})

    for trigger in tier.triggers:
        pos = text.find(trigger)
        if pos >= 0:
            result.matched.append(trigger)
            logger.log("DEBUG", EVENT_HIT, f"触发词 '{trigger}' 命中",
                       ctx={"tier": tier.level, "trigger": trigger, "position": pos, "fuzzy": False})
        elif fuzzy:
            is_match, f_start, f_text = fuzzy_match(trigger, text, max_gap)
            if is_match:
                result.fuzzy_matched.append(trigger)
                logger.log("DEBUG", EVENT_FUZZY_HIT,
                           f"触发词 '{trigger}' 模糊命中（匹配片段：'{f_text}'）",
                           ctx={"tier": tier.level, "trigger": trigger, "position": f_start,
                                "matched_text": f_text, "fuzzy": True})
            else:
                result.unmatched.append(trigger)
                logger.log("DEBUG", EVENT_MISS, f"触发词 '{trigger}' 未命中",
                           ctx={"tier": tier.level, "trigger": trigger})
        else:
            result.unmatched.append(trigger)
            logger.log("DEBUG", EVENT_MISS, f"触发词 '{trigger}' 未命中",
                       ctx={"tier": tier.level, "trigger": trigger})

    if result.is_matched:
        event = TIER_EVENTS.get(tier.level, EVENT_TIER_MATCHED)
        all_matched = result.all_matched
        logger.log("INFO", event, f"{tier.name}匹配成功",
                   ctx={"tier": tier.level, "matched_count": len(all_matched),
                        "matched": ",".join(all_matched),
                        "fuzzy_count": len(result.fuzzy_matched)})
    else:
        logger.log("DEBUG", EVENT_TIER_NO_MATCH, f"{tier.name}无触发词命中",
                   ctx={"tier": tier.level})

    return result


def match_input(text: str, tiers: dict[str, TriggerTier], logger: Logger,
                fuzzy: bool = False, max_gap: int = 2) -> dict:
    """对输入文本执行 T0→T1→T2 三级匹配，输出加载决策日志"""
    logger.log("INFO", EVENT_START, "开始触发词匹配",
               ctx={"input_length": len(text), "input_preview": text[:50], "fuzzy": fuzzy})

    results: dict[str, TierMatchResult] = {}
    for level in ["T0", "T1", "T2"]:
        if level in tiers:
            results[level] = match_tier(text, tiers[level], logger, fuzzy, max_gap)

    # 确定最高信号级（T2 > T1 > T0）
    highest: Optional[str] = None
    for level in ["T2", "T1", "T0"]:
        if level in results and results[level].is_matched:
            highest = level
            break

    # 加载决策
    if highest:
        tier = tiers[highest]
        logger.log("INFO", EVENT_LOAD_DECISION, f"加载决策：{highest}（{tier.name}）",
                   ctx={"signal": highest, "action": tier.action})
        load_action = tier.action
    else:
        logger.log("WARN", EVENT_NO_MATCH, "全部三级信号均未命中",
                   ctx={"input": text[:50]})
        load_action = "不加载"

    return {
        "input": text,
        "tiers": {
            k: {
                "matched": v.matched,
                "fuzzy_matched": v.fuzzy_matched,
                "unmatched_count": len(v.unmatched),
                "is_matched": v.is_matched,
            }
            for k, v in results.items()
        },
        "highest_signal": highest,
        "load_action": load_action,
        "log_entries": len(logger.entries),
    }


def main() -> None:
    setup_safe_output()
    parser = argparse.ArgumentParser(
        description="触发词三级信号匹配器：解析SKILL.md触发词配置，对输入文本进行T0/T1/T2匹配并输出详细日志"
    )
    parser.add_argument("text", help="要匹配的用户输入文本")
    parser.add_argument("--skill", default="mermaid-cmd", help="Skill名称（默认mermaid-cmd）")
    parser.add_argument("--cmd-log", action="store_true", help="使用CMD-LOG结构化格式输出日志")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示DEBUG级日志（逐词匹配过程）")
    parser.add_argument("--fuzzy", action="store_true", help="启用模糊匹配（处理'画个流程图'→'画流程图'等变体）")
    parser.add_argument("--max-gap", type=int, default=2, help="模糊匹配最大字符间距（默认2）")
    parser.add_argument("--json", action="store_true", help="以JSON格式输出最终匹配结果")
    args = parser.parse_args()

    root_dir = resolve_project_root(__file__)
    skill_md = root_dir / SKILLS_DIR / args.skill / "SKILL.md"

    if not skill_md.exists():
        print(f"错误：Skill文件不存在 {skill_md}", file=sys.stderr)
        sys.exit(1)

    logger = Logger(cmd_log=args.cmd_log, verbose=args.verbose, json_mode=args.json)

    tiers = parse_skill_triggers(skill_md)
    if not tiers:
        print(f"错误：未从 {skill_md.name} 解析到三级信号触发词配置", file=sys.stderr)
        print("提示：SKILL.md需包含 T0弱信号/T1中信号/T2强信号 三级表格", file=sys.stderr)
        sys.exit(1)

    if not args.json:
        tier_info = ", ".join(f"{k}({len(v.triggers)}词)" for k, v in tiers.items())
        print(f"Skill: {args.skill} | 触发词配置: {tier_info}")
        print("-" * 60)

    result = match_input(args.text, tiers, logger, fuzzy=args.fuzzy, max_gap=args.max_gap)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("-" * 60)
        signal = result["highest_signal"] or "无匹配"
        print(f"最终结果：最高信号={signal}，加载动作={result['load_action']}")
        print(f"日志条目数：{result['log_entries']}")


if __name__ == "__main__":
    main()
