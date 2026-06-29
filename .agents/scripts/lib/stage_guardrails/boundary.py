#!/usr/bin/env python3
"""操作边界校验引擎。

基于[stage-guardrails.md]中8个阶段的允许/禁止操作清单，
在运行时对智能体的操作进行实时合法性校验，
拦截跨阶段越界操作并给出标准拦截提示。

使用方式:
    from lib.stage_guardrails import BoundaryChecker, OperationType, BoundaryResult
    checker = BoundaryChecker()
    result = checker.check(
        operation=OperationType.WRITE_CODE,
        current_stage='S1',
        current_role='orchestrator',
        detail='编写Redis配置代码',
    )
    if not result.allowed:
        print(result.format_intercept_message())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from lib.stage_guardrails.state import (
    STAGE_ORDER,
    STAGE_NAMES,
    STAGE_ROLES,
    VALID_ROLES,
)


class OperationType(Enum):
    """操作类型枚举，覆盖智能体在开发流程中的各类操作。

    命名约定：使用动词短语，描述"做什么"而非"用什么工具"。
    工具调用（Edit/Write/RunCommand等）应映射到对应的OperationType。
    """

    READ_DOCS = 'read_docs'
    SEARCH_CODE = 'search_code'
    CLARIFY_REQUIREMENT = 'clarify_requirement'
    WRITE_SPEC = 'write_spec'
    CREATE_TASK_LIST = 'create_task_list'
    ESTIMATE_PRIORITY = 'estimate_priority'
    IDENTIFY_RISK = 'identify_risk'
    DISCUSS_TECH_IMPLEMENTATION = 'discuss_tech_implementation'
    CHOOSE_TECH_STACK = 'choose_tech_stack'
    WRITE_CODE = 'write_code'
    ESTIMATE_LINES = 'estimate_lines'
    ARCHITECTURE_DESIGN = 'architecture_design'
    MODULE_PARTITION = 'module_partition'
    DEFINE_API = 'define_api'
    DEFINE_DATA_MODEL = 'define_data_model'
    TECH_FEASIBILITY = 'tech_feasibility'
    ASSESS_IMPACT_SCOPE = 'assess_impact_scope'
    MODIFY_BUSINESS_CODE = 'modify_business_code'
    SPECIFY_IMPLEMENTATION_DETAIL = 'specify_implementation_detail'
    ASSIGN_TASK = 'assign_task'
    SET_DEADLINE = 'set_deadline'
    SET_ACCEPTANCE_CRITERIA = 'set_acceptance_criteria'
    MODIFY_ARCHITECTURE = 'modify_architecture'
    START_CODING_WITHOUT_SPEC = 'start_coding_without_spec'
    FOLLOW_CODING_STANDARDS = 'follow_coding_standards'
    CHOOSE_IMPLEMENTATION_APPROACH = 'choose_implementation_approach'
    SUBMIT_PR = 'submit_pr'
    WRITE_UNIT_TEST = 'write_unit_test'
    RUN_TEST = 'run_test'
    CHANGE_TECH_SELECTION = 'change_tech_selection'
    SKIP_UNIT_TEST = 'skip_unit_test'
    ADD_UNPLANNED_FEATURE = 'add_unplanned_feature'
    DESIGN_TEST_CASE = 'design_test_case'
    WRITE_INTEGRATION_TEST = 'write_integration_test'
    WRITE_E2E_TEST = 'write_e2e_test'
    RECORD_DEFECT = 'record_defect'
    REPORT_DEFECT = 'report_defect'
    VERIFY_FIX = 'verify_fix'
    FIX_BUG = 'fix_bug'
    TEST_ONLY_HAPPY_PATH = 'test_only_happy_path'
    SKIP_DEFECT_RECORD = 'skip_defect_record'
    REVIEW_CODE = 'review_code'
    REVIEW_SECURITY = 'review_security'
    REVIEW_PERFORMANCE = 'review_performance'
    GIVE_REVIEW_FEEDBACK = 'give_review_feedback'
    APPROVE_MERGE = 'approve_merge'
    REJECT_MERGE = 'reject_merge'
    GIVE_VAGUE_FEEDBACK = 'give_vague_feedback'
    FORCE_MERGE = 'force_merge'
    SKIP_CI_CHECK = 'skip_ci_check'
    NOTIFY_AFTER_MERGE = 'notify_after_merge'
    TRIGGER_CI_CD = 'trigger_ci_cd'
    IGNORE_CONFLICT = 'ignore_conflict'
    VERIFY_ACCEPTANCE = 'verify_acceptance'
    MARK_TASK_COMPLETE = 'mark_task_complete'
    NOTIFY_STAKEHOLDERS = 'notify_stakeholders'
    ARCHIVE_DOCS = 'archive_docs'
    SKIP_REGRESSION = 'skip_regression'
    CLOSE_WITHOUT_NOTIFICATION = 'close_without_notification'
    MARK_INCOMPLETE_COMPLETE = 'mark_incomplete_complete'


STAGE_EXIT_CRITERIA: dict[str, str] = {
    'S1': '明确功能边界与验收标准，输出任务分解清单',
    'S2': '技术方案完成且经orchestrator确认，风险评估覆盖，接口定义明确',
    'S3': '任务分配通知已发送至各角色，交付时间与验收标准明确',
    'S4': 'PR已创建，本地测试通过，单元测试覆盖核心路径',
    'S5': '测试报告已生成，缺陷已记录并反馈至developer',
    'S6': '审查报告已输出，合并决策明确（批准/退回修改）',
    'S7': 'CI流程通过，代码已合并，相关角色已通知',
    'S8': '任务状态已更新，相关方已通知，文档已归档',
}


_STAGE_PERMISSIONS: dict[str, dict] = {
    'S1': {
        'allowed': {
            OperationType.READ_DOCS,
            OperationType.SEARCH_CODE,
            OperationType.CLARIFY_REQUIREMENT,
            OperationType.WRITE_SPEC,
            OperationType.CREATE_TASK_LIST,
            OperationType.ESTIMATE_PRIORITY,
            OperationType.IDENTIFY_RISK,
        },
        'denied': {
            OperationType.DISCUSS_TECH_IMPLEMENTATION,
            OperationType.CHOOSE_TECH_STACK,
            OperationType.WRITE_CODE,
            OperationType.ESTIMATE_LINES,
            OperationType.START_CODING_WITHOUT_SPEC,
        },
        'deny_reason': {
            OperationType.DISCUSS_TECH_IMPLEMENTATION: '讨论具体技术实现方案属于②方案设计阶段职责',
            OperationType.CHOOSE_TECH_STACK: '指定技术选型或框架属于②方案设计阶段职责',
            OperationType.WRITE_CODE: '编写代码属于④代码实现阶段职责',
            OperationType.ESTIMATE_LINES: '估算代码行数或技术细节属于②方案设计阶段职责',
            OperationType.START_CODING_WITHOUT_SPEC: '跳过需求澄清直接进入设计违反阶段守卫核心原则',
        },
    },
    'S2': {
        'allowed': {
            OperationType.READ_DOCS,
            OperationType.SEARCH_CODE,
            OperationType.TECH_FEASIBILITY,
            OperationType.ARCHITECTURE_DESIGN,
            OperationType.MODULE_PARTITION,
            OperationType.CHOOSE_TECH_STACK,
            OperationType.DEFINE_API,
            OperationType.DEFINE_DATA_MODEL,
            OperationType.IDENTIFY_RISK,
            OperationType.ASSESS_IMPACT_SCOPE,
            OperationType.DISCUSS_TECH_IMPLEMENTATION,
        },
        'denied': {
            OperationType.MODIFY_BUSINESS_CODE,
            OperationType.WRITE_CODE,
            OperationType.SPECIFY_IMPLEMENTATION_DETAIL,
        },
        'deny_reason': {
            OperationType.MODIFY_BUSINESS_CODE: '直接修改已有代码文件属于④代码实现阶段职责',
            OperationType.WRITE_CODE: '编写业务逻辑代码属于④代码实现阶段职责',
            OperationType.SPECIFY_IMPLEMENTATION_DETAIL: '指定具体实现细节（如变量名、函数内部逻辑）属于④代码实现阶段职责',
        },
    },
    'S3': {
        'allowed': {
            OperationType.READ_DOCS,
            OperationType.SEARCH_CODE,
            OperationType.ASSIGN_TASK,
            OperationType.SET_DEADLINE,
            OperationType.SET_ACCEPTANCE_CRITERIA,
            OperationType.ESTIMATE_PRIORITY,
            OperationType.CREATE_TASK_LIST,
        },
        'denied': {
            OperationType.MODIFY_ARCHITECTURE,
            OperationType.WRITE_CODE,
            OperationType.START_CODING_WITHOUT_SPEC,
        },
        'deny_reason': {
            OperationType.MODIFY_ARCHITECTURE: '修改技术方案核心内容（架构、选型、接口定义）属于②方案设计阶段职责，需由architect确认',
            OperationType.WRITE_CODE: '直接开始编码属于④代码实现阶段职责，必须先完成任务分配',
            OperationType.START_CODING_WITHOUT_SPEC: '跳过architect确认自行决定技术方案违反协作协议',
        },
    },
    'S4': {
        'allowed': {
            OperationType.READ_DOCS,
            OperationType.SEARCH_CODE,
            OperationType.WRITE_CODE,
            OperationType.MODIFY_BUSINESS_CODE,
            OperationType.WRITE_UNIT_TEST,
            OperationType.RUN_TEST,
            OperationType.FOLLOW_CODING_STANDARDS,
            OperationType.CHOOSE_IMPLEMENTATION_APPROACH,
            OperationType.SUBMIT_PR,
            OperationType.FIX_BUG,
        },
        'denied': {
            OperationType.MODIFY_ARCHITECTURE,
            OperationType.CHANGE_TECH_SELECTION,
            OperationType.SKIP_UNIT_TEST,
            OperationType.ADD_UNPLANNED_FEATURE,
            OperationType.DISCUSS_TECH_IMPLEMENTATION,
        },
        'deny_reason': {
            OperationType.MODIFY_ARCHITECTURE: '擅自变更架构决策需回退至②方案设计阶段重新设计',
            OperationType.CHANGE_TECH_SELECTION: '擅自更换技术选型违反架构决策，需经architect批准并回退至②方案设计阶段',
            OperationType.SKIP_UNIT_TEST: '跳过单元测试直接提交违反开发规范，单元测试覆盖率需达80%以上',
            OperationType.ADD_UNPLANNED_FEATURE: '实现方案中未包含的功能属于范围蔓延，需回到①需求接收阶段重新确认',
            OperationType.DISCUSS_TECH_IMPLEMENTATION: '技术实现方案讨论应在②方案设计阶段完成，编码阶段应按既定方案执行',
        },
    },
    'S5': {
        'allowed': {
            OperationType.READ_DOCS,
            OperationType.SEARCH_CODE,
            OperationType.DESIGN_TEST_CASE,
            OperationType.WRITE_UNIT_TEST,
            OperationType.WRITE_INTEGRATION_TEST,
            OperationType.WRITE_E2E_TEST,
            OperationType.RUN_TEST,
            OperationType.RECORD_DEFECT,
            OperationType.REPORT_DEFECT,
            OperationType.VERIFY_FIX,
            OperationType.REVIEW_PERFORMANCE,
        },
        'denied': {
            OperationType.FIX_BUG,
            OperationType.MODIFY_BUSINESS_CODE,
            OperationType.TEST_ONLY_HAPPY_PATH,
            OperationType.SKIP_DEFECT_RECORD,
        },
        'deny_reason': {
            OperationType.FIX_BUG: 'tester不得自行修复缺陷，必须反馈给developer修复',
            OperationType.MODIFY_BUSINESS_CODE: 'tester不得修改业务逻辑代码，修复工作属于developer职责',
            OperationType.TEST_ONLY_HAPPY_PATH: '仅测试happy path忽略边界条件和异常情况违反测试规范',
            OperationType.SKIP_DEFECT_RECORD: '跳过缺陷记录直接标记测试通过违反测试规范',
        },
    },
    'S6': {
        'allowed': {
            OperationType.READ_DOCS,
            OperationType.SEARCH_CODE,
            OperationType.REVIEW_CODE,
            OperationType.REVIEW_SECURITY,
            OperationType.REVIEW_PERFORMANCE,
            OperationType.GIVE_REVIEW_FEEDBACK,
            OperationType.APPROVE_MERGE,
            OperationType.REJECT_MERGE,
        },
        'denied': {
            OperationType.MODIFY_BUSINESS_CODE,
            OperationType.WRITE_CODE,
            OperationType.GIVE_VAGUE_FEEDBACK,
        },
        'deny_reason': {
            OperationType.MODIFY_BUSINESS_CODE: 'reviewer不得直接修改业务代码，应给出改进建议由developer修改',
            OperationType.WRITE_CODE: 'reviewer不得直接编写代码，修复工作属于developer职责',
            OperationType.GIVE_VAGUE_FEEDBACK: '不给出具体改进建议直接打回违反审查规范，必须说明问题位置和改进方向',
        },
    },
    'S7': {
        'allowed': {
            OperationType.READ_DOCS,
            OperationType.SEARCH_CODE,
            OperationType.RUN_TEST,
            OperationType.TRIGGER_CI_CD,
            OperationType.NOTIFY_AFTER_MERGE,
        },
        'denied': {
            OperationType.FORCE_MERGE,
            OperationType.SKIP_CI_CHECK,
            OperationType.IGNORE_CONFLICT,
            OperationType.APPROVE_MERGE,
        },
        'deny_reason': {
            OperationType.FORCE_MERGE: '审查未通过时强行合违反质量门禁',
            OperationType.SKIP_CI_CHECK: '跳过CI检查直接合并违反CI规范',
            OperationType.IGNORE_CONFLICT: '忽略冲突警告强制合并可能导致代码丢失',
            OperationType.APPROVE_MERGE: '审查批准属于reviewer（⑥代码审查阶段）职责，orchestrator仅负责合并执行',
        },
    },
    'S8': {
        'allowed': {
            OperationType.READ_DOCS,
            OperationType.SEARCH_CODE,
            OperationType.VERIFY_ACCEPTANCE,
            OperationType.MARK_TASK_COMPLETE,
            OperationType.NOTIFY_STAKEHOLDERS,
            OperationType.ARCHIVE_DOCS,
        },
        'denied': {
            OperationType.MARK_INCOMPLETE_COMPLETE,
            OperationType.SKIP_REGRESSION,
            OperationType.CLOSE_WITHOUT_NOTIFICATION,
            OperationType.WRITE_CODE,
            OperationType.MODIFY_BUSINESS_CODE,
        },
        'deny_reason': {
            OperationType.MARK_INCOMPLETE_COMPLETE: '验收标准未全部满足时标记任务完成违反验收规范',
            OperationType.SKIP_REGRESSION: '跳过回归验证直接关闭任务可能导致遗漏缺陷',
            OperationType.CLOSE_WITHOUT_NOTIFICATION: '不通知相关方单方面关闭任务违反协作规范',
            OperationType.WRITE_CODE: '完成确认阶段不得编写代码，如需修改必须回退至对应阶段',
            OperationType.MODIFY_BUSINESS_CODE: '完成确认阶段不得修改代码，如需修改必须回退至④代码实现阶段',
        },
    },
}

_UNIVERSAL_READ_OPS = {
    OperationType.READ_DOCS,
    OperationType.SEARCH_CODE,
}

OPERATION_CATEGORIES: dict[str, set[OperationType]] = {
    'read_only': _UNIVERSAL_READ_OPS,
    'code_modification': {
        OperationType.WRITE_CODE,
        OperationType.MODIFY_BUSINESS_CODE,
        OperationType.FIX_BUG,
    },
    'architecture': {
        OperationType.ARCHITECTURE_DESIGN,
        OperationType.MODULE_PARTITION,
        OperationType.DEFINE_API,
        OperationType.DEFINE_DATA_MODEL,
        OperationType.CHOOSE_TECH_STACK,
        OperationType.MODIFY_ARCHITECTURE,
        OperationType.CHANGE_TECH_SELECTION,
        OperationType.DISCUSS_TECH_IMPLEMENTATION,
    },
    'testing': {
        OperationType.DESIGN_TEST_CASE,
        OperationType.WRITE_UNIT_TEST,
        OperationType.WRITE_INTEGRATION_TEST,
        OperationType.WRITE_E2E_TEST,
        OperationType.RUN_TEST,
        OperationType.RECORD_DEFECT,
        OperationType.REPORT_DEFECT,
        OperationType.VERIFY_FIX,
    },
    'review': {
        OperationType.REVIEW_CODE,
        OperationType.REVIEW_SECURITY,
        OperationType.REVIEW_PERFORMANCE,
        OperationType.GIVE_REVIEW_FEEDBACK,
        OperationType.APPROVE_MERGE,
        OperationType.REJECT_MERGE,
        OperationType.GIVE_VAGUE_FEEDBACK,
    },
}


@dataclass
class BoundaryResult:
    """边界校验结果。"""
    allowed: bool
    operation: OperationType
    current_stage: str
    current_role: str
    message: str = ''
    target_stage: Optional[str] = None
    violation_type: Optional[str] = None
    deny_reason: str = ''
    exit_criteria_hint: str = ''
    suggested_action: str = ''
    log_level: str = 'DEBUG'
    ctx: dict = field(default_factory=dict)

    def format_intercept_message(self) -> str:
        """生成标准拦截输出格式（对应stage-guardrails.md的拦截输出格式）。"""
        if self.allowed:
            return ''
        stage_name = STAGE_NAMES.get(self.current_stage, self.current_stage)
        op_desc = self.deny_reason or self.message or self.operation.value
        lines = [
            f'⚠️ 阶段守卫拦截：当前为【{self.current_stage}{stage_name}】阶段，'
            f'【{op_desc}】。'
        ]
        if self.exit_criteria_hint:
            lines.append(f'请先完成当前阶段：{self.exit_criteria_hint}')
        if self.suggested_action:
            lines.append(self.suggested_action)
        else:
            lines.append('如需跳过或回退阶段，请提交阶段跳转申请（request_jump）并经orchestrator批准。')
        return '\n'.join(lines)

    def to_log_dict(self, session_id: str) -> dict:
        """生成SG-LOG日志上下文字段。"""
        return {
            'current_stage': self.current_stage,
            'violating_operation': self.operation.value,
            'target_stage': self.target_stage,
            'violation_type': self.violation_type,
            'detail': self.message,
            'session': session_id,
        }


class BoundaryChecker:
    """操作边界校验引擎。

    基于8个阶段的允许/禁止操作清单，对智能体操作进行实时校验。
    只读操作（READ_DOCS/SEARCH_CODE）在所有阶段均被允许。
    """

    def __init__(self):
        self._permissions = _STAGE_PERMISSIONS
        self._exit_criteria = STAGE_EXIT_CRITERIA

    def get_allowed_operations(self, stage: str) -> set[OperationType]:
        """获取指定阶段的允许操作集合。"""
        if stage not in self._permissions:
            return set()
        return self._permissions[stage]['allowed'].copy()

    def get_denied_operations(self, stage: str) -> set[OperationType]:
        """获取指定阶段的明确禁止操作集合。"""
        if stage not in self._permissions:
            return set()
        return self._permissions[stage]['denied'].copy()

    def is_read_only_operation(self, op: OperationType) -> bool:
        """判断是否为全局允许的只读操作。"""
        return op in _UNIVERSAL_READ_OPS

    def check(self,
              operation: OperationType,
              current_stage: Optional[str],
              current_role: str,
              detail: str = '',
              extra_ctx: Optional[dict] = None) -> BoundaryResult:
        """校验操作是否符合当前阶段的边界约束。

        Args:
            operation: 操作类型
            current_stage: 当前阶段ID（S1~S8），None表示未进入任何阶段
            current_role: 执行角色
            detail: 操作详情描述（用于拦截消息和日志）
            extra_ctx: 额外上下文（如目标文件、操作参数等）

        Returns:
            BoundaryResult 校验结果
        """
        ctx = extra_ctx or {}

        if operation in _UNIVERSAL_READ_OPS:
            return BoundaryResult(
                allowed=True,
                operation=operation,
                current_stage=current_stage or 'NONE',
                current_role=current_role,
                message=detail or f'只读操作通过: {operation.value}',
                log_level='DEBUG',
                ctx=ctx,
            )

        if current_stage is None:
            return BoundaryResult(
                allowed=False,
                operation=operation,
                current_stage='NONE',
                current_role=current_role,
                message=detail or operation.value,
                violation_type='NO_ACTIVE_STAGE',
                deny_reason=f'当前未进入任何阶段，无法执行{operation.value}',
                exit_criteria_hint='请先进入S1需求接收阶段（enter_stage S1 orchestrator）',
                suggested_action='使用 StageStateManager.enter_stage("S1", "orchestrator", ...) 开始任务',
                log_level='ERROR',
                ctx=ctx,
            )

        if current_stage not in self._permissions:
            return BoundaryResult(
                allowed=False,
                operation=operation,
                current_stage=current_stage,
                current_role=current_role,
                violation_type='INVALID_STAGE',
                deny_reason=f'无效阶段: {current_stage}',
                log_level='ERROR',
                ctx=ctx,
            )

        perm = self._permissions[current_stage]

        if current_role not in VALID_ROLES:
            return BoundaryResult(
                allowed=False,
                operation=operation,
                current_stage=current_stage,
                current_role=current_role,
                violation_type='INVALID_ROLE',
                deny_reason=f'无效角色: {current_role}，有效角色为 {sorted(VALID_ROLES)}',
                log_level='ERROR',
                ctx=ctx,
            )

        allowed_roles = STAGE_ROLES.get(current_stage, set())
        if allowed_roles and current_role not in allowed_roles:
            return BoundaryResult(
                allowed=False,
                operation=operation,
                current_stage=current_stage,
                current_role=current_role,
                violation_type='ROLE_STAGE_MISMATCH',
                deny_reason=f'角色 {current_role} 无权在{current_stage}阶段执行操作，'
                            f'该阶段负责角色为 {sorted(allowed_roles)}',
                log_level='WARN',
                ctx={**ctx, 'allowed_roles': sorted(allowed_roles)},
            )

        if operation in perm.get('denied', set()):
            deny_reason = perm.get('deny_reason', {}).get(operation, '')
            target = self._find_owning_stage(operation)
            return BoundaryResult(
                allowed=False,
                operation=operation,
                current_stage=current_stage,
                current_role=current_role,
                message=detail,
                target_stage=target,
                violation_type='STAGE_BOUNDARY_VIOLATION',
                deny_reason=deny_reason or f'{operation.value}不属于{current_stage}阶段允许的操作',
                exit_criteria_hint=self._exit_criteria.get(current_stage, ''),
                log_level='WARN',
                ctx=ctx,
            )

        if operation in perm.get('allowed', set()):
            return BoundaryResult(
                allowed=True,
                operation=operation,
                current_stage=current_stage,
                current_role=current_role,
                message=detail or f'操作通过: {operation.value}',
                log_level='DEBUG',
                ctx=ctx,
            )

        if self._is_other_stage_allowed(operation, current_stage):
            target = self._find_owning_stage(operation)
            return BoundaryResult(
                allowed=False,
                operation=operation,
                current_stage=current_stage,
                current_role=current_role,
                message=detail,
                target_stage=target,
                violation_type='CROSS_STAGE_OPERATION',
                deny_reason=f'{operation.value}属于{target}（{STAGE_NAMES.get(target, "?")}）阶段职责',
                exit_criteria_hint=self._exit_criteria.get(current_stage, ''),
                suggested_action=self._suggest_for_cross_stage(operation, current_stage, target),
                log_level='WARN',
                ctx=ctx,
            )

        return BoundaryResult(
            allowed=True,
            operation=operation,
            current_stage=current_stage,
            current_role=current_role,
            message=detail or f'操作通过（未在显式禁止列表）: {operation.value}',
            log_level='DEBUG',
            ctx=ctx,
        )

    def _find_owning_stage(self, op: OperationType) -> Optional[str]:
        for stage_id, perm in self._permissions.items():
            if op in perm.get('allowed', set()) and op not in _UNIVERSAL_READ_OPS:
                return stage_id
        for stage_id, perm in self._permissions.items():
            if op in perm.get('denied', set()):
                continue
        for stage_id in sorted(STAGE_ORDER.keys(), key=lambda s: STAGE_ORDER[s]):
            perm = self._permissions.get(stage_id, {})
            if op in perm.get('allowed', set()):
                return stage_id
        return None

    def _is_other_stage_allowed(self, op: OperationType, current_stage: str) -> bool:
        for stage_id, perm in self._permissions.items():
            if stage_id == current_stage:
                continue
            if op in perm.get('allowed', set()) and op not in _UNIVERSAL_READ_OPS:
                return True
        return False

    def _suggest_for_cross_stage(self, op: OperationType,
                                  current_stage: str, target_stage: Optional[str]) -> str:
        if not target_stage:
            return '如需执行该操作，请先完成当前阶段或提交阶段跳转申请。'
        curr_order = STAGE_ORDER.get(current_stage, 0)
        target_order = STAGE_ORDER.get(target_stage, 0)
        if target_order > curr_order + 1:
            return f'如需跳至{target_stage}阶段，请提交正向跳过申请（request_jump skip {target_stage}）并经orchestrator批准。'
        if target_order < curr_order:
            return f'如需回退至{target_stage}阶段，请提交逆向回退申请（request_jump rollback {target_stage}）并经orchestrator+reviewer联合审批。'
        return f'请先完成当前阶段并退出后再进入{target_stage}阶段。'
