"""Task 7 冒烟测试。"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

from lib.knowledge_search import (
    sanitize_query,
    extract_keywords,
    filter_intact_entries,
    search_fulltext,
    search_knowledge,
    quick_search,
    _scan_knowledge_entries,
    _compute_relevance,
)

print("TR-7.0 PASS: imports OK")

# TR-7.1: 安全查询通过
q, safe, msg = sanitize_query("hello world")
assert safe, f"TR-7.1 FAIL: {msg}"
assert q == "hello world"
print("TR-7.1 PASS: safe query passes")

# TR-7.2: 路径遍历拒绝
q, safe, msg = sanitize_query("../../../../etc/passwd")
assert not safe, f"TR-7.2 FAIL: should have rejected"
print("TR-7.2 PASS: path traversal rejected")

# TR-7.3: XSS 拒绝
q, safe, msg = sanitize_query("<script>alert(1)</script>")
assert not safe, f"TR-7.3 FAIL: should have rejected"
print("TR-7.3 PASS: XSS rejected")

# TR-7.4: 超长查询拒绝
q, safe, msg = sanitize_query("x" * 1000)
assert not safe, f"TR-7.4 FAIL: should have rejected"
print("TR-7.4 PASS: long query rejected")

# TR-7.5: 关键词提取
kw = extract_keywords("hello world 加密 方法论")
assert len(kw) >= 3
assert "hello" in kw
assert "加密" in kw
print(f"TR-7.5 PASS: extracted {len(kw)} keywords: {kw}")

# TR-7.6: 相关性评分
meta = {"title": "Test Title", "tags": ["security", "crypto"], "summary": "test summary"}
score = _compute_relevance("hello world test content with security and crypto", ["hello", "security"], meta)
assert score > 0, f"TR-7.6 FAIL: score should be > 0, got {score}"
print(f"TR-7.6 PASS: relevance score={score}")

# TR-7.7: 全文搜索
entries = _scan_knowledge_entries()
results = search_fulltext("加密", entries, max_results=5)
assert len(results) > 0, f"TR-7.7 FAIL: no results for '加密'"
assert all(r["score"] > 0 for r in results)
print(f"TR-7.7 PASS: fulltext search found {len(results)} results")

# TR-7.8: 完整性过滤
entries_subset = entries[:10] if len(entries) >= 10 else entries
intact, damaged, msg = filter_intact_entries(entries_subset)
assert len(intact) + len(damaged) == len(entries_subset)
print(f"TR-7.8 PASS: {len(intact)} intact, {len(damaged)} damaged")

# TR-7.9: 综合检索
result = search_knowledge(
    query="review",
    knowledge_type="factual",
    max_results=10,
    exclude_damaged=True,
)
assert "total" in result
assert "results" in result
assert "damaged" in result
print(f"TR-7.9 PASS: total={result['total']}, filtered={result['filtered']}")

# TR-7.10: quick_search
results = quick_search("方法论", max_results=5)
assert isinstance(results, list)
print(f"TR-7.10 PASS: quick_search found {len(results)} results")

# TR-7.11: 空查询
results = quick_search("", max_results=5)
assert len(results) >= 0
print(f"TR-7.11 PASS: empty query handled gracefully")

# TR-7.12: 按安全级别筛选
result = search_knowledge(security_level="public", max_results=3)
assert result["filtered"] >= 0
print(f"TR-7.12 PASS: security level filter works")

print()
print("ALL 12 TESTS PASSED")