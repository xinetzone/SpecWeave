---
id: "templates-analysis-dimension-ci-integration"
title: "CI/集成类分析维度模板"
source: "AGENTS.md#模板"
x-toml-ref: "../../../.meta/toml/.agents/templates/analysis-dimension-templates/ci-integration-dimension.toml"
version: "1.1.0"
patterns_applied: ["spec-driven-development"]
---
# CI/集成类分析维度模板

## 核心分析维度

### 1. 触发机制

| 维度 | 分析要点 |
|------|---------|
| 触发事件 | push、PR、schedule、workflow_dispatch |
| 触发条件 | 路径过滤、分支过滤、标签过滤 |
| 手动触发 | 是否支持手动触发、触发参数 |

### 2. 认证流程

| 维度 | 分析要点 |
|------|---------|
| OIDC认证 | GitHub OIDC获取云凭证、audience设置、claims解析 |
| API Key认证 | API Key作为备选、Secret管理、密钥轮换 |
| 凭证优先级 | OIDC优先、API Key降级策略 |

### 3. 构建验证

| 维度 | 分析要点 |
|------|---------|
| iOS验证 | .app/.ipa检测、.app自动打包为.ipa |
| Android验证 | ABI验证、构建产物检测 |
| Web验证 | web-targets解析、web-url覆盖 |

### 4. 元数据提取

| 维度 | 分析要点 |
|------|---------|
| Git信息 | commit title自动检测、PR number/title |
| 分支信息 | baseRef/headRef、分支命名规范 |
| PR信息 | PR头SHA覆盖逻辑、Check运行上下文 |

### 5. 安全机制

| 维度 | 分析要点 |
|------|---------|
| Secret管理 | Secret存储、访问控制、最小权限原则 |
| 权限控制 | Workflow权限配置、GITHUB_TOKEN权限 |
| 凭证隔离 | 不同环境的凭证隔离策略 |

### 6. 产物管理

| 维度 | 分析要点 |
|------|---------|
| Artifact上传 | 构建产物、测试报告上传 |
| 部署流程 | 自动化部署、部署环境隔离 |
| 通知机制 | Slack/邮件通知、失败告警 |

## 关键实体标记

报告末尾必须附「关键实体汇总表」：

```markdown
## 关键实体

| 类型 | 名称 | 说明 |
|------|------|------|
| API | POST /api/v1/test/run | 执行测试任务接口 |
| CONFIG | MINITEST_API_KEY | API密钥配置 |
| MODULE | minitest.trigger | CI触发模块 |
```

**必须标记的实体类型**：

| 标记类型 | 说明 | 示例 |
|---------|------|------|
| API | REST/gRPC/WebSocket接口 | POST /api/v1/test/run |
| CONFIG | 环境变量或配置文件项 | MINITEST_API_KEY |
| MODULE | 代码模块/包名或关键组件 | minitest.trigger |

## 输出格式要求

```markdown
## CI/集成类分析报告 - {集成名称}

### 1. 触发机制分析
- 触发事件：{列表}
- 触发条件：{描述}
- 手动触发：{是/否，描述}

### 2. 认证流程分析
- OIDC认证：{是/否，描述}
- API Key认证：{是/否，描述}
- 凭证优先级：{描述}

### 3. 构建验证分析
- iOS验证：{描述}
- Android验证：{描述}
- Web验证：{描述}

### 4. 元数据提取分析
- Git信息：{描述}
- 分支信息：{描述}
- PR信息：{描述}

### 5. 安全机制分析
- Secret管理：{描述}
- 权限控制：{描述}
- 凭证隔离：{描述}

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

- [ ] 触发机制分析完整，包含所有触发事件类型
- [ ] 认证流程分析包含OIDC和API Key两种方式
- [ ] 构建验证分析包含iOS/Android/Web各平台要求
- [ ] 元数据提取分析包含PR头SHA覆盖逻辑说明
- [ ] 报告末尾附「关键实体汇总表」

### L1 质量项

- [ ] OIDC认证流程分析包含token获取、claims解析细节
- [ ] 构建验证分析包含各平台验证失败的处理方式
- [ ] 安全机制分析包含最小权限原则说明
- [ ] 元数据提取分析包含分支命名规范说明
- [ ] 产物管理分析包含部署环境隔离策略

### L2 优化项

- [ ] 提供认证流程时序图（Mermaid）
- [ ] 提供触发机制流程图（Mermaid）
- [ ] 分析OIDC与API Key的权衡考虑
- [ ] 识别可复用的安全实践模式
- [ ] 提供具体的改进建议和优先级

---

[CMD-LOG] | level=INFO | cmd=template | step=S1 | event=TEMPLATE_LOADED | session=analysis-dimension-ci | msg=CI/集成类分析维度模板已加载
