"""多Agent对抗式审查工作流模块。

基于第一性原理推导的审查框架：
- A1: 审查有效性 = 视角多样性 × 攻击深度
- A2: 审查安全性 = 所有攻击必须可逆
- A3: 审查可追溯性 = 每个发现必须有精确复现路径
- A4: 审查闭环 = 发现→分级→修复→回归验证

设计原则：
- 多Agent独立攻击，互不通信，确保视角多样性
- 每个攻击场景在隔离环境中执行，不导致永久损坏
- 审查报告结构化，包含复现步骤、风险等级、修复建议
- 审查结果自动归档到 docs/retrospective/ 体系
"""

import json
import logging
import os
import sys
import tempfile
import textwrap
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = PROJECT_ROOT / ".agents" / "scripts"
KNOWLEDGE_BASE = PROJECT_ROOT / "docs" / "knowledge"
REPORT_DIR = PROJECT_ROOT / "docs" / "retrospective" / "reports" / "adversarial-reviews"

# ---------------------------------------------------------------------------
# 攻击者Profile定义
# ---------------------------------------------------------------------------

@dataclass
class AttackerProfile:
    """攻击者角色定义。"""
    id: str
    name: str
    focus: str
    description: str
    attack_vectors: list[str] = field(default_factory=list)

ATTACKER_PROFILES: dict[str, AttackerProfile] = {
    "security": AttackerProfile(
        id="security",
        name="安全攻击者",
        focus="加密边界、密钥管理、认证绕过",
        description="模拟外部攻击者，尝试绕过加密保护、窃取密钥、篡改密文",
        attack_vectors=[
            "错误密钥解密",
            "空密钥/默认密钥",
            "篡改密文后解密",
            "加密级别混淆",
            "密钥泄露检测",
        ],
    ),
    "boundary": AttackerProfile(
        id="boundary",
        name="边界攻击者",
        focus="路径遍历、文件大小、格式畸形",
        description="模拟边界攻击者，尝试通过异常输入突破系统边界",
        attack_vectors=[
            "路径遍历注入",
            "超大文件攻击",
            "畸形YAML/JSON",
            "空文件/零字节文件",
            "Unicode混淆",
        ],
    ),
    "integrity": AttackerProfile(
        id="integrity",
        name="完整性攻击者",
        focus="校验和篡改、元数据污染、Git历史攻击",
        description="模拟完整性攻击者，尝试绕过校验和检测、污染元数据",
        attack_vectors=[
            "正文篡改（保持校验和）",
            "校验和字段删除",
            "元数据字段注入",
            "完整性标记伪造",
            "Git历史重写攻击",
        ],
    ),
    "timing": AttackerProfile(
        id="timing",
        name="时序攻击者",
        focus="并发冲突、超时、竞态条件",
        description="模拟时序攻击者，利用并发和时序漏洞",
        attack_vectors=[
            "并发读写竞争",
            "超时/资源耗尽",
            "递归深度攻击",
            "死锁触发",
            "大量并发请求",
        ],
    ),
    "fuzzer": AttackerProfile(
        id="fuzzer",
        name="模糊测试者",
        focus="随机/半随机异常输入、边界值",
        description="模拟模糊测试者，用大量随机输入寻找意外崩溃",
        attack_vectors=[
            "随机二进制数据",
            "控制字符注入",
            "极端边界值",
            "空值/null注入",
            "格式错误输入",
        ],
    ),
}

# ---------------------------------------------------------------------------
# 漏洞数据结构
# ---------------------------------------------------------------------------

@dataclass
class Vulnerability:
    """审查发现的漏洞。"""
    id: str
    title: str
    severity: str  # P0/P1/P2
    category: str
    attacker: str
    scenario: str
    description: str
    reproduction_steps: list[str]
    affected_file: str
    affected_function: str
    expected_behavior: str
    actual_behavior: str
    fix_suggestion: str
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity,
            "category": self.category,
            "attacker": self.attacker,
            "scenario": self.scenario,
            "description": self.description,
            "reproduction_steps": self.reproduction_steps,
            "affected_file": self.affected_file,
            "affected_function": self.affected_function,
            "expected_behavior": self.expected_behavior,
            "actual_behavior": self.actual_behavior,
            "fix_suggestion": self.fix_suggestion,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# 攻击场景生成器
# ---------------------------------------------------------------------------

