---
id: "checklist-create-token-optimizer-role"
title: "创建Token优化专家角色 - 验证清单"
date: "2026-08-01"
status: "draft"
---

# 创建Token优化专家（Token Optimizer）角色 - 验证清单

## 文件创建验证
- [ ] token-optimizer.md 文件已在 `d:\AI\.agents\roles\` 目录下创建
- [ ] 文件名使用 kebab-case：`token-optimizer.md`，纯英文无中文
- [ ] YAML frontmatter 格式正确，包含 id、title、source 字段
- [ ] frontmatter 中 id 为 `"token-optimizer"`，title 包含中文角色名称

## 角色内容验证 - Description
- [ ] Description 清晰描述角色定位：LLM Token使用优化专家
- [ ] 提到核心目标：在成本-质量-延迟三维空间寻找帕累托最优解
- [ ] 语言为标准现代汉语，无网络流行语

## 角色内容验证 - Responsibilities
- [ ] 包含Token优化方案设计与技术选型职责（关联决策树/选型矩阵）
- [ ] 包含Prompt结构优化职责（静态前缀+动态后缀、缓存友好设计）
- [ ] 包含分层缓存策略设计职责（三层缓存架构）
- [ ] 包含上下文压缩与对话管理策略职责
- [ ] 包含模型路由与分级策略职责
- [ ] 包含优化方案评审与风险识别职责（27条禁令合规检查）
- [ ] 包含评估指标体系建立职责
- [ ] 包含渐进式优化路线图规划职责
- [ ] 包含知识库查阅指引，引用了关键文档路径
- [ ] 核心概念覆盖：三大本质路径（减少/复用/压缩）
- [ ] 核心概念覆盖：五大最佳实践模式（P-001到P-005）
- [ ] 核心概念覆盖：P0级禁令合规检查
- [ ] 核心概念覆盖：三维权衡框架
- [ ] 所有知识库引用使用相对路径（相对于.agents/roles/目录）

## 角色内容验证 - Non-Goals
- [ ] 明确声明不负责整体架构设计（归architect）
- [ ] 明确声明不负责具体代码实现（归developer）
- [ ] 明确声明不负责代码审查（归reviewer）
- [ ] 明确声明不负责测试编写（归tester）
- [ ] 明确声明不负责任务编排协调（归orchestrator）
- [ ] 明确声明不做脱离质量底线的极端成本优化（C-001）
- [ ] 明确声明不跳过质量基线直接给出优化建议（C-024）
- [ ] 与其他6个现有角色的职责边界清晰，无重叠

## README.md索引更新验证
- [ ] 角色职责矩阵表格中新增了token-optimizer行
- [ ] 新行包含：角色名、ID(token-optimizer)、领域(optimization)、层级(specialist)、层级标记、核心职责
- [ ] 表格列数与修改前一致（6列）
- [ ] 表格Markdown语法正确（分隔符行完整）
- [ ] 文件结构说明代码块中添加了token-optimizer.md条目
- [ ] 修改表格时替换了整个表格而非局部修改（遵循project_memory约束）
- [ ] 未破坏README.md中其他已有内容

## 格式一致性验证
- [ ] 标题层级与现有角色文件一致（# 角色名 → ## Description → ## Responsibilities → ## Non-Goals）
- [ ] 列表使用 `-` 符号，缩进风格与architect.md/developer.md一致
- [ ] 相对路径格式与现有角色引用方式一致（参考architect.md中的 `../docs/knowledge/decisions/README.md`）
- [ ] frontmatter字段顺序与现有角色一致（id → title → x-toml-ref → source，或按决策省略x-toml-ref）
- [ ] 无file:///绝对路径引用（遵循开发规范）

## 链接有效性验证
- [ ] Responsibilities中引用的llm-token-optimization/README.md存在
- [ ] Responsibilities中引用的10-quick-reference.md存在
- [ ] Responsibilities中引用的09-constraints.md存在
- [ ] Responsibilities中引用的06-decision-framework下关键文档存在
- [ ] 所有Markdown链接指向的文件在文件系统中真实存在

## 术语准确性验证
- [ ] 使用的专业术语与glossary.md中的定义一致
- [ ] "Token"、"KV缓存"、"Prompt Caching"、"语义缓存"等术语使用正确
- [ ] 三大路径名称统一：减少(Reduce)/复用(Reuse)/压缩(Compress)
- [ ] 模式ID引用正确（P-001到P-005）
- [ ] 禁令引用格式正确（C-001、C-002等）

## 提交验证
- [ ] git status显示仅两个文件变更：1个新增（token-optimizer.md），1个修改（README.md）
- [ ] 无意外的文件删除或其他文件修改
- [ ] commit message符合Conventional Commits规范
- [ ] 提交单一职责，仅包含Token优化专家角色创建相关变更
