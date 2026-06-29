#!/usr/bin/env python3
"""阶段守卫日志聚合可视化仪表盘生成工具。

扫描多个会话日志文件中的 [SG-LOG] 和 [PDR-LOG] 结构化日志，
聚合分析后生成自包含HTML仪表盘，包含：
- 全局统计卡片（会话数、操作总数、拦截率、绕过检测数等）
- 事件类型分布饼图（Mermaid pie）
- 各阶段拦截率柱状对比（Mermaid bar / xychart）
- 审批通过率统计
- 高频拦截原因 Top-N
- 异常趋势（ERROR/BYPASS_DETECTED事件）
- 会话详情列表（阶段流转、拦截统计）
- 最近事件时间线

用法:
    python generate-sg-dashboard.py                         # 扫描默认日志目录
    python generate-sg-dashboard.py --log-dir <path>        # 指定日志目录
    python generate-sg-dashboard.py --output <path>         # 指定输出HTML路径
    python generate-sg-dashboard.py --demo                  # 使用内置demo数据生成仪表盘
    python generate-sg-dashboard.py --demo --open           # 生成后自动打开浏览器

参数说明:
    --log-dir PATH    日志目录（默认: .agents/logs/）
    --output PATH     输出HTML路径（默认: .agents/reports/sg-dashboard.html）
    --demo            使用内置多会话demo数据生成仪表盘
    --open            生成后自动在浏览器中打开
    --json            同时输出JSON格式的聚合数据
    --title TITLE     自定义仪表盘标题

相关文件:
    运行时工具: check-stage-guardrail-runtime.py（生成SG-LOG日志）
    离线分析: check-stage-guardrails.py（单日志异常检测）
    使用指南: docs/knowledge/stage-guardrails-guide.md
"""

import argparse
import json
import re
import sys
import webbrowser
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.project import resolve_project_root


LOG_LINE_RE = re.compile(
    r'\[(SG-LOG|PDR-LOG)\]\s*\|\s*'
    r'level=(\w+)\s*\|\s*'
    r'event=(\w+)\s*\|\s*'
    r'stage=(\w+)\s*\|\s*'
    r'role=(\w+)\s*\|\s*'
    r'session=([^|]+?)\s*\|\s*'
    r'msg=([^|]+?)(?:\s*\|\s*ctx=(.+))?$'
)

STAGE_ORDER = {'S1': 1, 'S2': 2, 'S3': 3, 'S4': 4, 'S5': 5, 'S6': 6, 'S7': 7, 'S8': 8}
STAGE_NAMES = {
    'S1': '需求接收', 'S2': '方案设计', 'S3': '任务分配', 'S4': '代码实现',
    'S5': '测试编写', 'S6': '代码审查', 'S7': '合并代码', 'S8': '完成确认',
    'NONE': '无活跃阶段',
}

SG_EVENTS = {
    'STAGE_ENTER', 'STAGE_EXIT', 'DOC_CHECK', 'PDR_CONFIRM',
    'BOUNDARY_CHECK', 'BOUNDARY_PASS', 'INTERCEPT', 'BYPASS_DETECTED',
    'JUMP_REQUEST', 'JUMP_APPROVED', 'JUMP_REJECTED', 'ERROR',
}


@dataclass
class LogEntry:
    prefix: str
    level: str
    event: str
    stage: str
    role: str
    session: str
    msg: str
    ctx: dict
    source_file: str
    line_num: int
    timestamp: str = ''


@dataclass
class SessionStats:
    session_id: str
    source_file: str
    stages_entered: list[str] = field(default_factory=list)
    stages_exited: list[str] = field(default_factory=list)
    operations_checked: int = 0
    operations_passed: int = 0
    operations_intercepted: int = 0
    bypass_detected: int = 0
    errors: int = 0
    jumps_requested: int = 0
    jumps_approved: int = 0
    jumps_rejected: int = 0
    jump_types: Counter = field(default_factory=Counter)
    intercept_reasons: Counter = field(default_factory=Counter)
    roles_seen: set[str] = field(default_factory=set)
    first_event_time: str = ''
    last_event_time: str = ''
    events: list[LogEntry] = field(default_factory=list)
    completed: bool = False


