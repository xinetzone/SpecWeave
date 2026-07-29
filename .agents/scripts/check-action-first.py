#!/usr/bin/env python3
"""
Action-First 输出范式合规性自检工具
用法：
  python check-action-first.py <file>           # 检查文件是否符合action-first范式
  python check-action-first.py --demo            # 运行内置演示，展示决策日志
  python check-action-first.py --self-test       # 对本脚本输出进行自检
  python check-action-first.py --log-demo        # 展示核心决策节点日志格式

检查规则（7条）：
  R1: 第一行是否为核心结论/命令（无铺垫客套，长度<200字）
  R2: 多步任务是否有数字编号步骤（短任务可豁免）
  R3: 多轮交互是否有进度重述（≤2轮可豁免）
  R4: 是否移除了程序化客套话（自动豁免代码块/反例章节/引号引用）
  R5: 建议>5条时是否区分【现在做】/【以后做】
  R6: 是否遵循黄金三层结构（核心区/详细区/补充区，完整度≥60%）
  R7: 高风险操作是否有前置⚠️警告标记
"""
import argparse
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

ANSI_GREEN = "\033[92m"
ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"
ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"

@dataclass
class DecisionLog:
    """核心决策节点日志条目"""
    node: str
    decision: str
    reason: str
    input_signal: str = ""
    output_action: str = ""

@dataclass
class CheckResult:
    rule_id: str
    rule_name: str
    passed: bool
    score: float
    detail: str
    line_hint: int = 0

@dataclass
class ParadigmDecision:
    """范式选择决策结果"""
    paradigm: str
    confidence: float
    broke_rules: list = field(default_factory=list)
    logs: list = field(default_factory=list)


def log_decision(node: str, decision: str, reason: str,
                 input_signal: str = "", output_action: str = "") -> DecisionLog:
    """记录核心决策节点日志（用于AI执行时打印到stderr）"""
    entry = DecisionLog(
        node=node,
        decision=decision,
        reason=reason,
        input_signal=input_signal,
        output_action=output_action,
    )
    print(f"[AF-LOG] [{node}] DECISION: {decision}", file=sys.stderr)
    if input_signal:
        print(f"[AF-LOG] [{node}] INPUT:    {input_signal}", file=sys.stderr)
    print(f"[AF-LOG] [{node}] REASON:   {reason}", file=sys.stderr)
    if output_action:
        print(f"[AF-LOG] [{node}] ACTION:   {output_action}", file=sys.stderr)
    print(f"[AF-LOG] [{node}] ---", file=sys.stderr)
    return entry


