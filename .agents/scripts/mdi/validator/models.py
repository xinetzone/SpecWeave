"""MDI验证器数据模型。

包含ValidationIssue和ValidationReport数据结构。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .constants import ERROR_SCORE_PENALTY, WARN_SCORE_PENALTY, INFO_SCORE_PENALTY


@dataclass
class ValidationIssue:
    """单个验证问题。"""

    severity: str
    code: str
    message: str
    line: int | None
    file: str
    suggestion: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "line": self.line,
            "file": self.file,
        }
        if self.suggestion:
            result["suggestion"] = self.suggestion
        return result


@dataclass
class ValidationReport:
    """MDI文档验证报告。"""

    file: str
    issues: list[ValidationIssue] = field(default_factory=list)
    score: int = 100
    profile_type: str = ""

    def passed(self) -> bool:
        """是否通过验证（无error级别问题）。"""
        return all(i.severity != "error" for i in self.issues)

    def errors(self) -> list[ValidationIssue]:
        """返回所有error级别问题。"""
        return [i for i in self.issues if i.severity == "error"]

    def warnings(self) -> list[ValidationIssue]:
        """返回所有warn级别问题。"""
        return [i for i in self.issues if i.severity == "warn"]

    def infos(self) -> list[ValidationIssue]:
        """返回所有info级别问题。"""
        return [i for i in self.issues if i.severity == "info"]

    def calculate_score(self) -> int:
        """计算质量评分（0-100）。"""
        score = 100
        for issue in self.issues:
            if issue.severity == "error":
                score -= ERROR_SCORE_PENALTY
            elif issue.severity == "warn":
                score -= WARN_SCORE_PENALTY
            elif issue.severity == "info":
                score -= INFO_SCORE_PENALTY
        self.score = max(0, min(100, score))
        return self.score

    def add_issue(
        self,
        severity: str,
        code: str,
        message: str,
        line: int | None = None,
        suggestion: str | None = None,
    ) -> None:
        """添加一个验证问题。"""
        self.issues.append(ValidationIssue(
            severity=severity,
            code=code,
            message=message,
            line=line,
            file=self.file,
            suggestion=suggestion,
        ))

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "profile": self.profile_type,
            "score": self.score,
            "passed": self.passed(),
            "errorCount": len(self.errors()),
            "warnCount": len(self.warnings()),
            "infoCount": len(self.infos()),
            "issues": [i.to_dict() for i in self.issues],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
