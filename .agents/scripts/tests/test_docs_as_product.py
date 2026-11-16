"""docs_as_product 模块单元测试。

覆盖发现层、结构校验、元数据漂移、质量门、读者契约、指标脚手架、
报告输出与 CLI 装配。
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

import json
import logging
import sys

import pytest

from lib.frontmatter import load_external_toml
from lib.docs_as_product import (
    DocsProductConfig,
    check_metadata_drift,
    check_quality_gates,
    check_reader_contract,
    check_structure,
    scaffold_metrics,
    scan_docs,
)
from lib.docs_as_product import reporter as reporter_mod
from lib.docs_as_product import structure as structure_mod
from lib.docs_as_product.metadata_drift import _is_drift_field
from lib.docs_as_product.quality_gates import _run_command, _tool_available
from lib.docs_as_product.reader_contract import find_contract_file


# ── 夹具构建 ────────────────────────────────────────────────

INDEX_MD = """# 首页

这是首页的首段说明。

```{toctree}
tutorial/first
how-to/task
reference/api
explanation/concept
```
"""

TUTORIAL_MD = """# 第一个教程

这是教程首段。

## 步骤一

操作内容。
"""

HOWTO_MD = """# 操作任务

这是操作指南首段。

## 做法

做法内容。
"""

REFERENCE_MD = """# API 参考

这是参考页首段。

## 模块

.. automodule:: some.module
"""

EXPLANATION_MD = """# 概念解释

这是解释页首段。

## 背景

背景内容。
"""

ORPHAN_MD = """# 逃逸页

这是逃逸页首段。

:orphan:
"""

# 中文目录名识别
CHINESE_TUTORIAL_MD = """# 中文教程

