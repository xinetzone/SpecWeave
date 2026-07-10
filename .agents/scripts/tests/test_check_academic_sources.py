"""check-academic-sources.py 单元测试。

测试覆盖：
- DOI/arXiv ID 正则提取（各种格式）
- DOI 规范化函数
- 标题模糊匹配（完全一致/近似/不匹配）
- CrossRef API 响应解析（mock数据）
- 缓存读写逻辑
"""

import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

_SPEC_PATH = SCRIPTS_DIR / "check-academic-sources.py"
_spec = importlib.util.spec_from_file_location("check_academic_sources", _SPEC_PATH)
cas = importlib.util.module_from_spec(_spec)
sys.modules["check_academic_sources"] = cas
_spec.loader.exec_module(cas)


class TestDOINormalization:
    """normalize_doi 函数测试。"""

    def test_bare_doi(self):
        assert cas.normalize_doi("10.1207/s15516709cog0702_3") == "10.1207/s15516709cog0702_3"

    def test_doi_url(self):
        assert cas.normalize_doi("https://doi.org/10.1207/s15516709cog0702_3") == "10.1207/s15516709cog0702_3"

    def test_dx_doi_url(self):
        assert cas.normalize_doi("http://dx.doi.org/10.1103/RevModPhys.71.1253") == "10.1103/revmodphys.71.1253"

    def test_doi_with_trailing_paren(self):
        assert cas.normalize_doi("10.1016/j.tics.2003.08.012)") == "10.1016/j.tics.2003.08.012"

    def test_doi_with_trailing_semicolon(self):
        assert cas.normalize_doi("10.1207/s15516709cog1202_4;") == "10.1207/s15516709cog1202_4"

    def test_doi_with_trailing_period(self):
        assert cas.normalize_doi("10.1126/science.185.4157.1124.") == "10.1126/science.185.4157.1124"

    def test_doi_case_insensitive(self):
        assert cas.normalize_doi("10.1126/SCIENCE.185.4157.1124") == "10.1126/science.185.4157.1124"


class TestTextNormalization:
    """normalize_text 和 text_similarity 测试。"""

    def test_normalize_lowercase(self):
        assert cas.normalize_text("Hello World") == "hello world"

    def test_normalize_punctuation(self):
        result = cas.normalize_text("Hello, World! How are you?")
        assert "," not in result
        assert "!" not in result
        assert "?" not in result

    def test_normalize_whitespace(self):
        assert cas.normalize_text("  hello   world  ") == "hello world"

    def test_similarity_identical(self):
        assert cas.text_similarity("Structure-mapping: A theoretical framework for analogy",
                                    "Structure-mapping: A theoretical framework for analogy") == 1.0

    def test_similarity_close(self):
        score = cas.text_similarity(
            "In two minds: dual-process accounts of reasoning",
            "In two minds dual process accounts of reasoning"
        )
        assert score >= 0.85

    def test_similarity_different(self):
        score = cas.text_similarity(
            "Structure mapping theory of analogy",
            "The theory of general relativity quantum gravity"
        )
        assert score < 0.5


class TestCrossRefMessageParsing:
    """parse_crossref_message 函数测试。"""

    def test_parse_valid_message(self):
        message = {
            "title": ["In two minds: dual-process accounts of reasoning"],
            "author": [
                {"given": "Jonathan St. B. T.", "family": "Evans"},
                {"given": "Other", "family": "Author"},
            ],
            "issued": {"date-parts": [[2003]]},
            "container-title": ["Trends in Cognitive Sciences"],
            "type": "journal-article",
            "publisher": "Elsevier",
        }
        result = cas.parse_crossref_message("10.1016/j.tics.2003.08.012", message)
        assert result["exists"] is True
        assert result["title"] == "In two minds: dual-process accounts of reasoning"
        assert result["first_author_surname"] == "evans"
        assert result["year"] == 2003
        assert result["journal"] == "Trends in Cognitive Sciences"
        assert result["type"] == "journal-article"

    def test_parse_message_no_title(self):
        message = {
            "author": [{"given": "D.", "family": "Kahneman"}],
            "issued": {"date-parts": [[2011]]},
        }
        result = cas.parse_crossref_message("test-doi", message)
        assert result["exists"] is True
        assert result["title"] is None
        assert result["first_author_surname"] == "kahneman"
        assert result["year"] == 2011

    def test_parse_message_no_authors(self):
        message = {
            "title": ["Some Paper"],
            "issued": {"date-parts": [[2020]]},
        }
        result = cas.parse_crossref_message("test-doi", message)
        assert result["exists"] is True
        assert result["first_author_surname"] is None
        assert result["authors"] == []


