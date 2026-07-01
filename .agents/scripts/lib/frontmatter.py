"""Frontmatter 解析工具。

提供从 Markdown 文件中提取 frontmatter 元数据并解析字段的通用能力。
支持两种格式：
  - TOML frontmatter（+++ ... +++），字段格式 key = "value"（已废弃，推荐使用 YAML+x-toml-ref）
  - YAML frontmatter（--- ... ---），字段格式 key: value，支持 x-toml-ref 引用外部 TOML 文件

新增统一入口：parse_frontmatter_unified() 自动识别格式、解析 x-toml-ref 外部引用并合并元数据。
"""

import logging
import re
import tomllib
import warnings
from pathlib import Path

logger = logging.getLogger(__name__)

_FRONTMATTER_RE = re.compile(
    r"^\+\+\+\s*\n(.*?)\n\+\+\+\s*$", re.MULTILINE | re.DOTALL
)

_YAML_FRONTMATTER_RE = re.compile(
    r"^---\s*\n(.*?)\n---\s*$", re.MULTILINE | re.DOTALL
)

_FIELD_RE = re.compile(r'^(\w+)\s*=\s*"([^"]*)"\s*$', re.MULTILINE)

_FIELD_RE_FULL = re.compile(
    r'^(\w+)\s*=\s*(?:"([^"]*)"|(\S+))\s*$', re.MULTILINE
)

_YAML_INLINE_LIST_RE = re.compile(r'^\[(.*)\]$')


def parse_toml_frontmatter(file_path: str | Path) -> str | None:
    """读取文件并返回 TOML frontmatter 内容（不含 +++ 标记）。

    Args:
        file_path: .md 文件路径。

    Returns:
        frontmatter 纯文本内容；无 frontmatter 或读取异常时返回 None。
    """
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    match = _FRONTMATTER_RE.match(content)
    if not match:
        return None

    return match.group(1)


def extract_frontmatter_field(
    frontmatter: str, field_name: str
) -> str | None:
    """从 frontmatter 文本中提取指定字段的值。

    支持的格式: field_name = "value" 和 field_name = unquoted_value

    Args:
        frontmatter: parse_toml_frontmatter 的返回值。
        field_name: 要提取的字段名（如 "id"、"tier"、"domain"、"validation_count"）。

    Returns:
        字段值字符串；未找到时返回 None。
    """
    pattern = re.compile(
        rf'^{re.escape(field_name)}\s*=\s*"([^"]*)"\s*$', re.MULTILINE
    )
    match = pattern.search(frontmatter)
    if match:
        return match.group(1)

    pattern = re.compile(
        rf'^{re.escape(field_name)}\s*=\s*(\S+)\s*$', re.MULTILINE
    )
    match = pattern.search(frontmatter)
    return match.group(1) if match else None


def extract_all_fields(frontmatter: str) -> dict[str, str]:
    """从 frontmatter 文本中提取所有字段（支持带引号和无引号值）。

    Args:
        frontmatter: parse_toml_frontmatter 的返回值。

    Returns:
        字段名到字段值的映射字典。
    """
    result = {}
    for match in _FIELD_RE_FULL.finditer(frontmatter):
        key = match.group(1)
        value = match.group(2) if match.group(2) is not None else match.group(3)
        result[key] = value
    return result


def parse_toml_frontmatter_as_dict(
    file_path: str | Path,
) -> dict[str, str] | None:
    """一步读取文件并解析 TOML frontmatter 为字段字典。

    便捷函数，等价于 ``parse_toml_frontmatter`` + ``extract_all_fields``。

    Args:
        file_path: .md 文件路径。

    Returns:
        字段名到字段值的映射字典；无 frontmatter 或读取异常时返回 None。
    """
    fm_text = parse_toml_frontmatter(file_path)
    if fm_text is None:
        return None
    return extract_all_fields(fm_text)


def parse_yaml_frontmatter(file_path: str | Path) -> str | None:
    """读取文件并返回 YAML frontmatter 内容（不含 --- 标记）。

    Args:
        file_path: .md 文件路径。

    Returns:
        frontmatter 纯文本内容；无 frontmatter 或读取异常时返回 None。
    """
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    match = _YAML_FRONTMATTER_RE.match(content)
    if not match:
        return None

    return match.group(1)