def decide_paradigm(user_input: str, context: dict = None) -> ParadigmDecision:
    """
    核心决策函数：根据用户输入和上下文选择输出范式
    这是action-first指令集的"执行入口"，对应指令文档中的范式切换决策树
    """
    ctx = context or {}
    logs = []
    broke = []
    paradigm = "action-first"
    confidence = 0.9

    user_lower = user_input.lower()

    # 决策节点1：用户明确要求解释/聊天？
    log = log_decision(
        node="Q1_EXPLAIN_REQUEST",
        decision="检查是否用户明确要求解释优先",
        reason="用户明确要求解释时尊重用户意愿",
        input_signal=f"user_input={user_input[:80]}...",
    )
    logs.append(log)
    explain_keywords = ["先解释", "解释一下", "聊聊", "讨论一下", "为什么", "原理", "教我"]
    if any(kw in user_input for kw in explain_keywords) and not ctx.get("force_action"):
        paradigm = "explanatory"
        confidence = 0.95
        logs.append(log_decision(
            node="Q1_EXPLAIN_REQUEST",
            decision="SWITCH→解释优先范式",
            reason="检测到解释请求关键词",
            input_signal=f"keywords={[kw for kw in explain_keywords if kw in user_input]}",
            output_action="切换到完整上下文铺垫+逐步解释模式",
        ))
        return ParadigmDecision(paradigm=paradigm, confidence=confidence,
                               broke_rules=broke, logs=logs)
    logs.append(log_decision(
        node="Q1_EXPLAIN_REQUEST",
        decision="KEEP→行动优先",
        reason="未检测到解释请求",
    ))

    # 决策节点2：用户情绪检测
    log = log_decision(
        node="Q2_EMOTION_CHECK",
        decision="检查用户情绪状态",
        reason="负面情绪时先共情再解决",
    )
    logs.append(log)
    emotion_keywords = ["崩溃", "烦", "气死了", "绝望", "太难了", "搞不定", "求助"]
    if any(kw in user_input for kw in emotion_keywords):
        paradigm = "empathy-first"
        confidence = 0.9
        broke.append("R1结论前置（情绪场景破规）")
        logs.append(log_decision(
            node="Q2_EMOTION_CHECK",
            decision="BREAK R1→共情优先",
            reason="检测到负面情绪关键词",
            input_signal=f"keywords={[kw for kw in emotion_keywords if kw in user_input]}",
            output_action="先共情回应（如'我理解这很让人沮丧'），稳定后再给方案",
        ))
        return ParadigmDecision(paradigm=paradigm, confidence=confidence,
                               broke_rules=broke, logs=logs)
    logs.append(log_decision(
        node="Q2_EMOTION_CHECK",
        decision="KEEP→行动优先",
        reason="未检测到负面情绪信号",
    ))

    # 决策节点3：风险等级判断
    log = log_decision(
        node="Q3_RISK_ASSESS",
        decision="评估操作风险等级",
        reason="高风险操作必须前置警告和回滚方案",
    )
    logs.append(log)
    high_risk_keywords = ["rm -rf", "删除", "drop table", "生产环境", "force push",
                          "--no-verify", "重置", "格式化", "不可逆", "危险"]
    if any(kw in user_lower for kw in high_risk_keywords):
        paradigm = "risk-first"
        confidence = 0.95
        broke.append("R1结论前置（高风险破规）")
        logs.append(log_decision(
            node="Q3_RISK_ASSESS",
            decision="BREAK R1→风险前置",
            reason="检测到高风险操作关键词",
            input_signal=f"keywords={[kw for kw in high_risk_keywords if kw in user_lower]}",
            output_action="⚠️先展示风险说明+回滚方案，等待用户确认后再给具体命令",
        ))
        return ParadigmDecision(paradigm=paradigm, confidence=confidence,
                               broke_rules=broke, logs=logs)
    logs.append(log_decision(
        node="Q3_RISK_ASSESS",
        decision="KEEP→行动优先",
        reason="操作风险等级为低/中",
    ))

    # 决策节点4：意图判断（做vs懂）
    logs.append(log_decision(
        node="Q4_INTENT",
        decision="判断用户意图是'做'还是'懂'",
        reason="'做'→行动优先；'懂'→解释优先",
    ))
    doing_keywords = ["帮我", "运行", "执行", "创建", "修改", "修复", "写", "生成",
                      "配置", "安装", "部署", "提交", "导出", "检查"]
    knowing_keywords = ["什么是", "为什么", "怎么理解", "原理", "区别", "比较"]
    is_doing = any(kw in user_input for kw in doing_keywords)
    is_knowing = any(kw in user_input for kw in knowing_keywords)
    if is_knowing and not is_doing:
        paradigm = "explanatory"
        confidence = 0.8
        logs.append(log_decision(
            node="Q4_INTENT",
            decision="SWITCH→解释优先",
            reason="意图为'懂'（理解/学习）",
            input_signal=f"knowing_keywords命中",
        ))
    else:
        logs.append(log_decision(
            node="Q4_INTENT",
            decision="KEEP→行动优先",
            reason="意图为'做'（执行/操作）",
        ))

    # 决策节点5：用户熟悉度与范式强度
    logs.append(log_decision(
        node="Q5_FAMILIARITY",
        decision="调整范式强度",
        reason="专家→极致简洁；新手→适度增加解释",
    ))
    if ctx.get("user_level") == "novice" or ctx.get("interaction_count", 99) < 3:
        confidence = 0.7
        broke.append("R4去客套（新用户前3轮保留礼貌）")
        logs.append(log_decision(
            node="Q5_FAMILIARITY",
            decision="BREAK R4→保留适度礼貌",
            reason="新用户/前3轮交互，建立信任",
            output_action="保留礼貌用语，适当增加解释比例",
        ))

    logs.append(log_decision(
        node="FINAL",
        decision=f"CONFIRM→{paradigm} (confidence={confidence})",
        reason=f"所有决策节点评估完成，破规={broke or '无'}",
        output_action="按选定范式生成输出，遵循黄金三层结构",
    ))

    return ParadigmDecision(paradigm=paradigm, confidence=confidence,
                           broke_rules=broke, logs=logs)


def _is_in_code_block(lines: list[str], line_idx: int) -> bool:
    """判断指定行是否在代码块内（```包裹）"""
    in_block = False
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_block = not in_block
        if i == line_idx:
            return in_block
    return False