class TestMetadataComparison:
    """compare_metadata 函数测试。"""

    def test_year_match(self):
        doc = {"year": 2003, "title": None, "first_author_surname": None}
        api = {"year": 2003, "title": None, "first_author_surname": None, "authors": [], "journal": None}
        issues = cas.compare_metadata(doc, api)
        year_issues = [i for i in issues if i[0] == "year"]
        assert len(year_issues) == 1
        assert year_issues[0][1] == cas.STATUS_PASS

    def test_year_mismatch_is_warn(self):
        doc = {"year": 2011, "title": None, "first_author_surname": None}
        api = {"year": 2003, "title": None, "first_author_surname": None, "authors": [], "journal": None}
        issues = cas.compare_metadata(doc, api)
        year_issues = [i for i in issues if i[0] == "year"]
        assert len(year_issues) == 1
        assert year_issues[0][1] == cas.STATUS_WARN
        assert "多篇论文" in year_issues[0][2]

    def test_year_missing_in_doc_is_info(self):
        doc = {"year": None, "title": None, "first_author_surname": None}
        api = {"year": 2003, "title": None, "first_author_surname": None, "authors": [], "journal": None}
        issues = cas.compare_metadata(doc, api)
        year_issues = [i for i in issues if i[0] == "year"]
        assert len(year_issues) == 1
        assert year_issues[0][1] == cas.STATUS_INFO

    def test_title_match(self):
        doc = {"year": None, "title": "In two minds: dual-process accounts", "first_author_surname": None}
        api = {"year": None, "title": "In two minds: dual-process accounts of reasoning",
               "first_author_surname": None, "authors": [], "journal": None}
        issues = cas.compare_metadata(doc, api)
        title_issues = [i for i in issues if i[0] == "title"]
        assert len(title_issues) == 1

    def test_author_match(self):
        doc = {"year": None, "title": None, "first_author_surname": "evans"}
        api = {"year": None, "title": None, "first_author_surname": "evans", "authors": ["J. Evans"], "journal": None}
        issues = cas.compare_metadata(doc, api)
        author_issues = [i for i in issues if i[0] == "author"]
        assert len(author_issues) == 1
        assert author_issues[0][1] == cas.STATUS_PASS

    def test_author_case_insensitive(self):
        doc = {"year": None, "title": None, "first_author_surname": "Kahneman"}
        api = {"year": None, "title": None, "first_author_surname": "kahneman", "authors": ["D. Kahneman"], "journal": None}
        issues = cas.compare_metadata(doc, api)
        author_issues = [i for i in issues if i[0] == "author"]
        assert len(author_issues) == 1
        assert author_issues[0][1] == cas.STATUS_PASS


class TestCacheOperations:
    """缓存读写测试。"""

    def test_load_nonexistent_cache(self, tmp_path):
        result = cas.load_cache(tmp_path)
        assert result == {}

    def test_save_and_load_cache(self, tmp_path):
        cache_data = {
            "10.1234/test": {
                "checked_at": datetime.now().isoformat(),
                "api_metadata": {"doi": "10.1234/test", "exists": True},
            }
        }
        cas.save_cache(tmp_path, cache_data)
        loaded = cas.load_cache(tmp_path)
        assert "10.1234/test" in loaded
        assert loaded["10.1234/test"]["api_metadata"]["exists"] is True
        assert "_metadata" in loaded

    def test_cache_validity_fresh(self):
        entry = {"checked_at": datetime.now().isoformat()}
        assert cas.is_cache_valid(entry, ttl_days=7) is True

    def test_cache_validity_expired(self):
        entry = {"checked_at": (datetime.now() - timedelta(days=10)).isoformat()}
        assert cas.is_cache_valid(entry, ttl_days=7) is False

    def test_cache_validity_missing_date(self):
        assert cas.is_cache_valid({}) is False


