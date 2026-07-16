"""提示词萃取系统 —— 路径常量"""

from pathlib import Path

# ── 默认输出目录 ──────────────────────────────────────────────
DEFAULT_OUTPUT_DIR = "output"

# ── .agents/ 绑定路径 ─────────────────────────────────────────
# 提示词萃取系统与 .agents/ 规范体系的桥接：
# 提取和优化后的提示词模式可回写至对应角色目录
AGENTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / ".agents"

# 角色名 → 提示词目录映射
AGENTS_PROMPTS_DIR = AGENTS_DIR / "prompts"

AGENTS_ROLES_DIR = AGENTS_DIR / "roles"

# 角色列表（与 .agents/prompts/ 下子目录同步）
AGENTS_ROLES = ["orchestrator", "architect", "developer", "reviewer", "tester"]
