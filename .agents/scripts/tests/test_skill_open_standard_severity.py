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

from lib.frontmatter import extract_yaml_field, extract_yaml_text_field
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


# --- 触发式写法覆盖（外部镜像技能的真实书写惯例） -------------------------


def _run_block(tmp_path: Path, name: str, indicator: str, body_lines: list[str]):
    """构造使用块标量写法的 SKILL.md。"""
    skill_dir = tmp_path / name
    skill_dir.mkdir()
    skill_md = skill_dir / "SKILL.md"
    body = "\n".join(f"  {line}" for line in body_lines)
    fmt = f"name: {name}\ndescription: {indicator}\n{body}\n"
    content = f"---\n{fmt}---\n\n# {name}\n"
    skill_md.write_text(content, encoding="utf-8")
    return skill_md, content, fmt


def test_extract_yaml_field_folded_scalar_returns_empty_not_marker() -> None:
    """回归：`description: >-` 曾被解析成字符串 '>-'（正则回溯把空格当值）。"""
    fm = "name: x\ndescription: >-\n  第一行\n  第二行\n"
    assert extract_yaml_field(fm, "description") == ""


def test_read_yaml_block_scalar_folds_lines() -> None:
    fm = "name: x\ndescription: >-\n  第一行\n  第二行\n"
    assert extract_yaml_text_field(fm, "description") == "第一行 第二行"


def test_folded_scalar_description_reaches_trigger_check(tmp_path: Path) -> None:
    """块标量描述必须被真实解析，否则整段描述检查会被静默跳过。"""
    md, content, fmt = _run_block(
        tmp_path, "demo-skill", ">-", ["搜索全网内容并获取热榜。", f"用户提到该需求时使用。{FILLER}"]
    )
    r = _find(check_open_standards_compliance(md, content, fmt), "open_standard.description.trigger_hint")
    assert r.passed is True


def test_english_triggers_on_phrase_accepted(tmp_path: Path) -> None:
    r = _find(
        _run(tmp_path, "demo-skill", f"Transcribe audio files to text. Triggers on: 转录, transcribe. {FILLER}"),
        "open_standard.description.trigger_hint",
    )
    assert r.passed is True


def test_capitalized_when_accepted(tmp_path: Path) -> None:
    """词表曾大小写敏感，`When you need...` 被漏检。"""
    r = _find(
        _run(tmp_path, "demo-skill", f"Comprehensive toolkit for documents. When you need to edit files, use it. {FILLER}"),
        "open_standard.description.trigger_hint",
    )
    assert r.passed is True


def test_chinese_applicable_phrase_accepted(tmp_path: Path) -> None:
    r = _find(
        _run(tmp_path, "demo-skill", f"企业数据查询工具，适用于主体核验与风险评估。{FILLER}"),
        "open_standard.description.trigger_hint",
    )
    assert r.passed is True


def test_capability_only_description_still_fails(tmp_path: Path) -> None:
    """守卫：只讲“能做什么”、不讲“何时用”的描述不得被放宽放行。"""
    r = _find(
        _run(tmp_path, "demo-skill", f"Use this skill to generate well-branded interfaces and assets for X. {FILLER}"),
        "open_standard.description.trigger_hint",
    )
    assert r.passed is False
    assert r.severity == "warn"


# --- 多行 plain 标量（无 |/> 指示符） ------------------------------------

def _run_plain_multiline(tmp_path: Path, name: str, body_lines: list[str]):
    """构造 description 为多行 plain 标量的 SKILL.md。

    YAML 允许 `description:` 换行后接缩进续行（不带 |/> 指示符）。外部镜像
    技能（如 vercel-composition-patterns）采用这种写法，而解析器曾把续行
    整体丢弃：description 被当作「字段存在但无文本」，既误报必需字段缺失，
    又让长度/触发时机等描述类检查全部静默跳过。
    """
    skill_dir = tmp_path / name
    skill_dir.mkdir()
    skill_md = skill_dir / "SKILL.md"
    body = "\n".join(f"  {line}" for line in body_lines)
    fmt = f"name: {name}\ndescription:\n{body}\n"
    content = f"---\n{fmt}---\n\n# {name}\n"
    skill_md.write_text(content, encoding="utf-8")
    return skill_md, content, fmt


def test_plain_multiline_description_reaches_trigger_check(tmp_path: Path) -> None:
    md, content, fmt = _run_plain_multiline(
        tmp_path,
        "demo-skill",
        [
            "React composition patterns that scale. Use when refactoring components",
            "with boolean prop proliferation, or building flexible component libraries.",
        ],
    )
    r = _find(
        check_open_standards_compliance(md, content, fmt),
        "open_standard.description.trigger_hint",
    )
    assert r.passed is True


def test_plain_multiline_description_counts_as_present(tmp_path: Path) -> None:
    """守卫：多行 plain 标量不得再被误判为「必需字段 description 缺失」。"""
    from lib.check_skill_quality.checks_frontmatter import check_frontmatter

    md, content, fmt = _run_plain_multiline(
        tmp_path, "demo-skill", ["Composition patterns for building React apps."]
    )
    r = _find(check_frontmatter(md, content, fmt), "frontmatter.description")
    assert r.passed is True


def test_frontmatter_module_reads_plain_multiline_scalar() -> None:
    from lib.frontmatter import extract_yaml_text_field

    fm = "name: x\ndescription:\n  第一行\n  第二行\n"
    assert extract_yaml_text_field(fm, "description") == "第一行 第二行"


# --- 外部镜像触发惯例（use for / use this skill for / MUST use） ---------


def test_use_for_phrase_accepted(tmp_path: Path) -> None:
    """`Use for <场景>` 是外部镜像的适用面写法，须识别为触发时机。"""
    r = _find(
        _run(tmp_path, "demo-skill", f"Generate static posters and banners. Use for campaign visuals. {FILLER}"),
        "open_standard.description.trigger_hint",
    )
    assert r.passed is True


def test_use_this_skill_for_phrase_accepted(tmp_path: Path) -> None:
    r = _find(
        _run(tmp_path, "demo-skill", f"Brand knowledge helper. Use this skill for identity questions. {FILLER}"),
        "open_standard.description.trigger_hint",
    )
    assert r.passed is True


def test_must_use_phrase_accepted(tmp_path: Path) -> None:
    r = _find(
        _run(tmp_path, "demo-skill", f"You MUST use this before any creative work. {FILLER}"),
        "open_standard.description.trigger_hint",
    )
    assert r.passed is True