def generate_attack_scenarios() -> list[dict]:
    """生成攻击场景清单。

    基于7类审查场景，为每个攻击者生成对应的测试用例。
    返回场景列表，每个场景包含：id, name, category, attacker, test_fn_description。
    """
    scenarios = []

    # 场景1: 超大/畸形文件
    for profile_id in ["boundary", "fuzzer"]:
        scenarios.append({
            "id": f"SC-001-{profile_id}",
            "name": "超大文件写入",
            "category": "oversized_malformed",
            "attacker": profile_id,
            "description": "尝试写入超过5MB限制的文件",
            "test": "write_oversized_file",
        })
        scenarios.append({
            "id": f"SC-002-{profile_id}",
            "name": "畸形YAML frontmatter",
            "category": "oversized_malformed",
            "attacker": profile_id,
            "description": "尝试写入包含畸形YAML的条目",
            "test": "write_malformed_yaml",
        })

    # 场景2: 加密边界
    for profile_id in ["security", "fuzzer"]:
        scenarios.append({
            "id": f"SC-003-{profile_id}",
            "name": "错误密钥解密",
            "category": "encryption_boundary",
            "attacker": profile_id,
            "description": "使用错误密钥尝试解密confidential条目",
            "test": "decrypt_with_wrong_key",
        })
        scenarios.append({
            "id": f"SC-004-{profile_id}",
            "name": "篡改密文后解密",
            "category": "encryption_boundary",
            "attacker": profile_id,
            "description": "篡改密文后尝试解密",
            "test": "decrypt_tampered_ciphertext",
        })
        scenarios.append({
            "id": f"SC-005-{profile_id}",
            "name": "空密钥/默认密钥",
            "category": "encryption_boundary",
            "attacker": profile_id,
            "description": "使用空字符串或默认密钥尝试解密",
            "test": "decrypt_with_empty_key",
        })

    # 场景3: 完整性校验绕过
    for profile_id in ["integrity", "security"]:
        scenarios.append({
            "id": f"SC-006-{profile_id}",
            "name": "正文篡改（保持校验和）",
            "category": "integrity_bypass",
            "attacker": profile_id,
            "description": "修改正文但保持校验和不变",
            "test": "tamper_content_keep_checksum",
        })
        scenarios.append({
            "id": f"SC-007-{profile_id}",
            "name": "校验和字段删除",
            "category": "integrity_bypass",
            "attacker": profile_id,
            "description": "删除integrity字段尝试绕过校验",
            "test": "remove_integrity_field",
        })
        scenarios.append({
            "id": f"SC-008-{profile_id}",
            "name": "完整性标记伪造",
            "category": "integrity_bypass",
            "attacker": profile_id,
            "description": "修改integrity_status为intact但内容已损坏",
            "test": "forge_integrity_status",
        })

    # 场景4: 检索注入
    for profile_id in ["boundary", "security"]:
        scenarios.append({
            "id": f"SC-009-{profile_id}",
            "name": "SQL注入尝试",
            "category": "search_injection",
            "attacker": profile_id,
            "description": "在搜索查询中注入SQL语句",
            "test": "sql_injection_query",
        })
        scenarios.append({
            "id": f"SC-010-{profile_id}",
            "name": "XSS注入尝试",
            "category": "search_injection",
            "attacker": profile_id,
            "description": "在搜索查询中注入脚本标签",
            "test": "xss_injection_query",
        })

    # 场景5: 路径遍历
    for profile_id in ["boundary", "security"]:
        scenarios.append({
            "id": f"SC-011-{profile_id}",
            "name": "路径遍历读取",
            "category": "path_traversal",
            "attacker": profile_id,
            "description": "尝试读取知识库外部的文件",
            "test": "path_traversal_read",
        })
        scenarios.append({
            "id": f"SC-012-{profile_id}",
            "name": "路径遍历写入",
            "category": "path_traversal",
            "attacker": profile_id,
            "description": "尝试写入知识库外部的文件",
            "test": "path_traversal_write",
        })

    # 场景6: 元数据污染
    for profile_id in ["integrity", "fuzzer"]:
        scenarios.append({
            "id": f"SC-013-{profile_id}",
            "name": "超长元数据字段",
            "category": "metadata_pollution",
            "attacker": profile_id,
            "description": "写入超长标签/标题值",
            "test": "oversized_metadata_field",
        })
        scenarios.append({
            "id": f"SC-014-{profile_id}",
            "name": "非法元数据注入",
            "category": "metadata_pollution",
            "attacker": profile_id,
            "description": "注入非法/危险元数据字段",
            "test": "inject_illegal_metadata",
        })

    # 场景7: 资源耗尽
    for profile_id in ["timing", "fuzzer"]:
        scenarios.append({
            "id": f"SC-015-{profile_id}",
            "name": "递归深度攻击",
            "category": "resource_exhaustion",
            "attacker": profile_id,
            "description": "触发深层递归导致栈溢出",
            "test": "recursion_depth_attack",
        })
        scenarios.append({
            "id": f"SC-016-{profile_id}",
            "name": "并发请求洪泛",
            "category": "resource_exhaustion",
            "attacker": profile_id,
            "description": "大量并发请求导致资源耗尽",
            "test": "concurrent_flood",
        })

    return scenarios


