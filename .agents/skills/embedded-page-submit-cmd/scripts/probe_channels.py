#!/usr/bin/env python3
"""内嵌智能页通道探针（只读）。

按「view / share / agent-gateway / 宿主 SDK」四类通道逐一探测可达性，
输出：通道可达性矩阵 + 目标表 schema（字段名/类型/select 选项/表 title）+ 登录态。

本脚本**不含任何写操作**（无 addRecord / updateRecord / deleteRecord / uploadImage）。
写入能力需另走 submit 流程，并须先通过用户确认闸门。

用法:
    python probe_channels.py --page-id <pageId> --database-id <databaseId>
    python probe_channels.py --page-id <pageId> --database-id <dbId> --json
"""

import argparse
import json
import os
import sys
from pathlib import Path

HOST = os.environ.get("WB_SPACE_HOST", "https://www.workbuddy.cn")

# ---------------------------------------------------------------- 依赖定位


def _safe_iterdir(p: Path) -> list[Path]:
    """列目录，跳过无权限项（Windows 盘根常有 System Volume Information）。"""
    try:
        return [c for c in p.iterdir() if c.is_dir()]
    except (PermissionError, OSError):
        return []


def find_library_root() -> Path | None:
    """定位内置 skill 库（含 workbuddy_ipc 子包）。

    查找顺序：环境变量 → 常见安装路径 → 用户级 skills 目录。
    找不到时返回 None，调用方须降级为「请用户手工填表」，不得硬扛。
    """
    candidates: list[Path] = []
    here = Path(__file__).resolve()

    env = os.environ.get("WORKBUDDY_SKILLS_ROOT")
    if env:
        candidates.append(Path(env))

    app_dir = os.environ.get("WORKBUDDY_APP_DIR")
    if app_dir:
        candidates.append(Path(app_dir) / "resources/app.asar.unpacked/resources/plugins/workbuddy-builtin/skills")

    # 宿主安装目录（Windows 常见：D:/<Vendor>/Install/<App>/resources/...）
    for parent in here.parents:
        candidates.append(parent / "resources/app.asar.unpacked/resources/plugins/workbuddy-builtin/skills")
        candidates.append(parent / "plugins/workbuddy-builtin/skills")

    # 用户级插件缓存：~/.workbuddy/plugins/cache/workbuddy-builtin/*/skills
    user_cache = Path.home() / ".workbuddy/plugins/cache/workbuddy-builtin"
    if user_cache.is_dir():
        for child in sorted(user_cache.iterdir()):
            candidates.append(child / "skills")

    # 已知宿主安装根（D:/<Vendor>/Install/<App>/）——按目录名匹配，不写死盘符
    for root in (Path("D:/"), Path("C:/")):
        if not root.is_dir():
            continue
        for vendor in _safe_iterdir(root):
            for level1 in _safe_iterdir(vendor):
                # 形如 D:/<Vendor>/Install/<App>
                if level1.name.lower() == "install":
                    app_dirs = _safe_iterdir(level1)
                else:
                    inst = level1 / "Install"
                    app_dirs = _safe_iterdir(inst) if inst.is_dir() else []
                for appdir in app_dirs:
                    candidates.append(appdir / "resources/app.asar.unpacked/resources/plugins/workbuddy-builtin/skills")
                    candidates.append(appdir / "resources/plugins/workbuddy-builtin/skills")

    seen: set[str] = set()
    for c in candidates:
        key = str(c)
        if key in seen:
            continue
        seen.add(key)
        # 库根在 skills/library 下，workbuddy_ipc 是其子包
        if (c / "library/workbuddy_ipc").is_dir():
            return c / "library"
        if (c / "workbuddy_ipc").is_dir():
            return c
    return None


def load_ipc():
    root = find_library_root()
    if root is None:
        return None, None
    sys.path.insert(0, str(root))
    try:
        import workbuddy_ipc  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return None, f"import workbuddy_ipc failed: {exc}"
    return workbuddy_ipc, None


# ---------------------------------------------------------------- 通道探测


def probe(ipc, path: str, body: dict, label: str) -> dict:
    result = {"channel": label, "path": path, "reachable": False, "code": None, "msg": None}
    try:
        r = ipc.http_request("POST", HOST + path, body=body)
    except Exception as exc:  # noqa: BLE001
        result["msg"] = str(exc)[:200]
        return result
    if isinstance(r, dict):
        result["code"] = r.get("code")
        result["msg"] = r.get("msg") or r.get("message")
        result["reachable"] = r.get("code") == 0
    else:
        result["msg"] = str(r)[:200]
    return result


def read_schema(ipc, db_id: str, page_id: str) -> tuple[dict | None, list[dict]]:
    """读目标表 schema。share 通道优先（无登录态也可读），失败再退 view。"""
    attempts = [
        ("share", "/space/api/page/share/database/get", {"databaseId": db_id, "pageId": page_id}),
        ("view", "/space/api/view/database/get", {"databaseId": db_id, "pageId": page_id}),
    ]
    for label, path, body in attempts:
        try:
            r = ipc.http_request("POST", HOST + path, body=body)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(r, dict) and r.get("code") == 0:
            return (r.get("data") or {}), [
                {"channel": label, "path": path, "reachable": True, "code": 0, "msg": None}
            ]
    return None, []


