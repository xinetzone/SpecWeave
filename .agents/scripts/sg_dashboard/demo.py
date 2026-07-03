"""sg-dashboard Demo数据生成模块。

生成多会话模拟日志数据，覆盖正常流程、跳过、回退、绕过检测、错误等场景。
"""

from __future__ import annotations

import random

from .constants import STAGE_ORDER
from .models import LogEntry


def generate_demo_entries() -> list[LogEntry]:
    """生成多会话demo日志数据，覆盖各种场景。"""
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