def _is_negative_example_context(lines: list[str], line_idx: int, context_window: int = 8) -> bool:
    """判断指定行附近是否是反例/反模式/错误示例上下文"""
    start = max(0, line_idx - context_window)
    end = min(len(lines), line_idx + 3)
    context = "\n".join(lines[start:end]).lower()
    negative_markers = [
        "反模式", "禁止", "❌", "错误示例", "bad example", "反例",
        "不要", "不得", "避免", "移除", "以下为严格禁止"
    ]
    return any(m in context for m in negative_markers)


def _find_phrase_contexts(text: str, phrase: str, lines: list[str]) -> list[dict]:
    """找出短语出现的所有位置及其上下文信息，用于区分实际使用vs举例引用"""
    contexts = []
    search_start = 0
    while True:
        idx = text.find(phrase, search_start)
        if idx == -1:
            break
        line_num = text[:idx].count("\n")
        in_code = _is_in_code_block(lines, line_num)
        is_negative = _is_negative_example_context(lines, line_num)
        is_quoted = False
        line_text = lines[line_num] if line_num < len(lines) else ""
        if (phrase in line_text and
            (('"' in line_text and line_text.count('"') >= 2) or
             ("'" in line_text and line_text.count("'") >= 2) or
             ("`" in line_text and line_text.count("`") >= 2))):
            is_quoted = True
        contexts.append({
            "phrase": phrase,
            "line": line_num + 1,
            "in_code_block": in_code,
            "in_negative_example": is_negative,
            "in_quotes": is_quoted,
            "is_real_usage": not (in_code or is_negative or is_quoted),
            "preview": line_text.strip()[:100],
        })
        search_start = idx + len(phrase)
    return contexts


