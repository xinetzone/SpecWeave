"""对抗式健壮知识库安全工具库。

提供知识库文件的路径安全验证、输入验证、安全读写等核心能力，
防止路径遍历攻击、恶意输入、文件注入等安全风险。
"""

import logging
import re
from pathlib import Path

from .frontmatter import split_frontmatter_and_content
from .knowledge_classification import (
    VALID_KNOWLEDGE_TYPES,
    VALID_VALIDATION_STATUSES,
    validate_knowledge_type,
    validate_validation_status,
)
from .knowledge_integrity import (
    compute_checksum,
    verify_integrity,
    update_integrity,
    try_repair_from_git,
    extract_readable_content,
)

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "docs" / "knowledge"
SECURITY_LEVELS = ["public", "internal", "confidential"]
KNOWLEDGE_TYPES = ["factual", "procedural", "conditional", "metacognitive"]
DEFAULT_MAX_FILE_SIZE_MB = 5

_FILENAME_SANITIZE_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def safe_resolve_path(base_dir: str | Path, user_path: str | Path) -> Path:
    """安全解析路径，防止路径遍历攻击。

    确保解析后的绝对路径位于 base_dir 目录内，阻止 ../ 等路径遍历尝试。

    Args:
        base_dir: 基础目录（知识库根目录）。
        user_path: 用户提供的相对或绝对路径。

    Returns:
        解析后的安全绝对路径。

    Raises:
        ValueError: 当路径解析后位于 base_dir 之外时抛出。
    """
    base = Path(base_dir).resolve()
    target = (base / user_path).resolve()

    try:
        target.relative_to(base)
    except ValueError:
        raise ValueError(
            f"路径遍历攻击检测: {user_path} 解析后位于允许目录 {base_dir} 之外"
        )

    return target


