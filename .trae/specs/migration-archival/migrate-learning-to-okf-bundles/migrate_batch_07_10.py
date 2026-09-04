# -*- coding: utf-8 -*-
"""learning → OKF bundles 迁移（07/08/09/10 分类 + learning 根级散文件）。

数据驱动：脚本负责
- 复制内容 md（跳过 index/README/隐私元数据）
- 重写 frontmatter 为 OKF v0.2（type/title/description/tags/sources/generated/status/stale_after）
- 隐私清洗（个人文件系统路径 → 占位符；retrospective 链接去链接化）
- 中文内嵌引号全角（代码块安全）
- 生成目录/束根 index.md（toctree）与 log.md
- 合并场景：向既有束新增子目录并更新其根 index.md 的 toctree + log
不执行 git 操作。禁改共享索引（由注册清单交给编排层）。
"""
from __future__ import annotations
import re
import shutil
from pathlib import Path

REPO = Path(r"d:\spaces\SpecWeave")
LEARNING = REPO / "docs" / "knowledge" / "learning"
BUNDLES = REPO / "projects" / "awesome-okf-xs" / "doc" / "bundles"

DATE = "2026-09-02"
GEN_BY = "process:learning-bundles-migration"
STALE = "2027-09-02"

SKIP_NAMES = {
    "readme.md", "log.md", "seven-concepts-report.md",
    "02-seven-concepts-report.md", "03-seven-concepts-report.md",
    "index.md", "categories.md", "learning-paths.md",
}
SKIP_PREFIXES = ("retrospective", "verification-report")

STATS = {"files": 0, "bundles_new": 0, "bundles_merged": 0, "skipped": 0}
REPORT = []


# ---------- frontmatter ----------
def split_frontmatter(text: str):
    if not text.startswith("---"):
        return "", text
    lines = text.splitlines(keepends=True)
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "".join(lines[1:i]), "".join(lines[i + 1:])
    return "", text


def parse_fm(fm_text: str) -> dict:
    import yaml
    try:
        data = yaml.safe_load(fm_text)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def yaml_str(v) -> str:
    if v is None:
        return '""'
    s = str(v).replace("\n", " ").strip()
    if s == "":
        return '""'
    if any(c in s for c in [":", "#", "{", "}", "[", "]", ",", "&", "*", "!", "|", ">", "'", '"', "%", "@", "`"]) or s != s.strip():
        return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return s


def build_frontmatter(src_fm: dict, rel_source: str, doc_type: str = "Concept") -> str:
    title = src_fm.get("title") or ""
    desc = src_fm.get("summary") or src_fm.get("description") or ""
    tags = src_fm.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    origin = src_fm.get("source") or ""
    if isinstance(origin, list):
        origin = "; ".join(str(x) for x in origin)

    L = ["---", f"type: {doc_type}"]
    if title:
        L.append(f"title: {yaml_str(title)}")
    if desc:
        L.append(f"description: {yaml_str(desc)}")
    if tags:
        L.append("tags: [" + ", ".join(yaml_str(t) for t in tags[:12]) + "]")
    L.append(f'generated: {{ by: "{GEN_BY}", at: "{DATE}T00:00:00Z" }}')
    L.append("status: draft")
    L.append(f"stale_after: {STALE}")
    L.append("sources:")
    L.append("  - id: learning-source")
    L.append(f"    resource: {yaml_str('SpecWeave docs/knowledge/learning/' + rel_source)}")
    if origin:
        L.append(f"    title: {yaml_str(str(origin))}")
    L.append("---")
    return "\n".join(L) + "\n"


# ---------- privacy & quotes ----------
CJK_PUNCT = "，。、；：！？（）《》【】…—·"


def is_cjk(ch: str) -> bool:
    if not ch:
        return False
    o = ord(ch)
    return (0x4E00 <= o <= 0x9FFF) or (0x3400 <= o <= 0x4DBF) or ch in CJK_PUNCT


