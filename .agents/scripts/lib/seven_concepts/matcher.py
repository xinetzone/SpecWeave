"""任务场景匹配器——根据自然语言描述匹配七概念方法论场景"""

from .constants import WORKFLOWS, QUALITY_GATES, ANTI_PATTERN_WARNINGS
from .models import MatchResult


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
