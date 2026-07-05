# Conventional Commits 规范详解

> 本文件是 git-commit-helper Skill 的 L1 参考文档，仅在需要查阅规范细节时加载。
> 日常使用遵循 SKILL.md 中的快速流程即可。

## 概述

Conventional Commits 是一种轻量级的提交信息规范，其格式为：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

提交信息必须以类型开头，可以带可选的作用域，后面跟冒号和空格，然后是描述。

## 完整格式规范

### 1. Type（类型）— 必填

| Type | 说明 | 版本影响 |
|------|------|---------|
| `feat` | 新功能 | MINOR |
| `fix` | Bug修复 | PATCH |
| `docs` | 文档变更 | 无 |
| `style` | 代码格式（空格、分号等，不影响逻辑） | 无 |
| `refactor` | 重构（既非新功能也非修复） | 无 |
| `perf` | 性能优化 | PATCH |
| `test` | 添加或修改测试 | 无 |
| `chore` | 构建过程、工具、依赖等变更 | 无 |
| `ci` | CI/CD配置变更 | 无 |
| `revert` | 回滚之前的提交 | 视回滚内容 |

### 2. Scope（作用域）— 可选

Scope 用于说明提交影响的范围，通常是模块名、包名或目录名。

示例：
- `feat(auth): 添加JWT刷新` — auth模块
- `fix(router): 修复路由匹配` — router模块
- `docs(readme): 更新安装说明` — readme文档

### 3. Subject（描述）— 必填

- 使用祈使句（"添加"而非"添加了"/"添加了一个"）
- 首字母小写（英文）或直接中文（本项目使用中文）
- 不加句号结尾
- 长度建议≤50字符
- 描述**变更意图**而非变更内容

### 4. Body（正文）— 可选

- 位于描述之后，空一行分隔
- 用于详细说明变更的动机和与之前行为的对比
- 每行建议≤72字符
- 说明"为什么改"而不是"改了什么"（diff已经展示了改了什么）

### 5. Footer（脚注）— 可选

- 位于正文之后，空一行分隔
- 用于标注**破坏性变更**（BREAKING CHANGE）和**关联Issue**
- BREAKING CHANGE 以 `BREAKING CHANGE:` 开头，后跟说明
- 关联Issue格式：`Closes #123`、`Refs #456`

### 6. fix类型提交特殊约定（项目强制规范）

根据全局核心规则"修复即闭环"要求，所有fix类型提交必须遵循"修复→预防→闭环"三阶段SOP，禁止纯点修复。

**预防措施标记**（在subject或正文中注明）：

| 标记 | 说明 | 适用场景 |
|------|------|---------|
| `[prevent: test-case]` | 添加测试用例预防回归 | 修复逻辑Bug，补充单元/集成测试 |
| `[prevent: check-script]` | 添加/更新检查脚本 | 添加自动化检测脚本防止同类问题 |
| `[prevent: rule-update]` | 更新规范/规则文档 | 发现规范漏洞导致的Bug，更新规则 |
| `[prevent: anti-pattern]` | 添加到反模式清单 | 沉淀为反模式供后续避免 |
| `[prevent: architecture]` | 架构调整/重构 | 通过架构改进从根本上消除问题 |
| `[prevent: trivial-exempt]` | 平凡修复豁免 | 拼写错误、格式调整、注释修正、临时文件清理 |

**平凡修复识别**：subject包含以下关键词时自动识别为平凡修复，可无需预防标记：
拼写、错字、typo、格式、format、注释、comment、清理、cleanup、临时文件、temp、空格、whitespace、标点、punctuation、换行、newline。

## 完整示例

### 简单提交（最常用）

```
feat(parser): 添加数组类型解析支持
```

### 带正文的提交

```
fix(login): 修复登录态过期跳转问题 [prevent: test-case]

当token过期后，用户访问需要认证的页面时
被重定向到404而非登录页，原因是路由守卫
未正确处理401响应。

添加401拦截器统一跳转登录页，补充过期场景测试用例。
```

### fix类型带预防标记

```
fix(links): 修复原子化后相对路径错误导致的断链 [prevent: check-script]
```

```
fix(mermaid): 修复流程图节点连接方向错误 [prevent: trivial-exempt]
```

```
fix(auth): 修复JWT过期时间配置错误导致凌晨登出问题 #123
```

### 破坏性变更提交

```
refactor(api)!: 重构用户API响应格式

BREAKING CHANGE: 用户接口响应从 {data: User}
改为 {code: number, data: User, message: string}，
所有调用方需要更新响应解析逻辑。

Closes #234
```

### 回滚提交

```
revert: 回滚"feat(parser): 添加数组类型解析支持"

This reverts commit 1a2b3c4d.
```

## 原子提交原则

1. **单一职责**：每个commit只做一件事
   - 一个commit里既有feat又有fix → 拆成两个commit
   - 一个commit里改了5个不相关的文件 → 思考是否需要拆分

2. **完整性**：每个commit应该是一个完整的、可工作的状态
   - 不要提交"半完成"的代码
   - 不要提交导致构建失败的代码

3. **频率**：小步提交，每完成一个小目标就提交
   - 不要一天只提交一次"今天所有的改动"
   - 不要一个文件改了N个东西一次性提交

## 与SemVer的关系

Conventional Commits 自动对应语义化版本号（SemVer）：

- `fix` → PATCH 版本（1.0.0 → 1.0.1）
- `feat` → MINOR 版本（1.0.0 → 1.1.0）
- `BREAKING CHANGE` → MAJOR 版本（1.0.0 → 2.0.0）

## 本项目提交信息语言规范

本项目（SpecWeave）提交信息使用**中文**subject，遵循以下约定：

```
<type>(<scope>): <中文描述>
```

示例：
- ✅ `feat(auth): 添加JWT令牌刷新机制`
- ✅ `fix(router): 修复嵌套路由参数解析错误 [prevent: test-case]`
- ✅ `fix(docs): 修正README中的拼写错误 [prevent: trivial-exempt]`
- ✅ `fix(links): 修复相对路径断链问题 [prevent: check-script]`
- ✅ `docs(learning): 添加学习路径推荐表`
- ✅ `refactor(harness): 提取上下文压缩为独立模块`
- ✅ `chore(deps): 更新mcp依赖到最新版本`
- ❌ `update code`（无类型、描述模糊）
- ❌ `修复bug`（无type、无scope、无具体描述、无预防标记）
- ❌ `feat: 添加了新功能，修复了登录问题，更新了文档`（多件事混在一起）
- ❌ `fix(login): 修复登录问题`（纯点修复，无预防措施标记）
