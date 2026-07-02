---
id: "mdi-extending-profiles"
title: "扩展指南：新增Profile类型"
source: "PATTERN-APPLICATION.md#扩展指南新增profile类型"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/mdi/docs/04-extending-profiles.toml"
---

# 扩展指南：新增Profile类型

本章节提供新增Profile类型的完整checklist。假设要新增`graphql`Profile支持GraphQL Schema文档。

## Step 1：创建Profile类

```
profiles/graphql_profile.py
```

继承`BaseProfile`，实现：
- `name`类属性
- `section_patterns`：章节识别正则
- `validation_rules`：验证规则列表

参考：[webapi_profile.py](../profiles/webapi_profile.py)、[clitool_profile.py](../profiles/clitool_profile.py)

## Step 2：注册到Profile Map

编辑 [profiles/__init__.py](../profiles/__init__.py)：

1. 添加import
2. 在`_PROFILE_MAP`添加条目
3. 在`detect_profile_type()`中添加检测规则（按P1-P5优先级）

## Step 3：创建Directive解析（如需要）

如果GraphQL需要新的directive类型（如`{query}`、`{mutation}`）：
- 在parser.py中添加directive_name识别
- 创建对应的解析函数处理特定选项
- **不要修改通用`_parse_directive_content`状态机**

## Step 4：创建Generator（如需要）

如果需要生成GraphQL特定的输出格式：
- 在`generators/`下创建新生成器
- 继承`BaseGenerator`
- 在`generator.py`中注册

## Step 5：创建测试示例

在`examples/`下添加示例文档：
- `examples/graphql-schema.md`
- 包含directive和checklist
- 运行 `python -m mdi validate examples/graphql-schema.md` 验证

## Step 6：扩展Checklist分类（如需要）

如果GraphQL测试有特殊的前置/断言关键词，在 [checklist_converter.py](../checklist_converter.py) 中添加：
- 更新`_PRE_KEYWORDS`/`_ASSERT_KEYWORDS`
- 在`_generate_assertion()`中添加GraphQL特定断言正则