@dataclass
class AggregateStats:
    total_sessions: int = 0
    total_entries: int = 0
    total_sg_entries: int = 0
    total_pdr_entries: int = 0
    total_operations_checked: int = 0
    total_passed: int = 0
    total_intercepted: int = 0
    total_bypasses: int = 0
    total_errors: int = 0
    total_jumps_requested: int = 0
    total_jumps_approved: int = 0
    total_jumps_rejected: int = 0
    sessions_completed: int = 0
    event_counts: Counter = field(default_factory=Counter)
    level_counts: Counter = field(default_factory=Counter)
    stage_intercept_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    stage_pass_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    stage_entry_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    role_intercept_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    top_intercept_reasons: list[tuple[str, int]] = field(default_factory=list)
    sessions: list[SessionStats] = field(default_factory=list)

    @property
    def interception_rate(self) -> float:
        if self.total_operations_checked == 0:
            return 0.0
        return self.total_intercepted / self.total_operations_checked * 100

    @property
    def approval_rate(self) -> float:
        total_decided = self.total_jumps_approved + self.total_jumps_rejected
        if total_decided == 0:
            return 0.0
        return self.total_jumps_approved / total_decided * 100

    @property
    def completion_rate(self) -> float:
        if self.total_sessions == 0:
            return 0.0
        return self.sessions_completed / self.total_sessions * 100


def parse_ctx(ctx_str: Optional[str]) -> dict:
    if not ctx_str or not ctx_str.strip():
        return {}
    try:
        return json.loads(ctx_str.strip())
    except json.JSONDecodeError:
        return {'_raw': ctx_str.strip()}


def parse_log_file(file_path: Path) -> list[LogEntry]:
    entries = []
    try:
        content = file_path.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        return entries

    for line_num, line in enumerate(content.splitlines(), 1):
        line = line.strip()
        if not line or ('[SG-LOG]' not in line and '[PDR-LOG]' not in line):
            continue
        m = LOG_LINE_RE.search(line)
        if not m:
            continue
        prefix, level, event, stage, role, session, msg, ctx_str = m.groups()
        entries.append(LogEntry(
            prefix=prefix,
            level=level.strip(),
            event=event.strip(),
            stage=stage.strip(),
            role=role.strip(),
            session=session.strip(),
            msg=msg.strip(),
            ctx=parse_ctx(ctx_str),
            source_file=str(file_path.name),
            line_num=line_num,
        ))
    return entries


def aggregate_entries(entries: list[LogEntry]) -> AggregateStats:
    stats = AggregateStats()
    sessions: dict[str, SessionStats] = {}

    for entry in entries:
        stats.total_entries += 1
        if entry.prefix == 'SG-LOG':
            stats.total_sg_entries += 1
        else:
            stats.total_pdr_entries += 1
        stats.event_counts[entry.event] += 1
        stats.level_counts[entry.level] += 1

        sid = entry.session
        if sid not in sessions:
            sessions[sid] = SessionStats(session_id=sid, source_file=entry.source_file)
        s = sessions[sid]
        s.events.append(entry)
        s.roles_seen.add(entry.role)

        if entry.event == 'STAGE_ENTER':
            s.stages_entered.append(entry.stage)
            stats.stage_entry_counts[entry.stage] += 1
        elif entry.event == 'STAGE_EXIT':
            s.stages_exited.append(entry.stage)
            if entry.stage == 'S8':
                s.completed = True
        elif entry.event == 'BOUNDARY_CHECK':
            s.operations_checked += 1
            stats.total_operations_checked += 1
        elif entry.event == 'BOUNDARY_PASS':
            s.operations_passed += 1
            stats.total_passed += 1
            stats.stage_pass_counts[entry.stage] += 1
        elif entry.event == 'INTERCEPT':
            s.operations_intercepted += 1
            stats.total_intercepted += 1
            stats.stage_intercept_counts[entry.stage] += 1
            stats.role_intercept_counts[entry.role] += 1
            reason = entry.ctx.get('violating_operation', entry.ctx.get('detail', entry.msg))
            s.intercept_reasons[reason] += 1
        elif entry.event == 'BYPASS_DETECTED':
            s.bypass_detected += 1
            stats.total_bypasses += 1
        elif entry.event == 'ERROR':
            s.errors += 1
            stats.total_errors += 1
        elif entry.event == 'JUMP_REQUEST':
            jt = entry.ctx.get('jump_type', 'unknown')
            s.jumps_requested += 1
            s.jump_types[jt] += 1
            stats.total_jumps_requested += 1
        elif entry.event == 'JUMP_APPROVED':
            s.jumps_approved += 1
            stats.total_jumps_approved += 1
        elif entry.event == 'JUMP_REJECTED':
            s.jumps_rejected += 1
            stats.total_jumps_rejected += 1

    all_reasons = Counter()
    for s in sessions.values():
        all_reasons.update(s.intercept_reasons)
        if s.completed:
            stats.sessions_completed += 1

    stats.total_sessions = len(sessions)
    stats.top_intercept_reasons = all_reasons.most_common(10)
    stats.sessions = sorted(sessions.values(), key=lambda x: x.session_id)
    return stats


