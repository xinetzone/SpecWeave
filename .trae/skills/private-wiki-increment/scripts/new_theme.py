# -*- coding: utf-8 -*-
"""新主题接入脚手架：从 themes/_template/ 生成 themes/<slug>/ 骨架 + logs/<slug>/。

做什么：
  1. 校验 slug（kebab-case）与幂等（themes / logs 同名目录已存在则拒绝）；
  2. 扫描根级台账与 09/10，计算全局续号：F起 = max(F)+1、I-x、AP-x、P-x；
  3. 复制页面骨架（01-overview.md、NN-tutorial-page.md），替换全部**元数据**占位符；
  4. 创建 logs/<slug>/（源纪要放这里）；
  5. 打印剩余正文占位符数与后续步骤（SOP ②⑤⑥ + 双门禁命令）。

不做：登记事实（SOP ②，走增量流程）、粘贴沉淀片段（SOP ⑤，从 _template 复制）、git 提交。

用法：
  python new_theme.py --slug <slug> --title <主题名> [--tag <标签如 E1>] [--date YYYY-MM-DD] [--session <id>] [--wiki <wiki路径>]
"""
import argparse
import datetime
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[4]
DEFAULT_WIKI = REPO / "playground" / "life" / "workbuddy" / "wiki"
SLUG_PAT = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def max_num(text: str, pat: re.Pattern) -> int:
    nums = [int(m) for m in pat.findall(text)]
    return max(nums) if nums else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="新主题接入脚手架")
    ap.add_argument("--slug", required=True, help="主题目录名，小写 kebab-case")
    ap.add_argument("--title", required=True, help="主题中文全名")
    ap.add_argument("--tag", default=None, help="台账信源标签（不带方括号，如 E1）；缺省按 slug 首字母推导并查重")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--session", default=None, help="会话标识；缺省 sc-<日期>-<slug>")
    ap.add_argument("--wiki", type=pathlib.Path, default=DEFAULT_WIKI)
    a = ap.parse_args()

    if not SLUG_PAT.match(a.slug):
        sys.exit(f"slug 不合法：{a.slug}（需小写 kebab-case，例：erqi-lifekey）")
    wiki = a.wiki.resolve()
    theme_dst = wiki / "themes" / a.slug
    logs_dst = wiki.parent / "logs" / a.slug
    tpl = wiki / "themes" / "_template"
    if theme_dst.exists() or logs_dst.exists():
        sys.exit(f"已存在，拒绝重复接入：{theme_dst if theme_dst.exists() else logs_dst}")
    if not tpl.is_dir():
        sys.exit(f"模板包不存在：{tpl}")

    # 全局续号（禁止凭记忆，脚本统一计算）
    ledger = (wiki / "00-fact-ledger.md").read_text(encoding="utf-8")
    f_start = max_num(ledger, re.compile(r"F-(\d{3})")) + 1
    tag = a.tag.lstrip("[").rstrip("]") if a.tag else None
    if not tag:
        prefix = next((ch.upper() for ch in a.slug if ch.isalpha()), "X")
        n = 1
        while f"[{prefix}{n}]" in ledger:
            n += 1
        tag = f"{prefix}{n}"
    ins = (wiki / "09-insights-patterns.md").read_text(encoding="utf-8")
    anti = (wiki / "10-antipatterns-boundaries.md").read_text(encoding="utf-8")
    i_next = max_num(ins, re.compile(r"I-(\d+)")) + 1
    ap_next = max_num(anti, re.compile(r"AP(\d+)")) + 1
    p_next = max_num(ins, re.compile(r"P-(\d+)")) + 1

    session = a.session or f"sc-{a.date.replace('-', '')}-{a.slug}"
    meta = {
        "{{SLUG}}": a.slug,
        "{{主题名}}": a.title,
        "{{信源标签}}": f"[{tag}]",
        "{{F起}}~{{F止}}": f"F-{f_start:03d} 起",
        "{{F起}}": f"F-{f_start:03d}",
        "{{F止}}": "（登记中）",
        "{{I-x}}": f"I-{i_next}",
        "{{AP-x}}": f"AP{ap_next}",
        "{{P-x}}": f"P-{p_next}",
        "{{日期}}": a.date,
        "{{session-id}}": session,
    }

    theme_dst.mkdir(parents=True)
    logs_dst.mkdir(parents=True)
    copied = []
    for src in sorted(tpl.glob("*.md")):
        if src.name == "README.md":  # 使用说明留在模板包，不随主题走
            continue
        text = src.read_text(encoding="utf-8")
        for k, v in meta.items():
            text = text.replace(k, v)
        (theme_dst / src.name).write_text(text, encoding="utf-8")
        copied.append(src.name)

    leftover = sum(
        len(re.findall(r"\{\{", md.read_text(encoding="utf-8")))
        for md in theme_dst.glob("*.md")
    )

    print(f"主题骨架:   {theme_dst}")
    print(f"源材料目录: {logs_dst}（空，纪要放这里）")
    print(f"复制文件:   {', '.join(copied)}")
    print(f"全局续号:   F起=F-{f_start:03d}｜信源 [{tag}]｜洞察 I-{i_next}｜反模式 AP{ap_next}｜模式 P-{p_next}")
    print(f"正文占位符剩余 {leftover} 处（写页时人工清零；元数据占位符已全部替换）")
    print("后续（themes/README SOP）：② 事实登记入根级台账（用 _template/ledger-section.md）"
          "→ ⑤ 沉淀片段粘贴根级 09/10（用 _template/synthesis-snippets.md）→ ⑥ CHANGELOG/REVIEW/README 登记")
    print("门禁：python .agents/scripts/check-links.py --path <wiki目录>")
    print("      python .trae/skills/private-wiki-increment/scripts/verify_increment.py --wiki <wiki目录> --from <F起> --to <F止>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
