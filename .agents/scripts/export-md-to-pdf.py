#!/usr/bin/env python3
"""三段式 Markdown+Mermaid -> PDF 导出工具。

三段式流程：
1. Pandoc: Markdown -> HTML（保留 Mermaid 代码块为 <pre class="mermaid">）
2. Mermaid.js: 浏览器端渲染 Mermaid 图为 SVG
3. Playwright Chromium: 渲染完整 HTML -> 打印为 PDF

用法:
  python export-md-to-pdf.py <input.md> [-o output.pdf] [--css CSS_FILE]
                                        [--no-mermaid] [--wait-ms MILLISECONDS]
                                        [--keep-html]

依赖:
  - pandoc (系统 PATH 中可访问)
  - playwright (pip install playwright && playwright install chromium)
  - 网络连接（Mermaid.js CDN）
"""

import argparse
import html as html_lib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import print_pass, print_error, print_warn

MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"

DEFAULT_CSS = """
@page { size: A4; margin: 2cm; }
body {
    font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
    font-size: 11pt; line-height: 1.7; color: #1a1a1a;
    max-width: 100%;
}
h1 { font-size: 20pt; border-bottom: 2px solid #333; padding-bottom: 8px; margin-top: 1.5em; }
h2 { font-size: 16pt; border-bottom: 1px solid #999; padding-bottom: 4px; margin-top: 1.3em; }
h3 { font-size: 13pt; margin-top: 1.1em; }
h4 { font-size: 11pt; }
code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-size: 10pt; }
pre { background: #f5f5f5; padding: 12px; border-radius: 6px; overflow-x: auto; }
pre code { background: none; padding: 0; }
pre.mermaid { background: #fafafa; text-align: center; }
pre.mermaid svg { max-width: 100%; height: auto; }
.mermaid { text-align: center; }
.mermaid svg { max-width: 100%; height: auto; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
th { background: #f0f0f0; font-weight: bold; }
blockquote { border-left: 4px solid #ddd; margin: 1em 0; padding: 0.5em 1em; color: #555; }
img { max-width: 100%; }
a { color: #0066cc; text-decoration: none; }
"""

MERMAID_BOOTSTRAP_JS = """
document.addEventListener('DOMContentLoaded', function() {
    var mermaidBlocks = document.querySelectorAll('pre.mermaid code, pre.mermaid');
    mermaidBlocks.forEach(function(block) {
        var text = block.textContent || block.innerText;
        var div = document.createElement('div');
        div.className = 'mermaid';
        div.textContent = text;
        var parent = block.closest('pre') || block;
        parent.parentNode.replaceChild(div, parent);
    });
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({
            startOnLoad: false,
            theme: 'base',
            themeVariables: {
                primaryColor: '#ffffff',
                primaryBorderColor: '#333333',
                lineColor: '#555555',
                textColor: '#222222',
                fontSize: '14px'
            },
            flowchart: { curve: 'linear', htmlLabels: true, useMaxWidth: true }
        });
        mermaid.run({ querySelector: '.mermaid' }).then(function() {
            window._mermaidRendered = true;
        }).catch(function(err) {
            console.error('Mermaid render error:', err);
            window._mermaidRendered = true;
        });
    } else {
        window._mermaidRendered = true;
    }
});
"""


def _log(msg: str) -> None:
    print(f"  {msg}")


def _check_pandoc() -> bool:
    return shutil.which("pandoc") is not None


def _md_to_html(md_path: Path, extra_css: str | None = None) -> str:
    css_content = DEFAULT_CSS
    if extra_css:
        css_path = Path(extra_css)
        if css_path.is_file():
            css_content += "\n" + css_path.read_text(encoding="utf-8")
        else:
            print_warn(f"CSS 文件不存在，使用默认样式: {extra_css}")

    cmd = [
        "pandoc",
        str(md_path),
        "-f", "markdown+pipe_tables+fenced_code_blocks+yaml_metadata_block",
        "-t", "html5",
        "--standalone",
        "--no-highlight",
        "-M", "title=",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"Pandoc 转换失败: {result.stderr}")

    raw_html = result.stdout
    raw_html = _unescape_mermaid_blocks(raw_html)
    raw_html = _inject_assets(raw_html, css_content)
    return raw_html


