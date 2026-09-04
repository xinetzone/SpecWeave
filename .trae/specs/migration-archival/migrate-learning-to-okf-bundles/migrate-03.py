# -*- coding: utf-8 -*-
"""learning/03-agent-platforms-tools → awesome-okf-xs bundles 迁移脚本（一次性工具）。"""
import re
import shutil
from pathlib import Path

SRC = Path(r"d:\spaces\SpecWeave\docs\knowledge\learning\03-agent-platforms-tools")
SRC08 = Path(r"d:\spaces\SpecWeave\docs\knowledge\learning\08-systems-infrastructure")
SRC02 = Path(r"d:\spaces\SpecWeave\docs\knowledge\learning\02-agent-engineering-methodology")
B = Path(r"d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\bundles")
AI = B / "jishu" / "ai"
AA = AI / "ai-agent"
MIG_DATE = "2026-09-02"
LEARNING_ROOT = "docs/knowledge/learning"

stats = {"new_bundles": [], "merged": [], "files": 0}
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.S)


def read(p): return p.read_text(encoding="utf-8").replace("\r\n", "\n")


def write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    stats["files"] += 1


def split_fm(text):
    m = FM_RE.match(text)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        mm = re.match(r'^(\w[\w-]*):\s*(.*)$', line)
        if mm:
            fm[mm.group(1)] = mm.group(2).strip()
    return fm, text[m.end():]


def get_title(fm, body, fallback):
    t = fm.get("title", "").strip().strip('"').strip("'")
    if t:
        return t
    m = re.search(r"^#\s+(.+)$", body, re.M)
    return m.group(1).strip() if m else fallback


def get_desc(fm, body):
    for k in ("summary", "description"):
        v = fm.get(k, "").strip().strip('"').strip("'")
        if v:
            return v[:200]
    for l in body.splitlines():
        s = l.strip()
        if s and not s.startswith(("#", ">", "|", "```", "-", "*", "<")):
            return s[:200]
    return ""


def fix_quotes(text):
    lines, out, fence = text.splitlines(), [], False
    pat = re.compile(r'(?<=[\u4e00-\u9fff，。；：、（）])"([^"\n]{1,120}?)"(?=[\u4e00-\u9fff，。；：、（）])')
    for l in lines:
        if re.match(r"^\s*(```|~~~)", l):
            fence = not fence
            out.append(l)
            continue
        out.append(l if fence else pat.sub(lambda m: "\u201c" + m.group(1) + "\u201d", l))
    return "\n".join(out)


def clean_body(body):
    out = []
    for line in body.splitlines():
        if "x-toml-ref" in line:
            continue
        if "本文档已原子化" in line or "已完成复盘→洞察→萃取" in line:
            continue
        if re.search(r"token\s*消耗|消耗\s*tokens?\s*[:：]|session\s*ID\s*[:：]", line, re.I):
            continue
        out.append(line)
    text = fix_quotes("\n".join(out))
    return re.sub(r"\n{4,}", "\n\n\n", text).strip() + "\n"


def yq(s): return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def fm_block(title, desc, tags, src_rel):
    lines = ["---", "type: " + yq("Wiki Tutorial"), "title: " + yq(title)]
    if desc:
        lines.append("description: " + yq(desc))
    if tags:
        lines.append("tags: [" + ", ".join(yq(t) for t in tags) + "]")
    lines += ["sources:", "  - id: learning-source",
              "    resource: " + yq(LEARNING_ROOT + "/" + src_rel),
              "    title: " + yq("SpecWeave learning wiki 迁移源"),
              "generated: { by: process:learning-to-okf-migration, at: 2026-09-02 }", "---"]
    return "\n".join(lines) + "\n\n"


def transform(src, dst, src_rel, tags, title_override=None):
    fm, body = split_fm(read(src))
    title = title_override or get_title(fm, body, dst.stem)
    write(dst, fm_block(title, get_desc(fm, body), tags, src_rel) + clean_body(body))
    return title


def rel(p, base=SRC): return str(p.relative_to(base)).replace("\\", "/")


def nav_index(bundle, name, desc, entries, extra=""):
    toc = "\n".join(e[0] for e in entries) + "\nlog"
    nav = "\n".join(f"- [{t}]({d}.md)" for d, t in entries)
    write(bundle / "index.md", f"""---
okf_version: "0.2"
title: {yq(name)}
description: {yq(desc)}
---

# {name}

{desc}

## 内容导航

{nav}
{extra}
```{{toctree}}
:hidden:
:maxdepth: 7

{toc}
```
""")


def log_migration(bundle, detail):
    write(bundle / "log.md", f"# 更新日志\n\n## {MIG_DATE}\n\n**Migration**: 从 SpecWeave {LEARNING_ROOT}/03-agent-platforms-tools 迁入 awesome-okf-xs\n\n{detail}\n")


