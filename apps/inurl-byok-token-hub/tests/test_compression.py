"""提示词压缩服务的单元测试。

覆盖点：
- 5 档参数化：代码块 / URL / JSON 逐字保留、结果非空、比例合法、
  ``claimed_ratio`` 取自 ``COMPRESSION_SPECS``（厂商自述估算值）。
- 拒绝压缩（``refused=True``）且原样返回。
- 工具链重复行样本：RTK 的去重效果强于 Lite。
- 空串与非法档位的健壮性。
"""

import dataclasses

import pytest

from inurl_byok_token_hub.errors import ByokError, ErrorCode
from inurl_byok_token_hub.models.routing import COMPRESSION_SPECS, CompressionLevel
from inurl_byok_token_hub.services.compression_service import (
    CompressionResult,
    compress_prompt,
)

ALL_LEVELS = tuple(CompressionLevel)

#: 含围栏代码块 + URL + JSON 的混合样本
MIXED_SAMPLE = (
    "请帮我审查下面的接口实现，并且给出一份非常详细的评审意见。\n"
    "请顺便检查一下错误处理和日志记录是否完整。\n"
    "参考文档在 https://example.com/docs/api?version=2&lang=zh 里面有说明。\n"
    "\n"
    "接口实现如下：\n"
    "```python\n"
    "def create_token(user_id: str, ttl: int = 3600) -> str:\n"
    "    return issue_token(user_id, ttl)\n"
    "```\n"
    "\n"
    "请求体示例：\n"
    '{"model": "inurl", "stream": false, "options": {"temperature": 0.2, "top_p": 0.9}}\n'
    "\n"
    "请给出评审意见。\n"
    "请给出评审意见。\n"
    "请给出评审意见。\n"
    "另外请确认 `create_token` 的签名是否与文档一致。\n"
    "请确认 `create_token` 的签名是否与文档一致。\n"
)

CODE_BLOCK = (
    "```python\n"
    "def create_token(user_id: str, ttl: int = 3600) -> str:\n"
    "    return issue_token(user_id, ttl)\n"
    "```"
)
URL = "https://example.com/docs/api?version=2&lang=zh"
JSON_SNIPPET = '{"model": "inurl", "stream": false, "options": {"temperature": 0.2, "top_p": 0.9}}'

#: 纯 JSON 输入：全文皆为受保护片段，无可压缩内容
PURE_JSON = '{\n  "model": "inurl",\n  "stream": false,\n  "options": {"top_p": 0.9}\n}'

#: 工具链输出样本（git diff / grep / 日志 重复行）
TOOL_SAMPLE = (
    "请查看本次改动的输出。\n"
    "请查看本次改动的输出。\n"
    "\n"
    "diff --git a/src/app.py b/src/app.py\n"
    "index 1234567..89abcde 100644\n"
    "--- a/src/app.py\n"
    "+++ b/src/app.py\n"
    "@@ -1,4 +1,4 @@\n"
    "-def old_handler(request):\n"
    "+def new_handler(request):\n"
    " src/app.py:12:     return call(request)\n"
    " src/app.py:34:     return call(request)\n"
    " src/app.py:56:     return call(request)\n"
    "[2026-09-29 10:00:01] INFO request ok\n"
    "[2026-09-29 10:00:02] INFO request ok\n"
    "[2026-09-29 10:00:03] INFO request ok\n"
    "\n"
    "请总结这些改动。\n"
)


@pytest.mark.parametrize("level", ALL_LEVELS, ids=lambda lv: lv.value)
def test_protected_fragments_are_preserved_verbatim(level):
    """代码块 / URL / JSON 在各档位下都必须逐字保留。"""
    result = compress_prompt(MIXED_SAMPLE, level)

    assert isinstance(result, CompressionResult)
    assert result.text.strip(), "压缩结果不应为空"
    assert CODE_BLOCK in result.text
    assert URL in result.text
    assert JSON_SNIPPET in result.text
    assert {"code_block", "url", "json"} <= set(result.protected)
    assert result.refused is False
    assert result.claimed_ratio == COMPRESSION_SPECS[level][0]
    assert result.level is level
    assert result.original_length == len(MIXED_SAMPLE)
    assert result.compressed_length == len(result.text)
    assert 0.0 <= result.estimated_ratio <= 1.0


