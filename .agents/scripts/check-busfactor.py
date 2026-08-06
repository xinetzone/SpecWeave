#!/usr/bin/env python3
"""人维·关系冗余自动化扫描工具。

通过扫描 MAINTAINERS.md / BUSFACTOR.md / CONTRIBUTING.md 三份治理文档，
客观评估项目的人维（关系冗余）健康度，计算 Bus Factor 风险分数。

用法:
    python .agents/scripts/check-busfactor.py              # 彩色报告输出
    python .agents/scripts/check-busfactor.py --json       # JSON格式输出（CI集成）
    python .agents/scripts/check-busfactor.py --repo-root <path>  # 指定仓库根目录

评分维度:
    - 维护者结构（40分）：核心维护者数/协作者数/领域贡献者/晋升路径/决策机制
    - 灾备就绪度（30分）：应急步骤/红线禁令/文件索引/健康检查/CI说明/漏洞处理
    - 贡献友好度（30分）：GFI章节/微任务表/贡献者承诺/零责备文化/示例路径
"""


import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from lib.cli import (
    add_common_args,
    print_error,
    print_header,
    print_pass,
    print_summary,
    print_warn,
    setup_safe_output,
)


# ── 数据结构 ──────────────────────────────────────────────

@dataclass
class CheckItem:
    """单个人维检查项。"""
    id: str
    category: str  # maintainers/busfactor/contributing
    name: str
    max_score: int
    actual_score: int = 0
    detail: str = ""
    passed: bool = False


@dataclass
class PeopleDimensionResult:
    """人维扫描完整结果。"""
    items: list[CheckItem]
    category_scores: dict[str, float]  # category -> percentage score
    total_score: float
    total_level: str
    bus_factor: int  # 估算的bus factor
    warnings: list[str]
    strengths: list[str]
    doc_status: dict[str, bool]  # document -> exists?


# ── 文档解析器 ─────────────────────────────────────────────

def parse_maintainers(content: str) -> list[CheckItem]:
    """解析 MAINTAINERS.md，返回检查项。"""
    items = []

    # 1. 核心维护者数量（20分）
    core_section = re.search(
        r'### 核心维护者.*?\n(.*?)(?=\n###|\n---|\Z)', content, re.DOTALL
    )
    core_count = 0
    if core_section:
        # 统计GitHub链接数，排除"待补充"行
        rows = re.findall(r'\[@\w+\]\(https?://github\.com/\w+\)', core_section.group(1))
        core_count = len(rows)
        # 排除占位符行
        placeholder = '（待补充）' in core_section.group(1) or '*（待补充）*' in core_section.group(1)
        if placeholder and core_count == 0:
            core_count = 0

    core_score = min(core_count * 10, 20) if core_count > 0 else 0
    items.append(CheckItem(
        id="m1", category="maintainers",
        name=f"核心维护者数量（当前{core_count}人）",
        max_score=20, actual_score=core_score,
        detail=f"检测到{core_count}位核心维护者。Bus Factor核心指标：目标≥3人。",
        passed=core_count >= 2,
    ))

    # 2. 协作者数量（8分）
    collab_section = re.search(
        r'### 协作者.*?\n(.*?)(?=\n###|\n---|\Z)', content, re.DOTALL
    )
    collab_count = 0
    if collab_section:
        rows = re.findall(r'\[@\w+\]\(https?://github\.com/\w+\)', collab_section.group(1))
        collab_count = len(rows)

    collab_score = min(collab_count * 4, 8) if collab_count > 0 else 0
    items.append(CheckItem(
        id="m2", category="maintainers",
        name=f"协作者数量（当前{collab_count}人）",
        max_score=8, actual_score=collab_score,
        detail=f"检测到{collab_count}位协作者（Triage权限）。协作者可分流Issue/PR管理压力。",
        passed=collab_count >= 1,
    ))

    # 3. 领域贡献者数量（4分）
    domain_section = re.search(
        r'### 领域贡献者.*?\n(.*?)(?=\n##|\n---|\Z)', content, re.DOTALL
    )
    domain_count = 0
    if domain_section:
        rows = re.findall(r'\[@\w+\]\(https?://github\.com/\w+\)', domain_section.group(1))
        domain_count = len(rows)

    domain_score = min(domain_count * 2, 4) if domain_count > 0 else 0
    items.append(CheckItem(
        id="m3", category="maintainers",
        name=f"领域贡献者数量（当前{domain_count}人）",
        max_score=4, actual_score=domain_score,
        detail=f"检测到{domain_count}位领域贡献者。",
        passed=domain_count >= 1,
    ))

    # 4. 晋升路径（4分）
    has_promotion = '如何成为维护者' in content or '晋升' in content
    items.append(CheckItem(
        id="m4", category="maintainers",
        name="维护者晋升路径",
        max_score=4, actual_score=4 if has_promotion else 0,
        detail="明确定义从贡献者→协作者→核心维护者的量化晋升标准。" if has_promotion
               else "缺少维护者晋升路径，贡献者不知道如何成长为维护者。",
        passed=has_promotion,
    ))

    # 5. 决策机制（2分）
    has_decision = '决策机制' in content
    items.append(CheckItem(
        id="m5", category="maintainers",
        name="决策机制说明",
        max_score=2, actual_score=2 if has_decision else 0,
        detail="已定义日常决策/规范变更/紧急修复的决策分级。" if has_decision
               else "缺少决策机制说明，决策过程不透明。",
        passed=has_decision,
    ))

    # 6. 荣誉退休机制（2分）
    has_retirement = '荣誉退休' in content
    items.append(CheckItem(
        id="m6", category="maintainers",
        name="荣誉退休机制",
        max_score=2, actual_score=2 if has_retirement else 0,
        detail="允许核心维护者转为荣誉状态，降低交接阻力。" if has_retirement
               else "缺少荣誉退休机制，维护者离场缺乏体面出口。",
        passed=has_retirement,
    ))

    return items