这是中文教程首段。
"""


def _build_standard_tree(base):
    """构建符合四型分区的标准文档树。"""
    (base / "index.md").write_text(INDEX_MD, encoding="utf-8")
    (base / "tutorial").mkdir()
    (base / "tutorial" / "first.md").write_text(TUTORIAL_MD, encoding="utf-8")
    (base / "how-to").mkdir()
    (base / "how-to" / "task.md").write_text(HOWTO_MD, encoding="utf-8")
    (base / "reference").mkdir()
    (base / "reference" / "api.md").write_text(REFERENCE_MD, encoding="utf-8")
    (base / "explanation").mkdir()
    (base / "explanation" / "concept.md").write_text(EXPLANATION_MD, encoding="utf-8")
    (base / "教程").mkdir()
    (base / "教程" / "zhongwen.md").write_text(CHINESE_TUTORIAL_MD, encoding="utf-8")


# ── 发现层 ──────────────────────────────────────────────────

class TestDiscovery:

    def test_scan_standard_tree(self, tmp_path):
        _build_standard_tree(tmp_path)
        tree = scan_docs(tmp_path)
        assert len(tree) == 6
        assert tree.get("index.md") is not None

    def test_mounted_nodes(self, tmp_path):
        _build_standard_tree(tmp_path)
        tree = scan_docs(tmp_path)
        for rel in (
            "tutorial/first.md",
            "how-to/task.md",
            "reference/api.md",
            "explanation/concept.md",
        ):
            assert tree.get(rel).in_toctree is True

    def test_index_exempt(self, tmp_path):
        _build_standard_tree(tmp_path)
        tree = scan_docs(tmp_path)
        assert tree.get("index.md").is_index is True

    def test_chinese_dir_type(self, tmp_path):
        _build_standard_tree(tmp_path)
        tree = scan_docs(tmp_path)
        node = tree.get("教程/zhongwen.md")
        assert node.doc_type == "tutorial"

    def test_explicit_frontmatter_type(self, tmp_path):
        (tmp_path / "pages").mkdir(parents=True)
        (tmp_path / "pages" / "a.md").write_text(
            "---\ndiataxis: reference\n---\n# 页\n\n首段。\n",
            encoding="utf-8",
        )
        tree = scan_docs(tmp_path)
        assert tree.get("pages/a.md").doc_type == "reference"

    def test_missing_root(self, tmp_path):
        tree = scan_docs(tmp_path / "nonexistent")
        assert len(tree) == 0

    def test_excluded_dirs(self, tmp_path):
        (tmp_path / "_build").mkdir()
        (tmp_path / "_build" / "a.md").write_text("# x", encoding="utf-8")
        tree = scan_docs(tmp_path)
        assert len(tree) == 0


# ── 结构校验 ────────────────────────────────────────────────

class TestStructure:

    def test_clean_tree_passes(self, tmp_path):
        _build_standard_tree(tmp_path)
        report = check_structure(scan_docs(tmp_path))
        # 中文教程页未挂载 → 存在 error
        codes = {f.code for f in report.findings}
        assert structure_mod.CODE_ORPHAN not in codes

    def test_orphan_finding(self, tmp_path):
        _build_standard_tree(tmp_path)
        (tmp_path / "orphan.md").write_text(ORPHAN_MD, encoding="utf-8")
        report = check_structure(scan_docs(tmp_path))
        orphans = [
            f for f in report.findings if f.code == structure_mod.CODE_ORPHAN
        ]
        assert len(orphans) == 1
        assert orphans[0].file == "orphan.md"

    def test_unmounted_finding(self, tmp_path):
        _build_standard_tree(tmp_path)
        (tmp_path / "loose.md").write_text(
            "# 游离页\n\n首段。\n", encoding="utf-8"
        )
        report = check_structure(scan_docs(tmp_path))
        unmounted = [
            f for f in report.findings
            if f.code == structure_mod.CODE_UNMOUNTED and f.file == "loose.md"
        ]
        assert unmounted

    def test_unclassified_warn(self, tmp_path):
        _build_standard_tree(tmp_path)
        (tmp_path / "loose.md").write_text(
            "# 游离页\n\n首段。\n", encoding="utf-8"
        )
        report = check_structure(scan_docs(tmp_path))
        warns = [
            f for f in report.findings
            if f.code == structure_mod.CODE_UNCLASSIFIED
            and f.file == "loose.md"
        ]
        assert warns

    def test_type_conflict(self, tmp_path):
        (tmp_path / "tutorial").mkdir()
        (tmp_path / "tutorial" / "a.md").write_text(
            "---\ndiataxis: reference\n---\n# 页\n\n首段。\n",
            encoding="utf-8",
        )
        report = check_structure(scan_docs(tmp_path))
        conflicts = [
            f for f in report.findings
            if f.code == structure_mod.CODE_TYPE_CONFLICT
        ]
        assert conflicts


# ── 元数据漂移 ──────────────────────────────────────────────

class TestMetadataDrift:

    def test_drift_detector(self):
        assert _is_drift_field("qw-pages:version")
        assert _is_drift_field("deployment-id")
        assert _is_drift_field("published-at")
        assert not _is_drift_field("canonical")

    def test_drift_field_error(self, tmp_path):
        (tmp_path / "a.md").write_text(
            "# 页\n\n首段。\n\n"
            '<meta name="qw-pages:version" content="1.0">\n',
            encoding="utf-8",
        )
        report = check_metadata_drift(scan_docs(tmp_path))
        drifts = [f for f in report.findings if "DRIFT" in f.code]
        assert drifts and drifts[0].severity == "error"

    def test_stable_only_passes(self, tmp_path):
        (tmp_path / "a.md").write_text(
            "---\ntitle: 干净页\ncanonical: https://x.io/a\n---\n"
            "# 页\n\n首段。\n",
            encoding="utf-8",
        )
        report = check_metadata_drift(scan_docs(tmp_path))
        assert not report.errors

    def test_nonstandard_warn(self, tmp_path):
        (tmp_path / "a.md").write_text(
            "---\ncustomfield: abc\n---\n# 页\n\n首段。\n",
            encoding="utf-8",
        )
        report = check_metadata_drift(scan_docs(tmp_path))
        assert any(f.code.endswith("NONSTANDARD") for f in report.findings)

    def test_canonical_mismatch(self, tmp_path):
        (tmp_path / "a.md").write_text(
            "---\ncanonical: https://other.io/a\n---\n# 页\n\n首段。\n",
            encoding="utf-8",
        )
        config = DocsProductConfig(canonical_base="https://x.io")
        report = check_metadata_drift(scan_docs(tmp_path), config)
        assert any(f.code.endswith("CANONICAL") for f in report.errors)

    def test_config_from_toml(self, tmp_path):
        cfg_path = tmp_path / "cfg.toml"
        cfg_path.write_text(
            '[docs-as-product]\ncanonical_base = "https://x.io"\n'
            'run_external = false\nstable_fields = ["a", "b"]\n',
            encoding="utf-8",
        )
        config = DocsProductConfig.from_toml(cfg_path)
        assert config.canonical_base == "https://x.io"
        assert config.run_external is False
        assert config.stable_fields == frozenset({"a", "b"})

    def test_config_missing_file(self, tmp_path):
        config = DocsProductConfig.from_toml(tmp_path / "none.toml")
        assert config.canonical_base == ""


# ── 质量门 ──────────────────────────────────────────────────

class TestQualityGates:

    def test_no_external(self, tmp_path):
        _build_standard_tree(tmp_path)
        report = check_quality_gates(tmp_path, run_external=False)
        g2 = [c for c in report.checks if c.gate == "G2"]
        assert g2 and all(c.passed for c in g2)

    def test_tool_missing_degrades(self, tmp_path, monkeypatch):
        _build_standard_tree(tmp_path)
        monkeypatch.setattr(
            "lib.docs_as_product.quality_gates._tool_available",
            lambda tool: False,
        )
        report = check_quality_gates(tmp_path, run_external=True)
        # 工具缺失全部降级 WARN，无外部失败 error
        assert not report.errors

    def test_g2_bad_lead_and_heading(self, tmp_path):
        (tmp_path / "a.md").write_text(
            "# 页\n\n## 子标题\n\n内容。\n", encoding="utf-8"
        )
        report = check_quality_gates(tmp_path, run_external=False)
        assert any(f.code == "DAP-G2-LEAD" for f in report.findings)
        # # 页 → ## 子标题 不跳跃；构造跳跃
        (tmp_path / "b.md").write_text(
            "# 页B\n\n### 跳级\n", encoding="utf-8"
        )
        report = check_quality_gates(tmp_path, run_external=False)
        assert any(f.code == "DAP-G2-HEADING" for f in report.findings)

    def test_g3_handwritten_signature(self, tmp_path):
        (tmp_path / "reference").mkdir()
        (tmp_path / "reference" / "h.md").write_text(
            "# 手写参考\n\n首段。\n\n## API\n\nmy_func(arg)\n",
            encoding="utf-8",
        )
        report = check_quality_gates(tmp_path, run_external=False)
        assert any(f.code == "DAP-G3-HANDWRITTEN" for f in report.findings)

    def test_g4_multi_unit(self, tmp_path):
        sections = "\n".join(f"## 单元{i}\n\n内容。" for i in range(7))
        (tmp_path / "a.md").write_text(f"# 多单元\n\n首段。\n\n{sections}\n",
                                       encoding="utf-8")
        report = check_quality_gates(tmp_path, run_external=False)
        assert any(f.code == "DAP-G4-MULTIUNIT" for f in report.findings)

    def test_tool_available(self):
        assert _tool_available("definitely-no-such-tool-xyz-123") is False

    def test_run_command_timeout(self, monkeypatch):
        import subprocess

        def raise_timeout(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="x", timeout=1)

        monkeypatch.setattr(subprocess, "run", raise_timeout)
        code, output = _run_command("x", 1)
        assert code == 124 and "超时" in output

    def test_run_command_oserror(self, monkeypatch):
        import subprocess

        def raise_oserror(*args, **kwargs):
            raise OSError("boom")

        monkeypatch.setattr(subprocess, "run", raise_oserror)
        code, output = _run_command("x", 1)
        assert code == 1 and "失败" in output


# ── 读者契约 ────────────────────────────────────────────────

CONTRACT_MD = """# 读者契约

