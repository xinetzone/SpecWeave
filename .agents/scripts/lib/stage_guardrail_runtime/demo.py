import json
import sys

from lib.cli import print_pass, print_warn, print_error, print_header, print_summary
from lib.stage_guardrails import (
    GuardrailRuntime,
    OperationType,
)


def run_demo(json_output: bool = False, strict: bool = False,
             enable_color: bool = True) -> int:
    session_id = 'demo-runtime'
    rt = GuardrailRuntime(session_id=session_id, enable_color=enable_color and sys.stdout.isatty())

    results = []
    intercept_count = 0
    bypass_count = 0

    def record(out, label: str):
        nonlocal intercept_count, bypass_count
        entry = {
            'label': label,
            'is_intercept': out.is_intercept,
            'event_type': out.event_type,
            'log_level': out.log_level,
            'user_message': out.user_message,
            'sg_log': out.sg_log_line,
        }
        results.append(entry)
        if out.is_intercept:
            if out.event_type == 'BYPASS_DETECTED':
                bypass_count += 1
            elif out.event_type != 'BOUNDARY_PASS':
                intercept_count += 1

    rt.enter_stage('S1', 'orchestrator', '收到用户需求：实现用户登录功能')

    record(rt.guard_operation(OperationType.CLARIFY_REQUIREMENT, 'orchestrator',
                               detail='澄清登录功能需求边界'), '1. 澄清需求（S1允许）')

    out = rt.guard_operation(OperationType.WRITE_CODE, 'orchestrator',
                              detail='直接开始编写登录模块代码')
    record(out, '2. S1阶段写代码（应被拦截）')

    out = rt.guard_operation(OperationType.CHOOSE_TECH_STACK, 'orchestrator',
                              detail='在S1阶段直接选型Redis')
    record(out, '3. S1阶段技术选型（应被拦截）')

    out = rt.guard_operation(OperationType.MODIFY_BUSINESS_CODE, 'orchestrator',
                              detail='尝试用替代操作绕过写代码限制')
    record(out, '4. 替代操作绕过检测（应触发BYPASS_DETECTED）')

    out = rt.guard_operation(OperationType.CREATE_TASK_LIST, 'orchestrator',
                              detail='创建任务分解清单')
    record(out, '5. 创建任务清单（S1允许）')

    rt.mark_doc_check(['spec.md', 'development-standards.md', 'stage-guardrails.md'])
    rt.mark_pdr_done()

    rt.exit_stage('S1', 'orchestrator', '需求澄清完成，进入方案设计',
                   exit_criteria_met=['需求边界明确', '验收标准定义', '风险已识别'],
                   output_artifacts=['需求文档', '任务分解清单', '风险评估表'],
                   next_stage='S2')
    rt.enter_stage('S2', 'architect', '开始方案设计')

    out = rt.guard_operation(OperationType.ARCHITECTURE_DESIGN, 'architect',
                              detail='设计系统分层架构')
    record(out, '6. S2架构设计（允许）')

    out = rt.guard_operation(OperationType.WRITE_CODE, 'architect',
                              detail='架构师直接写代码')
    record(out, '7. S2阶段写代码（应被拦截）')

    if json_output:
        output = {
            'session_id': session_id,
            'mode': 'demo',
            'interception_count': rt.interception_count,
            'bypass_count': rt.bypass_count,
            'log_count': len(rt.log_lines),
            'results': results,
            'logs': rt.log_lines,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print_header('阶段守卫运行时演示（基础模式）')
        print(f'Session: {session_id}\n')

        for entry in results:
            label = entry['label']
            if entry['is_intercept']:
                if entry['event_type'] == 'BYPASS_DETECTED':
                    print_error(f'{label} → ⚠️ 绕过检测 [{entry["event_type"]}]')
                else:
                    print_warn(f'{label} → ⚠️ 拦截 [{entry["event_type"]}]')
                if entry['user_message']:
                    for line in entry['user_message'].split('\n'):
                        print(f'      {line}')
            else:
                print_pass(f'{label} → ✅ 放行')

        print()
        print_summary(
            pass_count=sum(1 for r in results if not r['is_intercept']),
            warn_count=intercept_count,
            error_count=bypass_count,
        )
        print(f'\n共生成 {len(rt.log_lines)} 条 SG-LOG 日志')

    has_errors = bypass_count > 0
    has_warnings = intercept_count > 0
    if has_errors:
        return 1
    if strict and has_warnings:
        return 1
    return 0


def run_full_flow(json_output: bool = False, strict: bool = False,
                  enable_color: bool = True) -> int:
    session_id = 'demo-full-flow'
    rt = GuardrailRuntime(session_id=session_id, enable_color=enable_color and sys.stdout.isatty())
    events = []

    def record(out, label: str):
        events.append({
            'label': label,
            'is_intercept': out.is_intercept,
            'event_type': out.event_type,
            'log_level': out.log_level,
            'has_message': bool(out.user_message),
        })

    out = rt.enter_stage('S1', 'orchestrator', '收到需求：修复登录页面样式bug')
    record(out, '→ 进入S1需求接收')

    record(rt.guard_operation(OperationType.CLARIFY_REQUIREMENT, 'orchestrator',
                               detail='确认bug复现步骤和期望效果'), 'S1: 澄清需求')

    record(rt.guard_operation(OperationType.WRITE_CODE, 'orchestrator',
                               detail='直接修改CSS文件'), 'S1: 写代码（拦截）')

    record(rt.guard_operation(OperationType.IDENTIFY_RISK, 'orchestrator',
                               detail='识别CSS修改可能影响其他页面'), 'S1: 识别风险')

    rt.mark_doc_check(['bug-report.md'])
    rt.mark_pdr_done()

    jr, out = rt.request_jump('skip', 'S4', 'orchestrator',
                               reason='样式修复为 trivial change，跳过设计直接编码')
    record(out, '→ 申请S1→S4跳过')

    if jr:
        out = rt.approve_jump(jr.jump_id, 'orchestrator')
        record(out, '→ orchestrator批准跳过')
        out = rt.execute_skip(jr.jump_id, 'developer', '跳过S2/S3直接进入编码')
        record(out, '→ 执行跳过，进入S4')

    assert rt.current_stage == 'S4', f'Expected S4, got {rt.current_stage}'

    record(rt.guard_operation(OperationType.WRITE_CODE, 'developer',
                               detail='修复CSS样式'), 'S4: 写代码（放行）')

    record(rt.guard_operation(OperationType.WRITE_UNIT_TEST, 'developer',
                               detail='为CSS修复编写回归测试'), 'S4: 编写单测（放行）')

    record(rt.guard_operation(OperationType.CHOOSE_TECH_STACK, 'developer',
                               detail='顺便引入新框架'), 'S4: 技术选型（拦截）')

    record(rt.guard_operation(OperationType.MODIFY_ARCHITECTURE, 'developer',
                               detail='顺便重构认证模块'), 'S4: 修改架构（拦截）')

    jr2, out = rt.request_jump('rollback', 'S2', 'developer',
                                reason='发现需要先调整组件设计')
    record(out, '→ 申请S4→S2回退')
    if jr2:
        out = rt.approve_jump(jr2.jump_id, 'orchestrator',
                               rollback_scope='保留CSS修复，回退认证模块重构',
                               conditions='回退后需architect重新评审设计')
        record(out, '→ orchestrator批准回退，自动进入S2')

    if json_output:
        output = {
            'session_id': session_id,
            'mode': 'full_flow',
            'status': rt.get_status().__dict__,
            'interception_count': rt.interception_count,
            'bypass_count': rt.bypass_count,
            'events': events,
            'logs': rt.log_lines,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print_header('阶段守卫运行时演示（完整流程模式）')
        print(f'Session: {session_id}\n')

        pass_c = warn_c = err_c = 0
        for e in events:
            label = e['label']
            if label.startswith('→'):
                print(f'  {label}')
                continue
            if e['is_intercept']:
                if e['log_level'] == 'ERROR':
                    print_error(f'{label}')
                    err_c += 1
                else:
                    print_warn(f'{label}')
                    warn_c += 1
            else:
                print_pass(f'{label}')
                pass_c += 1

        print()
        status = rt.get_status()
        print(f'当前阶段: {status.current_stage} ({status.current_stage_name})')
        print(f'当前角色: {status.current_role}')
        print(f'已完成阶段: {", ".join(status.completed_stages) if status.completed_stages else "无"}')
        print(f'拦截次数: {status.interception_count}, 绕过检测: {status.bypass_count}')
        print()
        print_summary(pass_c, warn_c, err_c)
        print(f'\n共生成 {len(rt.log_lines)} 条 SG-LOG 日志')

    has_errors = rt.bypass_count > 0
    has_warnings = rt.interception_count > 0
    if has_errors:
        return 1
    if strict and has_warnings:
        return 1
    return 0
