#!/usr/bin/env python3
"""阶段守卫日志分析工具。

解析开发会话输出中的 [SG-LOG] 和 [PDR-LOG] 结构化日志，
检测阶段守卫执行过程中的异常情况：
- 阶段未正确进入/退出（缺少STAGE_ENTER/STAGE_EXIT）
- 跨阶段拦截后继续执行越界操作（INTERCEPTED）
- 阶段跳转申请缺少审批记录（JUMP_REQUEST无JUMP_APPROVED）
- ERROR级别日志缺少恢复建议（recovery_hint缺失）
- 前置文档缺失未标注风险等级和处理措施
- 跳过前置文档读取流程直接进入执行（NO_PDR_FOR_STAGE）
- 日志格式不规范无法解析（MALFORMED_LOG）

用法:
    python check-stage-guardrails.py --log-file <session_log_path>
    python check-stage-guardrails.py --log-file <session_log_path> --json
    python check-stage-guardrails.py --log-file <session_log_path> --strict  # 严格模式
    python check-stage-guardrails.py --demo  # 使用内置示例日志演示分析
    python check-stage-guardrails.py --demo --strict  # 演示严格模式效果

参数说明:
    --log-file PATH   指定会话日志文件路径
    --demo            使用内置示例日志演示分析功能
    --strict          严格模式：WARN级别异常也返回非零退出码（CI集成用）
    --json            以JSON格式输出分析结果（机器可读）

CI集成:
    CI流水线（ci-check.ps1/ci-check.sh）第11项自动调用本工具 --strict 模式。
    日志文件查找顺序：
      1. 环境变量 STAGE_GUARDRAIL_LOG 指定的路径
      2. .agents/logs/ 目录下最新的 *.log 文件
      3. 无日志文件时跳过检查（非agent工作流无SG-LOG输出）

退出码:
    0  所有检查通过（严格模式下ERROR+WARN均为0）
    1  发现异常（正常模式下仅ERROR导致失败；严格模式下WARN/ERROR均导致失败）

Demo日志覆盖场景:
    demo-001: 完整S1→S2→S3(审批跳过)→S4流程，演示正常执行+审批跳转+S3/S4跳过PDR警告
    demo-002: S1阶段越界操作被拦截（INTERCEPTED），演示跨阶段拦截
    demo-003: 完整S5测试阶段流程（含PDR），演示正常收尾
    demo-004: 未审批跳转ERROR日志（缺recovery_hint→ERROR_NO_RECOVERY警告）
    demo-005: 文档缺失未标风险（MISSING_RISK_ANNOTATION）+ 格式不规范日志（MALFORMED_LOG）
    Demo数据仅含WARN不含ERROR，用于演示 --strict 模式下WARN也导致失败的效果。

相关文档:
    日志格式规范: .agents/rules/stage-guardrails.md（结构化日志格式章节）
    PDR日志规范:  .agents/protocols/pre-document-reading.md（结构化日志输出章节）
    日志输出指引: .agents/workflows/feature-development.md（结构化日志输出要求章节）
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, add_common_args, setup_safe_output
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

SG_EVENTS = {
    'STAGE_ENTER', 'DOC_CHECK', 'DOC_READ', 'DOC_MISSING',
    'BOUNDARY_CHECK', 'BOUNDARY_PASS', 'INTERCEPT', 'BYPASS_DETECTED',
    'JUMP_REQUEST', 'JUMP_APPROVED', 'JUMP_REJECTED', 'STAGE_EXIT', 'ERROR',
    'PDR_CONFIRM',
}

PDR_EVENTS = {
    'PDR_START', 'PDR_DOC_READ', 'PDR_DOC_SKIP', 'PDR_DOC_MISSING',
    'PDR_DOC_REQ_GAP', 'PDR_CONFIRM', 'PDR_ERROR',
}

SG_LEVELS = {'DEBUG', 'INFO', 'WARN', 'ERROR'}

STAGE_ORDER = {'S1': 1, 'S2': 2, 'S3': 3, 'S4': 4, 'S5': 5, 'S6': 6, 'S7': 7, 'S8': 8}
STAGE_NAMES = {
    'S1': '需求接收', 'S2': '方案设计', 'S3': '任务分配', 'S4': '代码实现',
    'S5': '测试编写', 'S6': '代码审查', 'S7': '合并代码', 'S8': '完成确认',
}

ERROR_TYPES = {'UNAUTHORIZED_JUMP', 'CRITICAL_DOC_MISSING', 'VIOLATION_EXECUTED',
               'INVALID_STATE', 'APPROVAL_CONFLICT', 'CRITICAL_MISSING', 'PARSE_ERROR',
               'PERMISSION_DENIED', 'CIRCULAR_REF'}


@dataclass
class LogEntry:
    prefix: str
    level: str
    event: str
    stage: str
    role: str
    session: str
    msg: str
    ctx: dict = field(default_factory=dict)
    line_num: int = 0

    @property
    def is_sg(self) -> bool:
        return self.prefix == 'SG-LOG'

    @property
    def is_pdr(self) -> bool:
        return self.prefix == 'PDR-LOG'


@dataclass
class AnalysisIssue:
    severity: str
    code: str
    message: str
    line_num: int = 0
    entry: Optional[LogEntry] = None


def parse_ctx(ctx_str: Optional[str]) -> dict:
    if not ctx_str or not ctx_str.strip():
        return {}
    ctx_str = ctx_str.strip()
    try:
        return json.loads(ctx_str)
    except json.JSONDecodeError:
        return {"_raw": ctx_str, "_parse_error": True}


def parse_log_file(content: str) -> tuple[list[LogEntry], list[AnalysisIssue]]:
    entries = []
    issues = []
    for line_num, line in enumerate(content.splitlines(), 1):
        line = line.strip()
        if '[SG-LOG]' not in line and '[PDR-LOG]' not in line:
            continue
        m = LOG_LINE_RE.search(line)
        if not m:
            issues.append(AnalysisIssue(
                severity='WARN',
                code='MALFORMED_LOG',
                message=f'日志格式不规范，无法解析',
                line_num=line_num,
            ))
            continue
        prefix, level, event, stage, role, session, msg, ctx_str = m.groups()
        ctx = parse_ctx(ctx_str)

        entry = LogEntry(
            prefix=prefix,
            level=level.strip(),
            event=event.strip(),
            stage=stage.strip(),
            role=role.strip(),
            session=session.strip(),
            msg=msg.strip(),
            ctx=ctx,
            line_num=line_num,
        )

        if entry.is_sg and entry.event not in SG_EVENTS:
            issues.append(AnalysisIssue(
                severity='WARN',
                code='UNKNOWN_EVENT',
                message=f'未知的SG事件类型: {entry.event}',
                line_num=line_num,
                entry=entry,
            ))
        if entry.is_pdr and entry.event not in PDR_EVENTS:
            issues.append(AnalysisIssue(
                severity='WARN',
                code='UNKNOWN_EVENT',
                message=f'未知的PDR事件类型: {entry.event}',
                line_num=line_num,
                entry=entry,
            ))
        if entry.level not in SG_LEVELS:
            issues.append(AnalysisIssue(
                severity='WARN',
                code='UNKNOWN_LEVEL',
                message=f'未知的日志级别: {entry.level}',
                line_num=line_num,
                entry=entry,
            ))
        if entry.stage not in STAGE_ORDER:
            issues.append(AnalysisIssue(
                severity='WARN',
                code='UNKNOWN_STAGE',
                message=f'未知的阶段ID: {entry.stage}',
                line_num=line_num,
                entry=entry,
            ))

        entries.append(entry)

    return entries, issues


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


DEMO_LOGS = """[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S1 | role=orchestrator | session=demo-001 | msg=进入需求接收阶段，开始明确需求边界与验收标准 | ctx={"entry_condition":"收到用户需求描述","prev_stage":null}
[PDR-LOG] | level=INFO | event=PDR_START | stage=S1 | role=orchestrator | session=demo-001 | msg=开始前置文档读取,共3份文档待读取 | ctx={"required_count":3,"required_docs":["用户需求原始描述","项目README.md","相关历史spec"],"resume":false}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S1 | role=orchestrator | session=demo-001 | msg=已读取: 用户需求原始描述 | ctx={"doc":"用户输入","bytes":520,"key_points":["需要用户认证功能","支持JWT"]}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S1 | role=orchestrator | session=demo-001 | msg=已读取: README.md | ctx={"doc":"README.md","bytes":3200,"key_points":["项目技术栈:FastAPI+PostgreSQL"]}
[PDR-LOG] | level=WARN | event=PDR_DOC_MISSING | stage=S1 | role=orchestrator | session=demo-001 | msg=前置文档缺失: 相关历史spec | ctx={"doc":".trae/specs/auth/*","risk":"low","risk_detail":"无相关历史spec,不影响当前工作","action":"annotate"}
[PDR-LOG] | level=INFO | event=PDR_CONFIRM | stage=S1 | role=orchestrator | session=demo-001 | msg=前置文档确认完成: 2份已读取,1份缺失已标注风险 | ctx={"read_count":2,"missing_count":1,"missing_with_risk":1,"ready_to_proceed":true}
[SG-LOG] | level=INFO | event=STAGE_EXIT | stage=S1 | role=orchestrator | session=demo-001 | msg=阶段需求接收已完成,退出标准满足 | ctx={"exit_criteria_met":["需求已澄清","验收标准已明确"],"duration":"5min","output_artifacts":["任务分解清单"],"next_stage":"S2"}
[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S2 | role=architect | session=demo-001 | msg=进入方案设计阶段，开始产出可执行的技术方案 | ctx={"entry_condition":"收到任务分解清单","prev_stage":"S1"}
[PDR-LOG] | level=INFO | event=PDR_START | stage=S2 | role=architect | session=demo-001 | msg=开始前置文档读取,共4份文档待读取 | ctx={"required_count":4,"required_docs":["任务分解清单","技术栈文档","架构文档","开发规范"],"resume":false}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S2 | role=architect | session=demo-001 | msg=已读取: 任务分解清单 | ctx={"doc":"task-list.md","bytes":1200,"key_points":["用户认证模块","JWT+Refresh Token"]}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S2 | role=architect | session=demo-001 | msg=已读取: docs/development-standards.md | ctx={"doc":"docs/development-standards.md","bytes":8420,"key_points":["Conventional Commits","测试覆盖率>=80%"]}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S2 | role=architect | session=demo-001 | msg=已读取: 架构文档 | ctx={"doc":".agents/modules/","bytes":5800,"key_points":["分层架构模式"]}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S2 | role=architect | session=demo-001 | msg=已读取: 技术栈文档 | ctx={"doc":"docs/knowledge/","bytes":2100,"key_points":["FastAPI","SQLAlchemy","PyJWT"]}
[PDR-LOG] | level=INFO | event=PDR_CONFIRM | stage=S2 | role=architect | session=demo-001 | msg=前置文档确认完成: 4份已读取,0份缺失 | ctx={"read_count":4,"missing_count":0,"missing_with_risk":0,"ready_to_proceed":true}
[SG-LOG] | level=DEBUG | event=BOUNDARY_CHECK | stage=S2 | role=architect | session=demo-001 | msg=校验操作合法性: 设计用户认证模块分层架构 | ctx={"operation":"架构设计","allowed_ops":["技术可行性分析","架构设计","技术选型","接口定义","风险评估"]}
[SG-LOG] | level=DEBUG | event=BOUNDARY_PASS | stage=S2 | role=architect | session=demo-001 | msg=操作通过边界检查: 设计用户认证模块分层架构 | ctx={"operation":"架构设计"}
[SG-LOG] | level=INFO | event=STAGE_EXIT | stage=S2 | role=architect | session=demo-001 | msg=阶段方案设计已完成,退出标准满足 | ctx={"exit_criteria_met":["技术方案已完成","风险评估已覆盖","接口定义已明确"],"duration":"15min","output_artifacts":["技术方案文档","接口定义文档"],"next_stage":"S3"}
[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S3 | role=orchestrator | session=demo-001 | msg=进入任务分配阶段，开始匹配角色明确交付要求 | ctx={"entry_condition":"技术方案已确认","prev_stage":"S2"}
[SG-LOG] | level=INFO | event=JUMP_REQUEST | stage=S3 | role=developer | session=demo-001 | msg=申请阶段跳转: 从S3任务分配正向跳至S4代码实现 | ctx={"jump_type":"skip","from_stage":"S3","to_stage":"S4","reason":"方案明确,任务单一,无需独立分配阶段","requested_by":"developer"}
[SG-LOG] | level=INFO | event=JUMP_APPROVED | stage=S3 | role=orchestrator | session=demo-001 | msg=阶段跳转已批准: S3→S4跳过任务分配 | ctx={"jump_type":"skip","approved_by":"orchestrator","conditions":"developer直接按方案执行"}
[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S4 | role=developer | session=demo-001 | msg=进入代码实现阶段，开始按方案完成编码与单元测试 | ctx={"entry_condition":"收到任务分配+技术方案","prev_stage":"S3"}
[SG-LOG] | level=WARN | event=INTERCEPT | stage=S1 | role=developer | session=demo-002 | msg=阶段守卫拦截: 编写Redis配置代码属于S4代码实现阶段职责 | ctx={"current_stage":"S1","violating_operation":"编写Redis配置代码","target_stage":"S4","exit_criteria":"明确功能边界与验收标准"}
[SG-LOG] | level=INFO | event=STAGE_EXIT | stage=S4 | role=developer | session=demo-001 | msg=阶段代码实现已完成,退出标准满足 | ctx={"exit_criteria_met":["核心功能编码完成","单元测试通过"],"duration":"45min","output_artifacts":["auth.py","test_auth.py"],"next_stage":"S5"}
[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S5 | role=tester | session=demo-003 | msg=进入测试编写阶段，开始编写测试用例 | ctx={"entry_condition":"收到代码实现产物","prev_stage":"S4"}
[PDR-LOG] | level=INFO | event=PDR_START | stage=S5 | role=tester | session=demo-003 | msg=开始前置文档读取,共2份文档待读取 | ctx={"required_count":2,"required_docs":["技术方案文档","代码实现产物"],"resume":false}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S5 | role=tester | session=demo-003 | msg=已读取: 技术方案文档 | ctx={"doc":"technical-design.md","bytes":5600,"key_points":["JWT认证流程","接口契约"]}
[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S5 | role=tester | session=demo-003 | msg=已读取: 代码实现产物 | ctx={"doc":"auth.py","bytes":3200,"key_points":["login/logout接口","token刷新逻辑"]}
[PDR-LOG] | level=INFO | event=PDR_CONFIRM | stage=S5 | role=tester | session=demo-003 | msg=前置文档确认完成: 2份已读取,0份缺失 | ctx={"read_count":2,"missing_count":0,"missing_with_risk":0,"ready_to_proceed":true}
[SG-LOG] | level=INFO | event=STAGE_EXIT | stage=S5 | role=tester | session=demo-003 | msg=阶段测试编写已完成,退出标准满足 | ctx={"exit_criteria_met":["测试用例编写完成","测试报告已生成"],"duration":"20min","output_artifacts":["test_auth.py","test_report.md"],"next_stage":"S6"}
[SG-LOG] | level=ERROR | event=ERROR | stage=S4 | role=developer | session=demo-004 | msg=检测到未经审批的阶段跳转 | ctx={"error_type":"UNAUTHORIZED_JUMP","error_detail":"S4→S6跳转无orchestrator批准记录","impact":"代码未经测试可能引入缺陷"}
[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S1 | role=developer | session=demo-005 | msg=进入需求接收阶段(演示文档缺失未标风险+格式异常) | ctx={"entry_condition":"收到需求","prev_stage":null}
[PDR-LOG] | level=INFO | event=PDR_START | stage=S1 | role=developer | session=demo-005 | msg=开始前置文档读取 | ctx={"required_count":2}
[PDR-LOG] | level=WARN | event=PDR_DOC_MISSING | stage=S1 | role=developer | session=demo-005 | msg=前置文档缺失: 架构约束文档 | ctx={"doc":"docs/architecture.md"}
[SG-LOG] 格式错误的日志行-缺少竖线分隔符无法被正常解析
"""


def run_analysis(content: str, json_output: bool = False, strict: bool = False) -> int:
    entries, parse_issues = parse_log_file(content)
    analysis_issues = analyze(entries)
    all_issues = parse_issues + analysis_issues

    error_count = sum(1 for i in all_issues if i.severity == 'ERROR')
    warn_count = sum(1 for i in all_issues if i.severity == 'WARN')
    pass_count = max(0, len(entries) - error_count - warn_count)

    if json_output:
        result = {
            "summary": {
                "strict": strict,
                "total_log_entries": len(entries),
                "sg_entries": sum(1 for e in entries if e.is_sg),
                "pdr_entries": sum(1 for e in entries if e.is_pdr),
                "errors": error_count,
                "warnings": warn_count,
                "passed": pass_count,
            },
            "issues": [
                {
                    "severity": i.severity,
                    "code": i.code,
                    "message": i.message,
                    "line": i.line_num,
                    "stage": i.entry.stage if i.entry else None,
                    "event": i.entry.event if i.entry else None,
                }
                for i in all_issues
            ],
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if (error_count > 0 or (strict and warn_count > 0)) else 0

    header_title = "阶段守卫日志分析 [STRICT MODE]" if strict else "阶段守卫日志分析"
    print_header(header_title)
    print(f"  日志条目总数: {len(entries)} (SG: {sum(1 for e in entries if e.is_sg)}, PDR: {sum(1 for e in entries if e.is_pdr)})")
    if strict:
        print(f"  严格模式: WARN级别异常将导致非零退出码")

    if not all_issues:
        print_pass("未发现任何异常，阶段守卫执行记录完整合规")
    else:
        for issue in all_issues:
            if issue.severity == 'ERROR':
                detail = f" (line {issue.line_num})" if issue.line_num else ""
                print_error(f"[{issue.code}] {issue.message}{detail}")
            else:
                detail = f" (line {issue.line_num})" if issue.line_num else ""
                print_warn(f"[{issue.code}] {issue.message}{detail}")

    print_summary(pass_count=pass_count, warn_count=warn_count, error_count=error_count)
    return 1 if (error_count > 0 or (strict and warn_count > 0)) else 0


def main():
    setup_safe_output()
    parser = argparse.ArgumentParser(description='阶段守卫日志分析工具')
    add_common_args(parser)
    parser.add_argument('--log-file', type=str, help='会话日志文件路径')
    parser.add_argument('--demo', action='store_true', help='使用内置示例日志演示分析功能')
    parser.add_argument('--strict', action='store_true', help='严格模式: WARN级别异常也返回非零退出码')
    args = parser.parse_args()

    if args.demo:
        print("=== 使用内置示例日志进行演示分析 ===\n")
        return run_analysis(DEMO_LOGS, json_output=args.json, strict=args.strict)

    if not args.log_file:
        print_error("必须指定 --log-file <路径> 或使用 --demo")
        parser.print_help()
        return 1

    log_path = Path(args.log_file)
    if not log_path.exists():
        print_error(f"日志文件不存在: {log_path}")
        return 1

    try:
        content = log_path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as e:
        print_error(f"读取日志文件失败: {e}")
        return 1

    return run_analysis(content, json_output=args.json, strict=args.strict)


if __name__ == '__main__':
    sys.exit(main())