def generate_demo_entries() -> list[LogEntry]:
    """生成多会话demo日志数据，覆盖各种场景。"""
    import random
    random.seed(42)

    demo_scenarios = [
        {
            'session': 'feat-auth-001',
            'flow': 'normal',
            'stages': ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8'],
            'intercepts_in': {'S1': ['write_code'], 'S2': ['write_code'], 'S4': ['modify_architecture']},
        },
        {
            'session': 'bugfix-css-002',
            'flow': 'skip',
            'stages': ['S1', 'S4'],
            'skip_from': 'S1', 'skip_to': 'S4',
            'intercepts_in': {'S1': ['choose_tech_stack']},
        },
        {
            'session': 'refactor-api-003',
            'flow': 'rollback',
            'stages': ['S1', 'S2', 'S4', 'S2', 'S4', 'S5', 'S6', 'S7'],
            'rollback_from': 'S4', 'rollback_to': 'S2',
            'intercepts_in': {'S4': ['modify_architecture', 'choose_tech_stack']},
            'bypasses': 1,
        },
        {
            'session': 'feat-payment-004',
            'flow': 'normal',
            'stages': ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8'],
            'intercepts_in': {'S1': ['write_code', 'choose_tech_stack'], 'S2': ['write_code'],
                              'S4': ['modify_architecture'], 'S5': ['write_code']},
        },
        {
            'session': 'docs-update-005',
            'flow': 'normal',
            'stages': ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7'],
            'intercepts_in': {'S1': ['write_code']},
            'errors': 1,
        },
        {
            'session': 'feat-notify-006',
            'flow': 'skip',
            'stages': ['S1', 'S4', 'S5', 'S6', 'S7', 'S8'],
            'skip_from': 'S1', 'skip_to': 'S4',
            'intercepts_in': {'S4': ['change_tech_selection', 'approve_code']},
        },
        {
            'session': 'hotfix-sec-007',
            'flow': 'skip',
            'stages': ['S1', 'S4', 'S7'],
            'skip_from': 'S1', 'skip_to': 'S4',
            'skip2_from': 'S4', 'skip2_to': 'S7',
            'intercepts_in': {'S4': ['write_unit_test']},
            'bypasses': 1,
            'errors': 2,
        },
        {
            'session': 'test-coverage-008',
            'flow': 'normal',
            'stages': ['S1', 'S2', 'S3', 'S4', 'S5'],
            'intercepts_in': {'S1': ['write_code'], 'S4': ['merge_code']},
            'rejects': 1,
        },
    ]

    entries = []
    line_num = 0

    def add(prefix, level, event, stage, role, session, msg, ctx=None):
        nonlocal line_num
        line_num += 1
        entries.append(LogEntry(
            prefix=prefix, level=level, event=event, stage=stage, role=role,
            session=session, msg=msg, ctx=ctx or {}, source_file=f'{session}.log',
            line_num=line_num,
        ))

    for sc in demo_scenarios:
        sid = sc['session']
        role_map = {'S1': 'orchestrator', 'S2': 'architect', 'S3': 'orchestrator',
                    'S4': 'developer', 'S5': 'tester', 'S6': 'reviewer',
                    'S7': 'orchestrator', 'S8': 'orchestrator'}

        stages = sc['stages']
        entered = set()
        just_jumped = False
        jump_from_stage = None

        for i, st in enumerate(stages):
            role = role_map.get(st, 'orchestrator')
            is_new_stage = st not in entered
            if is_new_stage:
                add('SG-LOG', 'INFO', 'STAGE_ENTER', st, role, sid,
                    f'进入{st}阶段', {'via_jump': just_jumped})
                entered.add(st)
                just_jumped = False

            add('SG-LOG', 'INFO', 'DOC_CHECK', st, role, sid,
                '前置文档检查完成', {'required_docs': ['spec.md']})
            add('SG-LOG', 'INFO', 'PDR_CONFIRM', st, role, sid, '前置文档读取完成')

            ops_allowed = ['clarify_requirement', 'create_task_list', 'identify_risk',
                           'search_code', 'read_docs']
            if st == 'S2':
                ops_allowed += ['architecture_design', 'choose_tech_stack', 'define_api']
            elif st == 'S3':
                ops_allowed += ['assign_task', 'set_acceptance_criteria']
            elif st == 'S4':
                ops_allowed += ['write_code', 'write_unit_test', 'run_test', 'refactor_code', 'submit_pr']
            elif st == 'S5':
                ops_allowed += ['write_test', 'run_test', 'report_bug', 'verify_fix']
            elif st == 'S6':
                ops_allowed += ['review_code', 'approve_code', 'request_changes']
            elif st == 'S7':
                ops_allowed += ['merge_code', 'resolve_conflict']
            elif st == 'S8':
                ops_allowed += ['confirm_delivery', 'write_summary', 'close_task']

            n_ops = random.randint(3, 8)
            for _ in range(n_ops):
                op = random.choice(ops_allowed)
                add('SG-LOG', 'DEBUG', 'BOUNDARY_CHECK', st, role, sid, f'检查操作{op}',
                    {'operation': op})
                add('SG-LOG', 'DEBUG', 'BOUNDARY_PASS', st, role, sid, f'操作通过：{op}',
                    {'operation': op})

            if st in sc.get('intercepts_in', {}):
                for bad_op in sc['intercepts_in'][st]:
                    add('SG-LOG', 'DEBUG', 'BOUNDARY_CHECK', st, role, sid, f'检查操作{bad_op}',
                        {'operation': bad_op})
                    target = 'S4' if bad_op in ('write_code', 'modify_business_code') else 'S2'
                    add('SG-LOG', 'WARN', 'INTERCEPT', st, role, sid,
                        f'阶段守卫拦截: {bad_op}属于后续阶段职责',
                        {'current_stage': st, 'violating_operation': bad_op,
                         'target_stage': target, 'violation_type': 'STAGE_BOUNDARY_VIOLATION'})

            is_rollback_point = (st == sc.get('rollback_from') and 'rollback_to' in sc)
            is_skip_point = (st == sc.get('skip_from') and 'skip_to' in sc)
            is_skip2_point = (st == sc.get('skip2_from') and 'skip2_to' in sc)

            if is_rollback_point:
                rt = sc['rollback_to']
                add('SG-LOG', 'INFO', 'JUMP_REQUEST', st, role, sid, f'申请rollback跳转: {st}→{rt}',
                    {'jump_id': f'jump-{sid}-1', 'jump_type': 'rollback',
                     'from_stage': st, 'to_stage': rt, 'reason': 'design flaw'})
                add('SG-LOG', 'INFO', 'JUMP_APPROVED', st, 'orchestrator', sid,
                    f'跳转已批准: {st}→{rt}',
                    {'jump_id': f'jump-{sid}-1', 'jump_type': 'rollback', 'approved_by': 'orchestrator'})
                add('SG-LOG', 'INFO', 'STAGE_EXIT', st, role, sid, f'退出{st}阶段（回退）',
                    {'next_stage': rt})
                for s_rm in ('S3', 'S4', 'S5', 'S6', 'S7', 'S8'):
                    if STAGE_ORDER.get(s_rm, 0) >= STAGE_ORDER.get(rt, 0):
                        entered.discard(s_rm)
                just_jumped = True

            if is_skip_point:
                tt = sc['skip_to']
                jid = f'jump-{sid}-skip'
                add('SG-LOG', 'INFO', 'JUMP_REQUEST', st, role, sid, f'申请skip跳转: {st}→{tt}',
                    {'jump_id': jid, 'jump_type': 'skip', 'from_stage': st, 'to_stage': tt,
                     'reason': 'simple change'})
                add('SG-LOG', 'INFO', 'JUMP_APPROVED', st, 'orchestrator', sid,
                    f'跳转已批准: {st}→{tt}', {'jump_id': jid, 'jump_type': 'skip'})
                add('SG-LOG', 'INFO', 'STAGE_EXIT', st, role, sid, f'退出{st}阶段（跳过）',
                    {'next_stage': tt})
                just_jumped = True

            if is_skip2_point:
                tt2 = sc['skip2_to']
                jid2 = f'jump-{sid}-skip2'
                add('SG-LOG', 'INFO', 'JUMP_REQUEST', st, role, sid, f'申请skip跳转: {st}→{tt2}',
                    {'jump_id': jid2, 'jump_type': 'skip', 'from_stage': st, 'to_stage': tt2,
                     'reason': 'hotfix emergency'})
                add('SG-LOG', 'INFO', 'JUMP_APPROVED', st, 'orchestrator', sid,
                    f'跳转已批准: {st}→{tt2}', {'jump_id': jid2, 'jump_type': 'skip'})
                add('SG-LOG', 'INFO', 'STAGE_EXIT', st, role, sid, f'退出{st}阶段（跳过）',
                    {'next_stage': tt2})
                just_jumped = True

            if sc.get('rejects', 0) > 0 and st == 'S2':
                add('SG-LOG', 'INFO', 'JUMP_REQUEST', st, 'developer', sid,
                    '申请skip跳转: S2→S4', {'jump_id': f'jump-{sid}-r', 'jump_type': 'skip'})
                add('SG-LOG', 'WARN', 'JUMP_REJECTED', st, 'orchestrator', sid,
                    '跳转被拒绝：理由不充分',
                    {'jump_id': f'jump-{sid}-r', 'reject_reason': 'insufficient reason'})
                sc['rejects'] = 0

            if sc.get('bypasses', 0) > 0 and st in ('S1', 'S4'):
                add('SG-LOG', 'ERROR', 'BYPASS_DETECTED', st, role, sid,
                    '检测到疑似绕过：write_code被拦截后改用modify_business_code',
                    {'detection_reason': '疑似通过替代操作绕过拦截',
                     'evidence': '原操作write_code被拦截，改用modify_business_code'})
                sc['bypasses'] -= 1

            if sc.get('errors', 0) > 0:
                add('SG-LOG', 'ERROR', 'ERROR', st, role, sid,
                    '阶段转换错误: UNAUTHORIZED_JUMP',
                    {'error_type': 'UNAUTHORIZED_JUMP', 'error_detail': '未审批跳转',
                     'impact': '可能跳过测试', 'recovery_hint': '退回补审批'})
                sc['errors'] -= 1

            if not (is_skip_point or is_skip2_point or is_rollback_point):
                is_last = (i == len(stages) - 1)
                next_st = stages[i + 1] if i + 1 < len(stages) else None
                next_is_same = (not is_last and next_st == st)
                if not next_is_same:
                    if st == 'S8':
                        add('SG-LOG', 'INFO', 'STAGE_EXIT', st, role, sid, '项目完成',
                            {'exit_criteria_met': ['all done'], 'output_artifacts': ['deliverable']})
                    else:
                        add('SG-LOG', 'INFO', 'STAGE_EXIT', st, role, sid, f'退出{st}阶段',
                            {'next_stage': next_st, 'exit_criteria_met': ['done']})

    return entries


