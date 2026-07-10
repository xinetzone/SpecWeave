#!/usr/bin/env python3
"""第一性原理知识图谱生成脚本。解析Markdown文档提取节点和关系，生成交互式vis-network HTML知识图谱。"""

import argparse
import json
import re
import sys
from pathlib import Path
from collections import defaultdict

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import add_common_args, print_pass, print_warn, print_error, print_summary
from lib.project import resolve_project_root
from knowledge_graph_data import (
    NODE_CONCEPT, NODE_PERSON, NODE_EVENT, NODE_DOCUMENT, NODE_PERIOD,
    EDGE_RELATED, EDGE_INFLUENCED, EDGE_PRECEDED, EDGE_BELONGS_TO, EDGE_DEFINED_IN, EDGE_CONTRIBUTED,
    PERIOD_NODES, CONCEPT_DOC_MAP, get_influenced_edges, get_contributed_edges
)

INLINE_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
TEMPLATE_PATH = SCRIPTS_DIR / "templates" / "knowledge-graph-generic.html"


def _parse_markdown_table(content, section_header):
    """解析指定标题下的Markdown管道表格。"""
    lines, in_section, table_lines, table_started = content.split('\n'), False, [], False
    for line in lines:
        if line.startswith('## ') or line.startswith('### '):
            if in_section and table_started: break
            if line.strip() == section_header.strip(): in_section = True; continue
            elif in_section: in_section = False; continue
        if in_section and '|' in line:
            if not table_started and line.strip().startswith('|'): table_started = True
            if table_started: table_lines.append(line)
    if not table_lines: return []
    rows = []
    for line in table_lines:
        line = line.strip().strip('|')
        cells = [c.strip() for c in line.split('|')]
        if all(set(c.strip()) <= {'-', ':'} for c in cells): continue
        if cells: rows.append(cells)
    return rows


def _extract_domain(domain_str):
    """从领域字符串中提取主要领域分类。"""
    for d in ['哲学', '物理学', '方法论', '认知科学', '通用']:
        if d in domain_str: return d
    return domain_str.split('/')[0].strip() if '/' in domain_str else domain_str.strip()


def _extract_rating(remark_str):
    """从备注中提取可信度等级（A级/B级）。"""
    if '🟢' in remark_str or 'A级' in remark_str: return 'A'
    if '🔵' in remark_str or 'B级' in remark_str: return 'B'
    return 'B'


def parse_concepts_glossary(file_path):
    """解析概念术语表，返回(concepts, edges, unmatched_count)。"""
    content = file_path.read_text(encoding='utf-8')
    table = _parse_markdown_table(content, '## 2. 核心概念术语表')
    if not table or len(table) < 2:
        print_warn(f"未在 {file_path.name} 中找到核心概念术语表")
        return [], [], 0
    concepts, edges, concept_id_map, warn_count = [], [], {}, 0
    for i, row in enumerate(table[1:], 1):
        try:
            if len(row) < 7:
                print_warn(f"概念术语表第{i}行列数不足，跳过"); warn_count +=1; continue
            name_cn, name_en, definition, source, domain_str, related_str, remark = [c.strip() for c in row[:7]]
            if not name_cn: continue
            concept_id = f"concept_{name_cn.replace('/', '_').replace(' ', '_')}"
            domain = _extract_domain(domain_str)
            rating = _extract_rating(remark)
            source_url = f"file:///{file_path.as_posix()}"
            concepts.append({'id': concept_id, 'label': name_cn, 'type': NODE_CONCEPT, 'domain': domain,
                'definition': definition[:100], 'source_url': source_url, 'rating': rating,
                'english_name': name_en, 'source_author': source})
            concept_id_map[name_cn] = concept_id
            for alias in re.split(r'[/、]', name_cn):
                alias = alias.strip()
                if alias and alias not in concept_id_map: concept_id_map[alias] = concept_id
            for m in INLINE_LINK_RE.finditer(related_str):
                edges.append({'source': concept_id, 'target_name': m.group(1).strip(), 'relation': EDGE_RELATED})
        except Exception as e:
            print_warn(f"解析概念术语表第{i}行失败: {e}"); warn_count +=1; continue
    if warn_count: print_warn(f"概念术语表解析完成，{warn_count} 行解析失败")
    resolved, unmatched = [], 0
    for e in edges:
        tid = concept_id_map.get(e['target_name'])
        if tid: resolved.append({'source': e['source'], 'target': tid, 'relation': e['relation']})
        else: unmatched +=1; print_warn(f"概念链接无法匹配: {e['target_name']}")
    return concepts, resolved, unmatched


