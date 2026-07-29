# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

from .models import SkillReport


def calculate_score(report: SkillReport) -> int:
    score = 100

    for r in report.results:
        if r.passed:
            continue
        if r.severity == "error":
            score -= 15
        elif r.severity == "warn":
            score -= 5
        elif r.severity == "info":
            score -= 1

    return max(0, min(100, score))

