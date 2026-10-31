#!/usr/bin/env python3
"""OKF bundle -> 带双层目录 PDF 导出（方案A 主路径）。

七步链路：
1. 递归枚举 bundle 内 *.md，剔除嵌套 index.md（保留根 index.md 作前言）
2. 相对链接降级为纯文本（保留可读标题，http(s) 链接保持）
3. 注入标题锚点：h1 -> {#doc-<slug>}，h2 -> {#doc-<slug>-hN}（跳过代码围栏）
4. Pandoc 合并 -> HTML，开启 --toc --toc-depth=2（页内目录）
5. 浏览器端渲染 Mermaid（CDN -> SVG），等待所有 .mermaid 含 svg
6. CDP Page.printToPDF(generateDocumentOutline=True) 打印（书签大纲）
7. 程序化验收：页数 / outline 条目 / Annots 计数 / 首页含「目录」

用法:
  python build_bundle_pdf.py <bundle_dir> [-o out.pdf] [--title T] [--dry-run]
                             [--channel auto|msedge|chromium] [--no-mermaid]
                             [--wait-ms 15000] [--css FILE] [--keep-html]

依赖:
  - pandoc（系统 PATH 中可访问）
  - playwright（浏览器二进制可选，缺失时自动降级系统 Edge）
  - pypdf（可选，用于结构验收）
"""

import sys

if sys.version_info < (3, 10):
    sys.exit("本脚本需要 Python 3.10+")

import argparse
import base64
import html as html_lib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

MERMAID_CDN = "https://" + "cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"

DEFAULT_CSS = """
@page { size: A4; margin: 2cm; }
body {
    font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 11pt; line-height: 1.7; color: #1a1a1a; max-width: 100%;
}
h1 { font-size: 20pt; border-bottom: 2px solid #333; padding-bottom: 8px; margin-top: 1.5em; }
h2 { font-size: 16pt; border-bottom: 1px solid #999; padding-bottom: 4px; margin-top: 1.3em; }
h3 { font-size: 13pt; margin-top: 1.1em; }
code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-size: 10pt; }
pre { background: #f5f5f5; padding: 12px; border-radius: 6px; overflow-x: auto; }
pre code { background: none; padding: 0; }
pre.mermaid, .mermaid { background: #fafafa; text-align: center; }
pre.mermaid svg, .mermaid svg { max-width: 100%; height: auto; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; page-break-inside: avoid; }
th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
th { background: #f0f0f0; font-weight: bold; }
blockquote { border-left: 4px solid #ddd; margin: 1em 0; padding: 0.5em 1em; color: #555; }
img { max-width: 100%; }
a { color: #0066cc; text-decoration: none; }
#TOC { page-break-after: always; }
"""

MERMAID_BOOTSTRAP_JS = """
(function() {
    function processBlocks() {
        var mermaidPres = document.querySelectorAll('pre.mermaid');
        mermaidPres.forEach(function(pre) {
            var code = pre.querySelector('code');
            var text = code ? (code.textContent || code.innerText) : (pre.textContent || pre.innerText);
            var div = document.createElement('div');
            div.className = 'mermaid';
            div.textContent = text;
            pre.parentNode.replaceChild(div, pre);
        });
        return document.querySelectorAll('.mermaid');
    }

    function renderWhenReady() {
        var mermaidDivs = processBlocks();
        if (mermaidDivs.length === 0) return;
        if (typeof mermaid === 'undefined') { setTimeout(renderWhenReady, 100); return; }
        mermaid.initialize({
            startOnLoad: false,
            theme: 'base',
            themeVariables: {
                primaryColor: '#ffffff', primaryBorderColor: '#333333',
                lineColor: '#555555', textColor: '#222222', fontSize: '14px'
            },
            flowchart: { curve: 'linear', htmlLabels: true, useMaxWidth: true }
        });
        mermaid.run({ querySelector: '.mermaid' });
    }
    setTimeout(renderWhenReady, 50);
})();
"""


def _log(msg: str) -> None:
    print(f"  {msg}")


def print_pass(msg: str) -> None:
    print(f"[PASS] {msg}")


def print_warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def print_error(msg: str) -> None:
    print(f"[FAIL] {msg}")


# ---------------------------------------------------------------- 第 1 步


def discover_markdown(bundle: Path) -> list[Path]:
    """递归枚举 *.md，剔除嵌套 index.md，保留根 index.md 作前言（置于首篇）。"""
    all_md = sorted(bundle.rglob("*.md"))
    files: list[Path] = []
    root_index = bundle / "index.md"
    if root_index.is_file():
        files.append(root_index)
    for p in all_md:
        if p.name == "index.md":
            continue
        files.append(p)
    return files