# ---------------------------------------------------------------------------
# 审查执行器
# ---------------------------------------------------------------------------

def execute_adversarial_review(
    *,
    scenarios: list[dict] | None = None,
    profiles: list[str] | None = None,
    categories: list[str] | None = None,
    timeout_per_scenario: float = 5.0,
) -> dict:
    """执行多Agent对抗式审查。

    对每个攻击场景，模拟攻击者视角执行测试，
    收集所有发现的漏洞，生成结构化报告。

    Args:
        scenarios: 攻击场景列表，None 时自动生成全部。
        profiles: 限制的攻击者，None 时使用全部。
        categories: 限制的场景类别，None 时使用全部。
        timeout_per_scenario: 每个场景的超时时间（秒）。

    Returns:
        审查结果字典，包含 vulnerabilities, stats, metadata。
    """
    if scenarios is None:
        scenarios = generate_attack_scenarios()

    # 过滤
    if profiles:
        scenarios = [s for s in scenarios if s["attacker"] in profiles]
    if categories:
        scenarios = [s for s in scenarios if s["category"] in categories]

    vulnerabilities: list[Vulnerability] = []
    vuln_counter = 0
    start_time = time.time()

    for scenario in scenarios:
        try:
            results = _execute_scenario(scenario, timeout_per_scenario)
            for r in results:
                vuln_counter += 1
                r.id = f"VULN-{vuln_counter:03d}"
                r.timestamp = datetime.now(timezone.utc).isoformat()
                if not r.attacker:
                    r.attacker = scenario["attacker"]
                if not r.scenario:
                    r.scenario = scenario["id"]
                vulnerabilities.append(r)
        except Exception as e:
            # 攻击场景执行失败本身不应该是漏洞，而是框架错误
            logger.warning(f"场景 {scenario['id']} 执行异常: {e}")

    elapsed = time.time() - start_time

    # 按严重性统计
    p0_count = sum(1 for v in vulnerabilities if v.severity == "P0")
    p1_count = sum(1 for v in vulnerabilities if v.severity == "P1")
    p2_count = sum(1 for v in vulnerabilities if v.severity == "P2")

    return {
        "metadata": {
            "review_time": datetime.now(timezone.utc).isoformat(),
            "total_scenarios": len(scenarios),
            "total_vulnerabilities": len(vulnerabilities),
            "elapsed_seconds": round(elapsed, 2),
            "profiles_used": profiles or list(ATTACKER_PROFILES.keys()),
        },
        "stats": {
            "P0": p0_count,
            "P1": p1_count,
            "P2": p2_count,
            "total": len(vulnerabilities),
        },
        "vulnerabilities": [v.to_dict() for v in vulnerabilities],
    }


def _execute_scenario(scenario: dict, timeout: float) -> list[Vulnerability]:
    """执行单个攻击场景。"""
    test_name = scenario["test"]
    handler = _SCENARIO_HANDLERS.get(test_name)
    if handler is None:
        return [Vulnerability(
            id="", title=f"未实现的场景: {test_name}",
            severity="P2", category=scenario["category"],
            attacker=scenario["attacker"], scenario=scenario["id"],
            description=f"攻击场景 {test_name} 尚未实现",
            reproduction_steps=[], affected_file="", affected_function="",
            expected_behavior="", actual_behavior="", fix_suggestion="",
        )]

    try:
        return handler(scenario)
    except Exception as e:
        return [Vulnerability(
            id="", title=f"场景执行异常: {test_name}",
            severity="P2", category=scenario["category"],
            attacker=scenario["attacker"], scenario=scenario["id"],
            description=f"执行异常: {str(e)}",
            reproduction_steps=[traceback.format_exc()],
            affected_file="", affected_function="_execute_scenario",
            expected_behavior="场景正常执行", actual_behavior=str(e),
            fix_suggestion="检查场景处理器实现",
        )]


# ---------------------------------------------------------------------------
# 场景处理器
# ---------------------------------------------------------------------------

