---
id: "templates-analysis-dimension-ci-integration"
title: "CI/集成类分析维度模板"
source: "AGENTS.md#模板"
x-toml-ref: "../../../.meta/toml/.agents/templates/analysis-dimension-templates/ci-integration-dimension.toml"
version: "1.0.0"
---
# CI/集成类分析维度模板

## 核心分析维度

### 1. 触发机制

| 维度 | 分析要点 |
|------|---------|
| 触发事件 | push、PR、schedule、workflow_dispatch |
| 触发条件 | 路径过滤、分支过滤、标签过滤 |
| 手动触发 | 是否支持手动触发、触发参数 |

### 2. 事件流

| 维度 | 分析要点 |
|------|---------|
| Job编排 | Job依赖关系、并行执行策略 |
| Step定义 | Step类型、执行顺序、条件判断 |
| 数据流 | 跨Job数据传递方式 |

### 3. 配置项

| 维度 | 分析要点 |
|------|---------|
| 环境变量 | 内置变量、自定义变量、Secret管理 |
| 矩阵配置 | 多版本/多环境并行测试矩阵 |
| 缓存策略 | 依赖缓存、构建产物缓存 |

### 4. 环境依赖

| 维度 | 分析要点 |
|------|---------|
| Runner类型 | GitHub-hosted vs Self-hosted |
| Docker镜像 | 使用的基础镜像、自定义镜像构建 |
| 工具链版本 | Node/Python/Go等工具版本管理 |

### 5. 安全机制

| 维度 | 分析要点 |
|------|---------|
| OIDC认证 | 是否使用GitHub OIDC获取云凭证 |
| Secret管理 | Secret存储、访问控制 |
| 权限控制 | Workflow权限配置、GITHUB_TOKEN权限 |

### 6. 产物管理

| 维度 | 分析要点 |
|------|---------|
| Artifact上传 | 构建产物、测试报告上传 |
| 部署流程 | 自动化部署、部署环境隔离 |
| 通知机制 | Slack/邮件通知、失败告警 |

## 输出格式要求

```markdown
## CI/集成类分析报告

### 1. 触发机制分析
- 触发事件：{列表}
- 触发条件：{描述}

### 2. 事件流分析
- Job结构：{描述}
- Step编排：{描述}

### 3. 配置体系分析
- 环境变量：{描述}
- 矩阵配置：{描述}

### 4. 安全机制分析
- OIDC认证：{是/否，描述}
- Secret管理：{描述}

### 5. 设计亮点与改进建议
- 亮点：{列表}
- 建议：{列表}
```