# ---------------------------------------------------------------- 第 2 步


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def demote_links(text: str) -> str:
    """相对链接降级为纯文本（保留可读标题）；http(s)/mailto 保持。"""

    def _link(m: re.Match) -> str:
        label, target = m.group(1), m.group(2)
        if target.lower().startswith(("http://", "https://", "mailto:", "#")):
            return m.group(0)
        return label

    def _image(m: re.Match) -> str:
        alt, target = m.group(1), m.group(2)
        if target.lower().startswith(("http://", "https://", "data:")):
            return m.group(0)
        return alt

    text = re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", _link, text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _image, text)
    return text


# ---------------------------------------------------------------- 第 3 步


def inject_heading_ids(text: str, slug: str) -> str:
    """为 h1/h2 注入稳定锚点；跳过代码围栏内的 #。"""
    out: list[str] = []
    fence: str | None = None
    h2n = 0
    for line in text.split("\n"):
        stripped = line.lstrip()
        if fence is None:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fence = "```" if stripped.startswith("```") else "~~~"
                out.append(line)
                continue
            m = re.match(r"^(#{1,2})\s+(.*?)\s*$", line)
            if m:
                hashes, title = m.group(1), m.group(2)
                title = re.sub(r"\s*\{#[^}]*\}\s*$", "", title).strip()
                if hashes == "#":
                    anchor = f"{{#doc-{slug}}}"
                else:
                    h2n += 1
                    anchor = f"{{#doc-{slug}-h{h2n}}}"
                out.append(f"{hashes} {title} {anchor}")
                continue
            out.append(line)
        else:
            if stripped.startswith(fence):
                fence = None
            out.append(line)
    return "\n".join(out)


def _slugify(rel: str) -> str:
    return re.sub(r"[^0-9a-zA-Z]+", "-", rel).strip("-").lower()


def build_merged_markdown(bundle: Path, files: list[Path]) -> str:
    chunks: list[str] = []
    for p in files:
        rel = p.relative_to(bundle).as_posix()
        if rel.endswith(".md"):
            rel = rel[:-3]
        slug = _slugify(rel)
        text = strip_frontmatter(p.read_text(encoding="utf-8"))
        text = demote_links(text)
        text = inject_heading_ids(text, slug)
        chunks.append(text.rstrip() + "\n")
    return "\n\n".join(chunks)


# ---------------------------------------------------------------- 第 4 步


def _unescape_mermaid_blocks(html_content: str) -> str:
    return re.sub(
        r'<pre class="mermaid"><code>.*?</code></pre>',
        lambda m: html_lib.unescape(m.group(0)),
        html_content,
        flags=re.DOTALL,
    )


def _inject_assets(html_content: str, css: str) -> str:
    style_tag = f"<style>{css}</style>"
    script_tag = f'<script src="{MERMAID_CDN}"></script><script>{MERMAID_BOOTSTRAP_JS}</script>'
    if "</head>" in html_content:
        html_content = html_content.replace("</head>", f"{style_tag}</head>", 1)
        html_content = html_content.replace("</body>", f"{script_tag}</body>", 1)
    else:
        html_content = (
            f"<!DOCTYPE html><html><head><meta charset='utf-8'>{style_tag}</head>"
            f"<body>{html_content}{script_tag}</body></html>"
        )
    return html_content


