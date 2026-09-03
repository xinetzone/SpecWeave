#!/usr/bin/env python3
"""
Validate docx content completeness — detect empty documents, style issues, and numbering problems.

Usage:
    python validate_content.py document.docx

Exit codes:
    0  All checks passed
    1  Validation errors found (empty doc, empty sections, etc.)

Checks:
    1. Empty document — no text content at all
    2. Empty heading sections — a heading followed immediately by another heading (same or higher level) with no body paragraphs between them
    3. Hardcoded heading numbers — heading text starts with a number pattern like "1.", "2.1", "3.1.2", "一、", "（一）", "第一章"
    4. Heading size same as body — heading styles have the same font size as body text (paragraphStyles missing or incomplete)
    5. Missing numbering binding — heading styles lack numbering config (no automatic heading numbers will render)
    6. Run-level size override — heading paragraph contains TextRun with explicit font size equal to body text, overriding the style-level heading size
"""

import re
import sys
import zipfile
from xml.etree import ElementTree as ET

WML_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _text(elem):
    """Extract concatenated text from all w:t descendants."""
    parts = []
    for t in elem.iter(f"{{{WML_NS}}}t"):
        if t.text:
            parts.append(t.text)
    return "".join(parts).strip()


DWP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
DWP14_NS = "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"


def _heading_level(p_elem):
    """Return heading level (1-9) from pStyle, or 0 if not a heading."""
    ppr = p_elem.find(f"{{{WML_NS}}}pPr")
    if ppr is None:
        return 0
    pstyle = ppr.find(f"{{{WML_NS}}}pStyle")
    if pstyle is None:
        return 0
    val = pstyle.get(f"{{{WML_NS}}}val", "")
    m = re.match(r"[Hh]eading\s*(\d)", val)
    return int(m.group(1)) if m else 0


def _has_content(p_elem):
    """Check if a paragraph has meaningful content (text, images, or embedded objects)."""
    # Text content
    if _text(p_elem):
        return True
    # Images: <w:drawing> containing wp:inline or wp:anchor
    for drawing in p_elem.iter(f"{{{WML_NS}}}drawing"):
        for ns in (DWP_NS, DWP14_NS):
            if drawing.find(f"{{{ns}}}inline") is not None or drawing.find(f"{{{ns}}}anchor") is not None:
                return True
    # Embedded objects: <w:object>
    if p_elem.find(f".//{{{WML_NS}}}object") is not None:
        return True
    return False


_HARDCODED_NUM_RE = re.compile(
    r"^\d+(\.\d+)*[\.\s\uff0e\u3001]"            # Arabic: "1.", "2.1 ", "3.1.2."
    r"|^[一二三四五六七八九十百]+[、\.\uff0e\u3001]"  # Chinese: "一、", "二."
    r"|^[\uff08\(][一二三四五六七八九十百\d]+[\uff09\)]"  # Parenthesized: "（一）", "(1)"
    r"|^第[一二三四五六七八九十百\d]+[章节部篇]"      # Ordinal: "第一章", "第2节"
)


def _get_default_body_size(styles_root):
    """Extract default body text size (half-point) from styles.xml <w:docDefaults>."""
    # Try <w:docDefaults> → <w:rPrDefault> → <w:rPr> → <w:sz>
    doc_defaults = styles_root.find(f".//{{{WML_NS}}}docDefaults")
    if doc_defaults is not None:
        rpr_default = doc_defaults.find(f".//{{{WML_NS}}}rPrDefault")
        if rpr_default is not None:
            sz = rpr_default.find(f".//{{{WML_NS}}}rPr/{{{WML_NS}}}sz")
            if sz is not None:
                val = sz.get(f"{{{WML_NS}}}val")
                if val and val.isdigit():
                    return int(val)
    return None


def _get_heading_styles_info(styles_root):
    """Extract heading style font sizes and numbering bindings from styles.xml.

    Returns dict: { "Heading1": {"size": 32, "has_numbering": True}, ... }
    """
    info = {}
    for style in styles_root.findall(f"{{{WML_NS}}}style"):
        style_id = style.get(f"{{{WML_NS}}}styleId", "")
        if not re.match(r"[Hh]eading\d$", style_id):
            continue

        # Extract font size from <w:rPr><w:sz>
        rpr = style.find(f"{{{WML_NS}}}rPr")
        size = None
        if rpr is not None:
            sz = rpr.find(f"{{{WML_NS}}}sz")
            if sz is not None:
                val = sz.get(f"{{{WML_NS}}}val")
                if val and val.isdigit():
                    size = int(val)

        # Check for numbering binding: <w:pPr><w:numPr>
        ppr = style.find(f"{{{WML_NS}}}pPr")
        has_numbering = False
        if ppr is not None:
            num_pr = ppr.find(f"{{{WML_NS}}}numPr")
            if num_pr is not None:
                has_numbering = True

        info[style_id] = {"size": size, "has_numbering": has_numbering}

    return info


