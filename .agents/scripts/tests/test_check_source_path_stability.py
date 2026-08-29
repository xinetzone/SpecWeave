"""check-source-path-stability.py 单元测试。

覆盖信源引用稳定性扫描的核心场景：
- 三类载体（link/frontmatter/prose）× 两种斜杠的临时信源检测
- 稳定性分类（temporary/stable/env-bound/relative）
- 存在性复验、代码块内标记、frontmatter 区域识别
- 误报防护：https URL、bundle-relative 链接不命中
- 清理前扫描模式（--target）的签名匹配与退出码
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
import json
import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "check_source_path_stability",
    _SCRIPTS_DIR / "check-source-path-stability.py",
)
sps = importlib.util.module_from_spec(_spec)
sys.modules["check_source_path_stability"] = sps
_spec.loader.exec_module(sps)


@pytest.fixture
def project(tmp_path):
    """构造最小项目树：临时信源与 vendor 稳定信源均真实存在。"""
    (tmp_path / ".chaos" / "libs" / "temp-clone").mkdir(parents=True)
    (tmp_path / "vendor" / "stable-lib").mkdir(parents=True)
    return tmp_path


def _write(root: Path, rel: str, content: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# 分类与归一化
# ---------------------------------------------------------------------------
class TestClassify:
    def test_temp_segments(self):
        assert sps.classify_stability(r"d:\AI\.chaos\libs\foo") == "temporary"
        assert sps.classify_stability("d:/AI/.tmp/cache-x") == "temporary"
        assert sps.classify_stability("/tmp/work/x") == "temporary"

    def test_stable_segments(self):
        assert sps.classify_stability(r"d:\AI\vendor\veadk-python") == "stable"
        assert sps.classify_stability("/usr/lib/python3/site-packages/x") == "stable"

    def test_env_bound(self):
        assert sps.classify_stability(r"C:\Users\someone\Desktop\notes") == "env-bound"

    def test_relative(self):
        assert sps.classify_stability("concepts/01-task.md") == "relative"

    def test_normalize_file_url(self):
        assert sps.normalize_token("file:///d:/AI/vendor/x") == "d:/AI/vendor/x"
        assert sps.normalize_token("file:///d%3A/AI/x") == "d:/AI/x"

    def test_normalize_strips_punct(self):
        # 句尾标点与尾随斜杠剥离（目录路径形态）
        assert sps.normalize_token("d:/AI/x.") == "d:/AI/x"
        assert sps.normalize_token("d:/AI/.chaos/x/") == "d:/AI/.chaos/x"
        assert sps.normalize_token("d:/AI/x),") == "d:/AI/x"


class TestPathLike:
    def test_drive_path(self):
        assert sps._is_path_like(r"d:\AI\vendor\foo") is True

    def test_bundle_relative_not_path_like(self):
        # bundle-relative 链接不含盘符/临时段/稳定段，不应判为信源路径
        assert sps._is_path_like("/concepts/01-task.md") is False

    def test_vendor_relative(self):
        assert sps._is_path_like("vendor/veadk-python/veadk") is True


# ---------------------------------------------------------------------------
# audit 模式：三类载体
# ---------------------------------------------------------------------------
class TestAuditForms:
    def test_prose_backslash_temp(self, project):
        """prose 载体 + 反斜杠 + 临时段（veadk 案例形态）。"""
        target = (project / ".chaos" / "libs" / "temp-clone")
        _write(project, "docs/a.md", f"源码路径：`{target}`\n")
        findings = sps.scan_file(project / "docs/a.md", project)
        assert len(findings) == 1
        f = findings[0]
        assert f.stability == "temporary"
        assert f.form == "prose"
        assert f.exists is True

    def test_link_forward_slash_temp(self, project):
        """link 载体 + 正斜杠 file:/// URL。"""
        url = "file:///" + (project / ".chaos" / "libs" / "temp-clone" / "x.py").as_posix()
        _write(project, "docs/b.md", f"[源码]({url})\n")
        findings = sps.scan_file(project / "docs/b.md", project)
        temp = [f for f in findings if f.stability == "temporary"]
        assert len(temp) == 1
        assert temp[0].form == "link"

    def test_frontmatter_bare_path(self, project):
        """frontmatter 载体裸路径（source 字段，相对 vendor 路径）。"""
        content = (
            "---\n"
            "title: t\n"
            'source: "vendor/stable-lib"\n'
            "---\n# t\n"
        )
        _write(project, "docs/c.md", content)
        findings = sps.scan_file(project / "docs/c.md", project)
        fm = [f for f in findings if f.form == "frontmatter"]
        assert len(fm) == 1
        assert fm[0].stability == "stable"
        assert fm[0].exists is True

    def test_frontmatter_list_item_bare_temp_path(self, project):
        """frontmatter YAML 列表项裸临时路径（无键冒号，V阶段对抗审查发现的漏报面）。"""
        content = (
            "---\n"
            "title: t\n"
            "sources:\n"
            "  - .chaos/libs/temp-clone\n"
            "---\n# t\n"
        )
        _write(project, "docs/fm-list.md", content)
        findings = sps.scan_file(project / "docs/fm-list.md", project)
        temp = [f for f in findings if f.stability == "temporary"]
        assert len(temp) == 1
        assert temp[0].form == "frontmatter"
        assert temp[0].exists is True

    def test_frontmatter_list_item_mapping_not_double_counted(self, project):
        """列表项中的映射行（- key: value）走键值逻辑，不重复计数。"""
        content = (
            "---\n"
            "title: t\n"
            "sources:\n"
            "  - resource: vendor/stable-lib\n"
            "---\n# t\n"
        )
        _write(project, "docs/fm-map.md", content)
        findings = sps.scan_file(project / "docs/fm-map.md", project)
        stable = [f for f in findings if f.stability == "stable"]
        assert len(stable) == 1
        assert stable[0].form == "frontmatter"

    def test_missing_stable_path(self, project):
        """稳定段路径但目标不存在 → exists=False。"""
        _write(project, "docs/d.md", "`d:/AI/vendor/does-not-exist`\n")
        findings = sps.scan_file(project / "docs/d.md", project)
        assert len(findings) == 1
        assert findings[0].stability == "stable"
        assert findings[0].exists is False

    def test_code_block_tagged(self, project):
        """代码块内引用仍命中，但标记 in_code_block。"""
        content = "```python\npath = r'd:\\AI\\.chaos\\libs\\temp-clone'\n```\n"
        _write(project, "docs/e.md", content)
        findings = sps.scan_file(project / "docs/e.md", project)
        assert len(findings) == 1
        assert findings[0].in_code_block is True
        assert findings[0].stability == "temporary"

    def test_https_url_not_matched(self, project):
        """误报防护：https:// 不应被盘符正则命中。"""
        _write(project, "docs/f.md", "见 https://example.com/docs 与 [链接](https://x.io/a)\n")
        findings = sps.scan_file(project / "docs/f.md", project)
        assert findings == []

    def test_bundle_relative_link_not_matched(self, project):
        """误报防护：bundle-relative /concepts/ 链接不命中。"""
        _write(project, "docs/g.md", "[任务](/concepts/01-task.md) 与 `/references/src.md`\n")
        findings = sps.scan_file(project / "docs/g.md", project)
        assert findings == []