def test_claimed_ratio_is_vendor_estimate_string():
    """``claimed_ratio`` 是厂商自述估算值字符串，本实现不承诺实测比例与之相等。"""
    result = compress_prompt(MIXED_SAMPLE, CompressionLevel.ULTRA)
    assert result.claimed_ratio == "≈75%"
    assert isinstance(result.claimed_ratio, str)


@pytest.mark.parametrize(
    "level",
    [CompressionLevel.AGGRESSIVE, CompressionLevel.ULTRA, CompressionLevel.RTK],
    ids=lambda lv: lv.value,
)
def test_higher_levels_actually_shrink(level):
    """中高档位在混合样本上应当产生实际压缩。"""
    result = compress_prompt(MIXED_SAMPLE, level)
    assert result.estimated_ratio > 0.0
    assert len(result.text) < len(MIXED_SAMPLE)


def test_pure_json_is_refused_and_returned_verbatim():
    """纯 JSON 无可压缩内容：拒绝压缩并原样返回。"""
    result = compress_prompt(PURE_JSON, CompressionLevel.ULTRA)

    assert result.refused is True
    assert result.text == PURE_JSON
    assert result.compressed_length == result.original_length
    assert result.estimated_ratio == 0.0
    assert "json" in result.protected


def test_pure_code_block_is_refused_and_returned_verbatim():
    """纯代码块同样判定为无可压缩内容。"""
    result = compress_prompt(CODE_BLOCK, CompressionLevel.AGGRESSIVE)

    assert result.refused is True
    assert result.text == CODE_BLOCK
    assert "code_block" in result.protected


def test_rtk_dedupes_toolchain_lines_better_than_lite():
    """RTK 档对工具链重复行的去重效果强于 Lite 档。"""
    lite = compress_prompt(TOOL_SAMPLE, CompressionLevel.LITE)
    rtk = compress_prompt(TOOL_SAMPLE, CompressionLevel.RTK)

    assert lite.refused is False
    assert rtk.refused is False
    assert len(rtk.text) < len(lite.text)
    assert rtk.estimated_ratio > lite.estimated_ratio
    # 首行与末行都应保留
    assert "diff --git a/src/app.py b/src/app.py" in rtk.text
    assert "请总结这些改动。" in rtk.text


def test_rtk_keeps_protected_snippet_when_deduping():
    """RTK 去重不得吞掉受保护片段（代码块原样保留）。"""
    sample = CODE_BLOCK + "\n" + TOOL_SAMPLE
    rtk = compress_prompt(sample, CompressionLevel.RTK)

    assert CODE_BLOCK in rtk.text
    assert rtk.refused is False


def test_empty_input_is_robust():
    """空串输入不抛异常，原样返回。"""
    for level in ALL_LEVELS:
        result = compress_prompt("", level)
        assert result.text == ""
        assert result.original_length == 0
        assert result.estimated_ratio == 0.0


def test_whitespace_only_input_is_robust():
    result = compress_prompt("   \n\n\t\n", CompressionLevel.ULTRA)
    assert result.refused is False
    assert result.estimated_ratio == 0.0


def test_invalid_level_raises_byok_error():
    with pytest.raises(ByokError) as excinfo:
        compress_prompt("你好", "no-such-level")
    assert excinfo.value.error_code is ErrorCode.INVALID_REQUEST


def test_string_level_is_accepted():
    """允许传入档位的字符串值。"""
    result = compress_prompt(MIXED_SAMPLE, "standard")
    assert result.level is CompressionLevel.STANDARD
    assert URL in result.text


def test_result_is_frozen_dataclass():
    result = compress_prompt(MIXED_SAMPLE, CompressionLevel.LITE)
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.text = "篡改"
