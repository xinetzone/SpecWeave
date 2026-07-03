from pathlib import Path

from lib.cli import print_pass
from lib.stage_guardrails import (
    GuardrailRuntime,
    OperationType,
)


def run_export_logs(output_path: str, enable_color: bool = True) -> int:
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
