---
id: "spec-ver-04"
title: "04 变更日志格式与维护"
source: "rules/spec-version-control.md#04"
x-toml-ref: "../../../.meta/toml/.agents/rules/spec-version-control/04-changelog-format.toml"
---

# 04 变更日志格式与维护


### 4.1 标记语法

变更日志必须使用 `<!-- changelog -->` 注释标记包裹，形成独立的章节区域。

### 4.2 章节结构

```markdown
<!-- changelog -->
## Changelog

<!-- 变更记录列表 -->
<!-- changelog -->
```

### 4.3 变更记录格式

每条变更记录遵循以下格式：

```
- YYYY-MM-DD | <type> | <description>
```

| 组成部分 | 说明 |
|---------|------|
| `YYYY-MM-DD` | 变更日期（必须使用 ISO 8601 格式） |
| `<type>` | 变更类型标识 |
| `<description>` | 变更描述（modified 和 removed 类型需包含原内容说明） |

### 4.4 完整示例

```markdown
<!-- changelog -->
## Changelog

- 2025-06-24 | added | 支持 WebSocket 实时通信功能
- 2025-06-20 | modified | 登录失败锁定次数调整为 5 次（原内容：登录失败锁定次数为 3 次）
- 2025-06-15 | deprecated | 旧版用户认证接口（替代方案：迁移至新版 OAuth 2.0 接口）
- 2025-06-01 | removed | 移除对 TLS 1.0 和 1.1 的支持（迁移方案：升级至 TLS 1.2 及以上版本）
<!-- changelog -->
```

---

### 5.1 记录时机

每次重大变更必须在 changelog 中添加相应记录，重大变更包括：

- 主版本号递增
- 次版本号递增
- 新增、修改、移除、弃用任何需求

### 5.2 记录内容要求

每条变更记录必须包含以下要素：

| 要素 | 必须性 | 说明 |
|-----|-------|------|
| 日期 | 必须 | 精确到年月日 |
| 类型 | 必须 | added/modified/removed/deprecated |
| 描述 | 必须 | 清晰描述变更内容 |

### 5.3 排序规则

变更记录按时间倒序排列，**最新变更位于章节顶部**。

### 5.4 内容实质性要求

changelog 章节必须包含实质性内容，**禁止出现空章节**。

| 合规示例 | 不合规示例 |
|----------|-----------|
| 包含具体变更记录 | 仅包含章节标题无内容 |
| 提供完整信息 | 仅有日期无类型或描述 |

### 5.5 版本号更新同步

变更日志维护必须与版本号更新同步进行：

| 变更类型 | 版本号操作 | changelog 操作 |
|----------|-----------|---------------|
| 新增功能 | 次版本号 +1 | 添加 `added` 记录 |
| 行为修改 | 主版本号 +1 或次版本号 +1 | 添加 `modified` 记录 |
| 功能移除 | 主版本号 +1 | 添加 `removed` 记录 |
| 功能弃用 | 次版本号 +1 | 添加 `deprecated` 记录 |

---

---

## 相关模式

- [规范三同步原则](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/spec-triple-sync.md)
- [文档结构化Diff与SemVer](../../../docs/retrospective/patterns/code-patterns/structured-doc-diff-semver.md)
---

← 上一章: [03 变更类型分类](03-change-types.md) | **[返回索引](../spec-version-control.md)** | 下一章: [05 弃用流程与版本兼容性](05-deprecation-compatibility.md) →