def has_cjk(s: str) -> bool:
    return any(is_cjk(c) for c in s)


QUOTE_RE = re.compile(r'"([^"\n]*)"')


def convert_quotes_line(line: str) -> str:
    """成对半角引号 → 全角：内容含中文且至少一侧紧邻中文。"""
    def repl(m):
        content = m.group(1)
        prev = line[m.start() - 1] if m.start() > 0 else ""
        nxt = line[m.end()] if m.end() < len(line) else ""
        if has_cjk(content) and (is_cjk(prev) or is_cjk(nxt)):
            return "\u201c" + content + "\u201d"
        return m.group(0)
    return QUOTE_RE.sub(repl, line)


def clean_body(body: str) -> str:
    # 个人文件系统路径 → 占位符
    body = re.sub(r"[dD]:\\spaces\\SpecWeave", "<specweave-workspace>", body)
    body = re.sub(r"[dD]:/spaces/SpecWeave", "<specweave-workspace>", body)
    body = re.sub(r"[dD]:\\AI\\?", "<local-workspace>", body)
    body = re.sub(r"C:\\Users\\xinzo", "<user-home>", body)
    body = re.sub(r"C:/Users/xinzo", "<user-home>", body)
    # 指向私有 retrospective 的链接 → 去链接化
    body = re.sub(r"\[([^\]]+)\]\([^)]*retrospective[^)]*\)", r"\1", body)
    # 指向源仓库 AGENTS.md 的越界相对链接 → 去链接化
    body = re.sub(r"\[([^\]]+)\]\((?:\.\./)+AGENTS\.md[^)]*\)", r"\1", body)

    # 中文内嵌引号全角：跳过围栏代码块与行内代码
    lines = body.split("\n")
    in_fence = False
    fence_marker = ""
    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
            continue
        if in_fence:
            continue
        parts = line.split("`")
        for j in range(0, len(parts), 2):  # 偶数下标为非代码段
            parts[j] = convert_quotes_line(parts[j])
        lines[idx] = "`".join(parts)
    return "\n".join(lines)


def should_skip(p: Path) -> bool:
    name = p.name.lower()
    if name in SKIP_NAMES:
        return True
    if any(name.startswith(pre) for pre in SKIP_PREFIXES):
        return True
    if p.suffix.lower() in {".gitkeep", ".pyc"}:
        return True
    return False


def transform_md(src: Path, rel_source: str, doc_type: str = "Concept") -> str:
    text = src.read_text(encoding="utf-8")
    fm_text, body = split_frontmatter(text)
    src_fm = parse_fm(fm_text)
    body = clean_body(body)
    return build_frontmatter(src_fm, rel_source, doc_type) + body


def write_doc(dst: Path, content: str):
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")
    STATS["files"] += 1


def rel_to_learning(p: Path) -> str:
    try:
        return str(p.relative_to(LEARNING)).replace("\\", "/")
    except ValueError:
        return p.name


# ---------- content discovery ----------
def content_files(d: Path) -> list[Path]:
    out = []
    if not d.is_dir():
        return out
    for f in sorted(d.iterdir()):
        if f.is_file() and f.suffix == ".md" and not should_skip(f):
            out.append(f)
    return out


def content_subdirs(d: Path) -> list[Path]:
    out = []
    if not d.is_dir():
        return out
    for f in sorted(d.iterdir()):
        if f.is_dir() and not f.name.startswith(".") and not f.name.lower().startswith(SKIP_PREFIXES):
            out.append(f)
    return out


def dedup(files: list[Path]) -> list[Path]:
    seen, out = set(), []
    for f in files:
        if f.name in seen:
            STATS["skipped"] += 1
            continue
        seen.add(f.name)
        out.append(f)
    return out