def parse_timeline_events(file_path):
    """解析时间线节点快速索引。"""
    content = file_path.read_text(encoding='utf-8')
    table = _parse_markdown_table(content, '## 9. 时间线节点快速索引')
    if not table or len(table) < 2:
        print_warn(f"未在 {file_path.name} 中找到时间线节点索引表"); return []
    events, warn_count, source_url = [], 0, f"file:///{file_path.as_posix()}"
    for i, row in enumerate(table[1:], 1):
        try:
            if len(row) <5: print_warn(f"时间线表第{i}行列数不足，跳过"); warn_count +=1; continue
            seq, time_str, event_name, period, importance = [c.strip() for c in row[:5]]
            if not event_name: continue
            events.append({'id': f"event_{seq}_{event_name.replace(' ', '_')[:20]}", 'label': event_name, 'type': NODE_EVENT,
                'time': time_str, 'period': period, 'importance': importance, 'source_url': source_url})
        except Exception as e:
            print_warn(f"解析时间线表第{i}行失败: {e}"); warn_count +=1; continue
    if warn_count: print_warn(f"时间线解析完成，{warn_count} 行解析失败")
    return events


def parse_key_people(file_path):
    """解析关键人物传承关系简表。"""
    content = file_path.read_text(encoding='utf-8')
    table = _parse_markdown_table(content, '## 6. 关键人物传承关系简表')
    if not table or len(table) <2:
        print_warn(f"未在 {file_path.name} 中找到关键人物表"); return []
    people, warn_count, source_url = [], 0, f"file:///{file_path.as_posix()}"
    for i, row in enumerate(table[1:],1):
        try:
            if len(row) <4: print_warn(f"关键人物表第{i}行列数不足，跳过"); warn_count +=1; continue
            period, person_names, contribution, fp_view = [c.strip() for c in row[:4]]
            if not person_names: continue
            for name in re.split(r'[/、，,]', person_names):
                name = name.strip()
                if not name: continue
                pid = f"person_{name.replace(' ', '_')}"
                people.append({'id': pid, 'label': name, 'type': NODE_PERSON, 'period': period,
                    'contribution': contribution, 'first_principle_view': fp_view, 'source_url': source_url})
        except Exception as e:
            print_warn(f"解析关键人物表第{i}行失败: {e}"); warn_count +=1; continue
    if warn_count: print_warn(f"关键人物解析完成，{warn_count} 行解析失败")
    return people


def parse_documents(readme_path):
    """解析文件导航表。"""
    content = readme_path.read_text(encoding='utf-8')
    table = _parse_markdown_table(content, '## 6. 文件导航')
    if not table or len(table) <2:
        print_warn(f"未在 {readme_path.name} 中找到文件导航表"); return []
    docs, warn_count, base_dir = [], 0, readme_path.parent.as_posix()
    for i, row in enumerate(table[1:],1):
        try:
            if len(row) <6: print_warn(f"文件导航表第{i}行列数不足，跳过"); warn_count +=1; continue
            _, file_cell, title, intro, difficulty, order = [c.strip() for c in row[:6]]
            link_match = INLINE_LINK_RE.search(file_cell)
            filename = link_match.group(2).strip() if link_match else file_cell.strip()
            if filename.startswith('file:///'): filename = filename.split('/')[-1]
            if not filename or not filename.endswith('.md'): continue
            doc_id = f"doc_{filename.replace('.md', '')}"
            docs.append({'id': doc_id, 'label': title or filename, 'type': NODE_DOCUMENT, 'filename': filename,
                'introduction': intro, 'difficulty': difficulty, 'reading_order': order,
                'source_url': f"file:///{base_dir}/{filename}"})
        except Exception as e:
            print_warn(f"解析文件导航表第{i}行失败: {e}"); warn_count +=1; continue
    if warn_count: print_warn(f"文档导航解析完成，{warn_count} 行解析失败")
    return docs


def _match_period(period_str, period_id_map):
    """根据时期字符串模糊匹配到Period节点id。"""
    if not period_str: return None
    ps = period_str.strip()
    if '古希腊' in ps: return 'period_ancient'
    if '近代' in ps: return 'period_modern'
    if '现代科学' in ps or '现代' in ps: return 'period_modern_science'
    if '当代' in ps: return 'period_contemporary'
    for label, pid in period_id_map.items():
        if ps in label or label in ps: return pid
    return None