def generate_mermaid_pie(event_counts: Counter) -> str:
    top_events = event_counts.most_common(8)
    lines = ['pie title SG-LOG 事件类型分布']
    for event, count in top_events:
        lines.append(f'    "{event}" : {count}')
    return '\n'.join(lines)


def generate_mermaid_bar_chart(stage_intercept: dict, stage_pass: dict) -> str:
    stages_sorted = sorted(
        set(list(stage_intercept.keys()) + list(stage_pass.keys())),
        key=lambda s: STAGE_ORDER.get(s, 99),
    )
    if not stages_sorted:
        return 'pie title 暂无数据\n    "无数据" : 1'

    x_labels = ', '.join(f'"{STAGE_NAMES.get(s, s)}"' for s in stages_sorted)
    pass_vals = [stage_pass.get(s, 0) for s in stages_sorted]
    intercept_vals = [stage_intercept.get(s, 0) for s in stages_sorted]
    max_val = max((p + i for p, i in zip(pass_vals, intercept_vals)), default=1)
    lines = ['xychart-beta', '    title "各阶段操作拦截/放行对比"',
             f'    x-axis [{x_labels}]',
             f'    y-axis "操作次数" 0 --> {max_val + 2}',
             f'    bar [{", ".join(str(v) for v in pass_vals)}]',
             f'    bar [{", ".join(str(v) for v in intercept_vals)}]']
    return '\n'.join(lines)


