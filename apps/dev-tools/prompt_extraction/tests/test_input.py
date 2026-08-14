"""提示词输入模块单元测试。

测试覆盖：parser.py 各解析器、input_handler.py 处理逻辑，以及异常场景。
"""

import json
import os
import tempfile

import pytest

from prompt_extraction.input.parser import (
    detect_format,
    parse_csv,
    parse_file,
    parse_json,
    parse_markdown,
    parse_txt,
)
from prompt_extraction.input.input_handler import (
    process_batch_input,
    process_input,
    process_single_input,
)
from prompt_extraction.models import PromptRecord


# ============================================================
# 辅助函数
# ============================================================

def _write_temp_file(content: str, suffix: str) -> str:
    """创建临时文件并写入内容，返回文件路径。"""
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ============================================================
# detect_format 测试
# ============================================================

class TestDetectFormat:
    """检测文件格式测试。"""

    def test_csv_format(self):
        assert detect_format("test.csv") == "csv"

    def test_json_format(self):
        assert detect_format("test.json") == "json"

    def test_txt_format(self):
        assert detect_format("test.txt") == "txt"

    def test_md_format(self):
        assert detect_format("test.md") == "markdown"

    def test_markdown_format(self):
        assert detect_format("test.markdown") == "markdown"

    def test_unsupported_format(self):
        with pytest.raises(ValueError, match="不支持的文件格式"):
            detect_format("test.xml")

    def test_no_extension(self):
        with pytest.raises(ValueError, match="不支持的文件格式"):
            detect_format("testfile")


# ============================================================
# parse_csv 测试
# ============================================================

class TestParseCsv:
    """CSV 解析器测试。"""

    def test_normal_csv(self):
        content = "prompt,id\n写一首诗,001\n翻译一段文字,002\n"
        path = _write_temp_file(content, ".csv")
        try:
            result = parse_csv(path)
            assert len(result) == 2
            assert result[0]["text"] == "写一首诗"
            assert result[0]["id"] == "001"
            assert result[1]["text"] == "翻译一段文字"
            assert result[1]["id"] == "002"
        finally:
            os.unlink(path)

    def test_auto_detect_column(self):
        """自动检测提示词列：列名包含"内容"关键词。"""
        content = "序号,内容描述\n1,写一首诗\n2,翻译文字\n"
        path = _write_temp_file(content, ".csv")
        try:
            result = parse_csv(path)
            assert len(result) == 2
            assert result[0]["text"] == "写一首诗"
            assert result[1]["text"] == "翻译文字"
        finally:
            os.unlink(path)

    def test_empty_file(self):
        """空 CSV 文件应抛出 ValueError。"""
        content = "prompt,id\n"
        path = _write_temp_file(content, ".csv")
        try:
            with pytest.raises(ValueError, match="未找到有效的提示词内容"):
                parse_csv(path)
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        with pytest.raises(ValueError, match="文件不存在"):
            parse_csv("nonexistent.csv")

    def test_skip_empty_rows(self):
        """跳过空行，只保留有效行。"""
        content = "prompt,id\n写一首诗,001\n,\n翻译文字,002\n"
        path = _write_temp_file(content, ".csv")
        try:
            result = parse_csv(path)
            assert len(result) == 2
        finally:
            os.unlink(path)

    def test_auto_generate_id(self):
        """无 id 列时自动生成 ID。"""
        content = "prompt\n写一首诗\n翻译文字\n"
        path = _write_temp_file(content, ".csv")
        try:
            result = parse_csv(path)
            assert len(result) == 2
            assert len(result[0]["id"]) == 12
            assert result[0]["id"] != result[1]["id"]
        finally:
            os.unlink(path)


# ============================================================
# parse_json 测试
# ============================================================

