# -*- coding: utf-8 -*-
"""私域 Wiki 增量的机械验证（V 门）。

检查项:
  1. 事实台账内 F 编号连续无断号（含重复编号告警）；
  2. wiki 其它 Markdown 对 F 编号的引用无悬空（指向台账未定义编号）；
  2b. 示意/预告性编号可经 WHITELIST 豁免（文件名→{编号:原因}），命中打印 [whitelist] 行不判失败；
      白名单是审计项：须带原因、对应内容删除后同步移除，不得用于真实事实引用；
  3. 本次增量区间 [--from, --to] 每条事实在台账外至少被引用一次
     （登记了但教程零引用 = 并入不完整）；
  4. 可选 --pdf：页数、书签清单与目的页、目录/全文内部链接数、
     关键词归一化命中（PDF 抽取中文常带空格，自动去空白后匹配）、MD5/字节。

用法:
    python verify_increment.py --wiki <wiki目录> --from 122 --to 153 \
        [--ledger core/concepts/fact-ledger.md] \
        [--pdf <成品.pdf> --keywords 三大习惯 F-153 反向请教]

退出码: 0 全部通过；1 存在硬失败（断号/悬空/零引用/关键词缺失）。
"""
import argparse
import hashlib
import pathlib
import re
import sys

F_PAT = re.compile(r"F-(\d{3})")
# 事实定义行：形如「- **F-122** [D5] ...」（列表项 + 加粗编号开头）
F_DEF_PAT = re.compile(r"^\s*[-*]\s+\*\*F-(\d{3})\*\*", re.MULTILINE)

# 悬空引用白名单：{文件名: {编号int: 原因}}。仅限示意/预告性提及（脚手架实跑记录、
# 「下一编号」示意等），不得用于真实事实引用；每条须带原因，内容删除后同步移除。
# 空集 = 当前无激活豁免。
WHITELIST: dict[str, dict[int, str]] = {
    "CHANGELOG.md": {},
}


def filter_dangling(
    nums: set[int], defined: set[int], allow: set[int]
) -> tuple[set[str], set[int]]:
    """返回 (悬空引用编号串, 白名单豁免编号)。"""
    bad = {f"F-{n:03d}" for n in nums if n not in defined and n not in allow}
    skipped = {n for n in nums if n not in defined and n in allow}
    return bad, skipped


def norm(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def check_ledger(wiki: pathlib.Path, ledger_name: str):
    ledger = wiki / ledger_name
    text = ledger.read_text(encoding="utf-8")
    # 以定义行为准；若该台账不使用「- **F-NNN**」约定则回退为全部提及
    defs = [int(m) for m in F_DEF_PAT.findall(text)]
    nums = defs if defs else [int(m) for m in F_PAT.findall(text)]
    defined = sorted(set(nums))
    duplicates = sorted({n for n in nums if nums.count(n) > 1})
    gaps = [n for n in range(defined[0], defined[-1] + 1) if n not in defined]
    return ledger, defined, gaps, duplicates


def check_references(wiki: pathlib.Path, ledger_name: str, defined: set[int]):
    dangling: dict[str, set[str]] = {}
    refs: dict[str, set[int]] = {}
    for md in sorted(wiki.rglob("*.md")):
        if md.name == ledger_name or "_template" in md.parts:
            continue  # 模板包不参与引用检查（示例编号非真实事实）
        nums = {int(m) for m in F_PAT.findall(md.read_text(encoding="utf-8"))}
        refs[str(md.relative_to(wiki))] = nums
        bad, skipped = filter_dangling(nums, defined, set(WHITELIST.get(md.name, {})))
        if skipped:
            reasons = WHITELIST.get(md.name, {})
            print(
                f"[whitelist] {md.relative_to(wiki)}: "
                + ", ".join(f"F-{n:03d}（{reasons[n]}）" for n in sorted(skipped))
                + " —— 豁免不判失败"
            )
        if bad:
            dangling[md.name] = bad
    return refs, dangling


def check_pdf(pdf: pathlib.Path, keywords: list[str], expect_bookmarks: int | None):
    from pypdf import PdfReader

    data = pdf.read_bytes()
    reader = PdfReader(str(pdf))
    bookmarks = []
    for item in reader.outline or []:
        if isinstance(item, list):
            continue
        bookmarks.append((reader.get_destination_page_number(item) + 1, item.title))

    links = 0
    for page in reader.pages:
        for annot in page.get("/Annots") or []:
            obj = annot.get_object()
            if obj.get("/Subtype") == "/Link" and ("/A" in obj or "/Dest" in obj):
                links += 1

    full = norm("".join(pg.extract_text() or "" for pg in reader.pages))
    missing = [kw for kw in keywords if norm(kw) not in full]

    return {
        "pages": len(reader.pages),
        "size": len(data),
        "md5": hashlib.md5(data).hexdigest(),
        "bookmarks": bookmarks,
        "links": links,
        "missing_keywords": missing,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki", required=True, type=pathlib.Path)
    ap.add_argument("--ledger", default="core/concepts/fact-ledger.md")
    ap.add_argument("--from", dest="start", type=int, required=True)
    ap.add_argument("--to", dest="end", type=int, required=True)
    ap.add_argument("--pdf", type=pathlib.Path)
    ap.add_argument("--keywords", nargs="*", default=[])
    ap.add_argument("--expect-bookmarks", type=int, default=None)
    args = ap.parse_args()

    failures: list[str] = []

    ledger, defined, gaps, duplicates = check_ledger(args.wiki, args.ledger)
    print(f"[ledger] {ledger.name}: {len(defined)} facts, F-{defined[0]:03d}~F-{defined[-1]:03d}")
    if gaps:
        failures.append(f"编号断号: {gaps}")
    if duplicates:
        # 台账正文中同一编号可能在 G1 表等处重复出现，仅告警
        print(f"[warn] 编号在台账中重复出现: {[f'F-{n:03d}' for n in duplicates]}")

    refs, dangling = check_references(args.wiki, args.ledger, set(defined))
    if dangling:
        failures.append(f"悬空引用: { {k: sorted(v) for k, v in dangling.items()} }")
    else:
        print(f"[refs] {len(refs)} 个教程页引用检查通过，无悬空编号")

    unreferenced = [
        f"F-{n:03d}"
        for n in range(args.start, args.end + 1)
        if not any(n in nums for nums in refs.values())
    ]
    if unreferenced:
        failures.append(f"增量事实在台账外零引用: {unreferenced}")
    else:
        print(f"[increment] F-{args.start:03d}~F-{args.end:03d} 全部被教程页引用")

    if args.pdf:
        if not args.pdf.is_file():
            failures.append(f"PDF 不存在: {args.pdf}")
        else:
            info = check_pdf(args.pdf, args.keywords, args.expect_bookmarks)
            print(f"[pdf] {args.pdf.name}: {info['pages']} 页 / {info['size']} 字节 / md5 {info['md5']}")
            print(f"[pdf] 书签 {len(info['bookmarks'])} 条，内部链接 {info['links']} 个")
            for page_no, title in info["bookmarks"]:
                print(f"      p{page_no:02d}  {title}")
            if args.expect_bookmarks and len(info["bookmarks"]) != args.expect_bookmarks:
                failures.append(
                    f"书签数 {len(info['bookmarks'])} != 预期 {args.expect_bookmarks}"
                )
            if info["missing_keywords"]:
                failures.append(f"PDF 关键词缺失: {info['missing_keywords']}")
            else:
                print(f"[pdf] 关键词 {len(args.keywords)} 个全部命中")

    print("-" * 60)
    if failures:
        print("FAIL:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PASS: 增量验证全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