def merge_log(bundle, detail):
    p = bundle / "log.md"
    entry = f"**Merge**: 从 SpecWeave learning 合并独有内容（03 分类迁移）\n\n{detail}\n"
    if p.exists():
        old = read(p)
        m = re.search(r"^## " + MIG_DATE + r"\s*$", old, re.M)
        if m:
            nxt = re.search(r"^## ", old[m.end():], re.M)
            pos = m.end() + nxt.start() if nxt else len(old)
            write(p, old[:pos].rstrip() + "\n\n" + entry + "\n" + old[pos:])
            return
        m = re.search(r"(^#[^\n]*\n)", old, re.M)
        he = m.end() if m else 0
        write(p, old[:he] + f"\n## {MIG_DATE}\n\n" + entry + "\n" + old[he:])
        return
    write(p, f"# 更新日志\n\n## {MIG_DATE}\n\n{entry}")


def append_toctree(index_md, entries, ensure_log=False):
    text = read(index_md)
    lines = text.splitlines()
    open_i = max((i for i, l in enumerate(lines) if re.match(r"^(`{3,}|:{3,})\s*\{toctree\}", l)), default=None)
    assert open_i is not None, f"no toctree: {index_md}"
    close_i = next(j for j in range(open_i + 1, len(lines)) if re.match(r"^(?:`{3,}|:{3,})\s*$", lines[j]))
    block = lines[open_i + 1:close_i]
    insert_at = close_i
    for k, l in enumerate(block):
        if l.strip() == "log":
            insert_at = open_i + 1 + k
            break
    ne = [e for e in entries if e not in block]
    if ensure_log and not any(l.strip() == "log" for l in block):
        ne.append("log")
    write(index_md, "\n".join(lines[:insert_at] + ne + lines[insert_at:]) + ("\n" if text.endswith("\n") else ""))


def new_bundle(dest, name, desc, sources, tags, log_detail):
    """sources: (src_path, docname, base). 章节入 concepts/。"""
    entries = []
    for src, docname, base in sources:
        t = transform(src, dest / "concepts" / f"{docname}.md", rel(src, base), tags)
        entries.append((f"concepts/{docname}", t))
    entries.sort(key=lambda e: e[0])
    nav_index(dest, name, desc, entries)
    log_migration(dest, log_detail)
    stats["new_bundles"].append(str(dest.relative_to(B)).replace("\\", "/"))


# ============================ C. 新建束 ============================

# eve（ai-agent 下）
eve = SRC / "00-agent-frameworks" / "eve-wiki"
new_bundle(AA / "eve", "Eve 目录即 Agent 框架",
           "Eve（Vercel 出品的 nextjs-for-agents 框架）中文学习教程——目录即 Agent 设计（instructions.md/agent.ts/tools/skills）、生产能力、高级能力、快速上手与选型对比。",
           [(f, f.stem, eve) for f in sorted(eve.glob("*.md")) if re.match(r"^\d{2}-", f.stem)],
           ["eve", "agent-framework", "vercel"], "迁入 eve-wiki 10 章教程（00-overview ~ 09-glossary-resources）。")

# orca（ai-agent 下）
orca = SRC / "00-agent-frameworks" / "orca-wiki"
new_bundle(AA / "orca", "Orca Agent 编排框架",
           "Orca 多 Agent 编排框架中文学习教程——核心架构、CLI 编排、受支持的 Agent 生态、快速上手与价值趋势分析。",
           [(f, f.stem, orca) for f in sorted(orca.glob("*.md")) if re.match(r"^\d{2}-", f.stem)],
           ["orca", "agent-orchestration", "multi-agent"], "迁入 orca-wiki 8 章教程（00-overview ~ 07-faq-glossary）。")

# quantdinger
qd = SRC / "quantdinger"
new_bundle(AI / "quantdinger", "QuantDinger 自托管 AI 量化交易平台",
           "QuantDinger 开源 AI 量化交易平台分析——MCP Agent Gateway、双轨策略开发、全流程闭环、多市场支持与行业趋势洞察（源自微信公众号「极客之家」文章分析）。",
           [(qd / "00-overview.md", "00-overview", qd), (qd / "01-article-content.md", "01-article-content", qd),
            (SRC / "quantdinger-ai-trading-wiki.md", "02-ai-trading-analysis", SRC)],
           ["quantdinger", "quant-trading", "ai-agent", "mcp"],
           "迁入 quantdinger 主题 3 篇；02-seven-concepts-report.md 按隐私规则不迁入。")

# agent-industry-research（含 .html 附件，特殊处理）
air = AI / "agent-industry-research"
air_entries = []
for srcp, dn in [(SRC / "2026-08-25-ai-agent-industry-zhihu-article.md", "00-zhihu-article"),
                 (SRC / "2026-08-25-best-agent-systems-research.md", "01-best-agent-systems"),
                 (SRC / "2026-08-25-global-ai-agent-systems-industry-research.md", "02-global-industry-research")]:
    t = transform(srcp, air / "concepts" / f"{dn}.md", rel(srcp), ["ai-agent", "industry-research"])
    air_entries.append((f"concepts/{dn}", t))
