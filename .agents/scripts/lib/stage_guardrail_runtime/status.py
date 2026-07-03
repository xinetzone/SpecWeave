import json

from lib.cli import print_header, print_pass
from lib.stage_guardrails import (
    OperationType,
    STAGE_NAMES,
    STAGE_ORDER,
)


def run_status(json_output: bool = False, enable_color: bool = True) -> int:
    info = {
        'components': {
            'StageStateManager': 'available',
            'BoundaryChecker': 'available',
            'InterceptorFormatter': 'available',
            'GuardrailRuntime': 'available',
        },
        'stages': {sid: STAGE_NAMES[sid] for sid in sorted(STAGE_ORDER.keys(), key=lambda s: STAGE_ORDER[s])},
        'operation_count': len(OperationType),
        'log_format': '[SG-LOG] | level=<LEVEL> | event=<EVENT> | stage=<STAGE> | role=<ROLE> | session=<SID> | msg=<MSG> [| ctx=<JSON>]',
        'supported_events': [
            'STAGE_ENTER', 'STAGE_EXIT', 'DOC_CHECK', 'PDR_CONFIRM',
            'BOUNDARY_CHECK', 'BOUNDARY_PASS', 'INTERCEPT', 'BYPASS_DETECTED',
            'JUMP_REQUEST', 'JUMP_APPROVED', 'JUMP_REJECTED', 'ERROR',
        ],
    }

    if json_output:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        print_header('阶段守卫运行时状态')
        print('组件状态:')
        for name, status in info['components'].items():
            print_pass(f'{name}: {status}')
        print(f'\n阶段定义（共{len(info["stages"])}个阶段）:')
        for sid, sname in info['stages'].items():
            print(f'  {sid}: {sname}')
        print(f'\n操作类型: 共 {info["operation_count"]} 种')
        print(f'\n支持事件: {", ".join(info["supported_events"])}')
        print(f'\n日志格式: {info["log_format"]}')
    return 0
