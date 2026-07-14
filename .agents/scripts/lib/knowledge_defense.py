"""知识库异常输入防御与边界检查模块。

提供输入验证、资源消耗防护、错误处理框架等防御能力，
确保系统在异常输入下不崩溃、不OOM、不泄露敏感信息。

设计原则：
- 所有入口点验证输入，在数据进入核心逻辑前拦截
- 资源消耗有上限，防止恶意输入导致OOM或死循环
- 错误信息清晰但不泄露内部实现细节
- 防御深度：多层验证，不依赖单一检查点
"""

import logging
import re
import os
import sys
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

DEFAULT_MAX_FILE_SIZE_MB = 5
DEFAULT_MAX_CONTENT_LENGTH = 1_000_000  # 1MB 字符
DEFAULT_MAX_METADATA_FIELDS = 50
DEFAULT_MAX_TAG_LENGTH = 100
DEFAULT_MAX_TAGS_COUNT = 30
DEFAULT_MAX_FILENAME_LENGTH = 255
DEFAULT_MAX_PATH_DEPTH = 20
DEFAULT_MAX_RECURSION_DEPTH = 100

# 文件名安全字符集：字母、数字、连字符、下划线、点、中文
_FILENAME_SAFE_RE = re.compile(r'^[\w\-\.\u4e00-\u9fff]+$')

# 标签格式：字母、数字、连字符、下划线、中文
_TAG_FORMAT_RE = re.compile(r'^[\w\-\u4e00-\u9fff]+$')

# frontmatter 格式：检查 YAML 分隔符完整性
_FRONTMATTER_BOUNDARY_RE = re.compile(r'^---\s*\n.*?\n---', re.DOTALL)

# YAML 键名格式：字母、数字、下划线、连字符
_YAML_KEY_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_-]*$')


# ---------------------------------------------------------------------------
# 错误处理框架
# ---------------------------------------------------------------------------

class KnowledgeError(Exception):
    """知识库操作基础异常。

    所有知识库相关异常继承此类，提供统一的错误信息格式，
    不暴露内部栈追踪给调用方。
    """

    def __init__(self, message: str, code: str = "KNOWLEDGE_ERROR"):
        self.code = code
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"[{self.code}] {self.message}"


class ValidationError(KnowledgeError):
    """输入验证异常。"""
    def __init__(self, message: str, field: str = ""):
        self.field = field
        code = f"VALIDATION_ERROR"
        super().__init__(message, code)


class FileSizeError(KnowledgeError):
    """文件大小超限异常。"""
    def __init__(self, actual_bytes: int, max_bytes: int):
        self.actual_bytes = actual_bytes
        self.max_bytes = max_bytes
        message = (
            f"文件大小 {actual_bytes / 1024 / 1024:.2f}MB "
            f"超过限制 {max_bytes / 1024 / 1024:.0f}MB"
        )
        super().__init__(message, "FILE_SIZE_EXCEEDED")


class ResourceLimitError(KnowledgeError):
    """资源消耗超限异常。"""
    def __init__(self, resource: str, limit: Any, actual: Any):
        self.resource = resource
        self.limit = limit
        self.actual = actual
        message = f"{resource} 超过限制: 上限 {limit}, 实际 {actual}"
        super().__init__(message, "RESOURCE_LIMIT_EXCEEDED")


class FormatError(KnowledgeError):
    """格式错误异常。"""
    def __init__(self, message: str, detail: str = ""):
        self.detail = detail
        super().__init__(message, "FORMAT_ERROR")


def safe_call(
    func: Callable,
    *args,
    error_code: str = "OPERATION_FAILED",
    **kwargs,
) -> tuple[Any, KnowledgeError | None]:
    """安全调用包装器，捕获所有异常并转换为 KnowledgeError。

    确保任何异常都不会裸露栈追踪给调用方，所有错误都有清晰的
    错误码和用户可读的消息。

    Args:
        func: 要调用的函数。
        *args: 位置参数。
        error_code: 失败时的错误码。
        **kwargs: 关键字参数。

    Returns:
        (result, error) 元组，成功时 error 为 None。
    """
    try:
        return func(*args, **kwargs), None
    except KnowledgeError:
        raise
    except ValueError as e:
        return None, ValidationError(str(e), "value")
    except TypeError as e:
        return None, ValidationError(str(e), "type")
    except OSError as e:
        return None, KnowledgeError(f"文件操作失败: {e.strerror or str(e)}", "IO_ERROR")
    except RecursionError:
        return None, ResourceLimitError("递归深度", DEFAULT_MAX_RECURSION_DEPTH, "exceeded")
    except MemoryError:
        return None, ResourceLimitError("内存", "available", "exceeded")
    except Exception as e:
        logger.warning("Unexpected error in %s: %s", func.__name__, e)
        return None, KnowledgeError(f"操作失败: {type(e).__name__}", error_code)


