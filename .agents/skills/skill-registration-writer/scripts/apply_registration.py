#!/usr/bin/env python3
"""Skill 四处登记面写入器（默认 dry-run，``--write`` 才落盘）。

复用 ``.agents/scripts/check-skill-registration.py`` 的只读判定结果作为唯一事实
来源，只把「该改什么」落成受边界约束的定点写入：

1. 分类表行：在指定分类首表末尾插入一行，并把该分类标题的 ``（N个）`` 改成扫描值
2. CHANGELOG：按 ``--note`` 在最新条目之前插入 ``- **vX.Y** (日期): 说明``
3. TOML 镜像：仅当缺失时新建 ``.meta/toml/.agents/skills/<name>/SKILL.toml``

写入边界：每份文件只允许两类改动 —— 标题行内的计数 token、指定位置的整行插入。
落盘前用 ``difflib`` opcode 断言「改动全部落在允许区间」，越界即中止；写前重算
sha256，与计划时不一致即中止；先备份到 ``.temp/skill-registration-writer/`` 再原地
替换，``--revert`` 可整轮回滚。

退出码：0 无待办或写入成功 / 1 有待办（dry-run 检出）/ 2 被阻塞 / 3 参数或环境错误
"""

import argparse
import datetime
import difflib
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import time

EXIT_OK = 0
EXIT_PENDING = 1
EXIT_BLOCKED = 2
EXIT_USAGE = 3

CHECKER_REL = ".agents/scripts/check-skill-registration.py"
AUDIT_JS_REL = ".agents/skills/skill-registry-count-drift-audit/scripts/audit_surface_counts.js"
JOURNAL_DIR_REL = ".temp/skill-registration-writer"
BOM = b"\xef\xbb\xbf"

HEADING_RE = re.compile(r"^(#{3,4})\s+(.+?)\s*[（(](\d+)\s*个[^）)]*[）)]\s*$")
COUNT_TOKEN_RE = re.compile(r"[（(](\d+)\s*个")
SEPARATOR_RE = re.compile(r"^\s*\|(?:\s*:?-{2,}:?\s*\|)+\s*$")
QUOTED_RE = re.compile(
    r"「([^」\n]{1,40})」|“([^”\n]{1,40})”|‘([^’\n]{1,40})’|\"([^\"\n]{1,40})\"|'([^'\n]{1,40})'"
)
CHANGELOG_ENTRY_RE = re.compile(r"^- \*\*v([0-9]+(?:\.[0-9]+)*)\*\*")

TYPE_LABELS = {
    "完整Skill": "完整Skill",
    "命令集门面": "命令门面",
    "工作流门面": "工作流门面",
    "脚本命令门面": "脚本命令门面",
    "Trae 内置工作流 Skill": "Trae 内置工作流",
}

SURFACES = ("readme", "registry", "changelog")


class UsageError(Exception):
    """参数、环境或写入前置条件错误。"""


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def read_raw(path):
    with open(path, "rb") as handle:
        return handle.read()


def decode(raw):
    bom = raw.startswith(BOM)
    text = raw[3:].decode("utf-8", errors="replace") if bom else raw.decode("utf-8", errors="replace")
    return text, bom


def encode(text, bom):
    data = text.encode("utf-8")
    return BOM + data if bom else data


def write_bytes(path, data):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    with open(path, "wb") as handle:
        handle.write(data)


