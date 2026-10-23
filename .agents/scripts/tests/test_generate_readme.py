"""generate-readme.py 单元测试。

回归覆盖：
- resolve_docs_home_name：docs/index.md 存在时返回 index.md，否则回落 README.md
- generate_readme_content：生成的「📚 文档首页」链接必须解析到真实存在的文件

背景：docs/README.md 已在 OKF v0.2 改造中废止，文档中心首页改为 docs/index.md。
脚本此前硬编码 'README.md'，为所有目录 README 生成了指向已废止文件的断链。
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
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent
_SPEC_PATH = SCRIPTS_DIR / "generate-readme.py"
_spec = importlib.util.spec_from_file_location("generate_readme", _SPEC_PATH)
gen_readme = importlib.util.module_from_spec(_spec)
sys.modules["generate_readme"] = gen_readme
_spec.loader.exec_module(gen_readme)


DOCS_HOME_LINK_RE = re.compile(r"- \[📚 文档首页\]\(([^)]+)\)")


def _extract_docs_home_link(content: str) -> str:
    match = DOCS_HOME_LINK_RE.search(content)
    assert match is not None, "生成的 README 缺少「📚 文档首页」链接"
    return match.group(1)


def _make_root(tmp_path: Path, docs_home: str) -> Path:
    """构造含 docs 首页与一个子目录的临时项目根。"""
    docs = tmp_path / "docs"
    (docs / "sub").mkdir(parents=True)
    (docs / docs_home).write_text("# 文档首页\n", encoding="utf-8")
    (docs / "sub" / "sample.md").write_text("# 示例\n", encoding="utf-8")
    return tmp_path


class TestResolveDocsHomeName:
    """resolve_docs_home_name 单元测试。"""

    def test_prefers_index_md_when_present(self, tmp_path):
        root = _make_root(tmp_path, "index.md")
        assert gen_readme.resolve_docs_home_name(root) == "index.md"

    def test_falls_back_to_readme_md_for_legacy_layout(self, tmp_path):
        root = _make_root(tmp_path, "README.md")
        assert gen_readme.resolve_docs_home_name(root) == "README.md"

    def test_defaults_to_readme_md_when_docs_home_missing(self, tmp_path):
        root = tmp_path / "docs"
        root.mkdir()
        assert gen_readme.resolve_docs_home_name(root) == "README.md"


class TestDocsHomeLinkResolves:
    """生成的「📚 文档首页」链接必须指向真实存在的文件。"""

    def test_generated_link_points_to_existing_file(self, tmp_path):
        root = _make_root(tmp_path, "index.md")
        dir_path = root / "docs" / "sub"
        doc_entries, dir_entries = gen_readme.scan_directory(dir_path, root)

        content = gen_readme.generate_readme_content(
            dir_path, root, doc_entries, dir_entries
        )
        link = _extract_docs_home_link(content)

        assert link == "../index.md"
        assert (dir_path / link).resolve().is_file(), f"文档首页链接断链: {link}"

    def test_legacy_layout_link_points_to_existing_file(self, tmp_path):
        root = _make_root(tmp_path, "README.md")
        dir_path = root / "docs" / "sub"
        doc_entries, dir_entries = gen_readme.scan_directory(dir_path, root)

        content = gen_readme.generate_readme_content(
            dir_path, root, doc_entries, dir_entries
        )
        link = _extract_docs_home_link(content)

        assert (dir_path / link).resolve().is_file(), f"文档首页链接断链: {link}"

    def test_never_generates_link_to_missing_docs_readme(self, tmp_path):
        """核心回归：docs/README.md 已废止时，不得再生成指向它的链接。"""
        root = _make_root(tmp_path, "index.md")
        dir_path = root / "docs" / "sub"
        doc_entries, dir_entries = gen_readme.scan_directory(dir_path, root)

        content = gen_readme.generate_readme_content(
            dir_path, root, doc_entries, dir_entries
        )
        link = _extract_docs_home_link(content)

        assert not link.endswith("README.md"), (
            f"不得指向已废止的 docs/README.md: {link}"
        )
