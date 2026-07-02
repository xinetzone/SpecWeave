---
id: "mdi-pattern-profile-auto-detection"
title: "模式三：Profile自动检测"
source: "PATTERN-APPLICATION.md#模式三profile自动检测"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/mdi/docs/03-pattern-profile-auto-detection.toml"
---

# 模式三：Profile自动检测

> **模式文档**：[profile-auto-detection.md](../../../../docs/retrospective/patterns/code-patterns/profile-auto-detection.md)

## MDI中的实现位置

| 文件 | 函数 | 职责 |
|------|------|------|
| [profiles/__init__.py](../profiles/__init__.py) | `detect_profile_type()` (L53-L103) | 五级优先级自动检测 |
| [profiles/__init__.py](../profiles/__init__.py) | `get_profile()` (L33-L50) | 按类型获取Profile实例 |
| [profiles/__init__.py](../profiles/__init__.py) | `_PROFILE_MAP` (L26-L30) | Profile类型注册表 |

## 五级检测优先级（MDI实现）

| 优先级 | 检测逻辑 | 置信度 | MDI代码位置 |
|--------|---------|--------|------------|
| P1 | frontmatter `type`字段显式声明 | 极高 | L74-L78 |
| P2 | frontmatter特征字段：`baseUrl`→webapi, `argument-hint/user-invocable/paths`→skill | 高 | L80-L86 |
| P3 | 文件名/路径：`SKILL.md`→skill, 含`cli/command`→clitool | 中 | L88-L95 |
| P4 | 内容正则：`` `(GET\|POST\|PUT\|PATCH\|DELETE)\s+/ `` → webapi | 低 | L97-L101 |
| P5 | 默认值 → skill | - | L103 |

## 实际检测案例

| 文件 | 命中优先级 | 检测结果 | 命中原因 |
|------|-----------|---------|---------|
| user-api.md | P1→webapi | ✅ webapi | frontmatter有`type: webapi` |
| todo-api-v1.md | P4→webapi | ✅ webapi | 内容有`GET /todos` |
| file-cli.md | P1→clitool/P3→clitool | ✅ clitool | frontmatter有`type: clitool`且文件名含cli |
| SKILL.md（假设） | P3→skill | ✅ skill | 文件名为SKILL.md大写 |

## 新增Profile类型的扩展点

1. **在`profiles/`下创建新Profile类**：
```python
# profiles/graphql_profile.py
from .base import BaseProfile

class GraphQLProfile(BaseProfile):
    name = "graphql"
    # 实现section_patterns、validation_rules等
```

2. **在`_PROFILE_MAP`中注册**：
```python
from .graphql_profile import GraphQLProfile

_PROFILE_MAP: dict[str, type[BaseProfile]] = {
    "skill": SkillProfile,
    "webapi": WebApiProfile,
    "clitool": CliToolProfile,
    "graphql": GraphQLProfile,  # 新增
}
```

3. **在`detect_profile_type()`中添加检测规则**：
```python
# P2: frontmatter特征字段
graphql_indicators = {"schema", "query-type", "mutation-type"}
if graphql_indicators & fm_keys_lower:
    return "graphql"

# P3: 文件名特征
if "graphql" in name_lower or "gql" in name_lower:
    return "graphql"

# P4: 内容特征
if "type Query {" in full_text_lower or "type Mutation {" in full_text_lower:
    return "graphql"
```

## 常见陷阱

❌ **错误**：检测优先级顺序错误——P4内容特征在P1显式声明之前
```python
# 错误：内容里偶然出现GET单词就覆盖用户显式声明
if re.search(r"GET\s+/", full_text):  # 放在最前面！
    return "webapi"
fm_type = doc.frontmatter.get("type", "")  # 用户声明被忽略
```

✅ **正确**：P1（显式声明）必须在最前面，用户意图高于一切自动推断

❌ **错误**：所有信号同等权重投票
```python
# 错误：简单计数——1个弱信号推翻3个强信号
votes = {"webapi": 0, "skill": 0, "clitool": 0}
if "baseUrl" in fm: votes["webapi"] += 1
if "GET" in content: votes["webapi"] += 1  # 偶然出现也投票
if "cli" in filename: votes["clitool"] += 1
# 多数决，但弱信号可能决定结果
```

✅ **正确**：严格优先级链，高优先级命中立即返回，不继续检查低优先级

❌ **错误**：没有默认值兜底，所有信号都不匹配时直接报错
- 用户写了一个全新格式的文档
- 没有任何已知特征
- 工具直接崩溃退出

✅ **正确**：返回最通用的默认类型（MDI默认skill），保证工具能继续运行，可输出警告提示用户显式指定

❌ **错误**：检测逻辑散落在parser/validator/generator各处
- parser里写了一份类型判断
- validator里又写了一份
- generator里再写一份
- 新增类型时改不全，行为不一致

✅ **正确**：`detect_profile_type()`是唯一检测入口，所有组件统一调用
