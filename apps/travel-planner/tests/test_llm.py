"""LLM 客户端测试：六分支容错、密钥治理、JSON 提取（TR-4.x）。"""

import json

import httpx
import pytest

from travel_planner.config import LLMConfig
from travel_planner.errors import LLMError
from travel_planner.llm import GenerateRequest, LLMClient, extract_json, parse_draft

SECRET = "sk-SECRET-XYZ"


def make_client(handler, configured=True, timeout=5.0):
    cfg = (
        LLMConfig(base_url="http://llm.test/v1", api_key=SECRET, model="m", timeout=timeout)
        if configured
        else LLMConfig()
    )
    return LLMClient(cfg, transport=httpx.MockTransport(handler))


def ok_response(content):
    return httpx.Response(
        200, json={"choices": [{"message": {"role": "assistant", "content": content}}]}
    )


def valid_draft_json(days=3, items_per_day=2):
    days_payload = []
    for d in range(1, days + 1):
        days_payload.append(
            {
                "day_index": d,
                "items": [
                    {
                        "type": "sight" if j == 0 else "meal",
                        "start_time": "09:00" if j == 0 else "12:00",
                        "title": f"第{d}天条目{j}",
                        "location": "某地",
                        "cost": 50 + j,
                        "notes": "提示",
                    }
                    for j in range(items_per_day)
                ],
            }
        )
    return json.dumps({"days": days_payload}, ensure_ascii=False)


def make_request(days=3):
    return GenerateRequest(
        destination="杭州",
        days=days,
        start_date="2026-10-01",
        end_date=f"2026-10-0{days}",
        people=2,
        preferences="喜欢博物馆",
        budget_tier="舒适",
    )


def test_valid_draft():
    client = make_client(lambda req: ok_response(valid_draft_json(3)))
    draft = client.generate_draft(make_request(3))
    assert len(draft) == 6
    assert draft[0].type == "sight"
    assert draft[0].cost == 50
    assert draft[5].day_index == 3


def test_fenced_json_tolerated():
    fenced = "好的，以下是行程：\n```json\n" + valid_draft_json(2) + "\n```\n祝旅途愉快"
    client = make_client(lambda req: ok_response(fenced))
    draft = client.generate_draft(make_request(2))
    assert len(draft) == 4


def test_non_json_text_rejected():
    client = make_client(lambda req: ok_response("抱歉，我无法完成该请求。"))
    with pytest.raises(LLMError, match="未返回 JSON"):
        client.generate_draft(make_request())


def test_day_out_of_range_rejected():
    client = make_client(lambda req: ok_response(valid_draft_json(5)))
    with pytest.raises(LLMError, match="超出行程天数"):
        client.generate_draft(make_request(3))


def test_bad_type_rejected():
    payload = {"days": [{"day_index": 1, "items": [{"type": "hiking", "title": "x"}]}]}
    client = make_client(lambda req: ok_response(json.dumps(payload)))
    with pytest.raises(LLMError, match="type"):
        client.generate_draft(make_request())


def test_unknown_field_rejected():
    payload = {
        "days": [{"day_index": 1, "items": [{"type": "sight", "title": "x", "foo": 1}]}]
    }
    client = make_client(lambda req: ok_response(json.dumps(payload)))
    with pytest.raises(LLMError, match="未知字段"):
        client.generate_draft(make_request())


def test_timeout_degrades_to_chinese_error():
    def handler(request):
        raise httpx.ReadTimeout("timed out")

    client = make_client(handler, timeout=2.0)
    with pytest.raises(LLMError, match="超时"):
        client.generate_draft(make_request())


def test_http_error_status():
    client = make_client(lambda req: httpx.Response(401, json={"error": "bad key"}))
    with pytest.raises(LLMError, match="HTTP 401"):
        client.generate_draft(make_request())


def test_network_error_degrades():
    def handler(request):
        raise httpx.ConnectError("connection refused")

    client = make_client(handler)
    with pytest.raises(LLMError, match="不可达"):
        client.generate_draft(make_request())


def test_not_configured_no_request():
    captured = []

    def handler(request):
        captured.append(request)
        return ok_response("{}")

    client = make_client(handler, configured=False)
    with pytest.raises(LLMError, match="未配置"):
        client.generate_draft(make_request())
    assert captured == []  # 未配置时不得发起网络请求


def test_api_key_sent_but_never_leaked():
    captured = []

    def handler(request):
        captured.append(request)
        raise httpx.ConnectError("boom")

    client = make_client(handler)
    with pytest.raises(LLMError) as exc_info:
        client.generate_draft(make_request())
    assert SECRET not in str(exc_info.value)
    # 密钥确实通过请求头发送（BYOK 语义正确）
    assert captured[0].headers["Authorization"] == f"Bearer {SECRET}"