def _check_heading_sizes(styles_root, used_levels):
    """Check 4: Heading styles have same font size as body text.

    Only checks heading levels that are actually used in the document content.
    docx-js auto-generates Heading1-6 default styles, but unused ones are irrelevant.
    """
    errors = []
    body_size = _get_default_body_size(styles_root)
    heading_info = _get_heading_styles_info(styles_root)

    for style_id, info in sorted(heading_info.items()):
        # Extract level number from style_id (e.g., "Heading1" → 1)
        m = re.match(r"[Hh]eading(\d)", style_id)
        if m and int(m.group(1)) not in used_levels:
            continue  # Skip heading levels not used in document

        h_size = info["size"]
        if h_size is None:
            # Heading style has no explicit size → inherits body size
            errors.append(
                f"HEADING_NO_SIZE: {style_id} has no font size defined — "
                f"it will inherit the body text size ({body_size or 'unknown'} half-pt). "
                f"Add paragraphStyles with explicit size for each heading level"
            )
        elif body_size is not None and h_size == body_size:
            errors.append(
                f"HEADING_SIZE_SAME_AS_BODY: {style_id} size ({h_size} half-pt) "
                f"equals body text size ({body_size} half-pt) — "
                f"headings should be larger than body text"
            )

    return errors


def _check_heading_numbering(styles_root, has_numbering_xml, used_levels):
    """Check 5: Heading styles have numbering binding when numbering.xml exists.

    Only warns if the document HAS a numbering.xml (i.e., uses some numbering)
    but the heading styles are NOT bound to any numbering reference.
    If the document uses no numbering at all, skip this check.
    Only checks heading levels that are actually used in the document.
    """
    errors = []
    if not has_numbering_xml:
        return errors  # No numbering in document, skip

    heading_info = _get_heading_styles_info(styles_root)

    # Filter to only used heading levels
    used_info = {}
    for style_id, info in heading_info.items():
        m = re.match(r"[Hh]eading(\d)", style_id)
        if m and int(m.group(1)) in used_levels:
            used_info[style_id] = info

    # Check if ANY used heading has numbering → if none do, warn
    any_heading_has_numbering = any(
        info["has_numbering"] for info in used_info.values()
    )

    if used_info and not any_heading_has_numbering:
        errors.append(
            "HEADING_NO_NUMBERING: Document has numbering.xml but no heading styles "
            "are bound to a numbering reference — headings won't have automatic numbers. "
            "Add numbering: { reference: \"...\", level: N } to each heading paragraphStyle"
        )

    return errors


def _check_run_level_size_override(body, styles_root):
    """Check 6: Heading paragraphs contain TextRuns with explicit font size that
    overrides the style-level heading size, making headings render at body text size.

    This catches the common docx-js mistake where heading() helper creates TextRun
    with a hardcoded size (e.g., size: 21) that overrides the paragraphStyle size.
    """
    errors = []
    body_size = _get_default_body_size(styles_root) if styles_root is not None else None
    heading_styles = _get_heading_styles_info(styles_root) if styles_root is not None else {}

    children = list(body)
    for child in children:
        if child.tag != f"{{{WML_NS}}}p":
            continue
        lvl = _heading_level(child)
        if lvl == 0:
            continue

        style_id = f"Heading{lvl}"
        style_size = heading_styles.get(style_id, {}).get("size")

        # Collect all run-level sizes in this heading paragraph
        for run in child.findall(f"{{{WML_NS}}}r"):
            rpr = run.find(f"{{{WML_NS}}}rPr")
            if rpr is None:
                continue
            sz = rpr.find(f"{{{WML_NS}}}sz")
            if sz is None:
                continue
            val = sz.get(f"{{{WML_NS}}}val")
            if not val or not val.isdigit():
                continue
            run_size = int(val)

            # Problem: run explicitly sets size equal to body, overriding the larger style size
            if body_size is not None and run_size == body_size and style_size and run_size < style_size:
                text = _text(child)
                preview = text[:40] + ("..." if len(text) > 40 else "")
                errors.append(
                    f"RUN_SIZE_OVERRIDE: Heading{lvl} \"{preview}\" — "
                    f"TextRun has explicit size {run_size} half-pt (= body text) "
                    f"which overrides the style size {style_size} half-pt. "
                    f"Remove the size property from TextRun in heading paragraphs, "
                    f"or set it to match the heading style size"
                )
                break  # One error per heading paragraph is enough

    return errors