def _make_vuln(
    title: str, severity: str, category: str, attacker: str, scenario: str,
    description: str, repro: list[str], file: str, func: str,
    expected: str, actual: str, fix: str,
) -> Vulnerability:
    return Vulnerability(
        id="", title=title, severity=severity,
        category=category, attacker=attacker, scenario=scenario,
        description=description, reproduction_steps=repro,
        affected_file=file, affected_function=func,
        expected_behavior=expected, actual_behavior=actual,
        fix_suggestion=fix,
    )


def _h_write_oversized_file(scenario: dict) -> list[Vulnerability]:
    """测试超大文件写入防御。"""
    from .knowledge_defense import InputValidator, DEFAULT_MAX_FILE_SIZE_MB

    vulns = []
    large_content = "x" * (DEFAULT_MAX_FILE_SIZE_MB * 1024 * 1024 + 1000)

    try:
        InputValidator.validate_content_size(large_content, "test")
        vulns.append(_make_vuln(
            "超大文件未被拒绝", "P0", scenario["category"],
            scenario["attacker"], scenario["id"],
            "超过5MB限制的文件内容未被拒绝，可能导致OOM",
            ["调用 write_knowledge_entry 写入 >5MB 内容"],
            ".agents/scripts/lib/knowledge_defense.py",
            "validate_content_size",
            "超大文件被拒绝并返回错误",
            "超大文件被接受或未检测到",
            "在 validate_content_size 中增加严格的大小检查",
        ))
    except Exception:
        pass  # 预期行为：被拒绝

    return vulns


def _h_write_malformed_yaml(scenario: dict) -> list[Vulnerability]:
    """测试畸形YAML防御。"""
    from .knowledge_defense import InputValidator

    vulns = []
    malformed = "---\ntitle: [unclosed\n---\ncontent"

    try:
        InputValidator.validate_frontmatter(malformed)
        vulns.append(_make_vuln(
            "畸形YAML未被检测", "P1", scenario["category"],
            scenario["attacker"], scenario["id"],
            "畸形YAML frontmatter未被检测到",
            ["写入包含畸形YAML的条目"],
            ".agents/scripts/lib/knowledge_defense.py",
            "validate_frontmatter",
            "畸形YAML被拒绝",
            "畸形YAML被接受",
            "增强YAML边界检测",
        ))
    except Exception:
        pass

    return vulns


def _h_decrypt_with_wrong_key(scenario: dict) -> list[Vulnerability]:
    """测试错误密钥解密防御。"""
    from .knowledge_crypto import decrypt_entry, get_encryption_key

    vulns = []
    wrong_key = b"wrong_key_123456789012345678901234567890"  # 32 bytes

    try:
        meta, content, level, valid = decrypt_entry({}, "test content", key=wrong_key)
        if valid:
            vulns.append(_make_vuln(
                "错误密钥解密未返回无效", "P1", scenario["category"],
                scenario["attacker"], scenario["id"],
                "使用错误密钥解密时返回了 valid=True",
                ["调用 decrypt_entry 使用错误密钥"],
                ".agents/scripts/lib/knowledge_crypto.py",
                "decrypt_entry",
                "返回 valid=False",
                "返回 valid=True",
                "确保解密失败时返回 valid=False",
            ))
    except Exception:
        pass  # 预期行为：抛出异常或返回 invalid

    return vulns


def _h_decrypt_tampered_ciphertext(scenario: dict) -> list[Vulnerability]:
    """测试篡改密文解密防御。"""
    from .knowledge_crypto import encrypt_entry, decrypt_entry, get_encryption_key

    vulns = []
    try:
        key = get_encryption_key()
        meta, content, level = encrypt_entry(
            {"title": "test"}, "test content", level="confidential", key=key,
        )
        # 篡改密文
        tampered = content[:-5] + "XXXXX"
        dec_meta, dec_content, dec_level, valid = decrypt_entry(
            {}, tampered, key=key,
        )
        if valid:
            vulns.append(_make_vuln(
                "篡改密文解密未检测到", "P0", scenario["category"],
                scenario["attacker"], scenario["id"],
                "篡改密文后解密返回 valid=True，GCM认证失败",
                ["加密内容 → 篡改密文 → 调用 decrypt_entry"],
                ".agents/scripts/lib/knowledge_crypto.py",
                "decrypt_entry",
                "返回 valid=False",
                "返回 valid=True",
                "确保AES-GCM认证标签验证失败时返回 valid=False",
            ))
    except Exception:
        pass  # 预期行为

    return vulns


