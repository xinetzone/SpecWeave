---
id: "docs-knowledge-learning-01-agent-protocols-interfaces-protobuf-wiki-index"
title: "Protocol Buffers 版本演进知识库"
category: "knowledge"
date: "2026-07-23"
maturity: "L2-validated"
---
# Protocol Buffers 版本演进知识库

> 本目录 README 索引 protobuf-wiki 所有文档。使用七概念方法论（R→I→E→V 知识沉淀链路）产出，经四视角对抗审查验证。

<!-- README_INDEX_START -->
## 📄 文档索引

| 文档 | 说明 | 标签 |
|------|------|------|
| [Protobuf Wiki 总览](00-overview.md) | 总览与快速入口：TL;DR快速结论、文档结构图、≥3种阅读路径、一页纸版本速查表、与其他wiki的关系 | `protobuf` `overview` `quick-reference` |
| [版本演进时间轴](01-version-timeline.md) | protobuf完整版本时间线（proto1→proto2→proto3各里程碑→Editions 2023/2024），含ASCII时间轴图、8个版本节点详细说明、每个版本的核心特性与设计哲学 | `protobuf` `version-history` `evolution` `timeline` |
| [三版对比矩阵](02-version-comparison.md) | proto2/proto3/Editions 12维度详细对比矩阵（语法/presence/默认值/枚举/扩展/Any/JSON/map/oneof/未知字段/packed/线格式），含≥3个同一message三版写法代码示例、兼容性标注 | `protobuf` `comparison` `proto2` `proto3` `editions` |
| [核心功能演进史](03-feature-evolution.md) | 6个核心功能（presence/required/默认值/枚举/repeated编码/未知字段）的三阶段演进历程，解释"为什么变"而非仅"变了什么"，含设计哲学三阶段总结 | `protobuf` `feature-evolution` `design-philosophy` `presence` |
| [选型决策指南](04-selection-guide.md) | 版本选型决策树、8种场景版本匹配矩阵、序列化IDL版本选型决策模型、6个常见反模式、可打印检查清单 | `protobuf` `selection-guide` `decision-tree` `anti-patterns` |
| [迁移路径与风险清单](05-migration-guide.md) | proto2→proto3 10项迁移检查清单、5阶段灰度迁移策略、Editions迁移（Prototiller/feature映射）、线格式兼容性边界、caffe.proto迁移成本评估实例 | `protobuf` `migration` `checklist` `editions` `caffe` |

<!-- README_INDEX_END -->

## 🔗 相关资源

- [🏠 返回上级：Agent协议与接口技术栈](../README.md)
- [📚 IDL Wiki 基础教程](../idl-wiki/README.md) — IDL概念与protobuf语法基础
- [🔍 Caffe proto2/proto3 对比实例](../../caffe-architecture-wiki/04-proto2-vs-proto3-serialization-analysis.md) — proto2实际使用案例与对比分析
- [📚 文档首页](../../../../README.md)

---

<!-- generated on 2026-07-23 -->
