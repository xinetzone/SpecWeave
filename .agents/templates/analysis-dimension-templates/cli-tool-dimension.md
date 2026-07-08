---
id: "templates-analysis-dimension-cli-tool"
title: "CLI/工具类分析维度模板"
source: "AGENTS.md#模板"
x-toml-ref: "../../../.meta/toml/.agents/templates/analysis-dimension-templates/cli-tool-dimension.toml"
version: "1.1.0"
patterns_applied: ["spec-driven-development"]
---
# CLI/工具类分析维度模板

## 核心分析维度

### 1. 命令体系

| 维度 | 分析要点 |
|------|---------|
| 命令结构 | 主命令、子命令层级关系、命令分组逻辑 |
| 参数设计 | 位置参数、可选参数、标志位、默认值处理 |
| 命令注册 | 命令注册机制（Typer/Click/argparse） |
| 帮助系统 | 自动生成的帮助信息质量、示例命令 |

### 2. 配置管理

| 维度 | 分析要点 |
|------|---------|
| 配置来源 | 命令行参数、环境变量、配置文件优先级 |
| 配置格式 | TOML/YAML/JSON/pydantic-settings |
| 配置验证 | Schema校验、默认值处理、错误提示 |
| 敏感配置 | SecretStr、环境变量注入、密码输入方式 |

### 3. 认证机制

| 维度 | 分析要点 |
|------|---------|
| 凭证来源 | API Key、OAuth、TOKEN、SSO |
| 凭证优先级 | 多源凭证优先级策略、冲突处理 |
| 凭证存储 | 文件存储（权限0o600）、密钥链、环境变量 |
| 刷新机制 | 自动刷新、过期处理、重试策略 |

### 4. 输出约定

| 维度 | 分析要点 |
|------|---------|
| stdout/stderr分离 | 数据输出到stdout，诊断信息到stderr |
| 结构化输出 | JSON模式、--json参数、输出格式规范 |
| 退出码设计 | 细粒度退出码（0-5）、错误分类 |
| 用户反馈 | Rich表格渲染、进度提示、成功/失败提示 |

### 5. 核心API

| 维度 | 分析要点 |
|------|---------|
| HTTP客户端 | httpx/requests、异步支持、连接池 |
| API封装 | ApiClient设计、自动认证、重试逻辑 |
| 错误处理 | 异常捕获、错误码映射、用户友好提示 |
| 版本管理 | API版本控制、向后兼容 |

### 6. 依赖管理

| 维度 | 分析要点 |
|------|---------|
| 依赖声明 | pyproject.toml/requirements.txt/package.json |
| 依赖锁定 | uv.lock/package-lock.json/go.sum |
| 依赖类型 | 生产依赖 vs 开发依赖、可选项 |
| 依赖更新 | Renovate配置、版本策略 |

## 关键实体标记

报告末尾必须附「关键实体汇总表」：

```markdown
## 关键实体

| 类型 | 名称 | 说明 |
|------|------|------|
| API | POST /api/v1/test/run | 执行测试任务接口 |
| CONFIG | MINITEST_API_KEY | API密钥配置 |
| MODULE | minitest.cli.commands | CLI命令模块 |
```

**必须标记的实体类型**：

| 标记类型 | 说明 | 示例 |
|---------|------|------|
| API | REST/gRPC/WebSocket接口 | POST /api/v1/test/run |
| CONFIG | 环境变量或配置文件项 | MINITEST_API_KEY |
| MODULE | 代码模块/包名或关键组件 | minitest.cli.commands |

## 输出格式要求

```markdown
## CLI/工具类分析报告 - {工具名称}

### 1. 命令体系分析
- 命令结构：{描述层级关系}
- 核心命令列表：{列表}
- 参数设计：{描述参数策略}

### 2. 配置管理分析
- 配置来源优先级：{描述}
- 配置验证机制：{描述}
- 敏感配置处理：{描述}

### 3. 认证机制分析
- 凭证来源：{列表}
- 凭证优先级：{描述}
- 凭证存储：{描述}

### 4. 输出约定分析
- stdout/stderr分离：{是/否，描述}
- 结构化输出：{是/否，描述}
- 退出码设计：{描述}

### 5. 核心API分析
- HTTP客户端：{描述}
- API封装：{描述}
- 错误处理：{描述}

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

- [ ] 命令体系分析完整，包含所有命令组及其功能
- [ ] 配置管理分析包含配置来源优先级说明
- [ ] 认证机制分析包含凭证多源优先级策略
- [ ] 输出约定分析包含stdout/stderr分离说明
- [ ] 报告末尾附「关键实体汇总表」

### L1 质量项

- [ ] 命令体系分析包含命令注册机制说明
- [ ] 配置管理分析包含敏感配置安全处理方式
- [ ] 认证机制分析包含凭证存储方式和权限设置
- [ ] 输出约定分析包含退出码定义说明
- [ ] 核心API分析包含错误处理机制说明

### L2 优化项

- [ ] 提供命令体系架构图（Mermaid）
- [ ] 提供认证流程时序图（Mermaid）
- [ ] 分析设计决策的权衡考虑
- [ ] 识别可复用的设计模式
- [ ] 提供具体的改进建议和优先级

---

[CMD-LOG] | level=INFO | cmd=template | step=S1 | event=TEMPLATE_LOADED | session=analysis-dimension-cli | msg=CLI/工具类分析维度模板已加载
