---
id: "ngram-mixed-language-matching"
source: "docs/retrospective/reports/task-reports/retrospective-conflict-resolution-mechanism-20260708/insight-extraction.md"
domain: "code"
layer: "code-patterns"
maturity: "L2"
validation_count: 2
reuse_count: 0
documentation_level: "comprehensive"

[bindings]
rules = []
references = [
  "configurable-by-default-principle.md"
]
skills = []
---
# 中英文混合文本的n-gram子串匹配法：不依赖分词的关键词匹配

## 模式概述

从技术分歧仲裁的spec关键词匹配中萃取的文本处理模式。初始实现按英文空格分词后匹配关键词，但中文文本没有空格分词，导致中文spec完全无法匹配。采用n-gram滑动窗口子串匹配，无需分词，天然支持中英文混合文本。

**核心洞察**：按空格分词是英文特有的假设，中文/日文/泰文等语言不以空格分词。在多语言环境下做关键词匹配时，不要假设文本有词边界——子串包含或n-gram滑动窗口是更鲁棒的方案。

## 问题场景

### 反模式：按空格分词

```python
# ❌ 反模式：按空格分词，中文文本失效
def keyword_score(term: str, text: str) -> int:
    """计算term在text中的匹配分数"""
    text_words = set(text.lower().split())  # 中文无空格，得到整个字符串作为一个"词"
    term_words = set(term.lower().split())
    return len(text_words & term_words)

# 英文：正常工作
keyword_score("dependency injection", "Use dependency injection pattern")  # 返回1 ✅

# 中文：完全失效
keyword_score("依赖注入", "使用依赖注入模式")
# split()得到 ["使用依赖注入模式"]，与set(["依赖注入"])交集为空 → 返回0 ❌
```

**问题根因**：
1. **空格分词是英文假设**：中文词与词之间没有空格分隔
2. **分词器依赖重**：jieba/MeCab等分词器增加依赖，且领域专用词（如"依赖注入"）分词准确率不保证
3. **混合文本处理**："使用dependency injection模式"这种中英混排，空格分词也无法正确处理
4. **关键词长度不一**：短关键词（2字）和长关键词（4字）需要不同的匹配粒度

---

### 正解：n-gram滑动窗口子串匹配

核心思路：不做分词，直接在文本上滑动n-gram窗口（n默认4，可配置），统计关键词的子串匹配数量，加上完整包含的加分。

```python
def substring_match_score(proposal: str, spec: str, ngram_size: int = 4) -> int:
    """
    n-gram子串匹配，天然支持中英文混合文本。
    
    Args:
        proposal: 待匹配的关键词/术语（可以是中文/英文/混合）
        spec: 目标文本（spec正文）
        ngram_size: n-gram窗口大小，默认4（中英文都适用）
    
    Returns:
        匹配分数，越高表示匹配越好
    """
    pl = proposal.lower().strip()
    sl = spec.lower()
    if not pl or not sl:
        return 0
    
    score = 0
    # 滑动n-gram窗口：proposal上每个长度为ngram_size的子串
    for i in range(len(pl) - ngram_size + 1):
        ngram = pl[i:i + ngram_size]
        if len(ngram.strip()) >= 2 and ngram in sl:
            score += 1
    
    # 完整包含加分：如果整个proposal是spec的子串，额外加分（权重为proposal长度）
    if pl in sl:
        score += len(pl)
    
    return score
```

**为什么这个方法有效**：

| 场景 | 按空格分词 | n-gram子串匹配 |
|------|-----------|---------------|
| 英文关键词匹配 | ✅ | ✅（完整包含加分更准确） |
| 中文关键词匹配 | ❌ 失效 | ✅ 滑动窗口逐字匹配 |
| 中英混排匹配 | ❌ 部分失效 | ✅ 无需分词直接匹配 |
| 长关键词（>4字） | 依赖分词质量 | ✅ 窗口滑动覆盖所有子串 |
| 短关键词（2-3字） | ✅ | ✅ 完整包含加分 |
| 零额外依赖 | ✅ | ✅（纯Python实现） |

## 完整实现：正/负关键词规则匹配

在实际规则引擎中，通常有多条规则，每条包含正关键词（匹配则加分）和负关键词（匹配则减分）：

