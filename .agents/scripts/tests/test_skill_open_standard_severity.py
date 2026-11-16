# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

"""开放标准检查的严重度契约测试。

对应缺陷：
    checks_open_standard 的 trigger_hint 检查原写作
    `severity="info" if has_trigger else "info"`——三元两分支相同，
    导致「未通过」时产出 severity=info，而渲染层只输出 error/warn，
    该检查自诞生起从未在输出里出现过，只在评分上静默扣 1 分。

修复：失败分支改为 warn；本测试锁定该契约，并加一条不变式防止同类
「恒真三元」在其他检查项复发。
"""

from pathlib import Path

from lib.check_skill_quality.checks_open_standard import check_open_standards_compliance

FILLER = "。" * 60


def _run(tmp_path: Path, name: str, desc: str):
    skill_dir = tmp_path / name
    skill_dir.mkdir()
    skill_md = skill_dir / "SKILL.md"
    content = f"---\nname: {name}\ndescription: {desc}\n---\n\n# {name}\n"
    skill_md.write_text(content, encoding="utf-8")
    frontmatter = f"name: {name}\ndescription: {desc}\n"
    return check_open_standards_compliance(skill_md, content, frontmatter)


def _find(results, check_name):
    matched = [r for r in results if r.name == check_name]
    assert matched, f"未产出检查项 {check_name}"
    return matched[0]


def test_trigger_hint_missing_is_warn(tmp_path: Path) -> None:
    """缺少触发时机说明时必须为 warn（而非被静默丢弃的 info）。"""
    results = _run(tmp_path, "demo-skill", f"处理文档转换的辅助技能{FILLER}")
    r = _find(results, "open_standard.description.trigger_hint")
    assert r.passed is False
    assert r.severity == "warn"


def test_trigger_hint_present_is_info(tmp_path: Path) -> None:
    """包含触发时机说明时通过，严重度降为 info。"""
    results = _run(tmp_path, "demo-skill", f"Use when 用户需要转换文档{FILLER}")
    r = _find(results, "open_standard.description.trigger_hint")
    assert r.passed is True
    assert r.severity == "info"


def test_no_failed_result_uses_unrendered_severity(tmp_path: Path) -> None:
    """不变式：失败的检查项不得使用 error/warn 之外的严重度。

    渲染层（print_result_lines）只输出 error 与 warn，其它取值会被丢弃；
    此断言防止「恒真三元」在新增检查项里再次出现。
    """
    results = _run(tmp_path, "demo-skill", f"处理文档转换的辅助技能{FILLER}")
    bad = [r.name for r in results if not r.passed and r.severity not in ("error", "warn")]
    assert bad == [], f"以下失败项使用了不会被渲染的严重度：{bad}"
