---
id: "process-patterns-readme"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/process-patterns/README.toml"
---

# 流程模式索引（process-patterns）

本目录存放流程级可复用模式，聚焦于开发流程、构建流程、运维流程等宏观层面的最佳实践。

## 模式清单

| 模式 | 说明 | 成熟度 | 适用场景 |
|------|------|--------|---------|
| [container-build-env-optimization.md](container-build-env-optimization.md) | 容器化构建环境优化模式：镜像源优化+超时重试配置+命令链拆分+验证环节添加+多阶段构建，提升构建成功率和稳定性 | L2 已验证 | Docker镜像构建涉及网络依赖和复杂环境配置的场景 |

## 成熟度定义

| 等级 | 定义 | 验证条件 |
|------|------|---------|
| L1 实验性 | 仅 1 次成功案例，待更多验证 | 验证次数 = 1 |
| L2 已验证 | ≥ 2 次成功案例，模式稳定 | 验证次数 ≥ 2 |
| L3 可复用 | 已被其他任务复用，有文档化示例 | 复用次数 ≥ 1 |

> 详细评估标准见 [patterns/README.md](../README.md#模式成熟度评估标准)。

## 使用方式

1. 根据场景查找匹配模式
2. 阅读模式正文了解规则与正反例
3. 按模式规则执行操作
4. 验证后更新模式成熟度（若适用）