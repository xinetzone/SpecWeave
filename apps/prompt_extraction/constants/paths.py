"""提示词萃取系统 —— 路径常量"""

from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent.parent

# ── 默认输出目录 ──────────────────────────────────────────────
# 输出目录固定在包目录下，避免依赖运行时 CWD
DEFAULT_OUTPUT_DIR = str(_PACKAGE_DIR / "output")

# ── .agents/ 绑定路径 ─────────────────────────────────────────
# 提示词萃取系统与 .agents/ 规范体系的桥接：
# 提取和优化后的提示词模式可回写至对应角色目录
# 从 apps/prompt_extraction/constants/paths.py → 项目根目录/.agents
AGENTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / ".agents"

# 角色名 → 提示词目录映射
AGENTS_PROMPTS_DIR = AGENTS_DIR / "prompts"

AGENTS_ROLES_DIR = AGENTS_DIR / "roles"

# 角色列表（与 .agents/prompts/ 下子目录同步）
AGENTS_ROLES = ["orchestrator", "architect", "developer", "reviewer", "tester"]
