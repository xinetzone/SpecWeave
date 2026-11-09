#!/usr/bin/env python3
"""Skill 四处登记面只读判定器（dry-run）。

以磁盘实际目录为准，核对四个登记面：

1. ``.agents/skills/README.md``            分类表行与 ``（N个）`` 计数
2. ``.agents/capability-registry/02-skills.md`` 同构分类表
3. ``.agents/skills/CHANGELOG.md``         版本条目对技能名的覆盖
4. ``.meta/toml/.agents/skills/<name>/SKILL.toml`` 镜像存在性与字段

判定分为互不混算的五类：

- ``count-drift``   表头声明数与扫描到的数据行数不等
- ``cross-surface`` 同名分类在两份登记面之间的名称集合差
- ``unregistered``  磁盘存在但任一登记面完全缺行（需人工判类）
- ``toml-mirror``   镜像缺失或字段与 SKILL.md 不一致
- ``changelog``     CHANGELOG 缺少该技能的版本条目记录

本脚本只读，不写任何文件。退出码：0 零漂移 / 1 仅漏登记 / 2 含计数或镜像漂移 / 3 参数或环境错误。
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

EXIT_OK = 0
EXIT_UNREGISTERED = 1
EXIT_DRIFT = 2
EXIT_USAGE = 3

AUDIT_SCRIPT_REL = ".agents/skills/skill-registry-count-drift-audit/scripts/audit_surface_counts.js"
FRONT_MATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\s*(?:\r?\n|\Z)", re.S)
CHANGELOG_ENTRY = re.compile(r"^-\s+\*\*v([0-9]+(?:\.[0-9]+)*)\*\*", re.M)


class UsageError(Exception):
    """参数或环境错误。"""


def read_text(path):
    with open(path, encoding="utf-8-sig", errors="replace") as handle:
        return handle.read()


def parse_frontmatter(text):
    match = FRONT_MATTER.match(text)
    if not match:
        return {}
    fields = {}
    for line in match.group(1).splitlines():
        pair = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if not pair:
            continue
        fields[pair.group(1)] = pair.group(2).strip().strip("\"'")
    return fields


def scan_skills(skills_root):
    """扫描磁盘事实集。只认含 SKILL.md 的目录。"""
    if not os.path.isdir(skills_root):
        raise UsageError("技能根目录不存在: %s" % skills_root)
    facts = []
    for name in sorted(os.listdir(skills_root)):
        skill_dir = os.path.join(skills_root, name)
        skill_md = os.path.join(skill_dir, "SKILL.md")
        if not os.path.isdir(skill_dir) or not os.path.isfile(skill_md):
            continue
        fields = parse_frontmatter(read_text(skill_md))
        facts.append(
            {
                "name": name,
                "version": fields.get("version", ""),
                "mirror": bool(fields.get("source")),
                "title": fields.get("name", ""),
                "toml_ref": fields.get("x-toml-ref", ""),
            }
        )
    return facts


def run_surface_audit(repo_root, readme, registry, skills_root):
    """复用既有计数审计器（单一解析真源），避免重复实现表格解析。"""
    script = os.path.join(repo_root, AUDIT_SCRIPT_REL)
    if not os.path.isfile(script):
        raise UsageError("缺少计数审计脚本: %s" % script)
    node = shutil.which("node")
    if not node:
        raise UsageError("未找到 node，无法复用 %s" % AUDIT_SCRIPT_REL)
    result = subprocess.run(
        [
            node,
            script,
            "--readme",
            readme,
            "--registry",
            registry,
            "--skills-root",
            skills_root,
            "--json",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode not in (0, 1, 2):
        raise UsageError("计数审计脚本失败(%d): %s" % (result.returncode, result.stderr.strip()))
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise UsageError("计数审计脚本输出非 JSON: %s" % exc)


def registered_names(surfaces):
    names = set()
    for surface in surfaces:
        for category in surface.get("categories", []):
            names.update(category.get("names", []))
    return names


def collect_count_drift(surfaces):
    findings = []
    for surface in surfaces:
        for category in surface.get("categories", []):
            if category["declared"] == category["actual"]:
                continue
            findings.append(
                {
                    "surface": surface["label"],
                    "category": category["title"],
                    "declared": category["declared"],
                    "actual": category["actual"],
                    "delta": category["actual"] - category["declared"],
                    "tables": category["tableCount"],
                    "tables_and_rows": [category["firstTable"]],
                }
            )
    return findings


def collect_cross_surface(gaps):
    findings = []
    for gap in gaps:
        findings.append(
            {
                "category": gap["title"],
                "left": gap["left"]["label"],
                "right": gap["right"]["label"],
                "only_left": [item["name"] for item in gap["left"]["only"]],
                "only_right": [item["name"] for item in gap["right"]["only"]],
                "left_counts": "%d/%d" % (gap["left"]["declared"], gap["left"]["actual"]),
                "right_counts": "%d/%d" % (gap["right"]["declared"], gap["right"]["actual"]),
            }
        )
    return findings


def collect_unregistered(facts, surfaces):
    """磁盘有、两份登记面都没有技能的整行。"""
    known = registered_names(surfaces)
    missing = [item for item in facts if item["name"] not in known]
    return [
        {
            "name": item["name"],
            "kind": "mirror" if item["mirror"] else "native",
            "version": item["version"],
        }
        for item in missing
    ]


def collect_surface_coverage(surfaces):
    """登记面覆盖范围差：某面完全没有、另一面有的分类（非缺行，属口径差异）。"""
    by_title = {}
    for surface in surfaces:
        for category in surface.get("categories", []):
            by_title.setdefault(category["title"], {})[surface["label"]] = category["actual"]
    findings = []
    for title, counts in by_title.items():
        if len(counts) < 2:
            findings.append(
                {
                    "category": title,
                    "present_in": sorted(counts),
                    "missing_in": sorted(
                        surface["label"] for surface in surfaces if surface["label"] not in counts
                    ),
                    "rows": sum(counts.values()),
                }
            )
    return findings


def collect_toml_findings(facts, toml_root, registered, skills_root):
    """镜像缺失按原生/镜像轨分列；字段只校验可机械判定的项。

    版本号不参与判定：镜像 ``version`` 按仓内惯例固定为入库时的两段式快照，
    与 SKILL.md 不同步属于设计约定而非漂移。
    """
    missing_native = []
    missing_mirror_track = []
    orphan_mirror = []
    drift = []
    for item in facts:
        toml_path = os.path.join(toml_root, item["name"], "SKILL.toml")
        if not os.path.isfile(toml_path):
            if item["name"] not in registered:
                continue
            if item["mirror"]:
                missing_mirror_track.append(item["name"])
            else:
                missing_native.append(item["name"])
            continue
        if item["name"] not in registered:
            orphan_mirror.append(item["name"])
        text = read_text(toml_path)
        fields = {}
        for line in text.splitlines():
            pair = re.match(r"^([A-Za-z0-9_-]+)\s*=\s*\"(.*)\"\s*$", line)
            if pair:
                fields[pair.group(1)] = pair.group(2)

        problems = []
        expected_category = "skills/%s" % item["name"]
        if fields.get("category") != expected_category:
            problems.append("category=%r 应为 %r" % (fields.get("category"), expected_category))
        if not fields.get("title"):
            problems.append("title 为空")
        if item.get("toml_ref"):
            expected_ref = os.path.normpath(toml_path)
            actual_ref = os.path.normpath(
                os.path.join(skills_root, item["name"], item["toml_ref"])
            )
            if expected_ref != actual_ref:
                problems.append("x-toml-ref 解析为 %s" % actual_ref)
        if problems:
            drift.append({"name": item["name"], "problems": problems})
    return {
        "missing_native": sorted(missing_native),
        "missing_mirror_track": sorted(missing_mirror_track),
        "orphan_mirror": sorted(orphan_mirror),
        "drift": drift,
    }


def collect_changelog(facts, changelog_path, registered):
    """只核对已登记的原生技能：未登记技能缺版本记录属"漏登记"的下游后果，不重复计数。"""
    text = read_text(changelog_path)
    versions = CHANGELOG_ENTRY.findall(text)
    native_missing = [
        item["name"]
        for item in facts
        if not item["mirror"] and item["name"] in registered and item["name"] not in text
    ]
    duplicates = sorted({value for value in versions if versions.count(value) > 1})

    def key(value):
        return tuple(int(piece) for piece in value.split("."))

    unordered = False
    for current, following in zip(versions, versions[1:]):
        if key(current) <= key(following):
            unordered = True
            break
    return {
        "entries": len(versions),
        "latest": versions[0] if versions else "",
        "oldest": versions[-1] if versions else "",
        "duplicates": duplicates,
        "newest_first": not unordered,
        "native_missing": native_missing,
    }


def build_report(repo_root, args):
    readme = os.path.join(repo_root, args.readme)
    registry = os.path.join(repo_root, args.registry)
    skills_root = os.path.join(repo_root, args.skills_root)
    changelog = os.path.join(repo_root, args.changelog)
    toml_root = os.path.join(repo_root, args.toml_root)

    for path in (readme, registry, changelog):
        if not os.path.isfile(path):
            raise UsageError("登记面文件不存在: %s" % path)

    facts = scan_skills(skills_root)
    audit = run_surface_audit(repo_root, readme, registry, skills_root)
    registered = registered_names(audit.get("surfaces", []))

    return {
        "facts": {
            "skills": len(facts),
            "native": sum(1 for item in facts if not item["mirror"]),
            "mirror": sum(1 for item in facts if item["mirror"]),
            "registered": len(registered & {item["name"] for item in facts}),
        },
        "surfaces": [
            {
                "label": surface["label"],
                "categories": [
                    {
                        "title": category["title"],
                        "declared": category["declared"],
                        "actual": category["actual"],
                    }
                    for category in surface.get("categories", [])
                ],
            }
            for surface in audit.get("surfaces", [])
        ],
        "count_drift": collect_count_drift(audit.get("surfaces", [])),
        "cross_surface": collect_cross_surface(audit.get("gaps", [])),
        "surface_coverage": collect_surface_coverage(audit.get("surfaces", [])),
        "unregistered": collect_unregistered(facts, audit.get("surfaces", [])),
        "toml": collect_toml_findings(facts, toml_root, registered, skills_root),
        "changelog": collect_changelog(facts, changelog, registered),
        "modified_files": [],
    }


def print_report(report):
    out = []
    facts = report["facts"]
    out.append("Skill 四处登记面 dry-run 判定")
    out.append(
        "磁盘事实集: %d 个技能目录（原生 %d / 镜像 %d）"
        % (facts["skills"], facts["native"], facts["mirror"])
    )

    out.append("\n[1] 分类计数")
    for surface in report["surfaces"]:
        out.append("  %s" % surface["label"])
        for category in surface["categories"]:
            flag = "OK   " if category["declared"] == category["actual"] else "DRIFT"
            out.append(
                "    %s %s 声明=%d 实际=%d"
                % (flag, category["title"], category["declared"], category["actual"])
            )

    out.append("\n[2] 计数漂移（表头声明 vs 扫描行数）")
    if not report["count_drift"]:
        out.append("  无")
    for item in report["count_drift"]:
        out.append(
            "  DRIFT %s / %s 声明=%d 实际=%d 差=%+d（子表 %d）"
            % (
                item["surface"],
                item["category"],
                item["declared"],
                item["actual"],
                item["delta"],
                item["tables"],
            )
        )

    out.append("\n[3] 跨面缺行（同名分类，两面名称集合差）")
    if not report["cross_surface"]:
        out.append("  无")
    for item in report["cross_surface"]:
        out.append(
            "  %s: %s(%s) 独有 %s"
            % (item["category"], item["left"], item["left_counts"], item["only_left"] or "-")
        )
        out.append(
            "  %s: %s(%s) 独有 %s"
            % (item["category"], item["right"], item["right_counts"], item["only_right"] or "-")
        )

    out.append("\n[4] 漏登记（磁盘有、登记面零行；需人工判类后才能补行）")
    missing = report["unregistered"]
    if not missing:
        out.append("  无")
    else:
        native = [item["name"] for item in missing if item["kind"] == "native"]
        mirror = [item["name"] for item in missing if item["kind"] == "mirror"]
        out.append("  原生技能 %d 个: %s" % (len(native), native or "-"))
        out.append("  镜像技能 %d 个: %s" % (len(mirror), mirror or "-"))

    out.append("\n[5] TOML 镜像（.meta/toml/.agents/skills/<name>/SKILL.toml）")
    toml = report["toml"]
    out.append(
        "  已登记原生缺镜像 %d 个 / 已登记镜像轨缺镜像 %d 个 / 字段漂移 %d 个 / 孤儿镜像 %d 个"
        % (
            len(toml["missing_native"]),
            len(toml["missing_mirror_track"]),
            len(toml["drift"]),
            len(toml["orphan_mirror"]),
        )
    )
    if toml["missing_native"]:
        out.append("  原生缺镜像: %s" % toml["missing_native"])
    if toml["orphan_mirror"]:
        out.append("  孤儿镜像: %s" % toml["orphan_mirror"])
    for item in toml["drift"]:
        out.append("  DRIFT %s: %s" % (item["name"], "; ".join(item["problems"])))

    out.append("\n[6] CHANGELOG")
    changelog = report["changelog"]
    out.append(
        "  条目 %d 条，最新 v%s，最旧 v%s，新→旧排列=%s"
        % (
            changelog["entries"],
            changelog["latest"],
            changelog["oldest"],
            "是" if changelog["newest_first"] else "否",
        )
    )
    out.append("  重复版本: %s" % (changelog["duplicates"] or "无"))
    out.append(
        "  原生技能缺 CHANGELOG 专名记录 %d 个: %s"
        % (len(changelog["native_missing"]), changelog["native_missing"] or "-")
    )

    out.append("\n[7] 登记面覆盖范围差（同一分类未同时出现在两面）")
    if not report["surface_coverage"]:
        out.append("  无")
    for item in report["surface_coverage"]:
        out.append(
            "  %s: 仅见于 %s，%s 无此分类（共 %d 行）"
            % (item["category"], item["present_in"], item["missing_in"], item["rows"])
        )

    counts = {
        "count_drift": len(report["count_drift"]),
        "cross_surface": len(report["cross_surface"]),
        "unregistered": len(report["unregistered"]),
        "toml_missing_native": len(toml["missing_native"]),
        "toml_drift": len(toml["drift"]),
        "orphan_mirror": len(toml["orphan_mirror"]),
        "changelog_missing": len(changelog["native_missing"]),
    }
    out.append("\n结论: %s；本次未修改任何文件" % "，".join(
        "%s=%d" % (name, value) for name, value in counts.items()
    ))
    sys.stdout.write("\n".join(out) + "\n")
    return counts


def self_test_pipeline():
    """在临时目录搭一个"已对齐"仓库，跑完整链路验证零发现（幂等基线）。

    node 不可用时返回 None，由调用方打印 SKIP。
    """
    source = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), AUDIT_SCRIPT_REL)
    if not os.path.isfile(source) or not shutil.which("node"):
        return None

    with tempfile.TemporaryDirectory() as tmp:
        audit_target = os.path.join(tmp, AUDIT_SCRIPT_REL)
        os.makedirs(os.path.dirname(audit_target))
        shutil.copyfile(source, audit_target)

        skill_dir = os.path.join(tmp, ".agents", "skills", "alpha")
        os.makedirs(skill_dir)
        with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as handle:
            handle.write(
                "---\nname: alpha\nversion: 1.0.0\n"
                "x-toml-ref: ../../../.meta/toml/.agents/skills/alpha/SKILL.toml\n---\n"
            )
        os.makedirs(os.path.join(tmp, ".agents", "capability-registry"))
        table = (
            "### 完整Skill（1个）\n\n"
            "| 技能名 | 路径 |\n|---|---|\n| alpha | .agents/skills/alpha |\n\n"
        )
        with open(os.path.join(tmp, ".agents", "skills", "README.md"), "w", encoding="utf-8") as handle:
            handle.write("# Skills\n\n" + table)
        with open(
            os.path.join(tmp, ".agents", "capability-registry", "02-skills.md"), "w", encoding="utf-8"
        ) as handle:
            handle.write("# Registry\n\n" + table)
        with open(os.path.join(tmp, ".agents", "skills", "CHANGELOG.md"), "w", encoding="utf-8") as handle:
            handle.write("# Changelog\n\n- **v1.0** (2026-01-01): alpha 入库\n")
        toml_dir = os.path.join(tmp, ".meta", "toml", ".agents", "skills", "alpha")
        os.makedirs(toml_dir)
        with open(os.path.join(toml_dir, "SKILL.toml"), "w", encoding="utf-8") as handle:
            handle.write('id = "skill"\ntitle = "Alpha"\ncategory = "skills/alpha"\nversion = "1.0"\n')

        args = argparse.Namespace(
            skills_root=".agents/skills",
            readme=".agents/skills/README.md",
            registry=".agents/capability-registry/02-skills.md",
            changelog=".agents/skills/CHANGELOG.md",
            toml_root=".meta/toml/.agents/skills",
        )
        report = build_report(tmp, args)
        clean = (
            report["count_drift"] == []
            and report["cross_surface"] == []
            and report["unregistered"] == []
            and report["toml"]["missing_native"] == []
            and report["toml"]["drift"] == []
            and report["changelog"]["native_missing"] == []
        )
        if not clean:
            return ("已对齐仓库全链路零发现（幂等基线）", False)

        with open(
            os.path.join(tmp, ".agents", "skills", "README.md"), "a", encoding="utf-8"
        ) as handle:
            handle.write("\n### 完整Skill（2个）\n\n| 技能名 | 路径 |\n|---|---|\n| alpha | .agents/skills/alpha |\n")
        drifted = build_report(tmp, args)
        return (
            "已对齐仓库零发现，篡改表头后可检出漂移",
            len(drifted["count_drift"]) == 1 and drifted["count_drift"][0]["declared"] == 2,
        )


def self_test():
    scenarios = []

    fields = parse_frontmatter("---\nname: demo\nversion: 1.2.3\nsource: x\n---\n# body\n")
    scenarios.append(("frontmatter 解析", fields.get("name") == "demo" and fields.get("source") == "x"))

    with tempfile.TemporaryDirectory() as tmp:
        skills_root = os.path.join(tmp, "skills")
        os.makedirs(os.path.join(skills_root, "alpha"))
        os.makedirs(os.path.join(skills_root, "beta"))
        os.makedirs(os.path.join(skills_root, "empty-dir"))
        with open(os.path.join(skills_root, "alpha", "SKILL.md"), "w", encoding="utf-8") as handle:
            handle.write("---\nname: alpha\nversion: 1.0.0\n---\n")
        with open(os.path.join(skills_root, "beta", "SKILL.md"), "w", encoding="utf-8") as handle:
            handle.write("---\nname: beta\nversion: 2.3.4\nsource: external\n---\n")

        facts = scan_skills(skills_root)
        scenarios.append(
            (
                "磁盘扫描只认含 SKILL.md 的目录",
                [item["name"] for item in facts] == ["alpha", "beta"],
            )
        )
        scenarios.append(
            (
                "镜像识别按 source 字段",
                [item["name"] for item in facts if item["mirror"]] == ["beta"],
            )
        )

        surfaces = [
            {
                "label": "demo",
                "categories": [{"title": "完整Skill", "declared": 1, "actual": 1, "names": ["alpha"]}],
            }
        ]
        unregistered = collect_unregistered(facts, surfaces)
        scenarios.append(
            ("漏登记按登记面并集判定", [item["name"] for item in unregistered] == ["beta"])
        )

        toml_root = os.path.join(tmp, "toml")
        os.makedirs(os.path.join(toml_root, "alpha"))
        with open(os.path.join(toml_root, "alpha", "SKILL.toml"), "w", encoding="utf-8") as handle:
            handle.write('id = "skill"\ntitle = "Alpha"\ncategory = "skills/alpha"\nversion = "1.0"\n')
        toml = collect_toml_findings(facts, toml_root, {"alpha", "beta"}, skills_root)
        scenarios.append(
            (
                "TOML 镜像缺失按轨道分列",
                toml["missing_native"] == [] and toml["missing_mirror_track"] == ["beta"],
            )
        )

        with open(os.path.join(toml_root, "alpha", "SKILL.toml"), "w", encoding="utf-8") as handle:
            handle.write('id = "skill"\ntitle = "Alpha"\ncategory = "skills/wrong"\nversion = "9.9"\n')
        toml = collect_toml_findings(facts, toml_root, {"alpha", "beta"}, skills_root)
        scenarios.append(
            (
                "TOML 字段漂移可检出且版本号不参与判定",
                len(toml["drift"]) == 1 and len(toml["drift"][0]["problems"]) == 1,
            )
        )

        surfaces_two = surfaces + [
            {"label": "second", "categories": [{"title": "完整Skill", "declared": 1, "actual": 1, "names": ["alpha"]}]}
        ]
        scenarios.append(
            (
                "已对齐夹具零发现（幂等基线）",
                collect_count_drift(surfaces_two) == []
                and collect_cross_surface([]) == []
                and collect_surface_coverage(surfaces_two) == [],
            )
        )
        scenarios.append(
            (
                "单面分类可检出覆盖差",
                [item["category"] for item in collect_surface_coverage(surfaces)] == ["完整Skill"],
            )
        )

        changelog = os.path.join(tmp, "CHANGELOG.md")
        with open(changelog, "w", encoding="utf-8") as handle:
            handle.write("# Changelog\n- **v1.1** (2026-01-02): alpha 入库\n- **v1.0** (2026-01-01): 初始\n")
        result = collect_changelog(facts, changelog, {"alpha", "beta"})
        scenarios.append(
            (
                "CHANGELOG 覆盖与倒序判定",
                result["native_missing"] == [] and result["newest_first"] is True and result["entries"] == 2,
            )
        )

    pipeline = self_test_pipeline()
    if pipeline is None:
        sys.stdout.write("[SKIP] 已对齐仓库全链路零发现（未找到 node）\n")
    else:
        scenarios.append(pipeline)

    failed = 0
    for name, passed in scenarios:
        sys.stdout.write("[%s] %s\n" % ("PASS" if passed else "FAIL", name))
        if not passed:
            failed += 1
    sys.stdout.write("\n%d/%d PASS\n" % (len(scenarios) - failed, len(scenarios)))
    return EXIT_OK if failed == 0 else EXIT_DRIFT


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Skill 四处登记面只读判定器（dry-run，不写任何文件）",
        epilog="退出码: 0 零漂移 / 1 仅漏登记 / 2 含计数或镜像漂移 / 3 参数或环境错误",
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--skills-root", default=".agents/skills")
    parser.add_argument("--readme", default=".agents/skills/README.md")
    parser.add_argument("--registry", default=".agents/capability-registry/02-skills.md")
    parser.add_argument("--changelog", default=".agents/skills/CHANGELOG.md")
    parser.add_argument("--toml-root", default=".meta/toml/.agents/skills")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    parser.add_argument("--self-test", action="store_true", help="运行内置夹具")
    return parser.parse_args(argv)


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    args = parse_args(argv)
    if args.self_test:
        return self_test()

    try:
        report = build_report(os.path.abspath(args.repo_root), args)
    except UsageError as exc:
        sys.stderr.write("错误: %s\n" % exc)
        return EXIT_USAGE

    if args.json:
        sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        counts = {
            "count_drift": len(report["count_drift"]),
            "cross_surface": len(report["cross_surface"]),
            "unregistered": len(report["unregistered"]),
            "toml_missing_native": len(report["toml"]["missing_native"]),
            "toml_drift": len(report["toml"]["drift"]),
            "orphan_mirror": len(report["toml"]["orphan_mirror"]),
            "changelog_missing": len(report["changelog"]["native_missing"]),
        }
    else:
        counts = print_report(report)

    if (
        counts["count_drift"]
        or counts["cross_surface"]
        or counts["toml_missing_native"]
        or counts["toml_drift"]
        or counts["orphan_mirror"]
    ):
        return EXIT_DRIFT
    if counts["unregistered"]:
        return EXIT_UNREGISTERED
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
