---
id: "parameterization-over-duplication"
source: "../../../reports/task-reports/retrospective-frontmatter-refactor-20260710/insight-extraction.md"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/tools-automation/parameterization-over-duplication.toml"
---
> **提炼自**：[insight-extraction.md](../../../reports/task-reports/retrospective-frontmatter-refactor-20260710/insight-extraction.md) —— frontmatter解析逻辑重构复盘（洞察2）

# 参数化优于复制（Parameterization Over Duplication）

## 模式类型

方法论模式（工具自动化/函数设计）

## 成熟度

L1 首次提炼（frontmatter重构验证：通过pattern参数支持TOML/YAML两种格式，避免新的重复）

## 第一性原理

**当公共逻辑中有差异点时，通过参数抽象差异，而不是为每个差异创建相似函数——参数化保持单一真相源，复制产生多个真相源。**

提取公共函数时遇到的核心矛盾：多个调用方的逻辑"几乎一样但有点不同"。选择1：复制整个函数然后改几行——产生新的重复；选择2：把差异点作为参数传入——保持单一真相源。

## 适用场景

- 提取公共函数时发现调用方之间有差异
- 多个函数逻辑相似只有少数值不同
- 避免"为每种情况创建一个函数"的函数爆炸
- 设计可复用工具函数时

## 核心思想

### 参数化四原则

从frontmatter重构中提炼的 `_extract_frontmatter_text()` 函数是典型案例：
- 公共逻辑：读取文件→异常处理→正则匹配→返回group(1)
- 差异点：用哪个正则模式（TOML的`+++`还是YAML的`---`）
- 参数化方案：`pattern: re.Pattern[str]` 参数传入

**原则1：优先参数化，而非复制变体**

❌ 错误：创建两个几乎一样的函数
```python
def _extract_toml_text(file_path):
    # 10+行：读文件+异常处理+TOML正则
def _extract_yaml_text(file_path):
    # 10+行：读文件+异常处理+YAML正则（和上面90%重复）
```

✅ 正确：参数化差异点
```python
def _extract_frontmatter_text(file_path, pattern: re.Pattern):
    # 15行：读文件+异常处理+用传入的pattern匹配
# 调用方
parse_toml_frontmatter → _extract_frontmatter_text(path, _FRONTMATTER_RE)
parse_yaml_frontmatter → _extract_frontmatter_text(path, _YAML_FRONTMATTER_RE)
```

**原则2：参数要抽象，不要具体**

- ❌ 差的参数：`is_yaml: bool` 布尔标志
  - 问题：函数内部需要if/else分支，未来加第三种格式又要改
- ✅ 好的参数：`pattern: re.Pattern[str]` 抽象策略
  - 优势：函数不需要知道是什么格式，只负责匹配，符合开闭原则

| 参数类型 | 例子 | 评价 |
|---------|------|------|
| 布尔标志 | `is_yaml: bool` | ❌ 具体，扩展性差 |
| 枚举/常量 | `format: Literal["toml", "yaml"]` | ⚠️ 稍好但仍需if/else |
| 策略/函数/模式 | `pattern: re.Pattern` `transform: Callable` | ✅ 抽象，无需修改公共函数 |

**原则3：单一职责——参数化不引入复杂分支**

公共函数应该只做一件事。参数化是"让同一件事可以处理不同的输入"，不是"让一个函数做很多事"。

❌ 反模式（函数做太多事）：
```python
def process_file(path, is_yaml, validate_schema, auto_fix, write_back):
    # 大量if/else分支，职责不清
```

✅ 正例（单一职责）：
```python
def _extract_frontmatter_text(path, pattern):
    # 只做一件事：用给定的pattern提取frontmatter文本
```

**原则4：文档清晰说明参数预期**

参数化后，参数的用途必须写清楚——因为抽象参数比具体参数更需要文档说明。

```python
def _extract_frontmatter_text(
    file_path: str | Path,
    pattern: re.Pattern[str],  # 文档说清楚：用于匹配frontmatter的正则表达式
) -> str | None:
    """...
    Args:
        pattern: 用于匹配 frontmatter 的正则表达式（如 _YAML_FRONTMATTER_RE）。
    ...
```

## 反模式与误区

### 误区1："两个函数各自独立，更清晰"
错误。两个90%相同的函数不是"清晰"，是"重复"——未来修改异常处理逻辑时你必须改两处，漏一处就是bug。

### 误区2："加个bool参数最简单"
错误。bool参数是"代码坏味道"——它意味着函数内部有if/else做两件不同的事。如果差异是"策略"（不同的正则/不同的转换函数），传入策略对象比传入bool标志更好。

### 误区3："参数化会让函数太复杂"
不会。如果参数化后函数需要加很多if/else，说明你不是在"参数化差异"，而是在"合并多个函数"——这时候应该重新考虑抽象是否正确。正确的参数化应该是：公共逻辑完全不需要知道参数是什么，只是使用它。

## 正例：frontmatter重构验证

**重构前**：两个函数+一个统一入口，共3处重复的文件读取和正则匹配逻辑。

**重构后**：
- 1个参数化公共函数 `_extract_frontmatter_text(file_path, pattern)`
- TOML/YAML解析简化为单行return调用
- `parse_frontmatter_unified`也使用公共函数
- 新增格式支持（如JSON frontmatter）时，只需定义新正则，无需修改公共函数

结果：159个测试全部通过，消除约30行重复代码。

## 与现有模式的关系

- `encapsulation-contract-essence.md`：参数化公共函数是内部实现细节，可以自由重构
- `duplication-interest-model.md`：参数化是消除重复、避免利息成本的核心手段
- `first-citizen-abstraction.md`：把策略（正则/转换函数）作为一等公民参数传入
