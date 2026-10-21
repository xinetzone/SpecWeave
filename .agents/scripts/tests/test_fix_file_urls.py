"""fix-file-urls.py 的回归测试。

覆盖历次修复的缺陷：
- 代码围栏与行内代码中的示例链接不改写
- 目标不存在或为目录时跳过，不生成新的断链/目录链接
- #L 锚点不参与目标存在性判定且原样保留
- 读写按字节保真（CRLF 与 BOM 不被改动）
- 扫描剪枝 submodule（projects/、vendor/）与临时目录
"""

# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import importlib.util
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# 文件名含连字符，通过 importlib 加载
_SPEC = importlib.util.spec_from_file_location("fix_file_urls", SCRIPTS_DIR / "fix-file-urls.py")
fix_file_urls = importlib.util.module_from_spec(_SPEC)
sys.modules["fix_file_urls"] = fix_file_urls
_SPEC.loader.exec_module(fix_file_urls)

OLD_ROOT = "file:///d:/spaces/SpecWeave"


def _make_project(tmp_path: Path) -> Path:
    """构造含一个目标文件的临时项目根。"""
    project = tmp_path / "proj"
    (project / "docs").mkdir(parents=True)
    (project / "target").mkdir()
    (project / "target" / "a.py").write_text("x = 1\n", encoding="utf-8")
    return project


def test_converts_existing_file_and_keeps_anchor(tmp_path):
    project = _make_project(tmp_path)
    md = project / "docs" / "note.md"
    content = f"[a]({OLD_ROOT}/target/a.py#L10-L20)\n"

    new, count, skipped = fix_file_urls.convert_file_urls(content, md, project)

    assert count == 1
    assert skipped == []
    assert "[a](../target/a.py#L10-L20)" in new


def test_skips_missing_target(tmp_path):
    project = _make_project(tmp_path)
    md = project / "docs" / "note.md"
    content = f"[x]({OLD_ROOT}/target/missing.py)\n"

    new, count, skipped = fix_file_urls.convert_file_urls(content, md, project)

    assert count == 0
    assert new == content, "目标缺失时不得改写，否则会把绝对引用变成断链"
    assert len(skipped) == 1 and "不存在" in skipped[0][1]


def test_skips_directory_target(tmp_path):
    project = _make_project(tmp_path)
    md = project / "docs" / "note.md"
    content = f"[d]({OLD_ROOT}/target)\n"

    new, count, skipped = fix_file_urls.convert_file_urls(content, md, project)

    assert count == 0
    assert new == content
    assert len(skipped) == 1 and "目录" in skipped[0][1]


def test_skips_fenced_code_block(tmp_path):
    project = _make_project(tmp_path)
    md = project / "docs" / "note.md"
    fenced = f"```\n[示例]({OLD_ROOT}/target/a.py)\n```\n"
    live = f"[真实]({OLD_ROOT}/target/a.py)\n"
    content = fenced + live

    new, count, skipped = fix_file_urls.convert_file_urls(content, md, project)

    assert count == 1
    assert skipped == []
    assert fenced in new, "代码围栏内的示例必须原样保留"
    assert "[真实](../target/a.py)" in new


def test_skips_inline_code_span(tmp_path):
    project = _make_project(tmp_path)
    md = project / "docs" / "note.md"
    content = f"示例 `[x]({OLD_ROOT}/target/a.py)` 结束\n"

    new, count, _ = fix_file_urls.convert_file_urls(content, md, project)

    assert count == 0
    assert new == content


def test_preserves_crlf_and_bom(tmp_path):
    project = _make_project(tmp_path)
    md = project / "docs" / "crlf.md"
    body = f"[a]({OLD_ROOT}/target/a.py)\r\n第二行\r\n".encode("utf-8")
    md.write_bytes(b"\xef\xbb\xbf" + body)

    content, has_bom = fix_file_urls.read_text_exact(md)
    assert has_bom is True

    new, count, _ = fix_file_urls.convert_file_urls(content, md, project)
    assert count == 1
    fix_file_urls.write_text_exact(md, new, has_bom)

    raw = md.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    assert raw.count(b"\r\n") == 2
    assert b"\n" not in raw.replace(b"\r\n", b""), "不得把 CRLF 静默转成 LF"


def test_find_md_files_prunes_submodules_and_temp(tmp_path):
    project = tmp_path / "proj"
    for sub in ("docs", "projects/sub", "vendor/pkg", ".temp", "external"):
        (project / sub).mkdir(parents=True)
        (project / sub / "n.md").write_text("x", encoding="utf-8")

    found = {p.relative_to(project).as_posix() for p in fix_file_urls.find_md_files(project)}

    assert found == {"docs/n.md"}