def check_text_compliance(text: str, verbose: bool = True) -> list[CheckResult]:
    """检查文本是否符合action-first范式规则"""
    results = []
    lines = text.strip().split("\n")
    non_empty_lines = [l for l in lines if l.strip()]
    if not non_empty_lines:
        return [CheckResult("R0", "非空检查", False, 0, "文本为空")]

    print(f"[AF-LOG] [CHECK_START] 开始合规性检查：{len(lines)}行文本", file=sys.stderr)

    # R1: 第一行结论前置
    first_line = non_empty_lines[0].strip()
    filler_phrases = ["问得好", "好的！", "没问题！", "当然", "让我", "我来帮你",
                      "这个问题", "首先，", "好的，", "没问题，"]
    has_filler = any(p in first_line for p in filler_phrases)
    hit_fillers = [p for p in filler_phrases if p in first_line]
    is_command_like = bool(re.match(r'^[#\-\d`]|^[A-Za-z]+\s|^\[|^【|^\w+[:：]|^运行|^创建|^执行|^已|^✅|^⚠️', first_line))
    r1_pass = not has_filler and len(first_line) < 200
    r1_reason = f"首行: '{first_line[:80]}...'"
    if has_filler:
        r1_reason += f" ❌ 命中铺垫词: {hit_fillers}"
    elif len(first_line) >= 200:
        r1_reason += " ❌ 首行过长(≥200字)"
    else:
        r1_reason += " ✅ 无铺垫，长度合规"
    print(f"[AF-LOG] [R1_FIRST_LINE] filler_hit={hit_fillers} len={len(first_line)} pass={r1_pass}", file=sys.stderr)
    results.append(CheckResult(
        "R1", "结论前置", r1_pass,
        1.0 if r1_pass else 0.3,
        r1_reason,
        line_hint=1
    ))

    # R2: 步骤编号
    has_numbered_steps = bool(re.search(r'(^|\n)\s*\d+[\.\、）)]\s', text))
    step_matches = re.findall(r'(?:^|\n)\s*(\d+)[\.\、）)]\s', text)
    print(f"[AF-LOG] [R2_STEPS] numbered_steps_found={has_numbered_steps} count={len(step_matches)}", file=sys.stderr)
    results.append(CheckResult(
        "R2", "步骤编号", has_numbered_steps,
        1.0 if has_numbered_steps else 0.5,
        f"✅ 检测到{len(step_matches)}个数字编号步骤" if has_numbered_steps else "⚠️ 未检测到数字编号（短任务可豁免）"
    ))

    # R3: 进度重述
    progress_patterns = [r'已完成', r'待完成', r'当前进度', r'【当前进度】', r'\|已完成']
    progress_hits = [p for p in progress_patterns if re.search(p, text)]
    has_progress = len(progress_hits) > 0
    print(f"[AF-LOG] [R3_PROGRESS] progress_markers_hit={progress_hits} pass={has_progress}", file=sys.stderr)
    results.append(CheckResult(
        "R3", "进度重述", has_progress,
        1.0 if has_progress else 0.6,
        f"✅ 检测到进度标记: {progress_hits}" if has_progress else "⚠️ 未检测到进度重述（≤2轮短交互可豁免）"
    ))

    # R4: 去程序化客套（增强上下文感知）
    polite_phrases = ["希望这有帮助", "问得好！", "没问题！", "如果还有其他问题", "随时问我",
                      "很高兴能帮到你", "祝你好运", "best regards"]
    real_usages = []
    exempted = []
    for phrase in polite_phrases:
        contexts = _find_phrase_contexts(text, phrase, lines)
        for ctx in contexts:
            if ctx["is_real_usage"]:
                real_usages.append(ctx)
            else:
                exempted.append(ctx)
                print(f"[AF-LOG] [R4_POLITE] EXEMPT phrase='{phrase}' line={ctx['line']} "
                      f"code={ctx['in_code_block']} negative={ctx['in_negative_example']} quoted={ctx['in_quotes']}",
                      file=sys.stderr)
    r4_pass = len(real_usages) == 0
    if real_usages:
        print(f"[AF-LOG] [R4_POLITE] FAIL real_usages={len(real_usages)} exempted={len(exempted)}", file=sys.stderr)
        r4_detail = f"❌ 发现{len(real_usages)}处实际客套使用: " + "; ".join(
            f"L{u['line']}('{u['phrase']}')" for u in real_usages[:5]
        )
        if exempted:
            r4_detail += f"（已豁免{len(exempted)}处反例/代码块引用）"
    else:
        print(f"[AF-LOG] [R4_POLITE] PASS exempted_refs={len(exempted)}", file=sys.stderr)
        r4_detail = f"✅ 无程序化客套（已自动豁免{len(exempted)}处反例/代码块引用）" if exempted else "✅ 无程序化客套"
    results.append(CheckResult(
        "R4", "信噪比", r4_pass,
        1.0 if r4_pass else 0.4,
        r4_detail
    ))

    # R5: 建议分优先级
    has_now_later = "【现在做】" in text and "【以后做】" in text
    suggestion_count = len(re.findall(r'建议|recommend|💡', text))
    r5_pass = True
    r5_detail = "✅ 建议优先级正确"
    if suggestion_count > 5 and not has_now_later:
        r5_pass = False
        r5_detail = f"❌ 建议{suggestion_count}条但未区分【现在做】/【以后做】"
    elif suggestion_count <= 5:
        r5_detail = f"✅ 建议{suggestion_count}条（≤5条无需分组）"
    else:
        r5_detail = f"✅ 建议{suggestion_count}条，已区分【现在做】/【以后做】"
    print(f"[AF-LOG] [R5_SUGGESTIONS] count={suggestion_count} has_now_later={has_now_later} pass={r5_pass}", file=sys.stderr)
    results.append(CheckResult("R5", "建议分级", r5_pass, 1.0 if r5_pass else 0.5, r5_detail))

    # R6: 黄金三层结构
    core_markers = ['首屏', '核心', '结论', '第一行', '✅']
    detail_markers = ['步骤', '详细', '注意', '验证']
    extra_markers = ['原理', '备选', '参考', '💡', '补充']
    has_core = any(m in text for m in core_markers)
    has_detail = any(m in text for m in detail_markers)
    has_extra = any(m in text for m in extra_markers)
    layer_score = sum([has_core, has_detail, has_extra]) / 3
    core_hit = [m for m in core_markers if m in text]
    detail_hit = [m for m in detail_markers if m in text]
    extra_hit = [m for m in extra_markers if m in text]
    print(f"[AF-LOG] [R6_LAYERS] core={core_hit} detail={detail_hit} extra={extra_hit} score={layer_score:.0%}", file=sys.stderr)
    results.append(CheckResult(
        "R6", "三层结构", layer_score >= 0.6, layer_score,
        f"结构完整度{layer_score:.0%}（核心层命中={core_hit or '无'} | 详细层命中={detail_hit or '无'} | 补充层命中={extra_hit or '无'}）"
    ))

    # R7: 高风险操作前置警告
    risk_keywords = ["rm -rf", "drop table", "force push", "--no-verify", "格式化", "不可逆", "生产环境"]
    warning_markers = ["⚠️", "警告", "注意", "风险", "回滚", "备份"]
    found_risks = [kw for kw in risk_keywords if kw.lower() in text.lower()]
    has_warning = any(w in text for w in warning_markers)
    r7_pass = True
    r7_detail = "✅ 无高风险操作或已有警告"
    if found_risks and not has_warning:
        r7_pass = False
        r7_detail = f"❌ 检测到高风险关键词{found_risks}但未前置警告标记"
    elif found_risks:
        r7_detail = f"✅ 高风险关键词{found_risks}已有前置警告"
    print(f"[AF-LOG] [R7_RISK] risk_keywords={found_risks} has_warning={has_warning} pass={r7_pass}", file=sys.stderr)
    results.append(CheckResult(
        "R7", "风险前置", r7_pass,
        1.0 if r7_pass else 0.3,
        r7_detail
    ))

    print(f"[AF-LOG] [CHECK_DONE] total_rules={len(results)}", file=sys.stderr)
    return results


