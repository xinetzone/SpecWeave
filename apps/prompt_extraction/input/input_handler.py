"""统一输入处理入口：支持单条文本输入和批量文件输入。"""

import uuid

from prompt_extraction.constants import ID_HEX_LENGTH
from prompt_extraction.input.parser import parse_file
from prompt_extraction.models import PromptRecord


def _generate_id() -> str:
    """生成唯一标识符。"""
    return uuid.uuid4().hex[:ID_HEX_LENGTH]


def process_single_input(text: str) -> PromptRecord:
    """接收单条文本，创建 PromptRecord 实例。

    Args:
        text: 单条提示词文本。

    Returns:
        包含原始文本和唯一标识的 PromptRecord 实例。

    Raises:
        ValueError: 文本为空时抛出。
    """
    if not text or not text.strip():
        raise ValueError("输入文本不能为空")
    return PromptRecord(id=_generate_id(), original_text=text.strip())


def process_batch_input(file_path: str) -> list[PromptRecord]:
    """调用解析器解析文件，为每条结果创建 PromptRecord。

    Args:
        file_path: 待解析的文件路径。

    Returns:
        PromptRecord 列表，每个元素对应文件中的一条提示词。

    Raises:
        ValueError: 文件解析失败时抛出。
    """
    parsed_items = parse_file(file_path)
    records: list[PromptRecord] = []
    for item in parsed_items:
        record = PromptRecord(
            id=item["id"],
            original_text=item["text"],
        )
        records.append(record)
    return records


def process_input(source: str, is_file: bool = False) -> list[PromptRecord]:
    """统一输入入口，根据 is_file 判断调用单条还是批量处理。

    Args:
        source: 输入来源。当 is_file=True 时为文件路径，否则为单条文本。
        is_file: 是否以文件模式处理。

    Returns:
        PromptRecord 列表。单条输入时列表长度为 1。

    Raises:
        ValueError: 输入无效时抛出。
    """
    if is_file:
        return process_batch_input(source)
    else:
        return [process_single_input(source)]