# ---------------------------------------------------------------------------
# 清理前扫描模式
# ---------------------------------------------------------------------------
class TestCleanupScan:
    def test_signature_matches_both_slashes(self, project):
        sig = sps.build_target_signature(
            project / ".chaos/libs/temp-clone", project
        )
        import re
        pat = re.compile(sig)
        assert pat.search(r"d:\AI\.chaos\libs\temp-clone\veadk")
        assert pat.search("d:/AI/.chaos/libs/temp-clone/veadk")
        assert not pat.search("d:/AI/.chaos/libs/other-clone")

    def test_scan_finds_three_forms(self, project):
        _write(project, "docs/h1.md", "`d:\\AI\\.chaos\\libs\\temp-clone\\`\n")
        _write(project, "docs/h2.md", "[x](file:///d:/AI/.chaos/libs/temp-clone/a)\n")
        _write(project, "docs/sub/h3.md", "plain text d:/AI/.chaos/libs/temp-clone/b\n")
        findings = sps.scan_references_to_target(
            project / ".chaos/libs/temp-clone", [project], project
        )
        assert len(findings) == 3

    def test_scan_skips_unrelated_target(self, project):
        _write(project, "docs/i.md", "`d:\\AI\\.chaos\\libs\\other-clone\\`\n")
        findings = sps.scan_references_to_target(
            project / ".chaos/libs/temp-clone", [project], project
        )
        assert findings == []

    def test_signature_too_shallow_raises(self, project):
        with pytest.raises(ValueError):
            sps.build_target_signature(project / ".chaos", project)

    def test_scan_prunes_chaos_internal_refs(self, project):
        """.chaos 内部（克隆之间/克隆自身）的引用在目录级剪枝，不计数。"""
        # 另一个克隆中的文件引用待删除克隆——临时→临时引用，不阻断
        _write(
            project,
            ".chaos/libs/other-clone/note.md",
            "see d:/AI/.chaos/libs/temp-clone/x\n",
        )
        # 待删除克隆自身内部文件引用自己的路径——同样剪枝
        _write(
            project,
            ".chaos/libs/temp-clone/README.md",
            "self d:/AI/.chaos/libs/temp-clone\n",
        )
        findings = sps.scan_references_to_target(
            project / ".chaos/libs/temp-clone", [project], project
        )
        assert findings == []

    def test_iter_text_files_prunes_excluded_dirs(self, project):
        """walker 目录级剪枝：.chaos/vendor/.git/多段缓存均不下钻。"""
        _write(project, "docs/keep.md", "ok\n")
        _write(project, ".chaos/libs/x/a.md", "x\n")
        _write(project, "vendor/lib/b.md", "x\n")
        _write(project, ".git/c.md", "x\n")
        _write(project, ".trae/cache/d.md", "x\n")
        found = {
            str(p.relative_to(project)).replace("\\", "/")
            for p in sps._iter_text_files(project, {".md"})
        }
        assert found == {"docs/keep.md"}