(air / "references" / "html").mkdir(parents=True, exist_ok=True)
shutil.copy2(SRC / "2026-08-25-best-agent-systems-research.html", air / "references" / "html" / "2026-08-25-best-agent-systems-research.html")
shutil.copy2(SRC / "2026-08-25-global-ai-agent-systems-industry-research.html", air / "references" / "html" / "2026-08-25-global-ai-agent-systems-industry-research.html")
write(air / "references" / "index.md", """# 参考与附件

本目录存放研究报告的原始 HTML 附件（非 OKF 概念文档，不参与 toctree）：

- `html/2026-08-25-best-agent-systems-research.html` — 最佳 Agent 系统研究原始页面
- `html/2026-08-25-global-ai-agent-systems-industry-research.html` — 全球 AI Agent 系统产业研究原始页面
""")
air_entries.sort(key=lambda e: e[0])
nav_index(air, "AI Agent 行业研究（2026-08）",
          "2026-08-25 AI Agent 行业研究三篇——知乎行业文章、最佳 Agent 系统研究、全球 AI Agent 系统产业研究（市场规模口径差异、五场战争、头部系统对比）。",
          air_entries + [("references/index", "参考与附件")],
          "\n> 两份 .html 原件存于 references/html/（附件，不入 toctree）。\n")
log_migration(air, "迁入 2026-08-25 三份研究报告 + 2 份 .html 附件（references/html/）。")
stats["new_bundles"].append("jishu/ai/agent-industry-research")

# claude-tag（anthropic 下）
ct = SRC / "00-agent-frameworks" / "claude-tag-article"
ct_sources = [(SRC / "claude-tag-article.md", "00-article-capture", SRC)] + \
             [(f, f.stem, ct) for f in sorted(ct.glob("*.md")) if f.stem not in ("index", "README")]
new_bundle(AI / "anthropic" / "claude-tag", "Claude Tag 企业协作工具",
           "Anthropic 企业协作工具 Claude Tag 知识捕获——量子位文章解析（Claude Code 进化、Ambient Mode 主动介入、异步执行、卡帕西「LLM 第三次变革」论断）与核心概念、关键数据、SpecWeave 关联分析。",
           ct_sources, ["claude-tag", "anthropic", "enterprise-agent", "ambient-mode"],
           "迁入 claude-tag-article 目录 8 章 + 分类根散文件（文章捕获种子），共 9 篇。")

# echobird
eb = SRC / "00-agent-frameworks" / "echobird-wiki"
new_bundle(AI / "echobird", "EchoBird 百灵鸟 AI Agent 桌面管理工具",
           "EchoBird（百灵鸟）AI Agent 桌面管理工具中文学习教程——产品定位、架构、Model Nexus 模型枢纽、本地 LLM、Codex Proxy、工具注册表与快速上手（Tauri + Rust 桌面端，解决 60% 用户卡在安装配置的痛点）。",
           [(SRC / "echobird-wiki.md", "00-article-capture", SRC)] +
           [(f, f.stem, eb) for f in sorted(eb.glob("*.md")) if f.stem not in ("index", "README")],
           ["echobird", "ai-agent", "desktop-tool", "tauri"],
           "迁入 echobird-wiki 目录 12 章 + 分类根散文件（文章捕获种子），共 13 篇。")

# mopmonk
mp = SRC / "02-security" / "mopmonk-security-agent-wiki"
new_bundle(AI / "mopmonk", "MopMonk 安全 Agent",
           "MopMonk 安全 Agent 中文学习教程——核心概念、MiniMax M3 模型、核心技术、学习指南与 FAQ（安全领域的 Agent 实践）。",
           [(SRC / "mopmonk-security-agent-wiki.md", "00-article-capture", SRC)] +
           [(f, f.stem, mp) for f in sorted(mp.glob("*.md")) if f.stem not in ("index", "README")],
           ["mopmonk", "security-agent", "minimax"],
           "迁入 02-security/mopmonk-security-agent-wiki 7 章 + 分类根散文件，共 8 篇。")

# rainman-translate
rt = SRC / "06-content-translation" / "rainman-translate-book-wiki"
new_bundle(AI / "rainman-translate", "Rainman Translate 图书翻译",
           "Rainman Translate 图书翻译工具中文学习教程——核心概念、安装、使用、局限性与 FAQ（内容翻译方向的 Agent 工具）。",
           [(SRC / "rainman-translate-book-wiki.md", "00-article-capture", SRC)] +
           [(f, f.stem, rt) for f in sorted(rt.glob("*.md")) if f.stem not in ("index", "README")],
           ["rainman-translate", "translation", "ai-agent"],
           "迁入 06-content-translation/rainman-translate-book-wiki 8 章 + 分类根散文件，共 9 篇。")

# agent-platform-notes（聚合束）
apn_sources = [(SRC / n, dn) for n, dn in [
    ("anthropic-agent-roadmap-wiki.md", "anthropic-agent-roadmap"),
    ("areal-agent-rl-wiki.md", "areal-agent-rl"),
    ("areal-official-practical-wiki.md", "areal-official-practical"),
    ("atomgit-ai-best-practices.md", "atomgit-ai-best-practices"),
    ("browseract-official-wiki.md", "browseract-official"),
    ("browseract-wiki.md", "browseract"),
    ("minitap-official-wiki.md", "minitap-official"),
    ("octo-platform-wiki.md", "octo-platform")]]
