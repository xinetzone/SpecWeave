"""高风险操作拦截模板（Risk Interceptor）。

基于i-have-adhd项目V2分析的P0级改进：高风险不可逆操作必须遵循
"⚠️风险提示→回滚方案→确认请求→（确认后才给步骤）"四步拦截模板。

使用方式::

    from lib.risk_interceptor import (
        RiskLevel, RiskAssessment, assess_risk,
        format_intercept_template, is_confirmed,
    )

    assessment = assess_risk(user_message, command_list)
    if assessment.level >= RiskLevel.HIGH:
        print(format_intercept_template(assessment))
        # 等待用户确认
        if not is_confirmed(user_response):
            return  # 中止操作

日志控制::

    import logging
    logging.basicConfig(level=logging.DEBUG)  # 显示详细决策追踪
    # 或只启用风险拦截器的DEBUG日志
    logging.getLogger("risk_interceptor").setLevel(logging.DEBUG)
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import IntEnum

logger = logging.getLogger("risk_interceptor")


class RiskLevel(IntEnum):
    """风险等级枚举。数值越高风险越大。"""

    SAFE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


RISK_LEVEL_NAMES: dict[RiskLevel, str] = {
    RiskLevel.SAFE: "SAFE",
    RiskLevel.LOW: "LOW",
    RiskLevel.MEDIUM: "MEDIUM",
    RiskLevel.HIGH: "HIGH",
    RiskLevel.CRITICAL: "CRITICAL",
}


@dataclass
class RiskSignal:
    """检测到的单个风险信号。"""

    pattern: str
    description: str
    severity: RiskLevel
    category: str
    matched_text: str = ""


@dataclass
class RiskAssessment:
    """风险评估结果。"""

    level: RiskLevel = RiskLevel.SAFE
    signals: list[RiskSignal] = field(default_factory=list)
    user_message: str = ""
    detected_commands: list[str] = field(default_factory=list)
    suggested_rollback: str = ""
    impact_description: str = ""

    @property
    def requires_confirmation(self) -> bool:
        """HIGH及以上风险需要显式确认。"""
        return self.level >= RiskLevel.HIGH

    @property
    def highest_signal(self) -> RiskSignal | None:
        if not self.signals:
            return None
        return max(self.signals, key=lambda s: s.severity)


IRREVERSIBLE_OP_PATTERNS: list[tuple[str, str, RiskLevel, str]] = [
    (
        r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+|--recursive\s+)?(/|--no-preserve-root|\*|~)",
        "递归/根目录删除操作，可能删除系统关键文件",
        RiskLevel.CRITICAL,
        "filesystem",
    ),
    (
        r"\b(drop|delete|truncate)\s+(database|table|schema|collection)",
        "数据库删除/清空操作，数据将不可恢复",
        RiskLevel.CRITICAL,
        "database",
    ),
    (
        r"\b(format|mkfs)\b",
        "磁盘格式化操作，将清除分区所有数据",
        RiskLevel.CRITICAL,
        "filesystem",
    ),
    (
        r"\bgit\s+push\s+(-f|--force|--force-with-lease)",
        "Git强制推送，可能覆盖远程分支历史",
        RiskLevel.HIGH,
        "git",
    ),
    (
        r"\bgit\s+reset\s+--hard",
        "Git硬重置，未提交的修改将丢失",
        RiskLevel.HIGH,
        "git",
    ),
    (
        r"\bgit\s+clean\s+(-[a-zA-Z]*f[a-zA-Z]*|--force)",
        "Git强制清理未跟踪文件",
        RiskLevel.MEDIUM,
        "git",
    ),
    (
        r"\b(del|rmdir|rd|Remove-Item)\b.*(-Recurse|-r|--recursive)",
        "递归删除文件/目录（Windows/PowerShell）",
        RiskLevel.HIGH,
        "filesystem",
    ),
    (
        r"\b(chmod|chown)\s+(-R\s+)?777",
        "设置全局可读可写可执行权限（chmod 777），存在安全风险",
        RiskLevel.MEDIUM,
        "permissions",
    ),
    (
        r"\b(kubectl|docker)\s+(delete|rm)\b.*(--all|-a|--force)",
        "Kubernetes/Docker 批量删除资源",
        RiskLevel.HIGH,
        "container",
    ),
    (
        r"\bDROP\s+(USER|LOGIN|ROLE)\b",
        "删除数据库用户/角色",
        RiskLevel.HIGH,
        "database",
    ),
    (
        r"\b(ALTER|DROP)\s+(SYSTEM|DATABASE|TABLESPACE)\b",
        "数据库系统级修改/删除",
        RiskLevel.CRITICAL,
        "database",
    ),
    (
        r"\bnpm\s+(uninstall|rm)\s+(-g|--global)",
        "卸载全局npm包",
        RiskLevel.LOW,
        "package",
    ),
    (
        r"\bpip\s+uninstall\b",
        "卸载Python包",
        RiskLevel.LOW,
        "package",
    ),
    (
        r"\b(shutdown|reboot|init\s+[06]|poweroff)\b",
        "系统关机/重启操作",
        RiskLevel.HIGH,
        "system",
    ),
    (
        r"\b(dd)\b.*\bof=/dev/",
        "dd直接写入设备文件，可能覆盖磁盘数据",
        RiskLevel.CRITICAL,
        "filesystem",
    ),
    (
        r":(){ :|:& };:",
        "Fork炸弹，将耗尽系统资源导致系统无响应",
        RiskLevel.CRITICAL,
        "system",
    ),
    (
        r">\s*/dev/sd[a-z]",
        "重定向输出到磁盘设备，将覆盖分区数据",
        RiskLevel.CRITICAL,
        "filesystem",
    ),
    (
        r"\b(curl|wget)\b.*\|\s*(bash|sh|zsh|python)",
        "从网络下载脚本直接执行（管道执行），存在供应链风险",
        RiskLevel.HIGH,
        "security",
    ),
    (
        r"\beval\b.*\$",
        "eval执行变量内容，存在命令注入风险",
        RiskLevel.MEDIUM,
        "security",
    ),
    (
        r"\b(sudo|su)\s+(-\s*|root)",
        "以root权限执行命令",
        RiskLevel.MEDIUM,
        "permissions",
    ),
]

CONTEXT_KEYWORDS: list[tuple[str, str, RiskLevel]] = [
    (
        r"生产环境|prod(uction)?\s*env(ironment)?|线上|live\s*env",
        "操作涉及生产环境/线上环境，影响真实用户",
        RiskLevel.HIGH,
    ),
    (
        r"真实资金|real\s*money|支付|payment|转账|退款",
        "操作涉及真实资金流转",
        RiskLevel.CRITICAL,
    ),
    (
        r"法律|legal|合规|compliance",
        "操作涉及法律/合规风险",
        RiskLevel.HIGH,
    ),
    (
        r"不可恢复|不可撤销|irreversible|永久|permanent(ly)?\s*(delete|remove|destroy)",
        "操作被描述为不可恢复/不可逆",
        RiskLevel.HIGH,
    ),
    (
        r"所有用户|all\s*users|影响多人|影响所有人|massive\s*impact",
        "操作将影响大量用户",
        RiskLevel.HIGH,
    ),
    (
        r"清空|重置|reset\s*all|wipe|purge|clear\s*all",
        "清空/重置操作，可能丢失大量数据",
        RiskLevel.HIGH,
    ),
    (
        r"管理员权限|admin(\s*privilege)?|root\s*access|超级用户",
        "操作需要管理员/root权限且影响范围大",
        RiskLevel.MEDIUM,
    ),
]

CONFIRMATION_PATTERNS = [
    re.compile(r"^确[认定执行]*$", re.IGNORECASE),
    re.compile(r"^yes\s*$", re.IGNORECASE),
    re.compile(r"^y\s*$", re.IGNORECASE),
    re.compile(r"^confirm\s*$", re.IGNORECASE),
    re.compile(r"^继续\s*(执行)?$"),
    re.compile(r"^执行\s*吧?$"),
    re.compile(r"^好的?\s*(执行|继续)$"),
    re.compile(r"^我确认$"),
]

ROLLBACK_HINTS: dict[str, str] = {
    "git": "操作前先执行 git stash 或 git branch backup/<timestamp> 创建备份分支；git reset --hard 可用 git reflog 找回未提交内容（但不能保证完全恢复）",
    "database": "操作前必须先执行完整备份（如 pg_dump/mysqldump），备份文件保存至安全位置，确认备份可恢复后再执行操作",
    "filesystem": "操作前确认路径正确，重要文件先备份到独立位置；rm/rd 删除的文件无法通过回收站恢复",
    "container": "操作前先 kubectl/docker get 确认目标资源，建议使用 --dry-run=client 预览操作结果",
    "system": "系统关机/重启前确认所有工作已保存，通知可能受影响的用户",
    "permissions": "记录原始权限设置（stat/ls -la），操作后如有问题可恢复原权限",
    "security": "切勿直接执行来自网络的未经验证脚本；先下载到本地检查内容后再执行",
    "package": "记录被卸载的包名和版本，方便需要时重新安装",
}


def _compile_patterns() -> list[tuple[re.Pattern, str, RiskLevel, str]]:
    """编译正则表达式模式。"""
    return [
        (re.compile(pat, re.IGNORECASE), desc, level, cat)
        for pat, desc, level, cat in IRREVERSIBLE_OP_PATTERNS
    ]


def _compile_context_patterns() -> list[tuple[re.Pattern, str, RiskLevel]]:
    return [
        (re.compile(pat, re.IGNORECASE), desc, level)
        for pat, desc, level in CONTEXT_KEYWORDS
    ]


_COMPILED_OP_PATTERNS = _compile_patterns()
_COMPILED_CTX_PATTERNS = _compile_context_patterns()


def _extract_commands(text: str) -> list[str]:
    """从文本中提取看起来像命令的内容（代码块和反引号包裹内容）。"""
    commands = []
    code_block = re.compile(r"`{1,3}([^`]+)`{1,3}")
    for match in code_block.finditer(text):
        cmd = match.group(1).strip()
        if cmd and not cmd.startswith("#") and len(cmd) < 500:
            commands.append(cmd)
    return commands


def assess_risk(
    user_message: str,
    commands: list[str] | None = None,
    *,
    source: str = "<unknown>",
) -> RiskAssessment:
    """评估用户消息中包含的操作风险等级。

    Args:
        user_message: 用户的原始消息文本
        commands: 可选的命令列表（如果已解析），否则自动从消息中提取
        source: 来源标识（用于日志，如文件名/stdin/<command>）

    Returns:
        RiskAssessment 包含风险等级、检测到的信号和回滚建议
    """
    assessment = RiskAssessment(user_message=user_message)
    logger.debug("=" * 50)
    logger.debug("[%s] 开始风险评估，消息长度: %d 字符", source, len(user_message))

    if commands is None:
        commands = _extract_commands(user_message)
        logger.debug("[%s] 自动提取到 %d 个命令/代码片段: %s",
                      source, len(commands), commands if commands else "(无)")
    else:
        logger.debug("[%s] 使用传入的命令列表，共 %d 个", source, len(commands))
    assessment.detected_commands = commands

    scan_text = user_message + "\n" + "\n".join(commands)

    logger.debug("[%s] 开始扫描操作模式（共 %d 个危险模式）...",
                  source, len(_COMPILED_OP_PATTERNS))
    op_hit_count = 0
    for idx, (pattern, description, level, category) in enumerate(_COMPILED_OP_PATTERNS):
        matches = list(pattern.finditer(scan_text))
        if matches:
            op_hit_count += len(matches)
            for match in matches:
                matched = match.group(0)[:80]
                logger.debug(
                    "[%s] ✓ 模式#%d [%s/%s] 命中: 「%s」→ %s (等级=%s)",
                    source, idx, category, RISK_LEVEL_NAMES.get(level, str(level)),
                    matched, description, RISK_LEVEL_NAMES.get(level, str(level)),
                )
                assessment.signals.append(RiskSignal(
                    pattern=pattern.pattern,
                    description=description,
                    severity=level,
                    category=category,
                    matched_text=matched,
                ))
        else:
            logger.log(5, "[%s]   模式#%d [%s] 未命中", source, idx, category)

    logger.debug("[%s] 操作模式扫描完成: 命中 %d 个模式匹配", source, op_hit_count)

    logger.debug("[%s] 开始扫描上下文关键词（共 %d 个关键词）...",
                  source, len(_COMPILED_CTX_PATTERNS))
    ctx_hit_count = 0
    for idx, (pattern, description, level) in enumerate(_COMPILED_CTX_PATTERNS):
        matches = list(pattern.finditer(scan_text))
        if matches:
            ctx_hit_count += len(matches)
            for match in matches:
                matched = match.group(0)[:80]
                logger.debug(
                    "[%s] ✓ 上下文#%d [context/%s] 命中: 「%s」→ %s",
                    source, idx, RISK_LEVEL_NAMES.get(level, str(level)),
                    matched, description,
                )
                assessment.signals.append(RiskSignal(
                    pattern=pattern.pattern,
                    description=description,
                    severity=level,
                    category="context",
                    matched_text=matched,
                ))

    logger.debug("[%s] 上下文扫描完成: 命中 %d 个关键词", source, ctx_hit_count)

    total_signals = op_hit_count + ctx_hit_count
    if not assessment.signals:
        assessment.level = RiskLevel.SAFE
        logger.info("[%s] ✅ 未检测到任何风险信号，判定为 SAFE", source)
        return assessment

    logger.debug("[%s] 信号汇总: %d 个操作信号 + %d 个上下文信号 = %d 个总信号",
                  source, op_hit_count, ctx_hit_count, total_signals)
    for i, sig in enumerate(assessment.signals):
        logger.debug("  信号#%d: [%s/%s] 「%s」- %s",
                      i, sig.category, RISK_LEVEL_NAMES.get(sig.severity, str(sig.severity)),
                      sig.matched_text, sig.description)

    max_level = max(s.severity for s in assessment.signals)
    logger.debug("[%s] 初始最高风险等级: %s（来自单个信号最大值）",
                  source, RISK_LEVEL_NAMES.get(max_level, str(max_level)))

    high_count = sum(1 for s in assessment.signals if s.severity >= RiskLevel.HIGH)
    if high_count >= 2 and max_level == RiskLevel.HIGH:
        prev = max_level
        max_level = RiskLevel.CRITICAL
        logger.warning(
            "[%s] ⚠️  等级升级规则触发: 检测到 %d 个HIGH+信号（≥2个），"
            "等级从 %s 升级到 CRITICAL",
            source, high_count, RISK_LEVEL_NAMES.get(prev, str(prev)),
        )
    else:
        logger.debug("[%s] HIGH+信号数: %d，等级升级规则（≥2个HIGH→CRITICAL）未触发",
                      source, high_count)

    critical_cmd = any(
        s.severity >= RiskLevel.CRITICAL for s in assessment.signals
        if s.category != "context"
    )
    has_prod_context = any(
        "生产" in s.description or "prod" in s.description.lower()
        for s in assessment.signals
    )
    if critical_cmd and has_prod_context:
        if max_level < RiskLevel.CRITICAL:
            prev = max_level
            max_level = RiskLevel.CRITICAL
            logger.warning(
                "[%s] ⚠️  等级升级规则触发: CRITICAL命令 + 生产环境上下文双重命中，"
                "等级从 %s 升级到 CRITICAL",
                source, RISK_LEVEL_NAMES.get(prev, str(prev)),
            )
        else:
            logger.debug(
                "[%s] CRITICAL命令 + 生产环境上下文双重命中（等级已是CRITICAL，确认加固）",
                source,
            )
    else:
        logger.debug("[%s] CRITICAL命令=%s, 生产环境上下文=%s，"
                      "双重风险升级规则未触发",
                      source, critical_cmd, has_prod_context)

    assessment.level = max_level
    logger.info("[%s] 🎯 最终风险等级: %s（共 %d 个信号）",
                 source, RISK_LEVEL_NAMES.get(max_level, str(max_level)), total_signals)

    categories = {s.category for s in assessment.signals if s.category != "context"}
    if categories:
        cat_scores: dict[str, int] = {}
        for s in assessment.signals:
            if s.category == "context":
                continue
            cat_scores[s.category] = cat_scores.get(s.category, 0) + int(s.severity) ** 2
        primary_cat = max(cat_scores, key=cat_scores.get)
        assessment.suggested_rollback = ROLLBACK_HINTS.get(primary_cat, "")
        logger.debug("[%s] 风险类别权重: %s → 主要类别: %s，回滚方案已匹配",
                      source, cat_scores, primary_cat)
    else:
        assessment.suggested_rollback = "操作前请确保已备份相关数据，并确认可以安全回滚。"
        logger.debug("[%s] 仅上下文信号，使用通用回滚建议", source)

    impact_parts = []
    for sig in sorted(assessment.signals, key=lambda s: -s.severity):
        if sig.category == "context":
            impact_parts.append(sig.description)
    assessment.impact_description = "；".join(impact_parts[:3]) if impact_parts else ""
    if assessment.impact_description:
        logger.debug("[%s] 影响范围描述: %s", source, assessment.impact_description)

    logger.debug("[%s] 风险评估完成，requires_confirmation=%s",
                  source, assessment.requires_confirmation)
    return assessment


def format_intercept_template(assessment: RiskAssessment) -> str:
    """格式化高风险拦截输出模板。

    输出严格遵循四步模板：
    1. ⚠️ 风险提示
    2. 回滚方案
    3. 确认请求
    4. （确认后才给出具体操作步骤——此函数不输出步骤）

    Args:
        assessment: assess_risk() 返回的风险评估结果

    Returns:
        格式化的拦截消息文本，可直接输出给用户
    """
    if assessment.level < RiskLevel.HIGH:
        logger.debug("风险等级 %s < HIGH，跳过拦截模板生成",
                      RISK_LEVEL_NAMES.get(assessment.level, str(assessment.level)))
        return ""

    logger.debug("生成拦截模板: 等级=%s, 信号数=%d",
                  RISK_LEVEL_NAMES.get(assessment.level, str(assessment.level)),
                  len(assessment.signals))

    level_emoji = {
        RiskLevel.HIGH: "⚠️",
        RiskLevel.CRITICAL: "🚨",
    }
    emoji = level_emoji.get(assessment.level, "⚠️")

    lines: list[str] = []

    seen: set[tuple[str, str]] = set()
    risk_desc_parts = []
    for sig in sorted(assessment.signals, key=lambda s: -s.severity):
        key = (sig.description, sig.matched_text)
        if key in seen:
            continue
        seen.add(key)
        risk_desc_parts.append(f"- {sig.description}（检测到: `{sig.matched_text}`）")
        if len(risk_desc_parts) >= 5:
            break

    logger.debug("拦截模板去重后显示 %d/%d 个信号（最多5个）",
                  len(risk_desc_parts), len(assessment.signals))

    lines.append(f"{emoji} 重要风险提示：你要求的操作存在较高风险，请仔细阅读以下内容：")
    lines.append("")
    for part in risk_desc_parts:
        lines.append(part)
    lines.append("")

    if assessment.impact_description:
        lines.append(f"**影响范围**：{assessment.impact_description}")
        lines.append("")

    lines.append("**回滚方案**：")
    lines.append(assessment.suggested_rollback)
    lines.append("")

    if assessment.level >= RiskLevel.CRITICAL:
        lines.append("🚨 **此操作等级为 CRITICAL（严重），不可撤销！**")
        lines.append("")

    lines.append("请确认你已了解上述风险并完成必要的备份。确认执行请回复「确认」；")
    lines.append("如需更多信息或想取消操作，请直接告诉我。")

    logger.debug("拦截模板生成完成，共 %d 行", len(lines))
    return "\n".join(lines)


def is_confirmed(response: str) -> bool:
    """判断用户回复是否表示确认执行。

    Args:
        response: 用户的回复文本

    Returns:
        True 表示确认，False 表示未确认
    """
    if not response:
        logger.debug("用户回复为空，判定为未确认")
        return False
    text = response.strip().lower()
    logger.debug("判断用户确认: 回复文本「%s」（长度=%d）", text[:50], len(text))
    for pat in CONFIRMATION_PATTERNS:
        if pat.search(text):
            logger.debug("  ✓ 匹配确认模式: %s → 判定为确认", pat.pattern)
            return True
    logger.debug("  ✗ 未匹配任何确认模式 → 判定为未确认")
    return False


def should_block_command(command: str, *, source: str = "<cli>") -> RiskAssessment:
    """快速检查单个命令是否需要拦截（CLI/脚本场景使用）。

    Args:
        command: 要检查的命令字符串
        source: 来源标识（用于日志）

    Returns:
        RiskAssessment，如果需要确认则 level >= HIGH
    """
    logger.debug("[%s] 快速检查单个命令: %s", source, command[:80])
    return assess_risk(command, commands=[command], source=source)


__all__ = [
    "RiskLevel",
    "RiskSignal",
    "RiskAssessment",
    "RISK_LEVEL_NAMES",
    "assess_risk",
    "format_intercept_template",
    "is_confirmed",
    "should_block_command",
]
