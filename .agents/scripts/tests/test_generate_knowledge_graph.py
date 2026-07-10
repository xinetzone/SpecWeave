"""generate-knowledge-graph.py / generate-graph.py 单元测试。"""

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

# ==================== generate-graph.py (通用知识图谱) CI 兼容性测试 ====================

from lib.knowledge_graph_core import load_config, KnowledgeGraphBuilder, build_graph_from_config

_PROJECT_ROOT = _SCRIPTS_DIR.parent.parent


class TestTomliFallback:
    """验证 tomli fallback 机制在 CI 环境中正常工作。"""

    def test_toml_import_uses_tomli_first(self):
        """确认导入链路优先使用 tomli（如已安装），否则回退 tomllib。"""
        import importlib
        import lib.knowledge_graph_core as kgc
        # 重新加载以触发导入逻辑
        importlib.reload(kgc)
        assert kgc.tomllib is not None
        # tomli 或 tomllib 都可以正常导入
        assert hasattr(kgc.tomllib, 'load')

    def test_load_adversarial_review_config(self):
        """验证对抗性审查配置能被正确加载（曾因中文内联表导致 tomllib 报错）。"""
        config_path = _PROJECT_ROOT / "docs/knowledge/learning/02-agent-engineering-methodology/adversarial-review-wiki/knowledge-graph-config.toml"
        if not config_path.exists():
            pytest.skip("对抗性审查配置文件不存在")
        config = load_config(config_path)
        assert 'graph' in config
        assert 'node_types' in config['graph']
        assert 'concept' in config['graph']['node_types']
        # 验证 extra_links 格式正确
        auto_rels = config.get('auto_relations', [])
        defined_in = [r for r in auto_rels if r.get('type') == 'defined_in']
        assert len(defined_in) > 0, "应存在 defined_in 自动关系"
        extra_links = defined_in[0].get('extra_links', [])
        assert len(extra_links) >= 5, f"extra_links 应有至少5条映射，实际 {len(extra_links)} 条"

    def test_load_first_principles_config(self):
        """验证第一性原理配置能被正确加载（曾因 concept_doc_map 多行内联表导致报错）。"""
        config_path = _PROJECT_ROOT / "docs/knowledge/learning/first-principles/knowledge-graph-config.toml"
        if not config_path.exists():
            pytest.skip("第一性原理配置文件不存在")
        config = load_config(config_path)
        assert 'graph' in config
        assert 'node_types' in config['graph']
        # 验证 extra_links 已合并 concept_doc_map 内容
        auto_rels = config.get('auto_relations', [])
        defined_in = [r for r in auto_rels if r.get('type') == 'defined_in']
        assert len(defined_in) > 0
        extra_links = defined_in[0].get('extra_links', [])
        assert len(extra_links) >= 20, f"extra_links 应有至少20条映射，实际 {len(extra_links)} 条"


class TestKnowledgeGraphBuilderCI:
    """验证 KnowledgeGraphBuilder 在 CI 环境中的核心功能可用。"""

    def test_builder_initialization(self):
        """验证构建器能正常初始化。"""
        config = {
            "graph": {
                "title": "CI测试",
                "node_types": {"concept": {"label": "概念", "color": "#43A047", "size": 18}},
                "edge_types": {"related_to": {"label": "相关", "color": "#999", "width": 1}},
            },
            "parsers": [],
            "manual_nodes": [],
            "manual_edges": [],
            "auto_relations": [],
        }
        builder = KnowledgeGraphBuilder(config, Path("."))
        assert builder is not None
        assert builder.node_types == {"concept": {"label": "概念", "color": "#43A047", "size": 18}}
        assert builder.type_colors["concept"] == "#43A047"

    def test_deduplicate_handles_ci_data(self):
        """验证去重功能在 CI 数据上正常工作。"""
        config = {
            "graph": {
                "title": "CI测试",
                "node_types": {"concept": {"label": "概念", "color": "#43A047", "size": 18}},
                "edge_types": {"related_to": {"label": "相关", "color": "#999", "width": 1}},
            },
            "parsers": [],
            "manual_nodes": [],
            "manual_edges": [],
            "auto_relations": [],
        }
        builder = KnowledgeGraphBuilder(config, Path("."))
        builder.nodes = [
            {"id": "n1", "label": "Node1", "type": "concept"},
            {"id": "n1", "label": "Node1 Dup", "type": "concept"},
            {"id": "n2", "label": "Node2", "type": "concept"},
        ]
        builder.edges = [
            {"source": "n1", "target": "n2", "relation": "related_to"},
            {"source": "n1", "target": "n2", "relation": "related_to"},
        ]
        builder.deduplicate()
        assert len(builder.nodes) == 2
        assert len(builder.edges) == 1

    def test_isolated_detection(self):
        """验证孤立节点检测功能。"""
        config = {
            "graph": {
                "title": "CI测试",
                "node_types": {"concept": {"label": "概念", "color": "#43A047", "size": 18}},
                "edge_types": {"related_to": {"label": "相关", "color": "#999", "width": 1}},
            },
            "parsers": [],
            "manual_nodes": [],
            "manual_edges": [],
            "auto_relations": [],
        }
        builder = KnowledgeGraphBuilder(config, Path("."))
        builder.nodes = [
            {"id": "n1", "label": "Connected", "type": "concept"},
            {"id": "n2", "label": "Connected2", "type": "concept"},
            {"id": "n3", "label": "Isolated", "type": "concept"},
        ]
        builder.edges = [
            {"source": "n1", "target": "n2", "relation": "related_to"},
        ]
        isolated = builder.check_isolated()
        assert len(isolated) == 1
        assert isolated[0]["id"] == "n3"


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
        assert '__CONFIG_DATA__' in content
        assert '__TITLE__' in content
        assert '__SUBTITLE__' in content
        assert 'vis-network' in content
        assert '编辑模式' in content


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
