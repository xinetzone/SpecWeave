---
id: "spec-ver-02"
title: "02 版本号命名规则"
source: "rules/spec-version-control.md#02"
x-toml-ref: "../../../.meta/toml/.agents/rules/spec-version-control/02-version-naming.toml"
---

# 02 版本号命名规则


### 2.1 格式定义

版本号格式为 `version: X.Y`，其中：

| 组成部分 | 说明 |
|---------|------|
| `X` | 主版本号（Major Version） |
| `Y` | 次版本号（Minor Version） |

### 2.2 主版本号变更规则

**触发条件**：当发生以下破坏性变更时，主版本号递增，次版本号重置为 0：

- 移除现有需求或功能
- 改变已有需求的行为定义
- 废弃现有 API 或接口协议
- 更改已发布版本中确立的核心概念

**示例**：

```
version: 1.0  →  version: 2.0
```

### 2.3 次版本号变更规则

**触发条件**：当发生以下非破坏性变更时，次版本号递增：

- 新增需求或功能
- 扩展现有功能的适用范围
- 优化或改进现有实现而不改变行为
- 文档澄清不影响原有语义

**示例**：

```
version: 1.0  →  version: 1.1
```

### 2.4 版本号声明位置

版本号**必须**在 `spec.md` 文件头部声明，使用 TOML frontmatter 格式：

```toml
---
version: 1.0
---
```

---

---

## 相关模式

- [规范三同步原则](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/spec-triple-sync.md)
- [文档结构化Diff与SemVer](../../docs/retrospective/patterns/code-patterns/structured-doc-diff-semver.md)
---

← 上一章: [01 概述](01-overview.md) | **[返回索引](../spec-version-control.md)** | 下一章: [03 变更类型分类](03-change-types.md) →
