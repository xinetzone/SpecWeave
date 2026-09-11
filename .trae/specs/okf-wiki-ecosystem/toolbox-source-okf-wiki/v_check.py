import re
import pathlib

import yaml

base = pathlib.Path("projects/awesome-okf-xs/doc/bundles/jishu/containers/toolbox")
new = [
    "concepts/04-podman-argv-layer.md",
    "concepts/05-name-resolution.md",
    "concepts/06-create-argv.md",
    "concepts/07-init-container.md",
    "concepts/08-cross-distro-binary.md",
    "concepts/09-nvidia-cdi.md",
    "concepts/10-build-and-tests.md",
    "examples/03-multi-distro.md",
    "examples/04-nvidia-gpu.md",
    "examples/05-system-tests.md",
    "references/source-code-map.md",
    "references/docs-man-source.md",
]
for rel in new:
    p = base / rel
    raw = p.read_bytes()
    assert raw[:3] != b"\xef\xbb\xbf", f"BOM {rel}"
    txt = raw.decode("utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    assert m, f"no frontmatter {rel}"
    fm = yaml.safe_load(m.group(1))
    for k in ["type", "title", "description", "tags", "generated", "verified", "status", "stale_after", "sources"]:
        assert k in fm, f"{rel} missing {k}"
    assert fm["type"] in ("Concept", "Example", "Reference")
    assert fm["status"] == "stable"
    for s in fm["sources"]:
        res = s["resource"]
        if res.startswith("/references/"):
            t = (base / res.lstrip("/")).resolve()
            assert t.exists(), f"BROKEN source {rel} -> {res}"
    for link in re.findall(r"\]\(([^)]+\.md)(?:#[^)]*)?\)", txt):
        if link.startswith("http"):
            continue
        t = (p.parent / link.split("#")[0]).resolve()
        assert t.exists(), f"BROKEN {rel} -> {link}"
    print("OK", rel, "| sources:", len(fm["sources"]))
print("ALL STRUCTURE CHECKS PASSED")