# ---------- index/log generators ----------
def gen_subdir_index(title: str, files: list[Path], subdirs: list[Path], intro: str = "") -> str:
    L = [f"# {title}", ""]
    if intro:
        L += [intro, ""]
    entries = []
    for s in subdirs:
        L.append(f"* [{s.name}/]({s.name}/index.md)")
        entries.append(f"{s.name}/index")
    for f in files:
        L.append(f"* [{f.stem}]({f.name})")
        entries.append(f.stem)
    L += ["", "```{toctree}", ":hidden:", ":maxdepth: 7", ""]
    L += entries
    L += ["```", ""]
    return "\n".join(L)


def gen_bundle_index(title: str, description: str, nav: list[tuple[str, str]], entries: list[str], extra: str = "") -> str:
    L = ["---", 'okf_version: "0.2"', f"title: {yaml_str(title)}",
         f"description: {yaml_str(description)}", "---", "",
         f"# {title}", "", description, ""]
    if extra:
        L += [extra, ""]
    for label, relpath in nav:
        L.append(f"* [{label}]({relpath})")
    L += ["", "```{toctree}", ":hidden:", ":maxdepth: 7", ""]
    L += entries
    L += ["```", ""]
    return "\n".join(L)


def gen_log(batch: str, merge_lines: list[str] | None = None) -> str:
    L = ["# 更新日志", "", f"## {DATE}", "",
         f"**Migration**: 从 SpecWeave docs/knowledge/learning/ 迁入 awesome-okf-xs（{batch}）", "",
         "* 章节文档 frontmatter 重写为 OKF v0.2（type/title/description/tags/sources/generated/status/stale_after）",
         "* 隐私清洗：个人文件系统路径替换为占位符；中文内嵌引号转全角",
         "* 舍弃：源侧 README.md/index.md（导航）、log.md、seven-concepts-report.md、retrospective*/verification-report*（隐私元数据）"]
    if merge_lines:
        L.append("")
        L += merge_lines
    L.append("")
    return "\n".join(L)


# ---------- FLAT new bundle ----------
def new_flat_bundle(bundle_rel: str, title: str, description: str,
                    sources: list, batch: str):
    root = BUNDLES / bundle_rel
    concepts = root / "concepts"
    files = []
    for src in sources:
        if src.is_dir():
            files += content_files(src)
        elif src.is_file() and not should_skip(src):
            files.append(src)
    uniq = dedup(files)
    for f in uniq:
        write_doc(concepts / f.name, transform_md(f, rel_to_learning(f)))
    nav_files = sorted(uniq, key=lambda p: p.name)
    write_doc(concepts / "index.md", gen_subdir_index("概念文档", nav_files, []))
    write_doc(root / "index.md", gen_bundle_index(
        title, description,
        [(f"concepts/（{len(nav_files)} 篇）", "concepts/index.md")],
        ["concepts/index", "log"]))
    write_doc(root / "log.md", gen_log(batch))
    STATS["bundles_new"] += 1
    REPORT.append(f"NEW  {bundle_rel}  concepts={len(nav_files)}")


# ---------- TREE new bundle（保留子目录） ----------
def mirror_tree(src_dir: Path, dst_dir: Path, title: str | None = None):
    files = content_files(src_dir)
    subs = content_subdirs(src_dir)
    for f in files:
        write_doc(dst_dir / f.name, transform_md(f, rel_to_learning(f)))
    for s in subs:
        mirror_tree(s, dst_dir / s.name)
    write_doc(dst_dir / "index.md", gen_subdir_index(
        title or src_dir.name.replace("-", " ").title(), files, subs))
    return len(files), len(subs)


