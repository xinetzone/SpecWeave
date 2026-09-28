"""微信平台原生列表/搜索响应解析测试。"""

import json

import pytest

from mp_archiver.adapters.base import AccountRef
from mp_archiver.adapters.wechat_payload import (
    ApiRetError,
    CredentialExpiredError,
    PayloadError,
    parse_accounts,
    parse_article_url,
    parse_history_page,
    select_account,
)

BIZ = "MzA4MjA=="
URL_MAIN = (
    "http://mp.weixin.qq.com/s?__biz=MzA4MjA%3D%3D&mid=2447531234&idx=1"
    "&sn=abcmain&chksm=abc&amp;scene=27"
)
URL_SUB1 = (
    "http://mp.weixin.qq.com/s?__biz=MzA4MjA%3D%3D&mid=2447531234&idx=2&sn=abcsub1"
)
URL_SUB2 = (
    "http://mp.weixin.qq.com/s?__biz=MzA4MjA%3D%3D&mid=2447531234&idx=3&sn=abcsub2"
)


def _batch(*, url=URL_MAIN, multi=(), msg_type=49, ts=1609459200, copyright_stat=0):
    info = {
        "title": "主图文标题",
        "digest": "主图文摘要",
        "content_url": url,
        "cover": "http://img/main.jpg",
        "author": "主作者",
        "copyright_stat": copyright_stat,
    }
    info["multi_app_msg_item_list"] = list(multi)
    return {"comm_msg_info": {"id": 1001, "type": msg_type, "datetime": ts},
            "app_msg_ext_info": info}


def _payload(batches, *, as_string=True, next_offset=10, can_continue=1, ret=0):
    inner = {"list": batches}
    return {
        "ret": ret,
        "errmsg": "" if ret == 0 else "fail",
        "general_msg_list": json.dumps(inner, ensure_ascii=False) if as_string else inner,
        "next_offset": next_offset,
        "can_msg_continue": can_continue,
    }


# ---- URL 解析 ----

def test_parse_article_url_decodes_biz_and_parts():
    parts = parse_article_url(URL_MAIN)
    assert parts.biz == BIZ  # %3D%3D 解码为 ==
    assert parts.mid == "2447531234"
    assert parts.idx == 1
    assert parts.sn == "abcmain"


def test_parse_article_url_empty_and_bad_idx():
    empty = parse_article_url("")
    assert (empty.biz, empty.mid, empty.idx, empty.sn) == (None, None, None, None)
    parts = parse_article_url("http://x/?__biz=a&mid=1&idx=abc")
    assert parts.idx is None
    assert parts.biz == "a"


# ---- 历史页解析 ----

def test_parse_single_appmsg_batch():
    page = parse_history_page(_payload([_batch()]))
    assert page.has_more is True
    assert page.next_offset == 10
    assert page.skipped_non_article == 0
    assert len(page.articles) == 1
    article = page.articles[0]
    assert article.biz == BIZ
    assert article.idx == 1
    assert article.sn == "abcmain"
    assert article.title == "主图文标题"
    assert article.author == "主作者"
    assert article.cover_url == "http://img/main.jpg"
    assert article.publish_time == "2021-01-01T00:00:00+00:00"


def test_parse_multi_appmsg_splits_articles():
    multi = [
        {"title": "次条1", "content_url": URL_SUB1, "author": "次作者",
         "digest": "d1", "cover": ""},
        {"title": "次条2", "content_url": URL_SUB2, "digest": "d2"},
    ]
    page = parse_history_page(_payload([_batch(multi=multi)]))
    assert [a.idx for a in page.articles] == [1, 2, 3]
    assert [a.sn for a in page.articles] == ["abcmain", "abcsub1", "abcsub2"]
    assert page.articles[1].author == "次作者"
    # 次条继承群发时间
    assert page.articles[2].publish_time == "2021-01-01T00:00:00+00:00"


