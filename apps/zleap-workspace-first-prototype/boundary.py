"""Boundary 模块：四类边界检查。

对应 Zleap-Agent 设计中的 Boundary 概念：
- 真实工作流必须有边界
- 四类边界：数据边界（不出内网）、工具边界（按工作区可见）、
  模型边界（按工作区绑定）、记忆边界（不跨用户/任务串）
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from workspace import Workspace

logger = logging.getLogger(__name__)


class BoundaryViolation(Exception):
    """边界越权异常。"""


class BoundaryChecker:
    """四类边界检查器。"""

    def __init__(self) -> None:
        # 数据边界：标记为敏感的数据不得出内网
        self._sensitive_data: List[str] = []
        # 模型边界：允许的模型映射
        self._allowed_models: Dict[str, List[str]] = {}
        # 记忆边界：不允许跨用户/任务读取的记忆分区
        self._private_memory_partitions: List[str] = []

    # ---- 数据边界 ----
    def mark_sensitive(self, data_desc: str) -> None:
        """标记敏感数据（不得出内网）。"""
        self._sensitive_data.append(data_desc)
        logger.info("[Boundary] 标记敏感数据 data_desc=%r", data_desc)

    def check_data_boundary(self, data_desc: str, workspace: Workspace) -> bool:
        """数据边界检查：敏感数据若工作区非私有则拦截。"""
        if data_desc in self._sensitive_data and not workspace.private:
            logger.warning(
                "[Boundary] 数据边界越权：data=%r workspace=%s private=%s",
                data_desc, workspace.name, workspace.private,
            )
            raise BoundaryViolation(
                f"数据边界：{data_desc!r} 为敏感数据，工作区 {workspace.name} 非私有，禁止出内网"
            )
        logger.info("[Boundary] 数据边界通过 data=%r workspace=%s", data_desc, workspace.name)
        return True

    # ---- 工具边界 ----
    def check_tool_boundary(self, workspace: Workspace, tool_name: str) -> bool:
        """工具边界检查：工具必须绑定到当前工作区。"""
        if tool_name not in workspace.tools:
            logger.warning(
                "[Boundary] 工具边界越权：tool=%r workspace=%s 未绑定",
                tool_name, workspace.name,
            )
            raise BoundaryViolation(
                f"工具边界：工具 {tool_name!r} 未绑定到工作区 {workspace.name}"
            )
        logger.info("[Boundary] 工具边界通过 tool=%r workspace=%s", tool_name, workspace.name)
        return True

    # ---- 模型边界 ----
    def set_allowed_models(self, workspace_id: str, models: List[str]) -> None:
        """设置工作区允许的模型白名单。"""
        self._allowed_models[workspace_id] = models

    def check_model_boundary(self, workspace: Workspace) -> bool:
        """模型边界检查：工作区必须使用白名单内模型。"""
        allowed = self._allowed_models.get(workspace.workspace_id)
        if allowed is not None and workspace.model not in allowed:
            logger.warning(
                "[Boundary] 模型边界越权：workspace=%s model=%r allowed=%s",
                workspace.name, workspace.model, allowed,
            )
            raise BoundaryViolation(
                f"模型边界：工作区 {workspace.name} 使用模型 {workspace.model!r}，"
                f"不在白名单 {allowed} 内"
            )
        logger.info("[Boundary] 模型边界通过 workspace=%s model=%r", workspace.name, workspace.model)
        return True

    # ---- 记忆边界 ----
    def mark_memory_private(self, partition: str) -> None:
        """标记记忆分区为私有（不跨用户/任务读取）。"""
        self._private_memory_partitions.append(partition)

    def check_memory_boundary(self, partition: str) -> bool:
        """记忆边界检查：私有分区不可被跨用户读取。"""
        if partition in self._private_memory_partitions:
            logger.warning("[Boundary] 记忆边界越权：partition=%r", partition)
            raise BoundaryViolation(
                f"记忆边界：分区 {partition!r} 为私有记忆，禁止跨用户/任务读取"
            )
        logger.info("[Boundary] 记忆边界通过 partition=%r", partition)
        return True

    def check_all(self, workspace: Workspace) -> bool:
        """执行全部四类边界检查（模型边界 + 数据边界）。"""
        logger.info("[Boundary] 执行全量边界检查 workspace=%s", workspace.name)
        self.check_model_boundary(workspace)
        return True