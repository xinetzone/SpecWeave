#!/usr/bin/env python3
"""公开值取值域审计 · 高危形态扫描器。

用法：
    python scan_public_identifiers.py <项目根目录> [--json] [--identifiers a,b,c]
    python scan_public_identifiers.py <项目根目录> --only H1,H4
    python scan_public_identifiers.py <项目根目录> --allow-row-isolated public.registrations
    python scan_public_identifiers.py <项目根目录> --dry-run

检出的形态：
    H1 对外表只有表级 SELECT 授权（隐含所有列）
    H2 对外列级授权清单里含标识列
    H3 客户端字段白名单里含标识列
    H4 标识值出现在路径/URL 拼接处
    H5 RPC 返回整行（含标识列时高危）
    H6 路径型公开列的值域由调用方入参决定（含中间变量链 / INSERT 形态）
    H7 字面量路径里内嵌标识段（如 shared/2114562052432330752/activities/x.png）

分级原则：
    高 = 结构上即可判定为缺陷；中 = 取决于运行期语义（RLS 行隔离、值的实际可见性）。
    ⚠️ 静态分析判不了的**一律降为中危并要求人工确认**，不静默通过。
    ⚠️ 覆盖率为 0（没扫到任何候选文件）时退出码非 0——「没扫到」不等于「没问题」。

退出码：0 = 未发现高危；1 = 发现高危；2 = 参数/环境错误；3 = 覆盖率为 0（工具未生效）。
仅用 Python 标准库。
"""

import argparse
import json
import os
import re
import sys

DEFAULT_IDENTIFIERS = [
    # 归属类
    "owner_id", "creator_id", "created_by", "author_id", "user_id", "uid",
    "owner_uid", "creator", "operator", "assignee", "from_user", "owner_ref",
    # 身份类
    "openid", "unionid", "phone", "phone_number", "mobile", "email",
    "account", "login_name", "real_name", "id_card", "employee_no", "staff_no",
    # 凭据类
    "token",
]
PUBLIC_ROLES = ("anon", "authenticated")
SCAN_EXT = (".sql", ".js", ".cjs", ".mjs", ".ts")
SKIP_DIRS = {"node_modules", "vendor", "external", ".git", ".temp", "dist",
             "build", "__pycache__", "tests", "__snapshots__", ".venv",
             ".claude", ".workbuddy", ".meta"}
PATH_COL_RE = r"(?:[\w]*_)?(?:path|url|uri|key|location|prefix)$"
# 路径第 2 段像标识：长数字串 / wx: 前缀 / 含常见标识词的段
IDENT_SEG_RE = r"(?:\d{10,}|wx:[A-Za-z0-9_-]+|(?:user|owner|uid|account|employee)_[A-Za-z0-9_-]+)"


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
    """PUBLIC 隐含包含 anon/authenticated；ALL 含 SELECT。"""
    low = (blob or "").lower()
    if "public" in toks(low):
        return True
    return bool(toks(low) & set(PUBLIC_ROLES))


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def snippet(text, pos, width=110):
    start = text.rfind("\n", 0, pos) + 1
    end = text.find("\n", pos)
    if end < 0:
        end = len(text)
    raw = text[start:end].strip()
    return raw if len(raw) <= width else raw[: width - 1] + "…"


def norm_table(name):
    """表名归一化：public.activities / activities / "public"."activities" → 同一张表。"""
    t = (name or "").strip().strip('"').lower()
    return t.split(".")[-1]


def param_carries_identifier(param, body, identifiers):
    """判断一个入参是否可能承载用户标识。

    返回 (是否承载, 判定依据)。判定顺序：
      1. 入参名（或去掉 p_ 前缀的基名）命中标识词典 → 承载；
      2. 入参在函数体内被形状约束（正则 / LIKE 校验）→ 不承载（只能取受限字符集）；
      3. 路径型入参且无形状约束 → 承载（路径里可以塞标识）；
      4. 其余无约束入参 → 承载（值域完全由调用方决定）。
    """
    p = (param or "").lower()
    base = p[2:] if p.startswith("p_") else p
    if p in identifiers or base in identifiers:
        return True, "入参名 %s 命中标识词典" % p
    if re.search(r"\b" + re.escape(p) + r"\b\s*(!~|~|SIMILAR TO|ILIKE|LIKE)\s*'", body, re.I):
        return False, "入参 %s 被形状约束，取值只能是受限字符集，不承载标识" % p
    if re.search(PATH_COL_RE, p, re.I):
        return True, "路径型入参 %s 无形状约束，路径里可以承载标识" % p
    return True, "入参 %s 无形状约束，值域完全由调用方决定" % p


