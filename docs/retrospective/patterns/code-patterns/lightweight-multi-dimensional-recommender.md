---
id: "lightweight-multi-dimensional-recommender"
source: "docs/retrospective/reports/task-reports/retrospective-first-principles-knowledge-graph-20260709/insight-extraction.md"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/code-patterns/lightweight-multi-dimensional-recommender.toml"
---
# 无依赖轻量级多维度推荐算法

## 模式概述

在节点/条目数量<500的中小规模推荐场景下（如知识图谱孤立节点关联、标签推荐、相关文档推荐），无需引入jieba/numpy/sklearn/embedding等NLP/ML依赖，使用纯Python标准库实现的多维度加权评分算法即可获得良好的推荐效果（实测Top 1准确率100%）。

核心设计原则：**简单优先、零依赖、多维度、可解释**。

## 适用场景

| 场景 | 规模上限 | 是否适用 | 说明 |
|------|---------|---------|------|
| 知识图谱孤立节点关联推荐 | <500节点 | ✅ 核心场景 | IMP-004验证，77节点规模下Top1准确率100% |
| 标签/分类系统相似项推荐 | <1000标签 | ✅ 适用 | 标签名称短，字符匹配效果好 |
| 文档/代码相关链接推荐 | <1000文档 | ✅ 适用 | 标题+摘要匹配足够发现相关文档 |
| 配置项/参数智能补全 | <500选项 | ✅ 适用 | 配置项名称通常有规律 |
| 中小规模实体匹配 | <1000实体 | ✅ 适用 | 名称短、有分类/领域信息时效果好 |
| 大规模推荐（>1000条目） | >1000 | ❌ 不适用 | O(n²)复杂度性能下降，需考虑向量数据库 |
| 深层语义匹配 | - | ❌ 不适用 | 需要embedding理解隐喻/同义不同名 |
| 长文本相似度计算 | - | ❌ 不适用 | 需要TF-IDF/BM25/向量模型 |

## 算法架构

### 四维度加权评分模型

不依赖单一文本相似度信号，而是组合4个互补维度的加权评分：

| 维度 | 权重 | 信号强度 | 计算方式 |
|------|------|---------|---------|
| 精确标签匹配 | 0.40 | 强 | 标签完全包含/共享关键词/完全匹配 |
| 领域/分类相同 | 0.25 | 中 | domain/category字段相同 |
| 类型相容性 | 0.20 | 中 | 基于节点类型对的常见关系映射 |
| 文本相似度 | 0.15 | 弱 | 字符bigram Jaccard系数 |

**权重设计逻辑**：
- 精确匹配是最强信号（名称直接相关），权重最高
- 领域/分类是先验知识（同领域更可能相关），权重次高
- 类型相容性是结构化信号（document→concept常用defined_in），权重中等
- 纯文本相似度是兜底信号（字面相似），权重最低

### 中文文本相似度零依赖方案

对于短文本（节点名称、标签、标题），无需中文分词库：

```python
def _tokenize(text: str) -> set[str]:
    """简单分词：字符bigram + 单字符，无需外部依赖。"""
    text = text.strip().lower()
    tokens = set()
    for i in range(len(text) - 1):
        tokens.add(text[i:i+2])
    for char in text:
        if not char.isspace():
            tokens.add(char)
    return tokens

def _jaccard_similarity(s1: set[str], s2: set[str]) -> float:
    """Jaccard相似度 = 交集大小 / 并集大小。"""
    if not s1 or not s2:
        return 0.0
    intersection = len(s1 & s2)
    union = len(s1 | s2)
    return intersection / union if union > 0 else 0.0
```

**为什么字符bigram对中文短文本有效**：
- 中文词语通常是2-4个字，bigram能覆盖大部分词
- 节点名称/标签都是短文本（2-10个字），不需要复杂分词
- 零依赖，纯标准库，部署无负担

### 类型相容性矩阵

基于领域知识预设合理的关系类型映射，避免"人→事件"推荐"defined_in"这类不合理的关系：

```python
TYPE_RELATION_MAP = {
    frozenset(['document', 'concept']): ('defined_in', '概念定义'),
    frozenset(['person', 'concept']): ('contributed', '人物贡献'),
    frozenset(['person', 'event']): ('participated', '人物参与'),
    frozenset(['event', 'period']): ('belongs_to', '时期归属'),
    frozenset(['concept', 'concept']): ('related_to', '概念相关'),
}
```

## 核心代码实现

