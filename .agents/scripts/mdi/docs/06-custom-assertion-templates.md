---
id: "mdi-custom-assertion-templates"
title: "扩展指南：自定义测试断言模板"
source: "PATTERN-APPLICATION.md#扩展指南自定义测试断言模板"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/mdi/docs/06-custom-assertion-templates.toml"
---

# 扩展指南：自定义测试断言模板

## 添加新的专项断言正则

在 [checklist_converter.py](../checklist_converter.py) `_generate_assertion()`函数中添加：

```python
# 示例：响应时间断言
_RESPONSE_TIME_RE = re.compile(
    r"响应时间[<少于]\s*(\d+)\s*ms", re.I
)
m = _RESPONSE_TIME_RE.search(text)
if m:
    ms = int(m.group(1))
    return f"assert response.elapsed.total_seconds() < {ms / 1000}"

# 示例：响应头存在
_HEADER_EXISTS_RE = re.compile(
    r"响应[包含]?(?:头|header)\s*[`\"']?([\w-]+)[`\"']?", re.I
)
m = _HEADER_EXISTS_RE.search(text)
if m:
    header = m.group(1)
    return f'assert "{header}" in response.headers'
```

## 为不同语言生成器扩展

pytest_gen.py当前调用`convert_checklist_to_steps(text)`后直接用`step.code`。如果要为Jest/TypeScript等其他语言生成断言：

1. 在`checklist_converter.py`中添加`language`参数
2. 在`_generate_assertion()`中根据language选择代码模板
3. 或者在各generator中对ChecklistStep做二次转换（推荐：保持核心逻辑语言无关）