def md_to_html(md_text: str, title: str, extra_css: str = "") -> str:
    if shutil.which("pandoc") is None:
        raise RuntimeError("pandoc 未安装或不在 PATH 中：https://pandoc.org/installing.html")
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(md_text)
        tmp = Path(f.name)
    try:
        cmd = [
            "pandoc", str(tmp),
            "-f", "markdown+pipe_tables+fenced_code_blocks+yaml_metadata_block",
            "-t", "html5", "--standalone",
            "--toc", "--toc-depth=2",
            "--syntax-highlighting=none",
            "-M", f"title={title}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if result.returncode != 0:
            raise RuntimeError(f"Pandoc 转换失败: {result.stderr}")
        html_content = result.stdout
    finally:
        tmp.unlink(missing_ok=True)
    html_content = _unescape_mermaid_blocks(html_content)
    return _inject_assets(html_content, DEFAULT_CSS + ("\n" + extra_css if extra_css else ""))


# ---------------------------------------------------------------- 第 5/6 步


def _launch(p, channel: str):
    order = {"auto": [None, "msedge"], "chromium": [None], "msedge": ["msedge"]}[channel]
    last = None
    for ch in order:
        try:
            if ch:
                return p.chromium.launch(headless=True, channel=ch)
            return p.chromium.launch(headless=True)
        except Exception as e:  # noqa: BLE001
            last = e
    raise RuntimeError(f"浏览器启动失败（已尝试 {order}）: {last}")


def html_to_pdf(html_content: str, output_pdf: Path, channel: str = "auto",
                wait_ms: int = 15000, include_mermaid: bool = True) -> str:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError("playwright 未安装。请运行: pip install playwright")

    with tempfile.TemporaryDirectory() as td:
        tmp_html = Path(td) / "document.html"
        tmp_html.write_text(html_content, encoding="utf-8")
        with sync_playwright() as p:
            browser = _launch(p, channel)
            page = browser.new_page()
            page.goto(tmp_html.as_uri(), wait_until="load")
            page.wait_for_timeout(800)
            if include_mermaid:
                try:
                    page.wait_for_function("() => typeof mermaid !== 'undefined'",
                                           timeout=min(wait_ms, 10000))
                    page.wait_for_function(
                        """() => {
                            const divs = document.querySelectorAll('.mermaid');
                            if (divs.length === 0) return true;
                            return Array.from(divs).every(d => d.querySelector('svg'));
                        }""",
                        timeout=wait_ms,
                    )
                    page.wait_for_timeout(500)
                except Exception:  # noqa: BLE001
                    print_warn("Mermaid 渲染超时，继续导出")
            page.emulate_media(media="screen")
            used = "cdp"
            try:
                client = page.context.new_cdp_session(page)
                res = client.send("Page.printToPDF", {
                    "printBackground": True,
                    "preferCSSPageSize": True,
                    "paperWidth": 8.27,
                    "paperHeight": 11.69,
                    "marginTop": 0.7874,
                    "marginBottom": 0.7874,
                    "marginLeft": 0.7874,
                    "marginRight": 0.7874,
                    "generateDocumentOutline": True,
                })
                output_pdf.write_bytes(base64.b64decode(res["data"]))
            except Exception as e:  # noqa: BLE001
                print_warn(f"CDP 打印失败（{e}），回退 page.pdf —— 书签大纲将缺失")
                used = "page.pdf"
                page.pdf(
                    path=str(output_pdf),
                    format="A4",
                    margin={"top": "2cm", "bottom": "2cm", "left": "2cm", "right": "2cm"},
                    print_background=True,
                )
            browser.close()
    return used


# ---------------------------------------------------------------- 第 7 步


def verify_pdf(pdf_path: Path) -> dict:
    info = {"size": pdf_path.stat().st_size, "pages": None, "outline": None,
            "annots": None, "has_toc": None}
    try:
        from pypdf import PdfReader
    except ImportError:
        print_warn("pypdf 未安装，结构验收降级为「文件存在 + 非空」")
        return info
    reader = PdfReader(str(pdf_path))
    info["pages"] = len(reader.pages)
    counter = [0]

    def walk(nodes) -> None:
        for item in nodes:
            if isinstance(item, list):
                walk(item)
            else:
                counter[0] += 1

    try:
        walk(reader.outline)
    except Exception:  # noqa: BLE001
        pass
    info["outline"] = counter[0]
    annots = 0
    for pg in reader.pages:
        try:
            annots += len(pg.get("/Annots") or [])
        except Exception:  # noqa: BLE001
            pass
    info["annots"] = annots
    try:
        info["has_toc"] = "目录" in (reader.pages[0].extract_text() or "")
    except Exception:  # noqa: BLE001
        info["has_toc"] = None
    return info


def print_report(info: dict, used: str) -> None:
    print()
    print("| 指标 | 值 | 判定 |")
    print("|---|---|---|")
    print(f"| 文件大小 | {info['size']} 字节 | {'OK' if info['size'] > 0 else 'FAIL'} |")
    print(f"| 页数 | {info['pages']} | {'OK' if info['pages'] else 'FAIL'} |")
    print(f"| 书签大纲条目 | {info['outline']} | {'OK' if info['outline'] else 'FAIL（缺 /Outlines）'} |")
    print(f"| 链接注释 | {info['annots']} | {'OK' if info['annots'] else 'WARN'} |")
    toc = info["has_toc"]
    print(f"| 首页含「目录」 | {toc} | {'OK' if toc else 'WARN'} |")
    print(f"| 打印通道 | {used} | {'OK' if used == 'cdp' else 'WARN（页内目录仍在，书签缺失）'} |")


# ---------------------------------------------------------------- CLI


def run(bundle: Path, output_pdf: Path, title: str, css_file: str | None,
        channel: str, wait_ms: int, no_mermaid: bool, keep_html: bool,
        dry_run: bool) -> int:
    if not bundle.is_dir():
        print_error(f"bundle 目录不存在: {bundle}")
        return 1

    files = discover_markdown(bundle)
    if not files:
        print_error(f"未在 {bundle} 发现 .md 文件")
        return 1

    merged = build_merged_markdown(bundle, files)
    mermaid_count = len(re.findall(r"^```mermaid", merged, flags=re.MULTILINE))

    _log(f"bundle: {bundle}")
    _log(f"将合并 {len(files)} 个文件（根 index 优先，已剔除嵌套 index.md）")
    for p in files:
        _log(f"  - {p.relative_to(bundle).as_posix()}")
    _log(f"合并后约 {len(merged)} 字符，Mermaid 代码块 {mermaid_count} 个")
    _log(f"输出: {output_pdf}")

    if dry_run:
        print_pass("dry-run 预览完成（未写盘）。确认无误后去掉 --dry-run 正式导出。")
        return 0

    extra_css = ""
    if css_file:
        css_path = Path(css_file)
        if css_path.is_file():
            extra_css = css_path.read_text(encoding="utf-8")
        else:
            print_warn(f"CSS 文件不存在，使用默认样式: {css_file}")

    _log("阶段 1/3: Pandoc 合并转换（--toc --toc-depth=2）...")
    html_content = md_to_html(merged, title, extra_css)

    if keep_html:
        html_out = output_pdf.with_suffix(".html")
        html_out.write_text(html_content, encoding="utf-8")
        _log(f"中间 HTML 已保存: {html_out}")

    has_mermaid = 'class="mermaid"' in html_content
    include_mermaid = has_mermaid and not no_mermaid
    _log(f"阶段 2/3: Mermaid 渲染{'（跳过）' if not include_mermaid else ''} ...")
    _log("阶段 3/3: 打印 HTML -> PDF（CDP generateDocumentOutline）...")

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    used = html_to_pdf(html_content, output_pdf, channel=channel,
                       wait_ms=wait_ms, include_mermaid=include_mermaid)

    info = verify_pdf(output_pdf)
    print_report(info, used)

    if not info["size"] or not info["pages"]:
        print_error("产物验收失败：页数为空或文件为空")
        return 1
    if info["outline"] == 0:
        print_error("产物无书签大纲（PDF_001）：确认走 CDP 路径且 generateDocumentOutline=True")
        return 1
    print_pass(f"PDF 导出并通过结构验收: {output_pdf}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="OKF bundle -> 带双层目录 PDF 导出（Pandoc --toc + CDP generateDocumentOutline）"
    )
    parser.add_argument("bundle", help="bundle 根目录（含根 index.md 与子目录正文）")
    parser.add_argument("-o", "--output", help="输出 PDF 路径（默认 <bundle 名>.pdf）")
    parser.add_argument("--title", help="产物标题（默认 bundle 目录名）")
    parser.add_argument("--dry-run", action="store_true",
                        help="只读预览：打印将合并的文件清单与规模，不写盘")
    parser.add_argument("--channel", choices=["auto", "msedge", "chromium"], default="auto",
                        help="浏览器通道（默认 auto：先 chromium 后 msedge）")
    parser.add_argument("--no-mermaid", action="store_true", help="跳过 Mermaid 渲染")
    parser.add_argument("--wait-ms", type=int, default=15000, help="Mermaid 渲染等待超时(毫秒)")
    parser.add_argument("--css", help="追加自定义 CSS 文件路径")
    parser.add_argument("--keep-html", action="store_true", help="保留中间 HTML 用于调试")
    args = parser.parse_args()

    bundle = Path(args.bundle).resolve()
    output_pdf = Path(args.output).resolve() if args.output else Path.cwd() / f"{bundle.name}.pdf"
    title = args.title or bundle.name

    try:
        return run(bundle, output_pdf, title, args.css, args.channel,
                   args.wait_ms, args.no_mermaid, args.keep_html, args.dry_run)
    except Exception as e:  # noqa: BLE001
        print_error(f"导出失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