def extract_yaml_field(frontmatter: str, field_name: str) -> str | None:
    """从 YAML frontmatter 文本中提取指定字段的值。

    支持的值格式：
      - key: "value"（双引号标量）
      - key: 'value'（单引号标量）
      - key: value（无引号标量）
      - key: [a, b]（行内流列表，返回列表原文）
      - key:（块列表/块对象/块标量起始，返回空字符串表示字段存在但为非标量）

    块类型（列表/对象/多行标量）不解析具体内容，返回空字符串表示"字段存在"，
    适用于检查字段是否存在的场景（如frontmatter必填/推荐项校验）。

    Args:
        frontmatter: parse_yaml_frontmatter 的返回值。
        field_name: 要提取的字段名（如 "source"、"title"、"paths"）。

    Returns:
        字段值字符串；块类型字段返回空字符串 ""；未找到时返回 None。
    """
    block_pattern = re.compile(
        rf'^{re.escape(field_name)}[ \t]*:[ \t]*(?:[|>][ \t]*(?:#.*)?$|(?:#.*)?$)',
        re.MULTILINE,
    )
    if block_pattern.search(frontmatter):
        return ""

    scalar_pattern = re.compile(
        rf'^{re.escape(field_name)}[ \t]*:[ \t]*'
        r'(?:"([^"]*)"|\'([^\']*)\'|([^\n|>#][^\n]*?))(?:[ \t]+#.*)?[ \t]*$',
        re.MULTILINE,
    )
    match = scalar_pattern.search(frontmatter)
    if match:
        if match.group(1) is not None:
            return match.group(1).strip()
        if match.group(2) is not None:
            return match.group(2).strip()
        return match.group(3).strip()

    return None


def extract_frontmatter_field_from_file(
    file_path: str | Path, field_name: str
) -> str | None:
    """从 Markdown 文件中提取 frontmatter 字段值，自动识别 TOML/YAML 格式。

    依次尝试 TOML（+++ ... +++）和 YAML（--- ... ---）两种 frontmatter 格式。
    适用于扫描混合 frontmatter 格式的文档库（如 .agents/ 用 TOML、docs/knowledge/ 用 YAML）。

    Args:
        file_path: .md 文件路径。
        field_name: 要提取的字段名。

    Returns:
        字段值字符串；无 frontmatter 或未找到字段时返回 None。
    """
    toml_fm = parse_toml_frontmatter(file_path)
    if toml_fm is not None:
        value = extract_frontmatter_field(toml_fm, field_name)
        if value is not None:
            return value

    yaml_fm = parse_yaml_frontmatter(file_path)
    if yaml_fm is not None:
        return extract_yaml_field(yaml_fm, field_name)

    return None


def _parse_yaml_inline_list(value_str: str) -> list[str]:
    """解析 YAML 行内流列表 ["a", "b", 'c'] 为 Python 列表。

    Args:
        value_str: 方括号包裹的列表字符串。

    Returns:
        解析后的字符串列表。
    """
    inner = value_str.strip()[1:-1].strip()
    if not inner:
        return []

    items = []
    current = []
    in_double_quote = False
    in_single_quote = False

    for char in inner:
        if char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        elif char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == ',' and not in_double_quote and not in_single_quote:
            item = ''.join(current).strip()
            if (item.startswith('"') and item.endswith('"')) or \
               (item.startswith("'") and item.endswith("'")):
                item = item[1:-1]
            items.append(item)
            current = []
            continue
        current.append(char)

    if current:
        item = ''.join(current).strip()
        if (item.startswith('"') and item.endswith('"')) or \
           (item.startswith("'") and item.endswith("'")):
            item = item[1:-1]
        items.append(item)

    return items


def extract_all_yaml_fields(frontmatter_text: str) -> dict[str, str | list[str]]:
    """从 YAML frontmatter 文本提取所有字段为字典。

    支持：
      - key: "value"（双引号字符串）
      - key: 'value'（单引号字符串）
      - key: value（无引号标量：数字、布尔、纯字符串）
      - key: ["a", "b"]（行内流列表，解析为 Python 列表）
    块级 YAML（块列表、块对象）跳过不解析。

    Args:
        frontmatter_text: parse_yaml_frontmatter 返回的 YAML 文本。

    Returns:
        字段名到字段值的映射字典。
    """
    result: dict[str, str | list[str]] = {}

    for line in frontmatter_text.split('\n'):
        line = line.rstrip()
        if not line.strip() or line.strip().startswith('#'):
            continue

        if ':' not in line:
            continue

        colon_pos = line.find(':')
        key = line[:colon_pos].strip()
        value_part = line[colon_pos + 1:].strip()

        if not key:
            continue

        if not value_part:
            continue

        if value_part.startswith('#'):
            continue

        comment_pos = None
        in_dq = False
        in_sq = False
        for i, ch in enumerate(value_part):
            if ch == '"' and not in_sq:
                in_dq = not in_dq
            elif ch == "'" and not in_dq:
                in_sq = not in_sq
            elif ch == '#' and not in_dq and not in_sq:
                if i > 0 and value_part[i - 1] == ' ':
                    comment_pos = i
                    break

        if comment_pos is not None:
            value_part = value_part[:comment_pos].strip()

        if not value_part:
            continue

        if (value_part.startswith('"') and value_part.endswith('"')):
            result[key] = value_part[1:-1]
        elif (value_part.startswith("'") and value_part.endswith("'")):
            result[key] = value_part[1:-1]
        elif value_part.startswith('[') and value_part.endswith(']'):
            result[key] = _parse_yaml_inline_list(value_part)
        else:
            result[key] = value_part

    return result