def read_user(ipc) -> tuple[dict | None, dict]:
    """读登录态。返回体形状为 {code, msg, data: {userInfo: {...}}}（2026-10-26 实测）。"""
    try:
        r = ipc.http_request("POST", HOST + "/space/api/view/user/current", body={})
    except Exception as exc:  # noqa: BLE001
        return None, {"channel": "view", "path": "/space/api/view/user/current", "reachable": False,
                      "code": None, "msg": str(exc)[:200]}
    ok = isinstance(r, dict) and r.get("code") == 0
    data = (r.get("data") or {}) if isinstance(r, dict) else {}
    return (data.get("userInfo") or None), {
        "channel": "view", "path": "/space/api/view/user/current", "reachable": ok,
        "code": r.get("code") if isinstance(r, dict) else None,
        "msg": (r.get("msg") if isinstance(r, dict) else str(r)[:200]),
    }


def describe_schema(schema: dict) -> list[dict]:
    out = []
    for p in schema.get("properties") or []:
        item = {
            "name": p.get("name"),
            "type": p.get("type"),
            "options": [o.get("text") for o in ((p.get("config") or {}).get("options") or [])],
        }
        out.append(item)
    return out


def classify_table(title: str | None) -> str:
    """目标表身份判定：标题含审核/收集/待运营关键词 → 视为投稿收集类表。

    命中「已发布/正式/名单」类关键词 → 高风险（写入即污染对外列表），须停下确认。
    """
    t = (title or "").strip()
    risky = ("已发布", "正式名单", "公示", "上线")
    safe = ("待审核", "待运营", "收集", "投稿", "登记", "问卷")
    if any(k in t for k in risky):
        return "RISK: 标题含对外发布关键词，写入即污染公开列表，须用户明确确认"
    if any(k in t for k in safe):
        return "OK: 标题含收集/待审核类关键词，符合投稿收集表特征"
    return "UNKNOWN: 标题无判定关键词，须用户确认目标表身份"


def main() -> int:
    ap = argparse.ArgumentParser(description="内嵌智能页通道探针（只读）")
    ap.add_argument("--page-id", required=True, help="页面 ID（智能页 URL 末段）")
    ap.add_argument("--database-id", required=True, help="目标数据表 ID")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    ipc, err = load_ipc()
    if ipc is None:
        msg = err or "未找到内置 skill 库（workbuddy_ipc）"
        print(f"[FATAL] {msg}")
        print("        降级：请用户在页面内手工填写（不要硬扛无登录态的裸 HTTP 请求）。")
        return 3

    matrix: list[dict] = []

    user, user_row = read_user(ipc)
    matrix.append(user_row)

    schema, schema_rows = read_schema(ipc, args.database_id, args.page_id)
    matrix.extend(schema_rows)

    # 只读写入通道可达性探测：用一个必然不存在的路径判断前缀是否有权限
    for label, path in (
        ("view", "/space/api/view/database/query"),
        ("share", "/space/api/page/share/database/query"),
    ):
        body = {"databaseId": args.database_id, "pageId": args.page_id}
        row = probe(ipc, path, body, label)
        # permission denied 也说明通道本身可达（鉴权有反应），仅 query 被拒
        row["note"] = "query 被拒不代表不可写；写权限需另经确认闸门后用探针验证"
        matrix.append(row)

    fields = describe_schema(schema) if schema else []
    verdict = classify_table((schema or {}).get("title"))

    out = {
        "host": HOST,
        "page_id": args.page_id,
        "database_id": args.database_id,
        "login": {"reachable": user_row["reachable"], "nickName": (user or {}).get("nickName"),
                  "id": (user or {}).get("id")},
        "channel_matrix": matrix,
        "schema_title": (schema or {}).get("title"),
        "schema_fields": fields,
        "table_identity_verdict": verdict,
        "write_capability": "本脚本不含写操作；写入需另走 submit 流程并先取得用户确认",
    }

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    print("=" * 60)
    print(f"HOST       : {HOST}")
    print(f"pageId     : {args.page_id}")
    print(f"databaseId : {args.database_id}")
    print("=" * 60)
    print("\n[通道可达性]")
    for row in matrix:
        flag = "OK  " if row.get("reachable") else "FAIL"
        print(f"  [{flag}] {row.get('channel'):<14} {row.get('path')}")
        if not row.get("reachable"):
            print(f"           code={row.get('code')} msg={row.get('msg')}")

    print("\n[登录态]")
    if user:
        print(f"  nickName = {user.get('nickName')}")
        print(f"  id       = {user.get('id')}")
        print("  ⚠ 请与用户口述的本人账号核对一致后再写入。")
    else:
        print("  未取得登录态信息")

    print("\n[目标表 schema]")
    if schema:
        print(f"  title = {schema.get('title')}")
        for f in fields:
            opts = (" / ".join(f["options"])) if f["options"] else ""
            print(f"    - {f['name']} [{f['type']}]{('  选项: ' + opts) if opts else ''}")
    else:
        print("  未读到 schema")

    print(f"\n[目标表身份判定]\n  {verdict}")
    print(f"\n[写入能力]\n  {out['write_capability']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