def split_statements(code):
    """按分号切语句；无分号的尾句以 EOF 结束。"""
    parts = re.split(r";", code)
    return [p for p in parts if p.strip()]


def collect(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in sorted(fn):
            if f.endswith(SCAN_EXT):
                yield os.path.join(dp, f)


# ── 跨文件全局态 ──────────────────────────────────────────────────────────
class GlobalState:
    def __init__(self):
        self.public_tables = set()   # 对外可读的表（裸名）
        self.fn_public = set()       # 授予对外角色的函数（裸名）
        self.row_isolated = set()    # 有 RLS 行隔离到本人的表（裸名）
        self.seen_grants = 0         # 解析到的授权语句数


def scan_sql(text, path, identifiers, g):
    findings = []
    rel = path
    code = strip_comments(text, is_sql=True)

    # ── 授权面：按语句切分后逐条解析（避免 [^;]+ 跨语句误匹配）
    for stmt in split_statements(code):
        gm = re.search(r"GRANT\s+(ALL|SELECT)(\s*\([^)]*\))?\s+ON\s+(?:TABLE\s+)?([\w.\"]+)\s+TO\s+([^\n]*)$",
                       stmt, re.I | re.S)
        if not gm:
            continue
        g.seen_grants += 1
        grantee = gm.group(4)
        if not is_public(grantee):
            continue
        table = norm_table(gm.group(3))
        if gm.group(1).upper() == "ALL" or not gm.group(2):
            g.public_tables.add(table)
            findings.append(dict(
                rule="H1", severity="medium", file=rel, line=line_of(text, code.find(stmt)),
                target=table,
                detail="表级/全量 GRANT（%s）授予对外角色 %s —— 隐含所有列" % (gm.group(1).upper(), grantee.strip()),
                fix="改为列级授权；或确认该表有 RLS 行级隔离到本人（用 --allow-row-isolated 显式登记）。",
                snippet=snippet(text, code.find(stmt)),
            ))
        else:
            cols = {c.lower() for c in re.findall(r"[A-Za-z_][\w]*", gm.group(2))}
            g.public_tables.add(table)
            hit = sorted(c for c in cols if c in identifiers)
            if hit:
                findings.append(dict(
                    rule="H2", severity="high", file=rel, line=line_of(text, code.find(stmt)),
                    target=table,
                    detail="对外列级授权清单含标识列：%s" % ", ".join(hit),
                    fix="从 GRANT 清单中移除标识列；标识列只留给 RLS 策略内部求值。",
                    snippet=snippet(text, code.find(stmt)),
                ))

        # 角色组间接授予：静态不可解析 → 报中危并要求人工确认
        if re.search(r"TO\s+\w+\s*$", stmt, re.I) and not is_public(grantee):
            findings.append(dict(
                rule="H1", severity="medium", file=rel, line=line_of(text, code.find(stmt)),
                target=table,
                detail="授权给非对外角色 %s —— 若是角色组且间接授予 anon/authenticated，静态分析判不了"
                       % grantee.strip(),
                fix="人工确认该角色组是否间接授予对外角色；确认后用 --allow-row-isolated 或列级授权收口。",
                snippet=snippet(text, code.find(stmt)),
            ))

    # ── RLS 行隔离检测（决定 WARN 能否降级为「已豁免」）
    for pm in re.finditer(
            r"CREATE\s+POLICY\s+[\w\"]+\s+ON\s+(?:TABLE\s+)?([\w.\"]+)\s+.*?USING\s*\(([^;]*)\)",
            code, re.I | re.S):
        if re.search(r"auth\.uid\(\)", pm.group(2), re.I):
            g.row_isolated.add(norm_table(pm.group(1)))

    # ── EXECUTE 授权
    for fm in re.finditer(r"GRANT\s+EXECUTE\s+ON\s+FUNCTION\s+([\w.\"]+)\s*\(", code, re.I):
        tail = code[fm.end(): fm.end() + 220]
        tm = re.search(r"TO\s+([^;]+);", tail)
        if tm and is_public(tm.group(1)):
            g.fn_public.add(norm_table(fm.group(1)))

    # ── H5 RPC 返回整行（含复合类型）
    for m in re.finditer(r"RETURNS\s+(?:SETOF\s+)?([\w.\"]+)", code, re.I):
        t = norm_table(m.group(1))
        if t in ("text", "boolean", "integer", "bigint", "void", "json", "jsonb"):
            continue
        findings.append(dict(
            rule="H5", severity="medium", file=rel, line=line_of(text, m.start()),
            target=t,
            detail="函数返回整行/复合类型 %s —— 响应体可能带出未授权的标识列" % m.group(1),
            fix="改为只返回必要标量（RETURNS TEXT / BOOLEAN），或确认该表有 RLS 行隔离到本人。",
            snippet=snippet(text, m.start()),
        ))

    # ── H6 路径型公开列的值域由入参决定
    # 函数体按任意 dollar-quote tag 捕获（$$ / $fn$ / $func$ …）
    for fm in re.finditer(
            r"CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+([\w.\"]+)\s*\(([^)]*)\)(.*?)\$[A-Za-z_]*\$;",
            code, re.I | re.S):
        fn_name, args, body = fm.group(1), fm.group(2), fm.group(3)
        arg_types = {}
        for item in args.split(","):
            parts = item.strip().split()
            if len(parts) >= 2:
                arg_types[parts[0].strip('"').lower()] = parts[1].strip('"').upper()
        p_params = {k for k, v in arg_types.items() if k.startswith("p_") and v.startswith("TEXT")}

        # 变量传递链：哪些局部变量最终承载了入参
        tainted = set(p_params)
        sources = {p: {p} for p in p_params}
        for _ in range(4):  # 多轮传播，够覆盖常见中转层数
            for vm in re.finditer(r"(\w+)\s*:=\s*([^;]+);", body, re.I):
                lhs = vm.group(1).lower()
                rhs = vm.group(2)
                hit = [t for t in tainted
                       if re.search(r"\b" + re.escape(t) + r"\b", rhs, re.I)]
                if hit:
                    tainted.add(lhs)
                    sources[lhs] = set().union(*[sources.get(t, {t}) for t in hit])

        for sm in re.finditer(
                r"UPDATE\s+([\w.\"]+)\s+SET\s+([\w\"]+)\s*=\s*([\w\"]+)"
                r"|INSERT\s+INTO\s+([\w.\"]+)\s*\([^)]*\b([\w\"]+)\b[^)]*\)\s*VALUES\s*\(([^)]*)\)",
                body, re.I):
            if sm.group(1):
                table, col, expr = norm_table(sm.group(1)), sm.group(2).strip('"'), sm.group(3).strip('"')
                pos = fm.start(3) + sm.start()
            else:
                table = norm_table(sm.group(4))
                col = sm.group(5).strip('"')
                vals = sm.group(6)
                expr = "?"
                for v in vals.split(","):
                    if re.search(r"\b" + r"p_[a-z_]+" + r"\b", v, re.I):
                        expr = v.strip()
                        break
                pos = fm.start(3) + sm.start()
            if not re.search(PATH_COL_RE, col, re.I):
                continue
            if expr != "?" and expr.lower() not in tainted:
                continue
            if fn_name.split(".")[-1].lower() not in g.fn_public:
                continue
            if table not in g.public_tables:
                continue
            # 值域由入参决定 ≠ 泄露：关键是**该入参是否承载标识**。
            #   入参名命中标识词典 → 承载标识
            #   入参被形状约束（如 slug 的 ^[a-z0-9-]{1,64}$）→ 不承载标识
            #   路径型入参且无形状约束 → 路径里可以塞标识
            src = sources.get(expr.lower(), {expr.lower()}) if expr != "?" else {expr.lower()}
            carries, why = False, ""
            for p in sorted(src):
                carries, why = param_carries_identifier(p, body, identifiers)
                if carries:
                    break
            if table in g.row_isolated:
                sev, extra = "waived", "（该表有 RLS 行隔离到本人 → 自动豁免）"
            elif carries:
                sev, extra = "high", "；" + why
            else:
                sev, extra = "medium", "；" + why
            findings.append(dict(
                rule="H6", severity=sev, file=rel, line=line_of(text, pos), target=fn_name,
                detail="函数 %s 把调用方传入的 %s 写进对外可读表 %s 的路径型列 %s —— 该列取值域由调用方决定%s"
                       % (fn_name, expr, table, col, extra),
                fix="目标路径改由服务端拼出（调用方不传路径），并把该写入函数收回 service_role；"
                    "如确需给终端用户用，另开一个只返回规范路径的 RPC，且该 RPC 不得接受路径入参。",
                snippet=snippet(text, pos),
            ))

    # ── H7 字面量路径里内嵌标识段
    for m in re.finditer(r"['\"]([a-z_]+/[^'\"\s]{0,120}/[^'\"\s]*)['\"]", code, re.I):
        path = m.group(1)
        segs = path.split("/")
        if len(segs) < 2:
            continue
        if segs[0].lower() not in ("users", "shared", "user_private", "app_shared",
                                  "uploads", "files", "media", "assets"):
            continue
        if re.fullmatch(IDENT_SEG_RE, segs[1]):
            findings.append(dict(
                rule="H7", severity="high", file=rel, line=line_of(text, m.start()),
                target=path,
                detail="字面量路径第 2 段内嵌标识形态：%s" % segs[1],
                fix="若该路径会被写进对外可读列，路径必须由服务端拼出；"
                    "若这是历史数据/种子脚本的残留值，改为不含标识段的规范路径。",
                snippet=snippet(text, m.start()),
            ))
    return findings


def scan_js(text, path, identifiers, g):
    findings = []
    rel = path
    code = strip_comments(text, is_sql=False)

    for m in re.finditer(r"\.select\(\s*['\"]([^'\"]+)['\"]", code):
        cols = [c.strip().lower() for c in m.group(1).split(",") if c.strip()]
        hit = [c for c in cols if c in identifiers]
        if hit:
            findings.append(dict(
                rule="H3", severity="medium", file=rel, line=line_of(text, m.start()),
                target="select()",
                detail="客户端字段白名单含标识列：%s（判定依赖后端把该串原样当白名单列，"
                       "非 PostgREST 语义需人工确认）" % ", ".join(hit),
                fix="客户端不请求标识列；归属判定交服务端完成。",
                snippet=snippet(text, m.start()),
            ))
    for m in re.finditer(r"const\s+\w*FIELDS?\w*\s*=\s*['\"]([^'\"]+)['\"]", code):
        cols = [c.strip().lower() for c in m.group(1).split(",") if c.strip()]
        hit = [c for c in cols if c in identifiers]
        if hit:
            findings.append(dict(
                rule="H3", severity="medium", file=rel, line=line_of(text, m.start()),
                target="FIELDS",
                detail="客户端字段白名单含标识列：%s" % ", ".join(hit),
                fix="客户端不请求标识列；归属判定交服务端完成。",
                snippet=snippet(text, m.start()),
            ))

    # H4：标识值出现在路径/URL 拼接的代码里（收紧：必须是独立标识符且非复合词）
    pathish = r"(?:users|shared|user_private|app_shared|uploads?|files?|media|assets?)[/'\"]"
    for m in re.finditer(pathish, code, re.I):
        window = code[max(0, m.start() - 100): m.start() + 140]
        hit = []
        for t in identifiers:
            for wm in re.finditer(r"\b" + re.escape(t) + r"\b", window, re.I):
                nxt = window[wm.end(): wm.end() + 1]
                if nxt in ("-", "_"):      # mobile-navigation 这类复合词不算命中
                    continue
                hit.append(t)
                break
        if not hit:
            for vm in re.finditer(r"\$\{([^}]*)\}", window):
                low = vm.group(1).lower()
                if any(re.search(r"\b" + re.escape(t) + r"\b", low) for t in identifiers):
                    hit = [vm.group(1).strip()]
                    break
        if hit:
            findings.append(dict(
                rule="H4", severity="medium", file=rel, line=line_of(text, m.start()),
                target="path",
                detail="标识值 %s 出现在路径/URL 拼接处：%s" % (", ".join(hit), snippet(text, m.start())),
                fix="确认该路径是否会写进对外可读列；若是，路径必须由服务端拼出，"
                    "或改用不含标识的规范路径（如应用归属作用域）。",
                snippet=snippet(text, m.start()),
            ))

    # JS/TS 里内嵌 SQL：给显式告警（避免「扫不到就当没问题」）
    if re.search(r"\b(GRANT|REVOKE|CREATE\s+POLICY|CREATE\s+OR\s+REPLACE\s+FUNCTION)\b", code, re.I):
        findings.append(dict(
            rule="H4", severity="medium", file=rel, line=line_of(text, 0), target="embedded-sql",
            detail="该文件内嵌 SQL（GRANT/POLICY/FUNCTION）——本工具只按 .sql 扩展名解析 SQL，此处未覆盖",
            fix="把 SQL 抽到 .sql 文件供工具解析，或人工复核这段授权语句。",
            snippet=snippet(text, 0),
        ))
    return findings


def main():
    ap = argparse.ArgumentParser(description="公开值取值域审计 · 高危形态扫描器")
    ap.add_argument("root")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--identifiers", default="")
    ap.add_argument("--only", default="")
    ap.add_argument("--allow-row-isolated", default="", help="显式登记行级隔离到本人的表（逗号分隔）")
    ap.add_argument("--dry-run", action="store_true", help="只读模式：仅报告，不产生任何写操作（本工具本就只读）")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print("错误：目录不存在 %s" % root, file=sys.stderr)
        return 2

    identifiers = set(DEFAULT_IDENTIFIERS)
    if args.identifiers:
        identifiers |= {t.strip().lower() for t in args.identifiers.split(",") if t.strip()}
    only = {t.strip().upper() for t in args.only.split(",") if t.strip()}
    allowed = {norm_table(t) for t in args.allow_row_isolated.split(",") if t.strip()}

    g = GlobalState()
    findings = []
    files = []
    for path in collect(root):
        text = read_text(path)
        if not text:
            continue
        files.append(path)
        rel = os.path.relpath(path, root).replace("\\", "/")
        got = scan_sql(text, path, identifiers, g) if path.endswith(".sql") else scan_js(text, path, identifiers, g)
        if only:
            got = [f for f in got if f["rule"] in only]
        findings.extend(got)

    # 豁免：行级隔离到本人（显式登记或自动检测到 RLS）→ 降级为「已豁免」
    waived = []
    for f in list(findings):
        if f["rule"] not in ("H1", "H6"):
            continue
        tbl = f.get("target", "").split(".")[-1]
        if tbl not in allowed and tbl not in g.row_isolated:
            continue
        # H1：表级授权 + 行隔离到本人 → 该表行他人看不到，不是泄露面
        # H6：值写入行隔离到本人的表 → 写入值只对本人可见，不是泄露面
        if f["severity"] == "medium" and f["rule"] == "H1":
            f["severity"] = "waived"
            f["detail"] += "（已豁免：%s 登记/检测到 RLS 行隔离到本人）" % tbl
            waived.append(f)
        elif f["severity"] == "high":
            f["severity"] = "waived"
            f["detail"] += "（已豁免：%s 登记/检测到 RLS 行隔离到本人）" % tbl
            waived.append(f)

    high = [f for f in findings if f["severity"] == "high"]
    medium = [f for f in findings if f["severity"] == "medium"]
    coverage = dict(files=len(files), grants_parsed=g.seen_grants,
                    public_tables=len(g.public_tables), row_isolated=len(g.row_isolated))

    if args.json:
        print(json.dumps(dict(root=root, findings=findings, high=len(high), medium=len(medium),
                              waived=len(waived), coverage=coverage),
                         ensure_ascii=False, indent=2))
        return 1 if high else (3 if not files else 0)

    print("公开值取值域审计 · 扫描 %s" % root)
    print("覆盖：文件 %d · 授权语句 %d · 对外表 %d · 检测到行隔离 %d"
          % (coverage["files"], coverage["grants_parsed"], coverage["public_tables"],
             coverage["row_isolated"]))
    print("标识列词典 %d 项：高危 %d 条，中危 %d 条，已豁免 %d 条\n"
          % (len(identifiers), len(high), len(medium), len(waived)))

    if not files:
        print("未扫描到任何候选文件（.sql/.js/.cjs/.mjs/.ts）——这是「工具没生效」，不是「项目没问题」。")
        print("请确认扫描路径是否正确；本工具不扫描 .ts 内的 SQL 模板。")
        return 3

    if not findings:
        print("未发现需要人工确认的形态。")
        return 0

    for sev, title in (("high", "高危"), ("medium", "中危"), ("waived", "已豁免")):
        group = [f for f in findings if f["severity"] == sev]
        if not group:
            continue
        print("── %s %d 条 ──" % (title, len(group)))
        for f in group:
            print("\n[%s] %s:%d  目标=%s" % (f["rule"], f["file"], f["line"], f["target"]))
            print("  现象：%s" % f["detail"])
            print("  建议：%s" % f["fix"])
            print("  原文：%s" % f["snippet"])
        print("")

    print("提示：中危项需人工确认 RLS 行隔离与该值的实际可见性；")
    print("      高危项结构上必然把标识发出，应一律处理。")
    return 1 if high else 0


if __name__ == "__main__":
    sys.exit(main())
