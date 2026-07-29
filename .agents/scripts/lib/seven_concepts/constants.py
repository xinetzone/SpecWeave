CONCEPTS = {
    "R": "复盘(Retrospective)",
    "I": "洞察(Insight)",
    "E": "萃取(Extraction)",
    "C": "原子提交(Atomic Commit)",
    "A": "原子化(Atomization)",
    "F": "第一性原理(First Principles)",
    "V": "对抗性审查(Adversarial Review)",
}

WORKFLOWS = {
    "W1": {"name": "里程碑复盘闭环", "chain": "R→I→E→C", "id": "W1"},
    "W2": {"name": "问题解决闭环", "chain": "F→V→C→R→I→E", "id": "W2"},
    "W3": {"name": "重构优化闭环", "chain": "A→V→C→(R)", "id": "W3"},
    "W4": {"name": "知识沉淀闭环", "chain": "R→I→E→V→入库", "id": "W4"},
    "W5": {"name": "创新突破流程", "chain": "F→V→I→C", "id": "W5"},
}

QUALITY_GATES = {
    "W1": ["G1:事实无因果词", "G2:洞察四元组完整可证伪", "G3:模式通过V审查入库"],
    "W2": ["G1:根因可复现修复100%", "G2:含预防措施", "G3:同类pattern入库"],
    "W3": ["G1:功能等价无回归", "G2:链接100%完整", "G3:单文件≤500行"],
    "W4": ["G1:≥2个独立案例", "G2:配套≥1个反模式", "G3:maturity标注完整"],
    "W5": ["G1:所有假设显式列出", "G2:≥3个失败场景防御", "G3:PoC数据支撑"],
}

ANTI_PATTERN_WARNINGS = {
    "AP9": [
        "⚠️ AP9反模式预警：正向测试通过就上线",
        "   规则/匹配/分类/推荐类功能必须做V反例测试：",
        "   • 构造≥3个「应该不匹配」的反例（无关/边界/混合场景）",
        "   • 每个反例明确预期结果（不能「没崩溃就算通过」）",
        "   • 修复反例后重跑正向测试防回归",
        "   参考：adversarial-review-prompt-pattern.md §规则类反例构造五步法",
    ],
}
