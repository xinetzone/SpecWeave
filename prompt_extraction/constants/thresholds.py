"""提示词萃取系统 —— 阈值与评分常量"""

# ── 质量评估阈值 ──────────────────────────────────────────────
QUALITY_THRESHOLD = 60         # 触发优化阈值（0-100）

CLARITY_WEIGHT = 0.30          # 清晰度权重
COMPLETENESS_WEIGHT = 0.40     # 完整性权重
EXECUTABILITY_WEIGHT = 0.30    # 可执行性权重

# ── 等级映射 ──────────────────────────────────────────────────
GRADE_THRESHOLDS = {
    "优": 85,
    "良": 70,
    "中": 50,
    "差": 0,
}

# ── 文本长度评估 ──────────────────────────────────────────────
TEXT_TOO_SHORT_LENGTH = 20     # 过短阈值（字符数）
TEXT_TOO_LONG_LENGTH = 500     # 过长阈值（字符数）
SCORE_DEDUCTION_TOO_SHORT = 40 # 过短扣分
SCORE_DEDUCTION_TOO_LONG = 10  # 过长扣分

# ── 结构层次评估 ──────────────────────────────────────────────
SCORE_DEDUCTION_PER_MISSING_STRUCTURE = 10  # 缺少结构元素扣分

# ── 歧义度评估 ────────────────────────────────────────────────
SCORE_DEDUCTION_PER_AMBIGUOUS = 5  # 每个模糊词汇扣分
SCORE_DEDUCTION_AMBIGUOUS_MAX = 30 # 歧义扣分上限

# ── 完整性要素分值 ────────────────────────────────────────────
SCORE_INSTRUCTION = 20    # 指令要素分值
SCORE_CONSTRAINT = 20     # 约束要素分值
SCORE_CONTEXT = 20        # 上下文要素分值
SCORE_EXAMPLE = 20        # 示例要素分值
SCORE_OUTPUT_FORMAT = 20  # 输出格式要素分值

# ── 上下文检测 ────────────────────────────────────────────────
CONTEXT_LENGTH_THRESHOLD = 50  # 上下文长度阈值（字符数）

# ── 可执行性评估 ──────────────────────────────────────────────
VERB_SCORE_PER = 5               # 每个动作动词加分
VERB_SCORE_MAX = 33              # 动词评分上限
CONSTRAINT_VERIFIABLE_SCORE_MAX = 33  # 约束可验证评分上限
OUTPUT_DETERMINABLE_SCORE = 34   # 输出可判定分值
OUTPUT_TYPE_PARTIAL_SCORE = 17   # 输出类型部分分值

# ── 通用常量 ──────────────────────────────────────────────────
ID_HEX_LENGTH = 12               # 唯一标识十六进制长度
TEXT_TRUNCATE_LENGTH = 80        # 文本摘要截断长度
DESC_TRUNCATE_LENGTH = 60        # 描述截断长度