def new_tree_bundle(bundle_rel: str, title: str, description: str,
                    src_dirs: list[Path], root_files: list[Path],
                    batch: str, root_label: str = "concepts",
                    root_files_at_bundle_root: bool = False):
    root = BUNDLES / bundle_rel
    entries = []
    nav = []
    if root_files:
        uniq = dedup(root_files)
        if root_files_at_bundle_root:
            for f in uniq:
                write_doc(root / f.name, transform_md(f, rel_to_learning(f)))
            nav.append((f"（束根 {len(uniq)} 篇总览文档）", "#"))
            entries += [f.stem for f in sorted(uniq, key=lambda p: p.name)]
        else:
            rf_dir = root / root_label
            for f in uniq:
                write_doc(rf_dir / f.name, transform_md(f, rel_to_learning(f)))
            write_doc(rf_dir / "index.md", gen_subdir_index("综合文档", sorted(uniq, key=lambda p: p.name), []))
            nav.append((f"{root_label}/（{len(uniq)} 篇综合文档）", f"{root_label}/index.md"))
            entries.append(f"{root_label}/index")
    for sd in src_dirs:
        mirror_tree(sd, root / sd.name)
        nav.append((f"{sd.name}/", f"{sd.name}/index.md"))
        entries.append(f"{sd.name}/index")
    entries.append("log")
    nav = [(l, p) for l, p in nav if p != "#"]
    write_doc(root / "index.md", gen_bundle_index(title, description, nav, entries))
    write_doc(root / "log.md", gen_log(batch))
    STATS["bundles_new"] += 1
    REPORT.append(f"NEW  {bundle_rel}  subdirs={[s.name for s in src_dirs]} root_files={len(root_files)}")


# ---------- MERGE helpers ----------
def append_to_bundle_toctree(index_md: Path, entry: str):
    txt = index_md.read_text(encoding="utf-8")
    if re.search(rf"^\s*{re.escape(entry)}\s*$", txt, re.M):
        return
    toc = txt.find("```{toctree}")
    if toc == -1:
        return
    close = txt.find("```", toc + 3)
    if close == -1:
        return
    txt = txt[:close] + entry + "\n" + txt[close:]
    index_md.write_text(txt, encoding="utf-8")


def append_log(log_md: Path, batch: str, note: str):
    entry = f"**Migration**: {note}"
    if log_md.exists():
        txt = log_md.read_text(encoding="utf-8")
        if note in txt:
            return  # 幂等：重跑不重复登记
    else:
        txt = ""
    if not txt:
        log_md.write_text(gen_log(batch, [entry]), encoding="utf-8")
        return
    m = re.search(rf"^## {DATE}.*$", txt, re.M)
    if m:
        txt = txt[:m.end()] + "\n\n" + entry + txt[m.end():]
    else:
        m2 = re.search(r"^## ", txt, re.M)
        block = f"## {DATE}\n\n{entry}\n\n"
        if m2:
            txt = txt[:m2.start()] + block + txt[m2.start():]
        else:
            txt += "\n" + block
    log_md.write_text(txt, encoding="utf-8")


def merge_tree_into_bundle(bundle_rel: str, subdir_name: str, src_dir: Path,
                           subdir_title: str, batch: str, merge_note: str):
    root = BUNDLES / bundle_rel
    dst = root / subdir_name
    nfiles, nsubs = mirror_tree(src_dir, dst, subdir_title)
    append_to_bundle_toctree(root / "index.md", f"{subdir_name}/index")
    append_log(root / "log.md", batch, merge_note)
    append_to_bundle_toctree(root / "index.md", "log")
    STATS["bundles_merged"] += 1
    REPORT.append(f"MERGE {bundle_rel} <- {subdir_name}/ ({src_dir.name}, {nfiles} files, {nsubs} subdirs)")


def merge_files_as_subdir(bundle_rel: str, subdir_name: str, files: list[Path],
                          subdir_title: str, batch: str, merge_note: str):
    """把若干散文件转换后作为既有束的新子目录。"""
    root = BUNDLES / bundle_rel
    dst = root / subdir_name
    uniq = dedup(files)
    for f in uniq:
        write_doc(dst / f.name, transform_md(f, rel_to_learning(f)))
    write_doc(dst / "index.md", gen_subdir_index(subdir_title, sorted(uniq, key=lambda p: p.name), []))
    append_to_bundle_toctree(root / "index.md", f"{subdir_name}/index")
    append_log(root / "log.md", batch, merge_note)
    append_to_bundle_toctree(root / "index.md", "log")
    STATS["bundles_merged"] += 1
    REPORT.append(f"MERGE {bundle_rel} <- {subdir_name}/ ({len(uniq)} files)")


