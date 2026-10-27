#!/usr/bin/env python3
"""内嵌智能页代提交执行器（带强制闸门）。

流程严格对应 SKILL.md §7.3：
    步骤2.5 幂等查重 → 步骤4 dry-run 回显 → 步骤4.5 用户确认闸门
    → 步骤5 探针写删 → 步骤6 正式写入 → 步骤7 回读复核

三条硬闸门（缺一即拒绝执行）：
    1. --confirm-written 必须显式传入，且 dry-run 回显须已产出
    2. 幂等查重命中同键记录 → 直接拒绝写入
    3. 字段名命中红线关键词（授权/承诺/证件/金融/生物识别）→ 拒绝写入，
       除非该字段由 --user-provided 指定为「用户已亲自填写」

用法:
    # 1) 只读：查 schema + 幂等查重 + 打印将要写入的字段（不写库）
    python submit_record.py --page-id <pid> --database-id <dbid> \
        --fields-json fields.json --dry-run

    # 2) 正式写入（需先看过 dry-run 输出并取得用户确认）
    python submit_record.py --page-id <pid> --database-id <dbid> \
        --fields-json fields.json --idempotency-key "作品名" --confirm-written

字段 JSON 形状（值用裸值，脚本负责转 oneof）：
    {"应用名称": {"type": "text", "value": "..."},
     "作品截图": {"type": "image", "value": [{"title": "...", "imageUrl": "https://...", "width": 1280, "height": 720}]},
     "参赛授权": {"type": "checkbox", "value": true, "redline": true}}
"""

import argparse
import json
import os
import sys
from pathlib import Path

HOST = os.environ.get("WB_SPACE_HOST", "https://www.workbuddy.cn")

# ---------------------------------------------------------------- 依赖定位

sys.path.insert(0, str(Path(__file__).resolve().parent))
from probe_channels import (  # noqa: E402
    _safe_iterdir,
    classify_table,
    describe_schema,
    find_library_root,
    load_ipc,
)

# ---------------------------------------------------------------- 红线字段

REDLINE_KEYWORDS = (
    "授权", "承诺", "同意", "声明", "承诺函", "权利转让", "版权",
    "证件", "身份证", "护照", "社保", "银行卡", "支付", "结算",
    "住址", "地址", "签名", "指纹", "虹膜", "人脸", "生物识别",
)

# ---------------------------------------------------------------- oneof 构造

TYPE_MAP = {
    "text": lambda v: {"text": v},
    "number": lambda v: {"number": v},
    "select": lambda v: {"select": v},
    "url": lambda v: {"url": {"text": v[0], "link": v[1]}},
    "checkbox": lambda v: {"checkbox": bool(v)},
    "image": lambda v: {"image": {"images": v}},
    "attachment": lambda v: {"attachment": v},
}


def is_redline(field_name: str) -> bool:
    return any(k in field_name for k in REDLINE_KEYWORDS)


def build_props(fields: dict) -> dict:
    """裸值 + type → oneof 形状。"""
    out = {}
    for name, spec in fields.items():
        t = spec.get("type")
        if t not in TYPE_MAP:
            raise ValueError(f"字段 {name} 的 type={t!r} 不支持；可用：{sorted(TYPE_MAP)}")
        out[name] = TYPE_MAP[t](spec.get("value"))
    return out


# ---------------------------------------------------------------- HTTP 封装


def post(ipc, path: str, body: dict) -> dict:
    try:
        r = ipc.http_request("POST", HOST + path, body=body)
    except Exception as exc:  # noqa: BLE001
        return {"code": -1, "msg": f"transport error: {exc}"}
    return r if isinstance(r, dict) else {"code": -1, "msg": str(r)[:200]}


def read_schema(ipc, db_id: str, page_id: str) -> dict:
    for path in ("/space/api/page/share/database/get", "/space/api/view/database/get"):
        r = post(ipc, path, {"databaseId": db_id, "pageId": page_id})
        if r.get("code") == 0:
            return r.get("data") or {}
    return {}


def query_records(ipc, db_id: str, page_id: str) -> list[dict]:
    """无过滤全量取一页（仅用于探查表结构，不用于查重）。"""
    r = post(ipc, "/space/api/view/database/query", {"databaseId": db_id, "pageId": page_id})
    if r.get("code") != 0:
        return []
    data = r.get("data") or {}
    return data.get("results") or data.get("result") or []


