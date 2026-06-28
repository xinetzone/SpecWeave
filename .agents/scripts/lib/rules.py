"""误报过滤规则加载与应用工具。

从 .agents/scripts/config/false-positive-rules.toml 加载通用误报过滤规则，
提供路径排除、文件标记检测、块过滤、行过滤等能力，供所有 linter/checker 复用。

用法:
    from lib.rules import load_rules, FalsePositiveRules

    rules = load_rules()                    # 加载默认规则
    rules = load_rules(custom_path)         # 加载自定义路径规则

    if rules.should_exclude_path(path): ...
    if rules.is_excluded_file(path): ...
    if rules.is_excluded_block(lines): ...
    if rules.is_excluded_line(normalized_line): ...
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
DEFAULT_RULES_FILE = CONFIG_DIR / "false-positive-rules.toml"


@dataclass
class FileMarkerRule:
    """文件头标记规则：文件前N行包含任意pattern即排除。"""
    name: str
    patterns: list[str]
    scan_lines: int = 10
    match_all: bool = False
    min_matches: int = 1
    description: str = ""


@dataclass
class BlockFilterRule:
    """代码块过滤规则：块内行满足匹配条件则过滤。"""
    name: str
    patterns: list[re.Pattern]
    match_all: bool = True
    min_lines: int = 1
    min_matches: int = 1
    description: str = ""


@dataclass
class FalsePositiveRules:
    """误报过滤规则集合。"""

    excluded_dir_names: set[str] = field(default_factory=set)
    excluded_file_names: set[str] = field(default_factory=set)
    excluded_path_patterns: list[re.Pattern] = field(default_factory=list)
    file_marker_rules: list[FileMarkerRule] = field(default_factory=list)
    block_filter_rules: list[BlockFilterRule] = field(default_factory=list)
    line_filter_patterns: list[re.Pattern] = field(default_factory=list)

    def should_exclude_dir(self, dir_name: str) -> bool:
        """判断目录名是否应被排除。"""
        return dir_name in self.excluded_dir_names

    def should_exclude_file(self, file_name: str) -> bool:
        """判断文件名是否应被排除。"""
        return file_name in self.excluded_file_names

    def should_exclude_path(self, rel_path: str | Path) -> bool:
        """判断相对路径是否命中路径排除正则。"""
        path_str = str(rel_path).replace("\\", "/")
        return any(p.search(path_str) for p in self.excluded_path_patterns)

    def is_marked_file(self, file_path: Path) -> tuple[bool, str]:
        """判断文件是否被文件头标记规则排除。

        Returns:
            (is_excluded, matched_rule_description)
        """
        try:
            lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return False, ""

        for rule in self.file_marker_rules:
            head_text = "\n".join(lines[:rule.scan_lines])
            if rule.match_all:
                matched = all(p in head_text for p in rule.patterns)
            else:
                match_count = sum(1 for p in rule.patterns if p in head_text)
                matched = match_count >= rule.min_matches
            if matched:
                return True, rule.description
        return False, ""

    def is_excluded_line(self, normalized_line: str) -> bool:
        """判断归一化后的单行是否应被过滤。"""
        return any(p.search(normalized_line) for p in self.line_filter_patterns)

    def is_excluded_block(self, normalized_lines: list[str]) -> tuple[bool, str]:
        """判断归一化代码块是否应被过滤。

        Args:
            normalized_lines: 块内归一化代码行列表。

        Returns:
            (is_excluded, matched_rule_description)
        """
        if not normalized_lines:
            return False, ""

        for rule in self.block_filter_rules:
            if len(normalized_lines) < rule.min_lines:
                continue

            if rule.match_all:
                matched = all(
                    any(p.search(line) for p in rule.patterns)
                    for line in normalized_lines
                )
            else:
                match_count = sum(
                    1 for line in normalized_lines
                    if any(p.search(line) for p in rule.patterns)
                )
                matched = match_count >= rule.min_matches

            if matched:
                return True, rule.description

        return False, ""

    def filter_lines(self, normalized_lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
        """过滤归一化行列表中的排除行。

        Args:
            normalized_lines: (原始行号, 归一化内容) 列表。

        Returns:
            过滤后的列表。
        """
        return [
            (ln, norm) for ln, norm in normalized_lines
            if not self.is_excluded_line(norm)
        ]

    def should_skip_file(self, file_path: Path, root_dir: Path | None = None) -> tuple[bool, str]:
        """综合判断文件是否应被跳过（路径+文件名+标记三检查）。

        Args:
            file_path: 文件绝对路径。
            root_dir: 项目根目录（用于计算相对路径）。

        Returns:
            (should_skip, reason)
        """
        if self.should_exclude_file(file_path.name):
            return True, f"文件名排除: {file_path.name}"

        try:
            rel_parts = file_path.relative_to(root_dir).parts if root_dir else file_path.parts
        except ValueError:
            rel_parts = file_path.parts

        for part in rel_parts:
            if self.should_exclude_dir(part):
                return True, f"目录排除: {part}"

        if root_dir:
            try:
                rel_path = file_path.relative_to(root_dir)
                if self.should_exclude_path(rel_path):
                    return True, f"路径正则排除: {rel_path}"
            except ValueError:
                pass

        is_marked, reason = self.is_marked_file(file_path)
        if is_marked:
            return True, f"文件标记排除: {reason}"

        return False, ""


def _compile_patterns(patterns: list[str]) -> list[re.Pattern]:
    """编译正则表达式列表。"""
    return [re.compile(p, re.MULTILINE) for p in patterns]


def load_rules(rules_file: Path | str | None = None) -> FalsePositiveRules:
    """加载误报过滤规则。

    Args:
        rules_file: TOML规则文件路径，默认加载 config/false-positive-rules.toml。

    Returns:
        FalsePositiveRules 实例。
    """
    if rules_file is None:
        rules_file = DEFAULT_RULES_FILE
    else:
        rules_file = Path(rules_file)

    with open(rules_file, "rb") as f:
        data = tomllib.load(f)

    rules = FalsePositiveRules()

    path_exc = data.get("path_exclusions", {})
    rules.excluded_dir_names = set(path_exc.get("dir_names", []))
    rules.excluded_file_names = set(path_exc.get("file_names", []))
    rules.excluded_path_patterns = _compile_patterns(path_exc.get("path_patterns", []))

    for name, marker_data in data.get("file_markers", {}).items():
        rules.file_marker_rules.append(FileMarkerRule(
            name=name,
            patterns=marker_data.get("patterns", []),
            scan_lines=marker_data.get("scan_lines", 10),
            match_all=marker_data.get("match_all", False),
            min_matches=marker_data.get("min_matches", 1),
            description=marker_data.get("description", name),
        ))

    for name, block_data in data.get("block_filters", {}).items():
        rules.block_filter_rules.append(BlockFilterRule(
            name=name,
            patterns=_compile_patterns(block_data.get("patterns", [])),
            match_all=block_data.get("match_all", True),
            min_lines=block_data.get("min_lines", 1),
            min_matches=block_data.get("min_matches", 1),
            description=block_data.get("description", name),
        ))

    line_filters = data.get("line_filters", {})
    rules.line_filter_patterns = _compile_patterns(line_filters.get("patterns", []))

    return rules