new_bundle(AI / "agent-platform-notes", "Agent 平台散篇笔记",
           "AI Agent 平台与工具散篇笔记聚合束——收录独立篇数不足（<5 篇）的小主题：Anthropic Agent 产品线路线图、AReaL 强化学习框架（2 篇）、AtomGit AI 最佳实践、BrowserAct 浏览器自动化（2 篇）、Minitap 官方 Wiki、明略科技 Octo 多 Agent 协作平台。",
           [(p, dn, SRC) for p, dn in apn_sources], ["ai-agent", "platform-notes", "aggregation"],
           "聚合 8 个散文件小主题（各主题独立篇数 <5，按聚合束策略并入，避免束爆炸）。")

# fable5-cost-optimization
f5 = SRC / "03-code-devtools" / "fable5-cost-optimization-wiki"
new_bundle(AI / "fable5-cost-optimization", "Fable5 成本优化",
           "Fable5 定价与成本优化中文学习教程——定价背景、社区方案、官方优化、选型指南与核心洞察（AI 编程工具成本优化专题）。",
           [(f, f.stem, f5) for f in sorted(f5.glob("*.md")) if f.stem not in ("index", "README")],
           ["fable5", "cost-optimization", "ai-coding"],
           "迁入 fable5-cost-optimization-wiki 9 章（00-overview ~ 07-resources + article-content 原文）。")

# monkeycode-vibe-coding
mc = SRC / "03-code-devtools" / "seven-concepts-monkeycode-vibe-coding-wiki"
new_bundle(AI / "monkeycode-vibe-coding", "MonkeyCode Vibe Coding 七概念分析",
           "MonkeyCode Vibe Coding 七概念方法论分析——七概念框架、深度解析、实践指南、评估与七概念应用（内容主题章节，非工作流报告）。",
           [(f, f.stem, mc) for f in sorted(mc.glob("*.md")) if f.stem not in ("index", "README")],
           ["monkeycode", "vibe-coding", "seven-concepts"],
           "迁入 seven-concepts-monkeycode-vibe-coding-wiki 8 章；属内容主题，随主题迁移。")

# volcengine-agent
vap = SRC / "01-domestic-platforms" / "volcengine-agent-plan-wiki"
vak = SRC / "01-domestic-platforms" / "volcengine-agentkit-wiki"
va_sources = [(f, "plan-" + f.stem, vap) for f in sorted(vap.glob("*.md")) if f.stem not in ("index", "README")]
va_sources += [(f, "kit-" + f.stem, vak) for f in sorted(vak.glob("*.md")) if f.stem not in ("index", "README", "MAINTENANCE")]
new_bundle(AI / "volcengine-agent", "火山引擎 Agent 生态（AgentKit + 共建计划）",
           "火山引擎 Agent 生态中文学习教程——AgentKit 产品与架构（VEADK 框架、SDK/CLI、应用场景、对比生态）与 Agent 共建计划（贡献方向、参与指南、奖励认可、跨模态范式），共 20 章。产品与定价信息以 2026-07 快照为准，使用前需时效核验。",
           va_sources, ["volcengine", "agentkit", "veadk", "domestic-platform"],
           "迁入 volcengine-agent-plan-wiki 9 章（plan-*）+ volcengine-agentkit-wiki 11 章（kit-*）；MAINTENANCE 维护手册属工作流元数据不迁入。")

# open-code-review（三源整合）
ocr = AI / "open-code-review"
ocr_flat = SRC / "03-code-devtools" / "open-code-review-wiki"
ocr_struct = SRC / "open-code-review-wiki"


def ocr_base(p):
    return ocr_flat if p.is_relative_to(ocr_flat) else (ocr_struct if p.is_relative_to(ocr_struct) else SRC)


ocr_concepts = [(ocr_flat / "01-core-concepts.md", "00-core-concepts"),
                (ocr_struct / "concepts" / "03-architecture.md", "01-architecture"),
                (ocr_struct / "concepts" / "04-llm-providers.md", "02-llm-providers"),
                (ocr_struct / "concepts" / "05-tools-mcp.md", "03-tools-mcp"),
                (ocr_struct / "concepts" / "06-review-rules.md", "04-review-rules"),
                (ocr_struct / "concepts" / "07-session-telemetry.md", "05-session-telemetry"),
                (ocr_struct / "concepts" / "08-integrations.md", "06-integrations"),
                (ocr_flat / "04-optimizations.md", "07-optimizations"),
                (ocr_flat / "06-effectiveness.md", "08-effectiveness"),
                (ocr_flat / "07-limitations.md", "09-limitations"),
                (ocr_flat / "02-installation.md", "10-installation"),
                (ocr_flat / "03-usage.md", "11-usage")]
ocr_refs = [(ocr_struct / "references" / "02-cli-reference.md", "cli-reference"),
            (ocr_flat / "12-llm-providers.md", "llm-providers-detail"),
            (ocr_struct / "references" / "09-faq-troubleshooting.md", "faq-troubleshooting"),
            (ocr_flat / "10-resources.md", "resources"),
            (SRC / "open-code-review-wiki.md", "wechat-article-source")]
entries = []
for srcp, dn in ocr_concepts:
    t = transform(srcp, ocr / "concepts" / f"{dn}.md", rel(srcp, ocr_base(srcp)), ["open-code-review", "ai-code-review", "alibaba"])
    entries.append((f"concepts/{dn}", t))
for srcp, dn in ocr_refs:
    t = transform(srcp, ocr / "references" / f"{dn}.md", rel(srcp, ocr_base(srcp)), ["open-code-review", "ai-code-review", "alibaba"])
    entries.append((f"references/{dn}", t))