## Tutorial 读者

- [ ] 完成安装验收

承诺 <15 分钟内完成。

## How-to 读者

1. 完成配置任务

## Reference 读者

- [ ] 查阅 API

docstring 覆盖率 ≥90%。

## Explanation 读者

- [ ] 理解设计背景
"""


class TestReaderContract:

    def test_missing_contract(self, tmp_path):
        report = check_reader_contract(tmp_path)
        assert not report.passed
        assert any(f.code == "DAP-CONTRACT-MISSING" for f in report.findings)

    def test_valid_contract(self, tmp_path):
        (tmp_path / "reader-contract.md").write_text(CONTRACT_MD, encoding="utf-8")
        report = check_reader_contract(tmp_path)
        assert report.passed

    def test_find_contract_file(self, tmp_path):
        assert find_contract_file(tmp_path) is None
        (tmp_path / "reader-contract.md").write_text(CONTRACT_MD, encoding="utf-8")
        assert find_contract_file(tmp_path).name == "reader-contract.md"

    def test_missing_reader_section(self, tmp_path):
        (tmp_path / "reader-contract.md").write_text(
            "# 读者契约\n\n## Tutorial 读者\n\n- [ ] 任务\n",
            encoding="utf-8",
        )
        report = check_reader_contract(tmp_path)
        assert any(f.code == "DAP-CONTRACT-READER" for f in report.findings)

    def test_missing_task(self, tmp_path):
        (tmp_path / "reader-contract.md").write_text(
            "# 读者契约\n\n## Tutorial 读者\n\n仅描述性文字，无任何可执行内容。\n\n"
            "## How-to 读者\n\n- [ ] t\n\n"
            "## Reference 读者\n\n- [ ] t\n\n"
            "## Explanation 读者\n\n- [ ] t\n",
            encoding="utf-8",
        )
        report = check_reader_contract(tmp_path)
        assert any(f.code == "DAP-CONTRACT-TASK" for f in report.findings)

    def test_missing_time_commitment(self, tmp_path):
        text = CONTRACT_MD.replace("承诺 <15 分钟内完成。", "无时长承诺。")
        (tmp_path / "reader-contract.md").write_text(text, encoding="utf-8")
        report = check_reader_contract(tmp_path)
        assert any(f.code == "DAP-CONTRACT-TIME" for f in report.findings)

    def test_missing_docstring_commitment(self, tmp_path):
        text = CONTRACT_MD.replace("docstring 覆盖率 ≥90%。", "无覆盖率承诺。")
        (tmp_path / "reader-contract.md").write_text(text, encoding="utf-8")
        report = check_reader_contract(tmp_path)
        assert any(f.code == "DAP-CONTRACT-DOCSTRING" for f in report.findings)

    def test_table_form_contract(self, tmp_path):
        table = (
            "# 读者契约\n\n"
            "| 读者 | 验收任务 |\n|---|---|\n"
            "| tutorial | - [ ] 完成 |\n"
            "| how-to | - [ ] 完成 |\n"
            "| reference | - [ ] 完成 |\n"
            "| explanation | - [ ] 完成 |\n"
        )
        (tmp_path / "reader-contract.md").write_text(table, encoding="utf-8")
        report = check_reader_contract(tmp_path)
        # 表格行被识别为四类读者齐全（无 READER finding）
        assert not [
            f for f in report.findings if f.code == "DAP-CONTRACT-READER"
        ]


# ── 指标脚手架 ──────────────────────────────────────────────

class TestMetrics:

    def test_scaffold_creates_files(self, tmp_path):
        out = tmp_path / "metrics"
        created = scaffold_metrics(tmp_path, out)
        assert len(created) == 2
        records = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
        assert [r["id"] for r in records] == ["M1", "M2", "M3", "M4", "M5"]
        assert all(r["owner"] == "TODO" for r in records)

    def test_scaffold_idempotent(self, tmp_path):
        scaffold_metrics(tmp_path, tmp_path / "m")
        second = scaffold_metrics(tmp_path, tmp_path / "m")
        assert second == []


# ── 报告与模型序列化 ────────────────────────────────────────

class TestReporter:

    def test_reports_json_schema(self, tmp_path):
        _build_standard_tree(tmp_path)
        tree = scan_docs(tmp_path)
        payload = reporter_mod.reports_to_json(
            [check_structure(tree), check_metadata_drift(tree)]
        )
        assert "per_gate" in payload
        assert "findings" in payload
        for finding in payload["findings"]:
            assert "severity" in finding

    def test_report_json_serializable(self, tmp_path):
        _build_standard_tree(tmp_path)
        report = check_structure(scan_docs(tmp_path))
        json.dumps(report.to_dict(), ensure_ascii=True)


# ── CLI ─────────────────────────────────────────────────────

class TestCli:

    def test_structure_cli(self, tmp_path, monkeypatch, capsys):
        _build_standard_tree(tmp_path)
        monkeypatch.setattr(
            sys, "argv",
            ["docs-as-product", "structure", "--path", str(tmp_path),
             "--json"],
        )
        from lib.docs_as_product import cli as cli_mod

        with pytest.raises(SystemExit) as exc:
            cli_mod.main()
        assert exc.value.code in (0, 1)
        payload = json.loads(capsys.readouterr().out)
        assert "findings" in payload

    def test_metrics_cli(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(
            sys, "argv",
            ["docs-as-product", "metrics",
             "--scaffold", str(tmp_path / "m"), "--json"],
        )
        from lib.docs_as_product import cli as cli_mod

        with pytest.raises(SystemExit) as exc:
            cli_mod.main()
        assert exc.value.code == 0
        payload = json.loads(capsys.readouterr().out)
        assert len(payload["created"]) == 2

    def test_all_cli_no_external(self, tmp_path, monkeypatch):
        _build_standard_tree(tmp_path)
        monkeypatch.setattr(
            sys, "argv",
            ["docs-as-product", "all", "--path", str(tmp_path),
             "--no-external"],
        )
        from lib.docs_as_product import cli as cli_mod

        with pytest.raises(SystemExit) as exc:
            cli_mod.main()
        assert exc.value.code in (0, 1)


# ── 扫描期日志抑制的作用域 ──────────────────────────────────


@pytest.fixture
def frontmatter_logger():
    """把 lib.frontmatter 归零到 NOTSET，测试后还原，避免受执行顺序影响。"""
    logger = logging.getLogger("lib.frontmatter")
    original = logger.level
    logger.setLevel(logging.NOTSET)
    yield logger
    logger.setLevel(original)


def _write_missing_ref_doc(tmp_path) -> None:
    (tmp_path / "a.md").write_text(
        '---\nx-toml-ref: "missing.toml"\ntitle: 测试\n---\n\n正文\n',
        encoding="utf-8",
    )


class TestFrontmatterWarningScope:
    """发现层的日志抑制只能作用于扫描动作，不得改进程级 logger 配置。"""

    def test_scan_restores_logger_level(self, tmp_path, frontmatter_logger):
        _write_missing_ref_doc(tmp_path)
        scan_docs(tmp_path)
        assert frontmatter_logger.level == logging.NOTSET

    def test_scan_suppresses_missing_toml_warning(self, tmp_path, frontmatter_logger, caplog):
        _write_missing_ref_doc(tmp_path)
        with caplog.at_level(logging.WARNING):
            scan_docs(tmp_path)
        assert "不存在" not in caplog.text

    def test_warning_visible_after_scan(self, tmp_path, frontmatter_logger, caplog):
        _write_missing_ref_doc(tmp_path)
        scan_docs(tmp_path)
        caplog.set_level(logging.WARNING)
        assert load_external_toml("missing.toml", tmp_path) is None
        assert "不存在" in caplog.text
