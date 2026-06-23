# Developer Few-shot 示例

## 示例 1: 登录功能代码实现

**输入**: 任务：根据架构设计实现邮箱密码登录策略 EmailLoginStrategy，需校验密码并签发 JWT。

**输出**:
代码提交说明：

- 变更摘要：新增 EmailLoginStrategy 类，实现密码校验与 JWT 签发逻辑。
- 影响范围：auth/strategies/email-login.ts、auth/facade/auth-facade.ts。
- 测试结果：新增 8 个单元测试，全部通过，核心路径覆盖率 92%。
- 关联任务：T-002。

关键代码片段：
```typescript
export class EmailLoginStrategy implements ILoginStrategy {
  async login(request: LoginRequest): Promise<LoginResponse> {
    const user = await this.userRepository.findByEmail(request.email);
    if (!user) {
      throw new AuthError('USER_NOT_FOUND');
    }
    const valid = await bcrypt.compare(request.password, user.passwordHash);
    if (!valid) {
      throw new AuthError('INVALID_PASSWORD');
    }
    const token = this.tokenService.sign({ userId: user.id });
    return { token, expiresIn: 7200 };
  }
}
```

## 示例 2: 缺陷修复

**输入**: tester 反馈：登录接口在密码错误时返回 500 错误码，预期应返回 401。

**输出**:
缺陷修复报告：

- 缺陷描述：EmailLoginStrategy 在密码校验失败时抛出未捕获异常，导致网关返回 500。
- 根因分析：AuthError 未在 AuthFacade 中被捕获并转换为对应的 HTTP 状态码。
- 修复方案：在 AuthFacade 中增加 try-catch，将 AuthError 映射为 401 状态码并返回标准化错误响应。
- 验证结果：补充 2 个测试用例覆盖密码错误与用户不存在场景，测试通过，错误码符合预期。
- 关联任务：BUG-015。
