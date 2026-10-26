# -*- coding: utf-8 -*-
"""把 scripts/db/fn_*.sql 里的函数定义逐条应用到云端。

为什么用脚本而不是手抄：
  函数体有 100~200 行、含 $$ dollar-quote 与中文错误文案，
  手抄进工具调用必然产生漂移，且漂移后很难察觉（语法合法但逻辑不同）。
  脚本直接从「单一真相源」文件读取 → base64 → 交给云端 SQL 端点执行，
  执行内容与仓库文件逐字节一致。

云端 MCP 端点不支持多语句，且长 SQL 需转义：
  故用 sqlBase64 通道传同一条语句的 base64 编码。
"""
import base64
import json
import pathlib
import sys

DB_DIR = pathlib.Path(__file__).resolve().parent.parent / "db"

# 函数文件 → 云端要执行的语句提取规则
# 绝大多数文件整份就是一条 CREATE OR REPLACE FUNCTION ... $$ ... $$;
# 但文件里还夹着 REVOKE/GRANT 权限语句（同一文件内多语句），
# 因此统一按「分号切句 + 过滤注释与空句」拆成单条执行。
FILES = [
    "fn_activity_templates.sql",
    "fn_create_activity.sql",
    "fn_update_activity.sql",
    "fn_my_activities.sql",
    "fn_migrate_activity_template.sql",
]


def split_statements(sql: str):
    """按顶层分号切句，保留 dollar-quoted 函数体不被切断。"""
    out = []
    buf = []
    in_dollar = False
    tag = None
    i = 0
    while i < len(sql):
        if not in_dollar:
            m = sql.find("$$", i)
            if m != -1:
                # 必须连 $$ 一起收进 buf：漏掉开启标签会让函数体变成
                # 「AS + DECLARE ...」，Postgres 报 syntax error at or near "DECLARE"。
                buf.append(sql[i : m + 2])
                in_dollar = True
                i = m + 2
                continue
            ch = sql[i]
            buf.append(ch)
            if ch == ";":
                stmt = "".join(buf).strip()
                if stmt:
                    out.append(stmt)
                buf = []
            i += 1
        else:
            m = sql.find("$$", i)
            if m == -1:
                buf.append(sql[i:])
                break
            buf.append(sql[i : m + 2])
            in_dollar = False
            i = m + 2
    tail = "".join(buf).strip()
    if tail:
        out.append(tail)
    return out


def strip_leading_comments(stmt: str) -> str:
    """只剥掉语句【开头】的整行注释块。

    不能整篇剥：dollar-quoted 函数体内部本来就带大量中文说明注释，
    那些是函数语义的一部分（写明每条校验为什么这么设计），删掉会让
    云端函数体与仓库定义不再逐字一致，失去「单一真相源」的意义。

    剥的范围限定在第一条非注释、非空行之前——那才是文件头部的说明块。
    """
    lines = stmt.split("\n")
    idx = 0
    while idx < len(lines):
        s = lines[idx].strip()
        if s.startswith("--") or s == "":
            idx += 1
            continue
        break
    return "\n".join(lines[idx:]).strip()


def collect():
    """返回 [(标签, 单条SQL)]，按文件顺序、文件内顺序。"""
    result = []
    for name in FILES:
        path = DB_DIR / name
        if not path.exists():
            print("MISSING", name)
            continue
        raw = path.read_text(encoding="utf-8")
        for idx, stmt in enumerate(split_statements(raw), 1):
            body = strip_leading_comments(stmt)
            if not body:
                continue
            result.append(("%s#%d" % (name, idx), body))
    return result


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "list"
    items = collect()
    if mode == "list":
        for tag, body in items:
            print(tag, "|", body.split("\n")[0][:110])
        print("TOTAL", len(items))
    elif mode == "emit":
        # emit <tag>：打印 base64，供下一步粘贴执行
        want = sys.argv[2]
        for tag, body in items:
            if tag == want:
                print(base64.b64encode(body.encode("utf-8")).decode("ascii"))
                break
        else:
            print("NOT FOUND", want)
            sys.exit(1)
