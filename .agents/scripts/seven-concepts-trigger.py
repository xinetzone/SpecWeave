#!/usr/bin/env python3
"""
七概念方法论触发匹配工具
输入：自然语言任务描述
输出：推荐的概念组合、执行顺序、参考流程、质量门提醒
"""
import argparse
import sys
from dataclasses import dataclass, field
from typing import Optional


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


@dataclass
class MatchResult:
    scenario: str
    confidence: int
    concepts: list[str]
    workflow: Optional[str]
    notes: str = ""
    quality_gates: list[str] = field(default_factory=list)
    anti_patterns: list[str] = field(default_factory=list)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="七概念方法论触发匹配工具 - 根据任务描述推荐概念组合",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python seven-concepts-trigger.py "Sprint结束做复盘"
  python seven-concepts-trigger.py "修复线上支付Bug"
  python seven-concepts-trigger.py "重构超长文档" --top 3
        """,
    )
    parser.add_argument(
        "task",
        nargs="*",
        help="任务描述（自然语言）",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=1,
        choices=[1, 2, 3],
        help="返回前N个匹配（默认1，最大3）",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有支持的场景",
    )
    return parser


def list_scenarios():
    scenarios = [
        ("里程碑/迭代/Sprint结束/版本交付", "W1", "R→I→E→C"),
        ("P0/P1故障/线上问题/Bug根因", "W2", "F→V→C→R→I→E"),
        ("新功能开发/需求实现", "C→V→(R)", "C"),
        ("重构/技术债/结构优化", "W3", "A→V→C"),
        ("文档整理/原子化/文件过大", "W3", "A→V→C"),
        ("知识沉淀/模式入库/可复用经验", "W4", "R→I→E→V"),
        ("架构决策/技术选型", "W5", "F→V→I→C"),
        ("代码审查/PR Review/MR", "V→C", "V"),
        ("版本发布/打标签/CHANGELOG", "C→V→(R)", "C"),
        ("P2/P3 Bug修复/非紧急修复", "V→C→(R)", "V"),
        ("新人上手/Onboarding/知识传递", "R→E", "R"),
        ("工具链/CI优化/脚本改进", "V→C→(I)", "V"),
        ("规则引擎/匹配/分类/推荐系统", "F→V→C", "F+V"),
        ("规范制定/规则更新/流程变化", "W5变体", "F→V→E→C"),
        ("跨项目迁移/目录重构/资产转移", "W3", "A→V→C"),
        ("P0应急响应/线上止血", "仅恢复→事后R+I", "无（先恢复）"),
        ("PoC/原型验证/探索性实验", "C松散", "C"),
        ("简单修改/拼写错误/格式调整", "仅C", "C"),
    ]
    print("支持的场景列表：")
    print("-" * 70)
    for keyword, wf, chain in scenarios:
        print(f"  {keyword:<30} → {chain:<15} ({wf})")
    print("-" * 70)
    print(f"共 {len(scenarios)} 种典型场景")


def match_task(text: str) -> list[MatchResult]:
    results = []
    text_lower = text.lower()

    is_p0 = any(k in text_lower for k in ["线上挂了", "线上故障", "宕机", "p0", "止血", "紧急恢复"])
    is_p23 = any(k in text_lower for k in ["p2", "p3", "非紧急", "不紧急", "小bug", "typo fix", "warning", "警告修复"])
    is_spec = any(k in text for k in ["规范", "规则", "标准", "流程"]) and any(k in text for k in ["制定", "更新", "建立", "创建", "新增"])

    if any(k in text_lower for k in ["里程碑", "sprint", "迭代结束", "版本交付", "周期总结", "复盘会", "sprint结束", "迭代完成"]):
        results.append(MatchResult(
            scenario="里程碑/迭代完成",
            confidence=95,
            concepts=["R", "I", "E", "C"],
            workflow="W1",
            quality_gates=QUALITY_GATES["W1"],
        ))

    if is_p0:
        results.append(MatchResult(
            scenario="P0应急响应",
            confidence=98,
            concepts=[],
            workflow=None,
            notes="⚠️ 第一阶段：仅恢复服务，不用方法论。恢复后追加R+I复盘。",
        ))
    elif not is_p23 and any(k in text_lower for k in ["线上问题", "故障", "bug", "根因", "p1", "异常", "报错", "空指针", "回调失败", "支付失败", "修复", "崩溃", "error", "exception"]):
        if "p0" not in text_lower and "宕机" not in text:
            results.append(MatchResult(
                scenario="P1+故障/问题解决",
                confidence=85,
                concepts=["F", "V", "C", "R", "I", "E"],
                workflow="W2",
                quality_gates=QUALITY_GATES["W2"],
            ))

    if any(k in text for k in ["重构", "技术债", "结构优化", "重写", "拆分文件"]):
        has_retro = any(k in text for k in ["复盘", "总结", "回顾"])
        results.append(MatchResult(
            scenario="重构优化" + ("+复盘" if has_retro else ""),
            confidence=90 if has_retro else 85,
            concepts=["A", "V", "C", "R", "I", "E"] if has_retro else ["A", "V", "C"],
            workflow="W3",
            notes="重构完成后追加R→I→E沉淀经验" if has_retro else "功能等价重构，确保无回归",
            quality_gates=QUALITY_GATES["W3"],
        ))

    if any(k in text for k in ["文档整理", "原子化", "文件过大", "导航困难", "拆分文档"]):
        if "重构" not in text:
            results.append(MatchResult(
                scenario="文档整理/原子化",
                confidence=80,
                concepts=["A", "V", "C"],
                workflow="W3",
                quality_gates=QUALITY_GATES["W3"],
            ))

    if any(k in text for k in ["知识沉淀", "模式入库", "可复用", "经验总结", "重复踩坑", "经验沉淀", "沉淀成", "沉淀模式", "踩坑经验"]):
        results.append(MatchResult(
            scenario="知识沉淀",
            confidence=80,
            concepts=["R", "I", "E", "V"],
            workflow="W4",
            quality_gates=QUALITY_GATES["W4"],
        ))

    if any(k in text for k in ["架构决策", "技术选型", "方案选择", "新架构", "技术方案"]):
        results.append(MatchResult(
            scenario="架构决策/技术选型",
            confidence=90,
            concepts=["F", "V", "I", "C"],
            workflow="W5",
            quality_gates=QUALITY_GATES["W5"],
        ))

    if is_spec:
        results.append(MatchResult(
            scenario="规范制定/更新",
            confidence=90,
            concepts=["F", "V", "E", "C"],
            workflow="W5",
            notes="属于创新流程变体，需从公理推导规则，V找规则漏洞",
            quality_gates=QUALITY_GATES["W5"],
        ))

    if not is_spec and any(k in text_lower for k in ["代码审查", "pr review", "mr", "pull request", "合并请求", "code review"]):
        results.append(MatchResult(
            scenario="代码审查/PR",
            confidence=90,
            concepts=["V", "C"],
            workflow=None,
            notes="V证伪找问题→修复→C合并提交",
        ))

    if is_p23:
        results.append(MatchResult(
            scenario="P2/P3非紧急修复",
            confidence=80,
            concepts=["V", "C"],
            workflow=None,
            notes="轻量修复：V验证风险→C直接提交→积累到一定数量后R复盘趋势",
        ))

    if any(k in text_lower for k in ["版本发布", "打标签", "changelog", "release", "发版", "上线", "发布版本"]):
        results.append(MatchResult(
            scenario="版本发布/上线",
            confidence=85,
            concepts=["V", "C"],
            workflow=None,
            notes="V验收检查→C打标签提交→上线后观察→如有问题触发W2→里程碑触发W1",
        ))

    if any(k in text_lower for k in ["ci", "工具链", "脚本改进", "自动化", "自动化检查", "检查脚本", "pipeline", "构建优化", "部署优化", "docker"]):
        has_rule_keywords = any(k in text_lower for k in ["检查脚本", "脚本改进", "自动化检查", "匹配", "规则", "过滤", "分类", "校验", "linter"])
        results.append(MatchResult(
            scenario="工具链/CI优化",
            confidence=80,
            concepts=["V", "C", "I"],
            workflow=None,
            notes="V验证构建通过→C提交→如有重复痛点I洞察根本原因",
            anti_patterns=["AP9"] if has_rule_keywords else [],
        ))

    if any(k in text_lower for k in ["规则引擎", "决策表", "匹配逻辑", "分类器", "过滤器", "关键词匹配", "模式匹配", "推荐系统", "trigger", "路由规则", "校验规则", "规则匹配"]):
        results.append(MatchResult(
            scenario="规则引擎/匹配/分类系统",
            confidence=88,
            concepts=["F", "V", "C"],
            workflow=None,
            notes="F明确匹配规则公理→V构造反例测试（必须测不该匹配的场景）→C提交→发现误判触发W2",
            anti_patterns=["AP9"],
        ))

    if any(k in text for k in ["迁移", "移动目录", "跨项目", "模块转移"]):
        results.append(MatchResult(
            scenario="跨项目迁移",
            confidence=80,
            concepts=["A", "V", "C"],
            workflow="W3",
            quality_gates=QUALITY_GATES["W3"],
        ))

    if any(k in text for k in ["新人", "onboard", "入职", "上手", "培训", "知识传递"]):
        results.append(MatchResult(
            scenario="新人上手",
            confidence=75,
            concepts=["R", "E"],
            workflow=None,
            notes="案例复盘→萃取核心模式→学习文档",
        ))

    if any(k in text for k in ["poc", "原型", "验证", "探索", "可行性", "实验"]):
        results.append(MatchResult(
            scenario="PoC/原型验证",
            confidence=85,
            concepts=["C"],
            workflow=None,
            notes="快速松散迭代，验证通过后再用方法论重构",
        ))

    if any(k in text_lower for k in ["fix typo", "拼写错误", "错别字", "格式调整", "改个文案", "版本号升级", "依赖升级"]):
        results.append(MatchResult(
            scenario="简单修改",
            confidence=95,
            concepts=["C"],
            workflow=None,
            notes="trivial任务（<10min），直接C原子提交即可，不用其他概念",
        ))

    if not results:
        is_dev_related = any(k in text_lower for k in [
            "开发", "实现", "修复", "bug", "代码", "功能", "文档", "脚本",
            "写", "改", "加", "优化", "更新", "create", "fix", "update", "add",
            "新建", "增加", "新增", "写个", "开发个", "implement", "feature",
            "react", "vue", "组件", "接口", "api", "页面", "模块", "函数",
            "重构", "提交", "commit", "pr", "mr", "review", "测试", "单元测试",
        ])
        if is_dev_related:
            results.append(MatchResult(
                scenario="新功能开发（默认）",
                confidence=40,
                concepts=["C", "V"],
                workflow=None,
                notes="未明确匹配到具体场景，默认按新功能开发处理：C原子提交→V对抗审查→(上线后R复盘)。如遇'知其然不知其所以然'，追加F。",
            ))
        else:
            results.append(MatchResult(
                scenario="无匹配/非开发任务",
                confidence=20,
                concepts=[],
                workflow=None,
                notes="未识别为典型开发任务，请用更具体的描述重试，或查阅速查手册人工判断。",
            ))

    results.sort(key=lambda r: r.confidence, reverse=True)
    return results


def print_result(result: MatchResult, index: int = 0):
    prefix = f"[Top{index+1}] " if index > 0 else ""
    print(f"\n{prefix}🎯 场景：{result.scenario}")
    print(f"   置信度：{'█' * (result.confidence // 10)}{'░' * (10 - result.confidence // 10)} {result.confidence}%")

    if result.concepts:
        chain = " → ".join(result.concepts)
        print(f"   概念组合：{chain}")
    else:
        print(f"   概念组合：（无）")

    if result.workflow:
        wf = WORKFLOWS[result.workflow]
        print(f"   参考流程：{result.workflow} {wf['name']} [{wf['chain']}]")

    if result.notes:
        print(f"   💡 提示：{result.notes}")

    if result.quality_gates:
        print(f"   🚧 质量门：")
        for g in result.quality_gates:
            print(f"      • {g}")

    if result.anti_patterns:
        for ap_id in result.anti_patterns:
            warnings = ANTI_PATTERN_WARNINGS.get(ap_id, [f"⚠️ {ap_id}反模式预警"])
            for w in warnings:
                print(f"   {w}")


def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.list:
        list_scenarios()
        return 0

    if not args.task:
        parser.print_help()
        return 1

    task_text = " ".join(args.task)
    print(f"📋 任务描述：{task_text}")
    print("=" * 60)

    results = match_task(task_text)
    top_n = min(args.top, len(results))

    for i in range(top_n):
        print_result(results[i], i)

    print("\n" + "=" * 60)
    print("📖 详细规则参考：seven-concepts-quick-reference.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
