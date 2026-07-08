---
id: "templates-analysis-dimension-templates"
title: "差异化分析维度模板库"
source: "AGENTS.md#模板"
x-toml-ref: "../../../.meta/toml/.agents/templates/analysis-dimension-templates/README.toml"
version: "1.1.0"
patterns_applied: ["spec-driven-development", "preflight-exploration"]
---
# 差异化分析维度模板库

> **适用场景**：多对象并行分析任务中，为不同类型分析对象定义差异化分析维度，提升分析质量一致性和深度。

## 设计原则

1. **对象类型优先**：按分析对象类型切分，而非按分析维度切分
2. **维度差异化**：不同类型对象关注的核心维度不同
3. **质量一致性**：统一的分析深度要求，避免不同类型仓库分析深度不均
4. **可扩展性**：每个模板预留自定义扩展维度空间
5. **输出标准化**：统一的报告输出格式，便于整合阶段处理

## 模板索引

| 对象类型 | 模板文件 | 核心分析维度 | 适用场景 |
|---------|---------|-------------|---------|
| CLI/工具类 | [cli-tool-dimension.md](cli-tool-dimension.md) | 命令体系、配置管理、认证机制、输出约定、依赖管理 | Python/Go/Node CLI工具分析 |
| CI/集成类 | [ci-integration-dimension.md](ci-integration-dimension.md) | 触发机制、认证流程、构建验证、元数据提取、安全机制 | GitHub Actions/CI流水线分析 |
| 基建/配置类 | [infrastructure-config-dimension.md](infrastructure-config-dimension.md) | 配置结构、风控策略、并发限制、安全更新、版本管理 | Renovate配置/共享Action分析 |
| 示例/Demo类 | [example-demo-dimension.md](example-demo-dimension.md) | 项目结构、集成方式、演示功能、测试模式、构建部署 | 示例应用/演示项目分析 |
| Skills/插件类 | [skills-plugin-dimension.md](skills-plugin-dimension.md) | Skill定义、触发词设计、协作模式、最佳实践、生命周期 | AI Agent Skills/插件分析 |

## 使用方式

### 在tasks.md中引用

```markdown
## [ ] Task 1: minitest-cli CLI工具架构分析
- **Priority**: high
- **分析维度模板**: analysis-dimension-templates/cli-tool-dimension.md
- **Description**: 
  - 分析项目分层结构：commands/、core/、api/、models/、utils/
  - 研究Typer命令体系注册机制与命令组功能
  - 分析配置管理（pydantic-settings）、环境变量加载
```

### 在Pre-flight预探索报告中推荐

预探索报告中应包含「分析维度提示」，为每个分析对象推荐对应的模板：

```markdown
## 分析维度提示

| 分析对象 | 类型 | 推荐模板 | 核心分析维度 |
|---------|------|---------|-------------|
| minitest-cli | CLI/Tool | cli-tool-dimension.md | 命令体系、配置管理、认证机制、输出约定 |
| minitest-trigger | CI/Integration | ci-integration-dimension.md | 认证流程、构建验证、元数据提取、平台集成 |
| renovate-config | Infrastructure/Config | infrastructure-config-dimension.md | 配置结构、风控策略、并发限制、安全更新 |
| demo-app | Example/Demo | example-demo-dimension.md | 项目结构、集成方式、演示功能、测试模式 |
| agent-skills | Skills/Plugin | skills-plugin-dimension.md | Skill定义、触发词设计、协作模式、最佳实践 |
```

## 模板结构说明

每个分析维度模板包含以下部分：

1. **核心分析维度**：6个核心维度，每个维度包含多个分析要点
2. **关键实体标记**：需要标记的关键实体类型（API/CONFIG/MODULE）
3. **输出格式要求**：标准化的报告输出格式模板
4. **质量检查清单**：L0/L1/L2三层质量检查项

## 扩展指南

### 添加新模板

1. 创建新模板文件：`{type}-dimension.md`
2. 添加到README.md模板索引
3. 运行 `python .agents/scripts/fix-x-toml-ref.py --dir .agents/templates/analysis-dimension-templates --write --create-toml` 生成TOML元数据

### 自定义分析维度

在子代理prompt中，可以基于模板维度进行扩展：

```markdown
## 自定义分析维度（可选）

除模板定义的核心维度外，还可根据具体任务需求添加：
- 性能维度：响应时间、吞吐量、资源占用
- 安全维度：漏洞扫描、安全审计、合规性
- 可维护性维度：代码覆盖率、技术债务、文档完备度
```

## 版本记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.1.0 | 2026-07-08 | 增强所有模板分析维度，添加关键实体标记和质量检查清单 |
| 1.0.0 | 2026-07-07 | 初始版本，创建5个基础模板 |

---

[CMD-LOG] | level=INFO | cmd=template | step=S1 | event=TEMPLATE_LIBRARY_UPDATED | session=analysis-dimension-20260708 | msg=差异化分析维度模板库更新完成，包含5种对象类型的分析维度定义
