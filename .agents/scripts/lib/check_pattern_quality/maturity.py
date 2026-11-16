# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

"""模式成熟度等级归一（模板口径统一 A1）。

库索引的等级阶梯为 L1-draft → L1.5 → L2-validated → L3-mature → L4-optimized；
历史文档存在 24 种写法（L1-实验性 / L1 实验性 / L1-experimental / L2 已验证 /
L2（双案例验证） / L3 方法论（已完成闭环验证） 等）。统一在读取时归一为
基础等级，供成熟度一致性检查使用，避免每种写法各判各的。

为什么不直接把非法写法判 error：
    「统一口径」的目标是让新模板文档按等级表标注即可通过，而不是制造新债务。
    无等级前缀的描述性词（draft / stable / validated / established）只作告警，
    提示改用规范形态；真正缺失成熟度由 frontmatter 必填项检查负责。
"""

import re
from dataclasses import dataclass

# 等级前缀：L1 / L1.5 / L2 及其后的中文、全角括号、连字符后缀一律忽略
LEVEL_PREFIX_PATTERN = re.compile(r"^\s*L\s*([1-4])(\s*[.．]\s*5)?", re.IGNORECASE)

# 历史描述性词（无等级前缀）：可识别但不视为合规形态
DESCRIPTIVE_WORDS = {"draft", "stable", "validated", "established"}

CANONICAL_LEVELS = ("L1-draft", "L1.5", "L2-validated", "L3-mature", "L4-optimized")


@dataclass(frozen=True)
class MaturityResult:
    """成熟度归一结果。

    base:   归一后的基础等级（L1 / L1.5 / L2 / L3 / L4），无法识别时为 None
    status: level（等级前缀）/ alias（历史描述性词）/ unknown / empty
    """

    raw: str
    base: str | None
    status: str


def normalize_maturity(value) -> MaturityResult:
    """把任意成熟度写法归一为基础等级。"""
    if value is None or not str(value).strip():
        return MaturityResult("", None, "empty")

    raw = str(value).strip()
    matched = LEVEL_PREFIX_PATTERN.match(raw)
    if matched:
        major = matched.group(1)
        base = f"L{major}.5" if matched.group(2) else f"L{major}"
        return MaturityResult(raw, base, "level")

    if raw.lower() in DESCRIPTIVE_WORDS:
        return MaturityResult(raw, None, "alias")

    return MaturityResult(raw, None, "unknown")
