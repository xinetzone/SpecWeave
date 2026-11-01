"""Regression tests for Mermaid source preservation and fail-closed printing."""

import ast
import html
import importlib.util
import os
import re
from pathlib import Path
from urllib.request import urlopen

import pytest
from playwright.sync_api import sync_playwright

SCRIPT = Path(__file__).with_name("build_bundle_pdf.py")
spec = importlib.util.spec_from_file_location("bundle_pdf", SCRIPT)
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


@pytest.fixture(scope="session")
def mermaid_library():
    # Fetch the real parser once; individual browser cases use deterministic routing.
    cached = os.environ.get("MERMAID_TEST_LIBRARY")
    if cached:
        return Path(cached).read_bytes()
    with urlopen(exporter.MERMAID_CDN, timeout=60) as response:
        return response.read()


@pytest.mark.parametrize("fence", ["```", "~~~~"])
def test_link_demotion_preserves_fenced_code(fence):
    code = f'{fence}mermaid\nflowchart LR\n A["[label](relative.md)"] --> B\n{fence}\n'
    text = "[Guide](guide.md)\n" + code
    assert exporter.demote_links(text) == "Guide\n" + code


@pytest.mark.parametrize("label", ["line<br/>next", "&quot;quote&quot;", "<tag>&value"])
def test_pandoc_mermaid_text_roundtrip(label):
    source = f'flowchart LR\n A["{label}"] --> B\n'
    document = exporter.md_to_html("```mermaid\n" + source + "```\n", "Test")
    block = re.search(r'<pre class="mermaid"><code>(.*?)</code></pre>', document, re.S)
    assert block
    assert html.unescape(block.group(1)) == source.rstrip("\n")


def test_valid_mermaid_renders_once(mermaid_library):
    document = exporter.md_to_html('```mermaid\nflowchart LR\n A["line<br/>next"] --> B\n```\n', "Test")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge", headless=True)
        try:
            page = browser.new_page()
            page.route(exporter.MERMAID_CDN, lambda route: route.fulfill(
                content_type="application/javascript", body=mermaid_library
            ))
            page.set_content(document)
            page.wait_for_function(
                "() => window.__mermaidRender?.status === 'done'", timeout=30000
            )
            assert page.locator(".mermaid svg").count() == 1
            assert page.locator(".mermaid .error-text").count() == 0
            assert "line" in page.locator(".mermaid .nodeLabel").first.inner_text()
        finally:
            browser.close()


@pytest.mark.parametrize("failure", ["syntax", "cdn", "timeout"])
def test_failed_mermaid_does_not_overwrite_pdf(tmp_path, failure, monkeypatch, request):
    library = request.getfixturevalue("mermaid_library") if failure == "syntax" else None
    source = 'flowchart LR\n A["unclosed\n' if failure == "syntax" else "flowchart LR\n A --> B\n"
    document = exporter.md_to_html("```mermaid\n" + source + "```\n", "Test")
    target = tmp_path / "existing.pdf"
    target.write_bytes(b"existing-pdf")
    launch = exporter._launch
    blocked = []
    signals = []

    def blocked_launch(pw, channel):
        browser = launch(pw, channel)
        new_page = browser.new_page

        def routed_page(*args, **kwargs):
            page = new_page(*args, **kwargs)
            page.on("console", lambda message: signals.append(message.text))

            def abort(route):
                blocked.append(route.request.url)
                if failure == "timeout":
                    route.fulfill(
                        content_type="application/javascript",
                        body="window.mermaid={initialize(){},parse(){console.log('parse entered');return new Promise(()=>{})}};",
                    )
                elif failure == "cdn":
                    route.abort()
                else:
                    route.fulfill(content_type="application/javascript", body=library)

            page.route(exporter.MERMAID_CDN, abort)
            return page

        browser.new_page = routed_page
        return browser

    monkeypatch.setattr(exporter, "_launch", blocked_launch)
    reason = {"syntax": "Parse error", "cdn": "library unavailable", "timeout": "Timeout"}
    with pytest.raises(RuntimeError, match=reason[failure]):
        exporter.html_to_pdf(
            document, target, channel="msedge",
            wait_ms=2000 if failure == "timeout" else 30000,
        )
    assert target.read_bytes() == b"existing-pdf"
    if failure in {"cdn", "timeout"}:
        assert blocked == [exporter.MERMAID_CDN]
    if failure == "timeout":
        assert "parse entered" in signals


def test_myst_toctree_does_not_swallow_next_document():
    markdown = (
        "# Index\n\n```{toctree}\n:hidden:\n\nconcepts/index\n```\n\n"
        '# Concept\n\n```mermaid\nflowchart LR\n A --> B\n```\n'
    )
    document = exporter.md_to_html(markdown, "Test")
    assert '<h1 id="concept">' in document
    assert len(re.findall(r'<pre class="mermaid">', document)) == 1