class InputValidator:
    """输入验证器，提供文件大小、字符串、文件名等安全验证方法。"""

    @staticmethod
    def validate_file_size(file_path: str | Path, max_size_mb: int = DEFAULT_MAX_FILE_SIZE_MB) -> tuple[bool, str]:
        """验证文件大小是否在允许范围内。

        Args:
            file_path: 文件路径。
            max_size_mb: 最大允许大小（MB），默认5MB。

        Returns:
            (is_valid, error_msg) 元组，验证通过时 error_msg 为空字符串。
        """
        path = Path(file_path)
        max_bytes = max_size_mb * 1024 * 1024

        try:
            file_size = path.stat().st_size
        except OSError as e:
            return False, f"无法获取文件大小: {e}"

        if file_size > max_bytes:
            return False, f"文件大小 {file_size / 1024 / 1024:.2f}MB 超过限制 {max_size_mb}MB"

        return True, ""

    @staticmethod
    def validate_string_input(
        value: str,
        max_length: int = 10000,
        field_name: str = "input"
    ) -> tuple[bool, str]:
        """验证字符串输入的安全性。

        检查字符串长度、控制字符等潜在风险。

        Args:
            value: 待验证的字符串。
            max_length: 最大允许长度，默认10000字符。
            field_name: 字段名称，用于错误提示。

        Returns:
            (is_valid, error_msg) 元组，验证通过时 error_msg 为空字符串。
        """
        if not isinstance(value, str):
            return False, f"{field_name} 必须是字符串类型"

        if len(value) > max_length:
            return False, f"{field_name} 长度 {len(value)} 超过限制 {max_length}"

        if '\x00' in value:
            return False, f"{field_name} 包含空字节字符，可能存在注入风险"

        return True, ""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理文件名中的危险字符。

        移除或替换文件名中可能导致问题的特殊字符。

        Args:
            filename: 原始文件名。

        Returns:
            清理后的安全文件名。
        """
        sanitized = _FILENAME_SANITIZE_RE.sub('_', filename)
        sanitized = sanitized.strip('. ')
        if not sanitized:
            sanitized = "unnamed"
        return sanitized[:255]


def _apply_default_metadata(metadata: dict[str, str | list[str]] | None) -> dict[str, str | list[str]]:
    """为旧格式知识条目补全默认安全字段与分类字段。

    补全字段：
    - security_level: 默认 public，无效值回退为 internal
    - integrity: 默认 unchecked
    - knowledge_type: 默认 factual，无效值回退为 factual
    - validation_status: 默认 draft
    - reuse_count: 默认 "0"

    Args:
        metadata: 原始元数据字典，可能为 None。

    Returns:
        补全默认值后的元数据字典（不修改原输入）。
    """
    result = dict(metadata) if metadata else {}

    if 'security_level' not in result:
        result['security_level'] = 'public'
    elif result['security_level'] not in SECURITY_LEVELS:
        result['security_level'] = 'internal'

    if 'integrity' not in result:
        result['integrity'] = 'unchecked'

    if 'knowledge_type' not in result:
        result['knowledge_type'] = 'factual'
    elif result['knowledge_type'] not in KNOWLEDGE_TYPES:
        result['knowledge_type'] = 'factual'

    if 'validation_status' not in result:
        result['validation_status'] = 'draft'
    elif str(result['validation_status']) not in VALID_VALIDATION_STATUSES:
        result['validation_status'] = 'draft'

    if 'reuse_count' not in result:
        result['reuse_count'] = '0'

    return result


def read_knowledge_entry(
    file_path: str | Path,
    knowledge_base_dir: str | Path,
    *,
    auto_repair: bool = True,
) -> tuple[dict[str, str | list[str]], str, bool, str, bool, str]:
    """安全读取知识条目文件，含完整性自校验与自动修复。

    读取流程：路径安全验证 → 文件检查 → 编码检测 → frontmatter 解析 →
    默认值补全 → 完整性校验 → 损坏时 Git 修复/优雅降级。

    Args:
        file_path: 知识条目文件路径（相对于 knowledge_base_dir 或绝对路径）。
        knowledge_base_dir: 知识库根目录。
        auto_repair: 是否在校验失败时自动尝试修复，默认 True。

    Returns:
        (metadata, content, is_valid, error_msg, integrity_valid, integrity_msg) 元组：
        - metadata: 解析并补全默认值后的元数据字典
        - content: 文件正文内容（不含 frontmatter）
        - is_valid: 文件读取是否成功
        - error_msg: 读取错误信息，成功时为空字符串
        - integrity_valid: 完整性校验是否通过（未设校验和视为通过）
        - integrity_msg: 完整性校验/修复信息
    """
    try:
        safe_path = safe_resolve_path(knowledge_base_dir, file_path)
    except ValueError as e:
        return {}, "", False, str(e), False, ""

    if not safe_path.exists():
        return {}, "", False, f"文件不存在: {safe_path}", False, ""

    if not safe_path.is_file():
        return {}, "", False, f"路径不是文件: {safe_path}", False, ""

    size_valid, size_err = InputValidator.validate_file_size(safe_path)
    if not size_valid:
        return {}, "", False, size_err, False, ""

    try:
        raw_content = safe_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            raw_content = safe_path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            return {}, "", False, f"文件编码错误，仅支持 UTF-8: {safe_path}", False, ""
    except OSError as e:
        return {}, "", False, f"读取文件失败: {e}", False, ""

    metadata, content = split_frontmatter_and_content(raw_content, base_dir=safe_path.parent)
    # split_frontmatter_and_content 返回的 content 带有 frontmatter `---` 与正文之间的
    # 空白行（\n\n），需去除前导换行符以匹配写入时的原始 content
    content = content.lstrip('\n')
    metadata = _apply_default_metadata(metadata)

    # —— 完整性校验 ——
    integ_valid, actual_checksum, integ_msg = verify_integrity(metadata, content)

    if not integ_valid and auto_repair:
        # 损毁检测：尝试 Git 恢复
        repaired, repaired_content, repair_msg = try_repair_from_git(safe_path)
        if repaired:
            # 从 Git 恢复的内容需要重新解析 frontmatter，去除前导换行符
            r_metadata, r_content = split_frontmatter_and_content(repaired_content, base_dir=safe_path.parent)
            r_content = r_content.lstrip('\n')
            r_metadata = _apply_default_metadata(r_metadata)
            r_metadata['integrity'] = compute_checksum(r_content)  # 更新校验和
            # 将恢复后的内容写回文件
            try:
                _write_raw_to_file(safe_path, r_metadata, r_content)
            except OSError:
                pass  # 写回失败不影响返回
            return r_metadata, r_content, True, "", True, repair_msg

        # Git 恢复失败，尝试优雅降级
        degraded_content, degraded_fm, damage_report = extract_readable_content(raw_content)
        if degraded_content:
            metadata['integrity'] = 'damaged'
            return metadata, degraded_content, True, "", False, f"完整性校验失败: {integ_msg} | 优雅降级: {damage_report}"

        return metadata, content, True, "", False, integ_msg

    return metadata, content, True, "", integ_valid, integ_msg


def _escape_yaml_string(value: str) -> str:
    """转义字符串值用于 YAML 双引号包裹。

    处理反斜杠和双引号的转义，确保字符串在 YAML 双引号中被正确解析。

    Args:
        value: 原始字符串值。

    Returns:
        转义后的字符串（不含外层双引号）。
    """
    return str(value).replace('\\', '\\\\').replace('"', '\\"')


def _serialize_yaml_frontmatter(metadata: dict[str, str | list[str]]) -> str:
    """将元数据字典序列化为标准 YAML frontmatter 格式。

    简单 YAML 序列化实现（不引入 PyYAML 依赖）：
    - 字符串值统一用双引号包裹，内部双引号转义为 \\"，反斜杠转义为 \\\\
    - 列表序列化为行内流格式 [item1, item2]，各项也用双引号包裹并转义
    - 布尔值和数字保持裸格式（不加引号）
    注意：此实现仅支持标量和行内列表，不支持块级 YAML 结构（多行字符串、嵌套对象等）。
    含特殊字符（冒号、井号、换行等）的字符串由双引号包裹保证正确性。

    Args:
        metadata: 元数据字典。

    Returns:
        YAML frontmatter 字符串（包含 --- 标记）。
    """
    lines = ["---"]
    for key, value in metadata.items():
        if isinstance(value, list):
            items = ', '.join(f'"{_escape_yaml_string(item)}"' for item in value)
            lines.append(f"{key}: [{items}]")
        elif isinstance(value, bool):
            lines.append(f"{key}: {str(value).lower()}")
        elif isinstance(value, (int, float)):
            lines.append(f"{key}: {value}")
        else:
            escaped_value = _escape_yaml_string(value)
            lines.append(f'{key}: "{escaped_value}"')
    lines.append("---")
    return '\n'.join(lines)


def _write_raw_to_file(
    safe_path: Path,
    metadata: dict[str, str | list[str]],
    content: str
) -> None:
    """将元数据和内容序列化写入文件（内部辅助函数）。

    不执行输入验证，仅用于 integrity 修复流程中的写回操作。

    Args:
        safe_path: 已验证安全的文件路径。
        metadata: 元数据字典。
        content: 正文内容。

    Raises:
        OSError: 写入失败时抛出。
    """
    frontmatter_str = _serialize_yaml_frontmatter(metadata)
    full_content = f"{frontmatter_str}\n\n{content}"
    safe_path.parent.mkdir(parents=True, exist_ok=True)
    safe_path.write_text(full_content, encoding="utf-8")


def write_knowledge_entry(
    file_path: str | Path,
    metadata: dict[str, str | list[str]],
    content: str,
    knowledge_base_dir: str | Path
) -> tuple[bool, str]:
    """安全写入知识条目文件，自动计算 integrity 校验和。

    写入流程：输入验证 → 默认值补全 → integrity 校验和计算 →
    frontmatter 序列化 → 文件大小检查 → 安全写入。

    Args:
        file_path: 知识条目文件路径（相对于 knowledge_base_dir 或绝对路径）。
        metadata: 元数据字典。
        content: 文件正文内容。
        knowledge_base_dir: 知识库根目录。

    Returns:
        (is_valid, error_msg) 元组，写入成功时 error_msg 为空字符串。
    """
    try:
        safe_path = safe_resolve_path(knowledge_base_dir, file_path)
    except ValueError as e:
        return False, str(e)

    content_valid, content_err = InputValidator.validate_string_input(content, field_name="content")
    if not content_valid:
        return False, content_err

    for key, value in metadata.items():
        if isinstance(value, str):
            val_valid, val_err = InputValidator.validate_string_input(
                value, max_length=1000, field_name=f"metadata.{key}"
            )
            if not val_valid:
                return False, val_err

    safe_metadata = _apply_default_metadata(metadata)
    # 自动计算 integrity 校验和
    safe_metadata = update_integrity(safe_metadata, content)

    frontmatter_str = _serialize_yaml_frontmatter(safe_metadata)
    full_content = f"{frontmatter_str}\n\n{content}"

    if len(full_content.encode('utf-8')) > DEFAULT_MAX_FILE_SIZE_MB * 1024 * 1024:
        return False, f"写入后文件大小超过 {DEFAULT_MAX_FILE_SIZE_MB}MB 限制"

    try:
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_text(full_content, encoding="utf-8")
    except OSError as e:
        return False, f"写入文件失败: {e}"

    return True, ""