class TestParseJson:
    """JSON 解析器测试。"""

    def test_normal_json(self):
        content = json.dumps([
            {"text": "写一首诗", "id": "001"},
            {"text": "翻译文字", "id": "002"},
        ])
        path = _write_temp_file(content, ".json")
        try:
            result = parse_json(path)
            assert len(result) == 2
            assert result[0]["text"] == "写一首诗"
            assert result[0]["id"] == "001"
            assert result[1]["text"] == "翻译文字"
            assert result[1]["id"] == "002"
        finally:
            os.unlink(path)

    def test_auto_detect_field(self):
        """自动检测提示词字段：字段名包含"内容"关键词。"""
        content = json.dumps([
            {"内容": "写一首诗"},
            {"内容": "翻译文字"},
        ])
        path = _write_temp_file(content, ".json")
        try:
            result = parse_json(path)
            assert len(result) == 2
            assert result[0]["text"] == "写一首诗"
        finally:
            os.unlink(path)

    def test_empty_array(self):
        """空数组应抛出 ValueError。"""
        content = "[]"
        path = _write_temp_file(content, ".json")
        try:
            with pytest.raises(ValueError, match="未找到有效的提示词内容"):
                parse_json(path)
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        with pytest.raises(ValueError, match="文件不存在"):
            parse_json("nonexistent.json")

    def test_invalid_json(self):
        """无效 JSON 格式应抛出 ValueError。"""
        content = "not valid json"
        path = _write_temp_file(content, ".json")
        try:
            with pytest.raises(ValueError, match="JSON 解析失败"):
                parse_json(path)
        finally:
            os.unlink(path)

    def test_not_array(self):
        """顶层非数组格式应抛出 ValueError。"""
        content = '{"text": "hello"}'
        path = _write_temp_file(content, ".json")
        try:
            with pytest.raises(ValueError, match="顶层必须是数组格式"):
                parse_json(path)
        finally:
            os.unlink(path)

    def test_auto_generate_id(self):
        """无 id 字段时自动生成 ID。"""
        content = json.dumps([{"text": "写一首诗"}, {"text": "翻译文字"}])
        path = _write_temp_file(content, ".json")
        try:
            result = parse_json(path)
            assert len(result) == 2
            assert len(result[0]["id"]) == 12
            assert result[0]["id"] != result[1]["id"]
        finally:
            os.unlink(path)


# ============================================================
# parse_txt 测试
# ============================================================

class TestParseTxt:
    """TXT 解析器测试。"""

    def test_normal_txt(self):
        content = "写一首诗\n翻译一段文字\n总结以下内容\n"
        path = _write_temp_file(content, ".txt")
        try:
            result = parse_txt(path)
            assert len(result) == 3
            assert result[0]["text"] == "写一首诗"
            assert result[1]["text"] == "翻译一段文字"
            assert result[2]["text"] == "总结以下内容"
        finally:
            os.unlink(path)

    def test_skip_empty_lines(self):
        """跳过空行。"""
        content = "写一首诗\n\n翻译一段文字\n\n\n总结以下内容\n"
        path = _write_temp_file(content, ".txt")
        try:
            result = parse_txt(path)
            assert len(result) == 3
        finally:
            os.unlink(path)

    def test_empty_file(self):
        content = "\n\n\n"
        path = _write_temp_file(content, ".txt")
        try:
            with pytest.raises(ValueError, match="未找到有效的提示词内容"):
                parse_txt(path)
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        with pytest.raises(ValueError, match="文件不存在"):
            parse_txt("nonexistent.txt")

    def test_all_have_ids(self):
        """每条记录都应有唯一 ID。"""
        content = "a\nb\nc\n"
        path = _write_temp_file(content, ".txt")
        try:
            result = parse_txt(path)
            ids = [r["id"] for r in result]
            assert len(ids) == len(set(ids))
        finally:
            os.unlink(path)


# ============================================================
# parse_markdown 测试
# ============================================================

class TestParseMarkdown:
    """Markdown 解析器测试。"""

    def test_split_by_h1(self):
        """按一级标题拆分。"""
        content = "# 标题一\n内容一的第一行\n内容一的第二行\n\n# 标题二\n内容二\n"
        path = _write_temp_file(content, ".md")
        try:
            result = parse_markdown(path)
            assert len(result) == 2
            assert "标题一" in result[0]["text"]
            assert "内容一的第一行" in result[0]["text"]
            assert "标题二" in result[1]["text"]
            assert "内容二" in result[1]["text"]
        finally:
            os.unlink(path)

    def test_split_by_h2(self):
        """按二级标题拆分。"""
        content = "## 步骤一\n详细说明\n\n## 步骤二\n更多说明\n"
        path = _write_temp_file(content, ".md")
        try:
            result = parse_markdown(path)
            assert len(result) == 2
            assert "步骤一" in result[0]["text"]
            assert "步骤二" in result[1]["text"]
        finally:
            os.unlink(path)

    def test_mixed_h1_h2(self):
        """混合使用一级和二级标题。"""
        content = "# 大标题\n内容A\n\n## 小标题\n内容B\n"
        path = _write_temp_file(content, ".md")
        try:
            result = parse_markdown(path)
            assert len(result) == 2
            assert "大标题" in result[0]["text"]
            assert "小标题" in result[1]["text"]
        finally:
            os.unlink(path)

    def test_no_headings(self):
        """无标题时整个文件作为一个区块。"""
        content = "这是一段没有标题的文本。\n第二行。\n"
        path = _write_temp_file(content, ".md")
        try:
            result = parse_markdown(path)
            assert len(result) == 1
            assert "没有标题的文本" in result[0]["text"]
        finally:
            os.unlink(path)

    def test_empty_file(self):
        content = ""
        path = _write_temp_file(content, ".md")
        try:
            with pytest.raises(ValueError, match="未找到有效的提示词内容"):
                parse_markdown(path)
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        with pytest.raises(ValueError, match="文件不存在"):
            parse_markdown("nonexistent.md")

    def test_ignore_deep_headings(self):
        """忽略三级及更深层级标题，不按它们拆分。"""
        content = "# 一级标题\n开头内容\n### 三级标题\n不应该拆分的内容\n## 二级标题\n新区块\n"
        path = _write_temp_file(content, ".md")
        try:
            result = parse_markdown(path)
            assert len(result) == 2
            # 第一个区块应包含一级标题开头内容以及三级标题的内容
            assert "三级标题" in result[0]["text"]
            assert "不应该拆分的内容" in result[0]["text"]
            assert "二级标题" in result[1]["text"]
        finally:
            os.unlink(path)

    def test_block_structure(self):
        """验证区块文本结构：标题 + 换行 + 内容。"""
        content = "# 提示词\n请写一首关于春天的诗。\n"
        path = _write_temp_file(content, ".md")
        try:
            result = parse_markdown(path)
            assert len(result) == 1
            assert result[0]["text"] == "提示词\n请写一首关于春天的诗。"
        finally:
            os.unlink(path)