def create_belongs_to_edges(events, people, periods):
    """建立Event/Person→Period的belongs_to关系。"""
    pmap = {p['label']: p['id'] for p in periods}
    edges = []
    for n in events + people:
        pid = _match_period(n.get('period', ''), pmap)
        if pid: edges.append({'source': n['id'], 'target': pid, 'relation': EDGE_BELONGS_TO})
    return edges


def create_defined_in_edges(concepts, documents, events=None):
    """建立Concept→Document的defined_in关系。"""
    if events is None: events = []
    dmap = {d['filename']: d['id'] for d in documents}
    cmap = {c['label']: c['id'] for c in concepts}
    edges = []
    for c in concepts:
        fn = CONCEPT_DOC_MAP.get(c['label'])
        if fn and fn in dmap: edges.append({'source': c['id'], 'target': dmap[fn], 'relation': EDGE_DEFINED_IN})
        else: edges.append({'source': c['id'], 'target': dmap.get('06-concepts-glossary.md', 'doc_06-concepts-glossary'), 'relation': EDGE_DEFINED_IN})
    extra = []
    if '00-adversarial-review-protocol.md' in dmap:
        for cid in [cmap.get('事后归因偏差'), cmap.get('确认偏差'), cmap.get('幸存者偏差')]:
            if cid: extra.append({'source': cid, 'target': dmap['00-adversarial-review-protocol.md'], 'relation': EDGE_RELATED})
    if '07-timeline.md' in dmap:
        for e in events[:3]: extra.append({'source': e['id'], 'target': dmap['07-timeline.md'], 'relation': EDGE_RELATED})
    if '09-further-reading.md' in dmap:
        cid = cmap.get('范式转换')
        if cid: extra.append({'source': cid, 'target': dmap['09-further-reading.md'], 'relation': EDGE_RELATED})
    if '10-source-validation-log.md' in dmap:
        cid = cmap.get('草包族科学')
        if cid: extra.append({'source': cid, 'target': dmap['10-source-validation-log.md'], 'relation': EDGE_RELATED})
    if '11-external-review.md' in dmap and '00-adversarial-review-protocol.md' in dmap:
        extra.append({'source': dmap['00-adversarial-review-protocol.md'], 'target': dmap['11-external-review.md'], 'relation': EDGE_RELATED})
    edges.extend(extra)
    return edges


def _parse_time_to_sort_key(time_str):
    """将时间字符串解析为可排序的数值（公元前为负数）。"""
    if not time_str: return 99999
    ts = time_str.strip(); is_bc = '前' in ts
    m = re.search(r'(\d+)世纪', ts)
    if m:
        c = int(m.group(1)); return -c*100 if is_bc else c*100
    m = re.search(r'(\d+)年', ts)
    if m:
        y = int(m.group(1)); return -y if is_bc else y
    m = re.search(r'(\d+)年代', ts)
    if m:
        d = int(m.group(1)); d += 1900 if d >20 else 2000 if d <100 else 0
        return -d if is_bc else d
    m = re.search(r'(\d+)-(\d+)', ts)
    if m:
        y = int(m.group(1)); return -y if is_bc else y
    return 99999


def create_preceded_edges(events):
    """建立事件之间的preceded时序关系（按时间排序）。"""
    se = sorted(events, key=lambda e: _parse_time_to_sort_key(e.get('time', '')))
    return [{'source': se[i]['id'], 'target': se[i+1]['id'], 'relation': EDGE_PRECEDED} for i in range(len(se)-1)]


def deduplicate_nodes(nodes):
    """节点去重，确保每个id唯一。"""
    seen, res = set(), []
    for n in nodes:
        if n['id'] not in seen: seen.add(n['id']); res.append(n)
        else: print_warn(f"重复节点id已跳过: {n['id']}")
    return res


def deduplicate_edges(edges):
    """边去重，相同(source, target, relation)只保留一条。"""
    seen, res = set(), []
    for e in edges:
        k = (e['source'], e['target'], e['relation'])
        if k not in seen: seen.add(k); res.append(e)
    return res