def parse_busfactor(content: str) -> list[CheckItem]:
    """解析 BUSFACTOR.md，返回检查项。"""
    items = []

    # 1. 紧急接续步骤（8分）
    has_steps = '紧急接续步骤' in content or '接管流程' in content
    has_30day = '30天' in content or '30 天' in content
    has_fork = 'fork' in content.lower() or 'Fork' in content
    steps_score = 0
    if has_steps:
        steps_score += 3
    if has_30day:
        steps_score += 2
    if has_fork:
        steps_score += 3
    items.append(CheckItem(
        id="b1", category="busfactor",
        name="紧急接续步骤完整性",
        max_score=8, actual_score=steps_score,
        detail=f"接续步骤{'有' if has_steps else '缺'}，失联阈值{'明确（30天）' if has_30day else '未明确'}，Fork指引{'有' if has_fork else '缺'}。",
        passed=steps_score >= 6,
    ))

    # 2. 红线禁令（6分）
    red_lines_section = re.search(r'绝对禁止事项.*?\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    red_line_count = 0
    if red_lines_section:
        red_line_count = len(re.findall(r'^\d+\.\s+\*\*', red_lines_section.group(1), re.MULTILINE))
    red_score = min(red_line_count, 6)
    items.append(CheckItem(
        id="b2", category="busfactor",
        name=f"红线禁令数量（{red_line_count}条）",
        max_score=6, actual_score=red_score,
        detail=f"定义了{red_line_count}条绝对禁止事项。" if red_line_count >= 4
               else f"仅定义了{red_line_count}条红线，建议≥4条覆盖核心风险。",
        passed=red_line_count >= 4,
    ))

    # 3. 关键文件索引（5分）
    has_file_index = '关键文件索引' in content
    p0_count = 0
    p0_section = re.search(r'关键文件索引.*?\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if p0_section:
        p0_count = len(re.findall(r'\|\s*P0\s*\|', p0_section.group(1)))
    index_score = (3 if has_file_index else 0) + min(p0_count, 2)
    items.append(CheckItem(
        id="b3", category="busfactor",
        name=f"关键文件索引（{p0_count}个P0文件）",
        max_score=5, actual_score=index_score,
        detail=f"文件索引{'有' if has_file_index else '缺'}，P0优先级文件{p0_count}个。",
        passed=has_file_index and p0_count >= 2,
    ))

    # 4. 健康度检查命令（4分）
    has_health_check = '健康度快速检查' in content or '健康度检查' in content
    health_commands = 0
    if has_health_check:
        health_match = re.search(r'健康度.*?\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if health_match:
            health_commands = len(re.findall(r'python\s+\.agents/scripts/', health_match.group(1)))
    health_score = (2 if has_health_check else 0) + min(health_commands, 2)
    items.append(CheckItem(
        id="b4", category="busfactor",
        name=f"项目健康度检查命令（{health_commands}条）",
        max_score=4, actual_score=health_score,
        detail=f"健康检查章节{'有' if has_health_check else '缺'}，包含{health_commands}条验证命令。",
        passed=has_health_check and health_commands >= 2,
    ))

    # 5. CI/CD说明（3分）
    has_ci = 'CI/CD' in content or '流水线' in content or 'workflow' in content.lower()
    items.append(CheckItem(
        id="b5", category="busfactor",
        name="CI/CD流水线说明",
        max_score=3, actual_score=3 if has_ci else 0,
        detail="已说明CI/CD工作流配置。" if has_ci else "缺少CI/CD说明，接续维护者可能误判部署方式。",
        passed=has_ci,
    ))

    # 6. 安全漏洞处理流程（4分）
    has_security = '安全漏洞' in content or '安全' in content
    items.append(CheckItem(
        id="b6", category="busfactor",
        name="安全漏洞处理流程",
        max_score=4, actual_score=4 if has_security else 0,
        detail="已定义安全漏洞接收/修复/披露流程。" if has_security
               else "缺少安全漏洞处理流程，发现漏洞时可能应对失当。",
        passed=has_security,
    ))

    return items


def parse_contributing(content: str) -> list[CheckItem]:
    """解析 CONTRIBUTING.md，返回检查项。"""
    items = []

    # 1. Good First Issue 章节（8分）
    has_gfi = 'Good First Issue' in content or '首次贡献' in content
    items.append(CheckItem(
        id="c1", category="contributing",
        name="Good First Issue 章节",
        max_score=8, actual_score=8 if has_gfi else 0,
        detail="已添加首次贡献指南章节。" if has_gfi
               else "缺少Good First Issue章节，新贡献者不知从何入手。",
        passed=has_gfi,
    ))

    # 2. 微任务表（7分）
    micro_table = re.search(
        r'\|\s*\*\*修复错别字\*\*.*?\n(.*?)(?=\n>|\n###|\Z)', content, re.DOTALL
    )
    micro_rows = 0
    if micro_table:
        # 统计表格行（以|开头、包含**加粗**的任务类型行）
        micro_rows = len(re.findall(r'^\|\s*\*\*[^*]+\*\*', micro_table.group(0), re.MULTILINE))
    micro_score = min(micro_rows + 1, 7) if micro_rows > 0 else 0
    items.append(CheckItem(
        id="c2", category="contributing",
        name=f"微任务表（{micro_rows}类随时可做的任务）",
        max_score=7, actual_score=micro_score,
        detail=f"定义了{micro_rows}类无需讨论即可提交PR的微任务。" if micro_rows >= 4
               else f"微任务种类较少（{micro_rows}类），建议≥4类覆盖不同技能。",
        passed=micro_rows >= 4,
    ))

    # 3. 首次贡献者承诺（5分）
    has_promise = '首次贡献者承诺' in content or '不会因为' in content
    promise_items = 0
    if has_promise:
        promise_match = re.search(r'首次贡献者承诺.*?\n(.*?)(?=\n###|\n---|\Z)', content, re.DOTALL)
        if promise_match:
            promise_items = len(re.findall(r'^\-\s+🟢', promise_match.group(1), re.MULTILINE))
    promise_score = (2 if has_promise else 0) + min(promise_items, 3)
    items.append(CheckItem(
        id="c3", category="contributing",
        name=f"首次贡献者承诺（{promise_items}条）",
        max_score=5, actual_score=promise_score,
        detail=f"对首次贡献者做出{promise_items}条明确承诺。" if promise_items >= 3
               else f"承诺条目不足（{promise_items}条），建议≥3条（不拒绝/回复时限/零责备等）。",
        passed=has_promise and promise_items >= 3,
    ))

    # 4. 零责备文化声明（3分）
    has_no_blame = '零责备' in content or '不会有人因为你写错' in content or '犯错是正常' in content
    items.append(CheckItem(
        id="c4", category="contributing",
        name="零责备文化声明",
        max_score=3, actual_score=3 if has_no_blame else 0,
        detail="明确声明零责备文化，降低新贡献者心理负担。" if has_no_blame
               else "缺少零责备文化声明，新贡献者可能因怕犯错而不敢提交PR。",
        passed=has_no_blame,
    ))

    # 5. 首次贡献示例路径（4分）
    has_example = '示例路径' in content or '第一次贡献' in content or '如果你完全不知道' in content
    steps_in_example = 0
    if has_example:
        # 查找"示例路径"或"第一次贡献"章节后的编号列表
        example_match = re.search(
            r'(?:示例路径|第一次贡献[？?]|如果你完全不知道).*?(?:\n{1,2})(.*?)(?=\n>|\n##|\Z)',
            content, re.DOTALL
        )
        if example_match:
            steps_in_example = len(re.findall(r'^\d+\.\s+', example_match.group(1), re.MULTILINE))
        # 如果上面没匹配到，直接在整个文档中找紧跟在"按这个路径走"后的编号列表
        if steps_in_example == 0:
            walk_match = re.search(r'按这个路径走[：:].*?\n(.*?)(?=\n>|\n##|\Z)', content, re.DOTALL)
            if walk_match:
                steps_in_example = len(re.findall(r'^\d+\.\s+', walk_match.group(1), re.MULTILINE))
    example_score = (2 if has_example else 0) + min(steps_in_example, 2)
    items.append(CheckItem(
        id="c5", category="contributing",
        name=f"首次贡献示例路径（{steps_in_example}步）",
        max_score=4, actual_score=example_score,
        detail=f"提供了{steps_in_example}步首次贡献示例路径。" if steps_in_example >= 4
               else f"示例路径步数不足（{steps_in_example}步），建议4-5步具体指引。",
        passed=has_example and steps_in_example >= 3,
    ))

    # 6. 前置检查清单（3分）
    has_checklist = '提交前检查' in content
    items.append(CheckItem(
        id="c6", category="contributing",
        name="提交前检查清单",
        max_score=3, actual_score=3 if has_checklist else 0,
        detail="已定义提交前检查清单，降低PR被驳回的挫败感。" if has_checklist
               else "缺少提交前检查清单。",
        passed=has_checklist,
    ))

    return items


# ── 评分引擎 ──────────────────────────────────────────────

def _score_to_level(score: float) -> str:
    if score < 30:
        return "danger"
    if score < 50:
        return "warning"
    if score < 70:
        return "moderate"
    if score < 90:
        return "good"
    return "excellent"


def _level_cn(level: str) -> str:
    return {
        "danger": "危险🔴",
        "warning": "警告🟠",
        "moderate": "一般🟡",
        "good": "健康🟢",
        "excellent": "优秀🔵",
    }.get(level, "未知")


def estimate_bus_factor(core_count: int, collab_count: int, domain_count: int) -> int:
    """根据维护者结构估算Bus Factor。"""
    total = core_count + collab_count
    if core_count >= 3 and collab_count >= 2:
        return min(core_count + collab_count, 8)
    if core_count >= 2:
        return 2 + min(collab_count, 2)
    if core_count == 1:
        return 1 + min(collab_count, 1)
    return 1


def scan_repo(repo_root: Path) -> PeopleDimensionResult:
    """扫描仓库，计算人维得分。"""
    doc_status = {}
    all_items = []
    warnings = []
    strengths = []

    # 扫描三份文档
    docs = {
        "maintainers": repo_root / "MAINTAINERS.md",
        "busfactor": repo_root / "BUSFACTOR.md",
        "contributing": repo_root / "CONTRIBUTING.md",
    }

    parsers = {
        "maintainers": parse_maintainers,
        "busfactor": parse_busfactor,
        "contributing": parse_contributing,
    }

    category_max = {"maintainers": 40, "busfactor": 30, "contributing": 30}
    category_scores = {}

    for key, path in docs.items():
        doc_status[key] = path.exists()
        if path.exists():
            content = path.read_text(encoding="utf-8")
            items = parsers[key](content)
            all_items.extend(items)
            cat_score = sum(it.actual_score for it in items)
            cat_max = sum(it.max_score for it in items)
            category_scores[key] = round(cat_score / cat_max * 100, 1) if cat_max > 0 else 0
        else:
            category_scores[key] = 0
            warnings.append(f"文档缺失：{path.name} — 这是严重的人维风险信号")

    # 计算总分
    total_max = sum(it.max_score for it in all_items)
    total_actual = sum(it.actual_score for it in all_items)
    total_score = round(total_actual / total_max * 100, 1) if total_max > 0 else 0
    total_level = _score_to_level(total_score)

    # 估算Bus Factor
    core_count = sum(1 for it in all_items if it.id == "m1" and it.actual_score >= 10)
    # 更准确的估算：直接从maintainers项计算
    core_maintainers = 0
    collabs = 0
    domains = 0
    for it in all_items:
        if it.id == "m1":
            core_maintainers = it.actual_score // 10 if it.actual_score > 0 else 0
        elif it.id == "m2":
            collabs = it.actual_score // 4 if it.actual_score > 0 else 0
        elif it.id == "m3":
            domains = it.actual_score // 2 if it.actual_score > 0 else 0

    bus_factor = estimate_bus_factor(core_maintainers, collabs, domains)

    # 生成警告和强项
    for it in all_items:
        if not it.passed and it.actual_score < it.max_score * 0.5:
            warnings.append(f"⚠️ {it.name}：{it.detail}")
        elif it.passed and it.actual_score >= it.max_score * 0.8:
            strengths.append(f"✅ {it.name}")

    # Bus Factor特殊警告
    if bus_factor == 1:
        warnings.append("🚨 Bus Factor = 1：项目完全依赖单一维护者！这是人维最高级别风险——一旦该人失联，项目立刻陷入无人维护状态。")
    elif bus_factor == 2:
        warnings.append("⚠️ Bus Factor = 2：项目勉强有2人可维护，但仍处于危险区间。建议尽快发展第3位协作者。")

    if not doc_status.get("maintainers", False):
        warnings.append("🔴 MAINTAINERS.md 不存在：维护者职责不透明，外部贡献者不知道找谁。")
    if not doc_status.get("busfactor", False):
        warnings.append("🔴 BUSFACTOR.md 不存在：无应急接续方案，维护者失联=项目死亡。")
    if not doc_status.get("contributing", False):
        warnings.append("🔴 CONTRIBUTING.md 不存在：新贡献者无法了解贡献流程。")

    return PeopleDimensionResult(
        items=all_items,
        category_scores=category_scores,
        total_score=total_score,
        total_level=total_level,
        bus_factor=bus_factor,
        warnings=warnings,
        strengths=strengths,
        doc_status=doc_status,
    )


# ── 报告输出 ──────────────────────────────────────────────

def print_report(result: PeopleDimensionResult, repo_root: Path) -> None:
    """打印人维扫描报告。"""
    print()
    print_header("人维·关系冗余 自动化扫描报告", width=60)
    print()

    # 文档状态
    print("【文档状态】")
    print()
    doc_names = {
        "maintainers": "MAINTAINERS.md",
        "busfactor": "BUSFACTOR.md",
        "contributing": "CONTRIBUTING.md",
    }
    for key, name in doc_names.items():
        exists = result.doc_status.get(key, False)
        if exists:
            print_pass(f"{name} 存在")
        else:
            print_error(f"{name} 缺失")
    print()

    # 分类得分
    cat_names = {
        "maintainers": "🏗️  维护者结构（40分）",
        "busfactor": "🆘 灾备就绪度（30分）",
        "contributing": "🤝 贡献友好度（30分）",
    }
    print("【分类得分】")
    print()
    for cat_key in ["maintainers", "busfactor", "contributing"]:
        score = result.category_scores.get(cat_key, 0)
        level = _score_to_level(score)
        level_cn = _level_cn(level)
        bar_len = 30
        filled = int(score / 100 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"  {cat_names[cat_key]}")
        print(f"    [{bar}] {score}/100 {level_cn}")

        # 该分类下的详细项
        cat_items = [it for it in result.items if it.category == cat_key]
        for it in cat_items:
            icon = "✅" if it.passed else "❌"
            print(f"      {icon} {it.name}: {it.actual_score}/{it.max_score}")
        print()

    # Bus Factor
    print("【Bus Factor 评估】")
    print()
    bf = result.bus_factor
    bf_icon = "🔴" if bf <= 1 else ("🟠" if bf <= 2 else ("🟡" if bf <= 3 else "🟢"))
    print(f"  {bf_icon} 当前 Bus Factor ≈ {bf}")
    if bf <= 1:
        print_warn("    项目被卡车撞风险极高：1个人出事 = 项目停摆")
    elif bf <= 2:
        print_warn("    仍然脆弱：需要至少3人熟悉核心代码/规范才安全")
    elif bf <= 3:
        print(f"    基本可接受，但仍建议提升到≥4")
    else:
        print_pass(f"    Bus Factor健康，项目具备较强的抗失联能力")
    print()

    # 强项
    if result.strengths:
        print("【强项】")
        print()
        for s in result.strengths[:8]:
            print_pass(s)
        print()

    # 警告
    if result.warnings:
        print("【风险与改进建议】")
        print()
        for w in result.warnings:
            if w.startswith("🚨") or w.startswith("🔴"):
                print_error(w)
            else:
                print_warn(w)
        print()

    # 综合评分
    print("【综合评估】")
    print()
    total_bar_len = 40
    filled = int(result.total_score / 100 * total_bar_len)
    bar = "█" * filled + "░" * (total_bar_len - filled)
    level_cn = _level_cn(result.total_level)
    print(f"  人维总分: [{bar}] {result.total_score}/100 {level_cn}")
    print()

    # 人维等级建议
    if result.total_score < 30:
        print_error("人维极度危险：项目严重依赖单一个人，且无应急方案。强烈建议立即创建 MAINTAINERS.md 和 BUSFACTOR.md。")
    elif result.total_score < 50:
        print_warn("人维偏低：基础文档已建立但内容单薄，维护者集中度过高。建议按检查项逐项补齐。")
    elif result.total_score < 70:
        print_pass("人维一般：治理框架已搭好，但需要填充实际维护者和协作者。邀请信任的贡献者加入是关键下一步。")
    elif result.total_score < 90:
        print_pass("人维健康：维护者结构、灾备方案、贡献友好度均达到较好水平。继续保持并定期扫描。")
    else:
        print_pass("人维优秀：项目具备很强的社区韧性。考虑将这套治理模板推广到其他项目。")
    print()

    print("-" * 60)
    print("💡 建议：将本脚本集成到CI中，每月自动扫描一次。")
    print("   人维得分变化趋势比单次得分更重要——持续改善才是目标。")
    print("-" * 60)
    print()

    pass_count = sum(1 for it in result.items if it.passed)
    warn_count = sum(1 for it in result.items if not it.passed and it.actual_score > 0)
    error_count = sum(1 for it in result.items if it.actual_score == 0)
    if not result.doc_status.get("maintainers", False):
        error_count += 1
    if not result.doc_status.get("busfactor", False):
        error_count += 1
    if not result.doc_status.get("contributing", False):
        error_count += 1

    print_summary(pass_count, warn_count, error_count)


def result_to_json(result: PeopleDimensionResult) -> dict:
    """转换为JSON可序列化字典。"""
    return {
        "total_score": result.total_score,
        "total_level": result.total_level,
        "total_level_cn": _level_cn(result.total_level),
        "bus_factor": result.bus_factor,
        "category_scores": result.category_scores,
        "doc_status": result.doc_status,
        "items": [
            {
                "id": it.id,
                "category": it.category,
                "name": it.name,
                "max_score": it.max_score,
                "actual_score": it.actual_score,
                "passed": it.passed,
                "detail": it.detail,
            }
            for it in result.items
        ],
        "warnings": result.warnings,
        "strengths": result.strengths,
    }


# ── 主入口 ────────────────────────────────────────────────

def main() -> None:
    setup_safe_output()

    parser = argparse.ArgumentParser(
        description="人维·关系冗余自动化扫描工具 - 扫描治理文档评估Bus Factor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python .agents/scripts/check-busfactor.py                    # 扫描当前仓库
  python .agents/scripts/check-busfactor.py --json             # JSON输出（CI集成）
  python .agents/scripts/check-busfactor.py --repo-root /path/to/repo  # 指定路径
        """,
    )
    add_common_args(parser)
    parser.add_argument(
        "--repo-root",
        type=str,
        default=None,
        help="仓库根目录路径（默认为脚本所在仓库根目录）",
    )

    args = parser.parse_args()

    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
    else:
        # 默认：脚本在 .agents/scripts/ 下，仓库根目录是上三级
        repo_root = Path(__file__).resolve().parent.parent.parent

    result = scan_repo(repo_root)

    if args.json:
        print(json.dumps(result_to_json(result), ensure_ascii=False, indent=2))
    else:
        print_report(result, repo_root)


if __name__ == "__main__":
    main()
