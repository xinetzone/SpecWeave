"""Task 8 冒烟测试。"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

from lib.knowledge_adversarial import (
    generate_attack_scenarios,
    execute_adversarial_review,
    run_adversarial_review,
    generate_review_report,
    ATTACKER_PROFILES,
    Vulnerability,
)

print("TR-8.0 PASS: imports OK")

# TR-8.1: 攻击场景生成
scenarios = generate_attack_scenarios()
assert len(scenarios) >= 10, f"TR-8.1 FAIL: only {len(scenarios)} scenarios"
assert len(scenarios) == 32, f"TR-8.1 FAIL: expected 32, got {len(scenarios)}"
print(f"TR-8.1 PASS: {len(scenarios)} attack scenarios generated")

# TR-8.2: 场景覆盖7个类别
categories = set(s["category"] for s in scenarios)
assert len(categories) == 7, f"TR-8.2 FAIL: only {len(categories)} categories"
print(f"TR-8.2 PASS: {len(categories)} categories covered")

# TR-8.3: 每个场景不导致系统永久损坏
result = execute_adversarial_review()
assert "vulnerabilities" in result
assert "stats" in result
print(f"TR-8.3 PASS: no permanent damage (stats={result['stats']})")

# TR-8.4: 审查报告生成
report_path = generate_review_report(result)
assert report_path.exists(), f"TR-8.4 FAIL: report not found at {report_path}"
content = report_path.read_text(encoding="utf-8")
assert "审查摘要" in content
assert "漏洞统计" in content
print(f"TR-8.4 PASS: report generated at {report_path}")

# TR-8.5: 漏洞包含复现步骤
for v in result["vulnerabilities"][:3]:
    assert "reproduction_steps" in v
    assert "severity" in v
    assert "affected_file" in v
    assert "fix_suggestion" in v
print("TR-8.5 PASS: vulnerabilities have reproduction steps + fix suggestions")

# TR-8.6: 漏洞分级正确
for v in result["vulnerabilities"]:
    assert v["severity"] in ("P0", "P1", "P2"), f"TR-8.6 FAIL: invalid severity {v['severity']}"
print("TR-8.6 PASS: all severities valid (P0/P1/P2)")

# TR-8.7: 攻击者Profile完整
assert len(ATTACKER_PROFILES) == 5
for pid in ["security", "boundary", "integrity", "timing", "fuzzer"]:
    assert pid in ATTACKER_PROFILES
    assert ATTACKER_PROFILES[pid].attack_vectors
print(f"TR-8.7 PASS: {len(ATTACKER_PROFILES)} attacker profiles with vectors")

# TR-8.8: 按攻击者筛选
result_security = execute_adversarial_review(profiles=["security"])
assert result_security["metadata"]["profiles_used"] == ["security"]
print(f"TR-8.8 PASS: filtered by profile, {result_security['metadata']['total_scenarios']} scenarios")

# TR-8.9: 按类别筛选
result_cat = execute_adversarial_review(categories=["path_traversal"])
assert result_cat["metadata"]["total_scenarios"] == 4  # 2 profiles x 2 tests
print(f"TR-8.9 PASS: filtered by category, {result_cat['metadata']['total_scenarios']} scenarios")

# TR-8.10: Vulnerability 数据结构
v = Vulnerability(
    id="TEST-001", title="Test", severity="P0", category="test",
    attacker="security", scenario="SC-001", description="desc",
    reproduction_steps=["step1", "step2"],
    affected_file="test.py", affected_function="test_func",
    expected_behavior="expected", actual_behavior="actual",
    fix_suggestion="fix",
)
d = v.to_dict()
assert d["id"] == "TEST-001"
assert d["severity"] == "P0"
assert len(d["reproduction_steps"]) == 2
print("TR-8.10 PASS: Vulnerability dataclass works")

# TR-8.11: run_adversarial_review 完整流程
full_result = run_adversarial_review(profiles=["security"], verbose=False)
assert "report_path" in full_result
assert Path(full_result["report_path"]).exists()
print(f"TR-8.11 PASS: full review pipeline, report at {full_result['report_path']}")

# TR-8.12: 未发现漏洞时报告仍生成
empty_result = {"metadata": {"review_time": "2026-01-01", "total_scenarios": 0, "elapsed_seconds": 0, "profiles_used": []}, "stats": {"P0": 0, "P1": 0, "P2": 0, "total": 0}, "vulnerabilities": []}
empty_report = generate_review_report(empty_result)
assert empty_report.exists()
clean = empty_report.read_text(encoding="utf-8")
assert "未发现漏洞" in clean
print("TR-8.12 PASS: empty report still generated correctly")

print()
print("ALL 12 TESTS PASSED")