def query_by_filter(ipc, db_id: str, page_id: str, prop: str, op: str, value: str) -> list[dict]:
    """★ 服务端过滤查重（实测 2026-10-26 可靠）。

    filter 形状（来自宿主 SDK 契约 database-sdk-contract.md §4）：
        {"property": {"property": "<字段名>", "text": {"equals"|"contains": "<值>"}}}
    text/url/phone 字段的操作符为 equals / contains；number/select/date/checkbox 各有专属字段名。

    ⚠️ 全量翻页不可靠：实测该表首页仅 50 条、hasMore=true、nextCursor 存在，
    翻 10 页 500 条仍未必命中目标记录（记录按提交时间落位，不在首页）。
    **查重必须走服务端 filter，不能靠本地遍历。**
    """
    r = post(ipc, "/space/api/view/database/query",
             {"databaseId": db_id, "pageId": page_id,
              "filter": {"property": {"property": prop, "text": {op: value}}}})
    if r.get("code") != 0:
        return []
    data = r.get("data") or {}
    return data.get("results") or data.get("result") or []


def add_record(ipc, db_id: str, page_id: str, props: dict) -> str:
    r = post(ipc, "/space/api/view/database/addRecord",
             {"databaseId": db_id, "pageId": page_id, "properties": props})
    if r.get("code") != 0:
        raise RuntimeError(f"addRecord failed: {r}")
    return (r.get("data") or {}).get("id")


def get_record(ipc, db_id: str, page_id: str, record_id: str) -> dict:
    r = post(ipc, "/space/api/view/database/getRecord",
             {"databaseId": db_id, "pageId": page_id, "recordId": record_id})
    if r.get("code") != 0:
        return {}
    return (r.get("data") or {}).get("result") or {}


def delete_record(ipc, record_id: str) -> bool:
    """实测：body 仅需 recordId。"""
    r = post(ipc, "/space/api/view/database/deleteRecord", {"recordId": record_id})
    return r.get("code") == 0


def find_existing(records: list[dict], key: str) -> list[dict]:
    """按业务唯一键在结果集里找同键记录（对各字段值做包含匹配）。"""
    hits = []
    for rec in records:
        blob = json.dumps(rec, ensure_ascii=False)
        if key and key in blob:
            hits.append(rec)
    return hits
# ---------------------------------------------------------------- 闸门


def gate_redline(fields: dict, user_provided: list[str]) -> list[str]:
    """返回被拦截的红线字段名列表。"""
    blocked = []
    for name, spec in fields.items():
        if not (spec.get("redline") or is_redline(name)):
            continue
        if name in user_provided:
            continue  # 用户明确声明已亲自填写/提供
        blocked.append(name)
    return blocked


def gate_idempotency(records: list[dict], key: str | None) -> list[dict]:
    if not key:
        return []
    return find_existing(records, key)


def gate_confirm(confirm: bool, dry_run_done: bool) -> str | None:
    if not dry_run_done:
        return "未产出 dry-run 回显，禁止写入（SKILL.md §7.3 步骤4）"
    if not confirm:
        return "未取得用户明示确认（--confirm-written），禁止写入（SKILL.md §6.5 / §7.3 步骤4.5）"
    return None


def render_table(fields: dict, schema: dict, user_provided: list[str]) -> str:
    """dry-run 回显：字段 / 将写入值 / 取值来源 / 红线标记。"""
    schema_fields = {f["name"]: f for f in describe_schema(schema)}
    lines = [f"{'字段':<26} {'类型':<10} {'取值来源':<12} {'红线':<6} 值",
             "-" * 100]
    for name, spec in fields.items():
        sf = schema_fields.get(name)
        ftype = (sf or {}).get("type") or spec.get("type") or "?"
        src = "用户已提供" if name in user_provided else "用户口述/文件读出"
        rl = "是" if (spec.get("redline") or is_redline(name)) else "否"
        val = json.dumps(spec.get("value"), ensure_ascii=False)
        if len(val) > 46:
            val = val[:43] + "..."
        lines.append(f"{name:<26} {ftype:<10} {src:<12} {rl:<6} {val}")
    return "\n".join(lines)


# ---------------------------------------------------------------- 主流程


