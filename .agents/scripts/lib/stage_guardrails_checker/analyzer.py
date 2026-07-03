import re
from .constants import STAGE_NAMES, ERROR_TYPES
from .models import LogEntry, AnalysisIssue
from .governance import check_governance_layers

def analyze(entries: list[LogEntry]) -> list[AnalysisIssue]:
    issues = []

    stage_entered = set()
    stage_exited = set()
    current_stage = None
    pending_jumps = []
    intercept_events = []
    error_events = []
    pdr_missing_events = []
    has_pdr_confirm_per_stage = {}

    governance_layers_delivered = set()
    governance_layer_first_seen = {}

    for entry in entries:
        if entry.event == 'STAGE_ENTER':
            if entry.stage in stage_entered and entry.stage not in stage_exited:
                issues.append(AnalysisIssue(
                    severity='WARN',
                    code='DUPLICATE_ENTER',
                    message=f'重复进入阶段 {entry.stage}（{STAGE_NAMES.get(entry.stage, "?")}），未先退出',
                    entry=entry,
                ))
            if current_stage and entry.ctx.get('prev_stage') != current_stage:
                prev = entry.ctx.get('prev_stage')
                if prev and prev != current_stage:
                    issues.append(AnalysisIssue(
                        severity='WARN',
                        code='STAGE_MISMATCH',
                        message=f'进入阶段{entry.stage}时prev_stage={prev}，但当前阶段为{current_stage}，可能存在阶段跳跃',
                        entry=entry,
                    ))
            stage_entered.add(entry.stage)
            current_stage = entry.stage

        elif entry.event == 'STAGE_EXIT':
            if entry.stage not in stage_entered:
                issues.append(AnalysisIssue(
                    severity='ERROR',
                    code='EXIT_WITHOUT_ENTER',
                    message=f'阶段 {entry.stage}（{STAGE_NAMES.get(entry.stage, "?")}）退出但未记录进入事件',
                    entry=entry,
                ))
            if entry.stage in stage_exited:
                issues.append(AnalysisIssue(
                    severity='WARN',
                    code='DUPLICATE_EXIT',
                    message=f'重复退出阶段 {entry.stage}',
                    entry=entry,
                ))
            stage_exited.add(entry.stage)

        elif entry.event == 'INTERCEPT':
            intercept_events.append(entry)
            target = entry.ctx.get('target_stage', '?')
            issues.append(AnalysisIssue(
                severity='WARN',
                code='INTERCEPTED',
                message=f'阶段守卫拦截: {entry.msg}（目标阶段: {target}）',
                entry=entry,
            ))

        elif entry.event == 'BYPASS_DETECTED':
            issues.append(AnalysisIssue(
                severity='ERROR',
                code='BYPASS_DETECTED',
                message=f'疑似绕过阶段守卫: {entry.msg}',
                entry=entry,
            ))

        elif entry.event == 'JUMP_REQUEST':
            pending_jumps.append(entry)

        elif entry.event in ('JUMP_APPROVED', 'JUMP_REJECTED'):
            matched = False
            entry_to = entry.ctx.get('to_stage', '')
            if not entry_to:
                msg = entry.msg
                arrow_match = re.search(r'[S](\d)\s*→\s*[S]?(\d)', msg)
                if arrow_match:
                    entry_to = f'S{arrow_match.group(2)}'
            for i, req in enumerate(pending_jumps):
                if req.session != entry.session:
                    continue
                req_to = req.ctx.get('to_stage', '?')
                if entry_to and req_to == entry_to:
                    matched = True
                    pending_jumps.pop(i)
                    break
            if not matched and not entry_to:
                for i, req in enumerate(pending_jumps):
                    if req.session == entry.session:
                        matched = True
                        pending_jumps.pop(i)
                        break
            if not matched:
                issues.append(AnalysisIssue(
                    severity='ERROR',
                    code='ORPHAN_APPROVAL',
                    message=f'阶段跳转审批（{entry.event}）无对应申请记录',
                    entry=entry,
                ))

        elif entry.event == 'ERROR':
            error_events.append(entry)
            error_type = entry.ctx.get('error_type', '')
            if error_type and error_type not in ERROR_TYPES:
                issues.append(AnalysisIssue(
                    severity='WARN',
                    code='UNKNOWN_ERROR_TYPE',
                    message=f'未知的错误类型: {error_type}',
                    entry=entry,
                ))

        elif entry.event == 'DOC_MISSING' or entry.event == 'PDR_DOC_MISSING':
            pdr_missing_events.append(entry)
            risk = entry.ctx.get('risk', '')
            action = entry.ctx.get('action', '')
            if not risk and not action:
                issues.append(AnalysisIssue(
                    severity='WARN',
                    code='MISSING_RISK_ANNOTATION',
                    message=f'前置文档缺失未标注风险等级和处理措施: {entry.msg}',
                    entry=entry,
                ))
            elif risk == 'high' and action == 'annotate':
                issues.append(AnalysisIssue(
                    severity='ERROR',
                    code='HIGH_RISK_CONTINUE',
                    message=f'高风险文档缺失但仅标注风险后继续，应中止并请求获取',
                    entry=entry,
                ))

        elif entry.event == 'PDR_CONFIRM':
            has_pdr_confirm_per_stage[entry.stage] = entry
            ready = entry.ctx.get('ready_to_proceed', True)
            missing = entry.ctx.get('missing_count', 0)
            if missing > 0 and ready:
                missing_with_risk = entry.ctx.get('missing_with_risk', 0)
                if missing_with_risk < missing:
                    issues.append(AnalysisIssue(
                        severity='ERROR',
                        code='MISSING_WITHOUT_RISK',
                        message=f'PDR_CONFIRM显示{missing}份文档缺失，但仅{missing_with_risk}份标注了风险',
                        entry=entry,
                    ))

        elif entry.event == 'BOUNDARY_CHECK':
            pass

        issues.extend(check_governance_layers(
            entry, governance_layers_delivered, governance_layer_first_seen
        ))

    for req in pending_jumps:
        issues.append(AnalysisIssue(
            severity='ERROR',
            code='PENDING_JUMP',
            message=f'阶段跳转申请（{req.ctx.get("from_stage","?")}→{req.ctx.get("to_stage","?")}）无审批结果记录',
            entry=req,
        ))

    for err in error_events:
        recovery = err.ctx.get('recovery_hint', err.ctx.get('recovery', ''))
        if not recovery:
            issues.append(AnalysisIssue(
                severity='WARN',
                code='ERROR_NO_RECOVERY',
                message=f'ERROR日志缺少恢复建议: {err.msg}',
                entry=err,
            ))

    sg_only_entries = [e for e in entries if e.is_sg]
    pdr_only_entries = [e for e in entries if e.is_pdr]

    if not sg_only_entries:
        issues.append(AnalysisIssue(
            severity='WARN',
            code='NO_SG_LOGS',
            message='日志中未发现任何 [SG-LOG] 记录，阶段守卫日志可能未启用',
        ))

    stages_with_pdr = set(e.stage for e in pdr_only_entries if e.event == 'PDR_START')
    stages_with_enter = set(e.stage for e in sg_only_entries if e.event == 'STAGE_ENTER')
    for stage in stages_with_enter:
        if stage not in stages_with_pdr and stage not in ('S7', 'S8'):
            issues.append(AnalysisIssue(
                severity='WARN',
                code='NO_PDR_FOR_STAGE',
                message=f'阶段 {stage}（{STAGE_NAMES.get(stage, "?")}）有STAGE_ENTER但无PDR_START记录，前置文档读取可能被跳过',
            ))

    return issues