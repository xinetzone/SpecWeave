# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

from typing import Any, TypeAlias

type ConvertResult = dict[str, Any]
type BatchResult = dict[str, Any]
type VerificationResult = dict[str, Any]
type RollbackResult = dict[str, Any]
type Report = dict[str, Any]

