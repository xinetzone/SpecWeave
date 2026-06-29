#!/usr/bin/env python3
"""阶段守卫运行时模块。

提供阶段守卫运行时强制执行层的核心组件：
- state: StageStateManager 阶段状态管理器
- boundary: BoundaryChecker 操作边界校验引擎
- interceptor: InterceptorFormatter 拦截输出格式化器 + BypassDetector 绕过检测
- runtime: GuardrailRuntime 运行时集成门面（串联三组件的一站式入口）
- 后续模块：approval（审批流）、logger（运行时日志）

相关规范：
    阶段守卫规则: .agents/rules/stage-guardrails.md
    PDR协议: .agents/protocols/pre-document-reading.md
    离线检查工具: .agents/scripts/check-stage-guardrails.py
"""

from lib.stage_guardrails.state import (
    StageStateManager,
    StageStatus,
    StageTransition,
    JumpRecord,
    STAGE_ORDER,
    STAGE_NAMES,
    VALID_ROLES,
    STAGE_ROLES,
    TransitionError,
    InvalidStageError,
    InvalidRoleError,
    DuplicateEntryError,
    ExitWithoutEntryError,
    StageMismatchError,
    UnauthorizedJumpError,
    InvalidJumpError,
)

from lib.stage_guardrails.boundary import (
    BoundaryChecker,
    BoundaryResult,
    OperationType,
    STAGE_EXIT_CRITERIA,
    OPERATION_CATEGORIES,
)

from lib.stage_guardrails.interceptor import (
    InterceptorFormatter,
    BypassDetector,
    FormattedOutput,
)

from lib.stage_guardrails.runtime import (
    GuardrailRuntime,
    RuntimeStatus,
)

__all__ = [
    'StageStateManager',
    'StageStatus',
    'StageTransition',
    'JumpRecord',
    'STAGE_ORDER',
    'STAGE_NAMES',
    'VALID_ROLES',
    'STAGE_ROLES',
    'TransitionError',
    'InvalidStageError',
    'InvalidRoleError',
    'DuplicateEntryError',
    'ExitWithoutEntryError',
    'StageMismatchError',
    'UnauthorizedJumpError',
    'InvalidJumpError',
    'BoundaryChecker',
    'BoundaryResult',
    'OperationType',
    'STAGE_EXIT_CRITERIA',
    'OPERATION_CATEGORIES',
    'InterceptorFormatter',
    'BypassDetector',
    'FormattedOutput',
    'GuardrailRuntime',
    'RuntimeStatus',
]
