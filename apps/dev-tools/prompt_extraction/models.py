"""提示词萃取系统数据模型"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FeatureSet:
    """特征集：从提示词中提取的结构化特征"""
    instructions: list[str] = field(default_factory=list)
    constraints: list[dict] = field(default_factory=list)
    expected_output: str | None = None
    output_type: str | None = None  # JSON/文本/列表/代码


@dataclass
class QualityScore:
    """质量评分"""
    clarity: float = 0.0       # 清晰度 0-100
    completeness: float = 0.0  # 完整性 0-100
    executability: float = 0.0 # 可执行性 0-100
    overall: float = 0.0       # 综合评分
    grade: str = "差"          # 等级：优/良/中/差
    suggestions: list[str] = field(default_factory=list)


@dataclass
class OptimizationResult:
    """优化结果"""
    triggered: bool = False
    optimized_text: str = ""
    improvements: list[str] = field(default_factory=list)
    diff: str = ""


@dataclass
class PromptRecord:
    """提示词记录：贯穿流水线的核心数据结构"""
    id: str = ""
    original_text: str = ""
    cleaned_text: str = ""
    markdown_structure: dict | None = None
    features: FeatureSet = field(default_factory=FeatureSet)
    quality: QualityScore = field(default_factory=QualityScore)
    optimization: OptimizationResult = field(default_factory=OptimizationResult)
    error: str | None = None