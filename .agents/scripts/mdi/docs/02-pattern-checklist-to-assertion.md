---
id: "mdi-pattern-checklist-to-assertion"
title: "模式二：检查清单→断言转换"
source: "PATTERN-APPLICATION.md#模式二检查清单断言转换"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/mdi/docs/02-pattern-checklist-to-assertion.toml"
---

# 模式二：检查清单→断言转换

> **模式文档**：[checklist-to-assertion-conversion.md](../../../../docs/retrospective/patterns/code-patterns/checklist-to-assertion-conversion.md)

## MDI中的实现位置

| 文件 | 函数/类 | 职责 |
|------|---------|------|
| [checklist_converter.py](../checklist_converter.py) | `convert_checklist_to_steps()` (L64-L93) | 主转换入口：分类+排序+生成 |
| [checklist_converter.py](../checklist_converter.py) | `_classify_item()` (L36-L61) | 四级关键词分类器 |
| [checklist_converter.py](../checklist_converter.py) | `_generate_assertion()` (L96-L160) | 专项正则断言代码生成 |
| [checklist_converter.py](../checklist_converter.py) | `CheckItem`/`ChecklistStep` 数据类 | 结构化检查项/测试步骤 |
| [generators/pytest_gen/](../generators/pytest_gen/) | pytest测试生成器 | 调用checklist_converter生成断言 |

## 四级分类关键词（MDI中文版）

```python
_PRE_KEYWORDS = ("前置", "准备", "before", "setup", "given", "前提", "登录", "认证")
_ASSERT_KEYWORDS = ("验证", "确认", "断言", "assert", "expect", "返回", "状态码", "包含", "字段")
_POST_KEYWORDS = ("后置", "清理", "teardown", "after", "cleanup")
# 其他 → note（注释）
```

## 专项正则提取（真实代码生成）

| 正则 | 匹配示例 | 生成Python代码 |
|------|---------|---------------|
| `(?:状态码\|status\s*code)[^\d]*?(\d{3})` | "验证返回状态码200" | `assert response.status_code == 200` |
| `(?:包含\|存在\|has\|contain)[^，。；]*?(?:字段\|field)[^，。；]*?([a-zA-Z_]\w*)` | "响应包含id字段" | `assert "id" in data` |
| `([a-zA-Z_]\w*)\s*(?:字段)?\s*(?:等于\|为\|是\|==?)\s*([^\`'"，。；]+)` | "status为success" | `assert data["status"] == "success"` |

## 实际应用示例

user-api.md中的checklist：

```markdown
## Checklist

- [x] Login endpoint returns 200 with valid credentials
- [x] Login endpoint returns 401 with invalid credentials
- [x] Register endpoint creates user with valid data
- [ ] Password reset flow
- [ ] Email verification after registration
```

转换后的pytest测试片段：

```python
# 前置步骤
# TODO: 实现前置步骤: prepare valid test user credentials

# 断言步骤
# [x] Login endpoint returns 200 with valid credentials
assert response.status_code == 200
# [x] Login endpoint returns 401 with invalid credentials
assert response.status_code == 401
# [x] Register endpoint creates user with valid data
# TODO: 实现断言逻辑: Register endpoint creates user with valid data

# 后置步骤
# TODO: 实现后置清理步骤

# 注释
# [ ] Password reset flow
# [ ] Email verification after registration
```

## 扩展断言提取规则

在`_generate_assertion()`中添加新的专项正则：

```python
# 新增：Content-Type断言
_content_type_re = re.compile(r"content-type[为是=:]\s*([\w/\-]+)", re.I)
m = _content_type_re.search(text)
if m:
    ct = _convert_python_value(m.group(1).strip())
    return f'assert response.headers.get("content-type") == "{ct}"'
```

## 常见陷阱

❌ **错误**：分类顺序错误——先匹配assert再匹配pre
```python
# 错误："前置条件应验证状态码"会被误分类为assert
for kw in _ASSERT_KEYWORDS:  # 错误顺序！
    if kw in text:
        return "assert"
```

✅ **正确**：按pre→post→assert顺序匹配，避免assert范围过宽误分类

❌ **错误**：所有检查项都生成assert，不做分类
- "前置登录"变成 `assert "登录" in response`（无意义）
- "清理测试数据"变成 `assert "清理" in response`（荒谬）

✅ **正确**：前置/后置生成TODO注释，只有明确断言关键词才生成assert代码

❌ **错误**：不做值类型转换
```python
# 错误："is_active为true" → assert data["is_active"] == "true"（字符串！）
return f'assert data["{field}"] == "{value}"'
```

✅ **正确**：通过`_convert_python_value()`转换为正确的Python字面量（True/False/None/int/float）
