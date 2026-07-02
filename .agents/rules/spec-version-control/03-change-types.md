---
id: "spec-ver-03"
title: "03 变更类型分类"
source: "rules/spec-version-control.md#03"
x-toml-ref: "../../../.meta/toml/.agents/rules/spec-version-control/03-change-types.toml"
---

# 03 变更类型分类


### 3.1 分类体系

| 类型 | 标识 | 说明 |
|-----|------|------|
| 新增（Added） | `added` | 新增需求或功能 |
| 修改（Modified） | `modified` | 对现有需求的修改 |
| 移除（Removed） | `removed` | 移除现有需求 |
| 弃用（Deprecated） | `deprecated` | 标记为废弃 |

### 3.2 Added 类型

用于描述新增的需求、功能或能力。

**要求**：

- 清晰描述新增内容的范围和边界
- 明确新增功能的约束条件
- 说明新增功能与现有功能的关系

**示例**：

```
- 2025-03-15 | added | 支持多语言配置，用户可通过配置文件指定默认语言
```

### 3.3 Modified 类型

用于描述对现有需求的修改。

**要求**：

- 说明被修改的原内容
- 描述修改后的新内容
- 解释修改的原因

**格式**：

```
- YYYY-MM-DD | modified | 新内容（原内容：原描述）
```

**示例**：

```
- 2025-04-20 | modified | 认证超时时间调整为 30 分钟（原内容：认证超时时间为 15 分钟）
- 2025-05-10 | modified | 密码强度要求至少 8 位字符（原内容：密码强度要求至少 6 位字符）
```

### 3.4 Removed 类型

用于描述被移除的需求或功能。

**要求**：

- 清晰描述被移除的内容
- 提供迁移方案（Migration）
- 明确移除的版本号和时间

**格式**：

```
- YYYY-MM-DD | removed | 被移除内容（迁移方案：具体步骤）
```

**示例**：

```
- 2025-06-01 | removed | 移除对 HTTP 协议的支持（迁移方案：请迁移至 HTTPS 协议，具体配置见 Migration 章节）
```

### 3.5 Deprecated 类型

用于标记即将废弃但尚未移除的功能。

**要求**：

- 说明被弃用的功能
- 提供替代方案
- 明确预计移除的版本

**格式**：

```
- YYYY-MM-DD | deprecated | 被弃用功能（替代方案：替代方案描述）
```

**示例**：

```
- 2025-02-28 | deprecated | v1 API 接口（替代方案：请使用 v2 API 接口，迁移指南见 Migration 章节）
```

---

---

## 相关模式

- [规范三同步原则](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/spec-triple-sync.md)
- [文档结构化Diff与SemVer](../../../docs/retrospective/patterns/code-patterns/structured-doc-diff-semver.md)
---

← 上一章: [02 版本号命名规则](02-version-naming.md) | **[返回索引](../spec-version-control.md)** | 下一章: [04 变更日志格式与维护](04-changelog-format.md) →