def check_isolated_nodes(nodes, edges):
    """检查孤立节点（度数为0的节点）。"""
    deg = defaultdict(int)
    for e in edges: deg[e['source']] +=1; deg[e['target']] +=1
    return [n for n in nodes if deg.get(n['id'], 0) ==0]


NODE_COLORS = {('concept','哲学'):'#8B4513',('concept','物理学'):'#1E88E5',('concept','方法论'):'#43A047',('concept','认知科学'):'#FB8C00',('concept','通用'):'#757575'}
NODE_TYPE_COLORS = {NODE_CONCEPT:'#757575',NODE_PERSON:'#E53935',NODE_EVENT:'#8E24AA',NODE_DOCUMENT:'#00897B',NODE_PERIOD:'#546E7A'}
NODE_SIZES = {NODE_PERIOD:35,NODE_PERSON:22,NODE_EVENT:22,NODE_CONCEPT:18,NODE_DOCUMENT:18}
EDGE_STYLES = {EDGE_RELATED:{'color':'#999','width':1,'dashes':False,'arrows':''},EDGE_INFLUENCED:{'color':'#1565C0','width':2,'dashes':False,'arrows':'to'},EDGE_PRECEDED:{'color':'#BBB','width':1,'dashes':False,'arrows':'to'},EDGE_BELONGS_TO:{'color':'#CCC','width':1,'dashes':[6,4],'arrows':''},EDGE_DEFINED_IN:{'color':'#4CAF50','width':1,'dashes':[2,3],'arrows':''},EDGE_CONTRIBUTED:{'color':'#FF9800','width':2,'dashes':False,'arrows':'to'}}
TYPE_LABELS = {NODE_CONCEPT:'概念',NODE_PERSON:'人物',NODE_EVENT:'事件',NODE_DOCUMENT:'文档',NODE_PERIOD:'时期'}


def _get_node_color(n):
    if n['type'] == NODE_CONCEPT:
        return NODE_COLORS.get(('concept', n.get('domain','通用')), NODE_COLORS[('concept','通用')])
    return NODE_TYPE_COLORS.get(n['type'], '#757575')


def _get_node_size(n):
    return NODE_SIZES.get(n['type'],18) + (2 if n['type']==NODE_CONCEPT and n.get('rating')=='A' else 0)


def _get_node_shape(n): return 'diamond' if n['type']==NODE_PERIOD else 'dot'


def _transform_nodes_for_js(nodes):
    res = []
    for n in nodes:
        c, s, sh = _get_node_color(n), _get_node_size(n), _get_node_shape(n)
        dom = n.get('domain','')
        tl = TYPE_LABELS.get(n['type'], n['type'])
        title = f"{n['label']} [{tl}·{dom}]" if n['type']==NODE_CONCEPT and dom else f"{n['label']} [{tl}]"
        jn = {'id':n['id'],'label':n['label'],'type':n['type'],'domain':dom,'title':title,
            'color':{'background':c,'border':c,'highlight':{'background':c,'border':'#000'}},'size':s,
            'font':{'color':'#333','size':14,'face':'sans-serif'},'shape':sh,'borderWidth':2,'borderWidthSelected':4}
        if n['type']==NODE_CONCEPT:
            jn.update({'definition':n.get('definition',''),'source_url':n.get('source_url',''),'rating':n.get('rating','B'),'english_name':n.get('english_name','')})
        elif n['type']==NODE_PERSON:
            jn.update({'period':n.get('period',''),'contribution':n.get('contribution',''),'source_url':n.get('source_url','')})
        elif n['type']==NODE_EVENT:
            jn.update({'time':n.get('time',''),'period':n.get('period',''),'importance':n.get('importance',''),'source_url':n.get('source_url','')})
        elif n['type']==NODE_DOCUMENT:
            jn.update({'description':n.get('introduction',''),'difficulty':n.get('difficulty',''),'source_url':n.get('source_url','')})
        elif n['type']==NODE_PERIOD:
            jn.update({'time_range':n.get('time_range',''),'description':n.get('description','')})
        res.append(jn)
    return res


def _transform_edges_for_js(edges):
    res = []
    for e in edges:
        st = EDGE_STYLES.get(e['relation'], EDGE_STYLES[EDGE_RELATED])
        je = {'from':e['source'],'to':e['target'],'relation':e['relation'],
            'color':{'color':st['color'],'highlight':st['color'],'hover':st['color']},
            'width':st['width'],'smooth':{'enabled':True,'type':'continuous'}}
        if st['dashes']: je['dashes'] = st['dashes']
        if st['arrows']: je['arrows'] = {st['arrows']:{'enabled':True,'scaleFactor':0.8}}
        res.append(je)
    return res


