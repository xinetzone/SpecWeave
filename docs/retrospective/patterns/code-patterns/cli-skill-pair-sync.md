---
id: "cli-skill-pair-sync"
source: "docs/retrospective/reports/competitive-analysis/retrospective-minitest-ecosystem-learning-20260707/insight-extraction.md#模式6"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/code-patterns/cli-skill-pair-sync.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
related_patterns:
  - "cli-as-api-design"
  - "cli-json-pipeline"
---
> **来源**：从Minitest AI QA测试平台生态系统复盘萃取，经Minitest Agent Skills验证

# CLI-Skill配对同步模式（CLI-Skill Pair Sync Pattern）

## 模式类型

代码模式（AI Agent工具设计）

## 成熟度

L1 首次萃取（Minitest Agent Skills验证）

## 适用场景

CLI工具需要同时支持人类用户和AI Agent用户的场景。

## 问题背景

CLI命令演进时，AI Agent使用的Skill文档容易过时，导致Agent调用已变更/已删除的命令。

## 核心规则

### 方案

- Skill文档作为AI Agent使用CLI的权威指令源
- CLI命令变更必须在配对PR中同步更新Skill文档和Quick Reference表
- CLI提供`minitest init --agent`输出与Skill一致的原始markdown
- 动态数据（如flow-types）通过CLI命令实时获取（`minitest flow-types list`），不硬编码在Skill中
- CLI退出码标准化，便于Skill可靠处理

### 同步机制详解

| 同步要素 | 实现方式 | 目的 |
|---------|---------|------|
| 权威源 | Skill文档作为AI Agent使用CLI的权威指令源 | 确保Agent使用最新命令定义 |
| 配对PR | CLI命令变更必须在配对PR中同步更新Skill文档 | 防止文档与代码脱节 |
| 原始输出 | `minitest init --agent`输出原始markdown | Agent可直接按步骤执行 |
| 动态获取 | 动态数据通过CLI命令实时获取 | 避免硬编码过时数据 |
| 退出码标准 | CLI退出码标准化 | 便于Skill可靠处理错误 |

## 验证清单

- [ ] Skill文档与CLI命令定义保持同步
- [ ] CLI命令变更在配对PR中同步更新Skill文档
- [ ] `minitest init --agent`输出原始markdown到stdout
- [ ] 动态数据（如flow-types）通过CLI命令实时获取
- [ ] CLI退出码标准化，便于Skill可靠处理

## 最佳实践

- **双入口设计**：CLI同时支持人类交互和AI Agent调用
- **--json管道友好**：JSON到stdout，诊断到stderr，camelCase序列化
- **Playbook引导**：`minitest init`输出结构化的onboarding playbook
- **非阻塞更新检查**：24小时缓存，在main callback中异步检查，不阻塞命令执行

## 与cli-as-api-design的关系

本模式是cli-as-api-design在AI Agent场景的延伸，专注于CLI与AI Skill文档的同步机制，确保Agent始终使用最新的命令定义。