def main() -> int:
    ap = argparse.ArgumentParser(description="内嵌智能页代提交执行器（带闸门）")
    ap.add_argument("--page-id", required=True)
    ap.add_argument("--database-id", required=True)
    ap.add_argument("--fields-json", required=True, help="字段定义 JSON 文件路径")
    ap.add_argument("--idempotency-key", default=None, help="业务唯一键（提交编号/作品名）")
    ap.add_argument("--idempotency-field", default=None,
                    help="幂等键所在字段名；给了就用它做服务端 filter 查重（推荐）")
    ap.add_argument("--idempotency-op", default="equals", choices=["equals", "contains"])
    ap.add_argument("--confirm-written", action="store_true", help="用户已明示确认全部字段")
    ap.add_argument("--user-provided", default="", help="逗号分隔：用户已亲自填写/提供的字段名")
    ap.add_argument("--dry-run", action="store_true", help="只读：不写入，仅回显")
    ap.add_argument("--probe-write", action="store_true", help="写一条探针记录并立即删除")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    user_provided = [s.strip() for s in args.user_provided.split(",") if s.strip()]

    ipc, err = load_ipc()
    if ipc is None:
        print(f"[FATAL] {err or '未找到内置 skill 库（workbuddy_ipc）'}")
        print("        降级：请用户在页面内手工填写。")
        return 3

    fields = json.loads(Path(args.fields_json).read_text(encoding="utf-8"))

    # 步骤1：schema
    schema = read_schema(ipc, args.database_id, args.page_id)
    title = schema.get("title")
    verdict = classify_table(title)
    schema_names = {f["name"] for f in describe_schema(schema)}
    unknown = [n for n in fields if n not in schema_names]

    # 步骤2.5：幂等查重
    # 优先服务端 filter（可靠）；无字段名时退回全量首页扫描（不可靠，仅兜底并告警）
    if args.idempotency_field and args.idempotency_key:
        dup = query_by_filter(ipc, args.database_id, args.page_id,
                              args.idempotency_field, args.idempotency_op, args.idempotency_key)
        dup_mode = f"服务端 filter（{args.idempotency_field} {args.idempotency_op}）"
    else:
        records = query_records(ipc, args.database_id, args.page_id)
        dup = gate_idempotency(records, args.idempotency_key)
        dup_mode = "⚠ 仅扫描首页 50 条（未指定 --idempotency-field），可能漏检"

    # 步骤4：dry-run 回显
    print("=" * 100)
    print(f"[目标表] {title}    字段总数 {len(schema_names)}")
    print(f"[表身份判定] {verdict}")
    if unknown:
        print(f"[⚠ schema 中不存在的字段] {unknown} —— 这些字段会被服务端忽略或报错，须核对")
    print("-" * 100)
    print(render_table(fields, schema, user_provided))
    print("-" * 100)

    blocked = gate_redline(fields, user_provided)
    if blocked:
        print(f"[⛔ 红线字段拦截] {blocked}")
        print("        这些字段代表授权/承诺/证件/金融信息，Agent 不得代填。")
        print("        请由用户本人操作，或用 --user-provided 声明其已亲自提供。")

    if dup:
        print(f"[⛔ 幂等拦截] 查重方式：{dup_mode}")
        print(f"        表内已存在 {len(dup)} 条含同键 '{args.idempotency_key}' 的记录，判定为重复提交")
        for d in dup[:3]:
            print(f"        既有记录 id={d.get('_id')}  提交编号={d.get('提交编号')}  "
                  f"应用名称={d.get('应用名称')}  提交时间={d.get('提交时间')}")

    if args.dry_run:
        print("[dry-run] 只读模式结束，未写入任何记录。")
        if args.json:
            print(json.dumps({"title": title, "verdict": verdict, "blocked": blocked,
                              "duplicates": len(dup)}, ensure_ascii=False))
        return 0

    # 闸门
    fail = gate_confirm(args.confirm_written, dry_run_done=True)
    if fail:
        print(f"[⛔ 拒绝写入] {fail}")
        return 2
    if blocked:
        print("[⛔ 拒绝写入] 红线字段未处理。")
        return 2
    if dup:
        print("[⛔ 拒绝写入] 幂等查重命中，拒绝重复提交。")
        return 2
    if verdict.startswith("RISK"):
        print("[⛔ 拒绝写入] 目标表判定为 RISK（对外发布类表），须用户明确确认后另行处理。")
        return 2

    props = build_props(fields)

    # 步骤5：探针写删
    if args.probe_write:
        probe_props = dict(props)
        probe_props["应用名称"] = {"text": "__probe__"}
        probe_id = add_record(ipc, args.database_id, args.page_id, probe_props)
        ok = delete_record(ipc, probe_id)
        print(f"[探针] 写入 id={probe_id}；删除 {'成功' if ok else '失败（须立即重试并汇报残留）'}")
        if not ok:
            return 4

    # 步骤6：正式写入
    record_id = add_record(ipc, args.database_id, args.page_id, props)
    print(f"[写入] record id = {record_id}")

    # 步骤7：回读复核
    actual = get_record(ipc, args.database_id, args.page_id, record_id)
    diff = {}
    for name, spec in fields.items():
        want = spec.get("value")
        got = actual.get(name)
        if isinstance(want, (list, dict)):
            if json.dumps(want, ensure_ascii=False) not in json.dumps(got, ensure_ascii=False):
                diff[name] = {"expected": want, "actual": got}
        elif got != want:
            diff[name] = {"expected": want, "actual": got}

    if diff:
        print(f"[⛔ 回读复核不通过] {len(diff)} 个字段不一致：")
        for k, v in diff.items():
            print(f"    {k}: expected={str(v['expected'])[:80]} actual={str(v['actual'])[:80]}")
        return 5

    print(f"[✓ 回读复核通过] {len(fields)} 个字段逐项一致。")
    if args.json:
        print(json.dumps({"record_id": record_id, "verified_fields": len(fields),
                          "title": title}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
