from pathlib import Path
from typing import Optional

from lib.rules import load_rules


def find_skill_files(root: Path, skills_dir: Path, target_path: Path | None = None) -> list[Path]:
    rules = load_rules()
    skill_files = []

    if target_path:
        target = target_path if target_path.is_file() else target_path / "SKILL.md"
        if target.exists():
            return [target]
        return []

    if not skills_dir.exists():
        return []

    for skill_md in skills_dir.rglob("SKILL.md"):
        should_skip, _ = rules.should_skip_file(skill_md, root_dir=root)
        if should_skip:
            continue
        if skill_md.name == "SKILL-TEMPLATE.md" or "SKILL-TEMPLATE" in str(skill_md):
            continue
        skill_files.append(skill_md)

    return sorted(skill_files)