def generate_html(nodes, edges, output_path, title="🕸️ 第一性原理知识图谱"):
    """生成HTML可视化文件。"""
    jsn, jse = _transform_nodes_for_js(nodes), _transform_edges_for_js(edges)
    tpl = TEMPLATE_PATH.read_text(encoding='utf-8')
    
    js_config = {
        'typeColors': NODE_TYPE_COLORS,
        'domainColors': {'哲学': '#8B4513', '物理学': '#1E88E5', '方法论': '#43A047', '认知科学': '#FB8C00', '通用': '#757575'},
        'edgeStyles': {k: {'color': v['color'], 'dashes': v.get('dashes', False), 'arrows': v.get('arrows', '')} for k, v in EDGE_STYLES.items()},
        'typeLabels': TYPE_LABELS,
        'relationLabels': {EDGE_RELATED:'概念相关',EDGE_INFLUENCED:'思想传承',EDGE_PRECEDED:'时序先后',EDGE_BELONGS_TO:'时期归属',EDGE_DEFINED_IN:'概念定义',EDGE_CONTRIBUTED:'人物贡献'},
        'conceptType': 'concept',
        'detailFieldLabels': {
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
                {'key': 'description', 'label': '简介'},
                {'key': 'difficulty', 'label': '难度'},
                {'key': 'source_url', 'label': '打开文档', 'type': 'link'},
            ],
            'period': [
                {'key': 'time_range', 'label': '时间范围'},
                {'key': 'description', 'label': '概述'},
            ],
        },
        'subtitle': f"从古希腊哲学到当代商业方法论的思想传承网络 · {len(nodes)}个节点 · {len(edges)}条关系",
        'enableEditing': True,
    }
    
    repl = {
        '__TITLE__': title,
        '__SUBTITLE__': f"从古希腊哲学到当代商业方法论的思想传承网络 · {len(nodes)}个节点 · {len(edges)}条关系",
        '__NODE_COUNT__': str(len(nodes)),
        '__EDGE_COUNT__': str(len(edges)),
        '__NODES_DATA__': json.dumps(jsn, ensure_ascii=False),
        '__EDGES_DATA__': json.dumps(jse, ensure_ascii=False),
        '__CONFIG_DATA__': json.dumps(js_config, ensure_ascii=False),
    }
    for k,v in repl.items(): tpl = tpl.replace(k,v)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(tpl, encoding='utf-8')
    print_pass(f"HTML已生成: {output_path} ({output_path.stat().st_size/1024:.1f} KB)")


def print_statistics(nodes, edges, isolated):
    """打印图数据统计信息。"""
    tc = defaultdict(int)
    for n in nodes: tc[n['type']] +=1
    rc = defaultdict(int)
    for e in edges: rc[e['relation']] +=1
    stats = {'total_nodes':len(nodes),'total_edges':len(edges),'node_types':dict(tc),'edge_types':dict(rc),'isolated_count':len(isolated)}
    print("\n" + "="*60); print("知识图谱组装完成"); print("="*60)
    print_pass(f"总节点数: {stats['total_nodes']} 个")
    tn = {NODE_CONCEPT:'概念',NODE_PERSON:'人物',NODE_EVENT:'事件',NODE_DOCUMENT:'文档',NODE_PERIOD:'时期'}
    for nt,c in sorted(tc.items()): print_pass(f"  - {tn.get(nt,nt)}: {c} 个")
    print_pass(f"总边数: {stats['total_edges']} 条")
    rn = {EDGE_RELATED:'概念相关',EDGE_INFLUENCED:'思想传承',EDGE_BELONGS_TO:'时期归属',EDGE_DEFINED_IN:'概念定义',EDGE_CONTRIBUTED:'人物贡献',EDGE_PRECEDED:'时序先后'}
    for r,c in sorted(rc.items()): print_pass(f"  - {rn.get(r,r)}: {c} 条")
    if isolated:
        print_warn(f"发现 {len(isolated)} 个孤立节点（度数为0）：")
        for n in isolated: print_warn(f"  - [{n['type']}] {n['label']} ({n['id']})")
    else: print_pass("无孤立节点")
    return stats