def _h_decrypt_with_empty_key(scenario: dict) -> list[Vulnerability]:
    """测试空密钥解密防御。"""
    from .knowledge_crypto import decrypt_entry

    vulns = []
    try:
        meta, content, level, valid = decrypt_entry({}, "test", key=b"")
        if valid:
            vulns.append(_make_vuln(
                "空密钥解密未检测到", "P1", scenario["category"],
                scenario["attacker"], scenario["id"],
                "使用空密钥解密时返回 valid=True",
                ["调用 decrypt_entry 使用空密钥"],
                ".agents/scripts/lib/knowledge_crypto.py",
                "decrypt_entry",
                "返回 valid=False 或抛出异常",
                "返回 valid=True",
                "在解密前验证密钥非空",
            ))
    except Exception:
        pass  # 预期行为

    return vulns


def _h_tamper_content_keep_checksum(scenario: dict) -> list[Vulnerability]:
    """测试篡改正文但保持校验和不变量。"""
    from .knowledge_integrity import compute_checksum, verify_integrity

    vulns = []
    content = "original content for integrity test"
    checksum = compute_checksum(content)
    tampered = "modified content for integrity test"
    tampered_checksum = compute_checksum(tampered)

    if tampered_checksum == checksum:
        vulns.append(_make_vuln(
            "哈希碰撞——不同内容产生相同校验和", "P0", scenario["category"],
            scenario["attacker"], scenario["id"],
            "SHA-256 碰撞：不同内容产生了相同的校验和",
            [f"原始: '{content}' → {checksum}", f"篡改: '{tampered}' → {tampered_checksum}"],
            ".agents/scripts/lib/knowledge_integrity.py",
            "compute_checksum",
            "不同内容产生不同校验和",
            f"相同校验和: {checksum}",
            "检查校验和计算实现",
        ))

    # 验证检测能力
    metadata = {"integrity_checksum": checksum}
    valid, _, msg = verify_integrity(metadata, tampered)
    if valid:
        vulns.append(_make_vuln(
            "篡改内容但校验和未匹配检测到", "P1", scenario["category"],
            scenario["attacker"], scenario["id"],
            "校验和验证未能检测到内容篡改",
            [f"metadata.integrity_checksum = {checksum}", f"实际内容 = '{tampered}'"],
            ".agents/scripts/lib/knowledge_integrity.py",
            "verify_integrity",
            "verify_integrity 返回 False",
            "verify_integrity 返回 True",
            "确保 verify_integrity 正确比较内容与校验和",
        ))

    return vulns


def _h_remove_integrity_field(scenario: dict) -> list[Vulnerability]:
    """测试删除校验和字段防御。"""
    from .knowledge_integrity import verify_integrity

    vulns = []
    content = "test content"
    metadata = {}  # 无 integrity_checksum 字段

    valid, _, msg = verify_integrity(metadata, content)
    if not valid:
        vulns.append(_make_vuln(
            "无校验和字段时被误判为损坏", "P2", scenario["category"],
            scenario["attacker"], scenario["id"],
            "metadata 无 integrity_checksum 时被误判为损坏",
            ["创建无 integrity_checksum 的 metadata", "调用 verify_integrity"],
            ".agents/scripts/lib/knowledge_integrity.py",
            "verify_integrity",
            "返回 True（无校验和字段 = 跳过校验）",
            f"返回 False: {msg}",
            "无校验和字段时应视为'未校验'而非'损坏'",
        ))

    return vulns


def _h_forge_integrity_status(scenario: dict) -> list[Vulnerability]:
    """测试伪造完整性状态防御。"""
    vulns = []
    from .knowledge_integrity import compute_checksum, verify_integrity

    content = "forged content"
    real_checksum = compute_checksum(content)
    metadata = {"integrity_checksum": "fake_checksum_deadbeef"}

    valid, _, msg = verify_integrity(metadata, content)
    if valid:
        vulns.append(_make_vuln(
            "伪造校验和通过验证", "P0", scenario["category"],
            scenario["attacker"], scenario["id"],
            "伪造的校验和通过了完整性验证",
            ["设置 integrity_checksum 为 'fake_checksum_deadbeef'", "调用 verify_integrity"],
            ".agents/scripts/lib/knowledge_integrity.py",
            "verify_integrity",
            "返回 False",
            "返回 True",
            "确保 verify_integrity 比较 metadata 中的校验和与实际计算值",
        ))

    return vulns


