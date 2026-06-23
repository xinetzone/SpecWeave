# Reviewer Few-shot 示例

## 示例 1: 登录模块代码审查

**输入**: developer 提交的 EmailLoginStrategy 代码，包含密码校验与 JWT 签发逻辑。

**输出**:
代码审查报告：

- 审查范围：auth/strategies/email-login.ts、auth/facade/auth-facade.ts。
- 问题清单：

| 问题位置 | 等级 | 描述 | 建议方案 |
|---|---|---|---|
| email-login.ts:12 | 高危 | 密码错误时未限制重试次数，存在暴力破解风险 | 增加失败计数与账户锁定机制 |
| auth-facade.ts:8 | 中危 | AuthError 未映射为标准 HTTP 状态码 | 增加 try-catch 并转换为 401 |
| email-login.ts:20 | 低危 | JWT 密钥硬编码在代码中 | 迁移至环境变量配置 |

- 改进建议：建议增加登录失败限流策略，并将敏感配置外置。
- 审查结论：有条件通过，需修复高危与中危问题后重新提交。

## 示例 2: 安全漏洞识别

**输入**: developer 提交的 SQL 查询代码，使用字符串拼接构造查询语句。

**输出**:
代码审查报告：

- 审查范围：repository/user-repository.ts。
- 问题清单：

| 问题位置 | 等级 | 描述 | 建议方案 |
|---|---|---|---|
| user-repository.ts:15 | 严重 | 使用字符串拼接构造 SQL，存在注入风险 | 改用参数化查询或 ORM 占位符 |

- 改进建议：所有数据库查询必须使用参数化方式，禁止字符串拼接。
- 审查结论：不通过，必须修复严重问题后方可合入。