def generate_html_dashboard(stats: AggregateStats, title: str = '阶段守卫日志仪表盘',
                            generated_from: str = '') -> str:
    intercept_rate = f'{stats.interception_rate:.1f}%'
    approval_rate = f'{stats.approval_rate:.1f}%'
    completion_rate = f'{stats.completion_rate:.1f}%'

    event_pie = generate_mermaid_pie(stats.event_counts)
    stage_bar = generate_mermaid_bar_chart(stats.stage_intercept_counts, stats.stage_pass_counts)

    top_reasons_rows = ''
    for i, (reason, count) in enumerate(stats.top_intercept_reasons[:8], 1):
        top_reasons_rows += f'<tr><td>{i}</td><td><code>{reason}</code></td><td>{count}</td></tr>\n'

    session_rows = ''
    for s in stats.sessions:
        stage_flow = ' → '.join(s.stages_entered) if s.stages_entered else '-'
        n_stages = len(set(s.stages_entered))
        intercept_pct = (s.operations_intercepted / s.operations_checked * 100) if s.operations_checked > 0 else 0
        status = '✅ 完成' if s.completed else ('⚠️ 进行中' if s.stages_entered else '❓ 无阶段')
        bypass_badge = f' 🔴{s.bypass_detected}' if s.bypass_detected > 0 else ''
        error_badge = f' 🟥{s.errors}' if s.errors > 0 else ''
        session_rows += f'''<tr>
            <td><code>{s.session_id}</code></td>
            <td>{status}{bypass_badge}{error_badge}</td>
            <td>{n_stages}</td>
            <td>{s.operations_checked}</td>
            <td class="warn">{s.operations_intercepted} ({intercept_pct:.0f}%)</td>
            <td>{s.jumps_approved}/{s.jumps_requested}</td>
            <td class="muted small">{stage_flow}</td>
        </tr>\n'''

    event_timeline = ''
    recent = []
    for s in stats.sessions:
        for e in s.events[-5:]:
            recent.append(e)
    recent = recent[-30:]
    for e in recent:
        level_cls = {'ERROR': 'ev-error', 'WARN': 'ev-warn', 'INFO': 'ev-info', 'DEBUG': 'ev-debug'}.get(e.level, '')
        event_timeline += f'''<div class="event {level_cls}">
            <span class="ev-level">{e.level}</span>
            <span class="ev-stage">{e.stage}</span>
            <span class="ev-role">{e.role}</span>
            <span class="ev-event">{e.event}</span>
            <span class="ev-msg">{e.msg[:80]}</span>
            <span class="ev-sid muted">{e.session}</span>
        </div>\n'''

    stage_stats_rows = ''
    for sid in sorted(set(list(stats.stage_entry_counts.keys()) + list(stats.stage_pass_counts.keys())),
                      key=lambda x: STAGE_ORDER.get(x, 99)):
        entries_n = stats.stage_entry_counts.get(sid, 0)
        passed = stats.stage_pass_counts.get(sid, 0)
        intercepted = stats.stage_intercept_counts.get(sid, 0)
        total_ops = passed + intercepted
        rate = f'{intercepted/total_ops*100:.0f}%' if total_ops > 0 else '-'
        stage_stats_rows += f'''<tr>
            <td><strong>{sid}</strong></td>
            <td>{STAGE_NAMES.get(sid, sid)}</td>
            <td>{entries_n}</td>
            <td>{passed}</td>
            <td class="{'warn' if intercepted > 0 else ''}">{intercepted}</td>
            <td>{rate}</td>
        </tr>\n'''

    jump_stats = ''
    skip_n = sum(1 for s in stats.sessions for jt, c in s.jump_types.items() if jt == 'skip' for _ in range(c))
    rollback_n = sum(1 for s in stats.sessions for jt, c in s.jump_types.items() if jt == 'rollback' for _ in range(c))
    jump_stats = f'''<div class="stat-row">
        <div class="stat-card"><div class="stat-value">{stats.total_jumps_requested}</div><div class="stat-label">跳转申请</div></div>
        <div class="stat-card"><div class="stat-value">{stats.total_jumps_approved}</div><div class="stat-label">批准</div></div>
        <div class="stat-card"><div class="stat-value">{stats.total_jumps_rejected}</div><div class="stat-label">拒绝</div></div>
        <div class="stat-card"><div class="stat-value">{skip_n}</div><div class="stat-label">正向跳过</div></div>
        <div class="stat-card"><div class="stat-value">{rollback_n}</div><div class="stat-label">逆向回退</div></div>
    </div>'''

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
:root {{
    --bg: #0f172a; --surface: #1e293b; --border: #334155;
    --text: #e2e8f0; --muted: #94a3b8; --accent: #38bdf8;
    --green: #4ade80; --yellow: #facc15; --red: #f87171; --orange: #fb923c;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: var(--bg); color: var(--text); padding: 24px; line-height:1.6; }}
h1 {{ font-size:1.8rem; margin-bottom:4px; }}
.subtitle {{ color:var(--muted); font-size:0.9rem; margin-bottom:24px; }}
.dashboard-grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(200px,1fr)); gap:16px; margin-bottom:24px; }}
.stat-card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px;
             padding:20px; text-align:center; }}