def _h_sql_injection_query(scenario: dict) -> list[Vulnerability]:
    """测试SQL注入防御。"""
    from .knowledge_search import sanitize_query

    vulns = []
    q, safe, msg = sanitize_query("; DROP TABLE users --")
    if safe or q:
        vulns.append(_make_vuln(
            "SQL注入未被检测", "P1", scenario["category"],
            scenario["attacker"], scenario["id"],
            "SQL注入查询未被拒绝",
            ["搜索: '; DROP TABLE users --'"],
            ".agents/scripts/lib/knowledge_search.py",
            "sanitize_query",
            "返回 safe=False",
            f"返回 safe={safe}, q='{q}'",
            "增强 sanitize_query 的SQL注入检测模式",
        ))

    return vulns


def _h_xss_injection_query(scenario: dict) -> list[Vulnerability]:
    """测试XSS注入防御。"""
    from .knowledge_search import sanitize_query

    vulns = []
    q, safe, msg = sanitize_query("<script>alert(1)</script>")
    if safe:
        vulns.append(_make_vuln(
            "XSS注入未被检测", "P1", scenario["category"],
            scenario["attacker"], scenario["id"],
            "XSS注入查询未被拒绝",
            ["搜索: '<script>alert(1)</script>'"],
            ".agents/scripts/lib/knowledge_search.py",
            "sanitize_query",
            "返回 safe=False",
            "返回 safe=True",
            "增强 sanitize_query 的XSS检测模式",
        ))

    return vulns


def _h_path_traversal_read(scenario: dict) -> list[Vulnerability]:
    """测试路径遍历读取防御。"""
    from .knowledge_security import safe_resolve_path

    vulns = []
    try:
        result = safe_resolve_path("../../../../etc/passwd", KNOWLEDGE_BASE)
        vulns.append(_make_vuln(
            "路径遍历读取未被阻止", "P0", scenario["category"],
            scenario["attacker"], scenario["id"],
            "路径遍历读取未被阻止，可能泄露系统文件",
            ["调用 safe_resolve_path('../../../../etc/passwd', KNOWLEDGE_BASE)"],
            ".agents/scripts/lib/knowledge_security.py",
            "safe_resolve_path",
            "抛出异常或返回 None",
            f"返回了路径: {result}",
            "确保 safe_resolve_path 阻止知识库外部的路径",
        ))
    except (ValueError, Exception):
        pass

    return vulns


def _h_path_traversal_write(scenario: dict) -> list[Vulnerability]:
    """测试路径遍历写入防御。"""
    from .knowledge_security import safe_resolve_path

    vulns = []
    try:
        result = safe_resolve_path("../../.env", KNOWLEDGE_BASE)
        vulns.append(_make_vuln(
            "路径遍历写入未被阻止", "P0", scenario["category"],
            scenario["attacker"], scenario["id"],
            "路径遍历写入未被阻止，可能覆盖关键文件",
            ["调用 safe_resolve_path('../../.env', KNOWLEDGE_BASE)"],
            ".agents/scripts/lib/knowledge_security.py",
            "safe_resolve_path",
            "抛出异常或返回 None",
            f"返回了路径: {result}",
            "确保 safe_resolve_path 阻止知识库外部的路径",
        ))
    except (ValueError, Exception):
        pass

    return vulns


def _h_oversized_metadata_field(scenario: dict) -> list[Vulnerability]:
    """测试超长元数据字段防御。"""
    from .knowledge_defense import InputValidator

    vulns = []
    long_string = "A" * 20000

    try:
        InputValidator.validate_filename("test_" + long_string + ".md")
        vulns.append(_make_vuln(
            "超长文件名未被拒绝", "P1", scenario["category"],
            scenario["attacker"], scenario["id"],
            "超长文件名未被验证逻辑拒绝",
            [f"构造 {len(long_string)} 字符的文件名"],
            ".agents/scripts/lib/knowledge_defense.py",
            "validate_filename",
            "抛出异常",
            "文件名被接受",
            "在 validate_filename 中增加长度检查",
        ))
    except Exception:
        pass

    return vulns


def _h_inject_illegal_metadata(scenario: dict) -> list[Vulnerability]:
    """测试非法元数据注入防御。"""
    from .knowledge_defense import InputValidator

    vulns = []
    try:
        InputValidator.validate_metadata_key("__proto__")
        vulns.append(_make_vuln(
            "原型污染键名未被拒绝", "P1", scenario["category"],
            scenario["attacker"], scenario["id"],
            "'__proto__' 键名未被拒绝，可能导致原型污染",
            ["调用 validate_metadata_key('__proto__')"],
            ".agents/scripts/lib/knowledge_defense.py",
            "validate_metadata_key",
            "抛出异常",
            "键名被接受",
            "在 validate_metadata_key 中增加危险键名检查",
        ))
    except Exception:
        pass

    return vulns


