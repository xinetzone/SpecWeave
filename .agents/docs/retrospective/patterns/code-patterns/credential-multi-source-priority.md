---
id: "credential-multi-source-priority"
source: "../../reports/competitive-analysis/retrospective-minitest-ecosystem-learning-20260707/insight-extraction.md#模式3"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/code-patterns/credential-multi-source-priority.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
related_patterns:
  -   - "ci-oidc-keyless-auth"
  -   - "env-var-five-layer-protection"
---
> **来源**：从Minitest AI QA测试平台生态系统复盘萃取，经Minitest CLI验证

# 凭证多源优先级模式（Credential Multi-source Priority Pattern）

## 模式类型

代码模式（CLI工具认证设计）

## 成熟度

L1 首次萃取（Minitest CLI验证）

## 适用场景

需要同时支持交互式使用、CI使用、脚本使用的CLI工具认证设计。

## 问题背景

CLI工具需要支持多种认证方式（环境变量覆盖、CI密钥、用户交互式登录），优先级处理不当会导致意外行为。

## 核心规则

### 方案

- 定义明确的三级优先级：环境变量TOKEN > 环境变量API_KEY > OAuth持久化凭证
- 高优先级凭证存在时输出一次警告提示冲突（到stderr）
- OAuth凭证自动刷新（提前5分钟缓冲区）
- 凭证文件使用0o600权限存储（仅所有者可读写）

### 优先级层次

| 优先级 | 凭证来源 | 适用场景 | 特点 |
|--------|---------|---------|------|
| 1 | 环境变量TOKEN | CI/CD流水线、脚本自动化 | 最高优先级，可覆盖其他凭证 |
| 2 | 环境变量API_KEY | 非GitHub CI环境、特殊脚本 | 次高优先级，长期密钥 |
| 3 | OAuth持久化凭证 | 交互式使用 | 最低优先级，自动刷新 |

## 验证清单

- [ ] 环境变量TOKEN存在时优先使用，覆盖其他凭证
- [ ] 高优先级凭证存在时输出警告到stderr
- [ ] OAuth凭证自动刷新（提前5分钟缓冲区）
- [ ] 凭证文件权限为0o600（仅所有者可读写）
- [ ] API Key使用Pydantic SecretStr存储，避免意外日志泄露

## 安全最佳实践

- **SecretStr类型**：API Key使用Pydantic SecretStr存储，避免意外日志泄露
- **文件权限**：OAuth凭证存储在`~/.minitest/credentials.json`，权限设为0o600（仅所有者可读写）
- **stdin密码输入**：创建test-profile时优先`--password-stdin`通过管道传密码，禁止`--password`内联传值（避免shell历史记录）
