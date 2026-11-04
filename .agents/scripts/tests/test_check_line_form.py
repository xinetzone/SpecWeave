"""check-line-form 单元测试。

**为什么要有这份夹具**：本工具的价值完全取决于「报得准」。上一版用「行首白名单」
判据时全仓误报 525 条——闸门误报多了会被整体忽略，那时闸门就真的没了。所以
必须有**正样本**（正常文档必须零误报）与**负样本**（真故障必须报出）两侧夹具，
否则「改判据」就退化成「调参调到看不见」。

脚本文件名带连字符，不能直接 import，故用 importlib 加载。
"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import importlib.util
import sys

SCRIPTS_DIR = _Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

_spec = importlib.util.spec_from_file_location(
    "check_line_form", SCRIPTS_DIR / "check-line-form.py"
)
clf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(clf)


# ── 正样本：正常文档，零误报 ────────────────────────────────────────────────

NORMAL_MARKDOWN = """---
id: demo
title: 示例文档
---

# 一级标题

这是一段正文，含行内代码 `a-b` 与强调 **加粗**、*斜体*、`code`。

- 列表项一
- 列表项二
  - 嵌套项
    缩进续行段落

| 列一 | 列二 |
| --- | --- |
| 数据 | 值 |

```python
x = 1  # 注释
```

> 引用块

正文里出现 A- B 这种英文区间写法，还有 2024-01-01 与 3-4 分钟。

参见 [链接](https://example.com) 与 `#123` 引用，以及 `code | pipe` 这种内容。
"""

NESTED_FENCE = """````markdown
```js
const a = 1;
```
````
"""

TREE_IN_TABLE = """| 目录 | 说明 |
| --- | --- |
|   |   +-- sidenav-icon/             # 侧边导航专用图标（53 个） |
|   |   +-- *.svg                     # 通用图标 |
"""

NORMAL_PYTHON = '''"""模块说明。

这里的自由文本里出现 - 破折号 和 > 符号 都不该被当成结构标记。
"""

from pathlib import Path


def pick(flag: bool) -> Path | None:
    """docstring 里也可能有 - 破折号。"""
    negative = -1
    if flag:
        return Path("x") | None
    return None
'''


# ── 负样本：真故障，必须报出 ────────────────────────────────────────────────

UNCLOSED_FENCE = """# 标题

```python
x = 1
"""

UNCLOSED_FRONTMATTER = """---
id: demo
title: 没有结束分隔线

正文。
"""

MERGED_TABLE_ROW = """| 名称 | 说明 |
| --- | --- |
| a | 说明一 |
| b | 说明二 | 多出来的一列 |
"""


def _rules(text: str, suffix: str = ".md") -> list[str]:
    """返回扫描命中的规则名列表。"""
    return [issue.rule for issue in clf.scan_text(text, suffix)]


# ── 正样本测试 ──────────────────────────────────────────────────────────────


def test_normal_markdown_has_no_issue():
    """正常 Markdown 必须零命中——这是「闸门不能被整体忽略」的前提。"""
    assert _rules(NORMAL_MARKDOWN) == []


def test_frontmatter_is_ignored():
    """frontmatter 内的键值对不应被判成结构标记。"""
    assert _rules("---\nid: x\ntitle: y\n---\n\n正文\n") == []


def test_nested_fence_is_paired():
    """嵌套围栏（外层四反引号内含三反引号）按 CommonMark 规则配对成功。"""
    assert _rules(NESTED_FENCE) == []


def test_tree_inside_table_is_allowed():
    """表格里塞目录树是合法用法，不能按坏表格报。"""
    assert _rules(TREE_IN_TABLE) == []


def test_python_docstring_and_operators_are_ignored():
    """Python 的 docstring 自由文本、`|` 运算符、负数都不该被当成 Markdown 标记。"""
    assert _rules(NORMAL_PYTHON, ".py") == []


def test_table_with_pipes_in_cells_is_consistent():
    """单元格内容含未转义竖线时，若各行列数一致则不算坏表格。"""
    text = "| a | b |\n| --- | --- |\n| x | y |\n"
    assert _rules(text) == []


# ── 负样本测试 ──────────────────────────────────────────────────────────────


def test_unclosed_fence_is_detected():
    """围栏未闭合是吞行的典型后果，必须报出。"""
    assert clf.RULE_FENCE_UNPAIRED in _rules(UNCLOSED_FENCE)


def test_unclosed_frontmatter_is_detected():
    """frontmatter 未闭合必须报出。"""
    assert clf.RULE_FRONTMATTER_UNCLOSED in _rules(UNCLOSED_FRONTMATTER)


def test_merged_table_row_is_detected():
    """表格里某行列数多于其余行——两行被合并的特征，必须报出。"""
    rules = _rules(MERGED_TABLE_ROW)
    assert clf.RULE_TABLE_COLUMNS in rules


def test_short_table_row_is_not_reported():
    """列数**少于**基准是漏写列的另一种坏表格，与吞行无关，不该由本工具报。"""
    text = "| 名称 | 说明 | 备注 |\n| --- | --- | --- |\n| a | 说明一 |\n"
    assert clf.RULE_TABLE_COLUMNS not in _rules(text)


# ── 工具自身有效性 ──────────────────────────────────────────────────────────


def test_detector_fires_on_every_negative_sample():
    """负样本必须全部被检出——「核验通过」的前提是核验器本身有效。"""
    negatives = [UNCLOSED_FENCE, UNCLOSED_FRONTMATTER, MERGED_TABLE_ROW]
    for text in negatives:
        assert _rules(text), f"负样本未被检出：{text[:40]!r}"


def test_detector_is_quiet_on_all_positive_samples():
    """正样本必须全部零命中。"""
    positives = [
        (NORMAL_MARKDOWN, ".md"),
        (NESTED_FENCE, ".md"),
        (TREE_IN_TABLE, ".md"),
        (NORMAL_PYTHON, ".py"),
    ]
    for text, suffix in positives:
        assert _rules(text, suffix) == [], f"正样本被误报：{text[:40]!r}"


def test_no_phantom_rule_ids():
    """规则常量与实际使用的一致，避免改了判定却忘了改标识。"""
    used = {
        clf.RULE_INLINE_MARKER,
        clf.RULE_INLINE_MARKER_CJK,
        clf.RULE_FENCE_UNPAIRED,
        clf.RULE_FRONTMATTER_UNCLOSED,
        clf.RULE_TABLE_COLUMNS,
        clf.RULE_MARKER_NO_SPACE,
        clf.RULE_PY_UNTOKENIZABLE,
    }
    assert used == set(clf.HARD_RULES) | set(clf.VERBOSE_RULES) | {
        clf.RULE_PY_UNTOKENIZABLE
    }