def main(argv=None):
    parser = argparse.ArgumentParser(description="第一性原理知识图谱生成脚本 - 解析Markdown文档生成交互式HTML知识图谱")
    add_common_args(parser)
    parser.add_argument("--input-dir", type=Path, default=None, help="输入目录")
    parser.add_argument("--output", type=Path, default=None, help="HTML输出路径")
    parser.add_argument("--json-output", type=Path, default=None, help="JSON数据输出路径")
    args = parser.parse_args(argv)
    project_root = resolve_project_root(__file__)
    input_dir = args.input_dir or (project_root / "docs" / "knowledge" / "learning" / "first-principles")
    if not input_dir.exists(): print_error(f"输入目录不存在: {input_dir}"); return 1
    html_output = args.output or (input_dir / "12-knowledge-graph.html")
    glossary_path = input_dir / "06-concepts-glossary.md"
    timeline_path = input_dir / "07-timeline.md"
    readme_path = input_dir / "README.md"
    concepts, events, people, documents = [], [], [], []
    periods = PERIOD_NODES
    passc = warnc = errorc = 0
    print("="*60); print("第一性原理知识图谱生成器"); print("="*60)
    print(f"\n输入目录: {input_dir}"); print(f"输出文件: {html_output}")
    concept_edges = []
    if glossary_path.exists():
        print(f"\n1. 解析概念术语表: {glossary_path.name}")
        concepts, concept_edges, unmatched = parse_concepts_glossary(glossary_path)
        print_pass(f"提取概念: {len(concepts)} 个"); print_pass(f"提取概念关系: {len(concept_edges)} 条")
        warnc += unmatched; passc +=1
    else: print_error(f"概念术语表不存在: {glossary_path}"); errorc +=1
    if timeline_path.exists():
        print(f"\n2. 解析时间线节点: {timeline_path.name}")
        events = parse_timeline_events(timeline_path); print_pass(f"提取事件: {len(events)} 个"); passc +=1
        print(f"\n3. 解析关键人物: {timeline_path.name}")
        people = parse_key_people(timeline_path); print_pass(f"提取人物: {len(people)} 个"); passc +=1
    else: print_error(f"时间线文件不存在: {timeline_path}"); errorc +=1
    if readme_path.exists():
        print(f"\n4. 解析文档导航: {readme_path.name}")
        documents = parse_documents(readme_path); print_pass(f"提取文档: {len(documents)} 个"); passc +=1
    else: print_error(f"README文件不存在: {readme_path}"); errorc +=1
    print(f"\n5. 创建历史时期节点"); print_pass(f"添加时期: {len(periods)} 个"); passc +=1
    print(f"\n6. 添加手工编码关系")
    inf_e = get_influenced_edges(); print_pass(f"传承关系 (influenced): {len(inf_e)} 条")
    con_e = get_contributed_edges(); print_pass(f"贡献关系 (contributed): {len(con_e)} 条")
    bel_e = create_belongs_to_edges(events, people, periods); print_pass(f"归属关系 (belongs_to): {len(bel_e)} 条")
    def_e = create_defined_in_edges(concepts, documents, events); print_pass(f"定义关系 (defined_in): {len(def_e)} 条")
    pre_e = create_preceded_edges(events); print_pass(f"时序关系 (preceded): {len(pre_e)} 条"); passc +=1
    print(f"\n7. 组装图数据")
    all_n = concepts + events + people + documents + periods
    all_e = concept_edges + inf_e + con_e + bel_e + def_e + pre_e
    all_n = deduplicate_nodes(all_n); all_e = deduplicate_edges(all_e)
    print_pass(f"节点去重后: {len(all_n)} 个"); print_pass(f"边去重后: {len(all_e)} 条"); passc +=1
    iso = check_isolated_nodes(all_n, all_e)
    stats = print_statistics(all_n, all_e, iso)
    result = {'nodes': all_n, 'edges': all_e, 'summary': stats}
    if args.json: print("\n" + json.dumps(result, ensure_ascii=False, indent=2))
    if args.json_output:
        args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print_pass(f"JSON数据已保存到: {args.json_output}")
    print(f"\n8. 生成HTML可视化页面"); generate_html(all_n, all_e, html_output); passc +=1
    print_summary(passc, warnc, errorc)
    return 1 if errorc >0 else 0


if __name__ == "__main__":
    sys.exit(main())