def test_complete_bundle_preserves_every_mermaid_source():
    bundle = SCRIPT.parents[4] / (
        "projects/awesome-okf-xs/doc/bundles/guoxue/laozi/laozi-culture-ecosystem"
    )
    merged = exporter.build_merged_markdown(bundle, exporter.discover_markdown(bundle))
    sources = re.findall(r"^```mermaid\n(.*?)^```\s*$", merged, re.M | re.S)
    document = exporter.md_to_html(merged, "Test")
    blocks = re.findall(r'<pre class="mermaid"><code>(.*?)</code></pre>', document, re.S)
    assert len(sources) == 12
    assert [source.strip() for source in sources] == [
        html.unescape(block).strip() for block in blocks
    ]


def test_toc_has_explicit_title():
    document = exporter.md_to_html("# First\n\n## Second\n", "Test")
    toc = re.search(r'<nav id="TOC".*?</nav>', document, re.S)
    assert toc
    assert "\u76ee\u5f55" in toc.group(0)


def test_mermaid_loss_stops_before_printing(monkeypatch):
    run = exporter.subprocess.run

    def lose_diagram(*args, **kwargs):
        result = run(*args, **kwargs)
        result.stdout = re.sub(
            r'<pre class="mermaid"><code>.*?</code></pre>', "", result.stdout, flags=re.S
        )
        return result

    monkeypatch.setattr(exporter.subprocess, "run", lose_diagram)
    with pytest.raises(RuntimeError, match="Mermaid"):
        exporter.md_to_html("```mermaid\nflowchart LR\n A --> B\n```\n", "Test")


def test_final_validation_failure_preserves_existing_pdf(tmp_path, monkeypatch):
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "index.md").write_text("# Index\n", encoding="utf-8")
    target = tmp_path / "existing.pdf"
    target.write_bytes(b"existing-pdf")

    def print_invalid(document, output, **kwargs):
        output.write_bytes(b"invalid-pdf")
        return "cdp"

    monkeypatch.setattr(exporter, "html_to_pdf", print_invalid)
    monkeypatch.setattr(exporter, "verify_pdf", lambda path, **kwargs: {
        "size": 11, "pages": 1, "outline": 1, "annots": 1,
        "has_toc": False, "mermaid_errors": 0,
    })
    assert exporter.run(bundle, target, "Test", None, "msedge", 30000, False, False, False) == 1
    assert target.read_bytes() == b"existing-pdf"


def test_explicit_no_mermaid_prints_source(tmp_path):
    document = exporter.md_to_html(
        "# First\n\n```mermaid\nflowchart LR\n A --> B\n```\n", "Test"
    )
    target = tmp_path / "source.pdf"
    exporter.html_to_pdf(document, target, channel="msedge", include_mermaid=False)
    from pypdf import PdfReader

    assert "flowchart LR" in "".join(page.extract_text() for page in PdfReader(target).pages)


def test_no_future_annotations():
    for path in Path(__file__).parent.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        assert not any(
            isinstance(node, ast.ImportFrom)
            and node.module == "__future__"
            and any(alias.name == "annotations" for alias in node.names)
            for node in ast.walk(tree)
        ), path


def test_heading_injection_preserves_long_fence():
    text = "````text\n```\n# sample\n````\n\n# Real\n"
    assert exporter.inject_heading_ids(text, "test") == (
        "````text\n```\n# sample\n````\n\n# Real {#doc-test}\n"
    )


def test_pdf_navigation_rejects_missing_toc_targets(tmp_path):
    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.add_outline_item("First", 0)
    target = tmp_path / "missing.pdf"
    writer.write(target)
    info = exporter.verify_pdf(target, expected_targets={"first"})
    assert info["missing_targets"] == ["first"]
    assert info["navigation_ok"] is False


def test_pdf_navigation_accepts_real_named_destination(tmp_path):
    from pypdf import PdfWriter
    from pypdf.generic import DictionaryObject, NameObject, TextStringObject
    from pypdf.annotations import Link

    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.add_outline_item("First", 0)
    writer.add_named_destination("first", 0)
    annotation = Link(rect=(0, 0, 50, 50), target_page_index=0)
    annotation[NameObject("/Dest")] = TextStringObject("first")
    writer.add_annotation(0, DictionaryObject(annotation))
    target = tmp_path / "valid.pdf"
    writer.write(target)
    info = exporter.verify_pdf(target, expected_targets={"first"})
    assert info["missing_targets"] == []
    assert info["navigation_ok"] is True