class TestDocMetadataExtraction:
    """extract_doc_metadata 函数测试。"""

    def test_extract_year_before_doi(self):
        context = 'Evans, J. S. B. T. (2003). In two minds. DOI: 10.1016/j.tics.2003.08.012'
        meta = cas.extract_doc_metadata(context)
        assert meta["year"] == 2003

    def test_no_year_in_context(self):
        context = 'DOI: 10.1234/test'
        meta = cas.extract_doc_metadata(context)
        assert meta["year"] is None

    def test_year_not_matching_volume(self):
        context = 'Science 185(4157), 1124-1131. DOI: 10.1126/science.185.4157.1124'
        meta = cas.extract_doc_metadata(context)
        assert meta["year"] is None or meta["year"] == 1124 or meta["year"] not in [4157]


class TestArXivValidation:
    """arXiv ID 格式校验测试。"""

    def test_valid_new_format(self):
        ident = {"type": "arxiv", "id": "1106.0702", "file": "test.md", "line": 1, "context": ""}
        result = cas.verify_arxiv(ident)
        assert result["overall_status"] == cas.STATUS_PASS

    def test_valid_old_format(self):
        ident = {"type": "arxiv", "id": "hep-th/9711200", "file": "test.md", "line": 1, "context": ""}
        result = cas.verify_arxiv(ident)
        assert result["overall_status"] == cas.STATUS_PASS

    def test_valid_versioned(self):
        ident = {"type": "arxiv", "id": "1106.0702v2", "file": "test.md", "line": 1, "context": ""}
        result = cas.verify_arxiv(ident)
        assert result["overall_status"] == cas.STATUS_PASS


class TestIdentifierExtraction:
    """从Markdown文本中提取ID测试。"""

    def test_extract_bare_doi(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("See DOI: 10.1207/s15516709cog0702_3 for details.", encoding="utf-8")
        ids = cas.extract_identifiers_from_file(md)
        dois = [i for i in ids if i["type"] == "doi"]
        assert len(dois) == 1
        assert dois[0]["id"] == "10.1207/s15516709cog0702_3"
        assert dois[0]["line"] == 1

    def test_extract_doi_url(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("Available at https://doi.org/10.1126/science.185.4157.1124.", encoding="utf-8")
        ids = cas.extract_identifiers_from_file(md)
        dois = [i for i in ids if i["type"] == "doi"]
        assert len(dois) == 1
        assert dois[0]["id"] == "10.1126/science.185.4157.1124"

    def test_extract_dx_doi_url(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("See http://dx.doi.org/10.1103/RevModPhys.71.1253", encoding="utf-8")
        ids = cas.extract_identifiers_from_file(md)
        dois = [i for i in ids if i["type"] == "doi"]
        assert len(dois) == 1
        assert dois[0]["id"] == "10.1103/revmodphys.71.1253"

    def test_extract_arxiv(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("arXiv:1106.0702", encoding="utf-8")
        ids = cas.extract_identifiers_from_file(md)
        arxivs = [i for i in ids if i["type"] == "arxiv"]
        assert len(arxivs) == 1
        assert arxivs[0]["id"] == "1106.0702"

    def test_extract_arxiv_url(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("https://arxiv.org/abs/1106.0702", encoding="utf-8")
        ids = cas.extract_identifiers_from_file(md)
        arxivs = [i for i in ids if i["type"] == "arxiv"]
        assert len(arxivs) == 1
        assert arxivs[0]["id"] == "1106.0702"

    def test_no_duplicate_dois(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("""DOI: 10.1234/test
        See also https://doi.org/10.1234/test for reference.""", encoding="utf-8")
        ids = cas.extract_identifiers_from_file(md)
        dois = [i for i in ids if i["type"] == "doi"]
        assert len(dois) == 1

    def test_doi_with_parentheses_in_text(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("DOI: 10.1016/j.tics.2003.08.012 (Evans, 2003)", encoding="utf-8")
        ids = cas.extract_identifiers_from_file(md)
        dois = [i for i in ids if i["type"] == "doi"]
        assert len(dois) == 1
        assert dois[0]["id"] == "10.1016/j.tics.2003.08.012"

    def test_no_identifiers(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Just a regular markdown\n\nNo DOIs here.", encoding="utf-8")
        ids = cas.extract_identifiers_from_file(md)
        assert len(ids) == 0
