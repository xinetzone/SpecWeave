""".agents/scripts/ 智能体脚本共用常量

整合 check-gitignore、check-links、check-source-traceability、
check-spec-consistency、check-role-permissions、check-move、generate-nav
七个脚本中的重复硬编码定义，消除跨脚本重复，提供统一引用入口。
"""

# ============================================================================
# 通用排除目录（check-gitignore、check-links、check-source-traceability、check-move）
# ============================================================================
EXCLUDED_DIRS = {".git", "vendor", ".venv", "__pycache__", "node_modules", ".temp"}
NON_WORKTREE_PATH_PREFIXES = {
    ".meta/backup",
    ".backups",
    "external",
    "playground",
}

# ============================================================================
# .gitignore 必需规则（check-gitignore.py）
# ============================================================================
REQUIRED_RULES = [
    "vendor/",
    ".temp/",
    "__pycache__/",
    "*.pyc",
    ".venv/",
    "node_modules/",
    ".env",
    "*.log",
    ".DS_Store",
    "Thumbs.db",
]

# ============================================================================
# 临时依赖路径（check-gitignore.py）
# ============================================================================
TEMP_PATHS = [
    "vendor/",
    ".temp/",
    "__pycache__/",
    ".venv/",
    "node_modules/",
]

# ============================================================================
# check-links.py 默认参数
# ============================================================================
LINK_CHECK_TIMEOUT = 10          # 外部链接检查超时秒数
LINK_CHECK_WORKERS = 5           # 并发检查线程数
LINK_CHECK_EXCLUDE_DIRS = [
    "docs/templates",
    # 模板示例目录：含占位符链接（prev-chapter.md、next-chapter.md 等），
    # 这些链接是模板示例，非真实链接，不应校验。
    ".agents/templates/multi-product-wiki-template/example-wiki",
    ".trae/specs/knowledge-base-wiki-template/template",
]  # 默认排除目录
LINK_CHECK_USER_AGENT = "Mozilla/5.0 (compatible; LinkChecker/1.0)"

# ============================================================================
# 角色权限校验（check-role-permissions.py）
# ============================================================================
VALID_TIERS = {"co-founder", "standard"}
ROLE_EXCLUDED_FILES = {"README.md"}

# ============================================================================
# 规格一致性检查（check-spec-consistency.py）
# ============================================================================
PROJECT_ROOT_PREFIXES = [".agents/", "vendor/", ".trae/", "docs/"]

META_DOC_KEYWORDS = [
    "复盘", "回顾", "被复盘",
    "审计", "评审", "评估",
    "对比分析", "迁移方案",
    "retrospective", "audit", "review", "evaluation",
]

SPEC_MATCH_THRESHOLD = 1  # 语义匹配最少共同关键词数

# ============================================================================
# ANSI 颜色代码（check-spec-consistency.py）
# ============================================================================
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RED = "\033[91m"
ANSI_CYAN = "\033[96m"
ANSI_RESET = "\033[0m"

# ============================================================================
# 导航生成器（generate-nav.py / docgen.py nav）
# ============================================================================
ROOT_FILES = ["CONTRIBUTING.md"]

TARGETS = {
    "README.md": {
        "scan_dir": "docs/",
        "marker_start": "<!-- NAV_TABLE_START -->",
        "marker_end": "<!-- NAV_TABLE_END -->",
        "link_prefix": "docs/",
        "root_files_prefix": "",
        "root_files": ROOT_FILES,
    },
    "docs/README.md": {
        "scan_dir": "docs/",
        "marker_start": "<!-- NAV_TABLE_START -->",
        "marker_end": "<!-- NAV_TABLE_END -->",
        "link_prefix": "",
        "root_files_prefix": "../",
        "root_files": ROOT_FILES,
    },
    ".agents/docs/README.md": {
        "scan_dir": ".agents/docs/",
        "marker_start": "<!-- NAV_TABLE_START -->",
        "marker_end": "<!-- NAV_TABLE_END -->",
        "link_prefix": "",
        "root_files_prefix": "",
        "root_files": [],
    },
}

MANUAL_DESCRIPTIONS = {
    "project-overview.md": "项目定位、设计理念、核心特性",
    "project-structure.md": "完整目录树与职责说明",
    "tech-stack.md": "技术选型、环境依赖",
    "agent-roles.md": "5 个核心角色定义与绑定关系",
    "collaboration.md": "4 项协作协议、3 个标准工作流",
    "development-standards.md": "代码风格、提交规范、测试要求、文档边界",
    "verification-automation.md": "临时依赖治理、验证脚本",
    "knowledge-base.md": "技术知识库、复盘文档体系",
    "related-links.md": "外部标准、工具文档、项目仓库",
    "CONTRIBUTING.md": "贡献流程、分支命名、PR 规范",
}
