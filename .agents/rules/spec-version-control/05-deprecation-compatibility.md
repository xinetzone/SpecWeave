---
id: "spec-ver-05"
title: "05 弃用流程与版本兼容性"
source: "rules/spec-version-control.md#05"
x-toml-ref: "../../../.meta/toml/.agents/rules/spec-version-control/05-deprecation-compatibility.toml"
---

# 05 弃用流程与版本兼容性


### 6.1 弃用判定

当需要废弃某个功能或需求时，应评估以下因素：

- 功能使用频率和依赖程度
- 替代方案的成熟度
- 迁移成本和影响范围

### 6.2 弃用步骤

**步骤一：在 SPEC 文档中标记弃用**

在相关需求章节中添加 `deprecated: true` 标记，并说明弃用原因和替代方案。

```markdown
## 用户认证

> deprecated: true
> 替代方案：使用新版 OAuth 2.0 认证接口
> 预计移除版本：2.0

旧版用户认证接口，将于 v2.0 版本中移除。
```

**步骤二：更新版本号**

设置弃用版本号，弃用声明应使版本号递增（次版本号）。

```toml
---
version: 1.3
---
```

**步骤三：添加 Migration 章节**

在 SPEC 文档末尾添加 Migration 章节，提供详细的迁移指南。

```markdown
## Migration

### 从 v1.x 迁移至 v2.0

#### 弃用功能迁移

**旧版用户认证接口**

- 迁移时间：v1.3 至 v2.0 发布前
- 迁移步骤：
  1. 在配置文件中启用 `oauth2.enabled: true`
  2. 更新客户端代码使用 `/api/v2/auth` 端点
  3. 更新认证令牌刷新逻辑，参考 [OAuth 2.0 文档](./docs/oauth2.md)
- 回滚方案：v2.0 发布前可回滚至 v1.2 版本
```

**步骤四：记录变更日志**

```markdown
- 2025-06-15 | deprecated | 旧版用户认证接口（替代方案：迁移至新版 OAuth 2.0 接口）
```

### 6.3 弃用后移除

当主版本号递增至弃用功能标记的版本时，执行移除操作：

1. 从 SPEC 文档中删除弃用条目
2. 在 changelog 中添加 `removed` 记录
3. 确保迁移指南完整且可执行

---

### 7.1 向后兼容原则

新版本应尽量保持向后兼容，确保已有用户在不做修改的情况下能够继续正常使用系统。

### 7.2 破坏性变更处理

当必须进行破坏性变更时，应遵循以下原则：

**提前通知**：

- 在 changelog 中明确标注为破坏性变更
- 在 SPEC 文档中提供详细的迁移指南
- 主版本号递增时，在文档顶部添加不兼容说明

**文档结构示例**：

```markdown
---
version: 2.0
---

# 用户认证系统规格

> **Breaking Changes in v2.0**
>
> 本版本包含以下破坏性变更：
> - 移除了 v1.x 中的旧版认证接口
> - 改变了令牌刷新机制
>
> 请参阅 [Migration](#migration) 章节获取迁移指南。
```

### 7.3 主版本号变更含义

| 版本类型 | 兼容性 | 说明 |
|----------|--------|------|
| 次版本号递增 | 向后兼容 | 新增功能，不影响现有功能 |
| 主版本号递增 | 不兼容 | 破坏性变更，需要迁移 |

---

---

## 相关模式

- [规范三同步原则](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/spec-triple-sync.md)
- [文档结构化Diff与SemVer](../../../docs/retrospective/patterns/code-patterns/structured-doc-diff-semver.md)
---

← 上一章: [04 变更日志格式与维护](04-changelog-format.md) | **[返回索引](../spec-version-control.md)** | 下一章: [06 版本演进示例与检查清单](06-evolution-checklist.md) →
