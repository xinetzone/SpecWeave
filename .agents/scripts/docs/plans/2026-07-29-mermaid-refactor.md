# Mermaid 检查模块重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 重构 mermaid.py 模块，采用策略模式和职责拆分，消除代码重复，提升可测试性和可维护性，同时保持完全向后兼容性。

**Architecture:** 采用渐进式重构策略，将通用工具函数、检查器、修复器、扫描器和运行器逐步提取到独立模块中。保持 mermaid.py 作为兼容层，使用新模块的实现并暴露原有函数接口，确保现有测试和调用方无需修改。

**Tech Stack:** Python 3.11+, abc (抽象基类), typing (类型提示), pytest (测试), pathlib (路径处理)

---

## 文件结构规划

**新建文件：**
- `.agents/scripts/lib/mermaid/__init__.py` - 模块入口
- `.agents/scripts/lib/mermaid/common.py` - 公共工具函数（正则、工具方法）
- `.agents/scripts/lib/mermaid/checkers/__init__.py` - 检查器模块入口
- `.agents/scripts/lib/mermaid/checkers/base.py` - 检查器抽象基类
- `.agents/scripts/lib/mermaid/checkers/security.py` - 安全检查器
- `.agents/scripts/lib/mermaid/checkers/flowchart.py` - 流程图检查器
- `.agents/scripts/lib/mermaid/checkers/state_diagram.py` - 状态图检查器
- `.agents/scripts/lib/mermaid/checkers/sequence_diagram.py` - 序列图检查器
- `.agents/scripts/lib/mermaid/checkers/class_diagram.py` - 类图检查器
- `.agents/scripts/lib/mermaid/checkers/er_diagram.py` - ER图检查器
- `.agents/scripts/lib/mermaid/checkers/mindmap.py` - 思维导图检查器
- `.agents/scripts/lib/mermaid/checkers/generic.py` - 通用检查器
- `.agents/scripts/lib/mermaid/fixers/__init__.py` - 修复器模块入口
- `.agents/scripts/lib/mermaid/fixers/base.py` - 修复器抽象基类
- `.agents/scripts/lib/mermaid/fixers/flowchart.py` - 流程图修复器
- `.agents/scripts/lib/mermaid/fixers/state_diagram.py` - 状态图修复器
- `.agents/scripts/lib/mermaid/fixers/sequence_diagram.py` - 序列图修复器
- `.agents/scripts/lib/mermaid/fixers/class_diagram.py` - 类图修复器
- `.agents/scripts/lib/mermaid/fixers/er_diagram.py` - ER图修复器
- `.agents/scripts/lib/mermaid/fixers/mindmap.py` - 思维导图修复器
- `.agents/scripts/lib/mermaid/fixers/generic.py` - 通用修复器
- `.agents/scripts/lib/mermaid/scanner.py` - 文件扫描器
- `.agents/scripts/lib/mermaid/runner.py` - 运行器（含输出接口）
- `.agents/scripts/lib/mermaid/registry.py` - 策略注册表
- `.agents/scripts/lib/mermaid/processor.py` - 文件处理器

**修改文件：**
- `.agents/scripts/lib/checks/mermaid.py` - 重构为兼容层，使用新模块实现
- `.agents/scripts/tests/test_checks_mermaid.py` - 更新导入路径，添加新模块测试

---

### Task 1: 创建公共工具模块 common.py

**Files:**
- Create: `.agents/scripts/lib/mermaid/__init__.py`
- Create: `.agents/scripts/lib/mermaid/common.py`
- Test: `.agents/scripts/tests/test_mermaid_common.py`

- [ ] **Step 1: 创建 mermaid 目录和 __init__.py**

```bash
mkdir -p .agents/scripts/lib/mermaid/checkers .agents/scripts/lib/mermaid/fixers
```

- [ ] **Step 2: 编写 common.py，提取通用正则和工具函数**

创建 `.agents/scripts/lib/mermaid/common.py`：

