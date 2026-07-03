import logging
from pathlib import Path

from .constants import EXCLUDE_DIRS, TOML_FM_RE, YAML_FM_RE

logger = logging.getLogger(__name__)


def scan_files(root_path: Path, exclude_dirs: set[str] | None = None) -> list[Path]:
    """扫描所有 TOML frontmatter 文件（+++ 包裹）。

    Args:
        root_path: 扫描根目录。
        exclude_dirs: 需要排除的目录名集合。

    Returns:
        包含 TOML frontmatter 的 .md 文件路径列表（排序后）。
    """
    if exclude_dirs is None:
        exclude_dirs = EXCLUDE_DIRS

    toml_files = []
    for md_path in sorted(root_path.rglob("*.md")):
        rel_parts = md_path.relative_to(root_path).parts
        if any(part in exclude_dirs for part in rel_parts):
            continue

        try:
            content = md_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            logger.debug("跳过不可读文件: %s", md_path)
            continue

        if TOML_FM_RE.match(content):
            yaml_match = YAML_FM_RE.match(content)
            if yaml_match:
                yaml_text = yaml_match.group(1)
                if "x-toml-ref" in yaml_text:
                    logger.debug("跳过已迁移文件: %s", md_path)
                    continue
            toml_files.append(md_path)

    return toml_files
