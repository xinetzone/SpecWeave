"""阶段状态管理器异常类定义。"""

from __future__ import annotations

from typing import Optional


class TransitionError(Exception):
    """阶段转换异常基类。"""
    def __init__(self, code: str, message: str, details: Optional[dict] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class InvalidStageError(TransitionError):
    """无效阶段ID。"""
    pass


class InvalidRoleError(TransitionError):
    """角色无权操作当前阶段。"""
    pass


class DuplicateEntryError(TransitionError):
    """重复进入同一阶段而未退出。"""
    pass


class ExitWithoutEntryError(TransitionError):
    """未进入阶段就尝试退出。"""
    pass


class StageMismatchError(TransitionError):
    """退出的阶段与当前活跃阶段不一致。"""
    pass


class UnauthorizedJumpError(TransitionError):
    """未经审批的阶段跳转。"""
    pass


class InvalidJumpError(TransitionError):
    """非法跳转（如跳至完成确认之前跳过验证）。"""
    pass