.stat-value {{ font-size:2rem; font-weight:700; color:var(--accent); }}
.stat-label {{ color:var(--muted); font-size:0.85rem; margin-top:4px; }}
.stat-row {{ display:flex; gap:12px; flex-wrap:wrap; margin-bottom:24px; }}
.stat-row .stat-card {{ flex:1; min-width:120px; }}
.section {{ background:var(--surface); border:1px solid var(--border); border-radius:12px;
           padding:20px; margin-bottom:20px; }}
.section h2 {{ font-size:1.2rem; margin-bottom:16px; display:flex; align-items:center; gap:8px; }}
.charts-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:20px; }}
@media (max-width:900px) {{ .charts-grid {{ grid-template-columns:1fr; }} }}
.mermaid {{ background:var(--bg); border-radius:8px; padding:16px; display:flex; justify-content:center; }}
table {{ width:100%; border-collapse:collapse; font-size:0.9rem; }}
th {{ text-align:left; padding:10px 8px; border-bottom:2px solid var(--border); color:var(--muted); font-weight:600; }}
td {{ padding:8px; border-bottom:1px solid var(--border); }}
tr:hover {{ background:rgba(56,189,248,0.05); }}
.warn {{ color:var(--yellow); }} .err {{ color:var(--red); }} .ok {{ color:var(--green); }}
.muted {{ color:var(--muted); }} .small {{ font-size:0.8rem; }}
.event {{ display:flex; gap:10px; align-items:center; padding:6px 10px; border-left:3px solid var(--border);
         margin-bottom:4px; font-size:0.82rem; font-family:'SF Mono',Consolas,monospace; }}
