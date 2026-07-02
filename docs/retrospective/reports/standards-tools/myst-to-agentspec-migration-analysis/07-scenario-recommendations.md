---
id: "myst-migration-07-scenario-recommendations"
title: "Agent开发场景化建议"
source: "report.md#7-Agent开发场景化建议"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/standards-tools/myst-to-agentspec-migration-analysis/07-scenario-recommendations.toml"
---

## 7. Agent开发场景化建议

### 7.1 场景一：接口定义（API Endpoint / Tool Interface）

**场景描述：** 定义Agent可调用的工具接口或API端点，包括方法名、路径、参数、响应、错误处理等。这是Agent Spec最核心的场景。

**推荐使用：**
- ````{interface}```` 反引号围栏（代码类，降级显示为代码块易读）
- `:key: value` 选项格式指定方法、路径、鉴权要求
- 嵌套使用````{param}````和````{response}````指令
- `{type}` Role标记参数类型
- `{param-ref}` Role引用其他参数

**可选使用：**
- `::{warning}::` 标记接口的使用限制或副作用
- `::{note}::` 添加设计决策说明
- `{deprecated}` 标记即将下线的接口

**不推荐使用：**
- 冒号围栏（接口定义是代码性质，反引号更合适）
- YAML选项块（参数定义用独立的`{param}`指令更清晰）
- `{card}`/`{dropdown}`等UI组件（接口定义应保持简洁结构化）

**正例：**

````markdown
```{interface} create_user
:method: POST
:path: /api/v1/users
:auth: required

创建新用户账号。

当用户提交注册表单时调用此接口，会发送验证邮件。

```{param} email
:type: string
:required: true
:format: email

用户邮箱地址，必须未被注册过
```

```{param} password
:type: string
:required: true
:min-length: 8

用户密码，需包含大小写字母和数字
```

```{response} 200
:type: object
成功响应

```{param} user_id
:type: string
新创建的用户ID
```

```{response} 409
:type: Error
邮箱已被注册
```
```
````

**反例1（纯表格形式，语义不明确）：**

```markdown
## 创建用户

- 方法：POST
- 路径：/api/v1/users
- 鉴权：需要

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| email | string | 是 | 邮箱 |
| password | string | 是 | 密码 |

| 状态码 | 说明 |
|---|---|
| 200 | 成功 |
| 409 | 冲突 |
```

**反例2（过度使用冒号围栏和YAML）：**

```markdown
:::{interface} create_user
---
method: POST
path: /api/v1/users
auth:
  required: true
  type: bearer
---
这里过度使用了YAML和冒号围栏...
:::
```

### 7.2 场景二：参数与字段说明

**场景描述：** 详细说明接口参数、配置字段、数据结构字段的名称、类型、约束、示例值、默认值等。

**推荐使用：**
- ````{param}```` 反引号围栏
- `:type:`/`:required:`/`:default:`/`:example:`/`:constraints:` 等标准选项
- `{type}` Role标注嵌套类型
- `{literal}` Role标记字段名

**可选使用：**
- `::{tip}::` 提供参数填写建议
- `:{caution}::` 说明边界值或特殊处理

**不推荐使用：**
- 继续使用表格（新文档推荐Directive，老文档保持兼容即可）
- YAML块格式（单个参数用`:key: value`更清晰）
- 冒号围栏（参数定义倾向代码性质）

**正例：**

````markdown
```{param} timeout
:type: integer
:required: false
:default: 30
:unit: seconds
:range: 1-300

请求超时时间。

设置过短可能导致大文件上传失败，设置过长可能在服务不可达时等待过久。
建议生产环境使用默认值。
```
````

**反例（表格形式，但新文档推荐用Directive）：**

```markdown
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| timeout | integer | 否 | 30 | 超时时间（秒），范围1-300 |
```

### 7.3 场景三：提示框与注意事项

**场景描述：** 在文档中插入提示、警告、最佳实践、注意事项等内容，引导读者关注重要信息。

**推荐使用：**
- `:::{note}:::` 冒号围栏（Markdown内容类，降级效果较好）
- `:::{warning}:::` 标记易错点和潜在问题
- `:::{tip}:::` 分享最佳实践和小技巧
- `:::{important}:::` 标记必须遵守的关键规则
- `:::{caution}:::` 提醒谨慎操作的场景
- `:::{seealso}:::` 引导到相关文档

**可选使用：**
- 内容中使用`{strong}` Role强调关键词
- 简短提示也可用反引号围栏（保持一致性选择即可）

**不推荐使用：**
- 用粗体+大写手工写"注意："、"警告："（应该用指令）
- 嵌套超过2层提示框（影响可读性）
- 每个段落都加提示框（滥用会导致视觉噪音）

**正例：**

```markdown
:::{warning}
生产环境务必开启鉴权！

未开启鉴权时，任何人都可以调用{literal}`delete_user`等高危接口，造成数据泄露或丢失。
参见{ref}`auth-configuration`章节了解如何配置。
:::

:::{tip}
建议在客户端对{param-ref}`email`字段做前置格式校验，可减少约30%的无效请求。
:::

:::{seealso}
- {doc}`authentication.md` - 鉴权机制详解
- {doc}`error-handling.md` - 错误码列表
:::
```

**反例（手工标记，无统一语义）：**

```markdown
**注意！！！** 一定要开鉴权啊！！！不开会出事！！！