entries.sort(key=lambda e: e[0])
nav_index(ocr, "Open Code Review 阿里 AI 代码评审 CLI",
          "阿里巴巴开源 AI 代码评审 CLI 工具 Open Code Review 中文教程——确定性工程 × Agent 混合驱动架构、六阶段审查流水线、LLM Provider 配置、MCP 工具、评审规则、会话遥测、Claude Code/CI 集成、效果评估与局限性（三源整合去重）。",
          entries, "\n> 三源整合说明：重复章节（安装、使用流程、FAQ、总结、工具/规则/遥测平铺版）已去重，保留信息量最大的版本。\n")
log_migration(ocr, "三源整合新建：03-code-devtools/open-code-review-wiki（19 章）、根级 open-code-review-wiki（14 章结构化）、分类根散文件（微信文章教程）。去重后保留 12 概念 + 5 参考；各源 log/README/index 属元数据不迁入。")
stats["new_bundles"].append("jishu/ai/open-code-review")

# trae release notes：直接并入既有 jishu/ai/trae 束（单文件，不建子束）
transform(SRC / "trae-v3-3-74-release-notes.md", AI / "trae" / "trae-v3-3-74-release-notes.md",
          rel(SRC / "trae-v3-3-74-release-notes.md"), ["trae", "release-notes"],
          title_override="TRAE v3.3.74 版本发布笔记")
append_toctree(AI / "trae" / "index.md", ["trae-v3-3-74-release-notes"])
merge_log(AI / "trae", "新增 trae-v3-3-74-release-notes.md（2026-07-08 版本发布笔记：浏览器配置、Windows SDK/MSSDK 支持、Bug 修复；时效性内容，仅作版本历史记录）。")
stats["merged"].append("jishu/ai/trae")

print("Phase 1 新建束:", len(stats["new_bundles"]))
for b in stats["new_bundles"]:
    print("  +", b)

# ============================ B/D. 合并 ============================

# --- book-to-skill（A5）---
bts_src = SRC02 / "02-prompt-coding" / "book-to-skill-wiki"
bts = AA / "book-to-skill"
bts_map = {"01-core-architecture.md": "core-architecture",
           "02-extractor-deep-dive.md": "extractor-deep-dive",
           "03-skill-md-spec.md": "skill-md-generation-spec",
           "04-token-economics.md": "token-economics",
           "05-security-model.md": "security-model",
           "06-installation-usage.md": "installation-and-usage",
           "07-extending-development.md": "extending-development",
           "08-transferable-patterns.md": "transferable-patterns",
           "09-summary-faq.md": "summary-and-faq"}
for fn, dn in bts_map.items():
    transform(bts_src / fn, bts / "concepts" / f"{dn}.md", rel(bts_src / fn, SRC02), ["book-to-skill", "skill-compiler"])
append_toctree(bts / "index.md", [f"concepts/{dn}" for dn in bts_map.values()], ensure_log=True)
merge_log(bts, "新增 9 篇概念文档（核心架构、提取器深度解析、SKILL.md 生成规范、Token 经济学、安全模型、安装与使用、扩展开发、可复用工程模式、总结与 FAQ），源自 learning 02/02-prompt-coding/book-to-skill-wiki 01~09 章；00-overview 与根索引重叠、02/05 章与既有 multi-format-parsers/security-sanitization 部分重叠但深度更大予以保留、log/README/index 属元数据，均未迁入。")
stats["merged"].append("jishu/ai/ai-agent/book-to-skill")

# --- hermes-agent（A5，三目录整合）---
ha = AA / "hermes-agent"
ha_inst = SRC / "00-agent-frameworks" / "hermes-agent-installation"
ha_integ = SRC / "00-agent-frameworks" / "hermes-agent-integration"
ha_wiki = SRC / "00-agent-frameworks" / "hermes-agent-wiki"
ha_new = []
for f in sorted(ha_inst.glob("*.md")):
    if f.stem in ("index", "README"):
        continue
    dn = "install-" + f.stem
    transform(f, ha / "concepts" / f"{dn}.md", rel(f), ["hermes-agent", "installation"])
    ha_new.append(f"concepts/{dn}")
for f in sorted(ha_integ.glob("*.md")):
    if f.stem in ("index", "README"):
        continue
    dn = "integ-" + f.stem
    transform(f, ha / "concepts" / f"{dn}.md", rel(f), ["hermes-agent", "integration"])
    ha_new.append(f"concepts/{dn}")
for fn, dn in [("02-quickstart.md", "quickstart"), ("04-configuration.md", "configuration"),
               ("07-skills.md", "skills-system"), ("11-glossary-faq-resources.md", "glossary-faq-resources")]:
    transform(ha_wiki / fn, ha / "concepts" / f"{dn}.md", rel(ha_wiki / fn), ["hermes-agent"])
    ha_new.append(f"concepts/{dn}")