def validate(docx_path):
    errors = []

    with zipfile.ZipFile(docx_path, "r") as zf:
        if "word/document.xml" not in zf.namelist():
            errors.append("FATAL: word/document.xml not found in archive")
            return errors

        tree = ET.parse(zf.open("word/document.xml"))
        root = tree.getroot()

        # Parse styles.xml for heading size and numbering checks
        styles_root = None
        if "word/styles.xml" in zf.namelist():
            styles_root = ET.parse(zf.open("word/styles.xml")).getroot()

        has_numbering_xml = "word/numbering.xml" in zf.namelist()

    body = root.find(f"{{{WML_NS}}}body")
    if body is None:
        errors.append("FATAL: <w:body> not found")
        return errors

    # Iterate all direct children of body (w:p, w:tbl, w:sdt, etc.)
    children = list(body)
    paragraphs = [c for c in children if c.tag == f"{{{WML_NS}}}p"]

    # --- Check 1: empty document ---
    has_any_text = any(_text(p) for p in paragraphs)
    has_any_table = any(c.tag == f"{{{WML_NS}}}tbl" for c in children)
    if not has_any_text and not has_any_table:
        errors.append("EMPTY_DOC: Document contains no text content at all")
        return errors

    # --- Check 2 & 3: per-heading analysis ---
    # Build index over body children: (child_index, heading_level, text) for headings
    heading_entries = []
    for i, child in enumerate(children):
        if child.tag == f"{{{WML_NS}}}p":
            lvl = _heading_level(child)
            if lvl > 0:
                heading_entries.append((i, lvl, _text(child)))

    for pos, (idx, lvl, htxt) in enumerate(heading_entries):
        # Check 3: hardcoded number prefix
        if _HARDCODED_NUM_RE.match(htxt):
            errors.append(
                f"HARDCODED_NUM: Heading {lvl} \"{htxt}\" has hardcoded number prefix — use numbering config instead"
            )

        # Check 2: empty section
        next_idx = heading_entries[pos + 1][0] if pos + 1 < len(heading_entries) else len(children)

        # Count content elements between this heading and next boundary
        content_count = 0
        for j in range(idx + 1, next_idx):
            child = children[j]
            # Tables count as content
            if child.tag == f"{{{WML_NS}}}tbl":
                content_count += 1
                continue
            # Paragraphs: check for text, images, or objects
            if child.tag == f"{{{WML_NS}}}p":
                if _heading_level(child) > 0:
                    break
                if _has_content(child):
                    content_count += 1

        if content_count == 0 and htxt:
            # Skip parent headings (immediately followed by a sub-heading)
            has_sub = False
            if pos + 1 < len(heading_entries):
                next_lvl = heading_entries[pos + 1][1]
                next_i = heading_entries[pos + 1][0]
                if next_lvl > lvl and next_i == idx + 1:
                    has_sub = True
            if not has_sub:
                errors.append(
                    f"EMPTY_SECTION: Heading {lvl} \"{htxt}\" has no body content before next heading"
                )

    # --- Check 4 & 5: style and numbering checks (from styles.xml) ---
    # Collect which heading levels are actually used in the document
    used_levels = {lvl for _, lvl, _ in heading_entries}
    if styles_root is not None and used_levels:
        errors.extend(_check_heading_sizes(styles_root, used_levels))
        errors.extend(_check_heading_numbering(styles_root, has_numbering_xml, used_levels))

    # --- Check 6: run-level size override in heading paragraphs ---
    if styles_root is not None:
        errors.extend(_check_run_level_size_override(body, styles_root))

    return errors


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <document.docx>", file=sys.stderr)
        sys.exit(2)

    path = sys.argv[1]
    errors = validate(path)

    if not errors:
        print(f"PASSED: {path} — all content checks OK")
        sys.exit(0)
    else:
        print(f"FAILED: {path} — {len(errors)} issue(s) found:\n")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
