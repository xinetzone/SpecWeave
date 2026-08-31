#!/usr/bin/env python3
"""批量修复 docs/ 下 Markdown 文件的 frontmatter 合规性（check-frontmatter.py 的配套修复工具）。

修复管线（对每个文件依次尝试）：
  0) YAML 结构修复：
     - 模式 A：`source:` 空键后紧跟 `x-toml-ref:` 行（元数据注入错位），source 的
       列表/映射块被挤到 x-toml-ref 之后 → 将 x-toml-ref 行重排到 source 块之后；
     - 模式 B：双引号标量内含 Windows 反斜杠 / 未转义内层引号 → 外层改单引号（YAML 单引号为字面量）；
     修复后重新解析，仍失败则列入 MANUAL 清单，不做其他修改。
  1) 子目录 index.md 携带 frontmatter → 剥离 frontmatter 块（规范要求子 index 不得带 frontmatter）；
  2) 非 index 文件无 frontmatter → 文件头部追加最小 YAML（type + title）；
  3) 非 index 文件 frontmatter 可解析但缺 type（含空 type 行）→ 按目录/文件名规则推断并插入/替换。

用法:
    python scripts/fix-frontmatter.py             # dry-run：仅输出分析与修复计划
    python scripts/fix-frontmatter.py --apply     # 执行修复
    python scripts/fix-frontmatter.py --analyze   # 仅输出 type 词汇表与分布统计

退出码: 0 正常完成；1 apply 后仍存在需人工修复的 YAML 异常。
"""
import re
import sys
from pathlib import Path
from collections import Counter

try:
    import yaml