append_toctree(ha / "index.md", sorted(ha_new), ensure_log=True)
merge_log(ha, "三目录整合合并：新增安装指南 11 篇（install-01~11：环境/脚本/Windows/手动/Docker/配置/验证/排障/升级卸载/Termux/国内网络）、集成指南 9 篇（integ-00~08：插件接口/能力映射/配置/数据转换/认证权限/示例/排障/AGENTS.md 自动加载）、hermes-agent-wiki 独有 4 篇（quickstart/configuration/skills-system/glossary-faq-resources）；wiki 其余章节（00 概述/01 核心特性/03 CLI/05 网关/06 工具/08 记忆/09 扩展/10 架构）与既有 10 篇概念重叠，未重复迁入。")
stats["merged"].append("jishu/ai/ai-agent/hermes-agent")

# --- zleap-agent（A5）---
za = AA / "zleap-agent"
za_src = SRC / "00-agent-frameworks" / "zleap-agent-wiki"
for fn, dn in [("02-workspace-context.md", "workspace-context"), ("04-skills-tools-permissions.md", "skills-tools-permissions")]:
    transform(za_src / fn, za / "concepts" / f"{dn}.md", rel(za_src / fn), ["zleap-agent"])
transform(za_src / "08-faq-glossary.md", za / "references" / "faq-glossary.md", rel(za_src / "08-faq-glossary.md"), ["zleap-agent"])
append_toctree(za / "index.md", ["concepts/workspace-context", "concepts/skills-tools-permissions", "references/faq-glossary"], ensure_log=True)
merge_log(za, "新增 2 篇概念（Workspace 隔离与上下文组装、Skill 与工具权限）+ 1 篇参考（FAQ 与术语表）；其余章节与既有概念重叠（03 记忆→store-persistence、05 模型→ai-abstraction、06 网关任务→gateway-server/tasks-scheduling、00/01/07 概述/架构/快速上手），未重复迁入。")
stats["merged"].append("jishu/ai/ai-agent/zleap-agent")

# --- cordis（A5）---
cd = AA / "cordis"
cd_src = SRC / "cordis-spatiotemporal-composability-wiki"
for fn, dn in [("concepts\\02-repo-structure.md", "repo-structure"), ("concepts\\04-effects-coeffects.md", "effects-coeffects"),
               ("concepts\\07-loader-config.md", "loader-config"), ("concepts\\08-hmr.md", "hmr")]:
    transform(cd_src / fn, cd / "concepts" / f"{dn}.md", rel(cd_src / fn), ["cordis", "spatiotemporal-composability"])
for fn, dn in [("references\\01-background-paper.md", "background-paper"), ("references\\09-aux-packages.md", "aux-packages"),
               ("references\\11-faq-notes.md", "faq-notes")]:
    transform(cd_src / fn, cd / "references" / f"{dn}.md", rel(cd_src / fn), ["cordis"])
append_toctree(cd / "index.md", ["concepts/repo-structure", "concepts/effects-coeffects", "concepts/loader-config", "concepts/hmr",
                                 "references/background-paper", "references/aux-packages", "references/faq-notes"], ensure_log=True)
merge_log(cd, "新增 4 篇概念（Monorepo 文件结构、效应与协同效应机制、声明式加载与配置合并、热更新 HMR）+ 3 篇参考（背景理论与论文、辅助包、FAQ 与注意事项）；采用源侧 concepts/references 子目录版本（根级平铺章节为其重复件）；03/05/06 章与既有核心抽象/插件系统/Fiber 生命周期重叠，10/12 章示例与总结和既有 examples 及索引重叠，seven-concepts-report（2 处）按隐私规则不迁入。")
stats["merged"].append("jishu/ai/ai-agent/cordis")

# --- i-have-adhd（A5）---
ad = AA / "i-have-adhd"
ad_src = SRC / "03-code-devtools" / "i-have-adhd-wiki"
ad_map = {"01-design-philosophy.md": "design-philosophy", "03-exceptions-and-checklist.md": "exceptions-and-checklist",
          "06-evaluation-framework.md": "evaluation-framework", "07-customization-and-troubleshooting.md": "customization-and-troubleshooting",
          "08-patterns-extracted.md": "reusable-patterns", "10-action-first-paradigm.md": "action-first-paradigm",
          "11-reverse-adaptation-innovation.md": "reverse-adaptation-innovation", "12-design-tradeoffs-and-writing.md": "design-tradeoffs-and-writing"}
for fn, dn in ad_map.items():
    transform(ad_src / fn, ad / "concepts" / f"{dn}.md", rel(ad_src / fn), ["i-have-adhd", "agent-skill"])
transform(ad_src / "09-faq-and-resources.md", ad / "references" / "faq-and-resources.md", rel(ad_src / "09-faq-and-resources.md"), ["i-have-adhd"])
append_toctree(ad / "index.md", [f"concepts/{dn}" for dn in ad_map.values()] + ["references/faq-and-resources"], ensure_log=True)
merge_log(ad, "新增 8 篇概念（设计理念、例外场景与自检清单、评估框架、自定义与故障排查、可复用模式萃取、行动优先输出范式、逆向适配创新方法论、设计取舍与技术写作借鉴）+ 1 篇参考（FAQ 与资源汇总）；02 核心规则与既有 ten-output-rules、04 安装与既有 install-adhd-skill、05 持久化与既有 session-hooks-mechanism 重叠，00 概述与根索引重叠，均未重复迁入。")
stats["merged"].append("jishu/ai/ai-agent/i-have-adhd")

