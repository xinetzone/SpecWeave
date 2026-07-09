#!/usr/bin/env python3
"""第一性原理知识图谱静态数据模块。"""

NODE_CONCEPT = "concept"
NODE_PERSON = "person"
NODE_EVENT = "event"
NODE_DOCUMENT = "document"
NODE_PERIOD = "period"

EDGE_RELATED = "related_to"
EDGE_INFLUENCED = "influenced"
EDGE_PRECEDED = "preceded"
EDGE_BELONGS_TO = "belongs_to"
EDGE_DEFINED_IN = "defined_in"
EDGE_CONTRIBUTED = "contributed"

PERIOD_NODES = [
    {
        'id': 'period_ancient',
        'label': '古希腊哲学时期',
        'type': NODE_PERIOD,
        'time_range': '公元前6世纪-公元前3世纪',
        'description': '从泰勒斯等前苏格拉底哲学家对本原的探索，到亚里士多德系统阐述archē概念，欧几里得《几何原本》公理化实践',
    },
    {
        'id': 'period_modern',
        'label': '近代哲学与科学革命',
        'type': NODE_PERIOD,
        'time_range': '17世纪-18世纪',
        'description': '笛卡尔"我思故我在"认识论转向、斯宾诺莎几何学方法、牛顿经典力学公理体系、康德先天综合判断',
    },
    {
        'id': 'period_modern_science',
        'label': '现代科学时期',
        'type': NODE_PERIOD,
        'time_range': '19世纪-20世纪',
        'description': '非欧几何发展、量子力学建立、密度泛函理论（DFT）奠基与发展、费曼物理学方法论、Anderson"More is Different"对还原论的反思',
    },
    {
        'id': 'period_contemporary',
        'label': '当代商业与方法论时期',
        'type': NODE_PERIOD,
        'time_range': '20世纪末-21世纪',
        'description': '马斯克在创业实践中应用第一性原理、2013年TED演讲使其在硅谷广泛传播、AI时代的新发展',
    },
]

INFLUENCED_EDGES_RAW = [
    ('person_亚里士多德', 'person_欧几里得'),
    ('person_欧几里得', 'person_笛卡尔'),
    ('person_笛卡尔', 'person_牛顿'),
    ('person_牛顿', 'person_康德'),
    ('person_牛顿', 'person_薛定谔'),
    ('person_牛顿', 'person_海森堡等'),
    ('person_薛定谔', 'person_霍恩伯格'),
    ('person_薛定谔', 'person_科恩'),
    ('person_薛定谔', 'person_沈吕九'),
    ('person_海森堡等', 'person_霍恩伯格'),
    ('person_海森堡等', 'person_科恩'),
    ('person_海森堡等', 'person_沈吕九'),
    ('person_霍恩伯格', 'person_费曼'),
    ('person_科恩', 'person_费曼'),
    ('person_沈吕九', 'person_费曼'),
    ('person_费曼', 'person_马斯克'),
    ('person_笛卡尔', 'person_马斯克'),
    ('person_康德', 'person_安德森'),
    ('person_安德森', 'person_马斯克'),
]

CONTRIBUTED_EDGES_RAW = [
    ('person_亚里士多德', 'concept_第一性原理'),
    ('person_亚里士多德', 'concept_本原'),
    ('person_欧几里得', 'concept_公理系统'),
    ('person_欧几里得', 'concept_演绎推理'),
    ('person_笛卡尔', 'concept_怀疑方法_普遍怀疑'),
    ('person_笛卡尔', 'concept_还原论'),
    ('person_笛卡尔', 'concept_演绎推理'),
    ('person_笛卡尔', 'concept_我思故我在'),
    ('person_牛顿', 'concept_还原论'),
    ('person_牛顿', 'concept_第一性原理'),
    ('person_康德', 'concept_先天综合判断'),
    ('person_费曼', 'concept_费曼学习法'),
    ('person_费曼', 'concept_草包族科学'),
    ('person_费曼', 'concept_从头算方法'),
    ('person_安德森', 'concept_涌现___多者异也'),
    ('person_安德森', 'concept_还原论'),
    ('person_马斯克', 'concept_第一性原理'),
    ('person_马斯克', 'concept_类比推理'),
    ('person_霍恩伯格', 'concept_密度泛函理论'),
    ('person_科恩', 'concept_密度泛函理论'),
    ('person_沈吕九', 'concept_密度泛函理论'),
    ('person_薛定谔', 'concept_从头算方法'),
    ('person_海森堡等', 'concept_从头算方法'),
]

CONCEPT_DOC_MAP = {
    '第一性原理': '01-philosophy-origins.md',
    '本原': '01-philosophy-origins.md',
    '公理': '01-philosophy-origins.md',
    '公设': '01-philosophy-origins.md',
    '第一因': '01-philosophy-origins.md',
    '怀疑方法/普遍怀疑': '01-philosophy-origins.md',
    '我思故我在': '01-philosophy-origins.md',
    '先天综合判断': '01-philosophy-origins.md',
    '演绎推理': '01-philosophy-origins.md',
    '归纳推理': '06-concepts-glossary.md',
    '类比推理': '06-concepts-glossary.md',
    '从头算方法': '02-physics-applications.md',
    '密度泛函理论': '02-physics-applications.md',
    '公理系统': '01-philosophy-origins.md',
    '还原论': '02-physics-applications.md',
    '涌现 / 多者异也': '02-physics-applications.md',
    '草包族科学': '04-key-thinkers-quotes.md',
    '费曼学习法': '04-key-thinkers-quotes.md',
    '逆向思维': '03-business-innovation-cases.md',
    '多元思维模型': '03-business-innovation-cases.md',
    '范式转换': '05-academic-resources.md',
    '事后归因偏差': '08-methodology-framework.md',
    '确认偏差': '08-methodology-framework.md',
    '幸存者偏差': '08-methodology-framework.md',
}


def get_influenced_edges():
    return [{'source': s, 'target': t, 'relation': EDGE_INFLUENCED} for s, t in INFLUENCED_EDGES_RAW]


def get_contributed_edges():
    return [{'source': s, 'target': t, 'relation': EDGE_CONTRIBUTED} for s, t in CONTRIBUTED_EDGES_RAW]