except ImportError:
    print("错误: 需要 PyYAML（pip install pyyaml）", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {"_build", "_static", "_templates", ".git", "__pycache__"}
_DELIM = re.compile(r"^---\s*$", re.MULTILINE)

# ---------------------------------------------------------------------------
# type 推断：文件名语义覆盖（okf-bundles 约定）优先，其后按路径前缀（长前缀优先）。
# ---------------------------------------------------------------------------
PREFIX_RULES: list[tuple[str, str]] = [
    ("retrospective/reports", "Report"),
    ("retrospective/patterns", "Pattern"),
    ("retrospective/", "Reference"),
    ("knowledge/learning/okf-bundles", "Wiki Document"),
    ("knowledge/learning/", "Wiki Tutorial"),
    ("knowledge/best-practices", "best-practice"),
    ("knowledge/docs-separation-guide", "Guide"),
    ("knowledge/troubleshooting", "Guide"),
    ("knowledge/quality-assurance", "Guide"),
    ("knowledge/operations", "Guide"),
    ("knowledge/myst-unified-ecosystem", "Wiki Document"),
    ("knowledge/mdi-research", "Reference"),
    ("knowledge/mdi", "Reference"),
    ("knowledge/tech", "Reference"),
    ("knowledge/decisions", "Reference"),
    ("knowledge/categories", "Reference"),
    ("knowledge/tags", "Reference"),
    ("knowledge/scripts", "Reference"),
    ("knowledge/platform", "Reference"),
    ("knowledge/templates", "Reference"),
    ("knowledge/", "Reference"),
    ("tech/", "Guide"),
    ("refactor/", "Report"),
    ("general/", "Concept"),
    ("topics/", "Concept"),
]
DEFAULT_TYPE = "Reference"


def infer_type(rel_s: str) -> str:
    rel = rel_s.replace("\\", "/")
    stem = Path(rel).stem
    base = re.sub(r"^\d+-", "", stem).lower()

    # 文件名/目录语义覆盖（okf-bundles）
    if "/references/" in rel or rel.endswith("/references"):
        return "Insights" if "insight" in base else "Facts"
    if base == "insights":
        return "Insights"
    if base == "verification-report":
        return "VerificationReport"
    if "/concepts/" in rel:
        return "Concept"
    if "cross-bundle-review" in rel or base == "review":
        return "AdversarialReview"
    if "patterns-lessons" in rel:
        return "Patterns"
    if base.startswith("facts"):
        return "Facts"
    if base.startswith("01-facts") or base == "facts":
        return "Facts"

    best = DEFAULT_TYPE
    best_len = -1
    for prefix, t in PREFIX_RULES:
        if rel.startswith(prefix) and len(prefix) > best_len:
            best, best_len = t, len(prefix)
    return best


def parse_frontmatter(text: str):
    """返回 (data, err, fm_span)。fm_span=(start,end) 覆盖 frontmatter 文本切片。"""
    if not text.startswith("---"):
        return None, "无 frontmatter", None
    delims = list(_DELIM.finditer(text))
    if len(delims) < 2:
        return None, "frontmatter 未闭合", None
    span = (0, delims[1].end())
    try:
        data = yaml.safe_load(text[delims[0].end(): delims[1].start()])
        if data is None:
            return {}, None, span
        if not isinstance(data, dict):
            return None, "frontmatter 不是 YAML 映射", span
        return data, None, span
    except yaml.YAMLError as exc:
        return None, f"YAML 解析失败: {exc}", span


def _try_parse_lines(lines: list[str]):
    try:
        yaml.safe_load("\n".join(lines))
        return None
    except yaml.YAMLError as exc:
        return exc


def repair_yaml(text: str):
    """修复已知 YAML 结构错误。返回 (new_text, ok: bool, note: str)。"""
    delims = list(_DELIM.finditer(text))
    if len(delims) < 2:
        return text, False, "无闭合分隔符"
    fm_start, fm_end = delims[0].end(), delims[1].start()
    lines = text[fm_start:fm_end].split("\n")

    # --- 模式 A：source: 空键 + x-toml-ref 错位 → 重排 ---------------------
    reordered = False
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^source:\s*$", line) and i + 1 < len(lines) \
                and re.match(r"^x-toml-ref:", lines[i + 1]):
            xtoml = lines[i + 1]
            j = i + 2
            block: list[str] = []
            while j < len(lines):
                bl = lines[j]
                if bl.strip() == "":
                    break
                if bl.startswith((" ", "\t")) or re.match(r"^-\s", bl):
                    block.append(bl)
                    j += 1
                else:
                    break
            out.append(line)
            out.extend(block)
            out.append(xtoml)
            i = j
            reordered = True
        else:
            out.append(line)
            i += 1

    # --- 模式 B：双引号标量错误 → 外层改单引号（按错误标记定位，迭代修复）----
    quote_fixes = 0
    err = _try_parse_lines(out)
    while err is not None and quote_fixes < 5:
        msg = str(err)
        mark = getattr(err, "problem_mark", None)
        if mark is None or "quoted scalar" not in msg:
            break
        ln = mark.line
        if 0 <= ln < len(out):
            m = re.match(r'^(\s*[\w\-]+:\s*)"(.*)"(\s*)$', out[ln])
            if m:
                inner = m.group(2).replace("'", "''")
                out[ln] = f"{m.group(1)}'{inner}'{m.group(3)}"
                quote_fixes += 1
                err = _try_parse_lines(out)
                continue
        break

    if not (reordered or quote_fixes):
        return text, False, "无匹配修复模式"

    new_fm = "\n".join(out)
    try:
        yaml.safe_load(new_fm)
    except yaml.YAMLError as exc:
        return text, False, f"修复后仍失败: {str(exc)[:80].replace(chr(10), ' ')}"
    new_text = text[:fm_start] + new_fm + text[fm_end:]
    return new_text, True, f"重排source块={reordered}, 引号修复={quote_fixes}"


def iter_md_files() -> list[Path]:
    files = []
    for f in ROOT.rglob("*.md"):
        if any(p in EXCLUDE_DIRS or p.startswith(".") for p in f.relative_to(ROOT).parts):
            continue
        files.append(f)
    return sorted(files)


def title_from_text(text: str, fallback: str) -> str:
    for line in text.splitlines():
        m = re.match(r"^#\s+(.+?)\s*$", line)
        if m:
            return m.group(1).strip().replace('"', "'")
    return fallback.replace("-", " ").replace("_", " ").title()


def add_type_line(text: str, t: str) -> str:
    """在 frontmatter 中插入 type（若已有空 type 行则替换）。"""
    delims = list(_DELIM.finditer(text))
    # 注意：_DELIM 的 $ 匹配在换行符之前，插入位置必须取首行整行结束（含换行）
    m_open = re.match(r"^---[^\n]*\n", text)
    fm_open_end = m_open.end() if m_open else delims[0].end()
    fm_block = text[fm_open_end:delims[1].start()]
    # 已有空 type 行：type: / type: "" / type: ''
    m_empty = re.search(r"^type:\s*(?:['\"]{2})?\s*$", fm_block, re.MULTILINE)
    if m_empty:
        abs_start = fm_open_end + m_empty.start()
        abs_end = fm_open_end + m_empty.end()
        return text[:abs_start] + f"type: {t}" + text[abs_end:]
    return text[:fm_open_end] + f"type: {t}\n" + text[fm_open_end:]


def heal_broken_insertion(text: str) -> tuple[str, bool]:
    """纠偏：早期版本误将 type 插到分隔符同一行，产出 `---type: X` 首行污染。"""
    m = re.match(r"^---(type:[^\n]*)\n", text)
    if not m:
        return text, False
    return "---\n" + m.group(1) + "\n" + text[m.end():], True


# ---------------------------------------------------------------------------
# 分析模式
# ---------------------------------------------------------------------------
def analyze(files: list[Path]):
    type_vocab: Counter = Counter()
    dir_type: dict[str, Counter] = {}
    miss_type_dirs: Counter = Counter()
    sub_index, no_fm, yaml_err = [], [], []
    for f in files:
        rel = f.relative_to(ROOT)
        rel_s = str(rel)
        text = f.read_text(encoding="utf-8")
        is_root = f.name == "index.md" and len(rel.parts) == 1
        data, err, _ = parse_frontmatter(text)
        if f.name == "log.md":
            continue
        if f.name == "index.md":
            if not is_root and data is not None:
                sub_index.append(rel_s)
            continue
        if data is None:
            if err and err.startswith("YAML"):
                yaml_err.append((rel_s, err))
            else:
                no_fm.append((rel_s, err))
            continue
        t = data.get("type")
        if not t:
            prefix = "/".join(rel.parts[:2]) if len(rel.parts) > 2 else rel.parts[0]
            miss_type_dirs[prefix] += 1
        else:
            type_vocab[str(t)] += 1
            dir_type.setdefault(rel.parts[0], Counter())[str(t)] += 1

    print("== 子 index 带 frontmatter（%d，将剥离）==" % len(sub_index))
    for x in sub_index:
        print("  ", x)
    print("\n== 无 frontmatter（%d，将补最小 YAML）==" % len(no_fm))
    for x, _ in no_fm:
        print("  ", x, "->", infer_type(x))
    print("\n== YAML 异常（%d，将尝试结构修复，失败转人工）==" % len(yaml_err))
    for x, e in yaml_err:
        print("  ", x, "|", str(e)[:70].replace("\n", " "))
    print("\n== 合规文件 type 词汇表 ==")
    for t, n in type_vocab.most_common():
        print(f"  {n:5d}  {t}")
    print("\n== 缺 type 文件按两级目录分布（含推断值）==")
    for d, n in miss_type_dirs.most_common(40):
        print(f"  {n:5d}  {d}  -> {infer_type(d + '/x.md')}")
    return sub_index, no_fm, yaml_err


# ---------------------------------------------------------------------------
# 修复模式
# ---------------------------------------------------------------------------
def apply_fixes(files: list[Path]) -> int:
    n_repair = n_strip = n_addtype = n_addfm = 0
    manual = []
    for f in files:
        rel_s = str(f.relative_to(ROOT))
        text = f.read_text(encoding="utf-8")
        is_root = f.name == "index.md" and len(f.relative_to(ROOT).parts) == 1
        if f.name == "log.md":
            continue

        # 0) 先尝试 YAML 结构修复（仅对解析失败的文件）
        data, err, span = parse_frontmatter(text)
        if data is None and err and err.startswith("YAML"):
            new_text, ok, note = repair_yaml(text)
            if ok:
                f.write_text(new_text, encoding="utf-8")
                n_repair += 1
                print(f"  REPAIR  {rel_s}  ({note})")
                text = new_text
                data, err, span = parse_frontmatter(text)
            else:
                manual.append((rel_s, f"YAML修复未成功: {note}"))
                continue

        # 1) 子 index 剥离 frontmatter
        if f.name == "index.md":
            if not is_root and data is not None:
                f.write_text(text[span[1]:].lstrip("\n"), encoding="utf-8")
                n_strip += 1
                print(f"  STRIP   {rel_s}")
            continue

        # 2) 无 frontmatter → 补最小 YAML
        if data is None:
            if err and ("未闭合" in err or "不是 YAML" in err):
                manual.append((rel_s, err))
                continue
            t = infer_type(rel_s)
            title = title_from_text(text, f.stem)
            f.write_text(f'---\ntype: {t}\ntitle: "{title}"\n---\n\n' + text, encoding="utf-8")
            n_addfm += 1
            print(f"  ADDFM   {rel_s}  type={t}")
            continue

        # 3) 缺 type → 插入/替换
        if not data.get("type"):
            t = infer_type(rel_s)
            f.write_text(add_type_line(text, t), encoding="utf-8")
            n_addtype += 1
            print(f"  ADDTYPE {rel_s}  type={t}")

    print(f"\n汇总: YAML结构修复={n_repair}，剥离子index={n_strip}，"
          f"补type={n_addtype}，补frontmatter={n_addfm}，人工清单={len(manual)}")
    for x, e in manual:
        print("  MANUAL ", x, "|", str(e)[:90].replace("\n", " "))
    return len(manual)


def main() -> int:
    args = sys.argv[1:]
    files = iter_md_files()
    if "--analyze" in args:
        analyze(files)
        return 0
    if "--apply" in args:
        print("Applying frontmatter fixes...\n")
        remaining = apply_fixes(files)
        return 1 if remaining else 0
    print("DRY-RUN（加 --apply 执行；加 --analyze 仅看统计）\n")
    sub_index, no_fm, yaml_err = analyze(files)
    print("\n== 修复计划 ==")
    print(f"  YAML 结构修复（模式 A/B）: {len(yaml_err)}（失败转人工）")
    print(f"  剥离子 index frontmatter: {len(sub_index)}")
    print(f"  补最小 frontmatter:       {len(no_fm)}")
    print(f"  补 type 字段:             其余缺 type 文件（见目录分布）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
