---
id: "templates-analysis-dimension-skills-plugin"
title: "Skills/插件类分析维度模板"
source: "AGENTS.md#模板"
x-toml-ref: "../../../.meta/toml/.agents/templates/analysis-dimension-templates/skills-plugin-dimension.toml"
version: "1.1.0"
patterns_applied: ["spec-driven-development"]
---
# Skills/插件类分析维度模板

## 核心分析维度

### 1. Skill定义

| 维度 | 分析要点 |
|------|---------|
| Frontmatter | name、description、触发词设计 |
| 能力声明 | 提供的核心能力、能力边界 |
| 使用场景 | 适用场景、典型用例 |

### 2. 触发词设计

| 维度 | 分析要点 |
|------|---------|
| 关键词 | 触发Skill的关键词列表 |
| 语义匹配 | 语义理解、模糊匹配策略 |
| 上下文感知 | 基于对话上下文的触发 |

### 3. 协作模式

| 维度 | 分析要点 |
|------|---------|
| CLI调用 | CLI工具调用、命令行参数构造 |
| API调用 | REST/gRPC接口调用、认证处理 |
| 数据交换 | 输入输出数据格式、数据转换 |

### 4. 最佳实践

| 维度 | 分析要点 |
|------|---------|
| Onboarding | 首次使用引导、Playbook设计 |
| Profile管理 | Persona设计、配置文件管理 |
| 用户故事 | 验收标准编写、Story类型枚举 |

### 5. 生命周期

| 维度 | 分析要点 |
|------|---------|
| 初始化 | 启动时初始化、延迟初始化 |
| 运行时 | 请求处理、资源管理 |
| 销毁 | 优雅关闭、资源释放 |

### 6. 安全性

| 维度 | 分析要点 |
|------|---------|
| 身份认证 | API密钥、OAuth、JWT |
| 权限控制 | 细粒度权限、角色管理 |
| 数据隔离 | 租户隔离、数据加密 |

## 关键实体标记

报告末尾必须附「关键实体汇总表」：

```markdown
## 关键实体

| 类型 | 名称 | 说明 |
|------|------|------|
| API | POST /api/v1/test/run | 执行测试任务接口 |
| CONFIG | MINITEST_API_KEY | API密钥配置 |
| MODULE | agent.skills.minitest | Minitest Skill模块 |
```

**必须标记的实体类型**：

| 标记类型 | 说明 | 示例 |
|---------|------|------|
| API | REST/gRPC/WebSocket接口 | POST /api/v1/test/run |
| CONFIG | 环境变量或配置文件项 | MINITEST_API_KEY |
| MODULE | 代码模块/包名或关键组件 | agent.skills.minitest |

## 输出格式要求

```markdown
## Skills/插件类分析报告 - {Skill名称}

### 1. Skill定义分析
- Frontmatter：{描述}
- 能力声明：{列表}
- 使用场景：{列表}

### 2. 触发词设计分析
- 关键词：{列表}
- 语义匹配：{描述}
- 上下文感知：{描述}

### 3. 协作模式分析
- CLI调用：{描述}
- API调用：{描述}
- 数据交换：{描述}

### 4. 最佳实践分析
- Onboarding：{描述}
- Profile管理：{描述}
- 用户故事：{描述}

### 5. 安全性分析
- 身份认证：{描述}
- 权限控制：{描述}
- 数据隔离：{描述}

### 6. 设计亮点与改进建议
- 亮点：{列表}
- 建议：{列表}

## 关键实体

| 类型 | 名称 | 说明 |
|------|------|------|
| ... | ... | ... |
```

## 质量检查清单

### L0 门禁项

- [ ] Skill定义分析完整，包含Frontmatter和能力声明
- [ ] 触发词设计分析包含关键词列表和语义匹配策略
- [ ] 协作模式分析包含CLI调用和API调用说明
- [ ] 最佳实践分析包含Onboarding和Profile管理
- [ ] 报告末尾附「关键实体汇总表」

### L1 质量项

- [ ] Frontmatter分析包含触发词设计原则说明
- [ ] 协作模式分析包含数据交换格式和转换说明
- [ ] 最佳实践分析包含用户故事创建规则说明
- [ ] 生命周期分析包含资源管理和释放机制
- [ ] 安全性分析包含身份认证和权限控制策略

### L2 优化项

- [ ] 提供Skill调用流程图（Mermaid）
- [ ] 提供触发词匹配策略图（Mermaid）
- [ ] 分析CLI-Skill配对同步模式
- [ ] 识别可复用的Skill设计模式
- [ ] 提供具体的改进建议和优先级

---

[CMD-LOG] | level=INFO | cmd=template | step=S1 | event=TEMPLATE_LOADED | session=analysis-dimension-skill | msg=Skills/插件类分析维度模板已加载