# ---------------------------------------------------------------------------
# 输入验证器
# ---------------------------------------------------------------------------

class InputValidator:
    """输入验证器，提供全面的输入安全检查。"""

    # —— 文件大小 ——

    @staticmethod
    def validate_file_size(
        file_path: str | Path,
        max_size_mb: int = DEFAULT_MAX_FILE_SIZE_MB,
    ) -> tuple[bool, str]:
        """验证文件大小是否在允许范围内。

        先检查文件是否存在，再检查大小，避免读取超大文件导致OOM。
        """
        path = Path(file_path)
        max_bytes = max_size_mb * 1024 * 1024

        if not path.exists():
            return False, f"文件不存在: {path}"

        if not path.is_file():
            return False, f"路径不是普通文件: {path}"

        try:
            file_size = path.stat().st_size
        except OSError as e:
            return False, f"无法获取文件信息: {e.strerror or str(e)}"

        if file_size > max_bytes:
            return False, (
                f"文件大小 {file_size / 1024 / 1024:.2f}MB "
                f"超过限制 {max_size_mb}MB"
            )

        return True, ""

    # —— 字符串 ——

    @staticmethod
    def validate_string_input(
        value: str,
        max_length: int = DEFAULT_MAX_CONTENT_LENGTH,
        field_name: str = "input",
    ) -> tuple[bool, str]:
        """验证字符串输入的安全性。

        检查类型、长度、空字节等潜在风险。
        """
        if not isinstance(value, str):
            return False, f"{field_name} 必须是字符串类型，实际为 {type(value).__name__}"

        if len(value) > max_length:
            return False, (
                f"{field_name} 长度 {len(value)} 超过限制 {max_length}"
            )

        if '\x00' in value:
            return False, f"{field_name} 包含空字节字符，可能存在注入风险"

        if '\x1b' in value:
            return False, f"{field_name} 包含 ANSI 转义序列"

        return True, ""

    # —— 文件名 ——

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理文件名中的危险字符。

        移除 OS 特殊字符、控制字符，保留安全字符集。
        """
        # 移除 OS 危险字符
        dangerous = '<>:"/\\|?*'
        for ch in dangerous:
            filename = filename.replace(ch, '_')

        # 移除控制字符
        filename = ''.join(
            ch for ch in filename
            if ord(ch) >= 32 or ch in '\n\r\t'
        )

        filename = filename.strip('. ')
        if not filename:
            filename = "unnamed"
        return filename[:DEFAULT_MAX_FILENAME_LENGTH]

    @staticmethod
    def validate_filename(filename: str) -> tuple[bool, str]:
        """验证文件名格式是否安全。

        Args:
            filename: 文件名（不含路径）。

        Returns:
            (is_valid, error_msg) 元组。
        """
        if not filename:
            return False, "文件名不能为空"

        if len(filename) > DEFAULT_MAX_FILENAME_LENGTH:
            return False, f"文件名长度 {len(filename)} 超过限制 {DEFAULT_MAX_FILENAME_LENGTH}"

        if not _FILENAME_SAFE_RE.match(filename):
            return False, f"文件名包含非法字符: {filename}"

        # 检查是否以点开头（隐藏文件）
        if filename.startswith('.'):
            return False, f"文件名不能以点开头: {filename}"

        return True, ""

    # —— 路径 ——

    @staticmethod
    def validate_path_depth(relative_path: str | Path, max_depth: int = DEFAULT_MAX_PATH_DEPTH) -> tuple[bool, str]:
        """验证路径深度是否在允许范围内。

        防止深层嵌套目录导致遍历性能问题。
        """
        parts = Path(relative_path).parts
        depth = len(parts)
        if depth > max_depth:
            return False, f"路径深度 {depth} 超过限制 {max_depth}"
        return True, ""

    # —— 标签 ——

    @staticmethod
    def validate_tag(tag: str) -> tuple[bool, str]:
        """验证单个标签格式。

        Args:
            tag: 标签字符串。

        Returns:
            (is_valid, error_msg) 元组。
        """
        if not tag or not isinstance(tag, str):
            return False, f"标签不能为空且必须是字符串"

        if len(tag) > DEFAULT_MAX_TAG_LENGTH:
            return False, f"标签长度 {len(tag)} 超过限制 {DEFAULT_MAX_TAG_LENGTH}"

        if not _TAG_FORMAT_RE.match(tag):
            return False, f"标签包含非法字符: {tag}"

        return True, ""

    @staticmethod
    def validate_tags(tags: list[str]) -> tuple[bool, str]:
        """验证标签列表。

        Args:
            tags: 标签字符串列表。

        Returns:
            (is_valid, error_msg) 元组。
        """
        if not isinstance(tags, list):
            return False, "tags 必须是列表类型"

        if len(tags) > DEFAULT_MAX_TAGS_COUNT:
            return False, f"标签数量 {len(tags)} 超过限制 {DEFAULT_MAX_TAGS_COUNT}"

        for tag in tags:
            valid, err = InputValidator.validate_tag(tag)
            if not valid:
                return False, err

        return True, ""

    # —— Frontmatter ——

    @staticmethod
    def validate_frontmatter_format(content: str) -> tuple[bool, str]:
        """验证 frontmatter 格式完整性。

        检查 YAML frontmatter 分隔符是否成对出现，
        以及 frontmatter 区域大小是否合理。

        Args:
            content: 文件完整内容。

        Returns:
            (is_valid, error_msg) 元组。
        """
        if not content.strip():
            return True, ""  # 空文件无 frontmatter 是合法的

        lines = content.split('\n')

        # 检查 frontmatter 开始标记
        if lines and lines[0].strip() == '---':
            # 寻找结束标记
            end_idx = -1
            for i in range(1, min(len(lines), DEFAULT_MAX_METADATA_FIELDS + 5)):
                if lines[i].strip() == '---':
                    end_idx = i
                    break

            if end_idx == -1:
                return False, "frontmatter 缺少结束标记 ---"

            fm_size = len('\n'.join(lines[:end_idx + 1]))
            if fm_size > 100_000:  # 100KB frontmatter 不合理
                return False, f"frontmatter 大小 {fm_size} 字节超过限制"

            # 检查 frontmatter 内部的行数
            fm_lines = lines[1:end_idx]
            if len(fm_lines) > DEFAULT_MAX_METADATA_FIELDS:
                return False, (
                    f"frontmatter 字段数 {len(fm_lines)} "
                    f"超过限制 {DEFAULT_MAX_METADATA_FIELDS}"
                )

            # 验证每个键名
            for line in fm_lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' in line:
                    key = line.split(':', 1)[0].strip()
                    if key and not _YAML_KEY_RE.match(key):
                        return False, f"frontmatter 键名格式非法: {key}"

        return True, ""

    # —— 元数据 ——

    @staticmethod
    def validate_metadata(metadata: dict[str, str | list[str]]) -> tuple[bool, str]:
        """验证元数据字典的格式和大小。

        Args:
            metadata: 元数据字典。

        Returns:
            (is_valid, error_msg) 元组。
        """
        if not isinstance(metadata, dict):
            return False, "metadata 必须是字典类型"

        if len(metadata) > DEFAULT_MAX_METADATA_FIELDS:
            return False, (
                f"metadata 字段数 {len(metadata)} "
                f"超过限制 {DEFAULT_MAX_METADATA_FIELDS}"
            )

        for key, value in metadata.items():
            if not isinstance(key, str):
                return False, f"metadata 键必须是字符串，实际为 {type(key).__name__}"

            if not _YAML_KEY_RE.match(key):
                return False, f"metadata 键名格式非法: {key}"

            if isinstance(value, str) and len(value) > 10000:
                return False, f"metadata.{key} 值长度 {len(value)} 超过限制"

            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and len(item) > 1000:
                        return False, f"metadata.{key} 列表项长度超过限制"

        return True, ""


# ---------------------------------------------------------------------------
# 资源消耗防护
# ---------------------------------------------------------------------------

class ResourceGuard:
    """资源消耗防护器。

    在执行可能消耗大量资源的操作前检查限制，
    防止 OOM、死循环、递归爆炸等问题。
    """

    _recursion_depth = 0

    @staticmethod
    def check_content_size(
        content: str,
        max_chars: int = DEFAULT_MAX_CONTENT_LENGTH,
    ) -> tuple[bool, str]:
        """检查内容大小是否在安全范围内。

        在内存中处理前检查，防止 OOM。
        """
        if not isinstance(content, str):
            return False, f"内容必须是字符串类型"

        char_count = len(content)
        if char_count > max_chars:
            return False, (
                f"内容长度 {char_count} 字符超过限制 {max_chars} 字符"
            )

        byte_count = len(content.encode('utf-8'))
        max_bytes = DEFAULT_MAX_FILE_SIZE_MB * 1024 * 1024
        if byte_count > max_bytes:
            return False, (
                f"内容大小 {byte_count / 1024 / 1024:.2f}MB "
                f"超过限制 {DEFAULT_MAX_FILE_SIZE_MB}MB"
            )

        return True, ""

    @staticmethod
    def check_list_size(
        items: list,
        max_items: int = 10000,
        label: str = "列表",
    ) -> tuple[bool, str]:
        """检查列表大小是否在安全范围内。

        防止对超大列表进行遍历导致性能问题。
        """
        if not isinstance(items, (list, tuple)):
            return False, f"{label} 必须是列表或元组类型"

        if len(items) > max_items:
            return False, f"{label} 长度 {len(items)} 超过限制 {max_items}"

        return True, ""

    @staticmethod
    def enter_recursion(max_depth: int = DEFAULT_MAX_RECURSION_DEPTH) -> None:
        """进入递归层，检查深度限制。

        每次递归调用前调用此方法，防止递归爆炸。

        Raises:
            ResourceLimitError: 递归深度超限时抛出。
        """
        ResourceGuard._recursion_depth += 1
        if ResourceGuard._recursion_depth > max_depth:
            ResourceGuard._recursion_depth = 0
            raise ResourceLimitError(
                "递归深度", max_depth, ResourceGuard._recursion_depth
            )

    @staticmethod
    def exit_recursion() -> None:
        """退出递归层。"""
        ResourceGuard._recursion_depth = max(0, ResourceGuard._recursion_depth - 1)

    @staticmethod
    def check_iteration_count(
        current: int,
        max_iterations: int = 100000,
        label: str = "迭代",
    ) -> tuple[bool, str]:
        """检查迭代次数是否在安全范围内。

        防止死循环或无限迭代。
        """
        if current > max_iterations:
            return False, f"{label} 次数 {current} 超过限制 {max_iterations}"
        return True, ""


# ---------------------------------------------------------------------------
# 防御性入口包装器
# ---------------------------------------------------------------------------

def defensive_read(
    file_path: str | Path,
    max_size_mb: int = DEFAULT_MAX_FILE_SIZE_MB,
) -> tuple[str | None, KnowledgeError | None]:
    """防御性文件读取。

    在读取文件前进行多层检查：存在性、类型、大小、编码。

    Args:
        file_path: 文件路径。
        max_size_mb: 最大文件大小（MB）。

    Returns:
        (content, error) 元组，成功时 error 为 None。
    """
    path = Path(file_path)

    # 第1层：存在性与类型
    if not path.exists():
        return None, KnowledgeError(f"文件不存在: {path}", "FILE_NOT_FOUND")
    if not path.is_file():
        return None, KnowledgeError(f"路径不是文件: {path}", "NOT_A_FILE")

    # 第2层：文件大小
    size_valid, size_err = InputValidator.validate_file_size(path, max_size_mb)
    if not size_valid:
        return None, FileSizeError(
            path.stat().st_size, max_size_mb * 1024 * 1024
        )

    # 第3层：编码检测与读取
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            content = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError as e:
            return None, FormatError(
                f"文件编码错误，仅支持 UTF-8: {path.name}",
                detail=str(e),
            )
    except OSError as e:
        return None, KnowledgeError(
            f"读取文件失败: {e.strerror or str(e)}", "IO_ERROR"
        )

    # 第4层：内容大小
    size_valid, size_err = ResourceGuard.check_content_size(content)
    if not size_valid:
        return None, ResourceLimitError("内容", DEFAULT_MAX_CONTENT_LENGTH, len(content))

    return content, None


def validate_all_entry_points(
    metadata: dict[str, str | list[str]],
    content: str,
    file_path: str | Path,
) -> tuple[bool, str]:
    """多入口点综合验证。

    在一次调用中验证所有输入维度，返回第一个失败的错误。

    Args:
        metadata: 元数据字典。
        content: 正文内容。
        file_path: 文件路径。

    Returns:
        (is_valid, error_msg) 元组。
    """
    # 路径验证
    path = Path(file_path)
    if path.name:
        valid, err = InputValidator.validate_filename(path.name)
        if not valid:
            return False, err

        valid, err = InputValidator.validate_path_depth(path)
        if not valid:
            return False, err

    # 内容验证
    valid, err = InputValidator.validate_string_input(content, field_name="content")
    if not valid:
        return False, err

    # 元数据验证
    valid, err = InputValidator.validate_metadata(metadata)
    if not valid:
        return False, err

    # 标签验证
    tags = metadata.get("tags", [])
    if isinstance(tags, list):
        valid, err = InputValidator.validate_tags(tags)
        if not valid:
            return False, err

    return True, ""