def print_report(results: list[CheckResult]) -> int:
    """打印检查报告"""
    print("\n" + "=" * 60)
    print(f"{ANSI_BOLD}Action-First 范式合规性检查报告{ANSI_RESET}")
    print("=" * 60)
    total_score = 0
    passed = 0
    for r in results:
        status = f"{ANSI_GREEN}✅ PASS{ANSI_RESET}" if r.passed else f"{ANSI_RED}❌ FAIL{ANSI_RESET}"
        print(f"  {status} [{r.rule_id}] {r.rule_name} (score={r.score:.1f})")
        print(f"         {r.detail}")
        total_score += r.score
        if r.passed:
            passed += 1
    print("-" * 60)
    avg = total_score / len(results) if results else 0
    overall = "✅ 合规" if avg >= 0.8 else "⚠️ 部分合规" if avg >= 0.6 else "❌ 不合规"
    print(f"{ANSI_BOLD}总体：{overall} | 通过率：{passed}/{len(results)} | 平均得分：{avg:.1%}{ANSI_RESET}")
    print("=" * 60)
    return 0 if avg >= 0.6 else 1


def demo_log_output():
    """演示核心决策节点日志输出"""
    print(f"{ANSI_CYAN}=== Action-First 核心决策节点日志演示 ==={ANSI_RESET}", file=sys.stderr)
    print(f"{ANSI_CYAN}（日志输出到stderr，正式输出到stdout，互不干扰）{ANSI_RESET}\n", file=sys.stderr)

    test_inputs = [
        ("帮我修复登录页面的bug", {"interaction_count": 10}),
        ("解释一下什么是闭包，我想理解原理", {}),
        ("我要rm -rf /tmp这个目录", {}),
        ("这个配置搞了一天都搞不定，烦死了", {}),
        ("帮我创建一个新的Python文件", {"interaction_count": 1}),
    ]

    for text, ctx in test_inputs:
        print(f"\n{ANSI_BOLD}─── 用户输入：「{text}」{'(新用户)' if ctx.get('interaction_count',10)<3 else ''} ───{ANSI_RESET}", file=sys.stderr)
        decision = decide_paradigm(text, ctx)
        print(f"\n{ANSI_GREEN}▶ 最终选择：{decision.paradigm} (置信度{decision.confidence:.0%}){ANSI_RESET}", file=sys.stderr)
        if decision.broke_rules:
            print(f"{ANSI_YELLOW}▶ 破规：{', '.join(decision.broke_rules)}{ANSI_RESET}", file=sys.stderr)
        print("", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Action-First输出范式合规性自检工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("file", nargs="?", help="要检查的Markdown/文本文件路径")
    parser.add_argument("--demo", action="store_true", help="运行决策日志演示")
    parser.add_argument("--self-test", action="store_true", help="对内置范例文本进行自检")
    parser.add_argument("--log-demo", action="store_true", help="只展示日志格式")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    args = parser.parse_args()

    if args.demo or args.log_demo:
        demo_log_output()
        if args.log_demo:
            return 0

    if args.self_test:
        sample = """已修复登录页bug，共修改3个文件。

【当前进度】Bug修复 | 已完成：定位问题、修复代码 | 待完成：运行测试

步骤：
1. 打开 src/auth/login.py 修改第42行
2. 添加输入验证逻辑（约5分钟）
3. 运行 pytest tests/test_login.py 验证

💡 建议：
- 【现在做】运行测试确认修复
- 【以后做】添加边界情况测试用例

⚠️ 注意：修改前先备份原文件。
"""
        print("自检范例文本：")
        print("-" * 40)
        print(sample)
        print("-" * 40)
        results = check_text_compliance(sample, args.verbose)
        return print_report(results)

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"{ANSI_RED}错误：文件不存在 {path}{ANSI_RESET}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        print(f"检查文件：{path}（{len(text)}字符）")
        results = check_text_compliance(text, args.verbose)
        return print_report(results)

    parser.print_help()
    print("\n提示：先用 --demo 查看决策日志，再用 --self-test 查看自检效果")
    return 0


if __name__ == "__main__":
    sys.exit(main())
