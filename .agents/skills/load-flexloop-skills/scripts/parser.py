"""技能 Frontmatter 解析与验证模块。

提供单个 SKILL.md 文件解析和批量技能扫描功能，
支持严格/宽松两种验证模式，检查必填字段和推荐章节。
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Literal

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent.parent.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
if str(_PROJECT_ROOT / ".agents" / "scripts") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / ".agents" / "scripts"))

from lib.frontmatter import split_frontmatter_and_content

from models import SkillMetadata, SkillStatus, ScanError, ScanResult
from discovery import discover_skill_files, DEFAULT_SCAN_DIRS

ValidationMode = Literal["strict", "relaxed"]

_RECOMMENDED_SECTIONS: list[tuple[str, list[str]]] = [
    ("输入/参数", ["Input", "输入", "I/O", "参数"]),
    ("依赖", ["Dependencies", "依赖"]),
    ("部署/安装", ["Deployment", "部署", "安装"]),
    ("错误处理", ["Error Handling", "错误"]),
    ("版本记录", ["Changelog", "版本记录", "变更"]),
]


def _check_recommended_sections(body: str) -> list[str]:
    """检查正文中是否包含推荐章节标题。

    Args:
        body: SKILL.md 正文内容（不含 frontmatter）。

    Returns:
        缺失的推荐章节描述列表。
    """
    issues: list[str] = []
    body_lower = body.lower()

    for section_name, keywords in _RECOMMENDED_SECTIONS:
        found = False
        for kw in keywords:
            if kw.lower() in body_lower:
                found = True
                break
        if not found:
            issues.append(f"缺少推荐章节：{section_name}")

    return issues


def parse_skill_file(
    skill_path: Path,
    source: str,
    project_root: Path,
    mode: ValidationMode = "strict",
) -> tuple[SkillMetadata | None, list[ScanError]]:
    """解析单个 SKILL.md 文件并验证元数据。

    Args:
        skill_path: SKILL.md 文件绝对路径。
        source: 技能来源标记（"vendor" 或 "local"）。
        project_root: 项目根目录路径。
        mode: 验证模式，"strict" 检查推荐章节，"relaxed" 不检查。

    Returns:
        (SkillMetadata 对象或 None, 错误列表) 元组。
    """
    errors: list[ScanError] = []
    file_path_str = str(skill_path)

    try:
        content = skill_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        errors.append(ScanError(
            file_path=file_path_str,
            error_type="unicode_decode_error",
            message=f"文件编码错误: {e}",
            suggestion="请确保文件使用 UTF-8 编码",
        ))
        return None, errors
    except OSError as e:
        errors.append(ScanError(
            file_path=file_path_str,
            error_type="io_error",
            message=f"读取文件失败: {e}",
            suggestion="检查文件是否存在且可读",
        ))
        return None, errors
    except Exception as e:
        errors.append(ScanError(
            file_path=file_path_str,
            error_type="unknown_error",
            message=f"未知错误: {e}",
            suggestion="检查文件格式是否正确",
        ))
        return None, errors

    try:
        metadata, body = split_frontmatter_and_content(content, base_dir=skill_path.parent)
    except Exception as e:
        errors.append(ScanError(
            file_path=file_path_str,
            error_type="parse_error",
            message=f"解析 frontmatter 失败: {e}",
            suggestion="检查 YAML/TOML frontmatter 语法是否正确",
        ))
        return None, errors

    if metadata is None:
        errors.append(ScanError(
            file_path=file_path_str,
            error_type="missing_frontmatter",
            message="缺少 YAML frontmatter",
            suggestion="添加 YAML frontmatter（--- 包裹）",
        ))
        return None, errors

    name = metadata.get("name")
    if not name or not isinstance(name, str) or not name.strip():
        errors.append(ScanError(
            file_path=file_path_str,
            error_type="missing_name",
            message="frontmatter 中缺少 name 字段或 name 为空",
            suggestion="在 frontmatter 中添加 name 字段，如: name: skill-name",
        ))
        name = name if isinstance(name, str) else ""

    description = metadata.get("description", "")
    if not isinstance(description, str):
        description = str(description)
    version = metadata.get("version", "")
    if not isinstance(version, str):
        version = str(version)

    raw_metadata = {k: v for k, v in metadata.items() if k not in ("name", "description", "version")}

    try:
        rel_path = skill_path.relative_to(project_root).as_posix()
    except ValueError:
        rel_path = str(skill_path)

    status = SkillStatus.OK
    issues: list[str] = []

    if errors and any(e.error_type == "missing_name" for e in errors):
        status = SkillStatus.ERROR

    if mode == "strict" and name and name.strip():
        section_issues = _check_recommended_sections(body)
        issues.extend(section_issues)
        if section_issues:
            status = SkillStatus.WARNING

    skill_meta = SkillMetadata(
        name=name.strip() if isinstance(name, str) else "",
        skill_path=rel_path,
        source=source,
        description=description.strip(),
        version=version.strip(),
        status=status,
        issues=issues,
        raw_metadata=raw_metadata,
    )

    return skill_meta, errors


def parse_all_skills(
    project_root: Path,
    extra_dirs: list[str] | None = None,
    mode: ValidationMode = "strict",
    verbose: bool = False,
) -> ScanResult:
    """扫描并解析项目中所有技能文件。

    Args:
        project_root: 项目根目录路径。
        extra_dirs: 用户额外指定的扫描目录列表（相对于 project_root）。
        mode: 验证模式，"strict" 或 "relaxed"。
        verbose: 是否输出详细进度信息。

    Returns:
        ScanResult 对象，包含所有技能、错误和冲突信息。
    """
    project_root = project_root.resolve()
    result = ScanResult()
    result.scan_time = datetime.now().isoformat()

    scan_dirs: list[str] = [d for d, _ in DEFAULT_SCAN_DIRS]
    if extra_dirs:
        scan_dirs.extend(extra_dirs)
    result.scan_dirs = scan_dirs

    skill_files = discover_skill_files(project_root, extra_dirs=extra_dirs)

    if verbose:
        print(f"发现 {len(skill_files)} 个技能文件")

    name_counts: dict[str, int] = {}
    skills_by_name: dict[str, list[SkillMetadata]] = {}

    for skill_path, source in skill_files:
        if verbose:
            print(f"  解析: {skill_path}")

        skill_meta, errors = parse_skill_file(
            skill_path=skill_path,
            source=source,
            project_root=project_root,
            mode=mode,
        )

        result.errors.extend(errors)

        if skill_meta is not None:
            result.skills.append(skill_meta)
            name = skill_meta.name
            if name:
                name_counts[name] = name_counts.get(name, 0) + 1
                if name not in skills_by_name:
                    skills_by_name[name] = []
                skills_by_name[name].append(skill_meta)

    for name, count in name_counts.items():
        if count > 1:
            conflict_skills = [s.skill_path for s in skills_by_name[name]]
            result.conflicts.append({
                "name": name,
                "count": count,
                "files": conflict_skills,
            })

    return result