# =====================================================================
L7 = LEARNING / "07-vendor-product-learning"
L8 = LEARNING / "08-systems-infrastructure"
L9 = LEARNING / "09-ml-inference-deployment"
L10 = LEARNING / "10-foundational-knowledge"
LROOT = LEARNING


def main():
    # ---------------- A. 07-vendor-product-learning ----------------
    new_tree_bundle(
        "jishu/iot/sunlogin",
        "向日葵（Sunlogin）远程控制产品矩阵",
        "贝锐科技向日葵远程控制全线产品中文教程——安全架构、远控硬件（开机盒子/摄像头/鼠标/插座/PDU）、"
        "CLI 与 AI 开发者生态（MCP/Skill/HSK/UI Locator）、离线硬件与跨产品综合洞察。",
        [L7 / "sunlogin" / "sunlogin-bootbox-analysis",
         L7 / "sunlogin" / "sunlogin-offline-hardware-wiki"],
        content_files(L7 / "sunlogin"),
        "07 分类", root_label="concepts")

    new_flat_bundle(
        "jishu/iot/oray",
        "贝锐（Oray）公司与产品生态",
        "贝锐科技（Oray）公司全景与核心产品笔记——远程控制/内网穿透厂商的产品矩阵与商业模式分析。",
        [L7 / "oray" / "oray-comprehensive-analysis-wiki.md",
         L7 / "oray" / "oray-official-website-core-notes.md"],
        "07 分类")

    # tuya 3 篇学习报告 → 合并入既有 tuya-iot
    merge_files_as_subdir(
        "jishu/iot/tuya-iot", "learning-reports",
        [L7 / "tuya" / "tuya-open-learning-report.md",
         L7 / "tuya" / "tuyaopen-dev-skills-learning.md",
         L7 / "tuya" / "tuyaopen-folder-learning-path.md"],
        "TuyaOpen 学习报告", "07 分类",
        "合并 learning 07/tuya 三篇学习报告（TuyaOpen 全面学习报告、dev-skills 学习笔记、目录学习路径），"
        "与既有 concepts 互补；复盘链接已去链接化。")

    new_flat_bundle(
        "jishu/ai/baidu-ocr",
        "百度 Unlimited-OCR 长文档解析",
        "百度 Unlimited-OCR 长文档解析技术中文教程——R-SWA 滑动窗口架构、性能数据、快速上手、"
        "局限与风险、可迁移模式及对多智能体系统的启示。",
        [L7 / "baidu" / "baidu-ocr-wiki"], "07 分类")

    new_flat_bundle(
        "jishu/ai/deepseek-pricing",
        "DeepSeek-V4 免费方案与 API 定价",
        "DeepSeek-V4 免费方案与 API 定价中文 Wiki——网页/App 免费、API 赠送额度、峰谷定价、"
        "自托管、第三方路径、免费 vs 付费选型与 FAQ（与 jishu/ai/deepseek 基础设施技术束互补区分）。",
        [L7 / "deepseek"], "07 分类")

    new_flat_bundle(
        "jishu/ai/volcengine",
        "火山引擎（Volcengine）AI 产品生态",
        "火山引擎 AI 产品生态中文笔记——Ark 大模型平台、ArkCLI、Computer-Use/Mobile-Use Agent、"
        "Viking AI 搜索推荐、机器学习平台、云手机、EIP 与奖励计划等产品分析。",
        [L7 / "volcengine"], "07 分类")

    new_tree_bundle(
        "jishu/ai/miaowu",
        "秒悟（Miaowu/Meoo）AI 平台",
        "秒悟（Meoo）AI 应用平台中文教程——大使入驻指南与实训案例（7 实操场景 + 5 步应用搭建法）。",
        [L7 / "miaowu" / "miaowu-ambassador-guide",
         L7 / "miaowu" / "miaowu-meoo-practice-cases"],
        [], "07 分类")

    new_tree_bundle(
        "sheke/workplace/okr",
        "OKR 目标与关键成果方法论",
        "OKR（Objectives and Key Results）方法论中文知识库——核心概念、制定方法（自上而下/自下而上/共创）、"
        "实施指南、评分复盘、模板案例、工具使用与附录术语表。",
        [L7 / "okr-wiki" / "concepts", L7 / "okr-wiki" / "methods",
         L7 / "okr-wiki" / "implementation", L7 / "okr-wiki" / "scoring",
         L7 / "okr-wiki" / "templates", L7 / "okr-wiki" / "tools",
         L7 / "okr-wiki" / "appendix"],
        [L7 / "okr-wiki" / "00-overview.md", L7 / "okr-wiki" / "okr-guide.md"],
        "07 分类", root_files_at_bundle_root=True)

    merge_tree_into_bundle(
        "jishu/ai/ai-agent/openai-codex", "product-analysis",
        L7 / "openai" / "chatgpt-codex-wiki",
        "ChatGPT Codex 产品分析", "07 分类",
        "合并 learning 07/openai/chatgpt-codex-wiki（产品定位/界面设计/用户体验/多平台/定价/洞察等 16 章 + "
        "原始内容采集），与既有源码架构束互补；舍弃空 page.html 与导航文件。")

    REPORT.append("SKIP 07/google-cloud/knowledge-catalog（任务指示：由另一代理合并入 meta/okf-spec）")
    REPORT.append("SKIP 07/comparison（台账 §9：执行期可判低价值舍弃；厂商对比 2 篇未迁）")

    # ---------------- B. 08-systems-infrastructure ----------------
    wsl_files = content_files(L8 / "wsl-wiki") + [
        L8 / "wsl-cli-and-architecture-wiki.md", L8 / "wsl-learning-plan.md"]
    new_flat_bundle(
        "jishu/systems/wsl",
        "WSL（Windows Subsystem for Linux）",
        "WSL 中文教程——安装、快速上手、CLI 参考、架构、文件系统互操作、WSLc API、"
        "网络与 systemd、调试开发环境、最佳实践与术语，含 CLI 架构解析与学习计划。",
        wsl_files, "08 分类")

    new_flat_bundle(
        "jishu/systems/powershell-hell",
        "AI 与 PowerShell 5 困境（PS5 Hell）",
        "AI 智能体在 Windows PowerShell 5.1 环境的失败模式与防御中文教程——PS5/PS7 差异、"
        "AI 失败案例、第一性原理分析、地狱维度、防御模式、提示词模板、检查清单与反模式。",
        [L8 / "ai-powershell5-hell-wiki"], "08 分类")

    new_flat_bundle(
        "jishu/systems/git-advanced",
        "Git 进阶",
        "Git 进阶中文教程——git clone 高级用法等进阶主题。",
        [L8 / "git-advanced-wiki"], "08 分类")

    new_flat_bundle(
        "jishu/systems/git-baidu-sync",
        "Git + 百度网盘同步",
        "用 Git 裸仓库 + 百度网盘实现跨设备仓库同步的中文教程——目录结构、跨平台配置、"
        "锁机制、日常同步工作流、冲突检测、健康检查、性能优化、备份恢复与反模式。",
        [L8 / "git-baidu-sync"], "08 分类")

    systems = BUNDLES / "jishu" / "systems"
    write_doc(systems / "index.md", "\n".join([
        "---", 'okf_version: "0.2"', "type: group",
        'title: "🖥️ 系统与基础设施"',
        'description: "操作系统与基础设施知识包——WSL、PowerShell 困境防御、Git 进阶与网盘同步等 Windows/Linux 系统层主题"',
        "---", "",
        "# 🖥️ 系统与基础设施", "",
        "本组收录操作系统与基础设施相关的知识包：WSL 子系统、PowerShell 5 困境防御、Git 进阶用法与网盘同步方案。", "",
        "## 知识包列表", "",
        "| 知识包 | 定位 | 说明 |",
        "|--------|------|------|",
        "| [wsl/](wsl/index.md) | WSL 中文教程 | 安装/CLI/架构/文件系统互操作/WSLc API/网络与 systemd/调试与最佳实践 |",
        "| [powershell-hell/](powershell-hell/index.md) | PowerShell 5 困境防御 | AI 智能体在 PS5.1 环境的失败模式、防御模式与检查清单 |",
        "| [git-advanced/](git-advanced/index.md) | Git 进阶 | git clone 高级用法等进阶主题 |",
        "| [git-baidu-sync/](git-baidu-sync/index.md) | Git + 网盘同步 | Git 裸仓库 + 百度网盘跨设备同步工作流 |", "",
        "```{toctree}", ":hidden:", ":maxdepth: 7", "",
        "wsl/index", "powershell-hell/index", "git-advanced/index", "git-baidu-sync/index",
        "```", ""]))
    REPORT.append("NEW GROUP jishu/systems (index.md + 4 bundles)")

    merge_tree_into_bundle(
        "jishu/dev/github", "github-cli",
        L8 / "github-cli-wiki",
        "GitHub CLI（gh）", "08 分类",
        "合并 learning 08/github-cli-wiki（gh 安装/基础命令/PR 工作流/Actions/高级用法/FAQ/速查 8 章）；"
        "舍弃源侧 log.md 与 retrospective.md（隐私元数据）。")

    merge_tree_into_bundle(
        "jishu/ai/ai-agent/intelligent-terminal", "wiki",
        L8 / "intelligent-terminal-wiki",
        "Intelligent Terminal Wiki（章节版）", "08 分类",
        "合并 learning 08/intelligent-terminal-wiki（13 章：总览/架构/WTA master/helper TUI/C++ 集成/协议/"
        "wtcli/agent hooks/autofix/构建系统/日志调试/配置/设计模式），与既有 concepts 互补。")

    merge_tree_into_bundle(
        "jishu/build/conda/conda", "dev-source",
        L8 / "conda-dev-source-wiki",
        "Conda 源码研读", "08 分类",
        "合并 learning 08/conda-dev-source-wiki（conda 源码架构/核心模块/CLI 命令/网关插件/关键 API/"
        "典型场景/FAQ/最佳实践 10 章）。")
    merge_tree_into_bundle(
        "jishu/build/conda/conda", "dev-github",
        L8 / "conda-dev-github-wiki",
        "Conda .github 元仓库", "08 分类",
        "合并 learning 08/conda-dev-github-wiki（conda 组织 .github 元仓库：仓库结构/工作流/Issue 模板/"
        "社区文件/基础设施同步模型/Issue 分拣/运维指南 10 章）。")

    new_flat_bundle(
        "jishu/ml/caffe",
        "Caffe 架构分析",
        "Caffe 深度学习框架架构分析中文教程——include/src 依赖分析、proto2/proto3 序列化、"
        "pycaffe 独立构建复盘、TVM FFI 现代化、八大反模式防御模板与 slim 架构零侵入兼容方案。",
        [L8 / "caffe-architecture-wiki"], "08 分类")

    merge_tree_into_bundle(
        "jishu/python/cpython", "devguide",
        L8 / "cpython-devguide-wiki",
        "CPython 开发者指南", "08 分类",
        "合并 learning 08/cpython-devguide-wiki（贡献者快速上手/开发工作流/治理与社区/"
        "最佳实践与反模式/FAQ 资源 6 章）。")

    # ---------------- C. 09 ----------------
    merge_tree_into_bundle(
        "jishu/ml/onnx/onnx", "wiki",
        L9 / "onnx-wiki",
        "ONNX 实用教程", "09 分类",
        "合并 learning 09/onnx-wiki（总览/核心概念/Python API 实战/快速上手/最佳实践与反模式/FAQ 资源 6 章），"
        "与既有源码级 concepts 互补（教程视角 vs 源码视角）。")

    # ---------------- D. 10 ----------------
    new_flat_bundle(
        "kexue/math/pythagorean-theorem",
        "勾股定理（Pythagorean Theorem）",
        "勾股定理中文教程——概述、历史、证明方法、勾股数、推广、应用、文化意义、FAQ 与资源。",
        [L10 / "mathematical-foundations" / "pythagorean-theorem-wiki"],
        "10 分类")

    new_flat_bundle(
        "sheke/workplace/thesis-writing",
        "论文写作与学术技能",
        "论文写作全流程中文教程——全流程时间线、选题开题、文献综述、研究方法、论文结构、格式规范、"
        "修改润色、答辩准备、常见误区、资源工具与社会语言学视频资源。",
        [L10 / "academic-skills" / "thesis-writing-wiki"], "10 分类")

    # python314-cpython：04/ 无此目录（实测确认），唯一源为 10/；去重 learning-path.md
    py314 = L10 / "python314-cpython-wiki"
    merge_tree_into_bundle(
        "jishu/python/cpython", "python314",
        py314,
        "Python 3.14 新特性与 CPython", "10 分类",
        "合并 learning 10/python314-cpython-wiki（语言特性/自由线程/JIT/新模块/标准库改进/源码架构/"
        "C API/构建平台/迁移指南/实战示例/FAQ/官方文档路线图 + 学习路径）；"
        "去重 learning-path.md（保留更完整的 python314-learning-path.md）；"
        "舍弃 seven-concepts-report.md 与 log.md；cheatsheet.html 随迁。"
        "（任务所述 04 源实测不存在，04 仅有 python314-stdlib-wiki，属另一批次）")
    dup = BUNDLES / "jishu/python/cpython/python314/learning-path.md"
    if dup.exists():
        dup.unlink()
        STATS["skipped"] += 1
        REPORT.append("DEDUP jishu/python/cpython/python314/learning-path.md（与 python314-learning-path.md 重复，保留后者）")
    ch = py314 / "python314-cheatsheet.html"
    if ch.exists():
        shutil.copyfile(ch, BUNDLES / "jishu/python/cpython/python314/python314-cheatsheet.html")
        REPORT.append("COPY python314-cheatsheet.html -> jishu/python/cpython/python314/")
    p314_dir = BUNDLES / "jishu/python/cpython/python314"
    write_doc(p314_dir / "index.md", gen_subdir_index(
        "Python 3.14 新特性与 CPython", content_files(p314_dir), [],
        "附速查卡片：[python314-cheatsheet.html](python314-cheatsheet.html)"))

    # ---------------- E. learning 根级散文件 ----------------
    new_flat_bundle(
        "jishu/ai/docx-report-skill",
        "模板驱动报告生成 Skill 设计",
        "模板驱动报告生成（docx-template-report）Skill 设计方案——从 Word 模板 + 结构化数据"
        "确定性生成统一格式 .docx 报告的技能设计（单一职责、互斥关系、运行环境 py314）。",
        [LROOT / "docx-template-report-skill-design.md"],
        "learning 根级")
    REPORT.append("SKIP learning 根级导航：CATEGORIES.md/index.md/LEARNING-PATHS.md/README.md（舍弃-导航元数据）")

    # ---------------- 汇总 ----------------
    print("=" * 60)
    for r in REPORT:
        print(r)
    print("=" * 60)
    print(f"files_written={STATS['files']} new_bundles={STATS['bundles_new']} "
          f"merge_ops={STATS['bundles_merged']} skipped_dedup={STATS['skipped']}")


if __name__ == "__main__":
    main()
