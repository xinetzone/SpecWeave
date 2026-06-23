> **来源**：从 `docs/retrospective/knowledge-extraction.md` 一、可复用代码模式 拆分

# 元文档识别

## 来源
`check-spec-consistency.py` — `is_retrospective_context()` → `detect_meta_document()`

## 代码
```python
_META_DOC_KEYWORDS = ['复盘', '回顾', '审计', '评审', '评估', '对比', '迁移']

def is_meta_document(text: str) -> bool:
    """检测文档是否为元文档（描述其他文档/项目的文档）。"""
    return any(kw in text for kw in _META_DOC_KEYWORDS)

def check_data_consistency(data_refs, actual_stats, is_meta=False):
    """数据一致性检查，区分自引用与外部引用。"""
    for desc, expected in data_refs.items():
        if expected == actual:
            result.append(f"✓ {desc}: 一致")
        else:
            if is_meta:
                result.append(f"⚠ {desc}: 疑似引用外部项目数据（警告）")
            else:
                result.append(f"✗ {desc}: 不一致（错误）")
```

## 复用场景
任何需要区分"自引用数据"与"外部引用数据"的文档检查工具。

> **关联模块**：
> - `concepts/meta-document.md`
> - `frameworks/meta-document-processing-matrix.md`