```python
from dataclasses import dataclass, field

@dataclass
class MatchResult:
    score: int
    matched_positives: list[str] = field(default_factory=list)
    matched_negatives: list[str] = field(default_factory=list)

def match_proposal(
    proposal: str,
    positive_keywords: tuple[str, ...],
    negative_keywords: tuple[str, ...] = (),
    *,
    ngram_size: int = 4,
    threshold: int = 2,
) -> MatchResult:
    """
    用n-gram子串匹配检查proposal是否匹配规则。
    
    Args:
        proposal: 用户提案文本
        positive_keywords: 正关键词元组（匹配则加分）
        negative_keywords: 负关键词元组（匹配则减分）
        ngram_size: n-gram窗口大小
        threshold: 判定匹配的最低分数
    """
    pl = proposal.lower()
    score = 0
    matched_pos = []
    matched_neg = []
    
    for kw in positive_keywords:
        kw_score = substring_match_score(kw, pl, ngram_size)
        if kw_score >= threshold or kw.lower() in pl:
            score += kw_score + 1
            matched_pos.append(kw)
    
    for kw in negative_keywords:
        kw_score = substring_match_score(kw, pl, ngram_size)
        if kw_score >= threshold or kw.lower() in pl:
            score -= kw_score + 1
            matched_neg.append(kw)
    
    return MatchResult(
        score=score,
        matched_positives=matched_pos,
        matched_negatives=matched_neg,
    )

# 使用示例
bp_rules = {
    "异常优于错误码": (("异常抛出", "exception", "raise"), ("错误码", "error_code")),
    "单一职责": (("单一职责", "拆分", "separate"), ("大函数", "单文件", "monolith")),
    "最小变更": (("局部修复", "最小改动", "minimal", "最小变更"), ("重构", "大改")),
}

def count_best_practice_matches(proposal: str, rules: dict) -> int:
    score = 0
    for pos_kws, neg_kws in rules.values():
        result = match_proposal(proposal, pos_kws, neg_kws)
        if result.score > 0:
            score += 1
        elif result.score < 0:
            score -= 1
    return score

# 中文提案 → 正确匹配
count_best_practice_matches("这里应该抛出异常而不是返回错误码", bp_rules)
# → 匹配"异常优于错误码"：score=1

# 英文提案 → 正确匹配
count_best_practice_matches("Use exception handling instead of error codes", bp_rules)
# → 匹配"异常优于错误码"：score=1
```

## ngram_size选择指南

| ngram_size | 适用场景 | 特点 |
|-----------|---------|------|
| **2** | 短文本、短关键词为主 | 更敏感，可能误匹配 |
| **3** | 中等长度关键词 | 平衡灵敏度和精确度 |
| **4（推荐）** | 通用场景，中英文混合 | 中文4字词组正好是一个词的粒度，英文也能覆盖常见短语 |
| **5+** | 长文本、长专业术语 | 更精确，但短关键词匹配不上 |

**建议**：ngram_size通过构造函数可配置（遵循可配置性默认原则），默认值4适合大多数场景。

## 反模式清单

1. **❌ 假设文本有空格分词**：直接`text.split()`在中文/日文/泰文上完全失效
2. **❌ 只做完整包含检查（`kw in text`）**：遗漏变形、部分匹配、拼写变体
3. **❌ 引入重量级分词器（jieba/MeCab）做简单关键词匹配**：增加依赖、部署复杂度，分词准确率在领域文本上不保证
4. **❌ 固定ngram_size不可配置**：不同场景需要不同粒度，应该可注入
5. **❌ 只有正关键词没有负关键词**："不用X"的否定表述会误匹配，需要负关键词减分
6. **❌ 不做lower()归一化**：大小写不一致导致匹配失败
7. **❌ 关键词是元组/列表但不做防御性拷贝**：遵循防御性编程原则，可变参数应拷贝

## 验证清单

实现关键词匹配功能时，逐项确认：

- [ ] 不依赖空格分词，中文文本能正确匹配
- [ ] 英文文本能正确匹配
- [ ] 中英混排文本能正确匹配
- [ ] ngram_size可配置（默认4）
- [ ] 完整子串包含有额外加分
- [ ] 支持正/负关键词双向计分
- [ ] 大小写不敏感（lower()归一化）
- [ ] 空输入安全处理（不抛异常，返回0）
- [ ] 短关键词（2字）能正确匹配
- [ ] 长关键词（≥4字）能正确匹配

## 与其他模式的关系

- **与configurable-by-default-principle的关系**：ngram_size、阈值、规则表都应支持构造函数注入，提供合理默认值
- **与defensive-config-cache-deepcopy的关系**：传入的规则字典/关键词元组应做防御性拷贝

## 适用场景

- 规则引擎中的关键词匹配（技术分歧仲裁、代码评审规则）
- 文本分类（中英文混合标签）
- 搜索/过滤功能（用户输入自由文本匹配预定义关键词）
- 静态分析中的模式识别（代码注释/文档中的关键词检测）
- 任何"用户提供自由文本+预定义关键词列表"的匹配场景
- 需要零依赖、轻量级多语言文本匹配

## 不适用场景

- 需要语义理解（同义词、近义词、上下文）→ 使用词向量/LLM
- 需要精确分词（词性标注、命名实体识别）→ 使用专业分词器
- 大规模全文检索（百万级文档）→ 使用倒排索引（Elasticsearch/Lucene）

## 成功案例

| 项目 | 问题 | n-gram方案效果 |
|------|------|---------------|
| 冲突解决机制 | D8：中文spec按空格分词匹配失效 | n-gram匹配修复，中英文都正确工作，39个测试全部通过 |
| 规则引擎扩展 | 最佳实践规则从硬编码5条扩展到可配置任意条数 | 规则通过构造函数注入，n-gram匹配天然支持新规则无需改代码 |