def test_parse_original_flag_and_non_article_skip():
    page_original = parse_history_page(_payload([_batch(copyright_stat=11)]))
    assert page_original.articles[0].is_original is True

    page_normal = parse_history_page(
        _payload([_batch(copyright_stat=0), _batch(msg_type=1)])
    )
    assert page_normal.articles[0].is_original is False
    assert page_normal.skipped_non_article == 1
    assert len(page_normal.articles) == 1


def test_parse_general_msg_list_as_object():
    payload = _payload([_batch()], as_string=False, can_continue=0)
    page = parse_history_page(payload)
    assert len(page.articles) == 1
    assert page.has_more is False


def test_parse_empty_general_msg_list_string():
    page = parse_history_page({"ret": 0, "general_msg_list": "",
                               "next_offset": 0, "can_msg_continue": 0})
    assert page.articles == ()


def test_parse_bad_json_string_raises():
    with pytest.raises(PayloadError):
        parse_history_page({"ret": 0, "general_msg_list": "{not json"})


def test_parse_ret_errors():
    with pytest.raises(CredentialExpiredError):
        parse_history_page(_payload([], ret=200013))
    with pytest.raises(ApiRetError):
        parse_history_page(_payload([], ret=1))


def test_parse_skips_item_without_mid():
    batch = _batch(url="http://mp.weixin.qq.com/s?__biz=MzA4MjA%3D%3D&idx=1")
    page = parse_history_page(_payload([batch]), account_biz=BIZ)
    assert page.articles == ()


def test_parse_uses_account_biz_fallback():
    url = "http://mp.weixin.qq.com/s?mid=2447531234&idx=1&sn=zzz"
    page = parse_history_page(_payload([_batch(url=url)]), account_biz=BIZ)
    assert page.articles[0].biz == BIZ


# ---- 搜索解析 ----

def test_parse_accounts_native_searchbiz():
    payload = {
        "base_resp": {"ret": 0, "errmsg": ""},
        "list": [
            {"fakeid": 998877, "nickname": "意识食谱", "alias": "mindfood",
             "service_type": 1},
            {"fakeid": 112233, "nickname": "其他号", "alias": "other"},
        ],
    }
    accounts = parse_accounts(payload)
    assert accounts[0] == AccountRef("意识食谱", "mindfood", "998877", "")
    assert select_account(accounts, "意识食谱").fakeid == "998877"
    assert select_account(accounts, "mindfood").nickname == "意识食谱"


def test_parse_accounts_list_as_json_string():
    payload = {"list": json.dumps([
        {"fakeid": 1, "nickname": "健康饮食日报", "alias": "jk-daily"}],
        ensure_ascii=False)}
    accounts = parse_accounts(payload)
    # 包含匹配
    assert select_account(accounts, "饮食").nickname == "健康饮食日报"


def test_parse_accounts_biz_from_field_or_url():
    payload = {"list": [
        {"fakeid": 1, "nickname": "带biz", "alias": "", "__biz": BIZ},
        {"fakeid": 2, "nickname": "链接biz", "alias": "",
         "content_url": URL_MAIN},
    ]}
    accounts = parse_accounts(payload)
    assert accounts[0].biz == BIZ
    assert accounts[1].biz == BIZ


def test_parse_accounts_errors():
    with pytest.raises(CredentialExpiredError):
        parse_accounts({"base_resp": {"ret": 200013}})
    with pytest.raises(ApiRetError):
        parse_accounts({"ret": 500})
    assert select_account((), "x") is None


# ---- 边界与降级分支（Task 14 覆盖率补齐） ----

def test_parse_history_page_non_dict_payload_raises():
    """非 JSON 对象的历史消息响应（如数组）→ PayloadError。"""
    with pytest.raises(PayloadError):
        parse_history_page([])


