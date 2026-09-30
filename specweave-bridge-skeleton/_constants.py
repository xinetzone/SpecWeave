"""SpecWeave Bridge 插件常量定义。"""

PLUGIN_NAME = "specweave-bridge"
PLUGIN_VERSION = "0.2.0"
SPECWEAVE_SIGNATURE_KEYWORD = "启动协议"
AGENTS_MD_FILENAME = "AGENTS.md"
SUBREGIONS = ("apps", "projects", "vendor")
SKILLS_DIR_NAME = "skills"
SCRIPTS_DIR_NAME = "scripts"
AGENTS_DIR_NAME = ".agents"

# 工作区识别信号名（detector.detect_workspace_signal 返回值）
SIGNAL_AGENTS_MD = "agents_md"    # 主信号：AGENTS.md 存在且含「启动协议」关键词
SIGNAL_AGENTS_DIR = "agents_dir"  # 兼容信号：.agents/ 存在且含特征子目录

# 兼容信号特征子目录（须全部存在才视为 SpecWeave 兼容工作区）。
# 参照 .agents/protocols/workspace-discovery.md 五步发现流程步骤 3，但刻意更严格：
# 仅 roles/ 或仅 skills/ 不判定——排除通用技能管理器目录（如仅含 skills/ 的
# ~/.agents/），避免用户主目录被误判为兼容工作区、污染所有非 SpecWeave 会话。
AGENTS_DIR_REQUIRED_SUBDIRS = ("roles", "skills")

ROUTES = {
    "skill创建": ".agents/skills/README.md",
    "skill调试": ".agents/skills/README.md",
    "内容敏感度预检": ".agents/rules/content-sensitivity-precheck.md",
    "角色定义": ".agents/roles/README.md",
    "复盘": ".agents/commands/retrospective-cmd.md",
    "洞察": ".agents/commands/insight-cmd.md",
    "七概念": ".agents/commands/seven-concepts-cmd.md",
    "CI检查": ".agents/skills/ci-check-cmd.md",
    "链接检查": ".agents/skills/link-check-cmd.md",
    "原子化": ".agents/commands/atomization-cmd.md",
    "原子提交": ".agents/commands/atomic-commit-cmd.md",
    "Mermaid": ".agents/commands/mermaid-cmd.md",
    "知识沉淀": ".agents/commands/extraction-cmd.md",
    "文档生成": ".agents/skills/docgen-cmd.md",
    "重复代码检测": ".agents/skills/check-duplication-cmd.md",
    "vendor协同": ".agents/VENDOR-INTEGRATION.md",
    "硬编码治理": ".agents/rules/hardcode-governance.md",
    "数据安全": ".agents/rules/data-security.md",
    "阶段守卫": ".agents/rules/stage-guard.md",
    "功能开发": ".agents/workflows/feature-development.md",
    "代码审查": ".agents/workflows/code-review.md",
    "测试流程": ".agents/workflows/testing.md",
    "上下文路由": ".agents/context-routing.md",
    "全局核心规则": ".agents/global-core-rules.md",
    "能力注册中心": ".agents/capability-registry.md",
    "工作区发现": ".agents/protocols/workspace-discovery.md",
    "提示词自举": ".agents/protocols/prompt-bootstrap.md",
    "导出报告": ".agents/commands/export-report-cmd.md",
    "Token优化": ".agents/commands/token-optimize-cmd.md",
    "应用生命周期": ".agents/protocols/app-lifecycle.md",
}