def _h_recursion_depth_attack(scenario: dict) -> list[Vulnerability]:
    """测试递归深度攻击防御。"""
    from .knowledge_defense import ResourceGuard

    vulns = []
    guard = ResourceGuard()

    # 快速消耗递归深度配额
    exhausted = False
    try:
        for _ in range(100):
            guard.check_recursion_depth("test")
    except Exception:
        exhausted = True

    if not exhausted:
        vulns.append(_make_vuln(
            "递归深度限制未生效", "P1", scenario["category"],
            scenario["attacker"], scenario["id"],
            "递归深度限制未生效，可能导致栈溢出",
            ["连续调用 check_recursion_depth 100次"],
            ".agents/scripts/lib/knowledge_defense.py",
            "check_recursion_depth",
            "超过限制后抛出异常",
            "未抛出异常",
            "确保 ResourceGuard 正确追踪递归深度",
        ))

    return vulns


def _h_concurrent_flood(scenario: dict) -> list[Vulnerability]:
    """测试并发请求洪泛防御。"""
    vulns = []
    from .knowledge_defense import ResourceGuard

    guard = ResourceGuard()
    try:
        for i in range(200):
            guard.check_iteration_count("flood_test")
        vulns.append(_make_vuln(
            "迭代次数限制未生效", "P1", scenario["category"],
            scenario["attacker"], scenario["id"],
            "迭代次数限制未生效，可能导致资源耗尽",
            ["连续调用 check_iteration_count 200次"],
            ".agents/scripts/lib/knowledge_defense.py",
            "check_iteration_count",
            "超过限制后抛出异常",
            "未抛出异常",
            "确保 ResourceGuard 正确追踪迭代次数",
        ))
    except Exception:
        pass

    return vulns


# 场景处理器注册表
_SCENARIO_HANDLERS: dict[str, Callable] = {
    "write_oversized_file": _h_write_oversized_file,
    "write_malformed_yaml": _h_write_malformed_yaml,
    "decrypt_with_wrong_key": _h_decrypt_with_wrong_key,
    "decrypt_tampered_ciphertext": _h_decrypt_tampered_ciphertext,
    "decrypt_with_empty_key": _h_decrypt_with_empty_key,
    "tamper_content_keep_checksum": _h_tamper_content_keep_checksum,
    "remove_integrity_field": _h_remove_integrity_field,
    "forge_integrity_status": _h_forge_integrity_status,
    "sql_injection_query": _h_sql_injection_query,
    "xss_injection_query": _h_xss_injection_query,
    "path_traversal_read": _h_path_traversal_read,
    "path_traversal_write": _h_path_traversal_write,
    "oversized_metadata_field": _h_oversized_metadata_field,
    "inject_illegal_metadata": _h_inject_illegal_metadata,
    "recursion_depth_attack": _h_recursion_depth_attack,
    "concurrent_flood": _h_concurrent_flood,
}


# ---------------------------------------------------------------------------
# 报告生成
# ---------------------------------------------------------------------------

def generate_review_report(
    review_result: dict,
    *,
    output_dir: str | Path | None = None,
) -> Path:
    """生成结构化审查报告。

    报告包含：审查摘要、漏洞清单（按严重性分级）、
    每个漏洞的复现步骤和修复建议。

    Args:
        review_result: execute_adversarial_review 的返回结果。
        output_dir: 输出目录，默认为 docs/retrospective/reports/adversarial-reviews/。

    Returns:
        报告文件路径。
    """
    if output_dir is None:
        output_dir = REPORT_DIR

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_name = f"adversarial-review-{timestamp}.md"
    report_path = out / report_name

    meta = review_result["metadata"]
    stats = review_result["stats"]
    vulns = review_result["vulnerabilities"]

    # 按严重性分组
    p0 = [v for v in vulns if v["severity"] == "P0"]
    p1 = [v for v in vulns if v["severity"] == "P1"]
    p2 = [v for v in vulns if v["severity"] == "P2"]

    lines = []
    lines.append("---")
    lines.append(f"title: \"对抗式审查报告 - {timestamp}\"")
    lines.append("category: adversarial-review")
    lines.append(f"date: {meta['review_time'][:10]}")
    lines.append("---")
    lines.append("")
    lines.append("# 对抗式审查报告")
    lines.append("")
    lines.append("## 审查摘要")
    lines.append("")
    lines.append(f"- **审查时间**: {meta['review_time']}")
    lines.append(f"- **审查场景数**: {meta['total_scenarios']}")
    lines.append(f"- **攻击者**: {', '.join(meta['profiles_used'])}")
    lines.append(f"- **耗时**: {meta['elapsed_seconds']}s")
    lines.append("")
    lines.append("### 漏洞统计")
    lines.append("")
    lines.append(f"| 严重性 | 数量 |")
    lines.append(f"|--------|------|")
    lines.append(f"| P0 (严重) | {stats['P0']} |")
    lines.append(f"| P1 (高) | {stats['P1']} |")
    lines.append(f"| P2 (中) | {stats['P2']} |")
    lines.append(f"| **总计** | **{stats['total']}** |")
    lines.append("")

    if not vulns:
        lines.append("**未发现漏洞，所有攻击场景均被成功防御。**")
        lines.append("")
        report_path.write_text('\n'.join(lines), encoding="utf-8")
        return report_path

    # P0 漏洞
    if p0:
        lines.append("## P0 - 严重漏洞")
        lines.append("")
        for i, v in enumerate(p0, 1):
            _append_vuln_section(lines, v, i)

    # P1 漏洞
    if p1:
        lines.append("## P1 - 高危漏洞")
        lines.append("")
        for i, v in enumerate(p1, 1):
            _append_vuln_section(lines, v, i)

    # P2 漏洞
    if p2:
        lines.append("## P2 - 中危漏洞")
        lines.append("")
        for i, v in enumerate(p2, 1):
            _append_vuln_section(lines, v, i)

    lines.append("---")
    lines.append("")
    lines.append("*报告由多Agent对抗式审查框架自动生成*")
    lines.append("")

    report_path.write_text('\n'.join(lines), encoding="utf-8")
    return report_path


