"""audit-wiki-count-declarations.py 单元测试。

覆盖场景：
- normalize: 空白与中英文标点归一化
- count_fact_ids: rows 与 unique 分离、重复编号登记
- analyze_quotes: 无源文本的计数、有源文本的逐字命中与最短长度阈值
- longest_common_substring_len: 常规/无交集/空文本
- scan_for_secret: 文本文件命中、非文本后缀跳过、空口令
- evaluate: 引用红线只判「逐字命中源文本」的引语、公共子串红线、凭据红线、重复编号告警
- main: 端到端退出码（0/2）与 --json 输出
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
    "audit_wiki_count_declarations",
    _SCRIPTS_DIR / "audit-wiki-count-declarations.py",
)
awcd = importlib.util.module_from_spec(_spec)
sys.modules["audit_wiki_count_declarations"] = awcd
_spec.loader.exec_module(awcd)


# ---- 夹具 ----

def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _demo_wiki(root: Path) -> Path:
    _write(root / "index.md", "# 索引\n\n「现金流」与「资产负债表」\n")
    _write(
        root / "facts.md",
        "| 编号 | 事实 |\n|---|---|\n| F-001 | 甲 |\n| F-002 | 乙 |\n",
    )
    return root


# ---- normalize ----

def test_normalize_strips_whitespace_and_punctuation():
    assert awcd.normalize("融资 断流，能撑 几个月？") == "融资断流能撑几个月"


def test_normalize_handles_fullwidth_and_symbols():
    assert awcd.normalize("「现金流」（正/负）") == "现金流正负"


# ---- count_fact_ids ----

def test_count_fact_ids_separates_rows_and_unique():
    texts = [
        "| F-001 | 甲 |\n| F-002 | 乙 |\n",
        "| F-001 | 复述 |\n| F-001 | 再复述 |\n",
    ]
    result = awcd.count_fact_ids(texts)
    assert result["rows"] == 4
    assert result["unique"] == 2
    assert result["duplicates"] == {"F-001": 3}


def test_count_fact_ids_ignores_inline_mentions():
    # 行内提及（非表格首列）不计入事实台账
    assert awcd.count_fact_ids(["见 F-001 条"])["rows"] == 0
    assert awcd.count_fact_ids(["待核验：| F-001 | 复述 |"])["rows"] == 0


# ---- analyze_quotes ----

def test_analyze_quotes_counts_and_dedupes():
    text = "「现金流」和「现金流」，还有「资产负债表」"
    result = awcd.analyze_quotes(text)
    assert result["quotes_total"] == 3
    assert result["quotes_unique"] == 2
    assert result["max_quote_len"] == 5
    assert "quotes_hit_source" not in result


def test_analyze_quotes_marks_verbatim_hits():
    source = "我的经营性现金流是正还是负"
    wiki = "「经营性现金流」是核心，另有「完全不存在于源文的说法」"
    result = awcd.analyze_quotes(wiki, source, min_len=4)
    assert result["quotes_hit_source"] == 1
    assert result["max_hit_quote_len"] == 6


def test_analyze_quotes_respects_min_len():
    source = "现金流为正"
    wiki = "「现金流」"
    result = awcd.analyze_quotes(wiki, source, min_len=8)
    assert result["quotes_hit_source"] == 0


# ---- longest_common_substring_len ----

def test_lcs_finds_longest_overlap():
    assert awcd.longest_common_substring_len("abcde", "zzcdezz") == 3


def test_lcs_without_overlap_is_zero():
    assert awcd.longest_common_substring_len("abc", "xyz") == 0


def test_lcs_with_empty_input_is_zero():
    assert awcd.longest_common_substring_len("", "abc") == 0
    assert awcd.longest_common_substring_len("abc", "") == 0


def test_find_lcs_reports_offending_file():
    source = "经营性现金流为正的公司才有议价能力"
    files = [
        ("concepts/a.md", "普通表述，无重合片段"),
        ("facts.md", "该讲认为经营性现金流为正的公司才有议价能力"),
    ]
    best = awcd.find_longest_common_substring(files, source)
    assert best["file"] == "facts.md"
    assert best["len"] == len(awcd.normalize(source))


# ---- scan_for_secret ----

def test_scan_for_secret_reports_relative_paths(tmp_path):
    _write(tmp_path / "a.md", "口令是 s3cret")
    _write(tmp_path / "sub" / "b.toml", "value = 's3cret'")
    _write(tmp_path / "c.bin", "s3cret")
    hits = awcd.scan_for_secret(tmp_path, "s3cret")
    assert sorted(hits) == ["a.md", str(Path("sub") / "b.toml")]


def test_scan_for_secret_without_password_finds_nothing(tmp_path):
    _write(tmp_path / "a.md", "任意内容")
    assert awcd.scan_for_secret(tmp_path, "") == []


# ---- evaluate ----

def _report(**overrides):
    report = {
        "wiki_root": "x",
        "files": 1,
        "bytes": 1,
        "facts": {"rows": 1, "unique": 1, "duplicates": {}},
        "quotes": {"quotes_total": 1, "quotes_unique": 1, "max_quote_len": 32},
        "secret_hits": [],
    }
    report.update(overrides)
    return report


def test_evaluate_does_not_judge_quote_length_without_source():
    failures, warnings = awcd.evaluate(_report(), 30)
    assert failures == []
    assert any("未提供源 PDF" in w for w in warnings)


def test_evaluate_flags_verbatim_quote_over_limit():
    report = _report(
        quotes={
            "quotes_total": 1,
            "quotes_unique": 1,
            "max_quote_len": 40,
            "quote_min_len": 8,
            "quotes_hit_source": 1,
            "quotes_hit_unique": 1,
            "max_hit_quote_len": 31,
        }
    )
    failures, _ = awcd.evaluate(report, 30)
    assert any("逐字引用最长 31 字" in f for f in failures)


def test_evaluate_flags_lcs_and_secret_hits():
    report = _report(
        longest_common_substring={"len": 30, "file": "facts.md"},
        secret_hits=["a.md"],
    )
    failures, _ = awcd.evaluate(report, 30)
    assert any("最长公共子串 30 字（facts.md）" in f for f in failures)
    assert any("凭据残留" in f for f in failures)


def test_evaluate_warns_on_duplicate_ids():
    report = _report(facts={"rows": 4, "unique": 2, "duplicates": {"F-001": 3}})
    _, warnings = awcd.evaluate(report, 30)
    assert any("编号重复 1 个" in w for w in warnings)


# ---- main 端到端 ----

def test_main_clean_wiki_exits_zero(tmp_path):
    root = _demo_wiki(tmp_path / "wiki")
    assert awcd.main(["--wiki", str(root), "--skip-links"]) == 0


def test_main_missing_dir_exits_two(tmp_path):
    with pytest.raises(SystemExit) as exc:
        awcd.main(["--wiki", str(tmp_path / "nope"), "--skip-links"])
    assert exc.value.code == 2


def test_main_without_markdown_exits_two(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(SystemExit) as exc:
        awcd.main(["--wiki", str(empty), "--skip-links"])
    assert exc.value.code == 2


def test_main_json_output_is_parseable(tmp_path, capsys):
    root = _demo_wiki(tmp_path / "wiki")
    assert awcd.main(["--wiki", str(root), "--skip-links", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["files"] == 2
    assert payload["facts"]["unique"] == 2
    assert payload["failures"] == []