```python
from dataclasses import dataclass

@dataclass
class Suggestion:
    target_id: str
    target_label: str
    target_type: str
    score: float
    reasons: list[str]
    suggested_relation: str

def suggest_links(
    source_node: dict,
    candidate_nodes: list[dict],
    existing_edge_targets: set[str],
    top_k: int = 3,
) -> list[Suggestion]:
    """
    为源节点推荐可能的关联节点。
    
    多维度加权评分：标签匹配(40%) + 领域相同(25%) + 类型相容(20%) + 文本相似(15%)
    """
    suggestions = []
    source_tokens = _tokenize(source_node.get('label', '') + ' ' + source_node.get('description', ''))
    source_domain = source_node.get('domain', '')
    source_type = source_node.get('type', '')
    
    for candidate in candidate_nodes:
        candidate_id = candidate['id']
        if candidate_id == source_node['id'] or candidate_id in existing_edge_targets:
            continue
        
        score = 0.0
        reasons = []
        
        # 维度1：标签匹配（权重40%）
        candidate_label = candidate.get('label', '')
        label_score = _label_match_score(source_node.get('label', ''), candidate_label)
        if label_score > 0:
            score += 0.40 * label_score
            if label_score >= 0.9:
                reasons.append('标签完全匹配')
            elif label_score >= 0.6:
                reasons.append('标签包含关键词')
            else:
                reasons.append('标签共享字符')
        
        # 维度2：领域相同（权重25%）
        candidate_domain = candidate.get('domain', '')
        if source_domain and candidate_domain and source_domain == candidate_domain:
            score += 0.25
            reasons.append('同领域节点')
        
        # 维度3：类型相容性（权重20%）
        candidate_type = candidate.get('type', '')
        type_pair = frozenset([source_type, candidate_type])
        relation, relation_reason = TYPE_RELATION_MAP.get(type_pair, ('related_to', '默认相关'))
        type_score = 0.8 if type_pair in TYPE_RELATION_MAP else 0.3
        score += 0.20 * type_score
        
        # 维度4：文本相似度（权重15%）
        candidate_tokens = _tokenize(candidate_label + ' ' + candidate.get('description', ''))
        text_sim = _jaccard_similarity(source_tokens, candidate_tokens)
        if text_sim > 0.1:
            score += 0.15 * text_sim
            if not reasons:
                reasons.append('文本内容相似')
        
        if score > 0.2:
            suggestions.append(Suggestion(
                target_id=candidate_id,
                target_label=candidate_label,
                target_type=candidate_type,
                score=score,
                reasons=reasons,
                suggested_relation=relation,
            ))
    
    suggestions.sort(key=lambda s: s.score, reverse=True)
    return suggestions[:top_k]

def _label_match_score(label1: str, label2: str) -> float:
    """计算两个标签的匹配分数。"""
    if not label1 or not label2:
        return 0.0
    l1, l2 = label1.strip().lower(), label2.strip().lower()
    if l1 == l2:
        return 1.0
    if l1 in l2 or l2 in l1:
        return 0.8
    t1, t2 = _tokenize(l1), _tokenize(l2)
    return _jaccard_similarity(t1, t2)
```

## 输出格式规范

推荐结果必须包含三要素（与[human-in-the-loop-augmentation.md](../methodology-patterns/ai-collaboration/human-in-the-loop-augmentation.md)配套）：

1. **置信度分数**：0-100%，让用户快速筛选高质量推荐
2. **可解释理由**：说明"为什么推荐这个"，增强用户信任
3. **可操作片段**：直接给出可复制粘贴的代码/数据片段

```python
def print_suggestions(source_label: str, source_id: str, suggestions: list[Suggestion]):
    """格式化打印推荐结果。"""
    print(f"\n🔍 [{source_type}] {source_label} ({source_id}):")
    for i, s in enumerate(suggestions, 1):
        confidence = int(s.score * 100)
        reason_text = "、".join(s.reasons) if s.reasons else "综合评分"
        print(f"   {i}. [{confidence}%] → {s.target_label} [{s.target_type}]")
        print(f"      建议关系: {s.suggested_relation}")
        print(f"      理由: {reason_text}")
        # 直接输出可复制的字典片段
        edge_dict = f"{{'source': '{source_id}', 'target': '{s.target_id}', 'relation': '{s.suggested_relation}'}}"
        print(f"      添加: {edge_dict}")
```

## 验证结果：第一性原理知识图谱

**测试场景**：77个节点（24概念+17文档+19事件+4时期+13人物），176条边，5个孤立文档节点

**推荐效果**：

| 孤立节点 | Top 1推荐 | Top 1置信度 | 是否正确 |
|---------|----------|------------|---------|
| 第一性原理思维训练题库 | 第一性原理（概念） | 79% | ✅ 正确 |
| 第一性原理思维的认知科学基础 | 第一性原理（概念） | 79% | ✅ 正确 |
| AI时代的第一性原理应用 | 第一性原理（概念） | 79% | ✅ 正确 |
| 跨学科第一性原理案例库 | 第一性原理（概念） | 79% | ✅ 正确 |
| 第一性原理与类比推理的适用边界 | 第一性原理（概念） | 79% | ✅ 正确 |

