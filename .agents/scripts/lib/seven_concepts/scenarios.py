"""场景定义数据——支持的任务场景列表"""

SCENARIOS_LIST = [
    ("里程碑/迭代/Sprint结束/版本交付", "W1", "R→I→E→C"),
    ("P0/P1故障/线上问题/Bug根因", "W2", "F→V→C→R→I→E"),
    ("新功能开发/需求实现", None, "C→V→(R)"),
    ("重构/技术债/结构优化", "W3", "A→V→C"),
    ("文档整理/原子化/文件过大", "W3", "A→V→C"),
    ("知识沉淀/模式入库/可复用经验", "W4", "R→I→E→V"),
    ("架构决策/技术选型", "W5", "F→V→I→C"),
    ("代码审查/PR Review/MR", None, "V→C"),
    ("版本发布/打标签/CHANGELOG", None, "C→V→(R)"),
    ("P2/P3 Bug修复/非紧急修复", None, "V→C→(R)"),
    ("新人上手/Onboarding/知识传递", None, "R→E"),
    ("工具链/CI优化/脚本改进", None, "V→C→(I)"),
    ("规则引擎/匹配/分类/推荐系统", None, "F→V→C"),
    ("规范制定/规则更新/流程变化", "W5", "F→V→E→C"),
    ("跨项目迁移/目录重构/资产转移", "W3", "A→V→C"),
    ("P0应急响应/线上止血", None, "无（先恢复）"),
    ("PoC/原型验证/探索性实验", None, "C"),
    ("简单修改/拼写错误/格式调整", None, "C"),
]


def get_all_scenarios() -> list[tuple[str, str, str]]:
    """返回所有支持的场景列表"""
    return SCENARIOS_LIST
