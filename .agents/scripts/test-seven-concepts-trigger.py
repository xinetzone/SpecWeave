#!/usr/bin/env python3
"""七概念触发工具批量测试"""
import subprocess
import sys
from pathlib import Path

TEST_CASES = [
    ("Sprint结束了做个复盘", "W1/R→I→E→C"),
    ("线上支付挂了P0", "P0应急"),
    ("修复线上空指针异常Bug", "W2/F→V→C→R→I→E"),
    ("实现一个用户登录功能", "默认/C+V"),
    ("重构超长文档做原子化拆分", "W3/A→V→C"),
    ("把这次踩坑的经验沉淀成模式", "W4/R→I→E→V"),
    ("选Redis还是MongoDB做技术选型", "W5/F→V→I→C"),
    ("帮忙做一下PR Code Review", "代码审查/V→C"),
    ("准备发布v1.0版本打CHANGELOG", "版本发布/V→C"),
    ("修个不紧急的P2小bug", "P2/P3/V→C"),
    ("给新人做onboarding培训", "新人上手/R→E"),
    ("优化CI构建速度", "工具链/V→C→I"),
    ("制定代码审查规范", "规范制定/F→V→E→C"),
    ("把模块从vendor迁移到项目根目录", "迁移/W3"),
    ("做个PoC验证下这个方案可行吗", "PoC/C"),
    ("fix typo改个错别字", "简单修改/C"),
    ("写一个关键词匹配规则引擎", "规则引擎/F→V→C"),
    ("改进链接检查脚本", "工具链/V→C→I"),
    ("做个蛋糕", "无匹配"),
]

passed = 0
failed = 0
results = []

script = str(Path(__file__).resolve().parent / "seven-concepts-trigger.py")

print("七概念触发工具批量测试（19场景：16正向+3新增）")
print("=" * 70)

for task, expected in TEST_CASES:
    proc = subprocess.run(
        [sys.executable, script, task],
        capture_output=True, text=True, encoding="utf-8"
    )
    output = proc.stdout
    scenario_line = [l for l in output.split("\n") if "🎯 场景：" in l]
    concept_line = [l for l in output.split("\n") if "概念组合：" in l and "（无）" not in l]

    top_scenario = scenario_line[0].replace("🎯 场景：", "").strip() if scenario_line else "N/A"
    top_concept = concept_line[0].replace("概念组合：", "").strip() if concept_line else "N/A"

    ok = True
    if "P0" in expected and "P0" not in top_scenario:
        ok = False
    elif "W1" in expected and "里程碑" not in top_scenario:
        ok = False
    elif "W2" in expected and "问题解决" not in top_scenario and "故障" not in top_scenario:
        ok = False
    elif "W3" in expected and "重构" not in top_scenario and "迁移" not in top_scenario and "原子化" not in top_scenario:
        ok = False
    elif "W4" in expected and "知识沉淀" not in top_scenario:
        ok = False
    elif "W5" in expected and "架构" not in top_scenario and "规范" not in top_scenario and "技术选型" not in top_scenario:
        ok = False
    elif "代码审查" in expected and "审查" not in top_scenario:
        ok = False
    elif "版本发布" in expected and "发布" not in top_scenario:
        ok = False
    elif "P2" in expected and "P2" not in top_scenario and "非紧急" not in top_scenario:
        ok = False
    elif "新人" in expected and "新人" not in top_scenario:
        ok = False
    elif "工具链" in expected and "工具" not in top_scenario and "CI" not in top_scenario:
        ok = False
    elif "PoC" in expected and "PoC" not in top_scenario and "原型" not in top_scenario:
        ok = False
    elif "简单修改" in expected and "简单" not in top_scenario:
        ok = False
    elif "默认" in expected and "新功能" not in top_scenario and "默认" not in top_scenario:
        ok = False
    elif "规则引擎" in expected and "规则" not in top_scenario and "匹配" not in top_scenario:
        ok = False
    elif "无匹配" in expected and "无匹配" not in top_scenario:
        ok = False

    status = "✅ PASS" if ok else "❌ FAIL"
    if ok:
        passed += 1
    else:
        failed += 1
    print(f"{status} | {task[:30]:<30} → {top_scenario[:25]:<25} (期望:{expected[:15]})")

print("=" * 70)
total = passed + failed
print(f"准确率：{passed}/{total} = {passed/total*100:.0f}%")
print(f"失败：{failed}个")

if failed > 0:
    sys.exit(1)