**特殊案例验证**：
- 「第一性原理与类比推理的适用边界」Top 2正确推荐了「类比推理」概念（置信度79%）
- 算法正确识别了名称中包含的两个核心概念

**Top 1准确率**：100%（5/5）

## 复杂度分析

- **时间复杂度**：O(n × m)，其中n是孤立节点数，m是候选节点数
- **空间复杂度**：O(n + m)
- **实测性能**：77节点规模下，运行时间<10ms（纯Python，无任何加速）
- **适用上限**：~500节点时运行时间仍<100ms，可接受；超过1000节点建议升级方案

## 调优指南

### 权重调整

根据你的场景调整权重：

| 场景 | 标签匹配 | 领域相同 | 类型相容 | 文本相似 | 调整理由 |
|------|---------|---------|---------|---------|---------|
| 知识图谱（强结构化） | 0.40 | 0.25 | 0.20 | 0.15 | 默认值，结构化信息丰富 |
| 纯文本文档推荐 | 0.20 | 0.10 | 0.00 | 0.70 | 文本是主要信号 |
| 标签/分类推荐 | 0.50 | 0.20 | 0.10 | 0.20 | 标签精确匹配最重要 |
| 代码实体推荐 | 0.30 | 0.10 | 0.40 | 0.20 | 类型相容性非常重要 |

### 阈值调整

- **置信度阈值**：默认0.2（低于20%不显示），高质量场景可提高到0.4
- **Top-K数量**：默认3，推荐数量不要超过5，避免选择负担
- **分数校准**：实测一段时间后，根据用户采纳率调整各维度权重

### 扩展维度

可以根据场景添加更多评分维度：
- **连接度偏好**：优先推荐连接数适中的节点（避免"富者愈富"）
- **时间衰减**：近期创建/修改的节点优先级更高
- **共同邻居**：与源节点共享多个邻居的节点评分加成
- **人工反馈**：记录用户历史采纳/拒绝，个性化调整权重

## 反模式与陷阱

### 陷阱1：过度工程——一开始就上ML/embedding

**错误**：还没到1000节点，就引入numpy、sklearn、sentence-transformers，导致依赖地狱、部署复杂、冷启动慢。

**正确做法**：先用本模式的零依赖方案实现，验证推荐效果，当规模>1000且本方案效果不满意时，再考虑升级到ML方案。

### 陷阱2：单一维度——只看文本相似度

**错误**：只用Jaccard或编辑距离，导致"第一因"和"第一性原理"相似度很高但其实是不同概念。

**正确做法**：多维度加权评分，用类型、领域等结构化信号修正纯文本相似度的误判。

### 陷阱3：黑箱输出——只给分数不给理由

**错误**：只输出"推荐A，分数0.89"，用户不知道为什么推荐A，不敢信任。

**正确做法**：每个推荐附带明确理由（"标签包含关键词"、"同领域"等），理由是用户信任的基础。

### 陷阱4：格式不友好——输出需要人工转换

**错误**：输出一堆ID列表，用户需要自己查标签、自己构建字典/JSON。

**正确做法**：直接输出可复制粘贴的代码片段，零转换成本。

## 与其他模式的关系

| 关联模式 | 关系类型 | 关系说明 |
|---------|---------|---------|
| [human-in-the-loop-augmentation.md](../methodology-patterns/ai-collaboration/human-in-the-loop-augmentation.md) | **配套使用** | 本算法是人机协作模式的推荐层实现，两者经常一起使用 |
| [dict-comprehension-simplification.md](../methodology-patterns/tools-automation/dict-comprehension-simplification.md) | **代码风格** | 评分计算使用字典推导式保持代码简洁 |
| [semi-structured-parsing-complexity-budget.md](../methodology-patterns/tools-automation/semi-structured-parsing-complexity-budget.md) | **理念一致** | 半结构化解析复杂度预算强调"够用就好"，本算法同样遵循简单优先 |

## 升级路径

当规模或需求超出本模式能力时，按以下路径渐进升级：

1. **阶段1（<500节点）**：本模式——零依赖多维度加权评分（已验证，足够用）
2. **阶段2（500-2000节点）**：添加TF-IDF（仍纯Python，sklearn可选），提升文本匹配精度
3. **阶段3（2000-10000节点）**：引入sentence-transformers本地embedding，增加语义匹配能力
4. **阶段4（>10000节点）**：向量数据库（FAISS/Milvus）+ ANN检索，支持大规模实时推荐

**重要**：不要跳级升级！每个阶段都应该在前一个阶段验证不能满足需求后再升级。

> 来源：第一性原理知识图谱可视化开发复盘（retrospective-first-principles-knowledge-graph-20260709），IMP-004孤立节点关联建议功能验证