def test_malformed_response_structure():
    client = make_client(lambda req: httpx.Response(200, json={"unexpected": True}))
    with pytest.raises(LLMError, match="响应结构异常"):
        client.generate_draft(make_request())


def test_extract_json_variants():
    assert extract_json('{"a":1}') == {"a": 1}
    assert extract_json('说明 {"a":1} 结尾') == {"a": 1}
    assert extract_json('```json\n{"a":1}\n```') == {"a": 1}
    with pytest.raises(LLMError, match="未返回 JSON"):
        extract_json("完全没有大括号")
    with pytest.raises(LLMError, match="无法解析"):
        extract_json("{broken json")


def test_parse_draft_empty_items():
    with pytest.raises(LLMError, match="没有任何条目"):
        parse_draft(json.dumps({"days": [{"day_index": 1, "items": []}]}), 3)


def test_parse_draft_missing_days():
    with pytest.raises(LLMError, match="days"):
        parse_draft(json.dumps({"foo": 1}), 3)


# ---------------------------------------------------------------- 分支补齐
def test_endpoint_with_full_url_not_doubled():
    captured = []

    def handler(request):
        captured.append(request)
        return ok_response(valid_draft_json(1, 1))

    cfg = LLMConfig(base_url="http://llm.test/v1/chat/completions", api_key=SECRET, model="m")
    client = LLMClient(cfg, transport=httpx.MockTransport(handler))
    client.generate_draft(make_request(1))
    assert captured[0].url == "http://llm.test/v1/chat/completions"


def test_empty_content_rejected():
    client = make_client(lambda req: ok_response(""))
    with pytest.raises(LLMError, match="空内容"):
        client.generate_draft(make_request())


def test_extract_json_top_level_not_object():
    """顶层非对象防御分支：截取片段以 { 开头时必为对象，此处验证数组文本走「未返回 JSON」。"""
    with pytest.raises(LLMError, match="未返回 JSON"):
        extract_json("[1, 2, 3]")


def test_parse_draft_day_branches():
    with pytest.raises(LLMError, match="days\\[0\\] 必须是对象"):
        parse_draft(json.dumps({"days": [1]}), 3)
    with pytest.raises(LLMError, match="未知字段"):
        parse_draft(json.dumps({"days": [{"day_index": 1, "foo": 1}]}), 3)
    with pytest.raises(LLMError, match="day_index 必须是整数"):
        parse_draft(json.dumps({"days": [{"day_index": "1", "items": []}]}), 3)
    with pytest.raises(LLMError, match="items 必须是列表"):
        parse_draft(json.dumps({"days": [{"day_index": 1, "items": "x"}]}), 3)


def test_parse_draft_item_branches():
    base = lambda item: json.dumps({"days": [{"day_index": 1, "items": [item]}]})  # noqa: E731
    with pytest.raises(LLMError, match="items\\[0\\] 必须是对象"):
        parse_draft(base("x"), 3)
    with pytest.raises(LLMError, match="title"):
        parse_draft(base({"type": "sight", "title": "x" * 61}), 3)
    with pytest.raises(LLMError, match="title"):
        parse_draft(base({"type": "sight", "title": 123}), 3)
    with pytest.raises(LLMError, match="HH:MM"):
        parse_draft(base({"type": "sight", "title": "x", "start_time": "9:00"}), 3)
    with pytest.raises(LLMError, match="HH:MM"):
        parse_draft(base({"type": "sight", "title": "x", "start_time": 900}), 3)
    with pytest.raises(LLMError, match="结束时间"):
        parse_draft(
            base({"type": "sight", "title": "x", "start_time": "14:00", "end_time": "09:00"}), 3
        )
    with pytest.raises(LLMError, match="location"):
        parse_draft(base({"type": "sight", "title": "x", "location": "y" * 201}), 3)
    with pytest.raises(LLMError, match="location"):
        parse_draft(base({"type": "sight", "title": "x", "location": 9}), 3)
    with pytest.raises(LLMError, match="cost"):
        parse_draft(base({"type": "sight", "title": "x", "cost": True}), 3)
    with pytest.raises(LLMError, match="cost"):
        parse_draft(base({"type": "sight", "title": "x", "cost": -1}), 3)
    with pytest.raises(LLMError, match="notes"):
        parse_draft(base({"type": "sight", "title": "x", "notes": "n" * 501}), 3)


def test_parse_draft_item_count_limit():
    items = [{"type": "other", "title": f"条目{i}"} for i in range(201)]
    payload = json.dumps({"days": [{"day_index": 1, "items": items}]})
    with pytest.raises(LLMError, match="超过上限"):
        parse_draft(payload, 3)