```python
"""Mermaid 检查公共工具模块。

包含所有检查器/修复器共享的正则表达式、工具函数和常量。
"""

import re
from pathlib import Path
from typing import List, Tuple

MERMAID_FENCE_RE = re.compile(r"(```mermaid\s*\n)(.*?)(```)", re.DOTALL)
CHINESE_CHARS_RE = re.compile(r"[\u4e00-\u9fff]")
SPECIAL_CHARS = "@#≥≤+"
LIST_TRIGGER_RE = re.compile(r'^[-*+]\s|^\d+[.．、]\s')


def detect_diagram_type(block_text: str) -> str:
    """检测 Mermaid 代码块的图表类型。"""
    first_line = block_text.strip().split("\n")[0].strip()
    if not first_line:
        return "unknown"
    diagram_type = first_line.split()[0].lower()
    if diagram_type in ("flowchart", "graph"):
        return "flowchart"
    if diagram_type.startswith("statediagram"):
        return "stateDiagram"
    if diagram_type == "sequencediagram":
        return "sequenceDiagram"
    if diagram_type == "classdiagram":
        return "classDiagram"
    if diagram_type == "erdiagram":
        return "erDiagram"
    if diagram_type == "pie":
        return "pie"
    if diagram_type == "gantt":
        return "gantt"
    if diagram_type in ("timeline", "mindmap", "xychart-beta", "quadrantchart"):
        return diagram_type
    return "flowchart"


def text_needs_quotes(ntxt: str) -> bool:
    """判断文本是否需要引号包裹。"""
    if ntxt.startswith('"') and ntxt.endswith('"'):
        return False
    if ntxt.startswith("'") and ntxt.endswith("'"):
        return False
    return bool(CHINESE_CHARS_RE.search(ntxt) or any(c in ntxt for c in SPECIAL_CHARS) or " " in ntxt.strip())


def state_text_needs_quotes(ntxt: str) -> bool:
    """判断状态图文本是否需要引号包裹。"""
    if ntxt.startswith('"') and ntxt.endswith('"'):
        return False
    if ntxt.startswith("'") and ntxt.endswith("'"):
        return False
    if " " in ntxt.strip():
        return True
    dangerous = ":;{}|->"
    return any(c in ntxt for c in dangerous)


def has_list_trigger(text: str) -> bool:
    """检查文本是否以列表标记开头。"""
    stripped = text.strip().strip('"').strip("'")
    return bool(LIST_TRIGGER_RE.match(stripped))


def line_from_offset(content: str, offset: int) -> int:
    """根据偏移量计算行号。"""
    return content[:offset].count("\n") + 1


def strip_inline_comment(line: str) -> str:
    """移除行内 Mermaid 注释（%% 后的内容），返回代码部分。"""
    stripped = line.lstrip()
    if stripped.startswith("%%"):
        return ""
    if "%%" in line:
        return line.split("%%", 1)[0]
    return line


def check_empty_lines(block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
    """检查代码块中的空行问题。"""
    issues = []
    if "\n\n" in block_text or "\n \n" in block_text:
        issues.append((start_line, "error", "Mermaid 代码块内存在空行，可能导致解析中断"))
    return issues


def check_backslash_n(block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
    """检查代码块中的 \n 换行符问题。"""
    issues = []
    for i, line in enumerate(block_text.split("\n")):
        code_part = strip_inline_comment(line)
        if not code_part.strip():
            continue
        j = 0
        while True:
            idx = code_part.find("\\n", j)
            if idx == -1:
                break
            issues.append((start_line + i, "error",
                          f'节点/标签文本中使用了 \\n 换行符，应使用 <br/> 而非 \\n'))
            j = idx + 2
    return issues


def fix_backslash_n(text: str) -> str:
    """修复代码块中的 \n 换行符为 <br/>。"""
    lines = text.split("\n")
    result = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("%%"):
            result.append(line)
            continue
        if "%%" in line:
            code, comment = line.split("%%", 1)
            result.append(code.replace("\\n", "<br/>") + "%%" + comment)
        else:
            result.append(line.replace("\\n", "<br/>"))
    return "\n".join(result)


def fix_empty_lines(text: str) -> str:
    """修复代码块中的空行问题。"""
    return re.sub(r"\n[ \t]*\n+", "\n", text)


def check_list_trigger(text: str, line_offset: int, start_line: int,
                       context: str) -> Tuple[int, str, str] | None:
    """检查文本是否触发列表解析警告。"""
    if has_list_trigger(text):
        return (start_line + line_offset, "warning",
                f'{context}文本「{text.strip()[:20]}」以列表标记开头，可能触发Markdown列表解析')
    return None


def strip_mindmap_shape(text: str) -> str:
    """剥离思维导图节点的形状包裹，返回纯文本。"""
    t = text.strip()
    if t.startswith("<!--") and t.endswith("-->"):
        return ""
    dual_delims = [
        (r'^\(\((.+)\)\)$', 1),
        (r'^\(\[(.+)\]\)$', 1),
        (r'^\[\[(.+)\]\]$', 1),
        (r'^>\((.+)\)$', 1),
    ]
    for pat, grp in dual_delims:
        m = re.match(pat, t)
        if m:
            return m.group(grp)
    single_delims = [
        (r'^\((.+)\)$', 1),
        (r'^\[(.+)\]$', 1),
        (r'^\{(.+)\}$', 1),
    ]
    id_dual = re.match(r'^([A-Za-z][A-Za-z0-9_]*)(\(\(|\(\[|\[\[|>\()(.+?)(\)\)|\)\]|\]\]|\))$', t)
    if id_dual:
        return id_dual.group(3)
    id_single = re.match(r'^([A-Za-z][A-Za-z0-9_]*)(\(|\[|\{)(.+?)(\)|\]|\})$', t)
    if id_single:
        return id_single.group(3)
    for pat, grp in single_delims:
        m = re.match(pat, t)
        if m:
            return m.group(grp)
    return t
```

- [ ] **Step 3: 创建 __init__.py 模块入口**

创建 `.agents/scripts/lib/mermaid/__init__.py`：

```python
"""Mermaid 语法安全检查模块（重构版）。

采用策略模式和职责拆分的新架构，保持与旧版 mermaid.py 的完全向后兼容。
"""

from .common import (
    MERMAID_FENCE_RE,
    CHINESE_CHARS_RE,
    detect_diagram_type,
    text_needs_quotes,
    state_text_needs_quotes,
    has_list_trigger,
    line_from_offset,
    strip_inline_comment,
    check_empty_lines,
    check_backslash_n,
    fix_backslash_n,
    fix_empty_lines,
    check_list_trigger,
    strip_mindmap_shape,
)

__all__ = [
    "MERMAID_FENCE_RE",
    "CHINESE_CHARS_RE",
    "detect_diagram_type",
    "text_needs_quotes",
    "state_text_needs_quotes",
    "has_list_trigger",
    "line_from_offset",
    "strip_inline_comment",
    "check_empty_lines",
    "check_backslash_n",
    "fix_backslash_n",
    "fix_empty_lines",
    "check_list_trigger",
    "strip_mindmap_shape",
]
```

- [ ] **Step 4: 编写 common.py 的单元测试**

创建 `.agents/scripts/tests/test_mermaid_common.py`：

```python
"""mermaid.common 模块单元测试。"""

import pytest
from pathlib import Path

from lib.mermaid import common


class TestDetectDiagramType:
    """diagram 类型检测测试。"""

    def test_flowchart(self):
        assert common.detect_diagram_type("graph TD\n    A --> B") == "flowchart"
        assert common.detect_diagram_type("flowchart TD\n    A --> B") == "flowchart"

    def test_statediagram(self):
        assert common.detect_diagram_type("stateDiagram-v2\n    [*] --> A") == "stateDiagram"

    def test_sequencediagram(self):
        assert common.detect_diagram_type("sequenceDiagram\n    A->>B: Hello") == "sequenceDiagram"

    def test_classdiagram(self):
        assert common.detect_diagram_type("classDiagram\n    class A") == "classDiagram"

    def test_erdiagram(self):
        assert common.detect_diagram_type("erDiagram\n    CUSTOMER ||--o{ ORDER") == "erDiagram"

    def test_pie(self):
        assert common.detect_diagram_type("pie title Pets\n    \"Dogs\": 386") == "pie"

    def test_gantt(self):
        assert common.detect_diagram_type("gantt\n    title A Gantt Diagram") == "gantt"

    def test_mindmap(self):
        assert common.detect_diagram_type("mindmap\n    root((Root))") == "mindmap"

    def test_empty_returns_unknown(self):
        assert common.detect_diagram_type("") == "unknown"

    def test_unknown_defaults_to_flowchart(self):
        assert common.detect_diagram_type("someUnknownDiagram\n    stuff") == "flowchart"


class TestTextNeedsQuotes:
    """引号需求判断测试。"""

    def test_already_double_quoted(self):
        assert common.text_needs_quotes('"Hello"') is False

    def test_already_single_quoted(self):
        assert common.text_needs_quotes("'Hello'") is False

    def test_chinese_needs_quotes(self):
        assert common.text_needs_quotes("开始") is True

    def test_space_needs_quotes(self):
        assert common.text_needs_quotes("Hello World") is True

    def test_special_chars_needs_quotes(self):
        assert common.text_needs_quotes("a@b") is True

    def test_ascii_no_quotes(self):
        assert common.text_needs_quotes("StartNode") is False


class TestLineFromOffset:
    """行号计算测试。"""

    def test_start_of_file(self):
        assert common.line_from_offset("hello", 0) == 1

    def test_after_newlines(self):
        text = "line1\nline2\nline3\n"
        assert common.line_from_offset(text, text.index("line2")) == 2
        assert common.line_from_offset(text, text.index("line3")) == 3


class TestStripInlineComment:
    """注释剥离测试。"""

    def test_comment_line_returns_empty(self):
        assert common.strip_inline_comment("%% this is a comment") == ""

    def test_inline_comment_stripped(self):
        assert common.strip_inline_comment("A --> B %% comment") == "A --> B "

    def test_no_comment_unchanged(self):
        assert common.strip_inline_comment("A --> B") == "A --> B"


class TestCheckEmptyLines:
    """空行检查测试。"""

    def test_no_empty_lines(self):
        issues = common.check_empty_lines("A\nB\nC", 1)
        assert issues == []

    def test_double_newline_error(self):
        issues = common.check_empty_lines("A\n\nB", 1)
        assert len(issues) == 1
        assert issues[0][1] == "error"
        assert "空行" in issues[0][2]


class TestFixBackslashN:
    """\n 修复测试。"""

    def test_replaces_backslash_n(self):
        text = "A[Hello\\nWorld]"
        fixed = common.fix_backslash_n(text)
        assert fixed == "A[Hello<br/>World]"

    def test_preserves_comments(self):
        text = "A --> B %% note with \\n"
        fixed = common.fix_backslash_n(text)
        assert "%% note with \\n" in fixed

    def test_comment_lines_unchanged(self):
        text = "%% this is a comment with \\n"
        fixed = common.fix_backslash_n(text)
        assert fixed == text


class TestStripMindmapShape:
    """思维导图形状剥离测试。"""

    def test_round_rectangle(self):
        assert common.strip_mindmap_shape("((Root))") == "Root"

    def test_square(self):
        assert common.strip_mindmap_shape("[Node]") == "Node"

    def test_plain_text(self):
        assert common.strip_mindmap_shape("plain") == "plain"

    def test_html_comment_returns_empty(self):
        assert common.strip_mindmap_shape("<!-- comment -->") == ""
```

- [ ] **Step 5: 运行测试验证 common.py 正确**

Run: `python -m pytest .agents/scripts/tests/test_mermaid_common.py -v`
Expected: 所有测试 PASS

- [ ] **Step 6: 提交**

```bash
git add .agents/scripts/lib/mermaid/__init__.py .agents/scripts/lib/mermaid/common.py .agents/scripts/tests/test_mermaid_common.py
git commit -m "refactor(mermaid): create common utility module"
```

---

### Task 2: 创建检查器抽象基类和注册表

**Files:**
- Create: `.agents/scripts/lib/mermaid/checkers/__init__.py`
- Create: `.agents/scripts/lib/mermaid/checkers/base.py`
- Create: `.agents/scripts/lib/mermaid/checkers/security.py`
- Create: `.agents/scripts/lib/mermaid/registry.py`
- Test: `.agents/scripts/tests/test_mermaid_checkers.py`

- [ ] **Step 1: 编写 checkers/base.py 抽象基类**

创建 `.agents/scripts/lib/mermaid/checkers/base.py`：

```python
"""Mermaid 检查器抽象基类。

定义所有图表类型检查器的通用接口和共享逻辑。
"""

from abc import ABC, abstractmethod
from typing import List, Tuple

from ..common import (
    check_empty_lines,
    check_backslash_n,
)


class BaseDiagramChecker(ABC):
    """Mermaid 图表检查器抽象基类。

    使用模板方法模式：check() 方法定义通用检查流程，
    子类实现 _check_specific_rules() 提供图表特定的检查逻辑。
    """

    @abstractmethod
    def get_diagram_type(self) -> str:
        """返回图表类型标识（如 'flowchart', 'stateDiagram'）。"""
        pass

    def check(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        """执行完整的检查流程。

        按顺序执行：通用空行检查 → 通用换行符检查 → 图表特定检查。

        Args:
            block_text: Mermaid 代码块文本（不含 ```mermaid 标记）。
            start_line: 代码块在原文件中的起始行号。

        Returns:
            问题列表，每个问题为 (行号, 级别, 消息) 元组。
        """
        issues = []
        issues.extend(check_empty_lines(block_text, start_line))
        issues.extend(self._check_specific_rules(block_text, start_line))
        issues.extend(check_backslash_n(block_text, start_line))
        return issues

    @abstractmethod
    def _check_specific_rules(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        """执行图表特定的检查规则，子类必须实现。

        Args:
            block_text: Mermaid 代码块文本。
            start_line: 代码块在原文件中的起始行号。

        Returns:
            问题列表。
        """
        pass
```

- [ ] **Step 2: 编写 checkers/security.py 安全检查器**

创建 `.agents/scripts/lib/mermaid/checkers/security.py`：

```python
"""Mermaid 安全检查器。

检测所有图表类型通用的安全问题：
- click 事件绑定（JavaScript 回调注入风险）
- 危险 HTML 标签（script/img/iframe/svg/object/embed）
- HTML 事件处理器属性（on*）
- javascript: 协议 URL
- end 作为节点 ID（与 Mermaid 保留字冲突）
"""

import re
from typing import List, Tuple

from ..common import strip_inline_comment


class SecurityChecker:
    """Mermaid 安全检查器，适用于所有图表类型。"""

    def __init__(self):
        self._dangerous_tags = re.compile(r'<\s*(script|img|iframe|svg|object|embed)\b', re.IGNORECASE)
        self._event_handler = re.compile(r'\son\w+\s*=', re.IGNORECASE)
        self._click_pat = re.compile(r'^\s*click\s+\S+', re.IGNORECASE)
        self._js_url_pat = re.compile(r'javascript\s*:', re.IGNORECASE)
        self._end_as_node = re.compile(r'(^|[^a-zA-Z0-9_])end\s*[\(\[\{<]', re.IGNORECASE)

    def check(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        """执行安全检查。

        Args:
            block_text: Mermaid 代码块文本。
            start_line: 代码块起始行号。

        Returns:
            安全问题列表。
        """
        issues = []
        for i, line in enumerate(block_text.split("\n")):
            code_part = strip_inline_comment(line)
            if not code_part.strip():
                continue
            lb = start_line + i

            if self._click_pat.match(code_part):
                issues.append((lb, "error",
                              "禁止使用 click 事件绑定，存在 JavaScript 回调注入风险"))

            tag_m = self._dangerous_tags.search(code_part)
            if tag_m:
                issues.append((lb, "error",
                              f"禁止使用危险 HTML 标签 <{tag_m.group(1)}>，存在安全风险"))

            if self._event_handler.search(code_part):
                issues.append((lb, "error",
                              "禁止使用 HTML 事件处理器属性（on*），存在 XSS 风险"))

            if self._js_url_pat.search(code_part):
                issues.append((lb, "error",
                              '禁止使用 javascript: 协议 URL，存在 XSS 风险'))

            if self._end_as_node.search(code_part):
                issues.append((lb, "error",
                              '禁止使用 "end" 作为节点 ID，与 Mermaid 保留字冲突'))

        return issues
```

- [ ] **Step 3: 编写 registry.py 策略注册表**

创建 `.agents/scripts/lib/mermaid/registry.py`：

```python
"""Mermaid 检查器/修复器策略注册表。

提供检查器和修复器的注册、查找和管理功能。
"""

from typing import Dict, Optional, Type, Callable

from .checkers.base import BaseDiagramChecker


class CheckerRegistry:
    """检查器策略注册表。"""

    def __init__(self):
        self._checkers: Dict[str, BaseDiagramChecker] = {}
        self._security_checker: Optional[object] = None

    def register(self, checker: BaseDiagramChecker) -> None:
        """注册一个图表检查器。

        Args:
            checker: 检查器实例，必须继承自 BaseDiagramChecker。
        """
        self._checkers[checker.get_diagram_type()] = checker

    def get_checker(self, diagram_type: str) -> Optional[BaseDiagramChecker]:
        """根据图表类型获取检查器。

        Args:
            diagram_type: 图表类型标识。

        Returns:
            检查器实例，未找到时返回 None。
        """
        return self._checkers.get(diagram_type)

    def set_security_checker(self, checker: object) -> None:
        """设置安全检查器。"""
        self._security_checker = checker

    def get_security_checker(self) -> Optional[object]:
        """获取安全检查器。"""
        return self._security_checker

    def get_all_types(self) -> list[str]:
        """获取所有已注册的图表类型。"""
        return list(self._checkers.keys())


class FixerRegistry:
    """修复器策略注册表。"""

    def __init__(self):
        self._fixers: Dict[str, Callable] = {}

    def register(self, diagram_type: str, fixer: Callable) -> None:
        """注册一个图表修复器函数。

        Args:
            diagram_type: 图表类型标识。
            fixer: 修复器函数，接收 block_text，返回 (fixed_text, fixes_list)。
        """
        self._fixers[diagram_type] = fixer

    def get_fixer(self, diagram_type: str) -> Optional[Callable]:
        """根据图表类型获取修复器。

        Args:
            diagram_type: 图表类型标识。

        Returns:
            修复器函数，未找到时返回 None。
        """
        return self._fixers.get(diagram_type)

    def get_all_types(self) -> list[str]:
        """获取所有已注册的图表类型。"""
        return list(self._fixers.keys())
```

- [ ] **Step 4: 创建 checkers/__init__.py**

创建 `.agents/scripts/lib/mermaid/checkers/__init__.py`：

```python
"""Mermaid 检查器模块。"""

from .base import BaseDiagramChecker
from .security import SecurityChecker

__all__ = ["BaseDiagramChecker", "SecurityChecker"]
```

- [ ] **Step 5: 编写检查器基类和安全检查器的单元测试**

创建 `.agents/scripts/tests/test_mermaid_checkers.py`：

```python
"""mermaid.checkers 模块单元测试。"""

import pytest
from typing import List, Tuple

from lib.mermaid.checkers import BaseDiagramChecker, SecurityChecker


class TestBaseDiagramChecker:
    """检查器基类测试。"""

    def test_abstract_class_cannot_instantiate(self):
        with pytest.raises(TypeError):
            BaseDiagramChecker()

    def test_concrete_checker_works(self):
        class TestChecker(BaseDiagramChecker):
            def get_diagram_type(self) -> str:
                return "test"

            def _check_specific_rules(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
                return [(start_line + 1, "error", "test error")]

        checker = TestChecker()
        issues = checker.check("test line\nanother line", 1)
        assert len(issues) >= 1
        assert any("test error" in i[2] for i in issues)

    def test_empty_lines_checked_by_default(self):
        class EmptyLineChecker(BaseDiagramChecker):
            def get_diagram_type(self) -> str:
                return "test"

            def _check_specific_rules(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
                return []

        checker = EmptyLineChecker()
        issues = checker.check("A\n\nB", 1)
        assert any("空行" in i[2] for i in issues)


class TestSecurityChecker:
    """安全检查器测试。"""

    def setup_method(self):
        self.checker = SecurityChecker()

    def test_clean_block_no_issues(self):
        block = "graph TD\n    A --> B"
        issues = self.checker.check(block, 1)
        assert issues == []

    def test_detects_script_tag(self):
        block = "graph TD\n    A --> B\n    <script>alert(1)</script>"
        issues = self.checker.check(block, 1)
        assert any("script" in i[2] for i in issues)

    def test_detects_click_event(self):
        block = "graph TD\n    A --> B\n    click A callback"
        issues = self.checker.check(block, 1)
        assert any("click" in i[2] for i in issues)

    def test_detects_javascript_url(self):
        block = 'graph TD\n    A --> B\n    click A "javascript:alert(1)"'
        issues = self.checker.check(block, 1)
        assert any("javascript:" in i[2] for i in issues)

    def test_detects_on_event_handler(self):
        block = "graph TD\n    <img src=x onerror=alert(1)>"
        issues = self.checker.check(block, 1)
        assert any("on*" in i[2] or "事件处理器" in i[2] for i in issues)

    def test_detects_end_as_node(self):
        block = "graph TD\n    start --> end --> stop"
        issues = self.checker.check(block, 1)
        assert any('"end"' in i[2] for i in issues)

    def test_ignores_comments(self):
        block = "graph TD\n    A --> B\n    %% <script>commented</script>"
        issues = self.checker.check(block, 1)
        assert issues == []
```

- [ ] **Step 6: 运行测试验证检查器模块**

Run: `python -m pytest .agents/scripts/tests/test_mermaid_checkers.py -v`
Expected: 所有测试 PASS

- [ ] **Step 7: 提交**

```bash
git add .agents/scripts/lib/mermaid/checkers/__init__.py .agents/scripts/lib/mermaid/checkers/base.py .agents/scripts/lib/mermaid/checkers/security.py .agents/scripts/lib/mermaid/registry.py .agents/scripts/tests/test_mermaid_checkers.py
git commit -m "refactor(mermaid): create checker base class and security checker"
```

---

### Task 3: 创建具体图表检查器（流程图、状态图、序列图）

**Files:**
- Create: `.agents/scripts/lib/mermaid/checkers/flowchart.py`
- Create: `.agents/scripts/lib/mermaid/checkers/state_diagram.py`
- Create: `.agents/scripts/lib/mermaid/checkers/sequence_diagram.py`
- Modify: `.agents/scripts/lib/mermaid/checkers/__init__.py`
- Test: `.agents/scripts/tests/test_mermaid_diagram_checkers.py`

- [ ] **Step 1: 编写 flowchart.py 流程图检查器**

创建 `.agents/scripts/lib/mermaid/checkers/flowchart.py`：

```python
"""Mermaid 流程图（flowchart/graph）检查器。"""

import re
from typing import List, Tuple

from .base import BaseDiagramChecker
from ..common import (
    CHINESE_CHARS_RE,
    text_needs_quotes,
    check_list_trigger,
)


class FlowchartChecker(BaseDiagramChecker):
    """流程图检查器。"""

    def __init__(self):
        self._sub_pat = re.compile(r"^(\s*subgraph\s+)([^\s\[\"]+)(.*)$", re.MULTILINE)
        self._arrow_pat = re.compile(
            r"(-\.->|==>|-->|-\.-|===|---|<-->|<==>|<-\.->|<--|<==|<-\.-|==|--|-\.)\|([^|]*?)\|"
        )
        self._style_pat = re.compile(r"^\s*style\s+\w+\s+", re.MULTILINE)
        self._node_checks = [
            (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\(\(([^\)\"]+?)\)\)", re.MULTILINE), "圆形"),
            (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\(\[([^\]\"]+?)\]\)", re.MULTILINE), "体育场形"),
            (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\[\[([^\]\"]+?)\]\]", re.MULTILINE), "子程序"),
            (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)>\(([^\)\"]+?)\)", re.MULTILINE), "标签形状"),
            (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\[([^\]\"]+?)\]", re.MULTILINE), "矩形"),
            (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\{([^\}\"]+?)\}", re.MULTILINE), "菱形"),
            (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\(([^\)\"(<]+?)\)", re.MULTILINE), "圆角矩形"),
        ]

    def get_diagram_type(self) -> str:
        return "flowchart"

    def _check_specific_rules(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        issues = []
        issues.extend(self._check_subgraphs(block_text, start_line))
        issues.extend(self._check_nodes(block_text, start_line))
        issues.extend(self._check_arrows(block_text, start_line))
        issues.extend(self._check_style(block_text, start_line))
        return issues

    def _check_subgraphs(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        issues = []
        for m in self._sub_pat.finditer(block_text):
            sid = m.group(2).strip()
            rest = m.group(3).strip()
            lb = block_text[:m.start()].count("\n") + 1
            if CHINESE_CHARS_RE.search(sid) or "\uff1a" in sid or " " in sid:
                issues.append((start_line + lb - 1, "error",
                              f'subgraph 使用裸ID「{sid}」，应使用 subgraph EN_ID ["中文标题"] 格式'))
            if rest and not rest.startswith("["):
                if CHINESE_CHARS_RE.search(rest) or any(c in rest for c in "：（()"):
                    issues.append((start_line + lb - 1, "error",
                                  f'subgraph 标题「{rest[:20]}」缺少方括号，应使用 subgraph EN_ID ["标题"] 格式'))
        return issues

    def _check_nodes(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        issues = []
        for pat, shape_name in self._node_checks:
            for m in pat.finditer(block_text):
                ntxt = m.group(3)
                lb = block_text[:m.start()].count("\n") + 1
                if text_needs_quotes(ntxt):
                    issues.append((start_line + lb - 1, "error",
                                  f'{shape_name}节点含中文/特殊字符/空格但未加双引号：{ntxt[:20]}'))
                w = check_list_trigger(ntxt, lb - 1, start_line, f'{shape_name}节点')
                if w:
                    issues.append(w)
        return issues

    def _check_arrows(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        issues = []
        for m in self._arrow_pat.finditer(block_text):
            label = m.group(2)
            lb = block_text[:m.start()].count("\n") + 1
            if not (label.startswith('"') and label.endswith('"')):
                if text_needs_quotes(label) or label in ("是", "否"):
                    issues.append((start_line + lb - 1, "error",
                                  f'边标签「{label[:20]}」含中文/特殊字符但未加双引号'))
            w = check_list_trigger(label, lb - 1, start_line, '边标签')
            if w:
                issues.append(w)
        return issues

    def _check_style(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        issues = []
        for m in self._style_pat.finditer(block_text):
            lb = block_text[:m.start()].count("\n") + 1
            line = block_text[m.start():].split("\n")[0]
            if CHINESE_CHARS_RE.search(line):
                issues.append((start_line + lb - 1, "warning",
                              'style 语句含中文字符，可能导致解析错误'))
        return issues
```

（由于篇幅限制，状态图、序列图、类图、ER图、思维导图、通用检查器的代码将按相同模式迁移，此处省略部分重复代码，完整实现将在执行时完成）

- [ ] **Step 2-7: 按相同模式创建其他图表检查器、修复器、扫描器、运行器和处理器**

（遵循相同的 TDD 模式，为每个模块编写测试后实现）

- [ ] **Step 8: 更新 mermaid.py 为兼容层**

最后更新 `.agents/scripts/lib/checks/mermaid.py`，导入新模块并暴露原有函数接口，保持完全向后兼容。

- [ ] **Step 9: 运行现有测试验证兼容性**

Run: `python -m pytest .agents/scripts/tests/test_checks_mermaid.py -v`
Expected: 所有现有测试 PASS，无需修改

- [ ] **Step 10: 提交最终重构**

```bash
git add .agents/scripts/lib/mermaid/ .agents/scripts/lib/checks/mermaid.py .agents/scripts/tests/
git commit -m "refactor(mermaid): complete modular refactoring with backward compatibility"
```

---

## 回归验证清单

重构完成后，必须验证以下场景：

1. **所有现有测试通过** - `python -m pytest .agents/scripts/tests/test_checks_mermaid.py -v`
2. **命令行工具正常工作** - `python .agents/scripts/check-mermaid.py --help`
3. **实际文件检查** - 在包含各种 Mermaid 图表的文档上运行检查，结果与重构前一致
4. **自动修复功能** - `--fix` 和 `--dry-run` 参数正常工作
5. **CI 集成** - 退出码和输出格式保持兼容

## 风险缓解

- **渐进式重构**：不一次性删除旧代码，先建立新模块，最后通过兼容层切换
- **测试先行**：每个新模块都有单元测试，最后运行现有集成测试验证
- **向后兼容**：mermaid.py 保持原有函数签名和行为，调用方无需修改
- **小步提交**：每个 Task 完成后提交，便于回滚
