#!/usr/bin/env python3
"""阶段守卫运行时强制执行工具。

基于 GuardrailRuntime 运行时门面，提供交互式命令行工具用于：
1. 演示完整的阶段守卫强制执行流程（--demo）
2. 单步拦截测试：检查指定阶段/角色下某个操作是否被拦截（--check）
3. 导出 SG-LOG 日志样本文件，供离线分析工具消费（--export-logs）
4. 查询运行时状态信息（--status）

与离线分析工具 check-stage-guardrails.py 的关系：
- 本工具做运行时实时拦截（操作前检查 → 拦截/放行 → SG-LOG输出）
- 离线工具做事后日志分析（解析SG-LOG → 检测异常 → 报告）
- 两者共用 [SG-LOG] 结构化日志格式，构成"运行时+离线"双层验证闭环

用法:
    python check-stage-guardrail-runtime.py --demo
    python check-stage-guardrail-runtime.py --demo --json
    python check-stage-guardrail-runtime.py --check --stage S1 --role orchestrator --op write_code
    python check-stage-guardrail-runtime.py --check --stage S4 --role developer --op modify_architecture
    python check-stage-guardrail-runtime.py --export-logs <output_path>
    python check-stage-guardrail-runtime.py --status
    python check-stage-guardrail-runtime.py --full-flow  # S1→S8完整流程+越界拦截演示

参数说明:
    --demo              使用内置demo演示运行时拦截功能
    --full-flow         演示完整S1→S8生命周期（含越界拦截、审批跳转、绕过检测）
    --check             单步拦截检查模式（需配合--stage/--role/--op）
    --stage STAGE       指定阶段ID（S1~S8），check模式必填
    --role ROLE         指定角色（orchestrator/architect/developer/tester/reviewer）
    --op OPERATION      指定操作类型（write_code/clarify_requirement等）
    --detail DETAIL     操作描述文本
    --export-logs PATH  将demo生成的SG-LOG日志导出到指定文件
    --status            显示demo运行后的运行时状态
    --strict            严格模式：WARN级别拦截视为失败（退出码1）
    --json              以JSON格式输出结果（机器可读）
    --no-color          禁用终端彩色输出

退出码:
    0  所有检查通过（操作未被拦截）
    1  操作被拦截/发现异常（严格模式下WARN即失败）
    2  参数错误

示例:
    # 演示S1阶段写代码被拦截
    python check-stage-guardrail-runtime.py --check --stage S1 --role orchestrator --op write_code

    # 演示完整流程并导出日志
    python check-stage-guardrail-runtime.py --full-flow --export-logs .agents/logs/demo-runtime.log

相关文档:
    阶段守卫规则:      .agents/rules/stage-guardrails.md
    离线分析工具:      .agents/scripts/check-stage-guardrails.py
    运行时模块:        .agents/scripts/lib/stage_guardrails/
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, add_common_args
from lib.stage_guardrails import (
    GuardrailRuntime,
    OperationType,
    STAGE_NAMES,
    STAGE_ORDER,
)


OPERATION_MAP: dict[str, OperationType] = {
    op.value: op for op in OperationType
}

VALID_ROLES = {'orchestrator', 'architect', 'developer', 'tester', 'reviewer'}


def run_demo(json_output: bool = False, strict: bool = False,
             enable_color: bool = True) -> int:
    """运行基础演示：S1阶段越界拦截 + 正常放行 + 绕过检测。"""
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
    """运行完整S1→S4演示（含审批跳转和正常放行）。"""
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


def run_check(stage: str, role: str, op_name: str,
              detail: str = '', json_output: bool = False,
              strict: bool = False, enable_color: bool = True) -> int:
    """单步拦截检查。"""
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


def run_export_logs(output_path: str, enable_color: bool = True) -> int:
    """运行demo并导出SG-LOG到文件。"""
    session_id = 'demo-export'
    rt = GuardrailRuntime(session_id=session_id, enable_color=False)

    rt.enter_stage('S1', 'orchestrator', '收到需求')
    rt.guard_operation(OperationType.CLARIFY_REQUIREMENT, 'orchestrator', detail='澄清需求')
    rt.guard_operation(OperationType.WRITE_CODE, 'orchestrator', detail='尝试写代码（拦截）')
    rt.mark_doc_check(['spec.md'])
    rt.mark_pdr_done()
    rt.exit_stage('S1', 'orchestrator', 'S1完成', next_stage='S2')

    rt.enter_stage('S2', 'architect', '设计阶段')
    rt.guard_operation(OperationType.ARCHITECTURE_DESIGN, 'architect', detail='架构设计')
    rt.guard_operation(OperationType.WRITE_CODE, 'architect', detail='写代码（拦截）')
    rt.mark_doc_check(['architecture.md'])
    rt.mark_pdr_done()
    rt.exit_stage('S2', 'architect', 'S2完成', next_stage='S3')

    rt.enter_stage('S3', 'orchestrator', '任务分配')
    rt.guard_operation(OperationType.ASSIGN_TASK, 'orchestrator', detail='分配任务')
    rt.mark_doc_check(['tasks.md'])
    rt.mark_pdr_done()
    rt.exit_stage('S3', 'orchestrator', 'S3完成', next_stage='S4')

    rt.enter_stage('S4', 'developer', '编码阶段')
    rt.guard_operation(OperationType.WRITE_CODE, 'developer', detail='编写代码')
    rt.guard_operation(OperationType.WRITE_UNIT_TEST, 'developer', detail='编写单测')
    rt.guard_operation(OperationType.MODIFY_ARCHITECTURE, 'developer', detail='修改架构（拦截）')

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = '\n'.join(rt.log_lines) + '\n'
    out_path.write_text(content, encoding='utf-8')

    print_pass(f'SG-LOG日志已导出到: {out_path}')
    print(f'  共 {len(rt.log_lines)} 条日志，覆盖 S1→S4 阶段')
    print(f'  拦截次数: {rt.interception_count}')
    print(f'  文件大小: {len(content.encode("utf-8"))} bytes')
    return 0


def run_status(json_output: bool = False, enable_color: bool = True) -> int:
    """展示运行时组件状态。"""
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


def _get_stage_role(stage: str) -> str:
    from lib.stage_guardrails import STAGE_ROLES
    roles = STAGE_ROLES.get(stage, set())
    return next(iter(roles)) if roles else 'orchestrator'


def main():
    parser = argparse.ArgumentParser(
        description='阶段守卫运行时强制执行工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_common_args(parser)
    parser.add_argument('--demo', action='store_true',
                        help='使用内置demo演示运行时拦截功能（基础模式）')
    parser.add_argument('--full-flow', action='store_true',
                        help='演示完整S1→S8生命周期（含审批跳转、绕过检测）')
    parser.add_argument('--check', action='store_true',
                        help='单步拦截检查模式')
    parser.add_argument('--stage', type=str, help='阶段ID（S1~S8），--check模式必填')
    parser.add_argument('--role', type=str, help='执行角色')
    parser.add_argument('--op', type=str, help='操作类型（如write_code, clarify_requirement）')
    parser.add_argument('--detail', type=str, default='', help='操作描述文本')
    parser.add_argument('--export-logs', type=str, metavar='PATH',
                        help='将demo生成的SG-LOG日志导出到指定文件')
    parser.add_argument('--status', action='store_true',
                        help='显示运行时组件状态信息')
    parser.add_argument('--strict', action='store_true',
                        help='严格模式：WARN级别拦截返回非零退出码')
    parser.add_argument('--no-color', action='store_true',
                        help='禁用终端彩色输出')

    args = parser.parse_args()
    enable_color = not args.no_color

    mode_count = sum([args.demo, args.full_flow, args.check, bool(args.export_logs), args.status])
    if mode_count == 0:
        parser.print_help()
        return 0
    if mode_count > 1:
        print_error('只能选择一种模式（--demo/--full-flow/--check/--export-logs/--status）')
        return 2

    if args.demo:
        return run_demo(json_output=args.json, strict=args.strict, enable_color=enable_color)

    if args.full_flow:
        return run_full_flow(json_output=args.json, strict=args.strict, enable_color=enable_color)

    if args.check:
        if not args.stage or not args.role or not args.op:
            print_error('--check模式需要同时指定 --stage、--role、--op 参数')
            return 2
        return run_check(args.stage, args.role, args.op, detail=args.detail,
                         json_output=args.json, strict=args.strict, enable_color=enable_color)

    if args.export_logs:
        return run_export_logs(args.export_logs, enable_color=enable_color)

    if args.status:
        return run_status(json_output=args.json, enable_color=enable_color)

    return 0


if __name__ == '__main__':
    sys.exit(main())
