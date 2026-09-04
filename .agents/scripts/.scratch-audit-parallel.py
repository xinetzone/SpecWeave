import importlib
import importlib.util
import sys
import inspect
import re
from pathlib import Path

EXTENSIONS = [
    "mystx",
    "sphinx_design",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_comments",
    "_ext.gallery_directive",
    "sphinx_sitemap",
    "sphinxcontrib.bibtex",
    "autoapi.extension",
    "sphinx.ext.graphviz",
    "sphinx_contributors",
    "sphinxext.opengraph",
    "sphinx_tippy",
    "sphinx.ext.extlinks",
    "sphinx_examples",
    "sphinx_pyscript",
    "mystx.ext.github_readme_stats",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

def _import_safe(name):
    try:
        return importlib.import_module(name), None
    except Exception as e:
        return None, f"import_error: {type(e).__name__}: {e}"

def _inspect_module_setup(mod_name):
    mod, err = _import_safe(mod_name)
    if err:
        return {"name": mod_name, "status": "uninstalled", "error": err,
                "read_safe": None, "write_safe": None, "loc": None}
    setup_fn = getattr(mod, "setup", None)
    if setup_fn is None:
        return {"name": mod_name, "status": "no_setup_attr",
                "read_safe": "NA", "write_safe": "NA",
                "loc": getattr(mod, "__file__", None)}
    try:
        src_file = inspect.getsourcefile(setup_fn)
    except Exception:
        src_file = getattr(mod, "__file__", None)
    try:
        src = inspect.getsource(setup_fn)
    except Exception:
        src = ""
    read_safe = write_safe = "undeclared"
    m_read = re.search(r"[\"']parallel_read_safe[\"']\s*:\s*(True|False|None)", src)
    m_write = re.search(r"[\"']parallel_write_safe[\"']\s*:\s*(True|False|None)", src)
    if m_read:
        v = m_read.group(1)
        read_safe = True if v == "True" else (False if v == "False" else None)
    if m_write:
        v = m_write.group(1)
        write_safe = True if v == "True" else (False if v == "False" else None)
    return {
        "name": mod_name, "status": "ok",
        "read_safe": read_safe, "write_safe": write_safe,
        "loc": src_file, "has_setup": True,
    }

results = [_inspect_module_setup(n) for n in EXTENSIONS]

lines = []
lines.append("| 扩展 | 安装 | parallel_read_safe | parallel_write_safe | 位置 |")
lines.append("|------|:----:|:------------------:|:-------------------:|------|")
for r in results:
    name = r["name"]
    installed = {
        "ok": "ok", "no_setup_attr": "ok", "uninstalled": "no"
    }.get(r["status"], "?")
    rs = r["read_safe"]
    ws = r["write_safe"]
    def disp(v):
        if v is True: return "TRUE"
        if v is False: return "FALSE"
        if v is None: return "NONE"
        if v == "undeclared": return "UNDECLARED"
        return str(v)
    loc = r.get("loc") or r.get("error") or "-"
    if isinstance(loc, str) and "site-packages" in loc:
        loc = "...site-packages/" + loc.split("site-packages")[-1].lstrip("\\/")
    if isinstance(loc, str) and len(loc) > 120:
        loc = loc[:117] + "..."
    lines.append(f"| {name} | {installed} | {disp(rs)} | {disp(ws)} | `{loc}` |")

out = Path(r"d:\spaces\SpecWeave\.temp-p1-audit.md")
out.write_text("\n".join(lines), encoding="utf-8")
print("OK wrote", len(lines), "lines to", out)