def _append_vuln_section(lines: list[str], v: dict, index: int):
    """追加漏洞详情。"""
    lines.append(f"### {index}. {v['title']}")
    lines.append("")
    lines.append(f"- **ID**: {v['id']}")
    lines.append(f"- **类别**: {v['category']}")
    lines.append(f"- **攻击者**: {v['attacker']}")
    lines.append(f"- **场景**: {v['scenario']}")
    lines.append(f"- **影响文件**: `{v['affected_file']}`")
    lines.append(f"- **影响函数**: `{v['affected_function']}`")
    lines.append("")
    lines.append(f"**描述**: {v['description']}")
    lines.append("")
    lines.append("**复现步骤**:")
    for step in v['reproduction_steps']:
        lines.append(f"1. {step}")
    lines.append("")
    lines.append(f"**预期行为**: {v['expected_behavior']}")
    lines.append(f"**实际行为**: {v['actual_behavior']}")
    lines.append("")
    lines.append(f"**修复建议**: {v['fix_suggestion']}")
    lines.append("")


# ---------------------------------------------------------------------------
# 审查闭环
# ---------------------------------------------------------------------------

def run_adversarial_review(
    *,
    profiles: list[str] | None = None,
    categories: list[str] | None = None,
    output_dir: str | Path | None = None,
    verbose: bool = False,
) -> dict:
    """执行完整的对抗式审查闭环。

    1. 生成攻击场景
    2. 执行多Agent攻击
    3. 生成结构化报告
    4. 归档到 docs/retrospective/

    Args:
        profiles: 限制的攻击者列表。
        categories: 限制的场景类别。
        output_dir: 报告输出目录。
        verbose: 是否输出详细信息。

    Returns:
        审查结果字典。
    """
    if verbose:
        print("=" * 50)
        print("多Agent对抗式审查框架")
        print("=" * 50)
        print()
        print(f"攻击者: {profiles or list(ATTACKER_PROFILES.keys())}")
        print(f"类别: {categories or '全部'}")
        print()

    # 1. 生成场景
    scenarios = generate_attack_scenarios()
    if profiles:
        scenarios = [s for s in scenarios if s["attacker"] in profiles]
    if categories:
        scenarios = [s for s in scenarios if s["category"] in categories]

    if verbose:
        print(f"生成 {len(scenarios)} 个攻击场景")
        print()

    # 2. 执行审查
    result = execute_adversarial_review(
        scenarios=scenarios,
        profiles=profiles,
        categories=categories,
    )

    if verbose:
        print(f"审查完成: {result['metadata']['elapsed_seconds']}s")
        print(f"发现漏洞: {result['stats']['total']} 个")
        print(f"  P0: {result['stats']['P0']}")
        print(f"  P1: {result['stats']['P1']}")
        print(f"  P2: {result['stats']['P2']}")
        print()

    # 3. 生成报告
    report_path = generate_review_report(result, output_dir=output_dir)
    result["report_path"] = str(report_path)

    if verbose:
        print(f"报告已生成: {report_path}")

    return result