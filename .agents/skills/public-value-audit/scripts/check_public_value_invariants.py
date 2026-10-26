#!/usr/bin/env python3
"""公开值取值域审计 · 不变量断言器（可挂 CI）。

用法：
    python check_public_value_invariants.py <项目根目录> [--json]
    python check_public_value_invariants.py <项目根目录> --identifiers owner_id,uid
    python check_public_value_invariators.py <项目根目录> --allow-row-isolated public.registrations
    python check_public_value_invariants.py <项目根目录> --dry-run

不变量：
    I1  对外角色的列级授权清单里不含标识列            [FAIL —— 结构上即可判定]
    I2  客户端请求的列必须落在服务端列级授权清单内      [FAIL —— 否则整表查询失败]
    I3  路径型公开列的值域不由调用方入参决定           [FAIL —— 结构事实；行隔离则豁免]
    I4  对外 RPC 不返回整行/复合类型                    [WARN —— 行隔离则豁免]
    I5  客户端字段白名单不含标识列                      [FAIL —— 结构上即可判定]
    I6  对外表不得只有表级授权                         [FAIL —— 表级 ≡ 全列可见]
    I7  字面量路径不得内嵌标识段                        [FAIL —— 结构上即可判定]

关于 FAIL / WARN / 豁免的分界：
    · 结构上即可判定的（授权清单直接含标识列、客户端主动请求、表级授权、
      值域由入参决定、字面量含标识）一律 FAIL；
    · 只有「返回整行」这一类依赖运行期语义的标 WARN；
    · 若脚本在该表上检测到 RLS 行级隔离到本人（策略 USING 含 auth.uid()），
      对应项自动降为「已豁免」；也可用 --allow-row-isolated 显式登记。
    · 覆盖率为 0（没扫到任何候选文件）时退出码非 0——「没扫到」不等于「没问题」。

退出码：0 = 无 FAIL；1 = 有 FAIL；2 = 参数错误；3 = 覆盖率为 0。
仅用 Python 标准库。
"""

import argparse
import json
import os
import re
import sys

DEFAULT_IDENTIFIERS = [
    "owner_id", "creator_id", "created_by", "author_id", "user_id", "uid",
    "owner_uid", "creator", "operator", "assignee", "from_user", "owner_ref",
    "openid", "unionid", "phone", "phone_number", "mobile", "email",
    "account", "login_name", "real_name", "id_card", "employee_no", "staff_no",
    "token",
]
PUBLIC_ROLES = ("anon", "authenticated")
SCAN_EXT = (".sql", ".js", ".cjs", ".mjs", ".ts")
SKIP_DIRS = {"node_modules", "vendor", "external", ".git", ".temp", "dist",
             "build", "__pycache__", "tests", "__snapshots__", ".venv",
             ".claude", ".workbuddy", ".meta"}
PATH_COL_RE = r"(?:[\w]*_)?(?:path|url|uri|key|location|prefix)$"
IDENT_SEG_RE = r"(?:\d{10,}|wx:[A-Za-z0-9_-]+|(?:user|owner|uid|account|employee)_[A-Za-z0-9_-]+)"
SCALAR_TYPES = {"text", "boolean", "integer", "bigint", "void", "json", "jsonb"}


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def strip_comments(text, is_sql):
    out = list(text)
    pat = re.compile(r"--[^\n]*" if is_sql else r"//[^\n]*")
    for m in pat.finditer(text):
        for i in range(m.start(), m.end()):
            out[i] = " "
    for m in re.finditer(r"/\*.*?\*/", text, re.S):
        for i in range(m.start(), m.end()):
            if out[i] != "\n":
                out[i] = " "
    return "".join(out)


def toks(blob):
    return {t.strip().strip('"').lower() for t in re.split(r"[,\s]+", blob or "") if t.strip()}


def is_public(blob):
    low = (blob or "").lower()
    if "public" in toks(low):
        return True
    return bool(toks(low) & set(PUBLIC_ROLES))