def load_external_toml(toml_ref: str, base_dir: Path) -> dict[str, str | list[str]] | None:
    """加载并解析外部 TOML 文件。

    Args:
        toml_ref: x-toml-ref 的值，TOML 文件路径。
        base_dir: .md 文件所在目录（用于解析相对路径）。

    Returns:
        解析后的 TOML 字典（值为字符串或字符串列表）；失败时返回 None。
    """
    ref_path = toml_ref.replace('\\', '/')
    toml_path = (base_dir / ref_path).resolve()

    if not toml_path.exists():
        logger.warning(f"外部 TOML 文件不存在: {toml_path}")
        return None

    try:
        with open(toml_path, 'rb') as f:
            toml_data = tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError) as e:
        logger.warning(f"解析外部 TOML 文件失败 {toml_path}: {e}")
        return None

    result: dict[str, str | list[str]] = {}
    for key, value in toml_data.items():
        if isinstance(value, str):
            result[key] = value
        elif isinstance(value, bool):
            result[key] = str(value).lower()
        elif isinstance(value, (int, float)):
            result[key] = str(value)
        elif isinstance(value, list):
            result[key] = [str(item) for item in value]
        else:
            result[key] = str(value)

    return result


def merge_metadata(
    yaml_meta: dict[str, str | list[str]],
    toml_meta: dict[str, str | list[str]] | None,
) -> dict[str, str | list[str]]:
    """合并 YAML 和外部 TOML 元数据字典。

    YAML 字段优先级更高，覆盖 TOML 中的同名字段。

    Args:
        yaml_meta: YAML frontmatter 解析出的字段字典。
        toml_meta: 外部 TOML 文件解析出的字段字典，可以为 None。

    Returns:
        合并后的新字典（不修改输入参数）。
    """
    result: dict[str, str | list[str]] = {}

    if toml_meta:
        result.update(toml_meta)

    result.update(yaml_meta)

    return result


def parse_frontmatter_unified(
    file_path: str | Path,
) -> dict[str, str | list[str]] | None:
    """统一 frontmatter 解析入口，自动识别格式并处理 x-toml-ref。

    解析流程：
      1. 先检测 YAML(---) 格式，再检测 TOML(+++) 格式
      2. YAML 格式：解析所有字段，若存在 x-toml-ref 则加载外部 TOML 并合并（YAML 优先）
      3. TOML 格式：解析字段并发出 DeprecationWarning（提示迁移到 YAML+x-toml-ref）
      4. 无 frontmatter 返回 None

    Args:
        file_path: .md 文件路径。

    Returns:
        合并后的元数据字典；无 frontmatter 或读取失败时返回 None。
    """
    path = Path(file_path)

    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    yaml_match = _YAML_FRONTMATTER_RE.match(content)
    if yaml_match:
        yaml_text = yaml_match.group(1)
        yaml_meta = extract_all_yaml_fields(yaml_text)

        x_toml_ref = yaml_meta.get('x-toml-ref')
        if x_toml_ref and isinstance(x_toml_ref, str):
            toml_meta = load_external_toml(x_toml_ref, path.parent)
            return merge_metadata(yaml_meta, toml_meta)

        return yaml_meta

    toml_match = _FRONTMATTER_RE.match(content)
    if toml_match:
        warnings.warn(
            "TOML frontmatter (+++) 已废弃，请迁移到 YAML frontmatter (---) + x-toml-ref 引用外部 TOML",
            DeprecationWarning,
            stacklevel=2,
        )
        toml_text = toml_match.group(1)
        return extract_all_fields(toml_text)

    return None