# --- anthropic/financial-services（A5）---
fs = AI / "anthropic" / "financial-services"
transform(SRC / "anthropic-financial-services-wiki.md", fs / "references" / "wechat-article-analysis.md",
          rel(SRC / "anthropic-financial-services-wiki.md"), ["anthropic", "financial-services"],
          title_override="Anthropic Financial Services 微信文章解析（华尔街的 AI 金融 Agent 工具箱）")
append_toctree(fs / "references" / "index.md", ["wechat-article-analysis"])
merge_log(fs, "新增 1 篇参考文档（微信公众号「极客之家」文章解析：四层架构视角、竞争格局与落地观察），与既有 4 概念 + 1 参考（官方仓库视角）互补。")
stats["merged"].append("jishu/ai/anthropic/financial-services")

# --- agency-agents（重复对 #6 散文件）---
aa = AA / "agency-agents"
transform(SRC / "the-agency-project-wiki.md", aa / "concepts" / "the-agency-project-guide.md",
          rel(SRC / "the-agency-project-wiki.md"), ["agency-agents", "the-agency"],
          title_override="The Agency 项目完整学习教程（一人组建一支 Agent 军团）")
append_toctree(aa / "index.md", ["concepts/the-agency-project-guide"])
merge_log(aa, "新增 1 篇概念文档（The Agency 项目完整学习教程，源自微信公众号文章 + GitHub 源码分析视角），补全重复对 #6 散文件，与既有 persona/NEXUS/集成适配器概念互补。")
stats["merged"].append("jishu/ai/ai-agent/agency-agents")

# --- langgraph（散文件并入既有束）---
lg = AI / "langchain-ai" / "langgraph"
transform(SRC / "langgraph-implementation-roadmap.md", lg / "references" / "implementation-roadmap.md",
          rel(SRC / "langgraph-implementation-roadmap.md"), ["langgraph", "production", "roadmap"],
          title_override="LangGraph 生产级落地实施路线图")
append_toctree(lg / "references" / "index.md", ["implementation-roadmap"])
merge_log(lg, "新增 1 篇参考文档（LangGraph 生产级落地实施路线图：12-16 周四阶段、Demo-Prod 六层能力模型对齐）。")
stats["merged"].append("jishu/ai/langchain-ai/langgraph")

# --- intelligent-terminal（A3 改判合并，源在 08 分类）---
it = AA / "intelligent-terminal"
it_src = SRC08 / "intelligent-terminal-wiki"
it_map = {"03-wta-master.md": "wta-master", "04-wta-helper-tui.md": "wta-helper-tui", "05-cpp-integration.md": "cpp-integration",
          "10-build-system.md": "build-system", "11-logging-debugging.md": "logging-debugging", "13-design-patterns.md": "design-patterns"}
for fn, dn in it_map.items():
    transform(it_src / fn, it / "concepts" / f"{dn}.md", rel(it_src / fn, SRC08), ["intelligent-terminal", "windows-terminal"])
append_toctree(it / "index.md", [f"concepts/{dn}" for dn in it_map.values()], ensure_log=True)
merge_log(it, "新增 6 篇概念（wta-master 主进程、wta-helper TUI、C++ 集成、构建系统、日志与调试、设计模式），源自 learning 08-systems-infrastructure/intelligent-terminal-wiki；其余章节与既有概念重叠（02 架构→dual-process-architecture、06 协议→acp-json-rpc-protocol、07 wtcli→wtcli-command-tool、08 hooks→hooks-auto-upgrade、09 autofix→osc133-autofix、12 配置→settings-configuration），未重复迁入。")
stats["merged"].append("jishu/ai/ai-agent/intelligent-terminal")

# --- okf-kit → meta/okf-ecosystem（既有束已覆盖 okf-kit 0.3.3，改判合并）---
ok = B / "meta" / "okf-ecosystem"
ok_src = SRC / "okf-kit-wiki"
ok_concepts = [("concepts\\01-installation.md", "06-installation"), ("concepts\\08-registry-visualize.md", "07-registry-visualize"),
               ("concepts\\09-extension-development.md", "08-extension-development"), ("concepts\\03-okf-format.md", "09-okf-format")]
ok_refs = [("references\\02-cli-reference.md", "cli-reference"), ("references\\10-faq-troubleshooting.md", "faq-troubleshooting")]
for fn, dn in ok_concepts:
    transform(ok_src / fn, ok / "concepts" / f"{dn}.md", rel(ok_src / fn), ["okf-kit", "okf"])
    append_toctree(ok / "concepts" / "index.md", [dn])
for fn, dn in ok_refs:
    transform(ok_src / fn, ok / "references" / f"{dn}.md", rel(ok_src / fn), ["okf-kit", "okf"])
    append_toctree(ok / "references" / "index.md", [dn])
merge_log(ok, "合并 learning 03/okf-kit-wiki 独有内容：新增 4 篇概念（安装与配置、Registry 与可视化、扩展开发、OKF 格式章节）+ 2 篇参考（CLI 参考、FAQ 与故障排查）。台账原拟新建 meta/okf-spec/okf-kit，执行期确认本束已完整覆盖 okf-kit 0.3.3 核心（数据模型/爬取流水线/增量同步/三模服务），按 A3 先例改判合并回填，不建影子束；04/05/06/07 章与既有概念重叠、00/11 为概述总结、seven-concepts-report（2 处）按隐私规则不迁入。")
stats["merged"].append("meta/okf-ecosystem")