def load_checker(repo_root):
    path = os.path.join(repo_root, CHECKER_REL)
    if not os.path.isfile(path):
        raise UsageError("缺少只读判定器: %s" % path)
    spec = importlib.util.spec_from_file_location("check_skill_registration", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_sections(lines):
    """解析带 ``（N个）`` 的 3–4 级标题及其首表插入点。"""
    headings = []
    fence = None
    for index, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is not None:
            continue
        match = HEADING_RE.match(line.rstrip("\r\n"))
        if not match:
            continue
        count = COUNT_TOKEN_RE.search(line)
        headings.append(
            {
                "level": len(match.group(1)),
                "title": match.group(2).strip(),
                "line": index,
                "declared": int(match.group(3)),
                "count_span": count.span(1) if count else None,
            }
        )

    sections = {}
    for position, item in enumerate(headings):
        end = len(lines)
        for later in headings[position + 1 :]:
            if later["level"] <= item["level"]:
                end = later["line"]
                break
        insert_at, columns = find_first_table(lines, item["line"] + 1, end)
        sections[item["title"]] = {
            "level": item["level"],
            "line": item["line"],
            "declared": item["declared"],
            "count_span": item["count_span"],
            "insert_at": insert_at,
            "columns": columns,
            "end": end,
        }
    return sections


def find_first_table(lines, start, end):
    """返回首表最后一行之后的行号与列数；无表返回 (None, 0)。"""
    index = start
    while index < end - 1:
        if lines[index].lstrip().startswith("|") and SEPARATOR_RE.match(lines[index + 1].rstrip("\r\n")):
            columns = lines[index].count("|") - 1
            row = index + 2
            while row < end and lines[row].lstrip().startswith("|"):
                row += 1
            return row, columns
        index += 1
    return None, 0


class Surface:
    def __init__(self, key, path):
        self.key = key
        self.path = path
        self.raw = b""
        self.bom = False
        self.lines = []
        self.sha = ""
        self.newline = "\n"
        self.sections = {}

    def load(self):
        self.raw = read_raw(self.path)
        self.sha = sha256_bytes(self.raw)
        text, self.bom = decode(self.raw)
        self.lines = text.splitlines(keepends=True)
        self.newline = "\r\n" if "\r\n" in text else "\n"
        self.sections = parse_sections(self.lines)
        return self


def parse_frontmatter_fields(text):
    """解析 frontmatter，支持 ``>`` / ``|`` 块标量（多行 description 常态）。

    判定器的行级解析只取 ``description: >-`` 这一行，拿不到正文；登记面摘要与
    触发词都依赖 description，因此写入器自带一个块标量感知的解析。
    """
    match = re.match(r"\A---\r?\n(.*?)\r?\n---", text, re.S)
    if not match:
        return {}
    fields = {}
    lines = match.group(1).splitlines()
    index = 0
    while index < len(lines):
        pair = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", lines[index])
        if not pair:
            index += 1
            continue
        key, value = pair.group(1), pair.group(2).strip()
        if value in (">", ">-", ">+", "|", "|-", "|+"):
            block = []
            index += 1
            while index < len(lines) and (not lines[index].strip() or lines[index].startswith((" ", "\t"))):
                block.append(lines[index].strip())
                index += 1
            fields[key] = " ".join(part for part in block if part)
            continue
        fields[key] = value.strip("\"'")
        index += 1
    return fields


def load_skill_meta(checker, skills_root, name):
    path = os.path.join(skills_root, name, "SKILL.md")
    if not os.path.isfile(path):
        raise UsageError("技能目录不存在或缺少 SKILL.md: %s" % path)
    text, _ = decode(read_raw(path))
    fields = parse_frontmatter_fields(text)
    heading = ""
    for line in text.splitlines():
        if line.startswith("# "):
            heading = line[2:].strip()
            break
    return {
        "name": name,
        "version": fields.get("version", "").strip().lstrip("v"),
        "description": fields.get("description", "").strip(),
        "title": heading or fields.get("name", name),
    }


def summarize(description, limit=110):
    text = description.split("。")[0].strip() or description.strip()
    text = re.sub(r"\s+", " ", text)
    if len(text) <= limit:
        return text
    window = text[:limit]
    cut = max(window.rfind("；"), window.rfind("，"), window.rfind("："))
    if cut >= limit // 2:
        return window[:cut] + "…"
    return window[: limit - 1] + "…"


def extract_triggers(description, limit=6):
    found = []
    for match in QUOTED_RE.finditer(description):
        value = next((item for item in match.groups() if item), "").strip()
        if not value or value in found:
            continue
        found.append(value)
        if len(found) >= limit:
            break
    return found


def sanitize_cell(value):
    return re.sub(r"\s+", " ", value).replace("|", "\\|")


def readme_row(meta, category):
    label = TYPE_LABELS.get(category, category)
    type_cell = "%s（v%s）" % (label, meta["version"]) if meta["version"] else label
    cells = [
        meta["name"],
        type_cell,
        summarize(meta["description"]),
        "、".join(extract_triggers(meta["description"])) or meta["name"],
        "[%s/SKILL.md](%s/SKILL.md)" % (meta["name"], meta["name"]),
    ]
    return "| " + " | ".join(sanitize_cell(cell) for cell in cells) + " |"


def registry_row(meta):
    triggers = extract_triggers(meta["description"])
    trigger_cell = "、".join('"%s"' % item for item in triggers) if triggers else '"%s"' % meta["name"]
    cells = [
        meta["name"],
        trigger_cell,
        "1（%s）" % summarize(meta["description"], 200),
        "v%s" % meta["version"] if meta["version"] else "-",
        "[skills/%s/SKILL.md](../skills/%s/SKILL.md)" % (meta["name"], meta["name"]),
    ]
    return "| " + " | ".join(sanitize_cell(cell) for cell in cells) + " |"


def toml_content(meta, today):
    parts = meta["version"].split(".") if meta["version"] else []
    snapshot = ".".join(parts[:2]) if len(parts) >= 2 else (parts[0] if parts else "1.0")
    title = meta["title"].replace("\\", "\\\\").replace('"', '\\"')
    return (
        'id = "skill"\n'
        'title = "%s"\n'
        'category = "skills/%s"\n'
        'date = "%s"\n'
        'version = "%s"\n' % (title, meta["name"], today, snapshot)
    )


def next_version(text):
    versions = []
    for line in text.splitlines():
        match = CHANGELOG_ENTRY_RE.match(line)
        if match:
            versions.append(match.group(1))
    if not versions:
        raise UsageError("CHANGELOG 中未找到 `- **vX.Y**` 条目，无法取号")
    latest = max(versions, key=lambda value: tuple(int(part) for part in value.split(".")))
    pieces = [int(part) for part in latest.split(".")]
    pieces[-1] += 1
    return ".".join(str(piece) for piece in pieces)


def find_first_entry(lines):
    for index, line in enumerate(lines):
        if CHANGELOG_ENTRY_RE.match(line):
            return index
    return None


def changelog_has_note(lines, note):
    suffix = "): %s" % note
    for line in lines:
        if CHANGELOG_ENTRY_RE.match(line) and line.rstrip("\r\n").endswith(suffix):
            return True
    return False


def parse_assign(values):
    targets = []
    seen = {}
    for raw in values or []:
        if "=" not in raw:
            raise UsageError("--assign 需要 <name>=<category> 形式，收到: %r" % raw)
        name, category = (piece.strip() for piece in raw.split("=", 1))
        if not name or not category:
            raise UsageError("--assign 的名称与分类都不能为空: %r" % raw)
        if name in seen and seen[name] != category:
            raise UsageError("--assign 对 %s 给出了两个分类: %s / %s" % (name, seen[name], category))
        if name not in seen:
            targets.append((name, category))
            seen[name] = category
    return targets


def build_options(args, repo_root):
    return argparse.Namespace(
        repo_root=repo_root,
        skills_root=args.skills_root,
        readme=args.readme,
        registry=args.registry,
        changelog=args.changelog,
        toml_root=args.toml_root,
        assign=parse_assign(args.assign),
        note=(args.note or "").strip(),
        only=[item for item in args.only],
        write=bool(args.write),
        today=args.today or datetime.date.today().isoformat(),
    )


def build_plan(repo_root, opts):
    checker = load_checker(repo_root)
    try:
        report = checker.build_report(repo_root, opts)
    except checker.UsageError as exc:
        raise UsageError(str(exc))

    surfaces = {}
    for key in SURFACES:
        path = os.path.join(repo_root, getattr(opts, key))
        if not os.path.isfile(path):
            raise UsageError("登记面文件不存在: %s" % path)
        surfaces[key] = Surface(key, path).load()

    label_key = {}
    for key in ("readme", "registry"):
        label_key[os.path.splitext(os.path.basename(surfaces[key].path))[0]] = key

    actual_map = {}
    for surface in report["surfaces"]:
        key = label_key.get(surface["label"])
        if not key:
            continue
        for category in surface["categories"]:
            actual_map[(key, category["title"])] = category

    facts = {
        item["name"]: item
        for item in checker.scan_skills(os.path.join(repo_root, opts.skills_root))
    }
    unregistered = {item["name"] for item in report["unregistered"]}
    skills_root = os.path.join(repo_root, opts.skills_root)

    actions = []
    blocked = []
    skipped = []
    for name, category in opts.assign:
        fact = facts.get(name)
        if not fact:
            blocked.append("%s: 磁盘无该技能目录，--assign 无效" % name)
            continue
        section = surfaces["readme"].sections.get(category)
        if not section:
            blocked.append(
                "%s: README 无分类 %r（可选: %s）"
                % (name, category, "、".join(sorted(surfaces["readme"].sections)))
            )
            continue
        if section["insert_at"] is None or section["columns"] != 5:
            blocked.append("%s: 分类 %r 首表形态不可写（需 5 列且有表体）" % (name, category))
            continue

        meta = load_skill_meta(checker, skills_root, name)

        if name not in unregistered:
            skipped.append("%s: 表行已存在，跳过插入" % name)
        else:
            actions.append(
                {
                    "surface": "readme",
                    "kind": "insert_row",
                    "title": category,
                    "line": section["insert_at"],
                    "row": readme_row(meta, category),
                    "skill": name,
                }
            )
            registry_section = surfaces["registry"].sections.get(category)
            if registry_section and registry_section["insert_at"] is not None and registry_section["columns"] == 5:
                actions.append(
                    {
                        "surface": "registry",
                        "kind": "insert_row",
                        "title": category,
                        "line": registry_section["insert_at"],
                        "row": registry_row(meta),
                        "skill": name,
                    }
                )
            else:
                skipped.append("%s: registry 无分类 %r，仅写 README" % (name, category))

        toml_path = os.path.join(repo_root, opts.toml_root, name, "SKILL.toml")
        if not os.path.isfile(toml_path):
            actions.append(
                {
                    "surface": "toml",
                    "kind": "create_toml",
                    "path": toml_path,
                    "content": toml_content(meta, opts.today),
                    "skill": name,
                }
            )

    allowed = set(opts.only)
    actions = [action for action in actions if action["surface"] in allowed]

    inserted = {}
    for action in actions:
        if action["kind"] == "insert_row":
            key = (action["surface"], action["title"])
            inserted[key] = inserted.get(key, 0) + 1

    touched = set(inserted)
    for _, category in opts.assign:
        for key in ("readme", "registry"):
            if category in surfaces[key].sections and key in allowed:
                touched.add((key, category))

    for key, title in sorted(touched):
        section = surfaces[key].sections.get(title)
        if not section:
            continue
        info = actual_map.get((key, title))
        actual = info["actual"] if info else section["declared"]
        target = actual + inserted.get((key, title), 0)
        if section["declared"] == target or not section["count_span"]:
            continue
        actions.append(
            {
                "surface": key,
                "kind": "fix_count",
                "title": title,
                "line": section["line"],
                "span": section["count_span"],
                "old": section["declared"],
                "new": target,
            }
        )

    unassigned = sorted(
        name
        for name in unregistered
        if name not in {item[0] for item in opts.assign} and not facts[name]["mirror"]
    )

    if "changelog" in allowed:
        if opts.note and changelog_has_note(surfaces["changelog"].lines, opts.note):
            skipped.append("CHANGELOG 已存在同说明条目，跳过取号")
        elif opts.note:
            anchor = find_first_entry(surfaces["changelog"].lines)
            if anchor is None:
                blocked.append("CHANGELOG 未找到 `- **vX.Y**` 条目锚点，无法插入新条目")
            else:
                version = next_version("".join(surfaces["changelog"].lines))
                actions.append(
                    {
                        "surface": "changelog",
                        "kind": "prepend_changelog",
                        "line": anchor,
                        "row": "- **v%s** (%s): %s" % (version, opts.today, opts.note),
                        "version": version,
                    }
                )
        elif any(action["kind"] in ("insert_row", "create_toml") for action in actions):
            blocked.append("缺少 --note：已计划表行或镜像变更，不能留下无 CHANGELOG 条目的登记")

    return {
        "actions": actions,
        "blocked": blocked,
        "skipped": skipped,
        "unassigned": unassigned,
        "surfaces": surfaces,
        "report": report,
    }


def materialize(surface, actions):
    lines = list(surface.lines)
    replacements = [item for item in actions if item["kind"] == "fix_count"]
    insertions = [item for item in actions if item["kind"] in ("insert_row", "prepend_changelog")]

    allowed_replace = set()
    for item in replacements:
        index = item["line"]
        start, end = item["span"]
        line = lines[index]
        lines[index] = line[:start] + str(item["new"]) + line[end:]
        allowed_replace.add(index)

    by_line = {}
    for item in insertions:
        by_line.setdefault(item["line"], []).append(item)

    allowed_insert = set(by_line)
    new = list(lines)
    for index in sorted(by_line, reverse=True):
        rows = []
        for item in by_line[index]:
            row = item["row"]
            if not row.endswith(("\n", "\r")):
                row += surface.newline
            rows.append(row)
        new[index:index] = rows

    assert_confined(lines, new, allowed_insert, allowed_replace)
    expected = len(lines) + len(insertions)
    if len(new) != expected:
        raise UsageError("%s: 行数异常 %d != %d" % (surface.path, len(new), expected))
    return new


def assert_confined(old_lines, new_lines, allowed_insert, allowed_replace):
    matcher = difflib.SequenceMatcher(a=old_lines, b=new_lines, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag == "insert" and i1 == i2 and i1 in allowed_insert:
            continue
        if tag == "replace" and (i2 - i1) == 1 and i1 in allowed_replace:
            continue
        raise UsageError(
            "写入越界，已中止: %s old[%d:%d] new[%d:%d]" % (tag, i1, i2, j1, j2)
        )


def render_plan(plan, opts):
    out = ["Skill 四处登记面写入计划（%s）" % ("write" if opts.write else "dry-run")]
    rows = [item for item in plan["actions"] if item["kind"] == "insert_row"]
    fixes = [item for item in plan["actions"] if item["kind"] == "fix_count"]
    creates = [item for item in plan["actions"] if item["kind"] == "create_toml"]
    entries = [item for item in plan["actions"] if item["kind"] == "prepend_changelog"]

    out.append("\n[1] 表行插入 %d 条" % len(rows))
    for item in rows:
        out.append("  %s / %s  +1 行: %s" % (item["surface"], item["title"], item["skill"]))

    out.append("\n[2] 分类计数 %d 处" % len(fixes))
    for item in fixes:
        out.append("  %s / %s  %d → %d" % (item["surface"], item["title"], item["old"], item["new"]))

    out.append("\n[3] CHANGELOG %d 条" % len(entries))
    for item in entries:
        out.append("  v%s: %s" % (item["version"], opts.note))

    out.append("\n[4] TOML 镜像新建 %d 个" % len(creates))
    for item in creates:
        out.append("  %s" % os.path.relpath(item["path"], opts.repo_root))

    if plan["skipped"]:
        out.append("\n[5] 跳过")
        for item in plan["skipped"]:
            out.append("  %s" % item)
    if plan["unassigned"]:
        out.append("\n[6] 待指定分类（漏登记，需 --assign <name>=<分类>）")
        for name in plan["unassigned"]:
            out.append("  %s" % name)
    if plan["blocked"]:
        out.append("\n[7] 阻塞（--write 会拒绝执行）")
        for item in plan["blocked"]:
            out.append("  %s" % item)

    out.append(
        "\n结论: %d 项待写入, %d 项跳过, %d 项待指定分类, %d 项阻塞；%s"
        % (
            len(plan["actions"]),
            len(plan["skipped"]),
            len(plan["unassigned"]),
            len(plan["blocked"]),
            "已写入" if opts.write else "本次未修改任何文件",
        )
    )
    return "\n".join(out)


def apply_plan(repo_root, plan, opts):
    grouped = {}
    for action in plan["actions"]:
        grouped.setdefault(action["surface"], []).append(action)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    journal_dir = os.path.join(repo_root, JOURNAL_DIR_REL)
    backup_dir = os.path.join(journal_dir, "backup", stamp)
    entries = []

    for key in SURFACES:
        items = grouped.get(key, [])
        if not items:
            continue
        surface = plan["surfaces"][key]
        current = read_raw(surface.path)
        if sha256_bytes(current) != surface.sha:
            raise UsageError("写前哈希不一致，已中止（文件被并发修改）: %s" % surface.path)
        new_bytes = encode("".join(materialize(surface, items)), surface.bom)
        if new_bytes == current:
            continue
        if not os.path.isdir(backup_dir):
            os.makedirs(backup_dir)
        backup = os.path.join(backup_dir, os.path.basename(surface.path))
        write_bytes(backup, current)
        write_bytes(surface.path, new_bytes)
        entries.append(
            {
                "path": surface.path,
                "action": "modify",
                "backup": backup,
                "before_sha256": sha256_bytes(current),
                "after_sha256": sha256_bytes(new_bytes),
            }
        )

    for action in grouped.get("toml", []):
        path = action["path"]
        if os.path.isfile(path):
            continue
        data = action["content"].encode("utf-8")
        write_bytes(path, data)
        entries.append(
            {
                "path": path,
                "action": "create",
                "backup": None,
                "before_sha256": None,
                "after_sha256": sha256_bytes(data),
            }
        )

    journal = {
        "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "repo_root": repo_root,
        "note": opts.note,
        "assign": ["%s=%s" % item for item in opts.assign],
        "files": entries,
    }
    if not os.path.isdir(journal_dir):
        os.makedirs(journal_dir)
    journal_path = os.path.join(journal_dir, "journal-%s.json" % stamp)
    write_bytes(journal_path, json.dumps(journal, ensure_ascii=False, indent=2).encode("utf-8"))
    return entries, journal_path


def latest_journal(repo_root):
    journal_dir = os.path.join(repo_root, JOURNAL_DIR_REL)
    if not os.path.isdir(journal_dir):
        raise UsageError("无回滚记录目录: %s" % journal_dir)
    candidates = sorted(
        name
        for name in os.listdir(journal_dir)
        if name.startswith("journal-") and name.endswith(".json")
    )
    if not candidates:
        raise UsageError("无可用回滚记录: %s" % journal_dir)
    return os.path.join(journal_dir, candidates[-1])


def revert(repo_root, target):
    path = latest_journal(repo_root) if target in (None, "", "__latest__") else target
    if not os.path.isfile(path):
        raise UsageError("回滚记录不存在: %s" % path)
    data = json.loads(read_raw(path).decode("utf-8"))
    lines = ["Skill 登记面写入回滚（journal: %s）" % os.path.relpath(path, repo_root)]
    failures = []
    for entry in reversed(data.get("files", [])):
        if entry["action"] == "modify":
            backup = entry.get("backup")
            if not backup or not os.path.isfile(backup):
                failures.append("%s: 备份缺失" % entry["path"])
                continue
            write_bytes(entry["path"], read_raw(backup))
            ok = sha256_bytes(read_raw(entry["path"])) == entry.get("before_sha256")
            lines.append(("  OK   " if ok else "  FAIL ") + os.path.relpath(entry["path"], repo_root))
            if not ok:
                failures.append("%s: 回滚后哈希不符" % entry["path"])
        else:
            if os.path.isfile(entry["path"]):
                os.remove(entry["path"])
                lines.append("  删除 %s" % os.path.relpath(entry["path"], repo_root))
            else:
                lines.append("  已不存在 %s" % os.path.relpath(entry["path"], repo_root))
    lines.append("\n结论: %s" % ("全部回滚成功" if not failures else "存在 %d 项失败" % len(failures)))
    for item in failures:
        lines.append("  %s" % item)
    sys.stdout.write("\n".join(lines) + "\n")
    return EXIT_OK if not failures else EXIT_BLOCKED


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Skill 四处登记面写入器（默认 dry-run）",
        epilog="退出码: 0 无待办/写入成功 / 1 有待办 / 2 被阻塞 / 3 参数或环境错误",
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--skills-root", default=".agents/skills")
    parser.add_argument("--readme", default=".agents/skills/README.md")
    parser.add_argument("--registry", default=".agents/capability-registry/02-skills.md")
    parser.add_argument("--changelog", default=".agents/skills/CHANGELOG.md")
    parser.add_argument("--toml-root", default=".meta/toml/.agents/skills")
    parser.add_argument(
        "--assign",
        action="append",
        default=[],
        metavar="NAME=CATEGORY",
        help="为漏登记技能显式指定分类；可重复",
    )
    parser.add_argument("--note", default="", help="CHANGELOG 新条目的说明正文")
    parser.add_argument(
        "--only",
        action="append",
        choices=list(SURFACES + ("toml",)),
        default=[],
        help="限定作用面；可重复，缺省为四处全开",
    )
    parser.add_argument("--today", default="", help="覆盖条目日期（YYYY-MM-DD），仅用于复现")
    parser.add_argument("--write", action="store_true", help="真正落盘（缺省 dry-run）")
    parser.add_argument("--revert", nargs="?", const="__latest__", default=None, help="按回滚记录撤销")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    parser.add_argument("--self-test", action="store_true", help="运行内置夹具")
    return parser.parse_args(argv)


def collect_only(values):
    picked = []
    for value in values:
        if value not in picked:
            picked.append(value)
    return picked or list(SURFACES + ("toml",))


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    args = parse_args(argv)
    if args.self_test:
        return self_test()
    args.only = collect_only(args.only)
    repo_root = os.path.abspath(args.repo_root)

    try:
        if args.revert is not None:
            return revert(repo_root, args.revert)
        opts = build_options(args, repo_root)
        plan = build_plan(repo_root, opts)
    except UsageError as exc:
        sys.stderr.write("错误: %s\n" % exc)
        return EXIT_USAGE

    if args.json:
        payload = {
            "actions": [
                {key: value for key, value in item.items() if key not in ("content",)}
                for item in plan["actions"]
            ],
            "blocked": plan["blocked"],
            "skipped": plan["skipped"],
            "unassigned": plan["unassigned"],
            "wrote": False,
            "modified_files": [],
        }
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(render_plan(plan, opts) + "\n")

    if not opts.write:
        if plan["blocked"]:
            return EXIT_BLOCKED
        return EXIT_PENDING if plan["actions"] else EXIT_OK

    if plan["blocked"]:
        sys.stderr.write("拒绝写入：存在未解决阻塞，先处理再执行 --write\n")
        return EXIT_BLOCKED
    if not plan["actions"]:
        sys.stdout.write("已对齐，无需写入\n")
        return EXIT_OK

    try:
        entries, journal_path = apply_plan(repo_root, plan, opts)
    except UsageError as exc:
        sys.stderr.write("错误: %s\n" % exc)
        return EXIT_BLOCKED

    sys.stdout.write("\n已写入:\n")
    for entry in entries:
        sys.stdout.write("  %s %s\n" % (entry["action"], os.path.relpath(entry["path"], repo_root)))
    sys.stdout.write("回滚记录: %s\n" % os.path.relpath(journal_path, repo_root))

    remaining = build_plan(repo_root, opts)
    if remaining["actions"] or remaining["blocked"]:
        sys.stdout.write(
            "复跑核对: 仍有 %d 项待办 / %d 项阻塞（幂等未达成）\n"
            % (len(remaining["actions"]), len(remaining["blocked"]))
        )
        return EXIT_BLOCKED
    sys.stdout.write("复跑核对: 零待办（幂等）\n")
    return EXIT_OK


# ---------------------------------------------------------------- 自检夹具


def locate_repo_root():
    current = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.isdir(os.path.join(current, ".agents")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            raise UsageError("无法定位仓库根（自检需要真实判定器与审计脚本）")
        current = parent


FIXTURE_README = """---
id: "fixture-readme"
---
# Skill 列表

### 完整Skill（1个）

| Skill名称 | 类型 | 功能描述 | 核心触发词 | SKILL.md路径 |
|-----------|------|---------|-----------|-------------|
| alpha | 完整Skill | 甲技能。 | "甲"、"乙" | [alpha/SKILL.md](alpha/SKILL.md) |
"""

FIXTURE_REGISTRY = """---
id: "fixture-registry"
---
# Skill索引


### 完整Skill（1个）

| Skill名 | 触发词 | 方案数 | 版本 | 路径 |
|---------|--------|-------|------|------|
| alpha | "甲"、"乙" | 1（甲技能） | v1.0.0 | [skills/alpha/SKILL.md](../skills/alpha/SKILL.md) |
"""

FIXTURE_CHANGELOG = """---
id: "fixture-changelog"
date: "2026-01-01"
---
# Changelog
- **v1.0** (2026-01-01): 新增完整 Skill alpha。
"""

FIXTURE_SKILL = """---
name: %s
version: 1.0.0
description: "%s，用于写入夹具。当用户提到「%s」「写入验证」时必须使用此技能。"
---
# %s

正文。
"""


def build_fixture(root, checker_path, audit_path):
    os.makedirs(os.path.join(root, ".agents", "scripts"))
    shutil.copy2(checker_path, os.path.join(root, ".agents", "scripts", "check-skill-registration.py"))
    audit_dir = os.path.join(root, ".agents", "skills", "skill-registry-count-drift-audit", "scripts")
    os.makedirs(audit_dir)
    shutil.copy2(audit_path, os.path.join(audit_dir, "audit_surface_counts.js"))

    os.makedirs(os.path.join(root, ".agents", "skills", "alpha"))
    os.makedirs(os.path.join(root, ".agents", "skills", "beta"))
    os.makedirs(os.path.join(root, ".meta", "toml", ".agents", "skills", "alpha"))
    os.makedirs(os.path.join(root, ".agents", "capability-registry"))

    write_bytes(os.path.join(root, ".agents", "skills", "README.md"), FIXTURE_README.encode("utf-8"))
    write_bytes(
        os.path.join(root, ".agents", "capability-registry", "02-skills.md"),
        FIXTURE_REGISTRY.encode("utf-8"),
    )
    write_bytes(
        os.path.join(root, ".agents", "skills", "CHANGELOG.md"), FIXTURE_CHANGELOG.encode("utf-8")
    )
    write_bytes(
        os.path.join(root, ".agents", "skills", "alpha", "SKILL.md"),
        (FIXTURE_SKILL % ("alpha", "甲技能", "甲", "甲技能")).encode("utf-8"),
    )
    write_bytes(
        os.path.join(root, ".agents", "skills", "beta", "SKILL.md"),
        (FIXTURE_SKILL % ("beta", "乙技能", "乙", "乙技能")).encode("utf-8"),
    )
    write_bytes(
        os.path.join(root, ".meta", "toml", ".agents", "skills", "alpha", "SKILL.toml"),
        b'id = "skill"\ntitle = "alpha"\ncategory = "skills/alpha"\ndate = "2026-01-01"\nversion = "1.0"\n',
    )


def fixture_options(root, assign, note, write=False):
    return build_options(
        argparse.Namespace(
            skills_root=".agents/skills",
            readme=".agents/skills/README.md",
            registry=".agents/capability-registry/02-skills.md",
            changelog=".agents/skills/CHANGELOG.md",
            toml_root=".meta/toml/.agents/skills",
            assign=assign,
            note=note,
            only=collect_only([]),
            write=write,
            today="2026-11-09",
        ),
        root,
    )


def self_test():
    try:
        repo = locate_repo_root()
        checker_path = os.path.join(repo, CHECKER_REL)
        audit_path = os.path.join(repo, AUDIT_JS_REL)
        if not os.path.isfile(checker_path) or not os.path.isfile(audit_path):
            sys.stdout.write("自检跳过: 缺少判定器或审计脚本\n")
            return None
        if not shutil.which("node"):
            sys.stdout.write("自检跳过: 未找到 node\n")
            return None
    except UsageError as exc:
        sys.stdout.write("自检跳过: %s\n" % exc)
        return None

    root = tempfile.mkdtemp(prefix="skill-registration-writer-")
    checks = []
    try:
        build_fixture(root, checker_path, audit_path)
        paths = {
            "readme": os.path.join(root, ".agents", "skills", "README.md"),
            "registry": os.path.join(root, ".agents", "capability-registry", "02-skills.md"),
            "changelog": os.path.join(root, ".agents", "skills", "CHANGELOG.md"),
        }
        baseline = {key: read_raw(path) for key, path in paths.items()}

        # 1) 未给 --assign：漏登记必须显式列出，且不得静默插入
        plan = build_plan(root, fixture_options(root, [], ""))
        checks.append(
            (
                "缺 --assign 时不静默插入",
                not plan["actions"] and plan["unassigned"] == ["beta"],
            )
        )

        # 2) dry-run 计划：四类动作齐备且不改盘
        plan = build_plan(root, fixture_options(root, ["beta=完整Skill"], "新增完整 Skill beta。"))
        kinds = sorted({item["kind"] for item in plan["actions"]})
        checks.append(
            (
                "dry-run 计划含四类动作",
                kinds
                == ["create_toml", "fix_count", "insert_row", "prepend_changelog"]
                and len([item for item in plan["actions"] if item["kind"] == "insert_row"]) == 2,
            )
        )
        checks.append(
            ("dry-run 未改盘", all(read_raw(paths[key]) == baseline[key] for key in paths))
        )

        # 3) 写入并核对结果
        opts = fixture_options(root, ["beta=完整Skill"], "新增完整 Skill beta。", write=True)
        entries, journal_path = apply_plan(root, plan, opts)
        readme_text = read_raw(paths["readme"]).decode("utf-8")
        registry_text = read_raw(paths["registry"]).decode("utf-8")
        changelog_text = read_raw(paths["changelog"]).decode("utf-8")
        checks.append(("README 插入行与计数", "| beta |" in readme_text and "（2个）" in readme_text))
        checks.append(
            (
                "registry 插入行与计数",
                "| beta |" in registry_text and "（2个）" in registry_text,
            )
        )
        checks.append(
            (
                "TOML 镜像生成",
                os.path.isfile(os.path.join(root, ".meta", "toml", ".agents", "skills", "beta", "SKILL.toml"))
                and 'category = "skills/beta"' in read_raw(
                    os.path.join(root, ".meta", "toml", ".agents", "skills", "beta", "SKILL.toml")
                ).decode("utf-8"),
            )
        )
        checks.append(
            (
                "CHANGELOG 取号并按新→旧插入",
                changelog_text.index("- **v1.1**") < changelog_text.index("- **v1.0**"),
            )
        )

        # 4) 幂等：同参数复跑零动作
        again = build_plan(root, fixture_options(root, ["beta=完整Skill"], "新增完整 Skill beta。"))
        checks.append(("复跑零动作", not again["actions"] and not again["blocked"]))

        # 5) 回滚：三个登记面逐字节还原，镜像被删除
        code = revert(root, journal_path)
        checks.append(
            (
                "回滚后逐字节还原",
                code == EXIT_OK
                and all(read_raw(paths[key]) == baseline[key] for key in paths)
                and not os.path.isfile(
                    os.path.join(root, ".meta", "toml", ".agents", "skills", "beta", "SKILL.toml")
                ),
            )
        )

        # 6) 纯计数漂移：只改标题数字，不动表体
        tampered = baseline["readme"].decode("utf-8").replace("完整Skill（1个）", "完整Skill（2个）")
        write_bytes(paths["readme"], tampered.encode("utf-8"))
        plan = build_plan(root, fixture_options(root, ["alpha=完整Skill"], "占位说明。"))
        fixes = [item for item in plan["actions"] if item["kind"] == "fix_count"]
        checks.append(
            (
                "已登记技能的计数漂移可修正",
                len(fixes) == 1 and fixes[0]["old"] == 2 and fixes[0]["new"] == 1,
            )
        )
        opts = fixture_options(root, ["alpha=完整Skill"], "占位说明。", write=True)
        apply_plan(root, plan, opts)
        checks.append(
            (
                "计数漂移修正落盘",
                "（1个）" in read_raw(paths["readme"]).decode("utf-8"),
            )
        )
    except UsageError as exc:
        checks.append(("执行未抛异常", False))
        sys.stdout.write("自检异常: %s\n" % exc)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    failed = 0
    for name, ok in checks:
        sys.stdout.write("  [%s] %s\n" % ("PASS" if ok else "FAIL", name))
        if not ok:
            failed += 1
    sys.stdout.write("\n自检: %d 项, 失败 %d 项\n" % (len(checks), failed))
    return EXIT_OK if failed == 0 else EXIT_BLOCKED


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
