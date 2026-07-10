#!/usr/bin/env python3
"""通用知识图谱生成核心库。通过TOML配置驱动，支持从任意Markdown文档集提取节点和关系生成交互式知识图谱。

核心设计：四层混合策略（参考 markdown-to-knowledge-graph 架构模式）
1. 配置层：TOML定义节点类型、边类型、表格解析规则、样式配置
2. 解析层：通用表格解析器+可自定义解析钩子
3. 关系层：自动关系构建+手工关系配置
4. 输出层：HTML生成（vis-network）+JSON导出
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from collections import defaultdict
from pathlib import Path
from typing import Any
from collections.abc import Callable

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import add_common_args, print_pass, print_warn, print_error, print_summary
from lib.project import resolve_project_root

INLINE_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
DEFAULT_TEMPLATE_PATH = SCRIPTS_DIR / "templates" / "knowledge-graph-generic.html"
LEGACY_TEMPLATE_PATH = SCRIPTS_DIR / "templates" / "knowledge-graph-template.html"


def parse_markdown_table(content: str, section_header: str) -> list[list[str]]:
    """通用Markdown管道表格解析器。

    Args:
        content: Markdown文件内容
        section_header: 表格所在章节标题（如 "## 2. 核心概念术语表"）

    Returns:
        二维表格数据（第一行通常是表头）
    """
    lines = content.split('\n')
    in_section = False
    table_lines: list[str] = []
    table_started = False

    for line in lines:
        if line.startswith('## ') or line.startswith('### '):
            if in_section and table_started:
                break
            if line.strip() == section_header.strip():
                in_section = True
                continue
            elif in_section:
                in_section = False
                continue
        if in_section and '|' in line:
            if not table_started and line.strip().startswith('|'):
                table_started = True
            if table_started:
                table_lines.append(line)

    if not table_lines:
        return []

    rows: list[list[str]] = []
    for line in table_lines:
        line = line.strip().strip('|')
        cells = [c.strip() for c in line.split('|')]
        if all(set(c.strip()) <= {'-', ':'} for c in cells):
            continue
        if cells:
            rows.append(cells)
    return rows


def load_config(config_path: Path) -> dict[str, Any]:
    """加载TOML配置文件。"""
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with open(config_path, 'rb') as f:
        return tomllib.load(f)


def _default_id_generator(prefix: str, name: str, **kwargs: Any) -> str:
    """默认节点ID生成器：prefix + 清理后的名称。"""
    clean = name.replace('/', '_').replace(' ', '_').replace('、', '_')
    return f"{prefix}{clean}"


def _default_domain_extractor(domain_str: str, domain_mapping: dict[str, str] | None = None) -> str:
    """默认领域提取器。"""
    if domain_mapping:
        for keyword, domain in domain_mapping.items():
            if keyword in domain_str:
                return domain
    if '/' in domain_str:
        return domain_str.split('/')[0].strip()
    return domain_str.strip()


def _default_rating_extractor(remark_str: str, rating_keywords: dict[str, list[str]] | None = None) -> str:
    """默认可信度等级提取器。"""
    if rating_keywords is None:
        rating_keywords = {
            'A': ['🟢', 'A级', '一级来源', '高可信'],
            'B': ['🔵', 'B级', '二级来源', '中可信'],
        }
    for rating, keywords in rating_keywords.items():
        for kw in keywords:
            if kw in remark_str:
                return rating
    return 'B'


class KnowledgeGraphBuilder:
    """知识图谱构建器，通过配置驱动。"""

    def __init__(self, config: dict[str, Any], input_dir: Path):
        self.config = config
        self.input_dir = input_dir
        self.nodes: list[dict[str, Any]] = []
        self.edges: list[dict[str, Any]] = []
        self.node_id_map: dict[str, str] = {}
        self.warn_count = 0
        self.pass_count = 0
        self.error_count = 0

        self._init_defaults()

    def _init_defaults(self) -> None:
        """初始化默认配置。"""
        self.graph_config = self.config.get('graph', {})
        self.node_types = self.graph_config.get('node_types', {})
        self.edge_types = self.graph_config.get('edge_types', {})
        self.parsers_config = self.config.get('parsers', [])
        self.manual_nodes = self.config.get('manual_nodes', [])
        self.manual_edges = self.config.get('manual_edges', [])
        self.auto_relations = self.config.get('auto_relations', [])

        self.styles = self.config.get('styles', {})
        default_colors = self.styles.get('default_colors', {})
        default_sizes = self.styles.get('default_sizes', {})
        default_shapes = self.styles.get('default_shapes', {})

        self.type_colors: dict[str, str] = {}
        self.type_sizes: dict[str, int] = {}
        self.type_shapes: dict[str, str] = {}
        self.type_labels: dict[str, str] = {}
        self.concept_domain_colors: dict[tuple[str, str], str] = {}

        for nt_name, nt_conf in self.node_types.items():
            self.type_labels[nt_name] = nt_conf.get('label', nt_name)
            self.type_colors[nt_name] = nt_conf.get('color', default_colors.get(nt_name, '#757575'))
            self.type_sizes[nt_name] = nt_conf.get('size', default_sizes.get(nt_name, 18))
            self.type_shapes[nt_name] = nt_conf.get('shape', default_shapes.get(nt_name, 'dot'))

        if 'concept_domain_colors' in self.styles:
            for (typedom, color) in self.styles['concept_domain_colors'].items():
                parts = typedom.split('.', 1)
                if len(parts) == 2:
                    self.concept_domain_colors[(parts[0], parts[1])] = color

        self.edge_styles: dict[str, dict[str, Any]] = {}
        for et_name, et_conf in self.edge_types.items():
            self.edge_styles[et_name] = {
                'color': et_conf.get('color', '#999'),
                'width': et_conf.get('width', 1),
                'dashes': et_conf.get('dashes', False),
                'arrows': et_conf.get('arrows', ''),
            }

    def parse_table_nodes(self, parser_conf: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """通用表格解析：根据配置从Markdown表格提取节点和内部关系。

        Args:
            parser_conf: 解析器配置，包含file、section、node_type、id_prefix、columns等

        Returns:
            (nodes, edges) 元组
        """
        filename = parser_conf['file']
        section = parser_conf['section']
        node_type = parser_conf['node_type']
        id_prefix = parser_conf.get('id_prefix', f"{node_type}_")
        columns = parser_conf.get('columns', {})
        id_from = parser_conf.get('id_from', 'name')
        label_from = parser_conf.get('label_from')
        link_column = parser_conf.get('link_column')
        link_relation = parser_conf.get('link_relation', 'related_to')
        split_links_by = parser_conf.get('split_links_by', r'[/、]')
        split_names_by = parser_conf.get('split_names_by')
        filename_from_link = parser_conf.get('filename_from_link', False)
        filename_column = parser_conf.get('filename_column', id_from)
        base_dir_field = parser_conf.get('base_dir_field')
        domain_column = columns.get('domain')
        rating_column = columns.get('remark')
        domain_mapping = parser_conf.get('domain_mapping')
        rating_keywords = parser_conf.get('rating_keywords')
        min_columns = parser_conf.get('min_columns', 2)
        extra_fields = parser_conf.get('extra_fields', {})

        file_path = self.input_dir / filename
        if not file_path.exists():
            print_warn(f"文件不存在: {file_path}")
            self.warn_count += 1
            return [], []

        content = file_path.read_text(encoding='utf-8')
        table = parse_markdown_table(content, section)
        if not table or len(table) < 2:
            print_warn(f"未在 {filename} 中找到表格: {section}")
            self.warn_count += 1
            return [], []

        source_url_base = f"file:///{file_path.parent.as_posix()}/" if base_dir_field else f"file:///{file_path.as_posix()}"
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        local_id_map: dict[str, str] = {}

        for i, row in enumerate(table[1:], 1):
            try:
                if len(row) < min_columns:
                    print_warn(f"{filename} 表格 {section} 第{i}行列数不足({len(row)}<{min_columns})，跳过")
                    self.warn_count += 1
                    continue

                field_values: dict[str, str] = {}
                for field_name, col_idx in columns.items():
                    if isinstance(col_idx, int) and col_idx < len(row):
                        field_values[field_name] = row[col_idx].strip()
                    else:
                        field_values[field_name] = ''

                name_cell = field_values.get(id_from, '')
                if not name_cell:
                    continue

                doc_filename = None
                if filename_from_link:
                    link_match = INLINE_LINK_RE.search(name_cell)
                    if link_match:
                        doc_filename = link_match.group(2).strip()
                        if doc_filename.startswith('file:///'):
                            doc_filename = doc_filename.split('/')[-1]
                        display_label = link_match.group(1).strip()
                    else:
                        doc_filename = name_cell.strip()
                        display_label = field_values.get(label_from or 'title', doc_filename)
                else:
                    display_label = field_values.get(label_from, name_cell) if label_from else name_cell

                names_to_process: list[tuple[str, str]] = []
                if split_names_by and name_cell:
                    for nm in re.split(split_names_by, name_cell):
                        nm = nm.strip()
                        if nm:
                            names_to_process.append((nm, nm))
                elif filename_from_link and doc_filename:
                    if not doc_filename.endswith('.md'):
                        continue
                    node_label = field_values.get(label_from or 'title', display_label) or doc_filename
                    names_to_process.append((doc_filename.replace('.md', ''), node_label))
                else:
                    names_to_process.append((name_cell, display_label))

                for node_id_seed, node_label in names_to_process:
                    if not node_id_seed:
                        continue
                    node_id = _default_id_generator(id_prefix, node_id_seed)

                    node: dict[str, Any] = {
                        'id': node_id,
                        'label': node_label,
                        'type': node_type,
                    }

                    if filename_from_link and doc_filename:
                        node['filename'] = doc_filename
                        node['source_url'] = f"{source_url_base}{doc_filename}"
                    else:
                        node['source_url'] = source_url_base

                    for field_name, field_val in field_values.items():
                        if field_name != id_from and field_val:
                            if field_name == 'definition':
                                node[field_name] = field_val[:200]
                            elif filename_from_link and field_name == id_from:
                                pass
                            else:
                                node[field_name] = field_val

                    for ef_key, ef_val in extra_fields.items():
                        node[ef_key] = ef_val

                    if domain_column and domain_column in field_values and field_values[domain_column]:
                        node['domain'] = _default_domain_extractor(field_values[domain_column], domain_mapping)

                    if rating_column and rating_column in field_values and field_values[rating_column]:
                        node['rating'] = _default_rating_extractor(field_values[rating_column], rating_keywords)

                    nodes.append(node)
                    local_id_map[node_id_seed] = node_id
                    self.node_id_map[node_id_seed] = node_id
                    if node_label != node_id_seed:
                        local_id_map[node_label] = node_id
                        self.node_id_map[node_label] = node_id

                    aliases_field = parser_conf.get('aliases_from')
                    if aliases_field and aliases_field in field_values and field_values[aliases_field]:
                        for alias in re.split(split_links_by, field_values[aliases_field]):
                            alias = alias.strip()
                            if alias and alias not in local_id_map:
                                local_id_map[alias] = node_id
                                self.node_id_map[alias] = node_id

                    for alias in re.split(split_links_by, node_id_seed):
                        alias = alias.strip()
                        if alias and alias not in local_id_map:
                            local_id_map[alias] = node_id
                            self.node_id_map[alias] = node_id

                if link_column and link_column in field_values and field_values[link_column]:
                    link_text = field_values[link_column]
                    for m in INLINE_LINK_RE.finditer(link_text):
                        target_name = m.group(1).strip()
                        src_id = _default_id_generator(id_prefix, names_to_process[0][0] if names_to_process else name_cell)
                        edges.append({
                            'source': src_id,
                            'target_name': target_name,
                            'relation': link_relation,
                        })

            except Exception as e:
                print_warn(f"解析 {filename} 第{i}行失败: {e}")
                import traceback
                traceback.print_exc()
                self.warn_count += 1
                continue

        resolved_edges: list[dict[str, Any]] = []
        unmatched = 0
        for e in edges:
            tid = local_id_map.get(e['target_name']) or self.node_id_map.get(e['target_name'])
            if tid:
                resolved_edges.append({'source': e['source'], 'target': tid, 'relation': e['relation']})
            else:
                unmatched += 1
                print_warn(f"链接无法匹配: {e['target_name']} (来自 {filename})")

        if unmatched:
            self.warn_count += unmatched

        return nodes, resolved_edges

    def add_manual_data(self) -> None:
        """添加配置中定义的手工节点和边。"""
        for n in self.manual_nodes:
            self.nodes.append(n)
            if 'label' in n:
                self.node_id_map[n['label']] = n['id']
        print_pass(f"添加工节点: {len(self.manual_nodes)} 个")

        for e in self.manual_edges:
            self.edges.append({'source': e['source'], 'target': e['target'], 'relation': e['relation']})
        print_pass(f"添加工边: {len(self.manual_edges)} 条")

    def build_auto_relations(self) -> None:
        """构建自动关系（如belongs_to、preceded、defined_in等）。"""
        nodes_by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
        nodes_by_id: dict[str, dict[str, Any]] = {}
        for n in self.nodes:
            nodes_by_type[n['type']].append(n)
            nodes_by_id[n['id']] = n

        for rel_conf in self.auto_relations:
            rel_type = rel_conf['type']

            if rel_type == 'belongs_to':
                source_types = rel_conf.get('source_types', [])
                target_type = rel_conf.get('target_type', 'period')
                period_field = rel_conf.get('period_field', 'period')
                relation = rel_conf.get('relation', 'belongs_to')
                target_map = {n['label']: n['id'] for n in nodes_by_type.get(target_type, [])}
                period_keywords = rel_conf.get('period_keywords', {})

                created = 0
                for st in source_types:
                    for n in nodes_by_type.get(st, []):
                        period_str = n.get(period_field, '')
                        tid = None
                        for kw, pid in period_keywords.items():
                            if kw in period_str:
                                tid = pid
                                break
                        if not tid:
                            for label, pid in target_map.items():
                                if period_str in label or label in period_str:
                                    tid = pid
                                    break
                        if tid:
                            self.edges.append({'source': n['id'], 'target': tid, 'relation': relation})
                            created += 1
                print_pass(f"自动关系 {relation}: {created} 条")

            elif rel_type == 'preceded':
                source_type = rel_conf.get('source_type', 'event')
                time_field = rel_conf.get('time_field', 'time')
                relation = rel_conf.get('relation', 'preceded')

                events = nodes_by_type.get(source_type, [])
                if events:
                    def sort_key(e: dict[str, Any]) -> int:
                        return self._parse_time_to_sort_key(e.get(time_field, ''))
                    sorted_events = sorted(events, key=sort_key)
                    for i in range(len(sorted_events) - 1):
                        self.edges.append({
                            'source': sorted_events[i]['id'],
                            'target': sorted_events[i+1]['id'],
                            'relation': relation,
                        })
                    print_pass(f"自动关系 {relation}: {len(sorted_events)-1} 条")

            elif rel_type == 'defined_in':
                concept_type = rel_conf.get('concept_type', 'concept')
                doc_type = rel_conf.get('doc_type', 'document')
                file_field = rel_conf.get('file_field', 'filename')
                relation = rel_conf.get('relation', 'defined_in')
                concept_doc_map = rel_conf.get('concept_doc_map', {})
                default_doc = rel_conf.get('default_doc')
                extra_links = rel_conf.get('extra_links', [])

                concepts = nodes_by_type.get(concept_type, [])
                docs = nodes_by_type.get(doc_type, [])
                doc_map = {d.get(file_field, ''): d['id'] for d in docs}
                concept_map = {c['label']: c['id'] for c in concepts}

                created = 0
                for c in concepts:
                    fn = concept_doc_map.get(c['label'])
                    if fn and fn in doc_map:
                        self.edges.append({'source': c['id'], 'target': doc_map[fn], 'relation': relation})
                        created += 1
                    elif default_doc and default_doc in doc_map:
                        self.edges.append({'source': c['id'], 'target': doc_map[default_doc], 'relation': relation})
                        created += 1

                for link_conf in extra_links:
                    concept_name = link_conf.get('concept')
                    doc_file = link_conf.get('doc')
                    link_rel = link_conf.get('relation', relation)
                    cid = concept_map.get(concept_name)
                    did = doc_map.get(doc_file)
                    if cid and did:
                        self.edges.append({'source': cid, 'target': did, 'relation': link_rel})
                        created += 1

                print_pass(f"自动关系 {relation}: {created} 条")

    def _parse_time_to_sort_key(self, time_str: str) -> int:
        """将时间字符串解析为可排序的数值（公元前为负数）。"""
        if not time_str:
            return 99999
        ts = time_str.strip()
        is_bc = '前' in ts

        m = re.search(r'(\d+)世纪', ts)
        if m:
            c = int(m.group(1))
            return -c * 100 if is_bc else c * 100
        m = re.search(r'(\d+)年', ts)
        if m:
            y = int(m.group(1))
            return -y if is_bc else y
        m = re.search(r'(\d+)年代', ts)
        if m:
            d = int(m.group(1))
            d += 1900 if d > 20 else 2000 if d < 100 else 0
            return -d if is_bc else d
        m = re.search(r'(\d+)-(\d+)', ts)
        if m:
            y = int(m.group(1))
            return -y if is_bc else y
        return 99999

    def deduplicate(self) -> None:
        """节点和边去重。"""
        seen_nodes: set[str] = set()
        unique_nodes: list[dict[str, Any]] = []
        for n in self.nodes:
            if n['id'] not in seen_nodes:
                seen_nodes.add(n['id'])
                unique_nodes.append(n)
            else:
                print_warn(f"重复节点id已跳过: {n['id']}")
                self.warn_count += 1
        self.nodes = unique_nodes

        seen_edges: set[tuple[str, str, str]] = set()
        unique_edges: list[dict[str, Any]] = []
        for e in self.edges:
            key = (e['source'], e['target'], e['relation'])
            if key not in seen_edges:
                seen_edges.add(key)
                unique_edges.append(e)
        self.edges = unique_edges

        print_pass(f"节点去重后: {len(self.nodes)} 个")
        print_pass(f"边去重后: {len(self.edges)} 条")

    def check_isolated(self) -> list[dict[str, Any]]:
        """检查孤立节点。"""
        deg: dict[str, int] = defaultdict(int)
        for e in self.edges:
            deg[e['source']] += 1
            deg[e['target']] += 1
        return [n for n in self.nodes if deg.get(n['id'], 0) == 0]

    def _tokenize(self, text: str) -> set[str]:
        """简单文本分词：提取2-gram字符组合和停用词过滤后的词。"""
        if not text:
            return set()
        stopwords = {'的', '了', '在', '是', '有', '和', '与', '或', '等', '中', '对', '为', '以',
                     '上', '下', '不', '也', '都', '而', '及', '之', '其', '这', '那', '个',
                     'from', 'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for', 'and', 'or',
                     'is', 'are', 'was', 'were', 'be', 'by', 'with', 'as', 'i', 'you', 'it'}
        cleaned = re.sub(r'[^\w\u4e00-\u9fff]', ' ', text.lower())
        tokens: set[str] = set()
        words = cleaned.split()
        for w in words:
            if len(w) >= 2 and w not in stopwords:
                tokens.add(w)
            for i in range(len(w) - 1):
                bg = w[i:i+2]
                if len(bg.strip()) == 2:
                    tokens.add(bg)
        return tokens

    def _get_node_text(self, n: dict[str, Any]) -> str:
        """提取节点的所有文本字段用于相似度计算。"""
        fields = ['label', 'definition', 'introduction', 'description',
                  'contribution', 'english_name', 'title', 'domain', 'period']
        parts = []
        for f in fields:
            if f in n and n[f]:
                parts.append(str(n[f]))
        return ' '.join(parts)

    def _guess_relation(self, source_type: str, target_type: str) -> tuple[str, float]:
        """根据源节点和目标节点类型，猜测最可能的关系类型。"""
        type_pairs = {
            ('concept', 'concept'): ('related_to', 0.6),
            ('concept', 'document'): ('defined_in', 0.7),
            ('document', 'concept'): ('related_to', 0.5),
            ('person', 'concept'): ('contributed', 0.8),
            ('concept', 'person'): ('related_to', 0.4),
            ('person', 'person'): ('influenced', 0.5),
            ('event', 'period'): ('belongs_to', 0.9),
            ('person', 'period'): ('belongs_to', 0.9),
            ('event', 'event'): ('preceded', 0.5),
            ('document', 'document'): ('related_to', 0.4),
            ('concept', 'event'): ('related_to', 0.4),
            ('person', 'event'): ('related_to', 0.4),
        }
        key = (source_type, target_type)
        reverse_key = (target_type, source_type)
        if key in type_pairs:
            return type_pairs[key]
        if reverse_key in type_pairs:
            rel, conf = type_pairs[reverse_key]
            return rel, conf * 0.7
        return ('related_to', 0.3)

    def suggest_isolated_links(self, isolated_nodes: list[dict[str, Any]], top_k: int = 3) -> dict[str, list[dict[str, Any]]]:
        """为孤立节点推荐可能的关联。

        使用多维度评分策略：
        1. 名称子串/关键词匹配（最高权重）
        2. 领域相同（加分）
        3. 类型相容性（基于常见关系类型对）
        4. 描述/定义文本相似度（2-gram Jaccard）

        Args:
            isolated_nodes: 孤立节点列表
            top_k: 每个节点推荐数量

        Returns:
            字典 {node_id: [recommendation...]}，每个推荐包含 target_id, target_label, relation, confidence, reasons
        """
        if not isolated_nodes:
            return {}

        non_isolated = [n for n in self.nodes if n not in isolated_nodes]
        if not non_isolated:
            return {}

        node_text_cache: dict[str, set[str]] = {}
        for n in self.nodes:
            node_text_cache[n['id']] = self._tokenize(self._get_node_text(n))

        existing_edges: set[tuple[str, str]] = set()
        for e in self.edges:
            existing_edges.add((e['source'], e['target']))
            existing_edges.add((e['target'], e['source']))

        suggestions: dict[str, list[dict[str, Any]]] = {}

        for iso in isolated_nodes:
            iso_id = iso['id']
            iso_label = iso.get('label', iso_id)
            iso_type = iso.get('type', '')
            iso_domain = iso.get('domain', '')
            iso_tokens = node_text_cache[iso_id]

            candidates: list[dict[str, Any]] = []

            for candidate in non_isolated:
                cand_id = candidate['id']
                if (iso_id, cand_id) in existing_edges:
                    continue

                cand_label = candidate.get('label', cand_id)
                cand_type = candidate.get('type', '')
                cand_domain = candidate.get('domain', '')
                cand_tokens = node_text_cache[cand_id]

                score = 0.0
                reasons: list[str] = []

                if iso_label and cand_label:
                    if iso_label == cand_label:
                        score += 5.0
                        reasons.append('标签完全匹配')
                    elif iso_label in cand_label or cand_label in iso_label:
                        score += 3.0
                        shorter = iso_label if len(iso_label) < len(cand_label) else cand_label
                        longer = cand_label if len(iso_label) < len(cand_label) else iso_label
                        reasons.append(f'标签包含关键词（{shorter}）')
                    else:
                        overlap_chars = set(iso_label) & set(cand_label)
                        if len(overlap_chars) >= 2:
                            score += 1.5
                            reasons.append(f'标签共享{len(overlap_chars)}个字符')

                if iso_domain and cand_domain and iso_domain == cand_domain:
                    score += 2.0
                    reasons.append(f'相同领域（{iso_domain}）')

                guessed_rel, type_conf = self._guess_relation(iso_type, cand_type)
                score += type_conf * 2.0
                if type_conf >= 0.7:
                    reasons.append(f'类型匹配（{self.type_labels.get(iso_type, iso_type)}→{self.type_labels.get(cand_type, cand_type)}）')

                if iso_tokens and cand_tokens:
                    jaccard = len(iso_tokens & cand_tokens) / max(len(iso_tokens | cand_tokens), 1)
                    if jaccard > 0.1:
                        score += jaccard * 3.0
                        if jaccard > 0.3:
                            reasons.append(f'描述文本相似度高（{jaccard:.0%}）')
                        elif jaccard > 0.15:
                            reasons.append(f'描述文本有部分相似（{jaccard:.0%}）')

                if score > 0.5:
                    candidates.append({
                        'target_id': cand_id,
                        'target_label': cand_label,
                        'target_type': cand_type,
                        'relation': guessed_rel,
                        'confidence': min(score / 5.0, 1.0),
                        'reasons': reasons,
                    })

            candidates.sort(key=lambda x: x['confidence'], reverse=True)
            top_candidates = candidates[:top_k]
            for c in top_candidates:
                c['confidence'] = round(c['confidence'], 2)
            suggestions[iso_id] = {
                'node_label': iso_label,
                'node_type': iso_type,
                'recommendations': top_candidates,
            }

        return suggestions

    def print_isolated_suggestions(self, suggestions: dict[str, list[dict[str, Any]]]) -> None:
        """打印孤立节点关联建议。"""
        if not suggestions:
            return
        print("\n" + "=" * 60)
        print("💡 孤立节点关联建议")
        print("=" * 60)
        for iso_id, info in suggestions.items():
            label = info['node_label']
            ntype = self.type_labels.get(info['node_type'], info['node_type'])
            recs = info['recommendations']
            print(f"\n🔍 [{ntype}] {label} ({iso_id}):")
            if not recs:
                print("   （无高置信度建议）")
                continue
            for i, rec in enumerate(recs, 1):
                conf_pct = int(rec['confidence'] * 100)
                rel_label = self.edge_types.get(rec['relation'], {}).get('label', rec['relation'])
                cand_type = self.type_labels.get(rec['target_type'], rec['target_type'])
                print(f"   {i}. [{conf_pct}%] → {rec['target_label']} [{cand_type}]")
                print(f"      建议关系: {rel_label} ({rec['relation']})")
                if rec['reasons']:
                    print(f"      理由: {'、'.join(rec['reasons'])}")
                print(f"      添加: {{'source': '{iso_id}', 'target': '{rec['target_id']}', 'relation': '{rec['relation']}'}}")

    def get_statistics(self) -> dict[str, Any]:
        """获取统计信息。"""
        type_counts: dict[str, int] = defaultdict(int)
        for n in self.nodes:
            type_counts[n['type']] += 1
        rel_counts: dict[str, int] = defaultdict(int)
        for e in self.edges:
            rel_counts[e['relation']] += 1
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'node_types': dict(type_counts),
            'edge_types': dict(rel_counts),
        }

    def _get_node_color(self, n: dict[str, Any]) -> str:
        if n['type'] in self.node_types:
            domain = n.get('domain', '')
            key = (n['type'], domain)
            if key in self.concept_domain_colors:
                return self.concept_domain_colors[key]
            color_map = self.node_types[n['type']].get('domain_colors', {})
            if domain in color_map:
                return color_map[domain]
        return self.type_colors.get(n['type'], '#757575')

    def _get_node_size(self, n: dict[str, Any]) -> int:
        base = self.type_sizes.get(n['type'], 18)
        rating_bonus = 2 if n['type'] in self.node_types and self.node_types[n['type']].get('rating_bonus') and n.get('rating') == 'A' else 0
        return base + rating_bonus

    def _get_node_shape(self, n: dict[str, Any]) -> str:
        return self.type_shapes.get(n['type'], 'dot')

    def transform_nodes_for_js(self) -> list[dict[str, Any]]:
        """转换节点为vis-network格式。"""
        result = []
        for n in self.nodes:
            c = self._get_node_color(n)
            s = self._get_node_size(n)
            sh = self._get_node_shape(n)
            dom = n.get('domain', '')
            tl = self.type_labels.get(n['type'], n['type'])
            title = f"{n['label']} [{tl}·{dom}]" if dom else f"{n['label']} [{tl}]"

            jn = {
                'id': n['id'],
                'label': n['label'],
                'type': n['type'],
                'domain': dom,
                'title': title,
                'color': {
                    'background': c,
                    'border': c,
                    'highlight': {'background': c, 'border': '#000'},
                },
                'size': s,
                'font': {'color': '#333', 'size': 14, 'face': 'sans-serif'},
                'shape': sh,
                'borderWidth': 2,
                'borderWidthSelected': 4,
            }

            for key, val in n.items():
                if key not in ('id', 'label', 'type'):
                    jn[key] = val

            result.append(jn)
        return result

    def transform_edges_for_js(self) -> list[dict[str, Any]]:
        """转换边为vis-network格式。"""
        result = []
        for e in self.edges:
            st = self.edge_styles.get(e['relation'], self.edge_styles.get('related_to', {
                'color': '#999', 'width': 1, 'dashes': False, 'arrows': ''
            }))
            je = {
                'from': e['source'],
                'to': e['target'],
                'relation': e['relation'],
                'color': {'color': st['color'], 'highlight': st['color'], 'hover': st['color']},
                'width': st['width'],
                'smooth': {'enabled': True, 'type': 'continuous'},
            }
            if st.get('dashes'):
                je['dashes'] = st['dashes']
            if st.get('arrows'):
                je['arrows'] = {st['arrows']: {'enabled': True, 'scaleFactor': 0.8}}
            result.append(je)
        return result

    def _build_js_config(self) -> dict[str, Any]:
        """构建注入到HTML模板中的JS配置对象。"""
        domain_colors: dict[str, str] = {}
        concept_type = None
        for nt_name, nt_conf in self.node_types.items():
            if 'domain_colors' in nt_conf:
                concept_type = nt_name
                domain_colors.update(nt_conf['domain_colors'])
        for (typ, dom), color in self.concept_domain_colors.items():
            if concept_type is None:
                concept_type = typ
            domain_colors[dom] = color

        edge_styles_js: dict[str, dict[str, Any]] = {}
        for et_name, st in self.edge_styles.items():
            edge_styles_js[et_name] = {
                'color': st['color'],
                'dashes': st.get('dashes', False),
                'arrows': st.get('arrows', ''),
            }

        detail_fields = self.graph_config.get('detail_fields', {})
        if not detail_fields:
            detail_fields = {
                'concept': [
                    {'key': 'english_name', 'label': '英文名'},
                    {'key': 'definition', 'label': '定义摘要'},
                    {'key': 'rating', 'label': '可信度评级', 'type': 'rating'},
                    {'key': 'source_url', 'label': '查看源文档', 'type': 'link'},
                ],
                'person': [
                    {'key': 'period', 'label': '时期'},
                    {'key': 'contribution', 'label': '核心贡献'},
                    {'key': 'source_url', 'label': '查看源文档', 'type': 'link'},
                ],
                'event': [
                    {'key': 'time', 'label': '时间'},
                    {'key': 'period', 'label': '时期'},
                    {'key': 'importance', 'label': '重要程度'},
                    {'key': 'source_url', 'label': '详细说明', 'type': 'link'},
                ],
                'document': [
                    {'key': 'introduction', 'label': '简介'},
                    {'key': 'difficulty', 'label': '难度'},
                    {'key': 'source_url', 'label': '打开文档', 'type': 'link'},
                ],
                'period': [
                    {'key': 'time_range', 'label': '时间范围'},
                    {'key': 'description', 'label': '概述'},
                ],
            }

        subtitle = self.graph_config.get('subtitle', f"__NODE_COUNT__个节点 · __EDGE_COUNT__条关系")
        enable_editing = self.graph_config.get('enable_editing', True)

        return {
            'typeColors': dict(self.type_colors),
            'domainColors': domain_colors,
            'edgeStyles': edge_styles_js,
            'typeLabels': dict(self.type_labels),
            'relationLabels': {et: et_conf.get('label', et) for et, et_conf in self.edge_types.items()},
            'conceptType': concept_type or 'concept',
            'detailFieldLabels': detail_fields,
            'subtitle': subtitle,
            'enableEditing': enable_editing,
        }

    def generate_html(self, output_path: Path, template_path: Path | None = None) -> None:
        """生成HTML可视化文件。"""
        tpl_path = template_path or DEFAULT_TEMPLATE_PATH
        jsn = self.transform_nodes_for_js()
        jse = self.transform_edges_for_js()
        js_config = self._build_js_config()
        tpl = tpl_path.read_text(encoding='utf-8')

        title = self.graph_config.get('title', '知识图谱')
        subtitle = js_config.get('subtitle', f"{len(self.nodes)}个节点 · {len(self.edges)}条关系")
        subtitle = subtitle.replace('__NODE_COUNT__', str(len(self.nodes))).replace('__EDGE_COUNT__', str(len(self.edges)))

        repl = {
            '__TITLE__': title,
            '__SUBTITLE__': subtitle,
            '__NODE_COUNT__': str(len(self.nodes)),
            '__EDGE_COUNT__': str(len(self.edges)),
            '__NODES_DATA__': json.dumps(jsn, ensure_ascii=False),
            '__EDGES_DATA__': json.dumps(jse, ensure_ascii=False),
            '__CONFIG_DATA__': json.dumps(js_config, ensure_ascii=False),
        }
        for k, v in repl.items():
            tpl = tpl.replace(k, v)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(tpl, encoding='utf-8')
        print_pass(f"HTML已生成: {output_path} ({output_path.stat().st_size/1024:.1f} KB)")

    def print_stats(self, isolated: list[dict[str, Any]]) -> None:
        """打印统计信息。"""
        stats = self.get_statistics()
        print("\n" + "=" * 60)
        print("知识图谱组装完成")
        print("=" * 60)
        print_pass(f"总节点数: {stats['total_nodes']} 个")
        for nt, c in sorted(stats['node_types'].items()):
            print_pass(f"  - {self.type_labels.get(nt, nt)}: {c} 个")
        print_pass(f"总边数: {stats['total_edges']} 条")
        for r, c in sorted(stats['edge_types'].items()):
            rl = self.edge_types.get(r, {}).get('label', r)
            print_pass(f"  - {rl}: {c} 条")
        if isolated:
            print_warn(f"发现 {len(isolated)} 个孤立节点（度数为0）：")
            for n in isolated:
                print_warn(f"  - [{self.type_labels.get(n['type'], n['type'])}] {n['label']} ({n['id']})")
        else:
            print_pass("无孤立节点")


def build_graph_from_config(
    config_path: Path,
    input_dir: Path | None = None,
    output_path: Path | None = None,
    json_output_path: Path | None = None,
    template_path: Path | None = None,
    verbose: bool = False,
) -> KnowledgeGraphBuilder:
    """从配置文件构建知识图谱的便捷函数。

    Args:
        config_path: TOML配置文件路径
        input_dir: 输入目录（默认从配置中读取或使用配置文件所在目录）
        output_path: HTML输出路径
        json_output_path: JSON数据输出路径
        template_path: 自定义HTML模板路径
        verbose: 是否输出详细信息

    Returns:
        KnowledgeGraphBuilder实例（可用于进一步操作）
    """
    config = load_config(config_path)
    project_root = resolve_project_root(__file__)

    if input_dir is None:
        input_dir = Path(config.get('input_dir', config_path.parent))
        if not input_dir.is_absolute():
            input_dir = (config_path.parent / input_dir).resolve()

    if output_path is None:
        output_file = config.get('output', 'knowledge-graph.html')
        output_path = input_dir / output_file

    builder = KnowledgeGraphBuilder(config, input_dir)

    print("=" * 60)
    print(f"通用知识图谱生成器: {builder.graph_config.get('title', '未命名')}")
    print("=" * 60)
    print(f"\n配置文件: {config_path}")
    print(f"输入目录: {input_dir}")
    print(f"输出文件: {output_path}")

    for parser_conf in builder.parsers_config:
        ptype = parser_conf.get('type', 'table')
        if ptype == 'table':
            node_type = parser_conf['node_type']
            section = parser_conf['section']
            filename = parser_conf['file']
            print(f"\n解析 {node_type} 表格: {filename} -> {section}")
            nodes, edges = builder.parse_table_nodes(parser_conf)
            builder.nodes.extend(nodes)
            builder.edges.extend(edges)
            print_pass(f"提取{builder.type_labels.get(node_type, node_type)}: {len(nodes)} 个")
            print_pass(f"提取关系: {len(edges)} 条")
            builder.pass_count += 1

    print(f"\n添加手工节点和边")
    builder.add_manual_data()
    builder.pass_count += 1

    print(f"\n构建自动关系")
    builder.build_auto_relations()
    builder.pass_count += 1

    print(f"\n去重与验证")
    builder.deduplicate()
    builder.pass_count += 1

    isolated = builder.check_isolated()
    builder.print_stats(isolated)

    if isolated:
        suggestions = builder.suggest_isolated_links(isolated, top_k=3)
        builder.print_isolated_suggestions(suggestions)
        result = {'nodes': builder.nodes, 'edges': builder.edges, 'summary': builder.get_statistics(), 'isolated_suggestions': suggestions}
    else:
        result = {'nodes': builder.nodes, 'edges': builder.edges, 'summary': builder.get_statistics()}

    if json_output_path:
        json_output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print_pass(f"JSON数据已保存到: {json_output_path}")

    print(f"\n生成HTML可视化页面")
    builder.generate_html(output_path, template_path)
    builder.pass_count += 1

    if verbose:
        print_summary(builder.pass_count, builder.warn_count, builder.error_count)

    return builder


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="通用知识图谱生成器 - 通过TOML配置从Markdown文档生成交互式HTML知识图谱")
    add_common_args(parser)
    parser.add_argument("--config", type=Path, required=True, help="TOML配置文件路径")
    parser.add_argument("--input-dir", type=Path, default=None, help="输入目录（覆盖配置）")
    parser.add_argument("--output", type=Path, default=None, help="HTML输出路径（覆盖配置）")
    parser.add_argument("--json-output", type=Path, default=None, help="JSON数据输出路径")
    parser.add_argument("--template", type=Path, default=None, help="自定义HTML模板路径")
    args = parser.parse_args(argv)

    config_path = args.config
    if not config_path.is_absolute():
        config_path = config_path.resolve()

    try:
        builder = build_graph_from_config(
            config_path=config_path,
            input_dir=args.input_dir,
            output_path=args.output,
            json_output_path=args.json_output,
            template_path=args.template,
            verbose=True,
        )
        print_summary(builder.pass_count, builder.warn_count, builder.error_count)
        return 1 if builder.error_count > 0 else 0
    except Exception as e:
        print_error(f"生成失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())