def param_carries_identifier(param, body, identifiers):
    """判断一个入参是否可能承载用户标识（与扫描器同源，判定口径必须一致）。

    1. 入参名（或去 p_ 前缀的基名）命中标识词典 → 承载；
    2. 入参在函数体内被形状约束 → 不承载（只能取受限字符集）；
    3. 路径型入参且无形状约束 → 承载；
    4. 其余无约束入参 → 承载。
    """
    pr = (param or "").lower()
    base = pr[2:] if pr.startswith("p_") else pr
    if pr in identifiers or base in identifiers:
        return True, "入参名 %s 命中标识词典" % pr
    if re.search(r"\b" + re.escape(pr) + r"\b\s*(!~|~|SIMILAR TO|ILIKE|LIKE)\s*'", body, re.I):
        return False, "入参 %s 被形状约束，不承载标识" % pr
    if re.search(PATH_COL_RE, pr, re.I):
        return True, "路径型入参 %s 无形状约束，路径里可以承载标识" % pr
    return True, "入参 %s 无形状约束，值域完全由调用方决定" % pr


def norm_table(name):
    t = (name or "").strip().strip('"').lower()
    return t.split(".")[-1]


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def collect(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in sorted(fn):
            if f.endswith(SCAN_EXT):
                yield os.path.join(dp, f)


class GlobalState:
    def __init__(self):
        self.col_grants = {}     # 裸表名 -> 授权列集合
        self.table_grants = set()
        self.table_columns = {}
        self.fn_public = set()
        self.row_isolated = set()
        self.seen_grants = 0
        self.seen_files = 0


def parse_sql(text, rel, g):
    code = strip_comments(text, is_sql=True)

    for m in re.finditer(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w.\"]+)\s*\((.*?)\n\);",
                         code, re.I | re.S):
        table = norm_table(m.group(1))
        cols = set()
        for cm in re.finditer(r"^\s{2,}([\w\"]+)\s+[A-Za-z]", m.group(2), re.M):
            cols.add(cm.group(1).strip('"').lower())
        g.table_columns.setdefault(table, set()).update(cols)

    for stmt in re.split(r";", code):
        if not stmt.strip():
            continue
        gm = re.search(r"GRANT\s+(ALL|SELECT)(\s*\([^)]*\))?\s+ON\s+(?:TABLE\s+)?([\w.\"]+)\s+TO\s+([^\n]*)$",
                       stmt, re.I | re.S)
        if not gm:
            continue
        g.seen_grants += 1
        if not is_public(gm.group(4)):
            continue
        table = norm_table(gm.group(3))
        if gm.group(1).upper() == "ALL" or not gm.group(2):
            g.table_grants.add(table)
        else:
            cols = {c.lower() for c in re.findall(r"[A-Za-z_][\w]*", gm.group(2))}
            g.col_grants.setdefault(table, set()).update(cols)

    for m in re.finditer(r"CREATE\s+POLICY\s+[\w\"]+\s+ON\s+(?:TABLE\s+)?([\w.\"]+)\s+.*?USING\s*\(([^;]*)\)",
                         code, re.I | re.S):
        if re.search(r"auth\.uid\(\)", m.group(2), re.I):
            g.row_isolated.add(norm_table(m.group(1)))

    for m in re.finditer(r"GRANT\s+EXECUTE\s+ON\s+FUNCTION\s+([\w.\"]+)\s*\(", code, re.I):
        tail = code[m.end(): m.end() + 220]
        tm = re.search(r"TO\s+([^;]+);", tail)
        if tm and is_public(tm.group(1)):
            g.fn_public.add(norm_table(m.group(1)))

    return code


def parse_js(text, rel):
    code = strip_comments(text, is_sql=False)
    consts = {}
    for m in re.finditer(r"(?:const|let|var)\s+(\w+)\s*=\s*['\"]([^'\"]+)['\"]", code):
        consts[m.group(1)] = [c.strip().lower() for c in m.group(2).split(",") if c.strip()]

    reads = []
    for m in re.finditer(r"\.from\(\s*['\"]([\w.]+)['\"]\s*\)", code):
        table = norm_table(m.group(1))
        window = code[m.end(): m.end() + 300]
        sm = re.search(r"\.select\(\s*(['\"])([^'\"]+)\1", window)
        if sm:
            cols = [c.strip().lower() for c in sm.group(2).split(",") if c.strip()]
        else:
            vm = re.search(r"\.select\(\s*(\w+)\s*\)", window)
            if not vm or vm.group(1) not in consts:
                continue
            cols = consts[vm.group(1)]
        reads.append((table, cols, line_of(text, m.start())))

    loose = []
    for m in re.finditer(r"const\s+(\w*FIELDS?\w*)\s*=\s*['\"]([^'\"]+)['\"]", code):
        cols = [c.strip().lower() for c in m.group(2).split(",") if c.strip()]
        loose.append((m.group(1), cols, line_of(text, m.start())))

    return code, reads, loose


INV_NAMES = {
    "I1": "对外列级授权不含标识列",
    "I2": "客户端请求列 ⊆ 服务端列级授权清单",
    "I3": "路径型列取值域不由调用方入参决定",
    "I4": "对外 RPC 不返回整行/复合类型",
    "I5": "客户端字段白名单不含标识列",
    "I6": "对外表不得只有表级授权",
    "I7": "字面量路径不含标识段",
}


def main():
    ap = argparse.ArgumentParser(description="公开值取值域审计 · 不变量断言器")
    ap.add_argument("root")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--identifiers", default="")
    ap.add_argument("--allow-row-isolated", default="",
                    help="显式登记「行级隔离到本人」的表（逗号分隔；写裸名或带 public. 前缀均可）")
    ap.add_argument("--dry-run", action="store_true", help="只读模式（本工具本就只读）")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print("错误：目录不存在 %s" % root, file=sys.stderr)
        return 2

    identifiers = set(DEFAULT_IDENTIFIERS)
    if args.identifiers:
        identifiers |= {t.strip().lower() for t in args.identifiers.split(",") if t.strip()}
    user_allowed = [t for t in args.allow_row_isolated.split(",") if t.strip()]
    allowed = {norm_table(t) for t in user_allowed}

    g = GlobalState()
    findings = []
    js_reads, js_loose = [], []

    def add(inv, rel, line, msg, sev):
        findings.append((inv, rel, line, msg, sev))

    for p in collect(root):
        text = read_text(p)
        if not text:
            continue
        g.seen_files += 1
        rel = os.path.relpath(p, root).replace("\\", "/")
        if p.endswith(".sql"):
            code = parse_sql(text, rel, g)
        else:
            code, reads, loose = parse_js(text, rel)
            js_reads += [(rel,) + r for r in reads]
            js_loose += [(rel,) + r for r in loose]

        # I7 字面量路径含标识段
        for m in re.finditer(r"['\"]([a-z_]+/[^'\"\s]{0,120}/[^'\"\s]*)['\"]", code, re.I):
            segs = m.group(1).split("/")
            if len(segs) < 2:
                continue
            if segs[0].lower() not in ("users", "shared", "user_private", "app_shared",
                                       "uploads", "files", "media", "assets"):
                continue
            if re.fullmatch(IDENT_SEG_RE, segs[1]):
                add("I7", rel, line_of(text, m.start()),
                    "字面量路径第 2 段内嵌标识形态：%s（路径 %s）" % (segs[1], m.group(1)), "FAIL")

    # I1 对外列级授权含标识列
    for table, cols in g.col_grants.items():
        hit = sorted(c for c in cols if c in identifiers)
        if hit:
            add("I1", "-", 0, "表 %s 的对外列级授权含标识列：%s" % (table, ", ".join(hit)), "FAIL")

    # I6 对外表只有表级授权
    for table in sorted(g.table_grants):
        cols = g.table_columns.get(table, set())
        hit = sorted(c for c in cols if c in identifiers)
        if not hit:
            continue
        if table in allowed or table in g.row_isolated:
            add("I6", "-", 0, "（已豁免：%s 登记/检测到 RLS 行隔离到本人）" % table, "WAIVED")
        else:
            add("I6", "-", 0,
                "表 %s 只有表级对外授权，且含标识列 %s —— 表级授权 ≡ 全列可见，"
                "无法证明标识列未下发" % (table, ", ".join(hit)), "FAIL")

    # I4 RPC 返回整行/复合类型
    for p in collect(root):
        if not p.endswith(".sql"):
            continue
        text = read_text(p)
        if not text:
            continue
        rel = os.path.relpath(p, root).replace("\\", "/")
        code = strip_comments(text, is_sql=True)
        for m in re.finditer(r"RETURNS\s+(?:SETOF\s+)?([\w.\"]+)", code, re.I):
            t = norm_table(m.group(1))
            if t in SCALAR_TYPES:
                continue
            cols = g.table_columns.get(t, set())
            hit = sorted(c for c in cols if c in identifiers)
            if not hit:
                continue
            if t in allowed or t in g.row_isolated:
                add("I4", rel, 0, "（已豁免：%s 登记/检测到 RLS 行隔离到本人）" % t, "WAIVED")
            else:
                add("I4", rel, 0,
                    "存在返回整行 %s（含标识列 %s）的函数" % (t, ", ".join(hit)), "WARN")

    # I3 路径型列取值域由入参决定
    for p in collect(root):
        if not p.endswith(".sql"):
            continue
        text = read_text(p)
        if not text:
            continue
        rel = os.path.relpath(p, root).replace("\\", "/")
        code = strip_comments(text, is_sql=True)
        for fm in re.finditer(
                r"CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+([\w.\"]+)\s*\(([^)]*)\)(.*?)\$[A-Za-z_]*\$;",
                code, re.I | re.S):
            fn_name, arglist, body = fm.group(1), fm.group(2), fm.group(3)
            if norm_table(fn_name) not in g.fn_public:
                continue
            arg_types = {}
            for item in arglist.split(","):
                parts = item.strip().split()
                if len(parts) >= 2:
                    arg_types[parts[0].strip('"').lower()] = parts[1].strip('"').upper()
            tainted = {k for k, v in arg_types.items() if k.startswith("p_") and v.startswith("TEXT")}
            sources = {k: {k} for k in tainted}
            for _ in range(4):
                for vm in re.finditer(r"(\w+)\s*:=\s*([^;]+);", body, re.I):
                    hit = [t for t in tainted
                           if re.search(r"\b" + re.escape(t) + r"\b", vm.group(2), re.I)]
                    if hit:
                        tainted.add(vm.group(1).lower())
                        sources[vm.group(1).lower()] = set().union(
                            *[sources.get(t, {t}) for t in hit])
            for sm in re.finditer(
                    r"UPDATE\s+([\w.\"]+)\s+SET\s+([\w\"]+)\s*=\s*([\w\"]+)"
                    r"|INSERT\s+INTO\s+([\w.\"]+)\s*\([^)]*\b([\w\"]+)\b[^)]*\)\s*VALUES\s*\(([^)]*)\)",
                    body, re.I):
                if sm.group(1):
                    table, col, expr = norm_table(sm.group(1)), sm.group(2).strip('"'), sm.group(3).strip('"')
                else:
                    table, col = norm_table(sm.group(4)), sm.group(5).strip('"')
                    expr = "?"
                    for v in sm.group(6).split(","):
                        if re.search(r"\bp_[a-z_]+\b", v, re.I):
                            expr = v.strip()
                            break
                if not re.search(PATH_COL_RE, col, re.I):
                    continue
                if expr != "?" and expr.lower() not in tainted:
                    continue
                if table not in g.col_grants and table not in g.table_grants:
                    continue
                pos = fm.start(3) + sm.start()
                src = sources.get(expr.lower(), {expr.lower()}) if expr != "?" else {expr.lower()}
                carries, why = False, ""
                for pr in sorted(src):
                    carries, why = param_carries_identifier(pr, body, identifiers)
                    if carries:
                        break
                if table in allowed or table in g.row_isolated:
                    add("I3", rel, line_of(text, pos),
                        "（已豁免：%s 登记/检测到 RLS 行隔离到本人）" % table, "WAIVED")
                elif carries:
                    add("I3", rel, line_of(text, pos),
                        "函数 %s 把入参 %s 写进对外可读表 %s 的路径型列 %s —— 取值域由调用方决定；%s"
                        % (fn_name, expr, table, col, why), "FAIL")
                else:
                    add("I3", rel, line_of(text, pos),
                        "（中危·需人工确认）函数 %s 的入参 %s 决定路径型列 %s 的取值域，但该入参不承载标识：%s"
                        % (fn_name, expr, col, why), "WARN")

    # I2 / I5 客户端读路径
    for rel, table, cols, line in js_reads:
        hit = sorted(c for c in cols if c in identifiers)
        if hit:
            add("I5", rel, line, "客户端读取表 %s 的字段含标识列：%s" % (table, ", ".join(hit)), "FAIL")
        if table in g.col_grants:
            missing = [c for c in cols if c not in g.col_grants[table]]
            if missing:
                add("I2", rel, line,
                    "客户端请求表 %s 的列 %s 不在服务端列级授权清单内（会整表 42501）"
                    % (table, ", ".join(missing)), "FAIL")
    for rel, name, cols, line in js_loose:
        hit = sorted(c for c in cols if c in identifiers)
        if hit:
            add("I5", rel, line, "客户端字段白名单 %s 含标识列：%s" % (name, ", ".join(hit)), "FAIL")

    fails = [f for f in findings if f[4] == "FAIL"]
    warns = [f for f in findings if f[4] == "WARN"]
    waived = [f for f in findings if f[4] == "WAIVED"]
    coverage = dict(files=g.seen_files, grants_parsed=g.seen_grants,
                    public_tables=len(g.col_grants) + len(g.table_grants),
                    row_isolated=len(g.row_isolated))

    # 豁免表名未命中任何已发现的表 → 显式告警（避免静默失效）
    unmatched = [t for t in user_allowed
                 if norm_table(t) not in (g.col_grants.keys() | g.table_grants | g.row_isolated)]

    if args.json:
        print(json.dumps(dict(root=root, fail=len(fails), warn=len(warns), waived=len(waived),
                              coverage=coverage, unmatched_allow=unmatched, findings=findings),
                         ensure_ascii=False, indent=2))
        return 1 if fails else (3 if not g.seen_files else 0)

    print("公开值取值域审计 · 不变量断言（%s）\n" % root)
    print("覆盖：文件 %d · 授权语句 %d · 对外表 %d · 检测到行隔离 %d"
          % (coverage["files"], coverage["grants_parsed"], coverage["public_tables"],
             coverage["row_isolated"]))
    if not g.seen_files:
        print("未扫描到任何候选文件（.sql/.js/.cjs/.mjs/.ts）——这是「工具没生效」，不是「项目没问题」。")
        return 3
    if unmatched:
        print("警告：--allow-row-isolated 里的表名未匹配任何已发现的表，豁免未生效：%s" % ", ".join(unmatched))
    print("")

    for key in sorted(INV_NAMES):
        items = [f for f in findings if f[0] == key]
        hard = [f for f in items if f[4] == "FAIL"]
        soft = [f for f in items if f[4] == "WARN"]
        wvd = [f for f in items if f[4] == "WAIVED"]
        if hard:
            print("  ❌ %s  %s  （%d 处）" % (key, INV_NAMES[key], len(hard)))
            for _, rel, line, msg, _s in hard:
                print("       %s:%s  %s" % (rel, line or "-", msg))
        elif soft:
            print("  ⚠️  %s  %s  （%d 处 · 需人工确认行级隔离）" % (key, INV_NAMES[key], len(soft)))
            for _, rel, line, msg, _s in soft:
                print("       %s:%s  %s" % (rel, line or "-", msg))
        elif wvd:
            print("  🔓 %s  %s  （%d 处已豁免）" % (key, INV_NAMES[key], len(wvd)))
            for _, rel, line, msg, _s in wvd:
                print("       %s:%s  %s" % (rel, line or "-", msg))
        else:
            print("  ✅ %s  %s" % (key, INV_NAMES[key]))

    print("")
    print("结果：FAIL %d · WARN %d · 已豁免 %d" % (len(fails), len(warns), len(waived)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