.ev-error {{ border-left-color:var(--red); background:rgba(248,113,113,0.08); }}
.ev-warn {{ border-left-color:var(--yellow); background:rgba(250,204,21,0.05); }}
.ev-info {{ border-left-color:var(--accent); }}
.ev-debug {{ border-left-color:var(--border); opacity:0.7; }}
.ev-level {{ font-weight:700; min-width:45px; font-size:0.75rem;
            padding:1px 6px; border-radius:4px; text-align:center; }}
.ev-error .ev-level {{ background:var(--red); color:#000; }}
.ev-warn .ev-level {{ background:var(--yellow); color:#000; }}
.ev-info .ev-level {{ background:var(--accent); color:#000; }}
.ev-debug .ev-level {{ background:var(--border); color:var(--muted); }}
.ev-stage {{ font-weight:600; color:var(--accent); min-width:32px; }}
.ev-role {{ color:var(--orange); min-width:80px; }}
.ev-event {{ color:var(--green); min-width:120px; }}
.ev-msg {{ flex:1; color:var(--text); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.ev-sid {{ color:var(--muted); font-size:0.75rem; }}
code {{ background:rgba(56,189,248,0.1); padding:2px 6px; border-radius:4px; font-size:0.85rem; }}
.badge {{ display:inline-block; padding:2px 8px; border-radius:999px; font-size:0.75rem; font-weight:600; }}
.badge-green {{ background:rgba(74,222,128,0.15); color:var(--green); }}
.badge-yellow {{ background:rgba(250,204,21,0.15); color:var(--yellow); }}
.badge-red {{ background:rgba(248,113,113,0.15); color:var(--red); }}
.footer {{ text-align:center; color:var(--muted); font-size:0.8rem; margin-top:32px; padding-top:16px; border-top:1px solid var(--border); }}
</style>
</head>
<body>

<h1>🛡️ {title}</h1>
<div class="subtitle">
    生成时间: {now} | 数据来源: {generated_from} |
    <span class="badge badge-green">{stats.total_sessions} 个会话</span>
    <span class="badge badge-yellow">{stats.total_intercepted} 次拦截</span>
    <span class="badge badge-red">{stats.total_bypasses + stats.total_errors} 次异常</span>
</div>

<div class="dashboard-grid">
    <div class="stat-card">
        <div class="stat-value">{stats.total_sessions}</div>
        <div class="stat-label">会话总数</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{stats.total_entries}</div>
        <div class="stat-label">日志条目</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" style="color:var(--yellow)">{intercept_rate}</div>
        <div class="stat-label">拦截率</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" style="color:var(--green)">{approval_rate}</div>
        <div class="stat-label">审批通过率</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" style="color:var(--green)">{completion_rate}</div>
        <div class="stat-label">完成率</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" style="color:var(--red)">{stats.total_bypasses}</div>
        <div class="stat-label">绕过检测</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" style="color:var(--red)">{stats.total_errors}</div>
        <div class="stat-label">ERROR事件</div>
    </div>
</div>

{jump_stats}

<div class="charts-grid">
    <div class="section">
        <h2>📊 事件类型分布</h2>
        <div class="mermaid">
{event_pie}
        </div>
    </div>
    <div class="section">
        <h2>📈 各阶段操作拦截/放行对比</h2>
        <div class="mermaid">
{stage_bar}
        </div>
    </div>
</div>

<div class="section">
    <h2>🏆 高频拦截原因 Top-{len(stats.top_intercept_reasons[:8])}</h2>
    <table>
        <thead><tr><th>#</th><th>违规操作</th><th>拦截次数</th></tr></thead>
        <tbody>
{top_reasons_rows if top_reasons_rows else '<tr><td colspan="3" class="muted">无拦截记录</td></tr>'}
        </tbody>
    </table>
</div>

<div class="section">
    <h2>📋 各阶段统计</h2>
    <table>
        <thead><tr><th>阶段</th><th>名称</th><th>进入次数</th><th>放行操作</th><th>拦截操作</th><th>拦截率</th></tr></thead>
        <tbody>
{stage_stats_rows if stage_stats_rows else '<tr><td colspan="6" class="muted">无数据</td></tr>'}
        </tbody>
    </table>
</div>

<div class="section">
    <h2>🗂️ 会话详情</h2>
    <table>
        <thead><tr><th>会话ID</th><th>状态</th><th>阶段数</th><th>检查操作</th><th>拦截</th><th>审批(批/请)</th><th>阶段流转</th></tr></thead>
        <tbody>
{session_rows if session_rows else '<tr><td colspan="7" class="muted">无会话数据</td></tr>'}
        </tbody>
    </table>
</div>

<div class="section">
    <h2>⏱️ 最近事件时间线</h2>
{event_timeline if event_timeline else '<div class="muted">无事件数据</div>'}
</div>

<div class="footer">
    🛡️ SpecWeave 阶段守卫日志聚合仪表盘 |
    <a href="https://specweave.dev" style="color:var(--accent)">SpecWeave</a> |
    由 generate-sg-dashboard.py 生成
</div>

<script>
mermaid.initialize({{
    startOnLoad: true,
    theme: 'dark',
    themeVariables: {{
        primaryColor: '#1e3a5f',
        primaryTextColor: '#e2e8f0',
        primaryBorderColor: '#38bdf8',
        lineColor: '#94a3b8',
        secondaryColor: '#1e293b',
        tertiaryColor: '#0f172a',
        fontFamily: 'inherit',
    }},
    pie: {{ useWidth: 400 }},
    xyChart: {{ width: 420, height: 300, plotReservedSpacePercent: 45 }},
}});
</script>
</body>
</html>'''
    return html


def collect_log_files(log_dir: Path) -> list[Path]:
    if not log_dir.exists():
        return []
    files = []
    for ext in ('*.log', '*.txt'):
        files.extend(log_dir.glob(ext))
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(
        description='阶段守卫日志聚合可视化仪表盘生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--log-dir', type=str, help='日志目录（默认: .agents/logs/）')
    parser.add_argument('--output', type=str, help='输出HTML路径')
    parser.add_argument('--demo', action='store_true', help='使用内置demo数据生成')
    parser.add_argument('--open', action='store_true', help='生成后自动打开浏览器')
    parser.add_argument('--json', action='store_true', dest='json_output', help='输出JSON数据')
    parser.add_argument('--title', type=str, default='阶段守卫日志仪表盘', help='仪表盘标题')
    args = parser.parse_args()

    project_root = resolve_project_root(__file__)

    if args.demo:
        entries = generate_demo_entries()
        source_desc = '内置Demo数据（8个模拟会话）'
    else:
        log_dir = Path(args.log_dir) if args.log_dir else (project_root / '.agents' / 'logs')
        log_files = collect_log_files(log_dir)
        if not log_files:
            print(f'⚠️ 日志目录 {log_dir} 中未找到 .log 文件')
            print('   提示: 使用 --demo 生成内置demo仪表盘，或先用 check-stage-guardrail-runtime.py --export-logs 生成日志')
            return 1
        entries = []
        for f in log_files:
            entries.extend(parse_log_file(f))
        source_desc = f'{log_dir} ({len(log_files)} 个文件)'

    if not entries:
        print('❌ 未解析到任何 [SG-LOG]/[PDR-LOG] 日志条目')
        return 1

    stats = aggregate_entries(entries)

    if args.json_output:
        data = {
            'summary': {
                'total_sessions': stats.total_sessions,
                'total_entries': stats.total_entries,
                'interception_rate': round(stats.interception_rate, 2),
                'approval_rate': round(stats.approval_rate, 2),
                'completion_rate': round(stats.completion_rate, 2),
                'total_intercepted': stats.total_intercepted,
                'total_bypasses': stats.total_bypasses,
                'total_errors': stats.total_errors,
            },
            'event_counts': dict(stats.event_counts),
            'top_intercept_reasons': stats.top_intercept_reasons,
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
        if not args.output:
            return 0

    output_path = Path(args.output) if args.output else (project_root / '.agents' / 'reports' / 'sg-dashboard.html')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    html = generate_html_dashboard(stats, title=args.title, generated_from=source_desc)
    output_path.write_text(html, encoding='utf-8')

    print(f'✅ 仪表盘已生成: {output_path}')
    print(f'   会话数: {stats.total_sessions}')
    print(f'   日志条目: {stats.total_entries}')
    print(f'   拦截率: {stats.interception_rate:.1f}%')
    print(f'   审批通过率: {stats.approval_rate:.1f}%')
    print(f'   绕过检测: {stats.total_bypasses} | ERROR: {stats.total_errors}')

    if args.open:
        webbrowser.open(output_path.as_uri())

    return 0


if __name__ == '__main__':
    sys.exit(main())