def test_parse_history_page_ret_not_int_raises_api_ret_error():
    """ret 不可转 int：归 -1 后抛 ApiRetError，文案取 errmsg。"""
    with pytest.raises(ApiRetError) as ei:
        parse_history_page({"ret": "oops", "errmsg": "平台异常"})
    assert ei.value.ret == -1
    assert ei.value.errmsg == "平台异常"


def test_parse_history_page_light_wrapper_list_and_items():
    """无 general_msg_list 时的轻包装：分别取 list 与 items 兜底。"""
    page_list = parse_history_page({"ret": 0, "list": [_batch()]})
    assert len(page_list.articles) == 1
    page_items = parse_history_page({"ret": 0, "items": [_batch()]})
    assert len(page_items.articles) == 1
    assert page_items.articles[0].mid == "2447531234"


def test_parse_history_page_batches_not_list_raises():
    """general_msg_list 解析出的对象其 list 不是数组 → PayloadError。"""
    with pytest.raises(PayloadError):
        parse_history_page(
            {"ret": 0, "general_msg_list": json.dumps({"list": "x"})}
        )


def test_parse_history_page_skips_non_dict_batch():
    """批次元素非 dict：跳过且不计入非图文统计。"""
    page = parse_history_page(_payload([_batch(), "垃圾批次", 123]))
    assert len(page.articles) == 1
    assert page.skipped_non_article == 0


def test_parse_history_page_next_offset_not_int_defaults_zero():
    """next_offset 非数值：归 0 且不抛异常。"""
    payload = _payload([_batch()])
    payload["next_offset"] = "末尾"
    page = parse_history_page(payload)
    assert page.next_offset == 0
    assert len(page.articles) == 1


def test_parse_history_page_bad_datetime_yields_none():
    """comm_msg_info.datetime 非法（字符串/None）：publish_time 为 None 仍入库。"""
    page_str = parse_history_page(_payload([_batch(ts="abc")]))
    assert page_str.articles[0].publish_time is None
    page_none = parse_history_page(_payload([_batch(ts=None)]))
    assert page_none.articles[0].publish_time is None


def test_parse_history_page_copyright_stat_not_int_defaults_false():
    """copyright_stat 非数值：归 0，is_original 为 False。"""
    page = parse_history_page(_payload([_batch(copyright_stat="oops")]))
    assert page.articles[0].is_original is False


def test_parse_accounts_non_dict_payload_raises():
    """非 JSON 对象的搜索响应 → PayloadError。"""
    with pytest.raises(PayloadError):
        parse_accounts("not-an-object")


def test_parse_accounts_base_resp_ret_not_int_and_errmsg():
    """base_resp.ret 不可转 int → ApiRetError(-1)，文案取自 base_resp.errmsg。"""
    with pytest.raises(ApiRetError) as ei:
        parse_accounts({"base_resp": {"ret": "oops", "errmsg": "搜索被拒"}})
    assert ei.value.ret == -1
    assert ei.value.errmsg == "搜索被拒"


def test_parse_accounts_list_bad_json_raises():
    """list 为非法 JSON 字符串 → PayloadError。"""
    with pytest.raises(PayloadError):
        parse_accounts({"list": "{not json"})


def test_parse_accounts_list_none_falls_back_to_items():
    """list 为 None：回退 items，且非 dict 元素被跳过。"""
    accounts = parse_accounts({"list": None, "items": [
        "脏数据", {"fakeid": 7, "nickname": "回退号", "alias": "fb"}]})
    assert len(accounts) == 1
    assert accounts[0].nickname == "回退号"


def test_parse_accounts_list_not_array_raises():
    """list 既非字符串也非数组 → PayloadError。"""
    with pytest.raises(PayloadError):
        parse_accounts({"list": 123})


def test_select_account_blank_name_returns_none():
    """空/纯空白名称直接返回 None（不做包含匹配）。"""
    accounts = (AccountRef("意识食谱", "mindfood", "1", BIZ),)
    assert select_account(accounts, "   ") is None
