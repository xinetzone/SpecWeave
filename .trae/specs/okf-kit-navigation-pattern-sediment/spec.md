# 沉淀 okf-kit 洞察1「渐进式导航」到已有模式 Spec

## Why

okf-kit Wiki 教程的七概念执行报告在 I（洞察）阶段识别出 **洞察1——渐进式导航是 Agent 可用性的关键**（现象：每个目录都生成 `index.md` 列出子目录和文件；建议：任何面向 Agent 的知识打包格式都应内置目录索引机制）。该洞察需要经 E（萃取）阶段沉淀为可复用模式。

经模式库比对，已有架构模式 `agent-knowledge-graph-navigation`（L1 实验性，validation_count=1）已覆盖本洞察的核心机制——三层索引中的「子目录 index.md 局部路由」层。因此按萃取约束「禁止创建重复模式」，本次采用 **补充已有模式**（新增独立验证案例 + 成熟度升级），而非新建重复模式。

## What Changes

- 补充 [agent-knowledge-graph-navigation.md](../../../docs/retrospective/patterns/architecture-patterns/agent-knowledge-graph-navigation.md)：
  - 新增「okf-kit v0.3.3 源码实现」作为第 4 个实战案例（与既有「OKF v0.2 规范」形成「规范 + 实现」双重独立验证）
  - frontmatter 追加 okf-kit 报告 source 交叉引用（必要时将 `source` 由单字符串转为列表，与库内 `navigation-hub-filename-contract` 一致）
  - `validation_count` 1 → 2，`maturity` L1 → L2
  - 更新文末版本说明
- 更新 [README.md](../../../docs/retrospective/patterns/architecture-patterns/README.md) 索引：该模式行成熟度「L1 实验性」→「L2 已验证」，说明补充「okf-kit 实现验证」
- 补充交叉引用（okf-kit 报告 ↔ 模式）
- 运行链接检查与文件名/格式校验，原子提交

## Impact

- Affected specs：无既有 change-id 冲突
- Affected code：
  - `.agents/docs/retrospective/patterns/architecture-patterns/agent-knowledge-graph-navigation.md`
  - `.agents/docs/retrospective/patterns/architecture-patterns/README.md`
  - `docs/knowledge/learning/03-agent-platforms-tools/okf-kit-wiki/seven-concepts-report.md`（可选交叉引用）

## ADDED Requirements

### Requirement: 补充已有模式的验证案例
系统 SHALL 在已有模式 `agent-knowledge-graph-navigation` 中补充 okf-kit v0.3.3 作为独立验证案例，而非新建重复模式。

#### Scenario: 沉淀洞察1时发现已有模式
- **WHEN** 沉淀 okf-kit 洞察1（每目录生成 index.md 的渐进式导航机制）
- **THEN** 识别到已有模式 `agent-knowledge-graph-navigation` 已覆盖该机制，选择「补充」而非「新建」

#### Scenario: 补充第 2 个独立验证案例后成熟度升级
- **WHEN** 模式已累计「OKF v0.2 规范」与「okf-kit v0.3.3 实现」两个独立验证来源
- **THEN** `validation_count` 更新为 2，`maturity` 从 L1 升级为 L2

## MODIFIED Requirements

### Requirement: agent-knowledge-graph-navigation 模式
在原「三层索引 + Frontmatter 预过滤 + 图结构显式链接」模式基础上，新增 okf-kit v0.3.3 实现作为验证案例，并将成熟度升级为 L2（已验证）。

#### Scenario: 索引一致性
- **WHEN** 模式成熟度升级
- **THEN** architecture-patterns/README.md 索引中对应行的成熟度同步更新为 L2，避免索引与模式 frontmatter 不一致

## REMOVED Requirements

（无）