# --- mobile-use（05-mobile-testing 88 文件 + 2 散文件并入 chaos 直迁束）---
mu = AI / "mobile-use"
mu_src = SRC / "05-mobile-testing" / "minitest-mobile-use-wiki"


def mu_section(dst_sub, src_rel_dir, prefix_tags):
    """迁移一个章节子目录（丢弃源侧 index/README），返回 docname 列表。"""
    names = []
    for f in sorted((mu_src / src_rel_dir).glob("*.md")):
        if f.stem in ("index", "README"):
            continue
        dn = f.stem
        transform(f, mu / dst_sub / Path(src_rel_dir).name / f"{dn}.md", rel(f), prefix_tags)
        names.append(f"{Path(src_rel_dir).name}/{dn}")
    return names


mt_tags = ["minitest", "mobile-testing", "ai-qa"]
sdk_tags = ["mobile-use", "minitap", "sdk"]
mt_names = []
for sec in ["01-getting-started", "02-suite-management", "03-running-tests", "04-triage-and-integrations", "05-reference"]:
    mt_names += mu_section("minitest-docs", f"minitest-docs/{sec}", mt_tags)
for f in ["best-practices.md", "faq.md", "glossary.md", "resources.md"]:
    dn = f[:-3]
    transform(mu_src / f, mu / "minitest-docs" / f"{dn}.md", rel(mu_src / f), mt_tags)
transform(SRC / "minitest-mobile-use-official-docs-wiki.md", mu / "minitest-docs" / "official-wiki.md",
          rel(SRC / "minitest-mobile-use-official-docs-wiki.md"), mt_tags,
          title_override="Minitap.ai 官方 Wiki 学习教程（minitest 深度解析）")
mt_entries = sorted(mt_names + [f[:-3] for f in ["best-practices.md", "faq.md", "glossary.md", "resources.md"]] + ["official-wiki"])
toc = "\n".join(mt_entries)
write(mu / "minitest-docs" / "index.md", f"""# minitest 官方文档与产品指南

minitest（Minitap 出品的完全自主 AI QA 工程师）官方文档迁移存档——入门、套件管理、运行测试、分诊与集成、参考五大板块，另含最佳实践、FAQ、术语表、资源与官方 Wiki 学习教程。

```{{toctree}}
:maxdepth: 2

{toc}
```
""")

sdk_names = []
for sec in ["01-introduction-installation", "02-quickstarts", "03-core-concepts", "04-examples", "05-sdk-reference", "06-troubleshooting"]:
    sdk_names += mu_section("sdk-docs", f"mobile-use-sdk-docs/{sec}", sdk_tags)
sdk_entries = sorted(sdk_names)
toc2 = "\n".join(sdk_entries)
write(mu / "sdk-docs" / "index.md", f"""# mobile-use SDK 官方文档

minitap-mobile-use SDK 官方文档迁移存档——介绍与安装、快速上手（本地/平台/云/BrowserStack/iOS）、核心概念（架构/Agent/Builder/可观测性/Profiles/Tasks）、示例、SDK 参考（Agent/ConfigBuilder/TaskRequestBuilder/类型/异常）、故障排查。

```{{toctree}}
:maxdepth: 2

{toc2}
```
""")

transform(SRC / "mobile-use-deep-learning-analysis.md", mu / "references" / "deep-learning-analysis.md",
          rel(SRC / "mobile-use-deep-learning-analysis.md"), ["mobile-use", "deep-learning", "analysis"],
          title_override="mobile-use 深度学习分析")
append_toctree(mu / "references" / "index.md", ["deep-learning-analysis"])
append_toctree(mu / "index.md", ["minitest-docs/index", "sdk-docs/index"])
merge_log(mu, "并入 05-mobile-testing 全部内容：新增 minitest-docs/（30 篇：官方文档 5 板块 25 篇 + 最佳实践/FAQ/术语表/资源 + 官方 Wiki 学习教程）与 sdk-docs/（31 篇：mobile-use SDK 官方文档 6 板块）两个子目录，新增 references/deep-learning-analysis.md；与既有 7 概念（源码精读视角）互补——官方文档视角，未做内容删减。")
stats["merged"].append("jishu/ai/mobile-use")

print("Phase 2 合并束:", len(stats["merged"]))
for b in stats["merged"]:
    print("  ~", b)
print("写入文件总数:", stats["files"])

# ============================ 组索引注册（非禁改文件）============================
# ai-agent/index.md：注册 eve、orca
append_toctree(AA / "index.md", ["eve/index", "orca/index"])
# anthropic/index.md：注册 claude-tag
append_toctree(AI / "anthropic" / "index.md", ["claude-tag/index"])
print("组索引注册完成: ai-agent(+eve,orca), anthropic(+claude-tag)")
print("禁改共享文件待注册（返回清单）: jishu/ai/index.md += quantdinger, agent-industry-research, echobird, mopmonk, rainman-translate, agent-platform-notes, fable5-cost-optimization, monkeycode-vibe-coding, volcengine-agent, open-code-review")