# ============================================================
# parse_file 统一入口测试
# ============================================================

class TestParseFile:
    """统一解析入口测试。"""

    def test_parse_csv(self):
        path = _write_temp_file("prompt,id\nhello,1\n", ".csv")
        try:
            result = parse_file(path)
            assert len(result) == 1
            assert result[0]["text"] == "hello"
        finally:
            os.unlink(path)

    def test_parse_json(self):
        path = _write_temp_file('[{"text": "hello"}]', ".json")
        try:
            result = parse_file(path)
            assert len(result) == 1
            assert result[0]["text"] == "hello"
        finally:
            os.unlink(path)

    def test_parse_txt(self):
        path = _write_temp_file("hello\n", ".txt")
        try:
            result = parse_file(path)
            assert len(result) == 1
            assert result[0]["text"] == "hello"
        finally:
            os.unlink(path)

    def test_parse_markdown(self):
        path = _write_temp_file("# hello\nworld\n", ".md")
        try:
            result = parse_file(path)
            assert len(result) == 1
            assert "hello" in result[0]["text"]
        finally:
            os.unlink(path)

    def test_unsupported_format(self):
        with pytest.raises(ValueError, match="不支持的文件格式"):
            parse_file("test.xml")


# ============================================================
# process_single_input 测试
# ============================================================

class TestProcessSingleInput:
    """单条输入处理测试。"""

    def test_normal_input(self):
        record = process_single_input("写一首诗")
        assert isinstance(record, PromptRecord)
        assert record.original_text == "写一首诗"
        assert len(record.id) == 12

    def test_strip_whitespace(self):
        """自动去除首尾空白。"""
        record = process_single_input("  写一首诗  ")
        assert record.original_text == "写一首诗"

    def test_empty_input(self):
        with pytest.raises(ValueError, match="输入文本不能为空"):
            process_single_input("")

    def test_whitespace_only(self):
        with pytest.raises(ValueError, match="输入文本不能为空"):
            process_single_input("   ")


# ============================================================
# process_batch_input 测试
# ============================================================

class TestProcessBatchInput:
    """批量输入处理测试。"""

    def test_csv_batch(self):
        path = _write_temp_file("prompt,id\n写一首诗,1\n翻译文字,2\n", ".csv")
        try:
            records = process_batch_input(path)
            assert len(records) == 2
            assert all(isinstance(r, PromptRecord) for r in records)
            assert records[0].original_text == "写一首诗"
            assert records[0].id == "1"
            assert records[1].original_text == "翻译文字"
            assert records[1].id == "2"
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        with pytest.raises(ValueError, match="文件不存在"):
            process_batch_input("nonexistent.csv")


# ============================================================
# process_input 统一入口测试
# ============================================================

class TestProcessInput:
    """统一输入入口测试。"""

    def test_single_mode(self):
        records = process_input("写一首诗")
        assert len(records) == 1
        assert isinstance(records[0], PromptRecord)
        assert records[0].original_text == "写一首诗"

    def test_file_mode(self):
        path = _write_temp_file("prompt\n写一首诗\n", ".csv")
        try:
            records = process_input(path, is_file=True)
            assert len(records) == 1
            assert isinstance(records[0], PromptRecord)
            assert records[0].original_text == "写一首诗"
        finally:
            os.unlink(path)

    def test_file_mode_invalid_path(self):
        with pytest.raises(ValueError, match="文件不存在"):
            process_input("nonexistent.csv", is_file=True)