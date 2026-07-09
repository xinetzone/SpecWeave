"""generate-knowledge-graph.py 单元测试。"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

_spec = importlib.util.spec_from_file_location(
    "generate_knowledge_graph", _SCRIPTS_DIR / "generate-knowledge-graph.py"
)
gkg = importlib.util.module_from_spec(_spec)
sys.modules["generate_knowledge_graph"] = gkg
_spec.loader.exec_module(gkg)

from generate_knowledge_graph import (
    _parse_markdown_table, _extract_domain, _extract_rating, INLINE_LINK_RE,
    deduplicate_nodes, deduplicate_edges, _match_period, _parse_time_to_sort_key,
    TEMPLATE_PATH, generate_html, NODE_CONCEPT, NODE_PERSON, NODE_PERIOD
)


class TestParseMarkdownTable:
    def test_basic_table_parsing(self):
        md = """## 测试表格
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| a   | b   | c   |
| d   | e   | f   |
"""
        table = _parse_markdown_table(md, "## 测试表格")
        assert len(table) == 3
        assert table[0] == ["列1", "列2", "列3"]
        assert table[1] == ["a", "b", "c"]
        assert table[2] == ["d", "e", "f"]

    def test_empty_table(self):
        md = "## 空表格\n没有表格内容"
        table = _parse_markdown_table(md, "## 空表格")
        assert table == []


class TestExtractDomain:
    def test_philosophy(self):
        assert _extract_domain("哲学/形而上学") == "哲学"

    def test_physics(self):
        assert _extract_domain("物理学/量子力学") == "物理学"

    def test_methodology(self):
        assert _extract_domain("方法论/思维模型") == "方法论"

    def test_cognitive_science(self):
        assert _extract_domain("认知科学/心理学") == "认知科学"

    def test_general(self):
        assert _extract_domain("通用/其他") == "通用"

    def test_fallback(self):
        assert _extract_domain("经济学/微观") == "经济学"


class TestExtractRating:
    def test_green_a(self):
        assert _extract_rating("🟢 核心概念") == "A"
        assert _extract_rating("A级 重要") == "A"

    def test_blue_b(self):
        assert _extract_rating("🔵 相关概念") == "B"
        assert _extract_rating("B级 一般") == "B"

    def test_default_b(self):
        assert _extract_rating("无标记") == "B"


class TestInlineLinkRe:
    def test_basic_link(self):
        text = "这是一个[概念](concept.md)链接"
        matches = list(INLINE_LINK_RE.finditer(text))
        assert len(matches) == 1
        assert matches[0].group(1) == "概念"
        assert matches[0].group(2) == "concept.md"

    def test_multiple_links(self):
        text = "[第一性原理](1.md)和[还原论](2.md)"
        matches = list(INLINE_LINK_RE.finditer(text))
        assert len(matches) == 2
        assert matches[0].group(1) == "第一性原理"
        assert matches[1].group(1) == "还原论"


class TestDeduplicateNodes:
    def test_duplicate_ids_removed(self):
        nodes = [
            {'id': 'n1', 'label': 'Node 1'},
            {'id': 'n2', 'label': 'Node 2'},
            {'id': 'n1', 'label': 'Node 1 Duplicate'},
        ]
        deduped = deduplicate_nodes(nodes)
        assert len(deduped) == 2
        ids = [n['id'] for n in deduped]
        assert ids == ['n1', 'n2']
        assert deduped[0]['label'] == 'Node 1'


class TestDeduplicateEdges:
    def test_duplicate_edges_removed(self):
        edges = [
            {'source': 's1', 'target': 't1', 'relation': 'related_to'},
            {'source': 's2', 'target': 't2', 'relation': 'influenced'},
            {'source': 's1', 'target': 't1', 'relation': 'related_to'},
        ]
        deduped = deduplicate_edges(edges)
        assert len(deduped) == 2


class TestMatchPeriod:
    def test_ancient(self):
        pmap = {'古希腊哲学时期': 'period_ancient'}
        assert _match_period("古希腊", pmap) == 'period_ancient'

    def test_modern(self):
        pmap = {'近代哲学与科学革命': 'period_modern'}
        assert _match_period("近代", pmap) == 'period_modern'

    def test_modern_science(self):
        pmap = {'现代科学时期': 'period_modern_science'}
        assert _match_period("现代科学", pmap) == 'period_modern_science'
        assert _match_period("现代", pmap) == 'period_modern_science'

    def test_contemporary(self):
        pmap = {'当代商业与方法论时期': 'period_contemporary'}
        assert _match_period("当代", pmap) == 'period_contemporary'

    def test_no_match(self):
        pmap = {}
        assert _match_period("未知时期", pmap) is None
        assert _match_period("", pmap) is None


class TestParseTimeToSortKey:
    def test_bc_century(self):
        assert _parse_time_to_sort_key("约前6世纪") == -600

    def test_ad_century(self):
        assert _parse_time_to_sort_key("17世纪") == 1700

    def test_year(self):
        assert _parse_time_to_sort_key("1637年") == 1637

    def test_bc_year(self):
        assert _parse_time_to_sort_key("前300年") == -300

    def test_decade(self):
        assert _parse_time_to_sort_key("2020年代") == 2020

    def test_empty(self):
        assert _parse_time_to_sort_key("") == 99999


class TestTemplateFile:
    def test_template_exists(self):
        assert TEMPLATE_PATH.exists()

    def test_template_contains_placeholders(self):
        content = TEMPLATE_PATH.read_text(encoding='utf-8')
        assert '__NODES_DATA__' in content
        assert '__EDGES_DATA__' in content
        assert '__NODE_COUNT__' in content
        assert '__EDGE_COUNT__' in content
        assert 'vis-network' in content


class TestGenerateHtml:
    def test_generate_html_creates_valid_file(self, tmp_path):
        nodes = [
            {'id': 'c1', 'label': '第一性原理', 'type': NODE_CONCEPT, 'domain': '哲学', 'definition': '基本原理', 'source_url': '', 'rating': 'A', 'english_name': 'First Principles'},
            {'id': 'p1', 'label': '亚里士多德', 'type': NODE_PERSON, 'period': '古希腊', 'contribution': '提出archē', 'source_url': ''},
        ]
        edges = [
            {'source': 'p1', 'target': 'c1', 'relation': 'contributed'},
        ]
        output = tmp_path / "test-graph.html"
        generate_html(nodes, edges, output)
        assert output.exists()
        assert output.stat().st_size > 0
        content = output.read_text(encoding='utf-8')
        assert 'vis-network' in content
        assert 'cdn.jsdelivr.net' in content
        assert '第一性原理' in content
        assert '亚里士多德' in content
        assert output.stat().st_size > 1000
