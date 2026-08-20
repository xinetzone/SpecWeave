---
type: Specification
title: 版本控制
description: OKF v0.2 版本规则：<major>.<minor> 格式、次版本为向后兼容增量、主版本为破坏性变更，以及知识包声明目标版本方式与已推迟事项。
tags: [okf, spec, versioning]
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: okf-spec
    resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

# 版本控制

本文档规定 OKF 版本为 **0.2**。修订（revision）以 `<major>.<minor>` 形式版本化：[^okf-spec]

- **次版本（minor）**升级引入向后兼容（backward-compatible）的增量变更（新增可选字段、新增约定小节标题）。
- **主版本（major）**升级可以做（may make）破坏性变更（重命名必填字段、变更保留文件名）。

知识包可以（MAY）在知识包根 `index.md` 的 frontmatter 块中以 `okf_version: "0.2"` 声明其所面向的版本（这是 `index.md` 中唯一允许出现 frontmatter 的地方）。[^okf-spec]

```yaml
okf_version: "0.2"
```

不理解所声明版本的消费者应当（SHOULD）尝试尽最大努力（best-effort）消费，而非拒绝该知识包。

## 已考虑并推迟（Considered and deferred）

以下事项有意留待未来的修订：[^okf-spec]

- 完整的运行时协议（runtime protocol）：回执（receipt）与裁决（verdict）的线格式（wire format），以及一次运行周围的认证生命周期（attestation lifecycle）。
- 认证器（attester）的 ABI、可移植性（portability）与沙箱化（sandboxing），很可能与未来在服务（serving）与 Skills 上的工作一并打包。
- 认证缓存（attestation caching）。
- 语义层模板（semantic-layer templates，如 Looker、dbt），其认证器比较从 SQL 相等性转向模型与绑定相等性（model-and-binding equality）。

## 相关概念

- [知识包结构](./bundle-structure.md)

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。