# ---------------------------------------------------------------------------
# CLI 端到端
# ---------------------------------------------------------------------------
class TestCLI:
    def test_audit_exit_1_on_temp(self, project, capsys):
        _write(project, "docs/j.md", "`d:/AI/.chaos/libs/temp-clone`\n")
        rc = sps.main(["--path", str(project)])
        assert rc == 1

    def test_audit_exit_0_on_clean(self, project, capsys):
        _write(project, "docs/k.md", "[任务](/concepts/01-task.md)\n")
        rc = sps.main(["--path", str(project)])
        assert rc == 0

    def test_cleanup_exit_1_with_refs(self, project):
        _write(project, "docs/l.md", "`d:/AI/.chaos/libs/temp-clone`\n")
        rc = sps.main([
            "--path", str(project),
            "--target", str(project / ".chaos/libs/temp-clone"),
        ])
        assert rc == 1

    def test_cleanup_exit_0_no_refs(self, project):
        _write(project, "docs/m.md", "nothing relevant here\n")
        rc = sps.main([
            "--path", str(project),
            "--target", str(project / ".chaos/libs/temp-clone"),
        ])
        assert rc == 0

    def test_json_output(self, project, capsys):
        _write(project, "docs/n.md", "`d:/AI/.chaos/libs/temp-clone`\n")
        rc = sps.main(["--path", str(project), "--json"])
        assert rc == 1
        data = json.loads(capsys.readouterr().out)
        assert data["gate"] == "GATE-SPS"
        assert len(data["findings"]) == 1

    def test_missing_path_arg_error(self, project):
        rc = sps.main(["--path", str(project / "nope")])
        assert rc == 2
