import json
import sys

from lib.cli import print_pass, print_warn, print_error, print_header
from lib.stage_guardrails import (
    GuardrailRuntime,
    OperationType,
    STAGE_NAMES,
    STAGE_ORDER,
    STAGE_ROLES,
)

from .constants import OPERATION_MAP, VALID_ROLES


def _get_stage_role(stage: str) -> str:
    roles = STAGE_ROLES.get(stage, set())
    return next(iter(roles)) if roles else 'orchestrator'


def run_check(stage: str, role: str, op_name: str,
              detail: str = '', json_output: bool = False,
              strict: bool = False, enable_color: bool = True) -> int:
    if stage not in STAGE_ORDER:
        msg = f'无效阶段: {stage}，有效阶段: {sorted(STAGE_ORDER.keys())}'
        if json_output:
            print(json.dumps({'error': msg}, ensure_ascii=False))
        else:
            print_error(msg)
        return 2

    if role not in VALID_ROLES:
        msg = f'无效角色: {role}，有效角色: {sorted(VALID_ROLES)}'
        if json_output:
            print(json.dumps({'error': msg}, ensure_ascii=False))
        else:
            print_error(msg)
        return 2

    op = OPERATION_MAP.get(op_name)
    if op is None:
        valid_ops = sorted(OPERATION_MAP.keys())
        msg = f'无效操作: {op_name}'
        if json_output:
            print(json.dumps({'error': msg, 'valid_operations': valid_ops}, ensure_ascii=False))
        else:
            print_error(msg)
            print(f'  有效操作: {", ".join(valid_ops[:15])}...(共{len(valid_ops)}种)')
        return 2

    rt = GuardrailRuntime(session_id='check-single', enable_color=enable_color and sys.stdout.isatty(),
                          enable_bypass_detection=False)
    rt.enter_stage(stage, _get_stage_role(stage), f'进入{stage}进行拦截检查')

    actual_role = role
    out = rt.guard_operation(op, actual_role, detail=detail or f'执行{op.value}')

    if json_output:
        result = {
            'stage': stage,
            'stage_name': STAGE_NAMES.get(stage, stage),
            'role': actual_role,
            'operation': op.value,
            'detail': detail,
            'is_intercept': out.is_intercept,
            'event_type': out.event_type,
            'log_level': out.log_level,
            'user_message': out.user_message,
            'sg_log': out.sg_log_line,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        stage_name = STAGE_NAMES.get(stage, stage)
        print_header(f'阶段守卫拦截检查')
        print(f'  阶段: {stage}（{stage_name}）')
        print(f'  角色: {actual_role}')
        print(f'  操作: {op.value}')
        if detail:
            print(f'  描述: {detail}')
        print()

        if out.is_intercept:
            print(f'{out.user_message}')
            print()
            if out.event_type == 'BYPASS_DETECTED':
                print_error(f'结果: ❌ 绕过检测（{out.event_type}）')
                return 1
            else:
                print_warn(f'结果: ⚠️ 操作被拦截（{out.event_type}）')
                return 1 if strict else 0
        else:
            print_pass(f'结果: ✅ 操作被允许（{op.value}在{stage_name}阶段可由{actual_role}执行）')
            return 0
