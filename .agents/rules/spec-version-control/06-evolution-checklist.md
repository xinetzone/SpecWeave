---
id: "spec-ver-06"
title: "06 版本演进示例与检查清单"
source: "rules/spec-version-control.md#06"
x-toml-ref: "../../../.meta/toml/.agents/rules/spec-version-control/06-evolution-checklist.toml"
---

# 06 版本演进示例与检查清单


### 8.1 初始版本 v1.0

```toml
---
version: 1.0
---

# 用户管理模块规格

## 功能需求

### FR-001 用户注册

系统应支持用户通过邮箱进行注册。

### FR-002 用户登录

系统应支持用户通过邮箱和密码登录。

<!-- changelog -->
## Changelog

- 2025-01-01 | added | 初始版本，定义用户注册和登录功能
<!-- changelog -->
```

### 8.2 演进至 v1.1

**变更内容**：

- 新增：支持手机号注册
- 修改：登录失败锁定次数从 3 次调整为 5 次

**更新后的文档**：

```toml
---
version: 1.1
---

# 用户管理模块规格

## 功能需求

### FR-001 用户注册

系统应支持用户通过邮箱或手机号进行注册。

### FR-002 用户登录

系统应支持用户通过邮箱和密码登录。当连续登录失败 5 次后，账户将被锁定 30 分钟。

<!-- changelog -->
## Changelog

- 2025-04-15 | modified | 登录失败锁定次数调整为 5 次（原内容：登录失败锁定次数为 3 次）
- 2025-04-10 | added | 支持手机号注册功能
- 2025-01-01 | added | 初始版本，定义用户注册和登录功能
<!-- changelog -->
```

### 8.3 演进至 v1.2

**变更内容**：

- 新增：支持第三方登录（OAuth 2.0）
- 弃用：计划在 v2.0 中移除纯密码登录

**更新后的文档**：

```toml
---
version: 1.2
---

# 用户管理模块规格

## 功能需求

### FR-001 用户注册

系统应支持用户通过邮箱或手机号进行注册。

### FR-002 用户登录

> deprecated: true
> 替代方案：迁移至 OAuth 2.0 登录
> 预计移除版本：2.0

系统应支持用户通过邮箱和密码登录。当连续登录失败 5 次后，账户将被锁定 30 分钟。

### FR-003 第三方登录

系统应支持通过 OAuth 2.0 进行第三方登录。

## Migration

### 从纯密码登录迁移至 OAuth 2.0

详见 [OAuth 2.0 迁移指南](./docs/oauth2-migration.md)。

<!-- changelog -->
## Changelog

- 2025-05-20 | deprecated | 纯密码登录功能（替代方案：迁移至 OAuth 2.0 登录）
- 2025-05-15 | added | 支持 OAuth 2.0 第三方登录
- 2025-04-15 | modified | 登录失败锁定次数调整为 5 次（原内容：登录失败锁定次数为 3 次）
- 2025-04-10 | added | 支持手机号注册功能
- 2025-01-01 | added | 初始版本，定义用户注册和登录功能
<!-- changelog -->
```

### 8.4 演进至 v2.0

**变更内容**：

- 移除：纯密码登录功能
- 修改：用户标识符从邮箱改为用户 ID

**更新后的文档**：

```toml
---
version: 2.0
---

> **Breaking Changes in v2.0**
>
> 本版本包含以下破坏性变更：
> - 移除了纯密码登录功能
> - 用户标识符从邮箱改为用户 ID
>
> 请参阅 [Migration](#migration) 章节获取迁移指南。

# 用户管理模块规格

## 功能需求

### FR-001 用户注册

系统应支持用户通过邮箱、手机号或第三方 OAuth 进行注册。

### FR-002 用户标识

每位用户拥有唯一用户 ID，系统内部使用用户 ID 进行用户识别。

## Migration

### 从 v1.x 迁移至 v2.0

#### 1. 移除纯密码登录

已迁移至 OAuth 2.0 的用户不受影响。仍在使用纯密码登录的用户需在 v2.0 发布前完成 OAuth 迁移。

#### 2. 用户标识符变更

- 旧版本中使用邮箱作为用户标识
- 新版本中使用用户 ID 作为唯一标识
- API 响应中 `user_id` 字段已替换 `email` 字段
- 需要更新所有依赖邮箱字段的代码

<!-- changelog -->
## Changelog

- 2025-06-01 | removed | 移除纯密码登录功能（迁移方案：已全面迁移至 OAuth 2.0）
- 2025-06-01 | modified | 用户标识符从邮箱改为用户 ID（原内容：使用邮箱作为用户标识符）
- 2025-05-20 | deprecated | 纯密码登录功能（替代方案：迁移至 OAuth 2.0 登录）
- 2025-05-15 | added | 支持 OAuth 2.0 第三方登录
- 2025-04-15 | modified | 登录失败锁定次数调整为 5 次（原内容：登录失败锁定次数为 3 次）
- 2025-04-10 | added | 支持手机号注册功能
- 2025-01-01 | added | 初始版本，定义用户注册和登录功能
<!-- changelog -->
```

---

## 附录：快速检查清单

版本发布前，请确认以下项目：

- [ ] 版本号已更新
- [ ] 新增/修改/移除/弃用的需求已记录
- [ ] changelog 记录按时间倒序排列
- [ ] modified 和 removed 类型包含原内容说明
- [ ] removed 类型提供迁移方案
- [ ] deprecated 类型提供替代方案
- [ ] 主版本号变更已在文档顶部说明破坏性变更
- [ ] Migration 章节包含详细的迁移指南

版本发布前，请确认以下项目：

- [ ] 版本号已更新
- [ ] 新增/修改/移除/弃用的需求已记录
- [ ] changelog 记录按时间倒序排列
- [ ] modified 和 removed 类型包含原内容说明
- [ ] removed 类型提供迁移方案
- [ ] deprecated 类型提供替代方案
- [ ] 主版本号变更已在文档顶部说明破坏性变更
- [ ] Migration 章节包含详细的迁移指南

---

## 相关模式

- [规范三同步原则](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/spec-triple-sync.md)
- [文档结构化Diff与SemVer](../../../docs/retrospective/patterns/code-patterns/structured-doc-diff-semver.md)
---

← 上一章: [05 弃用流程与版本兼容性](05-deprecation-compatibility.md) | **[返回索引](../spec-version-control.md)**
