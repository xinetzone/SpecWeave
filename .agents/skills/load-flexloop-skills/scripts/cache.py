"""增量扫描缓存模块。

提供基于文件 mtime 和 size 的增量扫描缓存机制，
避免重复解析未变更的 SKILL.md 文件，提升扫描速度。
"""

from __future__ import annotations

import json
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

from models import SkillMetadata, SkillStatus, ScanError, ScanResult
from parser import parse_skill_file, ValidationMode
from discovery import discover_skill_files, DEFAULT_SCAN_DIRS

CACHE_VERSION = "1.0"
DEFAULT_CACHE_RELPATH = ".agents/skills/load-flexloop-skills/.scan-cache.json"
_MTIME_EPSILON = 1.0


def _skill_from_dict(data: dict) -> SkillMetadata:
    return SkillMetadata(
        name=data["name"],
        skill_path=data["skill_path"],
        source=data["source"],
        description=data.get("description", ""),
        version=data.get("version", ""),
        status=SkillStatus(data.get("status", "ok")),
        issues=data.get("issues", []),
        raw_metadata=data.get("raw_metadata", {}),
    )


def _error_from_dict(data: dict) -> ScanError:
    return ScanError(
        file_path=data["file_path"],
        error_type=data["error_type"],
        message=data["message"],
        suggestion=data.get("suggestion", ""),
    )


def _get_rel_path(file_path: str, project_root: Path) -> str:
    p = Path(file_path)
    if p.is_absolute():
        try:
            return p.relative_to(project_root).as_posix()
        except ValueError:
            return file_path
    return file_path


def load_cache(cache_path: Path) -> dict | None:
    if not cache_path.exists():
        return None
    try:
        content = cache_path.read_text(encoding="utf-8")
        data = json.loads(content)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    if data.get("version") != CACHE_VERSION:
        return None
    return data


def save_cache(cache_path: Path, result: ScanResult, mode: str) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    files_cache: dict[str, dict] = {}
    for skill in result.skills:
        rel_path = skill.skill_path
        abs_path = _PROJECT_ROOT / rel_path
        try:
            stat = abs_path.stat()
            files_cache[rel_path] = {
                "mtime": stat.st_mtime,
                "size": stat.st_size,
                "skill": skill.to_dict(),
            }
        except OSError:
            continue

    cache_data = {
        "version": CACHE_VERSION,
        "scan_dirs": result.scan_dirs,
        "mode": mode,
        "files": files_cache,
        "errors": [e.to_dict() for e in result.errors],
    }

    cache_path.write_text(
        json.dumps(cache_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_cached_or_parse(
    project_root: Path,
    extra_dirs: list[str] | None = None,
    mode: ValidationMode = "strict",
    use_cache: bool = True,
    cache_path: Path | None = None,
    verbose: bool = False,
) -> ScanResult:
    project_root = project_root.resolve()

    if cache_path is None:
        cache_path = project_root / DEFAULT_CACHE_RELPATH

    if not use_cache:
        from parser import parse_all_skills
        return parse_all_skills(
            project_root=project_root,
            extra_dirs=extra_dirs,
            mode=mode,
            verbose=verbose,
        )

    result = ScanResult()
    result.scan_time = datetime.now().isoformat()

    scan_dirs: list[str] = [d for d, _ in DEFAULT_SCAN_DIRS]
    if extra_dirs:
        scan_dirs.extend(extra_dirs)
    result.scan_dirs = scan_dirs

    cached = load_cache(cache_path)
    skill_files = discover_skill_files(project_root, extra_dirs=extra_dirs)

    if verbose:
        print(f"发现 {len(skill_files)} 个技能文件")

    cached_files: dict[str, dict] = {}
    cached_mode = None
    cached_scan_dirs = None
    cached_errors: list[dict] = []
    if cached is not None:
        cached_files = cached.get("files", {})
        cached_mode = cached.get("mode")
        cached_scan_dirs = cached.get("scan_dirs")
        cached_errors = cached.get("errors", [])

    cache_invalid = (
        cached is None
        or cached_mode != mode
        or cached_scan_dirs != scan_dirs
    )

    current_rel_paths: set[str] = set()
    re_parsed_paths: set[str] = set()
    skills: list[SkillMetadata] = []
    all_errors: list[ScanError] = []
    cache_hit_count = 0
    cache_miss_count = 0
    need_save = cache_invalid

    for skill_path, source in skill_files:
        try:
            rel_path = skill_path.relative_to(project_root).as_posix()
        except ValueError:
            rel_path = str(skill_path)
        current_rel_paths.add(rel_path)

        use_cached = False
        if not cache_invalid and rel_path in cached_files:
            try:
                stat = skill_path.stat()
                cached_entry = cached_files[rel_path]
                cached_mtime = cached_entry.get("mtime", 0)
                cached_size = cached_entry.get("size", 0)
                if (
                    abs(stat.st_mtime - cached_mtime) < _MTIME_EPSILON
                    and stat.st_size == cached_size
                ):
                    use_cached = True
            except OSError:
                pass

        if use_cached:
            cached_entry = cached_files[rel_path]
            skill = _skill_from_dict(cached_entry["skill"])
            skills.append(skill)
            cache_hit_count += 1
            if verbose:
                print(f"  缓存命中: {rel_path}")
        else:
            re_parsed_paths.add(rel_path)
            if verbose:
                print(f"  解析: {rel_path}")
            skill_meta, parse_errors = parse_skill_file(
                skill_path=skill_path,
                source=source,
                project_root=project_root,
                mode=mode,
            )
            all_errors.extend(parse_errors)
            if skill_meta is not None:
                skills.append(skill_meta)
            cache_miss_count += 1
            need_save = True

    if cached is not None:
        cached_rel_paths = set(cached_files.keys())
        deleted_paths = cached_rel_paths - current_rel_paths
        if deleted_paths:
            need_save = True

        if not cache_invalid:
            for err_data in cached_errors:
                err_path = _get_rel_path(err_data.get("file_path", ""), project_root)
                if err_path not in re_parsed_paths and err_path in current_rel_paths:
                    all_errors.append(_error_from_dict(err_data))

    result.skills = skills
    result.errors = all_errors

    name_counts: dict[str, int] = {}
    skills_by_name: dict[str, list[SkillMetadata]] = {}
    for skill in skills:
        name = skill.name
        if name:
            name_counts[name] = name_counts.get(name, 0) + 1
            if name not in skills_by_name:
                skills_by_name[name] = []
            skills_by_name[name].append(skill)

    conflicts: list[dict] = []
    for name, count in name_counts.items():
        if count > 1:
            conflict_skills = [s.skill_path for s in skills_by_name[name]]
            conflicts.append({
                "name": name,
                "count": count,
                "files": conflict_skills,
            })
    result.conflicts = conflicts

    if need_save:
        save_cache(cache_path, result, mode)
        if verbose:
            print(f"缓存已更新: {cache_path}")
    elif verbose:
        print(f"缓存命中 {cache_hit_count}/{len(skill_files)} 个文件，无需更新缓存")

    return result