> 小提示：可以在客户端先检查邮箱格式哦~

参考其他文档：鉴权、错误处理...
```

### 7.4 场景四：技能文档（SKILL.md）元数据与配置

**场景描述：** SKILL.md文档描述Agent技能，包含元数据、配置项、输入输出、使用示例等。当前SKILL.md 100%有frontmatter，表格密度3.79个/文档，代码块密度4.43个/文档，是结构化程度最高的文档类型。

**推荐使用：**
- TOML/YYYY frontmatter（保持现状，用于标题、描述、标签、版本等元数据）
- ````{config}```` 自定义指令描述配置项
- ````{input}````/`{output}```描述输入输出（可复用param/response模式）
- `::{example}::` 包含使用示例代码
- `{type}`/`{literal}`等Roles增强行内语义

**可选使用：**
- `::{note}:::`/`:{warning}::`标记技能使用限制
- `::{since}::`/`:{deprecated}::标记版本信息
- `{card}`分组展示相关信息（渲染层支持时）

**不推荐使用：**
- 把元数据放在frontmatter以外（保持frontmatter作为文档入口元数据的定位）
- 过度使用UI组件（SKILL.md应优先保证机器可读和命令行可读性）
- `{include}`包含其他文件（增加解析复杂度，初期不建议）

**正例：**

```markdown
+++
title = "代码审查技能"
description = "自动审查代码质量与安全问题"
version = "1.2.0"
tags = ["code-review", "security", "quality"]
+++

# 代码审查技能

自动分析代码变更，识别质量问题、安全漏洞、风格问题。

::{note}
此技能需要代码仓库读取权限，参见{ref}`permission-configuration`。
:::

```{config} severity_threshold
:type: string
:default: "warning"
:options: ["info", "warning", "error"]

审查结果严重程度阈值，低于此级别的问题将不被报告。
```

## 输入

```{input} repository
:type: string
:required: true
代码仓库路径或URL
```

## 输出

```{output} issues
:type: list<Issue>
发现的问题列表
```

::{example} 使用示例
```python
result = await skill.run(
    repository="https://github.com/example/repo",
    severity_threshold="error"
)
```
:::
```

**反例（frontmatter与内容混排）：**

```markdown
# 代码审查技能

- 版本：1.2.0
- 标签：code-review, security

配置项：...
输入：...
输出：...
```

### 7.5 场景五：版本记录与弃用标记

**场景描述：** 记录接口/参数的版本变更历史，标记已弃用或即将弃用的功能，提供迁移指南。

**推荐使用：**
- ````{deprecated}```` 自定义指令标记弃用项
- `:since:`/`:removed-after:`/`:alternative:` 选项
- `::{since}::` 标记新增版本
- `{version-ref}`自定义Role引用版本号

**可选使用：**
- `::{warning}::` 强调弃用通知
- `{seealso}`链接到迁移指南

**不推荐使用：**
- 只在文档中用文字写"已弃用"而无结构化标记
- 不提供替代方案就标记弃用
- 用删除线（~~）表示弃用（机器无法识别）

**正例：**

````markdown
```{deprecated} old_auth_method
:since: "2.0.0"
:removed-after: "3.0.0"
:alternative: "oauth2_auth"

此认证方式已弃用，将在3.0版本移除。

请迁移到{literal}`oauth2_auth`接口，迁移指南参见{doc}`migration-guide-v2-v3.md`。

```{migration}
将请求头从`X-Auth-Token`改为`Authorization: Bearer <token>`。
```
:::

```{param} new_field
:type: string
:since: "1.1.0"

新字段说明，1.1.0版本新增。
```
````

**反例（非结构化标记）：**

```markdown
~~old_auth_method~~ （已弃用，请改用新方法）

**new_field** - 这个是新加的，好像是1.1版本加的？
```

### 7.6 场景六：错误码与异常说明

**场景描述：** 列出接口可能返回的错误码、错误场景、处理建议。

**推荐使用：**
- ````{error-code}````自定义指令
- `:code:`/`:status:`/`:type:`/`:retryable:`选项
- 每个错误码一个独立指令块

**可选使用：**
- `::{tip}::`提供错误排查建议
- `{param-ref}`引用触发该错误的参数字段

**不推荐使用：**
- 大表格混合所有错误码（独立指令块更易维护和引用）
- 错误码定义分散在文档各处（集中在"错误处理"章节）

**正例：**

````markdown
```{error-code} EMAIL_ALREADY_EXISTS
:http-status: 409
:type: validation_error
:retryable: false

邮箱已被注册。

当{param-ref}`email`字段对应的邮箱已存在于用户表中时返回此错误。
请引导用户使用"忘记密码"功能或更换邮箱。
```

```{error-code} RATE_LIMIT_EXCEEDED
:http-status: 429
:type: rate_limit
:retryable: true

请求过于频繁。

请使用指数退避策略重试，详见{ref}`rate-limit-policy`。
```
````

**反例（大表格，但可在过渡期使用）：**

```markdown
| 错误码 | HTTP状态码 | 类型 | 可重试 | 说明 |
|---|---|---|---|---|
| EMAIL_ALREADY_EXISTS | 409 | validation | 否 | 邮箱已存在 |
| RATE_LIMIT_EXCEEDED | 429 | rate_limit | 是 | 限流 |
```

---