def _unescape_mermaid_blocks(html_content: str) -> str:
    def _unescape_match(m):
        return html_lib.unescape(m.group(0))

    return re.sub(
        r'<pre class="mermaid"><code>.*?</code></pre>',
        _unescape_match,
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


def _html_to_pdf(html_content: str, output_pdf: Path, wait_ms: int = 5000,
                include_mermaid: bool = True) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError(
            "playwright 未安装。请运行: pip install playwright && playwright install chromium"
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_html = Path(tmpdir) / "document.html"
        tmp_html.write_text(html_content, encoding="utf-8")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"file:///{tmp_html.as_posix()}", wait_until="networkidle")

            if include_mermaid:
                try:
                    page.wait_for_selector(".mermaid svg", timeout=wait_ms)
                except Exception:
                    print_warn("Mermaid SVG 未在超时内出现，尝试继续渲染...")
                    page.wait_for_timeout(min(wait_ms, 3000))

            page.emulate_media(media="screen")
            page.pdf(
                path=str(output_pdf),
                format="A4",
                margin={"top": "2cm", "bottom": "2cm", "left": "2cm", "right": "2cm"},
                print_background=True,
            )
            browser.close()


def export_pdf(input_md: Path, output_pdf: Path | None = None,
               css_file: str | None = None, wait_ms: int = 5000,
               keep_html: bool = False, no_mermaid: bool = False) -> Path:
    if not input_md.is_file():
        raise FileNotFoundError(f"输入文件不存在: {input_md}")

    if output_pdf is None:
        output_pdf = input_md.with_suffix(".pdf")

    _log(f"输入: {input_md}")
    _log(f"输出: {output_pdf}")

    if not _check_pandoc():
        raise RuntimeError("pandoc 未安装或不在 PATH 中。请安装 pandoc: https://pandoc.org/installing.html")

    _log("阶段 1/3: Pandoc 转换 MD -> HTML ...")
    html_content = _md_to_html(input_md, extra_css=css_file)

    has_mermaid = 'class="mermaid"' in html_content

    if keep_html:
        html_out = output_pdf.with_suffix(".html")
        html_out.write_text(html_content, encoding="utf-8")
        _log(f"  中间 HTML 已保存: {html_out}")

    if not no_mermaid and has_mermaid:
        _log("阶段 2/3: 等待 Mermaid.js 渲染 SVG ...")
    else:
        _log("阶段 2/3: 跳过 Mermaid 渲染 ...")

    _log("阶段 3/3: Playwright 打印 HTML -> PDF ...")
    _html_to_pdf(html_content, output_pdf, wait_ms=wait_ms,
                 include_mermaid=not no_mermaid and has_mermaid)

    print_pass(f"PDF 导出成功: {output_pdf}")
    return output_pdf


def main():
    parser = argparse.ArgumentParser(
        description="三段式 Markdown+Mermaid -> PDF 导出工具（Pandoc + Mermaid.js + Playwright）"
    )
    parser.add_argument("input", help="输入 Markdown 文件路径")
    parser.add_argument("-o", "--output", help="输出 PDF 文件路径（默认与输入同目录同名）")
    parser.add_argument("--css", help="自定义 CSS 文件路径（追加到默认样式之后）")
    parser.add_argument("--wait-ms", type=int, default=5000,
                        help="Mermaid 渲染等待超时(毫秒)，默认 5000")
    parser.add_argument("--keep-html", action="store_true",
                        help="保留中间 HTML 文件用于调试（与PDF同目录同名.html）")
    parser.add_argument("--no-mermaid", action="store_true",
                        help="跳过 Mermaid 渲染（文档不含Mermaid图时使用）")

    args = parser.parse_args()
    os.environ["PYTHONIOENCODING"] = "utf-8"

    input_md = Path(args.input).resolve()
    output_pdf = Path(args.output).resolve() if args.output else None

    try:
        export_pdf(
            input_md=input_md,
            output_pdf=output_pdf,
            css_file=args.css,
            wait_ms=args.wait_ms,
            keep_html=args.keep_html,
            no_mermaid=args.no_mermaid,
        )
        return 0
    except Exception as e:
        print_error(f"导出失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
